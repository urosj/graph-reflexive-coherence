# N25 Iteration 6 - Producer-Assisted Flux-Conditioned Formation Probe

Status: `passed`
Acceptance state: `accepted_producer_assisted_flux_conditioned_bf4_scaffold_candidate_native_bf_unchanged`
Output digest: `84dec8a317b7cf6abeb328b28c4ef1d58f9d52d5b8ae69caf0b0944b33959780`

## Scope

I6 opens the producer-assisted lane only. It consumes N24 I7-C as a
declared flux-conditioning scaffold and keeps the native I5 BF4 ceiling
unchanged.

## Result

```text
producer_assisted_lane_opened = true
producer_assisted_bf4_candidate_supported = true
producer_assisted_bf5_supported = false
native_bf_ceiling_preserved = BF4_native_replay_control_backed_sub_basin_differentiation_candidate
native_lane_failure_overwritten = false
missing_native_mechanism_probe_supported = true
basin_formation_claim_allowed = false
```

## Geometric Interpretation

Geometrically, I6 keeps the I5 spark-to-expansion sub-basin trace as the native object: the module boundary, old-center replacement, and replay-stable zero-margin support/coherence surface are unchanged. The added producer is not a new basin generator. It is a flux windowing surface that lets larger attempted flux arrive as multiple source-visible windows, each still capped at the native 1e-9 bound. That identifies the missing native mechanism: LGRC would need its own flux routing or rate-limiting surface before this producer lane could become native BF stress evidence.

The end result is a producer-mediated flux scaffold candidate, not a
native BF upgrade. I6 makes the missing native mechanism explicit:
`native_flux_routing_or_rate_limiting_surface`.

## Producer Ledger

- Producer result class: `producer_mediated_scaffold_candidate`
- Producer flux window bound: `1e-08`
- Per-window native bound: `1e-09`
- Window count bound: `10`
- Native flux debt overwritten: `false`

## Controls

- `producer_schedule_post_hoc_control`: `passed`; producer-assisted lane remains admissible only as declared scaffold
- `producer_hidden_support_control`: `passed`; hidden support remains blocked
- `producer_threshold_relaxation_control`: `passed`; threshold relaxation blocked
- `producer_basin_insertion_without_trace_control`: `passed`; producer insertion without source-current formation trace blocked
- `producer_success_as_native_relabel_control`: `passed`; producer success cannot upgrade native BF
- `producer_success_overwrites_native_failure_control`: `passed`; native debt remains visible for I7 comparison
- `producer_assisted_success_does_not_overwrite_native_failure`: `passed`; native and producer-assisted lanes remain separated
- `native_flux_debt_remains_row_local`: `passed`; native flux debt remains row-local under producer lane
- `n24_optionality_relabel_as_formation_rejected`: `passed`; N24 remains context/scaffold only
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `semantic_choice_relabel_rejected`: `passed`; semantic choice relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked
- `ant_ecology_relabel_rejected`: `passed`; ant ecology relabel blocked

## Checks

- PASS: `i1_inventory_passed`
- PASS: `i2_schema_passed`
- PASS: `i3_active_nulls_passed`
- PASS: `i4_native_probe_passed`
- PASS: `i5_native_matrix_passed`
- PASS: `n24_i7c_producer_contract_passed`
- PASS: `producer_contract_declared_before_use`
- PASS: `thresholds_and_floors_unchanged`
- PASS: `producer_adds_no_support_or_coherence`
- PASS: `producer_window_bound_recorded`
- PASS: `native_bf_ceiling_not_upgraded`
- PASS: `producer_controls_clean`
- PASS: `artifact_manifest_valid`
- PASS: `source_current_inputs_non_circular`
- PASS: `unsafe_claim_flags_false`
