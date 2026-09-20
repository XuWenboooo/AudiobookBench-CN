from __future__ import annotations

import json
from pathlib import Path
import importlib.util

from audiobookbench.topconf.preparation.evidence_ledger import validate_evidence_ledger
from audiobookbench.topconf.preparation.preregistration import check_preparation


REPO = Path(__file__).resolve().parents[2]


def _mismatch_builder():
    path = REPO / "tools/topconf/build_partialspoof_identity_mismatch.py"
    spec = importlib.util.spec_from_file_location("partialspoof_mismatch_builder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_preparation_firewall_passes():
    result = check_preparation(REPO)
    assert result["status"] == "PASS", result
    assert all(value == "PASS" for value in result["checks"].values())


def test_ledger_rejects_w7_metric_before_inference():
    ledger = json.loads((REPO / "research_assurance/topconf/w7_preparation/SCIENTIFIC_EVIDENCE_LEDGER_V1.json").read_text(encoding="utf-8"))
    ledger["entries"][-2]["value"] = 0.73
    errors = validate_evidence_ledger(ledger)
    assert any("W7_FORMAL value must be NOT_MEASURED" in error for error in errors)


def test_ledger_rejects_confirmatory_value_without_level2_access():
    ledger = json.loads((REPO / "research_assurance/topconf/w7_preparation/SCIENTIFIC_EVIDENCE_LEDGER_V1.json").read_text(encoding="utf-8"))
    ledger["entries"][-1]["value"] = 0.51
    errors = validate_evidence_ledger(ledger)
    assert any("CONFIRMATORY value must be NOT_MEASURED" in error for error in errors)


def test_state_artifact_keeps_w6_blocked_and_w7_unmeasured():
    state = json.loads((REPO / "research_assurance/topconf/w7_preparation/W7_PREPARATION_STATE_V1.json").read_text(encoding="utf-8"))
    assert state["W6_GATE"] == "BLOCKED"
    assert state["READY_EXTERNAL_DISTRIBUTIONS"] < state["REQUIRED_EXTERNAL_DISTRIBUTIONS"]
    assert state["W7_PROTOCOL_FROZEN"] == "NO"
    assert state["W7_SCIENTIFIC_INFERENCES"] == 0
    assert state["LEVEL2_OUTCOMES_ACCESSED"] == "NO"


def test_partialspoof_identity_builder_is_read_only_and_fail_closed(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    eval_path = artifact_root / "partialspoof_eval_extracted/database/eval/eval.lst"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text("CON_E_0034982\nCON_E_0058039\n", encoding="utf-8")
    result = _mismatch_builder().build_evidence(artifact_root)
    assert result["affected_count"] == 2
    assert result["identity_status"] == "UNRESOLVED_OFFICIAL_MISMATCH"
    assert result["PARTIALSPOOF_READY"] == "NO"
    assert result["prohibited_actions_taken"] == []
