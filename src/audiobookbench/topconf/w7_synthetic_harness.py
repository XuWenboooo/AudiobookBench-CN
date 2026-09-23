"""Synthetic W7 orchestration contracts. No formal W7 adapter is wired here."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Callable, Mapping, Protocol

import numpy as np


MARKER = "SYNTHETIC_NONSCIENTIFIC_OUTPUT"
STAGES = (
    "LOAD_CONFIG", "VALIDATE_APPROVAL_STATE", "LOAD_CASE", "RESOLVE_TRANSCRIPT",
    "RESOLVE_INTERVALS", "MATERIALIZE_MECHANISM", "APPLY_MEDIA_CONDITION",
    "RUN_LOCALIZER", "RUN_WHETHER_A", "RUN_WHETHER_B", "PRESERVE_RAW_OUTPUT",
    "COMPUTE_METRICS", "EVALUATE_GATE",
)
FAILURES = (
    "CONFIG_NOT_APPROVED", "INPUT_NOT_SYNTHETIC", "TRANSCRIPT_BINDING_FAILURE",
    "ALIGNMENT_FAILURE", "MASK_MAPPING_FAILURE", "GENERATION_FAILURE",
    "TRANSFORM_FAILURE", "LOCALIZER_FAILURE", "WHETHER_A_FAILURE",
    "WHETHER_B_FAILURE", "RAW_OUTPUT_WRITE_FAILURE", "METRIC_STAGE_BLOCKED",
    "GATE_STAGE_BLOCKED",
)
NAMESPACES = ("CASE", "MECHANISM", "INTERVAL", "MASK_GROUP", "CANDIDATE", "TRANSFORM")
MECHANISMS = ("M1", "M2", "M3", "M4", "M5")
REAL_CONTROL_FAMILIES = ("cross_speaker_boundary_control", "same_speaker_splice_crossfade_control")
MOCK_RUNTIME = "synthetic-mock-runtime-v1"
MOCK_ASSET = "synthetic-mock-assets-v1"
_SAFE_ID = re.compile(r"^SYNTH_[A-Za-z0-9_]+$")


class HarnessError(RuntimeError):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


class SimulatedCrash(RuntimeError):
    """Test hook: interrupt after a durably recorded stage."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def derive_subseed(master: int, policy: Mapping[str, str], namespace: str, identity: str, ordinal: int) -> int:
    if namespace not in NAMESPACES or namespace not in policy or ordinal < 0:
        raise HarnessError("CONFIG_NOT_APPROVED", "invalid seed namespace policy")
    payload = canonical([master, policy[namespace], namespace, identity, ordinal])
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


@dataclass(frozen=True)
class Interval:
    start: int
    end: int
    ordinal: int
    mask_group: int


@dataclass(frozen=True)
class StageContract:
    case_id: str
    distribution_id: str
    condition_id: str
    mechanism_family: str
    source_audio_identity: str
    source_audio_hash: str
    transcript_identity: str
    transcript_hash: str
    intervals: tuple[Interval, ...]
    seed: int
    runtime_identity: str
    asset_identity: str
    transform_identity: str
    output_audio_hash: str
    status: str
    failure_code: str | None
    provenance_parent_ids: tuple[str, ...]


@dataclass(frozen=True)
class StageResult:
    stage: str
    contract: StageContract
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class M3Observation:
    input_mask_interval: Interval
    generated_codec_frame_count: int
    generated_region_boundary: tuple[int, int]
    decoder_sample_mapping: tuple[int, int]
    extracted_segment_identity: str
    resampled_segment_identity: str
    final_splice_interval: Interval


class MechanismAdapter(Protocol):
    family: str
    def validate_runtime(self, identity: str) -> bool: ...
    def validate_assets(self, identity: str) -> bool: ...
    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]: ...
    def execute(self, source: np.ndarray, intervals: tuple[Interval, ...], seed: int) -> np.ndarray: ...
    def validate_output(self, source: np.ndarray, output: np.ndarray, intervals: tuple[Interval, ...]) -> bool: ...
    def emit_provenance(self, contract: StageContract, output_hash: str) -> Mapping[str, Any]: ...


