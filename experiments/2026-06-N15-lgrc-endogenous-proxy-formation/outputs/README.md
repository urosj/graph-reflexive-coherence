# N15 Outputs

Generated JSON artifacts for N15 belong here.

Generated artifacts:

- `n15_proxy_source_inventory.json`
- `n15_proxy_formation_schema_v1.json`
- `n15_runtime_derived_target_candidate.json`
- `n15_external_proxy_contrast_matrix.json`
- `n15_proxy_control_matrix.json`
- `n15_bounded_drift_replay_matrix.json`

Planned artifacts:

- `n15_claim_boundary_record.json`
- `n15_closeout_and_handoff.json`

Generated outputs must use relative paths, include source digests, and keep
claim flags explicit.

Every JSON output should use a top-level object with:

```text
experiment
iteration
artifact_id
acceptance_state
source_artifacts
schema_version
rows
controls
checks
claim_flags
output_digest
errors
```

Outputs must exclude wall-clock timestamps and local filesystem paths from
replay digests. Any absolute path in an output is a portability failure.
