"""Logic-only evidence tests for the independent Phase4.9 freshness audit.

These tests intentionally do not change the production validator.  They record
what the current implementation does for the policy branches that the audit
must distinguish.
"""

from __future__ import annotations

from audiobookbench.topconf.level2.materialization import validate_level2_freshness_v3


UNIVERSES = ("CASE_EXCLUSION", "SOURCE_EXCLUSION", "SPEAKER_USAGE", "LINEAGE_EXCLUSION")


def _population() -> dict:
    source = {
        "source_id": "ALIMEETING-SYNTHETIC-1",
        "speaker_id": "ALIMEETING_SPK0001",
        "source_audio_sha256": "a" * 64,
        "parent_asset_id": "ALIMEETING-PARENT-1",
        "session_id": "ALIMEETING-SESSION-1",
        "utterance_id": "ALIMEETING-UTTERANCE-1",
        "text_sha256": "b" * 64,
    }
    return {
        "status": "MATERIALIZED",
        "materialized": True,
        "sources": [source],
        "case_records": [{
            "case_id": "ALIMEETING-CASE-1",
            "source_id": source["source_id"],
            "speaker_id": source["speaker_id"],
            "source_audio_sha256": source["source_audio_sha256"],
            "parent_asset_id": source["parent_asset_id"],
        }],
    }


def _freshness(statuses: dict[str, str], isolation_status: str) -> dict:
    declared_verdict = (
        "INSUFFICIENT_EVIDENCE"
        if any(status in {"PARTIAL", "UNKNOWN"} for status in statuses.values())
        else "PASS"
    )
    return {
        "schema_version": "topconf.level2.freshness.v3",
        "freshness_verdict": declared_verdict,
        "result_based_selection": False,
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "universe_references": {
            name: {"status": status, "evidence_sources": [f"evidence/{name}.json"]}
            for name, status in statuses.items()
        },
        "comparison_counts": {
            "case_id_overlap_count": 0,
            "case_lineage_overlap_count": 0,
            "source_overlap_count": 0,
            "lineage_overlap_count": 0,
            "speaker_overlap_count": 0,
            "prohibited_speaker_overlap_count": 0,
            "unknown_case_comparisons": 0,
            "unknown_source_comparisons": 0,
            "unknown_lineage_comparisons": 0,
        },
        "corpus_isolation": [{
            "corpus": "ALIMEETING_SLR119",
            "pool_id": "SOURCE_POOL_A_ALIMEETING_SLR119",
            "status": isolation_status,
            "evidence_sources": ["project-entry-proof.json"],
        }],
    }


def _universes(statuses: dict[str, str]) -> dict[str, dict]:
    return {
        name: {
            "status": status,
            "evidence_sources": [f"evidence/{name}.json"],
            "records": [],
        }
        for name, status in statuses.items()
    }


def _observed(statuses: dict[str, str], isolation_status: str) -> str:
    result = validate_level2_freshness_v3(
        _population(),
        _freshness(statuses, isolation_status),
        _universes(statuses),
    )
    return result["status"]


def test_post_freeze_entry_does_not_bypass_unrelated_partial_history() -> None:
    statuses = {name: "COMPLETE" for name in UNIVERSES}
    statuses["CASE_EXCLUSION"] = "PARTIAL"
    # Counterfactual observation: the current implementation returns IE even
    # when the partial universe is unrelated and entry proof is present.
    assert _observed(statuses, "PASS_POST_FREEZE_ACQUISITION") == "INSUFFICIENT_EVIDENCE"


def test_pre_freeze_entry_with_partial_history_remains_insufficient() -> None:
    statuses = {name: "COMPLETE" for name in UNIVERSES}
    statuses["CASE_EXCLUSION"] = "PARTIAL"
    assert _observed(statuses, "NO_PRIOR_PROJECT_USAGE_FOUND") == "INSUFFICIENT_EVIDENCE"


def test_confirmed_prior_usage_is_not_enforced_by_current_validator() -> None:
    statuses = {name: "COMPLETE" for name in UNIVERSES}
    # Policy expectation is FAIL; this assertion records the current
    # implementation's observed result for the independent audit report.
    assert _observed(statuses, "FAIL_PRIOR_USAGE_FOUND") == "PASS"


def test_strong_entry_with_complete_zero_overlap_history_passes_current_validator() -> None:
    statuses = {name: "COMPLETE" for name in UNIVERSES}
    assert _observed(statuses, "PASS_POST_FREEZE_ACQUISITION") == "PASS"