class RealAdapterNotReady:
    """Typed contract for future M1..M5 bindings; execution always fails closed."""
    def __init__(self, family: str) -> None:
        if family not in MECHANISMS:
            raise ValueError(family)
        self.family = family

    def validate_runtime(self, identity: str) -> bool:
        return False

    def validate_assets(self, identity: str) -> bool:
        return False

    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]:
        raise HarnessError("GENERATION_FAILURE", "real adapter NOT_READY")

    def execute(self, source: np.ndarray, intervals: tuple[Interval, ...], seed: int) -> np.ndarray:
        raise HarnessError("GENERATION_FAILURE", "real adapter NOT_READY")

    def validate_output(self, source: np.ndarray, output: np.ndarray, intervals: tuple[Interval, ...]) -> bool:
        return False

    def emit_provenance(self, contract: StageContract, output_hash: str) -> Mapping[str, Any]:
        raise HarnessError("GENERATION_FAILURE", "real adapter NOT_READY")


REAL_ADAPTERS: Mapping[str, MechanismAdapter] = {name: RealAdapterNotReady(name) for name in MECHANISMS}


def seconds_to_samples(seconds: float, sample_rate: int) -> int:
    if not np.isfinite(seconds) or seconds < 0 or sample_rate <= 0:
        raise HarnessError("MASK_MAPPING_FAILURE")
    return int(np.floor(seconds * sample_rate + 0.5))


def seconds_to_codec_frames(seconds: float, frames_per_second: int) -> int:
    return seconds_to_samples(seconds, frames_per_second)


def validate_intervals(intervals: tuple[Interval, ...], sample_count: int) -> tuple[Interval, ...]:
    ordered = tuple(sorted(intervals, key=lambda item: (item.start, item.end)))
    if not ordered or any(not (0 <= item.start < item.end <= sample_count) for item in ordered):
        raise HarnessError("MASK_MAPPING_FAILURE", "empty or out-of-bounds mask")
    if any(left.end > right.start for left, right in zip(ordered, ordered[1:])):
        raise HarnessError("MASK_MAPPING_FAILURE", "overlapping masks")
    return tuple(Interval(item.start, item.end, ordinal, item.mask_group) for ordinal, item in enumerate(ordered))


def duration_fit(segment: np.ndarray, target_samples: int) -> np.ndarray:
    if segment.ndim != 1 or len(segment) == 0 or target_samples <= 0:
        raise HarnessError("TRANSFORM_FAILURE")
    if len(segment) == target_samples:
        return segment.copy()
    x = np.linspace(0, len(segment) - 1, target_samples, dtype=np.float64)
    return np.interp(x, np.arange(len(segment)), segment).astype(np.float32)


def splice(source: np.ndarray, replacements: tuple[np.ndarray, ...], intervals: tuple[Interval, ...]) -> np.ndarray:
    if len(replacements) != len(intervals):
        raise HarnessError("TRANSFORM_FAILURE")
    ordered = validate_intervals(intervals, len(source))
    if ordered != intervals:
        raise HarnessError("TRANSFORM_FAILURE", "composition must be ordered")
    result = source.copy()
    for interval, replacement in zip(ordered, replacements):
        result[interval.start:interval.end] = duration_fit(replacement, interval.end - interval.start)
    return result


class SyntheticMechanismAdapter:
    def __init__(self, family: str, namespace_policy: Mapping[str, str]) -> None:
        if family not in MECHANISMS:
            raise ValueError(family)
        self.family = family
        self.namespace_policy = namespace_policy

    def validate_runtime(self, identity: str) -> bool:
        return identity == MOCK_RUNTIME

    def validate_assets(self, identity: str) -> bool:
        return identity == MOCK_ASSET

    def prepare_case(self, contract: StageContract) -> Mapping[str, Any]:
        return {"case_id": contract.case_id, "family": self.family, "marker": MARKER}

    def execute(self, source: np.ndarray, intervals: tuple[Interval, ...], seed: int) -> np.ndarray:
        pieces = tuple(np.full((interval.end - interval.start) // 2 + 1,
                               ((derive_subseed(seed, self.namespace_policy, "INTERVAL", self.family, interval.ordinal) % 1000) / 1000.0) - 0.5,
                               dtype=np.float32) for interval in intervals)
        return splice(source, pieces, intervals)

    def validate_output(self, source: np.ndarray, output: np.ndarray, intervals: tuple[Interval, ...]) -> bool:
        if len(source) != len(output):
            return False
        mask = np.zeros(len(source), dtype=bool)
        for interval in intervals:
            mask[interval.start:interval.end] = True
        return bool(np.array_equal(source[~mask], output[~mask]))

    def emit_provenance(self, contract: StageContract, output_hash: str) -> Mapping[str, Any]:
        return {"family": self.family, "output_hash": output_hash, "marker": MARKER}


