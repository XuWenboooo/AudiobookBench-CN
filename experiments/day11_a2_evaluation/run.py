"""Day 11 frozen A2 detector evaluation (B0/B1a/B1b/B2 only)."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from collections import defaultdict

import numpy as np

REPO_ROOT = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from audiobookbench.data.manifest import load_manifest
from audiobookbench.preprocessing.audio_io import load_audio
from audiobookbench.security.day8_detector_denylist import assert_detector_inputs_safe
from audiobookbench.temporal.aggregation import (
    AggregationScale, aggregate_window_features, build_aggregation_grid, project_ground_truth,
)
from audiobookbench.temporal.day6a_scoring import combine_scores, compute_reference, feature_zscore_matrix
from audiobookbench.temporal.day6b_embed import SpeakerBackend, SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import b1_scores, b2_scores, project_ground_truth_speaker
from audiobookbench.temporal.frame_features import extract_frame_features
from audiobookbench.temporal.grid import TemporalGrid
from audiobookbench.evaluation.day6a_localization import auprc, auroc, f1_at_threshold

RESULTS = REPO_ROOT / "results" / "day11"
DAY10 = REPO_ROOT / "results" / "day10"
SIDE_CAR = DAY10 / "a2_sidecar.csv"
FREEZE = DAY10 / "day10_output_hashes.json"
PLAN = REPO_ROOT / "data" / "manifests" / "week2a_a2_planned_manifest.csv"
LONGFORM = REPO_ROOT / "data" / "manifests" / "day45_longform_manifest.csv"
SAMPLE_RATE = 16000
SEED = 20260905
BOOTSTRAP = 2000

FEATURE_DEFS = {
    "log_energy_mean": {"signal": "log_energy", "stat": "mean"},
    "log_energy_std": {"signal": "log_energy", "stat": "std"},
    "log_energy_min": {"signal": "log_energy", "stat": "min"},
    "log_energy_max": {"signal": "log_energy", "stat": "max"},
    "rms_mean": {"signal": "rms", "stat": "mean"},
    "rms_std": {"signal": "rms", "stat": "std"},
    "f0_median": {"signal": "f0_hz", "stat": "nanmedian"},
    "f0_std": {"signal": "f0_hz", "stat": "nanstd"},
    "voiced_fraction": {"signal": "voiced_ratio", "stat": "mean"},
    "pause_fraction": {"signal": "pause_ratio", "stat": "mean"},
}
CHANNELS = {
    "f0": ["f0_median", "f0_std"],
    "energy": ["log_energy_mean", "log_energy_std", "log_energy_min", "log_energy_max"],
    "rms": ["rms_mean", "rms_std"],
    "voicing": ["voiced_fraction", "valid_f0_fraction"],
    "pause": ["pause_fraction"],
}
# Day 6A's feature definitions derive valid_f0_fraction from f0_hz. Keep the
# frozen name explicit while using the same channel semantics.
FEATURE_DEFS["valid_f0_fraction"] = {"signal": "f0_hz", "stat": "finite_fraction"}
ABLATION_CHANNELS = {"ALL": ["f0", "energy", "rms", "voicing", "pause"]}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def verify_day10_freeze() -> tuple[list[dict[str, str]], dict[str, object]]:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("planned") != 23 or freeze.get("succeeded") != 23 or freeze.get("failed_by_class"):
        raise RuntimeError("Day10 denominator is not frozen 23/23")
    sidecar = read_csv(SIDE_CAR)
    if len(sidecar) != 23 or {r["generation_status"] for r in sidecar} != {"success"}:
        raise RuntimeError("Day10 sidecar is not 23 successful rows")
    frozen = {str(item["paired_case_id"]): item for item in freeze["output_hashes"]}
    if set(frozen) != {r["paired_case_id"] for r in sidecar}:
        raise RuntimeError("Day10 hash freeze case set mismatch")
    for row in sidecar:
        path = Path(row["manipulated_audio_path"])
        item = frozen[row["paired_case_id"]]
        if not path.is_file() or path.stat().st_size != int(item["bytes"]) or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Day10 waveform hash mismatch: {row['paired_case_id']}")
    return sidecar, freeze


def intervals(row: dict[str, str]) -> dict[str, tuple[int, int]]:
    return {
        "target": (int(row["clean_timeline_start_sample"]), int(row["clean_timeline_end_sample"])),
        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
        "blend": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
    }


def metrics_for(y: np.ndarray, score: np.ndarray, threshold: float) -> dict[str, float | int]:
    finite = np.isfinite(score)
    return {"auroc": auroc(y, score), "auprc": auprc(y, score),
            "f1": f1_at_threshold(y, score, threshold), "n_windows": int(y.size),
            "n_positive": int(np.asarray(y).astype(bool).sum()), "n_finite": int(finite.sum())}


def case_ci(score_map: dict[str, np.ndarray], gt: dict[str, list[dict[str, object]]],
            ids: list[str], label: str, resamples: int = BOOTSTRAP, seed: int = SEED) -> dict[str, object]:
    """Case-level percentile CI; each resample draws whole cases, never windows."""
    case_data = [(rid, np.asarray([bool(r[label]) for r in gt[rid]]),
                  np.asarray(score_map[rid], dtype=float)) for rid in ids]
    if len(case_data) < 2:
        return {"n_cases": len(case_data), "resamples": resamples, "seed": seed,
                "auroc_ci": ["nan", "nan"], "auprc_ci": ["nan", "nan"]}
    rng = np.random.default_rng(seed)
    aurocs, auprcs = [], []
    for _ in range(resamples):
        chosen = rng.integers(0, len(case_data), size=len(case_data))
        y = np.concatenate([case_data[i][1] for i in chosen])
        s = np.concatenate([case_data[i][2] for i in chosen])
        aurocs.append(auroc(y, s)); auprcs.append(auprc(y, s))
    def ci(values: list[float]) -> list[float | str]:
        finite = np.asarray(values)[np.isfinite(values)]
        return [float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))] if finite.size else ["nan", "nan"]
    return {"n_cases": len(case_data), "resamples": resamples, "seed": seed,
            "auroc_ci": ci(aurocs), "auprc_ci": ci(auprcs)}


def load_frozen_thresholds() -> dict[tuple[str, str, str], float]:
    out: dict[tuple[str, str, str], float] = {}
    for path, key_index in ((REPO_ROOT / "results/day6a/metrics_by_split.csv", "ablation"),
                            (REPO_ROOT / "results/day6b/metrics_by_split.csv", "baseline")):
        for row in read_csv(path):
            if row["variant"] == "a0" and row["split"] == "train" and row["gt"] == "full":
                out[(row["scale"], row[key_index], "train_f1")] = float(row["threshold"])
    required = [("100ms", "ALL", "train_f1"), ("250ms", "ALL", "train_f1"), ("500ms", "ALL", "train_f1"),
                ("S1_1000ms_250ms", "B1a", "train_f1"), ("S1_1000ms_250ms", "B1b", "train_f1"),
                ("S1_1000ms_250ms", "B2_adjacent", "train_f1"), ("S1_1000ms_250ms", "B2_symmetric", "train_f1"),
                ("S2_1500ms_250ms", "B1a", "train_f1"), ("S2_1500ms_250ms", "B1b", "train_f1"),
                ("S2_1500ms_250ms", "B2_adjacent", "train_f1"), ("S2_1500ms_250ms", "B2_symmetric", "train_f1")]
    if any(item not in out for item in required):
        raise RuntimeError("frozen Week1 threshold missing")
    return out


def main() -> int:
    if RESULTS.exists():
        raise RuntimeError(f"refusing to overwrite existing Day11 results: {RESULTS}")
    sidecar, freeze = verify_day10_freeze()
    thresholds = load_frozen_thresholds()
    plans = {r["paired_case_id"]: r for r in read_csv(PLAN)}
    longform = {r["sequence_id"]: r for r in read_csv(LONGFORM)}
    if set(plans) != {r["paired_case_id"] for r in sidecar}:
        raise RuntimeError("Day10 sidecar does not match planned population")
    split_counts = {s: sum(r["split"] == s for r in sidecar) for s in ("train", "val", "test")}
    if split_counts != {"train": 11, "val": 6, "test": 6}:
        raise RuntimeError(f"split mismatch: {split_counts}")
    assert_detector_inputs_safe({"waveform": np.zeros(16000, dtype=np.float32)})

    grid = TemporalGrid()
    records: dict[str, dict[str, object]] = {}
    waveforms: dict[str, np.ndarray] = {}
    for row in sidecar:
        rid = row["paired_case_id"]
        manipulated, sr = load_audio(row["manipulated_audio_path"], target_sr=SAMPLE_RATE)
        if sr != SAMPLE_RATE or manipulated.ndim != 1 or not np.isfinite(manipulated).all():
            raise RuntimeError(f"invalid Day10 waveform: {rid}")
        clean, clean_sr = load_audio(longform[row["clean_sequence_id"]]["sequence_audio_path"], target_sr=SAMPLE_RATE)
        if clean_sr != SAMPLE_RATE:
            raise RuntimeError(f"invalid clean waveform: {rid}")
        records[rid] = {"paired_case_id": rid, "split": row["split"], "speaker": row["target_speaker"],
                        "variant": "a2", "row": row, "clean": clean}
        waveforms[rid] = manipulated

    score_rows: list[dict[str, object]] = []
    gt_rows_out: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    case_rows: list[dict[str, object]] = []
    bootstrap_rows: list[dict[str, object]] = []
    threshold_rows: list[dict[str, object]] = []

    # B0: recompute the frozen Day-5 feature family on the A2 manipulated
    # timeline; train reference is clean-only and never uses A2 GT.
    b0_scales = [AggregationScale(name=n, window_frames=f, hop_frames=f, hop_length=160)
                 for n, f in (("100ms", 10), ("250ms", 25), ("500ms", 50))]
    b0_scores: dict[str, dict[str, np.ndarray]] = {}
    b0_gt: dict[str, list[dict[str, object]]] = {}
    b0_meta: dict[str, dict[str, object]] = {}
    for scale in b0_scales:
        clean_features: dict[str, list[float]] = {name: [] for name in FEATURE_DEFS}
        per_case: dict[str, tuple[list[dict[str, object]], list[dict[str, object]], list[object]]] = {}
        for rid, rec in records.items():
            for waveform, is_clean in ((rec["clean"], True), (waveforms[rid], False)):
                frames = extract_frame_features(waveform, grid)
                windows = build_aggregation_grid(len(frames["energy"]), scale, grid)
                feats = [aggregate_window_features(frames, win, FEATURE_DEFS) for win in windows]
                if is_clean and rec["split"] == "train":
                    for feat in feats:
                        for name in FEATURE_DEFS:
                            clean_features[name].append(float(feat[name]))
                if not is_clean:
                    gt = project_ground_truth(windows, intervals(rec["row"]), 0.5)
                    per_case[rid] = (feats, gt, windows)
        reference = compute_reference({k: np.asarray(v) for k, v in clean_features.items()}, FEATURE_DEFS)
        for rid, (feats, gt, windows) in per_case.items():
            z = feature_zscore_matrix({k: np.asarray([x[k] for x in feats]) for k in FEATURE_DEFS}, reference, FEATURE_DEFS)
            score = combine_scores(z, CHANNELS, ABLATION_CHANNELS["ALL"], min_valid_features=1)["combined"]
            b0_scores[rid] = {"B0": score}; b0_gt[rid] = gt
            b0_meta[rid] = records[rid]
            for i, (value, g) in enumerate(zip(score, gt)):
                score_rows.append({"case_id": rid, "split": records[rid]["split"], "method": "B0", "scale": scale.name,
                                   "window_index": i, "sample_start": windows[i].sample_start, "sample_end": windows[i].sample_end,
                                   "score": float(value) if np.isfinite(value) else "nan", "attack_overlap_ratio": g["attack_overlap_ratio"],
                                   "core_overlap_ratio": g["core_overlap_ratio"], "zone": g["zone"],
                                   "is_attack_window": g["is_attack_window"], "is_core_window": g["is_core_window"]})
                gt_rows_out.append({"case_id": rid, "split": records[rid]["split"], "method": "B0", "scale": scale.name,
                                    "window_index": i, "sample_start": windows[i].sample_start, "sample_end": windows[i].sample_end,
                                    "attack_overlap_ratio": g["attack_overlap_ratio"], "core_overlap_ratio": g["core_overlap_ratio"],
                                    "zone": g["zone"], "is_attack_window": g["is_attack_window"], "is_core_window": g["is_core_window"]})
        tau = thresholds[(scale.name, "ALL", "train_f1")]
        threshold_rows.append({"method": "B0", "scale": scale.name, "threshold_rule": "Week1_train_f1", "threshold": tau,
                               "source": "results/day6a/metrics_by_split.csv", "a2_tuning": False})
        _evaluate_method("B0", scale.name, b0_scores, b0_gt, b0_meta, tau, metric_rows, case_rows, bootstrap_rows)

    # B1a/B1b/B2: suspect waveform only; no reference/GT metadata enters the
    # embedding or scoring functions.
    backend = SpeakerBackend()
    scales = [SpeakerWindowScale("S1_1000ms_250ms", 16000, 4000), SpeakerWindowScale("S2_1500ms_250ms", 24000, 4000)]
    for scale in scales:
        score_by_method: dict[str, dict[str, np.ndarray]] = {m: {} for m in ("B1a", "B1b", "B2_adjacent", "B2_symmetric")}
        gt_by_case: dict[str, list[dict[str, object]]] = {}
        meta = {rid: records[rid] for rid in records}
        for rid, waveform in waveforms.items():
            assert_detector_inputs_safe({"waveform": waveform})
            windows = build_speaker_windows(waveform.size, scale)
            emb = backend.embed_windows(waveform, [(w["sample_start"], w["sample_end"]) for w in windows])
            s1, s2 = b2_scores(emb)
            scores = {"B1a": b1_scores(emb, False), "B1b": b1_scores(emb, True), "B2_adjacent": s1, "B2_symmetric": s2}
            gt = project_ground_truth_speaker(windows, intervals(records[rid]["row"]), 0.5)
            gt_by_case[rid] = gt
            for method, values in scores.items():
                score_by_method[method][rid] = values
                for i, (value, g, w) in enumerate(zip(values, gt, windows)):
                    score_rows.append({"case_id": rid, "split": records[rid]["split"], "method": method, "scale": scale.name,
                                       "window_index": i, "sample_start": w["sample_start"], "sample_end": w["sample_end"],
                                       "score": float(value) if np.isfinite(value) else "nan", "attack_overlap_ratio": g["attack_overlap_ratio"],
                                       "core_overlap_ratio": g["core_overlap_ratio"], "zone": g["zone"],
                                       "is_attack_window": g["is_attack_window"], "is_core_window": g["is_core_window"]})
                    gt_rows_out.append({"case_id": rid, "split": records[rid]["split"], "method": method, "scale": scale.name,
                                        "window_index": i, "sample_start": w["sample_start"], "sample_end": w["sample_end"],
                                        "attack_overlap_ratio": g["attack_overlap_ratio"], "core_overlap_ratio": g["core_overlap_ratio"],
                                        "zone": g["zone"], "is_attack_window": g["is_attack_window"], "is_core_window": g["is_core_window"]})
        for method in score_by_method:
            tau = thresholds[(scale.name, method, "train_f1")]
            threshold_rows.append({"method": method, "scale": scale.name, "threshold_rule": "Week1_train_f1", "threshold": tau,
                                   "source": "results/day6b/metrics_by_split.csv", "a2_tuning": False})
            _evaluate_method(method, scale.name, score_by_method[method], gt_by_case, meta, tau,
                             metric_rows, case_rows, bootstrap_rows)

    write_csv(RESULTS / "score_timeline.csv", score_rows)
    write_csv(RESULTS / "gt_timeline.csv", gt_rows_out)
    write_csv(RESULTS / "metrics_by_split.csv", metric_rows)
    write_csv(RESULTS / "case_level_metrics.csv", case_rows)
    write_csv(RESULTS / "case_bootstrap_ci.csv", bootstrap_rows)
    write_csv(RESULTS / "threshold_provenance.csv", threshold_rows)
    write_json(RESULTS / "freeze_verification.json", {"status": "PASS", "day10_hash_file": str(FREEZE),
               "day10_hash_sha256": sha256_file(FREEZE), "cases": 23, "split": split_counts,
               "sidecar_sha256": sha256_file(SIDE_CAR), "no_mutation": True})
    write_json(RESULTS / "evaluation_summary.json", {"status": "PASS", "methods": ["B0", "B1a", "B1b", "B2"],
               "b3_primary": "NOT_RUN", "b4": "NOT_RUN", "threshold_reuse": True,
               "a2_specific_tuning": False, "detector_leakage": "PASS", "timeline_gt": "PASS",
               "case_level_bootstrap": {"unit": "paired_case_id", "resamples": BOOTSTRAP, "seed": SEED},
               "day12_entered": False})
    return 0


def _evaluate_method(method: str, scale: str, scores: dict[str, dict[str, np.ndarray]] | dict[str, np.ndarray],
                     gt: dict[str, list[dict[str, object]]], meta: dict[str, dict[str, object]], tau: float,
                     metric_rows: list[dict[str, object]], case_rows: list[dict[str, object]],
                     bootstrap_rows: list[dict[str, object]]) -> None:
    if method == "B0":
        score_map = scores  # type: ignore[assignment]
    else:
        score_map = {rid: {method: value} for rid, value in scores.items()}  # type: ignore[union-attr]
    for split in ("train", "val", "test"):
        for gt_name, label in (("full", "is_attack_window"), ("core", "is_core_window")):
            ids = [rid for rid in sorted(score_map) if meta[rid]["split"] == split]
            y = np.concatenate([np.asarray([bool(r[label]) for r in gt[rid]]) for rid in ids])
            s = np.concatenate([np.asarray(score_map[rid][method], dtype=float) for rid in ids])
            result = metrics_for(y, s, tau)
            metric_rows.append({"method": method, "scale": scale, "split": split, "gt": gt_name,
                                "threshold": tau, "threshold_source": "Week1_train_f1", **result})
            ci = case_ci({rid: score_map[rid][method] for rid in ids}, {rid: gt[rid] for rid in ids}, ids,
                          "is_attack_window" if gt_name == "full" else "is_core_window", BOOTSTRAP, SEED)
            bootstrap_rows.append({"method": method, "scale": scale, "split": split, "gt": gt_name,
                                   **ci, "unit": "paired_case_id"})
    for rid in sorted(score_map):
        for gt_name, label in (("full", "is_attack_window"), ("core", "is_core_window")):
            y = np.asarray([bool(r[label]) for r in gt[rid]])
            s = np.asarray(score_map[rid][method], dtype=float)
            result = metrics_for(y, s, tau)
            case_rows.append({"case_id": rid, "split": meta[rid]["split"], "method": method, "scale": scale,
                              "gt": gt_name, "threshold": tau, **result})


if __name__ == "__main__":
    raise SystemExit(main())
