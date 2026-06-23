# N21 Withdrawal Resistance And Naturalization Depth Implementation Checklist

## Initialization

- [x] Create `experiment-N21` branch.
- [x] Create N21 experiment directory.
- [x] Add top-level N21 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N21 scoped to withdrawal resistance and naturalization depth.
- [x] Confirm N21 starts from N20 contract evidence, not primitive evidence.

## Global Rules

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Consume N20 I5 withdrawal-resistance row without redefinition.
- [x] Consume N20 I5 naturalization-depth row without redefinition.
- [x] Declare row-specific thresholds before use.
- [x] Require actual LGRC/source-current run artifacts for positive primitive
      evidence.
- [x] Reject report-only or synthetic-row success as insufficient evidence.
- [x] Separate N20 contract evidence from N21 primitive evidence.
- [x] Treat producer-mediated fields as producer residue unless source-backed
      naturalization evidence is produced.
- [x] Treat naturalization-debt fields as debt unless source-backed
      naturalization evidence is produced.
- [x] Reject blocked relabel fields when used as evidence.
- [x] Fail closed on hidden producer support.
- [x] Fail closed on proxy-only success.
- [x] Fail closed on label-only continuation.
- [x] Fail closed on post-hoc trace construction.
- [x] Force unsafe claim flags false in every row.
- [x] Do not modify `src/*`.
- [x] Do not write ant-ecology implementation specs in N21.
- [x] Keep agency, native support, sentience, and Phase 8 claims blocked.

## Iteration 1. Source Contract Inventory

- [x] Build N21 source contract inventory.
- [x] Read N20 closeout and N21 handoff.
- [x] Read N20 I5 same-basin continuation contract.
- [x] Record withdrawal-resistance source row.
- [x] Record naturalization-depth source row.
- [x] Record N21 readiness gates.
- [x] Record source-current fields, producer-mediated fields, naturalization
      debt fields, and blocked relabel fields.
- [x] Record required controls for each primitive.
- [x] Confirm no primitive evidence is opened.
- [x] Confirm no agency, native support, sentience, Phase 8, or ant-ecology
      implementation claim is opened.

Expected artifacts:

```text
outputs/n21_source_contract_inventory.json
reports/n21_source_contract_inventory.md
scripts/build_n21_source_contract_inventory.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_source_contract_inventory_no_primitive_evidence
artifact = outputs/n21_source_contract_inventory.json
report = reports/n21_source_contract_inventory.md
script = scripts/build_n21_source_contract_inventory.py
command = .venv/bin/python experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/scripts/build_n21_source_contract_inventory.py
row_count = 2
output_digest = d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee
artifact_sha256 = 9c4b35fad34d5bc1ec3cf740cd475f30b21ff4ee51a82ee0d148e2111769eb6e
report_sha256 = df1332a1901095249411394565e2a5a0afda8d65668aa3ed4daaa007ab4ee102
script_sha256 = 24dc7385f33f035358b336099210ef251687fd452d33817383c7cc6780536efd
failed_checks = []
check_count = 21
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
n21_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
source_contract_inventory_only = true
ready_for_iteration_2_schema_freeze = true
```

Iteration 1 is source-contract inventory only. It confirms N20 closeout marks
N21 ready, the required I5 rows exist and are complete, both rows are consumed
without redefinition, source-current fields and producer/debt/relabel fields are
recorded, required controls are listed, and no primitive evidence or unsafe
claim is opened. N20 contract completeness defines eligibility only; it does
not assign WR, ND, or N21-C ladder rungs.

Post-review tightening record:

```text
global_unsafe_claim_flags cover all blocked claims = true
row_specific_blocked_relabels separated from global unsafe flags = true
row_decision = not_applicable for inventory rows = true
inventory_decision = supported_as_contract_input_only = true
controls_declared_fail_closed_in_contract = true
control_execution_status = not_run
n20_source_downstream_consumption_status marked as inherited source status = true
markdown roadmap/handoff sources context-only = true
I2 artifact path/digest fail-closed requirements added = true
```

## Iteration 2. Withdrawal And Naturalization Schema Freeze

- [x] Freeze N21 row schema.
- [x] Freeze full candidate evidence row schema with every required evidence
      field.
- [x] Freeze `same_basin_continuation_rule` as an explicit candidate row
      schema field.
- [x] Freeze `primitive_claim_allowed` as an explicit candidate row schema
      field.
- [x] Freeze `claim_ceiling` as an explicit candidate row schema field.
- [x] Freeze I1 `same_basin_rule` structures as read-only primitive
      references.
- [x] Freeze I1 `support_scaffold` structures as read-only primitive
      references.
- [x] Freeze I1 `handoff_inputs` structures as read-only primitive references.
- [x] Freeze local definition of `source_current`.
- [x] Freeze run-artifact admissibility schema.
- [x] Freeze artifact path existence validation.
- [x] Freeze artifact digest algorithm declaration.
- [x] Freeze artifact digest match validation against file contents.
- [x] Freeze rule that `derived_report_only = true` blocks positive support.
- [x] Freeze rule that a missing required artifact blocks rung assignment.
- [x] Freeze Markdown roadmap/handoff sources as context-only, not evidence
      sources.
- [x] Freeze separation of `global_unsafe_claim_flags` from
      `row_specific_blocked_relabels`.
- [x] Freeze rule that inventory rows use `inventory_decision` for contract
      support and keep `row_decision = not_applicable`.
- [x] Freeze distinction between declared controls and executed controls.
- [x] Freeze threshold declaration policy.
- [x] Freeze withdrawal window schema.
- [x] Freeze withdrawal fields: mode, target, start, end, amount, recovery
      window, and floor-crossing policy.
- [x] Freeze restricted claim handling for `withdrawal_target =
      producer_surface`.
- [x] Freeze probe-present/probe-absent schema.
- [x] Freeze probe absence fields: runtime input absent, residue digest absent,
      support annotation not evidence, producer probe schedule disabled.
- [x] Freeze support/coherence/boundary/flux result schema.
- [x] Freeze replay result schema.
- [x] Freeze fail-closed control schema.
- [x] Freeze replay/control status enum: `passed`, `failed_closed`,
      `failed_open`, `not_run`, `not_applicable`.
- [x] Freeze active-null comparability rule.
- [x] Freeze withdrawal-resistance ladder `WR0...WR6`.
- [x] Freeze naturalization-depth ladder `ND0...ND6`.
- [x] Confirm `ND0...ND6` is a local artifact ladder, not the full cross-scale
      theoretical naturalization-depth ladder.
- [x] Freeze combined closeout ladder `N21-C0...N21-C6`.
- [x] Freeze rule that N20 contract completeness defines eligibility but cannot
      assign WR, ND, or N21-C rungs.
- [x] Freeze rule that ladder rungs may be assigned only from source-backed N21
      evidence rows.
- [x] Freeze demotion precedence: I4/I5 rungs are provisional until I6 replay
      and controls complete.
- [x] Freeze WR4 as requiring artifact replay AND snapshot/load replay AND
      duplicate replay.
- [x] Freeze ND3 as requiring declared multi-window replay without original
      probe/scaffold.
- [x] Freeze exact closeout status enums for WR and ND.
- [x] Freeze row-decision policy.
- [x] Confirm `supported` does not automatically permit unsafe claims.
- [x] Confirm `partial`, `blocked`, and `rejected` do not permit primitive
      support claims.
- [x] Confirm no positive primitive evidence is opened.

Expected artifacts:

```text
outputs/n21_withdrawal_schema_and_thresholds.json
reports/n21_withdrawal_schema_and_thresholds.md
scripts/build_n21_withdrawal_schema_and_thresholds.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence
artifact = outputs/n21_withdrawal_schema_and_thresholds.json
report = reports/n21_withdrawal_schema_and_thresholds.md
script = scripts/build_n21_withdrawal_schema_and_thresholds.py
command = .venv/bin/python experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/scripts/build_n21_withdrawal_schema_and_thresholds.py
source_i1_output_digest = d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee
output_digest = 49ec439aa4d3f2bb895dc11d8c7613a0f18f75d4f78fa38aead2282ebbf78bb7
artifact_sha256 = 3bfbfc843f5d627d1105b7b5e9c7b57fb7a17b566d785f4c9d13c61a807e8ff5
report_sha256 = e8c5befb1734e383f6a4e22eb39cf272b7fbb3e8b124f78570c67e97924b9d31
script_sha256 = dabefdc0e1bd6b5c1b422b531d24d3178b8b6e0a5609adfe0b6963fe61bd5a5d
failed_checks = []
check_count = 22
schema_freeze_only = true
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
n21_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
ready_for_iteration_3_active_nulls = true
```

