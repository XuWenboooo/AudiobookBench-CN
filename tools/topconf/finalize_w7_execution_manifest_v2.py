"""Bind hashes into the no-run W7 execution manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
    path = root / "W7_FINAL_EXECUTION_MANIFEST_V2.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["protocol_sha256"] = sha256(root / "W7_PILOT_PROTOCOL_V1_1.md")
    data["case_manifest_sha256"] = sha256(root / "W7_FINAL_CASE_MANIFEST_V2.jsonl.gz")
    data["environment_manifest_sha256"] = sha256(root / "W7_ENVIRONMENT_MANIFEST_V1.json")
    data["statistical_configuration_sha256"] = sha256(root / "W7_STATISTICAL_CONFIGURATION_V1.json")
    data["failure_propagation_configuration_sha256"] = sha256(root / "W7_FAILURE_PROPAGATION_CONFIGURATION_V1.json")
    data["execution_manifest_self_field_basis"] = "canonical JSON with execution_manifest_sha256 field set to TO_BE_FILLED_BY_HASH_AUDIT"
    basis = dict(data)
    basis["execution_manifest_sha256"] = "TO_BE_FILLED_BY_HASH_AUDIT"
    data["execution_manifest_sha256"] = hashlib.sha256((json.dumps(basis, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")).hexdigest()
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"protocol_sha256": data["protocol_sha256"], "case_manifest_sha256": data["case_manifest_sha256"], "execution_manifest_sha256": data["execution_manifest_sha256"]}))


if __name__ == "__main__":
    main()
