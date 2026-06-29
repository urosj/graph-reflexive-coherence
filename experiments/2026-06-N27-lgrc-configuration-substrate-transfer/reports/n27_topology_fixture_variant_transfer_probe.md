# N27 Iteration 4-A - Topology / Fixture Variant Transfer Probe

Status: `passed`

Acceptance state: `accepted_topology_fixture_variant_CT2_candidate_pending_replay_controls`

## Scope

Iteration 4-A adds a distinct source-current topology / fixture mapping
variant. It does not replace I4 and does not claim replay-backed transfer.

```text
positive_transfer_evidence_opened = true
provisional_ct_ladder_rung = CT2
ct_ladder_rung_assigned = false
ct_assignment_scope = variant_candidate_only_pending_replay_controls
i4_replaced = false
ct3_or_stronger_supported = false
ct5_or_stronger_supported = false
final_transfer_supported = false
```

## Candidate Row

| Row | Decision | Scope | Signature Margin | Boundary Margin | Support Margin | Coherence Margin | Flux Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `n27_i4a_row_01_topology_fixture_variant_transfer_probe` | `partial` | `topology` | `0.04` | `0.1` | `0.015` | `0.025` | `0.028` |

## Geometric Interpretation

I4-A maps a branched pre-frame fixture (`fixture_gamma_branch_frame`) to a
folded post-frame fixture (`fixture_delta_folded_frame`). Node ids, frame ids,
coordinate rules, and edge shape change. The row counts only because the
declared topological role mapping preserves the basin signature, maps all
boundary edges, keeps support/coherence above floor, keeps flux within bound,
and records an empty reconstruction ledger.

## Difference From I4

I4 is the minimal alpha/beta configuration-frame transfer: a three-node
core/support/boundary fixture is mapped into another three-node
core/support/boundary fixture. Its boundary mapping is admissible but exactly at
floor, with boundary margin `0.0`.

I4-A is not a replay of that row. It uses a different topology/fixture mapping:
a branched gamma fixture with two support arms and one outer boundary is mapped
into a folded delta fixture. Node ids, frame ids, coordinate rules, and edge
shape all change. The transfer-core digest differs from I4, and the boundary
margin is `0.1`.

So I4-A adds variant coverage: it shows that the CT2 transfer construction is
not confined to the original minimal alpha/beta frame. It still remains CT2
because replay, full controls, and stress/variant matrices are pending.

## Review Validation

I4-A consumes the current I4 artifact digest
`f98f5d56d15389fa6a8a3f138c6cccb30404bd7e9ef4c6a4badd7ef13be04294`. The
cross-substrate missing-mapping control is `not_applicable`, because I4-A is
topology-scope only and does not open a substrate-transfer claim.

This is additive variant evidence. It strengthens N27 beyond a single
alpha/beta fixture pair, but remains CT2 because replay, full controls, and
stress/variant matrices are still pending.

## Checks

| Check | Passed |
| --- | --- |
| `i4_ready_and_preserved` | `true` |
| `source_chain_digests_match` | `true` |
| `all_required_candidate_fields_present` | `true` |
| `ct2_artifact_roles_present` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `control_status_values_within_frozen_enum` | `true` |
| `transfer_core_digest_valid` | `true` |
| `variant_distinct_from_i4` | `true` |
| `mapping_declared_before_use_and_source_backed` | `true` |
| `source_current_not_report_only` | `true` |
| `same_basin_mapping_metrics_pass` | `true` |
| `support_coherence_flux_preserved` | `true` |
| `support_reconstruction_and_label_controls_cleared` | `true` |
| `transfer_not_same_frame_movement` | `true` |
| `replay_controls_defer_stronger_rungs` | `true` |
| `ap_gap_and_source_boundaries_preserved` | `true` |
| `predecessor_digest_fields_explicit` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I4-A supports one additional provisional CT2 topology/fixture transfer
candidate. It does not replace I4, does not widen I4's boundary edge, and does
not support CT3, CT4, CT5, final transfer, semantic identity, native support,
native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `5db5235c72e6954c5676be715cfdaa92cdc0e2d5746e5be40720e2152f5678f7`
