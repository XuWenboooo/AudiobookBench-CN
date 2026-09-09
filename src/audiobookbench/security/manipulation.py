from __future__ import annotations

from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class ManipulationRecord:
    attack_start: float
    attack_end: float
    attack_type: str
    source_id: str | None = None
    replacement_id: str | None = None


def replace_segment(source_audio: np.ndarray, replacement_audio: np.ndarray, sr: int, start_sec: float, end_sec: float) -> tuple[np.ndarray, ManipulationRecord]:
    """Replace [start_sec, end_sec) in source_audio with replacement audio trimmed/padded to same length."""
    if start_sec < 0 or end_sec <= start_sec:
        raise ValueError("Invalid attack interval")
    start = int(round(start_sec * sr))
    end = int(round(end_sec * sr))
    if end > len(source_audio):
        raise ValueError("Attack interval exceeds source audio length")
    target_len = end - start
    repl = np.asarray(replacement_audio, dtype=source_audio.dtype)
    if len(repl) < target_len:
        repl = np.pad(repl, (0, target_len - len(repl)))
    repl = repl[:target_len]
    out = np.array(source_audio, copy=True)
    out[start:end] = repl
    return out, ManipulationRecord(start_sec, end_sec, "segment_replacement")


def segment_labels(segment_starts: np.ndarray, segment_ends: np.ndarray, attack_start: float, attack_end: float) -> np.ndarray:
    starts = np.asarray(segment_starts, dtype=float)
    ends = np.asarray(segment_ends, dtype=float)
    return ((starts < attack_end) & (ends > attack_start)).astype(int)
