# BAM checkpoint official-use evidence v1

Audit date: `2026-09-21`  
This is an official-use/provenance record, not a redistribution license.

```text
SOURCE_REPOSITORY = media-sec-lab/BAM
SOURCE_REVISION = 55f3fb9e3b4dd6281597b86d7712fb23454179f6
README_SHA256 = D47FA2CD3AE6A00186DCFE824F63163A3C39F1D25AE0A79880BF71340DAFBAE1
CHECKPOINT_SHA256 = 5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1
CHECKPOINT_OFFICIALLY_PROVIDED_FOR_EVALUATION = YES
LOCAL_RESEARCH_EVALUATION_SUPPORTED_BY_OFFICIAL_SOURCE = YES
EXPLICIT_WEIGHT_REDISTRIBUTION_LICENSE = NOT_ESTABLISHED
DO_NOT_REDISTRIBUTE_CHECKPOINT = YES
```

## Pinned README evidence

The pinned README snapshot at the source revision contains the following
author-level instructions:

| Lines | Evidence | Scope |
| ---: | --- | --- |
| 59 | The authors say they provide `./checkpoint/model.ckpt` and link the Google Drive object `1eL3Ca27hEruI20lkoqkQEnZlb2GzTyHT`. | Official checkpoint provenance and author supply. |
| 62 | The authors provide `python train.py --test_only --checkpoint ./bam_checkpoint/model.ckpt --eval_root ./data/raw/eval`. | Explicit intended evaluation/test use of the checkpoint. |
| 68 | The authors request citation when code and results are used in a paper. | Publication attribution condition; not a weight redistribution grant. |

The source tree, official release metadata, and Zenodo source archive were also
checked. No checkpoint-specific redistribution license or separate weight
terms were found. Therefore this record supports restricted local evaluation
only; it does not authorize copying the checkpoint into a repository, release,
or other distribution channel.
