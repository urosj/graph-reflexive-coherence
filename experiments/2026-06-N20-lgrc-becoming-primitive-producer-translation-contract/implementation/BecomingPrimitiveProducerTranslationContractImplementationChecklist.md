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

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Treat Arc of Becoming as method, not evidence shortcut.
- [x] Treat agency essays as diagnostic vocabulary, not proof.
- [x] Treat `Sentience as Read-Back` as boundary-only.
- [x] Carry forward N19 AP4/N14 NAT4 evidence gap.
- [x] Carry forward N19 AP5/N15 NAT4 evidence gap.
- [x] Keep N29 as the first formal agentic-ecology bridge.
- [x] Do not write ant-ecology implementation specs in N20.
- [x] Include the N20 invariant block in every generated artifact.
- [x] Do not modify `src/*`.
- [x] Force unsafe claim flags false in every row.
- [x] Reject native-support claims unless a separate Phase 8 implementation
      exists and validates them.
- [x] Enforce that later experiments cannot redefine N20 basin signature,
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

- [x] Build producer residue ledger.
- [x] Build naturalization debt ledger.
- [x] Assign exactly one variable classification per variable.
- [x] Separate substrate-carried fields from producer-mediated fields.
- [x] Mark blocked relabel fields explicitly.
- [x] Record AP4/AP5 gap dependencies.
- [x] Record naturalization debt subtype for each naturalization-debt field.
- [x] Confirm each variable receives exactly one classification.
- [x] Confirm later experiments cannot treat producer-mediated success as native
      support.

Expected artifacts:

```text
outputs/n20_producer_residue_ledger.json
reports/n20_producer_residue_ledger.md
scripts/build_n20_producer_residue_ledger.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_producer_residue_naturalization_debt_ledger_no_primitive_evidence
artifact = outputs/n20_producer_residue_ledger.json
report = reports/n20_producer_residue_ledger.md
script = scripts/build_n20_producer_residue_ledger.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_producer_residue_ledger.py
row_count = 9
variable_record_count = 258
classification_counts = {
  blocked_relabel: 168,
  naturalization_debt: 27,
  producer_mediated: 27,
  substrate_carried: 36
}
output_digest = 0d7193fa14e9a3f299f0ff941f7424a944d6de963578eb9fc566a5244653d69f
artifact_sha256 = cfb4a0f00d75fe99924ccfacd37c86565cf459c7ab01150fd3761c54526dea70
report_sha256 = 82ac671430362ae5f54bc98d7c95e6c757f726ee4df9cfc2ef890378fde3cdc9
script_sha256 = 91120a1dbdf43b9ad69150ebcb3d9df11353adb96ccfabcef3f0e4828e19fc94
source_schema_output_digest = c0cf2a1990aa0ce302ebe52c0bf8d2d8ada695c8b812d2fd3abb78b9ffc935ef
source_schema_sha256 = c36c5ea5425535edee76aad5047377b50a15c259f1341baccdac76652ecc6875
failed_checks = []
producer_residue_rows_classified = true
naturalization_debt_ledger_defined = true
primitive_rows_evidence_classified = false
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
ready_for_iteration_4_native_function_proxy_contract = true
```

Iteration 3 supports each row as a residue/debt accounting row only. It does
not support withdrawal resistance, naturalization depth, learning, choice,
abundance, spark, proxy collapse, transfer, generative persistence, agency,
Phase 8, native support, sentience, or ant-ecology implementation. Every row
remains `contract_status = incomplete_missing_continuation_function` until
Iterations 4 and 5 define the continuation, proxy, support/scaffold,
same-basin, and control contracts.

Post-review double-check record:

```text
all expected primitives have one ledger row = true
all variables have exactly one classification = true
naturalization debt variables have debt subtypes = true
naturalization debt records name owner and source-backed conversion condition = true
blocked semantic labels are blocked_relabel variables = true
blocked semantic labels are not producer_mediated variables = true
full unsafe claim family blocked as variables in every row = true
core substrate/producer/debt field sets are primitive-specific = true
producer_mediated success cannot be native support = true
N21-N28 consumption rules present = true
primitive-specific N21-N28 consumption map present = true
diagnostic vocabulary cannot satisfy evidence gates = true
primitive evidence opened = false
all contract rows complete = false

Iteration 4 carry-forward guards:
  AP4/AP5 dependencies must be carried forward into I4 = true
  I4 must not mark all rows complete automatically = true
  suggested post-I4 status = incomplete_missing_same_basin_rule or
                             incomplete_missing_controls unless I4 also
                             supplies I5 same-basin/control criteria
  producer-mediated success can become native support in I4 = false
  blocked relabels may become proxy metrics = false

AP4/AP5 local dependencies:
  susceptibility_update has AP4 dependency = true
  susceptibility_update has conditional AP5 dependency = true
  live_continuation_collapse has AP4 dependency = true
  live_continuation_collapse has conditional AP5 dependency = true
  proxy_divergence_proxy_collapse has AP5 dependency = true
  configuration_substrate_transfer has conditional AP4 dependency = true
```

