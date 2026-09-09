from __future__ import annotations

import numpy as np


def energy_features(audio: np.ndarray) -> dict[str, float]:
    if audio.size == 0:
        return {"energy_mean": float("nan"), "energy_std": float("nan")}
    frame = 400
    hop = 160
    if audio.size < frame:
        e = np.array([np.mean(audio ** 2)])
    else:
        frames = np.lib.stride_tricks.sliding_window_view(audio, frame)[::hop]
        e = np.mean(frames ** 2, axis=1)
    return {"energy_mean": float(np.mean(e)), "energy_std": float(np.std(e))}


def zero_crossing_rate(audio: np.ndarray) -> float:
    if audio.size < 2:
        return float("nan")
    return float(np.mean(np.abs(np.diff(np.signbit(audio))).astype(float)))


def basic_prosody_features(audio: np.ndarray, sr: int) -> dict[str, float]:
    """Lightweight prosody-like sanity features.

    This is not a substitute for a validated F0 extractor. Add a real F0 backend before formal claims.
    """
    duration = float(len(audio) / sr) if sr else float("nan")
    out = energy_features(audio)
    out.update({
        "duration": duration,
        "zcr": zero_crossing_rate(audio),
        "voiced_ratio": float("nan"),
        "f0_mean": float("nan"),
        "f0_std": float("nan"),
        "pitch_range": float("nan"),
        "speech_rate": float("nan"),
        "pause_ratio": float("nan"),
    })
    return out
