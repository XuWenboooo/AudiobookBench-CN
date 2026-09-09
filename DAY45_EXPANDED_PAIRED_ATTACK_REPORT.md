# Day 4.5 Expanded Paired Attack Report

## 1. Executive Summary

Day 4.5 built a new deterministic, speaker-disjoint AISHELL-3 pilot without
overwriting the original five-speaker pilot. It contains 12 speakers and 480
real utterances, split as train/val/test = 6/3/3 speakers. From these sources,
24 new 16 kHz mono constructed long-form clean sequences were generated.

Twenty-three clean sequences support one complete paired attack case each. A
paired case contains exactly one A0 direct splice and one A1 RMS-matched,
crossfaded splice using the same clean sequence, target interval, donor source,
donor crop, and replacement length. This produced 46 manipulated WAVs with
legal attacks in train, val, and test. One 2.5 s train case was skipped as a
whole because no internal utterance satisfied the fixed safety margins.

**DAY 4.5 EXPANDED PAIRED ATTACK GATE = PASS.** No detector, performance
experiment, TTS deployment, unseen-generator test, adaptive attack, or Day 5
work was performed.

## 2. Expanded Speaker Selection

Selection is frozen in `configs/day45_expanded_paired.yaml`. The rule preserves
the original five Day 3 speakers in their existing pilot splits, then fills
seven predeclared metadata slots with the lexicographically first eligible
speaker. Eligibility requires at least 40 rows having a real WAV, transcript,
and speaker metadata. It does not inspect decoded waveform quality, VAD, RMS,
manual listening, attack success, or any model result.

| Split | Speaker | Age group | Gender | Accent |
|---|---|---|---|---|
| train | SSB0005 | B | female | north |
| train | SSB0009 | B | female | south |
| train | SSB0011 | C | female | north |
| train | SSB0261 | C | male | north |
| train | SSB0309 | D | female | north |
| train | SSB0393 | A | female | north |
| val | SSB0073 | B | male | north |
| val | SSB0197 | C | female | south |
| val | SSB0434 | D | male | north |
| test | SSB0139 | B | male | south |
| test | SSB0342 | B | female | others |
| test | SSB1100 | C | male | south |

Speakers are disjoint across splits. The split was frozen before text-overlap,
attack-placement, donor-availability, or diagnostic results were observed.

## 3. Expanded Pilot Statistics

- Speakers: 12 (train 6, val 3, test 3)
- Utterances: 480, exactly 40 per speaker
- Split utterances: train 240, val 120, test 120
- Gender: 7 female speakers / 5 male speakers (280/200 utterances)
- Accent: 7 north / 4 south / 1 others speakers (280/160/40 utterances)
- Age group: A/B/C/D = 1/5/4/2 speakers (40/200/160/80 utterances)
- Original corpus partitions among selected utterances: train 467, test 13
- Missing selected WAV/transcript/metadata rows: 0

`data/manifests/day45_source_audio.csv` records absolute and portable paths,
original corpus partition, transcript provenance, speaker metadata, canonical
clean lineage, selection rank, and the new experimental split. Original
AISHELL-3 remained read only; 480/480 selected WAV hashes were unchanged.

## 4. Text Overlap Audit

The Day 3.5 normalization was reused exactly: Unicode NFC plus leading/trailing
whitespace stripping, without semantic, punctuation, or paraphrase matching.

| Exact normalized overlap | Count |
|---|---:|
| train ∩ val | 0 |
| train ∩ test | 0 |
| val ∩ test | 0 |
| train ∩ val ∩ test | 0 |

The complete deterministic 480-text audit is stored in
`data/reports/day45_text_overlap_audit.csv`. No split was changed after seeing
these results. Zero exact overlap in this pilot does not imply semantic or
paraphrase disjointness.

## 5. Expanded Constructed Long-form

