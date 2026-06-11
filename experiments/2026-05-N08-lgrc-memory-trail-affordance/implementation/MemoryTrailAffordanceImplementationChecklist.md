# N08 Memory Trail Affordance Implementation Checklist

This checklist tracks implementation of
`2026-05-N08-lgrc-memory-trail-affordance`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N08 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N05 O5 as oscillator/circuit background only.
- [ ] Treat N05 O6 as blocked by `missing_route_conductance_memory_policy`.
- [ ] Treat N06 SC6 as route-choice artifact context, not memory evidence.
- [ ] Treat N07 ID6 as identity/support context, not memory evidence.
- [ ] Keep N08 scoped to memory/trail/affordance formation.
- [ ] Do not promote ACO, agency, intention, goal regulation, identity
      acceptance, locomotion, biological, personhood, unrestricted identity, or
      unrestricted movement claims.
- [ ] Keep producer scheduling labeled as scheduling/evidence, not agency.
- [ ] Keep `step()` as the packet mutation boundary.
- [ ] Preserve node-plus-packet budget accounting for every run.
- [ ] Keep memory-budget surfaces separate from node-plus-packet budgets.
- [ ] Treat Iterations 1-8 as Hypothesis A serialized producer/policy memory
      unless an iteration explicitly opens Hypothesis B.
- [ ] Do not treat independent `memory_strength` as a pure native RC memory
      quantity.
- [ ] For Hypothesis B, require the trail to be derived from native
      geometry/topology/support or coherence/packet/loop state, not from an
      independent scalar surface.
- [ ] Serialize memory surface state snapshots for artifact-only replay.
- [ ] Treat route selection and route use as separate evidence events.
- [ ] Treat N06 SC6 as pre-topology selection provenance, not committed
      route-use evidence by itself.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Record SHA-256 digests for positive fixture artifacts.
- [ ] Keep all claim flags false unless Iteration 8 artifact-only closeout
      explicitly supports the narrow memory/trail evidence flag.

## Iteration 0. Planning And Handoff

Status: Complete.

- [x] Create N08 experiment stub.
- [x] Create N08 root README.
- [x] Create implementation README.
- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Create `hypotheses/` directory placeholder.
- [x] Record inherited N05 result:
  `self_sustained_oscillator_candidate`.
- [x] Record inherited N05 blocker:
  `missing_route_conductance_memory_policy`.
- [x] Record inherited N06 result:
  `artifact_only_semantic_route_choice_candidate`.
- [x] Record inherited N07 result:
  `artifact_only_source_specific_ID6_bounded_non_destructive_exchange`.
- [x] Record that N08 does not prove ACO, agency, intention, regulation,
  identity acceptance, locomotion, biological behavior, or personhood.
- [x] Freeze initial MEM0-MEM6 ladder.
- [x] Record N08 as two hypotheses:
  Hypothesis A serialized producer/policy memory and Hypothesis B native
  geometry-mediated trail memory.
- [x] Record that Iterations 1-8 primarily explore Hypothesis A and do not by
  themselves solve pure coherence/flux trail memory.

Acceptance statement:

```text
N08 starts from a clean claim boundary: N05 supplies oscillator/circuit
background, N06 supplies route-choice artifacts, and N07 supplies
identity/support anchors. N08 opens only memory/trail/affordance formation
evidence. A valid N08 positive result requires runtime-visible route-use
history, memory/trail surface state, serialized decay or reinforcement policy,
memory-shaped route arbitration, controls, and artifact replay.
```

Hypothesis split statement:

```text
Iterations 1-8 explore serialized producer/policy memory. They are useful for
pheromone-like producer design, but they do not prove a pure native
coherence/flux trail because `memory_strength` remains an independent artifact
quantity. The native geometry-mediated hypothesis remains separate: route use
must change declared geometry/topology/support or coherence/packet/loop state,
and future flux must change because of that native substrate state.
```

Implementation record:

- Added `experiments/2026-05-N08-lgrc-memory-trail-affordance/README.md`.
- Added `implementation/README.md`.
- Added `implementation/MemoryTrailAffordanceImplementationPlan.md`.
- Added `implementation/MemoryTrailAffordanceImplementationChecklist.md`.
- Created placeholder `configs/`, `outputs/`, `reports/`, and `scripts/`
  directories.
- Created placeholder `hypotheses/` directory.
- No N08 probes have been run yet.
- No `src/*` changes are required for Iteration 0.

## Iteration 1. Baseline And Schema Inventory

Status: Complete.

- [x] Inventory N05 closeout artifacts:
  - [x] O5 self-sustained oscillator candidate
  - [x] O6 blocker `missing_route_conductance_memory_policy`
  - [x] route-aspect fields
  - [x] route-memory absent fields
- [x] Inventory N06 closeout artifacts:
  - [x] candidate route records
  - [x] candidate set records
  - [x] native route-arbitration records
  - [x] candidate score components
  - [x] context surfaces
  - [x] selected/rejected route digests
- [x] Inventory N07 closeout artifacts:
  - [x] bounded non-destructive exchange class
  - [x] source/support identity anchors
  - [x] claim-boundary fields
- [x] Inventory available native memory/trail-like surfaces.
- [x] Record missing native memory/trail policy surfaces.
- [x] Inventory native route-arbitration forbidden-input keys.
- [x] Verify proposed memory score component names are not forbidden native
      inputs, or record the relevant blocker.
- [x] Inventory whether native candidate-score components can carry:
  - [x] `memory_trail_strength`
  - [x] `memory_surface_digest_match`
  - [x] `memory_recency_weight`
  - [x] `memory_decay_adjusted_strength`
- [x] Inventory N07 support-area fields available as memory keys:
  - [x] `support_area_id`
  - [x] `support_area_digest`
  - [x] source/target support digests where present
- [x] Freeze MEM row schema.
- [x] Freeze claim flags.
- [x] Freeze `memory_or_trail_claim_allowed` promotion criteria:
  MEM6 artifact-only replay required.
- [x] Define baseline JSON/report schema for MEM0-MEM6 evidence.
- [x] Ensure no memory probe is run in Iteration 1.

Expected artifacts:

- [x] `outputs/n08_iteration_1_baseline_inventory.json`
- [x] `reports/n08_iteration_1_baseline_inventory.md`

Acceptance statement:

```text
Iteration 1 passes if N08 has a source-backed baseline inventory of inherited
N05/N06/N07 artifacts, a frozen MEM ladder and row schema, a recorded native
memory/trail policy gap inventory, clean claim boundaries, and no memory probe
execution.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/build_n08_iteration_1_baseline_inventory.py`.
- Generated `outputs/n08_iteration_1_baseline_inventory.json`.
- Generated `reports/n08_iteration_1_baseline_inventory.md`.
- Source-backed inventory reads:
  - N05 Iteration 8 O6 closeout:
    `O5`, `self_sustained_oscillator_candidate`,
    `missing_route_conductance_memory_policy`.
  - N06 Iteration 8 SC6 closeout:
    candidate route records, candidate sets, native route-arbitration records,
    candidate score components, context surfaces, and selected/rejected route
    digests.
  - N07 Iteration 12 closeout plus 11-B source:
    `bounded_non_destructive_exchange`, `ID6`, `support_area_id`,
    `support_area_digest`, and source/target support digests.
- Source report digests include the N07 Iteration 11-B report as paired
  provenance for the N07 11-B source artifact.
- Native route-arbitration forbidden inputs inventoried:
  `experiment_if_else`, `hidden_fixture_array`, `hidden_fixture_state`,
  `posthoc_threshold`, `preselected_sink_id`, `report_code`.
- Proposed memory score component names are not forbidden native route
  arbitration input keys:
  `memory_trail_strength`, `memory_surface_digest_match`,
  `memory_recency_weight`, `memory_decay_adjusted_strength`.
- N06 route digest rows preserve source native arbitration record IDs from
  per-cycle replay blockers so N08 route-use templates can stay source-backed
  without inventing unresolved arbitration IDs.
- Recorded the boundary that current native route candidate score components
  can carry serialized non-forbidden keys, but current native LGRC does not yet
  provide memory/trail semantics or a native memory surface validator.
- Recorded missing native memory/trail policy surfaces:
  `native_route_conductance_memory_policy_missing`,
  `native_trail_memory_surface_missing`,
  `native_memory_surface_serialization_policy_missing`,
  `native_memory_surface_keying_policy_missing`,
  `native_memory_budget_accounting_policy_missing`,
  `native_memory_cross_cycle_persistence_policy_missing`,
  `native_memory_decay_policy_missing`,
  `native_memory_reinforcement_policy_missing`,
  `native_memory_candidate_score_component_semantics_missing`,
  `native_memory_artifact_replay_validator_missing`.
- Frozen `MEM0`-`MEM6` as evidence classifications, not claim flags.
- Frozen row schema with route-use, memory-surface, support-anchor,
  candidate-route, native-arbitration, node-plus-packet budget, memory-budget,
  native-support, and visual-reference fields.
- Frozen `memory_surface_key` as a canonical JSON object, not a scalar string,
  with fields `route_id`, `source_support_area_digest`,
  `target_support_area_digest`, `route_aspect_digest`, and
  `memory_policy_id`.
- Added `memory_surface_key_digest =
  sha256(canonical_json(memory_surface_key))` to the row schema.
- Encoded `memory_or_trail_claim_allowed` promotion criteria as required gates
  that are not yet satisfied in Iteration 1, rather than booleans that could be
  misread as achieved results.
- Added dedicated checks for N06 candidate score components, N06 cycle
  structure, N07 11-B report provenance, baseline schema self-validation,
  explicit memory key contract, and required-gate promotion criteria.
- Stabilized `inventory_digest` by excluding `generated_at` and
  `inventory_digest` from the digest scope.
- All claim flags remain false. `memory_or_trail_claim_allowed` requires MEM6
  artifact-only replay.
- No N08 memory probe was run.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_1_baseline_inventory.py
python -m json.tool experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_1_baseline_inventory.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_1_baseline_inventory.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
json.tool passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
inventory_digest stable across rerun = true
inventory_digest = c27c011e1875c7e967aac398818c2a72b55adfb064752b594524e91530ed20de
```

Artifact SHA-256:

```text
scripts/build_n08_iteration_1_baseline_inventory.py
  22015bbbe48a1377f70321a73d6f66b445dfda06cb6c962fe7ad37f638e624b8

