# GRC/LGRC Causal Pathway Contracts

**Status:** Complete through Iteration 111 pressure-consumer validation

**Machine registry:** [`grc-lgrc-causal-pathway-contracts.json`](./grc-lgrc-causal-pathway-contracts.json)
**Evidence crosswalk:** [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](./grc-lgrc-causal-pathway-evidence-crosswalk.json)
**Composition matrix:** [`grc-lgrc-causal-pathway-composition-matrix.json`](./grc-lgrc-causal-pathway-composition-matrix.json)
**Selection guide:** [`grc-lgrc-causal-pathway-selection-guide.json`](./grc-lgrc-causal-pathway-selection-guide.json)
**Conformance policy:** [`grc-lgrc-causal-pathway-conformance.json`](./grc-lgrc-causal-pathway-conformance.json)
**Implementation plan:** [`Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md`](../implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md)

## Purpose

This specification identifies existing GRC/LGRC execution, diagnostic,
producer, and restoration pathways through a common set of analytical fields.
It helps callers choose and compose existing mechanics without assigning
authority that the substrate does not own.

The registry is a map over source contracts. It is not an evidence source, a
dispatcher, a universal runtime API, or a generic causal-work mechanism.

Registry V1 is limited to GRC9V3, LGRC9V3, and directly consumed shared PyGRC
utilities. It is not yet a registry of every GRC, LGRC, or GRCL family.

Iteration 106 audited the complete declared V1 source closure, classified every
surface, and froze 23 pathway contracts containing 52 authority-bearing stages.
The machine registry is authoritative for intrinsic pathway and stage facts.
The separate Iteration 107 crosswalk owns evidence attachment. The Iteration
108 matrix owns representative directional crossing facts and does not upgrade
the intrinsic status of either endpoint. The Iteration 109 guide derives
selection outcomes from those authorities and does not create new facts. The
Iteration 110 policy and checker enforce those separations mechanically and do
not execute any pathway.

## Contract Coordinates

Every pathway entry records:

- identity and purpose;
- substrate layer, contract kind, mechanism ownership, availability, and
  activation;
- consumed and produced state;
- temporal and spatial scope;
- direction, funding, eligibility, scheduling, commitment, and reception
  authorities;
- configured residue;
- restoration/serialization identity;
- supported and blocked claims;
- stable evidence, composition, and catalog relation references;
- verification revision, staleness, and supersession state.

The six authority fields are diagnostic coordinates:

```text
direction | funding | eligibility | scheduling | commitment | reception
```

Equal field shape does not imply equal semantics or a common implementation.

Each stage records its trigger, state transform, six authority coordinates,
action and mutation scope, temporal and spatial scope, and failure/no-op
behavior. Pathway-level authority is a derived summary and is marked `mixed`
as a list of distinct stage authorities. A list with more than one value
records mixed authority across stages.

The frozen schema separates:

```text
runtime-visible information from causally consumed information
retained history from constitutively consumed history
configured residue from producer residue and naturalization debt
```

## Orthogonal Status Axes

`mechanism_ownership` records who supplies the load-bearing relation:

```text
native
native_with_configured_semantics
producer
external_adapter
diagnostic
utility
```

`availability` records whether the implementation surface exists:

```text
installed
experiment_local
bounded_external
historical
absent
```

`activation` records how an installed surface enters execution:

```text
default_on
default_off
explicit_call
externally_orchestrated
```

These axes are independent. An installed pathway can be default-off; a native
mechanical stage can consume configured semantics; and successful producer
execution remains producer-owned. Evidence status belongs to the Iteration 107
crosswalk. Unsupported crossings and invalid relabels belong to the Iteration
108 composition matrix.

## Artifact Authority

The registry owns intrinsic pathway and stage facts. The source manifest owns
the complete V1 source closure and path classification. The crosswalk owns
source/specification/test/evidence relations and test execution status. The
composition matrix owns directional inter-pathway relations. The selection
guide is derived from those authorities and cannot create a pathway fact.

