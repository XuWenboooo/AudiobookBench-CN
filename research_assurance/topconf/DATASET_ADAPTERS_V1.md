# External Dataset Adapters v1

Status: **METADATA-ONLY / NO DATA ACCESS AUTHORIZED**

Adapters expose identity, provenance, split and annotation metadata. They may
not infer ground truth from filenames, audio, papers, OCR, or model outputs.
Unavailable official labels produce `BLOCKED_GT_UNAVAILABLE`.

| Dataset | Official source | GT / resolution | Speaker / mechanism metadata | License | Status |
|---|---|---|---|---|---|
| PartialSpoof | [EURECOM publication](https://www.eurecom.fr/publication/6870); original paper [arXiv](https://arxiv.org/abs/2204.05177) | official segment/frame labels; exact parser/resolution TBD | TBD before metadata inspection | TBD | SKELETON |
| PartialEdit | [project page](https://yzyouzhang.com/PartialEdit/index.html); [Interspeech paper](https://www.isca-archive.org/interspeech_2025/zhang25g_interspeech.pdf) | localization dataset; official format/access TBD | source VCTK and editing mechanism described by paper; exact fields TBD | TBD | SKELETON |
| HAD | [Zenodo record](https://zenodo.org/records/10377492); [Interspeech paper](https://www.isca-archive.org/interspeech_2021/yi21_interspeech.pdf) | region labels reported by source; exact parser/resolution TBD | Chinese; exact fields TBD | TBD | STRETCH / SKELETON |

No adapter may be promoted to Phase 3 until source, license, split policy,
audio location, GT format, temporal resolution, and hashes are verified.
