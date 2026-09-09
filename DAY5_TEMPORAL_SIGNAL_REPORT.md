# Day 5 Temporal Signal Report (Engineering Version)

Date: 2026-09-04 (evening run, ~7 h budget)
Scope: **engineering preparation only.** No detector, classifier, localizer,
AUROC, EER, TTS run, or Day 6 work was performed anywhere in this session.
No data protocol, manifest, config, or frozen artifact was modified.

## 1. Executive Summary

Day 5 established the unified temporal representation for the frozen Day 4.5
expanded paired pilot: all **70 waveforms** (24 clean + 23 A0 + 23 A1) were
decoded onto one shared 25 ms/10 ms frame grid, producing **224,566 frames**
of metadata with per-frame energy, log-energy, RMS, F0, voicing and pause
indicators, and per-frame overlap fractions against all four ground-truth
intervals (target / attack / core / blend).

- Pre-check gate (hashes, freeze, manifest, pytest): **PASS**
- Record-level validation: **70/70 PASS**
- Paired alignment validation: **23/23 PASS**
- F0 backend: `praat-parselmouth` used for **70/70** records (no fallback
  needed; fallback implemented and unit-tested anyway)
- Speaker embedding: **BLOCKED** (by user decision; nothing fabricated)
- Debug figures: **5/5** paired cases rendered
- Test suite: **76 passed** (50 prior + 26 new; target was 60+)

Gate: **DAY 5 ENGINEERING = PASS.**

## 2. Data (read-only)

| Variant | Records | Split coverage |
|---|---:|---|
| clean | 24 | train 12, val 6, test 6 |
| A0 `cross_speaker_splice` | 23 | train 11, val 6, test 6 |
| A1 `artifact_controlled_cross_speaker_splice` | 23 | train 11, val 6, test 6 |

- Decoded duration: 30.2056 – 34.8501 s per record; 2247.09 s total.
- One clean sequence (`day45_train_SSB0009_seq001`) has no paired case by
  frozen Day 4.5 design (whole-case skip); it is still grid-processed here as
  a clean record.

## 3. Unified Temporal Grid

Frozen for all records (`src/audiobookbench/temporal/grid.py`):

| Parameter | Value |
|---|---|
| frame length | 400 samples = 25 ms @ 16 kHz |
| hop length | 160 samples = 10 ms @ 16 kHz |
| frames | complete frames only: `1 + (N - 400) // 160` |
| trailing coverage gap | always < 10 ms (validated per record) |
| frames per record | 3019 – 3483 |
| frames total | **224,566** (clean 77,054 / A0 73,756 / A1 73,756) |

All timestamps are derived from integer samples (`seconds = samples / 16000`);
seconds are never stored as independent quantities. Frame counts by split:
train 109,756 / val 58,167 / test 56,643.

## 4. Frame Features (engineering contract)

Defined in `src/audiobookbench/temporal/frame_features.py`; one row per frame
in `results/day5_validation/day5_frame_metadata_{clean,a0,a1}.csv`.

| Column | Definition |
|---|---|
| `energy` | mean square power `mean(x^2)` of the 400-sample frame |
| `log_energy` | `10*log10(energy + 1e-12)` dB re full scale |
| `rms` | `sqrt(energy)` |
| `f0_hz` | F0 at the frame center; **NaN = unvoiced** (never imputed) |
| `voiced_ratio` | frame-level indicator in {0, 1}: F0 finite and in [75, 500] Hz |
| `pause_ratio` | frame-level indicator in {0, 1}: `20*log10(rms+1e-12) < -45 dBFS` |
| `overlap_target/attack/core/blend` | fraction of the frame covered by each GT interval |
| `in_target/attack/core/blend` | discrete label: full / partial / none |

Ground-truth intervals come verbatim from the frozen Day 4.5 manifest
(`target_*_sample`, `attack_*_sample`, `attack_core_*_sample`,
`blend_*_sample`, `crossfade_samples`). A0 core == target (crossfade 0);
A1 core == target shrunk by 400-sample crossfades on both edges — both were
re-validated per record tonight.

