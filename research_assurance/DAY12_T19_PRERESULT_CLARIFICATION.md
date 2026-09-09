# Day12 T19 pre-result procedural clarification

Date: 2026-09-06  
Label: **PRE-RESULT PROCEDURAL CLARIFICATION**

## Status and scope

T19 was underspecified in the original preregistration. The omission was
discovered before any Day12 P1 target↔synthetic cosine, D2
reference↔synthetic cosine, Spearman association, bootstrap CI, or other Day12
scientific result was computed or observed.

This clarification freezes only the minimum mechanical semantics needed to
execute the already preregistered silence-shortcut diagnostic. It does not
alter the P1 hypothesis, ECAPA backend, similarity definition, frozen B1b
scores, case population, detector method, or thresholds. No result-dependent
choice was used. This document does not rewrite the original preregistration.

## Authoritative frozen basis

- `research_assurance/WEEK2_A2_LEAKAGE_SHORTCUT_AUDIT.md:118-127` identifies
  the risk as different silence statistics for replaced utterances, states that
  the fixed-gap construction can interact, and requires a diagnostic report of
  the pause/silence feature distribution shift between removed-real and
  inserted-synthetic segments.
- `research_assurance/A2_REQUIRED_TEST_MAP.md:29` and
  `research_assurance/week2a_test_registry.yaml:331-350` register T19 as a
  DATA integration test, requiring A2 WAVs and the sidecar, for
  `DAY12_ANALYSIS_GATE` only. Its registered assertion is a diagnostic report,
  not a detector or performance claim.
- `THREAT_MODEL_WEEK2_DRAFT.md:54-70` freezes the complete removed target
  utterance interval and the full replacement bounds; the full attack includes
  both 400-sample blend zones. `THREAT_MODEL_WEEK2_DRAFT.md:76` freezes mono
  16-kHz analysis and 25-ms/10-ms `-45 dBFS` silence handling.
- `src/audiobookbench/temporal/grid.py:1-15` defines complete 400-sample
  frames on a 160-sample hop. `src/audiobookbench/temporal/frame_features.py:16-19,
  31, 144-148, 183-184` defines the pause indicator and its sequence-level mean
  as `pause_ratio`.
- `research_assurance/WEEK2_DAY12_MECHANISM_PREREG.md:47-56` classifies D1-D4
  as diagnostics only; `research_assurance/week2a_gate_registry.yaml:57-66`
  requires these diagnostics but forbids promotion of one into a new metric.

## Frozen T19 execution contract

| Field | Frozen execution rule |
| --- | --- |
| Purpose | Diagnostic disclosure of a possible silence-shortcut shift; it does not determine detector performance, P1, case inclusion, thresholds, or claims. |
| Population | Every Day10 sidecar row, retained by `paired_case_id` and split. The denominator includes all realized rows; a non-success row is retained as non-computable with its failure status. The current frozen population is 23 realized successful cases (11 train / 6 val / 6 test). |
| Removed-real region | Load each row's `source_audio_path` as mono 16-kHz audio and use the complete source utterance `[0, source_real_num_samples)`. This is the complete target utterance removed from the clean timeline. |
| Inserted-synthetic region | Load each row's `manipulated_audio_path` and use `[attack_start_sample, attack_end_sample)`. This is the full inserted replacement, including the two frozen 400-sample blends, because T19 registers the inserted segment rather than a strict-core-only analysis. |
| Signal / feature | On each region independently, use the frozen Day5 `TemporalGrid` (400 samples / 25 ms frame, 160 samples / 10 ms hop; complete frames only). A frame is pause=1 iff `20*log10(rms + 1e-12) < -45 dBFS`; the region `pause_fraction` is the arithmetic mean of its frame pause indicators. |
| Per-case quantity | `pause_fraction_delta = inserted_synthetic_pause_fraction - removed_real_pause_fraction`. This is descriptive only. |
| Aggregation | Case (`paired_case_id`) is the reporting unit. Frame values only form each case's two pause fractions; frames are never treated as independent cases. |
| Splits | Report the raw per-case rows and descriptive summaries for train, val, test, and `all`. Do not pool away split labels, filter a split, or run inferential testing. |
| Summary | For each split and `all`, report realized/computable/unavailable case counts and the mean and median of both pause fractions and their paired delta. The per-case table is the distribution-shift evidence. |
| Threshold / test statistic | None. T19 is report-only: no significance test, decision threshold, correlation, or detector threshold is introduced. |
| PASS semantics | PASS iff each successful retained case has exactly one finite, provenance-valid pair of pause fractions from the frozen paths and bounds; non-success rows are retained and counted; total and per-split summary rows are emitted; and the result is labelled DIAGNOSTIC ONLY. A high, low, zero, or mixed delta cannot itself fail T19. FAIL means missing/unreadable/nonfinite inputs, invalid bounds/sample rate, missing required row(s), or an absent/mislabeled report. |
| Interface | Implement `run_t19(repo_root: Path) -> dict[str, object]` in `experiments/day12_mechanism/run.py`; invoke only this diagnostic with `python -m experiments.day12_mechanism.run --t19-only`. No P1/D2 computation is permitted in this mode. |

## Frozen B1b and D2 status

P1 expressly names B1b case AUROC/AUPRC at **S1 and S2**
(`WEEK2_DAY12_MECHANISM_PREREG.md:21-28`). Therefore both S1 and S2 are
co-primary P1 scales; neither is a post-result secondary choice.

D2 is explicitly **DIAGNOSTIC ONLY**
(`WEEK2_DAY12_MECHANISM_PREREG.md:47-56`). D2 cannot determine case inclusion,
the P1 definition, embedding backend, metric selection, or B1b scale selection;
it is reported separately from P1.

## Canonical Day12 paths (frozen before numerical execution)

- `results/day12/per_case_similarity.csv`
- `results/day12/p1_association.csv`
- `results/day12/p1_bootstrap_ci.csv`
- `results/day12/d2_reference_synthetic_cosine.csv`
- `results/day12/t19_silence_distribution_shift.csv`
- `results/day12/t19_silence_distribution_shift_report.md`
- `results/day12/execution_record.json`
- `results/day12/day12_output_hashes.json`

These are canonical future output paths only. This clarification creates none
of them and contains no Day12 numerical result.

