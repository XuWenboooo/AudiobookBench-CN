# Phase 4.6 Level-2 Source-Pool Recovery Closure v1

Status: **BLOCKED — POPULATION RECOVERED; HISTORICAL FRESHNESS EVIDENCE INSUFFICIENT**  
Review date: **2026-09-15**  
Branch: `topconf-dl-robustness`

## Frozen-design interpretation

`SOURCE_CORPUS_IDENTITY_FROZEN = NO`.

Phase4 froze two independent, rights-cleared Mandarin long-form source pools,
the 400-source/120-speaker/two-pool cardinality, paired mechanisms,
transformations, statistics, metrics, thresholds, Whether-A/Whether-B policy,
freshness requirements, and the gap criterion. It deliberately left exact
corpus identities and hashes as pre-run freshness-manifest fields. This is
shown in §6 of `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md` and §9 of
`PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`.

Therefore, evaluating AISHELL-1 as the second corpus-level source pool is an
implementation of the frozen design. No prospective scientific amendment is
required or created. A V2 preregistration would be required only if the
frozen scientific architecture, sample size, mechanisms, metrics, statistics,
or policy were changed.

```text
AMENDMENT_REQUIRED = NO
AMENDMENT_STATUS = NOT_REQUIRED_IMPLEMENTATION_ONLY
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
MODEL_INFERENCE_RUNS = 0
SCIENTIFIC_RESULTS_USED_FOR_SOURCE_SELECTION = NO
RESULT_BASED_DESIGN_CHANGES = 0
```

## Recovery status

AISHELL-3 remains a historical/local candidate only: the prior header audit
found 532 eligible files but only 112 eligible speakers, and its train/test
speaker partitions share 170 speakers. It cannot be split into two independent
pools.

AISHELL-1 passed the pre-download feasibility gate. The official OpenSLR SLR33
record identifies it as Mandarin data under Apache License 2.0 with 400
participants and a 16 kHz release. The local 1.2M supplementary archive
contains 400 valid unique speaker IDs. The 15.58G official audio archive has
now been acquired for a read-only WAV-header audit; no model or scientific
output is involved.

The complete official audio archive was acquired, tar-integrity checked, and
audited with `tools/topconf/audit_aishell1_feasibility.py`. The audit measured:

```text
AISHELL1_WAV_FILES = 141925
AISHELL1_VALID_WAV_FILES = 141925
AISHELL1_ELIGIBLE_8_30_FILES = 2761
AISHELL1_ELIGIBLE_8_30_SPEAKERS = 300
AISHELL1_ELIGIBLE_TRANSCRIPT_COMPLETE_FILES = 2750
AISHELL1_ELIGIBLE_FILES_WITHOUT_TRANSCRIPT = 11
AISHELL1_SAMPLE_RATE_CHANNEL_FORMAT = 16000_HZ_MONO_PCM16
AISHELL1_ARCHIVE_SHA256 = A4A0313CDE0A933E0E01A451F77DE0A23D6C942F4694AF5BB7F40B9DC38143FE
```

The 11 eligible WAVs without transcript rows are explicitly excluded from
selection; the remaining candidates have source-audio and text hashes. The
full audio/transcript audit is therefore a capacity and lineage-input PASS,
not a freshness PASS.

The deterministic candidate materialization is recorded in
`LEVEL2_RQ1_POPULATION_MANIFEST_V2.json`: 400 primary sources, 120 speakers,
two 200-source pools, 40 reserve sources, and 1,600 cases. The population
validator returns `PASS`. It is a metadata-only candidate: no manipulated
audio, model inference, prediction, label, metric, or scientific outcome is
present.

## Required PASS state

The closure may become `PASS` only when two corpus-level pools are proven,
exactly 400 primary sources and at least 120 unique speakers are materialized,
the 40-source reserve and deterministic allocation are frozen, all required
historical exclusions are complete enough for the frozen policy, and population,
freshness, lineage, GT-isolation, and namespace validators pass. No score or
model output may enter any selection decision.

The paired V2 freshness manifest is
`LEVEL2_FRESHNESS_MANIFEST_V2.json`. Its fail-closed validator returns
`INSUFFICIENT_EVIDENCE` at `WEEK1_PILOT`, because the historical exclusion
universe remains partial. Physical cross-corpus speaker identity also remains
`NOT_DIRECTLY_VERIFIABLE_FROM_PUBLIC_METADATA`; no unsupported disjointness
claim is made.

The final Phase4.6 state is:

```text
SOURCE_POOL_RECOVERY = PASS_CAPACITY_AND_METADATA
SOURCE_POOL_INDEPENDENCE = PASS_CORPUS_LEVEL_PENDING_PHYSICAL_IDENTITY_REVIEW
FRESHNESS = BLOCKED_INSUFFICIENT_HISTORICAL_EXCLUSION
V2_POPULATION_VALIDATOR = PASS
V2_FRESHNESS_VALIDATOR = INSUFFICIENT_EVIDENCE
FINAL_AUTHORIZATION_DECISION = NO_GO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
```

The V1 blocked manifest is preserved unchanged. V2 is a candidate recovery
artifact only; it does not authorize materialized inference/evaluation views,
namespace ownership, GT reveal, or any Level-2 scientific run.
