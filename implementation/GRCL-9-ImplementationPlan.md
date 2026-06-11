# GRCL-9 Implementation Plan

## Purpose

This document defines the implementation lane for **GRCL-9**, the
GRC9-specific source and lowering surface that turns source-declared mechanical
preconditions into concrete `GRC9State` initial graphs.

The purpose is not to create a higher-level execution semantics for GRC9.
The purpose is narrower:

- define how a source fixture may request GRC9-native mechanical structure,
- lower that structure deterministically into a connected nine-port GRC9 graph,
- preserve source-to-runtime provenance,
- replay the lowered graph through the existing GRC9 runtime and Phase T-GRC9
  telemetry,
- and validate observed outcomes with field-backed selectors.

GRCL-9 source may declare structure and policy. It must not declare solved
runtime outcomes such as spark, expansion, growth, or fission confirmation.

Growth correction note: Revision 1 growth-bearing results that used
`legacy_any_inactive_port` broad parent eligibility are now historical
diagnostics, not paper-facing evidence. Corrected GRCL-9 growth evidence must
use `growth_semantics = "front_capacity"` in source and
`growth_parent_eligibility_mode = "grc9_front_capacity"` in telemetry. The
accepted corrected GRCL-9 growth catalog is `S0036`, and the migration summary
is `S0037`.

## Inputs

This plan is downstream of:

- [GRCL-9-Landscape-ProjectorProposal.md](./GRCL-9-Landscape-ProjectorProposal.md)
- [GRCL-9-Vocabulary.md](./GRCL-9-Vocabulary.md)
- [GRC9-PhenomenologyDiscovery-Plan.md](./GRC9-PhenomenologyDiscovery-Plan.md)
- [GRC9-PhenomenologyDiscovery-Checklist.md](./GRC9-PhenomenologyDiscovery-Checklist.md)
- [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md)
- `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`
- `outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`
- `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0037/growth_correction_supersession_summary.json`

It is also anchored in the current implementation surfaces:

- `src/pygrc/models/grc_9.py`
- `src/pygrc/models/grc_9_state.py`
- `src/pygrc/models/grc_9_ports.py`
- `src/pygrc/models/grc_9_expansion.py`
- `src/pygrc/models/grc_9_landscape.py`
- `src/pygrc/telemetry/grc9_contract.py`
- `src/pygrc/telemetry/_grc9_extensions.py`

## Why This Is The Right Next Step

Phase T-GRC9 made GRC9-specific phenomenology observable. The discovery track
then used that telemetry to identify connected, replayable GRC9-native motifs
that produce or suppress targeted behaviors.

The next question is no longer whether those motifs can be hand-built in GRC9.
They can.

The next question is:

- can a source-facing GRCL-9 declaration request those mechanical
  preconditions without smuggling in the runtime result?
- can that declaration be authored in GRCL landscape vocabulary, rather than
  as direct GRC9 graph literals or ad hoc prose?

That makes the correct next implementation step a family-native lowering
surface, not another discovery fixture generator and not a runtime equation
change.

## Core Boundary

GRCL-9 should be implemented as a typed family extension surface, not as a
replacement for the neutral landscape seed layer.

Allowed:

- top-level `extensions.grcl9`
- primitive-level `extensions.grcl9`
- GRCL-9 source fixture files that retain neutral ancestry where useful
- deterministic lowering into `GRC9State`
- provenance metadata on lowered nodes, edges, and cached quantities
- post-run validation through Phase T-GRC9 telemetry

Forbidden:

- changing GRC9 runtime equations to make GRCL-9 work
- injecting solved events into runtime history
- source fields that claim spark, expansion, growth, or fission occurred
- disconnected fixture graphs
- GRCV3 hierarchy semantics
- Lorentzian causal-layer semantics
- observer-local semantics

## Target Outcome

The first complete GRCL-9 slice should prove:

1. A GRCL-9 source fixture can declare a GRC9-native motif.
2. The source lowers deterministically to a connected GRC9 graph.
3. The lowered graph preserves nine-port capacity, budget, and provenance.
4. Saved telemetry and checkpoints are replayable under `outputs/`.
5. Field-backed selectors reproduce the expected pass/fail distinctions from
   the accepted S0025 motif catalog.
6. Visualizations consume saved telemetry/checkpoints, not source claims.
7. At least one authored example layer starts from GRCL landscape vocabulary
   and compiles into the existing GRCL-9 source schema before lowering.

## GRCL Landscape Example Layer

The Revision 1 source schema is intentionally mechanical because it must lower
unambiguously into GRC9. That schema is not, by itself, the final source-facing
GRCL expression layer. It should be treated as the intermediate family-native
mechanical contract, analogous to the direct-assembly target in the mature
GRCL-V3 path.

Before reviewing a GRCL-9 lowered motif catalog, the implementation track must
add an authored example corpus in GRCL vocabulary. These examples should be
closer to Morse-theoretic landscape descriptions than to direct GRC9 graph
construction:

