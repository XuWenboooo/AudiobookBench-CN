# External Dataset Adapters v1

Status: **METADATA-ONLY / NO DATA ACCESS AUTHORIZED**

Adapters expose identity, provenance, split and annotation metadata. They may
not infer ground truth from filenames, audio, papers, OCR, or model outputs.
Unavailable official labels produce `BLOCKED_GT_UNAVAILABLE`.

| Dataset | Official source | GT / resolution | Speaker / mechanism metadata | License | Status |
|---|---|---|---|---|---|
| PartialSpoof v1.2 | [Zenodo DOI 10.5281/zenodo.5766198](https://zenodo.org/records/5766198); [official repo](https://github.com/nii-yamagishilab/PartialSpoof) | `database_segment_labels_v1.2.tar.gz`, timestamp labels; multi-resolution; MD5 recorded in provenance register | speaker/split fields via official protocols; exact parser validation pending | CC BY 4.0; local research usable, redistribution separately reviewed | VERSION FROZEN / GT SOURCE VERIFIED |
| PartialEdit v1.1 | [Zenodo DOI 10.5281/zenodo.18829689](https://zenodo.org/records/18829689); [project page](https://yzyouzhang.com/PartialEdit/index.html) | `PartialEdit_E1E2.csv`; edited-region seconds; speaker split archive; MD5 recorded in provenance register | E1/E2 and codec controls; E3/E4 excluded | CC BY 4.0; E3/E4 not publicly released | VERSION FROZEN / GT SOURCE VERIFIED |
| HAD | [Zenodo record](https://zenodo.org/records/10377492); [Interspeech paper](https://www.isca-archive.org/interspeech_2021/yi21_interspeech.pdf) | official region labels; exact parser/resolution TBD | Chinese; exact fields TBD | TBD | STRETCH / SKELETON |

No adapter may be promoted to Phase 3 data access until source, license, split
policy, audio location, GT format, temporal resolution, and hashes are locally
verified. The version decisions above do not authorize download or inference.
