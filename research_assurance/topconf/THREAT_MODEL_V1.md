# Threat Model v1 (Protocol-Hardening Draft)

Status: **DRAFT / REVIEW REQUIRED**

## Assets to protect

- Held-out labels and evaluation inputs.
- Frozen protocol, scoring code, and analysis plan.
- Separation between pilot evidence and confirmatory evidence.
- Reproducible provenance for data, models, prompts, and outputs.

## Adversary, goal, knowledge, and access

The attacker is a creator or distributor of a partially manipulated recording.
The goal is selective forensic degradation: preserve coarse Whether detection
while obscuring the manipulated temporal region (Where), reducing the value
for fact-checking, investigation, evidence attribution, and content recovery.

The main threat model is black-box query access. Knowledge assumptions for
each track must separately record architecture, training data, parameters, and
decision thresholds: all are `TBD_BEFORE_AUTHORIZATION` (default assumption is
unknown). A query response must be fixed before execution as one of
`utterance score`, `localization map`, `interval/proposal predictions`, or an
explicitly documented tuple; access to hidden labels or gradients is forbidden.

Query budget and transformation budget are independent and both are
`TBD_BEFORE_AUTHORIZATION`. Every attempted query and transformation is
ledgered, including failures and terminal no-parent cases.

## Preservation constraints

An accepted attack must preserve semantic/content identity, speaker identity,
intelligibility, audio quality, duration and time alignment within
predeclared tolerances (`TBD_BEFORE_AUTHORIZATION`). These constraints are
measured independently of the target localizer. Out of scope: white-box
gradient attacks, generator retraining, text substitution, speaker
replacement, arbitrary destructive noise, and unbounded perceptual
degradation.

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

Distribution shift, imperfect independent Whether-B detectors, and metric
dependence remain residual risks. They must be acknowledged and accepted
before preregistration lock; unresolved risks block authorization.
