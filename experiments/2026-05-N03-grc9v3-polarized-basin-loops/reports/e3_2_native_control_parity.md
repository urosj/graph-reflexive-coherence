# E3.2 Native Control Parity

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
```

Status: `passed`

```json
{
  "classification": "native_lgrc9v3_control_parity_passed",
  "controls": {
    "broken_return": {
      "lane_id": "E3.2-C-broken-return",
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": false,
      "primary_blocker": "route_aspect_closed_loop_validation_failed"
    },
    "forward_only": {
      "cycle_count": 0,
      "event_count": 1,
      "lane_id": "E3.2-C-forward-only",
      "max_event_budget_error": 8.881784197001252e-16,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": false,
      "native_surplus_trigger": true,
      "primary_blocker": "return_chain_missing",
      "scheduled_event_count": 1,
      "self_rearm_count": 0,
      "topology_changed": false,
      "validation": {
        "candidate_count": 0,
        "completed_count": 0,
        "failure_reasons": [
          "no_completed_self_rearm_evidence"
        ],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": false,
        "validated_self_rearm_evidence_ids": [],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    },
    "no_surplus": {
      "cycle_count": 0,
      "event_count": 0,
      "lane_id": "E3.2-C-no-surplus",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": false,
      "native_surplus_trigger": false,
      "primary_blocker": "surplus_gate_failed",
      "scheduled_event_count": 0,
      "self_rearm_count": 0,
      "topology_changed": false,
      "validation": {
        "candidate_count": 0,
        "completed_count": 0,
        "failure_reasons": [
          "no_completed_self_rearm_evidence"
        ],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": false,
        "validated_self_rearm_evidence_ids": [],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    },
    "scrambled_order": {
      "lane_id": "E3.2-C-scrambled-order",
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": false,
      "primary_blocker": "route_aspect_pole_contiguity_validation_failed"
    },
    "subthreshold": {
      "cycle_count": 0,
      "event_count": 0,
      "lane_id": "E3.2-C-subthreshold",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": false,
      "native_surplus_trigger": false,
      "primary_blocker": "threshold_gate_failed",
      "scheduled_event_count": 0,
      "self_rearm_count": 0,
      "topology_changed": false,
      "validation": {
        "candidate_count": 0,
        "completed_count": 0,
        "failure_reasons": [
          "no_completed_self_rearm_evidence"
        ],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": false,
        "validated_self_rearm_evidence_ids": [],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    },
    "threshold_too_high": {
      "cycle_count": 0,
      "event_count": 4,
      "lane_id": "E3.2-C-threshold-too-high",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": false,
      "native_surplus_trigger": false,
      "primary_blocker": "threshold_gate_failed",
      "scheduled_event_count": 0,
      "self_rearm_count": 0,
      "topology_changed": false,
      "validation": {
        "candidate_count": 0,
        "completed_count": 0,
        "failure_reasons": [
          "no_completed_self_rearm_evidence"
        ],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": false,
        "validated_self_rearm_evidence_ids": [],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    },
    "wrong_direction": {
      "cycle_count": 0,
      "event_count": 5,
      "lane_id": "E3.2-C-wrong-direction",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": false,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": false,
      "native_surplus_trigger": true,
      "primary_blocker": "route_direction_gate_failed",
      "scheduled_event_count": 1,
      "self_rearm_count": 0,
      "topology_changed": false,
      "validation": {
        "candidate_count": 0,
        "completed_count": 0,
        "failure_reasons": [
          "no_completed_self_rearm_evidence"
        ],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": false,
        "validated_self_rearm_evidence_ids": [],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    }
  },
  "movement_claim_allowed": false,
  "native_grc9v3_loop_evidence": false,
  "required_controls": [
    "no_surplus",
    "subthreshold",
    "threshold_too_high",
    "wrong_direction",
    "forward_only",
    "broken_return",
    "scrambled_order"
  ],
  "status": "passed"
}
```
