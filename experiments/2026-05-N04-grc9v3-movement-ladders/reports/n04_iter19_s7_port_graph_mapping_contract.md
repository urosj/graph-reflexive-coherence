# N04 Iteration 19 S7 Port-Graph Mapping Contract

Status: **passed**

Claim ceiling: `s7_port_graph_mapping_contract_only`

Iteration 19 freezes a role-based S3-to-S7 port mapping. It runs no behavior probe.

## Mapping

- mapping id: `s3_integrated_2d_gate_to_s7_fixed_port_graph_v1`
- mapping type: `role_based_port_mapping`
- node-id preserving: `False`
- target fixture: `S7_port_graph_fixed_composed_gate_v1`
- topology mutation enabled: `False`

## Checks

- `source_18h_passed`: `True`
- `source_ceiling_is_integrated_2d_gate`: `True`
- `mapping_is_role_based_not_node_id_preserving`: `True`
- `all_required_ports_declared`: `True`
- `topology_mutation_disabled_by_default`: `True`
- `balanced_preference_has_zero_global_sum`: `True`
- `summary_only_no_new_probe`: `True`
- `no_claim_promotion`: `True`

## Boundary

This contract is not behavior evidence. It only freezes the S7 fixed-port role mapping before Iteration 19-A execution. Port-graph transfer, adaptive topology, topology-mutating movement, native LGRC choice selection, RC identity collapse, locomotion-like behavior, agency, and unrestricted movement remain blocked.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iter19_s7_port_graph_mapping_contract.py
```
