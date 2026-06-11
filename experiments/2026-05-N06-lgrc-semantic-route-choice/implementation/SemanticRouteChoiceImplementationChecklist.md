# N06 Semantic Route Choice Implementation Checklist

This checklist tracks implementation of
`2026-05-N06-lgrc-semantic-route-choice`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N06 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N05 O5 as oscillator/circuit background only.
- [ ] Treat N05 O6 as blocked by `missing_route_conductance_memory_policy`.
- [ ] Treat N06 as semantic route-choice evidence only.
- [ ] Do not treat native route arbitration alone as semantic choice.
- [ ] Keep memory/trail formation deferred to N08.
- [ ] Keep producer scheduling labeled as scheduling/evidence, not agency.
- [ ] Keep `step()` as the packet mutation boundary.
- [ ] Preserve node-plus-packet budget accounting for every run.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Record SHA-256 digests for positive fixture artifacts.
- [ ] Keep all claim flags false unless a later experiment separately validates
  them.

## Iteration 0. Planning And Handoff

Status: Complete.

- [x] Create N06 experiment stub.
- [x] Create N06 root README.
- [x] Create implementation README.
- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Record N05 inherited ceiling:
  `self_sustained_oscillator_candidate`.
- [x] Record N05 O6 blocker:
  `missing_route_conductance_memory_policy`.
- [x] Record that N06 does not prove memory, trail, ACO, agency, identity,
  regulation, or locomotion.
- [x] Record that native route arbitration is infrastructure, not semantic
  choice by itself.

Acceptance statement:

```text
N06 starts from a clean claim boundary: N05 supplies oscillator/circuit
background, while N06 opens only context-conditioned semantic route-choice
evidence. Native route arbitration is allowed as runtime selection
infrastructure, but semantic route-choice claims require serialized
runtime-visible context or affordance evidence and artifact replay.
```

## Iteration 1. Baseline And Schema Inventory

Status: Complete.

- [x] Inventory N05 closeout artifacts that may be cited.
- [x] Inventory available native route-arbitration surfaces:
  - [x] candidate route records
  - [x] candidate set records
  - [x] native route-arbitration records
  - [x] selected candidate digest fields
  - [x] rejected candidate digest fields
  - [x] candidate budget prediction fields
  - [x] candidate lineage map fields where topology-changing routes are used
  - [x] route-arbitration artifact replay support
- [x] Inventory available context/affordance surfaces.
- [x] Map N06 context/affordance surface to native fields:
  - [x] `candidate_score_components`
  - [x] `candidate_runtime_visible_inputs`
  - [x] `arbitration_runtime_visible_inputs`
  - [x] causal pulse-substrate surface rows, if used
  - [x] route-aspect mass/polarity/channel fields, if used
- [x] Record preferred Iteration 2 native context mapping:
  `candidate_score_components` plus `candidate_runtime_visible_inputs` and
  `arbitration_runtime_visible_inputs`.
- [x] Record mapping elimination criteria for hidden, report-side,
  non-replayable, or experiment-local-only context sources.
- [x] Record whether native N06 lanes run entirely at LGRC-3 or whether early
  LGRC-2 lanes are experiment-local scaffolds.
- [x] Inventory native route-arbitration causal-mode requirements:
  - [x] `lgrc_runtime_level = lgrc3`
  - [x] `causal_layer_mode = topology_changing_causal_history`
  - [x] `causal_topology_integration_allowed = true`
  - [x] supported surface-lineage transport
  - [x] supported topology-state reabsorption
- [x] Inventory `validate_lgrc9v3_native_route_arbitration_artifacts(...)`
  signature, required inputs, and failure modes.
- [x] Record native validator failure-mode mapping to primary blockers.
- [x] Record that `candidate_route_score ==
  sum(candidate_score_components)` is enforced by the native candidate-record
  contract.
- [x] Record candidate-set ordering keys, default N06 ordering, and
  unresolved-tie serialization fields.
- [x] Record native route-arbitration policy as configurable, with
  `score_ordered_topology_route_candidates` as N06's preferred default, not a
  hard gate.
- [x] Record route-intent classes and the `redirect` caveat.
- [x] Record N04/Phase 8 route-arbitration artifacts as upstream contract
  precedent/source provenance, not N06 evidence.
- [x] Freeze SC-ladder row schema.
- [x] Freeze blocked claim flags:
  - [x] `semantic_choice_claim_allowed = false`
  - [x] `memory_or_trail_claim_allowed = false`
  - [x] `movement_claim_allowed = false`
  - [x] `agency_claim_allowed = false`
  - [x] `agentic_like_claim_allowed = false`
  - [x] `rc_identity_collapse_claim_allowed = false`
  - [x] `identity_acceptance_claim_allowed = false`
  - [x] `goal_proxy_regulation_claim_allowed = false`
  - [x] `locomotion_like_claim_allowed = false`
  - [x] `biological_claim_allowed = false`
  - [x] `ant_colony_claim_allowed = false`
  - [x] `unrestricted_movement_claim_allowed = false`
- [x] Define `semantic_route_choice_report_v1`.
- [x] Define baseline JSON row schema for SC0-SC6 evidence.
- [x] Require every row to include:
  - [x] `sc_level`
  - [x] `sc_level_is_evidence_classification = true`
  - [x] `claim_ceiling`
  - [x] `claim_flags`
  - [x] `lgrc_runtime_level`
  - [x] `source_native_surfaces`
  - [x] `candidate_route_digests`
  - [x] `candidate_set_digest`
  - [x] `context_surface_digest`
  - [x] `selected_candidate_route_digest`
  - [x] `rejected_candidate_route_digests`
  - [x] `event_time_key`
  - [x] `scheduler_event_index`
  - [x] `node_proper_time` where available
  - [x] `selection_rule`
  - [x] `selection_reason_code`
  - [x] `producer_boundary`
  - [x] `claim_boundary`
- [x] Verify no route-choice probes are run in this iteration.
- [x] Verify no `src/*` changes are needed.

Expected artifacts:

- [x] `outputs/n06_iteration_1_baseline_inventory.json`
- [x] `reports/n06_iteration_1_baseline_inventory.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/build_n06_iteration_1_baseline_inventory.py
```

Result:

```json
{"claim_flags_frozen_false": true, "context_surface_dedicated_native_type": false, "native_runtime_level": "lgrc3", "output": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_1_baseline_inventory.json", "report": "experiments/2026-05-N06-lgrc-semantic-route-choice/reports/n06_iteration_1_baseline_inventory.md", "route_choice_probe_run": false, "status": "passed"}
```

Artifact digests:

```json
{
  "claim_boundary_digest": "ffcf9f3262407e22fdad4c175e46b4759fe8ef86a17e7349c3442493bbe53607",
  "context_affordance_inventory_digest": "843d173ca5132180492f36dd40c087eb1142a3462737a218052e77f4592cc294",
  "native_route_arbitration_surfaces_digest": "53ef97f95efd039d518fedcfa50108f052ef6beaf2c2250a58ef695e7573cb95",
  "sc_ladder_schema_digest": "4ac6a7742fd5dcd167506e3a0f4fbc3ec063274fe1943961b5f574e32c7c9396",
  "source_artifacts_digest": "d6125fd11ca305ee7235b9e60ae8509cdba8839c3e174234fb1b4e4125ca5934"
}
```

Generated file SHA-256:

