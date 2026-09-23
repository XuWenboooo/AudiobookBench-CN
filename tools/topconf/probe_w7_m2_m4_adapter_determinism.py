"""Run purpose-built M2/M4 adapter fixtures and print deterministic evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.w7_m2_m4_adapters import (  # noqa: E402
    M2RealAdapter, M4RealAdapter, current_runtime_identity,
    SYNTHETIC_ASSET_IDENTITY,
)
from audiobookbench.topconf.w7_synthetic_harness import Interval, StageContract, digest  # noqa: E402


FIXTURES = ROOT / "tests" / "topconf" / "fixtures" / "w7_m2_m4_adapter_cases_v1.json"
CONFIG = ROOT / "research_assurance" / "topconf" / "W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json"


def waveform(identity: str, count: int, *, clip: bool = False) -> np.ndarray:
    phase = int.from_bytes(hashlib.sha256(identity.encode()).digest()[:2], "big") / 65535.0
    positions = np.arange(count, dtype=np.float64)
    values = 0.2 * np.sin(positions * 0.013 + phase)
    if clip:
        values = np.linspace(-2.0, 2.0, count, dtype=np.float64)
    return values.astype(np.float32)


def execute_row(row: dict, family: str, config_hash: str) -> dict:
    source_id = f"SYNTH_SOURCE_{row.get('source_suffix', 'SRC')}"
    case = {**row, "data_origin": "synthetic", "distribution_id": "SYNTH_DIST_A",
            "condition_id": "synthetic_condition", "mechanism_family": family,
            "source_id": source_id,
            "waveform": waveform(row["case_id"], row["sample_count"], clip=row.get("source_clip", False))}
    intervals = tuple(Interval(pair[0], pair[1], i, i) for i, pair in enumerate(row["intervals"]))
    refs = []
    for ref in row.get("references", []):
        refs.append({
            **ref,
            "data_origin": "synthetic",
            "distribution_id": ref.get("distribution_id", "SYNTH_DIST_A"),
            "source_id": f"SYNTH_SOURCE_{ref.get('source_suffix', 'REF')}",
            "waveform": waveform(ref["case_id"], ref["sample_count"], clip=row.get("reference_clip", False)),
        })
    contract = StageContract(
        case["case_id"], case["distribution_id"], case["condition_id"], family,
        f"synthetic-wave:{case['case_id']}", hashlib.sha256(case["waveform"].tobytes()).hexdigest(),
        f"synthetic-transcript:{case['case_id']}", "synthetic-transcript-hash", intervals, 0,
        current_runtime_identity(), SYNTHETIC_ASSET_IDENTITY, "frozen-control-v1", "DEFERRED",
        "PASS", None, (),
    )
    adapter = (M2RealAdapter(case, list(reversed(refs)), config_hash=config_hash)
               if family == "cross_speaker_boundary_control"
               else M4RealAdapter(case, config_hash=config_hash))
    assert adapter.validate_runtime() and adapter.validate_assets()
    prepared = adapter.prepare_case(contract)
    output = adapter.execute(case["waveform"], intervals, seed=0)
    assert adapter.validate_output(case["waveform"], output, intervals)
    output_hash = hashlib.sha256(np.ascontiguousarray(output).tobytes()).hexdigest()
    provenance = adapter.emit_provenance(contract, output_hash)
    expected = row.get("expected_reference")
    if expected:
        assert prepared["reference_case_id"] == expected, (
            row["case_id"], prepared.get("reference_case_id"), expected)
    return {"case_id": row["case_id"], "schedule_hash": digest(json.dumps(
                {"case": row, "family": family, "config_hash": config_hash},
                sort_keys=True, separators=(",", ":")).encode()),
            "reference": prepared.get("reference_case_id", prepared.get("reference_sides")),
            "output_sha256": output_hash,
            "output_samples": len(output),
            "provenance": provenance}


def main() -> int:
    suite = json.loads(FIXTURES.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(CONFIG.read_bytes()).hexdigest()
    output = {}
    for key, family in (("m2", "cross_speaker_boundary_control"),
                        ("m4", "same_speaker_splice_crossfade_control")):
        output[key] = [execute_row(row, family, config_hash) for row in suite[key]
                       if "expected_failure" not in row]
    print(json.dumps({"runtime_identity": current_runtime_identity(),
                      "m2_count": len(output["m2"]), "m4_count": len(output["m4"]),
                      "results": output}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
