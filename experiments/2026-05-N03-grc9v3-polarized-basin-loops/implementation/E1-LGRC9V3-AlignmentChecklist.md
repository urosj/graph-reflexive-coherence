# E1 LGRC9V3 Alignment Checklist

This checklist tracks the experiment-local E1 alignment branch.

Primary plan:

- [`E1-LGRC9V3-AlignmentPlan.md`](./E1-LGRC9V3-AlignmentPlan.md)

## Ground Rules

- Keep E1 under
  `experiments/2026-05-N03-grc9v3-polarized-basin-loops/`.
- Do not modify `src/*`.
- Treat any required `src/*` change as a stop condition.
- E1 is an alignment/adapter branch, not a core implementation branch.
- D2.3 remains experiment-local packetized prototype evidence.
- Do not promote D2.3 to native GRC9V3 evidence.
- Do not claim movement, locomotion, agency, intention, biological behavior, or
  multi-pole native behavior.
- Generated E1 reports must state:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true|false
adapter_only = true|false
movement_claim_allowed = false
```

## E1.0. Scope And Surface Inventory

Status: complete.

### Goal

Inventory existing LGRC9V3 event, packet, queue, snapshot, and telemetry
surfaces relevant to D2.3 alignment.

### Checks

- [x] Inspect existing LGRC9V3 modules and docs.
- [x] Record whether packet departure records exist.
- [x] Record whether packet arrival records exist.
- [x] Record whether in-flight packet ledgers exist.
- [x] Record whether packet amount participates in budget evidence.
- [x] Record whether event-time key is serialized.
- [x] Record whether node proper time is serialized.
- [x] Record whether event-time key and node proper time are distinct.
- [x] Record whether route/channel declarations exist.
- [x] Record whether state-trigger policies exist.
- [x] Record missing surfaces without changing `src/*`.

### Outputs

- [x] `outputs/e1_lgrc9v3_surface_inventory.json`
- [x] `reports/e1_lgrc9v3_surface_inventory.md`

### Verification

- [x] Inventory command recorded.
- [x] Inventory is reproducible.
- [x] No `src/*` diff.

### Run Record

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e1_0_lgrc9v3_surface_inventory.py
```

Result:

```json
{"adapter_only": true, "classification": "adapter_compatible", "missing_surface_count": 3, "status": "complete"}
```

Summary:

- Existing LGRC9V3 surfaces are sufficient for packet records, event queue
  ordering, in-flight packet budgets, causal clocks, runtime state snapshots,
  telemetry/checkpoint overlays, and queued packet execution.
- D2.3 still needs experiment-local adapter surfaces for pole/channel route
  semantics, measured pole-surplus state triggers, and the semantic
  `self_rearm` event label.
- Boundary preserved:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

## E1.1. Event-Ledger Mapping

Status: complete.

### Goal

Define the minimal LGRC-style event ledger needed to represent D2.3.

### Checks

- [x] Define `packet_departure` event.
- [x] Define `packet_arrival` event.
- [x] Define `state_trigger` event.
- [x] Define `self_rearm` event.
- [x] Define `cycle_complete` event.
- [x] Define `control_blocked` event.
- [x] Include `event_id`.
- [x] Include `scheduler_event_index`.
- [x] Include `event_time_key`.
- [x] Include `node_proper_time`.
- [x] Include `packet_id` and `parent_packet_id`.
- [x] Include amount, source, target, and channel fields.
- [x] Include trigger value and trigger threshold.
- [x] Include declared route and canonical route step.
- [x] Include control lane metadata.
- [x] Mark inferred fields explicitly.

### Outputs

- [x] `configs/e1_lgrc9v3_event_ledger_schema.json`
- [x] schema notes in report.
- [x] `outputs/e1_event_ledger_schema_validation.json`
- [x] `reports/e1_event_ledger_schema_validation.md`

### Verification

- [x] Schema validates against sample D2.3 records.
- [x] No `src/*` diff.

### Run Record

Schema validation command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_1_event_ledger_schema.py
```

Result:

```json
{"sample_record_count": 6, "status": "passed", "validated_event_kinds": ["control_blocked", "cycle_complete", "packet_arrival", "packet_departure", "self_rearm", "state_trigger"]}
```

Summary:

- E1.1 defines the six required event kinds:
  `packet_departure`, `packet_arrival`, `state_trigger`, `self_rearm`,
  `cycle_complete`, and `control_blocked`.
- The schema preserves event ordering, event-time key, node proper-time
  surface, packet ids, parent packet ids, amount, pole/channel fields, trigger
  evidence, route evidence, control lane metadata, and explicit inference
  notes.
- The schema remains experiment-local and adapter-only:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

## E1.2. D2.3 Ledger Converter

Status: complete.

### Goal

Convert D2.3 JSON/time-series artifacts into the E1 event ledger schema.

### Inputs

- [x] `outputs/d2_3_self_rearming_packets.json`
- [x] `outputs/d2_3_self_rearming_packets_timeseries/*.jsonl`

### Checks

- [x] Read D2.3 summary artifact.
- [x] Read D2.3 timeseries artifacts.
- [x] Emit one ledger per D2.3 lane.
- [x] Preserve packet ids.
- [x] Preserve parent packet ids.
- [x] Preserve trigger/rearm/cycle evidence.
- [x] Preserve lane controls.
- [x] Mark inferred event-time/proper-time fields.
- [x] Do not recompute positive outcomes from hidden state.

### Outputs

- [x] `outputs/e1_d2_3_lgrc_event_ledgers/*.jsonl`
- [x] `outputs/e1_d2_3_lgrc_event_ledger_summary.json`
- [x] `reports/e1_d2_3_lgrc_event_ledger_summary.md`

### Verification

- [x] Converter command recorded.
- [x] JSON/JSONL artifacts are deterministic.
- [x] No `src/*` diff.

### Run Record

Converter command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/convert_d2_3_to_e1_lgrc_ledger.py
```

Result:

```json
{"converted_lane_count": 12, "errors": 0, "event_counts_by_kind": {"control_blocked": 8, "cycle_complete": 44, "packet_arrival": 235, "packet_departure": 240, "self_rearm": 44, "state_trigger": 240}, "status": "passed", "total_event_count": 811}
```

Summary:

- E1.2 converted all 12 D2.3 lanes into LGRC-style JSONL ledgers.
- Positive packet lanes preserve packet departures, arrivals, state triggers,
  self-rearm evidence, and cycle-complete evidence.
- Negative/control lanes preserve `control_blocked` evidence rather than being
  silently dropped.
- The converter marks inferred fields explicitly:
  `event_id`, `scheduler_event_index`, `event_time_key`, `node_proper_time`,
  `event_kind`, `budget_before`, and `budget_after`.
- Boundary preserved:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

## E1.3. Ledger-Only Validator

Status: complete.

### Goal

Validate D2.3 claims from the converted LGRC-style ledger alone.

### Checks

- [x] Packet ids are unique.
- [x] Parent packet ids resolve.
- [x] No unknown channels.
- [x] Departures and arrivals preserve packet amount.
- [x] In-flight packet budget is reconstructable.
- [x] Node-plus-packet budget is reconstructable.
- [x] Completed cycles match canonical route.
- [x] Self-rearm events occur only after returned-packet arrivals.
- [x] Wrong-direction control remains negative for declared direction.
- [x] Forward-only control remains negative.
- [x] Broken-return control remains negative.
- [x] Scrambled-order control remains negative.
- [x] Clockwise/counter-clockwise symmetry holds.

### Outputs

- [x] `outputs/e1_ledger_only_validation.json`
- [x] `reports/e1_ledger_only_validation.md`

### Verification

- [x] Validator command recorded.
- [x] Ledger-only results match D2.3 expected outcomes.
- [x] No `src/*` diff.

### Run Record

Validator command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e1_3_ledger_only.py
```

Result:

```json
{"errors": 0, "ledger_positive_lanes": ["D2.3-P-self-rearming-cw", "D2.3-R-self-rearming-ccw", "D2.3-S-low-threshold", "D2.3-N-jittered-delay"], "status": "passed", "symmetry_passed": true, "validated_lane_count": 12}
```

Summary:

- E1.3 validated D2.3 outcomes from the converted LGRC-style ledgers alone.
- Packet ids are unique; parent packet ids resolve; channel ids are known;
  departure/arrival amounts match; and node-plus-packet budgets reconstruct.
- `cycle_complete` events match the declared canonical route.
- `self_rearm` events occur only after returned-packet arrivals and after the
  next departure event has been created by the trigger.
- Wrong-direction, forward-only, broken-return, scrambled-order, no-surplus,
  subthreshold, threshold-too-high, and single-pass controls remain negative.
- Clockwise/counter-clockwise positive lanes are symmetric.
- Boundary preserved:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

## E1.4. LGRC9V3 Compatibility Report

Status: complete.

### Goal

Classify D2.3 against existing LGRC9V3 surfaces.

### Checks

- [x] Determine whether result is `native_surface_compatible`.
- [x] Determine whether result is `adapter_compatible`.
- [x] Determine whether result is `missing_runtime_primitive`.
- [x] Determine whether result is `not_lgrc_aligned`.
- [x] List sufficient existing surfaces.
- [x] List missing surfaces.
- [x] Propose names for missing surfaces.
- [x] Record whether a separate core task should be requested.
- [x] Keep E1 local unless separately approved.

### Outputs

- [x] `outputs/e1_lgrc9v3_compatibility.json`
- [x] `reports/e1_lgrc9v3_compatibility.md`

### Verification

- [x] Compatibility report command recorded.
- [x] Claim boundary is explicit.
- [x] No `src/*` diff.

### Run Record

Compatibility command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_4_lgrc9v3_compatibility.py
```

Result:

```json
{"adapter_only": true, "classification": "adapter_compatible", "request_core_task_now": false, "status": "complete"}
```

Summary:

- E1.4 classifies D2.3 as `adapter_compatible`.
- D2.3 is not `native_surface_compatible` because pole/channel route
  semantics, surplus-trigger policy, and `self_rearm` evidence remain
  experiment-local adapter surfaces.
- D2.3 is not `missing_runtime_primitive` for E1 because the packet/event/
  ledger/clock surfaces needed for adapter alignment already exist.
- D2.3 is not `not_lgrc_aligned` because E1.3 validated the converted
  LGRC-style ledger from ledger evidence alone.
- No separate core task is requested now. A core task should only be promoted
  if a later branch asks `LGRC9V3.step` or `LGRC9V3.run_event_queue` to
  natively produce the D2.3 event ledger.
- Boundary preserved:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

## E1.5. Closeout And Next Branch Decision

Status: complete.

### Goal

Close E1 with a decision.

### Allowed Outcomes

- [x] Adapter-only alignment record.
- [x] Stop and publish N03 as native-negative / packet-positive mechanism
      result.

Non-selected E1 closeout options:

```text
experiment-local E2 proposal
stop-point note requesting separate core LGRC9V3 task
movement-ladders handoff under packetized-surface claim ceiling
```

These are not pending tasks. E1 itself did not open E2 or request a core task.
E2 was opened later as a separate experiment-local branch after review of the
E1 alignment result.

### Outputs

- [x] `outputs/e1_lgrc9v3_alignment_closeout.json`
- [x] `reports/e1_lgrc9v3_alignment_closeout.md`

### Verification

- [x] Closeout records all commands and artifacts.
- [x] Closeout preserves native-negative / packet-positive distinction.
- [x] No `src/*` diff.

### Run Record

Closeout command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_5_alignment_closeout.py
```

Result:

```json
{"core_task_requested": false, "native_lgrc9v3_execution": false, "selected_outcome": "stop_and_publish_n03_native_grc9v3_negative_packet_positive_lgrc_adapter_compatible", "status": "complete"}
```

Summary:

- E1 closes as an adapter-only alignment record.
- Final selected outcome:
  `stop_and_publish_n03_native_grc9v3_negative_packet_positive_lgrc_adapter_compatible`.
- Summary claims:
  native fixed-topology GRC9V3 proposal flux remains negative for loop
  generation under tested fixtures; the experiment-local packetized mechanism
  is positive for self-rearming packet pulse under controls; the LGRC-style
  event ledger is validated from ledger evidence alone; LGRC9V3 compatibility
  is `adapter_compatible`.
- No E2 branch, core task, or movement-ladders handoff is opened by E1.
- Future question, if pursued separately:
  can native `LGRC9V3.step` or `LGRC9V3.run_event_queue` produce the D2.3
  event ledger through declared runtime primitives?
- Boundary preserved:
  `native_grc9v3_evidence = false`,
  `native_lgrc9v3_execution = false`,
  `adapter_only = true`,
  `movement_claim_allowed = false`.

Postscript after E2/E3:

```text
E1 remains historically correct as the adapter-compatible alignment branch.
E2 later tested existing native runtime execution.
Phase 8 later implemented missing native packet-loop primitives.
E3 later reproduced D2.3 with native LGRC9V3.
```