```text
b4e49ad42ac687b3e63254af727d166b27fab0f074b12e4ed92b3f2db56ef317  outputs/n06_iteration_1_baseline_inventory.json
d2117e25186949a2b61dfe13f9df2aefc8e5821eef766841489a08bbd1d49bb0  reports/n06_iteration_1_baseline_inventory.md
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_1_baseline_inventory.json
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/build_n06_iteration_1_baseline_inventory.py
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_1_baseline_inventory.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['route_choice_probe_run'] is False; assert d['n05_inheritance']['strongest_supported_o_level']=='O5'; assert d['n05_inheritance']['o6_route_coupled_oscillator_supported'] is False; assert d['native_route_arbitration_surfaces']['native_runtime_gate']['lgrc_runtime_level']=='lgrc3'; assert d['native_route_arbitration_surfaces']['native_runtime_gate']['lgrc2_native_route_arbitration_allowed'] is False; assert d['context_affordance_inventory']['dedicated_native_context_surface_exists'] is False; assert d['claim_boundary']['claim_flags']['semantic_choice_claim_allowed'] is False; assert d['acceptance']['no_route_choice_probe_run'] is True; assert all(v is False for v in d['claim_boundary']['claim_flags'].values()); print({'status': d['status'], 'probe': d['route_choice_probe_run'], 'native_runtime': d['native_route_arbitration_surfaces']['native_runtime_gate']['lgrc_runtime_level'], 'context_surface_native': d['context_affordance_inventory']['dedicated_native_context_surface_exists'], 'semantic_choice_flag': d['claim_boundary']['claim_flags']['semantic_choice_claim_allowed'], 'claim_flags_false': d['acceptance']['claim_flags_frozen_false']})"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_1_baseline_inventory.json'; d=json.load(open(p)); assert d['native_route_arbitration_surfaces']['native_route_arbitration_contract']['validator_failure_modes']; assert d['context_affordance_inventory']['preferred_default_native_mapping_for_iteration_2']['score_surface']=='candidate_score_components'; assert d['native_route_arbitration_surfaces']['native_runtime_gate']['native_lgrc_route_arbitration_policy_gate']=='policy != disabled'; assert d['native_route_arbitration_surfaces']['native_runtime_gate']['n06_default_native_lgrc_route_arbitration_policy']=='score_ordered_topology_route_candidates'; assert d['sc_ladder_schema']['minimum_runtime_level_by_sc']['SC1']['experiment_local_or_control'].startswith('lgrc2_allowed'); assert d['claim_boundary']['claim_flags']['movement_claim_allowed'] is False; print('hardened_inventory_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- Iteration 1 is inventory-only:
  `route_choice_probe_run = false`.
- N06 inherits only N05 oscillator/circuit background:
  `strongest_supported_o_level = O5`,
  `strongest_claim_ceiling = self_sustained_oscillator_candidate`.
- N05 O6 remains blocked by
  `missing_route_conductance_memory_policy`; N06 does not inherit memory/trail
  claims.
- Native route-arbitration rows are LGRC-3/topology-changing-causal-history
  gated. LGRC-2 rows may be experiment-local scaffolds or controls only.
- The current native contract has no dedicated `context_surface` record type.
  Iteration 2 must choose a concrete mapping to native score/runtime-visible
  input fields or explicitly label an experiment-local compatibility gate.
- The artifact inventories
  `validate_lgrc9v3_native_route_arbitration_artifacts(...)` with required
  inputs `events`, `candidate_route_records`, `candidate_set_records`, and
  `route_arbitration_records`.
- The artifact now records validator failure modes, native score-component
  score invariants, candidate-set ordering, unresolved-tie serialization, and
  the preferred N06 default policy as `score_ordered_topology_route_candidates`.
- N06's preferred Iteration 2 context mapping is native score components plus
  candidate/arbitration runtime-visible inputs. Other mappings require a
  blocker or experiment-local label.
- N04/Phase 8 route-arbitration artifacts are recorded as upstream contract
  precedent and source provenance only, not as N06 semantic route-choice
  evidence.
- Broad `semantic_choice_claim_allowed` remains false at baseline. A later
  scoped `semantic_route_choice_candidate` must still pass context-conditioned
  arbitration and artifact replay.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 1 passes if N06 has a source-backed baseline inventory, frozen
SC-ladder row schema, explicit blocked claim flags, and no new route-choice
probe evidence or claim promotion.
```

Acceptance result: Achieved.

Confirmation:

```json
{"claim_flags_frozen_false": true, "context_surface_dedicated_native_type": false, "native_runtime_level": "lgrc3", "route_choice_probe_run": false, "semantic_choice_claim_allowed": false, "status": "passed"}
```

## Iteration 2. Fixture Manifest And Controls

Status: Complete.

- [x] Define minimal source-plus-two-routes fixture.
- [x] Define route candidate ids, source node, sink/target nodes, and edge ids.
- [x] Define context/affordance surface.
- [x] Define context states A and B.
- [x] Define context relation:
  `route matches active context/affordance`.
- [x] Use the preferred native context mapping by default:
  `candidate_score_components`, `candidate_runtime_visible_inputs`, and
  `arbitration_runtime_visible_inputs`; otherwise record a blocker or label the
  row experiment-local.
- [x] Declare context-to-score-component derivation from runtime-visible
  context/source artifacts.
- [x] Define how compatibility gates are expressed:
  native score components with threshold interpretation or experiment-local
  gate records.
- [x] Verify candidate scores equal the sum of native score components.
- [x] Define arbitration window boundary:
  scheduler index range, event-time range, or producer invocation boundary.
- [x] Map arbitration window start/end labels to concrete artifact kinds.
- [x] Declare `causal_epoch`, `checkpoint_index`, and scheduler/event-order
  timing expectations for later rows.
- [x] Specify candidate source evidence fields:
  - [x] `candidate_source_surface_digest`
  - [x] `candidate_source_producer_record_id`, if used
  - [x] `candidate_source_topology_state_reabsorption_digest`, if used
- [x] Record that `candidate_source_topology_state_reabsorption_digest` is not
  required for the first pre-topology SC1 candidate set, and is required only
  for post-topology candidate sources.
- [x] Define Iteration 3 transition criteria from symbolic source evidence to
  committed runtime source evidence.
- [x] Declare route intent values:
  - [x] `redirect` or other fixed-route/control intent, if experiment-local
  - [x] `collapse|reabsorb|split|merge` or other topology-changing intent, if
    native LGRC-3 route arbitration is used
- [x] Declare expected selected topology event behavior:
  authorized-only in selection artifacts or committed in the same lane.
- [x] Define candidate completeness rule for arbitration windows.
- [x] Define deterministic candidate ordering.
- [x] Declare candidate-set order key:
  `score_desc_then_candidate_id` by default, or another serialized native
  order key with rationale.
- [x] Declare unresolved-tie handling and the serialized fields that implement
  any deterministic tiebreaker.
- [x] Define budget tolerance.
- [x] Verify validator uses declared budget tolerance for candidate budget
  predictions.
- [x] Define default-off policy behavior.
- [x] Record default-off causal-mode coupling:
  `LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED` requires
  `native_lgrc_route_arbitration_enabled = false`.
- [x] Define native route-arbitration policy fields.
- [x] Declare the full native dependency chain:
  surface enabled/validated, lineage enabled/validated/supported, and
  topology-state reabsorption enabled/validated/supported.
- [x] Record the preferred native policy
  `score_ordered_topology_route_candidates`, while keeping the actual gate as
  `native_lgrc_route_arbitration_policy != disabled`.
- [x] Define negative controls:
  - [x] policy disabled
  - [x] no candidates
  - [x] unresolved tie
  - [x] hidden context
  - [x] hidden route preference
  - [x] preselected sink
  - [x] experiment-side if/else
  - [x] report-side selection
  - [x] post-hoc threshold change
  - [x] budget mismatch
  - [x] order inversion
  - [x] stale candidate
  - [x] stale context
  - [x] duplicate arbitration
  - [x] producer mutation
  - [x] claim promotion
- [x] Add fixture/manifest validator.
- [x] Record validator command and output.

Expected artifacts:

- [x] `configs/n06_fixture_manifest_v1.json`
- [x] `outputs/n06_iteration_2_fixture_manifest_validation.json`
- [x] `reports/n06_iteration_2_fixture_manifest_validation.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/validate_n06_fixture_manifest.py
```

Result:

```json
{"checks_passed": true, "controls_declared": true, "manifest": "experiments/2026-05-N06-lgrc-semantic-route-choice/configs/n06_fixture_manifest_v1.json", "output": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_2_fixture_manifest_validation.json", "report": "experiments/2026-05-N06-lgrc-semantic-route-choice/reports/n06_iteration_2_fixture_manifest_validation.md", "route_choice_probe_run": false, "status": "passed"}
```

Artifact digests:

```json
{
  "checks_digest": "ddb0daf35dce931b7eccbd4547847555fcb98673d9084b34669ebfbd91857dac",
  "claim_boundary_digest": "7feec93231b69202decd5f141c241beaadd079826dd526ee9d2311891c8bd0eb",
  "controls_digest": "c073476ab4fab609e5f90644d43e34e4a16e88effa9bf6ef5987fe5a4780a4c7",
  "manifest_digest": "69175ec19d0a43223b726348e0e98cbdd13244b3d7533b6323236405ba7cd7f5"
}
```

Generated file SHA-256:

