# Phase3T MultiReso Execution Integrity Handoff v1

Status: **COMPLETED / INFRASTRUCTURE-INTEGRITY ONLY**  
Handoff date: 2026-09-14 (Asia/Shanghai)

This handoff records execution provenance and structural completeness. It is
not a scientific result report. No score, metric, ranking, selection, or
exclusion is interpreted here.

## Superseded historical attempt

The prior attempt remains preserved in its original namespace and is not
eligible for Phase3T evaluation:

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
OLD_STOP_ACTION = stopped after provenance capture; no resume
```

The old child executable did not match the frozen authorized executable,
despite its parent being the authorized environment. The old namespace,
logs, manifests, ledgers, and supersession markers were preserved. Duplicate
old-writer and supervisor provenance is recorded separately in:

```text
research_assurance/topconf/PHASE3T_MULTIRRESO_OLD_DUPLICATE_WRITER_PROVENANCE_V1.md
research_assurance/topconf/PHASE3T_MULTIRRESO_HIDDEN_OLD_WRITER_PROVENANCE_V1.md
```

The old writer/supervisor processes were stopped only after provenance
capture. No old output was resumed, overwritten, or used for science.

## Authorized recovery run

```text
AUTHORIZATION_ID = P3T-2026-09-13-01
FROZEN_AUTHORIZATION_BASE_COMMIT = 62994f0982149583a86533b20648dae07a789fa7
RECOVERY_CODE_BASE_COMMIT = ee8d3a157dd329116e5ea8607a14446f90f26e8d
INVOCATION_ID = PHASE3T_MRM_FULL_E1_002
BRANCH = topconf-phase3t-multireso-worker-r2
FINAL_REPOSITORY_COMMIT = 418593d2c9f0c90f7c663fa001fa15f8839bde7f
NAMESPACE = results/topconf_phase3t/multireso_worker_02
DATASET = PartialEdit_v1.1 E1
CASE_ORDER = official CSV E1 order
CASE_POPULATION = all valid E1 cases
PLANNED = 42471
TERMINAL = 42471
VALID_INFERENCE = 42438
AUDIO_LOAD_FAILURE = 33
MISSING = 0
```

The new run started from the first authorized E1 case in a fresh dedicated
namespace. The authorization and scientific protocol were unchanged. The 33
audio-load failures are terminal infrastructure records and are not
population exclusions.

## Environment and model gates

```text
AUTHORIZED_EXECUTABLE = F:\项目\申请实验室  TTS项目\envs\topconf-phase3v-multireso-py310\Scripts\python.exe
PYTHON = 3.10.11
TORCH = 1.13.1+cu117
TORCHAUDIO = 0.13.1+cu117
FAIRSEQ = 0.12.2
CUDA = available
GPU = NVIDIA GeForce RTX 4060 Laptop GPU
MODEL = MultiResoModel-Simple
MODEL_REPOSITORY_COMMIT = 0f69db3a2d654de47822d951fe6ad256bbaac9ba
CHECKPOINT_ARCHIVE_SHA256 = 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32
STRICT_LOAD_MISSING = 0
STRICT_LOAD_UNEXPECTED = 0
```

Six native temporal scales were preserved independently:
`0.02, 0.04, 0.08, 0.16, 0.32, 0.64` seconds, plus the native utterance
two-class output. No ground truth was supplied to the runner; no scientific
metrics were computed; no result-based scale selection or case exclusion was
performed.

## Structural audit

The completed namespace has one completed owner lock and no active MultiReso
writer or old supervisor at handoff. The final lock and summary manifest agree
on invocation, namespace, branch, commit, planned population, terminal count,
valid count, and failure count.

```text
RAW_JSONL = 42471 lines; duplicates 0; parse/status errors 0
CASE_LEDGER = 42471 lines; duplicates 0; VALID 42438; FAILED 33
OUTPUT_MANIFEST_JSONL = 42471 lines; duplicates 0
CASE_SET_EQUAL_TO_CANONICAL_E1 = YES
CASE_INDEXES_VALID = YES
VALID_NATIVE_SCHEMA_ERRORS = 0
RAW_OUTPUT_HASH_MISMATCHES = 0
OUTPUT_MANIFEST_HASH_MISMATCHES = 0
GT_KEYS_IN_RAW_RECORDS = 0
```

All valid records contain the six expected scales, native class columns,
utterance output, finite values, and shape metadata. The attempt ledger has
42,482 append-only start rows, 42,475 unique case/attempt pairs, and 7
retained duplicate start rows from earlier crash/resume boundaries; all 7
correspond to cases with terminal evidence and none is a backfill row. The
33 missing audio-load start rows were repaired by append-only structural
backfill; raw output and the terminal case ledger were not modified.

```text
RETRY_EVENTS = 4
RETRY_POLICY = CUDA_OOM only; batch size 4 -> 1; no crop/window/scale change
BACKFILL_REPORT = MULTIRESO_ATTEMPT_LEDGER_BACKFILL_V1.json
SCIENTIFIC_METRICS_COMPUTED = 0
GT_ACCESSED = NO
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_CASE_EXCLUSIONS = 0
```

## Completed artifact hashes

SHA-256 hashes below cover the completed namespace artifacts at handoff:

```text
multireso_raw_v1.jsonl
00E502AA418DC1279AE19F72E48E1617A4BCF56014307FE6E0BC666736E37925
multireso_case_ledger_v1.jsonl
24FAE99EEE5BE1E3CDE8D912AE8EF4C12DF6423A7705599F4C7C26DA97EA5733
multireso_output_manifest_v1.jsonl
4A606CA23126AF50CDDF3ACA1AABA536BB03B96DDF4C962DA924080034F521AC
multireso_attempts_v1.jsonl
D1C66CCF73538ECD810F56ABDD29402D85A38CA5A22323D83EED17869FCA204E
multireso_retry_ledger_v1.jsonl
87D9A2B86FBBCA61FFBCEC5788E3B205B0509D150F8A1D896EB0CF1EADC9F3AD
MULTIRESO_PHASE3T_RAW_OUTPUT_MANIFEST_V1.json
0EE148D1305675369D7B8772BD37A2C39E769A4C0CA8A9D335756A6DC6BB2333
worker_owner_lock.json
7339EF17B604F8784B55104B55A86F98AB05A6D345009587D53B49444E369DB0
MULTIRESO_ATTEMPT_LEDGER_BACKFILL_V1.json
ADAD92B6AE8B54D8C96C0D8EF2A84058D6FFFD38802374A6E6EED09211638B22
```

## Scope boundary and handoff

CFPRF was not operated by this task. A final read-only process check found no
active CFPRF process. Phase3T closure and authorization remain governed by
the frozen control documents; this handoff does not authorize closure or
scientific interpretation.

The mainline `topconf-dl-robustness` worktree was not modified by this task.
The completed changes and this handoff remain isolated on
`topconf-phase3t-multireso-worker-r2`.
