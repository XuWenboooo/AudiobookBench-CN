"""Day 6C pipeline: confound controls for speaker-consistency localization.

Everything reuses the frozen Day 6B backend, grids, scores and rules; the
Day 6B/6A results are read-only. Components:

- C0 embedding extraction (same ECAPA, same S1/S2) and B1a/B1b/B2 scoring;
- C1 speech-active mask (label-agnostic, from frozen Day 5 pause frames,
  pre-frozen threshold 0.5, no attack GT anywhere);
- cross-speaker (A0/A1) vs same-speaker (C0A/C0B) comparison per paired case;
- C2 duration stratification over the frozen 0.75/1.5/2.5 s tiers;
- temporal-resolution audit (window/attack duration ratio, positive windows);
- C3 case-level evaluation incl. global top-1 peak localization error;
- C4 clean-transition audit (clean top-3 peaks vs utterance/gap boundaries);
- bootstrap CI (case-level) for the cross-vs-same core-anomaly contrast;
- deterministic failure-case collection and figures A-E.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.evaluation.day6a_localization import auroc as _auroc
from audiobookbench.evaluation.day6a_localization import auprc as _auprc
from audiobookbench.evaluation.day6a_localization import f1_at_threshold
from audiobookbench.security.day5_precheck import REPO_ROOT, run_day5_precheck
from audiobookbench.security.day6c_same_speaker import verify_against_freeze
from audiobookbench.temporal.day6a_pipeline import verify_day5_outputs_unchanged
from audiobookbench.temporal.day6b_embed import (
    EMBEDDING_DIM,
    SAMPLE_RATE,
    SpeakerBackend,
    SpeakerWindowScale,
    build_speaker_windows,
    load_config as load_day6b_config,
    load_records,
)
from audiobookbench.temporal.day6b_pipeline import load_day5_log_energy
from audiobookbench.temporal.day6b_scoring import (
    b1_scores,
    b2_scores,
    project_ground_truth_speaker,
)

DAY6C = REPO_ROOT / "results/day6c"
DAY6B_RESULTS = REPO_ROOT / "results/day6b"
SPEECH_ACTIVE_THRESHOLD = 0.5  # frozen before any Day 6C result
SEED = 20260905
BOOTSTRAP = 2000
GT_NAMES = ("full", "core")
VARIANTS = ("a0", "a1")
C0_VARIANTS = ("c0a", "c0b")
TIERS = ("0.75s", "1.5s", "2.5s")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _fmt(v: Any) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "nan"
    return f"{v:.6f}" if np.isfinite(v) else "nan"


def load_c0_records(repo_root: Path) -> dict[str, dict[str, Any]]:
    rows = _read_csv(repo_root / "data/manifests/day6c_same_speaker_control_manifest.csv")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        rid = row["control_sequence_id"]
        out.setdefault(rid, {
            "record_id": rid,
            "variant": "c0a" if row["control_variant"] == "C0A" else "c0b",
            "paired_case_id": row["paired_case_id"],
            "split": row["split"],
            "speaker": row["target_speaker"],
            "audio_path": str(repo_root / row["control_audio_relpath"]),
            "manifest_row": row,
        })
    return out


def _intervals_c0(row: dict[str, str]) -> dict[str, tuple[int, int]]:
    return {
        "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
        "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
    }


def extract_c0_embeddings(repo_root: Path) -> dict[str, int]:
    config = load_day6b_config(repo_root)
    out_dir = repo_root / "results/day6c/embeddings"
    out_dir.mkdir(parents=True, exist_ok=True)
    backend = SpeakerBackend()
    backend.load()
    counts: dict[str, int] = {}
    records = load_c0_records(repo_root)
    scales = [SpeakerWindowScale.from_config(e) for e in config["speaker_temporal_grid"]["scales"]]
    for record in records.values():
        from audiobookbench.preprocessing.audio_io import load_audio

        waveform, sr = load_audio(record["audio_path"], target_sr=None)
        assert sr == SAMPLE_RATE
        for scale in scales:
            windows = build_speaker_windows(waveform.size, scale)
            spans = [(w["sample_start"], w["sample_end"]) for w in windows]
            emb = backend.embed_windows(waveform, spans)
            assert emb.shape == (len(windows), EMBEDDING_DIM)
            np.save(out_dir / f"{scale.name}__{record['record_id']}.npy", emb)
            counts[scale.name] = counts.get(scale.name, 0) + len(windows)
    return counts


def speech_active_fractions(repo_root: Path, scale: SpeakerWindowScale) -> dict[str, np.ndarray]:
    """Label-agnostic speech-active fraction per speaker window.

    Uses the frozen Day 5 pause rule (fixed -45 dBFS on 25 ms/10 ms frames);
    never reads attack GT, attack intervals, or variant labels. Records with
    frozen Day 5 frames reuse them; the C0 controls get the identical rule
    computed from their own waveform.
    """
    pause: dict[str, list[float]] = defaultdict(list)
    for variant in ("clean", "a0", "a1"):
        path = repo_root / "results/day5_validation" / f"day5_frame_metadata_{variant}.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                pause[row["record_id"]].append(float(row["pause_ratio"]))

    out: dict[str, np.ndarray] = {}

    def build(rid: str, values: np.ndarray, num_samples: int) -> np.ndarray:
        active = 1.0 - np.asarray(values, dtype=np.float64)
        rows = []
        for index in range(scale.window_count(num_samples)):
            lo, hi = scale.bounds(index)
            f_lo = max(0, lo // 160)
            f_hi = min(active.size, (hi + 159) // 160)
            segment = active[f_lo:f_hi]
            rows.append(float(np.mean(segment)) if segment.size else 0.0)
        return np.asarray(rows, dtype=np.float64)

    num_samples_by_id: dict[str, int] = {}
    for row in _read_csv(repo_root / "results/day5_validation/day5_sequence_summary.csv"):
        num_samples_by_id[row["record_id"]] = int(row["num_samples"])
    for rid, values in pause.items():
        out[rid] = build(rid, np.asarray(values, dtype=np.float64), num_samples_by_id.get(rid, len(values) * 160 + 400))

    from audiobookbench.preprocessing.audio_io import load_audio

    for rid, rec in load_c0_records(repo_root).items():
        if rid in out:
            continue
        waveform, _ = load_audio(rec["audio_path"], target_sr=None)
        waveform = np.asarray(waveform, dtype=np.float64)
        frame, hop = 400, 160
        count = 1 + (waveform.size - frame) // hop if waveform.size >= frame else 0
        if count:
            rms = np.sqrt(np.mean(
                np.lib.stride_tricks.sliding_window_view(waveform, frame)[: count * hop][::hop] ** 2,
                axis=1,
            ))
        else:
            rms = np.empty(0)
        pause_flags = (20.0 * np.log10(rms + 1e-12) < -45.0).astype(np.float64)
        out[rid] = build(rid, pause_flags, waveform.size)
    return out


def _score_record(emb: np.ndarray) -> dict[str, np.ndarray]:
    adj, sym = b2_scores(emb)
    return {"B1a": b1_scores(emb, trimmed=False), "B1b": b1_scores(emb, trimmed=True),
            "B2_adjacent": adj, "B2_symmetric": sym}


def _num_samples_from_embeddings(count: int, scale: SpeakerWindowScale) -> int:
    return scale.window_samples + (count - 1) * scale.hop_samples


def _case_metrics(y: np.ndarray, s: np.ndarray, threshold: float) -> dict[str, Any]:
    finite = np.isfinite(s)
    return {
        "case_auroc": _auroc(y, s), "case_auprc": _auprc(y, s), "case_f1": f1_at_threshold(y, s, threshold),
        "n_windows": int(y.size), "n_positive": int(y.sum()),
    }


def run_day6c(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    config = load_day6b_config(repo_root)
    results_dir = repo_root / "results/day6c"
    figures_dir = results_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "config.yaml").write_text(
        (repo_root / "configs/day6b_speaker_consistency.yaml").read_text(encoding="utf-8"), encoding="utf-8",
    )
    precheck = run_day5_precheck(repo_root)

    embed_counts = extract_c0_embeddings(repo_root)
    b6b_records = load_records(repo_root)
    c0_records = load_c0_records(repo_root)
    day6b_scores: dict[str, dict[str, np.ndarray]] = {}
    gt_rows: dict[str, list[dict[str, Any]]] = {}
    windows_by_record: dict[str, list[dict[str, Any]]] = {}
    scale_objs = {e["name"]: SpeakerWindowScale.from_config(e) for e in config["speaker_temporal_grid"]["scales"]}

    per_scale: dict[str, dict[str, Any]] = {}
    c0_score_rows: list[dict[str, Any]] = []
    for name, scale in scale_objs.items():
        records_all: dict[str, dict[str, Any]] = {}
        for rid, rec in b6b_records.items():
            records_all[rid] = rec
        for rid, rec in c0_records.items():
            records_all[rid] = rec
        emb_cache: dict[str, np.ndarray] = {}
        for rid in records_all:
            if rid in b6b_records:
                path = DAY6B_RESULTS / "embeddings" / f"{name}__{rid}.npy"
            else:
                path = results_dir / "embeddings" / f"{name}__{rid}.npy"
            emb_cache[rid] = np.load(path)
        scores_all: dict[str, dict[str, np.ndarray]] = {}
        for rid in records_all:
            scores_all[rid] = _score_record(emb_cache[rid])
            if records_all[rid]["variant"] in C0_VARIANTS:
                rec = records_all[rid]
                for i in range(emb_cache[rid].shape[0]):
                    c0_score_rows.append({
                        "scale": name, "record_id": rid, "variant": rec["variant"],
                        "paired_case_id": rec["paired_case_id"], "split": rec["split"],
                        "window_index": i,
                        **{b: _fmt(scores_all[rid][b][i]) for b in ("B1a", "B1b", "B2_adjacent", "B2_symmetric")},
                    })
            if records_all[rid]["variant"] in VARIANTS or records_all[rid]["variant"] in C0_VARIANTS:
                if records_all[rid]["variant"] in VARIANTS:
                    row = records_all[rid]["manifest_row"]
                    intervals = {
                        "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
                        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
                        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
                        "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
                    }
                else:
                    intervals = _intervals_c0(records_all[rid]["manifest_row"])
                wins = build_speaker_windows(_num_samples_from_embeddings(emb_cache[rid].shape[0], scale), scale)
                windows_by_record[(name, rid)] = wins
                gt_rows[(name, rid)] = project_ground_truth_speaker(wins, intervals, 0.5)
            else:  # clean records: windows only (no attack GT)
                windows_by_record[(name, rid)] = build_speaker_windows(
                    _num_samples_from_embeddings(emb_cache[rid].shape[0], scale), scale)
        per_scale[name] = {"records": records_all, "scores": scores_all, "emb": emb_cache}
        day6b_scores[name] = scores_all

    # ---------------- C1: speech-active mask ----------------
    mask_rows: list[dict[str, Any]] = []
    masks: dict[tuple[str, str], np.ndarray] = {}
    for name, scale in scale_objs.items():
        fractions = speech_active_fractions(repo_root, scale)
        speech_active_fractions_cache[name] = fractions
        for rid in per_scale[name]["records"]:
            fra = fractions[rid]
            n_windows = len(build_speaker_windows(_num_samples_from_embeddings(per_scale[name]["emb"][rid].shape[0], scale), scale))
            keep = (fra >= SPEECH_ACTIVE_THRESHOLD)[:n_windows]
            masks[(name, rid)] = keep
            for i, w in enumerate(build_speaker_windows(_num_samples_from_embeddings(per_scale[name]["emb"][rid].shape[0], scale), scale)):
                mask_rows.append({
                    "scale": name, "record_id": rid,
                    "variant": per_scale[name]["records"][rid]["variant"],
                    "window_index": i, "speech_active_fraction": f"{fra[i]:.6f}",
                    "speech_active": keep[i],
                })
    retained = {name: float(np.mean([masks[(name, rid)].mean() for rid in per_scale[name]["records"]]))
                for name in scale_objs}

    # ---------------- evaluation helpers ----------------
    def pooled(manip_ids: list[str], baseline: str, gt: str, split: str, scale_name: str, masked: bool = False):
        label_col = "is_attack_window" if gt == "full" else "is_core_window"
        y, s = [], []
        for rid in manip_ids:
            rec = per_scale[scale_name]["records"][rid]
            if rec["split"] != split:
                continue
            rows = gt_rows[(scale_name, rid)]
            scores = per_scale[scale_name]["scores"][rid][baseline]
            keep = masks[(scale_name, rid)] if masked else np.ones(len(rows), dtype=bool)
            for i, row in enumerate(rows):
                if not keep[i]:
                    continue
                v = float(scores[i])
                y.append(bool(row[label_col]))
                s.append(v if np.isfinite(v) else np.nan)
        return np.asarray(y), np.asarray(s, dtype=np.float64)

    # train threshold per (scale, baseline, gt) reused from Day6B semantics:
    # computed on TRAIN manipulated windows of the SAME evaluation population.
    def train_threshold(manip_ids: list[str], baseline: str, scale_name: str, masked: bool) -> float:
        y, s = pooled(manip_ids, baseline, "full", "train", scale_name, masked)
        if y.size == 0 or not y.any() or y.all():
            return float("nan")
        cands = np.unique(s[np.isfinite(s)])
        best_tau, best_f1 = float(cands[-1]) + 1e-9, -1.0
        for tau in cands:
            pred = s >= tau
            tp = int(np.sum(y & pred)); fp = int(np.sum(~y & pred)); fn = int(np.sum(y & ~pred))
            f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
            if f1 > best_f1 + 1e-12:
                best_f1, best_tau = f1, float(tau)
        return best_tau

    metric_rows: list[dict[str, Any]] = []
    def eval_variant(variant: str, baseline: str, scale_name: str, label: str, masked: bool = False) -> None:
        ids = [rid for rid, rec in per_scale[scale_name]["records"].items() if rec["variant"] == variant]
        tau = train_threshold(ids, baseline, scale_name, masked)
        for gt in GT_NAMES:
            for split in ("train", "val", "test"):
                y, s = pooled(ids, baseline, gt, split, scale_name, masked)
                r = {"auroc": _auroc(y, s), "auprc": _auprc(y, s), "f1": f1_at_threshold(y, s, tau)}
                metric_rows.append({
                    "scale": scale_name, "baseline": baseline, "gt": gt, "variant": variant,
                    "split": split, "masked": masked, "label": label,
                    "auroc": _fmt(r["auroc"]), "auprc": _fmt(r["auprc"]), "f1": _fmt(r["f1"]),
                    "threshold": _fmt(tau), "n_windows": int(y.size), "n_positive": int(y.sum()),
                })

    for scale_name in scale_objs:
        for v, label in (("a0", "cross_speaker_A0"), ("a1", "cross_speaker_A1"),
                         ("c0a", "same_speaker_C0A"), ("c0b", "same_speaker_C0B")):
            eval_variant(v, "B1b", scale_name, label, masked=False)
            eval_variant(v, "B1b", scale_name, label, masked=True)
            eval_variant(v, "B1a", scale_name, label, masked=False)

    # ---------------- C1 population audit (fixed train thresholds only) ----
    # prevalence / retention by GT class and duration tier; no threshold change.
    population_rows: list[dict[str, Any]] = []
    for name, scale in scale_objs.items():
        manip_ids = [rid for rid, rec in per_scale[name]["records"].items() if rec["variant"] in VARIANTS]
        tau_by_variant = {
            v: train_threshold([rid for rid, rec in per_scale[name]["records"].items()
                                if rec["variant"] == v], "B1b", name, False)
            for v in VARIANTS
        }
        for variant in VARIANTS:
            for split in ("train", "val", "test"):
                # Keep the population audit variant-specific.  The previous
                # implementation pooled A0 and A1 into both labelled rows;
                # localization metrics were unaffected, but counts and
                # retention values in this audit table were mislabeled.
                ids = [
                    rid for rid in manip_ids
                    if per_scale[name]["records"][rid]["split"] == split
                    and per_scale[name]["records"][rid]["variant"] == variant
                ]
                for gt, label_col in (("full", "is_attack_window"), ("core", "is_core_window")):
                    orig_pos = orig_neg = kept_pos = kept_neg = 0
                    for rid in ids:
                        rows = gt_rows[(name, rid)]
                        keep = masks[(name, rid)][: len(rows)]
                        s = per_scale[name]["scores"][rid]["B1b"]
                        pos = np.array([bool(r[label_col]) for r in rows])
                        neg = ~pos
                        orig_pos += int(pos.sum()); orig_neg += int(neg.sum())
                        kept_pos += int((pos & keep).sum()); kept_neg += int((neg & keep).sum())
                    population_rows.append({
                        "scale": name, "variant": variant, "split": split, "gt": gt,
                        "original_positives": orig_pos, "original_negatives": orig_neg,
                        "original_prevalence": _fmt(orig_pos / max(1, orig_pos + orig_neg)),
                        "masked_prevalence": _fmt(kept_pos / max(1, kept_pos + kept_neg)),
                        "positive_retention": _fmt(kept_pos / max(1, orig_pos)),
                        "negative_retention": _fmt(kept_neg / max(1, orig_neg)),
                        "threshold_train_f1": _fmt(tau_by_variant[variant]),
                    })
        # per-tier positive retention (A0/A1, full GT) + FP-per-minute at the
        # fixed train threshold (negative windows above threshold)
        for tier in TIERS:
            for variant in VARIANTS:
                ids = [rid for rid in manip_ids
                       if str(per_scale[name]["records"][rid].get("manifest_row", {}).get("duration_tier", "")) == tier
                       and per_scale[name]["records"][rid]["split"] == "test"]
                if not ids:
                    continue
                tau = tau_by_variant[variant]
                orig_pos = kept_pos = fp_windows = 0
                total_minutes = 0.0
                for rid in ids:
                    rows = gt_rows[(name, rid)]
                    keep = masks[(name, rid)][: len(rows)]
                    pos = np.array([r["is_attack_window"] for r in rows], dtype=bool)
                    s = per_scale[name]["scores"][rid]["B1b"]
                    finite = np.isfinite(s)
                    fp_windows += int(np.sum((s >= tau) & ~pos & finite & keep))
                    orig_pos += int(pos.sum()); kept_pos += int((pos & keep).sum())
                    total_minutes += (rows[-1]["sample_end"] if False else len(rows) * scale.hop_samples / 16000) / 60.0
                population_rows.append({
                    "scale": name, "variant": variant, "split": "test", "gt": f"tier_{tier}",
                    "original_positives": orig_pos, "masked_positive_retention": _fmt(kept_pos / max(1, orig_pos)),
                    "false_positive_windows_masked": fp_windows,
                    "false_positive_minutes_masked": _fmt(fp_windows * scale.hop_samples / 16000 / 60.0),
                    "evaluated_minutes": _fmt(total_minutes),
                    "false_positive_per_minute_masked": _fmt(fp_windows / max(1e-9, total_minutes)),
                    "threshold_train_f1": _fmt(tau),
                })


    # ---------------- cross vs same speaker (per case) ----------------
    compare_rows: list[dict[str, Any]] = []
    contrast_core: dict[str, list[float]] = defaultdict(list)  # scale -> per-case delta
    for name, scale in scale_objs.items():
        for case_id in sorted({rec["paired_case_id"] for rec in c0_records.values()}):
            def find(variant: str) -> str | None:
                return next((rid for rid, rec in per_scale[name]["records"].items()
                             if rec["paired_case_id"] == case_id and rec["variant"] == variant), None)
            rid_a0, rid_a1 = find("a0"), find("a1")
            rid_c0a, rid_c0b = find("c0a"), find("c0b")
            if not all((rid_a0, rid_a1, rid_c0a, rid_c0b)):
                continue
            row = {"scale": name, "paired_case_id": case_id, "split": per_scale[name]["records"][rid_a0]["split"]}
            for tag, rid in (("a0", rid_a0), ("a1", rid_a1), ("c0a", rid_c0a), ("c0b", rid_c0b)):
                rows = gt_rows[(name, rid)]
                s = per_scale[name]["scores"][rid]["B1b"]
                core_mask = np.array([r["is_core_window"] for r in rows])
                boundary_mask = np.array([r["zone"] == "boundary" for r in rows])
                outside_mask = np.array([r["zone"] == "outside" for r in rows])
                for zone, m in (("core", core_mask), ("boundary", boundary_mask), ("outside", outside_mask)):
                    vals = s[m & np.isfinite(s)]
                    row[f"{zone}_anomaly_{tag}"] = _fmt(np.mean(vals)) if vals.size else "nan"
                labels = np.array([r["is_attack_window"] for r in rows])
                row[f"case_auroc_{tag}"] = _fmt(_auroc(labels, s))
            row["delta_core_c0a_minus_a0"] = _fmt(_diff(row["core_anomaly_c0a"], row["core_anomaly_a0"]))
            row["delta_core_c0b_minus_a1"] = _fmt(_diff(row["core_anomaly_c0b"], row["core_anomaly_a1"]))
            compare_rows.append(row)
            if np.isfinite(float(row["delta_core_c0a_minus_a0"])):
                contrast_core[f"{name}|C0A_minus_A0"].append(float(row["delta_core_c0a_minus_a0"]))
                contrast_core[f"{name}|C0B_minus_A1"].append(float(row["delta_core_c0b_minus_a1"]))

    # bootstrap CI for cross-vs-same contrast (case-level resampling)
    boot_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(SEED)
    for key, deltas in sorted(contrast_core.items()):
        scale_name, contrast = key.split("|")
        deltas_arr = np.asarray(deltas, dtype=np.float64)
        means = np.empty(BOOTSTRAP)
        for b in range(BOOTSTRAP):
            idx = rng.integers(0, deltas_arr.size, deltas_arr.size)
            means[b] = deltas_arr[idx].mean()
        boot_rows.append({
            "scale": scale_name, "contrast": contrast, "n_cases": int(deltas_arr.size),
            "mean_delta": _fmt(deltas_arr.mean()), "ci_low": _fmt(np.percentile(means, 2.5)),
            "ci_high": _fmt(np.percentile(means, 97.5)), "resamples": BOOTSTRAP, "seed": SEED,
        })

    # ---------------- C2 duration stratification ----------------
    duration_rows: list[dict[str, Any]] = []
    resolution_rows: list[dict[str, Any]] = []
    for name, scale in scale_objs.items():
        for tier in TIERS:
            for variant in ("a0", "a1", "c0a", "c0b"):
                ids = [rid for rid, rec in per_scale[name]["records"].items()
                       if rec["variant"] == variant
                       and str(rec.get("manifest_row", {}).get("duration_tier", "")) == tier]
                if not ids:
                    continue
                tau = train_threshold([rid for rid, rec in per_scale[name]["records"].items()
                                       if rec["variant"] == variant], "B1b", name, False)
                for split in ("train", "val", "test"):
                    y, s = pooled(ids, "B1b", "full", split, scale_name)
                    core_y, core_s = pooled(ids, "B1b", "core", split, scale_name)
                    outside_s = []
                    for rid in ids:
                        if per_scale[name]["records"][rid]["split"] != split:
                            continue
                        rows = gt_rows[(name, rid)]
                        m = np.array([r["zone"] == "outside" for r in rows])
                        vals = per_scale[name]["scores"][rid]["B1b"][m & np.isfinite(per_scale[name]["scores"][rid]["B1b"])]
                        outside_s.extend(vals.tolist())
                    duration_rows.append({
                        "scale": name, "tier": tier, "variant": variant, "split": split,
                        "case_count": len({per_scale[name]["records"][rid]["paired_case_id"] for rid in ids}),
                        "auroc": _fmt(_auroc(y, s)), "auprc": _fmt(_auprc(y, s)),
                        "f1": _fmt(f1_at_threshold(y, s, tau)),
                        "core_anomaly_mean": _fmt(np.nanmean(core_s)) if core_s.size else "nan",
                        "outside_anomaly_mean": _fmt(np.mean(outside_s)) if outside_s else "nan",
                    })
            # resolution audit per tier (cross-speaker A0/A1 only)
            for variant in ("a0", "a1"):
                ids = [rid for rid, rec in per_scale[name]["records"].items()
                       if rec["variant"] == variant and str(rec["manifest_row"].get("duration_tier", "")) == tier]
                if not ids:
                    continue
                win_s = scale.window_samples / 16000
                pos_full, pos_core, ratios = [], [], []
                for rid in ids:
                    rows = gt_rows[(name, rid)]
                    ratios.append(win_s / float(per_scale[name]["records"][rid]["manifest_row"]["duration_tier"].replace("s", "")))
                    pos_full.append(sum(1 for r in rows if r["is_attack_window"]))
                    pos_core.append(sum(1 for r in rows if r["is_core_window"]))
                resolution_rows.append({
                    "scale": name, "tier": tier, "variant": variant, "n_cases": len(ids),
                    "window_attack_ratio_median": _fmt(np.median(ratios)),
                    "median_full_positive_windows": _fmt(np.median(pos_full)),
                    "median_core_positive_windows": _fmt(np.median(pos_core)),
                })

    # ---------------- C3 case-level ----------------
    case_rows: list[dict[str, Any]] = []
    for name, scale in scale_objs.items():
        for rid, rec in per_scale[name]["records"].items():
            if rec["variant"] not in ("a0", "a1", "c0a", "c0b"):
                continue
            rows = gt_rows[(name, rid)]
            s = per_scale[name]["scores"][rid]["B1b"]
            labels = np.array([r["is_attack_window"] for r in rows], dtype=bool)
            core_mask = np.array([r["is_core_window"] for r in rows], dtype=bool)
            outside_mask = np.array([r["zone"] == "outside" for r in rows], dtype=bool)
            tau = train_threshold([r2 for r2, r3 in per_scale[name]["records"].items()
                                   if r3["variant"] == rec["variant"]], "B1b", name, False)
            case = _case_metrics(labels, s, tau)
            centers = np.array([w["time_center"] for w in windows_by_record[(name, rid)]])
            peak_idx = int(np.nanargmax(np.where(np.isfinite(s), s, -np.inf)))
            core_center = float(np.mean([w["time_center"] for w, r in zip(windows_by_record[(name, rid)], rows) if r["is_core_window"]])) if core_mask.any() else float("nan")
            case_rows.append({
                "scale": name, "record_id": rid, "variant": rec["variant"],
                "paired_case_id": rec["paired_case_id"], "split": rec["split"],
                "case_auroc": _fmt(case["case_auroc"]), "case_auprc": _fmt(case["case_auprc"]),
                "case_f1": _fmt(case["case_f1"]),
                "core_anomaly_median": _fmt(np.nanmedian(s[core_mask])) if core_mask.any() else "nan",
                "core_anomaly_max": _fmt(np.nanmax(np.where(core_mask, s, np.nan))) if core_mask.any() else "nan",
                "outside_anomaly_median": _fmt(np.nanmedian(s[outside_mask])) if outside_mask.any() else "nan",
                "outside_anomaly_max": _fmt(np.nanmax(np.where(outside_mask, s, np.nan))) if outside_mask.any() else "nan",
                "global_peak_time": _fmt(centers[peak_idx]),
                "core_center_time": _fmt(core_center),
                "peak_localization_error_seconds": _fmt(abs(centers[peak_idx] - core_center)) if np.isfinite(core_center) else "nan",
                "n_full_positive_windows": int(labels.sum()),
                "n_core_positive_windows": int(core_mask.sum()),
            })

    # ---------------- C4 clean transition audit ----------------
    lineage = _read_csv(repo_root / "data/manifests/day45_longform_manifest.csv")
    boundaries: dict[str, list[float]] = defaultdict(list)
    # lineage sequence_start/end are already in seconds (frozen manifest)
    for row in lineage:
        sid = row["sequence_id"]
        boundaries[sid].append(float(row["sequence_start"]))
        boundaries[sid].append(float(row["sequence_end"]))
    clean_rows: list[dict[str, Any]] = []
    for name in scale_objs:
        for rid, rec in b6b_records.items():
            if rec["variant"] != "clean" or rid not in per_scale[name]["scores"]:
                continue
            s = per_scale[name]["scores"][rid]["B1b"].copy()
            wins = build_speaker_windows(_num_samples_from_embeddings(per_scale[name]["emb"][rid].shape[0], scale_objs[name]), scale_objs[name])
            order = sorted(range(len(s)), key=lambda i: (-s[i], i))  # desc anomaly, tie by time
            for rank, i in enumerate(order[:3]):
                t = wins[i]["time_center"]
                bnds = boundaries.get(rid, [])
                nearest_boundary = min((abs(t - b) for b in bnds), default=float("nan"))
                clean_rows.append({
                    "scale": name, "record_id": rid, "split": rec["split"], "peak_rank": rank + 1,
                    "peak_time": _fmt(t), "peak_anomaly": _fmt(s[i]),
                    "nearest_utterance_boundary_seconds": _fmt(nearest_boundary),
                    "speech_active_fraction": _fmt(speech_active_fractions_cache[name][rid][i]) if (name in speech_active_fractions_cache and rid in speech_active_fractions_cache[name]) else "nan",
                })

    failure_rows = collect_failures(per_scale, gt_rows, case_rows, compare_rows)
    figure_paths = render_figures(per_scale, gt_rows, windows_by_record, figures_dir, speech_active_fractions_cache)

    _write_csv(results_dir / "speaker_scores_c0.csv", c0_score_rows)
    _write_csv(results_dir / "cross_vs_same_speaker.csv", compare_rows)
    _write_csv(results_dir / "speech_active_mask.csv", mask_rows)
    _write_csv(results_dir / "speech_mask_population_audit.csv", population_rows)
    _write_csv(results_dir / "original_vs_masked_metrics.csv", [r for r in metric_rows])
    _write_csv(results_dir / "duration_stratified_metrics.csv", duration_rows)
    _write_csv(results_dir / "duration_resolution_audit.csv", resolution_rows)
    _write_csv(results_dir / "case_level_metrics.csv", case_rows)
    _write_csv(results_dir / "peak_localization_errors.csv",
               [r for r in case_rows if r["variant"] in ("a0", "a1")])
    _write_csv(results_dir / "bootstrap_ci.csv", boot_rows)
    _write_csv(results_dir / "clean_transition_audit.csv", clean_rows)
    _write_csv(results_dir / "failure_cases.csv", failure_rows)

    day6b_unchanged = verify_day6b_freeze(repo_root)
    summary = {
        "pipeline": "day6c_confound_controls",
        "c0": {"controls": len(c0_records), "verification": verify_against_freeze(repo_root)},
        "speech_mask": {"threshold": SPEECH_ACTIVE_THRESHOLD, "retained_fraction": retained},
        "windows_c0": embed_counts,
        "speaker_disjoint_precheck": precheck["all_passed"],
        "day5_outputs_unchanged": verify_day5_outputs_unchanged(repo_root),
        "day6b_freeze_unchanged": day6b_unchanged,
        "figures": [str(p) for p in figure_paths],
        "bootstrap": {"resamples": BOOTSTRAP, "seed": SEED, "unit": "paired_case_id"},
    }
    (results_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _diff(a: Any, b: Any) -> Any:
    a, b = float(a), float(b)
    return a - b if (np.isfinite(a) and np.isfinite(b)) else float("nan")


speech_active_fractions_cache: dict[str, dict[str, np.ndarray]] = {}


def collect_failures(per_scale: dict[str, Any], gt_rows: dict[Any, Any], case_rows: list[dict[str, Any]], compare_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for name in per_scale:
        # same-speaker C0 high anomaly
        c0_cases = [r for r in case_rows if r["scale"] == name and r["variant"] in ("c0a", "c0b")]
        for r in sorted(c0_cases, key=lambda r: -float(r["core_anomaly_max"]) if np.isfinite(float(r["core_anomaly_max"])) else -9)[:3]:
            failures.append({"scale": name, "failure_type": "same_speaker_high_anomaly",
                             "record_id": r["record_id"], "detail": f"core_max={r['core_anomaly_max']}"})
        # cross-speaker low anomaly
        cross = [r for r in case_rows if r["scale"] == name and r["variant"] in ("a0", "a1")]
        for r in sorted(cross, key=lambda r: float(r["case_auroc"]) if np.isfinite(float(r["case_auroc"])) else 2)[:3]:
            failures.append({"scale": name, "failure_type": "cross_speaker_low_case_auroc",
                             "record_id": r["record_id"], "detail": f"case_auroc={r['case_auroc']}"})
        # 0.75 s misses
        for r in cross:
            if r["record_id"].endswith(tuple(f"_{t}" for t in ())) :
                continue
        # high outside FP
        for r in sorted(cross, key=lambda r: -float(r["outside_anomaly_max"]) if np.isfinite(float(r["outside_anomaly_max"])) else -9)[:3]:
            failures.append({"scale": name, "failure_type": "high_outside_false_positive",
                             "record_id": r["record_id"], "detail": f"outside_max={r['outside_anomaly_max']}"})
        # worst peak error
        for r in sorted(cross, key=lambda r: -float(r["peak_localization_error_seconds"]) if np.isfinite(float(r["peak_localization_error_seconds"])) else -9)[:2]:
            failures.append({"scale": name, "failure_type": "worst_peak_localization_error",
                             "record_id": r["record_id"], "detail": f"error={r['peak_localization_error_seconds']}s"})
    # C0 worse than cross-speaker
    for r in compare_rows:
        try:
            if float(r["delta_core_c0a_minus_a0"]) > 0:
                failures.append({"scale": r["scale"], "failure_type": "same_speaker_anomaly_above_cross",
                                 "record_id": f"paircase={r['paired_case_id']}", "detail": f"delta={r['delta_core_c0a_minus_a0']}"})
        except ValueError:
            continue
    return failures


def render_figures(per_scale: dict[str, Any], gt_rows: dict[Any, Any], windows_by_record: dict[Any, Any],
                   figures_dir: Path, mask_fractions: dict[str, dict[str, np.ndarray]]) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scale_name = "S1_1000ms_250ms"
    scores = per_scale[scale_name]["scores"]
    records = per_scale[scale_name]["records"]
    paths: list[Path] = []

    def gt_arrays(rid: str):
        wins = windows_by_record[(scale_name, rid)]
        t = np.array([w["time_center"] for w in wins])
        rows = gt_rows.get((scale_name, rid))
        if rows is None:  # clean records carry no attack GT
            zeros = np.zeros(len(t))
            return wins, t, zeros, zeros
        return rows, t, np.array([r["attack_overlap_ratio"] for r in rows]), np.array([r["core_overlap_ratio"] for r in rows])

    def bands(ax, t, attack, core):
        # x must be the SAME time axis as the trajectories (seconds), never
        # window indices (integrity fix: index-based bands misplaced the GT).
        ax.fill_between(t, *ax.get_ylim(), where=attack > 0, step="mid", color="#805ad5", alpha=0.15, label="GT full")
        ax.fill_between(t, *ax.get_ylim(), where=core > 0, step="mid", color="#e53e3e", alpha=0.15, label="GT strict core")

    def find(variant: str, case_id: str | None = None, tier: str | None = None) -> str | None:
        for rid, rec in records.items():
            if rec["variant"] != variant:
                continue
            if case_id is not None and rec["paired_case_id"] != case_id:
                continue
            if tier is not None and str(rec.get("manifest_row", {}).get("duration_tier", "")) != tier:
                continue
            return rid
        return None

    # Figure A: cross vs same speaker B1b on one case timeline
    case_id = sorted({rec["paired_case_id"] for rec in records.values() if rec["variant"] == "c0a"})[0]
    rid_a0 = find("a0", case_id)
    rid_a1 = find("a1", case_id)
    rid_c0a = find("c0a", case_id)
    rid_c0b = find("c0b", case_id)
    rid_clean = rid_a0.split("_paircase_")[0] if rid_a0 else None
    rows, t, attack, core = gt_arrays(rid_a0 or rid_c0a)
    fig, ax = plt.subplots(figsize=(14, 5))
    series = [("clean", "#2b6cb0", rid_clean), ("A0", "#c05621", rid_a0), ("A1", "#2f855a", rid_a1),
              ("C0A", "#805ad5", rid_c0a), ("C0B", "#d69e2e", rid_c0b)]
    for label, color, rid in series:
        if rid is None or rid not in scores:
            continue
        vals = scores[rid]["B1b"]
        ax.plot(t[:len(vals)] if len(vals) != len(t) else t, vals, label=label, color=color, lw=0.9, alpha=0.85)
    bands(ax, t, attack, core)
    ax.set_title(f"Figure A: cross-speaker (A0/A1) vs same-speaker (C0A/C0B) B1b — {case_id}")
    ax.set_xlabel("time (s)"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); out = figures_dir / "figureA_cross_vs_same.png"
    fig.savefig(out, dpi=150); plt.close(fig); paths.append(out)

    # Figure B: original vs speech-active masked (A0 of the same case)
    if rid_a0:
        rows, t, attack, core = gt_arrays(rid_a0)
        s = scores[rid_a0]["B1b"]
        fra = mask_fractions[scale_name][rid_a0]
        masked = np.where(fra >= SPEECH_ACTIVE_THRESHOLD, s, np.nan)
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(t, s, label="original", color="#c05621", lw=0.9)
        ax.plot(t, masked, ".", ms=5, label="speech-active masked", color="#2b6cb0")
        bands(ax, t, attack, core)
        ax.set_title(f"Figure B: original vs speech-active masked B1b — {rid_a0}")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        fig.tight_layout(); out = figures_dir / "figureB_original_vs_masked.png"
        fig.savefig(out, dpi=150); plt.close(fig); paths.append(out)

    # Figures C/D: shortest vs longest duration tier (cross-speaker A0)
    for tier, out_name, title in (("0.75s", "figureC_075s_case.png", "Figure C: 0.75 s case (hardest tier)"),
                                  ("2.5s", "figureD_2500ms_case.png", "Figure D: 2.5 s case")):
        rid = find("a0", tier=tier)
        if rid is None:
            continue
        rows, t, attack, core = gt_arrays(rid)
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(t, scores[rid]["B1b"], label="A0 B1b", color="#c05621", lw=0.9)
        bands(ax, t, attack, core)
        ax.set_title(f"{title} — {rid}")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        fig.tight_layout(); out = figures_dir / out_name
        fig.savefig(out, dpi=150); plt.close(fig); paths.append(out)

    # Figure E: clean record with the highest single B1 peak (transition FP audit)
    clean_ids = [rid for rid, rec in records.items() if rec["variant"] == "clean" and rid in scores]
    if clean_ids:
        rid = max(clean_ids, key=lambda r: float(np.nanmax(scores[r]["B1b"])))
        rows, t, attack, core = gt_arrays(rid)
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(t, scores[rid]["B1b"], label="clean B1b", color="#2b6cb0", lw=0.9)
        bands(ax, t, np.zeros_like(attack), np.zeros_like(core))
        ax.set_title(f"Figure E: clean highest-anomaly case — {rid}")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        fig.tight_layout(); out = figures_dir / "figureE_clean_fp.png"
        fig.savefig(out, dpi=150); plt.close(fig); paths.append(out)
    return paths


_MASK_CACHE: dict[tuple[str, str], list[dict[str, str]]] = {}


def _mask_rows_for(scale_name: str, rid: str) -> list[dict[str, str]]:
    key = (scale_name, rid)
    if key not in _MASK_CACHE:
        _MASK_CACHE[key] = _read_csv(DAY6C / "speech_active_mask.csv")
    return [r for r in _MASK_CACHE[key] if r["scale"] == scale_name and r["record_id"] == rid]


def verify_day6b_freeze(repo_root: Path = REPO_ROOT) -> bool:
    import hashlib

    record_path = repo_root / "results/day6c/day6b_freeze_record.json"
    if not record_path.exists():
        return False
    record = json.loads(record_path.read_text(encoding="utf-8"))
    for relpath, expected in record["hashes"].items():
        path = repo_root / relpath
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

    parser = argparse.ArgumentParser(description="Run the Day 6C confound-control pipeline.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    summary = run_day6c(Path(args.repo_root))
    print(json.dumps(summary, indent=2))
    gates = [summary["c0"]["verification"], summary["speaker_disjoint_precheck"],
             summary["day5_outputs_unchanged"], summary["day6b_freeze_unchanged"]]
    return 0 if all(gates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
