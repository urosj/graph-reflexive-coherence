# N27 Configuration / Substrate Transfer Implementation Checklist

## Initialization

- [x] Create N27 experiment branch.
- [x] Create experiment directory structure.
- [x] Add README.
- [x] Add hypotheses.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add configs/outputs/reports/scripts indexes.

Initial state:

```text
status = initialized
positive_transfer_evidence_opened = false
ct_ladder_rung_assigned = false
n27_closeout_ladder_rung_assigned = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_1 = true
```

## Iteration 1 - Source Inventory And Transfer Contract Admission

- [x] Consume N20 I5 configuration/substrate transfer contract.
- [x] Consume N20 same-basin continuation rule for transfer.
- [x] Consume N26 closeout only as bounded PD6 proxy divergence / proxy collapse context.
- [x] Record N26 scoped artifact AP5 bridge context without promoting it to native AP5.
- [x] Record N26 AP5 NAT4 gap as unresolved.
- [x] Record N25.2 consumption only through N26 scoped context.
- [x] Record source roles, source digests, and source consumption boundaries.
- [x] Confirm no positive transfer evidence opens.
- [x] Confirm no semantic identity, native support, agency, sentience, Phase 8, or ant ecology claim opens.

Result:

```text
status = passed
acceptance_state = accepted_source_inventory_transfer_contract_admission_no_positive_evidence
descriptor_contract_row = n20_i4_row_08_configuration_substrate_transfer
consumable_contract_row = n20_i5_row_08_configuration_substrate_transfer
positive_transfer_evidence_opened = false
candidate_rows_classified = false
ct_ladder_rung_assigned = false
n27_closeout_ladder_rung_assigned = false
n26_consumed_as_transfer_evidence = false
n25_2_direct_transfer_consumption_allowed = false
native_support_opened = false
phase8_completion_opened = false
ant_ecology_opened = false
ready_for_iteration_2 = true
failed_checks = []
output_digest = 5ff3409dd63b9b52cf3e10e91797653c319af0564dbcc344dd9e9fc2c3cbb222
```

Interpretation: I1 admits the complete N20 I5 configuration/substrate transfer
contract and the N26 handoff boundary. It does not open transfer evidence.
N26 is available only as bounded PD6 proxy divergence / proxy collapse context
and scoped artifact AP5 bridge context; it is not native AP5, AP5 NAT4-gap
resolution, or transfer evidence. N25.2 remains inherited only through N26
scoped context and cannot be consumed directly as N27 substrate-transfer
evidence.

The movement/transfer boundary is also recorded: basin movement is within-frame
continuity, while transfer requires a declared cross-frame mapping with
pre/post basin signatures, boundary mapping, support/coherence preservation,
flux discipline, and fail-closed same-label/different-basin controls.

The active N20-N29 handoff and roadmap are cited as context but are not
SHA-pinned inside the I1 artifact, because they record the current N27 digest
state and would otherwise create a self-referential digest loop. JSON source
artifacts and stable markdown reports remain SHA-pinned.

Artifacts:

```text
outputs/n27_source_inventory_and_transfer_contract_admission.json
reports/n27_source_inventory_and_transfer_contract_admission.md
scripts/build_n27_source_inventory_and_transfer_contract_admission.py
```

## Iteration 2 - Transfer Schema And Control Freeze

- [x] Freeze CT0...CT6 ladder.
- [x] Freeze N27-C0...N27-C6 closeout ladder.
- [x] Freeze N20 I5 transfer contract as normative and N20 I4 descriptor as context-only.
- [x] Freeze source digest pins for I1 inventory, N20 I4 descriptor row, N20 I5 consumable row, and N26 closeout.
- [x] Freeze required evidence fields.
- [x] Freeze reusable `transfer_core` object.
- [x] Freeze `transfer_core_digest` canonicalization policy.
- [x] Freeze same-basin-under-mapping formulas and threshold record fields.
- [x] Freeze transfer scopes.
- [x] Freeze cross-substrate source-backed mapping requirements.
- [x] Freeze rung-specific artifact role requirements for CT1...CT6.
- [x] Freeze source-current mapping telemetry requirements.
- [x] Freeze support preservation vs support reconstruction separation.
- [x] Freeze replay requirements.
- [x] Freeze AP4/AP5 dependency statuses.
- [x] Require row-local reason when AP4/AP5 status is `not_applicable`.
- [x] Freeze active-null/control families.
- [x] Freeze orthogonal control semantics so each control rejects one false-positive path.
- [x] Freeze `control_satisfied_for_positive_row` and `control_applicability_reason`.
- [x] Freeze no-direct-N25.2 consumption invariant.
- [x] Freeze claim boundary and unsafe claim flags.
- [x] Confirm no positive transfer evidence opens.

