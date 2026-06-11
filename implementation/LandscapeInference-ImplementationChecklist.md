# Landscape Inference Implementation Checklist

This checklist tracks the observer/classifier layer that maps evolved `PyGRC`
geometry back into the existing landscape descriptor language.

Operator reference and examples are maintained in
[`LandscapeInference-ReferenceGuide.md`](../docs/reference/LandscapeInference-ReferenceGuide.md).

## Ground Rules

- Reuse `LandscapeSeed` and the existing neutral primitive vocabulary.
- Do not create a separate knowledge-graph ontology.
- Treat knowledge graphs as an application/export view of inferred landscape
  primitives.
- Keep classifiers read-only.
- Do not mutate runtime state, graph topology, coherence, conductance, flux, or
  budget state.
- Distinguish authored, lowered, and observed authority.
- Keep pressure-boundary/frontier provenance separate from ridge/membrane
  inference.
- Do not classify a path as a valley without path-level evidence.
- Do not classify a pheromone marker as an identity basin without basin
  evidence.
- Treat checkpoint series as authoritative for local path, ridge, pheromone,
  and authored-vs-observed evidence.
- Treat step-row/run-summary aggregates as selection or fallback evidence,
  not as proof of local geometry.
- Exclude or explicitly flag lowering bridge edges before claiming natural
  valley/relation paths.

## Iteration 1. Contract And Schema Boundary

Status: complete.

### Goal

Define the landscape-inference contract before implementing classifiers.

### Checks

- [x] Define `landscape_inference` extension namespace
- [x] Define contract version `landscape_inference_iter1_v1`
- [x] Define primitive authority values:
  - `authored`
  - `lowered`
  - `observed`
- [x] Define authored-vs-observed relationship values:
  - `preserved`
  - `transformed`
  - `split`
  - `collapsed`
  - `emerged`
  - `dissolved`
  - `unknown`
- [x] Define required observed primitive evidence fields
- [x] Define top-level inferred `LandscapeSeed` provenance fields
- [x] State that inferred output is a normal `LandscapeSeed`
- [x] State that classifiers are observer-only
- [x] Add tests for contract serialization once code exists

### Verification

- [x] Contract does not introduce new primitive types for concepts/relations
- [x] Contract uses `role`, `tags`, `hints`, and extensions for inference roles
- [x] Contract rejects runtime-state smuggling in inferred seed metadata

### Implementation Notes

- Added `src/pygrc/landscapes/inference.py`.
- Exported the Iteration 1 contract helpers from `pygrc.landscapes`.
- The contract is extension-only: it does not add primitive types and does not
  alter runtime dynamics.
- `tests/landscapes/test_landscape_inference_contract.py` verifies constants,
  normal `LandscapeSeed` round-trip behavior, primitive-role usage, evidence
  requirements, and runtime-state smuggling rejection.

## Iteration 2. Artifact Loader And Inference Window

Status: complete.

### Goal

Load telemetry/checkpoint artifacts and emit a minimal observed landscape
document with provenance but no primitive classifiers yet.

### Checks

- [x] Add artifact loader for one run/lane
- [x] Load run summary
- [x] Load step rows
- [x] Load event rows
- [x] Load checkpoint index when present
- [x] Define inference window selection:
  - explicit step range
  - final window
  - event-centered window
- [x] Emit minimal `LandscapeSeed` with empty primitives
- [x] Add top-level `extensions.landscape_inference`
- [x] Record source runtime family
- [x] Record source artifact paths
- [x] Record inference window

### Verification

- [x] Minimal inferred seed round-trips through landscape seed I/O
- [x] Missing checkpoint files produce explicit availability status
- [x] Loader is deterministic on repeated runs

### Implementation Notes

- Added `src/pygrc/landscapes/inference_loader.py`.
- The loader is family-agnostic over shared telemetry artifacts and detects
  `grcv3`, `grc9`, and `grc9v3` from family extensions before falling back to
  run identity.
- Supported Iteration 2 window policies are `whole_run`, `explicit`, `final`,
  and `event_centered`.
- Minimal inferred observed seeds intentionally carry zero primitives and a
  top-level `extensions.landscape_inference` payload. Core seed validation now
  permits this only for `meta.source_kind = inferred_observed_landscape`.
- `tests/landscapes/test_landscape_inference_loader.py` verifies family
  detection, artifact availability, checkpoint-index loading, inference-window
  selection, and normal `LandscapeSeed` round-trip behavior.

## Iteration 2.1. Checkpoint Evidence Substrate

Status: complete.

### Goal

