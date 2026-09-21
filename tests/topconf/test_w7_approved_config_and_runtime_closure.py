import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_human_approval_and_approved_config_are_bound_to_immutable_package():
    approval = read("W7_P4_HUMAN_APPROVAL_RECORD_V1.json")
    config = read("W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json")
    assert approval["approval_status"] == "RECORDED_PREINFERENCE_ONLY"
    assert approval["approved_package_sha256"] == "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
    assert approval["execution_authorized"] is False
    assert config["status"] == "HUMAN_APPROVED_PREINFERENCE_NOT_EXECUTION_AUTHORIZED"
    assert config["approved_package_sha256"] == approval["approved_package_sha256"]
    assert config["execution_authorized"] is False
    assert config["scientific_inferences"] == 0


def test_approved_execution_config_hash_is_canonical_and_complete():
    config = read("W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json")
    without_hash = {key: value for key, value in config.items() if key != "execution_config_sha256"}
    expected = hashlib.sha256(json.dumps(without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()
    assert config["execution_config_sha256"] == expected
    assert len(config["configurations"]) == 5
    assert all(item["candidate"] == "A" for item in config["configurations"].values())


def test_asset_manifest_is_identity_only_and_contains_no_checkpoint_bytes():
    manifest = read("W7_P4_CANDIDATE_RUNTIME_ASSET_MANIFEST_V1.json")
    assert manifest["status"] == "PARTIAL_IDENTITY_ONLY_ASSETS_NOT_MATERIALIZED"
    assert manifest["checkpoint_bytes_committed"] is False
    assert len(manifest["assets"]) == 4
    assert all(item["actual_sha256"] == "NOT_MATERIALIZED" for item in manifest["assets"])
    assert read("W7_M3_VOICECRAFT_ASSET_IDENTITY_V1.json")["checkpoint"]["expected_sha256"] == "2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3"


def test_runtime_and_readiness_remain_fail_closed_without_assets():
    env = read("W7_P4_CANDIDATE_RUNTIME_ENVIRONMENTS_V1.json")
    readiness = read("W7_P4_FINAL_EXECUTION_READINESS_AUDIT_V1.json")
    assert env["status"] == "NOT_CREATED_ASSET_OR_DEPENDENCY_GATED"
    assert env["main_environment_modified"] is False
    assert readiness["p4_package_executability"] == "FAIL_MISSING_APPROVED_ASSETS_OR_RUNTIMES"
    assert readiness["authorized_for_reexecution"] is False
    assert readiness["w7_executed"] is False
