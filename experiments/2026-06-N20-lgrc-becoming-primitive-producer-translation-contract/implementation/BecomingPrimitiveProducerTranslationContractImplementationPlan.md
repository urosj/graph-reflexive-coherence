# N20 Becoming-Primitive Producer Translation Contract Implementation Plan

## Goal

Define the translation contract that later N21-N28 becoming-primitive
experiments must consume.

N20 should answer:

```text
Which agency-of-becoming diagnostics are expressible in LGRC-visible geometry?
Which quantities remain producer mediated?
Which variables are naturalization debt?
Which apparent successes are only proxy-only successes?
Which claim boundaries must remain closed before primitive evidence begins?
```

N20 is contract work. It does not produce primitive evidence and does not open
agency, Phase 8, native support, or ant-ecology implementation.

## Hypotheses

Hypothesis A:

```text
Agency-of-becoming diagnostics can be translated into LGRC-visible primitive
contracts without promoting interpretive labels into primitive evidence.
```

Hypothesis B:

```text
Substrate-carried geometry, producer-mediated residue, naturalization debt, and
blocked relabels can be separated before primitive tests begin.
```

Hypothesis C:

```text
N20 can preserve the N19 AP4/AP5 NAT4 evidence gaps and unsafe claim blockers
while defining the becoming-primitive contract.
```

Hypothesis D:

```text
N20 can define a downstream-enforceable contract that N21-N28 must consume
without redefining basin signature, continuation condition, proxy-only success,
or producer-residue classification in order to pass.
```

## Non-Goals

N20 must not:

```text
implement primitive producer behavior
modify src/*
prove withdrawal resistance
prove learning or choice
prove abundance
prove spark or new-basin formation
prove proxy collapse
prove transfer
prove generative agency
open ant ecology specifications before N29
open Phase 8
claim native support
claim agency
claim semantic intention
claim semantic choice
claim semantic action or semantic perception
claim semantic goal ownership
claim selfhood
claim identity acceptance
claim organism/life behavior
claim sentience or consciousness
claim unrestricted autonomy
```

## Method

N20 uses the Arc of Becoming as method:

```text
Classification:
  name the LGRC-visible primitive without semantic promotion.

Interrogation:
  identify the bounded probes and controls required to expose failure modes.

Naturalization:
  separate substrate-carried state from producer-mediated support and
  naturalization debt.

Cultivation:
  define the minimal producer surface a later experiment may add without
  relabeling scaffolded success as native support.
```

The agency essays supply diagnostic vocabulary only:

```text
withdrawal resistance
naturalization depth
configuration / substrate transfer
proxy divergence / proxy collapse
generative versus extractive persistence
agency after choice
sentience boundary
```

They do not prove implementation evidence.

## Source Scope

Required source tranche:

```text
N19 closeout and native-readiness classifications
N20-N29 roadmap
N12-N18 agency-prerequisites roadmap and handoff
Arc of Becoming method titles
agency-specific essay titles
```

All generated records must use source IDs, titles, or repository-relative paths.
No local absolute paths may appear.

## Artifact Invariants

Every generated N20 artifact must include:

```text
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
src_diff_empty_required = true
```

These fields are not advisory. If any of them flips in N20, the contract row is
not admissible.

## Contract Objects

### Producer

Definition:

```text
producer = explicit implementation surface that introduces, updates, routes,
schedules, labels, or preserves a quantity not yet carried by LGRC
source-current geometry
```

Required producer fields:

```text
producer_surface_name
introduced_quantity
update_rule_owner
source_current_visibility
replay_visibility
budget_surface
claim_boundary
naturalization_debt
negative_controls
```

### Variable Classification

Each variable must use exactly one classification:

```text
substrate_carried
producer_mediated
naturalization_debt
blocked_relabel
```

Definitions:

```text
substrate_carried:
  quantity is carried by source-current LGRC geometry or committed source
  artifacts under replay.

producer_mediated:
  quantity is introduced, routed, preserved, scheduled, or labeled by an
  explicit producer surface.

naturalization_debt:
  quantity is necessary for the proposed primitive but is not yet source-current
  or replay-carried in the required way.

blocked_relabel:
  quantity would only pass by semantic, post-hoc, or claim-inflating relabel.
```

For `naturalization_debt`, exactly one debt subtype must be recorded:

```text
telemetry_debt
policy_debt
state_mutation_debt
replay_debt
budget_debt
source_currentness_debt
claim_boundary_debt
```

N21-N28 cannot convert `producer_mediated` or `naturalization_debt` fields into
`substrate_carried` evidence unless they record a source-backed naturalization
result.

### Continuation Function Descriptor

N20 may use the phrase "native function" only as a bounded continuation
condition descriptor. The safer schema name is
`continuation_function_descriptor`.

