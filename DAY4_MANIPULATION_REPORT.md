# Day 4 Manipulation Report

## 1. Executive Summary

Day 4 v2 generated and verified a deterministic, small-scale localized
manipulation pilot from the immutable Day 3.5 constructed long-form sequences.
Six eligible `train` clean sequences produced 11 manipulated waveforms: 6 A0
and 5 A1. All donor-lineage, split, temporal-boundary, pairing, waveform, clean
immutability, reproducibility, regression-test, and Day 3 freeze checks passed.

**DAY 4 LOCALIZED MANIPULATION GATE = PASS.**

No detector was trained, no performance experiment was run, and no Day 5 work
was performed.

## 2. Attack Taxonomy

- **A0 = `cross_speaker_splice`**: real speech from a different speaker is
  spliced into one complete internal source-utterance interval.
- **A1 = `artifact_controlled_cross_speaker_splice`**: real speech from a
  different speaker is inserted into a within-utterance interval after
  deterministic duration matching, RMS matching, and a fixed crossfade.
- **A2 = `same_text_tts_replacement` (PENDING)**: not implemented and no
  placeholder waveform generated.

A0 and A1 are forensic/localization baselines, not voice cloning, deepfake
voice replacement, or pure speaker-identity replacement.

## 3. Threat Model Mapping

A0 tests whether localized waveform replacement, exact localization ground
truth, clean/manipulated pairing, and donor attribution work end to end. It may
contain obvious splice artifacts. A1 tests the same pipeline with limited,
transparent artifact control and an internal-utterance placement that avoids
making every attack coincide with a fixed gap boundary.

Neither attack models same-text neural TTS, native audiobook generation,
unseen-generator robustness, adaptive attackers, or human perceptual realism.
Because donor and target usually differ in text as well as speaker, linguistic,
phonetic, prosodic, and recording-context changes are confounded.

## 4. Clean Constructed Long-form Input

The input is `data/manifests/day35_longform_manifest.csv` and its 10 immutable
Day 3.5 WAVs: 5 speakers, 2 sequences per speaker, 88 real AISHELL-3 utterances,
16 kHz mono, with fixed 0.3 s constructed gaps. These are constructed
long-form sequences, not native audiobook recordings.

Before generation, the four Day 3 hashes in `DAY3_DATA_FREEZE.md` matched. SHA256
hashes for all 10 Day 3.5 clean WAVs were captured in
`data/generated/day4_v2/metadata/day35_clean_input_hashes.csv`; all still match
after generation and verification. Raw AISHELL-3 and clean sequence files were
read only.

## 5. Eligible Splits

Only `train` is eligible. It has three speakers (`SSB0005`, `SSB0009`, and
`SSB0011`) and therefore permits a same-split, different-speaker donor. Pilot
`val` and `test` each contain one speaker, so their four clean sequences cannot
meet both constraints. Their eight A0/A1 attempts were explicitly skipped;
donors were not borrowed across splits and their clean WAVs were untouched.

This train-only pilot is not the final research evaluation split. A future
expanded dataset must provide multiple speakers in every split before legal
cross-speaker attacks can be generated there.

## 6. Target Selection

Sequence IDs are processed lexicographically. A0 selects the middle item from
the internal source utterances and replaces the complete sample-aligned source
interval. It never selects the first or last utterance.

A1 cycles the frozen duration tiers `0.75`, `1.5`, and `2.5` seconds by sorted
eligible-sequence index. It checks internal utterances in deterministic
nearest-to-sequence-middle order and centers the requested interval inside the
first utterance that supports a 0.5 s margin on both sides. If no utterance is
long enough, the attack is skipped instead of relaxing the constraint.

All operations are defined first as integer sample indices at 16 kHz. Seconds
are derived exactly as `sample_index / sample_rate`.

## 7. Donor Selection

Candidates come only from the real AISHELL-3 pilot source catalog. They are
sorted by `(speaker, sample_id)`, and the first decodable candidate satisfying
all of the following is selected:

- donor split equals target split;
- donor speaker differs from target speaker;
- decoded donor duration is at least the requested replacement duration;
- decoded waveform is available at the frozen 16 kHz condition.

Selection does not use VAD, detector scores, RMS preference, manual listening,
or future evaluation results. A0 uses a prefix crop; A1 uses a centered crop.

## 8. Text Confound

