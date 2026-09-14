# Phase3T Crash Recovery Audit V1

Status: **PASS — EXISTING AUTHORIZED ARTIFACTS RECONSTRUCTED AND VERIFIED**

This is a new recovery record. Historical Phase3, Phase3R, Phase3S, Phase3U,
Phase3V, and the frozen Phase3T authorization/closure files are unchanged.
The audit was performed on 2026-09-14 after the interrupted session resumed.

## Git and authorization identity

```text
BRANCH = topconf-dl-robustness
LOCAL_HEAD_AT_AUDIT = 64887a1585f48af9895e8a09370d9de88c22b761
REMOTE_HEAD_AT_AUDIT = 64887a1585f48af9895e8a09370d9de88c22b761
WORKING_TREE_AT_AUDIT = clean before recovery compatibility edits
PHASE3T_AUTHORIZATION = P3T-2026-09-13-01
PHASE3T_AUTHORIZATION_COMMIT = ee8d3a1
PHASE3T_AUTHORIZATION_SHA256 = A23327AA781ADAFC2302EADF3F552B9C50C5A775DC237918B3730703AC219331
PHASE3T_BASE_COMMIT = 62994f0982149583a86533b20648dae07a789fa7
DATASET = PartialEdit v1.1 E1
DATASET_CASES = 42471
DATASET_CSV_SHA256 = ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC
DATASET_ARCHIVE_MD5 = 1f489d2ff488ddd6c9b655127725af2f
DATASET_ARCHIVE_SHA256 = F4BB1A632EED8DDC66BB9285DE8B4BC07192D0539385EFE9AFC9EA04AEF3DDCB
CASE_MANIFEST_SHA256 = E30914242156A9383E0B71755FCE85CEDE01DB5CA91165ADCDB3EBF33F315FEE
```

The authorization is committed and frozen. The local CSV/archive and the
materialized E1 audio were not downloaded, replaced, or modified during
recovery.

## Live-process check

```text
LIVE_PROCESSES_FOUND = NO CFPRF OR MULTIRESO INFERENCE PROCESS
GPU = NVIDIA GeForce RTX 4060 Laptop GPU
GPU_MEMORY_AT_CHECK = approximately 2017 MiB / 8188 MiB, desktop processes only
```

No duplicate inference was started during this recovery.

## Invocation classification

| Invocation / namespace | Classification | Recovered decision |
|---|---|---|
| Mainline `results/topconf_phase3t/cfprf` resume chain | `AUTHORIZED_PARTIAL_RESUMABLE` → complete | Same authorized namespace was resumed using terminal-case skipping; no completed case was overwritten. The runner did not persist a separate invocation ID. |
| Mainline `results/topconf_phase3t/multireso` | `SUPERSEDED_INFRASTRUCTURE_ATTEMPT` | 7,810 cases; terminated after parallel ownership conflict; preserved and excluded from formal output. |
| Worker `multireso_worker_01` | `SUPERSEDED_INFRASTRUCTURE_ATTEMPT` | 7,880 cases; schema lacked the authorized native utterance output; preserved and excluded. |
| Worker-r2 `multireso_worker_02`, `PHASE3T_MRM_FULL_E1_002` | `AUTHORIZED_COMPLETE` | Exclusive-writer handoff passed; mainline only read-only verified and ingested this namespace. |

No artifact was deleted. Owner selection used completion count, namespace
integrity, schema compliance, and authorization provenance only; no score,
metric, threshold, or ranking was inspected.

## CFPRF recovery accounting

```text
CFPRF_INVOCATION = mainline authorized resume chain; separate invocation ID not persisted
CFPRF_NAMESPACE = results/topconf_phase3t/cfprf
CFPRF_PLANNED = 42471
CFPRF_RAW = 42471
CFPRF_TERMINAL = 42471
CFPRF_VALID = 42455
CFPRF_FAILED = 16
CFPRF_FAILURE_CLASSES = MODEL_INFERENCE_FAILURE:16 (retained MemoryError records)
CFPRF_MISSING = 0
CFPRF_ORPHAN = 0
CFPRF_DUPLICATE_TERMINAL = 0
CFPRF_ORDER_OR_INDEX_MISMATCH = 0
CFPRF_RETRIES = 3
CFPRF_RETRY_CASES = E1/p278/p278_261_edited_partial_16k.wav; E1/s5/s5_252_edited_partial_16k.wav; E1/s5/s5_298_edited_partial_16k.wav
CFPRF_RAW_SHA256 = CF86B16808DEC9580B46FA89DDBB49C8121E392B749ED7DF7B5A9F883EC8C493
CFPRF_ATTEMPTS_SHA256 = D5B213794C9C0970EFEF5BE804FEA47D0F4763B71E445EBD22AA3B6CE83C6CCD
CFPRF_OUTPUT_MANIFEST_SHA256 = 1ECA30A6F95B166D4466989AE0CB33A79C6314AFB710ACCCC6C42E47279F407C
```

The CFPRF attempts file contains 84,945 rows and 42,474 unique case-attempt
keys. All terminal attempts and all retry starts are represented. The 16
inference failures remain terminal records and are not silently excluded.

