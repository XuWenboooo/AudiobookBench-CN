"""Generic, fail-closed temporal ground-truth normalization for W7 preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping


class TemporalGTAdapterError(ValueError):
    """Structured adapter error; no silent correction is permitted."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TemporalInterval:
    start_sec: float
    end_sec: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.start_sec) or not math.isfinite(self.end_sec):
            raise TemporalGTAdapterError("NONFINITE_INTERVAL", "interval endpoints must be finite")
        if self.start_sec < 0 or self.end_sec <= self.start_sec:
            raise TemporalGTAdapterError("INVALID_INTERVAL", "interval requires 0 <= start < end")


@dataclass(frozen=True)
class CanonicalCase:
    distribution_id: str
    split: str
    audio_id: str
    audio_path: str
    duration_sec: float
    sample_rate: int
    gt_representation_type: str
    manipulated_intervals: tuple[TemporalInterval, ...]
    source_identity: str
    manipulation_identity: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    adapter_version: str = "topconf.w7.generic_temporal_gt_adapter.v1"


def _positive_number(value: Any, code: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise TemporalGTAdapterError(code, "value must be numeric") from exc
    if not math.isfinite(number) or number <= 0:
        raise TemporalGTAdapterError(code, "value must be finite and positive")
    return number


def _intervals_from_seconds(items: Any, duration_sec: float) -> tuple[TemporalInterval, ...]:
    if not isinstance(items, list):
        raise TemporalGTAdapterError("MALFORMED_GT", "intervals must be a list")
    intervals: list[TemporalInterval] = []
    for item in items:
        if not isinstance(item, Mapping) or "start_sec" not in item or "end_sec" not in item:
            raise TemporalGTAdapterError("MALFORMED_INTERVAL", "interval needs start_sec and end_sec")
        interval = TemporalInterval(float(item["start_sec"]), float(item["end_sec"]))
        if interval.end_sec > duration_sec:
            raise TemporalGTAdapterError("GT_OUT_OF_RANGE", "interval exceeds audio duration")
        intervals.append(interval)
    return tuple(intervals)


def normalize_ground_truth(
    representation_type: str,
    payload: Mapping[str, Any],
    *,
    duration_sec: float,
    sample_rate: int,
) -> tuple[TemporalInterval, ...]:
    """Normalize a supported GT form to half-open ``[start_sec, end_sec)`` intervals."""

    duration = _positive_number(duration_sec, "INVALID_DURATION")
    if not isinstance(payload, Mapping):
        raise TemporalGTAdapterError("MALFORMED_GT", "payload must be an object")
    if representation_type in {"intervals_sec", "json_interval_list", "csv_interval_list"}:
        return _intervals_from_seconds(payload.get("intervals"), duration)
    if representation_type in {"segment_labels", "manifest_segment_table"}:
        segments = payload.get("segments")
        if not isinstance(segments, list):
            raise TemporalGTAdapterError("MALFORMED_GT", "segments must be a list")
        intervals: list[TemporalInterval] = []
        for segment in segments:
            if not isinstance(segment, Mapping) or not {"start_sec", "end_sec", "label"}.issubset(segment):
                raise TemporalGTAdapterError("MALFORMED_SEGMENT", "segment needs start, end and label")
            if segment["label"] not in (0, 1, False, True):
                raise TemporalGTAdapterError("NONBINARY_LABEL", "segment label must be binary")
            if bool(segment["label"]):
                intervals.extend(_intervals_from_seconds([segment], duration))
        return tuple(intervals)
    if representation_type in {"frame_labels", "binary_frame_vector"}:
        labels = payload.get("labels")
        frame_duration = _positive_number(payload.get("frame_duration_sec"), "INVALID_FRAME_DURATION")
        if not isinstance(labels, list) or not labels:
            raise TemporalGTAdapterError("MALFORMED_FRAME_LABELS", "labels must be a non-empty list")
        if payload.get("frame_count") is not None and payload["frame_count"] != len(labels):
            raise TemporalGTAdapterError("FRAME_COUNT_MISMATCH", "declared frame_count differs from labels")
        if abs(len(labels) * frame_duration - duration) > 1e-6:
            raise TemporalGTAdapterError("FRAME_DURATION_MISMATCH", "frame support length differs from duration")
        intervals = []
        for index, label in enumerate(labels):
            if label not in (0, 1, False, True):
                raise TemporalGTAdapterError("NONBINARY_LABEL", "frame label must be binary")
            if bool(label):
                intervals.append(TemporalInterval(index * frame_duration, (index + 1) * frame_duration))
        return tuple(intervals)
    if representation_type == "sample_index_intervals":
        gt_rate = _positive_number(payload.get("sample_rate"), "INVALID_SAMPLE_RATE")
        if abs(gt_rate - int(sample_rate)) > 1e-9:
            raise TemporalGTAdapterError("SAMPLE_RATE_MISMATCH", "GT and audio sample rates differ")
        raw = payload.get("intervals")
        if not isinstance(raw, list):
            raise TemporalGTAdapterError("MALFORMED_SAMPLE_INTERVALS", "intervals must be a list")
        max_sample = int(round(duration * gt_rate))
        intervals = []
        for item in raw:
            if not isinstance(item, Mapping) or not isinstance(item.get("start_sample"), int) or not isinstance(item.get("end_sample"), int):
                raise TemporalGTAdapterError("MALFORMED_SAMPLE_INTERVAL", "sample interval needs integer bounds")
            start, end = item["start_sample"], item["end_sample"]
            if start < 0 or end <= start or end > max_sample:
                raise TemporalGTAdapterError("SAMPLE_INDEX_OUT_OF_RANGE", "sample interval is outside audio")
            intervals.append(TemporalInterval(start / gt_rate, end / gt_rate))
        return tuple(intervals)
    raise TemporalGTAdapterError("UNSUPPORTED_GT_REPRESENTATION", representation_type)


def emit_canonical_case(record: Mapping[str, Any], *, adapter_version: str = "topconf.w7.generic_temporal_gt_adapter.v1") -> CanonicalCase:
    """Validate identity and normalize one manifest record without repair."""

    required = ("distribution_id", "split", "audio_id", "audio_path", "duration", "sample_rate", "gt_representation_type", "gt_payload", "source_identity", "manipulation_identity")
    missing = [field for field in required if field not in record]
    if missing:
        raise TemporalGTAdapterError("MISSING_IDENTITY", f"missing fields: {missing}")
    values = [record[field] for field in ("distribution_id", "split", "audio_id", "audio_path", "source_identity", "manipulation_identity")]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise TemporalGTAdapterError("INVALID_IDENTITY", "identity fields must be non-empty strings")
    audio_path = record["audio_path"].replace("\\", "/")
    if audio_path.startswith("/") or ":" in audio_path.split("/", 1)[0]:
        raise TemporalGTAdapterError("ABSOLUTE_AUDIO_PATH", "audio path must be relative")
    duration = _positive_number(record["duration"], "INVALID_DURATION")
    try:
        sample_rate = int(record["sample_rate"])
    except (TypeError, ValueError) as exc:
        raise TemporalGTAdapterError("INVALID_SAMPLE_RATE", "sample_rate must be an integer") from exc
    if sample_rate <= 0:
        raise TemporalGTAdapterError("INVALID_SAMPLE_RATE", "sample_rate must be positive")
    intervals = normalize_ground_truth(record["gt_representation_type"], record["gt_payload"], duration_sec=duration, sample_rate=sample_rate)
    return CanonicalCase(
        distribution_id=record["distribution_id"],
        split=record["split"],
        audio_id=record["audio_id"],
        audio_path=audio_path,
        duration_sec=duration,
        sample_rate=sample_rate,
        gt_representation_type=record["gt_representation_type"],
        manipulated_intervals=intervals,
        source_identity=record["source_identity"],
        manipulation_identity=record["manipulation_identity"],
        metadata=dict(record.get("metadata", {})),
        adapter_version=adapter_version,
    )
