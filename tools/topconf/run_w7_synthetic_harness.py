"""Synthetic fixture orchestration only; never accepts formal case paths."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.w7_synthetic_harness import SyntheticW7Harness  # noqa: E402

CONFIG = ROOT / "tests" / "topconf" / "fixtures" / "w7_synthetic_config_v1.json"
CASES = ROOT / "tests" / "topconf" / "fixtures" / "w7_synthetic_cases_v1.json"
KNOWN_CONFIG_SHA256 = "90950eaa38eea4479de97f4d412305cf3ed2182bbdffb82a8abca0667d7d2e7e"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="resolve schedule without loading audio or models")
    parser.add_argument("--all", action="store_true", help="execute all built-in synthetic fixtures and record terminal states")
    parser.add_argument("--case", default="SYNTH_SINGLE", help="one built-in SYNTH_ fixture for execution")
    args = parser.parse_args()
    fixtures = tuple(json.loads(CASES.read_text(encoding="utf-8")))
    harness = SyntheticW7Harness(CONFIG, expected_config_hash=KNOWN_CONFIG_SHA256,
                                 output_root=ROOT / "artifacts" / "w7_synthetic_harness")
    if args.dry_run:
        result = harness.dry_run(fixtures)
    elif args.all:
        result = harness.run_schedule(fixtures)
    else:
        matched = [item for item in fixtures if item["case_id"] == args.case]
        if len(matched) != 1:
            parser.error("--case must name exactly one built-in SYNTH_ fixture")
        result = harness.run(matched[0])
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