## Iteration 4. Continuation Function / Proxy / Scaffold Contract

- [x] Build continuation function descriptor contract.
- [x] Build proxy metric definition contract.
- [x] Build support/scaffold declaration contract.
- [x] Define proxy-only success blockers.
- [x] Confirm continuation function descriptor stays geometric and bounded.
- [x] Confirm proxy improvement cannot replace basin continuation.
- [x] Confirm semantic function, goal, or intention labels remain blocked.
- [x] Confirm every primitive declares proxy-only success blockers.

Expected artifacts:

```text
outputs/n20_native_function_proxy_contract.json
reports/n20_native_function_proxy_contract.md
scripts/build_n20_native_function_proxy_contract.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_function_proxy_scaffold_contract_no_primitive_evidence
artifact = outputs/n20_native_function_proxy_contract.json
report = reports/n20_native_function_proxy_contract.md
script = scripts/build_n20_native_function_proxy_contract.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_native_function_proxy_contract.py
row_count = 9
contract_status_counts = {
  incomplete_missing_same_basin_rule: 9
}
output_digest = 44eac87775ae7e399e93a48ccf6ff020f157a0fbe3e3b77421a1a3ea059070c3
artifact_sha256 = 23e87346e05bb32347630b7ea3c688bf83096dfdb9ca11f99a35a82a2e602760
report_sha256 = b1e9b0bc55f4691fcf8ca343e4353ab4d9392099d3dd1ef4d73459c9b7e73b10
script_sha256 = 87503936da94630bb306da9984b3b105e4847875e39da52b625eb4f5d8377d09
source_ledger_output_digest = 0d7193fa14e9a3f299f0ff941f7424a944d6de963578eb9fc566a5244653d69f
source_ledger_sha256 = cfb4a0f00d75fe99924ccfacd37c86565cf459c7ab01150fd3761c54526dea70
failed_checks = []
native_function_descriptors_defined = true
continuation_function_descriptors_defined = true
proxy_metric_definitions_defined = true
support_scaffold_declarations_defined = true
proxy_only_success_blockers_defined = true
rows_marked_complete = false
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
ready_for_iteration_5_same_basin_control_contract = true
```

Iteration 4 defines contract objects only. The phrase
`native_function_descriptor` remains an alias for
`continuation_function_descriptor`, meaning a bounded geometric continuation
condition, not purpose, goal, semantic function, intention, task success, or
goal ownership. Each proxy metric is a bounded indicator, not a replacement
for the continuation function.

Post-review double-check record:

```text
source I3 ledger passed and primitive evidence unopened = true
all expected primitives have I4 contract rows = true
continuation descriptors are geometric and bounded = true
proxy metrics are signs, not replacements = true
proxy-only success blockers defined in every row = true
blocked relabels are not proxy metrics = true
support/scaffold declarations are explicit = true
N21 handoff inputs present for withdrawal_resistance = true
N21 handoff inputs present for naturalization_depth = true
all rows remain incomplete until I5 = true
primitive descriptors are distinct = true
primitive evidence opened = false

Proxy-only fail-closed rule:
  If proxy improves while continuation function, declared basin signature,
  support floor, coherence floor, boundary condition, or flux condition fails,
  the primitive is not supported.

AP4/AP5 local dependencies carried forward:
  susceptibility_update has AP4 dependency = true
  susceptibility_update has conditional AP5 dependency = true
  live_continuation_collapse has AP4 dependency = true
  live_continuation_collapse has conditional AP5 dependency = true
  proxy_divergence_proxy_collapse has AP5 dependency = true
  configuration_substrate_transfer has conditional AP4 dependency = true
```

Validation review note:

```text
contract_status = incomplete_missing_same_basin_rule is the primary I4
transition status because I5 owns the same-basin contract first. The row-level
missing_contract_objects array remains the fuller state of record and lists
both same_basin_continuation_rule and minimum_controls.

hidden_support_blocker and hidden_support_control intentionally share the same
fail-closed text in I4 because the directive asks for a blocker name while the
support/scaffold schema keeps the control field. I5 may normalize this if the
full control contract no longer needs both labels.
```

