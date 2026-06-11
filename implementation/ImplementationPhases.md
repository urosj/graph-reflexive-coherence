# Implementation Phases

This document defines the implementation phases for the full `PyGRC` spec set.

It is the top-level execution plan for:

- core model implementation,
- family-specific implementations,
- embedding and integration layers,
- machine-driver support,
- verification, determinism, and release readiness.

The codebase target remains the usual package layout under `src/`.

Operator-facing reference documentation lives under
[`docs/reference/`](../docs/reference/README.md). Start there for current usage
guides:

- [GRC Runtime](../docs/reference/GRC-Runtime-ReferenceGuide.md)
- [Telemetry](../docs/reference/Telemetry-ReferenceGuide.md)
- [Landscape Language](../docs/reference/LandscapeLanguage-ReferenceGuide.md)
- [Landscape Compiler And Lowering](../docs/reference/LandscapeCompiler-ReferenceGuide.md)
- [Landscape Inference](../docs/reference/LandscapeInference-ReferenceGuide.md)
- [Motion](../docs/reference/Motion-ReferenceGuide.md)
- [GRCL](../docs/reference/GRCL-ReferenceGuide.md)
- [Graph Visualization](../docs/reference/GraphVisualization-ReferenceGuide.md)
- [Catalogs And Evidence](../docs/reference/Catalogs-And-Evidence-ReferenceGuide.md)

## Objectives

The implementation plan must preserve the boundaries established in the specs:

- papers are the semantic source of truth,
- specs are the implementation contract,
- core model params must stay separate from runtime / observer / tooling config,
- family differences must remain explicit,
- deterministic behavior and reproducible snapshots are first-class requirements.

## Global Delivery Principles

1. Implement the common substrate before model families.
2. Use `GRCV2` as the first executable baseline.
3. Add semantic richness only after the baseline graph loop is stable.
4. Treat `GRC9` as a separate substrate, not as `GRCV2` with extra fields.
5. Defer integration and driver layers until the core model/state boundaries are stable.
6. Require deterministic serialization, parameter resolution, and budget checks early.
7. Keep implementation notes, decisions, and checklists in `implementation/`, not in source comments.
8. Use first-party graph backends for authoritative execution; add third-party adapters only later.

Cross-family backend-selection plan: [Common-BackendStrategyPlan.md](./Common-BackendStrategyPlan.md)

PDE-to-discrete parameter bridge: [PDE-ParameterFamilyBridge.md](./PDE-ParameterFamilyBridge.md)

Landscape-to-GRC bridge: [LandscapeToGRCPlan.md](./LandscapeToGRCPlan.md)

Landscape theory-first translation: [GRCL-Landscape-DSL-TranslationGuide.md](./GRCL-Landscape-DSL-TranslationGuide.md)

Landscape neutral seed schema: [LandscapeSeedSchema.md](./LandscapeSeedSchema.md)

Landscape inference / observed-geometry classifier plan:
[LandscapeInference-ImplementationPlan.md](./LandscapeInference-ImplementationPlan.md)

Landscape inference / observed-geometry classifier checklist:
[LandscapeInference-ImplementationChecklist.md](./LandscapeInference-ImplementationChecklist.md)

Landscape inference reference and user guide:
[LandscapeInference-ReferenceGuide.md](../docs/reference/LandscapeInference-ReferenceGuide.md)

Landscape inference status: complete for the first observed-geometry
classifier track. Milestone sessions `S0012`, `S0013`, and `S0014` record
observed `LandscapeSeed` artifacts, dynamic KG exports, valley/path-memory
refinements, and pheromone revival diagnostics.

Motion inference plan:
[Motion-ImplementationPlan.md](./Motion-ImplementationPlan.md)

Motion inference checklist:
[Motion-ImplementationChecklist.md](./Motion-ImplementationChecklist.md)

Motion inference reference and user guide:
[Motion-ReferenceGuide.md](../docs/reference/Motion-ReferenceGuide.md)

Motion inference status: complete for the first observer-level temporal
inference track. Motion is inferred from runtime telemetry, checkpoints, and
inferred landscape primitives. It is not a source-authored outcome and not a
separate runtime family.

`GRCV3`-rich seed extension plan:
[GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)

`GRCV3`-rich seed vocabulary:
[GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)

`GRCV3`-rich lowering architecture decision:
[GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)

`GRCV3`-rich family-native lowering refactor plan:
[GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)

`GRCV3`-rich family-native lowering refactor checklist:
[GRCL-V3-FamilyNativeLoweringRefactorChecklist.md](./GRCL-V3-FamilyNativeLoweringRefactorChecklist.md)

`GRCV3`-rich seed execution checklist:
[GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)

PDE landscape to seed translation: [PDELandscapeToSeedTranslation.md](./PDELandscapeToSeedTranslation.md)

Landscape implementation phase: [Phase-L-ImplementationPlan.md](./Phase-L-ImplementationPlan.md)

Landscape-to-`GRCV2` realization phase: [Phase-L1-ImplementationPlan.md](./Phase-L1-ImplementationPlan.md)

Telemetry and post-processing phase: [Phase-T-ImplementationPlan.md](./Phase-T-ImplementationPlan.md)

Phase T telemetry experiments refactor plan:
[Phase-T-ExperimentsRefactorPlan.md](./Phase-T-ExperimentsRefactorPlan.md)

Phase T telemetry experiments refactor checklist:
[Phase-T-ExperimentsRefactorChecklist.md](./Phase-T-ExperimentsRefactorChecklist.md)

`GRCV2` implementation closeout: [GRCV2-Closeout.md](./GRCV2-Closeout.md)

`GRCV3` semantic/runtime closeout: [GRCV3-Closeout.md](./GRCV3-Closeout.md)

`GRCV3` retrospective: [GRCV3-Retrospective.md](./GRCV3-Retrospective.md)

`GRCV3` landscape-projector follow-on:
[GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md)

`GRCV3` landscape-projector execution checklist:
[Phase-5-LandscapeProjectorChecklist.md](./Phase-5-LandscapeProjectorChecklist.md)

`GRCV3` telemetry closeout: [Phase-T-GRCV3-Closeout.md](./Phase-T-GRCV3-Closeout.md)

Phase 6 entry handoff: [Phase-6-Handoff.md](./Phase-6-Handoff.md)

