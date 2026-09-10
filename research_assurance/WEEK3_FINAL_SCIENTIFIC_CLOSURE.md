# Week 3 Final Scientific Closure

## Identity

| Field | Value |
|---|---|
| Project | AudiobookBench-CN |
| Milestone | Week 3 Stage-A |
| Clean run | `clean_rerun_20260907_01` |
| Review mode | Independent post-run read-only evidence review |
| Review date | 2026-09-10 |
| Review commit before closure write | `0c8dc55eaa0b7d4027fa641d9514a9fa3bbaeced` |
| Closure classification | `INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL` |

## Independent review decision

Phase A completed with no blockers. The retained evidence is sufficient for
Week 3 scientific closure within the frozen claim boundary.

```text
WEEK3_CLEAN_RERUN_VALID = PASS
AUTHORIZATION_CHAIN = PASS
NAMESPACE_ISOLATION = PASS
F5_SOURCE_IDENTITY = PASS
POPULATION_IDENTITY = 23/23 VERIFIED
SEED_CONTRACT = PASS
GENERATION_SEMANTICS = PASS
ATTEMPT_ACCOUNTING_COMPLETE = YES
CASE_EVIDENCE_CHAIN = PASS
B1B_S2_FROZEN_SEMANTICS = PASS
H1_INDEPENDENTLY_RECOMPUTABLE = YES
H2_INDEPENDENTLY_RECOMPUTABLE = YES
H3_INDEPENDENTLY_RECOMPUTABLE = YES
EVALUATION_REPRO_REEXECUTION_VALID = YES
BOOTSTRAP_PROTOCOL_MATCH = YES
HISTORICAL_COPY_FORWARD = NO
CLOSURE_TEST_REPAIR_VALID = YES
SCIENTIFIC_OUTPUT_MUTATION = NO
BLOCKERS = NONE
```

## Clean execution

| Quantity | Value |
|---|---:|
| Planned cases | 23 |
| Successful cases | 23 |
| Failed cases | 0 |
| Attempts | 23 |
| Retries | 0 |

Every case is bound to `run_id=clean_rerun_20260907_01`,
`invocation_id=invocation_20260907_01`, the canonical authorization, its
frozen seed, raw output, standardized waveform, sidecar, sample-first GT, and
evaluator evidence. The historical namespace remains separate and unchanged.

## Authorization and provenance

| Artifact | Value |
|---|---|
| Authorization | `results/week3_stage_a_f5_runs/authorization.json` |
| Authorization SHA-256 | `A094979BBAC9E2EE8D9F07E6B7A0268D060E73C60A5AB632AE0FEDC2F56D3DC5` |
| Scientific-integrity adjudication SHA-256 | `B00AE92F98FFD95D447123184632124ADDCB1995F221A0D411ECB3C60613849D` |
| Namespace verification SHA-256 | `B3CCB4C525659255E4FFC041928983FF35AF331629C2D0E19EF1EA42F01FC04B` |
| F5 source commit | `82fc4fe622fe36047d1dff99b550e6018181ea11` |
| F5 model revision | `84e5a410d9cead4de2f847e7c9369a6440bdfaca` |
| F5 local source manifest SHA-256 | `598BBC66E471B80D41C55F677C5F01C1BF6A81E37EC7FC23E62D013F3F60310E` |
| Clean score manifest SHA-256 | `E12E2DC6A707D14DE4AB34E07B8D5722523BF5B10E9C6FC7D76AE94FBEE2B660` |

The authorization records `prior_results_observed=true` and
`scientific_parameters_changed_after_observation=false`. This run is an
integrity reexecution of the frozen protocol, not a blind replication or a
new prospective-confirmatory study.

## Scientific results

All estimates use the frozen B1b/S2 evaluation and case bootstrap with
`N=2000`, seed `20260905`, percentile 95% CIs, and minimum finite threshold
1900. Observed finite replicates were 2000 for H1, H2, and H3.

### H1 — full-region transfer

| Estimand | Estimate | 95% CI |
|---|---:|---|
| `AUROC_full` | 0.46615006369633477 | [0.41167599331797444, 0.5207910047488823] |
| `AUPRC_full` | 0.07938101487170668 | [0.0673502880477091, 0.0949334311192232] |

### H2 — boundary/core decomposition

`DELTA_BOUNDARY_CORE = mean_score_boundary - mean_score_core`

| Estimand | Estimate | 95% CI | Available | Unavailable |
|---|---:|---|---:|---:|
| `DELTA_BOUNDARY_CORE` | 0.07618689502661326 | [0.04600431774168675, 0.10360243154560674] | 23 | 0 |

### H3 — full/core blend-exclusion effect

| Estimand | Estimate | 95% CI |
|---|---:|---|
| `DELTA_FULL_CORE_AUROC` | 0.00772253796155048 | [0.0025392724782134085, 0.012855862620052524] |
| `DELTA_FULL_CORE_AUPRC` | 0.0037096921853009834 | [0.0015907003838719254, 0.0059981408626662664] |

The H1 and H3 values and CIs were independently recovered from the
precommitted evaluator outputs. H2 was independently checked from the
case-level zone results with all 23 cases available.

## Evaluation-only reproducibility repair

The evaluation-only repair is limited to cryptographic recovery of
precommitted evaluator outputs:

- repair authorization SHA-256: `DC21FB729909422483ACE980863815279BB6E4A6884B25620EDDD8D092DC5925`;
- original clean score manifest SHA-256: `E12E2DC6A707D14DE4AB34E07B8D5722523BF5B10E9C6FC7D76AE94FBEE2B660`;
- 23/23 score vectors recovered with exact commitments;
- 23/23 waveform commitments verified;
- H1/H3 point estimates and CIs matched exactly;
- `generation_invoked=false`;
- scientific semantic change: `NONE`.

## Historical disposition

`results/week3_stage_a_f5/` remains `FORENSIC_ONLY`. Its 115 attempts,
including 46 terminal failures and 69 historical successes, are retained for
integrity provenance. The historical scientific-looking outputs are not
closure-eligible and no historical waveform, score, accounting row, or result
was copied forward as a scientific input to the clean run.

## Closure-test repair

The stale-state assumption in the missing-authorization tests was repaired by
using isolated `tmp_path` authorization paths while retaining the real
production fail-closed path. The targeted tests passed 23/23. The complete
relevant F5 environment suite passed 123 tests with 0 failures, 0 skips,
0 xfails, and 0 xpasses. No production scientific semantics were changed.

## Scientific interpretation boundary

Within the tested F5-TTS condition and frozen B1b/S2 protocol, temporal
localization performance is weak. The predefined boundary/core decomposition
has a positive `DELTA_BOUNDARY_CORE`, and the full-region metrics are slightly
higher than the core-only metrics.

These observations do not establish universal TTS detector failure, open-world
impossibility, a causal crossfade mechanism, a statistically significant F5
versus CosyVoice difference, or a universal claim about generated speech. The
clean rerun occurred after prior invalid results had been observed, so it is
not a blind or prospective replication.

## Limitations

- The tested generators are limited to the documented conditions.
- The historical run is forensic-only and cannot be used as a closed result.
- H2 is a predefined descriptive association, not causal proof.
- F5 versus CosyVoice is not treated as a preregistered direct significance
  comparison.
- AISHELL-3 training independence remains `UNKNOWN` unless an explicit frozen
  admission criterion establishes otherwise.

## Final verdict

```text
WEEK3_SCIENTIFIC_CLOSURE = PASS
WEEK3 = SCIENTIFICALLY COMPLETE
```
