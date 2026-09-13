# Novelty Ledger v1 (Protocol-Hardening Draft)

Status: **DRAFT / CLAIMS UNVERIFIED**

Purpose: maintain a dated, evidence-linked ledger of what is genuinely new in the TopConf phase. A novelty claim is not accepted merely because it is absent from the current repository.

| Claim | Closest prior art | Venue / year | What they do | Direct overlap | What they do not address | Our distinction | Risk | Safe wording | Forbidden wording | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| Detection–Localization Robustness Gap | `TBD; systematic primary-literature review required` | `TBD` | `TBD` | `TBD` | `TBD` | paired detection-retention/localization-retention under shift and transformations | HIGH | “No directly equivalent formulation was identified in the current review,” only with dated evidence | first / novel / unprecedented | UNSAFE_TO_CLAIM_FIRST |
| Detection-Preserving Black-Box Localization Suppression | `TBD; attack and audio-forensics review required` | `TBD` | `TBD` | `TBD` | `TBD` | conjunction of preserved Whether, degraded Where, and preservation/budget constraints | HIGH | “We evaluate a bounded black-box attack objective…” | first / novel / universally effective | UNSAFE_TO_CLAIM_FIRST |

The following are not novelty by themselves: partial-speech localization,
Chinese partial spoof, long-form localization, boundary-aware localization,
multiscale temporal modeling, modern TTS, generator OOD, codec robustness,
generic black-box audio attack, generic SSL backbone, temporal encoder, MoE.

Rules:

1. Every claim needs a source, date checked, and scope boundary.
2. Historical pilot observations can motivate a claim but cannot validate it.
3. Do not use observed pilot outcomes to narrow the confirmatory hypothesis after the fact.
4. Record negative or non-novel findings rather than deleting them.
