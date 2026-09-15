# Distinct Localization Paradigm Definition v1

Status: `FROZEN FOR W6 AUDIT / NO SCIENTIFIC RUN AUTHORIZED`  
Audit date: `2026-09-15`

## Operational definition

A localization paradigm is a distinct temporal inference mechanism whose
combination of (1) temporal representation, (2) prediction representation,
(3) localization formulation, and (4) proposal/frame/range structure changes
the way a model converts audio into a temporal localization claim.

Two systems are the same paradigm when they only differ by checkpoint, random
seed, backbone, hidden width, loss weight, temporal scale, or a deterministic
adapter. Multiple native scales of one architecture count once. Multiple
heads of one architecture count once unless the head changes the temporal
inference formulation itself. A detector with only an utterance score is not a
localization paradigm.

## Required evidence for a ready paradigm

Each counted paradigm must have:

1. a source or repository identity and checkpoint provenance;
2. a legal-use decision;
3. strict load and bounded smoke evidence;
4. an explicit temporal output schema and timestamp semantics;
5. a unified adapter and evaluator-compatible output;
6. failure propagation and no silent case deletion;
7. an eligibility decision made without inspecting W7 or confirmatory results.

## Frozen paradigm IDs

| ID | Mechanism | Representation / formulation | Count rule |
|---|---|---|---|
| `P1_SEQ_LOCAL_EMBEDDING` | Sequence-local embedding inconsistency over fixed windows | Window/frame scores derived from local representation deviation | B1b only; historical pilot unless an external-data adapter is independently frozen |
| `P2_FRAME_PLUS_PROPOSAL_REFINEMENT` | Frame detector followed by learned proposal refinement | Dense frame scores plus proposal/event intervals and boundary regression | CFPRF FDN+PRN is one paradigm; FDN and PRN are not counted separately |
| `P3_MULTI_RESOLUTION_FRAME` | Shared multi-resolution temporal inference | Frame/segment logits at six native resolutions plus utterance head | MultiResoModel-Simple is one paradigm; six scales are not six paradigms |
| `P4_BOUNDARY_AWARE_FRAME` | Boundary-aware temporal representation | Frame localization with explicit boundary-sensitive structure | BAM candidate; not ready while rights/checkpoint gates are unresolved |
| `P5_SEGMENT_AWARE_SEQUENCE` | Segment-aware sequence modeling | Fixed-resolution frame/segment output from SAL | SAL candidate; not ready without a verified checkpoint and smoke |
| `P6_TRAJECTORY_DERIVATIVE` | Training-free embedding-trajectory dynamics | First-order temporal embedding transitions and derived local anomaly/interval output | TRACE candidate; not ready without official implementation/output provenance |

## Exclusions

- AASIST is `WHETHER_ONLY`: it emits an utterance-level score and is not a
  temporal localization paradigm.
- B4 is an energy-transition diagnostic and does not satisfy the localizer
  output contract.
- Changing CFPRF checkpoints, MultiReso scales, or score adapters does not add
  paradigms.
- Phase3T and historical Week1–5 scores are not W7 outcomes.

## W6 count

```text
DISTINCT_LOCALIZATION_PARADIGMS_READY = 2
READY_IDS = P2_FRAME_PLUS_PROPOSAL_REFINEMENT, P3_MULTI_RESOLUTION_FRAME
REQUIRED_MINIMUM = 4
W6_PARADIGM_TARGET = NOT_MET
```
