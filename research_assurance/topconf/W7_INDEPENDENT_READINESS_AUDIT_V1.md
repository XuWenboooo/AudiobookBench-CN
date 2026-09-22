# W7 Independent Readiness Audit v1

Status: `FAIL_CLOSED`

This is an independent, read-only, fail-closed audit of the authoritative W7
worktree at `G:\项目\申请实验室  TTS项目\worktrees\topconf-w7-reconciliation\AudiobookBench-CN`.
It did not modify runtimes, install dependencies, download assets, modify
preregistration, run real W7, access Level-2 outcomes, or compute scientific
metrics.

## Snapshot

```text
SIDE_TASK = SIDE-W7-INDEPENDENT-READINESS-AUDIT
BASELINE_HEAD = be7c3bca207a5c17117e5acf3070bc8e22340b97
BRANCH = topconf-w7-reconciliation
P4_SCIENTIFIC_SPECIFICATION = FROZEN
P4_HUMAN_APPROVAL = COMPLETE
HUMAN_APPROVAL_INVALIDATED = NO
W7_EXECUTION_AUTHORIZED = NO
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
REAL_W7_CASES_USED = 0
```

## Mechanism evidence

| Mechanism | Independent classification | Evidence and caveats |
|---|---|---|
| M1 | `FAIL` | V4 records the official VITS Google Drive source, file identity, size `145599717`, and SHA-256 `c94fb49d...da5a561`; the G: asset and WSL `/mnt/g` mapping match. However, `runtime_m1_vits` itself cannot import `torch`, although V4 calls it VERIFIED through a shared M3 executor. `G:\W7-OFFLINE\logs\download.log` records `FAIL VITS_LJS_NOT_FOUND`, and no first-materialization record was found. The current loaded asset therefore cannot be independently tied to a recorded first materialization or ruled out as a silent replacement. |
| M2 | `PASS_EVIDENCED` | Repository control adapter `w7_candidate_transforms_v1`, frozen mechanism identity, synthetic deterministic tests, and outcome-blind source evidence are present. No external model runtime or checkpoint is required. |
| M3 | `PASS_BUT_EVIDENCE_INCOMPLETE` | VoiceCraft revision `f0a7a971...0b690`, AudioCraft revision `c5157b5b...4bc7f0`, both checkpoint hashes, MFA acoustic asset, dictionary, Python `3.9.16`, torch `2.0.1+cu117`, torchaudio `2.0.2+cu117`, xformers `0.0.22`, and MFA `2.2.17` match the current records and read-only environment probes. The acoustic model is v2.0.0 and the compatible ARPA dictionary is v3.0.0; the manifest records 70 used phones and zero unknown tokens. Raw strict-load, synthetic alignment, and determinism logs were not independently available in the repository; the current conclusion relies on the V4/V6 audit declarations. |
| M4 | `PASS_EVIDENCED` | Repository deterministic waveform control adapter, frozen identity, synthetic smoke, and repeatability tests are present; no external model or asset is required. |
| M5 | `PASS_BUT_EVIDENCE_INCOMPLETE` | Coqui TTS `0.7.0`, frozen YourTTS revision `23904e6b...f1e2a9`, registry commit `e9a1953e`, model SHA-256, Python `3.10.13`, torch/torchaudio, NumPy `1.23.5`, and pyworld `0.3.4` match read-only probes. The pyworld choice is explicitly documented as compatibility-only and non-scientific. Raw strict-load/synthetic-smoke logs were not independently available; the conclusion relies on V4/V6 declarations. |

## Manifest and hash rechecks

`W7_APPROVED_RUNTIME_ASSET_MANIFEST_V4.json` exists. All six Windows G:
physical paths and all six WSL `/mnt/g`/migration-audit mappings were present
and matched the recorded sizes and SHA-256 values. The V4 file hash is
`A32D0D4025E3C9EA68BCEAAA210D563E6CDF1948223E607EF26677F8CFC0E639`.

`W7_PREREGISTRATION_HASH_MANIFEST_V6.json` exists. All 13 referenced repository
records independently matched their recorded path, size, and SHA-256. The V6
file hash is `AA98B34DBE1C51241119EF27C0DAA48FE1D98AEE390EE7F4A089AA3196075029`.
No V4 or V6 file was created or modified by this audit.

The five protected prompt values match the authoritative repository records:
approved execution config, approved package, deterministic case map, V3, and
V5. The repository protected-hash checker and direct byte rechecks passed.

## Outcome and real-case firewall

The current preregistration and reconciliation checkers report no Level-2
outcome access, no metrics, no real W7 execution, and zero scientific
inferences. The source and test scan found synthetic-only W7 fixtures and
historical/pilot artifacts, but no current W7 output namespace or current W7
outcome access. The required current state is therefore:

```text
CURRENT_W7_OUTCOME_ACCESS = NO
REAL_W7_CASES_USED = 0
```

## Git, storage, and recovery

- Branch: `topconf-w7-reconciliation`; baseline and origin both pointed at
  `be7c3bc...0bc8e22340b97` before this audit.
- No merge commits or force-push evidence were found in the audited history;
  remote state matched the local baseline.
- No model/checkpoint/audio blobs are tracked. Five large tracked blobs are
  scientific manifests/case maps, not model assets. The secret-pattern scan
  found no credential material.
- Active current V4/V6/runtime records use G:, `/mnt/g`, `/opt`, G:\WSL, or
  G:\AudiobookBench-Data targets. F: and C: references remain only in
  historical exclusion/migration records; they are not active runtime paths.
- `G:\W7-RECOVERY-KIT` self-check and asset verification passed. Existing W7
  and main Git bundles both validate; WSL export remains deferred while the
  mainline is active.

## Contradictions and blockers

The readiness result is fail-closed because the following contradictions or
evidence gaps cannot be silently resolved in an independent audit:

1. `W7_APPROVED_RUNTIME_ENVIRONMENTS_V4.json` says M1 is VERIFIED with torch
   `2.0.1+cu117`, but the actual `runtime_m1_vits` interpreter has no torch
   importable. Its shared M3 validation executor note does not make the M1
   runtime self-consistent.
2. The M1 offline download log explicitly records `VITS_LJS_NOT_FOUND`, while
   V4 later records a materialized and verified checkpoint. No first-
   materialization log or immutable chain from official Google Drive to the
   current loaded asset was found.
3. Older committed recovery and asset-identity audits still state that M1/M3/M5
   runtimes/assets were not created or that MFA was absent, while current V4/V6
   state says all approved runtime assets and environments are verified. These
   records are plausibly historical, but are not explicitly marked superseded;
   therefore the audit cannot treat the readiness record as contradiction-free.
4. Current V4/V6 summaries declare strict loads, synthetic smokes, and
   determinism PASS for M1/M3/M5, but raw reproducible execution logs were not
   found in the repository for independent replay without entering model
   execution.

```text
READINESS_CONTRADICTIONS_FOUND = YES
INDEPENDENT_READINESS_AUDIT = FAIL_CLOSED
```

## Recommended next action

Repair the evidence chain without changing frozen science: rebuild or relabel
the stale historical audits, make M1 either self-contained or explicitly
bind its shared executor as the authoritative runtime, record first
materialization provenance for `pretrained_ljs.pth`, and attach immutable raw
strict-load/synthetic/determinism evidence. Re-run this audit afterward.
Do not authorize or run formal W7 until those contradictions are closed by
explicit human review.