Iteration 2 freezes the schema and no more. It locks source-current evidence,
candidate evidence row fields, run-artifact admissibility, threshold
declaration, withdrawal/probe absence, support/coherence/boundary/flux result
statuses, replay/control statuses, active-null comparability, WR/ND/N21-C
ladders, demotion precedence, row decisions, closeout enums, and claim
boundaries. It opens no positive primitive evidence and assigns no ladder
rungs.

Post-review tightening record:

```text
candidate_evidence_row_schema_complete = true
candidate_evidence_row_field_count = 33
same_basin_continuation_rule_schema_field_frozen = true
primitive_claim_allowed_schema_field_frozen = true
claim_ceiling_schema_field_frozen = true
i1_same_basin_rule_references_frozen_read_only = true
i1_support_scaffold_references_frozen_read_only = true
i1_handoff_inputs_references_frozen_read_only = true
i1_claim_ceiling_references_frozen = true
candidate_rows_missing_required_fields_blocked = true
```

## Iteration 3. Active Nulls And Failure Baselines

- [x] Build active null rows.
- [x] Confirm active nulls use the same source contract row as matching
      candidate rows.
- [x] Confirm active nulls use the same source contract row digest.
- [x] Confirm active nulls use the same basin signature fields.
- [x] Confirm active nulls use the same seed or declared seed-pairing rule.
- [x] Confirm active nulls use the same topology/config family.
- [x] Confirm active nulls use the same runtime envelope digest.
- [x] Confirm active nulls use the same budget/schedule family where
      applicable.
- [x] Confirm active nulls use the same budget schedule digest where
      applicable.
- [x] Show no-withdrawal/no-removal cannot pass as withdrawal resistance.
- [x] Show label-only continuation cannot pass.
- [x] Show proxy-only improvement cannot pass.
- [x] Show hidden support cannot pass.
- [x] Show post-hoc trace construction cannot pass.
- [x] Show producer-mediated state cannot be relabeled as native support.
- [x] Record fail-closed blockers distinctly.
- [x] Confirm pre-positive active nulls fail closed before Iterations 4 and 5
      are admitted.

Expected artifacts:

```text
outputs/n21_withdrawal_active_nulls.json
reports/n21_withdrawal_active_nulls.md
scripts/build_n21_withdrawal_active_nulls.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_primitive_evidence
artifact = outputs/n21_withdrawal_active_nulls.json
report = reports/n21_withdrawal_active_nulls.md
script = scripts/build_n21_withdrawal_active_nulls.py
command = .venv/bin/python experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/scripts/build_n21_withdrawal_active_nulls.py
source_i1_output_digest = d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee
source_i2_output_digest = 49ec439aa4d3f2bb895dc11d8c7613a0f18f75d4f78fa38aead2282ebbf78bb7
output_digest = 154d10eb14dc54289154f28e9eb0107343f6e02939bc9905f35c30a09f041cf2
artifact_sha256 = 8c0961c0bff8d35585fa5d701d2678c8522169176622b3c7e37e0a895354a79a
report_sha256 = dad4fb8d31327433edc0bc53417dde1b196c881a223895de61812ed20cd2153c
script_sha256 = 6f2c18c2d5179395c29b5aacc19966a0bf0699e723bcd16a8dc484c2f4bbe479
failed_checks = []
check_count = 14
row_count = 14
failed_closed_rows = 14
failed_open_rows = 0
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
n21_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
ready_for_iteration_4_withdrawal_probe = true
ready_for_iteration_5_naturalization_probe = true
```

Iteration 3 is a pre-positive active-null pass. It records 14 rejected rows
across withdrawal resistance and naturalization depth. The rows cover
no-withdrawal/no-removal, no probe absence, label-only continuation,
proxy-only success, hidden producer support, post-hoc trace construction,
support floor crossing, probe residue, support annotation relabel, semantic
relabel, native-support relabel, and Phase 8 relabel controls. All tested
paths fail closed, no WR/ND/N21-C rung is assigned, and no positive primitive
evidence is opened.

Geometric interpretation:

```text
n21_i3_row_01_withdrawal_resistance_no_declared_withdrawal:
  Baseline basin geometry is never put under declared withdrawal pressure.
  Any apparent persistence is unstressed continuation, not withdrawal
  resistance.

n21_i3_row_02_withdrawal_resistance_label_only_continuation:
  The basin label persists while source-current basin signature,
  support/coherence trace, and boundary trace are absent. Same label is not
  same basin geometry.

n21_i3_row_03_withdrawal_resistance_proxy_only_improvement:
  A proxy score can improve while support, coherence, boundary, or flux gates
  fail. Proxy motion alone is not same-basin continuation.

n21_i3_row_04_withdrawal_resistance_hidden_producer_support:
  Apparent stability is carried by an undeclared producer support channel.
  Geometrically, the support vector was not truly withdrawn.

n21_i3_row_05_withdrawal_resistance_post_hoc_trace_construction:
  The continuity trace is assembled after outcome inspection. There is no
  ordered source-current geometric path through withdrawal.

n21_i3_row_06_withdrawal_resistance_support_floor_crossing:
  A recognizable shape may remain, but support crosses below the declared
  continuation floor. The basin leaves the valid continuation envelope.

n21_i3_row_07_withdrawal_resistance_unsafe_native_support_relabel:
  Producer schedules, thresholds, or semantic labels are relabeled as native
  support geometry. The row rejects that relabel.

n21_i3_row_08_naturalization_depth_probe_present_only:
  The original probe/scaffold remains part of the geometry. The basin has not
  shown post-probe persistence.

n21_i3_row_09_naturalization_depth_label_only_continuation:
  The post-probe label persists while post-probe basin signature and
  support/coherence geometry are absent.

n21_i3_row_10_naturalization_depth_proxy_only_improvement:
  A depth/proxy score improves while post-probe same-basin geometry is not
  established. Proxy success is not naturalization.

n21_i3_row_11_naturalization_depth_hidden_producer_support:
  Apparent post-probe survival is carried by hidden producer support. The
  scaffold was not truly absent in geometric terms.

n21_i3_row_12_naturalization_depth_post_hoc_trace_construction:
  The post-probe continuity trace is reconstructed after outcome inspection.
  There is no live source-current trajectory through probe removal.

n21_i3_row_13_naturalization_depth_probe_residue_only:
  Persistence is carried by residue from the original probe. This is leftover
  scaffolding, not naturalized basin continuation.

n21_i3_row_14_naturalization_depth_support_annotation_native_support_relabel:
  A support annotation or producer label is treated as source-current support.
  Annotation is not geometric support, so the row rejects it.
```

Geometric bottom line: Iteration 3 does not show a basin surviving withdrawal
or probe absence. It shows which apparent continuations must fail before
Iterations 4 and 5 may test real source-current continuation.

Post-review consumption guardrails:

```text
I3 active nulls can block false-positive paths, but cannot support WR, ND,
replay-backed rungs, or primitive evidence.

I3 establishes pre-positive fail-closed blockers.
I3 does not provide source-current primitive evidence.
I3 does not satisfy I6 replay/control over positive rows.

failed_closed means the blocker triggered and the claim was correctly rejected.
failed_open means the blocker should have rejected the claim, but the claim
still passed.

If an I4 or I5 candidate uses a different seed family, topology/config family,
runtime envelope, budget schedule, or other comparability surface than the I3
null rows, the I3 null must either be regenerated for that candidate envelope
or marked non-consuming for that row.

I3 covers support-floor crossing explicitly and records coherence, boundary,
and flux result statuses in every row. Dedicated coherence-floor crossing,
boundary-integrity failure, and flux/leakage explanation controls remain
available for I6 unless I4/I5 require candidate-specific null regeneration.

For naturalization depth, I3 covers probe-present-only, label-only, proxy-only,
hidden support, post-hoc trace, probe residue, and support annotation/native
support relabel false positives. Dedicated post-probe support/coherence floor
crossing remains available for I6 unless needed earlier by an I5 candidate.

I3 supports only the fail-closed-control portion of Hypothesis C. Hypothesis C
remains open until positive rows, replay/control matrix, producer residue,
naturalization debt, unsafe claim flags, and run-artifact admissibility are
checked in later iterations.
```

## Iteration 4. Withdrawal Resistance Probe

