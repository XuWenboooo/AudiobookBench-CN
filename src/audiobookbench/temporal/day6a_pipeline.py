"""Day 6A pipeline: temporal aggregation + non-trained localization baseline.

Read-only over every frozen artifact (Day 3/3.5/4/4.5 data, Day 5 frame
features). New results are written only under ``results/day6a/``.

Pipeline per frozen aggregation scale (100/250/500 ms):

1. aggregate Day 5 frame signals into window features;
2. project attack/core/blend ground truth onto windows (majority rule 0.5);
3. estimate a robust reference (median/MAD) from TRAIN CLEAN windows only;
4. score every window with B0 robust z-scores: combined score per ablation
   set (ALL / NO_PAUSE / NO_ENERGY) plus per-channel scores;
5. derive two pre-declared thresholds (fixed |z| = 3.5 and a train-only
   max-F1 rule) and evaluate AUROC/AUPRC/F1 per split x variant x GT;
6. run the boundary-shortcut audit, paired A0/A1 analysis, deterministic
   failure-case collection and deterministic sanity figures.

No model is trained and no threshold is ever tuned on val/test.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from audiobookbench.evaluation.day6a_localization import (
    evaluate_windows,
    f1_at_threshold,
    zone_statistics,
)
from audiobookbench.security.day5_precheck import REPO_ROOT, run_day5_precheck
from audiobookbench.temporal.aggregation import (
    AggregationScale,
    aggregate_window_features,
    build_aggregation_grid,
    project_ground_truth,
)
from audiobookbench.temporal.day6a_scoring import (
    best_f1_threshold,
    combine_scores,
    compute_reference,
    feature_zscore_matrix,
)
from audiobookbench.temporal.grid import TemporalGrid

DAY5_RESULTS = REPO_ROOT / "results/day5_validation"
DAY6A_RESULTS = REPO_ROOT / "results/day6a"
CONFIG_PATH = REPO_ROOT / "configs/day6a_localization_baseline.yaml"

ABLATION_NAMES = ("ALL", "NO_PAUSE", "NO_ENERGY")
GT_NAMES = ("full", "core")
SPLITS = ("train", "val", "test")
VARIANTS = ("a0", "a1")


def load_config(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((repo_root / "configs/day6a_localization_baseline.yaml").read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_day5_frames(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Parse the three frozen Day 5 frame-metadata CSVs once into arrays."""
    identity: dict[str, dict[str, str]] = {}
    for row in _read_csv(DAY5_RESULTS / "day5_sequence_summary.csv"):
        identity[row["record_id"]] = row
    manifest_by_record: dict[str, dict[str, str]] = {}
    for row in _read_csv(repo_root / "data/manifests/day45_attack_manifest.csv"):
        manifest_by_record[row["manipulated_sequence_id"]] = row

    frames: dict[str, dict[str, list[float]]] = defaultdict(lambda: {s: [] for s in (
        "energy", "log_energy", "rms", "f0_hz", "voiced_ratio", "pause_ratio")})
    order: dict[str, list[int]] = defaultdict(list)
    for variant in ("clean", "a0", "a1"):
        with (DAY5_RESULTS / f"day5_frame_metadata_{variant}.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                rid = row["record_id"]
                for signal in frames[rid]:
                    frames[rid][signal].append(float(row[signal]))
                order[rid].append(int(row["frame_index"]))

    records: dict[str, dict[str, Any]] = {}
    for rid, signals in frames.items():
        meta = identity[rid]
        arrays = {name: np.asarray(values, dtype=np.float64) for name, values in signals.items()}
        expected_order = list(range(len(order[rid])))
        assert order[rid] == expected_order, f"frame rows out of order in {rid}"
        record: dict[str, Any] = {
            "record_id": rid,
            "variant": meta["variant"],
            "split": meta["split"],
            "speaker": meta["speaker"],
            "paired_case_id": meta["paired_case_id"],
            "frames": arrays,
            "frame_count": int(meta["frame_count"]),
            "num_samples": int(meta["num_samples"]),
        }
        if meta["variant"] in VARIANTS:
            record["manifest_row"] = manifest_by_record[rid]
            assert record["paired_case_id"] == record["manifest_row"]["paired_case_id"]
        records[rid] = record
    return records


def _intervals_from_manifest(row: Mapping[str, str]) -> dict[str, tuple[int, int]]:
    return {
        "target": (int(row["target_start_sample"]), int(row["target_end_sample"])),
        "attack": (int(row["attack_start_sample"]), int(row["attack_end_sample"])),
        "core": (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])),
        "blend": (int(row["blend_start_sample"]), int(row["blend_end_sample"])),
    }