The existing Day 3.5 construction protocol was reused with only a new
`day45` sequence-ID prefix and new output paths. Each sequence contains ordered,
complete utterances from one speaker and one split, resampled to 16 kHz mono,
with fixed 0.3 s zero-silence gaps and full source/gap lineage. No denoising,
normalization, time stretching, semantic selection, or manual quality selection
was added.

- Clean sequences: 24, exactly two per speaker
- Split sequences: train 12, val 6, test 6
- Lineage rows / unique used source utterances: 208 / 208
- Utterances per sequence: 6--12
- Duration: 30.2055625--34.8501250 s; mean 32.1261536 s
- Total clean duration: 771.0276875 s
- Output: `data/constructed_longform/day45_expanded/`
- Lineage: `data/manifests/day45_longform_manifest.csv`

All source order, speaker/split inheritance, source/gap boundaries, output
sample counts, durations, finite-waveform checks, and unique IDs validate.
These remain constructed long-form sequences, not native audiobooks.

## 6. Paired Attack Definition

Every `paired_case_id` corresponds to exactly two rows and two WAVs:

- A0 `cross_speaker_splice`: direct insertion of the unscaled donor crop;
- A1 `artifact_controlled_cross_speaker_splice`: the same donor crop with RMS
  gain and a fixed crossfade.

Within each pair, clean sequence, target source utterance, target sample
indices, donor utterance, donor speaker/text, donor crop start/end, replacement
sample count, split, and pair lineage are identical. Only the declared DSP
artifact-control treatment differs. If either variant cannot be built, the
whole case is skipped.

## 7. Target Selection

Clean sequences are sorted by ID. Duration tiers cycle deterministically as
0.75, 1.5, and 2.5 s. Internal source utterances are checked in a frozen
nearest-to-sequence-middle order. The interval is centered inside the first
candidate with at least 0.5 s safety margin on each side.

Every target is defined first by integer samples at 16 kHz and lies completely
inside one source utterance. No target crosses or touches a constructed fixed
gap. Seconds are derived as `sample_index / sample_rate`.

One target (`day45_train_SSB0009_seq000`, tier 2.5 s) had no qualifying internal
utterance. The entire paired case was skipped; no duration, margin, or placement
rule was relaxed.

## 8. Balanced Donor Assignment

Donors are assigned independently within each split by a deterministic
round-robin cursor over sorted speaker IDs. The target speaker is skipped.
Within the selected donor speaker, candidate utterances are ordered by current
reuse count and sample ID; the first decodable source long enough for the target
is used. The repeat cap is one use per donor utterance.

This guarantees donor split equals target split, donor speaker differs from
target speaker, and donor duration is sufficient. Selection does not use VAD,
RMS preference, detector scores, manual listening, or diagnostic outcomes.

## 9. Donor Usage Statistics

Counts below are paired-case counts; A0 and A1 share each assignment.

| Split | Donor speaker usage |
|---|---|
| train | SSB0005=2, SSB0009=2, SSB0011=2, SSB0261=2, SSB0309=2, SSB0393=1 |
| val | SSB0073=2, SSB0197=2, SSB0434=2 |
| test | SSB0139=2, SSB0342=2, SSB1100=2 |

Within each split, maximum-minus-minimum donor-speaker usage is at most one.
The maximum reuse of any donor utterance is exactly one. All 23 donor crops are
traceable to real selected AISHELL-3 sources.

## 10. Paired A0/A1 Construction

The donor waveform is resampled through the existing standardized loader and a
single centered crop is taken with exactly the target sample count. A0 directly
replaces the shared target interval and records gain 1, no RMS matching, and no
crossfade.

A1 computes `target_rms / max(donor_rms, 1e-8)`, clamps gain to `[0.25, 4.0]`,
and applies a fixed 25 ms (400-sample) crossfade on each side of the same shared
target. Actual A1 gains range from 0.25 to 3.1087330 (mean 1.2111217); no scaled
replacement sample exceeded full scale before writing. DSP parameters were
frozen before diagnostics and were not tuned per sample.

