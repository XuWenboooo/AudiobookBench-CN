# Open Science Manifest v1 (Protocol-Hardening Draft)

Status: **DRAFT / RELEASE CHECKLIST**

## Planned release contents

- [ ] Protocol and preregistration identifier
- [ ] Dataset cards, licenses, and split manifest
- [ ] Environment lockfile and hardware/software versions
- [ ] Source commit and configuration hashes
- [ ] Baseline implementations and provenance
- [ ] Complete run ledger, including failures and terminal no-parent cases
- [ ] Analysis scripts and exact metric definitions
- [ ] Redacted outputs sufficient for reproduction
- [ ] Limitations, deviations, and incident log

## Required per-run provenance

Record git commit, configuration, environment, hardware/software, seed,
dataset manifest and legally shareable hashes, model identity and checkpoint
hash, exact command, stdout/stderr, raw predictions, derived metrics,
bootstrap artifacts, failure ledger, and report. The release must classify
each artifact as `PUBLICLY_RELEASABLE`, `REPRODUCIBLE_WITH_EXTERNAL_DOWNLOAD`,
`LICENSE_RESTRICTED`, or `PRIVATE_NOT_RELEASABLE`; every `TBD_BEFORE_AUTHORIZATION`
entry blocks release approval.

## Privacy and safety gate

No release may expose restricted audio, personal data, held-out labels, credentials, or third-party material outside its license. Any redaction must be documented and must not selectively remove unfavorable outcomes.

## Reproducibility target

The final release should allow an independent reviewer to reconstruct inputs, code, configuration, execution order, and analysis without relying on undocumented local state.
