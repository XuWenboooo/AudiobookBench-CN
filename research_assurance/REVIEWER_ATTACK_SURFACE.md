# Reviewer Attack Surface — Week 1 Pilot

Simulated peer-review attack audit on the frozen Week-1 evidence. Each
objection is grounded in the actual protocol/artifacts, with the current
evidence, the current best answer, the remaining gap, and a severity.
**32 objections (8 per reviewer).** No objection below reopens an already
resolved historical correction (bootstrap contrast labels, figure index
axis, population variant pooling — all HISTORICAL CORRECTIONS, RESOLVED,
current artifacts verified clean).

---

## Reviewer A — Speech / TTS expert

### A1. Constructed long-form is not an audiobook
- **OBJECTION**: 24 sequences of stitched AISHELL-3 utterances with fixed
  0.3 s zero-gaps are not audiobooks; prosodic continuity, chapter-level
  coherence and studio post-processing are absent, so localization behavior
  may not transfer.
- **CURRENT EVIDENCE**: All reports state constructed ≠ native; the lineage
  manifest keeps every utterance boundary traceable; C4 quantifies
  transition false positives.
- **CURRENT ANSWER**: Week 1 claims are explicitly bounded to the
  constructed protocol; the transition-FP mechanism analysis exists
  precisely because the construction is synthetic.
- **REMAINING GAP**: no native or native-like long-form evaluation.
- **SEVERITY**: HIGH (scope, not validity of internal claims).

### A2. Different-text splice confounds speaker with content
- **OBJECTION**: A0/A1 donors differ in utterance and text; B1 may respond
  to phonetic/prosodic discontinuity rather than speaker identity.
- **CURRENT EVIDENCE**: C0 same-speaker different-utterance control (23/23
  cross > same, C0 AUROC 0.32–0.38).
- **CURRENT ANSWER**: C0 shows a mere "real-speech swap" does not trigger
  B1 — the signal is specific to the speaker change under this protocol.
- **REMAINING GAP**: text is not controlled (C0 donors also change text);
  same-text TTS (A2) is the decisive missing control.
- **SEVERITY**: HIGH.

### A3. ECAPA embeddings are not purely speaker-specific
- **OBJECTION**: ECAPA encodes channel, recording and prosodic traits too;
  "speaker-representation inconsistency" may partly be channel/utterance
  inconsistency.
- **CURRENT EVIDENCE**: backend sanity (same-speaker cosine 0.682 vs
  cross 0.268 on this corpus); C0 control.
- **CURRENT ANSWER**: claims are worded as "speaker-representation
  inconsistency", never "pure speaker identity"; WEEK1 claims.md explicitly
  denies pure speaker-identity causality.
- **REMAINING GAP**: disentangling speaker vs channel factors would need
  matched-channel controls or channel-robust embeddings.
- **SEVERITY**: MEDIUM.

### A4. Fixed 0.3 s zero-silence gaps are unnatural
- **OBJECTION**: digital-silence gaps create an acoustic pattern absent in
  natural speech; they may dominate anomaly statistics.
- **CURRENT EVIDENCE**: Day 5 limitation recorded; Day 6C C4 attributes
  outside FPs to transitions; Day 6A zone audit shows gap-window FPs.
- **CURRENT ANSWER**: gaps are disclosed as a construction confound; the
  speech-active mask (label-agnostic) removes most gap/transition windows.
- **REMAINING GAP**: natural pause distributions untested until native data.
- **SEVERITY**: MEDIUM.

### A5. Same-text / voice-conditioned replacement is untested
- **OBJECTION**: the operationally interesting attack (same text, TTS voice
  clone) is absent; the pilot cannot speak to deepfake detection at all.
- **CURRENT EVIDENCE**: WEEK1 claims.md lists TTS robustness as not
  supported; A2 protocol designed (whole-utterance same-text voice-
  conditioned natural-duration TTS replacement), implementation on hold.
- **CURRENT ANSWER**: explicit unsupported-claims list.
- **REMAINING GAP**: the entire A2 experiment.
- **SEVERITY**: HIGH (for any deepfake-framed venue).

### A6. 16 kHz standardization discards band-width cues
- **OBJECTION**: resampling all audio to 16 kHz removes high-frequency
  recording fingerprint cues that real forensics would use; results are
  conditional on this choice.
- **CURRENT EVIDENCE**: pipeline standardizes consistently; Day 4.5
  verification confirms uniform SR.
- **CURRENT ANSWER**: this is a controlled simplification, uniformly applied
  to clean/attack/controls, so internal contrasts are fair.
- **REMAINING GAP**: no band-above-8kHz ablation.
- **SEVERITY**: LOW.

### A7. Utterance boundaries inside the attack interval
- **OBJECTION**: a replaced region may contain natural utterance boundaries;
  are GT intervals aligned such that "core" excludes natural transitions?
