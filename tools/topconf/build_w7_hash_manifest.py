"""Write deterministic W7 preregistration and contract hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    root = repo / "research_assurance" / "topconf"
    protocol = root / "W7_PILOT_PROTOCOL_V1.md"
    case_manifest = root / "W7_FINAL_CASE_MANIFEST_V1.json"
    execution = root / "W7_FINAL_EXECUTION_MANIFEST_V1.json"
    execution_data = json.loads(execution.read_text(encoding="utf-8"))
    execution_data["protocol_sha256"] = sha256_file(protocol)
    execution_data["case_manifest_sha256"] = sha256_file(case_manifest)
    execution_data["execution_manifest_sha256_basis"] = "canonical JSON with execution_manifest_sha256 field set to TO_BE_FILLED_BY_HASH_AUDIT"
    execution_hash_basis = dict(execution_data)
    execution_hash_basis["execution_manifest_sha256"] = "TO_BE_FILLED_BY_HASH_AUDIT"
    execution_data["execution_manifest_sha256"] = hashlib.sha256(
        (json.dumps(execution_hash_basis, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    write_json(execution, execution_data)

    relative_files = [
        "W7_PILOT_PROTOCOL_V1.md",
        "W7_FINAL_CASE_MANIFEST_V1.json",
        "W7_FINAL_EXECUTION_MANIFEST_V1.json",
        "W7_GT_AND_IDENTITY_BINDING_V1.json",
        "W7_EXECUTION_NAMESPACE_PLAN_V1.md",
        "W7_WHETHER_READINESS_V1.md",
        "W7_UNIFIED_EVALUATOR_READINESS_V1.md",
        "w7_preparation/CASE_IDENTITY_SCHEMA_V1.json",
        "w7_preparation/MECHANISM_CONFIG_SCHEMA_V1.json",
        "w7_preparation/RESAMPLING_TRANSFORM_SCHEMA_V1.json",
        "w7_preparation/CASE_IDENTITY_CONTRACT_V1.md",
        "w7_preparation/MECHANISM_CONFIG_CONTRACT_V1.md",
        "w7_preparation/RESAMPLING_TRANSFORM_CONTRACT_V1.md",
        "W7_PROTOCOL_CONSISTENCY_AUDIT_V2.json",
        "w7_preparation/W7_PREPARATION_STATE_RECONCILED_V2.json",
    ]
    hashes = {rel: sha256_file(root / rel) for rel in relative_files}
    manifest = {
        "schema_version": "topconf.w7.preregistration_hash_manifest.v1",
        "audit_date": "2026-09-21",
        "status": "PASS_IMMUTABLE_BEFORE_FIRST_INFERENCE",
        "hash_algorithm": "SHA-256",
        "protocol_sha256": hashes["W7_PILOT_PROTOCOL_V1.md"],
        "case_manifest_sha256": hashes["W7_FINAL_CASE_MANIFEST_V1.json"],
        "execution_manifest_sha256": sha256_file(execution),
        "execution_manifest_self_field_basis_sha256": execution_data["execution_manifest_sha256"],
        "contract_hashes": hashes,
        "immutability_rule": "No listed file may change after first W7 inference; any change invalidates authorization and requires a new human review.",
        "w7_executed": False,
        "scientific_inferences": 0,
        "metrics": "NOT_MEASURED",
    }
    write_json(root / "W7_PREREGISTRATION_HASH_MANIFEST_V1.json", manifest)
    print(json.dumps({"protocol_sha256": manifest["protocol_sha256"], "case_manifest_sha256": manifest["case_manifest_sha256"], "execution_manifest_sha256": manifest["execution_manifest_sha256"]}))


if __name__ == "__main__":
    main()
