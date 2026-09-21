# W7 mechanism human-freeze template v1

Status: `REQUIRED_BEFORE_W7_REEXECUTION`
This is a decision form, not an authorization and not an executable
configuration. Complete it once, preserve it under a new immutable filename,
then recompute the pre-inference hash manifest. Do not execute any W7 case
while a required field remains blank.

## Freeze declaration

```text
FREEZE_DECISION_ID = ______________________________________________
DECISION_DATE_UTC = _______________________________________________
DECISION_MAKER = __________________________________________________
SOURCE_CASE_MANIFEST = W7_FINAL_CASE_MANIFEST_V2.jsonl.gz
SOURCE_CASE_MANIFEST_SHA256 = BEA3EB3E31F1A81219617D6994ACD3381C99B972300020C4B781B8FB878DE572
EVIDENCE_MATRIX = MECHANISM_PARAMETER_EVIDENCE_MATRIX_V1.md
CASE_MAP_PROPOSAL = W7_MECHANISM_CASE_MAP_PROPOSAL_V1.json
NO_W7_OUTCOMES_REVIEWED_BEFORE_FREEZE = YES / NO
```

If the final answer is not `YES`, stop: this template cannot close the
pre-inference mechanism gate.

## Decision M1 — total case-map rule

Choose exactly one auditable rule that covers every record in the detailed
proposal map, with no unmapped case and no ambiguity. Attach an immutable map
or state a deterministic grouping predicate and list every matching case ID.

```text
WHAT_MUST_BE_FROZEN = a total case-to-configuration-hash mapping
ALLOWED_VALUES_FROM_PREEXISTING_CONTRACT = only the five permitted mechanism families and complete schema-conforming configuration objects
METHODOLOGICAL_CONSEQUENCE = identifies the implementation relation before any W7 inference and preserves paired source/GT linkage
WHY_CODEX_CANNOT_CHOOSE = the frozen evidence fixes the allowable set but not one family/configuration per case
NO_OUTCOME_INFORMATION_USED = YES
```

```text
MAP_RULE_ID = ______________________________________________________
MAP_COVERAGE = 106859 / 106859 mechanism_shift cases
UNMAPPED_CASES = 0
AMBIGUOUS_CASES = 0
CASE_TO_MECHANISM_CONFIG_HASH_BINDING = ____________________________
ATTACHED_CASE_MAP_PATH_AND_SHA256 = ________________________________
```

For each group in the map, fill one line. Duplicate lines are allowed only
when their complete configuration hashes differ.

| group ID / exact case selector | number of cases | mechanism family | configuration hash | evidence/provenance for the mapping |
| --- | ---: | --- | --- | --- |
|  |  |  |  |  |

## Decision M2 — complete configuration object for every referenced hash

Repeat this block for every distinct configuration hash in Decision M1. All
fields correspond exactly to `MECHANISM_CONFIG_SCHEMA_V1.json`; no implicit
defaults are permitted.

```text
WHAT_MUST_BE_FROZEN = one immutable complete configuration object per referenced hash
ALLOWED_VALUES_FROM_PREEXISTING_CONTRACT = the schema fields and the fixed five-family enum; no additional family or parameter search
METHODOLOGICAL_CONSEQUENCE = makes generation reproducible and binds reference/span/seed/quality rules to every mapped case
WHY_CODEX_CANNOT_CHOOSE = the contract requires these values but does not supply concrete values or a unique derivation
NO_OUTCOME_INFORMATION_USED = YES
```

```json
{
  "mechanism_id": "",
  "mechanism_config_hash": "",
  "mechanism_family": "",
  "implementation": "",
  "version": "",
  "parameter_set_id": "",
  "reference_rule": "",
  "target_span_rule": "",
  "sample_rate": null,
  "codec_path": "",
  "seed_policy": "",
  "quality_gate_policy": "",
  "parameters": {}
}
```

Permitted `mechanism_family` values are fixed to:

- `same_speaker_splice_crossfade_control`
- `cross_speaker_boundary_control`
- `conventional_tts_replacement`
- `voice_conditioned_tts_vc_replacement`
- `neural_speech_editing_infilling`

## Decision M3 — invariant confirmation

```text
WHAT_MUST_BE_FROZEN = the invariants governing application of Decisions M1 and M2
ALLOWED_VALUES_FROM_PREEXISTING_CONTRACT = only the affirmative invariant statements below; a negative answer leaves the gate open
METHODOLOGICAL_CONSEQUENCE = prevents silent population, GT, mechanism-family, or failure-policy drift
WHY_CODEX_CANNOT_CHOOSE = this is a human attestation of the scientific completion and its provenance
NO_OUTCOME_INFORMATION_USED = YES
```

```text
SOURCE_AND_GT_LINKAGE_PRESERVED = YES / NO
NO_NEW_MECHANISM_FAMILY = YES / NO
NO_PARAMETER_OR_SEVERITY_SEARCH = YES / NO
DECLARED_TERMINAL_FAILURE_TAXONOMY_RETAINED = YES / NO
NO_CASE_DROPPING_OR_OUTCOME_GUIDED_RETRY = YES / NO
ALL_CONFIG_OBJECTS_CANONICALLY_HASHED = YES / NO
```

All six answers must be `YES`. Otherwise the mechanism gate remains
`PENDING_HUMAN_MECHANISM_FREEZE`.

## Separate post-closure authorization

This template neither cures BAM checkpoint rights nor authorizes W7. Only
after BAM rights, this complete mechanism freeze, every checkpoint identity,
and the re-audit pass may a human issue a new explicit W7 re-execution
authorization.
