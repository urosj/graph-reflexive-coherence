# Branch B2 Channel Attenuation Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b2_channel_attenuation.py
```

Status: `pass`

This diagnostic asks whether source export survives across intermediate
nodes as directed channel flux. It is not a positive loop-claim surface.

## Compact Summary

| Row | Lane | Gap Nodes | Forward Edges | Early Last/First | Early Sink/Source | Eval Last/First | Eval Sink/Source | Eval Channel Mass Dev |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| b2_s_n16_gap0 | S | 0 | 1 | 1 | 0.238951 | 1 | 0.820298 | 0.209763 |
| b2_k_n16_gap0 | K | 0 | 1 | 1 | 0.967993 | 1 | 1.33677 | 0.0645224 |
| b2_s_n16_gap1 | S | 1 | 2 | 1.03021 | 0.503222 | 2.15223 | 0.314362 | 0.0295519 |
| b2_k_n16_gap1 | K | 1 | 2 | 0.992677 | 0.885753 | 1.00814 | 0.829144 | 0.018868 |
| b2_s_n16_gap2 | S | 2 | 3 | 0.597203 | 0.282594 | 0.702187 | 1.41346 | 0.153855 |
| b2_k_n16_gap2 | K | 2 | 3 | 1.06113 | 1.09388 | 0.724683 | 0.862552 | 0.101903 |
| b2_s_n16_gap4 | S | 4 | 5 | 0.0629801 | 0.0463799 | 0.590698 | 1.04883 | 0.153801 |
| b2_k_n16_gap4 | K | 4 | 5 | 1.12597 | 1.14266 | 0.676934 | 0.789245 | 0.164733 |
| b2_s_n16_gap6 | S | 6 | 7 | 0.0471164 | 0.0494689 | 0.624248 | 0.872045 | 0.159134 |
| b2_k_n16_gap6 | K | 6 | 7 | 1.15868 | 1.15868 | 0.779189 | 0.779189 | 0.178013 |

## Errors

- none