- **CURRENT EVIDENCE**: GT is sample-exact from the manifest; blend/core
  semantics recorded per variant (A1 core shrinks by 400-sample crossfades).
- **CURRENT ANSWER**: core is defined by construction; transition overlap
  with core is measurable and the majority-rule labels are frozen.
- **REMAINING GAP**: sensitivity to the 0.5 majority threshold unexplored
  (pre-declared single convention).
- **SEVERITY**: LOW–MEDIUM.

### A8. Praat F0 and simple energy features are weak instruments
- **OBJECTION**: Day 5 signals (frame F0, RMS, pause flags) are coarse;
  the B0 negative may reflect instrument weakness, not the failure of all
  global-statistical approaches.
- **CURRENT EVIDENCE**: DAY6C report and retrospective explicitly bound the
  B0 failure to "the tested generic global scalar anomaly".
- **CURRENT ANSWER**: claims are bounded to the tested baseline family.
- **REMAINING GAP**: stronger global baselines (e.g. learned SSL-statistics
  baselines) untested.
- **SEVERITY**: MEDIUM.

---

## Reviewer B — Security / Forensics expert

### B1-I. Threat model is narrow and weak
- **OBJECTION**: one localized replacement per sequence, no multiple
  edits, no compression, no denoising attacker.
- **CURRENT EVIDENCE**: THREAT_MODEL_v0 scoping; WEEK1 unsupported list.
- **CURRENT ANSWER**: pilot explicitly scoped; multi-edit/channel variants
  deferred.
- **REMAINING GAP**: protocol extensions.
- **SEVERITY**: MEDIUM (for the mechanism-study framing), HIGH (if framed
  as a security benchmark).

