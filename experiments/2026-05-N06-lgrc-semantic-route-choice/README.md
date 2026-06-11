# N06 LGRC Semantic Route Choice

N06 studies whether LGRC can support route selection that is explained by a
runtime-visible context or affordance relation. It follows N05 coherence waves
and oscillators, but it does not inherit memory, trail, agency, identity, ACO,
or locomotion claims from N05.

N05 closed at:

```text
strongest_supported_o_level = O5
strongest_claim_ceiling = self_sustained_oscillator_candidate
o6_route_coupled_oscillator_supported = false
trail_memory_blocker = missing_route_conductance_memory_policy
```

N06 uses the O5 oscillator/circuit result as background only. Memory or trail
formation remains deferred to N08.

## Core Question

```text
Can LGRC select one route from competing alternatives because of a serialized,
runtime-visible context/affordance relation, without hidden fixture labels,
experiment-side if/else, report-side selection, or claim promotion?
```

## Semantic Choice Definition

For N06, semantic route choice means:

```text
native route selection whose selected route is reconstructable from:
    committed candidate routes
    serialized route-arbitration policy
    runtime-visible context/affordance evidence
    deterministic artifact-replayable scoring or compatibility gates
```

It does not mean:

```text
pheromone following
trail memory
agency
intention
identity acceptance
locomotion
ACO behavior
```

Pheromone/trail following belongs to N08 because it requires a memory or
route-history surface. N06 may use flux, polarity, route-aspect, or context
weights as runtime-visible selection inputs, but weighted routing counts only
if artifact replay can explain why the selected route matched the declared
context.

The current native route-arbitration contract does not define a dedicated
`context_surface` record type. N06 must map context/affordance evidence onto
native serialized fields before running probes, such as:

```text
candidate_score_components
candidate_runtime_visible_inputs
arbitration_runtime_visible_inputs
causal pulse-substrate surface rows
route-aspect mass, polarity, or channel fields
```

If a compatibility gate is needed, N06 must declare whether it is encoded as
native score components with a threshold interpretation or as an
experiment-local gate record. Hidden context arrays are invalid.

## Working Model

The minimal N06 fixture should expose:

```text
source node
two or more candidate routes
visible context/affordance surface
native route-arbitration policy
selected route evidence
scheduled/processed packet evidence where applicable
```

The essential positive pattern is:

```text
same source
-> competing candidate routes
-> context state A visible
-> native arbitration selects route A
-> context state B visible under the same policy
-> native arbitration selects route B
```

The context may be a declared compatibility gate, polarity relation, route
aspect relation, source demand signal, target affordance signal, or other
serialized runtime-visible field. Fixture labels such as "nest", "food",
"danger", or "goal" are shorthand only until the runtime-visible relation
explains selection.

## Native LGRC Surfaces

N06 should prefer existing native LGRC9V3 support where available:

```text
native route candidate records
native candidate-set records
native route-arbitration records
selected topology event linkage where topology changes are in scope
surface lineage transport
topology-state reabsorption
producer records and LGRC scheduling
artifact-only route-arbitration replay
```

Native route-arbitration records are LGRC-3/topology-changing-causal-history
surfaces. Enabling the native policy requires the LGRC-3 causal mode and the
prior topology support layers: causal topology integration, surface-lineage
transport, and topology-state reabsorption. LGRC-2 fixed-route probes may be
used only as experiment-local scaffolds or controls; they are not native route
arbitration evidence.

Native route arbitration is infrastructure. It becomes N06 evidence only when
the selected route is explained by a runtime-visible semantic/context relation.
Route arbitration by list order, hidden preference, fixture-side if/else, or
preselected sink is not semantic choice.

## Choice Ladder

The SC-ladder is local to N06. It is an evidence ladder, not a claim flag.

