# W7 case manifest rebuild audit v1

Decision: `POPULATION_SEMANTIC_EQUIVALENCE = PASS`.

The old metadata skeleton contained 106,859 logical source/GT cases. The new
manifest preserves exactly those logical keys and deterministically expands
each into the four already frozen conditions, producing 427,436 condition
rows. No case was added, removed, or selected by outcome.

The final manifest is [`W7_FINAL_CASE_MANIFEST_V2.jsonl.gz`](W7_FINAL_CASE_MANIFEST_V2.jsonl.gz)
with SHA-256:

```text
BEA3EB3E31F1A81219617D6994ACD3381C99B972300020C4B781B8FB878DE572
```

Every row has a `w7case_` deterministic ID and the required fields from
`w7_preparation/CASE_IDENTITY_SCHEMA_V1.json`. The validation found 427,436
unique row IDs, 106,859 logical cases, and exactly one row for each of
`clean`, `mechanism_shift`, `codec`, and `resampling` per logical case.

Clean rows bind actual source audio SHA-256 values. The other 320,577 rows do
not claim bytes that do not yet exist: their `audio_artifact_id` identifies a
deterministic derivation and their hash is explicitly a
`DERIVATION_IDENTITY_HASH`; their materialized artifact status is
`NOT_YET_MATERIALIZED`. Source hash, transform identity, and transform-config
hash are all included in the derivation identity.

No model input, transformed waveform, prediction, metric, or outcome was
created.
