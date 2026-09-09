# AudiobookBench-CN Week-1 Freeze

Freeze date: 2026-09-05  
Week-1 gate: **PASS**  
Independent Day 5–Day 6C audit: **PASS with disclosed audit fixes**  
Git commit: **NOT AVAILABLE** (the canonical directory has no `.git` metadata)

## Frozen experiment chain

Threat Model → real AISHELL-3 → constructed long-form → controlled A0/A1 manipulation → Day 5 temporal features → Day 6A B0 negative result → Day 6B ECAPA B1 positive signal → Day 6C same-speaker control → Day 6C conditional speech-active audit → bounded Week-1 conclusion.

No Week-2 experiment, TTS attack, new detector, supervised model, new feature, new data or hyperparameter tuning is included.

## Frozen data/protocol counts

- 12 speakers; train/val/test = 6/3/3 speaker-disjoint.
- 480 AISHELL-3 source utterances; raw source read-only.
- 24 constructed clean long-form sequences.
- 23 paired targets; 23 A0 + 23 A1.
- 23 C0A + 23 C0B same-speaker controls.
- Day 5: 70 waveforms and 224,566 frames at 16 kHz, 25 ms / 10 ms.

## Frozen configs and reports

Configs: `manifest_schema.yaml`, `day3_audio.yaml`, `day3_aishell3_pilot.yaml`, `day35_constructed_longform.yaml`, `day4_manipulation_v2.yaml`, `day45_expanded_paired.yaml`, `day6a_localization_baseline.yaml`, `day6b_speaker_consistency.yaml`, `day6c_confound_controls.yaml`, `week1.yaml`.

Reports: Day 1/2/3/3.5/4/4.5 canonical reports, `DAY5_PRECHECK.md`, `DAY5_TEMPORAL_SIGNAL_REPORT.md`, `DAY6A_NONTRAINED_LOCALIZATION_REPORT.md`, `DAY6B_PRECHECK.md`, `DAY6B_SPEAKER_CONSISTENCY_REPORT.md`, `DAY6B_FREEZE.md`, `DAY6B_CLAIM_ADDENDUM.md`, `DAY6C_CONFOUND_CONTROL_REPORT.md`, `DAY6C_INTEGRITY_CORRECTION.md`, `CODEX_INDEPENDENT_AUDIT_DAY5_DAY6C.md`, and `WEEK1_REPORT.md`.

## Frozen backend

- Backend: SpeechBrain ECAPA-TDNN, `speechbrain/spkrec-ecapa-voxceleb`.
- Provenance: VoxCeleb pretrained, inference-only.
- Input/output: 16 kHz, 192-dimensional embedding, CPU.
- Historical Day 6B environment: SpeechBrain 1.1.1, Torch 2.14.0+cpu.
- Independent audit environment: SpeechBrain 1.1.1, Torch 2.13.0+cpu, Torchaudio 2.11.0.
- ECAPA embedding checkpoint SHA-256: `0575CB64845E6B9A10DB9BCB74D5AC32B326B8DC90352671D345E2EE3D0126A2`.
- Independent fresh-vs-cached representative embedding cosine: 0.99999988.

## Frozen core results

- Day 6A: every observed AUROC is below 0.5; 250 ms test A0/A1 = 0.331217/0.349672. This is a negative result, with no significance claim.
- Day 6B: S2 B1b test A0/A1 AUROC = 0.901421/0.896658, AUPRC = 0.453843/0.491193, F1 = 0.506329/0.506329. B1 is a strong temporal signal, not a solved high-precision deployable localizer.
- B3 remains ORACLE ONLY. B4 remains DIAGNOSTIC ONLY.
- Day 6C: S1 core anomaly A0/A1 = 0.729014/0.731642 versus C0A/C0B = 0.365902/0.365906. C0 has no usable positive localization signal.
- Day 6C speech-active results are conditional on the retained population and must be paired with unmasked results. Test/full positive retention is 0.974–1.00; all split/GT slices span 0.933–1.00.
- Clean transition audit: 144 peaks, median distance 0.094 s, 97.2% within 1 s of a constructed utterance boundary.
- Duration: 2.5 s is easiest; 0.75 s has poor precision; S2/A1 0.75 s strict-core evaluation has no majority-positive window.

## Integrity correction frozen at Week 1

The independent audit found that `speech_mask_population_audit.csv` pooled A0 and A1 into each variant-labelled population row. The generator now filters the requested variant, the table was corrected, and a regression assertion ties each row to `original_vs_masked_metrics.csv`.

- Old population-audit SHA-256: `D4C32E80CBD8379F441B552039B330F0571547E46B34D8EEB1CB68474595F99B`.
- Week-1 corrected SHA-256: `9886F17E181DEA57180FEA79F9DB6782859F6A5389F842A4B8C15FF0E1C900FF`.
- Unchanged: masks, scores, AUROC/AUPRC/F1, GT, embeddings, attack/C0 waveforms and scientific direction.

## Hash and reproduction status

- Frozen chain: 696 SHA-256 checks, zero missing, zero mismatch.
- Group coverage: Day 3 (4), Day 3.5 (14), Day 4 (21), Day 4.5 outputs (70), raw sources (480), Day 5 (13), Day 6A (16), Day 6B (15), Day 6C (17), C0 audio (46).
- Core reproduction: Day 5 PASS; Day 6A PASS; Day 6B PASS; Day 6C C0 PASS; Day 6C speech-mask audit PASS.
- Final pytest: **169 passed / 0 failed**; one non-fatal SpeechBrain Windows symlink warning.
- Detailed hashes: `results/week1/hashes.json`.
- Reproduction log: `results/week1/run.log`.

## Reproduction entry

Verify only:

`python experiments/week1_baseline/run.py --config configs/week1.yaml --verify-only`

Representative core reproduction:

`python experiments/week1_baseline/run.py --config configs/week1.yaml --reproduce-core`

Both modes reuse frozen intermediates. Core reconstruction uses a temporary directory and never overwrites formal Day 3–Day 6C results.

## Frozen claim boundary

Supported and unsupported claims are exactly those in `results/week1/claims.md`. Any claim about native audiobooks, TTS, unseen generators, adaptive attackers, universal forensics, perception, deployment readiness or pure speaker-identity causality remains outside Week 1.