- [x] Run bounded withdrawal-resistance candidate.
- [x] Assign WR rung only from source-backed withdrawal evidence.
- [x] Record run artifact ID and artifact digest.
- [x] Record source commit or source digest.
- [x] Record runtime config digest.
- [x] Record source contract row digest.
- [x] Record baseline artifact path.
- [x] Record withdrawn artifact path.
- [x] Record event log or trace path.
- [x] Record snapshot or replay artifact path.
- [x] Confirm `derived_report_only = false`.
- [x] Record declared support weakening or removal.
- [x] Record withdrawal mode, target, start, end, amount, recovery window, and
      floor-crossing policy.
- [x] If `withdrawal_target = producer_surface`, restrict the positive claim to
      producer-dependence or residue analysis unless source-current basin
      continuation persists in declared fields.
- [x] Record baseline-vs-withdrawn comparison.
- [x] Confirm withdrawal evidence consumes source-current run artifacts.
- [x] Record same-basin continuation result.
- [x] Record support floor result.
- [x] Record coherence floor result.
- [x] Record boundary integrity result.
- [x] Record flux/leakage result.
- [x] Record withdrawal replay result.
- [x] Record withdrawal replay status using the frozen replay/control status
      enum.
- [x] Record hidden support control result.
- [x] Record proxy-only success control result.
- [x] Keep claim ceiling artifact-level and primitive-specific.

Expected artifacts:

```text
outputs/n21_withdrawal_resistance_probe.json
reports/n21_withdrawal_resistance_probe.md
scripts/build_n21_withdrawal_resistance_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_provisional_wr4_withdrawal_candidate_pending_i6
output_digest = 6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36
check_count = 12
failed_checks = []
row_id = n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening
run_artifact_id = n21_i4_withdrawal_resistance_lgrc9v3_packet_support
row_decision = supported
row_decision_scope = supported_for_replay_backed_WR4_candidate_only; I2-required control-backed WR5/WR6 gates remain deferred to I6
wr_ladder_rung = WR4
wr_ladder_rung_status = provisional_pending_iteration6_control_matrix
derived_report_only = false
primitive_claim_allowed = true
final_withdrawal_resistance_supported = false
iteration6_replay_control_matrix_required = true
executed_control_ids = hidden_producer_support_control, proxy_only_success_control, label_only_success_control, post_hoc_trace_construction_control, support_floor_crossing_control, snapshot_replay_control
deferred_controls_to_i6 = semantic_relabel_control, native_support_relabel_control, phase8_relabel_control, withdrawal_schedule_removed_control, hidden_support_margin_control
control_result_statuses = not_run, passed
```

Artifact hashes:

```text
output_json_sha256 = 3fb80e72cc1a739627794ef85f2191637564c04f266b5610e38849bf478b7a26
report_md_sha256 = d1b22ea378b9f6ea301f88527f8993b247637d702bdb1e7fae6a1600de9d1eee
script_py_sha256 = 0c512ee926eb75a48dd79af1049a520db244c332d94545b911c68771074524d1
candidate_artifact_digest = 7c1769fa8c16b5f95da947f3239ca71f69f7edac0638d849413351dc942b4293
runtime_config_digest = a21d7afd3c3623fda8ad1a18f2ca6f39bdbed522a756379e85110ca130b68d90
source_contract_row_digest = db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5
source_digest = e0b228e4142255c183334703a6e5867e2fa606bbc51fc70d8781a994c950687e
trace_digest = 50f14d7b3df6672e5e9ca112a8cb720362466e2bfe16736f5d829fa957b458b4
```

Source-current artifact paths:

```text
baseline_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/baseline_run.json
withdrawn_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_run.json
event_log_or_trace_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawal_trace.json
snapshot_or_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/snapshot_replay.json
duplicate_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_withdrawal_resistance_probe_artifacts/withdrawn_duplicate_replay_run.json
```

Geometric interpretation:

```text
baseline_packet_amount = 0.10
withdrawn_packet_amount = 0.07
withdrawal_amount = 0.03
support_retention_ratio = 0.70
support_packet_amount_floor = 0.06
support_margin = 0.01
center_coherence_floor = 10.05
withdrawn_center_coherence = 10.07
coherence_margin = 0.02
active_degree_floor = 9
withdrawn_active_degree = 9
target_arrival_amount = 0.07
leakage_amount = 0.0
withdrawn_budget_error = 0.0
withdrawn_in_flight_packet_total = 0.0
same_basin_continuation_status = preserved
```

I4 weakens a declared packetized support surface from the support-side
node into the center basin node. Geometrically, the producer removes
`0.03` from a `0.10` packet route while keeping the same center node,
same center basin, same topology signature, same active boundary degree,
and same basin member count. The weakened packet still arrives at the
target as `0.07`, above the declared `0.06` support floor, while center
coherence remains above the declared floor and no leakage or budget error
is recorded.

This is the first positive N21 source-current primitive candidate: the
artifact shows that the same basin can persist under bounded support
weakening in an LGRC9V3 run. It is not final withdrawal-resistance
closeout. The row is provisional WR4 because artifact replay,
snapshot/load replay, and duplicate replay pass. The row decision is
scoped to that replay-backed WR4 candidate only: five I2-required controls
are recorded as `not_run` and explicitly deferred to I6, namely semantic
relabel, native-support relabel, Phase 8 relabel, withdrawal-schedule
removed, and hidden-support-margin controls. They are not treated as
passed in I4, so the full I6 replay/control matrix can still demote or
block the row.

Claim boundary:

```text
artifact-level withdrawal-resistance candidate = allowed provisionally
final withdrawal-resistance support = false
naturalization depth support = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 4-A. Withdrawal Severity And Removal Boundary Probe

- [x] Keep the Iteration 4 producer family fixed.
- [x] Keep the Iteration 4 thresholds fixed.
- [x] Sweep declared support packet amounts across mild weakening, current I4
      weakening, floor, below-floor, strong withdrawal, and full removal.
- [x] Reproduce the current I4 `0.07` support row inside the sweep.
- [x] Record source-current run artifacts for every severity row.
- [x] Record snapshot/load replay and duplicate replay for every severity row.
- [x] Classify above-floor rows as bounded support-weakening candidates only.
- [x] Classify the exact floor row as zero-margin boundary evidence.
- [x] Reject below-floor and full-removal rows when gates fail.
- [x] Add support-necessity or relevance control.
- [x] Confirm the support surface measurably affects source-current geometry.
- [x] Keep support-removal resistance, robust withdrawal resistance, final WR,
      native support, agency, sentience, and Phase 8 claims blocked.

Expected artifacts:

```text
outputs/n21_withdrawal_severity_boundary_probe.json
reports/n21_withdrawal_severity_boundary_probe.md
scripts/build_n21_withdrawal_severity_boundary_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_withdrawal_severity_boundary_mapped_no_removal_overclaim
output_digest = 611de6672537df3a27c5a259fe53c09f302771eaceb1d40fac4284cea08558e8
check_count = 10
failed_checks = []
source_i4_output_digest = 6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36
source_contract_row_digest = db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5
runtime_config_digest = 5a9e8e6c08ad30160af9fb51ce9ef0e9cb5ba0838184b55271e18e773367def8
trace_digest = 77b7cf6c1be1e00b80230dbc1575b85da6cdcc718b48062c37a23acf3b2d8566
boundary_summary_digest = d8a2d786434e4f1f33c701bede82f84a90ae2e19e32a41faef570ab021356c28
artifact_digest = f41e5fa0d9a1df5c9109e794c5dde21bb7f828d9f2c3e93fe8de8c281af9c268
derived_report_only = false
source_current_run_artifacts_consumed = true
support_necessity_or_relevance_control = passed
```

Artifact hashes:

```text
output_json_sha256 = 82072dd08488153361adc6d682f1ded4e3083227ad8d5afc489888a635cb3357
report_md_sha256 = a7f7157c511d5d584a19a883ce34713bcba06699cc14bd98d743e9bf3fe7ba2a
script_py_sha256 = 580707735727ebf183aa53dd985c54637e9e331b5f7a4f0b7b609e5971c5336b
```

Severity sweep record:

```text
baseline_packet_amount = 0.10
support_floor = 0.06
coherence_floor = 10.05

amount 0.09:
  row_decision = supported
  severity_role = positive_margin_withdrawal_candidate
  withdrawal_amount = 0.01
  support_margin = 0.03
  coherence_margin = 0.04
  failure_modes = []

amount 0.07:
  row_decision = supported
  severity_role = positive_margin_withdrawal_candidate
  withdrawal_amount = 0.03
  support_margin = 0.01
  coherence_margin = 0.02
  failure_modes = []

