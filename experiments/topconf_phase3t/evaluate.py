from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from audiobookbench.topconf.datasets.external_parsers import parse_partialedit_csv
from audiobookbench.topconf.evaluation.detection import auprc, auroc
from audiobookbench.topconf.evaluation.frame_localization import frame_labels
from audiobookbench.topconf.evaluation.validation import validate_prediction_records
from audiobookbench.topconf.schemas import Interval, PredictionRecord

try:  # Supports both package imports in tests and direct script execution.
    from .common import DATASET_ID, read_jsonl, sha256_file, to_jsonable
except ImportError:  # pragma: no cover - exercised by the command-line entry point
    from common import DATASET_ID, read_jsonl, sha256_file, to_jsonable


def _ground_truth(csv_path: Path) -> dict[str, tuple[float, tuple[Interval, ...]]]:
    records = parse_partialedit_csv(csv_path)
    result: dict[str, tuple[float, tuple[Interval, ...]]] = {}
    for record in records:
        case_id = record.audio_path.replace("\\", "/")
        if not case_id.startswith("E1/"):
            continue
        result[case_id] = (record.duration, tuple(Interval(float(start), float(end)) for start, end in record.edited_regions))
    return result


def evaluate(canonical_path: Path, csv_path: Path, output_path: Path) -> dict[str, Any]:
    gt = _ground_truth(csv_path)
    grouped: dict[str, list[PredictionRecord]] = defaultdict(list)
    for raw in read_jsonl(canonical_path):
        case_id = raw.get("case_id")
        if case_id not in gt:
            raise ValueError(f"canonical case is absent from authorized E1 annotations: {case_id}")
        duration_csv, intervals = gt[case_id]
        duration = float(raw["duration_sec"])
        if abs(duration - duration_csv) > 1e-5:
            raise ValueError(f"{case_id}: raw duration differs from annotation duration")
        supports = tuple(tuple(float(v) for v in pair) for pair in raw["frame_times_sec"])
        scores = tuple(float(v) for v in raw["frame_scores"])
        prediction = PredictionRecord(
            case_id=case_id,
            dataset_id=DATASET_ID,
            split_id="E1",
            mechanism_id="VoiceCraft_partial_edit",
            audio_duration_sec=duration,
            ground_truth_intervals=intervals,
            frame_times_sec_optional=supports,
            frame_scores_optional=scores,
            metadata={"representation_id": raw["representation_id"], "gt_access_stage": "T4"},
        )
        grouped[str(raw["representation_id"])].append(prediction)

    rows: list[dict[str, Any]] = []
    for representation_id in sorted(grouped):
        predictions = grouped[representation_id]
        validate_prediction_records(predictions)
        labels: list[int] = []
        scores: list[float] = []
        cases = 0
        for prediction in predictions:
            supports = np.asarray(prediction.frame_times_sec_optional, dtype=float)
            values = np.asarray(prediction.frame_scores_optional, dtype=float)
            labels.extend(frame_labels(supports, prediction.ground_truth_intervals, overlap_threshold=0.5).tolist())
            scores.extend(values.tolist())
            cases += 1
        y = np.asarray(labels, dtype=int)
        s = np.asarray(scores, dtype=float)
        rows.append({
            "representation_id": representation_id,
            "metric_role": "LEVEL1_DESCRIPTIVE_DIAGNOSTIC",
            "gt_access_stage": "T4_EVALUATION_ONLY",
            "target_policy": "edited-region overlap fraction >= 0.5 of native support",
            "cases": cases,
            "frames": int(len(y)),
            "positive_frames": int(y.sum()),
            "auroc": auroc(y, s),
            "auprc": auprc(y, s),
            "winner_selected": False,
        })
    if not rows:
        raise ValueError("no canonical records were available for evaluation")
    result = {
        "dataset_id": DATASET_ID,
        "csv_sha256": sha256_file(csv_path),
        "canonical_file": str(canonical_path),
        "canonical_file_sha256": sha256_file(canonical_path),
        "metric_policy": "preauthorized frame AUROC/AUPRC only; Level-1 descriptive diagnostics",
        "threshold_metrics": False,
        "range_eer": False,
        "ld_dr95": False,
        "whether_a": "DEFERRED",
        "whether_b": "NOT_RUN",
        "rq1": "NOT_RUN",
        "representations": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(to_jsonable(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute authorized Phase3T Level-1 frame diagnostics")
    parser.add_argument("--canonical", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.canonical, args.csv, args.output), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
