# AudiobookBench-CN

Open research code and protocol materials for temporal security evaluation of
long-form generative speech. This public release includes source code,
configuration, manifests, test fixtures, documentation, and research-assurance
materials. It intentionally excludes audio, source datasets, generated results,
model checkpoints, and local environments.

## Reproducibility and data policy

- Obtain datasets and model weights directly from their original licensors.
- Local paths, generated audio, pretrained assets, and run outputs are ignored
  by Git and are not distributed in this repository.
- Some frozen historical records retain their original local paths so recorded
  hashes remain auditable; configure your own dataset location before running a
  workflow.
- Third-party model repositories are deliberately not bundled. Obtain them
  independently and comply with their respective licenses.
- Research claims and frozen protocol decisions are documented in the root
  reports and `research_assurance/`. Consult those documents before interpreting
  or extending experimental workflows.
- This repository is released under the [MIT License](LICENSE).

**Primary track:** Temporal Security and Forensics for Long-form Generative Speech.

**Secondary track:** Temporal Responsible Evaluation of Long-form TTS.

This integrated starter repository keeps the previous scripts under `legacy/` and provides a cleaner structure for Week 1. The current goal is not to claim benchmark-level results, but to build a real-audio pipeline, a formal threat model, and a minimal detection/localization baseline.

## Week 1 target

```text
Real long-form audio
  -> controlled localized manipulation
  -> temporal feature extraction
  -> segment-level anomaly score
  -> detection / localization metrics
```

## Key deliverables

- `AUDIT.md`
- `THREAT_MODEL.md`
- `DATASET_CARD.md`
- `results/security/week1/metrics.json`
- `results/security/week1/segment_scores.csv`
- `results/security/week1/figures/`

## Important rule

Do not use mock/random/synthetic-demo outputs as formal research evidence. Unit tests may use tiny synthetic arrays, but final claims must be based on real audio and documented protocols.

## Day 2 manifest protocol

The shared data protocol is now defined in `configs/manifest_schema.yaml` and implemented in `src/audiobookbench/data/manifest.py`.

Example usage:

```python
from audiobookbench.data.manifest import load_manifest, validate_manifest

records = load_manifest("data/manifests/example_manifest.csv")
validate_manifest(records)
```

`data/manifests/example_manifest.csv` is only a schema example for unit tests. It is not real experimental evidence. Day 3 should replace this with manifests generated from actual audio files.

Before Day 3, the schema was corrected so `source_type` records only the base source (`natural` or `tts`), while `is_manipulated` independently records manipulation state. `pair_id` groups clean/manipulated counterparts and `source_sample_id` records lineage; one `pair_id` must never cross train/val/test splits.

## Day 3 real-audio ingestion

Day 3 adds a deterministic clean-audio ingestion pipeline. The repository still does **not** bundle real research audio, so Day 3 engineering is complete while the real-data gate remains pending until actual audio is supplied.

1. Copy `data/manifests/source_audio_template.csv` to `data/manifests/source_audio.csv`.
2. Replace the placeholder rows with real natural/TTS audio paths and explicit metadata.
3. Run:

```bash
python -m audiobookbench.data.prepare_audio \
  --catalog data/manifests/source_audio.csv \
  --output data/manifests/week1_manifest.csv \
  --target-sr 16000 \
  --window-seconds 5.0 \
  --min-tail-seconds 1.0
```

The generated manifest stores the original audio path plus time-aligned segment boundaries; it does not duplicate audio files. Additional diagnostic columns include original sample rate/channels, segment duration, energy-VAD voiced ratio, RMS, and peak amplitude.

The current energy VAD is explicitly a **sanity baseline**, not a validated production VAD. Unit tests generate tiny deterministic WAV fixtures only to test code behavior; those fixtures are not research evidence.
