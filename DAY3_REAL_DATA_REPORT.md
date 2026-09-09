# Day 3 Real Data Report

Date: 2026-09-04  
Project: AudiobookBench-CN  
Scope: Day 3 Real Data Gate only

## 1. Executive Summary

The Day 3 Real Data Gate passes on a deterministic pilot built from the locally
available AISHELL-3 corpus. The complete raw corpus was audited read-only at the
header and metadata-lineage level. A 200-utterance pilot from five speakers was
then decoded, resampled, segmented, diagnosed with the energy-VAD sanity
baseline, written as a canonical segment manifest, and validated.

One real-data-triggered segmentation bug was found and fixed: a 5.x-second file
could retain a sub-one-second tail because the tail merge incorrectly required
a preceding segment to exist before extending the first window. A focused
regression test was added.

No original AISHELL-3 file was copied, modified, moved, renamed, or deleted. No
manipulation data, detector, attack experiment, or research result was created.

## 2. Dataset Location

Actual local root:

```text
F:\项目\申请实验室  TTS项目\datasets\AISHELL-3
```

Raw extracted corpus:

```text
F:\项目\申请实验室  TTS项目\datasets\AISHELL-3\raw
```

The root also contains `sample/audio/` with 200 `sample_*.wav` files. These were
excluded because their names do not provide the canonical speaker/transcript
lineage used by `raw/train` and `raw/test`. The 19 GB source archive
`raw/data_aishell3.tgz` was left untouched.

## 3. Dataset Audit

The observed raw structure is:

```text
raw/
  spk-info.txt
  phone_set.txt
  ReadMe.txt
  train/
    content.txt
    label_train-set.txt
    wav/<speaker_id>/<utterance_id>.wav
  test/
    content.txt
    wav/<speaker_id>/<utterance_id>.wav
```

Full raw-corpus read-only audit:

- WAV files: 88,035 (`train`: 63,262; `test`: 24,773)
- Speakers on disk: 218
- Unique WAV names: 88,035
- Format: 88,035 WAV, all PCM_16
- Sample rate: 88,035 at 44,100 Hz
- Channels: 88,035 mono
- Total header duration: 85.617826 hours
- Duration: min 0.789478 s, mean 3.501155 s, max 15.719977 s
- Files shorter than 1 s: 22; files longer than 10 s: 47. These are retained
  and reported, not treated as corrupt based only on duration.
- Unreadable WAV: 0; empty WAV: 0
- Transcript rows: 88,035; duplicate transcript IDs: 0
- WAV without transcript: 0; transcript without WAV: 0
- Speaker metadata rows: 218; missing/unmatched speaker metadata: 0
- WAV parent-directory / filename speaker mismatch: 0
- Train prosody-label rows: 63,262; parse errors: 0; unmatched train WAV: 0

`content.txt` uses one row per WAV: filename, a tab, then alternating Chinese
character and pinyin-with-tone tokens. The speaker is the parent directory and
the first seven characters of the utterance ID, for example
`SSB0005/SSB00050001.wav`. `spk-info.txt` provides age group, gender, and accent.

Actual `spk-info.txt` distributions:

- Age group: A=2, B=173, C=35, D=8
- Gender: female=176, male=42
- Accent: north=165, south=51, others=2

Metadata issue: `raw/ReadMe.txt` states 43 male / 175 female, while the actual
218 parsed rows in `spk-info.txt` contain 42 male / 176 female. Pilot metadata
uses the actual `spk-info.txt` rows and does not guess which document is wrong.

## 4. Pilot Selection

Pilot size: five speakers, 40 utterances per speaker, 200 utterances total.

Selected speakers:

| Speaker | Age group | Gender | Accent | Utterances |
|---|---:|---|---|---:|
| SSB0005 | B | female | north | 40 |
| SSB0009 | B | female | south | 40 |
| SSB0011 | C | female | north | 40 |
| SSB0073 | B | male | north | 40 |
| SSB0139 | B | male | south | 40 |

The deterministic speaker rule covers the four available gender/accent
combinations using the lexicographically first eligible speaker, then adds the
lexicographically first eligible age-group-C speaker not already selected.
Eligible speakers require at least 40 WAVs with matching transcript and
metadata. Within each speaker, files are sorted by utterance ID and the first 40
are selected. No model, VAD, RMS, peak, future detector result, or manual quality
preference influenced selection. Random seed: not applicable.

