"""Day 4 deterministic localized cross-speaker splice generation.

A0/A1 are forensic pipeline baselines using real, usually different-text donor
speech. They are not voice cloning or pure speaker-identity replacement.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import math
from pathlib import Path
from typing import Any, Iterable, Mapping
import unicodedata

import numpy as np

from audiobookbench.data.prepare_audio import resolve_audio_path
from audiobookbench.preprocessing.audio_io import load_audio, probe_audio, write_audio

A0 = "cross_speaker_splice"
A1 = "artifact_controlled_cross_speaker_splice"
ATTACK_TYPES = {A0, A1}

ATTACK_COLUMNS = [
    "attack_id", "attack_type", "clean_sequence_id", "manipulated_sequence_id",
    "sequence_pair_id", "clean_audio_path", "manipulated_audio_path",
    "target_source_sample_id", "target_source_order", "target_speaker", "target_text_id",
    "donor_source_sample_id", "donor_speaker", "donor_text_id", "donor_split", "same_text",
    "attack_duration_tier", "attack_start", "attack_end", "attack_core_start",
    "attack_core_end", "blend_start", "blend_end", "attack_start_sample",
    "attack_end_sample", "attack_core_start_sample", "attack_core_end_sample",
    "blend_start_sample", "blend_end_sample", "donor_start_sample", "donor_end_sample",
    "duration_matching_method", "rms_matching", "target_rms", "donor_rms",
    "rms_gain_unclamped", "rms_gain", "rms_gain_min", "rms_gain_max",
    "crossfade_samples", "sample_rate", "split", "source_type", "is_manipulated",
    "longform_type", "sequence_duration", "sequence_num_samples", "boundary_jump_in",
    "boundary_jump_out", "boundary_rms_discontinuity", "gain_clipped_sample_count",
]

SKIP_COLUMNS = ["clean_sequence_id", "split", "target_speaker", "attack_type", "reason"]


class AttackValidationError(ValueError):
    """Raised when Day 4 attack metadata or waveform verification fails."""


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _normalize_text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value).strip())


def _rms(waveform: np.ndarray) -> float:
    array = np.asarray(waveform, dtype=np.float64)
    return float(np.sqrt(np.mean(array**2))) if array.size else 0.0


def _boundary_diagnostics(clean: np.ndarray, manipulated: np.ndarray, start: int, end: int, sr: int) -> tuple[float, float, float]:
    jump_in = abs(float(manipulated[start]) - float(clean[start - 1])) if start > 0 else 0.0
    jump_out = abs(float(clean[end]) - float(manipulated[end - 1])) if end < len(clean) else 0.0
    window = max(1, int(round(0.025 * sr)))
    before = clean[max(0, start - window):start]
    inside_left = manipulated[start:min(end, start + window)]
    inside_right = manipulated[max(start, end - window):end]
    after = clean[end:min(len(clean), end + window)]
    rms_discontinuity = abs(_rms(before) - _rms(inside_left)) + abs(_rms(inside_right) - _rms(after))
    return jump_in, jump_out, rms_discontinuity


def select_donor(
    source_records: Iterable[Mapping[str, Any]],
    *,
    target_speaker: str,
    split: str,
    required_samples: int,
    dataset_root: str | Path,
    sample_rate: int = 16000,
) -> tuple[dict[str, Any], np.ndarray]:
    """Return the first sorted same-split, different-speaker donor long enough."""
    candidates = sorted(
        (dict(row) for row in source_records),
        key=lambda row: (str(row.get("speaker", "")), str(row.get("sample_id", ""))),
    )
    for row in candidates:
        if str(row.get("split", "")).lower() != split.lower():
            continue
        if str(row.get("speaker", "")) == target_speaker:
            continue
        waveform, sr = load_audio(resolve_audio_path(row, dataset_root=dataset_root), target_sr=sample_rate)
        if sr == sample_rate and len(waveform) >= required_samples:
            return row, waveform
    raise AttackValidationError(
        f"no same-split different-speaker donor with {required_samples} samples for split={split!r}"
    )


def _sequence_groups(longform_records: Iterable[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in longform_records:
        grouped[str(record["sequence_id"])].append(dict(record))
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["source_order"]))
    return grouped


def _a0_target(sequence_rows: list[dict[str, Any]]) -> dict[str, Any]:
    internal = sequence_rows[1:-1]
    if not internal:
        raise AttackValidationError("A0 requires an internal source utterance")
    return internal[len(internal) // 2]


def _a1_target(
    sequence_rows: list[dict[str, Any]],
    *,
    attack_samples: int,
    margin_samples: int,
    sample_rate: int,
) -> tuple[dict[str, Any], int, int]:
    midpoint = (len(sequence_rows) - 1) / 2
    internal = sorted(
        sequence_rows[1:-1],
        key=lambda row: (abs(int(row["source_order"]) - midpoint), int(row["source_order"])),
    )
    for row in internal:
        utterance_start = int(round(float(row["sequence_start"]) * sample_rate))
        utterance_end = int(round(float(row["sequence_end"]) * sample_rate))
        available = utterance_end - utterance_start
        if available < attack_samples + 2 * margin_samples:
            continue
        start = utterance_start + (available - attack_samples) // 2
        end = start + attack_samples
        if start - utterance_start >= margin_samples and utterance_end - end >= margin_samples:
            return row, start, end
    raise AttackValidationError("no internal utterance can satisfy A1 duration and safety margin")


def _crossfade_replace(clean: np.ndarray, replacement: np.ndarray, start: int, end: int, fade: int) -> np.ndarray:
    if fade <= 0 or 2 * fade >= end - start:
        raise ValueError("crossfade must be positive and shorter than half the attack interval")
    output = clean.copy()
    alpha_in = (np.arange(fade, dtype=np.float32) + 1.0) / (fade + 1.0)
    alpha_out = (np.arange(fade, 0, -1, dtype=np.float32)) / (fade + 1.0)
    output[start:start + fade] = clean[start:start + fade] * (1.0 - alpha_in) + replacement[:fade] * alpha_in
    output[start + fade:end - fade] = replacement[fade:-fade]
    output[end - fade:end] = clean[end - fade:end] * (1.0 - alpha_out) + replacement[-fade:] * alpha_out
    return output


def build_day4_attacks(
    longform_records: Iterable[Mapping[str, Any]],
    source_records: Iterable[Mapping[str, Any]],
    *,
    dataset_root: str | Path,
    repository_root: str | Path,
    a0_directory: str | Path,
    a1_directory: str | Path,
    sample_rate: int = 16000,
    allowed_splits: tuple[str, ...] = ("train",),
    a1_duration_tiers: tuple[float, ...] = (0.75, 1.5, 2.5),
    a1_margin_seconds: float = 0.5,
    crossfade_seconds: float = 0.025,
    rms_epsilon: float = 1e-8,
    rms_gain_min: float = 0.25,
    rms_gain_max: float = 4.0,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Generate at most one deterministic A0 and A1 per clean sequence."""
    if sample_rate <= 0 or not a1_duration_tiers:
        raise ValueError("sample rate and A1 duration tiers must be valid")
    if not (0 < rms_gain_min <= rms_gain_max):
        raise ValueError("invalid RMS gain clamp")
    repository_root = Path(repository_root).resolve()
    a0_directory = repository_root / a0_directory if not Path(a0_directory).is_absolute() else Path(a0_directory)
    a1_directory = repository_root / a1_directory if not Path(a1_directory).is_absolute() else Path(a1_directory)
    a0_directory.mkdir(parents=True, exist_ok=True)
    a1_directory.mkdir(parents=True, exist_ok=True)
    source_rows = [dict(row) for row in source_records]
    source_by_id = {str(row["sample_id"]): row for row in source_rows}
    groups = _sequence_groups(longform_records)
    attacks: list[dict[str, Any]] = []
    skips: list[dict[str, str]] = []
    eligible_index = 0

    for clean_sequence_id, sequence_rows in sorted(groups.items()):
        first = sequence_rows[0]
        split = str(first["split"]).lower()
        target_speaker = str(first["speaker"])
        for attack_label, attack_type in (("A0", A0), ("A1", A1)):
            if split not in allowed_splits:
                skips.append({"clean_sequence_id": clean_sequence_id, "split": split, "target_speaker": target_speaker, "attack_type": attack_type, "reason": "split_not_eligible_single_speaker_no_legal_donor"})
                continue
            try:
                clean, clean_sr = load_audio(first["sequence_audio_path"], target_sr=None)
                if clean_sr != sample_rate:
                    raise AttackValidationError(f"clean sequence sample rate must be {sample_rate}")
                sequence_samples = len(clean)
                if attack_type == A0:
                    target_row = _a0_target(sequence_rows)
                    start = int(round(float(target_row["sequence_start"]) * sample_rate))
                    end = int(round(float(target_row["sequence_end"]) * sample_rate))
                    tier = "complete_source_utterance"
                    fade_samples = 0
                    duration_method = "prefix_crop"
                else:
                    tier_seconds = float(a1_duration_tiers[eligible_index % len(a1_duration_tiers)])
                    attack_samples = int(round(tier_seconds * sample_rate))
                    margin_samples = int(round(a1_margin_seconds * sample_rate))
                    target_row, start, end = _a1_target(sequence_rows, attack_samples=attack_samples, margin_samples=margin_samples, sample_rate=sample_rate)
                    tier = f"{tier_seconds:g}s"
                    fade_samples = int(round(crossfade_seconds * sample_rate))
                    duration_method = "center_crop"
                required_samples = end - start
                donor_row, donor_audio = select_donor(source_rows, target_speaker=target_speaker, split=split, required_samples=required_samples, dataset_root=dataset_root, sample_rate=sample_rate)
                if duration_method == "center_crop":
                    donor_start = (len(donor_audio) - required_samples) // 2
                else:
                    donor_start = 0
                donor_end = donor_start + required_samples
                donor_region = donor_audio[donor_start:donor_end].astype(np.float32, copy=True)
                target_region = clean[start:end]
                target_rms = _rms(target_region)
                donor_rms = _rms(donor_region)

                if attack_type == A1:
                    gain_unclamped = target_rms / max(donor_rms, rms_epsilon)
                    gain = float(np.clip(gain_unclamped, rms_gain_min, rms_gain_max))
                    replacement = donor_region * gain
                    manipulated = _crossfade_replace(clean, replacement, start, end, fade_samples)
                    core_start = start + fade_samples
                    core_end = end - fade_samples
                    output_directory = a1_directory
                    rms_matching = True
                else:
                    gain_unclamped = 1.0
                    gain = 1.0
                    replacement = donor_region
                    manipulated = clean.copy()
                    manipulated[start:end] = replacement
                    core_start, core_end = start, end
                    output_directory = a0_directory
                    rms_matching = False

                attack_id = f"day4_{attack_label.lower()}_{clean_sequence_id}"
                manipulated_sequence_id = f"{clean_sequence_id}_{attack_label.lower()}_manipulated"
                output_path = output_directory / f"{manipulated_sequence_id}.wav"
                write_audio(output_path, manipulated, sample_rate)
                target_source = source_by_id[str(target_row["source_sample_id"])]
                same_text = _normalize_text(target_source.get("transcript_zh", "")) == _normalize_text(donor_row.get("transcript_zh", ""))
                jump_in, jump_out, rms_discontinuity = _boundary_diagnostics(clean, manipulated, start, end, sample_rate)
                attacks.append({
                    "attack_id": attack_id,
                    "attack_type": attack_type,
                    "clean_sequence_id": clean_sequence_id,
                    "manipulated_sequence_id": manipulated_sequence_id,
                    "sequence_pair_id": str(first["sequence_pair_id"]),
                    "clean_audio_path": str(Path(first["sequence_audio_path"]).resolve()),
                    "manipulated_audio_path": str(output_path.resolve()),
                    "target_source_sample_id": str(target_row["source_sample_id"]),
                    "target_source_order": int(target_row["source_order"]),
                    "target_speaker": target_speaker,
                    "target_text_id": str(target_source.get("text_id", "")),
                    "donor_source_sample_id": str(donor_row["sample_id"]),
                    "donor_speaker": str(donor_row["speaker"]),
                    "donor_text_id": str(donor_row.get("text_id", "")),
                    "donor_split": str(donor_row["split"]).lower(),
                    "same_text": same_text,
                    "attack_duration_tier": tier,
                    "attack_start": start / sample_rate,
                    "attack_end": end / sample_rate,
                    "attack_core_start": core_start / sample_rate,
                    "attack_core_end": core_end / sample_rate,
                    "blend_start": start / sample_rate,
                    "blend_end": end / sample_rate,
                    "attack_start_sample": start,
                    "attack_end_sample": end,
                    "attack_core_start_sample": core_start,
                    "attack_core_end_sample": core_end,
                    "blend_start_sample": start,
                    "blend_end_sample": end,
                    "donor_start_sample": donor_start,
                    "donor_end_sample": donor_end,
                    "duration_matching_method": duration_method,
                    "rms_matching": rms_matching,
                    "target_rms": target_rms,
                    "donor_rms": donor_rms,
                    "rms_gain_unclamped": gain_unclamped,
                    "rms_gain": gain,
                    "rms_gain_min": rms_gain_min,
                    "rms_gain_max": rms_gain_max,
                    "crossfade_samples": fade_samples,
                    "sample_rate": sample_rate,
                    "split": split,
                    "source_type": "natural",
                    "is_manipulated": True,
                    "longform_type": "constructed",
                    "sequence_duration": sequence_samples / sample_rate,
                    "sequence_num_samples": sequence_samples,
                    "boundary_jump_in": jump_in,
                    "boundary_jump_out": jump_out,
                    "boundary_rms_discontinuity": rms_discontinuity,
                    "gain_clipped_sample_count": int(np.count_nonzero(np.abs(replacement) > 1.0)),
                })
            except (AttackValidationError, ValueError) as exc:
                skips.append({"clean_sequence_id": clean_sequence_id, "split": split, "target_speaker": target_speaker, "attack_type": attack_type, "reason": str(exc)})
        if split in allowed_splits:
            eligible_index += 1

    validate_attack_manifest(attacks)
    return attacks, skips