Phase 6 execution checklist:
[Phase-6-ImplementationChecklist.md](./Phase-6-ImplementationChecklist.md)

Phase 6 equation map:
[Phase-6-EquationMap.md](./Phase-6-EquationMap.md)

Phase 6 step loop:
[Phase-6-StepLoop.md](./Phase-6-StepLoop.md)

Phase 6 mid-gate review:
[Phase-6-MidGate-Review.md](./Phase-6-MidGate-Review.md)

Phase 6 closeout:
[Phase-6-Closeout.md](./Phase-6-Closeout.md)

Phase 6 GRC9 telemetry contract:
[Phase-6-GRC9-TelemetryContract.md](./Phase-6-GRC9-TelemetryContract.md)

Phase 6 GRC9 representative telemetry:
[Phase-6-GRC9-RepresentativeTelemetry.md](./Phase-6-GRC9-RepresentativeTelemetry.md)

`GRC9` retrospective:
[GRC9-Retrospective.md](./GRC9-Retrospective.md)

Phase T GRC9 telemetry implementation:
[Phase-T-GRC9-ImplementationPlan.md](./Phase-T-GRC9-ImplementationPlan.md)

Phase T GRC9 telemetry contract:
[Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md)

Phase T GRC9 closeout:
[Phase-T-GRC9-Closeout.md](./Phase-T-GRC9-Closeout.md)

Phase V GRC9 representative visualization:
[Phase-V-GRC9-RepresentativeVisualization.md](./Phase-V-GRC9-RepresentativeVisualization.md)

GRC9 phenomenology discovery:
[GRC9-PhenomenologyDiscovery-Plan.md](./GRC9-PhenomenologyDiscovery-Plan.md)

GRCL-9 implementation plan:
[GRCL-9-ImplementationPlan.md](./GRCL-9-ImplementationPlan.md)

GRCL-9 handoff:
[GRCL-9-Handoff.md](./GRCL-9-Handoff.md)

Phase 7 implementation plan:
[Phase-7-ImplementationPlan.md](./Phase-7-ImplementationPlan.md)

Phase 7 execution checklist:
[Phase-7-ImplementationChecklist.md](./Phase-7-ImplementationChecklist.md)

Phase 7 equation map:
[Phase-7-EquationMap.md](./Phase-7-EquationMap.md)

Phase 7 step loop:
[Phase-7-StepLoop.md](./Phase-7-StepLoop.md)

Phase 7 representative runtime evidence:
[Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)

Phase 7 closeout:
[Phase-7-Closeout.md](./Phase-7-Closeout.md)

Phase 8 LGRC-9 implementation plan:
[Phase-8-LGRC9-ImplementationPlan.md](./Phase-8-LGRC9-ImplementationPlan.md)

Phase 8 LGRC-9 implementation checklist:
[Phase-8-LGRC9-ImplementationChecklist.md](./Phase-8-LGRC9-ImplementationChecklist.md)

Phase 8 LGRC-9 handoff:
[Phase-8-LGRC9-Handoff.md](./Phase-8-LGRC9-Handoff.md)

Phase 8 LGRC9 closeout:
[Phase-8-LGRC9-Closeout.md](./Phase-8-LGRC9-Closeout.md)

Phase 8 LGRC9 native packet-loop continuation plan:
[Phase-8-LGRC9-NativePacketLoopPlan.md](./Phase-8-LGRC9-NativePacketLoopPlan.md)

Phase 8 LGRC9 native packet-loop continuation checklist:
[Phase-8-LGRC9-NativePacketLoopChecklist.md](./Phase-8-LGRC9-NativePacketLoopChecklist.md)

Phase 8 LGRC9 causal pulse-substrate surface plan:
[Phase-8-LGRC9-CausalPulseSubstratePlan.md](./Phase-8-LGRC9-CausalPulseSubstratePlan.md)

Phase 8 LGRC9 causal pulse-substrate surface checklist:
[Phase-8-LGRC9-CausalPulseSubstrateChecklist.md](./Phase-8-LGRC9-CausalPulseSubstrateChecklist.md)

Phase 8 LGRC9 causal pulse-substrate surface closeout:
[Phase-8-LGRC9-CausalPulseSubstrateCloseout.md](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)

Phase 8 LGRC9 causal pulse-substrate surface-lineage closeout:
[Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md)

Phase 8 LGRC9 topology-state reabsorption closeout:
[Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)

Phase 8 LGRC9 time-scoped lineage replay closeout:
[Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)

Phase 8 LGRC9 native route-arbitration closeout:
[Phase-8-LGRC9-NativeRouteArbitrationCloseout.md](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md)

LGRC9V3 executable target specification:
[lgrc-9-v3-spec.md](../specs/lgrc-9-v3-spec.md)

GRC9V3 Hessian / hybrid spark readiness plan:
[GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)

GRC9V3 Hessian / hybrid spark readiness checklist:
[GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)

Phase T-GRC9V3 implementation plan:
[Phase-T-GRC9V3-ImplementationPlan.md](./Phase-T-GRC9V3-ImplementationPlan.md)

Phase T-GRC9V3 implementation checklist:
[Phase-T-GRC9V3-ImplementationChecklist.md](./Phase-T-GRC9V3-ImplementationChecklist.md)

Phase T-GRC9V3 telemetry contract:
[Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)

Phase T-GRC9V3 representative telemetry:
[Phase-T-GRC9V3-RepresentativeTelemetry.md](./Phase-T-GRC9V3-RepresentativeTelemetry.md)

Phase T-GRC9V3 closeout:
[Phase-T-GRC9V3-Closeout.md](./Phase-T-GRC9V3-Closeout.md)

Phase V shared visualization plan, including the GRC9V3 workstream:
[Phase-V-ImplementationPlan.md](./Phase-V-ImplementationPlan.md)

Phase V shared visualization checklist, including the GRC9V3 workstream:
[Phase-V-ImplementationChecklist.md](./Phase-V-ImplementationChecklist.md)

GRCL-9V3 vocabulary:
[GRCL-9V3-Vocabulary.md](./GRCL-9V3-Vocabulary.md)

GRCL-9V3 implementation plan:
[GRCL-9V3-ImplementationPlan.md](./GRCL-9V3-ImplementationPlan.md)

GRCL-9V3 implementation checklist:
[GRCL-9V3-ImplementationChecklist.md](./GRCL-9V3-ImplementationChecklist.md)

