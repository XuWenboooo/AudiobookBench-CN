# A2 Required Test Map — pre-implementation

Consolidated, de-duplicated test plan derived from
`A2_STATIC_COMPATIBILITY_AUDIT.md` (F-ids), `WEEK2_DAY11_EVAL_DRY_AUDIT.md`
(§3) and `WEEK2_A2_LEAKAGE_SHORTCUT_AUDIT.md`. Every test must exist and
pass **before** any A2 metric is treated as quotable (Day-11 gate).
Tests use synthetic dummy arrays unless marked DATA (real frozen data).

| # | Test name | Covers (findings) | Type | Asserts |
|---|---|---|---|---|
| 1 | test_a2_dual_timeline_gt | GT (protocol §6) | DATA+unit | prefix bit-equal; suffix == clean+delta; core == scaled synthetic; both blends match frozen formula; exact final length; half-open bounds |
| 2 | test_a2_variable_length_windows | F9, F17, Day11 | unit | window count/bounds correct for N_syn < N_real, ==, > |
| 3 | test_a2_case_grouping_unequal_counts | F13, Day11 | unit | bootstrap/case grouping with unequal per-case window counts |
| 4 | test_a2_mask_alignment | F12, Day11 | unit | mask length == embedding-derived window count |
| 5 | test_b3_forbidden_in_a2_primary | F5, Day11 | unit | A2 evaluation refuses B3 rows in primary tables (denylist) |
| 6 | test_a2_b3_skipped | F5 | unit | A2 pipeline completes with B3 absent/NaN, no abort |
| 7 | test_a2_figure_time_axis | F1, Day11 | unit/visual | clean trajectory clipped at attack start on manipulated timeline; bands on seconds axis |
| 8 | test_a2_detector_input_denylist | leakage §1/2/6, Day11 | unit | scoring input exposes only the suspect waveform; reference/GT/generator/QA fields raise |
| 9 | test_a2_threshold_reuse_frozen | F4, Day11, leakage §5 | unit | loaded thresholds == Week-1 frozen values from metrics_by_split.csv |
| 10 | test_a2_loader_reads_sidecar | F3 | DATA | A2 records load identity/timelines/GT purely from sidecar |
| 11 | test_a2_record_id_roundtrip | F2, leakage §14 | unit | A2 id convention parses; renamed files do not change labels |
| 12 | test_a2_variant_lookup | F10 | unit | A2 records resolvable by variant+case |
| 13 | test_a2_tier_fields_absent_ok | F6, F16 | unit | evaluation completes without duration_tier fields |
| 14 | test_a2_mask_fractions_present | F7 | DATA | every A2 record gets speech-active fractions via own waveform |
| 15 | test_a2_b4_frames_recomputed | F8 | unit | B4 works from recomputed A2 frame energies |
| 16 | test_a2_exact_lengths_from_sidecar | F9 | unit | evaluation prefers sidecar final_synthetic_num_samples |
| 17 | test_a2_blend_in_out_projection | F15 | unit | blend_in/out recorded; full/core labels unchanged |
| 18 | test_a2_prefix_null_control | F14, leakage §8 | DATA+unit | pre-attack-window B1 control computable and ≈ clean baseline |
| 19 | test_a2_silence_distribution_shift_report | leakage §11 | DATA | pause-feature shift between removed-real and inserted-synthetic reported as DIAGNOSTIC |
| 20 | test_a2_outside_anomaly_vs_a0_control | leakage §12 | DATA | A2-vs-A0 outside-anomaly comparison produced (construction-interaction disclosure) |
| 21 | test_a2_gt_axis_bounds | GT audit class | unit | all A2 GT intervals: start ≥ 0, end ≤ manipulated length, seconds consistent |

Notes:
- Tests 1–13 are pure unit tests (no TTS, no data).
- Tests 14–18, 20–21 run against frozen A2 outputs once they exist
  (DATA); they must be committed and passing before Day-11 numbers are
  quoted.
- Test 19 may be satisfied by the Day-12 DIAGNOSTIC report if the ASR
  backend is explicitly omitted.
- None of these tests modifies protocol semantics; all implement checks
  already required by the frozen config and the pre-registration suite.
