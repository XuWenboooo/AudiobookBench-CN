# W7 M2/M4 real-adapter integration — synthetic validation only

Status: `M2_REAL_ADAPTER = PASS_SYNTHETIC_VALIDATED`; `M4_REAL_ADAPTER = PASS_SYNTHETIC_VALIDATED`.
This is engineering validation against purpose-built synthetic waveforms only. It is not W7 execution readiness or authorization.

## Frozen semantics and implementation

- M2 family `cross_speaker_boundary_control` wraps `audiobookbench.topconf.w7_candidate_transforms::cross_speaker_boundary`. It selects the lexicographically next case ID in the same distribution whose `source_id` differs, rank 1 after deterministic ordering. It uses the first mono window, preserves the frozen target span, uses 400 linear crossfade samples, and ends terminally if no valid distinct-source reference exists.
- M4 family `same_speaker_splice_crossfade_control` wraps `audiobookbench.topconf.w7_candidate_transforms::same_speaker_splice_crossfade`. For each original-source target interval it selects a complete same-case context of target duration, preferring left and falling back to right. It preserves target span and uses the frozen 400-sample linear crossfade. Missing complete context is terminal.
- Adapter module: `src/audiobookbench/topconf/w7_m2_m4_adapters.py`. Harness integration: `src/audiobookbench/topconf/w7_synthetic_harness.py`. Selectable mode is `real_adapter_synthetic_fixture`; the existing `synthetic_mock` remains available. No M1/M3/M5 integration was added.
- The frozen transform source blob at the baseline matches its blob at the recorded mechanism-definition revision (`834263a4385f9aa79f59f65d1c6439f0cff5ea1f`); no transform semantics were changed.

## Fixture coverage and deterministic output evidence

Fixtures live in `tests/topconf/fixtures/w7_m2_m4_adapter_cases_v1.json`. Successful purpose-built cases: M2 12 and M4 17 (the suites additionally include terminal failure cases). Coverage includes reference ordering and identity, no-reference/context failures, 1/2/3/4/20 intervals, start/end targets, short/exact/long context, edge fades, 8 kHz normalization, mono conversion, and clipping. The probe `tools/topconf/probe_w7_m2_m4_adapter_determinism.py` was launched twice in clean Python processes. Schedule hashes, selected references/sides, byte-level output SHA-256 values, output sample counts, and full provenance objects were identical across the two runs.

Runtime identity (exact recorded runtime): Python `3.12.9`; NumPy `2.5.2`; Torch `NOT_USED`; torchaudio `NOT_USED`; resampler `numpy.interp_endpoint_aligned_v1`; OS/platform `Windows-11-10.0.26200-SP0`.

Output SHA-256 values (float32 output bytes):

| Fixture | SHA-256 | Fixture | SHA-256 |
|---|---|---|---|
| M2 `SYNTH_M2_DISTINCT` | `195d3101125ddcef47532b7731271d7bb667b1c7bd2918396c2981399de5a384` | M4 `SYNTH_M4_LEFT` | `8504a1702d86ce927d11edb1f786f98febfdb785acd0adaf2e0d94655db8b525` |
| M2 `SYNTH_M2_MULTIREF` | `eaf8b6990ea7df1104c669f5b35d96d98131e95a43ec0aa416855fa4c3cb941b` | M4 `SYNTH_M4_RIGHT` | `454b6dc66fa0045197fe23ba641ae5f625bf92ccf7f9bd755ca4e228cd9642c1` |
| M2 `SYNTH_M2_SINGLE` | `47b48cbcdf7638cc20e96931aa255eee3a69c1419baf21e554eb1e2dc2ae0097` | M4 `SYNTH_M4_PREFERLEFT` | `d47b751d826b4641d463947a27ee24da988366321c60fcb4b878258db5298d0d` |
| M2 `SYNTH_M2_MULTI` | `16f39a11eab62b72438f4dfceaf47bf0a2f7d8276f7019b1fd365f6312cf0d05` | M4 `SYNTH_M4_FALLBACK` | `e69f73f936b0d6eaa88f94706560cdd651514d337e20df44bc689f2a04d12c69` |
| M2 `SYNTH_M2_MULTI2` | `9a93c89998112537b68e39d50a1970fa411f17715f3ecbcb90b5d0b302e8dfa1` | M4 `SYNTH_M4_SINGLE` | `1c1abbc4f3c426383dbf0fcf1c4122734743901fd59387ac6a9f0cdbebe61cc7` |
| M2 `SYNTH_M2_START` | `52f514a521ec68a63f5c126e25e6a7dcf2192a38aae536b554befab42b7c2ea7` | M4 `SYNTH_M4_MULTI2` | `e5025b1e46b5cce9d20be02f45fe1dd9f980106383d1a6b995970ebcedd5e3d1` |
| M2 `SYNTH_M2_END` | `dd3fc4c379b2a6f72fcd7416aad374a27a6ced8a8cdc1304cf66b3b6f16c3ba4` | M4 `SYNTH_M4_MULTI3` | `6c8dbcb41d9670a966802a5e68e133c4d32e07d8daf743ded129879f497459d1` |
| M2 `SYNTH_M2_SHORTREF` | `64d91d910ddc47cf66c6eef094cb31d53ce2af1fd69327c4681cc04dd8b4fb1c` | M4 `SYNTH_M4_MULTI4` | `bfe546ccfb6f0c0ad4ae58f21cd79e3ddd49465232ff663dff62b82e8c1c35c7` |
| M2 `SYNTH_M2_8K` | `6965de33cc76e6058672b03b58b64935af3d7477fb9c82985401ad9ca058caf2` | M4 `SYNTH_M4_MULTI20` | `21eaa139bda8726f5114e064879980ca7c652995057515e40bfdf55906607333` |
| M2 `SYNTH_M2_CLIP` | `c9687f9573e201569a48c408518756e7644c1e1cf00292fe4a825874b2080ee9` | M4 `SYNTH_M4_START` | `4692fc0d46f1a270463fe1c766d4be82d8c7cbfdaa94bdabeeb895cbf6bd5660` |
| M2 `SYNTH_M2_MULTI4` | `ae80e963bcb1702a9ba7698cd5fea448803d2bd0fd7bc7998aec638e82964895` | M4 `SYNTH_M4_END` | `f30c7dd81eec0f7c095107b9a33ce2d4367f716c299b24bf3cf68e301bbf1ecc` |
| M2 `SYNTH_M2_MULTI20` | `61061209396d87ed6085575fcceff3163d19075fb5b2e765ac4bd02785e8c551` | M4 `SYNTH_M4_EXACT` | `994e6e2ca31646980f13772d7ae8b433d297019a5d0ed488d5442f8f88439790` |
|  |  | M4 `SYNTH_M4_LONG` | `d9492fe235978bdcbb3a800bfb36c0b48844548a0d64f66e75397f4d565e74e5` |
|  |  | M4 `SYNTH_M4_8K` | `0e70d7c4b2a52dbff24425d02aaa5d20f46971b2a1ebe7f6d431096ce8b9ff39` |
|  |  | M4 `SYNTH_M4_CLIP` | `07899659e55b2db88ef272218d4a765ce447d353f5474920e53af861329a1e67` |
|  |  | M4 `SYNTH_M4_CROSSFADE400` | `9290829fa6a121b227f933da302a1bc3001405f4c500b237aff5e98d688d0e38` |
|  |  | M4 `SYNTH_M4_CROSSFADEEDGE` | `bb72e511bd68eecaf06a1bb8650effd1727ba5b78a3eb137be8d5861bd719f43` |

