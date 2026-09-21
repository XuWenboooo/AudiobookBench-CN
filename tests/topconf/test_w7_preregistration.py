from __future__ import annotations

import json
from pathlib import Path
import importlib.util
import shutil

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


def _copy_checker_inputs(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    prep = repo / "research_assurance/topconf/w7_preparation"
    prep.mkdir(parents=True)
    source = REPO / "research_assurance/topconf/w7_preparation"
    for name in ("W7_PREPARATION_STATE_V1.json", "W7_PILOT_PROTOCOL_DRAFT_V1.md", "SCIENTIFIC_EVIDENCE_LEDGER_V1.json", "PARTIALSPOOF_IDENTITY_MISMATCH_V1.json"):
        shutil.copy2(source / name, prep / name)
    return repo


def test_checker_enforces_freeze_authorization_and_inference_invariants(tmp_path: Path):
    repo = _copy_checker_inputs(tmp_path)
    state_path = repo / "research_assurance/topconf/w7_preparation/W7_PREPARATION_STATE_V1.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["W7_PROTOCOL_FROZEN"] = "YES"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = check_preparation(repo)
    assert result["status"] == "FAIL"
    assert any("G2" in error or "G3" in error for error in result["errors"])

    state["W7_PROTOCOL_FROZEN"] = "NO"
    state["W7_EXECUTION_AUTHORIZED"] = "YES"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = check_preparation(repo)
    assert result["status"] == "FAIL"
    assert any("G4" in error for error in result["errors"])

    state["W7_EXECUTION_AUTHORIZED"] = "NO"
    state["W7_SCIENTIFIC_INFERENCES"] = 1
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = check_preparation(repo)
    assert any("G5" in error for error in result["errors"])

    state["W7_SCIENTIFIC_INFERENCES"] = 0
    state["W7_DETECTION_AUROC"] = 0.5
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = check_preparation(repo)
    assert any("G6" in error for error in result["errors"])

    state["W7_DETECTION_AUROC"] = "NOT_MEASURED"
    state["CONFIRMATORY_AUROC"] = 0.5
    state_path.write_text(json.dumps(state), encoding="utf-8")
    result = check_preparation(repo)
    assert any("G7" in error for error in result["errors"])

    state["CONFIRMATORY_AUROC"] = "NOT_MEASURED"
    mismatch_path = repo / "research_assurance/topconf/w7_preparation/PARTIALSPOOF_IDENTITY_MISMATCH_V1.json"
    mismatch = json.loads(mismatch_path.read_text(encoding="utf-8"))
    mismatch["PARTIALSPOOF_READY"] = "YES"
    mismatch_path.write_text(json.dumps(mismatch), encoding="utf-8")
    result = check_preparation(repo)
    assert any("G8" in error for error in result["errors"])


def test_paper_scaffolds_contain_no_outcome_claim_language():
    root = REPO / "research_assurance/topconf/w7_preparation"
    forbidden = ("expected winner", "expected result", "gap confirmed", "gap significant", "localization degrades")
    for name in ("PAPER_RESULTS_TABLE_DRAFT_V1.md", "PAPER_PROVENANCE_APPENDIX_DRAFT_V1.md", "PAPER_EXPERIMENT_MATRIX_DRAFT_V1.md"):
        text = (root / name).read_text(encoding="utf-8").lower()
        assert not any(phrase in text for phrase in forbidden), name
        assert "not_measured" in text or "not_yet_tested_under_w7" in text, name


def test_merge_manifest_is_explicit_and_has_no_machine_paths():
    path = REPO / "research_assurance/topconf/w7_preparation/W7_PREPARATION_MERGE_MANIFEST_V1.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["status"] == "COMPLETE"
    assert manifest["prohibited_artifacts_present"] is False
    assert manifest["safe_to_merge"]
    assert manifest["manual_review_required"]
    assert not any(":\\" in item or item.startswith("/") for group in manifest.values() if isinstance(group, list) for item in group)


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
