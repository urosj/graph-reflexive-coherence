# B2-GR - GRC9V3 Retention And Mediation Constructibility

B2-GR is the first GRC-side continuation after B1-GR. It asks whether the
unchanged synchronous `GRC9V3` runtime can produce stronger retention and
mediation witnesses than B1-GR found, before any runtime extension is selected
or specified.

## Experiment State

```text
experiment_id = B2-GR
status = iteration_3_effect_scope_active_nulls_passed_awaiting_human_review
source_experiment = B1-GR
source_closeout = accepted_GRV-C6
source_maximum_retention_rung = GRR2
target_rungs = GRR3, GRR4, GRR5
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
spec_extension_authorized = false
positive_B2_evidence_opened = false
closeout_ladder_rung_assigned = true
current_closeout_rung = B2-C0
iteration_1_source_record_count = 25
iteration_1_consumed_field_record_count = 71
iteration_1_accepted_B1_branch_count = 48
iteration_1_unchanged_runtime_file_count = 23
iteration_1_checks = 33_of_33_passed
iteration_1_preliminary_result = superseded_before_human_acceptance
iteration_1_acceptance_anchor_created = true
iteration_2_input_revision = b6669b8e0ad1ad70def6ab4c99dbe926a9e906ee
iteration_2_checks = 66_of_66_passed
iteration_2_candidate_required_field_count = 183
iteration_2_carrier_definition_count = 3
iteration_2_active_null_definition_count = 52
iteration_2_maximum_discovery_rows = 9648
iteration_2_preliminary_result = superseded_before_human_acceptance
iteration_2_constitutional_revision_execution = passed_and_accepted
iteration_2_artifact_payload_sha256 = bae04386692f35749c0897292f5a3ae99f8364a7251c6b7826817bdc8a4e4e28
iteration_2_receipt_payload_sha256 = 764c2f42ef6d28b4dda6c6d9f18e829d317c2ec60687e255597f79819185b088
iteration_2_acceptance_anchor_created = true
assigned_closeout_rung = B2-C1
ready_for_iteration_3 = true
iteration_3_required_active_null_count = 52
iteration_3_threshold_calibration_recipe_count = 4
iteration_3_preliminary_input_revision = 1e623e68a062bbaaccd25f144de9601b15e05e98
iteration_3_preliminary_checks = 29_of_29_passed
iteration_3_preliminary_failed_closed_rows = 52
iteration_3_preliminary_failed_open_rows = 0
iteration_3_preliminary_all_threshold_calibrations_usable = true
iteration_3_preliminary_artifact_payload_sha256 = 7260e5e2e1b23a97554107ad72f39f47f0e758a84797d5a9e3931ce1f5b97e0b
iteration_3_preliminary_threshold_payload_sha256 = c71388f43c5e16718aa0405bca5d383343193055363e0d6220592d2d6e7a55fa
iteration_3_preliminary_receipt_payload_sha256 = 340ba221310d147151f00a3e91545ea2bc99364cfce94e09e7aa1ae7f560920a
iteration_3_preliminary_execution = superseded_before_human_review
iteration_3_preliminary_result_revision = 99e814ffb03d4f71fe590f9842938605ba617a0e
iteration_3_hardened_input_revision = e33f43da6f015e275eb8e53699d50842005c00d3
iteration_3_hardened_checks = 48_of_48_passed
iteration_3_hardened_validator_case_count = 162
iteration_3_hardened_atomic_null_count = 52
iteration_3_hardened_pass_through_sentinel_count = 52
iteration_3_hardened_failed_open_count = 0
iteration_3_hardened_artifact_payload_sha256 = 52384117c91e10ba053eec2d0edbb451f4c487162c5a1fac4dcf2b77f801d4c4
iteration_3_hardened_threshold_payload_sha256 = 5fd452312900680bb0374f02b29e28d33157642818f1a1b9af64280caa9e3324
iteration_3_hardened_receipt_payload_sha256 = 36dc10d022799e8e3f88e3bcaa6b42006096c7ee2a12388a405cdf3a0e4f67fe
iteration_3_adjudicator_sha256 = 4ffc3208bfd8caa77e7c6b9486e126014df1fc96e716a5f252384ece65b68e84
iteration_3_hardened_execution = superseded_before_human_review
iteration_3_hardened_result_revision = b27d89ab5b0e022b77c61ec71dcbfa1608052ac5
iteration_3_effect_scope_input_revision = 8f791ed23f85c460d37d71317d63a85da3e3147f
iteration_3_effect_scope_checks = 59_of_59_passed
iteration_3_effect_scope_validator_case_count = 162
iteration_3_effect_scope_distribution = 32_rung_8_lane_5_route_4_claim_2_duplicate_1_robustness
iteration_3_effect_scope_artifact_payload_sha256 = a9749a11bde99da30a40aeea20114a8fabe76bf1db2b55d62d8ac79824d04d6a
iteration_3_effect_scope_threshold_payload_sha256 = 297bb166ef65b66e5e66a4c5d79e8ae7e21be4a2c71224a8c3054364481941e3
iteration_3_effect_scope_receipt_payload_sha256 = 9f13fda65a07659f7d34122f9b903a065961c906680013424850fd7351042e64
iteration_3_effect_scope_adjudicator_sha256 = ee323a5c115705f6ef9bb1bed9c84f56ed0458c35f92e08449907b22e0e803c6
iteration_3_effect_scope_execution = passed_awaiting_human_review
iteration_3_acceptance_anchor_created = false
ready_for_iteration_4 = false_pending_I3_execution_and_acceptance
extension_target_selected = false
B1_L_execution_authorized = false
N32_selected = false
```

