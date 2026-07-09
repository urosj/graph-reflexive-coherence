# N30 Iteration 6 - Later Eligibility / Susceptibility Probe

Status: `passed`

Acceptance state:
`accepted_provisional_M2_later_eligibility_dependency_candidate_pending_I7_controls`

Output digest: `44281258a0b7f62fa01a067bd4e308c4d35996e7c36333e2987458c672d3a7f4`

## Scope

I6 tests whether the I5/I5-A changed medium surfaces condition a later
eligibility/susceptibility result. It consumes the exact I5/I5-A surface IDs
and the N28 same-policy boundary transition traces.

This is not final N30-C5. I6 opens provisional M2 input evidence, but the full
N30-C5 minimal shared-medium participation claim remains blocked until I7 runs
the replay and relation-control matrix.

## Result

```text
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
n30_closeout_ceiling = N30-C4_with_provisional_C5_input_evidence
later_eligibility_dependency_evidence_opened = true
n30_c5_input_evidence_supported = true
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
runtime_origin = inherited_N28_source_current_transition_artifacts
n30_fresh_runtime = false
```

## Candidate Rows

- n30_i6_row_01_i5_single_shell_later_eligibility_candidate: surface=n28_i4a_neighbor_capacity_shell_beta, effect_vs_neutral=1.028056, min_margin=0.002, decision=supported_provisional_M2_later_eligibility_candidate_pending_I7_controls
- n30_i6_row_02_i5a_split_shell_later_eligibility_candidate: surface=n28_i4a2_split_neighbor_capacity_shell_epsilon, effect_vs_neutral=1.028056, min_margin=0.002, decision=supported_provisional_M2_later_eligibility_candidate_pending_I7_controls

## Geometric Interpretation

I5/I5-A established that a participant event can change a non-private neighbor
capacity surface. I6 adds the next dependency leg: the later same-policy
boundary-edge transition stays eligible only when the changed medium-surface
axes remain above their declared thresholds. The neutral-gap counterfactual has
the same stability context but no medium-surface gain, so it remains
unclassified. The extractive-cross counterfactual changes the surface in the
opposite direction, so it remains extractive rather than becoming generic
shared-medium eligibility.

Geometrically, the medium surface is not just present. Its distinguishability,
support, boundary, and environment-capacity deltas form the later eligibility
condition. The margin is narrow but positive, so I6 is a provisional M2 input
candidate, not a robust C5 closeout.

## Margin Semantics

The `0.002` margin is raw threshold headroom, not transmitted mass. It is the
smallest distance between a later medium-conditioned axis and its declared
surface-change threshold:

```text
environment_capacity_delta = 0.092 against threshold 0.090
neighbor_boundary_delta = 0.082 against threshold 0.080
neighbor_distinguishability_delta = 0.082 against threshold 0.080
neighbor_support_delta = 0.052 against threshold 0.050

mean observed axis delta ~= 0.077
mean threshold ~= 0.075
raw mean headroom ~= 0.002
relative headroom vs mean threshold ~= 2.7%
mean normalized score = 1.028056
```

So I6 is narrow in absolute raw-margin terms, but the normalized reading is
approximately 2.7-2.8% over the mean declared threshold. The weakest raw
headroom remains `0.002`, so the row stays provisional pending I7 controls.

## Claim Boundary

```text
M2 input evidence = supported provisionally
final C5 minimal shared-medium participation = blocked pending I7
shared-medium coordination = false
parent-basin modulation = false
resonant alignment = false
native shared-medium organization = false
agency / selfhood / sentience / ecology regime = false
```

## Artifacts

| Role | Path |
|---|---|
| i6_later_eligibility_aggregate_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i6_later_eligibility_aggregate_trace.json` |
| i6_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i6_claim_boundary_guard.json` |
| susceptibility_or_eligibility_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i5_single_shell_susceptibility_or_eligibility_trace.json` |
| coupled_relation_lineage_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i5_single_shell_coupled_relation_lineage_trace.json` |
| susceptibility_or_eligibility_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i5a_split_shell_susceptibility_or_eligibility_trace.json` |
| coupled_relation_lineage_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_i6_artifacts/i5a_split_shell_coupled_relation_lineage_trace.json` |

## Checks

- i5_i5a_i5b_inputs_passed: true
- later_metric_predeclared_and_effect_positive: true
- counterfactuals_separate_eligibility_from_labels: true
- coupled_relation_chain_present: true
- transition_policy_not_retuned_or_mutated: true
- final_c5_c6_claims_blocked_pending_i7: true
- artifact_manifest_sha256_matches: true
- derived_report_only_false_for_candidates: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
