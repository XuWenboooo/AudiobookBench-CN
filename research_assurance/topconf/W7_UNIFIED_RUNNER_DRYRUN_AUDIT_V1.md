# W7 unified formal runner dry-run audit v1

    UNIFIED_FORMAL_RUNNER = IMPLEMENTED_PREINFERENCE_ONLY
    RUNNER_LOCALIZERS = CFPRF, MultiReso, SAL, BAM
    REAL_W7_CASES_USED = 0
    W7_SCIENTIFIC_INFERENCES = 0
    GT_ACCESS_BY_RUNNER = NO
    REGISTRY_HASH_GATE = PASS
    SYNTHETIC_OUTPUT_CONTRACT = PASS_FOR_4_FIXTURES
    FAILURE_PROPAGATION_CONTRACT = PASS
    STRICT_LOAD_CFPRF = NOT_RERUN_IN_THIS_RECOVERY
    STRICT_LOAD_MULTIRESO = NOT_RERUN_IN_THIS_RECOVERY
    STRICT_LOAD_SAL = BLOCKED_CHECKPOINT_MISSING
    STRICT_LOAD_BAM = NOT_RERUN_RIGHTS_GATE_FAIL
    RUNNER_SYNTHETIC_DRYRUN = FAIL_PREREQUISITES_NOT_ALL_4_LOADED

The new shared harness has a static registry of exactly the four frozen
localizers and rejects other models, datasets, conditions, hash mismatches,
and silent failure rows. Its synthetic fixtures test deterministic native
temporal-output envelopes and the unified terminal-row contract only. They do
not instantiate a model, load a checkpoint, read a W7 case, create raw
prediction output, or calculate a scientific quantity.

The dry-run is not promoted to a formal readiness pass: SAL's exact frozen
checkpoint is absent, and BAM's checkpoint rights remain unresolved.
