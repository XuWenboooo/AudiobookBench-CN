"""Day 5 temporal-signal engineering tests.

Covers the unified temporal grid, frame features (energy family, F0 backends,
voicing/pause indicators), validation logic, ground-truth interval checks,
paired alignment, figure rendering, and the hash verifiers used by the
Day 5 pre-check.

No test in this file trains a model or computes any detection metric.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.security.day5_precheck import (
    _sha256,
    verify_output_audio_hashes,
)
from audiobookbench.temporal.day5_figures import plot_pair_trajectories
from audiobookbench.temporal.day5_validation import (
    interval_label,
    overlap_flags,
    validate_ground_truth_intervals,
    validate_pair_alignment,
    validate_record_frames,
)
from audiobookbench.temporal.frame_features import (
    EMBEDDING_STATUS,
    autocorrelation_f0,
    extract_frame_features,
    frame_energies,
    pause_indicator,
    sequence_summary,
    voiced_indicator,
)
from audiobookbench.temporal.grid import (
    HOP_LENGTH,
    FRAME_LENGTH,
    SAMPLE_RATE,
    TemporalGrid,
    framing_matrix,
    overlap_fraction,
)


GRID = TemporalGrid()


def _sine(duration_s: float = 1.0, freq: float = 220.0, amp: float = 0.3) -> np.ndarray:
    sr = SAMPLE_RATE
    t = np.arange(int(sr * duration_s), dtype=np.float64) / sr
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


# ---------------------------------------------------------------------------
# Temporal grid
# ---------------------------------------------------------------------------

def test_grid_frame_count_and_bounds_are_consistent() -> None:
    num_samples = 16000
    count = GRID.frame_count(num_samples)
    assert count == 1 + (num_samples - FRAME_LENGTH) // HOP_LENGTH
    start, end = GRID.frame_bounds(count - 1)
    assert end <= num_samples
    assert end - start == FRAME_LENGTH
    assert GRID.frame_bounds(0) == (0, FRAME_LENGTH)


def test_grid_frame_times_are_derived_from_samples_exactly() -> None:
    for index in (0, 1, 57, 999):
        start, end = GRID.frame_bounds(index)
        t_start, t_center, t_end = GRID.frame_times(index)
        assert t_start == start / SAMPLE_RATE
        assert t_end == end / SAMPLE_RATE
        assert t_center == ((start + end) // 2) / SAMPLE_RATE
        assert abs((t_end - t_start) - FRAME_LENGTH / SAMPLE_RATE) < 1e-12


def test_grid_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        TemporalGrid(hop_length=FRAME_LENGTH + 1)
    with pytest.raises(ValueError):
        TemporalGrid(frame_length=0)
    with pytest.raises(ValueError):
        TemporalGrid(sample_rate=-1)
    with pytest.raises(ValueError):
        GRID.frame_bounds(-1)


def test_grid_leaves_only_sub_hop_trailing_samples_uncovered() -> None:
    num_samples = 16000
    count = GRID.frame_count(num_samples)
    last_end = GRID.frame_bounds(count - 1)[1]
    assert 0 <= num_samples - last_end < HOP_LENGTH
    assert GRID.frame_count(FRAME_LENGTH - 1) == 0
    assert GRID.frame_centers(FRAME_LENGTH - 1).size == 0


def test_framing_matrix_shape_matches_grid() -> None:
    waveform = _sine(1.0)
    frames = framing_matrix(waveform, GRID)
    assert frames.shape == (GRID.frame_count(waveform.size), FRAME_LENGTH)
    assert np.array_equal(frames[5], waveform[5 * HOP_LENGTH:5 * HOP_LENGTH + FRAME_LENGTH])


# ---------------------------------------------------------------------------
# Frame features
# ---------------------------------------------------------------------------

def test_energy_rms_and_log_energy_are_mathematically_consistent() -> None:
    rng = np.random.default_rng(7)
    waveform = rng.standard_normal(SAMPLE_RATE).astype(np.float32) * 0.2
    features = frame_energies(waveform, GRID)
    count = GRID.frame_count(waveform.size)
    assert features["energy"].size == count
    np.testing.assert_allclose(features["rms"] ** 2, features["energy"], rtol=1e-9)
    np.testing.assert_allclose(
        features["log_energy"], 10.0 * np.log10(features["energy"] + 1e-12), rtol=1e-9,
    )
    frame = waveform[3 * HOP_LENGTH:3 * HOP_LENGTH + FRAME_LENGTH]
    assert math.isclose(features["energy"][3], float(np.mean(frame.astype(np.float64) ** 2)), rel_tol=1e-6)


def test_parselmouth_backend_recovers_sine_f0() -> None:
    pytest.importorskip("parselmouth")
    features = extract_frame_features(_sine(1.0, 220.0), GRID)
    assert features["f0_backend"] == "parselmouth_to_pitch_ac"
    voiced = np.asarray(features["f0_hz"])[np.asarray(features["voiced_ratio"]) > 0]
    assert voiced.size > 50
    median_f0 = float(np.nanmedian(voiced))
    assert abs(median_f0 - 220.0) <= 5.0


def test_silence_is_pause_and_never_gets_a_fake_f0() -> None:
    features = extract_frame_features(np.zeros(SAMPLE_RATE, dtype=np.float32), GRID)
    assert np.all(features["pause_ratio"] == 1.0)
    assert np.all(features["voiced_ratio"] == 0.0)
    assert np.all(~np.isfinite(features["f0_hz"]))
    summary = sequence_summary(features, GRID)
    assert summary["pause_ratio"] == 1.0
    assert math.isnan(summary["f0_mean"])  # no fake F0 for unvoiced sequences


def test_voiced_indicator_applies_range_bounds() -> None:
    indicators = voiced_indicator(np.array([np.nan, 60.0, 200.0, 520.0]))
    assert indicators.tolist() == [0.0, 0.0, 1.0, 0.0]


def test_pause_indicator_uses_fixed_threshold() -> None:
    rms = np.array([10.0 ** (-50 / 20), 10.0 ** (-40 / 20), 0.0])
    assert pause_indicator(rms).tolist() == [1.0, 0.0, 1.0]


def test_autocorrelation_fallback_recovers_sine_f0() -> None:
    sr = SAMPLE_RATE
    t = np.arange(400, dtype=np.float64) / sr
    frame = 0.5 * np.sin(2 * np.pi * 200.0 * t)
    f0 = autocorrelation_f0(frame, sr, 75.0, 500.0)
    assert abs(f0 - 200.0) <= 10.0
    assert math.isnan(autocorrelation_f0(np.zeros(400), sr, 75.0, 500.0))


def test_f0_fallback_backend_is_reported_when_parselmouth_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins

    real_import = builtins.__import__

    def broken_import(name: str, *args: object, **kwargs: object):
        if name.startswith("parselmouth"):
            raise ImportError("simulated missing parselmouth")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", broken_import)
    features = extract_frame_features(_sine(0.5, 180.0), GRID)
    assert features["f0_backend"] == "numpy_autocorrelation_fallback"
    voiced = np.asarray(features["f0_hz"])[np.asarray(features["voiced_ratio"]) > 0]
    assert voiced.size > 10
    assert abs(float(np.nanmedian(voiced)) - 180.0) <= 10.0


def test_speaker_embedding_is_blocked_and_never_fabricated() -> None:
    assert EMBEDDING_STATUS == "BLOCKED"
    features = extract_frame_features(_sine(0.2), GRID)
    assert "speaker_embedding" not in features
    assert all(key in features for key in ("energy", "log_energy", "rms", "f0_hz", "voiced_ratio", "pause_ratio"))


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def test_overlap_fraction_full_partial_and_disjoint() -> None:
    assert overlap_fraction(0, 400, 0, 400) == 1.0
    assert overlap_fraction(0, 400, 100, 300) == 0.5
    assert overlap_fraction(0, 400, 400, 800) == 0.0
    assert overlap_fraction(0, 400, -50, 50) == pytest.approx(50 / 400)
    with pytest.raises(ValueError):
        overlap_fraction(0, 400, 300, 300)


def test_interval_labels() -> None:
    assert interval_label(1.0) == "full"
    assert interval_label(0.4) == "partial"
    assert interval_label(0.0) == "none"


def test_overlap_flags_per_frame() -> None:
    flags = overlap_flags(0, 400, {"target": (0, 200), "core": (500, 600)})
    assert flags["target"] == 0.5
    assert flags["core"] == 0.0


def _synthetic_validation_case() -> tuple[np.ndarray, list[dict], dict]:
    waveform = _sine(1.0)
    rows = []
    for index in range(GRID.frame_count(waveform.size)):
        start, end = GRID.frame_bounds(index)
        t_start, t_center, t_end = GRID.frame_times(index)
        rows.append({
            "frame_index": index,
            "frame_start_sample": start,
            "frame_end_sample": end,
            "t_start": t_start,
            "t_center": t_center,
            "t_end": t_end,
        })
    features = extract_frame_features(waveform, GRID)
    return waveform, rows, features


def test_validate_record_frames_passes_on_consistent_data() -> None:
    waveform, rows, features = _synthetic_validation_case()
    result = validate_record_frames(waveform, GRID, rows, features)
    assert result["passed"], result["problems"]
    assert result["waveform_finite"] and result["features_finite"]


def test_validate_record_frames_detects_timestamp_corruption() -> None:
    waveform, rows, features = _synthetic_validation_case()
    rows[10]["t_start"] = float(rows[10]["t_start"]) + 0.5
    result = validate_record_frames(waveform, GRID, rows, features)
    assert not result["passed"]
    assert any("timestamp_mismatch" in p for p in result["problems"])


def test_validate_record_frames_detects_non_finite_feature() -> None:
    waveform, rows, features = _synthetic_validation_case()
    features["energy"] = features["energy"].copy()
    features["energy"][3] = np.nan
    result = validate_record_frames(waveform, GRID, rows, features)
    assert not result["passed"]
    assert any("non_finite_feature" in p for p in result["problems"])


# ---------------------------------------------------------------------------
# Ground truth intervals and pair alignment
# ---------------------------------------------------------------------------

def _manifest_rows() -> list[dict[str, str]]:
    repo_root = Path(__file__).resolve().parents[1]
    manifest = repo_root / "data/manifests/day45_attack_manifest.csv"
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def test_frozen_manifest_ground_truth_intervals_validate() -> None:
    rows = _manifest_rows()
    assert len(rows) == 46
    for row in rows:
        problems = validate_ground_truth_intervals(row, int(row["sequence_num_samples"]))
        assert problems == [], (row["attack_id"], problems)


def test_ground_truth_validator_rejects_corrupted_a0_core() -> None:
    row = dict(_manifest_rows()[0])
    assert row["attack_type"] == "cross_speaker_splice"
    row["attack_core_start_sample"] = str(int(row["attack_core_start_sample"]) + 1)
    problems = validate_ground_truth_intervals(row, int(row["sequence_num_samples"]))
    assert "A0_intervals_must_equal_target" in problems


def test_ground_truth_validator_enforces_a1_crossfade_core() -> None:
    rows = _manifest_rows()
    a1 = next(row for row in rows if row["attack_type"] == "artifact_controlled_cross_speaker_splice")
    corrupted = dict(a1)
    corrupted["attack_core_start_sample"] = str(int(corrupted["target_start_sample"]) + 1)
    problems = validate_ground_truth_intervals(corrupted, int(corrupted["sequence_num_samples"]))
    assert any(p.startswith("A1_core_must_shrink_by_crossfade") for p in problems)


def test_pair_alignment_detects_length_mismatch() -> None:
    rows = _manifest_rows()
    case_rows = [row for row in rows if row["paired_case_id"] == rows[0]["paired_case_id"]]
    clean_id = case_rows[0]["clean_sequence_id"]
    num_samples = int(case_rows[0]["sequence_num_samples"])
    decoded = {clean_id: (num_samples, 16000)}
    for row in case_rows:
        decoded[str(row["manipulated_sequence_id"])] = (num_samples, 16000)
    ok = validate_pair_alignment({"clean_sequence_id": clean_id}, case_rows, decoded)
    assert ok["passed"], ok["problems"]
    decoded[str(case_rows[0]["manipulated_sequence_id"])] = (num_samples - 1, 16000)
    bad = validate_pair_alignment({"clean_sequence_id": clean_id}, case_rows, decoded)
    assert not bad["passed"]
    assert any("sample_count_mismatch_vs_clean" in p for p in bad["problems"])


# ---------------------------------------------------------------------------
# Figures and pre-check helpers
# ---------------------------------------------------------------------------

def test_debug_figure_smoke(tmp_path: Path) -> None:
    waveform, rows, _ = _synthetic_validation_case()
    rows = [
        {**row, "record_id": "r", "variant": "clean", "paired_case_id": "c",
         "split": "test", "speaker": "SSB0000",
         "energy": "0.01", "log_energy": "-20.0", "rms": "0.1",
         "f0_hz": "nan", "voiced_ratio": "0.0", "pause_ratio": "1.0",
         "overlap_target": "0.0", "in_target": "none", "overlap_attack": "0.0",
         "in_attack": "none", "overlap_core": "0.0", "in_core": "none",
         "overlap_blend": "0.0", "in_blend": "none"}
        for row in rows
    ]
    out = plot_pair_trajectories(
        GRID, rows, rows, rows,
        {"target": (0.2, 0.5), "attack": (0.2, 0.5), "core": (0.2, 0.5), "blend": (0.2, 0.5)},
        "case_smoke", "test", tmp_path / "fig.png",
    )
    assert out.exists() and out.stat().st_size > 10_000


def test_sha256_verifier_detects_mismatch(tmp_path: Path) -> None:
    target = tmp_path / "audio.wav"
    target.write_bytes(b"\x00\x01\x02")
    digest = _sha256(target)
    assert len(digest) == 64 and digest == digest.upper()
    relpath = "some/audio.wav"
    (tmp_path / "some").mkdir()
    (tmp_path / relpath).write_bytes(b"\x00\x01\x02")
    rows = [{"artifact_type": "clean", "artifact_id": "x", "audio_relpath": relpath, "sha256": digest}]
    hash_csv = "hashes/output_audio_hashes.csv"
    (tmp_path / "hashes").mkdir()
    csv_path = tmp_path / hash_csv
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = verify_output_audio_hashes(tmp_path, hash_csv=hash_csv)
    assert result["passed"] and result["rows"] == 1
    rows[0]["sha256"] = "0" * 64
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = verify_output_audio_hashes(tmp_path, hash_csv=hash_csv)
    assert not result["passed"] and len(result["mismatches"]) == 1


def test_sequence_identity_parsing() -> None:
    from audiobookbench.temporal.day5_pipeline import _parse_sequence_identity

    assert _parse_sequence_identity("day45_train_SSB0005_seq000") == ("train", "SSB0005")
    assert _parse_sequence_identity("day45_val_SSB0073_seq001_paircase_0007_a1_manipulated") == ("val", "SSB0073")
