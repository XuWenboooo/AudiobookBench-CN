from __future__ import annotations
import copy, json
from pathlib import Path
import pytest
from audiobookbench.topconf.level2.governance import (Level2ValidationError, build_blinded_manifest, validate_failure_ledger, validate_level2_manifest, validate_namespace, validate_retry_ledger, validate_reveal_gate)

FIXTURES = Path(__file__).parent / "fixtures"
def cohort(): return json.loads((FIXTURES / "level2_valid_cohort.json").read_text(encoding="utf-8"))
def expect(payload, phrase):
    with pytest.raises(Level2ValidationError, match=phrase): validate_level2_manifest(payload)

def test_valid_synthetic_cohort_and_blinding_pass():
    payload = cohort(); validate_level2_manifest(payload)
    blinded = build_blinded_manifest(payload)
    assert blinded["ground_truth_visible"] is False
    assert all(not set(row).intersection({"mechanism_id", "source_id", "reference_id"}) for row in blinded["cases"])

def test_leakage_identity_and_gt_fail_closed():
    payload = cohort(); payload["sources"].append({"source_id":"s4","speaker_id":"p1","session_id":"x4","language":"zh","duration_sec":12,"waveform_sha256":"9" * 64,"text_hash":"e" * 64}); clone = copy.deepcopy(payload["variants"][0]); clone.update(case_id="c4", source_id="s4", waveform_sha256="8" * 64); payload["variants"].append(clone); payload["splits"].append({"case_id":"c4","split":"test","seed":1}); payload["ground_truth"].append({"case_id":"c4","target_start_sec":2,"target_end_sec":4,"label":"manipulated","visibility":"PRIVATE_GT"}); expect(payload, "speaker leakage")
    payload = cohort(); payload["variants"][1]["source_id"] = "s1"; payload["variants"][1]["speaker_id"] = "p1"; expect(payload, "source leakage")
    payload = cohort(); payload["variants"][1]["case_id"] = "c1"; expect(payload, "duplicate case ID")
    payload = cohort(); payload["ground_truth"][0]["target_end_sec"] = 20; expect(payload, "outside waveform")
    payload = cohort(); payload["sources"][0]["waveform_sha256"] = ""; expect(payload, "missing identity")

def test_reference_and_waveform_contract_fail_closed():
    payload = cohort(); payload["references"][0]["source_id"] = "s2"; payload["variants"][1]["reference_id"] = "r1"; expect(payload, "reference equals source")
    payload = cohort(); payload["variants"][1]["waveform_sha256"] = payload["variants"][0]["waveform_sha256"]; expect(payload, "duplicate waveform")

def test_failure_retry_namespace_and_reveal_gates():
    terminal = [{"case_id":"c1","terminal_category":"SCIENTIFIC_VALID_CASE"}]
    validate_failure_ledger(terminal)
    with pytest.raises(Level2ValidationError, match="retry after valid"):
        validate_retry_ledger([{ "attempt_id":"a2", "case_id":"c1", "attempt_type":"rerun", "invoked":True, "retry_reason":"infrastructure", "authorization_hash":"a"}], terminal)
    candidate = {"invocation_id":"i1","output_namespace":"synthetic/i1","authorization_hash":"a","protocol_hash":"p","dataset_hash":"d"}
    with pytest.raises(Level2ValidationError, match="collision"):
        validate_namespace(candidate, [candidate])
    with pytest.raises(Level2ValidationError, match="completion"):
        validate_reveal_gate({"status":"SYNTHETIC_GOVERNANCE_DRY_RUN","protocol_hash":"p","dataset_hash":"d"}, {"completed":False,"protocol_hash":"p"}, "p", "d")
    validate_reveal_gate({"status":"SYNTHETIC_GOVERNANCE_DRY_RUN","protocol_hash":"p","dataset_hash":"d"}, {"completed":True,"protocol_hash":"p"}, "p", "d")
