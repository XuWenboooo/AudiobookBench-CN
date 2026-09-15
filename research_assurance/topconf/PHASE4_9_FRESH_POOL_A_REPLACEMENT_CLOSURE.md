# Phase 4.9 Fresh Pool-A Replacement Closure

Date: 2026-09-15  
Protocol: `P4-RQ1-DESIGN-20260914-01`  
Branch: `topconf-dl-robustness`

## Decision

**CLOSED / BLOCKED / NO_GO**

Phase 4.9 completed exactly one fresh Pool-A candidate path, one V3
population materialization, and one V4 freshness audit. The final
authorization is `NO_GO` because the four historical exclusion universes are
still `PARTIAL`. Zero observed overlap in incomplete universes is not sufficient
evidence for a freshness `PASS`.

No model inference, CFPRF/MultiReso/AASIST execution, scientific metric,
`LD@DR95`, RQ1 result, RQ2, or RQ3 was run or accessed.

## Provenance and population action

- The entire AISHELL-3 Pool A from V2 is retired; this is not a seven-source
  patch. Its 200 primary sources, 60 speakers, 20 reserves, and 800 planned
  cases are not carried into V3.
- AISHELL-1 Pool B is retained exactly as the V2 Pool-B population: 200 primary
  sources, 60 speakers, and 20 reserves.
- AliMeeting SLR119 is the selected fresh Mandarin Pool A. It was selected
  before V3 materialization, after MAGICDATA SLR68 was rejected for its
  restrictive license/use terms and WenetSpeech was deferred because
  acquisition and speaker-level capacity were not established.
- The selection commit is
  `3fa5ce5984c01f1feb75f931c0c00c57c0f00872`; it precedes the V3 artifact
  commit. The work started from true HEAD `110e2b91c04625898b955c0d0dfcfccfe04515cb`;
  no reset, rebase, or force push was used. V1/V2 and Phase 4.5–4.8 evidence
  artifacts were preserved.

The V3 structure is:

```text
400 sources / 120 speakers / 400 pairs / 1,600 cases
Pool A: 200 sources / 60 speakers
Pool B: 200 sources / 60 speakers
Reserves: 20 per pool
Mechanisms: 400 per mechanism x 4
Transforms: CLEAN only, 1,600 cases
Pool-A primary segment hashes: 200 unique
Pool-A primary parent lineages: 200 unique
Pool-A vs Pool-B source hash overlap: 0
Pool-A primary vs reserve hash overlap: 0
```

The V3 population validator, inference-manifest validator, and evaluation-
manifest validator all pass structurally. The inference and evaluation views
contain no scientific outcomes and remain separated by the outcome firewall.

## V4 freshness result

The four Phase 4.7 historical universes remain incomplete:

```text
CASE_EXCLUSION      PARTIAL
SOURCE_EXCLUSION    PARTIAL
SPEAKER_USAGE       PARTIAL
LINEAGE_EXCLUSION   PARTIAL
```

The one permitted V4 comparison observed zero overlaps for case IDs, case
lineages, source audio identities, parent lineages, speakers, and prohibited
speakers. The V4 validator nevertheless returns
`INSUFFICIENT_EVIDENCE`, as required by the fail-closed rule. The required
terminal state is:

```text
STOP_AFTER_ONE_V3_AND_ONE_V4_AUDIT
CLOSURE = BLOCKED_INSUFFICIENT_HISTORICAL_EXCLUSION_EVIDENCE
AUTHORIZATION = NO_GO
MODEL_INFERENCE_RUNS = 0
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RQ2_STARTED = NO
RQ3_STARTED = NO
```

No repeated candidate search or second V4 attempt is authorized by this
closure. Any future continuation requires a new human decision and a new
complete historical exclusion proof.

## Evidence index and hashes

| Artifact | SHA256 / identity |
|---|---|
| `LEVEL2_AISHELL3_POOL_RETIREMENT_RECORD_V1.md` | `FC80F7FB8B23949883CD190FAC99B2EACA85AC1CE475F2C39F801BC179A7ED03` |
| `LEVEL2_FRESH_POOL_A_CANDIDATE_MATRIX_V1.md` | `598C992D779CB98683386BDDD4146DCFCC29E1D1538EF53E1B20C93B99DAD82D` |
| `LEVEL2_NEW_POOL_A_PROJECT_ENTRY_PROOF_V1.json` | `F28D3604D333EB03F868DF8C5DDFE474ABDD5F37CFFD03BAA23623F5F41EA120` |
| `LEVEL2_NEW_POOL_A_SELECTION_RECORD_V1.md` | `3F3BE07DD837DCC718771C672015A676FD2ACBBC9539717833D91620DBD5DACB` |
| `LEVEL2_SOURCE_POOL_INDEPENDENCE_PROOF_V2.json` | `14064A6F22980ACAF3DFD25C1D58814CD5D35CAA8BD68E646673E8C7F6E73592` |
| `LEVEL2_RQ1_POPULATION_MANIFEST_V3.json` internal manifest identity | `89834D9F85603727EE5E6F482C9BAC9832283EAF1902976FD31975AF61FCE78B` |
| `LEVEL2_RQ1_INFERENCE_MANIFEST_V3.json` | `CE99170FA2CD8650554640D0C18D492C6C8E9F01BF5DAEDE215359E9A7F901C6` |
| `LEVEL2_RQ1_EVALUATION_MANIFEST_V3.json` | `046932831684183DFF629C6C88EE2488A1F5FFCE819799C86E21BED6DDFE7C92` |
| `LEVEL2_FRESHNESS_MANIFEST_V4.json` internal manifest identity | `973002F7112B1A51F803C24817321BC2CF23BD814B1DBD673F6BFA85DA6FC4C6` |
| preserved V2 population identity | `ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0` |
| preserved Phase 4.7 V3 freshness identity | `640D128B0AC0557B0AAB5AA0F7DD209CE47597C096BE3C4EBE3C06B92FA30949` |

Official AliMeeting resource identity and license evidence are recorded in the
project-entry and independence proofs: [OpenSLR SLR119](https://www.openslr.org/119/).

## Commits

```text
SELECTION_COMMIT = 3fa5ce5984c01f1feb75f931c0c00c57c0f00872
V3_AND_V4_ARTIFACT_COMMIT = a242295444e1f2cdf78c1d8d3a2a662a111d6fd0
```
