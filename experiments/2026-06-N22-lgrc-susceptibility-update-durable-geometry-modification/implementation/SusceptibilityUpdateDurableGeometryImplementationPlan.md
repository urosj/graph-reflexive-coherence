# N22 Susceptibility Update And Durable Geometry Implementation Plan

## Goal

N22 tests whether prior interaction can durably alter later LGRC geometry in a
source-current, replayable, claim-clean way.

The experiment should support only:

```text
bounded artifact-level susceptibility-update / durable geometry modification
candidate
```

It must not support:

```text
semantic learning
semantic choice
intention
agency
free will
selfhood
identity acceptance
native support
sentience
Phase 8 implementation
ant ecology implementation
```

## Source Rules

N22 must consume the N20 I5 contract row:

```text
source_contract_row = n20_i5_row_03_susceptibility_update
```

N22 must consume N21 closeout only as prerequisite context:

```text
N21 withdrawal_resistance_ladder_rung = WR6
N21 naturalization_depth_ladder_rung = ND5
N21 n21_closeout_ladder_rung = N21-C6
N21 ready_for_n22 = true
```

N21 cannot supply susceptibility-update evidence. N22 must produce new
source-backed durable geometry deltas.

N19 may be consumed only as AP-gap boundary context:

```text
n19_native_readiness_boundary_consumption =
  ap_gap_boundary_only
```

N19 must not be consumed as susceptibility-update evidence, durable geometry
delta evidence, or an SU ladder assignment source.

When N22 mirrors N20 source statuses, inherited fields must be explicitly
prefixed:

```text
n20_source_downstream_consumption_status
```

This prevents N20's `contract_complete_pending_iteration6_closeout` status from
being confused with N22 Iteration 6 transfer/re-entry.

## N21 ND6 Bridge Rule

N22 does not reopen N21 and does not claim to perform N21 `ND6` directly.
N21 remains closed at bounded local `ND5`. N22 tests the missing source-backed
condition that blocked a stronger naturalization-depth closeout: durable
geometry modification / susceptibility update.

N22 closeout must record:

```text
n21_nd6_bridge_status =
  not_supported |
  bridge_candidate_supported |
  blocked_by_replay |
  blocked_by_controls |
  blocked_by_AP_gap |
  blocked_by_producer_residue
```

The bridge status may be `bridge_candidate_supported` only if N22 reaches
`SU5` or `SU6` cleanly with source-backed durable susceptibility delta
evidence, replay/re-entry support, peer/same-budget comparison where required,
and AP/claim controls intact. The bridge record is not general naturalization
depth and cannot retroactively upgrade N21 evidence.

## Required Evidence Fields

Every candidate evidence row must record:

```text
row_id
source_contract_row
source_contract_row_digest
source_output_digest
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_current_inputs
row_specific_thresholds_declared_before_use
n19_native_readiness_boundary_consumption
n20_source_downstream_consumption_status
interaction_window
reentry_window
pre_interaction_geometry_trace
post_interaction_geometry_trace
susceptibility_delta_trace
route_or_region_reentry_trace
same_basin_continuation_rule
allowed_delta_fields
same_basin_invariant_fields
out_of_scope_drift_blocks_row
delta_not_label_reassignment
route_or_region_conditioned
peer_same_budget_comparison
peer_same_budget_comparison_scope_reason
peer_route_or_region_trace
historical_interaction_provenance_present
active_reinforcement_schedule_disabled
active_reinforcement_queue_empty
reinforcement_budget_in_flight
reinforcement_schedule_not_used_as_evidence
support_floor_result
coherence_floor_result
boundary_integrity_result
flux_or_leakage_result
replay_result
control_results
ap4_dependency_status
ap5_dependency_status
ap4_condition_reason
ap5_condition_reason
interaction_delta_digest
post_replay_delta_digest
reentry_delta_digest
delta_persistence_ratio
delta_threshold_or_rule
one_window_transient_rejected
global_drift_rejected
producer_residue_fields
naturalization_debt_fields
blocked_relabel_fields
claim_ceiling
unsafe_claim_flags
row_decision
susceptibility_update_claim_allowed
derived_report_only
artifact_manifest
artifact_paths
artifact_sha256
all_artifact_sha256_match_file_contents
output_digest
```

## Local Ladder

```text
SU0 = no source-current susceptibility evidence
SU1 = interaction run present
SU2 = source-current pre/post geometry delta observed
SU3 = replay-backed susceptibility update candidate
SU4 = control-backed durable geometry modification candidate
SU5 = transfer/re-entry-backed susceptibility update candidate
SU6 = N23-ready bounded durable geometry modification evidence
```

Rows below `SU3` cannot support durable geometry modification. `SU6` is a
handoff rung, not an agency claim.

