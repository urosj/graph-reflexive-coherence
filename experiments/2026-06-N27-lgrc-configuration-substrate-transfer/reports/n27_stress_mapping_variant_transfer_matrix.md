# N27 Iteration 6 - Stress / Mapping-Variant Transfer Matrix

Status: `passed`

Acceptance state: `accepted_stress_mapping_variant_candidate_pending_i7_controls_no_final_transfer`

## Scope

Iteration 6 stress-tests the two replay-backed CT3 candidates. It exposes the
I4 boundary-at-floor limitation and tests whether I4-A's distinct topology
fixture has enough positive margin to survive the declared stress envelope.

```text
ct5_stress_variant_candidate_supported = true
ct5_assignment_allowed = false
ct5_assignment_blocker = full_control_trace_pending_iteration_7
ct5_or_stronger_supported = false
final_transfer_supported = false
```

## Stress Rows

| Row | Source | Scope | Decision | Stress Candidate | Failed Stress Rows |
| --- | --- | --- | --- | --- | --- |
| `n27_i6_row_i4_stress_mapping_variant` | `4` | `configuration` | `partial` | `false` | `boundary_tightening_0_05, combined_moderate_mapping_stress` |
| `n27_i6_row_i4a_stress_mapping_variant` | `4-A` | `topology` | `supported` | `true` | `none` |

## Geometric Interpretation

I6 keeps the two mapping families separate. The I4 alpha/beta row remains a
valid replay-backed CT3 candidate, but its boundary margin was already exactly
at floor, so a boundary-tightening stress row fails closed. This does not
invalidate I4; it records the narrowness of that transfer surface.

The I4-A gamma/delta topology fixture row has positive boundary, support,
coherence, and flux margins. It survives the declared bounded stress envelope,
so it becomes stress/variant candidate evidence. The result still does not
assign CT5 because the frozen CT5 role also requires a full control trace,
which is I7 scope.

## I7 Handoff

I7 must consume I6 asymmetrically. The I4 alpha/beta row remains
replay-backed CT3 evidence, but it is stress-limited and does not contribute
to CT5. The I4-A gamma/delta row is CT5-candidate evidence only: CT5
assignment remains blocked until the full I7 control matrix, AP4/AP5
dependency checks, and claim classification pass with no failed-open controls.

The I6 control trace is only a stress-control trace. It is not the full I7
control matrix.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match` | `true` |
| `i5_and_i5a_ready_for_stress` | `true` |
| `stress_rows_cover_i4_and_i4a_separately` | `true` |
| `stress_policy_declared_before_use` | `true` |
| `i4_boundary_at_floor_exposed` | `true` |
| `i4a_passes_declared_stress_envelope` | `true` |
| `stress_variant_evidence_does_not_create_new_transfer` | `true` |
| `stress_artifact_sha256_match_file_contents` | `true` |
| `ct5_assignment_deferred_until_i7_controls` | `true` |
| `final_transfer_remains_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I6 strengthens N27 by showing that the distinct topology/fixture variant can
survive bounded stress, while the minimal I4 row is correctly classified as
stress-limited at its boundary edge. This is stress/variant candidate evidence
pending I7 controls. It is not final transfer, semantic identity, native
support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `3335a4a6017a96b6d71c6e1f386bb2d17669208f8d8daf9b7a25a49755e7324a`
