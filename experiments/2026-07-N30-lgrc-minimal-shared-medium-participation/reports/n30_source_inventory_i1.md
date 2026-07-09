# N30 Iteration 1 - Source Inventory And Method Admission

Status: `passed`

Acceptance state:
`accepted_source_inventory_method_admission_no_positive_evidence`

Output digest: `2a7bc77d5c7034e0b329dd80a85de44e8bafa56ac966ca61ac501b89ae2f61a4`

## Scope

Iteration 1 admits sources only. Shared-medium documents are consumed as
vocabulary, method, controls, debt, and claim-boundary sources. N27, N28, and
N29 are guardrails and bridge context. No N30 participant, medium trace,
eligibility dependency, replay, or positive row is opened here.

## Source Records

| Source | Role | Runtime Evidence Allowed | Digest |
|---|---|---:|---|
| n30_plus_experiment_catalog_roadmap | catalog_ontology_and_claim_policy_source | false | sha256:3c5ac6d9cbb0... |
| n30_plus_candidate_directions | candidate_direction_and_dependency_context | false | sha256:47043d91d59c... |
| shared_medium_essay | shared_medium_conceptual_transition_source | false | sha256:c2c237152503... |
| shared_medium_coordination_engineering_spec | shared_medium_method_control_and_debt_source | false | sha256:db249acdfc95... |
| n27_closeout_and_n28_handoff | participant_continuity_and_transfer_guardrail | false | sha256:65def6d91e32... |
| n28_closeout_and_n29_handoff | environment_effect_and_medium_reshaping_guardrail | false | sha256:7e17af82ba5b... |
| n29_closeout_and_ecology_handoff | ecology_bridge_and_shared_medium_demand_context | false | sha256:842ba57e994b... |
| n20_n29_becoming_agency_ecology_roadmap | becoming_agency_ecology_arc_state | false | sha256:911c5055d8cf... |
| n20_n29_becoming_agency_ecology_handoff | handoff_state_and_next_step_context | false | sha256:2831fe6c668b... |
| claim_boundary_index | blocked_claim_and_claim_ceiling_index | false | sha256:a4a2e3fd042e... |

## Consumption Rule

Roadmap and shared-medium sources may shape the N30 schema and controls, but
they cannot satisfy any source-current evidence gate. N27/N28/N29 artifacts may
define continuity, environment-effect, and ecology-demand guardrails; they do
not count as N30 shared-medium participation evidence.

If N27/N28 closeout summaries do not expose the needed guardrail fields directly
for a later positive row, that row must consume the underlying N27/N28 result
artifacts rather than relying on closeout summary text.

## Digest Semantics

`output_digest` is the canonical payload digest. A file-content SHA, when used
by downstream artifacts, is the exact JSON artifact hash. Those values are
allowed to differ because they digest different scopes.

## Checks

- all_required_sources_exist: true
- required_method_sources_present: true
- external_shared_medium_sources_pinned: true
- method_sources_not_runtime_evidence: true
- n27_n28_n29_guardrails_present: true
- all_records_have_consumption_boundaries: true
- no_positive_n30_evidence_opened: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true

## Claim Boundary

`minimal_shared_medium_participation_claim_allowed = false`

`shared_medium_coordination_claim_allowed = false`

`native_shared_medium_organization_claim_allowed = false`