Build the reusable graph evidence substrate required by basin, valley, ridge,
pheromone, and authored-vs-observed classifiers.

### Checks

- [x] Load checkpoint series for an inference window
- [x] Implement deterministic inference-window selection policies:
  - explicit step range
  - final `N` checkpoints
  - event-centered `event_step +/- N`
  - whole-checkpoint-series window for short runs
- [x] Record selected window policy, checkpoint count, and step span
- [x] Mark persistence-sensitive windows with fewer than three checkpoints as
  diagnostic-only unless explicitly allowed
- [x] Reconstruct node records keyed by stable runtime node id
- [x] Reconstruct edge records keyed by stable runtime edge id
- [x] Reconstruct adjacency from checkpoint edge records
- [x] Preserve per-node geometric/hybrid evidence when available
- [x] Preserve per-edge conductance/flux evidence when available
- [x] Preserve GRC9/GRC9V3 port-state overlays when available
- [x] Reconstruct per-node port matrices from checkpoint node records when
  present
- [x] Reconstruct per-node port matrices from `family_extensions.*.port_overlay`
  when present
- [x] Record port-matrix availability status
- [x] Preserve provenance and lowering tags when available
- [x] Normalize source construct ids from node/edge payloads when present
- [x] Normalize lowered motif ids from node/edge payloads when present
- [x] Normalize source-to-runtime node/edge membership when present
- [x] Record provenance availability status
- [x] Implement candidate path extraction between endpoint node sets
- [x] Compute path aggregates:
  - bottleneck conductance
  - total or mean flux support
  - directionality
  - label support when available
- [x] Detect and flag bridge edges:
  - top-level `grcl9_edge_kind`
  - top-level `grcl9v3_edge_kind`
  - `grcl9_edge_kind = "bridge"`
  - `grcl9v3_edge_kind = "bridge"`
  - edge payload bridge-kind fields
  - `family_extensions.grcl9.bridge_edge_ids`
  - `family_extensions.grcl9v3.bridge_edge_ids`
  - lowered bridge-edge caches
- [x] Record bridge detection mode:
  - `source_tag`
  - `family_extension`
  - `lowered_cache`
  - `inferred_topology`
  - `unavailable`
- [x] Exclude bridge-only paths from positive `valley_channel` claims
- [x] Treat topology-inferred bridge detection as ambiguous fallback evidence
- [x] Detect path rupture across checkpoint windows
- [x] Record nodes/edges removed by pruning or merge windows
- [x] Implement read-only budget audit over checkpoint/state-like payloads
- [x] Compute budget sum with quadrature weights when present
- [x] Fall back to unit-weight coherence sum when weights are unavailable
- [x] Record quadrature-weight mode:
  - `checkpoint_weight`
  - `unit_measure`
  - `unit_measure_assumed`
  - `unavailable`
- [x] Emit budget availability and budget error
- [x] Emit primitive-level budget accountability:
  - `stores`
  - `passes`
  - `redistributes`
  - `conserved_zero`
  - `leak_error`
  - `unavailable`

### Verification

- [x] Path extraction is deterministic
- [x] Bridge edges are not silently promoted to natural valleys
- [x] Missing bridge tags produce explicit degraded/ambiguous evidence
- [x] Missing provenance produces explicit fallback-matching status
- [x] Missing quadrature weights produce explicit unit-measure or unavailable
  status
- [x] Missing port matrices prevent per-node gate/router claims
- [x] Persistence calculations use checkpoint series, not only final summary
- [x] Budget audit does not call correction functions or mutate state
- [x] Missing surfaces produce explicit availability fields

### Implementation Notes

- Added `src/pygrc/landscapes/inference_substrate.py`.
- The substrate normalizes checkpoint nodes, edges, adjacency, bridge markers,
  provenance, port matrices, path candidates, path persistence, and read-only
  budget audit summaries.
- Node evidence includes normalized geometric/hybrid fields for downstream
  classifiers: `gradient_norm`, `min_signed_hessian`, `tensor_trace`, and
  `tensor_anisotropy`.
- Edge evidence includes normalized label fields for downstream valley/path
  classifiers: `geometric_length`, `temporal_delay`, and `flux_coupling`.
- Bridge detection checks top-level edge fields, edge payload fields,
  `grcl9/grcl9v3` family extension bridge ids, and lowered bridge caches when
  present. The current substrate does not guess bridge identity from topology;
  absent bridge tags remain `unavailable`, which later classifiers must treat
  as degraded/ambiguous evidence.
- Candidate path extraction is deterministic and can exclude bridge-bearing
  paths before valley classifiers consume the result.
- Short checkpoint windows are marked diagnostic-only unless explicitly
  allowed.
