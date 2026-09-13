# TopConf Research Preregistration v1 (Protocol-Hardening Draft)

Status: **DRAFT / NOT LOCKED / NO EXPERIMENT AUTHORIZED**

This document defines the questions and governance that must be finalized before any confirmatory run. It does not authorize model training, inference, evaluation, bootstrap, or new data generation.

## 1. Scope and separation

- Historical Week1–5 work is archived pilot evidence only.
- Week4 scientific closure remains PASS; primary H4 remains NOT_REPORTABLE because the strict 12/12 winner requirement was not met.
- Week5 Exp6 is CANCELLED_UNEXECUTED and Exp7 is NOT_AUTHORIZED.
- No historical result may be relabeled as confirmatory evidence.

## 2. Research questions and claim boundary

RQ1 — Detection–Localization Robustness Gap: under manipulation-mechanism
shift and realistic media transformations, do utterance-level detection and
temporal localization degrade at different rates?

RQ2 — Selective Localization Suppression: can a bounded black-box adversary
preserve correct coarse detection while materially degrading localization,
subject to content, speaker, quality, alignment, query, and transformation
constraints?

RQ3 — Cause and Mitigation: which controlled interventions explain the gap,
and can unreliable localization be detected or mitigated?

Primary RQ1 estimand: localization degradation/retention measured at a
predeclared detection-retention constraint relative to the same-system clean
condition, paired within evaluation unit and aggregated over the frozen
population. The recommended primary gap is `LD@DR95`: the change in the
predeclared primary localization score among conditions whose detection
retention remains at least 95% of clean, or the authorized alternative
constraint recorded before execution. It is not a subtraction of AUROC and
mAP. Exact score, retention definition, population, and 95% operationalization
remain `TBD_BEFORE_AUTHORIZATION`.

RQ1 primary direction: larger localization degradation at retained detection
is stronger evidence of a gap. Paired detection-retention versus localization-
retention curves are a prespecified sensitivity/display analysis.

RQ2 primary estimand and success conjunction are `TBD_BEFORE_AUTHORIZATION`;
success requires detection preserved, localization materially degraded,
content and speaker preserved, quality and alignment passed, and query and
transformation budgets passed. RQ3 is controlled-intervention and mitigation
analysis, not a license for post-hoc cue mining.

Secondary questions and exploratory analyses: `[TO BE SPECIFIED AND LABELED]`.

## 3. Definitions and outcome hierarchy

Whether-A is detection derived from the localization system by a fixed,
predeclared pooling rule. Whether-B is an independently trained/frozen
utterance-level detector whose score is not computed from the localization
map. The confirmatory gap must report both where available; a missing
Whether-B comparison is a limitation, not evidence of causal decoupling.

Where is reported at four levels: frame score, event intervals, proposal
intervals, and boundary accuracy. The primary localization level and mapping
from frames to events/proposals are `TBD_BEFORE_AUTHORIZATION`.

Primary/secondary/diagnostic metric assignments, thresholds, and aggregation
are `TBD_BEFORE_AUTHORIZATION`; candidate metrics are listed in the protocol
skeleton and may not be promoted after outcome inspection.

Whether-A primary pooling is **NOT FROZEN**. Before Phase 3 authorization, the
team must choose exactly one of `mean_pool`, `max_pool`, or `top_k_mean` using
only task semantics, prevalence sensitivity, temporal-resolution dependence,
calibration stability, and cross-model comparability. No confirmatory score
comparison may inform this choice. If evidence remains insufficient, the
authorization record must explicitly defer the choice and designate the
procedure as non-primary.

Threshold policy: detection, frame-localization, and event/proposal thresholds
must come from an official fixed threshold, Level 1 calibration, or frozen
target-FPR/EER rule, each named in the authorization record. Level 2 test-set
threshold optimization is prohibited.

## 4. Design fields requiring lock

- Dataset and inclusion/exclusion rules: `[TBD]`
- Independent train/dev/test or held-out partitions: `[TBD]`
- Treatment/comparator definition: `[TBD]`
- Primary metric and aggregation: `TBD_BEFORE_AUTHORIZATION`
- Missingness, invalid case, and no-valid-parent policy: fail closed; exact
  adjudication is `TBD_BEFORE_AUTHORIZATION` and no case may be silently
  dropped or replaced.
- Statistical model, uncertainty interval, multiplicity, and stopping rule:
  `TBD_BEFORE_AUTHORIZATION`
- Reproducibility seed/configuration policy: `TBD_BEFORE_AUTHORIZATION`
- Statistical unit is source/case; paired comparisons use paired source-level
  bootstrap with 95% CIs, bootstrap N `TBD_BEFORE_AUTHORIZATION`, predefined
  primary hierarchy, and Holm adjustment only where required by the locked
  family. Missing/invalid cases are explicit fail-closed categories.

## 5. Mandatory stop gates

- GAP GATE: primary RQ1 is `WEAK`/`NO_GO` if the gap is not stable across at
  least 3 distinct localization paradigms and 2 independent distributions.
  Adding models, selective data, or metrics after inspection cannot rescue it.
- ATTACK GATE: RQ2 is not a primary contribution unless all preservation,
  material-degradation, baseline, and budget conditions pass.
- TOPCONF GATE: `SECURITY_TOPCONF_READINESS = NO` if evidence consists only
  of our dataset, our model, and our attack.

## 6. Freeze gate

Before execution, the team must approve a versioned protocol, threat model, baseline matrix, leakage policy, and open-science manifest. Any post-observation change requires a new version and is exploratory, not confirmatory.

## 7. Explicit prohibitions

Do not run F5, CosyVoice2, detector/localizer, evaluator, bootstrap, or model training as part of this preparation commit.
