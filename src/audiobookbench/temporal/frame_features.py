"""Day 5 frame-level signal features.

Feature definitions (engineering contract, frozen for Day 5):

- energy      : mean square power of the frame samples, ``mean(x^2)``.
- log_energy  : ``10 * log10(energy + 1e-12)`` in dB re full-scale 1.0.
- rms         : ``sqrt(energy)``.
- f0_hz       : F0 evaluated at the frame center.
                Primary backend: Praat autocorrelation via praat-parselmouth
                (time step 10 ms aligned to the grid hop, floor 75 Hz,
                ceiling 500 Hz). Deterministic NumPy autocorrelation is the
                documented fallback if the primary backend is unavailable.
- voiced_ratio: frame-level voicing indicator in {0.0, 1.0}; 1.0 when the F0
                value at the frame center is finite and within
                [f0_min, f0_max]. Sequence-level voiced ratio is the mean.
- pause_ratio : frame-level pause indicator in {0.0, 1.0}; 1.0 when
                ``20*log10(rms + 1e-12) < PAUSE_THRESHOLD_DB`` (fixed absolute
                threshold, deterministic and testable). Sequence-level pause
                ratio is the mean.
- speaker embedding: intentionally NOT extracted. No embedding backend is
                installed in this environment and no synthetic/fake embedding
                may ever be generated. Status is recorded as BLOCKED.
"""
from __future__ import annotations

import numpy as np

from audiobookbench.temporal.grid import TemporalGrid, framing_matrix

EPS = 1e-12
PAUSE_THRESHOLD_DB = -45.0
F0_MIN = 75.0
F0_MAX = 500.0
F0_TIME_STEP = 0.010

F0_BACKEND_PARSELMOUTH = "parselmouth_to_pitch_ac"
F0_BACKEND_AUTOCORRELATION = "numpy_autocorrelation_fallback"

EMBEDDING_STATUS = "BLOCKED"
EMBEDDING_REASON = (
    "No speaker embedding backend is installed in the Day 5 environment; "
    "per user decision no backend was installed tonight and no fake "
    "embedding was generated."
)


def frame_energies(waveform: np.ndarray, grid: TemporalGrid) -> dict[str, np.ndarray]:
    """Per-frame ``energy``, ``log_energy`` and ``rms`` over complete frames."""
    frames = framing_matrix(waveform, grid)
    if frames.shape[0] == 0:
        empty = np.empty(0, dtype=np.float64)
        return {"energy": empty.copy(), "log_energy": empty.copy(), "rms": empty.copy()}
    energy = np.mean(frames.astype(np.float64) ** 2, axis=1)
    log_energy = 10.0 * np.log10(energy + EPS)
    rms = np.sqrt(energy)
    return {"energy": energy, "log_energy": log_energy, "rms": rms}


def autocorrelation_f0(frame: np.ndarray, sample_rate: int, f0_min: float, f0_max: float) -> float:
    """Deterministic normalized-autocorrelation F0 for a single frame.

    Returns NaN when the frame is silent or has no reliable periodicity peak.
    """
    x = np.asarray(frame, dtype=np.float64)
    if x.size < 2:
        return float("nan")
    x = x - x.mean()
    energy = float(np.dot(x, x))
    if energy <= EPS:
        return float("nan")
    full = np.correlate(x, x, mode="full")
    ac = full[x.size - 1:] / energy
    lag_min = max(1, int(np.floor(sample_rate / f0_max)))
    lag_max = min(x.size - 1, int(np.ceil(sample_rate / f0_min)))
    if lag_max <= lag_min:
        return float("nan")
    segment = ac[lag_min:lag_max + 1]
    best = int(np.argmax(segment))
    peak = float(segment[best])
    if peak < 0.30:
        return float("nan")
    return float(sample_rate / (lag_min + best))


def extract_f0_parselmouth(
    waveform: np.ndarray,
    grid: TemporalGrid,
    num_samples: int,
    f0_min: float = F0_MIN,
    f0_max: float = F0_MAX,
    time_step: float = F0_TIME_STEP,
) -> np.ndarray:
    """F0 at every grid frame center using Praat autocorrelation pitch."""
    import parselmouth

    centers = grid.frame_centers(num_samples)
    if centers.size == 0:
        return np.empty(0, dtype=np.float64)
    sound = parselmouth.Sound(np.asarray(waveform, dtype=np.float64), sampling_frequency=grid.sample_rate)
    pitch = sound.to_pitch_ac(time_step=time_step, pitch_floor=f0_min, pitch_ceiling=f0_max)
    values = np.empty(centers.size, dtype=np.float64)
    for i, center in enumerate(centers):
        values[i] = pitch.get_value_at_time(center / grid.sample_rate)
    return values


