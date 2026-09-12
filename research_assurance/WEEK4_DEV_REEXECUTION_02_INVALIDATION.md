# Week4 DEV reexecution 02 invalidation

`results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_02` is a
consumed forensic namespace.  It is read-only and no artifact inside it may be
modified, resumed, overwritten, or reused as an execution input.

## Bound identity

```text
RUN_REPORT = research_assurance/WEEK4_DEV_INTEGRITY_REEXECUTION_02_REPORT.md
RUN_REPORT_SHA256 = C90794869B7CBF1A5EAF3E78531497F0699EE8A29B392209FBBC98DA07378054
AUTHORIZATION_SHA256 = A26471155AB4C3E57A7EFA01B6DDDA5BC9B0C85DCB8E471EC43589059DD074A7
INVOCATION_ID = week4_dev_integrity_reexecution_02
OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_02
```

## Observed execution state

```text
DEV_PLANNED = 24
DEV_COMPLETED = 3
CASE_0004_BLOCKED = YES

REAL_DEV_OUTCOMES_OBSERVED = YES
REAL_F5_CASES = 4
REAL_D0_INVOCATIONS = 132
REAL_CANDIDATE_SIDECARS = 132

VALIDATION_OUTCOMES_OBSERVED = NO
HELD_OUT_OUTCOMES_OBSERVED = NO
H4_OUTCOME_OBSERVED = NO
EVALUATOR_INVOKED = NO
```

The observed blockers are separately classified as
`FROZEN_EXECUTION_GOVERNANCE_UNDERSPECIFIED` for no valid adaptive parent and
`EVIDENCE_CANONICALIZATION_IMPLEMENTATION_DEFECT` for the divergent waveform
hash dtype.  Neither permits modifying the consumed evidence.

## Invalidation

```text
RUN_SCIENTIFICALLY_ADMISSIBLE = NO
RUN_RESUMABLE = NO
RUN_REUSABLE_AS_EXECUTION_INPUT = NO
AUTHORIZATION_STATUS = CONSUMED_BY_INVALIDATED_PARTIAL_DEV_EXECUTION
```

The metadata, candidate ledger, F5 attempt ledger, status ledger, waveforms,
sidecars, and authorization identity used by this run remain forensic evidence
only.  No DEV result, D0 result, winner, or waveform from this namespace may
be copied into a future run.
