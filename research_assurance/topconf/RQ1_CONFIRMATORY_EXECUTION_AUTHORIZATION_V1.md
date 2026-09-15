# RQ1 Confirmatory Execution Authorization v1 — Readiness Record

Status: **FINAL REVIEW COMPLETE / NO_GO / NOT AUTHORIZED / NOT STARTED**
Final authorization review date: **2026-09-15**
Authorization ID: `P4-RQ1-AUTH-READINESS-20260915-01`

This record prepares the final human authorization review after the Phase4
design-freeze closure. It is a binding record of the reviewed protocol, not an
execution command. It does not authorize population materialization, model
loading, inference, evaluation, bootstrap, RQ2 attack work, or RQ3 mitigation
work.

## 1. Version and provenance bindings

```text
BRANCH = topconf-dl-robustness
CURRENT_REVIEW_HEAD = ad58622 (Phase4.6 evidence commit)
LOCAL_FINAL_HEAD_BEFORE_PUSH_RETRY = ad58622
PHASE4_CLOSURE_COMMIT = 1e543c00678eca69339e874f4f9f98e44f0f77db
PHASE4_CLOSURE_SHA256 = 7B8FD4E7214840171C32F22EEBB64CBDA85B2EB2F2915535FE23F88B82AB5659
PROTOCOL_ID = P4-RQ1-DESIGN-20260914-01
PROTOCOL_COMMIT = 69dca0964c5b6865289420dae8cfb8bc15b153d9
PROTOCOL_SHA256 = 91BB6BE78BFBFF948C7B2559AFDC7ED6F3A87BA116BDC59807D1194B15BB115C
RECONCILIATION_MATRIX_SHA256 = 2FD60C3139F3FEFC180646C2E58687E83CA7DF2A2B072D84EECAC499BB8BB86F
RECONCILIATION_LEDGER_SHA256 = 6DC9744234D1B9163E19996C8B7D3C57CBDBD5BFD218A73D7E705876758C8174
OUTCOME_FIREWALL_SHA256 = A75A7C1F50B6E72C7EF4CA1B14BF65872292C93CE7B9E4C3114C83E133603CB0
REMOTE_HEAD_AT_FINAL_REVIEW = 6e7a0957809472a8189514781414b47cc4f494f8
REMOTE_PROVENANCE_SYNCHRONIZED = NO
PUSH_STATUS_AT_FINAL_REVIEW = BLOCKED_NETWORK
PUSH_FAILURE = github.com:443 connection failed on two bounded attempts
```

The protocol commit predates any Level-2 reveal. The closure history records
the earlier `BLOCKED` state and its AASIST-based resolution; the current
Phase4 state is `PASS`.

## 2. Level-2 population and freshness binding

