from __future__ import annotations

import numpy as np


def zscore_anomaly(values: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.full_like(values, np.nan, dtype=float)
    mu = float(np.mean(finite))
    sigma = float(np.std(finite)) + eps
    return np.abs((values - mu) / sigma)