amount 0.06:
  row_decision = partial
  severity_role = floor_boundary_zero_margin
  withdrawal_amount = 0.04
  support_margin = 0.00
  coherence_margin = 0.01
  failure_modes = []

amount 0.05:
  row_decision = rejected
  severity_role = fail_closed_boundary_row
  withdrawal_amount = 0.05
  support_margin = -0.01
  coherence_margin = 0.00
  failure_modes = [support_floor_crossed]

amount 0.03:
  row_decision = rejected
  severity_role = fail_closed_boundary_row
  withdrawal_amount = 0.07
  support_margin = -0.03
  coherence_margin = -0.02
  failure_modes = [support_floor_crossed, coherence_floor_crossed]

amount 0.00:
  row_decision = rejected
  severity_role = fail_closed_boundary_row
  withdrawal_amount = 0.10
  support_margin = -0.06
  coherence_margin = -0.05
  failure_modes = [support_floor_crossed, coherence_floor_crossed]
```

Boundary result:

```text
supported_positive_margin_amounts = [0.09, 0.07]
floor_boundary_amounts = [0.06]
fail_closed_amounts = [0.05, 0.03, 0.00]
max_positive_margin_supported_withdrawal_amount = 0.03
failure_boundary_interval = [0.06, 0.05]
full_removal_status = rejected
full_removal_failure_modes = [support_floor_crossed, coherence_floor_crossed]
bounded_support_weakening_scope_supported = true
support_removal_resistance_supported = false
robust_withdrawal_resistance_supported = false
final_withdrawal_resistance_supported = false
```

Support relevance control:

```text
control_id = support_necessity_or_relevance_control
control_status = passed
baseline_packet_amount = 0.10
removal_packet_amount = 0.00
center_coherence_delta = 0.10
source_coherence_delta = 0.10
packet_count_delta = 1
event_count_delta = 5
```

Geometric interpretation:

I4-A shows that the I4 support surface is not irrelevant. Removing the
surface changes center coherence, source coherence, packet records, and
event trace. Therefore the I4 positive result is not merely same-basin
invariance under a support perturbation that did no work.

The geometric boundary is narrow. The same center basin survives at `0.09`
and `0.07` support packet amounts, with positive support and coherence
margins. At `0.06`, the row is exactly on the declared support floor, so it
is treated as zero-margin boundary evidence rather than a widened positive
claim. At `0.05`, the support floor is crossed even though coherence remains
at the floor. At `0.03` and `0.00`, support and coherence both cross their
floors. Full removal therefore fails closed.

The result refines I4 rather than replacing it:

```text
I4 = provisional WR4 support-weakening candidate at 0.07
I4-A = local severity/removal boundary map

supported = bounded support weakening above the 0.06 floor
not supported = support-removal resistance
not supported = robust or broad withdrawal resistance
```

Claim boundary:

```text
bounded support-weakening scope = supported
support removal resistance = false
robust withdrawal resistance = false
final withdrawal resistance = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 4-B. Withdrawal Transfer And Schedule-Shape Probe

- [x] Keep the Iteration 4/4-A producer family fixed.
- [x] Keep the Iteration 4/4-A thresholds fixed.
- [x] Use matching baseline and withdrawn runs for every transfer variant.
- [x] Reproduce the I4 reference route at `0.10 -> 0.07`.
- [x] Test a distinct support route with the same total weakening.
- [x] Test a delayed schedule with the same total weakening.
- [x] Test a split schedule with the same total weakening.
- [x] Test a mixed route/split schedule with the same total weakening.
- [x] Record source-current run artifacts for every variant.
- [x] Record snapshot/load replay and duplicate replay for every variant.
- [x] Reject route-transfer evidence if it is only a label swap.
- [x] Reject schedule-shape evidence if it is only a prose relabel.
- [x] Confirm threshold policy was not retuned.
- [x] Keep WR5, WR6, final WR, robust withdrawal resistance,
      support-removal resistance, native support, agency, sentience, and Phase 8
      claims blocked.

Expected artifacts:

```text
outputs/n21_withdrawal_transfer_shape_probe.json
reports/n21_withdrawal_transfer_shape_probe.md
scripts/build_n21_withdrawal_transfer_shape_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_withdrawal_transfer_shape_wr4_candidate_pending_i6
output_digest = 8179871ea16bd6243c46e28249c1f1e8f12246158d873763fa9ee5909cc64a1f
check_count = 11
failed_checks = []
source_i4_output_digest = 6d80c4dd915c0c5d2b1f67c2af69881d88ab3d632acf828013389f90c53cfb36
source_i4a_output_digest = 611de6672537df3a27c5a259fe53c09f302771eaceb1d40fac4284cea08558e8
source_contract_row_digest = db8c2f0e93f81971f8b4316dda04c5f556aa0fbda691a8255713d86f209adee5
runtime_config_digest = a4041c73b2c4501259062a983149cf97ba5ee3f82409a233a4d29a80ebaaf97f
trace_digest = 2fc8b5427105461ec31fed6320f9367adad66e453ae1ddd3460621becfae6b0c
transfer_shape_summary_digest = a1621a953409b6246e972ea5eea98d1c6aeea071ad5a6262c421aa7d278c6cd1
artifact_digest = 980c7ef937e1d49fb779ca3ed58dc7a0adaec37c94a707893b0373d190b98e44
derived_report_only = false
source_current_run_artifacts_consumed = true
```

Artifact hashes:

```text
output_json_sha256 = 8e4aacf9f3e0ad371869903a533bcc8f87d2385a036680e14322358d6c95dca3
report_md_sha256 = 17f911697d9dd27a97270ae7263098ff03720cef256d683584724a269fa7d75a
script_py_sha256 = 29535c2dd096b1c068b9e4be22bf7af845d50e0632447abe23841659e3e9b887
```

Variant record:

```text
reference_single_route:
  transfer_role = i4_reference_reproduction
  row_decision = supported
  withdrawn_packet_total = 0.07
  packet_count = 1
  support_margin = 0.01
  coherence_margin = 0.02

alternate_single_route:
  transfer_role = route_transfer_candidate
  row_decision = supported
  route = node 9 -> node 0 on edge 8
  withdrawn_packet_total = 0.07
  packet_count = 1
  support_margin = 0.01
  coherence_margin = 0.02

delayed_single_route:
  transfer_role = schedule_delay_candidate
  row_decision = supported
  route = node 1 -> node 0 on edge 0
  departure_event_time_key = 2.0
  withdrawn_packet_total = 0.07
  packet_count = 1
  support_margin = 0.01
  coherence_margin = 0.02

split_same_route:
  transfer_role = schedule_split_candidate
  row_decision = supported
  route = node 1 -> node 0 on edge 0
  withdrawn_packets = [0.035, 0.035]
  withdrawn_packet_total = 0.07
  packet_count = 2
  support_margin = 0.01
  coherence_margin = 0.02

mixed_route_split:
  transfer_role = route_and_schedule_split_candidate
  row_decision = supported
  routes = node 1 -> node 0 on edge 0; node 9 -> node 0 on edge 8
  withdrawn_packets = [0.035, 0.035]
  withdrawn_packet_total = 0.07
  packet_count = 2
  support_margin = 0.01
  coherence_margin = 0.02
```

Transfer and schedule-shape result:

```text
supported_variant_ids = [
  reference_single_route,
  alternate_single_route,
  delayed_single_route,
  split_same_route,
  mixed_route_split
]
route_transfer_supported = true
schedule_shape_transfer_supported = true
mixed_route_split_supported = true
all_controls_passed = true
bounded_transfer_shape_wr4_candidate_supported = true
WR5 = false
WR6 = false
final_withdrawal_resistance_supported = false
support_removal_resistance_supported = false
robust_withdrawal_resistance_supported = false
```

Controls:

```text
route_transfer_source_current_control = passed
schedule_shape_source_current_control = passed
mixed_route_split_control = passed
threshold_retune_control = passed
```

Geometric interpretation:

I4-B keeps the same `0.10 -> 0.07` withdrawal amount and the same declared
support/coherence/boundary/flux thresholds, but changes the route and packet
schedule shape. Every variant has its own baseline and withdrawn run, so the
comparison is not made by relabeling the I4 row.

The reference row reproduces the I4 route. The alternate route sends the
same total support from node `9` over edge `8` into the center basin instead
of node `1` over edge `0`. The delayed row keeps the I4 route but shifts the
packet time. The split row keeps the I4 route but divides the packet into two
source-current packets. The mixed row divides the support across two source
nodes and two edges. In all cases, the center basin, topology signature,
support floor, coherence floor, boundary degree, flux/budget bounds, and
replay gates are preserved.

