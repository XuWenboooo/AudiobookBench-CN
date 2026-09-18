# W6 Recovery Localizer / Paradigm Matrix v2

Audit date: `2026-09-18`  
Status: `ALL-REGISTERED-CANDIDATES-ATTEMPTED / NO W7 SCIENTIFIC INFERENCE`

This matrix records every localization candidate registered in the W6 plan,
the prior inventory, or the official-source audit. Existing bounded evidence is
reused where it is complete. No scientific population, AUROC/AUPRC/EER,
RangeEER, event F1, mAP, boundary error, or Detection–Localization Gap was
read or computed in this recovery.

## Candidate records

| MODEL | SOURCE | COMMIT | LICENSE | CHECKPOINT | CHECKPOINT_HASH | STRICT_LOAD | RUNTIME | TEMPORAL_OUTPUT | ADAPTER | FORMULATION | PARADIGM | DISTINCTNESS_JUSTIFICATION | W7_ELIGIBLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CFPRF | `ItzJuny/CFPRF` | `358a901ead8a7d84dac979c3d626e34ef82c2854` | MIT | official FDN/PRN/XLSR | FDN `5FCBBC...6267`; PRN `88B605...AC36`; XLSR `B08927...0ED9` | PASS | frozen Python 3.10 / Torch 2.2.2+cu121 path | 20 ms frame scores, proposals, boundaries | `phase3t_adapter_v1` PASS | dense frame detector plus learned proposal refinement | `P2_FRAME_PLUS_PROPOSAL_REFINEMENT` | proposal refinement is a distinct temporal formulation | YES |
| MultiResoModel-Simple | `hieuthi/MultiResoModel-Simple` | `0f69db3a2d654de47822d951fe6ad256bbaac9ba` | root MIT; submodule terms tracked | `baseline-ps-e55.tgz` | archive `0C394F...0E32`; inner `5B7537...FDD1`; SSL `4E1B...5F75` | PASS | frozen Python 3.10 / Torch 1.13.1+cu117 path | six native temporal scales plus utterance head | six-scale canonical adapter PASS | shared multi-resolution temporal inference | `P3_MULTI_RESOLUTION_FRAME` | native multi-resolution inference is distinct from proposal refinement | YES |
| B1b | repository-local historical implementation | internal provenance; no current external commit | project-local | historical ECAPA local artifact | not externally bound | historical PASS | historical CPU SpeechBrain path | fixed-window/window-frame anomaly score | no frozen arbitrary-dataset adapter | sequence-local embedding deviation | `P1_SEQ_LOCAL_EMBEDDING` | distinct formulation, but historical-only and not externally reproducible here | PILOT_ONLY |
| B4 | repository-local historical implementation | internal | project-local | none | N/A | historical PASS | historical CPU feature path | energy-transition diagnostic, not a validated localizer contract | none | engineering diagnostic | `NOT_A_LOCALIZER` | diagnostic output is not a temporal deepfake localizer | NO |
| BAM | `media-sec-lab/BAM` | `55f3fb9e3b4dd6281597b86d7712fb23454179f6` | repository license unresolved; fail-closed | README-linked `checkpoint/model.ckpt` | unavailable; checkpoint not materialized | NOT_RUN | not qualified | boundary-aware frame output described by source | none | boundary-aware temporal representation | `P4_BOUNDARY_AWARE_FRAME` | boundary-aware structure would be distinct, but rights/checkpoint gates failed | NO |
| SAL | `SentryMao/SAL` | `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | MIT repository; checkpoint/data rights separate | README `ckpt_path`; no local checkpoint | unavailable | NOT_RUN | not qualified | fixed-resolution frame/segment output | none | segment-aware sequence modeling | `P5_SEGMENT_AWARE_SEQUENCE` | segment-aware sequence formulation would be distinct, but checkpoint unavailable | NO |
| TRACE | official paper `arXiv:2604.01083` | no verified official audio-localization repository commit | unresolved for matching implementation | no verified checkpoint | unavailable | NOT_RUN | not qualified | trajectory-derived temporal anomaly/interval output not contract-bound | none | first-order frozen embedding trajectory dynamics | `P6_TRAJECTORY_DERIVATIVE` | training-free trajectory dynamics would be distinct, but official implementation/output provenance is absent | NO |

AASIST remains recorded in the W7 Whether-B capability smoke but is not a
localization candidate: it has utterance-level output only and therefore cannot
increase the paradigm count.

## Recovery execution and blockers

| CANDIDATE | RECOVERY ACTION | RESULT | EXACT BLOCKER |
|---|---|---|---|
| BAM | official repository discovery and clone attempt on 2026-09-18 | NOT_RECOVERED | GitHub clone failed with `HTTP/2 framing layer`; checkpoint rights/hash remain unresolved |
| SAL | official repository discovery and clone attempt on 2026-09-18 | NOT_RECOVERED | GitHub clone failed with connection reset; no checkpoint is locally available |
| LlamaPartialSpoof-related source | official repository clone attempt on 2026-09-18 | NOT_RECOVERED; not a verified localizer checkpoint in current inventory | GitHub clone failed to connect to port 443; source metadata alone does not provide a ready localizer |
| TRACE | official paper/source discovery | NOT_RECOVERED | no verified official audio-localization implementation, checkpoint, or output contract |
| CFPRF | reuse closed bounded reproduction and preflight | SUCCESSFULLY_REPRODUCED / READY | 16 explicit model-inference failures in prior terminal ledger; no missing/orphan records |
| MultiResoModel-Simple | reuse closed bounded reproduction and preflight | SUCCESSFULLY_REPRODUCED / READY | public reimplementation rather than paper-exact checkpoint; 33 explicit audio-load failures |
| B1b/B4 | historical evidence review only | NOT_W7_READY | no frozen external adapter/checkpoint; B4 is diagnostic-only |

## Counts and classification

```text
TOTAL_LOCALIZER_CANDIDATES = 7
SUCCESSFULLY_REPRODUCED = 2 current external localizers (CFPRF, MultiResoModel-Simple)
READY_LOCALIZERS = 2
DISTINCT_LOCALIZATION_PARADIGMS = 2
READY_PARADIGMS = P2_FRAME_PLUS_PROPOSAL_REFINEMENT, P3_MULTI_RESOLUTION_FRAME
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
RESULT_BASED_MODEL_SELECTIONS = 0
```

The count is formulation-based: checkpoints, heads, scales, and architecture
variants are not separate paradigms. `DISTINCT_LOCALIZATION_PARADIGMS < 4`,
so the W6 gate remains blocked.
