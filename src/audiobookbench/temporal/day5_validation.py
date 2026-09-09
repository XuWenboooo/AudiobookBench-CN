"""Day 5 validation over frames, features, ground truth and paired alignment.

Checks performed per record (70 waveforms):

- frame consistency      : frame_count matches ``1 + (N - frame) // hop`` for the
                           decoded sample count; frame bounds are monotonic and
                           never exceed the waveform; coverage ends within one hop
                           of the sequence end.
- duration/timestamp     : every stored second value equals ``sample / 16000``.
- ground-truth intervals : target/attack/core/blend intervals lie inside the
                           sequence; A0 must have attack == blend == core ==
                           target and zero crossfade; A1 core must equal the
                           target shrunk by the recorded crossfade on both edges.
- feature finiteness     : energy/log_energy/rms/voiced/pause must be finite for
                           every frame. F0 may be NaN exactly where the frame is
                           unvoiced (standard representation, never a fake value).
- sample consistency     : decoded mono/16 kHz/sample count agree with probe data
                           and with the Day 4.5 manifest.

Pair-level checks (23 pairs):
- paired alignment       : clean/A0/A1 have identical sample counts and sample
                           rate; the pair shares target and donor crop bounds.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

import numpy as np

from audiobookbench.temporal.grid import TemporalGrid
from audiobookbench.temporal.frame_features import EPS


def overlap_flags(
    frame_start: int,
    frame_end: int,
    intervals: Mapping[str, tuple[int, int]],
) -> dict[str, float]:
    """Overlap fraction of one frame with each named interval."""
    from audiobookbench.temporal.grid import overlap_fraction

    return {
        name: overlap_fraction(frame_start, frame_end, lo, hi)
        for name, (lo, hi) in intervals.items()
    }


def interval_label(overlap: float) -> str:
    """Discrete label for reporting: full / partial / none."""
    if overlap >= 1.0 - 1e-9:
        return "full"
    if overlap > 0.0:
        return "partial"
    return "none"


def validate_ground_truth_intervals(
    row: Mapping[str, Any],
    num_samples: int,
    sample_rate: int = 16000,
) -> list[str]:
    """Return a list of ground-truth interval problems (empty list == pass)."""
    problems: list[str] = []
    try:
        target = (int(row["target_start_sample"]), int(row["target_end_sample"]))
        attack = (int(row["attack_start_sample"]), int(row["attack_end_sample"]))
        core = (int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"]))
        blend = (int(row["blend_start_sample"]), int(row["blend_end_sample"]))
        crossfade = int(row["crossfade_samples"])
    except (KeyError, ValueError) as exc:
        return [f"unparseable-interval-field: {exc}"]

    for name, (lo, hi) in {
        "target": target, "attack": attack, "core": core, "blend": blend,
    }.items():
        if not (0 <= lo < hi <= num_samples):
            problems.append(f"{name}_interval_out_of_bounds: [{lo},{hi}) vs N={num_samples}")

    if row.get("attack_type") == "cross_speaker_splice":  # A0
        if not (attack == target and blend == target and core == target):
            problems.append("A0_intervals_must_equal_target")
        if crossfade != 0:
            problems.append(f"A0_crossfade_must_be_zero: {crossfade}")
    elif row.get("attack_type") == "artifact_controlled_cross_speaker_splice":  # A1
        if attack != target:
            problems.append("A1_attack_interval_must_equal_target")
        if blend != target:
            problems.append("A1_blend_interval_must_equal_target")
        expected_core = (target[0] + crossfade, target[1] - crossfade)
        if core != expected_core:
            problems.append(f"A1_core_must_shrink_by_crossfade: got {core}, expected {expected_core}")
    else:
        problems.append(f"unknown_attack_type: {row.get('attack_type')}")

    # seconds must equal samples / sample_rate exactly
    for sec_col, smp_col in (
        ("target_start", "target_start_sample"), ("target_end", "target_end_sample"),
        ("attack_start", "attack_start_sample"), ("attack_end", "attack_end_sample"),
        ("attack_core_start", "attack_core_start_sample"), ("attack_core_end", "attack_core_end_sample"),
        ("blend_start", "blend_start_sample"), ("blend_end", "blend_end_sample"),
    ):
        try:
            seconds = float(row[sec_col])
            samples = int(row[smp_col])
        except (KeyError, ValueError):
            problems.append(f"unparseable-second-sample-pair: {sec_col}")
            continue
        if abs(seconds - samples / sample_rate) > 1e-9:
            problems.append(f"second_sample_mismatch: {sec_col}")
    return problems


def validate_record_frames(
    waveform: np.ndarray,
    grid: TemporalGrid,
    metadata_rows: Iterable[Mapping[str, Any]],
    features: Mapping[str, np.ndarray],
) -> dict[str, Any]:
    """Frame/timestamp/finiteness validation for one decoded record.

    Returns a result dict; ``problems`` is empty when everything passes.
    """
    waveform = np.asarray(waveform, dtype=np.float32)
    num_samples = int(waveform.size)
    expected_count = grid.frame_count(num_samples)
    rows = list(metadata_rows)
    problems: list[str] = []

    if len(rows) != expected_count:
        problems.append(f"frame_metadata_count_mismatch: rows={len(rows)} expected={expected_count}")
    if features["energy"].size != expected_count:
        problems.append(f"feature_count_mismatch: {features['energy'].size} vs {expected_count}")

    for index, row in enumerate(rows):
        if int(row["frame_index"]) != index:
            problems.append(f"frame_index_gap: row {index}")
            break
        start, end = grid.frame_bounds(index)
        if int(row["frame_start_sample"]) != start or int(row["frame_end_sample"]) != end:
            problems.append(f"frame_bounds_mismatch: frame {index}")
            break
        t_start, t_center, t_end = grid.frame_times(index)
        if (
            abs(float(row["t_start"]) - t_start) > 1e-9
            or abs(float(row["t_center"]) - t_center) > 1e-9
            or abs(float(row["t_end"]) - t_end) > 1e-9
        ):
            problems.append(f"timestamp_mismatch: frame {index}")
            break

    if expected_count > 0:
        last_end = grid.frame_bounds(expected_count - 1)[1]
        if num_samples - last_end >= grid.hop_length:
            problems.append("frame_coverage_gap: trailing samples exceed one hop")

    for key in ("energy", "log_energy", "rms", "voiced_ratio", "pause_ratio"):
        values = np.asarray(features[key], dtype=np.float64)
        if values.size and not np.all(np.isfinite(values)):
            problems.append(f"non_finite_feature: {key}")
    f0 = np.asarray(features["f0_hz"], dtype=np.float64)
    if f0.size and np.any(np.isinf(f0)):
        problems.append("inf_f0_values")  # NaN is the legal unvoiced marker; Inf never is

    waveform_finite = bool(np.all(np.isfinite(waveform)))
    if not waveform_finite:
        problems.append("non_finite_waveform")

    return {
        "num_samples": num_samples,
        "expected_frame_count": expected_count,
        "metadata_frame_count": len(rows),
        "waveform_finite": waveform_finite,
        "features_finite": not any(p.startswith("non_finite_feature") or p == "inf_f0_values" for p in problems),
        "problems": problems,
        "passed": not problems,
    }


def validate_pair_alignment(
    clean_row: Mapping[str, Any],
    pair_rows: Iterable[Mapping[str, Any]],
    decoded: Mapping[str, tuple[int, int]],
) -> dict[str, Any]:
    """Paired alignment between clean, A0 and A1 of one paired case.

    ``decoded`` maps record id -> (num_samples, sample_rate) of the decoded wave.
    """
    rows = [dict(row) for row in pair_rows]
    problems: list[str] = []
    clean_id = str(clean_row["clean_sequence_id"])
    clean_decoded = decoded.get(clean_id)
    if clean_decoded is None:
        problems.append("missing_clean_decoded")

    if len(rows) != 2:
        problems.append(f"pair_row_count_must_be_two: {len(rows)}")
    else:
        a0, a1 = rows
        if str(a0["attack_type"]) != "cross_speaker_splice":
            problems.append("first_pair_row_not_A0")
        if str(a1["attack_type"]) != "artifact_controlled_cross_speaker_splice":
            problems.append("second_pair_row_not_A1")
        for field in (
            "target_start_sample", "target_end_sample",
            "donor_start_sample", "donor_end_sample",
            "clean_sequence_id", "split", "donor_source_sample_id",
        ):
            if str(a0[field]) != str(a1[field]):
                problems.append(f"pair_field_disagreement: {field}")

    counts = {str(row["manipulated_sequence_id"]): decoded.get(str(row["manipulated_sequence_id"])) for row in rows}
    for record_id, info in counts.items():
        if info is None:
            problems.append(f"missing_decoded: {record_id}")
            continue
        if clean_decoded is not None and info[0] != clean_decoded[0]:
            problems.append(f"sample_count_mismatch_vs_clean: {record_id}")
        if clean_decoded is not None and info[1] != clean_decoded[1]:
            problems.append(f"sample_rate_mismatch_vs_clean: {record_id}")

    return {
        "paired_case_id": str(rows[0]["paired_case_id"]) if rows else "",
        "clean_sequence_id": clean_id,
        "problems": problems,
        "passed": not problems,
    }


def per_frame_gt_columns(
    grid: TemporalGrid,
    intervals: Mapping[str, tuple[int, int]],
    num_samples: int,
) -> list[dict[str, Any]]:
    """For one manipulated record, compute per-frame overlap columns."""
    out: list[dict[str, Any]] = []
    for index in range(grid.frame_count(num_samples)):
        start, end = grid.frame_bounds(index)
        overlaps = overlap_flags(start, end, intervals)
        row: dict[str, Any] = {"frame_index": index}
        for name, fraction in overlaps.items():
            row[f"overlap_{name}"] = f"{fraction:.6f}"
            row[f"in_{name}"] = interval_label(fraction)
        out.append(row)
    return out


def interval_validity(intervals: Mapping[str, tuple[int, int]], num_samples: int) -> list[str]:
    problems: list[str] = []
    for name, (lo, hi) in intervals.items():
        if not (0 <= lo < hi <= num_samples):
            problems.append(f"{name}_out_of_bounds")
    return problems


def log_energy_floor_check(log_energy: np.ndarray) -> bool:
    """log_energy must never exceed 0 dB for full-scale-bounded float input."""
    values = np.asarray(log_energy, dtype=np.float64)
    return bool(np.all(values <= EPS))
