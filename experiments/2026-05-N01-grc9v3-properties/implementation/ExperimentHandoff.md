# GRC9V3 Properties Experiment Handoff

Status: complete.

Date: 2026-05-06.

## Final State

The `2026-05-N01-grc9v3-properties` experiment family is complete through:

- O-style Experiments A-G
- O-style family synthesis
- D1-D8 discriminator pass
- late D2 predictive role-separation scoring
- final D1-D8 discriminator synthesis

Final discriminator classification:

```text
anonymous_port_null_partially_rejected_with_lane_a_boundaries
```

The local checklists are the source of truth:

- `implementation/ExperimentSpecificationChecklist.md`
- `implementation/DiscriminatorExperimentSpecificationChecklist.md`

The final reports are:

- `guides/GRC9V3-Ports-Reference.md`
- `reports/family_level_synthesis.md`
- `reports/discriminator_synthesis.md`

## Runtime Boundary

All work in this experiment family is observational and experiment-local.
Generated scripts, reports, and outputs stay under:

```text
experiments/2026-05-N01-grc9v3-properties/
```

No `src/pygrc` runtime behavior was changed for this pass.

The active baseline is:

```text
lane_id = current_hybrid_signed_hessian
```

This is Lane A. Under Lane A:

- hybrid spark candidates are signed-Hessian hybrid runtime events
- direct column-H spark gating is not implemented or claimed
- column-H / column-cancellation evidence is derived and non-gating under
  Lane A
- mechanical refinement is not identity fission
- child identity claims require persistent post-event sink/basin artifacts

Lane B now exists as the separate opt-in implementation lane
`grc9v3_column_h_assisted`. `canonical_column_h` names the conceptual core GRC9
diagnostic source, not the GRC9V3 runtime lane id. Direct column-H
proxy-branch gate evidence must come from explicit Lane B runs and must not be
inferred from this Lane A experiment family.

## Final Conclusion

D1-D8 partially reject the anonymous-port null for controlled Lane A artifact
classes.

Rows, columns, ports, composite basin context, and ordinary graph/edge-label
baselines explain different target classes:

- rows explain geometric/differential targets
- columns explain interface/refinement/multiscale targets
- ports explain signed edge-local and observer-local transition targets
- identity-level claims require composite basin context
- graph/edge-label baselines remain appropriate for generic capacity and
  path-label targets

H0 remains competitive for:

- D4 Lane A saturation gate
- Experiment F edge-label path disagreement
- D5 post-window endpoint persistence availability in the clean fixture

## Supported Discriminator Results

| Discriminator | Classification | Key evidence |
| --- | --- | --- |
| D1 factorization | `supported_with_lane_a_boundaries` | structured error `0.0`; sampled non-factorized error `1.0` |
| D2 predictive role separation | `role_separation_supported_with_scorecard_cv_limitations` | rows, columns, ports, composite context, and graph baselines win on different target classes |
| D3 transpose | `supported_with_available_controls` | role separation index `1.282396` |
| D4 saturation | `supported_with_lane_a_boundaries` | Lane A active-degree-9 signed-Hessian gate; budget error `0.0` |
| D5 interface memory | `mechanical_supported_post_window_partial` | immediate column memory `1.0`; post-window column memory `0.888889` |
| D6 port interaction | `supported_for_signed_edge_local_target_with_runtime_abs_control` | signed edge-local additive `R2 = 0.2`; port/intersection `R2 = 1.0` |
| D7 multiscale | `reconstruction_supported_semantic_columns_supported_with_boundaries` | true-column G/Split max error `1.11e-16`; true columns beat random triples |
| D8 identity emergence | `configured_window_persistent_child_identity_supported_with_boundaries` | accepted configured-window identity events `20`; strict-threshold failures `30` |

## Lane C Comparison

Lane C was run as an analysis pass over selected clean fixtures. It is not a
runtime lane and does not change Lane A or Lane B.

Classification:
    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

Result:

- comparison rows: `60`
- Lane A candidates/refinements: `25 / 25`
- Lane B candidates/refinements: `40 / 40`
- direct Lane B column-H proxy-branch rows: `15`
- candidate/refinement delta rows: `15 / 15`
- degree-8 near-saturation remains blocked

## Boundaries

These remain blocked, partial, or future work:

- degree-8 near-saturation policy
- inflow-weighted transfer lane
- checkpoint-window identity persistence
- landscape-general identity emergence
- full fitted held-out-landscape predictive CV
- reusable motion-loader full port histories
- exhaustive S9 coverage

Do not promote these from the completed artifacts.

## Artifact Index

Primary synthesis artifacts:

- `guides/GRC9V3-Ports-Reference.md`
- `outputs/lane_c_summary.json`
- `outputs/lane_c_comparison_manifest.json`
- `reports/lane_c_comparison_report.md`
- `outputs/family_level_hypothesis_status.csv`
- `outputs/family_level_synthesis_summary.json`
- `outputs/family_level_synthesis_manifest.json`
- `outputs/discriminator_hypothesis_status.csv`
- `outputs/discriminator_prediction_comparison.csv`
- `outputs/discriminator_followup_surfaces.csv`
- `outputs/discriminator_synthesis_summary.json`
- `outputs/discriminator_synthesis_manifest.json`

Primary discriminator outputs:

- `outputs/d1_factorization_summary.json`
- `outputs/d2_scoring_summary.json`
- `outputs/d3_transpose_summary.json`
- `outputs/d4_saturation_summary.json`
- `outputs/d5_interface_memory_summary.json`
- `outputs/d6_port_interaction_summary.json`
- `outputs/d7_multiscale_summary.json`
- `outputs/d8_identity_emergence_summary.json`

Primary discriminator reports:

- `reports/d1_artifact_distance_report.md`
- `reports/d2_cross_validation_report.md`
- `reports/d3_role_separation_report.md`
- `reports/d4_saturation_report.md`
- `reports/d5_interface_memory_report.md`
- `reports/d6_port_interaction_report.md`
- `reports/d7_multiscale_report.md`
- `reports/d8_identity_emergence_report.md`

## Follow-Up Candidates

Follow-up work should be explicit new work, not hidden changes to this pass:

- add a degree-8 near-saturation policy only as a separate runtime change
- add checkpoint-window identity persistence capture
- add reusable motion-loader full port-history support
- run a landscape/seed robustness suite
- broaden sampled S9/random regrouping controls

## Validation Pattern

Recent iterations used scoped validation:

```text
PYTHONPATH=src .venv/bin/python -m py_compile <experiment script>
PYTHONPATH=src .venv/bin/ruff check <experiment script>
.venv/bin/python -m json.tool <summary-or-manifest-json>
git diff --check -- <touched experiment files>
```

Full-repo cleanup was intentionally not performed because unrelated worktree
changes exist outside this experiment family.
