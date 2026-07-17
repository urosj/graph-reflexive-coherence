# N31 Iteration 2 - Semantic, Representation, And Control Schema Freeze

Status: `passed`

Acceptance state: `accepted_semantic_representation_control_schema_frozen_no_positive_evidence`

Output digest: `a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf`

## Scope

I2 freezes how later N31 evidence may be represented and classified. It does
not assign a semantic class, D0a representation status, DR rung, candidate
disposition, or scientific result.

## Frozen Axes

Primary semantic classes are exactly `D0a`, `D0b`, `D0c`, `A`, `B`, and `C`.
Representation/authority and candidate disposition are independent axes.
`D0-R` remains an ordinary-export subtype of D0 and `B-R` remains a
policy-owned subtype of Candidate B; neither is a seventh primary class.

## Normalized Evidence Contracts

Three contracts are mandatory and non-substitutable:

1. Route mass records support, boundary, measure, signed outward flux,
   integration window, in-flight treatment, single-count crossing policy, and
   continuity residual. The flux term is time-integrated exported coherence,
   not an instantaneous flux-rate sample.
2. Route organization records the mediator domain, diagnostic domains,
   load-bearing domain, authority, update owner, and recomputation status.
3. Causal mediation records a later local readout, intervention, matched state,
   packet exclusion, hidden-path controls, and mediation strength.

Lower route mass is not organization weakening. Organization weakening is not
causal mediation. A label may not author any of these facts.

## Temporal And Geometric Boundary

Temporal organization may be derived from admitted timing/packet state, but an
arrival histogram alone remains observable evidence. Forming packets must be
exhausted, isolated, or excluded by identity before a later independent
readout claim. Added coincidence or resonance state changes authority to a
closure/extension. Geometric shallowing requires a local transport
intervention rather than a changed curvature diagnostic alone.

## Producer And Restoration Boundary

D0 allows no load-bearing post-formation state mutation by an experiment-local
producer. A producer that decides or schedules export timing, amount, or
destination moves the row to `B-R`, even without direct mutation and even when
conservation closes. B-R classification alone is not positive decay support;
actual emission, mass change, debit/packet/credit closure, organization, and
mediation remain separate gates. Current-state replay uses
restoration identity v1; reset-sensitive equivalence uses v2. External state
requires separate versioned identity composition. Cache recomputation and
full execution reconstruction remain separate gates.

## Control Families

| Family | Frozen controls |
|---|---:|
| common | 16 |
| D0 | 28 |
| A | 5 |
| B | 8 |
| C | 5 |
| schema relations | 8 |

`failed_closed` means the false-positive path was correctly rejected.
`failed_open` invalidates the affected row. `not_run` blocks its dependent
rung, and `not_applicable` requires an explicit scope reason.

Active-null comparability includes semantic class, authority, organization and
load-bearing domains, internal-time policy, candidate schema, carrier, and
continuation-state contracts. Matching topology alone is insufficient.

## Schema Counts

- Candidate required fields: `72`
- Active-null required fields: `28`
- Route-mass fields: `20`
- Route-organization fields: `15`
- Causal-mediation fields: `18`
- RCAE return fields: `77`
- Control IDs: `70`

## Checks

- `I1_status_passed` = `true`
- `I1_output_digest_valid` = `true`
- `I1_output_digest_matches_frozen_value` = `true`
- `I1_artifact_sha256_matches` = `true`
- `I2_base_revision_is_ancestor` = `true`
- `protected_runtime_base_precedes_governance_base` = `true`
- `schema_authority_sources_pinned` = `true`
- `primary_semantic_classes_exact` = `true`
- `D0_R_and_B_R_not_primary_classes` = `true`
- `taxonomy_axes_separated` = `true`
- `DR_ladder_complete` = `true`
- `N31_closeout_ladder_complete` = `true`
- `D0a_representation_gate_fail_closed` = `true`
- `route_mass_contract_complete` = `true`
- `route_flux_is_integrated_and_single_counted` = `true`
- `route_organization_contract_complete` = `true`
- `causal_mediation_contract_complete` = `true`
- `mass_organization_mediation_separate` = `true`
- `mixed_domain_requires_load_bearing_resolution` = `true`
- `forming_packets_excluded_for_later_probe` = `true`
- `candidate_required_fields_complete` = `true`
- `active_null_comparability_frozen` = `true`
- `cross_field_relation_rules_frozen` = `true`
- `producer_call_audit_fail_closed` = `true`
- `D0_export_authoring_reclassified_to_B_R` = `true`
- `ownership_facts_trace_derived` = `true`
- `B_R_classification_separate_from_support` = `true`
- `semantic_transition_rules_frozen` = `true`
- `restoration_v1_v2_distinguished` = `true`
- `cache_and_execution_reconstruction_separate` = `true`
- `all_control_families_frozen` = `true`
- `failed_open_invalidates` = `true`
- `return_manifest_fields_complete` = `true`
- `src_diff_empty` = `true`
- `protected_runtime_contract_diff_empty` = `true`
- `positive_evidence_remains_closed` = `true`
- `unsafe_claim_flags_false` = `true`
- `no_absolute_paths_in_records` = `true`

## Claim Ceiling

`positive_evidence_opened = false`

`decay_relation_ladder_rung_assigned = false`

`n31_closeout_ceiling = N31-C1_source_and_semantic_contract_admitted`
