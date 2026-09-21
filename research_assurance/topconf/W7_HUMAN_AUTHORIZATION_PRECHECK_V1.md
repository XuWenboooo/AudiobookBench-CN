# W7 Human Authorization Precheck v1

**Audit date:** 2026-09-21  
**Scope:** read-only pre-inference authorization precheck; no W7 inference, Level-2 access, confirmatory outcome access, protocol change, dataset change, model change, metric change, threshold change, bootstrap change, case-population change, or adapter change was performed.

## Machine decision

```text
CURRENT_STAGE = W7_HUMAN_AUTHORIZATION_PRECHECK
READY_FOR_HUMAN_AUTHORIZATION = NO
AUTHORIZED = NO
W7_FORMAL_PILOT_AUTHORIZED = NO
W7_EXECUTION_AUTHORIZED = NO
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
METRICS = NOT_MEASURED
```

The precheck is not a scientific result and does not authorize execution. Human authorization remains required after the blockers below are resolved by an authorized human review. This run stops here.

## Blocking findings

1. `GATE1_INTEGRITY = FAIL`: the frozen `W7_PILOT_PROTOCOL_V1.md` names the four localizers and two distributions but does not contain the exact required Gate 1 criterion: `GAP_OBSERVED_IN >= 3 DISTINCT localization paradigms AND >= 2 external distributions`.
2. `LLAMA_MIGRATED_ASSET_INTEGRITY = FAIL_NOT_MIGRATED_FULL_ARCHIVE`: the G: migration target contains the `split` directory, but the official `label_R01TTS.0.b.txt`, license/metadata, and `R01TTS.0.b.tgz.part` remain in the F: recovery cache. The official label inventory is 64,388 unique rows, but the full official package is not migrated.
3. `CASE_MANIFEST_INTEGRITY = FAIL_METADATA_ONLY_UNBOUND_AUDIO`: all 106,859 records have null source-audio and condition-audio hashes; all IDs use `w7plan_...` rather than the frozen case-identity schema's `w7case_...` form. Counts and uniqueness are otherwise consistent: 106,859 records, 427,436 planned condition rows, 0 duplicate IDs, and only PartialEdit/LlamaPartialSpoof distributions.
4. `PREREGISTRATION_HASH_COVERAGE = FAIL_COVERAGE_INCOMPLETE`: all 15 entries actually listed in `W7_PREREGISTRATION_HASH_MANIFEST_V1.json` re-hash exactly, but the manifest does not list the model-preflight/checkpoint identity, distribution-acceptance schemas, generic temporal GT adapter contract/schema, bootstrap/statistical configuration, or a W7 environment manifest.

These are scientific-readiness blockers. No in-scope repair was attempted.

## Checks performed

| Check | Result | Evidence |
|---|---|---|
| Git baseline and clean worktree | PASS | local HEAD `ae1796d85fd0a71370073ae32fd9f8a1688d092f`; branch `topconf-w7-reconciliation`; worktree clean before audit artifact creation |
| Remote verification | PASS | final `git ls-remote` matches local HEAD `a87a4712a7c2505acd25d223575fa0c549044678`; an earlier transient network failure was not treated as a mismatch |
| Protected W6/Phase 4.9R hashes | PASS | V3 `AFCE602F7A1F77F07BC18F05B78CB717DCDE3BFB6FC35289A26AB23F9DE4F8E4`; V5 `6F77CAE912CFF9D9AFD7C75C4EA0910298FC11454D7B8104DBF0551B0AFE821E`; Phase4.9R preserved/not reopened |
| Listed preregistration hashes | PASS_LISTED_ENTRIES | all 15 recorded/current SHA-256 values match; coverage failure is recorded above |
| Frozen protocol immutability scan | PASS_WITH_GATE_BLOCKER | no TODO/TBD/placeholder/future decision language; exact Gate 1 string absent |
| Localizer set and preflight | PASS | only CFPRF, MultiResoModel-Simple, SAL, BAM are W7-eligible; strict-load, synthetic smoke, temporal semantics, adapters and failure propagation are recorded PASS |
| PartialEdit migrated integrity | PASS | G: target has 42,471 WAV files; official E1 archive MD5 `1F489D2FF488DDD6C9B655127725AF2F`; SHA-256 `F4BB1A632EED8DDC66BB9285DE8B4BC07192D0539385EFE9AFC9EA04AEF3DDCB`; metadata SHA-256 `ADEECB0A7DD39A982223C07970E02E41CA5395EA3D484FCC6CE03174EBDF6CBC` |
| Llama distribution acceptance | PASS_FOR_PREPARATION_ONLY | 64,388 official labels; Zenodo record `14214149`; rights `PASS_WITH_ATTRIBUTION`; migrated full-archive requirement still FAIL |
| Junction and alias audit | PASS_FOR_MIGRATED_TARGETS | five active F: Junctions target G:; PartialEdit CSV, CFPRF FDN checkpoint, and Llama split metadata have identical F/G SHA-256; target-based canonical dedup is required |
| Duplicate discovery | PASS_FOR_CANONICAL_SCAN | PartialEdit G scan discovers 42,471 WAVs once; alias roots are one physical target by Junction target identity; case IDs have 0 duplicates |
| Checkpoint alias identity | PASS | physical G hashes: FDN `5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267`; PRN `88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36`; XLSR `B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9` |
| Execution manifest | PASS_NO_RUN | frozen no-run status; four conditions; two accepted distribution identities; paired-source bootstrap seed `20260914`, 2,000 replicates; output namespace `results/topconf/w7_pilot/` |
| Environment identity | PASS_READINESS_EVIDENCE_ONLY | model-specific frozen runtime evidence exists; no separate `W7_ENVIRONMENT_MANIFEST_V1` is present |
| Resampling/mechanism identity | PASS_STATIC_SYNTHETIC | frozen contracts/schemas are hash-stable; no scientific materialization or inference performed |
| Level-2 firewall and formal outcome absence | PASS | no W7 formal prediction/metric/outcome was accessed; historical Level-2 files remain protected and untouched |
| Evidence ledger and paper scaffold | PASS_NO_OUTCOMES | ledger and paper result tables retain NOT_MEASURED/NOT_STARTED states |
| Human authorization record | PASS_NO_AUTHORIZATION | `AUTHORIZED = NO`, `W7_FORMAL_PILOT_AUTHORIZED = NO`, `W7_EXECUTION_AUTHORIZED = NO` |
| Scoped tests | PASS | `134 passed in 9.29s`; `check_w7_preregistration.py` PASS; `check_w7_reconciliation.py` PASS; `git diff --check` PASS |

## Explicit non-actions

- No W7 inference or formal case execution.
- No Level-2 or confirmatory result read.
- No change to protocol, dataset, case manifest, model/checkpoint, adapter, metric, threshold, bootstrap, namespace, or protected hashes.
- No authorization record update.

## Required human action

An authorized human must resolve the four blockers, re-run the complete read-only precheck, inspect the immutable manifests and environment, and explicitly authorize W7 before any first inference. Until then, `READY_FOR_HUMAN_AUTHORIZATION` must remain `NO`.
