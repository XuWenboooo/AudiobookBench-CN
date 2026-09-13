from __future__ import annotations

import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

from audiobookbench.security.week4_authorization import (
    CANONICAL_SOURCES,
    Week4AuthorizationError,
    sha256_file,
    validate_authorization_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEMPLATE = ROOT / "results/week4_adaptive_redteam/authorization.template.json"


def active_artifact(invocation_id: str = "TEST_ONLY_preflight_20260911", stage: str = "validation") -> dict[str, object]:
    artifact = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    artifact.update({
        "authorization_status": "ACTIVE",
        "ready": True,
        "READY_FOR_WEEK4_EXECUTION": True,
        "READY_FOR_STAGE_EXECUTION": True,
        "run_id": "week4_adaptive_redteam_v0",
        "stage": stage,
        "stage_authorization": stage,
        "invocation_id": invocation_id,
        "output_namespace": f"results/week4_adaptive_redteam_runs/{invocation_id}",
        "issued_at": "2026-09-11T00:00:00Z",
    })
    hashes = {name: sha256_file(path) for name, path in CANONICAL_SOURCES.items()}
    artifact["source_sha256"] = hashes
    artifact.update({
        "preregistration_sha256": hashes["preregistration"],
        "canonical_config_sha256": hashes["canonical_config"],
        "population_manifest_sha256": hashes["population_manifest"],
        "controller_sha256": hashes["controller"],
        "search_implementation_sha256": hashes["search_implementation"],
        "formal_runner_sha256": hashes["formal_runner"],
        "f5_qualification_sha256": hashes["f5_qualification"],
        "execution_supplement_sha256": hashes["execution_supplement"],
        "execution_supplement_config_sha256": hashes["execution_supplement_config"],
        "d0_asset_manifest_sha256": hashes["d0_asset_manifest"],
        "execution_source_manifest_sha256": hashes["execution_source_manifest"],
        "f5_frozen_source_manifest_sha256": hashes["f5_frozen_source_manifest"],
        "formal_runtime_environment_manifest_sha256": hashes["formal_runtime_environment_manifest"],
        "execution_governance_amendment_v2_sha256": hashes["execution_governance_amendment_v2"],
        "partial_dev_invalidation_sha256": hashes["partial_dev_invalidation"],
        "dev03_postrun_integrity_review_sha256": hashes["dev03_postrun_integrity_review"],
        "POST_DEV_GOVERNANCE_AMENDMENT_SHA256": hashes["execution_governance_amendment_v2"],
    })
    return artifact


def write_artifact(tmp_path: Path, artifact: dict[str, object]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_inactive_template_is_schema_valid_but_cannot_authorize():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "authorization.json"
        path.write_bytes(TEMPLATE.read_bytes())
        with pytest.raises(Week4AuthorizationError, match="not active"):
            validate_authorization_artifact(path)


def test_authorization_discloses_week1_3_and_prior_week4_outcome_history(tmp_path: Path):
    artifact = active_artifact()
    assert artifact["week1_3_scientific_results_already_observed"] is True
    assert artifact["week4_scientific_results_observed_before_authorization"] is True
    assert artifact["PRIOR_PARTIAL_RUNS_SCIENTIFICALLY_ADMISSIBLE"] is False
    assert artifact["EXECUTION_GOVERNANCE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is True
    artifact["week4_scientific_results_observed_before_authorization"] = False
    with pytest.raises(Week4AuthorizationError, match="canonical JSON Schema validation"):
        validate_authorization_artifact(write_artifact(tmp_path, artifact))


def test_missing_week4_outcome_disclosure_fails_canonical_schema(tmp_path: Path):
    artifact = active_artifact()
    artifact.pop("week4_scientific_results_observed_before_authorization")
    with pytest.raises(Week4AuthorizationError, match="canonical JSON Schema validation"):
        validate_authorization_artifact(write_artifact(tmp_path, artifact))


@pytest.mark.parametrize("field", [
    "preregistration_sha256", "canonical_config_sha256", "population_manifest_sha256",
    "controller_sha256", "search_implementation_sha256", "formal_runner_sha256", "f5_qualification_sha256",
    "execution_supplement_sha256", "execution_supplement_config_sha256", "d0_asset_manifest_sha256", "execution_source_manifest_sha256",
    "f5_frozen_source_manifest_sha256", "formal_runtime_environment_manifest_sha256", "execution_governance_amendment_v2_sha256", "partial_dev_invalidation_sha256", "dev03_postrun_integrity_review_sha256",
])
def test_missing_malformed_and_mismatched_hashes_fail_closed(tmp_path: Path, field: str):
    valid = active_artifact()
    missing = copy.deepcopy(valid)
    missing.pop(field)
    with pytest.raises(Week4AuthorizationError, match="canonical JSON Schema validation"):
        validate_authorization_artifact(write_artifact(tmp_path / "missing", missing))
    malformed = copy.deepcopy(valid)
    malformed[field] = "not-a-sha256"
    with pytest.raises(Week4AuthorizationError, match="canonical JSON Schema validation"):
        validate_authorization_artifact(write_artifact(tmp_path / "malformed", malformed))
    mismatched = copy.deepcopy(valid)
    mismatched[field] = "0" * 64
    with pytest.raises(Week4AuthorizationError, match="canonical hash mismatch"):
        validate_authorization_artifact(write_artifact(tmp_path / "mismatched", mismatched))


def test_post_dev_governance_amendment_hash_is_required_and_current(tmp_path: Path):
    valid = active_artifact()
    missing = copy.deepcopy(valid)
    missing.pop("POST_DEV_GOVERNANCE_AMENDMENT_SHA256")
    with pytest.raises(Week4AuthorizationError, match="canonical JSON Schema validation"):
        validate_authorization_artifact(write_artifact(tmp_path / "missing", missing))
    mismatched = copy.deepcopy(valid)
    mismatched["POST_DEV_GOVERNANCE_AMENDMENT_SHA256"] = "0" * 64
    with pytest.raises(Week4AuthorizationError, match="does not bind the frozen post-DEV governance amendment"):
        validate_authorization_artifact(write_artifact(tmp_path / "mismatched", mismatched))


def test_valid_authorization_and_preflight_are_read_only(tmp_path: Path):
    formal_run = importlib.import_module("experiments.week4_adaptive_red_team.formal_run")
    invocation_id = "TEST_ONLY_preflight_20260911"
    artifact_path = write_artifact(tmp_path, active_artifact(invocation_id))
    output = ROOT / "results/week4_adaptive_redteam_runs" / invocation_id
    assert not output.exists()
    context = formal_run.preflight(config=ROOT / "configs/week4_adaptive_red_team.yaml", population=ROOT / "data/manifests/week4_population_manifest.json", authorization=artifact_path, runtime_root=output, stage="validation")
    assert context["status"] == "PASS"
    assert context["generation_invoked"] is False and context["d0_invoked"] is False and context["evaluator_invoked"] is False
    assert context["accounting_initialization_safe"] is True and context["accounting_initialized"] is False
    assert context["scientific_execution_enabled"] is False
    assert context["runtime_permitted_by_external_authorization"] is True
    assert not output.exists()


def test_validation_authorization_cannot_preflight_heldout_and_heldout_needs_freeze(tmp_path: Path):
    validation = write_artifact(tmp_path / "validation", active_artifact("TEST_ONLY_validation", "validation"))
    with pytest.raises(Week4AuthorizationError, match="stage does not match"):
        validate_authorization_artifact(validation, expected_stage="held_out")
    heldout = active_artifact("TEST_ONLY_heldout", "held_out")
    heldout["source_sha256"]["post_validation_a0_freeze"] = "0" * 64  # type: ignore[index]
    heldout["post_validation_a0_freeze_sha256"] = "0" * 64
    with pytest.raises(Week4AuthorizationError, match="canonical hash mismatch"):
        validate_authorization_artifact(write_artifact(tmp_path / "heldout", heldout), expected_stage="held_out")


def test_frozen_hashes_are_checked_before_authorization(monkeypatch, tmp_path: Path):
    formal_run = importlib.import_module("experiments.week4_adaptive_red_team.formal_run")
    original_hash = formal_run.sha256_file
    calls: list[str] = []

    def fake_hash(path: Path) -> str:
        if Path(path).resolve() == formal_run.CANONICAL_PREREG.resolve():
            return "0" * 64
        return original_hash(path)

    def unexpected_authorization(*args, **kwargs):
        calls.append("authorization")
        raise AssertionError("authorization must not be read after a frozen-hash failure")

    monkeypatch.setattr(formal_run, "sha256_file", fake_hash)
    monkeypatch.setattr(formal_run, "validate_authorization_artifact", unexpected_authorization)
    with pytest.raises(formal_run.FormalRunBlocked, match="frozen preregistration hash mismatch"):
        formal_run.preflight(config=ROOT / "configs/week4_adaptive_red_team.yaml", population=ROOT / "data/manifests/week4_population_manifest.json", authorization=tmp_path / "authorization.json", runtime_root=ROOT / "results/week4_adaptive_redteam_runs/TEST_ONLY_not_created", stage="validation")
    assert calls == []


def test_failed_preoutput_namespace_is_preserved_but_future_namespace_is_absent():
    failed = ROOT / "results/week4_adaptive_redteam_runs/week4_adaptive_redteam_v0_20260912_supplement_v1"
    assert failed.is_dir()
    assert (failed / "accounting/f5_attempt_ledger.jsonl").is_file()
    assert not (ROOT / "results/week4_adaptive_redteam_runs/TEST_ONLY_preflight_20260911").exists()


def test_formal_runner_accepts_paths_only_and_rejects_scientific_flags():
    formal_run = importlib.import_module("experiments.week4_adaptive_red_team.formal_run")
    with pytest.raises(SystemExit):
        formal_run.parse_args(["--config", "x", "--population", "y", "--authorization", "z", "--runtime-root", "r", "--query-budget", "1"])


def test_frozen_config_hash_and_execution_flag_remain_unchanged():
    config = ROOT / "configs/week4_adaptive_red_team.yaml"
    assert sha256_file(config) == "1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D"
    assert "scientific_execution_enabled: false" in config.read_text(encoding="utf-8")


def test_current_authorization_is_validation_scoped_and_discloses_post_dev_governance():
    artifact = json.loads((ROOT / "results/week4_adaptive_redteam/authorization.json").read_text(encoding="utf-8"))
    assert artifact["invocation_id"] == "week4_validation_01"
    assert artifact["stage"] == artifact["stage_authorization"] == "validation"
    assert artifact["PRIOR_FAILED_ATTEMPT_EXISTED"] is True
    assert artifact["PRIOR_FAILED_ATTEMPT_PRODUCED_SCIENTIFIC_OUTCOME"] is False
    assert artifact["WEEK4_SCIENTIFIC_OUTCOME_OBSERVED_BEFORE_REAUTHORIZATION"] is True
    assert artifact["PRIOR_WEEK4_DEV_OUTCOMES_OBSERVED"] is True
    assert artifact["PRIOR_PARTIAL_RUNS_SCIENTIFICALLY_ADMISSIBLE"] is False
    assert artifact["POST_DEV_GOVERNANCE_AMENDMENT_EXISTS"] is True
    assert artifact["POST_DEV_GOVERNANCE_AMENDMENT_SHA256"] == sha256_file(
        ROOT / "research_assurance/WEEK4_EXECUTION_GOVERNANCE_AMENDMENT_V2.md"
    )
    assert artifact["EXECUTION_GOVERNANCE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is True
    assert artifact["ATTACK_METHOD_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is False
    assert artifact["OBJECTIVE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is False
    assert artifact["SEARCH_PROPOSAL_RULE_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is False
    assert artifact["H4_CHANGED_AFTER_PARTIAL_DEV_OBSERVATION"] is False
    assert artifact["SCIENTIFIC_ATTACK_AND_ESTIMAND_SPEC_CHANGED"] is False
    assert artifact["EXECUTION_GOVERNANCE_AMENDED"] is True
    assert artifact["EXECUTION_IMPLEMENTATION_CHANGED_AFTER_PRIOR_DEV_OBSERVATION"] is True
    assert artifact["formal_runtime_environment_manifest_sha256"] == sha256_file(
        ROOT / "research_assurance/WEEK4_FORMAL_RUNTIME_ENVIRONMENT_MANIFEST.json"
    )


def test_non_bound_python_is_rejected_for_the_bound_formal_environment(monkeypatch):
    formal_run = importlib.import_module("experiments.week4_adaptive_red_team.formal_run")
    monkeypatch.setattr(formal_run.sys, "executable", str(ROOT / "TEST_ONLY_not_the_bound_python.exe"))
    with pytest.raises(formal_run.FormalRunBlocked, match="authorization-bound Python environment"):
        formal_run._validate_runtime_environment()