## Closeout Ladder

N22 must also use a tranche-level closeout ladder:

```text
N22-C0 = contract-only closeout
  N20/N21 handoff consumed, but no N22 susceptibility evidence opened.

N22-C1 = active-null/control discipline established
  Active nulls and failure baselines fail closed, but no positive SU row.

N22-C2 = susceptibility partial
  Interaction or delta evidence appears, but replay, re-entry, controls, or AP
  gaps block stronger support.

N22-C3 = replay-backed susceptibility candidate
  SU3 reached on at least one source-backed row.

N22-C4 = durable geometry modification candidate
  SU4 reached after replay and fail-closed controls.

N22-C5 = transfer/re-entry-backed susceptibility candidate
  SU5 reached with later route/region re-entry or transfer evidence.

N22-C6 = N23-ready bounded durable geometry evidence
  SU5/SU6 evidence plus producer residue, naturalization debt, AP4/AP5
  discipline, unsafe-claim blockers, src_diff_empty, and N23 handoff.
```

The closeout ladder classifies the whole N22 tranche. It must not convert an
SU row into semantic learning, choice, agency, native support, sentience, or a
Phase 8 claim.

## Schema Policies To Freeze

Iteration 2 must freeze how geometry may change while same-basin continuation
remains bounded:

```text
allowed_delta_fields = source-current fields that may change and count as
  susceptibility evidence
same_basin_invariant_fields = basin signature fields that must remain stable
out_of_scope_drift_blocks_row = true
delta_not_label_reassignment = true
```

Rows with large topology, boundary, support, or identity drift outside the
declared allowed fields must be blocked rather than interpreted as successful
susceptibility update.

Route- or region-conditioned susceptibility rows must include a peer/same-budget
comparison:

```text
target route or region receives prior interaction
peer route or region receives same budget but not the same prior interaction
later re-entry differs only in the target route or region
```

If the same delta appears globally, or appears equally in the peer route or
region, the row is not route-conditioned susceptibility evidence.

Peer comparison may be `not_applicable` only for a non-route-conditioned `SU2`
row, and only with:

```text
peer_same_budget_comparison_scope_reason = non_route_conditioned_SU2_only
```

For `SU5`, `SU6`, `N22-C5`, and `N22-C6`, missing peer comparison blocks the
claim.

N22 must distinguish historical interaction provenance from active producer
reinforcement. Later rows may require prior interaction to exist historically,
but active reinforcement cannot carry the durable delta:

```text
historical_interaction_provenance_present = true
active_reinforcement_schedule_disabled = true
active_reinforcement_queue_empty = true
reinforcement_budget_in_flight = 0.0
reinforcement_schedule_not_used_as_evidence = true
```

If active reinforcement remains, the row may still be useful producer-residue
evidence, but it cannot support source-current durable geometry modification.

Active reinforcement remaining has a fixed rung effect:

```text
SU1/SU2 = descriptive only if source-current traces exist
SU3 = replay-limited only if replay is not reinforcement-carried
SU4/SU5/SU6 = blocked
N22-C4/N22-C5/N22-C6 = blocked
n21_nd6_bridge_status = blocked_by_producer_residue
```

Support/coherence/boundary/flux changes are field-specific. A changed status is
accepted only if the declared floor or bound remains preserved:

```text
support_floor_result = preserved | changed_within_allowed_delta_above_floor
coherence_floor_result = preserved | changed_within_allowed_delta_above_floor
boundary_integrity_result = preserved | changed_within_allowed_delta
flux_or_leakage_result = preserved | changed_within_bound
```

AP dependency statuses are closed enums:

```text
ap4_dependency_status =
  required_recorded |
  not_applicable |
  missing_blocks_row

ap5_dependency_status =
  conditional_required_recorded |
  not_applicable |
  missing_blocks_row
```

Each candidate row must record `ap4_condition_reason` and
`ap5_condition_reason`.

Durability must be measured, not only labeled:

```text
interaction_delta_digest
post_replay_delta_digest
reentry_delta_digest
delta_persistence_ratio
delta_threshold_or_rule
one_window_transient_rejected = true
global_drift_rejected = true
peer_same_budget_comparison_required_if_route_or_region_conditioned = true
```

The persistence rule must be declared before use. A positive row requires a
declared persistence floor, replay-window survival, later re-entry survival,
one-window transient rejection, and global-drift rejection.

Every positive row must record an artifact manifest:

```text
artifact_manifest = [
  { path, sha256, artifact_role }
]
all_artifact_sha256_match_file_contents = true
```

Replay names must use canonical names. `artifact_only_replay` is accepted only
as an alias for `artifact_replay`.

