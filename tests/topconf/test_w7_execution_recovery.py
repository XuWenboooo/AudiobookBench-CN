from __future__ import annotations

import hashlib
import gzip
import json
from pathlib import Path

import pytest

from audiobookbench.topconf.w7_execution import (
    FROZEN_LOCALIZER_REGISTRY,
    W7ExecutionContractError,
    assert_frozen_input_hashes,
    assert_reexecution_prerequisites,
    assert_registry_is_frozen,
    build_terminal_row,
    synthetic_adapter_output,
)


def test_registry_is_exactly_the_frozen_four_localizers():
    assert_registry_is_frozen()
    assert tuple(FROZEN_LOCALIZER_REGISTRY) == ("CFPRF", "MultiReso", "SAL", "BAM")


def test_synthetic_outputs_are_deterministic_and_not_w7_data():
    for model_id in FROZEN_LOCALIZER_REGISTRY:
        first = synthetic_adapter_output(model_id)
        assert first == synthetic_adapter_output(model_id)
        assert first["fixture"] == "SYNTHETIC_ONLY_NO_W7_CASE"
        assert first["finite"] is True


def test_terminal_rows_reject_unfrozen_inputs_and_silent_failures():
    row = build_terminal_row(run_id="dry", case_id="fixture", distribution="PartialEdit", condition="clean", model_id="SAL", status="MODEL_LOAD_FAILURE", failure_code="CHECKPOINT_MISSING", runtime_metadata={"synthetic": True})
    assert row["checkpoint_sha256"] == FROZEN_LOCALIZER_REGISTRY["SAL"].checkpoint_sha256
    with pytest.raises(W7ExecutionContractError):
        build_terminal_row(run_id="dry", case_id="fixture", distribution="other", condition="clean", model_id="SAL", status="VALID_INFERENCE", runtime_metadata={})
    with pytest.raises(W7ExecutionContractError):
        build_terminal_row(run_id="dry", case_id="fixture", distribution="PartialEdit", condition="clean", model_id="SAL", status="MODEL_LOAD_FAILURE", runtime_metadata={})


def test_frozen_hash_gate_is_fail_closed(tmp_path: Path):
    payload = tmp_path / "frozen.txt"
    payload.write_text("frozen\n", encoding="utf-8")
    actual = hashlib.sha256(payload.read_bytes()).hexdigest().upper()
    assert_frozen_input_hashes({payload: actual})
    with pytest.raises(W7ExecutionContractError):
        assert_frozen_input_hashes({payload: "0" * 64})


def test_sal_exact_recovery_and_bam_checkpoint_rights_are_separate_gates():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    sal = (root / "SAL_FROZEN_CHECKPOINT_IDENTITY_V1.md").read_text(encoding="utf-8")
    bam = (root / "BAM_CHECKPOINT_RIGHTS_BINDING_V1.md").read_text(encoding="utf-8")
    adjudication = json.loads((root / "W7_MODEL_AND_RIGHTS_ADJUDICATION_V2.json").read_text(encoding="utf-8"))
    assert "SAL_CHECKPOINT_IDENTITY = PASS" in sal
    assert "FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F" in sal
    assert adjudication["sal_checkpoint"]["identity"] == "PASS"
    assert adjudication["sal_checkpoint"]["actual_sha256"] == adjudication["sal_checkpoint"]["expected_sha256"]
    assert adjudication["bam_checkpoint_adjudication"] == "HISTORICALLY_VALID_BUT_PATH_BROKEN"
    assert adjudication["bam_checkpoint"]["identity"] == "PASS"
    assert adjudication["bam_checkpoint"]["actual_sha256"] == adjudication["bam_checkpoint"]["expected_sha256"]
    assert "BAM_CHECKPOINT_RIGHTS = FAIL_UNRESOLVED" in bam
    assert "DO_NOT_REDISTRIBUTE_CHECKPOINT = YES" in bam
    assert adjudication["bam_rights_adjudication"] == "FAIL_UNRESOLVED"
    assert adjudication["bam_rights"]["zenodo_file_bytes"] != adjudication["bam_rights"]["checkpoint_bytes"]
    assert adjudication["bam_rights"]["status"] == "FAIL"


