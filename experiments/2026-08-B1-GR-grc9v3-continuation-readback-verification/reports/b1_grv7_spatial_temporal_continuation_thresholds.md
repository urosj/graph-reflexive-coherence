# B1-GR GRV7 Spatial, Temporal, And Continuation Thresholds

## Result

```text
mechanical_status = passed
continuation_path_count = 6
primary_continuation_point_count = 27
complete_step_temporal_admitted_points = 16
complete_step_temporal_blocked_points = 11
frozen_temporal_classes_reached = ['minus_one_flip_marginality', 'plus_one_marginality', 'stable_interior', 'unstable_exterior']
complete_step_temporal_classes_reached = ['plus_one_marginality']
supported_bounded_counterexample_count = 2
decisive_uncertainty_separated_counterexample_count = 2
supported_full_map_counterexample_count = 0
bounded_spatial_temporal_non_equivalence_supported = true
full_map_non_equivalence_supported = false
scientific_acceptance = awaiting_human_review
GRV_C5_assigned = false
GRV8_authorized = false
```

## Load-Bearing Scientific Discriminators

GRV7 treats six checks as load-bearing rather than presenting generic
provenance hygiene as equally probative. `H_row`, `H_signed`, `H_WLS`,
`H_cont^{W*}`, `A_W H_cont^{W*}`, and `A_full` have separate domains,
metrics, sign conventions, and threshold rules. Cross-operator eigenvalue
index pairing is forbidden.

Every continuation sheet remains bound to its preregistered source branch;
symmetry copies remain separate variants. The frozen comparator is a clamped-
`W` zero-sum-`C` construction, not current slaving, so an `I-B_eff` inverse
is not used or claimed. Its tangent mobility gate passes at every point.
Complete-step comparisons remain independently governed by the GRV3 stratum
and spectral gates; blocked rows are not threshold disagreements.

The two decisive F1 examples share one exact one-dimensional zero-sum-`C`
critical subspace, so their relation does not depend on sorted eigenvalue
indices. Their threshold witnesses and off-threshold brackets are separated
from the preregistered tolerances. No corresponding full-map threshold
crossing was reached, so no full-map critical-subspace or non-equivalence
claim is available.

GRV7 follows preregistered branches rather than assembling unrelated solved
points after seeing spectra. All 48 GRV2 branches remain in source accounting;
the path seeds and symmetry partners were frozen before execution. A path
stops on topology, event, categorical, residual, state-match, or parameter-step
failure. An unreached threshold is not counted as negative evidence.

## Threshold Evidence

The F1 scale path holds the graph and coherence state fixed while changing
the quadratic potential scale. Its exact runtime row-basis unsigned, signed,
and WLS spatial diagnostics remain identical, while the separately derived
analytical constrained second variation passes through zero and the frozen-`W`
multiplier reaches `+1`. This distinguishes the runtime local spatial
diagnostics from the analytical continuation Hessian.

The F1 timestep path holds both runtime spatial diagnostics and the analytical
continuation Hessian fixed while the frozen-`W` discrete multiplier passes
through the stable interior and `-1`. The flip threshold therefore depends on
the evolution timestep and mobility, not on a spatial Hessian threshold alone.
These are exact clamped-counterfactual counterexamples, not complete-step
counterexamples.

The classical complete-step derivative remains blocked on F1 because two-sided
perturbations leave the zero-current sink/basin identity stratum. GRV7 preserves
that block rather than treating it as finite-difference nonconvergence. F2/F3
nonuniform points retain admitted complete-step spectra with basis, phase, and
symmetry controls. Their observed relation is reported as bounded correlation;
the preregistered paths do not supply a complete-step threshold crossing.

No complex unit-circle crossing was reached. The frozen comparator is real
self-adjoint in the tested families, and the admitted complete-step envelope
did not cross a complex threshold. This is scope-limited unavailability, not
global nonexistence evidence.

## Counterexamples

| Counterexample | Status | Separation | Full-map evidence |
| --- | --- | --- | --- |
| `CE1_runtime_spatial_vs_analytical_continuation_threshold` | `supported` | `passed` | `false` |
| `CE2_fixed_spatial_vs_discrete_flip_threshold` | `supported` | `passed` | `false` |
| `F2_dt_nonuniform_path_complete_step_screen` | `bounded_correlation_only_no_preregistered_full_threshold_crossing` | `not_applicable` | `false` |
| `F2_eta_nonuniform_path_complete_step_screen` | `bounded_correlation_only_no_preregistered_full_threshold_crossing` | `not_applicable` | `false` |
| `F3_dt_nonuniform_path_complete_step_screen` | `bounded_correlation_only_no_preregistered_full_threshold_crossing` | `not_applicable` | `false` |
| `F3_eta_nonuniform_path_complete_step_screen` | `bounded_correlation_only_no_preregistered_full_threshold_crossing` | `not_applicable` | `false` |

## Claim Boundary

GRV7 may support bounded non-equivalence among runtime spatial diagnostics,
the analytical continuation Hessian, and discrete frozen-`W` thresholds. It
does not prove spatial Hessians never correlate with temporal or basin
transitions, does not turn the frozen comparator into the complete step map,
and does not establish continuation, retention, Read-Back, or write-back.
`GRV-C5` remains unassigned until human review and a separate acceptance anchor.
GRV8 remains unopened.

## Provenance

- Input execution revision: `10d07aa09e5e6ad6cf2bdced94c3cb37a2679719`
- GRV6 receipt: `705b6967eedb86fe0d0d7d895998a3ad1147ede312502dae6567a9021fb449c3`
- GRV6 acceptance commit: `9606f2466769d89e10145e112ed5136704a5ad79`
- Runtime source/spec/root-test paths: unchanged under `protected_path_manifest_v7.json`
