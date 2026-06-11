# N06 Semantic Route Choice Implementation Plan

This document records the implementation plan for
`2026-05-N06-lgrc-semantic-route-choice`.

N06 asks whether LGRC can select one route from competing alternatives because
of serialized runtime-visible context or affordance evidence. It follows N05,
which closed at O5 self-sustained oscillator evidence and left O6
route-memory/trail coupling blocked.

## Scope

N06 is experiment-local unless a separate Phase 8/core task is opened. Scripts,
configs, reports, and outputs should live under:

```text
experiments/2026-05-N06-lgrc-semantic-route-choice/
```

Do not change `src/*` for N06 without stopping and opening a separate Phase 8
implementation task. Existing LGRC9V3 route-arbitration, candidate-route,
candidate-set, topology, producer, ledger, snapshot, telemetry, and
artifact-replay surfaces may be used, but N06 experiment-local code must not
silently redefine their semantics.

## Roadmap Position

N06 follows N05:

```text
N05:
    coherence waves and oscillators
    strongest_supported_o_level = O5
    strongest_claim_ceiling = self_sustained_oscillator_candidate

N06:
    semantic route choice through context-conditioned native route selection

N07:
    RC identity / attractor invariance

N08:
    memory / trail / affordance formation
```

N06 does not prove memory, trail, ACO, agency, identity acceptance, or
locomotion. It should hand off to N07 only after the route-choice ceiling is
explicit and all claim boundaries remain clean.

## Core Claim Discipline

Allowed if supported by gates:

- competing-route exposure candidate;
- native route-arbitration candidate;
- context-conditioned route-selection candidate;
- polarity/context-swapped route-selection candidate;
- repeated context-conditioned route-choice candidate;
- artifact-only semantic route-choice candidate.

Blocked in N06:

- memory or trail formation;
- pheromone following;
- ACO or colony-like behavior;
- agency or intention;
- RC identity collapse;
- identity acceptance;
- goal-proxy regulation;
- agentic-like behavior;
- locomotion-like behavior;
- biological behavior;
- unrestricted movement.

Native route arbitration is infrastructure. It is not semantic choice unless
the selected route is explained by serialized runtime-visible context or
affordance evidence and replayable from artifacts.

## Semantic Choice Definition

For N06, semantic route choice means:

```text
selected route =
    native route-arbitration result
    over a complete candidate set
    under a serialized policy
    explained by runtime-visible context/affordance relation
```

Invalid sources of semantic choice:

```text
hidden fixture labels
experiment-side if/else
preselected selected_sink_id
report-side route choice
Python/list order unless explicitly serialized as policy
post-hoc threshold changes
hidden route preference
hidden context array
```

The minimum positive result should show that the same source and same declared
policy select different routes when the runtime-visible context changes.

## RC Compatibility Boundary

Any context or affordance policy considered during N06 must be compatible with
the RC closed-system interpretation. Policies may expose compatibility,
polarity, route aspect, target affordance, source demand, budget prediction, or
local response. They must not inject coherence, delete coherence, preselect
outcomes, or emit claims.

Allowed policy role:

```text
runtime-visible context / compatibility / route-selection evidence
```

Forbidden policy role:

```text
external controller / hidden semantic label / agency / hidden source term
```

If current LGRC cannot express a needed semantic context surface as serialized
runtime-visible policy, N06 must record a native-policy blocker rather than
hiding the missing mechanism in fixture code.

## Context/Affordance Surface Mapping

The current native LGRC9V3 route-arbitration contract does not provide a
dedicated `context_surface` record type. N06 must map its context/affordance
surface onto existing serialized native fields before any SC3+ claim can be
made.

Allowed native mappings include:

```text
candidate_score_components
candidate_runtime_visible_inputs
arbitration_runtime_visible_inputs
causal pulse-substrate surface rows
route-aspect mass / polarity / channel fields
```

The baseline inventory must record the selected mapping and the fixture
manifest must define how context states A and B are serialized. If the context
relation needs binary compatibility gates, the manifest must declare one of:

```text
native score components with threshold interpretation
experiment-local compatibility gate records
```

Experiment-local gate records may support exploratory evidence, but they must
be labeled as experiment-local and cannot be described as native LGRC context
surfaces.

Preferred Iteration 2 default:

```text
context score:
    candidate_score_components

context source names:
    candidate_runtime_visible_inputs
    arbitration_runtime_visible_inputs

compatibility gate:
    native score components with threshold interpretation
```

This default keeps the context relation inside serialized native route
candidate/arbitration artifacts. Causal pulse-substrate rows may be cited as
source evidence when context is derived from pulse/substrate surfaces.
Experiment-local compatibility gate records are fallback scaffolds only and
cannot support native semantic route-choice claims.

## Native LGRC Surface Mapping