class LocalizerAdapter(Protocol):
    def infer(self, audio_hash: str, intervals: tuple[Interval, ...]) -> Mapping[str, Any]: ...


class DetectorAdapter(Protocol):
    def infer(self, audio_hash: str, name: str) -> Mapping[str, Any]: ...


class MetricStage(Protocol):
    def compute(self, raw: Mapping[str, Any]) -> Mapping[str, Any]: ...


class GateStage(Protocol):
    def evaluate(self, metrics: Mapping[str, Any]) -> Mapping[str, Any]: ...


class DummyLocalizer:
    def infer(self, audio_hash: str, intervals: tuple[Interval, ...]) -> Mapping[str, Any]:
        return {"marker": MARKER, "kind": "localizer", "source_hash": audio_hash,
                "segments": [[item.start, item.end] for item in intervals]}


class DummyDetector:
    def infer(self, audio_hash: str, name: str) -> Mapping[str, Any]:
        return {"marker": MARKER, "kind": name, "source_hash": audio_hash,
                "dummy_score": int(audio_hash[:8], 16) / 0xFFFFFFFF}


class DummyMetricStage:
    def compute(self, raw: Mapping[str, Any]) -> Mapping[str, Any]:
        if raw.get("marker") != MARKER:
            raise HarnessError("METRIC_STAGE_BLOCKED")
        return {"marker": MARKER, "formal_metrics": "NOT_COMPUTED", "status": "MOCK_INTERFACE_ONLY"}


class DummyGateStage:
    def evaluate(self, metrics: Mapping[str, Any]) -> Mapping[str, Any]:
        if metrics.get("marker") != MARKER:
            raise HarnessError("GATE_STAGE_BLOCKED")
        return {"marker": MARKER, "formal_gate": "NOT_EVALUATED", "status": "MOCK_INTERFACE_ONLY"}


def synthetic_waveform(case_id: str, sample_count: int) -> np.ndarray:
    if not _SAFE_ID.fullmatch(case_id) or sample_count <= 0:
        raise HarnessError("INPUT_NOT_SYNTHETIC")
    positions = np.arange(sample_count, dtype=np.float32)
    return (0.1 * np.sin(positions * np.float32(0.03125))).astype(np.float32)


def _safe_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if path.read_bytes() != content:
            raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", f"immutable artifact conflict: {path}")
    except OSError as exc:
        raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", str(exc)) from exc


class AppendOnlyLedger:
    """One immutable file per event avoids duplicate append on restart."""
    def __init__(self, root: Path) -> None:
        self.root = root

    def record(self, *, event_id: str, case_id: str, stage: str, input_hashes: Mapping[str, str],
               output_hashes: Mapping[str, str], config_hash: str, runtime_identity: str,
               seed: int, sub_seed: int, status: str, failure_code: str | None,
               parent_ids: tuple[str, ...]) -> None:
        path = self.root / f"{event_id}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            stable = ("event_id", "case_id", "stage", "input_hashes", "output_hashes", "config_hash",
                      "runtime_identity", "seed", "sub_seed", "status", "failure_code", "provenance_parent_ids")
            desired = locals().copy()
            desired["provenance_parent_ids"] = list(parent_ids)
            if any(existing[key] != desired[key] for key in stable):
                raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "ledger event conflict")
            return
        event = {"event_id": event_id, "timestamp": datetime.now(timezone.utc).isoformat(),
                 "case_id": case_id, "stage": stage, "input_hashes": dict(input_hashes),
                 "output_hashes": dict(output_hashes), "config_hash": config_hash,
                 "runtime_identity": runtime_identity, "seed": seed, "sub_seed": sub_seed,
                 "status": status, "failure_code": failure_code, "provenance_parent_ids": list(parent_ids)}
        _safe_write(path, canonical(event))


