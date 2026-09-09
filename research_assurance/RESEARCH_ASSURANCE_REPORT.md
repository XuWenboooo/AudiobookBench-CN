# Week 1 Research Assurance Report

Date: 2026-09-05
Role: independent research reviewer + paper-readiness auditor (bypass task;
Day 8 / A2 / supervised detectors explicitly out of scope and untouched).
All outputs are confined to `research_assurance/`. Zero modifications to
any frozen Week-1 artifact, any Day 5–6C canonical artifact, or anything
owned by the Day-8 Codex session.

## 1. Executive Summary

The frozen Week-1 evidence chain is **internally consistent, fully
traceable, and honestly bounded**. The verify-only entry re-confirmed the
696-entry frozen hash chain (0 missing, 0 mismatch). All 28 audited
headline numbers trace to their frozen artifacts; 27 are exact or standard
rounding, 1 is a LOW cosmetic rounding deviation (C4 median printed 0.094 s
vs stored 0.093375 s). The Week-1 figures use the seconds time axis with
manifest-exact GT bands (5-case spot check including paircase_0001:
13.75–14.50 s ✓). The Day-6C historical corrections do not reappear
anywhere. The single Codex audit fix (population variant pooling) is
correctly scoped: it affected only the variant-labelled rows of
`speech_mask_population_audit.csv` and no metric or conclusion.

**RESEARCH ASSURANCE GATE = PASS** — the frozen evidence is a reliable
foundation for Week 2 and for the future mechanism-study paper. This is
not a statement that a paper is finished.

## 2. Audit Scope

Read/verify/document over: WEEK1_REPORT/FREEZE/RETROSPECTIVE,
CODEX_INDEPENDENT_AUDIT, AGENT_WEEK1_CONTINUITY_REVIEW, THREAT_MODEL*.md,
Day 3/3.5/4/4.5/5/6A/6B/6C reports, results/week1 + results/day5–day6c
(CSV/JSON/YAML/figures/hash manifests), configs/, src/. Excluded (owned by
Day-8 Codex): results/day8/, .venv-cosyvoice/, third_party/CosyVoice/,
DAY8_PRECHECK.md, any download/installation state.

## 3. Frozen Integrity

- `--verify-only`: PASS — 696/696 hashes, 0 missing, 0 mismatches.
- Independent re-hash of the 17 Day-6C final artifacts recorded during the
  integrity correction: all match (the population-audit entry was updated
  by the disclosed Codex correction flow to 9886F17E…, verified).
- ECAPA checkpoint SHA-256 pinned in WEEK1_FREEZE ✓.
- No Week-1 artifact was modified by this audit.

## 4. Reviewer Attack Summary

32 grounded objections (4 reviewers × 8) in
`REVIEWER_ATTACK_SURFACE.md`. Zero CRITICAL. Four HIGH, all scope items
already declared unsupported in the frozen claims: constructed-vs-native
gap (A1), different-text confound (A2), missing A2 same-text TTS (A5),
adaptive attacker (B2-I). Strongest objections per reviewer:

- **A (Speech/TTS)**: different-text splice means the signal's specificity
  to *speaker identity* (vs phonetic/content discontinuity) is not yet
  proven — C0 controls the speaker factor but not text; A2 is required.
- **B (Security/Forensics)**: the C0 condition **is** a viable evasion —
  an attacker who splices the target speaker's own utterances defeats B1
  by construction; B1 is not an anti-evasion detector and the reports say
  so.
- **C (ML/Evaluation)**: masked metrics are computed on a shifted
  population (prevalence 0.052→0.074); AUPRC comparisons across populations
  are partly prevalence effects — the conditional framing is mandatory
  (enforced in reports; population audit quantifies it).
- **D (Reproducibility)**: no git metadata in the canonical directory;
  the 696-hash chain substitutes, but version control is the missing
  infrastructure piece.

## 5. Claim Audit Summary

`CLAIM_AUDIT.md`: 24 normalized claims audited across five levels
(SUPPORTED 9 / SUPPORTED WITH BOUNDARY 8 / WEAK-NEEDS QUALIFICATION 0
standalone / UNSUPPORTED 4 / FORBIDDEN UNDER CURRENT EVIDENCE 5 —
speaker causality, deepfake, TTS-as-tested, generalize, real audiobook).
Every claim carries required wording and forbidden stronger wording.
**Claim audit: PASS.**

## 6. Numeric Traceability

`NUMERIC_TRACEABILITY.md`: 28 programmatic claim→artifact comparisons,
plus a 5e-7 exact cross-check of `metrics_summary.csv` against upstream
artifacts. Result: 25 exact/standard rounding, 2 acceptable 2-dp
roundings, **1 LOW inconsistency** (C4 median 0.093375 printed as 0.094;
standard rounding is 0.093; deviation 0.0006 s, no consequence, recorded
not corrected). **Numeric traceability: PASS.**

