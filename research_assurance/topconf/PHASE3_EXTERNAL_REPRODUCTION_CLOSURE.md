# Phase 3 External Reproduction Closure

Status: **BLOCKED — INFRASTRUCTURE VALIDATION COMPLETE, EXTERNAL REPRODUCTION NOT COMPLETE**

## Gate decision

`PHASE3_EXTERNAL_REPRODUCTION_CLOSURE = BLOCKED`

`READY_FOR_PHASE4_CONFIRMATORY_DESIGN_FREEZE = NO`

`READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO`

## Evidence

- Phase 3 authorization was instantiated before any external model output was
  observed. Scope is limited to reproduction and infrastructure validation.
- The official PartialSpoof v1.2 protocols, segment labels, VAD metadata and
  README pass checksum verification. Segment-label parsers pass for train,
  dev and eval metadata at 0.16 seconds. The official audio archive was not
  completed; its local partial file fails the official MD5. The official
  v1.0 split fallback recommended by the v1.2 record was also probed, but the
  server returned a 504 HTML error with zero archive payload; this is recorded
  in the local manifest rather than treated as data.
- The official PartialEdit v1.1 CSV and speaker archive pass checksum
  verification. The CSV parser validates 85,007 rows, 85,632 edited regions,
  E1/E2 counts, and speaker metadata. E1/E2 audio and codec archives are not
  materialized, so duration/path cross-checks cannot pass.
- The two authorized CFPRF PS checkpoint files and the official fairseq XLSR
  front-end pass SHA256 recording and load checks. The official FDN state dict
  loads strictly with 0 missing and 0 unexpected keys, and one authorized
  PartialSpoof WAV produces finite segment/boundary outputs of shape
  `(1,107,2)` under a CPU-only infrastructure smoke. This is recorded only as
  `INFRASTRUCTURE_VALIDATION_ONLY`; no metric is reported. The official PRN
  checkpoint also loads strictly and produces finite verification/regression
  tensors on a synthetic embedding/proposal fixture; that fixture is not an
  external audio result. SAL has no verified local checkpoint. BAM remains
  rights-blocked. TRACE remains a stretch reimplementation and is not counted
  as a core reproduction.
- Parser/evaluator tests pass with `python -m pytest tests/topconf -q`.

## Non-results

No full external-baseline reproduction was completed, no full scientific
audio population was scored, and no external metric was computed. The limited
CFPRF infrastructure checkpoint/smoke loads above are not reproduction
metrics. No baseline was ranked or excluded by outcome. The Phase 4 design
freeze, confirmatory population, and RQ1/RQ2/RQ3 remain untouched.

## Reopening condition

Reopen only after the official audio archives and at least the authorized
external baseline checkpoint path are materialized and checksum/load/smoke
gates pass under a refreshed authorization commit. Any new model or output
contract requires a provenance entry before execution.
