# WEEK 2 — PUBLICATION CLAIM GATE (A2 evidence → permitted language)

Frozen before A2 execution. This gate defines exactly which terms may be
used for the first time after A2 completes, and which remain forbidden
regardless of A2 outcome. It complements `results/week1/claims.md` and
`DAY6C`/`DAY6B` claim boundaries.

## 1. Evidence classes (E-classes) produced by A2

- **E1** — A2 generation completed with realized denominators and failure
  taxonomy (exists after Day 10).
- **E2** — A2 evaluation under frozen Week-1 baselines/thresholds, original
  population (exists after Day 11).
- **E3** — Conditional-on-speech-active A2 evaluation (Day 11).
- **E4** — Day-12 similarity/mechanism diagnostics (P1 association + CIs).
- **E5** — Day-13 scenario determination (A/B/C/D) under the decision tree.
- **E6** — Second-generator replication (**does not exist in Week 2A**;
  requires week2b).

## 2. Term-by-term gate

| Term | First permitted when | Required qualifier | Still forbidden with |
|---|---|---|---|
| "TTS replacement" (describing A2 stimuli) | E1 | name the generator, checkpoint hash, constructed protocol | presenting as perceptually validated TTS quality |
| "synthetic speech" (describing A2 stimuli) | E1 | "under the tested immutable checkpoint" | "synthetic speech detection" results before E2 |
| "voice-conditioned replacement" | E1 | "conditioning intent; identity not verified" | "voice cloning quality" claims (no perceptual study) |
| "deepfake context" (motivation only) | E1 | as motivation/related work | "deepfake detection" results |
| "deepfake detection" (as a result) | **NOT PERMITTED in Week 2A** | requires ≥ E6 + perceptual + multi-condition studies | — |
| "same-text TTS localization signal" | E2 + E5 ∈ {A} or {C with graded framing} | quote AUROC **and** AUPRC/F1; name checkpoint; constructed-protocol caveat | "TTS detection solved"; generalizing beyond the checkpoint |
| "robust" | **NOT PERMITTED** for any untested condition (channel, codec, unseen generator, adaptive) | per-condition evidence only | unqualified "robust" |
| "generalize" | NOT PERMITTED in Week 2A (E6 missing) | — | "generalizes to unseen generators/speakers/data" |
| "adaptive robustness" | NOT PERMITTED (no adaptive experiment) | — | — |
| "native audiobook" | NOT PERMITTED (constructed protocol) | — | any native-audiobook result or benchmark claim |
| "speaker causality" | NOT PERMITTED (text confound remains; A2 adds same-text evidence but no causal identification) | may say "consistent with speaker-representation dependence" | "caused by speaker identity" |
| "deployment-ready" | NOT PERMITTED | — | any deployment/readiness claim |
| "universal forensics" | FORBIDDEN | — | — |
| "significant" | NOT PERMITTED (no hypothesis tests pre-registered) | CIs only | "statistically significant" |
| "conditional-on-speech-active" | E3 (mandatory pairing) | always with the unmasked population | masked-only presentation |
| "ORACLE" | as labelled in Week 1 | B3 never in deployable tables | — |

## 3. Interaction rules

1. E5 Scenario B (chance) **blocks** every positive TTS-related term above;
   the paper pivots to the boundary-mapping framing (see decision tree).
2. E5 Scenario D (boundary-driven) **blocks** "localization signal"
   language for A2 entirely; only the artifact-dependence finding may be
   claimed.
3. E4 associations are always reported as correlations with CIs; they
   never upgrade any other term's gate.
4. A failure-heavy pilot (realized denominators disclosed) caps all
   performance language to the realized subset.
5. A2 claims may never retroactively strengthen Week-1 claims (Week-1
   wording stays frozen).

## 4. Pre-written maximal claim (E1–E5, Scenario A, all qualifiers)

> "Under a frozen constructed protocol, whole-utterance same-text
> target-speaker-conditioned TTS replacement (CosyVoice2-0.5B, checkpoint
> SHA-256 recorded) was localized by a non-trained sequence-local
> ECAPA-consistency baseline (test AUROC X.XX, AUPRC Y.YY; conditional-
> on-speech-active variant reported alongside). The result is specific to
> the tested checkpoint and protocol; it does not establish deepfake
> detection, generator generalization, robustness, or deployment
> readiness."

Anything stronger than this template requires an amendment record and new
evidence classes.
