# AGENT_WEEK1_CONTINUITY_REVIEW.md

Reviewer: the agent that originally executed Day 5, Day 6A, Day 6B, Day 6C
and the Day 6C integrity correction.
Scope: **read-only continuity verification** of the Codex Week-1 closeout
(`WEEK1_REPORT.md`, `WEEK1_FREEZE.md`, `results/week1/`,
`CODEX_INDEPENDENT_AUDIT_DAY5_DAY6C.md`) against what was actually executed
in Day 5–Day 6C. No canonical Week-1 artifact was modified; no Week-2 work
was started.

Date: 2026-09-05
Verdict: **CONTINUITY REVIEW PASS**

## 1. Day 6A representation — PASS

- `WEEK1_REPORT.md` §7 states "Every observed AUROC is below 0.5" with the
  exact frozen values (test A0/A1: 0.379/0.378 @100 ms, 0.331/0.350
  @250 ms, 0.324/0.346 @500 ms) — verified byte-consistent with
  `results/day6a/metrics.json`.
- "No significance test was performed" is stated verbatim.
- The earlier "structural" wording is correctly replaced by "already
  present on train and cannot be explained by held-out distribution shift
  alone". No universal-failure claim exists.
- Verified against frozen artifact: 250 ms test A0 AUROC = 0.331217 ✓.

## 2. Day 6B representation — PASS

- Real backend correctly attributed (SpeechBrain ECAPA-TDNN,
  `speechbrain/spkrec-ecapa-voxceleb`, 16 kHz, 192-d, inference-only).
- B1 described as sequence-local speaker-representation inconsistency with
  "neither speaker ID nor enrollment".
- Explicit bounded claim: "not that a deployable high-precision localizer
  is solved"; precision limits stated (S2 AUPRC 0.454/0.491, F1 0.506).
- B3 marked ORACLE ONLY; B4 marked negative and DIAGNOSTIC ONLY.
- Frozen numbers verified: S2 B1b test AUROC 0.901421/0.896658, AUPRC
  0.453843/0.491193, F1 0.506329/0.506329; S1 B1b 0.830741 ✓.
- B2 range "roughly 0.37–0.45" matches frozen values (0.370398–0.447).

## 3. Day 6C representation — PASS

- C0 protocol described exactly as built (same frozen target interval,
  same-speaker same-split different-utterance donor, 23 C0A + 23 C0B,
  outside-unchanged/inside-changed).
- Core anomaly 0.729/0.732 (A0/A1) vs 0.366/0.366 (C0A/C0B) ✓; "every
  finite S1 paired contrast favors higher cross-speaker anomaly" ✓.
- C0 window AUROC 0.376/0.367 (S1), 0.323/0.307 (S2) ✓ traced to
  `original_vs_masked_metrics.csv`.
- Masked metrics explicitly labelled **conditional-on-speech-active** and
  required to be reported alongside the original population; the report
  does not interpret the masked AUPRC increase as a detector improvement.
- Short-attack limitation preserved (0.75 s AUPRC ≈ 0.124–0.125, F1
  ≈ 0.11–0.13; S2/A1 0.75 s strict-core not measurable under the frozen
  grid).
- C4 numbers verified against `clean_transition_audit.csv`: 144 peaks,
  median 0.0934 s (report: 0.094 s), 140/144 = 97.2 % within 1 s ✓.

## 4. The "Day 6C A0/A1 population mixed counting" audit fix

What the bug was: in the Day 6C speech-mask **population audit** generator,
the per-variant loop filtered rows by split but **not by variant**, so each
row labelled `a0`/`a1` actually pooled **A0+A1 together** (both labelled
rows carried identical pooled counts).

Affected files/fields:
- `results/day6c/speech_mask_population_audit.csv` — variant-labelled
  prevalence/retention rows only.

