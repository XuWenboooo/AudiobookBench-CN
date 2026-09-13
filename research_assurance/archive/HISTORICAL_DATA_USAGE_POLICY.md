# Historical Data Usage Policy

```text
DATA_CLASS = LEVEL_0_HISTORICAL_PILOT
WEEK1_5_DATA_ROLE = PILOT_ONLY
WEEK1_5_CONFIRMATORY_USE = PROHIBITED
```

## Permitted uses

Week1–5 material may be used for hypothesis generation, debugging, evaluator
development, sanity checks, visualization, preliminary/pilot motivation, and
regression testing. These uses must preserve the original population,
protocol, and provenance labels.

## Prohibited uses

Week1–5 material must not be used as a top-conference final confirmatory test,
for final attack hyperparameter/model/threshold selection, to claim independent
validation, or as after-the-fact confirmation of a new hypothesis.

No historical result may be repackaged as confirmatory data. The Week4
`NOT_REPORTABLE` outcome remains a valid frozen terminal state and must not be
recomputed by excluding the two no-parent cases.
