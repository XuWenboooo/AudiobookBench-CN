# Second-distribution closure v1

Audit date: `2026-09-21`  
Stage: `TOPCONF-W6-SECOND-DISTRIBUTION-CLOSURE`

## Result

`READY_EXTERNAL_DISTRIBUTIONS = 2`:

1. `PartialEdit`
2. `LlamaPartialSpoof R01TTS.0.b`

LlamaPartialSpoof is promoted only after the official Zenodo `1.0.b` package passed provenance, CC BY 4.0 rights, full archive MD5/size, tar inventory, full WAV decoding, temporal GT validation, duration alignment, one-to-one audio/GT identity, and official-parser adapter compatibility. The package is an author-defined official part, not a locally selected subset.

## Candidate ledger

| Candidate | Final classification | Evidence |
|---|---|---|
| LlamaPartialSpoof `R01TTS.0.b` | READY | [`LLAMA_PARTIALSPOOF_DISTRIBUTION_READINESS_V1.md`](LLAMA_PARTIALSPOOF_DISTRIBUTION_READINESS_V1.md) |
| HQ-MPSD English | NOT_READY: integrity/transport unresolved | official MD5 mismatch and unreadable ZIP from prior route |
| HAD | NOT_READY: integrity/transport unresolved | official MD5 mismatch and ZIP stream failure from prior route |
| PartialSpoof v1.2 eval | NOT_READY: upstream identity inconsistency | two official eval IDs have no audio or matching GT |
| MIST | NOT_READY: rights unresolved | no unambiguous research/evaluation permission |

The four non-promoted candidates remain fail-closed. No readiness standard was relaxed, no case was silently dropped, and no outcome or metric was used for selection. Because the target of two verified distributions is met, no additional large-archive recovery is authorized in this closure.

## Scientific firewall

No W7 inference, Level-2 outcome, confirmatory inference, model selection, metric change, threshold change, or outcome-guided dataset selection was performed. W7 outcome fields remain `NOT_MEASURED` pending the separately authorized pilot.

The machine-readable ledger is [`SECOND_DISTRIBUTION_CLOSURE_V1.json`](SECOND_DISTRIBUTION_CLOSURE_V1.json).