GRCL-9V3 handoff:
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md)

Cross-family pressure-boundary extension:
[PressureBoundary-ImplementationPlan.md](./PressureBoundary-ImplementationPlan.md)

Cross-family pressure-boundary checklist:
[PressureBoundary-ImplementationChecklist.md](./PressureBoundary-ImplementationChecklist.md)

Pressure-boundary status: closed through Iteration 7, with Iteration 8
exploratory complex-source comparison recorded. Accepted evidence is
restricted to corrected front-capacity or opt-in active-frontier runs with
pressure-boundary provenance; legacy broad-growth artifacts remain historical
controls only.

## Target Package Shape

The intended package shape remains:

```text
src/pygrc/
  __init__.py
  core/
    interfaces.py
    params.py
    types.py
    events.py
    graph.py
    serialization.py
    observables.py
    budget.py
  landscapes/
    seed.py
    validation.py
    io.py
    pde_translation.py
  telemetry/
    recorder.py
    schema.py
    io.py
    reports.py
    compare.py
  models/
    grc_v2.py
    grc_v2_landscape.py
    grc_v3.py
    grc_9.py
    grc_9_v3.py
  integrations/
    host/
    ide_v0/
    ril_v0/
  utils/
```

The exact filenames may vary, but the phase plan assumes a similar separation.

## Phase Overview

| Phase | Name | Primary Output |
| --- | --- | --- |
| 0 | Repository Bootstrap | `src/` layout, package skeleton, implementation conventions |
| 1 | Common Contracts | `GRCModel`, params, state, events, capability model |
| 2 | Core Graph + Storage | deterministic graph/storage substrate |
| 3 | Serialization + Determinism Base | snapshots, canonical params, hashes |
| 4 | `GRCV2` Baseline | first complete executable model |
| L | Landscape Bridge | normalized seed layer, validation, PDE-to-seed translation |
| L1 | Landscape To `GRCV2` Realization | executable seed projector, parameter-family presets, trajectory runner |
| T | Telemetry + Post-Processing | structured run telemetry, summaries, reports, experiment artifacts |
| V | Visualization Surfaces | plots, overlays, topology views, experiment-facing visuals |
| 5 | `GRCV3` Semantic Lift | basin attributes, differential summaries, hierarchy |
| 6 | `GRC9` Mechanical Substrate | nine-slot runtime plus telemetry, visuals, and GRCL-9 lowering |
| 7 | `GRC9V3` Hybrid | combined mechanical + semantic model |
| 8 | `LGRC-9` Causal-History Substrate | Lorentzian/event-driven nine-port planning and first runtime levels |

## Applications / IDE Track Overview

The phases below are application, host, IDE, driver, and release-facing tracks.
They are intentionally numbered separately from the core model phases so the
core sequence can continue after Phase 7. In particular, `LGRC-9` can occupy
core Phase 8 without renumbering host/IDE work.

| App Phase | Name | Primary Output |
| --- | --- | --- |
| A1 | Embedding Surface | host embedding helpers and transition rules |
| A2 | Integration Layer | adapter boundary and runtime wrappers |
| A3 | Machine Driver | deterministic inspection, diff, patch, replay |
| A4 | Verification + Robustness | correctness, determinism, invariants, stress tests |
| A5 | Packaging + Examples | docs, examples, release-ready structure |

## Current Family Completion Read

The core phase numbers are now reserved for model/runtime foundations, while
host, IDE, driver, verification, and packaging work lives in the separate
Applications / IDE track below. The current project state should be read with
two full-family completion layers:

1. Phase 5 closed the semantic/runtime `GRCV3` baseline
2. Phase T then closed the minimal behavior-facing `GRCV3` telemetry lane
3. Phase V has now closed the behavior-facing `GRCV3` visualization lane on
   real `cell-1` / `cell-4` artifacts
4. Phase T and Phase V then also closed the representative `GRCV3`
   checkpoint-backed graph telemetry/visualization lane
5. Phase T has now also closed the seed-driven `GRCV3` landscape checkpoint
   telemetry lane on real `cell-1` / `cell-4` artifacts
6. Phase V has now also closed the seed-driven `GRCV3` landscape
   graph-rendering lane on real checkpoint-backed `cell-1` / `cell-4`
   artifacts
7. however, seed-driven `GRCV3` still has one explicit open family-local lane:
   the landscape-projector revision recorded in
   [GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md)
   and
   [Phase-5-LandscapeProjectorChecklist.md](./Phase-5-LandscapeProjectorChecklist.md)
8. Phase 6 (`GRC9`) is now complete not only as a core runtime, but as a
   family implementation with GRC9-specific telemetry, visualization,
   phenomenology discovery, and `GRCL-9` source/lowering closeout

In other words:

- completed `GRCV2` graph work does **not** imply completed `GRCV3` graph work
- representative `GRCV3` graph telemetry and graph visualization are now
  complete
- seed-driven `GRCV3` landscape checkpoint telemetry is now complete
- seed-driven `GRCV3` landscape graph visualization is now also complete
- overall seed-driven `GRCV3` closeout is also still gated by the richer
  family-local landscape projector follow-on
- and, after the neutral/common projector-only lane was honestly falsified, by
  the `GRCL-v3` extension lane defined in
  [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)
- Phase 6 / `GRC9` should now be read as closed across runtime, telemetry,
  visualization, and family-native `GRCL-9` lowering/catalog evidence
- this closure does not add observer semantics, Lorentzian causal semantics,
  GRCV3 hierarchy semantics, or a native GRC9 collapse event

## Phase 0. Repository Bootstrap

### Goal

Create the implementation workspace and baseline project conventions.

Detailed plan: [Phase-0-ImplementationPlan.md](./Phase-0-ImplementationPlan.md)

Execution checklist: [Phase-0-ImplementationChecklist.md](./Phase-0-ImplementationChecklist.md)

### Deliverables

- `src/pygrc/` package skeleton
- test directory skeleton
- initial packaging metadata
- baseline lint / format / test command conventions
- `implementation/` tracker structure for decisions and checklists

### Checklist

- Create `src/pygrc/__init__.py`
- Create `src/pygrc/core/`, `src/pygrc/models/`, `src/pygrc/integrations/`, `src/pygrc/utils/`
- Create `tests/` with family-specific and integration-specific subtrees
- Decide baseline split / expansion distribution rules:
  - `split_distribution_mode = equal`
  - `expansion_distribution_mode = equal`
