# Phase 3 External Reproduction Authorization v1

Status: **AUTHORIZED FOR BOUNDED REPRODUCTION ONLY / NOT CONFIRMATORY**

Authorization is frozen before any external model output is observed. The
scope is official-code/checkpoint materialization, parser validation, smoke
tests, and bounded reproduction on the named public development/evaluation
artifacts. It cannot authorize RQ1/RQ2/RQ3, model ranking, pooling selection,
threshold tuning, attack/defense, or Level 2 confirmatory analysis.

```text
AUTHORIZATION_ID = P3-ER-2026-09-13-01
AUTHORIZED_COMMIT = bf66933347889b7f0acaa12ba2681470151b9d59
AUTHORIZED_DATASETS = PartialSpoof, PartialEdit
AUTHORIZED_DATASET_VERSIONS = PartialSpoof v1.2; PartialEdit v1.1
AUTHORIZED_BASELINES = internal B1b/B4, CFPRF, SAL, BAM conditional
AUTHORIZED_REPOSITORIES =
  PartialSpoof https://github.com/nii-yamagishilab/PartialSpoof
  CFPRF https://github.com/ItzJuny/CFPRF
  SAL https://github.com/SentryMao/SAL
  BAM https://github.com/media-sec-lab/BAM
AUTHORIZED_REPO_COMMITS =
  PartialSpoof 847347aaec6f65c3c6d2f17c63515b826b94feb3
  CFPRF 358a901ead8a7d84dac979c3d626e34ef82c2854
  SAL b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485
  BAM 55f3fb9e3b4dd6281597b86d7712fb23454179f6
AUTHORIZED_CHECKPOINTS = CFPRF official linked checkpoints; SAL official checkpoint if present; BAM only after rights clearance; no TRACE
AUTHORIZED_CHECKPOINT_SOURCES = official repositories and repository-linked download only
AUTHORIZED_ADAPTER_COMMIT = bf66933347889b7f0acaa12ba2681470151b9d59
AUTHORIZED_EVALUATOR_COMMIT = bf66933347889b7f0acaa12ba2681470151b9d59
AUTHORIZED_METRICS = native official metrics first; unified AUROC/AUPRC/EER/frame/event/proposal/boundary where compatible; RangeEER reference formula
AUTHORIZED_SMOKE_TEST_SCOPE = 1-3 synthetic or authorized Level-1 samples per model; no performance reporting
AUTHORIZED_REPRODUCTION_SPLITS = official dev/eval splits only; PartialEdit E1/E2 and E1-Codec/E2-Codec only
AUTHORIZED_OUTPUT_NAMESPACES = results/topconf/reproduction/<dataset>/<baseline>/<invocation_id>
AUTHORIZED_SEEDS = official default seed when documented; otherwise no new seed for reproduction
AUTHORIZED_COMMAND_CLASSES = metadata inspection, checksum verification, parser validation, checkpoint load, smoke test, official reproduction command
FAILURE_ACCOUNTING = every case/run classified; no silent skip
RETRY_POLICY = infrastructure-only retry; never performance-based retry
CODE_FIX_POLICY = stop, defect report, new commit/hash, reauthorization if outputs affected
REPRODUCTION_SUCCESS_CLASSES = EXACT, CLOSE, FUNCTIONAL, FAILED
STRICT_TOLERANCE = same official protocol/output and absolute published scalar difference <= 0.10 percentage points when comparison is defined
CLOSE_TOLERANCE = same official protocol/output and absolute published scalar difference <= 2.00 percentage points
FUNCTIONAL_REPRODUCTION_CRITERIA = model loads, authorized input runs, finite output matches documented granularity, official metric computable; no claim about numerical agreement
PROHIBITED_ACTIONS = confirmatory tuning, threshold/pooling selection by outcome, attack, defense, new generation, fresh cohort, result-based exclusion, RQ1/RQ2/RQ3 analysis
APPROVERS = Codex execution record; human review required before Phase 4
GT_VISIBILITY_POINT = permitted for reproduction only after parser validation; never Level-2 confirmatory
```

## Gate interpretation

This authorization permits external reproduction artifacts to be recorded as
`REPRODUCTION_ONLY` or `INFRASTRUCTURE_VALIDATION_ONLY`. It does not freeze
the Phase 4 confirmatory design and does not convert either external dataset
to Level 2.
