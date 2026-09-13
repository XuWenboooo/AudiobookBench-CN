# Protocol Consistency Review v1

Status: **PASS FOR PHASE-2 INFRASTRUCTURE PLANNING / NOT AUTHORIZATION**

## Completed decisions

- RQ1–RQ3, Level 0/1/2 separation, Whether-A/Whether-B, and Where levels
  are defined consistently across the protocol documents.
- The recommended primary RQ1 definition is `LD@DR95`: localization
  degradation under a predeclared detection-retention constraint. Detection
  and localization metrics are never subtracted across unlike scales.
- The gap gate requires at least 3 localization paradigms and 2 independent
  distributions. The attack gate requires the full preservation and budget
  conjunction. The TopConf gate rejects a closed world of only our dataset,
  model, and attack.
- All unknown population, threshold, budget, hardware, and statistical values
  remain `TBD_BEFORE_AUTHORIZATION`.

## Risks and blockers

- Novelty claims remain unsafe until a dated, primary-source literature and
  implementation review populates the ledger.
- Baseline code, checkpoints, licenses, formats, and compatible outputs remain
  unverified.
- No confirmatory execution is authorized; any one unresolved TBD in a
  required lock field is a blocker for confirmatory experiments.

## Integrity statement

This review did not run training, inference, evaluation, bootstrap, attacks,
defense, data generation, or scientific scoring. Archive files and scientific
code are outside the permitted modification set.
