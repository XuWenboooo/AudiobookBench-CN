# Threat Model v1

Status: **DRAFT / REVIEW REQUIRED**

## Assets to protect

- Held-out labels and evaluation inputs.
- Frozen protocol, scoring code, and analysis plan.
- Separation between pilot evidence and confirmatory evidence.
- Reproducible provenance for data, models, prompts, and outputs.

## Threats

| ID | Threat | Failure mode | Control | Verification |
|---|---|---|---|---|
| T-01 | Leakage | held-out content influences tuning | access controls and provenance log | pre-run audit |
| T-02 | Metric drift | metric changes after outcomes | preregistered metric lock | protocol diff |
| T-03 | Search drift | adaptive search expands after seeing results | fixed budget and stopping rule | run ledger |
| T-04 | Population drift | exclusions remove difficult cases | frozen inclusion/exclusion rules | dataset manifest |
| T-05 | Selective reporting | failed or no-parent cases omitted | terminal-case accounting | completeness check |
| T-06 | Implementation drift | code/config changes during run | immutable release identifier | hash review |

## Residual risks

`[To be reviewed and accepted before preregistration lock.]`
