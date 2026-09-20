# W7 Canonical Case Identity and Source Binding Contract v1

Status: `DRAFT_READY_TO_FREEZE` / not frozen / no execution authorization

Every future W7 row is assigned one canonical identity before any model
inference. Whether-A, Whether-B and Where join on that same `case_id`; a model
output, score order, filename proximity, timestamp or array position can never
create or alter a case identity.

## Identity record

The required identity fields are defined in
`CASE_IDENTITY_SCHEMA_V1.json`. They include distribution/version/split,
source audio ID and hash, optional speaker/utterance IDs, manipulation family
and mechanism, condition and transform IDs, final audio artifact ID/hash,
GT ID/version/hash, Whether definition, localizer, checkpoint and adapter
version. Optional fields remain explicit `null`; they are never omitted by
accident.

`case_id` is `w7case_` plus the first 32 hex characters of SHA-256 over the
sorted, compact UTF-8 JSON identity payload. The payload uses no absolute
path, temporary directory, execution timestamp or random UUID. Equal payloads
produce equal IDs; changing distribution, source, manipulation or condition
changes the ID.

## Parent-child source binding

The manifest must carry these parent-child nodes:

```text
SOURCE
  -> MANIPULATION
    -> CONDITION_TRANSFORM
      -> FINAL_AUDIO_ARTIFACT
        -> GT
```

Each child stores the parent ID. A codec row therefore identifies its original
source and manipulated artifact; a resampling row identifies the exact
manipulated parent and transform; GT remains bound to the final artifact and
records whether its temporal coordinates are invariant or deterministically
mapped. Missing or conflicting parent IDs fail closed.

The inference view excludes GT payload and outcome fields. The evaluation view
joins GT only after the raw inference row has reached a terminal state.
