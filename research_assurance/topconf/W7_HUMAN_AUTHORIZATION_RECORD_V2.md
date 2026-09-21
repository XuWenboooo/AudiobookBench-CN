# W7 human authorization record v2

```text
AUTHORIZED = YES
W7_FORMAL_PILOT_AUTHORIZED = YES
W7_EXECUTION_AUTHORIZED = YES
AUTHORIZED_STAGE = W7_FORMAL_PILOT_ONLY
AUTHORIZATION_DATE = 2026-09-21
AUTHORIZATION_ACTOR = HUMAN_USER_IN_CURRENT_TASK
AUTHORIZATION_SCOPE = FROZEN_W7_PILOT_PROTOCOL_V1_1_AND_FINAL_CASE_MANIFEST_V2_ONLY
```

This record records the explicit human authorization supplied in the current
task. It authorizes the frozen W7 formal pilot only: four authorized
localizers (CFPRF, MultiReso, SAL, BAM) over the two authorized external
distributions (PartialEdit and LlamaPartialSpoof R01TTS.0.b), with the frozen
case population, transforms, model identities, metrics, thresholds, and
failure policy.

```text
EXPECTED_PRE_AUTHORIZATION_HEAD = 5cf016098d519c76da1d82f70f8a792d27aac077
PROTOCOL = W7_PILOT_PROTOCOL_V1_1.md
PROTOCOL_SHA256 = AD2C318085E66796F822134259E207C74A1A01A691ADF7E1D77D4FB1242B1C80
FINAL_CASE_MANIFEST = W7_FINAL_CASE_MANIFEST_V2.jsonl.gz
FINAL_CASE_MANIFEST_SHA256 = BEA3EB3E31F1A81219617D6994ACD3381C99B972300020C4B781B8FB878DE572
PREREGISTRATION_HASH_MANIFEST = W7_PREREGISTRATION_HASH_MANIFEST_V2.json
PREREGISTRATION_HASH_MANIFEST_SHA256 = ce15af549e121679d5eba2374c544e3ce82f355053984b3e56c939a3a573d963
FINAL_EXECUTION_MANIFEST_SHA256 = 35a2324c70f1bf3d0770d55382032027ec0c61e19123e6999437fdef829c4ecb
```

The authorization does not authorize Level-2, confirmatory execution, RQ2,
RQ3, adaptive attacks, post-result search or candidate selection, or any
change to frozen scientific artifacts. `W7_HUMAN_AUTHORIZATION_RECORD_V1.md`
remains intentionally `AUTHORIZED = NO` and is preserved unchanged.

The next required action is a fresh pre-inference hash gate against these
values. Any mismatch is fail-closed and must prevent inference.

