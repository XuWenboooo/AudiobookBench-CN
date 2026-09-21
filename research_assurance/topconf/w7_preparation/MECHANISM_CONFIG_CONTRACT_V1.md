# W7 Mechanism Configuration Contract v1

Status: `DRAFT_READY_TO_FREEZE` / no outcome access

This contract reuses the existing frozen project mechanism families and their
fixed-case assumptions. It does not add a parameter search or select a
mechanism from future scores.

Each mechanism record must contain a family, implementation, immutable version,
`parameter_set_id`, reference rule, target-span rule, sample rate, codec path,
seed policy, quality-gate policy and a JSON-serializable parameter object.
The canonical hash is SHA-256 over sorted compact JSON; field order cannot
change the hash. A changed parameter changes the hash and `mechanism_id`.

The permitted families are same-speaker splice/crossfade control,
cross-speaker boundary control, conventional TTS replacement,
voice-conditioned TTS/VC replacement, and neural speech editing/infilling.
Existing frozen assumptions such as same-text voice-conditioned replacement,
natural duration, mono 16 kHz, 400-sample crossfade where that inherited case
spec applies, and declared seed/reference/quality rules are copied into the
case manifest rather than inferred here.

Before the first W7 inference, every mechanism cell must have one complete
configuration object and hash. After inference starts, the object is
append-only: no severity search, stronger/weaker variant, deletion of an
unfavorable cell, or outcome-guided retry is permitted. A missing field is a
terminal configuration failure, not a default.
