# N04 Iteration 19-C S7 Adaptive Gate With Native Surface Lineage

Status: **passed**

Claim ceiling: `adaptive_topology_entry_candidate`

Promotion result: `supported`

Iteration 19-C reruns the Iteration 19-B adaptive-topology entry gate after Phase 8 added native causal pulse-substrate surface lineage transport.

## Positive Lineage Lane

- source surface digest: `1cd1b0b50f096129b79170c084e5937e0407ae600b5d07ea35666a17bbf8ee3c`
- transported surface digest: `b0f871911c54f11cc54a565160217b3718e13e4872d201a15d99c30a1e7789f6`
- producer reads transported digest: `True`
- artifact-only validator passed: `True`

## Controls

- `transported_surface_successor_control`: passed=`True`, reason=`producer_reads_transported_successor_surface_digest`
- `superseded_source_stale_read_control`: passed=`True`, reason=`producer_stale_surface_read_blocked`
- `topology_only_claim_promotion_control`: passed=`True`, reason=`topology_lineage_transport_is_entry_evidence_not_topology_mutating_movement`

## Checks

- `iteration_19a_fixed_port_baseline_passed`: `True`
- `iteration_19b_boundary_passed_fail_closed`: `True`
- `phase8_surface_lineage_transport_supported`: `True`
- `transported_surface_row_emitted`: `True`
- `producer_reads_transported_digest`: `True`
- `producer_does_not_read_stale_source_digest`: `True`
- `artifact_only_lineage_replay_passed`: `True`
- `superseded_source_read_blocked`: `True`
- `topology_mutating_movement_still_blocked`: `True`
- `broader_claims_blocked`: `True`

## Boundary

This supports an adaptive-topology entry candidate only. Topology-mutating movement, native LGRC choice selection, RC identity collapse, semantic choice, agency, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, and unrestricted movement remain blocked.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.py
```
