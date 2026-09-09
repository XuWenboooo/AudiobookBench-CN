from pathlib import Path
import json
import importlib.util
import inspect
import shutil
import numpy as np
import pytest

from audiobookbench.security.day8_detector_denylist import DetectorLeakageError, assert_detector_inputs_safe
from audiobookbench.security.week3_accounting import classify_failure, final_accounting_rows
from audiobookbench.security.week3_authorization import validate_authorization_artifact
from audiobookbench.security.week3_authorization import sha256_file
from audiobookbench.security import week3_pipeline as pipeline
from audiobookbench.security.week3_authorization import CANONICAL_SCHEMA, CANONICAL_EVIDENCE
from audiobookbench.security import week3_authorization as authorization


def _schema_available() -> bool:
    return importlib.util.find_spec("jsonschema") is not None

def test_detector_boundary_rejects_adversarial_metadata():
    for key in ("reference_audio", "reference_text", "generator", "split", "GT", "attack_start_sample", "lineage", "seed"):
        with pytest.raises(DetectorLeakageError):
            assert_detector_inputs_safe({key: "injected"})

def test_failure_classifier_is_not_all_transient():
    assert classify_failure(ValueError("invalid output waveform")) == "waveform_QA_failure"
    assert classify_failure(RuntimeError("checkpoint load failed")) == "model_load_failure"

def test_final_accounting_retains_all_planned_cases():
    rows = final_accounting_rows([{"paired_case_id": "paircase_0001"}, {"paired_case_id": "paircase_0002"}], [{"paired_case_id": "paircase_0001", "status": "SUCCESS"}])
    assert [r["status"] for r in rows] == ["SUCCESS", "NOT_EXECUTED"]

def test_authorization_missing_fails_closed(tmp_path: Path):
    with pytest.raises(RuntimeError):
        validate_authorization_artifact(tmp_path / "missing.json", {})

def test_inactive_template_is_not_an_active_artifact():
    template = Path("results/week3_stage_a_f5/authorization.template.json")
    with pytest.raises(RuntimeError, match="canonical"):
        validate_authorization_artifact(template, {})

def test_authorization_wrong_source_hash_fails_closed(tmp_path):
    expected = pipeline._source_paths(Path("."))
    artifact = tmp_path / "authorization.json"
    hashes = {key: sha256_file(path) for key, path in expected.items()}
    hashes["config"] = "0" * 64
    artifact.write_text(json.dumps({
        "protocol": "WEEK3_STAGE_A_F5", "scope": "FORMAL_23_CASE_GENERATION_AND_FROZEN_STAGE_A_EVALUATION",
        "READY_FOR_STAGE_A_EXECUTION": True, "review_date": "2099-01-01",
        "review_evidence": str(expected["review_evidence"]), "source_sha256": hashes,
        "run_id": "test_run", "invocation_id": "test_invocation", "output_root": "results/week3_stage_a_f5_runs/test_run",
        "rerun_classification": "INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL", "historical_run_namespace": "results/week3_stage_a_f5",
        "historical_run_excluded": True, "prior_results_observed": True,
        "scientific_parameters_changed_after_observation": False, "independent_review_sha256": "0" * 64,
        **{field: sha256_file(path) for field, path in CANONICAL_EVIDENCE.items()},
    }), encoding="utf-8")
    expected_error = "hash mismatch" if _schema_available() else "schema validator is unavailable"
    with pytest.raises(RuntimeError, match=expected_error):
        validate_authorization_artifact(artifact, expected)


def _valid_authorization(expected):
    hashes = {key: sha256_file(path) for key, path in expected.items()}
    return {
        "protocol": "WEEK3_STAGE_A_F5", "scope": "FORMAL_23_CASE_GENERATION_AND_FROZEN_STAGE_A_EVALUATION",
        "READY_FOR_STAGE_A_EXECUTION": True, "review_date": "2099-01-01",
        "review_evidence": str(expected["review_evidence"]), "source_sha256": hashes,
        "run_id": "test_run", "invocation_id": "test_invocation", "output_root": "results/week3_stage_a_f5_runs/test_run",
        "rerun_classification": "INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL", "historical_run_namespace": "results/week3_stage_a_f5",
        "historical_run_excluded": True, "prior_results_observed": True,
        "scientific_parameters_changed_after_observation": False, "independent_review_sha256": "0" * 64,
        **{field: sha256_file(path) for field, path in CANONICAL_EVIDENCE.items()},
    }


