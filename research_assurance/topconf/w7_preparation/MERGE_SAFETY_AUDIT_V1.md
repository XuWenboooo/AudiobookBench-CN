# W7 Preparation Merge Safety Audit v1

Status: `LOW CONFLICT RISK`

This branch is based on `origin/topconf-dl-robustness` and writes only under
the new `research_assurance/topconf/w7_preparation/` tree, new preparation
modules under `src/audiobookbench/topconf/preparation/`, the new checker and
new preparation tests/fixtures. No active downloader state was copied or
modified.

## Safe merge files

- `research_assurance/topconf/w7_preparation/**`
- `src/audiobookbench/topconf/preparation/**`
- `tools/topconf/build_partialspoof_identity_mismatch.py`
- `tools/topconf/check_w7_preregistration.py`
- `tests/topconf/test_w7_preparation_acceptance.py`
- `tests/topconf/test_w7_preregistration.py`
- `tests/topconf/fixtures/w7_preparation_fixtures.py`

## Files requiring manual review

- Any future merge that touches `research_assurance/topconf/w6_recovery/W7_DISTRIBUTION_MATRIX_V2.md`.
- Any future merge that touches `research_assurance/topconf/w6_recovery/TOPCONF_W6_RECOVERY_CLOSURE_V1.md`.
- Any future merge that changes existing W7 evaluator, namespace, Level-2,
  population, or downloader contracts.

## Explicitly not modified

HQ-MPSD/HAD archive and `.part` files, downloader scripts/state, file locks,
Phase4.9R, V3 population, existing Level-2 assets, localizer checkpoints and
scientific outcome artifacts were not modified. This preparation branch does
not download, materialize or execute W7 data.
