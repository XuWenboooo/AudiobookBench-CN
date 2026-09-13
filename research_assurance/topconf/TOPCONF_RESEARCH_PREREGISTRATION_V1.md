# TopConf Research Preregistration v1 (Draft Skeleton)

Status: **DRAFT / NOT LOCKED / NO EXPERIMENT AUTHORIZED**

This document defines the questions and governance that must be finalized before any confirmatory run. It does not authorize model training, inference, evaluation, bootstrap, or new data generation.

## 1. Scope and separation

- Historical Week1–5 work is archived pilot evidence only.
- Week4 scientific closure remains PASS; primary H4 remains NOT_REPORTABLE because the strict 12/12 winner requirement was not met.
- Week5 Exp6 is CANCELLED_UNEXECUTED and Exp7 is NOT_AUTHORIZED.
- No historical result may be relabeled as confirmatory evidence.

## 2. Research question

Primary question: `[TO BE SPECIFIED BEFORE LOCK]`.

Primary estimand, population, unit of analysis, and direction of benefit: `[TO BE SPECIFIED]`.

Secondary questions and exploratory analyses: `[TO BE SPECIFIED AND LABELED]`.

## 3. Design fields requiring lock

- Dataset and inclusion/exclusion rules: `[TBD]`
- Independent train/dev/test or held-out partitions: `[TBD]`
- Treatment/comparator definition: `[TBD]`
- Primary metric and aggregation: `[TBD]`
- Missingness and no-valid-parent policy: `[TBD]`
- Statistical model, uncertainty interval, multiplicity, and stopping rule: `[TBD]`
- Reproducibility seed/configuration policy: `[TBD]`

## 4. Freeze gate

Before execution, the team must approve a versioned protocol, threat model, baseline matrix, leakage policy, and open-science manifest. Any post-observation change requires a new version and is exploratory, not confirmatory.

## 5. Explicit prohibitions

Do not run F5, CosyVoice2, detector/localizer, evaluator, bootstrap, or model training as part of this preparation commit.
