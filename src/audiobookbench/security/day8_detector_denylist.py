"""Fail-closed separation of attack-side metadata from detector inputs."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


FORBIDDEN_KEY_PREFIXES = (
    "reference_",
    "conditioning_",
    "speaker_enrollment_",
    "attack_side_embedding",
)
FORBIDDEN_EXACT_KEYS = {
    "target_speaker",
    "replacement_speaker",
    "generator",
    "generator_family",
    "attack_generator",
    "attack_interval",
    "attack_start_sample",
    "attack_end_sample",
    "source_text_exact",
    "tts_input_text",
    "split", "gt", "lineage", "seed", "reference_audio", "reference_text",
    "attack_start", "attack_end", "attack_start_sample", "attack_end_sample",
}


class DetectorLeakageError(ValueError):
    """Raised when a detector input contains attack-side information."""


def assert_detector_inputs_safe(value: Any, *, path: str = "input") -> None:
    """Reject forbidden metadata recursively before feature/scoring calls.

    Numeric waveform arrays are deliberately opaque here.  Mappings and named
    records are inspected because those are the route through which reference,
    enrollment, generator, text, or attack-GT metadata could leak into B0/B1/B2.
    """
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key)
            lowered = name.lower()
            if lowered in FORBIDDEN_EXACT_KEYS or lowered.startswith(FORBIDDEN_KEY_PREFIXES):
                raise DetectorLeakageError(f"forbidden detector input key at {path}.{name}")
            assert_detector_inputs_safe(child, path=f"{path}.{name}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            assert_detector_inputs_safe(child, path=f"{path}[{index}]")
