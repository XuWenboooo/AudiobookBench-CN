# Whether-B Candidate Audit v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**
Audit date: **2026-09-13**
Scientific Whether-B benchmark runs: **NO**

Whether-B must be an independently trained/frozen utterance-level detector,
not a score computed from a localizer. This is a provenance and feasibility
audit only. Checkpoint hashes are deliberately `NOT_DOWNLOADED`; no checkpoint
was loaded and no real dataset was evaluated.

## Shortlist

| Candidate | Classification | Paper / source | Official repo and commit checked | License | Checkpoint / source | Architecture and output | Training data | Input / language | Hardware / limitations |
|---|---|---|---|---|---|---|---|---|---|
| Codecfake W2V2+AASIST (codec-trained or co-trained variant) | **VERIFIED_CANDIDATE at source level; conditional for final inclusion** | [Codecfake paper](https://arxiv.org/abs/2405.04880) | [official repo](https://github.com/xieyuankun/Codecfake), `72c32e2840eef95fbeade349425fa9c5391fa11e` | Repository/data rights need separate review; dataset states CC BY-NC-ND 4.0 | `pretrained_model/codec_w2v2aasist/anti-spoofing_feat_model.pt` and `cotrain_w2v2aasist/...`; source listed in README; hash `NOT_DOWNLOADED` | XLS-R/wav2vec-style features with AASIST backend; utterance spoof score | Codecfake codec/ALM data; optional ASVspoof co-training | 16 kHz contract must be checked in code; Mandarin/general compatibility not established from metadata alone | README documents offline feature extraction and multi-GPU option; exact inference VRAM not stated; no localization head, hence architecturally independent candidate |
| AASIST | **CONDITIONAL_CANDIDATE** | [AASIST paper](https://arxiv.org/abs/2110.01200) | [official repo](https://github.com/clovaai/aasist), `a04c9863f63d44471dde8a6abcb3b082b07cd1d1` | MIT in repository metadata | `AASIST.pth` official release path; hash `NOT_DOWNLOADED` | Raw waveform spectro-temporal graph attention; 2-class utterance score | ASVspoof 2019 LA | Mono/16 kHz contract and crop behavior require local verification; Mandarin transfer conditional | Small model; upstream docs do not provide a final Mandarin compatibility guarantee; no localization output |
| SSL-Anti-spoofing / wav2vec2 detector | **CONDITIONAL_CANDIDATE** | [paper](https://arxiv.org/abs/2203.01573) and [official repo](https://github.com/TakHemlata/SSL_Anti-spoofing) | `4acaa61dcef5f7610f43aa4d0b29c4559b970cd2` | License and dependency terms require local verification | Repository provides training/evaluation artifacts; checkpoint identity/hash `NOT_DOWNLOADED` | SSL front-end plus utterance classifier; no localization output claimed | ASVspoof/ADD task data per repository/paper | Input and multilingual/general compatibility need code-level verification | Legacy fairseq/CUDA dependency; may be hard to reproduce on current host; independent output form |
| Codecfake W2V2+LCNN / MelCNN variants | **CONDITIONAL_CANDIDATE** | [Codecfake paper](https://arxiv.org/abs/2405.04880) | Same official repo and commit above | Same rights review as above | `pretrained_model/codec_w2v2lcnn/...` or `codec_mellcnn/...`; hash `NOT_DOWNLOADED` | Independent utterance detector; architecture differs from AASIST variant | Codecfake | Input contract and Mandarin compatibility conditional | More legacy dependency surface; candidate only if checkpoint and license chain are clear |
| RawNet2 anti-spoofing | **BLOCKED** | [RawNet2 anti-spoofing paper](https://arxiv.org/abs/2011.01108) | [official RawNet materials](https://github.com/jungjee/RawNet); exact anti-spoofing repository/checkpoint not verified in this audit | Code/repository metadata differs by implementation; final license chain unresolved | No frozen, source-identified anti-spoofing checkpoint was verified here; hash `NOT_DOWNLOADED` | Raw waveform utterance detector in published anti-spoofing use | ASVspoof 2019 LA in common recipes | General/Mandarin compatibility conditional | Do not select until exact checkpoint, commit, preprocessing, and rights are verified |
| SINE detector release | **BLOCKED pending provenance** | [SINE paper](https://arxiv.org/abs/2501.03805) | Dataset card exists at [SINE](https://huggingface.co/datasets/PeacefulData/SINE); independent frozen detector repo/commit not verified | Dataset card says Apache 2.0; model artifact terms not verified | Paper says models will be released; checkpoint identity/hash `NOT_DOWNLOADED` | Detector has utterance and frame outputs in paper, so independence must be checked | SINE/LibriLight plus detector recipe | English-focused source; Mandarin compatibility not established | Not a final candidate until exact release and model contract are pinned |
| Public hosted or community-only detectors | **NOT_RECOMMENDED** | No authoritative paper/checkpoint chain selected | Varies; often no reproducible commit | Varies | Identity, training data, and hashes incomplete | Output semantics and calibration may be opaque | Unknown | Language and privacy risks | Hosted/opaque inference is incompatible with a frozen, auditable Whether-B contract |

## Verification gates before authorization

For each retained candidate, record the exact paper, official repository commit,
checkpoint URL, checkpoint SHA256, code license, checkpoint/data license,
architecture, training datasets, preprocessing, output polarity, threshold
policy, and hardware smoke-test result. A load-only smoke test may be performed
after authorization of that infrastructure check, but a benchmark or real
research-data inference is outside this lane.

At least one retained candidate must be architecturally independent from every
localizer in the common core. If no candidate satisfies public reproducibility,
frozen checkpoint, reasonable general/Mandarin compatibility, and rights
requirements, Whether-B remains a stated limitation rather than a forced
comparison.

## Selection discipline

No candidate was selected, excluded, or ranked by RQ1 gap performance. The
labels above describe provenance and feasibility only. The current shortlist is
therefore not a scientific result and cannot authorize Phase 4.