- critical regions
- local basins
- unstable/stable directions
- separatrices
- saddles and weak bridges
- boundary strata
- gradient/flux pressure
- refinement loci
- post-refinement two-sink regions

The example layer should compile into the existing GRCL-9 source schema:

```text
GRCL landscape example
  -> GRCL-9 source schema constructs
  -> lowered GRC9State
  -> Phase T-GRC9 telemetry
  -> visualization
  -> reviewed catalog
```

It must not compile directly into raw GRC9 graph payloads, and it must not
declare solved runtime outcomes.

The example layer must have its own typed document/version boundary. The
expected first version is:

- `grcl9.landscape_example.v1`

It should include a top-level `grcl9_required` or `lowering_required` guard,
following the GRCL-V3 `rich_required` lesson: if a GRCL-9 example declares
family-specific landscape intent, the compiler/lowerer must consume it or fail
explicitly. It must not silently downgrade to a generic landscape seed or to a
mechanical fixture with erased source meaning.

The authored layer should distinguish three strata:

- **GRCL/Morse source terms**: critical regions, basins, stable/unstable
  directions, separatrices, saddle bridges, boundary strata, gradient pressure,
  refinement loci, post-refinement two-sink regions.
- **GRCL-9 mechanical source constructs**: `spark_candidate_region`,
  `column_proxy_profile`, `instability_profile`,
  `expansion_refinement_region`, `growth_locus`, and
  `post_expansion_fission_geometry`.
- **GRC9 runtime observations**: spark, expansion, growth, fission persistence,
  row/column diagnostics, and event counts.

Iteration 7 should implement the first-to-second mapping. It should not bypass
the GRCL/Morse layer by authoring more mechanical fixtures directly.

Examples of valid source intent language:

- saturated critical region with a near-cancelling columnwise boundary gradient
  along column 2
- critical region whose local unstable manifold has high outgoing cut and weak
  incoming support
- boundary stratum with one inactive port and high outward flux pressure
- post-refinement region with two stable sink candidates separated by a weak
  saddle/bridge

These are source-side GRCL landscape statements. Spark, expansion, growth, and
fission confirmation remain runtime observations validated through telemetry.

Initial compiler mappings should be explicit:

- `critical_region + columnwise_near_cancellation`
  -> `spark_candidate_region + column_proxy_profile`
- `critical_region + unstable_direction + weak_support`
  -> `spark_candidate_region + instability_profile`
- `critical_region + refinement_locus + effective_degree_target`
  -> `spark_candidate_region + expansion_refinement_region`
- `boundary_stratum + inactive_port + outward_gradient_pressure`
  -> `growth_locus`
- `post_refinement_two_sink_region + saddle_bridge`
  -> `post_expansion_fission_geometry`

## Source Constructs For Revision 1

Revision 1 should implement only the constructs needed to reproduce accepted
S0025/S0026 motif families.

### `spark_candidate_region`

Purpose:

- lower a saturated nine-port candidate region with a runtime-aligned spark
  gate intent.

Allowed gate intents:

- `saturation_column_proxy`
- `saturation_instability`
- reserved `saturation_sign_crossing`

Required lowering evidence:

- candidate node id
- occupied port chart
- neighbor/coherence profile
- expected saturated node cache
- source provenance

Telemetry validation:

- `family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count`
- `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`
- event-level `spark_evidence.spark_kind`

### `column_proxy_profile`

Purpose:

- lower a chart profile that targets the runtime column diagnostic:

```text
H_s^(b) = sum_r w(s, p(r,b)) * (C_neighbor(p(r,b)) - C_s)
```

Required lowering evidence:

- target column
- cancellation or imbalance mode
- conductance/coherence placement
- expected column-proxy candidate cache

Telemetry validation:

- `family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count`
- event-level `spark_evidence.column_proxy_gate_pass`

### `instability_profile`

Purpose:

- lower row-tensor and cut/support anisotropy for the instability branch.

Runtime anchors:

```text
T_row = lambda_c * C_s
      + xi_c * sum_row w(s,j) * (C_j - C_s)^2
      + zeta_c * (sum_row flux(s,j))^2

Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)
U = {s} union neighbors(s)
```

Telemetry validation:

- `family_extensions.grc9.final_row_tensor_summary`
- event-level `spark_evidence.instability_score`
- `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`

### `expansion_refinement_region`

Purpose:

- lower a spark-capable parent with expansion policy preserved.

Runtime anchors:

```text
n_req = max(1, ceil((D_eff - 2) / 7))
```

Required lowering evidence:

- `target_effective_degree`
- `module_size_formula`
- `bond_weight_mode`
- `coherence_transfer_mode`
- source `coherence_transfer_ratios` mapped to runtime
  `distribution_weights`
- column-preserving boundary reassignment expectation

Telemetry validation:

