# N31 Iteration 10 - Added-Mechanism Replay And Controls

## Result

```text
status = passed
acceptance_state = accepted_added_mechanism_family_replay_controls_with_lane_specific_DR5_and_no_native_upgrade
A added-mechanism lane = DR5 expression attenuation
B added-mechanism lane = DR5 conserved export
C.2 relation carrier lane = DR2
C.2 producer-extension lane = DR5 effective exact-history closure
C.2 native-runtime lane = DR0
native spatial D0a = DR2 unchanged
DR6 = unsupported in I10
N31 closeout progress = N31-C4
ready for I11 = true
```

I10 applies the replay, restoration, invariant, accounting, topology, hidden-state,
and producer/native gates to the three mechanism families. It admits each family
once. I9-A.1 and I9-B.1 strengthen their parent families; they are not extra
candidates. I9-C and I9-C.1 remain zero-weight C ancestry. C.2 is the sole
comparison-eligible C representative.

## Replay

```text
manifest references replayed = 66
unique artifact paths replayed = 66
all source identities exact = true
all manifest hashes exact = true
A artifact/snapshot/duplicate/branch = passed/passed/passed/passed
B artifact/snapshot/duplicate/branch = passed/passed/passed/passed
C artifact/snapshot/duplicate/branch = passed/passed/passed/passed
reset-sensitive identity = lgrc9v3_restoration_identity_v2
```

Fresh A replay reproduces the `0.20` versus `0.10` release split and the later
native `q=0.35` admission split. Fresh B replay reproduces explicit `0.04`
source debit, packet amount, destination credit, conservation, and the later
native admission boundary change. Fresh C.2 replay rederives the relation from
native packet history and reruns the producer/step composition on both formed
and progressed histories. Each C.2 branch now retains its post-transport native
snapshot. Those final states match under restoration identities v1 and v2,
rederive the same post-feedback `S`, and produce the same next candidate-step
result after load. This is the load-bearing C.2 restoration witness for producer
`DR5`; source-state roundtrip alone would have left C.2 at `DR4`.

## Controls

```text
control registry rows resolved = 70
family control-resolution rows = 210
runtime controls executed = 14
inherited schema nulls consumed = 76
positive conformance observations = 30
scope-not-applicable rows = 90
failed_open = 0
frozen I10 registry not_run = 0
deferred conditional C.2 controls are in I10 registry = false
all dependent controls resolved = true
```

The `70` count is registry coverage, not `70` family runtime executions.
`failed_closed` rows consume the exact I3 schema-validator fixture that triggered
the false-positive path; they are not described as family runtime failures.
Positive conformance observations and actually executed runtime controls are
counted separately. `not_applicable` is used only with a family-scope reason.
Candidate C additionally rejects duplicate committed arrivals, ignores lineage
and semantic labels, ignores wrong-direction nonqualifying events, survives
role-preserving topology renumbering, and changes only when physical progression
history changes. C/C.1-specific boundary controls remain non-contributory ancestry.

## Lane Boundary

C.2 is not collapsed into one rung:

```text
carrier/restoration comparison = DR2
producer-mediated mechanism comparison = DR5
native implementation comparison = DR0
```

The DR5 producer result does not naturalize C.2. The deferred packetization,
direct-mediation, multi-cycle, topology-lifecycle, cache, and native readmission
requirements remain outside N31 and were not silently converted into I10 gates.

## Comparative Boundary

I10 does not rank or select A, B, or C.2. I11 must compare semantic meaning,
theory compatibility, conservation, local causality, representation, producer
residue, and naturalization debt. Raw effect sizes are not a valid cross-family
ranking metric. I11 receives three added-mechanism units plus the admitted D0a,
D0b, and D0c rows from I8, for `6`
comparison rows. It must use a multi-axis profile or Pareto classification before
any plural or conditional selection; one scalar score is prohibited.

## Checks

| Check | Passed |
|---|---:|
| `all_exact_I2_I3_I8_I9_sources_consumed` | `true` |
| `all_source_artifact_manifests_replay_exact` | `true` |
| `A_family_all_required_replays_pass` | `true` |
| `A_family_DR5_gates_pass` | `true` |
| `B_family_all_required_replays_pass` | `true` |
| `B_family_DR5_gates_pass` | `true` |
| `C_family_all_required_replays_pass` | `true` |
| `C2_post_feedback_final_state_restoration_witness_exact` | `true` |
| `C_family_candidate_specific_controls_pass` | `true` |
| `C_family_lane_specific_rungs_preserved` | `true` |
| `C_and_C1_retained_as_separate_zero_weight_ancestry` | `true` |
| `complete_frozen_control_matrix_resolved` | `true` |
| `family_bundles_prevent_double_counting` | `true` |
| `I11_comparative_selection_not_preempted` | `true` |
| `src_and_protected_contracts_unchanged` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Ceiling

```text
A, B, and C.2 producer-mediated mechanism families pass bounded I10 replay, restoration, invariant, and control gates at lane-specific DR5, without native or semantic promotion
```

This is not native autonomous decay, a strict current-`C`-only realization of
C.2, a general decay law, memory, stigmergy, communication, ecology, learning,
agency, native support, Phase 8 completion, or automatic RCAE adoption.

## Reproduction

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_added_mechanism_replay_controls_i10.py
```

```text
output_digest = 29314dc62908e445deeb868ad04719dc1c23bd856562ac159098f5a3b081e257
```
