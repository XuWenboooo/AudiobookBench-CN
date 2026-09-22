# W7 Offline Recovery Kit Audit v1

Status: `COMPLETE_OFFLINE_INFRASTRUCTURE_AUDIT`

This compact audit records the recovery kit at `G:\W7-RECOVERY-KIT`. It was
created without running real W7 cases, accessing Level-2, changing scientific
configuration, installing packages, modifying checkpoints, or stopping WSL.

## Snapshot

```text
AUTHORITATIVE_W7_WORKTREE = G:\项目\申请实验室  TTS项目\worktrees\topconf-w7-reconciliation\AudiobookBench-CN
W7_BRANCH = topconf-w7-reconciliation
W7_HEAD = 6203ba7996c5d82d9bfe05726bf5cd1a67c47621
MAIN_HEAD = 9d3a033c192f61c1dd6134e8aff451a791e2ebf6
RECOVERY_ROOT = G:\W7-RECOVERY-KIT
```

The authoritative W7 worktree and main worktree were clean at snapshot time.
Both bundles passed `git bundle verify` and were hashed. The W7 bundle SHA-256
is `7967506d0dfe093e2a0f2b11f5d2e1bf50c9f3e4b722844b87de08ecbbed6b37`.
The main bundle SHA-256 is
`cae13a68cbaef4e92d5e1ebc1dfc0c2bda05a5496557ba27ce3440ac30d41561`.

## Offline inventory

- Five frozen source archives are indexed and stable under
  `G:\W7-OFFLINE\sources`; no source was redownloaded.
- Four model assets are present and stable under `G:\W7-OFFLINE\models`:
  VITS, VoiceCraft giga830M, VoiceCraft EnCodec and YourTTS archive. Their
  exact sizes and SHA-256 values are in the recovery manifest.
- M1/M3/M5 isolated runtime directories were not created at snapshot time.
  The model bytes are offline references only and do not imply runtime
  executability or redistribution permission.
- MFA `english_us_arpa` dictionary and acoustic model were not found in the
  offline root or target runtime paths.
- Conda is unavailable on the snapshot host; exact M1/M3/M5 package closure is
  therefore `NOT_COMPUTABLE_RUNTIME_ABSENT`. No package was installed.

## WSL and system boundary

`Ubuntu-22.04-W7` appeared in `wsl --list --running`. WSL export is therefore
`DEFERRED_MAINLINE_ACTIVE`; no `wsl --shutdown`, live VHDX copy, import or
restart was attempted. Windows/GPU/WSL and read-only Linux command snapshots
are under `07_system_inventory/` and `08_wsl/`.

## Verification

```text
RECOVERY_KIT_SELF_CHECK = PASS
MASTER_SHA256SUMS = 49 entries; independently verified
MANIFEST_SCHEMA = PASS
RESTORE_SCRIPT_SYNTAX = PASS
ASSET_HASH_VERIFICATION = PASS
SCOPED_TOPCONF_TESTS = 179 passed
PREREGISTRATION_CHECKER = PASS
W7_RECONCILIATION_CHECKER = PASS
GIT_DIFF_CHECK = PASS
```

The network matrix and engineering-only single-point-of-failure audit are in
`G:\W7-RECOVERY-KIT\11_audit`. Restore scripts are fail-closed, offline by
default and never overwrite an authoritative checkout without an explicit
operator flag.

## Scientific firewall

```text
P4_SCIENTIFIC_SPECIFICATION = FROZEN
P4_HUMAN_APPROVAL = COMPLETE
HUMAN_APPROVAL_INVALIDATED = NO
W7_EXECUTION_AUTHORIZED = NO
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
REAL_W7_CASES_USED = 0
SCIENTIFIC_CONFIG_CHANGED = NO
SCIENTIFIC_ASSET_BYTES_CHANGED = NO
SCIENTIFIC_POPULATION_CHANGED = NO
```

## Remaining recovery gaps

The remaining gaps are engineering-only: planned idle-window WSL export,
creation of isolated M1/M3/M5 environments, exact offline package closure,
MFA assets, restricted-license handling and an independent second copy of
recovery-critical artifacts. These gaps do not authorize any W7 execution.
