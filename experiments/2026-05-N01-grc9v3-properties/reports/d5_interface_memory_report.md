# D5 Interface-Memory Discriminator Report

Status: complete.

Classification: `mechanical_supported_post_window_partial`.

## Scope

D5 reuses completed Experiment D refinement artifacts and does not add
runtime behavior. It separates immediate mechanical column preservation
from stricter post-window interface-memory evidence.

Immediate memory is scored from
`hybrid_mechanical_expansion.payload.reassignment_map`. Post-window
memory is scored by joining reassignment endpoint nodes to Experiment D
runtime-state child sink/basin persistence rows.

## Identity Transform Scores

Identity-transform scores are stable across the uniform and custom
column-skewed transfer conditions, so the table reports one aggregate
row per predictor.

| Predictor | Immediate Score | Post-Window Score | Evidence | Notes |
| --- | --- | --- | --- | --- |
| true_old_column | 1.000000 | 0.888889 | direct | True parent column label against target module column. |
| old_row_label | 0.333333 | 0.222222 | derived | Row-label control kept separate from true-column evidence. |
| random_column_label | 0.222222 | 0.222222 | derived | Deterministic sampled random column-label control. |
| random_triple_label | 0.222222 | 0.222222 | derived | Deterministic sampled random triple grouping control. |
| degree_adjacency_endpoint_baseline | 0.888889 | 0.888889 | partial | Endpoint persistence baseline only; it does not predict semantic module column. |

## Findings

- immediate column preservation score: `1.0`
- post-window column memory score: `0.8888888888888888`
- post-window row-label score: `0.2222222222222222`
- post-window random-column score: `0.2222222222222222`
- post-window random-triple score: `0.2222222222222222`
- persistent endpoint edge count: `32 / 36`
- budget preserved for all refinement rows: `True`
- persistence window steps: `3`
- minimum basin mass threshold: `1.0`

## Interpretation

D5 supports immediate mechanical column memory directly and supports
post-window column memory only in the narrower runtime-state sense:
old parent column remains more predictive than row labels and sampled
random group controls for endpoints that participate in persistent
child sink/basin rows.

This does not establish post-event flux-memory behavior, checkpoint
observer-window interface memory, or landscape-general interface
memory.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: Immediate mechanical column memory is direct. Post-window memory is supported only for module endpoints that are persistent child sinks in Experiment D runtime-state windows; post-event flux windows and checkpoint observer windows are unavailable.
