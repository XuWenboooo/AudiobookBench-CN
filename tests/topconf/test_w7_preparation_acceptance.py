from __future__ import annotations

import json
from pathlib import Path

import pytest

from audiobookbench.topconf.preparation.distribution_acceptance import validate_distribution_file, validate_distribution_manifest
from audiobookbench.topconf.preparation.temporal_gt_adapter import TemporalGTAdapterError, emit_canonical_case, normalize_ground_truth
from tests.topconf.fixtures.w7_preparation_fixtures import fixtures

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("name,case", list(fixtures().items()))
def test_synthetic_acceptance_fixture(name, case):
    manifest, expected_ready, expected_reasons = case
    report = validate_distribution_manifest(manifest)
    assert report["ready_candidate"] is expected_ready, name
    for reason in expected_reasons:
        assert reason in report["failure_reasons"], (name, report)


def test_acceptance_report_has_fail_closed_fields():
    report = validate_distribution_manifest({"distribution_id": "broken", "split": "eval", "records": "not-a-list"})
    assert report["ready_candidate"] is False
    assert "manifest_parsing_failure" in report["failure_reasons"]
    assert report["audio_identity_pass"] is False


def test_malformed_manifest_file_fails_closed(tmp_path: Path):
    path = tmp_path / "manifest.json"
    path.write_text("{", encoding="utf-8")
    report = validate_distribution_file(path)
    assert report["ready_candidate"] is False
    assert "manifest_parsing_failure" in report["failure_reasons"]


def test_output_report_is_json_serializable(tmp_path: Path):
    report = validate_distribution_manifest(fixtures()["PASS_COMPLETE"][0])
    path = tmp_path / "result.json"
    path.write_text(json.dumps(report, allow_nan=False), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8"))["ready_candidate"] is True


def test_acceptance_output_schema_is_valid():
    import jsonschema

    schema_path = REPO / "research_assurance/topconf/w7_preparation/distribution_acceptance/DISTRIBUTION_ACCEPTANCE_RESULT_V1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    report = validate_distribution_manifest(fixtures()["PASS_COMPLETE"][0])
    jsonschema.Draft202012Validator(schema).validate(report)


def test_gt_adapter_supports_all_required_synthetic_forms():
    assert normalize_ground_truth("intervals_sec", {"intervals": [{"start_sec": 1, "end_sec": 2}]}, duration_sec=4, sample_rate=16000)
    assert normalize_ground_truth("frame_labels", {"labels": [0, 1, 0, 0], "frame_duration_sec": 1}, duration_sec=4, sample_rate=16000)
    assert normalize_ground_truth("segment_labels", {"segments": [{"start_sec": 1, "end_sec": 2, "label": 1}]}, duration_sec=4, sample_rate=16000)
    assert normalize_ground_truth("sample_index_intervals", {"sample_rate": 16000, "intervals": [{"start_sample": 16000, "end_sample": 32000}]}, duration_sec=4, sample_rate=16000)


def test_gt_adapter_rejects_silent_correction_cases():
    with pytest.raises(TemporalGTAdapterError, match="SAMPLE_INDEX_OUT_OF_RANGE"):
        normalize_ground_truth("sample_index_intervals", {"sample_rate": 16000, "intervals": [{"start_sample": 0, "end_sample": 64001}]}, duration_sec=4, sample_rate=16000)
    with pytest.raises(TemporalGTAdapterError, match="FRAME_COUNT_MISMATCH"):
        normalize_ground_truth("frame_labels", {"labels": [0, 1], "frame_duration_sec": 2, "frame_count": 3}, duration_sec=4, sample_rate=16000)
    with pytest.raises(TemporalGTAdapterError, match="UNSUPPORTED_GT_REPRESENTATION"):
        normalize_ground_truth("invented", {}, duration_sec=4, sample_rate=16000)


def test_canonical_case_requires_identity_and_normalizes():
    case = emit_canonical_case({
        "distribution_id": "toy", "split": "eval", "audio_id": "a1", "audio_path": "audio/a1.wav",
        "duration": 2, "sample_rate": 16000, "gt_representation_type": "intervals_sec",
        "gt_payload": {"intervals": [{"start_sec": 0.5, "end_sec": 1.0}]},
        "source_identity": "source-1", "manipulation_identity": "m-1",
    })
    assert case.manipulated_intervals[0].end_sec == 1.0
    with pytest.raises(TemporalGTAdapterError, match="MISSING_IDENTITY"):
        emit_canonical_case({})
