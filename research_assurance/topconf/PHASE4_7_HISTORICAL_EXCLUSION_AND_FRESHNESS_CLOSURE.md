# Phase 4.7 historical exclusion and freshness closure

```text
PHASE = PHASE4_7_HISTORICAL_EXCLUSION_RECONSTRUCTION_AND_FRESHNESS_CLOSURE
DATE = 2026-09-15
STATUS = CLOSED_WITH_FAIL
FINAL_AUTHORIZATION_DECISION = NO_GO
LEVEL2_INFERENCE_STARTED = NO
V2_POPULATION_MODIFIED = NO
```

## Outcome

The historical reconstruction is complete for the searched repositories,
worktrees, retained manifests, raw-output manifests, Git history, and external
dataset evidence. It found a narrow but decisive blocker against the frozen
Phase 4.6 V2 candidate: five verified AISHELL-3 source/audio lineages overlap
historical Week1/Week4 use, producing 20 affected V2 cases. Two of the 23
historically reused speaker keys are directly implicated: `AISHELL3:SSB0005`
and `AISHELL3:SSB1203`.

The remaining history is explicitly represented as `PARTIAL` or `UNKNOWN` where
complete identity was not recoverable. This prevents an apparent zero from being
mistaken for a proven exclusion.

## Validator and tests

The freshness validator now supports the V3 four-universe contract:

```text
CASE_EXCLUSION
SOURCE_EXCLUSION
SPEAKER_USAGE
LINEAGE_EXCLUSION
```

It recomputes case-ID, case-lineage, source, lineage, speaker, and prohibited
speaker overlap, validates corpus-isolation evidence, and returns
`INSUFFICIENT_EVIDENCE` for missing/unknown identity. Synthetic tests cover
incomplete/no-overlap, complete/no-overlap, verified lineage overlap with a
different case ID, AISHELL-1 post-freeze acquisition, missing evidence source,
and unknown speaker identity.

```text
python -m pytest tests/topconf -q       64 passed
V2 population validator                  PASS
V3 freshness validator                    FAIL (expected; exit 1)
synthetic governance dry run             PASS
```

## Frozen-state check

```text
LEVEL2_RQ1_POPULATION_MANIFEST_V2.json
SHA256 = ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
UNCHANGED_BEFORE_AFTER_RECONSTRUCTION = YES
```

No scientific metric, threshold, performance result, LD@DR95 value, or RQ
outcome was generated or consumed. The authorization artifact remains `NO_GO`.

## Artifact set

See `PHASE4_7_HISTORICAL_FRESHNESS_PROOF_V1.md` for the evidence narrative and
the JSON artifacts in this directory for the machine-checkable records. The
Phase 4.7 task is closed; any later authorization requires a new human review
after a fresh, passing population and freshness proof.