### B2-I. No adaptive attacker
- **OBJECTION**: an attacker matching speaker statistics (or simply using
  the target speaker's own utterances — exactly the C0 condition) evades
  B1 by construction.
- **CURRENT EVIDENCE**: C0 is precisely this attack and B1 does not fire on
  it — which the reports state plainly.
- **CURRENT ANSWER**: honest disclosure; adaptive attacker reserved.
- **REMAINING GAP**: adversarial evaluation.
- **SEVERITY**: HIGH (security framing).

### B3-I. Unseen generator/speaker generalization absent
- **OBJECTION**: speaker-disjoint splits exist, but all attacks use real
  AISHELL-3 speakers; no unseen TTS generator condition.
- **CURRENT EVIDENCE**: unsupported-claims list.
- **CURRENT ANSWER**: scoped out of Week 1.
- **REMAINING GAP**: Week ≥2 generator studies.
- **SEVERITY**: HIGH (security framing).

### B4-I. Channel/codec shift untested
- **OBJECTION**: forensic audio arrives compressed; no MP3/AAC/noise
  robustness data.
- **CURRENT EVIDENCE**: unsupported list.
- **CURRENT ANSWER**: scoped out.
- **REMAINING GAP**: channel-shift protocol.
- **SEVERITY**: MEDIUM.

### B5-I. Oracle contamination risk
- **OBJECTION**: B3 uses the paired clean original; if any deployable claim
  quietly leaned on it, the forensic setting is violated.
- **CURRENT EVIDENCE**: B3 marked ORACLE ONLY in config, code, CSVs,
  figures and both reports; deployable baselines are B1a/B1b/B2 only.
- **CURRENT ANSWER**: strict labelling everywhere (verified in figure
  audit).
- **REMAINING GAP**: none identified in current artifacts.
- **SEVERITY**: LOW (as currently handled).

### B6-I. Detection vs localization vs attribution conflation
- **OBJECTION**: "localization" claims may rest on ranking (AUROC) rather
  than usable interval output (precision/IoU).
- **CURRENT EVIDENCE**: reports consistently pair AUROC with AUPRC/F1 and
  peak error; WEEK1_REPORT states ranking strong, precision limited.
- **CURRENT ANSWER**: claims say "temporal ranking/localization signal",
  not "deployable localizer".
- **REMAINING GAP**: IoU-style interval metrics not yet implemented.
- **SEVERITY**: MEDIUM.

### B7-I. Enrollment/reference leakage paths
- **OBJECTION**: does any deployable path touch test-speaker enrollment or
  clean references?
- **CURRENT EVIDENCE**: B1 prototype is built from the suspect sequence
  only (unit-tested); B3 is the only clean consumer and is ORACLE; speaker
  IDs excluded from features (unit-tested); speaker-disjoint audit 6/3/3.
- **CURRENT ANSWER**: leakage guards are tested in CI.
- **REMAINING GAP**: none identified.
- **SEVERITY**: LOW.

### B8-I. Responsibility/attribution claims
- **OBJECTION**: THREAT_MODEL v0 promised responsibility scoring; Week 1
  delivers nothing there.
- **CURRENT EVIDENCE**: not claimed anywhere in Week 1 outputs.
- **CURRENT ANSWER**: deferred by design.
- **REMAINING GAP**: future work.
- **SEVERITY**: LOW (as long as unclaimed).

---

## Reviewer C — ML / Evaluation expert

### C1-I. Six test cases
- **OBJECTION**: 6 val / 6 test paired cases cannot support precise
  performance estimates.
- **CURRENT EVIDENCE**: case-level bootstrap CIs reported (S2 B1a test
  AUROC CI [0.813, 0.948]); limitations listed everywhere.
- **CURRENT ANSWER**: uncertainty quantified at the case level; claims
  bounded.
- **REMAINING GAP**: more cases.
- **SEVERITY**: HIGH (for point-estimate precision).

### C2-I. Overlapping windows are correlated
- **OBJECTION**: 0.25 s hop with 1.0/1.5 s windows ⇒ adjacent windows share
  up to 87.5 % of audio; window counts inflated.
- **CURRENT EVIDENCE**: bootstrap unit is paired_case_id (never windows);
  limitations state non-independence.
- **CURRENT ANSWER**: case-level CI is the primary uncertainty analysis.
- **REMAINING GAP**: none critical.
- **SEVERITY**: LOW (handled).

### C3-I. Pooled-window metrics across sequences
- **OBJECTION**: pooling windows from different sequences mixes per-sequence
  prototypes' score scales.
- **CURRENT EVIDENCE**: pooled metrics reported alongside per-case metrics
  (case AUROC median 0.898–0.907).
- **CURRENT ANSWER**: both views present; pooled AUROC is not the sole
  basis of claims.
- **REMAINING GAP**: score-calibration across sequences unexplored.
- **SEVERITY**: MEDIUM.

### C4-I. AUROC vs AUPRC divergence
- **OBJECTION**: headline AUROC ~0.9 coexists with AUPRC 0.45 under ~5 %
  prevalence; ranking ≠ usable detection.
- **CURRENT EVIDENCE**: metrics_summary.csv labels S2 rows
  "strong_temporal_signal" not "deployable"; claim addendum exists.
- **CURRENT ANSWER**: claims explicitly avoid high-precision language.
- **REMAINING GAP**: none (handled).
- **SEVERITY**: LOW (handled).

### C5-I. Conditional-on-speech-active population shift
- **OBJECTION**: masked metrics are computed on a different population
  (prevalence 0.052→0.074); comparing them to unmasked is apples-to-oranges.
- **CURRENT EVIDENCE**: population audit (positives retained 0.96–1.00,
  negatives ~0.67); reports label masked results
  "conditional-on-speech-active" and forbid standalone-improvement reading.
- **CURRENT ANSWER**: conditional framing is enforced in reports and claims.
- **REMAINING GAP**: a matched-population comparison (mask applied to both
  classes' reporting) could be added as future work.
- **SEVERITY**: MEDIUM.

### C6-I. Threshold selection and reuse
- **OBJECTION**: train-only max-F1 thresholds were reused for val/test and
  both GT variants; also a fixed |z| = 3.5 threshold exists in Day 6A.
- **CURRENT EVIDENCE**: thresholds frozen in configs; unit tests assert
  val/test thresholds equal the train threshold.
- **CURRENT ANSWER**: no test tuning; documented.
- **REMAINING GAP**: none.
- **SEVERITY**: LOW.

### C7-I. No significance tests / multiple comparisons
- **OBJECTION**: many metric slices reported without multiplicity control;
  observed orderings (e.g. A0 vs A1) could be noise.
- **CURRENT EVIDENCE**: reports avoid "significant" language (post-correction
  wording verified in the continuity review); bootstrap CIs provided for key
  contrasts.
- **CURRENT ANSWER**: descriptive statistics + CIs; no p-value claims.
- **REMAINING GAP**: formal paired tests deferred (recommendation only).
- **SEVERITY**: MEDIUM.

### C8-I. Undefined/NaN metric slices
- **OBJECTION**: S2/A1 0.75 s strict-core slice has no majority-positive
  window (NaN); clean-only slices have undefined AUROC.
- **CURRENT EVIDENCE**: NaN policy documented (NaN, not 0); WEEK1_REPORT
  §10 lists the unmeasurable slice; bootstrap NaN recorded, not imputed.
- **CURRENT ANSWER**: explicit unmeasurability rather than fabricated values.
- **REMAINING GAP**: a core definition measurable at S2 for 0.75 s attacks.
- **SEVERITY**: MEDIUM.

---

## Reviewer D — Reproducibility / Artifact reviewer

### D1-I. No git metadata in the canonical directory
- **OBJECTION**: WEEK1_FREEZE states "Git commit: NOT AVAILABLE"; provenance
  relies on hashes alone.
- **CURRENT EVIDENCE**: 696-hash frozen chain; per-stage hash manifests.
- **CURRENT ANSWER**: hash chain substitutes for version control at present.
- **REMAINING GAP**: initialize git for the repo (infrastructure, not
  research).
- **SEVERITY**: MEDIUM.

### D2-I. Environment drift between executions
- **OBJECTION**: Day 6B ran torch 2.14.0+cpu; the independent audit ran
  2.13.0+cpu.
- **CURRENT EVIDENCE**: WEEK1_FREEZE records both; fresh-vs-cached
  embedding cosine 0.99999988; B1 AUROC reproduced exactly from cached
  embeddings.
- **CURRENT ANSWER**: cross-version stability demonstrated on the frozen
  embeddings.
- **REMAINING GAP**: a lock file (requirements-speaker.txt exists but torch
  is documented, not pinned).
- **SEVERITY**: LOW–MEDIUM.

### D3-I. Report overwrite incident
- **OBJECTION**: DAY6A report was once overwritten by external text; how is
  lineage guaranteed?
- **CURRENT EVIDENCE**: restored from authoring session with identical
  numbers; all results/day6a/* hash-verified unchanged; incident disclosed
  in the restored header and DAY6B report.
- **CURRENT ANSWER**: disclosed and hash-guarded.
- **REMAINING GAP**: git would make this class of incident provable.
- **SEVERITY**: LOW (post-disclosure).

### D4-I. Historical Day 6C corrections
- **OBJECTION**: three corrections in one day (bootstrap labels, figure
  axis, population pooling) suggest process fragility.
- **CURRENT EVIDENCE**: all three are HISTORICAL CORRECTIONS — RESOLVED;
  current artifacts re-verified clean (continuity review + Week1 audit);
  corrections disclosed in DAY6C_INTEGRITY_CORRECTION.md and WEEK1_FREEZE.
- **CURRENT ANSWER**: the correction chain is documented and tested.
- **REMAINING GAP**: process maturity (pre-registration of analysis code).
- **SEVERITY**: LOW (as currently resolved).

### D5-I. Windows-specific pipeline
- **OBJECTION**: symlink handling, path separators, and the proxy workarounds
  recorded in DAY6B are Windows-specific.
- **CURRENT EVIDENCE**: offline local model copy + HF_HUB_OFFLINE removes
  the network dependency at run time; paths in code are repository-relative.
- **CURRENT ANSWER**: documented; no runtime absolute paths in src (scan: 0
  hits).
- **REMAINING GAP**: POSIX smoke test not yet run.
- **SEVERITY**: LOW–MEDIUM.

### D6-I. Checkpoint provenance
- **OBJECTION**: is the ECAPA checkpoint hash-pinned?
- **CURRENT EVIDENCE**: WEEK1_FREEZE records embedding_model.ckpt SHA-256
  0575CB64…126A2; local copy in-tree; offline load.
- **CURRENT ANSWER**: pinned and verified.
- **REMAINING GAP**: none.
- **SEVERITY**: LOW.

### D7-I. Seeds and determinism
- **OBJECTION**: are all stochastic steps seeded?
- **CURRENT EVIDENCE**: bootstrap seed 20260905 (2000 resamples); ECAPA CPU
  inference bit-identical; double-run byte-identical outputs at Day 6A/6B/6C.
- **CURRENT ANSWER**: documented and verified.
- **REMAINING GAP**: none identified.
- **SEVERITY**: LOW.

### D8-I. Figure regeneration fidelity
- **OBJECTION**: were figures regenerated after corrections, and do the
  committed PNGs match the current code?
- **CURRENT EVIDENCE**: Week-1 figures produced by the audited Week-1 code
  (index-axis bug not present — figure audit); Day 6C figures re-rendered
  post-correction with the seconds axis.
- **CURRENT ANSWER**: figure audit passed.
- **REMAINING GAP**: none.
- **SEVERITY**: LOW.

---

## Severity summary

| Severity | Count | IDs |
|---|---:|---|
| CRITICAL | 0 | — |
| HIGH | 4 | A1, A2, A5, B2-I (B3-I high under security framing) |
| MEDIUM | 12 | A3, A4, A7(–M), A8, B1-I, B4-I, B6-I, C1-I, C3-I, C5-I, C7-I, C8-I |
| LOW | remainder | A6, B5-I, B7-I, B8-I, C2-I, C4-I, C6-I, D1-I(M), D2-I, D3-I, D4-I, D5-I, D6-I, D7-I, D8-I |

Zero CRITICAL: no objection invalidates the frozen Week-1 evidence chain.
The HIGH items are scope limitations (constructed data, different-text
confound, missing A2, adaptive attacker) — all already declared unsupported
in the frozen claims, so they gate the *scope of the paper*, not the
*validity of Week 1*.