In N20, "native function" does not mean purpose, goal, intention, semantic
function, biological function, or goal ownership.

Required fields:

```text
descriptor_id
basin_signature
support_floor
coherence_floor
boundary_condition
flux_condition
continuation_condition
withdrawal_condition
transfer_condition
proxy_metric
proxy_divergence_blocker
claim_ceiling
```

### Proxy Metric

Proxy metrics must remain signs of a function, not replacements for it.

Required fields:

```text
proxy_id
measured_quantity
source_current_inputs
producer_inputs
expected_relation_to_continuation_function
divergence_condition
collapse_condition
proxy_only_success_blocker
```

### Same-Basin Continuation

Same-basin continuation must be geometric, not identity-language.

Required fields:

```text
basin_signature_fields
allowed_drift
required_support_floor
required_coherence_floor
boundary_integrity_floor
flux_balance_bounds
replay_requirement
failure_modes
blocked_relabels
```

## Becoming Primitive Schema

Each primitive row should include:

```text
primitive_id
primitive_name
roadmap_target
diagnostic_source_titles
LGRC_visible_fields
producer_mediated_fields
naturalization_debt_fields
blocked_relabel_fields
native_function_descriptor_alias
continuation_function_descriptor
proxy_metric_definition
support_scaffold_declaration
same_basin_continuation_rule
contract_status
row_decision
minimum_controls
expected_first_positive_experiment
claim_ceiling
unsafe_claim_flags
```

Frozen `contract_status` values:

```text
complete
incomplete_missing_producer_residue_classification
incomplete_missing_continuation_function
incomplete_missing_proxy_metric
incomplete_missing_support_scaffold_declaration
incomplete_missing_same_basin_rule
incomplete_missing_controls
incomplete_missing_claim_ceiling
incomplete_missing_unsafe_claim_flags
incomplete_missing_variable_classification
incomplete_missing_debt_subtype
blocked_by_relabel
```

Frozen `row_decision` values:

```text
supported
partial
blocked
rejected
not_applicable
```

N21-N28 may consume only rows with:

```text
contract_status = complete
row_decision = supported
```

Expected primitive rows:

```text
withdrawal_resistance
naturalization_depth
susceptibility_update
live_continuation_collapse
surplus_supported_optionality
spark_sub_basin_new_basin_formation
proxy_divergence_proxy_collapse
configuration_substrate_transfer
generative_extractive_persistence
```

## AP4/AP5 Gap Carry-Forward

N20 must preserve the N19 AP4/AP5 NAT4 gaps at top level and inside affected
primitive rows.

Structured carry-forward:

```text
ap4_gap_carry_forward:
  gap = route consequence selection is not yet source-current native policy
  blocked_relabels = semantic_choice, intention, producer_preference
  affected_primitives = susceptibility_update, live_continuation_collapse

ap5_gap_carry_forward:
  gap = proxy derivation depends on lower-stack artifact surfaces
  blocked_relabels = semantic_goal, goal_ownership, hidden_proxy_policy
  affected_primitives = proxy_divergence_proxy_collapse
```

Any later primitive whose evidence depends on route selection, proxy derivation,
target formation, or lower-stack source-currentness must carry the relevant gap
row until a source-backed naturalization result removes it.

## Primitive Dependency Map

N20 should freeze the downstream consumption map:

```text
N21 consumes:
  withdrawal_condition
  support_scaffold_declaration
  support_floor
  coherence_floor
  same_basin_continuation_rule
  hidden_producer_support_control
  proxy_only_success_control

N22 consumes:
  susceptibility_fields
  replay_requirement
  durable_geometry_modification_controls
  AP4_gap_dependency_if_route_conditioned

N23 consumes:
  live_continuation_set
  fake_alternative_controls
  producer_preference_injection_blockers
  AP4_gap_dependency

N24 consumes:
  surplus_support_condition
  optional_continuation_space
  floor_crossing_controls
  hidden_budget_relief_control

N25 consumes:
  basin_signature
  sub_basin_distinguishability_rule
  new_basin_replay_requirement
  hidden_producer_insertion_control

N26 consumes:
  proxy_metric_definition
  continuation_function_descriptor
  proxy_divergence_condition
  proxy_collapse_condition
  AP5_gap_dependency

N27 consumes:
  basin_signature
  transfer_mapping_declaration
  reconstructed_support_ledger
  producer_residue_ledger

N28 consumes:
  generative_persistence_fields
  extractive_persistence_fields
  environment_basin_forming_capacity_fields
  medium_debt_placeholder
```

Medium debt is reserved but not opened before N28:

```text
medium_debt_status = deferred_until_N28_N29
medium_debt_not_applicable_before_N28 = true
```

## Minimum Control Template

Every primitive row must include the shared controls:

