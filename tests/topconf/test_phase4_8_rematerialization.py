from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from audiobookbench.topconf.level2.materialization import (
    MaterializationValidationError,
    validate_level2_rematerialization_plan,
)


ROOT = Path(__file__).resolve().parents[2]
ASSURANCE = ROOT / "research_assurance" / "topconf"


def _actual() -> tuple[dict, dict, dict, list[dict]]:
    def load(name: str) -> dict:
        return json.loads((ASSURANCE / name).read_text(encoding="utf-8"))

    v2 = load("LEVEL2_RQ1_POPULATION_MANIFEST_V2.json")
    exclusion = load("LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json")
    ledger = load("LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json")
    return v2, exclusion, ledger, deepcopy(v2["reserve_records"])


def _offered_plan() -> tuple[dict, dict, dict, list[dict], dict]:
    v2, _unused, _unused_ledger, reserves = _actual()
    old = next(row for row in v2["sources"] if row["pool_id"] == "SOURCE_POOL_B_AISHELL1")
    old_cases = sorted((row for row in v2["case_records"] if row["source_id"] == old["source_id"]), key=lambda row: row["case_id"])
    replacement = next(
        row for row in sorted(reserves, key=lambda row: row["source_id"])
        if row["pool_id"] == old["pool_id"] and row["speaker_id"] != old["speaker_id"]
    )
    excluded = {
        "schema_version": "topconf.level2.v2.contamination_exclusion.v1",
        "reason": "VERIFIED_FRESHNESS_CONTAMINATION",
        "scientific_outcomes_accessed": False,
        "excluded_source_ids": [old["source_id"]],
        "excluded_speaker_ids": [old["speaker_id"]],
        "excluded_case_ids": [row["case_id"] for row in old_cases],
        "excluded_source_audio_sha256s": [old["source_audio_sha256"]],
        "excluded_parent_asset_ids": [old["parent_asset_id"]],
    }
    reserve_order = sorted(reserves, key=lambda row: (
        row.get("corpus", ""), row["speaker_id"], row["utterance_id"],
        row["source_id"], row["source_audio_sha256"].lower(), row["parent_asset_id"],
    ))
    rank = next(i for i, row in enumerate(reserve_order, 1) if row["source_id"] == replacement["source_id"])
    new_case_ids = [f"CASE-V3-M{index:02d}" for index in range(1, 5)]
    ledger = {
        "schema_version": "topconf.level2.v2_to_v3.replacement_ledger.v1",
        "status": "READY_FOR_V3_MATERIALIZATION",
        "activation_rule_id": "LEVEL2_RESERVE_ACTIVATION_RULE_V1",
        "scientific_outcome_consulted": False,
        "entries": [{
            "old_source_id": old["source_id"],
            "old_speaker_id": old["speaker_id"],
            "old_case_ids": [row["case_id"] for row in old_cases],
            "exclusion_reason": "VERIFIED_FRESHNESS_CONTAMINATION",
            "replacement_source_id": replacement["source_id"],
            "replacement_speaker_id": replacement["speaker_id"],
            "reserve_rank": rank,
            "new_case_ids": new_case_ids,
            "scientific_outcome_consulted": False,
        }],
    }
    return v2, excluded, ledger, reserves, replacement


def test_actual_phase4_8_stops_before_partial_v3() -> None:
    v2, exclusion, ledger, reserves = _actual()
    result = validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves)
    assert result["status"] == "BLOCKED_INSUFFICIENT_CLEAN_RESERVE"
    assert result["required_replacements"] == 7
    assert result["clean_same_pool_reserve_count"] == 0


def test_contaminated_source_retained_fails() -> None:
    v2, exclusion, ledger, reserves, _replacement = _offered_plan()
    ledger["status"] = "READY_FOR_V3_MATERIALIZATION"
    with pytest.raises(MaterializationValidationError, match="contaminated source retained"):
        validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves, deepcopy(v2))


def test_prohibited_speaker_retained_fails() -> None:
    v2, exclusion, ledger, reserves, replacement = _offered_plan()
    offered = deepcopy(v2)
    old_id = exclusion["excluded_source_ids"][0]
    offered_source = next(row for row in offered["sources"] if row["source_id"] == old_id)
    offered_source["source_id"] = replacement["source_id"]
    offered_source["speaker_id"] = exclusion["excluded_speaker_ids"][0]
    with pytest.raises(MaterializationValidationError):
        validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves, offered)


