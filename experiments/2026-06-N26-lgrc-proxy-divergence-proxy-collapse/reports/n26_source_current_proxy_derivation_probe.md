# N26 Iteration 4 - Source-Current Proxy Derivation Probe

Status: `passed`

Acceptance state: `accepted_source_current_pd2_proxy_derivation_candidate_pending_contrast_controls`

## Summary

I4 derives a proxy metric from scoped N25.2 MB6 child-basin replay inputs.
The metric is a local coupling-gap proxy:

```text
proxy_basin_coupling_gap = max(0, 1 - weakest persistence ratio)
```

Both candidate rows have weakest persistence ratio `1.0`, so the derived
gap is `0.0`. This supports PD2 derivation only. It does not support
proxy divergence, proxy collapse, final AP5, native support, agency,
sentience, Phase 8 completion, ant ecology, or unscoped multi-basin claims.

## Candidate Rows

| Row | Source | Core | Gap | Capacity | Rung | Ceiling |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `n26_i4_i4_reference_child_basin_core_0` | `i4_reference_child_basin_core_0` | 0 | 0.0 | 1.0 | `PD2` | PD2 derivation only |
| `n26_i4_i4a_route_variant_child_basin_core_2` | `i4a_route_variant_child_basin_core_2` | 2 | 0.0 | 1.0 | `PD2` | PD2 derivation only |

## Claim Boundary

`candidate_pd_ladder_rung = PD2`

`n26_closeout_ceiling = N26-C3_active_nulls_fail_closed_with_PD2_derivation_candidate`

`ap5_bridge_status = not_supported_i4_row_local_dependency_recorded`

I4 records AP5 dependency locally because proxy target derivation is in
scope, but N15/N19 remain gap context only. The AP5 bridge remains
unsupported until later contrast/control evidence exists.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match` | `true` |
| `n25_2_scoped_handoff_valid` | `true` |
| `all_candidate_required_fields_present` | `true` |
| `pd2_artifact_roles_present` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `proxy_target_declared_before_use` | `true` |
| `proxy_metric_and_basin_capacity_traces_present` | `true` |
| `scoped_mb6_consumption_preserved` | `true` |
| `ap5_dependency_recorded_without_native_ap5_upgrade` | `true` |
| `no_proxy_divergence_or_collapse_claim` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_source_current_proxy_derivation_probe.json
reports/n26_source_current_proxy_derivation_probe.md
outputs/n26_source_current_proxy_derivation_probe_artifacts/
scripts/build_n26_source_current_proxy_derivation_probe.py
```
