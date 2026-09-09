from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly


@dataclass(frozen=True)
class AudioInfo:
    path: str
    sample_rate: int
    frames: int
    channels: int
    duration: float


def probe_audio(path: str | Path) -> AudioInfo:
    """Read audio header metadata without loading the complete waveform."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        import soundfile as sf

        info = sf.info(path)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to inspect audio {path}. Install soundfile/libsndfile if needed."
        ) from exc
    return AudioInfo(
        path=str(path),
        sample_rate=int(info.samplerate),
        frames=int(info.frames),
        channels=int(info.channels),
        duration=float(info.duration),
    )


def load_audio(path: str | Path, target_sr: int | None = 16000) -> tuple[np.ndarray, int]:
    """Load audio as mono float32 and optionally resample.

    This function intentionally performs only minimal amplitude handling. Audio read by
    soundfile is normally already in [-1, 1]. If a file produces samples outside that
    range, the waveform is scaled only enough to avoid values with magnitude > 1.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        import soundfile as sf

        audio, sr = sf.read(path, always_2d=False)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load audio {path}. Install soundfile/libsndfile if needed."
        ) from exc

    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if audio.ndim != 1:
        raise ValueError(f"Expected mono/stereo waveform, got shape={audio.shape} for {path}")
    if audio.size == 0:
        raise ValueError(f"Audio file is empty: {path}")
    if not np.all(np.isfinite(audio)):
        raise ValueError(f"Audio contains NaN/Inf values: {path}")

    sr = int(sr)
    if sr <= 0:
        raise ValueError(f"Invalid sample rate {sr} for {path}")
    if target_sr is not None:
        if target_sr <= 0:
            raise ValueError("target_sr must be > 0 or None")
        if sr != target_sr:
            audio = resample_audio(audio, sr, target_sr)
            sr = int(target_sr)

    peak = float(np.max(np.abs(audio)))
    if peak > 1.0:
        audio = audio / peak
    return audio.astype(np.float32, copy=False), sr


def write_audio(path: str | Path, audio: np.ndarray, sr: int) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    waveform = np.asarray(audio, dtype=np.float32)
    if waveform.ndim != 1:
        raise ValueError("write_audio expects a mono 1-D waveform")
    if sr <= 0:
        raise ValueError("sr must be > 0")
    try:
        import soundfile as sf

        sf.write(path, waveform, sr)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to write audio {path}. Install soundfile/libsndfile if needed."
        ) from exc


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr <= 0 or target_sr <= 0:
        raise ValueError("orig_sr and target_sr must be > 0")
    waveform = np.asarray(audio, dtype=np.float32)
    if waveform.ndim != 1:
        raise ValueError("resample_audio expects a mono 1-D waveform")
    if orig_sr == target_sr:
        return waveform.copy()
    g = gcd(orig_sr, target_sr)
    return resample_poly(waveform, target_sr // g, orig_sr // g).astype(np.float32)
