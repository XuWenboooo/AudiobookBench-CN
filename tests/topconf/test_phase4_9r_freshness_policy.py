from __future__ import annotations

import pytest

from audiobookbench.topconf.level2.materialization import (
    FRESHNESS_PATH_A,
    FRESHNESS_PATH_B,
    FRESHNESS_POLICY_CLARIFICATION_ID,
    FreshnessInsufficientEvidence,
    V3_UNIVERSES,
    validate_level2_freshness_v3,
)


REQUIRED_STRONG_CHECKS = [
    "UNIQUE_CORPUS_ARCHIVE_IDENTITY",
    "OFFICIAL_SOURCE_PROVENANCE",
    "ARCHIVE_OR_FILE_HASH",
    "FIRST_GIT_REFERENCE",
    "FIRST_MANIFEST_REFERENCE",
    "FIRST_PROJECT_USE_REFERENCE",
    "REPOSITORY_WIDE_HISTORICAL_SEARCH",
    "ALIAS_PATH_ARCHIVE_SEARCH",
    "NO_PRIOR_SCIENTIFIC_PROJECT_USAGE",
    "ACQUISITION_PROJECT_ENTRY_TIMING",
    "ASSET_LINEAGE_BOUND_TO_ARCHIVE_IDENTITY",
]


def _hash(char: str) -> str:
    return char * 64


def _population(pool_id: str = "POOL_A") -> dict:
    source = {
        "source_id": f"{pool_id}-SOURCE-1",
        "speaker_id": f"{pool_id}-SPEAKER-1",
        "source_audio_sha256": _hash("a"),
        "parent_asset_id": f"{pool_id}-PARENT-1",
        "session_id": f"{pool_id}-SESSION-1",
        "utterance_id": f"{pool_id}-UTTERANCE-1",
        "text_sha256": _hash("b"),
        "pool_id": pool_id,
    }
    return {
        "status": "MATERIALIZED",
        "materialized": True,
        "result_based_selection": False,
        "sources": [source],
        "case_records": [{
            "case_id": f"{pool_id}-CASE-1",
            "source_id": source["source_id"],
            "speaker_id": source["speaker_id"],
            "source_audio_sha256": source["source_audio_sha256"],
            "parent_asset_id": source["parent_asset_id"],
        }],
    }


def _entry(pool_id: str, *, path: str = FRESHNESS_PATH_B, proof_strength: str = "STRONG",
           prior_use_status: str = "NO_PRIOR_PROJECT_USAGE_FOUND", status: str = "PASS_POST_FREEZE_ACQUISITION",
           contradiction: bool = False) -> dict:
    return {
        "corpus": pool_id,
        "pool_id": pool_id,
        "status": status,
        "evidence_sources": ["project-entry-proof.json"],
        "path": path,
        "proof_strength": proof_strength,
        "prior_use_status": prior_use_status,
        "project_entry_after_freeze": path == FRESHNESS_PATH_B,
        "asset_lineage_binding": "BOUND" if path == FRESHNESS_PATH_B else "UNBOUND",
        "proof_checks": REQUIRED_STRONG_CHECKS if proof_strength == "STRONG" else [],
        "provenance_contradiction": contradiction,
        "channel_semantics": {
            "channel_type": "SINGLE_SPEAKER_MONO",
            "audio_rendering": "MONO",
            "sample_rate_hz": 16000,
            "far_field_8ch_included": False,
        },
    }


def _freshness(*, statuses: dict[str, str], relevance: dict[str, dict[str, str]],
               entries: list[dict], verdict: str, path: str) -> dict:
    return {
        "schema_version": "topconf.level2.freshness.v3",
        "freshness_policy_id": FRESHNESS_POLICY_CLARIFICATION_ID,
        "freshness_evidence_path": path,
        "freshness_verdict": verdict,
        "status": verdict,
        "result_based_selection": False,
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "universe_references": {
            name: {"status": status, "evidence_sources": [f"evidence/{name}.json"]}
            for name, status in statuses.items()
        },
        "historical_universe_relevance": relevance,
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
        "corpus_isolation": entries,
    }


def _universes(statuses: dict[str, str], *, lineage_records: list[dict] | None = None) -> dict[str, dict]:
    return {
        name: {
            "status": status,
            "evidence_sources": [f"evidence/{name}.json"],
            "records": lineage_records if name == "LINEAGE_EXCLUSION" and lineage_records is not None else [],
        }
        for name, status in statuses.items()
    }


