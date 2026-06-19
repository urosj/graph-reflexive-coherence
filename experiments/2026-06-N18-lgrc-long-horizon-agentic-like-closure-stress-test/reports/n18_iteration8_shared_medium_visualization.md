# N18 Iteration 8 Shared-Medium Visualization

This is a supporting artifact-level visualization for N18 Iteration 8.
It is not a native LGRC telemetry run and does not create new evidence.

Generated artifacts:

- Stress relation graph: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_graph.png`
- Stress sequence panel: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_sequence.png`
- Stress animation: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_shared_medium_animation.gif`
- B4/C5 source geometry graph: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_graph.png`
- B4/C5 source geometry sequence panel: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_sequence.png`
- B4/C5 source geometry animation: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization/n18_i8_b4c5_source_geometry_animation.gif`
- Manifest: `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_iteration8_shared_medium_visualization.json`

Renderer boundary:

```text
supporting artifact-level visualization only; animation shows source-row/phase progression from the I8 matrix plus B4/C5 source geometry, not native LGRC runtime execution
```

Summary:

```json
{
  "boundary_to_loop_feedback_score": 0.8,
  "budget_headroom": 0.01,
  "highest_positive_stress_ladder_rung": "L5",
  "iteration": 8,
  "limit_rows": {
    "n18_i8_row_02_h4_shared_medium_merge_pressure_limit": "partial",
    "n18_i8_row_03_h4_shared_medium_budget_limit": "rejected",
    "n18_i8_row_04_h4_compound_shared_medium_limit": "rejected"
  },
  "max_supported_horizon": "h4",
  "positive_row": "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
  "positive_row_decision": "supported",
  "relabel_controls": {
    "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control": "rejected",
    "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control": "rejected",
    "n18_i8_row_07_resource_shared_medium_merge_relabel_control": "rejected"
  }
}
```

Geometry summary:

```json
{
  "basin_count": 2,
  "basin_separation_score": 0.74,
  "boundary_edges": [
    {
      "event": "shared_medium_boundary_exchange",
      "left": "b4_c5_a2",
      "left_side": "derived_internal_side",
      "right": "b4_c5_medium",
      "right_side": "derived_external_side",
      "weight": 0.1
    },
    {
      "event": "neighbor_medium_exchange",
      "left": "b4_c5_neighbor0",
      "left_side": "derived_external_side",
      "right": "b4_c5_medium",
      "right_side": "derived_external_side",
      "weight": 0.08
    }
  ],
  "boundary_exclusivity_score": 0.73,
  "geometry_source_row": "n16_i6_row_b4_c5",
  "geometry_source_status": "source_backed_artifact_geometry",
  "i8_overlay_role": "h4_L5_stress_overlay_not_geometry_source",
  "i8_overlay_row": "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
  "leakage_into_neighbor_basin": 0.07,
  "merge_confusion_pressure": 0.14,
  "native_lgrc_runtime_geometry_checkpoint_available": false,
  "nodes": {
    "b4_c5_a0": "derived_internal_side",
    "b4_c5_a1": "derived_internal_side",
    "b4_c5_a2": "derived_internal_side",
    "b4_c5_medium": "derived_external_side",
    "b4_c5_neighbor0": "derived_external_side",
    "b4_c5_neighbor1": "derived_external_side"
  },
  "shared_medium_leakage": 0.108,
  "shared_medium_pressure": 0.44
}
```

Claim boundary:

```text
does not add evidence, does not open AP8, does not open Phase 8, does not support agency or native support
```