## Why This Experiment Comes Before An Extension

B1-GR did not prove that `GRR3-GRR5` are impossible in current `GRC9V3`. It
found them unresolved under the tested branches and interventions. Its accepted
handoff therefore routes first to an unchanged-runtime constructibility search.

B2-GR must distinguish:

```text
no witness found in the declared search envelope
  != mathematical or mechanical impossibility

persistent branch-family displacement
  != transverse retained carrier

different no-probe baseline transport
  != carrier-conditioned later probe response

reduced frozen-W sensitivity
  != native full-step mediation

missing role identified by evidence
  != extension automatically selected
```

Only the final B2-GR route decision may recommend a target-specific,
revision-distinct extension specification. Any such implementation work must
occur later under top-level `specs/`, `implementation/`, `src/`, and `tests/`.

## Central Question

```text
Can unchanged GRC9V3 produce a runtime-reached, branch-relative retained
carrier that occupies an isolated temporal slow cluster, changes a later
matched native probe, and survives reset/swap/bypass/replay controls; or does
the bounded search identify a specific missing role without converting search
failure into a runtime-impossibility claim?
```

## Retention Ladder

The B1-GR ladder is retained unchanged:

| Rung | Meaning |
| --- | --- |
| `GRR0` | No attributable conductance or joint carrier. |
| `GRR1` | Activity changes a causal conductance or joint state. |
| `GRR2` | The difference persists after the forming intervention stops. |
| `GRR3` | The persistent difference occupies an isolated temporal slow cluster. |
| `GRR4` | A matched later probe causally depends on the candidate carrier. |
| `GRR5` | Write, persistence, mediation, reset/swap controls, and replay pass. |

`GRR5` remains a retained-geometry or joint-retention candidate ceiling. It is
not core Read-Back unless a present-current-conditioned directional read
relation satisfying the passive null is independently established.

## Local Closeout Ladder

```text
B2-C0 = source and B1-GR handoff admission accepted
B2-C1 = constructibility protocol and schema accepted
B2-C2 = false-positive surface and active nulls accepted
B2-C3 = runtime-reached discovery candidate set accepted and frozen
B2-C4 = GRR3 witness classification accepted and frozen
B2-C5 = GRR4 witness classification accepted and frozen
B2-C6 = bounded closeout and next-route decision accepted
```

The closeout ladder records experiment completeness, not a positive retention
rung. The initialized scaffold has no closeout rung. B2-GR may close at
`B2-C6` with `GRR2`, a higher rung, a bounded negative search, mixed evidence,
or an unresolved result. Iteration 7's `GRR5` qualification is consumed by the
Iteration 8 closeout rather than receiving a separate process rung.

## Primary Evidence Lane

The primary `GRR3-GRR5` lane is fixed-topology, event-free, and descended from
an accepted B1-GR branch through unchanged runtime execution. Preparation may
act only through a preregistered upstream driver. Direct authorship of a
candidate carrier or internal causal-state surface remains synthetic control
evidence.

A single deterministic witness with positive admissibility margin can establish
constructibility within the frozen envelope. Failure on other branches or under
substantially different amplitudes bounds robustness; it does not erase an
otherwise valid witness.

The cumulative evidence chain is row-local and lineage-preserving:

```text
admissible upstream driver
-> native runtime write of carrier CARRIER
-> the same carrier lineage persists in admitted slow dynamics
-> the same carrier lineage changes a later matched incremental response
-> controls remove, exchange, or follow that same carrier lineage
```

Direct authorship of the candidate carrier, cross-row rung composition, and
switching carrier classes between `GRR3`, `GRR4`, and `GRR5` are blocked.

## Claim Boundary

B2-GR may support unchanged-runtime constructibility evidence for `GRR3-GRR5`
within a frozen branch, fixture, intervention, and horizon envelope. It may
also identify which causal role remains missing.

It cannot by itself establish:

```text
core Read-Back
native write-back
closed read/write loop
unique retained projector
global nonexistence of GRR3-GRR5 witnesses
runtime extension necessity
automatic selection of current temporalization or oriented current
LGRC retention or Read-Back
B1-L execution
N32 selection
memory, learning, agency, organism, or life
```

## Documents

- [Implementation plan](implementation/GRC9V3RetentionMediationConstructibilityPlan.md)
- [Implementation checklist](implementation/GRC9V3RetentionMediationConstructibilityChecklist.md)
- [Hypotheses and claim boundaries](hypotheses/README.md)
- [Accepted B1-GR next-route handoff](../2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/continuation_readback_next_route_handoff.json)
- [Accepted B1-GR closeout](../2026-08-B1-GR-grc9v3-continuation-readback-verification/reports/b1_grv8_closeout.md)
