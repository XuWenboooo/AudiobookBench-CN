import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOP = ROOT / "research_assurance" / "topconf"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_gate1_correction_is_preexisting_and_protocol_is_refrozen():
    old = TOP / "W7_PILOT_PROTOCOL_V1.md"
    new = TOP / "W7_PILOT_PROTOCOL_V1_1.md"
    assert sha256(old) == "0d386e3461afeaa5a2dce361a8d7ebca58f5816f111827322576297774a51d3c"
    text = new.read_text(encoding="utf-8")
    assert "GAP_OBSERVED_IN >= 3 DISTINCT localization paradigms\nAND\nGAP_OBSERVED_IN >= 2 external distributions" in text
    assert "W7_PROTOCOL_FROZEN = YES" in text


def test_case_manifest_v2_is_schema_shaped_and_population_preserving():
    summary = json.loads((TOP / "W7_FINAL_CASE_MANIFEST_V2.json").read_text(encoding="utf-8"))
    assert summary["old_case_count"] == summary["new_case_count"] == 106859
    assert summary["condition_rows"] == 427436
    assert summary["population_semantic_equivalence"] == "PASS"
    assert summary["materialized_asset_hash_coverage"] == 106859
    assert summary["derivation_identity_coverage"] == 320577
    assert re.fullmatch(r"[0-9a-f]{64}", summary["manifest_sha256"])


def test_case_manifest_rows_have_deterministic_identity_and_four_conditions():
    required = {"case_id", "case_identity_hash", "source_audio_hash", "audio_artifact_hash", "gt_id", "condition_id"}
    by_logical = {}
    count = 0
    with gzip.open(TOP / "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            count += 1
            assert required <= row.keys()
            assert re.fullmatch(r"w7case_[0-9a-f]{32}", row["case_id"])
            assert re.fullmatch(r"[0-9a-f]{64}", row["case_identity_hash"])
            assert re.fullmatch(r"[0-9a-f]{64}", row["source_audio_hash"])
            assert re.fullmatch(r"[0-9a-f]{64}", row["audio_artifact_hash"])
            key = (row["distribution_id"], row["source_audio_id"], row["gt_id"])
            by_logical.setdefault(key, set()).add(row["condition_id"])
    assert count == 427436
    assert len(by_logical) == 106859
    assert all(value == {"clean", "mechanism_shift", "codec", "resampling"} for value in by_logical.values())


def test_preregistration_coverage_and_execution_firewall():
    prereg = json.loads((TOP / "W7_PREREGISTRATION_HASH_MANIFEST_V2.json").read_text(encoding="utf-8"))
    execution = json.loads((TOP / "W7_FINAL_EXECUTION_MANIFEST_V2.json").read_text(encoding="utf-8"))
    precheck = json.loads((TOP / "W7_HUMAN_AUTHORIZATION_PRECHECK_V2.json").read_text(encoding="utf-8"))
    assert prereg["status"] == "PASS_COMPLETE_COVERAGE_PRE_INFERENCE"
    assert prereg["hash_coverage_gaps"] == []
    assert execution["authorization"]["authorized"] is False
    assert execution["w7_executed"] is False
    assert execution["level2_outcomes_accessed"] is False
    assert precheck["ready_for_human_authorization"] == "YES"
    assert precheck["authorized"] == "NO"
    assert precheck["exact_blockers"] == []
