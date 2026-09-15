from __future__ import annotations

import copy

from audiobookbench.topconf.level2.materialization import (
    FRESHNESS_DIMENSIONS,
    validate_level2_freshness_v3,
)


def _hash(char: str) -> str:
    return char * 64


def _population() -> dict:
    source = {
        "source_id": "V2-SOURCE-1",
        "speaker_id": "AISHELL1_S0001",
        "source_audio_sha256": _hash("a"),
        "parent_asset_id": "V2-PARENT-1",
        "session_id": "V2-SESSION-1",
        "utterance_id": "V2-UTTERANCE-1",
        "text_sha256": _hash("b"),
    }
    return {
        "status": "MATERIALIZED",
        "materialized": True,
        "result_based_selection": False,
        "sources": [source],
        "case_records": [{
            "case_id": "V2-CASE-1",
            "source_id": source["source_id"],
            "speaker_id": source["speaker_id"],
            "source_audio_sha256": source["source_audio_sha256"],
            "parent_asset_id": source["parent_asset_id"],
        }],
    }


def _universe(status: str = "COMPLETE", records: list[dict] | None = None) -> dict:
    return {
        "status": status,
        "evidence_sources": ["evidence/history.json"],
        "records": records or [],
    }


def _freshness(
    *,
    statuses: dict[str, str] | None = None,
    counts: dict[str, int] | None = None,
    verdict: str = "PASS",
    isolation: list[dict] | None = None,
) -> dict:
    statuses = statuses or {name: "COMPLETE" for name in (
        "CASE_EXCLUSION", "SOURCE_EXCLUSION", "SPEAKER_USAGE", "LINEAGE_EXCLUSION"
    )}
    counts = counts or {
        "case_id_overlap_count": 0,
        "case_lineage_overlap_count": 0,
        "source_overlap_count": 0,
        "lineage_overlap_count": 0,
        "speaker_overlap_count": 0,
        "prohibited_speaker_overlap_count": 0,
        "unknown_case_comparisons": 0,
        "unknown_source_comparisons": 0,
        "unknown_lineage_comparisons": 0,
    }
    return {
        "schema_version": "topconf.level2.freshness.v3",
        "freshness_verdict": verdict,
        "status": verdict,
        "result_based_selection": False,
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "universe_references": {
            name: {"status": status, "evidence_sources": [f"evidence/{name}.json"]}
            for name, status in statuses.items()
        },
        "comparison_counts": counts,
        "corpus_isolation": isolation or [],
    }


def test_incomplete_history_without_overlap_is_insufficient() -> None:
    population = _population()
    freshness = _freshness(
        statuses={
            "CASE_EXCLUSION": "PARTIAL",
            "SOURCE_EXCLUSION": "COMPLETE",
            "SPEAKER_USAGE": "COMPLETE",
            "LINEAGE_EXCLUSION": "PARTIAL",
        },
        counts={
            "case_id_overlap_count": 0,
            "case_lineage_overlap_count": 0,
            "source_overlap_count": 0,
            "lineage_overlap_count": 0,
            "speaker_overlap_count": 0,
            "prohibited_speaker_overlap_count": 0,
            "unknown_case_comparisons": 1,
            "unknown_source_comparisons": 0,
            "unknown_lineage_comparisons": 1,
        },
        verdict="INSUFFICIENT_EVIDENCE",
    )
    universes = {name: _universe(status) for name, status in {
        "CASE_EXCLUSION": "PARTIAL",
        "SOURCE_EXCLUSION": "COMPLETE",
        "SPEAKER_USAGE": "COMPLETE",
        "LINEAGE_EXCLUSION": "PARTIAL",
    }.items()}
    result = validate_level2_freshness_v3(population, freshness, universes)
    assert result["status"] == "INSUFFICIENT_EVIDENCE"


def test_complete_history_without_overlap_passes() -> None:
    population = _population()
    freshness = _freshness()
    universes = {name: _universe() for name in (
        "CASE_EXCLUSION", "SOURCE_EXCLUSION", "SPEAKER_USAGE", "LINEAGE_EXCLUSION"
    )}
    result = validate_level2_freshness_v3(population, freshness, universes)
    assert result["status"] == "PASS"


