# W6 Localizer Reproduction Inventory v1

Audit date: `2026-09-15`  
Status: `FROZEN INVENTORY / W6 BLOCKED / NO W7 INFERENCE`

The inventory distinguishes an executable localizer from an utterance-only
detector, a historical pilot diagnostic, and an unverified candidate. The
inventory does not select a model from scores.

| MODEL_ID | MODEL_ROLE | LOCALIZATION_CAPABLE | PARADIGM | OFFICIAL_SOURCE | SOURCE_COMMIT | CHECKPOINT | CHECKPOINT_SHA256 | LICENSE | RUNTIME | STRICT_LOAD | SMOKE_TEST | FULL_INFERENCE_VALIDATED | UNIFIED_ADAPTER | UNIFIED_EVALUATOR_COMPATIBILITY | OFFICIAL_REPRODUCTION_CLASS | W7_ELIGIBILITY | LIMITATIONS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1b | internal historical temporal anomaly baseline | YES, legacy fixed-window score | `P1_SEQ_LOCAL_EMBEDDING` | repository-local Week1–5 implementation | internal provenance; no TopConf checkpoint identity | SpeechBrain ECAPA local artifact | not bound as external checkpoint | project-local | historical CPU SpeechBrain pipeline | historical PASS | historical PASS | historical pilot only | NO | NO for arbitrary W7 external distributions | `HISTORICAL_INTERNAL_PILOT` | `PILOT_ONLY` | no frozen external-data adapter; prior numbers are pilot-only |
| B4 | boundary-transient diagnostic | NO for the unified localizer contract | none | repository-local Week1–5 implementation | internal | none | N/A | project-local | historical CPU feature pipeline | historical PASS | historical PASS | diagnostic only | NO | NO | `DIAGNOSTIC_ONLY` | `ENGINEERING_ONLY` | energy transient is not a validated temporal deepfake localizer |
| BAM | boundary-aware localizer candidate | YES in source paper/repository | `P4_BOUNDARY_AWARE_FRAME` | `https://github.com/media-sec-lab/BAM` | `55f3fb9e3b4dd6281597b86d7712fb23454179f6` | README-linked `checkpoint/model.ckpt`; not materialized | unavailable | repository license unresolved; rights fail-closed | source README; runtime not qualified | NOT_RUN | NOT_RUN | NO | NO | NO | `CANDIDATE_BLOCKED` | `BLOCKED` | rights and checkpoint identity are unresolved; no replacement training allowed |
| CFPRF | external frame detector + proposal localizer | YES | `P2_FRAME_PLUS_PROPOSAL_REFINEMENT` | `https://github.com/ItzJuny/CFPRF` | `358a901ead8a7d84dac979c3d626e34ef82c2854` | official FDN/PRN + XLSR | FDN `5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267`; PRN `88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36`; XLSR `B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9` | MIT | Python 3.10.11; torch 2.2.2+cu121; fairseq 1.0.0a0; RTX 4060 | PASS, strict zero missing/zero unexpected | PASS, bounded FDN/PRN smoke | PASS: 42,471 terminal; 42,455 valid; 16 model-inference failures; missing/orphan 0 | PASS, `phase3t_adapter_v1` | PASS for frame and proposal-compatible fields; failures remain explicit | `AUTHORIZED_LEVEL1_EXTERNAL_FUNCTIONAL_REPRODUCTION` | `W7_LOCALIZER_ELIGIBLE` | Phase3T was PartialEdit E1 only; no W7 result is inferred |
| MultiResoModel-Simple | external public reimplementation multi-resolution localizer | YES | `P3_MULTI_RESOLUTION_FRAME` | `https://github.com/hieuthi/MultiResoModel-Simple` | `0f69db3a2d654de47822d951fe6ad256bbaac9ba` | author-linked `baseline-ps-e55.tgz` | archive `0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32`; inner `5B753752F7C25370C6ABF973F69F58E100DAD4B5D3EA035872335358A876FDD1`; SSL `4E1B1AE691F26947FBF0B709FF1DD5F2F16CB586161CC3E9461E35BCD9CB5F75` | root MIT; submodule terms tracked | Python 3.10.11; torch 1.13.1+cu117; fairseq 0.12.2; RTX 4060 | PASS, strict zero missing/zero unexpected | PASS, exactly 3 deterministic E1 samples; finite six-scale output | PASS: 42,471 terminal; 42,438 valid; 33 audio-load failures; missing/orphan 0; all 6 scales retained | PASS, six-scale canonical adapter | PASS for frame output and explicit time supports; failures remain explicit | `FUNCTIONAL_PUBLIC_REIMPLEMENTATION_NOT_PAPER_EXACT_CHECKPOINT` | `W7_LOCALIZER_ELIGIBLE` | repository explicitly says it is not exact original MultiReso reproduction |
| SAL | segment-aware localizer candidate | YES in source design | `P5_SEGMENT_AWARE_SEQUENCE` | `https://github.com/SentryMao/SAL` | `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | documented `ckpt_path`; no local checkpoint | unavailable | MIT repository; dataset/checkpoint rights still separate | source requires Lightning/Hydra; runtime not qualified | NOT_RUN | NOT_RUN | NO | NO | NO | `CANDIDATE_BLOCKED` | `BLOCKED` | checkpoint unavailable; do not train a replacement |
| TRACE | training-free trajectory localizer candidate | CONCEPTUALLY YES, output contract unverified | `P6_TRAJECTORY_DERIVATIVE` | paper: `https://arxiv.org/abs/2604.01083`; matching official audio repository not verified | no verified commit | no verified checkpoint | unavailable | unresolved for a matching implementation | not qualified | NOT_RUN | NOT_RUN | NO | NO | NO | `REIMPLEMENTATION_REQUIRED` | `BLOCKED` | no verified official audio-localization code/checkpoint/output semantics |
| AASIST | independent utterance detector for Whether-B | NO | `WHETHER_ONLY` | `https://github.com/clovaai/aasist` | `a04c9863f63d44471dde8a6abcb3b082b07cd1d1` | `models/weights/AASIST.pth` | `51D2D9CF0738172F61E2A384EC50A54A55363240F67C971ED55A92435BC1A1C0` | MIT | frozen CPU runtime; strict load | PASS | PASS, synthetic two-class finite output | not a localization run | not applicable as localizer | utterance score only | `WHETHER_B_CAPABILITY_SMOKE` | `WHETHER_ONLY` | must not be counted toward distinct localization paradigms |

## Reused terminal evidence

CFPRF and MultiReso terminal counts are reused from the closed Phase3T raw
manifest and crash-recovery audit. No full reproduction was rerun in W6. The
MultiReso six native units are `0.02/0.04/0.08/0.16/0.32/0.64 s`; they remain
one paradigm under the definition above.

```text
CFPRF_PLANNED = 42471
CFPRF_TERMINAL = 42471
CFPRF_VALID = 42455
CFPRF_FAILED = 16
CFPRF_MISSING_OR_ORPHAN = 0/0
MULTIRESO_PLANNED = 42471
MULTIRESO_TERMINAL = 42471
MULTIRESO_VALID = 42438
MULTIRESO_FAILED = 33
MULTIRESO_SCALES = 6/6
RESULT_BASED_MODEL_SELECTIONS = 0
```