Every attack records `target_text_id`, `donor_text_id`, and `same_text`. In this
pilot, `same_text=false` for all 11 attacks. The attacks therefore change text
as well as speaker and must not be interpreted as pure speaker-identity
replacement. A2 is reserved for future same-text TTS work intended to reduce
this confound.

## 9. A0 Waveform Construction

For a target interval of N samples, the deterministic donor prefix is cropped
to exactly N samples and directly replaces the complete internal source
utterance. A0 applies neither RMS matching nor crossfade. Its full attack,
blend, and strict-core intervals are identical. Samples outside that interval
remain exactly equal to the clean WAV after file round-trip.

## 10. A1 Artifact Control

A1 uses the frozen configuration below:

- duration matching: centered crop to the exact target sample count;
- target reference: RMS of the clean target interval;
- RMS gain: `target_rms / max(donor_rms, 1e-8)`;
- gain clamp: `[0.25, 4.0]`;
- crossfade: fixed 25 ms = 400 samples at 16 kHz;
- placement: centered within an internal utterance, with 0.5 s safety margins.

The five actual gains range from 0.3568579200 to 1.5045477532 (mean
0.7978444399). No replacement sample exceeded full scale before file writing,
so the recorded clipped-sample total is zero. All five attacks use exactly 400
crossfade samples on each side as encoded by the core/blend metadata.

## 11. Core / Blend Ground Truth

`attack_start/end` equals `blend_start/end` and covers the complete waveform
region that may differ from clean. For A1, the two 400-sample crossfade zones
surround a strict donor-only core:

`blend_start <= attack_core_start < attack_core_end <= blend_end`.

For A0, crossfade is zero and core equals the full replacement interval. All
six second-valued boundaries are derived from the corresponding stored integer
sample indices. Manifest validation and waveform verification found no
out-of-bounds or seconds/sample inconsistency.

## 12. Pair and Donor Lineage

Each row has unique `attack_id`, `manipulated_sequence_id`, and manipulated WAV
path. It retains the clean `sequence_pair_id`, points to the original
`clean_sequence_id`, and records target source order/sample/speaker/text plus
donor sample/speaker/text/split. Manipulated rows inherit their clean speaker,
split, and `longform_type=constructed`. Natural material remains
`source_type=natural`; manipulation state is independently recorded as
`is_manipulated=true`.

The canonical attack-level forensic lineage is
`data/manifests/day4_attack_manifest.csv`. It supplements rather than replaces
the immutable Day 3.5 clean-lineage manifest.

## 13. Generated Dataset Statistics

| Metric | Result |
|---|---:|
| Eligible clean sequences | 6 |
| A0 generated | 6 |
| A1 generated | 5 |
| Total generated | 11 |
| Skipped attempts | 9 |
| Split distribution | train: 11 |
| Same-text attacks | 0 |
| Cross-split leakage | 0 |

Skip reasons:

- `split_not_eligible_single_speaker_no_legal_donor`: 8 attempts (four
  val/test clean sequences times A0/A1);
- `no internal utterance can satisfy A1 duration and safety margin`: 1 attempt
  (`day35_train_SSB0009_seq000`, assigned 2.5 s tier).

Target speakers are `SSB0005`, `SSB0009`, and `SSB0011`; donor speakers are
`SSB0005` and `SSB0009`. Counts by target/donor pair are
`SSB0005 <- SSB0009: 4`, `SSB0009 <- SSB0005: 3`, and
`SSB0011 <- SSB0005: 4`.

Overall attack duration is 0.7500000--5.9030000 s. A0 spans
2.1344375--5.9030000 s (mean 4.4425104 s). A1 durations are 0.75, 0.75, 1.5,
1.5, and 2.5 s (mean 1.4 s).

## 14. Waveform Verification

All 11 attacks passed automated verification against the actual decoded WAV
samples:

- clean/manipulated sample rate and frame count are equal;
- output is 16 kHz mono and finite;
- samples outside the full attack/blend interval are exactly equal;
- samples inside the interval contain a real change;
- the strict core matches the recorded donor crop multiplied by the recorded
  gain within the PCM16 round-trip tolerance;
- crossfade length, RMS gain, and boundary metadata agree with the DSP record.

Results are stored in
`data/generated/day4_v2/metadata/waveform_verification.csv`. Manipulated file
hashes are stored in
`data/generated/day4_v2/metadata/manipulated_output_hashes.csv`.

## 15. Shortcut Audit

Crossfade was applied to all five A1 attacks and none of the A0 attacks. The
engineering diagnostics are:

