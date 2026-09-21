import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_wsl2_preflight_is_fail_closed_without_mutating_main_environment():
    evidence = read("W7_WSL2_RUNTIME_RECOVERY_PREFLIGHT_V1.json")
    assert evidence["wsl2_status"] == "NOT_INSTALLED"
    assert evidence["wsl2_distro"] == "NOT_AVAILABLE"
    assert evidence["wsl2_kernel"] == "NOT_AVAILABLE"
    assert evidence["wsl2_gpu_visible"] == "NOT_APPLICABLE_WSL2_NOT_INSTALLED"
    assert evidence["windows_main_environment_modified"] is False
    assert evidence["asset_materialization"] == "BLOCKED"
    assert evidence["environment_materialization"] == "BLOCKED"
    assert evidence["quarantined_partial_download"]["accepted_as_asset"] is False
    assert evidence["scientific_inferences"] == 0
    assert evidence["level2_outcomes_accessed"] is False
    assert evidence["real_w7_cases_used"] == 0
