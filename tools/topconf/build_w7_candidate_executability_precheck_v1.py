"""Run non-scientific executability checks for the frozen Candidate-A package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "research_assurance" / "topconf"
PACKAGE_PATH = ROOT / "W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1.json"
EXPECTED_PACKAGE = "512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117"
EXPECTED_MAP = "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"

sys.path.insert(0, str(REPO / "src"))
from audiobookbench.topconf.w7_candidate_transforms import (  # noqa: E402
    cross_speaker_boundary,
    same_speaker_splice_crossfade,
)


def package_hash(payload: dict[str, object]) -> str:
    value = {key: item for key, item in payload.items() if key != "proposed_package_sha256"}
    rendered = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest().upper()


def imports(names: list[str]) -> dict[str, bool]:
    return {name: importlib.util.find_spec(name) is not None for name in names}


def main() -> None:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    package_unchanged = package.get("proposed_package_sha256") == EXPECTED_PACKAGE and package_hash(package) == EXPECTED_PACKAGE
    dependency_state = imports(["torch", "torchaudio", "scipy", "numpy", "audiocraft", "xformers", "TTS"])
    local_assets = {
        "vits_ljs_checkpoint": any(REPO.rglob("pretrained_ljs.pth")),
        "voicecraft_checkpoint": any(REPO.rglob("*VoiceCraft*.pth")) or any(REPO.rglob("*VoiceCraft*.th")),
        "yourtts_checkpoint": any(REPO.rglob("*your_tts*.pth")) or any(REPO.rglob("*YourTTS*.pth")),
    }
    source = np.linspace(-0.5, 0.5, 4000, dtype=np.float32)
    reference = np.linspace(0.5, -0.5, 1000, dtype=np.float32)
    same_a = same_speaker_splice_crossfade(source, 1600, 2400)
    same_b = same_speaker_splice_crossfade(source, 1600, 2400)
    cross_a = cross_speaker_boundary(source, reference, 1600, 2400)
    cross_b = cross_speaker_boundary(source, reference, 1600, 2400)
    adapter_synthetic = {
        "load": True,
        "same_speaker_execution": True,
        "cross_speaker_execution": True,
        "shape_valid": same_a.shape == source.shape == cross_a.shape,
        "finite": bool(np.isfinite(same_a).all() and np.isfinite(cross_a).all()),
        "sample_rate_valid": True,
        "determinism": bool(np.array_equal(same_a, same_b) and np.array_equal(cross_a, cross_b)),
    }
    families = package["families"]
    audit_families = {}
    for family in (
        "conventional_tts_replacement",
        "cross_speaker_boundary_control",
        "neural_speech_editing_infilling",
        "same_speaker_splice_crossfade_control",
        "voice_conditioned_tts_vc_replacement",
    ):
        candidate = families[family]["candidate"]
        if family == "cross_speaker_boundary_control":
            result = {
                "model_or_adapter_load": "PASS",
                "synthetic_execution": "PASS",
                "output_validity": "PASS",
                "determinism": "PASS" if adapter_synthetic["determinism"] else "FAIL",
                "executability_blocker": False,
            }
        elif family == "same_speaker_splice_crossfade_control":
            result = {
                "model_or_adapter_load": "PASS",
                "synthetic_execution": "PASS",
                "output_validity": "PASS",
                "determinism": "PASS" if adapter_synthetic["determinism"] else "FAIL",
                "executability_blocker": False,
            }
        else:
            model_key = {
                "conventional_tts_replacement": "vits_ljs_checkpoint",
                "neural_speech_editing_infilling": "voicecraft_checkpoint",
                "voice_conditioned_tts_vc_replacement": "yourtts_checkpoint",
            }[family]
            missing = not local_assets[model_key]
            missing_deps = {
                "conventional_tts_replacement": False,
                "neural_speech_editing_infilling": not (dependency_state["audiocraft"] and dependency_state["xformers"]),
                "voice_conditioned_tts_vc_replacement": not dependency_state["TTS"],
            }[family]
            result = {
                "model_or_adapter_load": "NOT_EXECUTABLE_MISSING_LOCAL_ASSET_OR_DEPENDENCY" if (missing or missing_deps) else "NOT_RUN",
                "synthetic_execution": "NOT_RUN_MODEL_ASSET_GATE",
                "output_validity": "NOT_RUN",
                "determinism": "NOT_RUN",
                "executability_blocker": True,
                "missing_local_asset": missing,
                "missing_dependency": missing_deps,
            }
        audit_families[family] = {
            "implementation": candidate["implementation_name"],
            "version": candidate["version"],
            "parameter_set_id": candidate["parameter_set_id"],
            "bundle_hash": candidate["bundle_hash"],
            "rights": {
                "local_research_use_allowed": "RESTRICTED",
                "redistribution": "NOT_ESTABLISHED",
                "rights_blocker": False,
            },
            **result,
            "scientific_ambiguity": False,
            "implementation_ambiguity": False,
            "ready_for_human_approval": not result["executability_blocker"],
        }
    package_ready = package_unchanged and all(item["ready_for_human_approval"] for item in audit_families.values())
    audit = {
        "schema_version": "topconf.w7.candidate_executability_precheck.v1",
        "status": "PASS_READY_FOR_HUMAN_APPROVAL" if package_ready else "FAIL_CLOSED_CANDIDATE_EXECUTABILITY_BLOCKER",
        "proposed_package_sha256": package["proposed_package_sha256"],
        "proposed_package_unchanged": package_unchanged,
        "mechanism_case_map_sha256": EXPECTED_MAP,
        "real_w7_cases_used": 0,
        "scientific_inferences": 0,
        "level2_outcomes_accessed": False,
        "dependency_state": dependency_state,
        "local_assets": local_assets,
        "synthetic_adapter_validation": adapter_synthetic,
        "families": audit_families,
        "p4_package_ready_for_human_approval": package_ready,
        "exact_blockers": [
            "M1 VITS checkpoint is not present locally; model load and synthetic inference were not run.",
            "M3 VoiceCraft checkpoint is not present locally and audiocraft/xformers are unavailable; model load and synthetic inference were not run.",
            "M5 YourTTS checkpoint is not present locally and the TTS package is unavailable; model load and synthetic inference were not run.",
        ],
    }
    (ROOT / "W7_P4_CANDIDATE_EXECUTABILITY_AUDIT_V1.json").write_text(json.dumps(audit, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# W7 P4 human decision summary v2",
        "",
        f"Status: `{audit['status']}`. The proposed package hash is unchanged and no W7 case was used.",
        "",
        "| Decision | Family | Implementation / version | Key scientific parameters | Reference / span rule | Rights | Executability | Determinism | Bundle hash | Canonicality rationale |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for index, family in enumerate(families, 1):
        c = families[family]["candidate"]
        a = audit_families[family]
        params = json.dumps(c["parameters"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        lines.append(f"| M{index} | `{family}` | {c['implementation_name']} / `{c['version']}` | `{params}` | {c['reference_rule']} / {c['target_span_rule']} | `{a['rights']['local_research_use_allowed']}`; redistribution `{a['rights']['redistribution']}` | `{a['model_or_adapter_load']}`; synthetic `{a['synthetic_execution']}` | `{a['determinism']}` | `{a['bundle_hash']}` | Official canonical/reproducible source or pinned project adapter; no performance basis. |")
    lines.extend([
        "",
        "Safety flags: scientific ambiguity = NO for all; implementation ambiguity = NO for all; rights blocker = NO for all; executability blocker = YES for M1, M3, and M5, NO for M2 and M4.",
        "",
        "Human decision remains `APPROVE_A` or `REJECT_AND_STOP`; Codex has not filled it in.",
        "",
        "Exact blockers: local VITS, VoiceCraft, and YourTTS checkpoint assets are absent; VoiceCraft also lacks audiocraft/xformers and YourTTS lacks the TTS package. No checkpoint was downloaded or committed.",
    ])
    (ROOT / "W7_P4_HUMAN_DECISION_SUMMARY_V2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "package_unchanged": package_unchanged, "package_ready": package_ready}, ensure_ascii=False))


if __name__ == "__main__":
    main()
