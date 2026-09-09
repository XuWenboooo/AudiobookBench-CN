# Day 3.5 Long-form Protocol Report

Date: 2026-09-04  
Scope: Data Freeze + Portability + Constructed Long-form Protocol

## 1. Executive Summary

The Day 3.5 gate passes. Four Day 3 artifacts were frozen by SHA256 and remained
unchanged throughout this work. A backward-compatible `audio_relpath` extension
was implemented and verified with POSIX- and Windows-style relative paths. The
speaker-disjoint pilot was audited for normalized Chinese transcript overlap.

Ten deterministic constructed-long-form smoke sequences were generated from 88
real AISHELL-3 pilot utterances. All sequence/source/gap boundaries, waveform
durations, speaker/split constraints, source hashes, and lineage checks passed.
No manipulation, attack waveform, detector, training, or performance claim was
created.

## 2. Day 3 Data Freeze

Freeze timestamp: `2026-09-04T21:28:04+08:00`.  
Git commit: `NOT AVAILABLE`; the canonical directory has no `.git` metadata.

Frozen files and SHA256:

| File | SHA256 |
|---|---|
| `configs/day3_aishell3_pilot.yaml` | `5ABBF04AD741500D314EEA0EF4285C97EF0A538C0E9416A587F9933D3D49C36E` |
| `data/manifests/source_audio.csv` | `6F6D165B020416DA3153DC4D129E06998ED0A193C88C932C5CDF03B72E04A596` |
| `data/manifests/week1_manifest.csv` | `B1D77517031AAB2D02D29A7978CE3FA44097E23E9CC69095786D4746179C7264` |
| `DAY3_REAL_DATA_REPORT.md` | `A567BA2BD85ACD8401A7E5B7C733969E57792FC96832A270D100BF4DC67B426E` |

Post-construction verification reproduced all four hashes exactly. The complete
freeze record is in `DAY3_DATA_FREEZE.md`.

Frozen data summary:

- Sources: 200; segments: 217; speakers: 5
- Source splits: train=120, val=40, test=40
- Segment splits: train=135, val=42, test=40
- Standardized sample rate: 16 kHz mono
- Segmentation: 5 s fixed windows, tails shorter than 1 s merged
- Pilot selection: metadata-stratified deterministic speakers, then first 40
  utterance IDs per speaker; no random seed and no outcome-based selection

## 3. Path Portability

Old behavior used `audio_path` directly, and the Day 3 source catalog therefore
contained absolute Windows paths tied to this workstation.

New behavior keeps `audio_path` fully supported and adds the optional extension
`audio_relpath`. If `audio_relpath` and a dataset root are supplied, runtime
resolution prefers:

```text
dataset_root / audio_relpath
```

