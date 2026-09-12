# Week4 DEV integrity reexecution 03 report

`week4_dev_integrity_reexecution_03` is the completed, DEV-only integrity
reexecution of the frozen Week4 protocol. It used the active authorization and
the hash-bound local offline F5 environment. This report records execution
facts and post-run audit facts only; it is not primary H4 evidence and does not
authorize validation or held-out execution.

## Strict execution fields

```text
LOCAL_HEAD = 8d0eaaba7088eb7ac1f62ef6c6cbe73f273785b1
REMOTE_HEAD = 8d0eaaba7088eb7ac1f62ef6c6cbe73f273785b1
WORKING_TREE = CLEAN_BEFORE_RUN

AUTHORIZATION_SHA256 = 2971130A92C8A6250FD338DBEC01E766171E81D222EB97747AE70C17FE743D9E
INVOCATION_ID = week4_dev_integrity_reexecution_03
OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_03

DEV_PLANNED = 24
DEV_ATTEMPTED = 24
DEV_TERMINAL = 24
DEV_WITH_WINNER = 12
DEV_NO_VALID_ADAPTIVE_PARENT = 12
DEV_OTHER_FAILURES = 0

F5_TOTAL_ATTEMPTS = 24
F5_RETRIES = 0

STATIC_ACTUAL_D0 = 24
STATIC_LEDGER_D0 = 24
STATIC_ACCOUNTING_MATCH = PASS

ADAPTIVE_ACTUAL_D0 = 568
ADAPTIVE_LEDGER_D0 = 568
ADAPTIVE_ACCOUNTING_MATCH = PASS

ADAPTIVE_QUERY_MIN = 8
ADAPTIVE_QUERY_MAX = 40
ADAPTIVE_QUERY_MEAN = 23.6666666667

LEDGER_SIDECAR_WAVEFORM_HASH_MATCH = PASS (592/592 D0 sidecars; 8 pre-D0 invalid candidates have no sidecar)
SCORE_VECTOR_HASHES = PASS (592/592)
ATTEMPT_LEDGER_INTEGRITY = PASS (24 rows)
CANDIDATE_LEDGER_INTEGRITY = PASS (600 rows)
STATUS_EVENT_LEDGER_INTEGRITY = PASS (678 rows)
SAMPLE_FIRST_GT_INTEGRITY = PASS (592/592)

RUNTIME_COUNTS_MATCH_RECOMPUTATION = PASS (independent raw-ledger recomputation; dispatch accounting was not persisted by the CLI)

WEEK4_TESTS = 49 passed
WEEK3_DEPENDENCIES = 97 passed, 1 warning
FULL_REGRESSION = 321 passed, 1 skipped, 1 warning
FORMAL_ENV_REGRESSION = PASS in the bound F5 environment (same 321/1/1 full-regression result)

REEXECUTION_01_IMMUTABLE = YES
REEXECUTION_02_IMMUTABLE = YES

SCIENTIFIC_ATTACK_SPEC_CHANGED_DURING_RUN = NO
EXECUTION_GOVERNANCE_CHANGED_DURING_RUN = NO
EXECUTION_IMPLEMENTATION_CHANGED_DURING_RUN = NO
POPULATION_CHANGED = NO
AUTHORIZATION_CHANGED = NO

VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO

WEEK4_DEV03_STATUS = COMPLETED_DEV_ONLY
POST_DEV_INTEGRITY_REVIEW = PASS
READY_FOR_VALIDATION_STAGE_PREPARATION = YES
```

## Bound identity and environment

The run used the canonical config
`configs/week4_adaptive_red_team.yaml`, the finalized 48-case population
manifest, and the active authorization. The observed metadata ended with
`status=COMPLETED`, `lifecycle_status=COMPLETED`,
`final_status=COMPLETED`, `completed_case_count=24`,
`generation_invoked=true`, `d0_invoked=true`, and `evaluator_invoked=false`.
The canonical config hash was
`1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D`; the
population manifest hash was
`DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6`.
The formal environment was the local, offline F5-TTS v1 Base environment;
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` were set. No network fallback,
model replacement, validation runner, held-out runner, evaluator, bootstrap,
or H4 result was invoked.

## DEV accounting and terminal cases

The raw ledgers independently recompute 24 successful F5 attempts, with one
attempt per case and no retries. Every DEV case has a terminal case-outcome
record. Twelve cases completed with an adaptive winner. Twelve cases reached
the frozen terminal state `NO_VALID_ADAPTIVE_PARENT` after exactly eight
successful generation-0 adaptive D0 queries; those cases were retained as
terminal DEV evidence and the runner continued to the next case. There were
no other failures.

The 600 candidate rows comprise 24 static rows and 576 adaptive rows. Of the
adaptive rows, 568 were accounted D0 calls and eight were pre-D0 invalid
candidate records for the frozen `INVALID_BEFORE_D0_peak` rule. The 568
adaptive D0 calls are the sum of the case-level query counts and give a mean
of 23.6666666667. The 12 winner cases include one case with 32 adaptive D0
queries; the remaining winner cases reached 40. This is the observed frozen
ledger state, not a scientific claim about H4.

## Evidence integrity

The namespace contains 24 raw F5 waveforms, 24 standardized base-synthetic
waveforms, 592 D0 sidecars, 12 winner selections, and 24 case outcomes. The
candidate, attempt, and status-event JSONL chains were recomputed from their
canonical serialization and all passed. Every attempt raw and standardized
waveform hash matched its persisted NPY representation. Every D0 sidecar
matched its candidate-ledger waveform identity; every persisted score vector
matched its recorded float64 score-vector hash; and reconstruction from the
DEV source, standardized base synthetic, and ledger parameters matched the
sidecar waveform, S2 windows, and sample-first GT projection for all 592 D0
sidecars.

The namespace has no `final.json`, no validation or held-out output, and no
evaluator artifact. `RUNTIME_COUNTS_MATCH_RECOMPUTATION` is based on the raw
ledger and metadata because the CLI does not persist the dispatcher return
value; it is not a claim that an unpersisted runtime summary was independently
read.

The prior reexecution namespaces 01 and 02 remain separate forensic
namespaces. Their artifacts were not copied, resumed, or used as inputs. The
key 01 hashes still match its invalidation record:

```text
REEXECUTION_01_RUN_METADATA_SHA256 = F35E31805869DC14F0AB6C380852F50C6B608E72A18677856AD3C227471F3622
REEXECUTION_01_CANDIDATE_LEDGER_SHA256 = CAE1C58DE6CAEB67F5C7F5CD7062E110A3C3F394BD59E82A92058681C4C3E03B
REEXECUTION_01_ATTEMPT_LEDGER_SHA256 = 98FD6C145AD32A536190D3476AFDD5FCFDAED266B28589516B008699BB652E96
```

## Interpretation and next boundary

This is a completed DEV-only integrity reexecution. The twelve no-parent
terminals are governed, retained, and disclosed; they are not converted into
winners and do not produce a primary H4 result. The run is therefore suitable
as an input fact for preparing a future validation-stage review, subject to a
new independent authorization and all unchanged frozen gates. No validation
authorization was created by this report, and no validation or held-out
scientific execution is authorized by it.
