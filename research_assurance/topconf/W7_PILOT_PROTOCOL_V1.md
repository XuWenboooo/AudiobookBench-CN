# W7 formal pilot protocol v1

Status: `FROZEN FOR HUMAN REVIEW ONLY`  
Audit date: `2026-09-21`  
Execution status: `NOT EXECUTED`

This document freezes the already reviewed W7 pilot definitions after W6
distribution closure. It authorizes no run by itself and does not contain
scientific outcomes.

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
freezing this document.

```text
W7_PROTOCOL_FROZEN = YES
W7_FORMAL_PILOT_READY_FOR_HUMAN_REVIEW = YES
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
```
