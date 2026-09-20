# TOPCONF-W7-PREPARATION-SIDEBRANCH

This directory is permanently classified as:

```text
PRE-W7 / NON-OUTCOME PREPARATION
```

It is not a W7 result and not a confirmatory result. The W6 gate remains
blocked because only one external distribution is ready; W7 protocol freeze
and scientific authorization remain separate human decisions.

## Contents

- [W7 protocol draft](W7_PILOT_PROTOCOL_DRAFT_V1.md)
- [Distribution acceptance harness](distribution_acceptance/README.md) and
  [result schema](distribution_acceptance/DISTRIBUTION_ACCEPTANCE_RESULT_V1.schema.json)
- [PartialSpoof mismatch evidence](PARTIALSPOOF_IDENTITY_MISMATCH_V1.md) and
  its machine-readable companion
- [Generic temporal GT adapter contract](generic_temporal_gt_adapter/GENERIC_TEMPORAL_GT_ADAPTER_CONTRACT_V1.md)
  and [schema](generic_temporal_gt_adapter/GENERIC_TEMPORAL_GT_ADAPTER_SCHEMA_V1.json)
- [Scientific evidence ledger](SCIENTIFIC_EVIDENCE_LEDGER_V1.md) and JSON
- [Paper results table](PAPER_RESULTS_TABLE_DRAFT_V1.md)
- [Paper provenance appendix](PAPER_PROVENANCE_APPENDIX_DRAFT_V1.md)
- [Paper experiment matrix](PAPER_EXPERIMENT_MATRIX_DRAFT_V1.md)
- [Preparation state](W7_PREPARATION_STATE_V1.json)
- [Pre-registration invariant checker](../../../../tools/topconf/check_w7_preregistration.py)
- [Merge safety audit](MERGE_SAFETY_AUDIT_V1.md)

## Firewall state

```text
W6_GATE = BLOCKED
W7_PROTOCOL_FROZEN = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
W7_DETECTION_AUROC = NOT_MEASURED
W7_LOCALIZATION_AUROC = NOT_MEASURED
CONFIRMATORY_AUROC = NOT_MEASURED
RESULT_BASED_MODEL_SELECTIONS = 0
RESULT_BASED_DATASET_SELECTIONS = 0
RESULT_BASED_METRIC_CHANGES = 0
```

Run the static checker from the repository root:

```text
python tools/topconf/check_w7_preregistration.py --repo .
```

The checker is a state firewall, not an execution command.