Result:

```text
status = passed
acceptance_state = accepted_transfer_schema_and_controls_frozen_no_positive_evidence
n27_closeout_ceiling = N27-C2_transfer_schema_and_controls_frozen
positive_transfer_evidence_opened = false
candidate_rows_classified = false
ct_ladder_rung_assigned = false
n27_closeout_ladder_rung_assigned = false
ready_for_iteration_3 = true
failed_checks = []
output_digest = 15515b88b7b6853f9cb47f9fd22f4291a78d7037da586d795110dea91c55ab22
```

Digest pins:

```text
source_inventory_output_digest = 5ff3409dd63b9b52cf3e10e91797653c319af0564dbcc344dd9e9fc2c3cbb222
descriptor_contract_row_digest = c8be68905ad18176f6087210ad24cf2cc432d1b04e61e9db8edc54f86b46987f
consumable_contract_row_digest = 14d661d69af9aa62731834570a8db02e0050d8464c9a6b9608dcce2e472bb00c
n26_closeout_output_digest = bfb2f02a2c302da27215a87f5a42666ff11f5af5bbaed49ecc6204098afafe31
```

Interpretation: I2 freezes the transfer schema before positive evidence. It
makes N20 I5 normative and N20 I4 descriptor-only; it freezes CT/N27-C ladders,
the transfer-core fields, rung-specific artifact roles, source-current mapping
telemetry, transfer-core digest canonicalization, same-basin-under-mapping
formulas, threshold record fields, support-preservation versus
support-reconstruction separation, replay gates, AP4/AP5 row-local status
enums, positive-row control audit fields, and 22 fail-closed controls.

I2 blocks movement-only, same-label-only, visual/topological similarity,
proxy-score preservation, N26 proxy/AP5 relabeling, direct N25.2 backfill,
hidden support reconstruction, support reconstruction counted as preservation,
and AP4/AP5 prose-only handling. It still opens no transfer evidence.

Artifacts:

```text
outputs/n27_transfer_schema_and_controls.json
reports/n27_transfer_schema_and_controls.md
scripts/build_n27_transfer_schema_and_controls.py
```

## Iteration 3 - Active Nulls And Failure Baselines

- [x] Run same-label/different-basin control.
- [x] Run fixture-equivalence-label-only control.
- [x] Run mapping-declared-after-outcome control.
- [x] Run proxy-score-relabel-as-transfer control.
- [x] Run hidden-support-reconstruction control.
- [x] Run support-reconstruction-as-transfer control.
- [x] Run boundary-mapping-missing control.
- [x] Run post-transfer-signature-missing control.
- [x] Run source-current-inputs-missing control.
- [x] Run cross-substrate-mapping-missing control.
- [x] Run artifact-manifest-failure control.
- [x] Run replay-failure control.
- [x] Run stress-variant-failure control.
- [x] Run AP4-dependency-omitted control.
- [x] Run AP5-dependency-omitted control.
- [x] Run N26-proxy-as-transfer-evidence control.
- [x] Run N26-scoped-AP5-as-native-AP5 control.
- [x] Run N25.2-direct-transfer-consumption control.
- [x] Run semantic-identity-relabel control.
- [x] Run semantic-choice/goal-relabel control.
- [x] Run native-support-relabel control.
- [x] Run Phase 8 / ant ecology relabel control.
- [x] Confirm controls remain orthogonal and each null has a distinct blocker.
- [x] Confirm failed-open control count is zero.
- [x] Confirm all active nulls fail closed.
- [x] Confirm no positive CT rung is assigned.

