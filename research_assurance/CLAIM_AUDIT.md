# Claim Audit — Week 1 Frozen Evidence

Method: scanned WEEK1_REPORT.md, WEEK1_FREEZE.md, results/week1/claims.md,
results/week1/limitations.md, DAY6A/6B/6C reports, DAY6B_CLAIM_ADDENDUM.md,
DAY6C_INTEGRITY_CORRECTION.md, WEEK1_RETROSPECTIVE.md.

Levels: SUPPORTED / SUPPORTED WITH BOUNDARY / WEAK-NEEDS QUALIFICATION /
UNSUPPORTED / FORBIDDEN UNDER CURRENT EVIDENCE.

## 1. Claim-by-claim audit

| # | Claim (normalized) | Source | Supporting artifact | Level | Required wording | Forbidden stronger wording |
|---|---|---|---|---|---|---|
| 1 | "global anomaly fails" | WEEK1_REPORT §7 | results/day6a/metrics.json | SUPPORTED WITH BOUNDARY | "the tested generic global scalar robust-z anomaly fails on this pilot" | "global/global-statistical methods fail" (family not exhausted) |
| 2 | "every observed AUROC < 0.5" (Day6A) | WEEK1_REPORT §7 | day6a metrics.json | SUPPORTED | "every observed AUROC is below 0.5; no significance test" | "significantly below 0.5" |
| 3 | "speaker representation works" | WEEK1_REPORT §8 | day6b metrics.json | SUPPORTED WITH BOUNDARY | "B1 provides a strong temporal speaker-representation inconsistency signal" | "speaker verification/detection works" |
| 4 | "speaker inconsistency" | WEEK1_REPORT §8 | day6b metrics + figures | SUPPORTED | "sequence-local speaker-representation inconsistency" | "speaker change detected" (identity language) |
| 5 | "speaker-specific" | WEEK1_REPORT §9 | cross_vs_same_speaker.csv | SUPPORTED WITH BOUNDARY | "specific to cross-speaker substitution under the different-text protocol" | "speaker-specific in general" |
| 6 | "speaker causality" | — | — | FORBIDDEN UNDER CURRENT EVIDENCE | may only say speaker change is "the dominant identified contributor on this pilot" | "caused by speaker identity" (text not controlled) |
| 7 | "cross-speaker substitution" | WEEK1_REPORT §2/§9 | day45 manifest + A0/A1 wavs | SUPPORTED | "real-speech cross-speaker splice" | "cross-speaker TTS/deepfake attack" |
| 8 | "localization" | WEEK1_REPORT §8 | metrics_summary.csv | SUPPORTED WITH BOUNDARY | "temporal localization/ranking signal (AUROC)" + AUPRC/F1 quoted | "precise localization", "deployable localizer" |
| 9 | "strong signal" | WEEK1_REPORT §8 | S2 AUROC 0.901/0.897 | SUPPORTED WITH BOUNDARY | "strong temporal ranking signal" | "strong detector" |
| 10 | "high precision" | — | AUPRC/F1 | UNSUPPORTED | quote AUPRC/F1 as limitations | any high-precision claim |
| 11 | "deployable" | — | — | UNSUPPORTED for high-precision deployment | may say "deployable setting (no enrollment/clean reference)" for B1's *inputs* | "deployment-ready" |
| 12 | "deepfake" | — | — | FORBIDDEN UNDER CURRENT EVIDENCE | may describe as future threat context only | any deepfake detection result |
| 13 | "TTS" | — | — | FORBIDDEN UNDER CURRENT EVIDENCE (as tested subject) | A2 as future direction only | "TTS localization shown" |
| 14 | "forensics" | — | — | UNSUPPORTED (universal) | "forensics-motivated mechanism study" | "forensic tool/benchmark" |
| 15 | "robust" | — | — | UNSUPPORTED (unqualified) | "robust to X" only with an X experiment | unqualified "robust" |
| 16 | "generalize" | — | — | FORBIDDEN UNDER CURRENT EVIDENCE | "within-pilot" language only | "generalizes to unseen X" |
| 17 | "significant" | WEEK1_REPORT §7 | — | SUPPORTED (as negation) | "no significance test was performed" | "statistically significant" anywhere |
| 18 | "boundary artifact" | DAY6B §12, B4 | zone audit + B4 | SUPPORTED WITH BOUNDARY | "the tested energy-transient cue does not explain the B1 result" | "all boundary artifacts ruled out" |
| 19 | "transition confound" | WEEK1_REPORT §10/C4 | clean_transition_audit.csv | SUPPORTED | "constructed utterance transitions explain a large fraction of outside false positives" | "all false positives are transitions" |
| 20 | "speech-active improvement" | WEEK1_REPORT §9 | population audit | SUPPORTED WITH BOUNDARY | "conditional-on-speech-active evaluation; removes mainly transition/silence-heavy negatives" | "mask improves the detector" |
| 21 | "conditional evaluation" | WEEK1_REPORT §9 | original_vs_masked + population audit | SUPPORTED | always paired with the unmasked population | masked-only presentation |
| 22 | "oracle" | WEEK1_REPORT §8 | B3 rows/figures | SUPPORTED | "B3 is ORACLE ONLY (needs paired clean)" | using B3 in deployable tables |
| 23 | "real audiobook" | — | — | FORBIDDEN UNDER CURRENT EVIDENCE | "constructed long-form sequences" | "audiobook data/results" |
| 24 | "constructed long-form" | WEEK1_REPORT §4 | lineage manifest | SUPPORTED | with the not-native-audiobook caveat | presenting construction as evidence about natural speech |

## 2. Verdict

- **Claim audit: PASS.**
- All five SUPPORTED claims in `results/week1/claims.md` map 1:1 to frozen
  artifacts; the seven forbidden/unsupported families are consistently
  listed as unsupported in every major document (report, freeze, claims,
  limitations, retrospective).
- Two wording-level watch items (LOW, no artifact change required):
  1. WEEK1_REPORT §10 reports the C4 median as 0.094 s; the artifact
     median is 0.093375 s (standard 3-dp rounding gives 0.093). Cosmetic;
     see NUMERIC_TRACEABILITY.md.
  2. "B2 negative (test AUROC roughly 0.37–0.45)" is accurate
     (0.370–0.447 across scales/variants) — keep the word "roughly".
