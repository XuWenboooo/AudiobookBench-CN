"""Static checks for the non-outcome W7 preparation state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evidence_ledger import validate_evidence_ledger


def check_preparation(repo: str | Path) -> dict[str, Any]:
    repo = Path(repo)
    prep = repo / "research_assurance/topconf/w7_preparation"
    errors: list[str] = []
    checks: dict[str, str] = {}

    state_path = prep / "W7_PREPARATION_STATE_V1.json"
    protocol_path = prep / "W7_PILOT_PROTOCOL_DRAFT_V1.md"
    ledger_path = prep / "SCIENTIFIC_EVIDENCE_LEDGER_V1.json"
    mismatch_path = prep / "PARTIALSPOOF_IDENTITY_MISMATCH_V1.json"
    for path in (state_path, protocol_path, ledger_path, mismatch_path):
        if not path.exists():
            errors.append(f"missing preparation artifact: {path.relative_to(repo)}")
    if errors:
        return {"status": "FAIL", "checks": checks, "errors": errors}

    state = json.loads(state_path.read_text(encoding="utf-8"))
    expected = {
        "CURRENT_STAGE": "TOPCONF-W7-PREPARATION-SIDEBRANCH",
        "W6_GATE": "BLOCKED",
        "W7_PROTOCOL_FROZEN": "NO",
        "W7_SCIENTIFIC_INFERENCES": 0,
        "LEVEL2_OUTCOMES_ACCESSED": "NO",
        "W7_DETECTION_AUROC": "NOT_MEASURED",
        "W7_LOCALIZATION_AUROC": "NOT_MEASURED",
        "CONFIRMATORY_AUROC": "NOT_MEASURED",
        "RESULT_BASED_MODEL_SELECTIONS": 0,
        "RESULT_BASED_DATASET_SELECTIONS": 0,
        "RESULT_BASED_METRIC_CHANGES": 0,
        "PARTIALSPOOF_READY": "NO",
    }
    for key, value in expected.items():
        if state.get(key) != value:
            errors.append(f"state invariant failed: {key}={state.get(key)!r}, expected {value!r}")
    if state.get("READY_EXTERNAL_DISTRIBUTIONS", 0) >= state.get("REQUIRED_EXTERNAL_DISTRIBUTIONS", 2):
        errors.append("W6 distribution gate cannot be represented as blocked with enough ready distributions")
    if state.get("DISTINCT_LOCALIZATION_PARADIGMS", 0) < 4:
        errors.append("preparation state lost the four ready localization paradigms")
    checks["state_firewall"] = "PASS" if not errors else "FAIL"

    protocol = protocol_path.read_text(encoding="utf-8")
    required_markers = (
        "STATUS = DRAFT_NOT_FROZEN",
        "W7_PROTOCOL_FROZEN = NO",
        "LEVEL2_OUTCOMES_ACCESSED = NO",
        "W7_DETECTION_AUROC = NOT_MEASURED",
        "W7_LOCALIZATION_AUROC = NOT_MEASURED",
        "CONFIRMATORY_AUROC = NOT_MEASURED",
        "UNRESOLVED_PRE_FREEZE_ITEM",
    )
    for marker in required_markers:
        if marker not in protocol:
            errors.append(f"protocol missing marker: {marker}")
    if "W7_PROTOCOL_FROZEN = YES" in protocol:
        errors.append("draft protocol contains forbidden frozen state")
    checks["protocol_draft"] = "PASS" if not any("protocol" in error or "frozen state" in error for error in errors) else "FAIL"

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_errors = validate_evidence_ledger(ledger)
    errors.extend(f"ledger: {error}" for error in ledger_errors)
    checks["evidence_ledger"] = "PASS" if not ledger_errors else "FAIL"

    mismatch = json.loads(mismatch_path.read_text(encoding="utf-8"))
    if mismatch.get("identity_status") != "UNRESOLVED_OFFICIAL_MISMATCH" or mismatch.get("PARTIALSPOOF_READY") != "NO":
        errors.append("PartialSpoof mismatch evidence incorrectly marks the distribution ready")
    checks["partialspoof_firewall"] = "PASS" if not any("PartialSpoof" in error for error in errors) else "FAIL"
    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}