- `family_extensions.grc9.lifecycle_event_counts.expansion_count`
- `family_extensions.grc9.expansion_summary.max_module_node_count`
- event-level `expansion_evidence.target_effective_degree`
- event-level `expansion_evidence.coherence_transfer_ratios`

### `growth_locus`

Purpose:

- lower a birth-capable inactive-port region with pressure structure.

Runtime anchor:

```text
p_birth = 1 - exp(-lambda_birth * outward_flux_pressure)
```

Required lowering evidence:

- parent node
- inactive parent port
- pressure-producing neighborhood
- `birth_rule`
- `lambda_birth`

Telemetry validation:

- `family_extensions.grc9.lifecycle_event_counts.growth_count`
- event-level `growth_evidence.outward_flux_pressure`
- event-level `growth_evidence.birth_probability` when emitted
- optional `family_extensions.grc9.growth_summary.birth_probability_max`

### `post_expansion_fission_geometry`

Purpose:

- lower a two-sink post-expansion-like geometry suitable for telemetry
  persistence-window evaluation.

Required lowering evidence:

- two candidate sink basins
- minimum basin mass parameter
- persistence window parameter
- source provenance for module and basin members

Telemetry validation:

- `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count`
- `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps`
- `family_extensions.grc9.identity_abundance.basin_size_max`

Non-claim:

- this does not introduce GRCL-9 fission semantics or GRCV3 hierarchy.

## Concrete Data Carriers

Revision 1 should use explicit carriers for all GRCL-9 lowering metadata.

Source carriers:

- top-level `extensions.grcl9`
- primitive-level `extensions.grcl9`
- source construct ids and construct kinds

Lowered node/edge payload carriers:

- `grcl9_source_construct_id`
- `grcl9_source_construct_kind`
- `grcl9_motif_id`
- `grcl9_motif_role`
- `grcl9_projector_revision`
- `grcl9_edge_kind`
- `grcl9_bridge`
- `grcl9_bridge_role`

Lowered state cached quantities:

- `grcl9_provenance`
- `grcl9_motif_registry`
- `grcl9_assembly_policy`
- `grcl9_expected_saturated_node_ids`
- `grcl9_expected_column_proxy_candidate_ids`
- `grcl9_bridge_edge_ids`

`grcl9_motif_registry` should map motif ids to lowered node ids, edge ids,
source construct ids, and motif roles.

`grcl9_assembly_policy` should record:

- `port_assignment_mode`
- `mass_partition_mode`
- `bridge_edge_policy`
- `module_size_formula`
- `distribution_weight_mode`
- `budget_preservation_policy`

## Code Organization

Expected new implementation surfaces:

```text
src/pygrc/landscapes/extensions/grcl9/
  __init__.py
  schema.py                 # source dataclasses / validation
  manifest.py               # lowering manifest model
  fixtures.py               # built-in minimal source fixtures
  examples.py               # authored GRCL vocabulary examples -> source schema

src/pygrc/models/
  grc_9_grcl9_lowering.py   # GRCL-9 source -> GRC9State assembly
  grc_9_grcl9_provenance.py # provenance/motif registry helpers

src/pygrc/telemetry/
  grcl9_replay.py           # experiment/session wrapper helpers

src/pygrc/visualization/
  grcl9_lowering.py         # saved replay/checkpoint visualization wrappers
```

Expected tests:

```text
tests/landscapes/
  test_grcl9_schema.py
  test_grcl9_manifest.py
  test_grcl9_fixtures.py
  test_grcl9_examples.py

tests/models/
  test_grc_9_grcl9_lowering.py

tests/telemetry/
  test_grcl9_replay.py

tests/visualization/
  test_grcl9_lowering.py
```

The existing neutral projector in `src/pygrc/models/grc_9_landscape.py` should
remain available. GRCL-9 lowering may reuse helper functions where appropriate,
but its contract should be family-native and explicit.

## Artifact And Session Layout

All replayable experiment artifacts should remain under `outputs/`.

GRCL-9 implementation sessions should use:

```text
outputs/grcl9/lowering/sessions/S0001/
outputs/grcl9/lowering/sessions/S0002/
...
```

Each session should contain enough information to replay and inspect the run:

```text
session_manifest.json
source_fixtures/
grcl_landscape_examples/
lowered_states/
telemetry/
reports/
visualizations/
replay.sh
```

The GRCL-9 session log should live at:

```text
outputs/grcl9/lowering/ExperimentalLog.md
```

Session ids are scoped to the GRCL-9 lowering track and should not reuse the
GRC9 phenomenology discovery session directory.

## Iteration Plan

### Iteration 1: Lowering Manifest Contract

Create a document and typed model for the lowering manifest.

The manifest should map S0026 accepted motif requirements to:

- source construct kind
- graph preconditions
- required source knobs
- lowering carriers
- expected telemetry fields
- pass/fail controls
- non-claims

Expected artifacts:

