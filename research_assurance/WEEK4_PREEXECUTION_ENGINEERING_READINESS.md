# Week4 pre-execution engineering readiness

Date: 2026-09-11  
Scope: `PRE_EXECUTION_ENGINEERING_ONLY`

This record covers the final engineering preparation for the frozen Week4
adaptive red-team protocol.  It does not authorize or report scientific
execution.  The frozen preregistration and canonical Week4 configuration were
not scientifically amended.

## Final status

```text
WEEK4_POPULATION_FINALIZED = YES
FORMAL_RUNNER_IMPLEMENTED = YES
FORMAL_AUTHORIZATION_SCHEMA_READY = YES
PREEXECUTION_ENGINEERING_READY = YES
ACTIVE_FORMAL_AUTHORIZATION_CREATED = NO
READY_FOR_FORMAL_WEEK4_EXECUTION = NO
```

## Canonical hashes

```text
PREREGISTRATION_SHA256 = 6942358DFF60EBC042E06F9441436D2BCCAE43EA8A66C6BD6B891FAE345758C4
CANONICAL_CONFIG_SHA256 = 1942A6CBF1571BECE97BEE53DF15C042431650F1EC882DD39A4DDC1A2AE1382D
POPULATION_MANIFEST_SHA256 = DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6
WEEK3_CLOSURE_SHA256 = 24ADA3B4D55FF077C62510C9A47E5DE7C0F9E9296196643B0B2A1C782354270C
```

## Population freeze

The canonical manifest is `data/manifests/week4_population_manifest.json`.
The deterministic AISHELL-3 train builder selected 149 candidate pairs,
excluded 12 Week1–3 overlapping speakers, retained 137 eligible speakers,
and finalized 48 unique speakers in DEV/VALIDATION/HELD_OUT = 24/12/12.
Every selected case retains source/reference paths and audio/text identity
hashes, exact text, eligibility decision, split, and prior-overlap status.
AISHELL-3 was read only.  Selection used seed `20260912`, did not import or
invoke D0, and did not inspect detector scores.  See
`research_assurance/WEEK4_POPULATION_FREEZE.md` for the detailed freeze
record.

```text
POPULATION_48_24_12_12 = PASS
SPEAKER_DISJOINT = PASS
PRIOR_WEEK_EXCLUSION = PASS
POPULATION_SELECTED_WITHOUT_D0 = YES
```

## Authorization and runner

`configs/week4_formal_authorization.schema.json` and
`results/week4_adaptive_redteam/authorization.template.json` define the
external authorization contract.  The template is explicitly inactive and no
`authorization.json` is present.  An active artifact must bind the canonical
preregistration, config, population manifest, controller/search code, formal
runner, F5 qualification, D0/S2/F5 identities, query budget 40, H4 identity,
paired-case bootstrap contract, issue timestamp, and a unique
`results/week4_adaptive_redteam_runs/<invocation_id>` namespace.  The validator
recomputes the canonical hashes and, in formal preflight, the local F5 asset
hashes; missing, malformed, stale, wrong-run, or inactive authorization stops
before runtime.

`experiments/week4_adaptive_red_team/formal_run.py` accepts only path
arguments plus `--preflight-only`.  The frozen config retains
`scientific_execution_enabled: false`; this means
`CONFIG_SELF_AUTHORIZES_EXECUTION = NO`, not that the config may be edited.
Formal permission can only come from a valid external active authorization.
Preflight never creates the output namespace and never invokes F5, D0, or an
evaluator.

The candidate ledger now records run/case/split identity, generation,
query index, parameters, validity and reason, waveform hash, detector outcome
hash, selection/parent fields, and a previous-ledger/row hash chain.  Query
41 is rejected and restart reloads the persisted count.

## Required final report

```text
CONFIG_SELF_AUTHORIZES_EXECUTION = NO
ACTIVE_AUTHORIZATION_REQUIRED = YES
QUERY_BUDGET_FAIL_CLOSED = PASS
RESTART_ACCOUNTING_PERSISTENT = PASS
APPEND_ONLY_LEDGER = PASS
FORMAL_NAMESPACE_FAIL_CLOSED = PASS
SCIENTIFIC_CLI_OVERRIDE_REJECTED = PASS
PREFLIGHT_F5_INVOKED = NO
PREFLIGHT_D0_INVOKED = NO
PREFLIGHT_SCIENTIFIC_OUTPUT_CREATED = NO
AISHELL3_MUTATION = NO
FORMAL_F5_GENERATION = NOT STARTED
FORMAL_D0_QUERY = NOT STARTED
VALIDATION_SCIENTIFIC_RUN = NOT STARTED
HELD_OUT_RUN = NOT STARTED
H4_RESULT_OBSERVED = NO
READY_FOR_INDEPENDENT_WEEK4_READINESS_REVIEW = YES
READY_FOR_FORMAL_WEEK4_EXECUTION = NO
```

## Regression evidence

- Week4 tests: `27 passed`.
- Week3 direct dependency tests: `35 passed`.
- Full repository: `297 passed, 3 errors`; the three errors are the known base
  Python Day6B setup failures caused by missing `torch` and no unrelated
  production workaround was made.
- Formal offline F5 environment Day6B: `25 passed, 1 warning` (Windows
  SpeechBrain symlink warning).

The three known base-Python errors are classified as a pre-existing local
environment issue, not a Week4 admission failure.  No formal F5 generation,
D0 query, DEV scientific run, validation run, held-out run, bootstrap, score,
or H4 result was produced.