def test_mechanism_evidence_and_human_template_leave_no_implicit_configuration():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    matrix = (root / "MECHANISM_PARAMETER_EVIDENCE_MATRIX_V1.md").read_text(encoding="utf-8")
    template = (root / "W7_MECHANISM_HUMAN_FREEZE_TEMPLATE_V1.md").read_text(encoding="utf-8")
    proposal = json.loads((root / "W7_MECHANISM_CASE_MAP_PROPOSAL_V1.json").read_text(encoding="utf-8"))
    assert "A — explicitly frozen" in matrix
    assert "C — permitted but non-unique" in matrix
    assert "D — unspecified" in matrix
    assert "Decision M1" in template and "Decision M2" in template and "Decision M3" in template
    assert proposal["status"] == "PENDING_HUMAN_MECHANISM_FREEZE"
    assert proposal["records"] == 106859
    assert proposal["distribution_counts"] == {"LlamaPartialSpoof": 64388, "PartialEdit": 42471}
    with gzip.open(root / proposal["detailed_records"], "rt", encoding="utf-8") as handle:
        first = json.loads(next(handle))
    assert first["mechanism_family"] == "NOT_FROZEN"
    assert first["parameter_status"] == "HUMAN_DECISION_REQUIRED"
    assert set(first["parameter_fields"].values()) == {"HUMAN_DECISION_REQUIRED"}
    assert "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz" in first["evidence_sources"]
    assert first["configuration_hash"] == "NOT_FROZEN"
    assert first["condition_id"] == "mechanism_shift"


def test_runner_prerequisite_gate_rejects_current_state_and_never_self_authorizes():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    readiness = json.loads((root / "W7_EXECUTION_READINESS_REAUDIT_V2.json").read_text(encoding="utf-8"))
    assert readiness["w7_execution_readiness"] == "FAIL"
    assert readiness["authorized_for_reexecution"] is False
    with pytest.raises(W7ExecutionContractError):
        assert_reexecution_prerequisites({
            "sal_checkpoint_identity": readiness["sal_checkpoint_identity"],
            "bam_checkpoint_rights": readiness["bam_rights"],
            "mechanism_human_freeze": readiness["mechanism_execution_config"],
            "human_reexecution_authorization": "NOT_PRESENT",
        })
    assert_reexecution_prerequisites({
        "sal_checkpoint_identity": "PASS_EXACT_RECOVERED",
        "bam_checkpoint_rights": "PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS",
        "mechanism_human_freeze": "PASS_COMPLETE_TOTAL_MAP",
        "human_reexecution_authorization": "PASS_EXPLICIT_POST_CLOSURE",
    })


def test_v3_and_v5_protected_hashes_remain_exact_and_v4_is_preserved_by_reference():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    repo = root.parents[1]
    assert hashlib.sha256((root / "LEVEL2_RQ1_POPULATION_MANIFEST_V3.json").read_bytes()).hexdigest().upper() == "AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4"
    assert hashlib.sha256((root / "LEVEL2_FRESHNESS_MANIFEST_V5.json").read_bytes()).hexdigest().upper() == "6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E"
    manifest = json.loads((root / "W7_PREREGISTRATION_HASH_MANIFEST_V4.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "PASS_COMPLETE_COVERAGE_FINAL_BLOCKER_CLOSURE"
    assert manifest["hash_coverage_gaps"] == []
    assert manifest["prior_v3_reference"]["sha256"] == hashlib.sha256((root / "W7_PREREGISTRATION_HASH_MANIFEST_V3.json").read_bytes()).hexdigest().upper()
    v5 = json.loads((root / "W7_PREREGISTRATION_HASH_MANIFEST_V5.json").read_text(encoding="utf-8"))
    assert v5["prior_v4_reference"]["sha256"] == hashlib.sha256((root / "W7_PREREGISTRATION_HASH_MANIFEST_V4.json").read_bytes()).hexdigest().upper()
    assert v5["hash_coverage_gaps"] == []
    assert "src/audiobookbench/topconf/w7_execution.py" in manifest["records"]["runner_and_builders"]
    assert (repo / "tools/topconf/build_w7_mechanism_case_map_proposal.py").is_file()
