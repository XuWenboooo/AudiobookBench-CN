import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_state_machine_separates_approval_from_execution_readiness():
    readiness = read("W7_APPROVED_ASSET_RECOVERY_READINESS_V2.json")
    assert readiness["p4_scientific_specification"] == "FROZEN"
    assert readiness["p4_human_approval"] == "COMPLETE"
    assert readiness["human_approval_invalidated"] is False
    assert readiness["scientific_approval"] == {"M1": "APPROVED", "M2": "APPROVED", "M3": "APPROVED", "M4": "APPROVED", "M5": "APPROVED"}
    assert readiness["execution_readiness"]["M2"] == "PASS"
    assert readiness["execution_readiness"]["M4"] == "PASS"
    assert readiness["w7_execution_authorized"] is False


def test_m5_registry_identity_is_corrected_without_scientific_change():
    manifest = read("W7_APPROVED_RUNTIME_ASSET_MANIFEST_V2.json")
    m5 = next(item for item in manifest["assets"] if item["family"] == "voice_conditioned_tts_vc_replacement")
    assert m5["code_version"] == "Coqui TTS v0.7.0"
    assert m5["code_source_revision"] == "c7cca4135db0c108a30ba8fd6a437fb63a5ecc12"
    assert m5["model_registry_commit"] == "e9a1953e"
    assert m5["model_artifact_release"] == "v0.6.1_models"
    assert m5["official_source"] == "https://coqui.gateway.scarf.sh/v0.6.1_models/tts_models--multilingual--multi-dataset--your_tts.zip"
    assert m5["license"] == "CC BY-NC-ND 4.0"
    assert manifest["scientific_config_changed"] is False
    assert manifest["human_approval_invalidated"] is False


def test_v2_assets_are_not_materialized_and_no_v6_is_claimed():
    manifest = read("W7_APPROVED_RUNTIME_ASSET_MANIFEST_V2.json")
    assert all(item["sha256"] == "NOT_MATERIALIZED" or item.get("actual_sha256") == "NOT_MATERIALIZED" for item in manifest["assets"])
    assert manifest["checkpoint_bytes_committed"] is False
    assert not (ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V6.json").exists()
