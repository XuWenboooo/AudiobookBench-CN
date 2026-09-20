# External Distribution Acceptance Harness

The shared validator is
`src/audiobookbench/topconf/preparation/distribution_acceptance.py`.
It accepts the canonical manifest described by
`DISTRIBUTION_ACCEPTANCE_INPUT_V1.schema.json` and returns the machine-readable
`DISTRIBUTION_ACCEPTANCE_RESULT_V1.schema.json` shape. It checks identity,
audio metadata, GT representation/range, duration/sample/frame agreement,
split collisions, license/provenance status and all required duplicate/missing
conditions.

`ready_candidate` is mechanical only. It becomes project-level
`READY_EXTERNAL_DISTRIBUTION = YES` only after the existing human provenance,
license, adapter and authorization gates pass. Any critical ambiguity is
fail-closed; no ID is silently skipped.
