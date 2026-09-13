# Phase 3R External Reproduction Recovery Closure

Status: **BLOCKED — OFFICIAL RECOVERY RESOURCES UNAVAILABLE**

`ORIGINAL_PHASE3_CLOSURE = BLOCKED`

`PHASE3R_RECOVERY_CLOSURE = BLOCKED`

`READY_FOR_PHASE4_REVIEW = NO`

`READY_FOR_PHASE4_CONFIRMATORY_DESIGN_FREEZE = NO`

`READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO`

This document is the append-only recovery record. It does not modify or
replace `PHASE3_EXTERNAL_REPRODUCTION_CLOSURE.md`.

## Recovery scope and current gate

The recovery target is at least one fully validated external audio dataset,
one full-audio parser pass, two functional external paradigms, and one
auditable official reproduction. No result-based substitution is permitted.

| Gate | Current status | Evidence / next permitted action |
|---|---|---|
| PartialEdit E1 full audio | `BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS` | all authorized bounded attempts returned HTTP 504 with zero archive bytes |
| PartialSpoof v1.2 full audio | `BLOCKED_FROM_PHASE3` | bounded recovery retry only; previous invalid archive and endpoint failures retained |
| PartialSpoof MultiReso | `SOURCE_ROUTE_VERIFIED_CHECKPOINT_BLOCKED` | official commit/script/Zenodo route verified; bounded checkpoint probe failed |
| CFPRF | `INFRASTRUCTURE_SMOKE_PASS` | do not repeat unchanged smoke; full run requires validated audio |
| SAL | `DEFERRED_CHECKPOINT_UNAVAILABLE` | no self-training or unofficial checkpoint |
| BAM | `BLOCKED_RIGHTS_CLEARANCE` | provenance/rights inspection only |
| GPU environment | `LOCAL_GPU_VISIBLE_RUNTIME_INCOMPATIBLE` | RTX 4060 Laptop 8 GB and CUDA 12.1 are visible in an existing environment; official fairseq import fails under that environment's Python 3.12, so CFPRF GPU execution is not yet validated |

## Recovery attempt ledger

| Attempt ID | Timestamp | Official URL | HTTP status | Bytes received | Expected size | Official MD5 | Failure category |
|---|---|---|---:|---:|---:|---|---|
| `P3R-2026-09-13-01-E1-001` | `2026-09-13T16:12:45+08:00` | `https://zenodo.org/records/18829689/files/E1.tar.gz?download=1` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |
| `P3R-2026-09-13-01-E1-002` | `2026-09-13T16:14:11+08:00` | `https://zenodo.org/api/records/18829689/files/E1.tar.gz/content` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |
| `P3R-2026-09-13-01-E1-003` | `2026-09-13T16:15:21+08:00` | `https://zenodo.org/records/18829689/files/E1.tar.gz?download=1` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |
| `P3R-2026-09-13-01-MR-001` | `2026-09-13T16:17:47+08:00` | `https://zenodo.org/record/6674660/files/multi-reso.tar.gz?download=1` | `504` | `0` | not returned by endpoint | `NOT_AVAILABLE` | `HTTP_504` |
| `P3R-2026-09-13-01-LPS-001` | `2026-09-13T16:24:29+08:00` | `https://zenodo.org/records/14214149/files/label_R01TTS.0.a.txt?download=1` | `504` | `0` | approximately 10.5 MB | `86c60280e4cb2957542b365c3c8f52ac` | `HTTP_504` |

## Availability fallback

`LLAMAPARTIALSPOOF_FALLBACK_TRIGGERED = YES`

The trigger is availability-only: the three authorized PartialSpoof recovery
attempts were exhausted with `BLOCKED_EXTERNAL_SERVICE` before this source was
selected, and no model result was observed beforehand. The official fallback
source is LlamaPartialSpoof v1.0.b at Zenodo record `14214149`, with the
official repository `hieuthi/LlamaPartialSpoof` and CC BY 4.0 metadata. Its
large audio archives remain unmaterialized; it is not yet an evaluation
dataset.

