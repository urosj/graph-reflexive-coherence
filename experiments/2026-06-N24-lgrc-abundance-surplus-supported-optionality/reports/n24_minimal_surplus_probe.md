# N24 Iteration 4 - Minimal Source-Current Surplus Probe

Status: `passed`

Acceptance state: `accepted_minimal_source_current_ab2_surplus_candidate_pending_optionality_replay_controls`

Output digest: `2898f018c650a9d3fe6b93f82a540ae67d8ce8947081573b1e581e6e99afe9a3`

## Summary

Iteration 4 runs the first positive N24 probe. It records source-current
LGRC9V3 maintenance-basin support/coherence above predeclared floors.
It does not claim optionality yet: the row is capped at AB2 pending I5
optional-continuation evidence and I6 replay/control validation.

## Geometric Interpretation

The surplus is geometric: it is computed from LGRC node coherence over the declared maintenance-basin node set, using the frozen min aggregation, before any optional branch is claimed.

The basin signature and topology are recorded from the runtime snapshot, and the flux/leakage surface is quiet because no optional branch has been opened yet.

False rejection flags for optional branch label-only and independent-run assembly controls mean those controls were not applicable before optionality was opened; they do not permit those relabel paths.

surplus_persistence_ratio=1.0 is a single-snapshot descriptive placeholder for the preserved surplus row, not replay-backed persistence evidence.

The source snapshot intentionally matches the N23 I4 pre-collapse fixture hash,
because both probes start from the same LGRC fixture state. N24 re-emits
that state as its own runtime artifact and does not consume the N23 snapshot
as surplus evidence.

```text
maintenance_basin_id = n24_i4_core_support_maintenance_basin
maintenance_node_ids = [0, 1, 5, 6, 7, 8, 9]
support_measurement_scope = maintenance_basin_node_set
support_aggregation_method = min
support_floor = 9.850000000000
coherence_floor = 9.850000000000
observed_min_support = 10.000000000000
observed_min_coherence = 10.000000000000
support_surplus_margin = 0.150000000000
coherence_surplus_margin = 0.150000000000
```

## Candidate Row

| Field | Value |
| --- | --- |
| Row | `n24_i4_row_01_minimal_source_current_surplus_probe` |
| Decision | `partial` |
| Provisional AB rung | `AB2` |
| Claim allowed | `false` |
| Derived report only | `false` |
| AP4 status | `not_applicable` |
| AP5 status | `not_applicable` |
| Artifact manifest entries | `7` |

## Gates

| Gate | Status |
| --- | --- |
| Support | `preserved` |
| Coherence | `preserved` |
| Boundary | `preserved` |
| Flux/leakage | `preserved` |
| Optionality | `not_run` |
| Replay | `not_run` |

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_ready` | `true` |
| `direct_n23_context_preserved` | `true` |
| `candidate_row_field_set_matches_i2_required_fields` | `true` |
| `derived_report_only_false` | `true` |
| `source_current_inputs_present` | `true` |
| `artifact_manifest_non_empty` | `true` |
| `support_surplus_margin_positive` | `true` |
| `coherence_surplus_margin_positive` | `true` |
| `maintenance_basin_signature_present` | `true` |
| `boundary_and_flux_preserved` | `true` |
| `optionality_not_claimed` | `true` |
| `ab2_only_pending_i5_i6` | `true` |
| `ap4_local_context_preserved_ap5_not_applicable` | `true` |
| `unsafe_claim_flags_all_false` | `true` |

## Claim Boundary

This supports only AB2 source-current surplus input evidence. AB3+ requires I5 optional continuation evidence, and AB4+ requires replay/control validation.
