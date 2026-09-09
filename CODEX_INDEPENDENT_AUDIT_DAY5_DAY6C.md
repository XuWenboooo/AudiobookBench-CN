# CODEX DAY5–DAY6C INDEPENDENT AUDIT

**Gate: PASS, with one disclosed Day 6C audit-table correction.**

Audit date: 2026-09-05. Canonical repository: this repository. AISHELL-3 raw audio was opened read-only; representative regenerated files were written only to an automatically removed temporary directory.

## Scope and method

The audit read the Day 5/6A/6B/6C reports, configs, implementation, tests, manifests, frozen results and model provenance. Existing PASS text was not treated as evidence. Evidence came from full tests, independent SHA-256 calculation, code-path inspection and a separate representative reproduction entry.

## Required checks

| # | Check | Independent result |
|---:|---|---|
| 1 | Complete pytest | PASS: 163/163 before audit changes; 169/169 after portability and Week-1 freeze tests were added |
| 2 | Day 3–Day 6C frozen hashes | PASS: 696 files checked, zero missing/mismatch after the disclosed Day 6C correction |
| 3 | Day 5 temporal features | PASS: definitions and a 3,170-frame real-audio extraction reproduced |
| 4 | Day 6A train-clean-only reference | PASS: only `variant=clean, split=train` enters median/MAD |
| 5 | Day 6A test leakage | PASS: reference excludes val/test; thresholds use train manipulated only |
| 6 | Real ECAPA backend | PASS: SpeechBrain `EncoderClassifier`, local VoxCeleb checkpoint, CPU inference |
| 7 | No fake/random embedding | PASS: no mock/random research embedding path; NumPy randomness is limited to seeded bootstrap/tests |
| 8 | ECAPA checkpoint hash | PASS: `embedding_model.ckpt` = `0575CB64845E6B9A10DB9BCB74D5AC32B326B8DC90352671D345E2EE3D0126A2` |
| 9 | Speaker-disjoint 6/3/3 | PASS: train/val/test speakers are disjoint and counts are 6/3/3 |
| 10 | B1 does not use speaker ID | PASS: scoring accepts embeddings only; IDs are audit metadata |
| 11 | B1 does not use test enrollment | PASS: prototype is sequence-local; no enrollment input exists |
| 12 | B3 role | PASS: explicitly `B3_ORACLE`; requires paired clean embeddings |
| 13 | B4 role | PASS: explicitly `B4_DIAGNOSTIC`; energy-transient diagnostic only |
| 14 | C0 lineage | PASS: 23 cases; same speaker/split, different utterance, exact frozen target interval/tier |
| 15 | C0 waveform | PASS: all frozen verification rows pass; outside unchanged and inside changed |
| 16 | Bootstrap contrast direction | PASS: stored labels are `C0A_minus_A0` / `C0B_minus_A1`; negative means cross-speaker anomaly is higher |
| 17 | GT seconds axis | PASS: 184 projections checked; figures use sample bounds divided by 16 kHz on the same seconds axis |
| 18 | Speech mask label independence | PASS: fixed −45 dBFS pause-derived activity; function accepts no GT/label/attack input |
| 19 | Speech-mask population | PASS after audit fix: test/full positive retention 0.974–1.00; all split/GT slices 0.933–1.00; negative retention about 0.65–0.70 |
| 20 | Private-agent dependency | PASS: no formal code dependency on `.workbuddy`, temp venv or a user profile path |

The literal `.workbuddy/` string occurs only in a report discussion. A stray repository-root `%SystemDrive%` Windows-cache tree (four DB files) was found, has no references, and is not part of code/data/results; it remains non-canonical housekeeping material. Frozen manifests retain historical absolute paths for lineage, but Day 5/6B reads now prefer repository-relative paths and dataset access supports `AUDIOBOOKBENCH_DATASET_ROOT`.

## Independent reproduction

Command:

