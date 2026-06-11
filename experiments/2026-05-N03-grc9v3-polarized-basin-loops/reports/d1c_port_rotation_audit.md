# D1c Port-Rotation Circulation Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1c_port_rotation_audit.py
```

Status: `pass`

Classification: `d1c_weak_residual_port_rotation_circulation_observed`
Max abs loop circulation: `0.0036735167365173904`
Max abs normalized circulation: `0.005365511110850774`

D1c audits native GRC9V3 fixed-topology port-rotation fixtures. It
does not add a circulatory proposal term or modify `src/*`.

Port cycle:

```text
clockwise: 1 -> 2 -> 3 -> 6 -> 9 -> 8 -> 7 -> 4 -> 1
counter-clockwise: reverse(clockwise)
```

## Baseline

Prior D1 direct/channel-flow baseline:

```json
{
  "available": true,
  "classification": "d1_weak_residual_loop_circulation_observed",
  "max_abs_loop_circulation": 0.0070727893817062425,
  "max_abs_normalized_circulation": 0.006041388204739038
}
```

## Scenario Summary

| Scenario | Max Abs Circ | Mean Abs Circ | Max Norm Circ | Mean Norm Circ | Initial Circ | Final Circ | Final Mean Abs Flux |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d1c_rotation_cw_uniform | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1c_rotation_cw_single_bump | 0.0028476 | 0.000398779 | 0.00205594 | 0.000589674 | 0.000128163 | 0.0028476 | 0.173133 |
| d1c_rotation_cw_traveling_phase_seed | 0.00243217 | 0.000504918 | 0.00389342 | 0.00100858 | 0.000170358 | -0.00243217 | 0.0780859 |
| d1c_rotation_cw_quadrature | 0.00116299 | 0.000166526 | 0.000805888 | 0.000317783 | -6.21102e-05 | -0.00116299 | 0.180389 |
| d1c_rotation_cw_alternating | 0.00145093 | 0.00101503 | 0.00100254 | 0.000703337 | 2.26448e-07 | 0.00145093 | 0.180908 |
| d1c_rotation_ccw_traveling_phase_seed | 0.00367352 | 0.000516329 | 0.00536551 | 0.000865744 | 6.93758e-05 | -0.00367352 | 0.0855817 |
| d1c_rotation_ccw_quadrature | 0.00116299 | 0.000166526 | 0.000805888 | 0.000317783 | 6.21102e-05 | 0.00116299 | 0.180389 |
| d1c_rotation_cw_traveling_phase_seed_reversed | 0.00367352 | 0.000516329 | 0.00536551 | 0.000865744 | -6.93758e-05 | 0.00367352 | 0.0855817 |

## Interpretation

Port-rotation fixtures are native GRC9V3 fixed-topology tests. A material result would require normalized circulation >= 0.01. Weak residual rows remain diagnostic only and do not promote loop evidence.

## Errors

- none
