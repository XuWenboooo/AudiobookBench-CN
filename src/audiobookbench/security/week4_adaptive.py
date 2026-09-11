"""Fail-closed control plane for the frozen Week4 A0 adaptive red-team study.

This module never loads F5, AISHELL-3, or a real D0 backend.  It accepts only a
frozen spec, an authorization already validated by the future formal runner, and
a narrow detector callable.  Its tests use TEST_ONLY waveforms exclusively.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

import numpy as np


PROTOCOL = "WEEK4_ADAPTIVE_RED_TEAM_A0"
MAX_ADAPTIVE_D0_QUERIES_PER_CASE = 40
MAX_DETECTOR_QUERIES_PER_CASE = MAX_ADAPTIVE_D0_QUERIES_PER_CASE  # compatibility name
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260911
MIN_FINITE_BOOTSTRAPS = 1900
BOOTSTRAP_ALPHA = 0.05
ALLOWED_SPLITS = ("dev", "validation", "held_out")
HELD_OUT_SPLIT = "held_out"
SCORE_DIRECTION = "higher_is_more_anomalous"
STATIC_PHASE = "static_baseline"
ADAPTIVE_PHASE = "adaptive_search"
TUNING_PHASE = "tuning"
SEARCH_PHASES = frozenset({ADAPTIVE_PHASE, TUNING_PHASE})
FAILURE_CLASSES = frozenset({
    "infrastructure_transient", "infrastructure_terminal", "candidate_invalid",
    "authorization_failure", "query_budget_violation", "data_identity_failure",
    "detector_runtime_failure", "ledger_integrity_failure",
})
CANONICAL_CONFIG_SCHEMA = Path(__file__).resolve().parents[3] / "configs" / "week4_adaptive_red_team.schema.json"


class Week4ContractError(RuntimeError):
    """Base class for fail-closed Week4 contract violations."""


class AuthorizationError(Week4ContractError):
    pass


class QueryBudgetExceeded(Week4ContractError):
    pass


class SplitProtectionError(Week4ContractError):
    pass


class FreezeViolation(Week4ContractError):
    pass


class LedgerError(Week4ContractError):
    pass


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Week4ContractError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise Week4ContractError(f"{field} must be finite")
    return result


def _case_seed(seed: int, case_id: str, purpose: str) -> int:
    digest = hashlib.sha256(f"{seed}|{case_id}|{purpose}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


@dataclass(frozen=True)
class FrozenWindowSpec:
    """The only window information permitted to cross the detector boundary."""

    name: str
    window_samples: int
    hop_samples: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FrozenWindowSpec":
        if not isinstance(value, Mapping):
            raise Week4ContractError("window_spec must be a mapping")
        name = value.get("name")
        if not isinstance(name, str) or not name:
            raise Week4ContractError("window_spec.name is required")
        try:
            window, hop = int(value["window_samples"]), int(value["hop_samples"])
        except (KeyError, TypeError, ValueError) as exc:
            raise Week4ContractError("window_spec sample fields are required") from exc
        if window <= 0 or hop <= 0:
            raise Week4ContractError("window_spec sample fields must be positive")
        return cls(name, window, hop)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "window_samples": self.window_samples, "hop_samples": self.hop_samples}


@dataclass(frozen=True)
class FrozenAttackSpec:
    """Immutable executable subset of the canonical Week4 preregistration."""

    run_id: str
    parameter_bounds: Mapping[str, tuple[float, float]]
    parameter_defaults: Mapping[str, float]
    parameter_resolution: Mapping[str, float]
    window_spec: FrozenWindowSpec
    search_population_size: int
    search_generations: int
    search_elite_count: int
    search_mutation_scale_steps: int
    search_seed: int
    objective_name: str
    objective_direction: str
    score_direction: str = SCORE_DIRECTION
    protocol: str = PROTOCOL
    splits: tuple[str, ...] = ALLOWED_SPLITS
    max_adaptive_queries_per_case: int = MAX_ADAPTIVE_D0_QUERIES_PER_CASE
    bootstrap_n: int = BOOTSTRAP_N
    bootstrap_seed: int = BOOTSTRAP_SEED
    min_finite_bootstraps: int = MIN_FINITE_BOOTSTRAPS

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FrozenAttackSpec":
        if not isinstance(value, Mapping) or value.get("protocol") != PROTOCOL:
            raise Week4ContractError("Week4 protocol identifier mismatch")
        run_id = value.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise Week4ContractError("frozen Week4 run_id is required")
        raw_bounds = value.get("parameter_bounds")
        raw_defaults = value.get("parameter_defaults")
        raw_resolution = value.get("parameter_resolution")
        if not isinstance(raw_bounds, Mapping) or not isinstance(raw_defaults, Mapping) or not isinstance(raw_resolution, Mapping):
            raise Week4ContractError("frozen parameter bounds/defaults/resolution are required")
        if not raw_bounds or set(raw_bounds) != set(raw_defaults) or set(raw_bounds) != set(raw_resolution):
            raise Week4ContractError("frozen parameter definitions must have identical non-empty keys")
        bounds: dict[str, tuple[float, float]] = {}
        defaults: dict[str, float] = {}
        resolutions: dict[str, float] = {}
        for name in sorted(raw_bounds):
            raw = raw_bounds[name]
            if not isinstance(name, str) or not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or len(raw) != 2:
                raise Week4ContractError(f"parameter bound must be [minimum, maximum]: {name}")
            lo, hi = _finite_number(raw[0], f"parameter_bounds.{name}[0]"), _finite_number(raw[1], f"parameter_bounds.{name}[1]")
            default, resolution = _finite_number(raw_defaults[name], f"parameter_defaults.{name}"), _finite_number(raw_resolution[name], f"parameter_resolution.{name}")
            if lo > hi or resolution <= 0 or not lo <= default <= hi:
                raise Week4ContractError(f"invalid frozen parameter definition: {name}")
            steps = (hi - lo) / resolution
            default_steps = (default - lo) / resolution
            if not math.isclose(steps, round(steps), abs_tol=1e-9) or not math.isclose(default_steps, round(default_steps), abs_tol=1e-9):
                raise Week4ContractError(f"parameter bounds/default must lie on frozen resolution grid: {name}")
            bounds[name], defaults[name], resolutions[name] = (lo, hi), default, resolution
        if tuple(value.get("splits", ())) != ALLOWED_SPLITS:
            raise Week4ContractError("Week4 split set is frozen to dev/validation/held_out")
        if value.get("score_direction") != SCORE_DIRECTION:
            raise Week4ContractError("Week4 score direction is frozen")
        fixed = {
            "max_adaptive_d0_queries_per_case": MAX_ADAPTIVE_D0_QUERIES_PER_CASE,
            "bootstrap_n": BOOTSTRAP_N,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "min_finite_bootstraps": MIN_FINITE_BOOTSTRAPS,
        }
        for field, expected in fixed.items():
            if value.get(field) != expected:
                raise Week4ContractError(f"{field} is frozen and cannot be overridden")
        search = value.get("search_algorithm")
        if not isinstance(search, Mapping):
            raise Week4ContractError("frozen search_algorithm is required")
        expected_search = {
            "population_size": 8, "generations": 5, "elite_count": 1,
            "mutation_scale_steps": 1, "total_max_queries": MAX_ADAPTIVE_D0_QUERIES_PER_CASE,
            "initialization": "seeded_grid_without_replacement",
            "mutation": "seeded_symmetric_step_from_best_valid_candidate",
            "parent_selection": "lowest_objective_then_query_index",
            "duplicate_handling": "lexicographic_next_unseen_grid_point",
            "early_stopping": "none",
            "rng": "numpy_pcg64_seed_plus_case_sha256",
        }
        if any(search.get(key) != expected for key, expected in expected_search.items()):
            raise Week4ContractError("search_algorithm differs from the frozen Week4 definition")
        seed = search.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
            raise Week4ContractError("search_algorithm.seed must be a non-negative integer")
        if expected_search["population_size"] * expected_search["generations"] != MAX_ADAPTIVE_D0_QUERIES_PER_CASE:
            raise Week4ContractError("frozen search does not exhaust frozen query budget")
        objective = value.get("objective")
        if not isinstance(objective, Mapping) or objective.get("direction") != "minimize":
            raise Week4ContractError("frozen attacker objective must minimize")
        objective_name = objective.get("name")
        if not isinstance(objective_name, str) or not objective_name:
            raise Week4ContractError("frozen attacker objective name is required")
        return cls(
            run_id=run_id, parameter_bounds=MappingProxyType(bounds), parameter_defaults=MappingProxyType(defaults),
            parameter_resolution=MappingProxyType(resolutions), window_spec=FrozenWindowSpec.from_mapping(value.get("window_spec", {})),
            search_population_size=8, search_generations=5, search_elite_count=1,
            search_mutation_scale_steps=1, search_seed=seed, objective_name=objective_name,
            objective_direction="minimize",
        )

    @classmethod
    def from_path(cls, path: Path) -> "FrozenAttackSpec":
        try:
            if path.suffix.lower() in {".yaml", ".yml"}:
                import yaml
                value = yaml.safe_load(path.read_text(encoding="utf-8"))
            else:
                value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, ImportError) as exc:
            raise Week4ContractError("frozen Week4 spec cannot be loaded") from exc
        try:
            import jsonschema
        except ImportError as exc:
            raise Week4ContractError("canonical Week4 schema validator is unavailable") from exc
        try:
            schema = json.loads(CANONICAL_CONFIG_SCHEMA.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(value)
        except (OSError, ValueError, jsonschema.exceptions.SchemaError, jsonschema.exceptions.ValidationError) as exc:
            raise Week4ContractError("canonical Week4 config fails schema validation") from exc
        return cls.from_mapping(value)

    def as_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol, "run_id": self.run_id,
            "parameter_bounds": {key: list(value) for key, value in sorted(self.parameter_bounds.items())},
            "parameter_defaults": dict(sorted(self.parameter_defaults.items())),
            "parameter_resolution": dict(sorted(self.parameter_resolution.items())),
            "window_spec": self.window_spec.as_dict(), "score_direction": self.score_direction,
            "splits": list(self.splits), "max_adaptive_d0_queries_per_case": self.max_adaptive_queries_per_case,
            "bootstrap_n": self.bootstrap_n, "bootstrap_seed": self.bootstrap_seed,
            "min_finite_bootstraps": self.min_finite_bootstraps,
            "search_algorithm": {
                "population_size": self.search_population_size, "generations": self.search_generations,
                "elite_count": self.search_elite_count, "mutation_scale_steps": self.search_mutation_scale_steps,
                "total_max_queries": self.max_adaptive_queries_per_case, "seed": self.search_seed,
                "initialization": "seeded_grid_without_replacement",
                "mutation": "seeded_symmetric_step_from_best_valid_candidate",
                "parent_selection": "lowest_objective_then_query_index",
                "duplicate_handling": "lexicographic_next_unseen_grid_point", "early_stopping": "none",
                "rng": "numpy_pcg64_seed_plus_case_sha256",
            },
            "objective": {"name": self.objective_name, "direction": self.objective_direction},
        }

    def sha256(self) -> str:
        return sha256_bytes(_canonical_json(self.as_dict()))


def a0_freeze_sha256(spec: FrozenAttackSpec, method: str = "A0") -> str:
    if method != "A0":
        raise FreezeViolation("only the frozen A0 method is permitted")
    return sha256_bytes(_canonical_json({"method": method, "spec_sha256": spec.sha256()}))


def validate_authorization(authorization: Mapping[str, Any] | None, *, spec: FrozenAttackSpec, run_id: str, split: str) -> None:
    """Validate authorization before candidate construction or detector runtime."""
    if not isinstance(authorization, Mapping):
        raise AuthorizationError("active Week4 authorization is missing")
    required = ("protocol", "authorization_status", "run_id", "split", "spec_sha256", "a0_freeze_sha256", "ready")
    missing = [field for field in required if field not in authorization]
    if missing:
        raise AuthorizationError(f"authorization fields missing: {missing}")
    if authorization["protocol"] != PROTOCOL or authorization["authorization_status"] != "ACTIVE" or authorization["ready"] is not True:
        raise AuthorizationError("authorization is not an active ready Week4 artifact")
    if authorization["run_id"] != run_id or run_id != spec.run_id or authorization["split"] != split:
        raise AuthorizationError("authorization run_id or split mismatch")
    if str(authorization["spec_sha256"]).upper() != spec.sha256():
        raise AuthorizationError("frozen Week4 spec hash mismatch")
    if str(authorization["a0_freeze_sha256"]).upper() != a0_freeze_sha256(spec):
        raise AuthorizationError("authorization/A0 freeze hash mismatch")


def _record_hash(record: Mapping[str, Any]) -> str:
    body = dict(record); body.pop("record_sha256", None)
    return sha256_bytes(_canonical_json(body))


class CandidateLedger:
    """Append-only, hash-chained JSONL ledger: exactly one row per candidate."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise LedgerError("candidate ledger cannot be read") from exc
        records: list[dict[str, Any]] = []
        candidate_ids: set[str] = set(); previous = ""
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                raise LedgerError(f"blank line in candidate ledger at {line_number}")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerError(f"malformed candidate ledger row {line_number}") from exc
            if not isinstance(record, dict) or record.get("ledger_index") != line_number - 1:
                raise LedgerError("candidate ledger is not append-contiguous")
            if record.get("previous_record_sha256", "") != previous or record.get("record_sha256") != _record_hash(record):
                raise LedgerError("candidate ledger hash chain is broken")
            candidate_id = record.get("candidate_id")
            if not isinstance(candidate_id, str) or not candidate_id or candidate_id in candidate_ids:
                raise LedgerError("candidate_id must be present and unique")
            candidate_ids.add(candidate_id); previous = record["record_sha256"]; records.append(record)
        return records

    def append(self, record: Mapping[str, Any]) -> dict[str, Any]:
        existing = self.records(); candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id or any(row["candidate_id"] == candidate_id for row in existing):
            raise LedgerError("candidate_id is missing or already exists")
        body = dict(record)
        body["ledger_index"] = len(existing)
        body["previous_record_sha256"] = existing[-1]["record_sha256"] if existing else ""
        body["record_sha256"] = _record_hash(body)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8", newline="") as stream:
                stream.write(json.dumps(body, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
                stream.flush()
        except (OSError, ValueError) as exc:
            raise LedgerError("candidate ledger append failed") from exc
        return body


@dataclass(frozen=True)
class DetectorQuery:
    """Narrow reference-free D0 request: waveform, sample rate, frozen windows."""

    waveform: np.ndarray
    sample_rate: int
    window_spec: FrozenWindowSpec


def _normalise_params(params: Mapping[str, Any], spec: FrozenAttackSpec) -> dict[str, float]:
    if not isinstance(params, Mapping) or set(params) != set(spec.parameter_bounds):
        raise Week4ContractError("candidate parameter names do not match frozen specification")
    normalised: dict[str, float] = {}
    for name in sorted(spec.parameter_bounds):
        lo, hi = spec.parameter_bounds[name]
        value, resolution = _finite_number(params[name], f"candidate.{name}"), spec.parameter_resolution[name]
        if not lo <= value <= hi or not math.isclose((value - lo) / resolution, round((value - lo) / resolution), abs_tol=1e-9):
            raise Week4ContractError(f"candidate parameter violates frozen grid: {name}")
        normalised[name] = value
    return normalised


class A0AttackController:
    """Deterministic 8x5 A0 controller whose next proposal depends on D0 history."""

    def __init__(self, *, spec: FrozenAttackSpec, authorization: Mapping[str, Any] | None, case_id: str, split: str, ledger: CandidateLedger, detector: Callable[[DetectorQuery], float]):
        if not case_id or split not in ALLOWED_SPLITS or not callable(detector):
            raise Week4ContractError("case_id, frozen split, and detector callable are required")
        self.spec, self.authorization, self.case_id, self.split, self.ledger, self._detector = spec, authorization, case_id, split, ledger, detector
        self._method, self._freeze_hash = "A0", a0_freeze_sha256(spec)

    @property
    def a0_freeze_sha256(self) -> str:
        return self._freeze_hash

    def freeze(self) -> str:
        if a0_freeze_sha256(self.spec, self._method) != self._freeze_hash:
            raise FreezeViolation("A0 method/spec changed after freeze")
        return self._freeze_hash

    def set_method(self, method: str) -> None:
        if method != self._method:
            raise FreezeViolation("A0 method is frozen")

    def _gate(self, phase: str) -> None:
        validate_authorization(self.authorization, spec=self.spec, run_id=self.spec.run_id, split=self.split)
        if self.split not in self.spec.splits:
            raise SplitProtectionError("split is not in frozen split set")
        if phase == TUNING_PHASE and self.split == HELD_OUT_SPLIT:
            raise SplitProtectionError("held-out cases cannot be used for tuning")
        if phase not in {STATIC_PHASE, ADAPTIVE_PHASE, TUNING_PHASE}:
            raise Week4ContractError("unknown candidate phase")
        self.freeze()

    def _rows(self) -> list[dict[str, Any]]:
        return [row for row in self.ledger.records() if row.get("paired_case_id") == self.case_id and row.get("run_id") == self.spec.run_id]

    def _adaptive_query_count(self) -> int:
        return sum(row.get("detector_query") is True and row.get("phase") == ADAPTIVE_PHASE for row in self._rows())

    def _static_query_count(self) -> int:
        return sum(row.get("detector_query") is True and row.get("phase") == STATIC_PHASE for row in self._rows())

    def _new_candidate_id(self, phase: str) -> str:
        return f"{self.case_id}:{phase}:{len(self.ledger.records()):06d}"

    def accounting(self) -> dict[str, Any]:
        return {"adaptive_detector_queries": self._adaptive_query_count(), "static_baseline_detector_queries": self._static_query_count(), "max_adaptive_detector_queries": MAX_ADAPTIVE_D0_QUERIES_PER_CASE}

    def _grid(self, name: str) -> list[float]:
        lo, hi = self.spec.parameter_bounds[name]; resolution = self.spec.parameter_resolution[name]
        return [float(lo + step * resolution) for step in range(int(round((hi - lo) / resolution)) + 1)]

    def _seen_parameter_tuples(self) -> set[tuple[tuple[str, float], ...]]:
        out: set[tuple[tuple[str, float], ...]] = set()
        for row in self._rows():
            params = row.get("params")
            if isinstance(params, Mapping) and set(params) == set(self.spec.parameter_bounds):
                out.add(tuple((name, float(params[name])) for name in sorted(params)))
        return out

    def _deduplicate(self, candidate: Mapping[str, float]) -> dict[str, float]:
        seen = self._seen_parameter_tuples(); normalised = _normalise_params(candidate, self.spec)
        key = tuple((name, normalised[name]) for name in sorted(normalised))
        if key not in seen:
            return normalised
        names, grids = sorted(self.spec.parameter_bounds), [self._grid(name) for name in sorted(self.spec.parameter_bounds)]
        for values in np.ndindex(*(len(grid) for grid in grids)):
            replacement = {name: grids[index][values[index]] for index, name in enumerate(names)}
            if tuple((name, replacement[name]) for name in names) not in seen:
                return replacement
        raise Week4ContractError("frozen candidate grid is exhausted; no duplicate retry is allowed")

    def _initial_proposal(self, query_index: int) -> dict[str, float]:
        rng = np.random.default_rng(_case_seed(self.spec.search_seed, self.case_id, "generation_0"))
        proposal: dict[str, float] = {}
        for _ in range(query_index):
            proposal = {name: grid[int(rng.integers(0, len(grid)))] for name, grid in ((n, self._grid(n)) for n in sorted(self.spec.parameter_bounds))}
        return self._deduplicate(proposal)

    def _best_valid(self) -> Mapping[str, Any]:
        valid = [row for row in self._rows() if row.get("phase") == ADAPTIVE_PHASE and row.get("valid") is True and isinstance(row.get("score"), (int, float))]
        if not valid:
            raise Week4ContractError("adaptive mutation requires a valid prior detector score")
        return min(valid, key=lambda row: (float(row["score"]), int(row.get("query_index", 0)), str(row["candidate_id"])))

    def next_candidate(self) -> dict[str, float]:
        """Return the one frozen next A0 proposal; no detector invocation occurs here."""
        self._gate(ADAPTIVE_PHASE)
        count = self._adaptive_query_count()
        if count >= MAX_ADAPTIVE_D0_QUERIES_PER_CASE:
            raise QueryBudgetExceeded("the 41st adaptive D0 query is rejected fail-closed")
        query_index = count + 1
        if count < self.spec.search_population_size:
            return self._initial_proposal(query_index)
        best = self._best_valid()
        generation, within_generation = count // self.spec.search_population_size, count % self.spec.search_population_size
        rng = np.random.default_rng(_case_seed(self.spec.search_seed, self.case_id, f"generation_{generation}_slot_{within_generation}"))
        proposal: dict[str, float] = {}
        for name in sorted(self.spec.parameter_bounds):
            grid, current = self._grid(name), float(best["params"][name])
            current_index = min(range(len(grid)), key=lambda index: abs(grid[index] - current))
            sign = -1 if int(rng.integers(0, 2)) == 0 else 1
            proposal[name] = grid[min(max(current_index + sign * self.spec.search_mutation_scale_steps, 0), len(grid) - 1)]
        return self._deduplicate(proposal)

    def _append_invalid(self, candidate_id: str, phase: str, params: Mapping[str, Any] | None, reason: str, *, detector_query: bool, query_index: int) -> dict[str, Any]:
        return self.ledger.append({"recorded_at": datetime.now(timezone.utc).isoformat(), "candidate_id": candidate_id, "paired_case_id": self.case_id, "run_id": self.spec.run_id, "split": self.split, "phase": phase, "detector_query": detector_query, "query_index": query_index, "params": dict(params) if params is not None else None, "status": "INVALID", "valid": False, "failure_class": "candidate_invalid" if not detector_query else "detector_runtime_failure", "invalid_reason": reason})

    def evaluate_candidate(self, *, waveform: np.ndarray, sample_rate: int, params: Mapping[str, Any], phase: str = ADAPTIVE_PHASE) -> dict[str, Any]:
        """Evaluate exactly the next A0 proposal or the one A_STATIC comparator."""
        self._gate(phase); candidate_id = self._new_candidate_id(phase)
        if phase == ADAPTIVE_PHASE:
            if self._adaptive_query_count() >= MAX_ADAPTIVE_D0_QUERIES_PER_CASE:
                self._append_invalid(candidate_id, phase, params, "MAX_ADAPTIVE_D0_QUERIES_PER_CASE exceeded", detector_query=False, query_index=self._adaptive_query_count() + 1)
                raise QueryBudgetExceeded("the 41st adaptive D0 query is rejected fail-closed")
            expected = self.next_candidate()
            try:
                normalised = _normalise_params(params, self.spec)
            except Week4ContractError as exc:
                return self._append_invalid(candidate_id, phase, params, str(exc), detector_query=False, query_index=self._adaptive_query_count() + 1)
            if normalised != expected:
                raise FreezeViolation("adaptive candidate differs from deterministic frozen proposal")
            query_index = self._adaptive_query_count() + 1
        elif phase == STATIC_PHASE:
            if self._static_query_count() >= 1:
                raise QueryBudgetExceeded("A_STATIC permits exactly one separately-accounted D0 query per case")
            normalised = _normalise_params(params, self.spec)
            if normalised != dict(self.spec.parameter_defaults):
                raise FreezeViolation("A_STATIC parameters differ from frozen deterministic defaults")
            query_index = self._static_query_count() + 1
        else:
            raise Week4ContractError("tuning is governance-only and may not invoke D0")
        array = np.asarray(waveform, dtype=np.float64)
        if array.ndim != 1 or not np.isfinite(array).all() or int(sample_rate) != 16000:
            return self._append_invalid(candidate_id, phase, normalised, "invalid detector waveform", detector_query=False, query_index=query_index)
        try:
            score = float(self._detector(DetectorQuery(array.copy(), int(sample_rate), self.spec.window_spec)))
            if not math.isfinite(score):
                raise ValueError("detector score is non-finite")
        except Exception as exc:
            self._append_invalid(candidate_id, phase, normalised, f"detector_failure:{type(exc).__name__}:{exc}", detector_query=True, query_index=query_index)
            raise
        return self.ledger.append({"recorded_at": datetime.now(timezone.utc).isoformat(), "candidate_id": candidate_id, "paired_case_id": self.case_id, "run_id": self.spec.run_id, "split": self.split, "phase": phase, "detector_query": True, "query_index": query_index, "params": normalised, "score": score, "objective": self.spec.objective_name, "objective_direction": self.spec.objective_direction, "status": "VALID", "valid": True})


def paired_case_bootstrap(case_values: Mapping[str, Any] | Sequence[Any], *, statistic: Callable[[np.ndarray], float] = np.mean, n: int = BOOTSTRAP_N, seed: int = BOOTSTRAP_SEED, min_finite: int = MIN_FINITE_BOOTSTRAPS, alpha: float = BOOTSTRAP_ALPHA) -> dict[str, Any]:
    """Frozen paired-case percentile bootstrap; windows/frames are never sampled."""
    if n != BOOTSTRAP_N or seed != BOOTSTRAP_SEED or min_finite != MIN_FINITE_BOOTSTRAPS or alpha != BOOTSTRAP_ALPHA:
        raise Week4ContractError("Week4 bootstrap constants are frozen")
    items = list(case_values.items()) if isinstance(case_values, Mapping) else [(f"case_{index:04d}", value) for index, value in enumerate(case_values)]
    if not items:
        raise Week4ContractError("at least one complete case is required")
    case_stats: list[float] = []
    for _, value in items:
        array = np.asarray(value, dtype=float)
        finite = np.asarray([float(array)]) if array.ndim == 0 else array[np.isfinite(array)]
        case_stats.append(float(statistic(finite)) if finite.size else float("nan"))
    values = np.asarray(case_stats, dtype=float)
    if not np.isfinite(values).all():
        raise Week4ContractError("paired bootstrap requires finite complete-case statistics")
    rng = np.random.default_rng(seed)
    draws = np.asarray([float(statistic(rng.choice(values, size=values.size, replace=True))) for _ in range(n)], dtype=float)
    finite_count = int(np.isfinite(draws).sum())
    if finite_count < min_finite:
        raise Week4ContractError("finite paired-case bootstrap draws are below frozen threshold")
    low, high = np.quantile(draws[np.isfinite(draws)], [alpha / 2.0, 1.0 - alpha / 2.0])
    return {"unit": "paired_case_id", "requested": n, "finite": finite_count, "undefined": n - finite_count, "undefined_reason_counts": {} if finite_count == n else {"non_finite_statistic": n - finite_count}, "seed": seed, "confidence_level": 1.0 - alpha, "ci_percentile": [float(low), float(high)], "observed": float(statistic(values))}
