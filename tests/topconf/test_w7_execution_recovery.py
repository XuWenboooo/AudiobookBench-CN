from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from audiobookbench.topconf.w7_execution import (
    FROZEN_LOCALIZER_REGISTRY,
    W7ExecutionContractError,
    assert_frozen_input_hashes,
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


def test_checkpoint_and_rights_adjudication_bind_the_actual_assets():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    adjudication = json.loads((root / "W7_MODEL_AND_RIGHTS_ADJUDICATION_V1.json").read_text(encoding="utf-8"))
    assert adjudication["sal_checkpoint_adjudication"] == "HISTORICALLY_VALID_BUT_ASSET_NOT_MATERIALIZED_AFTER_MIGRATION"
    assert adjudication["sal_checkpoint"]["actual_sha256"] == "NOT_AVAILABLE"
    assert adjudication["bam_checkpoint_adjudication"] == "HISTORICALLY_VALID_BUT_PATH_BROKEN"
    assert adjudication["bam_checkpoint"]["identity"] == "PASS"
    assert adjudication["bam_checkpoint"]["actual_sha256"] == adjudication["bam_checkpoint"]["expected_sha256"]
    assert adjudication["bam_rights_adjudication"] == "HISTORICAL_EVIDENCE_REFERENCED_DIFFERENT_ASSET"
    assert adjudication["bam_rights"]["zenodo_file_bytes"] != adjudication["bam_rights"]["checkpoint_bytes"]
    assert adjudication["bam_rights"]["status"] == "FAIL"


def test_execution_recovery_hash_manifest_covers_runner_and_blocked_config():
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    manifest = json.loads((root / "W7_PREREGISTRATION_HASH_MANIFEST_V3.json").read_text(encoding="utf-8"))
    mechanism = json.loads((root / "W7_MECHANISM_EXECUTION_CONFIG_V1.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "PASS_COMPLETE_COVERAGE_EXECUTION_RECOVERY"
    assert manifest["hash_coverage_gaps"] == []
    assert "src/audiobookbench/topconf/w7_execution.py" in manifest["records"]["unified_runner"]
    assert mechanism["status"] == "NOT_GENERATED_FAIL_CLOSED"
