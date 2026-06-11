# E3.3 Snapshot And Telemetry Reproduction

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
```

Status: `passed`

```json
{
  "classification": "native_lgrc9v3_snapshot_telemetry_reproduction_passed",
  "continue_after_load": {
    "completed_count_after_continue": 13,
    "duplicate_reason_code": "idempotent_causal_surface_already_produced",
    "duplicate_scheduled_event_count": 0,
    "failure_reasons": [],
    "packet_event_count_after_continue": 28,
    "producer_count_after_continue": 15,
    "scheduled_event_count": 1,
    "valid": true
  },
  "counts_after": {
    "packet_events": 26,
    "producer": 13,
    "self_rearm": 12
  },
  "counts_before": {
    "packet_events": 26,
    "producer": 13,
    "self_rearm": 12
  },
  "movement_claim_allowed": false,
  "native_grc9v3_loop_evidence": false,
  "producer_log_preserved": true,
  "route_config_preserved": true,
  "self_rearm_log_preserved": true,
  "snapshot_validation": {
    "candidate_count": 12,
    "completed_count": 12,
    "failure_reasons": [],
    "movement_claim_allowed": false,
    "native_d2_3_equivalent": false,
    "native_grc9v3_loop_evidence": false,
    "valid": true,
    "validated_self_rearm_evidence_ids": [
      "6dfa2b6e18c0122edafbeaafaeea52d61e2b65ed1fb59fbe6f0e5b42e3fc4b3b",
      "4a96b3e7307ecec3907e7bc0031358d72738e3a90b01c1aafe5093eeefb56c06",
      "be0fa545149d6abe0271cb0db64fb35e8c6f4397f3632b9e5d6818c365d8cb2a",
      "87fae2f67a1d33962f9c86653f9b60e3edbe0389f60fbc020ca895991dff3ed3",
      "f2f1b81a26d5eb44d264d6bee13548004ecedd755b2ec8d0747f700f84d68f39",
      "714a20a6c78336a19e9ae4351f21dffaa79fdf3eca976fe444d8ec622435e14e",
      "c492a5f64e37529ec8581cef3ee91d17c21bacd50ba3cf33826cc5f5bd63bdcd",
      "dc0f9721b94ce072207c6134d7a163588726ab16c6fc3f8e21acc3715c0d2293",
      "980995ee63a3e6bb380d48f923ff6ef00ba53e3dbe2d8d6d68778d813560655b",
      "01f38b6ab456938b6fee06352314f5ef93a874e26cd0b48c87af32e86d726a33",
      "80f9705c33371a215ae1d9f49fc46d7249be69cdfa5287166e71b6eb1744d5e7",
      "ecf4e01cb1c9317f977eacbcc7dc29e79c83c724e7b3a802d020213543da35f1"
    ],
    "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
  },
  "status": "passed",
  "telemetry_packet_loop": {
    "adapter_required_for_d2_3_semantics": false,
    "autonomous_production_result_count": 15,
    "completed_self_rearm_count": 13,
    "latest_reason_code": "idempotent_causal_surface_already_produced",
    "movement_claim_allowed": false,
    "native_d2_3_equivalent": false,
    "native_d2_3_equivalent_requires_control_parity": true,
    "native_grc9v3_loop_evidence": false,
    "native_lgrc9v3_execution": true,
    "native_packet_execution": true,
    "native_self_rearm_evidence": true,
    "native_static_route_only": false,
    "native_surplus_trigger": true,
    "producer_policy": "packet_departure_from_route_aspect_surplus_policy",
    "route_aspect_digest": "25ce1cc1550c0a717d4c1bcaa7f4179789024b67c2c22893df1f0fa21d41cb57",
    "route_aspect_surplus_trigger_configured": true,
    "self_rearm_evidence_count": 13
  },
  "telemetry_validation": {
    "candidate_count": 12,
    "completed_count": 12,
    "failure_reasons": [],
    "movement_claim_allowed": false,
    "native_d2_3_equivalent": false,
    "native_grc9v3_loop_evidence": false,
    "valid": true,
    "validated_self_rearm_evidence_ids": [
      "6dfa2b6e18c0122edafbeaafaeea52d61e2b65ed1fb59fbe6f0e5b42e3fc4b3b",
      "4a96b3e7307ecec3907e7bc0031358d72738e3a90b01c1aafe5093eeefb56c06",
      "be0fa545149d6abe0271cb0db64fb35e8c6f4397f3632b9e5d6818c365d8cb2a",
      "87fae2f67a1d33962f9c86653f9b60e3edbe0389f60fbc020ca895991dff3ed3",
      "f2f1b81a26d5eb44d264d6bee13548004ecedd755b2ec8d0747f700f84d68f39",
      "714a20a6c78336a19e9ae4351f21dffaa79fdf3eca976fe444d8ec622435e14e",
      "c492a5f64e37529ec8581cef3ee91d17c21bacd50ba3cf33826cc5f5bd63bdcd",
      "dc0f9721b94ce072207c6134d7a163588726ab16c6fc3f8e21acc3715c0d2293",
      "980995ee63a3e6bb380d48f923ff6ef00ba53e3dbe2d8d6d68778d813560655b",
      "01f38b6ab456938b6fee06352314f5ef93a874e26cd0b48c87af32e86d726a33",
      "80f9705c33371a215ae1d9f49fc46d7249be69cdfa5287166e71b6eb1744d5e7",
      "ecf4e01cb1c9317f977eacbcc7dc29e79c83c724e7b3a802d020213543da35f1"
    ],
    "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
  }
}
```
