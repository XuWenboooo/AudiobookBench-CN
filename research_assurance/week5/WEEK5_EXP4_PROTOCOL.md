# WEEK5_EXP4_PROTOCOL

**Stage:** `WEEK5_EXP4_FROZEN_SSL_REPRESENTATION_REPLACEMENT_QUALIFICATION`  
**Status:** `QUALIFICATION_ONLY`

## Frozen scope

Exp4 reuses the Exp2 generator-OOD population byte-for-byte. Temporal scale search is closed: SHORT/MEDIUM/LONG, 8000/24000/64000 sample context contracts, 4000 sample hop, medium-center alignment, NaN edge handling, and Exp2 region definitions are unchanged. The three OOD folds remain exactly Exp2 Fold A/B/C.

The pre-outcome representation ladder is E0 frozen ECAPA and E1 frozen Chinese HuBERT base. No other candidate is hidden or selected after seeing OOD results. E1 is loaded only from the local cached asset; its last hidden layer is selected before evaluation, mean pooling is fixed, frame intervals are aligned by sample overlap to each canonical medium window, and per-vector L2 normalization is applied. No backbone is trainable, adapted, LoRA'd, or layer-reweighted.

## Fair detector contract

Track A is representation-only: one frozen representation anomaly score plus the same regularized linear classifier. Track B applies the same Exp2 B4 context construction to the representation-derived canonical score. For each representation, the anomaly score is a sequence-local robust prototype distance with the same 20% trim rule; no generator ID, test label, OOD calibration or generator-specific scoring is permitted. All representations use the same logistic head, training split, normalization governance, and fixed regularization `C=1.0`.

SSL embedding preprocessing statistics, if any, are fit on training generators only. The E1 embedding cache records waveform hash, model identity, hidden shape and embedding hash; a mismatch rejects reuse. E0 is the canonical Exp2 B4 baseline and must reproduce the Exp2/Exp3 frozen OOD values before E1 is accepted.

## Population, training and metrics

Training generators, dev rules, and OOD folds are inherited from Exp2. OOD data is excluded from all preprocessing, projection/PCA, calibration, model selection and thresholding. The head is a single regularized logistic classifier; no capacity or temporal-scale change is introduced. Primary metrics are ALL/BOUNDARY/CORE AUROC/AUPRC per fold, mean/worst OOD metrics, controlled-splice recovery, and in-domain qualification metrics. Secondary diagnostics include geometry and a generator probe.

Bootstrap is case-level, N=2000, seed `20260918`, percentile 95% CI, per fold and representation. Material OOD degradation is frozen as AUROC delta `< -0.03` in any fold.

## Success and stop rules

`STRONG_GO` requires a candidate to improve E0 on mean and worst OOD AUROC, improve controlled-splice OOD, improve at least 2/3 folds, avoid material degradation, and broadly preserve in-domain ALL/BOUNDARY/CORE. `WEAK_GO` allows uncertainty or one neutral fold only when mean, worst and controlled-splice directions improve. Otherwise the result is `NO_GO`. All candidates are reported. After first OOD evaluation, no model, layer, pooling, normalization, PCA, fold, case, or gate changes are allowed; an implementation bug requires an invalidation/revision record before rerun.