def validate_attack_manifest(records: Iterable[Mapping[str, Any]], tolerance: float = 1e-9) -> None:
    rows = [dict(row) for row in records]
    if not rows:
        raise AttackValidationError("attack manifest must not be empty")
    for column in ATTACK_COLUMNS:
        if any(column not in row for row in rows):
            raise AttackValidationError(f"attack manifest missing column={column!r}")
    for field in ("attack_id", "manipulated_sequence_id", "manipulated_audio_path"):
        values = [str(row[field]) for row in rows]
        if len(values) != len(set(values)):
            raise AttackValidationError(f"{field} must be unique")
    for row in rows:
        if row["attack_type"] not in ATTACK_TYPES:
            raise AttackValidationError("unknown attack_type")
        if str(row["donor_speaker"]) == str(row["target_speaker"]):
            raise AttackValidationError("donor speaker must differ from target speaker")
        if str(row["donor_split"]).lower() != str(row["split"]).lower():
            raise AttackValidationError("donor split must equal target split")
        if str(row["longform_type"]) != "constructed" or str(row["source_type"]) == "manipulated":
            raise AttackValidationError("attacked sequences remain constructed with origin source_type")
        if not _as_bool(row["is_manipulated"]):
            raise AttackValidationError("attack rows must have is_manipulated=true")
        sr = int(row["sample_rate"])
        start, end = int(row["attack_start_sample"]), int(row["attack_end_sample"])
        core_start, core_end = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
        blend_start, blend_end = int(row["blend_start_sample"]), int(row["blend_end_sample"])
        if not (0 <= blend_start <= core_start < core_end <= blend_end <= int(row["sequence_num_samples"])):
            raise AttackValidationError("invalid core/blend sample boundaries")
        if start != blend_start or end != blend_end:
            raise AttackValidationError("attack bounds must equal full blend bounds")
        for seconds_field, sample_value in (("attack_start", start), ("attack_end", end), ("attack_core_start", core_start), ("attack_core_end", core_end), ("blend_start", blend_start), ("blend_end", blend_end)):
            if abs(float(row[seconds_field]) - sample_value / sr) > tolerance:
                raise AttackValidationError(f"seconds/sample mismatch for {seconds_field}")
        gain = float(row["rms_gain"])
        if not math.isfinite(gain) or not float(row["rms_gain_min"]) <= gain <= float(row["rms_gain_max"]):
            raise AttackValidationError("RMS gain must be finite and clamped")
        fade = int(row["crossfade_samples"])
        if row["attack_type"] == A0 and (fade != 0 or _as_bool(row["rms_matching"])):
            raise AttackValidationError("A0 must not apply RMS matching or crossfade")
        if row["attack_type"] == A1:
            if fade <= 0 or not _as_bool(row["rms_matching"]):
                raise AttackValidationError("A1 requires RMS matching and crossfade")
            if core_start - start != fade or end - core_end != fade:
                raise AttackValidationError("A1 core/blend boundary does not match crossfade length")


