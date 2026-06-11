# E1 LGRC9V3 Alignment Plan

## Purpose

E1 follows the N03 D2/D2.1/D2.2/D2.3 packetized branch.

E1 is **experiment-local**. It stays under:

```text
experiments/2026-05-N03-grc9v3-polarized-basin-loops/
```

It does not belong to the global implementation plan unless a later E1 result
explicitly proposes a separate core LGRC9V3 task.

The N03 result is now two-part:

```text
Native fixed-topology GRC9V3 proposal flux:
    negative for polarized loop generation under tested fixtures.

Experiment-local conserved causal packet layer:
    positive for ordered closed-loop propagation;
    positive for state-triggered departure;
    positive for self-rearming packetized pulse cycling under controls.
```

E1 asks whether the positive packetized mechanism can be expressed using
LGRC9V3-native concepts:

```text
event queue
packet departure / arrival
in-flight coherence
causal timing
node proper-time surfaces
packet ledger snapshots
causal observability
```

The goal is alignment, not a new scientific claim and not a core
implementation change.

## Central Question

```text
Can the D2.3 experiment-local packetized pulse mechanism be represented as an
LGRC9V3 event-queue / packet-ledger process without changing its conservation,
causality, control, and claim-boundary semantics?
```

## Claim Boundary

Supported by E1 if successful:

- D2.3 maps cleanly onto LGRC9V3 event/packet surfaces.
- The packetized pulse mechanism is better understood as LGRC-shaped than as
  native synchronous GRC9V3 proposal-flux dynamics.
- Existing D2.3 artifacts can be translated into LGRC9V3-style event ledgers
  and snapshots.

Still blocked:

- native GRC9V3 loop formation;
- non-packetized fixed-topology flux-loop formation;
- movement or locomotion;
- agency, intention, biological behavior;
- multi-pole native claims;
- core `src/*` changes without separate approval.

## Core-Library Stop Rule

E1 may inspect existing `src/pygrc` LGRC9V3 surfaces and may write
experiment-local adapters, validators, and reports.

E1 must not change `src/*` unless explicitly promoted into a separate
core-library task.

If an E1 step requires a new LGRC9V3 runtime primitive, stop and record:

```text
missing primitive
why experiment-local adapter is insufficient
expected public surface
required tests
claim affected
```

## Alignment Targets

| D2.3 concept | LGRC9V3 target concept | Required evidence |
|---|---|---|
| packet id | packet ledger id | unique, stable, serializable |
| packet amount | in-flight coherence amount | budget inclusion |
| packet departure | departure event | source, channel, amount, event-time key |
| packet arrival | arrival event | target, channel, amount, event-time key |
| returned packet re-arms source | state-triggered departure eligibility | trigger evidence after arrival |
| trigger threshold | causal mode / runtime policy parameter | serialized threshold |
| ordered channel sequence | declared causal route | canonical route evidence |
| wrong-direction control | nonmatching causal route | blocked declared-direction claim |
| node-plus-packet budget | LGRC budget invariant | `sum(C_i) + sum(packet_amount)` |
| trigger/rearm/cycle counts | causal event observables | replayable event ledger |
| D2.3 timeseries | LGRC-compatible telemetry surface | event and snapshot artifacts |

## Non-Goals

E1 does not:

- implement a production LGRC9V3 runtime feature;
- rewrite D2.3 into `src/*`;
- add movement coupling;
- promote D2.3 to native GRC9V3 evidence;
- tune thresholds to improve a result;
- replace the N03 conclusion.

## Execution Strategy

E1 proceeds as a translation/alignment track inside the N03 experiment:

1. Inventory current LGRC9V3 packet/event surfaces.
2. Define an experiment-local D2.3-to-LGRC event schema.
3. Convert D2.3 output into LGRC-style ledgers.
4. Validate budget, causality, route, and trigger/rearm evidence from the
   converted ledger alone.
5. Compare converted ledger summaries against original D2.3 summaries.
6. Record whether existing LGRC9V3 surfaces are sufficient or whether E1
   should stop with a proposed separate core implementation task.

## Iteration E1.0. Scope And Surface Inventory

Goal:

```text
Inventory existing LGRC9V3 event, packet, queue, snapshot, and telemetry
surfaces relevant to D2.3 alignment.
```

Outputs:

- `outputs/e1_lgrc9v3_surface_inventory.json`
- `reports/e1_lgrc9v3_surface_inventory.md`

Required questions:

- Does LGRC9V3 already expose packet departure / arrival records?
- Does LGRC9V3 already expose a packet ledger with in-flight amount?
- Does LGRC9V3 serialize event-time key, proper time, and node update timing?
- Does LGRC9V3 distinguish event-time key from node proper time?
- Does LGRC9V3 expose enough state to reconstruct budget:
  `sum(C_i) + sum(packet_amount)`?
