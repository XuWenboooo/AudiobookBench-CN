# Phase4.9 AISHELL-3 Pool-A retirement record v1

Status: **RETIRED_FROM_CONFIRMATORY_POOL_A**

Protocol: P4-RQ1-DESIGN-20260914-01  
Parent population: LEVEL2_RQ1_POPULATION_MANIFEST_V2.json  
Parent population SHA-256: ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A00AA84F52B3955D0

## Decision

The entire AISHELL-3 Pool A is retired. This is not a seven-source patch:

- 200 primary AISHELL-3 sources are removed from the confirmatory population.
- 20 AISHELL-3 reserve records are removed from the confirmatory reserve.
- 800 AISHELL-3 case records are removed from the V2 case namespace.
- The AISHELL-3 corpus is not used as a fallback, replacement, reserve, or
  cross-pool substitute in V3.

AISHELL-1 Pool B is retained at its frozen 200-source/60-speaker allocation.
The new Pool A is a separate corpus-level identity and is selected before V3
materialization.

## Trigger and preserved evidence

Phase4.8 verified freshness contamination in the V2 AISHELL-3 population:

- five direct source-hash overlaps were verified;
- two prohibited AISHELL-3 speakers were verified;
- speaker-based exclusion expanded the affected source set to seven;
- 28 V2 cases were affected;
- the frozen AISHELL-3 reserve contained zero clean same-pool replacement
  records because all 20 reserve rows belonged to prohibited speaker
  AISHELL3_SSB0005.

The following artifacts remain unchanged and are evidence for this retirement:

- LEVEL2_RQ1_POPULATION_MANIFEST_V2.json
- LEVEL2_FRESHNESS_MANIFEST_V3.json
- LEVEL2_V2_VERIFIED_CONTAMINATION_EXCLUSION_V1.json
- LEVEL2_V2_TO_V3_REPLACEMENT_LEDGER_V1.json
- PHASE4_8_LEVEL2_POPULATION_REMATERIALIZATION_CLOSURE.md

## Firewall

No model inference, detector output, scientific metric, LD@DR95 value, RQ1
outcome, RQ2 attack, RQ3 mitigation, or result-based choice was used. The
retirement is caused solely by the verified provenance/freshness failure and
the absence of a clean same-pool reserve.

