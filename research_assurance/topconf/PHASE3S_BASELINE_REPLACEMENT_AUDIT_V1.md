# Phase 3S Baseline Replacement Audit v1

Status: **NO REPLACEMENT SELECTED**

This is a reproducibility-only audit. It does not authorize a full run and
does not select a baseline by performance.

| Candidate | Paper / paradigm | Official code | License | Checkpoint | Temporal output | Classification | Reason |
|---|---|---|---|---|---|---|---|
| PartialSpoof MultiReso | canonical multi-resolution partial-spoof localization | verified repository at frozen commit | BSD-3-Clause code; dataset rights separately tracked | official Zenodo route, not yet materialized | documented multi-resolution localization | CONDITIONAL | canonical lineage and official pretrained route |
| CFPRF | proposal refinement localization | verified repository and checkpoint hashes | MIT | verified existing FDN/PRN/XLSR | refined proposals | VERIFIED_EXISTING_PATH | existing infrastructure smoke only; full audio still required |
| SAL | segment-aware localization | verified official repository | MIT source | unavailable | documented frame localization | BLOCKED | checkpoint unavailable |
| BAM | boundary-aware localization | verified official repository | unresolved | README-linked Drive checkpoint; no official release asset | BLOCKED | rights/license unresolved |
| TRACE | embedding-trajectory approach | matching runnable official audio artifact not verified | unresolved | unavailable | not verified | BLOCKED | would require reimplementation and new provenance |

`RESULT_BASED_SUBSTITUTIONS = 0`

No candidate is promoted to a replacement baseline in Phase 3S. A new
candidate would require paper provenance, official code, clear license,
checkpoint identity, and temporal output verification before authorization.
