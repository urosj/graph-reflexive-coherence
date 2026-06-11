# Experiment F Path Disagreement

Status: complete.

## Scope

This report tests whether metric, temporal-delay, and strongest-flux
path notions can disagree while remaining auditable edge by edge under
the Lane A baseline.

Path disagreement is reported as edge-label evidence, not direct
row/column semantic evidence.

## Scoring

- metric path: `minimize sum geometric_length(e)`
- delay path: `minimize sum temporal_delay(e)`
- primary flux path: `maximize min_e abs(signed_flux(e))`
- primary coupling path: `maximize min_e flux_coupling(e)`
- secondary flux diagnostic: `maximize sum abs(signed_flux(e))`
- secondary coupling diagnostic: `maximize sum flux_coupling(e)`
- tie-break: `prefer fewer edges, then lexicographic edge-id tuple`

## Base Fixture Choices

| Criterion | Selected Path | Score | Tie |
| --- | --- | ---: | --- |
| P_metric | path_0_A_metric_short | 2 | `1` |
| P_delay | path_1_B_delay_fast | 0.363636363636 | `1` |
| P_flux_bottleneck | path_2_C_flux_strong | 20 | `1` |
| P_coupling_bottleneck | path_2_C_flux_strong | 20 | `1` |
| P_flux_cumulative | path_2_C_flux_strong | 40 | `1` |
| P_coupling_cumulative | path_2_C_flux_strong | 40 | `1` |

## Controls

| Variant | Metric Path | Delay Path | Flux Bottleneck Path | Coupling Bottleneck Path | Ties |
| --- | --- | --- | --- | --- | ---: |
| base_disagreement | path_0_A_metric_short | path_1_B_delay_fast | path_2_C_flux_strong | path_2_C_flux_strong | 0 |
| equalized_geometric_labels | path_0_A_metric_short | path_2_C_flux_strong | path_2_C_flux_strong | path_2_C_flux_strong | 1 |
| equalized_temporal_labels | path_0_A_metric_short | path_0_A_metric_short | path_2_C_flux_strong | path_2_C_flux_strong | 1 |
| equalized_flux_labels | path_0_A_metric_short | path_0_A_metric_short | path_0_A_metric_short | path_0_A_metric_short | 4 |
| all_equalized_labels | path_0_A_metric_short | path_0_A_metric_short | path_0_A_metric_short | path_0_A_metric_short | 6 |

## Summary

- base primary paths all distinct: `true`
- base metric/delay/flux paths disagree: `true`
- equalized flux collapses flux path to metric path: `true`
- equalized temporal labels remove delay-specific winner: `true`
- all equalized paths collapse to tie-broken path: `true`
- port relabel preserves path choices: `true`

## Interpretation

Experiment F supports auditable multi-label path disagreement in the
clean three-corridor fixture. The metric path, delay path, and primary
strongest-flux path select different corridors in the base fixture.
Equalized controls show the differences are driven by the intended
edge-label surfaces rather than nondeterministic path ordering.

The result does not by itself support row/column semantic separation.
It supports that the available GRC9V3 edge-label and flux artifacts can
back multiple distinct path notions with edge-by-edge explanations.
