# Week3 Clean Rerun Authorization and Namespace Verification

## Independent verification verdict

`CLEAN_RERUN_NAMESPACE_VERIFIED = YES`

The future formal path uses the canonical authorization location
`results/week3_stage_a_f5_runs/authorization.json` and derives its clean
output namespace from a validated `run_id`.  The historical namespace is
rejected, arbitrary output paths cannot override the authorized namespace,
cross-run evaluator inputs are rejected, and formal accounting remains scoped
to the authorization run identity.

## Authorization-contract verification

The canonical authorization schema is actively validated by
`validate_authorization_artifact`.  It requires and fixes:

- `prior_results_observed = true`
- `scientific_parameters_changed_after_observation = false`
- `rerun_classification = INTEGRITY_REEXECUTION_OF_FROZEN_PROTOCOL`

The validator returns these verified values to the formal pipeline, which
asserts them before formal generation or evaluation.  Schema validation and
canonical-evidence hash validation fail closed.

`HISTORICAL_SCIENTIFIC_COPY_FORWARD_PROHIBITED = true`

The future clean run must not copy or reuse historical waveforms, sidecars,
attempt rows, final accounting, score timelines, H1 results, H2 results, H3
results, bootstrap results, scientific JSON, or the historical scientific hash
manifest.  The authorization may reference forensic-report identity/hash,
scientific-adjudication identity/hash, historical-run disclosure metadata, and
frozen protocol inputs; historical scientific values are not inputs to the new
run or its analysis.

Frozen protocol inputs remain distinct from historical scientific outputs.
The 23 cases, source/reference files, seed map, F5 source/assets, frozen
configuration, B1b/S2 definitions, GT definitions, H1/H2/H3 definitions, and
bootstrap contract may be reused as protocol inputs.

## State at verification

No active future authorization exists, no clean run namespace exists, and no
clean F5 generation, B1b/S2 scoring, H1/H2/H3 evaluation, or bootstrap was
executed.  The historical run remains forensic-only.  This verification is
engineering-integrity evidence only and does not authorize scientific work.

## Source hashes reviewed

| binding | SHA-256 |
|---|---|
| authorization schema | `73BDE6A0EBFA418A1DC30F300C5D6CFF23D956079E7B0903D190D5AB1096DA8B` |
| authorization validator | `F8BC2BD538F67419640114952F5E2E4F70E05F47860EC41A39C0F49D6859A5D5` |
| formal pipeline | `D95F23AAEEF5DEDD5B1B05C6F09D1C98C19E97C47F8C50FB8344D5C2C122F521` |
| formal runner | `8D8529141BF6D79D75B0F314254E63F5B6560D347C93A88B6E444D5559C71B1D` |
| formal evaluator | `D9AB4C3D23A3548DD871A73E653FD59F148FBF2749896ABA9562FEDE6863FD40` |
| frozen config | `155FDE15647669BFEEDBAAD4913ADEFDAE9F7153C50D9B0246EAB0F4D16DB87D` |
| environment manifest | `E75FD44A139931B057243C1AFF58A564AC3D1EFD77B051457C91ED8477464604` |
| 23-case table | `E3B7044631D223B893A4EDA306236679EFDFCF38B91DED2101D1C7D0EA2CD4F8` |
| seed amendment | `89417408D18D7C529DC5B5F70A3B28CD57C8111245AC98E633B27C35DEBE3E63` |
| F5 source identity | `E0D123D6A53BF2BB02A598367E4B9240EC42BF328E6820EC5AE8F0FBC369665D` |
| F5 local source manifest | `598BBC66E471B80D41C55F677C5F01C1BF6A81E37EC7FC23E62D013F3F60310E` |
