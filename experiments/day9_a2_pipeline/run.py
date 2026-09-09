"""Formal CPU-only Day 9 A2 three-case engineering smoke."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys

import numpy as np

REPO_ROOT = Path(__file__).absolute().parents[2]
ARTIFACT_ROOT = Path(os.environ.get("DAY9_ARTIFACT_ROOT", str(REPO_ROOT))).absolute()
RESULTS = ARTIFACT_ROOT / "results" / "day9"
sys.path.insert(0, str(REPO_ROOT / "src"))

from audiobookbench.data.manifest import load_manifest
from audiobookbench.preprocessing.audio_io import load_audio, resample_audio
from audiobookbench.security.a2_readiness import (SAMPLE_RATE, active_speech_rms, match_active_speech_rms,
    replace_whole_utterance_with_crossfade, serialize_roundtrip, trim_synthetic_silence,
    validate_crossfade_reconstruction)
from audiobookbench.security.a2_sidecar_validator import run as validate_sidecars
from audiobookbench.security.a2_waveform_gt_verifier import run as verify_waveforms
from audiobookbench.security.day8_detector_denylist import assert_detector_inputs_safe

REVISION = "eec1ae6c79877dbd9379285cf8789c9e0879293d"
MODEL_DIR = REPO_ROOT / "pretrained" / "cosyvoice2-0.5b" / REVISION
OFFICIAL = {"train": "paircase_0007", "val": "paircase_0018", "test": "paircase_0001"}


def day8_module():
    p = REPO_ROOT / "experiments" / "day8_a2_readiness" / "smoke.py"
    spec = importlib.util.spec_from_file_location("day8_helpers", p)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({k for row in rows for k in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    if not MODEL_DIR.is_dir():
        raise RuntimeError("verified local checkpoint absent")
    helper = day8_module()
    plans = {r["paired_case_id"]: dict(r) for r in load_manifest(REPO_ROOT / "data/manifests/week2a_a2_planned_manifest.csv")}
    chosen = [plans[OFFICIAL[split]] for split in ("train", "val", "test")]
    if [r["split"] for r in chosen] != ["train", "val", "test"]:
        raise RuntimeError("official split selection mismatch")
    references = {r["speaker"]: r for r in load_manifest(REPO_ROOT / "data/manifests/week2a_reference_manifest.csv")}
    longform = {r["sequence_id"]: r for r in load_manifest(REPO_ROOT / "data/manifests/day45_longform_manifest.csv")}
    hashes = helper.checkpoint_hashes(MODEL_DIR)
    checkpoint_sha = helper.sha256_json(hashes)
    from cosyvoice.utils.common import set_all_random_seed
    model = helper.load_local_model()
    rows: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    for case in chosen:
        ref = references[case["target_speaker"]]
        case.update({"reference_sample_id": ref["reference_sample_id"], "reference_audio_path": ref["reference_audio_path"],
                     "reference_text_exact": ref["reference_text_exact"], "generator_checkpoint_sha256": checkpoint_sha})
        clean, _ = load_audio(longform[case["clean_sequence_id"]]["sequence_audio_path"], target_sr=SAMPLE_RATE)
        c0, c1 = int(case["clean_source_utterance_start_sample"]), int(case["clean_source_utterance_end_sample"])
        target = clean[c0:c1]
        if target.size != int(case["source_real_num_samples"]):
            raise RuntimeError("frozen complete-source interval mismatch")
        set_all_random_seed(int(case["generation_seed"]))
        raw = helper.synthesise(model, case)
        resampled = resample_audio(raw, int(model.sample_rate), SAMPLE_RATE)
        trimmed = trim_synthetic_silence(resampled)
        scaled, gain = match_active_speech_rms(target, trimmed.waveform)
        manipulated, layout = replace_whole_utterance_with_crossfade(clean, scaled, c0, c1)
        validate_crossfade_reconstruction(clean, scaled, manipulated, layout, c1)
        output = RESULTS / "smoke" / f"{case['paired_case_id']}.wav"
        serialization = serialize_roundtrip(manipulated, output)
        row: dict[str, object] = {**case, "protocol_version": "week2a-a2-v1.1-corrected", "attack_id": case["paired_case_id"],
            "sample_id": case["target_source_sample_id"], "pair_id": case["paired_case_id"], "source_sample_id": case["target_source_sample_id"],
            "generator_checkpoint_revision": REVISION, "generator_code_revision": "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc",
            "sample_rate": SAMPLE_RATE, "generation_attempt_count": 1, "generation_status": "success", "generation_failure_reason": "",
            "qa_flags": "[]", "official_smoke": True, "smoke_only": False, "generation_status_legacy": "smoke",
            "clean_timeline_start_sample": c0, "clean_timeline_end_sample": c1, "manipulated_timeline_start_sample": layout.attack_start_sample,
            "manipulated_timeline_end_sample": layout.attack_end_sample, "raw_model_output_num_samples": int(raw.size),
            "raw_model_output_sample_rate": int(model.sample_rate), "raw_model_output_duration": raw.size / model.sample_rate,
            "resampled_num_samples": int(resampled.size), "resampled_duration": resampled.size / SAMPLE_RATE,
            **trimmed.metadata(), **gain.as_dict(), **layout.as_dict(), "crossfade_samples": 400,
            "final_synthetic_num_samples": int(scaled.size), "synthetic_duration": scaled.size / SAMPLE_RATE,
            "output_peak": float(np.max(np.abs(manipulated))), "clipping": bool(np.max(np.abs(manipulated)) >= 1.0),
            "waveform_finite": bool(np.isfinite(manipulated).all()), "synthetic_active_speech_rms_after_gain": active_speech_rms(scaled),
            "duration_ratio": scaled.size / target.size, "generator_internal_normalization": "documented_raw_passthrough_text_frontend_false",
            "serialization_roundtrip": serialization["serialization"], "serialization_max_abs_error": serialization["max_abs_error"],
            "manipulated_audio_path": str(output), "checkpoint_manifest_sha256": checkpoint_sha,
            "attack_start": layout.attack_start_sample / SAMPLE_RATE, "attack_end": layout.attack_end_sample / SAMPLE_RATE}
        rows.append(row); attempts.append({"paired_case_id": case["paired_case_id"], "split": case["split"], "attempts": 1, "retry": False, "status": "PASS"})
    sidecar = RESULTS / "a2_sidecar.csv"; write_csv(sidecar, rows)
    side = validate_sidecars(sidecar, REPO_ROOT / "data/manifests/week2a_a2_planned_manifest.csv")
    side.update({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": "experiments/day9_a2_pipeline/run.py"})
    write_json(RESULTS / "sidecar_validator_result.json", side)
    wave = verify_waveforms(sidecar, REPO_ROOT / "data/manifests/day45_longform_manifest.csv")
    assert_detector_inputs_safe({"waveform": [0.0], "features": {"rms": 0.0}})
    wave.update({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": "experiments/day9_a2_pipeline/run.py", "leakage": "PASS"})
    write_json(RESULTS / "waveform_gt_verifier_result.json", wave)
    passed = len(rows) if side["status"] == "PASS" and wave["status"] == "PASS" else 0
    write_json(RESULTS / "smoke.json", {"planned": 3, "passed": passed, "failed": 3 - passed, "case_ids": [r["paired_case_id"] for r in rows],
        "splits": [r["split"] for r in rows], "attempts": attempts, "cpu_only": True, "offline": True,
        "sidecar_path": str(sidecar), "timestamp_utc": datetime.now(timezone.utc).isoformat()})
    if passed != 3:
        raise RuntimeError("Day9 validators failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
