# N05 Coherence Waves And Oscillators Implementation Checklist

This checklist tracks implementation of
`2026-05-N05-lgrc-coherence-waves-oscillators`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N05 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N04 as movement/topology-mutating baseline only.
- [ ] Treat N05 as oscillator/circuit evidence only.
- [ ] Keep producer scheduling labeled as scheduling/evidence, not agency.
- [ ] Keep `step()` as the mutation boundary.
- [ ] Preserve node-plus-packet budget accounting for every run.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Record SHA-256 digests for positive fixture artifacts.
- [ ] Keep all claim flags false unless a later experiment separately validates them.

## Iteration 0. Planning And Handoff

Status: Complete.

- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Record N04 inherited ceiling:
  `topology_mutating_movement_candidate`.
- [x] Record that N05 does not prove choice, identity, memory, regulation,
  ACO, agency, or locomotion.
- [x] Record Phase 3 native-policy caveat.
- [x] Link plan/checklist from implementation README.

Acceptance statement:

```text
N05 starts from a clean claim boundary: N04 supplies movement/topology-mutating
baseline context, while N05 opens only coherence-wave and oscillator evidence.
Producer-mediated probes are allowed as scheduling/evidence mechanisms, but
pure-native oscillator claims require existing serialized LGRC policy support.
```

## Iteration 1. Baseline And Schema Inventory

Status: Complete.

- [x] Inventory N03/N04/Phase 8 source artifacts that may be cited.
- [x] Inventory available native LGRC surfaces:
  - [x] native packet-loop route-aspect contract
  - [x] `LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE`
  - [x] `LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS`
  - [x] `LGRC9V3.set_route_aspect_surplus_trigger(...)`
  - [x] `LGRC9V3.run_autonomous(...)`
  - [x] native self-rearm evidence and
    `validate_lgrc9v3_self_rearm_evidence_artifacts(...)`
  - [x] native causal pulse-substrate surface and
    `validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(...)`
  - [x] surface lineage transport
  - [x] topology-state reabsorption
  - [x] time-scoped lineage replay
  - [x] native route arbitration
  - [x] native snapshot restore through `LGRC9V3.load(...)`
- [x] Inventory the N05-N11 roadmap.
- [x] Freeze O-ladder row schema.
- [x] Freeze blocked claim flags:
  - [x] `movement_claim_allowed = false`
  - [x] `semantic_choice_claim_allowed = false`
  - [x] `agency_claim_allowed = false`
  - [x] `rc_identity_collapse_claim_allowed = false`
  - [x] `identity_acceptance_claim_allowed = false`
  - [x] `memory_or_trail_claim_allowed = false`
  - [x] `goal_proxy_regulation_claim_allowed = false`
  - [x] `agentic_like_claim_allowed = false`
  - [x] `locomotion_like_claim_allowed = false`
  - [x] `biological_claim_allowed = false`
  - [x] `ant_colony_claim_allowed = false`
  - [x] `unrestricted_movement_claim_allowed = false`
- [x] Define `coherence_oscillator_report_v1`.
- [x] Define baseline JSON row schema for O0-O6 evidence.
- [x] Require every row to include:
  - [x] `o_level`
  - [x] `o_level_is_evidence_classification = true`
  - [x] `claim_ceiling`
  - [x] `claim_flags`
  - [x] `lgrc_runtime_level`
  - [x] `source_native_surfaces`
  - [x] `event_time_key`
  - [x] `scheduler_event_index`
  - [x] `causal_epoch`
  - [x] `node_proper_time` where available
  - [x] `scheduling_mode`
  - [x] `producer_mediated`
  - [x] `constitutive_native_claim_allowed`
  - [x] `cycle_semantics`
  - [x] `scheduling_semantics`
  - [x] `claim_boundary`
- [x] Verify no oscillator probes are run in this iteration.
- [x] Verify no `src/*` changes are needed.

Expected artifacts:

- [x] `outputs/n05_iteration_1_baseline_inventory.json`
- [x] `reports/n05_iteration_1_baseline_inventory.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/build_n05_iteration_1_baseline_inventory.py
```

Result:

