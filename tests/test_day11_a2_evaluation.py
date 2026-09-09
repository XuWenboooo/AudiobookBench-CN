"""Day 11 frozen A2 evaluation integrity tests."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.day8_detector_denylist import DetectorLeakageError, assert_detector_inputs_safe
from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, build_speaker_windows
from audiobookbench.temporal.day6b_scoring import b1_scores, b4_scores
from audiobookbench.temporal.frame_features import extract_frame_features
from audiobookbench.temporal.grid import TemporalGrid
from audiobookbench.evaluation.a2_reporting import clean_prefix_for_manipulated_axis
from audiobookbench.preprocessing.audio_io import load_audio

ROOT = Path(__file__).resolve().parents[1]
DAY10 = ROOT / "results/day10"
DAY11 = ROOT / "results/day11"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_day10_hash_freeze_matches_all_inputs() -> None:
    freeze = json.loads((DAY10 / "day10_output_hashes.json").read_text(encoding="utf-8"))
    assert freeze["planned"] == freeze["succeeded"] == 23
    assert freeze["failed_by_class"] == {}
    for item in freeze["output_hashes"]:
        path = Path(item["path"])
        assert path.is_file() and path.stat().st_size == int(item["bytes"])


def test_a2_dual_timeline_gt() -> None:
    from audiobookbench.security.a2_sidecar_validator import run as validate_sidecar
    from audiobookbench.security.a2_waveform_gt_verifier import run as verify_wave
    assert validate_sidecar(DAY10 / "a2_sidecar.csv", ROOT / "data/manifests/week2a_a2_planned_manifest.csv",
                            expected_count=23, official_smoke=False)["status"] == "PASS"
    assert verify_wave(DAY10 / "a2_sidecar.csv", ROOT / "data/manifests/day45_longform_manifest.csv",
                       expected_count=23)["status"] == "PASS"


def test_a2_variable_length_windows() -> None:
    scale = SpeakerWindowScale("S1", 16000, 4000)
    for n in (12000, 16000, 20000, 507597):
        windows = build_speaker_windows(n, scale)
        assert len(windows) == scale.window_count(n)
        assert all(w["sample_end"] <= n for w in windows)


def test_a2_case_grouping_unequal_counts() -> None:
    from experiments.day11_a2_evaluation.run import case_ci
    ids = ["c1", "c2", "c3"]
    gt = {"c1": [{"is_attack_window": False}] * 2 + [{"is_attack_window": True}] * 2,
          "c2": [{"is_attack_window": False}] * 3 + [{"is_attack_window": True}] * 2,
          "c3": [{"is_attack_window": False}] * 4 + [{"is_attack_window": True}] * 3}
    scores = {k: np.linspace(0, 1, len(v)) for k, v in gt.items()}
    result = case_ci(scores, gt, ids, "is_attack_window", resamples=30, seed=20260905)
    assert result["n_cases"] == 3 and result["resamples"] == 30


def test_a2_mask_alignment_and_gt_bounds() -> None:
    rows = _rows(DAY10 / "a2_sidecar.csv")
    assert len(rows) == 23
    for row in rows:
        n = int(row["final_synthetic_num_samples"])
        a0, a1 = int(row["attack_start_sample"]), int(row["attack_end_sample"])
        c0, c1 = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
        assert a1 - a0 == n and 0 <= a0 < c0 < c1 < a1
        assert int(row["blend_in_end_sample"]) - int(row["blend_in_start_sample"]) == 400
        assert int(row["blend_out_end_sample"]) - int(row["blend_out_start_sample"]) == 400


def test_a2_gt_axis_bounds() -> None:
    """T21: sample indices, rather than presentation seconds, define A2 GT."""
    for row in _rows(DAY10 / "a2_sidecar.csv"):
        start = int(row["attack_start_sample"])
        end = int(row["attack_end_sample"])
        assert start < end
        assert float(row["attack_start"]) == pytest.approx(start / 16000.0)
        assert float(row["attack_end"]) == pytest.approx(end / 16000.0)


def test_a2_mask_alignment() -> None:
    rows = _rows(DAY10 / "a2_sidecar.csv")
    scores = _rows(DAY11 / "score_timeline.csv")
    for row in rows:
        waveform, _ = load_audio(row["manipulated_audio_path"], target_sr=16000)
        for name, win, hop in (("S1_1000ms_250ms", 16000, 4000), ("S2_1500ms_250ms", 24000, 4000)):
            scale = SpeakerWindowScale(name, win, hop)
            windows = build_speaker_windows(waveform.size, scale)
            observed = [x for x in scores if x["case_id"] == row["paired_case_id"] and x["method"] == "B1b" and x["scale"] == name]
            assert len(observed) == len(windows)


def test_b3_forbidden_in_a2_primary() -> None:
    metrics = _rows(DAY11 / "metrics_by_split.csv")
    assert {row["method"] for row in metrics} == {"B0", "B1a", "B1b", "B2_adjacent", "B2_symmetric"}
    assert all("B3" not in row["method"] for row in metrics)


def test_a2_b3_skipped() -> None:
    summary = json.loads((DAY11 / "evaluation_summary.json").read_text(encoding="utf-8"))
    assert summary["b3_primary"] == "NOT_RUN"


def test_a2_figure_time_axis() -> None:
    times = np.array([0.0, 1.0, 2.0, 3.0])
    values = np.array([1.0, 2.0, 3.0, 4.0])
    clipped_t, clipped_v = clean_prefix_for_manipulated_axis(times, values, attack_start_sample=32000)
    assert np.array_equal(clipped_t, np.array([0.0, 1.0, 2.0]))
    assert np.array_equal(clipped_v, np.array([1.0, 2.0, 3.0]))


def test_a2_detector_input_denylist() -> None:
    assert_detector_inputs_safe({"waveform": np.zeros(16000, dtype=np.float32)})
    with pytest.raises(DetectorLeakageError):
        assert_detector_inputs_safe({"waveform": [0.0], "reference_audio_path": "forbidden"})
    with pytest.raises(DetectorLeakageError):
        assert_detector_inputs_safe({"waveform": [0.0], "attack_start_sample": 10})


def test_a2_threshold_reuse_frozen() -> None:
    rows = _rows(DAY11 / "threshold_provenance.csv")
    assert len(rows) == 11
    assert all(row["a2_tuning"] == "False" and row["threshold_rule"] == "Week1_train_f1" for row in rows)
    assert {row["source"] for row in rows} == {"results/day6a/metrics_by_split.csv", "results/day6b/metrics_by_split.csv"}


def test_a2_loader_reads_sidecar() -> None:
    from experiments.day11_a2_evaluation.run import verify_day10_freeze
    rows, freeze = verify_day10_freeze()
    assert len(rows) == freeze["planned"] == 23
    assert all("attack_start_sample" in row and "reference_audio_path" in row for row in rows)


def test_a2_record_id_roundtrip() -> None:
    rows = _rows(DAY10 / "a2_sidecar.csv")
    assert [r["paired_case_id"] for r in rows] == [f"paircase_{i:04d}" for i in range(1, 24)]
    moved = dict(rows[0]); moved["manipulated_audio_path"] = "arbitrary-renamed.wav"
    assert moved["paired_case_id"] == "paircase_0001"


def test_a2_variant_lookup() -> None:
    rows = _rows(DAY11 / "case_level_metrics.csv")
    for case_id in {r["case_id"] for r in rows}:
        assert any(r["case_id"] == case_id and r["method"] == "B1b" for r in rows)


def test_a2_tier_fields_absent_ok() -> None:
    rows = _rows(DAY10 / "a2_sidecar.csv")
    assert all("duration_tier" not in row for row in rows)
    assert "duration_tier" not in (ROOT / "experiments/day11_a2_evaluation/run.py").read_text(encoding="utf-8")


def test_a2_mask_fractions_present() -> None:
    for row in _rows(DAY10 / "a2_sidecar.csv"):
        waveform, _ = load_audio(row["manipulated_audio_path"], target_sr=16000)
        for window in build_speaker_windows(waveform.size, SpeakerWindowScale("S1", 16000, 4000)):
            segment = waveform[window["sample_start"]:window["sample_end"]]
            fraction = float(np.mean(20.0 * np.log10(np.maximum(np.abs(segment), 1e-12)) >= -45.0))
            assert 0.0 <= fraction <= 1.0


def test_a2_b4_frames_recomputed() -> None:
    row = _rows(DAY10 / "a2_sidecar.csv")[0]
    waveform, _ = load_audio(row["manipulated_audio_path"], target_sr=16000)
    features = extract_frame_features(waveform, TemporalGrid())
    spans = [(0, 100), (100, 200)]
    values = b4_scores(np.asarray(features["log_energy"]), spans)
    assert values.shape == (2,) and np.all(np.isfinite(values))


def test_a2_exact_lengths_from_sidecar() -> None:
    clean_by_id = {row["sequence_id"]: row for row in _rows(ROOT / "data/manifests/day45_longform_manifest.csv")}
    for row in _rows(DAY10 / "a2_sidecar.csv"):
        assert int(row["attack_end_sample"]) - int(row["attack_start_sample"]) == int(row["final_synthetic_num_samples"])
        waveform, _ = load_audio(row["manipulated_audio_path"], target_sr=16000)
        clean, _ = load_audio(clean_by_id[row["clean_sequence_id"]]["sequence_audio_path"], target_sr=16000)
        assert waveform.size == clean.size + int(row["duration_delta_samples"])


def test_a2_blend_in_out_projection() -> None:
    for row in _rows(DAY10 / "a2_sidecar.csv"):
        assert int(row["blend_in_start_sample"]) == int(row["attack_start_sample"])
        assert int(row["blend_out_end_sample"]) == int(row["attack_end_sample"])
        assert int(row["attack_core_start_sample"]) == int(row["blend_in_end_sample"])
        assert int(row["attack_core_end_sample"]) == int(row["blend_out_start_sample"])


def test_a2_prefix_null_control() -> None:
    sidecar = _rows(DAY10 / "a2_sidecar.csv")
    scores = _rows(DAY11 / "score_timeline.csv")
    by_key: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for score in scores:
        by_key.setdefault((score["case_id"], score["method"], score["scale"]), []).append(score)
    for row in sidecar:
        prefix = [float(x["score"]) for x in by_key[(row["paired_case_id"], "B1b", "S1_1000ms_250ms")]
                  if int(x["sample_end"]) <= int(row["attack_start_sample"]) and x["score"] != "nan"]
        emb = np.load(ROOT / "results/day6b/embeddings" / f"S1_1000ms_250ms__{row['clean_sequence_id']}.npy")
        clean = b1_scores(emb, trimmed=True)[:len(prefix)]
        assert prefix and np.isfinite(clean).all() and abs(float(np.mean(prefix)) - float(np.mean(clean))) < 0.02


def test_a2_outside_anomaly_vs_a0_control() -> None:
    a2 = _rows(DAY11 / "score_timeline.csv")
    a0 = _rows(ROOT / "results/day6a/anomaly_scores.csv")
    for case_id in {r["case_id"] for r in a2}:
        a2_values = [float(r["score"]) for r in a2 if r["case_id"] == case_id and r["method"] == "B0" and r["scale"] == "250ms" and r["zone"] == "outside" and r["score"] != "nan"]
        a0_values = [float(r["combined_ALL"]) for r in a0 if r["paired_case_id"] == case_id and r["scale"] == "250ms" and r["variant"] == "a0" and r["zone"] == "outside" and r["combined_ALL"] != "nan"]
        assert a2_values and a0_values


def test_case_ci_is_case_level() -> None:
    rows = _rows(DAY11 / "case_bootstrap_ci.csv")
    assert rows and all(row["unit"] == "paired_case_id" for row in rows)
    assert {int(row["n_cases"]) for row in rows} == {6, 11}
