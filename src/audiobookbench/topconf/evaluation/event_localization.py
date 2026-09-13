from __future__ import annotations

import numpy as np
from ..schemas import Interval


def iou(pred: Interval, truth: Interval) -> float:
    intersection = max(0.0, min(pred.end_sec, truth.end_sec) - max(pred.start_sec, truth.start_sec))
    union = max(pred.end_sec, truth.end_sec) - min(pred.start_sec, truth.start_sec)
    return intersection / union if union > 0 else 0.0


def match_events(predictions: list[tuple[Interval, float]], truths: tuple[Interval, ...], threshold: float) -> tuple[int, int, int]:
    if not 0 <= threshold <= 1:
        raise ValueError("IoU threshold must be in [0, 1]")
    if any(not np.isfinite(score) for _, score in predictions):
        raise ValueError("prediction scores must be finite")
    used: set[int] = set()
    tp = 0
    for interval, _score in sorted(predictions, key=lambda item: (-item[1], item[0].start_sec, item[0].end_sec)):
        candidates = [(iou(interval, truth), index) for index, truth in enumerate(truths) if index not in used]
        if candidates:
            best_iou, best_index = max(candidates, key=lambda item: (item[0], -item[1]))
            if best_iou >= threshold:
                used.add(best_index)
                tp += 1
    return tp, len(predictions) - tp, len(truths) - tp


def event_f1(predictions: list[tuple[Interval, float]], truths: tuple[Interval, ...], threshold: float = 0.5) -> float:
    tp, fp, fn = match_events(predictions, truths, threshold)
    denominator = 2 * tp + fp + fn
    return 2 * tp / denominator if denominator else 0.0


def average_precision(predictions: list[tuple[Interval, float]], truths: tuple[Interval, ...], threshold: float = 0.5) -> float:
    if not truths:
        return 0.0 if predictions else 1.0
    if any(not np.isfinite(score) for _, score in predictions):
        raise ValueError("prediction scores must be finite")
    used: set[int] = set()
    ranked = sorted(predictions, key=lambda item: (-item[1], item[0].start_sec, item[0].end_sec))
    hits = 0
    precisions = []
    hit_flags = []
    for rank, (interval, _score) in enumerate(ranked, start=1):
        candidates = [(iou(interval, truth), index) for index, truth in enumerate(truths) if index not in used]
        if candidates:
            best, index = max(candidates, key=lambda item: (item[0], -item[1]))
            if best >= threshold:
                used.add(index)
                hits += 1
                hit_flags.append(True)
            else:
                hit_flags.append(False)
        else:
            hit_flags.append(False)
        precisions.append(hits / rank)
    return float(sum(p for p, hit in zip(precisions, hit_flags) if hit) / len(truths)) if hits else 0.0


def event_metrics(predictions: list[tuple[Interval, float]], truths: tuple[Interval, ...]) -> dict[str, float]:
    result = {f"ap@{int(t * 100):02d}": average_precision(predictions, truths, t) for t in (0.50, 0.75, 0.95)}
    result["map"] = float(np.mean(list(result.values())))
    result["event_f1"] = event_f1(predictions, truths, 0.5)
    return result
