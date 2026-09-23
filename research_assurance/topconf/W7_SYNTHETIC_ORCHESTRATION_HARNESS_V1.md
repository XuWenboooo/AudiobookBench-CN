# W7 synthetic orchestration harness V1

Status: `SYNTHETIC_ORCHESTRATION_HARNESS = PASS` for engineering contract validation only. This record does not assert W7 execution readiness or approve any V2 candidate.

## Scope and entry point

The runner is `src/audiobookbench/topconf/w7_synthetic_harness.py`; the CLI is `tools/topconf/run_w7_synthetic_harness.py`. The fixed fixture set is `tests/topconf/fixtures/w7_synthetic_cases_v1.json` with 15 invented cases. Its config is `w7_synthetic_config_v1.json`, SHA-256 `90950eaa38eea4479de97f4d412305cf3ed2182bbdffb82a8abca0667d7d2e7e`, and explicitly says `CANDIDATE_NOT_APPROVED`. The config's candidate semantics are an engineering contract, not a scientific policy or a copy of real V2 case data. Every fixture has `data_origin=synthetic`, a `SYNTH_` case ID, generated waveform, and invented transcript.

The stage sequence is `LOAD_CONFIG → VALIDATE_APPROVAL_STATE → LOAD_CASE → RESOLVE_TRANSCRIPT → RESOLVE_INTERVALS → MATERIALIZE_MECHANISM → APPLY_MEDIA_CONDITION → RUN_LOCALIZER → RUN_WHETHER_A → RUN_WHETHER_B → PRESERVE_RAW_OUTPUT → COMPUTE_METRICS → EVALUATE_GATE`. A typed `StageContract` carries case/distribution/condition/mechanism identity, source and transcript identities/hashes, intervals, seed, runtime/asset/transform identities, output hash, status, failure code, and parent event IDs. Early stages use `DEFERRED` for a source hash that cannot exist before audio generation.

Each M1–M5 mechanism has a `MechanismAdapter` contract with runtime, asset, prepare, execute, output validation, and provenance methods. Only a deterministic synthetic implementation executes. The five real adapter placeholders return `NOT_READY` through fail-closed methods. Localizer, Whether-A, and Whether-B use deterministic dummy adapters. Their outputs carry `SYNTHETIC_NONSCIENTIFIC_OUTPUT` and are stored apart from orchestration metadata under `raw_non_scientific`. The metric and gate stages expose interfaces but record `NOT_COMPUTED` and `NOT_EVALUATED`; they do not calculate formal AUROC, AUPRC, EER, LD@DR95, or a formal gate.

## Guards and outputs

The candidate config cannot process a non-synthetic input. A real input aborts with `W7_REAL_EXECUTION_BLOCKED_UNAPPROVED_CONFIG` before any audio loader is called. Level-2 requests, unknown config hashes, unknown runtime identities, unfrozen asset identities, and attempts to treat this harness as authorized execution are rejected before input processing. The CLI only accepts built-in `SYNTH_` fixture names.

Output writes are restricted to `artifacts/w7_synthetic_harness/`; the harness refuses other output roots. Its JSON schema and `formal_w7_result=false` distinguish dummy outputs from formal result manifests. Each completed stage has an immutable artifact and a separate immutable provenance event with timestamp, input/output hashes, config hash, runtime identity, seed/sub-seed, status, failure code, and parent IDs. There are no silent retries, dropped cases, transcript substitutions, or model fallbacks. Resume verifies stage hashes and reuses the same event IDs; existing artifacts are never overwritten.

The `--dry-run` command resolves config, sorted case and mechanism schedule, conditions, all six configured seed namespaces, and expected artifact paths without generating waveform samples or loading models. Its schedule hash for the fixed 15 fixtures is `511b549d4e0fa0596bc35690a5ce2b95f13e23fde73688b0115f8eb6f7280290`. `--all` executes those fixtures in stable order and emits one terminal record per case; the suite contains seven expected completions and eight deliberately injected terminal failures.

Timeline utilities use half-open sample intervals, deterministic seconds-to-samples and seconds-to-codec-frames conversion, non-overlap validation, interval sorting, mask groups, deterministic ordinals, duration-fit resampling, and exact endpoint splicing. The mock M3 observation schema records each input mask, generated codec-frame count, generated region boundary, decoder/sample mapping, extracted/resampled segment identities, and final splice interval. No VoiceCraft model is called.

## Remaining integration work

Formal execution requires a separately approved configuration and authorization, actual M1–M5 runtime/asset readiness, real adapter implementations, frozen case binding, production raw-result preservation, and formal metric/gate services. This harness supplies only typed integration points and synthetic failure paths. Historical authorization records in the repository do not approve this candidate or reauthorize W7. Current branch decision for this side task: `V2_HUMAN_APPROVED=NO`, `W7_EXECUTION_READINESS=NO`, `W7_EXECUTION_AUTHORIZED=NO`, `W7_EXECUTED=NO`, and `LEVEL2_OUTCOMES_ACCESSED=NO`.