outputs/n08_iteration_1_baseline_inventory.json
  32f46adb7f07e78d391fd1160c4fc2e4513235371c29da115ab2762b112bf4c9

reports/n08_iteration_1_baseline_inventory.md
  aa4c437a966d4f73307e2786e642393435d7448e819e9b77591cdf11fde7703e
```

## Iteration 2. Fixture Manifest And Route-Use Trace Contract

Status: Complete.

- [x] Define fixture manifest for route-use memory probes.
- [x] Define route-use event schema.
- [x] Define committed route-use semantics:
  - [x] route arbitration record exists
  - [x] selected candidate digest exists
  - [x] N08 route-use event records route consumption for memory formation
  - [x] route-use event is ordered, serialized, budget-audited, and digest-pinned
  - [x] topology commit requirement is explicitly included or explicitly not
        used by the fixture
- [x] Define memory surface row schema.
- [x] Define memory surface storage format:
  experiment-local serialized JSON artifact rows unless Phase 8 adds native
  support.
- [x] Define memory surface key:
  - [x] `route_id`
  - [x] `source_support_area_digest`
  - [x] `target_support_area_digest`
  - [x] `route_aspect_digest`
  - [x] `memory_policy_id`
- [x] Define memory surface digest algorithm:
  SHA-256 over canonical JSON with sorted keys, excluding the digest field.
- [x] Require `memory_surface_state_snapshot` or `memory_surface_rows` in MEM2+
      artifacts.
- [x] Define memory decay and reinforcement policy schemas.
- [x] Define default decay/reinforcement functions:
  - [x] exponential decay per memory window
  - [x] saturating additive reinforcement
  - [x] floor `0.0`
  - [x] ceiling `1.0`
  - [x] same-window decay/reinforcement order serialized
- [x] Define memory-budget fields and node-plus-packet budget fields.
- [x] Define memory budget semantics:
  serialized trail/affordance strength accounting, not node coherence.
- [x] Define memory-budget equation:
  `before + reinforcement_input - decay_loss - saturation_clamp_loss == after`.
- [x] Define memory-derived score component names and required
      `candidate_runtime_visible_inputs`.
- [x] Define event ordering:
  `route arbitration -> selected route use -> memory update -> later
  candidate scoring`.
- [x] Define controls and distinct blockers before positive runs.
- [x] Distinguish `hidden_route_history` from
      `memory_policy_hidden_preference`.
- [x] Add controls:
  - [x] `producer_mutation_boundary_violation`
  - [x] `policy_disabled`
  - [x] `no_memory_surface_read_by_arbitration`
  - [x] `memory_surface_poisoned`
  - [x] `cross_cycle_memory_leak`

Expected artifacts:

- [x] `configs/n08_fixture_manifest_v1.json`
- [x] `outputs/n08_iteration_2_fixture_manifest_validation.json`
- [x] `reports/n08_iteration_2_fixture_manifest_validation.md`

Acceptance statement:

```text
Iteration 2 passes if the fixture manifest and route-use/memory contracts are
defined before positive memory probes. The manifest must make route-use events,
memory surfaces, decay/reinforcement policies, budget surfaces, event ordering,
and controls replayable from artifacts.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/build_n08_iteration_2_fixture_manifest.py`.
- Generated `configs/n08_fixture_manifest_v1.json`.
- Generated `outputs/n08_iteration_2_fixture_manifest_validation.json`.
- Generated `reports/n08_iteration_2_fixture_manifest_validation.md`.
- Defined the fixture manifest before any positive memory probe.
- Defined route-use event schema with source arbitration digest, candidate set
  digest, selected candidate route digest, selected route id, route aspect
  digest, source/target support digests, event ordering, scheduler index,
  node-plus-packet budget fields, claim flags, and route-use digest.
- Froze committed route-use semantics:
  N06 route selection artifact is not an N08 route-use event; the N08 route-use
  event is an ordered, serialized, budget-audited, digest-pinned memory-lane
  consumption record.
- Explicitly set the early fixture topology commit requirement to `false`.
  Later topology-committing fixtures must opt in explicitly.
- Defined memory surface rows as experiment-local serialized JSON artifacts
  until a separate Phase 8 task adds native memory/trail support.
- Defined `memory_surface_kind` semantics:
  `trail` records persistence of prior committed route use, while
  `affordance` records a prospective route capability signal derived from
  trail/support/aspect evidence rather than hidden preference.
- Defined canonical `memory_surface_key` fields:
  `route_id`, `source_support_area_digest`, `target_support_area_digest`,
  `route_aspect_digest`, and `memory_policy_id`.
- Defined digest rules:
  `route_use_event_digest`,
  `memory_surface_key_digest`, and
  `memory_surface_digest` use SHA-256 over canonical JSON with the relevant
  digest field excluded.
- Required `memory_surface_state_snapshot` or `memory_surface_rows` for MEM2+
  artifacts.
- Mapped `memory_strength` from memory surface rows into MEM2+ evidence rows
  through serialized `memory_surface_state_snapshot` or `memory_surface_rows`.
- Defined decay and reinforcement policies:
  exponential decay per memory window, saturating additive reinforcement,
  floor `0.0`, ceiling `1.0`, and same-window order
  `decay -> reinforcement`.
- Recorded that decay can only reduce memory strength.
- Defined memory-budget accounting as a separate serialized trail/affordance
  strength surface, not node coherence.
- Defined memory-budget equation:
  `before + reinforcement_input - decay_loss - saturation_clamp_loss == after`.
- Required memory surface rows to serialize the intermediate memory-budget
  equation terms `reinforcement_input`, `decay_loss`, and
  `saturation_clamp_loss` so artifact-only replay can verify the equation.
- Preserved exact node-plus-packet budget accounting as a separate surface.
- Defined memory-derived route-score component names:
  `memory_trail_strength`, `memory_surface_digest_match`,
  `memory_recency_weight`, and `memory_decay_adjusted_strength`.
- Defined required runtime-visible candidate inputs:
  `memory_surface_id`, `memory_surface_digest`,
  `memory_surface_state_snapshot_digest`, `memory_policy_id`,
  `route_use_event_digest`, and `memory_event_time_key`.
- Defined event ordering:
  route arbitration -> selected route use -> memory update -> later candidate
  scoring -> native route arbitration.
- Added distinct control blockers for hidden route history, missing route-use
  event, missing/digest-mismatched/poisoned memory surface, missing policy,
  hidden memory policy preference, missing decay/reinforcement policy,
  memory score digest omission, hidden memory score input, memory-order
  inversion, memory-budget discontinuity, node-plus-packet discontinuity,
  stale memory surface read, cross-cycle memory leak, duplicate memory update,
  policy disabled, producer mutation boundary violation, no memory surface read
  by arbitration, posthoc memory threshold change, and claim promotion.
- Kept `hidden_route_history` distinct from
  `memory_policy_hidden_preference`.
- Route-use templates cover N06 route A and route B, preserve concrete N06
  source native arbitration record IDs, and explicitly require Iteration 3 to
  resolve and pin the actual `source_arbitration_record_digest` before MEM1
  route-use events are emitted.
- Recorded that Iteration 2 templates are unique route shapes only; Iteration 3
  must emit route-use events for all four N06 SC6 source cycles:
  `cycle_0`, `cycle_1`, `cycle_2`, and `cycle_3`.
- Added explicit claim flag references for route-use and memory-surface rows:
  both must carry the Iteration 1 frozen claim flag key set with all values
  false.
- Added producer/step boundary and inherited native policy blocker sections to
  the generated report.
- No route-use events were emitted.
- No memory surface rows were emitted.
- No N08 memory probe was run.
- All claim flags remain false.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_1_baseline_inventory.py
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_2_fixture_manifest.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_1_baseline_inventory.json experiments/2026-05-N08-lgrc-memory-trail-affordance/configs/n08_fixture_manifest_v1.json experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_2_fixture_manifest_validation.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_1_baseline_inventory.py experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/build_n08_iteration_2_fixture_manifest.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
manifest_digest = 7dbcdf1ada38683a33abb1230a5354972fe9365bbe24ee54c448c9ca4110a85a
validation_digest = 1ad3ec9766390e621c5338671466f65654929d80643d3003efb1cac294f7779a
source_baseline_digest_matches = true
memory_probe_not_run = true
```

Artifact SHA-256:

```text
scripts/build_n08_iteration_2_fixture_manifest.py
  ff5505a56ba9aa98f362272cf2d9a62131c6d0264cc0fbb7a8bc064c1dc17a50

configs/n08_fixture_manifest_v1.json
  be8556f209b0dd31ed0b9896c04e5a91fcdeca0efb7702ba53e48ea4202818c6

outputs/n08_iteration_2_fixture_manifest_validation.json
  dae2805fc7bcb4cd85a8f6f204ceacf4b06196fa7790e7d447796d87c877ee70

reports/n08_iteration_2_fixture_manifest_validation.md
  ee19f82e5161781842930e4363219977bf22c16f746c0f7a3de0528e3b54b893
```

## Iteration 3. MEM1 Route-Use Trace

Status: Complete.

- [x] Emit route-use event traces from selected route artifacts.
- [x] Verify route-use is not merely an N06 candidate/arbitration record.
- [x] Record selected candidate digest, route id, event time, scheduler index,
      budget surface, and route-use digest.
