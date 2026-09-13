from __future__ import annotations

import numpy as np
from .detection import auprc, auroc, threshold_metrics
from ..schemas import Interval


def frame_labels(frame_supports, ground_truth: tuple[Interval, ...], *, overlap_threshold: float = 0.5) -> np.ndarray:
    supports = np.asarray(frame_supports, dtype=float)
    if supports.ndim != 2 or supports.shape[1] != 2 or len(supports) == 0 or not np.isfinite(supports).all():
        raise ValueError("frame supports must be a non-empty finite (n, 2) array")
    if not 0 <= overlap_threshold <= 1:
        raise ValueError("overlap_threshold must be in [0, 1]")
    if np.any(supports[:, 1] <= supports[:, 0]) or np.any(supports[1:, 0] < supports[:-1, 1]):
        raise ValueError("frame supports must be increasing and non-overlapping")
    labels = np.zeros(len(supports), dtype=int)
    for i, (start, end) in enumerate(supports):
        support = end - start
        for interval in ground_truth:
            overlap = max(0.0, min(end, interval.end_sec) - max(start, interval.start_sec))
            if overlap / support >= overlap_threshold:
                labels[i] = 1
                break
    return labels


def evaluate_frames(frame_supports, frame_scores, ground_truth: tuple[Interval, ...], *, threshold: float | None = None) -> dict[str, float]:
    supports = np.asarray(frame_supports, dtype=float)
    scores = np.asarray(frame_scores, dtype=float)
    labels = frame_labels(supports, ground_truth)
    if scores.ndim != 1 or len(scores) != len(labels) or not np.isfinite(scores).all():
        raise ValueError("frame scores must match supports and be finite")
    result = {"auroc": auroc(labels, scores), "auprc": auprc(labels, scores)}
    if threshold is not None:
        result.update(threshold_metrics(labels, scores, threshold))
    return result
