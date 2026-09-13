# Closest Prior-Art Matrix v2

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Search cut-off: **2026-09-13**
Scope: primary papers, publisher/conference pages, official repositories, and
official dataset/model pages. No project scientific outcome was used.

## Matrix

`Yes` means the primary source explicitly presents the capability; `Partial`
means it is present only for a subset, auxiliary output, or related setting;
`No/Not verified` means it was not established in the source review.

| Work | Year / venue | Primary source | Task | Dataset / manipulation | Detection | Localization | Robustness / OOD | Attack | Black-box | Detection preservation | Temporal localization suppression | Main overlap | Main distinction | Risk |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PartialSpoof | 2023 TASLP (paper 2022 preprint) | [paper](https://arxiv.org/abs/2204.05177), [official repo](https://github.com/nii-yamagishilab/PartialSpoof) | Partial spoof detection and segment localization | PartialSpoof v1.2; embedded synthesized/transformed short segments | Yes | Yes | Limited cross-task/in-domain emphasis | No | No | No | No | Establishes partial-spoof detection/localization and multi-resolution labels | Does not formulate paired retained-detection versus localization degradation across paradigms/distributions | HIGH |
| Half-Truth / HAD | 2021 Interspeech | [paper](https://www.isca-archive.org/interspeech_2021/yi21_interspeech.pdf), [dataset](https://zenodo.org/records/10377492) | Partial fake detection and pinpointing | Mandarin/Chinese partial word edits using TTS; HAD | Yes | Yes | Generalization is not the proposed estimand | No | No | No | No | Chinese partial spoof and temporal localization | Does not test a cross-paradigm robustness gap or preservation-constrained suppression | HIGH |
| Cai et al. frame/boundary systems | 2024 CSL / ADD line | [publisher record](https://www.sciencedirect.com/science/article/pii/S088523082300116X) | Frame detection plus boundary-aware localization | ADD partial-fake tracks and public datasets | Yes | Yes | Multiple public datasets, not the proposed paired gap | No | No | No | No | Explicit boundary detector and localization | Boundary integration is a method, not a detection-retention estimand | HIGH |
| CFPRF | 2024 ACM MM | [paper](https://arxiv.org/abs/2407.16554), [official repo](https://github.com/ItzJuny/CFPRF) | Coarse-to-fine temporal forgery proposal detection/localization | PartialSpoof, HAD, LAV-DF; proposal refinement | Yes | Yes | Some dataset transfer reported | No | No | No | No | Proposal-level Where and detection outputs | No preservation-constrained black-box attack or paired robustness gap | HIGH |
| BAM | 2024 Interspeech | [paper](https://www.isca-archive.org/interspeech_2024/zhong24_interspeech.pdf), [official repo](https://github.com/media-sec-lab/BAM) | Boundary-aware partial-spoof localization | Partial-spoof data; boundary attention | Yes | Yes | Not the proposed cross-distribution estimand | No | No | No | No | Boundary shortcut is directly relevant to localization reliability | Does not compare retained Whether with degraded Where under controlled shifts | HIGH |
| Efficient temporary deepfake location | 2024 ICASSP | [CFPRF repository citation](https://github.com/ItzJuny/CFPRF) | Embedding-based partial spoof location | Partial-spoof challenge setting | Yes | Yes | Not verified as a robustness study | No | No | No | No | Temporal location from learned/embedding cues | No detection-preserving suppression objective | MEDIUM |
| SAL | 2026 ICASSP / arXiv | [paper](https://arxiv.org/abs/2601.21925), [official repo](https://github.com/SentryMao/SAL) | Segment-aware partial deepfake localization | Multiple partial-localization datasets; boundary and interior cues | Yes | Yes | Explicit in-domain and OOD discussion | No | No | No | No | Directly studies transition/boundary shortcut and OOD localization | Still a model/training method; not the proposed paired gap estimand | HIGH |
| Robust Localization of Partially Fake Speech | 2025 arXiv | [paper](https://arxiv.org/abs/2507.03468) | Metrics and cross-dataset localization audit | PartialSpoof, LlamaPartialSpoof, Half-Truth; CFPRF | Yes | Yes | Yes, cross-dataset | No | No | No | No | Closest robustness/metric critique and explicit OOD localization degradation | Does not define a retained-detection-constrained, paired, multi-paradigm gap or attack | HIGH |
| PartialEdit | 2025 Interspeech | [paper](https://arxiv.org/abs/2506.02958), [project page](https://yzyouzhang.com/PartialEdit/) | Detection and localization of neural speech edits | VCTK source; VoiceCraft, SSR-Speech, Audiobox-Speech/Audiobox codec-based edits | Yes | Yes | Cross-editing/generalization | No | No | No | No | Modern neural editing, codec artifacts, and content-region definition | Does not measure detection/localization robustness retention as a predeclared cross-paradigm estimand | HIGH |
| SINE | 2025 SLT | [paper](https://arxiv.org/abs/2501.03805), [dataset card](https://huggingface.co/datasets/PeacefulData/SINE) | Detection/localization of seamless speech edits | LibriLight/LibriHeavy; Voicebox-style infilling and cut/paste | Yes | Yes | Cross-editing and unseen-model discussion | No | No | No | No | Directly separates cut/paste from seamless infilling | No preservation-constrained adversarial suppression objective | HIGH |
| LENS-DF | 2025 arXiv | [paper](https://arxiv.org/abs/2507.16220) | Long-form noisy speech detection and temporal localization recipe | Long/noisy/multi-speaker generated speech | Yes | Yes | Realistic conditions and robustness recipe | No | No | No | No | Long-form and realistic media regime | Long-form/noise is a regime, not the same gap or attack claim | HIGH |
| LlamaPartialSpoof | 2024 arXiv / dataset | [paper](https://arxiv.org/abs/2409.14743), [official repo](https://github.com/hieuthi/LlamaPartialSpoof) | LLM-driven partial fake speech dataset | English partial edits with commercial/LLM-driven generation | Yes | Yes where labels permit | OOD target used by later audits | No | No | No | No | Modern, semantically targeted partial edits | Dataset/manipulation precedent, not the proposed estimator | MEDIUM |
| TRACE | 2026 CVPRW | [paper](https://openaccess.thecvf.com/content/CVPR2026W/MMFM5/html/khan_TRACE_Training-Free_Partial_Audio_Deepfake_Detection_via_Embedding_Trajectory_Analysis_CVPRW_2026_paper.html), [arXiv](https://arxiv.org/abs/2604.01083) | Training-free partial deepfake detection from embedding trajectories | PartialSpoof and other benchmarks; splice-boundary dynamics | Yes | Partial / temporal signal | Yes, multiple benchmarks and foundation models | No | No | No | No | Training-free and boundary/trajectory shortcut analysis | Does not test a detection-preserving localization suppression condition | HIGH |
| Split and Conquer | 2026 arXiv | [paper](https://arxiv.org/abs/2604.02913) | Boundary detection plus segment classification | PartialSpoof and Half-Truth | Yes | Yes | Cross-dataset evidence reported | No | No | No | No | Explicitly decomposes boundary detection and segment authenticity | No retained-Detection/Where gap estimand or black-box attacker | HIGH |
| SpeechSplice | 2026 Computer Speech & Language | [publisher article](https://www.sciencedirect.com/science/article/pii/S1077314226002559) | Audio novelty for splicing detection/localization | SpeechSplice and PartialSpoof; synthetic portions spliced into pristine speech | Yes | Yes, multiple points | Evaluates realistic/bias-free corpus | No | No | No | No | Multiple splicing points and training on clean speech | Splicing novelty pipeline, not preservation-constrained suppression | HIGH |
| MIST / ISA / SF1 | 2026 arXiv | [paper](https://arxiv.org/abs/2605.02223) | Multi-region inpainting tampering localization | Six languages; 1--3 word-level neural inpainting regions | Yes | Yes | Zero-shot/generalization framing | No | No | No | No | Multi-region, fine-grained localization, unknown region count | A new dataset/method/metric; no detection-retention robustness estimand | HIGH |
| VoiceNoNG | 2025 Interspeech | [official research page](https://research.nvidia.com/labs/twn/publication/interspeech_2025_voicenong/), [paper](https://www.isca-archive.org/interspeech_2025/huang25c_interspeech.pdf) | Neural speech editing generation | Codec latent flow-matching speech edits | No | No | Generates realistic/robust edits; not a detector study | No | N/A | N/A | N/A | Modern mechanism precedent and codec-consistency concern | Generator, not a forensic robustness or attack study | MEDIUM |
| VoiceCraft | 2024 arXiv | [paper](https://arxiv.org/abs/2403.16973), [official repo](https://github.com/jasonppy/VoiceCraft) | Zero-shot speech editing/TTS | RealEdit/in-the-wild; neural codec token infilling | No | No | Realistic editing conditions | No | N/A | N/A | N/A | Modern codec-based speech-editing mechanism | Generator precedent only | MEDIUM |
| Proteus | 2026 arXiv | [paper](https://arxiv.org/abs/2606.29544) | Automated detector robustness testing | Codec, noise, reverberation, compression, VoIP chains | Yes | No | Robustness/search over transformations | Yes, detector-flipping transformations | Yes in a detector-access sense | No | No | Closest generic transformation-search and detector robustness work | Does not localize time or require Whether preserved while Where is suppressed | HIGH |
| Transferable adversarial attacks on ADD | 2025 arXiv | [paper](https://arxiv.org/abs/2501.11902) | Black/gray/white-box ADD attack transfer | ADD benchmark datasets; GAN/adversarial perturbations | Yes, target detector | No | Cross-dataset transfer discussed | Yes | Yes / transfer | No | No | Black-box/transferable audio detector attack precedent | No temporal localization output or detection-preserving localization objective | HIGH |
| Defense against adversarial attacks on Audio DeepFake Detection | 2022 arXiv | [paper](https://arxiv.org/abs/2212.14597) | Detector attack and adaptive defense | ADD models including RawNet3 | Yes | No | Attack robustness | Yes | Transfer/white-box scenarios | No | No | Adversarial detector robustness precedent | Not partial temporal Where and not the proposed conjunction | MEDIUM |

## Synthesis

The closest prior work is distributed across separate axes: cross-dataset
localization robustness (Luong et al.), boundary dependence (BAM/SAL/TRACE),
neural editing (SINE/PartialEdit/VoiceCraft/VoiceNoNG), long-form and realistic
media conditions (LENS-DF), multi-region localization (MIST), and generic
detector attacks (Proteus/Farooq et al.). The review found no primary source
that combines these into the exact paired estimand “localization degradation
conditioned on retained utterance detection,” evaluated across independent
localization paradigms and distributions. This is a bounded search finding,
not a first-ever claim; see `CLAIM_SAFETY_REVIEW_V2.md`.

## Sources and audit notes

Primary source URLs are preserved inline so a reviewer can re-open the exact
paper, official repository, dataset page, or publisher record. Repository HEAD
identity checks on 2026-09-13 were performed read-only for PartialSpoof
(`847347aaec6f65c3c6d2f17c63515b826b94feb3`), BAM
(`55f3fb9e3b4dd6281597b86d7712fb23454179f6`), CFPRF
(`358a901ead8a7d84dac979c3d626e34ef82c2854`), SAL
(`b4e80d1d2fd98f3d8b9a85a47837ab3a73e12485`), AASIST
(`a04c9863f63d44471dde8a6abcb3b082b07cd1d1`), SSL-Anti-spoofing
(`4acaa61dcef5f7610f43aa4d0b29c4559b970cd2`), Codecfake
(`72c32e2840eef95fbeade349425fa9c5391fa11e`), and VoiceCraft
(`f0a7a971363905883a21c466a3aa4ea2d4c0b690`). No repository was cloned and
no checkpoint or dataset was downloaded.
