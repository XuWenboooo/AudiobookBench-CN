# W7 model and rights adjudication v1

    SAL_CHECKPOINT_ADJUDICATION = HISTORICALLY_VALID_BUT_ASSET_NOT_MATERIALIZED_AFTER_MIGRATION
    SAL_CHECKPOINT_IDENTITY = FAIL
    SAL_EXPECTED_SHA256 = FDE76030DF782E140658AA5A2726D18EBFFA9FA359E11CE2B237F6EC46114D2F
    SAL_ACTUAL_SHA256 = NOT_AVAILABLE

    BAM_CHECKPOINT_ADJUDICATION = HISTORICALLY_VALID_BUT_PATH_BROKEN
    BAM_CHECKPOINT_IDENTITY = PASS
    BAM_EXPECTED_SHA256 = 5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1
    BAM_ACTUAL_SHA256 = 5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1

    BAM_RIGHTS_ADJUDICATION = HISTORICAL_EVIDENCE_REFERENCED_DIFFERENT_ASSET
    BAM_RIGHTS = FAIL

SAL's historical strict-load record fixes an official 4,037,013,806-byte
checkpoint and SHA-256. That asset is absent from the selected migration,
migration backup, and historical recovery worktree. The frozen source could
not be contacted because huggingface.co was DNS-unreachable during this audit,
so no new bytes were accepted.

BAM's 1,353,631,994-byte historical ZIP was found in the historical recovery
worktree and copy-recovered to the controlled G-drive cache. Its SHA-256 is an
exact match. This resolves a path/migration defect only.

The official Zenodo API record 12747417 confirms CC BY 4.0 for the 527,740
byte software ZIP media-sec-lab/BAM-version1.0.0.zip. The W7 checkpoint is a
separate README-linked Google Drive artifact and is not in that release.
Consequently the code-license evidence cannot establish a license for the
checkpoint. The BAM rights gate remains fail-closed.
