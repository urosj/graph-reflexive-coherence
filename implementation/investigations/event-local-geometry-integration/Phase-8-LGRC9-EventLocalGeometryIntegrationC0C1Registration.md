# Phase 8 LGRC9 Event-Local Geometry Integration C0/C1 Registration

**Date:** 2026-08-16
**Iteration:** 96
**Status:** Prospectively registered before claim-bearing execution
**Machine record:** [`Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Registration.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Registration.json)

## Question

Does producer-mediated event-triggered global geometry reconstruction and
directly funded packet transduction create a bounded non-tied order effect
beyond a full-drain composition null, while leaving the external orchestrator
visible as the missing LGRC ownership layer?

## Registered Fixture

The fixed three-node fork begins at coherence `(0.40, 0.35, 0.35)`. Equal
`0.06` packets travel from the left and right nodes to the center. `H12` and
`H21` exchange the non-tied arrival order at event times `1.0` and `3.0`.
`F12` and `F21` place both arrivals at the same `1.0` frontier.

C0 drains both exogenous packets, reconstructs once, converts center-owned
outward current through `p = 0.1 * |J|`, and drains the generated work. C1
performs that producer-owned reconstruction after each completed exogenous
arrival frontier. Equal-time arrivals are batched before one reconstruction.

The mapping must remain directly funded. A proposal is rejected as a whole on
underfunding, stale source state, action outside node 0, wrong direction, or
malformed scale. LGRC `step()` remains the sole packet executor.

## Independent Later Effect

After the queue drains, a fresh GRC reconstruction is made over the final
committed LGRC coherence. Potential, flux, sink set, and choice state form the
later readout. The active proposal current and any route score are not inputs to
this readout, so proposal production cannot prove itself.

## Required Controls

```text
C0 full-drain null
same-frontier scheduler/batching
geometry off
packetization off
stale proposal
scope leak
label only
wrong direction
wrong scale
funding/overdraw
restoration
duplicate replay
mutation leak
basin identity
budget conservation
```

Each claim-bearing arm is executed once. The raw output is create-once. An
independent reconstruction reads JSON only and may not import PyGRC.

## Claim Boundary

A successful result can only justify a separate owner decision about opening a
source-changing Phase 8 tranche. It cannot establish native event-local
geometry integration, implementation evidence, N32, full RC Read-Back,
learning, agency, or ecology.

In this record, `C2` always means **event-local geometry integration C2**. It is
not N31 Candidate C.2.
