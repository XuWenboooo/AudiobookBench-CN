# A2 Variable-Duration Static Code Compatibility Audit

Scope: static analysis (READ-ONLY) of the Week-1 evaluation code that A2
will reuse — B0/B1a/B1b/B2/B3/B4, window labeling, GT projection, speech
mask, bootstrap, case grouping, figures, peak error, threshold handling —
against the frozen variable-duration A2 semantics
(`week2a-a2-v1.1-corrected`: natural synthetic duration, suffix shift,
dual timelines). Every line number below was taken from the current
repository state at audit time.

Legend — ASSUMPTION: the hidden equal-duration/same-timeline premise;
A2 FAILURE MODE: what happens if A2 data hits the code unchanged;
SEVERITY: HIGH / MEDIUM / LOW; every finding has a REQUIRED TEST and a
RECOMMENDED FIX (analysis only — nothing was modified). Protocol
amendment: **NO for all findings** (the corrected protocol already
specifies the right semantics; these are implementation gaps).

## Findings

### F1 — Clean-trajectory overlay assumes identical timelines (figure)
- FILE: `src/audiobookbench/temporal/day6c_pipeline.py`
- FUNCTION: `render_figures` → Figure A series loop
- LINE/REGION: 700 (`ax.plot(t[:len(vals)] …)`) and 626–630 (t from
  `rid_a0`'s windows); same pattern in Day6B `_render_case_figure`
  (day6b_pipeline.py:240, 695–705 region)
- ASSUMPTION: clean and manipulated sequences share one time axis; only
  count truncation (`t[:len(vals)]`) is handled.
- A2 FAILURE MODE: the clean trajectory is drawn on the manipulated time
  axis beyond the attack, where clean time ≠ manipulated time by
  `duration_delta` — visually wrong GT/trajectory alignment (same bug
  class as the historical index-axis incident).
- SEVERITY: **HIGH** (figure correctness)
- REQUIRED TEST: `test_a2_figure_time_axis` — clean trajectory clipped at
  the attack start on the manipulated timeline.
- RECOMMENDED FIX: plot clean only for `t < attack_start_seconds`; draw a
  visible timeline-split marker at the attack; never extend clean past it.
- PROTOCOL AMENDMENT: NO.

### F2 — Variant/record-id parsing by filename convention
- FILE: day6b_pipeline.py:90–91 (`_clean_id_of` via
  `split("_paircase_")[0]`); day6c_pipeline.py:691 (same pattern)
- ASSUMPTION: manipulated record ids always embed `_paircase_` and the
  clean id is the prefix.
- A2 FAILURE MODE: A2 ids (e.g. `..._a2_manipulated`) parse to the wrong
  or missing clean id → wrong/absent reference lookups, KeyErrors in
  figure/case code.
- SEVERITY: **MEDIUM–HIGH**
- REQUIRED TEST: `test_a2_record_id_roundtrip` — id parsing for the A2
  naming convention.
- RECOMMENDED FIX: resolve the clean id from the sidecar/manifest field,
  never from name parsing.
- PROTOCOL AMENDMENT: NO.

### F3 — Loaders are hard-bound to Week-1/C0 manifests
- FILE: day6b_embed.py:147 (`day45_attack_manifest.csv`);
  day6c_pipeline.py:74 (`day6c_same_speaker_control_manifest.csv`);
  day6b_pipeline.py:76 + day6c_pipeline.py:133
  (`day5_frame_metadata_*.csv`)
- ASSUMPTION: the only record sources are the Week-1/C0 manifests.
- A2 FAILURE MODE: no A2 loader exists — the pipeline cannot ingest A2
  records at all (implementation gap, not a wrong-output bug).
- SEVERITY: **MEDIUM** (required new loader)
- REQUIRED TEST: `test_a2_loader_reads_sidecar` — A2 records load with
  identity/timelines/GT purely from the A2 sidecar.
- RECOMMENDED FIX: generalize the record loader to accept the A2 sidecar
  manifest (additive; Week-1 paths untouched).
- PROTOCOL AMENDMENT: NO.

### F4 — Thresholds recomputed from current population vs frozen
      `reuse_week1_only`
- FILE: day6c_pipeline.py:303 (`def train_threshold`) and its call sites;
  day6b_pipeline.py (same train-only recomputation pattern)
- ASSUMPTION: recomputing the train-only max-F1 threshold on the current
  train population equals the frozen Week-1 threshold (true in Week 1
  because the population was Week-1 data).
- A2 FAILURE MODE: on A2, recomputation uses **A2 train windows**
  (synthetic audio) — violating the frozen protocol field
  `thresholds: reuse_week1_only` (frozen sources:
  `results/day6a|day6b/metrics_by_split.csv`). This is the audit's
  **central protocol-consistency finding**: not a calculation bug in Week
  1, but a code/protocol divergence that becomes live the moment A2 data
  flows through.
- SEVERITY: **HIGH**
- REQUIRED TEST: `test_a2_threshold_reuse_frozen` — the A2 evaluation
  loads thresholds from `results/day6b/metrics_by_split.csv` and asserts
  equality with the frozen values; recomputation path disabled for A2.
- RECOMMENDED FIX: add a frozen-threshold loader reading
  `metrics_by_split.csv`; keep the recomputation path only behind an
  explicit non-A2 flag.
- PROTOCOL AMENDMENT: NO (the protocol already mandates reuse).

### F5 — B3 crashes (rather than silently erring) on unequal grids
- FILE: day6b_scoring.py:91 (`if emb_manip.shape != emb_clean.shape:
  raise ValueError`)
- ASSUMPTION: paired clean/manipulated embeddings share the grid.
- A2 FAILURE MODE: correct protective behavior — A2's unequal lengths
  raise immediately; but the call site (day6b_pipeline.py:341,
  `scores["B3_ORACLE"] = b3_scores(...)`) is not variant-gated, so an
  A2 run through the Week-1 pipeline **aborts** instead of skipping B3.
- SEVERITY: **HIGH** (crash risk in the reused pipeline)
- REQUIRED TEST: `test_b3_forbidden_in_a2_primary` (denylist) +
  `test_a2_b3_skipped` — A2 rows carry B3 = NaN/absent without abort.
- RECOMMENDED FIX: gate B3 on the frozen denylist
  (`forbidden_baselines`) before the call; keep the shape guard as the
  second line of defense.
- PROTOCOL AMENDMENT: NO (denylist already frozen).

### F6 — `duration_tier` treated as a required manifest field
- FILE: day6c_pipeline.py:384, 466, 493, 500
      (`manifest_row["duration_tier"]`, `.replace("s", "")`)
- ASSUMPTION: every record carries a Week-1 duration tier; tier arithmetic
  (`win_s / float(tier)`) drives the resolution audit.
- A2 FAILURE MODE: A2 rows have no duration tier (forbidden metadata) →
  KeyError; the tier-stratified resolution audit is meaningless for A2.
- SEVERITY: **MEDIUM**
- REQUIRED TEST: `test_a2_tier_fields_absent_ok` — evaluation completes
  when `duration_tier` is missing (stratification section skipped /
  replaced by duration-ratio diagnostics per Day-12 S3).
- RECOMMENDED FIX: make tier handling conditional; for A2 report the
  duration-ratio distribution (already pre-registered) instead.
- PROTOCOL AMENDMENT: NO.

### F7 — Speech-active fractions: C0-only loader branch
- FILE: day6c_pipeline.py:159 (`for rid, rec in load_c0_records(repo_root).items()`)
- ASSUMPTION: records without Day-5 frames are exactly the C0 controls.
- A2 FAILURE MODE: A2 records fall outside both branches (no Day-5 frames,
  not in the C0 manifest) → empty fractions → mask IndexError (the exact
  crash class hit during Day-6C development).
- SEVERITY: **MEDIUM**
- REQUIRED TEST: `test_a2_mask_fractions_present` — every A2 record gets
  fractions via its own waveform under the frozen −45 dBFS rule.
- RECOMMENDED FIX: generalize the fallback to "any record without Day-5
  frames" (A2 sidecar supplies the audio path).
- PROTOCOL AMENDMENT: NO.

### F8 — B4 requires Day-5 frame rows that do not exist for A2
- FILE: day6b_pipeline.py:76 (`load_day5_log_energy`); day6c usage of
  `b4_scores` with Day-5 frame spans
- ASSUMPTION: every scored record has frozen Day-5 frame features.
- A2 FAILURE MODE: B4_DIAGNOSTIC impossible for A2 without recomputing the
  25 ms/10 ms frame grid on the A2 manipulated waveform.
- SEVERITY: **MEDIUM** (B4 is DIAGNOSTIC ONLY, so no primary impact)
- REQUIRED TEST: `test_a2_b4_frames_recomputed` — B4 works from
  freshly-computed A2 frame energies.
- RECOMMENDED FIX: compute A2 frames with the frozen Day-5 rule (same
  pattern as the C0 speech-mask fallback).
- PROTOCOL AMENDMENT: NO.

### F9 — Sample-count back-derivation from embedding count
- FILE: day6c_pipeline.py (`_num_samples_from_embeddings`)
- ASSUMPTION: `N = window + (count−1)·hop` recovers the true sample count.
- A2 FAILURE MODE: the estimate can differ from the true length by up to
  one hop; window bounds/GT seconds could drift by ≤ 0.25 s vs the exact
  sidecar values.
- SEVERITY: **LOW–MEDIUM**
- REQUIRED TEST: `test_a2_exact_lengths_from_sidecar` — A2 evaluation uses
  `final_synthetic_num_samples` from the sidecar when present.
- RECOMMENDED FIX: prefer sidecar `final_synthetic_num_samples`; keep the
  back-derivation only as fallback.
- PROTOCOL AMENDMENT: NO.

### F10 — `find()` / `_record_for_case` variant lookups
- FILE: day6c_pipeline.py:416, 674; day6b_pipeline.py `_record_for_case`
- ASSUMPTION: variant ∈ {clean, a0, a1, c0a, c0b} with Week-1 id shapes.
- A2 FAILURE MODE: lookups must learn the `a2` variant and its id
  convention; otherwise A2 cases silently drop out of paired analyses.
- SEVERITY: **LOW–MEDIUM**
- REQUIRED TEST: `test_a2_variant_lookup` — A2 records resolvable by
  variant+case.
- RECOMMENDED FIX: extend the variant registry; drive ids from the
  sidecar.
- PROTOCOL AMENDMENT: NO.

### F11 — Peak-error / case metrics on the manipulated timeline
- FILE: day6c_pipeline.py:526 (`core_center` via
  `windows_by_record[(name, rid)]`)
- ASSUMPTION CHECKED: windows for manipulated records already derive from
  the manipulated embedding count → the manipulated timeline. **SAFE for
  A2** provided the sidecar length (F9) is used.
- SEVERITY: — (no change needed beyond F9)
- REQUIRED TEST: covered by F9's test.
- PROTOCOL AMENDMENT: NO.

### F12 — Mask length alignment
- FILE: day6c_pipeline.py (`keep = (fra >= threshold)[:n_windows]`)
- ASSUMPTION CHECKED: alignment by truncation already implemented for the
  C0 path. **SAFE for A2** given F7's loader generalization.
- SEVERITY: —
- REQUIRED TEST: covered by `test_a2_mask_fractions_present` + existing
  alignment test.
- PROTOCOL AMENDMENT: NO.

### F13 — Bootstrap grouping with unequal counts
- FILE: day6b_scoring/day6c `case_bootstrap_ci`
- ASSUMPTION CHECKED: concatenation-based grouping does not require equal
  per-case window counts. **SAFE.**
- SEVERITY: —
- REQUIRED TEST: `test_a2_case_grouping_unequal_counts` (Day-11 list) to
  lock it.
- PROTOCOL AMENDMENT: NO.

### F14 — Clean-prefix null control not implementable today
- FILE: (absent) — required by WEEK2_A2_LEAKAGE_SHORTCUT_AUDIT.md item 8
- ASSUMPTION: none exists yet; the "pre-attack windows of A2 manipulated
  sequences must match clean behavior" control needs new code (a window
  split at the attack start + clean-reference comparison).