- `tests/landscapes/test_landscape_inference_substrate.py` verifies bridge
  detection, port matrix reconstruction, provenance extraction, path aggregate
  calculation, bridge-path exclusion, rupture detection, short-window
  diagnostic status, and weighted budget audit.

## Iteration 3. Basin Classifier

Status: Complete.

### Goal

Infer observed `basin` primitives from identity/basin telemetry.

### Checks

- [x] Implement GRCV3 basin inference
- [x] Implement GRC9 topology-only basin inference
- [x] Implement GRC9V3 basin inference
- [x] Use sink/basin telemetry when present
- [x] Use gradient and signed-Hessian evidence when present
- [x] Use checkpoint basin mass when present
- [x] Record coherence-mass fallback when true basin mass is unavailable
- [x] Record family capability limits:
  - GRCV3 full geometric inference
  - GRC9 topology/mechanical inference
  - GRC9V3 full hybrid inference
- [x] Add persistence-window metadata
- [x] Emit `type = basin`
- [x] Use `role = identity_basin` or `basin_seed`
- [x] Attach evidence fields and node ids
- [x] Compare with authored basin primitives when source seed is available

### Verification

- [x] Inferred basins do not appear without evidence
- [x] GRC9 topology-only basins are not overclaimed as full geometric basins
- [x] Missing basin mass produces explicit weaker-evidence status
- [x] GRC9V3 full-geometric basin inference is artifact-backed after Phase 7
      basin-mass repair
- [x] Basin classifier is read-only
- [x] Output seed validates
- [x] Authored-vs-observed basin comparison records preserved/emerged/dissolved

### Implementation Notes

- `src/pygrc/landscapes/inference_basin.py` implements the first observed
  primitive classifier.
- The classifier consumes normalized checkpoint evidence from Iteration 2.1
  and emits normal `BasinSeedPrimitive` records with
  `extensions.landscape_inference` and `extensions.landscape_inference_basin`.
- GRCV3/GRC9V3 basins can be classified as `full_geometric_basin` when
  checkpoint gradient, signed-Hessian, and basin-mass evidence are present.
  When geometry is present but true basin mass is absent, the classifier emits
  `geometric_basin_mass_proxy` and records `coherence_mass_fallback`.
- `outputs/landscape_inference/sessions/S0006/` is the post-Phase-7-Iteration-9.1
  GRC9V3 basin-mass repair probe. It reruns representative GRC9V3 telemetry and
  basin inference after `M_i` became a core runtime/checkpoint field. The report
  records `basin_mass_sources = ["checkpoint_basin_mass"]` and
  `evidence_modes = ["full_geometric_basin"]`, closing the GRC9V3 full-hybrid
  basin evidence case for Iteration 3.
- `outputs/landscape_inference/sessions/S0004/` remains historical diagnostic
  evidence of the pre-repair limitation: GRC9V3 geometry was available, but true
  checkpoint basin mass was missing, so the classifier correctly emitted
  `geometric_basin_mass_proxy` with `coherence_mass_fallback`.
- GRC9 basins are classified as `topology_mechanical_basin`; they are not
  overclaimed as geometric basins.
- The emitted seed carries `landscape_inference_basin_summary` with
  preserved, emerged, and dissolved basin ids when an authored source seed is
  supplied.
- `tests/landscapes/test_landscape_inference_basin.py` covers the full
  geometric, topology-only, mass-fallback, no-evidence, seed-validation, and
  authored-comparison paths.

## Iteration 4. Valley / Path Classifier

### Goal

Infer observed `valley` primitives from persistent path-level throughflow.

### Checks

- [x] Extract candidate paths from graph checkpoints
- [x] Link path endpoints to basin domains when available
- [x] Compute path flux support
- [x] Compute bottleneck conductance when available
- [x] Record delay/geometric labels when available
- [x] Require intermediate nodes not to be stable basin seeds
- [x] Require persistence over the configured window
- [x] Exclude artificial lowering bridge edges from positive path claims
- [x] Flag bridge edges encountered in rejected/ambiguous path evidence
- [x] Detect path rupture across checkpoint windows
- [x] Count nodes/edges removed by pruning or merge windows
- [x] Emit `type = valley`
- [x] Use `role = valley_channel`
- [x] Record path node ids and edge ids

### Verification

- [x] Single edges are not overclaimed as valleys unless they are the complete
  path
- [x] Valley classifier rejects paths that become stable basin interiors
- [x] Valley classifier rejects bridge-only paths
- [x] Valley classifier records pruned/ruptured paths explicitly
- [x] Output seed validates

