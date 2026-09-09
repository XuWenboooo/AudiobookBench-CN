"""Day 5 debug trajectory figures for paired cases.

Each figure shows, for one paired case (clean vs A0 vs A1):

1. frame energy trajectory in dB;
2. F0 trajectory (NaN = unvoiced, gaps are expected and honest);
3. ground-truth interval bands (target / attack / core / blend) on the time axis
   over the frame energy;
4. frame-level absolute energy difference against clean.

Figures are engineering debug artifacts only; they encode no performance claim.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from audiobookbench.temporal.grid import TemporalGrid

COLORS = {"clean": "#2b6cb0", "a0": "#c05621", "a1": "#2f855a"}
GT_BANDS = [
    ("target", "#4299e1", 0.25),
    ("attack", "#ed8936", 0.25),
    ("core", "#e53e3e", 0.35),
    ("blend", "#38a169", 0.18),
]


def _times(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.array([float(row["t_center"]) for row in rows], dtype=np.float64)


def plot_pair_trajectories(
    grid: TemporalGrid,
    clean_rows: list[dict[str, Any]],
    a0_rows: list[dict[str, Any]],
    a1_rows: list[dict[str, Any]],
    gt: Mapping[str, tuple[float, float]],
    case_id: str,
    split: str,
    out_path: str | Path,
) -> Path:
    """Render one paired-case debug figure and return the written path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    t_clean = _times(clean_rows)
    t_a0 = _times(a0_rows)
    t_a1 = _times(a1_rows)
    energy_clean = np.array([float(row["log_energy"]) for row in clean_rows])
    energy_a0 = np.array([float(row["log_energy"]) for row in a0_rows])
    energy_a1 = np.array([float(row["log_energy"]) for row in a1_rows])
    f0_clean = np.array([float(row["f0_hz"]) for row in clean_rows])
    f0_a0 = np.array([float(row["f0_hz"]) for row in a0_rows])
    f0_a1 = np.array([float(row["f0_hz"]) for row in a1_rows])

    fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)
    fig.suptitle(f"Day5 debug pair {case_id} (split={split})", fontsize=13)

    ax = axes[0]
    ax.plot(t_clean, energy_clean, label="clean", color=COLORS["clean"], lw=0.9)
    ax.plot(t_a0, energy_a0, label="A0", color=COLORS["a0"], lw=0.9, alpha=0.85)
    ax.plot(t_a1, energy_a1, label="A1", color=COLORS["a1"], lw=0.9, alpha=0.85)
    ax.set_ylabel("frame energy (dB)")
    ax.set_title("Frame energy trajectory")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[1]
    for times, values, label, color in (
        (t_clean, f0_clean, "clean", COLORS["clean"]),
        (t_a0, f0_a0, "A0", COLORS["a0"]),
        (t_a1, f0_a1, "A1", COLORS["a1"]),
    ):
        voiced = np.isfinite(values)
        times_v, values_v = times[voiced], values[voiced]
        ax.plot(times_v, values_v, ".", ms=2.5, label=label, color=color, alpha=0.8)
    ax.set_ylabel("F0 (Hz)")
    ax.set_title("F0 trajectory (gaps = unvoiced frames, not missing data)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(t_clean, energy_clean, color="#a0aec0", lw=0.7, label="clean energy (context)")
    for name, color, alpha in GT_BANDS:
        if name in gt:
            lo, hi = gt[name]
            ax.axvspan(lo, hi, color=color, alpha=alpha, label=name)
    ax.set_ylabel("frame energy (dB)")
    ax.set_title("Ground truth: target / attack / core / blend intervals")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[3]
    min_len = min(t_a0.size, t_clean.size)
    diff_a0 = np.abs(energy_a0[:min_len] - energy_clean[:min_len])
    min_len1 = min(t_a1.size, t_clean.size)
    diff_a1 = np.abs(energy_a1[:min_len1] - energy_clean[:min_len1])
    ax.plot(t_a0[:min_len], diff_a0, label="|A0 - clean|", color=COLORS["a0"], lw=0.8)
    ax.plot(t_a1[:min_len1], diff_a1, label="|A1 - clean|", color=COLORS["a1"], lw=0.8)
    for name in ("attack", "core", "blend"):
        if name in gt:
            lo, hi = gt[name]
            ax.axvspan(lo, hi, color="#805ad5", alpha=0.12)
    ax.set_ylabel("|energy diff| (dB)")
    ax.set_xlabel("time (s)")
    ax.set_title("Frame-level energy deviation from clean (violet band = ground truth)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
