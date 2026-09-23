"""Synthetic fixture adapters around the frozen W7 M2/M4 waveform functions."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from typing import Any, Mapping, Sequence

import numpy as np

from .w7_candidate_transforms import (
    CROSSFADE_SAMPLES,
    SAMPLE_RATE_HZ,
    VERSION,
    cross_speaker_boundary,
    same_speaker_splice_crossfade,
)
from .w7_synthetic_harness import HarnessError, Interval, StageContract, validate_intervals


M2_FAMILY = "cross_speaker_boundary_control"
M4_FAMILY = "same_speaker_splice_crossfade_control"
SYNTHETIC_ASSET_IDENTITY = "synthetic-fixture-waveforms-v1"
RESAMPLER_IDENTITY = "numpy.interp_endpoint_aligned_v1"


def current_runtime_identity() -> str:
    return json.dumps({
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "torch": "NOT_USED",
        "torchaudio": "NOT_USED",
        "resampler": RESAMPLER_IDENTITY,
        "os": platform.platform(),
    }, sort_keys=True, separators=(",", ":"))


def normalize_audio(waveform: np.ndarray, sample_rate: int) -> np.ndarray:
    """Normalize channel-last synthetic audio to finite clipped mono float32/16 kHz."""
    values = np.asarray(waveform)
    if values.ndim == 2:
        values = values.mean(axis=1, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or sample_rate <= 0:
        raise HarnessError("TRANSFORM_FAILURE", "invalid synthetic waveform/sample rate")
    values = values.astype(np.float64, copy=False)
    if not np.isfinite(values).all():
        raise HarnessError("TRANSFORM_FAILURE", "non-finite synthetic waveform")
    values = np.clip(values, -1.0, 1.0)
    count = int(np.floor(len(values) * SAMPLE_RATE_HZ / sample_rate + 0.5))
    if count <= 0:
        raise HarnessError("TRANSFORM_FAILURE", "resampling produced no samples")
    if sample_rate != SAMPLE_RATE_HZ:
        values = np.interp(np.linspace(0.0, 1.0, count, dtype=np.float64),
                           np.linspace(0.0, 1.0, len(values), dtype=np.float64), values)
    return np.clip(values, -1.0, 1.0).astype(np.float32)


def _sample_map(intervals: tuple[Interval, ...], sample_rate: int, sample_count: int) -> tuple[Interval, ...]:
    mapped = tuple(Interval(
        int(np.floor(item.start * SAMPLE_RATE_HZ / sample_rate + 0.5)),
        int(np.floor(item.end * SAMPLE_RATE_HZ / sample_rate + 0.5)),
        item.ordinal, item.mask_group,
    ) for item in intervals)
    return validate_intervals(mapped, sample_count)


def _audio_hash(waveform: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(waveform, dtype=np.float32).tobytes()).hexdigest()


def _is_synthetic(value: Any, prefix: str) -> bool:
    return isinstance(value, str) and value.startswith(prefix) and len(value) > len(prefix)


def _get_waveform(case: Mapping[str, Any]) -> np.ndarray:
    waveform = case.get("waveform")
    if not isinstance(waveform, np.ndarray) or waveform.ndim not in (1, 2) or waveform.size == 0:
        raise HarnessError("INPUT_NOT_SYNTHETIC", "adapter requires an in-memory synthetic waveform")
    if int(case.get("sample_count", -1)) != waveform.shape[0]:
        raise HarnessError("INPUT_NOT_SYNTHETIC", "synthetic waveform length does not match fixture")
    return waveform


class _AdapterBase:
    family: str
    implementation: str

    def __init__(self, case: Mapping[str, Any], *, config_hash: str) -> None:
        self.case = dict(case)
        self.config_hash = config_hash
        self.runtime_identity = current_runtime_identity()
        self.asset_identity = SYNTHETIC_ASSET_IDENTITY
        self.failure_code: str | None = None
        self._normalized_source: np.ndarray | None = None
        self._mapped_intervals: tuple[Interval, ...] = ()
        self._details: dict[str, Any] = {}

    def validate_runtime(self, identity: str | None = None) -> bool:
        return identity is None or identity == self.runtime_identity

    def validate_assets(self, identity: str | None = None) -> bool:
        return (
            (identity is None or identity == self.asset_identity)
            and self.case.get("data_origin") == "synthetic"
            and _is_synthetic(self.case.get("case_id"), "SYNTH_")
            and _is_synthetic(self.case.get("source_id"), "SYNTH_SOURCE_")
            and _get_waveform(self.case).shape[0] == int(self.case["sample_count"])
        )

    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]:
        if contract.mechanism_family != self.family or contract.case_id != self.case.get("case_id"):
            self.failure_code = "INPUT_NOT_SYNTHETIC"
            raise HarnessError(self.failure_code, "adapter case binding mismatch")
        if not self.validate_runtime(contract.runtime_identity) or not self.validate_assets(contract.asset_identity):
            self.failure_code = "CONFIG_NOT_APPROVED"
            raise HarnessError(self.failure_code, "runtime/fixture identity validation failed")
        sample_rate = int(self.case.get("sample_rate", SAMPLE_RATE_HZ))
        if sample_rate <= 0:
            self.failure_code = "TRANSFORM_FAILURE"
            raise HarnessError(self.failure_code, "invalid sample rate")
        source = normalize_audio(_get_waveform(self.case), sample_rate)
        self._normalized_source = source
        self._mapped_intervals = _sample_map(contract.intervals, sample_rate, len(source))
        self._details = {
            "source_audio_hash": _audio_hash(source),
            "target_intervals": [{
                "ordinal": item.ordinal, "input_start": item.start, "input_end": item.end,
                "output_start": item.start, "output_end": item.end,
                "composition_order": item.ordinal,
            } for item in self._mapped_intervals],
        }
        return {
            "case_id": contract.case_id,
            "family": self.family,
            "mapped_intervals": [
                {"ordinal": item.ordinal, "mask_group": item.mask_group,
                 "input_start": item.start, "input_end": item.end,
                 "output_start": item.start, "output_end": item.end,
                 "composition_order": item.ordinal}
                for item in self._mapped_intervals
            ],
        }

    def validate_output(self, source: np.ndarray, output: np.ndarray, intervals: tuple[Interval, ...]) -> bool:
        if self._normalized_source is None:
            return False
        if output.dtype != np.float32 or output.ndim != 1 or len(output) != len(self._normalized_source):
            return False
        if not np.isfinite(output).all() or np.any(output < -1.0) or np.any(output > 1.0):
            return False
        edited = np.zeros(len(output), dtype=bool)
        for item in self._mapped_intervals:
            fade = min(CROSSFADE_SAMPLES, (item.end - item.start) // 2, item.start,
                       len(output) - item.end)
            edited[item.start - fade:item.end] = True
        return bool(np.array_equal(self._normalized_source[~edited], output[~edited]))

    def _base_provenance(self, contract: StageContract, output_hash: str) -> dict[str, Any]:
        return {
            "case_id": contract.case_id,
            "mechanism_family": self.family,
            "implementation_identity": self.implementation,
            "version": VERSION,
            "config_hash": self.config_hash,
            "source_audio_hash": self._details.get("source_audio_hash"),
            "reference_audio_hash": self._details.get("reference_audio_hash"),
            "source_id": self.case.get("source_id"),
            "reference_source_id": self._details.get("reference_source_id"),
            "target_intervals": self._details.get("target_intervals", []),
            "crossfade_samples": CROSSFADE_SAMPLES,
            "interpolation": "linear",
            "output_hash": output_hash,
            "failure_code": self.failure_code,
            "runtime_identity": self.runtime_identity,
            "asset_identity": self.asset_identity,
            "input_sample_rate_hz": int(self.case.get("sample_rate", SAMPLE_RATE_HZ)),
            "output_sample_rate_hz": SAMPLE_RATE_HZ,
            "resampler": RESAMPLER_IDENTITY,
        }


class M2RealAdapter(_AdapterBase):
    """Reference selection plus the frozen cross_speaker_boundary function."""
    family = "cross_speaker_boundary_control"
    implementation = "audiobookbench.topconf.w7_candidate_transforms::cross_speaker_boundary"

    def __init__(self, case: Mapping[str, Any], reference_pool: Sequence[Mapping[str, Any]], *, config_hash: str) -> None:
        super().__init__(case, config_hash=config_hash)
        self.reference_pool = tuple(dict(item) for item in reference_pool)
        self.reference: Mapping[str, Any] | None = None
        self.reference_rank: int | None = None
        self._reference_wave: np.ndarray | None = None
        self._candidate_order: list[str] = []

    def validate_assets(self, identity: str | None = None) -> bool:
        if not super().validate_assets(identity):
            return False
        return all(
            item.get("data_origin") == "synthetic"
            and _is_synthetic(item.get("case_id"), "SYNTH_")
            and _is_synthetic(item.get("source_id"), "SYNTH_SOURCE_")
            and isinstance(item.get("waveform"), np.ndarray)
            and item["waveform"].ndim in (1, 2)
            for item in self.reference_pool
        )

    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]:
        result = super().prepare_case(contract)
        eligible = sorted((item for item in self.reference_pool
                           if item.get("distribution_id") == self.case.get("distribution_id")
                           and item.get("case_id", "") > self.case.get("case_id", "")
                           and item.get("source_id") != self.case.get("source_id")),
                          key=lambda item: item["case_id"])
        self._candidate_order = [str(item["case_id"]) for item in eligible]
        if not eligible:
            self.failure_code = "GENERATION_FAILURE"
            raise HarnessError(self.failure_code, "no lexicographically next distinct-source reference")
        self.reference = eligible[0]
        self.reference_rank = 1
        self._reference_wave = normalize_audio(self.reference["waveform"], int(self.reference.get("sample_rate", SAMPLE_RATE_HZ)))
        self._details.update({
            "reference_audio_hash": _audio_hash(self._reference_wave),
            "reference_source_id": self.reference["source_id"],
            "reference_case_id": self.reference["case_id"],
            "lexicographic_reference_rank": self.reference_rank,
            "candidate_order": self._candidate_order,
            "different_source_id_check": "PASS",
            "target_intervals": [{**item, "reference_identity": self.reference["case_id"]}
                                 for item in self._details["target_intervals"]],
        })
        return {**result, "reference_case_id": self.reference["case_id"],
                "reference_source_id": self.reference["source_id"],
                "candidate_order": self._candidate_order,
                "lexicographic_reference_rank": self.reference_rank,
                "different_source_id_check": "PASS"}

    def execute(self, source: np.ndarray, intervals: tuple[Interval, ...], seed: int) -> np.ndarray:
        if self.reference is None or self._reference_wave is None:
            self.failure_code = "GENERATION_FAILURE"
            raise HarnessError(self.failure_code, "reference was not prepared")
        normalized = normalize_audio(source, int(self.case.get("sample_rate", SAMPLE_RATE_HZ)))
        if self._normalized_source is None or not np.array_equal(normalized, self._normalized_source):
            self.failure_code = "INPUT_NOT_SYNTHETIC"
            raise HarnessError(self.failure_code, "source waveform does not match prepared fixture")
        output = normalized.copy()
        effective_fades = []
        for item in self._mapped_intervals:
            # The frozen rule chooses the first available mono window; a shorter
            # non-empty recording is duration-fit by the frozen transform itself.
            reference_window = self._reference_wave[:max(1, item.end - item.start)]
            transformed = cross_speaker_boundary(normalized, reference_window, item.start, item.end)
            fade = min(CROSSFADE_SAMPLES, (item.end - item.start) // 2,
                       item.start, len(output) - item.end)
            support_start = item.start - fade
            output[support_start:item.end] = transformed[support_start:item.end]
            effective_fades.append(fade)
        for index, item in enumerate(self._details["target_intervals"]):
            item["effective_crossfade_samples"] = effective_fades[index]
            item["output_start"] = self._mapped_intervals[index].start - effective_fades[index]
            item["output_end"] = self._mapped_intervals[index].end
            item["crossfade_support"] = [item["output_start"], item["output_end"]]
        self._details["effective_crossfade_samples"] = effective_fades
        return np.clip(output, -1.0, 1.0).astype(np.float32)

    def emit_provenance(self, contract: StageContract, output_hash: str) -> Mapping[str, Any]:
        return {**self._base_provenance(contract, output_hash),
                "lexicographic_reference_rank": self.reference_rank,
                "lexicographic_candidate_order": self._candidate_order,
                "different_source_id_check": "PASS" if self.reference else "FAIL",
                "reference_case_id": self.reference.get("case_id") if self.reference else None,
                "effective_crossfade_samples": self._details.get("effective_crossfade_samples", [])
class M4RealAdapter(_AdapterBase):
    """Same-case left-then-right reference selection plus the frozen M4 function."""
    family = "same_speaker_splice_crossfade_control"
    implementation = "audiobookbench.topconf.w7_candidate_transforms::same_speaker_splice_crossfade"

    def __init__(self, case: Mapping[str, Any], *, config_hash: str) -> None:
        super().__init__(case, config_hash=config_hash)
        self.reference_sides: list[str] = []
        self.reference_windows: list[dict[str, Any]] = []

    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]:
        result = super().prepare_case(contract)
        assert self._normalized_source is not None
        for item in self._mapped_intervals:
            span = item.end - item.start
            if item.start >= span:
                side, start, end = "left", item.start - span, item.start
            elif len(self._normalized_source) - item.end >= span:
                side, start, end = "right", item.end, item.end + span
            else:
                self.failure_code = "GENERATION_FAILURE"
                raise HarnessError(self.failure_code, "no complete same-case non-target context")
            self.reference_sides.append(side)
            self.reference_windows.append({
                "side": side, "start": start, "end": end,
                "identity": f"{contract.case_id}:context:{start}:{end}",
            })
        self._details.update({
            "reference_source_id": self.case.get("source_id"),
            "reference_audio_hash": [_audio_hash(self._normalized_source[item["start"]:item["end"]])
                                     for item in self.reference_windows],
            "reference_sides": self.reference_sides,
            "reference_windows": self.reference_windows,
            "target_intervals": [{**item, "reference_identity": self.reference_windows[i]["identity"],
                                  "reference_side": self.reference_sides[i]}
                                 for i, item in enumerate(self._details["target_intervals"])],
        })
        return {**result, "reference_sides": self.reference_sides,
                "reference_windows": self.reference_windows}

    def execute(self, source: np.ndarray, intervals: tuple[Interval, ...], seed: int) -> np.ndarray:
        normalized = normalize_audio(source, int(self.case.get("sample_rate", SAMPLE_RATE_HZ)))
        if self._normalized_source is None or not np.array_equal(normalized, self._normalized_source):
            self.failure_code = "INPUT_NOT_SYNTHETIC"
            raise HarnessError(self.failure_code, "source waveform does not match prepared fixture")
        output = normalized.copy()
        effective_fades = []
        for item in self._mapped_intervals:
            # Always reference the original waveform, never a prior interval edit.
            transformed = same_speaker_splice_crossfade(normalized, item.start, item.end)
            fade = min(CROSSFADE_SAMPLES, (item.end - item.start) // 2,
                       item.start, len(output) - item.end)
            support_start = item.start - fade
            output[support_start:item.end] = transformed[support_start:item.end]
            effective_fades.append(fade)
        for index, item in enumerate(self._details["target_intervals"]):
            item["effective_crossfade_samples"] = effective_fades[index]
            item["output_start"] = self._mapped_intervals[index].start - effective_fades[index]
            item["output_end"] = self._mapped_intervals[index].end
            item["crossfade_support"] = [item["output_start"], item["output_end"]]
        self._details["effective_crossfade_samples"] = effective_fades
        return np.clip(output, -1.0, 1.0).astype(np.float32)

    def emit_provenance(self, contract: StageContract, output_hash: str) -> Mapping[str, Any]:
        unique_sides = sorted(set(self.reference_sides))
        side: str | list[str] = unique_sides[0] if len(unique_sides) == 1 else list(self.reference_sides)
        return {**self._base_provenance(contract, output_hash),
                "reference_side": side,
                "reference_sides": self.reference_sides,
                "reference_windows": self.reference_windows,
                "effective_crossfade_samples": self._details.get("effective_crossfade_samples", [])}
# End of the synthetic M2/M4 adapter definitions.
