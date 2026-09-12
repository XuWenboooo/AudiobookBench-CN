"""Future Week4 formal entrypoint and zero-side-effect preflight.

The executable scientific path is intentionally gated behind a separately
issued active authorization.  This file's preflight performs only reads and
returns a validated context; it never imports F5, D0, torchaudio, or an
evaluator and never creates a run directory.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.security.week4_adaptive import FrozenAttackSpec  # noqa: E402
from audiobookbench.security.week4_authorization import (  # noqa: E402
    Week4AuthorizationError,
    sha256_file,
    validate_authorization_artifact,
)


class FormalRunBlocked(RuntimeError):
    """Raised before any scientific side effect can occur."""


CANONICAL_CONFIG = ROOT / "configs/week4_adaptive_red_team.yaml"
CANONICAL_POPULATION = ROOT / "data/manifests/week4_population_manifest.json"
CANONICAL_PREREG = ROOT / "research_assurance/WEEK4_ADAPTIVE_REDTEAM_PREREGISTRATION.md"
CANONICAL_RUN_BASE = "results/week4_adaptive_redteam_runs"
FROZEN_PREREGISTRATION_SHA256 = "6942358DFF60EBC042E06F9441436D2BCCAE43EA8A66C6BD6B891FAE345758C4"
FROZEN_CONFIG_SHA256 = "1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D"
FROZEN_POPULATION_SHA256 = "DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week4 formal preflight; scientific flags are not accepted")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    return parser.parse_args(argv)


def _canonical_path(path: Path) -> Path:
    return path.resolve()


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FormalRunBlocked(f"{label} cannot be loaded") from exc


def _require_frozen_hashes(config: Path, population: Path) -> None:
    """Verify scientific freezes before reading population or authorization state."""
    for label, path, expected in (
        ("preregistration", CANONICAL_PREREG, FROZEN_PREREGISTRATION_SHA256),
        ("canonical config", config, FROZEN_CONFIG_SHA256),
        ("population manifest", population, FROZEN_POPULATION_SHA256),
    ):
        if sha256_file(path) != expected:
            raise FormalRunBlocked(f"frozen {label} hash mismatch")


def _validate_population(path: Path) -> dict[str, Any]:
    population = _load_json(path, "population manifest")
    if population.get("status") != "FINALIZED":
        raise FormalRunBlocked("population manifest is not FINALIZED")
    if population.get("selection_seed") != 20260912 or population.get("selected_without_d0") is not True:
        raise FormalRunBlocked("population selection seed or D0-independence flag mismatch")
    if population.get("d0_invoked") is not False or population.get("d0_outcome_inspected") is not False:
        raise FormalRunBlocked("population manifest indicates D0 involvement")
    cases = population.get("selected_cases")
    if not isinstance(cases, list) or len(cases) != 48:
        raise FormalRunBlocked("population must contain exactly 48 selected cases")
    if population.get("split_counts") != {"dev": 24, "validation": 12, "held_out": 12}:
        raise FormalRunBlocked("population split counts must be 24/12/12")
    speakers = [row.get("speaker") for row in cases]
    if any(not isinstance(speaker, str) or not speaker for speaker in speakers) or len(set(speakers)) != 48:
        raise FormalRunBlocked("population speakers are not unique")
    if any(row.get("prior_week_overlap") is True for row in cases):
        raise FormalRunBlocked("population contains a prior Week1-3 speaker")
    required = {"source_audio_sha256", "reference_audio_sha256", "source_text_sha256", "reference_text_sha256", "source_path", "reference_path"}
    if any(not required.issubset(row) for row in cases):
        raise FormalRunBlocked("population case identity fields are incomplete")
    return population


def preflight(*, config: Path, population: Path, authorization: Path, runtime_root: Path) -> dict[str, Any]:
    """Read and validate every formal input without creating output."""
    if _canonical_path(config) != _canonical_path(CANONICAL_CONFIG):
        raise FormalRunBlocked("only the canonical Week4 config is accepted")
    if _canonical_path(population) != _canonical_path(CANONICAL_POPULATION):
        raise FormalRunBlocked("only the canonical finalized population is accepted")
    if not config.is_file() or not population.is_file() or not CANONICAL_PREREG.is_file():
        raise FormalRunBlocked("canonical Week4 inputs are missing")
    # Schema/spec precede every hash-bound input.  Frozen scientific hashes
    # precede population parsing and active-authorization validation.
    spec = FrozenAttackSpec.from_path(config)
    _require_frozen_hashes(config, population)
    selected = _validate_population(population)
    validated = validate_authorization_artifact(authorization, repo=ROOT, expected_run_id=spec.run_id, verify_f5_assets=True)
    expected_namespace = ROOT / Path(validated.output_namespace)
    runtime_root = _canonical_path(runtime_root)
    if runtime_root != expected_namespace:
        raise FormalRunBlocked("runtime root is not the authorization-bound output namespace")
    if runtime_root.exists():
        raise FormalRunBlocked("authorization-bound output namespace already exists")
    if spec.run_id != validated.run_id:
        raise FormalRunBlocked("formal config and authorization run_id mismatch")
    if sha256_file(config) != validated.source_sha256["canonical_config"]:
        raise FormalRunBlocked("canonical config hash mismatch")
    if sha256_file(population) != validated.source_sha256["population_manifest"]:
        raise FormalRunBlocked("population manifest hash mismatch")
    ledger_path = runtime_root / "accounting" / "candidate_ledger.jsonl"
    if ledger_path.exists():  # defensive: runtime_root is required to be new above.
        raise FormalRunBlocked("new formal namespace already contains accounting state")
    return {
        "status": "PASS",
        "mode": "VALIDATED_CONTEXT",
        "scientific_execution_enabled": False,
        "generation_invoked": False,
        "d0_invoked": False,
        "evaluator_invoked": False,
        "run_id": validated.run_id,
        "invocation_id": validated.invocation_id,
        "output_namespace": validated.output_namespace,
        "authorization_sha256": validated.artifact_sha256,
        "config_sha256": sha256_file(config),
        "population_manifest_sha256": sha256_file(population),
        "population_counts": selected["split_counts"],
        "accounting_ledger_path": str(ledger_path),
        "accounting_initialization_safe": True,
        "accounting_initialized": False,
        "runtime_permitted_by_external_authorization": True,
    }


def dispatch(*, context: dict[str, Any], population: Path, runtime_root: Path) -> dict[str, Any]:
    """The only real-execution dispatcher, reachable after successful preflight.

    Model imports occur inside the lazy factories, so `preflight` remains a
    strictly read-only authorization check.
    """
    from audiobookbench.security.week4_execution import execute_protocol, real_d0_backend, real_f5_generator
    spec = FrozenAttackSpec.from_path(CANONICAL_CONFIG)
    selected = _validate_population(population)
    return execute_protocol(cases=selected["selected_cases"], spec=spec, runtime_root=runtime_root,
                            f5_generator=real_f5_generator(), d0_backend=real_d0_backend())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        context = preflight(config=args.config, population=args.population, authorization=args.authorization, runtime_root=args.runtime_root)
        if args.preflight_only:
            print(json.dumps(context, ensure_ascii=False, sort_keys=True))
            return 0
        dispatch(context=context, population=args.population, runtime_root=args.runtime_root)
    except (FormalRunBlocked, Week4AuthorizationError, RuntimeError) as exc:
        raise SystemExit(f"WEEK4 FORMAL PATH BLOCKED: {exc}") from exc
    return 0


if __name__ == "__main__":
    main()
