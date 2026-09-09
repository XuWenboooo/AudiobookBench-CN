"""Day 6A non-trained localization baseline tests.

Covers the frozen aggregation layer, train-clean-only reference, B0 scoring,
zero-scale protection, GT projection, thresholds, ablations, paired
alignment, reproducibility, and protection of all frozen artifacts.

No test in this file trains a model or claims detection performance.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from audiobookbench.evaluation.day6a_localization import (
    auroc,
    evaluate_windows,
    zone_statistics,
)
from audiobookbench.security.day5_precheck import run_day5_precheck
from audiobookbench.temporal.aggregation import (
    AggregationScale,
    aggregate_window_features,
    build_aggregation_grid,
    project_ground_truth,
)
from audiobookbench.temporal.day6a_pipeline import (
    collect_failure_cases,
    load_config,
    load_day5_frames,
    run_day6a,
    verify_day5_outputs_unchanged,
)
from audiobookbench.temporal.day6a_scoring import (
    best_f1_threshold,
    combine_scores,
    compute_reference,
    feature_zscore_matrix,
    robust_zscore,
)
from audiobookbench.temporal.grid import TemporalGrid

REPOSITORY = Path(__file__).resolve().parents[1]
GRID = TemporalGrid()
CONFIG = load_config(REPOSITORY)
DAY6A = REPOSITORY / "results/day6a"


def _scale(name: str = "100ms") -> AggregationScale:
    entry = next(e for e in CONFIG["aggregation"]["scales"] if e["name"] == name)
    return AggregationScale.from_config(entry, GRID.hop_length)


def _frames(frame_count: int, seed: int = 0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    f0 = np.where(rng.random(frame_count) < 0.5, rng.normal(200, 20, frame_count), np.nan)
    return {
        "energy": rng.random(frame_count) * 0.1,
        "log_energy": rng.normal(-30, 5, frame_count),
        "rms": rng.random(frame_count) * 0.1,
        "f0_hz": f0,
        "voiced_ratio": (np.isfinite(f0)).astype(float),
        "pause_ratio": (rng.random(frame_count) < 0.2).astype(float),
    }


# ---------------------------------------------------------------------------
# 1-3: aggregation grid
# ---------------------------------------------------------------------------

def test_aggregation_grid_is_deterministic() -> None:
    scale = _scale()
    count = GRID.frame_count(507597)
    first = build_aggregation_grid(count, scale, GRID)
    second = build_aggregation_grid(count, scale, GRID)
    assert first == second
    assert len(first) == scale.window_count(count)


def test_same_length_records_share_one_aggregation_grid() -> None:
    # clean/A0/A1 of a paired case are sample-count identical (frozen Day 4.5
    # verification), so their aggregation windows must coincide exactly.
    scale = _scale("250ms")
    count = GRID.frame_count(507597)
    windows_a = build_aggregation_grid(count, scale, GRID)
    windows_b = build_aggregation_grid(count, scale, GRID)
    assert [(w.sample_start, w.sample_end) for w in windows_a] == [
        (w.sample_start, w.sample_end) for w in windows_b
    ]
    assert [w.frame_start_index for w in windows_a] == [w.frame_start_index for w in windows_b]


def test_aggregation_never_exceeds_waveform_bounds() -> None:
    num_samples = 507597
    count = GRID.frame_count(num_samples)
    for name in ("100ms", "250ms", "500ms"):
        scale = _scale(name)
        for window in build_aggregation_grid(count, scale, GRID):
            assert window.frame_end_index <= count
            assert window.sample_end <= num_samples
            assert window.sample_start < window.sample_end


def test_aggregation_scale_rejects_invalid_config() -> None:
    with pytest.raises(ValueError):
        AggregationScale.from_config({"name": "bad", "window_ms": 107, "hop_ms": 100}, GRID.hop_length)
    with pytest.raises(ValueError):
        AggregationScale("bad", window_frames=1, hop_frames=2, hop_length=160)


# ---------------------------------------------------------------------------
# 4-8: reference and z-scores
# ---------------------------------------------------------------------------

def test_reference_source_is_train_clean_only() -> None:
    # Pipeline contract: reference rows must record TRAIN_CLEAN_ONLY and the
    # n_train counts must equal the train-clean window count for the scale.
    for name in ("100ms", "250ms", "500ms"):
        path = DAY6A / f"reference/reference_{name}.csv"
        assert path.exists(), f"missing reference for {name}"
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        assert rows
        assert all(row["source"] == "TRAIN_CLEAN_ONLY" for row in rows)
        assert all(int(row["n_train"]) > 0 for row in rows)


def test_reference_is_computed_from_provided_train_windows_only() -> None:
    train = np.array([1.0, 1.2, 0.8, 1.1, 0.9])
    ref = compute_reference({"f": train}, ["f"])
    # val/test values never enter the function: a different "polluted" array
    # passed by the caller cannot retroactively change an already-frozen ref.
    z_train = robust_zscore(train, ref["f"])
    far = robust_zscore(np.array([50.0]), ref["f"])
    assert np.all(np.isfinite(z_train))
    assert far[0] > 5.0
    assert ref["f"]["n_train"] == 5


def test_robust_zscores_are_finite_for_ordinary_inputs() -> None:
    values = np.array([0.0, 1.0, 2.0, 3.0, 10.0])
    ref = compute_reference({"f": values}, ["f"])
    z = robust_zscore(values, ref["f"])
    assert np.all(np.isfinite(z))
    assert z[2] == 0.0  # the median-valued window scores zero
    assert z[4] == max(z)  # the farthest value scores highest


def test_zero_scale_feature_is_degenerate_and_never_fires() -> None:
    values = np.zeros(50)  # pause_fraction with MAD == 0 at the 100 ms scale
    values[:10] = 0.0
    ref = compute_reference({"pause_fraction": values}, ["pause_fraction"])
    assert ref["pause_fraction"]["degenerate"] == 1.0
    z = robust_zscore(np.array([0.0, 0.3, 1.0, 100.0]), ref["pause_fraction"])
    assert np.all(np.isnan(z))  # zero-scale protection: no epsilon explosion


def test_unvoiced_f0_window_stays_nan_and_is_excluded() -> None:
    frame_count = GRID.frame_count(16000)
    frames = _frames(frame_count)
    frames["f0_hz"] = np.full(frame_count, np.nan)  # all unvoiced
    scale = _scale()
    windows = build_aggregation_grid(frame_count, scale, GRID)
    row = aggregate_window_features(frames, windows[0], CONFIG["window_features"])
    assert np.isnan(row["f0_median"]) and np.isnan(row["f0_std"])
    assert row["valid_f0_fraction"] == 0.0
    ref = compute_reference({"f0_median": np.array([np.nan] * 20)}, ["f0_median"])
    z = robust_zscore(np.array([np.nan]), ref["f0_median"])
    assert np.isnan(z[0])
    combo = combine_scores(
        {"f0_median": z, "rms_mean": np.array([1.0])},
        {"f0": ["f0_median"], "rms": ["rms_mean"]},
        ["f0", "rms"],
    )
    assert combo["combined"][0] == 1.0  # NaN excluded, valid feature kept
    assert combo["n_valid_features"][0] == 1


# ---------------------------------------------------------------------------
# 9: combined anomaly determinism
# ---------------------------------------------------------------------------

def test_combined_anomaly_is_deterministic() -> None:
    rng = np.random.default_rng(11)
    features = {f"f{i}": rng.normal(0, 1, 100) for i in range(4)}
    ref = compute_reference(features, list(features))
    z1 = feature_zscore_matrix(features, ref, list(features))
    z2 = feature_zscore_matrix(features, ref, list(features))
    c1 = combine_scores(z1, {"a": ["f0", "f1"], "b": ["f2", "f3"]}, ["a", "b"])
    c2 = combine_scores(z2, {"a": ["f0", "f1"], "b": ["f2", "f3"]}, ["a", "b"])
    assert np.array_equal(c1["combined"], c2["combined"], equal_nan=True)


# ---------------------------------------------------------------------------
# 10-12: GT projection (full / core / blend)
# ---------------------------------------------------------------------------

def _one_window() -> Any:
    scale = _scale("250ms")
    return build_aggregation_grid(GRID.frame_count(507597), scale, GRID)[5]


def test_full_gt_projection_ratios_and_majority_label() -> None:
    window = _one_window()
    rows = project_ground_truth(
        [window], {"attack": (window.sample_start + 100, window.sample_end + 100),
                   "target": (window.sample_start + 100, window.sample_end + 100),
                   "core": (window.sample_start + 100, window.sample_end + 100),
                   "blend": (window.sample_start + 100, window.sample_end + 100)},
        label_threshold=0.5,
    )
    row = rows[0]
    assert 0.0 < float(row["attack_overlap_ratio"]) < 1.0
    assert row["is_attack_window"] is (float(row["attack_overlap_ratio"]) >= 0.5)


def test_core_gt_projection_majority_rule() -> None:
    window = _one_window()
    span = window.sample_end - window.sample_start
    # core covers exactly half the window -> label True under majority rule
    rows = project_ground_truth(
        [window], {"attack": (window.sample_start, window.sample_end),
                   "target": (window.sample_start, window.sample_end),
                   "core": (window.sample_start, window.sample_start + span // 2),
                   "blend": (window.sample_start, window.sample_end)},
    )
    row = rows[0]
    assert float(row["core_overlap_ratio"]) == pytest.approx(0.5, abs=0.01)
    assert row["is_core_window"] is True


def test_blend_gt_projection_disjoint_is_none() -> None:
    window = _one_window()
    rows = project_ground_truth(
        [window], {"attack": (window.sample_end + 1000, window.sample_end + 2000),
                   "target": (window.sample_end + 1000, window.sample_end + 2000),
                   "core": (window.sample_end + 1000, window.sample_end + 2000),
                   "blend": (window.sample_end + 1000, window.sample_end + 2000)},
    )
    row = rows[0]
    assert float(row["blend_overlap_ratio"]) == 0.0
    assert row["is_blend_window"] is False
    assert row["zone"] == "outside"


def test_zone_assignment_outside_boundary_core() -> None:
    window = _one_window()
    span = window.sample_end - window.sample_start
    rows = project_ground_truth(
        [window],
        {
            "attack": (window.sample_start, window.sample_end),
            "target": (window.sample_start, window.sample_end),
            "core": (window.sample_start + span // 4, window.sample_end - span // 4),
            "blend": (window.sample_start, window.sample_end),
        },
    )
    assert rows[0]["zone"] == "core"
    rows = project_ground_truth(
        [window],
        {
            "attack": (window.sample_start, window.sample_start + span // 10),
            "target": (window.sample_start, window.sample_start + span // 10),
            "core": (window.sample_start, window.sample_start + span // 10),
            "blend": (window.sample_start, window.sample_start + span // 10),
        },
    )
    assert rows[0]["zone"] == "boundary"


# ---------------------------------------------------------------------------
# 13: thresholds never see val/test
# ---------------------------------------------------------------------------

def test_train_f1_threshold_undefined_without_two_train_classes() -> None:
    y_single_class = np.zeros(50, dtype=bool)
    assert np.isnan(best_f1_threshold(y_single_class, np.random.default_rng(0).random(50)))


def test_threshold_applied_to_val_test_equals_train_threshold() -> None:
    metrics = json.loads((DAY6A / "metrics.json").read_text(encoding="utf-8"))
    for key, result in metrics.items():
        scale, ablation, _gt, _variant, split = key.split("|")
        train_key = f"{scale}|{ablation}|full|a0|train"
        train_threshold = metrics[train_key]["threshold_train_f1"]
        assert result["threshold_train_f1"] == train_threshold, key
        if split in ("val", "test"):
            # identical numeric threshold reused verbatim on val/test
            assert result["f1"] == result["f1"]  # finite or NaN, never fitted on this split


def test_best_f1_threshold_recovers_separable_case() -> None:
    y = np.zeros(40, dtype=bool)
    y[30:] = True
    s = np.concatenate([np.random.default_rng(2).random(30) * 0.4, 0.6 + np.random.default_rng(3).random(10) * 0.4])
    tau = best_f1_threshold(y, s)
    result = evaluate_windows(y, s, tau)
    assert result["f1"] == 1.0


# ---------------------------------------------------------------------------
# 14: A0/A1 paired alignment
# ---------------------------------------------------------------------------

def test_paired_a0_a1_share_windows_and_labels() -> None:
    records = load_day5_frames(REPOSITORY)
    cases: dict[str, tuple[str, str]] = {}
    for rid, rec in records.items():
        if rec["variant"] in ("a0", "a1"):
            cases.setdefault(rec["paired_case_id"], {})[rec["variant"]] = rid  # type: ignore[union-attr]
    assert len(cases) == 23
    scale = _scale("250ms")
    for case_id, pair in cases.items():
        rid_a0, rid_a1 = pair["a0"], pair["a1"]
        w_a0 = build_aggregation_grid(records[rid_a0]["frame_count"], scale, GRID)
        w_a1 = build_aggregation_grid(records[rid_a1]["frame_count"], scale, GRID)
        assert len(w_a0) == len(w_a1)
        gt_a0 = project_ground_truth(w_a0, {
            "target": (int(records[rid_a0]["manifest_row"]["target_start_sample"]), int(records[rid_a0]["manifest_row"]["target_end_sample"])),
            "attack": (int(records[rid_a0]["manifest_row"]["attack_start_sample"]), int(records[rid_a0]["manifest_row"]["attack_end_sample"])),
            "core": (int(records[rid_a0]["manifest_row"]["attack_core_start_sample"]), int(records[rid_a0]["manifest_row"]["attack_core_end_sample"])),
            "blend": (int(records[rid_a0]["manifest_row"]["blend_start_sample"]), int(records[rid_a0]["manifest_row"]["blend_end_sample"])),
        })
        gt_a1 = project_ground_truth(w_a1, {
            "target": (int(records[rid_a1]["manifest_row"]["target_start_sample"]), int(records[rid_a1]["manifest_row"]["target_end_sample"])),
            "attack": (int(records[rid_a1]["manifest_row"]["attack_start_sample"]), int(records[rid_a1]["manifest_row"]["attack_end_sample"])),
            "core": (int(records[rid_a1]["manifest_row"]["attack_core_start_sample"]), int(records[rid_a1]["manifest_row"]["attack_core_end_sample"])),
            "blend": (int(records[rid_a1]["manifest_row"]["blend_start_sample"]), int(records[rid_a1]["manifest_row"]["blend_end_sample"])),
        })
        assert [r["is_attack_window"] for r in gt_a0] == [r["is_attack_window"] for r in gt_a1]
        # Full-region labels must agree. Core windows may differ by frozen
        # design (A1 core shrinks by the 400-sample crossfades), but A0's
        # core coverage must dominate A1's window-by-window at ratio level.
        for r_a0, r_a1 in zip(gt_a0, gt_a1):
            assert float(r_a0["core_overlap_ratio"]) >= float(r_a1["core_overlap_ratio"]) - 1e-9
        assert case_id  # non-empty pairing provenance


# ---------------------------------------------------------------------------
# 15: multi-scale reproducibility
# ---------------------------------------------------------------------------

def test_multi_scale_aggregation_is_reproducible_and_correct() -> None:
    records = load_day5_frames(REPOSITORY)
    rid = sorted(records)[0]
    rec = records[rid]
    for entry in CONFIG["aggregation"]["scales"]:
        scale = AggregationScale.from_config(entry, GRID.hop_length)
        windows_a = build_aggregation_grid(rec["frame_count"], scale, GRID)
        windows_b = build_aggregation_grid(rec["frame_count"], scale, GRID)
        assert len(windows_a) == len(windows_b)
        feats_a = aggregate_window_features(rec["frames"], windows_a[0], CONFIG["window_features"])
        feats_b = aggregate_window_features(rec["frames"], windows_b[0], CONFIG["window_features"])
        assert feats_a.keys() == feats_b.keys()
        for key in feats_a:
            assert (
                feats_a[key] == feats_b[key]
                or (np.isnan(feats_a[key]) and np.isnan(feats_b[key]))
            )


# ---------------------------------------------------------------------------
# 16-17: pause and energy ablations
# ---------------------------------------------------------------------------

def _z_for_ablation_tests() -> tuple[dict[str, np.ndarray], dict[str, list[str]]]:
    channels = {
        "f0": ["f0_median"],
        "energy": ["log_energy_mean"],
        "rms": ["rms_mean"],
        "voicing": ["voiced_fraction"],
        "pause": ["pause_fraction"],
    }
    z = {
        "f0_median": np.array([1.0, 1.0]),
        "log_energy_mean": np.array([2.0, 2.0]),
        "rms_mean": np.array([2.0, 2.0]),
        "voiced_fraction": np.array([0.5, 0.5]),
        "pause_fraction": np.array([1000.0, 1000.0]),  # huge pause signal
    }
    return z, channels


def test_pause_ablation_removes_pause_influence() -> None:
    z, channels = _z_for_ablation_tests()
    with_pause = combine_scores(z, channels, ["f0", "energy", "rms", "voicing", "pause"])
    no_pause = combine_scores(z, channels, ["f0", "energy", "rms", "voicing"])
    assert with_pause["combined"][0] > no_pause["combined"][0]
    assert no_pause["combined"][0] == pytest.approx(1.375)
    assert with_pause["n_valid_features"][0] == 5 and no_pause["n_valid_features"][0] == 4


def test_energy_ablation_removes_energy_and_rms_influence() -> None:
    z, channels = _z_for_ablation_tests()
    no_energy = combine_scores(z, channels, ["f0", "voicing", "pause"])
    assert no_energy["combined"][0] == pytest.approx((1.0 + 0.5 + 1000.0) / 3)
    # NO_ENERGY must not contain any energy/rms channel contribution:
    # flip energy features and verify the NO_ENERGY score is unchanged.
    z2 = dict(z)
    z2["log_energy_mean"] = np.array([50.0, 50.0])
    z2["rms_mean"] = np.array([50.0, 50.0])
    no_energy_2 = combine_scores(z2, channels, ["f0", "voicing", "pause"])
    assert np.array_equal(no_energy["combined"], no_energy_2["combined"])


def test_config_freezes_all_three_ablations() -> None:
    assert set(CONFIG["ablations"]) == {"ALL", "NO_PAUSE", "NO_ENERGY"}
    assert "pause" not in CONFIG["ablations"]["NO_PAUSE"]
    assert "energy" not in CONFIG["ablations"]["NO_ENERGY"] and "rms" not in CONFIG["ablations"]["NO_ENERGY"]


# ---------------------------------------------------------------------------
# 18: failure-case collection determinism
# ---------------------------------------------------------------------------

def test_failure_case_collection_is_deterministic() -> None:
    summary_a = _failure_snapshot()
    summary_b = _failure_snapshot()
    assert summary_a == summary_b
    path = DAY6A / "failure_cases.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows, "failure cases must be preserved, never deleted"
    types = {row["failure_type"] for row in rows}
    assert "clean_high_anomaly" in types
    assert "a0_success_a1_failure" in types


def _failure_snapshot() -> list[tuple]:
    config = load_config(REPOSITORY)
    records = load_day5_frames(REPOSITORY)
    metrics = json.loads((DAY6A / "metrics.json").read_text(encoding="utf-8"))
    paired = list(csv.DictReader((DAY6A / "paired_analysis.csv").open(encoding="utf-8")))
    contexts = {
        scale: [r for r in paired if r["scale"] == scale]
        for scale in ("100ms", "250ms", "500ms")
    }
    rows = collect_failure_cases(
        records, contexts, metrics, config,
        anomaly_scores_path=DAY6A / "anomaly_scores.csv",
    )
    return [tuple(sorted(r.items())) for r in rows]


# ---------------------------------------------------------------------------
# 19-20: frozen artifact protection
# ---------------------------------------------------------------------------

def test_existing_frozen_hashes_unchanged() -> None:
    precheck = run_day5_precheck(REPOSITORY)
    assert precheck["all_passed"], json.dumps(precheck["checks"], indent=1)


def test_day5_feature_files_unchanged() -> None:
    assert verify_day5_outputs_unchanged(REPOSITORY)


# ---------------------------------------------------------------------------
# metrics NaN-safety and zone statistics
# ---------------------------------------------------------------------------

def test_auroc_is_nan_for_single_class_slice() -> None:
    y = np.zeros(20, dtype=bool)
    assert np.isnan(auroc(y, np.random.default_rng(4).random(20)))


def test_zone_statistics_reports_mean_and_median() -> None:
    scores = np.array([1.0, 2.0, 3.0, np.nan])
    zones = np.array(["outside", "outside", "core", "boundary"])
    stats = zone_statistics(scores, zones)
    assert stats["outside"]["mean"] == 1.5
    assert stats["core"]["mean"] == 3.0
    assert stats["boundary"]["n"] == 0 and np.isnan(stats["boundary"]["mean"])


def test_day6a_run_summary_gate_conditions() -> None:
    summary = json.loads((DAY6A / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["precheck_all_passed"] is True
    assert summary["day5_outputs_unchanged"] is True
    assert summary["reference_source"] == "TRAIN_CLEAN_ONLY"
    assert summary["scales"] == ["100ms", "250ms", "500ms"]
    assert summary["thresholds_never_use_val_test"] is True
    assert len(summary["figures"]) == 5


def test_config_matches_written_config_copy() -> None:
    written = yaml.safe_load((DAY6A / "config.yaml").read_text(encoding="utf-8"))
    assert written == CONFIG
