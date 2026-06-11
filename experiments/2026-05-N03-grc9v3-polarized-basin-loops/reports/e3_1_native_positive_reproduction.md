# E3.1 Native Positive Reproduction

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
```

Status: `passed`

```json
{
  "classification": "native_lgrc9v3_positive_reproduction_passed",
  "direction_symmetry": {
    "cycle_count_delta": 0,
    "passed": true,
    "self_rearm_count_delta": 0,
    "trigger_count_delta": 0
  },
  "movement_claim_allowed": false,
  "native_grc9v3_loop_evidence": false,
  "positive_rows": {
    "clockwise": {
      "adapter_required_for_d2_3_semantics": false,
      "cycle_count": 3,
      "direction": "clockwise",
      "duplicate_suppressed_count": 1,
      "event_count": 76,
      "lane_id": "E3.1-positive-clockwise",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": true,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": true,
      "native_surplus_trigger": true,
      "prototype_runner_used_as_execution_engine": false,
      "route_aspect_digest": "25ce1cc1550c0a717d4c1bcaa7f4179789024b67c2c22893df1f0fa21d41cb57",
      "route_order": [
        "S1_to_K2",
        "K2_to_S2",
        "S2_to_K1",
        "K1_to_S1"
      ],
      "self_rearm_count": 12,
      "topology_changed": false,
      "trigger_count": 12,
      "validation": {
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
    },
    "counter_clockwise": {
      "adapter_required_for_d2_3_semantics": false,
      "cycle_count": 3,
      "direction": "counter_clockwise",
      "duplicate_suppressed_count": 0,
      "event_count": 76,
      "lane_id": "E3.1-positive-counter_clockwise",
      "max_event_budget_error": 0.0,
      "movement_claim_allowed": false,
      "native_d2_3_equivalent": true,
      "native_grc9v3_loop_evidence": false,
      "native_lgrc9v3_execution": true,
      "native_packet_execution": true,
      "native_self_rearm_evidence": true,
      "native_surplus_trigger": true,
      "prototype_runner_used_as_execution_engine": false,
      "route_aspect_digest": "a621e96cd477308e0365b1d06f2a80f4a1285c7c7f4680d24cd3715a878ef3c8",
      "route_order": [
        "S1_to_K1",
        "K1_to_S2",
        "S2_to_K2",
        "K2_to_S1"
      ],
      "self_rearm_count": 12,
      "topology_changed": false,
      "trigger_count": 12,
      "validation": {
        "candidate_count": 12,
        "completed_count": 12,
        "failure_reasons": [],
        "movement_claim_allowed": false,
        "native_d2_3_equivalent": false,
        "native_grc9v3_loop_evidence": false,
        "valid": true,
        "validated_self_rearm_evidence_ids": [
          "a041f9fe4b6f9689547b08f4e4ee89e701fe1868570248d92bacdcf7fd9d855b",
          "0b469913ee3d1780c5082e7caae11f9dac921767939ad59ca76c960caaed8053",
          "ad9fee80292162e52c26cb42a2499ab9dce1aecaf0a9d82f698322791eed2359",
          "000c0e434a48b6df668939eaed07ca526fb8fb3d19b1761004b62048a58536a3",
          "2f593922f59e893a0c1140c1f8fba03bb08e458ad2a1d1e352cf076d7a3fb1f8",
          "c76d5ac2be06cbe6d215f333a839e5241d4f9f25d9ebce570251b16b25f69312",
          "c68fcba08e7bd6d394d4472de90fb1c0ca2b60602f994032450b3c019592010c",
          "59294f47c1e983bc67b38d65b164e5572d6f358e480c3b10ddd6462c00952f97",
          "d60b3b906fbdd1725bf3a75b39fdee8e2fb257308e962a787fb2aa8e7cd771c7",
          "9c88b3cc3a0e5424aed6782c8528aa15d7e7ef00417b60ae8e022a4c68ed55e4",
          "484ee693518cc7acfecd18feaad802953a36af0ace0875b6f09d8b987a4be7d1",
          "639b03de9fad248d7219ea273f45c715c51f97cc18b3337c08384a5c8a4f8083"
        ],
        "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts"
      }
    }
  },
  "status": "passed"
}
```
