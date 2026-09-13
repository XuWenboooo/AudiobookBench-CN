from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

TOOLS_DIR = Path(__file__).parents[2] / "tools" / "topconf"
sys.path.insert(0, str(TOOLS_DIR))

from simulate_rq1_statistics import (  # noqa: E402
    STRATEGIES,
    bootstrap_ci,
    make_synthetic_population,
    run_simulation,
)


def test_synthetic_population_is_hierarchical_and_finite():
    population = make_synthetic_population(20, 5, 3, 0.5, 0.2, seed=7)
    assert population.deltas.shape == (60,)
    assert np.isfinite(population.deltas).all()
    assert len(np.unique(population.source_ids)) == 20
    assert len(np.unique(population.speaker_ids)) == 5


def test_all_bootstrap_strategies_return_intervals():
    population = make_synthetic_population(30, 6, 3, 0.6, 0.0, seed=11)
    first = {}
    second = {}
    for strategy in STRATEGIES:
        first[strategy] = bootstrap_ci(population, strategy, 80, seed=19)
        second[strategy] = bootstrap_ci(population, strategy, 80, seed=19)
        assert first[strategy]["ci_lower"] <= first[strategy]["ci_upper"]
        assert first[strategy]["ci_width"] >= 0.0
    assert first == second


def test_small_grid_is_synthetic_only_and_records_strategies():
    payload = run_simulation(
        sources=(20,),
        speakers=(5,),
        mechanisms=(3,),
        speaker_rhos=(0.0, 0.7),
        effects=(0.0, 0.2),
        n_replicates=3,
        n_bootstrap=40,
        seed=23,
    )
    assert payload["data_source"] == "SYNTHETIC_ONLY"
    assert payload["scientific_runs_invoked"] is False
    assert payload["level2_outcomes_accessed"] is False
    assert len(payload["results"]) == 4
    for cell in payload["results"]:
        assert set(cell["strategies"]) == set(STRATEGIES)
        for summary in cell["strategies"].values():
            assert 0.0 <= summary["coverage"] <= 1.0