- Decide curvature backend rollout strategy:
  - default `none`
  - first in-house backend `forman`
  - later advanced backend `ollivier`
- Confirm use of the spec-defined reference differential backend for `induced_local_frame`, gradient, and Hessian
- Define project-local conventions for:
  - deterministic ordering,
  - ID stability,
  - parameter canonicalization,
  - float tolerance policy,
  - snapshot naming/versioning

### Exit Criteria

- Package imports cleanly
- Empty test suite runs
- Directory structure matches the intended implementation boundary

## Phase 1. Common Contracts

### Goal

Implement the common abstractions all families depend on.

Detailed plan: [Phase-1-ImplementationPlan.md](./Phase-1-ImplementationPlan.md)

Execution checklist: [Phase-1-ImplementationChecklist.md](./Phase-1-ImplementationChecklist.md)

### Deliverables

- `GRCModel` base interface
- `GRCParams`, `GRCState`, `StepResult`, `GRCEvent`
- capability enumeration / string constants
- parameter grouping and canonicalization boundary

### Checklist

- Implement immutable params base structure
- Implement resolved-params access
- Implement capability discovery contract
- Implement common event datatypes
- Implement base observable contract
- Encode parameter domains explicitly in code structure

### Exit Criteria

- All family stubs can inherit from common contracts
- Parameter resolution and snapshot schema are defined centrally
- No family-specific logic leaks into the core abstractions

## Phase 2. Core Graph + Storage

### Goal

Implement deterministic graph and storage primitives shared across model families.

Detailed plan: [Phase-2-ImplementationPlan.md](./Phase-2-ImplementationPlan.md)

Execution checklist: [Phase-2-ImplementationChecklist.md](./Phase-2-ImplementationChecklist.md)

### Deliverables

- weighted graph substrate for `GRCV2` / `GRCV3`
- port-graph substrate for `GRC9` / `GRC9V3`
- stable node/edge IDs
- deterministic iteration and serialization order
- backend protocols that allow later adapters without making them authoritative

### Checklist

- Implement abstract graph protocol
- Implement standard weighted graph backend
- Implement port-graph backend with ordered ports
- Keep the execution substrate independent of `networkx`
- Implement edge and port lookup rules
- Implement insertion/removal semantics without unstable ID reuse
- Implement cached derived-field invalidation rules
- Define optional future adapter boundary for:
  - `networkx` interchange / analysis
  - `pyvis` visualization / export

### Exit Criteria

- Graph backends support all required operations from specs
- Snapshot order is deterministic
- Port graph supports exact row/column lookup and rewiring
- No core model step depends on third-party graph or visualization libraries

## Phase 3. Serialization + Determinism Base

### Goal

Make state, params, and hashes reproducible before model complexity increases.

Detailed plan: [Phase-3-ImplementationPlan.md](./Phase-3-ImplementationPlan.md)

Execution checklist: [Phase-3-ImplementationChecklist.md](./Phase-3-ImplementationChecklist.md)

### Deliverables

- canonical snapshot serializer
- param canonicalization and hash support
- state digest support
- deterministic save/load path

### Checklist

- Serialize resolved params separately from raw config
- Implement canonical JSON-safe snapshot form
- Add params hash and snapshot version markers
- Add RNG-state persistence hooks
- Define bounded remainder representation for budget bookkeeping

### Exit Criteria

- Save/load roundtrip is stable
- Identical params produce identical canonical hashes
- Deterministic snapshots are possible before model completion

## Phase 4. `GRCV2` Baseline

### Goal

Implement the first complete graph model end to end.

Detailed plan: [Phase-4-ImplementationPlan.md](./Phase-4-ImplementationPlan.md)

Execution checklist: [Phase-4-ImplementationChecklist.md](./Phase-4-ImplementationChecklist.md)

Design-defense note: [Phase-4-DiscretizationDefense.md](./Phase-4-DiscretizationDefense.md)

Retrospective: [Phase-4-Retrospective.md](./Phase-4-Retrospective.md)

### Deliverables

- `GRCV2` step loop
- sink/basin extraction
- spark proxy detection
- soft split, birth, pruning / boundary behavior
- exact budget enforcement
- analytic edge labels

### Checklist

- Implement node tensor and conductance map
- Implement potential and flux law
- Implement sink-set and basin extraction
- Implement spark proxy backend selection
- Implement soft split progression
- Implement front birth
- Implement boundary mode handling
- Implement selected edge-label computation
- Implement core observables

### Exit Criteria

- `GRCV2` runs from config to stable snapshots
- Budget is preserved exactly or with explicitly bounded remainder
- Deterministic replay works for fixed seed and fixed params

## Phase L. Landscape Bridge

### Goal

Implement the normalized landscape-seed layer that bridges the PDE landscape DSL
into `PyGRC` without collapsing source meaning into one family's internal
representation.

Detailed plan: [Phase-L-ImplementationPlan.md](./Phase-L-ImplementationPlan.md)

Execution checklist: [Phase-L-ImplementationChecklist.md](./Phase-L-ImplementationChecklist.md)

### Deliverables

- runtime seed datatypes and validation support under `src/pygrc/landscapes/`
- load/save support for normalized seed documents
- PDE landscape JSON to normalized seed translation support
- canonical translation fixtures for representative source landscapes
- explicit family-projector boundary for later `GRCV3` / `GRC9` work

### Checklist

- implement the runtime seed model and validation boundary
- decide and document the seed I/O parser strategy
- implement normalized seed load/save support
- implement conservative PDE-to-seed translation
- preserve source-chart hints without treating them as ontological geometry
- preserve provenance, translation notes, and source-side compile metadata
- verify canonical translation targets against `cell-1`, `cell-4`, and `s6`
- define the handoff boundary from neutral seeds to later family projectors

### Exit Criteria

- normalized seeds can be loaded and validated programmatically
- PDE source landscapes can be translated into normalized seeds deterministically
- canonical seed fixtures are testable reference targets rather than prose-only examples
- later family phases can consume one stable landscape bridge instead of rediscovering it

## Phase L1. Landscape To `GRCV2` Realization

### Goal

Turn validated neutral landscape seeds into executable `GRCV2` runs with
documented projection policy and PDE-informed parameter-family selection.

