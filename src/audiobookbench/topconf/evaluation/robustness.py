from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class RobustnessPoint:
    condition_strength: float
    detection_metric: float
    localization_metric: float
    detection_retention: float | None = None
    localization_retention: float | None = None


def build_point(condition_strength: float, detection_metric: float, localization_metric: float, *, clean_detection: float, clean_localization: float) -> RobustnessPoint:
    values = (condition_strength, detection_metric, localization_metric, clean_detection, clean_localization)
    if not np.isfinite(values).all() or clean_detection == 0 or clean_localization <= 0:
        raise ValueError("curve values must be finite; clean denominators must be valid")
    return RobustnessPoint(float(condition_strength), float(detection_metric), float(localization_metric), float(detection_metric / clean_detection), float(localization_metric / clean_localization))
