# Shared Discriminator Harness

Status: complete.

## Scope

This harness defines shared D1-D8 record contracts, evidence labels,
classification labels, transform metadata, manifest fields, blocked
observation format, artifact extraction registry, and expected outputs.

It is experiment-local and does not change `src/pygrc` runtime behavior.

## Evidence Labels

- `direct`
- `derived`
- `partial`
- `blocked`
- `inconclusive`

## Manifest Required Fields

- `discriminator_id`
- `iteration`
- `script_path`
- `command`
- `git_commit`
- `lane_id`
- `fixture_id`
- `transform_id`
- `seed`
- `runtime_params`
- `artifact_schema_version`
- `artifact_source_map`
- `output_paths`

## Artifact Registry

| Artifact Class | Evidence Label | Primary Sources |
| --- | --- | --- |
| row_differential_signature | derived | Experiment A rows; GRC9V3State/cached row artifacts |
| derived_column_proxy | derived | Experiment B rows; endpoint ports and conductance/coherence/flux |
| lane_a_saturation_gate | direct | Experiment C rows; spark candidates and event payloads |
| refinement_reassignment | direct | Experiment D reassignment rows; expansion payload |
| coarse_split_reconstruction | direct | Experiment E reconstruction rows and summary |
| path_label_selection | direct | Experiment F edge/path/criteria rows |
| motion_port_history | partial | Experiment G checkpoint-overlay port history |
| identity_persistence | partial | Experiment D persistence rows; later D8 windows |

## D2 Split

D2 schema definition and D2 scoring are intentionally separate.
Iteration 3 defines targets and feature families; Iteration 10 runs
scoring only after enough O-style and D-style run data exist.

## Output Coverage

The machine-readable schema lists expected outputs for D1-D8 and can
represent the current D1 outputs.