def test_same_lineage_under_new_case_id_fails() -> None:
    v2, exclusion, ledger, reserves, replacement = _offered_plan()
    offered = deepcopy(v2)
    old_id = exclusion["excluded_source_ids"][0]
    source = next(row for row in offered["sources"] if row["source_id"] == old_id)
    replacement_split = next(row["split"] for row in offered["sources"] if row["speaker_id"] == replacement["speaker_id"])
    source.update({"source_id": replacement["source_id"], "speaker_id": replacement["speaker_id"], "session_id": replacement["session_id"], "utterance_id": replacement["utterance_id"], "text_sha256": replacement["text_sha256"], "parent_asset_id": exclusion["excluded_parent_asset_ids"][0], "source_audio_sha256": exclusion["excluded_source_audio_sha256s"][0], "split": replacement_split})
    for case in offered["case_records"]:
        if case["source_id"] == old_id:
            case.update({"case_id": f"V3-{case['case_id']}", "source_id": replacement["source_id"], "speaker_id": replacement["speaker_id"], "session_id": replacement["session_id"], "utterance_id": replacement["utterance_id"], "text_sha256": replacement["text_sha256"], "parent_asset_id": source["parent_asset_id"], "source_audio_sha256": source["source_audio_sha256"], "split": source["split"]})
    for pool in offered["source_pools"]:
        pool["source_ids"] = [replacement["source_id"] if value == old_id else value for value in pool["source_ids"]]
    # An activated reserve is removed from the remaining reserve list.  Keep
    # the count at 40 with an otherwise valid unused reserve so the test reaches
    # the intended lineage check rather than a reserve/primary collision.
    offered["reserve_records"] = [
        row for row in offered["reserve_records"] if row["source_id"] != replacement["source_id"]
    ]
    spare = deepcopy(reserves[0])
    spare["source_id"] = "TEST-UNUSED-RESERVE"
    offered["reserve_records"].append(spare)
    offered["case_records"] = sorted(offered["case_records"], key=lambda row: row["case_id"])
    offered["case_order"] = sorted(row["case_id"] for row in offered["case_records"])
    with pytest.raises(MaterializationValidationError):
        validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves, offered)


def test_replacement_not_in_reserve_fails() -> None:
    v2, exclusion, ledger, reserves, _replacement = _offered_plan()
    ledger["entries"][0]["replacement_source_id"] = "NOT-IN-FROZEN-RESERVE"
    with pytest.raises(MaterializationValidationError, match="frozen reserve"):
        validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves)


def test_reserve_ordering_violation_fails() -> None:
    v2, _unused, _unused_ledger, reserves = _actual()
    old_sources = [row for row in v2["sources"] if row["pool_id"] == "SOURCE_POOL_B_AISHELL1" and row["speaker_id"] == "AISHELL1_S0002"][:2]
    reserve_rows = [row for row in sorted(reserves, key=lambda row: row["source_id"]) if row["pool_id"] == "SOURCE_POOL_B_AISHELL1" and row["speaker_id"] == "AISHELL1_S0003"][:2]
    ranks = {row["source_id"]: i for i, row in enumerate(sorted(reserves, key=lambda row: (row.get("corpus", ""), row["speaker_id"], row["utterance_id"], row["source_id"], row["source_audio_sha256"].lower(), row["parent_asset_id"])), 1)}
    excluded = {"schema_version": "topconf.level2.v2.contamination_exclusion.v1", "reason": "VERIFIED_FRESHNESS_CONTAMINATION", "scientific_outcomes_accessed": False, "excluded_source_ids": [row["source_id"] for row in old_sources], "excluded_speaker_ids": ["AISHELL1_S0002"], "excluded_case_ids": [case["case_id"] for row in old_sources for case in v2["case_records"] if case["source_id"] == row["source_id"]], "excluded_source_audio_sha256s": [row["source_audio_sha256"] for row in old_sources], "excluded_parent_asset_ids": [row["parent_asset_id"] for row in old_sources]}
    entries = []
    for old, new in zip(old_sources, reversed(reserve_rows)):
        entries.append({"old_source_id": old["source_id"], "old_speaker_id": old["speaker_id"], "old_case_ids": sorted(case["case_id"] for case in v2["case_records"] if case["source_id"] == old["source_id"]), "exclusion_reason": "VERIFIED_FRESHNESS_CONTAMINATION", "replacement_source_id": new["source_id"], "replacement_speaker_id": new["speaker_id"], "reserve_rank": ranks[new["source_id"]], "new_case_ids": ["a", "b", "c", "d"], "scientific_outcome_consulted": False})
    ledger = {"schema_version": "topconf.level2.v2_to_v3.replacement_ledger.v1", "status": "READY_FOR_V3_MATERIALIZATION", "activation_rule_id": "LEVEL2_RESERVE_ACTIVATION_RULE_V1", "scientific_outcome_consulted": False, "entries": entries}
    with pytest.raises(MaterializationValidationError, match="activation order"):
        validate_level2_rematerialization_plan(v2, excluded, ledger, reserves)


@pytest.mark.parametrize("mutation", ["source", "speaker", "case", "pool", "pair", "gt"])
def test_population_or_gt_contract_drift_fails(mutation: str) -> None:
    v2, exclusion, ledger, reserves, _replacement = _offered_plan()
    offered = deepcopy(v2)
    if mutation == "source":
        offered["sources"] = offered["sources"][:-1]
    elif mutation == "speaker":
        offered["sources"][0]["speaker_id"] = offered["sources"][1]["speaker_id"]
    elif mutation == "case":
        offered["case_records"] = offered["case_records"][:-1]
    elif mutation == "pool":
        offered["sources"][0]["pool_id"] = offered["sources"][1]["pool_id"]
    elif mutation == "pair":
        offered["case_records"][0]["source_id"] = offered["case_records"][1]["source_id"]
    elif mutation == "gt":
        offered["ground_truth"] = [{"case_id": "leaked"}]
    with pytest.raises(MaterializationValidationError):
        validate_level2_rematerialization_plan(v2, exclusion, ledger, reserves, offered)
