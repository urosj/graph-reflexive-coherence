# Native Causal-Work Admission Pattern Audit

**Date:** 2026-08-16
**Status:** Source audit complete; recurring grammar observed; generic block absent
**Execution:** None
**Runtime change:** None
**Machine record:** [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json)

## Question

The ownership pressure map found no single native bearer of causal work. This
audit therefore asks a narrower source question:

> Do existing LGRC mechanisms already compose direction, funding, eligibility,
> scheduling, commitment, and reception through a reusable native admission
> relation?

This is a source audit, not a mechanism proposal. It does not select an owner,
define a new primitive, authorize a runtime extension, reopen Iteration 97, or
select N32.

## Result

Existing mechanisms repeatedly instantiate an authority chain of the form:

```text
relation or direction
+ local funding or capacity
+ mechanism-specific eligibility
+ producer or caller scheduling
+ runtime commitment
+ target or topology reception
```

That recurring shape is source-supported. A generic native causal-work
admission block is not.

In particular, the current runtime does not expose the requested crossing:

```text
native current J(k -> i)
+ source-local causal availability at k
+ source funding at k
-> native departure eligibility at k
```

Configured flux routes and route-aspect surplus producers can schedule packet
departures, but their route, target, amount policy, pole meaning, reference
mass, and threshold remain configured. They do not derive a general local
eligibility relation from reconstructed current alone.

The audit therefore lands between two of the proposed outcomes:

```text
recurring native admission grammar = observed
existing reusable native composition = not established
generic admission runtime block = absent
missing current-source crossing = confirmed
new generic extension justified = not yet
```

The last line matters. Recurrence is evidence for a useful comparison grammar,
not by itself evidence that one abstraction should replace the specialized
mechanisms.

## Pattern Matrix

| Native mechanism | Direction or proposal | Funding | Eligibility | Scheduler | Committer | Configured residue | Generalization result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Caller-scheduled packet departure | Caller supplies source, target, edge, and amount | Source coherence is checked and debited at departure processing | Endpoint, positive amount, time order, and source-budget checks | Caller | Packet event processing through `step()` | Entire route and amount | Transport contract only; no native reason for departure |
| Packet arrival and local eligibility | In-flight packet fixes target and edge | In-flight amount | Arrival state/order plus caller-supplied eligibility booleans | Prior departure and queue order | `step()` credits target and emits eligibility/local-update records | Local-update and spark eligibility default inputs | Reception is native; downstream eligibility predicate is not a general derived admission rule |
| Configured causal-flux-route producer | Declared `causal_flux_routes` supply source, target, and edge | Aggregate source coherence preflight | Positive configured/derived amount plus route validation and idempotency | Native producer over configured routes | `step()` processes queued departure | Route topology, target, amount source, arrival timing | Reusable scheduling machinery; meaning and relation remain configured |
| Route-aspect surplus producer | Configured route aspect, pole, and first channel hop | Source-node coherence | Observed pole-mass surplus over configured reference and threshold | Native autonomous producer | `step()` processes queued departure | Pole regions, channel, reference mass, threshold, amount | Strongest packet-admission analogue, but policy semantics remain configured and route-specific |
| Spark diagnostics and topology integration | Hybrid spark detector proposes candidate node | Mechanical expansion/budget machinery | Diagnostic thresholds plus explicit LGRC-3 topology-integration and expansion policies | Arrival/local-update path or explicit diagnostic call supplies candidates | Topology integration mutates immediately in its runtime path | Spark lane, evolution thresholds, opt-in topology policies | Distributed detection-to-commit pattern; specialized to spark/refinement, not packet admission |
| Sink-compatibility choice/collapse | Positive outgoing flux is aggregated by reachable sink and ranked | Existing graph state; collapse record carries no generic packet funding | Configured choice backend and epsilon thresholds; prior choice state required for collapse | Rebuild path evaluates deterministically | Choice rebuild mutates registries/basin assignment; LGRC collapse path commits explicit/arbitrated records | Sink set, successor map, thresholds, candidate specifications | Native compatibility scoring exists, but topology route candidates and scores may still be supplied by specs |
| Native route arbitration | Candidate scores propose a selected topology route | Candidate budget prediction must close | Committed source surface, visible inputs, ordering, budget validity, and tie policy | Explicit arbitration API | Explicit commit validates digest freshness then runs collapse/reabsorption | Candidate construction, score components, tie policy, topology intent | Reusable arbitration and stale guards; not a general source-current departure gate |
| Boundary-birth producer | Native outward-flux pressure at eligible parent port | Parent coherence, debited by accepted birth | Opt-in policy, inactive/front-capacity port, positive pressure, probability/RNG, queue/idempotency guards | Native boundary-birth producer | `step()` consumes trial; birth application mutates topology and parent/child coherence | Birth rate, parent-eligibility policy, seed fraction, bond/delay policy | Most complete distributed admission chain, but specialized to topology birth |
| Time, replay, and stale guards | No direction of their own | No funding of their own | Event-time order, proper-time surfaces, idempotency, committed lineage, digest freshness | Existing scheduler | Existing mechanism-specific committer | Guard policy and recorded lineage | Cross-cutting admission constraints, not an action-selection primitive |