```text
label_only_success_control
proxy_only_success_control
hidden_producer_support_control
post_hoc_trace_construction_control
semantic_relabel_control
native_support_relabel_control
phase8_relabel_control
```

Primitive-specific controls may be added, but these cannot be removed.

## Downstream Immutability Rule

Each N21-N28 experiment must consume the N20 producer, continuation-function,
proxy, and same-basin contract. A later primitive cannot be counted as
supported if it passes only by changing the N20 basin signature, continuation
condition, proxy-only success blocker, or producer-residue classification.

## Validator Failure Conditions

N20 scripts should fail closed if:

```text
any variable lacks exactly one classification
any naturalization_debt variable lacks a debt subtype
any primitive lacks a continuation_function_descriptor
any primitive lacks a proxy metric definition
any primitive lacks a same-basin continuation rule
any primitive lacks minimum controls
any row opens primitive evidence
any unsafe claim flag is true
any absolute local path appears
any applicable AP4/AP5 gap is omitted
```

## Iteration Plan

### Iteration 1. Source And Method Inventory

Build the source inventory and method boundary.

Expected artifacts:

```text
outputs/n20_source_method_inventory.json
reports/n20_source_method_inventory.md
scripts/build_n20_source_method_inventory.py
```

Acceptance:

```text
source titles recorded
N19 AP4/AP5 NAT4 gaps carried forward
Arc of Becoming method roles separated
agency essay diagnostic roles separated
Sentience as Read-Back marked boundary-only
no primitive evidence opened
```

### Iteration 2. Translation Schema Freeze

Freeze the becoming primitive row schema, variable classification enum, producer
definition, and claim flags.

Expected artifacts:

```text
outputs/n20_translation_schema_v1.json
reports/n20_translation_schema_v1.md
scripts/build_n20_translation_schema_v1.py
```

Acceptance:

```text
schema frozen before primitive evidence
producer definition frozen
variable classification enum frozen
naturalization debt subtype enum frozen
continuation function descriptor schema frozen
proxy metric schema frozen
same-basin continuation schema frozen
contract_status enum frozen
row_decision enum frozen
unsafe claim flags forced false
```

### Iteration 3. Producer Residue And Naturalization Debt Ledger

Classify each future primitive's required quantities as substrate-carried,
producer-mediated, naturalization debt, or blocked relabel.

Expected artifacts:

```text
outputs/n20_producer_residue_ledger.json
reports/n20_producer_residue_ledger.md
scripts/build_n20_producer_residue_ledger.py
```

Acceptance:

```text
each primitive has a residue row
each variable has exactly one classification
AP4/AP5 gaps remain explicit
N21-N28 cannot consume producer-mediated success as native support
```

### Iteration 4. Continuation Function / Proxy / Scaffold Contract

Freeze descriptors for continuation function, proxy metric, support/scaffold,
and proxy-only success.

Expected artifacts:

```text
outputs/n20_native_function_proxy_contract.json
reports/n20_native_function_proxy_contract.md
scripts/build_n20_native_function_proxy_contract.py
```

Acceptance:

```text
continuation function descriptor is geometric and bounded
proxy metric cannot replace continuation function
support/scaffold declarations are mandatory
proxy-only success blockers are explicit
```

### Iteration 5. Same-Basin Continuation And Control Contract

Define what counts as the same basin continuing and what controls must fail
closed in later primitive experiments.

Expected artifacts:

```text
outputs/n20_same_basin_continuation_contract.json
reports/n20_same_basin_continuation_contract.md
scripts/build_n20_same_basin_continuation_contract.py
```

Acceptance:

```text
same-basin continuation uses support/coherence/boundary/flux/replay criteria
label-only continuation is rejected
proxy-only success is rejected
hidden producer support is rejected
semantic agency relabels are rejected
```

### Iteration 6. Closeout And N21 Handoff

Close N20 as a contract and hand off to N21 withdrawal resistance and
naturalization depth.

Expected artifacts:

```text
outputs/n20_closeout_and_n21_handoff.json
reports/n20_closeout_and_n21_handoff.md
scripts/build_n20_closeout_and_n21_handoff.py
```

Acceptance:

```text
N20 contract complete
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
N21 handoff records required withdrawal and naturalization-depth inputs
N21 readiness gate recorded
```

N21 readiness gate:

```text
n21_ready = true only when all required N21 inputs are present
n21_required_inputs_present =
  withdrawal_condition
  support_scaffold_declaration
  support_floor
  coherence_floor
  same_basin_continuation_rule
  hidden_producer_support_control
  proxy_only_success_control
n21_blockers = [] only when the gate is complete
```

## Closeout Ceiling

The strongest allowed N20 closeout is:

```text
final_claim_ceiling = artifact_level_becoming_primitive_translation_contract
N21_ready = true
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
```
