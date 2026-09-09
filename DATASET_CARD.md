# DATASET_CARD.md

Status: **protocol implemented; real research data not yet bundled**.

## Source types

- `natural`: human speech control
- `tts`: clean generated speech

Manipulation state is represented independently by `is_manipulated`.

## Canonical segment-manifest fields

```text
audio_path
sample_id
pair_id
source_sample_id
source_type
generator
generator_family
speaker
text_id
duration
sample_rate
segment_id
segment_start
segment_end
position
is_manipulated
attack_type
attack_start
attack_end
attack_generator
source_generator
replacement_speaker
split
```

## Day 2 manifest status

`configs/manifest_schema.yaml` defines the shared protocol.

- `source_type` is only `natural` or `tts`.
- `is_manipulated` is independent from provenance.
- `pair_id` groups clean/manipulated counterparts and must remain within one split.
- `source_sample_id` records clean/manipulated lineage.
- `data/manifests/example_manifest.csv` is a schema/unit-test example only and is not research evidence.

## Day 3 source-audio catalog

Day 3 introduces a separate **file-level** source catalog because speaker/generator/text metadata must be explicit rather than guessed from filenames.

Template:

```text
data/manifests/source_audio_template.csv
```

Copy it to:

```text
data/manifests/source_audio.csv
```

and replace placeholders with actual natural/TTS audio metadata.

Day 3 only accepts clean source rows (`is_manipulated=false`). Manipulated audio is deliberately deferred to Day 4.

## Day 3 generated segment diagnostics

The generated canonical manifest may also contain these additional diagnostic columns:

```text
original_sample_rate
original_channels
segment_duration
vad_voiced_ratio
rms
peak
```

They are sanity/traceability metadata, not standalone research claims.

## Day 3.5 path portability

`audio_path` remains supported for backward compatibility. A source catalog may
also add the optional extension field `audio_relpath`, stored with POSIX `/`
separators. At runtime it is joined to an explicit dataset root or the
`AUDIOBOOKBENCH_DATASET_ROOT` environment variable. This extension does not
change the Day 2 canonical required columns.

## Day 3.5 constructed long-form

`configs/day35_constructed_longform.yaml` defines deterministic concatenation
of same-speaker, same-split AISHELL-3 utterances with fixed recorded silence
gaps. The separate `data/manifests/day35_longform_manifest.csv` records ordered
source lineage and sample-aligned boundaries.

These waveforms have `longform_type=constructed`. They are not native audiobook
or native continuous long-form recordings. The fixed gap is an engineering
construction parameter, not natural-pause ground truth.

## Day 4 localized manipulation pilot

`configs/day4_manipulation_v2.yaml` freezes a small, deterministic forensic
manipulation protocol over the Day 3.5 clean constructed sequences. The
separate `data/manifests/day4_attack_manifest.csv` records attack-level temporal
ground truth, clean/manipulated pairing, and donor lineage; it does not replace
the immutable Day 3.5 clean-lineage manifest.

- `A0 = cross_speaker_splice`: a complete internal source-utterance interval is
  replaced by same-split, different-speaker real AISHELL-3 pilot speech.
- `A1 = artifact_controlled_cross_speaker_splice`: a deterministic internal
  interval is duration-matched, RMS-matched, and blended with a fixed 25 ms
  crossfade.
- `A2 = same_text_tts_replacement`: **PENDING**; no TTS waveform was generated.

The current pilot generates A0/A1 only for `train`, because the pilot `val` and
`test` splits each contain one speaker and therefore cannot provide a legal
same-split, different-speaker donor. A0/A1 usually change both speaker and text;
they are localization/forensic baselines, not neural voice cloning or pure
speaker-identity replacement. All attacked sequences retain
`longform_type=constructed`, `source_type=natural`, and use
`is_manipulated=true` independently.

## Current limitations

- No raw research audio is bundled in this package; manifests reference the
  external read-only AISHELL-3 location.
- A five-speaker Day 3 pilot manifest and a small Day 3.5 constructed-long-form
  smoke set have been generated. Neither is a final research dataset.
- The current VAD is an energy-based sanity baseline, not a validated production VAD.
- No real speaker embedding backend is configured yet.
- F0, pause ratio, and speech rate remain unvalidated on real audio.
- Day 4 contains only a small train-split manipulation-engineering pilot. No
  detection/localization performance, perceptual realism, unseen-generator,
  adaptive-attack, or native-audiobook result is claimed.
