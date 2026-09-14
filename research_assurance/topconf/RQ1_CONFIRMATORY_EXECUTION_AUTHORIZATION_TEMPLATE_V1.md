# RQ1 Confirmatory Execution Authorization Template v1

Status: **TEMPLATE ONLY / NOT AUTHORIZED / NOT STARTED**

This template is intentionally incomplete and cannot be interpreted as an
execution command. A human review must complete every field, verify hashes, and
change the explicit authorization status in a new versioned record. Creating
this template does not authorize data generation, model loading, inference,
evaluation, bootstrap, RQ2, or RQ3.

## Required bindings before authorization

```text
AUTHORIZATION_ID = <new unique ID>
PROTOCOL_ID = P4-RQ1-DESIGN-20260914-01
PROTOCOL_COMMIT = <commit containing the reviewed preregistration>
PROTOCOL_SHA256 = <sha256 of frozen preregistration>
DATASET_MANIFEST = <materialized LEVEL2_FRESHNESS_MANIFEST_V1.json>
DATASET_SHA256 = <sha256 of materialized freshness manifest>
FRESHNESS_PROOF = <PASS record proving no pilot/Phase3T/development reuse>
BASELINE_SET = <model IDs and exact commits>
CHECKPOINT_HASHES = <one exact SHA256 per checkpoint>
WHETHER_B_PROVENANCE = <independent detector, license, training/source, runtime>
THIRD_PARADIGM_GATE = <PASS or explicit NO_GO claim limitation>
CALIBRATION_MANIFEST = <speaker/source-disjoint Level-1 calibration hash>
THRESHOLD_POLICY = LEVEL1_CALIBRATION_TARGET_FPR_0.05
OUTPUT_NAMESPACE = results/topconf_level2_rq1_v1/<invocation_id>
NAMESPACE_REGISTRY_CHECK = <PASS>
ENVIRONMENT_LOCKS = <one frozen environment per model>
BLINDING_MANIFEST_HASH = <hash of inference-safe manifest>
GT_REVEAL_CUSTODIAN = <named authorized evaluator role>
FAILURE_LEDGER_SCHEMA = <version and hash>
SEED = 20260914
```

## Mandatory preflight checklist

```text
[ ] Phase3T closure PASS independently rechecked
[ ] Phase4 reconciliation matrix and ledger reviewed
[ ] Outcome firewall PASS; result-based design changes = 0
[ ] Preregistration hash predates any Level-2 reveal
[ ] Freshness manifest materialized and independently checked
[ ] Whether-A contract and Level-1 calibration hash fixed
[ ] Whether-B independent checkpoint/license/runtime gate PASS
[ ] Three-paradigm/two-distribution H1 claim gate disposition recorded
[ ] All model/checkpoint/environment hashes verified
[ ] Blinded inference view contains no GT, mechanism, span, or source linkage
[ ] New namespace is unused and has one owner
[ ] Failure/retry ledger and stop rules loaded
[ ] Synthetic governance dry run PASS
[ ] No real Level-2 outcome, metric, or visualization has been accessed
```

## Explicit state (frozen now)

```text
STATUS = TEMPLATE_ONLY_NON_AUTHORIZING
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
```

The template must not be filled or executed automatically by a preregistration
build, test, or dry-run command.
