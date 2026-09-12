# Week4 DEV implementation-integrity repair review

Scope: corrective execution implementation repair, TEST_ONLY verification,
and reauthorization only. No real F5 waveform generation, D0 query,
validation, held-out execution, or H4 calculation occurred in this review.

## Forensic boundary

`results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_01` is
frozen as an invalidated partial formal run. Its status, non-resumability,
and non-admissibility are recorded in
`WEEK4_DEV_REEXECUTION_01_INVALIDATION.md`.

The consumed authorization was copied byte-for-byte to:
`results/week4_adaptive_redteam/authorization_history/authorization_9A563E763E7252D38E9E5B585497F40772FA9CFB9B160DB6A6D0524980FCFEA7.json`.
The archived and original pre-replacement authorization SHA-256 is
`9A563E763E7252D38E9E5B585497F40772FA9CFB9B160DB6A6D0524980FCFEA7`.
Its historical disposition is
`CONSUMED_BY_INVALIDATED_PARTIAL_DEV_EXECUTION`.

## Corrective findings

1. `execute_protocol.evaluate()` no longer calls `score_candidate()` before
   the controller. The staged controller closure is the sole backend call. A
   TEST_ONLY sentinel backend verifies actual calls equal ledger-accounted
   detector invocations for static and 40-query adaptive paths.
2. `DetectorOutcome` separates successful D0 scoring from objective
   reportability. Static candidates retain finite score vectors with
   `objective_status = NOT_APPLICABLE`; adaptive candidates with absent
   `FULL_ATTACK` or `OUTSIDE_CLEAN` retain evidence as `OBJECTIVE_UNDEFINED`,
   consume their query, and cannot win.
3. `run_metadata.json` now has an atomic lifecycle snapshot and an append-only
   hash-chained `accounting/run_status_events.jsonl` ledger. It records
   INITIALIZED, RUNNING, COMPLETED/FAILED/BLOCKED states, backend timestamps,
   completed-case count, and failure identity.

The stored case-0004 geometry was reproduced only with TEST_ONLY fixtures:
9 S2 windows, `FULL_ATTACK = 6`, and `OUTSIDE_CLEAN = 0`. The static path
retained its vector without throwing; adaptive rows were non-winners; the
controller failed closed with `NO_VALID_ADAPTIVE_PARENT` when no defined
parent existed.

## Scientific freeze audit

```text
PREREGISTRATION_CHANGED = NO
CANONICAL_CONFIG_CHANGED = NO
POPULATION_CHANGED = NO
EXECUTION_SUPPLEMENT_CHANGED = NO
D0_ASSET_MANIFEST_CHANGED = NO
F5_SCIENTIFIC_SETTINGS_CHANGED = NO
SCIENTIFIC_PROTOCOL_CHANGED_AFTER_DEV_OBSERVATION = NO
EXECUTION_IMPLEMENTATION_CHANGED_AFTER_DEV_OBSERVATION = YES
IMPLEMENTATION_CHANGE_CLASS = CORRECTIVE_IMPLEMENTATION_INTEGRITY_REPAIR
```

Unchanged SHA-256 values: preregistration
`6942358DFF60EBC042E06F9441436D2BCCAE43EA8A66C6BD6B891FAE345758C4`,
config `1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D`,
population `DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6`,
supplement `B7E0589E491F70B893F62E17D587A341AF747FD817A2F85EA646AE291AC92ACC`,
and D0 asset manifest
`94009FE3F0EDD80FCEC78B78E44C90DEEEF9119C69A2221662A24774922EF0CF`.

## Verification

```text
WEEK4_TARGETED_TESTS = PASS (44 passed)
WEEK3_DEPENDENCIES = PASS (14 passed)
TEST_ONLY_FULL_E2E = PASS
FROZEN_ENVIRONMENT_FULL_REGRESSION = PASS (316 passed, 1 skipped)
ACTUAL_D0_EQUALS_LEDGER = PASS
OBJECTIVE_UNDEFINED_SEMANTICS = PASS
METADATA_LIFECYCLE = PASS
```

The repaired execution source manifest SHA-256 is
`C6CAB0FD7F1D648398BFAA5F3AF94200B70325F46B3CEAFA804B3301A844DB84`.
The new active invocation is `week4_dev_integrity_reexecution_02`, bound to
the empty namespace
`results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_02`.
It discloses prior DEV outcomes, no prior validation/held-out/H4 outcomes,
and the partial run's scientific non-admissibility. This review does not start
the future clean DEV run.