The exact selection, including `selection_rank`, is persisted in
`data/manifests/source_audio.csv`; the policy is recorded in
`configs/day3_aishell3_pilot.yaml`.

## 5. Split Strategy

Pilot split is deterministic and speaker-disjoint:

- train: SSB0005, SSB0009, SSB0011 (120 sources)
- val: SSB0073 (40 sources)
- test: SSB0139 (40 sources)

No speaker crosses a pilot split. Every clean source has its own `pair_id`, so no
pair crosses a split. The original AISHELL-3 train/test partition is retained as
traceability metadata but is not used as the pilot split because 170 speakers
occur in both original partitions. This five-speaker allocation is an
engineering pilot and is not claimed as a final experimental split.

## 6. Real Audio Pipeline

The following pipeline was executed on all 200 selected real WAV files:

```text
AISHELL-3 WAV absolute path
  -> probe WAV header
  -> decode float32 waveform
  -> mono conversion (inputs were already mono)
  -> resample 44.1 kHz to 16 kHz
  -> deterministic 5 s windows
  -> merge final tail when shorter than 1 s
  -> segment energy-VAD/RMS/peak diagnostics
  -> canonical CSV manifest
  -> canonical validation
```

The source WAVs were referenced by absolute path. No pilot WAV copies were made.

## 7. Manifest Statistics

- Source samples: 200
- Segments: 217
- Speakers: 5
- Sources by split: train=120, val=40, test=40
- Segments by split: train=135, val=42, test=40
- Sources producing one segment: 183; two segments: 17
- Source duration: min=1.493741 s, mean=3.691496 s, max=9.708005 s
- Total source duration: 738.299116 s (12.304985 min)
- Segment duration: min=1.028937 s, mean=3.402327 s, max=5.948063 s
- Original sample rate: 44,100 Hz for all sources
- Output sample rate: 16,000 Hz for all segments
- Original channels: mono for all sources

Energy-VAD sanity ratios across 217 segments:

- min=0.018072
- 5th percentile=0.051211
- median=0.153846
- mean=0.165844
- 95th percentile=0.326601
- max=0.422741
- exactly zero: 0; exactly one: 0

Other waveform sanity diagnostics after resampling:

- RMS: min=0.014199, mean=0.040643, max=0.083882
- peak: min=0.077632, mean=0.306521, max=0.767334
- near-silent segments using RMS < 1e-4: 0
- clipping-suspect segments using peak >= 0.999: 0
- decoded empty or non-finite pilot waveform: 0

These are engineering sanity statistics only. They are not speech-quality,
speaker, detector, or scientific-performance results.

## 8. Lineage Validation

Validation passed for all source and segment rows:

- `sample_id` is unique across 200 sources.
- `pair_id` is unique per clean source and does not cross splits.
- Every clean row has `source_sample_id == sample_id`.
- `source_type == natural` and `is_manipulated == false` for every source.
- All attack fields are empty under the canonical clean-row rule.
- `speaker` matches both the WAV parent directory and utterance ID prefix.
- `text_id` deterministically references the utterance ID.
- Chinese transcript, pinyin, transcript source file, original AISHELL-3
  partition, age group, gender, and accent remain in the source catalog.
- No speaker crosses train/val/test.

## 9. Temporal Alignment Validation

Audit tolerance for segment boundaries: `1e-6` seconds.

- All `segment_start >= 0` and `segment_start < segment_end`.
- All `segment_end <= resampled duration`.
- Maximum final-segment-end versus manifest-duration difference: 0 s.
- Maximum recorded `segment_duration` consistency error: 0 s.
- Gaps or overlaps between adjacent segments: 0.
- Positions are continuous from zero for every source.
- All 217 `segment_id` values are globally unique.
- Maximum original-header versus resampled-duration difference:
  0.000061791 s, below one 16 kHz sample period (0.0000625 s).
- The corrected short-tail behavior was exercised by real 5.x-second files;
  for example, SSB00050006 (5.026984 s) now produces one merged segment.

## 10. Spot Checks

The first 20 source samples in sorted `sample_id` order
(`SSB00050001` through `SSB00050020`) were checked deterministically.

For all 20:

