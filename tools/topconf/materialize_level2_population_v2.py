"""Materialize a metadata-only Level-2 population candidate from audited pools.

This script performs deterministic source selection and identity binding only.
It does not load waveform samples, checkpoints, predictions, labels, or
scientific outcomes.  The resulting V2 population is deliberately paired with
an insufficient-evidence freshness manifest until the historical exclusion
universe is complete.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import tarfile
import wave


FROZEN_PLAN = {
    "independent_source_pools": 2,
    "primary_sources": 400,
    "speakers": 120,
    "sources_per_pool": 200,
    "speakers_per_pool": 60,
    "mechanisms_per_source": 4,
    "predeclared_source_reserve": 40,
    "target_duration_sec": [8, 30],
}
MECHANISMS = (
    "splice_crossfade_control",
    "conventional_tts",
    "voice_conditioned_tts_vc",
    "neural_edit_infilling",
)
SPLITS = ("TRAIN", "DEV", "CALIBRATION", "HELDOUT")
AISHELL3_ARCHIVE_SHA256 = "BE2507D431AD59419EC871E60674CAEDB2B585F84FFA01FE359784686DB0E0CC"


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical_sha256(payload: object) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha256_bytes(rendered.encode("utf-8"))


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_aishell3(raw_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for split in ("train", "test"):
        content_path = raw_root / split / "content.txt"
        for line in content_path.read_text(encoding="utf-8").splitlines():
            fields = line.split("\t", 1)
            if len(fields) != 2:
                continue
            utterance_id, text = fields[0].strip(), fields[1].strip()
            audio_path = raw_root / split / "wav" / utterance_id[:7] / utterance_id
            if not audio_path.is_file():
                continue
            with wave.open(str(audio_path), "rb") as handle:
                channels = handle.getnchannels()
                sample_rate = handle.getframerate()
                sample_width = handle.getsampwidth()
                duration = handle.getnframes() / sample_rate if sample_rate else 0.0
            if not (
                8.0 <= duration <= 30.0
                and channels == 1
                and sample_width == 2
            ):
                continue
            speaker = audio_path.parent.name
            audio_sha = _sha256_path(audio_path)
            rows.append(
                {
                    "corpus": "AISHELL3",
                    "speaker_raw": speaker,
                    "speaker_id": f"AISHELL3_{speaker}",
                    "session_id": f"AISHELL3_RELEASE_SPEAKER_{speaker}",
                    "utterance_id": utterance_id.removesuffix(".wav"),
                    "text_sha256": _sha256_bytes(text.encode("utf-8")),
                    "source_audio_sha256": audio_sha,
                    "source_audio_path": str(audio_path),
                    "audio_size_bytes": audio_path.stat().st_size,
                    "sample_rate_hz": sample_rate,
                    "channels": channels,
                    "format": "WAV_PCM16_MONO",
                    "duration_sec": duration,
                    "corpus_split": split,
                    "parent_asset_id": f"AISHELL3_ARCHIVE_{AISHELL3_ARCHIVE_SHA256}_{utterance_id.removesuffix('.wav')}",
                }
            )
    return sorted(rows, key=lambda row: (str(row["speaker_id"]), str(row["utterance_id"])))


def _inner_member_name(row: dict[str, object]) -> str:
    path = Path(str(row["path"]))
    # The nested AISHELL-1 speaker archive stores members under train/dev/test.
    # The audit label starts at data_aishell/wav/<split>/..., so retain the
    # split component for tarfile lookup.
    return "/".join(path.parts[2:])


def _read_aishell1(audit_path: Path, extracted_root: Path) -> list[dict[str, object]]:
    audit = _load_json(audit_path)
    archive = dict(audit["official_audio_archive"])
    archive_sha = str(archive["observed_archive_sha256"])
    rows: list[dict[str, object]] = []
    for item in audit["records"]:
        if not item.get("eligible_under_frozen_filter") or not item.get("transcript_present"):
            continue
        path_label = str(item["path"])
        path_parts = Path(path_label).parts
        speaker_raw = str(item["speaker_id"])
        archive_path = extracted_root / "data_aishell" / "wav" / f"S{speaker_raw}.tar.gz"
        member_name = _inner_member_name(item)
        if not archive_path.is_file():
            raise FileNotFoundError(f"missing AISHELL-1 speaker archive: {archive_path}")
        rows.append(
            {
                "corpus": "AISHELL1",
                "speaker_raw": speaker_raw,
                "speaker_id": f"AISHELL1_S{speaker_raw}",
                "session_id": f"AISHELL1_RELEASE_SPEAKER_S{speaker_raw}",
                "utterance_id": str(item["utterance_id"]),
                "text_sha256": str(item["text_sha256"]),
                "source_audio_sha256": str(item["source_audio_sha256"]),
                "source_audio_path": f"{archive_path}::{member_name}",
                "audio_size_bytes": int(item["audio_size_bytes"]),
                "sample_rate_hz": int(item["sample_rate"]),
                "channels": int(item["channels"]),
                "format": "WAV_PCM16_MONO",
                "duration_sec": float(item["duration_sec"]),
                "corpus_split": str(item["split"]),
                "parent_asset_id": f"AISHELL1_ARCHIVE_{archive_sha}_{str(item['utterance_id'])}",
                "archive_path": str(archive_path),
                "member_name": member_name,
            }
        )
    return sorted(rows, key=lambda row: (str(row["speaker_id"]), str(row["utterance_id"])))


def _select_rows(
    rows: list[dict[str, object]],
    *,
    source_prefix: str,
    pool_id: str,
    primary_count: int = 200,
    speaker_count: int = 60,
    reserve_count: int = 20,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str]]:
    by_speaker: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_speaker[str(row["speaker_id"])].append(row)
    ranked_speakers = sorted(
        by_speaker,
        key=lambda speaker: (-len(by_speaker[speaker]), speaker),
    )
    selected_speakers = ranked_speakers[:speaker_count]
    if len(selected_speakers) != speaker_count:
        raise ValueError(f"{pool_id}: only {len(selected_speakers)} eligible speakers")
    for speaker in selected_speakers:
        by_speaker[speaker].sort(key=lambda row: str(row["utterance_id"]))

    primary: list[dict[str, object]] = []
    cursor = 0
    while len(primary) < primary_count:
        added = False
        for speaker in selected_speakers:
            if cursor < len(by_speaker[speaker]):
                primary.append(by_speaker[speaker][cursor])
                added = True
                if len(primary) == primary_count:
                    break
        if not added:
            raise ValueError(f"{pool_id}: insufficient sources for primary allocation")
        cursor += 1

    used = {str(row["utterance_id"]) for row in primary}
    reserve_candidates = [row for row in rows if str(row["utterance_id"]) not in used]
    reserve_candidates.sort(
        key=lambda row: (str(row["speaker_id"]) not in selected_speakers, str(row["speaker_id"]), str(row["utterance_id"]))
    )
    if len(reserve_candidates) < reserve_count:
        raise ValueError(f"{pool_id}: insufficient sources for reserve allocation")
    reserve = reserve_candidates[:reserve_count]

    def decorate(source_rows: list[dict[str, object]], label: str) -> list[dict[str, object]]:
        result = []
        for index, row in enumerate(source_rows, 1):
            item = dict(row)
            item["source_id"] = f"{source_prefix}-{label}-{index:04d}"
            item["pool_id"] = pool_id
            item["data_role"] = "LEVEL2_CONFIRMATORY_POPULATION"
            result.append(item)
        return result

    return decorate(primary, "SRC"), decorate(reserve, "RESERVE"), selected_speakers


def _materialize_cases(sources: list[dict[str, object]]) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    speakers_by_pool: dict[str, list[str]] = defaultdict(list)
    for source in sources:
        pool_id = str(source["pool_id"])
        speaker_id = str(source["speaker_id"])
        if speaker_id not in speakers_by_pool[pool_id]:
            speakers_by_pool[pool_id].append(speaker_id)
    split_by_speaker = {
        speaker_id: f"{pool_id.replace('SOURCE_POOL_', '')}_{SPLITS[index // 15]}"
        for pool_id, pool_speakers in speakers_by_pool.items()
        for index, speaker_id in enumerate(sorted(pool_speakers))
    }
    for source_index, source in enumerate(sources, 1):
        split = split_by_speaker[str(source["speaker_id"])]
        source["split"] = split
        pair_id = f"PAIR-{source_index:04d}"
        for mechanism_index, mechanism in enumerate(MECHANISMS, 1):
            generation_seed = 20260915_000000 + source_index * 10 + mechanism_index
            transform_seed = 20260915_100000 + source_index * 10 + mechanism_index
            case_id = f"CASE-{source_index:04d}-M{mechanism_index:02d}"
            input_identity = _canonical_sha256(
                {
                    "source_audio_sha256": source["source_audio_sha256"],
                    "text_sha256": source["text_sha256"],
                    "mechanism_id": mechanism,
                    "transform_condition": "CLEAN",
                    "generator_id": "FROZEN_LEVEL2_GENERATOR_PLACEHOLDER",
                    "generator_version": "UNEXECUTED",
                    "generation_seed": generation_seed,
                    "transform_seed": transform_seed,
                }
            )
            cases.append(
                {
                    "case_id": case_id,
                    "pair_id": pair_id,
                    "source_id": source["source_id"],
                    "speaker_id": source["speaker_id"],
                    "session_id": source["session_id"],
                    "utterance_id": source["utterance_id"],
                    "reference_audio_id": None,
                    "text_sha256": source["text_sha256"],
                    "parent_asset_id": source["parent_asset_id"],
                    "source_audio_sha256": source["source_audio_sha256"],
                    "mechanism_id": mechanism,
                    "transform_condition": "CLEAN",
                    "target_position": 0.0,
                    "target_duration_sec": source["duration_sec"],
                    "generator_input_identity": input_identity,
                    "generator_id": "FROZEN_LEVEL2_GENERATOR_PLACEHOLDER",
                    "generator_version": "UNEXECUTED",
                    "generation_seed": generation_seed,
                    "transform_seed": transform_seed,
                    "data_role": "LEVEL2_CONFIRMATORY_POPULATION",
                    "split": split,
                }
            )
    return sorted(cases, key=lambda row: str(row["case_id"]))


def _historical_freshness(
    population: dict[str, object],
    historical_path: Path,
) -> dict[str, object]:
    historical = _load_json(historical_path)
    stages = historical.get("stages", [])
    by_id = {str(stage.get("set_id")): stage for stage in stages if isinstance(stage, dict)}
    required = [
        "WEEK1_PILOT", "WEEK2_PILOT", "WEEK3_PILOT", "WEEK4_PILOT",
        "WEEK5_QUALIFICATION", "PHASE3T_PARTIALEDIT_E1", "MODEL_SELECTION_SETS",
        "METRIC_SELECTION_SETS", "THRESHOLD_SELECTION_SETS", "WHETHER_A_DECISION_SET",
        "WHETHER_B_CAPABILITY_SMOKE",
    ]
    exclusion_sets = []
    set_hashes: dict[str, str | None] = {}
    for set_id in required:
        stage = by_id.get(set_id, {})
        records = stage.get("records", []) if isinstance(stage, dict) else []
        completeness = str(stage.get("completeness", "UNKNOWN")) if isinstance(stage, dict) else "UNKNOWN"
        status = "COMPLETE_EXCLUSION_EMPTY" if set_id == "WHETHER_B_CAPABILITY_SMOKE" and completeness == "COMPLETE" else (
            "COMPLETE" if completeness == "COMPLETE" else "INCOMPLETE_NOT_RECONSTRUCTED"
        )
        manifest_hash = _canonical_sha256({"set_id": set_id, "records": records})
        set_hashes[set_id] = manifest_hash
        exclusion_sets.append(
            {
                "set_id": set_id,
                "status": status,
                "manifest_sha256": manifest_hash,
                "identity_dimensions": [],
                "records": records if status == "COMPLETE" else [],
                "evidence_source": stage.get("evidence", []) if isinstance(stage, dict) else [],
            }
        )
    dimensions = [
        "case_id", "pair_id", "source_id", "speaker_id", "session_id",
        "utterance_id", "reference_audio_id", "text_sha256", "parent_asset_id",
        "source_audio_sha256", "generator_input_identity",
    ]
    return {
        "schema_version": "topconf.level2.freshness.v1",
        "manifest_id": "TOPCONF_RQ1_LEVEL2_FRESH_V2",
        "status": "BLOCKED_INSUFFICIENT_EVIDENCE",
        "freshness_verdict": "INSUFFICIENT_EVIDENCE",
        "materialized": True,
        "source_corpus_identity_frozen": False,
        "real_level2_outcomes_accessed": False,
        "result_based_selection": False,
        "level2_population_manifest": "LEVEL2_RQ1_POPULATION_MANIFEST_V2.json",
        "level2_population_manifest_sha256": population["manifest_sha256"],
        "exclusion_universe_manifest": historical_path.name,
        "exclusion_universe_manifest_sha256": _sha256_path(historical_path),
        "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
        "comparison_dimensions": dimensions,
        "required_exclusion_sets": required,
        "all_historical_exclusion_set_hashes": set_hashes,
        "exclusion_sets": exclusion_sets,
        "overlap_counts": {dimension: None for dimension in dimensions},
        "policy": {
            "speaker_overlap_policy": "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT",
            "case_overlap": "PROHIBITED",
            "source_overlap": "PROHIBITED",
            "lineage_overlap": "PROHIBITED",
            "selection_data_overlap": "PROHIBITED",
            "capability_smoke_source_ids": [],
            "freshness_claim": "NO_PASS_CLAIM; HISTORICAL_EXCLUSION_UNIVERSE_INCOMPLETE",
        },
        "authorization_gate": "NO_AUTHORIZATION_UNTIL_MATERIALIZED_POPULATION_AND_FRESHNESS_PROOF_PASS",
        "firewall": {
            "model_inference_runs": 0,
            "scientific_scores_computed": False,
            "real_level2_outcomes_accessed": False,
            "result_based_design_changes": 0,
            "authorization": "NO_GO",
        },
    }


def build(args: argparse.Namespace) -> tuple[dict[str, object], dict[str, object]]:
    aishell1_audit = _load_json(args.aishell1_audit)
    aishell1_rows = _read_aishell1(args.aishell1_audit, args.aishell1_root)
    aishell3_rows = _read_aishell3(args.aishell3_root)
    a_sources, a_reserve, a_speakers = _select_rows(
        aishell3_rows,
        source_prefix="AISHELL3",
        pool_id="SOURCE_POOL_A_AISHELL3",
    )
    b_sources, b_reserve, b_speakers = _select_rows(
        aishell1_rows,
        source_prefix="AISHELL1",
        pool_id="SOURCE_POOL_B_AISHELL1",
    )
    sources = a_sources + b_sources
    reserves = a_reserve + b_reserve
    cases = _materialize_cases(sources)
    for source in reserves:
        source.pop("archive_path", None)
        source.pop("member_name", None)
        source["split"] = f"{str(source['pool_id']).replace('SOURCE_POOL_', '')}_RESERVE"

    def pool_record(pool_id: str, pool_sources: list[dict[str, object]], speakers: list[str]) -> dict[str, object]:
        source_ids = [str(row["source_id"]) for row in pool_sources]
        speaker_ids = sorted({str(row["speaker_id"]) for row in pool_sources})
        return {
            "pool_id": pool_id,
            "source_count": len(source_ids),
            "speaker_count": len(speaker_ids),
            "source_ids": source_ids,
            "speaker_ids": speaker_ids,
            "manifest_sha256": _canonical_sha256({"pool_id": pool_id, "source_ids": source_ids, "speaker_ids": speaker_ids}),
            "selection_speaker_ranking": "eligible speaker count descending, speaker ID ascending; metadata-only",
        }

    mechanism_counts = Counter(row["mechanism_id"] for row in cases)
    population: dict[str, object] = {
        "schema_version": "topconf.level2.rq1.population.v1",
        "manifest_id": "TOPCONF_RQ1_LEVEL2_POPULATION_V2",
        "materialization_iteration": "V2",
        "status": "MATERIALIZED",
        "materialized": True,
        "population_claim": True,
        "source_corpus_identity_frozen": False,
        "amendment_required": False,
        "authorization": "NO_GO",
        "freshness_status": "BLOCKED_INSUFFICIENT_HISTORICAL_EXCLUSION",
        "real_level2_outcomes_accessed": False,
        "result_based_selection": False,
        "protocol_id": "P4-RQ1-DESIGN-20260914-01",
        "frozen_plan": FROZEN_PLAN,
        "selection_method": {
            "model_free": True,
            "primary_rule": "deterministic round-robin within the 60 highest-count eligible speakers per corpus, after corpus-level frozen filtering",
            "transcript_rule": "eligible source must have a transcript row; 11 AISHELL-1 eligible WAVs without transcript are excluded",
            "split_rule": "speaker-block assignment to four deterministic split labels; no speaker crosses split",
            "reserve_rule": "20 unused deterministic records per pool, never expanded into primary counts",
        },
        "counts": {
            "population_size": len(sources),
            "source_count": len(sources),
            "speaker_count": len({row["speaker_id"] for row in sources}),
            "pair_count": len(sources),
            "case_count": len(cases),
            "mechanism_counts": dict(mechanism_counts),
            "transform_counts": {"CLEAN": len(cases)},
        },
        "source_pools": [
            pool_record("SOURCE_POOL_A_AISHELL3", a_sources, a_speakers),
            pool_record("SOURCE_POOL_B_AISHELL1", b_sources, b_speakers),
        ],
        "sources": [
            {key: value for key, value in row.items() if key not in {"corpus_split", "speaker_raw", "archive_path", "member_name", "data_role"}}
            for row in sources
        ],
        "reserve_records": [
            {key: value for key, value in row.items() if key not in {"corpus_split", "speaker_raw", "archive_path", "member_name", "data_role"}}
            for row in reserves
        ],
        "case_records": cases,
        "case_order": [str(row["case_id"]) for row in cases],
        "audio_materialized": False,
        "resource_inventory": [
            {
                "resource_id": "AISHELL3_LOCAL",
                "root": str(args.aishell3_root),
                "role": "HISTORICAL_CANDIDATE_POOL_A",
                "archive_sha256": AISHELL3_ARCHIVE_SHA256,
                "eligible_8_30_wav_files": len(aishell3_rows),
                "eligible_8_30_speakers": len({row["speaker_id"] for row in aishell3_rows}),
            },
            {
                "resource_id": "AISHELL1_LOCAL_OFFICIAL_SLR33",
                "root": str(args.aishell1_root),
                "role": "RECOVERED_CANDIDATE_POOL_B",
                "archive_sha256": str(aishell1_audit["official_audio_archive"]["observed_archive_sha256"]),
                "eligible_8_30_transcript_complete_files": len(aishell1_rows),
                "eligible_8_30_transcript_complete_speakers": len({row["speaker_id"] for row in aishell1_rows}),
                "eligible_wav_without_transcript_excluded": 11,
            },
        ],
        "excluded_lineages": [
            "WEEK1_5_HISTORICAL_PILOT",
            "PHASE3T_PARTIALEDIT_V1.1_E1",
            "ANY_LEVEL1_MODEL_SELECTION_SET",
            "ANY_LEVEL1_METRIC_SELECTION_SET",
            "ANY_LEVEL1_THRESHOLD_CALIBRATION_TEST_SET",
            "WHETHER_B_CAPABILITY_SMOKE_SOURCE_IDS",
        ],
        "firewall": {
            "model_inference_runs": 0,
            "scientific_scores_computed": False,
            "real_level2_outcomes_accessed": False,
            "result_based_design_changes": 0,
            "authorization": "NO_GO",
        },
    }
    population["manifest_sha256"] = _canonical_sha256(population)
    freshness = _historical_freshness(population, args.historical)
    return population, freshness


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aishell3-root", type=Path, required=True)
    parser.add_argument("--aishell1-root", type=Path, required=True)
    parser.add_argument("--aishell1-audit", type=Path, required=True)
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--population-output", type=Path, required=True)
    parser.add_argument("--freshness-output", type=Path, required=True)
    args = parser.parse_args()
    population, freshness = build(args)
    args.population_output.write_text(json.dumps(population, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.freshness_output.write_text(json.dumps(freshness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "MATERIALIZED_CANDIDATE_NOT_AUTHORIZING",
        "population_sha256": population["manifest_sha256"],
        "population_counts": population["counts"],
        "freshness_status": freshness["status"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