### Summary

Implemented in `src/pygrc/landscapes/inference_valley.py`. The classifier
consumes the Iteration 2 checkpoint substrate path extractor, links endpoints
to basin domains, computes path aggregate evidence, rejects bridge-only paths,
marks bridge-containing paths as ambiguous, records rupture evidence across the
checkpoint window, and emits validated `ValleySeedPrimitive` records for
accepted `valley_channel` paths. Endpoint basin stubs are emitted only as
references required by the normalized landscape seed schema.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin
```

Result: 17 tests OK.

## Iteration 4.1. Valley Candidate Ranking And Deduplication

### Goal

Refine Iteration 4 so valley output remains useful on real runs with many
equivalent path candidates. Keep the broad candidate scan for diagnostics, but
rank and deduplicate emitted `valley_channel` primitives before they enter the
observed seed.

This refinement is motivated by applying Iteration 4 to existing Iteration 3
artifacts:

| Session | Runtime | Checkpoints | Candidates | Accepted | Ambiguous | Rejected |
|---|---:|---:|---:|---:|---:|---:|
| `S0001` | `grc9v3` | 3 | 739 | 21 | 0 | 718 |
| `S0003` | `grcv3` | 12 | 304 | 32 | 0 | 272 |
| `S0004` | `grc9v3` | 100 | 65 | 8 | 41 | 16 |
| `S0006` | `grc9v3` | 3 | 739 | 21 | 0 | 718 |

The accepted candidates are real path evidence, but the raw classifier can
emit multiple equivalent or near-equivalent paths for the same basin pair.

### Checks

- [x] Define deterministic valley candidate score
- [x] Prefer accepted over ambiguous over rejected candidates
- [x] Prefer non-bridge paths over bridge-containing paths
- [x] Prefer higher persistence over lower persistence
- [x] Prefer stronger flux support when persistence is tied
- [x] Prefer higher bottleneck conductance when flux is tied
- [x] Prefer shorter paths when score evidence is otherwise tied
- [x] Deduplicate emitted valleys by endpoint basin pair
- [x] Preserve rejected/ambiguous candidates in diagnostic summaries
- [x] Record `ranking_score`, `ranking_reason`, and `deduplication_group_id`
      on candidate evidence
- [x] Add optional `max_valleys_per_endpoint_pair` classifier parameter
- [x] Keep path extraction deterministic after ranking

### Verification

- [x] Real artifact scan over `S0001` / `S0003` / `S0004` / `S0006` records raw
      versus emitted valley counts
- [x] Ranking is deterministic across repeated runs
- [x] Deduplication keeps the strongest accepted path for one endpoint pair
- [x] Deduplication does not hide bridge/rupture diagnostics
- [x] Output seed validates after deduplicated emission

### Summary

Implemented. Raw valley candidate classification remains broad and diagnostic;
seed emission now uses deterministic endpoint-pair deduplication. Ranking
prefers accepted, non-bridge, persistent, higher-flux, higher-bottleneck,
shorter paths. Candidate evidence records `ranking_score`, `ranking_reason`,
`deduplication_group_id`, and whether the candidate was emitted.

Artifact scan:

| Session | Runtime | Raw Candidates | Raw Accepted | Ambiguous | Rejected | Emitted |
|---|---:|---:|---:|---:|---:|---:|
| `S0001` | `grc9v3` | 739 | 21 | 0 | 718 | 21 |
| `S0003` | `grcv3` | 304 | 32 | 0 | 272 | 5 |
| `S0004` | `grc9v3` | 65 | 8 | 41 | 16 | 8 |
| `S0006` | `grc9v3` | 739 | 21 | 0 | 718 | 21 |

Stored under `outputs/landscape_inference/sessions/S0007/`:

- `valley_ranking_report.json`
- `README.md`
- one deduplicated observed-valley seed per source session

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_import_smoke \
  tests.landscapes.test_landscape_inference_contract \
  tests.landscapes.test_landscape_inference_loader \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley
```

Result: 30 tests OK.