```text
867a2bb464bbbdc0c782f334cf3bb9821b3d8f60d792dceab4644695b947363b  configs/n06_fixture_manifest_v1.json
2e54ea5f149e92e7ef9fd31965eeb1070f36d73e23d4f3c25a014e69594dd70e  outputs/n06_iteration_2_fixture_manifest_validation.json
8ca7271eb57d59f26c0901a0286e56f5e54ddadd1337a0f5d89d43a23541ac20  reports/n06_iteration_2_fixture_manifest_validation.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/validate_n06_fixture_manifest.py
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_2_fixture_manifest_validation.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['route_choice_probe_run'] is False; assert d['checks']['context_a_b_select_different_routes'] is True; assert d['checks']['candidate_scores_equal_component_sums'] is True; assert d['checks']['control_blockers_are_distinct'] is True; assert d['checks']['default_off_policy_declared'] is True; assert d['checks']['selected_topology_event_behavior_declared'] is True; print({'status': d['status'], 'checks_passed': all(d['checks'].values()), 'controls_declared': d['acceptance']['controls_declared']})"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_2_fixture_manifest_validation.json'; d=json.load(open(p)); required=['context_to_score_mapping_declared','candidate_source_sc1_reabsorption_digest_conditional','iteration_3_transition_criteria_declared','arbitration_window_artifact_mapping_declared','arbitration_timing_declared','native_dependency_chain_policy_declared']; assert d['status']=='passed'; assert all(d['checks'][k] is True for k in required); assert d['manifest']['candidate_source_evidence']['topology_state_reabsorption_digest_required_for_sc1'] is False; assert d['manifest']['candidate_source_evidence']['topology_state_reabsorption_digest_required_for_post_topology_candidates'] is True; print({'status': d['status'], 'review_hardening_checks': {k:d['checks'][k] for k in required}})"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- Iteration 2 is manifest-only:
  `route_choice_probe_run = false`.
- The fixture is `N06_S0_source_two_route_context_fork_v1`: source node `0`,
  branch node `1`, sinks `2` and `3`, context signal nodes `4` and `5`.
- Context A selects route A and context B selects route B by native
  `candidate_score_components` under the same serialized policy.
- The selected native policy is
  `score_ordered_topology_route_candidates`; the actual gate remains
  `native_lgrc_route_arbitration_policy != disabled`.
- `redirect` is retained only as a fixed-route/control or explicitly declared
  native redirect caveat; the positive templates use native `collapse` route
  intent with `lgrc9v3_causal_collapse`.
- Candidate source evidence fields are declared, but Iteration 2 uses symbolic
  manifest declarations only. Runtime committed surface/producers are deferred
  to the SC1+ lanes.
- `candidate_source_topology_state_reabsorption_digest` is conditional:
  it is not required for the first pre-topology SC1 candidate set and is
  required only for post-topology candidate sources.
- Post-Iteration-4 compatibility refresh: candidate lineage maps now map all
  transferred nodes to the selected sink lineage for each route. This matches
  LGRC9V3 collapse/reabsorption `selected_sink_clock_continuity` and does not
  promote any route-choice claim.
- Post-review hardening added `score_tolerance = 1e-9` to the serialized
  arbitration policy so selection replay no longer uses an implicit hardcoded
  score epsilon.
- Context-to-score derivation is declared from runtime-visible context/source
  artifacts; Iteration 3 must emit artifacts that make the derivation
  reconstructable.
- Arbitration window labels are mapped to concrete artifact kinds, and timing
  fields are declared for future rows.
- Candidate retirement fields are native candidate fields in this repo; they
  are treated as candidate predictions that must later agree with topology /
  reabsorption records if the route is selected and committed.
- All controls have distinct primary blockers.
- All claim flags remain false.

Acceptance statement:

```text
Iteration 2 passes if N06 fixtures, context surfaces, route candidates,
arbitration policies, budget surfaces, and controls are declared before route
choice probes, and invalid hidden context, hidden preference, preselected sink,
budget ambiguity, producer mutation, and claim-promotion attempts fail closed.
```

Acceptance result: Achieved.

Confirmation:

```json
{"checks_passed": true, "controls_declared": true, "route_choice_probe_run": false, "status": "passed"}
```

## Iteration 3. SC1 Alternatives Exposed

Status: Complete.

- [x] Run default-off lane and verify no candidate routes are emitted.
- [x] Run enabled SC1 lane.
- [x] Emit candidate route records from committed runtime-visible evidence.
- [x] Verify every emitted candidate has a non-null
  `candidate_source_surface_digest`.
- [x] Verify `candidate_source_surface_digest` resolves to a committed native
  causal pulse-substrate surface row or equivalent native source surface.
- [x] Verify `candidate_source_topology_state_reabsorption_digest` is null or
  absent for the first pre-topology SC1 candidate set.
- [x] Verify context-to-score derivation is reconstructable from
  runtime-visible source/context artifacts.
- [x] Verify candidate records carry `causal_epoch`, `checkpoint_index`,
  `event_time_key`, and `scheduler_event_index` ordering evidence where
  available.
- [x] Emit one candidate set record.
- [x] Verify candidate set includes all eligible candidates in the arbitration
  window.
- [x] Verify deterministic candidate ordering.
- [x] Verify candidate route digests are recorded.
- [x] Verify candidate budget predictions are present.
- [x] Verify candidate context/source evidence is committed.
- [x] Verify no route-arbitration record is emitted.
- [x] Verify no selected topology event is committed.
- [x] Verify no packet is scheduled by candidate emission alone.
- [x] Run hidden route, hidden context, missing budget prediction, malformed
  candidate, duplicate candidate, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n06_iteration_3_sc1_candidate_alternatives.json`
- [x] `reports/n06_iteration_3_sc1_candidate_alternatives.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_3_sc1_candidate_alternatives.py
```

Result:

```json
{"candidate_route_count": 2, "candidate_set_count": 1, "controls_passed": true, "default_off_passed": true, "route_selected": false, "status": "passed"}
```

Artifact digests:

```json
{
  "acceptance_digest": "797e171d001749ee33d81798796dca1507e178113342bb2423be7f8728e4eb98",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "0a282475cd1a0ecc5c7c2e90c0730db8ca43f51a14e0e5bfbac28d39468b6eca",
  "enabled_lane_digest": "c78e13ca3cfbfc3e3974aede500bad52632402bf4b8424a533c1c0a4e446b843"
}
```

Generated file SHA-256:

```text
7023df3276a6b393205baa0cdf9c2b63855a849d7fc7afa6e4dd000d62ee2f59  scripts/run_n06_iteration_3_sc1_candidate_alternatives.py
8d7d04722415265bdd80a59999216127183713b603c5c9a81527a913601977fc  outputs/n06_iteration_3_sc1_candidate_alternatives.json
b1bf9cdfa54294104aff3a7c19c724ce7cc6b1d4593d5ff952ae7dcdcf1f4e11  reports/n06_iteration_3_sc1_candidate_alternatives.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_3_sc1_candidate_alternatives.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['acceptance']['sc_level']=='SC1'; assert d['acceptance']['route_selected'] is False; assert d['lanes']['enabled_sc1']['candidate_route_count']==2; assert d['lanes']['enabled_sc1']['candidate_set_count']==1; assert d['lanes']['enabled_sc1']['candidate_only_artifact_validation']['unexpected_failure_reasons']==[]; assert all(control['passed'] for control in d['controls'].values()); assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_3_assertions_passed')"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json'; d=json.load(open(p)); c=d['lanes']['enabled_sc1']['checks']; assert c['source_producer_record_id_null_when_not_producer_backed'] is True; assert c['candidate_budget_predictions_match_manifest'] is True; assert c['candidate_set_idempotency_key_reconstructable'] is True; assert d['lanes']['enabled_sc1']['context_derivation']['comparison_tolerance']==1e-9; assert d['controls']['claim_promotion']['detail']['specific_claim_promotion_blocker_present'] is True; print('n06_iteration_3_review_hardening_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- The default-off lane returned
  `native_route_arbitration_policy_disabled` and emitted no candidate routes,
  candidate set, arbitration record, topology event, production result, or
  scheduled packet.
- The enabled SC1 lane emitted two native candidate route records and one
  candidate set from committed `route_local_pulse_contact` surface evidence.
- The first pre-topology SC1 candidate set intentionally has
  `candidate_source_topology_state_reabsorption_digest = null` on both
  candidates.
- The full native route-arbitration artifact validator is not expected to
  mark support true in SC1 because no arbitration record exists yet. Iteration
  3 records this as the explicit candidate-only replay scope:
  `expected_incomplete_reasons = ["no_native_route_arbitration_records"]`,
  with `unexpected_failure_reasons = []`.
- Hidden route, hidden context, missing budget prediction, malformed
  candidate, unknown source surface digest, duplicate candidate, and
  claim-promotion controls all passed with distinct blockers or duplicate
  suppression evidence.
- Post-review hardening added explicit checks that
  `candidate_source_producer_record_id` is null for this non-producer-backed
  SC1 lane, candidate budget prediction values match the manifest under the
  manifest `budget_tolerance = 1e-9`, and the candidate-set idempotency key is
  reconstructable from serialized candidate-set fields.
- The SC1 context derivation intentionally checks only `context_a`.
  `context_b` inversion is recorded as deferred to Iteration 5 / SC3.
- Malformed-candidate and unknown-source controls are treated as fail-closed
  rejection controls rather than depending on exact native exception wording.
- `candidate_selected_sink_id` remains candidate payload only. No route is
  selected until a native route-arbitration record is emitted in Iteration 4.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 3 passes if N06 emits complete candidate route sets from committed
runtime-visible evidence under a default-off policy, while selecting no route,
committing no topology event, scheduling no packet, and promoting no claims.
```

