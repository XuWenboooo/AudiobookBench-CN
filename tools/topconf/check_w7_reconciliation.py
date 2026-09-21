"""Outcome-blind final W7 pre-execution reconciliation checker."""

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


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    root = repo / "research_assurance" / "topconf"
    state = json.loads((root / "w7_preparation" / "W7_PREPARATION_STATE_RECONCILED_V2.json").read_text(encoding="utf-8"))
    protocol = json.loads((root / "W7_PROTOCOL_CONSISTENCY_AUDIT_V2.json").read_text(encoding="utf-8"))
    acceptance = (root / "W7_DISTRIBUTION_ACCEPTANCE_FINAL_V2.md").read_text(encoding="utf-8")
    case_manifest = json.loads((root / "W7_FINAL_CASE_MANIFEST_V1.json").read_text(encoding="utf-8"))
    execution = json.loads((root / "W7_FINAL_EXECUTION_MANIFEST_V1.json").read_text(encoding="utf-8"))
    hashes = json.loads((root / "W7_PREREGISTRATION_HASH_MANIFEST_V1.json").read_text(encoding="utf-8"))

    checks = {
        "state_w6_gate": state["W6_GATE"] == "PASS",
        "state_localizers": state["READY_LOCALIZERS"] >= 4,
        "state_paradigms": state["DISTINCT_LOCALIZATION_PARADIGMS"] >= 3,
        "state_distributions": state["READY_EXTERNAL_DISTRIBUTIONS"] >= 2,
        "state_unresolved_pre_freeze": state["UNRESOLVED_PRE_FREEZE_ITEMS"] == [],
        "protocol_frozen": state["W7_PROTOCOL_FROZEN"] == "YES",
        "protocol_no_conflicts": protocol["scientific_conflicts"] == 0 and protocol["protocol_conflicts"] == [],
        "resampling_complete": protocol["resampling_protocol_incomplete"] == "NO",
        "acceptance_two_ready": "READY_EXTERNAL_DISTRIBUTIONS = 2" in acceptance,
        "case_two_distributions": case_manifest["counts"]["by_distribution"] == {"PartialEdit": 42471, "LlamaPartialSpoof": 64388},
        "case_no_predictions": case_manifest["manifest_status"] == "FROZEN_METADATA_ONLY_NO_PREDICTIONS" and case_manifest["w7_executed"] is False,
        "execution_auth_no": execution["authorization"]["authorized"] is False,
        "execution_no_run": execution["w7_executed"] is False and execution["w7_scientific_inferences"] == 0,
        "execution_no_level2": execution["gt_separation"]["level2_outcomes_accessed"] is False,
        "metrics_not_measured": execution["metrics_status"] == "NOT_MEASURED",
        "result_based_selection_zero": execution["result_based_selection_count"] == 0,
        "protected_v3": sha256_file(root / "LEVEL2_RQ1_POPULATION_MANIFEST_V3.json").upper() == "AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4",
        "protected_v5": sha256_file(root / "LEVEL2_FRESHNESS_MANIFEST_V5.json").upper() == "6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E",
        "hash_protocol": hashes["protocol_sha256"] == sha256_file(root / "W7_PILOT_PROTOCOL_V1.md"),
        "hash_case": hashes["case_manifest_sha256"] == sha256_file(root / "W7_FINAL_CASE_MANIFEST_V1.json"),
        "hash_execution": hashes["execution_manifest_sha256"] == sha256_file(root / "W7_FINAL_EXECUTION_MANIFEST_V1.json"),
    }
    result = {
        "schema_version": "topconf.w7.pre_execution_audit.v2",
        "audit": "PASS" if all(checks.values()) else "NOT_PASS",
        "checks": checks,
        "W7_PRE_EXECUTION_AUDIT": "PASS" if all(checks.values()) else "NOT_PASS / STOPPED",
        "W7_FORMAL_PILOT_AUTHORIZED": "NO",
        "W7_EXECUTED": "NO",
        "W7_SCIENTIFIC_INFERENCES": 0,
        "LEVEL2_OUTCOMES_ACCESSED": "NO",
        "METRICS": "NOT_MEASURED",
        "NOTE": "PASS means pre-execution reconciliation only; it never authorizes W7 inference.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["audit"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