| Fallback artifact | Official source | Official identity | Local status |
|---|---|---|---|
| `label_R01TTS.0.a.txt` | `https://zenodo.org/records/14214149/files/label_R01TTS.0.a.txt?download=1` | MD5 `86c60280e4cb2957542b365c3c8f52ac`, approximately 10.5 MB | `ATTEMPT_1_FAILED_HTTP_504` |
| `label_R01TTS.0.b.txt` | `https://zenodo.org/records/14214149/files/label_R01TTS.0.b.txt?download=1` | MD5 `6f5f94d3dbca70c011370ded232c8519`, approximately 14.2 MB | `NOT_PROBED` |
| `R01TTS.0.a.tgz` | `https://zenodo.org/records/14214149/files/R01TTS.0.a.tgz?download=1` | MD5 `685acfe986b50baaf3e25e9d5e3091a4`, approximately 15.4 GB | `NOT_PROBED` |
| `R01TTS.0.b.tgz` | `https://zenodo.org/records/14214149/files/R01TTS.0.b.tgz?download=1` | MD5 `a4de860a845816fa65785dddd7849700`, approximately 12.8 GB | `NOT_PROBED` |

## Required recovery fields

```text
PARTIALEDIT_E1_MATERIALIZATION = BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS
PARTIALEDIT_E1_CHECKSUM = NOT_STARTED
PARTIALEDIT_FULL_AUDIO_PARSER = NOT_STARTED
PARTIALSPOOF_RECOVERY_ATTEMPTS = 0 OF 3
PARTIALSPOOF_MATERIALIZATION = BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS
PARTIALSPOOF_MULTIRESO_REPO_COMMIT = 847347aaec6f65c3c6d2f17c63515b826b94feb3
PARTIALSPOOF_MULTIRESO_PROVENANCE = SOURCE_ROUTE_VERIFIED
PARTIALSPOOF_MULTIRESO_CHECKPOINT_SHA256 = NOT_MATERIALIZED
PARTIALSPOOF_MULTIRESO_STATUS = BLOCKED_EXTERNAL_SERVICE_AFTER_PROBE
CFPRF_FULL_REPRODUCTION = BLOCKED_UNTIL_FULL_AUDIO_VALIDATION
SAL_STATUS = DEFERRED_CHECKPOINT_UNAVAILABLE
BAM_RIGHTS_STATUS = UNRESOLVED
LLAMAPARTIALSPOOF_FALLBACK_TRIGGERED = YES_AVAILABILITY_ONLY_NO_MODEL_RESULTS
LLAMAPARTIALSPOOF_STATUS = BLOCKED_EXTERNAL_SERVICE_AFTER_METADATA_PROBE; AUDIO_NOT_MATERIALIZED
FULL_AUDIO_EXTERNAL_DATASETS = 0
EXTERNAL_FUNCTIONAL_PARADIGMS = 0 FULL / 1 INFRASTRUCTURE_ONLY
OFFICIAL_REPRODUCTIONS = 0 FUNCTIONAL
UNIFIED_EVALUATOR_COMPATIBILITY = SCHEMA_ONLY_NOT_END_TO_END
FAILURE_ACCOUNTING = PRIOR_FAILURES AND RECOVERY_ATTEMPTS RETAINED; NO SILENT SKIP
RESULT_BASED_SUBSTITUTIONS = 0
```

## Recovery exit gate

| Required condition | Observed status | Gate |
|---|---|---|
| At least one full-audio external dataset | `0` | `FAIL` |
| At least one full-audio parser pass | `0` | `FAIL` |
| At least two functional external paradigms | `0 full; 1 infrastructure-only` | `FAIL` |
| At least one functional official reproduction | `0` | `FAIL` |
| Failure accounting, zero result-based substitutions, pilot boundary intact | `PASS / 0 / PASS` | `PASS` |

Therefore the recovery exit gate is not met. The original Phase 3 `BLOCKED`
closure remains authoritative, and this recovery record stops without any
Phase 4 authorization.

## Stop condition

If the bounded official recovery paths fail, the closure remains
`BLOCKED_EXTERNAL_SERVICE` or another explicit infrastructure class. No
unofficial data, self-generated checkpoint, forced CPU full benchmark, or
Phase 4 action may be used to turn this record into PASS.
`GPU_EXECUTION_ENVIRONMENT_STATUS = LOCAL_RTX4060_8GB_CUDA12.1_VISIBLE_IN_EXISTING_ENVIRONMENT`

`GPU_RUNTIME_COMPATIBILITY = OFFICIAL_FAIRSEQ_IMPORT_FAILED_PYTHON312_DATACLASS_INCOMPATIBILITY`

`FULL_REPRODUCTION_CPU_FEASIBILITY = IMPRACTICAL_FOR_FULL_AUDIO`