```text
SOURCE_CORPUS_IDENTITY_FROZEN = NO
AMENDMENT_REQUIRED = NO
AMENDMENT_STATUS = NOT_REQUIRED_IMPLEMENTATION_ONLY
LEVEL2_POPULATION_MANIFEST = LEVEL2_RQ1_POPULATION_MANIFEST_V1.json
LEVEL2_POPULATION_MANIFEST_STATUS = BLOCKED_INSUFFICIENT_MATERIALIZATION_EVIDENCE
LEVEL2_POPULATION_MANIFEST_SHA256 = E270B21842ECF0A1A287B51B3984CEB56A95C0C06DEB011060BDAAA3D2B3F516
LEVEL2_EXCLUSION_UNIVERSE_MANIFEST_SHA256 = 012582F4F5BE8A31688F4AAB7EB2365CA219BD1588D790248ACA799D00288C48
LEVEL2_FRESHNESS_MANIFEST = LEVEL2_FRESHNESS_MANIFEST_V1.json
LEVEL2_FRESHNESS_MANIFEST_SHA256 = B6F753FA9664A4619F29952EEAAE0625740B16347F4286E1E55867821F9FDF2E
FRESHNESS_PROOF = INSUFFICIENT_EVIDENCE / NOT_AUTHORIZABLE
LEVEL2_INFERENCE_MANIFEST = LEVEL2_RQ1_INFERENCE_MANIFEST_V1.json
LEVEL2_INFERENCE_MANIFEST_SHA256 = CF226509E53CCAA1178222C92AB978EBEBCEFF502F60BB2C026CD8F871212047
LEVEL2_EVALUATION_MANIFEST = LEVEL2_RQ1_EVALUATION_MANIFEST_V1.json
LEVEL2_EVALUATION_MANIFEST_SHA256 = C752869CED2CF5745DFC31DC3619024A8A37A1465C4F3145C18E28911BD3FE4E
INFERENCE_MANIFEST_STATUS = NOT_MATERIALIZED / NO_CASES
EVALUATION_MANIFEST_STATUS = NOT_MATERIALIZED / NO_CASES
AUTHORIZED_POPULATION_SIZE = NONE
AUTHORIZED_CASE_ORDER = NONE
AUTHORIZED_NAMESPACE = results/topconf_level2_rq1_v1/ (PROPOSED_NOT_AUTHORIZED)
FRESHNESS_POLICY = exclude WEEK1_5_HISTORICAL_PILOT and PHASE3T_PARTIALEDIT_V1.1_E1;
  prove source/session/speaker disjointness and generator/checkpoint lineage
POPULATION = 2 independent Mandarin long-form source pools;
  400 primary sources / 120 speakers / 4 mechanisms / 40 reserve
LEVEL2_POPULATION_MANIFEST_V2 = LEVEL2_RQ1_POPULATION_MANIFEST_V2.json
LEVEL2_POPULATION_MANIFEST_V2_SHA256 = ED6FE30A4F9B7AEFA4C36821E04CB7E5F9B1780B20EE7ED9A0AA84F52B3955D0
LEVEL2_POPULATION_MANIFEST_V2_INTERNAL_IDENTITY_SHA256 = FCFFEEC32F4CAB32DA53BFAD06C0BBBC6F1354AA87277DCE1B1A4EA8E6F90674
LEVEL2_POPULATION_MANIFEST_V2_STATUS = MATERIALIZED_METADATA_CANDIDATE / POPULATION_VALIDATOR_PASS
LEVEL2_FRESHNESS_MANIFEST_V2 = LEVEL2_FRESHNESS_MANIFEST_V2.json
LEVEL2_FRESHNESS_MANIFEST_V2_SHA256 = BFD62914A0580FD96AFF1F2847727F016E0BE554AB4A9E3CDC4E418E26B94420
LEVEL2_FRESHNESS_MANIFEST_V2_STATUS = BLOCKED_INSUFFICIENT_EVIDENCE / FRESHNESS_VALIDATOR_EXIT_2
LEVEL2_V2_AUTHORIZATION = NO_GO
```

V1 remains the blocked template and is preserved. V2 is a metadata-only
candidate population produced after AISHELL-1 capacity recovery. Its
population validator passes the frozen 400/120/two-pool/4-mechanism/40-reserve
contract, but its freshness validator fails closed because the historical
exclusion universe is still partial. No case-level freshness PASS claim is
made, and V2 does not authorize inference, evaluation, GT reveal, or namespace
ownership.

## 3. Frozen baseline and score contracts

```text
BASELINE_CFPRF = official commit 358a901ead8a7d84dac979c3d626e34ef82c2854;
  FDN 5FCBBC725761F99F7CA22A6BD095242B7D4FCBB2B285A766047941766D496267;
  PRN 88B605BA432B978D481264266F3DE5BC434B4C1E74A1ABAAA1BDADC3313FAC36;
  XLS-R B08927597F2C9EB2EBD7DCC3AC78EE4B5F6021CBAC4B3A6C5A9DEEC445D80ED9
CFPRF_OUTPUT_POLICY = native FDN 20ms primary; boundary/PRN secondary
BASELINE_MULTIRESO = MultiResoModel-Simple commit 0f69db3a2d654de47822d951fe6ad256bbaac9ba;
  archive 0C394F03558ECDD7A6B81BF6C0FD8EE642C5937BA22CC852F58AE4E7DC480E32;
  inner 5B753752F7C25370C6ABF973F69F58E100DAD4B5D3EA035872335358A876FDD1;
  SSL 4E1B1AE691F26947FBF0B709FF1DD5F2F16CB586161CC3E9461E35BCD9CB5F75
MULTIRESO_SCALE_POLICY = fixed native 0.02s common scale;
  retain all 0.02/0.04/0.08/0.16/0.32/0.64s scales; no best-scale selection
```

