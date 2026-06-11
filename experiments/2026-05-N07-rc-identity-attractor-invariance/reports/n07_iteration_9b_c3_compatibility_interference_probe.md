# N07 Iteration 9-B C3 Compatibility And Interference Probe

Status: `passed`

Iteration 9-B ran the frozen C3/T7 fixture as an experiment-local
compatibility probe. Basin A and Basin B both have source-backed support rows
in this artifact, shared neighborhood `U` is explicit, and all compatibility
metrics are derived from serialized probe rows. The result remains an ID5
compatibility candidate pending Iteration 9-C artifact-only replay.

## Interpretation

Iteration 9-B is a positive one-window C3/T7 compatibility probe: Basin A retains coherent, legible support near source-backed Basin B, and Basin B retains support near A, under the frozen shared-U compatibility metric contract.

What it shows:

- A and B are compatible as distinct support areas in this serialized shared-U probe window without collapsing into ambiguous overlap.
- The shared neighborhood permits bounded interaction without destructive interference under the frozen thresholds for this window.
- Wrong-basin leakage stays below threshold, so the probe does not show evidence being captured by the competitor basin.
- The positive compatibility result uses declared support rows and serialized metrics, not hidden support fields.

Simulation scope:

- dynamic LGRC steps run: `0`
- probe windows: `1`
- prolonged simulation run: `False`
- prolonged simulation result: `not_tested`

9-B emits source-backed support, metric, and control rows for one compatibility window. It does not iterate the A/B/shared-U system forward through repeated LGRC steps.

Prolongation expectation:

Unknown from 9-B. If the simulation is prolonged, A/B support could remain separated, drift below retention threshold, leak into the wrong basin, develop destructive interference, or expose budget drift. Those are exactly the conditions a future 9-B-stress or post-9-C stress iteration should measure rather than infer.

Identity-ladder effect:

- strengthens: `ID5_identity_candidate_with_C3_compatibility_evidence`
- does not yet promote to: `ID6`
- blocker: `c3_artifact_replay_pending_iteration_9c`

Why not ID6 yet:

9-B is a source-backed one-window probe artifact. C3 needs Iteration 9-C artifact-only replay to prove the compatibility chain can be reconstructed without private runtime state, and a separate prolonged compatibility stress probe would be needed to claim multi-step persistence of the A/B relation.

Control meaning:

The six source control rows show the compatibility gate has separate failure modes for destructive interference, ambiguous overlap, wrong-basin leakage, hidden support, budget drift, and support drift. A future closeout cannot collapse these into one generic blocker.

Claim boundary:

This is structural compatibility evidence for coherence-basin identity. It is not identity acceptance, RC identity collapse, semantic choice, agency, biological identity, personhood, movement, or unrestricted identity.

## Compatibility Metrics

| Metric | Value | Threshold | Comparison | Passed |
|---|---:|---:|---|---|
| `a_support_retention_near_b` | `0.952348066298` | `0.85` | `greater_than_or_equal` | `True` |
| `b_support_retention_near_a` | `0.958333333333` | `0.85` | `greater_than_or_equal` | `True` |
| `destructive_interference_score` | `0.047619047619` | `0.15` | `less_than_or_equal` | `True` |
| `ambiguous_overlap_score` | `0.0` | `0.2` | `less_than_or_equal` | `True` |
| `wrong_basin_leakage_score` | `0.04` | `0.1` | `less_than_or_equal` | `True` |
| `hidden_support_rejection_rule` | `0` | `0` | `must_equal` | `True` |

## Controls

| Control | Status | Primary Blocker | Derived Ceiling |
|---|---|---|---|
| `destructive_interference` | `blocked` | `destructive_interference` | `ID5` |
| `ambiguous_overlap` | `blocked` | `ambiguous_overlap` | `ID5` |
| `wrong_basin` | `blocked` | `wrong_basin` | `ID5` |
| `hidden_support_field` | `blocked` | `hidden_support_field` | `ID5` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID5` |
| `support_drift_beyond_threshold` | `blocked` | `support_drift_beyond_threshold` | `ID5` |

## Claim Boundary

- `derived_id_ceiling`: `ID5`
- `id6_claimed`: `False`
- `id6_blocker`: `c3_artifact_replay_pending_iteration_9c`
- all claim flags false: `True`

## Checks

| Check | Passed |
|---|---|
| `A_B_U_node_sets_disjoint` | `True` |
| `A_support_digest_recomputes` | `True` |
| `A_support_row_source_backed` | `True` |
| `B_support_digest_recomputes` | `True` |
| `B_support_row_source_backed` | `True` |
| `all_metric_rows_passed` | `True` |
| `artifact_replay_pending` | `True` |
| `budget_exact` | `True` |
| `candidate_boundary_rung_allowed` | `True` |
| `candidate_claim_flags_false` | `True` |
| `claim_flags_false` | `True` |
| `compatibility_gate_passed` | `True` |
| `control_blockers_distinct` | `True` |
| `control_blockers_match_fixture` | `True` |
| `control_ceilings_id5` | `True` |
| `control_count_matches_fixture` | `True` |
| `controls_are_source_rows` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id5` | `True` |
| `fixture_schema_matches` | `True` |
| `fixture_status_passed` | `True` |
| `id6_not_claimed` | `True` |
| `metric_count_matches_fixture` | `True` |
| `native_policy_blocker_recorded` | `True` |
| `next_iteration_is_9c` | `True` |
| `no_src_changes_required` | `True` |
| `route_movement_oscillator_topology_context_only` | `True` |
| `semantic_competition_not_agency` | `True` |
| `source_artifact_hashes_present` | `True` |
| `source_iteration_7b_passed` | `True` |
| `source_iteration_8_passed` | `True` |
| `status_passed` | `True` |
| `visuals_not_evidence` | `True` |

## Artifact Digests

```json
{
  "A_support_area_row_digest": "e15784368f0482c69054b69660469228127790cb4c4a8ec5d31ce6179f0697da",
  "B_support_area_row_digest": "bcca680261e60cf5d87edb9441fb24ba6029997f8a863bb642dc90bda5e57ad9",
  "candidate_row_digest": "843a3d09c56ba4e52291c3cc8b1d988f9afd3f044bdb90aa2b6b9b044cce993f",
  "checks_digest": "9056b4a1e62a600782dfac4f287c0240f9a054308cea16630d66cfdda378edc3",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "compatibility_record_digest": "5557960abd77fd4da5e2dcc8cc6d5b1cd7b069e1bb5d778853df2626a40e9aa1",
  "control_rows_digest": "ac5530f3cddb8b22d42425f404b6b323196b171130e04ea16c378c2fd30b6d4f",
  "interpretation_digest": "852cb936aa0b9bbb627e3afe73675730f1f3b5f5133c1ae2c9f0f7345e523a65",
  "metric_records_digest": "ebfcf10f9393d5386853fe5b1598d7a20603cc4084c995a3b15d763ae9d64913",
  "shared_u_row_digest": "a7c45b58886bf1780d07da5c94456e31d1c50a9bd399273782d035dec653ac0d"
}
```

## Acceptance

Iteration 9-B passes if the C3 fixture emits source-backed compatibility evidence and source control rows while keeping artifact replay, ID6, identity acceptance, RC identity collapse, agency, and semantic choice unclaimed.

Achieved: `True`