- `implementation/GRCL-9-LoweringManifest.md`
- `src/pygrc/landscapes/extensions/grcl9/manifest.py`
- `tests/landscapes/test_grcl9_manifest.py`

Acceptance:

- every accepted S0026 motif family has a manifest entry
- telemetry paths use Phase T-GRC9 contract field names
- no manifest entry claims a runtime event as source truth

### Iteration 2: Source Schema

Implement Revision 1 source dataclasses and validation.

Expected source constructs:

- `spark_candidate_region`
- `column_proxy_profile`
- `instability_profile`
- `expansion_refinement_region`
- `growth_locus`
- `post_expansion_fission_geometry`

Acceptance:

- valid source fixtures round-trip through JSON/YAML-compatible mappings
- invalid spark intent values are rejected
- nine-port, budget, bridge, and provenance fields are validated before
  lowering
- source schema distinguishes required fields from optional telemetry
  expectations

### Iteration 3: Minimal Source Fixtures

Author source fixtures for the accepted S0026 pass/fail motif families.

Initial fixture set:

- column-proxy spark pass/fail
- instability spark pass/fail
- expansion `D_eff` low/high
- growth `lambda_birth` high/low
- fission min-mass pass/fail

Acceptance:

- fixtures are source-level declarations, not serialized GRC9 runtime states
- each fixture records expected selector ids
- each fixture records explicit non-claims
- each fixture can be loaded without invoking runtime execution
- fission fixtures lower two sink-capable regions with separable conductance
  geometry and do not claim runtime-computed basins

### Iteration 4: Lowerer Revision 1

Implement deterministic source-to-`GRC9State` assembly.

Required behavior:

- connected graph output
- nine-port capacity enforcement
- deterministic port assignment
- deterministic bridge edge creation
- bridge edges use `grcl9_edge_kind = "bridge"`
- budget preservation
- source-to-node and source-to-edge provenance
- cached `grcl9_*` lowering metadata

Acceptance:

- repeated lowering of the same source fixture is byte-stable after
  serialization
- no lowered graph is disconnected
- no lowered node exceeds nine occupied ports
- bridge edges are explicit metadata, not threshold-only inference
- lowered metadata contains motif registry, provenance, assembly policy, and
  expected candidate sets

The lowerer produces a `GRC9State` compatible with the existing GRC9 model
shell; it does not replace `src/pygrc/models/grc_9_landscape.py` or modify
GRC9 runtime equations.

### Iteration 5: Telemetry Replay

Run lowered fixtures through the existing GRC9 runtime and Phase T-GRC9
telemetry.

`src/pygrc/telemetry/grcl9_replay.py` should wrap GRCL-9 source loading,
lowering, and telemetry capture around existing GRC9 landscape/runtime entry
points such as `build_grc9_from_landscape_seed` and
`run_grc9_landscape_seed`.

Acceptance:

- all replay artifacts are written under `outputs/grcl9/lowering/sessions/`
- each run has telemetry, graph checkpoints, reports, source fixture copy, and
  replay command
- selectors validate expected pass/fail distinctions against telemetry fields
- failures are recorded as source/lowering/runtime/selector failures, not
  silently dropped

### Iteration 6: Visualization

Render visualizations for accepted lowered fixtures.

Acceptance:

- visuals consume telemetry and graph checkpoints
- visuals show connected graphs
- bridge edges and motif roles are visible
- labels distinguish source intent from runtime observation
- no visualization is treated as proof without selector evidence

### Iteration 6.1: GRCL-9 Boundary Refactor

Move the implementation to the same source/runtime/package boundaries used by
the existing GRCL-V3 lowering architecture.

Acceptance:

- GRCL-9 source schema, manifest, fixtures, and examples live under
  `src/pygrc/landscapes/extensions/grcl9/`
- GRCL-9 lowering and provenance helpers live under `src/pygrc/models/`
- GRCL-9 replay wrappers live under `src/pygrc/telemetry/`
- GRCL-9 visualization wrappers live under `src/pygrc/visualization/`
- no public long-lived `pygrc.grcl9` package remains
- tests are split by ownership under `tests/landscapes/`, `tests/models/`,
  `tests/telemetry/`, and `tests/visualization/`
- replay scripts use `python -m pygrc.telemetry.grcl9_replay`

### Iteration 7: GRCL-9 Landscape Example Compiler

Author GRCL landscape examples using the vocabulary in
`GRCL-9-Vocabulary.md`, then compile those examples into the existing GRCL-9
source schema. This iteration is not another mechanical fixture pass; it adds
the Morse/phenomenology-facing source layer above `grcl9.source.v1`.

Expected artifacts:

- `src/pygrc/landscapes/extensions/grcl9/examples.py`
- `tests/landscapes/test_grcl9_examples.py`
- saved example copies under
  `outputs/grcl9/lowering/sessions/<S####>/grcl_landscape_examples/`

Initial example families:

- column-proxy critical region
- instability critical region
- expansion/refinement locus
- growth boundary stratum
- post-refinement fission saddle/bridge geometry

Expected typed source terms:

- `GRCL9LandscapeExampleDocument`
- `GRCL9CriticalRegion`
- `GRCL9StableBasin`
- `GRCL9UnstableDirection`
- `GRCL9Separatrix`
- `GRCL9SaddleBridge`
- `GRCL9BoundaryStratum`
- `GRCL9GradientPressure`
- `GRCL9RefinementLocus`
- `GRCL9PostRefinementTwoSinkRegion`

Expected compiler helpers:

- `compile_grcl9_landscape_example_to_source(...)`
- `default_grcl9_landscape_examples()`
- `grcl9_landscape_example_by_name()`

Acceptance:

- examples are authored in GRCL landscape vocabulary, not direct GRC9 graph
  payloads
- examples carry `grcl9.landscape_example.v1`
- examples carry a required lowering guard such as `grcl9_required = true`
- examples compile into existing GRCL-9 source schema constructs
- the compiler records source-term to mechanical-construct provenance
- examples preserve explicit non-claims and selector expectations
- source-invariant tests pass before replay/visualization tests are considered
- examples replay and visualize through the Iteration 5/6 machinery
- no example contains solved GRC9 telemetry, event history, or raw lowered
  graph literals

### Iteration 7.1: Seed-Backed GRCL-9 Examples

Add checked-in `LandscapeSeed` examples with `extensions.grcl9`, matching the
GRCL-V3 rich-seed workflow more closely than generated in-code example
documents. These are the examples we will tune over multiple iterations to
find source-side seeds that reliably emit the GRC9 phenomenology.

Expected artifacts:

- `configs/landscapes/seed/grcl9-*.seed.yaml`
- seed-extension extraction helpers under
  `src/pygrc/landscapes/extensions/grcl9/`
- replay source mode `landscape_seed_examples`
- saved original seed copies under
  `outputs/grcl9/lowering/sessions/<S####>/grcl_landscape_seeds/`

Acceptance:

- seed files carry GRCL/Morse-facing terms only under `extensions.grcl9`
- primitive-level `extensions.grcl9` terms extract to
  `grcl9.landscape_example.v1`
- extracted examples compile to `grcl9.source.v1`
- compiled sources lower to connected GRC9 states
- replay stores the original seed files, extracted example documents, compiled
  source documents, lowered states, telemetry, and selector reports
- this iteration may expose missed lifecycle events; working seeds are expected
  to require follow-up tuning

Non-goals:

- do not encode raw GRC9 node/edge/port topology in the seed examples
- do not claim first-pass seed examples reproduce every direct GRC9
  phenomenology run
- do not change GRC9 runtime equations

### Iteration 7.2: Working GRCL-9 Phenomenology Seeds

Tune the seed-backed examples until they produce the lifecycle signatures they
are meant to demonstrate. This iteration gates catalog work: a reviewed
lowered motif catalog should not select from seed examples that do not emit
their expected GRC9 telemetry.

Expected artifacts:

- revised GRCL-9 seed examples under `configs/landscapes/seed/`
- lowering/compiler repairs that preserve source vocabulary while satisfying
  runtime predicates
- replay session under `outputs/grcl9/lowering/sessions/` where all seed
  selector lanes pass

Acceptance:

- column-proxy spark pass emits spark and expansion
- column-proxy fail emits no spark
- instability pass emits instability spark and expansion
- instability fail emits no instability spark
- expansion low/high both emit spark and expansion, with module-size response
  visible in run-summary telemetry
- growth high emits growth events
- growth low emits no growth events
- fission pass produces confirmed fission run-summary telemetry
- fission fail suppresses confirmed fission telemetry
- visualizations are rendered for the working session

### Iteration 7.3: ComposingCells-Aligned Seed Families

Add a second seed-backed layer whose source shape is closer to
`2026-02-ComposingCells.md` than to isolated GRC9 mechanism probes. These seeds
should still compile through the GRCL-9 landscape example surface and
`grcl9.source.v1`, but their neutral seed primitives should visibly compose
cell-like structures:

- basins and nested basins for identity regions
- ridges/membranes for boundaries
- valleys/channels for transport pressure
- plateaus for local support regions
- saddles/bridges for branch and separatrix geometry

Expected seed families:

- boundary ridge / membrane cell
- internal valley / transport cell
- nested basin / plateau cell
- saddle branch / instability cell
- refinement cell with expansion and budget partition intent

Acceptance:

- seeds use neutral GRCL/Morse primitives, not raw GRC9 graph literals
- each seed carries `extensions.grcl9` with `grcl9_required = true`
- each seed maps a ComposingCells primitive composition to an existing GRCL-9
  mechanical manifest entry
- seeds declare structural preconditions and selector expectations only
- replay stores original seed files, extracted examples, compiled sources,
  lowered states, telemetry, checkpoints, and reports