Full landscape test discovery:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest discover tests/landscapes
```

Result: 240 tests OK.

## Iteration 5. Ridge / Boundary Classifier

### Goal

Infer observed `ridge` primitives from separating/high-gradient structures.

### Checks

- [x] Use gradient/tensor evidence when available
- [x] Use low-leakage or low-throughflow evidence when available
- [x] Use boundary/port evidence when available
- [x] Use pruning-survival evidence when available
- [x] Treat ridge inference as checkpoint-local when per-node evidence is
  required
- [x] Emit `type = ridge`
- [x] Use `role = boundary_ridge`, `membrane`, or `separator`
- [x] Keep pressure-boundary/frontier provenance distinct from ridge inference

### Verification

- [x] Pressure-boundary source labels alone do not create ridge primitives
- [x] Ridge classifier records evidence limitations explicitly
- [x] Step-row aggregates alone do not produce per-node ridge claims
- [x] Output seed validates

### Summary

Implemented in `src/pygrc/landscapes/inference_ridge.py`. The classifier is
checkpoint-local: accepted ridge claims require per-node gradient or tensor
anisotropy evidence. Port-boundary evidence and low-throughflow evidence enrich
the claim when present, and missing leakage/port evidence is recorded as an
explicit limitation. Pressure-boundary/front-capacity labels alone are rejected
as frontier evidence, not ridge/membrane evidence.

Artifact scan:

| Session | Runtime | Candidates | Accepted | Ambiguous | Rejected |
|---|---:|---:|---:|---:|---:|
| `S0001` | `grc9v3` | 16 | 16 | 0 | 0 |
| `S0003` | `grcv3` | 40 | 0 | 0 | 40 |
| `S0004` | `grc9v3` | 12 | 0 | 0 | 12 |
| `S0006` | `grc9v3` | 16 | 16 | 0 | 0 |

Stored under `outputs/landscape_inference/sessions/S0008/`:

- `ridge_inference_report.json`
- `README.md`
- one observed-ridge seed per source session

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_import_smoke \
  tests.landscapes.test_landscape_inference_contract \
  tests.landscapes.test_landscape_inference_loader \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_ridge
```

Result: 35 tests OK.

Full landscape test discovery:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest discover tests/landscapes
```

Result: 245 tests OK.

## Iteration 6. Junction / Saddle / Event Classifiers

### Goal

Infer junction and saddle primitives from routing, choice/collapse, and spark
evidence.

### Checks

- [x] Infer `junction` with `role = gate` where pass/block evidence exists
- [x] Infer `junction` with `role = router` where multi-output routing evidence
  exists
- [x] Infer `junction` with `role = collapse_site` from choice/collapse
  telemetry
- [x] Infer `saddle` with `role = spark_candidate` from spark candidate or
  curvature-degeneracy evidence
- [x] Use GRC9/GRC9V3 port-state overlays for gate/router classification
- [x] Distinguish gates from routers by port pattern and flux distribution
- [x] Use step-row port aggregates only to find candidate sessions/windows
- [x] Require checkpoint port matrices for per-node gate/router claims
- [x] Link event ids and step windows
- [x] Keep event-backed roles separate from persistent landscape roles

### Verification

- [x] Spark candidate does not automatically become a basin
- [x] Collapse site does not automatically become a valley or ridge
- [x] Output seed validates

### Result

Iteration 6 is complete. `src/pygrc/landscapes/inference_junction.py` emits
observed `junction` and `saddle` primitives from checkpoint-local port/flux
evidence and event rows. Gate/router claims require checkpoint port matrices;
step-row port aggregates remain session/window hints only. Event-backed
collapse and spark roles carry explicit event references and remain separate
from persistent basin, ridge, and valley claims.

Evidence was recorded in `outputs/landscape_inference/sessions/S0009` over the
same artifact set used by Iterations 3-5:

| Source | Runtime | Checkpoints | Events | Candidates | Junctions | Saddles |
|---|---:|---:|---:|---:|---:|---:|
| `S0001` | `grc9v3` | 3 | 7 | 33 | 19 | 14 |
| `S0003` | `grcv3` | 12 | 52 | 47 | 6 | 41 |
| `S0004` | `grc9v3` | 100 | 15 | 25 | 13 | 12 |
| `S0006` | `grc9v3` | 3 | 7 | 33 | 19 | 14 |

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_junction \
  tests.landscapes.test_import_smoke \
  tests.landscapes.test_landscape_inference_contract \
  tests.landscapes.test_landscape_inference_loader \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_ridge
```

Result: 41 tests OK.

## Iteration 7. Pheromone And Persistence Windows

### Goal

Infer reinforced path memory without overclaiming identity.

### Checks

- [x] Define path-memory persistence window
- [x] Detect repeated flux through a path
- [x] Detect conductance reinforcement when available
- [x] Emit `type = valley`
- [x] Use `role = pheromone_marker`
- [x] Record why identity-basin criteria are not met
- [x] Record promotion-candidate status separately from identity status
- [x] Emit promotion only as a policy suggestion
- [x] Compare pheromone evidence across checkpoint windows

### Verification

