# W7 mechanism parameter evidence matrix v1

Audit date: `2026-09-21`
Scope: outcome-blind reconstruction of `mechanism_shift` evidence. This matrix
does not select a generator, a mechanism family, a parameter value, or a case
assignment.

## Evidence classes

| Class | Meaning |
| --- | --- |
| A — explicitly frozen | A source fixes the value or invariant directly. |
| B — uniquely implied | The value follows uniquely from Class-A material without a scientific choice. |
| C — permitted but non-unique | The source permits a value set but leaves more than one valid choice. |
| D — unspecified | No frozen source supplies a value or a unique derivation. |

## Field matrix

| Field | Class | Evidence | Consequence for W7 |
| --- | --- | --- |
| condition identifier | A | frozen protocol and V2 manifest use `mechanism_shift` | must remain exactly `mechanism_shift` |
| paired source, source ID, GT ID/hash, distribution, split | A | `W7_FINAL_CASE_MANIFEST_V2.jsonl.gz` and its V2 summary | preserve unchanged for every generated case |
| source text/position and edited-interval linkage | A | frozen pilot protocol §1 and canonical identity contract | must remain paired; no score-based substitution |
| allowed mechanism family set | A | frozen protocol and `MECHANISM_CONFIG_CONTRACT_V1.md` | only the five listed families may appear |
| terminal failure taxonomy | A | frozen pilot protocol §7 | missing configuration/generation/quality evidence is terminal, never a default |
| complete config object must be hashed before inference | A | mechanism contract and schema | every chosen cell must have a complete canonical object and hash |
| canonical config field names | A | `MECHANISM_CONFIG_SCHEMA_V1.json` | all required fields must be supplied by a human freeze |
| per-case provenance row | B | each V2 manifest `mechanism_shift` row uniquely fixes case ID, distribution, split, source ID/hash, GT ID/hash, and declared source manipulation label | copied into the proposal map without interpretation |
| same-text voice-conditioned replacement | C | named as an inherited assumption in the contract, but no case/family assignment is frozen | cannot be applied globally or to a particular distribution without a human decision |
| natural duration and mono 16 kHz | C | inherited assumptions are mentioned, but their per-family and per-case scope is not bound | can only be adopted when a human freeze explicitly states applicability |
| 400-sample crossfade | C | contract says “where that inherited case spec applies” | not a global default and not evidence for an unassigned case |
| mechanism family per case | D | V2 records source manipulation labels, not an executable W7 mechanism relation | human must map every proposal record or a complete deterministic group rule |
| implementation / generator / immutable version | D | no frozen artifact binds a concrete implementation to any W7 mechanism cell | human freeze required |
| parameter set and parameter values | D | schema has fields only; no values are bound | human freeze required |
| reference rule and target-span rule | D | protocol demands preservation but does not instantiate the rules | human freeze required |
| codec path, seed policy, quality-gate policy | D | required by schema but uninstantiated | human freeze required |

## Why the existing case manifest is not a configuration

`rebuild_w7_case_manifest_v2.py` assigns every `mechanism_shift` row the
SHA-256 of `MECHANISM_CONFIG_SCHEMA_V1.json`, not the SHA-256 of an executable
configuration. Its non-clean audio artifact is therefore a derivation identity
only; it is not generated audio. This establishes that the population is
frozen while confirming that mechanism parameters remain intentionally
unfrozen.

The resulting state is `PENDING_HUMAN_MECHANISM_FREEZE`; filling any Class-C
or Class-D value here would be a new scientific choice.