- selector evidence distinguishes which composed-cell seeds are runtime-active
  and which evidence remains structural-only
- visualizations are rendered from saved telemetry/checkpoints

Non-goals:

- do not introduce new runtime equations
- do not claim full GRCL cell semantics beyond the lowered GRC9 evidence
- do not promote telemetry-only Phase T diagnostics into source claims

### Iteration 8: Reviewed GRCL-9 Lowered Motif Catalog

Promote validated lowered examples into a reviewed GRCL-9 catalog.

Expected artifact:

- `outputs/grcl9/lowering/sessions/<S####>/reviewed_grcl9_lowered_motif_catalog.json`

Acceptance:

- accepted motifs link GRCL landscape example, compiled source fixture, lowered
  state, telemetry, checkpoints, selectors, and visualization
- rejected motifs record rejection reason
- duplicate structural motifs are linked, not silently copied
- catalog explicitly preserves non-claims

### Iteration 8.1: Collapse-Adjacent Structural Seeds

Before closing Revision 1, implement the planned collapse-adjacent structural
seed batch documented in
[`GRCL-9-CollapseAdjacentNextBatch.md`](./GRCL-9-CollapseAdjacentNextBatch.md).

Current status:

- `S0008` catalogs spark, expansion, growth, and identity-fission diagnostic
  evidence.
- Current GRC9 does not emit a `collapse` event kind.
- Phase T-GRC9 explicitly keeps GRCV3 choice/collapse semantics out of the
  current contract.
- Phase V-GRC9 may reuse the transparent-source/arrow/target visual grammar
  only for labeled structural probes; this does not make the run collapse
  evidence.

Expected scope:

- add collapse-adjacent GRCL-9 seeds as structural probes,
- classify them without claiming runtime collapse,
- review which collapse-adjacent fields are observable through existing Phase
  T-GRC9 telemetry and graph checkpoints,
- record whether GRC9-native structural collapse should remain
  `reserved_future` or receive a diagnostic-only telemetry extension.

Candidate source seed families:

- membrane rupture / ridge failure,
- basin merge before fission persistence,
- support-loss identity decay,
- saddle choice pressure without GRCV3 choice semantics.

Acceptance:

- no source fixture declares that collapse occurred,
- no GRCV3 `choice` / `collapse_registry` semantics are imported,
- replay artifacts classify outcomes as structural-only, candidate, observed
  non-fission, or reserved-future,
- `S0009` is treated as structural-probe evidence only unless a runtime
  collapse-like transition is observed in saved telemetry,
- the Phase T and Phase V review notes are updated before any implementation
  beyond structural seeds proceeds.

### Iteration 8.2: Collapse-Producing Seed Discovery

Iteration 8.1 proved that GRCL-9 can author collapse-adjacent structure, but
`S0009` does not show a runtime collapse. Before closing the collapse lane or
adding telemetry, run a targeted seed-discovery pass whose purpose is to find
GRCL/Morse examples that actually produce collapse-like runtime transitions in
GRC9 telemetry.

Scope:

- author additional GRCL landscape seeds that intensify the 8.1 mechanisms,
- vary basin mass, support conductance, bridge conductance, outward pressure,
  and persistence thresholds in controlled pass/fail families,
- replay them under GRC9 with graph checkpoints and selector reports,
- record every attempt as a reproducible session under `outputs/grcl9/lowering`,
- decide from observed telemetry whether collapse remains structural-only or
  has a stable GRC9-native diagnostic surface.

Candidate mechanisms:

- fission candidate that loses one sink basin before the persistence window,
- basin merge caused by weak saddle/bridge geometry and asymmetric support,
- support-loss identity decay with low conductance support and mass drain,
- membrane/ridge rupture that converts a saturated region into expansion or
  sink loss,
- saddle-pressure examples that choose one branch and extinguish the other
  without importing GRCV3 choice semantics.

Acceptance:

- at least one new replay session after `S0009` records the attempted
  collapse-producing seeds,
- each lane is classified as `runtime_collapse_like_observed`,
  `structural_only`, `ambiguous`, or `failed_control`,
- any positive claim is backed by event rows, run-summary fields, graph
  checkpoints, and visualization,
- if no positive examples are found, the handoff explicitly records collapse
  as not yet produced by GRCL-9 seeds.

Current outcome:

- implemented as `S0011`,
- `cell_basin_merge_runtime_collapse_probe` produces
  `runtime_collapse_like_observed` by losing source-declared sink role
  `fission_sink_b` in final runtime identity telemetry,
- `cell_basin_merge_runtime_stability_control` remains `structural_only`,
- `S0015` adds a third, longer-window example:
  `cell_developed_basin_centroid_collapse_long_window` lowers two developed
  multi-node basins, runs for 24 steps, and records a `group_centroid` selected
  receiving-basin target after the source-declared `fission_sink_b` anchor is
  lost,
