# Week4 population freeze

Date: 2026-09-11  
Status: `WEEK4_POPULATION_FINALIZED = YES`

The canonical population is the read-only AISHELL-3 train-derived manifest
at `data/manifests/week4_population_manifest.json`.  It was built with fixed
selection seed `20260912` by
`experiments/week4_adaptive_red_team/build_population.py`, using
`src/audiobookbench/security/week4_population.py` as the deterministic
builder.  The AISHELL-3 directory was read only; D0 was not imported,
invoked, or inspected.

## Freeze evidence

| Item | Frozen value |
| --- | --- |
| candidate pair pool | 149 |
| Week1–3 prior speaker overlap | 12 |
| eligible after prior exclusion | 137 |
| final selected cases | 48 |
| split counts | DEV 24 / VALIDATION 12 / HELD_OUT 12 |
| selection seed | 20260912 |
| selected without D0 | YES |
| D0 invoked / outcome inspected | NO / NO |
| builder SHA-256 | `6467ED02D0D077361964E85FCA91BC24AE0976E486D55962CB0684E62E399F89` |
| population build entrypoint SHA-256 | `558805FDF5447918E7D433AF7F26F4F8124FE14B7864A3FFD04BBBD3085EED4D` |
| frozen manifest SHA-256 | `DD71B3B70E558B73FA5E5545A52C2A819999171930ADA81D207EC5BFB60973F6` |

The selected case rows retain source/reference paths, audio hashes, exact
text and text hashes, same-speaker/different-utterance identity, split,
selection rank, and the prior-exclusion decision.  Selected speaker IDs are
unique and disjoint from the recorded Week1–3 scientific speaker set.

This is population and engineering evidence only.  It does not authorize
Week4 generation, adaptive search, D0 evaluation, held-out execution, or H4.