Result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_transfer_evidence
n27_closeout_ceiling = N27-C3_active_nulls_fail_closed
positive_transfer_evidence_opened = false
candidate_rows_classified = false
ct_ladder_rung_assigned = false
n27_closeout_ladder_rung_assigned = false
required_control_count = 22
instantiated_control_count = 22
failed_closed_control_count = 22
failed_open_control_count = 0
ready_for_iteration_4_minimal_configuration_transfer_probe = true
failed_checks = []
output_digest = 2ef877fbbd8a66ca858a28d9deaf8ec84dbaf4529471920a90623499a2d4ebe3
```

Interpretation: I3 instantiates every frozen I2 false-transfer control before
positive probes. All 22 controls fail closed, with zero failed-open controls.
The rows reject label identity, fixture-label equivalence, post-hoc mapping,
proxy-score transfer relabels, hidden support reconstruction, support
reconstruction as preservation, missing boundary mapping, missing post-transfer
signature, report-only source inputs, unmapped substrate transfer, artifact
manifest failure, replay failure, stress failure, AP4/AP5 omission, N26 proxy
or AP5 overconsumption, direct N25.2 backfill, and semantic/native/Phase-8
relabels.

I3 supports only fail-closed blocker discipline. It does not support CT1, CT2,
CT3, transfer, identity, native support, native AP5, AP5 NAT4-gap resolution,
Phase 8, or ant ecology.

Revision note: the negative set is intentionally orthogonal. Each row records
one `primary_blocker_control_id`, marks that blocker as isolated by schema, and
keeps non-target positive gates at `not_evaluated_active_null`. This prevents a
null row from being accepted because unrelated transfer gates were forced to
fail.

Final boundary check: I3 also records every row as a negative-control row, not a
source-current positive probe. The report table now exposes
`control_id | blocker_triggered | expected_status | actual_status |
rung_effect | claim_allowed`, and the artifact records source precedence,
artifact-manifest failure subcases, and `implementation_patch_opened = false`.
That makes the I3 negative surface consumable by I4 without allowing label,
movement, proxy, support reconstruction, AP-gap, N26/N25.2, or unsafe relabel
shortcuts.

Artifacts:

```text
outputs/n27_active_nulls_and_failure_baselines.json
reports/n27_active_nulls_and_failure_baselines.md
scripts/build_n27_active_nulls_and_failure_baselines.py
```

## Iteration 4 - Minimal Configuration Transfer Probe

- [x] Declare mapping before use.
- [x] Record pre-transfer basin signature.
- [x] Record post-transfer basin signature.
- [x] Record boundary mapping trace.
- [x] Record support/coherence preservation.
- [x] Record flux balance.
- [x] Record artifact manifest and hashes.
- [x] Keep result provisional pending replay/control validation.

Result:

```text
status = passed
acceptance_state = accepted_minimal_source_current_CT2_candidate_pending_replay_controls
n27_closeout_ceiling = N27-C4_source_current_transfer_candidate_supported
positive_transfer_evidence_opened = true
candidate_rows_classified = true
provisional_ct_ladder_rung = CT2
ct_ladder_rung_assigned = false
ct_assignment_scope = provisional_candidate_only_pending_replay_controls
ct3_or_stronger_supported = false
final_transfer_supported = false
ready_for_iteration_4a_topology_fixture_variant_transfer_probe = true
ready_for_iteration_5_replay_same_basin_mapping_matrix = true
failed_checks = []
output_digest = f98f5d56d15389fa6a8a3f138c6cccb30404bd7e9ef4c6a4badd7ef13be04294
```

Interpretation: I4 opens the first positive source-current transfer surface.
The row maps `fixture_alpha_frame` to `fixture_beta_frame` with a declared
configuration mapping before post-transfer observation. It records pre/post
basin signatures, mapped boundary, support and coherence floors above
threshold, bounded flux imbalance, and an empty reconstruction ledger.

Alpha/beta frame explanation: `fixture_alpha_frame` is the pre-transfer
configuration, and `fixture_beta_frame` is the post-transfer configuration.
They are not semantic places or identities. They are two declared graph /
configuration frames with different node ids and coordinate/config rules.

The I4 mapping is:

```text
pre frame:
  alpha_core
  alpha_support
  alpha_boundary

declared mapping:
  alpha_core     -> beta_core
  alpha_support  -> beta_support
  alpha_boundary -> beta_boundary

post frame:
  beta_core
  beta_support
  beta_boundary
