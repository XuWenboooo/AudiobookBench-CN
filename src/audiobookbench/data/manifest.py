from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

REQUIRED_COLUMNS: list[str] = [
    "audio_path",
    "sample_id",
    "pair_id",
    "source_sample_id",
    "source_type",
    "generator",
    "generator_family",
    "speaker",
    "text_id",
    "duration",
    "sample_rate",
    "segment_id",
    "segment_start",
    "segment_end",
    "position",
    "is_manipulated",
    "attack_type",
    "attack_start",
    "attack_end",
    "attack_generator",
    "source_generator",
    "replacement_speaker",
    "split",
]

REQUIRED_NON_EMPTY: set[str] = {
    "audio_path",
    "sample_id",
    "pair_id",
    "source_sample_id",
    "source_type",
    "generator",
    "generator_family",
    "speaker",
    "text_id",
    "duration",
    "sample_rate",
    "segment_id",
    "segment_start",
    "segment_end",
    "position",
    "is_manipulated",
    "split",
}

ALLOWED_SOURCE_TYPES = {"natural", "tts"}
ALLOWED_SPLITS = {"train", "val", "test"}

_EMPTY = {"", "none", "null", "nan", "na", "n/a"}


class ManifestValidationError(ValueError):
    """Raised when an AudiobookBench manifest violates the schema."""


def _row_label(record: Mapping[str, Any], row_index: int | None = None) -> str:
    sample_id = record.get("sample_id")
    prefix = f"row {row_index}" if row_index is not None else "record"
    if sample_id not in (None, ""):
        prefix += f" sample_id={sample_id!r}"
    return prefix


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _EMPTY
    return False


def normalize_bool(value: Any, *, field_name: str = "is_manipulated", row_index: int | None = None) -> bool:
    """Normalize common CSV/JSON boolean spellings."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
    where = f"row {row_index}: " if row_index is not None else ""
    raise ManifestValidationError(f"{where}{field_name} must be a boolean-like value, got {value!r}")


def parse_float(
    value: Any,
    field_name: str,
    row_index: int | None = None,
    *,
    allow_empty: bool = False,
) -> float | None:
    if _is_empty(value):
        if allow_empty:
            return None
        where = f"row {row_index}: " if row_index is not None else ""
        raise ManifestValidationError(f"{where}{field_name} is required")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        where = f"row {row_index}: " if row_index is not None else ""
        raise ManifestValidationError(f"{where}{field_name} must be numeric, got {value!r}") from exc


def parse_int(
    value: Any,
    field_name: str,
    row_index: int | None = None,
    *,
    allow_empty: bool = False,
) -> int | None:
    if _is_empty(value):
        if allow_empty:
            return None
        where = f"row {row_index}: " if row_index is not None else ""
        raise ManifestValidationError(f"{where}{field_name} is required")
    try:
        as_float = float(value)
    except (TypeError, ValueError) as exc:
        where = f"row {row_index}: " if row_index is not None else ""
        raise ManifestValidationError(f"{where}{field_name} must be an integer, got {value!r}") from exc
    if not as_float.is_integer():
        where = f"row {row_index}: " if row_index is not None else ""
        raise ManifestValidationError(f"{where}{field_name} must be an integer, got {value!r}")
    return int(as_float)


def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    """Load a manifest from CSV or JSONL without requiring pandas."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return [dict(row) for row in reader]

    if suffix in {".jsonl", ".ndjson"}:
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ManifestValidationError(f"line {idx}: JSONL item must be an object")
                records.append(obj)
        return records

    raise ValueError(f"Unsupported manifest format: {path.suffix}. Use .csv or .jsonl")


