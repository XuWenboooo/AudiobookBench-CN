"""Generate deterministic M1 assignment and stop at unresolved M2 P4 fields."""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from audiobookbench.topconf.w7_mechanism_spec import (
    ASSIGNMENT_SALT,
    FAMILY_IDS,
    FIXED_FIELDS,
    P4_FIELDS,
    PROTOCOL_ID,
    SEED_SALT,
    assign_family,
    canonical_bytes,
    family_config_status,
    validate_assignment,
)


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
SOURCE = ROOT / "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz"
DETAIL = ROOT / "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.jsonl.gz"
SUMMARY = ROOT / "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.json"
CONFIG = ROOT / "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json"
ADDENDUM_MD = ROOT / "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.md"
ADDENDUM_JSON = ROOT / "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def row(record: dict[str, object]) -> dict[str, object]:
    assigned = assign_family(record)
    config = family_config_status(str(assigned["mechanism_family"]))
    output = {
        "case_id": record["case_id"],
        "distribution_id": record["distribution_id"],
        "distribution_version": record["distribution_version"],
        "split_id": record["split_id"],
        "source_id": record["source_audio_id"],
        "source_audio_hash": record["source_audio_hash"],
        "gt_id": record["gt_id"],
        "gt_hash": record["gt_hash"],
        "condition_id": "mechanism_shift",
        "source_manipulation_family": record["manipulation_family"],
        "source_manipulation_mechanism": record["manipulation_mechanism"],
        **assigned,
        **config,
        "configuration_hash": "NOT_AVAILABLE",
        "evidence_sources": [
            "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz",
            "w7_preparation/W7_PILOT_PROTOCOL_DRAFT_V1.md",
            "w7_preparation/MECHANISM_CONFIG_CONTRACT_V1.md",
            "w7_preparation/MECHANISM_CONFIG_SCHEMA_V1.json",
            "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.md",
        ],
    }
    validate_assignment(output)
    return output


