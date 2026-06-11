# N07 RC Identity Attractor Invariance Implementation Checklist

This checklist tracks implementation of
`2026-05-N07-rc-identity-attractor-invariance`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N07 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] Treat N06 as route-choice background only, not identity evidence.
- [ ] Treat N04 topology-mutating movement as movement baseline only, not
      identity acceptance.
- [ ] Treat topology design as a first-class N07 evidence object, not as a
      neutral fixture container.
- [ ] Keep N07 topology families gate-isolating: each topology should test one
      identity gate and each negative topology should break one declared
      property.
- [ ] Treat primitive topology families as identity-taxonomy unit tests.
- [ ] Treat composite topology families as taxonomy-classification probes, not
      automatic identity promotions.
- [ ] Use theory gates from the full RC/GRC/LGRC identity stack:
  - [ ] `papers/2025-11-RC-IdentityChoiceAbundance.md`
  - [ ] `papers/2025-12-GRC-V2.md`
  - [ ] `papers/2026-02-GRC-V3.md`
  - [ ] `papers/2026-04-GRC-9.md`
  - [ ] `papers/2026-05-LGRC-9.md`
  - [ ] `papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md`
- [ ] Use Arc of Becoming methodological sources by title only:
  - [ ] `Classification of Becoming`
  - [ ] `Interrogation of Becoming`
  - [ ] `Naturalization of Becoming`
  - [ ] `Cultivation of Becoming`
- [ ] Keep ID levels as evidence classifications, not claim flags.
- [ ] Keep `step()` and committed topology machinery as mutation boundaries.
- [ ] Do not mutate node coherence, edge state, packet ledgers, or topology
      from experiment-local code outside `step()` or committed topology
      machinery.
- [ ] Preserve node-plus-packet budget accounting for every run.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Record SHA-256 digests for positive fixture artifacts.
- [ ] Keep all agency, biology, personhood, and unrestricted identity claims
      false unless a later experiment separately validates them.

## Iteration 0. Planning And Handoff

Status: Complete.

- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Record N06 inherited ceiling:
  `artifact_only_semantic_route_choice_candidate`.
- [x] Record that N07 does not prove agency, memory, trail, goal regulation,
  ACO, biology, personhood, or unrestricted identity.
- [x] Define ID0-ID6 identity ladder.
- [x] Link plan/checklist from implementation README.

Acceptance statement:

```text
N07 starts from a clean claim boundary: N06 supplies route-choice context only,
while N07 opens RC identity attractor invariance. The experiment must validate
support, stability, attractivity, invariance, reflexive closure, and coherence
compatibility before any identity-acceptance candidate can be considered.
```

## Iteration 1. Baseline And Theory/Schema Inventory

Status: Complete.

