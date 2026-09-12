# Week4 final readiness review and external authorization

Date: 2026-09-12  
Scope: `WEEK4_FINAL_READINESS_REPAIR_AND_AUTHORIZATION`  
Execution boundary: `NO_FORMAL_F5_OR_D0_RUNTIME_IN_THIS_REVIEW`

## Verdict

```text
WEEK4_FINAL_READINESS_REVIEW = PASS
ACTIVE_FORMAL_AUTHORIZATION_CREATED = YES
AUTHORIZATION_PREFLIGHT = PASS
READY_FOR_FORMAL_WEEK4_EXECUTION = YES

FORMAL_F5_GENERATION = NOT STARTED
FORMAL_D0_QUERY = NOT STARTED
DEV_SCIENTIFIC_RUN = NOT STARTED
VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO
```

## Frozen-scientific-artifact review

| Artifact | SHA-256 | Verdict |
| --- | --- | --- |
| Week3 final closure | `24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C` | unchanged |
| Week4 preregistration | `6942358DFF60EBC042E06F9441436D2BCCAE43EA8A66C6BD6B891FAE345758C4` | unchanged |
| Week4 canonical config | `1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D` | unchanged |
| Week4 population manifest | `DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6` | unchanged |

The semantic repair was deliberately limited to the external authorization
contract. It replaces the misleading generic assertion that prior scientific
results were unobserved with the true pair:

```text
WEEK1_3_RESULTS_ALREADY_OBSERVED = TRUE
WEEK4_RESULTS_OBSERVED_BEFORE_AUTHORIZATION = FALSE
```

No preregistration, canonical config, population row, attack factor, bound,
search rule, seed, query budget, bootstrap rule, split, detector, or generator
identity was changed.

## Independent readiness checks

```text
WEEK3_IMMUTABLE = YES
PREREGISTRATION_HASH_MATCH = YES
CANONICAL_CONFIG_HASH_MATCH = YES
POPULATION_HASH_MATCH = YES

POPULATION_48_24_12_12 = PASS
SPEAKER_DISJOINT = PASS
PRIOR_WEEK_EXCLUSION = PASS
POPULATION_SELECTED_WITHOUT_D0 = YES

STATIC_COMPARATOR_FROZEN = PASS
SEARCH_ACTUALLY_ADAPTIVE = PASS
SEARCH_DETERMINISTIC = PASS
HIDDEN_RESEARCHER_DISCRETION = NONE

QUERY_ACCOUNTING = PASS
APPEND_ONLY_LEDGER = PASS
HELDOUT_GOVERNANCE = PASS

AUTHORIZATION_SCHEMA = PASS
PREAUTH_OBSERVATION_SEMANTICS = PASS
CONFIG_AUTHORIZATION_SEMANTICS = PASS
FORMAL_RUNNER_GATE_ORDER = PASS
FORMAL_NAMESPACE_CONTRACT = PASS

F5_SOURCE_IDENTITY = PASS
FORMAL_ENVIRONMENT = PASS
OUTCOME_LEAKAGE = NONE
BLOCKERS = NONE
```

Population was independently parsed rather than accepted from a prior report:
48 selected cases have 48 unique speakers; split counts are DEV 24,
VALIDATION 12, HELD_OUT 12; all source/reference pairs are same-speaker,
different-utterance, and different-text; no selected row has prior-week
overlap. The manifest records selection seed `20260912`, `d0_invoked=false`,
and `d0_outcome_inspected=false`.

The static comparator remains middle-active-interval insertion, 400-sample
crossfade, 0.0 dB gain, mono 16 kHz, and sample-first deterministic ground
truth. A0 permits only crossfade 160–400 samples in steps of 80 and gain
-3.0–3.0 dB in steps of 0.5; its fixed 8×5 search has a maximum of 40 D0
queries and generation 1–4 proposals derive from prior valid D0 history.
Tests independently cover 1–40/41 rejection, failed-invoked accounting,
pre-invocation invalid candidates, restart persistence, hash-chain tamper
detection, retention of invalid/non-winner candidates, and held-out tuning
rejection.

## Active authorization

Canonical artifact: `results/week4_adaptive_redteam/authorization.json`

```text
AUTHORIZATION_SHA256 = AFA6BA2CC68556B832FA7C11CBAF0BF1AF1FE56B4DDB844FBA8F82FC5F7F3B48
RUN_ID = week4_adaptive_redteam_v0
INVOCATION_ID = week4_adaptive_redteam_v0_20260912_authorized
OUTPUT_NAMESPACE = results/week4_adaptive_redteam_runs/week4_adaptive_redteam_v0_20260912_authorized
```

The artifact binds the current preregistration, config, population, controller
and search implementation (`965BE008DC1816A1393081A5B0138AC3A0015B0D513CEAA28D47A9B4AC256818`),
formal runner (`516532AF5376D7B5825AADD8889EDDD4A2502108DFE8C2617E80000D57BA73F6`),
F5 qualification (`9612DCCD346FB86C3C4E026E4C9769CC58ECE5069848F95BDFCEF8067AD9DB6C`),
D0/S2/F5 identity, query budget 40, H4 identity, paired-case bootstrap, and
the finalized outcome-blind population. The authorization schema SHA-256 is
`BC31C0DF2E4497AE097735EFCA890C115B270BE1190BEC9C9736EB43233B046B`.

Formal preflight validates, in order: frozen config/schema; preregistration,
config, and population frozen hashes; population structure; implementation
and active-authorization hashes; run and invocation identities; F5
qualification/assets; and a new, absent output namespace. Its active-artifact
result was:

```text
AUTHORIZATION_VALID = YES
F5_INVOKED = NO
D0_INVOKED = NO
SCIENTIFIC_OUTPUT_CREATED = NO
ACCOUNTING_INITIALIZATION_SAFE = YES
```

The authorized output namespace remains absent after preflight. No Week4 F5
waveform, D0 score, validation result, held-out result, H4 result, ledger, or
cache outcome exists. The only Week4 result-directory files are the inactive
template and this active authorization artifact.

## Test and environment evidence

| Check | Result |
| --- | --- |
| Week4 contracts, authorization, population, and formal-runner tests | `30 passed` |
| Week3 direct dependency tests | `35 passed` |
| Full base-Python suite | `300 passed, 3 errors` |
| Formal offline F5 environment Day6B suite | `25 passed, 1 Windows symlink warning` |

The three base-Python errors are the pre-existing Day6B setup errors caused by
missing `torch`; the formal F5 environment has the necessary stack and passed
the complete Day6B suite. They are therefore recorded as
`NON_BLOCKING_PREEXISTING_ENVIRONMENT_ERRORS`, with no Week4 formal-path
dependency overlap.
