# RQ1 Failure Accounting and Retry Draft v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

## Terminal categories

| Category | Meaning | Counts in denominator? | Retry candidate? |
|---|---|---:|---:|
| `SOURCE_INVALID` | Source missing, corrupt, unauthorized, or fails input contract | Explicit accounting; final estimand policy TBD | No unless a predeclared source replacement rule exists |
| `REFERENCE_INVALID` | Reference missing, invalid, disallowed, or violates policy | Explicit accounting; paired unit remains unresolved | Only under a predeclared deterministic reference retry |
| `GENERATION_FAILURE` | Generator cannot produce an output after allowed attempts | Explicit terminal state | Only within fixed retry budget |
| `QUALITY_GATE_FAILURE` | Output fails audio/content/speaker/quality/alignment gate | Explicit terminal state | Only within fixed retry budget; no quality-based cherry-picking |
| `MODEL_LOAD_FAILURE` | Checkpoint or architecture cannot load | Explicit run/model failure | Only for infrastructure retry, not model selection |
| `INFERENCE_FAILURE` | Authorized input cannot produce a valid model output | Explicit terminal state | Only within fixed retry budget |
| `INVALID_OUTPUT` | Output non-finite, malformed, wrong length/unit, or violates contract | Explicit terminal state | Only if deterministic rerun is authorized |
| `GT_INVALID` | Label/span/manifest invalid or inconsistent | Explicit terminal state | No silent relabeling |
| `INFRASTRUCTURE_FAILURE` | Host, storage, driver, process, or external service failure | Explicit operational state | Yes only when the same case/config is rerun and budget is recorded |
| `SCIENTIFIC_VALID_CASE` | Case passed the declared validity gates and has an analyzable output | Eligible | N/A |

## Denominator policy candidate

The run ledger must contain one terminal row for every planned case-condition-
model invocation. Primary denominators must be defined before authorization,
with at least two reported views where appropriate:

1. **Planned-unit accounting:** all planned units, including terminal failures.
2. **Valid-case estimand:** only `SCIENTIFIC_VALID_CASE` units, with the count
   and failure composition reported beside every metric.

An invalid or missing case is never treated as a zero score, never silently
dropped, and never replaced by a new source without a documented protocol rule.
If a primary estimand is not defined under the observed missingness pattern,
report `NOT_ESTIMABLE` and preserve the ledger.

## Retry policy candidate

- Only `INFRASTRUCTURE_FAILURE`, and possibly deterministic `GENERATION_FAILURE`
  or `INVALID_OUTPUT`, may be retry-eligible.
- A retry uses the same source, configuration, model, target, and namespace
  lineage unless the protocol explicitly says otherwise.
- Every attempt consumes a predeclared attempt budget and remains in the ledger.
- A quality-based retry may not be used to search for a better result.
- `GT_INVALID` and unblinding incidents do not become valid through retry.

## Mandatory invariant

```text
NO SILENT CASE DROPPING
```

Any missing case has an explicit terminal state, reason, timestamp, and
provenance. Closure is blocked until planned cases and ledger rows reconcile.