- A2 FAILURE MODE: the leakage audit's required null control cannot run.
- SEVERITY: **MEDIUM**
- REQUIRED TEST: `test_a2_prefix_null_control` — control metric computable
  and ≈ clean baseline on synthetic data.
- RECOMMENDED FIX: implement as a Day-11 evaluation option (analysis
  code only).
- PROTOCOL AMENDMENT: NO.

### F15 — GT projection inputs
- FILE: day6b_scoring.py `project_ground_truth_speaker` (duration-
  agnostic) — SAFE; the A2 gap is the input source (F3), not the
  projection math. Intervals must come from the A2 sidecar's
  full/core/blend-in/blend-out fields; `blend_in/out` fields are new
  relative to Week 1 and need an explicit projection decision (frozen
  protocol: full includes blends; core excludes them; blend-in/out are
  informational).
- SEVERITY: LOW
- REQUIRED TEST: `test_a2_blend_in_out_projection` — blend_in/out recorded,
  full/core labels unchanged by their introduction.
- PROTOCOL AMENDMENT: NO.

### F16 — Duration-tier ratio arithmetic
- FILE: day6c_pipeline.py:500 (`.replace("s","")`)
- ASSUMPTION: tier strings parse to seconds.
- A2 FAILURE MODE: same as F6; also the S2/0.75 s "ratio ≥ 1 ⇒ core
  unmeasurable" logic is Week-1-tier-specific and must not run for A2.
- SEVERITY: covered by F6.
- REQUIRED TEST: covered by F6.
- PROTOCOL AMENDMENT: NO.

### F17 — Intra-record `zip(windows, gt_rows)` usages
- FILE: day6b_pipeline.py:449; day6c_pipeline.py:526
- ASSUMPTION CHECKED: both iterables are built together per record, so
  lengths coincide by construction regardless of duration. **SAFE.**
- SEVERITY: —
- REQUIRED TEST: covered by the variable-length window tests (Day-11).
- PROTOCOL AMENDMENT: NO.

## Summary

| Severity | Findings |
|---|---|
| HIGH | F4 (threshold protocol divergence), F5 (B3 abort), F1 (figure timeline overlay) |
| MEDIUM | F2, F3, F6, F7, F8, F9, F10, F14 |
| LOW | F11, F12, F13, F15, F16, F17 (safe-with-tests) |

No finding constitutes a protocol contradiction: the corrected A2
semantics (variable duration, dual timelines, forbidden Week-1 bounds)
are implementable with the listed tests and localized fixes, none of
which require a protocol amendment.