## What Is Common

The following roles recur across more than one mechanism:

1. A relation or candidate proposes what may happen.
2. A local budget or capacity bounds what can be committed.
3. An eligibility surface rejects inadmissible work before mutation.
4. A producer, caller, or evaluation path materializes a queued or committed
   record.
5. A runtime-owned transition performs the debit, credit, or topology change.
6. Time, lineage, budget, idempotency, and stale-record checks preserve causal
   order and replay integrity.

This is a **distributed admission grammar** in the descriptive sense.

## What Is Not Common

The load-bearing eligibility predicate is not shared:

- packet departure accepts an externally supplied route and amount;
- route surplus consumes configured pole and channel semantics;
- spark integration consumes detector thresholds and topology policy;
- sink compatibility consumes sink sets, successor relations, and epsilon
  thresholds;
- route arbitration consumes candidate specs and score components;
- boundary birth consumes front capacity, outward pressure, and stochastic
  birth policy.

These cannot be collapsed into one native rule merely because all include a
check before mutation.

## Current-Source Crossing

The C1 fixture specifically needs an admission relation at a native current
source. Existing code supplies the surrounding pieces:

```text
GRC9V3:
  coherence + conductance + potential -> oriented edge current

LGRC9V3:
  scheduled source departure -> source debit -> in-flight packet -> target credit
```

No inspected native surface turns an arbitrary reconstructed current source
into a locally eligible packet source without a configured route, pole policy,
candidate specification, or other mechanism-specific producer condition.

This preserves the C1 closeout. It also explains why choosing the source node
as the owner would have been premature: source funding is native, but the
source-local causal availability relation is absent.

## Decision Boundary

A later generic admission contract should be considered only if a concrete
consumer can show that at least two mechanisms need the same load-bearing
relation without erasing their distinct eligibility semantics. Such a contract
would have to distinguish:

```text
orientation evidence
funding evidence
eligibility evidence
scheduling record
commit record
reception record
configured residue
```

This audit does not establish that threshold. The most faithful next state is:

```text
ownership model = unselected
distributed native authority = source-supported
distributed admission grammar = observed descriptively
generic causal-work admission = absent and unselected
current-source local eligibility = absent
Phase 8 implementation = closed
Iteration 97 = closed
RCAE L04 return = unopened
N32 = unselected
```

## Claim Boundary

This audit does not support:

- a causal-work owner;
- native autonomous action;
- a generic causal-work admission primitive;
- event-locus, source-node, edge, route, field, or queue agency;
- Read-Back closure;
- support recruitment, shared-medium coordination, or ecology;
- Iteration 97, an RCAE return, or N32.

Its positive claim is limited to a source-backed architectural finding:

> LGRC contains several specialized native mechanisms in which causal work is
> admitted through distributed authorities. Their shared shape is auditable,
> but their load-bearing eligibility relations remain mechanism-specific, and
> no generic native current-source admission block presently exists.
