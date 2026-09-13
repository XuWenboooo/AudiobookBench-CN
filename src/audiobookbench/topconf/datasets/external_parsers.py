"""Fail-closed parsers for the authorized Phase 3 external metadata.

These parsers validate annotation structure only.  They deliberately do not
infer audio duration or manufacture missing audio/model artifacts.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PartialEditRecord:
    audio_path: str
    edited_regions: tuple[tuple[float, float], ...]
    duration: float


def _finite_nonnegative(value: str, *, field: str, row_number: int) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: {field} is not numeric") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"row {row_number}: {field} must be finite and non-negative")
    return parsed


def parse_partialedit_csv(path: str | Path) -> tuple[PartialEditRecord, ...]:
    """Parse the official PartialEdit E1/E2 CSV without lossy conversion.

    Each row is ``audio_path, start, end, duration`` for one edited region,
    with additional start/end pairs inserted before the final duration for
    multi-region examples.
    """

    records: list[PartialEditRecord] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row_number, row in enumerate(csv.reader(handle), start=1):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) < 4 or len(row[1:]) % 2 != 1:
                raise ValueError(f"row {row_number}: expected path plus start/end pairs and duration")
            audio_path = row[0].strip().replace("\\", "/")
            if not audio_path or Path(audio_path).is_absolute():
                raise ValueError(f"row {row_number}: audio path must be relative and non-empty")
            duration = _finite_nonnegative(row[-1], field="duration", row_number=row_number)
            region_values = row[1:-1]
            regions: list[tuple[float, float]] = []
            for index in range(0, len(region_values), 2):
                start = _finite_nonnegative(region_values[index], field="start", row_number=row_number)
                end = _finite_nonnegative(region_values[index + 1], field="end", row_number=row_number)
                if not end > start or end > duration:
                    raise ValueError(f"row {row_number}: edited region is outside duration or empty")
                if regions and start < regions[-1][1]:
                    raise ValueError(f"row {row_number}: edited regions overlap or are unsorted")
                regions.append((start, end))
            records.append(PartialEditRecord(audio_path, tuple(regions), duration))
    if not records:
        raise ValueError("PartialEdit CSV contains no records")
    return tuple(records)


def parse_partialspoof_segment_labels(path: str | Path) -> dict[str, tuple[int, ...]]:
    """Validate one official PartialSpoof ``*_seglab_*.npy`` mapping."""

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("numpy is required to parse PartialSpoof segment labels") from exc

    loaded: Any = np.load(Path(path), allow_pickle=True)
    if getattr(loaded, "shape", None) != ():
        raise ValueError("PartialSpoof segment labels must contain one object mapping")
    mapping = loaded.item()
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("PartialSpoof segment labels must be a non-empty mapping")
    parsed: dict[str, tuple[int, ...]] = {}
    for key, values in mapping.items():
        if not isinstance(key, str) or not key:
            raise ValueError("PartialSpoof segment-label keys must be non-empty strings")
        array = np.asarray(values)
        if array.ndim != 1 or array.size == 0:
            raise ValueError(f"PartialSpoof key {key!r}: labels must be a non-empty vector")
        labels: list[int] = []
        for value in array.tolist():
            if str(value) not in {"0", "1"}:
                raise ValueError(f"PartialSpoof key {key!r}: labels must be binary 0/1")
            labels.append(int(value))
        parsed[key] = tuple(labels)
    return parsed


def summarize_partialedit(records: tuple[PartialEditRecord, ...]) -> dict[str, int]:
    """Return auditable counts without inspecting or changing model outputs."""

    return {
        "records": len(records),
        "edited_regions": sum(len(record.edited_regions) for record in records),
        "unique_audio_paths": len({record.audio_path for record in records}),
    }
