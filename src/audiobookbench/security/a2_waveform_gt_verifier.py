"""Independent serialized-waveform and sample-first GT verifier for Day 9."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from audiobookbench.preprocessing.audio_io import load_audio
from audiobookbench.security.a2_readiness import SAMPLE_RATE


def verify_row(row: dict[str, str], sequence_path: str) -> None:
    wav_path = Path(row["manipulated_audio_path"])
    info = sf.info(wav_path)
    waveform, sr = sf.read(wav_path, dtype="float32", always_2d=False)
    if sr != SAMPLE_RATE or info.channels != 1 or waveform.ndim != 1 or waveform.size == 0 or not np.all(np.isfinite(waveform)):
        raise ValueError("invalid serialized waveform")
    if np.max(np.abs(waveform)) >= 1.0 or row["clipping"] != "False":
        raise ValueError("invalid clipping")
    clean, _ = load_audio(sequence_path, target_sr=SAMPLE_RATE)
    c0, c1 = int(row["clean_source_utterance_start_sample"]), int(row["clean_source_utterance_end_sample"])
    a0, a1 = int(row["attack_start_sample"]), int(row["attack_end_sample"])
    core0, core1 = int(row["attack_core_start_sample"]), int(row["attack_core_end_sample"])
    bi0, bi1 = int(row["blend_in_start_sample"]), int(row["blend_in_end_sample"])
    bo0, bo1 = int(row["blend_out_start_sample"]), int(row["blend_out_end_sample"])
    fade, delta = int(row["crossfade_samples"]), int(row["duration_delta_samples"])
    if (a0, a1) != (c0, c0 + int(row["final_synthetic_num_samples"])) or waveform.size != clean.size + delta:
        raise ValueError("timeline length mismatch")
    if (bi0, bi1, core0, core1, bo0, bo1) != (a0, a0 + fade, a0 + fade, a1 - fade, a1 - fade, a1):
        raise ValueError("core/blend bounds mismatch")
    tol = float(row["serialization_max_abs_error"]) + 1e-7
    if np.max(np.abs(waveform[:a0] - clean[:c0])) > tol or np.max(np.abs(waveform[a1:] - clean[c1:])) > tol:
        raise ValueError("prefix/suffix mapping mismatch")


def run(sidecar_path: Path, longform_path: Path, *, expected_count: int = 3) -> dict[str, Any]:
    rows = list(csv.DictReader(sidecar_path.open(encoding="utf-8", newline="")))
    longform = {r["sequence_id"]: r for r in csv.DictReader(longform_path.open(encoding="utf-8", newline=""))}
    errors: list[dict[str, str]] = []
    for row in rows:
        try:
            verify_row(row, longform[row["clean_sequence_id"]]["sequence_audio_path"])
        except Exception as exc:
            errors.append({"paired_case_id": row.get("paired_case_id", ""), "error": str(exc)})
    return {"status": "PASS" if not errors and len(rows) == expected_count else "FAIL", "passed": len(rows) - len(errors),
            "failed": len(errors), "errors": errors, "case_ids": [r.get("paired_case_id") for r in rows],
            "tool": "a2_waveform_gt_verifier"}
