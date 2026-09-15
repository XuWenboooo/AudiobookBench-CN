"""Fail-closed validation for the frozen Level-2 population boundary.

This module validates identity and governance metadata only.  It never loads
audio, checkpoints, predictions, labels, or scientific outcomes.  A blocked
or incomplete manifest is deliberately not treated as an empty valid cohort.
"""

from __future__ import annotations

from collections import Counter
import math
import re
from typing import Any, Iterable, Mapping


HEX64 = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)

FROZEN_LEVEL2_PLAN = {
    "independent_source_pools": 2,
    "primary_sources": 400,
    "speakers": 120,
    "sources_per_pool": 200,
    "speakers_per_pool": 60,
    "mechanisms_per_source": 4,
    "predeclared_source_reserve": 40,
    "target_duration_sec": [8.0, 30.0],
}

SOURCE_FIELDS = (
    "source_id",
    "speaker_id",
    "session_id",
    "utterance_id",
    "text_sha256",
    "parent_asset_id",
    "source_audio_sha256",
    "source_audio_path",
    "audio_size_bytes",
    "sample_rate_hz",
    "channels",
    "format",
    "duration_sec",
    "pool_id",
    "split",
)

CASE_FIELDS = (
    "case_id",
    "pair_id",
    "source_id",
    "speaker_id",
    "session_id",
    "utterance_id",
    "reference_audio_id",
    "text_sha256",
    "parent_asset_id",
    "source_audio_sha256",
    "mechanism_id",
    "transform_condition",
    "target_position",
    "target_duration_sec",
    "generator_input_identity",
    "generator_id",
    "generator_version",
    "generation_seed",
    "transform_seed",
    "data_role",
    "split",
)

FRESHNESS_DIMENSIONS = (
    "case_id",
    "pair_id",
    "source_id",
    "speaker_id",
    "session_id",
    "utterance_id",
    "reference_audio_id",
    "text_sha256",
    "parent_asset_id",
    "source_audio_sha256",
    "generator_input_identity",
)

INFERENCE_FORBIDDEN_FIELDS = frozenset(
    {
        "target_start_sec",
        "target_end_sec",
        "ground_truth",
        "label",
        "mechanism_id",
        "source_id",
        "speaker_id",
        "session_id",
        "utterance_id",
        "reference_audio_id",
        "parent_asset_id",
        "text_sha256",
        "generator_input_identity",
        "generator_id",
        "generator_version",
        "terminal_category",
        "failure_status",
        "scientific_outcome",
        "prediction",
        "score",
    }
)


class MaterializationValidationError(ValueError):
    """Raised when a population or view violates the identity contract."""


class FreshnessValidationError(ValueError):
    """Raised when a freshness claim is contradicted by the evidence."""


