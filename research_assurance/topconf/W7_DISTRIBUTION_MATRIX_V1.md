# W7 Distribution Matrix v1

Audit date: `2026-09-15`  
Status: `FROZEN PRE-RUN MATRIX / NO W7 INFERENCE`

Readiness requires all of: official source, legal-use decision, complete
audio for the selected split, temporal GT, split/speaker metadata, a frozen
adapter, integrity validation, and compatibility with the existing evaluator.
AliMeeting and AISHELL-1 are not rows here: they remain future confirmatory
pools and are not W7 external partial-deepfake distributions.

| DATASET_ID | DATA_ORIGIN | OFFICIAL_SOURCE | LICENSE_STATUS | AUDIO_AVAILABLE | FULL_AUDIO_MATERIALIZED | TEMPORAL_GT_AVAILABLE | GT_RESOLUTION | SPLIT_PROTOCOL | SPEAKER_METADATA | ADAPTER_STATUS | INTEGRITY_VALIDATION | UNIFIED_EVALUATOR_COMPATIBILITY | READY_FOR_W7 | ROLE | BLOCKER |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `PartialEdit_v1.1_E1` | official authors' release | [Zenodo 18829689](https://zenodo.org/records/18829689); project page `https://yzyouzhang.com/PartialEdit/index.html` | CC BY 4.0; local research use recorded, redistribution separately reviewed | YES | YES; 42,471 WAV | YES | edited-region start/end seconds plus duration; E1 | official train/dev/eval and speaker split metadata | YES | PASS: official CSV parser; E1 audio/CSV binding | PASS: 42,471/42,471 paths, no missing/extra/duplicate; mono PCM16 16 kHz; duration/GT checks pass | PASS for dataset input | YES | PRIMARY | none for the audited E1 subset |
| `PartialSpoof_v1.2_eval` | official authors' release | [Zenodo 5766198](https://zenodo.org/records/5766198); [official repository](https://github.com/nii-yamagishilab/PartialSpoof) | CC BY 4.0 / ODC-By acknowledgement chain; local-use decision recorded | YES at source; local recovery bounded to official eval archive | NO; original 499,712-byte file was not a valid full archive; final suspended BITS counter was 2,775,598,164/5,803,817,500 bytes and no completed destination file materialized | YES | v1.2 VAD timestamps and 0.01–0.64 s segment labels | official eval protocol; no split remixing | YES in official protocol/metadata | PASS for labels/VAD parser; full audio adapter gate pending recovery verification | labels/VAD/protocols pass; full audio archive hash/extraction/count check not passed | NO until recovery and full integrity pass | PRIMARY | official eval archive recovery ended in repeated transient remote-close errors; no inference may use the placeholder |
| `LlamaPartialSpoof_v1.0.b` | official authors' release mirrored through official project/Hugging Face dataset | [Hugging Face dataset](https://huggingface.co/datasets/HaoY0001/LlamaPartialSpoof); [official repository](https://github.com/hieuthi/LlamaPartialSpoof) | CC BY 4.0 | source archives advertised; local cache has only split `.utt/.spk` metadata | NO | YES in label files as segment start/end/label, but not locally bound to audio | segment intervals in label lines | official train/test metadata; exact W7 split not frozen | YES in split metadata | NOT_IMPLEMENTED for current unified W7 view | NOT_RUN; local audio absent | NOT_READY | NO | BLOCKED | no local audio archive and no frozen W7 adapter/integrity proof |
| `HAD` | official authors' release | [Zenodo 10377492](https://zenodo.org/records/10377492); Interspeech 2021 paper | source record does not provide a completed local rights decision | YES at source (`HAD.zip`) | NO | source paper describes localization; exact local temporal-GT binding not audited | TBD pending official archive audit | official protocol TBD | TBD | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NO | BLOCKED | 8.1 GB archive not materialized; license/GT/adapter unresolved |
| `MIST` | recent public research dataset | [paper](https://arxiv.org/abs/2605.02223); [dataset card](https://huggingface.co/datasets/tung2308/MIST_SpeechInpaintingDataset) | Research Only badge in source repository; not accepted as W7 legal-ready without rights review | source audio advertised | NO | source claims multi-region temporal localization | word/segment regions; exact schema not locally audited | TBD | TBD | NOT_IMPLEMENTED | NOT_RUN | NOT_READY | NO | BLOCKED | license is not yet cleared and no local integrity/adapter evidence |
| `HQ-MPSD` | third-party audit artifact, not an authoritative dataset release for this project | third-party cross-domain audit card only | not adopted | unknown | NO | unknown | unknown | unknown | unknown | NOT_ACCEPTED | NOT_RUN | NO | NO | BLOCKED | secondary derivative evidence cannot substitute for an official dataset release |

## PartialEdit audit binding

The local E1 archive has official MD5 `1f489d2ff488ddd6c9b655127725af2f`,
SHA256 `F4BB1A632EED8DDC66BB9285DE8B4BC07192D0539385EFE9AFC9EA04AEF3DDCB`,
42,471 CSV records and 42,471 WAV files. No result, threshold or model
selection was used to retain E1.

## PartialSpoof recovery rule

Only the official `database_eval.tar.gz` source is admissible. The existing
placeholder is preserved and cannot be used. The bounded recovery attempted
the official source twice through one resumable BITS job, reached approximately
2.80 GB; the final suspended counter was
`2,775,598,164 / 5,803,817,500` bytes after a repeated
remote-close error; no completed destination file exists. A successful recovery must bind
the official MD5 `79c7c834d0d9979ecd374a98a059ea19`, archive integrity, full
audio count against the official eval list, decodability/sample-rate checks,
and VAD/segment-label identity before the row can become `READY_FOR_W7=YES`.
