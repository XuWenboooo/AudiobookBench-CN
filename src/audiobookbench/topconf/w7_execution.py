"""Frozen-input W7 execution contracts.

This module deliberately does not load a checkpoint or read a W7 case.  It is
the shared, outcome-blind harness used to validate a formal invocation before
any future human reauthorization.  Backends must be supplied explicitly by a
future execution process; registry lookup never searches for a model or a
"latest" checkpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Mapping, Protocol


FROZEN_LOCALIZERS = ("CFPRF", "MultiReso", "SAL", "BAM")
FROZEN_CONDITIONS = ("clean", "mechanism_shift", "codec", "resampling")
FROZEN_DISTRIBUTIONS = ("PartialEdit", "LlamaPartialSpoof R01TTS.0.b")


@dataclass(frozen=True)
class LocalizerSpec:
    model_id: str
    paradigm_id: str
    checkpoint_sha256: str
    adapter_id: str
    entrypoint: str
    temporal_resolution_sec: float


FROZEN_LOCALIZER_REGISTRY: dict[str, LocalizerSpec] = {
    "CFPRF": LocalizerSpec("CFPRF", "P2_FRAME_PLUS_PROPOSAL_REFINEMENT", "5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267", "phase3t_adapter_v1", "experiments/topconf_phase3t/run_cfprf.py", 0.02),
    "MultiReso": LocalizerSpec("MultiReso", "P3_MULTI_RESOLUTION_FRAME", "5B753752F7C25370C6ABF973F69F58E100DAD4B5D3EA035872335358A876FDD1", "six_scale_canonical_adapter_v1", "experiments/topconf_phase3t/run_multireso.py", 0.02),
    "SAL": LocalizerSpec("SAL", "P5_SEGMENT_AWARE_SEQUENCE", "FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F", "sal_temporal_adapter_v1", "research_assurance/topconf/w6_recovery/SAL_ADAPTER_CONTRACT_V1.json", 0.16),
    "BAM": LocalizerSpec("BAM", "P4_BOUNDARY_AWARE_FRAME", "5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1", "bam_temporal_adapter_v1", "research_assurance/topconf/w6_recovery/BAM_ADAPTER_CONTRACT_V1.json", 0.16),
}


class W7ExecutionContractError(ValueError):
    """Raised before an invocation can enter model inference."""


class LocalizerBackend(Protocol):
    def strict_load(self) -> None: ...

    def infer(self, waveform: Any) -> Mapping[str, Any]: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def assert_registry_is_frozen(registry: Mapping[str, LocalizerSpec] = FROZEN_LOCALIZER_REGISTRY) -> None:
    if tuple(registry) != FROZEN_LOCALIZERS:
        raise W7ExecutionContractError("localizer registry differs from frozen W7 set")
    if any(len(spec.checkpoint_sha256) != 64 for spec in registry.values()):
        raise W7ExecutionContractError("invalid checkpoint identity in registry")


def assert_frozen_input_hashes(expected: Mapping[Path, str]) -> None:
    for path, expected_hash in expected.items():
        if not path.is_file():
            raise W7ExecutionContractError(f"missing frozen input: {path}")
        actual = sha256_file(path)
        if actual != expected_hash.upper():
            raise W7ExecutionContractError(f"frozen hash mismatch: {path}")


def assert_reexecution_prerequisites(prerequisites: Mapping[str, str]) -> None:
    """Reject a W7 invocation unless every post-closure prerequisite is explicit.

    This is intentionally a pure contract check.  It neither loads a model nor
    reads a case, and it cannot convert an audit or a template into a human
    authorization.
    """
    required = {
        "sal_checkpoint_identity": {"PASS_EXACT_RECOVERED"},
        "bam_checkpoint_rights": {"PASS_EXPLICIT_BINDING", "PASS_FOR_LOCAL_RESEARCH_EVALUATION_WITH_RESTRICTIONS"},
        "mechanism_human_freeze": {"PASS_COMPLETE_TOTAL_MAP"},
        "human_reexecution_authorization": {"PASS_EXPLICIT_POST_CLOSURE"},
    }
    missing = [name for name, expected in required.items() if prerequisites.get(name) not in expected]
    if missing:
        raise W7ExecutionContractError("W7 re-execution prerequisites are not closed: " + ", ".join(missing))


def build_terminal_row(*, run_id: str, case_id: str, distribution: str, condition: str, model_id: str, status: str, runtime_metadata: Mapping[str, Any], whether_a: Any = None, whether_b: Any = None, where: Any = None, failure_code: str | None = None) -> dict[str, Any]:
    """Build the append-only raw-row contract without evaluating a sample."""
    if distribution not in FROZEN_DISTRIBUTIONS:
        raise W7ExecutionContractError("unfrozen distribution")
    if condition not in FROZEN_CONDITIONS:
        raise W7ExecutionContractError("unfrozen condition")
    if model_id not in FROZEN_LOCALIZER_REGISTRY:
        raise W7ExecutionContractError("unfrozen localizer")
    if not run_id or not case_id or not status:
        raise W7ExecutionContractError("terminal row requires run_id, case_id and status")
    if status == "VALID_INFERENCE" and failure_code is not None:
        raise W7ExecutionContractError("valid inference cannot carry a failure code")
    if status != "VALID_INFERENCE" and failure_code is None:
        raise W7ExecutionContractError("terminal failure requires a failure code")
    spec = FROZEN_LOCALIZER_REGISTRY[model_id]
    return {
        "run_id": run_id,
        "case_id": case_id,
        "distribution": distribution,
        "condition": condition,
        "model_id": model_id,
        "checkpoint_sha256": spec.checkpoint_sha256,
        "adapter_id": spec.adapter_id,
        "whether_a": whether_a,
        "whether_b": whether_b,
        "where": where,
        "status": status,
        "failure_code": failure_code,
        "runtime_metadata": dict(runtime_metadata),
    }


def synthetic_adapter_output(model_id: str, sample_count: int = 16000) -> dict[str, Any]:
    """Deterministic fixture only; it is never a W7 model inference output."""
    if model_id not in FROZEN_LOCALIZER_REGISTRY or sample_count <= 0:
        raise W7ExecutionContractError("invalid synthetic dry-run request")
    resolution = FROZEN_LOCALIZER_REGISTRY[model_id].temporal_resolution_sec
    frames = max(1, int(sample_count / 16000 / resolution))
    return {
        "fixture": "SYNTHETIC_ONLY_NO_W7_CASE",
        "model_id": model_id,
        "native_resolution_sec": resolution,
        "frame_count": frames,
        "spoof_scores": [0.5] * frames,
        "finite": True,
    }