```

So I4 is not saying that a basin moved from one nearby location to another in
the same frame. It is saying that a pre-transfer basin signature is compared to
a post-transfer basin signature through a mapping declared before the post
result is inspected. The row counts only because the mapped boundary is present,
support/coherence floors remain above threshold, flux imbalance remains within
bound, and hidden support reconstruction is absent.

This is only a provisional CT2 candidate. It is not replay-backed CT3,
control-backed CT4, stress-backed CT5, final transfer, semantic identity,
native support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Review tightening: I4 now keeps replay and stress controls within the frozen
control-status enum by using `control_status = not_applicable` and recording
the CT2-specific deferral in `control_applicability_reason`. The boundary
mapping margin is exactly at floor:

```text
boundary_acceptance_operator = greater_than_or_equal
boundary_mapping_margin = 0.0
boundary_margin_at_floor = true
```

This is admissible for CT2, but it must be treated as a narrow boundary edge in
I6 stress/variant testing. I4 also records `transfer_schema_output_digest`,
`active_nulls_output_digest`, and `immediate_predecessor_output_digest` so the
predecessor chain is explicit.

Artifacts:

```text
outputs/n27_minimal_configuration_transfer_probe.json
outputs/n27_minimal_configuration_transfer_probe_artifacts/
reports/n27_minimal_configuration_transfer_probe.md
scripts/build_n27_minimal_configuration_transfer_probe.py
```

## Iteration 4-A - Topology / Fixture Variant Transfer Probe

- [x] Add a distinct declared mapping variant.
- [x] Verify the variant is source-backed.
- [x] Verify mapping-specific pre/post signature traces.
- [x] Reject same-label/different-basin success.
- [x] Keep result bounded as variant transfer evidence only.

Result:

```text
status = passed
acceptance_state = accepted_topology_fixture_variant_CT2_candidate_pending_replay_controls
n27_closeout_ceiling = N27-C4_source_current_transfer_candidate_supported
positive_transfer_evidence_opened = true
candidate_rows_classified = true
provisional_ct_ladder_rung = CT2
ct_ladder_rung_assigned = false
ct_assignment_scope = variant_candidate_only_pending_replay_controls
i4_replaced = false
i4a_replaces_i4 = false
ct3_or_stronger_supported = false
ct5_or_stronger_supported = false
final_transfer_supported = false
ready_for_iteration_5_replay_same_basin_mapping_matrix = true
failed_checks = []
output_digest = 5db5235c72e6954c5676be715cfdaa92cdc0e2d5746e5be40720e2152f5678f7
```

Interpretation: I4-A adds a distinct source-current topology / fixture mapping
variant. It maps a branched pre-frame fixture
`fixture_gamma_branch_frame` to a folded post-frame fixture
`fixture_delta_folded_frame`. Node ids, frame ids, coordinate rules, and edge
shape change. The row counts only because the declared topological role mapping
preserves the basin signature, maps all boundary edges, keeps support and
coherence above floor, keeps flux within bound, and records an empty
reconstruction ledger.

How I4-A differs from I4:

```text
I4:
  transfer kind = minimal configuration-frame transfer
  pre frame = fixture_alpha_frame
  post frame = fixture_beta_frame
  mapped nodes = alpha_core / alpha_support / alpha_boundary
               -> beta_core / beta_support / beta_boundary
  graph shape = simple three-node core-support-boundary fixture
  boundary margin = 0.0
  role in N27 = first minimal CT2 source-current transfer candidate

I4-A:
  transfer kind = topology / fixture variant transfer
  pre frame = fixture_gamma_branch_frame
  post frame = fixture_delta_folded_frame
  mapped nodes = gamma_core / gamma_left_support / gamma_right_support /
                 gamma_outer_boundary
               -> delta_core / delta_north_support / delta_south_support /
                  delta_outer_boundary
  graph shape = branched support fixture mapped into folded/cyclic support fixture
  boundary margin = 0.1
  role in N27 = additive distinct CT2 variant candidate
