# N11 Iteration 9 Artifact-Only Generalization Validator

Status: `passed`.

## Result

Iteration 9 reconstructed the N11 generalization chain from exported
artifacts only. It validated artifact digests, source links, transfer
row schemas, the context/proxy/support matrix, the longer-horizon
window, negative controls, budget-surface separation, and claim
boundaries without private runtime state.

Current replayed ceiling:

```text
strongest_replayed_gali_level = GALI6
strongest_replayed_claim_ceiling = longer_horizon_generalization_candidate
artifact_only = true
runtime_state_used = false
A7/GALI7 supported = false
```

## Validation Passes

```json
{
  "budget_surface_pass": true,
  "claim_boundary_pass": true,
  "context_proxy_support_matrix_pass": true,
  "longer_horizon_window_pass": true,
  "negative_control_pass": true,
  "source_artifact_digest_pass": true,
  "transfer_row_schema_pass": true
}
```

## Checks

```json
{
  "all_artifact_digests_valid": true,
  "all_artifact_statuses_passed": true,
  "all_artifacts_present": true,
  "all_manifest_required_passes_passed": true,
  "all_source_digest_links_match": true,
  "artifact_only": true,
  "budget_surfaces_validate": true,
  "claim_boundary_validates": true,
  "controls_validate": true,
  "longer_horizon_validates": true,
  "manifest_required_passes_match": true,
  "matrix_validates": true,
  "runtime_state_not_used": true,
  "src_clean_for_iteration_9": true,
  "transfer_rows_validate": true
}
```

## Matrix Summary

```json
{
  "accepted_and_blocked_rows_present": true,
  "accepted_gali5_row_count": 7,
  "accepted_row_count": 12,
  "all_budget_surfaces_separate": true,
  "all_source_status_digest_links_present": true,
  "blocked_row_count": 12,
  "context_variant_count": 3,
  "distinct_blockers_present": true,
  "matrix_cell_digests_valid": true,
  "proxy_variant_count": 2,
  "row_count": 24,
  "row_count_matches_manifest": true,
  "support_variant_count": 4
}
```

## Longer Horizon Summary

```json
{
  "accepted_gali6_row_count": 7,
  "budget_zero_all_windows": true,
  "event_window_order_valid": true,
  "node_plus_packet_budget_error_max": 0.0,
  "proxy_in_band_all_windows": true,
  "row_count": 12,
  "source_current_all_windows": true,
  "support_survives_all_windows": true,
  "transfer_stable_all_windows": true,
  "trend_digests_valid": true,
  "trend_fields_present": true,
  "unstable_window_count": 0
}
```

## Control Summary

```json
{
  "all_claim_flags_false_after_controls": true,
  "all_controls_fail_closed": true,
  "all_controls_passed": true,
  "all_observed_blockers_match_expected": true,
  "all_primary_blockers_distinct": true,
  "control_count": 12,
  "control_record_digests_valid": true,
  "no_generic_failures": true
}
```

## Interpretation

This validator strengthens the artifact-only status of the GALI6 chain.
It does not convert the result into GALI7/A7 or native agency. The
remaining boundary is still broader/general artifact-only integration
and later native absorption, not replayability of the existing GALI6
evidence.

## Acceptance

Iteration 9 passes if an artifact-only validator reconstructs the accepted N11 generalization chain and controls from exported artifacts, with stable digests, event/window ordering, separated budget surfaces, source-current status, and no private runtime fallback.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/run_n11_iteration_9_artifact_only_generalization_validator.py
```

Output digest:

```text
a44607c05a90c9d3169bce2e9fbb4bd560e9811180420631a7ccd1faaf8aa481
```
