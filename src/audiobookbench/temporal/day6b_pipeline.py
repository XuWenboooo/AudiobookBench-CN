"""Day 6B pipeline: speaker-consistency localization (non-trained).

Loads the frozen temporal speaker embeddings (Day 6B extraction), scores
every window with B1a/B1b (sequence-local prototype), B2 (neighbor change),
B3 (paired-clean ORACLE) and B4 (boundary transient DIAGNOSTIC), projects
full/core/blend ground truth onto the speaker grid, evaluates AUROC/AUPRC/F1
per split x variant x GT x baseline with train-only thresholds, adds
case-level bootstrap CIs, the zone shortcut audit, paired A0/A1 analysis and
deterministic figures.

The Day 6A negative result is never re-run or modified.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.evaluation.day6a_localization import evaluate_windows, f1_at_threshold
from audiobookbench.security.day5_precheck import REPO_ROOT, run_day5_precheck
from audiobookbench.temporal.day6a_pipeline import verify_day5_outputs_unchanged
from audiobookbench.temporal.day6b_embed import (
    EMBEDDING_DIM,
    SpeakerWindowScale,
    build_speaker_windows,
    load_config,
    load_records,
)
from audiobookbench.temporal.day6b_scoring import (
    b1_scores,
    b2_scores,
    b3_scores,
    b4_scores,
    project_ground_truth_speaker,
)

DAY6B = REPO_ROOT / "results/day6b"
DAY6B_SEED = 20260905
BOOTSTRAP_RESAMPLES = 2000
BASELINES = ("B1a", "B1b", "B2_adjacent", "B2_symmetric", "B3_ORACLE", "B4_DIAGNOSTIC")
GT_NAMES = ("full", "core")
SPLITS = ("train", "val", "test")
VARIANTS = ("a0", "a1")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _fmt(value: Any) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "nan"
    return f"{value:.6f}" if np.isfinite(value) else "nan"


def _intervals(row: dict[str, str]) -> dict[str, tuple[int, int]]:
    return {
        "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
        "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
    }


def load_day5_log_energy(repo_root: Path) -> dict[str, np.ndarray]:
    """Parse only the log_energy column from the frozen Day 5 frame CSVs."""
    out: dict[str, list[float]] = {}
    for variant in ("clean", "a0", "a1"):
        path = repo_root / "results/day5_validation" / f"day5_frame_metadata_{variant}.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                out.setdefault(row["record_id"], []).append(float(row["log_energy"]))
    return {rid: np.asarray(values, dtype=np.float64) for rid, values in out.items()}


def load_embeddings(repo_root: Path, scale_name: str, record_id: str) -> np.ndarray:
    path = repo_root / "results/day6b/embeddings" / f"{scale_name}__{record_id}.npy"
    emb = np.load(path)
    assert emb.shape[1] == EMBEDDING_DIM
    return emb


def _clean_id_of(manipulated_id: str) -> str:
    return manipulated_id.split("_paircase_")[0]


def speaker_disjoint_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    by_split: dict[str, set[str]] = defaultdict(set)
    for rec in records.values():
        by_split[rec["split"]].add(rec["speaker"])
    assert set(by_split) == {"train", "val", "test"}
    sizes = {s: len(by_split[s]) for s in by_split}
    disjoint = not (by_split["train"] & by_split["val"]) and \
        not (by_split["train"] & by_split["test"]) and \
        not (by_split["val"] & by_split["test"])
    return {
        "speakers_per_split": sizes,
        "expected": {"train": 6, "val": 3, "test": 3},
        "disjoint": disjoint,
        "sizes_ok": sizes == {"train": 6, "val": 3, "test": 3},
        "passed": disjoint and sizes == {"train": 6, "val": 3, "test": 3},
    }


def _collect(manip_scores: dict[str, np.ndarray], record_meta: dict[str, dict[str, Any]],
             gt_rows: dict[str, list[dict[str, Any]]], split: str, baseline: str,
             gt: str, variant: str | None) -> tuple[np.ndarray, np.ndarray, list[str]]:
    label_col = "is_attack_window" if gt == "full" else "is_core_window"
    y, s, zones = [], [], []
    for rid, rec in record_meta.items():
        if rec["variant"] not in VARIANTS or rec["split"] != split:
            continue
        if variant is not None and rec["variant"] != variant:
            continue
        scores = manip_scores[rid][baseline]
        rows = gt_rows[rid]
        for i, row in enumerate(rows):
            value = float(scores[i])
            y.append(bool(row[label_col]))
            s.append(value if np.isfinite(value) else np.nan)
            zones.append(row["zone"])
    return np.asarray(y), np.asarray(s, dtype=np.float64), zones


def best_f1_threshold(y: np.ndarray, s: np.ndarray, grid_size: int = 512) -> float:
    mask = np.isfinite(s)
    y, s = y[mask], s[mask]
    if y.size == 0 or not y.any() or y.all():
        return float("nan")
    candidates = np.quantile(s, np.linspace(0.0, 1.0, grid_size)) if s.size > grid_size else np.unique(s)
    best_tau, best_f1 = float(candidates[-1]) + 1e-9, -1.0
    for tau in candidates:
        pred = s >= tau
        tp = int(np.sum(y & pred)); fp = int(np.sum(~y & pred)); fn = int(np.sum(y & ~pred))
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        if f1 > best_f1 + 1e-12:
            best_f1, best_tau = f1, float(tau)
    return best_tau


def case_bootstrap_ci(
    record_meta: dict[str, dict[str, Any]],
    manip_scores: dict[str, np.ndarray],
    gt_rows: dict[str, list[dict[str, Any]]],
    baseline: str,
    gt: str,
    split: str,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = DAY6B_SEED,
) -> dict[str, Any]:
    """Case-level bootstrap (resample paired_case_id, not windows)."""
    rng = np.random.default_rng(seed)
    label_col = "is_attack_window" if gt == "full" else "is_core_window"
    case_data: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for rid, rec in record_meta.items():
        if rec["variant"] not in VARIANTS or rec["split"] != split:
            continue
        rows = gt_rows[rid]
        y = np.array([bool(r[label_col]) for r in rows])
        s = np.asarray(manip_scores[rid][baseline], dtype=np.float64)
        case_data.setdefault(rec["paired_case_id"], ([], []))
        y0, s0 = case_data[rec["paired_case_id"]]
        case_data[rec["paired_case_id"]] = (np.concatenate([y0, y]), np.concatenate([s0, s]))
    case_ids = sorted(case_data)
    if len(case_ids) < 2:
        return {"n_cases": len(case_ids), "auroc_ci": ["nan", "nan"], "auprc_ci": ["nan", "nan"]}
    aurocs, auprcs = [], []
    from audiobookbench.evaluation.day6a_localization import auprc as _auprc, auroc as _auroc
    for _ in range(resamples):
        chosen = rng.choice(case_ids, size=len(case_ids), replace=True)
        ys = np.concatenate([case_data[c][0] for c in chosen])
        ss = np.concatenate([case_data[c][1] for c in chosen])
        aurocs.append(_auroc(ys, ss))
        auprcs.append(_auprc(ys, ss))
    aurocs_arr = np.asarray(aurocs, dtype=np.float64)
    auprcs_arr = np.asarray(auprcs, dtype=np.float64)

    def ci(vals: np.ndarray) -> list[float]:
        finite = vals[np.isfinite(vals)]
        if finite.size < resamples * 0.5:
            return ["nan", "nan"]
        return [float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))]

    return {
        "n_cases": len(case_ids), "resamples": resamples, "seed": seed,
        "auroc_ci": ci(aurocs_arr), "auprc_ci": ci(auprcs_arr),
    }


def render_day6b_figures(
    records: dict[str, dict[str, Any]],
    per_scale: dict[str, dict[str, Any]],
    figures_dir: Path,
    n_cases: int = 5,
) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scale_name = "S1_1000ms_250ms"
    context = per_scale[scale_name]
    gt_rows, scores = context["gt_rows"], context["manip_scores"]
    windows_by_record = context["windows_by_record"]
    clean_scores = context["clean_scores"]

    case_infos = []
    for case_id in sorted({rec["paired_case_id"] for rec in records.values() if rec["variant"] in VARIANTS}):
        rid_a0 = next((r for r, v in records.items() if v["paired_case_id"] == case_id and v["variant"] == "a0"), None)
        rid_a1 = next((r for r, v in records.items() if v["paired_case_id"] == case_id and v["variant"] == "a1"), None)
        if rid_a0 is None or rid_a1 is None or records[rid_a0]["split"] != "test":
            continue
        core_mask = np.array([r["is_core_window"] for r in gt_rows[rid_a0]], dtype=bool)
        d = float(np.nanmean(scores[rid_a1]["B1b"][core_mask]) - np.nanmean(scores[rid_a0]["B1b"][core_mask]))
        case_infos.append({"case_id": case_id, "rid_a0": rid_a0, "rid_a1": rid_a1, "delta": d})
    if not case_infos:
        return []
    ordered = sorted(case_infos, key=lambda r: r["delta"])
    chosen: dict[str, dict[str, Any]] = {}
    if ordered:
        chosen[ordered[0]["case_id"]] = ordered[0]
        chosen[ordered[-1]["case_id"]] = ordered[-1]
        chosen[ordered[len(ordered) // 2]["case_id"]] = ordered[len(ordered) // 2]
    for r in ordered:
        if len(chosen) >= n_cases:
            break
        chosen.setdefault(r["case_id"], r)

    paths = []
    for case_id in sorted(chosen):
        info = chosen[case_id]
        rid_a0, rid_a1 = info["rid_a0"], info["rid_a1"]
        rid_clean = _clean_id_of(rid_a0)
        rows = gt_rows[rid_a0]
        t = np.array([r["time_center"] for r in windows_by_record[rid_a0]])
        attack = np.array([r["attack_overlap_ratio"] for r in rows])
        core = np.array([r["core_overlap_ratio"] for r in rows])

        fig, axes = plt.subplots(4, 1, figsize=(14, 13), sharex=True)
        fig.suptitle(f"Day6B speaker-consistency pair {case_id} ({scale_name})", fontsize=13)

        ax = axes[0]
        if rid_clean in clean_scores:
            ax.plot(t, clean_scores[rid_clean]["B1b"], label="clean", color="#2b6cb0", lw=0.9)
        ax.plot(t, scores[rid_a0]["B1b"], label="A0", color="#c05621", lw=0.9, alpha=0.85)
        ax.plot(t, scores[rid_a1]["B1b"], label="A1", color="#2f855a", lw=0.9, alpha=0.85)
        ax.set_ylabel("B1b 1-cos to robust proto")
        ax.set_title("Sequence-local speaker inconsistency (B1b robust prototype)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        for band, color, alpha in ((attack, "#805ad5", 0.15), (core, "#e53e3e", 0.15)):
            ax.fill_between(t, ax.get_ylim()[0], ax.get_ylim()[1], where=band > 0, step="mid", color=color, alpha=alpha)

        ax = axes[1]
        ax.plot(t, scores[rid_a0]["B2_adjacent"], label="A0 adjacent", color="#c05621", lw=0.9)
        ax.plot(t, scores[rid_a1]["B2_adjacent"], label="A1 adjacent", color="#2f855a", lw=0.9)
        ax.set_ylabel("B2 adjacent 1-cos")
        ax.set_title("Neighbor speaker change (adjacent windows)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[2]
        ax.plot(t, scores[rid_a0]["B3_ORACLE"], label="A0 vs clean (ORACLE)", color="#c05621", lw=0.9)
        ax.plot(t, scores[rid_a1]["B3_ORACLE"], label="A1 vs clean (ORACLE)", color="#2f855a", lw=0.9)
        ax.set_ylabel("B3 ORACLE 1-cos")
        ax.set_title("Paired-clean embedding differential (ORACLE / DIAGNOSTIC, not deployable)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[3]
        ax.fill_between(t, 0, attack, step="mid", color="#805ad5", alpha=0.35, label="GT full")
        ax.fill_between(t, 0, core, step="mid", color="#e53e3e", alpha=0.35, label="GT strict core")
        ax.set_ylabel("GT overlap"); ax.set_xlabel("time (s)")
        ax.set_title("Ground truth projection on the speaker grid (majority rule 0.5)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        fig.tight_layout(rect=(0, 0, 1, 0.97))
        out = figures_dir / f"day6b_speaker_{case_id}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        paths.append(out)
    return paths


def run_day6b(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    config = load_config(repo_root)
    results_dir = repo_root / "results/day6b"
    figures_dir = results_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "config.yaml").write_text(
        (repo_root / "configs/day6b_speaker_consistency.yaml").read_text(encoding="utf-8"), encoding="utf-8",
    )
    precheck = run_day5_precheck(repo_root)
    records = load_records(repo_root)
    disjoint = speaker_disjoint_audit(records)
    label_threshold = float(config["gt_projection"]["label_threshold"])
    scale_entries = config["speaker_temporal_grid"]["scales"]

    log_energy = load_day5_log_energy(repo_root)
    all_score_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    zone_audit: dict[str, Any] = {}
    paired_rows: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    per_scale: dict[str, dict[str, Any]] = {}

    for entry in scale_entries:
        scale = SpeakerWindowScale.from_config(entry)
        name = scale.name
        record_meta = {rid: rec for rid, rec in records.items() if rec["split"] in SPLITS}
        gt_rows: dict[str, list[dict[str, Any]]] = {}
        windows_by_record: dict[str, list[dict[str, Any]]] = {}
        clean_emb: dict[str, np.ndarray] = {}
        manip_emb: dict[str, np.ndarray] = {}
        for rid, rec in record_meta.items():
            emb = load_embeddings(repo_root, name, rid)
            if rec["variant"] == "clean":
                clean_emb[rid] = emb
            else:
                manip_emb[rid] = emb
                wins = build_speaker_windows(_num_samples(records, rid, scale, repo_root), scale)
                windows_by_record[rid] = wins
                gt_rows[rid] = project_ground_truth_speaker(
                    wins, _intervals(rec["manifest_row"]), label_threshold,
                )

        manip_scores: dict[str, dict[str, np.ndarray]] = {}
        clean_scores: dict[str, dict[str, np.ndarray]] = {}
        for rid, emb in manip_emb.items():
            scores: dict[str, np.ndarray] = {
                "B1a": b1_scores(emb, trimmed=False),
                "B1b": b1_scores(emb, trimmed=True),
            }
            adj, sym = b2_scores(emb)
            scores["B2_adjacent"], scores["B2_symmetric"] = adj, sym
            cid_clean = _clean_id_of(rid)
            if cid_clean in clean_emb and clean_emb[cid_clean].shape[0] == emb.shape[0]:
                scores["B3_ORACLE"] = b3_scores(emb, clean_emb[cid_clean])
            else:
                scores["B3_ORACLE"] = np.full(emb.shape[0], np.nan)
            spans = _frame_spans(windows_by_record[rid])
            scores["B4_DIAGNOSTIC"] = b4_scores(log_energy[rid], spans)
            manip_scores[rid] = scores
            all_score_rows.extend(_score_rows(name, records[rid], windows_by_record[rid], gt_rows[rid], scores))
        for rid, emb in clean_emb.items():
            clean_scores[rid] = {"B1a": b1_scores(emb, trimmed=False), "B1b": b1_scores(emb, trimmed=True)}
            adj, sym = b2_scores(emb)
            clean_scores[rid]["B2_adjacent"], clean_scores[rid]["B2_symmetric"] = adj, sym

        thresholds = {}
        for baseline in BASELINES:
            y, s, _ = _collect(manip_scores, record_meta, gt_rows, "train", baseline, "full", None)
            thresholds[baseline] = best_f1_threshold(y, s)
            for gt in GT_NAMES:
                for variant in VARIANTS:
                    for split in SPLITS:
                        y2, s2, _ = _collect(manip_scores, record_meta, gt_rows, split, baseline, gt, variant)
                        result = evaluate_windows(y2, s2, thresholds[baseline])
                        result.update({
                            "threshold_train_f1": thresholds[baseline], "scale": name,
                            "baseline": baseline, "gt": gt, "variant": variant, "split": split,
                        })
                        key = f"{name}|{baseline}|{gt}|{variant}|{split}"
                        metrics[key] = result
                        metric_rows.append({
                            "scale": name, "baseline": baseline, "gt": gt, "variant": variant, "split": split,
                            "auroc": _fmt(result["auroc"]), "auprc": _fmt(result["auprc"]), "f1": _fmt(result["f1"]),
                            "threshold": _fmt(thresholds[baseline]), "n_windows": result["n_windows"],
                            "n_positive": result["n_positive"],
                        })

        for baseline in ("B1a", "B1b", "B2_adjacent"):
            for variant in VARIANTS:
                for split in SPLITS:
                    _, s, zones = _collect(manip_scores, record_meta, gt_rows, split, baseline, "full", variant)
                    zone_audit[f"{name}|{baseline}|{variant}|{split}"] = _zone_stats(s, np.asarray(zones))

        for case_id in sorted({rec["paired_case_id"] for rec in records.values() if rec["variant"] in VARIANTS}):
            rid_a0 = next((r for r, v in records.items() if v["paired_case_id"] == case_id and v["variant"] == "a0"), None)
            rid_a1 = next((r for r, v in records.items() if v["paired_case_id"] == case_id and v["variant"] == "a1"), None)
            if rid_a0 is None or rid_a1 is None:
                continue
            rows0 = gt_rows[rid_a0]
            labels = np.array([r["is_attack_window"] for r in rows0], dtype=bool)
            core_mask = np.array([r["is_core_window"] for r in rows0], dtype=bool)
            boundary_mask = np.array([r["zone"] == "boundary" for r in rows0], dtype=bool)
            s0, s1 = manip_scores[rid_a0]["B1b"], manip_scores[rid_a1]["B1b"]
            from audiobookbench.evaluation.day6a_localization import auroc
            paired_rows.append({
                "scale": name, "paired_case_id": case_id, "split": records[rid_a0]["split"],
                "auroc_a0_full": _fmt(auroc(labels, s0)), "auroc_a1_full": _fmt(auroc(labels, s1)),
                "mean_anom_core_a0": _fmt(_nanmean(np.where(core_mask, s0, np.nan))),
                "mean_anom_core_a1": _fmt(_nanmean(np.where(core_mask, s1, np.nan))),
                "delta_core_a1_minus_a0": _fmt(_diff(_nanmean(np.where(core_mask, s1, np.nan)), _nanmean(np.where(core_mask, s0, np.nan)))),
                "mean_anom_boundary_a0": _fmt(_nanmean(np.where(boundary_mask, s0, np.nan))),
                "mean_anom_boundary_a1": _fmt(_nanmean(np.where(boundary_mask, s1, np.nan))),
            })

        for baseline in ("B1a", "B1b", "B2_adjacent", "B3_ORACLE"):
            for gt in GT_NAMES:
                for split in ("val", "test"):
                    ci = case_bootstrap_ci(record_meta, manip_scores, gt_rows, baseline, gt, split)
                    bootstrap_rows.append({"scale": name, "baseline": baseline, "gt": gt, "split": split,
                                           "auroc_ci_low": _fmt(ci["auroc_ci"][0]), "auroc_ci_high": _fmt(ci["auroc_ci"][1]),
                                           "auprc_ci_low": _fmt(ci["auprc_ci"][0]), "auprc_ci_high": _fmt(ci["auprc_ci"][1]),
                                           "n_cases": ci["n_cases"], "resamples": ci.get("resamples", BOOTSTRAP_RESAMPLES), "seed": DAY6B_SEED})

        per_scale[name] = {"gt_rows": gt_rows, "windows_by_record": windows_by_record, "manip_scores": manip_scores, "clean_scores": clean_scores, "thresholds": thresholds}

    figures = render_day6b_figures(records, per_scale, figures_dir)
    failure_rows = collect_day6b_failures(records, per_scale)
    _write_outputs(results_dir, all_score_rows, metric_rows, metrics, zone_audit, paired_rows, bootstrap_rows, failure_rows, disjoint, precheck, figures, records, per_scale)
    return json.loads((results_dir / "run_summary.json").read_text(encoding="utf-8"))


def _num_samples(
    records: dict[str, dict[str, Any]],
    rid: str,
    scale: SpeakerWindowScale,
    repo_root: Path = REPO_ROOT,
) -> int:
    # waveform length is recovered from the embedding manifest grid: use the
    # saved embedding count to rebuild windows without re-decoding audio.
    emb = load_embeddings(repo_root, scale.name, rid)
    count = emb.shape[0]
    # invert window_count: count = 1 + (N - W) // H  =>  N = W + (count-1)*H .. W + (count-1)*H + H - 1
    return scale.window_samples + (count - 1) * scale.hop_samples


def _frame_spans(windows: list[dict[str, Any]]) -> list[tuple[int, int]]:
    """Map speaker windows to inclusive Day5 frame index ranges (sample-exact)."""
    hop, frame = 160, 400
    spans = []
    for row in windows:
        lo, hi = row["sample_start"], row["sample_end"]
        f_lo = max(0, (lo - frame + hop) // hop)
        f_hi = (hi - frame) // hop
        spans.append((f_lo, max(f_lo, f_hi)))
    return spans


def _score_rows(scale: str, rec: dict[str, Any], windows: list[dict[str, Any]], gt_rows: list[dict[str, Any]], scores: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows = []
    for i, (w, g) in enumerate(zip(windows, gt_rows)):
        row = {
            "scale": scale, "record_id": rec["record_id"], "variant": rec["variant"],
            "paired_case_id": rec["paired_case_id"], "split": rec["split"],
            "window_index": g["window_index"], "sample_start": w["sample_start"],
            "sample_end": w["sample_end"], "time_center": f"{w['time_center']:.6f}",
        }
        for baseline, values in scores.items():
            v = float(values[i])
            row[baseline] = f"{v:.6f}" if np.isfinite(v) else "nan"
        for name in ("attack", "core", "blend"):
            row[f"{name}_overlap_ratio"] = f"{g[f'{name}_overlap_ratio']:.6f}"
        row["zone"] = g["zone"]
        rows.append(row)
    return rows


def _zone_stats(scores: np.ndarray, zones: np.ndarray) -> dict[str, Any]:
    out = {}
    for zone in ("outside", "boundary", "core"):
        values = scores[(zones == zone) & np.isfinite(scores)]
        out[zone] = {
            "mean": float(np.mean(values)) if values.size else float("nan"),
            "median": float(np.median(values)) if values.size else float("nan"),
            "q25": float(np.percentile(values, 25)) if values.size else float("nan"),
            "q75": float(np.percentile(values, 75)) if values.size else float("nan"),
            "n": int(values.size),
        }
    return out


def _nanmean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else float("nan")


def _diff(a: float, b: float) -> float:
    return a - b if (np.isfinite(a) and np.isfinite(b)) else float("nan")


def collect_day6b_failures(records: dict[str, dict[str, Any]], per_scale: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for name, context in per_scale.items():
        paired = context.get("paired_rows", [])
        for variant in VARIANTS:
            ranked = sorted(
                (r for r in paired if np.isfinite(float(r[f"auroc_{variant}_full"]))),
                key=lambda r: float(r[f"auroc_{variant}_full"]),
            )
            for r in ranked[:2]:
                failures.append({
                    "scale": name, "failure_type": f"{variant}_lowest_case_auroc",
                    "record_id": "", "split": r["split"], "variant": variant,
                    "detail": f"paired_case={r['paired_case_id']} auroc_full={r[f'auroc_{variant}_full']}",
                })
        ranked_core = sorted(
            (r for r in paired if np.isfinite(float(r["delta_core_a1_minus_a0"]))),
            key=lambda r: float(r["delta_core_a1_minus_a0"]),
        )
        for r in ranked_core[:2]:
            failures.append({
                "scale": name, "failure_type": "a1_core_anomaly_above_a0",
                "record_id": "", "split": r["split"], "variant": "a1>a0",
                "detail": f"paired_case={r['paired_case_id']} delta_core_a1_minus_a0={r['delta_core_a1_minus_a0']}",
            })
    return failures


def _write_outputs(results_dir: Path, score_rows: list[dict[str, Any]], metric_rows: list[dict[str, Any]],
                   metrics: dict[str, Any], zone_audit: dict[str, Any], paired_rows: list[dict[str, Any]],
                   bootstrap_rows: list[dict[str, Any]], failure_rows: list[dict[str, Any]], disjoint: dict[str, Any],
                   precheck: dict[str, Any], figures: list[Path], records: dict[str, dict[str, Any]],
                   per_scale: dict[str, dict[str, Any]]) -> None:
    _write_csv(results_dir / "speaker_scores.csv", score_rows)
    _write_csv(results_dir / "metrics_by_split.csv", metric_rows)
    _write_csv(results_dir / "paired_analysis.csv", paired_rows)
    _write_csv(results_dir / "bootstrap_ci.csv", bootstrap_rows)
    _write_csv(results_dir / "failure_cases.csv", failure_rows)
    _write_csv(results_dir / "zone_audit.csv", _zone_rows(zone_audit))
    _write_csv(results_dir / "metrics_by_attack.csv", _attack_rows(metrics))
    (results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (results_dir / "zone_audit.json").write_text(json.dumps(zone_audit, indent=2), encoding="utf-8")

    day6a_unchanged = _verify_day6a_unchanged()
    run_summary = {
        "pipeline": "day6b_speaker_consistency",
        "non_trained": True,
        "speaker_disjoint": disjoint,
        "precheck_all_passed": precheck["all_passed"],
        "day5_outputs_unchanged": verify_day5_outputs_unchanged(),
        "day6a_outputs_unchanged": day6a_unchanged,
        "baselines": {"B1a": "deployable", "B1b": "deployable", "B2_adjacent": "deployable",
                      "B2_symmetric": "deployable", "B3_ORACLE": "oracle_only", "B4_DIAGNOSTIC": "diagnostic_only"},
        "speaker_id_used_as_feature": False,
        "thresholds_never_use_val_test": True,
        "bootstrap": {"unit": "paired_case_id", "resamples": BOOTSTRAP_RESAMPLES, "seed": DAY6B_SEED},
        "figures": [str(p) for p in figures],
        "records_scored": len(records),
        "scales": sorted(per_scale),
    }
    (results_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")


def _zone_rows(zone_audit: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, zones in sorted(zone_audit.items()):
        scale, baseline, variant, split = key.split("|")
        for zone, stats in zones.items():
            rows.append({"scale": scale, "baseline": baseline, "variant": variant, "split": split,
                         "zone": zone, **{k: _fmt(v) if isinstance(v, float) else v for k, v in stats.items()}})
    return rows


def _attack_rows(metrics: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: dict[tuple[str, str, str], dict[str, Any]] = {}
    for key, result in metrics.items():
        scale, baseline, gt, variant, split = key.split("|")
        if split != "test" or gt != "full":
            continue
        row = rows.setdefault((scale, baseline, variant), {"scale": scale, "baseline": baseline, "variant": variant})
        for s in SPLITS:
            r = metrics[f"{scale}|{baseline}|full|{variant}|{s}"]
            row[f"{s}_auroc"] = _fmt(r["auroc"])
            row[f"{s}_auprc"] = _fmt(r["auprc"])
            row[f"{s}_f1"] = _fmt(r["f1"])
    return [rows[k] for k in sorted(rows)]


def _verify_day6a_unchanged() -> bool:
    import hashlib

    record_path = REPO_ROOT / "results/day6b/day6a_frozen_record.json"
    if not record_path.exists():
        return False
    record = json.loads(record_path.read_text(encoding="utf-8"))
    for relpath, expected in record["hashes"].items():
        path = REPO_ROOT / relpath
        if not path.exists():
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest().upper() != expected:
            return False
    return True


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the Day 6B speaker-consistency pipeline.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    summary = run_day6b(Path(args.repo_root))
    print(json.dumps(summary, indent=2))
    gates = [
        summary["precheck_all_passed"], summary["day5_outputs_unchanged"],
        summary["day6a_outputs_unchanged"], summary["speaker_disjoint"]["passed"],
    ]
    return 0 if all(gates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
