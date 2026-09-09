# Week2A Verification Matrix (human-readable companion to week2a_verification_matrix.csv)

Generated: 2026-09-05. Companions: `week2a_verification_matrix.csv` (92 rows),
`week2a_findings_registry.yaml`, `week2a_test_registry.yaml`,
`week2a_failure_registry.yaml`, `week2a_leakage_registry.yaml`,
`week2a_detector_denylist.yaml`, `week2a_claim_registry.yaml`,
`week2a_day13_decision_registry.yaml`, `week2a_gate_registry.yaml`,
`A2_STATUS_MODEL.md`, `tools/week2a_gate_check.py`.

## Current Status

| Stage | Status | Evidence |
|---|---|---|
| Week1 | CLOSED / PASS | research_assurance/RESEARCH_ASSURANCE_REPORT.md; 696/696 |
| Week2A protocol design | PASS | WEEK2_A2_PROTOCOL_DESIGN.md |
| Semantic correction | PASS | WEEK2_A2_PREIMPLEMENTATION_CORRECTION.md |
| Preregistration | PASS | WEEK2_A2_PREREGISTRATION_REPORT.md |
| Static compatibility | PASS | A2_STATIC_COMPATIBILITY_AUDIT.md |
| Day8 | HOLD | other Codex session; DAY8_PRECHECK.md absent |
| Day9 | BLOCKED_BY_DAY8 | dry-run |
| Day10 | BLOCKED_BY_DAY9 | dry-run |
| Day11 | BLOCKED_BY_A2_OUTPUT | dry-run |
| Day12 | BLOCKED_BY_A2_OUTPUT | dry-run |
| Day13 | BLOCKED_BY_A2_OUTPUT | dry-run |
| Week2A claims | NO_A2_CLAIMS_YET | dry-run |

Matrix composition: 17 FINDING + 21 TEST + 17 FAILURE_CLASS + 14 LEAKAGE + 7 GATE + 16 CLAIM_GATE = 92 rows.

## Gate Dependency Graph

```text
Week1 PASS
   |
Protocol PASS -> Semantic Correction PASS -> Preregistration PASS -> Static Compatibility PASS
   |
Day8 HOLD
   |
Day9 BLOCKED
   |
Day10 BLOCKED
   |
Day11 BLOCKED
   |
Day12 BLOCKED
   |
Day13 BLOCKED
   |
Week2A claims unavailable
```

## 17 Findings (normalized: 3 HIGH / 8 MEDIUM / 6 LOW-SAFE)

| ID | Severity | Area | Summary |
|---|---|---|---|
| F1 | HIGH | figure | clean trajectory overlaid on the manipulated time axis past the attack |
| F2 | MEDIUM | id parsing | clean id derived from filename convention |
| F3 | MEDIUM | loader | loaders hard-bound to Week1/C0 manifests |
| F4 | HIGH | thresholds | train-only recomputation vs frozen reuse_week1_only |
| F5 | HIGH | B3 | shape guard raises and aborts the A2 run; no denylist gate |
| F6 | MEDIUM | tiers | duration_tier treated as required metadata |
| F7 | MEDIUM | mask | speech-fraction fallback covers C0 only |
| F8 | MEDIUM | B4 | Day5 frame rows absent for A2 |
| F9 | MEDIUM | length | sample count back-derived instead of sidecar-exact |
| F10 | MEDIUM | lookup | variant registry lacks the a2 variant |
| F11 | LOW | peak error | SAFE (manipulated timeline) |
| F12 | LOW | mask align | SAFE (truncation already implemented) |
| F13 | LOW | bootstrap | SAFE (concatenation, unequal counts OK) |
| F14 | MEDIUM | control | pre-attack prefix null control absent |
| F15 | LOW | GT proj | SAFE (blend_in/out recording decision) |
| F16 | LOW | tier math | SAFE (covered by F6) |
| F17 | LOW | zip | SAFE (intra-record, lengths coincide) |

## 21 Required Tests (phases normalized)

PHASE_A_PRE_A2_UNIT (no real A2 TTS output): T01 (unit portion), T02, T03, T04,
T05, T06, T07, T08, T09, T11, T12, T13, T15, T16, T17, T21.
PHASE_B_FIXTURE_MANIFEST (sidecar/manifest fixture only): T10, T01 (fixture
portion).
PHASE_C_POST_A2_DATA (frozen A2 outputs required): T14, T18, T19, T20, plus all
real waveform/GT integration checks.
All result_status values are NOT_RUN; no test is claimed as implemented.

## 17 Failure Classes

See `week2a_failure_registry.yaml`; status_effect distribution: 15 HARD_FAILURE,
1 QA_FLAG (RMS_MATCH_FAIL), 1 DETERMINISM_LIMITATION (DETERMINISM_MISMATCH),
plus TRIM_COLLAPSE/INSUFFICIENT_SYNTHETIC_CORE counted as HARD_FAILURE.

## 14 Leakage Vectors

L1 reference audio, L2 reference embedding, L3 speaker ID, L4 paired-clean/B3,
L5 threshold tuning, L6 generator metadata, L7 failure code, L8 duration delta,
L9 crossfade, L10 trim edge, L11 silence, L12 constructed boundaries,
L13 sample rate/codec, L14 filename/path. All MITIGATED_PENDING_TEST.

## Detector Denylist

FORBIDDEN: reference_*, conditioning_*, speaker_enrollment_*, paired_clean_*,
generator_*, checkpoint_*, generation_status, generation_failure_reason,
qa_flags, GT fields (attack/core/blend), duration_delta, speaker IDs, split
labels, filename-derived labels, all detector/diagnostic scores.
ALLOWED: suspect waveform + Week1 baseline-required waveform-derived features
only.

## Day9 Gate

Requires Day8 PASS, backend provenance complete, checkpoint/component hashes
complete, offline reload PASS, determinism documented, reference freeze PASS,
sidecar contract ready, Week1 696/696; at most 3 official smoke cases.
Day8 disposable smoke is NOT Day9 official smoke.

## Day10 Gate

Requires Day9 official smoke 3/3, sidecar validator PASS, waveform/GT verifier
PASS, Week1 696/696, formal_generation_allowed true via the allowed transition.
No quality replacement, no score filtering, no silent reroll.

## Day11 Metric Gate

All PHASE_A tests PASS, applicable PHASE_B/C PASS, F1/F4/F5 resolved, B3 absent
from the primary path, frozen thresholds loaded, sidecar loader used,
variable-duration GT correct, grouping and mask alignment correct, denylist
PASS, realized denominator disclosed.

## Day12 Analysis Gate

P1/P2 with CIs, S1-S5 reported, D1-D4 as diagnostics; no post-hoc metrics, no
filtering, no promoted diagnostics.

## Day13 Decision Gate

Scenario A/B/C/D determined under the operative definitions; mixed outcomes use
the intersection-of-allowed-claims rule; no Scenario E.

## Publication Claim Gate

E1-E5 available in Week2A (E6 absent); deepfake detection, robust, generalize,
adaptive, native audiobook, deployment-ready, universal forensics, significant
remain forbidden; same-text TTS localization signal only under Scenario A/C with
full qualifiers.

## Current Blocking Chain

Day8 HOLD -> Day9 BLOCKED_BY_DAY8 -> Day10 BLOCKED_BY_DAY9 -> Day11/12/13
BLOCKED_BY_A2_OUTPUT -> Week2A claims NO_A2_CLAIMS_YET. This is correct status
propagation, not failure.