class FreshnessInsufficientEvidence(FreshnessValidationError):
    """Raised when a freshness decision cannot be made from available data."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MaterializationValidationError(f"missing required metadata: {field}")
    return value


def _hash(value: Any, field: str) -> str:
    value = _text(value, field)
    if not HEX64.fullmatch(value):
        raise MaterializationValidationError(f"invalid SHA256: {field}")
    return value.lower()


def _finite(value: Any, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise MaterializationValidationError(f"invalid number: {field}") from exc
    if not math.isfinite(parsed):
        raise MaterializationValidationError(f"invalid number: {field}")
    return parsed


def _records(manifest: Mapping[str, Any], field: str) -> list[dict[str, Any]]:
    value = manifest.get(field)
    if not isinstance(value, list) or not all(isinstance(row, Mapping) for row in value):
        raise MaterializationValidationError(f"missing or invalid {field}")
    return [dict(row) for row in value]


def _expected_plan(expected_plan: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(FROZEN_LEVEL2_PLAN)
    if expected_plan is not None:
        merged.update(expected_plan)
    return merged


def _require_fields(row: Mapping[str, Any], fields: Iterable[str], prefix: str) -> None:
    for field in fields:
        if field not in row:
            raise MaterializationValidationError(f"missing required metadata: {prefix}.{field}")


def _unique(rows: Iterable[Mapping[str, Any]], field: str, label: str) -> set[str]:
    values = [_text(row.get(field), f"{label}.{field}") for row in rows]
    if len(values) != len(set(values)):
        raise MaterializationValidationError(f"duplicate {label}: {field}")
    return set(values)


def _validate_source_row(row: Mapping[str, Any], prefix: str) -> None:
    _require_fields(row, SOURCE_FIELDS, prefix)
    for field in (
        "source_id",
        "speaker_id",
        "session_id",
        "utterance_id",
        "parent_asset_id",
        "source_audio_path",
        "pool_id",
        "split",
        "format",
    ):
        _text(row[field], f"{prefix}.{field}")
    _hash(row["text_sha256"], f"{prefix}.text_sha256")
    _hash(row["source_audio_sha256"], f"{prefix}.source_audio_sha256")
    if _finite(row["duration_sec"], f"{prefix}.duration_sec") <= 0:
        raise MaterializationValidationError(f"non-positive duration: {prefix}")
    if int(row["audio_size_bytes"]) <= 0:
        raise MaterializationValidationError(f"non-positive audio size: {prefix}")
    if int(row["sample_rate_hz"]) <= 0 or int(row["channels"]) <= 0:
        raise MaterializationValidationError(f"invalid audio format metadata: {prefix}")


def _validate_case_row(
    row: Mapping[str, Any],
    prefix: str,
    source: Mapping[str, Any],
    duration_bounds: tuple[float, float],
) -> None:
    _require_fields(row, CASE_FIELDS, prefix)
    for field in (
        "case_id",
        "pair_id",
        "source_id",
        "speaker_id",
        "session_id",
        "utterance_id",
        "mechanism_id",
        "transform_condition",
        "generator_input_identity",
        "generator_id",
        "generator_version",
        "data_role",
        "split",
    ):
        _text(row[field], f"{prefix}.{field}")
    if row["data_role"] != "LEVEL2_CONFIRMATORY_POPULATION":
        raise MaterializationValidationError(f"wrong data role: {prefix}.data_role")
    if row["source_id"] != source["source_id"]:
        raise MaterializationValidationError(f"case/source mismatch: {prefix}.source_id")
    for field in ("speaker_id", "session_id", "utterance_id", "parent_asset_id", "source_audio_sha256", "text_sha256"):
        expected = source[field]
        observed = row[field]
        if observed != expected:
            raise MaterializationValidationError(f"case/source binding mismatch: {prefix}.{field}")
    if row["split"] != source["split"]:
        raise MaterializationValidationError(f"case/source split mismatch: {prefix}.split")
    if row["reference_audio_id"] is not None:
        _text(row["reference_audio_id"], f"{prefix}.reference_audio_id")
    for field in ("generation_seed", "transform_seed"):
        if not isinstance(row[field], int) or isinstance(row[field], bool):
            raise MaterializationValidationError(f"seed must be an integer: {prefix}.{field}")
    target_position = _finite(row["target_position"], f"{prefix}.target_position")
    target_duration = _finite(row["target_duration_sec"], f"{prefix}.target_duration_sec")
    if target_position < 0:
        raise MaterializationValidationError(f"invalid target position: {prefix}")
    if target_duration <= 0 or target_position + target_duration > _finite(source["duration_sec"], f"{prefix}.source_duration_sec"):
        raise MaterializationValidationError(f"invalid target duration: {prefix}")
    if target_duration < duration_bounds[0] or target_duration > duration_bounds[1]:
        raise MaterializationValidationError(f"target duration outside frozen bounds: {prefix}")

    # A generated variant hash is required only when the manifest explicitly
    # claims that the manipulated audio already exists.
    if row.get("variant_audio_sha256") is not None:
        _hash(row["variant_audio_sha256"], f"{prefix}.variant_audio_sha256")
        if int(row.get("variant_audio_size_bytes", 0)) <= 0:
            raise MaterializationValidationError(f"missing generated audio size: {prefix}")
    forbidden = set(row).intersection({"prediction", "score", "outcome", "result", "auroc", "auprc", "ld_dr95"})
    if forbidden:
        raise MaterializationValidationError(f"scientific outcome leaked into population: {sorted(forbidden)[0]}")


def validate_level2_population(
    manifest: Mapping[str, Any],
    expected_plan: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a materialized population against the frozen cardinality contract."""
    if manifest.get("schema_version") != "topconf.level2.rq1.population.v1":
        raise MaterializationValidationError("wrong Level-2 population schema")
    if manifest.get("status") != "MATERIALIZED" or manifest.get("materialized") is not True:
        raise MaterializationValidationError("population is not materialized")
    if manifest.get("real_level2_outcomes_accessed") is not False:
        raise MaterializationValidationError("real Level-2 outcome access is not false")
    if manifest.get("result_based_selection") is not False:
        raise MaterializationValidationError("result-based selection marker is not false")

    plan = _expected_plan(expected_plan)
    lower, upper = [float(value) for value in plan["target_duration_sec"]]
    sources = _records(manifest, "sources")
    cases = _records(manifest, "case_records")
    reserves = _records(manifest, "reserve_records")
    pools = _records(manifest, "source_pools")
    if len(sources) != int(plan["primary_sources"]):
        raise MaterializationValidationError("source count does not match frozen plan")
    if len(reserves) != int(plan["predeclared_source_reserve"]):
        raise MaterializationValidationError("reserve count does not match frozen plan")
    if len(pools) != int(plan["independent_source_pools"]):
        raise MaterializationValidationError("independent source-pool count does not match frozen plan")
    for index, row in enumerate(sources):
        _validate_source_row(row, f"sources[{index}]")
    for index, row in enumerate(reserves):
        _validate_source_row(row, f"reserve_records[{index}]")
    source_ids = _unique(sources, "source_id", "source")
    reserve_ids = _unique(reserves, "source_id", "reserve source")
    if source_ids.intersection(reserve_ids):
        raise MaterializationValidationError("reserve source overlaps primary source")
    source_by_id = {row["source_id"]: row for row in sources}
    speaker_ids = {row["speaker_id"] for row in sources}
    if len(speaker_ids) != int(plan["speakers"]):
        raise MaterializationValidationError("speaker count does not match frozen plan")

    pool_ids = _unique(pools, "pool_id", "source pool")
    if len(pool_ids) != int(plan["independent_source_pools"]):
        raise MaterializationValidationError("source pool IDs are not unique")
    pool_speakers: list[set[str]] = []
    for index, pool in enumerate(pools):
        prefix = f"source_pools[{index}]"
        _require_fields(pool, ("pool_id", "source_count", "speaker_count", "source_ids", "speaker_ids", "manifest_sha256"), prefix)
        _text(pool["pool_id"], f"{prefix}.pool_id")
        _hash(pool["manifest_sha256"], f"{prefix}.manifest_sha256")
        ids = pool["source_ids"]
        spks = pool["speaker_ids"]
        if not isinstance(ids, list) or not isinstance(spks, list):
            raise MaterializationValidationError(f"invalid pool identity arrays: {prefix}")
        if len(ids) != int(plan["sources_per_pool"]) or int(pool["source_count"]) != len(ids):
            raise MaterializationValidationError(f"source allocation mismatch: {prefix}")
        if len(spks) != int(plan["speakers_per_pool"]) or int(pool["speaker_count"]) != len(spks):
            raise MaterializationValidationError(f"speaker allocation mismatch: {prefix}")
        if len(set(ids)) != len(ids) or not set(ids).issubset(source_ids):
            raise MaterializationValidationError(f"invalid source IDs in pool: {prefix}")
        if len(set(spks)) != len(spks) or not set(spks).issubset(speaker_ids):
            raise MaterializationValidationError(f"invalid speaker IDs in pool: {prefix}")
        observed_speakers = {source_by_id[source_id]["speaker_id"] for source_id in ids}
        if observed_speakers != set(spks):
            raise MaterializationValidationError(f"pool speaker/source mapping mismatch: {prefix}")
        pool_speakers.append(set(spks))
    if pool_speakers[0].intersection(pool_speakers[1]):
        raise MaterializationValidationError("speaker overlap across independent source pools")
    if set().union(*pool_speakers) != speaker_ids:
        raise MaterializationValidationError("source pool speaker coverage is incomplete")

    if len(cases) != int(plan["primary_sources"]) * int(plan["mechanisms_per_source"]):
        raise MaterializationValidationError("case count does not match frozen mechanism grid")
    _unique(cases, "case_id", "case")
    order = manifest.get("case_order")
    if order != [row["case_id"] for row in cases] or order != sorted(order):
        raise MaterializationValidationError("case ordering is not deterministic")
    seeds: set[tuple[int, int]] = set()
    generation_seeds: set[int] = set()
    transform_seeds: set[int] = set()
    pair_groups: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(cases):
        source_id = row.get("source_id")
        if source_id not in source_by_id:
            raise MaterializationValidationError(f"case references unknown source: case_records[{index}]")
        _validate_case_row(row, f"case_records[{index}]", source_by_id[source_id], (lower, upper))
        seed_pair = (int(row["generation_seed"]), int(row["transform_seed"]))
        if seed_pair in seeds:
            raise MaterializationValidationError("duplicate case generation/transformation seed")
        if seed_pair[0] in generation_seeds or seed_pair[1] in transform_seeds:
            raise MaterializationValidationError("seed is not unique across Level-2 cases")
        seeds.add(seed_pair)
        generation_seeds.add(seed_pair[0])
        transform_seeds.add(seed_pair[1])
        pair_groups.setdefault(row["pair_id"], []).append(row)
    if len(pair_groups) != int(plan["primary_sources"]):
        raise MaterializationValidationError("pair count does not match frozen source count")
    for pair_id, group in pair_groups.items():
        if len(group) != int(plan["mechanisms_per_source"]):
            raise MaterializationValidationError(f"pair mechanism count mismatch: {pair_id}")
        if len({row["mechanism_id"] for row in group}) != len(group):
            raise MaterializationValidationError(f"duplicate mechanism in pair: {pair_id}")
        for field in ("source_id", "speaker_id", "session_id", "utterance_id", "split", "target_position", "target_duration_sec", "parent_asset_id"):
            if len({row[field] for row in group}) != 1:
                raise MaterializationValidationError(f"pair integrity mismatch: {pair_id}.{field}")

    mechanisms = Counter(row["mechanism_id"] for row in cases)
    if len(mechanisms) != int(plan["mechanisms_per_source"]) or len(set(mechanisms.values())) != 1:
        raise MaterializationValidationError("mechanism allocation is not balanced")
    declared_counts = manifest.get("counts")
    if not isinstance(declared_counts, Mapping):
        raise MaterializationValidationError("missing declared counts")
    expected_counts = {
        "population_size": len(sources),
        "source_count": len(sources),
        "speaker_count": len(speaker_ids),
        "pair_count": len(pair_groups),
        "case_count": len(cases),
    }
    for field, actual in expected_counts.items():
        if declared_counts.get(field) != actual:
            raise MaterializationValidationError(f"declared count mismatch: {field}")
    if dict(declared_counts.get("mechanism_counts", {})) != dict(mechanisms):
        raise MaterializationValidationError("declared mechanism counts mismatch")
    transforms = Counter(row["transform_condition"] for row in cases)
    if dict(declared_counts.get("transform_counts", {})) != dict(transforms):
        raise MaterializationValidationError("declared transform counts mismatch")

    source_split = {row["source_id"]: row["split"] for row in sources}
    speaker_split: dict[str, str] = {}
    for row in sources:
        prior = speaker_split.setdefault(row["speaker_id"], row["split"])
        if prior != row["split"]:
            raise MaterializationValidationError("speaker leakage across Level-2 splits")
    if any(source_split[row["source_id"]] != row["split"] for row in cases):
        raise MaterializationValidationError("case split differs from source split")
    return {
        "status": "PASS",
        "population_size": len(sources),
        "source_count": len(sources),
        "speaker_count": len(speaker_ids),
        "pair_count": len(pair_groups),
        "case_count": len(cases),
        "mechanism_counts": dict(mechanisms),
        "transform_counts": dict(transforms),
    }


