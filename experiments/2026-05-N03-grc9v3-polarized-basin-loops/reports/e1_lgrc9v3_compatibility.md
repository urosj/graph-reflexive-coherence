# E1.4 LGRC9V3 Compatibility Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/build_e1_4_lgrc9v3_compatibility.py
```

Status: `complete`

Classification: `adapter_compatible`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = false
adapter_only = true
movement_claim_allowed = false
```

## Outcome Matrix

| Outcome | Value |
| --- | --- |
| `native_surface_compatible` | `False` |
| `adapter_compatible` | `True` |
| `missing_runtime_primitive` | `False` |
| `not_lgrc_aligned` | `False` |

## Interpretation

D2.3 is LGRC-aligned and adapter-compatible. The packet mechanism can be represented as LGRC-style causal packet history and validated from that ledger alone. It is not yet native LGRC9V3 runtime execution because pole/channel route semantics, surplus-trigger policy, and self-rearm evidence remain experiment-local adapter surfaces.

## Sufficient Existing Surfaces

- `LGRC9V3PacketRecord`
- `LGRC9V3PacketQueueEventRecord`
- `LGRC9V3PacketLedger`
- `LGRC9V3RuntimeState`
- `schedule_lgrc9v3_packet_departure`
- `process_lgrc9v3_packet_departure`
- `process_lgrc9v3_packet_arrival`
- `process_lgrc9v3_next_packet_event`
- `LGRC9V3.schedule_packet_departure`
- `LGRC9V3.step`
- `LGRC9V3.run_event_queue`
- `LGRC9V3.set_causal_flux_routes`
- `classify_lgrc9v3_step_extension`
- `build_lgrc9v3_graph_checkpoint`

## Missing Or Adapter-Only Surfaces

- `d2_3_pole_channel_route_manifest`: `experiment_local_adapter_required`
  LGRC9V3 supports node/edge causal flux routes, but D2.3 defines poles and ordered channels at experiment level.
- `source_pole_surplus_trigger_policy`: `experiment_local_adapter_required`
  LGRC9V3 does not expose a native trigger of the form source_pole_mass - reference_pole_mass >= threshold.
- `d2_3_self_rearm_event_kind`: `experiment_local_adapter_required`
  LGRC9V3 can represent the packet arrival and next departure, but D2.3's semantic self_rearm label is experiment-level evidence.

## Proposed Surface Names

- `d2_3_pole_channel_route_manifest`
  - experiment: `e1_pole_channel_route_manifest`
  - possible native: `LGRC9V3CausalRouteManifest`
  - reason: D2.3 route semantics are pole/channel-level. Existing LGRC9V3 routes are node/edge packet routes.
- `source_pole_surplus_trigger_policy`
  - experiment: `e1_source_pole_surplus_trigger_policy`
  - possible native: `LGRC9V3StateTriggerPolicy`
  - reason: D2.3 uses a measured pole surplus threshold to authorize packet departure. Existing LGRC9V3 has packet producers, but not this named trigger.
- `d2_3_self_rearm_event_kind`
  - experiment: `e1_self_rearm_evidence`
  - possible native: `LGRC9V3SelfRearmEvidence`
  - reason: The runtime can represent arrival and later departure. The semantic label that returned coherence recreated the trigger is experiment-level evidence.

## Core Task Recommendation

Request core task now: `False`

E1 can complete as an adapter-only alignment record. A core LGRC9V3 task should only be requested if a later branch requires native runtime execution of pole/channel route manifests or surplus-trigger packet production.

Future trigger:

Promote only if the next branch asks LGRC9V3.step/run_event_queue to natively produce the D2.3 event ledger rather than validate an experiment-local adapter ledger.

## Ledger Validation Summary

- validated lanes: `12`
- ledger-positive lanes: `D2.3-P-self-rearming-cw, D2.3-R-self-rearming-ccw, D2.3-S-low-threshold, D2.3-N-jittered-delay`
- direction symmetry passed: `True`
