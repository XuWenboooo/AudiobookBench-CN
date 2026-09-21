import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
PACKAGE_SHA = "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
CONFIG_SHA = "009CAEDD67EA2CA7C6AA8C4DEF32F87465754A0E3C37E1D95D9403D48E9875C2"
MAP_SHA = "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_v3_records_approved_science_and_blocked_execution_separately():
    audit = read("W7_FINAL_APPROVED_ASSET_MATERIALIZATION_AUDIT_V1.json")
    assert audit["p4_scientific_specification"] == "FROZEN"
    assert audit["p4_human_approval"] == "COMPLETE"
    assert audit["human_approval_invalidated"] == "NO"
    assert audit["scientific_approval"] == {"M1": "APPROVED", "M2": "APPROVED", "M3": "APPROVED", "M4": "APPROVED", "M5": "APPROVED"}
    assert audit["execution_readiness"] == {"M1": "BLOCKED_ASSET", "M2": "PASS", "M3": "BLOCKED_ASSET_RUNTIME", "M4": "PASS", "M5": "BLOCKED_ASSET_RUNTIME"}
    assert audit["w7_execution_readiness"] == "FAIL_BLOCKED_ASSET_RUNTIME"
    assert audit["w7_execution_authorized"] is False
    assert audit["w7_executed"] is False


def test_v3_preserves_immutable_scientific_hashes_and_no_v6():
    manifest = read("W7_APPROVED_RUNTIME_ASSET_MANIFEST_V3.json")
    environments = read("W7_APPROVED_RUNTIME_ENVIRONMENTS_V3.json")
    for value in (manifest, environments):
        assert value["approved_package_sha256"] == PACKAGE_SHA
        assert value["approved_execution_config_sha256"] == CONFIG_SHA
        assert value["scientific_config_changed"] is False
        assert value["human_approval_invalidated"] is False
    assert manifest["mechanism_case_map_sha256"] == MAP_SHA
    assert not (ROOT / "W7_PREREGISTRATION_HASH_MANIFEST_V6.json").exists()


def test_v3_has_exact_m3_expected_identity_but_no_bytes():
    manifest = read("W7_APPROVED_RUNTIME_ASSET_MANIFEST_V3.json")
    assets = {item["filename"]: item for item in manifest["assets"]}
    assert assets["giga830M.pth"]["expected_size"] == 3358342977
    assert assets["giga830M.pth"]["expected_sha256"] == "2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3"
    assert assets["encodec_4cb2048_giga.th"]["expected_size"] == 1167842971
    assert assets["encodec_4cb2048_giga.th"]["expected_sha256"] == "caa0c595d4919527a9728d627150aa2a0b15b6d117b21855165851333dc63378"
    for name in ("pretrained_ljs.pth", "giga830M.pth", "encodec_4cb2048_giga.th", "tts_models--multilingual--multi-dataset--your_tts.zip"):
        assert assets[name]["actual_size"] == "NOT_MATERIALIZED"
        assert assets[name]["actual_sha256"] == "NOT_MATERIALIZED"
    assert manifest["checkpoint_bytes_committed"] is False


def test_v3_preserves_exact_m5_provenance_correction():
    manifest = read("W7_APPROVED_RUNTIME_ASSET_MANIFEST_V3.json")
    m5 = next(item for item in manifest["assets"] if item["family"] == "voice_conditioned_tts_vc_replacement")
    assert m5["code_version"] == "Coqui TTS v0.7.0"
    assert m5["code_source_revision"] == "c7cca4135db0c108a30ba8fd6a437fb63a5ecc12"
    assert m5["model_registry_file"] == "TTS/.models.json"
    assert m5["model_registry_commit"] == "e9a1953e"
    assert m5["model_artifact_release"] == "v0.6.1_models"
    assert m5["official_source"] == "https://coqui.gateway.scarf.sh/v0.6.1_models/tts_models--multilingual--multi-dataset--your_tts.zip"
    assert m5["license"] == "CC BY-NC-ND 4.0"
    assert m5["redistribution"] == "NO"
    assert m5["source_status"] == "OFFICIAL_DOWNLOAD_INCOMPLETE_PARTIAL_QUARANTINED_NOT_ACCEPTED"


def test_v3_runtime_manifest_is_explicitly_not_created():
    environments = read("W7_APPROVED_RUNTIME_ENVIRONMENTS_V3.json")
    assert environments["status"] == "BLOCKED_RUNTIME_NOT_CREATED"
    assert environments["main_environment_modified"] is False
    assert all("RUNTIME_NOT_CREATED" in item["status"] for item in environments["runtimes"].values())
