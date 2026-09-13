# RQ1 Ground-Truth Blinding and Leakage Draft v1

Status: **DRAFT / CANDIDATE / PRE-FREEZE / NON-AUTHORIZING**

This design is intended for a single-person research workflow. It provides
mechanical separation and auditability; it does not pretend that a second human
custodian exists.

## Namespaces and manifests

| Artifact | Namespace | Accessible during inference? | Contains |
|---|---|---:|---|
| Generation manifest | `gen/<invocation_id>/` | No, after generation closes | Source/config/model inputs, generator status, output hashes |
| Private GT manifest | `gt/<case_id_hash>/` | No | Labels, target spans, mechanism, source linkage, adjudication fields |
| Public inference manifest | `infer/<invocation_id>/` | Yes | Hashed case IDs, authorized audio paths/hashes, input contract, no labels |
| Predictions | `pred/<invocation_id>/<model_id>/` | Yes after inference | Raw outputs, model/checkpoint identity, no GT |
| Evaluation package | `eval/<invocation_id>/` | Only after authorization | Joined predictions/GT, metrics, failure ledger, closure |

Case IDs should be random, non-semantic, and independent of source filename,
mechanism, target position, or label. The private mapping from case ID to
ground truth must never be in the inference working directory.

## Mechanical controls

1. Generate and hash a private GT manifest before producing the public
   inference manifest.
2. Build the inference manifest from a schema that rejects label, mechanism,
   target-span, and failure-outcome fields.
3. Run inference in a process/container whose working directory and environment
   do not contain the private GT path.
4. Make the GT manifest read-protected and use a separate evaluator command that
   is not importable by model/threshold/attack code.
5. Require an evaluation authorization record naming the inference namespace,
   prediction hashes, and GT hash before joining the two namespaces.
6. Hash every manifest and record the exact code commit, command, seed, and
   operator timestamp.

## Accidental unblinding policy candidate

The following events are incidents:

- GT opened before protocol/inference freeze;
- a case-specific label, target span, or source-to-case mapping inspected;
- inference, threshold, model, attack, or reference-selection code accesses GT;
- manual sample selection is changed because of GT or a GT-derived outcome.

For an incident, preserve logs and files, stop the affected run, create an
incident record, and mark the affected confirmatory scope invalid. No silent
repair, replacement parent, retry, deletion, or fallback is permitted. A new
versioned protocol is required for any replacement scope.

## Limitation

The workflow cannot claim independent human custody. It can claim only
mechanical namespace separation, access control, hashed provenance, and a
fail-closed evaluator gate. This limitation must remain in the final report.
