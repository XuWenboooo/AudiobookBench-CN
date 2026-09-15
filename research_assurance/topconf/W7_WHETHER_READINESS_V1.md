# W7 Whether Readiness v1

Audit date: `2026-09-15`  
Scope: protocol/capability readiness only; no W7 inference and no final
confirmatory authorization.

## Whether-A

```text
WHETHER_A_W7_READY = YES
POOLING = duration-weighted mean of finite native higher-is-better spoof scores
COMMON_SUPPORT = native 20 ms support; MultiReso retains all six scales as secondary
THRESHOLD = frozen Level-1 target FPR 0.05 empirical quantile with fixed tie rule
LEVEL2_TEST_THRESHOLD_OPTIMIZATION = PROHIBITED
FAILURE_POLICY = invalid/empty/nonfinite/out-of-duration/ambiguous output is fail-closed
```

Evidence: `TOPCONF_RQ1_CONFIRMATORY_PREREGISTRATION_V1.md` and the Phase4
design-freeze closure. The numeric final confirmatory calibration artifact is
not required for this pilot-readiness decision and remains a Gate-B item.

## Whether-B

```text
WHETHER_B_W7_READY = YES
MODEL = official AASIST utterance detector
REPOSITORY_COMMIT = a04c9863f63d44471dde8a6abcb3b082b07cd1d1
CHECKPOINT_SHA256 = 51D2D9CF0738172F61E2A384EC50A54A55363240F67C971ED55A92435BC1A1C0
LICENSE = MIT; LICENSE SHA256 B7290F12E8346F663833EC1C4F9964A84C74CD091DB042B3CD680548BDD18A3F
INPUT = mono 16 kHz, 64,600 samples
SCORE = softmax class 0, official mapping 0=spoof and 1=bonafide
STRICT_LOAD = PASS
SMOKE = PASS; finite deterministic two-class output
CALIBRATION = frozen Level-1 target-FPR rule; final numeric calibration remains Gate B
```

Evidence: `WHETHER_B_AASIST_CAPABILITY_SMOKE_V1.json`. AASIST is Whether-only
and does not contribute a localization paradigm.