def aggregate_record_windows(
    record: Mapping[str, Any],
    scale: AggregationScale,
    grid: TemporalGrid,
    feature_defs: Mapping[str, Mapping[str, str]],
    label_threshold: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Aggregate one record; returns (feature_rows, gt_rows)."""
    windows = build_aggregation_grid(record["frame_count"], scale, grid)
    base = {
        "record_id": record["record_id"],
        "variant": record["variant"],
        "paired_case_id": record.get("paired_case_id", ""),
        "split": record["split"],
        "speaker": record["speaker"],
    }
    feature_rows: list[dict[str, Any]] = []
    gt_rows: list[dict[str, Any]] = []
    for window in windows:
        row = window.as_row(base)
        row.update(aggregate_window_features(record["frames"], window, feature_defs))
        feature_rows.append(row)
        if "manifest_row" in record:
            gt_row = project_ground_truth([window], _intervals_from_manifest(record["manifest_row"]), label_threshold)[0]
            gt_row["record_id"] = record["record_id"]
            gt_row["variant"] = record["variant"]
            gt_row["paired_case_id"] = record["paired_case_id"]
            gt_row["split"] = record["split"]
            gt_rows.append(gt_row)
    return feature_rows, gt_rows


def _to_float(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return result


def run_day6a(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    config = load_config(repo_root)
    results_dir = repo_root / "results/day6a"
    figures_dir = results_dir / "figures"
    reference_dir = results_dir / "reference"
    for directory in (results_dir, figures_dir, reference_dir):
        directory.mkdir(parents=True, exist_ok=True)
    (results_dir / "config.yaml").write_text(
        (repo_root / "configs/day6a_localization_baseline.yaml").read_text(encoding="utf-8"), encoding="utf-8",
    )

    precheck = run_day5_precheck(repo_root)
    grid = TemporalGrid()
    feature_defs = config["window_features"]
    channels = config["feature_channels"]
    ablations = config["ablations"]
    label_threshold = float(config["gt_projection"]["label_threshold"])
    eps = float(config["reference"]["eps"])
    z_cap = float(config["reference"].get("z_cap", 1.0e4))
    fixed_abs_z = float(config["threshold"]["fixed_abs_z"])
    min_valid = int(config["anomaly"]["min_valid_features"])
    feature_names = list(feature_defs)

    records = load_day5_frames(repo_root)

    scale_names = [entry["name"] for entry in config["aggregation"]["scales"]]
    all_feature_rows: list[dict[str, Any]] = []
    all_score_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    zone_audit: dict[str, Any] = {}
    per_scale_context: dict[str, Any] = {}

    for entry in config["aggregation"]["scales"]:
        scale = AggregationScale.from_config(entry, grid.hop_length)
        record_windows: dict[str, list[dict[str, Any]]] = {}
        record_gt: dict[str, list[dict[str, Any]]] = {}
        record_scores: dict[str, dict[str, np.ndarray]] = {}

        for record in records.values():
            feat_rows, gt_rows = aggregate_record_windows(record, scale, grid, feature_defs, label_threshold)
            record_windows[record["record_id"]] = feat_rows
            record_gt[record["record_id"]] = gt_rows
            all_feature_rows.extend(feat_rows)

        # ---- train-clean-only reference ----
        train_clean_ids = sorted(
            rid for rid, rec in records.items() if rec["variant"] == "clean" and rec["split"] == "train"
        )
        ref_source: dict[str, list[float]] = {name: [] for name in feature_names}
        for rid in train_clean_ids:
            for row in record_windows[rid]:
                for name in feature_names:
                    ref_source[name].append(_to_float(row[name]))
        reference = compute_reference(
            {name: np.asarray(values, dtype=np.float64) for name, values in ref_source.items()},
            feature_names, eps=eps,
        )
        reference_rows = [
            {"scale": scale.name, "feature": name, **reference[name], "source": "TRAIN_CLEAN_ONLY"}
            for name in feature_names
        ]

        # ---- z-scores, combinations, channels, ablations ----
        for rid, feat_rows in record_windows.items():
            z = feature_zscore_matrix(
                {name: np.array([_to_float(row[name]) for row in feat_rows]) for name in feature_names},
                reference, feature_names, cap=z_cap,
            )
            scores: dict[str, np.ndarray] = {}
            for ablation, channel_list in ablations.items():
                combo = combine_scores(z, channels, channel_list, per_channel=False, min_valid_features=min_valid)
                scores[f"combined_{ablation}"] = combo["combined"]
                scores[f"n_valid_{ablation}"] = combo["n_valid_features"]
            for channel in channels:
                per_channel = combine_scores(z, channels, [channel], per_channel=False, min_valid_features=min_valid)
                scores[f"channel_{channel}"] = per_channel["combined"]
            record_scores[rid] = scores
            variant = records[rid]["variant"]
            for i, row in enumerate(feat_rows):
                score_row = {
                    "scale": scale.name,
                    "record_id": rid,
                    "variant": variant,
                    "paired_case_id": row["paired_case_id"],
                    "split": row["split"],
                    "window_index": row["window_index"],
                    "t_start": row["t_start"],
                    "t_center": row["t_center"],
                    "t_end": row["t_end"],
                }
                for key, values in scores.items():
                    v = values[i]
                    score_row[key] = f"{v:.6f}" if np.isfinite(v) else "nan"
                if gt_rows := record_gt.get(rid):
                    if i < len(gt_rows):
                        score_row.update({
                            "attack_overlap_ratio": gt_rows[i]["attack_overlap_ratio"],
                            "core_overlap_ratio": gt_rows[i]["core_overlap_ratio"],
                            "blend_overlap_ratio": gt_rows[i]["blend_overlap_ratio"],
                            "is_attack_window": gt_rows[i]["is_attack_window"],
                            "is_core_window": gt_rows[i]["is_core_window"],
                            "is_blend_window": gt_rows[i]["is_blend_window"],
                            "zone": gt_rows[i]["zone"],
                        })
                all_score_rows.append(score_row)

        # ---- thresholds: train-only ----
        thresholds: dict[tuple[str, str], float] = {}
        for ablation in ablations:
            y_train, s_train = _collect(record_gt, record_scores, records, "train", ablation, "full")
            thresholds[(ablation, "fixed")] = fixed_abs_z
            thresholds[(ablation, "train_f1")] = best_f1_threshold(np.asarray(y_train), np.asarray(s_train))

        # ---- evaluation per split x variant x gt x ablation ----
        for ablation in ablations:
            for gt in GT_NAMES:
                label_col = "is_attack_window" if gt == "full" else "is_core_window"
                for variant in VARIANTS:
                    for split in SPLITS:
                        y, s = _collect(record_gt, record_scores, records, split, ablation, gt, variant=variant, label_col=label_col)
                        tau = thresholds[(ablation, "train_f1")]
                        result = evaluate_windows(np.asarray(y), np.asarray(s), tau)
                        result.update({
                            "f1_fixed_threshold": f1_at_threshold(np.asarray(y), np.asarray(s), fixed_abs_z),
                            "threshold_train_f1": tau,
                            "threshold_fixed": fixed_abs_z,
                            "scale": scale.name, "ablation": ablation, "gt": gt,
                            "variant": variant, "split": split,
                        })
                        key = f"{scale.name}|{ablation}|{gt}|{variant}|{split}"
                        metrics[key] = result
                        metric_rows.append({
                            "scale": scale.name, "ablation": ablation, "gt": gt,
                            "variant": variant, "split": split,
                            "auroc": _fmt(result["auroc"]), "auprc": _fmt(result["auprc"]),
                            "f1": _fmt(result["f1"]), "f1_fixed": _fmt(result["f1_fixed_threshold"]),
                            "threshold": _fmt(tau), "n_windows": result["n_windows"],
                            "n_positive": result["n_positive"],
                        })

        # ---- boundary shortcut audit (ALL ablation, per variant/split) ----
        for ablation in ("ALL",):
            for variant in VARIANTS:
                for split in SPLITS:
                    y, s, zones = _collect_with_zones(record_gt, record_scores, records, split, ablation, variant)
                    zone_audit[f"{scale.name}|{ablation}|{variant}|{split}"] = zone_statistics(np.asarray(s), np.asarray(zones))

        # ---- paired per-case analysis ----
        scale_paired_rows: list[dict[str, Any]] = []
        case_ids = sorted({
            records[rid]["paired_case_id"] for rid in records if records[rid]["variant"] in VARIANTS
        })
        for case_id in case_ids:
            rid_a0 = _record_for_case(records, case_id, "a0")
            rid_a1 = _record_for_case(records, case_id, "a1")
            if rid_a0 is None or rid_a1 is None:
                continue
            split = records[rid_a0]["split"]
            gt_rows_a0, gt_rows_a1 = record_gt[rid_a0], record_gt[rid_a1]
            core_mask = np.array([row["is_core_window"] for row in gt_rows_a0], dtype=bool)
            boundary_mask = np.array([row["zone"] == "boundary" for row in gt_rows_a0], dtype=bool)
            target_mask = np.array([row["is_attack_window"] for row in gt_rows_a0], dtype=bool)
            s_a0 = record_scores[rid_a0]["combined_ALL"]
            s_a1 = record_scores[rid_a1]["combined_ALL"]
            labels = np.array([row["is_attack_window"] for row in gt_rows_a0], dtype=bool)
            row_out = {
                "scale": scale.name,
                "paired_case_id": case_id,
                "split": split,
                "auroc_a0_full": _fmt(evaluate_windows(labels, s_a0, np.nan)["auroc"]),
                "auroc_a1_full": _fmt(evaluate_windows(labels, s_a1, np.nan)["auroc"]),
                "delta_auroc_a1_minus_a0": _fmt(_diff(evaluate_windows(labels, s_a1, np.nan)["auroc"], evaluate_windows(labels, s_a0, np.nan)["auroc"])),
                "mean_anom_target_a0": _fmt(_nanmean(np.where(target_mask, s_a0, np.nan))),
                "mean_anom_target_a1": _fmt(_nanmean(np.where(target_mask, s_a1, np.nan))),
                "delta_target_a1_minus_a0": _fmt(_diff(_nanmean(np.where(target_mask, s_a1, np.nan)), _nanmean(np.where(target_mask, s_a0, np.nan)))),
                "mean_anom_boundary_a0": _fmt(_nanmean(np.where(boundary_mask, s_a0, np.nan))),
                "mean_anom_boundary_a1": _fmt(_nanmean(np.where(boundary_mask, s_a1, np.nan))),
                "delta_boundary_a1_minus_a0": _fmt(_diff(_nanmean(np.where(boundary_mask, s_a1, np.nan)), _nanmean(np.where(boundary_mask, s_a0, np.nan)))),
                "mean_anom_core_a0": _fmt(_nanmean(np.where(core_mask, s_a0, np.nan))),
                "mean_anom_core_a1": _fmt(_nanmean(np.where(core_mask, s_a1, np.nan))),
                "delta_core_a1_minus_a0": _fmt(_diff(_nanmean(np.where(core_mask, s_a1, np.nan)), _nanmean(np.where(core_mask, s_a0, np.nan)))),
            }
            scale_paired_rows.append(row_out)

        per_scale_context[scale.name] = {
            "record_windows": record_windows,
            "record_gt": record_gt,
            "record_scores": record_scores,
            "thresholds": thresholds,
            "reference_rows": reference_rows,
            "paired_rows": scale_paired_rows,
            "scale": scale,
        }

    # ---- write outputs ----
    _write_csv(results_dir / "aggregated_features.csv", all_feature_rows)
    _write_csv(results_dir / "anomaly_scores.csv", all_score_rows)
    _write_csv(results_dir / "metrics_by_split.csv", metric_rows)
    _write_csv(results_dir / "ablations.csv", _ablation_rows(metrics))
    _write_csv(results_dir / "metrics_by_scale.csv", _scale_rows(metrics, scale_names))
    _write_csv(results_dir / "metrics_by_attack.csv", _attack_rows(metrics, scale_names))
    _write_csv(
        results_dir / "paired_analysis.csv",
        [row for context in per_scale_context.values() for row in context["paired_rows"]],
    )

    (results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (results_dir / "boundary_shortcut_audit.json").write_text(
        json.dumps(zone_audit, indent=2), encoding="utf-8",
    )
    for scale_name, context in per_scale_context.items():
        (reference_dir / f"reference_{scale_name}.csv").is_file()  # keep name stable
        _write_csv(reference_dir / f"reference_{scale_name}.csv", context["reference_rows"])

    failure_rows = collect_failure_cases(
        records,
        {scale: context["paired_rows"] for scale, context in per_scale_context.items()},
        metrics, config,
        anomaly_scores_path=results_dir / "anomaly_scores.csv",
    )
    _write_csv(results_dir / "failure_cases.csv", failure_rows)

    figure_paths = render_day6a_figures(records, per_scale_context, metrics, config, figures_dir)

    day5_unchanged = verify_day5_outputs_unchanged(repo_root)
    run_summary = {
        "pipeline": "day6a_nontrained_localization_baseline",
        "scales": scale_names,
        "total_windows": len(all_score_rows),
        "total_window_feature_rows": len(all_feature_rows),
        "reference_source": "TRAIN_CLEAN_ONLY",
        "records_scored": len(records),
        "ablations": list(ablations),
        "thresholds_never_use_val_test": True,
        "precheck_all_passed": precheck["all_passed"],
        "day5_outputs_unchanged": day5_unchanged,
        "figures": [str(p) for p in figure_paths],
        "research_integrity": {
            "non_trained_baseline": True,
            "anomaly_score_is_not_a_learned_detector": True,
            "a0_a1_reported_separately": True,
            "full_and_core_gt_evaluated": True,
            "no_threshold_tuned_on_test": True,
        },
    }
    (results_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    return run_summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _collect(
    record_gt: Mapping[str, list[dict[str, Any]]],
    record_scores: Mapping[str, Mapping[str, np.ndarray]],
    records: Mapping[str, Mapping[str, Any]],
    split: str,
    ablation: str,
    gt: str,
    *,
    variant: str | None = None,
    label_col: str = "is_attack_window",
) -> tuple[list[bool], list[float]]:
    y: list[bool] = []
    s: list[float] = []
    for rid, rows in record_gt.items():
        rec = records[rid]
        if rec["split"] != split or rec["variant"] not in VARIANTS:
            continue
        if variant is not None and rec["variant"] != variant:
            continue
        scores = record_scores[rid][f"combined_{ablation}"]
        for i, row in enumerate(rows):
            y.append(bool(row[label_col]))
            value = float(scores[i])
            s.append(value if np.isfinite(value) else np.nan)
    return y, s


def _collect_with_zones(
    record_gt: Mapping[str, list[dict[str, Any]]],
    record_scores: Mapping[str, Mapping[str, np.ndarray]],
    records: Mapping[str, Mapping[str, Any]],
    split: str,
    ablation: str,
    variant: str,
) -> tuple[list[bool], list[float], list[str]]:
    y, s = _collect(record_gt, record_scores, records, split, ablation, "full", variant=variant)
    zones: list[str] = []
    for rid, rows in record_gt.items():
        rec = records[rid]
        if rec["split"] != split or rec["variant"] != variant:
            continue
        zones.extend(str(row["zone"]) for row in rows)
    return y, s, zones


def _record_for_case(records: Mapping[str, Mapping[str, Any]], case_id: str, variant: str) -> str | None:
    for rid, rec in records.items():
        if rec["variant"] == variant and rec["paired_case_id"] == case_id:
            return rid
    return None


def _diff(a: float, b: float) -> float:
    if np.isfinite(a) and np.isfinite(b):
        return a - b
    return float("nan")


def _nanmean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else float("nan")


def _fmt(value: Any) -> str:
    return f"{float(value):.6f}" if value is not None and np.isfinite(float(value)) else "nan"


def _ablation_rows(metrics: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for key, result in metrics.items():
        scale, ablation, gt, variant, split = key.split("|")
        if split != "test":
            continue
        row = rows.setdefault((scale, ablation), {"scale": scale, "ablation": ablation})
        row[f"{gt}_{variant}_auroc"] = _fmt(result["auroc"])
        row[f"{gt}_{variant}_auprc"] = _fmt(result["auprc"])
        row[f"{gt}_{variant}_f1"] = _fmt(result["f1"])
    return [rows[key] for key in sorted(rows)]


def _scale_rows(metrics: Mapping[str, Mapping[str, Any]], scale_names: list[str]) -> list[dict[str, Any]]:
    rows = []
    for scale in scale_names:
        row: dict[str, Any] = {"scale": scale}
        for split in SPLITS:
            for gt in GT_NAMES:
                for variant in VARIANTS:
                    result = metrics[f"{scale}|ALL|{gt}|{variant}|{split}"]
                    row[f"{split}_{variant}_{gt}_auroc"] = _fmt(result["auroc"])
                    row[f"{split}_{variant}_{gt}_auprc"] = _fmt(result["auprc"])
                    row[f"{split}_{variant}_{gt}_f1"] = _fmt(result["f1"])
        rows.append(row)
    return rows


def _attack_rows(metrics: Mapping[str, Mapping[str, Any]], scale_names: list[str]) -> list[dict[str, Any]]:
    rows = []
    for scale in scale_names:
        for variant in VARIANTS:
            row: dict[str, Any] = {"scale": scale, "variant": variant}
            for split in SPLITS:
                for gt in GT_NAMES:
                    result = metrics[f"{scale}|ALL|{gt}|{variant}|{split}"]
                    row[f"{split}_{gt}_auroc"] = _fmt(result["auroc"])
                    row[f"{split}_{gt}_auprc"] = _fmt(result["auprc"])
                    row[f"{split}_{gt}_f1"] = _fmt(result["f1"])
            rows.append(row)
    return rows


def collect_failure_cases(
    records: Mapping[str, Mapping[str, Any]],
    paired_rows_by_scale: Mapping[str, list[dict[str, Any]]],
    metrics: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
    anomaly_scores_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Deterministic failure-case collection; nothing is ever deleted.

    Clean false positives are read from the already-written
    ``anomaly_scores.csv`` so the collector works identically inside the
    pipeline and from saved results alone.
    """
    failures: list[dict[str, Any]] = []

    clean_scores_by_scale: dict[str, list[tuple[float, str, int, str]]] = defaultdict(list)
    if anomaly_scores_path is not None and anomaly_scores_path.exists():
        with anomaly_scores_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["variant"] != "clean":
                    continue
                value = float(row["combined_ALL"])
                if np.isfinite(value):
                    clean_scores_by_scale[row["scale"]].append(
                        (value, row["record_id"], int(row["window_index"]), row["split"])
                    )

    for scale_name, paired in paired_rows_by_scale.items():
        # 1) clean windows with the highest combined anomaly (false positives)
        for value, rid, win, split in sorted(clean_scores_by_scale.get(scale_name, []), reverse=True)[:3]:
            failures.append({
                "scale": scale_name, "failure_type": "clean_high_anomaly",
                "record_id": rid, "window_index": win, "split": split,
                "variant": "clean", "combined_anomaly": _fmt(value),
                "detail": "top clean false-positive window",
            })

        # 2) attack core low-score: weakest case AUROC per variant (all splits)
        for variant in VARIANTS:
            ranked = sorted(
                paired,
                key=lambda r: float(r[f"auroc_{variant}_full"]) if np.isfinite(float(r[f"auroc_{variant}_full"])) else 2.0,
            )
            for r in ranked[:2]:
                failures.append({
                    "scale": scale_name, "failure_type": f"{variant}_lowest_case_auroc",
                    "record_id": "", "window_index": -1, "split": r["split"],
                    "variant": variant, "combined_anomaly": "",
                    "detail": f"paired_case={r['paired_case_id']} auroc_full={r[f'auroc_{variant}_full']}",
                })
        # 3) boundary-only detection: largest |boundary - core| asymmetry
        ranked_boundary = sorted(paired, key=_safe_delta_boundary, reverse=True)
        for r in ranked_boundary[:2]:
            failures.append({
                "scale": scale_name, "failure_type": "boundary_only_detection",
                "record_id": "", "window_index": -1, "split": r["split"],
                "variant": "a0+a1", "combined_anomaly": "",
                "detail": f"paired_case={r['paired_case_id']} boundary-core delta a0={r['delta_boundary_a1_minus_a0']}",
            })
        # 4) A0 success / A1 failure
        ranked_pair = sorted(
            (r for r in paired if np.isfinite(float(r["delta_auroc_a1_minus_a0"]))),
            key=lambda r: float(r["delta_auroc_a1_minus_a0"]),
        )
        for r in ranked_pair[:2]:
            failures.append({
                "scale": scale_name, "failure_type": "a0_success_a1_failure",
                "record_id": "", "window_index": -1, "split": r["split"],
                "variant": "a0>a1", "combined_anomaly": "",
                "detail": f"paired_case={r['paired_case_id']} delta_auroc_a1_minus_a0={r['delta_auroc_a1_minus_a0']}",
            })
    return failures


def _safe_delta_boundary(row: Mapping[str, Any]) -> float:
    try:
        return abs(float(row["delta_boundary_a1_minus_a0"]))
    except (TypeError, ValueError):
        return 0.0


def render_day6a_figures(
    records: Mapping[str, Mapping[str, Any]],
    per_scale_context: Mapping[str, Mapping[str, Any]],
    metrics: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
    figures_dir: Path,
) -> list[Path]:
    """Deterministic sanity figures; selection rule is frozen in config."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure_seed = int(config["figure"]["seed"])
    scale_name = "250ms"
    context = per_scale_context[scale_name]
    record_gt = context["record_gt"]
    record_scores = context["record_scores"]

    paired_rows = []
    for case_id in sorted({rec["paired_case_id"] for rec in records.values() if rec["variant"] in VARIANTS}):
        rid_a0 = _record_for_case(records, case_id, "a0")
        rid_a1 = _record_for_case(records, case_id, "a1")
        if rid_a0 is None or rid_a1 is None or records[rid_a0]["split"] != "test":
            continue
        labels = np.array([row["is_attack_window"] for row in record_gt[rid_a0]], dtype=bool)
        s_a0, s_a1 = record_scores[rid_a0]["combined_ALL"], record_scores[rid_a1]["combined_ALL"]
        core_mask = np.array([row["is_core_window"] for row in record_gt[rid_a0]], dtype=bool)
        delta_core = float(np.nanmean(s_a1[core_mask]) - np.nanmean(s_a0[core_mask]))
        from audiobookbench.evaluation.day6a_localization import auroc
        paired_rows.append({
            "case_id": case_id, "rid_a0": rid_a0, "rid_a1": rid_a1,
            "delta_core": delta_core,
            "a0_auroc": auroc(labels, s_a0),
        })
    if not paired_rows:
        return []

    deltas = sorted(paired_rows, key=lambda r: r["delta_core"])
    chosen: dict[str, dict[str, Any]] = {}
    # Deterministic selection: extremes + median + worst-A0 failures, then
    # fill up to n_cases in delta order. Never more/less than config asks.
    if deltas:
        chosen[deltas[0]["case_id"]] = deltas[0]                    # A1 suppressed most
        chosen[deltas[-1]["case_id"]] = deltas[-1]                  # A1 NOT suppressed
        chosen[deltas[len(deltas) // 2]["case_id"]] = deltas[len(deltas) // 2]
    by_a0 = sorted((r for r in paired_rows if np.isfinite(r["a0_auroc"])), key=lambda r: r["a0_auroc"])
    for r in by_a0:                                                 # worst A0 localization (failures)
        if len(chosen) >= int(config["figure"]["n_cases"]):
            break
        chosen.setdefault(r["case_id"], r)
    for r in deltas:                                                # deterministic fill-up
        if len(chosen) >= int(config["figure"]["n_cases"]):
            break
        chosen.setdefault(r["case_id"], r)

    paths: list[Path] = []
    for case_id in sorted(chosen):
        info = chosen[case_id]
        paths.append(_render_case_figure(
            records, context, case_id, info, figures_dir / f"day6a_localization_{case_id}.png",
        ))
    return paths


def _render_case_figure(
    records: Mapping[str, Mapping[str, Any]],
    context: Mapping[str, Any],
    case_id: str,
    info: Mapping[str, Any],
    out_path: Path,
) -> Path:
    import matplotlib.pyplot as plt

    rid_a0, rid_a1 = str(info["rid_a0"]), str(info["rid_a1"])
    rid_clean = rid_a0.replace("_a0_manipulated", "")  # clean sequence id equals manipulated id minus suffix
    gt = context["record_gt"][rid_a0]
    feat_rows = context["record_windows"][rid_a0]
    s_clean = context["record_scores"].get(rid_clean, {}).get("combined_ALL")
    s_a0 = context["record_scores"][rid_a0]["combined_ALL"]
    s_a1 = context["record_scores"][rid_a1]["combined_ALL"]
    ch_a0 = context["record_scores"][rid_a0]
    ch_a1 = context["record_scores"][rid_a1]

    times = np.array([float(row["t_center"]) for row in feat_rows])
    attack = np.array([float(row["attack_overlap_ratio"]) for row in gt])
    core = np.array([float(row["core_overlap_ratio"]) for row in gt])

    fig, axes = plt.subplots(4, 1, figsize=(14, 13), sharex=True)
    fig.suptitle(f"Day6A localization pair {case_id}", fontsize=13)

    ax = axes[0]
    if s_clean is not None:
        ax.plot(times, s_clean, label="clean", color="#2b6cb0", lw=0.9)
    ax.plot(times, s_a0, label="A0", color="#c05621", lw=0.9, alpha=0.85)
    ax.plot(times, s_a1, label="A1", color="#2f855a", lw=0.9, alpha=0.85)
    ax.set_ylabel("combined |z| (ALL)")
    ax.set_title("Combined anomaly score (B0 robust z)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    _draw_gt_band(axes[0], times, attack, core)

    ax = axes[1]
    ax.plot(times, ch_a0["channel_f0"], label="A0 f0", color="#c05621", lw=0.9)
    ax.plot(times, ch_a1["channel_f0"], label="A1 f0", color="#2f855a", lw=0.9)
    _draw_gt_band(axes[1], times, attack, core)
    ax.set_ylabel("A_f0 |z|")
    ax.set_title("Feature-specific score: F0 channel")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(times, ch_a0["channel_energy"], label="A0 energy", color="#c05621", lw=0.9)
    ax.plot(times, ch_a1["channel_energy"], label="A1 energy", color="#2f855a", lw=0.9)
    _draw_gt_band(axes[2], times, attack, core)
    ax.set_ylabel("A_energy |z|")
    ax.set_title("Feature-specific score: energy channel")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[3]
    ax.fill_between(times, 0, attack, step="mid", color="#805ad5", alpha=0.35, label="GT full (attack/blend)")
    ax.fill_between(times, 0, core, step="mid", color="#e53e3e", alpha=0.35, label="GT strict core")
    ax.set_ylabel("GT overlap")
    ax.set_xlabel("time (s)")
    ax.set_title("Ground truth projection (majority rule 0.5)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def _draw_gt_band(ax: Any, times: np.ndarray, attack: np.ndarray, core: np.ndarray) -> None:
    ymax = ax.get_ylim()[1]
    ax.fill_between(times, 0, ymax, where=attack > 0, step="mid", color="#805ad5", alpha=0.15)
    ax.fill_between(times, 0, ymax, where=core > 0, step="mid", color="#e53e3e", alpha=0.15)


def verify_day5_outputs_unchanged(repo_root: Path = REPO_ROOT) -> bool:
    import hashlib

    record_path = repo_root / "results/day6a/day5_output_hashes.json"
    if not record_path.exists():
        return False
    record = json.loads(record_path.read_text(encoding="utf-8"))
    for relpath, expected in record["hashes"].items():
        path = repo_root / relpath
        if not path.exists():
            return False
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        if digest != expected:
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

    parser = argparse.ArgumentParser(description="Run the Day 6A non-trained localization baseline.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    summary = run_day6a(Path(args.repo_root))
    print(json.dumps(summary, indent=2))
    return 0 if summary["precheck_all_passed"] and summary["day5_outputs_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
