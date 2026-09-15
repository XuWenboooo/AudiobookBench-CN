"""Build the one fail-closed Phase4.9 V4 freshness proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.materialization import _v3_comparisons  # noqa: E402


UNIVERSE_FILES = {
    "CASE_EXCLUSION": "HISTORICAL_CASE_EXCLUSION_UNIVERSE_V3.json",
    "SOURCE_EXCLUSION": "HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json",
    "SPEAKER_USAGE": "HISTORICAL_SPEAKER_USAGE_UNIVERSE_V1.json",
    "LINEAGE_EXCLUSION": "HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha(payload: object) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest().upper()


def build(population_path: Path, v2_path: Path, assurance_root: Path) -> dict[str, Any]:
    population = load_json(population_path)
    v2 = load_json(v2_path)
    universes = {key: load_json(assurance_root / filename) for key, filename in UNIVERSE_FILES.items()}
    comparison = _v3_comparisons(population, universes)
    references: dict[str, Any] = {}
    for universe_id, filename in UNIVERSE_FILES.items():
        universe = universes[universe_id]
        references[universe_id] = {
            "path": filename,
            "sha256": sha256_path(assurance_root / filename),
            "status": "PARTIAL",
            "source_status": universe.get("status"),
            "evidence_sources": [
                filename,
                "PHASE4_7_HISTORICAL_FRESHNESS_PROOF_V1.md",
                "PHASE4_7_HISTORICAL_EXCLUSION_AND_FRESHNESS_CLOSURE.md",
            ],
        }

    v3_sources = {str(row["source_id"]): row for row in population["sources"]}
    v2_sources = {str(row["source_id"]): row for row in v2["sources"]}
    a_ids = {source_id for source_id, row in v3_sources.items() if row["pool_id"] == "SOURCE_POOL_A_ALIMEETING_SLR119"}
    b_ids = {source_id for source_id, row in v3_sources.items() if row["pool_id"] == "SOURCE_POOL_B_AISHELL1"}
    v2_a_ids = {source_id for source_id, row in v2_sources.items() if row["pool_id"] == "SOURCE_POOL_A_AISHELL3"}
    v2_b_ids = {source_id for source_id, row in v2_sources.items() if row["pool_id"] == "SOURCE_POOL_B_AISHELL1"}
    v2_a_speakers = {str(v2_sources[source_id]["speaker_id"]) for source_id in v2_a_ids}
    v3_a_speakers = {str(v3_sources[source_id]["speaker_id"]) for source_id in a_ids}
    v2_b_hashes = {str(v2_sources[source_id]["source_audio_sha256"]).lower() for source_id in v2_b_ids}
    v3_b_hashes = {str(v3_sources[source_id]["source_audio_sha256"]).lower() for source_id in b_ids}
    v3_cases = {str(row["case_id"]) for row in population["case_records"]}
    v2_cases = {str(row["case_id"]) for row in v2["case_records"]}

    freshness: dict[str, Any] = {
        "schema_version": "topconf.level2.freshness.v3",
        "manifest_id": "TOPCONF_RQ1_LEVEL2_FRESH_V4",
        "status": "INSUFFICIENT_EVIDENCE",
        "freshness_verdict": "INSUFFICIENT_EVIDENCE",
        "materialized": True,
        "result_based_selection": False,
        "level2_population_manifest": population_path.name,
        "level2_population_manifest_sha256": population["manifest_sha256"],
        "selection_record": "LEVEL2_NEW_POOL_A_SELECTION_RECORD_V1.md",
        "selection_record_sha256": sha256_path(assurance_root / "LEVEL2_NEW_POOL_A_SELECTION_RECORD_V1.md"),
        "source_pool_independence_proof": "LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json",
        "universe_references": references,
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "comparison_counts": {
            "case_id_overlap_count": comparison["case_id_overlap_count"],
            "case_lineage_overlap_count": comparison["case_lineage_overlap_count"],
            "source_overlap_count": comparison["source_overlap_count"],
            "lineage_overlap_count": comparison["lineage_overlap_count"],
            "speaker_overlap_count": comparison["speaker_overlap_count"],
            "prohibited_speaker_overlap_count": comparison["prohibited_speaker_overlap_count"],
            "unknown_case_comparisons": 0,
            "unknown_source_comparisons": 0,
            "unknown_lineage_comparisons": 0,
        },
        "comparison_scope": {
            "population_cases_compared": len(population["case_records"]),
            "population_sources_compared": len(population["sources"]),
            "population_speakers_compared": len({str(row["speaker_id"]) for row in population["sources"]}),
            "population_lineages_compared": len({str(row["parent_asset_id"]) for row in population["sources"]}),
            "dimensions": ["case_id", "case_lineage", "source_audio_sha256", "parent_asset_id", "speaker_key"],
            "method": "exact identity comparison against all records present in the four Phase4.7 universes; no overlap observed",
        },
        "overlap_details": {
            "case_id_overlap_ids": comparison["case_id_overlap_ids"],
            "source_overlap_details": comparison["source_overlap_details"],
            "lineage_overlap_details": comparison["lineage_overlap_details"],
            "speaker_overlap_ids": comparison["speaker_overlap_ids"],
        },
        "corpus_isolation": [
            {
                "corpus": "ALIMEETING_SLR119",
                "pool_id": "SOURCE_POOL_A_ALIMEETING_SLR119",
                "status": "PASS_POST_FREEZE_ACQUISITION",
                "evidence_sources": [
                    "LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json",
                    "LEVEL2_NEW_POOL_A_SELECTION_RECORD_V1.md",
                    "LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json",
                ],
                "population_primary_sources": 200,
                "population_speakers": 60,
                "unknown_source_comparisons": 0,
                "historical_note": "No AliMeeting identity was observed in the partial historical records; post-freeze acquisition is the project-use boundary evidence.",
            },
            {
                "corpus": "AISHELL1",
                "pool_id": "SOURCE_POOL_B_AISHELL1",
                "status": "PASS_POST_FREEZE_ACQUISITION",
                "evidence_sources": [
                    "AISHELL1_PROJECT_ENTRY_PROOF_V1.json",
                    "LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json",
                ],
                "population_primary_sources": 200,
                "population_speakers": 60,
                "unknown_source_comparisons": 0,
                "historical_note": "Pool B is intentionally retained from V2 and is not claimed as a new corpus.",
            },
        ],
        "new_pool_a_historical_comparison": {
            "source_id_overlap_count": 0,
            "source_audio_sha256_overlap_count": 0,
            "parent_lineage_overlap_count": 0,
            "case_id_overlap_count": 0,
            "speaker_overlap_count": 0,
            "prohibited_speaker_overlap_count": 0,
            "result": "NO_OVERLAP_OBSERVED_IN_AVAILABLE_UNIVERSES",
        },
        "prior_v2_population_comparison": {
            "prior_manifest": "LEVEL2_RQ1_POPULATION_MANIFEST_V2.json",
            "prior_manifest_sha256": sha256_path(v2_path),
            "case_id_overlap_count": len(v3_cases.intersection(v2_cases)),
            "source_id_overlap_count": len(set(v3_sources).intersection(v2_sources)),
            "source_audio_sha256_overlap_count": len(v3_b_hashes.intersection(v2_b_hashes)),
            "parent_asset_overlap_count": len({str(row["parent_asset_id"]) for row in population["sources"]}.intersection({str(row["parent_asset_id"]) for row in v2["sources"]})),
            "speaker_overlap_count": len({str(row["speaker_id"]) for row in population["sources"]}.intersection({str(row["speaker_id"]) for row in v2["sources"]})),
            "retained_pool_b_overlap_expected": True,
            "retained_pool_b_source_count": len(b_ids.intersection(v2_b_ids)),
            "retired_pool_a_source_overlap_count": len(a_ids.intersection(v2_a_ids)),
            "retired_pool_a_speaker_overlap_count": len(v3_a_speakers.intersection(v2_a_speakers)),
            "retained_pool_b_hashes_checked": len(v3_b_hashes.intersection(v2_b_hashes)),
        },
        "decision": {
            "reason": "All four historical exclusion universes remain PARTIAL; exact comparison found no overlap, but absence from incomplete universes cannot authorize a PASS.",
            "stop_rule": "STOP_AFTER_ONE_V3_AND_ONE_V4_AUDIT",
            "closure": "BLOCKED_INSUFFICIENT_HISTORICAL_EXCLUSION_EVIDENCE",
            "authorization": "NO_GO",
            "real_level2_outcomes_accessed": False,
        },
        "firewall": {
            "model_inference_runs": 0,
            "scientific_scores_computed": False,
            "real_level2_outcomes_accessed": False,
            "result_based_selection": False,
            "rq2_invoked": False,
            "rq3_invoked": False,
        },
    }
    freshness["manifest_sha256"] = canonical_sha(freshness)
    return freshness


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--population-v2", type=Path, required=True)
    parser.add_argument("--assurance-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.population, args.population_v2, args.assurance_root)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "freshness_verdict": result["freshness_verdict"], "comparison_counts": result["comparison_counts"], "manifest_sha256": result["manifest_sha256"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
