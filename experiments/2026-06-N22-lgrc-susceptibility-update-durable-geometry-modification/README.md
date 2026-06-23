# N22 - LGRC Susceptibility Update And Durable Geometry Modification

N22 is the next becoming-primitive experiment after N21. It consumes the N20
same-basin continuation contract for `susceptibility_update` and the N21
closeout handoff as prerequisite context, then asks whether prior interaction
can durably alter later basin geometry without becoming a semantic learning
label.

Current state:

```text
status = initialized
source_contract_row = n20_i5_row_03_susceptibility_update
n21_context = WR6, ND5, N21-C6, ready_for_n22
target_primitive = susceptibility_update
target_reading = durable_geometry_modification
```

Core question:

```text
Can prior interaction durably alter later basin geometry in source-current
fields, with replayable re-entry evidence and controls against label-only,
transient, hidden producer, and semantic-learning relabel paths?
```

N22 is not a general learning, choice, or agency experiment. `Learning` may be
used only as bounded interpretation for durable geometry modification. The
primitive label is:

```text
susceptibility_update
durable_geometry_modification
```

## Source Boundary

Primary source artifacts:

```text
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_same_basin_continuation_contract.json
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_closeout_and_n21_handoff.json
experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_closeout_and_n22_handoff.json
experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md
experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md
```

N22 must consume:

```text
N20 source contract row = n20_i5_row_03_susceptibility_update
N21 closeout context = WR6, ND5, N21-C6, ready_for_n22
```

N21 WR/ND evidence is prerequisite context only. It cannot satisfy
susceptibility update or durable geometry modification.

## N21 ND6 Bridge Boundary

N22 should not claim that it is doing N21 `ND6` directly. N21 remains closed.
However, N21 closed at bounded local `ND5` because source-backed durable
geometry modification / susceptibility update was not yet produced. N22 tests
that missing condition.

N22 closeout should record:

```text
n21_nd6_bridge_status =
  not_supported |
  bridge_candidate_supported |
  blocked_by_replay |
  blocked_by_controls |
  blocked_by_AP_gap |
  blocked_by_producer_residue
```

The bridge can be a candidate only if N22 reaches `SU5` or `SU6` cleanly with
source-backed durable susceptibility delta evidence. It does not reopen N21,
does not upgrade N21 artifacts retroactively, and does not support general
naturalization depth.

## Required Source-Current Fields

Positive N22 rows must provide source-current evidence for:

```text
source_current_inputs
row_specific_thresholds_declared_before_use
susceptibility_update.pre_interaction_geometry_trace
susceptibility_update.post_interaction_geometry_trace
susceptibility_update.susceptibility_delta_trace
susceptibility_update.route_or_region_reentry_trace
```

Evidence must come from LGRC runtime or replay artifacts. A route label,
reinforcement schedule, producer note, report-built row, or semantic learning
label is not evidence.

## Primitive Reading

Susceptibility update means:

```text
after an interaction, later route, boundary, corridor, or region behavior
differs in a replayable source-current way because geometry changed, while
same-basin continuation and declared support/coherence/boundary/flux gates
remain inside scope.
```

Durable geometry modification means:

```text
the susceptibility delta survives a later replay or re-entry window without
the producer reinforcement schedule carrying the result.
```

N22 must allow geometry to change while preserving same-basin continuation.
Iteration 2 should freeze:

```text
allowed_delta_fields
same_basin_invariant_fields
out_of_scope_drift_blocks_row = true
delta_not_label_reassignment = true
```

N22 should also include a same-budget peer comparison when route or region
conditioning is tested:

```text
target route or region receives prior interaction
peer route or region receives the same budget but not the same prior interaction
later re-entry differs only in the target route or region
```

Without that comparison, global drift or scheduler artifacts can masquerade as
route-conditioned susceptibility.

It is not:

```text
semantic learning
semantic choice
intention
free will
agency
native support
identity acceptance
sentience
Phase 8 implementation
ant ecology implementation
```

## Local N22 Ladder

N22 uses a local susceptibility-update ladder:

```text
SU0 = no source-current susceptibility evidence
SU1 = interaction run present
SU2 = source-current pre/post geometry delta observed
SU3 = replay-backed susceptibility update candidate
SU4 = control-backed durable geometry modification candidate
SU5 = transfer/re-entry-backed susceptibility update candidate
SU6 = N23-ready bounded durable geometry modification evidence
```

The ladder is not an agency score and not a full learning taxonomy. It records
how much source-backed evidence exists for the N22 primitive.

## AP Gap Boundary

N22 must preserve the AP gap split inherited from N19/N20/N21:

```text
route-conditioned susceptibility update:
    AP4 dependency must be carried row-locally.

proxy-conditioned susceptibility update:
    conditional AP5 dependency must be carried when proxy derivation or target
    formation participates.
```

Rows should use closed status enums:

```text
ap4_dependency_status =
  required_recorded |
  not_applicable |
  missing_blocks_row

ap5_dependency_status =
  conditional_required_recorded |
  not_applicable |
  missing_blocks_row

ap4_condition_reason = ...
ap5_condition_reason = ...
```

N22 may contribute new evidence toward AP4/AP5 native-readiness gaps, but it
may not bypass those gaps by relabeling route labels, target labels, or proxy
metrics as source-current geometry.

## Evidence Standard

Good N22 evidence requires:

```text
actual LGRC/source-current run artifacts
predeclared interaction and later re-entry windows
source_current_inputs recorded
row_specific_thresholds_declared_before_use = true
pre-interaction geometry trace
post-interaction geometry trace
susceptibility delta trace
later route or region re-entry trace
same-budget peer or null comparison where route/region conditioning is claimed
interaction_delta_digest
post_replay_delta_digest
reentry_delta_digest
delta_persistence_ratio
delta_threshold_or_rule
one_window_transient_rejected = true
artifact replay
snapshot/load replay
duplicate replay where applicable
negative controls that fail closed
```

Insufficient evidence:

```text
route label changed without geometry change
reinforcement schedule label changed without source-current delta
one-window flux transient treated as durable modification
post-hoc delta construction
proxy improvement without same-basin continuation
global drift without same-budget peer distinction
N21 WR/ND closeout reused as susceptibility evidence
semantic learning or choice label used as evidence
```

## Expected Output Shape

Initial planned artifacts:

```text
outputs/n22_source_handoff_inventory.json
reports/n22_source_handoff_inventory.md
scripts/build_n22_source_handoff_inventory.py

outputs/n22_susceptibility_schema_and_controls.json
reports/n22_susceptibility_schema_and_controls.md
scripts/build_n22_susceptibility_schema_and_controls.py

outputs/n22_active_nulls_and_failure_baselines.json
reports/n22_active_nulls_and_failure_baselines.md
scripts/build_n22_active_nulls_and_failure_baselines.py

outputs/n22_minimal_susceptibility_update_probe.json
reports/n22_minimal_susceptibility_update_probe.md
scripts/build_n22_minimal_susceptibility_update_probe.py

outputs/n22_durability_replay_probe.json
reports/n22_durability_replay_probe.md
scripts/build_n22_durability_replay_probe.py

outputs/n22_transfer_reentry_probe.json
reports/n22_transfer_reentry_probe.md
scripts/build_n22_transfer_reentry_probe.py

outputs/n22_replay_and_control_matrix.json
reports/n22_replay_and_control_matrix.md
scripts/build_n22_replay_and_control_matrix.py

outputs/n22_closeout_and_n23_handoff.json
reports/n22_closeout_and_n23_handoff.md
scripts/build_n22_closeout_and_n23_handoff.py
```
