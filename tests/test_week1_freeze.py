from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml


REPOSITORY = Path(__file__).resolve().parents[1]


def _runner_module():
    path = REPOSITORY / "experiments/week1_baseline/run.py"
    spec = importlib.util.spec_from_file_location("week1_runner", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_week1_required_artifacts_exist() -> None:
    required = [
        "config.yaml", "metrics.json", "metrics_summary.csv", "claims.md",
        "limitations.md", "failure_cases.csv", "run.log",
        "reproduction_manifest.json", "hashes.json",
    ]
    assert all((REPOSITORY / "results/week1" / name).is_file() for name in required)
    assert len(list((REPOSITORY / "results/week1/figures").glob("*.png"))) >= 5


def test_week1_hash_chain_verifies() -> None:
    result = _runner_module().verify_frozen_hashes(REPOSITORY)
    assert result["passed"] is True
    assert result["checked"] == 696
    assert not result["missing"] and not result["mismatches"]


def test_week1_freezes_positive_and_negative_results() -> None:
    metrics = json.loads((REPOSITORY / "results/week1/metrics.json").read_text(encoding="utf-8"))
    assert all(value < 0.5 for scale in metrics["day6a_test_full_auroc"].values() for value in scale.values())
    assert metrics["day6b_test_full"]["S2_B1b"]["A0"]["auroc"] > 0.89
    assert metrics["day6c"]["s1_test_c0_full"]["C0A"]["auroc"] < 0.5


def test_week1_config_is_read_only_and_portable() -> None:
    config = yaml.safe_load((REPOSITORY / "configs/week1.yaml").read_text(encoding="utf-8"))
    assert config["dataset"]["raw_access"] == "read_only"
    assert config["dataset"]["root_environment_variable"] == "AUDIOBOOKBENCH_DATASET_ROOT"
    assert config["reproduction"]["temporary_outputs_only"] is True
