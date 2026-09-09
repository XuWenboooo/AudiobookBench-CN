# Paper Skeleton — AudiobookBench-CN (structure only)

STATUS: skeleton for planning. Not a submission draft. Sections 9–10 are
placeholders for experiments that do not exist yet.

---

# Working Title

Localizing Cross-Speaker Substitution in Constructed Long-Form Speech:
A Controlled Mechanism Study of Temporal Speaker-Representation
Consistency

*(alternative: "What Does a Speaker Embedding Notice? Controlled
Confounds for Temporal Speaker-Consistency Localization")*

## Abstract Skeleton

- **Problem**: long-form speech can contain localized real-speech
  substitutions; utterance-level metrics cannot say where.
- **Motivation**: security/forensics-motivated mechanism study; need
  controlled ground truth before touching synthetic speech.
- **Week-1 bounded mechanism result** (frozen): a global scalar robust-z
  anomaly fails (all observed AUROC < 0.5); an inference-only pretrained
  speaker-embedding sequence-local consistency signal strongly ranks
  cross-speaker substitutions (test AUROC ≈ 0.90 at 1.5 s windows) while a
  same-speaker different-utterance control does not trigger it (23/23
  cases); constructed utterance transitions explain most outside false
  positives; conditional-on-speech-active evaluation removes mainly
  transition/silence-heavy negatives.
- **Future A2 direction**: whole-utterance same-text voice-conditioned TTS
  replacement to separate speaker identity from linguistic content.
- MUST NOT claim: TTS detection achieved, deepfake localization solved,
  unseen-generator/adaptive robustness, deployment readiness.

## 1. Introduction

- localized manipulation in long-form audio; why utterance-level fails.
- contributions: (i) reproducible constructed-protocol pilot with exact
  sample GT; (ii) negative result for global scalar anomaly; (iii) positive,
  confound-controlled result for speaker-consistency; (iv) transition-FP
  mechanism; (v) claim-bounded evaluation protocol.

## 2. Related Work

### Long-form TTS evaluation
### Audio deepfake / spoofing detection
### Temporal localization
### Speaker representations
### Security evaluation

## 3. Threat Model

- Week-1 attacker: bounded real-speech cross-speaker replacement in a
  same-speaker long-form sequence; non-adaptive; no channel access.
- Explicit non-goals (adaptive, TTS, codec) with pointers to §9–10.

## 4. AudiobookBench-CN

- 12 speaker-disjoint speakers (6/3/3); 480 AISHELL-3 utterances; 24
  constructed sequences; lineage manifest; read-only raw data.

## 5. Manipulation Protocol

- A0 direct splice; A1 RMS-matched + 25 ms crossfade; C0 same-speaker
  control; duration tiers 0.75/1.5/2.5 s; full/strict-core/blend GT;
  fail-closed verification; sample-exact bounds.

## 6. Temporal Representations

- Day-5 grid (25 ms/10 ms; 224,566 frames; energy/log-energy/RMS/voiced/
  pause/Praat F0).
- ECAPA-TDNN (VoxCeleb, inference-only, 192-d, 16 kHz); S1 1.0 s/0.25 s and
  S2 1.5 s/0.25 s speaker grids.

## 7. Experimental Protocol

- train-only references and thresholds; speaker-disjoint splits; case-level
  bootstrap (2000, seed 20260905); original + conditional populations;
  ablations (NO_PAUSE/NO_ENERGY); label-agnostic speech mask (0.5).

## 8. Week1 Mechanism Study

### B0 negative
All observed AUROC < 0.5; zone audit (outside > core); already present on
train; bounded to the tested scalar family.

### B1 speaker consistency
S2 test AUROC 0.901/0.897; zone ordering outside < boundary < core;
AUPRC/F1 limits stated; case-level CIs.

### C0 confound control
Cross > same in 23/23 cases (core anomaly 0.729/0.732 vs 0.366/0.366);
C0 AUROC at/below chance; specificity-not-causality wording.

### transition analysis
144 clean top peaks, median 0.093 s to the nearest constructed boundary;
population audit of the mask.

## 9. Same-Text Synthetic Replacement

**WEEK2 — NOT YET AVAILABLE.** Protocol only: whole-utterance same-text
voice-conditioned natural-duration TTS replacement; dual timeline; suffix
shift; 25 ms crossfade; reuse of paired_case_id/target identity.

## 10. Generalization

**FUTURE / UNSUPPORTED.** Unseen generators, adaptive attackers, channel
shift, native audiobooks.

## 11. Discussion

- why global statistics fail while sequence-local consistency works;
- what C0 does and does not control; ECAPA as speaker+channel+prosody
  representation; resolution vs embedding stability trade-off (S1 vs S2).

## 12. Limitations

From results/week1/limitations.md + Reviewer Attack Surface HIGH items.

## 13. Responsible Claims

Supported / supported-with-boundary / unsupported lists verbatim from
results/week1/claims.md; per-claim required/forbidden wording from
CLAIM_AUDIT.md.

## Appendix

- A. Frozen protocol configs and hashes (696-entry chain).
- B. Population audit and correction history (3 resolved historical
  corrections).
- C. Reproduction entry and environment records.
- D. Failure-case gallery.
