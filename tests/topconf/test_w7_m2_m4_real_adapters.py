"""Synthetic-only contract and determinism tests for frozen W7 M2/M4 adapters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from audiobookbench.topconf.w7_candidate_transforms import CROSSFADE_SAMPLES, cross_speaker_boundary
from audiobookbench.topconf.w7_m2_m4_adapters import (
    M2RealAdapter, M4RealAdapter, SYNTHETIC_ASSET_IDENTITY, current_runtime_identity, normalize_audio,
)
from audiobookbench.topconf.w7_synthetic_harness import (
    HarnessError, Interval, StageContract, SyntheticW7Harness, digest, synthetic_waveform,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads((ROOT / "tests/topconf/fixtures/w7_m2_m4_adapter_cases_v1.json").read_text(encoding="utf-8"))
HARNESS_CONFIG = ROOT / "tests/topconf/fixtures/w7_synthetic_config_v1.json"
HARNESS_CONFIG_HASH = hashlib.sha256((ROOT / "tests/topconf/fixtures/w7_synthetic_config_v1.json").read_bytes()).hexdigest()
ADAPTER_CONFIG_HASH = hashlib.sha256((ROOT / "research_assurance/topconf/W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json").read_bytes()).hexdigest()


def purpose_wave(identity: str, count: int, *, clip: bool = False) -> np.ndarray:
    phase = int.from_bytes(hashlib.sha256(identity.encode()).digest()[:2], "big") / 65535.0
    values = 0.2 * np.sin(np.arange(count, dtype=np.float64) * 0.013 + phase)
    if clip:
        values = np.linspace(-2.0, 2.0, count, dtype=np.float64)
    return values.astype(np.float32)


def make_contract(case: dict, intervals: tuple[Interval, ...], family: str) -> StageContract:
    return StageContract(
        case["case_id"], case["distribution_id"], "synthetic_condition", family,
        f"synthetic-wave:{case['case_id']}", digest(case["waveform"].tobytes()),
        f"synthetic-transcript:{case['case_id']}", "synthetic-transcript-hash", intervals, 0,
        current_runtime_identity(), SYNTHETIC_ASSET_IDENTITY, "frozen-control-v1", "DEFERRED", "PASS", None, (),
    )


def make_direct_fixture(row: dict, family: str):
    case = {**row, "data_origin": "synthetic", "distribution_id": "SYNTH_DIST_A",
            "source_id": f"SYNTH_SOURCE_{row.get('source_suffix', 'SRC')}",
            "waveform": purpose_wave(row["case_id"], row["sample_count"], clip=row.get("source_clip", False))}
    intervals = tuple(Interval(a, b, i, i) for i, (a, b) in enumerate(row["intervals"]))
    refs = [{**ref, "data_origin": "synthetic", "distribution_id": ref.get("distribution_id", "SYNTH_DIST_A"),
             "source_id": f"SYNTH_SOURCE_{ref.get('source_suffix', 'REF')}",
             "waveform": purpose_wave(ref["case_id"], ref["sample_count"], clip=row.get("reference_clip", False))}
            for ref in row.get("references", [])]
    adapter = (M2RealAdapter(case, list(reversed(refs)), config_hash=ADAPTER_CONFIG_HASH)
               if family == "cross_speaker_boundary_control" else M4RealAdapter(case, config_hash=ADAPTER_CONFIG_HASH))
    return case, intervals, adapter, make_contract(case, intervals, family)


@pytest.mark.parametrize("family,key", [
    ("cross_speaker_boundary_control", "m2"),
    ("same_speaker_splice_crossfade_control", "m4"),
])
def test_all_successful_purpose_fixtures_obey_adapter_contract(family, key):
    rows = [row for row in FIXTURES[key] if "expected_failure" not in row]
    assert len(rows) >= 10
    for row in rows:
        case, intervals, adapter, ct = make_direct_fixture(row, family)
        assert adapter.validate_runtime() and adapter.validate_runtime(ct.runtime_identity)
        assert adapter.validate_assets() and adapter.validate_assets(ct.asset_identity)
        prepared = adapter.prepare_case(ct)
        output = adapter.execute(case["waveform"], intervals, seed=0)
        assert adapter.validate_output(case["waveform"], output, intervals), row["case_id"]
        assert output.dtype == np.float32 and output.ndim == 1
        assert len(output) == len(adapter._normalized_source)
        assert np.isfinite(output).all() and output.min() >= -1 and output.max() <= 1
        assert all(item["ordinal"] == i and item["composition_order"] == i
                   for i, item in enumerate(prepared["mapped_intervals"]))
        out_hash = hashlib.sha256(output.tobytes()).hexdigest()
        provenance = adapter.emit_provenance(ct, out_hash)
        assert provenance["case_id"] == row["case_id"] and provenance["mechanism_family"] == family
        assert provenance["crossfade_samples"] == 400 and provenance["interpolation"] == "linear"
        assert provenance["output_hash"] == out_hash and provenance["runtime_identity"] == current_runtime_identity()
        assert provenance["failure_code"] is None
        if family == "cross_speaker_boundary_control":
            assert provenance["different_source_id_check"] == "PASS"
            assert provenance["lexicographic_reference_rank"] == 1
            if row.get("expected_reference"):
                assert prepared["reference_case_id"] == row["expected_reference"]
        else:
            assert all(side in {"left", "right"} for side in provenance["reference_sides"])


@pytest.mark.parametrize("family,key,case_id,expected", [
    ("cross_speaker_boundary_control", "m2", "SYNTH_M2_NOREF", "GENERATION_FAILURE"),
    ("cross_speaker_boundary_control", "m2", "SYNTH_M2_INVALIDREF", "TRANSFORM_FAILURE"),
    ("same_speaker_splice_crossfade_control", "m4", "SYNTH_M4_NEITHER", "GENERATION_FAILURE"),
    ("same_speaker_splice_crossfade_control", "m4", "SYNTH_M4_SHORT", "GENERATION_FAILURE"),
])
def test_no_reference_or_context_is_a_terminal_failure(family, key, case_id, expected):
    row = next(row for row in FIXTURES[key] if row["case_id"] == case_id)
    _, _, adapter, ct = make_direct_fixture(row, family)
    with pytest.raises(HarnessError) as err:
        adapter.prepare_case(ct)
    assert err.value.code == expected


def test_m2_lexical_reference_selection_and_different_source_enforcement():
    row = next(row for row in FIXTURES["m2"] if row["case_id"] == "SYNTH_M2_MULTIREF")
    _, _, adapter, ct = make_direct_fixture(row, "cross_speaker_boundary_control")
    prepared = adapter.prepare_case(ct)
    assert prepared["candidate_order"] == ["SYNTH_M2_MULTIREF_B", "SYNTH_M2_MULTIREF_C"]
    assert prepared["reference_case_id"] == "SYNTH_M2_MULTIREF_B"
    assert prepared["reference_source_id"] != adapter.case["source_id"]


def test_m4_reference_prefers_left_then_falls_back_to_right():
    expected = {"SYNTH_M4_LEFT": "left", "SYNTH_M4_RIGHT": "right",
                "SYNTH_M4_PREFERLEFT": "left", "SYNTH_M4_FALLBACK": "right"}
    for case_id, side in expected.items():
        row = next(row for row in FIXTURES["m4"] if row["case_id"] == case_id)
        _, _, adapter, ct = make_direct_fixture(row, "same_speaker_splice_crossfade_control")
        assert adapter.prepare_case(ct)["reference_sides"] == [side]


def test_normalization_is_mono_finite_clipped_and_16khz():
    stereo = np.column_stack((np.linspace(-2, 2, 800), np.linspace(2, -2, 800)))
    normalized = normalize_audio(stereo, 8000)
    assert normalized.dtype == np.float32 and normalized.ndim == 1 and len(normalized) == 1600
    assert np.isfinite(normalized).all() and normalized.min() >= -1 and normalized.max() <= 1


def test_frozen_crossfade_400_numeric_endpoints_monotonicity_and_support():
    source = np.zeros(2400, dtype=np.float32)
    replacement = np.ones(800, dtype=np.float32)
    output = cross_speaker_boundary(source, replacement, 600, 1400)
    weights = np.linspace(1.0, 0.0, CROSSFADE_SAMPLES, endpoint=False, dtype=np.float32)
    assert CROSSFADE_SAMPLES == 400 and weights[0] == 1.0
    assert weights[-1] == pytest.approx(1 / 400, abs=1e-8) and np.all(np.diff(weights) < 0)
    assert np.allclose(output[200:600], 1.0 - weights)
    assert output[200] == 0.0 and output[599] == pytest.approx(399 / 400, abs=1e-7)
    assert output[1000] == 1.0 and output[1399] == pytest.approx(1 / 400, abs=1e-7)
    assert np.array_equal(output[:200], source[:200]) and np.array_equal(output[1400:], source[1400:])


def test_harness_real_adapter_mode_writes_provenance_without_formal_gate(tmp_path):
    row = next(row for row in FIXTURES["m2"] if row["case_id"] == "SYNTH_M2_DISTINCT")
    family = "cross_speaker_boundary_control"
    meta = {"case_id": row["case_id"], "data_origin": "synthetic", "distribution_id": "SYNTH_DIST_A",
            "condition_id": "synthetic_condition", "mechanism_family": family,
            "source_id": "SYNTH_SOURCE_SRC", "sample_count": row["sample_count"],
            "intervals": [row["intervals"][0]],
            "transcript": f"synthetic {row['case_id']}"}
    ref = row["references"][0]
    pool = [{**ref, "data_origin": "synthetic", "distribution_id": "SYNTH_DIST_A", "source_id": "SYNTH_SOURCE_B",
             "waveform": purpose_wave(ref["case_id"], ref["sample_count"])}]
    adapter = M2RealAdapter({**meta, "waveform": synthetic_waveform(row["case_id"], row["sample_count"])},
                            pool, config_hash=ADAPTER_CONFIG_HASH)
    harness = SyntheticW7Harness(HARNESS_CONFIG, expected_config_hash=HARNESS_CONFIG_HASH,
                                 output_root=tmp_path / "artifacts" / "w7_synthetic_harness")
    result = harness.run(meta, adapter_mode="real_adapter_synthetic_fixture", real_adapter=adapter)
    assert result["w7_execution_authorized"] is False and result["scientific_inferences"] == 0
    assert result["gate"]["formal_gate"] == "NOT_EVALUATED"
    path = harness.output_root / row["case_id"] / "adapter_provenance" / f"{family}.json"
    provenance = json.loads(path.read_text(encoding="utf-8"))
    assert provenance["case_id"] == row["case_id"] and provenance["output_hash"] == result["output_audio_hash"]


def test_harness_real_adapter_mode_integrates_m4_and_records_context_provenance(tmp_path):
    row = next(row for row in FIXTURES["m4"] if row["case_id"] == "SYNTH_M4_LEFT")
    family = "same_speaker_splice_crossfade_control"
    meta = {"case_id": row["case_id"], "data_origin": "synthetic", "distribution_id": "SYNTH_DIST_A",
            "condition_id": "synthetic_condition", "mechanism_family": family,
            "source_id": "SYNTH_SOURCE_M4", "sample_count": row["sample_count"],
            "intervals": [row["intervals"][0]], "transcript": f"synthetic {row['case_id']}"}
    adapter = M4RealAdapter({**meta, "waveform": synthetic_waveform(row["case_id"], row["sample_count"])},
                            config_hash=ADAPTER_CONFIG_HASH)
    harness = SyntheticW7Harness(HARNESS_CONFIG, expected_config_hash=HARNESS_CONFIG_HASH,
                                 output_root=tmp_path / "artifacts" / "w7_synthetic_harness")
    result = harness.run(meta, adapter_mode="real_adapter_synthetic_fixture", real_adapter=adapter)
    provenance_path = harness.output_root / row["case_id"] / "adapter_provenance" / f"{family}.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert result["output_audio_hash"] == provenance["output_hash"]
    assert provenance["reference_side"] == "left"
    assert provenance["reference_windows"][0]["start"] < provenance["reference_windows"][0]["end"]


def test_real_case_is_blocked_before_adapter_validation_or_execution(tmp_path):
    harness = SyntheticW7Harness(HARNESS_CONFIG, expected_config_hash=HARNESS_CONFIG_HASH,
                                 output_root=tmp_path / "artifacts" / "w7_synthetic_harness")

    class NeverRun:
        family = "cross_speaker_boundary_control"
        runtime_identity = current_runtime_identity()
        asset_identity = SYNTHETIC_ASSET_IDENTITY

        def validate_runtime(self, identity=None):
            raise AssertionError("real adapter was reached")

    case = {"case_id": "W7_CASE_FORBIDDEN", "data_origin": "real",
            "mechanism_family": "cross_speaker_boundary_control"}
    with pytest.raises(HarnessError) as err:
        harness.run(case, adapter_mode="real_adapter_synthetic_fixture", real_adapter=NeverRun())
    assert err.value.code == "W7_REAL_EXECUTION_BLOCKED"
    assert not harness.output_root.exists()


def test_two_clean_processes_match_schedule_reference_output_hash_and_provenance():
    script = ROOT / "tools/topconf/probe_w7_m2_m4_adapter_determinism.py"
    runs = []
    for _ in range(2):
        done = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, capture_output=True, text=True)
        runs.append(json.loads(done.stdout))
    assert runs[0] == runs[1]
    assert runs[0]["m2_count"] >= 10 and runs[0]["m4_count"] >= 10
    assert all(len(item["output_sha256"]) == 64 for group in runs[0]["results"].values() for item in group)
