"""Day 5 unified temporal grid.

Single shared frame parameterization for all 70 Day 4.5 long-form sequences
(24 clean + 23 A0 + 23 A1):

- frame_length = 400 samples (25 ms at 16 kHz)
- hop_length   = 160 samples (10 ms at 16 kHz)
- complete frames only; trailing samples that do not fill a full frame are
  not covered by any frame

All frame boundaries are defined in integer samples at 16 kHz. Seconds are
always derived as ``sample_index / sample_rate`` and never stored independently.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

import numpy as np

FRAME_LENGTH = 400
HOP_LENGTH = 160
SAMPLE_RATE = 16000


@dataclass(frozen=True)
class TemporalGrid:
    """Immutable frame grid shared by every Day 5 record."""

    frame_length: int = FRAME_LENGTH
    hop_length: int = HOP_LENGTH
    sample_rate: int = SAMPLE_RATE

    def __post_init__(self) -> None:
        if self.frame_length <= 0 or self.hop_length <= 0:
            raise ValueError("frame_length and hop_length must be positive")
        if self.hop_length > self.frame_length:
            raise ValueError("hop_length must not exceed frame_length")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

    def frame_count(self, num_samples: int) -> int:
        """Number of complete frames for a waveform of ``num_samples``."""
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative")
        if num_samples < self.frame_length:
            return 0
        return 1 + (num_samples - self.frame_length) // self.hop_length

    def frame_bounds(self, frame_index: int) -> tuple[int, int]:
        """Integer sample bounds ``[start, end)`` of ``frame_index``."""
        if frame_index < 0:
            raise ValueError("frame_index must be non-negative")
        start = frame_index * self.hop_length
        return start, start + self.frame_length

    def frame_center_sample(self, frame_index: int) -> int:
        start, end = self.frame_bounds(frame_index)
        return (start + end) // 2

    def frame_times(self, frame_index: int) -> tuple[float, float, float]:
        """``(t_start, t_center, t_end)`` in seconds for ``frame_index``."""
        start, end = self.frame_bounds(frame_index)
        center = self.frame_center_sample(frame_index)
        return (
            start / self.sample_rate,
            center / self.sample_rate,
            end / self.sample_rate,
        )

    def frame_centers(self, num_samples: int) -> np.ndarray:
        """Center sample indices of every frame of a ``num_samples`` waveform."""
        count = self.frame_count(num_samples)
        if count == 0:
            return np.empty(0, dtype=np.int64)
        return np.array([self.frame_center_sample(i) for i in range(count)], dtype=np.int64)

    def frame_index_at_sample(self, sample: int) -> int:
        """Index of the frame whose center is nearest to ``sample``."""
        if sample < 0:
            raise ValueError("sample must be non-negative")
        raw = (sample - self.frame_length / 2) / self.hop_length
        return max(0, int(round(raw)))

    def iter_frames(self, num_samples: int) -> Iterator[tuple[int, int, int, float, float, float]]:
        """Yield ``(frame_index, start, end, t_start, t_center, t_end)``."""
        for index in range(self.frame_count(num_samples)):
            start, end = self.frame_bounds(index)
            t_start, t_center, t_end = self.frame_times(index)
            yield index, start, end, t_start, t_center, t_end


def framing_matrix(waveform: np.ndarray, grid: TemporalGrid) -> np.ndarray:
    """Return a read-only 2-D view of complete frames, shape ``(frame_count, frame_length)``."""
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim != 1:
        raise ValueError("waveform must be 1-D")
    count = grid.frame_count(waveform.size)
    if count == 0:
        return np.empty((0, grid.frame_length), dtype=np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(waveform, grid.frame_length)[:: grid.hop_length]
    if frames.shape[0] != count:
        raise AssertionError(
            f"framing mismatch: computed {frames.shape[0]} frames, grid expects {count}"
        )
    return frames


def frame_record(
    grid: TemporalGrid,
    frame_index: int,
    base: dict[str, Any],
) -> dict[str, Any]:
    """One row of frame metadata: identity + timestamps for a single frame."""
    start, end = grid.frame_bounds(frame_index)
    t_start, t_center, t_end = grid.frame_times(frame_index)
    row = dict(base)
    row.update(
        {
            "frame_index": frame_index,
            "frame_start_sample": start,
            "frame_end_sample": end,
            "frame_center_sample": grid.frame_center_sample(frame_index),
            "t_start": f"{t_start:.6f}",
            "t_center": f"{t_center:.6f}",
            "t_end": f"{t_end:.6f}",
        }
    )
    return row


def overlap_fraction(
    frame_start: int,
    frame_end: int,
    seg_start: int,
    seg_end: int,
) -> float:
    """Fraction of the frame covered by ``[seg_start, seg_end)``; 0.0 when disjoint."""
    if seg_end <= seg_start:
        raise ValueError("segment must be non-empty (seg_end > seg_start)")
    if frame_end <= frame_start:
        raise ValueError("frame must be non-empty (frame_end > frame_start)")
    lo = max(frame_start, seg_start)
    hi = min(frame_end, seg_end)
    if hi <= lo:
        return 0.0
    return (hi - lo) / (frame_end - frame_start)
