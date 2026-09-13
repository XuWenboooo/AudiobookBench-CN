# Baseline Provenance Register v2

Status: **AUTHORIZED SCOPE RECORDED / NO EXTERNAL MODEL OUTPUT OBSERVED**

All rows were retained by predefined paradigm diversity and output
compatibility. No baseline was excluded because of a score. Checkpoint hashes
are required before any full reproduction.

| Baseline | Official source and frozen commit | License / rights | Checkpoint evidence | Phase 3 status |
|---|---|---|---|---|
| Internal B1b/B4 | repository-local implementation; evaluator authorization anchored at the Phase 3 authorization commit | project-local; no redistribution | existing internal artifacts only; no new checkpoint selected | `FUNCTIONAL_EXISTING_INTERNAL`, reproduction run not invoked |
| CFPRF | `https://github.com/ItzJuny/CFPRF` at `358a901ead8a7d84dac979c3d626e34ef82c2854` | MIT; LICENSE SHA256 `BB5BF39CA260648C9810E7449C820F6015605ED53AFB6E1B4A8F7CAAA06B100D` | official README-linked Google Drive: `1FDN_PS.pth` SHA256 `5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267`; `2PRN_PS.pth` SHA256 `88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36`; official fairseq XLSR SHA256 `B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9`; strict FDN and PRN state loads; one-sample FDN CPU forward pass | `INFRASTRUCTURE_SMOKE_PASS_FULL_REPRODUCTION_BLOCKED_INCOMPLETE_AUDIO_AND_NO_CUDA` |
| SAL | `https://github.com/SentryMao/SAL` at `b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | MIT; repository metadata confirms MIT | README documents evaluation and `ckpt_path`; no verified local checkpoint/hash | `BLOCKED_CHECKPOINT_UNAVAILABLE` |
| BAM | `https://github.com/media-sec-lab/BAM` at `55f3fb9e3b4dd6281597b86d7712fb23454179f6` | repository license unresolved; redistribution prohibited pending rights clearance | README names `./checkpoint/model.ckpt` and a linked Google Drive source | `BLOCKED_RIGHTS_CLEARANCE` |
| TRACE | CVPRW 2026 paper source reviewed; no matching official audio-localization repository/checkpoint verified | unresolved | reimplementation and extractor/checkpoint provenance would be required | `STRETCH_REIMPLEMENTATION_REQUIRED` |

Failure accounting is infrastructure-based only. No result-based retry,
threshold selection, pooling selection, or model ranking was performed.
