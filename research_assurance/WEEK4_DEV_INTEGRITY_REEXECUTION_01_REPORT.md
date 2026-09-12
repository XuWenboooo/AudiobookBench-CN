# Week4 DEV integrity reexecution 01 report

`WEEK4_CLEAN_DEV_INTEGRITY_REEXECUTION_01` was started under the separately
authorized identity below.  It was stopped at the first formal anomaly, as
required by the execution instructions.  This is not a completed DEV run and
no validation, held-out, or H4 execution was started.

## Identity and classification

```text
FAILED_HISTORICAL_RUN_PRESERVED = YES
FAILED_HISTORICAL_RUN_REUSED = NO

NEW_AUTHORIZATION_SHA256 = 9A563E763E7252D38E9E5B585497F40772FA9CFB9B160DB6A6D0524980FCFEA7
NEW_INVOCATION_ID = week4_dev_integrity_reexecution_01
NEW_OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_01
RERUN_CLASSIFICATION = INFRASTRUCTURE_QUALIFICATION_REEXECUTION_BEFORE_SCIENTIFIC_OUTCOME
```

The historical failed namespace remains untouched:
`results/week4_adaptive_redteam_runs/week4_adaptive_redteam_v0_20260912_supplement_v1`.
It still contains exactly `run_metadata.json` and
`accounting/f5_attempt_ledger.jsonl`, with hashes
`D5ACDAAA34566C0D8D02C5294646BDFE4D2A271B636E70BE5A3E4A973E900CAE` and
`6A0F033CB7C24827BBA986D7C377041320729C52A8120045663A22097B6E63DC`.

## Gates and environment

```text
F5_RUNTIME_IMPORT_GATE = PASS
ACTIVE_PREFLIGHT = PASS
FIRST_REAL_F5_OUTPUT = SUCCESS
F5_SOURCE_IDENTITY = PASS
FORMAL_ENVIRONMENT = QUALIFIED_OFFLINE
HF_HUB_OFFLINE = 1
TRANSFORMERS_OFFLINE = 1
```

The F5 source identity is commit
`82fc4fe622fe36047d1dff99b550e6018181ea11`, bound through
`research_assurance/WEEK4_F5_FROZEN_SOURCE_MANIFEST.json` with SHA-256
`689600D6D3C83335C19952492CB833F645EEDAB5ED517AC406A781DB88BB6317`.
The environment is bound through
`research_assurance/WEEK4_FORMAL_RUNTIME_ENVIRONMENT_MANIFEST.json` with
SHA-256 `90EB8CD3D5E666D9AC7717A01B691341A5855C565BA538FA4ED7286A6A521C6E`.
The package uses the recorded PEP 420 namespace layout: `f5_tts.__file__`
is `None`, while `f5_tts.api.__file__` resolves to the frozen local source
tree.  API construction and exact checkpoint/vocoder loading passed.

## Execution result

```text
DEV_PLANNED = 24
DEV_STARTED = YES
DEV_COMPLETED = 3
DEV_SUCCESS = 3
DEV_FAILED = 1

F5_TOTAL_ATTEMPTS = 4
F5_SUCCESSFUL_CASES = 4
F5_FAILED_CASES = 0
F5_RETRIES = 0

STATIC_D0_INVOCATIONS = 4
ADAPTIVE_D0_INVOCATIONS = 120
ADAPTIVE_QUERY_MIN = 40
ADAPTIVE_QUERY_MAX = 40
ADAPTIVE_QUERY_MEAN = 40.0
CASES_WITH_40_D0_QUERIES = 3
CASES_WITH_PRE_D0_INVALID_CANDIDATES = 0
CASES_WITH_D0_RUNTIME_FAILURE = 1
CASES_WITH_NO_VALID_WINNER = 1
```

The counts above are the ledger-accounted candidate queries.  Read-only
control-flow tracing identified an additional execution-integrity defect:
`execute_protocol.evaluate()` calls `score_candidate()` once before invoking
`A0AttackController.evaluate_candidate()`, and the controller's detector
closure calls `score_candidate()` a second time for the same candidate.  Thus
the real backend invocation count is not represented by the ledger: the
observed candidates imply at least 8 static and 240 adaptive backend calls,
while only 4 and 120 respectively were recorded.  This violates the
exactly-one-query accounting contract and is an independent reason the formal
run is invalid.  No attempt was made to repair or replay it.

Cases `week4_case_0001` through `week4_case_0003` completed with one F5
attempt, one static D0 invocation, and 40 adaptive D0 queries each.  Case
`week4_case_0004` produced and retained its real F5 waveform, then failed at
the static D0 detector call with:

```text
ValueError: detector score is non-finite
```

The failure was recorded as an invalid candidate with
`failure_class = detector_runtime_failure`; the process then terminated.
No fifth case was started, and no automatic patch or retry was performed.

## Evidence inventory and integrity

```text
RAW_WAVEFORM_EVIDENCE = PRESENT_FOR_4_CASES
STANDARDIZED_WAVEFORM_EVIDENCE = PRESENT_FOR_4_CASES
SCORE_VECTOR_EVIDENCE = PRESENT_FOR_123_CANDIDATES
SAMPLE_FIRST_GT_EVIDENCE = PRESENT_FOR_123_CANDIDATES
ATTEMPT_LEDGER_INTEGRITY = PASS (4 rows, hash chain verified)
CANDIDATE_LEDGER_INTEGRITY = PASS (124 rows, hash chain verified)
```

The namespace contains 4 raw F5 waveforms, 4 standardized base synthetic
waveforms, 123 sidecars with score vectors and GT projections, and 124
candidate ledger rows.  All candidate rows, including the detector failure,
remain retained.  No winner was produced for case 0004.

The run metadata was written before backend invocation and was not updated by
the current runner after execution.  Consequently its initial fields
`generation_invoked = false`, `d0_invoked = false`, and `status = PASS` do not
describe the observed run.  This is an evidence-consistency defect and is
reported as-is; the metadata, ledgers, waveforms, authorization, and frozen
scientific inputs were not edited after the anomaly.

## Immutability and stop state

```text
SCIENTIFIC_PARAMETERS_CHANGED = NO
EXECUTION_CODE_CHANGED_AFTER_REAL_OUTPUT = NO
POPULATION_CHANGED = NO
AUTHORIZATION_CHANGED = NO
PREREGISTRATION_CHANGED = NO
CANONICAL_CONFIG_CHANGED = NO
EXECUTION_SUPPLEMENT_CHANGED = NO

VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO

WEEK4_CLEAN_DEV_REEXECUTION = INCOMPLETE_STOPPED_ON_FORMAL_ANOMALY
READY_FOR_POST_DEV_INTEGRITY_REVIEW = NO
```

The current output namespace is now a consumed partial formal run and must
not be resumed or overwritten.  Any future action requires a separate review
of the non-finite detector failure and the metadata finalization defect; this
report does not authorize a new run.
