# Phase 4.6 Level-2 Source-Pool Feasibility Matrix v1

Status: **AISHELL-1 CAPACITY PASS; HISTORICAL FRESHNESS BLOCKED**  
Review date: **2026-09-15**  
Protocol: `P4-RQ1-DESIGN-20260914-01`

## Frozen interpretation

`SOURCE_CORPUS_IDENTITY_FROZEN = NO`. Phase4 freezes two independent,
rights-cleared Mandarin long-form source pools and their population constraints;
it does not name AISHELL-3 or any other corpus. The preregistration requires the
exact pool identities and hashes to be populated in the pre-run freshness
manifest. Therefore, a separately documented AISHELL-1 pool is an
implementation of the frozen design, not a scientific design amendment.

Evidence:

- `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md`, §6: exact pool identity is
  deferred to the pre-run freshness manifest and the Phase4 design manifest is
  intentionally not materialized.
- `PHASE4_CONFIRMATORY_DESIGN_DECISION_DOSSIER_V1.md`, §9: exact pool identities
  and hashes are pre-run fields; only the 400/120/two-pool architecture is
  frozen.
- `PHASE4_HUMAN_RECONCILIATION_AND_DESIGN_FREEZE_CLOSURE.md`: the Level-2 pool
  is described by distribution, rights, metadata, and freshness constraints,
  without a named corpus.

## Matrix

| Candidate | Mandarin fit | Speaker count | 8–30 s eligible files/speakers | License / authority | Speaker metadata | Lineage / freshness | Corpus independence | Local availability | Download reproducibility | Final status |
|---|---|---:|---:|---|---|---|---|---|---|---|
| AISHELL-3 | PASS | 218 raw / 112 eligible | 532 / 112 from RIFF headers | Apache-2.0 metadata; OpenSLR SLR93/local archive | PASS for local speaker IDs | Historical Week1–5 use; complete exclusion not reconstructed | FAIL as two pools; train/test share 170 speakers | PASS | Local archive hash recorded | **FAIL for frozen two-pool population** |
| AISHELL-1 | PASS | 400 in official speaker.info | 2,750 transcript-complete eligible files / 300 eligible speakers | Apache-2.0; Beijing Shell Shell Technology via OpenSLR SLR33 | PASS: 400 rows / 400 unique IDs | No AISHELL-1 audio use found in repository scan; historical exclusion remains partial | Corpus-level independence candidate; physical cross-corpus identity not directly verifiable | Full official archive acquired and integrity checked | Official OpenSLR URL, 15,582,913,665-byte archive, ETag, resource hash, and observed archive hash recorded | **PASS_CAPACITY_PENDING_FRESHNESS** |
| WenetSpeech | Not audited | Unknown | Unknown | Not audited | Unknown | Unknown | Unknown | Not located | Not audited | **DEFERRED** |
| THCHS-30 | Not audited | Unknown | Unknown | Not audited | Unknown | Unknown | Unknown | Not located | Not audited | **DEFERRED** |

## AISHELL-1 evidence boundary

The official OpenSLR SLR33 page identifies AISHELL-1 as Mandarin data under
Apache License 2.0, with 400 participants and a 16 kHz release. The downloaded
`resource_aishell.tgz` is 1,246,920 bytes with SHA256
`1A6749854456E9402BC7295767937367AFED1327799A5E1DF0ED64BAA5F77409`; its
`speaker.info` contains exactly 400 valid, unique speaker IDs and its
`lexicon.txt` is present. The complete official audio archive is 15,582,913,665
bytes and has observed SHA256
`A4A0313CDE0A933E0E01A451F77DE0A23D6C942F4694AF5BB7F40B9DC38143FE`.

The complete read-only audit found 141,925 valid WAV headers, all 16 kHz,
mono, 16-bit; 2,761 files / 300 speakers satisfy the 8–30 second frozen
filter. Eleven eligible WAVs have no transcript row and are excluded, leaving
2,750 transcript-complete candidates across 300 speakers. Each retained
candidate has an audio-byte SHA256 and transcript SHA256. No model, detector,
score, quality ranking, or scientific result is used by that audit.

## Decision rule

AISHELL-1 passes the capacity and format gate: it yields at least 120 eligible
speakers and enough model-free, transcript-complete sources for the frozen
400-source allocation. It does not by itself pass freshness: the source-pool
proof still records physical speaker identity as not directly verifiable, and
the complete historical exclusion universe is not reconstructed. No speaker,
case, pool, or duration requirement may be relaxed.