@pytest.mark.parametrize("field,value", [
    ("prior_results_observed", None), ("prior_results_observed", False),
    ("scientific_parameters_changed_after_observation", None),
    ("scientific_parameters_changed_after_observation", True),
    ("rerun_classification", "OTHER"),
])
def test_authorization_integrity_semantics_are_schema_enforced(tmp_path, field, value):
    expected = pipeline._source_paths(Path("."))
    artifact = _valid_authorization(expected)
    if value is None:
        artifact.pop(field)
    else:
        artifact[field] = value
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    expected_error = "JSON Schema" if _schema_available() else "schema validator is unavailable"
    with pytest.raises(RuntimeError, match=expected_error):
        validate_authorization_artifact(path, expected)


def test_schema_required_field_is_not_documentation_only(tmp_path):
    expected = pipeline._source_paths(Path("."))
    artifact = _valid_authorization(expected)
    artifact.pop("review_date")
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    expected_error = "JSON Schema" if _schema_available() else "schema validator is unavailable"
    with pytest.raises(RuntimeError, match=expected_error):
        validate_authorization_artifact(path, expected)


def test_valid_authorization_returns_validated_integrity_context(tmp_path):
    if not _schema_available():
        unavailable = tmp_path / "authorization.json"
        unavailable.write_text("{}", encoding="utf-8")
        with pytest.raises(RuntimeError, match="schema validator is unavailable"):
            validate_authorization_artifact(unavailable, {})
        return
    expected = pipeline._source_paths(Path("."))
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(_valid_authorization(expected)), encoding="utf-8")
    context = validate_authorization_artifact(path, expected)
    assert context["prior_results_observed"] is True
    assert context["scientific_parameters_changed_after_observation"] is False
    assert context["rerun_classification"] == "INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL"
    for field in CANONICAL_EVIDENCE:
        assert context[field] == sha256_file(CANONICAL_EVIDENCE[field])


@pytest.mark.parametrize("field,value", [
    ("scientific_integrity_adjudication_sha256", None),
    ("authorization_namespace_verification_sha256", None),
    ("scientific_integrity_adjudication_sha256", "0" * 64),
    ("authorization_namespace_verification_sha256", "0" * 64),
])
def test_canonical_evidence_hashes_are_required_and_recomputed(tmp_path, field, value):
    expected = pipeline._source_paths(Path("."))
    artifact = _valid_authorization(expected)
    if value is None:
        artifact.pop(field)
    else:
        artifact[field] = value
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    expected_error = "JSON Schema" if value is None else "canonical evidence hash mismatch"
    with pytest.raises(RuntimeError, match=expected_error):
        validate_authorization_artifact(path, expected)


@pytest.mark.parametrize("field", list(CANONICAL_EVIDENCE))
def test_canonical_evidence_file_tampering_fails_closed(tmp_path, monkeypatch, field):
    expected = pipeline._source_paths(Path("."))
    artifact = _valid_authorization(expected)
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    tampered = tmp_path / f"tampered_{field}.md"
    shutil.copyfile(CANONICAL_EVIDENCE[field], tampered)
    tampered.write_text(tampered.read_text(encoding="utf-8") + "\nTAMPERED\n", encoding="utf-8")
    monkeypatch.setattr(authorization, "CANONICAL_EVIDENCE", {**CANONICAL_EVIDENCE, field: tampered})
    with pytest.raises(RuntimeError, match="canonical evidence hash mismatch"):
        validate_authorization_artifact(path, expected)


def test_formal_validator_rejects_alternate_evidence_substitution(tmp_path):
    expected = pipeline._source_paths(Path("."))
    artifact = _valid_authorization(expected)
    alternate = tmp_path / "alternate_evidence.md"
    alternate.write_text("alternate evidence with a superficially valid shape", encoding="utf-8")
    artifact["scientific_integrity_adjudication_sha256"] = sha256_file(alternate)
    artifact["scientific_adjudication_path"] = str(alternate)
    artifact["evidence_root"] = str(tmp_path)
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    assert "scientific_adjudication_path" not in inspect.signature(validate_authorization_artifact).parameters
    assert "verification_path" not in inspect.signature(validate_authorization_artifact).parameters
    with pytest.raises(RuntimeError, match="canonical evidence hash mismatch"):
        validate_authorization_artifact(path, expected)


def test_malformed_canonical_schema_fails_closed(tmp_path, monkeypatch):
    if not _schema_available():
        pytest.skip("jsonschema unavailable; unavailable-validator path is covered above")
    expected = pipeline._source_paths(Path("."))
    artifact = tmp_path / "authorization.json"
    artifact.write_text(json.dumps(_valid_authorization(expected)), encoding="utf-8")
    malformed_schema = tmp_path / "schema.json"
    malformed_schema.write_text("{\"type\":}", encoding="utf-8")
    monkeypatch.setattr(authorization, "CANONICAL_SCHEMA", malformed_schema)
    with pytest.raises(RuntimeError, match="JSON Schema"):
        validate_authorization_artifact(artifact, expected)
