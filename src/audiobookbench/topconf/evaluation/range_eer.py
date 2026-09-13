"""Pure RangeEER implementation following Zhang et al., Interspeech 2023.

The official PartialSpoof implementation is the reference, not a dependency:
this module implements its published range-duration FPR/FNR equations for a
partitioned timeline and selects the threshold minimizing |FPR-FNR|. Scores
use the TopConf convention (higher means spoof); callers can invert scores
explicitly when adapting an official lower-is-spoof output.
"""

from __future__ import annotations

import numpy as np
from ..schemas import Interval


def _overlap(a: Interval, b: Interval) -> float:
    return max(0.0, min(a.end_sec, b.end_sec) - max(a.start_sec, b.start_sec))


def range_rates(supports, scores, ground_truth: tuple[Interval, ...], threshold: float) -> tuple[float, float]:
    supports = np.asarray(supports, dtype=float)
    scores = np.asarray(scores, dtype=float)
    if supports.ndim != 2 or supports.shape[1] != 2 or len(supports) != len(scores) or len(scores) == 0:
        raise ValueError("supports and scores must be non-empty and aligned")
    if not np.isfinite(supports).all() or not np.isfinite(scores).all() or not np.isfinite(threshold):
        raise ValueError("supports, scores, and threshold must be finite")
    if np.any(supports[:, 1] <= supports[:, 0]) or np.any(supports[1:, 0] < supports[:-1, 1]):
        raise ValueError("supports must be increasing and non-overlapping")
    total = Interval(float(supports[0, 0]), float(supports[-1, 1]))
    gt = tuple(ground_truth)
    positive = sum(_overlap(interval, total) for interval in gt)
    negative = total.duration_sec - positive
    if positive <= 0 or negative <= 0:
        raise ValueError("RangeEER requires both positive and negative reference duration")
    fp = fn = 0.0
    for support, score in zip(supports, scores):
        interval = Interval(float(support[0]), float(support[1]))
        spoof = score >= threshold
        positive_overlap = sum(_overlap(interval, truth) for truth in gt)
        if spoof:
            fp += interval.duration_sec - positive_overlap
        else:
            fn += positive_overlap
    return float(fp / negative), float(fn / positive)


def range_eer(supports, scores, ground_truth: tuple[Interval, ...]) -> dict[str, float | str | int]:
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 1 or len(scores) == 0 or not np.isfinite(scores).all():
        raise ValueError("scores must be a non-empty finite 1-D array")
    thresholds = np.concatenate(([float(np.min(scores)) - 1e-12], np.unique(scores), [float(np.max(scores)) + 1e-12]))
    candidates = []
    for threshold in thresholds:
        fpr, fnr = range_rates(supports, scores, ground_truth, float(threshold))
        candidates.append((abs(fpr - fnr), fpr, fnr, float(threshold)))
    _gap, fpr, fnr, threshold = min(candidates, key=lambda row: (row[0], row[3]))
    return {"status": "ESTIMABLE", "eer": float((fpr + fnr) / 2), "fpr": fpr, "fnr": fnr, "threshold": threshold, "threshold_count": len(thresholds)}
