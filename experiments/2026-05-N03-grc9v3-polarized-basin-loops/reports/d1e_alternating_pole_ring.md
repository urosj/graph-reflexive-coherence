# D1e Alternating Source/Sink Pole Ring Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1e_alternating_pole_ring.py
```

Status: `pass`

Classification: `d1e_partial_alternating_pole_evidence_only`

D1e distributes source/sink-aspect polarity around the fixed ring:

```text
S1 -> K2 -> S2 -> K1 -> S1
```

It changes only the fixture/initialization surface; it does not add
role switching, propulsion, edge storage, or a circulatory proposal term.

## Scenario Summary

| Scenario | Max Norm Circ | Max Abs Circ | Cycle Proxy | Role Pattern | Candidate |
| --- | ---: | ---: | ---: | --- | --- |
| d1e_uniform | 0 | 0 | 0 | no | no |
| d1e_alternating | 0 | 0 | 0 | yes | no |
| d1e_alternating_strong | 0 | 0 | 0 | yes | no |
| d1e_alternating_reversed | 0 | 0 | 0 | no | no |
| d1e_traveling_four_pole | 0.00143527 | 0.00111004 | 0 | no | no |
| d1e_one_active_pair | 0.000754275 | 0.000965957 | 0 | no | no |

## Interpretation

D1e tests whether passive intermediate-node loss was the main issue by distributing active source/sink-aspect regions around the ring. Rows remain native evidence only if they arise without role switching, edge storage, propulsion, or a circulatory proposal term.

## Errors

- none
