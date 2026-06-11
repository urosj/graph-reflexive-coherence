# N05 Iteration 1 Baseline And Schema Inventory

Generated: `2026-06-04T18:12:28.674935+00:00`

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/build_n05_iteration_1_baseline_inventory.py
```

## Boundary

- N05 is experiment-local.
- No oscillator probes were run.
- `src/*` changes are not required for Iteration 1.
- N04 is background only, not an inherited oscillator or agency claim.
- O-levels are evidence classifications, not claim flags.
- `native_lgrc_agentic_like_dynamics_candidate` remains blocked.

## Source Status

```text
(no src/* status entries)
```

## Native LGRC Surfaces Available For N05

| Surface | Minimum level | N05 use | Claim boundary |
|---|---:|---|---|
| `native_packet_loop_flux_route_producer` | `lgrc2` | O1 delayed outbound packet from declared causal flux routes | scheduling/evidence only |
| `native_packet_loop_route_aspect_surplus_producer` | `lgrc2` | O3-O5 runtime-visible surplus/reservoir-triggered cycles | surplus trigger is not choice, agency, or memory |
| `native_self_rearm_evidence` | `lgrc2` | O4/O5 repeated-cycle and renewal evidence | self-rearm evidence is cycle evidence, not agency |
| `native_causal_pulse_substrate_surface` | `lgrc2` | O2/O3 target contact and local substrate response evidence | surface rows are evidence, not movement or agency claims |
| `surface_lineage_transport` | `lgrc3` | Only if O6 becomes topology-aware | lineage hygiene only |
| `topology_state_reabsorption` | `lgrc3` | Only if O6 consumes topology-mutating route coupling | runtime state/ledger support only |
| `time_scoped_lineage_replay` | `lgrc3` | Artifact replay of topology-aware producer timing if needed | artifact validation only |
| `native_route_arbitration` | `lgrc3` | Candidate O6 route-coupling surface only | route arbitration is not semantic choice |
| `bounded_autonomous_run_loop` | `lgrc2` | O4-O6 bounded producer+step execution | bounded run loop is not agency |
| `snapshot_restore` | `lgrc2` | Snapshot continue-after-load controls | persistence support only |

## O-Ladder Schema

| O-level | Name | Minimum level | Claim ceiling |
|---|---|---:|---|
| `O0` | no oscillation / passive relaxation | `lgrc0_or_synchronous_control` | `no_oscillation` |
| `O1` | delayed outbound pulse | `lgrc2` | `delayed_pulse_candidate` |
| `O2` | reflected return pulse | `lgrc2` | `reflected_pulse_candidate` |
| `O3` | amplified return with reservoir accounting | `lgrc2` | `amplified_return_candidate` |
| `O4` | repeated source-target-source cycle | `lgrc2` | `repeated_oscillator_cycle_candidate` |
| `O5` | self-sustained delayed oscillator boundary | `lgrc2` | `self_sustained_oscillator_candidate` |
| `O6` | route-coupled / trail-reinforced oscillator boundary | `lgrc2_or_lgrc3_if_topology_aware` | `route_coupled_oscillator_candidate` |

Required row fields:

```text
run_id
o_level
o_level_is_evidence_classification
claim_ceiling
claim_flags
runtime_family
lgrc_runtime_level
execution_stage
scheduling_mode
producer_mediated
constitutive_native_claim_allowed
source_native_surfaces
fixture_id
source_node_id
target_node_id
route_id
event_time_key
scheduler_event_index
causal_epoch
node_proper_time
source_node_proper_time
target_node_proper_time
outbound_packet_id
outbound_packet_digest
outbound_amount
target_reservoir_before
target_reservoir_after
return_packet_id
return_packet_digest
return_amount
cycle_id
causal_delay
scheduler_order
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
producer_records
cycle_semantics
scheduling_semantics
amplification_accounting
route_coupling
artifact_only_replay
blocked_claims
```

Cycle definition:

```text
outbound_departure -> target_contact -> return_eligibility -> return_packet -> source_contact_absorption
```

Plateau samples counted as cycles: `false`.

## Claim Flags

```json
{
  "agency_claim_allowed": false,
  "agentic_like_claim_allowed": false,
  "ant_colony_claim_allowed": false,
  "biological_claim_allowed": false,
  "goal_proxy_regulation_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "memory_or_trail_claim_allowed": false,
  "movement_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "semantic_choice_claim_allowed": false,
  "unrestricted_movement_claim_allowed": false
}
```

## Source Summaries

```json
{
  "n03_e3": {
    "classification": "n03_native_lgrc9v3_packet_loop_reproduced",
    "movement_claim_allowed": false,
    "native_lgrc9v3_execution": true,
    "native_self_rearm_evidence": true,
    "native_surplus_trigger": true,
    "snapshot_telemetry_replayable": true,
    "status": "passed"
  },
  "n04": {
    "achieved_movement_level": "M6",
    "agency_claim_allowed": false,
    "current_ceiling": "topology_mutating_movement_candidate",
    "movement_claim_allowed": false,
    "native_route_arbitration_supported": true,
    "semantic_choice_claim_allowed": false,
    "status": "passed",
    "time_scoped_lineage_replay_supported": true,
    "topology_state_reabsorption_supported": true
  }
}
```

## Artifact Inventory

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
| `n05_readme` | `True` | `96c82b3f49ef643934248b13992aa1bd3b9ca84e7d4c0c925268aa95097917b7` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/README.md` |
| `n05_n11_roadmap` | `True` | `eb997dc4322b607e238810d6f29f7eecf76d942a1f625c4846436a801e32f4c0` | `experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md` |
| `n05_plan` | `True` | `4c2bb7835006c8a298c4795553bfbd62cf5091d6df10b91d5361cfdd242c38a3` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/implementation/CoherenceOscillatorsImplementationPlan.md` |
| `n05_checklist` | `True` | `99fab63edd77d6b728f9d972efbb7174b6a26e6e86e56f1b9fe6f2bde378c84e` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/implementation/CoherenceOscillatorsImplementationChecklist.md` |
| `n03_d2_3_self_rearming_packets` | `True` | `0a868b5e2155d48c9bf38670c705a4726c9b87b053f69af5d1f61737eb262c68` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/d2_3_self_rearming_packets.json` |
| `n03_e2_4_native_autonomy_feasibility` | `True` | `fbcf1095c85d59f46f64beaafd79a42473283e0a75065d7157b9b3c7336b6552` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e2_4_native_autonomy_feasibility.json` |
| `n03_e2_4a_native_autonomy_boundary` | `True` | `4ae1db5daf245cad05713ebe80b7e912c6d4c9b4d24ff552e07cf3360ecb1cdb` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e2_4a_native_autonomy_boundary.json` |
| `n03_e3_route_manifest` | `True` | `12c9cd933e3209dca2fdc78eeccad84644477a206c72901bbda9b1858c66cd0f` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/configs/e3_native_lgrc9v3_packet_loop_route_manifest.json` |
| `n03_e3_positive` | `True` | `e421e11a15fba7c7df6c7483b5a026b3afe1b3a83f2d948060ba357f24c14dc7` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_1_native_positive_reproduction.json` |
| `n03_e3_controls` | `True` | `4a037ccd1ba375ba1e867d41ce95cdf26f8b780477c95dc090676c24942b889b` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_2_native_control_parity.json` |
| `n03_e3_snapshot_telemetry` | `True` | `e03cc3d813a11d502742e91520cb17d13061201226fa9c1997e08b31ded3fd9a` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_3_snapshot_telemetry_reproduction.json` |
| `n03_e3_closeout` | `True` | `75e02858f32484a8c4e9a24d9751c0ce98e4ef603fd6e550d8a47f7466e2288e` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json` |
| `n03_e3_closeout_report` | `True` | `92c697eb444168ae1182b481ed0fbe10671892b341dc078f57d2f2944aa15c8d` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md` |
| `n04_baseline_inventory` | `True` | `15e9da40be95289dc25882499863c542672cad0664315bbf1ac36f8f9ab7e3eb` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_baseline_inventory.json` |
| `n04_e3_pulse_import_validation` | `True` | `9f50510dfa4b0a393151ab7f5eab0e79677f0fb23bb699b9bec37e64ae6bb4bb` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/e3_pulse_import_validation.json` |
| `n04_lane_f_surface_bridge` | `True` | `0c88c5e5696169bda153e2d5ed1735e0d7d1f3b3a06bbb54cff8d9e23b8f2655` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_lgrc_lane_f_surface_bridge.json` |
| `n04_lane_f_surface_closeout` | `True` | `1641543e8132af1a474c30bd6f90bd669cbb666a88df2fce55fc6982b0fa5169` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_f_native_surface_closeout.json` |
| `n04_taxonomy_continuation_closeout` | `True` | `36a96f188b2d0d32ee7d8840305bec34554b54de68f46c433f96271c2c53d780` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json` |
| `n04_route_arbitration_rerun` | `True` | `4d28f1fa0d2822de374d09ae20927eac6c682c112b7434254010890c059694c1` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json` |
| `phase8_lgrc9_closeout` | `True` | `29fe44ad6fcda5918d92289dc1d6f6c7cf38c742b73eb8e66d0f78bdd1d8df28` | `implementation/Phase-8-LGRC9-Closeout.md` |
| `phase8_native_packet_loop_checklist` | `True` | `76fd55a330b9dd1fe5347c12fbd6210153de85e172352746d5cc331500d05324` | `implementation/Phase-8-LGRC9-NativePacketLoopChecklist.md` |
| `phase8_causal_pulse_substrate_closeout` | `True` | `63cd7a332be71701896d29f054aaab36fc83bad0a207255d04e40062cd5541ff` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.md` |
| `phase8_causal_pulse_substrate_closeout_json` | `True` | `2c2b1171c31cc8ad4bcc4373d6a8a04f94865714707d7f9924066ce7e3feb2e2` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json` |
| `phase8_surface_lineage_closeout` | `True` | `e623455570a496776d90605d1fc84c68ce3c83264637433d47fff66362cb3de5` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md` |
| `phase8_surface_lineage_closeout_json` | `True` | `97ad2e56ba6f2b2b303070dcbc4eb16ee54a5267c4911269abb664f35571709f` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json` |
| `phase8_topology_state_reabsorption_closeout` | `True` | `b9c9bbb4756bedb4469029649a431ae638d4adec3c04daf3cb480fc7b8c2305c` | `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md` |
| `phase8_topology_state_reabsorption_closeout_json` | `True` | `7db33f5c04b34e3046ebbfda523a245c1b8dd80457e6fdf3a158dae1a6ecac31` | `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json` |
| `phase8_time_scoped_lineage_replay_closeout` | `True` | `e1490f0792a27a25fe36b0f6cbba596b344061dec42621d8612a425aa2cd0a6f` | `implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md` |
| `phase8_time_scoped_lineage_replay_closeout_json` | `True` | `26a291a3fe17432b55e5da1fea22db950508c71ad4effe83346c09e6ee050201` | `implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json` |
| `phase8_native_route_arbitration_closeout` | `True` | `1d3166a3ca4b08cf88aa50b6054782442e7739b11eb2d2e7157c0581d830292c` | `implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.md` |
| `phase8_native_route_arbitration_closeout_json` | `True` | `cabc1f5b81fdb19154d778b04463f74f32e82653db6291daa62b1e5128d01b65` | `implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json` |

## Acceptance

Iteration 1 passes because N05 has a source-backed baseline
inventory, frozen O-ladder row schema, explicit blocked claim
flags, and no oscillator probe evidence or claim promotion.
