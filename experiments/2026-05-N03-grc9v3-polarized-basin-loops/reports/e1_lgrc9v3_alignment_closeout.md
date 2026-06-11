# E1.5 LGRC9V3 Alignment Closeout

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_5_alignment_closeout.py
```

Status: `complete`

Final decision:

`stop_and_publish_n03_native_grc9v3_negative_packet_positive_lgrc_adapter_compatible`

E1 answered its central question: D2.3 can be faithfully represented as LGRC9V3-style causal packet history. The result is adapter-compatible, not native runtime execution, so E1 should close without requesting a core task or movement handoff.

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

## Summary Claims

- `native_fixed_topology_grc9v3_proposal_flux`: `negative_for_loop_generation_under_tested_fixtures`
- `experiment_local_packetized_mechanism`: `positive_for_self_rearming_packet_pulse_under_controls`
- `lgrc_style_event_ledger`: `validated_from_ledger_only`
- `lgrc9v3_compatibility`: `adapter_compatible`
- `core_task_requested`: `False`

## Validated Evidence

- `surface_inventory_classification`: `adapter_compatible`
- `schema_validation_status`: `passed`
- `converted_lane_count`: `12`
- `ledger_event_count`: `811`
- `ledger_only_validation_status`: `passed`
- `ledger_positive_lanes`: `D2.3-P-self-rearming-cw, D2.3-R-self-rearming-ccw, D2.3-S-low-threshold, D2.3-N-jittered-delay`
- `compatibility_classification`: `adapter_compatible`

## Commands

### E1.0

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e1_0_lgrc9v3_surface_inventory.py
```

### E1.1

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_1_event_ledger_schema.py
```

### E1.2

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/convert_d2_3_to_e1_lgrc_ledger.py
```

### E1.3

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_3_ledger_only.py
```

### E1.4

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_4_lgrc9v3_compatibility.py
```

### E1.5

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_5_alignment_closeout.py
```

## Artifacts

### E1.0

- `outputs/e1_lgrc9v3_surface_inventory.json`
- `reports/e1_lgrc9v3_surface_inventory.md`

### E1.1

- `configs/e1_lgrc9v3_event_ledger_schema.json`
- `outputs/e1_event_ledger_schema_validation.json`
- `reports/e1_event_ledger_schema_validation.md`

### E1.2

- `outputs/e1_d2_3_lgrc_event_ledgers/*.jsonl`
- `outputs/e1_d2_3_lgrc_event_ledger_summary.json`
- `reports/e1_d2_3_lgrc_event_ledger_summary.md`

### E1.3

- `outputs/e1_ledger_only_validation.json`
- `reports/e1_ledger_only_validation.md`

### E1.4

- `outputs/e1_lgrc9v3_compatibility.json`
- `reports/e1_lgrc9v3_compatibility.md`

### E1.5

- `outputs/e1_lgrc9v3_alignment_closeout.json`
- `reports/e1_lgrc9v3_alignment_closeout.md`

## Blocked Claims

- native GRC9V3 loop formation
- native LGRC9V3 execution
- movement or locomotion
- agency or intention
- biological behavior
- multi-pole native behavior

## Future Question

Can native LGRC9V3.step or LGRC9V3.run_event_queue produce the D2.3 event ledger through declared runtime primitives?

E1 does not open that branch. It closes as an adapter-only alignment
record.
