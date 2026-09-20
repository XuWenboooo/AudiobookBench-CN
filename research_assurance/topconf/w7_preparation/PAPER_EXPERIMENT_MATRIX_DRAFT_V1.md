# Paper Experiment Matrix Draft v1

Status: `STRUCTURAL SCAFFOLD / NO OUTCOME`

The intended W7 report has four localization paradigms crossed with each
accepted external distribution and the four predeclared conditions. The
matrix is deliberately complete before outcomes and no row or column may be
removed after observing a metric.

## Localization paradigms

| Paradigm | Localizer | Native output | Adapter/provenance |
|---|---|---|---|
| P2_FRAME_PLUS_PROPOSAL_REFINEMENT | CFPRF | 20 ms frames, boundaries, proposals | `phase3t_adapter_v1`; official commit recorded in W7 preflight |
| P3_MULTI_RESOLUTION_FRAME | MultiResoModel-Simple | six native temporal scales plus utterance score | six-scale canonical adapter; author-linked reimplementation explicitly labeled |
| P4_BOUNDARY_AWARE_FRAME | BAM | 160 ms authenticity and boundary outputs | official source/checkpoint and BAM adapter evidence |
| P5_SEGMENT_AWARE_SEQUENCE | SAL | 160 ms position/binary sequence outputs | official source/checkpoint and SAL adapter evidence |

## Distribution × condition grid

| Distribution | clean | mechanism_shift | codec | resampling | readiness |
|---|---|---|---|---|---|
| PartialEdit_v1.1_E1 | reserved | reserved | reserved | reserved | ACCEPTED_AS_POTENTIAL_INPUT_ONLY |
| PartialSpoof_v1.2_eval | reserved | reserved | reserved | reserved | NO; unresolved two-ID identity mismatch |
| second external distribution | reserved | reserved | reserved | reserved | UNRESOLVED_PRE_FREEZE_ITEM |

Every cell must trace to `distribution_id`, `adapter_version`, case-set hash,
condition transform identity, model/localizer provenance, whether definition,
raw prediction namespace, evaluator version and bootstrap identity. All current
cell values are `NOT_MEASURED`.