- [x] Verify no memory surface is emitted yet.
- [x] Controls: missing selected route, hidden route history, budget mismatch,
      duplicate route-use event, premature memory surface emission, claim
      promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_3_mem1_route_use_trace.json`
- [x] `reports/n08_iteration_3_mem1_route_use_trace.md`

Acceptance statement:

```text
Iteration 3 passes if route-use traces are source-backed and replayable, but no
memory/trail surface is yet claimed. MEM1 supports route-use history only.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_3_mem1_route_use_trace.py`.
- Generated `outputs/n08_iteration_3_mem1_route_use_trace.json`.
- Generated `reports/n08_iteration_3_mem1_route_use_trace.md`.
- Built four committed MEM1 route-use events from the N06 SC5 repeated-context
  source cycles:
  `cycle_0`, `cycle_1`, `cycle_2`, and `cycle_3`.
- Route-use sequence recorded:
  `route_a -> route_b -> route_a -> route_b`.
- Resolved source native arbitration record digests from the full N06 SC5
  route-arbitration records:
  `c55c034882aea07b7ce6093249ea4c30c533f89e2ede7bc7bf040106a8731a24`,
  `e55e128a031d39708b11de4f34289d55f5ce5216ff1a8ca59bd5ad133e04ea9b`,
  `715bbac6df142956748a403236d214a949c7b36f3a87716a3cb2978e3f959e8f`,
  and `274002a129793722412f4019ea2ff18f2b45710c0fa8d80e6bebb083cf085db0`.
- Each route-use event records selected candidate route digest, selected route
  id, route aspect digest, source/target support digests, event time,
  scheduler index, source arbitration digest, source candidate-set digest,
  node-plus-packet budget fields, claim flags, and route-use event digest.
- Route-use events are N08 artifacts with ids prefixed `n08-route-use:*`; they
  are not merely N06 candidate or arbitration records.
- Source arbitration record IDs are now cross-validated against the Iteration 2
  manifest contract and against the N06 SC5 lane that supplies the source
  arbitration digest.
- Source surface digest extraction is guarded and validated as present for each
  route-use event.
- MEM1 supplementary event fields are explicitly declared in the output/report
  so replay auditors can distinguish intentional provenance/context fields from
  accidental leakage beyond the Iteration 2 minimum required fields.
- Event-time derivation uses named constants:
  `ROUTE_USE_EVENT_TIME_OFFSET = 0.1`,
  `ROUTE_USE_EVENT_TIME_STRIDE = 1.0`, and
  `ROUTE_USE_SCHEDULER_INDEX_OFFSET = 1`; the report records why the MEM1
  events are placed after same-time N06 source arbitrations and separated by
  cycle index.
- Route-use events are evidence-only and budget-neutral:
  `node_plus_packet_budget_before == node_plus_packet_budget_after == 0.0`
  and `node_plus_packet_budget_error == 0.0`.
- No memory surface rows, memory surface digests, or memory state snapshots were
  emitted in Iteration 3.
- Added Arc-of-Becoming interpretation:
  question, observations, classification, cultivation next question, and
  naturalization boundary. The report treats pass/fail as a gate, not as the
  whole result.
- Arc classification:
  `route_use_history_trace`, naturalization rung
  `Nat0_trace_dependent_expression`.
- Cultivation next question:
  whether committed route-use events can cultivate a persisted trail or
  affordance surface whose digest and budget replay from artifacts.
- Recorded learning boundary:
  Iteration 3 is not reinforcement learning, neural weight update, graph weight
  propagation, conductance learning, policy update, or future-route bias. Its
  closest analogy is an event log or trace buffer. Learning-like behavior can
  only begin after later iterations add serialized memory surfaces,
  decay/reinforcement updates, memory-derived score components, and repeated
  memory-shaped selection.
- Added producer/step boundary and inherited native policy blocker sections to
  the Iteration 3 report.
- Controls pass with distinct blockers:
  `missing_selected_route`, `hidden_route_history`,
  `node_plus_packet_budget_discontinuity`, `duplicate_route_use_event`,
  `memory_surface_not_allowed_in_mem1`, and `claim_promotion`.
- All claim flags remain false, including `memory_or_trail_claim_allowed`.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_3_mem1_route_use_trace.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_3_mem1_route_use_trace.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_3_mem1_route_use_trace.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
route_use_event_count = 4
route_sequence = route_a, route_b, route_a, route_b
memory_surface_emitted = false
failed_checks = []
learning_boundary_recorded = true
no_policy_or_weight_update = true
source_arbitration_record_ids_match_manifest_contract = true
source_arbitration_id_digest_same_n06_lane = true
route_use_event_supplementary_fields_declared = true
source_surface_digest_present = true
output_digest = fb6c40e48dd5c30772f3305b32dff5ebc91a0a90796891e006ef9c8647f1445c
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_3_mem1_route_use_trace.py
  4ba7a13863d3110cd0a80fdc459762da01be688336f4d28193616b19b38f5593

outputs/n08_iteration_3_mem1_route_use_trace.json
  abd7cc5485ea1f347a5c4d7c7e81722814656c16026a864c32300247f60e4c5d

reports/n08_iteration_3_mem1_route_use_trace.md
  97b2571a5bfb5a6dbbf756079bada40aa2df22a3b6d2e40d7e6b04823d663e68
```

## Iteration 4. MEM2 Trail / Affordance Memory Surface

Status: Complete.

- [x] Convert route-use traces into memory surface rows.
- [x] Record memory surface digest, route-use digest, policy id, and budget.
- [x] Serialize memory surface state snapshot or memory surface rows.
- [x] Verify memory surface key and digest recompute.
- [x] Verify persistence after route-use event.
- [x] Controls: missing route-use event, memory surface digest mismatch,
      memory surface key digest mismatch, hidden route history, memory budget
      discontinuity, node-plus-packet budget discontinuity, claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_4_mem2_memory_surface.json`
- [x] `reports/n08_iteration_4_mem2_memory_surface.md`

Acceptance statement:

```text
Iteration 4 passes if prior route use creates a persisted runtime-visible
memory/trail/affordance surface with source provenance and exact budgets.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_4_mem2_memory_surface.py`.
- Generated `outputs/n08_iteration_4_mem2_memory_surface.json`.
- Generated `reports/n08_iteration_4_mem2_memory_surface.md`.
- Converted four MEM1 route-use events into four experiment-local serialized
  MEM2 trail surface rows.
- Memory surface kind is `trail`; affordance remains latent until later
  candidate scoring reads the trail as runtime-visible evidence.
- Final serialized trail strengths:
  `route_a = 0.5`, `route_b = 0.5`.
- Each memory surface row records route-use digest, route-use id, source
  arbitration digest, selected candidate route digest, route id, memory surface
  key, memory surface key digest, memory policy id/digest, event ordering,
  node-plus-packet budget fields, memory-budget fields, claim flags, and memory
  surface digest.
- Memory surface key remains canonical:
  `route_id`, `source_support_area_digest`, `target_support_area_digest`,
  `route_aspect_digest`, and `memory_policy_id`.
- Memory surface rows cite MEM1 route-use event digests and occur after their
  source route-use events in event time and scheduler order.
- Serialized state snapshot produced:
  `n08_mem2_trail_surface_state_snapshot_v1`.
- State snapshot digest:
  `60448fc4c7d491c254fafd21a7745b34cf6cf1922f560a6a8b2f2c9df75a4d68`.
- State snapshot is explicitly scoped as
  `latest_state_summary_not_full_replay_record`; full artifact replay requires
  the serialized `memory_surface_rows`.
- Recomputed the manifest memory policy digest from
  `memory_policy_without_memory_policy_digest` and verified that every row
  carries the validated digest.
- Documented `memory_surface_id` construction as
  `n08-memory-surface:{memory_surface_key_digest[:16]}:{route_use_event_digest[:16]}`.
- Documented MEM2 ordering conventions:
  `event_time_key = route_use_event_time_key + 0.2` and memory surface rows in
  scheduler band `10-19`.
- Declared the allowed supplementary row fields so artifact consumers can
  distinguish intentional provenance/context fields from accidental leakage.
- Memory-budget equation holds for every row:
  `memory_budget_before + reinforcement_input - decay_loss -
  saturation_clamp_loss == memory_budget_after`.
- Iteration 4 formation-phase seed accumulation is now distinguished from the
  formal MEM3 decay/reinforcement policy window:
  `formation_window_applied = true`,
  `formation_update_kind = route_use_seed_accumulation`,
  `formal_mem3_policy_window_applied = false`, and
  `formal_mem3_decay_reinforcement_window_applied = false`.
- Node-plus-packet budget remains exact and separate from trail-strength
  bookkeeping.
- No decay window, reinforcement window, memory-shaped route arbitration,
  candidate-score update, future-route bias, or native route weight update is
  performed in Iteration 4.
- Added Arc-of-Becoming interpretation:
  question, observations, classification, cultivation next question, and
  naturalization boundary.
- Arc classification:
  `trail_memory_surface_candidate`, naturalization rung
  `Nat1_persisted_artifact_surface`, affordance status
  `latent_not_yet_operational`.
- Cultivation next question:
  whether the persisted trail surface can undergo serialized decay and
  reinforcement updates while preserving memory-budget and node-plus-packet
  budget separation.
- Controls pass with distinct blockers:
  `missing_route_use_event`, `memory_surface_digest_mismatch`,
  `memory_surface_key_digest_mismatch`, `hidden_route_history`,
  `memory_budget_discontinuity`, `node_plus_packet_budget_discontinuity`, and
  `claim_promotion`.
- All claim flags remain false, including `memory_or_trail_claim_allowed`.
- Native memory surface support remains experiment-local and blocked by the
  inherited native policy blockers until a later Phase 8 task.
- Report now includes dedicated Producer / Step Boundary and inherited native
  policy blocker sections.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_4_mem2_memory_surface.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_4_mem2_memory_surface.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_4_mem2_memory_surface.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
memory_surface_row_count = 4
final_strength.route_a = 0.5
final_strength.route_b = 0.5
failed_checks = []
check_count = 34
memory_policy_digest_valid = true
snapshot_scope = latest_state_summary_not_full_replay_record
output_digest = acced36658c46bab5e6daa0f44a28f566c5848d1bc0578bd71da6b8720f27af8
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_4_mem2_memory_surface.py
  e6023b35ae1f898a45b9005b1e990df824e4cf7f384984e3bb52d2395dd9ee12

outputs/n08_iteration_4_mem2_memory_surface.json
  61f388c526f8afe3cbce5ac7a394fd5ff8e82cb8a40c54834926c074a8e407a6

reports/n08_iteration_4_mem2_memory_surface.md
  d7e1a0894f24169ecee2b70f9171e4778bc6abe1024f91809277c0772d73689c
```

## Iteration 5. MEM3 Decay / Reinforcement Update

Status: Complete.

- [x] Apply serialized decay policy.
- [x] Apply serialized reinforcement policy after repeated route use.
- [x] Record decay loss, reinforcement input, saturation clamp loss, floor, and
      ceiling.
- [x] Record whether decay and reinforcement happen in the same window and the
      serialized order if so.