The root may be passed by API/CLI or set through
`AUDIOBOOKBENCH_DATASET_ROOT`. Relative paths are normalized with `pathlib`;
both `/` and `\` input separators are accepted, while absolute or parent-escape
`audio_relpath` values are rejected. Portable manifests store `/` separators.

The frozen Day 3 catalog was not rewritten. A new
`data/manifests/day35_source_audio_portable.csv` contains 200 optional
`audio_relpath` values. The real long-form build resolved those paths against
the configured AISHELL-3 root. Day 2 required columns and canonical validation
remain unchanged.

Portability status: **PASS**.

## 4. Text Overlap Audit

Normalization is deterministic and deliberately narrow:

1. Unicode NFC normalization;
2. strip leading/trailing whitespace;
3. preserve punctuation, Chinese characters, and meaning exactly.

Results:

| Measure | Count |
|---|---:|
| train unique texts | 120 |
| val unique texts | 40 |
| test unique texts | 40 |
| train ∩ val | 0 |
| train ∩ test | 0 |
| val ∩ test | 0 |
| train ∩ val ∩ test | 0 |

There are no overlap examples because all measured intersections are empty. The
full 200-text audit is saved at
`data/reports/day3_text_overlap_audit.csv`.

Speaker-disjoint does not logically imply text-disjoint. This specific pilot
happens to have zero exact overlap under the stated normalization; that result
must not be generalized to another split or to semantic/paraphrase overlap.
The split was not changed after observing the audit.

## 5. Constructed Long-form Definition

A constructed long-form sequence is a deterministic concatenation of complete,
ordered, real AISHELL-3 utterances from exactly one speaker and one pilot split,
with explicit fixed silence gaps and complete source lineage.

It is not a native audiobook, native long-form speech, or a continuous audiobook
recording. AISHELL-3 is primarily an utterance-level Mandarin corpus.

## 6. Sequence Construction Policy

Protocol version 1.0 is frozen in
`configs/day35_constructed_longform.yaml`:

- allowed sources: the five-speaker Day 3 pilot only;
- ordering: `selection_rank`, then `sample_id`;
- two sequences per speaker;
- minimum/preferred/maximum duration: 20/30/60 s;
- minimum/maximum utterances per sequence: 4/12;
- greedy ordered packing stops after reaching at least the preferred duration;
- one speaker and one inherited split per sequence;
- mono conversion and resampling to the standardized 16 kHz condition;
- no loudness normalization, denoise, time stretch, semantic editing, random
  ordering, or manual quality selection.

Sequence IDs use `day35_<split>_<speaker>_seq<index>`. Source utterances are
consumed in order and are not selected from waveform or detector outcomes.

## 7. Gap Policy

Every internal gap is exactly 0.3 s, represented by 4,800 zero-valued samples at
16 kHz. The first utterance has no leading gap and the last has no trailing gap.
All 78 generated internal gaps were 0.3 s. Maximum measured gap-duration error
was `2.8311e-15` s, below the `1e-6` s audit tolerance.

This fixed silence is an engineering construction parameter. It is not natural
pause ground truth and is not claimed to simulate audiobook prosody.

## 8. Long-form Lineage Schema

The separate `data/manifests/day35_longform_manifest.csv` contains one row per
source utterance and records:

- `sequence_id`, `sequence_pair_id`, and `clean_sequence_id`;
- output absolute path and repository-relative path;
- speaker, split, sequence duration/sample count/sample rate;
- canonical `source_sample_id`, portable source path, and continuous order;
- source interval and standardized source duration;
- exact sequence interval;
- duration and explicit start/end boundaries for preceding/following gaps;
- `longform_type=constructed`.

For future Day 4 compatibility, a manipulated counterpart can reuse
`sequence_pair_id`, point to `clean_sequence_id`, record `attack_start` and
`attack_end` in sequence time, and identify the overlapping
`source_sample_id`/source interval. This structure was checked only for future
compatibility; no attack or manipulated waveform was generated.

## 9. Generated Smoke-test Dataset

Output directory:

```text
data/constructed_longform/day35_smoke
```

Observed results:

- Sequences: 10, exactly two per speaker
- Sequence split counts: train=6, val=2, test=2
- Lineage rows / unique source utterances used: 88 / 88
- Utterances per sequence: min=6, max=12
- Duration: min=30.494 s, mean=32.588925 s, max=34.850125 s
- Total constructed duration: 325.88925 s
- Format: ten 16 kHz, mono WAV files
- Non-finite output waveforms: 0

All waveform material comes from real pilot AISHELL-3 audio plus documented
zero-silence gaps. No synthetic speech fixture is present in this dataset.

## 10. Temporal Alignment Validation

Tolerance: `1e-6` s. Validation covered all 88 lineage rows and all ten output
waveforms.

- Source intervals begin at zero, remain within actual resampled source
  waveforms, and preserve full utterance duration.
- Maximum source duration versus actual waveform error: 0 s.
- Source order is continuous from zero.
- Sequence utterance intervals do not overlap.
- Every interval between utterances is represented by an explicit gap.
- Maximum adjacent-boundary error: 0 s.
- Maximum output WAV versus manifest sequence-duration error: 0 s.
- Gap-before/gap-after boundaries and durations are internally consistent.
- Sequence sample counts equal the written WAV frame counts.
- Sequence-level IDs and output waveform paths are unique.

Temporal alignment status: **PASS**.

## 11. Speaker / Split Integrity

Each of the five speakers generated exactly two sequences. Every lineage row was
cross-checked against the portable source catalog: source speaker and split
match, no sequence crosses a speaker, and no sequence crosses a split.

Speaker/split integrity status: **PASS**.

## 12. Tests

New regression coverage includes:

- POSIX relative path resolution;
- Windows-style relative path compatibility;
- legacy absolute-path compatibility and environment-root resolution;
- same-speaker and same-split enforcement;
- continuous source order and traceable `source_sample_id`;
- source and sequence interval bounds;
- fixed gap values and explicit gap boundaries;
- sequence waveform/sample-count/duration agreement;
- unique sequence identities and `longform_type=constructed`;
- finite constructed waveforms;
- before/after source-file hash equality.

Final complete regression result:

```text
python -m pytest -q
34 passed in 1.43s
```

## 13. Bugs Found

- Day 3 source manifests were tied to an absolute local Windows dataset path.
  This was a portability limitation, not a manifest-lineage failure.
- No existing sequence-level schema could represent ordered utterance and gap
  lineage without overloading the canonical segment manifest.
- No new temporal-alignment or waveform-integrity bug was found during the real
  long-form construction.

## 14. Fixes Made

- Added optional, safe `audio_relpath` resolution while retaining `audio_path`.
- Added API/CLI dataset-root support and the
  `AUDIOBOOKBENCH_DATASET_ROOT` environment fallback.
- Added the portable Day 3.5 source catalog and text-overlap audit.
- Added a separate constructed-long-form builder, validator, lineage schema,
  protocol configuration, and tests.
- Generated ten real constructed-long-form smoke WAVs and their lineage
  manifest.
- Recorded SHA256 for all 200 pilot source WAVs before construction and verified
  them after construction; mismatches: 0.
- Updated the dataset card to document portability and the strict
  constructed-versus-native distinction.

## 15. Research Integrity

- AISHELL-3 is an utterance-level corpus.
- Every generated long-form waveform is explicitly marked `constructed`.
- Constructed long-form is not native audiobook or native long-form speech.
- The 0.3 s fixed gap is not natural-pause ground truth.
- The standardized 16 kHz condition is not the only real-world condition;
  native/native-like sample-rate evaluation remains a documented extension.
- No long-form TTS robustness, human perception, quality, or security
  performance conclusion is drawn.
- No sequence membership was selected or adjusted using detector outcomes.
- No detector was trained, no attack was implemented, and Day 4 was not entered.
- All original AISHELL-3 files remained unchanged; 200/200 pilot source hashes
  matched before and after.

## 16. Limitations

The smoke set contains only ten sequences from five speakers and 88 source
utterances. It tests engineering traceability and alignment, not research-scale
generalization. Exact text overlap is zero only for this small pilot and this
normalization rule. Semantic overlap was not measured. Fixed silence and
utterance concatenation do not reproduce the discourse, prosody, continuity, or
recording process of a native audiobook.

**Constructed long-form != native audiobook.**

## 17. Day 3.5 Gate

**DAY 3.5 DATA FREEZE + LONGFORM PROTOCOL GATE = PASS.**

All required hashes, portability behavior, text audit, protocol, real smoke
sequences, lineage, temporal alignment, speaker/split checks, source immutability
checks, and regression tests passed without describing constructed data as
native long-form.

## 18. Day 4 Entry Conditions

Before any Day 4 work, explicitly freeze:

1. whether attacks target an entire source utterance or an interval inside it;
2. manipulated sequence naming plus `sequence_pair_id`/`clean_sequence_id`
   semantics;
3. attack timestamp and boundary-rounding rules at 16 kHz;
4. replacement source speaker/text/generator/channel metadata;
5. rules preventing cross-split, cross-pair, speaker, text, and channel leakage;
6. whether the first experiment remains in standardized 16 kHz or adds a
   separately reported native/native-like condition;
7. an explicit statement that any attacked sequence remains constructed
   long-form, not a native audiobook.

Day 4 was not started.
