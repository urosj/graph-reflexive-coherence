# N27 Iteration 4 - Minimal Configuration Transfer Probe

Status: `passed`

Acceptance state: `accepted_minimal_source_current_CT2_candidate_pending_replay_controls`

## Scope

Iteration 4 opens the first positive source-current N27 row. It tests a minimal
configuration transfer from `fixture_alpha_frame` to `fixture_beta_frame` under
a mapping declared before post-transfer observation.

```text
positive_transfer_evidence_opened = true
provisional_ct_ladder_rung = CT2
ct_ladder_rung_assigned = false
ct_assignment_scope = provisional_candidate_only_pending_replay_controls
ct3_or_stronger_supported = false
final_transfer_supported = false
```

## Candidate Row

| Row | Decision | Provisional Rung | Signature Margin | Support Margin | Coherence Margin | Flux Margin |
| --- | --- | --- | --- | --- | --- | --- |
| `n27_i4_row_01_minimal_configuration_transfer_probe` | `partial` | `CT2` | `0.035` | `0.01` | `0.02` | `0.025` |

## Geometric Interpretation

The source-current trace uses distinct pre/post frames and node ids, so it is
not same-frame basin movement. The row succeeds only because a declared mapping
links the pre-transfer basin signature to a post-transfer signature with a
mapped boundary, preserved support/coherence floors, bounded flux imbalance,
and an empty support-reconstruction ledger.

The boundary result is equality-at-floor rather than positive slack:
`boundary_mapping_margin = 0.0` with
`boundary_acceptance_operator = greater_than_or_equal`. This is admissible for
CT2, but I6 must treat it as a narrow boundary edge when stress-testing the
mapping. Replay and stress controls use the frozen status enum
`not_applicable` in I4, with CT2-specific deferral recorded in the applicability
reason.

This is a bounded CT2 candidate. It is not replay-backed CT3, not
control-backed CT4, not stress-backed CT5, and not final N27 transfer closeout.

## Checks

| Check | Passed |
| --- | --- |
| `i3_ready_for_i4` | `true` |
| `source_chain_digests_match` | `true` |
| `all_required_candidate_fields_present` | `true` |
| `ct2_artifact_roles_present` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `control_status_values_within_frozen_enum` | `true` |
| `transfer_core_digest_valid` | `true` |
| `mapping_declared_before_use_and_source_backed` | `true` |
| `source_current_not_report_only` | `true` |
| `same_basin_mapping_metrics_pass` | `true` |
| `boundary_floor_equality_explicitly_allowed` | `true` |
| `support_coherence_flux_preserved` | `true` |
| `support_reconstruction_and_label_controls_cleared` | `true` |
| `transfer_not_same_frame_movement` | `true` |
| `replay_controls_defer_stronger_rungs` | `true` |
| `ap_gap_and_source_boundaries_preserved` | `true` |
| `predecessor_digest_fields_explicit` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I4 supports a provisional source-current configuration-transfer candidate at
CT2 scope. I5 still needs to replay the transfer core and prove that the same
basin mapping survives artifact, snapshot/load, duplicate, and mapping-order
replay. I4 does not support semantic identity, native support, native AP5, AP5
NAT4-gap resolution, Phase 8, ant ecology, or final transfer.

Output digest: `f98f5d56d15389fa6a8a3f138c6cccb30404bd7e9ef4c6a4badd7ef13be04294`
