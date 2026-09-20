# Paper Provenance Appendix Draft v1

Status: `NON-OUTCOME PROVENANCE SCAFFOLD`; all W7 outcomes `NOT_MEASURED`

Missing facts are recorded as `UNKNOWN_FROM_CURRENT_EVIDENCE`; no checkpoint,
license, adapter or archive fact is guessed.

## Localization models

| Model | Identity/source | Checkpoint/runtime | License | Adapter/output semantics | Readiness evidence |
|---|---|---|---|---|---|
| CFPRF | `ItzJuny/CFPRF`, official commit `358a901ead8a7d84dac979c3d626e34ef82c2854` | official FDN/PRN/XLSR hashes bound; frozen runtime in W7 preflight | MIT | `phase3t_adapter_v1`; 20 ms frame, boundary and proposal outputs | strict load/smoke PASS; preparation-eligible only |
| MultiResoModel-Simple | `hieuthi/MultiResoModel-Simple`, commit `0f69db3a2d654de47822d951fe6ad256bbaac9ba` | `baseline-ps-e55.tgz` and inner/SSL hashes recorded; public reimplementation, not paper-exact | root MIT; submodule terms tracked | six-scale canonical adapter; native 20/40/80/160/320/640 ms outputs | strict load/smoke PASS; preparation-eligible only |
| BAM | `media-sec-lab/BAM`, commit `55f3fb9e3b4dd6281597b86d7712fb23454179f6`; Zenodo `12747417` | official Drive checkpoint ZIP hash recorded; embedded WavLM strict match | CC BY 4.0 | BAM temporal adapter; 160 ms authenticity and boundary outputs | strict load/smoke/adapter PASS; preparation-eligible only |
| SAL | `SentryMao/SAL`, commit `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485`; HF revision `d9ab313d86a8b00a6345419721389d8b4eabe992` | official WavLM checkpoint hash recorded | MIT repository; checkpoint/data rights separate | SAL adapter; 160 ms position/binary outputs | strict load/smoke/adapter PASS; preparation-eligible only |

`TRACE` remains unverified and is not included in the four-ready matrix.

## External distributions

| Distribution | Official source | License/provenance | GT | Adapter | Identity/readiness |
|---|---|---|---|---|---|
| PartialEdit_v1.1_E1 | Zenodo `18829689`; project page recorded in W7 matrix | CC BY 4.0; local-use and redistribution decisions recorded | official edited-region seconds and duration | official CSV parser/evaluator compatible | potential input only; no authorization |
| PartialSpoof_v1.2_eval | Zenodo `5766198`; official repository recorded in W7 matrix | CC BY 4.0 / ODC-By acknowledgement chain | official v1.2 temporal/segment labels | NOT_READY until two IDs are reconciled | `READY = NO`; unresolved official mismatch |
| HAD | Zenodo `10377492`; Interspeech source | `UNKNOWN_FROM_CURRENT_EVIDENCE` for completed local rights decision | exact local GT binding unresolved | NOT_IMPLEMENTED | not ready; active archive state is not read by this branch |
| HQ-MPSD | not accepted as authoritative release in current evidence | not adopted | unknown | not accepted | not ready; active archive state is not read by this branch |

## Stable provenance boundary

The appendix uses only repository evidence and stable official metadata. It does
not inspect changing HQ-MPSD/HAD `.part` files, and it does not promote any
synthetic smoke or historical metric to scientific W7 evidence.
