# Phase 7 Implementation Plan

This document is the execution plan for **Phase 7: `GRC9V3` Hybrid**.

It turns the Phase 7 summary in
[`ImplementationPhases.md`](./ImplementationPhases.md), the completed `GRC9`
record, the completed `GRCV3` record, and the hybrid contract in
[`../specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md) into an explicit
implementation track.

Required kickoff companion documents:

- [`Phase-7-ImplementationChecklist.md`](./Phase-7-ImplementationChecklist.md)
- [`Phase-7-EquationMap.md`](./Phase-7-EquationMap.md)
- [`Phase-7-StepLoop.md`](./Phase-7-StepLoop.md)

Required mid-phase review artifact:

- `Phase-7-MidGate-Review.md`

## Purpose

Phase 7 exists to implement `GRC9V3` as the real hybrid family:

- the substrate is `GRC9`,
- the semantic lift is `GRCV3`,
- and the hybrid behavior is not reducible to metadata copied onto either
  parent.

The implementation must keep three ownership layers separate:

| Layer | Owns |
|---|---|
| `GRC9` mechanics | ordered nine ports, row/column chart, port occupancy, mechanical expansion, column-preserving reassignment, inactive-port growth, column coarse-graining |
| `GRCV3` semantics | basin attributes, signed Hessian convention, hierarchy, choice/collapse/learning events, quadrature budget interpretation |
| `GRC9V3` hybrid | row-basis differential summaries, saturation plus signed-Hessian spark semantics, post-expansion child-basin stabilization, hierarchy-aware mechanical refinement, port-chart semantic observables |

The purpose is not to reopen `GRC9` or `GRCV3`. The purpose is to define the
first executable hybrid family on top of both completed parents.

## Inputs

Authoritative inputs:

- [`../specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`../specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)
- [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
- [`../papers/2026-02-GRC-V3.md`](../papers/2026-02-GRC-V3.md)
- [`Phase-6-EquationMap.md`](./Phase-6-EquationMap.md)
- [`Phase-6-StepLoop.md`](./Phase-6-StepLoop.md)
- [`Phase-5-StepLoop.md`](./Phase-5-StepLoop.md)
- [`GRC9-Retrospective.md`](./GRC9-Retrospective.md)
- [`GRCL-9-Handoff.md`](./GRCL-9-Handoff.md)

Current code state:

- Historical starting point: `src/pygrc/models/grc_9_v3.py` was a
  non-executable family stub.
- Current status: Phase 7 replaced the stub with a typed and executable family
  surface, and the post-core telemetry, visualization, phenomenology, and
  GRCL-9V3 source/lowering tracks are now closed through
  [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

## In Scope

- `GRC9V3State` and `GRC9V3NodeState`
- GRC9 port graph plus GRCV3 basin attributes
- row-basis gradient summaries
- row-basis signed Hessian summaries
- explicit Hessian backend selection, with `row_basis_diagonal` as the Eq. G3
  baseline and `weighted_least_squares` as a comparison backend
- hybrid node tensor construction
- scalar base conductance on occupied port-pairs
- selected analytic edge labels
- potential, flux, sinks, basins, and basin seeds
- effective basin mass `M_i` recomputed from current basin membership after
  identity extraction
- spark candidate detection from GRC9 saturation plus GRCV3 degeneracy
- mechanical expansion with post-event child-basin stabilization
- hierarchy updates after successful refinement
- optional choice/collapse/learning event logic required by the spec
- quadrature-style budget `sum_i mu_i C_i`
- deterministic snapshot/save/load support
- core runtime observables sufficient for Phase 7 closeout

## Out Of Scope For Core Phase 7

- Phase T-GRC9V3 telemetry contract
- Phase V-GRC9V3 visualization
- GRC9V3 phenomenology discovery catalogs
- GRCL/source-seed layer for GRC9V3
- observer-local semantics
- complete Lorentzian causal layer
- explicit FRC sigma field
- anisotropic edge transport beyond scalar base conductance
- host embedding frame

These are downstream work after the core runtime closes.

Current status: these downstream tracks have now been implemented and closed as
the post-core Phase 7 completion track. See:

- [Phase-T-GRC9V3-Closeout.md](./Phase-T-GRC9V3-Closeout.md)
- [Phase-V-GRC9V3-ImplementationPlan.md](./Phase-V-GRC9V3-ImplementationPlan.md)
- [GRC9V3-PhenomenologyDiscovery-Checklist.md](./GRC9V3-PhenomenologyDiscovery-Checklist.md)
- [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md)

Correctness note, May 2026: downstream landscape-inference work exposed a core
Phase 7 defect in the GRC9V3 basin-attribute lift. `basin_mass` is part of the
GRCV3 semantic bundle in Appendix G, but the runtime originally preserved or
seeded the field instead of recomputing effective basin mass from current
flux-topology/geometric basin membership. Iteration 9.1 repaired this for new
runtime/checkpoint evidence. Older GRC9V3 results produced before Iteration 9.1
that depend on basin mass, full geometric basin evidence, or child-basin mass
remain incomplete historical evidence unless rerun.

Correctness note, May 2026: the capability profile declares
`column_coarse_graining` as a required `GRC9V3` capability, inherited from
GRC9. The runtime originally implemented coarse-cache invalidation/hygiene but
did not expose the actual `coarse_grain_columns(...)` and
`split_columns(...)` operator surface. Iteration 9.2 repaired this by adding
the GRC9 column coarse-graining/Split operators to `GRC9V3`, with exact
round-trip tests and telemetry evidence for operator-backed warm coarse fields.
GRC9V3 `column_coarse_graining` claims are now operator-backed for supported
port fields.

## Design Constraints

### 1. Hybrid Ownership Must Be Explicit

Every field, helper, and event added in Phase 7 must state its ownership:

- inherited GRC9 mechanical field,
- inherited GRCV3 semantic field,
- or new GRC9V3 hybrid field.

Silent reuse is a risk. Phase 7 should prefer small wrappers or explicit
adapter helpers over ambiguous inheritance when ownership would otherwise be
unclear.

### 2. Spark Completion Is Hybrid

GRC9 spark detection is mechanical. GRCV3 spark completion is semantic.

For GRC9V3:

- candidate eligibility requires local GRC9 saturation,
- candidate validity requires basin-interior and signed-Hessian degeneracy
  evidence,
- completion requires post-expansion gain of at least one stable child basin or
  attractor.

The runtime must not log a completed hybrid spark solely because mechanical
expansion happened.

### 3. Expansion Remains Mechanical But Gains Semantic Consequences

Expansion uses GRC9 module construction and column-preserving reassignment.

After expansion, the hybrid layer must:

- refresh row-basis differential summaries,
- evaluate child-basin stabilization,
- update hierarchy if stabilization passes,
- and expose the distinction between mechanical expansion and completed hybrid
  spark.

### 4. Choice / Collapse Is A Runtime Event Layer

Unlike pure GRC9, GRC9V3 must expose choice/collapse/learning event logic.

Baseline Phase 7 should implement the minimum required event layer:

- sink compatibility scoring,
- choice regime detection,
- collapse when one route becomes dominant,
- learning as persistent post-collapse state change.

If a full scoring backend is not ready in an early iteration, the field should
be capability-gated and explicitly deferred. It must not be faked with source
metadata.

### 5. Hessian Backend Choice Is A First-Class Runtime Choice

The GRC9V3 baseline Hessian is the row-basis diagonal form from Eq. G3. This is
the default because it is intrinsic to the fixed 3x3 port chart.

The runtime should also allow the full weighted least-squares Hessian inherited
from GRCV3 Appendix A.3 as a named comparison backend. This allows Phase 7
representative evidence to show how geometry changes when the richer Hessian is
used, without confusing it with the default GRC9V3 equation.

### 6. Boundary, Causal, Sigma, And Anisotropy Claims Are Capability-Gated

Baseline Phase 7 may use:

- `frame_mode = "fixed_port_chart"`,
- `boundary_mode = "prune"`,
- `edge_label_selection = "all"`,
- `curvature_backend = "none"` by default,
- scalar `base_conductance` on each occupied port-pair.

It must not claim:

- `boundary_barrier`,
- `causal_layer`,
- `multiscale_sigma`,
- or `anisotropic_edges`

unless the corresponding runtime state, serialization, tests, and capability
advertising are implemented.

## Workstreams

### Workstream 1. State, Params, And Capabilities

Deliver:

- `GRC9V3NodeState`
- `GRC9V3State`
- parameter parsing and validation
- capability profile alignment with `grc-9-v3-spec.md`
- snapshot/save/load round trip

Acceptance:

- `GRC9V3` no longer subclasses `BaseFamilyStub`
- state carries port graph, basin attributes, hierarchy, choice/collapse
  registries, coarse cache, and quadrature metadata
- unsupported capabilities are not advertised

### Workstream 2. Row-Basis Differential And Tensor Layer

Deliver:

- row-basis gradient summaries
- signed Hessian row-basis summaries
- run-fixed Hessian sign convention
- hybrid node tensor construction

Acceptance:

- summaries are deterministic and inspectable
- row-basis semantics are tied to the fixed 3x3 port chart
- no host embedding frame is required

### Workstream 3. Transport And Identity

Deliver:

- base conductance update on occupied port-pairs
- selected analytic edge labels
- potential and flux
- sink/basin extraction
- geometric basin seed validation
- effective basin mass derivation from current basin membership

Acceptance:

- GRC9 transport remains port-pair based
- GRCV3 identity seed semantics are visible
- each sink/geometric basin has a current `M_i` value derived from
  `sum_i mu_i C_i`, with unit-measure fallback when no non-unit measures exist
- both identity layers can be inspected separately

Corrective acceptance, added after downstream inference review:

- `rebuild_identity_state()` must update/cache basin masses after
  `detect_flux_topology_identities()` and `validate_geometric_basin_seeds()`
- `GRC9V3NodeState.basin_mass` must not remain a stale carried-forward value
  for representative basin-chart nodes
- checkpoint exporters must expose basin mass so downstream inference can
  distinguish full geometric basin evidence from coherence-mass fallback

### Workstream 4. Spark, Expansion, And Hierarchy

Deliver:

- hybrid spark candidate predicate
- mechanical expansion reuse from GRC9
- post-expansion child-basin stabilization check
- hierarchy update on successful stabilization
- event distinction between expansion and completed hybrid spark

Acceptance:

- mechanical expansion alone is not a completed spark
- hierarchy changes are deterministic and serialized
- candidate/completed event counts are separately testable

### Workstream 5. Choice, Collapse, Learning, Boundary, Budget

Deliver:

- sink compatibility scoring
- choice/collapse/learning event logic
- configured boundary behavior
- quadrature-style budget preservation
- final refresh and observables

Acceptance:

- choice/collapse events are runtime evidence, not source claims
- boundary modes are capability-gated
- budget target uses `sum_i mu_i C_i`

### Workstream 6. Artifact-Backed Core Closeout

Deliver:

- representative runtime lane
- deterministic replay lane
- artifact-backed event rows and run summary
- `Phase-7-Closeout.md`

Acceptance:

- evidence exists beyond unit tests
- parent-layer and hybrid-layer claims remain distinguishable
- Phase T-GRC9V3 can start without reopening core runtime decisions

## Completion Definition

Core Phase 7 is complete when:

- `GRC9V3` is executable and deterministic,
- GRC9 mechanical and GRCV3 semantic layers remain separately inspectable,
- hybrid spark registration differs from pure GRC9 and pure GRCV3 in the
  intended way,
- hierarchy, choice/collapse, and quadrature budget are serialized,
- artifact-backed representative evidence exists,
- and downstream Phase T/V/phenomenology/GRCL-GRC9V3 work can start from a
  stable core runtime.
