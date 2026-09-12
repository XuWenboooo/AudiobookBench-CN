# Week4 DEV03 post-run integrity review

This is a read-only post-run review of
`results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_03`.
It records readiness facts only. It does not authorize validation, held-out
execution, evaluator execution, or H4 reporting.

```text
REVIEW_STATUS = PASS
RUN_CLASS = DEV_ONLY
INVOCATION_ID = week4_dev_integrity_reexecution_03
OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_03
AUTHORIZATION_SHA256 = 2971130A92C8A6250FD338DBEC01E766171E81D222EB97747AE70C17FE743D9E
SOURCE_MANIFEST_SHA256 = 1D17BABC8987C21962CFCFB271C9DB95B8B878C4F13852674FDC4BA6D04067A7
GOVERNANCE_AMENDMENT_SHA256 = B7F0BD3C715F87295FAEEEC311410C5B443B3654CBBF0AF1F37F5AB405A440C6
PRIOR_REEXECUTION_02_INVALIDATION_SHA256 = 4EEB0F08A76113CA26057156F5CA3EF09195E48FB4D364881FAED1A0D076E683

DEV_PLANNED = 24
DEV_TERMINAL = 24
DEV_WITH_WINNER = 12
DEV_NO_VALID_ADAPTIVE_PARENT = 12
DEV_OTHER_FAILURES = 0
F5_TOTAL_ATTEMPTS = 24
F5_RETRIES = 0
STATIC_D0 = 24
ADAPTIVE_D0 = 568
TOTAL_CANDIDATE_ROWS = 600
TOTAL_D0_SIDECARS = 592

ATTEMPT_LEDGER_INTEGRITY = PASS
CANDIDATE_LEDGER_INTEGRITY = PASS
STATUS_EVENT_LEDGER_INTEGRITY = PASS
WAVEFORM_HASH_INTEGRITY = PASS
SCORE_VECTOR_HASH_INTEGRITY = PASS
SAMPLE_FIRST_GT_INTEGRITY = PASS
HISTORICAL_NAMESPACE_INPUT_LEAKAGE = PASS

VALIDATION_OBSERVED = NO
HELD_OUT_OBSERVED = NO
EVALUATOR_OBSERVED = NO
H4_OBSERVED = NO
```

The 12 no-parent cases each consumed the allowed eight generation-0 adaptive
D0 queries and terminated structurally because no finite adaptive parent
existed. The runner then continued through all 24 DEV cases. The eight
pre-D0 invalid candidates were retained in the candidate ledger and did not
create D0 sidecars. No result-dependent protocol, attack specification,
population, authorization, or execution implementation change was observed
during the run.

The independent audit reconstructed the sidecar waveform and GT contract from
the canonical DEV source, the per-case standardized base synthetic, and the
candidate ledger parameters. All 592 D0 sidecars passed waveform identity,
float64 score-vector hashing, S2-window, and sample-first GT checks. The
previous 01 and 02 namespaces remain forensic-only and were not read as
inputs.

`REVIEW_STATUS=PASS` means the completed DEV evidence is internally coherent
under the current frozen implementation and governance amendment. It does
not mean that an H4 result exists or that the validation stage may start
without a new authorization.
