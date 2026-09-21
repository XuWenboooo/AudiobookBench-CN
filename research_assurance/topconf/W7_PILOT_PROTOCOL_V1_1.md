# W7 formal pilot protocol v1.1

Status: `FROZEN PRE-EXECUTION CORRECTION`  
Correction reason: `SUPERSEDED_PRE_EXECUTION_DUE_TO_SPECIFICATION_OMISSION`  
Previous protocol: `W7_PILOT_PROTOCOL_V1.md`  
Previous SHA-256: `0d386e3461afeaa5a2dce361a8d7ebca58f5816f111827322576297774a51d3c`  
Execution status: `NOT EXECUTED`

This is a byte-distinct pre-execution correction of v1. The only scientific
text restored here is the exact Gate 1 criterion already present in the
outcome-blind W7 preparation draft, the preregistration, and the reconciliation
audit. Whether-A, Whether-B, Where, models, distributions, conditions,
metrics, aggregation, bootstrap philosophy, and failure rules are unchanged.

## Frozen inputs

- External distributions: `PartialEdit v1.1 E1` and official
  `LlamaPartialSpoof 1.0.b / R01TTS.0.b`.
- Localization paradigms: `CFPRF`, `MultiReso`, `SAL`, and `BAM`.
- Whether-A: duration-weighted mean of finite native higher-is-better spoof
  scores on native 20 ms support; frozen Level-1 target-FPR 0.05 empirical
  quantile and tie rule; invalid, empty, nonfinite, out-of-duration, or
  ambiguous output is fail-closed.
- Whether-B: official AASIST utterance detector, frozen repository commit and
  checkpoint from `W7_WHETHER_READINESS_V1.md`, with official class mapping.
- Evaluator: frozen detection, frame localization, event proposal, RangeEER,
  time-alignment, and explicit failure-accounting implementation described in
  `W7_UNIFIED_EVALUATOR_READINESS_V1.md`.
- Namespace and GT separation: `W7_EXECUTION_NAMESPACE_PLAN_V1.md` and
  `W7_GT_AND_IDENTITY_BINDING_V1.json`; model inference cannot read GT.

## Authorized pilot conditions

Only `clean`, `mechanism_shift`, `codec`, and `resampling` are permitted.
Each model × dataset × condition × owner invocation receives one unique
append-only namespace and one terminal state. Adaptive attack, query search,
result-guided retry, threshold changes, metric changes, and access to V3 or
confirmatory outcomes are prohibited.

## Gate 1

The pre-declared Gate 1 criterion is:

```text
GAP_OBSERVED_IN >= 3 DISTINCT localization paradigms
AND
GAP_OBSERVED_IN >= 2 external distributions
```

The criterion cannot be lowered or changed after observing W7 output. It is a
pre-execution eligibility criterion, not a result and not an authorization to
run W7.

## Stop and reporting rules

Raw outputs, attempts, failures, and canonical evaluator rows are retained in
the frozen W7 namespace. Invalid or failed rows are retained and handled only
by the frozen fail-closed policy. Any identity, GT separation, namespace, or
nonfinite-output violation stops the affected invocation and is recorded; it
does not trigger outcome-guided repair.

## Pre-freeze audit

`UNRESOLVED_PRE_FREEZE_ITEMS = NONE` for the W7 pilot definitions above.
The separate final confirmatory calibration/authorization remains a later
Gate-B decision and is not silently converted into a W7 result. No pilot run,
metric calculation, or detection–localization gap estimate was performed in
this correction.

```text
W7_PROTOCOL_FROZEN = YES
W7_SCIENTIFIC_INFERENCES_AT_REFREEZE = 0
LEVEL2_OUTCOMES_ACCESSED_AT_REFREEZE = NO
W7_EXECUTED = NO
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
```