```json
{"oscillator_probe_run": false, "output": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_1_baseline_inventory.json", "report": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_1_baseline_inventory.md", "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_1_baseline_inventory.json
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- `git status --short src` returned no `src/*` status entries.
- `git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators`
  passed.
- N03/E3 native packet-loop support is inventoried as oscillator substrate
  evidence only, not agency, choice, memory, or locomotion evidence.
- N04 is inventoried as background at
  `topology_mutating_movement_candidate`; no N04 claim is inherited by N05.
- Native route arbitration is inventoried as possible O6 route-coupling
  support only, not semantic choice.

Acceptance statement:

```text
Iteration 1 passes if N05 has a source-backed baseline inventory, frozen
O-ladder row schema, explicit blocked claim flags, and no new probe evidence or
claim promotion.
```

## Iteration 2. Fixture Manifest And Controls

Status: Complete.

- [x] Define minimal source-target-reservoir fixture.
- [x] Decide fixture reuse strategy:
  - [x] reuse N03 E3 clockwise/counter-clockwise route fixtures as prior art
  - [x] adapt N04 boundary/pulse-substrate fixtures as control precedent
  - [x] define new N05 source-target-reservoir fixture
- [x] Define source node, target node, and route ids.
- [x] Define source reservoir and target reservoir accounting.
- [x] Define outbound and return delay policy.
- [x] Freeze cycle definition:
  `outbound_departure -> target_contact -> return_eligibility -> return_packet -> source_contact_absorption`.
- [x] Define plateau/sample dedup rule:
  repeated samples from one persistent contact plateau do not count as
  distinct cycles.
- [x] Define node-plus-packet budget tolerance.
- [x] Declare conservative LGRC defaults:
  - [x] lapse policy
  - [x] edge delay policy
  - [x] symmetric delay policy
  - [x] packetized causal flux representation
  - [x] packet/pending-flux ledger representation
- [x] Define default-off policy behavior.
- [x] Define producer policy fields for Phase 1/2 probes.
- [x] Define Phase 3 native-policy support-audit fields.
- [x] Define negative controls:
  - [x] policy disabled
  - [x] pulse disabled
  - [x] missing source
  - [x] missing target
  - [x] missing route
  - [x] hidden schedule
  - [x] hidden reservoir
  - [x] budget ambiguity
  - [x] stale producer read
  - [x] idempotent duplicate production
  - [x] snapshot continue-after-load
  - [x] producer mutation attempt
  - [x] claim promotion attempt
- [x] Add fixture/manifest validator.
- [x] Record validator command and output.

Expected artifacts:

- [x] `configs/n05_fixture_manifest_v1.json`
- [x] `outputs/n05_iteration_2_fixture_manifest_validation.json`
- [x] `reports/n05_iteration_2_fixture_manifest_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/validate_n05_fixture_manifest.py
```

Result:

```json
{"oscillator_probe_run": false, "output": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_2_fixture_manifest_validation.json", "report": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_2_fixture_manifest_validation.md", "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/configs/n05_fixture_manifest_v1.json
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_2_fixture_manifest_validation.json
git status --short src
```

Notes:

- `git status --short src` returned no `src/*` status entries.
- The selected fixture strategy is a new N05 source-target-reservoir chain,
  with N03 E3 and N04 pulse-substrate artifacts used as prior art only.
- The target reservoir is an ordinary declared runtime node, not a hidden
  fixture array.
- Post-review hardening added explicit O-level to LGRC-level/claim-ceiling
  mapping, native route-aspect/surplus/self-rearm/run-autonomous cross
  references, and LGRC timing vocabulary to the manifest validator.
- General review hardening added explicit
  `positive_o_level_evidence_generated = false`, fixture-role non-semantic
  boundaries, and nonnegative visible reservoir/node coherence validation.
- The validator records distinct blockers for hidden schedule, hidden
  reservoir, budget ambiguity, stale producer read, duplicate production,
  producer mutation, and claim-promotion controls.
- No oscillator probe was run and all N05 claim flags remain false.

Acceptance statement:

```text
Iteration 2 passes if N05 fixtures, policies, budget surfaces, and controls are
declared before oscillator probes, and invalid hidden schedules, hidden
reservoirs, ambiguous budgets, producer mutation, and claim-promotion attempts
fail closed.
```

## Iteration 3. O1 Delayed Outbound Pulse

Status: Complete.

- [x] Run default-off lane and verify no outbound packet is emitted.
- [x] Run enabled O1 lane.
- [x] Emit one outbound pulse chain from committed source evidence.
- [x] Prefer existing flux-route producer:
  `LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE`.
- [x] Verify causal delay and scheduler ordering.
- [x] Record `event_time_key`, `scheduler_event_index`, and proper-time fields
  where available.
- [x] Verify outbound packet id and digest are recorded.
- [x] Verify node-plus-packet budget remains exact.
- [x] Verify producer records are scheduling/evidence only.
- [x] Record `scheduling_mode = explicit_schedule|runtime_threshold`.
- [x] Record `producer_mediated` and `constitutive_native_claim_allowed`.
- [x] Verify `step()` processes packet mutation.
- [x] Verify artifact-only replay reconstructs source -> outbound packet ->
  target-contact chain.
- [x] Run negative controls for missing source, missing route, hidden schedule,
  budget mismatch, producer mutation, and claim promotion.

Expected artifacts:

- [x] `outputs/n05_iteration_3_o1_delayed_outbound_pulse.json`
- [x] `reports/n05_iteration_3_o1_delayed_outbound_pulse.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_3_o1_delayed_outbound_pulse.py
```

Result:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_ceiling": "delayed_pulse_candidate", "controls_passed": true, "o_level": "O1", "packet_events": 4, "row_schema_passed": true, "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_3_o1_delayed_outbound_pulse.json
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- `git status --short src` returned no `src/*` status entries.
- The positive O1 lane uses one outbound source-to-target pulse chain over the
  declared two-hop route. LGRC emits one native packet per hop; hop 2 is
  configured only after the committed hop 1 arrival.
- The packet chain is:
  `0 -> 1` departure/arrival followed by `1 -> 2` departure/arrival.
- The final target-contact packet is
  `lgrc9v3-packet-aee1863b655fbd5a`; the final target-contact event is
  `lgrc9v3-packet-event-39c554bb549d6020`.
- Post-review schema hardening added `causal_epoch = post_update` to the O1
  row and to each processed packet event.
- The positive row now records the frozen-schema O1 non-applicable fields:
  `return_packet_id = null`, `return_packet_digest = null`,
  `return_amount = null`, and `cycle_id = null`.
- The positive row records the declared target reservoir as unchanged:
  `target_reservoir_before = 0.5`, `target_reservoir_after = 0.5`.
- The singular frozen-schema `outbound_packet_id`/`outbound_packet_digest`
  fields use the terminal target-contact packet for the multi-hop O1 chain;
  the plural `outbound_packet_ids`/`outbound_packet_digests` preserve every
  native hop packet.
- The `pulse_disabled` control is explicitly scoped as a
  manifest/policy-gate check in O1. O1 has no separate runtime pulse surface;
  packet emission is gated by the existing flux-route producer policy.
- Artifact digests recorded in the output:
  `positive_lane_digest = 5905dd6d2f17abc59302255e19f3f6db21d7982caf452c128467b54f0c8db71e`,
  `producer_records_digest = 5c6f40564e82aeb03602b1f13d16bec8d54c303c093613af22351ddb1dd053d4`,
  `processed_packet_events_digest = 9c53688f59634750f7fa8a7ac2297f12edde5d4e9e0f395cd3f25c3bd73686e2`.
- Producers enqueue scheduled packet work only; `step()` processes departure
  and arrival mutation.
- Implementation boundary:
  - Existing LGRC9V3 provides the packet producer, packet queue,
    `step()` mutation, event timing, and node-plus-packet budget ledger.
  - The N05 experiment runner provides only fixture declaration, route-hop
    sequencing, artifact/report generation, controls, and O-level
    classification.
  - No new LGRC runtime mechanism or native oscillator policy is added in
    Iteration 3.
  - If LGRC later needs to treat a multi-hop source-target pulse as one native
    oscillator operation without experiment-local hop sequencing, that is a
    separate Phase 8/core task.
- O1 remains a delayed-pulse evidence classification only. All movement,
  semantic choice, agency, identity, memory/trail, regulation, agentic-like,
  locomotion-like, biological, ACO, and unrestricted movement claim flags
  remain false.

Acceptance statement:

```text
Iteration 3 passes if O1 delayed outbound pulse evidence is emitted only when
policy is enabled, is ordered and budget-valid, replays from artifacts, and
does not mutate state through producers or promote claims.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "producer_mutation_blocked": true, "row_schema_passed": true, "status": "passed"}
```

## Iteration 4. O2 Reflected Return Pulse

Status: Complete.

- [x] Require committed outbound arrival or target-contact evidence.
- [x] Prefer native causal pulse-substrate surface rows for target-contact
  evidence where available.
- [x] Emit return packet linked to outbound event.
- [x] Verify outbound-return lineage fields.
- [x] Verify return packet id and digest are recorded.
- [x] Verify scheduler order:
  `outbound departure -> target contact -> return eligibility -> return packet`.
- [x] Verify return is not emitted from hidden fixture timing.
- [x] Record scheduling semantics and claim-boundary fields.
- [x] Verify node-plus-packet budget remains exact.
- [x] Verify artifact-only replay reconstructs outbound -> contact -> return.
- [x] Run stale outbound, missing contact, hidden schedule, budget mismatch,
  producer mutation, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n05_iteration_4_o2_reflected_return_pulse.json`
- [x] `reports/n05_iteration_4_o2_reflected_return_pulse.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_4_o2_reflected_return_pulse.py
```

Result:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_ceiling": "reflected_pulse_candidate", "controls_passed": true, "o_level": "O2", "packet_events": 8, "row_schema_passed": true, "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_4_o2_reflected_return_pulse.json
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- `git status --short src` returned no `src/*` status entries.
- O2 remains Stage 1 explicit scheduling over existing LGRC9V3 packet
  producer and `step()` mechanics. No new LGRC runtime mechanism or native
  oscillator policy is added.
- `source_native_surfaces` is limited to actual LGRC mechanisms:
  `LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE` and
  `LGRC9V3.step`. The committed packet-arrival target contact is recorded as
  `target_contact_evidence.evidence_kind`, not as a native surface constant.
- Target-contact evidence is the committed LGRC9V3 packet-arrival event
  `lgrc9v3-packet-event-39c554bb549d6020`, with digest
  `19b5e94f09fd1f3fa5a380b28b9b6827fb6c6fb8cccfc0f8e965c1da9ab69346`.
  Native causal pulse-substrate surface rows are not enabled for this lane.
- The return eligibility record is
  `n05-o2-return-eligibility-19b5e94f09fd1f3fa5a380b2` and requires the
  committed target-contact event before return scheduling.
- Packet chain:
  `0 -> 1 -> 2` outbound, then `2 -> 1 -> 0` return.
- Scheduler order is `[1, 2, 3, 4, 5, 6, 7, 8]`; event-time order is
  `[0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0]`.
- The terminal return source-contact packet is
  `lgrc9v3-packet-3e430fa14f438186`; the source-contact event is
  `lgrc9v3-packet-event-daaf47b678a56237`.
- Artifact digests recorded in the output:
  `positive_lane_digest = 40813fb7acc824194f18a97d5e1cc0ff59f4b55a548df3411170daebf775d091`,
  `producer_records_digest = 76bb453df37b112efc988a00303750814da69b968df93232de31344ea0db8d4a`,
  `processed_packet_events_digest = f34c46c0a073a197354ec7df18d3a0dfa3ac2a4623ec2ac7c781b7fe17776f85`,
  `return_eligibility_digest = 23adc9a6f98f2c4719ac8e4edf182f115c59899135298366a0e0d442f0cdd389`.
- Controls passed with distinct blockers:
  `n05_policy_disabled_noop`, `n05_missing_target_contact`,
  `n05_stale_outbound_contact`, `n05_hidden_return_schedule_rejected`,
  `n05_node_plus_packet_budget_mismatch`,
  `n05_producer_mutation_boundary_violation`, and
  `n05_claim_promotion_rejected`.
- Post-review clarification: `missing_contact` and `stale_outbound` are
  structural validator/linkage controls, not independent runtime replay lanes.
  They prove the return eligibility record cannot validate without the
  committed target-contact event digest.
- O2 remains a reflected-return evidence classification only. It does not
  promote amplified return, repeated-cycle oscillator, self-sustained
  oscillator, memory/trail, choice, agency, movement, locomotion-like,
  biological, ACO, or unrestricted movement claims.

Acceptance statement:

```text
Iteration 4 passes if O2 return evidence is causally linked to committed
outbound target-contact evidence, remains budget-valid, rejects hidden return
timing, and replays from artifacts without claim promotion.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "producer_mutation_blocked": true, "return_linkage_ok": true, "row_schema_passed": true, "status": "passed"}
```

## Iteration 5. O3 Amplified Return With Reservoir Accounting

Status: Complete.

- [x] Declare target reservoir or boundary/surplus source.
- [x] Map reservoir to runtime-visible source:
  - [ ] source node observed mass above serialized reference mass
  - [x] target node declared stored coherence released by policy
  - [ ] route-aspect surplus trigger observed/reference mass
- [x] Record `amplification_source_kind`.
- [x] Record `reservoir_runtime_visible = true`.
- [x] Record `reservoir_hidden_array_used = false`.
- [x] Record reservoir before and after target interaction.
- [x] Record `return_excess_debited`.
- [x] Allow return amount greater than outbound amount only when excess is
  debited from declared reservoir.
- [x] Verify no silent amplification occurs.
- [x] Verify node-plus-packet plus reservoir accounting is exact.
- [x] Verify reservoir source is serialized and runtime-visible.
- [x] Verify artifact-only replay reconstructs amplification accounting.
- [x] Run hidden reservoir, undeclared source, budget mismatch, negative
  reservoir, producer mutation, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n05_iteration_5_o3_amplified_return.json`
- [x] `reports/n05_iteration_5_o3_amplified_return.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_5_o3_amplified_return.py
```

Result:

```json
{"amplification_accounting_ok": true, "artifact_replay_passed": true, "budget_error": 0.0, "claim_ceiling": "amplified_return_candidate", "controls_passed": true, "o_level": "O3", "row_schema_passed": true, "status": "passed"}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_5_o3_amplified_return.json
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- `git status --short src` returned no `src/*` status entries.
- O3 remains Stage 1 explicit scheduling over existing LGRC9V3 packet
  producer and `step()` mechanics. No new LGRC runtime mechanism or native
  oscillator policy is added.
- The positive lane uses the declared target reservoir node `3` as the
  amplification source. `amplification_source_kind = target_reservoir` follows
  the plan enum, while `amplification_source_detail =
  declared_target_reservoir_node` preserves the more specific implementation
  detail. Source-node surplus and route-aspect surplus trigger alternatives
  were not used in this lane.
- The outbound target-contact event is
  `lgrc9v3-packet-event-39c554bb549d6020`, with digest
  `19b5e94f09fd1f3fa5a380b28b9b6827fb6c6fb8cccfc0f8e965c1da9ab69346`.
- The reservoir release route is
  `n05_o3_declared_target_reservoir_release_route_v1`, serialized in the O3
  artifact, and releases `0.25` from reservoir node `3` to target node `2`.
- Return amount is `0.5`; outbound amount is `0.25`; return excess is `0.25`.
  The excess is exactly debited from the reservoir:
  `target_reservoir_before = 0.5`,
  `target_reservoir_after_release = 0.25`,
  `target_reservoir_after = 0.25`.
  The artifact also records plan-aligned aliases
  `reservoir_budget_before = 0.5` and `reservoir_budget_after = 0.25`.
- Packet chain:
  `0 -> 1 -> 2` outbound, `3 -> 2` reservoir release, then
  `2 -> 1 -> 0` amplified return.
- Scheduler order is `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`; event-time order is
  `[0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0, 5.0]`.
- Artifact replay reconstructs outbound contact, reservoir release, amplified
  return, and the reservoir-debit accounting without runtime state.
- Artifact digests recorded in the output:
  `positive_lane_digest = a81bac4111ec6061dde395104724a87195022d8b7d53665ef9c805a3c87b0878`,
  `producer_records_digest = f184f8827e482d69d1e64fb1945b0f9853777e3321ce264f65847f1aa4f7fb3c`,
  `processed_packet_events_digest = 4038e1e4639a7f6c2c03c570fa4c3644481374a0d9d974b8034bfea93f502b40`,
  `reservoir_release_policy_digest = 18da358fddf64ac60f336f48b446833f74c96ea9629be87f2b8adebb84fd1bd6`,
  `return_eligibility_digest = 22502654d461a15fa8300fcfe00fd44d99aedad765321e390105f19d100c8e96`.
- Controls passed with distinct blockers:
  `n05_policy_disabled_noop`, `n05_hidden_reservoir_rejected`,
  `n05_undeclared_reservoir_source`,
  `n05_node_plus_packet_budget_mismatch`,
  `n05_negative_reservoir_rejected`,
  `n05_silent_amplification_rejected`,
  `n05_producer_mutation_boundary_violation`, and
  `n05_claim_promotion_rejected`.
- Post-review clarification: O3 records shared controls not rerun in this lane
  as `deferred_shared_controls`: `missing_target`, `missing_route`,
  `stale_producer_read`, `idempotent_duplicate_production`, and
  `snapshot_continue_after_load`. These are not blocking for O3 because this
  lane ran the O3-specific reservoir and amplification controls plus shared
  policy/budget/producer/claim controls.
- O3 remains an amplified-return evidence classification only. It does not
  promote repeated-cycle oscillator, self-sustained oscillator, memory/trail,
  choice, agency, movement, locomotion-like, biological, ACO, or unrestricted
  movement claims.

Acceptance statement:

```text
Iteration 5 passes if O3 amplified return is explained by declared reservoir or
boundary/surplus accounting, rejects silent amplification, preserves budget,
and emits no choice, agency, identity, memory, ACO, or locomotion claims.
```

Acceptance result: Achieved.

Confirmation:

```json
{"amplification_accounting_ok": true, "artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "producer_mutation_blocked": true, "reservoir_debit_matches_return_excess": true, "row_schema_passed": true, "status": "passed"}
```

## Iteration 6. O4 Repeated Source-Target-Source Cycle

Status: Complete.

- [x] Run at least two complete outbound-return cycles.
- [x] Use `LGRC9V3.run_autonomous(...)` for bounded repeated-cycle lanes unless
  explicitly scoped otherwise.
- [x] Validate native self-rearm evidence where applicable with
  `validate_lgrc9v3_self_rearm_evidence_artifacts(...)`.
- [x] Assign distinct cycle ids.
- [x] Verify each cycle is authorized by the same declared policy.
- [x] Verify cycles are not preauthored as a hidden event list.
- [x] Verify duplicate suppression for repeated producer eligibility.
- [x] Verify node-plus-packet budget remains exact across all cycles.
- [x] Verify artifact-only replay reconstructs every cycle.
- [x] Verify cycle count semantics distinguish repeated cycles from repeated
  samples of one plateau.
- [x] Verify `plateau_samples_counted_as_cycles = false`.
- [x] Run hidden schedule, duplicate packet, stale cycle, budget drift,
  producer mutation, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n05_iteration_6_o4_repeated_cycle.json`
- [x] `reports/n05_iteration_6_o4_repeated_cycle.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_6_o4_repeated_cycle.py
```

Result:

```json
{"claim_ceiling": "repeated_oscillator_cycle_candidate", "cycle_count": 2, "o_level": "O4", "output": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_6_o4_repeated_cycle.json", "report": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_6_o4_repeated_cycle.md", "row_schema_passed": true, "status": "passed"}
```

Artifact digests:

```json
{
  "artifact_replay_digest": "40e05090c9b95a7cdb941bcfb643c5ced296f2b807fc0247688e5a768363c0df",
  "cycle_records_digest": "5790a041aeaa6dcca34e8f85eaafd5fb0fa75f01c657f3e32c4c93e0a3146a59",
  "positive_lane_digest": "11cf7ff5b3350a351d17a0fbe2c5f2263305ac85d767333be61a7845f8a535a8",
  "processed_packet_events_digest": "af581e62ec80324d6a9733d4901bb1e04b3f393e8239e767acd7c4c199df138e",
  "producer_records_digest": "26f53748842c4371a09ee8fd0303fee13d855543bd6b88f626c1600921c1d901"
}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_6_o4_repeated_cycle.json
.venv/bin/python -c "import json; p='experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_6_o4_repeated_cycle.json'; d=json.load(open(p)); lane=d['positive_lane']; assert d['status']=='passed'; assert lane['cycle_semantics']['distinct_cycle_count']==2; assert lane['cycle_semantics']['plateau_samples_counted_as_cycles'] is False; assert lane['run_autonomous_used'] is True; assert lane['native_self_rearm_validator']['used'] is False; assert d['artifact_replay']['passed'] is True; assert d['controls']['all_controls_passed'] is True; assert lane['node_plus_packet_budget_error']==0.0; assert lane['duplicate_suppression']['packet_event_ids_unique'] is True; assert lane['duplicate_suppression']['packet_ids_repeat_across_departure_arrival_events'] is True; assert lane['amplification_accounting']['reservoir_exhausted_after_recorded_cycles'] is True; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'cycle_count': lane['cycle_semantics']['distinct_cycle_count'], 'budget_error': lane['node_plus_packet_budget_error'], 'artifact_replay': d['artifact_replay']['passed'], 'controls': d['controls']['all_controls_passed'], 'packet_event_ids_unique': lane['duplicate_suppression']['packet_event_ids_unique']})"
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- O4 uses bounded `LGRC9V3.run_autonomous(...)` segments per declared route
  hop. Cycle ids are serialized into the route evidence, so the second cycle is
  a distinct runtime-visible producer opportunity rather than a duplicate
  replay of the first cycle.
- Native self-rearm artifact validation is not applicable to this O4 lane: O4
  repeats explicit source-target-source cycle segments. The self-rearm
  validator remains reserved for O5 renewal, where the next cycle must be
  authorized by committed circuit state instead of explicit cycle-route
  configuration.
- Duplicate packet control verifies same-state producer duplicate suppression
  with primary blocker `n05_duplicate_cycle_packet_suppressed`.
- Packet event ids are unique across the 20 emitted packet events. Packet ids
  intentionally repeat across each packet's departure and arrival event, so O4
  records `packet_ids_repeat_across_departure_arrival_events = true` and
  `distinct_packet_count = 10`.
- Stale cycle control corrupts the second cycle's source-contact authorization
  and fails artifact replay with primary blocker
  `n05_stale_cycle_authorization_rejected`.
- Lane-level `causal_delay = 10.0` is explicitly the total elapsed event time
  across the recorded two-cycle set; per-cycle causal delays are `[5.0, 5.0]`.
- The declared target reservoir is exhausted after the two recorded cycles
  (`0.5 -> 0.0`), so a third cycle without replenishment is not claimed.
- `git status --short src` returned no `src/*` status entries.
- `git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators`
  passed.

Acceptance statement:

```text
Iteration 6 passes if O4 repeated-cycle evidence contains at least two distinct
source-target-source cycles under one declared policy, with exact budget,
duplicate suppression, artifact replay, and no hidden preauthored schedule.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "controls_passed": true, "cycle_count": 2, "plateau_samples_counted_as_cycles": false, "row_schema_passed": true, "status": "passed"}
```

## Iteration 7. O5 Self-Sustained Oscillator Boundary

Status: Complete.

- [x] Define runtime-visible trigger criteria for the next cycle.
- [x] Record `run_autonomous_stop_condition`.
- [x] Distinguish `max_events_reached` from natural exhaustion with no
  schedulable producer work and empty queues.
- [x] Record `o5_mode`:
  `threshold_authorized|producer_mediated|constitutive_native|native_policy_gap`.
- [x] Verify cycle renewal depends on committed circuit state.
- [x] Verify renewal does not come from a preauthored event list.
- [x] Verify producers, if present, only observe/record/schedule.
- [x] Verify `step()` remains the only mutation boundary.
- [x] Run disabled-trigger, subthreshold, wrong-state, hidden event-list,
  producer mutation, budget drift, and claim-promotion controls.
- [x] Run Phase 3 native-policy support audit:
  - [x] custom node potentials support
  - [x] potential inversion support
  - [x] flux-facilitated metric map support
  - [x] delayed passive response support
  - [x] route conductance memory support
- [x] If current LGRC lacks required native policy support, record blocker
  instead of claiming pure-native oscillator dynamics.
- [x] Record:
  - [x] `native_constitutive_oscillator_supported`
  - [x] `native_policy_blocker`
  - [x] `constitutive_native_claim_allowed`

Expected artifacts:

- [x] `outputs/n05_iteration_7_o5_self_sustained_boundary.json`
- [x] `reports/n05_iteration_7_o5_self_sustained_boundary.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_7_o5_self_sustained_boundary.py
```

Result:

```json
{"claim_ceiling": "self_sustained_oscillator_candidate", "native_constitutive_oscillator_supported": false, "o5_mode": "producer_mediated", "o_level": "O5", "output": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_7_o5_self_sustained_boundary.json", "report": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_7_o5_self_sustained_boundary.md", "row_schema_passed": true, "self_rearm_cycle_count": 3, "status": "passed"}
```

Artifact digests:

```json
{
  "artifact_replay_digest": "d2d06e240fd432b8131c169a0c0a9310d79a1545de6b54577f0e78320a6570a1",
  "cycle_records_digest": "accd808bd7531750146999a0f68ea298fcd762b606f8766ac1e2653ad21528f1",
  "phase3_native_policy_support_audit_digest": "fd6dbb8ff7694a5353d055c57101ab639f6e7bf29593341fef1637dd8cdfba8e",
  "positive_lane_digest": "4074a7ea25e6f1a007d62b1191ac401f274fc0a4db02aa1007700fa06ee67098",
  "processed_packet_events_digest": "58f8a47f61c7edbcc3accaf88a899db921f053d6793ec61e4fe614657cfa61d4",
  "producer_records_digest": "837d6a0297b43a8d11dd424a55b942f9c5161952842af34319d4c8a1d7f5d127",
  "self_rearm_events_digest": "1133eb5b03647cf8bcf21b7b142a17658310568f25718dbbecdc3e4f8f376c92",
  "snapshot_events_digest": "7cf3716329f9d18ec20e266fc43ccbf3ada42ac64324cc4745d48da70a4abfb7"
}
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_7_o5_self_sustained_boundary.json
.venv/bin/python -c "import json; p='experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_7_o5_self_sustained_boundary.json'; d=json.load(open(p)); lane=d['positive_lane']; assert d['status']=='passed'; assert lane['o5_mode']=='producer_mediated'; assert lane['native_self_rearm_evidence'] is True; assert lane['self_rearm_cycle_count']==3; assert lane['native_constitutive_oscillator_supported'] is False; assert lane['constitutive_native_claim_allowed'] is False; assert d['artifact_replay']['passed'] is True; assert d['artifact_replay']['validation_valid'] is True; assert d['controls']['all_controls_passed'] is True; assert lane['node_plus_packet_budget_error']==0.0; assert lane['run_autonomous_natural_exhaustion_probe']['passed'] is True; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'o5_mode': lane['o5_mode'], 'self_rearm_cycle_count': lane['self_rearm_cycle_count'], 'budget_error': lane['node_plus_packet_budget_error'], 'artifact_replay': d['artifact_replay']['passed'], 'controls': d['controls']['all_controls_passed']})"
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- O5 uses the native `LGRC9V3RouteAspect` surplus-trigger producer,
  `LGRC9V3.run_autonomous(...)`, and
  `validate_lgrc9v3_self_rearm_evidence_artifacts(...)`.
- O5 intentionally uses a two-pole closed-loop route-aspect fixture rather
  than the source-target-reservoir chain from O3/O4, because native
  self-rearm evidence is defined over `LGRC9V3RouteAspect` channels.
- The positive lane records `o5_mode = producer_mediated`: renewal is
  threshold-authorized by runtime-visible route-aspect mass after committed
  parent-arrival events, but a producer still performs observation/recording
  and scheduling.
- The first parent return is a declared seed. The three counted O5 cycles are
  reconstructed from six completed native self-rearm events, not from repeated
  samples of one plateau.
- Artifact-only replay reruns the native self-rearm validator from exported
  snapshot events and production results. It reconstructs three cycles with
  `validation_valid = true`, `completed_self_rearm_count = 6`, and no runtime
  state fallback.
- `run_autonomous_stop_condition = max_events_reached` for the bounded
  positive trigger segments. A separate natural-exhaustion probe records
  `run_autonomous_stop_condition = no_autonomous_work_available` with no
  schedulable producer work and an empty queue.
- Controls passed with distinct blockers:
  `n05_o5_trigger_policy_disabled`,
  `n05_o5_threshold_gate_failed`,
  `n05_o5_committed_parent_arrival_missing`,
  `n05_o5_hidden_event_list_rejected`,
  `n05_o5_duplicate_trigger_suppressed`,
  `n05_o5_node_plus_packet_budget_mismatch`,
  `n05_o5_producer_mutation_boundary_violation`, and
  `n05_o5_claim_promotion_rejected`.
- Phase 3 native-policy support audit remains blocked for pure constitutive
  oscillator dynamics:
  `native_constitutive_oscillator_supported = false`,
  `constitutive_native_claim_allowed = false`, and
  `native_policy_blocker =
  missing_serialized_delayed_passive_response_policy`.
- Missing native policy surfaces are recorded for custom node potentials,
  potential inversion, flux-facilitated metric maps, delayed passive response,
  and route conductance memory.
- O5 does not promote pure native constitutive oscillator, route-coupled
  oscillator, semantic choice, memory/trail, agency, movement, locomotion-like,
  biological, ACO, or unrestricted movement claims.
- `git status --short src` returned no `src/*` status entries.
- `git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators`
  passed.

Acceptance statement:

```text
Iteration 7 passes if O5 renewal is authorized by runtime-visible circuit
state and not by hidden schedule. Pure-native oscillator support may be claimed
only if the required mechanism is expressible by existing serialized LGRC
policy; otherwise the result is a producer-mediated or threshold-mediated
oscillator candidate with a recorded native-policy blocker.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "constitutive_native_claim_allowed": false, "controls_passed": true, "native_constitutive_oscillator_supported": false, "native_policy_blocker": "missing_serialized_delayed_passive_response_policy", "o5_mode": "producer_mediated", "self_rearm_cycle_count": 3, "status": "passed"}
```

## Iteration 8. O6 Route-Coupled Oscillator Boundary And Closeout

Status: Complete.

- [x] Define route/edge coupling fields.
- [x] If route arbitration is used, record it as runtime route-arbitration
  support only, not semantic choice.
- [x] Record `route_coupling_surface`.
- [x] Verify route coupling is serialized and runtime-visible.
- [x] Record `route_coupling_runtime_visible`.
- [x] Verify route coupling does not promote memory/trail claim.
- [x] Record `memory_or_trail_claim_allowed = false`.
- [x] Record `trail_memory_blocker`.
- [x] Verify artifact-only replay reconstructs route-coupled oscillator
  evidence.
- [x] Verify node-plus-packet budget remains exact.
- [x] Run hidden trail, hidden route preference, budget mismatch, producer
  mutation, and claim-promotion controls.
- [x] Freeze strongest supported O-level.
- [x] Record strongest claim ceiling.
- [x] Record positive artifact SHA-256 digests.
- [x] Record negative controls and primary blockers.
- [x] Record Phase 3 native-policy blockers, if any.
- [x] Record N06 handoff recommendation.

Expected artifacts:

- [x] `outputs/n05_iteration_8_o6_closeout.json`
- [x] `reports/n05_iteration_8_o6_closeout.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_8_o6_closeout.py
```

Result:

```json
{"artifact_replay_passed": true, "controls_passed": true, "o6_route_coupled_oscillator_supported": false, "output": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json", "report": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_8_o6_closeout.md", "status": "passed", "strongest_claim_ceiling": "self_sustained_oscillator_candidate", "strongest_supported_o_level": "O5", "trail_memory_blocker": "missing_route_conductance_memory_policy"}
```

Artifact digests:

```json
{
  "artifact_replay_digest": "58c0885f672adba94fe0f0aed3238160adcaaac5a8bb7196836a23837044d72f",
  "closeout_summary_digest": "01500714849337fd08ab1fd4da40590110dc1f3c118395bf16329c072af4d8b4",
  "controls_digest": "06174541750d67a28ad21939b4e41f751008d9f7087f85d2c320bf5ec1c2dffb",
  "o6_boundary_digest": "5ca3733c6ac1d4d5293afb0f26ce7937ea9981c8948a89b9bffc65f7c419cd85",
  "source_artifact_index_digest": "f0e98294704ef8e38db878795eda7cb68c41c6b1860093a7ee30ca27c91f4517"
}
```

Generated file SHA-256:

```text
38c9b37186d1139a3ce7d3cf324e8f9a2b649099aa8bddd79c11eb346a86f1c8  outputs/n05_iteration_8_o6_closeout.json
fa9d3b7f7d44ddc03e5a14537f4d06fb6540019c0d3251dd503b0182d1a425c2  reports/n05_iteration_8_o6_closeout.md
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json
.venv/bin/python -c "import json; p='experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['n05_closeout']['strongest_supported_o_level']=='O5'; assert d['n05_closeout']['strongest_claim_ceiling']=='self_sustained_oscillator_candidate'; assert d['o6_boundary']['o6_route_coupled_oscillator_supported'] is False; assert d['o6_boundary']['trail_memory_blocker']=='missing_route_conductance_memory_policy'; assert d['artifact_replay']['artifact_only'] is True; assert d['artifact_replay']['runtime_state_used'] is False; assert d['artifact_replay']['passed'] is True; assert d['controls']['all_controls_passed'] is True; assert d['budget']['node_plus_packet_budget_error']==0.0; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'strongest_supported_o_level': d['n05_closeout']['strongest_supported_o_level'], 'o6_supported': d['o6_boundary']['o6_route_coupled_oscillator_supported'], 'blocker': d['o6_boundary']['trail_memory_blocker'], 'artifact_replay': d['artifact_replay']['passed'], 'controls': d['controls']['all_controls_passed']})"
git status --short src
git diff --check -- experiments/2026-05-N05-lgrc-coherence-waves-oscillators
```

Notes:

- N05 closes at `strongest_supported_o_level = O5` with claim ceiling
  `self_sustained_oscillator_candidate`.
- O6 route-coupled/trail-reinforced oscillator support remains blocked by
  `missing_route_conductance_memory_policy`.
- The O6 closeout replays the O5 route-aspect/self-rearm evidence from
  artifacts and confirms the route-aspect surface is serialized and
  runtime-visible:
  `route_coupling_surface =
  serialized_lgrc9v3_route_aspect_without_route_conductance_memory`.
- `route_coupling_runtime_visible = true`, but
  `route_memory_runtime_visible = false`.
- Route arbitration was not used in the N05 O6 closeout. If a later lane uses
  native route arbitration as route-coupling evidence, it remains runtime route
  selection evidence only, not semantic choice.
- Controls passed with distinct blockers:
  `n05_o6_hidden_trail_rejected`,
  `n05_o6_hidden_route_preference_rejected`,
  `n05_o6_node_plus_packet_budget_mismatch`,
  `n05_o6_producer_mutation_boundary_violation`,
  `n05_o6_claim_promotion_rejected`, and
  `n05_o6_route_memory_surface_missing`.
- Phase 3 native-policy blockers remain:
  `missing_serialized_custom_node_potentials_policy`,
  `missing_serialized_potential_inversion_policy`,
  `missing_flux_facilitated_metric_map_policy`,
  `missing_serialized_delayed_passive_response_policy`, and
  `missing_route_conductance_memory_policy`.
- N06 handoff recommendation is
  `open_N06_with_N05_O5_as_oscillator_background`.
- N06 must not inherit memory/trail, semantic choice, agency, RC identity
  collapse, identity acceptance, locomotion-like, biological, ACO, or
  unrestricted movement claims from N05.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 8 passes if N05 freezes its strongest supported O-level with
source-backed artifacts, exact budget accounting, artifact-only replay,
claim-boundary evidence, and a clear recommendation for whether N06 can open.
Route-coupled oscillator evidence may support later memory/trail work, but it
does not itself prove memory, ACO, semantic choice, agency, identity, or
locomotion.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_replay_passed": true, "budget_error": 0.0, "claim_flags_remain_false": true, "controls_passed": true, "o6_route_coupled_oscillator_supported": false, "status": "passed", "strongest_claim_ceiling": "self_sustained_oscillator_candidate", "strongest_supported_o_level": "O5", "trail_memory_blocker": "missing_route_conductance_memory_policy"}
```
