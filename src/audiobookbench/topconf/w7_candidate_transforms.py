"""Outcome-blind deterministic waveform adapters for the two control families."""
from __future__ import annotations

import numpy as np


VERSION = "w7_candidate_transforms_v1"
SAMPLE_RATE_HZ = 16_000
CROSSFADE_SAMPLES = 400


def _mono_float32(waveform: np.ndarray) -> np.ndarray:
    array = np.asarray(waveform, dtype=np.float32)
    if array.ndim == 2:
        array = array.mean(axis=1, dtype=np.float32)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("waveform must be a non-empty mono vector or channel-last matrix")
    if not np.isfinite(array).all():
        raise ValueError("waveform must be finite")
    return np.clip(array, -1.0, 1.0).astype(np.float32, copy=False)


def _resample_linear(segment: np.ndarray, length: int) -> np.ndarray:
    segment = _mono_float32(segment)
    if length <= 0:
        raise ValueError("length must be positive")
    if len(segment) == length:
        return segment.copy()
    old = np.linspace(0.0, 1.0, len(segment), dtype=np.float64)
    new = np.linspace(0.0, 1.0, length, dtype=np.float64)
    return np.interp(new, old, segment).astype(np.float32)


def _replace_with_crossfade(source: np.ndarray, replacement: np.ndarray, start: int, end: int) -> np.ndarray:
    source = _mono_float32(source)
    if not (0 <= start < end <= len(source)):
        raise ValueError("target span must be in source bounds")
    replacement = _resample_linear(replacement, end - start)
    output = source.copy()
    output[start:end] = replacement
    fade = min(CROSSFADE_SAMPLES, (end - start) // 2, start, len(source) - end)
    if fade > 0:
        left = np.linspace(1.0, 0.0, fade, endpoint=False, dtype=np.float32)
        right = 1.0 - left
        output[start - fade:start] = source[start - fade:start] * left + replacement[:fade] * right
        output[end - fade:end] = replacement[-fade:] * left + source[end - fade:end] * right
    return np.clip(output, -1.0, 1.0).astype(np.float32)


def same_speaker_splice_crossfade(source: np.ndarray, start: int, end: int) -> np.ndarray:
    """Use the nearest same-case context window, left first, then right."""
    source = _mono_float32(source)
    span = end - start
    if start >= span:
        reference = source[start - span:start]
    elif len(source) - end >= span:
        reference = source[end:end + span]
    else:
        raise ValueError("same-case source has no complete reference window")
    return _replace_with_crossfade(source, reference, start, end)


def cross_speaker_boundary(source: np.ndarray, reference: np.ndarray, start: int, end: int) -> np.ndarray:
    """Replace the target span with a deterministic different-speaker reference window."""
    return _replace_with_crossfade(_mono_float32(source), _mono_float32(reference), start, end)