- [x] Preserve memory-budget and node-plus-packet budget separation.
- [x] Controls: missing decay policy, missing reinforcement policy, hidden
      preference, post-hoc threshold, duplicate update, order inversion,
      memory budget discontinuity, node-plus-packet budget discontinuity, claim
      promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_5_mem3_decay_reinforcement.json`
- [x] `reports/n08_iteration_5_mem3_decay_reinforcement.md`

Acceptance statement:

```text
Iteration 5 passes if memory surface strength changes through serialized decay
or reinforcement policy and the update is replayable without hidden state.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_5_mem3_decay_reinforcement.py`.
- Generated `outputs/n08_iteration_5_mem3_decay_reinforcement.json`.
- Generated `reports/n08_iteration_5_mem3_decay_reinforcement.md`.
- Started from the latest MEM2 trail surface state, not from hidden route
  history and not by re-applying Iteration 4 formation inputs.
- Emitted two new experiment-local MEM3 memory surface rows, one per canonical
  memory surface key.
- Applied the serialized same-window update order:
  `decay -> reinforcement`.
- Decay policy:
  `n08_exponential_decay_v1`, `decay_factor = 0.9`, floor `0.0`.
- Reinforcement policy:
  `n08_saturating_additive_reinforcement_v1`,
  `reinforcement_amount = 0.25`, ceiling `1.0`.
- MEM3 update window:
  `n08_mem3_decay_reinforcement_window_0`,
  `update_window_event_time_key = 5.5`,
  scheduler band `20-29`.
- Elapsed memory window rule:
  `max(1, floor(update_window_event_time_key -
  source_memory_surface_event_time_key))`.
- Reinforcement eligibility rule is route-neutral:
  `route_use_count_for_key >= 2`; both route keys qualify.
- Route A source surface is older, so it decays across two windows before
  reinforcement:
  `0.5 -> 0.405 -> 0.655`.
- Route B source surface is newer, so it decays across one window before
  reinforcement:
  `0.5 -> 0.45 -> 0.7`.
- Final serialized MEM3 trail strengths:
  `route_a = 0.655`, `route_b = 0.7`.
- The route strength difference comes from serialized source-surface recency
  and the declared elapsed-window rule, not from route-specific preference.
- `decay_loss` is explicitly recorded as
  `serialized_memory_signal_attenuation`, not physical RC flux.
- `decay_is_physical_flux = false`, `decay_destination_surface = null`, and
  `coherence_pocket_transfer_performed = false` for every MEM3 row.
- Physical memory decay support remains
  `not_supported_without_explicit_conserved_destination_surface`.
- If a later iteration transfers memory decay into coherence pockets, it must
  declare a conserved destination surface and prove node-plus-packet budget
  conservation; without that destination this is a divergent artifact-signal
  path, not RC mass/flux.
- Memory-budget equation holds for every row:
  `memory_budget_before + reinforcement_input - decay_loss -
  saturation_clamp_loss == memory_budget_after`.
- Node-plus-packet budget remains exact and separate from trail-strength
  bookkeeping.
- State snapshot produced:
  `n08_mem3_decay_reinforcement_state_snapshot_v1`.
- State snapshot digest:
  `38d70c060d517c477452f9719bec053fc9530372ec5e045bc1f5df32f7c60b5f`.
- State snapshot is explicitly scoped as
  `latest_state_summary_not_full_replay_record`; full artifact replay requires
  the serialized `memory_surface_rows`.
- Added Arc-of-Becoming interpretation:
  question, observations, classification, cultivation next question, and
  naturalization boundary.
- Arc classification:
  `decay_reinforcement_memory_candidate`, naturalization rung
  `Nat2_policy_updated_artifact_surface`, affordance status
  `latent_not_yet_operational`.
- Cultivation next question:
  whether candidate-route score components can cite these MEM3 memory surface
  digests and alter route arbitration without hidden memory inputs.
- Controls pass with distinct blockers:
  `decay_policy_missing`, `reinforcement_policy_missing`,
  `memory_policy_hidden_preference`, `posthoc_memory_threshold_change`,
  `duplicate_memory_update`, `arbitration_memory_order_invalid`,
  `memory_budget_discontinuity`, `node_plus_packet_budget_discontinuity`, and
  `claim_promotion`.
- All claim flags remain false, including `memory_or_trail_claim_allowed`.
- Native memory update support remains experiment-local and blocked by the
  inherited native policy blockers until a later Phase 8 task.
- No candidate-score update, future route bias, memory-shaped arbitration,
  native route weight update, or `src/*` change is performed in Iteration 5.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_5_mem3_decay_reinforcement.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_5_mem3_decay_reinforcement.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_5_mem3_decay_reinforcement.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
memory_surface_row_count = 2
check_count = 41
failed_checks = []
final_strength.route_a = 0.655
final_strength.route_b = 0.7
elapsed_memory_windows.route_a = 2
elapsed_memory_windows.route_b = 1
decay_quantity_kind = serialized_memory_signal_attenuation
decay_is_physical_flux = false
decay_destination_surface = null
coherence_pocket_transfer_performed = false
output_digest = e9b752b1bf5df9e4d58aa5da15c0a741df53b0e1237c9d5124390986ca8b89be
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_5_mem3_decay_reinforcement.py
  c95fe355dbe97ef099d5336d102cd6a8ca85b5fec3e0da0f5420b01fdd86ca1f

outputs/n08_iteration_5_mem3_decay_reinforcement.json
  21383fe9661e98ebaf0b0956c35e5bc0268b85adbe936843b7b5147f3b5ba45f

reports/n08_iteration_5_mem3_decay_reinforcement.md
  19b9ca7b7fc810405bdb6dcc8703c0e3e5afe2d34abaaa60b6d86af1f055bd62
```

## Iteration 6. MEM4 Memory-Shaped Route Arbitration

Status: Complete.

- [x] Candidate-route score components cite memory surface digest.
- [x] Candidate-route score components include only allowed memory component
      keys.
- [x] `candidate_runtime_visible_inputs` include memory surface id/digest,
      memory policy id, route-use digest, and memory event time key.
- [x] Verify `candidate_route_score == sum(candidate_score_components)`.
- [x] Run counterfactual lane:
  same source/context/policy without memory component.
- [x] Record selected-route delta and memory-score delta.
- [x] Route arbitration reads memory-derived scores.
- [x] Selected route changes because of serialized memory state.
- [x] Controls: candidate score missing memory digest, hidden memory input,
      stale memory surface read, order inversion, budget mismatch, claim
      promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_6_mem4_memory_shaped_arbitration.json`
- [x] `reports/n08_iteration_6_mem4_memory_shaped_arbitration.md`

Acceptance statement:

```text
Iteration 6 passes if memory surface state changes candidate-route evidence and
native route arbitration selects according to serialized memory-derived score
components.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_6_mem4_memory_shaped_arbitration.py`.
- Generated `outputs/n08_iteration_6_mem4_memory_shaped_arbitration.json`.
- Generated `reports/n08_iteration_6_mem4_memory_shaped_arbitration.md`.
- Consumed Iteration 5 MEM3 memory surface rows as serialized candidate-score
  evidence.
- Iteration 6 is explicitly Hypothesis A only:
  serialized producer/policy memory.
- It does not claim Hypothesis B native geometry-mediated trail memory, pure
  coherence/flux trail memory, ACO, agency, biological pheromone behavior, or
  locomotion.
- Built a no-memory counterfactual lane:
  `n08_mem4_counterfactual_without_memory_component`.
- Counterfactual candidate scores:
  `route_a = 0.0`, `route_b = 0.0`.
- Counterfactual selection uses deterministic candidate order key and selects:
  `route_a`.
- Built a memory-shaped arbitration lane:
  `n08_mem4_memory_shaped_arbitration`.
- Memory-shaped candidate score components use only the allowed component names:
  `memory_trail_strength`, `memory_surface_digest_match`,
  `memory_recency_weight`, and `memory_decay_adjusted_strength`.
- Memory-shaped `candidate_runtime_visible_inputs` cite:
  `memory_surface_id`, `memory_surface_digest`,
  `memory_surface_state_snapshot_digest`, `memory_policy_id`,
  `route_use_event_digest`, and `memory_event_time_key`.
- Memory-shaped candidate scores:
  `route_a = 0.8455`, `route_b = 0.945`.
- Memory-shaped arbitration selects:
  `route_b`.
- Selected-route delta:
  `without_memory = route_a`, `with_memory = route_b`.
- Memory score delta:
  `route_b - route_a = 0.0995`.
- Every candidate satisfies:
  `candidate_route_score == sum(candidate_score_components)`.
- Route arbitration records cite the selected candidate digest, candidate set
  digest, rejected candidate digest, score, and runtime-visible memory inputs.
- No topology event is committed, no packet is scheduled, no state is mutated,
  and no producer/step boundary is weakened.
- Node-plus-packet budget predictions remain exact.
- Memory-budget rows from Iteration 5 remain exact and source-backed.
- Controls pass with distinct blockers:
  `candidate_score_memory_digest_missing`,
  `candidate_score_hidden_memory_input`, `stale_memory_surface_read`,
  `arbitration_memory_order_invalid`, `memory_budget_discontinuity`,
  `node_plus_packet_budget_discontinuity`,
  `no_memory_surface_read_by_arbitration`, and `claim_promotion`.
- All claim flags remain false, including `memory_or_trail_claim_allowed`.
- Native memory score semantics remain experiment-local and blocked by the
  inherited native policy blockers until a later Phase 8/native-memory task.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_6_mem4_memory_shaped_arbitration.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_6_mem4_memory_shaped_arbitration.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_6_mem4_memory_shaped_arbitration.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact acceptance achieved = true
check_count = 29
failed_checks = []
counterfactual_selected_route = route_a
memory_shaped_selected_route = route_b
memory_score_delta = 0.0995
output_digest = f154865ec31bcd2187b777682cb58269d2845c92d981e1196507cb53a08d6cc5
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_6_mem4_memory_shaped_arbitration.py
  25ab13b6aa36b4da408bed16822152c3f29af191d48fcd1b2e21037713525545

outputs/n08_iteration_6_mem4_memory_shaped_arbitration.json
  006fa6d98c816e6f247766be0210ed1892a286ab75ab8469c0e72dcfa7c69dc2

reports/n08_iteration_6_mem4_memory_shaped_arbitration.md
  4df3c66769e25d624320a574c896e5e49c99ca0585f750f6f16e56a5fe108dd9
```

## Iteration 7. MEM5 Repeated Memory-Shaped Selection

Status: Complete.

- [x] Run repeated cycles of route use, memory update, and route arbitration.
- [x] Use at least four cycles unless a lower count is explicitly justified.
- [x] Verify reinforcement and decay trends across cycles.
- [x] Record saturation, extinction, and competing-memory behavior.
- [x] Record whether competing memories converge, oscillate, or tie.
- [x] Verify context/identity anchors remain source-backed.
- [x] Controls: repeated hidden route preference, stale memory read, duplicate
      memory update, budget drift, claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_7_mem5_repeated_memory_selection.json`
- [x] `reports/n08_iteration_7_mem5_repeated_memory_selection.md`

Acceptance statement:

```text
Iteration 7 passes if repeated route-use cycles produce memory-shaped route
selection without hidden steering and without budget drift.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_7_mem5_repeated_memory_selection.py`.
- Generated `outputs/n08_iteration_7_mem5_repeated_memory_selection.json`.
- Generated `reports/n08_iteration_7_mem5_repeated_memory_selection.md`.
- Replayed the Hypothesis A serialized producer/policy memory loop for four
  cycles:
  `memory state -> candidate scores -> route arbitration -> route use ->
  decay/reinforcement update -> next memory state`.
- Source artifacts:
  - `outputs/n08_iteration_2_fixture_manifest_validation.json`
  - `outputs/n08_iteration_6_mem4_memory_shaped_arbitration.json`
- Source report:
  - `reports/n08_iteration_6_mem4_memory_shaped_arbitration.md`
- Reused Iteration 6 MEM4 memory-shaped candidate records as the initial
  repeated-cycle memory state.
- Route B was selected on all four cycles:
  `["route_b", "route_b", "route_b", "route_b"]`.
- Route B reached serialized memory saturation:
  `[0.88, 1.0, 1.0, 1.0]`.
- Route A decayed under non-selection but did not reach the floor:
  `[0.5895, 0.53055, 0.477495, 0.4297455]`.
- Competing-memory behavior was classified as
  `route_b_converges_to_saturation_while_route_a_decays_without_reinforcement`.
- No oscillation or unresolved tie was observed.
- Recorded Arc-of-Becoming interpretation as a question/observation/
  classification/cultivation/naturalization record:
  `Nat4_repeated_policy_memory_loop`.
- Preserved the Hypothesis A/Hypothesis B boundary:
  - `serialized_memory_policy_loop = true`
  - `native_geometry_mediated_trail_path = false`
  - `native_geometry_trail_claimed = false`
  - `pure_coherence_flux_trail_claimed = false`
  - `independent_memory_strength_used_as_physical_flux = false`
- `memory_strength` remains serialized score evidence, not a physical flux
  quantity and not a pure native RC memory quantity.
- Controls passed with distinct blockers:
  - `repeated_hidden_route_preference` ->
    `candidate_score_hidden_memory_input`
  - `stale_memory_surface_read` -> `stale_memory_surface_read`
  - `duplicate_memory_update` -> `duplicate_memory_update`
  - `cross_cycle_memory_leak` -> `cross_cycle_memory_leak`
  - `memory_budget_discontinuity` -> `memory_budget_discontinuity`
  - `node_plus_packet_budget_discontinuity` ->
    `node_plus_packet_budget_discontinuity`
  - `claim_promotion` -> `claim_promotion`
- Node-plus-packet budget remained exact.
- Memory-budget equations held for every update row.
- Candidate, arbitration, route-use, and memory-surface digests recomputed.
- All claim flags remain false, including:
  `memory_or_trail_claim_allowed`, `aco_like_claim_allowed`,
  `agentic_like_claim_allowed`, `agency_claim_allowed`,
  `ant_colony_claim_allowed`, `semantic_choice_claim_allowed`,
  `movement_claim_allowed`, and `biological_claim_allowed`.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_7_mem5_repeated_memory_selection.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_7_mem5_repeated_memory_selection.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_7_mem5_repeated_memory_selection.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = a5b8673f705a67394f284808a780a5ec4e30af00eac003b7f411ec14ce2b135a
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_7_mem5_repeated_memory_selection.py
  7f086e146a02302942bf1c0794791af9441592bf37d199d8b255ecb89f379c91

outputs/n08_iteration_7_mem5_repeated_memory_selection.json
  2ea61b7024e6275b352ddbd1fabf76e2b92862f285739279dcf5f87b3b296772

reports/n08_iteration_7_mem5_repeated_memory_selection.md
  97314510d3b2db24e6c28b01d0719237d733179e8442be0922d9c85121c21131
```

## Iteration 8. MEM6 Artifact-Only Replay And Closeout

Status: Complete.

- [x] Replay route-use events from artifacts only.
- [x] Replay memory surface updates from artifacts only.
- [x] Reconstruct memory surface state from serialized snapshots/rows.
- [x] Replay decay/reinforcement policy from artifacts only.
- [x] Replay memory-shaped candidate scores and route arbitration.
- [x] Recompute memory-derived score components and candidate route scores.
- [x] Reject replay on digest mismatch, score mismatch, stale memory read,
      order inversion, duplicate update, or budget discontinuity.
- [x] Replay controls with distinct primary blockers.
- [x] Freeze strongest N08 ceiling.
- [x] Preserve ACO, agency, intention, regulation, identity acceptance,
      locomotion, biological, personhood, and unrestricted claims as blocked.

Expected artifacts:

- [x] `outputs/n08_iteration_8_mem6_closeout.json`
- [x] `reports/n08_iteration_8_mem6_closeout.md`

Acceptance statement:

```text
Iteration 8 passes if the route-use -> memory surface -> decay/reinforcement
-> memory-shaped route arbitration chain can be reconstructed from artifacts
only, controls fail with distinct blockers, budgets remain exact, and the
strongest N08 Hypothesis A memory/trail evidence ceiling is frozen without ACO,
agency, intention, goal-regulation, identity-acceptance, locomotion,
biological, or unrestricted claims.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_8_mem6_closeout.py`.
- Generated `outputs/n08_iteration_8_mem6_closeout.json`.
- Generated `reports/n08_iteration_8_mem6_closeout.md`.
- The closeout reads Iteration 7 JSON as the source artifact and does not
  import or call the Iteration 7 runner.
- Artifact-only replay scope:
  - `route_use_events_replayed = 4`
  - `memory_surface_update_rows_replayed = 8`
  - `candidate_route_records_replayed = 8`
  - `candidate_set_records_replayed = 4`
  - `route_arbitration_records_replayed = 4`
  - scheduled/processed packet records were recorded as not applicable because
    the Hypothesis A fixture did not schedule packets.
- Replayed selected-route sequence:
  `["route_b", "route_b", "route_b", "route_b"]`.
- Replayed route B memory saturation:
  `[0.88, 1.0, 1.0, 1.0]`.
- Replayed route A non-selected decay:
  `[0.5895, 0.53055, 0.477495, 0.4297455]`.
- Recomputed source Iteration 7 `output_digest`.
- Recomputed candidate, candidate-set, route-arbitration, route-use, and
  memory-surface digests during replay.
- Recomputed memory-derived score components and candidate scores.
- Replayed source Iteration 7 controls with expected blockers:
  - `repeated_hidden_route_preference` ->
    `candidate_score_hidden_memory_input`
  - `stale_memory_surface_read` -> `stale_memory_surface_read`
  - `duplicate_memory_update` -> `duplicate_memory_update`
  - `cross_cycle_memory_leak` -> `cross_cycle_memory_leak`
  - `memory_budget_discontinuity` -> `memory_budget_discontinuity`
  - `node_plus_packet_budget_discontinuity` ->
    `node_plus_packet_budget_discontinuity`
  - `claim_promotion` -> `claim_promotion`
- Added corrupted-artifact controls that fail with distinct blockers:
  - `missing_route_use_event`
  - `memory_surface_digest_mismatch`
  - `memory_state_reconstruction_mismatch`
  - `score_component_mismatch`
  - `event_order_inversion`
  - `stale_memory_read`
  - `duplicate_update`
  - `memory_budget_discontinuity`
  - `claim_promotion`
- Strongest supported MEM level frozen:
  `MEM6`.
- Strongest Hypothesis A claim ceiling frozen:
  `artifact_only_route_memory_or_trail_affordance_candidate`.
- Narrow `memory_or_trail_claim_allowed` is now true only at the closeout row
  and only with scope
  `artifact_only_serialized_producer_policy_route_memory_or_trail`.
- Source runtime rows remain claim-free:
  `source_runtime_claim_flags_remained_false = true`.
- All broader claims remain blocked:
  ACO, agentic-like, agency, ant-colony, biological, goal-proxy regulation,
  identity acceptance, intention, locomotion-like, movement, personhood,
  RC identity collapse, runtime identity acceptance, semantic choice,
  unrestricted identity, and unrestricted movement.
- Hypothesis B remains open and not claimed with blocker
  `native_geometry_mediated_trail_not_tested_in_iterations_1_8`.
- `memory_strength` remains serialized score evidence, not physical flux.
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_8_mem6_closeout.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_8_mem6_closeout.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_8_mem6_closeout.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = 202cd1a6d447aedf6c2914b0768819fff6f15c918f509cb26b88eba2d88e7a5c
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_8_mem6_closeout.py
  e571ac5bae446594baf755f0cdb5d6382902cdbe146195ce06914b68e18c8741

outputs/n08_iteration_8_mem6_closeout.json
  73c0681ff6f2d32fe259f2153e3398abad03095e6d9dcfd364b55bf23c48454e

reports/n08_iteration_8_mem6_closeout.md
  f60aa7ab93ca41823c117f45ddd4e4443721f284bc16456f53ea8b8213162d81
```

## Iteration 9. Native Geometry Trail Baseline

Status: Complete.

- [x] Freeze Hypothesis B as separate from Iterations 1-8.
- [x] Inventory existing native LGRC mechanisms that can change routing without
      an independent `memory_strength` quantity.
- [x] Check topology-event, edge-split, inserted-node, geometry-parameter,
      support-shape, local-coupling, packet/loop residue, and lineage/reabsorption
      surfaces.
- [x] Record which mechanisms are available now and which require Phase 8.
- [x] Confirm no memory-shaped scoring or serialized memory scalar is used.
- [x] Preserve node-plus-packet budget and all claim boundaries.

Expected artifacts:

- [x] `outputs/n08_iteration_9_native_geometry_trail_baseline.json`
- [x] `reports/n08_iteration_9_native_geometry_trail_baseline.md`

Acceptance statement:

```text
Iteration 9 passes if the native geometry-mediated trail question is frozen
with a source-backed inventory of available LGRC geometry/topology/support
mechanisms and explicit blockers, without using `memory_strength`, hidden route
preference, memory-shaped scoring, or claim promotion.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_9_native_geometry_trail_baseline.py`.
- Generated `outputs/n08_iteration_9_native_geometry_trail_baseline.json`.
- Generated `reports/n08_iteration_9_native_geometry_trail_baseline.md`.
- Iteration 9 starts Hypothesis B and does not run a new memory probe.
- Hypothesis A remains closed at
  `artifact_only_route_memory_or_trail_affordance_candidate`.
- Hypothesis B remains separate from Iterations 1-8 and is not claimed.
- Hypothesis B current blocker:
  `native_geometry_mediated_trail_not_tested_before_iteration_9`.
- Preferred Iteration 10 probe:
  `edge_split_or_inserted_node_topology_trace`.
- Iteration 10 entry gate:
  `iteration_10_entry_allowed = true`.
- Source-backed mechanisms available for Iteration 10:
  - `committed_topology_event`
  - `edge_split_or_inserted_node`
  - `surface_lineage_transport`
  - `topology_state_reabsorption`
  - `time_scoped_lineage_replay`
- Source-backed mechanism available for Iteration 11 response measurement:
  - `native_route_arbitration`
- Blocked or unconfirmed mechanisms:
  - `declared_node_or_edge_geometry_parameter_change` ->
    `declared_geometry_parameter_update_not_inventory_confirmed`
  - `support_shape_or_local_coupling_geometry_change` ->
    `support_shape_update_policy_not_inventory_confirmed`
  - `packet_or_loop_residue_visible_in_existing_state` ->
    `packet_loop_residue_route_memory_not_demonstrated`
  - `route_conductance_memory_metric` ->
    `native_route_conductance_memory_policy_missing`
- Iteration 10 guardrails freeze that the probe must not use:
  - `memory_strength`
  - `memory_shaped_candidate_score`
  - `hidden_route_preference`
  - `report_side_route_history`
  - `unserialized_geometry_state`
- Required Iteration 10 controls:
  - `missing_route_use_event`
  - `missing_geometry_or_topology_event`
  - `hidden_scalar_memory`
  - `stale_geometry_read`
  - `budget_drift`
  - `unsupported_topology_mutation`
  - `claim_promotion`
- All Iteration 9 claim flags remain false. The narrow Hypothesis A
  `memory_or_trail_claim_allowed` does not transfer to Hypothesis B.
- No `src/*` changes were made or required.

Source artifacts:

```text
outputs/n08_iteration_8_mem6_closeout.json
reports/n08_iteration_8_mem6_closeout.md
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json
experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json
implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json
implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json
implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json
implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json
```

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_9_native_geometry_trail_baseline.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_9_native_geometry_trail_baseline.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_9_native_geometry_trail_baseline.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = ac57b1dd11a603ded02fe12446cb3826862d93b252a60358729da1c65346fd95
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_9_native_geometry_trail_baseline.py
  7a20b828bb0ecc2b98ae7cc23e5e49abe8d7bd5bff4dbd757ceba137607ec920

outputs/n08_iteration_9_native_geometry_trail_baseline.json
  d95ed03bca9ad24a2932c711d985a56ee99e67d27dab55e22610047eeab5eeb1

reports/n08_iteration_9_native_geometry_trail_baseline.md
  69fe21ea253d92f9d95f776e14bd08cd04ab41b768fc43a0a0bafb1f2b44d5d8
```

## Iteration 10. Geometry-Mediated Trail Formation

Status: Complete.

- [x] Use prior route use to create a declared topology/geometry/support trace.
- [x] Represent the trace as native topology/geometry/support state, not
      `memory_strength`.
- [x] Candidate trace mechanisms may include edge split, inserted node,
      modified edge geometry, support deformation, or coupling-geometry change.
- [x] Record source route-use digest, topology/geometry event digest, lineage,
      state reabsorption if needed, and exact budget surfaces.
- [x] Verify no hidden scalar trail quantity is introduced.
- [x] Controls: missing route-use event, missing geometry event, hidden scalar
      memory, budget drift, unsupported topology mutation, claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_10_geometry_trail_formation.json`
- [x] `reports/n08_iteration_10_geometry_trail_formation.md`

Acceptance statement:

```text
Iteration 10 passes if prior route use forms a native geometry/topology/support
trace with artifact-visible lineage and exact budgets, without independent
memory-strength storage or claim promotion.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_10_geometry_trail_formation.py`.
- Generated `outputs/n08_iteration_10_geometry_trail_formation.json`.
- Generated `reports/n08_iteration_10_geometry_trail_formation.md`.
- Used the last source-backed MEM1 `route_b` route-use event as the cause:
  `e44cdc336ccfc5adebf42618cfa9fc739f695a5f88c1f787724afb85c8f428ab`.
- Created declared topology trace:
  `edge_split_inserted_node_trace`.
- Inserted native trace node:
  `30`.
- Retired source edge:
  `[1]`.
- Created target edges:
  `1a: 1 -> 30` and `1b: 30 -> 3`.
- Topology event digest:
  `151c581e905f3e30622ed9045daa73a35e6d196f6ac338a38182a55ade793368`.
- Surface lineage record digest:
  `487dcadb5ab432eb15934ac3f2134bf5d79f0e9ec7f217d5014830f2e568f664`.
- Topology-state reabsorption digest:
  `904f907fc9fc5a1fba8440734e7a1b7d90273dd2176ebd8476d753c61729fb23`.
- Theory caveat digest:
  `13ec614426e62f28dadf5883a1793fa8da16f00d509f878f09ec78ee1a42c245`.
- Inserted node initial coherence:
  `0.0`.
- Theory caveat recorded from `RC Distance v4`, `Language of Becoming`, and
  `GRC V3`: zero coherence is not a theory-clean active carrier for ordinary
  RC geometry. The inserted node is therefore a degenerate boundary probe, not
  reinforcement evidence.
- Expected Iteration 11 effect recorded:
  `leakage_or_absorption_into_zero_node_likely_not_reinforcement`.
- Node-plus-packet budget error:
  `0.0`.
- No `memory_strength` was used.
- No memory-shaped candidate score was used.
- No hidden route preference was used.
- No physical flux claim was made.
- Arc-of-Becoming interpretation recorded:
  - question:
    `What becomes available when route-use history is expressed as a declared topology trace instead of serialized memory_strength?`
  - classification:
    `native_geometry_trace_formation_boundary_probe`
  - naturalization rung:
    `Nat1_degenerate_boundary_trace_probe`
  - next question:
    `Does future flux leak into or respond to the zero-coherence topology trace, and what positive-coherence or rebalanced geometry would make a viable native trail?`
- Iteration 10 forms a substrate trace as a boundary probe only. It does not
  claim future flux response, native trail memory closeout, reinforcement,
  ACO, agency, or movement.
- Controls passed with distinct blockers:
  - `missing_route_use_event` -> `missing_route_use_event`
  - `missing_geometry_or_topology_event` ->
    `geometry_or_topology_event_missing`
  - `hidden_scalar_memory` -> `hidden_scalar_memory_blocked`
  - `stale_geometry_read` -> `stale_geometry_read`
  - `budget_drift` -> `node_plus_packet_budget_discontinuity`
  - `unsupported_topology_mutation` -> `unsupported_topology_mutation`
  - `claim_promotion` -> `claim_promotion`
- All claim flags remain false, including:
  `memory_or_trail_claim_allowed`,
  `native_geometry_mediated_trail_claim_allowed`,
  `pure_coherence_flux_trail_claim_allowed`, ACO, agency, semantic choice,
  movement, biological, identity acceptance, and unrestricted claims.
- No `src/*` changes were made or required.

Source artifacts:

```text
outputs/n08_iteration_9_native_geometry_trail_baseline.json
outputs/n08_iteration_3_mem1_route_use_trace.json
experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_7_sc5_repeated_context_selection.json
```

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_10_geometry_trail_formation.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_10_geometry_trail_formation.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_10_geometry_trail_formation.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = 07e03b829759a9df228a651eb77efc3616a5309c33eec6a5ea47fb75568373b9
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_10_geometry_trail_formation.py
  9c0819580d484d202bdefafde10558212803d19cf8bb09595a118d867c2db32e

outputs/n08_iteration_10_geometry_trail_formation.json
  667ffc61c5b59fdf061d82160657a8003bc661d2cf5b9b4cdf08e15fad79b857

reports/n08_iteration_10_geometry_trail_formation.md
  4e6767348c735bf9468d69d2cda7211861ed6fa924cd3b57ebdcf967c0a85b72
```

## Iteration 11. Future Flux Response To Geometry Trace

Status: Complete.

- [x] Run matched lanes with and without the geometry-mediated trail trace.
- [x] Measure whether future flux/routing changes because native dynamics
      follow the changed substrate, or whether the zero-coherence trace becomes
      a leakage/absorption site.
- [x] Treat the zero-coherence inserted node as a theory-caveated boundary
      probe, not as reinforcement evidence.
- [x] Compare the zero-node trace against at least one positive-coherence or
      rebalanced follow-up design candidate if the zero node behaves as a
      sink/leak.
- [x] Verify the changed route response is not produced by candidate score
      bookkeeping or hidden route preference.
- [x] Record route/flux deltas, source topology/geometry digests, packet/loop
      state, inserted-node coherence deltas, and budget surfaces.
- [x] Controls: hidden route preference, score-only memory input, stale
      geometry read, order inversion, budget drift, claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_11_geometry_trace_flux_response.json`
- [x] `reports/n08_iteration_11_geometry_trace_flux_response.md`

Acceptance statement:

```text
Iteration 11 passes if future flux/routing behavior around the declared
geometry/topology/support trace is source-backed and classified without
promotion: either as leakage/absorption into the zero-coherence boundary probe,
as avoidance/no-response, or as a stronger response from a positive-coherence
or rebalanced geometry candidate, with no independent memory scalar, no hidden
steering, and exact budgets.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_11_geometry_trace_flux_response.py`.
- Generated `outputs/n08_iteration_11_geometry_trace_flux_response.json`.
- Generated `reports/n08_iteration_11_geometry_trace_flux_response.md`.
- Used Iteration 10 topology event as the source trace:
  `151c581e905f3e30622ed9045daa73a35e6d196f6ac338a38182a55ade793368`.
- Used Iteration 10 theory caveat:
  `13ec614426e62f28dadf5883a1793fa8da16f00d509f878f09ec78ee1a42c245`.
- Ran three matched lanes:
  - `no_trace_control`
  - `zero_coherence_trace`
  - `positive_rebalanced_trace_design`
- Response summary:
  - classification:
    `zero_trace_leakage_boundary_with_positive_rebalanced_design_direction`
  - zero-trace inserted-node delta:
    `0.1`
  - zero-trace leakage fraction:
    `1.0`
  - zero-trace target-delivery fraction:
    `0.0`
  - no-trace target-delivery fraction:
    `1.0`
  - positive-rebalanced target-delivery fraction:
    `1.0`
  - positive-rebalanced leakage fraction:
    `0.0`
- Primary observation: the Iteration 10 zero-coherence trace behaves as an
  absorber/leakage site under the serialized diagnostic response probe, not as
  reinforcement.
- Positive/rebalanced design direction recorded:
  `coherence_split_preserving_positive_trace_can_transit_probe_packet`.
- Claim ceiling:
  `diagnostic_geometry_trace_response_boundary_probe`.
- Native policy blocker remains:
  `native_route_conductance_memory_policy_missing`.
- Arc-of-Becoming interpretation recorded:
  - question:
    `What does future flux become when it encounters the Iteration 10 zero-coherence topology trace?`
  - naturalization rung:
    `Nat2_response_boundary_classified`
  - next question:
    `Can a positive-coherence, geometry-mediated trace shape future route arbitration through native-visible geometry rather than through a diagnostic response probe?`
- Next iteration pointer updated to:
  `11-A_positive_coherence_geometry_route_arbitration_response`.
- No `memory_strength` was used.
- No memory-shaped candidate score was used.
- No hidden route preference was used.
- No native geometry-mediated trail claim was made.
- Controls passed with distinct blockers:
  - `hidden_route_preference` -> `hidden_route_preference_blocked`
  - `score_only_memory_input` -> `score_only_memory_input_blocked`
  - `stale_geometry_read` -> `stale_geometry_read`
  - `order_inversion` -> `future_response_order_inversion`
  - `budget_drift` -> `node_plus_packet_budget_discontinuity`
  - `missing_positive_followup_design` ->
    `positive_coherence_followup_design_missing`
  - `claim_promotion` -> `claim_promotion`
- All claim flags remain false, including:
  `memory_or_trail_claim_allowed`,
  `native_geometry_mediated_trail_claim_allowed`,
  `pure_coherence_flux_trail_claim_allowed`, ACO, agency, semantic choice,
  movement, biological, identity acceptance, and unrestricted claims.
- No `src/*` changes were made or required.

Source artifacts:

```text
outputs/n08_iteration_10_geometry_trail_formation.json
reports/n08_iteration_10_geometry_trail_formation.md
outputs/n08_iteration_9_native_geometry_trail_baseline.json
```

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_11_geometry_trace_flux_response.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_11_geometry_trace_flux_response.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_11_geometry_trace_flux_response.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = 09d76bed44960151fe9ca0a01321dfb6f17bdb83bb5cd0d86074d4f7ba5fe7a1
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_11_geometry_trace_flux_response.py
  879f5a0a1ad59662ea08e3921b5768aa6a50f66b1d1dbae59b0c99ccb29a50de

outputs/n08_iteration_11_geometry_trace_flux_response.json
  26c446c8d3a21397fa0073c0451ba4dcd5330d269c6fe17d9660955feb8d50b9

reports/n08_iteration_11_geometry_trace_flux_response.md
  0b5acbfa4320340198851b896dd61462131d26cb8441a32dc48e3c752c66c72e
```

## Iteration 11-A. Positive-Coherence Geometry Route Arbitration Response

Status: Complete.

- [x] Use the Iteration 11 leakage result to define a positive-coherence
      geometry response probe.
- [x] Compare no-trace, zero-trace, and positive-rebalanced trace lanes.
- [x] Require no-trace route arbitration to fail closed as unresolved tie.
- [x] Require zero-trace route `route_b` to be blocked as
      `zero_coherence_trace_absorber`.
- [x] Require positive-rebalanced trace route `route_b` to be selected through
      runtime-visible geometry score components.
- [x] Verify no `memory_strength`, memory-shaped candidate score, hidden route
      preference, or report-side route history is used.
- [x] Record the remaining native blocker for pure flux/conductance trail
      memory.
- [x] Controls: hidden route preference, memory-strength input, zero trace as
      reinforcement, missing positive-coherence carrier, unresolved tie without
      geometry, stale geometry read, budget drift, route-conductance overclaim,
      claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_11a_positive_geometry_route_arbitration.json`
- [x] `reports/n08_iteration_11a_positive_geometry_route_arbitration.md`

Acceptance statement:

```text
Iteration 11-A passes if a conserved positive-coherence geometry trace changes
future native route arbitration through runtime-visible geometry evidence,
while no trace remains unresolved, the zero trace remains blocked as absorber,
and no memory-strength, hidden preference, pure flux trail, ACO, agency,
movement, identity, or claim-promotion flag is emitted.
```

Acceptance result: Achieved.

Implementation record:

- Added `scripts/run_n08_iteration_11a_positive_geometry_route_arbitration.py`.
- Generated
  `outputs/n08_iteration_11a_positive_geometry_route_arbitration.json`.
- Generated
  `reports/n08_iteration_11a_positive_geometry_route_arbitration.md`.
- Source Iteration 11 output digest:
  `09d76bed44960151fe9ca0a01321dfb6f17bdb83bb5cd0d86074d4f7ba5fe7a1`.
- Ran three route-arbitration lanes:
  - `no_trace_control`
  - `zero_coherence_trace`
  - `positive_rebalanced_trace_design`
- No-trace result:
  `native_route_arbitration_unresolved_tie`.
- Zero-trace result:
  `route_b` was blocked with `zero_coherence_trace_absorber`; fallback
  `route_a` was selected.
- Positive-rebalanced trace result:
  `route_b` was selected through geometry-derived score components.
- Geometry score components:
  - `budget_validity`
  - `lineage_ready`
  - `positive_coherence_path_support`
  - `source_geometry_trace_match`
- Response summary classification:
  `positive_coherence_geometry_route_arbitration_candidate`.
- Claim ceiling:
  `positive_coherence_geometry_route_response_candidate`.
- Hypothesis B answer scope:
  `routing_response_candidate_not_pure_flux_trail_closeout`.
- Native route arbitration reads geometry evidence:
  `true`.
- Remaining native blocker:
  `native_route_conductance_memory_policy_missing`.
- Arc-of-Becoming interpretation recorded:
  - question:
    `Can the Hypothesis B trace be expressed as positive-coherence geometry evidence that changes future route arbitration without serialized memory strength?`
  - naturalization rung:
    `Nat3_positive_geometry_route_response_candidate`
  - next question:
    `Does the positive-coherence geometry route-response candidate persist, relax, or require a native route-conductance memory policy before it can become a trail-memory closeout?`
- No `memory_strength` was used.
- No memory-shaped candidate score was used.
- No hidden route preference was used.
- No report-side route history was used.
- No native geometry-mediated trail closeout or pure flux trail-memory claim was
  made.
- Controls passed with distinct blockers:
  - `hidden_route_preference` -> `hidden_route_preference_blocked`
  - `memory_strength_input` -> `memory_strength_input_blocked`
  - `zero_trace_as_reinforcement` -> `zero_trace_reinforcement_blocked`
  - `missing_positive_coherence_carrier` -> `positive_coherence_carrier_missing`
  - `unresolved_tie_without_geometry` ->
    `native_route_arbitration_unresolved_tie`
  - `stale_geometry_read` -> `stale_geometry_read`
  - `budget_drift` -> `node_plus_packet_budget_discontinuity`
  - `route_conductance_policy_overclaim` ->
    `native_route_conductance_memory_policy_missing`
  - `claim_promotion` -> `claim_promotion`
- All claim flags remain false, including:
  `memory_or_trail_claim_allowed`,
  `native_geometry_mediated_trail_claim_allowed`,
  `pure_coherence_flux_trail_claim_allowed`, ACO, agency, semantic choice,
  movement, biological, identity acceptance, and unrestricted claims.
- No `src/*` changes were made or required.

Source artifacts:

```text
outputs/n08_iteration_10_geometry_trail_formation.json
outputs/n08_iteration_11_geometry_trace_flux_response.json
reports/n08_iteration_11_geometry_trace_flux_response.md
```

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_11a_positive_geometry_route_arbitration.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_11a_positive_geometry_route_arbitration.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_11a_positive_geometry_route_arbitration.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
output_digest = 2907ea12a71f12f25c60ea13fb0a53053aceca3b070480a84f88871606d1e759
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_11a_positive_geometry_route_arbitration.py
  72f77e46190724e97e6294123f9825baf098ae070911399f3ff2b90c2620f47f

outputs/n08_iteration_11a_positive_geometry_route_arbitration.json
  8e4c752625edc9607309f772f0aa229001550552cbaabc5b8b1641bf19e0b5da

reports/n08_iteration_11a_positive_geometry_route_arbitration.md
  c5035ac0702521b1b6d2f60542969c96e4762dd84783ce5438a9a76f6cf53dce
```

## Iteration 12. Native Trace Persistence And Relaxation

Status: Complete.

- [x] Test whether the geometry-mediated trail persists, relaxes, or is
      reabsorbed over repeated windows.
- [x] If relaxation/decay moves mass, require an explicit conserved destination
      surface.
- [x] If relaxation is non-physical geometry/policy relaxation, record it as
      non-flux and keep pure flux claims blocked.
- [x] Track route response over repeated windows and compare against no-trace
      control.
- [x] Controls: missing destination surface, silent mass deletion, hidden
      relaxation policy, duplicate relaxation, budget drift, claim promotion.

Expected artifacts:

- [x] `outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json`
- [x] `reports/n08_iteration_12_geometry_trace_persistence_relaxation.md`

Acceptance statement:

```text
Iteration 12 passes if the native geometry-mediated trail persistence or
relaxation behavior is replayable, budget-safe, and explicitly classified as
physical flux with a conserved destination or non-physical geometry relaxation
with pure flux claims blocked.
```

Acceptance result: Achieved with a bounded classification.

Implementation record:

- Added
  `scripts/run_n08_iteration_12_geometry_trace_persistence_relaxation.py`.
- Generated
  `outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json`.
- Generated
  `reports/n08_iteration_12_geometry_trace_persistence_relaxation.md`.
- Source fixture:
  `outputs/n08_iteration_11a_positive_geometry_route_arbitration.json`.
- Repeated-window probe:
  - Four repeated windows were replayed from the Iteration 11-A positive
    geometry route-response candidate.
  - Each window selected `route_b`.
  - The selected-route sequence was
    `["route_b", "route_b", "route_b", "route_b"]`.
  - Candidate route score remained `1.0` in every window.
  - The positive geometry digest remained stable across all windows.
  - Node-plus-packet budget error remained `0.0` in every window.
- Comparator controls:
  - No-trace comparator remained blocked by
    `native_route_arbitration_unresolved_tie`.
  - Zero-trace comparator route B remained blocked by
    `zero_coherence_trace_absorber`.
- Classification:
  `static_positive_geometry_route_response_persistence_candidate`.
- Claim ceiling:
  `static_positive_geometry_route_response_persistence_candidate`.
- Interpretation:
  - The positive route response persists when the declared geometry is held
    fixed.
  - This is static geometry persistence, not adaptive trail memory.
  - No route strengthening, route conductance update, physical relaxation, or
    non-physical relaxation was applied.
  - Physical relaxation/decay remains blocked unless an explicit conserved
    destination surface exists.
  - Non-physical geometry/policy relaxation remains blocked unless serialized
    as a policy and kept outside pure flux claims.
  - The active native-policy blocker remains
    `native_route_conductance_memory_policy_missing`.
- Relaxation audit:
  - `physical_relaxation_performed = false`
  - `nonphysical_relaxation_performed = false`
  - `relaxation_policy_available = false`
  - `relaxation_status = not_applied_policy_missing`
  - `missing_destination_surface_blocked = true`
  - `silent_mass_deletion_blocked = true`
  - `native_conductance_decay_policy_missing = true`
- Controls and blockers:
  - `missing_destination_surface` ->
    `missing_relaxation_destination_surface`
  - `silent_mass_deletion` -> `silent_mass_deletion_blocked`
  - `hidden_relaxation_policy` -> `hidden_relaxation_policy_blocked`
  - `duplicate_relaxation` -> `duplicate_relaxation_blocked`
  - `budget_drift` -> `node_plus_packet_budget_discontinuity`
  - `hidden_route_preference` -> `hidden_route_preference_blocked`
  - `memory_strength_input` -> `memory_strength_input_blocked`
  - `route_conductance_policy_overclaim` ->
    `native_route_conductance_memory_policy_missing`
  - `claim_promotion` -> `claim_promotion`
- Claim boundary:
  - `memory_or_trail_claim_allowed = false`
  - `native_geometry_mediated_trail_claim_allowed = false`
  - `pure_coherence_flux_trail_claim_allowed = false`
  - `aco_like_claim_allowed = false`
  - `agency_claim_allowed = false`
  - `agentic_like_claim_allowed = false`
  - `ant_colony_claim_allowed = false`
  - `biological_claim_allowed = false`
  - `goal_proxy_regulation_claim_allowed = false`
  - `identity_acceptance_claim_allowed = false`
  - `intention_claim_allowed = false`
  - `locomotion_like_claim_allowed = false`
  - `movement_claim_allowed = false`
  - `personhood_claim_allowed = false`
  - `rc_identity_collapse_claim_allowed = false`
  - `runtime_identity_acceptance_claim_allowed = false`
  - `semantic_choice_claim_allowed = false`
  - `unrestricted_identity_claim_allowed = false`
  - `unrestricted_movement_claim_allowed = false`
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_12_geometry_trace_persistence_relaxation.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_12_geometry_trace_persistence_relaxation.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact_digest = 0fc4a8a98509068a7926d562d2999289aaa8a934a144229195221b9ed68813f6
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_12_geometry_trace_persistence_relaxation.py
  c06d7685ea69273e467a21770f6ee4023d2e1db1e0ebdabd23517939c4b63667

outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json
  deffdf7ea8fa9da25ec20c04459eff48c85f36c4dd7fad8e370a1136123a218f

reports/n08_iteration_12_geometry_trace_persistence_relaxation.md
  9c1e7bf1e19b02c4b53575b04dba019bb5353630789aad4fbf3aa0ed23ea3542
```

## Iteration 13. Native Geometry-Mediated Trail Replay And Closeout

Status: Complete.

- [x] Replay route use, geometry/topology/support trace formation, future
      flux/routing response, persistence/relaxation, and controls from
      artifacts only.
- [x] Recompute topology/geometry/support digests and route/flux deltas.
- [x] Verify no independent `memory_strength` or hidden route history is needed.
- [x] Freeze strongest Hypothesis B ceiling.
- [x] Record blockers for native geometry-mediated trail memory if unresolved.
- [x] Preserve ACO, agency, intention, regulation, identity acceptance,
      locomotion, biological, personhood, and unrestricted claims as blocked.

Expected artifacts:

- [x] `outputs/n08_iteration_13_native_geometry_trail_closeout.json`
- [x] `reports/n08_iteration_13_native_geometry_trail_closeout.md`

Acceptance statement:

```text
Iteration 13 passes if the native geometry-mediated route-trail chain can be
reconstructed from artifacts only, either freezing a
native_geometry_mediated_route_trail_candidate ceiling or recording explicit
native blockers, while preserving all stronger ACO, agency, identity,
locomotion, biological, and unrestricted claims as blocked.
```

Acceptance result: Achieved with bounded Hypothesis B closeout.

Implementation record:

- Added `scripts/run_n08_iteration_13_native_geometry_trail_closeout.py`.
- Generated `outputs/n08_iteration_13_native_geometry_trail_closeout.json`.
- Generated `reports/n08_iteration_13_native_geometry_trail_closeout.md`.
- Artifact-only replay sources:
  - Iteration 8 Hypothesis A MEM6 closeout.
  - Iteration 9 native geometry mechanism inventory and entry gate.
  - Iteration 10 route-use event and geometry trace topology event.
  - Iteration 11 zero-trace response classification.
  - Iteration 11-A positive geometry route-arbitration response.
  - Iteration 12 static positive geometry response persistence windows.
- Replay chain:
  - `iteration_9_entry_gate` ->
    `edge_split_inserted_node_trace_entry_allowed`
  - `route_use_source_event` -> `route_b`
  - `geometry_trace_topology_event` -> `edge_split_inserted_node_trace`
  - `zero_trace_response_classification` ->
    `zero_coherence_trace_behaves_as_absorber`
  - `positive_geometry_route_arbitration_response` -> `route_b`
  - `static_positive_geometry_response_persistence` ->
    `["route_b", "route_b", "route_b", "route_b"]`
- Hypothesis A closeout preserved:
  - `hypothesis_a_claim_ceiling =
    artifact_only_route_memory_or_trail_affordance_candidate`
  - `hypothesis_a_scoped_memory_or_trail_claim_allowed = true`
  - `hypothesis_a_claim_scope =
    artifact_only_serialized_producer_policy_route_memory_or_trail`
- Hypothesis B closeout frozen:
  - `hypothesis_b_claim_ceiling =
    static_positive_geometry_route_response_persistence_candidate`
  - `hypothesis_b_current_blocker =
    native_route_conductance_memory_policy_missing`
  - `hypothesis_b_native_geometry_mediated_trail_claim_allowed = false`
  - `hypothesis_b_pure_coherence_flux_trail_claim_allowed = false`
- Interpretation:
  - Hypothesis B is a roadmap-aligned scaffold/native-policy-gap result.
  - Declared positive geometry can shape native route arbitration and persist
    as a static response.
  - Current LGRC does not yet provide native conductance update,
    strengthening, or relaxation policy.
  - The result does not change RC field mechanics and does not claim native
    route-conductance memory.
- Controls and blockers:
  - `missing_source_artifact` -> `source_artifact_missing`
  - `digest_mismatch` -> `source_artifact_digest_mismatch`
  - `event_order_inversion` -> `hypothesis_b_replay_order_invalid`
  - `hidden_memory_strength` -> `memory_strength_input_blocked`
  - `zero_trace_overclaim` -> `zero_trace_reinforcement_blocked`
  - `missing_positive_geometry_response` ->
    `positive_geometry_route_response_missing`
  - `missing_static_persistence` ->
    `static_geometry_response_persistence_missing`
  - `budget_discontinuity` -> `node_plus_packet_budget_discontinuity`
  - `route_conductance_policy_overclaim` ->
    `native_route_conductance_memory_policy_missing`
  - `claim_promotion` -> `claim_promotion`
- No `src/*` changes were made or required.

Replay and validation commands:

```bash
.venv/bin/python experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_13_native_geometry_trail_closeout.py
jq empty experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_13_native_geometry_trail_closeout.json
.venv/bin/python -m py_compile experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/run_n08_iteration_13_native_geometry_trail_closeout.py
git diff --check -- experiments/2026-05-N08-lgrc-memory-trail-affordance
git status --short src
```

Validation result:

```text
status = passed
all artifact checks passed
jq empty passed
py_compile passed
git diff --check passed
git status --short src produced no output
artifact_digest = 45351727bc12b243b62f8562f38c541029c46ccc443e67707fcb3280cd95153e
```

Artifact SHA-256:

```text
scripts/run_n08_iteration_13_native_geometry_trail_closeout.py
  fd46faf7d1754555b69f0a624c4abb3c6dc0fa64917d4e55975d58d88ea93dde

outputs/n08_iteration_13_native_geometry_trail_closeout.json
  505181543e19f2e046b40399cb1e1441ad9d3f13077a607d3232d9639f457bfa

reports/n08_iteration_13_native_geometry_trail_closeout.md
  d8916078bf5b7ea5016514641b53436f2a1695071c27aa2c14a4aafe2445a4f1
```