Sequence-level aggregates (70 rows, `day5_sequence_summary.csv`):
voiced ratio 0.411–0.615 (mean 0.547), pause ratio 0.261–0.480 (mean 0.360),
sequence F0 mean 114.8–253.4 Hz. Per-variant voiced means: clean 0.5511,
A0 0.5377, A1 0.5512 — A0/A1 differences are localized to attack regions by
construction, and these whole-sequence aggregates are reported only as
sanity context, not as findings.

### 4.1 F0 backends

- Primary: Praat autocorrelation (`Sound.to_pitch_ac`, time step 10 ms
  aligned to the grid hop, floor 75 Hz, ceiling 500 Hz), evaluated at each
  frame center via `get_value_at_time`.
- Fallback (implemented + unit-tested, not needed tonight): deterministic
  NumPy normalized-autocorrelation per frame with a 0.30 peak threshold;
  silent/unreliable frames stay NaN.
- Tonight: `parselmouth_to_pitch_ac` = 70/70 records, zero fallbacks.

### 4.2 Speaker embedding: BLOCKED

**Status: BLOCKED.** No speaker embedding backend exists in this environment
and, per user decision taken before the run, no backend was installed
tonight. **No fake/synthetic/random embedding was generated** — the six
signal features above are complete and the embedding slot is explicitly
empty. The BLOCKED record is written into
`results/day5_validation/day5_pipeline_summary.json`.

## 5. Validation Results

Per-record validator (`day5_record_validation.csv`): **70/70 passed**, checks:

1. frame metadata row count == grid expectation for decoded `N`;
2. frame bounds monotonic, exact, never out of waveform bounds;
3. trailing uncovered samples < one hop;
4. stored seconds == samples / 16000 (all eight GT second/sample pairs
   re-checked on manipulated records);
5. GT intervals inside sequence bounds; A0 attack==blend==core==target with
   zero crossfade; A1 core == target shrunk by recorded crossfade;
6. energy / log_energy / rms / voiced / pause finite on every frame;
   F0 Inf forbidden (NaN allowed as the unvoiced marker);
7. waveform fully finite; probe (frames, sr=16000, mono) == decoded ==
   manifest expectation.

Pair validator (`day5_pair_alignment.csv`): **23/23 passed** — A0 and A1 of
every case share clean sequence, split, donor source and donor crop, target
bounds, and both manipulated WAVs are sample-count and sample-rate identical
to their clean sequence.

Machine-readable copies: `day5_validation/day5_pipeline_summary.json`,
`day5_precheck.json`.

## 6. Debug Trajectory Figures

Deterministic sample (`random.Random(20260904)` over sorted case IDs):
**paircase_0004, 0007, 0009, 0013, 0017** — one figure each in
`results/day5_debug_figures/`, four panels per figure:

1. frame energy trajectories (clean vs A0 vs A1);
2. F0 trajectories (gaps are unvoiced frames, honestly NaN);
3. ground-truth bands (target/attack/core/blend) over the clean energy;
4. frame-level `|manipulated - clean|` energy deviation with the GT band.

Visual spot-check (e.g. `day5_debug_paircase_0013.png`): deviation is exactly
zero outside the target band and concentrated inside it — the plotted
equivalent of the `outside_equal` waveform check. F0 inside the band clearly
follows the donor speaker's register in both A0 and A1. These figures are
engineering debug artifacts only.

## 7. Regression Tests

New file `tests/test_day5_temporal.py`, 26 tests, none replacing an old test:

- grid: frame count/bounds, exact sample→second derivation, invalid-parameter
  rejection, sub-hop trailing coverage, framing-matrix shape (5)