- the original file exists and decodes;
- the parent directory, filename prefix, and speaker metadata agree;
- Chinese and pinyin transcripts exist and trace to the correct `content.txt`;
- duration is positive and segment count is consistent with the configured
  segmentation rule;
- positions and start/end times are valid;
- the final segment is in bounds;
- actual resampled waveform slice lengths equal the expected sample counts;
- clean-row lineage and split are correct.

Spot checks passed: 20/20.

## 11. Bugs Found

1. `fixed_windows` failed to merge a short tail immediately after the first
   5-second window. Twenty-four selected real files exposed this 5.x-second
   boundary case.
2. The repository was distributed as a ZIP inside the canonical directory;
   Windows `tar` mis-decoded two Chinese filenames. The source was re-expanded
   with PowerShell's ZIP support and only the two malformed extraction
   duplicates were removed. The source archive was retained unchanged.
3. The CLI requires an editable install or `PYTHONPATH=src`. The pytest config
   handles tests, but an uninstalled plain Python invocation cannot import the
   package. The documented `PYTHONPATH=src` execution path was used; no packaging
   change was necessary for this gate.
4. AISHELL-3's readme gender totals disagree with the actual speaker metadata by
   one speaker, as documented in Section 3.

## 12. Fixes Made

- Removed the unnecessary `segments` precondition from the short-tail merge in
  `src/audiobookbench/preprocessing/segment.py`.
- Added a regression test for a 5.4-second waveform in
  `tests/test_audio_pipeline.py`.
- Added `configs/day3_aishell3_pilot.yaml` to freeze pilot membership, split,
  selection policy, and audio parameters.
- Generated the real `data/manifests/source_audio.csv` and validated
  `data/manifests/week1_manifest.csv`.

No raw AISHELL-3 data was changed.

## 13. Regression Tests

The focused audio-pipeline suite passed after the boundary fix:

```text
7 passed
```

The complete final regression suite passed after all outputs were generated:

```text
python -m pytest -q
28 passed in 1.01s
```

## 14. Research Integrity Checks

- All reported dataset and pilot statistics came from local file reads and real
  pipeline execution.
- The full corpus was not copied into the repository.
- Original audio was used read-only through absolute paths.
- Selection was independent of VAD, waveform scores, and future model outcomes.
- The pilot is clean natural speech only; no manipulation or attack metadata was
  fabricated.
- Test fixtures remain separate from research data.
- Energy-VAD, RMS, and peak values are reported only as sanity diagnostics.
- No detector was trained and no attack or performance experiment was run.

## 15. Limitations

AISHELL-3 is primarily an utterance-level Mandarin TTS corpus. It is not a set of
native, continuous, long-form audiobook recordings. This pilot validates real
audio ingestion and temporal bookkeeping but does not validate long-form
audiobook behavior.

If future work concatenates utterances into longer sequences, every such sample
must be labeled **constructed long-form** and must not be described as a native
long-form recording. The five-speaker split is too small for final scientific
evaluation. The energy VAD remains an unvalidated sanity baseline. No conclusion
is drawn from the observed demographic counts, VAD ratios, RMS, or peaks.

## 16. Day 3 Real Data Gate

**PASS.** The real corpus was read successfully; deterministic pilot selection,
audio/transcript/speaker lineage, speaker-disjoint splits, real audio processing,
canonical manifest generation, validation, temporal alignment, spot checks, and
regression tests all passed.

## 17. Remaining Blockers

- AISHELL-3 does not provide native long-form audiobook recordings.
- The pilot contains only five speakers and is not a final research split.
- The readme/spk-info gender-total discrepancy should be cited or clarified if
  demographic analysis is later attempted.
- Production VAD, F0, pause/speech-rate features, speaker embeddings, human
  checks, and security experiments remain outside Day 3.

## 18. Recommended Day 4 Entry Conditions

Before Day 4, explicitly freeze and review:

1. whether Day 4 will operate on utterance-level samples or separately labeled
   constructed-long-form sequences;
2. a larger speaker-disjoint split suitable for the intended generalization
   claim;
3. clean/replacement pairing rules that preserve text, speaker, generator, and
   channel lineage;
4. manipulation boundary and resampling policies that avoid trivial splice or
   codec shortcuts;
5. an immutable copy or checksum record for the Day 3 source and segment
   manifests.

Day 4 was not started by this gate.