The crosswalk addresses stages by `(pathway_id, stage_id)`. It may attach a
pathway-wide evidence record only when the cited evidence covers every
load-bearing stage. It also owns migration from the twelve I105 family labels
to the frozen I106 pathways and keeps implementation evidence separate from
cross-cutting dependency evidence.

## Composition Status

```text
lawful_native
lawful_with_explicit_adapter
diagnostic_only
producer_mediated
unsupported_missing_crossing
invalid_relabel
```

A composition status never upgrades the status of its input pathways.

## Frozen V1 Registry

Iteration 105 admitted twelve families as an initial census. Source inspection
in Iteration 106 split those families where timing, identity, topology,
producer, surface-lineage, or restoration behavior carried a distinct
load-bearing contract. The frozen registry contains these 23 pathways:

| Pathway ID | Bounded meaning | Mechanism ownership | Activation |
| --- | --- | --- | --- |
| `grc9v3.synchronous_update_cycle` | Differential/transport reconstruction, continuity, invariants, and observable refresh | `native` | `explicit_call` |
| `grc9v3.identity_basin_reconstruction` | Current-derived identity basins, seeds, and effective masses | `native` | `default_on` |
| `grc9v3.sink_compatibility_choice` | Reachable-sink compatibility and bounded choice/collapse state | `native_with_configured_semantics` | `default_on` |
| `grc9v3.hybrid_spark_refinement` | Hessian/gradient spark detection and bounded configured expansion | `native_with_configured_semantics` | `default_on` |
| `grc9v3.legacy_inactive_port_growth` | Legacy outward-flux growth over any inactive port | `native_with_configured_semantics` | `default_off` |
| `grc9v3.front_capacity_growth` | GRCL9V3 front-capacity-constrained growth into child topology | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.causal_history_annotation` | Lapse, delay, distance, cone, and causal-basin annotations | `diagnostic` | `explicit_call` |
| `lgrc9v3.fixed_topology_eligibility` | Bounded semi-causal eligibility over fixed topology | `diagnostic` | `explicit_call` |
| `lgrc9v3.explicit_packet_transport` | Declared packet debit, in-flight state, arrival, and target credit | `native_with_configured_semantics` | `explicit_call` |
| `lgrc9v3.configured_flux_route` | Packet departure over caller-configured causal routes | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.route_aspect_surplus` | Configured pole-mass surplus and bounded route continuation | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.pulse_substrate_coupling_producer` | Experiment-configured pulse contact to packet work | `producer` | `default_off` |
| `lgrc9v3.feedback_eligibility_producer` | Experiment-authored feedback eligibility to packet work | `producer` | `default_off` |
| `lgrc9v3.native_route_arbitration` | Validation and selection over supplied route candidates/scores | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.boundary_birth` | Outward-flux/front-capacity trial and parent-funded topology birth | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.causal_spark_topology_integration` | Arrival-local spark evaluation and optional mechanical refinement | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.collapse_reabsorption` | Collapse/reabsorption plus packet, lineage, surface, and active-state transport | `native_with_configured_semantics` | `explicit_call` |
| `lgrc9v3.proper_time_identity_evaluation` | Proper-time identity-persistence evaluation | `diagnostic` | `explicit_call` |
| `lgrc9v3.proper_time_identity_acceptance` | Policy-gated identity-acceptance event emission | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.causal_pulse_surface_lineage` | Pulse-contact surface emission and topology-event lineage | `native_with_configured_semantics` | `default_off` |
| `lgrc9v3.multi_basin_record_validation` | Child-basin/flow-window records and bounded replay/control validation | `diagnostic` | `default_off` |
| `lgrc9v3.diagnostic_grc_reconstruction` | Explicit GRC reconstruction over an LGRC base-state copy | `diagnostic` | `explicit_call` |
| `pygrc.restoration_replay_identity` | Versioned snapshot, restoration, reset, identity, and replay boundaries | `utility` | `explicit_call` |

All entries are installed in the current source tree. Empty `evidence_refs` and
`composition_refs` are deliberate until Iterations 107 and 108 establish those
separate authorities.

Pathway contracts are not experiment-catalog entries. A pathway explains how
a transition executes and where authority resides. Primitive, building-block,
motif, and regime entries describe evidence-backed capacities that may consume
one or several pathways without upgrading their nativity.

## Key Boundaries

### GRC flux versus LGRC packet work

GRC flux is a synchronous oriented relation reconstructed from graph state.
LGRC packet work is an explicitly scheduled debit/in-flight/credit lifecycle.
No general native adapter currently turns arbitrary GRC flux into packet work.

### Compatibility versus current generation

Sink compatibility consumes oriented outgoing flux and reachable-sink state.
It does not generate the flux it scores.

### Arbitration versus candidate formation

Native route arbitration can validate, order, and select supplied candidate
records. Candidate construction and score formation remain separately
attributed.

### Scheduling versus eligibility

A queued event proves scheduling. It does not prove the native condition that
made work eligible.

### Mutation versus causal authority

`step()` and topology integrators own committed mutation. They do not thereby
own the reason for the transition.

### Diagnostic reconstruction versus execution

Explicit reconstruction helpers can expose GRC surfaces over LGRC state. They
do not prove that ordinary `LGRC9V3.step()` performed the reconstruction or
consumed its result.

### Retention versus constitutive use

Persisted basin assignments, ledger history, or restoration identity establish
retention/equivalence only at their declared scope. A later constitutive effect
requires a separately evidenced read path.

## Promotion Rule

A newly promoted GRC/LGRC mechanism should reuse an existing pathway contract
or update the registry, composition relation, claim boundary, and conformance
evidence before promotion. This is architectural maintenance guidance, not a
requirement to manufacture registry records for exploratory work.

The reusable checker is:

```bash
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_conformance.py
```

It fails closed on stale or substituted authority artifacts, missing current
source/test references, incomplete stage authority, erased producer or adapter
ownership, unsupported crossing promotion, arbitrary ambiguity resolution,
and selection-time claim upgrades. It checks frozen architecture records only;
passing it is not runtime evidence, extension authorization, or ecological
interpretation.

The global negative-control matrix keeps the accepted digest envelope active.
A separate target-only mode activates one named rule and excludes `CF-001` and
all unrelated rules. I110 uses that mode to show that each of `CF-002` through
`CF-020` independently rejects its corresponding defect; `CF-001` has its own
stale accepted-digest control.

### Stale-to-reviewed continuation

`stale_pending_review` is a blocking state, not a permanent dead end and not a
license to replace accepted hashes. A legal continuation follows this order:

```text
detect relevant source or authority-artifact drift
-> mark the affected dependency closure stale_pending_review
-> derive affected stages, pathways, compositions, and selection cases
-> rerun affected I106 classification and source digests
-> rerun affected I107 evidence and claim ceilings
-> rerun affected I108 crossings and controls
-> rerun affected I109 selections and ambiguity handling
-> issue versioned successor artifacts and explicit supersession records
-> update accepted digests prospectively after review
-> run full I110 conformance, global negatives, and rule isolation
-> restore current status only after every affected dependency passes
```

The rerun may be dependency-scoped when current references completely identify
the affected closure. Incomplete or uncertain dependency coverage requires the
broader re-audit. Changes outside the declared dependency closure do not stale
unrelated pathways. A stale record cannot authorize its own re-admission.

## Claim Boundary

The registry can support precise statements about which runtime owns which
part of an existing pathway. It cannot establish a causal-work owner, generic
admission, native route formation, Read-Back, ecological support,
shared-medium coordination, agency, or N32.
