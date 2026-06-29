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

## Iteration 5 - Replay And Same-Basin Mapping Matrix

- [ ] Run artifact replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Verify same-basin signature preservation under mapping.
- [ ] Verify support/coherence floors.
- [ ] Verify boundary mapping.
- [ ] Verify hidden support reconstruction is absent.
- [ ] Demote rows that pass only by support reconstruction.

## Iteration 6 - Stress / Mapping-Variant Transfer Matrix

- [ ] Stress boundary mapping tolerance.
- [ ] Stress support preservation.
- [ ] Stress coherence preservation.
- [ ] Stress flux balance.
- [ ] Stress mapping variants.
- [ ] Distinguish narrow single-mapping transfer from variant-backed transfer.

## Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

- [ ] Run full fail-closed control matrix.
- [ ] Record AP4 dependency row-locally when route/selection participates.
- [ ] Record AP5 dependency row-locally when proxy/target participates.
- [ ] Confirm N26 scoped AP5 bridge does not become native AP5.
- [ ] Confirm AP5 NAT4 gap remains unresolved unless independently source-backed.
- [ ] Classify strongest CT rung.
- [ ] Keep unsafe claim flags false.

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