This strengthens the future I6 evidence base by showing that the bounded
withdrawal pattern is not confined to the single I4 route and single schedule
shape. It still does not widen I4-A's severity boundary and does not support
support-removal resistance. It remains provisional WR4 transfer/schedule-shape
evidence pending I6 controls and closeout.

I6 should consume I4-B only as bounded transfer/schedule-shape WR4 evidence.
It must not consume I4-B as robust withdrawal resistance, support-removal
resistance, or a widened severity envelope.

Claim boundary:

```text
bounded transfer/schedule-shape WR4 candidate = true
WR5 = false
WR6 = false
final withdrawal resistance = false
robust withdrawal resistance = false
support removal resistance = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 5. Naturalization Depth Probe

- [x] Run bounded naturalization-depth candidate.
- [x] Assign ND rung only from source-backed post-probe evidence.
- [x] Record run artifact ID and artifact digest.
- [x] Record source commit or source digest.
- [x] Record runtime config digest.
- [x] Record source contract row digest.
- [x] Record baseline artifact path.
- [x] Record probe-absent artifact path.
- [x] Record event log or trace path.
- [x] Record snapshot or replay artifact path.
- [x] Confirm `derived_report_only = false`.
- [x] Record original probe/scaffold present in baseline.
- [x] Record original probe/scaffold absent in evaluated run.
- [x] Confirm `probe_absent_runtime_input = true`.
- [x] Confirm `probe_residue_digest_absent = true`.
- [x] Confirm `support_annotation_not_used_as_evidence = true`.
- [x] Confirm `producer_probe_schedule_disabled = true`.
- [x] Record probe-present-vs-probe-absent comparison.
- [x] Confirm naturalization-depth evidence consumes source-current run
      artifacts.
- [x] Record post-probe same-basin continuation result.
- [x] Record post-probe support floor result.
- [x] Record post-probe coherence floor result.
- [x] Record post-probe boundary result.
- [x] Record multi-window replay result.
- [x] Record multi-window replay status using the frozen replay/control status
      enum.
- [x] Record probe residue control result.
- [x] Record support source annotation relabel control result.
- [x] Report naturalization depth as candidate/rung-limited unless an explicit
      `ND0...ND6` rung ladder is defined and tested.
- [x] Keep claim ceiling artifact-level and primitive-specific.

Expected artifacts:

```text
outputs/n21_naturalization_depth_probe.json
reports/n21_naturalization_depth_probe.md
scripts/build_n21_naturalization_depth_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_provisional_nd3_naturalization_candidate_pending_i6
output_digest = 076461e9779b024e0633810be35e78359b8e36cd88bbb9ea655aa8b5c9bf7df2
check_count = 16
failed_checks = []
row_id = n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence
run_artifact_id = n21_i5_naturalization_depth_lgrc9v3_probe_absence
row_decision = supported
nd_ladder_rung = ND3
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
derived_report_only = false
primitive_claim_allowed = true
final_naturalization_depth_supported = false
post_probe_aftereffect_evidence_supported = false
naturalization_depth_candidate_scope = provisional_probe_absent_same_basin_replay_candidate
iteration6_replay_control_matrix_required = true
```

Artifact hashes:

```text
output_json_sha256 = 367b1ca45639a91f313271bc84f52b067f953d7f13e1f1dbea65a10e0c59e45a
report_md_sha256 = c1fa38f96fce1bca766e9bbd1d7819d262943adda45f75aa69723ea2c53c50bf
script_py_sha256 = 9147c1c73ff09f95609d47b5b0ac31c7fe89f9ac2aeb0b29e3596ff4e3a6e450
candidate_artifact_digest = ed286eceffcba380fe02c1e6d926e7272a060e563923878108d2e02b3d233b4b
runtime_config_digest = b4df3ed60904865fdb5035ed4793a8d6e2a0ef092c705e7d47906f8929bb9c87
source_contract_row_digest = 9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda
source_digest = 535b5b6d15fdbcc5d0c96ba7c4ca6e85e23c3e22a5ce4fc6cc49c71b69d268d2
trace_digest = c2e64f269ee53d2775529deb39774f482478f6324b215219beb4e45dfbd9fa9f
state_derivation_digest = 3c20abdbb2725d04edee33b80de74c4652262025e211286b0685cf16019e2423
probe_effect_digest = 6de5940b36f4f2a7073e8200b3fa5e94c2ebb6bcb25162160484a2e51f01b71f
```

Source-current artifact paths:

```text
probe_present_baseline_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_present_baseline_run.json
probe_absent_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_run.json
event_log_or_trace_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/naturalization_trace.json
snapshot_or_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/multi_window_replay.json
duplicate_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_probe_artifacts/probe_absent_duplicate_replay_run.json
```

Probe-absence and geometric record:

```text
baseline_original_probe_packet_amount = 0.04
baseline_original_probe_packet_record_count = 1
probe_absent_original_probe_packet_record_count = 0
probe_absent_event_count = 0
probe_absent_initial_state_source = initial_fixture_state
probe_removed_from_existing_state = false
post_probe_state_carried_into_probe_absent_run = false
baseline_probe_effect_observed = true
center_coherence_delta = 0.04
source_coherence_delta = -0.04
packet_count_delta = 1
replay_kind = static_snapshot_replay
eventful_post_probe_continuation = false
probe_absent_runtime_input = true
probe_residue_digest_absent = true
support_annotation_not_used_as_evidence = true
producer_probe_schedule_disabled = true
post_probe_replay_windows = 3
post_probe_same_basin_continuation_status = preserved
post_probe_support_floor = 9.95
post_probe_support_score = 10.0
post_probe_support_margin = 0.05
post_probe_coherence_floor = 9.95
post_probe_center_coherence = 10.0
post_probe_coherence_margin = 0.05
post_probe_active_degree = 9
post_probe_budget_error = 0.0
post_probe_packet_count = 0
post_probe_in_flight_packet_total = 0.0
declared_multi_window_replay_without_original_probe_scaffold = passed
```

I5 contrasts two source-current LGRC9V3 runs. The baseline run includes
the original packetized probe scaffold: a `0.04` packet from the support
side into the center basin. The baseline probe has a visible geometric
effect: center coherence changes by `+0.04`, source coherence changes by
`-0.04`, packet count increases by `1`, and `5` baseline events are
recorded. The evaluated run disables that original probe schedule and
replays the same initial substrate for three no-probe windows. In the
evaluated run there are no original-probe packet records, no probe-absent
events, no in-flight packet budget, and no support annotation is used as
evidence.

Geometrically, the center basin remains the same basin when the probe is
absent: center node, center basin id, topology signature, active boundary
degree, and basin member count are preserved. Residual support and
coherence remain above the predeclared `9.95` floors with `0.05` margin,
and the replay geometry digest matches across the declared no-probe
multi-window replay.

Important limitation: this is not carried post-probe-aftereffect evidence.
The probe-absent run starts from the declared initial fixture state, not
from the probe-present final snapshot. Therefore the supported scope is
narrower than strong naturalization-depth persistence:

```text
supported = provisional_probe_absent_same_basin_replay_candidate
not_supported = post_probe_aftereffect_persistence
not_supported = general_naturalization_depth
```

This supports only a provisional local `ND3` probe-absent same-basin replay
candidate. It does not support general naturalization depth, native
support, agency, sentience, Phase 8, or ant-ecology implementation. The
I6 replay/control matrix can still demote or block the row before closeout.

Claim boundary:

```text
bounded N21 naturalization-depth candidate = allowed provisionally
final naturalization-depth support = false
post-probe aftereffect persistence = false
general naturalization-depth = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 5-A. Post-Probe State Derivation Persistence Probe

- [x] Run a probe-present baseline that measurably changes source-current
      geometry.
- [x] Checkpoint and digest the probe-present final state.
- [x] Start no-probe replay from the derived post-probe checkpoint.
- [x] Confirm the no-probe replay initial state matches the derived
      post-probe state.
- [x] Separate historical probe provenance from active probe support.
- [x] Confirm historical probe provenance is present and allowed.
- [x] Confirm active probe schedule is disabled.
- [x] Confirm active probe queue is empty.
- [x] Confirm in-flight probe budget is zero.
- [x] Confirm no active probe packet is replayed as support.
- [x] Confirm probe support is not used as evidence.
- [x] Record reset-to-initial/no-probe comparison against I5.
- [x] Record same-basin continuation result.
- [x] Record support, coherence, boundary, and flux gates.
- [x] Keep `nd_ladder_rung = ND3`.
- [x] Record `nd_evidence_variant = post_probe_derived_state`.
- [x] Keep ND4/ND5 and final naturalization-depth support pending I6/I7.

