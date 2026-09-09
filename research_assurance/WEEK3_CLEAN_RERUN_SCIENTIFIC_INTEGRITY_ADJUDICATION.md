# Week3 Clean Rerun Scientific-Integrity Adjudication

## Determination

`CLEAN_RERUN_SCIENTIFICALLY_ADMISSIBLE = YES`

`RERUN_CLASSIFICATION = INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL`

`prior_results_observed = true`

`scientific_parameters_changed_after_observation = false`

`SOL_GUIDANCE_REQUIRED = NO`

`historical_run_status = FORENSIC_ONLY`

`historical_run_excluded_from_scientific_closure = true`

`clean_rerun_may_support_week3_closure = true`

`requires_independent_post_run_closure_review = true`

## Scope and claim boundary

The historical Week3 Stage-A execution is `FORENSIC_ONLY` and is not eligible
for Week3 scientific closure.  Its retained results must not be copied forward
or presented as a closed scientific result.  A future clean rerun may reuse
only the frozen protocol inputs and, after independent closure review, may
support `WEEK3 = SCIENTIFICALLY COMPLETE`.

This authorization class is an integrity reexecution of the frozen protocol.
It is not a new prospective-confirmatory execution and does not change the
frozen model, cases, references, seed map, inference parameters, DSP,
detector, ground-truth, statistical, bootstrap, retry, or claim contracts.

## Required historical disclosure

1. An initial Week3 Stage-A execution occurred.
2. H1/H2/H3 values from that execution were observed before the clean rerun.
3. A later forensic review discovered integrity failures, including terminal-
   failure reexecution, accounting, and provenance defects.
4. The historical execution was therefore excluded from Week3 scientific
   closure.
5. Any future clean integrity reexecution occurs after those historical
   H1/H2/H3 results were observed.
6. No scientific parameter was changed after observing the invalid-run
   results.
7. The future clean run is an integrity reexecution of the already-frozen
   protocol, not a new blind prospective confirmation.

The frozen scientific contract remains unchanged: generator, F5 revision,
23-case population, source/reference pairs, seed map, inference parameters,
DSP, B1b, S2, GT, zones, H1, H2, H3, bootstrap N, bootstrap seed, CI rule,
and claim boundaries.

## Evidence basis

The historical execution reconstruction and its closure ineligibility are
recorded in `research_assurance/WEEK3_EXECUTION_FORENSIC_REPORT.md`
(`AD720F5D07A2C4BAB53899048B5D95E7DEBBA59CA69AF8972AA763F1B2F7C7CC`).
This adjudication supplies only the scientific-admissibility decision; it does
not create an active authorization or execute a rerun.
