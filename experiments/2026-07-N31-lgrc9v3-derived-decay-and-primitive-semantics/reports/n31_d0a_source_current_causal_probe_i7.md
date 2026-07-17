# N31 Iteration 7 - D0a Source-Current Causal Probe

## Result

```text
status = passed
acceptance_state = accepted_native_spatial_D0a_DR2_formation_persistence_and_conditional_reorganization_probe
primary_semantic_class = D0a
representation_or_authority_class = exact_derived_projection
organization_domain = spatial_distribution
native_D0a_ladder_ceiling = DR2
conditional_internal_reorganization_relation = supported
mediation_strength = bounded_partial
full_spatial_distribution_mediation_supported = false
n31_closeout_progress_rung = N31-C3
ready_for_iteration_8_replay_controls_classification = true
final_D0a_supported = false
final_N31_supported = false
```

I7 supports native spatial D0a formation and bounded persistence at `DR2`.
It also supplies a useful conditional perturbation result: native packet
transport executes an experiment-predeclared internal redistribution that
weakens, but does not erase, the signed formation coordinate. A later packet
departure is admitted in the persisted strong state and rejected after that
redistribution. The perturbation is not autonomous D0a weakening.

## Separate Evidential Objects

```text
native_spatial_D0a:
  formation = supported
  persistence = supported
  ladder ceiling = DR2
  autonomous weakening = unsupported

conditional_internal_reorganization:
  perturbation owner = experiment fixture
  execution owner = native LGRC9V3 runtime
  weakening direction = supported
  reverse reinforcement = supported
  local source-C consequence = supported, bounded partial
  native D0a rung effect = none
  D0 decay relation = false
```

These objects share one source-current trace but are aggregated separately.
The conditional perturbation cannot raise the native D0a ladder ceiling.

## Geometry

The registered route is `0 -> 1 -> 2`, with node 2 as the coordinate anchor.
The selected coordinate is `C[1] - C[2]`, oriented by the formation event
before outcomes are inspected:

```text
baseline strength = 0.000000000000
formed strength = 0.200000000000
persisted strength = 0.200000000000
weakened strength = 0.120000000000
reinforced-control strength = 0.280000000000
weakening amount = 0.080000000000
residual organization fraction = 0.600000000000
```

The hold row moves coherence only on the outside `3 -> 4 -> 3` lane and leaves
route organization unchanged. The weakening row moves `0.04` coherence from
route node 1 to anchor node 2. The reverse row moves the same amount from node
2 to node 1 and strengthens the coordinate. This is a preregistered directional
perturbation matrix, not an equal-state continuation test. The three branches
already contain different future packet queues. It shows different declared
inputs producing the expected conservative reorganizations; it does not show
an equal state autonomously diverging into weakening and reinforcement.

Route mass remains `1.0`; the weakening is redistribution inside the registered
route, not loss. No packet crosses the route boundary and signed integrated
outward transfer is zero.

## Causal Readout

The readout packet (`1 -> 0`, amount `0.22`) is queued before
the first runtime event in every branch. Native departure eligibility reads
source-current node-1 coherence:

```text
formed/hold readout admitted = true
formed/hold eligibility margin = 0.020000000000
weakened readout admitted = false
weakened eligibility margin = -0.020000000000
```

Two I4-admitted matched interventions establish a bounded local-C causal effect.
Clamping the hold branch back to baseline route C removes eligibility. Restoring
the formed route C in the weakened branch restores eligibility. In both
controls, route mass is unchanged and the complete restoration identity differs
only within declared route-node coherence paths. Native departure eligibility,
however, reads only source-node `C[1]`. The full `C[1]-C[2]` distribution is not
isolated as the load-bearing mediator, and `set_state()` does not recompute
constitutive dependent geometry. Full route-distribution and induced-geometric
mediation therefore remain unresolved.

The binary readout is narrowly threshold-gated. It differs only for readout
amounts in `0.20 < q <= 0.24`; the preregistered `q = 0.22` gives margins
`+0.02` and `-0.02`. I8 should preserve this continuous margin interpretation
and may audit the interval with a preregistered amount sweep.

## Producer Boundary

All four packet schedules are registered before the first runtime event. The
forming packet is exhausted before persistence, progression, and readout, and
there are no post-formation producer calls. That timing does not remove
producer authorship: the experiment fixture selects the weakening packet's
time, amount, source, destination, and direction. The native runtime owns the
conservative debit, in-flight state, and credit. The
`producer_scheduled_D0_decay` control therefore triggers and fails closed,
blocking autonomous weakening above native `DR2`.

The added producer-mechanism lane remains open pending I8 confirmation and I9
admission. The I7 result does not eliminate candidate A/B/C consideration.

## Comparative Boundary

```text
I5 D0c = instantaneous state/flux geometry at DR1
I6 D0b = fading finite-window observable at DR3, no mediation
I7 native D0a = spatial formation and persistence at DR2
I7 perturbation = experiment-authored internal reorganization with bounded local-C effect
```

The provisional RCAE projection preserves the same split, allows no automatic
adoption, and is not the final N31 return manifest.

## Contract Validation

```text
candidate required fields missing = []
nested contract fields missing = {}
nested contract values conform = true
```

## Checks

| Check | Passed |
|---|---:|
| `source_chain_exact` | `true` |
| `I4_exact_spatial_representation_admitted` | `true` |
| `trace_passed` | `true` |
| `candidate_schema_complete` | `true` |
| `native_D0a_DR2_and_conditional_reorganization_classification_pass` | `true` |
| `producer_schedule_authorship_fail_closed` | `true` |
| `bounded_partial_mediation_scope_preserved` | `true` |
| `control_status_meanings_conform` | `true` |
| `evidential_objects_remain_separate` | `true` |
| `RCAE_projection_preserves_I7_boundary` | `true` |
| `autonomous_relaxation_not_overclaimed` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `src_diff_empty` | `true` |
| `protected_runtime_contract_diff_empty` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Ceiling

```text
native_spatial_D0a_formation_and_persistence_at_DR2_plus_experiment_authored_conditional_internal_reorganization_with_bounded_local_source_C_readout_effect
```

This is not autonomous weakening, full route-distribution mediation,
induced-geometric mediation, a general decay law, memory,
trail/stigmergy, learning, communication, ecology, agency, native support, or
Phase 8 completion.

## Reproduction

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_d0a_source_current_causal_probe_i7.py
```

```text
output_digest = ada29118f7c3cad7db308ff0c026ee09270afbad620c3a613d378f28c35086d1
```
