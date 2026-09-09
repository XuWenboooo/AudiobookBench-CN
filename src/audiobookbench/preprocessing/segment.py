from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    index: int

    @property
    def duration(self) -> float:
        return self.end - self.start


def fixed_windows(
    duration: float,
    window_seconds: float = 5.0,
    *,
    min_tail_seconds: float = 0.0,
) -> list[Segment]:
    """Create deterministic non-overlapping time windows.

    If the final tail is shorter than ``min_tail_seconds``, it is merged into the
    preceding window instead of creating a tiny final segment.
    """
    if duration <= 0:
        return []
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")
    if min_tail_seconds < 0:
        raise ValueError("min_tail_seconds must be >= 0")

    segments: list[Segment] = []
    start = 0.0
    idx = 0
    while start < duration:
        end = min(duration, start + window_seconds)
        tail = duration - end
        if end < duration and 0 < tail < min_tail_seconds:
            end = duration
        segments.append(Segment(start=start, end=end, index=idx))
        start = end
        idx += 1
    return segments


def slice_segment(audio: np.ndarray, sr: int, segment: Segment) -> np.ndarray:
    if sr <= 0:
        raise ValueError("sr must be > 0")
    waveform = np.asarray(audio)
    start = max(0, int(round(segment.start * sr)))
    end = min(len(waveform), int(round(segment.end * sr)))
    if end <= start:
        return np.asarray([], dtype=waveform.dtype)
    return waveform[start:end]


def _frame_energy(audio: np.ndarray, frame_size: int, hop: int) -> np.ndarray:
    waveform = np.asarray(audio, dtype=np.float32)
    if frame_size <= 0 or hop <= 0:
        raise ValueError("frame_size and hop must be > 0")
    if waveform.size == 0:
        return np.array([], dtype=np.float32)
    if waveform.size < frame_size:
        return np.array([np.mean(waveform**2)], dtype=np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(waveform, frame_size)[::hop]
    return np.mean(frames**2, axis=1).astype(np.float32)


def simple_energy_vad(
    audio: np.ndarray,
    frame_size: int = 400,
    hop: int = 160,
    threshold_ratio: float = 0.25,
) -> np.ndarray:
    """Return a frame-level voiced mask using an energy threshold.

    This is intentionally a sanity-check baseline, not a production VAD. Formal
    experiments should later compare against a validated speech VAD backend.
    """
    if not 0.0 <= threshold_ratio <= 1.0:
        raise ValueError("threshold_ratio must be in [0, 1]")
    energy = _frame_energy(audio, frame_size, hop)
    if energy.size == 0:
        return np.array([], dtype=bool)

    peak = float(np.max(energy))
    if peak <= 1e-12:
        return np.zeros_like(energy, dtype=bool)
    floor = float(np.quantile(energy, 0.2))
    if np.isclose(peak, floor, rtol=1e-5, atol=1e-12):
        threshold = peak * 0.5
    else:
        threshold = floor + threshold_ratio * (peak - floor)
    return energy >= threshold


def voiced_ratio(
    audio: np.ndarray,
    sr: int,
    *,
    frame_ms: float = 25.0,
    hop_ms: float = 10.0,
    threshold_ratio: float = 0.25,
) -> float:
    if sr <= 0:
        raise ValueError("sr must be > 0")
    frame_size = max(1, int(round(sr * frame_ms / 1000.0)))
    hop = max(1, int(round(sr * hop_ms / 1000.0)))
    mask = simple_energy_vad(
        audio,
        frame_size=frame_size,
        hop=hop,
        threshold_ratio=threshold_ratio,
    )
    return float(np.mean(mask)) if mask.size else 0.0
