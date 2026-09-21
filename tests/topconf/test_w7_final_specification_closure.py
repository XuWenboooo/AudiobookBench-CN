from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from audiobookbench.topconf.w7_mechanism_spec import (
    ASSIGNMENT_SALT,
    FAMILY_IDS,
    P4_FIELDS,
    SEED_SALT,
    assign_family,
    family_config_status,
)


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
REPO = ROOT.parents[1]
DETAIL = ROOT / "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.jsonl.gz"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_bam_rights_gate_separates_evaluation_from_redistribution():
    evidence = json.loads((ROOT / "BAM_CHECKPOINT_OFFICIAL_USE_EVIDENCE_V1.json").read_text(encoding="utf-8"))
    decision = json.loads((ROOT / "BAM_RIGHTS_FINAL_ADJUDICATION_V2.json").read_text(encoding="utf-8"))
    assert evidence["checkpoint_officially_provided_for_evaluation"] is True
    assert evidence["local_research_evaluation_supported_by_official_source"] is True
    assert evidence["explicit_weight_redistribution_license"] == "NOT_ESTABLISHED"
    assert evidence["do_not_redistribute_checkpoint"] is True
    assert decision["rights_gate"] == "PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS"
    assert decision["bam_rights"] == decision["rights_gate"]


def test_family_eligibility_is_frozen_and_assignment_is_outcome_blind():
    with gzip.open(DETAIL, "rt", encoding="utf-8") as handle:
        first = json.loads(next(handle))
    assert tuple(first["eligible_families"]) == FAMILY_IDS
    assert first["assignment_salt"] if "assignment_salt" in first else True
    expected = assign_family(first)
    assert first["assignment_hash"] == expected["assignment_hash"]
    assert first["mechanism_family"] == expected["mechanism_family"]
    assert first["seed_hash"] == expected["seed_hash"]
    assert first["configuration_status"] == "INCOMPLETE_P4_HUMAN_DECISION_REQUIRED"


def test_seed_rule_is_deterministic_and_does_not_use_time():
    with gzip.open(DETAIL, "rt", encoding="utf-8") as handle:
        first = json.loads(next(handle))
    again = assign_family(first)
    assert first["seed_hash"] == again["seed_hash"]
    assert first["seed_uint64"] == again["seed_uint64"]
    assert SEED_SALT == "W7_MECHANISM_SEED_V1"
    assert ASSIGNMENT_SALT == "W7_MECHANISM_ASSIGNMENT_V1"
    assert "timestamp" not in json.dumps(first).lower()


def test_precedence_fixes_only_documented_fields_and_p4_fails_closed():
    config = json.loads((ROOT / "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json").read_text(encoding="utf-8"))
    assert config["status"] == "INCOMPLETE_P4_FAIL_CLOSED"
    assert config["fixed_fields"]["sample_rate"] == 16000
    assert config["p4_fields"] == list(P4_FIELDS)
    assert config["mechanism_config_sha256"] == "NOT_AVAILABLE"
    assert all(family_config_status(family)["p4_fields"] == list(P4_FIELDS) for family in FAMILY_IDS)


def test_map_preserves_population_and_has_no_scientific_identity_fields():
    summary = json.loads((ROOT / "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.json").read_text(encoding="utf-8"))
    assert summary["records"] == 106859
    assert summary["distribution_counts"] == {"LlamaPartialSpoof": 64388, "PartialEdit": 42471}
    assert summary["map_determinism"] == "PASS_GENERATOR_CANONICAL_BYTES"
    assert summary["p4_count"] == 35
    with gzip.open(DETAIL, "rt", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    assert len(rows) == 106859
    assert len({row["case_id"] for row in rows}) == 106859
    assert all("absolute" not in json.dumps(row).lower() for row in rows[:5])
    assert all(row["configuration_hash"] == "NOT_AVAILABLE" for row in rows)


def test_map_generator_is_byte_deterministic():
    command = [sys.executable, str(REPO / "tools/topconf/build_w7_mechanism_specification_v1.py")]
    subprocess.run(command, cwd=REPO, check=True, capture_output=True, text=True)
    first = sha256(DETAIL)
    subprocess.run(command, cwd=REPO, check=True, capture_output=True, text=True)
    second = sha256(DETAIL)
    assert first == second


def test_m3_invariants_and_addendum_bind_current_artifacts():
    audit = json.loads((ROOT / "W7_MECHANISM_SPECIFICATION_AUDIT_V1.json").read_text(encoding="utf-8"))
    addendum = json.loads((ROOT / "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.json").read_text(encoding="utf-8"))
    assert audit["m1_assignment_rule"] == "PASS"
    assert audit["m3_invariants"] == "PASS_FOR_GENERATED_ASSIGNMENT_MAP"
    assert addendum["pre_inference_specification_completion"] is True
    assert addendum["w7_scientific_inferences_at_freeze"] == 0
    assert addendum["mechanism_map_sha256"] == sha256(DETAIL)
    assert addendum["mechanism_config_sha256"] == sha256(ROOT / "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json")
    assert addendum["p4_count"] == 35


def test_readiness_remains_fail_closed_until_p4_is_human_completed():
    readiness = json.loads((ROOT / "W7_EXECUTION_READINESS_REAUDIT_V3.json").read_text(encoding="utf-8"))
    assert readiness["bam_rights"] == "PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS"
    assert readiness["ready_localizers"] == 4
    assert readiness["mechanism_p4_count"] == 35
    assert readiness["mechanism_config_complete"] is False
    assert readiness["runner_synthetic_dryrun"] == "NOT_RUN_P4_CONFIG_INCOMPLETE"
    assert readiness["w7_execution_readiness"] == "FAIL_PENDING_HUMAN_P4_DECISIONS"
    assert readiness["authorized_for_reexecution"] is False
