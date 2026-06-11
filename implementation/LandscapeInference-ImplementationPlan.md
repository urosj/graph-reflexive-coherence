# Landscape Inference Implementation Plan

## Purpose

This document defines the implementation track for mapping evolved `PyGRC`
geometry back into the existing landscape descriptor language.

The purpose is not to add a separate knowledge-graph subsystem. In this project,
knowledge graphs are an application of:

```text
landscape descriptor language
-> PyGRC runtime evolution
-> telemetry/checkpoints
-> inferred landscape primitives
```

The missing implementation layer is therefore inference/classification:

```text
observed geometry -> inferred LandscapeSeed primitives
```

## Source Anchors

- [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
- [`LandscapeInference-ReferenceGuide.md`](../docs/reference/LandscapeInference-ReferenceGuide.md)
- [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
- [`GRCL-V3-Vocabulary.md`](./GRCL-V3-Vocabulary.md)
- [`GRCL-9-Vocabulary.md`](./GRCL-9-Vocabulary.md)
- [`GRCL-9V3-Vocabulary.md`](./GRCL-9V3-Vocabulary.md)
- Phase T telemetry contracts for `GRCV3`, `GRC9`, and `GRC9V3`
- Phase V graph checkpoint artifacts
- External source notebook: `2026-04-30-ReflexiveKnowledgeGeometry-SynthesisSeed.md`
  (not included in this repository)

## Core Position

Landscape inference reuses the existing neutral primitive vocabulary:

- `basin`
- `plateau`
- `ridge`
- `valley`
- `junction`
- `saddle`

It may add inference metadata and family-specific extensions, but it should not
invent a parallel ontology for knowledge graphs. Terms such as
`identity_basin`, `boundary_ridge`, `valley_channel`, `pheromone_marker`,
`spark_candidate`, or `growth_frontier` should be represented as:

- existing primitive types,
- `role` values,
- `tags`,
- `hints`,
- and `extensions.landscape_inference`.

## Authority Model

The same vocabulary can appear in three authority modes:

```text
authored  -> declared by source landscape / GRCL input
lowered   -> produced by a lowering/projector stage
observed  -> inferred from runtime telemetry and checkpoints
```

The runtime remains authoritative for dynamics. The inference layer is
observer-only. It must not mutate coherence, flux, conductance, topology,
budget state, or source/lowering registries.

Authority order:

```text
dynamics
-> telemetry/checkpoint evidence
-> observed primitive inference
-> diagnostics, comparison, export, or policy suggestions
```

## Output Shape

The primary output is a normal `LandscapeSeed` document with:

```yaml
seed_schema: pygrc.landscape_seed
seed_version: "0.1"
meta:
  source_kind: inferred_observed_landscape
primitives: [...]
extensions:
  landscape_inference:
    contract_version: landscape_inference_iter1_v1
    source_session_id: S....
    source_artifact_paths: [...]
    inference_window:
      start_step: int
      end_step: int
```

Each observed primitive should carry:

```yaml
extensions:
  landscape_inference:
    authority: observed
    classifier_id: string
    classifier_version: string
    confidence: float
    source_runtime_family: grcv3 | grc9 | grc9v3
    observed_from:
      session_id: string
      run_id: string
      artifact_root: string
      step_window: [start, end]
    evidence:
      telemetry_fields: [...]
      checkpoint_ids: [...]
      node_ids: [...]
      edge_ids: [...]
      path_node_ids: [...]
    matched_authored_primitive_id: string | null
    relationship_to_authored:
      preserved | transformed | split | collapsed | emerged | dissolved | unknown
```

## Evidence Substrate

Landscape inference is checkpoint-first for any claim that requires local graph
structure. Step rows and run summaries are useful for coarse selection and
session triage, but they usually compress away the node/edge detail needed for
classifying paths, ridges, pheromone traces, and authored-vs-observed
relationships.

The first implementation should build a small reusable substrate that loads a
checkpoint series and reconstructs:

- node records keyed by stable runtime node id,
- edge records keyed by stable runtime edge id,
- adjacency from checkpoint edge records,
- per-node geometric or hybrid evidence when present,
- per-edge conductance/flux evidence when present,
- port-state overlays for GRC9/GRC9V3 when present,
- provenance and lowering tags when present.

Persistence windows should be computed from checkpoint series, not inferred
from a single final summary. Step-row aggregates may be recorded as weak
fallback evidence, but they cannot by themselves prove path persistence,
pruning survival, pheromone repetition, or ridge survival.

## Data Dependencies And Availability Rules

Classifiers must not assume that every checkpoint serializer exposes every
local field as a top-level canonical key. The evidence substrate should
normalize the following surfaces when they are available and emit explicit
availability/degraded-evidence metadata when they are absent.

### Bridge Edges

GRCL-9 and GRCL-9V3 lowerers preserve bridge information in edge payloads and
bridge-edge caches, but generic checkpoint `edge_records` do not require a
top-level `grcl9_edge_kind` field. Bridge detection should therefore check, in
order:

- `edge_record.grcl9_edge_kind`,
- `edge_record.grcl9v3_edge_kind`,
- `edge_record.payload.grcl9_edge_kind`,
- `edge_record.payload.grcl9v3_edge_kind`,
- `family_extensions.grcl9.bridge_edge_ids`,
- `family_extensions.grcl9v3.bridge_edge_ids`,
- lowered cached quantities when available in a replay payload.

Topology-based bridge guessing may be used only as an ambiguous fallback. It
must be recorded as `bridge_detection_mode = inferred_topology`, not as a
source-provenanced bridge tag.

### Provenance Tags

Authored-vs-observed matching should prefer explicit provenance when present:

- source construct ids,
- lowered motif ids,
- source-to-runtime node/edge membership,
- lowered motif registry records,
- node or edge payload provenance.

If checkpoint node/edge records do not carry provenance, matching falls back to
topology and geometry. The comparison report must record
`provenance_available = false` for those matches.

### Quadrature Weights

Budget audit uses per-node quadrature weights only when they are present. The
current GRC9V3 runtime is unit-measure, so unit-weight budget audit is valid
for those artifacts. Future non-unit quadrature checkpoints should expose
`quadrature_weight` on node records or an equivalent topology extension. When
weights are missing, the audit must emit `quadrature_weight_mode =
unit_measure_assumed` or `unavailable` rather than silently pretending that
non-unit weights were checked.

### Port-State Overlays

Per-node `junction` gate/router classification needs checkpoint-local port
state. Step-row `PortChartSummary` aggregates can identify candidate sessions,
but they cannot prove a per-node gate or router. The evidence substrate should
reconstruct port matrices from checkpoint node records and/or
`family_extensions.*.port_overlay`.

### Window Selection

Inference windows must be deterministic and replayable. Supported policies:

- explicit `[start_step, end_step]`,
- final `N` checkpoints,
- event-centered `event_step +/- N` windows,
- whole-checkpoint-series windows for short runs.

Persistence-sensitive classifiers should require at least three checkpoints
unless the run is explicitly marked as single-checkpoint diagnostic evidence.
Each classifier should record the selected policy, checkpoint count, step span,
and whether the window satisfies its minimum span.

## Family Capability Matrix

The classifier must record evidence availability per runtime family instead of
pretending that every family exposes the same geometry.

| Family | Supported Inference | Main Evidence | Limits |
|---|---|---|---|
| `grcv3` | Full geometric basin/ridge inference, path and pheromone inference when checkpoints contain edge evidence | checkpoint gradient, Hessian, basin mass, conductance/flux | no nine-port port chart |
| `grc9` | Topology/mechanical inference, port/growth/spark evidence, weaker basin inference | successor/basin topology, sink flags, port overlays, flow overlays | no row-basis Hessian or GRCV3 gradient geometry |
| `grc9v3` | Full hybrid inference with GRC9 ports plus GRCV3-style semantic geometry | row-basis gradient/Hessian, tensor summaries, basin mass, ports, events | some surfaces remain checkpoint-only |

Basin mass should be read from checkpoint node records when available. For
families or artifacts that do not expose basin mass, the classifier may record
a weaker coherence-mass proxy, but the primitive evidence must say that a true
mass threshold was unavailable.

## Path Extraction And Persistence

Valley and pheromone classifiers depend on explicit path extraction. This is a
new infrastructure requirement, not an existing helper.

The path extractor should:

- reconstruct adjacency from graph checkpoint edge records,
- enumerate candidate paths between basin domains or candidate endpoint sets,
- compute path aggregates such as bottleneck conductance, total or mean flux
  support, directionality, and label support when present,
- exclude artificial lowering bridge edges from positive valley claims,
- flag bridge edges if they are encountered,
- detect path rupture by comparing path node/edge sets across checkpoints,
- record nodes or edges removed by pruning/merge windows.

GRCL-9 and GRCL-9V3 lowering bridge edges are connectivity artifacts, not
natural relation channels. Edges tagged with `grcl9_edge_kind = "bridge"` or
listed in lowered bridge caches must not by themselves support a
`valley_channel` claim.

## Budget Audit

Budget accountability is part of the inferred primitive evidence, but the code
does not yet have a standalone audit utility. The inference track should add a
read-only budget audit over checkpoints or state-like payloads.

The audit should compute the available budget sum, preferably
`sum(mu_i * C_i)` when quadrature weights are present and a unit-weight sum
otherwise. It should compare the result to a recorded runtime target when one
exists, emit `budget_error`, and classify primitive-level budget evidence as
`stores`, `passes`, `redistributes`, `conserved_zero`, `leak_error`, or
`unavailable`.

This audit is diagnostic only. It must not call runtime correction functions or
modify state.

## Primitive Matching Strategy

Authored-vs-observed comparison requires an explicit matching algorithm.
Matching should proceed in priority order:

1. Provenance match through source construct ids, lowered motif ids, or
   source-to-runtime node/edge membership.
2. Topology match through containment, endpoint overlap, basin membership, or
   stable path overlap.
3. Geometry/role match through primitive type, role, tags, location hints, and
   evidence similarity.
4. Fallback classification as `emerged` for unmatched observed primitives or
   `dissolved` for unmatched authored primitives.

Split and collapse must be emitted as explicit relationship records. They
should not be hidden as several unrelated mismatches.

## Inference Targets

### Basin / Identity Basin

Represent as:

```text
type = basin
role = identity_basin | basin_seed
```

Evidence may include sink status, basin membership, low gradient, signed
Hessian stability, basin mass, persistence, hierarchy parent/depth, and budget
accounting.

### Ridge / Boundary Ridge

Represent as:

```text
type = ridge
role = boundary_ridge | membrane | separator
```

Evidence may include high gradient/tensor anisotropy, low leakage,
frontier/boundary port roles, pruning survival, and separation between basin
domains.

### Valley / Relation Channel

Represent as:

```text
type = valley
role = valley_channel | relation_channel
```

A valley is inferred as a path, not merely an edge. Evidence may include
endpoint basin ids, path node ids, persistent throughflow, bottleneck
conductance, delay/geometric labels, and absence of basin-seed formation along
the interior.

### Pheromone / Flux Memory

Represent as:

```text
type = valley
role = pheromone_marker
```

This keeps memory traces inside the path/valley vocabulary. A pheromone marker
is a reinforced route that biases future routing but has not become an
identity basin. Evidence may include repeated flux over a window and
conductance reinforcement without basin stability.

Pheromone-to-identity promotion is not a classifier result in this track. It is
a downstream policy suggestion that requires comparing a path-memory window
against later basin-seed evidence.

### Junction / Gate / Router / Collapse Site

Represent as:

```text
type = junction
role = gate | router | collapse_site
```

Evidence may include port pattern, multi-output flux distribution,
choice/collapse telemetry, and path branching.

### Saddle / Spark Candidate

Represent as:

```text
type = saddle
role = spark_candidate | curvature_degeneracy
```

Evidence may include signed-Hessian degeneracy, GRC9 saturation/instability
signals, spark candidate events, or expansion records.

### Plateau / Ambiguous Support

Represent as:

```text
type = plateau
role = ambiguous_support | unresolved_region
```

Evidence may include broad support, weak differentiation, no stable basin seed,
or multi-basin unresolved structure.

## Authored-vs-Observed Comparison

Inference should support comparison between source landscape and observed
landscape:

- `preserved`: observed primitive matches an authored primitive.
- `transformed`: same rough role, different evidence or geometry.
- `split`: one authored primitive became multiple observed primitives.
- `collapsed`: multiple authored primitives became one observed primitive.
- `emerged`: observed primitive has no authored source.
- `dissolved`: authored primitive has no observed support.
- `unknown`: insufficient evidence.

This comparison is the bridge from runtime evolution back to dynamic knowledge
graph interpretation.

## Non-Claims

Landscape inference does not:

- create new runtime dynamics,
- mutate graph state,
- replace GRCL/source lowering,
- replace reviewed motif catalogs,
- prove semantic truth of inferred concepts,
- infer open-system environmental exchange unless telemetry explicitly
  records it,
- treat every edge as a relation,
- treat every reinforced path as an identity.

## Iteration Plan

### Iteration 1: Contract And Schema Boundary

- Define `landscape_inference` extension payload.
- Define authority values: `authored`, `lowered`, `observed`.
- Define comparison statuses.
- Define required evidence metadata.
- State that output is a normal `LandscapeSeed`.

### Iteration 2: Artifact Loader And Inference Window

- Load a telemetry artifact pack or session lane.
- Load optional graph checkpoints.
- Define a stable inference window.
- Write a minimal inferred seed with top-level provenance extension and no
  primitive inference yet.

### Iteration 2.1: Checkpoint Evidence Substrate

- Reconstruct node, edge, and adjacency views from checkpoint artifacts.
- Implement candidate path extraction and path aggregate helpers.
- Implement checkpoint-window persistence helpers.
- Implement bridge-edge exclusion/flagging for GRCL-9 and GRCL-9V3 lowered
  artifacts.
- Normalize bridge tags from edge payloads, family extensions, and lowered
  bridge caches.
- Normalize provenance tags from node/edge payloads, motif registries, and
  source-to-runtime membership when present.
- Normalize quadrature-weight availability and unit-measure fallback.
- Normalize per-node port matrices from checkpoint node records or port
  overlays.
- Define deterministic inference-window selection policies.
- Implement read-only budget audit helpers.

### Iteration 3: Basin Classifier

Status: implemented.

- Infer `basin` primitives from family-specific evidence.
- Support full GRCV3/GRC9V3 geometric basin inference when checkpoint gradient,
  signed-Hessian, and basin-mass evidence are present.
- Support weaker GRC9 topology-only basin inference when only sink/basin
  topology is available.
- Attach observed evidence fields.
- Compare observed basins with authored basin primitives when source seed
  provenance is available.

Implementation notes:
- `src/pygrc/landscapes/inference_basin.py` emits observed
  `BasinSeedPrimitive` records from normalized checkpoint evidence.
- GRCV3/GRC9V3 full geometric claims require checkpoint gradient,
  signed-Hessian, and basin mass. Missing basin mass is recorded as a
  coherence-mass fallback with weaker evidence status.
- GRC9 claims remain topology/mechanical and do not claim geometric support.
- Authored-vs-observed basin matching records preserved, emerged, and
  dissolved basin ids in the output seed extension.

### Iteration 4: Valley / Path Classifier

- Extract candidate paths from checkpoint topology and flux overlays.
- Infer `valley` primitives only for persistent throughflow paths between
  basin domains.
- Record path evidence and reject single-edge overclaims unless the edge is the
  complete path.
- Exclude or explicitly flag artificial lowering bridge edges.
- Record path rupture when nodes/edges disappear across the persistence window.
- Implementation status: closed by `landscape_inference_iter4_v1` in
  `src/pygrc/landscapes/inference_valley.py`. The classifier consumes the
  checkpoint substrate path extractor, emits validated `ValleySeedPrimitive`
  records for accepted persistent paths, and records rejected/ambiguous path
  evidence for bridge and rupture cases.

### Iteration 4.1: Valley Candidate Ranking And Deduplication

- Add deterministic ranking for raw valley candidates before observed seed
  emission.
- Deduplicate emitted `valley_channel` primitives by endpoint basin pair while
  preserving all rejected and ambiguous candidates in diagnostic summaries.
- Prefer accepted, persistent, non-bridge, higher-flux, higher-bottleneck,
  shorter paths in that order.
- Record ranking metadata (`ranking_score`, `ranking_reason`,
  `deduplication_group_id`) so downstream review can explain why one path was
  emitted and another stayed diagnostic-only.
- Validate on the existing Iteration 3 artifact set (`S0001`, `S0003`,
  `S0004`, `S0006`), where raw candidate counts are intentionally larger than
  the number of useful emitted valley primitives.
- Implementation status: closed with `S0007` evidence. Raw accepted paths in
  `S0003` compress from 32 candidates to 5 emitted endpoint-pair valleys,
  while `S0001`, `S0004`, and `S0006` already have unique accepted endpoint
  pairs.

### Iteration 5: Ridge / Boundary Classifier

- Infer `ridge` primitives from checkpoint-local high-gradient, tensor, and
  port-boundary evidence.
- Keep pressure-boundary/frontier provenance separate from ridge/membrane
  inference.
- Record leakage/low-throughflow evidence when available.
- Implementation status: closed by `landscape_inference_iter5_v1` in
  `src/pygrc/landscapes/inference_ridge.py`, with `S0008` evidence over the
  existing Iteration 3 artifact set. Ridge claims require checkpoint-local
  gradient or tensor-anisotropy evidence; pressure-boundary/front-capacity
  labels alone are rejected as insufficient ridge evidence.

### Iteration 6: Junction / Saddle / Event Classifiers

- Infer `junction` roles from router/gate/collapse evidence.
- Infer `saddle` roles from spark candidate and curvature-degeneracy evidence.
- Preserve event-backed provenance.
- Use GRC9/GRC9V3 port-state overlays for gate/router evidence when present.
- Treat step-row port aggregates as candidate-selection evidence only, not as
  per-node gate/router proof.
- Implementation status: closed by `landscape_inference_iter6_v1` in
  `src/pygrc/landscapes/inference_junction.py`, with `S0009` evidence over the
  existing Iteration 3-5 artifact set. Gate/router claims require
  checkpoint-local port matrices and flux/branch evidence; event-backed
  collapse and spark roles remain separate from persistent landscape roles.

### Iteration 7: Pheromone And Persistence Windows

- Infer pheromone markers as `valley` primitives with
  `role = pheromone_marker`.
- Require repeated flux or conductance reinforcement over a persistence
  window.
- Explicitly prevent pheromone markers from being counted as identity basins.
- Emit pheromone promotion only as a policy suggestion, not as an identity
  claim.
- Implementation status: closed by `landscape_inference_iter7_v1` in
  `src/pygrc/landscapes/inference_pheromone.py`, with `S0010` evidence over
  the existing Iteration 3-6 artifact set. Collapse/choice events are optional
  path-emphasis evidence only; they do not define pheromone markers and cannot
  replace repeated path activity or conductance reinforcement.

### Iteration 8: Authored-vs-Observed Landscape Comparison

- Compare source landscape primitives with inferred observed primitives.
- Match by provenance first, then topology/containment/path overlap, then
  role/geometry similarity.
- Record whether provenance was available for each match.
- Emit preserved/transformed/split/collapsed/emerged/dissolved statuses.
- Emit explicit split and collapse records.
- Write JSON and Markdown comparison reports.
- Implementation status: closed by `landscape_inference_iter8_v1` in
  `src/pygrc/landscapes/inference_compare.py`, with `S0011` comparison
  reports. When original authored GRCL seeds are unavailable, comparison can
  run against an explicit reference observed seed without claiming source
  preservation.

### Iteration 9: Replayable Knowledge-Graph Application Demo

- Use existing GRCL/GRC9V3 and GRCV3 source examples.
- Run or load replay sessions with checkpoint-backed evidence.
- Infer observed landscape primitives across basin, valley, ridge, junction,
  saddle, and pheromone classifiers.
- Compare authored and observed primitives.
- Export the observed landscape as the dynamic knowledge graph view.
- Keep the demo explicitly downstream of runtime evidence.
- Implementation status: closed by `landscape_inference_iter9_v1` in
  `src/pygrc/landscapes/inference_kg.py`, with `S0012` exports for
  `corrected_propagated_front_relay`, `corrected_hybrid_full_composition`,
  `grcv3_mediated_spill_branch_single_intermediate_probe`, and
  `corrected_multi_center_delayed_collapse_learning`.
- Interpretation status: `S0012` establishes the first dynamic KG milestone.
  The KG export is the observed evolved landscape, not the authored source
  seed. Source seeds define geometric intention; runtime dynamics transform
  them; inference reconstructs the runtime-supported geometry afterward. The
  resulting `split`, `dissolved`, and `emerged` relationships are meaningful
  observations of transformation rather than failure labels.

## Optional Future Refinements

These items are useful next-order improvements, but they are not required
before continuing to ridge, junction, pheromone, or authored-vs-observed
inference. They should remain general and artifact-family-neutral.

### Valley Significance Optimization

- Status: partly implemented in S0013 for refinements 1-3. Remaining optional
  item: module/hierarchy-level endpoint grouping.
- Added endpoint-role filtering so persistent sinks, high-mass basins, and
  authored/lowered anchors rank above tiny one-node basin fragments unless the
  fragment carries strong flux or provenance.
- Added path significance scoring, with a threshold used during emission so
  low-significance paths can be filtered without changing raw diagnostics.
- Added dominance pruning inside each endpoint group: when one path has equal
  persistence and clearly stronger flux/bottleneck support, weaker alternatives
  remain diagnostic-only.
- Add optional module/hierarchy-level endpoint grouping when provenance is
  available, so many node-level module-internal paths can compress to one
  higher-level relation without losing checkpoint evidence.
- Added bridge ambiguity tiers: none, bridge-only, bridge-at-endpoint,
  bridge-in-middle, and bridge-mixed.
- Added flux-stability scoring across the checkpoint window, so a path with
  persistent throughflow ranks above a path that only persists topologically.
- S0013 result: the selected Iteration 9 probe set retained the same high-level
  primitive counts while gaining bridge-tier and flux-stability evidence on
  emitted valley/pheromone primitives. This confirms the refinements enrich
  interpretation without disturbing the established S0012 milestone.

Deferred ideas:

- Run-relative path significance threshold variants, for example total flux
  percentile, minimum absolute flux, or an exception for structurally unique
  connectors.
- Bridge-suppressed-by-non-bridge-alternative annotation when both bridge and
  non-bridge alternatives exist for the same endpoint pair.

### Pheromone Revival Probe

- Status: read-only diagnostic implemented in S0014. Matched runtime feedback
  variants remain deferred until geometry crawlers or policy hooks exist.
- Added a revival probe that groups `choice_detected` and `collapse` emphasis
  events by primary node, measures checkpoint-local activity after emphasis,
  and associates revived nodes with emitted pheromone path-memory markers.
- S0014 reused existing long-window artifacts rather than mutating runtime
  dynamics:
  - GRC9V3 corrected multi-center delayed collapse/learning: 4 monitored
    nodes, 1 revival candidate, and path-memory association for all monitored
    nodes.
  - GRCV3 mediated spill branch probe: 6 monitored nodes, 3 revival
    candidates, but only 1 with path-memory association. This is the strongest
    current signal that future path-memory feedback could be useful.
  - GRC9 developed-basin long-window artifact: 0 candidates because it has no
    event rows, so it acts as a no-event availability/negative case.
- The probe remains diagnostic. It does not prove suppression or delay, does
  not apply feedback, and does not convert pheromone markers into
  identity-basin claims.
- Future work: run matched variants with and without path-memory feedback once
  such a policy hook exists, then measure whether reinforced path memory
  suppresses or delays revival.

## Completion Criteria

Status: complete.

The first Landscape Inference track is complete because:

- inferred output reuses `LandscapeSeed`,
- every observed primitive has authority/evidence metadata,
- the observer is read-only,
- basin, valley, ridge, junction/saddle, and pheromone inference are
  implemented,
- authored-vs-observed comparison is available,
- dynamic KG export is implemented as an application view over inferred
  landscape primitives,
- `S0012` demonstrates the full source -> runtime -> observed landscape ->
  KG-view cycle,
- `S0013` records general valley/path-memory evidence refinements,
- `S0014` records the read-only pheromone revival diagnostic,
- and `docs/reference/LandscapeInference-ReferenceGuide.md` records capabilities,
  parameters, instructions, API examples, and script examples.
