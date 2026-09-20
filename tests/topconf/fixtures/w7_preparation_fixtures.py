from __future__ import annotations

import math


def _record(**updates):
    record = {
        "audio_id": "audio-001",
        "audio_path": "synthetic/audio-001.wav",
        "gt_id": "gt-001",
        "gt_representation_type": "intervals_sec",
        "gt_payload": {"intervals": [{"start_sec": 1.0, "end_sec": 2.0}]},
        "duration": 4.0,
        "sample_rate": 16000,
        "source_identity": "synthetic-source-001",
        "manipulation_identity": "synthetic-manipulation-001",
        "audio_present": True,
        "gt_present": True,
        "audio_metadata": {"readable": True, "duration_sec": 4.0, "sample_count": 64000},
        "identity_candidates": ["synthetic-source-001"],
        "split": "eval",
        "license_provenance": {"license_status": "PASS", "provenance_status": "PASS"},
    }
    record.update(updates)
    return record


def _manifest(*records, **updates):
    manifest = {
        "distribution_id": "SYNTHETIC_W7_ACCEPTANCE",
        "split": "eval",
        "license_status": "PASS",
        "provenance_status": "PASS",
        "records": list(records),
    }
    manifest.update(updates)
    return manifest


def fixtures():
    base = _record()
    return {
        "PASS_COMPLETE": (_manifest(base), True, []),
        "FAIL_MISSING_AUDIO": (_manifest(_record(audio_present=False)), False, ["missing_audio_ids"]),
        "FAIL_MISSING_GT": (_manifest(_record(gt_present=False)), False, ["missing_gt_ids"]),
        "FAIL_DUPLICATE_AUDIO_ID": (_manifest(base, _record(gt_id="gt-002")), False, ["duplicate_audio_ids"]),
        "FAIL_DUPLICATE_GT_ID": (_manifest(base, _record(audio_id="audio-002", audio_path="synthetic/audio-002.wav")), False, ["duplicate_gt_ids"]),
        "FAIL_NEGATIVE_TIMESTAMP": (_manifest(_record(gt_payload={"intervals": [{"start_sec": -1.0, "end_sec": 1.0}]})), False, ["invalid_intervals"]),
        "FAIL_END_AFTER_DURATION": (_manifest(_record(gt_payload={"intervals": [{"start_sec": 1.0, "end_sec": 5.0}]})), False, ["invalid_intervals"]),
        "FAIL_START_AFTER_END": (_manifest(_record(gt_payload={"intervals": [{"start_sec": 3.0, "end_sec": 2.0}]})), False, ["invalid_intervals"]),
        "FAIL_EMPTY_GT": (_manifest(_record(gt_payload={"intervals": []})), False, ["empty_manipulated_regions"]),
        "FAIL_NAN_TIMESTAMP": (_manifest(_record(gt_payload={"intervals": [{"start_sec": math.nan, "end_sec": 2.0}]})), False, ["invalid_intervals"]),
        "FAIL_INF_TIMESTAMP": (_manifest(_record(gt_payload={"intervals": [{"start_sec": 1.0, "end_sec": math.inf}]})), False, ["invalid_intervals"]),
        "FAIL_DURATION_MISMATCH": (_manifest(_record(audio_metadata={"readable": True, "duration_sec": 5.0, "sample_count": 64000})), False, ["duration_mismatches"]),
        "FAIL_SPLIT_COLLISION": (_manifest(_record(split="train")), False, ["split_conflicts"]),
        "FAIL_IDENTITY_AMBIGUITY": (_manifest(_record(identity_candidates=["source-a", "source-b"])), False, ["identity_ambiguities"]),
        "FAIL_FRAME_LENGTH_MISMATCH": (_manifest(_record(gt_representation_type="frame_labels", gt_payload={"labels": [0, 1], "frame_duration_sec": 2.0, "frame_count": 3})), False, ["frame_count_mismatches"]),
        "FAIL_SAMPLE_INDEX_OUT_OF_RANGE": (_manifest(_record(gt_representation_type="sample_index_intervals", gt_payload={"sample_rate": 16000, "intervals": [{"start_sample": 1000, "end_sample": 70000}]})), False, ["invalid_intervals"]),
    }


def fixture_names():
    return tuple(fixtures())
