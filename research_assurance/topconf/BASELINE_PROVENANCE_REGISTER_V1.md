# Baseline Provenance Register v1

Status: **SOURCE VERIFIED / NO CHECKPOINT DOWNLOADED OR RUN**

| Baseline | Repository HEAD | License | Checkpoint/provenance | Reproduction disposition |
|---|---|---|---|---|
| BAM | `media-sec-lab/BAM@55f3fb9e3b4dd6281597b86d7712fb23454179f6` | `UNRESOLVED`; GitHub API reports no repository license | README names `./checkpoint/model.ckpt`, linked Google Drive; exact hash unavailable without download | Core candidate; research use/redistribution require clarification |
| CFPRF | `ItzJuny/CFPRF@358a901ead8a7d84dac979c3d626e34ef82c2854` | MIT; LICENSE SHA256 `BB5BF39CA260648C9810E7449C820F6015605ED53AFB6E1B4A8F7CAAA06B100D` | README names `1FDN_{HAD,LAVDF,PS}.pth` and `2PRN_{HAD,LAVDF,PS}.pth`; linked Google Drive | Verified core candidate; download/run deferred |
| SAL | `SentryMao/SAL@b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485` | MIT; repository metadata confirms SPDX MIT | README documents evaluation entry point and checkpoint path; release hash/source TBD | Verified core candidate; checkpoint availability needs local inspection |
| TRACE | paper/source reviewed; matching audio-localization repo not verified | UNRESOLVED | exact extractor/checkpoint/output contract not verified | Stretch; reimplementation may be required |

Core selection is based on paradigm diversity, output compatibility, and
reproducibility—not reported scores. No external result is copied into the
primary analysis.
