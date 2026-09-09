# Research Risk Register — AudiobookBench-CN (post Week 1)

Probability/impact: LOW / MEDIUM / HIGH. "Blocks publication" refers to the
current mechanism-study paper scope; "blocks Week2" refers to the A2
same-text TTS experiment.

| # | Risk | Stage | Prob. | Impact | Current mitigation | Remaining mitigation | Blocks pub? | Blocks W2? |
|---|---|---|---|---|---|---|---|---|
| 1 | Constructed-protocol boundary shortcut (stitched utterances + fixed gaps create artificial transitions) | D3.5/D6C | HIGH | MEDIUM | C4 transition audit; speech mask; disclosure everywhere | native/native-like long-form data; natural-pause construction | No (scoped claims) | No |
| 2 | Different-text confound: speaker vs linguistic content not separable | D4.5/D6C | HIGH | HIGH | C0 same-speaker control (specificity shown) | A2 same-text TTS replacement | No (claims scoped) | **YES — A2 is the designed mitigation** |
| 3 | TTS train-data contamination unknown (AISHELL-3 may appear in TTS training sets) | W2 (future) | UNKNOWN | HIGH | not yet assessable | generator audit / held-out speaker check when A2 runs | No | Partially (informs generator choice) |
| 4 | Speaker-reference leakage into deployable path | D6B | LOW | HIGH | unit tests (no enrollment/no speaker-ID; B1 self-prototype only) | keep CI guards | No | No |
| 5 | Small test case count (6 val / 6 test) | D4.5 | HIGH (certainty) | MEDIUM | case-level bootstrap CIs; bounded claims | expand paired cases in later phases | No (CIs reported) | No |
| 6 | Native audiobook gap | D3.5 | HIGH (certainty) | MEDIUM | scoped claims; construction lineage | native data acquisition | No for mechanism paper; Yes for applied venues | No |
| 7 | Channel/codec mismatch untested | — | MEDIUM | MEDIUM | scoped out in claims | channel-shift protocol | No | No |
| 8 | Unseen generator generalization | — | MEDIUM | HIGH | scoped out in claims | generator study | No | No |
| 9 | Short-attack resolution (S2 core unmeasurable at 0.75 s) | D6B grid | HIGH (certainty) | MEDIUM | resolution audit; S1 retains coverage | multi-scale fusion / finer grid (future) | No | No |
| 10 | Conditional-population misinterpretation (masked metrics read as detector gain) | D6C | MEDIUM | MEDIUM | conditional-on-speech-active framing enforced; population audit; claim addendum | matched-population reporting (FUTURE WORK) | No | No |
| 11 | ECAPA embedding may encode non-speaker traits (channel/prosody) | D6B backend | MEDIUM | MEDIUM | C0 control; careful wording | disentanglement study | No | No |
| 12 | Environment drift (torch unpinned; audit ran 2.13 vs 2.14) | D6B | LOW | LOW | frozen embeddings decouple evaluation; cross-version cosine 0.99999988 | pin torch in a lock file | No | No |
| 13 | No git metadata in canonical directory | repo | MEDIUM | LOW | 696-hash chain; disclosure of overwrite incident | initialize git (infra task) | No | No |
| 14 | Day-8 CosyVoice environment instability | W2 (Day 8, other session) | MEDIUM | MEDIUM | owned by Day-8 Codex; this audit does not touch it | Day-8 precheck gates | No | Only via schedule |
| 15 | Over-claiming drift in future writing | writing | MEDIUM | HIGH | CLAIM_AUDIT.md required/forbidden wording; claims.md frozen | run claim audit on every draft | Preventable | No |

## Top risks by expected impact

1. **#2 Different-text confound** — the single largest interpretive risk;
   A2 is its designed resolution.
2. **#3 TTS contamination** — could undermine A2 conclusions if the chosen
   generator has memorized AISHELL-3 speakers; assess at A2 design review.
3. **#1/#6 constructed/native gap** — scopes the paper; not fixable in
   Week 2.

All 15 risks currently have active or planned mitigation; none invalidates
the frozen Week-1 evidence under its scoped claims.
