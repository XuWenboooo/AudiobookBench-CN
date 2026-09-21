import hashlib
import json
from pathlib import Path

import numpy as np

from audiobookbench.topconf.w7_candidate_transforms import cross_speaker_boundary, same_speaker_splice_crossfade


ROOT = Path(__file__).resolve().parents[2] / "research_assurance" / "topconf"
PACKAGE = ROOT / "W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1.json"


def load_package():
    return json.loads(PACKAGE.read_text(encoding="utf-8"))


def test_five_families_and_35_field_coverage_are_complete_but_unapproved():
    package = load_package()
    assert package["status"] == "PROPOSED_NOT_HUMAN_APPROVED"
    assert list(package["families"]) == [
        "conventional_tts_replacement",
        "cross_speaker_boundary_control",
        "neural_speech_editing_infilling",
        "same_speaker_splice_crossfade_control",
        "voice_conditioned_tts_vc_replacement",
    ]
    assert package["raw_p4_fields"] == 35
    assert package["total_covered_fields"] == 35
    assert package["unaccounted_fields"] == 0
    assert package["implementation_bindings_complete"] is True
    assert package["candidate_execution_authorization"] == "NO"


def test_candidates_have_no_ambiguous_placeholders_and_have_required_bindings():
    package = load_package()
    required = {"implementation", "version", "parameter_set_id", "reference_rule", "target_span_rule", "codec_path", "parameters", "source_revision", "entrypoint"}
    text = PACKAGE.read_text(encoding="utf-8").upper()
    for placeholder in ("TBD", "AUTO", "LATEST", "DEFAULT"):
        assert placeholder not in text
    for family, record in package["families"].items():
        candidate = record["candidate"]
        assert required.issubset(candidate), family
        assert candidate["candidate"] == "A"
        assert candidate["bundle_hash"] == hashlib.sha256(json.dumps({k: v for k, v in candidate.items() if k != "bundle_hash"}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()
        assert record["recommended_candidate"] == "A"


def test_proposed_package_hash_is_canonical_and_case_map_is_unchanged():
    package = load_package()
    without_hash = {key: value for key, value in package.items() if key != "proposed_package_sha256"}
    expected = hashlib.sha256(json.dumps(without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()
    assert package["proposed_package_sha256"] == expected
    assert package["mechanism_case_map_sha256"] == "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9"


def test_project_control_adapters_are_synthetic_deterministic_only():
    source = np.linspace(-0.5, 0.5, 4000, dtype=np.float32)
    reference = np.linspace(0.5, -0.5, 1000, dtype=np.float32)
    first = same_speaker_splice_crossfade(source, 1600, 2400)
    second = same_speaker_splice_crossfade(source, 1600, 2400)
    cross_first = cross_speaker_boundary(source, reference, 1600, 2400)
    cross_second = cross_speaker_boundary(source, reference, 1600, 2400)
    assert np.array_equal(first, second)
    assert np.array_equal(cross_first, cross_second)
    assert first.shape == source.shape == cross_first.shape
    assert np.isfinite(first).all() and np.isfinite(cross_first).all()
    assert float(np.max(np.abs(first))) <= 1.0
    assert float(np.max(np.abs(cross_first))) <= 1.0
