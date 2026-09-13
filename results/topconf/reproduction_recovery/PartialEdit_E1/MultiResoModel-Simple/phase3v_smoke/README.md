# Phase3V MultiResoModel-Simple bounded smoke evidence

This directory records the authorized functional smoke only. It is not a
benchmark result and contains no ground-truth access, metric, ranking,
threshold, calibration, smoothing, or selection output.

## Frozen inputs

- `research_assurance/topconf/PHASE3V_SMOKE_SAMPLES_V1.txt`
- PartialEdit v1.1 E1, manifest-order first three cases:
  `p225_001_edited_partial_16k.wav`, `p225_002_edited_partial_16k.wav`,
  `p225_003_edited_partial_16k.wav`
- mono PCM16, 16 kHz; three samples only

## Load and forward

- MultiResoModel-Simple repository commit:
  `0f69db3a2d654de47822d951fe6ad256bbaac9ba`
- checkpoint: `baseline-ps-e55.tgz`, expected size and SHA256 both passed
- loader: fairseq 0.12.2 with a lifecycle-compatible architecture build
  followed by `strict=True` state-dict load
- missing keys: 0; unexpected keys: 0
- device: NVIDIA GeForce RTX 4060 Laptop GPU, CUDA torch 1.13.1+cu117
- forward wall time: 3.5845 s for the three-sample batch
- peak allocated VRAM: 1,872,419,840 bytes

## Raw temporal output

All six repository-defined units were finite for all three samples:
`0.02`, `0.04`, `0.08`, `0.16`, `0.32`, and `0.64` seconds. The raw output
keeps the repository's two-class values; the schema dry mapping exposes
class-1 as `frame_scores` and maps index `i` at unit `u` to
`frame_times=[i*u, min((i+1)*u, audio_duration)]`. No score transformation
was applied.

This is a functional baseline-path smoke and does not authorize Phase3T
execution, Phase4 review, or confirmatory experiments.
