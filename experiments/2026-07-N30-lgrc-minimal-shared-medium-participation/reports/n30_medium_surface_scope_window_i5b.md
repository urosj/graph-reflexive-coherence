# N30 Iteration 5-B - Medium Surface Persistence / Scope-Window Probe

Status: `passed`

Acceptance state:
`accepted_C4_M1_scope_window_audit_split_scope_supported_temporal_decay_blocked`

Output digest: `b795a864f4db404b4a620fac248d9fc47f6ef508c2929d6e82639dca9427d956`

## Scope

I5-B audits the persistence and scope limits of I5/I5-A before I6 tries later
eligibility. It consumes I5, I5-A, and the N28 neighbor-capacity stress rows.

This is still C4/M1 only. I5-B does not test later response, trace-mediated
eligibility, minimal shared-medium participation, shared-medium coordination,
or native shared-medium organization.

## Result

```text
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
larger_local_scope_supported = true
shared_global_scope_supported = false
replay_and_stress_variant_persistence_supported = true
longer_temporal_window_supported = false
temporal_decay_window_supported = false
slow_trace_or_medium_memory_supported = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Surface Rows

- I5_single_shell: scope=single_neighbor_capacity_shell, stress_passed=true, minimum_stress_margin=0.014, larger_than_i5=false
- I5A_split_shell: scope=split_shell_neighbor_capacity_surface, stress_passed=true, minimum_stress_margin=0.014, larger_than_i5=true

## Interpretation

I5-B answers the persistence/scope question in two parts.

First, I5-A gives a broader local medium surface than I5: I5 uses one neighbor
capacity shell, while I5-A uses a split-shell neighboring surface. This
supports a local scope broadening, not a global shared medium.

Second, both I5 and I5-A survive replay and the N28 neighbor-capacity
compression stress variant. That supports replay/stress-variant persistence of
the C4 surface trace. It does not support a temporal decay curve, slow trace,
medium memory, or long-horizon persistence. Stress variants and duplicate
replay are not time windows.

I5-B therefore strengthens the C4/M1 surface trace boundary for I6, but it also
prevents I6 from silently inheriting slow-trace or medium-memory evidence.

## Claim Boundary

```text
C4/M1 surface trace admission = supported
larger local split-shell scope = supported
global shared scope = false
C5/M2 later eligibility dependency = false
slow trace / medium memory = false
shared-medium coordination = false
native shared-medium organization = false
```

## Artifacts

| Role | Path |
|---|---|
| medium_surface_window_policy | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_scope_window_i5b_artifacts/medium_surface_window_policy.json` |
| medium_surface_scope_window_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_scope_window_i5b_artifacts/medium_surface_scope_window_matrix.json` |
| medium_surface_persistence_decay_limit | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_scope_window_i5b_artifacts/medium_surface_persistence_decay_limit.json` |
| i5b_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_scope_window_i5b_artifacts/i5b_claim_boundary_guard.json` |

## Checks

- i5_and_i5a_inputs_passed_c4_only: true
- n28_neighbor_capacity_stress_rows_passed: true
- split_shell_larger_local_scope_supported: true
- temporal_decay_and_slow_trace_not_overclaimed: true
- c4_c5_boundary_preserved: true
- artifact_manifest_sha256_matches: true
- derived_report_only_false_for_candidate: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