def verify_attack_waveforms(
    records: Iterable[Mapping[str, Any]],
    source_records: Iterable[Mapping[str, Any]],
    *,
    dataset_root: str | Path,
    atol: float = 2.0 / 32768.0,
) -> list[dict[str, Any]]:
    source_by_id = {str(row["sample_id"]): dict(row) for row in source_records}
    results = []
    for row in records:
        sr = int(row["sample_rate"])
        clean, clean_sr = load_audio(row["clean_audio_path"], target_sr=None)
        manipulated, manipulated_sr = load_audio(row["manipulated_audio_path"], target_sr=None)
        if clean_sr != sr or manipulated_sr != sr or len(clean) != len(manipulated):
            raise AttackValidationError(f"duration/sample-rate mismatch: {row['attack_id']}")
        if not np.all(np.isfinite(manipulated)):
            raise AttackValidationError(f"non-finite manipulated waveform: {row['attack_id']}")
        start, end = int(row["attack_start_sample"]), int(row["attack_end_sample"])
        outside_equal = np.array_equal(clean[:start], manipulated[:start]) and np.array_equal(clean[end:], manipulated[end:])
        inside_changed = bool(np.any(clean[start:end] != manipulated[start:end]))
        if not outside_equal or not inside_changed:
            raise AttackValidationError(f"waveform change-region mismatch: {row['attack_id']}")
        donor_row = source_by_id[str(row["donor_source_sample_id"])]
        donor, donor_sr = load_audio(resolve_audio_path(donor_row, dataset_root=dataset_root), target_sr=sr)
        donor_start, donor_end = int(row["donor_start_sample"]), int(row["donor_end_sample"])
        expected = donor[donor_start:donor_end] * float(row["rms_gain"])
        core_start, core_end = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
        offset_start, offset_end = core_start - start, core_end - start
        core_matches_donor = np.allclose(manipulated[core_start:core_end], np.clip(expected[offset_start:offset_end], -1.0, 1.0), atol=atol, rtol=0.0)
        if not core_matches_donor:
            raise AttackValidationError(f"core donor material mismatch: {row['attack_id']}")
        results.append({"attack_id": row["attack_id"], "outside_equal": outside_equal, "inside_changed": inside_changed, "core_matches_donor": core_matches_donor})
    return results


def save_attack_manifest(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    rows = [dict(row) for row in records]
    validate_attack_manifest(rows)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ATTACK_COLUMNS)
        writer.writeheader(); writer.writerows(rows)


def load_attack_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def save_skip_manifest(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SKIP_COLUMNS)
        writer.writeheader(); writer.writerows(records)
