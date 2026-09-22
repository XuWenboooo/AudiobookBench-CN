# W7 Worktree C-to-G Migration Audit V1

## Scope and authority

- Authoritative project root: `G:\项目\申请实验室  TTS项目`
- Source W7 worktree: `C:\Users\ZhuanZ（无密码）\.codex\worktrees\topconf-w7-reconciliation\AudiobookBench-CN`
- Destination W7 worktree: `G:\项目\申请实验室  TTS项目\worktrees\topconf-w7-reconciliation\AudiobookBench-CN`
- Branch: `topconf-w7-reconciliation`
- Local W7 source and destination baseline HEAD: `32ed968f12338bef31cf259d2e0fe85f65e5c8e0`
- Remote W7 observed before push: `29d5605bf7e00932016c225a1bd8e26a19911a4a` (stale)
- Local W7 is authoritative; no fetch, reset, checkout of remote, pull, rebase, merge, or force push was used.

## Backup and worktree method

- Bundle: `G:\TTS-Migration-Audit\baseline\topconf-w7-reconciliation-pre-worktree-migration.bundle`
- Bundle SHA-256: `3377363DCEC289B292D2BF6F6AE94B4B4D0E2A3D62194FF206192E2453DA9160`
- `git bundle verify`: PASS; complete history and `refs/heads/topconf-w7-reconciliation` at `32ed968f...`.
- `git worktree move` was attempted and safely rejected because the C: worktree `.git` file did not point back to the copied G: worktree administration area.
- Safe fallback was used: the W7 linkage was repaired to the G: common Git directory, a temporary branch was created at the exact local HEAD, a new G: worktree was created, and tracked contents were compared before C: was detached.
- The temporary branch was deleted only after it was verified identical to the formal W7 branch. The old C: directory remains as a clean detached rollback copy at `32ed968f...`.
- A broad Git repair scan reported unrelated external pointers; those non-W7 pointers were restored to their original F: common Git directory. No unrelated worktree was deleted or content-rewritten.

## Tracked-content comparison

- Pre-rebinding: 1,299 tracked files on each side; missing 0; unexpected 0; byte-hash mismatches 0.
- Post-rebinding: 1,299 tracked files on each side; the only 7 differences are the explicitly authorized F:→G: prospective path bindings in 5 configs and 2 phase3t runners. No scientific file differed.
- Historical, frozen, documentation, population, exclusion, and portability-fixture path references were preserved.
- Active F: references after rebinding: 0. Active C: worktree references: 0.

## Protected scientific identity

- Approved execution config declared SHA-256: `009CAEDD67EA2CA7C6AA8C4DEF32F87465754A0E3C37E1D95D9403D48E9875C2`
- Approved package declared SHA-256: `512929394F7ACAFE417EC5018CA922DE73E8F56A7488D601E427ACC5F4A23117`
- Deterministic mechanism case map SHA-256: `8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9`
- V3 population manifest SHA-256: `AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4`
- V5 freshness manifest SHA-256: `6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E`
- Protected scientific file comparison C:↔G: PASS; scientific config, asset bytes, and population bytes changed: NO.

## Verification

- `python -m pytest tests/topconf -q`: **179 passed in 46.14s**
- `python tools/topconf/check_w7_reconciliation.py`: PASS; W7 pre-execution audit only, no metrics measured.
- `python tools/topconf/check_w7_preregistration.py`: PASS.
- `git diff --check`: PASS.
- W7 execution: not authorized and not executed.
- Level-2 outcomes accessed: NO.
- Scientific inferences: 0.
- Human approval invalidated: NO.

## Commit and remote policy

- The migration commit is made directly on the local `topconf-w7-reconciliation` branch with parent `32ed968f...`; no merge or rebase is used.
- Remote publication is non-force only and is attempted after local verification. A network failure is recorded as unavailable network rather than treated as a scientific failure.
- F: main source remains present. Other C:/F: worktrees remain present and undeleted.
