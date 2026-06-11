# E1.1 Event-Ledger Schema Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_1_event_ledger_schema.py
```

Status: `passed`

Schema: `n03_e1_event_ledger_schema_validation_v1`

Sample record count: `6`

Validated event kinds:

- `control_blocked`
- `cycle_complete`
- `packet_arrival`
- `packet_departure`
- `self_rearm`
- `state_trigger`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

Errors:

- none
