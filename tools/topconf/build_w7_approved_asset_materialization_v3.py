"""Write the addition-only W7 approved asset materialization audit.

This builder records the current execution-readiness boundary.  It never
downloads, installs, or accepts checkpoint bytes, and it deliberately does
not create the V6 preregistration manifest.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "research_assurance" / "topconf"
PACKAGE_SHA = "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
CONFIG_SHA = "009CAEDD67EA2CA7C6AA8C4DEF32F87465754A0E3C37E1D95D9403D48E9875C2"
MAP_SHA = "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"
M5_REGISTRY_SHA = "E05F64B5CA7AE542ACFBE6987A8AFFFC746C41BAF8FCBD2847CD679228F2F87C"

M1_REVISION = "2e561ba58618d021b5b8323d3765880f7e0ecfdb"
M3_REVISION = "f0a7a971363905883a21c466a3aa4ea2d4c0b690"
M3_AUDIOCRAFT_REVISION = "c5157b5bf14bf83449c17ea1eeb66c19fb4bc7f0"
M5_CODE_REVISION = "c7cca4135db0c108a30ba8fd6a437fb63a5ecc12"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    asset_manifest = {
        "schema_version": "topconf.w7.approved_runtime_asset_manifest.v3",
        "status": "BLOCKED_OFFICIAL_ASSETS_NOT_MATERIALIZED",
        "current_stage": "W7_FINAL_APPROVED_ASSET_MATERIALIZATION",
        "scientific_config_changed": False,
        "human_approval_invalidated": False,
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "mechanism_case_map_sha256": MAP_SHA,
        "scientific_inferences": 0,
        "real_w7_cases_used": 0,
        "level2_outcomes_accessed": False,
        "checkpoint_bytes_committed": False,
        "assets": [
            {
                "family": "conventional_tts_replacement",
                "role": "official VITS LJS checkpoint",
                "official_source": "jaywalnut310/vits README-linked pretrained model folder",
                "source_revision": M1_REVISION,
                "source_status": "OFFICIAL_CHECKPOINT_NOT_FOUND_OR_MATERIALIZED",
                "filename": "pretrained_ljs.pth",
                "expected_size": "NOT_ESTABLISHED",
                "expected_sha256": "NOT_ESTABLISHED",
                "actual_size": "NOT_MATERIALIZED",
                "actual_sha256": "NOT_MATERIALIZED",
                "license": "SOURCE_LICENSE_AND_CHECKPOINT_LICENSE_SEPARATE; CHECKPOINT_LICENSE_NOT_ESTABLISHED",
                "redistribution": "NOT_ESTABLISHED",
                "logical_path": "runtime_assets/w7_p4/vits/pretrained_ljs.pth",
                "physical_path": "NOT_MATERIALIZED",
            },
            {
                "family": "neural_speech_editing_infilling",
                "role": "VoiceCraft giga830M checkpoint",
                "official_source": "https://huggingface.co/pyp1/VoiceCraft_giga830M",
                "source_revision": M3_REVISION,
                "source_status": "OFFICIAL_SOURCE_UNAVAILABLE_HF_DNS_FAILURE",
                "filename": "giga830M.pth",
                "expected_size": 3358342977,
                "expected_sha256": "2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3",
                "actual_size": "NOT_MATERIALIZED",
                "actual_sha256": "NOT_MATERIALIZED",
                "license": "VoiceCraft model license as documented by pinned repository",
                "redistribution": "NOT_ESTABLISHED",
                "logical_path": "runtime_assets/w7_p4/voicecraft/giga830M.pth",
                "physical_path": "NOT_MATERIALIZED",
            },
            {
                "family": "neural_speech_editing_infilling",
                "role": "VoiceCraft EnCodec asset",
                "official_source": "https://huggingface.co/pyp1/VoiceCraft",
                "source_revision": M3_REVISION,
                "source_status": "OFFICIAL_SOURCE_UNAVAILABLE_HF_DNS_FAILURE",
                "filename": "encodec_4cb2048_giga.th",
                "expected_size": 1167842971,
                "expected_sha256": "caa0c595d4919527a9728d627150aa2a0b15b6d117b21855165851333dc63378",
                "actual_size": "NOT_MATERIALIZED",
                "actual_sha256": "NOT_MATERIALIZED",
                "license": "Follow pinned VoiceCraft model/code terms",
                "redistribution": "NOT_ESTABLISHED",
                "logical_path": "runtime_assets/w7_p4/voicecraft/encodec_4cb2048_giga.th",
                "physical_path": "NOT_MATERIALIZED",
            },
            {
                "family": "voice_conditioned_tts_vc_replacement",
                "role": "v0.7.0 registry-bound YourTTS model artifact",
                "code_version": "Coqui TTS v0.7.0",
                "code_source_revision": M5_CODE_REVISION,
                "model_registry_file": "TTS/.models.json",
                "model_registry_commit": "e9a1953e",
                "model_artifact_release": "v0.6.1_models",
                "model_commit": "e9a1953e",
                "official_source": "https://coqui.gateway.scarf.sh/v0.6.1_models/tts_models--multilingual--multi-dataset--your_tts.zip",
                "registry_source": "https://raw.githubusercontent.com/coqui-ai/TTS/c7cca4135db0c108a30ba8fd6a437fb63a5ecc12/TTS/.models.json",
                "registry_sha256": M5_REGISTRY_SHA,
                "source_status": "OFFICIAL_DOWNLOAD_INCOMPLETE_PARTIAL_QUARANTINED_NOT_ACCEPTED",
                "filename": "tts_models--multilingual--multi-dataset--your_tts.zip",
                "expected_size": "NOT_ESTABLISHED",
                "expected_sha256": "NOT_ESTABLISHED",
                "actual_size": "NOT_MATERIALIZED",
                "actual_sha256": "NOT_MATERIALIZED",
                "license": "CC BY-NC-ND 4.0",
                "redistribution": "NO",
                "logical_path": "runtime_assets/w7_p4/yourtts/tts_models--multilingual--multi-dataset--your_tts.zip",
                "physical_path": "NOT_MATERIALIZED",
                "materialization_note": "An incomplete download was quarantined outside the repository and is not accepted as an asset.",
            },
        ],
    }
    write_json(ROOT / "W7_APPROVED_RUNTIME_ASSET_MANIFEST_V3.json", asset_manifest)

    environments = {
        "schema_version": "topconf.w7.approved_runtime_environments.v3",
        "status": "BLOCKED_RUNTIME_NOT_CREATED",
        "current_stage": "W7_FINAL_APPROVED_ASSET_MATERIALIZATION",
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "scientific_config_changed": False,
        "human_approval_invalidated": False,
        "main_environment_modified": False,
        "host": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "architecture": platform.machine(),
            "cuda": "NOT_USED",
        },
        "runtimes": {
            "runtime_m1_vits": {
                "python": "3.9_or_3.10_official_requirements_target",
                "implementation_revision": M1_REVISION,
                "torch": "NOT_ESTABLISHED",
                "status": "BLOCKED_MISSING_CHECKPOINT; RUNTIME_NOT_CREATED",
            },
            "runtime_m3_voicecraft": {
                "python": "3.9.16",
                "implementation_revision": M3_REVISION,
                "torch": "2.0.1",
                "torchaudio": "2.0.2",
                "xformers": "0.0.22",
                "audiocraft_revision": M3_AUDIOCRAFT_REVISION,
                "status": "BLOCKED_MISSING_ASSETS_AND_DEPENDENCIES; RUNTIME_NOT_CREATED",
            },
            "runtime_m5_yourtts": {
                "python": "3.10",
                "implementation_revision": "23904e6b7158d42cacf2a94dba0791ef69f1e2a9",
                "coqui_tts": "0.7.0",
                "model_registry_commit": "e9a1953e",
                "status": "BLOCKED_MISSING_MODEL_ARTIFACT_AND_TTS_PACKAGE; RUNTIME_NOT_CREATED",
            },
        },
    }
    write_json(ROOT / "W7_APPROVED_RUNTIME_ENVIRONMENTS_V3.json", environments)

    audit = {
        "schema_version": "topconf.w7.final_approved_asset_materialization_audit.v1",
        "current_stage": "W7_FINAL_APPROVED_ASSET_MATERIALIZATION",
        "p4_scientific_specification": "FROZEN",
        "p4_human_approval": "COMPLETE",
        "human_approval_invalidated": "NO",
        "scientific_config_changed": False,
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "mechanism_case_map_sha256": MAP_SHA,
        "scientific_approval": {"M1": "APPROVED", "M2": "APPROVED", "M3": "APPROVED", "M4": "APPROVED", "M5": "APPROVED"},
        "execution_readiness": {"M1": "BLOCKED_ASSET", "M2": "PASS", "M3": "BLOCKED_ASSET_RUNTIME", "M4": "PASS", "M5": "BLOCKED_ASSET_RUNTIME"},
        "w7_execution_readiness": "FAIL_BLOCKED_ASSET_RUNTIME",
        "w7_execution_authorized": False,
        "w7_executed": False,
        "w7_scientific_inferences": 0,
        "real_w7_cases_used": 0,
        "level2_outcomes_accessed": False,
        "strict_load_smoke_determinism": "NOT_RUN_ASSET_RUNTIME_GATES_BLOCKED",
        "preregistration_manifest_v6": "NOT_GENERATED_UNTIL_ALL_ASSET_RUNTIME_GATES_PASS",
        "exact_blockers": [
            "M1 official pretrained_ljs.pth is not materialized.",
            "M3 exact giga830M.pth and encodec_4cb2048_giga.th are not materialized; official Hugging Face retrieval was unavailable and the isolated runtime is not created.",
            "M5 registry-bound YourTTS archive is not materialized; the incomplete official download is quarantined and the isolated Coqui TTS 0.7.0 runtime is not created.",
        ],
    }
    write_json(ROOT / "W7_FINAL_APPROVED_ASSET_MATERIALIZATION_AUDIT_V1.json", audit)
    (ROOT / "W7_FINAL_APPROVED_ASSET_MATERIALIZATION_AUDIT_V1.md").write_text(
        "# W7 final approved asset materialization audit v1\n\n"
        "P4 scientific specification is frozen and human approval is complete. The execution gate remains blocked because the exact official M1, M3, and M5 assets and isolated runtimes are not materialized. M2 and M4 remain executable PASS controls.\n\n"
        "The incomplete M5 official download is quarantined outside the repository and is not accepted as an asset. No checkpoint bytes are committed. V6 is intentionally not generated, and no W7, Level-2, or metric computation was performed.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": audit["w7_execution_readiness"], "v6": audit["preregistration_manifest_v6"], "scientific_inferences": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
