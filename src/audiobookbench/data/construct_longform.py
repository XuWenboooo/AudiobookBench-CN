"""Deterministic construction of traceable long-form sequences.

The outputs are explicitly constructed long-form and must never be described as
native audiobook or native continuous long-form recordings.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from audiobookbench.data.manifest import normalize_bool
from audiobookbench.data.prepare_audio import resolve_audio_path
from audiobookbench.preprocessing.audio_io import load_audio, probe_audio, write_audio

LONGFORM_TYPE = "constructed"

LINEAGE_COLUMNS = [
    "sequence_id",
    "sequence_pair_id",
    "clean_sequence_id",
    "sequence_audio_path",
    "sequence_audio_relpath",
    "speaker",
    "split",
    "sequence_duration",
    "sequence_num_samples",
    "sample_rate",
    "source_sample_id",
    "source_audio_relpath",
    "source_order",
    "source_start",
    "source_end",
    "source_duration",
    "sequence_start",
    "sequence_end",
    "gap_before",
    "gap_before_start",
    "gap_before_end",
    "gap_after",
    "gap_after_start",
    "gap_after_end",
    "longform_type",
]


class LongformValidationError(ValueError):
    """Raised when constructed-long-form lineage is inconsistent."""


def _source_sort_key(record: Mapping[str, Any]) -> tuple[int, str]:
    try:
        rank = int(record.get("selection_rank", 0))
    except (TypeError, ValueError) as exc:
        raise LongformValidationError("selection_rank must be an integer") from exc
    return rank, str(record["sample_id"])


def construct_longform_sequences(
    source_records: Iterable[Mapping[str, Any]],
    *,
    dataset_root: str | Path,
    output_directory: str | Path,
    repository_root: str | Path,
    target_sr: int = 16000,
    gap_seconds: float = 0.3,
    min_duration: float = 20.0,
    preferred_duration: float = 30.0,
    max_duration: float = 60.0,
    min_utterances: int = 4,
    max_utterances: int = 12,
    sequences_per_speaker: int = 2,
    sequence_id_prefix: str = "day35",
) -> list[dict[str, Any]]:
    """Construct deterministic same-speaker, same-split real-audio sequences."""
    if target_sr <= 0:
        raise ValueError("target_sr must be > 0")
    if gap_seconds < 0:
        raise ValueError("gap_seconds must be >= 0")
    if not (0 < min_duration <= preferred_duration <= max_duration):
        raise ValueError("duration bounds must satisfy 0 < minimum <= preferred <= maximum")
    if not (1 <= min_utterances <= max_utterances):
        raise ValueError("utterance bounds must satisfy 1 <= minimum <= maximum")
    if sequences_per_speaker <= 0:
        raise ValueError("sequences_per_speaker must be > 0")
    if not sequence_id_prefix or not sequence_id_prefix.replace("_", "").isalnum():
        raise ValueError("sequence_id_prefix must contain only letters, digits, or underscores")

    rows = [dict(row) for row in source_records]
    seen_samples: set[str] = set()
    speaker_splits: dict[str, set[str]] = defaultdict(set)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        sample_id = str(row.get("sample_id", "")).strip()
        speaker = str(row.get("speaker", "")).strip()
        split = str(row.get("split", "")).strip().lower()
        if not sample_id or not speaker or not split:
            raise LongformValidationError("sample_id, speaker, and split are required")
        if sample_id in seen_samples:
            raise LongformValidationError(f"duplicate source sample_id={sample_id!r}")
        seen_samples.add(sample_id)
        if normalize_bool(row.get("is_manipulated", False)):
            raise LongformValidationError("constructed clean sequences require unmanipulated sources")
        speaker_splits[speaker].add(split)
        grouped[(speaker, split)].append(row)
    conflicts = {speaker: splits for speaker, splits in speaker_splits.items() if len(splits) > 1}
    if conflicts:
        raise LongformValidationError(f"speaker must not cross splits: {conflicts}")

    repository_root = Path(repository_root).resolve()
    output_directory = Path(output_directory)
    if not output_directory.is_absolute():
        output_directory = repository_root / output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    gap_samples = int(round(gap_seconds * target_sr))
    actual_gap = gap_samples / target_sr
    lineage: list[dict[str, Any]] = []

    for (speaker, split), group in sorted(grouped.items()):
        ordered = sorted(group, key=_source_sort_key)
        cursor = 0
        for sequence_index in range(sequences_per_speaker):
            selected: list[tuple[dict[str, Any], np.ndarray, float]] = []
            running_samples = 0
            while cursor < len(ordered) and len(selected) < max_utterances:
                source = ordered[cursor]
                path = resolve_audio_path(source, dataset_root=dataset_root)
                waveform, sr = load_audio(path, target_sr=target_sr)
                projected = running_samples + (gap_samples if selected else 0) + len(waveform)
                projected_seconds = projected / target_sr
                if len(selected) >= min_utterances and projected_seconds > max_duration:
                    break
                selected.append((source, waveform, len(waveform) / sr))
                running_samples = projected
                cursor += 1
                if len(selected) >= min_utterances and projected_seconds >= preferred_duration:
                    break

            if len(selected) < min_utterances or running_samples / target_sr < min_duration:
                raise LongformValidationError(
                    f"insufficient ordered source audio for {speaker} sequence {sequence_index}"
                )

            sequence_id = f"{sequence_id_prefix}_{split}_{speaker}_seq{sequence_index:03d}"
            sequence_pair_id = f"longform_pair_{sequence_id}"
            parts: list[np.ndarray] = []
            current_sample = 0
            sequence_rows: list[dict[str, Any]] = []
            for source_order, (source, waveform, source_duration) in enumerate(selected):
                gap_before_samples = gap_samples if source_order else 0
                if gap_before_samples:
                    parts.append(np.zeros(gap_before_samples, dtype=np.float32))
                    current_sample += gap_before_samples
                sequence_start_sample = current_sample
                parts.append(waveform.astype(np.float32, copy=False))
                current_sample += len(waveform)
                sequence_end_sample = current_sample
                gap_after_samples = gap_samples if source_order < len(selected) - 1 else 0
                sequence_rows.append(
                    {
                        "sequence_id": sequence_id,
                        "sequence_pair_id": sequence_pair_id,
                        "clean_sequence_id": sequence_id,
                        "speaker": speaker,
                        "split": split,
                        "sample_rate": target_sr,
                        "source_sample_id": str(source["sample_id"]),
                        "source_audio_relpath": str(source.get("audio_relpath", "")).replace("\\", "/"),
                        "source_order": source_order,
                        "source_start": 0.0,
                        "source_end": source_duration,
                        "source_duration": source_duration,
                        "sequence_start": sequence_start_sample / target_sr,
                        "sequence_end": sequence_end_sample / target_sr,
                        "gap_before": gap_before_samples / target_sr,
                        "gap_before_start": (sequence_start_sample - gap_before_samples) / target_sr,
                        "gap_before_end": sequence_start_sample / target_sr,
                        "gap_after": gap_after_samples / target_sr,
                        "gap_after_start": sequence_end_sample / target_sr,
                        "gap_after_end": (sequence_end_sample + gap_after_samples) / target_sr,
                        "longform_type": LONGFORM_TYPE,
                    }
                )

            sequence_audio = np.concatenate(parts).astype(np.float32, copy=False)
            if not np.all(np.isfinite(sequence_audio)):
                raise LongformValidationError(f"non-finite constructed waveform: {sequence_id}")
            output_path = output_directory / split / speaker / f"{sequence_id}.wav"
            write_audio(output_path, sequence_audio, target_sr)
            relative_output = output_path.resolve().relative_to(repository_root).as_posix()
            sequence_duration = len(sequence_audio) / target_sr
            for row in sequence_rows:
                row.update(
                    {
                        "sequence_audio_path": str(output_path.resolve()),
                        "sequence_audio_relpath": relative_output,
                        "sequence_duration": sequence_duration,
                        "sequence_num_samples": len(sequence_audio),
                    }
                )
            lineage.extend(sequence_rows)

    validate_longform_lineage(lineage, source_sample_ids=seen_samples, check_audio=True)
    return lineage


def validate_longform_lineage(
    records: Iterable[Mapping[str, Any]],
    *,
    source_sample_ids: set[str] | None = None,
    check_audio: bool = False,
    tolerance: float = 1e-6,
) -> None:
    rows = [dict(row) for row in records]
    if not rows:
        raise LongformValidationError("long-form lineage must not be empty")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sequence_identity: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        missing = [column for column in LINEAGE_COLUMNS if column not in row]
        if missing:
            raise LongformValidationError(f"long-form row missing columns: {missing}")
        if row["longform_type"] != LONGFORM_TYPE:
            raise LongformValidationError("longform_type must equal 'constructed'")
        if source_sample_ids is not None and row["source_sample_id"] not in source_sample_ids:
            raise LongformValidationError(f"untraceable source_sample_id={row['source_sample_id']!r}")
        sequence_id = str(row["sequence_id"])
        identity = (str(row["speaker"]), str(row["split"]), str(row["sequence_audio_path"]))
        if sequence_id in sequence_identity and sequence_identity[sequence_id] != identity:
            raise LongformValidationError(f"sequence_id reused across speaker/split/path: {sequence_id}")
        sequence_identity[sequence_id] = identity
        grouped[sequence_id].append(row)

    for sequence_id, sequence_rows in grouped.items():
        sequence_rows.sort(key=lambda row: int(row["source_order"]))
        if [int(row["source_order"]) for row in sequence_rows] != list(range(len(sequence_rows))):
            raise LongformValidationError(f"source_order is not continuous: {sequence_id}")
        speakers = {row["speaker"] for row in sequence_rows}
        splits = {row["split"] for row in sequence_rows}
        if len(speakers) != 1 or len(splits) != 1:
            raise LongformValidationError(f"sequence crosses speaker or split: {sequence_id}")

        for index, row in enumerate(sequence_rows):
            source_start = float(row["source_start"])
            source_end = float(row["source_end"])
            source_duration = float(row["source_duration"])
            sequence_start = float(row["sequence_start"])
            sequence_end = float(row["sequence_end"])
            gap_before = float(row["gap_before"])
            gap_after = float(row["gap_after"])
            if source_start < 0 or source_start >= source_end or source_end > source_duration + tolerance:
                raise LongformValidationError(f"source interval out of bounds: {sequence_id}")
            if abs((sequence_end - sequence_start) - (source_end - source_start)) > tolerance:
                raise LongformValidationError(f"source/sequence duration mismatch: {sequence_id}")
            if abs(float(row["gap_before_end"]) - sequence_start) > tolerance:
                raise LongformValidationError(f"gap_before boundary mismatch: {sequence_id}")
            if abs(float(row["gap_before_end"]) - float(row["gap_before_start"]) - gap_before) > tolerance:
                raise LongformValidationError(f"gap_before duration mismatch: {sequence_id}")
            if abs(float(row["gap_after_start"]) - sequence_end) > tolerance:
                raise LongformValidationError(f"gap_after boundary mismatch: {sequence_id}")
            if abs(float(row["gap_after_end"]) - float(row["gap_after_start"]) - gap_after) > tolerance:
                raise LongformValidationError(f"gap_after duration mismatch: {sequence_id}")
            if index == 0 and (abs(sequence_start) > tolerance or abs(gap_before) > tolerance):
                raise LongformValidationError(f"first source must begin at zero: {sequence_id}")
            if index:
                previous = sequence_rows[index - 1]
                if abs(sequence_start - float(previous["gap_after_end"])) > tolerance:
                    raise LongformValidationError(f"unrecorded gap or overlap: {sequence_id}")
                if abs(gap_before - float(previous["gap_after"])) > tolerance:
                    raise LongformValidationError(f"adjacent gap values disagree: {sequence_id}")

        last = sequence_rows[-1]
        if abs(float(last["gap_after"])) > tolerance:
            raise LongformValidationError(f"last source must not have trailing gap: {sequence_id}")
        if abs(float(last["sequence_end"]) - float(last["sequence_duration"])) > tolerance:
            raise LongformValidationError(f"sequence duration mismatch: {sequence_id}")
        if check_audio:
            info = probe_audio(last["sequence_audio_path"])
            expected_samples = int(last["sequence_num_samples"])
            if info.sample_rate != int(last["sample_rate"]) or info.frames != expected_samples:
                raise LongformValidationError(f"waveform metadata mismatch: {sequence_id}")
            if abs(info.duration - float(last["sequence_duration"])) > tolerance:
                raise LongformValidationError(f"waveform duration mismatch: {sequence_id}")


def save_longform_manifest(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    rows = [dict(row) for row in records]
    validate_longform_lineage(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LINEAGE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def load_longform_manifest(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]
