"""Machine-readable evidence ledger invariants for outcome-blind W7 preparation."""

from __future__ import annotations

from typing import Any, Mapping


LEDGER_STATUSES = frozenset({"HISTORICAL_PILOT", "READINESS_ONLY", "W7_FORMAL", "CONFIRMATORY"})
REQUIRED_ENTRY_FIELDS = frozenset({"evidence_id", "stage", "source_artifact", "date", "model", "distribution", "condition", "metric", "value", "scientific_status"})


class EvidenceLedgerInvariantError(ValueError):
    pass


def validate_evidence_ledger(ledger: Mapping[str, Any]) -> list[str]:
    """Return no errors only when the ledger obeys the current outcome firewall."""

    errors: list[str] = []
    if not isinstance(ledger, Mapping):
        return ["ledger root must be an object"]
    if ledger.get("w7_scientific_inferences") != 0:
        errors.append("W7_SCIENTIFIC_INFERENCES must be 0")
    if ledger.get("level2_outcomes_accessed") is not False:
        errors.append("LEVEL2_OUTCOMES_ACCESSED must be false")
    if ledger.get("w7_formal_pilot_status") != "NOT_STARTED":
        errors.append("W7 formal pilot must remain NOT_STARTED")
    if ledger.get("confirmatory_status") != "NOT_STARTED":
        errors.append("confirmatory status must remain NOT_STARTED")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return errors + ["entries must be a list"]
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"entry[{index}] must be an object")
            continue
        missing = REQUIRED_ENTRY_FIELDS - set(entry)
        if missing:
            errors.append(f"entry[{index}] missing fields: {sorted(missing)}")
        evidence_id = entry.get("evidence_id")
        if evidence_id in seen:
            errors.append(f"duplicate evidence_id: {evidence_id}")
        seen.add(str(evidence_id))
        stage = entry.get("stage")
        status = entry.get("scientific_status")
        if stage not in LEDGER_STATUSES or status != stage:
            errors.append(f"entry[{index}] stage/scientific_status mismatch")
        if stage == "W7_FORMAL" and ledger.get("w7_scientific_inferences") == 0 and entry.get("value") != "NOT_MEASURED":
            errors.append(f"entry[{index}] W7_FORMAL value must be NOT_MEASURED")
        if stage == "CONFIRMATORY" and ledger.get("level2_outcomes_accessed") is False and entry.get("value") != "NOT_MEASURED":
            errors.append(f"entry[{index}] CONFIRMATORY value must be NOT_MEASURED")
    return errors


def assert_valid_evidence_ledger(ledger: Mapping[str, Any]) -> None:
    errors = validate_evidence_ledger(ledger)
    if errors:
        raise EvidenceLedgerInvariantError("; ".join(errors))