```

So I4 proves that the basic declared-transfer machinery can preserve a basin
signature across one minimal alpha/beta configuration mapping. I4-A asks
whether the same discipline survives a more structurally different fixture:
the node ids change, the frame changes, the coordinate rule changes, and the
edge geometry changes from a branch-like support layout to a folded support
layout. I4-A is stronger as variant coverage, but it is not a replay result and
does not erase I4's narrow boundary-at-floor condition.

Review validation: I4-A consumes the current I4 artifact digest
`f98f5d56d15389fa6a8a3f138c6cccb30404bd7e9ef4c6a4badd7ef13be04294` in
the top-level source record, row predecessor fields, and source-record chain.
The cross-substrate missing-mapping control is recorded as
`control_status = not_applicable` with
`rung_effect = substrate_transfer_claim_not_opened`, because I4-A is a
topology/fixture variant and does not open a substrate-transfer claim.

This is additive variant evidence. It does not replace I4, does not widen I4's
boundary-at-floor edge, and does not support replay-backed CT3, control-backed
CT4, stress-backed CT5, final transfer, semantic identity, native support,
native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Artifacts:

```text
outputs/n27_topology_fixture_variant_transfer_probe.json
outputs/n27_topology_fixture_variant_transfer_probe_artifacts/
reports/n27_topology_fixture_variant_transfer_probe.md
scripts/build_n27_topology_fixture_variant_transfer_probe.py
```

## Iteration 4-B - Transfer Side-Effect Observation Probe

- [x] Record focal-basin stability under the I4-A transfer surface.
- [x] Record neighbor distinguishability and support/coherence side effects.
- [x] Record environment basin-forming capacity side effects.
- [x] Record focal extraction cost and extractive flattening.
- [x] Record merge/leakage as a blocker, not as support.
- [x] Keep N28 generative persistence blocked.

Result:

```text
status = passed
acceptance_state = accepted_source_current_transfer_side_effect_observation_no_n28_claim
n28_readiness_side_effect_observation_supported = true
n28_generative_persistence_supported = false
ready_for_iteration_5b_side_effect_replay = true
failed_checks = []
output_digest = a398c63ae42d5275b4d7ca32a7a7be0f7c88b279b90b8e6bfd495107343e94a0
```

Interpretation: I4-B observes the environment-side consequences of the I4-A
topology transfer candidate. It records focal stability, neighbor
distinguishability, neighbor support, environment basin-forming capacity,
focal extraction cost, extractive flattening, and merge/leakage ceilings.

The result is useful for N28 because it is not only a transfer ledger. It gives
N28 a measured side-effect surface. It still does not support N28 generative
persistence, ecology, agency, native support, semantic cooperation, or Phase 8.

Artifacts:

```text
outputs/n27_transfer_side_effect_observation_probe.json
outputs/n27_transfer_side_effect_observation_probe_artifacts/
reports/n27_transfer_side_effect_observation_probe.md
scripts/build_n27_transfer_side_effect_observation_probe.py
```

## Iteration 5 - Replay And Same-Basin Mapping Matrix

- [x] Run artifact replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Verify same-basin signature preservation under mapping.
- [x] Verify support/coherence floors.
- [x] Verify boundary mapping.
- [x] Verify hidden support reconstruction is absent.
- [x] Demote rows that pass only by support reconstruction.

Result:

```text
status = passed
acceptance_state = accepted_replay_same_basin_mapping_matrix_CT3_candidates_pending_controls_stress
n27_closeout_ceiling = N27-C4_source_current_transfer_candidate_supported
positive_transfer_evidence_opened = true
candidate_rows_classified = true
provisional_ct_ladder_rung = CT3
ct_ladder_rung_assigned = false
ct_assignment_scope = replay_backed_candidate_only_pending_controls_stress_closeout
ct3_replay_candidate_supported = true
ct4_or_stronger_supported = false
ct5_or_stronger_supported = false
ct6_or_stronger_supported = false
final_transfer_supported = false
replay_row_count = 2
ready_for_iteration_6_stress_mapping_variant_transfer_matrix = true
failed_checks = []
output_digest = de0f5f7dc0f3cd1482569465198473940faa52275943ab7af1333a5c88bcf7c6
```

Interpretation: I5 replays the two existing CT2 candidates: the I4
alpha/beta minimal configuration-frame transfer and the I4-A gamma/delta
topology/fixture variant transfer. It runs the frozen CT3 replay modes:

```text
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
mapping_order_replay = passed
```

Duplicate replay is interpreted as idempotent replay: the digest remains
stable and no second positive transfer row is created. Mapping-order replay
checks that the declared mapping precedes the pre/post observations and that
the mapping digest excludes the post-transfer outcome.

Geometrically, I5 does not introduce a new transfer geometry. It verifies that
the already observed I4 and I4-A basin signatures, boundary mappings,
support/coherence floors, flux bounds, and empty reconstruction ledgers remain
stable when replayed. That moves the strongest local evidence from CT2
source-current transfer candidate to CT3 replay-backed same-basin transfer
candidate.

This is not final transfer. I5 does not run stress/variant testing, does not
complete full claim classification, does not resolve AP4/AP5 NAT4 gaps, does
not support native support, and does not open Phase 8 or ant ecology.

Artifacts:

```text
outputs/n27_replay_same_basin_mapping_matrix.json
outputs/n27_replay_same_basin_mapping_matrix_artifacts/
reports/n27_replay_same_basin_mapping_matrix.md
scripts/build_n27_replay_same_basin_mapping_matrix.py
```

## Iteration 5-A - Artifact-Only Reconstruction Replay Probe

- [x] Reconstruct I4 transfer core from artifact files only.
- [x] Reconstruct I4-A transfer core from artifact files only.
- [x] Use source manifests only as artifact indexes.
- [x] Use source row summaries only as expected digest targets.
- [x] Verify reconstructed transfer cores match source and I5 digests.
- [x] Verify reconstruction digest stability.
- [x] Verify mapping order from artifact traces.
- [x] Verify same-basin metrics from artifact traces.
- [x] Confirm no new transfer evidence is created.

Result:

```text
status = passed
acceptance_state = accepted_artifact_only_reconstruction_replay_hygiene_for_CT3_candidates_no_new_transfer
n27_closeout_ceiling = N27-C4_source_current_transfer_candidate_supported
positive_transfer_evidence_opened = true
new_transfer_evidence_created = false
candidate_rows_classified = true
provisional_ct_ladder_rung = CT3
ct_ladder_rung_assigned = false
ct_assignment_scope = artifact_only_reconstruction_hygiene_for_existing_CT3_candidates
ct3_replay_hygiene_supported = true
ct4_or_stronger_supported = false
ct5_or_stronger_supported = false
ct6_or_stronger_supported = false
final_transfer_supported = false
reconstruction_row_count = 2
ready_for_iteration_6_stress_mapping_variant_transfer_matrix = true
failed_checks = []
output_digest = 5cba66c4ac1d1c855fc830ac1bbe274e209a08aef8faf884f1b1576512b6de36
```

Interpretation: I5-A strengthens I5 replay hygiene by reconstructing the I4
and I4-A transfer cores from emitted artifact files only. The reconstruction
uses the source candidate manifest as an artifact index and the source/I5
transfer-core digests as comparison targets, but it does not trust candidate
row summary fields to build the core.

Both rows pass:

```text
I4 artifact-only reconstructed core =
  205a7848363076da87de0ff9713437504606769844c8eba9792f4a68e602afa4

