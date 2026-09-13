# Phase3T MultiReso Manifest Serialization Recovery v1

Status: **INFRASTRUCTURE-ONLY / SERIALIZATION COMPATIBILITY FIX**

The authorized r2 worker repeatedly stopped after a structurally valid batch
when Windows returned `PermissionError` from the atomic summary-manifest
replacement. No raw output, case order, native output semantics, model,
checkpoint, GT field, metric, scale policy, or selection/exclusion logic was
changed. The lock and manifest evidence from each stop remains in the
namespace.

```text
FAILURE = transient Windows PermissionError during summary manifest os.replace
RAW_LEDGER_INTACT_AT_LAST_STOP = 9392 / 9392
FIX_SCOPE = bounded retry of atomic summary-manifest replacement only
SCIENTIFIC_PROTOCOL_CHANGED = NO
SCIENTIFIC_OUTCOMES_USED = NO
INVOCATION = PHASE3T_MRM_FULL_E1_002
NAMESPACE = results/topconf_phase3t/multireso_worker_02
```

The retry is bounded and does not fall back to a non-atomic overwrite. A
failed retry remains a terminal infrastructure stop requiring explicit
resume; it cannot silently alter or omit a raw record.

