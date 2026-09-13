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

## Append-only Phase3S materialization result

The official MultiReso checkpoint route was tested once under the frozen
Phase3S budget:

```text
SOURCE = https://zenodo.org/record/6674660/files/multi-reso.tar.gz?download=1
EXPECTED = 3895061057 bytes; md5:138fc6901a495ff71137d9ca15d9393a
RESULT = HTTP_504_ZERO_BYTES
STATUS = NOT_MATERIALIZED
```

CFPRF remains the only verified external baseline path, and only at
infrastructure/load level. PartialEdit E1 is a fully validated external audio
dataset, not a second baseline. Consequently:

```text
EXTERNAL_BASELINE_PATHS = 1
BASELINE_GATE = BLOCKED
PHASE3S_CLOSURE = BLOCKED_BASELINE_PATH_GATE
```

No candidate is promoted to a replacement baseline in Phase 3S. A new
candidate would require paper provenance, official code, clear license,
checkpoint identity, and temporal output verification before authorization.
