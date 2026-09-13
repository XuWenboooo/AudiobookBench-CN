# RQ1 Statistical Simulation Report v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Data source: **SYNTHETIC_ONLY**
Run date: **2026-09-13**

## Synthetic-only disclaimer

This report uses no Week1--5 effect sizes, Phase3/3R outcomes, model outputs,
audio, labels, Level-2 population, or real benchmark. The synthetic effect grid
(`null`, `small`, `moderate`) is symmetric and chosen for design sensitivity,
not to reproduce or optimize toward an observed result. The script is
`tools/topconf/simulate_rq1_statistics.py`; it generates a speaker -> source ->
mechanism hierarchy and compares four resampling units.

## Simulation assumptions

- Paired source-condition deltas are generated with centered mechanism offsets.
- Speaker-cluster dependence is varied by a synthetic `speaker_rho` parameter.
- The expected super-population effect is the declared synthetic effect; no
  scientific interpretation is attached to its magnitude or direction.
- Percentile bootstrap intervals use a fixed seed and are assessed against the
  known synthetic effect.
- `case_level` intentionally ignores hierarchy; `speaker_cluster` resamples
  complete speaker clusters; `hierarchical_speaker_case` resamples speakers
  and then source units within speaker; `paired_source` resamples source units
  while retaining all mechanism rows for each source.

## Executed candidate grid

The transparent host smoke grid used 16 cells:

```text
sources       = [200, 400]
speakers      = [50, 100]
mechanisms    = [3]
speaker_rho   = [0.0, 0.8]
effects       = [0.0, 0.2]
replicates    = 5 per cell
bootstrap     = 50 resamples per replicate
seed          = 20260913
```

The module also accepts the broader planning ranges `sources=[200,300,400,
500,600]`, `speakers=[50,75,100,125,150]`, `mechanisms=[3,4]`, multiple
correlation levels, and null/small/moderate/large effects. The reduced grid was
chosen to keep this CPU-only planning check bounded; it is not a final power
analysis.

## Bootstrap comparison

Values below are unweighted averages across the 16 executed cells. They are
simulation diagnostics, not estimates for the project.

| Strategy | Mean coverage | Mean CI width | CI-width SD | Mean absolute bias |
|---|---:|---:|---:|---:|
| case-level | 0.763 | 0.0939 | 0.0093 | 0.0290 |
| speaker-cluster | 0.888 | 0.1351 | 0.0177 | 0.0290 |
| hierarchical speaker→case | 0.962 | 0.1618 | 0.0231 | 0.0290 |
| paired-source | 0.813 | 0.1098 | 0.0127 | 0.0290 |

In the null/small-effect smoke grid, increasing synthetic speaker dependence
from `rho=0.0` to `rho=0.8` produced the following directional sensitivity:

| Strategy | Coverage at rho=0.0 | Width at rho=0.0 | Coverage at rho=0.8 | Width at rho=0.8 |
|---|---:|---:|---:|---:|
| case-level | 0.850 | 0.0939 | 0.675 | 0.0940 |
| speaker-cluster | 0.900 | 0.1142 | 0.875 | 0.1560 |
| hierarchical speaker→case | 0.975 | 0.1456 | 0.950 | 0.1779 |
| paired-source | 0.900 | 0.1116 | 0.725 | 0.1080 |

The pattern is consistent with the planning concern that treating correlated
rows as independent can produce intervals that are too narrow when speaker
dependence is high. Hierarchical intervals are wider and had better coverage in
this particular synthetic configuration. This does not make hierarchical
bootstrap the final choice: the real statistical unit, number of conditions,
missingness, and estimand must be locked independently.

## Candidate sample-size bands

The simulation supports sensitivity bands rather than a final N:

- `300 sources / 100 speakers / 3 mechanisms`: low-budget candidate;
- `400 sources / 120 speakers / 4 mechanisms`: target candidate;
- `500 sources / 150+ speakers / 4 mechanisms`: stretch candidate.

Larger source and speaker counts generally reduce estimator variance, while
more mechanisms increase paired rows but also increase dependence and multiple
comparison burden. The final band must account for expected failure attrition,
rights, compute, and the verified model core; it cannot be selected from an
observed gap.

## Limitations

The smoke run uses only five population replicates and fifty bootstrap
resamples per cell, so coverage values are noisy. The generator has a simple
Gaussian hierarchy, balanced speaker assignment, centered mechanism offsets,
and no missingness or invalid-case process. It does not model threshold
selection, LD@DR95 feasible-set emptiness, multiple-testing families, metric
nonlinearity, or real audio quality gates. These are required questions for a
future authorized planning run and are not silently resolved here.

## Phase 4 questions

Before any final freeze, reviewers should decide:

1. Is the statistical unit the source, source-condition, or a
   speaker-clustered estimand?
2. Should the primary interval resample paired sources, speakers
   hierarchically, or a predeclared alternative?
3. How are invalid and terminal failure cases represented in the estimand and
   sensitivity views?
4. What condition grid and multiplicity family are fixed before outcomes?
5. What bootstrap count is computationally and statistically adequate?

No answer in this document authorizes a real-data run.
