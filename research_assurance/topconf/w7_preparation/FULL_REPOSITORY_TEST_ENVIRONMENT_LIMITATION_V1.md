# Full Repository Test Environment Limitation v1

Status: evidence record for this isolated preparation worktree

## A. Preparation package

The preparation tests and new identity/transform tests run without W7 data,
checkpoints or downloader state. They are the scoped regression gate for this
branch.

## B. TopConf scoped tests

`tests/topconf` passed in full after the preparation changes. The scoped count
is recorded in the final report. The static pre-registration checker also
passes all state, protocol, ledger and PartialSpoof firewall checks.

## C. Full repository suite

The isolated worktree full-suite rerun completed with `315 passed, 137 failed,
3 errors`. This is not reported as an all-benign result. The failures are
classified from representative tracebacks and test-name groups as follows:

| Class | Representative evidence | Dependency/asset cause |
|---|---|---|
| Missing historical Week 1/Day 6C artifacts | `test_week1_required_artifacts_exist`; `test_c0_cross_split_leakage_zero` | ignored `results/week1/**` and `data/manifests/day6c_same_speaker_control_manifest.csv` are not present in the managed worktree |
| Missing Week 3/4 evidence and authorization artifacts | `test_original_score_commitments_are_exactly_23`; Week 3/4 formal/security groups | ignored historical score manifests, closure artifacts and authorization evidence are absent |
| Missing local pretrained backend | three `test_day6b_speaker.py` errors | `pretrained/spkrec-ecapa-voxceleb` is absent; the traceback explicitly requests Day 6B model setup |
| Dependent legacy readiness/portability tests | Day 8 A2, portability, Day 6C controls | they require the same ignored manifests, generated audio or prior frozen outputs |

The full-suite failures are outside the new preparation package: no failing
test name belongs to the new preparation tests, and the complete `tests/topconf`
scope remains green. The absence of these ignored assets is therefore an
environment limitation for full-repository reproduction, not evidence that
the preparation changes passed every historical dependency. No asset was
copied into this branch to manufacture a green result.

No active downloader, archive, `.part` file, checkpoint or real W7 sample was
read or modified for this record.
