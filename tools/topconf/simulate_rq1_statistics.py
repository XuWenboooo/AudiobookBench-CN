"""Synthetic-only statistical planning for the RQ1 pre-freeze lane.

This module deliberately generates no project audio and never imports a model
or research dataset. It compares bootstrap unit choices under a synthetic
speaker -> source -> mechanism hierarchy. The output is planning sensitivity,
not a power calculation or a confirmatory result.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable

import numpy as np


STRATEGIES = (
    "case_level",
    "speaker_cluster",
    "hierarchical_speaker_case",
    "paired_source",
)


@dataclass(frozen=True)
class SyntheticPopulation:
    """One synthetic population of paired source/condition deltas."""

    source_ids: np.ndarray
    speaker_ids: np.ndarray
    mechanism_ids: np.ndarray
    deltas: np.ndarray
    expected_effect: float


def make_synthetic_population(
    n_sources: int,
    n_speakers: int,
    n_mechanisms: int,
    speaker_rho: float,
    effect: float,
    seed: int,
) -> SyntheticPopulation:
    """Generate a fully synthetic hierarchical paired population.

    Each source has one synthetic delta for every mechanism. The expected
    super-population effect is ``effect``; mechanism offsets are symmetric and
    therefore do not encode a directional result. ``speaker_rho`` controls the
    relative speaker-cluster component and is a sensitivity parameter, not an
    estimate from project data.
    """

    if n_sources <= 0 or n_speakers <= 0 or n_mechanisms <= 0:
        raise ValueError("population sizes must be positive")
    if n_speakers > n_sources:
        raise ValueError("n_speakers cannot exceed n_sources")
    if not 0.0 <= speaker_rho <= 1.0:
        raise ValueError("speaker_rho must be in [0, 1]")

    rng = np.random.default_rng(seed)
    source_ids = np.repeat(np.arange(n_sources, dtype=int), n_mechanisms)
    mechanism_ids = np.tile(np.arange(n_mechanisms, dtype=int), n_sources)

    # A shuffled balanced allocation avoids making speaker identity a source
    # ordering artefact while retaining a source-disjoint hierarchy.
    speaker_assignment = np.resize(np.arange(n_speakers, dtype=int), n_sources)
    rng.shuffle(speaker_assignment)
    speaker_ids = np.repeat(speaker_assignment, n_mechanisms)

    speaker_effects = rng.normal(0.0, 0.35 * np.sqrt(speaker_rho), n_speakers)
    source_effects = rng.normal(0.0, 0.35 * np.sqrt(1.0 - speaker_rho), n_sources)
    residual = rng.normal(0.0, 0.65, n_sources * n_mechanisms)
    mechanism_offsets = np.linspace(-0.20, 0.20, n_mechanisms, dtype=float)
    mechanism_offsets -= mechanism_offsets.mean()

    deltas = (
        float(effect)
        + speaker_effects[speaker_ids]
        + source_effects[source_ids]
        + mechanism_offsets[mechanism_ids]
        + residual
    )
    return SyntheticPopulation(
        source_ids=source_ids,
        speaker_ids=speaker_ids,
        mechanism_ids=mechanism_ids,
        deltas=deltas,
        expected_effect=float(effect),
    )


def _indices_by_group(values: np.ndarray) -> dict[int, np.ndarray]:
    return {
        int(group): np.flatnonzero(values == group)
        for group in np.unique(values)
    }


def _resample_indices(
    population: SyntheticPopulation,
    strategy: str,
    rng: np.random.Generator,
) -> np.ndarray:
    """Return a bootstrap sample index vector for one strategy."""

    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy: {strategy}")

    n = population.deltas.size
    if strategy == "case_level":
        # Intentionally treats every source x mechanism row as independent.
        return rng.integers(0, n, size=n)

    source_groups = _indices_by_group(population.source_ids)
    speaker_groups = _indices_by_group(population.speaker_ids)

    if strategy == "paired_source":
        # Resample source units, retaining every mechanism row in each source.
        source_keys = np.array(sorted(source_groups), dtype=int)
        sampled = rng.choice(source_keys, size=source_keys.size, replace=True)
        return np.concatenate([source_groups[int(source)] for source in sampled])

    speaker_keys = np.array(sorted(speaker_groups), dtype=int)
    sampled_speakers = rng.choice(speaker_keys, size=speaker_keys.size, replace=True)

    if strategy == "speaker_cluster":
        # Resample complete speaker clusters, retaining all their source rows.
        return np.concatenate([speaker_groups[int(speaker)] for speaker in sampled_speakers])

    # Hierarchical bootstrap: resample speakers, then resample the same number
    # of source units within each sampled speaker, retaining all mechanisms.
    source_by_speaker: dict[int, np.ndarray] = {}
    for speaker, rows in speaker_groups.items():
        source_by_speaker[speaker] = np.unique(population.source_ids[rows])
    hierarchical_rows: list[np.ndarray] = []
    for speaker in sampled_speakers:
        sources = source_by_speaker[int(speaker)]
        sampled_sources = rng.choice(sources, size=sources.size, replace=True)
        for source in sampled_sources:
            hierarchical_rows.append(source_groups[int(source)])
    return np.concatenate(hierarchical_rows)


def bootstrap_ci(
    population: SyntheticPopulation,
    strategy: str,
    n_bootstrap: int,
    seed: int,
    alpha: float = 0.05,
) -> dict[str, float]:
    """Compute one percentile bootstrap interval for a synthetic population."""

    if n_bootstrap < 20:
        raise ValueError("n_bootstrap must be at least 20 for a planning interval")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")

    rng = np.random.default_rng(seed)
    estimates = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        rows = _resample_indices(population, strategy, rng)
        estimates[index] = float(np.mean(population.deltas[rows]))

    lower, upper = np.quantile(estimates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return {
        "estimate": float(np.mean(population.deltas)),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "ci_width": float(upper - lower),
        "bootstrap_sd": float(np.std(estimates, ddof=1)),
    }


def run_simulation(
    sources: Iterable[int] = (200, 300, 400, 500, 600),
    speakers: Iterable[int] = (50, 75, 100, 125, 150),
    mechanisms: Iterable[int] = (3, 4),
    speaker_rhos: Iterable[float] = (0.0, 0.3, 0.6, 0.8),
    effects: Iterable[float] = (0.0, 0.05, 0.20, 0.50, 1.0),
    n_replicates: int = 100,
    n_bootstrap: int = 500,
    seed: int = 20260913,
) -> dict[str, object]:
    """Run the synthetic design-sensitivity grid.

    The full default grid is intentionally configurable because it can be
    expensive. A report may use a reduced, transparently recorded grid while
    retaining the broader candidate ranges for later sensitivity work.
    """

    source_values = tuple(int(value) for value in sources)
    speaker_values = tuple(int(value) for value in speakers)
    mechanism_values = tuple(int(value) for value in mechanisms)
    rho_values = tuple(float(value) for value in speaker_rhos)
    effect_values = tuple(float(value) for value in effects)
    if n_replicates <= 0:
        raise ValueError("n_replicates must be positive")

    results: list[dict[str, object]] = []
    base_seed = int(seed)
    cell = 0
    for n_sources in source_values:
        for n_speakers in speaker_values:
            if n_speakers > n_sources:
                continue
            for n_mechanisms in mechanism_values:
                for speaker_rho in rho_values:
                    for effect in effect_values:
                        per_strategy: dict[str, list[dict[str, float]]] = {
                            strategy: [] for strategy in STRATEGIES
                        }
                        for replicate in range(n_replicates):
                            population = make_synthetic_population(
                                n_sources=n_sources,
                                n_speakers=n_speakers,
                                n_mechanisms=n_mechanisms,
                                speaker_rho=speaker_rho,
                                effect=effect,
                                seed=base_seed + cell * 100_000 + replicate,
                            )
                            for offset, strategy in enumerate(STRATEGIES):
                                summary = bootstrap_ci(
                                    population,
                                    strategy=strategy,
                                    n_bootstrap=n_bootstrap,
                                    seed=base_seed + cell * 100_000 + replicate * 100 + offset,
                                )
                                per_strategy[strategy].append(summary)

                        strategy_summary: dict[str, dict[str, float]] = {}
                        for strategy, rows in per_strategy.items():
                            estimates = np.array([row["estimate"] for row in rows])
                            widths = np.array([row["ci_width"] for row in rows])
                            covered = np.array(
                                [
                                    row["ci_lower"] <= effect <= row["ci_upper"]
                                    for row in rows
                                ],
                                dtype=float,
                            )
                            strategy_summary[strategy] = {
                                "coverage": float(np.mean(covered)),
                                "mean_ci_width": float(np.mean(widths)),
                                "ci_width_sd": float(np.std(widths, ddof=1))
                                if len(widths) > 1
                                else 0.0,
                                "mean_estimate": float(np.mean(estimates)),
                                "estimate_sd": float(np.std(estimates, ddof=1))
                                if len(estimates) > 1
                                else 0.0,
                                "mean_abs_bias": float(np.mean(np.abs(estimates - effect))),
                            }
                        results.append(
                            {
                                "n_sources": n_sources,
                                "n_speakers": n_speakers,
                                "n_mechanisms": n_mechanisms,
                                "speaker_rho": speaker_rho,
                                "synthetic_effect": effect,
                                "n_replicates": n_replicates,
                                "n_bootstrap": n_bootstrap,
                                "strategies": strategy_summary,
                            }
                        )
                        cell += 1

    return {
        "schema_version": "topconf.rq1.synthetic-statistics.v1",
        "data_source": "SYNTHETIC_ONLY",
        "scientific_runs_invoked": False,
        "level2_outcomes_accessed": False,
        "result_based_selection": False,
        "grid": {
            "sources": list(source_values),
            "speakers": list(speaker_values),
            "mechanisms": list(mechanism_values),
            "within_speaker_correlation": list(rho_values),
            "effects": list(effect_values),
        },
        "results": results,
    }


def _parse_list(text: str, cast):
    return tuple(cast(item.strip()) for item in text.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", default="200,300,400,500,600")
    parser.add_argument("--speakers", default="50,75,100,125,150")
    parser.add_argument("--mechanisms", default="3,4")
    parser.add_argument("--rhos", default="0,0.3,0.6,0.8")
    parser.add_argument("--effects", default="0,0.05,0.2,0.5,1.0")
    parser.add_argument("--n-replicates", type=int, default=100)
    parser.add_argument("--n-bootstrap", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260913)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()

    payload = run_simulation(
        sources=_parse_list(args.sources, int),
        speakers=_parse_list(args.speakers, int),
        mechanisms=_parse_list(args.mechanisms, int),
        speaker_rhos=_parse_list(args.rhos, float),
        effects=_parse_list(args.effects, float),
        n_replicates=args.n_replicates,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        from pathlib import Path

        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
