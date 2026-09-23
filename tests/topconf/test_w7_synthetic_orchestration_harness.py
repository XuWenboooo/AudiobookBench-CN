"""Engineering-only synthetic W7 orchestration checks."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.topconf.w7_synthetic_harness import (
    AppendOnlyLedger, DummyGateStage, DummyMetricStage, FAILURES, HarnessError,
    Interval, MARKER, MECHANISMS, MOCK_ASSET, MOCK_RUNTIME, NAMESPACES,
    REAL_ADAPTERS, STAGES, SimulatedCrash, SyntheticW7Harness, derive_subseed,
    digest, duration_fit, seconds_to_codec_frames, seconds_to_samples, splice,
    synthetic_waveform, validate_intervals,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
CONFIG = FIXTURE_ROOT / "w7_synthetic_config_v1.json"
CASES = json.loads((FIXTURE_ROOT / "w7_synthetic_cases_v1.json").read_text(encoding="utf-8"))
CONFIG_HASH = "4981ca7c24d197ffe31566e9b805cc19ae7e884b03c3a207d5d6d1ac82694552"


def make_harness(tmp_path: Path) -> SyntheticW7Harness:
    return SyntheticW7Harness(CONFIG, expected_config_hash=CONFIG_HASH,
                              output_root=tmp_path / "artifacts" / "w7_synthetic_harness")


def fixture(name: str) -> dict:
    return next(item for item in CASES if item["case_id"] == name)


def assert_code(code: str, fn) -> None:
    with pytest.raises(HarnessError) as error:
        fn()
    assert error.value.code == code


def test_fixture_scope_and_config_identity(tmp_path):
    assert len(CASES) == 15
    assert all(item["data_origin"] == "synthetic" and item["case_id"].startswith("SYNTH_") for item in CASES)
    assert digest(CONFIG.read_bytes()) == CONFIG_HASH
    assert make_harness(tmp_path).config["approval_state"] == "CANDIDATE_NOT_APPROVED"


def test_dry_run_is_deterministic_and_does_not_write_or_load(tmp_path):
    harness = make_harness(tmp_path)
    first = harness.dry_run(tuple(CASES))
    second = harness.dry_run(tuple(reversed(CASES)))
    assert first == second
    assert first["audio_loaded"] is False and first["models_loaded"] is False
    assert len(first["schedule"]) == 15
    three = next(item for item in first["schedule"] if item["case_id"] == "SYNTH_THREE")
    assert len(three["mask_group_seeds"]) == 2
    assert len(three["interval_seeds"]) == 3
    assert all(isinstance(three[key], int) for key in ("candidate_seed", "transform_seed"))
    assert len(first["schedule_hash"]) == 64
    assert not harness.output_root.exists()
    assert all(all(path.startswith("SYNTH_") for path in entry["expected_artifact_paths"])
               for entry in first["schedule"])


def test_full_fixture_schedule_records_every_terminal_case(tmp_path):
    harness = make_harness(tmp_path)
    summary = harness.run_schedule(tuple(reversed(CASES)))
    assert summary["case_count"] == 15
    assert [item["case_id"] for item in summary["terminal_cases"]] == sorted(item["case_id"] for item in CASES)
    assert sum(item["status"] == "SYNTHETIC_ORCHESTRATION_COMPLETE" for item in summary["terminal_cases"]) == 7
    assert sum(item["status"] == "TERMINAL_FAILURE" for item in summary["terminal_cases"]) == 8
    assert summary["schedule_hash"] == harness.dry_run(tuple(CASES))["schedule_hash"]
    assert summary["scientific_inferences"] == 0


@pytest.mark.parametrize("name,count", [
    ("SYNTH_SINGLE", 1), ("SYNTH_TWO", 2), ("SYNTH_THREE", 3),
    ("SYNTH_FOUR", 4), ("SYNTH_TWENTY", 20),
    ("SYNTH_BOUNDARY_START", 1), ("SYNTH_BOUNDARY_END", 1),
])
def test_full_pipeline_and_untouched_samples(tmp_path, name, count):
    harness = make_harness(tmp_path)
    case = fixture(name)
    result = harness.run(case)
    assert result["status"] == "SYNTHETIC_ORCHESTRATION_COMPLETE"
    assert result["stage_count"] == len(STAGES) == 13
    assert result["gate"] == {"marker": MARKER, "formal_gate": "NOT_EVALUATED", "status": "MOCK_INTERFACE_ONLY"}
    assert result["w7_execution_authorized"] is False and result["scientific_inferences"] == 0
    base = harness.output_root / name
    events = list((base / "ledger").glob("*.json"))
    assert len(events) == len(STAGES)
    stage = json.loads((base / "stages" / "MATERIALIZE_MECHANISM.json").read_text(encoding="utf-8"))
    assert len(stage["payload"]["composition_ledger"]) == count
    if name == "SYNTH_THREE":
        assert len(stage["payload"]["m3_observations"]) == 3
        assert all(item["generated_codec_frame_count"] > 0 for item in stage["payload"]["m3_observations"])
    original = synthetic_waveform(name, case["sample_count"])
    output_bytes = (harness.output_root / stage["payload"]["media_path"]).read_bytes()
    assert digest(output_bytes) == result["output_audio_hash"]
    output = np.frombuffer(output_bytes, dtype=np.float32)
    assert len(output) == len(original)
    mask = np.zeros(len(original), dtype=bool)
    for item in stage["payload"]["composition_ledger"]:
        mask[item["start"]:item["end"]] = True
    assert np.array_equal(original[~mask], output[~mask])
    raw = json.loads((base / "raw_non_scientific" / "combined.json").read_text(encoding="utf-8"))
    assert raw["marker"] == MARKER and raw["formal_w7_result"] is False
    assert all(value["marker"] == MARKER for value in raw["outputs"].values())
    assert not (tmp_path / "results" / "topconf" / "w7_pilot").exists()


@pytest.mark.parametrize("name,code", [
    ("SYNTH_EMPTY_MASK", "MASK_MAPPING_FAILURE"),
    ("SYNTH_OVERLAP_MASK", "MASK_MAPPING_FAILURE"),
    ("SYNTH_ALIGNMENT_FAIL", "ALIGNMENT_FAILURE"),
    ("SYNTH_GENERATION_FAIL", "GENERATION_FAILURE"),
    ("SYNTH_CODEC_FAIL", "TRANSFORM_FAILURE"),
    ("SYNTH_LOCALIZER_FAIL", "LOCALIZER_FAILURE"),
    ("SYNTH_WHETHER_A_FAIL", "WHETHER_A_FAILURE"),
    ("SYNTH_WHETHER_B_FAIL", "WHETHER_B_FAILURE"),
])
def test_failures_are_terminal_and_recorded(tmp_path, name, code):
    harness = make_harness(tmp_path)
    assert_code(code, lambda: harness.run(fixture(name)))
    events = [json.loads(path.read_text(encoding="utf-8"))
              for path in (harness.output_root / name / "ledger").glob("*.json")]
    failed = [event for event in events if event["status"] == "FAIL"]
    assert len(failed) == 1 and failed[0]["failure_code"] == code
    assert all(event["case_id"] == name and event["config_hash"] == CONFIG_HASH for event in events)
    assert_code(code, lambda: harness.run(fixture(name)))
    assert len(list((harness.output_root / name / "ledger").glob("*.json"))) == len(events)


def test_transcript_binding_failure_is_recorded(tmp_path):
    case = dict(fixture("SYNTH_SINGLE"), case_id="SYNTH_TRANSCRIPT_FAIL", transcript="not a synthetic transcript")
    harness = make_harness(tmp_path)
    assert_code("TRANSCRIPT_BINDING_FAILURE", lambda: harness.run(case))
    failed = [json.loads(path.read_text(encoding="utf-8")) for path in
              (harness.output_root / case["case_id"] / "ledger").glob("*.json")]
    assert any(item["failure_code"] == "TRANSCRIPT_BINDING_FAILURE" for item in failed)


def test_real_and_level2_guards_precede_audio_loader(tmp_path):
    harness = make_harness(tmp_path)
    calls = []

    def forbidden_loader(_case):
        calls.append("audio_read")
        raise AssertionError("audio loader must not run")

    real = {"case_id": "REAL_CASE", "data_origin": "real", "audio_path": "forbidden.wav"}
    assert_code("W7_REAL_EXECUTION_BLOCKED_UNAPPROVED_CONFIG",
                lambda: harness.run(real, audio_loader=forbidden_loader, execution_authorized=False))
    assert_code("INPUT_NOT_SYNTHETIC",
                lambda: harness.run(fixture("SYNTH_SINGLE"), audio_loader=forbidden_loader, request_level2=True))
    assert_code("CONFIG_NOT_APPROVED",
                lambda: harness.run(fixture("SYNTH_SINGLE"), audio_loader=forbidden_loader, execution_authorized=True))
    assert_code("CONFIG_NOT_APPROVED",
                lambda: harness.run(fixture("SYNTH_SINGLE"), audio_loader=forbidden_loader, runtime_identity="unknown"))
    assert_code("CONFIG_NOT_APPROVED",
                lambda: harness.run(fixture("SYNTH_SINGLE"), audio_loader=forbidden_loader, asset_identity="unfrozen"))
    assert calls == []
    assert not harness.output_root.exists()


def test_unknown_config_hash_and_namespace_guard(tmp_path):
    assert_code("CONFIG_NOT_APPROVED", lambda: SyntheticW7Harness(CONFIG, expected_config_hash="0" * 64,
                output_root=tmp_path / "artifacts" / "w7_synthetic_harness"))
    assert_code("RAW_OUTPUT_WRITE_FAILURE", lambda: SyntheticW7Harness(CONFIG, expected_config_hash=CONFIG_HASH,
                output_root=tmp_path / "results" / "topconf" / "w7_pilot"))


def test_spoofed_synthetic_case_cannot_supply_external_audio(tmp_path):
    harness = make_harness(tmp_path)
    disguised = dict(fixture("SYNTH_SINGLE"), audio_path="real-w7-audio.wav")
    assert_code("INPUT_NOT_SYNTHETIC", lambda: harness.run(disguised))
    assert not harness.output_root.exists()


def test_seed_namespaces_and_restart_stability():
    policy = json.loads(CONFIG.read_text(encoding="utf-8"))["namespace_policy"]
    assert set(policy) == set(NAMESPACES)
    for namespace in NAMESPACES:
        a = derive_subseed(7, policy, namespace, "SYNTH_CASE", 0)
        assert a == derive_subseed(7, policy, namespace, "SYNTH_CASE", 0)
        assert a != derive_subseed(7, policy, namespace, "SYNTH_CASE", 1)


def test_timeline_half_open_resampling_order_and_hashes():
    assert seconds_to_samples(0.25, 16000) == 4000
    assert seconds_to_codec_frames(0.25, 75) == 19
    source = np.arange(20, dtype=np.float32)
    intervals = validate_intervals((Interval(10, 14, 1, 1), Interval(0, 3, 0, 0)), len(source))
    assert [(x.start, x.end, x.ordinal) for x in intervals] == [(0, 3, 0), (10, 14, 1)]
    out = splice(source, (np.array([9], dtype=np.float32), np.array([8, 7], dtype=np.float32)), intervals)
    assert len(out) == len(source)
    assert np.array_equal(out[3:10], source[3:10]) and np.array_equal(out[14:], source[14:])
    assert np.array_equal(out[:3], np.array([9, 9, 9], dtype=np.float32))
    assert digest(out.tobytes()) == digest(splice(source, (np.array([9], dtype=np.float32),
                                               np.array([8, 7], dtype=np.float32)), intervals).tobytes())
    assert len(duration_fit(np.array([1, 2], dtype=np.float32), 9)) == 9
    assert_code("MASK_MAPPING_FAILURE", lambda: validate_intervals((Interval(1, 5, 0, 0), Interval(4, 6, 1, 1)), 20))


@pytest.mark.parametrize("crash_stage", [
    "MATERIALIZE_MECHANISM", "RUN_LOCALIZER", "RUN_WHETHER_A", "RUN_WHETHER_B"
])
def test_crash_resume_without_duplicate_events_or_overwrite(tmp_path, crash_stage):
    case = fixture("SYNTH_THREE")
    recovering = make_harness(tmp_path / "interrupted")
    with pytest.raises(SimulatedCrash):
        recovering.run(case, crash_after=crash_stage)
    base = recovering.output_root / case["case_id"]
    before = {path.name: path.read_bytes() for path in (base / "ledger").glob("*.json")}
    resumed = recovering.run(case)
    after = {path.name: path.read_bytes() for path in (base / "ledger").glob("*.json")}
    assert all(after[name] == content for name, content in before.items())
    assert len(after) == len(STAGES)
    clean = make_harness(tmp_path / "clean").run(case)
    assert resumed["schedule_hash"] == clean["schedule_hash"]
    assert resumed["output_audio_hash"] == clean["output_audio_hash"]
    assert resumed["gate"] == clean["gate"]


def test_real_adapter_contracts_remain_not_ready():
    assert set(REAL_ADAPTERS) == set(MECHANISMS)
    for adapter in REAL_ADAPTERS.values():
        assert adapter.validate_runtime(MOCK_RUNTIME) is False
        assert adapter.validate_assets(MOCK_ASSET) is False
        assert_code("GENERATION_FAILURE", lambda adapter=adapter: adapter.execute(np.zeros(10, dtype=np.float32), (), 1))


def test_formal_metric_and_gate_cannot_consume_unmarked_output():
    assert_code("METRIC_STAGE_BLOCKED", lambda: DummyMetricStage().compute({"formal": True}))
    assert_code("GATE_STAGE_BLOCKED", lambda: DummyGateStage().evaluate({"formal": True}))
    assert set(FAILURES) >= {"METRIC_STAGE_BLOCKED", "GATE_STAGE_BLOCKED", "RAW_OUTPUT_WRITE_FAILURE"}


def test_resume_detects_tampered_stage_record(tmp_path):
    harness = make_harness(tmp_path)
    case = fixture("SYNTH_SINGLE")
    with pytest.raises(SimulatedCrash):
        harness.run(case, crash_after="MATERIALIZE_MECHANISM")
    path = harness.output_root / case["case_id"] / "stages" / "MATERIALIZE_MECHANISM.json"
    path.write_bytes(path.read_bytes() + b" ")
    assert_code("RAW_OUTPUT_WRITE_FAILURE", lambda: harness.run(case))


def test_dummy_adapter_exception_becomes_terminal_ledger_failure(tmp_path):
    class BrokenLocalizer:
        def infer(self, audio_hash, intervals):
            raise RuntimeError("test injection")

    harness = SyntheticW7Harness(CONFIG, expected_config_hash=CONFIG_HASH,
                                 output_root=tmp_path / "artifacts" / "w7_synthetic_harness",
                                 localizer=BrokenLocalizer())
    assert_code("LOCALIZER_FAILURE", lambda: harness.run(fixture("SYNTH_SINGLE")))
    events = [json.loads(path.read_text(encoding="utf-8")) for path in
              (harness.output_root / "SYNTH_SINGLE" / "ledger").glob("*.json")]
    assert sum(event["failure_code"] == "LOCALIZER_FAILURE" for event in events) == 1
