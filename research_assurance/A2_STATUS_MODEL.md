# A2 Status Model (machine semantics, pre-registered)

Normalization of the status contract so that later automation cannot mistake a
QA observation for a generation failure, or a detector score for a failure
criterion. Transcribed from A2_FAILURE_TAXONOMY.md; no taxonomy change.

## 1. Fields

| Field | Allowed values | Meaning |
|---|---|---|
| generation_status | PLANNED \| SUCCESS \| FAILURE | outcome of the generation attempt for a planned case |
| generation_failure_reason | one of the 17 taxonomy classes or empty | machine-readable hard-failure cause |
| qa_flags | zero or more of the flag list | non-blocking observations, retained for context |

## 2. QA flag vocabulary (never failures)

- RMS_MATCH_FAIL — gain clamped and post-gain speech RMS still > 6 dB from reference
- DETERMINISM_MISMATCH — identical inputs/seed produced different outputs in the probe
- HIGH_CER — ASR CER above the diagnostic reporting threshold (ASR defines nothing)
- LOW_SPEAKER_SIMILARITY — reference/target similarity cosine below the diagnostic reporting threshold
- AUDIBLE_ARTIFACT — recorded observation, not a criterion
- UNUSUAL_PROSODY — recorded observation, not a criterion

## 3. Rules

1. `generation_status = FAILURE` is set **only** by a HARD_FAILURE class (15 of the 17 classes).
2. `RMS_MATCH_FAIL` → qa_flags only; it never changes generation_status.
3. `DETERMINISM_MISMATCH` → qa_flags + limitation disclosure; it does not block the pilot and does not change generation_status.
4. Detector and diagnostic outputs (AUROC, AUPRC, F1, B1, B2, B4, any score) are **never** failure criteria, never qa_flags, and never influence retention, ordering or regeneration.
5. Failed rows are retained; successful rows may also carry qa_flags.
6. Every report must show, per split and per speaker: planned, succeeded, failed-by-class, and qa-flag counts.

## 4. State transitions

```text
PLANNED --(hard failure class)--> FAILURE (row retained, reason recorded)
PLANNED --(valid output + verifications pass)--> SUCCESS (+ optional qa_flags)
SUCCESS --(never)--> FAILURE due to score, CER, similarity or artifact judgment
FAILURE --(never)--> silently dropped or replaced
```

## 5. Anti-patterns explicitly forbidden

- mapping RMS_MATCH_FAIL to generation_status=FAILURE;
- treating DETERMINISM_MISMATCH as a pilot blocker;
- filtering cases by CER, similarity, or any detector score;
- regenerating to "improve" a score (best_of_n and quality retry are forbidden by protocol);
- deriving labels from filenames instead of the sidecar.
