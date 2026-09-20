# W7 Recovery Distribution Matrix v2

Audit date: `2026-09-21`
Status: `SECOND-DISTRIBUTION-CLOSED / NO W7 SCIENTIFIC INFERENCE`

AISHELL-1 and AliMeeting are not external partial-deepfake distributions and
are excluded from this matrix. Dataset readiness is determined only by source,
legal use, audio/GT/integrity/identity and adapter evidence; no detection or
localization outcome was used.

| DATASET | OFFICIAL SOURCE | LICENSE | AUDIO | TEMPORAL GT / SEMANTICS | IDENTITY / SPLIT | ADAPTER | INTEGRITY | EVALUATOR | READINESS | BLOCKER |
|---|---|---|---|---|---|---|---|---|---|---|
| PartialEdit v1.1 E1 | Zenodo `18829689`; project page | CC BY 4.0; local research use recorded | 42,471 WAV materialized | edited-region start/end seconds; E1 | official train/dev/eval and speaker metadata | PASS | PASS; official CSV/WAV binding, no missing/extra/duplicate | PASS | READY | none |
| PartialSpoof v1.2 eval | Zenodo `5766198`; official repository | CC BY 4.0 / acknowledgement chain | official archive closed: 71,237 WAV; 16 kHz mono; all headers decode | archive `eval.lst` has 71,239 IDs; two IDs have no WAV and no matching materialized GT entry | official eval protocol and speaker metadata | parser/schema evidence present, frozen adapter blocked by two official list/audio mismatches | MD5 `79c7c834d0d9979ecd374a98a059ea19` PASS; size `5,803,817,500` PASS | GT binding incomplete | NOT_READY | `CON_E_0034982` and `CON_E_0058039` are absent from the official archive audio |
| LlamaPartialSpoof v1.0.b / R01TTS.0.b | Zenodo `14214149`; official project record | CC BY 4.0 | 64,388 WAV; 16 kHz mono; all members decode; official MD5 and size pass | 64,388 unique temporal GT rows; 464,714 ordered segments; zero-length bonafide markers are deterministic no-ops | official package identity and record version are frozen | PASS; official SAL parser grammar and semantics confirmed | PASS; 12,791,859,200 bytes, MD5 `a4de860a845816fa65785dddd7849700`; tar inventory complete | PASS | READY | none |
| HAD | Zenodo `10377492`; Interspeech 2021 source | CC BY 4.0 (Zenodo record) | official `HAD.zip` materialized at `8,073,665,280` bytes, but MD5 `6fd23321b03abef5dac6ba7c26c3196d` mismatches official `4daef62a7cf20c71b052635c968ece1c`; ZIP central directory reads but streaming CRC/decompression fails | paper/repository describe localization; local archive integrity is not closed | official protocol not frozen locally | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NOT_READY | fail-closed after official-size download: checksum and ZIP content integrity failure |
| MIST | official paper and HF dataset card | Research Only / rights not cleared | source advertised; no local materialization | multi-region claim; exact local schema not audited | split not frozen | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NOT_READY | rights and integrity/adapter evidence incomplete |
| HQ-MPSD English | Zenodo `17929533`, official `English.zip` | CC BY 4.0 | official-size local transfer `3,204,831,988` bytes; MD5 `0d007ce820e7a7d3300f72662447668b` mismatches official `c89346355d9afb0ba8dca4247c35dbe6`; ZIP central directory unreadable | official record describes 30 ms frame labels, but local archive integrity is not closed | language pack identity is official; audio/GT binding not audited after integrity failure | NOT_IMPLEMENTED | FAIL | NOT_READY | NOT_READY | repeated incomplete/reset Range transfers; fail-closed |

## Counts

```text
TOTAL_EXTERNAL_CANDIDATES = 6
READY_EXTERNAL_DISTRIBUTIONS = 2
BLOCKED_EXTERNAL_DISTRIBUTIONS = 4
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
RESULT_BASED_DATASET_SELECTIONS = 0
```

## Recovery ledger

```text
2026-09-19 PartialSpoof official recovery: official archive size and MD5 closed; isolated extraction and full WAV-header scan passed; two entries in the archive's own eval.lst have no corresponding audio/GT and therefore block READY promotion.
2026-09-19 HAD fallback recovery: official-size range download completed, but MD5 mismatched the Zenodo record and ZIP streaming integrity failed; HAD remains NOT_READY.
2026-09-20 HQ-MPSD fallback recovery: official English pack reached the advertised size, but MD5 mismatched and the ZIP central directory was unreadable after repeated incomplete/reset Range transfers; HQ-MPSD remains NOT_READY.
2026-09-21 LlamaPartialSpoof official Zenodo `1.0.b` / `R01TTS.0.b` recovery: official size and MD5 pass; the tar inventory, all 64,388 WAV decodes, duration alignment, and one-to-one audio/GT identity pass; official SAL parser compatibility confirmed. Promoted to READY without outcome access.
No dataset was promoted to READY because of a model score, metric, threshold, aggregation, or expected performance.
```
