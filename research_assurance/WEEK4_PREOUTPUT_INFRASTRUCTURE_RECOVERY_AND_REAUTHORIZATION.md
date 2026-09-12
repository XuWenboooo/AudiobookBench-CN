# Week4 pre-output infrastructure recovery and reauthorization

## Failed-run forensic freeze

The immutable failed namespace is
`results/week4_adaptive_redteam_runs/week4_adaptive_redteam_v0_20260912_supplement_v1`.
It contains only `run_metadata.json` and its one-row append-only F5 attempt
ledger; there is no candidate ledger or waveform directory.

```text
FAILED_RUN_FORENSICALLY_FROZEN = YES
FAILED_RUN_PRODUCED_REAL_WAVEFORM = 0
FAILED_RUN_D0_INVOCATIONS = 0
FAILED_RUN_SCIENTIFIC_OUTCOME_OBSERVED = NO
FAILED_RUN_REUSED = NO
FAILED_NAMESPACE_IMMUTABLE = YES
```

The failed authorization (`D30FEA154573357214361326349C04594E9704045D98D36D3AFC90DD427ADF41`)
is preserved byte-for-byte in `authorization_history`; it is consumed by a
failed pre-output infrastructure attempt, not superseded before execution.

## Admissibility

No waveform, D0 query, scientific metric, validation, held-out result, or H4
outcome was observed. Frozen preregistration, canonical config, population,
and execution supplement remain unchanged.

```text
CLEAN_REEXECUTION_SCIENTIFICALLY_ADMISSIBLE = YES
RERUN_CLASSIFICATION = INFRASTRUCTURE_QUALIFICATION_REEXECUTION_BEFORE_SCIENTIFIC_OUTCOME
```

## Frozen runtime qualification

The exact local source package root is
`results/week3_engineering_qualification/f5_tts_v1_base/source/F5-TTS-82fc4fe622fe36047d1dff99b550e6018181ea11/src`.
`f5_tts` is a PEP 420 namespace package (there is no `__init__.py`); its
`api.py` resolves to the frozen source tree. The existing local editable formal
environment was used with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.

```text
F5_SOURCE_LAYOUT_VERIFIED = YES
F5_TTS_IMPORTABLE = YES
F5_TTS_RESOLVES_TO_FROZEN_SOURCE = YES
FORMAL_ENVIRONMENT_QUALIFIED = YES
F5_API_CONSTRUCTION = PASS
CHECKPOINT_LOAD = PASS
VOCODER_LOAD = PASS
```

No Week4 population input or scientific waveform was used for qualification.
The original failure was environment selection (system Python) rather than a
generator, source, asset, or scientific-protocol change.

## Reauthorization and stop state

The new active identity is `week4_dev_integrity_reexecution_01`, bound to a new
empty namespace `results/week4_adaptive_redteam_runs/week4_dev_integrity_reexecution_01`.
It binds the frozen F5 source manifest and formal runtime environment manifest
in addition to all prior protocol, asset, and execution-source hashes. Its
offline preflight passed using the bound Python executable.

```text
EXECUTION_CODE_CHANGED = YES
IMPORT_PATH_REPAIR_ONLY = NO
NEW_AUTHORIZATION_CREATED = YES
NEW_AUTHORIZATION_PREFLIGHT = PASS
PREREGISTRATION_CHANGED = NO
CANONICAL_CONFIG_CHANGED = NO
POPULATION_CHANGED = NO
EXECUTION_SUPPLEMENT_CHANGED = NO
REAL_F5_GENERATION = NOT STARTED
REAL_D0_QUERY = NOT STARTED
VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO
READY_FOR_WEEK4_CLEAN_DEV_REEXECUTION = YES
```

The execution-code change is limited to formal-environment identity validation
before dispatch. No scientific setting or construction/evaluation logic changed.
This task stops here; it does not start the new DEV execution.
