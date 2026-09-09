"""Narrow reference-free detector boundary used by Stage-A evaluators."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass(frozen=True)
class FrozenWindowSpec:
    name: str = "S2_1500ms_250ms"
    window_samples: int = 24000
    hop_samples: int = 4000

def score_reference_free(backend: Any, waveform: np.ndarray, sample_rate: int, window_spec: FrozenWindowSpec):
    if not isinstance(waveform, np.ndarray) or waveform.ndim != 1 or not np.isfinite(waveform).all():
        raise ValueError("detector waveform must be finite mono ndarray")
    if int(sample_rate) != 16000:
        raise ValueError("detector sample rate must be frozen 16 kHz")
    if not hasattr(backend, "embed_windows"):
        raise TypeError("backend does not implement embed_windows")
    from audiobookbench.temporal.day6b_scoring import b1_scores
    from audiobookbench.temporal.day6b_embed import SpeakerWindowScale, build_speaker_windows
    scale = SpeakerWindowScale(window_spec.name, window_spec.window_samples, window_spec.hop_samples)
    windows = build_speaker_windows(int(waveform.size), scale)
    embeddings = backend.embed_windows(waveform, [(w["sample_start"], w["sample_end"]) for w in windows])
    return np.asarray(b1_scores(embeddings, True), dtype=float), windows