def validate_inference_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate the model-facing view and reject GT/source semantics."""
    if manifest.get("schema_version") != "topconf.level2.rq1.inference.v1":
        raise MaterializationValidationError("wrong inference manifest schema")
    if manifest.get("ground_truth_visible") is not False:
        raise MaterializationValidationError("ground truth is visible to inference")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise MaterializationValidationError("missing inference cases")
    if manifest.get("status") == "MATERIALIZED" and not cases:
        raise MaterializationValidationError("materialized inference manifest is empty")
    seen: set[str] = set()
    for index, row in enumerate(cases):
        if not isinstance(row, Mapping):
            raise MaterializationValidationError(f"invalid inference case: {index}")
        leaked = set(row).intersection(INFERENCE_FORBIDDEN_FIELDS)
        if leaked:
            raise MaterializationValidationError(f"GT/source semantics leaked: {sorted(leaked)[0]}")
        case_id = _text(row.get("opaque_case_id"), f"inference.cases[{index}].opaque_case_id")
        if case_id in seen:
            raise MaterializationValidationError("duplicate inference case")
        seen.add(case_id)
        _hash(row.get("audio_sha256"), f"inference.cases[{index}].audio_sha256")
        if _finite(row.get("duration_sec"), f"inference.cases[{index}].duration_sec") <= 0:
            raise MaterializationValidationError("non-positive inference duration")
        _text(row.get("split"), f"inference.cases[{index}].split")


def validate_evaluation_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate the private evaluation view without accepting predictions."""
    if manifest.get("schema_version") != "topconf.level2.rq1.evaluation.v1":
        raise MaterializationValidationError("wrong evaluation manifest schema")
    if manifest.get("model_runner_access") is not False:
        raise MaterializationValidationError("model runner can access evaluation manifest")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise MaterializationValidationError("missing evaluation cases")
    for index, row in enumerate(cases):
        if not isinstance(row, Mapping):
            raise MaterializationValidationError(f"invalid evaluation case: {index}")
        for field in ("case_id", "target_start_sec", "target_end_sec", "label", "mechanism_id"):
            if field not in row:
                raise MaterializationValidationError(f"missing evaluation GT field: {field}")
        if _finite(row["target_start_sec"], f"evaluation[{index}].target_start_sec") < 0:
            raise MaterializationValidationError("negative evaluation GT start")
        if _finite(row["target_end_sec"], f"evaluation[{index}].target_end_sec") <= _finite(row["target_start_sec"], f"evaluation[{index}].target_start_sec"):
            raise MaterializationValidationError("invalid evaluation GT interval")
        if set(row).intersection({"prediction", "score", "outcome", "metric", "auroc", "auprc", "ld_dr95"}):
            raise MaterializationValidationError("scientific outcome leaked into evaluation manifest")


