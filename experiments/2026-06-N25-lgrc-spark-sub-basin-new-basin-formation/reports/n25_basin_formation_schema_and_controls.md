# N25 Iteration 2 - Basin-Formation Schema And Controls

Status: `passed`
Acceptance state: `accepted_basin_formation_schema_controls_frozen_no_positive_evidence`
Output digest: `eef875053c66bc84f0df7b4c3d206d8f342be0e473c9730f328fcc488c9a72ce`

## Frozen Schema

- Candidate rows require explicit native or producer-assisted lane.
- Row-level lane ceilings prevent producer-assisted success from upgrading native BF or N24 native C6.
- Formation class and formation source are closed enums.
- Native rows must preserve `native_flux_debt_bound = 1e-9` and `native_flux_debt_widened = false`.
- Producer-assisted rows cap conditioned flux at `1e-8` across at most 10 windows.
- Active-null controls expect `failed_closed`; positive candidate controls expect blocker absence as `passed`.
- Candidate rows must carry source digests, artifact path/SHA equality, temporal windows, and basin signature digests.
- Artifact manifests must use formation-specific roles, not generic runtime traces.

## Ladders

- `BF0`: no source-current basin-formation evidence
- `BF1`: run artifact with becoming-pressure / N24 optionality context
- `BF2`: bifurcation or spark trace observed, but distinguishable basin not yet stable
- `BF3`: source-current distinguishable sub-basin boundary/support candidate
- `BF4`: replay/control-backed sub-basin differentiation candidate
- `BF5`: stress/threshold-backed new-basin formation candidate with merge/leakage controls clean
- `BF6`: N26-ready bounded basin-formation evidence

## Checks

- PASS: `i1_inventory_passed`
- PASS: `candidate_schema_has_all_required_fields`
- PASS: `lane_enum_frozen`
- PASS: `lane_ceilings_frozen`
- PASS: `formation_class_and_source_frozen`
- PASS: `distinguishability_metrics_required`
- PASS: `native_flux_debt_policy_frozen`
- PASS: `producer_flux_bounds_frozen`
- PASS: `artifact_roles_frozen`
- PASS: `control_status_semantics_frozen`
- PASS: `i1_i2_control_alias_map_frozen`
- PASS: `lane_cross_field_invariants_frozen`
- PASS: `temporal_window_fields_required`
- PASS: `basin_signature_digests_required`
- PASS: `producer_controls_frozen`
- PASS: `no_positive_n25_evidence_opened`

## Result

```text
failed_checks = []
basin_formation_evidence_opened = false
ready_for_iteration_3_active_nulls = true
```