- no GRC9 `collapse` event kind is introduced.

### Iteration 8.3: Full-Capacity Phenomenology Cascade

Add the most complex source-authored GRCL-9 seed in the current batch.

Purpose:

- compose spark, expansion, growth, fission, and collapse-adjacent identity
  evidence in one connected GRC9 replay,
- keep the source layer in GRCL/Morse vocabulary rather than direct GRC9 graph
  literals,
- and verify that the visualization stack can show the full system state.

Current outcome:

- implemented as `S0020`,
- seed:
  `configs/landscapes/seed/grcl9-cell-full-capacity-phenomenology-cascade.seed.yaml`,
- replay:
  `outputs/grcl9/lowering/sessions/S0020/`,
- lowered graph: `24` nodes and `28` edges,
- requested steps: `24`,
- runtime events: `1` spark, `1` expansion, `60` growth,
- selector status: `passed`,
- collapse-like target selection remains diagnostic and uses `group_centroid`.

### Iteration 8.4: Cascade Robustness Family

Stress the accepted S0020 full-capacity cascade with source-level perturbations
that preserve the GRCL-9 lowering boundary.

Purpose:

- test whether the full-capacity cascade survives moderate growth-pressure
  changes,
- test whether the explicit merge bridge is required for the collapse-like
  long-window observation,
- test how basin-support scale, absent refinement, and absent growth affect
  selector interpretation,
- and keep each variant replayable as a source-authored GRCL-9 landscape seed.

Seed variants:

- `grcl9-cell-full-capacity-cascade-low-growth.seed.yaml`
- `grcl9-cell-full-capacity-cascade-high-growth.seed.yaml`
- `grcl9-cell-full-capacity-cascade-no-merge-bridge.seed.yaml`
- `grcl9-cell-full-capacity-cascade-weak-merge-bridge.seed.yaml`
- `grcl9-cell-full-capacity-cascade-isolated-bridge.seed.yaml`
- `grcl9-cell-full-capacity-cascade-larger-basin-support.seed.yaml`
- `grcl9-cell-full-capacity-cascade-no-refinement.seed.yaml`
- `grcl9-cell-full-capacity-cascade-no-growth.seed.yaml`
- `grcl9-cell-full-capacity-cascade-balanced-basins.seed.yaml`
- `grcl9-cell-full-capacity-cascade-mild-asymmetry.seed.yaml`
- `grcl9-cell-full-capacity-cascade-threshold-asymmetry.seed.yaml`
- `grcl9-cell-full-capacity-cascade-deep-collapse.seed.yaml`
- `grcl9-cell-full-capacity-cascade-isolated-threshold.seed.yaml`

Current outcome:

- first implemented as `S0021`, refined as `S0022`,
- replay:
  `outputs/grcl9/lowering/sessions/S0022/`,
- requested steps: `24` per lane,
- lanes: `9`,
- total runtime events: `444`,
- baseline, low-growth, and high-growth lanes passed,
- removing, weakening, or making the fission bridge negligible did not prevent
  collapse-like sink-role loss, so the bridge-necessity assumption is false for
  the current dynamics,
- larger basin support is now classified through an explicit ambiguous
  multi-anchor-loss selector rather than as a plain miss,
- no-refinement now uses runtime expansion event count instead of module-size
  summaries, which separates actual expansion events from fission-module
  evidence,
- no-growth remains a useful negative control: spark and expansion persist, but
  collapse-like target selection remains ambiguous when growth is removed,
- `S0023` adds the basin-asymmetry ladder:
  - balanced basins miss the structural-only hypothesis and classify as
    ambiguous by losing the A anchor while retaining B,
  - mild asymmetry already produces B-loss,
  - threshold, deep-collapse, and isolated-threshold variants all produce
    collapse-like B-loss,
  - the isolated-threshold pass reinforces that explicit fission bridge
    strength is not the primary driver,
- `S0024` adds a compact phase diagram:
  - basin regimes: balanced, mild asymmetry, threshold asymmetry, deep
    collapse,
  - growth regimes: no growth, low growth, nominal growth,
  - all no-growth lanes classify as ambiguous with both source sink anchors
    lost,
  - balanced low/nominal lanes classify as ambiguous with A-anchor loss,
  - threshold and deep low/nominal lanes classify as collapse-like B-loss,
  - mild asymmetry is the transition row: no-growth is ambiguous,
    low-growth is ambiguous after runaway spark/expansion/growth, and
    nominal-growth is collapse-like B-loss,
  - packaged summary artifacts are written to
    `outputs/grcl9/lowering/sessions/S0024/reports/phase_diagram_summary.json`
    and `phase_diagram_summary.md`,
  - the visual matrix index is written to
    `outputs/grcl9/lowering/sessions/S0024/visualizations/phase_diagram_visual_index.md`.

### Iteration 8.5: Accepted Collapse Extension