I4-A artifact-only reconstructed core =
  e1c4dc4d6dbc9bcd99c2d347ff05a955cf69dab07a933ad2fb20c890bcf602a9
```

The reconstructed cores match the source candidate digests and the I5 replay
source digests. Mapping order, same-basin preservation, boundary mapping,
support/coherence floors, flux bounds, and empty support-reconstruction ledgers
are all reconstructed from artifact traces.

This is not new transfer evidence. I5-A does not add a mapping, does not
create a post-transfer basin signature, does not run stress, does not complete
full controls, and does not support final transfer, semantic identity, native
support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Artifacts:

```text
outputs/n27_artifact_only_reconstruction_replay_probe.json
outputs/n27_artifact_only_reconstruction_replay_probe_artifacts/
reports/n27_artifact_only_reconstruction_replay_probe.md
scripts/build_n27_artifact_only_reconstruction_replay_probe.py
```

## Iteration 5-B - Transfer Side-Effect Replay Probe

- [x] Replay I4-B side-effect traces.
- [x] Reconstruct side-effect traces from artifacts.
- [x] Verify replay digest stability.
- [x] Verify duplicate replay does not create a second positive row.
- [x] Confirm no new side-effect evidence is created by replay.
- [x] Keep N28 generative persistence blocked.

Result:

```text
status = passed
acceptance_state = accepted_transfer_side_effect_replay_reconstruction_no_n28_claim
n28_readiness_side_effect_replay_supported = true
n28_generative_persistence_supported = false
ready_for_iteration_6a_side_effect_evaluation_matrix = true
failed_checks = []
output_digest = 3f034af77147172b99e885793b82438285990d46ee364ae95cd801ea6385eef7
```

Interpretation: I5-B makes the I4-B side-effect observation replayable and
artifact-reconstructable. This avoids handing N28 only a report-level claim.
Replay does not create new side-effect evidence and does not support N28
generative persistence.

Artifacts:

```text
outputs/n27_transfer_side_effect_replay_probe.json
outputs/n27_transfer_side_effect_replay_probe_artifacts/
reports/n27_transfer_side_effect_replay_probe.md
scripts/build_n27_transfer_side_effect_replay_probe.py
```

## Iteration 6 - Stress / Mapping-Variant Transfer Matrix

- [x] Stress boundary mapping tolerance.
- [x] Stress support preservation.
- [x] Stress coherence preservation.
- [x] Stress flux balance.
- [x] Stress mapping variants.
- [x] Distinguish narrow single-mapping transfer from variant-backed transfer.

Result:

```text
status = passed
acceptance_state = accepted_stress_mapping_variant_candidate_pending_i7_controls_no_final_transfer
n27_closeout_ceiling = N27-C4_source_current_transfer_candidate_supported
positive_transfer_evidence_opened = true
new_transfer_evidence_created = false
candidate_rows_classified = true
provisional_ct_ladder_rung = CT5_candidate_pending_controls
ct_ladder_rung_assigned = false
ct_assignment_scope = stress_variant_candidate_pending_i7_controls_and_closeout
ct3_replay_candidate_supported = true
ct5_stress_variant_candidate_supported = true
ct5_assignment_allowed = false
ct5_assignment_blocker = full_control_trace_pending_iteration_7
ct5_or_stronger_supported = false
ct6_or_stronger_supported = false
final_transfer_supported = false
stress_pass_count = 1
stress_limited_count = 1
ready_for_iteration_7_controls_ap_dependency_claim_classification = true
failed_checks = []
output_digest = 3335a4a6017a96b6d71c6e1f386bb2d17669208f8d8daf9b7a25a49755e7324a
```

Interpretation: I6 stress-tests the two replay-backed CT3 candidates under a
declared boundary/support/coherence/flux stress policy. It keeps I4 and I4-A
separate rather than merging their outcomes.

I4 remains valid CT3 replay-backed evidence, but it is stress-limited:

```text
source = I4 alpha/beta minimal configuration transfer
boundary_margin = 0.0
failed_stress_rows =
  boundary_tightening_0_05
  combined_moderate_mapping_stress
