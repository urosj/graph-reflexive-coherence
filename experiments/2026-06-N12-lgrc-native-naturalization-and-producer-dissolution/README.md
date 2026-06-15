# N12 - LGRC Native Naturalization And Producer Dissolution

N12 is a bridge experiment. It takes the N05-N11 artifact/producer-layer
foundation and asks which parts can be dissolved into native LGRC mechanisms
without changing the RC theory boundary.

The core question is:

```text
Can the N05-N11 producer-layer mechanisms be classified into native-absorption
candidates, blocked theory-sensitive mechanisms, and experiment-local scaffolds,
while preserving claim boundaries?
```

N12 does not prove agency. It decides what can become native LGRC support later
if a separate Phase 8 task implements and validates the native surfaces.

## Boundary

N05-N11 produced an agentic-like foundation, not agency:

```text
final_supported_gali_ceiling = GALI7
final_claim_ceiling = broader_general_artifact_only_agentic_like_integration_candidate
artifact_only = true
fully_native = false
```

Producer mechanisms remain scaffolds unless Phase 8 implements them natively.
N12 may identify native absorption candidates, but an absorption candidate is
not native support.

Native absorption must remain compatible with:

```text
RC causality
RC coherence
LGRC geometry
packet scheduling
topology lineage
budget conservation
artifact replay
claim-boundary preservation
```

Do not change `src/*` for N12 without stopping and opening a separate Phase 8
task. If Phase 8 is later opened, native telemetry surfaces under
`src/pygrc/telemetry` are part of the search space, not an afterthought.

## Roadmap Position

N12 starts the N12-N18 agency-prerequisite tranche:

```text
N12:
    native naturalization / producer dissolution

N13-N18:
    self-maintenance, consequence sensitivity, endogenous proxy formation,
    self/environment boundary, closed action-perception loop, and long-horizon
    agentic-like closure stress testing
```

This tranche remains an agency-prerequisite program, not an agency claim.

## Primary Sources

N12 starts from these source artifacts:

```text
experiments/N12-N18-LGRC-AgencyPrerequisitesHandoff.md
experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md
experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md
experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_final_interpretation_and_roadmap_significance.md
experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_11_hypothesis_c_native_generalization_gap.md
experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_12_final_closeout_and_handoff.md
```

N11 carried forward these native blockers:

```text
native_route_conductance_memory_policy_missing
native_response_magnitude_policy_missing_for_unbounded_perturbations
native_identity_acceptance_validator_missing
native_agentic_like_integration_policy_missing
```

## Hypotheses

Hypothesis A:

```text
Some N05-N11 producer mechanisms are valid scaffolds but remain
artifact/producer-layer only.
```

Hypothesis B:

```text
Some mechanisms can be naturalized as native LGRC policy surfaces without
adding non-RC quantities.
```

Likely Hypothesis B candidates:

```text
native_route_conductance_memory_policy
native_response_magnitude_policy
```

Hypothesis C:

```text
Some mechanisms are theory-sensitive and must stay blocked until identity,
acceptance, or agency semantics are formalized.
```

Likely Hypothesis C candidates:

```text
native_identity_acceptance_validator
native_agentic_like_integration_policy
```

## N12 Naturalization Ladder

N12 uses a local naturalization ladder, separate from the AP0-AP8
agency-prerequisite ladder:

```text
NAT0:
    producer-only artifact scaffold

NAT1:
    source-backed producer pattern

NAT2:
    replayable producer pattern with controls

NAT3:
    native contract candidate; the native policy surface is named and
    plausible, but one or more Phase 8 readiness gates may still be missing

NAT4:
    Phase 8-ready native policy candidate; all readiness gates are explicit,
    but no native implementation or native support claim exists

NAT5:
    native implementation exists but is not integrated into agentic-like
    composition

NAT6:
    native implementation validates within composition replay
```

N12 aims for `NAT4`, not `NAT6`. `NAT5` and `NAT6` require separate Phase 8
implementation and return-validation work.

`NAT4` requires all of the following before a row can be called Phase 8-ready:

```text
native policy name
record schema sketch
default-off flags
enabled/validated/supported separation
idempotency/digest plan
runtime-visible inputs
budget surfaces
telemetry requirements
snapshot/replay requirements
negative controls
compatibility tests
claim flags forced false
non_rc_quantity_audit
mutation_boundary
producer_or_policy_may_schedule_only
step_or_topology_event_owns_state_mutation
src_diff_empty = true
native_supported_flags = false
phase8_opened = false
```

Current N12 state:

```text
status = n12_closed
target_naturalization_level = NAT4
strongest_recorded_level = NAT4
phase8_ready_rows = 2
identity_acceptance_boundary_nat_level = NAT2
agentic_like_integration_boundary_nat_level = NAT2
phase8_ready_contracts = native_route_conductance_memory_policy, native_response_magnitude_policy
phase8_implementation_opened = false
native_support_opened = false
n12_closeout_status = closed_claim_clean_bridge_experiment
```