Detailed plan: [Phase-L1-ImplementationPlan.md](./Phase-L1-ImplementationPlan.md)

Execution checklist: [Phase-L1-ImplementationChecklist.md](./Phase-L1-ImplementationChecklist.md)

### Deliverables

- `LandscapeSeed -> GRCV2` realization entry point
- documented mapping policy from neutral primitives into weighted-graph
  initialization
- first executable parameter-family presets derived from the PDE bridge
- trajectory / smoke runner for representative seeds such as `cell-1` and
  `cell-4`
- deterministic verification for seed-driven `GRCV2` runs

### Checklist

- Define the family-specific projector module boundary
- Define primitive-to-topology realization rules for:
  - basin / plateau support units
  - ridge interface constraints
  - valley transport channels
  - junction / saddle routing hints
- Define how constitutive profile and PDE family presets resolve into `GRCV2`
  params
- Implement executable seed-driven `GRCV2` construction
- Implement repeatable multi-step runner support for observables and event traces
- Add end-to-end smokes for `cell-1` and `cell-4`

### Exit Criteria

- A validated seed can be turned into an executable `GRCV2` model without
  manual topology assembly
- Named PDE-informed parameter families can be selected programmatically
- `cell-1` and `cell-4` can be run for `N` steps with deterministic replay
- Projector policy is explicit enough that later `GRCV3` / `GRC9` realization
  work can compare against it rather than rediscover the bridge

## Phase T. Telemetry + Post-Processing

### Goal

Make executable runs experimentally usable through structured telemetry,
deterministic artifacts, and post-processing/report surfaces.

Detailed plan: [Phase-T-ImplementationPlan.md](./Phase-T-ImplementationPlan.md)

Execution checklist: [Phase-T-ImplementationChecklist.md](./Phase-T-ImplementationChecklist.md)

Structural refactor plan:
[Phase-T-ExperimentsRefactorPlan.md](./Phase-T-ExperimentsRefactorPlan.md)

Structural refactor checklist:
[Phase-T-ExperimentsRefactorChecklist.md](./Phase-T-ExperimentsRefactorChecklist.md)

### Deliverables

- runtime telemetry contract for step-level and run-summary data
- deterministic telemetry artifact layout and save/load support
- post-processing surface for summaries, comparisons, and report generation
- representative experiment artifacts for seed-driven `GRCV2` runs
- explicit handoff boundary to later visualization work

### Checklist

- Define telemetry schema and event/observable families
- Define artifact layout for runs, summaries, and comparison outputs
- Implement telemetry recording hooks for executable runs
- Implement post-processing helpers and report builders
- Add experiment-facing checks for `cell-1` and `cell-4`
- Define what telemetry guarantees before visualization begins

### Exit Criteria

- `GRCV2` seed-driven runs can emit deterministic structured telemetry
- post-processing can build summaries/comparisons without scraping ad hoc logs
- representative experiments produce inspectable telemetry/report artifacts
- visualization can consume a stable telemetry boundary instead of raw runtime state

## Phase V. Visualization Surfaces

### Goal

Build experiment-facing visual surfaces on top of the telemetry and report
contracts from Phase T.

Downstream contract: [Phase-V-Handoff.md](./Phase-V-Handoff.md)

Detailed plan: [Phase-V-ImplementationPlan.md](./Phase-V-ImplementationPlan.md)

Execution checklist:
[Phase-V-ImplementationChecklist.md](./Phase-V-ImplementationChecklist.md)

### Deliverables

- trajectory plots
- event timelines
- topology/state overlays
- experiment-panel and report visuals
- family-specific representative visual suites, including the GRC9V3 Appendix E
  cell-division artifact lane

### Checklist

- Reuse telemetry artifacts rather than reaching directly into model internals
- Keep visualization contracts aligned with experiment/report windows/checkpoints
- Make comparison visuals deterministic and reproducible from saved artifacts
- Keep hybrid GRC9V3 mechanical, semantic, and interaction-owned surfaces
  visually distinguishable

### Exit Criteria

- key experiment visuals can be regenerated from saved telemetry/report artifacts
- visualization remains downstream of telemetry rather than becoming the primary evidence source
- family-specific visualization status is explicit:
  - `GRCV2` graph-capable visualization may be complete
  - `GRCV3` behavior-facing visualization may close earlier than later
    `GRCV3` graph-visible work
  - `GRC9` and `GRC9V3` representative visualization lanes are now closed over
    their respective artifact fixtures

## Phase 5. `GRCV3` Semantic Lift

### Goal

Implement basin-attribute semantics and the richer differential summary backend.

Backend-selection architecture note:
[Common-BackendStrategyPlan.md](./Common-BackendStrategyPlan.md)

Phase handoff:
[Phase-5-Handoff.md](./Phase-5-Handoff.md)

Detailed plan:
[Phase-5-ImplementationPlan.md](./Phase-5-ImplementationPlan.md)

Execution checklist:
[Phase-5-ImplementationChecklist.md](./Phase-5-ImplementationChecklist.md)

Equation map:
[Phase-5-EquationMap.md](./Phase-5-EquationMap.md)

### Deliverables

- `BasinAttributes`
- canonical differential backend
- signed Hessian handling
- hierarchy tracking
- choice/collapse registry
- `GRCV3` backend-selection surface aligned with the common strategy plan

### Checklist

- Adopt the common backend-selection architecture before adding `GRCV3`-specific backend branches
- Define `GRCV3` backend categories and names in a way that is consistent with the common strategy plan
- Keep backend formulas family-local even when backend naming and serialization are shared
- Implement canonical `induced_local_frame`
- Implement weighted least-squares gradient backend
- Implement weighted least-squares Hessian backend
- Implement Hessian sign calibration
- Implement basin seed validation
- Implement spark registration via local degeneracy + attractor-count change
- Implement hierarchy updates
- Implement quadrature-budget mode
- Implement choice/collapse event layer

### Exit Criteria

- `GRCV3` exposes both identity layers from the spec
- Differential summaries are reproducible and serialized
- `GRCV3` backend selection is serialized and testable through the common strategy pattern
- Family-specific semantics stay separate from `GRCV2`
- Phase 5 closeout alone does not imply full family closeout:
  - later Phase T behavior-facing telemetry
  - later Phase V behavior-facing visualization
  - and later `GRCV3` graph-telemetry / graph-visualization work as separate
    stages
  - all of those later telemetry/visualization stages are now complete
  - the remaining open `GRCV3` work is family-local landscape/projector
    semantics rather than Phase T/V infrastructure

