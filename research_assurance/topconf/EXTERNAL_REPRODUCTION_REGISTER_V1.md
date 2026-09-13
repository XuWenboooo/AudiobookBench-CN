# External Reproduction Register v1

Status: **PHASE 3 NOT COMPLETE: EXTERNAL AUDIO/CHECKPOINT GATES BLOCKED**

This is a run ledger, not a scientific result table. There are zero external
model-output rows and zero reproduction scores.

| Invocation | Dataset / split | Baseline | Scope | Status | Failure accounting |
|---|---|---|---|---|---|
| P3-ER-2026-09-13-01 | PartialSpoof v1.2 dev/eval | CFPRF | authorized metadata, checkpoint load, smoke, official reproduction | `SMOKE_PASS_FULL_REPRODUCTION_BLOCKED` | both PS checkpoint files, official XLSR front-end, strict FDN state load and one-sample forward pass; full audio archive fails official checksum; `BLOCKED_AUDIO_ARCHIVE` |
| P3-ER-2026-09-13-01-FDN-SMOKE | PartialSpoof v1.2 Level-1 sample `CON_E_0005290` | CFPRF FDN | strict checkpoint load plus one authorized WAV forward; no metric | `INFRASTRUCTURE_VALIDATION_ONLY` | strict state load: 0 missing/0 unexpected; finite segment and boundary outputs `(1,107,2)`; CPU device mapping used because host has no CUDA; not a reproduction score |
| P3-ER-2026-09-13-01-PRN-SMOKE | PartialSpoof v1.2 infrastructure fixture | CFPRF PRN | strict checkpoint load plus one synthetic embedding/proposal forward; no metric | `INFRASTRUCTURE_VALIDATION_ONLY` | official `2PRN_PS.pth` strict state load: 0 missing/0 unexpected; finite verification/regression outputs `(1,1)` and `(1,2)`; synthetic tensor only, not an external audio result |
| P3-ER-2026-09-13-01 | PartialEdit v1.1 E1/E2 and codec controls | CFPRF / SAL / BAM conditional | authorized metadata, checkpoint load, smoke, official reproduction | `NOT_INVOKED_BLOCKED` | audio archives not materialized; checkpoint/rights gates unresolved |
| P3-ER-2026-09-13-01 | PartialSpoof v1.2 metadata | parser validation only | official segment-label mappings and checksums | `INFRASTRUCTURE_VALIDATION_ONLY` | GT metadata passes; audio-duration crosscheck remains blocked |
| P3-ER-2026-09-13-01 | PartialEdit v1.1 metadata | parser validation only | official CSV and speaker lists | `INFRASTRUCTURE_VALIDATION_ONLY` | CSV/speaker metadata passes; audio-duration/path crosscheck remains blocked |

No synthetic metric is reported here. Synthetic fixtures are confined to
unit tests for parser and evaluator behavior.
