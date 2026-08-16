# GRC/LGRC Causal Pathway Contracts

**Status:** Draft registry seed pending Phase 8 Iteration 106 freeze

**Machine registry:** [`grc-lgrc-causal-pathway-contracts.json`](./grc-lgrc-causal-pathway-contracts.json)
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

The current machine file is an Iteration 105 seed, not the frozen Iteration 106
schema. Its single `status_class`, pathway-level authority summary, embedded
test pointers, and embedded composition hints are provisional structures that
Iteration 106 must decompose rather than preserve by inertia.

## Contract Coordinates

Every pathway entry records:

- identity and purpose;
- substrate layer and status class;
- consumed and produced state;
- temporal and spatial scope;
- direction, funding, eligibility, scheduling, commitment, and reception
  authorities;
- configured residue;
- restoration/serialization identity;
- supported and blocked claims;
- source, specification, tests, and evidence;
- lawful and unlawful composition boundaries.

The six authority fields are diagnostic coordinates:

```text
direction | funding | eligibility | scheduling | commitment | reception
```

Equal field shape does not imply equal semantics or a common implementation.

Iteration 106 must add stage-local contracts where authority changes within a
pathway. Each stage records its trigger, state transform, six authority
coordinates, action and mutation scope, temporal and spatial scope, and
failure/no-op behavior. Pathway-level authority becomes a derived summary.

The frozen schema must also separate:

```text
runtime-visible information from causally consumed information
retained history from constitutively consumed history
configured residue from producer residue and naturalization debt
```

## Provisional Status Classes

The compressed classes below describe the I105 seed only. I106 must replace
them with orthogonal `mechanism_ownership`, `availability`, and `activation`
axes. Evidence status belongs to the crosswalk, while unsupported crossings
and invalid relabels belong to the composition matrix.

### `native_behavior`

The runtime derives and commits the load-bearing relation under its declared
native contract. Configuration may select a documented constitutive mode, but
must not supply the result being claimed.

### `native_mechanics_with_configured_semantics`

The runtime owns transport, validation, accounting, or commitment while the
route, role, threshold, score, or semantic relation remains supplied.

### `producer_mediated`

A producer or experiment-owned policy supplies a load-bearing eligibility or
composition relation. Runtime mechanics consumed by the producer remain
native, but the composed phenomenon does not become native.

### `diagnostic_only`

The pathway derives a readout or reconstruction without being part of ordinary
runtime causal execution.

### `restoration_or_replay_utility`

The pathway defines state identity, restoration, replay, or equivalence
boundaries. It does not choose work merely because it preserves work records.

### `experimental_composition`

An experiment joins pathways under an explicit adapter and bounded claim.

### `unsupported_crossing`

The requested relation has no admitted pathway. Similar source pieces must not
be assembled and relabelled as existing native behavior.

This label is retained only to interpret the seed. It is not an allowed frozen
pathway status because it describes a composition failure, not a pathway.

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

## Initial Registry Seed

Iteration 105 admitted twelve source-backed families for schema work:

| Pathway ID | Bounded meaning | Status class |
| --- | --- | --- |
| `grc9v3.synchronous_transport` | Differential/transport reconstruction and synchronous continuity | `native_behavior` |
| `grc9v3.sink_compatibility_choice` | Current-derived sink compatibility and collapse/basin assignment | `native_behavior` |
| `lgrc9v3.explicit_packet_transport` | Explicit departure, debit, in-flight packet, arrival, and credit | `native_mechanics_with_configured_semantics` |
| `lgrc9v3.configured_flux_route` | Producer traversal of configured packet routes | `native_mechanics_with_configured_semantics` |
| `lgrc9v3.route_aspect_surplus` | Configured pole/channel surplus to packet scheduling | `native_mechanics_with_configured_semantics` |
| `lgrc9v3.producer_feedback_eligibility` | Producer-owned eligibility to scheduled work | `producer_mediated` |
| `lgrc9v3.native_route_arbitration` | Native validation and selection over supplied candidates/scores | `native_mechanics_with_configured_semantics` |
| `lgrc9v3.boundary_birth` | Flux-conditioned default-off topology birth | `native_behavior` |
| `lgrc9v3.spark_topology_integration` | Spark diagnostic candidates to default-off mechanical refinement | `native_behavior` |
| `lgrc9v3.collapse_reabsorption` | Explicit or arbitrated collapse/reabsorption and lineage transport | `native_mechanics_with_configured_semantics` |
| `lgrc9v3.diagnostic_grc_reconstruction` | Explicit synchronous GRC reconstruction over LGRC state | `diagnostic_only` |
| `pygrc.restoration_replay_identity` | Snapshot/reset/restoration/replay identity boundaries | `restoration_or_replay_utility` |

These entries remain draft until Iteration 106 freezes exact schema and source
meaning. Later source inspection may split or merge them.

The registry will own intrinsic pathway and stage facts. A separate crosswalk
will own source/specification/test/evidence relations, and the composition
matrix will own inter-pathway relations. The final registry should retain only
stable `evidence_refs`, `composition_refs`, and optional
`catalog_relation_refs`; the selection guide remains derived from those
authorities.

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

## Claim Boundary

The registry can support precise statements about which runtime owns which
part of an existing pathway. It cannot establish a causal-work owner, generic
admission, native route formation, Read-Back, ecological support,
shared-medium coordination, agency, or N32.
