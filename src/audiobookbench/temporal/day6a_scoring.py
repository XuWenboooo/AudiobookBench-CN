"""Day 6A non-trained reference and B0 anomaly scoring.

Reference statistics come from TRAIN CLEAN windows only. Val/test clean and
all manipulated windows never participate in reference estimation.

B0 anomaly score (frozen in config):
    z_f(t) = |x_f(t) - median_train_clean_f| / (MAD_train_clean_f + eps)
    A(t)   = mean of the valid per-feature z-scores in the chosen ablation set

Invalid handling is explicit: a window feature that is NaN (e.g. f0_median in
an all-unvoiced window) yields a NaN z-score which is excluded from the mean
and counted in ``n_valid``; a window contributes a score only when at least
``min_valid_features`` features are valid. No weights are learned anywhere.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

import numpy as np


def compute_reference(
    window_features: Mapping[str, np.ndarray],
    feature_names: Iterable[str],
    eps: float = 1.0e-8,
) -> dict[str, dict[str, float]]:
    """Robust per-feature center (median) and scale (MAD) from TRAIN CLEAN.

    Zero-scale protection: a feature whose train-clean MAD is exactly zero
    (over half the reference windows share one value, e.g. pause_fraction at
    the 100 ms scale) is marked ``degenerate``; its z-scores are always NaN
    and it is excluded from every combination. Pure epsilon scaling would
    otherwise amplify tiny deviations to |z| ~ 1e8. A defensive ``z_cap`` is
    applied in :func:`robust_zscore` against near-degenerate scales.
    """
    ref: dict[str, dict[str, float]] = {}
    for name in feature_names:
        values = np.asarray(window_features[name], dtype=np.float64)
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            ref[name] = {"center": float("nan"), "scale": float("nan"), "n_train": 0, "degenerate": 1.0}
            continue
        center = float(np.median(finite))
        mad = float(np.median(np.abs(finite - center)))
        degenerate = 1.0 if mad == 0.0 else 0.0
        ref[name] = {"center": center, "scale": mad + eps, "n_train": int(finite.size), "degenerate": degenerate}
    return ref


def robust_zscore(
    values: np.ndarray,
    reference: Mapping[str, float],
    cap: float = 1.0e4,
) -> np.ndarray:
    """Absolute robust z-scores; NaN inputs stay NaN (excluded downstream).

    Degenerate references (zero train-clean MAD) yield all-NaN. A defensive
    cap bounds near-degenerate explosions without affecting ordinary ranges.
    """
    x = np.asarray(values, dtype=np.float64)
    center = float(reference["center"])
    scale = float(reference["scale"])
    degenerate = bool(reference.get("degenerate", 0.0))
    if degenerate or not np.isfinite(center) or not np.isfinite(scale) or scale <= 0:
        return np.full(x.shape, np.nan)
    z = np.abs(x - center) / scale
    return np.minimum(z, cap)


def feature_zscore_matrix(
    window_features: Mapping[str, np.ndarray],
    reference: Mapping[str, Mapping[str, float]],
    feature_names: Iterable[str],
    cap: float = 1.0e4,
) -> dict[str, np.ndarray]:
    return {
        name: robust_zscore(window_features[name], reference[name], cap=cap)
        for name in feature_names
    }


def combine_scores(
    z_matrix: Mapping[str, np.ndarray],
    channels: Mapping[str, Iterable[str]],
    ablation_channels: Iterable[str],
    *,
    per_channel: bool = False,
    min_valid_features: int = 1,
) -> dict[str, np.ndarray]:
    """Mean of valid |z| over the ablation feature set (B0 combination).

    With ``per_channel=True`` also returns one combined score per feature
    channel (A_f0, A_energy, ...). Windows with fewer than
    ``min_valid_features`` valid features get NaN instead of a fake score.
    """
    selected: list[str] = []
    for channel in ablation_channels:
        selected.extend(channels[channel])
    combined = _mean_valid([z_matrix[name] for name in selected], min_valid_features)
    out: dict[str, np.ndarray] = {"combined": combined, "n_valid_features": _n_valid(
        [z_matrix[name] for name in selected]
    )}
    if per_channel:
        for channel, names in channels.items():
            out[f"channel_{channel}"] = _mean_valid(
                [z_matrix[name] for name in names], min_valid_features
            )
    return out


def _mean_valid(arrays: list[np.ndarray], min_valid: int) -> np.ndarray:
    if not arrays:
        return np.full(1, np.nan)
    stack = np.vstack([np.asarray(a, dtype=np.float64) for a in arrays])
    with np.errstate(invalid="ignore"):
        valid_mask = np.isfinite(stack)
    n_valid = valid_mask.sum(axis=0)
    sums = np.where(valid_mask, stack, 0.0).sum(axis=0)
    result = np.full(stack.shape[1], np.nan)
    enough = n_valid >= min_valid
    result[enough] = sums[enough] / n_valid[enough]
    return result


def _n_valid(arrays: list[np.ndarray]) -> np.ndarray:
    stack = np.vstack([np.asarray(a, dtype=np.float64) for a in arrays])
    return np.isfinite(stack).sum(axis=0).astype(int)


def best_f1_threshold(y_true: np.ndarray, scores: np.ndarray, grid_size: int = 512) -> float:
    """Choose the score threshold maximizing F1 on TRAIN windows only.

    Deterministic sweep over a fixed quantile grid of the train score
    distribution; ties broken toward the higher threshold. Never call with
    val/test data.
    """
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(scores, dtype=np.float64)
    mask = np.isfinite(s)
    y, s = y[mask], s[mask]
    if y.size == 0 or not y.any() or y.all():
        return float("nan")  # undefined without both classes on train
    if s.size > grid_size:
        candidates = np.quantile(s, np.linspace(0.0, 1.0, grid_size))
    else:
        candidates = np.unique(s)
    best_tau, best_f1 = float(candidates[-1]) + 1e-9, -1.0
    for tau in candidates:
        pred = s >= tau
        tp = int(np.sum(y & pred))
        fp = int(np.sum(~y & pred))
        fn = int(np.sum(y & ~pred))
        denom = 2 * tp + fp + fn
        f1 = 2 * tp / denom if denom else 0.0
        if f1 > best_f1 + 1e-12:
            best_f1, best_tau = f1, float(tau)
    return best_tau
