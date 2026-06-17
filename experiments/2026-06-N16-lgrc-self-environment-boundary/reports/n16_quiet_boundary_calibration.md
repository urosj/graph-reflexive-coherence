# N16 Quiet Boundary Calibration

Status: `passed`.

## Acceptance State

```text
accepted_quiet_boundary_calibration_no_ap6
```

Iteration 3 is calibration only. It populates B0, B1, and B2 under C0 quiet reference to check that the frozen boundary machinery can distinguish null external coherence, a localized partition, and a quiet support-persistent basin before any robustness claim is made.

It does not prove AP6, run the challenge sweep, run the full control matrix, or evaluate repair/reabsorption behavior.

## Row Outcomes

| Cell | Decision | Boundary Claim Allowed | Classification |
| --- | --- | --- | --- |
| B0_C0 | rejected | False | active_null_external_coherence_rejected_as_boundary_support |
| B1_C0 | partial | False | localized_partition_candidate_under_C0 |
| B2_C0 | supported | False | support_persistent_basin_under_C0_only |

## Calibration Findings

- `B0_C0` is a valid active-null row, but it is rejected as boundary support because external coherence alone produced no derived internal side and no boundary edge.
- `B1_C0` extracts boundary edges and an inside/outside partition, but remains only a localized partition candidate. It does not claim persistence.
- `B2_C0` adds quiet-window stability over B1: derived side assignments and boundary edges remain stable across the C0 window, with support and coherence above the frozen floors.

## Minimum Quiet Baseline

```json
{
  "claim_boundary": "quiet_baseline_for_later_challenges_not_ap6_closeout",
  "maximum_quiet_leakage_ratio": 0.12,
  "minimum_coherence_margin": 0.52,
  "minimum_internal_coherence": 0.84,
  "minimum_internal_support": 0.85,
  "support_sweep": [
    {
      "candidate_internal_coherence": 0.82,
      "candidate_internal_support": 0.78,
      "coherence_margin": 0.46,
      "detectable_partition": true,
      "persistent_under_quiet_window": false,
      "reason": "partition visible but below support persistence floor"
    },
    {
      "candidate_internal_coherence": 0.83,
      "candidate_internal_support": 0.82,
      "coherence_margin": 0.5,
      "detectable_partition": true,
      "persistent_under_quiet_window": false,
      "reason": "quiet partition still below frozen support floor"
    },
    {
      "candidate_internal_coherence": 0.84,
      "candidate_internal_support": 0.85,
      "coherence_margin": 0.52,
      "detectable_partition": true,
      "persistent_under_quiet_window": true,
      "reason": "first quiet calibration point satisfying support and coherence floors"
    }
  ]
}
```

## Boundary Derivation

Boundary-side assignments are derived from support, coherence, and basin-signal thresholds. The case data does not supply trusted `self_region_nodes`, `external_region_nodes`, or boundary labels. Those schema fields are populated after derivation.

B1 derived boundary edges:

```json
[
  {
    "left": "b1_q1",
    "left_side": "derived_internal_side",
    "right": "b1_q2",
    "right_side": "derived_external_side",
    "weight": 0.18
  }
]
```

B2 derived boundary edges:

```json
[
  {
    "left": "b2_q2",
    "left_side": "derived_internal_side",
    "right": "b2_q3",
    "right_side": "derived_external_side",
    "weight": 0.09
  }
]
```

## B2 Cross-Snapshot Stability

```json
{
  "all_snapshots_meet_persistence_floors": true,
  "quiet_window_metrics": [
    {
      "boundary_edge_count": 1,
      "classification_path": "primary_floor",
      "coherence_margin": 0.53,
      "external_coherence": 0.35,
      "internal_coherence": 0.88,
      "minimum_internal_support": 0.86,
      "snapshot_id": "q0"
    },
    {
      "boundary_edge_count": 1,
      "classification_path": "primary_floor",
      "coherence_margin": 0.53,
      "external_coherence": 0.34,
      "internal_coherence": 0.87,
      "minimum_internal_support": 0.85,
      "snapshot_id": "q1"
    },
    {
      "boundary_edge_count": 1,
      "classification_path": "primary_floor",
      "coherence_margin": 0.531667,
      "external_coherence": 0.345,
      "internal_coherence": 0.876667,
      "minimum_internal_support": 0.85,
      "snapshot_id": "q2"
    }
  ],
  "quiet_window_snapshot_count": 3,
  "stable_boundary_edges": true,
  "stable_side_assignments": true
}
```

## Claim Boundary

```text
quiet boundary calibration passed != AP6 supported
localized partition candidate != support-persistent boundary
support-persistent basin under C0 != challenge-stable boundary
artifact-visible boundary separability != selfhood, agency, native support, or life
```

## Checks

```json
{
  "all_boundary_claims_false": true,
  "all_rows_under_c0": true,
  "ap_level_remains_provisional": true,
  "b0_rejected_as_boundary_support": true,
  "b1_boundary_edges_incident_to_both_sides": true,
  "b1_non_persistence_threshold_breaches_recorded": true,
  "b1_partition_candidate_not_persistence": true,
  "b2_all_snapshots_meet_persistence_floors": true,
  "b2_boundary_edges_incident_to_both_sides": true,
  "b2_multi_snapshot_stability_recorded": true,
  "b2_quiet_persistence_stronger_than_b1": true,
  "c0_marked_calibration_only": true,
  "classification_path_recorded": true,
  "minimum_support_baseline_recorded": true,
  "no_externally_supplied_boundary_labels": true,
  "row_count_is_three": true
}
```

## Output Digest

```text
863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1
```
