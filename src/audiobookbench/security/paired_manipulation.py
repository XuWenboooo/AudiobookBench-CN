"""Day 4.5 deterministic paired A0/A1 manipulation controls."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from audiobookbench.data.prepare_audio import resolve_audio_path
from audiobookbench.preprocessing.audio_io import load_audio, probe_audio, write_audio
from audiobookbench.security.manipulation_dataset import A0, A1, _crossfade_replace, _normalize_text, _rms


PAIRED_ATTACK_COLUMNS = [
    "paired_case_id", "attack_id", "attack_type", "clean_sequence_id",
    "manipulated_sequence_id", "sequence_pair_id", "clean_audio_path",
    "clean_audio_relpath", "manipulated_audio_path", "manipulated_audio_relpath",
    "split", "target_source_sample_id", "target_source_order", "target_speaker",
    "target_text_id", "donor_source_sample_id", "donor_speaker", "donor_text_id",
    "donor_split", "same_text", "donor_usage_count", "donor_speaker_usage_count",
    "target_start", "target_end", "target_start_sample", "target_end_sample",
    "attack_start", "attack_end", "attack_core_start", "attack_core_end",
    "blend_start", "blend_end", "attack_start_sample", "attack_end_sample",
    "attack_core_start_sample", "attack_core_end_sample", "blend_start_sample",
    "blend_end_sample", "donor_start_sample", "donor_end_sample", "duration_tier",
    "duration_matching_method", "rms_matching", "target_rms", "donor_rms",
    "rms_gain_unclamped", "rms_gain", "rms_gain_min", "rms_gain_max",
    "crossfade_samples", "sample_rate", "source_type", "is_manipulated",
    "longform_type", "sequence_duration", "sequence_num_samples",
    "boundary_jump_in", "boundary_jump_out", "boundary_jump_total",
    "local_rms_discontinuity", "gain_clipped_sample_count",
]

SKIP_COLUMNS = ["clean_sequence_id", "split", "target_speaker", "duration_tier", "reason"]
VERIFICATION_COLUMNS = [
    "paired_case_id", "attack_id", "attack_type", "duration_equal", "sample_rate_equal",
    "channel_equal", "finite", "outside_equal", "inside_changed", "core_matches_donor",
]
DIAGNOSTIC_COLUMNS = [
    "paired_case_id", "split", "a0_boundary_jump_total", "a1_boundary_jump_total",
    "boundary_jump_difference_a1_minus_a0", "a1_lower_boundary_jump",
    "a0_local_rms_discontinuity", "a1_local_rms_discontinuity",
    "rms_difference_a1_minus_a0", "a1_lower_local_rms_discontinuity",
]


class PairedAttackError(ValueError):
    """Raised when paired attack selection, lineage, or waveform checks fail."""


def _groups(records: Iterable[Mapping[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record[key])].append(dict(record))
    return grouped


def _as_bool(value: Any) -> bool:
    return value if isinstance(value, bool) else str(value).strip().lower() in {"true", "1", "yes"}


def _boundary_diagnostics(waveform: np.ndarray, start: int, end: int, sample_rate: int) -> tuple[float, float, float]:
    jump_in = abs(float(waveform[start]) - float(waveform[start - 1])) if start else 0.0
    jump_out = abs(float(waveform[end]) - float(waveform[end - 1])) if end < len(waveform) else 0.0
    window = max(1, int(round(0.025 * sample_rate)))
    before = waveform[max(0, start - window):start]
    inside_left = waveform[start:min(end, start + window)]
    inside_right = waveform[max(start, end - window):end]
    after = waveform[end:min(len(waveform), end + window)]
    local_rms = abs(_rms(before) - _rms(inside_left)) + abs(_rms(inside_right) - _rms(after))
    return jump_in, jump_out, local_rms


def _select_target(
    rows: list[dict[str, Any]], attack_samples: int, margin_samples: int, sample_rate: int,
) -> tuple[dict[str, Any], int, int]:
    ordered = sorted(rows, key=lambda row: int(row["source_order"]))
    midpoint = (len(ordered) - 1) / 2
    candidates = sorted(
        ordered[1:-1],
        key=lambda row: (abs(int(row["source_order"]) - midpoint), int(row["source_order"])),
    )
    for row in candidates:
        source_start = int(round(float(row["sequence_start"]) * sample_rate))
        source_end = int(round(float(row["sequence_end"]) * sample_rate))
        available = source_end - source_start
        if available < attack_samples + 2 * margin_samples:
            continue
        start = source_start + (available - attack_samples) // 2
        end = start + attack_samples
        if start - source_start >= margin_samples and source_end - end >= margin_samples:
            return row, start, end
    raise PairedAttackError("no internal utterance satisfies duration tier and safety margin")


def _select_balanced_donor(
    source_rows: list[dict[str, Any]], *, target_speaker: str, split: str,
    required_samples: int, dataset_root: str | Path, sample_rate: int,
    speaker_usage: Counter[str], utterance_usage: Counter[str], repeat_cap: int,
    speaker_cursor: dict[str, int],
) -> tuple[dict[str, Any], np.ndarray]:
    by_speaker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        if str(row["split"]) == split and str(row["speaker"]) != target_speaker:
            by_speaker[str(row["speaker"])].append(row)
    all_split_speakers = sorted({str(row["speaker"]) for row in source_rows if str(row["split"]) == split})
    start = speaker_cursor.get(split, 0) % len(all_split_speakers)
    speaker_order = [all_split_speakers[(start + offset) % len(all_split_speakers)] for offset in range(len(all_split_speakers))]
    for speaker in speaker_order:
        if speaker == target_speaker or speaker not in by_speaker:
            continue
        candidates = sorted(
            by_speaker[speaker],
            key=lambda row: (utterance_usage[str(row["sample_id"])], str(row["sample_id"])),
        )
        for row in candidates:
            sample_id = str(row["sample_id"])
            if utterance_usage[sample_id] >= repeat_cap:
                continue
            donor, donor_sr = load_audio(resolve_audio_path(row, dataset_root=dataset_root), target_sr=sample_rate)
            if donor_sr == sample_rate and len(donor) >= required_samples:
                speaker_usage[speaker] += 1
                utterance_usage[sample_id] += 1
                speaker_cursor[split] = (all_split_speakers.index(speaker) + 1) % len(all_split_speakers)
                return row, donor
    raise PairedAttackError("no legal same-split balanced donor within utterance repeat cap")


def build_paired_attacks(
    longform_records: Iterable[Mapping[str, Any]],
    source_records: Iterable[Mapping[str, Any]],
    *,
    dataset_root: str | Path,
    repository_root: str | Path,
    a0_directory: str | Path,
    a1_directory: str | Path,
    duration_tiers: tuple[float, ...] = (0.75, 1.5, 2.5),
    margin_seconds: float = 0.5,
    sample_rate: int = 16000,
    crossfade_seconds: float = 0.025,
    rms_epsilon: float = 1e-8,
    rms_gain_min: float = 0.25,
    rms_gain_max: float = 4.0,
    donor_repeat_cap: int = 1,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not duration_tiers or any(value <= 0 for value in duration_tiers):
        raise ValueError("duration tiers must be positive")
    if donor_repeat_cap <= 0 or sample_rate <= 0:
        raise ValueError("repeat cap and sample rate must be positive")
    root = Path(repository_root).resolve()
    a0_root = Path(a0_directory)
    a1_root = Path(a1_directory)
    if not a0_root.is_absolute():
        a0_root = root / a0_root
    if not a1_root.is_absolute():
        a1_root = root / a1_root
    a0_root.mkdir(parents=True, exist_ok=True)
    a1_root.mkdir(parents=True, exist_ok=True)

    source_rows = [dict(row) for row in source_records]
    source_by_id = {str(row["sample_id"]): row for row in source_rows}
    sequences = _groups(longform_records, "sequence_id")
    speaker_usage: dict[str, Counter[str]] = defaultdict(Counter)
    speaker_cursor: dict[str, int] = {}
    utterance_usage: Counter[str] = Counter()
    attacks: list[dict[str, Any]] = []
    skips: list[dict[str, Any]] = []
    fade_samples = int(round(crossfade_seconds * sample_rate))
    margin_samples = int(round(margin_seconds * sample_rate))

    for sequence_index, clean_sequence_id in enumerate(sorted(sequences)):
        rows = sequences[clean_sequence_id]
        first = rows[0]
        split = str(first["split"])
        target_speaker = str(first["speaker"])
        tier = float(duration_tiers[sequence_index % len(duration_tiers)])
        attack_samples = int(round(tier * sample_rate))
        try:
            target_row, target_start, target_end = _select_target(rows, attack_samples, margin_samples, sample_rate)
            clean, clean_sr = load_audio(first["sequence_audio_path"], target_sr=None)
            if clean_sr != sample_rate:
                raise PairedAttackError(f"clean sequence must be {sample_rate} Hz")
            donor_row, donor = _select_balanced_donor(
                source_rows, target_speaker=target_speaker, split=split,
                required_samples=attack_samples, dataset_root=dataset_root,
                sample_rate=sample_rate, speaker_usage=speaker_usage[split],
                utterance_usage=utterance_usage, repeat_cap=donor_repeat_cap,
                speaker_cursor=speaker_cursor,
            )
            donor_start = (len(donor) - attack_samples) // 2
            donor_end = donor_start + attack_samples
            donor_crop = donor[donor_start:donor_end].astype(np.float32, copy=True)
            target_crop = clean[target_start:target_end]
            target_rms = _rms(target_crop)
            donor_rms = _rms(donor_crop)
            gain_unclamped = target_rms / max(donor_rms, rms_epsilon)
            gain = float(np.clip(gain_unclamped, rms_gain_min, rms_gain_max))
            if 2 * fade_samples >= attack_samples:
                raise PairedAttackError("duration tier is too short for fixed crossfade")

            pair_number = len(attacks) // 2 + 1
            paired_case_id = f"paircase_{pair_number:04d}"
            target_source = source_by_id[str(target_row["source_sample_id"])]
            same_text = _normalize_text(target_source["transcript_zh"]) == _normalize_text(donor_row["transcript_zh"])
            clean_path = Path(str(first["sequence_audio_path"])).resolve()
            clean_relpath = str(first.get("sequence_audio_relpath", "")).replace("\\", "/")

            constructions = []
            a0_waveform = clean.copy()
            a0_waveform[target_start:target_end] = donor_crop
            constructions.append((A0, "A0", a0_waveform, 1.0, 1.0, False, 0, target_start, target_end, a0_root))
            scaled = donor_crop * gain
            a1_waveform = _crossfade_replace(clean, scaled, target_start, target_end, fade_samples)
            constructions.append((A1, "A1", a1_waveform, gain_unclamped, gain, True, fade_samples, target_start + fade_samples, target_end - fade_samples, a1_root))

            for attack_type, label, waveform, unclamped, actual_gain, rms_matching, crossfade, core_start, core_end, output_root in constructions:
                attack_id = f"day45_{paired_case_id}_{label.lower()}"
                manipulated_id = f"{clean_sequence_id}_{paired_case_id}_{label.lower()}_manipulated"
                output_path = output_root / split / target_speaker / f"{manipulated_id}.wav"
                write_audio(output_path, waveform, sample_rate)
                output_relpath = output_path.resolve().relative_to(root).as_posix()
                jump_in, jump_out, local_rms = _boundary_diagnostics(waveform, target_start, target_end, sample_rate)
                attacks.append({
                    "paired_case_id": paired_case_id,
                    "attack_id": attack_id,
                    "attack_type": attack_type,
                    "clean_sequence_id": clean_sequence_id,
                    "manipulated_sequence_id": manipulated_id,
                    "sequence_pair_id": str(first["sequence_pair_id"]),
                    "clean_audio_path": str(clean_path),
                    "clean_audio_relpath": clean_relpath,
                    "manipulated_audio_path": str(output_path.resolve()),
                    "manipulated_audio_relpath": output_relpath,
                    "split": split,
                    "target_source_sample_id": str(target_row["source_sample_id"]),
                    "target_source_order": int(target_row["source_order"]),
                    "target_speaker": target_speaker,
                    "target_text_id": str(target_source["text_id"]),
                    "donor_source_sample_id": str(donor_row["sample_id"]),
                    "donor_speaker": str(donor_row["speaker"]),
                    "donor_text_id": str(donor_row["text_id"]),
                    "donor_split": str(donor_row["split"]),
                    "same_text": same_text,
                    "donor_usage_count": utterance_usage[str(donor_row["sample_id"])],
                    "donor_speaker_usage_count": speaker_usage[split][str(donor_row["speaker"])],
                    "target_start": target_start / sample_rate,
                    "target_end": target_end / sample_rate,
                    "target_start_sample": target_start,
                    "target_end_sample": target_end,
                    "attack_start": target_start / sample_rate,
                    "attack_end": target_end / sample_rate,
                    "attack_core_start": core_start / sample_rate,
                    "attack_core_end": core_end / sample_rate,
                    "blend_start": target_start / sample_rate,
                    "blend_end": target_end / sample_rate,
                    "attack_start_sample": target_start,
                    "attack_end_sample": target_end,
                    "attack_core_start_sample": core_start,
                    "attack_core_end_sample": core_end,
                    "blend_start_sample": target_start,
                    "blend_end_sample": target_end,
                    "donor_start_sample": donor_start,
                    "donor_end_sample": donor_end,
                    "duration_tier": f"{tier:g}s",
                    "duration_matching_method": "center_crop",
                    "rms_matching": rms_matching,
                    "target_rms": target_rms,
                    "donor_rms": donor_rms,
                    "rms_gain_unclamped": unclamped,
                    "rms_gain": actual_gain,
                    "rms_gain_min": rms_gain_min,
                    "rms_gain_max": rms_gain_max,
                    "crossfade_samples": crossfade,
                    "sample_rate": sample_rate,
                    "source_type": "natural",
                    "is_manipulated": True,
                    "longform_type": "constructed",
                    "sequence_duration": len(clean) / sample_rate,
                    "sequence_num_samples": len(clean),
                    "boundary_jump_in": jump_in,
                    "boundary_jump_out": jump_out,
                    "boundary_jump_total": jump_in + jump_out,
                    "local_rms_discontinuity": local_rms,
                    "gain_clipped_sample_count": int(np.count_nonzero(np.abs(donor_crop * actual_gain) > 1.0)),
                })
        except (PairedAttackError, ValueError, RuntimeError) as exc:
            skips.append({
                "clean_sequence_id": clean_sequence_id,
                "split": split,
                "target_speaker": target_speaker,
                "duration_tier": f"{tier:g}s",
                "reason": str(exc),
            })
    validate_paired_attack_manifest(attacks)
    return attacks, skips


def validate_paired_attack_manifest(records: Iterable[Mapping[str, Any]], tolerance: float = 1e-9) -> None:
    rows = [dict(row) for row in records]
    if not rows:
        raise PairedAttackError("paired attack manifest must not be empty")
    for column in PAIRED_ATTACK_COLUMNS:
        if any(column not in row for row in rows):
            raise PairedAttackError(f"paired attack manifest missing column={column}")
    for field in ("attack_id", "manipulated_sequence_id", "manipulated_audio_path"):
        values = [str(row[field]) for row in rows]
        if len(values) != len(set(values)):
            raise PairedAttackError(f"{field} must be unique")
    paired = _groups(rows, "paired_case_id")
    for case_id, case in paired.items():
        if len(case) != 2 or {row["attack_type"] for row in case} != {A0, A1}:
            raise PairedAttackError(f"{case_id} must contain exactly one A0 and one A1")
        shared = (
            "clean_sequence_id", "sequence_pair_id", "split", "target_source_sample_id",
            "target_speaker", "target_text_id", "donor_source_sample_id", "donor_speaker",
            "donor_text_id", "donor_split", "same_text", "target_start_sample",
            "target_end_sample", "donor_start_sample", "donor_end_sample",
        )
        for field in shared:
            if len({str(row[field]) for row in case}) != 1:
                raise PairedAttackError(f"{case_id} paired field differs: {field}")
        for row in case:
            if str(row["split"]) != str(row["donor_split"]):
                raise PairedAttackError("cross-split donor leakage")
            if str(row["target_speaker"]) == str(row["donor_speaker"]):
                raise PairedAttackError("donor speaker must differ from target")
            if str(row["source_type"]) != "natural" or str(row["longform_type"]) != "constructed" or not _as_bool(row["is_manipulated"]):
                raise PairedAttackError("invalid source/manipulation/longform semantics")
            sr = int(row["sample_rate"])
            target_start, target_end = int(row["target_start_sample"]), int(row["target_end_sample"])
            if not 0 <= target_start < target_end <= int(row["sequence_num_samples"]):
                raise PairedAttackError("target interval out of bounds")
            if int(row["attack_start_sample"]) != target_start or int(row["attack_end_sample"]) != target_end:
                raise PairedAttackError("attack interval must equal shared target interval")
            for seconds_name, samples_name in (
                ("target_start", "target_start_sample"), ("target_end", "target_end_sample"),
                ("attack_start", "attack_start_sample"), ("attack_end", "attack_end_sample"),
                ("attack_core_start", "attack_core_start_sample"), ("attack_core_end", "attack_core_end_sample"),
                ("blend_start", "blend_start_sample"), ("blend_end", "blend_end_sample"),
            ):
                if abs(float(row[seconds_name]) - int(row[samples_name]) / sr) > tolerance:
                    raise PairedAttackError(f"seconds/sample mismatch: {seconds_name}")
            core_start, core_end = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
            if not target_start <= core_start < core_end <= target_end:
                raise PairedAttackError("invalid core boundary")
            if row["attack_type"] == A0:
                if int(row["crossfade_samples"]) or _as_bool(row["rms_matching"]) or (core_start, core_end) != (target_start, target_end):
                    raise PairedAttackError("invalid A0 DSP metadata")
            else:
                fade = int(row["crossfade_samples"])
                gain = float(row["rms_gain"])
                if fade <= 0 or not _as_bool(row["rms_matching"]) or not math.isfinite(gain):
                    raise PairedAttackError("invalid A1 DSP metadata")
                if core_start - target_start != fade or target_end - core_end != fade:
                    raise PairedAttackError("A1 core does not match fixed crossfade")


def verify_paired_waveforms(
    records: Iterable[Mapping[str, Any]], source_records: Iterable[Mapping[str, Any]],
    *, dataset_root: str | Path, atol: float = 2.0 / 32768.0,
) -> list[dict[str, Any]]:
    rows = [dict(row) for row in records]
    validate_paired_attack_manifest(rows)
    source_by_id = {str(row["sample_id"]): dict(row) for row in source_records}
    results: list[dict[str, Any]] = []
    for row in rows:
        clean_info = probe_audio(row["clean_audio_path"])
        manipulated_info = probe_audio(row["manipulated_audio_path"])
        clean, clean_sr = load_audio(row["clean_audio_path"], target_sr=None)
        manipulated, manipulated_sr = load_audio(row["manipulated_audio_path"], target_sr=None)
        duration_equal = clean_info.frames == manipulated_info.frames == int(row["sequence_num_samples"])
        sample_rate_equal = clean_sr == manipulated_sr == int(row["sample_rate"])
        channel_equal = clean_info.channels == manipulated_info.channels == 1
        finite = bool(np.all(np.isfinite(manipulated)))
        start, end = int(row["target_start_sample"]), int(row["target_end_sample"])
        outside_equal = np.array_equal(clean[:start], manipulated[:start]) and np.array_equal(clean[end:], manipulated[end:])
        inside_changed = bool(np.any(clean[start:end] != manipulated[start:end]))
        donor_row = source_by_id[str(row["donor_source_sample_id"])]
        donor, _ = load_audio(resolve_audio_path(donor_row, dataset_root=dataset_root), target_sr=int(row["sample_rate"]))
        donor_start, donor_end = int(row["donor_start_sample"]), int(row["donor_end_sample"])
        expected = donor[donor_start:donor_end] * float(row["rms_gain"])
        core_start, core_end = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
        offset_start, offset_end = core_start - start, core_end - start
        core_matches = bool(np.allclose(
            manipulated[core_start:core_end], np.clip(expected[offset_start:offset_end], -1.0, 1.0),
            atol=atol, rtol=0.0,
        ))
        checks = (duration_equal, sample_rate_equal, channel_equal, finite, outside_equal, inside_changed, core_matches)
        if not all(checks):
            raise PairedAttackError(f"waveform verification failed for {row['attack_id']}: {checks}")
        results.append({
            "paired_case_id": row["paired_case_id"], "attack_id": row["attack_id"],
            "attack_type": row["attack_type"], "duration_equal": duration_equal,
            "sample_rate_equal": sample_rate_equal, "channel_equal": channel_equal,
            "finite": finite, "outside_equal": outside_equal,
            "inside_changed": inside_changed, "core_matches_donor": core_matches,
        })
    return results


def build_paired_diagnostics(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in records]
    validate_paired_attack_manifest(rows)
    output = []
    for case_id, case in sorted(_groups(rows, "paired_case_id").items()):
        by_type = {row["attack_type"]: row for row in case}
        a0, a1 = by_type[A0], by_type[A1]
        a0_jump, a1_jump = float(a0["boundary_jump_total"]), float(a1["boundary_jump_total"])
        a0_rms, a1_rms = float(a0["local_rms_discontinuity"]), float(a1["local_rms_discontinuity"])
        output.append({
            "paired_case_id": case_id, "split": a0["split"],
            "a0_boundary_jump_total": a0_jump, "a1_boundary_jump_total": a1_jump,
            "boundary_jump_difference_a1_minus_a0": a1_jump - a0_jump,
            "a1_lower_boundary_jump": a1_jump < a0_jump,
            "a0_local_rms_discontinuity": a0_rms, "a1_local_rms_discontinuity": a1_rms,
            "rms_difference_a1_minus_a0": a1_rms - a0_rms,
            "a1_lower_local_rms_discontinuity": a1_rms < a0_rms,
        })
    return output


def save_paired_attack_manifest(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    rows = [dict(row) for row in records]
    validate_paired_attack_manifest(rows)
    _save_csv(rows, path, PAIRED_ATTACK_COLUMNS)


def load_paired_attack_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def save_skips(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    _save_csv([dict(row) for row in records], path, SKIP_COLUMNS)


def save_verification(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    _save_csv([dict(row) for row in records], path, VERIFICATION_COLUMNS)


def save_diagnostics(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    _save_csv([dict(row) for row in records], path, DIAGNOSTIC_COLUMNS)


def _save_csv(rows: list[dict[str, Any]], path: str | Path, columns: list[str]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
