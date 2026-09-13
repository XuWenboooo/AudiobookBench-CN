from __future__ import annotations

import numpy as np
from ..schemas import Interval


def boundary_errors(prediction: Interval, truth: Interval) -> dict[str, float]:
    return {"onset_error_sec": float(prediction.start_sec - truth.start_sec), "offset_error_sec": float(prediction.end_sec - truth.end_sec)}


def false_positive_duration_per_hour(predictions: tuple[Interval, ...], truths: tuple[Interval, ...], duration_sec: float) -> float:
    if not np.isfinite(duration_sec) or duration_sec <= 0:
        raise ValueError("duration_sec must be positive and finite")
    # Union predicted time not covered by any GT; denominator is audio hours.
    def union(intervals: tuple[Interval, ...]) -> list[Interval]:
        merged: list[Interval] = []
        for current in sorted(intervals, key=lambda item: (item.start_sec, item.end_sec)):
            if merged and current.start_sec <= merged[-1].end_sec:
                merged[-1] = Interval(merged[-1].start_sec, max(merged[-1].end_sec, current.end_sec))
            else:
                merged.append(current)
        return merged

    predicted_union, truth_union = union(predictions), union(truths)
    fp = 0.0
    for pred in predicted_union:
        covered = sum(max(0.0, min(pred.end_sec, gt.end_sec) - max(pred.start_sec, gt.start_sec)) for gt in truth_union)
        fp += max(0.0, pred.duration_sec - min(pred.duration_sec, covered))
    return float(fp / (duration_sec / 3600.0))
