# External Baseline Matrix v1 (Protocol-Hardening Draft)

Status: **DRAFT / NO BASELINE RUN AUTHORIZED**

This matrix records comparators to be specified before confirmatory execution. It is a planning artifact, not a result table.

| ID / paradigm | Paper / venue / year | Official code/checkpoint | Inputs / output / resolution | Raw scores / Whether-A | License / dataset | Hardware / difficulty | Scope |
|---|---|---|---|---|---|---|---|
| B1b/B4 — simple or local-context | internal historical implementation; commit/hash TBD | internal wrapper only | project-specific; raw output TBD | TBD | repository license | TBD | CORE / internal |
| BAM — boundary-aware | [paper](https://arxiv.org/abs/2407.21611), 2024 | [official repo](https://github.com/media-sec-lab/BAM), HEAD `55f3fb9`; checkpoint via linked Google Drive | frame-level localization; exact input/output TBD | raw scores likely inspectable; Whether-A TBD | repository API reports no license; redistribution blocked pending author clarification | Python 3.8, ~4GB GPU stated; MODERATE | CORE candidate |
| CFPRF — proposal-based | [ACM MM 2024 paper](https://arxiv.org/abs/2407.16554) | [official repo](https://github.com/ItzJuny/CFPRF); checkpoints via Google Drive | frame detector + refined proposals | raw scores/output files documented; Whether-A TBD | MIT | Python 3.8, legacy CUDA stack; HIGH | CORE candidate |
| SAL — segment-aware | [ICASSP 2026 paper](https://arxiv.org/abs/2601.21925) | [official repo](https://github.com/SentryMao/SAL), HEAD `b4e80d1`; checkpoint availability TBD | frame localization; default 160 ms stated | raw outputs/evaluator require inspection; Whether-A TBD | MIT confirmed by repository metadata | Python 3.10, Lightning/Hydra; MODERATE | CORE candidate |
| TRACE — training-free trajectory | [CVPRW 2026 paper](https://openaccess.thecvf.com/content/CVPR2026W/MMFM5/html/khan_TRACE_Training-Free_Partial_Audio_Deepfake_Detection_via_Embedding_Trajectory_Analysis_CVPRW_2026_paper.html) | matching official audio-forensics repo/checkpoint not verified | trajectory-based detection; localization output TBD | raw scores/localization not verified | license not verified | TBD | STRETCH / UNVERIFIED |

Acceptance rules:

- Baselines must be selected before inspecting confirmatory outcomes.
- Differences in data, preprocessing, compute, and tuning access must be disclosed.
- External results are not copied into the primary analysis without a compatible evaluation definition.
- Core must contain at least 4 distinct paradigms, not merely four model
  checkpoints. Each row must be verified from the primary paper/repository
  before lock; unverified rows are not evidence.
- Current provenance status: BAM, CFPRF, and SAL are verified source-level
  candidates; B1b/B4 is an internal candidate. No row has been executed.
