# Prefreeze Integration Plan v1

Status: **STATIC PLAN / NO CHERRY-PICK EXECUTED / NON-AUTHORIZING**.

| Commit | Purpose / files | Safe integration assessment | Method / likely conflict |
|---|---|---|---|
| `ebad271` | context audit and novelty docs | documentation only | copy/reconcile citations; conflict with later related-work edits |
| `5d24f89` | population, GT, failure, metrics, Whether, mechanism/transformation docs | partial carry | reconcile candidate wording and replace prose gates with schema |
| `ae2a702` | synthetic statistics script/test/report | optional background | retain test; do not treat report as power or endpoint decision |
| `4a66e66` | generic assurance validator/test | integrate with edits | extend rather than duplicate validator; preserve old API |
| `5ec945c` | environment templates and handoff | partial carry | reconcile Phase3R→Phase3T and current host/lock state |
| `82e6fd2` | frozen hash ledger | provenance only | verify hash, do not rewrite frozen ledger |

If human reconciliation later chooses integration, fetch both tips, verify the
frozen hash ledger, compare path-by-path against committed mainline, then make
new reviewed commits. Do not cherry-pick blindly, merge automatically, or
modify `topconf-rq1-prefreeze`.