Expected artifacts:

```text
outputs/n21_naturalization_depth_post_probe_derivation.json
reports/n21_naturalization_depth_post_probe_derivation.md
scripts/build_n21_naturalization_depth_post_probe_derivation.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_provisional_post_probe_derived_nd3_candidate_pending_i6
output_digest = 311440952d246a6fa1748f3a215ae8d8513c4bd8c29eb0fcce346ecf76060dc2
check_count = 15
failed_checks = []
row_id = n21_i5a_row_01_post_probe_derived_state_persistence
run_artifact_id = n21_i5a_naturalization_depth_post_probe_derivation
row_decision = supported
nd_ladder_rung = ND3
nd_evidence_variant = post_probe_derived_state
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
derived_report_only = false
primitive_claim_allowed = true
final_naturalization_depth_supported = false
post_probe_aftereffect_evidence_supported = true
general_naturalization_depth_supported = false
iteration6_replay_control_matrix_required = true
```

Interpretation note: the generated `post_probe_aftereffect_evidence_supported`
field means only geometric post-probe-derived state persistence. It records
that a source-current probe-present final snapshot differed from the initial
fixture and then persisted without active probe support. It does not mean
learning, memory, agency, semantic naturalization, native support, or final
naturalization depth. The stricter closeout wording is
`post_probe_derived_state_persistence_supported`.

Artifact hashes:

```text
output_json_sha256 = ecbc42f3dd722f2565325b5b4105e42caddd2a3a768d09c2e47e92507c999c07
report_md_sha256 = a94d6147a98dcbfaf693a23a53193b6540b1ca6c0a801529431499fb0ea85030
script_py_sha256 = 1774e36748363c8e86ca9a1aa849e5d83a9401d5f33eef998cd053999642c69a
candidate_artifact_digest = 4efad21fa827575822ae29734fee7fd5bfb3b93de766d8faac4b30e0f4af004a
runtime_config_digest = 326695d9f83e1f529e590b092c1b0910d17bab49981c4e9f9c757a0aad933c1c
source_contract_row_digest = 9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda
source_digest = 681f287e309509ce33c86bb492e59e4a94c0890164ba03b95386206c399e2ffc
trace_digest = 1b266999adf837529b54192df04db93ed3258d771d7b8c891b83b1898f510526
state_derivation_digest = 1440a81727bea11cc9132322360f421184b115273b6c57ce43f05d7937d948ac
probe_effect_digest = 8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a
```

Source-current artifact paths:

```text
probe_present_baseline_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/probe_present_baseline_run.json
post_probe_derived_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derived_run.json
event_log_or_trace_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derivation_trace.json
snapshot_or_replay_artifact_path = experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/outputs/n21_naturalization_depth_post_probe_derivation_artifacts/post_probe_derivation_replay.json
```

Derivation and geometric record:

```text
probe_effect_detected = true
probe_event_count = 5
center_coherence_delta = 0.04
source_coherence_delta = -0.04
packet_count_delta = 1
post_probe_state_derivation_source = probe_present_final_snapshot
probe_absent_initial_state_matches_derived_post_probe_state = true
post_probe_state_carried_into_probe_absent_run = true
historical_probe_provenance_present = true
historical_probe_provenance_allowed = true
active_probe_schedule_disabled = true
active_probe_queue_empty = true
in_flight_probe_budget = 0.0
active_probe_packet_records_in_replay = 0
probe_support_not_used_as_evidence = true
derived_state_differs_from_initial_no_probe_state = true
post_probe_same_basin_continuation_status = preserved
post_probe_support_floor = 9.95
post_probe_support_score = 10.0
post_probe_coherence_floor = 9.95
post_probe_center_coherence = 10.04
post_probe_active_degree = 9
post_probe_budget_error = 0.0
replay_kind = static_post_probe_snapshot_replay
eventful_post_probe_continuation = false
```

5-A is stronger than I5 because the no-probe replay starts from the
probe-present final snapshot rather than from the initial fixture. The
probe-present baseline produces a measurable source-current state change,
then the derived post-probe checkpoint is used as the no-probe replay
initial state. The historical probe packet remains as provenance, but
active probe support is not doing the work: no active probe schedule is
enabled, the queue is empty, in-flight budget is zero, and no active probe
packet is replayed.

Geometrically, the post-probe-derived state preserves the same center
basin, topology signature, active boundary degree, support floor,
coherence floor, and budget surface across the no-active-probe replay.
This supports only a provisional `ND3` post-probe-derived state variant.
It does not support `ND4`, `ND5`, final naturalization depth, native
support, agency, sentience, Phase 8, or ant-ecology implementation.

Claim boundary:

```text
post-probe-derived ND3 candidate = allowed provisionally
ND4 = false
ND5 = false
final naturalization-depth support = false
general naturalization-depth = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 5-B. Eventful Post-Probe Continuation Probe

- [x] Start from a probe-present run that measurably changes source-current
      geometry.
- [x] Start the evaluated run from the probe-present final snapshot.
- [x] Disable the original probe support schedule.
- [x] Add a distinct non-original post-probe runtime event.
- [x] Confirm the original probe route is not reintroduced.
- [x] Confirm the eventful post-probe run emits source-current events.
- [x] Confirm same-basin continuation after the eventful window.
- [x] Confirm support, coherence, boundary, and flux gates remain preserved.
- [x] Confirm snapshot/load replay and duplicate eventful replay pass.
- [x] Record eventful controls and keep them fail-closed.
- [x] Keep `nd_ladder_rung = ND3`.
- [x] Record `nd_evidence_variant = eventful_post_probe_derived_state`.
- [x] Keep ND4/ND5, final naturalization-depth, native support, agency,
      sentience, Phase 8, and ant-ecology claims blocked.

Expected artifacts:

```text
outputs/n21_naturalization_depth_eventful_post_probe.json
reports/n21_naturalization_depth_eventful_post_probe.md
scripts/build_n21_naturalization_depth_eventful_post_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_provisional_eventful_post_probe_derived_nd3_candidate_pending_i6
output_digest = 5cdb24a076ae5a4e814a523663ad460754937f3650f3359da86d3c9f5147cec6
check_count = 15
failed_checks = []
row_id = n21_i5b_row_01_eventful_post_probe_continuation
run_artifact_id = n21_i5b_naturalization_depth_eventful_post_probe
row_decision = supported
nd_ladder_rung = ND3
nd_evidence_variant = eventful_post_probe_derived_state
nd_ladder_rung_status = provisional_pending_iteration6_control_matrix
derived_report_only = false
primitive_claim_allowed = true
eventful_post_probe_derived_candidate_supported = true
final_naturalization_depth_supported = false
ND4 = false
ND5 = false
general_naturalization_depth_supported = false
iteration6_replay_control_matrix_required = true
```

Artifact hashes:

```text
output_json_sha256 = fa367d72356fe60f68ebcb961effe72129c1a7bbbde99a216ac83804fa8c8b7e
report_md_sha256 = b11affb3563656cd1b4f76d62b02b3eeb6893ee74bc35390e8f389bf37d398c5
script_py_sha256 = c7095235795ad498fd51caf854891c6711bed717f01fb1521ba46eab011ea42d
candidate_artifact_digest = 49333fd071bb993a1937539747f8dac70a9ced42b14e94334208d60f15680610
runtime_config_digest = db88d29ba976df09047542b803d82ee0e6d6a354ef6298b819c3e8093c87b447
source_contract_row_digest = 9b12a96f64a9a2da181437389cd1315820b6f4c817868590785ba951bac5afda
source_digest = aaac3d9db443308d38ac85d8158c2760847edfe8fb28ba264274b927ab478732
source_i5_output_digest = 076461e9779b024e0633810be35e78359b8e36cd88bbb9ea655aa8b5c9bf7df2
source_i5a_output_digest = 311440952d246a6fa1748f3a215ae8d8513c4bd8c29eb0fcce346ecf76060dc2
trace_digest = f91e00df832a7a74d1bd0a49e04e98a0bbb6dd195af2564590c71bf1b9727894
state_derivation_digest = d13556c8089437df94c8010b611615a6d3a0568287a9435b62c6158afaec4dd3
probe_effect_digest = 8f3ed3b6152d315772fbe0e1dab9c09ccb354cfbd09498ce2c99701d3c77ff3a
```

Eventful post-probe record:

```text
challenge_packet:
  source_node_id = 0
  target_node_id = 2
  edge_id = 1
  amount = 0.01
  departure_event_time_key = 2.0
  scheduler_event_index = 2

