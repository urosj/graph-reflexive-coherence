# Branch B3 Conductance Corridor Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b3_conductance_corridor.py
```

Status: `pass`

B3 is diagnostic-only. It tests fixed-topology in-memory conductance
corridors and cannot promote a positive loop claim.

Rows: `24`
Promising diagnostic rows: `0`
Interpretation: `conductance_corridor_did_not_create_role_gated_loop_evidence`

## Compact Summary

| Row | Lane | Variant | Source | Sink | Raw | Role-Gated | Would Claim | Eval Last/First | Eval Sink/Source | Max Correction |
| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| b3_s_forward_x1p5 | S | forward_x1.5 | False | False | 0 | 0 | False | 1.01464 | 0.725641 | 4.44089e-16 |
| b3_k_forward_x1p5 | K | forward_x1.5 | False | False | 0 | 0 | False | 0.771721 | 0.771721 | 4.44089e-16 |
| b3_s_return_x1p5 | S | return_x1.5 | False | False | 0 | 0 | False | 1.0145 | 0.725623 | 3.33067e-16 |
| b3_k_return_x1p5 | K | return_x1.5 | False | False | 0 | 0 | False | 0.77172 | 0.771721 | 4.44089e-16 |
| b3_s_balanced_x1p5 | S | balanced_x1.5 | False | False | 0 | 0 | False | 1.01463 | 0.725637 | 4.44089e-16 |
| b3_k_balanced_x1p5 | K | balanced_x1.5 | False | False | 0 | 0 | False | 0.771721 | 0.771721 | 5.55112e-16 |
| b3_s_forward_x2 | S | forward_x2 | False | False | 0 | 0 | False | 1.01473 | 0.72565 | 4.44089e-16 |
| b3_k_forward_x2 | K | forward_x2 | False | False | 0 | 0 | False | 0.771722 | 0.771721 | 3.33067e-16 |
| b3_s_return_x2 | S | return_x2 | False | False | 0 | 0 | False | 1.0145 | 0.72562 | 4.44089e-16 |
| b3_k_return_x2 | K | return_x2 | False | False | 0 | 0 | False | 0.77172 | 0.771721 | 3.33067e-16 |
| b3_s_balanced_x2 | S | balanced_x2 | False | False | 0 | 0 | False | 1.01472 | 0.725642 | 4.44089e-16 |
| b3_k_balanced_x2 | K | balanced_x2 | False | False | 0 | 0 | False | 0.771721 | 0.771721 | 6.66134e-16 |
| b3_s_forward_x4 | S | forward_x4 | False | False | 0 | 0 | False | 1.01492 | 0.725667 | 3.33067e-16 |
| b3_k_forward_x4 | K | forward_x4 | False | False | 0 | 0 | False | 0.771723 | 0.771721 | 4.44089e-16 |
| b3_s_return_x4 | S | return_x4 | False | False | 0 | 0 | False | 1.01449 | 0.725613 | 4.44089e-16 |
| b3_k_return_x4 | K | return_x4 | False | False | 0 | 0 | False | 0.77172 | 0.771721 | 4.44089e-16 |
| b3_s_balanced_x4 | S | balanced_x4 | False | False | 0 | 0 | False | 1.01492 | 0.725654 | 4.44089e-16 |
| b3_k_balanced_x4 | K | balanced_x4 | False | False | 0 | 0 | False | 0.771722 | 0.771722 | 4.44089e-16 |
| b3_s_forward4_return1p5 | S | forward4_return1p5 | False | False | 0 | 0 | False | 1.01492 | 0.725663 | 4.44089e-16 |
| b3_k_forward4_return1p5 | K | forward4_return1p5 | False | False | 0 | 0 | False | 0.771722 | 0.771721 | 4.44089e-16 |
| b3_s_forward1p5_return4 | S | forward1p5_return4 | False | False | 0 | 0 | False | 1.01463 | 0.725627 | 3.33067e-16 |
| b3_k_forward1p5_return4 | K | forward1p5_return4 | False | False | 0 | 0 | False | 0.77172 | 0.771721 | 4.44089e-16 |
| b3_s_source_exit_sink_entry_x4 | S | source_exit_sink_entry_x4 | False | False | 0 | 0 | False | 1.01535 | 0.725692 | 4.44089e-16 |
| b3_k_source_exit_sink_entry_x4 | K | source_exit_sink_entry_x4 | False | False | 0 | 0 | False | 0.771726 | 0.771722 | 5.55112e-16 |

## Errors

- none