## 7. Figure Integrity

`FIGURE_AUDIT.md`: all 5 Week-1 figures use the seconds time axis; the
Day-6C index-axis GT bug does not reappear; ORACLE/DIAGNOSTIC/conditional
labelling correct; negative and positive cases both present; no misleading
scales. GT spot check on 5 cases (incl. paircase_0001 = 13.7535–14.5035 s
from samples 220056–232056) matches the manifest exactly, backed by the
184/184 GT-axis audit. **Figure audit: PASS.**

## 8. Artifact Traceability

`ARTIFACT_INDEX.md`: full inventory across D3–W1 with stage, purpose,
frozen status, hash availability, paper/reproduction/audit relevance and
oracle/diagnostic/deployable status. Large datasets listed as
registry+count+hash (not per-file). **Artifact traceability: PASS.**

## 9. Statistical Integrity

`STATISTICAL_INTEGRITY.md`: case-level bootstrap (never windows); correlated
windows disclosed; NaN policy (never zero, never imputed); significance
sweep clean (only negations; one non-statistical prose use flagged as a
paper wording caution); no multiplicity issue because no per-slice
significance claims exist. Four recommendations recorded as FUTURE WORK.
**Statistical integrity: PASS.**

## 10. Reproducibility

`DEPENDENCY_AUDIT.md`: full Week-1 dependency chain verified
(numpy 2.5.2, scipy 1.18.1, parselmouth 0.4.7, torch 2.14.0+cpu,
speechbrain 1.1.1, …); ECAPA checkpoint hash-pinned and loaded offline;
requirements unpinned (documented risk); torch cross-version stability
evidenced (cosine 0.99999988). Source-code absolute-path scan: **0 hits**;
configs contain dataset-root lineage paths only (class A, bypassed by the
portable relpath mechanism). YAML audit: 11/11 parse with a safe loader,
no duplicate keys, no seed/split/threshold mismatches found.
**Dependency audit: PASS.**

## 11. Paper Readiness

`PAPER_SKELETON.md` (structure only) and
`PAPER_TRACEABILITY_MATRIX.md` (6 core claims → report/metrics/config/
code/figure/freeze) are in place. Sections 9–10 are explicitly marked
NOT YET AVAILABLE / UNSUPPORTED.

## 12. Critical Risks

**None.** No hash mismatch, no leakage, no GT error, no untraceable
metric, no material report-vs-artifact contradiction.

## 13. High Risks

1. Different-text confound (speaker vs content) — resolved only by A2.
2. Constructed-vs-native gap — scoped by claims.
3. Missing same-text TTS evidence — the paper cannot touch deepfake
   framing until A2 exists.
4. Adaptive evasion (same-speaker splice defeats B1 by construction) —
   disclosed; future work.

(Also HIGH-certainty but fully mitigated: small test case count — CIs
reported.)

## 14. Medium Risks

ECAPA non-speaker trait leakage (wording guarded); channel/codec untested;
unseen-generator untested; conditional-population misinterpretation
(framing enforced); pooled-window metric interpretation; 1.5 s-tier F1=0
threshold artefact; short-attack core coverage at S2; unpinned core
requirements; no git; transition-FP dependence on construction specifics.

## 15. Week2 Implications

- A2 (whole-utterance same-text voice-conditioned TTS replacement) is the
  single highest-value next experiment: it closes claim-gap #13/#2.
  Week-1 provides: reuse of paired_case_id/target identity, dual-timeline
  protocol, and the full evaluation machinery (masks, CIs, audits).
- Week-1 tier boundaries (0.75/1.5/2.5 s) must NOT be written as A2 exact
  intervals — A2 uses natural synthetic duration with suffix shift.
- Keep the original+conditional paired reporting convention for any A2
  evaluation.

## 16. Publication Readiness

分级：**CONFERENCE EXPERIMENTALLY INCOMPLETE.**

- The mechanism study (B0 negative → B1 positive → C0 specificity →
  transition/mask analysis) is coherent, reproducible and honestly
  bounded — more than a workshop-only result in terms of internal quality.
- But the paper's motivating question (synthetic/TTS manipulation in
  long-form audio) has **zero synthetic-speech evidence** until A2 runs;
  reviewer attack surface items A2/A5/B2-I/B3-I would be fatal at a
  speech-security venue today.
- Path: complete A2 (+ ideally channel/unseen-generator probes) →
  reassess; then this material supports a conference-grade controlled
  study with explicitly bounded claims.

## 17. Final Gate

**RESEARCH ASSURANCE GATE = PASS.**

Week-1 frozen evidence is internally consistent and traceable; it is a
reliable foundation for Week 2 and the future paper. The gate does not
mean the paper is complete, and it does not license any claim beyond the
frozen boundaries.
