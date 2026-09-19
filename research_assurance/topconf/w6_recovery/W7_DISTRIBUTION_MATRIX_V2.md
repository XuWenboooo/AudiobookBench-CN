# W7 Recovery Distribution Matrix v2

Audit date: `2026-09-19`
Status: `PARALLEL-RECOVERY-EVIDENCE-UPDATED / NO W7 SCIENTIFIC INFERENCE`

AISHELL-1 and AliMeeting are not external partial-deepfake distributions and
are excluded from this matrix. Dataset readiness is determined only by source,
legal use, audio/GT/integrity/identity and adapter evidence; no detection or
localization outcome was used.

| DATASET | OFFICIAL SOURCE | LICENSE | AUDIO | TEMPORAL GT / SEMANTICS | IDENTITY / SPLIT | ADAPTER | INTEGRITY | EVALUATOR | READINESS | BLOCKER |
|---|---|---|---|---|---|---|---|---|---|---|
| PartialEdit v1.1 E1 | Zenodo `18829689`; project page | CC BY 4.0; local research use recorded | 42,471 WAV materialized | edited-region start/end seconds; E1 | official train/dev/eval and speaker metadata | PASS | PASS; official CSV/WAV binding, no missing/extra/duplicate | PASS | READY | none |
| PartialSpoof v1.2 eval | Zenodo `5766198`; official repository | CC BY 4.0 / acknowledgement chain | official 5.8 GB archive is under resumable recovery; smaller official metadata archives are materialized | VAD timestamps and segment labels available | official eval protocol and speaker metadata | labels/VAD parser PASS; full adapter pending | archive MD5 `79c7c834d0d9979ecd374a98a059ea19` pending | pending full archive | NOT_READY | official archive transfer not yet closed |
| LlamaPartialSpoof v1.0.b | official HF dataset / project repository | CC BY 4.0 as recorded | only `.utt/.spk` metadata cached locally; audio absent | segment intervals in labels, not audio-bound locally | split metadata present | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NOT_READY | no local audio archive; GitHub recovery attempt failed to connect |
| HAD | Zenodo `10377492`; Interspeech 2021 source | rights decision incomplete | 8.1 GB archive not materialized | paper describes localization; local field binding not audited | official protocol not frozen locally | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NOT_READY | archive unavailable; license/GT/adapter unresolved |
| MIST | official paper and HF dataset card | Research Only / rights not cleared | source advertised; no local materialization | multi-region claim; exact local schema not audited | split not frozen | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NOT_READY | rights and integrity/adapter evidence incomplete |
| HQ-MPSD | third-party derivative audit artifact | not adopted | unknown | unknown | unknown | NOT_ACCEPTED | NOT_RUN | NO | NOT_READY | not an authoritative official dataset release |

## Counts

```text
TOTAL_EXTERNAL_CANDIDATES = 6
READY_EXTERNAL_DISTRIBUTIONS = 1
BLOCKED_EXTERNAL_DISTRIBUTIONS = 5
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
RESULT_BASED_DATASET_SELECTIONS = 0
```

## Recovery ledger

```text
2026-09-19 PartialSpoof official recovery: resumed directly from the official Zenodo content URL; final size/MD5 and archive adapter remain pending.
2026-09-18 LlamaPartialSpoof official repository clone: failed to connect to github.com:443.
No dataset was promoted to READY because of a model score, metric, threshold, aggregation, or expected performance.
```
