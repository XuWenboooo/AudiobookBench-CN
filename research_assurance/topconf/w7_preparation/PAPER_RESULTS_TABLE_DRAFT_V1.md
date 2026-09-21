# Paper Results Table Draft v1

Status: `EMPTY OUTCOME SCAFFOLD / PRE-W7`

All performance cells intentionally contain `NOT_MEASURED`. This table
defines reporting structure only; it does not predict direction, expected
degradation or a future gap.

| Distribution | Condition | Localizer | Paradigm | Whether-A | Whether-B | Where | Detection AUROC | Detection AUPRC | Detection EER | TPR@fixed-FPR | Localization AUROC | Localization AUPRC | RangeEER | Event F1 | mAP | Boundary Error | Gap indicator | Bootstrap CI | Gate contribution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PartialEdit_v1.1_E1 | clean | CFPRF | P2_FRAME_PLUS_PROPOSAL_REFINEMENT | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |
| PartialEdit_v1.1_E1 | mechanism_shift | MultiResoModel-Simple | P3_MULTI_RESOLUTION_FRAME | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |
| PartialEdit_v1.1_E1 | codec | BAM | P4_BOUNDARY_AWARE_FRAME | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |
| PartialEdit_v1.1_E1 | resampling | SAL | P5_SEGMENT_AWARE_SEQUENCE | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |
| PartialSpoof_v1.2_eval | all declared conditions | CFPRF / MultiReso / BAM / SAL | four ready paradigms | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |
| SECOND_EXTERNAL_DISTRIBUTION | all declared conditions | all four ready paradigms | four ready paradigms | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED | NOT_MEASURED |

The future matrix expands every distribution × condition × localizer cell
without deleting rows after results. A row is reportable only after the
acceptance harness, case identity, adapter, terminal ledger and human
authorization gates all pass.