Implement the outcome of Iterations 8.1, 8.2, and the Phase T/V review.

Accepted outcome:

- keep Phase T-GRC9 unchanged: no `collapse` event kind, no new GRC9 collapse
  equation, and no change to `phase_t_grc9_iter1_v1` field meanings,
- keep Phase V-GRC9 boundary language unchanged: collapse visuals are backed by
  saved telemetry/checkpoints and remain source-role overlays,
- accept S0024 as diagnostic-only evidence for collapse-like source-role loss
  across a basin-asymmetry/growth phase diagram,
- extend the reviewed GRCL-9 lowered motif catalog with an additive
  `collapse_diagnostic` block for collapse-related selectors.

Implemented artifacts:

- catalog generator:
  `src/pygrc/telemetry/grcl9_lowered_motif_catalog.py`
- accepted-collapse catalog session:
  `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json`
- review report:
  `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_report.json`
- summary:
  `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`

S0025 records:

- source session: `S0024`
- accepted motifs: 12
- rejected motifs: 0
- collapse diagnostics: 12
- runtime-collapse-like diagnostics: 5
- ambiguous collapse-like diagnostics: 7

Acceptance:

- `S0008` remains the first reviewed lowered motif catalog,
- `S0025` records the accepted diagnostic-only collapse extension,
- source, telemetry, visualization, and catalog language all preserve the
  difference between source-role loss diagnostics and runtime collapse
  semantics.

### Iteration 9: Handoff

Record the first GRCL-9 source/lowering handoff.

Implemented artifact:

- `implementation/GRCL-9-Handoff.md`

Acceptance:

- documents implemented source constructs
- documents unsupported/deferred constructs
- records replayable sessions
- states that GRCL-9 remains lowering-only and does not add execution or
  observer semantics

Completion note:

- Revision 1 closes with S0024 as the strongest replayed phase-diagram
  evidence and S0025 as the accepted collapse-diagnostic catalog.
- The handoff records that the next lane should be an authorability test for
  any missing basin-asymmetry/growth source distinction, not an immediate
  source-schema expansion.

## Runtime And Telemetry Non-Changes

This plan should not require changes to:

- GRC9 step equations
- spark/expansion/growth runtime semantics
- Phase T-GRC9 telemetry contract field meanings
- existing GRC9 phenomenology discovery artifacts

Telemetry may gain GRCL-9 lowering summaries in a separate family/source
extension area, but GRC9 runtime telemetry must remain observation-oriented.

Collapse-adjacent work is the exception that must be reviewed explicitly before
closeout. If that review adds telemetry, it should do so as a new
diagnostic-only surface or a new contract version; it must not silently change
the meaning of the existing Phase T-GRC9 contract.

## Risk Register

### Source Smuggling Runtime Results

Risk:

- source fields accidentally become event declarations.

Mitigation:

- every source construct has explicit non-claims
- selectors validate runtime evidence after replay
- schema rejects event-count or solved-diagnostic source fields

### Generic Projector Drift

Risk:

- GRCL-9 becomes another heuristic neutral projector.

Mitigation:

- lower only explicit source constructs
- require manifest entries for every construct
- record assembly policy and projector revision

### Vocabulary Bypass

Risk:

- examples bypass GRCL vocabulary and become thin wrappers over GRC9 graph
  literals.

Mitigation:

- require authored landscape examples before catalog review
- compile examples into GRCL-9 source schema instead of raw GRC9 payloads
- reject examples that embed solved telemetry, event histories, or lowered graph
  literals

### Disconnected Motif Regression

Risk:

- multi-motif fixtures regress to disconnected graphs.

Mitigation:

- connected-graph validation is mandatory
- bridge edges are explicit and checkpoint-visible
- disconnected output is a lowering error

### Telemetry Path Drift

Risk:

- selectors use convenience paths that do not match Phase T-GRC9 contract.

Mitigation:

- manifest entries must use contract field names
- tests verify selector field paths against representative telemetry payloads

### Optional Field Overclaim

Risk:

- optional telemetry such as birth-probability summaries is treated as required.

Mitigation:

- plan and manifest must mark optional evidence as optional
- required evidence should use lifecycle counts or event rows where available

## Completion Definition

GRCL-9 Revision 1 is complete when:

- source schema and lowering manifest exist,
- accepted S0026 motif families have source fixtures,
- authored GRCL landscape examples compile into those source fixtures,
- fixtures lower deterministically to connected GRC9 graphs,
- replay sessions are stored under `outputs/grcl9/lowering/`,
- telemetry selectors reproduce the intended pass/fail distinctions,
- visualizations are generated from saved checkpoints,
- reviewed lowered motifs are cataloged from the full GRCL example -> source
  schema -> lowered graph -> telemetry -> visualization chain,
- collapse-adjacent source structures are reviewed and either cataloged as
  structural probes or explicitly deferred,
- and the handoff document states exactly what GRCL-9 can and cannot claim.
