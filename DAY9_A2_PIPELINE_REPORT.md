# Day 9 A2 formal pipeline report

Date: 2026-09-06  
Status: **PASS**

## Scope

Day 9 is engineering/readiness only. Day 8 is PASS. No Day10 work, 23-case
production generation, detector evaluation, ASR/CER, similarity scoring, or
scientific metric was run. AISHELL-3 remained read-only; its generator-training
independence remains **UNKNOWN**.

## Frozen backend and CPU policy

- Source revision: `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`.
- Checkpoint: official CosyVoice2-0.5B revision
  `eec1ae6c79877dbd9379285cf8789c9e0879293d`, verified 12/12 by
  `results/day8/checkpoint_hashes.json`.
- All formal Day9 generation used the existing CPU-only, offline local path
  (`CUDA_VISIBLE_DEVICES=''`, Hugging Face/Transformers offline, Xet disabled).
  The RTX 4060 Laptop 8-GB GPU is recorded as `FAIL_OOM` for a full model load;
  this did not alter generator, checkpoint, text, reference, DSP, or protocol.

## Preregistered official smoke

The frozen first-sorted IDs were recorded before execution and run exactly once:

| Split | Paircase | Result | Retry |
| --- | --- | --- | --- |
| train | `paircase_0007` | PASS | 0 |
| val | `paircase_0018` | PASS | 0 |
| test | `paircase_0001` | PASS | 0 |

`results/day9/smoke.json` records `planned=3`, `passed=3`, and explicit
`failed=0`. Every case used its frozen exact transcript, target-speaker
reference, seed, clean sequence, and same checkpoint. No case was replaced.

## Pipeline and integrity evidence

- `experiments/day9_a2_pipeline/run.py` generated each natural-duration raw
  TTS waveform, resampled to mono 16 kHz, applied frozen silence trimming,
  active-RMS scalar matching, and 400-sample crossfade whole-utterance
  replacement, then serialized the final waveform.
- The additive sidecar is `results/day9/a2_sidecar.csv`; frozen Day2 manifests
  were not changed. It records exact text and hashes, source/reference lineage,
  checkpoint revision/hash, natural duration delta, clean/manipulated sample
  timelines, attack/core/blend bounds, attempt/status/failure fields, QA flags,
  and official-smoke status.
- `src/audiobookbench/security/a2_sidecar_validator.py` actually validated all
  three sidecar rows. Its execution artifact is
  `results/day9/sidecar_validator_result.json`: PASS, 3 passed, 0 failed.
- `src/audiobookbench/security/a2_waveform_gt_verifier.py` actually verified all
  three serialized waveforms and sample-first GT. Its execution artifact is
  `results/day9/waveform_gt_verifier_result.json`: PASS, 3 passed, 0 failed.
- Verifier checks include readable finite mono 16-kHz waveforms, non-empty and
  unclipped output, sidecar/sample-count consistency, 400-sample blend/core
  bounds, prefix preservation, suffix mapping after natural duration delta, and
  serialized-path lineage. Exact transcript equality/hashes, frozen reference
  provenance, and detector denylist separation passed. The generation pipeline
  makes no detector invocation, and attacker reference/speaker information is
  excluded from detector-facing payloads.

## Regression evidence and decision

- Relevant pytest: `tests/test_day8_a2_readiness.py` — **20 passed**.
- Research-assurance gate script: **123/123 passed** (script-style execution;
  it is not collected as normal pytest tests).
- Fresh Week1 verify-only: **696/696 PASS**, missing 0, mismatch 0.

**DAY9 = PASS.** The three independent required Day9 execution evidence classes
are present and PASS. Stop here: Day10 is not entered, no 23-case generation or
A2 metrics ran, and no scientific claims were added.
