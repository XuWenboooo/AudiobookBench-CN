"""Record human approval and materialize the approved config without executing W7."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "research_assurance" / "topconf"
PACKAGE_PATH = ROOT / "W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1.json"
PACKAGE_SHA = "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
MAP_SHA = "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest().upper()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    if package.get("proposed_package_sha256") != PACKAGE_SHA or package.get("mechanism_case_map_sha256") != MAP_SHA:
        raise SystemExit("immutable package hash gate failed")

    approval = {
        "schema_version": "topconf.w7.p4.human_approval_record.v1",
        "approval_date": "2026-09-21",
        "approval_status": "RECORDED_PREINFERENCE_ONLY",
        "approved_package": "W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1",
        "approved_package_sha256": PACKAGE_SHA,
        "approved_case_map_sha256": MAP_SHA,
        "approved_families": {
            family: {"candidate": "A", "implementation": package["families"][family]["candidate"]["implementation_name"], "bundle_hash": package["families"][family]["candidate"]["bundle_hash"]}
            for family in package["families"]
        },
        "p4_fields_resolved": 35,
        "w7_scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "execution_authorized": False,
        "confirmatory_outcomes_accessed": False,
        "approval_scope": "final outcome-blind pre-inference mechanism specification only",
    }
    approval_sha = sha(approval)
    approval["approval_record_sha256"] = approval_sha
    write_json(ROOT / "W7_P4_HUMAN_APPROVAL_RECORD_V1.json", approval)
    (ROOT / "W7_P4_HUMAN_APPROVAL_RECORD_V1.md").write_text(
        "# W7 P4 human approval record v1\n\n"
        "Human approval was recorded for the five Candidate A bundles as a pre-inference scientific specification only. It does not authorize formal W7 execution.\n\n"
        f"Approved package SHA256: `{PACKAGE_SHA}`\n\nApproved case-map SHA256: `{MAP_SHA}`\n\n"
        "W7 scientific inferences: `0`\n\nLevel-2 outcomes accessed: `NO`\n\nFormal W7 execution authorized: `NO`\n",
        encoding="utf-8",
    )

    configurations = {}
    required = ("implementation", "version", "parameter_set_id", "reference_rule", "target_span_rule", "sample_rate", "codec_path", "seed_policy", "quality_gate_policy", "failure_policy", "normalization_policy", "parameters")
    for family, record in package["families"].items():
        candidate = record["candidate"]
        configurations[family] = {key: candidate[key] for key in required} | {
            "candidate": "A",
            "bundle_hash": candidate["bundle_hash"],
            "entrypoint": candidate["entrypoint"],
            "source_revision": candidate["source_revision"],
        }
    config = {
        "schema_version": "topconf.w7.mechanism_execution_config.approved_preinference.v1",
        "status": "HUMAN_APPROVED_PREINFERENCE_NOT_EXECUTION_AUTHORIZED",
        "approved_package_sha256": PACKAGE_SHA,
        "approval_record_sha256": approval_sha,
        "mechanism_case_map_sha256": MAP_SHA,
        "family_registry": list(configurations),
        "configurations": configurations,
        "implementation_bindings_complete": True,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "execution_authorized": False,
        "real_w7_cases_used": 0,
    }
    config_sha = sha(config)
    config["execution_config_sha256"] = config_sha
    write_json(ROOT / "W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json", config)

    assets = {
        "schema_version": "topconf.w7.p4.candidate_runtime_asset_manifest.v1",
        "status": "PARTIAL_IDENTITY_ONLY_ASSETS_NOT_MATERIALIZED",
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "assets": [
            {"family": "conventional_tts_replacement", "role": "official VITS LJS checkpoint", "source": "https://drive.google.com/drive/folders/1ksarh-cJf3F5eKJjLVWY0X1j1qsQqiS2", "source_revision": "2e561ba58618d021b5b8323d3765880f7e0ecfdb", "filename": "pretrained_ljs.pth", "expected_size": "NOT_ESTABLISHED", "expected_sha256": "NOT_ESTABLISHED", "actual_size": "NOT_MATERIALIZED", "actual_sha256": "NOT_MATERIALIZED", "local_logical_path": "runtime_assets/w7_p4/vits/pretrained_ljs.pth", "physical_storage_identity": "NOT_MATERIALIZED", "rights": "RESTRICTED_LOCAL_RESEARCH; REDISTRIBUTION_NOT_ESTABLISHED", "redistribution": "NOT_ESTABLISHED"},
            {"family": "neural_speech_editing_infilling", "role": "VoiceCraft giga830M checkpoint", "source": "https://huggingface.co/pyp1/VoiceCraft_giga830M", "source_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "filename": "giga830M.pth", "expected_size": 3358342977, "expected_sha256": "2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3", "actual_size": "NOT_MATERIALIZED", "actual_sha256": "NOT_MATERIALIZED", "local_logical_path": "runtime_assets/w7_p4/voicecraft/giga830M.pth", "physical_storage_identity": "NOT_MATERIALIZED", "rights": "RESTRICTED_LOCAL_RESEARCH; REDISTRIBUTION_NOT_ESTABLISHED", "redistribution": "NOT_ESTABLISHED"},
            {"family": "neural_speech_editing_infilling", "role": "official VoiceCraft EnCodec asset", "source": "https://huggingface.co/pyp1/VoiceCraft", "source_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "filename": "encodec_4cb2048_giga.th", "expected_size": "NOT_ESTABLISHED", "expected_sha256": "NOT_ESTABLISHED", "actual_size": "NOT_MATERIALIZED", "actual_sha256": "NOT_MATERIALIZED", "local_logical_path": "runtime_assets/w7_p4/voicecraft/encodec_4cb2048_giga.th", "physical_storage_identity": "NOT_MATERIALIZED", "rights": "RESTRICTED_LOCAL_RESEARCH; REDISTRIBUTION_NOT_ESTABLISHED", "redistribution": "NOT_ESTABLISHED"},
            {"family": "voice_conditioned_tts_vc_replacement", "role": "official YourTTS released model package", "source": "https://github.com/Edresson/YourTTS/releases/download/MOS/Audios_MOS.zip; https://github.com/coqui-ai/TTS/releases/download/v0.5.0_models/tts_models--multilingual--multi-dataset--your_tts.zip", "source_revision": "23904e6b7158d42cacf2a94dba0791ef69f1e2a9; c7cca4135db0c108a30ba8fd6a437fb63a5ecc12", "filename": "tts_models--multilingual--multi-dataset--your_tts.zip", "expected_size": "NOT_ESTABLISHED", "expected_sha256": "NOT_ESTABLISHED", "actual_size": "NOT_MATERIALIZED", "actual_sha256": "NOT_MATERIALIZED", "local_logical_path": "runtime_assets/w7_p4/yourtts/tts_models--multilingual--multi-dataset--your_tts.zip", "physical_storage_identity": "NOT_MATERIALIZED", "rights": "RESTRICTED_LOCAL_RESEARCH; CC BY-NC-ND 4.0 checkpoint; DO_NOT_REDISTRIBUTE", "redistribution": "NO"},
        ],
        "checkpoint_bytes_committed": False,
    }
    write_json(ROOT / "W7_P4_CANDIDATE_RUNTIME_ASSET_MANIFEST_V1.json", assets)
    write_json(ROOT / "W7_M1_VITS_ASSET_IDENTITY_V1.json", assets["assets"][0])
    write_json(ROOT / "W7_M3_VOICECRAFT_ASSET_IDENTITY_V1.json", {"checkpoint": assets["assets"][1], "codec": assets["assets"][2]})
    write_json(ROOT / "W7_M5_YOURTTS_ASSET_IDENTITY_V1.json", assets["assets"][3])
    (ROOT / "W7_M1_VITS_ASSET_IDENTITY_V1.md").write_text("# W7 M1 VITS asset identity v1\n\nNo local official checkpoint was found. Expected identity is `pretrained_ljs.pth` from the pinned jaywalnut310/vits README-linked source; size and SHA-256 remain `NOT_ESTABLISHED` until official retrieval succeeds. No checkpoint was downloaded or committed.\n", encoding="utf-8")
    (ROOT / "W7_M3_VOICECRAFT_ASSET_IDENTITY_V1.md").write_text("# W7 M3 VoiceCraft asset identity v1\n\nCandidate A requires `giga830M.pth`, expected size `3358342977` and SHA-256 `2454b51575822a04d24a00f8ba78f201f916439ffa62a3c1ac0ffa5220f429e3`. The local asset was not found and no checkpoint or EnCodec bytes were downloaded or committed.\n", encoding="utf-8")
    (ROOT / "W7_M5_YOURTTS_ASSET_IDENTITY_V1.md").write_text("# W7 M5 YourTTS asset identity v1\n\nCandidate A requires the frozen Coqui YourTTS release package under the pinned v0.7.0 runtime path. No local checkpoint/package was found; size and SHA-256 remain `NOT_ESTABLISHED`. YourTTS released checkpoints are restricted and must not be redistributed.\n", encoding="utf-8")

    dependency_state = {name: importlib.util.find_spec(name) is not None for name in ("torch", "torchaudio", "scipy", "numpy", "audiocraft", "xformers", "TTS")}
    environments = {
        "schema_version": "topconf.w7.p4.candidate_runtime_environments.v1",
        "status": "NOT_CREATED_ASSET_OR_DEPENDENCY_GATED",
        "host": {"os": platform.platform(), "python": platform.python_version(), "architecture": platform.machine()},
        "environments": {
            "runtime_m1_vits": {"target_python": "3.9_or_3.10_pinned_by_official_requirements", "implementation_revision": "2e561ba58618d021b5b8323d3765880f7e0ecfdb", "status": "NOT_CREATED_MISSING_CHECKPOINT", "dependencies_observed": dependency_state},
            "runtime_m3_voicecraft": {"target_python": "3.9.16", "implementation_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690", "audiocraft_revision": "c5157b5bf14bf83449c17ea1eeb66c19fb4bc7f0", "xformers": "0.0.22", "torch": "2.0.1", "torchaudio": "2.0.2", "status": "NOT_CREATED_MISSING_CHECKPOINT_AND_DEPENDENCIES", "dependencies_observed": dependency_state},
            "runtime_m5_yourtts": {"target_python": "3.10", "implementation_revision": "23904e6b7158d42cacf2a94dba0791ef69f1e2a9", "coqui_tts": "0.7.0", "status": "NOT_CREATED_MISSING_CHECKPOINT_AND_PACKAGE", "dependencies_observed": dependency_state},
        },
        "main_environment_modified": False,
    }
    write_json(ROOT / "W7_P4_CANDIDATE_RUNTIME_ENVIRONMENTS_V1.json", environments)

    download_audit = {
        "schema_version": "topconf.w7.p4.candidate_download_audit.v1",
        "status": "NO_DOWNLOAD_COMPLETED_OFFICIAL_NETWORK_UNAVAILABLE",
        "attempt_date": "2026-09-21",
        "records": [
            {"family": "conventional_tts_replacement", "source": "official VITS README-linked Google Drive", "expected_identity": "pretrained_ljs.pth; hash not previously frozen", "attempt": "NOT_STARTED_AFTER_LOCAL_MISS; official network retrieval not completed", "fallback": "NONE"},
            {"family": "neural_speech_editing_infilling", "source": "official VoiceCraft/Hugging Face source", "expected_identity": "giga830M.pth; size/hash recorded above", "attempt": "NOT_STARTED_AFTER_LOCAL_MISS; official network retrieval not completed", "fallback": "NONE"},
            {"family": "voice_conditioned_tts_vc_replacement", "source": "official Coqui/YourTTS release source", "expected_identity": "frozen YourTTS v0.7.0 model path", "attempt": "NOT_STARTED_AFTER_LOCAL_MISS; official network retrieval not completed", "fallback": "NONE"},
        ],
        "silent_mirror_fallback": False,
        "checkpoint_bytes_committed": False,
    }
    write_json(ROOT / "W7_P4_CANDIDATE_DOWNLOAD_AUDIT_V1.json", download_audit)

    readiness = {
        "schema_version": "topconf.w7.p4.final_execution_readiness_audit.v1",
        "current_stage": "W7_P4_CANDIDATE_ASSET_MATERIALIZATION_AND_RUNTIME_CLOSURE",
        "human_approval_recorded": True,
        "approved_package_sha256": PACKAGE_SHA,
        "approval_record_sha256": approval_sha,
        "execution_config_sha256": config_sha,
        "execution_config_status": config["status"],
        "mechanism_case_map_sha256": MAP_SHA,
        "package_unchanged": True,
        "real_w7_cases_used": 0,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "m1_model_load": "BLOCKED_MISSING_CHECKPOINT",
        "m1_synthetic_execution": "NOT_RUN",
        "m1_determinism": "NOT_RUN",
        "m2_synthetic_regression": "PASS",
        "m3_model_load": "BLOCKED_MISSING_CHECKPOINT_AND_RUNTIME_DEPENDENCIES",
        "m3_synthetic_execution": "NOT_RUN",
        "m3_determinism": "NOT_RUN",
        "m4_synthetic_regression": "PASS",
        "m5_model_load": "BLOCKED_MISSING_CHECKPOINT_AND_TTS_PACKAGE",
        "m5_synthetic_execution": "NOT_RUN",
        "m5_determinism": "NOT_RUN",
        "p4_package_executability": "FAIL_MISSING_APPROVED_ASSETS_OR_RUNTIMES",
        "authorized_for_reexecution": False,
        "w7_executed": False,
        "exact_remaining_blockers": ["M1 official pretrained_ljs.pth absent locally and official retrieval incomplete.", "M3 official giga830M.pth/EnCodec assets absent locally; audiocraft and xformers unavailable; Windows-compatible isolated runtime not established.", "M5 frozen YourTTS package absent locally; TTS==0.7.0 runtime not established."],
    }
    write_json(ROOT / "W7_P4_FINAL_EXECUTION_READINESS_AUDIT_V1.json", readiness)
    (ROOT / "W7_P4_FINAL_EXECUTION_READINESS_AUDIT_V1.md").write_text("# W7 P4 final execution-readiness audit v1\n\nHuman approval is recorded for the pre-inference mechanism specification, and the approved executable configuration is materialized and hashed. Formal W7 execution remains unauthorized.\n\nM2 and M4 synthetic regressions pass. M1, M3, and M5 remain blocked because approved model assets are absent locally; M3 also lacks audiocraft/xformers and M5 lacks TTS==0.7.0. No checkpoint bytes were downloaded or committed.\n\n`P4_PACKAGE_EXECUTABILITY = FAIL_MISSING_APPROVED_ASSETS_OR_RUNTIMES`\n", encoding="utf-8")
    print(json.dumps({"approval_sha256": approval_sha, "execution_config_sha256": config_sha, "readiness": readiness["p4_package_executability"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
