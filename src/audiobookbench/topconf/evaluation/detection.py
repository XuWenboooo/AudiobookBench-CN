from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve


def _binary_inputs(labels, scores):
    y = np.asarray(labels, dtype=int)
    s = np.asarray(scores, dtype=float)
    if y.ndim != 1 or s.ndim != 1 or len(y) != len(s) or len(y) == 0:
        raise ValueError("labels and scores must be non-empty 1-D arrays of equal length")
    if not np.isin(y, [0, 1]).all() or not np.isfinite(s).all():
        raise ValueError("labels must be binary and scores finite")
    if np.unique(y).size < 2:
        raise ValueError("metric is undefined when labels contain one class")
    return y, s


def auroc(labels, scores) -> float:
    y, s = _binary_inputs(labels, scores)
    return float(roc_auc_score(y, s))


def auprc(labels, scores) -> float:
    y, s = _binary_inputs(labels, scores)
    return float(average_precision_score(y, s))


def eer(labels, scores) -> float:
    y, s = _binary_inputs(labels, scores)
    fpr, tpr, _ = roc_curve(y, s)
    fnr = 1.0 - tpr
    if np.any((fpr == 0.0) & (fnr == 0.0)):
        return 0.0
    crossing = np.where(np.diff(np.sign(fpr - fnr)) != 0)[0]
    if len(crossing) == 0:
        return float((fpr[np.argmin(np.abs(fpr - fnr))] + fnr[np.argmin(np.abs(fpr - fnr))]) / 2)
    i = int(crossing[0])
    return float((fpr[i] + fnr[i]) / 2)


def threshold_metrics(labels, scores, threshold: float) -> dict[str, float]:
    y, s = _binary_inputs(labels, scores)
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite")
    pred = s >= threshold
    tp, fp, fn = np.sum((y == 1) & pred), np.sum((y == 0) & pred), np.sum((y == 1) & ~pred)
    tn = np.sum((y == 0) & ~pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": float(precision), "recall": float(recall), "f1": float(f1), "fpr": float(fpr)}


def pool_localization(scores, method: str = "mean", *, top_k: int | None = None) -> float:
    values = np.asarray(scores, dtype=float)
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError("localization scores must be a non-empty finite 1-D array")
    if method == "max_pool":
        return float(np.max(values))
    if method == "mean_pool":
        return float(np.mean(values))
    if method == "top_k_mean":
        if top_k is None or not 1 <= top_k <= len(values):
            raise ValueError("top_k must be in [1, n] for top_k_mean")
        return float(np.mean(np.sort(values)[-top_k:]))
    raise ValueError(f"unknown pooling method: {method}")