```text
SC0: no choice / fixed route
    The runtime has no competing route candidates or always follows one
    declared fixed route.

SC1: alternatives exposed
    Multiple route candidates are emitted from committed runtime-visible
    evidence, but no route is selected.

SC2: native arbitration selection
    A serialized native arbitration policy selects exactly one candidate from
    a complete candidate set. Selection is replayable, but not yet semantic.

SC3: context-conditioned selection
    Selection changes when a runtime-visible context or affordance surface
    changes, under the same serialized policy.

SC4: bidirectional or polarity-swapped selection
    Forward/reversed or polarity-swapped fixtures select corresponding routes
    with matched policy, thresholds, and controls.

SC5: repeated context-conditioned selection
    The same policy repeatedly selects the context-compatible route across
    multiple cycles without hidden schedule or report-side steering.

SC6: artifact-only semantic route-choice candidate
    Artifact replay reconstructs candidate set, context evidence, native
    arbitration, selected route, rejected routes, downstream scheduling, and
    controls without private runtime state.
```

## Required Evidence

Every N06 positive row should record:

```text
run_id
sc_level
sc_level_is_evidence_classification = true
claim_ceiling
claim_flags
runtime_family
lgrc_runtime_level
source_native_surfaces
candidate_route_records
candidate_set_record
native_route_arbitration_record
selected_candidate_route_digest
rejected_candidate_route_digests
context_surface
context_surface_digest
context_relation
context_runtime_visible = true
selection_rule
selection_reason_code
score_components or compatibility_gate_components
event_time_key
scheduler_event_index
node_proper_time where available
scheduled_packet_id where applicable
processed_packet_id where applicable
artifact_only_replay
budget_surface
node_plus_packet_budget_error
producer_boundary
blocked_claims
```

## Controls

N06 must include negative controls with distinct primary blockers:

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

Candidate and arbitration artifacts must be default-off unless N06 explicitly
enables the relevant policy.

## Claim Boundary

The following remain false in N06 unless a later experiment separately
validates them:

```text
memory_or_trail_claim_allowed = false
agency_claim_allowed = false
agentic_like_claim_allowed = false
rc_identity_collapse_claim_allowed = false
identity_acceptance_claim_allowed = false
goal_proxy_regulation_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
ant_colony_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

N06 may support:

```text
semantic_route_choice_candidate
```

only if the selection is context-conditioned, native-arbitrated, replayable
from artifacts, and guarded by controls.

N06 does not support:

```text
memory / trail formation
ACO behavior
agency
identity acceptance
locomotion
```

## Implementation Strategy

N06 should start experiment-local and source-backed:

```text
Iteration 1:
    baseline, source inventory, claim flags, SC schema

Iteration 2:
    fixture manifest and controls

Iteration 3:
    SC1 candidate alternatives exposed

Iteration 4:
    SC2 native arbitration selection without semantic promotion

Iteration 5:
    SC3 context-conditioned route selection

Iteration 6:
    SC4 polarity/context swap controls

Iteration 7:
    SC5 repeated context-conditioned selection

Iteration 8:
    SC6 artifact-only replay and closeout
```

If current LGRC cannot express a needed context or affordance surface as a
serialized runtime-visible policy, N06 should record a native-policy blocker
instead of hiding the missing mechanism in fixture code.

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
native-policy blockers, if any
handoff recommendation for N07
```

N06 should hand off to N07 only after the route-choice ceiling is explicit and
no memory/trail, identity, agency, ACO, or locomotion claims have leaked into
the route-choice evidence.

## Closeout Result

N06 closes at:

```text
strongest_supported_sc_level = SC6
strongest_claim_ceiling = artifact_only_semantic_route_choice_candidate
semantic_choice_claim_allowed = false
memory_or_trail_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

The closeout artifact is:

```text
outputs/n06_iteration_8_sc6_closeout.json
reports/n06_iteration_8_sc6_closeout.md
```

The final replay also rechecks source-surface provenance, score-component
invariants, arbitration-score consistency, context-field consistency,
candidate-set digest separation, stale-candidate rejection, and false claim
flags in route-arbitration artifacts.

SC6 is an evidence classification for artifact-only, selection-only semantic
route-choice candidate evidence. It does not promote broad semantic-choice,
memory/trail, agency, identity, ACO, locomotion, biology, or unrestricted
movement claims.

N07 handoff recommendation:

```text
proceed_to_N07_rc_identity_attractor_invariance
```

N07 may use N06's artifact-only route-choice candidate as route-selection
background, but must independently validate RC identity and attractor
invariance.
