# External Reproduction Register v1

Status: **PHASE 3 NOT COMPLETE: EXTERNAL AUDIO/CHECKPOINT GATES BLOCKED**

This is a run ledger, not a scientific result table. There are zero external
model-output rows and zero reproduction scores.

| Invocation | Dataset / split | Baseline | Scope | Status | Failure accounting |
|---|---|---|---|---|---|
| P3-ER-2026-09-13-01 | PartialSpoof v1.2 dev/eval | CFPRF | authorized metadata, checkpoint load, smoke, official reproduction | `NOT_INVOKED_BLOCKED` | audio archive download did not reach official checksum; checkpoint not materialized; `BLOCKED_DOWNLOAD_THROUGHPUT` |
| P3-ER-2026-09-13-01 | PartialEdit v1.1 E1/E2 and codec controls | CFPRF / SAL / BAM conditional | authorized metadata, checkpoint load, smoke, official reproduction | `NOT_INVOKED_BLOCKED` | audio archives not materialized; checkpoint/rights gates unresolved |
| P3-ER-2026-09-13-01 | PartialSpoof v1.2 metadata | parser validation only | official segment-label mappings and checksums | `INFRASTRUCTURE_VALIDATION_ONLY` | GT metadata passes; audio-duration crosscheck remains blocked |
| P3-ER-2026-09-13-01 | PartialEdit v1.1 metadata | parser validation only | official CSV and speaker lists | `INFRASTRUCTURE_VALIDATION_ONLY` | CSV/speaker metadata passes; audio-duration/path crosscheck remains blocked |

No synthetic metric is reported here. Synthetic fixtures are confined to
unit tests for parser and evaluator behavior.
