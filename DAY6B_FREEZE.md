# Day 6B Freeze Record

Frozen at: 2026-09-05T12:04:22 (before any Day 6C experiment)

Machine-readable record (all SHA256): `results/day6c/day6b_freeze_record.json`

## Frozen files

| File | SHA256 (first 16) |
|---|---|
| `configs/day6b_speaker_consistency.yaml` | 01769BE242FF1AA5 |
| `DAY6B_PRECHECK.md` | D9D665F4DA2FC32A |
| `DAY6B_SPEAKER_CONSISTENCY_REPORT.md` | 8166F265ECE1E21A |
| `results/day6b/metrics.json` | 087F6758F1893488 |
| `results/day6b/speaker_scores.csv` | D7EFA66354A01E8A |
| `results/day6b/bootstrap_ci.csv` | ADA95697F9FE167B |
| `results/day6b/paired_analysis.csv` | F1097D39DF964C5F |
| `results/day6b/zone_audit.csv` | (full hash in record) |
| `results/day6b/run_summary.json` | (full hash in record) |
| `results/day6b/embedding_backend.json` | (full hash in record) |
| ECAPA `embedding_model.ckpt` (83,316,686 B) | (full hash in record) |
| ECAPA `classifier.ckpt` (5,534,328 B) | (full hash in record) |
| ECAPA `mean_var_norm_emb.ckpt` | (full hash in record) |
| ECAPA `label_encoder.ckpt` | (full hash in record) |
| ECAPA `hyperparams.yaml` | (full hash in record) |

## Backend state at freeze

- speechbrain 1.1.1, torch 2.14.0+cpu, model `speechbrain/spkrec-ecapa-voxceleb`
- embedding dim 192, expected sample rate 16 000 Hz, device CPU, offline local load
- pytest at freeze: **130 passed / 0 failed**

Day 6C may not overwrite any Day 6B result. The freeze record is re-verified
at the end of Day 6C (`test_day6b_results_unchanged`).