eventful_post_probe_event_count = 5
center_coherence_delta_after_challenge = -0.009999999999999787
original_probe_route_reused = false
active_original_probe_packet_records_in_eventful_window = 0
active_original_probe_schedule_disabled = true
active_probe_queue_empty = true
in_flight_probe_budget = 0.0
support_floor_result = preserved
coherence_floor_result = preserved
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
replay_result_status = passed
control_result_statuses = [passed]
```

Controls:

```text
probe_effect_absent_control = passed
post_probe_state_derivation_control = passed
eventful_continuation_control = passed
original_probe_reintroduction_control = passed
hidden_producer_support_control = passed
support_annotation_relabel_control = passed
post_hoc_trace_construction_control = passed
eventful_replay_control = passed
```

Geometric interpretation:

5-B strengthens 5-A by replacing static post-probe snapshot replay with an
eventful post-probe continuation window. The original probe first changes the
state, then the evaluated run starts from that probe-present final snapshot
with the original probe support disabled. The eventful window schedules a
new, non-original challenge packet from center node `0` outward to neighbor
node `2` over edge `1`. This slightly weakens the center basin instead of
reapplying the original support probe.

The center coherence moves downward by about `0.01`, but the same center
basin, support floor, coherence floor, boundary degree, and flux/budget gates
remain preserved. The original probe packet remains only as historical
provenance: no new original-probe packet is introduced during the eventful
window. Duplicate eventful replay is stable.

The result is stronger than 5-A because it is no longer only static
post-probe-derived persistence:

```text
I5 = no-probe replay from initial fixture
5-A = probe-present final state -> active probe removed -> static
      post-probe-derived replay
5-B = probe-present final state -> active probe removed -> distinct
      non-original eventful challenge -> same-basin continuation
```

The claim remains bounded:

```text
eventful post-probe-derived ND3 candidate = allowed provisionally
ND4 = false
ND5 = false
final naturalization-depth support = false
general naturalization-depth = false
native support = false
agency = false
sentience = false
Phase 8 implementation = false
ant-ecology implementation = false
```

Validation record:

```text
script_compile = passed
idempotency_rerun = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 6. Replay And Control Matrix

- [x] Run artifact-only replay.
- [x] Run snapshot/load replay.
- [x] Run duplicate replay.
- [x] Run order-inversion control.
- [x] Run label-only continuation control.
- [x] Run proxy-only success control.
- [x] Run hidden producer support control.
- [x] Run post-hoc trace construction control.
- [x] Run withdrawal schedule removed control.
- [x] Run support floor crossing control.
- [x] Run probe-present-only control.
- [x] Run probe residue control.
- [x] Run support source annotation relabel control.
- [x] Run native support relabel control.
- [x] Run semantic agency/sentience relabel control.
- [x] Run Phase 8 relabel control.
- [x] Record every required replay/control status as `passed`,
      `failed_closed`, `failed_open`, `not_run`, or `not_applicable`.
- [x] Confirm negative controls fail closed as expected.
- [x] Confirm controls consume or replay the same run artifacts and do not
      construct success post-hoc.
- [x] Confirm controls can demote or block WR/ND ladder rungs when they fail.
- [x] Confirm any required replay/control with status `not_run` blocks the rung
      that depends on it.
- [x] Consume I4 reference support-weakening WR4 row.
- [x] Consume I4-A positive severity rows.
- [x] Consume I4-A floor-boundary and fail-closed rows as boundary evidence.
- [x] Consume I4-B transfer/schedule-shape rows only as bounded WR4
      candidates, not as robust withdrawal or support-removal evidence.
- [x] Consume I5 no-probe initial-fixture ND3 row.
- [x] Consume I5-A post-probe-derived static ND3 row.
- [x] Consume I5-B eventful post-probe-derived ND3 row.
- [x] For every consumed row, record `candidate_id`, `source_iteration`,
      `source_output_digest`, `control_statuses`, `replay_statuses`,
      `demoted_rung_if_any`, `final_consumable_rung`, and
      `i6_consumable_rung`.
- [x] Assign final WR/ND rungs only after I6 control results.

Expected artifacts:

```text
outputs/n21_replay_and_control_matrix.json
reports/n21_replay_and_control_matrix.md
scripts/build_n21_replay_and_control_matrix.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_replay_control_matrix_consumed_all_candidates_no_closeout
output_digest = d4b25c36f84d0300dd7a41f19cbdcfe47d771281ba9a25fbac30b16d346b941f
check_count = 15
failed_checks = []
candidate_row_count = 15
wr_candidate_rows_consumed = 12
nd_candidate_rows_consumed = 3
wr5_consumable_rows = 8
wr_floor_boundary_rows_consumed = 1
wr_rejected_boundary_rows_consumed = 3
nd3_consumable_rows = 1
nd4_consumable_rows = 2
failed_open_controls = 0
failed_open_replays = 0
not_run_controls = 0
not_run_replays = 0
all_artifact_paths_exist = true
all_artifact_sha256_match_file_contents = true
no_absolute_paths = true
final_withdrawal_resistance_supported = false
final_naturalization_depth_supported = false
final_closeout_pending_iteration7 = true
ready_for_iteration7_closeout = true
```

Artifact hashes:

```text
output_json_sha256 = c06bcc82fcee643d437a942e32fe20d105264fd6c0a7d3a77dd9f33b2045f63e
report_md_sha256 = 989ba81afe5385677836a052161326f8665cef242e46e1968238813d06b46aef
script_py_sha256 = 267fb686653d9e01de1e9a742a863c7f72fba8783607e9a2305d22a0fd4f7164
```

Status and field semantics:

```text
final_consumable_rung = legacy plan-required field; read as I6-consumable by I7,
not closeout-final
i6_consumable_rung = preferred closeout-facing field name

passed = positive required condition passed for the row's declared scope
failed_closed = false-positive claim path was rejected; candidate may be retained
failed_open = false-positive claim path passed when it should not; candidate invalid
not_run = required status was not executed; dependent rung is blocked
not_applicable = control or replay mode is outside the row's declared scope
```

Replay requirement map:

```text
WR rows require:
  artifact_only_replay
  snapshot_load_replay
  duplicate_replay

I5 ND row requires:
  artifact_only_replay
  declared_multi_window_replay_without_original_probe_scaffold
  snapshot_load_replay
  duplicate_replay

I5-A ND row requires:
  artifact_only_replay
  declared_multi_window_replay_without_original_probe_scaffold
  snapshot_load_replay
  duplicate_replay if declared by source row, otherwise not_applicable with scope reason

I5-B ND row requires:
  artifact_only_replay
  declared_multi_window_replay_without_original_probe_scaffold
  snapshot_load_replay
  duplicate_replay
```

Consumed row effects:

```text
I4 reference support-weakening WR4 row:
  i6_consumable_rung = WR5

I4-A positive severity rows:
  n21_i4a_row_amount_0_09 -> WR5
  n21_i4a_row_amount_0_07 -> WR5

I4-A boundary/fail-closed rows:
  n21_i4a_row_amount_0_06 -> WR3_floor_boundary_evidence
  n21_i4a_row_amount_0_05 -> rejected boundary evidence
  n21_i4a_row_amount_0_03 -> rejected boundary evidence
  n21_i4a_row_amount_0_00 -> rejected boundary evidence

I4-B transfer/schedule-shape rows:
  reference_single_route -> WR5
  alternate_single_route -> WR5
  delayed_single_route -> WR5
  split_same_route -> WR5
  mixed_route_split -> WR5

I5 no-probe initial-fixture row:
  i6_consumable_rung = ND3_initial_fixture_no_probe_replay_candidate
  demotion = not_promoted_beyond_ND3_initial_fixture_scope

I5-A post-probe-derived static row:
  i6_consumable_rung = ND4

I5-B eventful post-probe-derived row:
  i6_consumable_rung = ND4
```

Evidence/support split:

```text
I4-A floor and rejected boundary rows:
  evidence_claim_allowed = true
  positive_primitive_support_allowed = false
  primitive_claim_allowed = false

Positive WR/ND rows:
  evidence_claim_allowed = true
  positive_primitive_support_allowed = true
```

Interpretation:

