from __future__ import annotations

from typing import Callable
import numpy as np


def bootstrap_ci(values: np.ndarray, fn: Callable[[np.ndarray], float] = np.mean, n: int = 1000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n):
        sample = rng.choice(values, size=len(values), replace=True)
        stats.append(fn(sample))
    lo, hi = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)
