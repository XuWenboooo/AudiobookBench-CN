"""Hash the final rights/specification closure, preserving V4 and fail-closing P4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
REPO = ROOT.parents[1]
FILES = [
    "BAM_CHECKPOINT_OFFICIAL_USE_EVIDENCE_V1.md",
    "BAM_CHECKPOINT_OFFICIAL_USE_EVIDENCE_V1.json",
    "BAM_RIGHTS_FINAL_ADJUDICATION_V2.md",
    "BAM_RIGHTS_FINAL_ADJUDICATION_V2.json",
    "BAM_RIGHTS_FINAL_ADJUDICATION_V3.json",
    "W7_MECHANISM_P4_HUMAN_DECISION_TEMPLATE_V1.md",
    "W7_P4_EXACT_INVENTORY_V1.json",
    "W7_P4_CLASSIFICATION_AND_COMPRESSION_V1.json",
    "W7_MECHANISM_SHARED_POLICIES_V1.json",
    "W7_MECHANISM_P4_RESOLUTION_PROVENANCE_V1.md",
    "W7_MECHANISM_P4_MINIMAL_HUMAN_DECISIONS_V1.md",
    "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.json",
    "W7_MECHANISM_CASE_MAP_DETERMINISTIC_ASSIGNMENT_V1.jsonl.gz",
    "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json",
    "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.md",
    "W7_MECHANISM_PREINFERENCE_FREEZE_ADDENDUM_V1.json",
    "W7_MECHANISM_SPECIFICATION_AUDIT_V1.json",
    "W7_EXECUTION_IMPLEMENTATION_MANIFEST_V2.json",
    "W7_EXECUTION_READINESS_REAUDIT_V3.json",
    "W7_EXECUTION_READINESS_REAUDIT_V3.md",
]
CODE = [
    "src/audiobookbench/topconf/w7_execution.py",
    "src/audiobookbench/topconf/w7_mechanism_spec.py",
    "tests/topconf/test_w7_execution_recovery.py",
    "tools/topconf/build_w7_mechanism_specification_v1.py",
    "tools/topconf/build_w7_preregistration_hash_manifest_v5.py",
    "tools/topconf/build_w7_p4_decision_compression_v1.py",
    "tests/topconf/test_w7_p4_decision_compression.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def item(path: Path) -> dict[str, object]:
    return {"sha256": sha256(path), "size": path.stat().st_size}


def main() -> None:
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    missing += [name for name in CODE if not (REPO / name).is_file()]
    manifest = {
        "schema_version": "topconf.w7.preregistration_hash_manifest.v5",
        "status": "INCOMPLETE_P4_FAIL_CLOSED" if not missing else "FAIL_MISSING_ARTIFACTS",
        "hash_algorithm": "SHA-256",
        "prior_v4_reference": item(ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V4.json"),
        "coverage_scope": "pre-inference rights and mechanism specification closure; V4 and frozen scientific artifacts preserved by reference",
        "scientific_population_changed": False,
        "post_outcome_scientific_change": False,
        "outcome_guided_change": False,
        "w7_executed": False,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "metrics": "NOT_MEASURED",
        "mechanism_config_complete": False,
        "mechanism_p4_count": 35,
        "hash_coverage_gaps": missing,
        "records": {
            "closure": {name: item(ROOT / name) for name in FILES if (ROOT / name).is_file()},
            "code": {name: item(REPO / name) for name in CODE if (REPO / name).is_file()},
        },
    }
    out = ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V5.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (ROOT / "W7_PREREGISTRATION_HASH_COVERAGE_AUDIT_V5.md").write_text(
        "# W7 preregistration hash coverage audit v5\n\n"
        f"Decision: `{manifest['status']}`. V5 preserves V4 and covers the BAM rights evidence, deterministic M1 map, pending-P4 config, addendum, implementation manifest, readiness re-audit, generator, and runner contracts. No W7 case inference, prediction, metric, bootstrap, or Level-2 outcome is included.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "missing": missing}, ensure_ascii=False))


if __name__ == "__main__":
    main()