Iteration 3 must include AP-gap active nulls:

```text
route_conditioned_row_missing_AP4 -> failed_closed
proxy_or_target_conditioned_row_missing_AP5 -> failed_closed
AP_gap_prose_only -> failed_closed
```

## Iteration Plan

### Iteration 1. Source Handoff Inventory

Inventory N20 I5 susceptibility-update contract, N21 closeout, N19 AP4/AP5
gap status, and the N20-N29 roadmap/handoff. No susceptibility evidence is
opened.

Expected artifacts:

```text
outputs/n22_source_handoff_inventory.json
reports/n22_source_handoff_inventory.md
scripts/build_n22_source_handoff_inventory.py
```

### Iteration 2. Schema, Ladder, And Control Freeze

Freeze source-current fields, run-artifact admissibility, N19 boundary-only
consumption, N20-prefixed inherited source status, local SU ladder, N22-C
closeout ladder, AP4/AP5 dependency rules, replay requirements, row decisions,
allowed drift versus same-basin invariants, historical interaction versus
active reinforcement, peer/same-budget comparison, durability metrics, N21 ND6
bridge status, and claim boundary.

Expected artifacts:

```text
outputs/n22_susceptibility_schema_and_controls.json
reports/n22_susceptibility_schema_and_controls.md
scripts/build_n22_susceptibility_schema_and_controls.py
```

### Iteration 3. Active Nulls And Failure Baselines

Show that label-only route changes, producer schedule changes, one-window flux
transients, no-reentry rows, post-hoc deltas, hidden reinforcement, AP-gap
omissions, AP-gap prose-only handling, and semantic learning relabels fail
closed.

Expected artifacts:

```text
outputs/n22_active_nulls_and_failure_baselines.json
reports/n22_active_nulls_and_failure_baselines.md
scripts/build_n22_active_nulls_and_failure_baselines.py
```

### Iteration 4. Minimal Susceptibility Update Probe

Run the first source-backed pre-interaction -> interaction -> post-interaction
-> later re-entry probe with row-specific thresholds declared before use and
source-current inputs recorded. Include a same-budget peer/null route when
route or region conditioning is claimed. Target `SU2` or provisional `SU3`,
not final N22 closeout.

Expected artifacts:

```text
outputs/n22_minimal_susceptibility_update_probe.json
reports/n22_minimal_susceptibility_update_probe.md
scripts/build_n22_minimal_susceptibility_update_probe.py
```

### Iteration 5. Durability Replay Probe

Replay the provisional susceptibility delta and test whether it survives
artifact-only reconstruction, snapshot/load replay, duplicate replay where
applicable, and later re-entry without producer reinforcement. Record
interaction, post-replay, and re-entry delta digests plus persistence ratio.

Expected artifacts:

```text
outputs/n22_durability_replay_probe.json
reports/n22_durability_replay_probe.md
scripts/build_n22_durability_replay_probe.py
```

### Iteration 6. Transfer / Re-entry Probe

Test whether the susceptibility delta is expressed in a declared later route,
boundary, corridor, or region re-entry context. This may remain local and
bounded; it must not claim general learning.

Expected artifacts:

```text
outputs/n22_transfer_reentry_probe.json
reports/n22_transfer_reentry_probe.md
scripts/build_n22_transfer_reentry_probe.py
```

### Iteration 7. Replay And Control Matrix

Consume all provisional rows and controls. Assign I7-consumable SU rungs only
after replay and negative controls pass or fail closed.

Expected artifacts:

```text
outputs/n22_replay_and_control_matrix.json
reports/n22_replay_and_control_matrix.md
scripts/build_n22_replay_and_control_matrix.py
```

### Iteration 8. Closeout And N23 Handoff

Classify final N22 support, record producer residue and naturalization debt,
preserve AP4/AP5 dependency status, record the N21 ND6 bridge status, and hand
off to N23 live-continuation collapse / selection geometry.

Expected artifacts:

```text
outputs/n22_closeout_and_n23_handoff.json
reports/n22_closeout_and_n23_handoff.md
scripts/build_n22_closeout_and_n23_handoff.py
```

## Closeout Requirement

N22 closeout must answer:

```text
Did N22 produce source-backed susceptibility-update evidence?
Did the delta survive replay and later re-entry?
Did same-budget peer comparison rule out global drift or scheduler artifact?
Was the result durable geometry modification rather than label/schedule/proxy?
Is any N21 ND6 bridge record supported, blocked, or not supported?
Which producer-mediated fields remain residue?
Which naturalization-debt fields remain unresolved?
Were AP4/AP5 dependencies carried row-locally?
Did unsafe relabels stay blocked?
Is N23 ready, and with what claim ceiling?
```
