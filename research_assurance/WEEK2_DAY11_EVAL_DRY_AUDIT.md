# WEEK 2 — DAY 11 EVALUATION DRY AUDIT (read-only; no A2 metrics executed)

Question: which Week-1 evaluation components can be reused verbatim for the
variable-duration A2 pilot, and what breaks? This is a design-time dry
audit against the frozen Week-1 code; no A2 metric is computed here.

## 1. Baseline-by-baseline reusability

| Baseline | Reusable for A2? | Notes |
|---|---|---|
| B0 (Day-6A global robust-z) | YES, with one caveat | Its 25 ms/10 ms grid and train-clean reference are duration-agnostic; the Day-6A reference came from **Week-1 clean sequences** — A2 clean is the same construction family, so reuse is protocol-consistent. Caveat: A2 windows sit on the **manipulated** timeline; the A2 manipulated sequence has a different length than clean (suffix shift), so B0 window↔GT projection must use the A2 manipulated grid (same code path as A0/A1, new manifest rows). |
| B1a (untrimmed self-prototype) | YES unchanged | Sequence-local by construction: prototype from the suspect sequence's own windows. Variable duration only changes the window count. No enrollment, no clean pair. |
| B1b (20 % trimmed) | YES unchanged | Same as B1a; trim rule is count-relative, duration-independent. |
| B2 (adjacent/symmetric neighbor) | YES unchanged | Purely local; variable length harmless. |
| B4 (boundary transient) | YES as DIAGNOSTIC ONLY | Needs the Day-5-style frame grid of the **A2 manipulated** waveform (recompute log-energy frames on the new audio; do not reuse Week-1 frame rows). |
| **B3 (paired-clean oracle)** | **FORBIDDEN for primary A2 evaluation** | A2's dual timeline has a suffix shift: after the attack, clean and manipulated samples diverge by `duration_delta`, so a same-grid `1 − cos(emb_manip(t), emb_clean(t))` is **undefined beyond the attack** without interpolation — and the frozen protocol explicitly bans `b3_same_grid` and clean-embedding interpolation. B3 may appear only as a clearly-marked ORACLE diagnostic **restricted to the common prefix region** if ever computed; it must not enter any headline table. |

## 2. Variable-duration impact analysis (the core of this audit)

A2's manipulated sequence length = clean length + `duration_delta_samples`
(delta ≠ 0 in general; sign and magnitude vary per case). Consequences:

### 2.1 Window labeling / GT projection — SAFE with new inputs
`build_speaker_windows` derives windows from the manipulated sample count;
`project_ground_truth_speaker` consumes A2 manifest bounds
(`attack_start = c0`, `attack_end = c0 + N_syn`, core ± 400). The existing
functions are duration-agnostic. **Required new input**: the A2 sidecar
replacing the Week-1 manifest row. Risk: LOW.

### 2.2 Case grouping / bootstrap unit — SAFE
A2 cases inherit `paired_case_id`; `case_bootstrap_ci` groups by that id
and never assumes equal lengths across cases. **Required new test**: a
grouping test with unequal per-case window counts. Risk: LOW.

### 2.3 Speech-active masking — SAFE with one alignment rule
The label-agnostic −45 dBFS rule is recomputed on the A2 manipulated
waveform (exactly the C0 path already implemented). The mask array length
must be truncated/aligned to the window count derived from the embedding
count (same rule as Day 6C). Risk: LOW; needs a test.

### 2.4 Threshold reuse — SAFE but interpretability caveat
Week-1 train-only thresholds (`results/day6a|day6b/metrics_by_split.csv`)
are frozen and reused per config (`thresholds: reuse_week1_only`). F1 under
a threshold fitted on Week-1 short attacks is only weakly comparable for
A2's longer attacks — the frozen rule avoids tuning but weakens F1
interpretation. AUPRC (threshold-free, config-required) is therefore the
primary conditional comparison. Risk: MEDIUM (interpretation, not
correctness).

### 2.5 Plot alignment — NEEDS CODE CARE
Day-6C figure code derived the x axis from window centers of a **single**
record and overlaid paired variants of equal length. For A2, clean and
manipulated timelines diverge after the attack; any figure overlaying
clean and A2 trajectories must either plot on the **manipulated timeline**
with a clean-trajectory cut at the attack, or use dual aligned axes.
Misalignment here is a figure-only bug class (cf. the Day-6C index-axis
incident). Risk: MEDIUM — pre-register the convention: **A2 figures plot
the manipulated timeline; the clean trajectory is drawn only up to the
attack start.**

### 2.6 Peak-error definition — SAFE with GT on the manipulated timeline
`peak_localization_error_seconds = |argmax-window center − strict-core
center|` where both centers are computed on the **manipulated** grid from
A2 GT rows. Definition unchanged. Risk: LOW.

### 2.7 Core/full distinction — SAFE
A2 GT already provides full (includes both 400-sample blends) vs strict
core (excludes them); `blend_in`/`blend_out` add finer zones. The
majority-rule 0.5 labeling is reused frozen. Risk: LOW.

### 2.8 Duration-ratio shortcut risk (new in A2)
Unlike Week 1, A2 duration is **outcome-carrying**: `duration_delta` could
in principle correlate with manipulation (e.g. TTS systematically shorter).
The evaluation must therefore report duration-ratio distributions per
split and never use duration as a feature. Diagnostic only (Day-12
variable #4). Risk: MEDIUM (analysis-design risk, mitigated by
pre-registration).

## 3. Required new tests (before any A2 metric runs)

1. `test_a2_dual_timeline_gt` — suffix-shift lineage: prefix equal, suffix
   equals clean+delta, core equals scaled synthetic, blends match the
   frozen formula (mirror of the generator's own verification, evaluated
   independently).
2. `test_a2_variable_length_windows` — window count/bounds for three
   synthetic lengths (N_syn < N_real, =, >).
3. `test_a2_case_grouping_unequal_counts` — bootstrap grouping with
   unequal per-case window counts.
4. `test_a2_mask_alignment` — mask length aligned to embedding-derived
   window count for A2 records.
5. `test_b3_forbidden_in_a2_primary` — A2 evaluation refuses B3 rows in
   primary tables (config denylist assertion).
6. `test_a2_figure_time_axis` — figure helper plots on the manipulated
   timeline and clips the clean trajectory at the attack start
   (regression test for the Day-6C axis-bug class).
7. `test_a2_detector_input_denylist` — evaluation loader raises if any
   FORBIDDEN sidecar field is reachable from the detector input path.
8. `test_a2_threshold_reuse_frozen` — A2 evaluation asserts the loaded
   thresholds equal the Week-1 frozen values.

## 4. Explicit non-goals of Day 11

No A2 metric execution; no detector/threshold changes; no new baselines;
no B3 in primary tables; no population redefinition beyond the frozen
mask; no result peeking of any kind.
