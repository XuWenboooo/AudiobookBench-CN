import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def test_candidate_precheck_preserves_package_and_case_map():
    audit = json.loads((ROOT / "W7_P4_CANDIDATE_EXECUTABILITY_AUDIT_V1.json").read_text(encoding="utf-8"))
    assert audit["proposed_package_sha256"] == "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
    assert audit["proposed_package_unchanged"] is True
    assert audit["mechanism_case_map_sha256"] == "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"
    assert audit["real_w7_cases_used"] == 0
    assert audit["scientific_inferences"] == 0


def test_candidate_precheck_fail_closes_only_missing_model_assets():
    audit = json.loads((ROOT / "W7_P4_CANDIDATE_EXECUTABILITY_AUDIT_V1.json").read_text(encoding="utf-8"))
    assert audit["status"] == "FAIL_CLOSED_CANDIDATE_EXECUTABILITY_BLOCKER"
    assert audit["p4_package_ready_for_human_approval"] is False
    families = audit["families"]
    assert families["cross_speaker_boundary_control"]["ready_for_human_approval"] is True
    assert families["same_speaker_splice_crossfade_control"]["ready_for_human_approval"] is True
    for family in ("conventional_tts_replacement", "neural_speech_editing_infilling", "voice_conditioned_tts_vc_replacement"):
        assert families[family]["executability_blocker"] is True
        assert families[family]["synthetic_execution"] == "NOT_RUN_MODEL_ASSET_GATE"


def test_project_adapters_are_fully_synthetic_validated():
    audit = json.loads((ROOT / "W7_P4_CANDIDATE_EXECUTABILITY_AUDIT_V1.json").read_text(encoding="utf-8"))
    validation = audit["synthetic_adapter_validation"]
    assert validation["load"] is True
    assert validation["shape_valid"] is True
    assert validation["finite"] is True
    assert validation["sample_rate_valid"] is True
    assert validation["determinism"] is True
