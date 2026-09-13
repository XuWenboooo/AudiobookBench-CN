# Confirmatory Protocol Skeleton v1 (Hardening Draft)

Status: **DRAFT / NOT EXECUTABLE**

## Required locked sections

1. Hypothesis and estimand: RQ1 `LD@DR95` as defined in preregistration;
   RQ2 conjunction and RQ3 intervention estimands: `TBD_BEFORE_AUTHORIZATION`
2. Population, speaker/source/mechanism policy, prevalence, and sampling frame: `TBD_BEFORE_AUTHORIZATION`
3. Dataset versions, independent train/dev/calibration/test split manifest, and external datasets: `TBD_BEFORE_AUTHORIZATION`
4. Model versions, checkpoint hashes, intervention/system, and comparator: `TBD_BEFORE_AUTHORIZATION`
5. Outcomes: primary `LD@DR95`; secondary detection AUROC/AUPRC/EER/TPR@fixed-FPR/decision retention and localization event F1/AP@0.5/AP@0.75/AP@0.95/mAP/onset/offset error; diagnostic frame AUROC/AUPRC/RangeEER/false-positive duration per hour. Exact assignment is locked before authorization.
6. Validity, failure accounting, invalid case, and no-valid-parent handling: fail closed; no silent exclusion, replacement, fallback, or query transfer; detailed adjudication `TBD_BEFORE_AUTHORIZATION`
7. Passive transformations, attack/transformation/query budget, quality constraints, and stopping rules: `TBD_BEFORE_AUTHORIZATION`
8. Statistical unit, paired aggregation, bootstrap plan, uncertainty, multiplicity, and seed policy: `TBD_BEFORE_AUTHORIZATION`
9. Exclusions, missingness, retries, deviations, and invalidation rules: `TBD_BEFORE_AUTHORIZATION`
10. Reproducibility, hashes, commands, stdout/stderr, raw predictions, ledger, report, and release procedure: `TBD_BEFORE_AUTHORIZATION`

## Execution gate

No confirmatory experiment starts until this skeleton is converted into a reviewed, versioned protocol and the data classification, threat model, baseline matrix, and open-science manifest are approved together.

The skeleton remains non-executable until an explicit authorization record
names the frozen commit, population, thresholds, budgets, and custodians.

## Historical boundary

The archived Week1–5 pilot can inform design rationale. It cannot be used to change the confirmatory population, endpoint, or analysis after the protocol is locked.
