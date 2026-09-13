# Dataset Provenance Register v1

Status: **VERSION TARGETS FROZEN / NO DATA DOWNLOADED OR EVALUATED**

## PartialSpoof

- Target: v1.2, DOI `10.5281/zenodo.5766198`.
- Official repository: `https://github.com/nii-yamagishilab/PartialSpoof`,
  verified HEAD `847347aaec6f65c3c6d2f17c63515b826b94feb3`.
- Zenodo metadata: open access, version `1.2`, CC BY 4.0.
- Core files and official MD5: `database_train.tar.gz`
  `c4853ddd831e8e96b0e279fc0a512e7e`; `database_dev.tar.gz`
  `ddd4cd3221b7210ac879f67452fb209e`; `database_eval.tar.gz`
  `79c7c834d0d9979ecd374a98a059ea19`; `database_protocols.tar.gz`
  `699d81f020e4b7fa8f33747010e1cba8`; `database_segment_labels_v1.2.tar.gz`
  `c2bf6638e59ec7a5cf93c4a510fe4efe`; `database_vad.tar.gz`
  `95e77e19a1bb4f2e79ed138fd35621ad`; `README_v1.2`
  `4fec0742e2a606d1b1186067d79862d6`.
- GT: segment labels at multiple resolutions plus timestamp labels; parser,
  split and speaker-field validation remain required before data access.
- `USABLE_FOR_LOCAL_RESEARCH = CONDITIONAL YES`; `REDISTRIBUTABLE = NO/REVIEW`
  until rights are separately documented. The official code repository is
  BSD-3-Clause, but repository licensing does not determine dataset rights.

## PartialEdit

- Target: v1.1, DOI `10.5281/zenodo.18829689`.
- Zenodo metadata: version `1.1`, CC BY 4.0; timestamps corrected and speaker
  splits added.
- Core subsets: E1, E2, E1-Codec, E2-Codec. E3/E4 are excluded because they
  are not publicly released under Audiobox licensing constraints.
- Official files and MD5: `E1.tar.gz`
  `1f489d2ff488ddd6c9b655127725af2f`; `E2.tar.gz`
  `0e2cb7ba075b301de55ab8657cfa7631`; `E1-Codec.tar.gz`
  `a0c0904eaa7a079c825ab733ae69f700`; `E2-Codec.tar.gz`
  `e1e2fbfd2c145c24bf3d3a07068b06a5`; `PartialEdit_E1E2.csv`
  `3ff74c4e5cab69013d1d9c4a30f59cae`; `PartialEdit_spk.zip`
  `09b1e6e2e345918ee8250b547dcd67ba`; `modified_txt.tar.gz`
  `108934d45414c92c1bd14c9dc89b227b`; `txt.tar.gz`
  `5191f55b438d71cb47f07ccd75eddb43`; `README.md`
  `14f0fee2123e6b31ef9e36f3377c00f0`.
- GT CSV contains edited-region seconds and total duration; speaker split
  schema is official metadata, not inferred from filenames.
- `USABLE_FOR_LOCAL_RESEARCH = CONDITIONAL YES`; `REDISTRIBUTABLE = REVIEW`.
