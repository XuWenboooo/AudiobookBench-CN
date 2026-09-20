"""Static, fail-closed checks for the non-outcome W7 preparation state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evidence_ledger import validate_evidence_ledger


FORMAL_METRICS = ("W7_DETECTION_AUROC", "W7_LOCALIZATION_AUROC")
CONFIRMATORY_METRICS = ("CONFIRMATORY_AUROC",)


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
    state_start = len(errors)
    expected = {
        "CURRENT_STAGE": "TOPCONF-W7-PREPARATION-SIDEBRANCH",
        "W6_GATE": "BLOCKED",
        "W7_PREPARATION_STATUS": "DRAFT_READY_TO_FREEZE",
        "W7_PROTOCOL_STATUS": "DRAFT_READY_TO_FREEZE",
        "W7_PROTOCOL_FROZEN": "NO",
        "W7_EXECUTION_AUTHORIZED": "NO",
        "W7_EXECUTED": "NO",
        "W7_SCIENTIFIC_INFERENCES": 0,
        "LEVEL2_OUTCOMES_ACCESSED": "NO",
        "W7_FORMAL_PILOT_STATUS": "NOT_STARTED",
        "CONFIRMATORY_STATUS": "NOT_STARTED",
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
        errors.append("G1: W6 distribution gate cannot be blocked with enough ready distributions")
    if state.get("W6_GATE") != "PASS" and state.get("W7_PROTOCOL_FROZEN") == "YES":
        errors.append("G2: W7 cannot be frozen while W6_GATE is not PASS")
    unresolved = state.get("UNRESOLVED_PRE_FREEZE_ITEMS")
    if not isinstance(unresolved, list) or any(not isinstance(item, str) or not item.strip() for item in unresolved):
        errors.append("G3: unresolved_pre_freeze_items must be a non-empty list of strings")
    elif state.get("W7_PROTOCOL_FROZEN") == "YES":
        errors.append("G3: unresolved pre-freeze items prohibit protocol freeze")
    if state.get("W7_PROTOCOL_FROZEN") != "YES" and state.get("W7_EXECUTION_AUTHORIZED") == "YES":
        errors.append("G4: execution cannot be authorized before protocol freeze")
    if state.get("W7_EXECUTION_AUTHORIZED") != "YES" and state.get("W7_SCIENTIFIC_INFERENCES") != 0:
        errors.append("G5: unauthorized execution must have zero scientific inferences")
    if state.get("W7_SCIENTIFIC_INFERENCES") == 0:
        for metric in FORMAL_METRICS:
            if state.get(metric) != "NOT_MEASURED":
                errors.append(f"G6: {metric} must be NOT_MEASURED before inference")
    if state.get("LEVEL2_OUTCOMES_ACCESSED") == "NO":
        for metric in CONFIRMATORY_METRICS:
            if state.get(metric) != "NOT_MEASURED":
                errors.append(f"G7: {metric} must be NOT_MEASURED without Level-2 access")
    checks["state_firewall"] = "PASS" if len(errors) == state_start else "FAIL"

    protocol = protocol_path.read_text(encoding="utf-8")
    protocol_start = len(errors)
    required_markers = (
        "STATUS = DRAFT_READY_TO_FREEZE",
        "W7_PROTOCOL_FROZEN = NO",
        "W7_EXECUTION_AUTHORIZED = NO",
        "W7_EXECUTED = NO",
        "LEVEL2_OUTCOMES_ACCESSED = NO",
        "W7_DETECTION_AUROC = NOT_MEASURED",
        "W7_LOCALIZATION_AUROC = NOT_MEASURED",
        "CONFIRMATORY_AUROC = NOT_MEASURED",
    )
    for marker in required_markers:
        if marker not in protocol:
            errors.append(f"protocol missing marker: {marker}")
    if "W7_PROTOCOL_FROZEN = YES" in protocol or "W7_EXECUTION_AUTHORIZED = YES" in protocol:
        errors.append("protocol contains a forbidden authorized/frozen state")
    checks["protocol_draft"] = "PASS" if len(errors) == protocol_start else "FAIL"

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger_errors = validate_evidence_ledger(ledger)
    errors.extend(f"ledger: {error}" for error in ledger_errors)
    checks["evidence_ledger"] = "PASS" if not ledger_errors else "FAIL"

    mismatch = json.loads(mismatch_path.read_text(encoding="utf-8"))
    mismatch_start = len(errors)
    if mismatch.get("identity_status") != "UNRESOLVED_OFFICIAL_MISMATCH" or mismatch.get("PARTIALSPOOF_READY") != "NO":
        errors.append("G8: PartialSpoof mismatch evidence incorrectly marks the distribution ready")
    checks["partialspoof_firewall"] = "PASS" if len(errors) == mismatch_start else "FAIL"
    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}
