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
| PartialSpoof v1.2 full audio | `BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS` | all three 3R bounded probes returned HTTP 504 with zero archive bytes; previous failures retained |
| PartialSpoof MultiReso | `SOURCE_ROUTE_VERIFIED_CHECKPOINT_BLOCKED` | official commit/script/Zenodo route verified; bounded checkpoint probe failed |
| LlamaPartialSpoof fallback | `REPOSITORY_SPLIT_METADATA_PASS_AUDIO_BLOCKED` | availability-only fallback triggered; official split metadata is validated, but audio archives remain unavailable |
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
| `P3R-2026-09-13-01-PS-001` | `2026-09-13` (shell seconds not persisted) | `https://zenodo.org/records/5766198/files/database_eval.tar.gz?download=1` | `504` | `0` | approximately 5.8 GB | `79c7c834d0d9979ecd374a98a059ea19` | `HTTP_504` |
| `P3R-2026-09-13-01-PS-002` | `2026-09-13` (shell seconds not persisted) | `https://zenodo.org/records/4817532/files/database_eval.tar.gz.aa?download=1` | `504` | `0` | approximately 2.1 GB | `2f2087bb3b9c32b9f2ac24028e77a734` | `HTTP_504` |
| `P3R-2026-09-13-01-PS-003` | `2026-09-13` (shell seconds not persisted) | `https://zenodo.org/record/4817532/files/database_eval.tar.gz.ab?download=1` | `504` | `0` | approximately 2.1 GB | `2e79c7cec8b05f4231e0144bd633174d` | `HTTP_504` |

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

The official repository split metadata was materialized through the GitHub
Contents/Git blob API at commit `61d072e472dbbec6c17b3a591d3ae046b7d8ef72`:

| Artifact | Official Git blob SHA | Local bytes | Local SHA256 | Validation |
|---|---|---:|---|---|
| `split/train.spk` | `4495c88831a21c9f3838b01e806bf7b1b7ceebd9` | 97 | `0BFD2564E7A41006CDB4BB06A7E357AF7960E4C112EFD54D358B28BA718FA992` | 20 unique numeric speakers |
| `split/train.utt` | `ab08e9916455466f32a549fe9dfac2af8ef5c4db` | 1,405,900 | `E754DA1867C06A34B49D3EADA45BAC8F6612A49BA367F6DB42A1452F2B77ADF6` | 29,880 unique utterance IDs |
| `split/test.spk` | `fe4128811545702ac7a0b2ec682518d7e3f0e611` | 284 | `524BA2D73AFA269D57967828D1B941B8EB4FFCD2DB80607AE1DA495E00CF9AA6` | 59 unique numeric speakers |
| `split/test.utt` | `bed7ddb43fa36de16c3ae500f950188434e2225d` | 2,120,692 | `C39934BE2DD4EFEF5FC4B9CBE61C742A5C584A89E696731D21C8D96D3E8CD375` | 46,348 unique utterance IDs |

This is repository metadata validation only. It does not establish audio
existence, waveform duration alignment, or a full-audio fallback dataset.

## Required recovery fields

```text
PARTIALEDIT_E1_MATERIALIZATION = BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS
PARTIALEDIT_E1_CHECKSUM = BLOCKED_NO_ARCHIVE
PARTIALEDIT_FULL_AUDIO_PARSER = BLOCKED_NO_AUDIO
PARTIALSPOOF_RECOVERY_ATTEMPTS = 3 OF 3 FAILED_HTTP_504
PARTIALSPOOF_MATERIALIZATION = BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS
PARTIALSPOOF_MULTIRESO_REPO_COMMIT = 847347aaec6f65c3c6d2f17c63515b826b94feb3
PARTIALSPOOF_MULTIRESO_PROVENANCE = SOURCE_ROUTE_VERIFIED
PARTIALSPOOF_MULTIRESO_CHECKPOINT_SHA256 = NOT_MATERIALIZED
PARTIALSPOOF_MULTIRESO_STATUS = BLOCKED_EXTERNAL_SERVICE_AFTER_PROBE
CFPRF_FULL_REPRODUCTION = BLOCKED_UNTIL_FULL_AUDIO_VALIDATION
SAL_STATUS = DEFERRED_CHECKPOINT_UNAVAILABLE
BAM_RIGHTS_STATUS = UNRESOLVED
LLAMAPARTIALSPOOF_FALLBACK_TRIGGERED = YES_AVAILABILITY_ONLY_NO_MODEL_RESULTS
LLAMAPARTIALSPOOF_STATUS = REPOSITORY_SPLIT_METADATA_PASS_AUDIO_NOT_MATERIALIZED
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

## Append-only official rights and checkpoint inspection

Inspection date: `2026-09-13` (read-only; no restricted artifact was
downloaded or used).

### BAM

The official repository API reports no declared repository license
(`license = null`) at `https://api.github.com/repos/media-sec-lab/BAM`. Its
default branch tree contains source/model code but no checkpoint, weight, or
license artifact. The only official release, `version1.0.0`, is published at
`https://github.com/media-sec-lab/BAM/releases/tag/version1.0.0` and has no
release assets. The official README directs users to a Google Drive file for
`./checkpoint/model.ckpt`, but this does not resolve redistribution or usage
rights for this recovery. Accordingly:

`BAM_RIGHTS_STATUS = UNRESOLVED_NO_CHECKPOINT_ASSET_LICENSE_OR_CLEARANCE`

`BAM_REPRODUCTION_STATUS = NOT_USED_AND_NOT_COUNTED`

### SAL

The official repository API reports MIT source licensing and zero releases at
`https://api.github.com/repos/SentryMao/SAL`. The frozen official tree contains
configs and model source but no checkpoint or weight artifact. The missing
checkpoint remains a prerequisite for an auditable evaluation; no self-trained
or unofficial checkpoint is admitted.

`SAL_STATUS = DEFERRED_CHECKPOINT_UNAVAILABLE_CONFIRMED_BY_OFFICIAL_TREE`

These inspections do not alter the recovery gate: full-audio datasets remain
zero, functional external paradigms remain below two, and functional official
reproductions remain zero.

## Append-only current-state continuity audit

The attachment's reported recovery base `9873ac4b527f3bd72499b8e8230be8a337c9dd2a`
is superseded by the continuous TopConf Phase 3/3R history. The current
authoritative state is:

`CURRENT_HEAD_SUPERSEDES_REPORTED_HEAD = YES`

`LOCAL_HEAD = fe0b87ade6a2b069dd80d0e405ae3e1565c72223`

`REMOTE_HEAD = fe0b87ade6a2b069dd80d0e405ae3e1565c72223`

`WORKING_TREE = CLEAN`

`ORIGINAL_PHASE3_CLOSURE_UNCHANGED_SINCE_RECOVERY_BASE = YES`

The original Phase 3 closure remains `BLOCKED`; no reset, checkout, rebase,
amend, force push, or history rewrite was performed.
