"""Correct M5 registry provenance and write state-machine-aware runtime manifests."""
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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    asset_manifest = {
        "schema_version": "topconf.w7.approved_runtime_asset_manifest.v2",
        "status": "PARTIAL_IDENTITY_ONLY_ASSETS_NOT_MATERIALIZED",
        "asset_provenance_correction": True,
        "scientific_config_changed": False,
        "human_approval_invalidated": False,
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "mechanism_case_map_sha256": MAP_SHA,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "assets": [
            {"family": "conventional_tts_replacement", "role": "official VITS LJS checkpoint", "official_source": "jaywalnut310/vits README-linked pretrained model folder", "source_revision": "2e561ba58618d021b5b8323d3765880f7e0ecfdb", "filename": "pretrained_ljs.pth", "size": "NOT_ESTABLISHED", "sha256": "NOT_MATERIALIZED", "license": "SOURCE_LICENSE_AND_CHECKPOINT_LICENSE_SEPARATE; CHECKPOINT_LICENSE_NOT_ESTABLISHED", "redistribution": "NOT_ESTABLISHED", "logical_path": "runtime_assets/w7_p4/vits/pretrained_ljs.pth", "physical_path": "NOT_MATERIALIZED"},
            {"family": "neural_speech_editing_infilling", "role": "VoiceCraft giga830M checkpoint", "official_source": "https://huggingface.co/pyp1/VoiceCraft_giga830M", "source_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "filename": "giga830M.pth", "size": 3358342977, "sha256": "2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3", "actual_size": "NOT_MATERIALIZED", "actual_sha256": "NOT_MATERIALIZED", "license": "VoiceCraft model license as documented by pinned repository", "redistribution": "NOT_ESTABLISHED", "logical_path": "runtime_assets/w7_p4/voicecraft/giga830M.pth", "physical_path": "NOT_MATERIALIZED"},
            {"family": "neural_speech_editing_infilling", "role": "VoiceCraft EnCodec asset", "official_source": "https://huggingface.co/pyp1/VoiceCraft", "source_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "filename": "encodec_4cb2048_giga.th", "size": "NOT_ESTABLISHED", "sha256": "NOT_MATERIALIZED", "license": "Follow pinned VoiceCraft model/code terms", "redistribution": "NOT_ESTABLISHED", "logical_path": "runtime_assets/w7_p4/voicecraft/encodec_4cb2048_giga.th", "physical_path": "NOT_MATERIALIZED"},
            {"family": "voice_conditioned_tts_vc_replacement", "role": "v0.7.0 registry-bound YourTTS model artifact", "code_version": "Coqui TTS v0.7.0", "code_source_revision": "c7cca4135db0c108a30ba8fd6a437fb63a5ecc12", "model_registry_file": "TTS/.models.json", "model_registry_commit": "e9a1953e", "model_artifact_release": "v0.6.1_models", "model_commit": "e9a1953e", "official_source": "https://coqui.gateway.scarf.sh/v0.6.1_models/tts_models--multilingual--multi-dataset--your_tts.zip", "registry_source": "https://raw.githubusercontent.com/coqui-ai/TTS/c7cca4135db0c108a30ba8fd6a437fb63a5ecc12/TTS/.models.json", "registry_sha256": M5_REGISTRY_SHA, "filename": "tts_models--multilingual--multi-dataset--your_tts.zip", "size": "NOT_ESTABLISHED", "sha256": "NOT_MATERIALIZED", "license": "CC BY-NC-ND 4.0", "redistribution": "NO", "logical_path": "runtime_assets/w7_p4/yourtts/tts_models--multilingual--multi-dataset--your_tts.zip", "physical_path": "NOT_MATERIALIZED"},
        ],
        "checkpoint_bytes_committed": False,
        "v1_provenance_superseded_by_addition_only": True,
    }
    write_json(ROOT / "W7_APPROVED_RUNTIME_ASSET_MANIFEST_V2.json", asset_manifest)
    (ROOT / "W7_APPROVED_RUNTIME_ASSET_MANIFEST_V2.md").write_text(
        "# W7 approved runtime asset manifest v2\n\n"
        "V2 corrects M5 provenance only. Coqui TTS code remains pinned to v0.7.0, while its registry entry resolves the YourTTS model artifact through the v0.6.1_models release path with model commit e9a1953e. This is not a scientific configuration change and does not invalidate human approval.\n\n"
        "M1, M3, and M5 artifacts remain unmaterialized because no exact local assets were found and official retrieval/runtime closure is incomplete. No checkpoint bytes are committed.\n",
        encoding="utf-8",
    )

    environments = {
        "schema_version": "topconf.w7.approved_runtime_environments.v2",
        "status": "NOT_READY_ASSET_AND_RUNTIME_GATED",
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "scientific_config_changed": False,
        "human_approval_invalidated": False,
        "host": {"os": platform.platform(), "python": platform.python_version(), "architecture": platform.machine(), "cuda": "NOT_USED"},
        "runtimes": {
            "runtime_m1_vits": {"python": "3.9_or_3.10_official_requirements_target", "implementation_revision": "2e561ba58618d021b5b8323d3765880f7e0ecfdb", "torch": "NOT_ESTABLISHED", "status": "BLOCKED_MISSING_CHECKPOINT"},
            "runtime_m3_voicecraft": {"python": "3.9.16", "implementation_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "torch": "2.0.1", "torchaudio": "2.0.2", "xformers": "0.0.22", "audiocraft_revision": "c5157b5bf14bf83449c17ea1eeb66c19fb4bc7f0", "status": "BLOCKED_MISSING_CHECKPOINT_AND_RUNTIME_DEPENDENCIES"},
            "runtime_m5_yourtts": {"python": "3.10", "implementation_revision": "23904e6b7158d42cacf2a94dba0791ef69f1e2a9", "coqui_tts": "0.7.0", "model_registry_commit": "e9a1953e", "status": "BLOCKED_MISSING_MODEL_ARTIFACT_AND_TTS_PACKAGE"},
        },
        "main_environment_modified": False,
    }
    write_json(ROOT / "W7_APPROVED_RUNTIME_ENVIRONMENTS_V2.json", environments)

    readiness = {
        "schema_version": "topconf.w7.approved_asset_recovery_readiness.v2",
        "current_stage": "W7_APPROVED_ASSET_RECOVERY_AND_RUNTIME_CLOSURE",
        "p4_scientific_specification": "FROZEN",
        "p4_human_approval": "COMPLETE",
        "human_approval_invalidated": False,
        "scientific_config_changed": False,
        "approved_package_sha256": PACKAGE_SHA,
        "approved_execution_config_sha256": CONFIG_SHA,
        "mechanism_case_map_sha256": MAP_SHA,
        "w7_scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "real_w7_cases_used": 0,
        "scientific_approval": {"M1": "APPROVED", "M2": "APPROVED", "M3": "APPROVED", "M4": "APPROVED", "M5": "APPROVED"},
        "execution_readiness": {"M1": "BLOCKED_ASSET", "M2": "PASS", "M3": "BLOCKED_ASSET_RUNTIME", "M4": "PASS", "M5": "BLOCKED_ASSET_RUNTIME"},
        "m5_provenance_correction": "YES",
        "p4_package_executability": "FAIL_MISSING_APPROVED_ASSETS_OR_RUNTIMES",
        "w7_execution_readiness": "FAIL_BLOCKED_ASSET_RUNTIME",
        "w7_execution_authorized": False,
        "w7_executed": False,
        "exact_remaining_blockers": ["M1 official pretrained_ljs.pth not materialized.", "M3 exact giga830M.pth and EnCodec assets not materialized; isolated Python 3.9.16/audiocraft/xformers runtime not established.", "M5 v0.7.0 registry-bound YourTTS archive not materialized; isolated Python 3.10/TTS 0.7.0 runtime not established."],
    }
    write_json(ROOT / "W7_APPROVED_ASSET_RECOVERY_READINESS_V2.json", readiness)
    (ROOT / "W7_APPROVED_ASSET_RECOVERY_READINESS_V2.md").write_text(
        "# W7 approved asset recovery readiness v2\n\n"
        "Scientific approval is complete and unchanged. M5 provenance is corrected to the v0.7.0 registry-bound v0.6.1_models artifact at model commit e9a1953e.\n\n"
        "Execution readiness remains blocked: M1 lacks pretrained_ljs.pth; M3 lacks giga830M.pth/EnCodec and its isolated dependencies; M5 lacks the registry-bound archive and TTS 0.7.0 runtime. M2 and M4 remain PASS.\n\n"
        "No W7 case, Level-2 outcome, metric, or checkpoint bytes were accessed or committed.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": readiness["w7_execution_readiness"], "m5_registry_commit": "e9a1953e", "scientific_config_changed": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