## MultiReso recovery accounting

```text
MULTIRESO_INVOCATION = PHASE3T_MRM_FULL_E1_002
MULTIRESO_EXECUTION_OWNER = PARALLEL_WORKER_R2
MULTIRESO_NAMESPACE = F:/项目/申请实验室  TTS项目/AudiobookBench-CN-phase3t-multireso-worker-r2/results/topconf_phase3t/multireso_worker_02
MULTIRESO_PLANNED = 42471
MULTIRESO_RAW = 42471
MULTIRESO_TERMINAL = 42471
MULTIRESO_VALID = 42438
MULTIRESO_FAILED = 33
MULTIRESO_FAILURE_CLASSES = AUDIO_LOAD_FAILURE:33
MULTIRESO_MISSING = 0
MULTIRESO_ORPHAN = 0
MULTIRESO_DUPLICATE_TERMINAL = 0
MULTIRESO_ORDER_OR_INDEX_MISMATCH = 0
MULTIRESO_RETRIES = 4
MULTIRESO_RETRY_POLICY = preauthorized CUDA OOM batch-size reduction 4→1; waveform/model semantics unchanged
MULTIRESO_SCALES = 6/6 native temporal scales preserved independently
MULTIRESO_RAW_SHA256 = 00E502AA418DC1279AE19F72E48E1617A4BCF56014307FE6E0BC666736E37925
MULTIRESO_ATTEMPTS_SHA256 = D1C66CCF73538ECD810F56ABDD29402D85A38CA5A22323D83EED17869FCA204E
MULTIRESO_CASE_LEDGER_SHA256 = 24FAE99EEE5BE1E3CDE8D912AE8EF4C12DF6423A7705599F4C7C26DA97EA5733
MULTIRESO_OUTPUT_MANIFEST_JSONL_SHA256 = 4A606CA23126AF50CDDF3ACA1AABA536BB03B96DDF4C962DA924080034F521AC
MULTIRESO_RETRY_LEDGER_SHA256 = 87D9A2B86FBBCA61FFBCEC5788E3B205B0509D150F8A1D896EB0CF1EADC9F3AD
MULTIRESO_HANDOFF_SHA256 = 2005CE7AB93347FD15A0A5D556AD9C28A457E81F20A50FA7F599214F7C46B60A
```

The r2 attempts history contains 42,482 append-only rows and seven retained
duplicate start rows from infrastructure restarts. It has no duplicate
terminal case and no raw/ledger set mismatch. The 33 audio-load failures are
retained in failure accounting.

## Environment identity

```text
CFPRF_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3s-cfprf-py310/Scripts/python.exe
CFPRF_PYTHON = 3.10.11
CFPRF_TORCH = 2.2.2+cu121
CFPRF_FAIRSEQ = 1.0.0a0
CFPRF_GPU = NVIDIA GeForce RTX 4060 Laptop GPU
CFPRF_CHECKPOINTS = authorized FDN/PRN/XLSR hashes from authorization

MULTIRESO_ENVIRONMENT = F:/项目/申请实验室  TTS项目/envs/topconf-phase3v-multireso-py310/Scripts/python.exe
MULTIRESO_PYTHON = 3.10.11
MULTIRESO_TORCH = 1.13.1+cu117
MULTIRESO_FAIRSEQ = 0.12.2
MULTIRESO_GPU = NVIDIA GeForce RTX 4060 Laptop GPU
MULTIRESO_CHECKPOINT_ARCHIVE_SHA256 = 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32
```

Both identities match the frozen authorization and Phase3V records. Different
executable paths were not treated as environment mismatches.

## Validation and compatibility findings

```text
CFPRF_T2_RAW_VALIDATION = PASS
MULTIRESO_T2_RAW_VALIDATION = PASS
CFPRF_ADAPTER = PASS
MULTIRESO_ADAPTER = PASS
UNIFIED_EVALUATOR_END_TO_END = PASS
LEVEL1_METRICS = frame AUROC and frame AUPRC only, per native head/scale
LD_DR95 = NO
RANGEEER = NO
WHETHER_A = DEFERRED
WHETHER_B = NOT_RUN
RQ1 = NOT_RUN
```

The validator compatibility correction preserves official CFPRF refined
proposal ends without clipping them to audio duration; the official
`decoder_reg` path clamps negative starts but does not clip refined ends. The
adapter additionally normalizes only decimal-grid floating-point roundoff at
canonical temporal endpoints. Neither change modifies native raw outputs,
scores, model execution, or ground-truth access.

```text
RESULT_BASED_SELECTIONS = 0
RESULT_BASED_EXCLUSIONS = 0
RESULT_BASED_SCALE_SELECTIONS = 0
RESULT_BASED_HEAD_SELECTIONS = 0
GT_ACCESSED_BY_MODEL = NO
SCIENTIFIC_ROLE = LEVEL_1_EXTERNAL_FUNCTIONAL_VALIDATION
```

The remaining work after this audit is administrative closure: commit the
recovery records and compatibility tests, create the final closure and raw
manifest records, validate the final Git state, and push the authorized
branch. Phase4 and confirmatory execution remain closed.
