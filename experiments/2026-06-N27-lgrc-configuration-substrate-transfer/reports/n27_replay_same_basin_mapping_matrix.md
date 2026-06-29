# N27 Iteration 5 - Replay And Same-Basin Mapping Matrix

Status: `passed`

Acceptance state: `accepted_replay_same_basin_mapping_matrix_CT3_candidates_pending_controls_stress`

## Scope

Iteration 5 replays the two existing CT2 candidates: I4 minimal
configuration-frame transfer and I4-A topology/fixture variant transfer. It
does not introduce a new mapping family and does not claim final transfer.

```text
provisional_ct_ladder_rung = CT3
ct3_replay_candidate_supported = true
ct4_or_stronger_supported = false
ct5_or_stronger_supported = false
final_transfer_supported = false
```

## Matrix Summary

```text
candidate_count = 2
replay_pass_count = 2
replay_fail_count = 0
ct3_candidate_count = 2
```

## Replay Rows

| Row | Source | Scope | Artifact | Snapshot | Duplicate | Mapping Order | CT Rung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `n27_i5_row_i4_same_basin_mapping_replay` | `4` | `configuration` | `passed` | `passed` | `passed` | `passed` | `CT3` |
| `n27_i5_row_i4a_same_basin_mapping_replay` | `4-A` | `topology` | `passed` | `passed` | `passed` | `passed` | `CT3` |

## Geometric Interpretation

I5 asks whether the I4 and I4-A basin-transfer traces remain the same after
replay. For each row, replay reconstructs the artifact manifest, reloads the
transfer core and pre/post signature digests, checks that the declared mapping
still precedes pre/post observations, and verifies that duplicate replay is
idempotent rather than creating a second positive transfer row.

Duplicate replay uses the explicit semantics:

```text
duplicate_replay_first_emitted = true
duplicate_replay_second_emitted = false
duplicate_replay_digest_stable = true
```

Here `second_emitted = false` means duplicate suppression worked. The second
replay validated the same digest without creating another positive row.

The result is CT3 because the same-basin transfer records are replay-backed.
It is not CT4 or CT5: fail-closed controls and stress/variant testing remain
later iterations.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match` | `true` |
| `i4_and_i4a_ready_for_replay` | `true` |
| `two_ct2_candidates_consumed` | `true` |
| `required_ct3_replay_modes_pass` | `true` |
| `duplicate_replay_stable_without_duplicate_positive_rows` | `true` |
| `mapping_order_replay_preserves_declared_order` | `true` |
| `same_basin_mapping_replay_preserves_required_metrics` | `true` |
| `replay_validates_source_records_without_creating_transfer_evidence` | `true` |
| `support_reconstruction_absent_and_not_counted` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `ct3_artifact_roles_present` | `true` |
| `control_status_values_within_frozen_enum` | `true` |
| `replay_failure_control_passed_for_ct3` | `true` |
| `stress_and_final_transfer_remain_blocked` | `true` |
| `ap_gap_and_source_boundaries_preserved` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I5 supports two provisional CT3 replay-backed same-basin transfer candidates:
the original I4 alpha/beta minimal configuration transfer and the I4-A
gamma/delta topology fixture variant. This strengthens N27 from source-current
CT2 existence to replay-backed CT3 evidence, but it still does not support
control-backed CT4, stress-backed CT5, final transfer, semantic identity,
native support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `de0f5f7dc0f3cd1482569465198473940faa52275943ab7af1333a5c88bcf7c6`
