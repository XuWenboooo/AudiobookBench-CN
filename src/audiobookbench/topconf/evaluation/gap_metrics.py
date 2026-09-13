from __future__ import annotations

import numpy as np
from .robustness import RobustnessPoint


def ld_at_dr95(points: list[RobustnessPoint], *, retention: float = 0.95) -> dict[str, float | str | int]:
    """Candidate LD@DR95: 1 - mean localization retention over feasible points.

    Feasibility is condition-level and paired to a clean reference. An empty
    feasible set is explicitly NOT_ESTIMABLE, never zero.
    """
    if not 0 < retention <= 1 or not points:
        raise ValueError("retention must be in (0,1] and points non-empty")
    feasible = [p for p in points if p.detection_retention is not None and p.detection_retention >= retention]
    if not feasible:
        return {"status": "NOT_ESTIMABLE", "feasible_count": 0}
    localizations = np.asarray([p.localization_retention for p in feasible], dtype=float)
    if not np.isfinite(localizations).all():
        raise ValueError("localization retentions must be finite")
    return {"status": "ESTIMABLE", "feasible_count": len(feasible), "ld_at_dr95": float(1.0 - np.mean(localizations)), "mean_localization_retention": float(np.mean(localizations)), "worst_localization_retention": float(np.min(localizations))}