def test_verified_lineage_overlap_fails_even_with_different_case_id() -> None:
    population = _population()
    lineage = [{
        "lineage_id": "OLD-LINEAGE-1",
        "source_audio_sha256": _hash("a"),
        "parent_asset_id": "OLD-PARENT-1",
        "evidence_sources": ["results/old.jsonl"],
    }]
    source = [{
        "source_id": "OLD-SOURCE-1",
        "source_audio_sha256": _hash("z"),
        "speaker_key": "OTHER:old",
    }]
    counts = _freshness(verdict="FAIL", counts={
        "case_id_overlap_count": 0,
        "case_lineage_overlap_count": 1,
        "source_overlap_count": 0,
        "lineage_overlap_count": 1,
        "speaker_overlap_count": 0,
        "prohibited_speaker_overlap_count": 0,
        "unknown_case_comparisons": 0,
        "unknown_source_comparisons": 0,
        "unknown_lineage_comparisons": 0,
    })
    universes = {
        "CASE_EXCLUSION": _universe(records=[{"case_id": "OLD-CASE-1"}]),
        "SOURCE_EXCLUSION": _universe(records=source),
        "SPEAKER_USAGE": _universe(),
        "LINEAGE_EXCLUSION": _universe(records=lineage),
    }
    result = validate_level2_freshness_v3(population, counts, universes)
    assert result["status"] == "FAIL"
    assert result["comparison_counts"]["case_lineage_overlap_count"] == 1


def test_aishell1_post_freeze_acquisition_evidence_is_recognized() -> None:
    population = _population()
    freshness = _freshness(isolation=[{
        "corpus": "AISHELL-1",
        "pool_id": "SOURCE_POOL_B_AISHELL1",
        "status": "PASS_POST_FREEZE_ACQUISITION",
        "evidence_sources": ["AISHELL1_PROJECT_ENTRY_PROOF_V1.json"],
    }])
    universes = {name: _universe() for name in (
        "CASE_EXCLUSION", "SOURCE_EXCLUSION", "SPEAKER_USAGE", "LINEAGE_EXCLUSION"
    )}
    result = validate_level2_freshness_v3(population, freshness, universes)
    assert result["status"] == "PASS"
    assert result["corpus_isolation"][0]["status"] == "PASS_POST_FREEZE_ACQUISITION"


def test_missing_evidence_source_is_insufficient() -> None:
    population = _population()
    freshness = _freshness()
    freshness["universe_references"]["SOURCE_EXCLUSION"]["evidence_sources"] = []
    universes = {name: _universe() for name in (
        "CASE_EXCLUSION", "SOURCE_EXCLUSION", "SPEAKER_USAGE", "LINEAGE_EXCLUSION"
    )}
    freshness["universe_references"]["SOURCE_EXCLUSION"]["status"] = "COMPLETE"
    universes["SOURCE_EXCLUSION"]["evidence_sources"] = []
    try:
        validate_level2_freshness_v3(population, freshness, universes)
    except Exception as exc:
        assert "evidence source" in str(exc)
    else:
        raise AssertionError("missing evidence source did not fail closed")


def test_unknown_speaker_identity_when_required_is_insufficient() -> None:
    population = _population()
    freshness = _freshness(
        statuses={
            "CASE_EXCLUSION": "COMPLETE",
            "SOURCE_EXCLUSION": "COMPLETE",
            "SPEAKER_USAGE": "UNKNOWN",
            "LINEAGE_EXCLUSION": "COMPLETE",
        },
        counts={
            "case_id_overlap_count": 0,
            "case_lineage_overlap_count": 0,
            "source_overlap_count": 0,
            "lineage_overlap_count": 0,
            "speaker_overlap_count": 0,
            "prohibited_speaker_overlap_count": 0,
            "unknown_case_comparisons": 0,
            "unknown_source_comparisons": 0,
            "unknown_lineage_comparisons": 1,
        },
        verdict="INSUFFICIENT_EVIDENCE",
    )
    universes = {name: _universe(status) for name, status in {
        "CASE_EXCLUSION": "COMPLETE",
        "SOURCE_EXCLUSION": "COMPLETE",
        "SPEAKER_USAGE": "UNKNOWN",
        "LINEAGE_EXCLUSION": "COMPLETE",
    }.items()}
    result = validate_level2_freshness_v3(population, freshness, universes)
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