row_decision = partial
```

This does not invalidate I4. It records that the minimal configuration
transfer sits exactly at the boundary floor and should not be overread as broad
stress robustness.

I4-A supplies the stronger stress result:

```text
source = I4-A gamma/delta topology fixture variant
boundary_margin = 0.1
support_margin = 0.015
coherence_margin = 0.025
flux_margin = 0.028
failed_stress_rows = none
row_decision = supported
```

The I4-A row survives boundary tightening, support drawdown, coherence
drawdown, flux pressure, and combined moderate mapping stress. This supports a
bounded stress/variant candidate. However, the frozen CT5 artifact role also
requires a full control trace, so I6 records
`ct5_assignment_allowed = false` pending I7.

I7 must consume I6 asymmetrically:

```text
I4   = CT3 replay-backed stress-limited candidate; no CT5 contribution
I4-A = CT5-candidate evidence pending I7 controls
```

The I6 control trace is only a stress-control trace, not the full I7 control
matrix. I7 must still validate the frozen controls, AP4/AP5 row-local
dependency statuses, N26/N25.2 consumption boundaries, and unsafe claim
blockers before assigning any stronger CT rung.

This is not final transfer. I6 does not complete full claim classification,
does not resolve AP4/AP5 NAT4 gaps, does not support native support, and does
not open Phase 8 or ant ecology.

Artifacts:

```text
outputs/n27_stress_mapping_variant_transfer_matrix.json
outputs/n27_stress_mapping_variant_transfer_matrix_artifacts/
reports/n27_stress_mapping_variant_transfer_matrix.md
scripts/build_n27_stress_mapping_variant_transfer_matrix.py
```

## Iteration 6-A - N28 Precursor Side-Effect Evaluation Matrix

- [x] Evaluate replayed side-effect traces under a declared N28 precursor policy.
- [x] Confirm focal stability is preserved.
- [x] Confirm neighbor capacity, distinguishability, and support improve.
- [x] Confirm focal extraction cost remains below ceiling.
- [x] Confirm extractive flattening remains below ceiling.
- [x] Confirm merge/leakage remains below ceiling.
- [x] Keep N28 generative persistence blocked.

Result:

```text
status = passed
acceptance_state = accepted_n28_precursor_side_effect_evaluation_no_n28_claim
n28_precursor_evaluation_supported = true
n28_generative_persistence_supported = false
ready_for_iteration_7a_side_effect_claim_classification = true
failed_checks = []
output_digest = 2dbe7d94d14ffd6753952dfb5360ac779b2c433c0a24e3a8a7444b40964fd1af
```

Evaluation summary:

```text
focal_stability_preserved = true
neighbor_capacity_delta = 0.10
neighbor_distinguishability_delta = 0.10
neighbor_support_delta = 0.04
focal_extraction_cost = 0.018
extractive_flattening_score = 0.022
merge_leakage_score = 0.018
```

Interpretation: I6-A evaluates the replayed I4-B/I5-B side-effect surface as a
N28-ready precursor. It shows focal transfer stability with positive
environment-side capacity indicators below extraction/leakage ceilings. It
does not claim N28 generative persistence; that remains N28 scope.

Artifacts:

```text
outputs/n27_n28_precursor_side_effect_evaluation_matrix.json
outputs/n27_n28_precursor_side_effect_evaluation_matrix_artifacts/
reports/n27_n28_precursor_side_effect_evaluation_matrix.md
scripts/build_n27_n28_precursor_side_effect_evaluation_matrix.py
```

## Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

- [x] Run full fail-closed control matrix.
- [x] Record AP4 dependency row-locally when route/selection participates.
- [x] Record AP5 dependency row-locally when proxy/target participates.
- [x] Confirm N26 scoped AP5 bridge does not become native AP5.
- [x] Confirm AP5 NAT4 gap remains unresolved unless independently source-backed.
- [x] Classify strongest CT rung.
- [x] Keep unsafe claim flags false.

Result:

```text
status = passed
acceptance_state = accepted_ct5_controls_ap_claim_classification_pending_i8_closeout
n27_closeout_ceiling = N27-C5_replay_control_stress_backed_transfer_candidate_supported
positive_transfer_evidence_opened = true
new_transfer_evidence_created = false
candidate_rows_classified = true
classified_ct_ladder_rung = CT5
ct_ladder_rung_assigned = true
ct_assignment_scope = controls_ap_claim_classification_pending_i8_closeout
ct3_replay_candidate_supported = true
ct4_control_backed_candidate_supported = true
ct5_or_stronger_supported = true
ct6_or_stronger_supported = false
final_transfer_supported = false
failed_open_control_count = 0
failed_closed_control_count = 1
ready_for_iteration_8_closeout_and_n28_handoff = true
failed_checks = []
output_digest = d25a2490345a25e41c76f76afecbd267d3dba77e3d2b0fdf6b3f8c256ccaa08c
```

Interpretation: I7 consumes I6 without creating new transfer geometry. It runs
the full frozen I2 control matrix over both candidate rows and records AP4/AP5
dependency statuses row-locally.

The I4 alpha/beta row remains useful, but bounded:

```text
source = I4 alpha/beta minimal configuration transfer
classification = CT4_control_clean_stress_limited
row_decision = partial
ct5_supported = false
ct5_contribution_allowed = false
failed_closed_control = stress_variant_failure_control
```

The row is control-clean for its supported scope, but the I6 stress blocker
remains valid. I7 therefore does not let I4 contribute to CT5.

The I4-A gamma/delta topology / fixture variant becomes the strongest
classified row:

```text
source = I4-A gamma/delta topology fixture variant
classification = CT5
row_decision = supported
ct5_supported = true
failed_open_control_count = 0
```

The full control matrix records all frozen controls as passed or explicitly
not applicable. The only `failed_closed` control in I7 is the I4 stress gate,
which correctly blocks I4 from CT5 rather than invalidating the whole tranche.

AP4/AP5 classification:

```text
ap4_dependency_status = not_applicable
ap4_condition_reason = configuration/topology mapping does not use route-conditioned selection
ap5_dependency_status = not_applicable
ap5_condition_reason = mapping does not use proxy or target formation
```

N26 remains bounded context, not transfer evidence. N25.2 is not directly
consumed. Native AP5 and AP5 NAT4-gap resolution remain blocked. Semantic
identity, semantic choice, native support, sentience, Phase 8 completion, and
ant ecology claims remain false.

This is still not final transfer. I7 supports CT5 as a controlled
stress/variant-backed transfer candidate, while CT6 and final N27 closeout
remain I8 scope.

Artifacts:

```text
outputs/n27_controls_ap_dependency_claim_classification.json
outputs/n27_controls_ap_dependency_claim_classification_artifacts/
reports/n27_controls_ap_dependency_claim_classification.md
scripts/build_n27_controls_ap_dependency_claim_classification.py
```

## Iteration 7-A - N28 Precursor Side-Effect Claim Classification

- [x] Block focal survival alone as N28 generativity.
- [x] Block neighbor label/count-only success.
- [x] Block merge/leakage as neighbor support.
- [x] Block masked extractive flattening.
- [x] Block CT5 transfer success as N28 success.
- [x] Block semantic cooperation and agency relabels.
- [x] Block native support, ant ecology, and Phase 8 relabels.

Result:

```text
status = passed
acceptance_state = accepted_n28_ready_side_effect_precursor_claim_clean_no_n28_claim
n28_precursor_evaluation_supported = true
n28_generative_persistence_supported = false
n28_experiment_ready = true
ready_for_iteration_8_closeout_and_n28_handoff = true
failed_checks = []
output_digest = 10a4ca23ea7c111a6de53fd2c5b27d30cd75063ef7c7304cad46010776362fbb
```

Interpretation: I7-A makes the side-effect evaluation claim-clean for N28
handoff. It blocks the main false positives: focal survival alone,
neighbor-label-only capacity, merge/leakage masquerading as support,
extractive flattening hidden by focal persistence, CT5 transfer relabeled as
N28 success, semantic cooperation, native support, ant ecology, and Phase 8
completion.

The supported result is:

```text
N28-ready precursor side-effect evaluation artifact
```

Not:

```text
N28 generative persistence
ecology
agency
native support
semantic cooperation
Phase 8 completion
```

Artifacts:

```text
outputs/n27_n28_precursor_side_effect_claim_classification.json
outputs/n27_n28_precursor_side_effect_claim_classification_artifacts/
reports/n27_n28_precursor_side_effect_claim_classification.md
scripts/build_n27_n28_precursor_side_effect_claim_classification.py
```

## Iteration 8 - Closeout And N28 Handoff

- [ ] Assign final CT rung if warranted.
- [ ] Assign final N27-C rung if warranted.
- [ ] Record final claim ceiling.
- [ ] Record final source roles.
- [ ] Record final controls and blockers.
- [ ] Confirm no absolute paths.
- [ ] Confirm `src_diff_empty` unless implementation changes were explicitly opened.
- [ ] Record N28 handoff.

## Claim Boundary

N27 must not support:

```text
semantic identity
semantic choice
semantic goal ownership
semantic learning
agency
native support
selfhood
identity acceptance
sentience
organism/life
ant ecology implementation
Phase 8 completion
unscoped multi-basin substrate
native AP5
AP5 NAT4 gap resolution
```
