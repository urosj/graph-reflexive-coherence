# GRC9V3 Lane C Comparison Setup

Date: 2026-05-06

Status: prepared and executed from the experiment family

Companion implementation lane:

- [GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md)
- [GRC9V3-CanonicalColumnH-ImplementationChecklist.md](./GRC9V3-CanonicalColumnH-ImplementationChecklist.md)

Execution artifact:

- `experiments/2026-05-N01-grc9v3-properties/scripts/run_lane_c_comparison.py`

Execution result:

- comparison rows: `60`;
- Lane A candidates/refinements: `25 / 25`;
- Lane B candidates/refinements: `40 / 40`;
- direct Lane B column-H proxy-branch rows: `15`;
- degree-8 near-saturation remains blocked.

Classification:
    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

## Purpose

Lane C is an analysis setup for comparing the frozen Lane A baseline against
the opt-in Lane B v1 runtime lane.

Lane C is not a third spark predicate. It does not change Lane A or Lane B.
It only defines how to run a small shared fixture subset under both lanes and
how to report the difference without retroactively reinterpreting old Lane A
artifacts.

## Lanes

| Lane | `spark_lane` | Role |
| --- | --- | --- |
| Lane A | `current_hybrid_signed_hessian` | Frozen default baseline. Column-H/cancellation is derived and non-gating. |
| Lane B v1 | `grc9v3_column_h_assisted` | Opt-in GRC9V3 column-H-assisted lane. Direct column-H proxy-branch evidence exists only when candidate payloads record this lane and a column-H branch reason. |
| Lane C | `comparison` | Analysis pass over paired Lane A/Lane B artifacts. Not a runtime lane. |

## Core Questions

Lane C should answer only these first-order questions:

- Which column effects were already visible under Lane A as derived proxies?
- Which effects become direct proxy-branch gate evidence only under Lane B?
- Does Lane B change candidate count, refinement frequency, column memory, or
  configured-window child-basin outcomes in the selected fixtures?

It should not claim landscape generality, degree-8 near-saturation support, or
identity fission from mechanical expansion alone.

## Shared Fixture Subset

Use seed `0` and the existing completed fixture families as the first Lane C
subset.

| Comparison slice | Source artifacts | Fixture ids / condition ids | Required comparison |
| --- | --- | --- | --- |
| Experiment B column-interface cancellation | `outputs/experiment_b_column_interface_cancellation_manifest.json` | `b_column_1_near_cancellation_near_zero_seed_0`, `b_column_2_near_cancellation_near_zero_seed_0`, `b_column_3_near_cancellation_near_zero_seed_0` | Lane A derived column proxy scores versus Lane B direct column-H values and branch hits. |
| Experiment C / D4 saturation and spark gating | `outputs/experiment_c_saturation_manifest.json`, `outputs/d4_saturation_summary.json` | `C1_degree_7_stressed`, `C2_degree_8_stressed`, `C3_degree_9_stressed`, `C5_degree_9_stable_hessian` | Candidate/refinement counts, degree-9 requirement, large/fullness-only negatives, and Lane B branch attribution. |
| Experiment D / D5 refinement and interface memory | `outputs/experiment_d_refinement_identity_manifest.json`, `outputs/d5_interface_memory_summary.json` | `d_equal_transfer_refinement`, `d_column_1_skewed_transfer`, `d_column_2_skewed_transfer`, `d_column_3_skewed_transfer`, `d_degree_8_no_refinement_control` | Reassignment map, old-column preservation, budget, and post-window endpoint persistence where Lane B refines. |
| D8 identity emergence | `outputs/d8_identity_emergence_summary.json` | Same Experiment D refinement conditions, only if Lane B produces refinement events | Configured-window persistent child-basin criteria, lineage, budget audit, and negative controls. |
| D1 / D3 near candidate events | `outputs/d1_factorization_summary.json`, `outputs/d3_transpose_summary.json` | Existing transform ids: `identity`, `row_column_transpose`, `column_permutation_312`, `row_permutation_231`, `degree_preserving_random_relabel` | Factorization/transpose evidence near Lane B candidate events, with sampled controls kept labeled as sampled. |