## Phase 6. `GRC9` Mechanical Substrate

### Goal

Implement and close the nine-slot substrate as an independent mechanical graph
family, including the runtime, telemetry, visualization, phenomenology
discovery, and family-native GRCL-9 source/lowering evidence layers.

### Deliverables

- ordered nine-port node substrate
- row-based tensor computation
- mechanical spark trigger
- deterministic expansion modules
- coarse-graining and Split
- representative artifact-backed telemetry lane
- real-seed structural bridge lane for mechanical validation
- GRC9-specific Phase T telemetry contract and closeout
- GRC9-specific Phase V visualization suite
- GRC9-native phenomenology discovery and reviewed motif handoff
- GRCL-9 source schema, lowering manifest, replay sessions, visualization, and
  reviewed lowered motif catalogs
- accepted diagnostic collapse-adjacent catalog evidence with explicit
  non-claims

### Checklist

- Implement port occupancy model
- Implement row/column conversion helpers
- Implement row-based tensor and conductance update
- Implement mechanical spark trigger
- Implement deterministic expansion
- Implement growth on inactive ports
- Implement coarse-grain / Split API
- Implement analytic edge labels on occupied port-pairs
- Reuse the shared telemetry/report infrastructure rather than rebuilding
  Phase T/V inside Phase 6
- Add one representative eventful artifact lane for mechanical replay evidence
- Add one real-seed structural bridge lane for nontrivial source-input evidence
- Extend GRC9 telemetry through the Phase T-GRC9 contract and closeout
- Extend GRC9 visualization through the Phase V-GRC9 representative and
  graph-checkpoint surfaces
- Discover and review GRC9-native phenomenology before promoting source
  language
- Implement family-native `GRCL-9` source/lowering, replay, visualization, and
  reviewed cataloging
- Preserve diagnostic-only collapse-adjacent language unless a later Phase T
  contract adds true runtime collapse semantics

### Exit Criteria

- `GRC9` runs end to end without any `v3` semantic dependency
- Expansion and rewiring are deterministic
- Coarse-grain / Split is invertible on supported fields
- Artifact-backed validation exists beyond tests alone
- Phase T-GRC9 telemetry is implemented and closed
- Phase V-GRC9 visualization is implemented and closed
- GRC9 phenomenology discovery has a reviewed handoff into GRCL-9
- GRCL-9 Revision 1 has a source schema, lowering path, replayable evidence,
  visualization, and reviewed lowered motif catalogs
- S0024 and S0025 record the strongest final GRCL-9 diagnostic evidence
- Remaining deferred work is stated explicitly: no observer semantics,
  Lorentzian causal layer, GRCV3 hierarchy semantics, or native GRC9 collapse
  event is claimed

## Phase 7. `GRC9V3` Hybrid

### Goal

Combine the `GRC9` substrate with `GRCV3` semantic lift cleanly.

### Deliverables

- hybrid state model
- row-basis differential summaries
- hybrid spark semantics
- hierarchy-aware expansion refinement

### Checklist

- Reuse `GRC9` substrate rather than duplicating it
- Add basin-attribute state to nine-slot nodes
- Add signed Hessian semantics to row basis
- Add post-expansion child-basin stabilization checks
- Add choice/collapse/learning event logic
- Add quadrature budget interpretation

### Exit Criteria

- [x] `GRC9V3` differs behaviorally from both parents in the intended way
- [x] Mechanical and semantic layers remain inspectable separately
- [x] Hybrid snapshots remain deterministic

### Core Closeout

Core Phase 7 is closed by:

- [Phase-7-Closeout.md](./Phase-7-Closeout.md)
- [Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)

The closed scope is the executable `GRC9V3` runtime. The representative
Phase T-GRC9V3 telemetry and Phase V-GRC9V3 visualization slices are now also
closed over the Appendix E artifact lane. GRC9V3 phenomenology discovery,
reviewed motif catalogs, and GRCL/source-seed lowering were completed as the
post-core completion track and are recorded below.

May 2026 readiness note: before running the new GRC9V3 property experiments,
the project records a bounded Hessian / hybrid spark readiness pass in
[GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md).
That pass preserves the current signed-Hessian hybrid spark runtime as the
baseline and treats any direct column-H spark gate as a separate canonical lane,
not as an incidental experiment-support change.

### Post-Phase-7 Completion Track

Phase 7 should follow the same full-family closure pattern that is now proven
for GRC9:

1. implement the core `GRC9V3` runtime first,
2. add a Phase T-GRC9V3 telemetry contract and replay evidence,
3. add Phase V-GRC9V3 visualization over saved telemetry/checkpoints,
4. define basic GRC9V3 phenomenological cases from theory before source claims,
5. build reviewed GRC9V3 motif catalogs from replayed evidence,
6. then define the GRCL/source-seed layer for GRC9V3 and its deterministic
   seed examples.

Current status:

- items 1-3 are complete for the representative Appendix E lane,
- items 4-5 are complete and feed source handoff through:
  - [GRC9V3-PhenomenologyDiscovery-Plan.md](./GRC9V3-PhenomenologyDiscovery-Plan.md)
  - [GRC9V3-PhenomenologyDiscovery-Checklist.md](./GRC9V3-PhenomenologyDiscovery-Checklist.md)
- item 6 is complete through GRCL-9V3 Revision 1:
  - [GRCL-9V3-Vocabulary.md](./GRCL-9V3-Vocabulary.md)
  - [GRCL-9V3-ImplementationPlan.md](./GRCL-9V3-ImplementationPlan.md)
  - [GRCL-9V3-ImplementationChecklist.md](./GRCL-9V3-ImplementationChecklist.md)
  - [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md)

Final GRCL-9V3 source/lowering catalog:

- `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`
- accepted motifs: 28
- strong candidates: 2
- superseded legacy standalone-growth records: 26
- accepted corrected growth/front motifs: 12

The main planning constraint is ownership: every hybrid field or behavior must
state whether it belongs to GRC9 mechanics, GRCV3 semantics, or a genuinely
new GRC9V3 interaction. Phase 7 should not blur those layers merely because
both parent families are now implemented.

