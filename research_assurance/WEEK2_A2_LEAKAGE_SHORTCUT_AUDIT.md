# WEEK 2 — A2 LEAKAGE / SHORTCUT AUDIT (pre-registered)

Each item: risk → current mitigation (already frozen in the A2 config or
Week-1 artifacts) → required test (before A2 results are quotable) →
remaining gap.

## 1. Reference audio leakage

- **Risk**: the 3–8 s speaker reference is construction-side only; if it
  leaked into the detector path, B1's "no enrollment" property would be
  void.
- **Mitigation**: `speaker_reference.access_side =
  attacker_construction_only`; `detector_access: forbidden`; frozen
  reference list per speaker; detector denylist in config.
- **Required test**: evaluation-loader denylist test — the scoring input
  object must expose only the suspect waveform; any reference field raises.
- **Remaining gap**: none beyond test enforcement.

## 2. Reference embedding leakage

- **Risk**: `reference_synthetic_ecapa_cosine` (a sidecar diagnostic) could
  be mistaken for a detection feature.
- **Mitigation**: field classed DIAGNOSTIC ONLY in the sidecar contract;
  detector denylist.
- **Required test**: same denylist test must cover embedding-typed sidecar
  fields.
- **Remaining gap**: none.

## 3. Speaker ID leakage

- **Risk**: `target_speaker`/`reference_speaker` columns adjacent to
  scoring rows invite accidental feature use.
- **Mitigation**: speaker metadata restricted to audits; Week-1 unit tests
  assert no baseline signature accepts speaker IDs; speaker-disjoint
  splits maintained.
- **Required test**: reuse Week-1 signature/leakage tests against the A2
  evaluation path.
- **Remaining gap**: none.

## 4. Paired-clean leakage

- **Risk**: A2 dual timelines make the clean counterpart available; B3-style
  clean-pair scoring would silently become deployable-looking.
- **Mitigation**: `b3_same_grid: forbidden`; `forbidden_baselines:
  B3_same_grid_clean_pair_oracle`; clean-embedding interpolation forbidden.
- **Required test**: `test_b3_forbidden_in_a2_primary` (Day-11 list).
- **Remaining gap**: B3 restricted to the common-prefix region remains an
  optional clearly-marked ORACLE diagnostic only.

## 5. Test-based threshold tuning

- **Risk**: variable-duration A2 invites "adjust thresholds for the new
  condition".
- **Mitigation**: `thresholds: reuse_week1_only`; frozen threshold sources
  pinned to Week-1 CSVs; Day-6A fixed |z| = 3.5 also frozen.
- **Required test**: `test_a2_threshold_reuse_frozen`.
- **Remaining gap**: none.

## 6. Generator metadata leakage

- **Risk**: generator identity/version in the sidecar could let an
  evaluation inadvertently condition on generator-specific artifacts (or
  imply generator-identification results).
- **Mitigation**: provenance fields are REQUIRED for provenance but classed
  out of the detector input path; generator metadata is not a feature.
- **Required test**: denylist test covers provenance fields; paper rule:
  generator identity appears only as a boundary qualifier.
- **Remaining gap**: generator-identification experiments are out of scope
  (week2b/c).

## 7. Failure-code leakage

- **Risk**: `generation_status/failure_reason` correlated with split could
  distort denominators (e.g. failures concentrated in test).
- **Mitigation**: retention policy; denominators reported per split and
  speaker; failure classes are pipeline-determined, outcome-blind.
- **Required test**: per-split failure-rate report in Day-10 close;
  any split-skew > 1 case is disclosed.
- **Remaining gap**: none.

## 8. Duration-delta shortcut

- **Risk**: `duration_delta_samples` shifts the suffix; a detector could in
  principle key on timeline-length changes rather than content.
- **Mitigation**: B1/B2 are window-content based (no length input); B0's
  grid is content-based; duration ratio is DIAGNOSTIC ONLY; pre-registered
  S3 analysis examines the association instead of exploiting it.
- **Required test**: report B1 performance on the pre-attack (clean-prefix)
  windows of A2 manipulated sequences as a null control — it should match
  clean behavior (no elevated anomaly from the shift itself).
- **Remaining gap**: a length-aware detector is out of scope and its
  existence would itself be a finding to disclose.

## 9. Crossfade shortcut

- **Risk**: the two 400-sample blend zones are deterministic mixtures; a
  detector could key on the crossfade envelope instead of synthetic core.
- **Mitigation**: 25 ms crossfade frozen (A1 artifact-control principle);
  strict-core GT excludes blends; core-only metrics reported; blend formula
  public; B4-style transient diagnostic available as DIAGNOSTIC.
- **Required test**: zone statistics (core vs blend_in/blend_out) reported
  separately in Day 11 outputs.
- **Remaining gap**: an adversary could smooth further; adaptive study out
  of scope.

## 10. Trim-edge shortcut

- **Risk**: deterministic edge trim leaves a characteristic 50 ms margin;
  trim points could be detectable.
- **Mitigation**: trim points are inside the attack/core region (edges of
  the synthetic segment), not at sequence boundaries; QA records
  leading/trailing trim; no test may target them.
- **Required test**: core-only metrics exclude trim edges by construction
  (core excludes 400-sample blends; trim margins lie within the synthetic
  segment); verify trim margins < core bounds in the validator.
- **Remaining gap**: none beyond disclosure.

## 11. Silence shortcut

- **Risk**: A2 replaced utterances may have different silence statistics
  than the removed real utterance; the fixed-gap construction could interact.
- **Mitigation**: speech-active mask is label-agnostic and applied
  identically; silence handling frozen (−45 dBFS trim); pause features were
  shown non-pivotal in Day-6C ablations (NO_PAUSE ≈ ALL).
- **Required test**: report pause/silence feature distribution shift
  between removed-real and inserted-synthetic segments as DIAGNOSTIC.
- **Remaining gap**: natural-silence conditions await native data.

## 12. Constructed-boundary shortcut

- **Risk**: A2 replaces a **complete utterance**, removing that utterance's
  own constructed boundaries — the attack region partially *removes* known
  transition FPs, which could inflate B1 contrast vs clean.
- **Mitigation**: C4 transition audit provides the clean baseline;
  evaluation reports outside-anomaly on A2 vs A0 for comparison;
  pre-registered S2 zone analysis.
- **Required test**: compare A2 outside-window anomaly against the matched
  A0 outside anomaly (same case); a large drop must be reported as a
  construction interaction, not a detector improvement.
- **Remaining gap**: fully natural material is the only complete fix.

## 13. Sample-rate / codec shortcut

- **Risk**: generator output may carry a different native SR or implied
  codec fingerprint; uniform 16 kHz mono PCM re-serialization mitigates but
  resampler artifacts could differ between real and synthetic segments.
- **Mitigation**: single resampler (algorithm+version recorded before
  implementation); identical serialization for all outputs; asymmetric DSP
  (denoise/EQ/limiter/codec) forbidden by config.
- **Required test**: record resampler identity in the sidecar; verify SR
  and format on every file (validator).
- **Remaining gap**: no codec-shift condition exists; scoped out.

## 14. File naming / path leakage

- **Risk**: record IDs embed variant/split (`..._c0a_...` in Week 1); a
  sloppy loader could infer labels from names.
- **Mitigation**: evaluation loaders index by explicit sidecar/manifest
  fields, never by parsing filenames; Week-1 loaders already field-based.
- **Required test**: A2 loader unit test must map rows purely by sidecar
  fields (a renamed-file test).
- **Remaining gap**: none.
