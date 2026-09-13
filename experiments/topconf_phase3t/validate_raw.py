from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:  # Supports both package imports in tests and direct script execution.
    from .adapter import deterministic_supports
    from .common import (
        ALLOWED_TERMINAL_STATUSES,
        EXPECTED_CASES,
        FORBIDDEN_GT_KEYS,
        forbidden_keys,
        read_case_manifest,
        read_jsonl,
        sha256_file,
        sha256_json,
        to_jsonable,
    )
except ImportError:  # pragma: no cover - exercised by the command-line entry point
    from adapter import deterministic_supports
    from common import (
        ALLOWED_TERMINAL_STATUSES,
        EXPECTED_CASES,
        FORBIDDEN_GT_KEYS,
        forbidden_keys,
        read_case_manifest,
        read_jsonl,
        sha256_file,
        sha256_json,
        to_jsonable,
    )


def _finite_array(value: Any, shape_tail: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.size == 0 or not np.isfinite(array).all():
        raise ValueError("empty or non-finite output array")
    if shape_tail is not None and (array.ndim != 2 or array.shape[1] != shape_tail):
        raise ValueError(f"expected N x {shape_tail} output array")
    return array


def _validate_cfprf(record: dict[str, Any]) -> None:
    native = record.get("native_outputs")
    if not isinstance(native, dict):
        raise ValueError("CFPRF native output missing")
    seg = _finite_array(native.get("fdn_segment_scores"), 2)
    boundary = _finite_array(native.get("fdn_boundary_scores"), 2)
    if len(seg) != len(boundary):
        raise ValueError("CFPRF segment and boundary lengths differ")
    duration = float(record["duration_sec"])
    deterministic_supports(len(seg), 0.02, duration)
    if native.get("fdn_segment_class_order") != ["spoof", "bonafide"]:
        raise ValueError("CFPRF class order missing")
    for key in ("fdn_coarse_proposals", "prn_input_coarse_proposals", "prn_scored_coarse_proposals", "prn_verification_proposals", "prn_refined_proposals"):
        proposals = native.get(key)
        if not isinstance(proposals, list):
            raise ValueError(f"CFPRF {key} must be a list")
        for proposal in proposals:
            if len(proposal) != 3 or not np.isfinite(np.asarray(proposal, dtype=float)).all() or proposal[2] <= proposal[1] or proposal[1] < 0 or proposal[2] > duration + 1e-9:
                raise ValueError(f"CFPRF invalid proposal in {key}")
    ver = np.asarray(native.get("prn_verification_scores"), dtype=float)
    reg = np.asarray(native.get("prn_regression_outputs"), dtype=float)
    if ver.size:
        _finite_array(ver, 1)
    if reg.size:
        _finite_array(reg, 2)
    if (ver.size == 0) != (reg.size == 0):
        raise ValueError("CFPRF PRN score/regression emptiness differs")


def _validate_multireso(record: dict[str, Any]) -> None:
    native = record.get("native_outputs")
    if not isinstance(native, dict) or not isinstance(native.get("scales"), dict) or len(native["scales"]) != 6:
        raise ValueError("MultiReso must contain six scales")
    duration = float(record["duration_sec"])
    for scale_id, scale in native["scales"].items():
        scores = _finite_array(scale.get("native_class_scores"), 2)
        times = _finite_array(scale.get("native_times_sec"), 2)
        if len(scores) != len(times) or float(scale.get("unit_sec")) <= 0:
            raise ValueError(f"{scale_id}: scores/times mismatch")
        expected = deterministic_supports(len(scores), float(scale["unit_sec"]), duration)
        if not np.allclose(times, expected, rtol=0, atol=1e-12):
            raise ValueError(f"{scale_id}: non-deterministic native times")
        if scale.get("class_order") != ["spoof", "bonafide"]:
            raise ValueError(f"{scale_id}: class order missing")
    utterance = _finite_array(native.get("utterance_class_scores"))
    if utterance.shape != (2,):
        raise ValueError("MultiReso utterance output must contain two classes")
    if native.get("utterance_class_order") != ["spoof", "bonafide"]:
        raise ValueError("MultiReso utterance class order missing")


def validate(model_id: str, manifest_path: Path, raw_path: Path, attempts_path: Path) -> dict[str, Any]:
    expected = list(read_case_manifest(manifest_path))
    expected_ids = [row["case_id"] for row in expected]
    if len(expected_ids) != EXPECTED_CASES or len(set(expected_ids)) != len(expected_ids):
        raise ValueError("case manifest is not the authorized complete population")
    expected_set = set(expected_ids)
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    forbidden: list[str] = []
    for record in read_jsonl(raw_path):
        case_id = record.get("case_id")
        if not isinstance(case_id, str) or case_id in seen:
            raise ValueError(f"duplicate/invalid raw case_id: {case_id!r}")
        seen.add(case_id)
        if record.get("terminal") is not True or record.get("status") not in ALLOWED_TERMINAL_STATUSES:
            raise ValueError(f"invalid terminal record for {case_id}")
        forbidden.extend(forbidden_keys(record))
        if record.get("status") == "VALID_INFERENCE":
            if not isinstance(record.get("native_outputs"), dict) or not isinstance(record.get("raw_output_sha256"), str):
                raise ValueError(f"{case_id}: valid record missing raw output/hash")
            if sha256_json(to_jsonable(record["native_outputs"])) != record["raw_output_sha256"]:
                raise ValueError(f"{case_id}: raw output hash mismatch")
            if record.get("sample_rate") != 16_000 or not math.isfinite(float(record.get("duration_sec"))):
                raise ValueError(f"{case_id}: invalid audio metadata")
            if model_id == "CFPRF":
                _validate_cfprf(record)
            else:
                _validate_multireso(record)
        records.append(record)
    if seen != expected_set:
        missing = expected_set - seen
        extra = seen - expected_set
        raise ValueError(f"raw completeness mismatch: missing={len(missing)} extra={len(extra)}")
    if forbidden:
        raise ValueError(f"GT-like keys found in model raw output: {forbidden[:5]}")
    if attempts_path.exists():
        attempts = list(read_jsonl(attempts_path))
    else:
        attempts = []
    per_case_attempts: dict[str, set[int]] = {}
    for attempt in attempts:
        case_id = attempt.get("case_id")
        number = attempt.get("attempt")
        if case_id not in expected_set or not isinstance(number, int) or not 1 <= number <= 2:
            raise ValueError("invalid attempt ledger record")
        per_case_attempts.setdefault(case_id, set()).add(number)
    for record in records:
        case_id = record["case_id"]
        attempt = record.get("attempt")
        if attempt not in per_case_attempts.get(case_id, set()):
            raise ValueError(f"{case_id}: terminal attempt absent from attempt ledger")
        if not 1 <= int(attempt) <= 2:
            raise ValueError(f"{case_id}: retry budget exceeded")
    counts: dict[str, int] = {status: 0 for status in ALLOWED_TERMINAL_STATUSES}
    runtime = []
    vram = []
    retries = 0
    for record in records:
        status = record["status"]
        counts[status] += 1
        retries += int(record.get("retry_count", 0))
        if status == "VALID_INFERENCE":
            runtime.append(float(record["runtime_sec"]))
            vram.append(int(record.get("peak_vram_bytes", 0)))
    return {
        "model_id": model_id,
        "expected_cases": len(expected_ids),
        "terminal_cases": len(records),
        "valid_cases": counts["VALID_INFERENCE"],
        "failed_cases": len(records) - counts["VALID_INFERENCE"],
        "counts_by_status": counts,
        "retry_count": retries,
        "raw_file": str(raw_path),
        "raw_file_sha256": sha256_file(raw_path),
        "attempts_file": str(attempts_path),
        "attempts_file_sha256": sha256_file(attempts_path) if attempts_path.exists() else None,
        "gt_keys_found": forbidden,
        "runtime_total_sec": float(sum(runtime)),
        "runtime_mean_sec": float(np.mean(runtime)) if runtime else None,
        "runtime_median_sec": float(np.median(runtime)) if runtime else None,
        "peak_vram_max_bytes": max(vram) if vram else 0,
        "raw_output_completeness": "PASS",
        "failure_accounting": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase3T raw output completeness and hashes")
    parser.add_argument("--model", choices=["CFPRF", "MultiResoModel-Simple"], required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--attempts", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    summary = validate(args.model, args.manifest, args.raw, args.attempts)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