def save_manifest(records: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    """Save manifest records to CSV or JSONL."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [dict(record) for record in records]

    suffix = path.suffix.lower()
    if suffix == ".csv":
        fieldnames = list(REQUIRED_COLUMNS)
        extras = sorted({key for row in rows for key in row.keys()} - set(fieldnames))
        fieldnames.extend(extras)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return

    if suffix in {".jsonl", ".ndjson"}:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return

    raise ValueError(f"Unsupported manifest format: {path.suffix}. Use .csv or .jsonl")


def validate_manifest(records: Iterable[Mapping[str, Any]]) -> None:
    """Validate rows plus pair/source lineage integrity."""
    rows = list(records)
    if not rows:
        raise ManifestValidationError("manifest must contain at least one record")
    for row_index, record in enumerate(rows, start=1):
        validate_record(record, row_index=row_index)
    validate_pair_split_integrity(rows)
    validate_source_lineage(rows)


def validate_record(record: Mapping[str, Any], row_index: int | None = None) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in record]
    if missing_columns:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} missing required columns: {missing_columns}"
        )

    empty_required = [field for field in REQUIRED_NON_EMPTY if _is_empty(record.get(field))]
    if empty_required:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} has empty required fields: {sorted(empty_required)}"
        )

    source_type = str(record["source_type"]).strip().lower()
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}, got {record['source_type']!r}"
        )

    split = str(record["split"]).strip().lower()
    if split not in ALLOWED_SPLITS:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} split must be one of {sorted(ALLOWED_SPLITS)}, got {record['split']!r}"
        )

    is_manipulated = normalize_bool(record["is_manipulated"], row_index=row_index)

    duration = parse_float(record["duration"], "duration", row_index)
    sample_rate = parse_int(record["sample_rate"], "sample_rate", row_index)
    segment_start = parse_float(record["segment_start"], "segment_start", row_index)
    segment_end = parse_float(record["segment_end"], "segment_end", row_index)
    position = parse_int(record["position"], "position", row_index)

    assert duration is not None
    assert sample_rate is not None
    assert segment_start is not None
    assert segment_end is not None
    assert position is not None

    if duration <= 0:
        raise ManifestValidationError(f"{_row_label(record, row_index)} duration must be > 0")
    if sample_rate <= 0:
        raise ManifestValidationError(f"{_row_label(record, row_index)} sample_rate must be > 0")
    if position < 0:
        raise ManifestValidationError(f"{_row_label(record, row_index)} position must be >= 0")
    if segment_start >= segment_end:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} segment_start must be < segment_end"
        )
    if segment_start < 0:
        raise ManifestValidationError(f"{_row_label(record, row_index)} segment_start must be >= 0")
    if segment_end > duration:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} segment_end must be <= duration"
        )

    attack_start = parse_float(record.get("attack_start"), "attack_start", row_index, allow_empty=True)
    attack_end = parse_float(record.get("attack_end"), "attack_end", row_index, allow_empty=True)

    if is_manipulated:
        if _is_empty(record.get("attack_type")):
            raise ManifestValidationError(
                f"{_row_label(record, row_index)} manipulated rows require attack_type"
            )
        if attack_start is None or attack_end is None:
            raise ManifestValidationError(
                f"{_row_label(record, row_index)} manipulated rows require attack_start and attack_end"
            )
    elif (attack_start is None) ^ (attack_end is None):
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} attack_start and attack_end must be both present or both empty"
        )

    if attack_start is not None and attack_end is not None:
        if attack_start >= attack_end:
            raise ManifestValidationError(
                f"{_row_label(record, row_index)} attack_start must be < attack_end"
            )
        if attack_start < 0:
            raise ManifestValidationError(f"{_row_label(record, row_index)} attack_start must be >= 0")
        if attack_end > duration:
            raise ManifestValidationError(f"{_row_label(record, row_index)} attack_end must be <= duration")

    sample_id = str(record["sample_id"]).strip()
    source_sample_id = str(record["source_sample_id"]).strip()
    if not is_manipulated and source_sample_id != sample_id:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} clean rows must self-reference source_sample_id == sample_id"
        )
    if is_manipulated and source_sample_id == sample_id:
        raise ManifestValidationError(
            f"{_row_label(record, row_index)} manipulated rows must reference a distinct clean source_sample_id"
        )


def validate_pair_split_integrity(records: Iterable[Mapping[str, Any]]) -> None:
    """Ensure every pair_id is confined to exactly one split."""
    pair_splits: dict[str, set[str]] = {}
    for record in records:
        pair_id = str(record["pair_id"]).strip()
        split = str(record["split"]).strip().lower()
        pair_splits.setdefault(pair_id, set()).add(split)

    conflicts = {pair_id: splits for pair_id, splits in pair_splits.items() if len(splits) > 1}
    if conflicts:
        details = ", ".join(
            f"{pair_id!r} -> {sorted(splits)}" for pair_id, splits in sorted(conflicts.items())
        )
        raise ManifestValidationError(f"pair_id must not cross splits: {details}")


def validate_source_lineage(records: Iterable[Mapping[str, Any]]) -> None:
    """Validate source_sample_id lineage for clean/manipulated counterfactual pairs.

    Clean rows self-reference. Manipulated rows must point to an existing clean sample
    with the same pair_id and split. Multiple segment rows may share the same sample_id.
    """
    rows = list(records)
    clean_index: dict[str, list[Mapping[str, Any]]] = {}
    for record in rows:
        if not normalize_bool(record["is_manipulated"]):
            clean_index.setdefault(str(record["sample_id"]).strip(), []).append(record)

    for record in rows:
        if not normalize_bool(record["is_manipulated"]):
            continue
        source_sample_id = str(record["source_sample_id"]).strip()
        candidates = clean_index.get(source_sample_id, [])
        if not candidates:
            raise ManifestValidationError(
                f"record sample_id={record.get('sample_id')!r} references missing clean source_sample_id={source_sample_id!r}"
            )

        pair_id = str(record["pair_id"]).strip()
        split = str(record["split"]).strip().lower()
        if not any(
            str(candidate["pair_id"]).strip() == pair_id
            and str(candidate["split"]).strip().lower() == split
            for candidate in candidates
        ):
            raise ManifestValidationError(
                f"record sample_id={record.get('sample_id')!r} source_sample_id={source_sample_id!r} must reference a clean row with the same pair_id and split"
            )