All 23 pairs have different target and donor text (`same_text=false`). A0/A1
therefore retain a linguistic-content confound and are not pure speaker-identity
replacement.

## 11. Temporal Ground Truth

`target_start_sample/end_sample` defines the common paired experimental target.
For both attacks, `attack_start/end` and `blend_start/end` cover that same full
changed region. A0 strict core equals the full target. A1 strict core excludes
the 400-sample crossfade region at each edge.

All sample boundaries satisfy sequence and source-utterance bounds. Stored
seconds match sample indices exactly under `samples / 16000`. Donor crop length
equals target length in every pair. Target equality and donor source/crop
equality are both **PASS** for 23/23 cases.

## 12. Train/Val/Test Coverage

| Split | Clean sequences | Paired cases | A0 | A1 | Skipped cases |
|---|---:|---:|---:|---:|---:|
| train | 12 | 11 | 11 | 11 | 1 |
| val | 6 | 6 | 6 | 6 | 0 |
| test | 6 | 6 | 6 | 6 | 0 |

Every split has clean data and legal paired A0/A1 attacks. Cross-split donor
leakage is zero; same-speaker donor violations are zero.

## 13. Generated Dataset Statistics

- Paired cases: 23
- Manipulated WAVs: 46 (A0=23, A1=23)
- Duration tiers by case: 0.75 s=8, 1.5 s=8, 2.5 s=7
- Attack duration range: 0.75--2.5 s
- Skipped whole cases: 1
- Same-text cases: 0
- Unique attack IDs / manipulated IDs: 46 / 46
- Source semantics: `source_type=natural`, `is_manipulated=true`
- Long-form semantics: `longform_type=constructed`

The forensic lineage is stored in
`data/manifests/day45_attack_manifest.csv`; skip lineage is in
`data/generated/day45_paired/metadata/day45_skips.csv`.

## 14. Waveform Verification

All 46 manipulated WAVs passed actual decoded-sample verification:

- frame count and duration equal the clean sequence;
- sample rate equals 16 kHz and channel count equals mono;
- every sample is finite;
- samples outside the shared target/blend interval are exactly unchanged;
- the target interval contains a real waveform change;
- A0 core reconstructs from the exact unscaled donor crop;
- A1 strict core reconstructs from the same donor crop and recorded gain within
  PCM16 round-trip tolerance;
- crossfade length and core/blend metadata match the actual DSP operation.

Pair-level checks also confirm equal target, donor source, donor crop, and
replacement length. Verification rows are stored in
`data/generated/day45_paired/metadata/waveform_verification.csv`.

## 15. Paired Shortcut Diagnostics

Diagnostics are computed per pair over identical target/donor material. A
negative A1-minus-A0 difference means A1 reduced that specific diagnostic.

| Diagnostic | A0 mean | A1 mean | Mean difference | Median difference | A1 lower cases |
|---|---:|---:|---:|---:|---:|
| Boundary jump total | 0.07191283 | 0.01261646 | -0.05929637 | -0.02646242 | 23/23 (100.00%) |
| Local RMS discontinuity | 0.06603274 | 0.03458953 | -0.03144321 | -0.03020943 | 20/23 (86.96%) |

Every per-case value and difference is recorded in
`data/generated/day45_paired/metadata/paired_diagnostics.csv`. A1 reduced the
specified boundary-jump diagnostic in every pair and the specified local-RMS
diagnostic in 20 pairs. This is an engineering comparison of two DSP treatments
on paired material. It is not evidence that A1 is perceptually more realistic
or harder for a detector.

## 16. Reproducibility

An independent build under a temporary repository root reproduced all eight
checked components:

- 480-row source catalog;
- 480-row text-overlap audit;
- 208-row long-form lineage after excluding environment-local absolute output
  paths;
- 46-row paired attack manifest after excluding environment-local absolute
  output paths;
