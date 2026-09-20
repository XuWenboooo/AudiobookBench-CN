# W6 external-distribution recovery closure v1

Audit date: `2026-09-20`  
Stage: `TOPCONF-W6-EXTERNAL-DISTRIBUTION-RECOVERY`

```text
BASELINE_HEAD = 3f67838c7f598c4f7eddad882b5057f82c169bd3
FINAL_AUDIT_HEAD_AT_EVIDENCE_BASELINE = 3f67838c7f598c4f7eddad882b5057f82c169bd3
READY_LOCALIZERS = 4
DISTINCT_LOCALIZATION_PARADIGMS = 4
READY_EXTERNAL_DISTRIBUTIONS = 1
W6_GATE = BLOCKED
W7_PROTOCOL_FROZEN = NO
W7_EXECUTED = NO
W7_SCIENTIFIC_INFERENCES = 0
LEVEL2_OUTCOMES_ACCESSED = NO
```

## Acceptance decisions

| Candidate | Provenance/rights | Integrity | audio↔GT↔identity | Adapter | Decision |
|---|---|---|---|---|---|
| PartialEdit E1 | PASS | PASS | PASS | PASS | READY |
| PartialSpoof v1.2 eval | PASS | PASS | FAIL: two official eval IDs have no audio/GT | FAIL-closed | NOT_READY |
| HAD | PASS | FAIL: official MD5 and ZIP stream failure | not audited | not implemented | NOT_READY |
| HQ-MPSD English | PASS, CC BY 4.0 | FAIL: official MD5 and ZIP central directory failure | not audited | not implemented | NOT_READY |
| LlamaPartialSpoof | provenance known | audio not materialized | not audited | not implemented | NOT_READY |
| MIST | rights unresolved | not attempted | not audited | not implemented | NOT_READY |

## Transport result

Small official HQ-MPSD ranges are deterministic through the curl/Schannel
path: exact `206` responses, repeat SHA-256
`E6959E13EDDD5C7C3FBC6F20BD6DC364BA40B5AF48EA3C209A91127CC1B9828A`, and
adjacent-range concatenation pass. The synthetic independent-writer test
also passes. Large transfers nevertheless show incomplete reads, resets, and
corrupt full-size files; therefore transport is not authorized for blind
archive acceptance.

## Exact remaining blocker

No predeclared candidate currently satisfies the complete acceptance gate for
a second external distribution. The minimum recovery action is an official,
integrity-valid asset or an externally repaired official transport route,
followed by full audio/GT/identity/rights/adapter audit. Scientific outcomes,
W7 inference, metric changes, and protected Phase4.9R assets remain untouched.

```text
TRANSPORT_DIAGNOSTICS = PASS_FOR_SMALL_RANGES_AND_SYNTHETIC_WRITER
TOPCONF_TESTS = 96 passed
GIT_DIFF_CHECK = PASS
```
