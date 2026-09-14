# Phase 4 Outcome Firewall v1

Status: **PASS — DESIGN FIREWALL ACTIVE / NON-AUTHORIZING**
Audit date: **2026-09-14**

## Authority and scope

The authoritative Phase3T closure is
`research_assurance/topconf/PHASE3T_CONTROLLED_REPRODUCTION_CLOSURE.md` at
mainline commit `17b6419e4ee185a7029034776034235bcf17eac7`. Its scope is
Level-1 external functional reproduction and compatibility. The recorded
CFPRF and MultiReso native outputs, terminal ledgers, hashes, and adapter
checks are capability evidence; they are not RQ1 confirmatory outcomes.

The Phase3T raw output manifest records two completed, accounted runs on
PartialEdit v1.1 E1: CFPRF (`42471` planned/terminal, `42455` valid, `16`
model-inference failures) and MultiReso worker-r2 (`42471` planned/terminal,
`42438` valid, `33` audio-load failures, all six native scales retained).
These counts are reproduced here only to establish the capability boundary;
no Level-2 score, metric, or ranking is selected from them.

## Firewall decisions

```text
PHASE3T_OUTCOMES_AVAILABLE = YES
PHASE3T_OUTCOMES_ALLOWED_FOR_CAPABILITY_CHECK = YES
PHASE3T_OUTCOMES_ALLOWED_FOR_FAILURE_DIAGNOSIS = YES
PHASE3T_OUTCOMES_ALLOWED_FOR_DESIGN_SELECTION = NO
PHASE3T_OUTCOMES_ALLOWED_FOR_THRESHOLD_SELECTION = NO
PHASE3T_OUTCOMES_ALLOWED_FOR_SAMPLE_SIZE_ADJUSTMENT = NO
PHASE3T_OUTCOMES_ALLOWED_FOR_BASELINE_SELECTION = NO
PHASE3T_OUTCOMES_ALLOWED_FOR_METRIC_SELECTION = NO
PHASE3T_OUTCOMES_ALLOWED_FOR_SCALE_OR_HEAD_SELECTION = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RQ2_ATTACK_INVOKED = NO
RQ3_MITIGATION_INVOKED = NO
RESULT_BASED_DESIGN_CHANGES = 0
```

The predeclared capability facts used in reconciliation are: CFPRF exposes a
finite native 20 ms FDN temporal output and native boundary/proposal outputs;
MultiReso exposes finite native temporal outputs at `0.02/0.04/0.08/0.16/0.32/
0.64` seconds; both adapters preserve provenance and reject semantic repair;
and both runs have complete terminal accounting. The diagnostic AUROC/AUPRC
values are intentionally not copied into any Phase4 decision table.

## Prohibited paths

No Phase4 decision may be justified by a Phase3T performance ordering, a
numeric metric, a winner, a failed-case pattern, or an observed scale/head
ordering. This includes choosing a baseline, Where level, Whether-A pooling,
threshold, mechanism, transformation strength, sample size, bootstrap, or
gap threshold. If a future choice changes after any outcome is revealed, it
must receive a new version and be labelled exploratory.

The Week1–5 archive remains behind the separate historical firewall:
`WEEK1_5_DATA_ROLE = PILOT_ONLY` and
`WEEK1_5_CONFIRMATORY_USE = PROHIBITED`.

## Audit conclusion

The firewall is PASS because the Phase3T artifacts are available for checking
native contracts and failure accounting while all outcome-driven selection
uses are explicitly prohibited. This document does not authorize Phase4 data
materialization, model inference, evaluation, bootstrap, RQ2, or RQ3.
