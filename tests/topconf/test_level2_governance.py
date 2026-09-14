from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from audiobookbench.topconf.level2.governance import (
    Level2ValidationError,
    build_blinded_manifest,
    validate_case_coverage,
    validate_checkpoint_binding,
    validate_level2_manifest,
    validate_metric_registration,
    validate_namespace,
    validate_reveal_gate,
    validate_retry_ledger,
    validate_threshold_policy,
)


FIXTURE = Path(__file__).parent / "fixtures" / "level2_valid_cohort.json"


def cohort() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_valid_synthetic_cohort_and_blinding_pass() -> None:
    payload = cohort()
    validate_level2_manifest(payload)
    blinded = build_blinded_manifest(payload)
    assert blinded["ground_truth_visible"] is False
    assert all(
        not set(row).intersection({"mechanism_id", "source_id", "reference_id"})
        for row in blinded["cases"]
    )


def test_real_level2_manifest_is_rejected() -> None:
    payload = cohort()
    payload["data_source"] = "REAL_LEVEL2"
    with pytest.raises(Level2ValidationError, match="real Level-2"):
        validate_level2_manifest(payload)


def test_gt_visible_to_inference_fails_closed() -> None:
    payload = cohort()
    blinded = build_blinded_manifest(payload)
    blinded["cases"][0]["target_start_sec"] = 2.0
    with pytest.raises(Level2ValidationError, match="GT visible"):
        from audiobookbench.topconf.level2.governance import validate_blinded_manifest

        validate_blinded_manifest(blinded)


def test_identity_leakage_duplicate_case_and_bad_gt_fail_closed() -> None:
    payload = cohort()
    payload["variants"][1]["source_id"] = "s1"
    payload["variants"][1]["speaker_id"] = "p1"
    with pytest.raises(Level2ValidationError, match="source leakage"):
        validate_level2_manifest(payload)

    payload = cohort()
    payload["variants"][1]["case_id"] = "c1"
    with pytest.raises(Level2ValidationError, match="duplicate case ID"):
        validate_level2_manifest(payload)

    payload = cohort()
    payload["ground_truth"][0]["target_end_sec"] = 99.0
    with pytest.raises(Level2ValidationError, match="outside waveform"):
        validate_level2_manifest(payload)


def test_unknown_case_and_missing_terminal_status_fail_closed() -> None:
    with pytest.raises(Level2ValidationError, match="unknown case"):
        validate_case_coverage(
            ["c1", "c2"],
            [
                {"case_id": "c1", "terminal_category": "SCIENTIFIC_VALID_CASE"},
                {"case_id": "c9", "terminal_category": "INFERENCE_FAILURE"},
            ],
        )
    with pytest.raises(Level2ValidationError, match="missing terminal status"):
        validate_case_coverage(
            ["c1", "c2"],
            [{"case_id": "c1", "terminal_category": "SCIENTIFIC_VALID_CASE"}],
        )


def test_second_namespace_writer_fails_closed() -> None:
    candidate = {
        "invocation_id": "i1",
        "output_namespace": "synthetic/i1",
        "authorization_hash": "a" * 64,
        "protocol_hash": "b" * 64,
        "dataset_hash": "c" * 64,
    }
    with pytest.raises(Level2ValidationError, match="collision"):
        validate_namespace(candidate, [candidate])


def test_unregistered_retry_and_retry_after_valid_fail_closed() -> None:
    terminal = [{"case_id": "c1", "terminal_category": "SCIENTIFIC_VALID_CASE"}]
    base = {
        "attempt_id": "a2",
        "case_id": "c1",
        "attempt_type": "rerun",
        "invoked": True,
        "retry_reason": "infrastructure",
        "authorization_hash": "a" * 64,
    }
    with pytest.raises(Level2ValidationError, match="unregistered"):
        validate_retry_ledger([base], terminal)

    registered = dict(base, registered=True)
    with pytest.raises(Level2ValidationError, match="retry after valid"):
        validate_retry_ledger([registered], terminal)


def test_wrong_checkpoint_and_unregistered_metric_fail_closed() -> None:
    with pytest.raises(Level2ValidationError, match="wrong checkpoint"):
        validate_checkpoint_binding({"checkpoint_sha256": "a" * 64}, "b" * 64)
    with pytest.raises(Level2ValidationError, match="metric not preregistered"):
        validate_metric_registration("posthoc_metric", ["LD@DR95", "AUPRC"])


def test_wrong_dataset_hash_and_reveal_before_freeze_fail_closed() -> None:
    auth = {
        "status": "SYNTHETIC_GOVERNANCE_DRY_RUN",
        "protocol_frozen": True,
        "freeze_record_hash": "f" * 64,
        "protocol_hash": "p" * 64,
        "dataset_hash": "d" * 64,
    }
    inference = {"completed": True, "protocol_hash": "p" * 64}
    with pytest.raises(Level2ValidationError, match="protocol/dataset"):
        validate_reveal_gate(auth, inference, "p" * 64, "e" * 64)

    auth["protocol_frozen"] = False
    with pytest.raises(Level2ValidationError, match="before freeze"):
        validate_reveal_gate(auth, inference, "p" * 64, "d" * 64)


def test_threshold_from_level2_test_set_fails_closed() -> None:
    with pytest.raises(Level2ValidationError, match="threshold from test set"):
        validate_threshold_policy(
            {
                "source": "LEVEL2_TEST_OPTIMIZATION",
                "calibration_split": "level2_test",
                "frozen_before_level2_reveal": False,
            }
        )


def test_valid_reveal_gate_passes_only_after_completion_and_freeze() -> None:
    auth = {
        "status": "SYNTHETIC_GOVERNANCE_DRY_RUN",
        "protocol_frozen": True,
        "freeze_record_hash": "f" * 64,
        "protocol_hash": "p" * 64,
        "dataset_hash": "d" * 64,
    }
    validate_reveal_gate(
        auth,
        {"completed": True, "protocol_hash": "p" * 64},
        "p" * 64,
        "d" * 64,
    )
