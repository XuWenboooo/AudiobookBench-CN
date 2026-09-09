"""Day 6B speaker-consistency baselines (B1a/B1b/B2/B3) and B4 diagnostic.

All baselines are non-trained. B1 uses only the suspect sequence's own
embeddings; B2 uses adjacent-window differences; B3 uses the paired clean
original and is therefore marked ORACLE (not deployable); B4 is a
waveform-energy transient diagnostic marked DIAGNOSTIC.

No speaker-ID information is ever an input feature: prototypes and scores
are computed from embeddings only. Attack ground truth is never read by any
prototype or scoring function.
"""
from __future__ import annotations

from typing import Any

import numpy as np

TRIM_RATIO = 0.20  # frozen in configs/day6b_speaker_consistency.yaml


def normalize_rows(embeddings: np.ndarray) -> np.ndarray:
    """L2-normalize each embedding; zero vectors stay zero (never NaN)."""
    e = np.asarray(embeddings, dtype=np.float64)
    norms = np.linalg.norm(e, axis=1, keepdims=True)
    return e / np.maximum(norms, 1e-12)


def cosine_to(embeddings: np.ndarray, prototype: np.ndarray) -> np.ndarray:
    """Cosine similarity of each (normalized) embedding to the prototype."""
    e = normalize_rows(embeddings)
    p = prototype / (np.linalg.norm(prototype) + 1e-12)
    return e @ p


def untrimmed_prototype(embeddings: np.ndarray) -> np.ndarray:
    """B1a: normalized centroid over all windows (no GT access)."""
    v = normalize_rows(embeddings).mean(axis=0)
    return v / (np.linalg.norm(v) + 1e-12)


def robust_prototype(embeddings: np.ndarray, trim_ratio: float = TRIM_RATIO) -> np.ndarray:
    """B1b: trimmed normalized centroid (frozen rule, no GT access).

    Step 1 centroid; step 2 cosine distance to it; step 3 drop the top
    ``trim_ratio`` most distant windows; step 4 recompute the centroid.
    """
    e = normalize_rows(embeddings)
    v1 = e.mean(axis=0)
    v1 = v1 / (np.linalg.norm(v1) + 1e-12)
    distances = 1.0 - e @ v1
    n_trim = int(np.floor(len(e) * trim_ratio))
    if n_trim >= len(e):
        raise ValueError("trim_ratio removes every window")
    if n_trim == 0:
        return untrimmed_prototype(embeddings)
    keep = np.argsort(distances, kind="stable")[: len(e) - n_trim]
    v2 = e[keep].mean(axis=0)
    return v2 / (np.linalg.norm(v2) + 1e-12)


def b1_scores(embeddings: np.ndarray, trimmed: bool) -> np.ndarray:
    """A_spk(t) = 1 - cos(emb(t), prototype); sequence-local, no GT access."""
    proto = robust_prototype(embeddings) if trimmed else untrimmed_prototype(embeddings)
    return 1.0 - cosine_to(embeddings, proto)


def b2_scores(embeddings: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """B2 neighbor speaker-change scores.

    adjacent: ``1 - cos(emb(t), emb(t+1))`` assigned to window t (NaN last).
    symmetric: ``1 - cos(emb(t-1), emb(t+1))`` assigned to window t (NaN at
    both ends). Both are local change-point signals, no GT access.
    """
    e = normalize_rows(embeddings)
    n = len(e)
    adjacent = np.full(n, np.nan)
    if n >= 2:
        adjacent[:-1] = 1.0 - np.sum(e[:-1] * e[1:], axis=1)
    symmetric = np.full(n, np.nan)
    if n >= 3:
        symmetric[1:-1] = 1.0 - np.sum(e[:-2] * e[2:], axis=1)
    return adjacent, symmetric


def b3_scores(emb_manip: np.ndarray, emb_clean: np.ndarray) -> np.ndarray:
    """ORACLE paired-clean differential: 1 - cos at identical grid positions.

    Requires the paired clean original; never deployable in the stated
    forensic setting.
    """
    if emb_manip.shape != emb_clean.shape:
        raise ValueError("paired embeddings must share the grid")
    e1 = normalize_rows(emb_manip)
    e2 = normalize_rows(emb_clean)
    return 1.0 - np.sum(e1 * e2, axis=1)


def b4_scores(day5_log_energy: np.ndarray, window_frame_spans: list[tuple[int, int]]) -> np.ndarray:
    """DIAGNOSTIC boundary transient: max adjacent-frame energy step per window.

    ``window_frame_spans`` maps each speaker window to the inclusive range of
    Day 5 frame indices it covers. Pure waveform diagnostic; no GT access.
    """
    diff = np.abs(np.diff(np.asarray(day5_log_energy, dtype=np.float64)))
    out = np.empty(len(window_frame_spans), dtype=np.float64)
    for i, (lo, hi) in enumerate(window_frame_spans):
        # frames lo..hi; adjacent steps inside the window are diffs at lo..hi-1
        segment = diff[lo:hi]
        out[i] = float(np.max(segment)) if segment.size else 0.0
    return out


def project_ground_truth_speaker(
    windows: list[dict[str, Any]],
    intervals: dict[str, tuple[int, int]],
    label_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    """Recompute overlap ratios on the speaker grid from true sample bounds."""
    rows = []
    for w in windows:
        span = w["sample_end"] - w["sample_start"]
        row: dict[str, Any] = {"window_index": w["window_index"]}
        for name, (lo, hi) in intervals.items():
            overlap = max(0, min(w["sample_end"], hi) - max(w["sample_start"], lo)) / span
            row[f"{name}_overlap_ratio"] = float(overlap)
        row["is_attack_window"] = row["attack_overlap_ratio"] >= label_threshold
        row["is_core_window"] = row["core_overlap_ratio"] >= label_threshold
        row["is_blend_window"] = row["blend_overlap_ratio"] >= label_threshold
        if row["is_core_window"]:
            row["zone"] = "core"
        elif row["attack_overlap_ratio"] > 0 or row["blend_overlap_ratio"] > 0:
            row["zone"] = "boundary"
        else:
            row["zone"] = "outside"
        rows.append(row)
    return rows
