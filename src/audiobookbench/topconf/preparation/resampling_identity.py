"""Explicit W7 resampling identity and synthetic-only validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

import numpy as np
import scipy
from scipy.signal import resample_poly

from .case_identity import sha256_canonical


RESAMPLING_IMPLEMENTATION = "scipy.signal.resample_poly"
RESAMPLING_IMPLEMENTATION_VERSION = "1.18.0"
RESAMPLING_TRANSFORM_ID = "topconf.w7.resampling.16k_8k_16k.scipy-resample-poly.v1"


class ResamplingIdentityError(ValueError):
    pass


@dataclass(frozen=True)
class ResamplingTransformIdentity:
    transform_name: str = "w7_resampling_16k_8k_16k"
    implementation: str = RESAMPLING_IMPLEMENTATION
    implementation_version: str = RESAMPLING_IMPLEMENTATION_VERSION
    input_sr: int = 16000
    intermediate_sr: int = 8000
    output_sr: int = 16000
    algorithm_backend: str = "polyphase_fir"
    anti_aliasing: bool = True
    filter_config: Mapping[str, Any] = None  # type: ignore[assignment]
    length_policy: str = "ceil(input_frames * output_sr / input_sr) per leg"
    rounding_behavior: str = "scipy_resample_poly_output_length"
    dtype_policy: str = "float32_after_each_leg"
    channel_policy: str = "mono_only"
    normalization_policy: str = "none_in_transform"

    def __post_init__(self) -> None:
        if self.filter_config is None:
            object.__setattr__(self, "filter_config", {"window": ["kaiser", 5.0], "padtype": "constant", "cval": 0.0})

    def as_dict(self) -> dict[str, Any]:
        return {
            "transform_id": RESAMPLING_TRANSFORM_ID,
            "transform_name": self.transform_name,
            "implementation": self.implementation,
            "implementation_version": self.implementation_version,
            "input_sr": self.input_sr,
            "intermediate_sr": self.intermediate_sr,
            "output_sr": self.output_sr,
            "algorithm_backend": self.algorithm_backend,
            "anti_aliasing": self.anti_aliasing,
            "filter_config": dict(self.filter_config),
            "length_policy": self.length_policy,
            "rounding_behavior": self.rounding_behavior,
            "dtype_policy": self.dtype_policy,
            "channel_policy": self.channel_policy,
            "normalization_policy": self.normalization_policy,
        }

    @property
    def config_hash(self) -> str:
        return sha256_canonical(self.as_dict())


def validate_runtime_identity(identity: ResamplingTransformIdentity) -> None:
    if scipy.__version__ != identity.implementation_version:
        raise ResamplingIdentityError(
            f"runtime scipy {scipy.__version__} does not match frozen {identity.implementation_version}"
        )
    if identity.implementation != RESAMPLING_IMPLEMENTATION or not identity.anti_aliasing:
        raise ResamplingIdentityError("unsupported resampling implementation or anti-aliasing policy")


def apply_declared_resampling(waveform: Sequence[float] | np.ndarray, identity: ResamplingTransformIdentity) -> np.ndarray:
    """Apply the declared transform to synthetic or future authorized audio only."""

    validate_runtime_identity(identity)
    values = np.asarray(waveform, dtype=np.float32)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ResamplingIdentityError("waveform must be a finite non-empty mono vector")
    window = ("kaiser", float(identity.filter_config["window"][1]))
    values = resample_poly(values, identity.intermediate_sr // math.gcd(identity.input_sr, identity.intermediate_sr), identity.input_sr // math.gcd(identity.input_sr, identity.intermediate_sr), window=window, padtype="constant", cval=0.0).astype(np.float32)
    values = resample_poly(values, identity.output_sr // math.gcd(identity.intermediate_sr, identity.output_sr), identity.intermediate_sr // math.gcd(identity.intermediate_sr, identity.output_sr), window=window, padtype="constant", cval=0.0).astype(np.float32)
    return values


def validate_synthetic_transform(waveform: Sequence[float] | np.ndarray, identity: ResamplingTransformIdentity) -> dict[str, Any]:
    first = apply_declared_resampling(waveform, identity)
    second = apply_declared_resampling(waveform, identity)
    input_count = int(np.asarray(waveform).size)
    expected_output = math.ceil(input_count * identity.output_sr / identity.input_sr)
    return {
        "deterministic_array": bool(np.array_equal(first, second)),
        "finite_output": bool(np.isfinite(first).all()),
        "expected_output_frames": expected_output,
        "actual_output_frames": int(first.size),
        "duration_error_sec": abs(first.size / identity.output_sr - input_count / identity.input_sr),
        "transform_id": RESAMPLING_TRANSFORM_ID,
        "transform_config_hash": identity.config_hash,
    }
