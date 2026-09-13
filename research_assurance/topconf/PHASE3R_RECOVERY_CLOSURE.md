# Phase 3R External Reproduction Recovery Closure

Status: **BLOCKED_PENDING_RECOVERY**

`ORIGINAL_PHASE3_CLOSURE = BLOCKED`

`PHASE3R_RECOVERY_CLOSURE = BLOCKED_PENDING_RECOVERY`

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
| PartialEdit E1 full audio | `NOT_STARTED` | bounded official Zenodo attempts after authorization commit |
| PartialSpoof v1.2 full audio | `BLOCKED_FROM_PHASE3` | bounded recovery retry only; previous invalid archive and endpoint failures retained |
| PartialSpoof MultiReso | `NOT_STARTED` | inspect official repository route before checkpoint download |
| CFPRF | `INFRASTRUCTURE_SMOKE_PASS` | do not repeat unchanged smoke; full run requires validated audio |
| SAL | `DEFERRED_CHECKPOINT_UNAVAILABLE` | no self-training or unofficial checkpoint |
| BAM | `BLOCKED_RIGHTS_CLEARANCE` | provenance/rights inspection only |
| GPU environment | `NOT_AVAILABLE_UNVERIFIED` | audit actual accessible environments; no paid resource creation |

## Recovery attempt ledger

| Attempt ID | Timestamp | Official URL | HTTP status | Bytes received | Expected size | Official MD5 | Failure category |
|---|---|---|---:|---:|---:|---|---|
| `P3R-2026-09-13-01-E1-001` | `2026-09-13T16:12:45+08:00` | `https://zenodo.org/records/18829689/files/E1.tar.gz?download=1` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |
| `P3R-2026-09-13-01-E1-002` | `2026-09-13T16:14:11+08:00` | `https://zenodo.org/api/records/18829689/files/E1.tar.gz/content` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |
| `P3R-2026-09-13-01-E1-003` | `2026-09-13T16:15:21+08:00` | `https://zenodo.org/records/18829689/files/E1.tar.gz?download=1` | `504` | `0` | approximately 3.4 GB | `1f489d2ff488ddd6c9b655127725af2f` | `HTTP_504` |

## Required recovery fields

```text
PARTIALEDIT_E1_MATERIALIZATION = BLOCKED_EXTERNAL_SERVICE_AFTER_3_ATTEMPTS
PARTIALEDIT_E1_CHECKSUM = NOT_STARTED
PARTIALEDIT_FULL_AUDIO_PARSER = NOT_STARTED
PARTIALSPOOF_RECOVERY_ATTEMPTS = 0 OF 3
PARTIALSPOOF_MATERIALIZATION = BLOCKED_FROM_PHASE3_PENDING_BOUNDED_RETRY
PARTIALSPOOF_MULTIRESO_PROVENANCE = NOT_STARTED
CFPRF_FULL_REPRODUCTION = BLOCKED_UNTIL_FULL_AUDIO_VALIDATION
SAL_STATUS = DEFERRED_CHECKPOINT_UNAVAILABLE
BAM_RIGHTS_STATUS = UNRESOLVED
LLAMAPARTIALSPOOF_FALLBACK_TRIGGERED = NO
FULL_AUDIO_EXTERNAL_DATASETS = 0
EXTERNAL_FUNCTIONAL_PARADIGMS = 0 FULL / 1 INFRASTRUCTURE_ONLY
OFFICIAL_REPRODUCTIONS = 0 FUNCTIONAL
UNIFIED_EVALUATOR_COMPATIBILITY = SCHEMA_ONLY_NOT_END_TO_END
FAILURE_ACCOUNTING = PRIOR_FAILURES RETAINED; RECOVERY LEDGER TO BE APPENDED
RESULT_BASED_SUBSTITUTIONS = 0
```

## Stop condition

If the bounded official recovery paths fail, the closure remains
`BLOCKED_EXTERNAL_SERVICE` or another explicit infrastructure class. No
unofficial data, self-generated checkpoint, forced CPU full benchmark, or
Phase 4 action may be used to turn this record into PASS.