No baseline, head, metric, scale, threshold, or sample-size decision was made
from Phase3T or pilot outcomes.

## 4. Whether-A and Whether-B binding

```text
WHETHER_A = duration-weighted mean native higher-is-better spoof score;
  invalid/empty/non-finite/out-of-support = NOT_ESTIMABLE
WHETHER_A_THRESHOLD = speaker/source-disjoint Level-1 calibration;
  target FPR 0.05; no Level-2 test optimization
WHETHER_B_MODEL = official AASIST independent utterance detector
WHETHER_B_SOURCE_COMMIT = a04c9863f63d44471dde8a6abcb3b082b07cd1d1
WHETHER_B_CHECKPOINT = models/weights/AASIST.pth
WHETHER_B_CHECKPOINT_SHA256 = 51D2D9CF0738172F61E2A384EC50A54A55363240F67C971ED55A92435BC1A1C0
WHETHER_B_LICENSE = MIT; LICENSE SHA256
  B7290F12E8346F663833EC1C4F9964A84C74CD091DB042B3CD680548BDD18A3F
WHETHER_B_INPUT = mono 16kHz / 64600 samples
WHETHER_B_SCORE = softmax class-0 spoof posterior;
  official mapping 0=spoof, 1=bonafide
WHETHER_B_TRAINING_SOURCE = ASVspoof2019 LA per official repository;
  Mandarin transfer performance is not assumed by this smoke
WHETHER_B_CAPABILITY_SMOKE = PASS
WHETHER_B_SMOKE_ARTIFACT_SHA256 = E79D3E91816039DE73F0A1FB62FDEA91E2A239AAE41B0CE5A30791A2AEFDA927
WHETHER_B_ENVIRONMENT = topconf-phase3s-cfprf-py310; Python 3.10;
  torch 2.2.2+cu121; CPU capability smoke
WHETHER_B_PERFORMANCE_SELECTION_USED = NO
WHETHER_B_LEVEL2_INFERENCE_USED = NO
```

The smoke proves only strict checkpoint loading, accepted synthetic input,
finite output, fixed two-class schema, and deterministic repeatability. It is
not AUROC validation, Level-2 performance validation, threshold tuning, or
evidence for the gap hypothesis.

## 5. Frozen estimands and design grid

```text
PRIMARY_WHERE_METRIC = native common 20ms frame AUPRC;
  positive frame iff >=0.5 support overlap with private GT interval
SECONDARY_WHERE_METRICS = native frame AUROC/AUPRC at all scales;
  compatible boundary/proposal/event diagnostics
LD_DR95 = 1 - mean(L_c/L_r over cells with D_c/D_r >= 0.95);
  paired source/reference; higher-is-better utilities;
  NOT_ESTIMABLE for invalid/empty/incompatible/undefined cells
GAP_CRITERION = >=3 localization paradigms x 2 independent distributions;
  all six cells estimable; each point >=0.10; every 95% CI lower >0.00;
  no result-driven exclusion
MECHANISMS = same-speaker splice/crossfade control; conventional TTS;
  voice-conditioned TTS/VC; neural edit/infilling
TRANSFORMS = Opus 64kbps; 16-8-16k resampling; 4kHz low-pass;
  20dB SNR noise; RT60 0.3s reverb; -6dB gain
SAMPLE_SIZE = 400 sources / 120 speakers / 4 mechanisms + 40 reserve
STATISTICAL_UNIT = paired source; speaker clustering sensitivity
BOOTSTRAP = 2,000 paired-source percentile + 2,000 hierarchical speaker->source;
  seed 20260914; deterministic child seeds from frozen identities
MULTIPLICITY = H1 single primary; Holm within locked H2-H4 families;
  two-sided alpha 0.05; no significance stopping
```

## 6. Governance and reveal binding

