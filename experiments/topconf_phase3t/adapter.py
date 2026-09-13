from __future__ import annotations

from typing import Any

import numpy as np

try:  # Supports both package imports in tests and direct script execution.
    from .common import assert_finite_tree, read_jsonl, to_jsonable
except ImportError:  # pragma: no cover - exercised by the command-line entry point
    from common import assert_finite_tree, read_jsonl, to_jsonable


class AdapterError(ValueError):
    """Raised when native output cannot be mapped without semantic repair."""


def deterministic_supports(count: int, unit_sec: float, duration_sec: float) -> np.ndarray:
    if count <= 0 or not np.isfinite([unit_sec, duration_sec]).all() or unit_sec <= 0 or duration_sec <= 0:
        raise AdapterError("support arguments must be finite and positive")
    supports = np.asarray([[i * unit_sec, (i + 1) * unit_sec] for i in range(count)], dtype=float)
    if not np.isfinite(supports).all() or np.any(supports[:, 1] <= supports[:, 0]):
        raise AdapterError("generated supports are invalid")
    if np.any(supports[1:, 0] < supports[:-1, 1]):
        raise AdapterError("generated supports are not monotonic")
    # No duration clipping is performed. A model/output mismatch is a gate
    # failure, not an invitation to alter a support on a per-case basis.
    if np.any(supports[:, 1] > duration_sec + 1e-9):
        raise AdapterError("native support exceeds waveform duration")
    return supports


def _canonical(record: dict[str, Any], representation_id: str, supports: np.ndarray, class_scores: np.ndarray) -> dict[str, Any]:
    if class_scores.ndim != 2 or class_scores.shape[1] != 2 or len(class_scores) != len(supports):
        raise AdapterError(f"{representation_id}: expected aligned N x 2 class scores")
    assert_finite_tree(class_scores)
    result = {
        "case_id": record["case_id"],
        "case_index": record["case_index"],
        "model_id": record["model_id"],
        "representation_id": representation_id,
        "dataset_id": record["dataset_id"],
        "duration_sec": record["duration_sec"],
        "frame_times_sec": supports,
        "frame_scores": class_scores[:, 0],
        "native_class_scores": class_scores,
        "class_order": ["spoof", "bonafide"],
        "adapter_version": "phase3t_adapter_v1",
    }
    assert_finite_tree(result)
    return result


def adapt_cfprf(record: dict[str, Any]) -> list[dict[str, Any]]:
    if record.get("status") != "VALID_INFERENCE":
        return []
    native = record.get("native_outputs")
    if not isinstance(native, dict):
        raise AdapterError("CFPRF native outputs missing")
    scores = np.asarray(native.get("fdn_segment_scores"), dtype=float)
    boundary = np.asarray(native.get("fdn_boundary_scores"), dtype=float)
    supports = deterministic_supports(len(scores), 0.02, float(record["duration_sec"]))
    if boundary.shape != scores.shape:
        raise AdapterError("CFPRF boundary and segment shapes differ")
    return [
        _canonical(record, "CFPRF_FDN_20ms", supports, scores),
        _canonical(record, "CFPRF_BOUNDARY_20ms", supports, boundary),
    ]


def adapt_multireso(record: dict[str, Any]) -> list[dict[str, Any]]:
    if record.get("status") != "VALID_INFERENCE":
        return []
    native = record.get("native_outputs")
    if not isinstance(native, dict) or not isinstance(native.get("scales"), dict):
        raise AdapterError("MultiReso native scales missing")
    output: list[dict[str, Any]] = []
    for scale_id, scale in native["scales"].items():
        if not isinstance(scale, dict):
            raise AdapterError(f"{scale_id}: invalid scale record")
        scores = np.asarray(scale.get("native_class_scores"), dtype=float)
        unit = float(scale.get("unit_sec"))
        times = np.asarray(scale.get("native_times_sec"), dtype=float)
        supports = deterministic_supports(len(scores), unit, float(record["duration_sec"]))
        if times.shape != supports.shape or not np.allclose(times, supports, rtol=0, atol=1e-12):
            raise AdapterError(f"{scale_id}: native times do not match deterministic mapping")
        output.append(_canonical(record, f"MRM_{scale_id}", supports, scores))
    if len(output) != 6:
        raise AdapterError(f"MultiReso must preserve six scales, got {len(output)}")
    return output


def adapt_raw_file(raw_path: str, output_path: str, model_id: str) -> dict[str, int]:
    import json
    from pathlib import Path

    output = Path(output_path)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite canonical output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = {"terminal": 0, "valid": 0, "canonical": 0, "failures": 0}
    function = adapt_cfprf if model_id == "CFPRF" else adapt_multireso
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in read_jsonl(raw_path):
            counts["terminal"] += 1
            if record.get("status") != "VALID_INFERENCE":
                counts["failures"] += 1
                continue
            counts["valid"] += 1
            for canonical in function(record):
                handle.write(json.dumps(to_jsonable(canonical), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
                counts["canonical"] += 1
    return counts


def main() -> None:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Map Phase3T native output to the canonical temporal schema")
    parser.add_argument("--model", choices=["CFPRF", "MultiResoModel-Simple"], required=True)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    summary = adapt_raw_file(str(args.raw), str(args.output), args.model)
    summary.update({"model_id": args.model, "canonical_file": str(args.output)})
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
