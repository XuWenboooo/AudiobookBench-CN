# W7 Preparation Merge Manifest v1

Status: `COMPLETE`; generated from the preparation branch diff

## SAFE_TO_MERGE

- `research_assurance/topconf/w7_preparation/**`
- `src/audiobookbench/topconf/preparation/**`
- `tools/topconf/build_partialspoof_identity_mismatch.py`
- `tools/topconf/check_w7_preregistration.py`
- `tests/topconf/fixtures/w7_preparation_fixtures.py`
- `tests/topconf/test_w7_preparation_acceptance.py`
- `tests/topconf/test_w7_preregistration.py`
- `tests/topconf/test_w7_identity_contracts.py`

These paths contain contracts, schemas, outcome-blind validators, synthetic
tests, preparation evidence and paper scaffolds. They do not contain real
datasets, archives, checkpoints or runtime results.

## MANUAL_REVIEW_REQUIRED

The branch does not modify these existing shared files, but any future merge
that changes them requires manual review:

- `research_assurance/topconf/w6_recovery/W7_DISTRIBUTION_MATRIX_V2.md`
- `research_assurance/topconf/w6_recovery/TOPCONF_W6_RECOVERY_CLOSURE_V1.md`
- existing W7 evaluator or namespace implementation
- Level-2 interfaces, population definitions or scientific manifest code
- downloaders, locks or recovery state

## DO_NOT_MERGE

- real data, archives, checkpoints, `.part` files and file locks
- temporary output, caches and runtime logs not required as evidence
- absolute machine-specific paths and secrets
- any W7 result, metric, bootstrap output or outcome-derived selection

The current branch contains none of these prohibited artifacts.
