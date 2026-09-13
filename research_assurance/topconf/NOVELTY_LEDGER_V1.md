# Novelty Ledger v1 (Protocol-Hardening Draft)

Status: **DRAFT / CLAIMS UNVERIFIED**

Purpose: maintain a dated, evidence-linked ledger of what is genuinely new in the TopConf phase. A novelty claim is not accepted merely because it is absent from the current repository.

| Claim | Closest prior art | Venue / year | What they do | Direct overlap | What they do not address | Our distinction | Risk | Safe wording | Forbidden wording | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| Detection–Localization Robustness Gap | BAM (2024), CFPRF (2024), SAL (2026), TRACE (2026) | arXiv/CVPRW/ICASSP; checked 2026-09-13 | existing works address frame/proposal/segment localization or training-free detection | partial: Where, OOD, or detection signals overlap | no reviewed source explicitly defines the same fixed-detection-retention estimand across paradigms/distributions | paired detection-retention/localization-retention under shift and transformations | HIGH | “No directly equivalent formulation was identified in the reviewed primary sources.” | first / novel / unprecedented | REVIEWED_SAFE_BOUNDARY |
| Detection-Preserving Black-Box Localization Suppression | generic black-box audio attacks; partial-localization sources above | venues/years require targeted attack review; checked 2026-09-13 | existing sources establish partial spoof/localization and robustness contexts | conceptual overlap only; direct attack conjunction unverified | preservation-constrained attack retaining Whether while degrading Where not established by current sources | bounded black-box objective with explicit preservation/budget conjunction | HIGH | “We evaluate a bounded black-box attack objective…” | first / novel / universally effective | UNSAFE_TO_CLAIM_FIRST |

The following are not novelty by themselves: partial-speech localization,
Chinese partial spoof, long-form localization, boundary-aware localization,
multiscale temporal modeling, modern TTS, generator OOD, codec robustness,
generic black-box audio attack, generic SSL backbone, temporal encoder, MoE.

Rules:

1. Every claim needs a source, date checked, and scope boundary.
2. Historical pilot observations can motivate a claim but cannot validate it.
3. Do not use observed pilot outcomes to narrow the confirmatory hypothesis after the fact.
4. Record negative or non-novel findings rather than deleting them.
