# D4 Saturation Discriminator Report

Status: complete.

Classification: `supported_with_lane_a_boundaries`.

## Scope

D4 reuses completed Experiment C saturation artifacts and does not add
runtime behavior. The canonical Lane A gate is:

```text
active_degree == 9 AND gradient_norm < eps_gradient AND min_signed_hessian < eps_spark
```

This is saturation plus basin-interior / signed-Hessian degeneracy
evidence. It is not direct column-H gating.

## Canonical Identity Rows

| Condition | Degree | Instability | Saturated | Candidate | Refinement | Budget Evidence | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1_degree_7_stressed | 7 | True | False | 0 | 0 | False | stress_without_fullness_does_not_trigger |
| C2_degree_8_stressed | 8 | True | False | 0 | 0 | False | stress_without_fullness_does_not_trigger |
| C3_degree_9_stressed | 9 | True | True | 1 | 1 | True | saturation_plus_instability_triggers_lane_a_expansion |
| C5_degree_9_stable_hessian | 9 | False | True | 0 | 0 | False | fullness_without_instability_does_not_trigger |

## Findings

- degree 7/8 stressed nontrigger: `True`
- degree 9 stressed candidate: `True`
- degree 9 stressed refinement: `True`
- degree 9 stable-Hessian nontrigger: `True`
- fullness alone insufficient: `True`
- signed-Hessian stress without saturation insufficient: `True`
- candidate detection matches formula for all rows: `True`
- transform candidate/refinement invariance: `True`

## Budget

- canonical positive budget error: `0.0`
- budget tolerance: `1e-12`
- within tolerance: `True`

## Near-Saturation And Column-H

- near-saturation policy: `not_implemented_in_lane_a`
- derived column diagnostic role: `reported_separately_not_gate_evidence`

The degree-8 near-saturation policy remains blocked under Lane A.
The column diagnostic is reported separately as an analysis
diagnostic and is not used as direct gate evidence.

## Interpretation

D4 supports the Lane A saturation bottleneck discriminator. Degree 7
and degree 8 stressed fixtures do not trigger despite matching the
central signed-Hessian degeneracy of the positive run. The degree 9
stressed fixture triggers one candidate and one mechanical expansion
with budget evidence. The degree 9 stable-Hessian control shows that
fullness alone is insufficient.

Transform invariance is expected for this Lane A gate and is reported
as capacity/signed-Hessian behavior, not row/column factorization
evidence.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D4 formalizes Lane A active-degree saturation plus signed-Hessian degeneracy evidence. It does not claim direct column-H gating or near-saturation behavior.
