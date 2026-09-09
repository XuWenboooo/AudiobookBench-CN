"""A2 reporting helpers that preserve the manipulated timeline convention."""
from __future__ import annotations

import numpy as np


def clean_prefix_for_manipulated_axis(times: np.ndarray, values: np.ndarray,
                                      attack_start_sample: int, sample_rate: int = 16000) -> tuple[np.ndarray, np.ndarray]:
    """Clip a clean trajectory at the A2 attack start before a manipulated-axis plot.

    A clean suffix must never be overlaid after the manipulated timeline shifts
    by the variable synthetic duration. Scores are unchanged; this is strictly
    a reporting-time coordinate guard.
    """
    t = np.asarray(times, dtype=float)
    v = np.asarray(values)
    if t.shape != v.shape:
        raise ValueError("times and values must have identical shape")
    return t[t <= attack_start_sample / sample_rate], v[t <= attack_start_sample / sample_rate]