## Phase 8. `LGRC-9` Causal-History Substrate

### Goal

Define and implement the first Lorentzian/event-driven nine-port runtime
substrate without turning it into a broad multi-family LGRC program.

Phase 8 should use [papers/2026-05-LGRC-9.md](../papers/2026-05-LGRC-9.md)
as the semantic source. The phase target is the `LGRC-9` family. Hyphenated
names such as `LGRC-9` and `LGRC-V3` name paper/family phases; executable
runtime names omit the hyphen, for example `LGRC9`, `LGRCV3`, and `LGRC9V3`.
The first executable implementation target is `LGRC9V3` annotation/timing
evidence, because `GRC9V3` is the current complete nine-port runtime with basin
and spark evidence. Pure `LGRC9` remains the substrate interpretation; general
`LGRC` or `LGRC-V3` family phases, including executable `LGRCV3`, may be
derived later if implementation tension requires them, but they are not Phase
8 deliverables.

### Scope Boundary

Phase 8 should start with conservative runtime levels:

```text
LGRC-0:
    causal annotation over existing GRC9V3 artifacts, with pure GRC9 substrate
    terms kept explicit where they are used

LGRC-1:
    semi-causal local proper-time eligibility on fixed topology

LGRC-2:
    packetized causal flux on fixed topology

LGRC-2 ledger gate:
    pending-flux ledger compaction before topology changes

LGRC-3:
    topology-changing causal history
```

LGRC-2 and LGRC-3 are later Phase 8 continuation scopes, not part of the
completed LGRC-0/LGRC-1 slice. They require their own decision records,
contracts, tests, and handoffs before code changes.
Pending-flux ledger compaction is a required gate between LGRC-2 and LGRC-3.

After the first executable LGRC9V3 runtime and autonomy surfaces are complete,
the N03 polarized-basin-loop experiment opens a narrower Phase 8 continuation:
native support for state-triggered, self-rearming packet-loop routes. That work
is tracked separately in
[Phase-8-LGRC9-NativePacketLoopPlan.md](./Phase-8-LGRC9-NativePacketLoopPlan.md)
and
[Phase-8-LGRC9-NativePacketLoopChecklist.md](./Phase-8-LGRC9-NativePacketLoopChecklist.md).

The N04 movement-ladders experiment then opens the next narrower Phase 8
continuation: a native causal pulse-substrate surface over committed LGRC9V3
packet events, with policy-gated coupling and feedback producer
specializations. That work is tracked separately in
[Phase-8-LGRC9-CausalPulseSubstratePlan.md](./Phase-8-LGRC9-CausalPulseSubstratePlan.md)
and
[Phase-8-LGRC9-CausalPulseSubstrateChecklist.md](./Phase-8-LGRC9-CausalPulseSubstrateChecklist.md).
It is closed in
[Phase-8-LGRC9-CausalPulseSubstrateCloseout.md](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)
as native surface support. N04 Lane H subsequently uses that native surface and
feedback producer to support a bounded
`native_m6_same_fixture_self_renewal_candidate`; locomotion-like,
adaptive-topology, biological, agency, identity-acceptance, inherited-N03
movement, and unrestricted movement claims remain blocked.

### Deliverables

- LGRC-9 family implementation plan and checklist
- timing/state schema for:
  - scheduler index `kappa`
  - snapshot index `k`
  - event-time key `T_e`
  - node proper time `tau_i`
  - edge delay `tau_ij`
  - lapse policy
- LGRC-0 causal annotation surfaces over the first LGRC9V3 target
- three-distance path surfaces:
  - geometric
  - causal/proper-time
  - functional/coupling
- LGRC-1 local proper-time eligibility prototype on fixed topology
- LGRC-2 packet/event-queue causal flux with in-flight budget accounting
- pending-flux ledger compaction with lineage-retention rules
- LGRC-3 topology-changing causal history over refinement lineage
- reduction/no-regression tests against synchronous GRC behavior under the
  uniform synchronous limit
- N03-driven native packet-loop continuation:
  route-aspect semantics,
  surplus-trigger producer,
  and self-rearm causality evidence

### Checklist

- Create `Phase-8-LGRC9-ImplementationPlan.md`
- Create `Phase-8-LGRC9-ImplementationChecklist.md`
- Record that Phase 8 is the `LGRC-9` family phase, with first executable
  target `LGRC9V3`
- Record that Phase 8 is not a general LGRC family program
- Define the timing schema and event-time key contract
- Define the initial lapse and edge-delay policies from the paper defaults
- Implement or plan LGRC-0 annotation before behavioral update changes
- Keep LGRC-1 explicitly semi-causal unless causal availability buffers exist
- Preserve budget and deterministic replay invariants
- Open LGRC-2 packetized causal flux only with explicit packet/budget contract
- Close pending-flux ledger compaction before topology-changing LGRC-3
- Open LGRC-3 topology-changing causal history only after LGRC-2 packet
  accounting and pending-flux ledger compaction are stable
- Track N03-driven native packet-loop work in the dedicated Phase 8
  continuation plan/checklist rather than in the experiment implementation docs

### Exit Criteria

- The repo has a reviewed LGRC-9 family implementation plan and checklist
- The first executable work, if started, can annotate causal/proper-time
  surfaces on `LGRC9V3` evidence without changing synchronous runtime behavior
- Any LGRC-1 behavior is labeled semi-causal unless causal availability
  buffers exist
- Any LGRC-2 behavior preserves the in-flight packet budget invariant
- Pending-flux ledger compaction preserves budget equivalence and lineage
  evidence
- Any LGRC-3 behavior preserves packet, topology, and lineage audit evidence
- The synchronous-limit reduction is testable
- No existing `GRC9` or `GRC9V3` runtime semantics are silently changed

## Application Phase A1. Embedding Surface

### Goal

Implement the lightweight host embedding path before full IDE/runtime integration.

### Deliverables

- host graph adapter helpers
- mapping bridge helpers
- sync validation helpers
- lightweight inspection utilities

### Checklist

- Implement host-owned mirror helpers
- Implement `host_to_grc()` / `grc_to_host()` conventions
- Implement sync authority metadata support
- Implement budget sync validation helper
- Implement lightweight local inspection helpers

### Exit Criteria

- External host project can adopt `step()` and snapshots without using full driver stack
- Transition-mode drift checks are available