def main() -> None:
    count = 0
    families = Counter()
    distribution_families: dict[str, Counter[str]] = {}
    with DETAIL.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as output:
            with gzip.open(SOURCE, "rt", encoding="utf-8") as source:
                for line in source:
                    record = json.loads(line)
                    if record["condition_id"] != "mechanism_shift":
                        continue
                    generated = row(record)
                    output.write(canonical_bytes(generated) + b"\n")
                    count += 1
                    family = str(generated["mechanism_family"])
                    distribution = str(generated["distribution_id"])
                    families[family] += 1
                    distribution_families.setdefault(distribution, Counter())[family] += 1

    config_payload = {
        "schema_version": "topconf.w7.mechanism_execution_config.v1",
        "status": "INCOMPLETE_P4_FAIL_CLOSED",
        "protocol_id": PROTOCOL_ID,
        "assignment_rule": "SHA256(protocol_id||distribution_id||case_id||W7_MECHANISM_ASSIGNMENT_V1)[:64bits] mod len(lexicographically_sorted_eligible_families)",
        "assignment_salt": ASSIGNMENT_SALT,
        "seed_rule": "SHA256(protocol_id||distribution_id||case_id||mechanism_family||W7_MECHANISM_SEED_V1)[:64bits]",
        "seed_salt": SEED_SALT,
        "eligible_family_registry": list(FAMILY_IDS),
        "fixed_fields": dict(FIXED_FIELDS),
        "p4_fields": list(P4_FIELDS),
        "family_config_status": {family: family_config_status(family) for family in FAMILY_IDS},
        "mechanism_config_sha256": "NOT_AVAILABLE",
        "reason": "Pinned pre-W7 evidence does not uniquely provide implementation, version, parameter set, reference/span, codec path, or parameter values for any permitted family.",
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
    }
    CONFIG.write_text(json.dumps(config_payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    summary = {
        "schema_version": "topconf.w7.mechanism_case_map_deterministic_assignment.v1",
        "status": "INCOMPLETE_P4_FAIL_CLOSED",
        "source_case_manifest": SOURCE.name,
        "source_case_manifest_sha256": sha256(SOURCE),
        "records": count,
        "distribution_counts": {key: sum(value.values()) for key, value in distribution_families.items()},
        "family_counts": dict(sorted(families.items())),
        "distribution_family_counts": {key: dict(sorted(value.items())) for key, value in sorted(distribution_families.items())},
        "eligible_family_exclusions": {},
        "detailed_records": DETAIL.name,
        "detailed_records_sha256": sha256(DETAIL),
        "mechanism_config": CONFIG.name,
        "mechanism_config_sha256": sha256(CONFIG),
        "assignment_rule": config_payload["assignment_rule"],
        "assignment_salt": ASSIGNMENT_SALT,
        "seed_rule": config_payload["seed_rule"],
        "p4_count": len(FAMILY_IDS) * len(P4_FIELDS),
        "p4_fields": list(P4_FIELDS),
        "map_determinism": "PASS_GENERATOR_CANONICAL_BYTES",
        "scientific_population_changed": False,
        "post_outcome_scientific_change": False,
        "outcome_guided_change": False,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    generator_path = Path(__file__).resolve()
    addendum = {
        "schema_version": "topconf.w7.mechanism_preinference_freeze_addendum.v1",
        "status": "INCOMPLETE_P4_FAIL_CLOSED",
        "created_before_first_w7_scientific_inference": True,
        "w7_scientific_inferences_at_freeze": 0,
        "level2_outcomes_accessed_at_freeze": False,
        "formal_outcome_absence": "PASS",
        "pre_inference_specification_completion": True,
        "outcome_blind_deterministic_completion": True,
        "human_authorization_scope": "mechanism specification completion only; not W7 execution authorization",
        "protocol_base_id": PROTOCOL_ID,
        "source_case_manifest_sha256": sha256(SOURCE),
        "assignment_generator_sha256": sha256(generator_path),
        "mechanism_config_path": CONFIG.name,
        "mechanism_config_sha256": sha256(CONFIG),
        "mechanism_map_path": DETAIL.name,
        "mechanism_map_sha256": sha256(DETAIL),
        "mechanism_map_count": count,
        "assignment_rule": config_payload["assignment_rule"],
        "assignment_salt": ASSIGNMENT_SALT,
        "seed_rule": config_payload["seed_rule"],
        "p4_count": summary["p4_count"],
        "p4_fields": list(P4_FIELDS),
        "mechanism_freeze": "INCOMPLETE",
        "execution_authorization": "NOT_GRANTED",
    }
    ADDENDUM_JSON.write_text(json.dumps(addendum, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    ADDENDUM_MD.write_text(
        "# W7 mechanism pre-inference freeze addendum v1\n\n"
        "Status: `PRE_INFERENCE_SPECIFICATION_COMPLETION / INCOMPLETE_P4_FAIL_CLOSED`\n\n"
        "This addendum was created before any W7 scientific inference. It records the human-authorized deterministic M1 assignment rule and seed rule, but it does not invent missing implementation or parameter values.\n\n"
        "```text\n"
        f"W7_SCIENTIFIC_INFERENCES_AT_FREEZE = 0\nLEVEL2_OUTCOMES_ACCESSED_AT_FREEZE = NO\nFORMAL_OUTCOME_ABSENCE = PASS\nPRE_INFERENCE_SPECIFICATION_COMPLETION = YES\nASSIGNMENT_SALT = {ASSIGNMENT_SALT}\nMECHANISM_CASE_MAP_COUNT = {count}\nMECHANISM_MAP_DETERMINISM = PASS_GENERATOR_CANONICAL_BYTES\nP4_COUNT = {summary['p4_count']}\nMECHANISM_FREEZE = INCOMPLETE\nW7_EXECUTION_AUTHORIZATION = NO\n" +
        "```\n\n"
        "M1 maps each case to the lexicographically sorted eligible family list using the frozen SHA-256 rule. No pre-W7 evidence excludes a family, so all five families are eligible for every logical case. M2 uses fixed 16 kHz/seed/quality/failure policies but leaves the seven family-specific P4 fields unresolved for every family: implementation, version, parameter set, reference rule, target-span rule, codec path, and parameters. M3 validates identity, determinism, source/GT linkage, no timestamps/absolute paths, no outcomes, and no Level-2 access.\n\n"
        "Because P4 remains nonzero, no complete executable config hash exists, no final map is claimed, and no four-localizer runner dry-run is authorized. A separate human decision is required for each P4 field class before a new re-authorization request.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": summary["status"], "records": count, "p4_count": summary["p4_count"], "map_sha256": summary["detailed_records_sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
