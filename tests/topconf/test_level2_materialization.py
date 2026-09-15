from __future__ import annotations

import copy

import pytest

from audiobookbench.topconf.level2.materialization import (
    FRESHNESS_DIMENSIONS,
    FreshnessInsufficientEvidence,
    FreshnessValidationError,
    MaterializationValidationError,
    validate_evaluation_manifest,
    validate_inference_manifest,
    validate_level2_freshness,
    validate_level2_population,
)


def _hash(char: str) -> str:
    return char * 64


def _plan() -> dict:
    return {
        "independent_source_pools": 2,
        "primary_sources": 4,
        "speakers": 4,
        "sources_per_pool": 2,
        "speakers_per_pool": 2,
        "mechanisms_per_source": 4,
        "predeclared_source_reserve": 1,
        "target_duration_sec": [8.0, 30.0],
    }


def _source(index: int, pool: str, speaker: str, reserve: bool = False) -> dict:
    sid = f"{'reserve' if reserve else 'source'}-{index:02d}"
    return {
        "source_id": sid,
        "speaker_id": speaker,
        "session_id": f"session-{sid}",
        "utterance_id": f"utterance-{sid}",
        "text_sha256": _hash(chr(ord('a') + (index % 20))),
        "parent_asset_id": f"parent-{sid}",
        "source_audio_sha256": _hash(chr(ord('A') + (index % 20))),
        "source_audio_path": f"/inputs/{sid}.wav",
        "audio_size_bytes": 1000 + index,
        "sample_rate_hz": 16000,
        "channels": 1,
        "format": "PCM_S16LE",
        "duration_sec": 12.0,
        "pool_id": pool,
        "split": "held_out" if reserve else ("development" if pool == "pool-a" else "calibration"),
    }


def population() -> tuple[dict, dict]:
    plan = _plan()
    sources = [
        _source(0, "pool-a", "speaker-a0"),
        _source(1, "pool-a", "speaker-a1"),
        _source(2, "pool-b", "speaker-b0"),
        _source(3, "pool-b", "speaker-b1"),
    ]
    mechanisms = ["splice", "conventional_tts", "voice_conditioned", "neural_edit"]
    cases = []
    case_number = 0
    for source in sources:
        for mechanism in mechanisms:
            cases.append(
                {
                    "case_id": f"case-{case_number:03d}",
                    "pair_id": f"pair-{source['source_id']}",
                    "source_id": source["source_id"],
                    "speaker_id": source["speaker_id"],
                    "session_id": source["session_id"],
                    "utterance_id": source["utterance_id"],
                    "reference_audio_id": None,
                    "text_sha256": source["text_sha256"],
                    "parent_asset_id": source["parent_asset_id"],
                    "source_audio_sha256": source["source_audio_sha256"],
                    "mechanism_id": mechanism,
                    "transform_condition": "NONE",
                    "target_position": 1.0,
                    "target_duration_sec": 8.0,
                    "generator_input_identity": f"input-{case_number:03d}",
                    "generator_id": f"generator-{mechanism}",
                    "generator_version": "frozen-v1",
                    "generation_seed": 1000 + case_number,
                    "transform_seed": 2000 + case_number,
                    "data_role": "LEVEL2_CONFIRMATORY_POPULATION",
                    "split": source["split"],
                }
            )
            case_number += 1
    manifest = {
        "schema_version": "topconf.level2.rq1.population.v1",
        "manifest_id": "SYNTHETIC_LEVEL2_POPULATION",
        "status": "MATERIALIZED",
        "materialized": True,
        "real_level2_outcomes_accessed": False,
        "result_based_selection": False,
        "frozen_plan": plan,
        "source_pools": [
            {
                "pool_id": "pool-a",
                "source_count": 2,
                "speaker_count": 2,
                "source_ids": ["source-00", "source-01"],
                "speaker_ids": ["speaker-a0", "speaker-a1"],
                "manifest_sha256": _hash("1"),
            },
            {
                "pool_id": "pool-b",
                "source_count": 2,
                "speaker_count": 2,
                "source_ids": ["source-02", "source-03"],
                "speaker_ids": ["speaker-b0", "speaker-b1"],
                "manifest_sha256": _hash("2"),
            },
        ],
        "sources": sources,
        "reserve_records": [_source(4, "reserve", "reserve-speaker", reserve=True)],
        "case_records": cases,
        "case_order": [row["case_id"] for row in cases],
        "counts": {
            "population_size": 4,
            "source_count": 4,
            "speaker_count": 4,
            "pair_count": 4,
            "case_count": 16,
            "mechanism_counts": {mechanism: 4 for mechanism in mechanisms},
            "transform_counts": {"NONE": 16},
        },
        "audio_materialized": False,
    }
    return manifest, plan


