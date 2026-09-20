from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from audiobookbench.topconf.preparation.case_identity import (
    CaseIdentityError,
    assert_same_case_across_views,
    build_case_identity,
    validate_source_binding,
)
from audiobookbench.topconf.preparation.mechanism_identity import (
    MechanismIdentityError,
    build_mechanism_identity,
)
from audiobookbench.topconf.preparation.resampling_identity import (
    ResamplingTransformIdentity,
    apply_declared_resampling,
    validate_synthetic_transform,
)
from audiobookbench.topconf.preparation.temporal_gt_adapter import normalize_ground_truth


def _case(**changes: str) -> dict[str, str]:
    base = {
        "distribution_id": "toy",
        "distribution_version": "v1",
        "split_id": "eval",
        "source_audio_id": "source-1",
        "source_audio_hash": "a" * 64,
        "manipulation_id": "manip-1",
        "manipulation_family": "tts",
        "manipulation_mechanism": "voice_conditioned_tts_vc_replacement",
        "condition_id": "clean",
        "condition_type": "clean",
        "transform_id": "none",
        "transform_version": "v1",
        "audio_artifact_id": "audio-1",
        "audio_artifact_hash": "b" * 64,
        "gt_id": "gt-1",
        "gt_version": "v1",
        "whether_definition_id": "whether-a-v1",
        "localizer_id": "SAL",
        "model_checkpoint_id": "model-v1",
        "adapter_version": "adapter-v1",
    }
    base.update(changes)
    return base


def _mechanism(**changes: object) -> dict[str, object]:
    base: dict[str, object] = {
        "mechanism_family": "voice_conditioned_tts_vc_replacement",
        "implementation": "frozen-project-generator",
        "version": "v1",
        "parameter_set_id": "w7-mechanism-v1",
        "reference_rule": "predeclared_same_speaker_reference",
        "target_span_rule": "predeclared_source_span",
        "sample_rate": 16000,
        "codec_path": "pcm16",
        "seed_policy": "protocol-derived",
        "quality_gate_policy": "frozen-fail-closed",
        "parameters": {"crossfade_samples": 400, "gain_db": 0.0},
    }
    base.update(changes)
    return base


def test_case_id_is_stable_and_sensitive_to_scientific_identity():
    first = build_case_identity(_case())
    second = build_case_identity(_case())
    assert first["case_id"] == second["case_id"]
    assert first["case_identity_hash"] == second["case_identity_hash"]
    assert first["case_id"] != build_case_identity(_case(source_audio_id="source-2"))["case_id"]
    assert first["case_id"] != build_case_identity(_case(manipulation_id="manip-2"))["case_id"]
    assert first["case_id"] != build_case_identity(_case(condition_id="codec", condition_type="codec"))["case_id"]
    assert first["case_id"] != build_case_identity(_case(distribution_id="other"))["case_id"]


def test_case_identity_rejects_missing_identity_and_same_case_join_mismatch():
    with pytest.raises(CaseIdentityError):
        build_case_identity({})
    assert assert_same_case_across_views({"whether_a": "c", "whether_b": "c", "where": "c"}) == "c"
    with pytest.raises(CaseIdentityError):
        assert_same_case_across_views({"whether_a": "c", "whether_b": "other", "where": "c"})


def test_source_binding_requires_parent_child_lineage():
    binding = {
        "source": {"id": "source-1"},
        "manipulation": {"id": "manip-1", "parent_source_id": "source-1"},
        "condition_transform": {"id": "condition-1", "parent_manipulation_id": "manip-1"},
        "final_audio_artifact": {"id": "audio-1", "parent_condition_id": "condition-1"},
        "gt": {"id": "gt-1", "parent_audio_artifact_id": "audio-1"},
    }
    validate_source_binding(binding)
    binding["gt"]["parent_audio_artifact_id"] = "wrong"
    with pytest.raises(CaseIdentityError):
        validate_source_binding(binding)


def test_mechanism_hash_is_order_independent_but_parameter_sensitive():
    first = build_mechanism_identity(_mechanism())
    reordered = _mechanism(parameters={"gain_db": 0.0, "crossfade_samples": 400})
    changed = _mechanism(parameters={"crossfade_samples": 320, "gain_db": 0.0})
    assert first["mechanism_id"] == build_mechanism_identity(reordered)["mechanism_id"]
    assert first["mechanism_config_hash"] == build_mechanism_identity(reordered)["mechanism_config_hash"]
    assert first["mechanism_id"] != build_mechanism_identity(changed)["mechanism_id"]
    with pytest.raises(MechanismIdentityError):
        build_mechanism_identity({"mechanism_family": "unknown"})


def test_resampling_identity_and_synthetic_waveform_are_deterministic():
    identity = ResamplingTransformIdentity()
    waveform = np.linspace(-0.5, 0.5, 1600, dtype=np.float32)
    report = validate_synthetic_transform(waveform, identity)
    assert report["deterministic_array"] is True
    assert report["finite_output"] is True
    assert report["actual_output_frames"] == report["expected_output_frames"]
    assert report["duration_error_sec"] <= 1 / identity.output_sr
    assert np.array_equal(apply_declared_resampling(waveform, identity), apply_declared_resampling(waveform, identity))


def test_resampling_keeps_seconds_gt_and_maps_sample_gt_before_transform():
    identity = ResamplingTransformIdentity()
    waveform = np.zeros(1600, dtype=np.float32)
    transformed = apply_declared_resampling(waveform, identity)
    seconds = normalize_ground_truth(
        "intervals_sec", {"intervals": [{"start_sec": 0.025, "end_sec": 0.05}]}, duration_sec=0.1, sample_rate=16000
    )
    samples = normalize_ground_truth(
        "sample_index_intervals", {"sample_rate": 16000, "intervals": [{"start_sample": 400, "end_sample": 800}]}, duration_sec=0.1, sample_rate=16000
    )
    assert seconds == samples
    assert seconds[0].end_sec <= transformed.size / identity.output_sr


def test_identity_schemas_are_valid_and_case_payload_has_no_machine_path(tmp_path: Path):
    import jsonschema

    root = Path(__file__).resolve().parents[2] / "research_assurance/topconf/w7_preparation"
    schemas = {}
    for name in ("CASE_IDENTITY_SCHEMA_V1.json", "MECHANISM_CONFIG_SCHEMA_V1.json", "RESAMPLING_TRANSFORM_SCHEMA_V1.json"):
        schema = json.loads((root / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        schemas[name] = schema
    identity = build_case_identity(_case())
    assert not any("\\" in str(value) for value in identity.values() if value is not None)
    jsonschema.Draft202012Validator(schemas["CASE_IDENTITY_SCHEMA_V1.json"]).validate(identity)
    jsonschema.Draft202012Validator(schemas["MECHANISM_CONFIG_SCHEMA_V1.json"]).validate(build_mechanism_identity(_mechanism()))
    jsonschema.Draft202012Validator(schemas["RESAMPLING_TRANSFORM_SCHEMA_V1.json"]).validate(ResamplingTransformIdentity().as_dict())
