# NON-G safe-delete plan (offline draft)

Status: `DRAFT_ONLY`. No deletion was performed.

## SAFE_DELETE_CANDIDATE

None promoted at this stage. Candidate promotion requires remote/local HEAD equality, which is pending because GitHub push is unavailable.

## KEEP_UNTIL_REMOTE_SYNC

- Any F: Git-trackable artifact proposed for recovery or deletion.
- C: rollback worktree and its repository metadata.

## KEEP_UNTIL_W7_COMPLETE

- W7 execution manifests, runtime preparation files, recovery records, and all scientific inputs.
- F: dataset, model, audio, environment, cache, and archive trees.

## KEEP_PERMANENTLY_OR_EXTERNAL_BACKUP

- `G:\W7-RECOVERY-KIT\01_git\topconf-w7-reconciliation_d320045dd2a8f5f8501d8ca5233bba69abbbe199.bundle`
- `G:\W7-RECOVERY-KIT\01_git\main_37d53e4a3f624ebd05ad0fbea6e4aae2dcda4834.bundle`

## UNKNOWN_DO_NOT_DELETE

- All non-G paths not yet paired by a verified size/hash comparison.
- F: active dataset references, including `F:\项目\申请实验室  TTS项目\datasets\AISHELL-3`.

## Evidence

- G branch bundle verifies as a complete history.
- Main branch bundle verifies as a complete history.
- `python -m pytest tests/topconf -q`: 179 passed.
- `git diff --check`: pass.
- Remote sync remains pending: local `d320045dd2a8f5f8501d8ca5233bba69abbbe199`, remote `be7c3bca207a5c17117e5acf3070bc8e22340b97`.
