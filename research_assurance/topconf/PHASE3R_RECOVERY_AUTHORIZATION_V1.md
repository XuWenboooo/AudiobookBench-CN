# Phase 3R External Reproduction Recovery Authorization v1

Status: **AUTHORIZED FOR BOUNDED INFRASTRUCTURE RECOVERY / NOT CONFIRMATORY**

This authorization is append-only with respect to the original Phase 3
closure. It authorizes only recovery of official external data, checkpoint,
rights/provenance, and execution-environment gates. It does not authorize
RQ1/RQ2/RQ3, robustness analysis, attack/defense, model ranking, result-based
substitution, or Phase 4 execution.

```text
PHASE3R_AUTHORIZATION_ID = P3R-2026-09-13-01
RECOVERY_BASE_COMMIT = 9873ac4b527f3bd72499b8e8230be8a337c9dd2a
ORIGINAL_PHASE3_CLOSURE = BLOCKED (research_assurance/topconf/PHASE3_EXTERNAL_REPRODUCTION_CLOSURE.md)

AUTHORIZED_DATASETS = PartialEdit E1; PartialSpoof v1.2; LlamaPartialSpoof fallback only if trigger is met
AUTHORIZED_DATASET_SOURCES =
  PartialEdit v1.1: https://zenodo.org/records/18829689
  PartialSpoof v1.2: https://zenodo.org/records/5766198
  PartialSpoof official v1.0 eval split fallback: https://zenodo.org/records/4817532
  PartialSpoof project route: https://github.com/nii-yamagishilab/PartialSpoof
  LlamaPartialSpoof: official repository/Zenodo source only, source TBD before trigger
AUTHORIZED_DOWNLOAD_PATHS = official Zenodo record-file/API routes only; official repository download route only after inspection
DOWNLOAD_RETRY_BUDGET =
  PartialEdit E1: 3 bounded infrastructure attempts
  PartialSpoof v1.2/fallback: 3 bounded attempts total across the authorized routes
  No unbounded retry, mirror, cloud copy, or random alternate URL

AUTHORIZED_BASELINES = CFPRF; PartialSpoof official MultiReso candidate; SAL/BAM provenance recovery only; TRACE stretch feasibility only
AUTHORIZED_CHECKPOINTS = existing CFPRF PS checkpoints; official PartialSpoof MultiReso checkpoint if source is verified; SAL/BAM only if official provenance/rights gates pass
AUTHORIZED_CHECKPOINT_SOURCES = official repository or repository-linked download only
AUTHORIZED_SMOKE_SCOPE = metadata/hash/load checks and at most 1-3 authorized samples; no performance metric
AUTHORIZED_FULL_REPRODUCTION_SCOPE = one canonical official baseline on one fully validated external dataset, only after dataset/checkpoint/adapter/environment gates pass; output label REPRODUCTION_ONLY
AUTHORIZED_OUTPUT_NAMESPACES = results/topconf/reproduction_recovery/<dataset>/<baseline>/<recovery_invocation_id>

GPU_POLICY = CPU permitted for metadata, hashing, tests, checkpoint inspection/load, and bounded smoke; no forced CPU full benchmark
GPU_EXECUTION_POLICY = record local/WSL/remote/cloud availability only if actually accessible with user authorization; do not purchase or create paid resources
RIGHTS_POLICY = do not download, redistribute, or use a checkpoint/data artifact when rights are unresolved; local-only use requires documented authorization
FAILURE_ACCOUNTING = every attempt records id, timestamp, URL, HTTP status, bytes, expected size, checksum, and failure category; no silent skip
RETRY_POLICY = bounded infrastructure retry only; no outcome/performance/seed/checkpoint shopping
CODE_FIX_POLICY = append-only defect report and new commit; reauthorize before any affected output
SUBSTITUTION_POLICY = availability/provenance/rights/hardware only; RESULT_BASED_SUBSTITUTIONS = 0
LlamAPARTIALSPOOF_TRIGGER = only after PartialSpoof official retry budget is exhausted and status is BLOCKED_EXTERNAL_SERVICE, before observing model results on the fallback

PROHIBITED_ACTIONS = Phase 4 freeze/execution; confirmatory cohort; RQ1/RQ2/RQ3; attack/defense; training/retraining; unofficial mirror; GT edits; result-based model/data selection; metric/pooling/threshold tuning; forced CPU full reproduction
REAUTHORIZATION_REQUIRED_FOR = new dataset, new checkpoint, new output contract, new adapter/evaluator commit, any full reproduction after a code change
HUMAN_REVIEW_REQUIRED_BEFORE_PHASE4 = YES
```

The authorization freezes availability and provenance rules, not scientific
outcomes. A recovery success is still development/reproduction evidence and
cannot change the original Phase 3 closure.
