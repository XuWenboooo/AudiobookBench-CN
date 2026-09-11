"""Fail-closed Week4 entry point.

This preparation-phase command deliberately exposes no scientific CLI options
and cannot execute F5 or D0.  The future formal runner must replace this guard
only after an independent readiness review and active authorization.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from audiobookbench.security.week4_adaptive import FrozenAttackSpec, Week4ContractError


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week4 fail-closed preparation scaffold", allow_abbrev=False)
    parser.add_argument("--config", type=Path, default=Path("configs/week4_adaptive_red_team.yaml"))
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--test-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    FrozenAttackSpec.from_path(args.config)
    if not args.test_only:
        raise RuntimeError("Week4 formal execution is disabled pending independent readiness review")
    if args.authorization is not None or args.runtime_root is not None:
        raise RuntimeError("TEST_ONLY scaffold does not accept authorization or runtime execution paths")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Week4ContractError as exc:
        raise SystemExit(f"Week4 frozen-config validation failed: {exc}")
