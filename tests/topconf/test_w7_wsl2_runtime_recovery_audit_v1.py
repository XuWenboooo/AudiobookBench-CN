import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def test_wsl2_audit_records_authorized_feature_enablement_and_fail_closed_runtime():
    audit = json.loads((ROOT / "W7_WSL2_RUNTIME_RECOVERY_AUDIT_V1.json").read_text(encoding="utf-8"))
    assert audit["system_level_wsl2_installation_authorized"] is True
    assert audit["windows_features"] == {
        "Microsoft-Windows-Subsystem-Linux": "Enabled",
        "VirtualMachinePlatform": "Enabled",
    }
    assert audit["wsl_reboot_required"] is True
    assert audit["wsl_reboot_occurred"] is True
    assert audit["wsl2_distro"] == "NOT_INSTALLED"
    assert audit["wsl2_version"] == "NOT_AVAILABLE"
    assert audit["official_wsl_msi_attempt"]["accepted"] is False
    assert audit["main_windows_python_modified"] is False
    assert audit["asset_manifest_v4"] == "NOT_GENERATED_UNTIL_ACTUAL_ASSETS_EXIST"
    assert audit["environment_manifest_v4"] == "NOT_GENERATED_UNTIL_ACTUAL_RUNTIMES_EXIST"
    assert audit["prereg_manifest_v6"] == "NOT_GENERATED_UNTIL_M1_M2_M3_M4_M5_PASS"
    assert audit["w7_execution_authorized"] is False
    assert audit["w7_executed"] is False
