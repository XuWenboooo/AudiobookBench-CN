# Artifact Index — Week 1

Legend — Stage: D3/D3.5/D4/D4.5/D5/D6A/D6B/D6C/W1. Status: FROZEN (hash-
guarded) / RECORD (point-in-time hash record) / WORKING. Relevance:
P = paper, R = reproduction, A = audit.

## Data & manifests (large sets listed as registry, not per-file)

| Artifact | Stage | Purpose | Status | Hash | P/R/A |
|---|---|---|---|---|---|
| `datasets/AISHELL-3/` (480 pilot utterances; 88k corpus) | source | real speech, read-only | FROZEN (source_input_hashes, 480) | ✓ in week1 chain | P,R,A |
| `data/manifests/day45_source_audio.csv` | D4.5 | source utterance registry | FROZEN | ✓ | P,R |
| `data/manifests/day45_longform_manifest.csv` (208 rows) | D3.5 | construction lineage incl. utterance boundaries | FROZEN | ✓ | P,R,A |
| `data/manifests/day45_attack_manifest.csv` | D4.5 | GT: target/attack/core/blend sample bounds | FROZEN | ✓ | P,R,A |
| `data/generated/day45_paired/` (70 WAVs + metadata) | D4.5 | clean/A0/A1 audio | FROZEN (70) | ✓ | P,R |
| `data/generated/day6c_same_speaker_control/` (46 WAVs) | D6C | C0 controls | FROZEN (46) | ✓ | P,R |
| `data/manifests/day6c_same_speaker_control_manifest.csv` | D6C | C0 lineage | FROZEN | ✓ | P,R,A |

## Configs

| Artifact | Stage | Purpose | Status | Notes |
|---|---|---|---|---|
| `configs/week1.yaml` | W1 | Week-1 entry | FROZEN | in 696 chain |
| `configs/day6a_localization_baseline.yaml` (+copy in results/day6a) | D6A | B0 protocol | FROZEN | equality unit-tested |
| `configs/day6b_speaker_consistency.yaml` | D6B | grids/trim/thresholds | FROZEN | hash in day6b_freeze_record |
| `configs/day6c_confound_controls.yaml` | D6C | executed-values record | FROZEN | unit-tested |
| `configs/day3_audio.yaml`, `day3_aishell3_pilot.yaml`, `day35_constructed_longform.yaml`, `day4_manipulation_v2.yaml`, `day45_expanded_paired.yaml`, `manifest_schema.yaml` | D3–D4.5 | data protocols | FROZEN | in 696 chain |

## Results — Day 5

| Artifact | Purpose | Status | P/R/A |
|---|---|---|---|
| `results/day5_validation/day5_frame_metadata_{clean,a0,a1}.csv` (224,566 rows) | frozen frame features | FROZEN (13 files) | R,A |
| `results/day5_validation/day5_sequence_summary.csv` | per-record identity/duration | FROZEN | P,R |
| `results/day5_validation/day5_precheck.json` etc. | validation records | FROZEN | A |
| `results/day5_debug_figures/` (5 PNG) | sanity trajectories | FROZEN | A |

## Results — Day 6A

| Artifact | Purpose | Status | P/R/A |
|---|---|---|---|
| `results/day6a/metrics.json` | B0 full metric matrix | FROZEN (16 files) | P,R,A |
| `results/day6a/aggregated_features.csv`, `anomaly_scores.csv` | window features/scores | FROZEN | R |
| `results/day6a/config.yaml` | frozen config copy | FROZEN | A |
| `DAY6A_NONTRAINED_LOCALIZATION_REPORT.md` | canonical report (restored) | RECORD | P |

## Results — Day 6B

| Artifact | Purpose | Status | P/R/A |
|---|---|---|---|
| `results/day6b/metrics.json` | B1/B2/B3/B4 matrix | FROZEN (15 files) | P,R,A |
| `results/day6b/embeddings/*.npy` (140) | frozen ECAPA embeddings | FROZEN | R |
| `results/day6b/embedding_manifest.csv`, `embedding_backend.json` | embedding provenance | FROZEN | P,R,A |
| `results/day6b/bootstrap_ci.csv`, `paired_analysis.csv`, `zone_audit.csv` | signal analyses | FROZEN | P |
| `results/day6b/figures/` (5 PNG) | sanity figures | FROZEN | A |
| `pretrained/spkrec-ecapa-voxceleb/` | ECAPA checkpoints | FROZEN (ckpt SHA-256 pinned in freeze) | P,R,A |
| `DAY6B_*` reports + `DAY6B_CLAIM_ADDENDUM.md` | canonical records | RECORD | P |

## Results — Day 6C

| Artifact | Purpose | Status | P/R/A |
|---|---|---|---|
| `results/day6c/original_vs_masked_metrics.csv` | original vs conditional metrics | FROZEN (17) | P,R,A |
| `results/day6c/speech_mask_population_audit.csv` | **corrected** variant-filtered audit | FROZEN (corrected hash 9886F17E…) | P,A |
| `results/day6c/cross_vs_same_speaker.csv` | per-case cross/same core anomaly | FROZEN | P,R,A |
| `results/day6c/bootstrap_ci.csv` | case-level CIs (direction-explicit contrasts) | FROZEN | P,R |
| `results/day6c/case_level_metrics.csv`, `peak_localization_errors.csv` | case-level view | FROZEN | P |
| `results/day6c/clean_transition_audit.csv` | C4 transition mechanism | FROZEN | P,R,A |
| `results/day6c/gt_axis_audit.json`, `day6b_freeze_record.json`, `day6a_frozen_record.json`, `day5_output_hashes.json`, `day6c_final_hashes.json` | protection/audit records | RECORD | A |
| `results/day6c/embeddings/*.npy` (92) | C0 embeddings | FROZEN | R |
| `results/day6c/figures/` (5 PNG, seconds-axis) | sanity figures | FROZEN | A |

## Week 1 closeout (Codex)

| Artifact | Purpose | Status | P/R/A |
|---|---|---|---|
| `WEEK1_REPORT.md`, `WEEK1_FREEZE.md` | canonical closeout | FROZEN | P,A |
| `results/week1/metrics_summary.csv` | curated numbers | FROZEN | P,R |
| `results/week1/hashes.json` | 696-entry frozen chain | FROZEN | A |
| `results/week1/claims.md`, `limitations.md` | claim boundary | FROZEN | P |
| `results/week1/figures/` (5 PNG) | paper candidates | FROZEN | P |
| `results/week1/reproduction_manifest.json`, `run.log` | reproduction evidence | FROZEN | R |
| `CODEX_INDEPENDENT_AUDIT_DAY5_DAY6C.md`, `WEEK1_RETROSPECTIVE.md`, `AGENT_WEEK1_CONTINUITY_REVIEW.md` | audit trail | RECORD | A |
| `DAY6C_INTEGRITY_CORRECTION.md`, `DAY6B_FREEZE.md`, `DAY6B_CLAIM_ADDENDUM.md`, `DAY6C_CONFOUND_CONTROL_REPORT.md` | correction/claim records | RECORD | A |

Excluded by design: `results/day8/`, `.venv-cosyvoice/`,
`third_party/CosyVoice/` — owned by Day-8 Codex; read-only to this audit.
