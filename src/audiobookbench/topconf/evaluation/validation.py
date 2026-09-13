from __future__ import annotations

import numpy as np
from ..schemas import PredictionRecord, validate_unique_case_ids


def validate_prediction_records(records: list[PredictionRecord]) -> None:
    """Validate contract records before any aggregation; never repair inputs."""
    validate_unique_case_ids(records)
    for record in records:
        if record.frame_scores_optional is not None and not np.isfinite(record.frame_scores_optional).all():
            raise ValueError(f"non-finite frame score in case {record.case_id}")
