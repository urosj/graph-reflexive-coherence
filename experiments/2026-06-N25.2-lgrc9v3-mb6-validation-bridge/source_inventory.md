# N25.2 Source Inventory Scaffold

This scaffold records the initial source set before Iteration 1 generates the
audited JSON and Markdown source-inventory artifacts.

## Source Consumption Rules

```text
N25 = scoped BF5 / N25-C6 context
N25.1 = MB ladder and Phase 8 requirements context
Phase 8 multi-basin closeout = MB5 implementation evidence
LGRC9V3 spec/tests/code = admissibility and implementation-boundary evidence
examples = telemetry/visual corroboration only
```

N25.2 must not consume:

```text
N25 BF5 as independent multi-basin formation
N25.1 requirements as runtime evidence
Phase 8 MB5 as automatic MB6
producer-assisted evidence as native support
visual graph growth as standalone MB6 proof
```

## Initial Sources

| Source ID | Path | May Consume As | Must Not Consume As |
|---|---|---|---|
| `n25_closeout_json` | `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json` | scoped BF5 / N25-C6 context | independent multi-basin formation, MB6 |
| `n25_closeout_report` | `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/reports/n25_closeout_and_n26_handoff.md` | interpretation of scoped BF5 and BF6 blockers | runtime evidence, native support |
| `n25_1_closeout_json` | `experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/outputs/n25_1_closeout_and_phase8_extension_handoff.json` | MB ladder, requirements, N26 constraints | runtime evidence, MB5/MB6 support |
| `n25_1_closeout_report` | `experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/reports/n25_1_closeout_and_phase8_extension_handoff.md` | requirements interpretation | runtime evidence, MB5/MB6 support |
| `phase8_closeout_json` | `implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.json` | Phase 8 MB5 implementation closeout evidence | automatic MB6, native support, agency |
| `phase8_closeout_report` | `implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md` | Phase 8 MB5 interpretation and N25.2 transition | automatic MB6, N26 unscoped consumption |
| `phase8_contract_schema_json` | `implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.json` | schema/admissibility context | positive runtime result by itself |
| `phase8_contract_schema_report` | `implementation/Phase-8-LGRC9-MultiBasinFormationContractSchema.md` | schema interpretation | positive runtime result by itself |
| `phase8_plan` | `implementation/Phase-8-LGRC9-MultiBasinFormationPlan.md` | planned gate and source boundary context | final result evidence by itself |
| `phase8_checklist` | `implementation/Phase-8-LGRC9-MultiBasinFormationChecklist.md` | implementation record and verification context | automatic MB6 |
| `phase8_handoff` | `implementation/Phase-8-LGRC9-Handoff.md` | current Phase 8 state pointer | MB6 support by itself |
| `lgrc9v3_spec` | `specs/lgrc-9-v3-spec.md` | implementation contract and claim boundary | experimental result by itself |
| `examples_readme` | `examples/lgrc9v3/README.md` | example interpretation and visual boundary | proof by visualization |
| `runtime_contract_code` | `src/pygrc/models/lgrc_9_v3_contract.py` | implementation-boundary audit | claim support without artifacts |
| `runtime_code` | `src/pygrc/models/lgrc_9_v3_runtime.py` | producer/runtime mutation-boundary audit | claim support without artifacts |
| `runtime_state_code` | `src/pygrc/models/lgrc_9_v3_runtime_state.py` | runtime state surface audit | claim support without artifacts |
| `telemetry_code` | `src/pygrc/telemetry/lgrc9v3_contract.py` | telemetry export audit | proof by telemetry alone |
| `contract_tests` | `tests/models/test_lgrc_9_v3_contract.py` | test/admissibility evidence | MB6 support by itself |
| `runtime_tests` | `tests/models/test_lgrc_9_v3_runtime.py` | test/admissibility evidence | MB6 support by itself |
| `autonomy_contract_tests` | `tests/models/test_lgrc_9_v3_autonomy_contract.py` | producer discipline evidence | native support evidence |
| `telemetry_tests` | `tests/telemetry/test_lgrc9v3_contract.py` | telemetry contract evidence | proof by telemetry alone |
| `visualization_tests` | `tests/visualization/test_visualization.py` | visualization contract evidence | proof by visualization alone |

## Initial Boundary

```text
starting_mb_ceiling = MB5_control_backed_native_multi_basin_formation_candidate
starting_mb6_supported = false
n26_unscoped_consumption_allowed = false
runtime_implementation_opened = false
```
