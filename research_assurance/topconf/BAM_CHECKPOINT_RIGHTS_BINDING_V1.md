# BAM checkpoint-specific rights binding v1

Audit date: `2026-09-21`
Scope: rights binding for the exact BAM checkpoint only. No W7 inference,
audio, prediction, metric, or outcome was accessed.

```text
BAM_CHECKPOINT_IDENTITY = PASS
BAM_CHECKPOINT_RIGHTS = FAIL_UNRESOLVED
BAM_PUBLIC_RESEARCH_EVALUATION_PERMISSION = NOT_ESTABLISHED
BAM_REDISTRIBUTION_PERMISSION = NOT_ESTABLISHED
DO_NOT_REDISTRIBUTE_CHECKPOINT = YES
```

## Artifact-specific evidence table

| Evidence source | What it establishes | What it does not establish |
| --- | --- | --- |
| Official `media-sec-lab/BAM` source at `55f3fb9e3b4dd6281597b86d7712fb23454179f6`, README | The authors describe and link a Google Drive model checkpoint, and the evaluation command consumes it. | A license, research-evaluation grant, redistribution grant, or any other terms for that checkpoint. |
| README-linked Drive object `1eL3Ca27hEruI20lkoqkQEnZlb2GzTyHT` | Provenance link for the intended checkpoint family. | Checkpoint-specific terms. The object could not be freshly inspected in this audit because the Drive endpoint timed out. |
| Controlled local `bam_checkpoint.zip` | Exact identity: 1,353,631,994 bytes and SHA-256 `5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1`. | Any permission merely from possession of the bytes. |
| Official Zenodo record `12747417`, version `version1.0.0`, CC BY 4.0 | License scope for its released source archive `media-sec-lab/BAM-version1.0.0.zip` (527,740 bytes). | A binding from that software archive or its CC BY label to the 1,353,631,994-byte Drive checkpoint. The checkpoint is not the Zenodo file. |
| Official repository releases and tracked repository files | No release asset or repository license text was found that supplies checkpoint terms. | A negative search is not a grant of permission. |

## Decision

The current evidence binds **identity and author-linked provenance**, but it
does not bind **rights** to the exact checkpoint. Code-license scope cannot be
silently extended to weights. The checkpoint must not be used for W7 execution
or redistributed until one of the following is preserved as a source record
that explicitly names or unambiguously covers this checkpoint: author terms,
a model-card/license, a Drive description with terms, an official release
asset carrying terms, or written authorization.

This is a fail-closed legal/provenance decision, not a judgment about BAM's
technical validity or performance.
