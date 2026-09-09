"""Day 6A lightweight localization metrics for the non-trained baseline.

Window-level AUROC / AUPRC / F1, split-aware and variant-aware. All metrics
return NaN (not 0) when undefined, e.g. when only one class is present in an
evaluation slice — a clean-only slice has no positive windows by design.
"""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from audiobookbench.evaluation.metrics import binary_f1


def auroc(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(scores, dtype=np.float64)
    mask = np.isfinite(s)
    y, s = y[mask], s[mask]
    if y.size == 0 or not y.any() or y.all():
        return float("nan")
    return float(roc_auc_score(y, s))


def auprc(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(scores, dtype=np.float64)
    mask = np.isfinite(s)
    y, s = y[mask], s[mask]
    if y.size == 0 or not y.any():
        return float("nan")
    return float(average_precision_score(y, s))


def f1_at_threshold(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> float:
    s = np.asarray(scores, dtype=np.float64)
    if not np.isfinite(s).any() or np.isnan(threshold):
        return float("nan")
    return binary_f1(y_true, s >= threshold)


def evaluate_windows(
    y_true: np.ndarray,
    scores: np.ndarray,
    threshold: float,
) -> dict[str, float]:
    return {
        "auroc": auroc(y_true, scores),
        "auprc": auprc(y_true, scores),
        "f1": f1_at_threshold(y_true, scores, threshold),
        "n_windows": int(np.asarray(y_true).size),
        "n_positive": int(np.asarray(y_true).astype(bool).sum()),
    }


def zone_statistics(
    scores: np.ndarray,
    zones: np.ndarray,
) -> dict[str, dict[str, float]]:
    """Mean/median anomaly score per zone; the boundary-shortcut audit."""
    out: dict[str, dict[str, float]] = {}
    s = np.asarray(scores, dtype=np.float64)
    for zone in ("outside", "boundary", "core"):
        mask = (zones == zone) & np.isfinite(s)
        values = s[mask]
        out[zone] = {
            "mean": float(np.mean(values)) if values.size else float("nan"),
            "median": float(np.median(values)) if values.size else float("nan"),
            "n": int(values.size),
        }
    return out


def metrics_key(**parts: Any) -> str:
    """Deterministic result key like ``250ms|a0|test|full|ALL``."""
    return "|".join(str(p) for p in parts.values())