- [x] Pheromone markers are not counted as identity basins
- [x] Pheromone markers require path evidence
- [x] Pheromone promotion is not emitted as an identity claim
- [x] Output seed validates

### Result

Iteration 7 is complete. `src/pygrc/landscapes/inference_pheromone.py`
classifies path-memory candidates from checkpoint-window path activity and
emits accepted candidates as normal `valley` primitives with
`role = pheromone_marker`. The classifier requires repeated path flux or
conductance reinforcement. Choice/collapse events are recorded only as optional
path-emphasis evidence and cannot create a pheromone marker without path
evidence.

Promotion remains a policy suggestion (`consider_promote_pheromone_candidate`)
and is never emitted as an identity-basin claim.

Evidence was recorded in `outputs/landscape_inference/sessions/S0010` over the
existing Iteration 3-6 artifact set:

| Source | Runtime | Checkpoints | Events | Candidates | Accepted | Emitted Markers | Policy Suggestions | Identity Claims |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `S0001` | `grc9v3` | 3 | 7 | 739 | 21 | 21 | 21 | 0 |
| `S0003` | `grcv3` | 12 | 52 | 304 | 32 | 5 | 5 | 0 |
| `S0004` | `grc9v3` | 100 | 15 | 65 | 8 | 8 | 8 | 0 |
| `S0006` | `grc9v3` | 3 | 7 | 739 | 21 | 21 | 21 | 0 |

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_pheromone \
  tests.landscapes.test_landscape_inference_junction \
  tests.landscapes.test_import_smoke \
  tests.landscapes.test_landscape_inference_contract \
  tests.landscapes.test_landscape_inference_loader \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_ridge
```

Result: 46 tests OK.

## Iteration 8. Authored-vs-Observed Landscape Comparison

### Goal

Compare source landscape primitives with observed inferred primitives.

### Checks

- [x] Load authored/source `LandscapeSeed` when available
- [x] Load inferred observed `LandscapeSeed`
- [x] Match primitives by provenance/source construct id first
- [x] Record `provenance_available` for each provenance-first match attempt
- [x] Match primitives by topology, containment, endpoint overlap, or path
  overlap second
- [x] Match primitives by role and geometry similarity third
- [x] Classify unmatched observed primitives as `emerged`
- [x] Classify unmatched authored primitives as `dissolved`
- [x] Emit preserved/transformed/split/collapsed/emerged/dissolved/unknown
  statuses
- [x] Emit explicit split records
- [x] Emit explicit collapse records
- [x] Write JSON comparison report
- [x] Write Markdown comparison summary

### Verification

- [x] Split and collapse are explicit, not hidden as mismatches
- [x] Emerged observed primitives are recorded
- [x] Dissolved authored primitives are recorded
- [x] Comparison is deterministic

### Result

Iteration 8 is complete. `src/pygrc/landscapes/inference_compare.py`
implements deterministic authored/reference-vs-observed primitive comparison.
Matching priority is provenance/source construct id first, topology/path/
containment second, and role/geometry fallback third. The report emits explicit
`split` and `collapsed` records for one-to-many and many-to-one matches, and
records unmatched observed/reference primitives as `emerged`/`dissolved`.

Evidence was recorded in `outputs/landscape_inference/sessions/S0011`. The
available artifact set does not include original authored GRCL landscape seeds,
so S0011 uses the S0004 observed basin seed as a reference landscape and says
so explicitly:

| Comparison | Candidates | Records | Relationship Counts |
|---|---:|---:|---|
| `S0004_basin_vs_valley` | 121 | 19 | `{'dissolved': 10, 'emerged': 8, 'split': 1}` |
| `S0004_basin_vs_pheromone` | 121 | 19 | `{'dissolved': 10, 'emerged': 8, 'split': 1}` |
| `S0004_basin_vs_junction` | 0 | 36 | `{'dissolved': 11, 'emerged': 25}` |

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_compare \
  tests.landscapes.test_landscape_inference_pheromone \
  tests.landscapes.test_landscape_inference_junction \
  tests.landscapes.test_import_smoke \
  tests.landscapes.test_landscape_inference_contract \
  tests.landscapes.test_landscape_inference_loader \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_ridge
```

Result: 50 tests OK.

## Iteration 9. Replayable Knowledge-Graph Application Demo

Status: complete.

### Goal

Demonstrate dynamic knowledge-graph behavior as an application of PyGRC
landscape inference.

### Checks

- [x] Select existing source/GRCL examples
- [x] Replay or reuse saved runtime sessions
- [x] Infer observed landscape primitives
- [x] Compare authored and observed primitives
- [x] Export observed landscape as the dynamic knowledge graph view
- [x] Include replay commands
- [x] Store artifacts under `outputs/landscape_inference/sessions/S0012`