- Does LGRC9V3 have a route/causal channel abstraction, or must E1 define an
  experiment-local route manifest?
- Does LGRC9V3 have a native state-trigger surface, or is D2.3's trigger an
  experiment-local policy?

Stop condition:

```text
If the inventory shows no existing packet/event surfaces, E1 becomes an
adapter-only alignment report and must not imply native LGRC9V3 execution.
```

## Iteration E1.1. Event-Ledger Mapping

Goal:

```text
Define the minimal LGRC-style event ledger needed to represent D2.3.
```

Required event kinds:

- `packet_departure`
- `packet_arrival`
- `state_trigger`
- `self_rearm`
- `cycle_complete`
- `control_blocked`

Required event fields:

```json
{
  "event_id": "",
  "event_kind": "",
  "scheduler_event_index": 0,
  "event_time_key": 0.0,
  "node_proper_time": {},
  "source_pole": "",
  "target_pole": "",
  "channel_id": "",
  "packet_id": "",
  "parent_packet_id": "",
  "amount": 0.0,
  "trigger_policy": "",
  "trigger_value": 0.0,
  "trigger_threshold": 0.0,
  "canonical_route_step": 0,
  "declared_route_id": "",
  "control_lane": ""
}
```

Output:

- `configs/e1_lgrc9v3_event_ledger_schema.json`
- schema notes in the report.

## Iteration E1.2. D2.3 Ledger Converter

Goal:

```text
Convert D2.3 JSON/time-series artifacts into the E1 event ledger schema.
```

Inputs:

- `outputs/d2_3_self_rearming_packets.json`
- `outputs/d2_3_self_rearming_packets_timeseries/*.jsonl`

Outputs:

- `outputs/e1_d2_3_lgrc_event_ledgers/*.jsonl`
- `outputs/e1_d2_3_lgrc_event_ledger_summary.json`
- `reports/e1_d2_3_lgrc_event_ledger_summary.md`

Replay requirement:

```text
The ledger converter must not recompute outcomes from hidden state. It should
derive event records from D2.3 artifacts and record any inferred fields.
```

## Iteration E1.3. Ledger-Only Validator

Goal:

```text
Validate D2.3 claims from the converted LGRC-style ledger alone.
```

Checks:

- packet ids unique;
- parent packet ids resolvable;
- no unknown channels;
- departures subtract from node/pole budget surface;
- arrivals add to target surface;
- in-flight budget included;
- completed cycles match canonical route;
- self-rearm events occur only after returned-packet arrivals;
- wrong-direction control remains negative for declared direction;
- forward-only, broken-return, scrambled-order controls remain negative;
- clockwise/counter-clockwise symmetry holds.

Outputs:

- `outputs/e1_ledger_only_validation.json`
- `reports/e1_ledger_only_validation.md`

## Iteration E1.4. LGRC9V3 Compatibility Report

Goal:

```text
Classify D2.3 against existing LGRC9V3 surfaces.
```

Possible outcomes:

| Outcome | Meaning |
|---|---|
| `native_surface_compatible` | Existing LGRC9V3 surfaces can represent D2.3 with no new primitives. |
| `adapter_compatible` | Experiment-local adapter can represent D2.3, but native runtime lacks one or more public surfaces. |
| `missing_runtime_primitive` | D2.3 needs a real LGRC9V3 primitive before native alignment can proceed. |
| `not_lgrc_aligned` | D2.3 relies on semantics outside LGRC9V3's causal packet model. |

Required output:

- list of sufficient existing surfaces;
- list of missing surfaces;
- proposed names for missing surfaces;
- explicit stop/go recommendation for core LGRC9V3 implementation.

## Iteration E1.5. Closeout And Next Branch Decision

Goal:

```text
Close E1 with a decision: adapter-only record, core LGRC9V3 implementation
proposal, or movement-ladder handoff under a packetized-surface claim ceiling.
```

Allowed next branches:

- `E2`: experiment-local LGRC9V3 packet-loop runtime proposal, or a stop-point
  note requesting a separate core task;
- movement-ladders handoff with explicit packetized-surface boundary;
- stop and publish N03 as native-negative / packet-positive mechanism result.

## Evidence Requirements

Every E1 report must state:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true|false
adapter_only = true|false
movement_claim_allowed = false
```

If an E1 artifact uses `native_lgrc9v3_execution = false`, the result is an
alignment or adapter result only, not native LGRC9V3 runtime evidence.

## Final E1 Success Condition

E1 succeeds if it produces a replayable answer to:

```text
Can D2.3 be faithfully represented as LGRC9V3-style causal packet history?
```

It does not need to produce a native runtime implementation to succeed.
