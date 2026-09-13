# Phase 3U Baseline Provenance Register v1

Status: **INITIAL — NO SECOND PATH VERIFIED YET**

| Path | Role | Repository / revision | License evidence | Checkpoint evidence | Functional status |
|---|---|---|---|---|---|
| CFPRF | `CORE_PATH` / `VERIFIED_PATH` | official CFPRF at `358a901ead8a7d84dac979c3d626e34ef82c2854` | MIT | verified FDN/PRN/XLSR hashes; GPU load pass | existing path, unchanged |
| MultiResoModel-Simple | `CORE_PATH` / candidate second path | `hieuthi/MultiResoModel-Simple@0f69db3a2d654de47822d951fe6ad256bbaac9ba` | root MIT; submodule terms tracked separately | author-linked HF `baseline-ps-e55.tgz`, pinned revision `31fd984c53a95e428551f13c4d95645b3cb8c885`; not yet downloaded | authorization frozen; validation pending |
| SAL | `BLOCKED` | official repository previously audited | source MIT | checkpoint unavailable | deferred |
| BAM | `BLOCKED` | official repository previously audited | rights unresolved | no authorized release asset | blocked rights |
| TRACE | `CROSS_DOMAIN_ONLY` | matching runnable artifact unverified | unresolved | unavailable | stretch only |
| UMMAFormer | `CROSS_DOMAIN_ONLY` | official repository candidate previously audited | MIT | new model/dataset path; not authorized here | task/modality mismatch for core audio-only gate |

`RESULT_BASED_BASELINE_SELECTIONS = 0`

MultiResoModel-Simple is not called the original official Zhang et al.
checkpoint. Its README explicitly describes an unofficial reimplementation
and states that the linked Hugging Face checkpoints are different runs from
the original LlamaPartialSpoof paper. That identity distinction remains part
of the gate.

## Append-only checkpoint result

The author-repository-linked Hugging Face checkpoint identity and metadata
were resolved, but the single authorized transport produced zero bytes because
the local curl Schannel certificate-revocation check failed. It is therefore
not a verified functional path and does not increase `EXTERNAL_BASELINE_PATHS`.

```text
MULTIRESO_SIMPLE_STATUS = CHECKPOINT_UNAVAILABLE
MULTIRESO_SIMPLE_CHECKPOINT_SHA256 = NOT_COMPUTED
MULTIRESO_SIMPLE_FUNCTIONAL_PATH = NOT_ESTABLISHED
PHASE3U_CLOSURE = BLOCKED_CHECKPOINT_UNAVAILABLE
```