## Iteration 5. Same-Basin Continuation And Control Contract

- [x] Define same-basin continuation criteria.
- [x] Define allowed drift.
- [x] Define support/coherence floors.
- [x] Define boundary integrity and flux balance criteria.
- [x] Define replay requirements.
- [x] Define label-only continuation control.
- [x] Define proxy-only success control.
- [x] Define hidden producer support control.
- [x] Define semantic overclaim controls.
- [x] Define minimum shared control template for all primitive rows.
- [x] Define primitive dependency map for N21-N28.
- [x] Record medium debt as deferred until N28/N29.

Expected artifacts:

```text
outputs/n20_same_basin_continuation_contract.json
reports/n20_same_basin_continuation_contract.md
scripts/build_n20_same_basin_continuation_contract.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_same_basin_control_contract_complete_no_primitive_evidence
artifact = outputs/n20_same_basin_continuation_contract.json
report = reports/n20_same_basin_continuation_contract.md
script = scripts/build_n20_same_basin_continuation_contract.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_same_basin_continuation_contract.py
row_count = 9
contract_status_counts = {
  complete: 9
}
output_digest = 6a1975e6811c6990ae882d4e5b59233c08784909ddbef823706cad31b61a3bb5
artifact_sha256 = 72c4297b923a5dc0226e67be97ff368d0b586278f8b93ef4bd6fa7b79d1fb4d0
report_sha256 = e77c2e8b9c4b716ec718b394e056086d9357ac37f2600bb2fa9d2a940c2d94d2
script_sha256 = ab6c835e963052e1c6324a0b51c2afdf4972078814c1d59b299f18a9e8517abd
source_contract_output_digest = 44eac87775ae7e399e93a48ccf6ff020f157a0fbe3e3b77421a1a3ea059070c3
source_contract_sha256 = 23e87346e05bb32347630b7ea3c688bf83096dfdb9ca11f99a35a82a2e602760
failed_checks = []
same_basin_rules_defined = true
minimum_controls_defined = true
primitive_dependency_map_defined = true
contract_rows_complete = true
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
ready_for_iteration_6_closeout = true
```

Iteration 5 completes the N20 contract rows only. `contract_status = complete`
means the contract surface now contains residue/debt classification,
continuation/proxy/scaffold definitions, same-basin continuation rules, replay
requirements, the shared control template, and primitive-specific controls. It
does not mean any primitive is supported.

Post-review double-check record:

```text
source I4 contract passed and ready = true
all expected primitives have I5 rows = true
same-basin required fields present = true
support/coherence floors defined = true
boundary integrity and flux balance criteria defined = true
replay requirements defined = true
minimum shared control template present in every row = true
primitive-specific controls present = true
all controls fail closed = true
proxy-only success rejected = true
label-only continuation rejected = true
hidden producer support rejected = true
AP4/AP5 dependencies carried forward locally = true
primitive dependency map frozen = true
susceptibility AP5 dependency split explicit = true
configuration transfer scope primary = true
N28 medium-debt relation controls present = true
medium debt deferred until N28/N29 = true
definition components have source basis = true
definition components are necessary but not sufficient = true
definition revision policy present = true
definition validation source roles explicit = true
future outcomes not pre-decided by contract = true
contract rows complete but primitive evidence unopened = true
contract_complete means N20 contract surface complete only = true
unsafe claim flags false per row = true
primitive evidence opened = false
```

Definition correctness record:

```text
definition_validation_status = validated_as_evidence_informed_conservative_contract_not_as_primitive_evidence
definition_sufficiency_status = necessary_contract_gates_not_sufficient_primitive_evidence
definition_component_count = 9
direct prior boundary evidence components = 1
direct prior control evidence components = 2
direct claim-boundary evidence components = 1
prior experiment backed contract components = 2
conservative admissibility assumptions = 1
ledger/method backed contract components = 1
prior control pattern and row-specific contract components = 1
contract definitions are primitive evidence = false
future rows must supply source-backed pass/fail evidence = true
ad hoc redefinition to pass allowed = false
row-specific thresholds must be declared before use = true
claim boundary must be preserved = true
```

The I5 definitions are correctness constraints for future primitive tests, not
future primitive results. Basin signature, drift bounds, support/coherence
floors, boundary integrity, flux bounds, replay requirements, failure modes,
blocked relabels, and minimum controls are all required gates. They are
necessary but not sufficient: N21-N28 must still produce source-backed
pass/fail evidence for each primitive. Later experiments cannot redefine these
contracts ad hoc to pass; any correction must record source-backed evidence
that a definition is over- or under-constraining while preserving N19 AP4/AP5
gap propagation and unsafe claim blockers.