Run record:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/build_n07_iteration_1_baseline_theory_schema_inventory.py
```

- [x] Inventory theory gates:
  - [x] GRC-V2 directed-flux identity basin / sink attraction domain
  - [x] GRC-V3 basin-attribute bundle
  - [x] GRC-9/GRC9V3 nine-port basin chart and spark/refinement boundary
  - [x] LGRC proper-time identity windows
  - [x] LGRC lineage-current identity evidence
  - [x] pulse-substrate identity-carrier taxonomy
  - [x] coherence state `(C, J_C)`
  - [x] continuity equation
  - [x] coherence functional `P[C]`
  - [x] global coherence invariance
  - [x] identity basin stability
  - [x] attractivity
  - [x] invariance
  - [x] reflexive closure
  - [x] coherence compatibility
  - [x] local irreducibility / agency boundary
- [x] Inventory source artifacts:
  - [x] N04 topology-mutating movement candidate artifacts
  - [x] N04 Iteration 22/22-B identity-through-topology boundary artifacts
  - [x] Record N04 Iteration 22/22-B artifacts as boundary/negative evidence
        for identity-through-topology, not as N07 identity support.
  - [x] N05 oscillator closeout artifacts
  - [x] N06 semantic route-choice closeout artifacts
  - [x] existing motion identity diagnostics
  - [x] existing LGRC proper-time identity evaluator support
- [x] Inventory available native LGRC surfaces:
  - [x] native causal pulse-substrate surface
  - [x] surface lineage transport
  - [x] topology-state reabsorption
  - [x] native route arbitration
  - [x] packet ledger and budget accounting
  - [x] proper-time identity evaluation
  - [x] identity-acceptance event contract, if used
  - [x] telemetry export surfaces
- [x] Freeze ID-ladder row schema.
- [x] Include minimum ID-ladder row fields:
  - [x] `row_id`
  - [x] `id_level`
  - [x] `topology_family_id`
  - [x] `composite_topology_id`
  - [x] `candidate_identity_carrier_type`
  - [x] `identity_carrier_surface`
  - [x] `support_area_id`
  - [x] `support_area_digest`
  - [x] `source_artifacts`
  - [x] `source_artifact_sha256`
  - [x] `source_reports`
  - [x] `runtime_family`
  - [x] `implementation_surface`
  - [x] `gate_vector`
  - [x] `derived_id_ceiling`
  - [x] `primary_blocker`
  - [x] `native_support_status`
  - [x] `native_observables_used`
  - [x] `experiment_local_observables_used`
  - [x] `native_policy_blockers`
  - [x] `becoming_class_status`
  - [x] `probe_role`
  - [x] `boundary_rung`
  - [x] `support_dependency_status`
  - [x] `withdrawal_test_status`
  - [x] `naturalization_rung`
  - [x] `activity_history_digest`
  - [x] `claim_flags`
  - [x] `visual_reference`
  - [x] `visual_is_evidence_source`
- [x] Freeze becoming-method field enums:
  - [x] `becoming_class_status`
  - [x] `probe_role`
  - [x] `boundary_rung`
  - [x] `support_dependency_status`
  - [x] `withdrawal_test_status`
  - [x] `naturalization_rung = Nat0..Nat6 | not_applicable`
- [x] Freeze topology ladder schema:
  - [x] `T0` label-only null topology
  - [x] `T1` support-area fixture topology
  - [x] `T2` stable local well topology
  - [x] `T3` attractor-neighborhood topology
  - [x] `T4` no-mutation invariance topology
  - [x] `T5` lineage-current invariance topology
  - [x] `T6` reflexive-closure topology
  - [x] `T7` compatibility topology
- [x] Freeze nine-port basin-chart mapping fields when used:
  - [x] support ports
  - [x] basin chart id
  - [x] sink relation
  - [x] gradient summary
  - [x] Hessian/well proxy
  - [x] net flux summary
  - [x] basin mass
  - [x] parent id and depth
- [x] Freeze identity-carrier taxonomy:
  - [x] `coherence_basin` is identity-carrier eligible
  - [x] `surface_row` is evidence only
  - [x] `deformation_token` is evidence only
  - [x] `boundary_signal` is evidence only
- [x] Freeze canonical control taxonomy from the implementation plan.
- [x] Verify `identity_threshold_missing` is included as the threshold-control
      blocker.
- [x] Freeze blocked claim flags:
  - [x] `semantic_choice_claim_allowed = false`
  - [x] `agency_claim_allowed = false`
  - [x] `agentic_like_claim_allowed = false`
  - [x] `intention_claim_allowed = false`
  - [x] `memory_or_trail_claim_allowed = false`
  - [x] `goal_proxy_regulation_claim_allowed = false`
  - [x] `movement_claim_allowed = false`
  - [x] `locomotion_like_claim_allowed = false`
  - [x] `biological_claim_allowed = false`
  - [x] `ant_colony_claim_allowed = false`
  - [x] `identity_acceptance_claim_allowed = false`
  - [x] `rc_identity_collapse_claim_allowed = false`
  - [x] `personhood_claim_allowed = false`
  - [x] `unrestricted_identity_claim_allowed = false`
  - [x] `unrestricted_movement_claim_allowed = false`
- [x] Verify no identity probes are run in this iteration.
- [x] Verify no `src/*` changes are needed.

Expected artifacts:

- [x] `outputs/n07_iteration_1_baseline_theory_schema_inventory.json`
- [x] `reports/n07_iteration_1_baseline_theory_schema_inventory.md`

Result:

```text
status = passed
identity_probe_run = false
new_support_rows_emitted = false
src_changes_required = false
next_iteration = 2_fixture_manifest_and_discrete_rc_observable_mapping
```

Acceptance statement:

```text
Iteration 1 passes if N07 has a source-backed theory/schema inventory, a frozen
ID-ladder row schema, explicit blocked claim flags, and no new probe evidence
or claim promotion.
```

Acceptance state:

```json
{
  "status": "passed",
  "source_backed_inventory": true,
  "id_ladder_schema_frozen": true,
  "becoming_schema_frozen": true,
  "topology_schema_frozen": true,
  "identity_carrier_taxonomy_frozen": true,
  "canonical_control_taxonomy_frozen": true,
  "claim_flags_frozen_false": true,
  "identity_probe_run": false,
  "new_support_rows_emitted": false,
  "src_changes_required": false,
  "next_iteration": "2_fixture_manifest_and_discrete_rc_observable_mapping"
}
```

Implementation records:

```json
{
  "output": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json",
  "report": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_1_baseline_theory_schema_inventory.md",
  "script": "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/build_n07_iteration_1_baseline_theory_schema_inventory.py",
  "schema": "n07_iteration_1_baseline_theory_schema_inventory_v1",
  "execution_stage": "baseline_inventory_no_identity_probe",
  "next_iteration": "2_fixture_manifest_and_discrete_rc_observable_mapping",
  "arc_sources_recorded_by_title_only": true,
  "n04_iter22_and_22b_are_boundary_evidence_only": true,
  "n05_oscillator_is_context_only": true,
  "n06_route_choice_is_context_only": true
}
```

Artifact digests:

```json
{
  "becoming_schema_digest": "6ad45d6586678d977ab98f8a09c434031e2276e54d6d6c6e9bec55b58284d551",
  "claim_flags_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_taxonomy_digest": "cb5dc4c3cbfcfc0fc16a4f342da65c2d76998b5160d78678bfbec7372b0ff873",
  "id_ladder_schema_digest": "afc1c4ae4e0a114c1b0af8f1f13804b6893420ba9e8ac6d76a02c9d0b3ecf8d3",
  "native_surfaces_digest": "8db53ef65e8ef3e67c87ae00eee75c569155dd6608adda499f0c64cf2c8f96a0",
  "source_artifacts_digest": "d33b076cd089bcf16609831b85baf028b2c402766c6f9eddcf5689d2986e8e50",
  "theory_gates_digest": "7101f45f81f6d23fce7eeeafde217e5a28f135446012e73a8e6d0241fa6bfc00",
  "topology_schema_digest": "fe480f0a797cf73b47a185aa0b50cfcdf4a0963ea4e7161694cd8031570d7d75"
}
```

Generated file SHA-256:

```text
56e27d9b0783ac33f97ab06e42e64cf153e9289a00b07e77e02ff17e0ad6b0c2  outputs/n07_iteration_1_baseline_theory_schema_inventory.json
b758dda4f28e33f43f998edc396b3c4ad4c9fab253971b78fe3865d507302841  reports/n07_iteration_1_baseline_theory_schema_inventory.md
b85e5d7ef6f22f6ad81a109d2beef9198ec1c49a013c3a75f2a58abea2c859bf  scripts/build_n07_iteration_1_baseline_theory_schema_inventory.py
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/build_n07_iteration_1_baseline_theory_schema_inventory.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json'; d=json.load(open(p)); assert d['status']=='passed'; assert d['baseline_decisions']['identity_probe_run'] is False; assert d['baseline_decisions']['new_support_rows_emitted'] is False; assert d['baseline_decisions']['src_changes_required'] is False; assert d['acceptance']['claim_flags_frozen_false'] is True; assert d['acceptance']['id_ladder_schema_frozen'] is True; assert d['identity_carrier_taxonomy']['eligible_identity_carrier']=='coherence_basin'; assert d['inherited_boundaries']['n06']['identity_inherited'] is False; assert d['inherited_boundaries']['n04_22b']['rc_identity_supported'] is False; assert all(v is False for v in d['claim_flags'].values()); assert all(not s.get('path_recorded') for s in d['external_sources_by_title']); print({'status': d['status'], 'identity_probe_run': d['baseline_decisions']['identity_probe_run'], 'carrier': d['identity_carrier_taxonomy']['eligible_identity_carrier'], 'claim_flags_false': d['acceptance']['claim_flags_frozen_false'], 'arc_paths_recorded': any(s.get('path_recorded') for s in d['external_sources_by_title'])})"
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json'; d=json.load(open(p)); assert 'identity_threshold_missing' in d['canonical_controls']; assert 'intention_claim_allowed' in d['claim_flags']; assert 'native_observables_used' in d['id_ladder_schema']['row_required_fields']; assert 'experiment_local_observables_used' in d['id_ladder_schema']['row_required_fields']; assert d['id_ladder_schema']['levels'][4]['conditional_required_gates']['lineage_current']['required_value']=='pass'; assert 'pass_if_topology_changes' not in json.dumps(d['id_ladder_schema']); print({'controls': len(d['canonical_controls']), 'claim_flags': len(d['claim_flags']), 'row_fields': len(d['id_ladder_schema']['row_required_fields']), 'conditional_lineage_gate': True})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'identity_probe_run': False, 'carrier': 'coherence_basin', 'claim_flags_false': True, 'arc_paths_recorded': False}
{'controls': 31, 'claim_flags': 15, 'row_fields': 30, 'conditional_lineage_gate': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 2. Fixture Manifest And Discrete RC Observable Mapping

Status: Complete.

- [x] Add topology design policy to the manifest:
  - [x] topology is the experimental object, not just the container
  - [x] each positive topology isolates one identity gate
  - [x] each negative topology breaks one declared property
  - [x] rich omnibus fixtures are disallowed for the first pass
  - [x] primitive fixtures prove gate legibility
  - [x] composite fixtures prove taxonomy usefulness
- [x] Freeze first canonical topology families:
  - [x] `n07_T1_support_area_minimal`
  - [x] `n07_T2_stable_well_basin`
  - [x] `n07_T3_attractor_neighborhood`
  - [x] `n07_T5_lineage_current_invariance`
- [x] For every topology family, declare:
  - [x] `topology_family_id`
  - [x] `target_id_level`
  - [x] `candidate_identity_carrier_type`
  - [x] candidate runtime coherence basin
  - [x] support area
  - [x] neighborhood `U`
  - [x] gate under test
  - [x] primary positive metric
  - [x] paired negative-control topology
  - [x] expected primary blocker
  - [x] expected maximum ID ceiling
  - [x] whether topology mutation occurs
  - [x] whether lineage-current support is required
  - [x] budget surface
  - [x] claim flags
- [x] Define support-area fixture.
- [x] Define candidate basin/support nodes, edges, and ports.
- [x] Define neighborhood `U` for attractivity tests.
- [x] Define support-area digest/idempotency key.
- [x] Define support-area digest as canonical JSON over sorted support ids,
      lineage status/map digest, support surface digest, event/scheduler keys,
      and budget fields, excluding the digest field itself.
- [x] Define `duplicate_support_row` by support-area idempotency key.
- [x] Define stability/well proxy:
  - [x] native policy if available
  - [x] experiment-local proxy only if formula, threshold, input fields, and
        digest scope are declared before the run
  - [x] native-policy blocker when native support is missing or partial
  - [x] blocker if neither native nor declared experiment-local proxy can be
        justified
- [x] Define flux-convergence metric.
- [x] Define flux-convergence native-policy boundary:
  - [x] `native_policy_available = false`
  - [x] `native_policy_blocker = native_attractor_neighborhood_policy_missing`
- [x] Define invariance metric:
  - [x] support overlap
  - [x] lineage-current support mapping
  - [x] proper-time persistence window
  - [x] budget conservation
- [x] Declare invariance thresholds:
  - [x] `support_overlap_threshold`
  - [x] `lineage_current_overlap_threshold`
  - [x] `proper_time_persistence_threshold`
  - [x] `perturbation_magnitude`
  - [x] `perturbation_window`
  - [x] `destructive_perturbation_blocker`
- [x] Define reflexive-closure metric.
- [x] Define reflexive closure as re-entry coherence into support, maintained or
      strengthened basin evidence, later-cycle consumption of updated evidence,
      and exact budget accounting.
- [x] Define coherence-compatibility metric.
- [x] Define compatibility using nonnegative state, exact budget, bounded
      support overlap, no lineage conflict, no hidden support, and bounded
      destructive-interference score.
- [x] Define composite topology policy:
  - [x] composite topologies derive ID ceiling from gate vectors
  - [x] imported prior-experiment surfaces are marked evidence-only unless
        independently validated as identity carriers
  - [x] route choice is not identity
  - [x] movement trace is not identity acceptance
  - [x] mechanical refinement is not identity fission by itself
- [x] Define becoming-method classification fields for every topology row:
  - [x] result is classified at the lowest valid rung
  - [x] probe-supported results are marked as probe-supported
  - [x] withdrawal/support-dependence status is recorded
  - [x] naturalization rung is recorded without promoting identity claims
  - [x] activity-history digest links orientation, observation, classification,
        probe, withdrawal, naturalization, and integration records when present
- [x] Freeze initial composite topology suite:
  - [x] `n07_C1_recurrent_single_basin_identity_candidate`
  - [x] `n07_C2_lineage_current_topology_mutating_identity_candidate`
  - [x] `n07_C3_competing_basin_compatibility_candidate`
  - [x] `n07_C4_route_fed_route_independent_identity_candidate`
  - [x] `n07_C5_movement_carried_movement_independent_identity_candidate`
  - [x] `n07_C6_parent_child_refinement_identity_boundary_candidate`
- [x] For every composite topology, declare:
  - [x] `composite_topology_id`
  - [x] primitive blocks combined
  - [x] expected ID ceiling
  - [x] informative lower ceilings
  - [x] false-positive confusion under test
  - [x] imported prior-experiment surfaces, if any
  - [x] imported surfaces are evidence-only where appropriate
  - [x] identity carrier surface
  - [x] gate vector
  - [x] derived ID ceiling
  - [x] primary blocker
  - [x] claim flags
- [x] Define gate-vector fields:
  - [x] `support`
  - [x] `stability`
  - [x] `attractivity`
  - [x] `invariance`
  - [x] `lineage_current`
  - [x] `reflexive_closure`
  - [x] `compatibility`
  - [x] `artifact_replay`
- [x] Define gate-vector allowed values:
  - [x] `pass`
  - [x] `fail`
  - [x] `blocked`
  - [x] `not_measured`
  - [x] `not_applicable`
- [x] Define derived-ID ceiling algorithm from weakest required gate.
- [x] Define negative controls and primary blockers.
- [x] Include topology-derived negative controls:
  - [x] `label_only_null_topology`
  - [x] `missing_support_area`
  - [x] `external_label_only`
  - [x] `duplicate_support_row`
  - [x] `unstable_basin_no_local_well`
  - [x] `non_attractive_flux`
  - [x] `wrong_polarity`
  - [x] `subthreshold_flux`
  - [x] `wrong_basin`
  - [x] `hidden_route_context_steering`
  - [x] `budget_discontinuity`
  - [x] `stale_node_id_replay`
  - [x] `missing_topology_state_reabsorption`
  - [x] `lineage_map_scrambled`
  - [x] `support_drift_beyond_threshold`
  - [x] `destructive_interference`
  - [x] `ambiguous_overlap`
  - [x] `hidden_support_field`
  - [x] `hidden_potential_or_report_side_well_score`
  - [x] `posthoc_threshold_change`
  - [x] `identity_threshold_missing`
  - [x] `wrong_support_area`
  - [x] `no_reentry`
  - [x] `closure_not_consumed_by_later_cycle`
  - [x] `improper_proper_time_threshold`
  - [x] `failed_persistence`
  - [x] `producer_mutation_boundary_violation`
  - [x] `direct_state_or_topology_rewrite`
  - [x] `unauthorized_identity_acceptance_event`
  - [x] `identity_claim_promotion`
  - [x] `agency_claim_promotion`
- [x] Verify manifest has no hidden identity labels as evidence.
- [x] Verify an authored central node is not treated as identity evidence.
- [x] Verify T4 no-mutation invariance is explicitly deferred as a recurrence
      baseline, not omitted from the topology ladder.
- [x] Verify no `src/*` changes are needed.

Expected artifacts:

- [x] `configs/n07_fixture_manifest_v1.json`
- [x] `outputs/n07_iteration_2_fixture_manifest_validation.json`
- [x] `reports/n07_iteration_2_fixture_manifest_validation.md`

Acceptance statement:

```text
Iteration 2 passes if N07 has a topology design policy and manifest that map
RC identity gates to runtime-visible LGRC observables. The manifest freezes the
first canonical primitive topology families and the initial composite topology
suite, declares support/neighborhood/budget/lineage fields, derives controls
from the topology ladder, defines gate-vector classification, rejects hidden
labels or authored central-node identity, and declares distinct blockers for
missing support, unstable basins, non-attractive flux, stale lineage, budget
discontinuity, and claim promotion.
```

Acceptance state:

```json
{
  "status": "passed",
  "checks_passed": true,
  "manifest_declared": true,
  "controls_declared": true,
  "validation_check_count": 45,
  "topology_family_count": 4,
  "composite_topology_count": 6,
  "control_count": 31,
  "identity_probe_run": false,
  "support_rows_emitted": false,
  "positive_identity_evidence_generated": false,
  "topology_family_gates_valid": true,
  "topology_family_metrics_resolve": true,
  "composite_primitive_refs_resolve": true,
  "becoming_enum_values_declared": true,
  "claim_flags_all_false": true,
  "src_changes_required": false,
  "next_iteration": "3_id1_support_area_candidate"
}
```

Run record:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/validate_n07_fixture_manifest.py
```

Result:

```json
{"checks_passed": true, "composite_topology_count": 6, "control_count": 31, "identity_probe_run": false, "manifest": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json", "output": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json", "report": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_2_fixture_manifest_validation.md", "status": "passed", "support_rows_emitted": false, "topology_family_count": 4}
```

Artifact digests:

```json
{
  "checks_digest": "c71087b29078131e270c2d9508d6f3474762a88cc66d7838e6f6342a4a68e8ae",
  "claim_boundary_digest": "462a721dd54e1b29c82d73cd4385d84b0021f96e51825c4c4aaea3214044ea7b",
  "composite_topologies_digest": "836e37869b5740a8770c8707d160c1ca8e0abde89742de76b96698ee1bbb624f",
  "controls_digest": "4cd7e48045aaabb0dc80b30878b7b680fa10254617cd4310803dfd85e9ddfca5",
  "manifest_digest": "89d46bf941cb40f359b99381f0c7d1b391f67ae3eb07955ec850a8c03a242e5e",
  "metric_definitions_digest": "4f41926bce131f4022aa472cbf83c6ef64f461275ddb5550d4f17dae2c562a1f",
  "topology_families_digest": "5cefd2b9f0a7e66a3d0d26b21ab7111c0111d5a82bff81849f7a3a0df808a949"
}
```

Generated file SHA-256:

```text
e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603  configs/n07_fixture_manifest_v1.json
b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26  outputs/n07_iteration_2_fixture_manifest_validation.json
e7796b9cf4467d48f5778fcdbadd75c6ce4d1742cdbfa9401b7036e834085a82  reports/n07_iteration_2_fixture_manifest_validation.md
f330f53a0b251746946824f9fe1b89ad235642bbbdd3e7d0d5af096f5f8d6c22  scripts/validate_n07_fixture_manifest.py
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/validate_n07_fixture_manifest.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json'; d=json.load(open(p)); flux=d['manifest']['metric_definitions']['flux_convergence']; assert d['status']=='passed'; assert all(d['checks'].values()); assert d['identity_probe_run'] is False; assert d['support_rows_emitted'] is False; assert d['positive_identity_evidence_generated'] is False; assert len(d['manifest']['topology_families']) == 5; assert len(d['manifest']['composite_topologies']) == 6; assert len(d['manifest']['controls']) == 31; assert d['manifest']['support_area']['lineage_status'] == 'fixed_topology'; assert flux['native_policy_available'] is False; assert flux['native_policy_blocker']=='native_attractor_neighborhood_policy_missing'; assert d['checks']['support_area_digest_matches'] is True; assert d['checks']['t4_deferred_with_rationale'] is True; assert d['checks']['hidden_identity_labels_blocked'] is True; assert d['checks']['claim_flags_all_false'] is True; assert d['checks']['topology_family_gates_valid'] is True; assert d['checks']['topology_family_metrics_resolve'] is True; assert d['checks']['composite_primitive_refs_resolve'] is True; assert d['checks']['becoming_enum_values_declared'] is True; assert [f for f in d['manifest']['topology_families'] if f['topology_family_id']=='n07_T5_lineage_current_invariance'][0]['gate_under_test'] == 'lineage_current'; assert [f for f in d['manifest']['topology_families'] if f['topology_family_id']=='n07_T6_reflexive_closure'][0]['gate_under_test'] == 'reflexive_closure'; print({'status': d['status'], 'checks_passed': all(d['checks'].values()), 'identity_probe_run': d['identity_probe_run'], 'support_rows_emitted': d['support_rows_emitted'], 'controls': len(d['manifest']['controls']), 'topology_families': len(d['manifest']['topology_families']), 'composites': len(d['manifest']['composite_topologies']), 'lineage_status': d['manifest']['support_area']['lineage_status'], 'flux_native_policy_blocker': flux['native_policy_blocker']})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_manifest_passed
json_tool_output_passed
py_compile_passed
{'status': 'passed', 'checks_passed': True, 'identity_probe_run': False, 'support_rows_emitted': False, 'controls': 31, 'topology_families': 5, 'composites': 6, 'lineage_status': 'fixed_topology', 'flux_native_policy_blocker': 'native_attractor_neighborhood_policy_missing'}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 3. ID1 Support-Area Candidate

Status: Complete.

- [x] Emit or derive a runtime-visible support-area candidate.
- [x] Record support nodes, edges, ports, lineage ids, surface digest, event
      time, scheduler index, and budget fields.
- [x] Record that Iteration 3 runs zero LGRC `step()` cycles.
- [x] Record that `scheduler_event_index = 0` is a support-commit marker,
      not a runtime simulation step.
- [x] Record that the support area is manifest-derived from Iteration 2,
      not discovered from dynamic stability.
- [x] Record that the stability probe is deferred to Iteration 4.
- [x] Verify the candidate row's topology family, gate, primary metric, target
      ID level, lineage status, claim flags, gate-vector values, native support
      status, and becoming-method fields against the Iteration 2 manifest.
- [x] Verify the support area is source-backed, not report-side only.
- [x] Verify support area does not imply identity.
- [x] Verify `candidate_identity_carrier_type == coherence_basin`.
- [x] Verify `surface_row`, `deformation_token`, `boundary_signal`, route
      selection, and movement traces are evidence-only if present.
- [x] Run controls:
  - [x] `label_only_null_topology`
  - [x] `missing_support_area`
  - [x] `external_label_only`
  - [x] `hidden_support_field`
  - [x] `duplicate_support_row`
  - [x] `budget_discontinuity`
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_3_id1_support_area_candidate.json`
- [x] `reports/n07_iteration_3_id1_support_area_candidate.md`

Acceptance statement:

```text
Iteration 3 passes if a support-area candidate is emitted from runtime-visible
evidence with exact budget accounting, manifest-contract checks, and controls,
while recording that no LGRC step cycles or stability dynamics were run and
while identity, identity-acceptance, and agency claims remain blocked.
```

Acceptance state:

```json
{
  "status": "passed",
  "checks_passed": true,
  "derived_id_ceiling": "ID1",
  "claim_ceiling": "support_area_candidate",
  "native_support_status": "experiment_local",
  "support_area_source_backed": true,
  "support_area_runtime_visible": true,
  "step_cycles_run": 0,
  "lgrc_step_invocations": 0,
  "support_area_derivation": "manifest_declared_support_core",
  "support_area_discovered_by_dynamics": false,
  "stability_probe_run": false,
  "stability_deferred_to_iteration_4": true,
  "manifest_contract_checks_passed": true,
  "paired_negative_control_topology": "label_only_null_topology",
  "support_area_not_identity_claim": true,
  "budget_exact": true,
  "validation_check_count": 31,
  "control_count": 6,
  "controls_blocked": true,
  "control_blockers_distinct": true,
  "claim_flags_all_false": true,
  "identity_acceptance_blocked": true,
  "src_changes_required": false,
  "next_iteration": "4_id2_stability_candidate"
}
```

Run record:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_3_id1_support_area_candidate.py
```

Result:

```json
{"checks_passed": true, "claim_ceiling": "support_area_candidate", "claim_flags_false": true, "control_count": 6, "derived_id_ceiling": "ID1", "manifest_contract_checks_passed": true, "native_support_status": "experiment_local", "stability_deferred_to_iteration_4": true, "status": "passed", "step_cycles_run": 0, "support_area_discovered_by_dynamics": false, "support_area_derivation": "manifest_declared_support_core", "validation_check_count": 31}
```

Artifact digests:

```json
{
  "checks_digest": "2f9af72dbcf16a74f2aff435877cbf889eedd994371b39ae38418d26d72fdf4b",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "ea97659931681a32a80b00efcb10f85bf440d4fe346a3c65903bca7bc3cf7e0a",
  "execution_boundary_digest": "ea45152d1633d0f9cc314543b3d52a3accebbff059381f70003373e5bf3b50a1",
  "id1_candidate_row_digest": "c0b9112eec28c076fc149767c18fc0bfac2410f03b602918021890337dd9ac1b",
  "source_support_event_digest": "3944f51fcd6dad9b1b751ecd8899c501084d2a66d50e90c7bf6ff50950ef7baf",
  "support_area_row_digest": "9fdc6d7862752cfbca82baccb96d1c6b5814c53b7acbaf399c3adb4fca2fda4b"
}
```

Generated file SHA-256:

```text
05389b5ea5381b3bbd4680b2be5c33628cce51108cf5d16b697d212686c39a3f  outputs/n07_iteration_3_id1_support_area_candidate.json
fb92b6e28a6604bbd9e05b0189acd4d2ab85e7bbbdcf9c897b157e34fe64a437  reports/n07_iteration_3_id1_support_area_candidate.md
d3a5a0d2df8a984ec60f10e06c3a5bbfc79fd65915928782e6b6f1369635dcf7  scripts/run_n07_iteration_3_id1_support_area_candidate.py
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_3_id1_support_area_candidate.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 31; assert d['id1_candidate_row']['derived_id_ceiling']=='ID1'; assert d['id1_candidate_row']['claim_ceiling']=='support_area_candidate'; assert d['id1_candidate_row']['native_support_status']=='experiment_local'; assert d['support_area_row']['source_backed'] is True; assert d['support_area_row']['runtime_visible'] is True; assert d['support_area_row']['budget_error'] == 0.0; assert d['support_area_row']['lineage_status'] == d['manifest']['support_area']['lineage_status'] == 'fixed_topology'; assert d['checks']['candidate_topology_family_matches_manifest'] is True; assert d['checks']['candidate_gate_matches_manifest'] is True; assert d['checks']['candidate_primary_metric_matches_manifest'] is True; assert d['checks']['candidate_target_id_matches_manifest'] is True; assert d['checks']['paired_negative_control_present'] is True; assert d['checks']['claim_flag_keys_match_manifest'] is True; assert d['checks']['gate_vector_schema_matches_manifest'] is True; assert d['checks']['native_support_status_value_allowed'] is True; assert d['checks']['becoming_method_values_allowed'] is True; assert d['execution_boundary']['step_cycles_run'] == 0; assert d['execution_boundary']['lgrc_step_invocations'] == 0; assert d['execution_boundary']['support_area_derivation'] == 'manifest_declared_support_core'; assert d['execution_boundary']['support_area_discovered_by_dynamics'] is False; assert d['execution_boundary']['stability_probe_run'] is False; assert d['execution_boundary']['stability_deferred_to_iteration_4'] is True; assert len(d['control_rows']) == 6; assert 'label_only_null_topology' in {c['control_id'] for c in d['control_rows']}; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID0' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 6; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks_passed': all(d['checks'].values()), 'validation_check_count': len(d['checks']), 'derived_id_ceiling': d['id1_candidate_row']['derived_id_ceiling'], 'claim_ceiling': d['id1_candidate_row']['claim_ceiling'], 'native_support_status': d['id1_candidate_row']['native_support_status'], 'step_cycles_run': d['execution_boundary']['step_cycles_run'], 'support_area_derivation': d['execution_boundary']['support_area_derivation'], 'support_area_discovered_by_dynamics': d['execution_boundary']['support_area_discovered_by_dynamics'], 'stability_deferred_to_iteration_4': d['execution_boundary']['stability_deferred_to_iteration_4'], 'manifest_contract_checks_passed': d['acceptance']['manifest_contract_checks_passed'], 'control_count': len(d['control_rows']), 'claim_flags_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks_passed': True, 'validation_check_count': 31, 'derived_id_ceiling': 'ID1', 'claim_ceiling': 'support_area_candidate', 'native_support_status': 'experiment_local', 'step_cycles_run': 0, 'support_area_derivation': 'manifest_declared_support_core', 'support_area_discovered_by_dynamics': False, 'stability_deferred_to_iteration_4': True, 'manifest_contract_checks_passed': True, 'control_count': 6, 'claim_flags_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 4. ID2 Stability / Local Well Candidate

Status: Complete.

Run record:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_4_id2_stability_candidate.py
```

- [x] Apply the manifest-declared stability/well proxy.
- [x] Verify local stability evidence is serialized.
- [x] Verify thresholds/proxies are fixed before the run.
- [x] Verify no hidden potential or report-side well score is used.
- [x] Verify support-area mass/proper-time persistence is source-backed.
- [x] Verify the Iteration 3 ID1 support-area row is consumed as the source
      support evidence.
- [x] Verify the stability score is recomputable from serialized inputs:
      `0.5 * support_area_mass_retention + 0.5 *
      local_inflow_dominance_score`.
- [x] Verify the score `0.9085714285714286` passes the fixed threshold `0.75`.
- [x] Verify proper-time samples are ordered by ascending proper-time index.
- [x] Verify aggregate incoming/outgoing flux values match the per-sample
      sums.
- [x] Record native policy blocker
      `native_basin_potential_policy_missing`.
- [x] Verify `candidate_identity_carrier_type == coherence_basin`.
- [x] Verify `surface_row`, `deformation_token`, `boundary_signal`, route
      selection, and movement traces are evidence-only if present.
- [x] Run controls:
  - [x] `unstable_basin_no_local_well`
  - [x] `posthoc_threshold_change`
  - [x] `hidden_potential_or_report_side_well_score`
  - [x] `wrong_support_area`
  - [x] `budget_discontinuity`
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_4_id2_stability_candidate.json`
- [x] `reports/n07_iteration_4_id2_stability_candidate.md`

Acceptance statement:

```text
Iteration 4 passes if the support area also satisfies a declared stability
proxy with source-backed thresholds and negative controls. Stability is still
not identity acceptance.
```

Acceptance state:

```json
{
  "status": "passed",
  "checks_passed": true,
  "validation_check_count": 33,
  "derived_id_ceiling": "ID2",
  "claim_ceiling": "stable_basin_candidate",
  "native_support_status": "experiment_local",
  "stability_proxy_policy": "experiment_local_declared_second_difference_retention_proxy",
  "stability_score": 0.9085714285714286,
  "stability_threshold": 0.75,
  "stability_threshold_fixed_before_run": true,
  "support_gate_passed": true,
  "stability_gate_passed": true,
  "source_id1_consumed": true,
  "hidden_potential_or_report_side_score_used": false,
  "posthoc_threshold_change_used": false,
  "budget_exact": true,
  "manifest_contract_checks_passed": true,
  "control_count": 5,
  "controls_blocked": true,
  "control_blockers_distinct": true,
  "control_ceilings": "ID1",
  "claim_flags_all_false": true,
  "identity_acceptance_blocked": true,
  "native_policy_blockers": [
    "native_basin_potential_policy_missing"
  ],
  "src_changes_required": false,
  "next_iteration": "5_id3_attractivity_candidate"
}
```

Result:

```json
{"checks_passed": true, "claim_ceiling": "stable_basin_candidate", "claim_flags_false": true, "control_count": 5, "derived_id_ceiling": "ID2", "native_support_status": "experiment_local", "stability_score": 0.9085714285714286, "status": "passed", "threshold": 0.75, "validation_check_count": 33}
```

Artifact digests:

```json
{
  "checks_digest": "a55708f5f3af0ca23becaf3e84b9cacf7e322c75fcd6b72a70a315a45df347f0",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "bc956df2a40021d1624e5ca09832e26d4ba9dc38039868b3b139af807a120403",
  "id2_candidate_row_digest": "6c08ee866b185464a2ff49424453e28519e2c8ca26807aab7abd4e58ff9fcdba",
  "source_id1_output_digest": "d205952470866a09af372d225920e0b4c6dea191098d9cb55142854de1bea6f9",
  "stability_observation_event_digest": "7d5a85dd31170f2735e51b170710b0b452f35f6a1ba000a1ff8149c1334aa37e",
  "stability_proxy_record_digest": "9481a7f1a6be363b399b92a68ca6603a1ef7eb5d7cd86e460bdbdfb40a9f0b81"
}
```

Generated file SHA-256:

```text
e08f05724898a11150515afe486679bd98eda2130edf35cdb19e2a54e0983cb3  outputs/n07_iteration_4_id2_stability_candidate.json
743f516d45030286b8235c8b4b4c780399f6c479b817f2d38654fe1fceac848b  reports/n07_iteration_4_id2_stability_candidate.md
11985805d94f242f3dce38b94f6751fa9cd4fcd387ddf9652d7a67c2b548c673  scripts/run_n07_iteration_4_id2_stability_candidate.py
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_4_id2_stability_candidate.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 33; assert d['source_id1_output']['status']=='passed'; assert d['id2_candidate_row']['derived_id_ceiling']=='ID2'; assert d['id2_candidate_row']['claim_ceiling']=='stable_basin_candidate'; assert d['id2_candidate_row']['native_support_status']=='experiment_local'; assert d['stability_proxy_record']['stability_gate']=='pass'; assert d['stability_proxy_record']['thresholds_fixed_before_run'] is True; assert d['stability_proxy_record']['hidden_potential_or_report_side_well_score_used'] is False; assert d['stability_proxy_record']['posthoc_threshold_change_used'] is False; assert d['stability_proxy_record']['native_policy_blocker']=='native_basin_potential_policy_missing'; assert d['checks']['stability_score_recomputed'] is True; assert d['checks']['stability_score_above_threshold'] is True; assert d['checks']['proper_time_samples_source_backed'] is True; assert d['checks']['proper_time_sample_ordering_valid'] is True; assert d['checks']['proper_time_flux_aggregates_match_samples'] is True; assert d['checks']['native_support_not_overstated'] is True; assert d['stability_proxy_record']['budget_error'] == 0.0; assert len(d['control_rows']) == 5; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID1' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 5; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks_passed': all(d['checks'].values()), 'validation_check_count': len(d['checks']), 'derived_id_ceiling': d['id2_candidate_row']['derived_id_ceiling'], 'claim_ceiling': d['id2_candidate_row']['claim_ceiling'], 'native_support_status': d['id2_candidate_row']['native_support_status'], 'stability_score': d['stability_proxy_record']['stability_score'], 'threshold': d['stability_proxy_record']['threshold'], 'control_count': len(d['control_rows']), 'claim_flags_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks_passed': True, 'validation_check_count': 33, 'derived_id_ceiling': 'ID2', 'claim_ceiling': 'stable_basin_candidate', 'native_support_status': 'experiment_local', 'stability_score': 0.9085714285714286, 'threshold': 0.75, 'control_count': 5, 'claim_flags_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 5. ID3 Attractivity / Flux Convergence

Status: Complete.

Run record:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5_id3_attractivity_candidate.py
```

- [x] Declare an open-neighborhood proxy `U`.
- [x] Emit or derive flux from `U` toward the candidate support area.
- [x] Verify flux convergence by runtime-visible packet/surface evidence.
- [x] Verify budget and nonnegative state across convergence.
- [x] Verify convergence is not preselected by fixture labels.
- [x] Verify the Iteration 4 ID2 stable-basin row is consumed as source
      evidence.
- [x] Verify the manifest-declared flux metric:
      `net_flux_into_support_from_U > net_flux_out_of_support`.
- [x] Verify the manifest-declared flux native-policy fields:
      `native_policy_available = false` and
      `native_policy_blocker = native_attractor_neighborhood_policy_missing`.
- [x] Verify incoming source nodes and outgoing target nodes are members of
      the declared neighborhood `U`.
- [x] Verify packet event ids are unique.
- [x] Verify packet `route_node_ids` follow declared manifest edges.
- [x] Verify manifest-declared flux controls are exercised.
- [x] Verify incoming flux `0.3`, outgoing flux `0.06`, and convergence
      margin `0.24` against threshold `0.0`.
- [x] Record native policy blocker
      `native_attractor_neighborhood_policy_missing`.
- [x] Run controls:
  - [x] `non_attractive_flux`
  - [x] `wrong_basin`
  - [x] `wrong_polarity`
  - [x] `subthreshold_flux`
  - [x] `hidden_route_context_steering`
  - [x] `budget_discontinuity`
- [x] Verify `candidate_identity_carrier_type == coherence_basin`.
- [x] Verify `surface_row`, `deformation_token`, `boundary_signal`, route
      selection, and movement traces are evidence-only if present.
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_5_id3_attractivity_candidate.json`
- [x] `reports/n07_iteration_5_id3_attractivity_candidate.md`

Acceptance statement:

```text
Iteration 5 passes if flux from a declared runtime-visible neighborhood
converges into the stable support area under exact budget accounting and
controls. Attractivity is still not agency.
```

Acceptance state:

```json
{
  "status": "passed",
  "checks_passed": true,
  "validation_check_count": 37,
  "derived_id_ceiling": "ID3",
  "claim_ceiling": "attractor_candidate",
  "native_support_status": "experiment_local",
  "flux_metric_id": "n07_flux_convergence_to_support_v1",
  "neighborhood_U_declared": true,
  "net_flux_into_support_from_U": 0.3,
  "net_flux_out_of_support": 0.06,
  "flux_margin": 0.24,
  "positive_threshold": 0.0,
  "support_gate_passed": true,
  "stability_gate_passed": true,
  "attractivity_gate_passed": true,
  "source_id2_consumed": true,
  "runtime_visible_packet_work_events": true,
  "preselected_by_fixture_label": false,
  "hidden_route_context_steering_used": false,
  "budget_exact": true,
  "nonnegative_state_passed": true,
  "manifest_contract_checks_passed": true,
  "control_count": 6,
  "controls_blocked": true,
  "control_blockers_distinct": true,
  "control_ceilings": "ID2",
  "claim_flags_all_false": true,
  "identity_acceptance_blocked": true,
  "agency_blocked": true,
  "native_policy_blockers": [
    "native_attractor_neighborhood_policy_missing"
  ],
  "src_changes_required": false,
  "next_iteration": "5B_id3_attractivity_stress_candidate"
}
```

Result:

```json
{"checks_passed": true, "claim_ceiling": "attractor_candidate", "claim_flags_false": true, "control_count": 6, "derived_id_ceiling": "ID3", "flux_margin": 0.24, "incoming": 0.3, "native_support_status": "experiment_local", "outgoing": 0.06, "status": "passed", "threshold": 0.0, "validation_check_count": 37}
```

Artifact digests:

```json
{
  "checks_digest": "20d7aa05c27236aa7076dd45b92eb87c967af10bc15c85ae76cd28847e6750d7",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "ebc029486a0c77ab24f81512c6885e1ff036f0fc0374cfa7de1a0df9c1c96205",
  "flux_convergence_record_digest": "51c371ed6ee97dd723f5841bc135a4b938e30fec6d218e2759b4529b6e7630d0",
  "flux_observation_event_digest": "7099af2135c8ded2af842cf3e54b3bedda7274b595ba53176828996202c876c6",
  "id3_candidate_row_digest": "b0a016102dcd69f483878d4bff8aff656a0987f4afa82c4c86dabd01553c1e63",
  "source_id2_output_digest": "2ad5d0a9237c8cbecce4b4e61027af0c31d9a0bc14a93c05b57038ac549b6976"
}
```

Generated file SHA-256:

```text
3c812eb11c21a99030ae935a09156f221df0dff28a73dc7969ac974a3e532166  outputs/n07_iteration_5_id3_attractivity_candidate.json
b0bd1e59d6a35d3a9f3b83ced10078c1bbf9879b09ef24b44abbb7ed4b2a9bf6  reports/n07_iteration_5_id3_attractivity_candidate.md
f00c0e397a068f4d6afd65eaa5773cfeedfd2659afe7b0344d6940aa96b95ef2  scripts/run_n07_iteration_5_id3_attractivity_candidate.py
```

Additional validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5_id3_attractivity_candidate.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 37; assert d['source_id2_output']['status']=='passed'; assert d['id3_candidate_row']['derived_id_ceiling']=='ID3'; assert d['id3_candidate_row']['claim_ceiling']=='attractor_candidate'; assert d['id3_candidate_row']['native_support_status']=='experiment_local'; assert d['acceptance']['next_iteration']=='5B_id3_attractivity_stress_candidate'; assert d['flux_convergence_record']['attractivity_gate']=='pass'; assert d['flux_convergence_record']['net_flux_into_support_from_U'] == 0.3; assert d['flux_convergence_record']['net_flux_out_of_support'] == 0.06; assert d['flux_convergence_record']['net_flux_convergence_margin'] == 0.24; assert d['flux_convergence_record']['positive_threshold'] == 0.0; assert d['flux_convergence_record']['native_policy_blocker']=='native_attractor_neighborhood_policy_missing'; assert d['checks']['flux_native_policy_fields_match_manifest'] is True; assert d['checks']['flux_nodes_are_members_of_neighborhood_u'] is True; assert d['checks']['packet_event_ids_unique'] is True; assert d['checks']['packet_routes_follow_manifest_edges'] is True; assert d['checks']['manifest_flux_controls_exercised'] is True; assert d['flux_convergence_record']['hidden_route_context_steering_used'] is False; assert d['flux_convergence_record']['preselected_by_fixture_label'] is False; assert d['checks']['flux_margin_recomputed'] is True; assert d['checks']['flux_convergence_passed'] is True; assert d['checks']['flux_events_runtime_visible'] is True; assert d['checks']['nonnegative_state_passed'] is True; assert d['checks']['native_support_not_overstated'] is True; assert d['flux_convergence_record']['budget_error'] == 0.0; assert len(d['control_rows']) == 6; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID2' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 6; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks_passed': all(d['checks'].values()), 'validation_check_count': len(d['checks']), 'derived_id_ceiling': d['id3_candidate_row']['derived_id_ceiling'], 'claim_ceiling': d['id3_candidate_row']['claim_ceiling'], 'native_support_status': d['id3_candidate_row']['native_support_status'], 'incoming': d['flux_convergence_record']['net_flux_into_support_from_U'], 'outgoing': d['flux_convergence_record']['net_flux_out_of_support'], 'flux_margin': d['flux_convergence_record']['net_flux_convergence_margin'], 'threshold': d['flux_convergence_record']['positive_threshold'], 'next_iteration': d['acceptance']['next_iteration'], 'control_count': len(d['control_rows']), 'claim_flags_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks_passed': True, 'validation_check_count': 37, 'derived_id_ceiling': 'ID3', 'claim_ceiling': 'attractor_candidate', 'native_support_status': 'experiment_local', 'incoming': 0.3, 'outgoing': 0.06, 'flux_margin': 0.24, 'threshold': 0.0, 'next_iteration': '5B_id3_attractivity_stress_candidate', 'control_count': 6, 'claim_flags_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 5-B. ID3 Attractivity Stress / Multi-Source, Multi-Window Convergence

Status: Complete.

- [x] Treat Iteration 5 as a first-pass attractivity candidate, not a complete
      basin-attractor proof.
- [x] Reuse the declared neighborhood `U` and support area from the manifest.
- [x] Run at least two distinct source points in `U` toward the candidate
      support area.
- [x] Run more than one event/proper-time window.
- [x] Verify each positive window has runtime-visible packet/surface evidence.
- [x] Verify convergence by a stricter approach metric:
  - [x] distance-to-support decreases or remains non-increasing, and
  - [x] declared potential/score decreases toward support.
- [x] Verify support-area evidence remains stable after inflow.
- [x] Verify inflow is not immediately lost or only routed through the support
      area.
- [x] Verify budget and nonnegative state across every window.
- [x] Verify no hidden route-context steering or fixture-label preselection.
- [x] Record whether native LGRC has a native attractor-neighborhood policy;
      if missing, keep `native_support_status = experiment_local`.
- [x] Run controls:
  - [x] `non_attractive_flux`
  - [x] `wrong_basin`
  - [x] `wrong_polarity`
  - [x] `subthreshold_flux`
  - [x] `hidden_route_context_steering`
  - [x] `failed_persistence`
  - [x] `budget_discontinuity`
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json`
- [x] `reports/n07_iteration_5b_id3_attractivity_stress_candidate.md`

Acceptance statement:

```text
Iteration 5-B passes if attractivity remains positive across multiple
runtime-visible source points and multiple windows from the declared
neighborhood U, with a serialized approach metric, exact budget accounting,
stable post-inflow support evidence, and distinct controls. It strengthens the
ID3 attractor candidate but does not promote to ID4, agency, identity
acceptance, or native identity support.
```

Implementation records:

- Runner:
  `scripts/run_n07_iteration_5b_id3_attractivity_stress_candidate.py`
- Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5b_id3_attractivity_stress_candidate.py
```

Run result:

```json
{
  "status": "passed",
  "checks_passed": true,
  "validation_check_count": 39,
  "derived_id_ceiling": "ID3",
  "claim_ceiling": "attractor_candidate_stress_validated",
  "native_support_status": "experiment_local",
  "window_count": 3,
  "distinct_source_count": 2,
  "support_retention_after_inflow_passed": true,
  "approach_metric_passed": true,
  "next_iteration": "6_id4_invariance_candidate",
  "control_count": 7,
  "claim_flags_false": true
}
```

Artifact digests:

```json
{
  "source_iteration_5_output_digest": "1cb8febb4c5dc43989d5134e81ffeaeb321228ba85add5c06d14bbd3b4e5e7ae",
  "multi_window_event_digest": "359c5262635f166dce7f2945e4d41ee79ae238ded18f85a086d21c402086bbed",
  "attractivity_stress_record_digest": "0703c12ed509ada2b0dc2a615c148b1a413531b3a0463df8df4373f4ba8ceb6e",
  "id3_stress_candidate_row_digest": "bdd0d4bedc545e4aed2d2c8b38a12821cdff9ac17885493c406f67e2bf1053d9",
  "control_rows_digest": "bbf1cbe0b404d4047e0e295cd15b287a456ba2565479b8d3329e7c7efba202f3",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "checks_digest": "8703ac5bf2585b6005224e967ec2712c19798106bd81b45c54482053e040f9a8"
}
```

Generated file SHA-256:

```text
7552168e8df8ec7ae177b90be3e44be9848605c52069ebfba762326e489f91b8  outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json
93c1dbc11f57200464f6eb1c72d058b8b8807022ae23f30a4bbd47c56d215163  reports/n07_iteration_5b_id3_attractivity_stress_candidate.md
a5c5c09a00bd6e5873b80158739d90c317609fe5b28fa264832d98f117918698  scripts/run_n07_iteration_5b_id3_attractivity_stress_candidate.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5b_id3_attractivity_stress_candidate.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 39; assert d['source_iteration_5_output']['status']=='passed'; assert d['multi_window_attractivity_event']['window_count'] == 3; assert d['multi_window_attractivity_event']['distinct_source_count'] == 2; assert d['attractivity_stress_record']['support_retention_after_inflow_passed'] is True; assert d['attractivity_stress_record']['approach_metric_passed'] is True; assert d['id3_attractivity_stress_candidate_row']['derived_id_ceiling']=='ID3'; assert d['id3_attractivity_stress_candidate_row']['claim_ceiling']=='attractor_candidate_stress_validated'; assert d['id3_attractivity_stress_candidate_row']['native_support_status']=='experiment_local'; assert d['acceptance']['next_iteration']=='6_id4_invariance_candidate'; assert len(d['control_rows']) == 7; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID2' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 7; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': d['acceptance']['derived_id_ceiling'], 'window_count': d['multi_window_attractivity_event']['window_count'], 'source_count': d['multi_window_attractivity_event']['distinct_source_count'], 'retention': d['attractivity_stress_record']['support_retention_after_inflow_passed'], 'approach': d['attractivity_stress_record']['approach_metric_passed'], 'native': d['acceptance']['native_support_status'], 'next': d['acceptance']['next_iteration'], 'controls': len(d['control_rows']), 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 39, 'checks_passed': True, 'ceiling': 'ID3', 'window_count': 3, 'source_count': 2, 'retention': True, 'approach': True, 'native': 'experiment_local', 'next': '6_id4_invariance_candidate', 'controls': 7, 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 6. ID4 Invariance Across Cycles, Perturbation, And Lineage

Status: Complete.

- [x] Repeat the support/stability/attractivity chain across multiple cycles.
- [x] Add mild perturbation control.
- [x] Add topology/lineage context if supported by existing artifacts.
- [x] Verify support is lineage-current after topology changes.
- [x] Verify stale node ids/support rows fail closed.
- [x] Verify identity support overlap and/or lineage continuity is above the
      declared threshold.
- [x] Verify overlap is declared as lineage-weighted and literal node-set
      overlap is serialized separately.
- [x] Verify perturbation magnitude/window match manifest-declared values.
- [x] Verify invariance record digest recomputes from its declared digest input.
- [x] Verify topology-state reabsorption budget fields match surrounding cycle
      budget fields.
- [x] Verify transported node ids do not collide with original fixture node ids.
- [x] Verify `candidate_identity_carrier_type == coherence_basin`.
- [x] Verify `surface_row`, `deformation_token`, `boundary_signal`, route
      selection, and movement traces are evidence-only if present.
- [x] Run controls:
  - [x] `stale_node_id_replay`
  - [x] `missing_topology_state_reabsorption`
  - [x] `lineage_map_scrambled`
  - [x] `support_drift_beyond_threshold`
  - [x] `budget_discontinuity`
  - [x] `identity_claim_promotion`
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_6_id4_invariance_candidate.json`
- [x] `reports/n07_iteration_6_id4_invariance_candidate.md`

Acceptance statement:

```text
Iteration 6 passes if the candidate basin remains lineage-current and
identity-continuous across repeated cycles, perturbation, and any declared
topology lineage context. Invariance is still not unrestricted identity.
```

Implementation records:

- Runner:
  `scripts/run_n07_iteration_6_id4_invariance_candidate.py`
- Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6_id4_invariance_candidate.py
```

Run result:

```json
{
  "status": "passed",
  "checks_passed": true,
  "validation_check_count": 43,
  "derived_id_ceiling": "ID4",
  "claim_ceiling": "invariant_basin_candidate",
  "native_support_status": "mixed_native_experiment_local",
  "proper_time_window_count": 4,
  "support_overlap_min": 0.96,
  "lineage_current_overlap_min": 0.97,
  "support_overlap_threshold": 0.95,
  "lineage_current_overlap_threshold": 0.95,
  "perturbation_magnitude": 0.1,
  "perturbation_window": "one_proper_time_window",
  "topology_lineage_context_present": true,
  "identity_inherited_from_infrastructure": false,
  "native_policy_blockers": [
    "native_identity_invariance_policy_missing"
  ],
  "control_count": 6,
  "claim_flags_false": true,
  "next_iteration": "6B_id4_topology_split_birth_invariance_stress"
}
```

Artifact digests:

```json
{
  "checks_digest": "d1cd83cbf6d45ef62751bb267c76e036c9c58d70d0e4d7a6c30e9901ec632ca2",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "30400e77b2396f4fe19e3a9a0ea3b8f1c65124bed1e84884800eaca8b41abf64",
  "id4_candidate_row_digest": "b98fcaab33396a6f052f602b39066dd17c0e72683079289ae94af9f10d8c9d3f",
  "invariance_cycle_event_digest": "4f703d1653d38508bcbac64895eab79e93e40bca641d42c5b538d7eff411b039",
  "invariance_record_digest": "f4c55a80f5842126126c7291ee8787d7b8ef9196b1e9b9df814c4947a22c2f69",
  "source_iteration_5b_output_digest": "510e44a011aeae3efad226d16de23cfd87fb751ea1b4e10da4890325d97033cb",
  "topology_lineage_context_digest": "7fb61fee01f595296c6958cc2ada97279b9bb002a2c1752519dbd6043a1e1427"
}
```

Generated file SHA-256:

```text
03d687b0fcaaa8ba0591aed9f7b2b9a5c5e7b53d4c1aed4cca7f9cc8cdd5b2ba  outputs/n07_iteration_6_id4_invariance_candidate.json
e627d318044d0286f6fec5cc968dba69a273bbbd88a30b413dae34eea004e8f3  reports/n07_iteration_6_id4_invariance_candidate.md
7e8b248d80fc80179bcecc3dbceba5a86f45fccad771e9baf882198aedd5735b  scripts/run_n07_iteration_6_id4_invariance_candidate.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6_id4_invariance_candidate.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 43; assert d['source_iteration_5b_output']['status']=='passed'; assert d['id4_invariance_candidate_row']['derived_id_ceiling']=='ID4'; assert d['id4_invariance_candidate_row']['claim_ceiling']=='invariant_basin_candidate'; assert d['id4_invariance_candidate_row']['native_support_status']=='mixed_native_experiment_local'; assert d['invariance_record']['support_overlap_min'] == 0.96; assert d['invariance_record']['lineage_current_overlap_min'] == 0.97; assert d['invariance_record']['proper_time_window_count'] == 4; assert d['invariance_record']['native_policy_blocker']=='native_identity_invariance_policy_missing'; assert d['topology_lineage_context']['support_lineage_current'] is True; assert d['topology_lineage_context']['identity_inherited_from_infrastructure'] is False; assert d['checks']['overlap_method_matches_manifest'] is True; assert d['checks']['lineage_weighted_overlap_literal_overlap_disambiguated'] is True; assert d['checks']['invariance_record_digest_recomputed'] is True; assert d['checks']['topology_state_reabsorption_budget_matches_cycles'] is True; assert d['checks']['transported_node_ids_do_not_collide_with_fixture'] is True; assert len(d['control_rows']) == 6; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID3' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 6; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': d['acceptance']['derived_id_ceiling'], 'support_overlap_min': d['invariance_record']['support_overlap_min'], 'lineage_current_overlap_min': d['invariance_record']['lineage_current_overlap_min'], 'native': d['acceptance']['native_support_status'], 'next': d['acceptance']['next_iteration'], 'controls': len(d['control_rows']), 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 43, 'checks_passed': True, 'ceiling': 'ID4', 'support_overlap_min': 0.96, 'lineage_current_overlap_min': 0.97, 'native': 'mixed_native_experiment_local', 'next': '6B_id4_topology_split_birth_invariance_stress', 'controls': 6, 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 6-B. ID4 Split/Birth Topology Invariance Stress

Status: Complete.

- [x] Consume the minimum Iteration 6 ID4 invariance candidate.
- [x] Extend the lineage-proper-time sequence beyond the minimum Iteration 6
      window count.
- [x] Include a committed topology split event.
- [x] Include a lineage-authorized support birth event with explicit parent
      lineage.
- [x] Verify all topology events are committed before lineage/current support
      evaluation.
- [x] Verify all lineage maps are complete and not scrambled.
- [x] Verify topology-state reabsorption records exist for split and birth
      events.
- [x] Verify post-birth support remains lineage-current for multiple cycles.
- [x] Verify support overlap and lineage-current overlap remain above the
      manifest-declared thresholds.
- [x] Verify overlap is declared as lineage-weighted and literal node-set
      overlap is serialized separately.
- [x] Verify stress record digest recomputes from its declared digest input.
- [x] Verify topology-state reabsorption budget fields match surrounding cycle
      budget fields for split and birth events.
- [x] Verify retired split node ids, split target node ids, and born node ids
      are structurally disjoint where required.
- [x] Verify transported split/birth node ids do not collide with original
      fixture node ids.
- [x] Verify every post-birth cycle includes the born support node.
- [x] Verify split/birth topology events are infrastructure context only, not
      identity acceptance, RC identity collapse, reproduction, agency, or
      native identity support.
- [x] Verify exact node-plus-packet budget and nonnegative state.
- [x] Run controls:
  - [x] `stale_node_id_replay`
  - [x] `lineage_map_scrambled`
  - [x] `missing_topology_state_reabsorption`
  - [x] `ambiguous_overlap`
  - [x] `support_drift_beyond_threshold`
  - [x] `direct_state_or_topology_rewrite`
  - [x] `budget_discontinuity`
  - [x] `identity_claim_promotion`
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json`
- [x] `reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md`

Acceptance statement:

```text
Iteration 6-B passes if the ID4 candidate remains lineage-current and
support-continuous across a longer topology-changing sequence with split and
lineage-authorized birth events. Birth is topology lineage only, not identity
acceptance or agency, and the ceiling remains ID4.
```

Implementation records:

- Runner:
  `scripts/run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py`
- Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py
```

Run result:

```json
{
  "status": "passed",
  "checks_passed": true,
  "validation_check_count": 46,
  "derived_id_ceiling": "ID4",
  "claim_ceiling": "invariant_basin_candidate_topology_stress_validated",
  "native_support_status": "mixed_native_experiment_local",
  "proper_time_window_count": 7,
  "topology_event_count": 2,
  "split_event_present": true,
  "birth_event_present": true,
  "birth_is_identity_acceptance": false,
  "support_overlap_min": 0.955,
  "lineage_current_overlap_min": 0.96,
  "support_overlap_threshold": 0.95,
  "lineage_current_overlap_threshold": 0.95,
  "native_policy_blockers": [
    "native_identity_invariance_policy_missing"
  ],
  "control_count": 8,
  "claim_flags_false": true,
  "next_iteration": "7_id5_reflexive_closure_candidate"
}
```

Artifact digests:

```json
{
  "checks_digest": "86c6f667991daf3e2aef1e3fb0949da371f9fa83b760e8dd9fb7a1ccf187e326",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "810cef61a746eda973131eba329ab4c8c7c0c901e795d50f3af9b203cf826073",
  "id4_stress_candidate_row_digest": "5ac0bc04b9094a1283d3b54c386bc55ce4f6822563e09c1a60e0bbdd37e2d4ac",
  "source_iteration_6_output_digest": "825fd98dc563663dc49aba00d63822cecfa22d38349004337b7f27b2adcb0116",
  "topology_stress_event_digest": "0e6218df4161c97ec78d625abcb244f32fa2250f49f822a620f78c5f3dcdd190",
  "topology_stress_record_digest": "b3d9052165ffeb1f6b631b7a34dc0c198ee2582556d3f8812dae9a4f8a053a53",
  "topology_stress_sequence_digest": "033da18b48153c3407d48b3d7c8eb81366c212830a116ee0e22c45496adc570c"
}
```

Generated file SHA-256:

```text
5833e359cc1635b92a9de6e6407f2bd085fd0e4afd2650dae4494f80e6150fff  outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json
e3c48faa7dfdcd35ddd4ecc4d7c2dddc45402f9c8dd581630ef0455e7d85cd17  reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md
e906cab3c91cc1b27c9f662ee0600d5443e18e66bc91f842b2e051f2badf13ef  scripts/run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 46; assert d['source_iteration_6_output']['status']=='passed'; assert d['id4_topology_stress_candidate_row']['derived_id_ceiling']=='ID4'; assert d['id4_topology_stress_candidate_row']['claim_ceiling']=='invariant_basin_candidate_topology_stress_validated'; assert d['topology_stress_record']['proper_time_window_count'] == 7; assert d['topology_stress_record']['topology_event_count'] == 2; assert d['topology_stress_record']['split_event_present'] is True; assert d['topology_stress_record']['birth_event_present'] is True; assert d['topology_stress_record']['birth_is_identity_acceptance'] is False; assert d['topology_stress_record']['support_overlap_min'] == 0.955; assert d['topology_stress_record']['lineage_current_overlap_min'] == 0.96; assert d['topology_stress_record']['native_policy_blocker']=='native_identity_invariance_policy_missing'; assert d['checks']['overlap_method_matches_manifest'] is True; assert d['checks']['lineage_weighted_overlap_literal_overlap_disambiguated'] is True; assert d['checks']['stress_record_digest_recomputed'] is True; assert d['checks']['topology_state_reabsorption_budget_matches_cycles'] is True; assert d['checks']['split_birth_node_id_disjointness'] is True; assert d['checks']['transported_node_ids_do_not_collide_with_fixture'] is True; assert d['checks']['post_birth_support_includes_born_nodes'] is True; assert len(d['control_rows']) == 8; assert all(c['status']=='blocked' and c['derived_id_ceiling']=='ID3' for c in d['control_rows']); assert len({c['primary_blocker'] for c in d['control_rows']}) == 8; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': d['acceptance']['derived_id_ceiling'], 'cycles': d['topology_stress_record']['proper_time_window_count'], 'topology_events': d['topology_stress_record']['topology_event_count'], 'support_overlap_min': d['topology_stress_record']['support_overlap_min'], 'lineage_current_overlap_min': d['topology_stress_record']['lineage_current_overlap_min'], 'birth_is_identity_acceptance': d['topology_stress_record']['birth_is_identity_acceptance'], 'native': d['acceptance']['native_support_status'], 'next': d['acceptance']['next_iteration'], 'controls': len(d['control_rows']), 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 46, 'checks_passed': True, 'ceiling': 'ID4', 'cycles': 7, 'topology_events': 2, 'support_overlap_min': 0.955, 'lineage_current_overlap_min': 0.96, 'birth_is_identity_acceptance': False, 'native': 'mixed_native_experiment_local', 'next': '7_id5_reflexive_closure_candidate', 'controls': 8, 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 7. ID5 Reflexive Closure And Proper-Time Persistence Boundary

Status: Passed.

- [x] Verify re-entry into the candidate basin maintains or strengthens
      artifact-visible experiment-local basin evidence.
- [x] Verify later cycles consume updated basin evidence from artifacts.
- [x] Run proper-time identity persistence evaluator if applicable.
- [x] Verify `candidate_identity_carrier_type == coherence_basin`.
- [x] Verify `surface_row`, `deformation_token`, `boundary_signal`, route
      selection, and movement traces are evidence-only if present.
- [x] Verify no runtime identity-acceptance event is emitted unless a native
      contract/policy id exists; otherwise fail with
      `unauthorized_identity_acceptance_event`.
- [x] Run controls:
  - [x] `no_reentry`
  - [x] `closure_not_consumed_by_later_cycle`
  - [x] `improper_proper_time_threshold`
  - [x] `failed_persistence`
  - [x] `unauthorized_identity_acceptance_event`
  - [x] `producer_mutation_boundary_violation`
  - [x] `agency_claim_promotion`
- [x] Verify all non-identity claim flags remain false.

Artifacts:

- [x] `outputs/n07_iteration_7_id5_reflexive_closure_persistence.json`
- [x] `reports/n07_iteration_7_id5_reflexive_closure_persistence.md`
- [x] `scripts/run_n07_iteration_7_id5_reflexive_closure_persistence.py`

Acceptance statement:

```text
Iteration 7 passes if re-entry into the basin maintains or strengthens
artifact-visible experiment-local basin evidence, the re-entry node lineage is
source-backed by the Iteration 6-B topology record, and any proper-time
identity persistence evaluation is source-backed. This may support an ID5
identity candidate boundary but still does not support agency, identity
acceptance, RC identity collapse, or native LGRC identity support.
```

Acceptance state:

```text
Achieved.
```

Implementation record:

```text
Iteration 7 consumes the Iteration 6-B ID4 topology stress candidate and emits
an experiment-local reflexive closure record. Re-entry coherence into the
lineage-current support basin is positive (`0.08`), basin evidence after
re-entry is stronger than before, and the later proper-time cycle consumes the
updated basin evidence digest. The re-entry route uses born node `32` and
parent node `30`, with node lineage sourced from the Iteration 6-B committed
birth topology event and lineage map. Proper-time identity persistence passes
over four evidence points against the manifest threshold of three.

The topology family under test is now `n07_T6_reflexive_closure`, and the
composite topology under test is
`n07_C1_recurrent_single_basin_identity_candidate`. The source context remains
the Iteration 6-B `n07_T5_lineage_current_invariance` result. Reflexive
closure measurements are explicitly marked as
`experiment_local_declared_probe_values`, `artifact_visible = true`, and
`native_runtime_observed = false`. The candidate carrier remains
`coherence_basin`, no identity-acceptance event is emitted, the producer
boundary is preserved, budget error remains `0.0`, and all claim flags remain
false.

This establishes `ID5` only:
`reflexively_self_maintaining_identity_candidate`. It does not establish ID6,
identity acceptance, RC identity collapse, agency, semantic choice, biological
identity, unrestricted identity, or native LGRC identity support. Native
reflexive-closure policy remains blocked by
`native_reflexive_closure_policy_missing`. The source-backed T6 evidence check
is intentionally separated into Iteration 7-B.
```

Run result:

```json
{
  "status": "passed",
  "checks": 42,
  "checks_passed": true,
  "ceiling": "ID5",
  "topology_family": "n07_T6_reflexive_closure",
  "composite_topology": "n07_C1_recurrent_single_basin_identity_candidate",
  "source_context_topology": "n07_T5_lineage_current_invariance",
  "reentry_coherence_into_support": 0.08,
  "reentry_source_node": 32,
  "reentry_target_node": 30,
  "proper_time_window_count": 4,
  "proper_time_persistence_threshold": 3,
  "later_cycle_consumed_updated_basin_evidence": true,
  "native_runtime_reflexive_closure_observed": false,
  "native": "mixed_native_experiment_local",
  "next": "7B_source_backed_t6_reflexive_closure",
  "controls": 7,
  "claims_false": true
}
```

Artifact digests:

```json
{
  "checks_digest": "964ba7adf04b75da8889590e2eb6f05656fce8bb75f8328f439f008cb372a137",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "b8f0d288826268cd4bb2ad55274aa12e92fdc0e9efe2111b1e2e8020b981fce1",
  "id5_candidate_row_digest": "1d9a5bca48662fbb927e66abfd3ee346a0adb512da5fbc0a9ae59f39417a6e2a",
  "proper_time_persistence_evaluation_digest": "045c6dcb159f5205413aaac393981bfd23ad5170f87b626e95474751f18a4b2d",
  "reentry_event_digest": "7014cc83a38bfb897de72455316e5598a59a5df9102322a0e32563ecb826329d",
  "reflexive_closure_record_digest": "1e7e20292a217c1a8549f08e7fea8cf45000f8a192acd16539400c6ace0d90f1",
  "source_iteration_6b_output_digest": "4afe80c667d17079a9cf6b1d7a70be3a37bd366e1b421706bd121c78db34a988"
}
```

Generated file SHA-256:

```text
59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e  outputs/n07_iteration_7_id5_reflexive_closure_persistence.json
a43304bbfafa5f7d5a1645f870716be3d1c93602c6f4916abe7a29a5c24d231b  reports/n07_iteration_7_id5_reflexive_closure_persistence.md
770badd0d0a987cb06c3dbfb824d706a370e75d46fe35e626360725701466684  scripts/run_n07_iteration_7_id5_reflexive_closure_persistence.py
```

Post-Iteration 7 manifest refresh:

Iteration 7 hardened the manifest reflexive-closure contract and added the
`n07_T6_reflexive_closure` topology family. Iterations 2 through 6-B were
regenerated before running Iteration 7. Detailed SHA provenance is kept in each
JSON artifact; the checklist records only the current Iteration 7 output,
report, and script hashes.

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_7_id5_reflexive_closure_persistence.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 42; c=d['id5_reflexive_closure_candidate_row']; assert c['derived_id_ceiling']=='ID5'; assert c['topology_family_id']=='n07_T6_reflexive_closure'; assert c['composite_topology_id']=='n07_C1_recurrent_single_basin_identity_candidate'; assert c['source_context_topology_family_id']=='n07_T5_lineage_current_invariance'; assert c['candidate_identity_carrier_type']=='coherence_basin'; assert d['reflexive_closure_record']['reentry_coherence_into_support'] == 0.08; assert d['reflexive_closure_record']['basin_evidence_after_reentry_strengthened'] is True; assert d['reflexive_closure_record']['later_cycle_consumed_updated_basin_evidence'] is True; assert d['reflexive_reentry_event']['reentry_node_lineage']['born_node_id'] == 32; assert d['reflexive_reentry_event']['reentry_node_lineage']['parent_node_id'] == 30; assert d['scope_limitations']['native_runtime_reflexive_closure_observed'] is False; assert d['proper_time_identity_persistence_evaluation']['persistence_passed'] is True; assert d['proper_time_identity_persistence_evaluation']['proper_time_window_count'] == 4; assert d['proper_time_identity_persistence_evaluation']['native_runtime_observed'] is False; assert d['reflexive_closure_record']['identity_acceptance_event_emitted'] is False; assert c['id5_is_not_id6'] is True; assert len(d['control_rows']) == 7; assert all(cn['status']=='blocked' and cn['derived_id_ceiling']=='ID4' for cn in d['control_rows']); assert len({cn['primary_blocker'] for cn in d['control_rows']}) == 7; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': d['acceptance']['derived_id_ceiling'], 'topology': c['topology_family_id'], 'composite': c['composite_topology_id'], 'source_context': c['source_context_topology_family_id'], 'native_runtime_observed': d['scope_limitations']['native_runtime_reflexive_closure_observed'], 'next': d['acceptance']['next_iteration'], 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 42, 'checks_passed': True, 'ceiling': 'ID5', 'topology': 'n07_T6_reflexive_closure', 'composite': 'n07_C1_recurrent_single_basin_identity_candidate', 'source_context': 'n07_T5_lineage_current_invariance', 'native_runtime_observed': False, 'next': '7B_source_backed_t6_reflexive_closure', 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 7-B. Source-Backed T6 Reflexive Closure

Status: Passed.

- [x] Consume the Iteration 6-B T5 lineage-current source context and
      Iteration 7 T6 design probe without running a new native policy.
- [x] Emit a source-backed T6 chain from serialized state rows and
      digest-linked experiment-local packet/producer records.
- [x] Verify re-entry is represented by source rows, not authored measurement
      values.
- [x] Verify the later cycle consumes the post-reentry basin evidence digest.
- [x] Verify later-cycle consumption is marked as artifact-chain construction,
      not independent runtime observation.
- [x] Verify packet records do not claim actual LGRC `step()` execution.
- [x] Verify node-31 core membership and allocation weights are recorded as
      experiment-local design policy over source-backed support nodes.
- [x] Verify T4 no-mutation baseline deferral is recorded as a limitation.
- [x] Verify proper-time persistence over a source-backed before/reentry/after
      sequence.
- [x] Verify the candidate remains `ID5`, not `ID6`.
- [x] Verify native runtime reflexive-closure support remains false.
- [x] Run controls:
  - [x] `no_reentry`
  - [x] `closure_not_consumed_by_later_cycle`
  - [x] `hidden_support_field`
  - [x] `improper_proper_time_threshold`
  - [x] `failed_persistence`
  - [x] `budget_discontinuity`
  - [x] `unauthorized_identity_acceptance_event`
  - [x] `producer_mutation_boundary_violation`
  - [x] `agency_claim_promotion`
- [x] Verify all non-identity claim flags remain false.

Artifacts:

- [x] `outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json`
- [x] `reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md`
- [x] `scripts/run_n07_iteration_7b_source_backed_t6_reflexive_closure.py`

Acceptance statement:

```text
Iteration 7-B passes if the T6 reflexive-closure chain can be reconstructed
from serialized state rows and digest-linked experiment-local packet/producer
records: pre-reentry basin evidence, re-entry packet application, post-reentry
strengthened basin evidence, later producer/cycle consumption of the updated
digest, and proper-time persistence across the sequence. Packet records do not
claim actual LGRC `step()` execution, core membership/allocation policy is
marked experiment-local, and T4 no-mutation recurrence remains deferred. This
supports a source-backed artifact-derived ID5 candidate only. It does not
support ID6 artifact-only closeout, native runtime reflexive closure, identity
acceptance, RC identity collapse, agency, semantic choice, biological identity,
or unrestricted identity.
```

Acceptance state:

```text
Achieved.
```

Implementation record:

```text
Iteration 7-B consumes the Iteration 6-B topology-stress source context and
the Iteration 7 reflexive-closure design probe, then rebuilds the reflexive
closure evidence from explicit source rows. The source-backed chain records
pre-reentry basin evidence, the re-entry packet event, post-reentry basin
evidence, a producer-linked later cycle, and the later state row that consumes
the updated post-reentry digest. The before/after basin mass is conserved at
`1.448`; basin evidence strengthens from `1.21632` to `1.25632`; the
re-entry packet is applied by experiment-local step-semantics simulation rather
than actual LGRC `step()` execution; and the node-plus-packet budget error
remains `0.0`.

The derived topology family is `n07_T6_reflexive_closure`, the composite
topology is `n07_C1_recurrent_single_basin_identity_candidate`, and the source
context remains `n07_T5_lineage_current_invariance`. The candidate carrier
remains `coherence_basin`. The stricter row closes the prior source-backing
gap by requiring measurements to be derived from source rows and by rejecting
hidden support fields, missing re-entry, later-cycle non-consumption, failed
persistence, budget discontinuity, unauthorized identity acceptance, producer
mutation, and agency promotion.

The 7-B review refinements are recorded directly in the artifact: scheduled
and processed packet records have `source_backed = false` with
`digest_chain_source_backed = true`, actual LGRC step processing is false,
node 31 core membership is an experiment-local design policy over source-backed
support nodes, allocation weights are experiment-local design policy, the later
cycle consumption check is artifact-chain digest linkage rather than
independent runtime observation, and T4 no-mutation recurrence remains deferred.

This establishes source-backed artifact-derived `ID5` evidence only. Native
runtime reflexive-closure support remains false and the next step remains
Iteration 8 artifact-only replay and closeout.
```

Run result:

```json
{
  "status": "passed",
  "checks": 35,
  "checks_passed": true,
  "ceiling": "ID5",
  "topology_family": "n07_T6_reflexive_closure",
  "composite_topology": "n07_C1_recurrent_single_basin_identity_candidate",
  "source_context_topology": "n07_T5_lineage_current_invariance",
  "mass_before": 1.448,
  "mass_after": 1.448,
  "basin_score_before": 1.21632,
  "basin_score_after": 1.25632,
  "later_cycle_consumed_updated_basin_evidence": true,
  "all_measurements_derived_from_source_rows": true,
  "actual_lgrc_step_processed_packet": false,
  "experiment_local_packet_application": true,
  "core_membership_source_backed": false,
  "allocation_policy_origin": "experiment_local_design_probe",
  "later_cycle_consumption_independently_observed": false,
  "t4_no_mutation_baseline_deferred": true,
  "native_runtime_reflexive_closure_observed": false,
  "native": "mixed_native_experiment_local",
  "next": "8_id6_artifact_only_replay_and_closeout",
  "controls": 9,
  "claims_false": true
}
```

Artifact digests:

```json
{
  "checks_digest": "a456a32d333bd4be18280ee6a5eff590d1f2aaea7b05772e7d31f009df5eee4c",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "821a20660669e83b4ac6a8ae4a17f55a76abb0be9b0a8827b4d5daef6df3b9f9",
  "id5_candidate_row_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
  "proper_time_persistence_evaluation_digest": "a8839b20c2bebff8baae6db5639bcd03ce6bb8822b6c446f83898c40276a050d",
  "source_backed_t6_chain_digest": "96cc04a82aeaed185ba540c1201911113b8af1c074bb24a79bc41fdffd0b381f",
  "source_backed_t6_record_digest": "7ac28f40a645fbb013d64816e4c88e6ee89f1124ac1cefcce9eacd40349e393d"
}
```

Generated file SHA-256:

```text
617bb86c85ccc4a653280237f51b8749ecda50670b3df2efa9afc01b39464b33  outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json
5da517fd853adfadc69b753c0cdb55c28867593a825a6100c64fc36661f228c0  reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md
7839517fafb5a170e9065819c54441903fde212746344a9be0d9fe522b50295b  scripts/run_n07_iteration_7b_source_backed_t6_reflexive_closure.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_7b_source_backed_t6_reflexive_closure.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 35; c=d['id5_source_backed_t6_candidate_row']; r=d['source_backed_t6_record']; assert c['derived_id_ceiling']=='ID5'; assert c['topology_family_id']=='n07_T6_reflexive_closure'; assert c['composite_topology_id']=='n07_C1_recurrent_single_basin_identity_candidate'; assert c['source_context_topology_family_id']=='n07_T5_lineage_current_invariance'; assert c['candidate_identity_carrier_type']=='coherence_basin'; assert r['all_measurements_derived_from_source_rows'] is True; assert r['later_cycle_consumed_updated_basin_evidence'] is True; assert r['actual_lgrc_step_processed_packet'] is False; assert r['experiment_local_packet_application'] is True; assert r['core_membership_source_backed'] is False; assert r['allocation_policy_origin']=='experiment_local_design_probe'; assert r['later_cycle_consumption_independently_observed'] is False; assert r['t4_no_mutation_baseline_deferred'] is True; assert d['proper_time_identity_persistence_evaluation']['persistence_passed'] is True; assert r['native_runtime_observed'] is False; assert len(d['control_rows']) == 9; assert len({cn['primary_blocker'] for cn in d['control_rows']}) == 9; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': d['acceptance']['derived_id_ceiling'], 'topology': c['topology_family_id'], 'composite': c['composite_topology_id'], 'source_context': c['source_context_topology_family_id'], 'native_runtime_observed': r['native_runtime_observed'], 'actual_lgrc_step': r['actual_lgrc_step_processed_packet'], 'next': d['acceptance']['next_iteration'], 'controls': len(d['control_rows']), 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 35, 'checks_passed': True, 'ceiling': 'ID5', 'topology': 'n07_T6_reflexive_closure', 'composite': 'n07_C1_recurrent_single_basin_identity_candidate', 'source_context': 'n07_T5_lineage_current_invariance', 'native_runtime_observed': False, 'actual_lgrc_step': False, 'next': '8_id6_artifact_only_replay_and_closeout', 'controls': 9, 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 8. C1/T6 Artifact-Only Replay And ID5 Closeout

Status: Passed.

- [x] Reconstruct the full identity chain from artifacts only:
  - [x] source packet/flux events
  - [x] support-area row
  - [x] stability evidence
  - [x] attractivity evidence
  - [x] invariance/lineage evidence
  - [x] reflexive closure evidence
  - [x] proper-time identity evaluation if used
  - [x] identity closeout row
- [x] Verify no private runtime state is used.
- [x] Verify all in-scope controls fail with distinct primary blockers.
- [x] Verify compatibility controls are explicitly recorded as deferred:
  - [x] `destructive_interference`
  - [x] `ambiguous_overlap`
  - [x] `wrong_basin`
- [x] Verify source artifacts and SHA-256 digests are recorded.
- [x] Verify budget, lineage, and support-area checks survive replay.
- [x] Verify claim flags remain separate from ID level.
- [x] Verify becoming-method fields are preserved:
  - [x] `becoming_class_status`
  - [x] `probe_role`
  - [x] `boundary_rung`
  - [x] `support_dependency_status`
  - [x] `withdrawal_test_status`
  - [x] `naturalization_rung`
  - [x] `activity_history_digest`
- [x] Verify probe-supported expression is not reported as native regime
      expression unless withdrawal/endogenous support evidence passes.
- [x] Verify artifact replay passes but ID6 is not claimed while C3/T7
      compatibility is deferred.
- [x] Record Iteration 9 C3/T7 compatibility handoff boundary.

Expected artifacts:

- [x] `outputs/n07_iteration_8_c1_t6_artifact_replay_closeout.json`
- [x] `reports/n07_iteration_8_c1_t6_artifact_replay_closeout.md`
- [x] `scripts/run_n07_iteration_8_c1_t6_artifact_replay_closeout.py`

Acceptance statement:

```text
Iteration 8 passes if N07 freezes the current source-backed C1/T6 single-basin
chain at ID5 with exact budget accounting, artifact-only replay,
claim-boundary evidence, and a clear Iteration 9 C3/T7 compatibility handoff.
Artifact replay may pass, but Iteration 8 must not claim ID6 because C3
compatibility is deferred. Identity evidence must not promote agency,
memory/trail, goal regulation, ACO, biology, personhood, or unrestricted
identity claims.
```

Acceptance state:

```text
Achieved.
```

Implementation record:

```text
Iteration 8 reconstructs the current source-backed C1/T6 single-basin identity
chain from exported artifacts only. The replay chain verifies ID1 support,
ID2 stability, ID3 attractivity stress, ID4 lineage-current invariance, and
ID5 source-backed T6 reflexive closure. All source row digests match their
recorded artifact digests, older summary source links match their file SHA and
row digests, Iteration 7-B embedded source outputs validate, T6 record digests
recompute, scheduler order is monotonic, and budget error remains `0.0`.

The closeout freezes the current ceiling at `ID5`. Artifact replay passes, but
C3/T7 compatibility remains `deferred_to_iteration_9_c3_t7`, so ID6 is not
claimed. Iteration 8 preserves the refined 7-B scope: state rows are
source-backed; packet/producers are digest-linked experiment-local
constructions; actual LGRC `step()` packet processing is not claimed; node 31
core membership and allocation weights remain experiment-local design policy;
and all claim flags remain false.

In-scope negative controls are replayed from their source artifacts, not
synthetically regenerated in Iteration 8. Their derived ceilings remain
source-specific: `missing_support_area` stays at `ID0`, stability controls stay
at `ID1`, attractivity controls stay at `ID2`, invariance controls stay at
`ID3`, and reflexive-closure controls stay at `ID4`. Compatibility controls
(`destructive_interference`, `ambiguous_overlap`, `wrong_basin`) are explicitly
deferred to Iteration 9 rather than silently treated as passed.

The closeout row now satisfies the frozen ID row schema: it records
`support_area_id`, `support_area_digest`, `runtime_family`,
`implementation_surface`, `native_policy_blockers`, `native_observables_used`,
and `experiment_local_observables_used`. Its `boundary_rung` is the frozen enum
value `recurrence_or_continuation`, not a new closeout-only label. Support-area
digest replay recomputes the manifest and ID1 support digests, links the T6
transported support digest to the Iteration 7-B lineage chain, and records the
full activity-history digest scope
`orientation -> observation -> classification -> probe -> withdrawal ->
naturalization -> integration`.
```

Run result:

```json
{
  "status": "passed",
  "checks": 34,
  "checks_passed": true,
  "artifact_only_replay_passed": true,
  "runtime_state_used": false,
  "private_runtime_state_used": false,
  "derived_id_ceiling": "ID5",
  "id6_claimed": false,
  "id6_blocker": "c3_t7_compatibility_not_yet_tested",
  "compatibility_status": "deferred_to_iteration_9_c3_t7",
  "control_rows": 15,
  "source_replayed_blocked_controls": 11,
  "next": "9_c3_t7_competing_basin_compatibility_fixture_design",
  "claims_false": true
}
```

Artifact digests:

```json
{
  "artifact_replay_chain_digest": "ce4dcb296fff85fc084314e7701637d81d31922b3f84ca0aa113fc0d91e8f88b",
  "checks_digest": "fbb57232652c7f852e1b25953d5c7343a4a19e08bb86bb50350d5cf743ef00cd",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "closeout_row_artifact_digest": "127b268a9df06b80286829e6face9ec747f0071973f16ac6e97f3d16a93b9804",
  "closeout_row_digest": "6a074e6680fb3f7e80f63cdc8ecfc92066d811a3a8cb32284bd9e7334ed8e1d7",
  "control_rows_digest": "fa34172aff876c394e71d3eea68e7db52a5dbb51b1adea876190d9951f1decbe"
}
```

Generated file SHA-256:

```text
3cb3da0aec3437971af8694abc4eb29c2e256374f4f69a8e6387cd746b1e594c  outputs/n07_iteration_8_c1_t6_artifact_replay_closeout.json
98aa0b1ce5b2d0fd671abde3d89038fb21f7abf1d45b5e6fcdae574af93530c2  reports/n07_iteration_8_c1_t6_artifact_replay_closeout.md
ca0f10ec5065146cb16454993203088f01bdf9b35b93b7d5401627f11801794b  scripts/run_n07_iteration_8_c1_t6_artifact_replay_closeout.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_8_c1_t6_artifact_replay_closeout.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_8_c1_t6_artifact_replay_closeout.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_8_c1_t6_artifact_replay_closeout.json'; d=json.load(open(p)); assert d['status']=='passed'; assert all(d['checks'].values()); assert len(d['checks']) == 34; a=d['acceptance']; c=d['c1_t6_closeout_row']; r=d['artifact_replay_chain']; assert a['artifact_only_replay_passed'] is True; assert a['runtime_state_used'] is False; assert a['private_runtime_state_used'] is False; assert a['derived_id_ceiling']=='ID5'; assert a['id6_claimed'] is False; assert a['compatibility_status']=='deferred_to_iteration_9_c3_t7'; assert c['artifact_replay_gate']=='pass'; assert c['compatibility_gate']=='blocked'; assert c['id6_not_claimed'] is True; assert c['boundary_rung']=='recurrence_or_continuation'; assert c['runtime_family']=='hybrid_lgrc9v3_experiment_local'; assert c['implementation_surface']=='artifact_only_validator'; required=d['source_outputs']['iteration_1']['id_ladder_schema']['row_required_fields']; assert not [f for f in required if f not in c]; assert c['activity_history_digest_scope']==d['source_manifest']['becoming_method_fields']['activity_history_digest_scope']; assert r['support_area_digest_replay']['manifest_support_area_digest_matches'] is True; assert r['support_area_digest_replay']['id1_support_area_digest_matches'] is True; assert r['support_area_digest_replay']['transported_t6_support_area_digest_linked'] is True; assert r['semantic_consistency']['semantic_consistency_passed'] is True; assert len(d['control_rows']) == 15; assert sum(1 for row in d['control_rows'] if row['status']=='blocked') == 11; assert sum(1 for row in d['control_rows'] if row['status']=='deferred') == 3; assert any(row['control_id']=='identity_threshold_missing' and row['status']=='schema_guard_declared' for row in d['control_rows']); assert all(row.get('source_control_replayed') is True for row in d['control_rows'] if row['status']=='blocked'); assert len({row['primary_blocker'] for row in d['control_rows']}) == 15; assert c['actual_lgrc_step_processed_packet'] is False; assert c['experiment_local_packet_application'] is True; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'checks_passed': all(d['checks'].values()), 'ceiling': a['derived_id_ceiling'], 'id6_claimed': a['id6_claimed'], 'controls': len(d['control_rows']), 'source_replayed_blocked_controls': sum(1 for row in d['control_rows'] if row.get('source_control_replayed') is True and row['status']=='blocked'), 'compatibility': a['compatibility_status'], 'next': a['next_iteration'], 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 34, 'checks_passed': True, 'ceiling': 'ID5', 'id6_claimed': False, 'controls': 15, 'source_replayed_blocked_controls': 11, 'compatibility': 'deferred_to_iteration_9_c3_t7', 'next': '9_c3_t7_competing_basin_compatibility_fixture_design', 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 9. C3/T7 Competing-Basin Compatibility Fixture Design

Status: Complete.

- [x] Add or activate a `n07_T7_compatibility` fixture family only after the
      Iteration 8 C1/T6 closeout is complete.
- [x] Define `n07_C3_competing_basin_compatibility_candidate`.
- [x] Declare A basin, B basin, shared neighborhood `U`, support areas,
      metric ids, lineage status, event keys, and budget surfaces.
- [x] Freeze compatibility metrics before running probes:
  - [x] A support retention near B
  - [x] B support retention near A, if measured
  - [x] destructive-interference score
  - [x] ambiguous-overlap score
  - [x] wrong-basin leakage score
  - [x] hidden-support rejection rule
- [x] Define gate-vector mapping for `compatibility`.
- [x] Define required C3/T7 row fields using the frozen ID row schema,
      including `support_area_id`, `support_area_digest`, `runtime_family`,
      `implementation_surface`, native/experiment-local observables, native
      policy blockers, and claim flags.
- [x] Define support-area digest replay inputs for both A and B basins; do not
      rely on support names or visual labels as evidence.
- [x] Define source-control replay requirements for 9-B and 9-C; controls must
      replay from probe artifacts with gate-specific derived ceilings.
- [x] Keep imported route, movement, oscillator, or topology evidence as
      evidence context only if present.
- [x] Verify no ID promotion occurs from fixture naming.

Expected artifacts:

- [x] `configs/n07_c3_t7_compatibility_fixture_v1.json`
- [x] `outputs/n07_iteration_9_c3_t7_compatibility_fixture_design.json`
- [x] `reports/n07_iteration_9_c3_t7_compatibility_fixture_design.md`

Acceptance statement:

```text
Iteration 9 passes if the C3/T7 competing-basin compatibility fixture is
declared with frozen metrics, explicit A/B basin support areas, a shared
neighborhood, budget surfaces, source-artifact requirements, and fail-closed
controls before any compatibility probe is run. The fixture must also declare
artifact-replay requirements, support-area digest replay inputs, and
source-control replay requirements. This iteration designs the compatibility
test only; it does not pass compatibility, artifact replay, ID6, identity
acceptance, RC identity collapse, agency, or semantic choice.
```

Acceptance state:

```text
Achieved.
```

Implementation record:

```text
Iteration 9 generated the C3/T7 compatibility fixture as a design-only
contract. It declares `n07_T7_compatibility`,
`n07_C3_competing_basin_compatibility_candidate`, A/B support-area rows,
the shared neighborhood `n07_U_shared_A_B_competing_basin_v1`, frozen
compatibility metrics, source-control replay requirements, artifact-only
replay requirements, and frozen ID row field requirements.

The frozen Iteration 2 manifest remains unchanged because prior artifacts pin
its SHA-256. Iteration 9 records T7 as a post-Iteration-8 fixture extension:
9-B must validate the one-window C3/T7 probe against
`configs/n07_c3_t7_compatibility_fixture_v1.json`, 9-B2 must stress that
one-window result, and 9-C must replay the short-window evidence plus
prolonged-stress blocker. The old manifest alone does not contain T7, and 9-C
must not treat this branch as persistent C3 compatibility.

Basin A is source-backed only for its imported C1/T6 support nodes and support
digest. Its C3 edge and port ids are explicitly marked as structural
re-expression for the compatibility fixture. Basin B is design-only in
Iteration 9 and must become source-backed in Iteration 9-B before it can be
used as compatibility evidence.

"Competing" is recorded as a structural compatibility condition, not as
goal-directed or agentic competition. A and B are competing because they share
or border the same local coherence/flux context `U`, where flux, support
evidence, attractor strength, or replay legibility can be captured by, leaked
into, or disturbed by either basin.

The fixture records six compatibility metrics before probes run:
`a_support_retention_near_b`, `b_support_retention_near_a`,
`destructive_interference_score`, `ambiguous_overlap_score`,
`wrong_basin_leakage_score`, and `hidden_support_rejection_rule`.

The fixture records six 9-B/9-C source-control requirements:
`destructive_interference`, `ambiguous_overlap`, `wrong_basin`,
`hidden_support_field`, `budget_discontinuity`, and
`support_drift_beyond_threshold`. Each is explicitly a compatibility-gate
control with `gate_specific_derived_id_ceiling = ID5`, so a failed C3
compatibility probe cannot erase the already closed C1/T6 ID5 chain.

No compatibility probe was run. Compatibility remains `not_measured`, artifact
replay remains not run, the N07 ceiling remains `ID5`, and ID6 is not claimed.
All claim flags remain false.
```

Run result:

```json
{
  "status": "passed",
  "checks": 12,
  "checks_passed": true,
  "fixture_checks": 31,
  "fixture_checks_passed": true,
  "fixture_path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_c3_t7_compatibility_fixture_v1.json",
  "derived_id_ceiling": "ID5",
  "id6_claimed": false,
  "compatibility_probe_run": false,
  "artifact_replay_passed": false,
  "next": "9B_c3_compatibility_interference_probe",
  "claims_false": true
}
```

Artifact digests:

```json
{
  "acceptance_digest": "d6513c6cb3a50e4bbb65853388c07ea03b442908f3f4586b49b3fa4b3f286866",
  "checks_digest": "02358d5daf1ac2b3bc6f146fc4dd6211d78c98081cf02c1d022295f18d88d3ec",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "fixture_checks_digest": "32b3b0123a956dc69bffee752c2e7fbd42bdbb44270120d24989e6e7a0ab0958",
  "fixture_digest": "d6a96b467f62a995dc212d3b0d0f0392939fabab65974c4edcec20675a2b0d7b"
}
```

Generated file SHA-256:

```text
9447a5d60c261db66e8bca4ccf8e47598b6668ae1b9ddc4a337857bf5f210e58  configs/n07_c3_t7_compatibility_fixture_v1.json
173d3a49fb4c6a0022d2e0560a60942527cfaaaf53cff53209926645fbfd5a14  outputs/n07_iteration_9_c3_t7_compatibility_fixture_design.json
0bf73a4d4c103cd8c7c5280b2760075941232d2bada8ddd8b73fe003c61e8749  reports/n07_iteration_9_c3_t7_compatibility_fixture_design.md
1fdf98125054f368ca0d8fa891b158b1fecf5f1b5dfa92377605dad2cf465396  scripts/run_n07_iteration_9_c3_t7_compatibility_fixture_design.py
```

Validation:

```bash
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_c3_t7_compatibility_fixture_v1.json
.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_9_c3_t7_compatibility_fixture_design.json
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9_c3_t7_compatibility_fixture_design.py
.venv/bin/python -c "import json; p='experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_9_c3_t7_compatibility_fixture_design.json'; d=json.load(open(p)); f=d['fixture']; a=d['acceptance']; assert d['status']=='passed'; assert all(d['checks'].values()); assert all(d['fixture_checks'].values()); assert len(d['checks']) == 12; assert len(d['fixture_checks']) == 31; assert f['schema']=='n07_c3_t7_compatibility_fixture_v1'; assert f['manifest_extension_policy']['manifest_remains_frozen'] is True; assert f['topology_family']['topology_family_id']=='n07_T7_compatibility'; assert f['topology_family']['manifest_extension_status']=='post_iteration_8_fixture_extension'; assert f['composite_topology']['composite_topology_id']=='n07_C3_competing_basin_compatibility_candidate'; assert f['composite_topology']['primitive_extension_requires_fixture_validation'] is True; assert f['source_iteration_7b_direct_artifact']['matches_iteration_8_embedded_7b'] is True; assert f['basins']['A']['source_status']=='source_backed_c1_t6_nodes_structurally_reexpressed_for_c3'; assert f['basins']['B']['source_backing_required_in_iteration_9b'] is True; assert set(f['basins'].keys()) == {'A','B'}; assert 'shared_neighborhood_U' in f['competition_semantics']['competition_axes']; assert 'agency' in f['competition_semantics']['not_meant_as']; assert set(f['artifact_replay_requirements']['support_area_digest_replay_required_for']) == {'A','B'}; assert f['source_control_replay_requirements']['synthetic_closeout_controls_allowed'] is False; assert f['source_control_replay_requirements']['gate_specific_ceilings_required'] is True; assert len(f['compatibility_metric_contract']['metrics']) == 6; assert any(m['metric_name']=='hidden_support_rejection_rule' and m['metric_formula']=='hidden_support_field_count == 0' for m in f['compatibility_metric_contract']['metrics']); assert len(f['control_requirements']) == 6; assert all(row['gate_specific_derived_id_ceiling']=='ID5' for row in f['control_requirements']); assert a['compatibility_probe_run'] is False; assert a['compatibility_passed'] is False; assert a['artifact_replay_passed'] is False; assert a['derived_id_ceiling']=='ID5'; assert a['id6_claimed'] is False; assert a['next_iteration']=='9B_c3_compatibility_interference_probe'; assert all(v is False for v in d['claim_flags'].values()); print({'status': d['status'], 'checks': len(d['checks']), 'fixture_checks': len(d['fixture_checks']), 'fixture': d['fixture_path'], 'ceiling': a['derived_id_ceiling'], 'id6_claimed': a['id6_claimed'], 'next': a['next_iteration'], 'claims_false': all(v is False for v in d['claim_flags'].values())})"
git status --short src
git diff --check -- experiments/2026-05-N07-rc-identity-attractor-invariance
```

Validation output:

```text
fixture_json_tool_passed
output_json_tool_passed
py_compile_passed
{'status': 'passed', 'checks': 12, 'fixture_checks': 31, 'fixture': 'experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_c3_t7_compatibility_fixture_v1.json', 'ceiling': 'ID5', 'id6_claimed': False, 'next': '9B_c3_compatibility_interference_probe', 'claims_false': True}
git status --short src = (no output)
git diff --check = passed
```

## Iteration 9-B. C3 Compatibility And Interference Probe

Status: Completed.

- [x] Run A-basin/B-basin/shared-`U` compatibility probe from the Iteration 9
      frozen fixture.
- [x] Verify candidate A remains coherent near candidate B, or record the
      strongest lower ceiling and primary blocker.
- [x] Verify candidate B remains coherent if B is in positive scope, or mark B
      as evidence context only.
- [x] Preserve exact node-plus-packet budget accounting.
- [x] Run controls with distinct primary blockers:
  - [x] `destructive_interference`
  - [x] `ambiguous_overlap`
  - [x] `wrong_basin`
  - [x] `hidden_support_field`
  - [x] `budget_discontinuity`
  - [x] `support_drift_beyond_threshold`
- [x] Record every control as a source probe/control row with a
      gate-specific `derived_id_ceiling`; do not synthesize 9-C blockers from
      checklist text.
- [x] Verify support-area digest replay for A basin and B basin source rows.
- [x] Verify semantic consistency: A/B support ids, shared neighborhood `U`,
      basin carrier kind, lineage status, compatibility metric ids, and budget
      surfaces remain stable across the probe.
- [x] Verify route choice, movement, oscillator context, and topology mutation
      do not become identity claims.
- [x] Verify all claim flags remain false.

Expected artifacts:

- [x] `outputs/n07_iteration_9b_c3_compatibility_interference_probe.json`
- [x] `reports/n07_iteration_9b_c3_compatibility_interference_probe.md`

Acceptance statement:

```text
Iteration 9-B passes if the C3 fixture produces source-backed compatibility
evidence showing whether a candidate coherence basin remains legible near
another basin under destructive-interference, ambiguous-overlap, wrong-basin,
hidden-support, support-drift, and budget controls. Control rows must be
artifact-backed and retain gate-specific ceilings. A positive result may
strengthen the N07 identity candidate, but it does not emit identity
acceptance, RC identity collapse, agency, semantic choice, biological identity,
personhood, or unrestricted identity claims.
```

Acceptance state: Achieved.

Implementation record:

- Added
  `scripts/run_n07_iteration_9b_c3_compatibility_interference_probe.py`.
- Generated source-backed A and B support rows from the frozen Iteration 9
  C3/T7 fixture, with shared neighborhood `U` serialized as probe evidence.
- Recorded six compatibility metrics:
  `a_support_retention_near_b = 0.952348066298`,
  `b_support_retention_near_a = 0.958333333333`,
  `destructive_interference_score = 0.047619047619`,
  `ambiguous_overlap_score = 0.0`,
  `wrong_basin_leakage_score = 0.04`, and
  `hidden_support_rejection_rule = 0`.
- Emitted six source control rows with distinct primary blockers:
  `destructive_interference`, `ambiguous_overlap`, `wrong_basin`,
  `hidden_support_field`, `budget_discontinuity`, and
  `support_drift_beyond_threshold`.
- Added an explicit interpretation record: 9-B is positive one-window C3/T7
  compatibility evidence showing A and B retain distinct support areas in the
  serialized shared-`U` probe window without destructive interference,
  ambiguous overlap, wrong-basin capture, hidden support fields, or budget
  drift.
- Recorded scope limitation: 9-B runs `0` dynamic LGRC steps and `1` serialized
  compatibility probe window. Prolonged A/B/shared-`U` behavior is
  `not_tested` and must not be inferred from 9-B.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false` because
  Iteration 9-C artifact-only replay is still pending.
- Preserved all claim flags as `false`; route choice, movement, oscillator
  context, and topology mutation remain evidence context only.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9b_c3_compatibility_interference_probe.py
{"checks": 33, "status": "passed"}
outputs/n07_iteration_9b_c3_compatibility_interference_probe.json
reports/n07_iteration_9b_c3_compatibility_interference_probe.md
```

Artifact hashes:

```text
0577bdfd702c0a4d057c45d507757b755f80280b725501de8aeb8a8367adb3cd  scripts/run_n07_iteration_9b_c3_compatibility_interference_probe.py
814eb489c9fddd884c6a3642bfb5d247b1cb8662db7c97daf1214cb2cd34fef3  outputs/n07_iteration_9b_c3_compatibility_interference_probe.json
cabeec9503dbb01a00aec3cff320a9a4af7a79ea7becb176e2baa68db8e77de7  reports/n07_iteration_9b_c3_compatibility_interference_probe.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9b_c3_compatibility_interference_probe.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_9b_c3_compatibility_interference_probe.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 33, 'controls': 6, 'ceiling': 'ID5', 'id6_claimed': False}

git status --short src
(no output)
```

## Iteration 9-B2. C3 Compatibility Prolonged Stress

Status: Completed.

- [x] Prolong the 9-B compatibility boundary beyond one serialized probe
      window.
- [x] Treat the 9-B `wrong_basin_leakage_score = 0.04` as a stability risk,
      not as negligible background noise.
- [x] Run a repeated-window no-recovery stress model over the source-backed
      9-B support-retention and wrong-basin leakage measurements.
- [x] Record the first stress-window failure and primary blocker.
- [x] Preserve exact node-plus-packet budget accounting in the stress model.
- [x] Keep the result explicitly experiment-local; do not call it native LGRC
      dynamic persistence.
- [x] Preserve `derived_id_ceiling = ID5`; do not claim ID6.
- [x] Preserve all claim flags as `false`.

Expected artifacts:

- [x] `outputs/n07_iteration_9b2_c3_compatibility_prolonged_stress.json`
- [x] `reports/n07_iteration_9b2_c3_compatibility_prolonged_stress.md`

Acceptance statement:

```text
Iteration 9-B2 passes if it explicitly tests prolonged compatibility under a
serialized stress model, records whether the 9-B leakage/support-loss boundary
remains stable, and does not promote ID6 or identity claims.
```

Acceptance state: Achieved.

Implementation record:

- Added
  `scripts/run_n07_iteration_9b2_c3_compatibility_prolonged_stress.py`.
- Ran a 12-window repeated compatibility stress model over the source-backed
  9-B metrics.
- Recorded model scope as
  `experiment_local_repeated_window_stress_not_native_lgrc_dynamics`; dynamic
  LGRC step count remains `0`.
- First failure occurs at stress window `3`, with
  `primary_blockers = ["wrong_basin"]`.
- At first failure:
  `A_cumulative_support_retention = 0.8637481156814181`,
  `B_cumulative_support_retention = 0.8801359953694519`,
  `cumulative_wrong_basin_leakage_score = 0.12`, and
  `cumulative_destructive_interference_score = 0.13625188431858193`.
- Later stress windows additionally trip
  `destructive_interference` and `support_drift_beyond_threshold`.
- Interpretation: 9-B is one-window compatibility evidence only. Under a
  no-recovery prolonged stress model, the 4% one-window wrong-basin leakage is
  enough to block persistent C3 compatibility before the 12-window horizon.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Preserved all claim flags as `false`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9b2_c3_compatibility_prolonged_stress.py
{"checks": 17, "first_failure_window": 3, "primary_blockers": ["wrong_basin"], "status": "passed"}
outputs/n07_iteration_9b2_c3_compatibility_prolonged_stress.json
reports/n07_iteration_9b2_c3_compatibility_prolonged_stress.md
```

Artifact hashes:

```text
09442e8860455241c091452120f3a8c329db801a21b079d7c0f81f5889a01a94  scripts/run_n07_iteration_9b2_c3_compatibility_prolonged_stress.py
2ca5bde6c2bfc3d12fd5be976e66f53da5a1ac1133f182749d96368331861c7e  outputs/n07_iteration_9b2_c3_compatibility_prolonged_stress.json
46bcabd67fe70b268ae3c2e680990569cf99fa5c06b1681a1af582e9c9171600  reports/n07_iteration_9b2_c3_compatibility_prolonged_stress.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9b2_c3_compatibility_prolonged_stress.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_9b2_c3_compatibility_prolonged_stress.json
json_tool_passed
```

## Iteration 9-C. Short-Window Artifact Replay And Evidence Closeout

Status: Completed.

- [x] Reconstruct the short-window N07 evidence chain from artifacts only:
  - [x] Iteration 1-2 baseline/schema/fixture inventory
  - [x] Iteration 3-8 single-basin support/stability/attractivity/
        invariance/reflexive-closure evidence
  - [x] A basin support row
  - [x] B basin support row
  - [x] shared-neighborhood evidence
  - [x] compatibility/interference measurements
  - [x] prolonged compatibility stress boundary from 9-B2
  - [x] controls and blockers
  - [x] budget and lineage records
  - [x] closeout row
- [x] Verify no private runtime state is used.
- [x] Verify controls replay from 9-B source artifacts and fail with distinct
      primary blockers.
- [x] Verify control ceilings remain source-specific rather than collapsed into
      one closeout ceiling.
- [x] Verify A/B support-area digests recompute from declared digest inputs.
- [x] Verify closeout row includes all frozen ID row required fields.
- [x] Verify `boundary_rung` uses a frozen enum value.
- [x] Verify semantic consistency across support, stability, attractivity,
      invariance, reflexive closure, compatibility, artifact replay, and
      claim-boundary fields.
- [x] Verify compatibility is either passed, failed, or explicitly blocked with
      source-backed rationale.
- [x] Account for the 9-B2 prolonged-stress blocker before any ID6 statement;
      if unresolved, close C3 as one-window compatibility evidence plus
      prolonged-stress failure, not persistent compatibility.
- [x] Freeze the post-9-C N07 ceiling and long-horizon Iteration 10+ handoff.

Expected artifacts:

- [x] `outputs/n07_iteration_9c_short_window_evidence_closeout.json`
- [x] `reports/n07_iteration_9c_short_window_evidence_closeout.md`

Acceptance statement:

```text
Iteration 9-C passes if the N07 short-window evidence chain through Iteration
9-B2 can be replayed from artifacts only and the N07 ceiling is updated without
claim promotion. It must record Iteration 9-B as one-window compatibility
evidence and Iteration 9-B2 as prolonged-stress failure. It must not close C3
as persistent compatibility, must not claim ID6, and must not report identity
acceptance, RC identity collapse, agency, semantic choice, biological identity,
personhood, or unrestricted identity.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n07_iteration_9c_short_window_evidence_closeout.py`.
- Replayed the N07 short-window evidence chain from exported artifacts only:
  Iterations 1-2 baseline/schema/fixture inventory, Iterations 3-8
  single-basin support/stability/attractivity/invariance/reflexive-closure
  evidence, Iteration 9 C3/T7 fixture design, Iteration 9-B one-window
  compatibility evidence, and Iteration 9-B2 prolonged-stress boundary.
- Recomputed A and B support-area digests from declared 9-B digest inputs.
- Recomputed 9-B metric, compatibility, and control record digests.
- Recomputed 9-B2 stress-model and stress-window digests.
- Emitted `n07_i9c_short_window_evidence_closeout_row_v1` with the frozen ID
  row schema fields.
- Recorded artifact replay as `pass`, one-window compatibility as `pass`,
  prolonged compatibility as `blocked`, and `primary_blocker = wrong_basin`.
- Froze `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Set next iteration to `10_long_horizon_compatibility_design`.
- Preserved all claim flags as `false`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9c_short_window_evidence_closeout.py
{"ceiling": "ID5", "checks": 34, "id6_claimed": false, "next": "10_long_horizon_compatibility_design", "primary_blocker": "wrong_basin", "status": "passed"}
outputs/n07_iteration_9c_short_window_evidence_closeout.json
reports/n07_iteration_9c_short_window_evidence_closeout.md
```

Artifact hashes:

```text
ee44e57a25e0e87e1b898730f97101279666fca2fa117bc95dc93d2eeb7fd9bc  scripts/run_n07_iteration_9c_short_window_evidence_closeout.py
75e045c676a7c0232f62bafaacdfd6beacd7317c29b7e7699de6b3b94456e548  outputs/n07_iteration_9c_short_window_evidence_closeout.json
e52bdc404ff996e0cf6a6ede8d83ce93dede0923bbe7799a7d5431c392e52d75  reports/n07_iteration_9c_short_window_evidence_closeout.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_9c_short_window_evidence_closeout.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_9c_short_window_evidence_closeout.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 34, 'ceiling': 'ID5', 'id6_claimed': False, 'primary_blocker': 'wrong_basin', 'next': '10_long_horizon_compatibility_design'}
```

## Iteration 10. Long-Horizon Compatibility Design

Status: Completed.

- [x] Reuse the Iteration 9-B and 9-B2 evidence to define survivability
      criteria before new probes.
- [x] Freeze the stress horizon, support-retention threshold, wrong-basin
      leakage budget, destructive-interference threshold, and budget
      continuity criteria.
- [x] Freeze a change-function / trajectory contract so Iteration 11 records
      leakage, support-retention, interference, and budget trends rather than
      only a fixed-horizon true/false endpoint.
- [x] Define candidate recovery/re-separation mechanisms that could prevent
      repeated-window leakage accumulation.
- [x] Define which existing N07 evidence can be reused directly and which must
      be rerun under long-horizon conditions.
- [x] Preserve claim boundaries: no ID6, identity acceptance, RC identity
      collapse, agency, semantic choice, biological identity, personhood, or
      unrestricted identity claims.

Expected artifacts:

- [x] `outputs/n07_iteration_10_long_horizon_compatibility_design.json`
- [x] `reports/n07_iteration_10_long_horizon_compatibility_design.md`

Acceptance statement:

```text
Iteration 10 passes if it freezes a long-horizon compatibility design contract
that directly addresses the 9-B2 wrong-basin prolonged-stress failure. It must
define survivability criteria and recovery/re-separation hypotheses before any
new long-horizon probe is interpreted as identity evidence. The design must
also record that endpoint pass/fail is a claim gate, while trajectory regime is
the evidence interpretation.
```

Acceptance state: Achieved.

Implementation record:

- Added `scripts/run_n07_iteration_10_long_horizon_compatibility_design.py`.
- Consumed Iteration 9-B, 9-B2, and 9-C as source artifacts.
- Froze the source boundary:
  `current_ceiling = ID5`, `current_primary_blocker = wrong_basin`, one-window
  `wrong_basin_leakage_score = 0.04`, and 9-B2 first failure at stress window
  `3`.
- Froze a 12-window survivability contract with:
  `A_support_retention_min_each_window = 0.85`,
  `B_support_retention_min_each_window = 0.85`,
  `cumulative_wrong_basin_leakage_max_each_window = 0.1`,
  `net_unresolved_wrong_basin_leakage_budget_per_window =
  0.008333333333333333`,
  `destructive_interference_score_max_each_window = 0.15`,
  `ambiguous_overlap_score_max = 0.2`, `node_plus_packet_budget_error_max =
  0.0`, and `hidden_support_field_count = 0`.
- Added `n07_long_horizon_compatibility_change_function_v1`, which records the
  fixed horizon as a measurement frame rather than the result itself. The
  contract requires Iteration 11 to emit per-window metric series, first
  differences, slopes, endpoint status, first failure window, trajectory
  regime, and trajectory interpretation.
- Classified the 9-B2 source trend as
  `unbounded_degrading_without_recovery`: wrong-basin leakage increases by
  `0.04` per window, A support retention slopes by
  `-0.03597648527676473` per window, B support retention slopes by
  `-0.03256974356768539` per window, and destructive interference slopes by
  `0.03597648527676473` per window.
- Recorded the Arc-of-Becoming alignment by paper title:
  `Classification of Becoming`, `Cultivation of Becoming`, and
  `Naturalization of Becoming`. The record states that the probe should first
  classify the expressed compatibility regime and then use endpoint pass/fail
  only as a claim boundary.
- Declared three recovery/re-separation hypotheses:
  `source_digest_reentry_buffer_v1`, `neutral_absorber_reservoir_v1`, and
  `symmetric_dual_reentry_v1`.
- Declared the Iteration 11 lanes:
  `baseline_no_recovery_replay`, `source_digest_reentry_buffer`,
  `neutral_absorber_reservoir`, and optional `symmetric_dual_reentry`.
- Reframed Iteration 11 as an `11-*` long-horizon C3 classification learning
  series. Branches such as 11-A, 11-B, and later 11-* are allowed while they
  expose new trajectory regimes, blockers, or recovery/re-separation
  mechanisms. Iteration 12 is therefore a closeout after the 11-* series, not a
  mandatory closeout after one branch.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Preserved all claim flags as `false`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_10_long_horizon_compatibility_design.py
{"ceiling": "ID5", "checks": 31, "horizon": 12, "id6_claimed": false, "next": "11_long_horizon_compatibility_recovery_probe", "status": "passed"}
outputs/n07_iteration_10_long_horizon_compatibility_design.json
reports/n07_iteration_10_long_horizon_compatibility_design.md
```

Artifact hashes:

```text
0297a74aa6a0da962cc6eb4fa9c1f2dee676c385d6ed01c0ce6d37fb6ae92456  scripts/run_n07_iteration_10_long_horizon_compatibility_design.py
e226de77cfc29d7f88ad39b92ed19bdb2c383842ee93b4b9114a46df0db14ee2  outputs/n07_iteration_10_long_horizon_compatibility_design.json
1385850e55705d9b6c075ccee3c1c3356b5e826449e43229b7b1fa647ecfd89a  reports/n07_iteration_10_long_horizon_compatibility_design.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_10_long_horizon_compatibility_design.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_10_long_horizon_compatibility_design.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 31, 'horizon': 12, 'ceiling': 'ID5', 'id6_claimed': False, 'trajectory_contract': 'n07_long_horizon_compatibility_change_function_v1', 'series_scope': '11_star_long_horizon_c3_classification_learning_series', 'branch_continuation_allowed': True, 'iteration_12_after_series': True, 'next': '11_long_horizon_compatibility_recovery_probe'}

N07 artifact sweep:
{'artifact_count': 16, 'total_checks': 513, 'failed': []}
```

## Iteration 11*. Long-Horizon Compatibility Recovery Learning Series

Status: Active. Branches 11-0, 11-A, and 11-B completed; Iteration 12 is the
next closeout/replay step.

- [x] Run the Iteration 10 long-horizon fixture/probe as the first 11-* branch.
- [x] Measure whether wrong-basin leakage, destructive interference, support
      drift, and budget drift remain bounded across the declared stress
      horizon for 11-0.
- [x] Emit trajectory evidence for 11-0: per-window metric series, first
      differences, second differences, metric slopes, endpoint status, first
      failure window, trajectory regime, and trajectory interpretation.
- [x] For 11-0, record the question answered, mechanism or fixture change,
      what was learned, next question, endpoint status, trajectory regime, and
      claim flags.
- [x] Continue with 11-A because 11-0 exposed an
      `unbounded_degrading_without_recovery` trajectory and a source-digest
      reentry buffer was the next specified recovery mechanism to test.
- [x] Continue with 11-B and later 11-* branches while the branch exposes a new
      long-term C3 basin regime, blocker, or recovery/re-separation mechanism.
- [x] Stop the 11-* series only when the branch results are repetitive, blocked
      by the same unresolved missing mechanism, or sufficient to define the
      current long-term C3 class for Iteration 12 replay.
- [x] Verify the 11-0 no-recovery baseline is source-backed and serialized, not
      report-side interpretation.
- [x] Record first failure window and distinct primary blocker for 11-0.
- [x] Preserve claim boundaries and keep all claim flags false.

Expected artifacts for 11-0:

- [x] `outputs/n07_iteration_11_long_horizon_compatibility_recovery_probe.json`
- [x] `reports/n07_iteration_11_long_horizon_compatibility_recovery_probe.md`

Expected artifacts for 11-A:

- [x] `outputs/n07_iteration_11a_source_digest_reentry_buffer.json`
- [x] `reports/n07_iteration_11a_source_digest_reentry_buffer.md`

Expected artifacts for 11-B:

- [x] `outputs/n07_iteration_11b_neutral_absorber_reservoir.json`
- [x] `reports/n07_iteration_11b_neutral_absorber_reservoir.md`

11-* branch acceptance:

```text
Each 11-* branch passes if it records a source-backed question/answer pair with
endpoint status, trajectory regime, trend metrics, controls, and claim flags.
The 11-* series is ready for Iteration 12 only when the branch record is
sufficient to classify the current long-term C3 basin compatibility regime or
when a repeated blocker is explicitly recorded as the stop condition.
```

11-0 implementation record:

- Added `scripts/run_n07_iteration_11_long_horizon_compatibility_recovery_probe.py`.
- Consumed Iteration 9-B2 and Iteration 10 as source artifacts.
- Replayed the no-recovery baseline through the Iteration 10 change-function
  contract.
- Classified the 11-0 trajectory as
  `unbounded_degrading_without_recovery`.
- Added an explicit Arc-of-Becoming interpretation record with question,
  observations, expressed property, classification, cultivation next question,
  naturalization status, and claim boundary.
- Classified the expressed property as:
  `Repeated no-recovery C3 pressure expresses an unbounded degrading
  compatibility regime.`
- Classified the branch as `reusable_negative_class`, not merely a failed
  endpoint.
- Recorded naturalization as `Nat0_probe_dependent_expression`; no
  self-regenerated support or recovery mechanism was observed in 11-0.
- Recorded endpoint status `blocked`, first failure window `3`, and primary
  blocker `wrong_basin`.
- Recorded trend slopes:
  `wrong_basin_leakage_level_slope_per_window = 0.04`,
  `A_support_retention_level_slope_per_window = -0.03597648527676473`,
  `B_support_retention_level_slope_per_window = -0.03256974356768539`,
  `destructive_interference_level_slope_per_window = 0.03597648527676473`,
  and `budget_error_level_slope_per_window = 0.0`.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Preserved all claim flags as `false`.
- Recorded `series_ready_for_iteration_12 = false`.
- Recorded next branch:
  `11-A_source_digest_reentry_buffer`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11_long_horizon_compatibility_recovery_probe.py
{"branch": "11-0", "checks": 35, "endpoint": "blocked", "id6_claimed": false, "next": "11-A_source_digest_reentry_buffer", "status": "passed", "trajectory_regime": "unbounded_degrading_without_recovery"}
outputs/n07_iteration_11_long_horizon_compatibility_recovery_probe.json
reports/n07_iteration_11_long_horizon_compatibility_recovery_probe.md
```

Artifact hashes:

```text
f34441346cd60f4056a8e3691f5e9350eea7ce133204d80f2891414192d70c79  scripts/run_n07_iteration_11_long_horizon_compatibility_recovery_probe.py
976cf7dea0d0feb131697a5b439c3f297d9c1bf3515fd5521a3ed93a95d14811  outputs/n07_iteration_11_long_horizon_compatibility_recovery_probe.json
950a0627b7d244c5539024af60ede3c07a002e99c95c6776ba205380bc95a685  reports/n07_iteration_11_long_horizon_compatibility_recovery_probe.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11_long_horizon_compatibility_recovery_probe.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_11_long_horizon_compatibility_recovery_probe.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 35, 'branch': '11-0', 'endpoint': 'blocked', 'first_failure': 3, 'primary_blocker': 'wrong_basin', 'trajectory_regime': 'unbounded_degrading_without_recovery', 'arc_style': 'question_observation_classification_cultivation_naturalization', 'observations': 4, 'classification': 'reusable_negative_class', 'naturalization': 'Nat0_probe_dependent_expression', 'series_ready_for_12': False, 'next': '11-A_source_digest_reentry_buffer', 'id6_claimed': False, 'claim_flags_false': True}

N07 artifact sweep:
{'artifact_count': 17, 'total_checks': 548, 'failed': []}
```

11-A intro:

```text
Can source_digest_reentry_buffer_v1 convert the 11-0 trajectory from
unbounded_degrading_without_recovery into bounded-flat, bounded-improving,
or oscillatory-recovering compatibility?
```

11-A implementation record:

- Added `scripts/run_n07_iteration_11a_source_digest_reentry_buffer.py`.
- Consumed Iteration 7-B, 9-B, 10, and 11-0 as source artifacts.
- Used `source_digest_reentry_buffer_v1` with a serialized capture fraction
  `0.8`. The frozen Iteration 10 leakage budget required at least
  `0.7916666666666667`, so the policy meets the declared threshold without
  hidden routing.
- Emitted the full source-backed reentry chain for each window:
  `leakage_event -> neutral_buffer_state -> source_digest_reentry_event ->
  post_reentry_support_measurement`.
- 11-A changed the expressed regime from
  `unbounded_degrading_without_recovery` to `bounded_degrading`.
- The fixed 12-window endpoint passed, but the trend remains degrading:
  `wrong_basin_leakage_level_slope_per_window = 0.007999999999999998`,
  `A_support_retention_level_slope_per_window = -0.009002364041475657`,
  `B_support_retention_level_slope_per_window = -0.007928026592438813`, and
  `destructive_interference_level_slope_per_window = 0.009002364041475657`.
- Recorded the Arc-of-Becoming classification as
  `reusable_partial_recovery_class`: endpoint survival is real improvement but
  not stable long-term compatibility.
- Recorded naturalization as `Nat2_regime_assisted_expression`; the recovery
  is serialized and regime-assisted, not native endogenous recovery.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Preserved all claim flags as `false`.
- Recorded `series_ready_for_iteration_12 = false`.
- Recorded next branch:
  `11-B_neutral_absorber_reservoir`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11a_source_digest_reentry_buffer.py
{"branch": "11-A", "checks": 32, "endpoint": "passed_12_window_horizon", "id6_claimed": false, "next": "11-B_neutral_absorber_reservoir", "status": "passed", "trajectory_regime": "bounded_degrading", "wrong_basin_slope": 0.007999999999999998}
outputs/n07_iteration_11a_source_digest_reentry_buffer.json
reports/n07_iteration_11a_source_digest_reentry_buffer.md
```

Artifact hashes:

```text
bf059850ccf7ca68216de8a55e85cf402c48077919251b8e2503a1e513d61a07  scripts/run_n07_iteration_11a_source_digest_reentry_buffer.py
1cc5a3e3ccb0770ef758f68e5ee1dc9cf5f4f6e530f214220bc98b3539564dce  outputs/n07_iteration_11a_source_digest_reentry_buffer.json
96ecad412bb6ce399f4a843c6a282d34a9b4c4a179d70a7f9f5b8969979600b7  reports/n07_iteration_11a_source_digest_reentry_buffer.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11a_source_digest_reentry_buffer.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_11a_source_digest_reentry_buffer.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 32, 'branch': '11-A', 'endpoint': 'passed_12_window_horizon', 'trajectory_regime': 'bounded_degrading', 'wrong_basin_slope': 0.007999999999999998, 'classification': 'reusable_partial_recovery_class', 'naturalization': 'Nat2_regime_assisted_expression', 'series_ready_for_12': False, 'next': '11-B_neutral_absorber_reservoir', 'id6_claimed': False, 'claim_flags_false': True}

N07 artifact sweep:
{'artifact_count': 18, 'total_checks': 580, 'failed': []}
```

11-B intro and C3 redirection:

```text
For connected basins, no-leakage is not the natural C3 target. The better
question is whether leakage becomes bounded, non-destructive exchange that
does not erase either basin.

11-A is therefore incomplete not because leakage existed, but because support,
leakage, and destructive-interference trends still degraded.

Can neutral_absorber_reservoir_v1 turn connected-basin leakage into bounded
non-destructive exchange while both basins remain separable attractors?
```

11-B implementation record:

- Added `scripts/run_n07_iteration_11b_neutral_absorber_reservoir.py`.
- Consumed Iteration 7-B, 9-B, 10, 11-0, and 11-A as source artifacts.
- Reframed the 11-* C3 target from sealed/no-leakage basins to bounded
  non-destructive exchange between connected basins.
- Used `neutral_absorber_reservoir_v1` with serialized exchange cap `0.075`,
  reservoir settling factor `0.65`, neutral absorption fraction `0.85`,
  post-transient flattening epsilon `0.001`, and explicit
  `zero_leakage_required = false`.
- Emitted the full per-window reservoir chain:
  `connected_basin_exchange_event -> neutral_absorber_reservoir_state ->
  non_destructive_exchange_measurement`.
- Classified the 11-B trajectory as `bounded_non_destructive_exchange`.
- The fixed 12-window endpoint passed with nonzero leakage. Leakage plateaued
  after the transient rather than accumulating linearly:
  `wrong_basin_leakage_level_slope_per_window = 0.00439303630184246`,
  `wrong_basin_leakage_level_post_transient_slope_per_window =
  0.0008716360195236764`.
- Final 11-B measurements improved over 11-A while preserving the connected
  basin interpretation:
  `final_wrong_basin_leakage = 0.07457339932026706`,
  `final_A_support_retention = 0.9731535762447039`,
  `final_B_support_retention = 0.9753907782243119`,
  `final_destructive_interference = 0.02684642375529611`, and
  `final_basin_separability = 0.9731535762447039`.
- Recorded the Arc-of-Becoming classification as
  `reusable_dual_basin_exchange_class`: the expressed property is bounded
  non-destructive exchange, not zero leakage.
- Recorded naturalization as `Nat2_regime_assisted_expression`; the absorber is
  still serialized/experiment-local, not endogenously formed by native LGRC.
- Preserved `derived_id_ceiling = ID5`; `id6_claimed = false`.
- Preserved all claim flags as `false`.
- Recorded `series_ready_for_iteration_12 = true`.
- Recorded next branch:
  `12_long_horizon_artifact_replay_and_compatibility_closeout`.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11b_neutral_absorber_reservoir.py
{"branch": "11-B", "checks": 35, "endpoint": "passed_12_window_horizon", "id6_claimed": false, "next": "12_long_horizon_artifact_replay_and_compatibility_closeout", "status": "passed", "trajectory_regime": "bounded_non_destructive_exchange", "wrong_basin_post_transient_slope": 0.0008716360195236764, "wrong_basin_slope": 0.00439303630184246}
outputs/n07_iteration_11b_neutral_absorber_reservoir.json
reports/n07_iteration_11b_neutral_absorber_reservoir.md
```

Artifact hashes:

```text
5237d2940d25ae408000f0a57f1ceba74f928391251da4d1dc87e91e6c0a2319  scripts/run_n07_iteration_11b_neutral_absorber_reservoir.py
0a45dfa122bc2f727501208ed3731444907060f67c79a3ea56921e71f1b2a497  outputs/n07_iteration_11b_neutral_absorber_reservoir.json
866f767ca4b098b46aad4f5833f9644092eaa028bb9e4c742763fe612b238354  reports/n07_iteration_11b_neutral_absorber_reservoir.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_11b_neutral_absorber_reservoir.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_11b_neutral_absorber_reservoir.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 35, 'branch': '11-B', 'endpoint': 'passed_12_window_horizon', 'trajectory_regime': 'bounded_non_destructive_exchange', 'wrong_basin_slope': 0.00439303630184246, 'wrong_basin_post_transient_slope': 0.0008716360195236764, 'classification': 'reusable_dual_basin_exchange_class', 'series_ready_for_12': True, 'next': '12_long_horizon_artifact_replay_and_compatibility_closeout', 'id6_claimed': False, 'claim_flags_false': True}

N07 artifact sweep:
{'artifact_count': 19, 'total_checks': 615, 'failed': []}
```

## Iteration 12. Long-Horizon Artifact Replay And Compatibility Closeout

Status: Passed. Core N07 closeout is complete.

- [x] Replay the Iteration 10 design and the completed 11-* long-horizon branch
      series from artifacts only.
- [x] Recompute support, compatibility, leakage, recovery/re-separation, and
      budget records.
- [x] Reconstruct the 11-* trajectory-regime inventory and the stop/closeout
      rationale from artifacts only.
- [x] Verify controls replay with source-specific ceilings and distinct
      blockers.
- [x] Freeze the strongest N07 ceiling after long-horizon evidence.
- [x] Preserve all claim flags as false unless a separate future native
      identity-acceptance contract exists.

Expected artifacts:

- [x] `outputs/n07_iteration_12_long_horizon_compatibility_closeout.json`
- [x] `reports/n07_iteration_12_long_horizon_compatibility_closeout.md`

Acceptance statement:

```text
Iteration 12 passes if the long-horizon 11-* compatibility branch series can be
replayed from artifacts only and the strongest supported N07 ceiling is frozen
without runtime claim promotion. It must reconstruct the trajectory-regime
inventory and the 11-* stop/closeout rationale. If long-horizon compatibility
remains blocked, the closeout must preserve that blocker rather than promoting
ID6. If replay passes, any ID6 wording is source-specific artifact-only
evidence classification, not runtime identity acceptance.
```

Implementation record:

- Added `scripts/run_n07_iteration_12_long_horizon_compatibility_closeout.py`.
- Consumed Iteration 10, 11-0, 11-A, and 11-B exported artifacts and reports.
- Performed artifact-only replay with `runtime_state_used = false`.
- Reconstructed the completed 11-* branch inventory:
  `11-0 = unbounded_degrading_without_recovery`,
  `11-A = bounded_degrading`,
  `11-B = bounded_non_destructive_exchange`.
- Recomputed 11-B metric series and slopes from serialized
  `reservoir_window_records`; verified series, slopes, and post-transient
  slopes match the source artifact.
- Replayed 21 controls with 14 distinct blockers and required blockers present:
  `wrong_basin`, `wrong_support_area`, `hidden_support_field`,
  `budget_discontinuity`, `misframed_zero_leakage_requirement`,
  `support_drift_beyond_threshold`, and `identity_claim_promotion`.
- Froze the long-horizon C3 class as `bounded_non_destructive_exchange`.
- Froze the strongest source-specific N07 evidence ceiling as `ID6`.
- Recorded that this ID6 is artifact-only evidence classification, not runtime
  identity acceptance.
- Preserved all claim flags as `false`, including runtime identity acceptance,
  RC identity collapse, semantic choice, agency, biological identity,
  personhood, and unrestricted identity.
- Recorded optional Iteration 13 invitations as future work, not required for
  N07 closeout.

Run result:

```text
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_12_long_horizon_compatibility_closeout.py
{"artifact_only": true, "c3_class": "bounded_non_destructive_exchange", "ceiling": "ID6", "checks": 30, "identity_acceptance_claim_allowed": false, "next": "13_future_exploration_invitations_optional", "runtime_state_used": false, "status": "passed"}
outputs/n07_iteration_12_long_horizon_compatibility_closeout.json
reports/n07_iteration_12_long_horizon_compatibility_closeout.md
```

Artifact hashes:

```text
127262715f6871e997efeabb861f9426e369ee1ffebbd6099637a16a7bc94142  scripts/run_n07_iteration_12_long_horizon_compatibility_closeout.py
af966c2f8063d88078d7a1c5fb9cfc0286b383ce7970221bdd8248e443c5c189  outputs/n07_iteration_12_long_horizon_compatibility_closeout.json
33bfb5c32c7212cce496d1d0e2495dda95b9627ffe510fe79afe4981548d7bc8  reports/n07_iteration_12_long_horizon_compatibility_closeout.md
```

Validation:

```text
.venv/bin/python -m py_compile experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_12_long_horizon_compatibility_closeout.py
py_compile_passed

.venv/bin/python -m json.tool experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_12_long_horizon_compatibility_closeout.json
json_tool_passed

focused artifact assertions:
{'status': 'passed', 'checks': 30, 'ceiling': 'ID6', 'c3_class': 'bounded_non_destructive_exchange', 'id6_evidence_classification_supported': True, 'id6_is_runtime_identity_acceptance': False, 'runtime_identity_acceptance_claim_allowed': False, 'artifact_only': True, 'runtime_state_used': False, 'claim_flags_false': True, 'next': '13_future_exploration_invitations_optional'}
```

## Iteration 13. Identity-Support Withdrawal Baseline For N10

Status: Passed.

Detailed intro:

N07 Iteration 12 closed the core identity/compatibility question with an
artifact-only, source-specific ID6 evidence classification for bounded
non-destructive exchange. That closeout intentionally did not test what happens
when the support area is weakened or withdrawn.

N09 then preserved the blocker:

```text
n07_identity_withdrawal_baseline_not_available
```

That was the right boundary. N09 could regulate a proxy, but it could not
decide whether a support weakening disrupted the identity substrate or merely
exposed an untested N07 condition.

Iteration 13 supplies that missing baseline for N10. It does not reopen broad
N07 identity theory and does not promote runtime identity acceptance. It gives
N10 a source-backed way to distinguish:

- support-intact bounded exchange;
- mild support weakening that still survives;
- N09-matched partial support withdrawal that disrupts support without
  restoration;
- explicit restoration that recovers support survival.

Goal:

Make identity/support consumption precise before N10 uses N09 goal-proxy
regulation evidence. N10 can now ask whether a regulated proxy is attached to
a surviving support basin, a disrupted support basin, or a basin that survived
only because restoration support was explicitly supplied.

- [x] Consume N07 Iteration 11-B and Iteration 12 source artifacts.
- [x] Consume N09 Iteration 8 support-withdrawal handoff and Iteration 12
      closeout artifacts.
- [x] Verify the N09 identity-support digest matches the N07 support-area
      digest.
- [x] Emit support-intact, mild-withdrawal, N09-matched partial-withdrawal, and
      explicit-restoration lanes.
- [x] Classify support survival/disruption without private runtime state.
- [x] Preserve exact budget accounting.
- [x] Confirm old N09 artifacts are not retroactively changed.
- [x] Emit N10 handoff fields.
- [x] Preserve all identity, agency, semantic choice, biological, personhood,
      and unrestricted claims as blocked.

Expected artifacts:

- [x] `outputs/n07_iteration_13_identity_support_withdrawal_baseline.json`
- [x] `reports/n07_iteration_13_identity_support_withdrawal_baseline.md`

Acceptance statement:

```text
Iteration 13 passes if N07 emits a source-backed identity/support withdrawal
baseline for N10 consumption, tied to the N07 Iteration 12 support digest and
the N09 withdrawal blocker. The baseline must include support-intact, weakened,
N09-matched withdrawn, and explicitly restored lanes; classify
survival/disruption without private runtime state; preserve exact budget
accounting; avoid retroactively changing N09 closeout artifacts; and keep
identity acceptance, RC identity collapse, semantic choice, agency, biological,
personhood, and unrestricted identity claims blocked.
```

Acceptance state: Achieved.

Implementation record:

- Command:
  `.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_13_identity_support_withdrawal_baseline.py`
- Script:
  `scripts/run_n07_iteration_13_identity_support_withdrawal_baseline.py`
- Output:
  `outputs/n07_iteration_13_identity_support_withdrawal_baseline.json`
- Report:
  `reports/n07_iteration_13_identity_support_withdrawal_baseline.md`
- Result:
  - Status: `passed`.
  - Baseline available: `true`.
  - N09 prior blocker:
    `n07_identity_withdrawal_baseline_not_available`.
  - N09 prior blocker resolved for future consumption: `true`.
  - Old N09 artifacts retroactively changed: `false`.
  - N10 can consume identity-support withdrawal baseline: `true`.

Source baseline:

- Support area id: `n07_support_area_A_v1`.
- Support area digest:
  `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`.
- Source N07 ceiling: `ID6`.
- Source C3 class: `bounded_non_destructive_exchange`.
- Reference A support retention: `0.9731535762447039`.
- Support survival threshold: `0.85`.

Withdrawal lanes:

| Lane | Withdrawal | Restoration | Final A Support | Survives | Outcome |
|---|---:|---:|---:|---:|---|
| `support_intact_reference` | `0.0` | `0.0` | `0.9731535762447039` | `true` | `support_intact_bounded_exchange_reference` |
| `mild_support_weakening` | `0.1` | `0.0` | `0.8758382186202335` | `true` | `support_withdrawal_survival_baseline` |
| `n09_matched_partial_support_withdrawal` | `0.25` | `0.0` | `0.7298651821835279` | `false` | `support_disrupted_by_withdrawal_without_restoration` |
| `restored_after_n09_partial_withdrawal` | `0.25` | `0.8` | `0.9244958974324687` | `true` | `explicit_restoration_recovers_support_survival_baseline` |

N09 / N10 connection:

- N09's preserved blocker is resolved for future N10 consumption, not for
  retroactive reinterpretation of old N09 artifacts.
- N10 may use this baseline to distinguish proxy regulation attached to
  surviving support from proxy regulation where identity support is disrupted
  or explicitly restored.
- The N09 0.25 support withdrawal depth is now classified as support-disrupting
  without restoration under the N07 source baseline.

Controls:

- N09 support digest match control passed with blocker
  `identity_support_digest_mismatch`.
- Withdrawal depth serialized control passed with blocker
  `withdrawal_depth_missing_or_mismatch`.
- N09 partial withdrawal disrupts support control passed with blocker
  `support_disruption_not_detected`.
- Explicit restoration control passed with blocker
  `hidden_support_restoration_blocked`.
- Budget exact control passed with blocker `budget_discontinuity`.
- N09 not retroactively promoted control passed with blocker
  `retroactive_n09_claim_promotion_blocked`.
- Identity claim promotion control passed with blocker
  `identity_claim_promotion`.

Validation:

- `source_11b_passed = true`
- `source_12_passed = true`
- `source_12_id6_artifact_classification_preserved = true`
- `source_n09_i8_passed = true`
- `source_n09_i12_passed = true`
- `n09_prior_blocker_present = true`
- `n09_support_digest_matches_n07 = true`
- `four_lanes_recorded = true`
- `mild_withdrawal_survives = true`
- `n09_partial_withdrawal_disrupts_support = true`
- `explicit_restoration_recovers_support = true`
- `baseline_available_for_n10 = true`
- `old_n09_artifacts_not_retroactively_changed = true`
- `budget_exact = true`
- `claim_flags_all_false = true`
- `controls_all_passed = true`

Claim boundary:

- Iteration 13 makes a withdrawal baseline available for N10 consumption.
- It does not retroactively change N09 artifacts.
- It does not support runtime identity acceptance, RC identity collapse,
  semantic choice, agency, biological identity, personhood, or unrestricted
  identity.