Acceptance result: Achieved.

Confirmation:

```json
{"candidate_route_count": 2, "candidate_set_count": 1, "candidate_set_contract_valid_pre_arbitration": true, "context_to_score_reconstructable": true, "route_selected": false, "semantic_choice_claim_allowed": false, "status": "passed"}
```

## Iteration 4. SC2 Native Arbitration Selection

Status: Complete.

- [x] Consume a committed candidate set.
- [x] Emit one native route-arbitration record.
- [x] Select exactly one candidate route digest.
- [x] Record rejected candidate route digests.
- [x] Record arbitration rule and reason code.
- [x] Verify selection is replayable from serialized candidate scores or
  compatibility gates.
- [x] Verify unresolved ties fail closed unless deterministic tie-breaker is
  serialized and runtime-visible.
- [x] Verify budget-invalid candidates cannot win.
- [x] Verify order-invalid candidates fail.
- [x] Verify hidden-input candidates fail.
- [x] Verify no selected topology event is committed in this iteration unless
  explicitly scoped.
- [x] Verify no semantic-choice claim is promoted yet without context-swap
  evidence.

Expected artifacts:

- [x] `outputs/n06_iteration_4_sc2_native_arbitration.json`
- [x] `reports/n06_iteration_4_sc2_native_arbitration.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_4_sc2_native_arbitration.py
```

Result:

```json
{"controls_passed": true, "route_arbitration_count": 1, "selected_route": "route_a", "semantic_choice_claim_allowed": false, "status": "passed", "topology_event_committed": false}
```

Artifact digests:

```json
{
  "acceptance_digest": "b1e6b8422201da05e71e339cca1b9464cf00a6314f1cbcca371e1b62f12269f5",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "60af0cf7bbd9194ba5175e49e69551caf5552674e4722b83317899b7b436407a",
  "enabled_lane_digest": "3a8c41e74ae9299d04013957c1bc15a3d420d361e6b33f17ae9c996ade1eb225"
}
```

Generated file SHA-256:

```text
eabfa264534d5840ff8e3debc8eb48b44071c48b26b93f941d956ae10241f707  scripts/run_n06_iteration_4_sc2_native_arbitration.py
495e26f942e530dd53a94b4d3924b206dedea9277844a330b6ff27632d174c6f  outputs/n06_iteration_4_sc2_native_arbitration.json
7da12572aba79d13141d1803d68281d86201e78b3d7f0338dcd5637db87862ba  reports/n06_iteration_4_sc2_native_arbitration.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_4_sc2_native_arbitration.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_4_sc2_native_arbitration.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_4_sc2_native_arbitration.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['acceptance']['sc_level']=='SC2'; assert d['acceptance']['selected_route']=='route_a'; assert d['acceptance']['topology_event_committed'] is False; assert d['acceptance']['semantic_choice_claim_allowed'] is False; assert d['lanes']['enabled_sc2']['route_arbitration_count']==1; assert d['lanes']['enabled_sc2']['selection_only_artifact_validation']['unexpected_failure_reasons']==[]; assert all(control['passed'] for control in d['controls'].values()); assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_4_assertions_passed')"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_4_sc2_native_arbitration.json'; d=json.load(open(p)); lane=d['lanes']['enabled_sc2']; assert lane['checks']['authorized_topology_event_matches_selected_candidate'] is True; assert lane['selection_replay']['checks']['arbitration_score_equals_selected_candidate_score'] is True; assert lane['selection_replay']['score_tolerance']==1e-9; assert d['controls']['budget_invalid']['detail']['budget_error_exceeds_manifest_tolerance'] is True; assert d['controls']['duplicate_arbitration']['detail']['same_route_arbitration_artifact'] is True; print('n06_iteration_4_review_hardening_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- Iteration 4 consumes the committed SC1 candidate set and emits one native
  route-arbitration record with reason
  `native_route_arbitration_selected_highest_score`.
- The selected candidate is `route_a`; the rejected candidate digest is
  recorded in the arbitration artifact.
- The route-arbitration record authorizes a selected topology event id/digest
  for replay, but this iteration does not commit that topology event.
- Post-review hardening verifies that the authorized topology event id/digest
  is derived from the selected candidate's topology-event kind, selected sink,
  and collapse lineage map. It also verifies
  `arbitration_score == selected_candidate_route_score` under the serialized
  `score_tolerance`.
- The artifact-only validator reconstructs the selected route and records the
  expected pre-commit limitation:
  `selected_topology_event_count_mismatch:*:0`. There are no unexpected replay
  failures.
- Disabled-policy, no-candidate, unresolved-tie, budget-invalid,
  order-invalid, hidden-input, duplicate-arbitration, and claim-promotion
  controls passed. Empty-candidate and order-invalid controls use
  experiment-injected candidate-set records to exercise native arbitrator
  fail-closed branches that native candidate emission normally prevents.
- Hidden-input controls now record both attempted forbidden inputs and the
  native rejection record's validation marker. Budget-invalid controls record
  that the mutated budget error exceeds the manifest tolerance. Duplicate
  arbitration controls verify idempotency key, arbitration digest, and complete
  returned artifact identity.
- Full native candidate records remain in the machine-readable JSON artifact
  as replay/provenance payloads; the report/checklist summarize the evidence
  by digests and selected/rejected route ids.
- No semantic-choice, agency, memory/trail, identity, movement, locomotion,
  biology, ACO, or unrestricted movement claim is promoted.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 4 passes if native route arbitration selects exactly one route from a
complete candidate set using serialized runtime-visible inputs, while disabled
policy, no-candidate, unresolved-tie, budget-invalid, order-invalid, and
hidden-input controls fail with distinct blockers.
```

Acceptance result: Achieved.

Confirmation:

```json
{"route_arbitration_count": 1, "selected_route": "route_a", "selection_replayable_from_serialized_scores": true, "semantic_choice_claim_allowed": false, "status": "passed", "topology_event_committed": false}
```

## Iteration 5. SC3 Context-Conditioned Route Selection

Status: Complete.

