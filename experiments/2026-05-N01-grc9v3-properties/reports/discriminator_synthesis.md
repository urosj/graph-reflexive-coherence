# Discriminator Synthesis

Status: complete.

Classification: `anonymous_port_null_partially_rejected_with_lane_a_boundaries`.

## Conclusion

D1-D8 partially reject the anonymous-port null for the controlled Lane A
artifact classes tested here. Rows, columns, ports, composite basin
context, and ordinary graph/edge-label baselines explain different
artifact classes. H0 is no longer competitive for all artifacts, but it
remains competitive for generic capacity and edge-label path behavior.

## Hypothesis Status

| ID | Hypothesis | Classification | Key Evidence | Boundaries |
| --- | --- | --- | --- | --- |
| H0 | anonymous-port null | partially_weakened_not_globally_refuted | Structured row/column transforms preserve sensitive artifacts better than sampled S9/random triples; D2 scorecard separates row, column, port, and composite target families. structured_error=0.0; s9_error=1.0; separated_targets=9 | No landscape-general refutation, exhaustive S9 proof, or full fitted held-out predictive CV. |
| D1 | factorization discriminator | supported_with_lane_a_boundaries | Structured row/column transforms have zero mean semantic error on factorization-sensitive artifacts; sampled non-factorized proxy has error 1.0. structured_error=0.0; s9_error=1.0; records=70 | Sampled non-factorized control, not exhaustive S9 coverage. |
| D2 | predictive role separation | role_separation_supported_with_scorecard_cv_limitations | Rows, columns, ports, composite context, and degree/edge-label baselines are strongest on different target classes. score_rows=11; random_groupings_explain_all=False; degree_explains_all=False | Artifact scorecard only; fitted held-out landscape CV inconclusive. |
| D3 | row/column transpose non-equivalence | supported_with_available_controls | Row-local geometry response and column-local interface proxy response drop under transpose. role_separation_index=1.2823960779719024; row=0.6270514633291143; row_transpose=0.3333333333333333; column=0.9886779479761213; column_transpose=0.0 | Direct column-H and event-capable transpose refinement remain blocked/inconclusive. |
| D4 | saturation bottleneck | supported_with_lane_a_boundaries | Degree 7/8 stressed nodes do not trigger; degree 9 stressed node triggers; degree 9 stable-Hessian control does not. gate='active_degree == 9 AND gradient_norm < eps_gradient AND min_signed_hessian < eps_spark'; budget_error=0.0; rows=20 | Direct column-H and degree-8 near-saturation remain blocked under Lane A. |
| D5 | interface memory | mechanical_supported_post_window_partial | Immediate old-column memory is complete; post-window true columns beat row/random semantic controls. immediate=1.0; post_window=0.8888888888888888; random_triple=0.2222222222222222; persistent_edges=32/36 | Post-refinement flux windows and checkpoint observer windows unavailable. |
| D6 | port interaction | supported_for_signed_edge_local_target_with_runtime_abs_control | Signed edge-local target is not additive row+column, while port-level and interaction models fit exactly. additive_r2=0.19999999999999996; interaction_r2=1.0; port_r2=1.0; random_triple_r2=0.09999999999999998 | Existence witness only, not universal port non-additivity. |
| D7 | multiscale discriminator | reconstruction_supported_semantic_columns_supported_with_boundaries | True-column G/Split reconstructs eligible fields; signed flux is exact through J+/J-; true columns beat rows/random triples on interface/refinement targets. max_error=1.1102230246251565e-16; signed_flux_j_split=True; immediate_column=1.0; random_triple=0.2222222222222222 | Before/after refinement E-style G/Split checkpoints remain blocked. |
| D8 | identity emergence | configured_window_persistent_child_identity_supported_with_boundaries | Configured-window identity requires refinement, persistent child sink/basin rows, lineage, and budget evidence. accepted_events=20; accepted_rows=60; strict_failures=30; no_refinement_controls=5 | Checkpoint-window, collapse/reabsorption, and landscape-general identity remain inconclusive. |

## H0-Competitive Scope

- `d5_post_window_column_memory`
- `d4_lane_a_saturation_gate`
- `experiment_f_edge_label_path_disagreement`

## Prediction Comparison

| Prediction | Observed Result | Synthesis |
| --- | --- | --- |
| H0 will be partially rejected, not completely destroyed. | matched | H0 is weakened for row/column/port-sensitive artifact classes but remains competitive for generic capacity and edge-label targets. |
| Rows will show clean geometry/differential evidence. | matched | A, D2, and D3 support row-geometric/differential targets. |
| Columns will show strongest mechanical support in refinement/coarse-graining. | matched | D5 and D7 support column refinement/multiscale targets. |
| Direct/dynamic column claims may need caveats. | matched | Direct column-H remains blocked under Lane A; D5 post-window support is partial. |
| Port interaction is fixture-dependent. | matched | D6 supports a signed edge-local witness but runtime absolute flux is additive. |
| Path disagreement depends on exposed labels. | supported | Experiment F and D2 confirm edge-label path disagreement as a generic path-label target. |
| Identity emergence is most uncertain. | partially_supported_with_boundaries | D8 supports configured-window child-basin persistence only with strict thresholds. |

## Follow-Up Surfaces

| Surface Or Suite | Status | Reason | Guardrail |
| --- | --- | --- | --- |
| grc9v3_column_h_assisted Lane B / Lane C | completed post-pass comparison | Direct column-H proxy-branch spark evidence remains blocked under Lane A but observed in explicit Lane B rows. | Do not reinterpret Lane A derived B proxies or D4 Lane A sparks as direct column-H branch evidence. |
| near-saturation degree-8 policy | future implementation candidate | D4 marks near-saturation blocked because Lane A has no such policy. | Do not treat degree-9 saturation support as degree-8 near-saturation support. |
| checkpoint-window identity persistence | small addendum candidate | D8 uses runtime-state windows, not persisted checkpoint observer windows. | Do not promote configured-window runtime support to checkpoint-window support. |
| reusable motion-loader full port histories | future implementation candidate | Experiment G used checkpoint-overlay observer reconstruction. | Do not infer reusable loader support from observer-local overlays. |
| landscape/seed predictive robustness suite | future experiment suite | D2 fitted held-out-landscape CV remains inconclusive. | Do not report clean-fixture scorecards as landscape-general statistics. |
| exhaustive or broader S9 sampling | future robustness addendum | D1/D2 random controls are sampled non-factorized proxies. | Do not describe sampled S9 controls as exhaustive. |

## Guardrails

- Supported discriminator claims cite generated outputs, not source intent alone.
- Lane A is `current_hybrid_signed_hessian`; direct column-H proxy-branch evidence belongs only to explicit `grc9v3_column_h_assisted` Lane B/Lane C artifacts.
- Mechanical refinement is not identity fission.
- Configured-window child-basin persistence is not checkpoint-window or landscape-general identity.
- D2 is an artifact scorecard, not full fitted held-out-landscape CV.
- Sampled non-factorized controls are not exhaustive S9 coverage.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D1-D8 partially reject the anonymous-port null for controlled Lane A artifact classes. The result does not establish landscape-general semantics, near-saturation policy, checkpoint-window identity, or exhaustive S9 robustness.