- one skip row;
- 23 paired diagnostic rows;
- 46 waveform-verification rows;
- all 70 output audio hashes (24 clean + 46 manipulated).

Status: **PASS**. The record is
`data/generated/day45_paired/metadata/reproducibility.csv`.

## 17. Bugs Found

The first donor-balancing implementation used a lowest-current-use greedy tie
break. Although deterministic and legal, it produced a 3/2/1 donor-speaker
distribution in three-speaker splits, leaving an avoidable identity imbalance.
This was caught before the final artifacts were frozen.

One sequence cannot support its assigned 2.5 s target plus two 0.5 s safety
margins. This is a real data constraint rather than a generator defect and is
preserved as an explicit whole-case skip.

No final paired-boundary, donor-lineage, split-leakage, waveform, or ID defect
remains.

## 18. Fixes Made

- Replaced greedy donor-speaker tie-breaking with a deterministic round-robin
  cursor, yielding 2/2/2 usage in val/test and 2/2/2/2/2/1 in train.
- Enforced a donor-utterance repeat cap of one.
- Added exact shared target and donor-crop fields plus paired-case validation.
- Added paired actual-waveform reconstruction and boundary verification.
- Added per-case paired shortcut diagnostics and portable independent
  regeneration checks.
- Added a backward-compatible optional long-form sequence-ID prefix; existing
  Day 3.5 behavior remains the default.

No original AISHELL-3, Day 3 frozen file, Day 3.5 smoke WAV, or Day 4 v2
artifact was overwritten.

## 19. Regression Tests

Eight new Day 4.5 tests cover the expanded split, speaker disjointness, minimum
speaker coverage, deterministic metadata-slot selection, 480-source lineage,
text-audit reproducibility, 24-sequence long-form lineage, paired-case
cardinality, shared target/donor/crop fields, sample/second consistency,
within-utterance margin, donor legality and balancing, repeat cap, train/val/test
coverage, actual A0/A1 waveform verification, paired diagnostics, deterministic
regeneration, raw-source hashes, and prior-stage artifact hashes.

No old test was removed. Final full-suite result: **50 passed in 66.15 s; 0 failed**.

## 20. Research Integrity

- The expanded pilot is not a final benchmark.
- Constructed long-form is not a native audiobook.
- All A0/A1 cases retain a different-text confound.
- Pairing controls target and donor differences only; it does not make A0/A1 a
  pure speaker-identity experiment.
- Artifact diagnostics are not perceptual realism or detection difficulty.
- No detector was trained and no detection/localization performance was run.
- No TTS, unseen-generator, adaptive-attacker, or robustness claim is made.
- A2 `same_text_tts_replacement` remains PENDING.

## 21. Limitations

This remains a small 12-speaker pilot with 23 paired cases in a standardized
16 kHz mono condition. Speaker and metadata diversity are limited by the
predeclared deterministic slots, and exact-text disjointness does not guarantee
semantic disjointness. Fixed gaps and concatenated utterances do not model
native audiobook discourse, prosody, pauses, or recording continuity. One
long-duration case is absent by design. No listening study or detector-based
validation has been performed.

## 22. Day 4.5 Gate

**PASS.**

The expanded pilot has 12 speaker-disjoint speakers with 6/3/3 split coverage;
all splits have paired A0/A1; target and donor equality validate; round-robin
assignment and reuse cap validate; leakage is zero; all 46 waveforms pass;
paired diagnostics are available; temporary regeneration passes; and 39 prior
artifacts plus 480 raw input WAVs remained unchanged.

## 23. Day 5 Entry Conditions

Day 5 is not started. Any later detector/localization work must first preserve
the frozen Day 4.5 config, manifests, skip record, output hashes, and paired
diagnostics; predefine clean/manipulated sampling without pair leakage; retain
speaker-disjoint splits; choose full-region versus strict-core localization
metrics; and explicitly control text, donor-identity, and boundary shortcuts.
A2 requires a separate same-text TTS protocol and remains out of scope.