Do not include the full A-G/D1-D8 family in the first Lane C pass. The point is
to test the spark-lane delta, not to rerun the entire experiment program.

## Runtime Parameters

Lane A params:

```text
spark_lane = current_hybrid_signed_hessian
hessian_backend = row_basis_diagonal
boundary_mode = prune
seed = 0
```

Lane B v1 params:

```text
spark_lane = grc9v3_column_h_assisted
hessian_backend = row_basis_diagonal
boundary_mode = prune
seed = 0
enable_column_h_threshold = true
enable_column_h_sign_crossing = false unless a sign-crossing-specific slice is run
store_previous_column_h = false unless sign crossing is enabled
require_active_degree_9 = true
require_sink_for_column_h_spark = true
enable_near_saturation = false
```

Shared thresholds should be copied from the source fixture manifests unless
the comparison explicitly declares a threshold sweep. Any sweep must record the
threshold grid in the manifest and must not overwrite the default Lane B v1
claim.

## Artifact Schema

Use `artifact_schema_version = "grc9v3_lane_c_comparison_v1"` for new Lane C
outputs. Each paired-row artifact should include:

```text
comparison_id
source_experiment_or_discriminator
source_fixture_id
condition_id
transform_id
seed
lane_a_id
lane_b_id
lane_a_runtime_params
lane_b_runtime_params
lane_a_artifact_paths
lane_b_artifact_paths
candidate_count_lane_a
candidate_count_lane_b
refinement_count_lane_a
refinement_count_lane_b
lane_a_column_proxy_status
lane_a_column_proxy_value
lane_b_column_h
lane_b_column_h_branch_hit
lane_b_gate_reasons
lane_b_candidate_event_id
lane_b_linked_expansion_event_id
budget_error_lane_a
budget_error_lane_b
old_column_preservation_lane_a
old_column_preservation_lane_b
post_window_identity_status_lane_a
post_window_identity_status_lane_b
evidence_boundary
```

Lane A column evidence must be labeled:

```text
derived_non_gating
```

Lane B column-H evidence may be labeled:

```text
direct_runtime_proxy_branch
```

only when:

```text
spark_lane == "grc9v3_column_h_assisted"
AND column_h_branch_hit == true
AND gate_reasons contains "column_h_threshold_hit"
    OR "column_h_sign_crossing_hit"
```

## Expected Outputs

Recommended output paths:

```text
outputs/lane_c_comparison_manifest.json
outputs/lane_c_candidate_comparison.csv
outputs/lane_c_refinement_comparison.csv
outputs/lane_c_identity_comparison.csv
outputs/lane_c_branch_attribution.csv
outputs/lane_c_summary.json
reports/lane_c_comparison_report.md
reports/lane_c_blocked_observations.md
```

The report must include:

- Lane A derived proxy versus Lane B direct runtime proxy-branch evidence.
- Candidate/refinement deltas.
- Degree-8 near-saturation remains blocked in Lane B v1.
- Expansion is mechanical; identity requires post-event basin persistence.
- Whether D8 was skipped because Lane B did not produce refinement events.

## Non-Claims

Lane C must not claim:

- Lane B is now the default.
- Old Lane A artifacts contain direct column-H gate evidence.
- Degree-8 near-saturation is implemented.
- Mechanical expansion is identity fission.
- Landscape-general robustness.
- Exhaustive S9 coverage.

## Readiness Check

Lane C is ready to run when:

- Lane A and Lane B tests pass.
- The paired fixture subset above is available.
- Both lane parameter blocks are serialized in every manifest.
- Event payloads are captured for candidate and expansion evidence.
- Reports preserve direct versus derived evidence labels.