`py -3.14 experiments/week1_baseline/run.py --config configs/week1.yaml --reproduce-core --log results/week1/run.log`

| Link | Result | Independent evidence |
|---|---|---|
| Day 5 | PASS | `day45_test_SSB0139_seq000`, 3,170 frames, real Parselmouth F0; stored rounding tolerances met |
| Day 6A | PASS | 250 ms test AUROC exactly reproduced: A0 0.3312172437, A1 0.3496715140; reference TRAIN CLEAN ONLY |
| Day 6B | PASS | Real ECAPA fresh-vs-cached cosine 0.99999988; S2 B1b test AUROC exactly 0.9014214368 / 0.8966577027 |
| Day 6C C0 | PASS | `paircase_0001` C0A/C0B regenerated in temp; both WAV SHA-256 values exactly match frozen artifacts |
| Day 6C mask | PASS | S2/A0/test/full independently gives 38 positives, 685 negatives, positive retention 1.0, negative retention 0.659854 |

## Leakage and code-quality audit

- No train/val/test speaker overlap was found.
- No test data enter the Day 6A reference or Day 6A/6B thresholds.
- B1 uses no speaker label, enrollment or GT. B3 alone reads paired clean data and is correctly excluded from deployable claims.
- The speech-active mask is label-agnostic. GT is used only after scoring for evaluation/projection.
- NaNs remain explicit and are excluded from valid-feature aggregation. Zero MAD produces a degenerate/NaN channel instead of an inflated score; row normalization uses a `1e-12` guard.
- Seeds are frozen for figure selection/bootstrap. No hard-coded metric/result computation was found.
- Broad exceptions in Day 5 F0 are an intentional, named fallback whose selected backend is persisted. Day 6C donor probing was narrowed to expected I/O/value failures.
- Research pipelines can overwrite their own stage directory if invoked directly. The Week-1 entry is therefore verification-oriented and uses temporary output for reconstruction.
- S2/C0B strict-core bootstrap remains NaN for eight 0.75 s cases because those cases have no majority-positive strict-core window. This is documented and is not used as positive evidence.

## Audit fixes

1. Added missing `praat-parselmouth` to `requirements.txt`; made Torch and Torchaudio explicit optional speaker dependencies.
2. Day 5/6B now prefer repository-relative manipulated paths; Day 5 precheck/Day 6C honor `AUDIOBOOKBENCH_DATASET_ROOT`; Day 6B no longer falls back to a module-global repo root when rebuilding grids.
3. Replaced an ineffective bootstrap assertion ending in `or True` with a real config assertion.
4. Corrected Day 6C population-audit construction to filter each variant. The old table pooled A0+A1 into both labelled rows. `speech_mask_population_audit.csv` and its freeze hash were updated; B1 scores, AUROC/AUPRC/F1, masks, GT and waveforms were unchanged. Old hash: `D4C32E80...F99B`; corrected hash: `9886F17E...00FF`.
5. Added two portability regression tests and the Week-1 read-only reproduction entry.

## Dependency audit

`praat-parselmouth` is now in the main requirements. `requirements-speaker.txt` names SpeechBrain, Torch and Torchaudio and documents offline local model loading. The frozen historical backend record is SpeechBrain 1.1.1 / Torch 2.14.0+cpu / 192-d / 16 kHz. Independent reproduction used SpeechBrain 1.1.1 / Torch 2.13.0+cpu without downloading a model. The local checkpoint has model ID, VoxCeleb provenance and SHA-256 recorded in the freeze chain.

## Gate decision

The independently observed scientific chain agrees with the handoff after the population-table correction. The correction changes only variant-labelled audit counts/retention, tightens the range from the previously pooled 0.96–1.00 statement to 0.933–1.00 across all slices, and does not overturn the bounded claim that the mask retains most positive windows. Therefore the Day 5–Day 6C handoff is accepted for Week-1 freezing.
