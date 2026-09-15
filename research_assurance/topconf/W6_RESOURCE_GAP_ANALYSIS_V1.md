# W6 Resource Gap Analysis v1

Audit date: `2026-09-15`  
Status: `BLOCKED / MINIMUM RECOVERY ACTION FROZEN`  
No result, threshold, metric or confirmatory outcome was used for any
eligibility decision.

## Current gap

```text
DISTINCT_LOCALIZATION_PARADIGMS_READY = 2
REQUIRED = 4
READY_IDS = P2_FRAME_PLUS_PROPOSAL_REFINEMENT, P3_MULTI_RESOLUTION_FRAME
W6_GATE = BLOCKED
```

The six MultiReso temporal scales are one paradigm. CFPRF's FDN, boundary and
PRN outputs are one proposal-refinement paradigm. AASIST is utterance-only,
B4 is diagnostic-only, and neither can fill the gap.

## Candidate blockers

| Candidate | Objective blocker | Minimum evidence needed |
|---|---|---|
| SAL | official source commit is known, but no checkpoint is locally verified | obtain an official/legal checkpoint, bind SHA256, strict-load, bounded smoke, timestamp/output semantics and adapter |
| BAM | repository/checkpoint source exists, but repository license and checkpoint rights are unresolved | author/source rights decision plus checkpoint hash, strict-load/smoke and output adapter |
| TRACE | paper-level method is identified, but no matching official audio-localization implementation/checkpoint/output contract is verified | official implementation/checkpoint, or a prospective resource amendment explicitly accepting a clearly labeled reimplementation without changing the W7 target |

## Minimum recovery action

Recover exactly two additional *distinct* legal localization mechanisms from
the candidates above, in this order: (1) resolve one of SAL/BAM through an
official checkpoint-and-rights path; (2) resolve the other, or verify TRACE's
official audio implementation. Each recovery must pass the full W7 model
preflight before it is counted. Do not train a replacement, add a backbone,
count scales as paradigms, or inspect W7/confirmatory outcomes.

If SAL, BAM and TRACE are objectively unavailable after bounded official-source
checks, prepare `TOPCONF_19W_W6_BASELINE_RESOURCE_AMENDMENT_V1.md` with
`AMENDMENT_TYPE=RESOURCE_SUBSTITUTION`, preserving hypothesis, threat model,
metrics, paradigm target and W7 gate. No amendment is issued by this audit
because the current evidence records unresolved gates, not objective
unavailability.

## W7 consequence

The missing paradigms are a W6/Gate-A blocker, not a reason to run a partial
scientific pilot. `W7_FORMAL_PILOT_AUTHORIZED=NO` until the W6 four-paradigm
gate and all other W7 gates pass.