External-source review adjustment:

```text
N20 I5 reviewed as conceptually consistent with the agency/becoming, agentic
ecology, shared-medium, and graph-reflexive-coherence boundaries = true

Main fix applied:
  susceptibility_update AP5 handling is now explicit split, not silent
  weakening.

Split rule:
  base_susceptibility_update carries AP4 when route-conditioned selection
  participates.

  proxy_conditioned_susceptibility_update carries AP5 when proxy derivation or
  target formation participates.

  N19 AP5 gap removed = false

Contract-complete alias:
  contract_complete = true
  contract_complete_means = N20_contract_surface_complete
  primitive_supported = false
  primitive_evidence_opened = false
  all_primitives_complete_language_allowed = false

N27 scope:
  configuration/topology transfer inside LGRC is primary.
  cross-substrate transfer is optional and requires a declared source-backed
  substrate mapping before it can count.

N28 controls:
  medium_debt_as_success_control present = true
  direct_message_scaffold_as_native_medium_control present = true
  shared_medium_label_only_control present = true
```

## Iteration 6. Closeout And N21 Handoff

- [x] Close N20 as a contract experiment.
- [x] Confirm primitive evidence remains unopened.
- [x] Confirm agency remains unopened.
- [x] Confirm Phase 8 remains unopened.
- [x] Confirm native support remains unopened.
- [x] Confirm sentience remains unopened.
- [x] Confirm `src_diff_empty = true`.
- [x] Record N21 withdrawal-resistance handoff inputs.
- [x] Record N21 naturalization-depth handoff inputs.
- [x] Record N21 readiness gate and blockers.

Expected artifacts:

```text
outputs/n20_closeout_and_n21_handoff.json
reports/n20_closeout_and_n21_handoff.md
scripts/build_n20_closeout_and_n21_handoff.py
```

Implementation record:

```text
status = passed
acceptance_state = closed_n20_contract_and_n21_handoff_no_primitive_evidence
artifact = outputs/n20_closeout_and_n21_handoff.json
report = reports/n20_closeout_and_n21_handoff.md
script = scripts/build_n20_closeout_and_n21_handoff.py
command = .venv/bin/python experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/scripts/build_n20_closeout_and_n21_handoff.py
final_supported_status = N20_contract_closed_no_primitive_evidence
final_claim_ceiling = artifact_level_becoming_primitive_translation_contract_only
output_digest = 1f28287546b42bc258778b6020226a45e68d8dc6665639debbeb7fb96b6fd621
artifact_sha256 = f6897b0bd39d716e3f8de33ff1818d7b71cf59d9da957197dccd247e7ec438e9
report_sha256 = 64c06f0376b62039c824db8b3ec71d8d671e623f78d502a76f74a1f34637f4e9
script_sha256 = a1fea6fce54c0229daa73ecb179b36f9d27f6d4cf95f81d29fd963d73c3a774e
source_i5_output_digest = 6a1975e6811c6990ae882d4e5b59233c08784909ddbef823706cad31b61a3bb5
source_i5_sha256 = 72c4297b923a5dc0226e67be97ff368d0b586278f8b93ef4bd6fa7b79d1fb4d0
failed_checks = []
n20_contract_complete = true
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
src_diff_empty = true
ready_for_n21 = true
n21_handoff_scope = withdrawal_resistance, naturalization_depth
```

Iteration 6 closes N20 as a contract/schema experiment only. Hypotheses A-D
are closed as contract-supported, not primitive-supported. The final claim
ceiling is `becoming_primitive_translation_contract_only`.

N21 handoff gate:

```text
must_consume_i5_contract = true
may_redefine_n20_contract_to_pass = false
must_declare_row_specific_thresholds_before_use = true
must_produce_source_backed_pass_fail_evidence = true
must_fail_closed_on_hidden_support = true
must_fail_closed_on_proxy_only_success = true
must_keep_primitive_evidence_separate_from_contract = true
must_keep_agency_native_phase8_sentience_claims_blocked = true
```

Closeout checks:

```text
all source artifacts passed = true
I5 contract passed and ready for closeout = true
contract rows complete but not primitive evidence = true
artifact invariants preserved = true
unsafe claim flags false per row = true
definition guards preserved = true
AP4/AP5 gap guards preserved = true
N21 handoff rows present = true
N21 handoff requires hidden-support and proxy controls = true
N21 readiness gate blocks redefinition = true
hypotheses closed as contract-supported = true
src_diff_empty = true
no_absolute_paths = true
```
