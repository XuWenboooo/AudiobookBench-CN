# Phase3T MultiReso Execution Integrity Recovery v1

Status: **INFRASTRUCTURE_INTEGRITY_REEXECUTION / NON-SCIENTIFIC**

This record documents an execution-integrity recovery. It does not interpret,
rank, filter, select, exclude, or compare scientific outputs. The prior
attempt is preserved as evidence and is not eligible for Phase3T evaluation.

## Superseded attempt

```text
OLD_INVOCATION = PHASE3T_MRM_FULL_E1_001
OLD_NAMESPACE = results/topconf_phase3t/multireso_worker_01
OLD_PID = 39048
OLD_PARENT_PID = 40004
OLD_START = 2026-09-13T21:40:43+08:00
OLD_EXECUTABLE = F:\项目\申请实验室\python.exe
OLD_COMMAND = "F:\项目\申请实验室\python.exe" experiments/topconf_phase3t/run_multireso_worker.py --batch-size 4
OLD_TERMINAL = 16629
OLD_RAW = 16622
OLD_FAILURES = 7 AUDIO_LOAD_FAILURE
OLD_ORPHAN_RAW = 0
OLD_STATUS = SUPERSEDED_INFRASTRUCTURE_ATTEMPT
OLD_OUTPUTS_USED_FOR_SCIENCE = NO
OLD_STOP_ACTION = process already terminated after provenance capture; no resume
```

The old process provenance also recorded parent executable
`F:\项目\申请实验室  TTS项目\envs\topconf-phase3v-multireso-py310\Scripts\python.exe`.
The child command identity nevertheless resolved to the non-authorized
`F:\项目\申请实验室\python.exe` path. This differs from the frozen invocation
identity required for the new run. The seven audio-load failures remain in the
old infrastructure ledger; they are not population exclusions.

All old raw outputs, manifests, ledgers, logs, and hashes remain in the old
namespace. They must not be deleted, overwritten, appended with inference
records, resumed, or ingested by an evaluator.

## Root cause and recovery boundary

```text
ROOT_CAUSE = EXECUTION_ENVIRONMENT_IDENTITY_MISMATCH + CONCURRENT_NAMESPACE_OWNERSHIP
NEW_INVOCATION = PHASE3T_MRM_FULL_E1_002
NEW_NAMESPACE = results/topconf_phase3t/multireso_worker_02
NEW_BRANCH = topconf-phase3t-multireso-worker-r2
NEW_BASE_COMMIT = ee8d3a157dd329116e5ea8607a14446f90f26e8d
```

The new run is a clean full-split infrastructure reexecution from the first
authorized E1 case. It must plan and account for all 42,471 valid E1 cases;
it must not resume at case 16,630 or reuse `multireso_worker_01`.

## Frozen authorization and protocol

```text
AUTHORIZATION_ID = P3T-2026-09-13-01
AUTHORIZATION = UNCHANGED
SCIENTIFIC_PROTOCOL_CHANGED = NO
DATASET = PartialEdit v1.1 E1
CASE_POPULATION = all valid E1 cases; expected 42471
CASE_ORDER = official CSV E1 order
MODEL = MultiResoModel-Simple commit 0f69db3a2d654de47822d951fe6ad256bbaac9ba
CHECKPOINT_SHA256 = 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32
SCALES = 0.02, 0.04, 0.08, 0.16, 0.32, 0.64 seconds; all six independently preserved
OUTPUT_SEMANTICS = unchanged native raw outputs, native class columns, utterance output
GT_ACCESS = NO
SCIENTIFIC_METRICS_COMPUTED = 0
RESULT_BASED_SELECTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
```

The only intended change is correction of execution-environment identity and
namespace ownership. The dataset, model, checkpoint, case order, scale policy,
output semantics, retry policy, and authorization are unchanged.

## Authorized environment gate

The frozen source is
`research_assurance/topconf/PHASE3V_MULTIRESo_ENVIRONMENT_V1.md`. The new
invocation must satisfy all of the following before inference starts:

```text
AUTHORIZED_EXECUTABLE = F:\项目\申请实验室  TTS项目\envs\topconf-phase3v-multireso-py310\Scripts\python.exe
PYTHON = 3.10.11
TORCH = 1.13.1+cu117
TORCHAUDIO = 0.13.1+cu117
FAIRSEQ = 0.12.2
CUDA = available
GPU = NVIDIA GeForce RTX 4060 Laptop GPU
CHECKPOINT_STRICT_LOAD = 0 missing / 0 unexpected
```

## Ownership and concurrent work

The new namespace has an atomic owner lock and invocation/environment identity
checks. A second active writer, wrong invocation, wrong environment, stale
lock without an explicit safe recovery path, or completed-namespace reuse must
be rejected. There is no CFPRF operation in this recovery. CFPRF was observed
as another Codex-owned process and was not terminated, changed, resumed, or
otherwise operated by this task.

## Recovery decision

```text
SCIENTIFIC_OUTCOMES_USED_FOR_RECOVERY_DECISION = NO
OLD_NAMESPACE_ELIGIBLE_FOR_SCIENCE = NO
NEW_RUN_REQUIRED = YES
PHASE3T_CLOSURE = remains governed by frozen authorization; no closure change
```