N06 should reuse existing Phase 8 LGRC9V3 surfaces before adding
experiment-local equivalents:

```text
SC1:
    candidate route records
    candidate set records

SC2:
    native route-arbitration records
    deterministic selected/rejected candidate digests

SC3-SC5:
    native route arbitration plus serialized context/affordance surface
    producer records and LGRC scheduling where packet work is in scope

Topology-changing variants:
    selected topology event
    surface lineage transport
    topology-state reabsorption
    time-scoped lineage replay

Artifact replay:
    route-arbitration artifact-only replay
    candidate/context/order/budget/claim controls
```

Native route-arbitration records require:

```text
lgrc_runtime_level = lgrc3
causal_layer_mode = topology_changing_causal_history
causal_topology_integration_allowed = true
causal_pulse_substrate_surface_lineage_transport_supported = true
causal_topology_state_reabsorption_supported = true
native_lgrc_route_arbitration_enabled = true
native_lgrc_route_arbitration_policy != disabled
```

N06's preferred native policy is:

```text
native_lgrc_route_arbitration_policy =
    score_ordered_topology_route_candidates
```

This is the default N06 policy, not a hard gate. The hard gate is that the
policy is not `disabled` and that the serialized policy is compatible with the
native route-arbitration contract.

LGRC-2 fixed-route alternatives may still be useful as experiment-local
scaffolds or controls, but they are not native route-arbitration evidence.
Iteration 1 must decide whether N06 runs native SC lanes entirely at LGRC-3, or
uses LGRC-2 experiment-local scaffolds before transitioning to native LGRC-3
arbitration.

The disabled policy coupling is strict:

```text
LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
requires native_lgrc_route_arbitration_enabled = false.
```

`redirect` is a native route-intent value, but N06 must declare whether it is
used as fixed-route/control scaffolding or with an explicit topology-event kind.
It must not be read as topology-mutating movement evidence merely because the
route intent value is present.

N04/Phase 8 route-arbitration artifacts may be cited as upstream contract
precedent and source provenance, but they are not N06 semantic route-choice
evidence.

## SC-Ladder

The SC-ladder is local to N06. It records route-choice evidence and does not
itself promote agency, identity, memory, ACO, or locomotion claims.

```text
SC0:
    no choice / fixed route

SC1:
    alternatives exposed

SC2:
    native arbitration selection

SC3:
    context-conditioned selection

SC4:
    bidirectional or polarity/context-swapped selection

SC5:
    repeated context-conditioned selection

SC6:
    artifact-only semantic route-choice candidate
```

SC-levels are evidence classifications, not claim flags.

Required LGRC runtime levels should be recorded per row:

```text
SC0:
    LGRC-0/LGRC-1/LGRC-2 fixed-route control

SC1:
    LGRC-3 for native candidate route emission; LGRC-2 only for explicitly
    experiment-local scaffold/control rows

SC2:
    LGRC-3 topology-changing causal history for native route arbitration

SC3-SC6:
    LGRC-3 for native route-arbitrated rows; experiment-local LGRC-2 rows must
    be labeled as non-native scaffolds
```

## Required Evidence

Every positive row should record:

```text
run_id
sc_level
sc_level_is_evidence_classification
claim_ceiling
claim_flags
runtime_family
lgrc_runtime_level
source_native_surfaces
fixture_id
source_node_id
candidate_route_records
candidate_route_digests
candidate_set_record
candidate_set_digest
native_route_arbitration_record
native_route_arbitration_digest
selected_candidate_route_digest
rejected_candidate_route_digests
context_surface
context_surface_digest
context_relation
context_runtime_visible
selection_rule
selection_reason_code
score_components
compatibility_gate_components or native score-component threshold mapping
arbitration_window_id
candidate_source_surface_digest
candidate_source_producer_record_id where applicable
candidate_source_topology_state_reabsorption_digest where applicable
route_intent
selected_topology_event_id where native arbitration selects a route
event_time_key
scheduler_event_index
causal_epoch
node_proper_time where available
scheduled_packet_id where applicable
processed_packet_id where applicable
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
producer_records where applicable
producer_boundary
artifact_only_replay
controls
blocked_claims
```

## Report Schema

Initial reports should use:

```text
semantic_route_choice_report_v1
```

Required top-level fields:

```json
{
  "schema": "semantic_route_choice_report_v1",
  "run_id": "",
  "iteration": "",
  "runtime_family": "LGRC9V3|experiment_local",
  "lgrc_runtime_level": "lgrc0|lgrc1|lgrc2|lgrc3",
  "execution_stage": "",
  "source_native_surfaces": {},
  "fixture": {},
  "sc_ladder": {},
  "candidate_routes": {},
  "candidate_set": {},
  "context_surface": {},
  "route_arbitration": {},
  "selection_evidence": {},
  "timing": {},
  "producer_boundary": {},
  "conservation": {},
  "artifact_replay": {},
  "controls": {},
  "claim_boundary": {},
  "claim_flags": {},
  "claim_ceiling": "",
  "blocked_claims": []
}
```

