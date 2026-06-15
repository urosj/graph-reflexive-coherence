# N14 Consequence-Sensitive Route Selection Implementation Plan

## Purpose

N14 tests whether route selection can depend on source-backed expected
downstream effects on support, memory, or regulation rather than immediate
route affordance alone.

N14 targets `AP4` at most:

```text
AP4 = consequence-sensitive selection candidate
```

The expected final ceiling, if supported, is:

```text
artifact_level_ap4_consequence_sensitive_route_selection_candidate
```

This is not intention, agency, semantic goal ownership, identity acceptance,
selfhood, personhood, biological behavior, native support, or fully native
agentic-like integration.

## Source Rules

Iteration 1 must pin source artifacts before mechanism interpretation. Primary
source lanes are:

```text
N06 route arbitration and route alternatives
N08 memory / affordance evidence
N09 bounded response regulation evidence
N12 NAT4 readiness records
N13 AP3 support-seeking regulation closeout and stress matrix
```

N14 may consume N13 only as artifact-level AP3 support-seeking regulation
evidence. N14 may consume N12 NAT4 records only as Phase 8 readiness evidence,
not native support.

## AP4 Gate

Assign `AP4` only when all of the following are present and validated:

```text
candidate route set
eligible candidate completeness record
pre-selection consequence record for each candidate
source artifact/report/digest for each consequence record
prediction basis and derivation policy
source window for each projection
downstream support effect descriptor
downstream memory effect descriptor
downstream regulation effect descriptor
observed downstream effect descriptor when the bounded horizon is evaluated
prediction match status
immediate affordance rank
consequence rank
selected rank
affordance/consequence conflict case
affordance_consequence_conflict_resolved_by_consequence
budget cost surface
bounded consequence horizon
deterministic selection rule
tie policy
missing consequence record rejection policy
idempotency/digest plan
snapshot/replay requirements
artifact-only replay requirement
snapshot/load equivalence requirement
order inversion replay requirement
runtime_state_used = false
stale-record policy
negative controls
compatibility checks
claim flags forced false
src_diff_empty = true
native_supported_flags = false
phase8_opened = false
```

`AP4` is a final closeout level only after Iterations 5-7 controls pass. Earlier
iterations may use `provisional_ap_level`.

## Provisional Iteration 1 Row Schema

```text
row_id
source_experiment
source_iteration
source_artifact
source_report
source_sha256
source_report_sha256
mechanism_name
mechanism_role
route_candidate_id
route_alternative_surface
eligible_candidate_set_id
candidate_set_completeness_status
rejected_candidate_record
immediate_affordance_surface
immediate_affordance_rank
consequence_record_source
consequence_record_timing
bounded_consequence_horizon
prediction_basis
derivation_policy
source_window
expected_support_effect
expected_memory_effect
expected_regulation_effect
observed_downstream_effect
prediction_match_status
consequence_rank
selected_rank
affordance_consequence_conflict_resolved_by_consequence
budget_cost_surface
budget_validity
selection_rationale_surface
tie_policy
missing_consequence_record_rejection
hidden_outcome_table_control
post_hoc_scoring_control
stale_record_policy
artifact_only_replay_status
snapshot_load_status
order_inversion_replay_status
runtime_state_used
provisional_ap_level
provisional_claim_ceiling
blocked_claims
missing_gates
```

## Iterations

### Iteration 1. Baseline And Consequence Source Inventory

Collect source artifacts and classify which prior records can supply:

```text
route alternatives
immediate affordance baselines
route memory / trail effects
bounded response regulation effects
source-current support-seeking regulation effects
Phase 8 readiness records
claim boundary blockers
```

Expected artifacts:

```text
outputs/n14_consequence_source_inventory.json
reports/n14_consequence_source_inventory.md
scripts/build_n14_consequence_source_inventory.py
```

Result:

```text
Status: passed.
Artifact: outputs/n14_consequence_source_inventory.json
Report: reports/n14_consequence_source_inventory.md
Acceptance state: accepted_source_inventory_only_no_ap4
Output digest: 7e8013464efdb35805bc9aa9b765a5c81afaa2a1f0d7210706d43ddd06a41513
```

