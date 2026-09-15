"""Validate the single Phase4.8 V2-to-V3 rematerialization attempt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.materialization import (  # noqa: E402
    MaterializationValidationError,
    validate_level2_rematerialization_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    def load(name: str) -> dict:
        return json.loads((args.output_dir / name).read_text(encoding="utf-8"))

    try:
        parent = load("LEVEL2_RQ1_POPULATION_MANIFEST_V2.json")
        exclusion = load("LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json")
        ledger = load("LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json")
        result = validate_level2_rematerialization_plan(
            parent,
            exclusion,
            ledger,
            parent["reserve_records"],
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "BLOCKED_INSUFFICIENT_CLEAN_RESERVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
