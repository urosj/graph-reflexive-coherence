# Phase 8 LGRC9 Multi-Basin Formation Closeout

Status: Closed.

Date: 2026-06-28.

## Summary

This continuation implements the N25.1 Phase 8 multi-basin formation tranche as
a default-off LGRC9V3 runtime extension. It adds runtime-visible multi-basin
flow-window records, child-basin state records, replay validation, merge/leakage
controls, telemetry exports, visual examples, and a front-capacity-gated
boundary-birth companion.

The supported ceiling is:

```text
MB5 = control-backed native multi-basin formation candidate
```

The closeout does not support:

```text
MB6
N26-ready unscoped multi-basin substrate evidence
BF6
independent new-basin formation as a general native capacity
native support
semantic learning
semantic choice
agency
identity acceptance
sentience
organism/life
ant ecology
Phase 8 completion
```

## Producer Compatibility Audit

The audited producer rule remains the existing LGRC9V3 producer discipline:

```text
producers observe declared runtime-visible LGRC/RC surfaces;
producers record declared evidence;
producers schedule declared work;
LGRC9V3 runtime transitions own coherence, topology, packet-ledger,
child-basin, replay/control, and claim-state mutation.
```

Audited producers:

- packet departure from flux routes;
- packet departure from route surplus;
- packet departure from pulse-substrate coupling;
- packet departure from feedback eligibility;
- boundary-birth trial producer.

The packet producers schedule packet-departure work from declared route,
surface-lineage, feedback, or route-surplus evidence. Packet coherence mutation
remains owned by the packet event processing path.

The boundary-birth producer schedules
`lgrc9v3_causal_boundary_birth_trial` records. Topology mutation remains owned
by `apply_causal_boundary_birth_trial(...)` when `step()` consumes the queued
trial. Iteration 88-A adds a stricter opt-in parent eligibility mode:

```text
causal_boundary_birth_parent_eligibility = grcl9v3_front_capacity
```

That mode consumes:

```text
grcl9v3_front_growth_eligible_ports
grcl9v3_growth_parent_capacity_sources
```

Missing or mismatched front-capacity metadata fails closed. This keeps the
producer from inventing basin content or choosing formation success above the
RC/LGRC runtime loop.

Producer scheduling is not treated as native support, semantic agency, or a
claim upgrade.

## Supported Capability

The implementation supports:

```text
multi_basin_runtime_surfaces_exposed = true
multi_basin_replay_validation_available = true
merge_leakage_control_matrix_available = true
front_capacity_boundary_birth_companion_available = true
mb5_control_backed_candidate_allowed = true
```

The implementation keeps:

```text
native_lgrc_multi_basin_formation_supported = false
mb6_or_stronger_supported = false
n26_unscoped_consumption_allowed = false
```

This means N26 should not consume this tranche as final multi-basin substrate
evidence. The next step is a smaller N25.2 bridge that records what N25, N25.1,
and this Phase 8 tranche still leave unresolved before N26.

## N25.2 Transition

N25.2 should consume:

```text
N25 BF5 scoped native and producer-assisted basin-formation evidence
N25.1 multi-basin requirement and missing-surface inventory
Phase 8 MB5 control-backed runtime/replay/control evidence
Iteration 88-A front-capacity boundary-birth companion evidence
remaining MB6 blockers
```

N25.2 should answer the narrower pre-N26 question:

```text
What exactly is still missing for N26-ready multi-basin substrate evidence,
given the new Phase 8 runtime surfaces and the remaining MB6 ceiling?
```

## Verification

Focused model, telemetry, visual, example, and lint checks:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py tests/telemetry/test_lgrc9v3_contract.py -q
333 passed, 81 subtests passed

.venv/bin/python -m pytest tests/visualization/test_visualization.py -q -k "lgrc9v3"
5 passed, 63 deselected

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/multi_basin_formation_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/topology_birth_refinement_visual_bundle.py
passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py
passed

.venv/bin/python -m ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/__init__.py src/pygrc/telemetry/lgrc9v3_contract.py src/pygrc/visualization/render.py src/pygrc/visualization/graph_render.py tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_autonomy_contract.py tests/telemetry/test_lgrc9v3_contract.py tests/visualization/test_visualization.py examples/lgrc9v3/multi_basin_formation_bundle.py examples/lgrc9v3/topology_birth_refinement_visual_bundle.py examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py
All checks passed

git diff --check
passed
```

## Claim Boundary

The following remain false:

```text
semantic_learning_claim_allowed = false
semantic_choice_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
native_support_claim_allowed = false
sentience_claim_allowed = false
organism_life_claim_allowed = false
ant_ecology_claim_allowed = false
phase8_completion_claim_allowed = false
```