### Verification

- [x] Demo does not add a special KG ontology
- [x] Demo uses inferred `LandscapeSeed` output
- [x] Demo records evidence paths for every observed primitive
- [x] Demo states remaining classifier limitations

### Result

Iteration 9 is complete. `src/pygrc/landscapes/inference_kg.py` exports a
dynamic KG view over existing `LandscapeSeed` primitives. The exporter is
application-level only: it records `ontology_source =
pygrc_landscape_seed_primitives` and `introduces_new_ontology = false`.

Evidence was recorded in `outputs/landscape_inference/sessions/S0012` using
the four selected seed/runtime pairs:

| Seed | Runtime | Window | Primitives | KG Edges | Relationships |
|---|---|---:|---:|---:|---|
| `corrected_propagated_front_relay` | `grc9v3` | 76-100 | 70 | 48 | `{'dissolved': 3, 'split': 4}` |
| `corrected_hybrid_full_composition` | `grc9v3` | 1-3 | 133 | 64 | `{'dissolved': 14, 'split': 5}` |
| `grcv3_mediated_spill_branch_single_intermediate_probe` | `grcv3` | 1-12 | 72 | 20 | `{'dissolved': 7, 'emerged': 47, 'split': 2}` |
| `corrected_multi_center_delayed_collapse_learning` | `grc9v3` | 1-20 | 85 | 52 | `{'dissolved': 10, 'split': 4}` |

The session includes copied source seeds, observed landscape seeds,
authored-vs-observed comparison reports, and `dynamic_kg_view.json` exports for
each selected seed. Runtime artifacts were reused rather than rerun because the
selected sessions already contained checkpoint-backed evidence.

Observational result:

- `corrected_propagated_front_relay` produced a front-relay inferred landscape
  with 14 basins, 12 valley channels, 12 pheromone/path-memory markers, 17
  junctions, and 15 saddles. Ridge candidates were rejected, preserving the
  rule that pressure/frontier labels alone do not imply ridge evidence.
- `corrected_hybrid_full_composition` produced the strongest full
  knowledge-geometry surface: 19 basins, 16 valley channels, 16 pheromone
  markers, 19 ridges, 34 junctions, and 29 saddles.
- `grcv3_mediated_spill_branch_single_intermediate_probe` produced the
  clearest runtime-emergent geometry: 15 basins, 5 valley channels, 5
  pheromone markers, 6 junctions, 41 saddles, and 47 `emerged`
  authored-vs-observed comparison records.
- `corrected_multi_center_delayed_collapse_learning` produced the strongest
  collapse/learning/path-memory surface: 15 basins, 12 valley channels, 14
  pheromone markers, 24 junctions, and 20 saddles.

The source-vs-observed comparison mostly reports `split`, `dissolved`, and
`emerged` relationships rather than `preserved` relationships. This is the
intended conservative interpretation: the dynamic KG exports are observed
runtime geometry mapped back into the `LandscapeSeed` primitive language, not
semantic-truth claims and not exact source-preservation claims.

Milestone interpretation:

- Iteration 9 is the first point where landscape inference functions as an
  application-level dynamic knowledge-graph observer rather than only an
  artifact loader or classifier test.
- The dynamic KG is the observed evolved landscape, not the authored source
  seed. The source seed defines geometric intention; runtime dynamics transform
  it; inference reconstructs the geometry that actually exists afterward.
- `split`, `dissolved`, and `emerged` relationships are therefore meaningful
  evidence, not failure labels. They show authored structures branching,
  disappearing, densifying, or producing new runtime-supported geometry.
- The selected examples now form a diagnostic synthetic probe set:
  full-composition for broad coverage, front-relay for propagation/path memory,
  GRCV3 mediated spill for runtime-emergent geometry, and multi-center
  collapse for collapse/learning/path-memory behavior.
- Ridge and pheromone behavior stayed correctly conservative: pressure/frontier
  labels alone did not become ridges, and pheromone markers remained path
  memory rather than identity-basin claims.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_basin \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_ridge \
  tests.landscapes.test_landscape_inference_junction \
  tests.landscapes.test_landscape_inference_pheromone \
  tests.landscapes.test_landscape_inference_compare \
  tests.landscapes.test_landscape_inference_kg
