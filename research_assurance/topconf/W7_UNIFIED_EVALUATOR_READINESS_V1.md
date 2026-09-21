# W7 Unified Evaluator Readiness v1

Status: `PASS FOR PILOT PREPARATION / NO RUN AUTHORIZED BY THIS FILE`  
Audit date: `2026-09-15`

```text
W7_UNIFIED_EVALUATOR_READY = YES
DETECTION = AUROC, AUPRC, EER, fixed-FPR threshold metrics, decision retention
FRAME_LOCALIZATION = frame AUROC/AUPRC and thresholded precision/recall/F1
EVENT_PROPOSAL = IoU matching, AP@0.5/AP@0.75/AP@0.95, mAP, event F1
RANGEEER = present with finite support and positive/negative duration checks
TIME_ALIGNMENT = explicit monotonic in-duration supports; no silent clipping
FAILURE_ACCOUNTING = invalid and missing outputs are explicit fail-closed categories
METRIC_REDESIGN = NO
```

Evidence is the existing package under
`src/audiobookbench/topconf/evaluation/`, schemas and external parsers, plus
`python -m pytest tests/topconf -q` (`134 passed` in the reconciled scoped
baseline). Synthetic fixtures
and contract tests are preparation evidence only. No external W7 score vector
or gap result was generated.