- features: energy/RMS/log-energy mathematical consistency, parselmouth F0 on
  a 220 Hz sine, silence → pause + no fake F0, voicing bounds, pause
  threshold, autocorrelation fallback on a 200 Hz sine, simulated missing
  parselmouth → fallback backend reported, embedding stays BLOCKED (8)
- validation: overlap fraction cases, interval labels, overlap flags,
  consistent-record pass, timestamp corruption detection, non-finite feature
  detection, frozen-manifest GT re-validation (46 rows), corrupted-A0-core
  rejection, A1-crossfade-core enforcement, pair alignment + mismatch
  detection (10)
- figures + precheck helpers + identity parsing (3)

Full suite: **76 passed in 90.92 s; 0 failed** (target ≥ 60 met).

## 8. Design Notes & Known Limitations (recorded, not acted on)

Per the standing rule, no data protocol was changed. The following are
recorded for future discussion:

1. **log_energy floor.** Digital silence gets the epsilon floor
   `-120 dB` (= `10*log10(1e-12)`), not a physical measurement. Any future
   threshold near the floor must account for this.
2. **Pause threshold is absolute.** `-45 dBFS` is deterministic and testable,
   but it couples to recording gain. If a future dataset is normalized
   differently, the threshold must be re-calibrated and re-frozen.
3. **`voiced_ratio`/`pause_ratio` are frame-level 0/1.** Only sequence-level
   aggregates are true ratios. Column names keep the agreed feature names;
   value semantics are documented here and in the module docstring.
4. **Single-point F0 sampling.** F0 is read at the frame center of a 25 ms
   window; within-window pitch movement is not captured. Sufficient for
   engineering debug; a formal prosody study would need a finer protocol.
5. **Constructed-gap confound.** Fixed 0.3 s zero-silence gaps make part of
   `pause_ratio` an artifact of the construction protocol rather than natural
   pausing. Any future pause-based detector must control for this (already
   flagged in the Day 4.5 report as constructed ≠ native audiobook).
6. **Core vs blend semantics.** A1 `core` excludes the 400-sample crossfades;
   `attack` and `blend` cover the full target. Frame labels expose all four
   intervals so later localization work can choose full-region vs strict-core
   without re-extraction (per the Day 4.5 entry conditions).
7. **Embedding gap.** The embedding slot is intentionally empty (BLOCKED).
   Any future speaker-trajectory work must install a real backend; fabricating
   embeddings remains forbidden.

## 9. Artifacts

| Path | Content |
|---|---|
| `DAY5_PRECHECK.md` | pre-check report (this session) |
| `DAY5_TEMPORAL_SIGNAL_REPORT.md` | this report |
| `results/day5_validation/day5_precheck.json` | machine-readable pre-check |
| `results/day5_validation/day5_frame_metadata_clean.csv` | 77,054 frame rows |
| `results/day5_validation/day5_frame_metadata_a0.csv` | 73,756 frame rows |
| `results/day5_validation/day5_frame_metadata_a1.csv` | 73,756 frame rows |
| `results/day5_validation/day5_sequence_summary.csv` | 70 sequence aggregates |
| `results/day5_validation/day5_record_validation.csv` | 70 record validations |
| `results/day5_validation/day5_pair_alignment.csv` | 23 pair validations |
| `results/day5_validation/day5_pipeline_summary.json` | pipeline summary |
| `results/day5_debug_figures/day5_debug_paircase_*.png` | 5 debug figures |

New source modules: `temporal/grid.py`, `temporal/frame_features.py`,
`temporal/day5_validation.py`, `temporal/day5_figures.py`,
`temporal/day5_pipeline.py`, `security/day5_precheck.py`;
new tests: `tests/test_day5_temporal.py`.

## 10. Gate

**DAY 5 ENGINEERING PREPARATION = PASS.**
No Day 6 work, no model training, no detection/localization metric was
executed. The temporal representation is ready for future detector work under
the Day 4.5 entry conditions, pending the BLOCKED speaker-embedding decision.
