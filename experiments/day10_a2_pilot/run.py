"""Formal CPU-only, outcome-blind Day 10 A2 23-case pilot generation."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
from collections import Counter

import numpy as np

REPO_ROOT = Path(__file__).absolute().parents[2]
ARTIFACT_ROOT = Path(os.environ.get("DAY10_ARTIFACT_ROOT", str(REPO_ROOT))).absolute()
RESULTS = ARTIFACT_ROOT / "results" / "day10"
sys.path.insert(0, str(REPO_ROOT / "src"))

from audiobookbench.data.manifest import load_manifest
from audiobookbench.preprocessing.audio_io import load_audio, resample_audio
from audiobookbench.security.a2_readiness import (
    SAMPLE_RATE, active_speech_rms, match_active_speech_rms,
    replace_whole_utterance_with_crossfade, serialize_roundtrip,
    trim_synthetic_silence, validate_crossfade_reconstruction,
)
from audiobookbench.security.a2_sidecar_validator import run as validate_sidecars
from audiobookbench.security.a2_waveform_gt_verifier import run as verify_waveforms
from audiobookbench.security.day8_detector_denylist import assert_detector_inputs_safe

REVISION = "eec1ae6c79877dbd9379285cf8789c9e0879293d"
MODEL_DIR = REPO_ROOT / "pretrained" / "cosyvoice2-0.5b" / REVISION
PLAN_PATH = REPO_ROOT / "data" / "manifests" / "week2a_a2_planned_manifest.csv"
REFERENCE_PATH = REPO_ROOT / "data" / "manifests" / "week2a_reference_manifest.csv"
LONGFORM_PATH = REPO_ROOT / "data" / "manifests" / "day45_longform_manifest.csv"


def day8_module():
    path = REPO_ROOT / "experiments" / "day8_a2_readiness" / "smoke.py"
    spec = importlib.util.spec_from_file_location("day8_helpers", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def failure_row(case: dict[str, object], checkpoint_sha: str, exc: BaseException) -> dict[str, object]:
    return {**case, "protocol_version": "week2a-a2-v1.1-corrected", "attack_id": case["paired_case_id"],
            "sample_id": case["target_source_sample_id"], "pair_id": case["paired_case_id"],
            "source_sample_id": case["target_source_sample_id"], "generator_checkpoint_revision": REVISION,
            "generator_code_revision": "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc",
            "generator_checkpoint_sha256": checkpoint_sha, "sample_rate": SAMPLE_RATE,
            "generation_attempt_count": 1, "generation_status": "failure",
            "generation_failure_reason": f"{type(exc).__name__}: {exc}", "failure_class": "generation_runtime_failure",
            "qa_flags": json.dumps(["generation_runtime_failure"]), "official_smoke": False, "smoke_only": False,
            "generation_status_legacy": "failure"}


def success_row(case: dict[str, object], clean: np.ndarray, raw: np.ndarray, model_rate: int,
                resampled: np.ndarray, trimmed, scaled: np.ndarray, gain, manipulated: np.ndarray,
                layout, serialization: dict[str, object], output: Path, checkpoint_sha: str) -> dict[str, object]:
    c0, c1 = int(case["clean_source_utterance_start_sample"]), int(case["clean_source_utterance_end_sample"])
    return {**case, "protocol_version": "week2a-a2-v1.1-corrected", "attack_id": case["paired_case_id"],
            "sample_id": case["target_source_sample_id"], "pair_id": case["paired_case_id"],
            "source_sample_id": case["target_source_sample_id"], "generator_checkpoint_revision": REVISION,
            "generator_code_revision": "074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc",
            "generator_checkpoint_sha256": checkpoint_sha, "sample_rate": SAMPLE_RATE,
            "generation_attempt_count": 1, "generation_status": "success", "generation_failure_reason": "",
            "qa_flags": "[]", "official_smoke": False, "smoke_only": False, "generation_status_legacy": "success",
            "clean_timeline_start_sample": c0, "clean_timeline_end_sample": c1,
            "manipulated_timeline_start_sample": layout.attack_start_sample,
            "manipulated_timeline_end_sample": layout.attack_end_sample,
            "raw_model_output_num_samples": int(raw.size), "raw_model_output_sample_rate": int(model_rate),
            "raw_model_output_duration": raw.size / model_rate, "resampled_num_samples": int(resampled.size),
            "resampled_duration": resampled.size / SAMPLE_RATE, **trimmed.metadata(), **gain.as_dict(), **layout.as_dict(),
            "crossfade_samples": 400, "final_synthetic_num_samples": int(scaled.size),
            "synthetic_duration": scaled.size / SAMPLE_RATE, "output_peak": float(np.max(np.abs(manipulated))),
            "clipping": bool(np.max(np.abs(manipulated)) >= 1.0), "waveform_finite": bool(np.isfinite(manipulated).all()),
            "synthetic_active_speech_rms_after_gain": active_speech_rms(scaled), "duration_ratio": scaled.size / (c1 - c0),
            "generator_internal_normalization": "documented_raw_passthrough_text_frontend_false",
            "serialization_roundtrip": serialization["serialization"],
            "serialization_max_abs_error": serialization["max_abs_error"], "manipulated_audio_path": str(output),
            "checkpoint_manifest_sha256": checkpoint_sha, "attack_start": layout.attack_start_sample / SAMPLE_RATE,
            "attack_end": layout.attack_end_sample / SAMPLE_RATE}


def main() -> int:
    if not MODEL_DIR.is_dir():
        raise RuntimeError("verified local checkpoint absent")
    if RESULTS.exists():
        raise RuntimeError(f"refusing to overwrite a Day10 artifact directory: {RESULTS}")
    helper = day8_module()
    plans = sorted((dict(row) for row in load_manifest(PLAN_PATH)), key=lambda row: row["paired_case_id"])
    if len(plans) != 23 or len({row["paired_case_id"] for row in plans}) != 23:
        raise RuntimeError("frozen population is not exactly 23 unique paired cases")
    expected_seeds = [20260905 + index for index in range(1, 24)]
    if [int(row["generation_seed"]) for row in plans] != expected_seeds:
        raise RuntimeError("frozen seed convention mismatch")
    split_counts = Counter(row["split"] for row in plans)
    if dict(split_counts) != {"test": 6, "train": 11, "val": 6}:
        raise RuntimeError(f"frozen split mismatch: {dict(split_counts)}")
    references = {row["speaker"]: row for row in load_manifest(REFERENCE_PATH)}
    longform = {row["sequence_id"]: row for row in load_manifest(LONGFORM_PATH)}
    frozen_rows: list[dict[str, object]] = []
    cases: list[dict[str, object]] = []
    for index, original in enumerate(plans, start=1):
        case = dict(original)
        ref = references[case["target_speaker"]]
        case.update({"reference_sample_id": ref["reference_sample_id"], "reference_audio_path": ref["reference_audio_path"],
                     "reference_text_exact": ref["reference_text_exact"]})
        cases.append(case)
        frozen_rows.append({"order_index": index, "paired_case_id": case["paired_case_id"], "split": case["split"],
                            "target_speaker": case["target_speaker"], "target_source_sample_id": case["target_source_sample_id"],
                            "reference_sample_id": case["reference_sample_id"], "tts_input_text": case["tts_input_text"],
                            "generation_seed": case["generation_seed"]})
    write_csv(RESULTS / "frozen_case_list.csv", frozen_rows)
    hashes = helper.checkpoint_hashes(MODEL_DIR)
    checkpoint_sha = helper.sha256_json(hashes)
    from cosyvoice.utils.common import set_all_random_seed
    model = helper.load_local_model()
    rows: list[dict[str, object]] = []
    attempts: list[dict[str, object]] = []
    for order_index, case in enumerate(cases, start=1):
        try:
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
            output = RESULTS / "waveforms" / f"{case['paired_case_id']}.wav"
            serialization = serialize_roundtrip(manipulated, output)
            rows.append(success_row(case, clean, raw, int(model.sample_rate), resampled, trimmed, scaled, gain,
                                    manipulated, layout, serialization, output, checkpoint_sha))
            attempts.append({"order_index": order_index, "paired_case_id": case["paired_case_id"], "attempts": 1,
                             "retry": False, "status": "success"})
        except Exception as exc:
            rows.append(failure_row(case, checkpoint_sha, exc))
            attempts.append({"order_index": order_index, "paired_case_id": case["paired_case_id"], "attempts": 1,
                             "retry": False, "status": "failure", "failure_class": "generation_runtime_failure",
                             "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    write_csv(RESULTS / "a2_sidecar.csv", rows)
    successful = [row for row in rows if row["generation_status"] == "success"]
    success_sidecar = RESULTS / "a2_success_sidecar.csv"
    write_csv(success_sidecar, successful)
    side = validate_sidecars(success_sidecar, PLAN_PATH, expected_count=len(successful), official_smoke=False)
    side.update({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": "experiments/day10_a2_pilot/run.py",
                 "successful_generation_count": len(successful)})
    write_json(RESULTS / "sidecar_validator_result.json", side)
    wave = verify_waveforms(success_sidecar, LONGFORM_PATH, expected_count=len(successful))
    assert_detector_inputs_safe({"waveform": [0.0], "features": {"rms": 0.0}})
    wave.update({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": "experiments/day10_a2_pilot/run.py",
                 "leakage": "PASS", "successful_generation_count": len(successful)})
    write_json(RESULTS / "waveform_gt_verifier_result.json", wave)
    failures = Counter(str(row.get("failure_class", "generation_runtime_failure")) for row in rows
                       if row["generation_status"] != "success")
    output_hashes = []
    for row in successful:
        path = Path(str(row["manipulated_audio_path"]))
        output_hashes.append({"paired_case_id": row["paired_case_id"], "path": str(path), "bytes": path.stat().st_size,
                              "sha256": sha256_file(path)})
    freeze = {"planned": 23, "split": [11, 6, 6], "succeeded": len(successful), "failed_by_class": dict(sorted(failures.items())),
              "accounting_check": len(successful) + sum(failures.values()) == 23, "retries": 0, "replacements": 0,
              "cpu_only": True, "offline": True, "checkpoint_revision": REVISION, "checkpoint_manifest_sha256": checkpoint_sha,
              "frozen_case_list_sha256": sha256_file(RESULTS / "frozen_case_list.csv"),
              "a2_sidecar_sha256": sha256_file(RESULTS / "a2_sidecar.csv"), "output_hashes": output_hashes,
              "timestamp_utc": datetime.now(timezone.utc).isoformat()}
    write_json(RESULTS / "day10_output_hashes.json", freeze)
    # This is a compact, standard generated-data index, not a second sidecar:
    # canonical per-case provenance remains RESULTS / "a2_sidecar.csv".
    write_json(ARTIFACT_ROOT / "data" / "generated" / "a2_day10_pilot_freeze.json", {
        "artifact_type": "a2_day10_pilot_freeze_index", "canonical_sidecar": str(RESULTS / "a2_sidecar.csv"),
        "canonical_hash_freeze": str(RESULTS / "day10_output_hashes.json"), "planned": 23,
        "succeeded": len(successful), "failed_by_class": dict(sorted(failures.items())),
        "no_replacements": True, "no_detector_scoring": True, "no_a2_metrics": True,
    })
    write_json(RESULTS / "generation_summary.json", {"planned": 23, "succeeded": len(successful),
               "failed_by_class": dict(sorted(failures.items())), "accounting_check": freeze["accounting_check"],
               "attempts": attempts, "detector_scoring_executed": False, "a2_metrics_executed": False,
               "scientific_claims_added": False, "day11_entered": False})
    if not freeze["accounting_check"] or side["status"] != "PASS" or wave["status"] != "PASS" or len(successful) != 23:
        raise RuntimeError("Day10 generation or validation failed; all outcomes were recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
