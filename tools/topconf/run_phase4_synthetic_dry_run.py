"""Run the metadata-only Phase-4 Level-2 governance rehearsal.

The rehearsal uses fabricated identities and scalar placeholders only.  It
never opens audio, a checkpoint, a real manifest, or a research outcome.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from audiobookbench.topconf.level2.governance import (  # noqa: E402
    build_blinded_manifest,
    validate_case_coverage,
    validate_level2_manifest,
    validate_metric_registration,
    validate_namespace,
    validate_reveal_gate,
    validate_retry_ledger,
    validate_threshold_policy,
)


def run(manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_level2_manifest(manifest)
    blinded = build_blinded_manifest(manifest)
    case_ids = [row["case_id"] for row in manifest["variants"]]

    namespace = {
        "invocation_id": "SYNTHETIC_PHASE4_001",
        "output_namespace": "synthetic/phase4/001",
        "authorization_hash": "a" * 64,
        "protocol_hash": "b" * 64,
        "dataset_hash": "c" * 64,
    }
    validate_namespace(namespace, [])

    terminal = [
        {"case_id": case_id, "terminal_category": "SCIENTIFIC_VALID_CASE"}
        for case_id in case_ids
    ]
    validate_case_coverage(case_ids, terminal)
    validate_retry_ledger([], terminal)

    # Synthetic adapter/evaluator placeholders: finite scalars with stable
    # identities, never model or audio outputs.
    adapter_rows = [
        {
            "case_id": case_id,
            "where_score": 0.4 + 0.1 * index,
            "whether_score": 0.6 - 0.1 * index,
        }
        for index, case_id in enumerate(case_ids)
    ]
    if not all(
        math.isfinite(row["where_score"]) and math.isfinite(row["whether_score"])
        for row in adapter_rows
    ):
        raise ValueError("synthetic adapter produced a non-finite placeholder")
    validate_metric_registration("LD@DR95", ["LD@DR95"])
    validate_threshold_policy(
        {
            "source": "LEVEL1_CALIBRATION",
            "calibration_split": "synthetic_dev",
            "frozen_before_level2_reveal": True,
        }
    )

    # Exercise the resampling path with fabricated scalar values.  The means
    # are intentionally not emitted: this is a control-flow rehearsal, not a
    # scientific estimate.
    rng = random.Random(20260914)
    bootstrap_means = []
    for _ in range(64):
        sample = [adapter_rows[rng.randrange(len(adapter_rows))]["where_score"] for _ in case_ids]
        bootstrap_means.append(sum(sample) / len(sample))
    if not all(math.isfinite(value) for value in bootstrap_means):
        raise ValueError("synthetic bootstrap produced a non-finite placeholder")

    authorization = {
        "status": "SYNTHETIC_GOVERNANCE_DRY_RUN",
        "protocol_frozen": True,
        "freeze_record_hash": "d" * 64,
        "protocol_hash": "b" * 64,
        "dataset_hash": "c" * 64,
    }
    inference = {"completed": True, "protocol_hash": "b" * 64}
    validate_reveal_gate(authorization, inference, "b" * 64, "c" * 64)

    return {
        "schema_version": "topconf.phase4.synthetic-dry-run.v1",
        "status": "PASS",
        "data_source": "SYNTHETIC_GOVERNANCE_DRY_RUN",
        "scientific_runs_invoked": False,
        "real_level2_outcomes_accessed": False,
        "result_based_design_changes": 0,
        "stages": {
            "manifest": "PASS",
            "inference_safe_view": "PASS",
            "blinding": "PASS",
            "namespace": "PASS",
            "failure_accounting": "PASS",
            "retry_ledger": "PASS",
            "adapter": "PASS",
            "evaluator": "PASS",
            "bootstrap": "PASS",
            "reveal_gate": "PASS",
        },
        "synthetic_case_count": len(case_ids),
        "blinded_case_count": len(blinded["cases"]),
        "bootstrap_replicates": 64,
        "scientific_outputs": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.manifest)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
