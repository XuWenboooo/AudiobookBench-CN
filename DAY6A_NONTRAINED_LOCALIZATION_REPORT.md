# Day 6A Non-Trained Localization Baseline Report

> **Restoration note (2026-09-05):** the original report file was found
> overwritten with unrelated plain text before Day 6B started. This file is
> the restored original report (identical content and numbers); during
> restoration two claim wordings were corrected per the Day 6B review item
> (§6 "significantly below 0.5" → "all observed AUROC values are below 0.5";
> §7 "structural" → the training-split formulation). No numeric value or
> result was changed; all numbers remain reproducible from
> `results/day6a/metrics.json` and the frozen Day 6A outputs.

Date: 2026-09-05
Config (frozen before evaluation): `configs/day6a_localization_baseline.yaml`
Scope: temporal aggregation + non-trained anomaly scoring + localization
sanity evaluation. **No MLP/RF/CNN/Transformer, no supervised classifier, no
learned detector, no hyperparameter search, no threshold tuning on test, no
unseen-generator claims, no A2 TTS, no speaker-embedding substitute, and no
Day 6B / Day 7 work was performed.** No frozen artifact was modified.

## 1. Executive Summary

Day 6A established the first evaluation layer on top of the frozen Day 5
signals: all **70 waveforms** (24 clean + 23 A0 + 23 A1) were aggregated
onto three pre-declared window scales (100/250/500 ms, **35,826 windows**
total), a robust reference was estimated from **TRAIN CLEAN windows only**,
and every window was scored with the B0 non-trained robust z-score under
three pre-declared ablation sets (ALL / NO_PAUSE / NO_ENERGY), plus
feature-specific channel scores.

**Main scientific finding (negative, reported honestly): the B0 baseline
fails to localize A0/A1 manipulation.** Window-level AUROC is below 0.5 in
every split × variant × scale × ablation combination (range 0.25–0.43).
The zone audit shows the mechanism: anomaly scores are highest on OUTSIDE
windows (driven by constructed 0.3 s gaps and natural content variation in
the clean context) and *lowest* inside the attack core — the spliced donor
speech is real human speech whose frame statistics sit closer to the
train-clean median than its own surrounding context does. This is the
opposite of a boundary shortcut: the baseline responds to the construction
protocol and context, not to the manipulation.

Gate: **DAY 6A ENGINEERING = PASS** (pipeline correctness gate — §20). A
negative detection result with a correct, reproducible pipeline passes this
gate by definition; the result must not be packaged as localization success.

## 2. Data (read-only)

| Variant | Records | Split coverage |
|---|---:|---|
| clean | 24 | train 12, val 6, test 6 |
| A0 `cross_speaker_splice` | 23 | train 11, val 6, test 6 |
| A1 `artifact_controlled_cross_speaker_splice` | 23 | train 11, val 6, test 6 |

- Decoded duration: 30.2056 – 34.8501 s per record; 2247.09 s total.
- One clean sequence (`day45_train_SSB0009_seq001`) has no paired case by
  frozen Day 4.5 design (whole-case skip); it is still grid-processed as a
  clean record.

## 3. Unified Temporal Grid

| Parameter | Value |
|---|---|
| frame length | 400 samples = 25 ms @ 16 kHz |
| hop length | 160 samples = 10 ms @ 16 kHz |
| frames | complete frames only: `1 + (N - 400) // 160` |
| trailing coverage gap | always < 10 ms (validated per record) |
| frames per record | 3019 – 3483 |
| frames total | **224,566** (clean 77,054 / A0 73,756 / A1 73,756) |

All timestamps derive from integer samples (`seconds = samples / 16000`).
Frame counts by split: train 109,756 / val 58,167 / test 56,643.

## 4. Frame Features (engineering contract)

| Column | Definition |
|---|---|
| `energy` | mean square power `mean(x^2)` of the 400-sample frame |
| `log_energy` | `10*log10(energy + 1e-12)` dB re full scale |
| `rms` | `sqrt(energy)` |
| `f0_hz` | F0 at the frame center; **NaN = unvoiced** (never imputed) |
| `voiced_ratio` | frame-level indicator in {0, 1}: F0 finite and in [75, 500] Hz |
| `pause_ratio` | frame-level indicator in {0, 1}: `20*log10(rms+1e-12) < -45 dBFS` |
| `overlap_*` / `in_*` | per-frame overlap with target/attack/core/blend |

Ground truth comes verbatim from the frozen Day 4.5 manifest. A0 core ==
target (crossfade 0); A1 core == target shrunk by 400-sample crossfades —
both re-validated per record.

Sequence-level aggregates (70 rows): voiced ratio 0.411–0.615 (mean 0.547),
pause ratio 0.261–0.480 (mean 0.360), sequence F0 mean 114.8–253.4 Hz.
Per-variant voiced means: clean 0.5511, A0 0.5377, A1 0.5512 — reported
only as sanity context, not findings.