Fix-before / fix-after (SHA-256, disclosed by Codex and re-verified here):
- Before: `D4C32E80CBD8379F441B552039B330F0571547E46B34D8EEB1CB68474595F99B`
- After:  `9886F17E181DEA57180FEA79F9DB6782859F6A5389F842A4B8C15FF0E1C900FF`
- Current on-disk file matches the corrected hash; the corrected file now
  separates a0/a1 (e.g. S2 test full positive retention A0 1.000 vs
  A1 0.974 — previously identical pooled rows).

Impact assessment:
- AUROC: **NOT AFFECTED**
- AUPRC: **NOT AFFECTED**
- F1: **NOT AFFECTED**
- Speech-mask retention: affected **only in the variant-labelled audit
  table** (masks themselves unchanged); corrected retention range across
  all split/GT slices is 0.933–1.00 (previously pooled statement 0.96–1.00).
- Cross-vs-same conclusion: **NOT AFFECTED**
- Week-1 supported claims: **NOT AFFECTED** (direction unchanged; only the
  retention-range statement tightened, which WEEK1_FREEZE discloses).

Note: my own `results/day6c/day6c_final_hashes.json` entry for this CSV was
updated by the correction flow to the corrected hash, which is why my
re-hash diff showed 17/17 unchanged; the before/after hashes above come
from the Codex disclosure and were independently confirmed here.

## 5. Week-1 numeric traceability — PASS

Spot-traced to frozen artifacts (all matched):
- Day 6A 250 ms test A0 AUROC 0.331217 ← `results/day6a/metrics.json`.
- Day 6B S2 B1b 0.901421/0.896658, AUPRC 0.453843/0.491193, F1
  0.506329/0.506329; S1 B1b 0.830741 ← `results/day6b/metrics.json`.
- B2 0.370398–0.434230 (range "0.37–0.45" ✓).
- C0 AUROC 0.376199/0.366609 (S1), 0.323319/0.306531 (S2) ←
  `original_vs_masked_metrics.csv`.
- C4 median 0.0934 s, 140/144 = 97.2 % ← `clean_transition_audit.csv`.
- Population retention range 0.933–1.000 ← corrected
  `speech_mask_population_audit.csv`.
No number in WEEK1_REPORT contradicts a frozen artifact.

## 6. Week-1 figures — PASS

`results/week1/figures/` (5 figures) visually inspected:
- GT bands plotted on the seconds time axis (no re-introduction of the
  Day 6C index-axis bug); 02 confirmed GT at 13.75–14.50 s for
  paircase_0001, 05 shows the 0.75 s narrow band.
- Negative (01 Day-6A anti-correlation, 05 duration limitation) and
  positive (02) cases both present; 03 shows the C0 control contrast.
- B3 appears only with "ORACLE / DIAGNOSTIC, not deployable" annotation
  and is not mixed into deployable claims.

## 7. Reproduction entry — PASS

`--verify-only` executed read-only in this review: 696 frozen hashes
checked, zero missing, zero mismatches, `"passed": true` (groups: raw
sources 480, Day 3–4.5 outputs, Day 5 13, Day 6A 16, Day 6B 15, Day 6C 17,
C0 audio 46). No data modified, no model download. `--reproduce-core` was
not re-executed in this review (it was Codex's recorded run; the entry,
flags and temporary-directory semantics were inspected in
`experiments/week1_baseline/run.py` and `results/week1/run.log`).

## 8. pytest

Full suite re-run in this review: **169 passed / 0 failed** (88.8 s),
matching the Codex closeout.

## 9. Issues found

None blocking. One bookkeeping observation: the Day-6C correction flow
also updated the `speech_mask_population_audit.csv` entry inside my
`day6c_final_hashes.json` to the corrected hash (disclosed in
WEEK1_FREEZE; independently re-verified above). Reviewers comparing against
pre-correction hashes should use the before/after pair in §4.

## 10. Verdict

**CONTINUITY REVIEW PASS.** The Codex Week-1 closeout accurately reflects
the Day 5–Day 6C work actually executed, preserves the Day 6A negative
result and all claim boundaries, and its single audit fix (population
mixed counting) is correctly scoped, disclosed, and non-consequential to
the scientific conclusions.