def _case_intervals(case: Mapping[str, Any]) -> tuple[Interval, ...]:
    count = int(case.get("interval_count", 0))
    length = int(case["sample_count"])
    if "intervals" in case:
        raw = case["intervals"]
        return tuple(Interval(int(pair[0]), int(pair[1]), index,
                              int(pair[2]) if len(pair) > 2 else index) for index, pair in enumerate(raw))
    if count < 1 or count > 20:
        raise HarnessError("MASK_MAPPING_FAILURE", "interval count outside synthetic fixture range")
    width = max(1, length // (count * 3))
    groups = case.get("mask_groups", list(range(count)))
    if len(groups) != count:
        raise HarnessError("MASK_MAPPING_FAILURE", "mask group count mismatch")
    return tuple(Interval(index * 3 * width, index * 3 * width + width, index, int(groups[index]))
                 for index in range(count))


class SyntheticW7Harness:
    def __init__(self, config_path: Path, *, expected_config_hash: str, output_root: Path,
                 localizer: LocalizerAdapter | None = None, whether_a: DetectorAdapter | None = None,
                 whether_b: DetectorAdapter | None = None) -> None:
        self.output_root = output_root.resolve()
        if self.output_root.parts[-2:] != ("artifacts", "w7_synthetic_harness"):
            raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "synthetic namespace required")
        config_bytes = config_path.read_bytes()
        self.config_hash = digest(config_bytes)
        if self.config_hash != expected_config_hash.lower():
            raise HarnessError("CONFIG_NOT_APPROVED", "unknown config hash")
        self.config = json.loads(config_bytes)
        if self.config.get("approval_state") != "CANDIDATE_NOT_APPROVED":
            raise HarnessError("CONFIG_NOT_APPROVED", "fixture config must be a candidate")
        self.localizer = localizer or DummyLocalizer()
        self.whether_a = whether_a or DummyDetector()
        self.whether_b = whether_b or DummyDetector()
        self.metric_stage: MetricStage = DummyMetricStage()
        self.gate_stage: GateStage = DummyGateStage()

    def _guard(self, case: Mapping[str, Any], *, request_level2: bool, execution_authorized: bool,
               runtime_identity: str, asset_identity: str, adapter_mode: str = "synthetic_mock") -> None:
        if request_level2:
            raise HarnessError("INPUT_NOT_SYNTHETIC", "Level-2 request blocked")
        if case.get("data_origin") != "synthetic" or not _SAFE_ID.fullmatch(str(case.get("case_id", ""))):
            if adapter_mode == "real_adapter_synthetic_fixture":
                raise HarnessError("W7_REAL_EXECUTION_BLOCKED", "real adapters are synthetic-fixture only")
            if self.config.get("approval_state") != "APPROVED":
                raise HarnessError("W7_REAL_EXECUTION_BLOCKED_UNAPPROVED_CONFIG")
            raise HarnessError("INPUT_NOT_SYNTHETIC")
        if any(key in case for key in ("audio_path", "source_path", "waveform", "real_case_id", "outcome_path")):
            raise HarnessError("INPUT_NOT_SYNTHETIC", "external input field is forbidden")
        if execution_authorized:
            raise HarnessError("CONFIG_NOT_APPROVED", "synthetic harness cannot authorize W7")
        if adapter_mode == "synthetic_mock":
            if runtime_identity != MOCK_RUNTIME or asset_identity != MOCK_ASSET:
                raise HarnessError("CONFIG_NOT_APPROVED", "unknown or unfrozen runtime/asset identity")
        elif adapter_mode == "real_adapter_synthetic_fixture":
            from .w7_m2_m4_adapters import current_runtime_identity, SYNTHETIC_ASSET_IDENTITY
            if case.get("mechanism_family") not in REAL_CONTROL_FAMILIES:
                raise HarnessError("CONFIG_NOT_APPROVED", "real fixture mode is limited to frozen M2/M4")
            if runtime_identity != current_runtime_identity() or asset_identity != SYNTHETIC_ASSET_IDENTITY:
                raise HarnessError("CONFIG_NOT_APPROVED", "unknown runtime or fixture asset identity")
        else:
            raise HarnessError("CONFIG_NOT_APPROVED", "unknown adapter mode")

    def _artifact_path(self, relative: str) -> Path:
        path = (self.output_root / relative).resolve()
        if not path.is_relative_to(self.output_root):
            raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "artifact escaped synthetic namespace")
        return path

    def dry_run(self, cases: tuple[Mapping[str, Any], ...], *, request_level2: bool = False,
                execution_authorized: bool = False, runtime_identity: str = MOCK_RUNTIME,
                asset_identity: str = MOCK_ASSET, adapter_mode: str = "synthetic_mock") -> Mapping[str, Any]:
        schedule = []
        for case in sorted(cases, key=lambda item: str(item.get("case_id", ""))):
            self._guard(case, request_level2=request_level2, execution_authorized=execution_authorized,
                        runtime_identity=runtime_identity, asset_identity=asset_identity, adapter_mode=adapter_mode)
            raw_intervals = _case_intervals(case)
            try:
                intervals = validate_intervals(raw_intervals, int(case["sample_count"]))
                interval_validation = "PASS"
            except HarnessError:
                intervals = raw_intervals
                interval_validation = "MASK_MAPPING_FAILURE"
            mechanism = str(case["mechanism_family"])
            if mechanism not in MECHANISMS and mechanism not in REAL_CONTROL_FAMILIES:
                raise HarnessError("CONFIG_NOT_APPROVED", "unknown mechanism")
            seed = derive_subseed(self.config["master_seed"], self.config["namespace_policy"],
                                  "CASE", str(case["case_id"]), 0)
            artifact_paths = [f"{case['case_id']}/stages/{stage}.json" for stage in STAGES]
            artifact_paths += [f"{case['case_id']}/ledger/{digest(canonical([self.config_hash, case['case_id'], stage]))}.json"
                               for stage in STAGES]
            artifact_paths += [f"{case['case_id']}/raw_non_scientific/{name}.json"
                               for name in ("RUN_LOCALIZER", "RUN_WHETHER_A", "RUN_WHETHER_B", "combined")]
            artifact_paths += [f"{case['case_id']}/media/<sha256>.bin"]
            schedule.append({"case_id": case["case_id"], "mechanism_family": mechanism,
                             "condition_id": case["condition_id"], "intervals": [asdict(x) for x in intervals],
                             "interval_validation": interval_validation,
                             "seed": seed,
                             "mechanism_seed": derive_subseed(seed, self.config["namespace_policy"], "MECHANISM", mechanism, 0),
                             "interval_seeds": [derive_subseed(seed, self.config["namespace_policy"], "INTERVAL", mechanism, x.ordinal) for x in intervals],
                             "mask_group_seeds": {str(group): derive_subseed(seed, self.config["namespace_policy"], "MASK_GROUP", mechanism, group)
                                                  for group in sorted({x.mask_group for x in intervals})},
                             "candidate_seed": derive_subseed(seed, self.config["namespace_policy"], "CANDIDATE", mechanism, 0),
                             "transform_seed": derive_subseed(seed, self.config["namespace_policy"], "TRANSFORM", str(case["condition_id"]), 0),
                             "expected_artifact_paths": artifact_paths})
        body = {"config_hash": self.config_hash, "schedule": schedule, "marker": MARKER}
        return {**body, "schedule_hash": digest(canonical(body)), "audio_loaded": False, "models_loaded": False}

    def run(self, case: Mapping[str, Any], *, crash_after: str | None = None,
            audio_loader: Callable[[Mapping[str, Any]], np.ndarray] | None = None,
            request_level2: bool = False, execution_authorized: bool = False,
            runtime_identity: str | None = None, asset_identity: str | None = None,
            adapter_mode: str = "synthetic_mock", real_adapter: MechanismAdapter | None = None) -> Mapping[str, Any]:
        # This guard precedes LOAD_CASE and every possible audio loader call.
        if adapter_mode == "real_adapter_synthetic_fixture":
            if real_adapter is None:
                from .w7_m2_m4_adapters import current_runtime_identity, SYNTHETIC_ASSET_IDENTITY
                runtime_identity = runtime_identity or current_runtime_identity()
                asset_identity = asset_identity or SYNTHETIC_ASSET_IDENTITY
            else:
                runtime_identity = runtime_identity or str(getattr(real_adapter, "runtime_identity", ""))
                asset_identity = asset_identity or str(getattr(real_adapter, "asset_identity", ""))
        else:
            runtime_identity = runtime_identity or MOCK_RUNTIME
            asset_identity = asset_identity or MOCK_ASSET
        self._guard(case, request_level2=request_level2, execution_authorized=execution_authorized,
                    runtime_identity=runtime_identity, asset_identity=asset_identity, adapter_mode=adapter_mode)
        if adapter_mode == "real_adapter_synthetic_fixture" and (
                real_adapter is None or real_adapter.family != case.get("mechanism_family")):
            raise HarnessError("CONFIG_NOT_APPROVED", "matching M2/M4 real adapter required")
        if audio_loader is not None:
            raise HarnessError("INPUT_NOT_SYNTHETIC", "external audio loaders are disabled")
        plan = self.dry_run((case,), runtime_identity=runtime_identity, asset_identity=asset_identity,
                            adapter_mode=adapter_mode)
        case_id = str(case["case_id"])
        base = self.output_root / case_id
        ledger = AppendOnlyLedger(base / "ledger")
        seed = plan["schedule"][0]["seed"]
        intervals = _case_intervals(case)
        parents: list[str] = []
        source: np.ndarray | None = None
        output: np.ndarray | None = None
        source_hash = "DEFERRED"
        output_hash = "DEFERRED"
        transcript = str(case.get("transcript", ""))
        transcript_hash = digest(transcript.encode("utf-8"))
        transform_id = f"synthetic-{case['mechanism_family']}-{case['condition_id']}-v1"
        raw_refs: dict[str, Mapping[str, Any]] = {}

        def contract(stage: str, status: str = "PASS", failure: str | None = None) -> StageContract:
            return StageContract(case_id, str(case["distribution_id"]), str(case["condition_id"]),
                                 str(case["mechanism_family"]), f"synthetic-wave:{case_id}", source_hash,
                                 f"synthetic-transcript:{case_id}", transcript_hash, intervals, seed,
                                 runtime_identity, asset_identity, transform_id, output_hash, status, failure,
                                 tuple(parents))

        def stage(name: str, fn: Callable[[], Mapping[str, Any]]) -> Mapping[str, Any]:
            event_id = digest(canonical([self.config_hash, case_id, name]))
            artifact = base / "stages" / f"{name}.json"
            if artifact.exists() and (base / "ledger" / f"{event_id}.json").exists():
                encoded_existing = artifact.read_bytes()
                event = json.loads((base / "ledger" / f"{event_id}.json").read_text(encoding="utf-8"))
                if (event["output_hashes"]["stage_record"] != digest(encoded_existing)
                        or event["config_hash"] != self.config_hash
                        or event["runtime_identity"] != runtime_identity
                        or event["provenance_parent_ids"] != parents):
                    raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "resume provenance mismatch")
                payload = json.loads(encoded_existing)
                if payload["contract"]["status"] != "PASS":
                    raise HarnessError(payload["contract"]["failure_code"])
                parents.append(event_id)
                return payload["payload"]
            try:
                value = dict(fn())
                status, failure = "PASS", None
            except HarnessError as exc:
                value, status, failure = {"error": str(exc)}, "FAIL", exc.code
                if name == "MATERIALIZE_MECHANISM" and adapter_mode == "real_adapter_synthetic_fixture" and real_adapter:
                    real_adapter.failure_code = exc.code
                    provenance = real_adapter.emit_provenance(contract(name, status, failure), "")
                    value["adapter_provenance"] = provenance
                    _safe_write(base / "adapter_provenance" / f"{case['mechanism_family']}.json", canonical(provenance))
            entry = StageResult(name, contract(name, status, failure), value)
            encoded = canonical(asdict(entry))
            _safe_write(artifact, encoded)
            ledger.record(event_id=event_id, case_id=case_id, stage=name,
                          input_hashes={"source": source_hash, "transcript": transcript_hash},
                          output_hashes={"stage_record": digest(encoded), "audio": output_hash},
                          config_hash=self.config_hash, runtime_identity=runtime_identity, seed=seed,
                          sub_seed=derive_subseed(seed, self.config["namespace_policy"], "CASE", case_id, STAGES.index(name)),
                          status=status, failure_code=failure, parent_ids=tuple(parents))
            parents.append(event_id)
            if failure:
                raise HarnessError(failure, str(value.get("error", "")))
            if crash_after == name:
                raise SimulatedCrash(name)
            return value

        stage("LOAD_CONFIG", lambda: {"config_hash": self.config_hash, "approval_state": self.config["approval_state"]})
        stage("VALIDATE_APPROVAL_STATE", lambda: {"synthetic_fixture_allowed": True, "formal_approved": False})

        def load_case() -> Mapping[str, Any]:
            nonlocal source, source_hash
            source = synthetic_waveform(case_id, int(case["sample_count"]))
            if (not isinstance(source, np.ndarray) or source.dtype != np.float32 or source.ndim != 1
                    or len(source) != int(case["sample_count"]) or not np.isfinite(source).all()):
                raise HarnessError("INPUT_NOT_SYNTHETIC", "invalid synthetic waveform")
            source_hash = digest(source.tobytes())
            return {"source_audio_hash": source_hash, "sample_count": len(source), "data_origin": "synthetic"}

        loaded = stage("LOAD_CASE", load_case)
        if source is None:
            source = synthetic_waveform(case_id, int(case["sample_count"]))
            source_hash = digest(source.tobytes())
            if source_hash != loaded["source_audio_hash"]:
                raise HarnessError("INPUT_NOT_SYNTHETIC", "source changed across resume")
        stage("RESOLVE_TRANSCRIPT", lambda: _transcript_result(case, transcript, transcript_hash))
        stage("RESOLVE_INTERVALS", lambda: _interval_result(case, intervals))
        intervals = validate_intervals(intervals, int(case["sample_count"]))
        adapter = (SyntheticMechanismAdapter(str(case["mechanism_family"]), self.config["namespace_policy"])
                   if adapter_mode == "synthetic_mock" else real_adapter)
        if adapter is None:
            raise HarnessError("CONFIG_NOT_APPROVED", "mechanism adapter missing")

        def materialize() -> Mapping[str, Any]:
            nonlocal output, output_hash, intervals
            if case.get("fail_at") == "generation":
                raise HarnessError("GENERATION_FAILURE")
            if not adapter.validate_runtime(runtime_identity) or not adapter.validate_assets(asset_identity):
                raise HarnessError("CONFIG_NOT_APPROVED")
            prepared = adapter.prepare_case(contract("MATERIALIZE_MECHANISM"))
            if adapter_mode == "real_adapter_synthetic_fixture":
                intervals = tuple(Interval(item["output_start"], item["output_end"], item["ordinal"],
                                           item.get("mask_group", item["ordinal"]))
                                  for item in prepared["mapped_intervals"])
            try:
                output = adapter.execute(source, intervals, seed)
            except HarnessError:
                raise
            except Exception as exc:
                raise HarnessError("GENERATION_FAILURE", "synthetic adapter failed") from exc
            if not adapter.validate_output(source, output, intervals):
                raise HarnessError("TRANSFORM_FAILURE")
            output_hash = digest(output.tobytes())
            media_path = base / "media" / f"{output_hash}.bin"
            _safe_write(media_path, output.tobytes())
            observation = None
            if case["mechanism_family"] == "M3":
                observation = [asdict(M3Observation(x,
                               seconds_to_codec_frames((x.end - x.start) / 16000, 75),
                               (seconds_to_codec_frames(x.start / 16000, 75),
                                seconds_to_codec_frames(x.end / 16000, 75)),
                               (x.start, x.end),
                               f"mock-codec-segment:{x.ordinal}", f"mock-resampled:{x.ordinal}", x))
                               for x in intervals]
            provenance = adapter.emit_provenance(contract("MATERIALIZE_MECHANISM"), output_hash)
            if adapter_mode == "real_adapter_synthetic_fixture":
                _safe_write(base / "adapter_provenance" / f"{case['mechanism_family']}.json", canonical(provenance))
            return {"output_audio_hash": output_hash, "media_path": str(media_path.relative_to(self.output_root)),
                    "composition_ledger": [asdict(x) for x in intervals], "m3_observations": observation,
                    "provenance": provenance}

        materialized = stage("MATERIALIZE_MECHANISM", materialize)
        if output is None:
            output_hash = materialized["output_audio_hash"]
            media_path = self._artifact_path(materialized["media_path"])
            media_bytes = media_path.read_bytes()
            if digest(media_bytes) != output_hash:
                raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "materialized media changed")
            output = np.frombuffer(media_bytes, dtype=np.float32).copy()

        def media_condition() -> Mapping[str, Any]:
            if case.get("fail_at") == "codec":
                raise HarnessError("TRANSFORM_FAILURE", "synthetic codec failure")
            return {"condition_id": case["condition_id"], "output_audio_hash": output_hash,
                    "transform_identity": transform_id, "marker": MARKER}

        stage("APPLY_MEDIA_CONDITION", media_condition)

        def dummy_call(name: str, fn: Callable[[], Mapping[str, Any]], failure: str) -> Mapping[str, Any]:
            if case.get("fail_at") == name.lower():
                raise HarnessError(failure)
            try:
                result = dict(fn())
            except Exception as exc:
                raise HarnessError(failure, "synthetic dummy adapter failed") from exc
            if result.get("marker") != MARKER:
                raise HarnessError(failure, "dummy marker missing")
            path = base / "raw_non_scientific" / f"{name}.json"
            _safe_write(path, canonical(result))
            return {"raw_path": str(path.relative_to(self.output_root)), "raw_hash": digest(canonical(result)), "marker": MARKER}

        for name, fn, failure in (
            ("RUN_LOCALIZER", lambda: self.localizer.infer(output_hash, intervals), "LOCALIZER_FAILURE"),
            ("RUN_WHETHER_A", lambda: self.whether_a.infer(output_hash, "Whether-A"), "WHETHER_A_FAILURE"),
            ("RUN_WHETHER_B", lambda: self.whether_b.infer(output_hash, "Whether-B"), "WHETHER_B_FAILURE"),
        ):
            raw_refs[name] = stage(name, lambda n=name, f=fn, e=failure: dummy_call(n, f, e))

        def preserve() -> Mapping[str, Any]:
            raw = {}
            for name, ref in raw_refs.items():
                try:
                    content = self._artifact_path(ref["raw_path"]).read_bytes()
                except OSError as exc:
                    raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "raw adapter output missing") from exc
                if digest(content) != ref["raw_hash"]:
                    raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "raw adapter output changed")
                raw[name] = json.loads(content)
            if any(item.get("marker") != MARKER for item in raw.values()):
                raise HarnessError("RAW_OUTPUT_WRITE_FAILURE", "non-scientific marker missing")
            combined = {"marker": MARKER, "case_id": case_id, "outputs": raw,
                        "formal_w7_result": False}
            path = base / "raw_non_scientific" / "combined.json"
            _safe_write(path, canonical(combined))
            return {"raw_path": str(path.relative_to(self.output_root)), "raw_hash": digest(canonical(combined)),
                    "marker": MARKER}

        preserved = stage("PRESERVE_RAW_OUTPUT", preserve)
        stage("COMPUTE_METRICS", lambda: self.metric_stage.compute({"marker": preserved["marker"]}))
        gate = stage("EVALUATE_GATE", lambda: self.gate_stage.evaluate({"marker": MARKER}))
        return {"case_id": case_id, "status": "SYNTHETIC_ORCHESTRATION_COMPLETE",
                "schedule_hash": plan["schedule_hash"], "output_audio_hash": output_hash,
                "stage_count": len(STAGES), "gate": gate, "marker": MARKER,
                "w7_execution_authorized": False, "scientific_inferences": 0}

    def run_schedule(self, cases: tuple[Mapping[str, Any], ...]) -> Mapping[str, Any]:
        """Execute every synthetic fixture in stable order; report terminal failures."""
        plan = self.dry_run(cases)
        by_id = {str(case["case_id"]): case for case in cases}
        if len(by_id) != len(cases):
            raise HarnessError("CONFIG_NOT_APPROVED", "duplicate synthetic case ID")
        terminal = []
        for item in plan["schedule"]:
            case = by_id[item["case_id"]]
            try:
                result = self.run(case)
                terminal.append({"case_id": item["case_id"], "status": result["status"],
                                 "failure_code": None, "output_audio_hash": result["output_audio_hash"]})
            except HarnessError as exc:
                event_files = (self.output_root / item["case_id"] / "ledger").glob("*.json")
                if not any(json.loads(path.read_text(encoding="utf-8")).get("failure_code") == exc.code
                           for path in event_files):
                    raise
                terminal.append({"case_id": item["case_id"], "status": "TERMINAL_FAILURE",
                                 "failure_code": exc.code, "output_audio_hash": None})
        return {"marker": MARKER, "schedule_hash": plan["schedule_hash"],
                "terminal_cases": terminal, "case_count": len(terminal),
                "w7_execution_authorized": False, "scientific_inferences": 0}


def _transcript_result(case: Mapping[str, Any], transcript: str, transcript_hash: str) -> Mapping[str, Any]:
    if case.get("fail_at") == "transcript" or not transcript.startswith("synthetic "):
        raise HarnessError("TRANSCRIPT_BINDING_FAILURE")
    return {"transcript_hash": transcript_hash, "identity": f"synthetic-transcript:{case['case_id']}"}


def _interval_result(case: Mapping[str, Any], intervals: tuple[Interval, ...]) -> Mapping[str, Any]:
    if case.get("fail_at") == "alignment":
        raise HarnessError("ALIGNMENT_FAILURE")
    ordered = validate_intervals(intervals, int(case["sample_count"]))
    return {"intervals": [asdict(x) for x in ordered], "interval_count": len(ordered)}
