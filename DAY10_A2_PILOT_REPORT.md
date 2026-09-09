# Day 10 formal 23-case A2 pilot generation and freeze

Date: 2026-09-06  
Status: **PASS**

## Scope and frozen execution

Day 9 prerequisite is PASS. Day 10 processed the preregistered 23-case A2
population in `paircase_0001` through `paircase_0023` order. The pre-generation
record is `results/day10/frozen_case_list.csv`; it records index, paircase,
split, target speaker/source sample, frozen reference, exact transcript, and
seed. Seeds are the encoded `20260905 + i` sequence.

The split is 11 train / 6 val / 6 test, with 6 / 3 / 3 speakers (12 total).
All work used CPU and the offline, official CosyVoice2-0.5B checkpoint at
revision `eec1ae6c79877dbd9379285cf8789c9e0879293d` (12/12 Day8-verified).
GPU full-model use on the RTX 4060 Laptop 8GB remains `FAIL_OOM`; no GPU
optimization was attempted. AISHELL-3 stayed read-only and its training
independence remains **UNKNOWN**.

## Outcome-blind accounting and integrity

All 23 cases were processed exactly once in frozen order: succeeded 23,
`failed_by_class={}`, retries 0, replacements 0. Thus `23 + 0 = 23` and the
denominator accounting is PASS. No output was filtered, rerolled, substituted,
or selected by quality, duration, ASR/CER, similarity, or detector behavior.

The canonical sidecar is `results/day10/a2_sidecar.csv`. It preserves exact
text and hashes, source/reference lineage, generator/checkpoint provenance,
attempt/status/QA fields, natural synthetic duration/delta, sample-first
attack/core/blend bounds, and clean/manipulated timelines. Each successful
waveform is serialized under `results/day10/waveforms/`.

- Sidecar validation: PASS, 23/23.
- Waveform and GT validation: PASS, 23/23.
- Exact-text identity, dual timelines/sample-first GT, 400-sample blends,
  prefix preservation, suffix mapping, and detector-leakage separation: PASS.
- `results/day10/day10_output_hashes.json` freezes all final waveform paths,
  sizes, SHA-256 values, checkpoint-manifest identity, and canonical artifact
  hashes. `data/generated/a2_day10_pilot_freeze.json` is only the standard
  generated-data index pointing to those canonical artifacts, not a second
  provenance schema.

## Regression and boundary evidence

- Relevant pytest: `tests/test_day8_a2_readiness.py` — **20 passed**.
- Week2A gate-check script contracts: **123/123 passed**.
- Fresh Week1 verify-only: **696 matched, 0 missing, 0 mismatch, PASS**.

The direct live gate command could not independently declare a PASS in this
environment because PyYAML is unavailable and its retained Day8/Day9 declared
configuration is HOLD despite their closed execution evidence. This is an
environment/legacy-registry limitation, not a Day10 artifact failure; no gate
design or prior closed state was changed.

No detector scoring, A2 metrics, thresholding, or scientific claims were run.
**DAY10 = PASS.** Stop here; Day11 has not been entered.
