# Baseline Provenance Register v2

Status: **AUTHORIZED SCOPE RECORDED / NO EXTERNAL MODEL OUTPUT OBSERVED**

All rows were retained by predefined paradigm diversity and output
compatibility. No baseline was excluded because of a score. Checkpoint hashes
are required before any full reproduction.

| Baseline | Official source and frozen commit | License / rights | Checkpoint evidence | Phase 3 status |
|---|---|---|---|---|
| Internal B1b/B4 | repository-local implementation; evaluator authorization anchored at the Phase 3 authorization commit | project-local; no redistribution | existing internal artifacts only; no new checkpoint selected | `FUNCTIONAL_EXISTING_INTERNAL`, reproduction run not invoked |
| CFPRF | `https://github.com/ItzJuny/CFPRF` at `358a901ead8a7d84dac979c3d626e34ef82c2854` | MIT; LICENSE SHA256 `BB5BF39CA260648C9810E7449C820F6015605ED53AFB6E1B4A8F7CAAA06B100D` | official README lists `1FDN_{HAD,LAVDF,PS}.pth` and `2PRN_{HAD,LAVDF,PS}.pth` via linked Google Drive; no local hash | `BLOCKED_CHECKPOINT_DOWNLOAD_THROUGHPUT` |
| SAL | `https://github.com/SentryMao/SAL` at `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | MIT; repository metadata confirms MIT | README documents evaluation and `ckpt_path`; no verified local checkpoint/hash | `BLOCKED_CHECKPOINT_UNAVAILABLE` |
| BAM | `https://github.com/media-sec-lab/BAM` at `55f3fb9e3b4dd6281597b86d7712fb23454179f6` | repository license unresolved; redistribution prohibited pending rights clearance | README names `./checkpoint/model.ckpt` and a linked Google Drive source | `BLOCKED_RIGHTS_CLEARANCE` |
| TRACE | CVPRW 2026 paper source reviewed; no matching official audio-localization repository/checkpoint verified | unresolved | reimplementation and extractor/checkpoint provenance would be required | `STRETCH_REIMPLEMENTATION_REQUIRED` |

Failure accounting is infrastructure-based only. No result-based retry,
threshold selection, pooling selection, or model ranking was performed.
