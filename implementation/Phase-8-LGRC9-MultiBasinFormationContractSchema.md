# Phase 8 LGRC9 Multi-Basin Formation Contract Schema

Status: passed.

Iteration 84 adds the default-off native multi-basin formation contract surface.
It does not emit flow windows, child-basin records, replay records, controls,
packets, topology events, or multi-basin runtime evidence.

## Default Flags

```text
native_lgrc_multi_basin_formation_enabled = false
native_lgrc_multi_basin_formation_policy = disabled
native_lgrc_multi_basin_formation_validated = false
native_lgrc_multi_basin_formation_supported = false
```

The active v1 policy is:

```text
post_refinement_child_basin_replay
```

When enabled, the policy requires LGRC-3 topology-changing causal history and
`causal_topology_integration_allowed = true`.

## Added Contract Artifacts

| Artifact | Kind | Digest |
|---|---|---|
| Post-refinement flow window | `lgrc9v3_multi_basin_post_refinement_flow_window_record` | `post_refinement_flow_window_digest` |
| Child-basin state | `lgrc9v3_child_basin_state_record` | `child_basin_state_digest` |
| Replay validation | `lgrc9v3_multi_basin_replay_validation_record` | `replay_validation_digest` |
| Merge/leakage control | `lgrc9v3_multi_basin_merge_leakage_control_record` | `control_record_digest` |

The child-basin state record also carries:

```text
child_basin_membership_digest
```

## Schema Guards

- Native multi-basin formation is default-off.
- Enabling requires LGRC-3 and `topology_changing_causal_history`.
- Enabling requires `causal_topology_integration_allowed = true`.
- Active policy without enablement fails closed.
- Validated requires enabled.
- Supported requires validated.
- Flow-window records require committed topology/refinement provenance, lineage,
  support/coherence/flux traces, packet flux trace, budget trace, and
  runtime-visible inputs.
- Child-basin records require source flow-window digest, core ids, membership
  digest, support/coherence/boundary/flux records, old-basin relation trace,
  merge/leakage trace, producer-residue classification, and runtime-visible
  inputs.
- Replay validation records require artifact, snapshot/load, duplicate, and
  time-order replay status fields plus persistence ratios in `[0, 1]`.
- Control records require blocked condition, expected/actual result, rung
  effect, merge/leakage metrics, and fail-closed claim handling.
- Hidden fixture inputs, label-only child basins, old-basin thickening,
  transient flow sinks, merge/leakage-as-success, hidden producer basin
  insertion, producer-assisted success as native upgrade, and post-hoc
  membership selection are rejected as runtime-visible inputs.
- Unsafe claim flags are rejected, including native support, agency, semantic
  learning, semantic choice, independent new-basin, BF6, sentience, ant
  ecology, unrestricted autonomy, and Phase 8 completion claims.
- The implementation rejects a defensive superset of runtime-visible input and
  claim-promotion aliases inherited from earlier native-route and movement /
  identity guardrails. These aliases are recorded in the JSON schema for
  traceability and do not broaden the positive multi-basin claim.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
133 passed, 81 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "multi_basin or native_route or child_basin or active_topology_integration_expands_causal_lane_b_candidate or stress_mixed_packet_birth_and_lane_b_expansion_preserves_runtime_refs or snapshot_round_trip"
64 passed, 220 deselected, 42 subtests passed

git diff --check
passed
```

## Claim Boundary

This is contract/schema support only. Multi-basin runtime emission, replayed
child-basin persistence, merge/leakage controls, MB4/MB5/MB6, BF6, independent
new-basin formation, native support, semantic learning, semantic choice,
agency, sentience, ant ecology, and Phase 8 completion remain blocked.
