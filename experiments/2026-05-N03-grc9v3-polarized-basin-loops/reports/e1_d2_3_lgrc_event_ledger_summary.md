# E1.2 D2.3 To LGRC Event Ledger Summary

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/convert_d2_3_to_e1_lgrc_ledger.py
```

Status: `passed`

Converted lanes: `12`
Total ledger events: `811`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

## Event Counts By Kind

- `packet_departure`: `240`
- `packet_arrival`: `235`
- `state_trigger`: `240`
- `self_rearm`: `44`
- `cycle_complete`: `44`
- `control_blocked`: `8`

## Lane Ledgers

- `D2.3-U0-no-surplus` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_u0_no_surplus_ledger.jsonl` (`1` events)
- `D2.3-P-self-rearming-cw` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_p_self_rearming_cw_ledger.jsonl` (`162` events)
- `D2.3-R-self-rearming-ccw` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_r_self_rearming_ccw_ledger.jsonl` (`162` events)
- `D2.3-C-single-pass-no-rearm` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_single_pass_no_rearm_ledger.jsonl` (`1` events)
- `D2.3-C-subthreshold` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_subthreshold_ledger.jsonl` (`1` events)
- `D2.3-C-threshold-too-high` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_threshold_too_high_ledger.jsonl` (`1` events)
- `D2.3-S-low-threshold` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_s_low_threshold_ledger.jsonl` (`162` events)
- `D2.3-C-wrong-direction` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_wrong_direction_ledger.jsonl` (`141` events)
- `D2.3-C-forward-only` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_forward_only_ledger.jsonl` (`4` events)
- `D2.3-C-broken-return` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_broken_return_ledger.jsonl` (`10` events)
- `D2.3-C-scrambled-order` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_c_scrambled_order_ledger.jsonl` (`4` events)
- `D2.3-N-jittered-delay` -> `outputs/e1_d2_3_lgrc_event_ledgers/d2_3_n_jittered_delay_ledger.jsonl` (`162` events)

## Inference Notes

- `budget_after`
- `budget_before`
- `event_id`
- `event_kind`
- `event_time_key`
- `node_proper_time`
- `scheduler_event_index`

## Errors

- none