```text
THRESHOLD_POLICY = OFFICIAL_FIXED_THRESHOLD / LEVEL1_CALIBRATION /
  FROZEN_FIXED_FPR only; no Level-2 test-set tuning
BLINDING = gen and private GT isolated from infer/pred; evaluator joins after reveal gate
GT_ISOLATION = no labels, spans, mechanisms, source/session linkage, or failure outcomes
FAILURE_ACCOUNTING = exact one terminal per planned model/case/condition;
  missing/unknown/duplicate rows fail closed
RETRY_POLICY = at most one registered deterministic infrastructure/invalid-output retry;
  same lineage; never post-valid or score-driven
OUTPUT_NAMESPACE = results/topconf_level2_rq1_v1/<invocation_id>/
NAMESPACE_POLICY = one invocation / one owner / one authorization hash /
  one protocol-dataset identity; never overwrite Phase3T or pilot paths
REVEAL_GATE = protocol frozen + freeze hash + protocol/dataset hashes + inference complete;
  no reveal before all gates pass
STOPPING_RULE = process complete frozen population/grid and every terminal ledger row;
  never stop for significance, positivity, or convenience
```

## 7. Readiness checklist

```text
[PASS] Phase3T closure independently rechecked
[PASS] Phase4 reconciliation matrix and ledger reviewed
[PASS] Outcome firewall; REAL_LEVEL2_OUTCOMES_ACCESSED = NO
[PASS] Result-based design changes = 0
[PASS] Whether-A and Whether-B design contracts frozen
[PASS] Synthetic governance dry run and fail-closed tests
[PASS] AASIST checkpoint/license/runtime capability record
[PASS] AISHELL-1 capacity and read-only audio/transcript lineage audit
[PASS] V2 metadata-only population materialization and population validator
[NO_GO] V2 freshness proof; historical exclusion universe remains partial
[PASS] Frozen cardinality requires 400 sources / 120 speakers / 2 independent pools;
  V2 satisfies the cardinality and metadata allocation contract
[BLOCKED] Corpus-level physical cross-corpus speaker identity is not directly verifiable
[BLOCKED] Complete cross-dimensional historical exclusion universe
[NOT_READY] Level-1 calibration manifest/hash for the final run
[NOT_READY] Materialized blinded inference manifest/hash
[NOT_READY] New namespace registry ownership for the final invocation
[REVIEW] Third-paradigm H1 claim gate; without PASS, positive H1 claim is NO_GO
[REVIEW] Model-specific final environment locks and all checkpoint hashes
```

The final authorization decision remains `NO_GO`. Phase 4.6 recovered enough
audited AISHELL-1 capacity to materialize a V2 metadata candidate, while
preserving the V1 blocked artifact. The V2 freshness validator returns
`INSUFFICIENT_EVIDENCE` at the incomplete historical exclusion universe, and
public metadata cannot prove physical cross-corpus speaker identity. The
preregistration does not declare an execution-time population-generation
exception. No source-pool, case-level non-overlap, generator-lineage,
private-GT, or operator-time proof is therefore available for authorization.
This remains a Level-2 authorization blocker, not a Phase4 design defect.

## 8. Explicit non-authorization state

```text
AUTHORIZATION_STATUS = BLOCKED_LEVEL2_POPULATION
FINAL_AUTHORIZATION_DECISION = NO_GO
PHASE4_CLOSURE = PASS
PHASE4_5_CLOSURE = BLOCKED_POPULATION_MATERIALIZATION
PHASE4_6_CLOSURE = BLOCKED_POPULATION_RECOVERED_FRESHNESS_INSUFFICIENT
POPULATION_MATERIALIZATION_V1 = BLOCKED
POPULATION_MATERIALIZATION_V2 = PASS_METADATA_ONLY_CANDIDATE
LEVEL2_FRESHNESS_V2 = INSUFFICIENT_EVIDENCE
REAL_LEVEL2_OUTCOMES_ACCESSED = NO
RQ1_CONFIRMATORY_EXECUTION_AUTHORIZED = NO
RQ1_CONFIRMATORY_EXECUTION_STARTED = NO
RQ2_STARTED = NO
RQ3_STARTED = NO
```

The remaining entries are prerequisites for a later human authorization
decision, not permission to begin work. This artifact must not be converted to
`AUTHORIZED = YES` until the materialized freshness proof and all other
preflight gates pass through a new human review. No authorization commit is
created for this `NO_GO` decision.
