# GRC/LGRC Composition Matrix

**Status:** Draft matrix seed pending Phase 8 Iteration 108
**Pathway registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)

## Purpose

This matrix distinguishes lawful composition from adapter-mediated behavior,
diagnostic use, producer mediation, missing crossings, and invalid relabels.
It does not execute compositions or upgrade input pathway claims.

The table below is an Iteration 105 seed. Iteration 108 must replace its compact
rows with directional, versioned composition records sourced from the frozen
registry and crosswalk. This document does not own intrinsic pathway facts.

## Status Meanings

| Status | Meaning |
| --- | --- |
| `lawful_native` | Existing runtime contracts compose without adding a load-bearing external relation. |
| `lawful_with_explicit_adapter` | Composition is allowed when the adapter and its authority are named. |
| `diagnostic_only` | Composition produces a bounded readout, not ordinary runtime behavior. |
| `producer_mediated` | A producer supplies a load-bearing relation and must remain in the claim. |
| `unsupported_missing_crossing` | Required relation is not admitted by current substrate contracts. |
| `invalid_relabel` | Composition may be mechanically possible, but the proposed claim erases authority or scope. |

## Required Iteration 108 Row Shape

Every frozen composition row should record:

```text
composition_id
from_pathway_id
to_pathway_id
composition_order
state_identity_mapping
temporal_compatibility
spatial_compatibility
budget_or_invariant_compatibility
authority_retained
authority_transferred
adapter_id
adapter_owner
information_lost_or_compressed
shared_carrier_surface
visible_interaction_term
separable_and_combined_controls
transfer_scope
evidence_status
claim_ceiling
blocked_relabels
```

Composition is directional. An admitted `A -> B` row supplies no evidence for
`B -> A`. Missing crossings, hidden producer bridges, incompatible timescales,
budget conflicts, and lossy state mappings must remain explicit.

## Seed Matrix

| Composition ID | Input -> output | Pathways | Status | Required adapter or boundary |
| --- | --- | --- | --- | --- |
| `CMP-01` | GRC state -> flux -> synchronous continuity | `grc9v3.synchronous_transport` | `lawful_native` | Ordinary GRC9V3 constitutive step only. |
| `CMP-02` | Explicit packet -> source debit -> arrival -> target credit | `lgrc9v3.explicit_packet_transport` | `lawful_native` for transport mechanics | Route, amount, and times remain supplied. |
| `CMP-03` | GRC flux -> Gate-B-style packet work | `grc9v3.synchronous_transport` + `lgrc9v3.explicit_packet_transport` | `producer_mediated` | Explicit flux-to-packet adapter owns sign, amount, source, and schedule. |
| `CMP-04` | LGRC event -> explicit diagnostic GRC reconstruction | `lgrc9v3.diagnostic_grc_reconstruction` | `diagnostic_only` | Caller owns reconstruction boundary. |
| `CMP-05` | Diagnostic reconstruction -> ordinary LGRC behavior claim | diagnostic reconstruction + any runtime path | `invalid_relabel` | Ordinary `LGRC9V3.step()` did not necessarily consume the diagnostic. |
| `CMP-06` | Sink compatibility -> packet or route scheduling | `grc9v3.sink_compatibility_choice` + packet/route path | `unsupported_missing_crossing` | Requires explicit admission and scheduling contract. |
| `CMP-07` | Supplied candidate scores -> native route selection -> topology commit | `lgrc9v3.native_route_arbitration` + `lgrc9v3.collapse_reabsorption` | `lawful_native` for arbitration and commit | Candidate and score formation remain external/configured. |
| `CMP-08` | External score formation -> native route formation claim | native route arbitration | `invalid_relabel` | Native arbitration does not naturalize candidate formation. |
| `CMP-09` | Basin assignment -> later GRC transport effect | sink compatibility + synchronous transport | `unsupported_missing_crossing` unless source proves read path | Persistent basin ID is not currently sufficient constitutive mediation. |
| `CMP-10` | Event queue mutation -> causal eligibility claim | explicit packet transport | `invalid_relabel` | Queue/`step()` owns commit order, not the reason work became eligible. |
| `CMP-11` | Configured causal route -> native formed role | configured flux route | `invalid_relabel` | Route semantics remain configured. |
| `CMP-12` | Pole surplus -> configured packet continuation | route-aspect surplus + explicit packet transport | `lawful_native` under configured semantics | Pole, channel, reference, threshold, and amount remain residue. |
| `CMP-13` | Outward flux + front capacity -> boundary birth | boundary birth | `lawful_native` under declared default-off policy | Specialized birth policy; no generic admission inference. |
| `CMP-14` | Boundary-birth admission -> generic current-to-packet admission | boundary birth + packet transport | `invalid_relabel` | Birth eligibility is topology-specific. |
| `CMP-15` | Spark candidate -> enabled mechanical refinement | spark topology integration | `lawful_native` under declared LGRC-3 policies | Diagnostic spark candidate is not identity acceptance. |
| `CMP-16` | Explicit/arbitrated collapse -> lineage and packet transport | collapse/reabsorption + optional arbitration | `lawful_native` for transport/commit mechanics | Event or candidate formation remains separately attributed. |
| `CMP-17` | Derived history functional -> temporary conductance -> later flux | diagnostic/producer history + synchronous transport | `producer_mediated` | History functional and conductance adapter remain producer-owned. |
| `CMP-18` | Ledger history presence -> native Read-Back | packet/history + restoration utility | `unsupported_missing_crossing` | Requires native constitutive read and write paths, not persistence alone. |
| `CMP-19` | Restoration identity equality -> unrestricted behavioral identity | restoration/replay identity | `invalid_relabel` | Identity is versioned and scope-bounded. |
| `CMP-20` | Producer eligibility -> native packet mechanics | producer feedback eligibility + explicit packet transport | `lawful_with_explicit_adapter` | Producer remains load-bearing and cannot be omitted from the claim. |

## Authority Preservation Rule

For every composition, keep separate:

```text
direction authority
funding authority
eligibility authority
scheduling authority
commit authority
reception authority
```

If an experiment controller supplies any load-bearing coordinate, the composed
result is not fully native even when all state mutations use native runtime
mechanics.

## Maintenance Rule

Iteration 108 should use crosswalk evidence references and validate every
pathway reference before freezing this matrix. It should not duplicate source,
specification, test, or evidence facts owned by the crosswalk. New promoted
mechanisms should add or update relevant composition rows when they introduce
a new lawful path or invalidate an old boundary.

## Claim Boundary

The matrix classifies composition contracts. It does not establish ecological
support, coordination, route formation, Read-Back, agency, or N32.
