"""CLI for fail-closed Level-2 case and lineage freshness validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.materialization import (
    FreshnessInsufficientEvidence,
    FreshnessValidationError,
    validate_level2_freshness,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("population", type=Path)
    parser.add_argument("freshness", type=Path)
    args = parser.parse_args()
    population = json.loads(args.population.read_text(encoding="utf-8"))
    freshness = json.loads(args.freshness.read_text(encoding="utf-8"))
    if freshness.get("schema_version") == "topconf.level2.freshness.v3":
        references = freshness.get("universe_references", {})
        universes = {}
        if isinstance(references, dict):
            for universe_id, reference in references.items():
                if not isinstance(reference, dict):
                    continue
                raw_path = reference.get("path")
                if not isinstance(raw_path, str):
                    continue
                path = Path(raw_path)
                if not path.is_absolute():
                    path = args.freshness.parent / path
                if path.is_file():
                    universes[universe_id] = json.loads(path.read_text(encoding="utf-8"))
        try:
            summary = validate_level2_freshness(population, freshness, universes=universes)
        except FreshnessInsufficientEvidence as exc:
            print(json.dumps({"status": "INSUFFICIENT_EVIDENCE", "error": str(exc)}, ensure_ascii=False))
            return 2
        except (FreshnessValidationError, TypeError, ValueError) as exc:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
            return 1
        print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
        return {"PASS": 0, "FAIL": 1, "INSUFFICIENT_EVIDENCE": 2}[summary["status"]]
    try:
        summary = validate_level2_freshness(population, freshness)
    except FreshnessInsufficientEvidence as exc:
        print(json.dumps({"status": "INSUFFICIENT_EVIDENCE", "error": str(exc)}, ensure_ascii=False))
        return 2
    except (FreshnessValidationError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
