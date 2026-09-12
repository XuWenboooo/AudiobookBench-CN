# Week4 DEV integrity reexecution 02 report

`WEEK4_CLEAN_DEV_INTEGRITY_REEXECUTION_02` was started under the separately
authorized identity below.  It was stopped at the first formal anomaly, as
required by the execution instructions.  This is not a completed 24-case DEV
run.  Validation, held-out, H4, and evaluator execution were not started.

## Identity and classification

```text
PRIOR_INVALID_PARTIAL_DEV_OBSERVED = YES
SCIENTIFIC_PROTOCOL_CHANGED_AFTER_PRIOR_DEV_OBSERVATION = NO
IMPLEMENTATION_REPAIRED_AFTER_PRIOR_DEV_OBSERVATION = YES

OLD_INVALID_RUN_REUSED = NO
OLD_D0_RESULTS_COPIED = NO
OLD_WINNERS_COPIED = NO
OLD_WAVEFORMS_USED_AS_INPUT = NO

AUTHORIZATION_SHA256 = A26471155AB4C3E57A7EFA01B6DDDA5BC9B0C85DCB8E471EC43589059DD074A7
SOURCE_MANIFEST_SHA256 = C6CAB0FD7F1D648398BFAA5F3AF94200B70325F46B3CEAFA804B3301A844DB84
INVOCATION_ID = week4_dev_integrity_reexecution_02
OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_02
RERUN_CLASSIFICATION = CORRECTIVE_IMPLEMENTATION_INTEGRITY_REPAIR
```

The prior invalid namespace `results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_01`
was not read as an execution input and remains untouched.

## Gates and environment

```text
FINAL_IDENTITY_GATE = PASS
WORKTREE_CLEAN_BEFORE_RUN = YES
LOCAL_HEAD_EQUALS_ORIGIN_MAIN = YES
ACTIVE_PREFLIGHT = PASS
F5_RUNTIME = QUALIFIED_OFFLINE
HF_HUB_OFFLINE = 1
TRANSFORMERS_OFFLINE = 1
FORMAL_GENERATION_STARTED = YES
FIRST_REAL_F5_OUTPUT = SUCCESS
```

The preflight bound the frozen 24-case DEV population and reported
`generation_invoked=false`, `d0_invoked=false`, and `evaluator_invoked=false`
before the real run.  The first real output then loaded the bound local F5
API, checkpoint, and Vocos assets.  No network fallback or model replacement
was observed.

## Execution result

```text
DEV_PLANNED = 24
DEV_STARTED = 4
DEV_COMPLETED = 3
DEV_FORMAL_SUCCESSFUL_CASES = 3
DEV_FAILED_OR_BLOCKED_CASES = 1

F5_TOTAL_ATTEMPTS = 4
F5_SUCCESSFUL_CASES = 4
F5_FAILED_CASES = 0
F5_RETRIES = 0

STATIC_D0_INVOCATIONS = 4
ADAPTIVE_D0_INVOCATIONS = 128
ADAPTIVE_D0_TOTAL = 132
ADAPTIVE_QUERY_MIN = 8
ADAPTIVE_QUERY_MAX = 40
ADAPTIVE_QUERY_MEAN = 32.0
CASES_WITH_40_ADAPTIVE_QUERIES = 3
CASES_WITH_FEWER_THAN_40_DUE_TO_NO_VALID_PARENT = 1
CASES_WITH_NO_VALID_WINNER = 1
```

Cases `0001`–`0003` each completed with one F5 attempt, one static D0, and
40 adaptive D0 queries.  Case `0004` completed F5 generation and its static
D0, then retained 8 adaptive D0 candidate records, all with
`OBJECTIVE_UNDEFINED`.  The next frozen proposal required a defined prior
objective and raised:

```text
NO_VALID_ADAPTIVE_PARENT: frozen mutation requires a defined prior objective
```

The runner recorded `failure_case_id=week4_case_0004`,
`failure_class=Week4ContractError`, `final_status=BLOCKED`, and terminated.
The relevant fail-closed path is
`src/audiobookbench/security/week4_adaptive.py:482-485`; the caller is
`src/audiobookbench/security/week4_execution.py:417-418`.

The required case-0004 geometry was observed correctly in all 9 retained
sidecars: 9 S2 windows, 6 `FULL_ATTACK`, and 0 `OUTSIDE_CLEAN`.  The static
sidecar retained its score vector while reporting
`objective_status=NOT_APPLICABLE`; the 8 adaptive sidecars retained their
score vectors while reporting `objective_status=OBJECTIVE_UNDEFINED`.

## Evidence inventory and integrity

```text
RAW_WAVEFORM_EVIDENCE = PRESENT_FOR_4_CASES
STANDARDIZED_WAVEFORM_EVIDENCE = PRESENT_FOR_4_CASES
SIDECARS = 132
CANDIDATE_LEDGER_ROWS = 132
F5_ATTEMPT_LEDGER_ROWS = 4
STATUS_EVENT_ROWS = 145
STATUS_EVENT_HASH_CHAIN = PASS
RAW_AND_STANDARDIZED_DATA_HASHES = PASS (4 of 4 attempts)
LEDGER_ACCOUNTED_D0_INVOCATIONS = 132
EVALUATOR_ARTIFACTS = NONE
```

All 132 retained candidate rows had a successful D0 record and a matching
sidecar identity/outcome record.  However, a separate waveform-hash
consistency check found a blocking implementation defect: the candidate
ledger hashes each waveform after coercion to `float64` at
`src/audiobookbench/security/week4_adaptive.py:538-539`, while the sidecar
uses `float32` at `src/audiobookbench/security/week4_execution.py:148-150`.
Consequently, the ledger `candidate_waveform_sha256` and sidecar
`waveform_sha256` disagreed for 132/132 retained candidates.  This is an
`IMPLEMENTATION_BLOCKER` even though the F5 attempt raw/standardized data
hashes and the status-event chain passed.

## Immutability and stop state

```text
SCIENTIFIC_PARAMETERS_CHANGED = NO
EXECUTION_CODE_CHANGED_AFTER_FIRST_REAL_OUTPUT = NO
POPULATION_CHANGED = NO
AUTHORIZATION_CHANGED = NO
PREREGISTRATION_CHANGED = NO
CANONICAL_CONFIG_CHANGED = NO
EXECUTION_SUPPLEMENT_CHANGED = NO

VALIDATION_SCIENTIFIC_RUN = NOT_STARTED
HELD_OUT_RUN = NOT_STARTED
H4_RESULT_OBSERVED = NO
EVALUATOR_INVOKED = NO

WEEK4_CLEAN_DEV_REEXECUTION = INCOMPLETE_STOPPED_ON_FORMAL_ANOMALY
READY_FOR_POST_DEV_INTEGRITY_REVIEW = NO
```

This consumed partial namespace must not be resumed, overwritten, or used as
a source for a future formal run.  The two blocking defects requiring a new
review are the no-valid-parent behavior after undefined objectives and the
float32/float64 waveform-hash convention mismatch.  This report does not
authorize another execution.
