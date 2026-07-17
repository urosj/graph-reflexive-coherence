# N31 Iteration 9 - Added-Mechanism Admission

## Result

```text
status = passed
acceptance_state = accepted_lane_qualified_added_mechanism_admission_frozen_no_candidate_evidence
native_carrier_lane = D0a / existing_native carrier / DR2
native_organization_observable = exact_derived_projection
added_mechanism_lanes = A, B, C
positive_candidate_evidence_opened = false
n31_closeout_progress_rung = N31-C4
ready_for_I9_A = true
ready_for_I9_B = true
ready_for_I9_C = true
final_N31_supported = false
```

I9 freezes three semantically distinct added-mechanism contracts. It does not
run them and assigns no positive producer or closure rung.

The reviewed pre-correction I8 identity and the exact corrected I8 consumed by
I9 are linked in `n31_i8_revision_lineage_r1.json`. The correction changed no
scientific conclusion.

## Lane-Qualified Classification

| Candidate | Semantic class | Authority | Next probe | Current rung | Later eligible ceiling |
|---|---|---|---|---|---|
| A_release_efficacy_attenuation | A | producer_mediated | I9-A | DR0 | DR5_expression_attenuation_not_field_state_decay |
| B_conserved_source_leakage | B | producer_mediated | I9-B | DR0 | DR6_after_DR5_and_reusable_B_R_contract |
| C_route_susceptibility_relaxation | C | effective_non_markovian_closure | I9-C | DR0 | DR6_after_DR5_and_reusable_susceptibility_contract |

The native D0a lane remains at DR2. A later producer-assisted DR5 or DR6 result
will remain separate and cannot upgrade that native ceiling. A future native
implementation must be rerun as native evidence.

## Candidate Roles

```text
A = release-efficacy expression attenuation; never in-flight attenuation
B = producer-owned conserved B-R export to an explicit destination
C = independently restored susceptibility closure with explicit relaxation
```

## Pre-Execution Boundary

| Candidate | Allowed source-current inputs | Lane controls | Complete controls to regenerate | Canonical topology digest |
|---|---:|---:|---:|---|
| A_release_efficacy_attenuation | 10 | 5 | 57 | `8b8c379411a32e059d8f4a075710dc35c9772d75eaf7df961ec9147c18af5f1f` |
| B_conserved_source_leakage | 7 | 8 | 60 | `9f0a651d2194bb12a47b8136c7c0f0a793e306917a4ae49882c8d85b63624e3f` |
| C_route_susceptibility_relaxation | 7 | 5 | 57 | `56b54d0bdb60ccfb0b4e95b6fb5ef3eb5e3a1f558aeebc7b90c1fdd4bbe87d4c` |

Every unlisted input blocks the candidate row. I3 null results are not consumed
directly: all applicable common, D0, schema-relation, and lane controls must be
regenerated against the candidate carrier and authority.

Candidate A distinguishes formation source node 0, release source node 1, and
receiver node 2. Only `q_created` is debited; `q_unreleased` is a derived
counterfactual that remains in release-source coherence. Only the exact
registered formation-arrival receipt can age the release phase.

Candidate B distinguishes formation source node 0, leakage source node 1,
destination node 2, and later readout node 3. Conserved export is not enough:
the preregistered route-organization contrast must weaken independently of mass
loss, and destination clamp/trace controls must exclude return influence before
readout.

Candidate C applies `S * g_native` after native conductance reconstruction and
before native `compute_potential` and `compute_flux`. Ordinary `LGRC9V3.step()`
would overwrite a prior conductance write, so the closure owns this partial
pipeline ordering. That missing hook is explicit producer/closure debt, not a
native decay claim. `absolute_delta_S` is a report-only update magnitude, not a
resource cost; the composed LGRC-plus-S system may itself be Markovian.

The candidates do not share one scalar decay law and are not ranked by raw
effect size. A is capped at expression-attenuation DR5. B and C may become DR6
only after DR5 controls and a reusable bounded contract. `N31-C6` remains a
closeout-completeness statement rather than mechanism DR6 evidence.

## Claim Boundary

```text
three_lane_qualified_added_mechanism_contracts_admitted_for_execution_with_native_D0a_preserved_at_DR2
```

No positive A/B/C support, native decay, memory, trail, communication, ecology,
agency, native-support, or Phase 8 claim is opened.

## Checks

| Check | Passed |
|---|---:|
| `I2_and_I8_source_identities_exact` | true |
| `I8_ready_for_I9_admission` | true |
| `I8R1_revision_lineage_explicit_and_current_I8_consumed` | true |
| `native_lane_preserved_at_DR2` | true |
| `three_distinct_added_mechanism_lanes_admitted` | true |
| `authority_classes_use_frozen_enum` | true |
| `all_added_mechanism_lanes_remain_DR0_without_evidence` | true |
| `candidate_topologies_complete_and_executable` | true |
| `source_current_input_allowlists_fail_closed` | true |
| `candidate_equations_clocks_invariants_frozen` | true |
| `lane_specific_controls_are_valid_frozen_I2_controls` | true |
| `complete_inherited_control_matrices_frozen_for_regeneration` | true |
| `candidate_A_release_efficacy_boundary_frozen` | true |
| `candidate_B_conservation_destination_and_ownership_frozen` | true |
| `candidate_B_organization_isolation_and_one_shot_contracts_frozen` | true |
| `candidate_C_independent_state_restoration_and_update_magnitude_frozen` | true |
| `candidate_C_executable_native_consumer_path_frozen_with_hook_debt` | true |
| `producer_residue_and_naturalization_debt_explicit` | true |
| `native_upgrade_blocked_for_all_added_lanes` | true |
| `candidate_semantics_not_collapsed_or_ranked` | true |
| `no_positive_candidate_evidence_opened` | true |
| `artifact_manifest_exact` | true |
| `unsafe_claim_flags_false` | true |
| `src_diff_empty` | true |
| `protected_runtime_contract_diff_empty` | true |
| `no_absolute_paths_in_records` | true |