def test_population_cardinality_pairing_and_seed_contract_pass() -> None:
    manifest, plan = population()
    summary = validate_level2_population(manifest, expected_plan=plan)
    assert summary["status"] == "PASS"
    assert summary["case_count"] == 16
    assert summary["mechanism_counts"]["neural_edit"] == 4


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda p: p["case_records"].__setitem__(1, dict(p["case_records"][0])), "duplicate case"),
        (lambda p: p["counts"].__setitem__("speaker_count", 3), "speaker_count"),
        (lambda p: p["case_records"][1].__setitem__("mechanism_id", "splice"), "mechanism"),
        (lambda p: p["case_records"][1].__setitem__("generation_seed", p["case_records"][0]["generation_seed"]), "seed"),
        (lambda p: p["sources"][0].pop("parent_asset_id"), "required metadata"),
        (lambda p: p["case_records"][0].__setitem__("source_audio_sha256", _hash("z")), "binding mismatch"),
        (lambda p: p["case_records"].pop(), "case count"),
        (lambda p: p["case_records"].append(dict(p["case_records"][-1], case_id="case-extra", generation_seed=9999, transform_seed=9999)), "case count"),
    ],
)
def test_population_corruption_fails_closed(mutation, message: str) -> None:
    manifest, plan = population()
    mutation(copy.deepcopy(manifest))
    broken = copy.deepcopy(manifest)
    mutation(broken)
    with pytest.raises(MaterializationValidationError, match=message):
        validate_level2_population(broken, expected_plan=plan)


def _exclusion_record(**overrides: object) -> dict:
    row = {dimension: f"old-{dimension}" for dimension in FRESHNESS_DIMENSIONS}
    row["text_sha256"] = _hash("9")
    row["source_audio_sha256"] = _hash("8")
    row.update(overrides)
    return row


def freshness(population_manifest: dict, records: list[dict]) -> dict:
    overlaps = {dimension: 0 for dimension in FRESHNESS_DIMENSIONS}
    if records and records[0].get("speaker_id") == "speaker-a0":
        overlaps["speaker_id"] = 1
    return {
        "schema_version": "topconf.level2.freshness.v1",
        "status": "PASS",
        "freshness_verdict": "PASS",
        "result_based_selection": False,
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "required_exclusion_sets": ["historical"],
        "exclusion_sets": [
            {
                "set_id": "historical",
                "status": "COMPLETE",
                "manifest_sha256": _hash("e"),
                "identity_dimensions": list(FRESHNESS_DIMENSIONS),
                "records": records,
            }
        ],
        "overlap_counts": overlaps,
    }


def test_freshness_passes_with_allowed_historical_speaker_overlap() -> None:
    manifest, plan = population()
    validate_level2_population(manifest, expected_plan=plan)
    result = validate_level2_freshness(manifest, freshness(manifest, [_exclusion_record(speaker_id="speaker-a0")]))
    assert result["status"] == "PASS"
    assert result["overlap_counts"]["speaker_id"] == 1


def test_same_case_and_prohibited_lineage_overlap_fail_closed() -> None:
    manifest, plan = population()
    validate_level2_population(manifest, expected_plan=plan)
    with pytest.raises(FreshnessValidationError, match="overlap"):
        validate_level2_freshness(manifest, freshness(manifest, [_exclusion_record(case_id="case-000")]))
    with pytest.raises(FreshnessValidationError, match="overlap"):
        validate_level2_freshness(manifest, freshness(manifest, [_exclusion_record(parent_asset_id="parent-source-00")]))


def test_missing_lineage_is_insufficient_evidence() -> None:
    manifest, _ = population()
    row = _exclusion_record()
    row.pop("parent_asset_id")
    with pytest.raises(FreshnessInsufficientEvidence, match="lineage"):
        validate_level2_freshness(manifest, freshness(manifest, [row]))


def test_nonmaterialized_population_cannot_pass_freshness() -> None:
    manifest, _ = population()
    manifest["status"] = "BLOCKED_INSUFFICIENT_EVIDENCE"
    manifest["materialized"] = False
    with pytest.raises(FreshnessInsufficientEvidence, match="not materialized"):
        validate_level2_freshness(manifest, freshness(manifest, []))


def test_inference_view_rejects_gt_and_evaluation_view_has_runner_firewall() -> None:
    inference = {
        "schema_version": "topconf.level2.rq1.inference.v1",
        "status": "MATERIALIZED",
        "ground_truth_visible": False,
        "cases": [{"opaque_case_id": "case-000", "audio_sha256": _hash("a"), "duration_sec": 12.0, "split": "test"}],
    }
    validate_inference_manifest(inference)
    inference["cases"][0]["target_start_sec"] = 1.0
    with pytest.raises(MaterializationValidationError, match="semantics"):
        validate_inference_manifest(inference)

    evaluation = {
        "schema_version": "topconf.level2.rq1.evaluation.v1",
        "status": "MATERIALIZED",
        "model_runner_access": False,
        "cases": [{"case_id": "case-000", "target_start_sec": 1.0, "target_end_sec": 3.0, "label": "manipulated", "mechanism_id": "splice"}],
    }
    validate_evaluation_manifest(evaluation)
    evaluation["cases"][0]["score"] = 0.5
    with pytest.raises(MaterializationValidationError, match="outcome"):
        validate_evaluation_manifest(evaluation)
