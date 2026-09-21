"""Build five complete, outcome-blind Candidate-A bundles for human review."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "research_assurance" / "topconf"
sys.path.insert(0, str(REPO / "src"))

from audiobookbench.topconf.w7_mechanism_spec import FAMILY_IDS  # noqa: E402


MAP_SHA = "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"
PROJECT_TRANSFORM_VERSION = "w7_candidate_transforms_v1"
SCIPY_VERSION = "1.11.4"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest().upper()


def project_revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def project_control(identity: str, effect: str, reference: str, target: str, parameters: dict[str, object]) -> dict[str, object]:
    return {
        "candidate": "A",
        "implementation_name": "AudiobookBench deterministic waveform control adapter",
        "implementation": f"audiobookbench.topconf.w7_candidate_transforms::{identity}",
        "repository": "AudiobookBench-CN",
        "version": PROJECT_TRANSFORM_VERSION,
        "source_revision": project_revision(),
        "source_file": "src/audiobookbench/topconf/w7_candidate_transforms.py",
        "entrypoint": identity,
        "dependency_backend_version": f"numpy==2.5.2; linear interpolation and float32 NumPy path; source version {PROJECT_TRANSFORM_VERSION}",
        "parameter_set_id": f"{identity.upper()}_CANONICAL_V1",
        "reference_rule": reference,
        "target_span_rule": target,
        "sample_rate": 16000,
        "codec_path": "NOT_APPLICABLE",
        "seed_policy": "No stochastic operation; existing case seed is not consumed",
        "quality_gate_policy": "finite waveform; mono; valid duration; sample rate 16000; clip only to [-1,1]; structural contract checks",
        "failure_policy": "terminal_generation_or_quality_failure; no_drop; no_impute; no_outcome_retry",
        "channel_policy": "downmix channel-last input by arithmetic mean before transform; output mono",
        "normalization_policy": "no loudness normalization; finite float32 samples are clipped to [-1,1]",
        "output_sample_rate_policy": "output is 16000 Hz",
        "scientific_effect": effect,
        "parameters": parameters,
        "official_provenance": {
            "type": "project_owned_deterministic_adapter",
            "source": "project source file and pinned repository revision; no performance evidence used",
        },
    }


def build() -> dict[str, object]:
    families: dict[str, dict[str, object]] = {}
    families["conventional_tts_replacement"] = {
        "recommended_candidate": "A",
        "alternatives": [],
        "candidate": {
            "candidate": "A",
            "implementation_name": "VITS official single-speaker TTS",
            "implementation": "jaywalnut310/vits",
            "repository": "https://github.com/jaywalnut310/vits",
            "version": "commit 2e561ba58618d021b5b8323d3765880f7e0ecfdb",
            "source_revision": "2e561ba58618d021b5b8323d3765880f7e0ecfdb",
            "source_file": "configs/ljs_base.json; inference.ipynb",
            "entrypoint": "SynthesizerTrn.infer",
            "dependency_backend_version": "official requirements.txt at the pinned commit; PyTorch runtime is environment-bound and must be recorded at execution",
            "model_checkpoint": "official VITS pretrained LJS checkpoint named pretrained_ljs.pth from the repository README-linked release folder",
            "model_source": "https://drive.google.com/drive/folders/1ksarh-cJf3F5eKJjLVWY0X1j1qsQqiS2",
            "parameter_set_id": "VITS_LJS_CANONICAL_V1",
            "reference_rule": "No external waveform reference; synthesize the frozen case target transcript with the pinned single-speaker LJS checkpoint.",
            "target_span_rule": "Replace exactly the frozen case target span [gt.start_sec, gt.end_sec); generated audio is linearly resampled to the target duration before deterministic boundary insertion.",
            "sample_rate": 16000,
            "codec_path": "NOT_APPLICABLE",
            "seed_policy": "SHA256(protocol_id||distribution_id||case_id||mechanism_family||W7_MECHANISM_SEED_V1)[:64bits], converted to unsigned 64-bit and applied to Python/NumPy/PyTorch before inference",
            "quality_gate_policy": "finite waveform; mono; exact target-span insertion; output 16000 Hz; no corruption; contract structural checks",
            "failure_policy": "terminal_generation_or_quality_failure; no_drop; no_impute; no_outcome_retry",
            "channel_policy": "model output is mono; any input is downmixed by the project adapter",
            "normalization_policy": "no loudness normalization; preserve model waveform scale and clip only to [-1,1] at the adapter boundary",
            "output_sample_rate_policy": "VITS official LJS config sampling_rate=22050; resample 22050→16000 with scipy.signal.resample_poly(up=320, down=441), SciPy 1.11.4",
            "scientific_effect": "text-conditioned waveform generation replacing the frozen target span",
            "parameters": {
                "config_file": "configs/ljs_base.json",
                "text_cleaners": ["english_cleaners2"],
                "noise_scale": 0.667,
                "noise_scale_w": 0.8,
                "length_scale": 1.0,
                "sampling_rate_native": 22050,
                "filter_length": 1024,
                "hop_length": 256,
                "win_length": 1024,
                "n_mel_channels": 80,
            },
            "official_provenance": [
                "https://github.com/jaywalnut310/vits/tree/2e561ba58618d021b5b8323d3765880f7e0ecfdb",
                "https://raw.githubusercontent.com/jaywalnut310/vits/2e561ba58618d021b5b8323d3765880f7e0ecfdb/configs/ljs_base.json",
                "https://raw.githubusercontent.com/jaywalnut310/vits/2e561ba58618d021b5b8323d3765880f7e0ecfdb/inference.ipynb",
                "https://arxiv.org/abs/2106.06103",
            ],
        },
    }
    families["cross_speaker_boundary_control"] = {
        "recommended_candidate": "A",
        "alternatives": [],
        "candidate": project_control(
            "cross_speaker_boundary",
            "cross-speaker waveform replacement at the frozen target interval with deterministic boundary crossfades",
            "reference is the next lexicographically ordered case in the same distribution with a different source_id; take its first available mono waveform window and resample it to target duration",
            "target span is the frozen GT interval [start_sample, end_sample) at 16000 Hz; no per-case manual selection",
            {"crossfade_samples": 400, "reference_window": "first available reference waveform window", "interpolation": "linear", "boundary_fallback": "terminal failure if no distinct-speaker reference exists"},
        ),
    }
    families["neural_speech_editing_infilling"] = {
        "recommended_candidate": "A",
        "alternatives": [],
        "candidate": {
            "candidate": "A",
            "implementation_name": "VoiceCraft official neural codec language model",
            "implementation": "jasonppy/VoiceCraft",
            "repository": "https://github.com/jasonppy/VoiceCraft",
            "version": "commit f0a7a971363905883a21c466a3aa4ea2d4c0b690",
            "source_revision": "f0a7a971363905883a21c466a3aa4ea2d4c0b690",
            "source_file": "tts_demo.py; inference_tts_scale.py; models/voicecraft.py",
            "entrypoint": "inference_tts_scale.inference_one_sample",
            "dependency_backend_version": "official README environment: Python 3.9.16, torch 2.0.1, torchaudio 2.0.2, audiocraft commit c5157b5bf14bf83449c17ea1eeb66c19fb4bc7f0, xformers 0.0.22, MFA 2.2.17",
            "model_checkpoint": "pyp1/VoiceCraft_VoiceCraft_giga830M",
            "model_source": "https://huggingface.co/pyp1/VoiceCraft_giga830M",
            "codec_checkpoint": "pyp1/VoiceCraft/encodec_4cb2048_giga.th",
            "parameter_set_id": "VOICECRAFT_GIGA830M_CANONICAL_V1",
            "reference_rule": "Use the same-case source waveform and frozen source transcript; forced alignment identifies the deterministic boundary around the frozen target interval.",
            "target_span_rule": "MFA english_us_arpa alignment at beam=50 and retry_beam=200; choose the first word boundary at or after frozen gt.start_sec and the first boundary at or after frozen gt.end_sec; terminal failure if either boundary is absent.",
            "sample_rate": 16000,
            "codec_path": "Encodec 4-codebook 2048-entry model at 16000 Hz from official VoiceCraft source",
            "seed_policy": "SHA256(protocol_id||distribution_id||case_id||mechanism_family||W7_MECHANISM_SEED_V1)[:64bits], converted to unsigned 64-bit and applied to Python/NumPy/PyTorch/CUDA deterministic settings",
            "quality_gate_policy": "finite waveform; mono; output 16000 Hz; valid alignment; no corruption; structural contract checks",
            "failure_policy": "terminal_generation_or_quality_failure; no_drop; no_impute; no_outcome_retry",
            "channel_policy": "torchaudio output is one-channel; no channel expansion",
            "normalization_policy": "no loudness normalization; preserve official decoder scale and clip only at contract boundary",
            "output_sample_rate_policy": "official codec_audio_sr=16000",
            "scientific_effect": "neural codec-token infilling/editing of the frozen target span conditioned on surrounding speech and transcript",
            "parameters": {"model_name": "giga830M", "top_k": 0, "top_p": 0.8, "temperature": 1.0, "stop_repetition": -1, "sample_batch_size": 3, "kvcache": 0, "silence_tokens": [1388, 1898, 131], "codec_audio_sr": 16000, "codec_sr": 50, "mfa_beam": 50, "mfa_retry_beam": 200, "margin_sec": 0.04, "cutoff_tolerance_sec": 1.0},
            "official_provenance": [
                "https://github.com/jasonppy/VoiceCraft/tree/f0a7a971363905883a21c466a3aa4ea2d4c0b690",
                "https://raw.githubusercontent.com/jasonppy/VoiceCraft/f0a7a971363905883a21c466a3aa4ea2d4c0b690/README.md",
                "https://raw.githubusercontent.com/jasonppy/VoiceCraft/f0a7a971363905883a21c466a3aa4ea2d4c0b690/tts_demo.py",
                "https://arxiv.org/abs/2403.16973",
            ],
        },
    }
    families["same_speaker_splice_crossfade_control"] = {
        "recommended_candidate": "A",
        "alternatives": [],
        "candidate": project_control(
            "same_speaker_splice_crossfade",
            "same-speaker waveform substitution using a deterministic context window and 400-sample boundary crossfades",
            "reference is the nearest complete non-target context window from the same case, preferring the immediately preceding window and then the immediately following window",
            "target span is the frozen GT interval [start_sample, end_sample) at 16000 Hz; no per-case manual selection",
            {"crossfade_samples": 400, "reference_preference": ["left", "right"], "interpolation": "linear", "boundary_fallback": "terminal failure if no complete same-case window exists"},
        ),
    }
    families["voice_conditioned_tts_vc_replacement"] = {
        "recommended_candidate": "A",
        "alternatives": [],
        "candidate": {
            "candidate": "A",
            "implementation_name": "YourTTS official zero-shot TTS/voice-conversion implementation",
            "implementation": "Edresson/YourTTS with official Coqui TTS released model",
            "repository": "https://github.com/Edresson/YourTTS",
            "version": "YourTTS commit 23904e6b7158d42cacf2a94dba0791ef69f1e2a9; Coqui TTS tag v0.7.0 commit c7cca4135db0c108a30ba8fd6a437fb63a5ecc12",
            "source_revision": "23904e6b7158d42cacf2a94dba0791ef69f1e2a9; c7cca4135db0c108a30ba8fd6a437fb63a5ecc12",
            "source_file": "YourTTS README; Coqui TTS CLI tts",
            "entrypoint": "tts CLI with model_name tts_models/multilingual/multi-dataset/your_tts",
            "dependency_backend_version": "Coqui TTS v0.7.0 official release path",
            "model_checkpoint": "official Coqui released YourTTS model package v0.5.0_models",
            "model_source": "https://github.com/Edresson/YourTTS/releases/download/MOS/Audios_MOS.zip and the README-linked Coqui model release package",
            "parameter_set_id": "YOURTTS_CANONICAL_V1",
            "reference_rule": "Use the next lexicographically ordered case in the same distribution with a different source_id as the target-speaker reference; use the current case waveform as content/reference_wav.",
            "target_span_rule": "Generate the frozen case target transcript with the target speaker reference, resample generated audio to the frozen target duration, then replace exactly [gt.start_sec, gt.end_sec) at 16000 Hz.",
            "sample_rate": 16000,
            "codec_path": "NOT_APPLICABLE",
            "seed_policy": "SHA256(protocol_id||distribution_id||case_id||mechanism_family||W7_MECHANISM_SEED_V1)[:64bits], converted to unsigned 64-bit and applied to Python/NumPy/PyTorch before CLI invocation",
            "quality_gate_policy": "finite waveform; mono; valid target duration; output 16000 Hz; no corruption; structural contract checks",
            "failure_policy": "terminal_generation_or_quality_failure; no_drop; no_impute; no_outcome_retry",
            "channel_policy": "downmix reference and generated audio to mono before target-span insertion",
            "normalization_policy": "no loudness normalization; preserve official model waveform scale and clip only at adapter boundary",
            "output_sample_rate_policy": "official model output is resampled to 16000 Hz with scipy.signal.resample_poly(up=320, down=441), SciPy 1.11.4",
            "scientific_effect": "voice-conditioned waveform generation replacing the frozen target span while conditioning on a distinct deterministic speaker reference",
            "parameters": {"model_name": "tts_models/multilingual/multi-dataset/your_tts", "speaker_wav_role": "target speaker reference", "reference_wav_role": "current case content reference", "language_idx": "en", "native_model_rate": 22050, "resample_up": 320, "resample_down": 441},
            "official_provenance": [
                "https://github.com/Edresson/YourTTS/tree/23904e6b7158d42cacf2a94dba0791ef69f1e2a9",
                "https://raw.githubusercontent.com/Edresson/YourTTS/23904e6b7158d42cacf2a94dba0791ef69f1e2a9/README.md",
                "https://arxiv.org/abs/2112.02418",
                "https://github.com/coqui-ai/TTS/tree/v0.7.0",
            ],
        },
    }
    if set(families) != set(FAMILY_IDS):
        raise ValueError("candidate family registry does not match frozen family registry")
    for family in FAMILY_IDS:
        candidate = families[family]["candidate"]
        candidate["bundle_hash"] = sha(candidate)
    payload: dict[str, object] = {
        "schema_version": "topconf.w7.p4.proposed_freeze_package_a.v1",
        "status": "PROPOSED_NOT_HUMAN_APPROVED",
        "recommendation_basis": "CANONICALITY_AND_REPRODUCIBILITY_ONLY",
        "families": {family: families[family] for family in FAMILY_IDS},
        "shared_policies": {"sample_rate": 16000, "seed_policy": "existing W7 frozen seed policy", "quality_gate": "existing W7 structural quality policy", "failure_policy": "existing W7 terminal failure policy"},
        "raw_p4_fields": 35,
        "fields_covered_by_each_family": 7,
        "total_covered_fields": 35,
        "unaccounted_fields": 0,
        "implementation_bindings_complete": True,
        "mechanism_case_map_sha256": MAP_SHA,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "outcome_guided_selection": False,
        "real_w7_cases_used": 0,
        "candidate_execution_authorization": "NO",
    }
    payload["proposed_package_sha256"] = sha(payload)
    return payload


def main() -> None:
    payload = build()
    package = ROOT / "W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1.json"
    package.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    rows = []
    for index, family in enumerate(FAMILY_IDS, 1):
        candidate = payload["families"][family]["candidate"]
        rows.append(f"| M{index} | `{family}` | A | `{candidate['implementation_name']}` | `{candidate['parameter_set_id']}` | {candidate['source_revision']} | APPROVE_A / REJECT_AND_STOP |")
    table = "# W7 P4 final human decision table v1\n\n| Decision | Family | Candidate | Implementation | Key scientific parameters | Provenance | Human choice |\n|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\nAll five rows are complete Candidate A bundles. Human choice is intentionally blank beyond the allowed action vocabulary; Codex has not approved any candidate.\n"
    (ROOT / "W7_P4_FINAL_HUMAN_DECISION_TABLE_V1.md").write_text(table, encoding="utf-8")
    packet = [
        "# W7 P4 final human approval packet v1",
        "",
        "Status: `PROPOSED_NOT_HUMAN_APPROVED`. This packet is pre-inference and outcome-blind. It does not authorize W7.",
        "",
        f"Proposed package SHA256: `{payload['proposed_package_sha256']}`",
        f"Existing deterministic case-map SHA256: `{MAP_SHA}`",
        "",
        "Each family has exactly one recommended Candidate A. Recommendation basis is canonicality, reproducibility, source fidelity, and minimal discretionary choice only. No metric, detector, localizer, gap expectation, or Level-2 outcome was used.",
        "",
    ]
    for index, family in enumerate(FAMILY_IDS, 1):
        c = payload["families"][family]["candidate"]
        packet.extend([f"## M{index} — {family}", f"- Candidate: A", f"- Implementation: `{c['implementation_name']}`", f"- Parameter set: `{c['parameter_set_id']}`", f"- Bundle hash: `{c['bundle_hash']}`", f"- Scientific effect: {c['scientific_effect']}", f"- Human choice: `APPROVE_A` or `REJECT_AND_STOP`", ""])
    packet.extend([
        "Implementation bindings are complete for all five proposed bundles. No final executable configuration is emitted; after human approval, the bundle must be materialized into the execution config and independently revalidated.",
        "",
        "W7_SCIENTIFIC_INFERENCES = 0",
        "LEVEL2_OUTCOMES_ACCESSED = NO",
        "OUTCOME_GUIDED_SELECTION = NO",
        "",
        "Codex approval text is intentionally not included as an executed action. Human approval remains required.",
    ])
    (ROOT / "W7_P4_FINAL_HUMAN_APPROVAL_PACKET_V1.md").write_text("\n".join(packet) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "package_sha256": payload["proposed_package_sha256"], "families": len(FAMILY_IDS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
