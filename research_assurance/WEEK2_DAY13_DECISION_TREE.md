# WEEK 2 — DAY 13 SCIENTIFIC DECISION TREE (pre-registered, result-blind)

Written before any A2 generation/metric exists. Four pre-defined outcome
scenarios; each fixes the supported interpretation, the forbidden
interpretation, and the priority shifts. No branch is pre-labelled
"success"; negative results carry scientific value. If the realized outcome
mixes scenarios, each applicable branch is reported and the paper claims
the intersection of their allowed interpretations.

Anchor for all branches: Week-1 frozen anchors — B1b S2 test AUROC
0.901/0.897 on A0/A1; C0 (same-speaker) at/below chance; B3 ORACLE 0.996;
B2/B4 negative.

---

## Scenario A — B1 remains strong on A2

**Operative definition (frozen):** A2 B1b test AUROC (original population,
S2) ≥ 0.85, with zone ordering outside < boundary ≤ core preserved, and
case-level CIs excluding 0.5.

- **Supported interpretation**: sequence-local speaker-representation
  inconsistency survives same-text, target-conditioned, natural-duration
  TTS replacement under the tested immutable checkpoint — i.e. the signal
  is not an artifact of real-speech donor discontinuity alone, and the
  Week-1 specificity result extends to synthetic same-text substitution
  **for this generator/protocol**.
- **Forbidden interpretation**: "B1 detects deepfakes/TTS"; "robust to
  voice cloning"; any generator-family or unseen-condition generalization;
  deployment readiness; pure speaker-identity causality (C0 controls
  speaker change, but A2 similarity varies — see Scenario C interplay).
- **Next experiment**: Day-12 similarity-stratified analysis becomes the
  headline; then a second generator (week2b) to break the
  single-checkpoint dependency.
- **Channel robustness priority**: unchanged (still untested).
- **Second generator priority**: **RISES** (single-checkpoint evidence is
  now the weakest link).
- **Short-attack priority**: unchanged (separate axis).
- **Native long-form priority**: unchanged (still untested).
- **Paper framing change**: mechanism paper may now include a synthetic-
  speech section with the exact tested-checkpoint boundary; deepfake
  framing still forbidden until multi-generator evidence.

## Scenario B — B1 near chance on A2

**Operative definition:** A2 B1b test AUROC (original, S2) within
[0.40, 0.60] (CI including 0.5), zone audit flat.

- **Supported interpretation**: the Week-1 B1 signal does **not** transfer
  to whole-utterance same-text target-conditioned TTS replacement under
  the tested checkpoint — i.e. the Week-1 signal likely depended on
  real-speech donor properties (cross-speaker natural-utterance
  discontinuity) that same-text synthetic replacement does not reproduce,
  or ECAPA-based consistency is insufficient for this synthetic condition.
- **Forbidden interpretation**: "B1 failed"; "the Week-1 result was wrong";
  "TTS is undetectable by speaker embeddings" (one checkpoint, one
  protocol); "A2 implementation must be wrong" without failure-class
  evidence.
- **Next experiment**: FIRST the Day-12 similarity/CER/duration
  diagnostics to characterize *why* (e.g. near-target synthetic similarity,
  duration collapse), THEN a second generator and/or reference-variation
  study. Also re-examine A2 failure classes: a chance result on a heavily
  failed pilot is inconclusive, not negative.
- **Channel robustness priority**: unchanged.
- **Second generator priority**: **RISES strongly** (distinguish
  checkpoint-specific from family-general behavior).
- **Short-attack priority**: DROPS (resolution is moot if the primary
  condition is at chance).
- **Native long-form priority**: unchanged.
- **Paper framing change**: the paper becomes a **boundary-mapping study**
  ("when does speaker-consistency localization hold?"): Week-1 positive on
  real-speech cross-speaker splice, Week-2 negative boundary on same-text
  TTS — a genuinely useful negative result with full provenance.
  Scientific value: HIGH; framing must avoid both over-claiming failure
  and burying it.

## Scenario C — B1 performance tracks speaker similarity (continuous)

**Operative definition:** the Day-12 P1 Spearman association between
case-level target↔synthetic cosine and B1b case AUROC/AUPRC has a bootstrap
CI excluding zero (direction either way), regardless of the overall A2
level.

- **Supported interpretation**: within this pilot, B1's localization
  strength varies **monotonically with the synthetic voice's similarity to
  the target speaker representation** — evidence that the signal measures
  a graded representation distance rather than a binary real/synthetic
  property. (If the association is NEGATIVE — higher similarity ⇒ weaker
  localization — this is the expected direction for a distance-based
  signal and also supports the graded reading.)
- **Forbidden interpretation**: "voice cloning of the target defeats
  detection" (similarity here is embedding distance, not perceptual clone
  quality); "ECAPA cosine is a validated deepfake metric"; any causal
  claim; per-case similarity thresholds as operational detectors.
- **Next experiment**: similarity-gradient study with multiple reference
  choices / generators producing a controlled similarity range; add
  perceptual similarity measures as separate diagnostics.
- **Channel robustness priority**: unchanged.
- **Second generator priority**: **RISES** (a similarity gradient on one
  checkpoint may not extend).
- **Short-attack priority**: unchanged.
- **Native long-form priority**: unchanged.
- **Paper framing change**: adds a graded-mechanism subsection; the
  correlation-not-causation caveat is mandatory and must appear in the
  abstract if this becomes a headline finding.

## Scenario D — Boundary/core analysis indicates artifact-driven results

**Operative definition:** on A2, B1b zone statistics show boundary mean
substantially above core mean (or B4-style transient diagnostics — any
DIAGNOSTIC, frozen in advance — fire at the crossfades), while
conditional-on-speech-active or blend-excluded views erase most of the
signal.

- **Supported interpretation**: whatever A2 signal exists is dominated by
  splice-boundary/crossfade artifacts rather than synthetic-speech core
  properties; the Week-1 core-entering behavior did not transfer.
- **Forbidden interpretation**: silent re-attribution of Week-1 results
  ("Week 1 was boundary-driven too") without re-running the Week-1 zone
  audit under the same definitions; or "TTS core is undetectable".
- **Next experiment**: crossfade ablation (with-amendment: it is a
  protocol change) and/or core-only evaluation research; re-audit Week-1
  zone numbers for comparability before claiming a contrast.
- **Channel robustness priority**: unchanged.
- **Second generator priority**: unchanged.
- **Short-attack priority**: unchanged.
- **Native long-form priority**: **RISES** (construction-specific boundary
  effects motivate more natural material).
- **Paper framing change**: any positive A2 claim is withdrawn; the paper
  reports the boundary dependence as the finding, with the B4/B4-style
  DIAGNOSTIC role kept strictly separate from detector claims.

---

## Cross-scenario rules

- Every branch reports realized denominators and failure classes first
  (a result on < 20 valid cases is annotated as fragile).
- All branches keep: B3 ORACLE exclusion; original+conditional paired
  reporting; correlation≠causation wording; the frozen unsupported-claims
  list.
- Branch priority shifts feed the Week-3 planning discussion only; they do
  not authorize any work in Week 2 beyond the pre-registered plan.
