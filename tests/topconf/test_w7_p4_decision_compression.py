import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_exact_inventory_accounts_for_all_35_fields():
    inventory = load("W7_P4_EXACT_INVENTORY_V1.json")
    assert inventory["raw_p4_fields"] == 35
    assert len(inventory["records"]) == 35
    assert len({row["p4_id"] for row in inventory["records"]}) == 35
    assert all(row["resolution_level"] == "P5" for row in inventory["records"])
    assert all(row["outcome_information_used"] is False for row in inventory["records"])


def test_classification_and_compression_have_zero_unclassified_fields():
    classification = load("W7_P4_CLASSIFICATION_AND_COMPRESSION_V1.json")
    assert classification["classification_counts"] == {
        "SCIENTIFIC_CHOICE": 15,
        "IMPLEMENTATION_BINDING": 20,
        "VALIDATION_POLICY": 0,
        "DERIVED": 0,
        "DUPLICATED_SHARED_POLICY": 0,
        "UNCLASSIFIED": 0,
    }
    assert classification["raw_p4_fields"] == 35
    assert classification["minimal_independent_scientific_decisions"] == 5
    assert classification["candidate_complete"] is False


def test_shared_policies_do_not_falsely_collapse_raw_p4_fields():
    shared = load("W7_MECHANISM_SHARED_POLICIES_V1.json")
    assert shared["raw_p4_fields_collapsed"] == 0
    assert set(shared["policies"]) == {"sample_rate_policy", "seed_policy", "quality_gate_policy", "failure_policy"}
    assert "codec_backend" in shared["not_assumed"]


def test_p5_fail_closed_and_case_map_unchanged():
    classification = load("W7_P4_CLASSIFICATION_AND_COMPRESSION_V1.json")
    assert classification["p5_field_count"] == 35
    assert classification["candidate_status"] == "NOT_CREATED_P5_REMAINS"
    map_path = ROOT / "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.jsonl.gz"
    assert hashlib.sha256(map_path.read_bytes()).hexdigest().upper() == "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"
