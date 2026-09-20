# PartialSpoof upstream identity investigation v1

Audit date: `2026-09-20`  
Official repository: `https://github.com/nii-yamagishilab/PartialSpoof`  
Observed default branch: `main`  
Official Zenodo distribution: record `5766198`

## Missing official eval identities

```text
BAD_ID_1 = CON_E_0034982
BAD_ID_2 = CON_E_0058039
```

The local official v1.2 eval archive has no WAV for either ID, and the
materialized official protocol/segment-label metadata has no matching GT
entry. Exact-ID lookup in the official repository README and repository tree
returned no correction, alias, replacement, or erratum for either ID. The
GitHub issue-search endpoint was not usable anonymously (`422` resource
validation), so it is not treated as evidence of absence.

```text
OFFICIAL_AUTHOR_MAPPING_FOUND = NO
OFFICIAL_CORRECTED_MANIFEST_FOUND = NO
NEAREST_NAME_MATCHING = FORBIDDEN
DROP_IDS = FORBIDDEN
PARTIALSPOOF_READY = NO
```

The two IDs therefore remain an unresolved upstream dataset inconsistency;
the acceptance decision stays fail-closed.