```

Result: 35 tests OK.

## Optional Future Refinements

These are intentionally not blockers for Iterations 5-9.

### Valley Significance Optimization

- [x] Endpoint-role filtering: prefer persistent sinks, high-mass basins, and
      authored/lowered anchors over tiny one-node fragments unless the fragment
      has strong flux or provenance
- [x] Run-relative significance threshold: minimum absolute flux, flux
      percentile, or structurally unique connector exception
- [x] Dominance pruning: suppress weaker alternatives with equal persistence
      and clearly lower flux/bottleneck support
- [ ] Optional module/hierarchy-level endpoint grouping when provenance is
      available
- [x] Bridge ambiguity tiers: bridge-only, bridge-at-endpoint,
      bridge-in-middle, bridge-mixed, and none
- [x] Flux-stability score across checkpoint windows

Result: refinements 1-3 are implemented and recorded in
`outputs/landscape_inference/sessions/S0013`.

- `src/pygrc/landscapes/inference_substrate.py` now emits
  `LandscapeInferencePathFluxStability` with flux series, observed fraction,
  coefficient of variation, stability score, and stability mode.
- `src/pygrc/landscapes/inference_valley.py` now records bridge ambiguity
  tiers, path flux-stability, endpoint-aware significance score, and refined
  ranking reason on valley candidates and emitted valley primitives.
- `src/pygrc/landscapes/inference_pheromone.py` now uses the shared
  flux-stability score when classifying and ranking path-memory markers.

The selected S0012 probe set was rerun as S0013. High-level primitive counts
were unchanged, which means the refinements enriched evidence and ranking
without disrupting the established milestone landscapes. The new bridge tiers
show the expected distinction: GRCV3 paths have no bridge ambiguity, while
GRCL-9V3-derived composite probes expose bridge-at-endpoint, bridge-in-middle,
bridge-mixed, and bridge-only candidate paths.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_substrate \
  tests.landscapes.test_landscape_inference_valley \
  tests.landscapes.test_landscape_inference_pheromone
```

Result: 18 tests OK.

### Pheromone Revival Probe

- [x] Build or reuse long-window collapse/revival artifacts where a collapsed
      or de-emphasized node can regain activity
- [ ] Run matched variants with and without pheromone/path-memory policy
      feedback once geometry crawlers or policy hooks exist
- [x] Measure revival candidates and path-memory association as a read-only
      diagnostic
- [x] Verify pheromone markers still remain `valley` primitives and do not
      become identity-basin claims
- [x] Record replay commands and comparison artifacts under
      `outputs/landscape_inference/sessions/S0014`

Result: the read-only revival probe is implemented and recorded in
`outputs/landscape_inference/sessions/S0014`.

- Added `src/pygrc/landscapes/inference_revival.py`.
- The probe groups `choice_detected` and `collapse` emphasis events by primary
  node, measures checkpoint-local activity after emphasis, and associates
  revived nodes with emitted pheromone path-memory markers when path evidence
  exists.
- The probe is explicitly diagnostic. It does not apply runtime path-memory
  feedback, does not prove suppression or delay, and does not promote
  pheromone markers to identity basins.
- S0014 ran three artifacts:
  - GRC9V3 `corrected_multi_center_delayed_collapse_learning`: 4 monitored
    nodes, 1 revival candidate, 4 path-memory-associated candidates.
  - GRCV3 mediated spill branch probe: 6 monitored nodes, 3 revival
    candidates, 1 path-memory-associated candidate.
  - GRC9 long-window developed-basin collapse artifact: 0 candidates because
    no event rows are present; this is an availability/negative case.

Verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_landscape_inference_revival
```

Result: 3 tests OK.

## Closeout Criteria

- [x] Plan and checklist are linked from `ImplementationPhases.md`
- [x] Reference/user guide is linked from `ImplementationPhases.md`
- [x] At least one inferred `LandscapeSeed` artifact exists
- [x] At least basin and valley classifiers are implemented
- [x] Authored-vs-observed comparison exists
- [x] Observer-only boundary is tested
- [x] Dynamic KG interpretation is documented as an application/export view
- [x] Replayable milestone sessions are recorded

Closeout status: complete.

Evidence:

- `outputs/landscape_inference/sessions/S0012` contains observed
  `LandscapeSeed` artifacts, authored-vs-observed comparisons, and dynamic KG
  views for four selected probes.
- `outputs/landscape_inference/sessions/S0013` reruns the same probe set with
  valley significance, bridge ambiguity, and path flux-stability refinements.
- `outputs/landscape_inference/sessions/S0014` records the read-only pheromone
  revival diagnostic over existing long-window artifacts.
- `docs/reference/LandscapeInference-ReferenceGuide.md` is the operator-facing
  capability, parameter, script, and API guide.

Final verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests/landscapes -p 'test_landscape_inference*.py'
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_import_smoke
```
