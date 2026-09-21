"""Hash pre-inference execution-recovery artifacts without mutating V2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
RECOVERY_FILES = [
    "W7_PREREGISTRATION_HASH_MANIFEST_V2.json",
    "W7_HUMAN_AUTHORIZATION_RECORD_V2.json",
    "W7_EXECUTION_ATTEMPT_1_EVIDENCE_LEDGER_V1.json",
    "W7_EXECUTION_READINESS_RECOVERY_BASELINE_V1.md",
    "W7_MODEL_AND_RIGHTS_ADJUDICATION_V1.json",
    "W7_MECHANISM_EXECUTION_CONFIG_V1.json",
    "W7_MECHANISM_CONFIG_EQUIVALENCE_AUDIT_V1.md",
    "W7_UNIFIED_RUNNER_DRYRUN_AUDIT_V1.md",
    "W7_EXECUTION_IMPLEMENTATION_MANIFEST_V1.json",
    "W7_EXECUTION_READINESS_REAUDIT_V1.json",
]
RUNNER_FILES = [
    Path("src/audiobookbench/topconf/w7_execution.py"),
    Path("tests/topconf/test_w7_execution_recovery.py"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def item(path: Path) -> dict[str, object]:
    return {"sha256": sha256(path), "size": path.stat().st_size}


def main() -> None:
    repo = ROOT.parents[1]
    missing = [name for name in RECOVERY_FILES if not (ROOT / name).is_file()]
    missing += [str(name) for name in RUNNER_FILES if not (repo / name).is_file()]
    records = {
        "frozen_v2_reference": item(ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V2.json"),
        "execution_recovery": {name: item(ROOT / name) for name in RECOVERY_FILES[1:] if (ROOT / name).is_file()},
        "unified_runner": {str(name).replace("\\", "/"): item(repo / name) for name in RUNNER_FILES if (repo / name).is_file()},
    }
    manifest = {
        "schema_version": "topconf.w7.preregistration_hash_manifest.v3",
        "status": "PASS_COMPLETE_COVERAGE_EXECUTION_RECOVERY" if not missing else "FAIL_MISSING_ARTIFACTS",
        "hash_algorithm": "SHA-256",
        "coverage_scope": "pre-inference execution-closure artifacts only; V2 frozen scientific coverage is preserved by reference",
        "scientific_population_changed": False,
        "scientific_config_changed": False,
        "w7_executed": False,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "metrics": "NOT_MEASURED",
        "hash_coverage_gaps": missing,
        "records": records,
    }
    out = ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V3.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    audit = ROOT / "W7_PREREGISTRATION_HASH_COVERAGE_AUDIT_V3.md"
    audit.write_text(
        "# W7 preregistration hash coverage audit v3\n\n"
        + "Decision: " + str(manifest["status"]) + ". V3 adds only pre-inference execution-recovery artifacts and references immutable V2 for frozen scientific coverage. "
        + "No W7 case, model inference, outcome, metric, or Level-2 artifact is included.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "missing": missing}, ensure_ascii=False))


if __name__ == "__main__":
    main()