def _relevance(pool_id: str, value: str) -> dict[str, dict[str, str]]:
    return {pool_id: {name: value for name in V3_UNIVERSES}}


def test_verified_prior_usage_fails_before_completeness_handling() -> None:
    statuses = {name: "PARTIAL" for name in V3_UNIVERSES}
    entry = _entry(
        "POOL_A",
        prior_use_status="FAIL_PRIOR_USAGE_FOUND",
        status="FAIL_PRIOR_USAGE_FOUND",
    )
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY"),
        entries=[entry],
        verdict="FAIL",
        path=FRESHNESS_PATH_B,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "FAIL"
    assert result["decision_reason"] == "VERIFIED_PRIOR_USAGE_FOUND"


def test_verified_lineage_overlap_fails_even_with_strong_entry() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    entry = _entry("POOL_A")
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY"),
        entries=[entry],
        verdict="FAIL",
        path=FRESHNESS_PATH_B,
    )
    lineage = [{
        "lineage_id": "OLD-LINEAGE-1",
        "source_audio_sha256": _hash("a"),
        "parent_asset_id": "OLD-PARENT-1",
        "evidence_sources": ["results/old.jsonl"],
    }]
    freshness["comparison_counts"].update({
        "case_lineage_overlap_count": 1,
        "lineage_overlap_count": 1,
    })
    result = validate_level2_freshness_v3(
        _population(), freshness, _universes(statuses, lineage_records=lineage)
    )
    assert result["status"] == "FAIL"
    assert result["decision_reason"] == "VERIFIED_PROHIBITED_OVERLAP"


def test_strong_post_freeze_entry_can_discharge_unrelated_partial_history() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    statuses["CASE_EXCLUSION"] = "PARTIAL"
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY"),
        entries=[_entry("POOL_A")],
        verdict="PASS",
        path=FRESHNESS_PATH_B,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "PASS"
    assert result["freshness_evidence_path"] == FRESHNESS_PATH_B


def test_weak_entry_with_relevant_partial_history_fails_closed() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    statuses["SOURCE_EXCLUSION"] = "PARTIAL"
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "DIRECTLY_RELEVANT"),
        entries=[_entry("POOL_A", proof_strength="NOT_STRONG")],
        verdict="INSUFFICIENT_EVIDENCE",
        path=FRESHNESS_PATH_B,
    )
    with pytest.raises(FreshnessInsufficientEvidence):
        validate_level2_freshness_v3(_population(), freshness, _universes(statuses))


def test_strong_entry_with_contradictory_prior_use_fails() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    entry = _entry(
        "POOL_A",
        prior_use_status="FAIL_PRIOR_USAGE_FOUND",
        contradiction=True,
    )
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "IRRELEVANT_BY_STRONG_POST_FREEZE_PROJECT_ENTRY"),
        entries=[entry],
        verdict="FAIL",
        path=FRESHNESS_PATH_B,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "FAIL"
    assert result["decision_reason"] == "VERIFIED_PRIOR_USAGE_FOUND"


def test_pre_freeze_corpus_with_incomplete_relevant_history_is_insufficient() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    statuses["LINEAGE_EXCLUSION"] = "PARTIAL"
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "POTENTIALLY_RELEVANT"),
        entries=[_entry("POOL_A", path=FRESHNESS_PATH_A)],
        verdict="INSUFFICIENT_EVIDENCE",
        path=FRESHNESS_PATH_A,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert "RELEVANT_HISTORICAL_UNIVERSE_INCOMPLETE" in result["decision_reason"]


def test_complete_history_with_zero_overlap_passes() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "DIRECTLY_RELEVANT"),
        entries=[_entry("POOL_A", path=FRESHNESS_PATH_A)],
        verdict="PASS",
        path=FRESHNESS_PATH_A,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "PASS"
    assert result["freshness_evidence_path"] == FRESHNESS_PATH_A


def test_unknown_critical_relevance_is_insufficient() -> None:
    statuses = {name: "COMPLETE" for name in V3_UNIVERSES}
    freshness = _freshness(
        statuses=statuses,
        relevance=_relevance("POOL_A", "UNKNOWN"),
        entries=[_entry("POOL_A")],
        verdict="INSUFFICIENT_EVIDENCE",
        path=FRESHNESS_PATH_B,
    )
    result = validate_level2_freshness_v3(_population(), freshness, _universes(statuses))
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert "UNKNOWN_CRITICAL_HISTORICAL_RELEVANCE" in result["decision_reason"]