### 4.1 F0 backends

- Primary: Praat autocorrelation (`to_pitch_ac`, 10 ms step aligned to the
  hop, 75–500 Hz), evaluated at each frame center.
- Fallback (implemented + unit-tested, not needed): deterministic NumPy
  normalized autocorrelation with 0.30 peak threshold; unvoiced stays NaN.
- Tonight: `parselmouth_to_pitch_ac` = 70/70 records, zero fallbacks.

### 4.2 Speaker embedding: BLOCKED

**Status: BLOCKED.** No embedding backend existed and, per user decision, no
backend was installed in Day 5. **No fake embedding was generated.**

## 5. Validation Results

- Record-level validation: **70/70 PASS** (frame count, bounds monotonicity,
  sub-hop trailing coverage, sample↔second consistency, GT interval bounds,
  A0/A1 interval identities, feature finiteness, probe/decode agreement).
- Pair validation: **23/23 PASS** (shared clean sequence, donor crop, target
  bounds; identical sample counts and rates).

## 6. Debug Trajectory Figures

`results/day5_debug_figures/`, 5 deterministic pairs
(paircase_0004/0007/0009/0013/0017, seed 20260904). Visual spot check:
frame-level `|manipulated − clean|` energy deviation is exactly zero outside
the target band — the plotted equivalent of `outside_equal`.

## 7. Regression Tests

Day 5 added 26 tests (`tests/test_day5_temporal.py`); full suite at Day 5
close: **76 passed, 0 failed**.

## 8. Design Notes & Known Limitations (recorded, not acted on)

1. **log_energy floor**: digital silence gets the epsilon floor −120 dB.
2. **Pause threshold is absolute** (−45 dBFS) and couples to recording gain.
3. **`voiced_ratio`/`pause_ratio` are frame-level 0/1**; only sequence-level
   aggregates are true ratios.
4. **Single-point F0 sampling** at the frame center of a 25 ms window.
5. **Constructed-gap confound**: fixed 0.3 s zero-silence gaps contribute to
   `pause_ratio` independent of natural pausing.
6. **Core vs blend semantics**: A1 core excludes the 400-sample crossfades;
   frame labels expose all four intervals so later work can choose
   full-region vs strict-core without re-extraction.
7. **Embedding gap**: the embedding slot is intentionally empty (BLOCKED).

## 9. Artifacts

`DAY5_PRECHECK.md`, `DAY5_TEMPORAL_SIGNAL_REPORT.md`,
`results/day5_validation/` (pre-check JSON, three frame-metadata CSVs with
224,566 rows, sequence summary, record validation, pair alignment, pipeline
summary), `results/day5_debug_figures/` (5 PNGs).

## 10. Day 5 Gate

**DAY 5 ENGINEERING PREPARATION = PASS.**

---

# Day 6A Report (below) — non-trained localization baseline

## 1. Executive Summary

All 70 waveforms were aggregated onto three pre-declared scales
(100/250/500 ms; 35,826 windows), a robust reference was estimated from
TRAIN CLEAN windows only, and B0 robust z-scores were computed under three
pre-declared ablations.

**Main scientific finding (negative): B0 fails to localize A0/A1.** All
observed window-level AUROC values are below 0.5 (range 0.25–0.43) across
every split × variant × scale × ablation. High anomaly concentrates on
OUTSIDE windows (constructed gaps + content variation), while the spliced
donor core sits *closer* to the train-clean median than its own context.
**DAY 6A GATE = PASS** (pipeline correctness; the detection result is
negative and must be quoted as such).

## 2. Input Data

Read-only: 70 frozen Day 4.5 WAVs, 224,566 frozen Day 5 frames, the Day 4.5
attack manifest, and output-audio hashes. Speaker embedding: still BLOCKED.

## 3. Aggregation Protocol

| Scale | Window | Hop | Windows total |
|---|---|---|---:|
| 100 ms | 10 Day-5 frames | 10 frames | 22,424 |
| 250 ms | 25 frames | 25 frames | 8,945 |
| 500 ms | 50 frames | 50 frames | 4,457 |

Non-overlapping, aligned to complete Day 5 frames; shared grid across
clean/A0/A1 of a pair. Window features (11): log_energy mean/std/min/max,
rms mean/std, f0 nanmedian/nanstd (voiced only) + finite fraction,
voiced_fraction, pause_fraction, valid_f0_fraction.

## 4. Train-clean Reference

median / MAD (+ eps) per feature from train-clean windows only
(n = 3,872 / 1,545 / 770). Zero-scale protection (amended after the first
run, disclosed): a feature with train-clean MAD exactly 0 is degenerate
(pause_fraction at 100 ms), z-scores forced NaN and excluded; defensive cap
z ≤ 10,000.

## 5. Anomaly Score Definition

`z_f(t) = |x − median| / (MAD + eps)`; `A(t)` = mean of valid z over the
ablation set; per-channel scores A_f0/A_energy/A_rms/A_voicing/A_pause kept
separately; equal weights, nothing learned; <1 valid feature ⇒ NaN.