## Initial Candidate Partition

This partition is a seed from N11, not a completed N12 result.

Native absorption candidates:

```text
native_route_conductance_memory_policy
native_response_magnitude_policy
```

Experiment-local scaffolds unless future scope changes:

```text
route_context_contract_hardening_if_scope_extends_beyond_selection
artifact_only_replay_validator_surfaces
claim_boundary_audit_fields
producer_fixture_fields
```

Theory-sensitive blockers:

```text
native_identity_acceptance_validator
native_agentic_like_integration_policy
semantic_goal_ownership_validator
native_self_environment_boundary_validator
closed_action_perception_loop_meta_policy
```

N12 rows use a non-overlapping disposition model:

```text
primary_disposition =
    scaffold
    native_absorption_candidate
    theory_sensitive_blocker
    blocked_missing_source_or_gate

nat_level =
    NAT0..NAT6

phase8_ready =
    true only when nat_level = NAT4
```

`phase8_ready` is derived from the NAT level. It is not a competing primary
class.

## Provisional Iteration 1 Row Shape

Iteration 2 freezes the final schema, but Iteration 1 inventory rows must use
this minimal provisional shape:

```text
row_id
source_experiment
source_iteration
source_artifact
source_report
source_sha256
mechanism_name
mechanism_role
producer_decision_fields
bookkeeping_fields
runtime_visible_surfaces
budget_surfaces
native_gap
provisional_primary_disposition
provisional_nat_level
provisional_phase8_ready
claim_ceiling
blocked_claims
missing_gates
non_rc_quantity_audit
```

For route conductance memory, `non_rc_quantity_audit` must ask whether memory
is a coherence, geometry, or flux effect; whether it is only producer
bookkeeping; whether decay or relaxation conserves an accounted quantity; and
whether the candidate requires a new scalar state outside RC accounting. A row
that requires an unaccounted extra quantity cannot reach `NAT4`.

For response magnitude, `non_rc_quantity_audit` must ask whether proxy
measurement is a derived observable or new state; whether the target band is
exogenous or a runtime-visible policy; whether response gain is serialized and
replayable; whether correction debits node-plus-packet budget; and whether
response sizing requires hidden optimization or external controller state.

## Iteration Structure

```text
Iteration 0:
    planning and stubs

Iteration 1:
    baseline and mechanism inventory

Iteration 2:
    naturalization schema and ladder

Iteration 3:
    route conductance memory candidate

Iteration 4:
    response magnitude candidate

Iteration 5:
    identity acceptance boundary

Iteration 6:
    agentic-like integration boundary

Iteration 7:
    Phase 8 readiness package, no implementation

Iteration 8:
    N12 closeout and handoff
```

Minimum planned outputs:

```text
outputs/n12_native_naturalization_inventory.json
reports/n12_native_naturalization_inventory.md

outputs/n12_naturalization_schema_v1.json
reports/n12_naturalization_schema_v1.md

outputs/n12_phase8_readiness_matrix.json
reports/n12_phase8_readiness_matrix.md

outputs/n12_closeout_and_handoff.json
reports/n12_closeout_and_handoff.md
```

## Claim Boundary

The following statements must remain explicit throughout N12:

```text
native absorption candidate != native support
native support != agency
route conductance memory != intention
response magnitude policy != goal ownership
identity validator candidate != identity acceptance
agentic-like integration != agency
```

The following implications remain invalid:

```text
producer dissolution plan => native support
Phase 8 readiness => Phase 8 implementation
route conductance memory policy => ACO or ant-colony behavior
response magnitude policy => semantic goal ownership or intention
support survival => identity acceptance
native policy support => semantic agency
artifact-only replay => fully native integration
agentic-like integration => agency, personhood, or biological behavior
```

The clean N12 result would be:

```text
N12 classifies the N05-N11 producer mechanisms into native absorption
candidates, Phase 8-ready contracts, and theory-sensitive blockers. It
identifies route conductance memory and response magnitude policy as the first
concrete native implementation candidates, while keeping identity acceptance
and full agentic-like integration blocked.
```

N12 closes only when every seed row is classified, every NAT level is frozen,
every Phase 8-ready row has controls, telemetry requirements, and tests, and
every deferred row has a blocker and rationale.

N12 closeout status:

```text
n12_closed = true
final_status = closed_claim_clean_bridge_experiment
phase8_ready_contracts = native_route_conductance_memory_policy, native_response_magnitude_policy
deferred_blockers = native_identity_acceptance_validator, native_agentic_like_integration_policy
native_supported_flags = false
phase8_opened = false
phase8_implementation_opened = false
```
