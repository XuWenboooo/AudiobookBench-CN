"""Hash W7 final-blocker closure artifacts without modifying V3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
CLOSURE_FILES = [
    "SAL_FROZEN_CHECKPOINT_IDENTITY_V1.md",
    "BAM_CHECKPOINT_RIGHTS_BINDING_V1.md",
    "MECHANISM_PARAMETER_EVIDENCE_MATRIX_V1.md",
    "W7_MECHANISM_CASE_MAP_PROPOSAL_V1.json",
    "W7_MECHANISM_CASE_MAP_PROPOSAL_V1.jsonl.gz",
    "W7_MECHANISM_HUMAN_FREEZE_TEMPLATE_V1.md",
    "W7_MODEL_AND_RIGHTS_ADJUDICATION_V2.json",
    "W7_EXECUTION_READINESS_REAUDIT_V2.json",
    "W7_EXECUTION_READINESS_REAUDIT_V2.md",
]
RUNNER_FILES = [
    Path("src/audiobookbench/topconf/w7_execution.py"),
    Path("tests/topconf/test_w7_execution_recovery.py"),
    Path("tools/topconf/build_w7_mechanism_case_map_proposal.py"),
    Path("tools/topconf/build_w7_preregistration_hash_manifest_v4.py"),
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
    repo = ROOT.parents[1]
    missing = [name for name in CLOSURE_FILES if not (ROOT / name).is_file()]
    missing += [str(name).replace("\\", "/") for name in RUNNER_FILES if not (repo / name).is_file()]
    manifest = {
        "schema_version": "topconf.w7.preregistration_hash_manifest.v4",
        "status": "PASS_COMPLETE_COVERAGE_FINAL_BLOCKER_CLOSURE" if not missing else "FAIL_MISSING_ARTIFACTS",
        "hash_algorithm": "SHA-256",
        "prior_v3_reference": item(ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V3.json"),
        "coverage_scope": "pure pre-inference final-blocker closure only; V3 and all frozen scientific artifacts remain preserved by reference",
        "scientific_population_changed": False,
        "scientific_config_changed": False,
        "w7_executed": False,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "metrics": "NOT_MEASURED",
        "hash_coverage_gaps": missing,
        "records": {
            "final_blocker_closure": {name: item(ROOT / name) for name in CLOSURE_FILES if (ROOT / name).is_file()},
            "runner_and_builders": {str(name).replace("\\", "/"): item(repo / name) for name in RUNNER_FILES if (repo / name).is_file()},
        },
    }
    out = ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V4.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    audit = ROOT / "W7_PREREGISTRATION_HASH_COVERAGE_AUDIT_V4.md"
    audit.write_text(
        "# W7 preregistration hash coverage audit v4\n\n"
        + "Decision: " + str(manifest["status"]) + ". V4 adds only final-blocker closure artifacts and preserves V3 by exact reference. "
        + "No W7 case audio, model output, metric, bootstrap, or Level-2 artifact is included.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "missing": missing}, ensure_ascii=False))


if __name__ == "__main__":
    main()
