# DAY2_REPORT.md — Manifest Schema and Project Structure

Date: 2026-09-04  
Project: AudiobookBench-CN  
Priority: Liu Zheli security/forensics track first; Qin Yong responsible-evaluation track second.

## 1. What changed

Day 2 focused on the shared data protocol required for all later experiments. The project now has a canonical manifest schema, a standard-library manifest loader/validator/saver, a small schema example, and stronger tests. This is still infrastructure work; no real audio experiment, manipulation generator, detection baseline, or research result was added today.

## 2. Files created or modified

Created:

- `configs/manifest_schema.yaml`
- `src/audiobookbench/data/__init__.py`
- `src/audiobookbench/data/manifest.py`
- `data/manifests/example_manifest.csv`
- `DAY2_REPORT.md`

Modified:

- `pyproject.toml`
- `src/audiobookbench/utils/manifest.py`
- `tests/test_manifest.py`
- `README.md`
- `DATASET_CARD.md`

## 3. Manifest schema design

The Day 2 schema defines the shared metadata contract for clean, natural, TTS, and manipulated speech rows.

Required manifest columns:

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

Allowed values:

```text
source_type = natural / tts
split = train / val / test
```

All later experiments must use manifest-controlled splits. Scripts should not create ad hoc random train/test splits, because that can cause speaker, text, generator, or clean/manipulated-pair leakage.


## 3.1 Pre-Day-3 schema correction

Before real audio ingestion, the schema was corrected to separate provenance from attack state. `source_type` now means only `natural` or `tts`; manipulation is represented solely by `is_manipulated`. Two lineage fields were added: `pair_id` groups clean/manipulated counterfactual counterparts, while `source_sample_id` points manipulated samples to their clean source. Pair-level split integrity is validated to prevent clean/manipulated leakage across train/val/test. No Day 3 functionality was implemented in this correction.

## 4. Validation rules

`src/audiobookbench/data/manifest.py` implements:

- `load_manifest(path)`
- `validate_manifest(records)`
- `validate_record(record, row_index=None)`
- `save_manifest(records, path)`
- `normalize_bool(value)`
- `parse_float(...)`
- `parse_int(...)`

Validation checks include:

- required columns must exist;
- required core fields must be non-empty;
- `source_type` must be `natural` or `tts` and is independent of `is_manipulated`;
- `split` must be `train`, `val`, or `test`;
- `duration > 0`;
- `sample_rate > 0`;
- `position >= 0`;
- `segment_start < segment_end`;
- segment intervals must be inside `duration`;
- rows with `is_manipulated=true` must contain `attack_type`, `attack_start`, and `attack_end`;
- `attack_start < attack_end` when an attack interval is present;
- clean rows self-reference `source_sample_id == sample_id`;
- manipulated rows reference an existing clean `source_sample_id` in the same `pair_id` and split;
- a `pair_id` must never cross train/val/test splits.

## 5. Tests added

`tests/test_manifest.py` now checks:

1. loading `data/manifests/example_manifest.csv`;
2. successful validation of the corrected example manifest;
3. CSV roundtrip through `save_manifest()`;
4. missing required column failure, including lineage fields;
5. illegal `source_type` failure (`source_type` is only `natural` or `tts`);
6. illegal `split` failure;
7. manipulated row missing attack interval failure;
8. `segment_start >= segment_end` failure;
9. `attack_start >= attack_end` failure;
10. clean and manipulated counterparts may share the same `source_type`;
11. non-positive duration failure;
12. non-positive sample rate failure;
13. clean `source_sample_id` must self-reference;
14. manipulated `source_sample_id` must be distinct from the manipulated `sample_id`;
15. the same `pair_id` cannot cross train/val/test splits;
16. manipulated rows must reference an existing clean source sample;
17. referenced clean source must share the same `pair_id` and split.

## 6. Test result

Command run from repository root:

```bash
python -m pytest -q
```

Result:

```text
21 passed
```

The package is configured through `pyproject.toml` so pytest can import `src/audiobookbench` without manual `PYTHONPATH=src`. For standalone Python snippets outside pytest, run `pip install -e .` first, or run from an environment where the package is installed.

## 7. Known limitations

- Current `example_manifest.csv` is a schema/unit-test example only, not experimental evidence.
- No real audio pipeline has been implemented or validated yet.
- No real Week 1 manifest has been collected from actual audio files.
- No controlled manipulation dataset has been generated yet.
- No detection/localization baseline has been run yet.
- No real speaker embedding backend is configured yet.
- F0, pause ratio, and speech rate have not been validated on real audio.
- Legacy scripts remain legacy and must not be used for formal research claims.

## 8. Day 3 implementation plan

Day 3 should implement the real long-form audio pipeline:

1. Add a script or experiment entry point that scans a small `data/raw/` directory.
2. Load real audio with `load_audio()`.
3. Resample to the configured sample rate.
4. Segment each file with one fixed policy first, such as 5-second windows.
5. Save segment-level metadata using the Day 2 manifest schema.
6. Validate the generated manifest with `validate_manifest()`.
7. Add tests for segment-time alignment and metadata integrity.
8. Do not implement manipulation, detection, attribution, or adaptive attacks until the real audio manifest is reliable.

## 9. Day 2 status

Day 2 plus the pre-Day-3 schema correction is complete if `python -m pytest` passes from the repository root and the following snippet works:

```python
from audiobookbench.data.manifest import load_manifest, validate_manifest

records = load_manifest("data/manifests/example_manifest.csv")
validate_manifest(records)
```
