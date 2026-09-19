# Localizer Paradigm Matrix v1

Status: `FROZEN FOR W6 / NO OUTCOME-BASED SELECTION`  
Definition: `DISTINCT_LOCALIZATION_PARADIGM_V1.md`  
Audit date: `2026-09-19` (long-run recovery overlay)

| model_id | paradigm_id | paradigm_definition | localization_output_type | official/reimplementation status | checkpoint provenance | adapter | evaluator compatibility | W7 eligibility | known limitation |
|---|---|---|---|---|---|---|---|---|---|
| B1b | `P1_SEQ_LOCAL_EMBEDDING` | sequence-local embedding deviation over fixed windows | window/frame anomaly score | internal historical implementation | project-local ECAPA artifact; no external checkpoint identity | no frozen arbitrary-dataset adapter | legacy pilot evaluator only | `PILOT_ONLY` | historical constructed pilot; not an external W7 localizer |
| CFPRF | `P2_FRAME_PLUS_PROPOSAL_REFINEMENT` | dense frame detector followed by proposal verification/regression | 20 ms frame scores, boundaries and proposal intervals | official repository; functional Phase3T reproduction | official FDN/PRN/XLSR hashes bound | `phase3t_adapter_v1`, PASS | PASS | `W7_LOCALIZER_ELIGIBLE` | Phase3T evidence is PartialEdit E1 only; 16 explicit failures |
| MultiResoModel-Simple | `P3_MULTI_RESOLUTION_FRAME` | multi-resolution segment/frame logits with a fixed utterance head | six native temporal scales plus utterance score | author-linked public reimplementation | archive/inner/SSL hashes bound; not original-paper exact checkpoint | six-scale canonical adapter, PASS | PASS | `W7_LOCALIZER_ELIGIBLE` | 33 explicit audio-load failures; reimplementation semantics |
| BAM | `P4_BOUNDARY_AWARE_FRAME` | boundary-aware frame localization | temporal authenticity logits plus boundary output at 160 ms | official source/checkpoint; Zenodo `12747417`, CC BY 4.0 | Drive checkpoint ZIP SHA256 `5C7379...2994D1`; strict load PASS | BAM temporal adapter PASS | PASS | `W7_LOCALIZER_ELIGIBLE` | source requires 8-frame pooling groups; no scientific inference run |
| SAL | `P5_SEGMENT_AWARE_SEQUENCE` | segment-aware sequence localization | position `(B,T,8)` and binary `(B,T,2)` logits at 160 ms | official source/checkpoint; HF revision `d9ab313d86a8b00a6345419721389d8b4eabe992` | WavLM checkpoint SHA256 `FDE760...14D2F`; strict load PASS | SAL temporal adapter PASS | PASS | `W7_LOCALIZER_ELIGIBLE` | W2V2 variant not needed; no scientific inference run |
| TRACE | `P6_TRAJECTORY_DERIVATIVE` | first-order frozen-foundation-model embedding trajectory dynamics | temporal anomaly/interval output contract not verified | paper-level candidate; official audio implementation not verified | no verified checkpoint | none | NO | `BLOCKED / REIMPLEMENTATION_REQUIRED` | no official code/checkpoint/output semantics bound |
| AASIST | `WHETHER_ONLY` | utterance-level anti-spoof classifier | two-class utterance score | official capability smoke | official checkpoint hash bound | not applicable as localizer | utterance detection only | `WHETHER_ONLY` | cannot count as a temporal localization paradigm |

## Matrix decision

```text
DISTINCT_LOCALIZATION_PARADIGMS_READY = 4
READY_PARADIGMS = P2_FRAME_PLUS_PROPOSAL_REFINEMENT, P3_MULTI_RESOLUTION_FRAME, P4_BOUNDARY_AWARE_FRAME, P5_SEGMENT_AWARE_SEQUENCE
REQUIRED_W6_MINIMUM = 4
SCALES_COUNTED_AS_SEPARATE_PARADIGMS = NO
HEADS_COUNTED_AS_SEPARATE_PARADIGMS = NO
W6_PARADIGM_GATE = PASS
```
