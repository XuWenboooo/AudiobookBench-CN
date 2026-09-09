"""Day 6A temporal aggregation layer over the frozen Day 5 measurement grid.

Day 5 grid (25 ms frame / 10 ms hop @ 16 kHz) is never modified. This module
groups complete, contiguous Day 5 frames into larger windows (100/250/500 ms,
frozen in ``configs/day6a_localization_baseline.yaml``) and computes a small
interpretable feature vector per window from the Day 5 scalar signals only:

- log_energy: mean / std / min / max
- rms: mean / std
- f0: nanmedian / nanstd over voiced frames (NaN = unvoiced stays NaN;
      zero is never treated as pitch) + finite fraction
- voiced_ratio -> voiced_fraction (mean)
- pause_ratio  -> pause_fraction (mean)

Every window records its frame-index range, sample interval and times so that
ground truth can be projected losslessly. The same aggregation grid is shared
by clean/A0/A1 of a paired case.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import numpy as np

SIGNALS = ("energy", "log_energy", "rms", "f0_hz", "voiced_ratio", "pause_ratio")


@dataclass(frozen=True)
class AggregationScale:
    """One frozen aggregation scale; windows are aligned to Day 5 frames."""

    name: str
    window_frames: int
    hop_frames: int
    hop_length: int  # Day 5 hop in samples (160)

    def __post_init__(self) -> None:
        if self.window_frames <= 0 or self.hop_frames <= 0:
            raise ValueError("window_frames and hop_frames must be positive")
        if self.hop_frames > self.window_frames:
            raise ValueError("hop_frames must not exceed window_frames")

    @classmethod
    def from_config(cls, entry: Mapping[str, Any], hop_length: int) -> "AggregationScale":
        window_ms = int(entry["window_ms"])
        hop_ms = int(entry["hop_ms"])
        if window_ms % 10 != 0 or hop_ms % 10 != 0:
            raise ValueError("aggregation windows must be multiples of the 10 ms Day 5 hop")
        return cls(
            name=str(entry["name"]),
            window_frames=window_ms // 10,
            hop_frames=hop_ms // 10,
            hop_length=hop_length,
        )

    def window_count(self, frame_count: int) -> int:
        if frame_count < 0:
            raise ValueError("frame_count must be non-negative")
        if frame_count < self.window_frames:
            return 0
        return 1 + (frame_count - self.window_frames) // self.hop_frames


@dataclass(frozen=True)
class AggregationWindow:
    """One aggregation window with full provenance back to Day 5 frames."""

    scale_name: str
    window_index: int
    frame_start_index: int
    frame_end_index: int  # exclusive
    sample_start: int
    sample_end: int
    t_start: float
    t_center: float
    t_end: float

    def as_row(self, base: Mapping[str, Any]) -> dict[str, Any]:
        row = dict(base)
        row.update(
            {
                "scale": self.scale_name,
                "window_index": self.window_index,
                "frame_start_index": self.frame_start_index,
                "frame_end_index_exclusive": self.frame_end_index,
                "covered_frame_indices": f"{self.frame_start_index}-{self.frame_end_index - 1}",
                "sample_start": self.sample_start,
                "sample_end": self.sample_end,
                "t_start": f"{self.t_start:.6f}",
                "t_center": f"{self.t_center:.6f}",
                "t_end": f"{self.t_end:.6f}",
            }
        )
        return row


def build_aggregation_grid(
    frame_count: int,
    scale: AggregationScale,
    grid: Any,  # TemporalGrid, typed loosely to avoid a circular import
) -> list[AggregationWindow]:
    """Contiguous windows over complete Day 5 frames; deterministic."""
    windows: list[AggregationWindow] = []
    count = scale.window_count(frame_count)
    for index in range(count):
        f_start = index * scale.hop_frames
        f_end = f_start + scale.window_frames
        sample_start, _ = grid.frame_bounds(f_start)
        _, sample_end = grid.frame_bounds(f_end - 1)
        t_start = sample_start / grid.sample_rate
        t_end = sample_end / grid.sample_rate
        center_sample = (sample_start + sample_end) // 2
        windows.append(
            AggregationWindow(
                scale_name=scale.name,
                window_index=index,
                frame_start_index=f_start,
                frame_end_index=f_end,
                sample_start=sample_start,
                sample_end=sample_end,
                t_start=t_start,
                t_center=center_sample / grid.sample_rate,
                t_end=t_end,
            )
        )
    return windows


def _finite(values: np.ndarray) -> np.ndarray:
    return values[np.isfinite(values)]


def aggregate_window_features(
    frames: Mapping[str, np.ndarray],
    window: AggregationWindow,
    feature_defs: Mapping[str, Mapping[str, str]],
) -> dict[str, float]:
    """Compute the frozen window features from Day 5 frame arrays.

    ``frames`` maps signal name -> 1-D array over all frames of one record.
    F0 semantics: NaN frames are unvoiced; median/std use voiced frames only;
    a window with zero voiced frames yields NaN f0_median/f0_std (never 0).
    """
    lo, hi = window.frame_start_index, window.frame_end_index
    out: dict[str, float] = {}
    for name, spec in feature_defs.items():
        signal = str(spec["signal"])
        stat = str(spec["stat"])
        values = np.asarray(frames[signal][lo:hi], dtype=np.float64)
        if values.size == 0:
            out[name] = float("nan")
            continue
        if stat == "finite_fraction":
            out[name] = float(np.mean(np.isfinite(values)))
            continue
        if signal == "f0_hz":
            voiced = _finite(values)
            if voiced.size == 0:
                out[name] = float("nan")
                continue
            values = voiced
        if stat == "mean":
            out[name] = float(np.mean(values))
        elif stat == "std":
            out[name] = float(np.std(values))
        elif stat == "median":
            out[name] = float(np.median(values))
        elif stat == "nanmedian":
            out[name] = float(np.nanmedian(values))
        elif stat == "nanstd":
            out[name] = float(np.nanstd(values))
        elif stat == "min":
            out[name] = float(np.min(values))
        elif stat == "max":
            out[name] = float(np.max(values))
        else:
            raise ValueError(f"unsupported window stat: {stat}")
    return out


def project_ground_truth(
    windows: Iterable[AggregationWindow],
    intervals: Mapping[str, tuple[int, int]],
    label_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    """Project sample-level GT intervals onto windows.

    For each window: overlap ratio with target/attack/core/blend plus boolean
    labels under the frozen majority rule and a three-way zone assignment.
    """
    from audiobookbench.temporal.grid import overlap_fraction

    rows: list[dict[str, Any]] = []
    for window in windows:
        row: dict[str, Any] = {"window_index": window.window_index}
        span = window.sample_end - window.sample_start
        overlaps = {
            name: (max(0, min(window.sample_end, hi) - max(window.sample_start, lo)) / span)
            for name, (lo, hi) in intervals.items()
        }
        for name, ratio in overlaps.items():
            row[f"{name}_overlap_ratio"] = f"{ratio:.6f}"
        row["is_attack_window"] = overlaps["attack"] >= label_threshold
        row["is_core_window"] = overlaps["core"] >= label_threshold
        row["is_blend_window"] = overlaps["blend"] >= label_threshold
        in_core = overlaps["core"] >= label_threshold
        if in_core:
            zone = "core"
        elif overlaps["attack"] > 0 or overlaps["blend"] > 0:
            zone = "boundary"
        else:
            zone = "outside"
        row["zone"] = zone
        rows.append(row)
    return rows