def _population_identity_records(population: Mapping[str, Any]) -> list[dict[str, Any]]:
    sources = _records(population, "sources")
    cases = _records(population, "case_records")
    source_by_id = {row.get("source_id"): row for row in sources}
    records: list[dict[str, Any]] = []
    for source in sources:
        records.append(dict(source))
    for case in cases:
        source = source_by_id.get(case.get("source_id"), {})
        merged = dict(source)
        merged.update(case)
        records.append(merged)
    return records


def _overlap_counts(population: Mapping[str, Any], exclusion_sets: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    population_values: dict[str, set[Any]] = {dimension: set() for dimension in FRESHNESS_DIMENSIONS}
    for row in _population_identity_records(population):
        for dimension in FRESHNESS_DIMENSIONS:
            value = row.get(dimension)
            if value not in (None, ""):
                population_values[dimension].add(value)
    overlaps = {dimension: 0 for dimension in FRESHNESS_DIMENSIONS}
    for exclusion in exclusion_sets:
        for row in exclusion.get("records", []):
            if not isinstance(row, Mapping):
                continue
            for dimension in FRESHNESS_DIMENSIONS:
                value = row.get(dimension)
                if value not in (None, "") and value in population_values[dimension]:
                    overlaps[dimension] += 1
    return overlaps


def validate_level2_freshness(
    population: Mapping[str, Any],
    freshness: Mapping[str, Any],
    *,
    universes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate a case/lineage freshness claim, failing closed on gaps."""
    if freshness.get("schema_version") == "topconf.level2.freshness.v3":
        return validate_level2_freshness_v3(population, freshness, universes=universes)
    if population.get("materialized") is not True or population.get("status") != "MATERIALIZED":
        raise FreshnessInsufficientEvidence("population is not materialized")
    if freshness.get("schema_version") != "topconf.level2.freshness.v1":
        raise FreshnessValidationError("wrong freshness schema")
    if freshness.get("result_based_selection") is not False:
        raise FreshnessValidationError("freshness record permits result-based selection")
    required = freshness.get("required_exclusion_sets")
    sets = freshness.get("exclusion_sets")
    if not isinstance(required, list) or not isinstance(sets, list):
        raise FreshnessInsufficientEvidence("exclusion universe is not materialized")
    by_id = {item.get("set_id"): item for item in sets if isinstance(item, Mapping)}
    if len(by_id) != len(sets):
        raise FreshnessValidationError("duplicate or invalid exclusion set")
    for set_id in required:
        item = by_id.get(set_id)
        if item is None:
            raise FreshnessInsufficientEvidence(f"missing exclusion set: {set_id}")
        status = item.get("status")
        if status not in {"COMPLETE", "COMPLETE_EXCLUSION_EMPTY"}:
            raise FreshnessInsufficientEvidence(f"exclusion set is incomplete: {set_id}")
        _hash(item.get("manifest_sha256"), f"exclusion_sets.{set_id}.manifest_sha256")
        if not isinstance(item.get("records"), list):
            raise FreshnessInsufficientEvidence(f"exclusion records are unavailable: {set_id}")
        dimensions = item.get("identity_dimensions")
        if not isinstance(dimensions, list) or not set(FRESHNESS_DIMENSIONS).issubset(dimensions):
            raise FreshnessInsufficientEvidence(f"lineage dimensions are incomplete: {set_id}")
        for index, row in enumerate(item["records"]):
            if not isinstance(row, Mapping):
                raise FreshnessInsufficientEvidence(f"invalid exclusion record: {set_id}[{index}]")
            missing = [dimension for dimension in FRESHNESS_DIMENSIONS if dimension not in row]
            if missing:
                raise FreshnessInsufficientEvidence(f"missing lineage metadata: {set_id}[{index}].{missing[0]}")

    overlaps = _overlap_counts(population, [by_id[set_id] for set_id in required])
    declared = freshness.get("overlap_counts")
    if not isinstance(declared, Mapping) or any(declared.get(key) != value for key, value in overlaps.items()):
        raise FreshnessValidationError("declared freshness overlap counts do not match identity comparison")
    speaker_policy = freshness.get("speaker_overlap_policy")
    prohibited = dict(overlaps)
    if speaker_policy == "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT":
        prohibited["speaker_id"] = 0
    if any(value for key, value in prohibited.items() if key != "speaker_id"):
        raise FreshnessValidationError("prohibited case/source/lineage overlap")
    if freshness.get("freshness_verdict") != "PASS" or freshness.get("status") != "PASS":
        raise FreshnessInsufficientEvidence("freshness verdict is not PASS")
    return {"status": "PASS", "overlap_counts": overlaps}


V3_UNIVERSES = (
    "CASE_EXCLUSION",
    "SOURCE_EXCLUSION",
    "SPEAKER_USAGE",
    "LINEAGE_EXCLUSION",
)
V3_COMPLETENESS = frozenset({"COMPLETE", "PARTIAL", "UNKNOWN", "COMPLETE_EXCLUSION_EMPTY"})


def _v3_records(universe: Mapping[str, Any], universe_id: str) -> list[dict[str, Any]]:
    records = universe.get("records")
    if not isinstance(records, list) or not all(isinstance(row, Mapping) for row in records):
        raise FreshnessInsufficientEvidence(f"{universe_id} records are unavailable")
    return [dict(row) for row in records]


def _v3_speaker_key(row: Mapping[str, Any]) -> str | None:
    explicit = row.get("speaker_key")
    if isinstance(explicit, str) and explicit.strip():
        return explicit
    speaker = row.get("speaker_id")
    if not isinstance(speaker, str) or not speaker.strip():
        return None
    corpus = row.get("corpus") or row.get("dataset") or row.get("speaker_namespace")
    if isinstance(corpus, str) and corpus.strip():
        return f"{corpus}:{speaker}"
    return speaker


def _v3_population_speaker_key(row: Mapping[str, Any]) -> str | None:
    speaker = row.get("speaker_id")
    if not isinstance(speaker, str) or not speaker.strip():
        return None
    if speaker.startswith("AISHELL3_"):
        return f"AISHELL3:{speaker.removeprefix('AISHELL3_')}"
    if speaker.startswith("AISHELL1_"):
        return f"AISHELL1:{speaker.removeprefix('AISHELL1_')}"
    return speaker


def _v3_nonempty_strings(row: Mapping[str, Any], fields: Iterable[str]) -> set[str]:
    return {
        str(row[field])
        for field in fields
        if isinstance(row.get(field), str) and row[field].strip()
    }


def _v3_comparisons(
    population: Mapping[str, Any],
    universes: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    sources = _records(population, "sources")
    cases = _records(population, "case_records")
    case_history = _v3_records(universes["CASE_EXCLUSION"], "CASE_EXCLUSION")
    source_history = _v3_records(universes["SOURCE_EXCLUSION"], "SOURCE_EXCLUSION")
    speaker_history = _v3_records(universes["SPEAKER_USAGE"], "SPEAKER_USAGE")
    lineage_history = _v3_records(universes["LINEAGE_EXCLUSION"], "LINEAGE_EXCLUSION")

    historical_case_ids = {
        str(row["case_id"])
        for row in case_history
        if isinstance(row.get("case_id"), str) and row["case_id"].strip()
    }
    population_case_ids = {
        str(row["case_id"])
        for row in cases
        if isinstance(row.get("case_id"), str) and row["case_id"].strip()
    }
    case_id_overlap = population_case_ids.intersection(historical_case_ids)

    historical_source_keys: dict[str, list[dict[str, Any]]] = {}
    for row in source_history:
        for key in _v3_nonempty_strings(row, ("source_audio_sha256", "source_id")):
            historical_source_keys.setdefault(key.lower(), []).append(row)
    historical_lineage_keys: dict[str, list[dict[str, Any]]] = {}
    for row in lineage_history:
        for key in _v3_nonempty_strings(row, ("source_audio_sha256", "parent_asset_id", "lineage_id")):
            historical_lineage_keys.setdefault(key.lower(), []).append(row)

    source_overlaps: list[dict[str, Any]] = []
    lineage_overlaps: list[dict[str, Any]] = []
    lineage_overlap_case_ids: set[str] = set()
    overlap_speakers: set[str] = set()
    for source in sources:
        source_keys = _v3_nonempty_strings(source, ("source_audio_sha256", "source_id"))
        matched_source_rows: list[dict[str, Any]] = []
        for key in source_keys:
            matched_source_rows.extend(historical_source_keys.get(key.lower(), []))
        if matched_source_rows:
            source_overlaps.append({
                "population_source_id": source.get("source_id"),
                "population_speaker_id": source.get("speaker_id"),
                "source_audio_sha256": source.get("source_audio_sha256"),
                "historical_matches": matched_source_rows,
            })
            speaker_key = _v3_population_speaker_key(source)
            if speaker_key:
                overlap_speakers.add(speaker_key)

        lineage_keys = _v3_nonempty_strings(source, ("source_audio_sha256", "parent_asset_id"))
        matched_lineage_rows: list[dict[str, Any]] = []
        for key in lineage_keys:
            matched_lineage_rows.extend(historical_lineage_keys.get(key.lower(), []))
        if matched_lineage_rows:
            lineage_overlaps.append({
                "population_source_id": source.get("source_id"),
                "population_speaker_id": source.get("speaker_id"),
                "source_audio_sha256": source.get("source_audio_sha256"),
                "historical_matches": matched_lineage_rows,
            })
            speaker_key = _v3_population_speaker_key(source)
            if speaker_key:
                overlap_speakers.add(speaker_key)
            source_id = source.get("source_id")
            if isinstance(source_id, str):
                lineage_overlap_case_ids.update(
                    str(row["case_id"])
                    for row in cases
                    if row.get("source_id") == source_id and isinstance(row.get("case_id"), str)
                )

    population_speakers = {
        key
        for key in (_v3_population_speaker_key(row) for row in sources)
        if key is not None
    }
    historical_speakers = {
        key
        for key in (_v3_speaker_key(row) for row in speaker_history)
        if key is not None
    }
    speaker_overlap = population_speakers.intersection(historical_speakers)

    return {
        "case_id_overlap_count": len(case_id_overlap),
        "case_id_overlap_ids": sorted(case_id_overlap),
        "case_lineage_overlap_count": len(lineage_overlap_case_ids),
        "source_overlap_count": len({row["population_source_id"] for row in source_overlaps}),
        "lineage_overlap_count": len({row["population_source_id"] for row in lineage_overlaps}),
        "speaker_overlap_count": len(speaker_overlap),
        "prohibited_speaker_overlap_count": len(speaker_overlap.intersection(overlap_speakers)),
        "source_overlap_details": source_overlaps,
        "lineage_overlap_details": lineage_overlaps,
        "speaker_overlap_ids": sorted(speaker_overlap),
    }


def validate_level2_freshness_v3(
    population: Mapping[str, Any],
    freshness: Mapping[str, Any],
    universes: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate V2 freshness against separate historical case/source/lineage universes.

    The function returns a detailed PASS, FAIL, or INSUFFICIENT_EVIDENCE
    summary.  It never turns missing historical identity into zero overlap.
    """
    if population.get("materialized") is not True or population.get("status") != "MATERIALIZED":
        raise FreshnessInsufficientEvidence("population is not materialized")
    if freshness.get("schema_version") != "topconf.level2.freshness.v3":
        raise FreshnessValidationError("wrong V3 freshness schema")
    if freshness.get("result_based_selection") is not False:
        raise FreshnessValidationError("freshness record permits result-based selection")

    references = freshness.get("universe_references")
    if not isinstance(references, Mapping):
        raise FreshnessInsufficientEvidence("V3 universe references are unavailable")
    if universes is None:
        embedded = freshness.get("embedded_universes")
        universes = embedded if isinstance(embedded, Mapping) else None
    if universes is None:
        raise FreshnessInsufficientEvidence("V3 historical universes were not supplied")

    completeness: dict[str, str] = {}
    for universe_id in V3_UNIVERSES:
        reference = references.get(universe_id)
        universe = universes.get(universe_id)
        if not isinstance(reference, Mapping) or not isinstance(universe, Mapping):
            raise FreshnessInsufficientEvidence(f"missing V3 universe: {universe_id}")
        status = reference.get("status") or universe.get("status")
        if status not in V3_COMPLETENESS:
            raise FreshnessValidationError(f"invalid V3 completeness status: {universe_id}")
        completeness[universe_id] = str(status)
        evidence = reference.get("evidence_sources") or universe.get("evidence_sources")
        if status != "COMPLETE_EXCLUSION_EMPTY" and (not isinstance(evidence, list) or not evidence):
            raise FreshnessInsufficientEvidence(f"missing evidence source: {universe_id}")
        _v3_records(universe, universe_id)

    isolation_records = freshness.get("corpus_isolation", [])
    if not isinstance(isolation_records, list):
        raise FreshnessValidationError("invalid V3 corpus isolation evidence")
    for index, record in enumerate(isolation_records):
        if not isinstance(record, Mapping):
            raise FreshnessValidationError(f"invalid V3 corpus isolation record: {index}")
        if record.get("status") not in {
            "PASS_POST_FREEZE_ACQUISITION",
            "NO_PRIOR_PROJECT_USAGE_FOUND",
            "FAIL_PRIOR_USAGE_FOUND",
        }:
            raise FreshnessValidationError(f"invalid V3 corpus isolation status: {index}")
        if not isinstance(record.get("evidence_sources"), list) or not record["evidence_sources"]:
            raise FreshnessInsufficientEvidence(f"missing evidence source: corpus_isolation[{index}]")

    comparison = _v3_comparisons(population, universes)
    declared = freshness.get("comparison_counts")
    if not isinstance(declared, Mapping):
        raise FreshnessInsufficientEvidence("V3 comparison counts are unavailable")
    count_fields = (
        "case_id_overlap_count", "case_lineage_overlap_count", "source_overlap_count",
        "lineage_overlap_count", "speaker_overlap_count", "prohibited_speaker_overlap_count",
        "unknown_case_comparisons", "unknown_source_comparisons", "unknown_lineage_comparisons",
    )
    for field in count_fields:
        if field in comparison:
            observed = comparison[field]
            if declared.get(field) != observed:
                raise FreshnessValidationError(f"declared V3 count mismatch: {field}")
        else:
            value = declared.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise FreshnessValidationError(f"invalid V3 count: {field}")

    prohibited = (
        comparison["case_id_overlap_count"]
        or comparison["case_lineage_overlap_count"]
        or comparison["source_overlap_count"]
        or comparison["lineage_overlap_count"]
    )
    speaker_policy = freshness.get("speaker_overlap_policy")
    if speaker_policy == "PROHIBIT_ALL_SPEAKER_REUSE":
        prohibited = prohibited or comparison["speaker_overlap_count"]
    elif speaker_policy == "ALLOW_HISTORICAL_SPEAKER_REUSE_ONLY_WITH_LINEAGE_DISJOINT":
        prohibited = prohibited or comparison["prohibited_speaker_overlap_count"]
    else:
        raise FreshnessValidationError("missing or unsupported V3 speaker overlap policy")

    unknown_total = sum(
        int(declared[field])
        for field in ("unknown_case_comparisons", "unknown_source_comparisons", "unknown_lineage_comparisons")
    )
    if prohibited:
        status = "FAIL"
        verdict = "FAIL"
    elif unknown_total or any(value in {"PARTIAL", "UNKNOWN"} for value in completeness.values()):
        status = "INSUFFICIENT_EVIDENCE"
        verdict = "INSUFFICIENT_EVIDENCE"
    else:
        status = "PASS"
        verdict = "PASS"
    declared_verdict = freshness.get("freshness_verdict")
    if declared_verdict != verdict:
        raise FreshnessValidationError("declared V3 freshness verdict does not match evidence")

    return {
        "status": status,
        "freshness_verdict": verdict,
        "completeness": completeness,
        "comparison_counts": dict(declared),
        "overlap_details": {
            "case_id_overlap_ids": comparison["case_id_overlap_ids"],
            "source_overlap_details": comparison["source_overlap_details"],
            "lineage_overlap_details": comparison["lineage_overlap_details"],
            "speaker_overlap_ids": comparison["speaker_overlap_ids"],
        },
        "corpus_isolation": isolation_records,
    }