## Numerical crossfade and support

Independent test uses the frozen 400-element float32 ramp `linspace(1, 0, 400, endpoint=False)`: first source weight `1.0`, last source weight `0.0025`, strictly decreasing. Complementary replacement weights therefore run from `0.0` through `0.9975`. At the right fade the frozen implementation applies the same ramp to replacement and its complement to source, so the last sample retains source weight `0.0025`. The target replacement itself is exact-duration resampled. With target `[600,1400)` in a 2400-sample source, observed changed support is `[200,1400)`; samples outside it are unchanged. Edge-limited fades follow the frozen `min(400, target_length//2, start, source_length-end)` rule. This matches the frozen implementation; no contradiction was found.

## Provenance, guards, and failures

Each adapter reports case/family/implementation/version/config digest/source and reference audio digests/source identities/target intervals and reference identity/crossfade and interpolation/output digest/failure/runtime/input and output sample rates/resampler. M2 records lexicographic rank and the different-source check. M4 records each `reference_side` and context window. The harness persists `adapter_provenance/<family>.json` for successful runs and terminal materialization failures.

The real-adapter mode rejects non-synthetic identity with `W7_REAL_EXECUTION_BLOCKED` before audio loading, adapter validation, or mechanism execution. It rejects Level-2 requests and any execution authorization. Synthetic mode is limited to the two frozen families and a runtime identity generated from the actual process. Missing M2 reference, invalid/empty selected reference, or missing M4 context produces terminal failure; there is no drop, imputation, alternate model, manual selection, or quality-based retry.

## Verification and limitations

- New adapter tests: 14 passed. Existing harness regression: 32 passed. Full `tests/topconf`: 225 passed (final run after M4 harness integration).
- Preregistration checker: PASS. W7 reconciliation checker: PASS (pre-execution only). `git diff --check`: PASS.
- V2, execution-readiness, authorization, formal metrics/gates, real W7 inputs, and Level-2 outcomes were not accessed or changed. Scientific inference count remains zero.
- Protected V6 source files and the manifest were not edited. The direct working-tree checker is not clean on this Windows checkout, and checking baseline Git blobs against the V6 manifest also finds eight stale SHA/size entries. The failing names are `W7_MECHANISM_EXECUTION_CONFIG_APPROVED_PREINFERENCE_V1.json`, `W7_P4_PROPOSED_FREEZE_PACKAGE_A_V1.json`, `LEVEL2_RQ1_POPULATION_MANIFEST_V3.json`, `LEVEL2_FRESHNESS_MANIFEST_V5.json`, `W7_P4_HUMAN_APPROVAL_RECORD_V1.json`, `W7_PILOT_PROTOCOL_V1.md`, `W7_PREREGISTRATION_HASH_MANIFEST_V5.json`, and `W7_PREREGISTRATION_HASH_MANIFEST_V4.json`. This pre-existing record mismatch is left untouched; the preregistration and reconciliation checkers independently pass.
- Limitations: only synthetic-purpose inputs were exercised; these results do not validate real W7 asset discovery, rights/readiness, case-specific mapping, real runtime compatibility, or any global execution gate. No formal W7 readiness is implied.
