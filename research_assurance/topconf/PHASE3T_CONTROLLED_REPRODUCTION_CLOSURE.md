# Phase 3T Controlled External Reproduction Closure

Status: **IN PROGRESS — AUTHORIZATION FROZEN**

This document is append-only. Phase3, Phase3R, Phase3S, Phase3U and Phase3V
closures remain historical and authoritative in their own files.

```text
PHASE3T_AUTHORIZATION = P3T-2026-09-13-01
PHASE3T_AUTHORIZATION_FILE = PHASE3T_CONTROLLED_REPRODUCTION_AUTHORIZATION_V1.md
PHASE3T_AUTHORIZATION_SHA256 = PENDING_AUTHORIZATION_COMMIT
DATA_ROLE = LEVEL_1_EXTERNAL_REPRODUCTION_AND_COMPATIBILITY
PHASE3_CLOSURE = BLOCKED
PHASE3R_CLOSURE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE
PHASE3V_CLOSURE = PASS
PHASE3T_CLOSURE = IN_PROGRESS
```

## Initial frozen gates

```text
DATASET = PartialEdit v1.1 E1; all valid cases; expected 42471
CASE_ORDER = official PartialEdit_E1E2.csv rows beginning E1/ in file order
CFPRF_FULL_INFERENCE = NOT_STARTED
MULTIRESO_FULL_INFERENCE = NOT_STARTED
RAW_OUTPUT_COMPLETENESS = NOT_STARTED
FAILURE_ACCOUNTING = NOT_STARTED
CFPRF_ADAPTER = NOT_STARTED
MULTIRESO_ADAPTER = NOT_STARTED
UNIFIED_EVALUATOR_END_TO_END = NOT_STARTED
LEVEL1_METRICS_COMPUTED = NOT_STARTED
LD_DR95_COMPUTED = NO
WHETHER_A_SELECTED = NO
WHETHER_B_RUN = NO
RESULT_BASED_SUBSTITUTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_HEAD_SELECTIONS = 0
EXTERNAL_FUNCTIONAL_PARADIGMS = 2 planned
FULL_AUDIO_EXTERNAL_DATASETS = 1
```

## Exit rule

Phase3T can close PASS only after both baselines have exactly one terminal
state for all 42,471 planned cases, raw native outputs are preserved and
hashed, all six MultiReso scales remain available, the canonical adapters and
unified evaluator pass end-to-end, and no result-based selection or exclusion
occurred. A PASS permits only human Phase4 reconciliation; it does not start
Phase4 or authorize RQ1 confirmatory execution.

## Crash-recovery completion record (append-only)

Recorded after the controlled execution artifacts were recovered and
revalidated on 2026-09-14. The initial frozen gates above remain preserved.

```text
BRANCH = topconf-dl-robustness
LOCAL_HEAD = pending closure commit
REMOTE_HEAD = 64887a1585f48af9895e8a09370d9de88c22b761 before closure commit
WORKING_TREE = pending closure commit

CRASH_RECOVERY_AUDIT = PASS; PHASE3T_CRASH_RECOVERY_AUDIT_V1.md
CRASH_RESUME_LEDGER = COMPLETE; PHASE3T_CRASH_RESUME_LEDGER_V1.md
PHASE3T_AUTHORIZATION = P3T-2026-09-13-01
PHASE3T_AUTHORIZATION_SHA256 = A23327AA781ADAFC2302EADF3F552B9C50C5A775DC237918B3730703AC219331

CFPRF_INVOCATION = mainline authorized resume chain; ID not persisted
CFPRF_NAMESPACE = results/topconf_phase3t/cfprf
CFPRF_PLANNED = 42471
CFPRF_TERMINAL = 42471
CFPRF_VALID = 42455
CFPRF_FAILED = 16
CFPRF_MISSING = 0
CFPRF_ORPHAN = 0
CFPRF_RETRIES = 3
CFPRF_RESUMED = YES; existing terminal cases skipped

MULTIRESO_INVOCATION = PHASE3T_MRM_FULL_E1_002
MULTIRESO_NAMESPACE = F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02
MULTIRESO_PLANNED = 42471
MULTIRESO_TERMINAL = 42471
MULTIRESO_VALID = 42438
MULTIRESO_FAILED = 33
MULTIRESO_MISSING = 0
MULTIRESO_ORPHAN = 0
MULTIRESO_RETRIES = 4
MULTIRESO_SCALES = 6/6
MULTIRESO_RESUMED = YES; worker-r2 unfinished cases only

SUPERSEDED_INVOCATIONS = mainline MultiReso partial (7810); worker-01 MultiReso partial (7880)
LIVE_PROCESSES_FOUND = none at recovery audit
ENVIRONMENT_IDENTITY_CFPRF = Python 3.10.11; torch 2.2.2+cu121; fairseq 1.0.0a0; RTX 4060; authorized py310 environment
ENVIRONMENT_IDENTITY_MULTIRESo = Python 3.10.11; torch 1.13.1+cu117; fairseq 0.12.2; RTX 4060; authorized py310 environment

RAW_OUTPUT_COMPLETENESS = PASS
FAILURE_ACCOUNTING = PASS; CFPRF MODEL_INFERENCE_FAILURE=16; MultiReso AUDIO_LOAD_FAILURE=33
RAW_OUTPUT_HASH_MANIFEST = PHASE3T_RAW_OUTPUT_MANIFEST_V1.json

CFPRF_ADAPTER = PASS
MULTIRESO_ADAPTER = PASS
UNIFIED_EVALUATOR_END_TO_END = PASS
LEVEL1_METRICS_COMPUTED = frame AUROC and frame AUPRC only, all authorized heads/scales
METRICS_COMPUTED = CFPRF FDN AUROC=0.7592932155776073 AUPRC=0.390163089579501; CFPRF boundary AUROC=0.535833446353212 AUPRC=0.2129300223563507; MultiReso scales retained independently in evaluator artifact
LD_DR95_COMPUTED = NO
WHETHER_A_SELECTED = DEFERRED
WHETHER_B_RUN = NO

RESULT_BASED_SELECTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_HEAD_SELECTIONS = 0
SCIENTIFIC_PROTOCOL_VIOLATIONS = 0; execution deconfliction was documented and no scientific outcome informed ownership

TESTS = python -m pytest tests/topconf -q: 33 passed; git diff --check: PASS; both raw validators: PASS; both adapters: PASS; unified evaluator: PASS; final raw manifest JSON parse: PASS
HISTORICAL_FULL_SUITE_DEPENDENCY = results/day10/day10_output_hashes.json is absent; not fabricated; full historical suite not used as Phase3T gate

PHASE3T_CLOSURE = PASS
REMAINING_BLOCKERS = none for Phase3T; human Phase4 reconciliation remains a separate next-stage decision
READY_FOR_PHASE4_HUMAN_RECONCILIATION = YES
PHASE4_STARTED = NO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO
```

The MultiReso Level-1 evaluator artifact contains all six scale rows with
`winner_selected=false`; no scale or head was chosen. All evaluator rows are
descriptive Level-1 external functional diagnostics only and must not be
treated as RQ1 confirmatory evidence.
