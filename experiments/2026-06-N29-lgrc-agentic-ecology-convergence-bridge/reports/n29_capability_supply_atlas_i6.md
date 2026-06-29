# N29 Iteration 6 - Capability Supply Atlas

## Summary

- status: `passed`
- acceptance_state: `accepted_capability_supply_atlas`
- capability supply rows: `26`
- direct prototype candidates: `18`
- coverage_debt_rows_opened: `false`
- demand_supply_matching_opened: `false`
- bridge_motifs_created: `false`
- prototype_rows_opened: `false`
- ready_for_iteration_7: `true`
- output_digest: `8b80dcc636f8d3333f6e344bbf33ffc12eebe256e7ce2e4f19db33573a6e7181`

Iteration 6 is supply-only. It indexes I3 capability cards by supplied
surface family and preserves native-readiness, producer residue,
naturalization debt, medium debt, source claim ceilings, and blocked
relabels. Direct prototype candidates are supply-side potential only;
no prototype rows or coverage matches are opened.

Source-of-truth rule: I3 cards are orientation indexes. Any I7+ coverage,
motif, prototype, or runtime claim must return to the original source
artifacts, closeouts, runtime records, source reports, or visual manifests
listed in the row manifest.

## Supply Families

| Family | Capability Count |
| --- | ---: |
| `trace_aftereffect` | 10 |
| `pressure_reserve_support` | 14 |
| `boundary_multi_basin_unit` | 14 |
| `closed_loop_perturbation_response` | 9 |
| `proxy_divergence_collapse` | 10 |
| `transfer_replay_relocation` | 4 |
| `formation_child_basin` | 14 |
| `medium_reshaping_generative_extractive` | 8 |
| `route_choice_arbitration` | 4 |
| `regulation_homeostasis` | 13 |
| `visual_or_report_only` | 0 |
| `control_only_or_negative` | 11 |

## Prototype Potential

| Status | Capability Count |
| --- | ---: |
| `blocked_by_claim_boundary` | 2 |
| `mapping_only_candidate` | 4 |
| `none` | 4 |
| `source_backed_reconstruction_candidate` | 16 |

## Readiness And Debt

| Normalized readiness status | Capability Count |
| --- | ---: |
| `artifact_level_only` | 0 |
| `blocked_by_missing_source` | 0 |
| `blocked_by_review_gate` | 2 |
| `bounded_runtime_surface` | 3 |
| `control_only` | 2 |
| `medium_debt` | 19 |
| `native_ready_surface` | 0 |
| `naturalization_debt` | 0 |
| `producer_mediated` | 0 |
| `visual_diagnostic_only` | 0 |

## Debt Ledgers

| Ledger | Row Count |
| --- | ---: |
| `producer_residue_ledger` | 26 |
| `medium_debt_ledger` | 26 |
| `naturalization_debt_ledger` | 26 |

## Recurring Supply Surfaces

| Kind | Top Entries |
| --- | --- |
| Geometry/dynamic | `delayed_coherence_pulse` (1), `return_cycle` (1), `oscillator_candidate` (1), `budgeted_replayable_circuit` (1), `route_candidate_commitment` (1), `runtime_visible_affordance_relation` (1) |
| Possible ecology demand | `naturalization_condition` (8), `pressure` (6), `parent_basin` (5), `co_response` (4), `producer_residue` (4), `role_susceptibility_division_of_labor` (4) |
| Blocked relabel | `agency` (5), `semantic_choice` (3), `intention` (3), `semantic_goal` (3), `Phase8_completion` (3), `choice` (2) |

## Checks

| Check | Passed |
| --- | --- |
| `i3_capability_atlas_passed` | `true` |
| `i4_bridge_schema_passed` | `true` |
| `i3_source_digest_matches` | `true` |
| `i6_phase_b_separation_rule_consumed` | `true` |
| `only_i3_and_i4_sources_consumed` | `true` |
| `uses_i3_as_index_not_full_evidence` | `true` |
| `capability_row_count_matches_i3` | `true` |
| `all_i4_capability_card_schema_fields_present` | `true` |
| `all_i6_row_extensions_are_namespaced` | `true` |
| `required_supply_groups_present` | `true` |
| `native_readiness_and_debt_preserved_row_locally` | `true` |
| `native_readiness_normalized_without_claim_upgrade` | `true` |
| `debt_ledgers_emitted` | `true` |
| `direct_prototype_candidates_identified_without_opening_rows` | `true` |
| `prototype_potential_is_not_prototype_evidence` | `true` |
| `source_artifacts_required_for_future_coverage_claims` | `true` |
| `original_source_artifacts_available_for_reconstruction_candidates` | `true` |
| `no_demand_supply_matching_or_coverage_rows_opened` | `true` |
| `coverage_status_assigned_false` | `true` |
| `no_bridge_motifs_created_or_claimed` | `true` |
| `positive_ecology_and_implementation_evidence_closed` | `true` |
| `claim_boundary_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
| `ready_for_iteration_7` | `true` |

## Interpretation

I6 supports a capability supply atlas, not coverage. It makes the N05-N28
supply side navigable for I7 by grouping supplied surfaces and preserving
row-local debt and claim ceilings. Any later source-backed coverage, motif,
or prototype claim must return to the original experiment artifacts named
inside each card.

Normalized readiness statuses are intentionally conservative. A row may
be a bounded runtime surface or source-backed reconstruction candidate
without becoming native ecology, native agency, or demand coverage.