Every positive row should separate route selection from claim permission:

```json
{
  "claim_boundary": {
    "sc_level_is_evidence_classification": true,
    "native_route_arbitration_is_not_semantic_choice_by_itself": true,
    "semantic_choice_claim_allowed": false,
    "agency_claim_allowed": false,
    "memory_or_trail_claim_allowed": false
  }
}
```

## Controls

N06 controls must fail with distinct primary blockers:

```text
policy disabled
no candidates
unresolved tie
hidden context
hidden route preference
preselected sink
experiment-side if/else
report-side selection
post-hoc threshold change
budget mismatch
order inversion
stale candidate
stale context
duplicate arbitration
producer mutation
claim promotion
```

Controls should verify both construction-time and artifact-replay rejection
where applicable.

## Iterations

### Iteration 0. Planning And Handoff

Create the N06 README, implementation plan, and checklist. Record N05 inherited
boundary and N06 claim discipline.

### Iteration 1. Baseline And Schema Inventory

Inventory N05 closeout artifacts, native route-arbitration surfaces, candidate
route/set schemas, artifact replay validators, and available context/affordance
surfaces. Freeze the SC row schema and blocked claim flags. No route-choice
probes run in this iteration.

This iteration must also record:

```text
context/affordance native-field mapping
LGRC-3 native route-arbitration gate
validate_lgrc9v3_native_route_arbitration_artifacts(...) signature and
failure modes
candidate_route_score == sum(candidate_score_components) native invariant
candidate-set ordering and unresolved-tie serialization fields
```

### Iteration 2. Fixture Manifest And Controls

Define the minimal source-plus-two-routes fixture, candidate routes, context
surface, context-swap lanes, budget tolerance, default-off policy, and negative
controls. Freeze semantics for candidate completeness and context visibility.

The fixture manifest must define:

```text
arbitration_window_id boundary
arbitration window artifact kinds and timing fields
candidate source evidence fields
SC1 vs post-topology candidate source evidence requirements
compatibility gate representation
context-to-score-component derivation from runtime-visible artifacts
route_intent values
selected topology event behavior
default-off causal-mode fields
```

For SC1 candidate exposure, `candidate_source_surface_digest` must become a
committed runtime value, while `candidate_source_topology_state_reabsorption_digest`
is not required for the first pre-topology candidate set. Reabsorption digests
are required only when the candidate source is already post-topology. Context
score components must be reconstructable from serialized runtime-visible
context/source artifacts, not only from manifest templates.

### Iteration 3. SC1 Alternatives Exposed

Emit candidate route records and a candidate set from committed
runtime-visible evidence. Do not select a route. Verify default-off behavior,
candidate completeness, deterministic ordering, idempotency, budget prediction,
and hidden-input rejection.

### Iteration 4. SC2 Native Arbitration Selection

Use native route arbitration to select exactly one candidate from a committed
candidate set. Record selected and rejected digests, reason codes, score or
compatibility rule, and artifact-replayable ordering. Do not claim semantic
choice yet unless the context relation is in scope and validated.

### Iteration 5. SC3 Context-Conditioned Route Selection

Run the same fixture and same serialized policy under two runtime-visible
context states. Verify that context A selects route A and context B selects
route B, with selection reconstructed from serialized context evidence.

### Iteration 6. SC4 Polarity Or Context-Swap Controls

Run matched reversed/polarity-swapped/context-swapped lanes. Verify the same
policy, thresholds, budget tolerance, candidate-set rules, and validator are
used. Distinguish context-conditioned selection from hidden direction labels.

### Iteration 7. SC5 Repeated Context-Conditioned Selection

Repeat context-conditioned route selection across multiple cycles or windows.
Verify no hidden schedule, no stale context reads, no duplicate arbitration,
and exact node-plus-packet budget.

### Iteration 8. SC6 Artifact-Only Replay And Closeout

Run artifact-only replay over candidate routes, candidate set, context surface,
arbitration record, selected route, rejected routes, scheduled/processed packet
evidence where applicable, and controls. Freeze strongest supported SC level,
claim ceiling, native-policy blockers, and N07 handoff recommendation.

## Closeout Criteria

N06 closeout should record:

```text
strongest_supported_sc_level
strongest_claim_ceiling
positive artifacts and SHA-256 digests
negative controls and primary blockers
artifact-only replay result
budget conservation result
producer boundary result
native-policy blocker, if any
handoff recommendation for N07
```

N06 must not promote memory, trail, agency, identity acceptance, ACO,
locomotion, biology, or unrestricted movement claims.
