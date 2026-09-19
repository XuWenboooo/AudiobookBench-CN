# BAM strict-load and temporal smoke evidence v1

Audit date: `2026-09-19`

The official BAM source at commit `55f3fb9e3b4dd6281597b86d7712fb23454179f6`
and the README-linked Google Drive checkpoint were recovered. The source
archive SHA256 is `86E3B131017AB711489B452B24A6F7CB1D4A4418450644147BD032A2E2FB13D6`;
the checkpoint ZIP SHA256 is
`5C7379D23028606D3BEEB8B1AA5C340395FCC403CE70A2CA559EA322AB2994D1`.

The checkpoint contains the complete WavLM state under
`model.ssl_layer.model.*`. A deterministic wrapper placed those unchanged
tensors in the fairseq structure expected by the official s3prl loader. The
official BAM network then loaded the checkpoint with `strict=True`.

```text
BAM_STRICT_LOAD = PASS
BAM_SYNTHETIC_INPUT = B=1, 33280 samples, 16 kHz
BAM_OUTPUT_SHAPES = (1, 13, 2), (1, 13)
BAM_OUTPUT_FINITE = PASS
SCIENTIFIC_INFERENCE = NO
OUTCOME_GUIDED_SELECTION = NO
```

The repository contains no LICENSE file or explicit research-use grant in its
README, and the linked checkpoint has no separate rights statement in the
recovered material. Therefore:

```text
BAM_TECHNICAL_REPRODUCIBILITY = PASS
BAM_RIGHTS_GATE = UNRESOLVED / FAIL_CLOSED
BAM_W7_ELIGIBLE = NO
```

This evidence does not promote BAM or count it as a W7 paradigm.
