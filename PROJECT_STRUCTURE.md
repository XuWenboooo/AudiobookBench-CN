# Project Structure and Evidence Boundary

## Historical Pilot (frozen)

The existing Week1–5 code, results, reports, and assurance archive remain historical pilot material. Week4 closure is PASS with primary H4 NOT_REPORTABLE; the two `NO_VALID_ADAPTIVE_PARENT` cases remain preserved. Week5 Exp6 is CANCELLED_UNEXECUTED and Exp7 is NOT_AUTHORIZED. These artifacts are not moved or rewritten by the TopConf preparation.

## TopConf Confirmatory Phase (protocol hardening; not started)

The `topconf-dl-robustness` branch/worktree contains governance and protocol skeletons under `research_assurance/topconf/`. These documents define prerequisites and open questions; they do not authorize experiments.

## Working rules

- Keep historical references stable; prefer additive documentation.
- Keep pilot and confirmatory data classes separate.
- Lock protocol, threat model, baselines, leakage policy, and release manifest before execution.
- Record all failures and deviations; do not curate them away.
- Use Level 0 (historical pilot), Level 1 (development), and Level 2
  (outcome-blind confirmatory) labels consistently; Week1–5 are Level 0 only.
- Do not treat a protocol draft as authorization. Unknown values remain
  `TBD_BEFORE_AUTHORIZATION`.
- Do not run F5, CosyVoice2, detector/localizer, evaluator, bootstrap, training, or new scientific generation during preparation.

## Planned future layout

```text
research_assurance/
  archive/                 # Week1–5 historical governance and closure
  topconf/                 # confirmatory preparation and preregistration drafts
configs/                   # existing project configs; no historical rewrite
experiments/               # existing experiment code; untouched in preparation
results/                   # existing historical outputs; untouched in preparation
```
