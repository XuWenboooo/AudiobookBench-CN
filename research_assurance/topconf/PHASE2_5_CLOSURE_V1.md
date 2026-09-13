# Phase 2.5 Infrastructure Closure v1

Status: **PASS FOR PHASE 3 AUTHORIZATION PREPARATION / NO SCIENTIFIC EXECUTION**

## Closure results

- RangeEER official source verified: `nii-yamagishilab/PartialSpoof`, commit
  `847347aaec6f65c3c6d2f17c63515b826b94feb3`; `metric/RangeEER.py` SHA256
  `8B9C65C20C89443DC36AA77C4862CE9E89F62A2FB48227096F37D44E22DEE194`.
  Pure implementation follows the published range-duration FPR/FNR equations;
  synthetic reference tests pass for perfect, miss, boundary/resolution and
  constant-score fixtures. It remains a candidate implementation, not a
  replacement of the official algorithm.
- Dataset targets frozen to PartialSpoof v1.2 and PartialEdit v1.1; exact
  metadata, official MD5 and rights boundaries are recorded in the provenance
  register. No archives were downloaded.
- CFPRF and SAL license/provenance are source-verified; BAM remains
  `LICENSE_UNRESOLVED`; TRACE remains stretch/unverified.
- Whether-A primary pooling remains **NOT FROZEN** with a predefined decision
  procedure; no scientific scores were compared.
- Threshold policy, LD@DR95 candidate definition, statistical skeleton and
  Phase 3 authorization template are documented without confirmatory values.

## Exit gate

`RANGEEER_REFERENCE_VERIFICATION = PASS`

`PARTIALSPOOF_VERSION_FROZEN = YES`; `PARTIALSPOOF_GT_VERIFIED = SOURCE-YES,
LOCAL-PARSER-PENDING`

`PARTIALEDIT_VERSION_FROZEN = YES`; `PARTIALEDIT_GT_VERIFIED = SOURCE-YES,
LOCAL-PARSER-PENDING`

`CORE_BASELINE_PROVENANCE_VERIFIED >= 3 external paradigms = CONDITIONAL`;
source identity is verified, but BAM licensing and checkpoint hashes remain
blockers for unrestricted reproduction.

`THRESHOLD_POLICY = DEFINED`; `LD_DR95 = READY_FOR_PREREG_DECISION`;
`STATISTICAL_PROTOCOL = SUFFICIENT_FOR_PHASE3_AUTHORIZATION_REVIEW`.

`SCIENTIFIC_RUNS_INVOKED = NO`; `READY_FOR_CONFIRMATORY_EXPERIMENT_EXECUTION = NO`.
