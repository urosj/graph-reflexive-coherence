# N27 Iteration 5-A - Artifact-Only Reconstruction Replay Probe

Status: `passed`

Acceptance state: `accepted_artifact_only_reconstruction_replay_hygiene_for_CT3_candidates_no_new_transfer`

## Scope

Iteration 5-A rebuilds the I4 and I4-A transfer cores from artifact files only.
It uses source manifests as artifact indexes and source digests as expected
comparison targets, but it does not trust candidate-row summary fields for the
reconstruction itself.

```text
provisional_ct_ladder_rung = CT3
ct3_replay_hygiene_supported = true
new_transfer_evidence_created = false
ct4_or_stronger_supported = false
ct5_or_stronger_supported = false
final_transfer_supported = false
```

## Reconstruction Rows

| Row | Source | Scope | Reconstructed Core | Source Core | Stable | Result |
| --- | --- | --- | --- | --- | --- | --- |
| `n27_i5a_row_i4_artifact_only_reconstruction` | `4` | `configuration` | `205a7848363076da87de0ff9713437504606769844c8eba9792f4a68e602afa4` | `205a7848363076da87de0ff9713437504606769844c8eba9792f4a68e602afa4` | `true` | `passed` |
| `n27_i5a_row_i4a_artifact_only_reconstruction` | `4-A` | `topology` | `e1c4dc4d6dbc9bcd99c2d347ff05a955cf69dab07a933ad2fb20c890bcf602a9` | `e1c4dc4d6dbc9bcd99c2d347ff05a955cf69dab07a933ad2fb20c890bcf602a9` | `true` | `passed` |

## Interpretation

I5 showed replay-backed CT3 candidate evidence. I5-A asks a narrower audit
question: can the same transfer cores be reconstructed from the emitted
artifact files alone? Both rows pass. This strengthens replay hygiene by
showing the transfer core is not merely a row-body assertion.

I5-A does not create a new transfer geometry, does not add a new mapping
variant, and does not provide stress or full-control evidence. It remains CT3
hygiene support pending I6 stress and later classification.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match` | `true` |
| `i5_replay_matrix_passed` | `true` |
| `two_artifact_only_reconstruction_rows_present` | `true` |
| `source_row_body_not_used_for_reconstruction` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `reconstructed_transfer_core_matches_source_and_i5` | `true` |
| `artifact_only_reconstruction_digest_stable` | `true` |
| `mapping_order_reconstructed` | `true` |
| `same_basin_metrics_reconstructed_cleanly` | `true` |
| `support_reconstruction_absent` | `true` |
| `no_new_transfer_evidence_created` | `true` |
| `ct4_ct5_final_remain_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Claim Boundary

No final transfer, semantic identity, native support, native AP5, AP5 NAT4-gap
resolution, Phase 8, or ant ecology claim is opened.

Output digest: `5cba66c4ac1d1c855fc830ac1bbe274e209a08aef8faf884f1b1576512b6de36`
