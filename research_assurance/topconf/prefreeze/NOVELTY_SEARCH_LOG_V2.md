# Novelty Search Log v2

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Search date: **2026-09-13**

## Search protocol

The search prioritized arXiv records, publisher/conference pages, official
GitHub repositories, official dataset pages, model cards, and Zenodo records.
Blogs, surveys, search snippets, and third-party summaries were used only to
discover leads and were not used as sole support for a matrix row. No benchmark,
checkpoint inference, dataset download, or result reproduction was performed.

## Query families and outcomes

| Query family | Primary sources inspected | Relevance |
|---|---|---|
| partial/segment audio deepfake localization | PartialSpoof, HAD, Cai et al., CFPRF, BAM | Establishes the mature direct task prior art. |
| cross-dataset/OOD localization robustness | Robust Localization of Partially Fake Speech, SAL, LENS-DF, TRACE, Split-and-Conquer | Establishes strong adjacent robustness, boundary, and long-form prior art. |
| neural editing/infill/codec-consistent edits | SINE, PartialEdit, VoiceCraft, VoiceNoNG, LlamaPartialSpoof | Establishes modern manipulation-mechanism and paired-source precedents. |
| multi-region and long-form localization | MIST, SpeechSplice, LENS-DF | Establishes multi-region and deployment-regime overlap. |
| generic detector robustness/black-box attacks | Proteus, Transferable Adversarial Attacks on ADD, Defense Against Adversarial Attacks on Audio DeepFake Detection | Establishes attack and transformation robustness adjacency, without temporal suppression conjunction. |
| independent utterance detectors | AASIST, SSL-Anti-spoofing, Codecfake, RawNet2 official materials | Establishes candidate provenance; final Whether-B inclusion remains conditional. |

## Search limitations

Some 2026 papers and repositories may have incomplete checkpoint, license, or
implementation metadata. “Not verified” means the primary source did not
provide enough information in the accessible record, not that the capability
does not exist. Mandarin compatibility and code/checkpoint independence require
direct local provenance checks before authorization.
