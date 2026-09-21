# External cache migration record v1

Audit date: `2026-09-21`

```text
STATUS = COMPLETE_SELECTED_DATA_ONLY
TARGET = G:/AudiobookBench-CN/external_data/topconf_phase3_cache
RECOVERABLE_BACKUP = G:/AudiobookBench-CN/external_data/topconf_phase3_cache_migration_backup_20260921
F_SOURCE_BACKUP = REMOVED_AFTER_VERIFICATION
F_FREE_SPACE_AFTER = 25.99 GB
G_FREE_SPACE_AFTER = 1404.11 GB
```

The following directories were byte/file-diff verified before switching the
original F-drive paths to junctions: `PartialEdit_v1.1`, `checkpoints`,
`LlamaPartialSpoof_v1.0.b`, `tools`, `cfprf_runtime`, and
`fairseq-a54021305d6b3c4c5959ac9395135f63202db8f1`.

`PartialSpoof_v1.2` was not switched because it remains a blocked W7
candidate and its large copy was intentionally left at the original F-drive
path. `repos` was also left at the original path because its copy was not
completed; neither choice affects the two READY W7 distributions or the
experiment path compatibility. No Git-tracked data, checkpoints, archives,
logs, partial files, or predictions were added by this migration.
