from __future__ import annotations

import numpy as np


def binary_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype(bool)
    y_pred = np.asarray(y_pred).astype(bool)
    tp = np.sum(y_true & y_pred)
    fp = np.sum(~y_true & y_pred)
    fn = np.sum(y_true & ~y_pred)
    denom = 2 * tp + fp + fn
    return float(2 * tp / denom) if denom else 0.0


def interval_iou(pred_start: float, pred_end: float, true_start: float, true_end: float) -> float:
    inter = max(0.0, min(pred_end, true_end) - max(pred_start, true_start))
    union = max(pred_end, true_end) - min(pred_start, true_start)
    return float(inter / union) if union > 0 else 0.0
