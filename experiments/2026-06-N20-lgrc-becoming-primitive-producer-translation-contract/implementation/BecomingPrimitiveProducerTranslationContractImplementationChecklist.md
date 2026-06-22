# N20 Becoming-Primitive Producer Translation Contract Implementation Checklist

## Initialization

- [x] Create `experiment-N20` branch.
- [x] Create N20 experiment directory.
- [x] Add top-level N20 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N20 scoped as contract/schema work only.
- [x] Confirm N20 does not open primitive evidence, agency, Phase 8, or native
      support.
- [x] Add explicit downstream contract-enforceability hypothesis.

## Global Rules

- [ ] Use source IDs, titles, and relative paths only.
- [ ] Confirm generated records contain no local absolute paths.
- [ ] Treat Arc of Becoming as method, not evidence shortcut.
- [ ] Treat agency essays as diagnostic vocabulary, not proof.
- [ ] Treat `Sentience as Read-Back` as boundary-only.
- [ ] Carry forward N19 AP4/N14 NAT4 evidence gap.
- [ ] Carry forward N19 AP5/N15 NAT4 evidence gap.
- [ ] Keep N29 as the first formal agentic-ecology bridge.
- [ ] Do not write ant-ecology implementation specs in N20.
- [ ] Include the N20 invariant block in every generated artifact.
- [ ] Do not modify `src/*`.
- [ ] Force unsafe claim flags false in every row.
- [ ] Reject native-support claims unless a separate Phase 8 implementation
      exists and validates them.
- [ ] Enforce that later experiments cannot redefine N20 basin signature,
      continuation condition, proxy-only success, or producer-residue
      classification in order to pass.

## Iteration 1. Source And Method Inventory

- [x] Build N20 source/method inventory.
- [x] Record N19 closeout as current implementation boundary.
- [x] Record N20-N29 roadmap as experiment arc source.
- [x] Record Arc of Becoming method roles.
- [x] Record agency essay diagnostic roles.
- [x] Record `Sentience as Read-Back` as boundary-only.
- [x] Record source consumption rules.
- [x] Confirm direct primitive evidence is not opened.
- [x] Confirm agency, Phase 8, native support, and sentience remain unopened.

Expected artifacts:

```text
outputs/n20_source_method_inventory.json
reports/n20_source_method_inventory.md
scripts/build_n20_source_method_inventory.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_source_method_inventory_no_primitive_evidence
artifact = outputs/n20_source_method_inventory.json
report = reports/n20_source_method_inventory.md
script = scripts/build_n20_source_method_inventory.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_source_method_inventory.py
row_count = 13
output_digest = 07a827ef3cade00882e9b04f53cadea75ca277df8ec12e04e4db60b99b0e0aa3
artifact_sha256 = 42ae9bbdb700346fc49098e58fb2f9251b288e21a7771852ac84ac0f7780ed07
report_sha256 = e34d78b4fdb104131711bb5b54c9c020ab867540d5b614f1b4e94f1fa0b31ffc
script_sha256 = 795a78c167c09ddf46b56307ec4ea638638f2930a0695b166adc5b5b13e16b38
failed_checks = []
primitive_evidence_opened = false
primitive_rows_classified = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
ap4_gap_carried_forward = true
ap5_gap_carried_forward = true
ready_for_iteration_2_schema = true
```

Iteration 1 records source and method boundaries only. N19 is consumed as the
current implementation/native-readiness boundary, with AP4/N14 and AP5/N15
NAT4 gaps carried forward. The Arc of Becoming rows are method-only, the agency
essay rows are diagnostic-vocabulary or boundary-only, `Sentience as Read-Back`
is boundary-only, and the agentic ecology project remains future application
context until N29.

Post-review double-check record:

```text
N12-N18 rows remain historical prerequisite context only = true
N19 remains current implementation/classification boundary = true
all 13 rows have may_consume_as and must_not_consume_as = true
unsafe claim flags false per row = true
Arc rows method-only = true
agency essays diagnostic-vocabulary or boundary-only = true
Sentience as Read-Back boundary-only = true
agentic ecology future context only until N29 = true
primitive evidence opened = false
```

The I1 AP4/AP5 gap map remains the source-boundary map. Post-review alignment
keeps the plan-level `gap`, `blocked_relabels`, and `affected_primitives`
values exact, carries N19 `best_current_evidence` forward, reads each source
experiment from N19 data, and moves extra conservative relabel blockers into
`source_specific_blockers`. Conditional dependency expansion is frozen in I2
rather than backfilled into I1, so I1 stays an inventory artifact and I2
carries the stricter schema rule.

## Iteration 2. Translation Schema Freeze

- [x] Freeze becoming primitive row schema.
- [x] Freeze producer definition.
- [x] Freeze variable classification enum.
- [x] Freeze naturalization debt subtype enum.
- [x] Freeze native function descriptor schema as bounded continuation only.
- [x] Freeze `continuation_function_descriptor` as the preferred schema label.
- [x] Freeze proxy metric schema.
- [x] Freeze support/scaffold declaration schema.
- [x] Freeze same-basin continuation schema.
- [x] Freeze `contract_status` enum.
- [x] Freeze `row_decision` enum.
- [x] Freeze unsafe claim flags.
- [x] Confirm no primitive row is classified before schema freeze.

Expected artifacts:

```text
outputs/n20_translation_schema_v1.json
reports/n20_translation_schema_v1.md
scripts/build_n20_translation_schema_v1.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_translation_schema_frozen_no_primitive_evidence
artifact = outputs/n20_translation_schema_v1.json
report = reports/n20_translation_schema_v1.md
script = scripts/build_n20_translation_schema_v1.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_translation_schema_v1.py
output_digest = c0cf2a1990aa0ce302ebe52c0bf8d2d8ada695c8b812d2fd3abb78b9ffc935ef
artifact_sha256 = c36c5ea5425535edee76aad5047377b50a15c259f1341baccdac76652ecc6875
report_sha256 = 39081a57f5399bbdd637f37f104ced290cc38aa934d497073c7434db0588b5b2
script_sha256 = a8e746e6fd1661a412fc34b9bb9cefded313bc7e37cf8451e210c046c682b810
source_inventory_output_digest = 07a827ef3cade00882e9b04f53cadea75ca277df8ec12e04e4db60b99b0e0aa3
source_inventory_sha256 = 42ae9bbdb700346fc49098e58fb2f9251b288e21a7771852ac84ac0f7780ed07
failed_checks = []
candidate_rows_classified = false
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
```

Iteration 2 freezes schema and controls only. It preserves the rule:

```text
N12-N18 = historical prerequisite context
N19 = current classification boundary
```

It also freezes the rule that diagnostic vocabulary may define fields and
controls, but cannot satisfy evidence gates. The AP4/AP5 gap schema carries the
I1 required dependencies forward and adds conditional dependencies:

```text
AP4 affects configuration_substrate_transfer if route-conditioned selection is
part of transfer.

AP5 affects live_continuation_collapse if proxy or target formation participates
in branch valuation.
```

Post-review double-check record:

```text
contract_status_complete_gate_hard_to_earn = true
all_complete_requires_have_contract_status_mapping = true
variable_classification_and_debt_subtype_failures_have_contract_status_mapping = true
complete_requires = producer_residue_classification,
                    continuation_function_descriptor,
                    proxy_metric_definition,
                    support_scaffold_declaration,
                    same_basin_continuation_rule,
                    minimum_controls,
                    claim_ceiling,
                    unsafe_claim_flags
variable_field_partition_rule_frozen = true
blocked_relabel_is_variable_classification = true
diagnostic_vocabulary_cannot_satisfy_evidence_gates = true
AP4/AP5 dependencies are row-local = true
N12-N18 historical / N19 current boundary = true
all primitives have N21-N28 handoff targets = true
primitive evidence opened = false
```

## Iteration 3. Producer Residue And Naturalization Debt Ledger

- [ ] Build producer residue ledger.
- [ ] Build naturalization debt ledger.
- [ ] Assign exactly one variable classification per variable.
- [ ] Separate substrate-carried fields from producer-mediated fields.
- [ ] Mark blocked relabel fields explicitly.
- [ ] Record AP4/AP5 gap dependencies.
- [ ] Record naturalization debt subtype for each naturalization-debt field.
- [ ] Confirm each variable receives exactly one classification.
- [ ] Confirm later experiments cannot treat producer-mediated success as native
      support.

Expected artifacts:

```text
outputs/n20_producer_residue_ledger.json
reports/n20_producer_residue_ledger.md
scripts/build_n20_producer_residue_ledger.py
```

## Iteration 4. Continuation Function / Proxy / Scaffold Contract

- [ ] Build continuation function descriptor contract.
- [ ] Build proxy metric definition contract.
- [ ] Build support/scaffold declaration contract.
- [ ] Define proxy-only success blockers.
- [ ] Confirm continuation function descriptor stays geometric and bounded.
- [ ] Confirm proxy improvement cannot replace basin continuation.
- [ ] Confirm semantic function, goal, or intention labels remain blocked.
- [ ] Confirm every primitive declares proxy-only success blockers.

Expected artifacts:

```text
outputs/n20_native_function_proxy_contract.json
reports/n20_native_function_proxy_contract.md
scripts/build_n20_native_function_proxy_contract.py
```

## Iteration 5. Same-Basin Continuation And Control Contract

- [ ] Define same-basin continuation criteria.
- [ ] Define allowed drift.
- [ ] Define support/coherence floors.
- [ ] Define boundary integrity and flux balance criteria.
- [ ] Define replay requirements.
- [ ] Define label-only continuation control.
- [ ] Define proxy-only success control.
- [ ] Define hidden producer support control.
- [ ] Define semantic overclaim controls.
- [ ] Define minimum shared control template for all primitive rows.
- [ ] Define primitive dependency map for N21-N28.
- [ ] Record medium debt as deferred until N28/N29.

Expected artifacts:

```text
outputs/n20_same_basin_continuation_contract.json
reports/n20_same_basin_continuation_contract.md
scripts/build_n20_same_basin_continuation_contract.py
```

## Iteration 6. Closeout And N21 Handoff

- [ ] Close N20 as a contract experiment.
- [ ] Confirm primitive evidence remains unopened.
- [ ] Confirm agency remains unopened.
- [ ] Confirm Phase 8 remains unopened.
- [ ] Confirm native support remains unopened.
- [ ] Confirm sentience remains unopened.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Record N21 withdrawal-resistance handoff inputs.
- [ ] Record N21 naturalization-depth handoff inputs.
- [ ] Record N21 readiness gate and blockers.

Expected artifacts:

```text
outputs/n20_closeout_and_n21_handoff.json
reports/n20_closeout_and_n21_handoff.md
scripts/build_n20_closeout_and_n21_handoff.py
```
