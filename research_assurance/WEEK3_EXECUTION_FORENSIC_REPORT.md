# Week3 Execution Forensic Report

## Executive Summary

The immutable source log contains 115 attempts: 46 terminal environment failures and 69 successes. The rows reconstruct into five contiguous invocations: two failed 23-case batches followed by three successful 23-case batches. The 46 failures emitted no usable waveform and no score, but later full-case re-executions mean the existing 23-case scientific table is not an admissible frozen closure. The detailed structured index is `results/week3_stage_a_f5/forensics/week3_attempt_lineage.json`.

## Frozen Policy

The frozen Week3 contract fixes 23 cases, no replacement, and at most one same-case retry only for `infrastructure_transient`. Terminal outcomes are terminal. The scientific population is the successful-generation set, but no outcome-driven rerun is permitted.

## Observed Attempt History

| invocation | time (UTC) | environment | result |
|---|---|---|---|
| 001 | 02:57:44 | `E0068F3E…` | 23 terminal failures |
| 002 | 03:07:58 | `990ECD8D…` | 23 terminal failures |
| 003 | 03:12–03:33 | `73ACF078…` | 23 successes |
| 004 | 03:40–04:05 | `38F5D6C8…` | 23 successes |
| 005 | 04:09–04:31 | `E75FD44A…` | 23 successes |

## Invocation Reconstruction

Invocation boundaries are evidence-defined by contiguous timestamp and environment-hash batches. Historical rows have no authorization, run, invocation, preflight, runner, evaluator, or case-table hash; those fields remain `UNKNOWN` in the lineage index rather than being inferred from timestamp proximity.

## 46 Failure Analysis

All 46 rows are `FAILED`, `infrastructure_terminal`, and have an empty `raw_output_hash`. The first 23 fail at `torch.manual_seed` while accessing `torch.xpu._is_in_bad_fork`; the second 23 fail at the same seed path while accessing `torch.xpu.manual_seed_all`. In the current runner, inference precedes `write_audio`, sidecar construction, GT validation, and scoring; therefore these failures are proven to be before those outputs. No scientific output was observed from the 46 rows.

## 69 Success Analysis

Each case has three successful attempt rows. The raw-output hashes are identical per case across the three logged success batches, while the prior waveform/sidecar files were overwritten by later runs. Complete historical byte-level comparison is therefore unavailable. No historical success row can be bound to a score timeline or scientific JSON with the evidence retained.

## Authorization Provenance

The current `authorization.json` validates against current source hashes and has SHA256 `3455E63AFEE47124108D93EA01804F452C2397A41D9FB744B1DD38C000AFEEC0`. It cannot be proven to apply to any historical row because the rows contain no authorization hash and prior authorization artifacts are not retained separately.

## Environment Provenance

Five environment hashes occur. The final environment `E75FD44A…` matches the current readiness manifest; the four earlier variants cannot be fully bound to authorization/preflight from retained evidence. The two failure causes are runtime XPU compatibility failures, not scientific generation outcomes.

## Final Accounting Provenance

`final_accounting_rows` receives the current invocation’s `final_attempts` list and `cases.csv` is written from that list. It does not read the complete append-only history. This explains the current 23 SUCCESS / 0 FAILED table despite 115 historical rows.

## Scientific Writer Provenance

The evaluator source bound to the historical scientific outputs wrote authorization, review, config, environment, case-table and score-manifest hashes. It did not write `f5_source_identity_sha256` or `f5_local_source_manifest_sha256`, although both fields are present in the existing scientific JSON. The current future writer now emits these fields, but that does not reconstruct historical provenance. No historical source version that emits those fields was recovered: `PROVENANCE_SOURCE_NOT_RECOVERED`.

## Protocol Deviations

1. Terminal failures were followed by three later full-case successful executions.
2. Final accounting was latest-invocation-only rather than complete-history-derived.
3. Historical authorization and preflight binding is absent.
4. Existing scientific JSON contains provenance fields unexplained by its authorization-bound evaluator source.

## What Scientific Outputs Were / Were Not Observed

No usable waveform or score was produced by the 46 failures. Current scientific hashes recompute, and current H1/H2/H3 numbers are internally reproducible from current artifacts, but historical score binding and complete output provenance are not proven. Therefore those numbers are `INTERNALLY_REPRODUCIBLE_EXISTING_ARTIFACTS`, not a closed Week3 result.

## What Can Be Proven / What Remains Unknown

Proven: row counts, failure classes, failure exceptions, empty raw hashes, fixed case/seed/config lineage, five environment variants, current hash recomputation, and current 23-case ID alignment. Unknown: historical authorization/preflight, historical evaluator binding, historical score observation before the final artifacts, and complete byte identity of overwritten artifacts.

## Integrity Consequences

`WEEK3 = NOT SCIENTIFICALLY COMPLETE`. A future clean run requires independent scientific adjudication and a distinct authorization/run identity; this report does not authorize one.

## Engineering Corrections Applied

Future formal paths now require run/invocation identity, per-attempt authorization provenance, terminal-history/restart fail-closed checks, complete-run accounting validation, evaluator-side source/F5 provenance fields, and a new run-scoped output namespace. TEST_ONLY fixture paths remain the only test execution path.

## Open Scientific Adjudication Question

Whether a clean prospective Stage-A rerun is scientifically admissible remains for the next independent Terra decision.
