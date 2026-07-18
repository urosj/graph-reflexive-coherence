# N31 Iteration 9-C - Route-Susceptibility Relaxation

## Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_C_R_DR4_route_susceptibility_relaxation_pending_I10
current rung = provisional producer-mediated C-R / DR4
DR5_supported = false
DR6_supported = false
native lane = D0a / DR2 unchanged
```

## Geometry And Formation

The three-node fixture contains a source route `0--1` and a registered
susceptible/readout edge `1--2`. A native `0.4` route-use packet crosses edge 1
from node 1 to node 2. Its exact arrival receipt triggers the producer-owned
closure, which raises susceptibility from `0.5` to
`0.9` under the frozen formation equation. Native route use
does not itself form susceptibility.

The packet changes native coherence conservatively. It does not directly write
conductance. The separately restored closure state is the only carrier of `S`.

## Relaxation Under Matched Progression

Two restored branches execute the same four native packet events on disjoint
edge 0. Their complete native v1/v2 identities and budgets remain equal. In the
active branch, the producer-owned closure consumes each exact arrival receipt
and applies `S_next = 0.5 + 0.75 * (S - 0.5)`. In the omitted branch, `S`
remains formed.

```text
formed S = 0.9
relaxed S = 0.6265625
S weakening = 0.2734375
```

The native events are experiment-scheduled and the closure callback is
producer-owned. This is not autonomous native susceptibility decay.

## Closure-Orchestrated Native-Kernel Readout

Before readout, both rows consume the same complete native state. The experiment
harness requests the readout; the Candidate C closure inserts the effective
edge-1 conductance after native conductance reconstruction; native GRC9V3
kernels compute potential and flux:

```text
g_native = 0.6065306597126334
formed g_effective = 0.5458775937413701
relaxed g_effective = 0.3800293664761969
g_effective weakening = 0.16584822726517323

formed signed flux = 0.1765143937092521
relaxed signed flux = 0.1480967673715728
signed flux change = 0.028417626337679303
```

This establishes bounded partial mediation through the registered edge's
conductance. The potential solution is graph-level. The result is a diagnostic
native-kernel flux computation, not packet transport, a coherence transition,
or an ordinary `LGRC9V3.step()` that consumes `S`. Exact pre-application native
v1/v2 identities and the complete snapshot are restored after every hook.

## Representation And Claim Boundary

`S` is versioned non-coherence closure state. The susceptibility-update
magnitude ledger is report-only and noncausal; it is not a cost ledger. Native
LGRC has no susceptibility memory or ordinary hook for this partial pipeline.
No resource cost is established, and the independently causal non-coherence
state is not naturalized into RC coherence. The weakening clock is the sequence
of experiment-scheduled edge-0 arrival receipts, not route-local proper time.

## Theory Positioning

Candidate C is closest to the *functional appearance* of reflexive geometry:
prior route use changes `S`, `S` changes effective conductance, and native
potential/flux diagnostics change. It is not closest to the strict 2025-11
coherence-only ontology. Under identical complete native coherence state,
independently restored `S` changes the readout, so `S` is an additional causal
degree of freedom. Candidate B is the closest added mechanism to the strict
ontology; D0a remains the preferred overall theory target.

Candidate C is therefore an effective closure or possible theory-extension
candidate. Naturalization would require `S` to be exactly reconstructable from
source-current `C/J_C` history with no independent freedom, or a native
`C_fast/C_slow` decomposition in which route use and ordinary coherence
dynamics form and relax the slow mode.

Candidate C therefore reaches provisional producer-mediated `C-R / DR4`.
`DR5` still requires I10's formal recursive row and complete control matrix;
`DR6` additionally requires a reusable closure contract. Native D0a remains at
`DR2`, and ordinary D0-R remains untested.

## Checks

| Check | Passed |
|---|---:|
| `exact_sources_consumed` | true |
| `topology_matches_frozen_candidate_C_contract` | true |
| `registered_native_route_use_triggers_producer_owned_susceptibility_formation` | true |
| `formed_closure_restores_before_progression` | true |
| `matched_native_progression_is_identical_between_closure_lanes` | true |
| `exact_receipts_drive_monotonic_bounded_relaxation` | true |
| `same_native_state_different_S_changes_native_readout` | true |
| `readout_shape_is_monotonic_and_local` | true |
| `native_coherence_budget_and_topology_preserved_during_readout` | true |
| `closure_observed_inputs_match_declared_allowlists` | true |
| `readout_authority_and_diagnostic_boundary_explicit` | true |
| `closure_and_native_readout_replay_exact` | true |
| `candidate_C_lane_controls_resolved` | true |
| `carrier_ledger_and_native_memory_boundaries_preserved` | true |
| `functional_resemblance_not_overpromoted_as_strict_ontological_fidelity` | true |
| `producer_C_R_DR4_ceiling_preserved` | true |
| `protected_runtime_contracts_unchanged` | true |
| `artifact_manifest_exact` | true |
| `no_absolute_paths_in_records` | true |
| `unsafe_claim_flags_false` | true |
| `I10_obligations_preserved` | true |