Iteration 1 classified seven source rows: N06 route arbitration, N08
serialized memory affordance, N08 geometry memory boundary, N09 bounded
regulation, N12 Phase 8 readiness, N13 support stress, and N13 closeout/handoff.
No final `AP4`, Phase 8, native support, intention, or agency claim is opened.

Interpretation:

```text
N14 has sufficient pinned source coverage to proceed to schema and later route
consequence record construction. It does not yet build pre-selection
consequence records or show route selection by consequences.
```

Iteration 1 must not assign final `AP4`.

### Iteration 2. Consequence Selection Schema And AP4 Gate

Freeze the N14 schema:

```text
consequence record fields
route candidate fields
eligible candidate completeness and rejected-candidate record fields
selection rule fields
tie-policy fields
affordance/consequence rank conflict fields
projection basis and prediction-match fields
budget fields
missing consequence record rejection rules
stale-record rules
artifact-only replay, snapshot/load, and order-inversion replay fields
negative controls
claim flags
AP4 acceptance gates
```

Expected artifacts:

```text
outputs/n14_consequence_selection_schema_v1.json
reports/n14_consequence_selection_schema_v1.md
scripts/build_n14_consequence_selection_schema_v1.py
```

Result:

```text
Status: passed.
Artifact: outputs/n14_consequence_selection_schema_v1.json
Report: reports/n14_consequence_selection_schema_v1.md
Acceptance state: accepted_schema_freeze_no_row_validation
Output digest: 56a2080a76f941e77e7a822874fa62e292f34452c06f02cbb8e971bccc540217
```

Iteration 2 froze the N14 AP4 gate and row schema, including candidate-set
completeness, derivation/projection basis, affordance/consequence conflict
resolution, snapshot/replay requirements, missing-record rejection, tie policy,
and expanded false claim flags. Row validation starts in Iterations 3-7.

Interpretation:

```text
N14 has a strict validation contract for later AP4 candidate rows. It does not
validate route consequence records or support AP4.
```

### Iteration 3. Route Consequence Record Candidate

Construct pre-selection consequence records for candidate routes. This
iteration records downstream support, memory, and regulation effect descriptors
but does not yet claim consequence-sensitive selection.

Expected artifacts:

```text
outputs/n14_route_consequence_records.json
reports/n14_route_consequence_records.md
scripts/build_n14_route_consequence_records.py
```

Acceptance state:

```text
accepted_route_consequence_records_no_selection
```

Result:

```text
Status: passed.
Artifact: outputs/n14_route_consequence_records.json
Report: reports/n14_route_consequence_records.md
Output digest: 9eef9c0bbcfd64004915259964ddcbb39efb32563fec5975a6bb30684d83d253
```

Interpretation:

```text
N14 now has source-backed pre-selection route consequence records for the
route_a/route_b candidate set. Immediate affordance favors route_a, while the
serialized memory-dominant consequence score ranks route_b higher. Support and
regulation sources are compatible but not route-specific in this iteration. No
selected route, AP4 support, intention, agency, or native support claim is
opened.
```

Required checks:

```text
records serialized before selection
source digests pinned
prediction basis pinned
derivation policy pinned
source window pinned
support/memory/regulation descriptors explicit
consequence score components serialized
consequence rank derived from score components
memory-dominant scope recorded
bounded horizon present
observed downstream effect recorded when horizon is evaluated
prediction match status recorded
budget surfaces present
hidden outcome table absent
post-hoc scoring absent
```

### Iteration 4. Consequence-Sensitive Selection Candidate

Apply a deterministic selection rule to route candidates using the
pre-selection consequence records and budget validity.

Expected artifacts:

```text
outputs/n14_consequence_sensitive_selection_candidate.json
reports/n14_consequence_sensitive_selection_candidate.md
scripts/build_n14_consequence_sensitive_selection_candidate.py
```

Acceptance state:

```text
accepted_consequence_sensitive_selection_candidate_pending_controls
```

Result:

```text
Status: passed.
Artifact: outputs/n14_consequence_sensitive_selection_candidate.json
Report: reports/n14_consequence_sensitive_selection_candidate.md
Selected route: route_b
Rejected route: route_a
Provisional AP level: AP4_candidate
Output digest: d867b665e3ca96df4a78576b89fb2b89a19ff2761f0099e48d057f00c6b8cfdd
```

Interpretation:

```text
N14 now has a provisional AP4 candidate selection. The deterministic
artifact-only rule selects route_b by derived, memory-dominant pre-selection
consequence rank even though immediate affordance favors route_a. Current
missing/stale/budget handling is recorded as policy only; final AP4 remains
unsupported until adversarial controls, replay/snapshot checks, and
claim-boundary classification pass.
```

Required checks:

```text
all eligible route candidates in the bounded selection window are recorded
rejected candidate records are present
candidates missing consequence records are rejected
immediate_affordance_rank is recorded
consequence_rank is recorded
consequence_score_components are serialized
consequence_rank is derived from serialized score components
selected_rank is recorded
matched or conflicting affordance case is present
affordance_consequence_conflict_resolved_by_consequence = true
tie policy is explicit and replayable
control handling is recorded as policy only until Iteration 5
```

Iteration 4 may assign only `provisional_ap_level = AP4_candidate`. Final AP4
requires Iterations 5-7.

### Iteration 5. Hidden Outcome, Post-Hoc, Stale, And Budget Controls

Run the core N14 controls:

```text
hidden outcome table blocked
post-hoc consequence scoring blocked
stale consequence record blocked
budget-invalid route blocked
missing consequence record blocked
candidate-set cherry-picking blocked
tie-policy ambiguity blocked
immediate-affordance-only relabel blocked
matched affordance conflict resolved by consequence
fixture-label preference blocked
semantic intention relabel blocked
agency relabel blocked
native support relabel blocked
identity acceptance relabel blocked
selfhood relabel blocked
personhood relabel blocked
biological behavior relabel blocked
semantic choice relabel blocked
unrestricted agency relabel blocked
```

Expected artifacts:

```text
outputs/n14_consequence_control_matrix.json
reports/n14_consequence_control_matrix.md
scripts/build_n14_consequence_control_matrix.py
```

Acceptance state:

```text
pending_not_run
```

### Iteration 6. Consequence Perturbation And Replay Matrix

Stress the candidate by changing support, memory, and regulation consequence
records under controlled variants. The route ranking should change only when
source-backed consequence inputs change and should replay identically for the
same inputs.

Expected artifacts:

```text
outputs/n14_consequence_perturbation_matrix.json
reports/n14_consequence_perturbation_matrix.md
scripts/build_n14_consequence_perturbation_matrix.py
```

Acceptance state:

```text
pending_not_run
```

Required regimes:

```text
support-preserving route preferred when support risk is active
memory-stabilizing route preferred when memory effect dominates
regulation-restoring route preferred when regulation deficit is active
budget-invalid high-consequence route rejected
stale consequence record rejected
duplicate replay stable
artifact-only replay stable
snapshot/load replay stable
order inversion replay stable
runtime_state_used = false
```

### Iteration 7. Claim Boundary And AP4 Classification

Freeze the N14 claim boundary and determine whether `AP4` is supported.

Expected artifacts:

```text
outputs/n14_claim_boundary_record.json
reports/n14_claim_boundary_record.md
scripts/build_n14_claim_boundary_record.py
```

Acceptance state:

```text
pending_not_run
```

Required false flags:

```text
agency_claim_opened = false
intention_claim_opened = false
semantic_goal_ownership_opened = false
identity_acceptance_opened = false
selfhood_opened = false
semantic_choice_opened = false
personhood_or_biological_behavior_opened = false
unrestricted_agency_opened = false
native_support_opened = false
fully_native_integration_opened = false
phase8_opened = false
```

### Iteration 8. N14 Closeout And N15 Handoff

Close hypotheses, freeze the supported AP level, list blockers, and decide
whether the next work is N15 or targeted Phase 8.

Expected artifacts:

```text
outputs/n14_closeout_and_handoff.json
reports/n14_closeout_and_handoff.md
scripts/build_n14_closeout_and_handoff.py
```

Acceptance state:

```text
pending_not_run
```

N14 closes only when every source row is classified, every AP4 gate is either
validated or recorded as a blocker, every control has a pass/fail result, and
all unsafe claim flags remain false.

## Claim Boundary

```text
consequence-sensitive route selection != intention
expected downstream support effect != semantic goal ownership
support-preserving route choice != agency
memory-sensitive route choice != identity acceptance
regulation-sensitive route choice != goal ownership
route preference != selfhood
artifact-level AP4 != native support
N14 AP4 != fully native agentic-like integration
```
