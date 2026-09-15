from __future__ import annotations

import hashlib
import json
from pathlib import Path

from audiobookbench.topconf.level2.materialization import (
    validate_evaluation_manifest,
    validate_inference_manifest,
    validate_level2_freshness_v3,
    validate_level2_population,
)


ROOT = Path(__file__).resolve().parents[2]
ASSURANCE = ROOT / "research_assurance" / "topconf"


def _load(name: str) -> dict:
    return json.loads((ASSURANCE / name).read_text(encoding="utf-8"))


def _sha256(name: str) -> str:
    return hashlib.sha256((ASSURANCE / name).read_bytes()).hexdigest().upper()


def test_phase4_9_v3_views_and_firewall_are_structurally_valid() -> None:
    population = _load("LEVEL2_RQ1_POPULATION_MANIFEST_V3.json")
    inference = _load("LEVEL2_RQ1_INFERENCE_MANIFEST_V3.json")
    evaluation = _load("LEVEL2_RQ1_EVALUATION_MANIFEST_V3.json")

    summary = validate_level2_population(population)
    validate_inference_manifest(inference)
    validate_evaluation_manifest(evaluation)
    assert summary["status"] == "PASS"
    assert summary["source_count"] == 400
    assert summary["speaker_count"] == 120
    assert summary["pair_count"] == 400
    assert summary["case_count"] == 1600
    assert population["authorization"] == "NO_GO"
    assert population["real_level2_outcomes_accessed"] is False
    assert population["result_based_selection"] is False
    assert population["firewall"]["model_inference_runs"] == 0
    assert population["firewall"]["scientific_scores_computed"] is False


def test_phase4_9_pool_shape_and_session_disjointness() -> None:
    population = _load("LEVEL2_RQ1_POPULATION_MANIFEST_V3.json")
    pools = {row["pool_id"]: row for row in population["source_pools"]}
    assert pools["SOURCE_POOL_A_ALIMEETING_SLR119"]["source_count"] == 200
    assert pools["SOURCE_POOL_A_ALIMEETING_SLR119"]["speaker_count"] == 60
    assert pools["SOURCE_POOL_B_AISHELL1"]["source_count"] == 200
    assert pools["SOURCE_POOL_B_AISHELL1"]["speaker_count"] == 60
    assert len(population["reserve_records"]) == 40
    assert sum(row["pool_id"] == "SOURCE_POOL_A_ALIMEETING_SLR119" for row in population["reserve_records"]) == 20
    assert sum(row["pool_id"] == "SOURCE_POOL_B_AISHELL1" for row in population["reserve_records"]) == 20

    split_by_session: dict[str, set[str]] = {}
    for row in population["sources"]:
        split_by_session.setdefault(row["session_id"], set()).add(row["split"])
    assert split_by_session
    assert all(len(splits) == 1 for splits in split_by_session.values())

    pool_a = [row for row in population["sources"] if row["pool_id"] == "SOURCE_POOL_A_ALIMEETING_SLR119"]
    pool_b = [row for row in population["sources"] if row["pool_id"] == "SOURCE_POOL_B_AISHELL1"]
    reserve_a = [row for row in population["reserve_records"] if row["pool_id"] == "SOURCE_POOL_A_ALIMEETING_SLR119"]
    assert len({row["source_audio_sha256"] for row in pool_a}) == 200
    assert len({row["lineage_id"] for row in pool_a}) == 200
    assert not ({row["source_audio_sha256"] for row in pool_a} & {row["source_audio_sha256"] for row in pool_b})
    assert not ({row["source_audio_sha256"] for row in pool_a} & {row["source_audio_sha256"] for row in reserve_a})


def test_phase4_9_v4_fails_closed_and_preserves_prior_identities() -> None:
    population = _load("LEVEL2_RQ1_POPULATION_MANIFEST_V3.json")
    freshness = _load("LEVEL2_FRESHNESS_MANIFEST_V4.json")
    universes = {}
    for reference in freshness["universe_references"].values():
        path = Path(reference["path"])
        if not path.is_absolute():
            path = ASSURANCE / path
        universes[next(name for name, item in freshness["universe_references"].items() if item is reference)] = json.loads(path.read_text(encoding="utf-8"))

    summary = validate_level2_freshness_v3(population, freshness, universes)
    assert summary["status"] == "INSUFFICIENT_EVIDENCE"
    assert all(value == "PARTIAL" for value in summary["completeness"].values())
    assert all(value == 0 for value in summary["comparison_counts"].values())
    assert freshness["decision"]["authorization"] == "NO_GO"
    assert freshness["decision"]["stop_rule"] == "STOP_AFTER_ONE_V3_AND_ONE_V4_AUDIT"
    assert _sha256("LEVEL2_RQ1_POPULATION_MANIFEST_V2.json") == "ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0"
    assert _sha256("LEVEL2_FRESHNESS_MANIFEST_V3.json") == "640D128B0AC0557B0AAB5AA0F7DD209CE47597C096BE3C4EBE3C06B92FA30949"
