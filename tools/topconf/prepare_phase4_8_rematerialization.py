"""Prepare exactly one outcome-blind V2-to-V3 remediation attempt.

The command audits the frozen V2 primary/reserve membership and the frozen
Phase4.7 contamination evidence.  It writes an explicit exclusion set and a
replacement ledger.  If the same-pool clean reserve is insufficient it stops
without creating a V3 population.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


RULE_ID = "LEVEL2_RESERVE_ACTIVATION_RULE_V1"
TRIGGER = "VERIFIED_FRESHNESS_CONTAMINATION"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _canonical_sha256(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest().upper()


def _reserve_key(row: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(row.get("corpus") or row.get("dataset") or ""),
        str(row.get("speaker_id") or ""),
        str(row.get("utterance_id") or ""),
        str(row.get("source_id") or ""),
        str(row.get("source_audio_sha256") or "").lower(),
        str(row.get("parent_asset_id") or ""),
    )


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    out = args.output_dir
    v2_path = out / "LEVEL2_RQ1_POPULATION_MANIFEST_V2.json"
    freshness_path = out / "LEVEL2_FRESHNESS_MANIFEST_V3.json"
    source_universe_path = out / "HISTORICAL_SOURCE_EXCLUSION_UNIVERSE_V3.json"
    lineage_universe_path = out / "HISTORICAL_LINEAGE_EXCLUSION_UNIVERSE_V1.json"
    v2 = _load(v2_path)
    freshness = _load(freshness_path)
    source_universe = _load(source_universe_path)
    lineage_universe = _load(lineage_universe_path)
    v2_hash = _sha256(v2_path)

    direct_overlaps = freshness.get("overlap_details", {}).get("source_overlap_details", [])
    direct_sources = sorted({str(row["population_source_id"]) for row in direct_overlaps})
    direct_hashes = sorted({
        str(row["source_audio_sha256"]).lower()
        for row in direct_overlaps
        if isinstance(row.get("source_audio_sha256"), str)
    })
    prohibited_speakers = sorted({
        str(row["population_speaker_id"])
        for row in direct_overlaps
        if isinstance(row.get("population_speaker_id"), str)
    })
    if direct_sources != [
        "AISHELL3-SRC-0001", "AISHELL3-SRC-0036", "AISHELL3-SRC-0061",
        "AISHELL3-SRC-0121", "AISHELL3-SRC-0181",
    ]:
        raise ValueError("Phase4.7 direct contamination evidence changed")
    if len(prohibited_speakers) != 2:
        raise ValueError("Phase4.7 prohibited speaker evidence changed")

    sources = [dict(row) for row in v2["sources"]]
    cases = [dict(row) for row in v2["case_records"]]
    cases_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cases:
        cases_by_source[str(row["source_id"])].append(row)
    contaminated_sources = sorted(
        (row for row in sources if str(row.get("speaker_id")) in prohibited_speakers),
        key=lambda row: str(row["source_id"]),
    )
    contaminated_source_ids = [str(row["source_id"]) for row in contaminated_sources]
    contaminated_case_ids = sorted({
        str(case["case_id"])
        for source_id in contaminated_source_ids
        for case in cases_by_source[source_id]
    })
    if len(contaminated_source_ids) != 7 or len(contaminated_case_ids) != 28:
        raise ValueError("unexpected all-membership speaker contamination cardinality")

    historical_source_hashes = {
        str(row["source_audio_sha256"]).lower()
        for row in source_universe.get("records", [])
        if isinstance(row, dict) and isinstance(row.get("source_audio_sha256"), str)
    }
    historical_lineage_hashes = {
        str(row["source_audio_sha256"]).lower()
        for row in lineage_universe.get("records", [])
        if isinstance(row, dict) and isinstance(row.get("source_audio_sha256"), str)
    }
    historical_parent_assets = {
        str(row["parent_asset_id"])
        for row in lineage_universe.get("records", [])
        if isinstance(row, dict) and isinstance(row.get("parent_asset_id"), str)
    }

    reserves = [dict(row) for row in v2["reserve_records"]]
    ordered_reserves = sorted(reserves, key=_reserve_key)
    reserve_ranks = {str(row["source_id"]): index for index, row in enumerate(ordered_reserves, 1)}
    reserve_audit: list[dict[str, Any]] = []
    clean_by_pool: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ordered_reserves:
        speaker = str(row.get("speaker_id") or "")
        audio_hash = str(row.get("source_audio_sha256") or "").lower()
        parent_asset = str(row.get("parent_asset_id") or "")
        metadata_qualified = all(
            row.get(field) not in (None, "")
            for field in (
                "source_id", "speaker_id", "session_id", "utterance_id",
                "text_sha256", "parent_asset_id", "source_audio_sha256",
                "source_audio_path", "audio_size_bytes", "sample_rate_hz",
                "channels", "format", "duration_sec", "pool_id", "split",
            )
        ) and 8 <= float(row["duration_sec"]) <= 30
        speaker_allowed = speaker not in prohibited_speakers
        source_disjoint = audio_hash not in historical_source_hashes
        lineage_disjoint = audio_hash not in historical_lineage_hashes and parent_asset not in historical_parent_assets
        clean = metadata_qualified and speaker_allowed and source_disjoint and lineage_disjoint
        pool_id = str(row["pool_id"])
        if clean:
            clean_by_pool[pool_id].append(row)
        reserve_audit.append({
            "source_id": row["source_id"],
            "pool_id": pool_id,
            "speaker_id": row["speaker_id"],
            "reserve_rank": reserve_ranks[str(row["source_id"])],
            "metadata_qualified_from_frozen_v2": metadata_qualified,
            "speaker_allowed": speaker_allowed,
            "source_lineage_disjoint": source_disjoint,
            "parent_lineage_disjoint": lineage_disjoint,
            "eligible_clean_same_pool_reserve": clean,
        })

    excluded_parent_assets = sorted({
        str(row["parent_asset_id"]) for row in contaminated_sources
    })
    exclusion = {
        "schema_version": "topconf.level2.v2.contamination_exclusion.v1",
        "status": "VERIFIED_CONTAMINATION_EXCLUSION",
        "reason": TRIGGER,
        "parent_population_version": "V2",
        "parent_population_manifest": v2_path.name,
        "parent_population_sha256": v2_hash,
        "historical_freshness_manifest": freshness_path.name,
        "direct_verified_overlap_source_ids": direct_sources,
        "direct_verified_overlap_records": direct_overlaps,
        "excluded_speaker_ids": prohibited_speakers,
        "excluded_source_ids": contaminated_source_ids,
        "excluded_case_ids": contaminated_case_ids,
        "excluded_source_audio_sha256s": sorted({
            str(row["source_audio_sha256"]).lower() for row in contaminated_sources
        }),
        "excluded_parent_asset_ids": excluded_parent_assets,
        "historical_evidence_sources": sorted({
            source
            for overlap in direct_overlaps
            for match in overlap.get("historical_matches", [])
            for source in match.get("evidence_sources", [])
        }),
        "contamination_expansion_policy": "exclude_all_V2_membership_of_prohibited_speakers",
        "affected_primary_source_count": len(contaminated_source_ids),
        "affected_case_count": len(contaminated_case_ids),
        "scientific_outcomes_accessed": False,
        "model_inference_runs": 0,
        "result_based_selection": False,
    }
    exclusion_path = out / "LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json"
    _write(exclusion_path, exclusion)

    required_by_pool = CounterLike()
    for row in contaminated_sources:
        required_by_pool.add(str(row["pool_id"]))
    clean_same_pool_count = sum(len(clean_by_pool[pool_id]) for pool_id in required_by_pool.keys())
    blocked = clean_same_pool_count < len(contaminated_sources)
    entries: list[dict[str, Any]] = []
    for row in contaminated_sources:
        source_id = str(row["source_id"])
        entries.append({
            "old_source_id": source_id,
            "old_speaker_id": row["speaker_id"],
            "old_pool_id": row["pool_id"],
            "old_case_ids": sorted(str(case["case_id"]) for case in cases_by_source[source_id]),
            "exclusion_reason": TRIGGER,
            "replacement_source_id": None,
            "replacement_speaker_id": None,
            "reserve_rank": None,
            "activation_rule": RULE_ID,
            "new_case_ids": [],
            "scientific_outcome_consulted": False,
        })
    ledger = {
        "schema_version": "topconf.level2.v2_to_v3.replacement_ledger.v1",
        "status": "BLOCKED_INSUFFICIENT_CLEAN_RESERVE" if blocked else "READY_FOR_V3_MATERIALIZATION",
        "parent_population_version": "V2",
        "parent_population_manifest": v2_path.name,
        "parent_population_sha256": v2_hash,
        "contamination_exclusion_manifest": exclusion_path.name,
        "contamination_exclusion_sha256": _sha256(exclusion_path),
        "activation_rule_id": RULE_ID,
        "activation_trigger": TRIGGER,
        "activation_is_result_independent": True,
        "required_replacements": len(contaminated_sources),
        "required_replacements_by_pool": dict(required_by_pool.items()),
        "reserve_counts_by_pool": {pool: len(rows) for pool, rows in clean_by_pool.items()},
        "clean_same_pool_reserve_count": clean_same_pool_count,
        "activated_reserve_source_ids": [],
        "reserve_audit": reserve_audit,
        "entries": entries,
        "rematerialized_population_created": False,
        "scientific_outcome_consulted": False,
        "model_inference_runs": 0,
        "result_based_design_changes": 0,
    }
    return exclusion, ledger


class CounterLike:
    def __init__(self) -> None:
        self._values: dict[str, int] = {}

    def add(self, key: str) -> None:
        self._values[key] = self._values.get(key, 0) + 1

    def keys(self):
        return self._values.keys()

    def items(self):
        return self._values.items()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    exclusion, ledger = build(args)
    ledger_path = args.output_dir / "LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json"
    _write(ledger_path, ledger)
    print(json.dumps({
        "status": ledger["status"],
        "excluded_speakers": exclusion["excluded_speaker_ids"],
        "excluded_sources": exclusion["excluded_source_ids"],
        "excluded_cases": len(exclusion["excluded_case_ids"]),
        "clean_same_pool_reserve_count": ledger["clean_same_pool_reserve_count"],
        "required_replacements": ledger["required_replacements"],
        "exclusion_manifest": str(args.output_dir / "LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json"),
        "replacement_ledger": str(ledger_path),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
