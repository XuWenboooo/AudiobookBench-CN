# DAY3_REPORT.md — Real Audio Ingestion Pipeline

Date: 2026-09-04  
Project: AudiobookBench-CN  
Priority: Liu Zheli security/forensics track first; Qin Yong responsible-evaluation track second.

## 1. Day 3 goal

Day 3 implements the real clean-audio path required before any manipulation or security experiment:

```text
Real Audio
  -> inspect/load
  -> mono conversion
  -> resample
  -> deterministic segmentation
  -> energy-VAD sanity diagnostics
  -> canonical segment-level manifest
  -> manifest validation
```

No Day 4 manipulation, detection, localization, attribution, or adaptive-attack functionality was added.

## 2. Files created or modified

Created:

- `configs/day3_audio.yaml`
- `data/manifests/source_audio_template.csv`
- `data/raw/README.md`
- `data/natural_control/README.md`
- `src/audiobookbench/data/prepare_audio.py`
- `tests/test_audio_pipeline.py`
- `DAY3_REPORT.md`

Modified:

- `src/audiobookbench/preprocessing/audio_io.py`
- `src/audiobookbench/preprocessing/segment.py`
- `src/audiobookbench/preprocessing/__init__.py`
- `src/audiobookbench/data/__init__.py`
- `README.md`
- `DATASET_CARD.md`

## 3. Audio ingestion behavior

`load_audio()` now:

- requires an existing non-empty audio file;
- loads through `soundfile`;
- converts stereo/multichannel input to mono by channel averaging;
- rejects NaN/Inf waveforms;
- optionally resamples with `scipy.signal.resample_poly`;
- returns mono `float32` plus final sample rate.

`probe_audio()` records original:

- sample rate;
- frame count;
- channel count;
- duration.

## 4. Segmentation policy

The first protocol intentionally uses deterministic, non-overlapping fixed windows.

Default:

```text
window_seconds = 5.0
min_tail_seconds = 1.0
```

A tiny final tail is merged into the preceding window so the manifest does not contain unusably short final segments.

This fixed-window protocol is deliberately simple so later security results are not confounded by an evolving segmentation policy.

## 5. VAD policy

Day 3 retains an energy-based frame VAD only as a **sanity baseline**. It produces `vad_voiced_ratio` per segment.

It must not be described as a validated speech VAD in formal claims. A stronger VAD backend can be added later after the real-data pipeline is stable.

## 6. Source catalog

The project does not infer speaker/generator/text metadata from filenames.

The researcher must create:

```text
data/manifests/source_audio.csv
```

from:

```text
data/manifests/source_audio_template.csv
```

The Day 3 source catalog is file-level and accepts **clean rows only**. This prevents Day 3 from silently drifting into Day 4 manipulation work.

## 7. Generated canonical manifest

Run:

```bash
python -m audiobookbench.data.prepare_audio \
  --catalog data/manifests/source_audio.csv \
  --output data/manifests/week1_manifest.csv \
  --target-sr 16000 \
  --window-seconds 5.0 \
  --min-tail-seconds 1.0
```

Each file-level source row becomes one or more canonical segment rows. The generated rows are immediately checked by `validate_manifest()`.

Additional diagnostics are saved as extra columns:

```text
original_sample_rate
original_channels
segment_duration
vad_voiced_ratio
rms
peak
```

## 8. Tests

New unit tests cover:

- audio header probing;
- resampling from 8 kHz to 16 kHz;
- finite waveform loading;
- deterministic fixed-window segmentation;
- tiny-tail merging;
- silence vs tone behavior of the energy-VAD sanity baseline;
- source-catalog loading;
- conversion from file-level metadata to canonical segment manifest;
- output CSV generation and canonical validation;
- rejection of manipulated rows during Day 3 ingestion.

The audio fixtures created inside tests are deterministic synthetic WAVs used only for software validation. They are not experimental evidence.

## 9. Test result

Command:

```bash
python -m pytest -q
```

Result:

```text
27 passed
```

The CLI entry point was also checked with:

```bash
python -m audiobookbench.data.prepare_audio --help
```

## 10. Research gate status

### Engineering gate

**PASS.** The repository can ingest a real audio file, resample it, segment it, produce time-aligned metadata, and validate a canonical manifest.

### Real-data gate

**PENDING.** No real audio files were provided in the current package, so Day 3 has not yet demonstrated the pipeline on actual research audio.

This distinction is important: software unit tests do not substitute for real-data validation.

## 11. What is still missing before Day 4

Before starting controlled manipulation, the researcher should supply a small real-audio pilot set and verify:

1. at least 20–50 real natural/TTS audio files or a smaller pilot sufficient for manual inspection;
2. `source_audio.csv` contains correct explicit metadata;
3. `week1_manifest.csv` is generated successfully;
4. random manual checks confirm segment start/end times align with the audio;
5. resampling does not introduce obvious corruption;
6. `vad_voiced_ratio` is not systematically zero/one for normal speech;
7. split/pair lineage rules still validate.

If these checks fail, fix Day 3 data ingestion before starting Day 4.

## 12. Day 3 status

Day 3 **engineering implementation is complete**, but the **real-data research gate remains pending** until actual audio is supplied and manually sanity-checked.
