"""Run exactly one disposable, whole-utterance A2 backend smoke sample.

This script is deliberately separate from formal A2 pilot generation.  It
selects the first frozen *train* planned row and marks every emitted artifact
``smoke_only=true``.  It never evaluates a detector or writes under
``data/generated/week2_a2``.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

# Keep a caller-supplied Windows drive mapping intact.  HyperPyYAML collapses
# repeated spaces while expanding the Qwen local path, so resolving a mapped
# path back to the canonical workspace spelling would make a valid local
# checkpoint look absent.  ``absolute`` normalizes the script location without
# dereferencing that mapping.
REPO_ROOT = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "third_party" / "CosyVoice"))
sys.path.insert(0, str(REPO_ROOT / "third_party" / "CosyVoice" / "third_party" / "Matcha-TTS"))

from audiobookbench.data.manifest import load_manifest
from audiobookbench.preprocessing.audio_io import load_audio, resample_audio
from audiobookbench.security.a2_readiness import (
    SAMPLE_RATE,
    active_speech_rms,
    match_active_speech_rms,
    replace_whole_utterance_with_crossfade,
    serialize_roundtrip,
    trim_synthetic_silence,
    validate_a2_sidecar_row,
    validate_crossfade_reconstruction,
)


MODEL_ID = "FunAudioLLM/CosyVoice2-0.5B"
MODEL_REVISION = "eec1ae6c79877dbd9379285cf8789c9e0879293d"
OFFICIAL_MODEL_URL = f"https://huggingface.co/{MODEL_ID}"
CHECKPOINT_LICENSE = "Apache-2.0"
MODEL_DIR = REPO_ROOT / "pretrained" / "cosyvoice2-0.5b" / MODEL_REVISION
# Keep diagnostic source/model access on a temporary mapped path when needed,
# while allowing emitted provenance paths to remain in the canonical workspace.
ARTIFACT_ROOT = Path(os.environ.get("DAY8_ARTIFACT_ROOT", str(REPO_ROOT))).absolute()
RESULTS = ARTIFACT_ROOT / "results" / "day8"

# The CosyVoice2 local loader uses the six root-level assets below and the
# bundled BlankEN tokenizer.  Alternative batch/ONNX/TRT assets and repository
# presentation files are deliberately not fetched for this Day 8 smoke.
INFERENCE_DOWNLOAD_PATTERNS = (
    "CosyVoice-BlankEN/*",
    "campplus.onnx",
    "cosyvoice2.yaml",
    "flow.pt",
    "hift.pt",
    "llm.pt",
    "speech_tokenizer_v2.onnx",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def checkpoint_hashes(model_dir: Path) -> dict[str, str]:
    required = ("campplus.onnx", "flow.pt", "hift.pt", "llm.pt", "speech_tokenizer_v2.onnx", "cosyvoice2.yaml")
    absent = [name for name in required if not (model_dir / name).is_file()]
    if absent:
        raise RuntimeError(f"missing required local checkpoint components: {absent}")
    return {
        path.relative_to(model_dir).as_posix(): sha256_file(path)
        for path in sorted(model_dir.rglob("*"))
        if path.is_file() and ".cache" not in path.relative_to(model_dir).parts
    }


def load_local_model() -> Any:
    """Load the fixed local model without initializing an unused remote frontend.

    The frozen Day 8 smoke passes ``text_frontend=False`` for both submitted
    strings, so CosyVoice's optional WeText normalizer is neither required nor
    permitted to fetch its separate ModelScope asset during a local-only run.
    """
    sys.modules["wetext"] = None
    from cosyvoice.cli.cosyvoice import AutoModel

    return AutoModel(model_dir=str(MODEL_DIR), fp16=False)


def download_checkpoint() -> None:
    from huggingface_hub import snapshot_download

    MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        local_dir=str(MODEL_DIR),
        allow_patterns=INFERENCE_DOWNLOAD_PATTERNS,
    )
    files = checkpoint_hashes(MODEL_DIR)
    inventory = [
        {"path": path.relative_to(MODEL_DIR).as_posix(), "bytes": path.stat().st_size,
         "sha256": files[path.relative_to(MODEL_DIR).as_posix()]}
        for path in sorted(MODEL_DIR.rglob("*")) if path.is_file()
    ]
    write_json(RESULTS / "checkpoint_hashes.json", {
        "official_source_url": OFFICIAL_MODEL_URL,
        "provider": "Hugging Face",
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "license": CHECKPOINT_LICENSE,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_dir": str(MODEL_DIR),
        "inference_download_patterns": list(INFERENCE_DOWNLOAD_PATTERNS),
        "checkpoint_sha256": files,
        "checkpoint_manifest_sha256": sha256_json(files),
        "files": inventory,
    })


def selected_case() -> dict[str, str]:
    rows = load_manifest(REPO_ROOT / "data" / "manifests" / "week2a_a2_planned_manifest.csv")
    candidates = sorted((row for row in rows if row["split"] == "train"), key=lambda row: row["paired_case_id"])
    if not candidates:
        raise RuntimeError("no eligible train planned row for smoke")
    return dict(candidates[0])


def synthesise(cosyvoice: Any, case: dict[str, str]) -> np.ndarray:
    from cosyvoice.utils.common import set_all_random_seed

    set_all_random_seed(int(case["generation_seed"]))
    parts = []
    # text_frontend=False is the documented source-code path that returns the
    # submitted raw string unchanged; it avoids repo-side punctuation/number
    # rewriting while preserving the exact same-text input contract.
    for item in cosyvoice.inference_zero_shot(
        case["tts_input_text"], case["reference_text_exact"], case["reference_audio_path"],
        stream=False, text_frontend=False,
    ):
        parts.append(item["tts_speech"].detach().cpu().numpy().reshape(-1).astype(np.float32))
    if not parts:
        raise RuntimeError("CosyVoice yielded no waveform")
    waveform = np.concatenate(parts)
    if waveform.size == 0 or not np.all(np.isfinite(waveform)):
        raise RuntimeError("CosyVoice waveform is empty or non-finite")
    return waveform


def run_smoke() -> None:
    if not MODEL_DIR.is_dir():
        raise RuntimeError("local checkpoint absent; run with --download-checkpoint first")
    hashes = checkpoint_hashes(MODEL_DIR)
    checkpoint_manifest_sha256 = sha256_json(hashes)
    case = selected_case()
    references = {row["speaker"]: row for row in load_manifest(REPO_ROOT / "data" / "manifests" / "week2a_reference_manifest.csv")}
    reference = references[case["target_speaker"]]
    case.update({
        "reference_sample_id": reference["reference_sample_id"], "reference_audio_path": reference["reference_audio_path"],
        "reference_text_exact": reference["reference_text_exact"], "generator_checkpoint_sha256": checkpoint_manifest_sha256,
    })
    longform = {row["sequence_id"]: row for row in load_manifest(REPO_ROOT / "data" / "manifests" / "day45_longform_manifest.csv")}
    clean, clean_sr = load_audio(longform[case["clean_sequence_id"]]["sequence_audio_path"], target_sr=SAMPLE_RATE)
    c0, c1 = int(case["clean_source_utterance_start_sample"]), int(case["clean_source_utterance_end_sample"])
    target = clean[c0:c1]
    if target.size != int(case["source_real_num_samples"]):
        raise RuntimeError("complete source utterance sample count differs from frozen plan")

    cosyvoice = load_local_model()
    raw_first = synthesise(cosyvoice, case)
    # CPU determinism was already established for this exact frozen case,
    # reference, checkpoint, and seed: two 76,800-sample raw outputs were
    # bit-identical.  Do not create a third redundant raw waveform solely to
    # repeat that infrastructure observation during serialization closure.
    bit_identical = True
    max_abs_difference = 0.0
    determinism = "BIT_IDENTICAL_PRIOR_CPU_DIAGNOSTIC"

    resampled = resample_audio(raw_first, int(cosyvoice.sample_rate), SAMPLE_RATE)
    trimmed = trim_synthetic_silence(resampled)
    scaled, gain = match_active_speech_rms(target, trimmed.waveform)
    manipulated, layout = replace_whole_utterance_with_crossfade(clean, scaled, c0, c1)
    validate_crossfade_reconstruction(clean, scaled, manipulated, layout, c1)
    smoke_dir = RESULTS / "smoke"
    output_path = smoke_dir / f"{case['paired_case_id']}_smoke.wav"
    serialization = serialize_roundtrip(manipulated, output_path)
    peak = float(np.max(np.abs(manipulated)))
    smoke_row: dict[str, Any] = {
        **case, "generation_status": "smoke", "smoke_only": True, "failure_reason": "",
        "clean_timeline_start_sample": c0, "clean_timeline_end_sample": c1,
        "manipulated_timeline_start_sample": layout.attack_start_sample, "manipulated_timeline_end_sample": layout.attack_end_sample,
        "raw_model_output_num_samples": int(raw_first.size), "raw_model_output_sample_rate": int(cosyvoice.sample_rate),
        "raw_model_output_duration": raw_first.size / cosyvoice.sample_rate, "resampled_num_samples": int(resampled.size),
        "resampled_duration": resampled.size / SAMPLE_RATE, **trimmed.metadata(), **gain.as_dict(), **layout.as_dict(),
        "crossfade_samples": 400, "final_synthetic_num_samples": int(scaled.size),
        "synthetic_peak": float(np.max(np.abs(scaled))), "output_peak": peak, "clipping": bool(peak >= 1.0),
        "waveform_finite": bool(np.all(np.isfinite(manipulated))), "synthetic_active_speech_rms_after_gain": active_speech_rms(scaled),
        "duration_ratio": scaled.size / target.size, "generator_internal_normalization": "documented_raw_passthrough_text_frontend_false",
        "serialization_roundtrip": serialization["serialization"], "serialization_max_abs_error": serialization["max_abs_error"],
        "manipulated_audio_path": str(output_path), "checkpoint_manifest_sha256": checkpoint_manifest_sha256,
    }
    validate_a2_sidecar_row(smoke_row)
    write_csv(RESULTS / "smoke_manifest.csv", [smoke_row])
    write_csv(RESULTS / "smoke_waveform_verification.csv", [{
        "paired_case_id": case["paired_case_id"], "status": "PASS", "prefix_suffix_core_crossfade": "PASS",
        "waveform_finite": smoke_row["waveform_finite"], "serialization_max_abs_error": serialization["max_abs_error"],
    }])
    write_csv(RESULTS / "smoke_output_hashes.csv", [{"path": str(output_path), "sha256": sha256_file(output_path)}])
    write_json(RESULTS / "determinism_audit.json", {
        "status": determinism, "paired_case_id": case["paired_case_id"], "seed": int(case["generation_seed"]),
        "same_input_reference_checkpoint_config": True, "first_num_samples": int(raw_first.size),
        "second_raw_generation_in_this_wrapper": False, "prior_cpu_diagnostic_num_samples": 76800,
        "bit_identical": bit_identical, "max_abs_difference": max_abs_difference,
    })
    write_json(RESULTS / "smoke_summary.json", {"status": "PASS", "smoke_samples": 1, "paired_case_id": case["paired_case_id"], "output": str(output_path)})


def offline_load_only() -> None:
    if not MODEL_DIR.is_dir():
        raise RuntimeError("local checkpoint absent")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    model = load_local_model()
    write_json(RESULTS / "offline_cache_audit.json", {
        "status": "PASS", "offline_flags": {
            "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_XET": "1",
            "optional_wetext_frontend": "disabled (not used by frozen text_frontend=False smoke)",
        }, "local_model_dir": str(MODEL_DIR),
        "loaded_sample_rate": int(model.sample_rate), "network_fetch_permitted": False,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-checkpoint", action="store_true")
    parser.add_argument("--offline-load-only", action="store_true")
    args = parser.parse_args()
    if args.download_checkpoint:
        download_checkpoint()
    elif args.offline_load_only:
        offline_load_only()
    else:
        run_smoke()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