## Application Phase A2. Integration Layer

### Goal

Implement runtime-facing adapters without polluting the core model layer.

### Deliverables

- integration adapter base
- host integration helpers
- initial runtime adapter scaffolding
- optional external graph / visualization adapter scaffolding

### Checklist

- Implement model binding wrapper
- Implement capability translation layer
- Implement observation translation layer
- Implement restricted-view adapter semantics
- Keep runtime params separate from core model params
- If needed, implement `networkx` import/export adapter as non-authoritative
- If needed, implement `pyvis` export adapter as visualization-only

### Exit Criteria

- Adapters wrap models without redefining step semantics
- Observer/runtime policies live outside model params unless explicitly promoted

## Application Phase A3. Machine Driver

### Goal

Implement deterministic inspection and mutation tooling.

### Deliverables

- machine driver protocol implementation
- deterministic state serializer
- patch / diff support
- invariant checks
- local observer views

### Checklist

- Implement state summary and entity inspection
- Implement basin and spark reports
- Implement invariant report
- Implement freeze/thaw
- Implement patch/diff encoding
- Implement local observer view projection

### Exit Criteria

- Driver can inspect implemented families under a common surface
- Deterministic digests and patches are stable

## Application Phase A4. Verification + Robustness

### Goal

Make correctness and determinism explicit, not assumed.

### Deliverables

- unit tests
- property/invariant tests
- determinism tests
- snapshot roundtrip tests
- family comparison baselines

### Checklist

- Test exact/bounded budget handling
- Test deterministic serialization
- Test label availability modes
- Test graph and port invariants
- Test differential backend reproducibility
- Test coarse-grain / Split invertibility
- Test machine-driver roundtrips

### Exit Criteria

- Core invariants pass across implemented families
- Repeat runs with fixed seed produce identical results where required

## Application Phase A5. Packaging + Examples

### Goal

Make the implementation usable outside the development loop.

### Deliverables

- example configs
- example notebooks or scripts
- package metadata cleanup
- implementation-facing docs

### Checklist

- Add minimal examples for implemented families
- Add host embedding example
- Add machine-driver example
- Add package import/export polish
- Add implementation status table

### Exit Criteria

- A new user can instantiate and run each implemented family
- The package layout, examples, and docs match the implemented surfaces

## Dependency Order

The core model/runtime critical path is:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6
8. Phase 7
9. Phase 8

The Applications / IDE track should be read as a separate downstream path:

1. Application Phase A1
2. Application Phase A2
3. Application Phase A3
4. Application Phase A4
5. Application Phase A5

Notes:

- Phase 5 (`GRCV3`) is semantically/runtime-closed, but the overall `GRCV3`
  family closeout also required later Phase T and Phase V work, and those
  telemetry/visualization follow-ons are now complete.
- The completed `GRCV3` follow-ons remain part of the project baseline:
  - Phase T minimal behavior-facing telemetry: complete
  - Phase V behavior-facing visualization on real `cell-1` / `cell-4`
    artifacts: complete
  - Phase T representative and landscape checkpoint telemetry: complete
  - Phase V representative and landscape graph visualization: complete
- The remaining open `GRCV3` work is not telemetry/visualization work; it is
  the family-local landscape/projector and `GRCL-v3` semantic track.
- Phase 6 (`GRC9`) is now fully implemented in the practical family sense:
  core runtime, GRC9-specific telemetry, GRC9-specific visualization,
  phenomenology discovery, and GRCL-9 source/lowering/catalog evidence are all
  complete for Revision 1.
- Post-closeout review identified one semantics migration for Phase 6 growth:
  broad inactive-port birth must be separated from paper-facing front-capacity
  growth. That migration is now complete and recorded in
  [GRC9-GRCL9-GrowthCorrection-Plan.md](./GRC9-GRCL9-GrowthCorrection-Plan.md)
  and
  [GRC9-GRCL9-GrowthCorrection-Checklist.md](./GRC9-GRCL9-GrowthCorrection-Checklist.md),
  with handoff in
  [GRC9-GRCL9-GrowthCorrection-Handoff.md](./GRC9-GRCL9-GrowthCorrection-Handoff.md).
  Historical broad-growth artifacts remain replayable only to reproduce or
  debug the old behavior; they are not evidence for any paper-facing claim.
  Corrected front-capacity reruns and catalogs are now the accepted growth
  evidence (`S0035`, `S0036`, `S0037`).
- The GRC9 closure still preserves its non-claims: no observer semantics,
  Lorentzian causal layer, GRCV3 hierarchy semantics, or native GRC9 collapse
  event is introduced by the completed telemetry/visualization/GRCL-9 layers.
- Phase 8 (`LGRC-9`) should begin as a planning/checklist phase after Phase 7
  closeout and the LGRC-9 paper are stable. Its first executable target should
  be LGRC-0 annotation over `LGRC9V3` evidence, followed only if warranted by
  LGRC-1 fixed-topology eligibility, not full topology-changing LGRC-3.
- Application Phase A1 can begin once at least `GRCV2` snapshots and params are
  stable.
- Application Phase A3 should not begin seriously before Phase 3 and at least
  one full model family are stable.

## Recommended Companion Documents

The following documents should be added later under `implementation/` as work starts:

- `ArchitectureDecisions.md`
- `Phase0-BootstrapChecklist.md`
- `Phase4-GRCV2Checklist.md`
- `Phase5-GRCV3Checklist.md`
- `Phase6-GRC9Checklist.md`
- `Phase7-GRC9V3Checklist.md`
- `Phase-8-LGRC9-ImplementationPlan.md`
- `Phase-8-LGRC9-ImplementationChecklist.md`
- `DeterminismChecklist.md`
- `OpenQuestions.md`

Several of these now exist under their final names, especially the Phase 6 /
GRC9 and GRCL-9 planning, checklist, closeout, and handoff documents linked at
the top of this file. This companion-document list is retained as a historical
template for future phases rather than a claim that those GRC9 documents are
missing.

## Definition of Done

The implementation is complete only when:

- all implemented core model families satisfy the common interface,
- family-specific capability boundaries are enforced,
- params are resolved, canonicalized, and serialized deterministically,
- snapshots, hashes, and save/load paths are stable,
- Applications / IDE track surfaces work against real models where enabled,
- and invariant / determinism tests cover the full family matrix.
