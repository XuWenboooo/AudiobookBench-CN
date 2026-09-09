# AudiobookBench-CN Week 1 Report

## 1. Research Question

Can a reproducible temporal pipeline localize controlled substitutions inside constructed long-form real speech, and which non-trained signals succeed or fail under this narrow protocol?

## 2. Threat Model

The Week-1 attacker replaces a bounded interval of a constructed long-form sequence with real speech from another speaker. A0 is a direct cross-speaker splice; A1 adds RMS matching and a 25 ms crossfade. The setting does not include TTS, adaptive attacks, perceptual realism testing or native audiobook recording conditions.

## 3. Dataset

The source is real AISHELL-3 audio, used read-only. The frozen pilot has 12 speaker-disjoint speakers (train/val/test = 6/3/3), 480 source utterances and no cross-split speaker overlap.

## 4. Constructed Long-form Protocol

The protocol deterministically constructs 24 clean long-form sequences. These are engineering constructions, not natural audiobook recordings and not research evidence about natural pause distributions. Utterance boundaries remain traceable in the lineage manifest.

## 5. Manipulation Protocol

There are 23 paired cases, each sharing exactly one clean sequence, target interval, duration tier and split across A0 and A1. Counts are 23 A0 and 23 A1. Sample-level waveform verification, paired target/donor equality and deterministic regeneration pass. Exact sample bounds provide temporal ground truth.

## 6. Temporal Features

Day 5 processes 70 waveforms (24 clean, 23 A0, 23 A1) at 16 kHz on a 25 ms / 10 ms grid, producing 224,566 frames. Features are energy, log energy, RMS, voiced ratio, pause ratio and Praat-Parselmouth F0. All 23 paired grids align. Speaker embeddings are not fabricated at Day 5; Day 6B separately uses a real pretrained SpeechBrain ECAPA-TDNN backend.

## 7. Day 6A Negative Baseline

The non-trained B0 baseline uses only TRAIN CLEAN windows to estimate feature medians and MADs, then evaluates robust absolute-z anomaly at 100/250/500 ms. Every observed AUROC is below 0.5. Test A0/A1 AUROC is 0.379/0.378 at 100 ms, 0.331/0.350 at 250 ms and 0.324/0.346 at 500 ms.

This is a negative result: the tested generic global scalar anomaly does not localize the substitutions. Outside context is more anomalous than attack core. The failure is already present on train and cannot be explained by held-out distribution shift alone. No significance test was performed.

## 8. Day 6B Speaker-Consistency Result

B1 compares each ECAPA window embedding with a prototype computed only from the same suspect sequence. B1 uses neither speaker ID nor enrollment. On test, B1b AUROC is 0.831/0.830 at S1 and 0.901/0.897 at S2 for A0/A1. S2 AUPRC is 0.454/0.491 and F1 is 0.506/0.506, so ranking is strong but precision remains limited. Zone anomaly follows outside < boundary < core.

B2 neighbor change is negative (test AUROC roughly 0.37–0.45). B3 paired-clean differential reaches about 0.996 at S1 but is ORACLE ONLY. B4 energy transient is negative and DIAGNOSTIC ONLY. The bounded conclusion is that B1 supplies a strong temporal speaker-representation inconsistency signal, not that a deployable high-precision localizer is solved.

## 9. Day 6C Confound Controls

C0 replaces the same frozen target with a same-speaker, same-split, different-utterance donor. There are 23 C0A and 23 C0B controls; outside samples remain unchanged and inside samples change. At S1, mean core anomaly is 0.729/0.732 for A0/A1 and 0.366/0.366 for C0A/C0B. Every finite S1 paired contrast favors higher cross-speaker anomaly. C0 test AUROC is only 0.376/0.367 at S1 and 0.323/0.307 at S2.

This supports specificity to cross-speaker substitution under the current constructed, different-text protocol. It does not establish pure speaker-identity causality because linguistic content is not controlled.

The label-agnostic speech-active mask retains mainly speech-dominant windows. On S2/A0/test/full it retains 100% of positives and 66.0% of negatives. Across test/full A0/A1 it retains 97.4–100% of positives; across all split/GT slices the range is 93.3–100%. S2/A0 metrics change from 0.901/0.454/0.506 to 0.972/0.744/0.657, but the latter are **conditional-on-speech-active** and must be reported alongside the original population.

## 10. Failure Cases

- Day 6A anti-correlates with the target at every tested scale.
- B1 AUROC is much stronger than AUPRC/F1, especially at S1.
- 144 clean top-three peaks lie near constructed utterance boundaries: median distance 0.094 s and 97.2% within 1 s.
- At S2, 0.75 s attacks have AUPRC about 0.124–0.125 and F1 about 0.11–0.13.
- The S2/A1 0.75 s strict core produces no majority-positive window, so that strict-core slice is not measurable under the frozen grid.

Detailed rows are frozen in `results/week1/failure_cases.csv`.

## 11. Known Confounds

The sequences are constructed; utterance transitions create strong false positives. Cross-speaker donor utterances also differ in text. Channel, phonetic and speaker differences are therefore not fully separable. Val/test contain only six paired cases each, and overlapping windows are not independent cases.

## 12. Reproducibility

The repository provides:

`python experiments/week1_baseline/run.py --config configs/week1.yaml --verify-only`

and:

`python experiments/week1_baseline/run.py --config configs/week1.yaml --reproduce-core`

Verification re-hashes 696 frozen inputs/artifacts. Core reproduction uses frozen intermediates, performs real representative ECAPA inference and writes reconstructed C0 audio only to a temporary directory. It neither downloads AISHELL-3 nor overwrites Day 3–Day 6C outputs. Full details are in `results/week1/run.log` and `results/week1/reproduction_manifest.json`.

## 13. Supported Claims

1. The frozen real-audio temporal security pipeline is reproducible.
2. Controlled localized cross-speaker manipulations have exact sample-derived temporal ground truth.
3. The tested global scalar statistical anomaly fails in this setting.
4. Pretrained ECAPA sequence-local consistency supplies a strong temporal signal for the tested cross-speaker splices.
5. Same-speaker, different-utterance C0 does not supply a usable positive B1 localization signal.
6. Constructed utterance transitions explain a large fraction of outside false positives.
7. Conditional-on-speech-active evaluation removes mainly transition/silence-heavy negatives while retaining most positive windows.

## 14. Unsupported Claims

Week 1 does not support native audiobook robustness, neural-TTS or same-text TTS robustness, unseen-generator robustness, adaptive-attacker robustness, universal speech forensics, human perceptual realism, high-precision deployment readiness or pure speaker-identity causality.

## 15. Week 1 Conclusion

The frozen experiment chain is coherent: a generic global scalar anomaly fails; mechanism analysis motivates speaker consistency; pretrained ECAPA B1 gives a substantially stronger temporal ranking signal; same-speaker and speech-active controls narrow the interpretation and expose transition and resolution limitations. The conclusion applies only to the current controlled constructed cross-speaker substitution protocol.

## 16. Week 2 Decision

Recommendation only—no Week-2 work was started. Priority 1 is A2 same-text TTS replacement to control linguistic content; priority 2 is short-attack temporal resolution; priority 3 is native or native-like longer-form data.
