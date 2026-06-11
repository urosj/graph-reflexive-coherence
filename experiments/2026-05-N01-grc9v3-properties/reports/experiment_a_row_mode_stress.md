# Experiment A Row-Mode Stress

Status: complete.

## Scope

This report tests whether row-local perturbations produce row-local
differential/geometric signatures under the Lane A baseline
`current_hybrid_signed_hessian`.

Column-H is not used as direct spark-gating evidence in this experiment.

## Outputs

- `../outputs/experiment_a_row_mode_stress_rows.csv`
- `../outputs/experiment_a_row_mode_stress_summary.json`
- `../outputs/experiment_a_row_mode_stress_manifest.json`

## Fixture Matching

- total absolute coherence delta matched: `true`
- total squared coherence delta matched: `true`
- affected-port counts matched: `true`
- energy totals matched: `true`
- row-local fixtures and the balanced fixture each perturb exactly three
  ports with the same total absolute and squared coherence delta.

## Identity Row-Stress Responses

| Fixture | Expected Row | Dominant Row | Dominance | Isotropic Dominance Ratio |
| --- | ---: | ---: | ---: | ---: |
| a_row_1_stress_seed_0 | 1 | 1 | 0.640699 | 15.086394 |
| a_row_2_stress_seed_0 | 2 | 2 | 0.620228 | 14.193718 |
| a_row_3_stress_seed_0 | 3 | 3 | 0.620228 | 14.193718 |

## Row Permutation Controls

- row signatures move under row permutation: `true`

| Fixture | Expected Row After Permutation | Dominant Row |
| --- | ---: | ---: |
| a_row_1_stress_seed_0 | 2 | 2 |
| a_row_2_stress_seed_0 | 3 | 3 |
| a_row_3_stress_seed_0 | 1 | 1 |

## Controls Summary

- identity row stress matches expected row: `true`
- column permutation preserves stressed row: `true`
- random relabel removes a predefined clean expected row: `true`
- minimum true-minus-random interpretability margin: `0.165575`
- isotropic terms dominate any row stress: `true`

## Balanced Control

- balanced identity dominant row: `None` with dominance `0.333333`

## Interpretation

Experiment A supports the row-mode stress hypothesis in a clean
saturated central-node fixture under Lane A.

Row-local perturbations produce the expected dominant row signature,
and the signature transforms correctly under row permutation. Column
permutation does not explain the row-local signature. Balanced and
random-relabel controls do not provide the same clean row-local
interpretation.

This supports row-local differential/geometric observability in this
controlled fixture. The result weakens the anonymous-port null for
row-resolved artifacts and provides partial support for the row side
of the factorization discriminator. It does not yet establish column
semantics, non-additive port interactions, or landscape-level
generality.

The anisotropic row span is detectable and transforms correctly, but
the isotropic `K` component is large relative to that span in this
fixture. The correct claim is row-resolved anisotropic detectability,
not dominance of `K` by row anisotropy.
