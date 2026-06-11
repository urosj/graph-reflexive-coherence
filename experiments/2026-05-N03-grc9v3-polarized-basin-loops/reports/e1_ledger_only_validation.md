# E1.3 Ledger-Only Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_3_ledger_only.py
```

Status: `passed`

Validated lanes: `12`
Positive lanes from ledger: `D2.3-P-self-rearming-cw, D2.3-R-self-rearming-ccw, D2.3-S-low-threshold, D2.3-N-jittered-delay`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

## Checks

- `packet_ids_unique`: `True`
- `parent_packet_ids_resolve`: `True`
- `no_unknown_channels`: `True`
- `departure_arrival_amounts_preserved`: `True`
- `node_plus_packet_budget_reconstructable`: `True`
- `cycles_match_canonical_route`: `True`
- `self_rearm_after_returned_arrival`: `True`
- `controls_remain_negative`: `True`
- `clockwise_counter_clockwise_symmetry`: `True`

## Lane Summary

| Lane | Expected | Ledger Positive | Cycles | Self-Rearms | Departures | Arrivals | Blocked | Errors |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D2.3-U0-no-surplus | False | False | 0 | 0 | 0 | 0 | 1 | 0 |
| D2.3-P-self-rearming-cw | True | True | 11 | 11 | 47 | 46 | 0 | 0 |
| D2.3-R-self-rearming-ccw | True | True | 11 | 11 | 47 | 46 | 0 | 0 |
| D2.3-C-single-pass-no-rearm | False | False | 0 | 0 | 0 | 0 | 1 | 0 |
| D2.3-C-subthreshold | False | False | 0 | 0 | 0 | 0 | 1 | 0 |
| D2.3-C-threshold-too-high | False | False | 0 | 0 | 0 | 0 | 1 | 0 |
| D2.3-S-low-threshold | True | True | 11 | 11 | 47 | 46 | 0 | 0 |
| D2.3-C-wrong-direction | False | False | 0 | 0 | 47 | 46 | 1 | 0 |
| D2.3-C-forward-only | False | False | 0 | 0 | 1 | 1 | 1 | 0 |
| D2.3-C-broken-return | False | False | 0 | 0 | 3 | 3 | 1 | 0 |
| D2.3-C-scrambled-order | False | False | 0 | 0 | 1 | 1 | 1 | 0 |
| D2.3-N-jittered-delay | True | True | 11 | 11 | 47 | 46 | 0 | 0 |

## Direction Symmetry

```json
{"ccw_lane": "D2.3-R-self-rearming-ccw", "cw_lane": "D2.3-P-self-rearming-cw", "deltas": {"computed_cycle_count": 0, "cycle_complete_count": 0, "event_count": 0, "packet_arrival_count": 0, "packet_departure_count": 0, "self_rearm_count": 0, "state_trigger_count": 0, "unarrived_packet_count": 0}, "passed": true}
```

## Errors

- none
