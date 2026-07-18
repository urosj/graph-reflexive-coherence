# N31 Iteration 8 - D0 Replay, Controls, And Classification

## Result

```text
status = passed
acceptance_state = accepted_replay_control_backed_D0_classification_with_native_D0a_DR2_ceiling_and_autonomous_weakening_mechanism_need
n31_closeout_progress_rung = N31-C4
native_spatial_D0a_ladder_ceiling = DR2
autonomous_D0a_weakening_supported = false
conditional_internal_reorganization_supported = true
conditional_reorganization_is_D0_decay = false
mediation_strength = bounded_partial_local_source_C
full_route_distribution_mediation = unresolved
added_mechanism_admission_scientifically_justified = true
ready_for_iteration_9_added_mechanism_admission = true
final_N31_supported = false
```

I8 replays and classifies the current coherence-only decay evidence without
promoting the I7 perturbation result. Existing LGRC supports spatial formation
and persistence, plus conservative externally specified reorganization, but it
does not supply a native autonomous weakening trajectory.

## Comparative Classification

```text
D0c = DR1 instantaneous current-state geometry; no persistence or mediation
D0b = DR3 finite-window fading derived observable; no causal mediation
native spatial D0a = DR2 formation and persistence; autonomous weakening absent
conditional reorganization = replay-clean perturbation with bounded local-C effect
D0-R = not instantiated in the executed fixtures; ordinary export was not tested
```

The native D0a result and conditional reorganization remain separate
evidential objects. The latter cannot raise the native D0a rung.

## Replay

```text
artifact manifest references replayed = 45
unique artifact paths replayed = 25
duplicate cross-source references = 20
snapshot rows roundtripped = 19
execution reconstruction = passed_complete
duplicate replay = passed
equal-state continuation = true
direction matrix consumed as equal-state = false
```

I8 directly reruns the I3, I5, I6, and I7 builders. It verifies I2, I3R1,
I4, I4R1, and I5R1 transitively through those exact source chains; it does not
claim that every evidence-stack builder was directly rerun. The `45` manifest
references resolve to `25` unique paths, with `20` repeated cross-source
references. Every reference hash is exact.

Restoration identities v1 and v2 remain exact across snapshot/load replay.
No consumed row invokes `reset`; v2 is nevertheless audited on every I7
snapshot roundtrip. Cache recomputation and execution reconstruction remain
separate checks. Equal-state continuation establishes replay correctness only;
it adds no weakening-selection, mediation, or route-distribution-causality
evidence.

## Threshold Scope

| Amount `q` | Hold admitted | Weakened admitted | Region |
|---:|---:|---:|---|
| 0.18 | true | true | `both_pass_below_or_at_weakened_source_C` |
| 0.20 | true | true | `both_pass_below_or_at_weakened_source_C` |
| 0.21 | true | false | `differentiated_threshold_interval` |
| 0.22 | true | false | `differentiated_threshold_interval` |
| 0.24 | true | false | `differentiated_threshold_interval` |
| 0.25 | false | false | `both_fail_above_hold_source_C` |
| 0.26 | false | false | `both_fail_above_hold_source_C` |

The differentiated effect is confined to `0.20 < q <= 0.24`. The `q = 0.24`
row is the native floating-point eligibility boundary with effectively zero
hold margin, not a meaningful positive-margin endpoint. This is a narrow native
source-C departure threshold, not broad route retuning or full-distribution
mediation.

## Control Boundary

```text
producer_scheduled_D0_decay = failed_closed
forming_packet_exclusion = passed
route_mass_match = passed
direction_matrix = perturbation_control
proper_time_alignment = not_applicable
failed_open candidate controls = 0
not_run candidate controls = 0
```

The `70` I3 rows are generic pre-positive nulls. They remain separate from the
candidate-specific I5-I7 controls and are not presented as direct per-candidate
null consumption. All required controls are resolved, with no `failed_open` or
`not_run` dependent control.

## Added-Mechanism Consequence

The existing admission enum remains `d0_insufficient`, qualified precisely as
`d0_insufficient_for_autonomous_causal_weakening`. D0 is not wholly
insufficient: its D0c, D0b, and native spatial D0a results remain supported at
their bounded ceilings. D0-R is uninstantiated in the executed fixtures, not
globally refuted.
I8 does not select A, B, or C, but it keeps all three candidate lanes open.
The purpose is to test a bounded producer-owned lifecycle mechanism that may
supply the missing transition selection, not to relabel the I7 perturbation as
native decay.

## Checks

| Check | Passed |
|---|---:|
| `I8_trace_passed` | `true` |
| `D0_classes_remain_separate` | `true` |
| `I7_demotion_preserved_on_all_aggregation_surfaces` | `true` |
| `added_mechanism_lane_remains_open` | `true` |
| `RCAE_projection_bounded` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `src_diff_empty` | `true` |
| `protected_runtime_contract_diff_empty` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Ceiling

```text
replay_control_backed_native_spatial_D0a_formation_and_persistence_at_DR2_plus_separate_experiment_authored_conditional_reorganization_with_bounded_local_C_effect
```

This is not autonomous D0a weakening, a native DR4 relation, full route
mediation, induced-geometric mediation, a general decay law, memory,
trail/stigmergy, communication, ecology, agency, native support, or Phase 8
completion.

## Reproduction

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_d0_replay_controls_classification_i8.py
```

```text
output_digest = bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8
```
