"""Build the frozen Week4 candidate population without any D0 call."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from audiobookbench.security.week4_population import build_aishell3_train_candidate_population, write_candidate_population_manifest


PRIOR_WEEK_SPEAKERS = frozenset({
    "SSB0005", "SSB0009", "SSB0011", "SSB0073", "SSB0139", "SSB0197",
    "SSB0261", "SSB0309", "SSB0342", "SSB0393", "SSB0434", "SSB1100",
})


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Week4 population manifest")
    parser.add_argument("--aishell-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/manifests/week4_population_manifest.json"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_aishell3_train_candidate_population(args.aishell_root, selection_seed=20260912, prior_week_speakers=set(PRIOR_WEEK_SPEAKERS))
    write_candidate_population_manifest(manifest, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