| Type | boundary jump-in min / mean / max | boundary RMS discontinuity min / mean / max |
|---|---|---|
| A0 | 0.00003051 / 0.00018331 / 0.00036863 | 0.00121997 / 0.01136189 / 0.02862209 |
| A1 | 0.00017085 / 0.00301782 / 0.00598031 | 0.01395330 / 0.03891159 / 0.05952523 |

A1 does **not** show a lower aggregate boundary-RMS diagnostic than A0 in this
pilot. These are non-paired attacks with different durations and placements:
A0 often begins at a constructed gap/utterance boundary and uses a donor prefix
that may start near silence, while A1 occurs inside speech. Therefore the table
cannot isolate the causal effect of crossfade or RMS matching. It verifies that
the configured controls were applied, but does not support claims that A1 is
more realistic, has fewer artifacts overall, or is harder to detect. A0 may
still contain abrupt or otherwise trivial splice cues.

## 16. Bugs Found

No unresolved boundary, waveform, ID-uniqueness, donor-lineage, split-leakage,
or clean-overwrite defect was found in the final artifacts. Two data-constraint
conditions were detected rather than hidden: singleton-speaker `val`/`test`
cannot supply legal donors, and one train A1 target cannot satisfy its assigned
2.5 s tier plus safety margins. The shortcut audit also exposed that the
current cross-attack summary is not a controlled A0/A1 artifact comparison.

## 17. Fixes Made

Day 4 added a narrowly scoped deterministic generator and validation layer:

- explicit same-split/different-speaker donor rejection;
- sample-index-first target, donor, core, and blend boundaries;
- internal A1 safety-margin checks with recorded skip reasons;
- finite, clamped RMS gain and fixed crossfade metadata;
- independent `source_type` and `is_manipulated` semantics;
- attack-manifest validation, actual-waveform verification, clean-input hashes,
  manipulated-output hashes, and deterministic rerun verification.

No Day 1--3 pipeline was reimplemented and no frozen file was changed.

## 18. Regression Tests

The Day 4 tests cover donor speaker/split constraints, impossible donor
rejection, deterministic donor and attack selection, interval bounds, internal
A1 placement, sample/second consistency, A0/A1 outside-equality and
inside/core-change checks, crossfade length, finite clamped RMS gain,
duration/sample-rate equality, finite waveform, pair/donor lineage, unique IDs,
constructed/natural source semantics, CSV round-trip, clean immutability, and
Day 3 frozen hashes.

The complete suite passes with no old tests removed. The final pytest count is
recorded after the terminal verification run.

An independent regeneration into temporary output directories reproduced all
11 manipulated WAV SHA256 hashes and all nine skip rows exactly.

## 19. Research Integrity

A0 and A1 use real, usually different-text donor speech from another speaker.
A0 is a basic forensic pipeline baseline and may expose obvious splice cues.
A1 adds only transparent RMS matching and crossfade; it remains different-text
cross-speaker splicing, not neural voice cloning. No detector performance,
localization accuracy, perceptual realism, unseen-generator robustness,
long-form TTS robustness, or adaptive robustness is claimed.

## 20. Limitations

- This is a small pilot with only six eligible clean sequences and 11 attacks.
- Attack generation is train-only because current val/test each have one
  speaker.
- Constructed long-form sequences are not native audiobooks.
- All 11 attacks have a different-text confound.
- A0/A1 are not neural voice cloning.
- Only the standardized 16 kHz mono condition is covered.
- Artifact diagnostics are descriptive and non-paired, not perceptual or
  detector evidence.
- A2 remains pending.

## 21. Day 4 Gate

**PASS.** Real A0 and A1 waveforms exist; lineage and pairing validate; donors are same-split and
different-speaker; singleton splits are rejected; boundaries match actual
samples; core/blend checks pass; samples outside attacks remain unchanged;
temporary regeneration is byte-reproducible; Day 3 and clean Day 3.5 hashes are
unchanged.

Final full-suite result: **42 passed in 4.33 s; 0 failed**.

## 22. Day 5 Entry Conditions

Day 5 is not started. Before any later detector/localization experiment, retain
the frozen Day 4 config and manifests, preserve clean/manipulated separation,
decide how to construct multi-speaker validation and test splits without donor
leakage, define metrics separately for full blend region and strict core, and
pre-register how text and boundary shortcuts will be controlled. A2 requires a
separate same-text TTS protocol and remains out of scope.