- [x] Run context A lane.
- [x] Run context B lane under the same serialized policy.
- [x] Verify context A selects route A.
- [x] Verify context B selects route B.
- [x] Verify both context states are serialized and runtime-visible.
- [x] Verify selected route follows the declared context relation.
- [x] Verify context relation is replayable from artifacts.
- [x] Verify no hidden fixture labels or report-side selection are used.
- [x] Verify budget remains exact.
- [x] Run hidden context, stale context, context/order inversion, budget
  mismatch, producer mutation, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n06_iteration_5_sc3_context_conditioned_selection.json`
- [x] `reports/n06_iteration_5_sc3_context_conditioned_selection.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_5_sc3_context_conditioned_selection.py
```

Result:

```json
{"context_a_selected": "route_a", "context_b_selected": "route_b", "controls_passed": true, "selection_changes_with_context": true, "semantic_choice_claim_allowed": false, "status": "passed"}
```

Artifact digests:

```json
{
  "acceptance_digest": "16c412651fd1666d86fd4caa4694c3f5b79d921d38bd50c1ce97974964954737",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "context_a_lane_digest": "c7367cbb552a5dee7ab2feee28bad9d33124dc0de805d6d2372f73fffdd728a1",
  "context_b_lane_digest": "4c2fcb77b3186423358641ccf9779e290f5efd2b71d34f7c5b3274ebf6d7544b",
  "controls_digest": "363bfc093449a8a5a7fb568e48499af33218401eac571860f503c8c5a01fb50a"
}
```

Generated file SHA-256:

```text
292a96f7874869282949bb3d18d7e7668f9efd105663aa091f7043aebb0f3e6c  scripts/run_n06_iteration_5_sc3_context_conditioned_selection.py
086c637b161e22e3a8c828591722033efcd49557e17ed5c02f32860aeb6e9b77  outputs/n06_iteration_5_sc3_context_conditioned_selection.json
4f2fd63e3a329c84d0a605be42b1b09e0738d51edd89b6a124192b50c6b1bfe9  reports/n06_iteration_5_sc3_context_conditioned_selection.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_5_sc3_context_conditioned_selection.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_5_sc3_context_conditioned_selection.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_5_sc3_context_conditioned_selection.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['acceptance']['sc_level']=='SC3'; assert d['acceptance']['context_a_selected_route']=='route_a'; assert d['acceptance']['context_b_selected_route']=='route_b'; assert d['acceptance']['selection_changes_with_context'] is True; assert d['acceptance']['context_relation_replayable'] is True; assert d['acceptance']['semantic_choice_claim_allowed'] is False; assert d['acceptance']['topology_event_committed'] is False; assert d['acceptance']['packet_scheduled_by_arbitration'] is False; assert d['checks']['same_serialized_policy'] is True; assert d['lanes']['context_a']['context_relation_replay']['checks']['selected_route_matches_serialized_context_relation'] is True; assert d['lanes']['context_b']['context_relation_replay']['checks']['selected_route_matches_serialized_context_relation'] is True; assert d['controls']['stale_context']['primary_blocker']=='n06_stale_context_surface_blocked'; assert d['controls']['stale_context']['passed'] is True; assert all(c['passed'] for c in d['controls'].values()); assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_5_assertions_passed')"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_5_sc3_context_conditioned_selection.json'; d=json.load(open(p)); assert d['checks']['same_policy_id_but_context_specific_arbitration_inputs'] is True; assert d['checks']['candidate_set_digest_distinguishes_context_lanes'] is True; assert d['artifact_payload_policy']['full_candidate_route_records_in_json'] is True; assert d['candidate_set_identity']['candidate_set_id_is_not_context_unique'] is True; assert d['candidate_set_identity']['context_unique_key']=='candidate_set_digest';\nfor lane_id in ('context_a','context_b'):\n    replay=d['lanes'][lane_id]['context_relation_replay']['checks'];\n    assert replay['arbitration_context_fields_serialized'] is True;\n    assert replay['candidate_arbitration_context_consistent'] is True;\n    assert replay['arbitration_score_equals_selected_candidate_score'] is True;\n    assert replay['candidate_route_scores_equal_component_sums'] is True;\n    assert replay['serialized_context_values_agree_across_candidates'] is True;\n    assert replay['selected_route_matches_serialized_context_relation'] is True;\nassert d['controls']['hidden_context']['detail']['artifact_replay_gate']['passed'] is True; assert d['controls']['stale_context']['detail']['failure_reasons'].count('n06_stale_context_surface_blocked')==1; assert d['controls']['claim_promotion']['passed'] is True; print('n06_iteration_5_review_hardening_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- Iteration 5 uses the same fixture source surface and the same serialized
  native route-arbitration policy for both context lanes.
- `context_a` serializes active context node `4`, compatible route `route_a`,
  and selects `route_a` with score `1.0` vs `0.4`.
- `context_b` serializes active context node `5`, compatible route `route_b`,
  and selects `route_b` with score `1.0` vs `0.4`.
- Artifact replay verifies the selected route matches both the manifest
  context relation and the serialized context relation in candidate runtime
  inputs.
- Post-review hardening also records context fields in
  `arbitration_runtime_visible_inputs`, verifies arbitration-visible context
  fields match candidate-visible context fields, verifies
  `arbitration_score == selected_candidate_route_score`, verifies
  `candidate_route_score == sum(candidate_score_components)`, and explicitly
  checks that serialized context values agree across all candidates in a lane.
- The selected topology event id/digest is authorized for each selected
  candidate, but no topology event is committed in this iteration.
- Hidden-context, stale-context, context-order-inversion, budget-mismatch,
  producer-mutation-boundary, and claim-promotion controls passed with
  distinct blockers:

```json
{
  "budget_mismatch": "native_route_arbitration_budget_invalid",
  "claim_promotion": "native_route_arbitration_claim_promotion_blocked",
  "context_order_inversion": "n06_context_order_inversion_blocked",
  "hidden_context": "native_route_arbitration_hidden_input_rejected",
  "producer_mutation": "n06_producer_mutation_boundary_violation",
  "stale_context": "n06_stale_context_surface_blocked"
}
```

- Hidden-context rejection is checked at both native candidate emission and
  artifact replay. Stale-context and context-order controls remain
  N06/artifact-level semantic replay controls because the current native route
  arbitration contract has no dedicated semantic-context validator.
- Full candidate route records remain in the JSON artifact intentionally as
  replay payloads. SC3 and SC6 replay require candidate runtime-visible
  context inputs, score components, budget predictions, and lineage maps. The
  report and checklist summarize by digests and selected/rejected route ids.
- Both context lanes currently share the same `candidate_set_id`, while their
  `candidate_set_digest` values differ:

```json
{
  "candidate_set_id_is_not_context_unique": true,
  "context_unique_key": "candidate_set_digest",
  "context_a_candidate_set_digest": "b2e4fc1d53538a2c75a0127e5876ddc5de2f8faba102759774d5a8ad855af081",
  "context_b_candidate_set_digest": "e721a542cde7652fd3ef6ef341a166575c96de5022bc34ba937923e1921ec218"
}
```

- SC3 is recorded as the evidence classification and
  `context_conditioned_route_selection_candidate` as the claim ceiling.
  `semantic_choice_claim_allowed` remains false until later artifact-only
  closeout.
- No memory/trail, agency, identity, movement, locomotion, biology, ACO, or
  unrestricted movement claim is promoted.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 5 passes if the same source and same serialized policy select
different routes under different runtime-visible context states, and artifact
replay reconstructs why each selected route matches the declared context
relation.
```

Acceptance result: Achieved.

Confirmation:

```json
{"context_a_selected_route": "route_a", "context_b_selected_route": "route_b", "context_relation_replayable": true, "sc_level": "SC3", "selection_changes_with_context": true, "semantic_choice_claim_allowed": false, "status": "passed"}
```

## Iteration 6. SC4 Polarity Or Context-Swap Controls

Status: Complete.

- [x] Run matched forward/reversed or polarity/context-swapped lanes.
- [x] Verify same fixture family, same policy, same thresholds, and same
  validator.
- [x] Verify swapped context reverses or swaps route selection as expected.
- [x] Verify selected and rejected candidate digests are recorded for both
  lanes.
- [x] Verify route choice is not caused by hidden direction labels.
- [x] Verify budget remains exact.
- [x] Run wrong-polarity, unswapped-context, hidden direction, budget mismatch,
  order inversion, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n06_iteration_6_sc4_context_swap_controls.json`
- [x] `reports/n06_iteration_6_sc4_context_swap_controls.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_6_sc4_context_swap_controls.py
```

Result:

```json
{"context_a_selected": "route_a", "context_b_selected": "route_b", "controls_passed": true, "semantic_choice_claim_allowed": false, "status": "passed", "swap_replayable": true}
```

Artifact digests:

```json
{
  "acceptance_digest": "2c2c1c138ad04de179b351caacd0c3638cac27f9ce3f286a3d25da68f9d0238f",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "context_a_lane_digest": "153d2255f0f31656ce56b1ae5a5f6ebc06000c8df69bd0c9b23288e703783d97",
  "context_b_lane_digest": "d1b96176bfc224b9eb29b79389b0140bf3fb2a3f933d7f2ff120e74185217c8b",
  "controls_digest": "53abaa7f7457b7aa511f7972acea95b6056644a01431fb521d79059c18e81bdd",
  "matched_settings_digest": "f9c67eb7959616231b20c9ed3cffd1a713cd7d9d0cc7b2fd48f61095cb7b5a2c",
  "swap_replay_digest": "b3bf8e48e429cff26e8fef4b7f8965e61461f6acb3fba5bba1bdfdbb9f26de43"
}
```

Generated file SHA-256:

```text
46a32b9822e322e10978214ccf6a3f69f2947efae3e2caeae4af2de01ee803d6  scripts/run_n06_iteration_6_sc4_context_swap_controls.py
63ce78f277f60ea4dd32716af208682eba40807a02f973675a77d45496ceea0f  outputs/n06_iteration_6_sc4_context_swap_controls.json
a40c0fa3f592a1380e3b36854e48155306770c968c2441ef9c78c94c3cd7546c  reports/n06_iteration_6_sc4_context_swap_controls.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_6_sc4_context_swap_controls.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_6_sc4_context_swap_controls.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_6_sc4_context_swap_controls.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['acceptance']['sc_level']=='SC4'; assert d['acceptance']['claim_ceiling']=='context_swap_route_selection_candidate'; assert d['acceptance']['context_a_selected_route']=='route_a'; assert d['acceptance']['context_b_selected_route']=='route_b'; assert d['acceptance']['selection_swapped_by_serialized_context'] is True; assert d['acceptance']['same_policy_thresholds_and_validator'] is True; assert d['acceptance']['hidden_direction_labels_absent'] is True; assert d['acceptance']['semantic_choice_claim_allowed'] is False; assert d['acceptance']['topology_event_committed'] is False; assert d['acceptance']['packet_scheduled_by_arbitration'] is False; assert d['scope_notes']['independent_polarity_surface_tested'] is False; assert d['matched_settings']['matched'] is True; assert d['swap_replay']['swap_replayable'] is True; assert d['swap_replay']['context_a_rejected_routes']==['route_b']; assert d['swap_replay']['context_b_rejected_routes']==['route_a']; assert d['controls']['wrong_polarity']['primary_blocker']=='n06_wrong_context_or_polarity_blocked'; assert d['controls']['unswapped_context']['primary_blocker']=='n06_unswapped_context_blocked'; assert d['controls']['hidden_direction']['primary_blocker']=='n06_hidden_direction_label_rejected'; assert all(c['passed'] for c in d['controls'].values()); assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_6_assertions_passed')"
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_6_sc4_context_swap_controls.json'; d=json.load(open(p)); assert d['lanes']['context_a']['lane_id']=='sc4_context_a_native_arbitration'; assert d['lanes']['context_b']['lane_id']=='sc4_context_b_native_arbitration'; assert d['lanes']['context_a']['selection_only_artifact_validation']['validator_scope']=='sc4_context_swap_pre_topology_commit'; assert d['lanes']['context_b']['selection_only_artifact_validation']['validator_scope']=='sc4_context_swap_pre_topology_commit'; assert d['acceptance']['forbidden_runtime_inputs_absent'] is True; assert d['checks']['no_forbidden_runtime_inputs'] is True; assert d['matched_settings']['context_a_budget_errors']==[0.0,0.0]; assert d['matched_settings']['context_b_budget_errors']==[0.0,0.0]; assert d['swap_replay']['context_a_forbidden_runtime_inputs']==[]; assert d['swap_replay']['context_b_forbidden_runtime_inputs']==[]; assert d['controls']['hidden_direction']['detail']['artifact_semantic_validator']['valid'] is False; assert d['controls']['hidden_direction']['detail']['artifact_semantic_validator']['failure_reasons']==['n06_hidden_direction_label_rejected']; assert sorted(d['controls']['wrong_polarity']['detail']['expected_underlying_reasons_present'])==sorted(d['controls']['wrong_polarity']['detail']['expected_underlying_reasons']); assert d['controls']['unswapped_context']['detail']['checks']['paired_context_b_changes_selection'] is True; print('n06_iteration_6_review_hardening_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- Iteration 6 is scoped to context-swap evidence. The current fixture
  serializes context A/B affordance; it does not expose an independent polarity
  surface.
- Matched settings were identical across lanes: same fixture family, policy
  id, arbitration rule, candidate-set order key, unresolved-tie policy, budget
  tolerance, score tolerance, validator scope, and source surface digest.
- Post-review hardening labels the reused context lanes as
  `sc4_context_a_native_arbitration` and `sc4_context_b_native_arbitration`,
  records validator scope as `sc4_context_swap_pre_topology_commit`, and checks
  score/budget tolerances from lane artifacts rather than with tautological
  manifest self-comparisons.
- Context A selects `route_a` and rejects `route_b`; context B selects
  `route_b` and rejects `route_a`.
- Selected and rejected candidate digests are recorded for both lanes.
- Positive lanes contain no direction, polarity, or broader hidden runtime
  input fields. Hidden-direction artifact corruption injects into all candidate
  route records and fails semantic artifact replay with
  `n06_hidden_direction_label_rejected`.
- The wrong-context/polarity control records the underlying semantic replay
  reasons it expects:

```json
[
  "n06_stale_context_surface_blocked",
  "n06_context_relation_mismatch",
  "n06_context_evidence_not_replayable"
]
```

- The unswapped-context control now checks both same-context determinism and
  the paired `context_b` route change, so it is not only a repeated `context_a`
  consistency check.
- Wrong-context/polarity, unswapped-context, hidden-direction,
  budget-mismatch, order-inversion, and claim-promotion controls passed with
  distinct blockers:

```json
{
  "budget_mismatch": "native_route_arbitration_budget_invalid",
  "claim_promotion": "native_route_arbitration_claim_promotion_blocked",
  "hidden_direction": "n06_hidden_direction_label_rejected",
  "order_inversion": "n06_context_order_inversion_blocked",
  "unswapped_context": "n06_unswapped_context_blocked",
  "wrong_polarity": "n06_wrong_context_or_polarity_blocked"
}
```

- Stale-context/order-style controls remain N06 artifact-level semantic replay
  controls until a future Phase 8 native semantic-context validator exists.
- SC4 is recorded as the evidence classification and
  `context_swap_route_selection_candidate` as the claim ceiling.
  `semantic_choice_claim_allowed` remains false until artifact-only closeout.
- No memory/trail, agency, identity, movement, locomotion, biology, ACO, or
  unrestricted movement claim is promoted.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 6 passes if matched context/polarity swaps change route selection
only through serialized runtime-visible context evidence, with identical policy
and validator settings and no hidden direction labels.
```

Acceptance result: Achieved.

Confirmation:

```json
{"claim_ceiling": "context_swap_route_selection_candidate", "context_a_selected_route": "route_a", "context_b_selected_route": "route_b", "sc_level": "SC4", "selection_swapped_by_serialized_context": true, "semantic_choice_claim_allowed": false, "status": "passed"}
```

## Iteration 7. SC5 Repeated Context-Conditioned Selection

Status: Complete.

- [x] Run repeated context-conditioned selection across multiple cycles or
  arbitration windows.
- [x] Assign distinct window or cycle ids.
- [x] Verify each selection uses committed current context evidence.
- [x] Verify no hidden schedule or preauthored selection list is used.
- [x] Verify duplicate arbitration suppression.
- [x] Verify stale context reads fail closed.
- [x] Verify node-plus-packet budget remains exact.
- [x] Verify artifact-only replay reconstructs every selection.
- [x] Run hidden schedule, stale context, duplicate arbitration, budget drift,
  producer mutation, and claim-promotion controls.

Expected artifacts:

- [x] `outputs/n06_iteration_7_sc5_repeated_context_selection.json`
- [x] `reports/n06_iteration_7_sc5_repeated_context_selection.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_7_sc5_repeated_context_selection.py
```

Result:

```json
{"controls_passed": true, "cycle_count": 4, "selected_route_sequence": ["route_a", "route_b", "route_a", "route_b"], "semantic_choice_claim_allowed": false, "status": "passed"}
```

Artifact digests:

```json
{
  "acceptance_digest": "93ad1330a3fae8dc7e9ea2583a9741aba2e4f798929ab71982570a4cdc5120d7",
  "artifact_only_replay_digest": "5043144f64df88a8a53f4d39e8ea395974c2b247918efc86e3d9d4d9a714b217",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "be586f452e4695090040a88b1ca44095160d1de3e31ec5698372d0b5c9337c91",
  "cycle_replay_digest": "bd29bcf83ed78806ab6175235def176b7ee6df7cec078eeeee18a0078dcbb884",
  "lanes_digest": "09566526c057b358c163ccf01a6b2b492624da53b1bdd93489f1eccf1a3f012e"
}
```

Generated file SHA-256:

```text
0a273dc9e2523f5897ac0331f213e179ab318a62d479537d6957e7c418f6c570  scripts/run_n06_iteration_7_sc5_repeated_context_selection.py
2f1ac9446f9095ee3b1d3a0b173a1336801846646c4a3ba4cc7b2a9db8bcfc24  outputs/n06_iteration_7_sc5_repeated_context_selection.json
8a6510a310bd1caef14bdc4bc17b60ab0334b127f6823c229e23e89d38d9e255  reports/n06_iteration_7_sc5_repeated_context_selection.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_7_sc5_repeated_context_selection.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_7_sc5_repeated_context_selection.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_7_sc5_repeated_context_selection.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['acceptance']['sc_level']=='SC5'; assert d['acceptance']['claim_ceiling']=='repeated_context_conditioned_route_selection_candidate'; assert d['acceptance']['cycle_count']==4; assert d['acceptance']['context_sequence']==['context_a','context_b','context_a','context_b']; assert d['acceptance']['selected_route_sequence']==['route_a','route_b','route_a','route_b']; assert d['acceptance']['selected_route_sequence_matches_context_sequence'] is True; assert d['acceptance']['artifact_only_replay_reconstructs_every_selection'] is True; assert d['acceptance']['hidden_schedule_or_preauthored_selection_used'] is False; assert d['acceptance']['semantic_choice_claim_allowed'] is False; assert d['acceptance']['topology_event_committed'] is False; assert d['acceptance']['packet_scheduled_by_arbitration'] is False; assert d['cycle_replay']['checks']['arbitration_window_ids_distinct'] is True; assert d['cycle_replay']['checks']['candidate_set_digests_distinct'] is True; assert d['cycle_replay']['checks']['no_forbidden_runtime_inputs'] is True; assert d['artifact_only_replay']['artifact_only'] is True; assert d['artifact_only_replay']['runtime_state_used'] is False; assert d['artifact_only_replay']['all_cycles_reconstructed'] is True; assert d['controls']['hidden_schedule']['primary_blocker']=='n06_hidden_schedule_rejected'; assert d['controls']['duplicate_arbitration']['primary_blocker']=='duplicate_native_route_arbitration_suppressed'; assert d['controls']['stale_context']['primary_blocker']=='n06_stale_context_surface_blocked'; assert d['controls']['budget_drift']['primary_blocker']=='native_route_arbitration_budget_invalid'; assert d['controls']['producer_mutation']['primary_blocker']=='n06_producer_mutation_boundary_violation'; assert d['controls']['claim_promotion']['primary_blocker']=='native_route_arbitration_claim_promotion_blocked'; assert all(c['passed'] for c in d['controls'].values()); assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_7_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Review-hardening validation:

```bash
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_7_sc5_repeated_context_selection.json'; d=json.load(open(p)); assert d['acceptance']['selection_causality_basis']=='serialized_context_relation_replay_and_native_selection_replay'; assert d['acceptance']['independent_runtime_instances_per_cycle'] is True; assert d['acceptance']['single_runtime_multi_window_persistence_tested'] is False; assert d['acceptance']['cross_window_budget_accumulation_tested'] is False; assert d['acceptance']['trail_like_state_created'] is False; assert d['cycle_replay']['checks']['serialized_context_causality_replayable_all_cycles'] is True; assert d['cycle_replay']['checks']['distinct_context_input_signatures'] is True; assert d['cycle_replay']['checks']['repeated_context_input_signatures_stable'] is True; assert d['cycle_replay']['checks']['no_trail_like_runtime_inputs'] is True; assert d['artifact_only_replay']['independent_native_validator_invoked_per_cycle'] is True; assert all(c['selection_contract_valid_under_pre_topology_scope'] is True for c in d['artifact_only_replay']['per_cycle']); assert all(c['native_validator_valid'] is False for c in d['artifact_only_replay']['per_cycle']); assert d['controls']['duplicate_arbitration']['detail']['idempotency_key_reconstructable'] is True; assert d['controls']['budget_drift']['detail']['cross_cycle_budget_accumulation_tested'] is False; assert all(c['passed'] for c in d['controls']['hidden_schedule']['detail']['per_cycle']); assert all(c['passed'] for c in d['controls']['producer_mutation']['detail']['per_cycle']); assert all(c['passed'] for c in d['controls']['claim_promotion']['detail']['per_cycle']); print('n06_iteration_7_review_hardening_assertions_passed')"
```

Notes:

- Iteration 7 runs four repeated native route-arbitration windows with context
  sequence `context_a`, `context_b`, `context_a`, `context_b`.
- Review hardening records that these are distinct independent runtime windows,
  not a single-runtime persistence lane. Cross-window state persistence and
  accumulated budget drift are not tested by Iteration 7.
- The selected route sequence is `route_a`, `route_b`, `route_a`, `route_b`,
  derived from serialized context evidence in each window rather than a
  preauthored route list.
- Selection causality is based on serialized context relation replay plus
  native selection replay, not on sequence matching alone.
- Context input signatures are stable for repeated same-context windows and
  distinct between `context_a` and `context_b`.
- Each cycle has a distinct `cycle_id`, arbitration window id, candidate-set
  digest, selected candidate digest, and rejected candidate digest.
- Artifact-only replay reconstructs every selection with
  `runtime_state_used = false`. The aggregate replay now independently invokes
  the native selection-only artifact validator for every cycle.
- The native validator's raw `valid = false` result is expected in this
  pre-topology scope because selected topology events are intentionally not
  committed. The relevant SC5 check is
  `selection_contract_valid_under_pre_topology_scope = true`.
- Hidden-schedule, stale-context, duplicate-arbitration, budget-drift,
  producer-mutation, and claim-promotion controls passed with distinct
  blockers:

```json
{
  "budget_drift": "native_route_arbitration_budget_invalid",
  "claim_promotion": "native_route_arbitration_claim_promotion_blocked",
  "duplicate_arbitration": "duplicate_native_route_arbitration_suppressed",
  "hidden_schedule": "n06_hidden_schedule_rejected",
  "producer_mutation": "n06_producer_mutation_boundary_violation",
  "stale_context": "n06_stale_context_surface_blocked"
}
```

- Duplicate arbitration suppression is checked in native runtime by repeating
  arbitration on the same candidate set and confirming the same artifact is
  returned without increasing the arbitration-record count. The recorded
  arbitration idempotency key is independently reconstructed.
- Hidden-schedule control remains an N06 experiment-level semantic artifact
  replay control. Native LGRC route arbitration does not yet have a dedicated
  semantic-context or hidden-schedule validator beyond its current hidden-input
  contract.
- Producer-mutation and claim-promotion controls now run against all four
  cycles, not only `cycle_0`.
- `budget_drift` is a single-candidate budget-mismatch guard reused for SC5;
  true cross-cycle accumulated budget drift is explicitly untested here because
  SC5 uses independent runtime windows.
- SC5 is repeated-window route-selection evidence, not memory/trail evidence.
  Memory/trail formation remains deferred to N08, and no trail-like runtime
  inputs are present.
- SC5 is recorded as the evidence classification and
  `repeated_context_conditioned_route_selection_candidate` as the claim
  ceiling. `semantic_choice_claim_allowed` remains false until artifact-only
  closeout.
- No memory/trail, agency, identity, movement, locomotion, biology, ACO, or
  unrestricted movement claim is promoted.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 7 passes if repeated route selections are authorized by committed
runtime-visible context in each window, not by hidden schedules or preauthored
selection lists, with exact budget, duplicate suppression, and artifact replay.
```

Acceptance result: Achieved.

Confirmation:

```json
{"claim_ceiling": "repeated_context_conditioned_route_selection_candidate", "cycle_count": 4, "sc_level": "SC5", "selected_route_sequence": ["route_a", "route_b", "route_a", "route_b"], "semantic_choice_claim_allowed": false, "status": "passed"}
```

## Iteration 8. SC6 Artifact-Only Replay And Closeout

Status: Complete.

- [x] Run artifact-only replay over candidate route records.
- [x] Replay candidate set record.
- [x] Replay context surface and context relation.
- [x] Replay native route-arbitration record.
- [x] Replay selected and rejected candidate digests.
- [x] Replay scheduled/processed packet evidence where applicable.
- [x] Verify replay uses no private runtime state.
- [x] Verify disabled policy, no candidates, unresolved tie, hidden context,
  hidden preference, preselected sink, budget mismatch, order inversion, stale
  candidate, stale context, duplicate arbitration, producer mutation, and
  claim-promotion controls fail with distinct blockers.
- [x] Freeze strongest supported SC level.
- [x] Record strongest claim ceiling.
- [x] Record positive artifact SHA-256 digests.
- [x] Record negative controls and primary blockers.
- [x] Record native-policy blockers, if any.
- [x] Record that SC5 repeated selections used independent runtime windows,
  not a single-runtime persistence or accumulated budget-drift lane.
- [x] Record that route-sequence agreement is not itself causality evidence;
  SC6 must cite serialized context relation replay and native selection replay
  as the causality basis.
- [x] Carry forward that stale-context, hidden-schedule, and context-order
  controls are N06 artifact-level semantic replay checks pending a future
  native semantic-context validator.
- [x] Define N07 handoff criteria:
  minimum SC level, required controls, budget conservation, artifact replay,
  and claim-boundary cleanliness.
- [x] Record N07 handoff recommendation.

Expected artifacts:

- [x] `outputs/n06_iteration_8_sc6_closeout.json`
- [x] `reports/n06_iteration_8_sc6_closeout.md`

Run record:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_8_sc6_closeout.py
```

Result:

```json
{"artifact_only_replay_passed": true, "controls_passed": true, "n07_handoff_ready": true, "semantic_choice_claim_allowed": false, "status": "passed", "strongest_claim_ceiling": "artifact_only_semantic_route_choice_candidate", "strongest_supported_sc_level": "SC6"}
```

Artifact digests:

```json
{
  "acceptance_digest": "e3207fdfea331cb8f6247969cc862832e4d0d5e189b4606d732efd4f621c18a8",
  "artifact_only_closeout_digest": "2ddaa59790379e61a6ad4e8c1b9dfa8f6ec1497e99d579cfcafb5b0ea6ff1e49",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "closeout_digest": "4c1be1ca6e0f2789ca0ed31d1b612b502e41b1585faca7f941d58eda39f3f456",
  "control_matrix_digest": "6be8ce15fe33797dbd739ab1194e2daf7a95ec095c5a09789365a7311778fe60",
  "control_summary_digest": "7df542decb40be021f340a0cbbd57039d1fdb4e56e0314c4803e90d5334f2609",
  "n07_handoff_digest": "379622e310655b53f2211437a145114a035a1963e41f7ee51d150405d1fe3514",
  "positive_artifacts_digest": "bd5a9bfa5c34aa915d67404afc9848fa8dabc1871ec08cdff7b56231ec681f64",
  "source_artifacts_digest": "af85abce7cc36b2a967f8f2beb75cac955edb6b69f41705a39e94959539889d0"
}
```

Generated file SHA-256:

```text
73281ccf6c7c4fa41611b1bb860ae18597665f8cc070a66b7b7c904415b7eb82  scripts/run_n06_iteration_8_sc6_closeout.py
c020d954bdf5bfc53da9d550cd313f660af07f4b47e70b4c5102637500cc30bf  outputs/n06_iteration_8_sc6_closeout.json
994a49ee0727a10b28f974bb08dbf6573ee0e3e104c861238b1c5f0594aece1f  reports/n06_iteration_8_sc6_closeout.md
```

Additional validation:

```bash
.venv/bin/python -m py_compile experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_8_sc6_closeout.py
.venv/bin/python -m json.tool experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_8_sc6_closeout.json
.venv/bin/python -c "import json; p='experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_8_sc6_closeout.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['closeout']['strongest_supported_sc_level']=='SC6'; assert d['closeout']['strongest_claim_ceiling']=='artifact_only_semantic_route_choice_candidate'; assert d['closeout']['semantic_choice_claim_allowed'] is False; assert d['acceptance']['artifact_only_replay_passed'] is True; assert d['acceptance']['controls_passed'] is True; assert d['acceptance']['budget_conservation_passed'] is True; assert d['acceptance']['producer_boundary_passed'] is True; assert d['acceptance']['n07_handoff_ready'] is True; assert d['artifact_only_closeout']['artifact_only'] is True; assert d['artifact_only_closeout']['runtime_state_used'] is False; assert d['artifact_only_closeout']['valid_under_selection_only_scope'] is True; assert d['artifact_only_closeout']['checks']['runtime_state_not_used'] is True; assert d['artifact_only_closeout']['checks']['scheduled_processed_packet_evidence_scoped'] is True; assert all(c['replay_ok'] for c in d['artifact_only_closeout']['per_cycle']); assert all(c['native_validator_valid'] is False for c in d['artifact_only_closeout']['per_cycle']); assert all(c['selection_contract_valid_under_pre_topology_scope'] is True for c in d['artifact_only_closeout']['per_cycle']); required={'policy_disabled','no_candidates','unresolved_tie','hidden_context','hidden_preference','preselected_sink','experiment_side_if_else','report_side_selection','posthoc_threshold_change','budget_mismatch','order_inversion','stale_candidate','stale_context','duplicate_arbitration','producer_mutation','claim_promotion'}; assert required == set(d['control_summary']); assert all(c['passed'] for c in d['control_summary'].values()); assert d['n07_handoff']['recommendation']=='proceed_to_N07_rc_identity_attractor_invariance'; assert d['n07_handoff']['claim_boundary_clean'] is True; assert all(v is False for v in d['claim_flags'].values()); print('n06_iteration_8_assertions_passed')"
git status --short src
git diff --check -- experiments/2026-05-N06-lgrc-semantic-route-choice
```

Notes:

- N06 closes at `strongest_supported_sc_level = SC6`.
- The strongest claim ceiling is
  `artifact_only_semantic_route_choice_candidate`.
- SC6 is an evidence classification, not broad claim permission.
  `semantic_choice_claim_allowed` remains false.
- Artifact-only replay reconstructs candidate routes, candidate sets, context
  relation, native route-arbitration records, selected route digests, and
  rejected route digests without private runtime state.
- Final review hardening is included: SC6 replay now rechecks source-surface
  digest provenance through Iteration 3, score-component sums, arbitration
  score vs. selected-candidate score, context-field consistency, distinct
  candidate-set digests across cycles, and false claim flags in candidate,
  candidate-set, and arbitration records.
- The expected `native_validator_valid = false` / `replay_ok = true` split is
  explicit in the report: N06 SC6 is pre-topology and selection-only, so the
  native validator is expected to be incomplete only because selected topology
  event evidence is absent.
- The stale-candidate control now also records native artifact-validator
  rejection of the corrupted stale selection record.
- Scheduled/processed packet evidence is explicitly not applicable for this
  pre-topology selection-only N06 closeout.
- All required controls pass with distinct primary blockers:

```json
{
  "budget_mismatch": "native_route_arbitration_budget_invalid",
  "claim_promotion": "native_route_arbitration_claim_promotion_blocked",
  "duplicate_arbitration": "duplicate_native_route_arbitration_suppressed",
  "experiment_side_if_else": "n06_experiment_side_selection_rejected",
  "hidden_context": "native_route_arbitration_hidden_input_rejected",
  "hidden_preference": "native_route_arbitration_hidden_input_rejected:hidden_route_preference",
  "no_candidates": "native_route_arbitration_no_candidates",
  "order_inversion": "native_route_arbitration_order_invalid",
  "policy_disabled": "native_route_arbitration_policy_disabled",
  "posthoc_threshold_change": "n06_posthoc_threshold_change_rejected",
  "preselected_sink": "native_route_arbitration_hidden_input_rejected:preselected_sink",
  "producer_mutation": "n06_producer_mutation_boundary_violation",
  "report_side_selection": "n06_report_side_selection_rejected",
  "stale_candidate": "n06_stale_candidate_route_blocked",
  "stale_context": "n06_stale_context_surface_blocked",
  "unresolved_tie": "native_route_arbitration_unresolved_tie"
}
```

- Native policy blockers: none for the SC6 selection-only closeout.
- Native policy limitations carried forward:
  no dedicated native semantic-context validator yet; selected topology events
  and post-selection packet scheduling are outside N06 scope; SC5 repeated
  windows are independent runtime windows and do not test single-runtime
  persistence or accumulated budget drift.
- N07 handoff recommendation:
  `proceed_to_N07_rc_identity_attractor_invariance`.
- N07 may use N06's artifact-only route-choice candidate as route-selection
  background, but must independently validate RC identity and attractor
  invariance.
- No memory/trail, agency, agentic-like, RC identity collapse, identity
  acceptance, goal-proxy regulation, locomotion-like, biological, ACO, or
  unrestricted movement claim is promoted.
- `git status --short src` returned no `src/*` status entries.

Acceptance statement:

```text
Iteration 8 passes if N06 freezes its strongest supported SC level with
source-backed artifacts, exact budget accounting, artifact-only replay,
claim-boundary evidence, and a clear N07 handoff. Semantic route-choice
evidence must not promote memory, trail, ACO, agency, identity acceptance,
locomotion, biology, or unrestricted movement claims.
```

Acceptance result: Achieved.

Confirmation:

```json
{"artifact_only_replay_passed": true, "claim_ceiling": "artifact_only_semantic_route_choice_candidate", "controls_passed": true, "n07_handoff_ready": true, "sc_level": "SC6", "semantic_choice_claim_allowed": false, "status": "passed"}
```