I6 is a control matrix, not final closeout. It consumes every provisional
candidate family from I4 through I5-B and records no `failed_open` or
`not_run` replay/control statuses. The positive WR rows become consumable as
control-backed `WR5` candidates, while the I4-A floor and below-floor rows
remain boundary/fail-closed evidence rather than support-removal or robust
withdrawal evidence.

The naturalization-depth side now has a clean split. I5 remains only an
`ND3` no-probe initial-fixture baseline because it did not start from a
probe-present final state. I5-A and I5-B become `ND4`-consumable because
post-probe derivation, active probe residue, hidden support,
support-annotation relabel, post-hoc trace, and unsafe relabel controls pass
or fail closed within scope. They do not support `ND5`, `ND6`, final
naturalization depth, native support, agency, sentience, Phase 8, or
ant-ecology implementation.

Validation record:

```text
script_compile = passed
producer_run = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Iteration 7. Closeout And N22 Handoff

- [x] Classify withdrawal-resistance result.
- [x] Record final WR ladder rung.
- [x] Classify naturalization-depth result.
- [x] Record final ND ladder rung.
- [x] Record final N21-C closeout ladder rung.
- [x] Record exact WR status enum.
- [x] Record exact ND status enum.
- [x] Record remaining producer residue.
- [x] Record remaining naturalization debt.
- [x] Record final primitive claim ceiling.
- [x] Record unsafe claim blockers.
- [x] Confirm agency, native support, sentience, Phase 8, and ant-ecology
      implementation remain blocked.
- [x] Confirm `src_diff_empty`.
- [x] Record N22 handoff for susceptibility update / durable geometry
      modification.

Expected artifacts:

```text
outputs/n21_closeout_and_n22_handoff.json
reports/n21_closeout_and_n22_handoff.md
scripts/build_n21_closeout_and_n22_handoff.py
```

Implementation record:

```text
status = passed
acceptance_state = closed_n21_bounded_wr_nd_candidate_and_n22_handoff
output_digest = dce76d6bd2f9ebda65111c1324e2a51f0553e428ae1675a22ff6dcc36efb7e10
check_count = 12
failed_checks = []
source_i6_output_digest = d4b25c36f84d0300dd7a41f19cbdcfe47d771281ba9a25fbac30b16d346b941f
source_n20_i5_output_digest = 6a1975e6811c6990ae882d4e5b59233c08784909ddbef823706cad31b61a3bb5
ready_for_n22 = true
src_diff_empty = true
no_absolute_paths = true
```

Artifact hashes:

```text
output_json_sha256 = 91e7799c1a75ff2839cd5c64b0ca89ba584e8f1e69395f03b69f3565791fd47d
report_md_sha256 = 80ec12366b4cc7e1b3cbc52ef5c697660613af4f4d72e8229e5354888ffd5977
script_py_sha256 = d084b4333bf616926fd7373fa99a1021ea7ebd6d01bae4bdeb4846c1778f11e4
```

Closeout classification:

```text
withdrawal_resistance_status = withdrawal_resistance_supported_artifact_level_candidate
withdrawal_resistance_ladder_rung = WR6
source_backed_i6_consumable_rung = WR5

naturalization_depth_status = naturalization_depth_supported_bounded_N21_candidate
naturalization_depth_ladder_rung = ND5
source_backed_i6_consumable_rungs = [
  ND3_initial_fixture_no_probe_replay_candidate,
  ND4
]

n21_closeout_status = n22_ready_bounded_primitive_evidence
n21_closeout_ladder_rung = N21-C6
final_supported_status = bounded_artifact_level_withdrawal_and_naturalization_candidate
final_claim_ceiling = bounded artifact-level WR6 withdrawal candidate plus bounded
  N21-local ND5 naturalization-depth candidate; no agency, native support,
  sentience, Phase 8, or ant-ecology implementation
```

Withdrawal-resistance closeout:

```text
wr5_consumable_row_count = 8
floor_boundary_row = n21_i4a_row_amount_0_06
below_floor_or_removal_rejections = [
  n21_i4a_row_amount_0_05,
  n21_i4a_row_amount_0_03,
  n21_i4a_row_amount_0_00
]

support-removal resistance = false
robust withdrawal resistance = false
general withdrawal resistance = false
native support = false
agency = false
```

I7 closes WR as `WR6` because I6 supplies source-backed, replay/control-clean
`WR5` consumable rows and I7 records the remaining producer residue,
naturalization debt, claim ceiling, unsafe blockers, and source-clean closeout
state. The WR6 result remains bounded to artifact-level withdrawal evidence.
It does not upgrade the zero-margin floor row, below-floor rows, or full-removal
row into support-removal resistance.

Naturalization-depth closeout:

```text
nd3_consumable_row_count = 1
nd4_consumable_row_count = 2
static_post_probe_row = n21_i5a_row_01_post_probe_derived_state_persistence
eventful_post_probe_row = n21_i5b_row_01_eventful_post_probe_continuation

ND6 = false
general naturalization depth = false
native support = false
agency = false
sentience = false
```

I7 closes ND as a bounded N21-local `ND5` candidate. I5 remains only the
initial-fixture no-probe `ND3` baseline. I5-A and I5-B remain the stronger
post-probe-derived `ND4` consumable rows from I6. I7 records
producer/debt boundedness and claim hygiene, so the local closeout can report
`ND5` while keeping `ND6`, general naturalization depth, native support,
agency, sentience, Phase 8, and ant-ecology implementation blocked.

Remaining producer residue and naturalization debt:

```text
withdrawal_resistance producer residue:
  withdrawal_resistance.declared_withdrawal_schedule
  withdrawal_resistance.withdrawal_amount_policy
  withdrawal_resistance.pass_fail_threshold_label

withdrawal_resistance naturalization debt:
  withdrawal_resistance.source_current_support_withdrawal_surface
  withdrawal_resistance.producer_independent_withdrawal_replay
  withdrawal_resistance.native_support_decay_owner

naturalization_depth producer residue:
  naturalization_depth.naturalization_depth_score_formula
  naturalization_depth.support_source_annotation
  naturalization_depth.depth_rank_label

naturalization_depth naturalization debt:
  naturalization_depth.source_current_producer_removal_observation
  naturalization_depth.multi_window_without_probe_replay
  naturalization_depth.naturalization_depth_budget_surface

n22_susceptibility_update producer residue:
  susceptibility_update.route_update_rule
  susceptibility_update.reinforcement_schedule
  susceptibility_update.learning_label

n22_susceptibility_update naturalization debt:
  susceptibility_update.source_current_route_conditioned_state_mutation
  susceptibility_update.peer_route_same_budget_comparison
  susceptibility_update.proxy_free_susceptibility_policy
```

Unsafe claim blockers:

```text
agency = false
choice = false
willpower = false
semantic action = false
semantic perception = false
semantic goal ownership = false
semantic intention = false
selfhood = false
identity acceptance = false
native support = false
Phase 8 implementation = false
sentience = false
consciousness = false
organism/life = false
native ant agency = false
native colony agency = false
unrestricted autonomy = false
ant ecology implementation = false
support-removal resistance = false
robust withdrawal resistance = false
general naturalization depth = false
ND6 naturalization closeout = false
```

N22 handoff:

```text
target_primitive = susceptibility_update
target_experiment = N22
source_contract_row = n20_i5_row_03_susceptibility_update
required_n22_inputs = [
  susceptibility_fields,
  replay_requirement,
  durable_geometry_modification_controls,
  AP4_gap_dependency_if_route_conditioned,
  AP5_gap_dependency_if_proxy_conditioned
]
```

N22 must test susceptibility update / durable geometry modification with new
source-backed durable geometry deltas. N21 can be consumed only as bounded
becoming-primitive context. N21 evidence cannot directly satisfy N22's
susceptibility update primitive, cannot backfill AP4/AP5 NAT4 gaps, and cannot
turn producer-mediated route updates, reinforcement schedules, or learning
labels into substrate-carried evidence.

Validation record:

```text
script_compile = passed
producer_run = passed
jq_failed_checks_empty = passed
idempotency_rerun = passed
all_n21_scripts_compile = passed
git_diff_check = passed
src_diff_empty = true
absolute_path_scan = passed
```

## Closeout Requirement

N21 closeout must answer:

```text
Did withdrawal resistance receive source-backed artifact-level primitive
candidate support?

Did naturalization depth receive source-backed artifact-level primitive
candidate or rung-limited support?

Which WR, ND, and N21-C rungs were source-backed, and which stronger rungs
remained blocked?

Which producer-mediated or naturalization-debt fields remain unresolved?

Did all unsafe relabels stay blocked?
```