## 6. Multi-scale Results

Test, ALL ablation, AUROC / AUPRC (full GT):

| Scale | A0 | A1 |
|---|---|---|
| 100 ms | 0.379 / 0.038 | 0.378 / 0.037 |
| 250 ms | 0.331 / 0.035 | 0.350 / 0.036 |
| 500 ms | 0.324 / 0.038 | 0.346 / 0.039 |

All observed AUROC values are below 0.5, i.e. the score anti-correlates with
manipulation. No scale is recommended; the full matrix is in `metrics.json`.

## 7. Train / Val / Test Results

250 ms ALL, GT full, AUROC: train A0 0.359 / A1 0.365; val A0 0.427 /
A1 0.327; test A0 0.331 / A1 0.350. The failure is already present on the
training split and therefore cannot be explained by held-out distribution
shift alone. F1 at the train-derived threshold ≈ 0.09–0.10; at fixed
|z| ≥ 3.5, F1 = 0.00.

## 8. A0 vs A1 Results

Reported separately everywhere; differences are small and split-inconsistent.
No variant-ordering claim.

## 9. Full-region vs Core Results

Nearly identical (e.g. 250 ms test A0: 0.331 vs 0.331). With no usable
signal, the full-vs-core contrast carries no information at this stage.

## 10. Pause Ablation

ALL vs NO_PAUSE (test, full): 0.331→0.330 (A0), 0.350→0.343 (A1) — the
failure does not depend on the fixed-gap pause shortcut.

## 11. Energy Ablation

ALL vs NO_ENERGY (test, full): 0.331→0.345 (A0), 0.350→0.366 (A1) — removing
energy slightly improves the (still failing) score; energy contributes a mild
anti-correlation. Pre-declared ablations; no feature selection.

## 12. Boundary Shortcut Audit

Zone means/medians (test, ALL): outside 2.235/1.379; boundary 1.411/1.519
(n=7); core 1.164/1.038 (A0; A1 similar). **The anomaly concentrates on
outside windows, not at the boundary and not in the core.** Channel medians:
energy 1.14 outside vs 0.70 core; rms 1.15 vs 0.67; voicing 1.00 vs 0.50;
f0 ≈ equal; pause ≈ 1.0 both. Mechanism: the donor core is continuous real
speech, closer to the train-clean median than its heterogeneous context.

## 13. Paired A0/A1 Analysis

Paired Δ core anomaly (A1 − A0): mean −0.019, median +0.014, A1 < A0 in
11/23 cases — a coin flip. B0 is insensitive to the artifact controls; this
says nothing about perceptual realism.

## 14. Failure Cases

33 deterministic rows (top clean false positives = constructed-gap windows,
lowest case AUROC, boundary/core asymmetry, A0-success/A1-failure). Nothing
removed.

## 15. Figures

5 paired-case localization figures, deterministic selection; visible spikes
on constructed gaps outside the GT band, low scores inside it.

## 16. Reproducibility

Full pipeline run twice; `anomaly_scores.csv`, `aggregated_features.csv`,
`paired_analysis.csv`, `metrics.json` byte-identical across runs. Config
copy equals repo config. Day 3/3.5/4/4.5 hashes and Day 5 outputs re-verified
unchanged. The zero-scale amendment is disclosed in §4 and frozen in config.

## 17. Tests

29 new tests in `tests/test_day6a_baseline.py`; full suite **105 passed**.

## 18. Research Integrity

Non-trained baseline; anomaly score ≠ learned detector; constructed ≠ native
audiobook; A0/A1 different-text confound; speaker embedding not implemented;
A2 PENDING; 16 kHz condition; fixed 0.3 s gaps may constitute a pause
shortcut; below-random AUROC must not be inverted into a "detector" claim.

## 19. Limitations

Equal-weight robust z on 11 features is deliberately weak; no embedding
channel; F0 window-sparse at 100 ms; val/test have only 6 cases; boundary
windows rare (5–10); majority-rule labels are one convention; constructed
gap windows contaminate the anomaly distribution.

## 20. Day 6A Gate

All 13 pipeline-correctness requirements PASS.
**DAY 6A NON-TRAINED LOCALIZATION BASELINE = PASS** (correctness only; the
detection result is negative).

## 21. Recommendation for Day 6B

(Recommendation only; Day 6B was not started in Day 6A.)

1. Do not scale up B0 — the failure mechanism defeats frame-statistics z.
2. Priority 1: un-block the speaker-embedding channel; a speaker
   discontinuity at the target boundary is the strongest available cue for a
   cross-speaker splice.
3. Priority 2: within-sequence contrast (paired clean differential) to
   remove the content confound.
4. Priority 3: sample-level boundary-transient measure.
5. Keep dual GT, zone audit, ablation discipline and paired reporting as
   standing infrastructure.
