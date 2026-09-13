from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
import math


class SchemaValidationError(ValueError):
    """Raised when a TopConf prediction contract is invalid."""


def _finite(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise SchemaValidationError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise SchemaValidationError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class Interval:
    start_sec: float
    end_sec: float

    def __post_init__(self) -> None:
        start = _finite(self.start_sec, "interval.start_sec")
        end = _finite(self.end_sec, "interval.end_sec")
        if start < 0 or end <= start:
            raise SchemaValidationError("interval requires 0 <= start_sec < end_sec")

    @property
    def duration_sec(self) -> float:
        return self.end_sec - self.start_sec


@dataclass(frozen=True)
class PredictionRecord:
    """Canonical case-level output; absent optional outputs stay absent."""

    case_id: str
    dataset_id: str
    split_id: str
    mechanism_id: str
    audio_duration_sec: float
    ground_truth_intervals: tuple[Interval, ...]
    speaker_id_if_available: str | None = None
    utterance_score_optional: float | None = None
    frame_times_sec_optional: tuple[tuple[float, float], ...] | None = None
    frame_scores_optional: tuple[float, ...] | None = None
    predicted_intervals_optional: tuple[Interval, ...] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(isinstance(x, str) and x.strip() for x in (self.case_id, self.dataset_id, self.split_id, self.mechanism_id)):
            raise SchemaValidationError("case/dataset/split/mechanism identifiers must be non-empty strings")
        duration = _finite(self.audio_duration_sec, "audio_duration_sec")
        if duration <= 0:
            raise SchemaValidationError("audio_duration_sec must be positive")
        for interval in self.ground_truth_intervals:
            self._check_interval(interval, duration, "ground_truth")
        if self.utterance_score_optional is not None:
            _finite(self.utterance_score_optional, "utterance_score_optional")
        times = self.frame_times_sec_optional
        scores = self.frame_scores_optional
        if (times is None) != (scores is None):
            raise SchemaValidationError("frame_times and frame_scores must be supplied together")
        if times is not None and scores is not None:
            if len(times) != len(scores):
                raise SchemaValidationError("frame_times and frame_scores lengths differ")
            previous_end = -math.inf
            for index, pair in enumerate(times):
                if len(pair) != 2:
                    raise SchemaValidationError(f"frame_times[{index}] must be (start_sec, end_sec)")
                start, end = _finite(pair[0], f"frame_times[{index}].start"), _finite(pair[1], f"frame_times[{index}].end")
                if start < 0 or end <= start or end > duration or start < previous_end:
                    raise SchemaValidationError("frame supports must be finite, in-duration, and monotonic")
                previous_end = end
                _finite(scores[index], f"frame_scores[{index}]")
        if self.predicted_intervals_optional is not None:
            for interval in self.predicted_intervals_optional:
                self._check_interval(interval, duration, "prediction")

    @staticmethod
    def _check_interval(interval: Interval, duration: float, label: str) -> None:
        if not isinstance(interval, Interval) or interval.end_sec > duration:
            raise SchemaValidationError(f"{label} interval is outside audio duration")


def validate_unique_case_ids(records: Sequence[PredictionRecord]) -> None:
    ids = [record.case_id for record in records]
    if len(ids) != len(set(ids)):
        raise SchemaValidationError("duplicate case IDs")
