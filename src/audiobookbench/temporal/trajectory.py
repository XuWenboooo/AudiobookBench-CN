from __future__ import annotations

import numpy as np


def delta_from_reference(values: np.ndarray, reference_index: int = 0) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return values
    return values - values[reference_index]


def trajectory_summary(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "slope": float("nan"), "max_deviation": float("nan")}
    x = np.arange(len(values), dtype=float)
    mask = np.isfinite(values)
    slope = float(np.polyfit(x[mask], values[mask], 1)[0]) if mask.sum() >= 2 else float("nan")
    return {
        "mean": float(np.mean(finite)),
        "std": float(np.std(finite)),
        "slope": slope,
        "max_deviation": float(np.max(np.abs(finite - finite[0]))),
    }
