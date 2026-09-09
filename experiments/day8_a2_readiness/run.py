"""Materialize and validate Day 8 A2 readiness artifacts without TTS inference."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from audiobookbench.data.manifest import load_manifest
from audiobookbench.security.a2_readiness import (
    A2ReadinessError,
    CROSSFADE_SAMPLES,
    SAMPLE_RATE,
    active_speech_rms,
    choose_reference_rows,
    materialize_whole_utterance_cases,
    match_active_speech_rms,
    replace_whole_utterance_with_crossfade,
    serialize_roundtrip,
    trim_synthetic_silence,
    validate_a2_sidecar_row,
    validate_crossfade_reconstruction,
)
from audiobookbench.security.day8_detector_denylist import DetectorLeakageError, assert_detector_inputs_safe


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def dummy_timeline_audit() -> dict[str, Any]:
    cases = [
        ("synthetic_short", 1200, 3600, 1800),
        ("synthetic_long", 2800, 5200, 3000),
        ("synthetic_equal", 4200, 6600, 2400),
        ("target_early", 900, 3300, 2000),
        ("target_late", 7600, 10000, 2600),
    ]
    checks: list[dict[str, Any]] = []
    for name, start, end, syn_len in cases:
        clean = (np.arange(12000, dtype=np.float32) / 15000.0) - 0.4
        synthetic = np.linspace(-0.2, 0.2, syn_len, dtype=np.float32)
        output, layout = replace_whole_utterance_with_crossfade(clean, synthetic, start, end)
        validate_crossfade_reconstruction(clean, synthetic, output, layout, end)
        checks.append({"name": name, "passed": True, **layout.as_dict(), "output_num_samples": int(output.size)})
    try:
        replace_whole_utterance_with_crossfade(np.zeros(2000, dtype=np.float32), np.zeros(800, dtype=np.float32), 500, 1500)
    except A2ReadinessError as exc:
        short_failure = str(exc)
    else:
        raise AssertionError("short synthetic did not fail closed")
    return {"status": "PASS", "cases": checks, "short_synthetic_failure": short_failure}


def dsp_audit(results_dir: Path) -> dict[str, Any]:
    active = np.full(3200, 0.1, dtype=np.float32)
    wave = np.concatenate((np.zeros(1600, dtype=np.float32), active, np.zeros(1600, dtype=np.float32)))
    trimmed = trim_synthetic_silence(wave)
    # The frozen margin is measured from the first/last *active frame*, not a
    # hidden sample-level onset detector.  Overlapping 25 ms / 10 ms frames
    # make this synthetic fixture's expected deterministic bounds 480 and 560.
    if trimmed.leading_trim_samples != 480 or trimmed.trailing_trim_samples != 560:
        raise AssertionError("deterministic 50 ms frame-margin behavior changed")
    target = np.full(3200, 0.1, dtype=np.float32)
    synthetic = np.full(3200, 0.01, dtype=np.float32)
    scaled, gain = match_active_speech_rms(target, synthetic)
    serialization = serialize_roundtrip(scaled, results_dir / "dummy_serialization_roundtrip.wav")
    return {
        "status": "PASS",
        "silence_trim": trimmed.metadata(),
        "target_active_rms": active_speech_rms(target),
        "gain": gain.as_dict(),
        "serialization": serialization,
    }


def denylist_audit() -> dict[str, Any]:
    assert_detector_inputs_safe({"waveform": [0.0, 0.1], "features": {"rms": 0.2}})
    blocked: list[str] = []
    for key in ("reference_sample_id", "conditioning_embedding", "speaker_enrollment_vector", "attack_side_embedding"):
        try:
            assert_detector_inputs_safe({key: "forbidden"})
        except DetectorLeakageError:
            blocked.append(key)
    if len(blocked) != 4:
        raise AssertionError("detector denylist did not fail closed")
    return {"status": "PASS", "blocked_keys": blocked}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results/day8")
    args = parser.parse_args()
    results_dir = (REPO_ROOT / args.results_dir).resolve()
    source = load_manifest(REPO_ROOT / "data/manifests/day45_source_audio.csv")
    longform = load_manifest(REPO_ROOT / "data/manifests/day45_longform_manifest.csv")
    attacks = load_manifest(REPO_ROOT / "data/manifests/day45_attack_manifest.csv")
    cases = materialize_whole_utterance_cases(attacks, longform, source)
    references = choose_reference_rows(source, attacks, longform)
    reference_by_speaker = {row["speaker"]: row for row in references}
    planned: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        reference = reference_by_speaker[case["target_speaker"]]
        row = {
            **case,
            "reference_sample_id": reference["reference_sample_id"],
            "reference_audio_path": reference["reference_audio_path"],
            "reference_speaker": reference["speaker"],
            "attack_type": "same_text_tts_replacement",
            "attack_generator": "CosyVoice2-0.5B",
            "attack_generator_family": "CosyVoice",
            "generator_checkpoint_sha256": "PENDING_DAY8_BACKEND_DOWNLOAD",
            "generation_status": "planned",
            "generation_seed": 20260905 + index,
            "smoke_only": False,
        }
        validate_a2_sidecar_row(row)
        planned.append(row)
    timeline = dummy_timeline_audit()
    dsp = dsp_audit(results_dir)
    denylist = denylist_audit()
    write_csv(REPO_ROOT / "data/manifests/week2a_reference_manifest.csv", references)
    write_csv(REPO_ROOT / "data/manifests/week2a_a2_planned_manifest.csv", planned)
    write_json(results_dir / "reference_manifest_audit.json", {"status": "PASS", "count": len(references), "rows": references})
    write_json(results_dir / "text_lineage_audit.json", {"status": "PASS", "count": len(cases), "all_exact": True})
    write_json(results_dir / "manifest_validator_audit.json", {"status": "PASS", "planned_rows": len(planned)})
    write_json(results_dir / "dummy_timeline_tests.json", timeline)
    write_json(results_dir / "detector_denylist_audit.json", denylist)
    write_json(results_dir / "dsp_audit.json", dsp)
    write_json(results_dir / "precheck.json", {
        "status": "PASS", "python": sys.version, "platform": platform.platform(),
        "whole_utterance_cases": len(cases), "reference_count": len(references),
        "crossfade_samples_per_edge": CROSSFADE_SAMPLES, "sample_rate": SAMPLE_RATE,
    })
    write_json(results_dir / "run_summary.json", {
        "stage": "day8_non_tts_readiness", "status": "PASS", "formal_a2_generation": False,
        "smoke_generation": False, "planned_cases": len(planned), "references": len(references),
    })
    print(json.dumps({"status": "PASS", "planned_cases": len(planned), "references": len(references)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