def extract_f0(
    waveform: np.ndarray,
    grid: TemporalGrid,
    num_samples: int,
    f0_min: float = F0_MIN,
    f0_max: float = F0_MAX,
    primary_backend: str | None = F0_BACKEND_PARSELMOUTH,
) -> tuple[np.ndarray, str]:
    """F0 with explicit backend selection and documented deterministic fallback.

    Returns ``(f0_values, backend_name)``. The fallback never fabricates values:
    unvoiced/silent frames remain NaN.
    """
    if primary_backend == F0_BACKEND_PARSELMOUTH:
        try:
            return (
                extract_f0_parselmouth(waveform, grid, num_samples, f0_min=f0_min, f0_max=f0_max),
                F0_BACKEND_PARSELMOUTH,
            )
        except Exception:  # documented fallback path; never fake values
            pass
    frames = framing_matrix(waveform, grid)
    values = np.array(
        [
            autocorrelation_f0(frame, grid.sample_rate, f0_min, f0_max) for frame in frames
        ],
        dtype=np.float64,
    )
    return values, F0_BACKEND_AUTOCORRELATION


def voiced_indicator(f0_values: np.ndarray, f0_min: float = F0_MIN, f0_max: float = F0_MAX) -> np.ndarray:
    """Frame-level voicing indicator in {0.0, 1.0} from F0 values."""
    f0_values = np.asarray(f0_values, dtype=np.float64)
    return np.where(np.isfinite(f0_values) & (f0_values >= f0_min) & (f0_values <= f0_max), 1.0, 0.0)


def pause_indicator(rms_values: np.ndarray, threshold_db: float = PAUSE_THRESHOLD_DB) -> np.ndarray:
    """Frame-level pause indicator in {0.0, 1.0} from a fixed absolute dBFS threshold."""
    rms_values = np.asarray(rms_values, dtype=np.float64)
    rms_db = 20.0 * np.log10(rms_values + EPS)
    return np.where(rms_db < threshold_db, 1.0, 0.0)


def extract_frame_features(
    waveform: np.ndarray,
    grid: TemporalGrid,
    *,
    f0_backend: str | None = F0_BACKEND_PARSELMOUTH,
    f0_min: float = F0_MIN,
    f0_max: float = F0_MAX,
) -> dict[str, np.ndarray | str]:
    """Extract every Day 5 frame feature for one waveform.

    Returns a dict with ``energy``, ``log_energy``, ``rms``, ``f0_hz``,
    ``voiced_ratio``, ``pause_ratio`` arrays plus ``f0_backend`` (str).
    """
    waveform = np.asarray(waveform, dtype=np.float32)
    energies = frame_energies(waveform, grid)
    f0, backend_used = extract_f0(waveform, grid, waveform.size, f0_min=f0_min, f0_max=f0_max, primary_backend=f0_backend)
    return {
        "energy": energies["energy"],
        "log_energy": energies["log_energy"],
        "rms": energies["rms"],
        "f0_hz": f0,
        "voiced_ratio": voiced_indicator(f0, f0_min=f0_min, f0_max=f0_max),
        "pause_ratio": pause_indicator(energies["rms"]),
        "f0_backend": backend_used,
    }


def sequence_summary(features: dict[str, np.ndarray], grid: TemporalGrid) -> dict[str, float]:
    """Sequence-level aggregates; NaN-safe (voiced-only F0 statistics)."""
    f0 = np.asarray(features["f0_hz"], dtype=np.float64)
    voiced = f0[np.isfinite(f0)]
    return {
        "voiced_ratio": float(np.mean(features["voiced_ratio"])) if features["voiced_ratio"].size else float("nan"),
        "pause_ratio": float(np.mean(features["pause_ratio"])) if features["pause_ratio"].size else float("nan"),
        "f0_mean": float(np.mean(voiced)) if voiced.size else float("nan"),
        "f0_std": float(np.std(voiced)) if voiced.size else float("nan"),
        "energy_mean": float(np.mean(features["energy"])) if features["energy"].size else float("nan"),
        "rms_mean": float(np.mean(features["rms"])) if features["rms"].size else float("nan"),
        "frame_count": int(features["energy"].size),
    }
