# Motion Implementation Checklist

This checklist tracks the inference layer that observes motion across RC/GRC
systems.

Companion plan:

- [`Motion-ImplementationPlan.md`](./Motion-ImplementationPlan.md)
- [`Motion-ReferenceGuide.md`](../docs/reference/Motion-ReferenceGuide.md)

## Ground Rules

- Motion is inferred from runtime evidence.
- Do not source-inject a claim that an identity moved.
- Reuse landscape inference substrates and vocabulary.
- Do not introduce a parallel motion ontology.
- Do not mutate runtime state, topology, coherence, flux, budget, source
  registries, or lowering registries.
- Distinguish coherence motion, representative motion, identity motion,
  boundary motion, and topological motion.
- Treat graph nodes as carriers, not automatically as identities.
- Do not equate identity preservation with stable node ids.
- Do not equate representative change with identity death.
- Do not claim Euclidean movement without coordinates or embedding evidence.
- Use checkpoint series for local motion claims.
- Treat step rows and run summaries as triage/fallback evidence unless local
  evidence is present.
- Keep temporal motion relationships distinct from authored-vs-observed
  landscape comparison relationships.
- Reuse landscape inference classifiers and substrates where they already
  exist; do not build parallel ridge/path/event classifiers for motion.

## Iteration 1. Contract And Definitions

Status: complete.

### Goal

Define the motion-inference contract and vocabulary before implementation.

### Checks

- [x] Define contract version `motion_inference_iter1_v1`
- [x] Define motion kinds:
  - `coherence`
  - `representative`
  - `identity`
  - `boundary`
  - `topological`
- [x] Define relationship labels:
  - `stationary`
  - `drifted`
  - `walked`
  - `split`
  - `merged`
  - `collapsed`
  - `dissolved`
  - `emerged`
  - `ambiguous`
- [x] Define carrier fields:
  - old node ids
  - new node ids
  - old basin ids
  - new basin ids
  - old edge/path ids
  - new edge/path ids
- [x] Define evidence fields:
  - checkpoint ids
  - step window
  - mass overlap
  - flux support
  - continuity delta
  - successor-map continuity
  - hierarchy/provenance continuity
  - topology mutation events
  - these semantic quantities are recorded as compact evidence references,
    classifier summaries, or `telemetry_fields`, not as copied runtime vectors
    or full graph state
- [x] Define confidence scoring fields
- [x] Define confidence range `[0.0, 1.0]`
- [x] Define evidence quality labels:
  - `strong`
  - `partial`
  - `degraded`
  - `missing_surface`
  - `diagnostic_only`
- [x] Define non-claim fields
- [x] Define JSON-safe `MotionRecord` shape
- [x] Require `classifier_id` on every motion record
- [x] Require `classifier_version` on every motion record
- [x] Require `authority = observed` on every motion record
- [x] Require per-record step/time metadata
- [x] Define `competing_claims` for identity motion records
- [x] Define top-level motion report shape
- [x] Define optional `extensions.motion_inference` payload for inferred
      `LandscapeSeed` exports
- [x] Verify `extensions.motion_inference` can coexist with
      `extensions.landscape_inference`
- [x] State that Lorentzian/proper-time motion is out of scope for the
      baseline track
- [x] State that FRC scale-indexed motion is out of scope for the baseline
      track
- [x] State that observer-local partial-graph motion is a future extension
- [x] Distinguish temporal motion labels from authored-vs-observed comparison
      labels

### Verification

- [x] Contract serializes deterministically
- [x] Contract rejects runtime-state smuggling
- [x] Contract does not add new `LandscapeSeed` primitive types
- [x] Relationship labels are distinct from source-authored outcomes
- [x] Motion schema contains classifier provenance and evidence-quality fields
- [x] Confidence thresholds are deterministic and documented

### Summary

Implemented `src/pygrc/landscapes/motion.py` with the Iteration 1 motion
contract:

- constants for motion kinds, relationship labels, evidence-quality labels,
  runtime families, checkpoint spacing, and confidence thresholds
- typed records for `MotionWindow`, `MotionCarrierSet`, `MotionEvidence`,
  `MotionCompetingClaim`, `MotionRecord`, `MotionReport`, and
  `MotionPrimitiveExtension`
- deterministic JSON-safe mapping helpers
- `LandscapeSeed` extension validation for `extensions.motion_inference`
- package exports from `pygrc.landscapes`

The contract keeps motion observer-only: every emitted motion record has
`authority = observed`; non-stationary identity motion records require
competing-claim metadata; and runtime-state smuggling is rejected in reports,
records, evidence, and primitive extensions.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_contract`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_landscape_inference_contract tests.landscapes.test_motion_contract`

Post-Iteration 3 clarification:

- added the explicit `degraded` confidence threshold so budget-leak or
  corrupted-surface evidence is distinct from `diagnostic_only` short-window
  evidence
- documented confidence thresholds and provisional classifier parameters in
  `Motion-ImplementationPlan.md`; current fixed values are implementation
  defaults, not theory-derived constants

## Iteration 2. Motion Window Loader

Status: complete.

### Goal

Reuse landscape inference artifact loading and checkpoint evidence substrate to
build deterministic motion windows.

### Checks

- [x] Load telemetry/checkpoint artifacts from a session root
- [x] Reuse landscape inference window policies:
  - explicit step range
  - final `N` checkpoints
  - event-centered window
  - whole checkpoint series
- [x] Require at least two checkpoints for motion claims
- [x] Mark persistence-sensitive windows with fewer than three checkpoints as
      diagnostic-only
- [x] Record checkpoint spacing:
  - step index delta
  - runtime time delta when available
  - ordinal-only when time is unavailable
- [x] Normalize per-checkpoint node coherence
- [x] Normalize per-checkpoint edge flux
- [x] Normalize per-checkpoint continuity deltas when available
- [x] Normalize per-checkpoint basin membership
- [x] Normalize per-checkpoint representative candidates
- [x] Normalize node/edge birth and removal
- [x] Preserve provenance/lowering tags when available
- [x] Preserve graph coordinates when available
- [x] Preserve GRC9/GRC9V3 port overlays when available

### Verification

- [x] Missing checkpoint series produces explicit `unavailable` status
- [x] Single-checkpoint windows cannot produce strong motion claims
- [x] Irregular checkpoint spacing is recorded and does not silently produce
      uniform-velocity claims
- [x] Loader output is deterministic on repeated runs
- [x] Loader remains read-only

### Summary

Implemented `src/pygrc/landscapes/motion_loader.py` with the Iteration 2
motion window loader:

- reuses the landscape inference artifact loader and checkpoint evidence
  substrate rather than introducing a separate session reader
- builds deterministic `MotionWindow` records from checkpoint series, explicit
  step ranges, final-window selection, or event-centered windows
- normalizes compact checkpoint node evidence: coherence, basin membership,
  basin mass, representative candidates, continuity deltas, coordinates,
  centroid/medoid-representative capability flags, provenance availability,
  and port-overlay availability
- normalizes compact checkpoint edge evidence: endpoints, signed flux,
  conductance, provenance availability, and lowered bridge-edge flags
- records topology deltas between adjacent checkpoints as node/edge births and
  removals
- records checkpoint spacing as regular, irregular, ordinal-only, unknown, or
  unavailable
- exposes a direct quadrature mode for downstream budget/coherence observers:
  checkpoint weight, unit measure, unit measure assumed, or unavailable
- marks missing or single-checkpoint inputs as unavailable for motion claims and
  marks two-checkpoint persistence-sensitive windows as diagnostic-only

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

## Iteration 3. Coherence Motion Observer

Status: complete.

### Goal

Infer coherence transfer across graph carriers without claiming identity
motion.

### Checks

- [x] Compute node coherence deltas across adjacent checkpoints
- [x] Compute edge-supported transfer candidates from flux
- [x] Compare continuity deltas against observed coherence deltas
- [x] Track budget preservation or leak status
- [x] Reuse landscape-inference budget audit helpers when available
- [x] Record quadrature mode:
  - checkpoint weights
  - unit measure
  - unit measure assumed
  - unavailable
- [x] Define budget leak threshold and confidence degradation rule
- [x] Compute graph approximation of basin drift velocity when basin evidence
      is available
- [x] Emit `coherence` motion records
- [x] Distinguish direct edge transfer from ambiguous multi-edge transfer
- [x] Support GRCV3, GRC9, and GRC9V3 when fields are available

### Verification

- [x] Coherence transfer example produces a `coherence` motion record
- [x] Zero-flux control does not produce a false positive
- [x] Budget leak produces degraded confidence
- [x] Identity fields are not required for coherence motion
- [x] Drift-velocity output is unavailable/degraded when required basin or flux
      evidence is missing

### Summary

Implemented `src/pygrc/landscapes/motion_coherence.py` with the Iteration 3
coherence-motion observer:

- consumes `MotionWindowLoadResult` or loads a motion window directly from a
  telemetry artifact root
- compares adjacent checkpoint node coherence values to identify losing and
  gaining carriers
- requires signed edge-flux support for direct carrier-to-carrier transfer
  records, avoiding false positives in zero-flux controls
- emits ambiguous `coherence` records when transfer is supported only by
  multi-edge or indirect flux evidence
- compares available continuity deltas against observed coherence deltas and
  degrades confidence when they disagree or are missing
- reuses landscape-inference checkpoint budget audits, records quadrature mode,
  and degrades confidence on budget leak evidence
- estimates basin drift velocity from coherence-weighted checkpoint coordinates
  when basin membership and coordinates are available
- emits observer-only `MotionRecord` and `MotionReport` payloads with explicit
  non-claims that node carriers are not identity-motion evidence

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_coherence tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

Provisional parameters used by this observer:

| Parameter | Value |
|---|---:|
| `min_coherence_delta` | `1e-9` |
| `min_flux_support` | `1e-12` |
| `budget_leak_threshold` | `1e-9` |
| `continuity_tolerance` | `1e-6` |
| direct-transfer confidence base | `0.85` |
| ambiguous-transfer confidence base | `0.55` |
| diagnostic-only confidence cap | `0.25` |
| budget-leak confidence cap | `0.45` |
| generic degradation confidence cap | `0.65` |

These are recorded as provisional classifier defaults pending calibration from
reviewed motion evidence sessions.

## Iteration 4. Representative Motion Observer

Status: complete.

### Goal

Track representative changes for basins and identity candidates.

### Checks

- [x] Identify representative candidates per checkpoint:
  - sink node
  - peak coherence node
  - centroid when coordinates exist
  - graph medoid proxy when coordinates are absent
  - port/front representative for GRC9/GRC9V3
- [x] Track representative stability across a motion window
- [x] Emit `representative` motion records
- [x] Distinguish representative drift from identity walking
- [x] Record representative selection mode
- [x] Record candidate identity-continuity evidence for later identity matcher
      consumption

### Verification

- [x] Stable representative records `stationary`
- [x] Representative switch records `drifted` or `ambiguous` until the
      identity matcher confirms `walked`
- [x] Missing coordinates falls back to graph proxy, not Euclidean claims
- [x] Representative motion does not imply identity preservation by itself

### Summary

Implemented `src/pygrc/landscapes/motion_representative.py` with the Iteration
4 representative-motion observer:

- consumes `MotionWindowLoadResult` or loads a motion window directly from a
  telemetry artifact root
- groups nodes by basin id when available, with node-local fallback groups
- selects representatives deterministically by sink, centroid-nearest node,
  peak coherence, GRC9/GRC9V3 port/front candidate, graph medoid proxy, then
  lowest-node-id fallback
- records checkpoint-local representative selections with selection mode,
  candidate modes, member node ids, and evidence quality
- compares adjacent checkpoint selections and emits `representative`
  `stationary` or `drifted` motion records
- explicitly records non-claims that representative changes are not identity
  walking and are not identity-motion claims
- degrades confidence for graph-medoid or fallback evidence and caps
  diagnostic-only windows

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_representative tests.landscapes.test_motion_coherence tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

Provisional parameters used by this observer:

| Parameter | Value |
|---|---:|
| stable-representative confidence base | `0.80` |
| representative-drift confidence base | `0.70` |
| ambiguous/degraded confidence cap | `0.55` |
| partial-representative confidence cap | `0.65` |
| diagnostic-only confidence cap | `0.25` |

These are recorded as provisional classifier defaults pending calibration from
reviewed motion evidence sessions.

## Iteration 5. Identity Continuity Matcher

Status: complete.

### Goal

Infer identity preservation and identity walking across changing carriers.

### Checks

- [x] Match old/new basins by mass overlap
- [x] Match old/new representatives by flux-supported path
- [x] Match old/new identities by successor-map continuity
- [x] Use hierarchy/provenance continuity when available
- [x] Resolve competing continuity claims deterministically
- [x] Record competing continuity claims on identity motion records
- [x] Emit identity relationships:
  - `stationary`
  - `drifted`
  - `walked`
  - `split`
  - `merged`
  - `collapsed`
  - `dissolved`
  - `emerged`
  - `ambiguous`
- [x] Record why a relationship was selected
- [x] Preserve ambiguous cases rather than forcing a label
- [x] Keep temporal identity-motion labels distinct from authored-vs-observed
      comparison labels

### Verification

- [x] Identity walking example changes representative carrier but preserves
      identity continuity
- [x] Split example maps one old identity to multiple new identities
- [x] Merge/collapse example maps multiple old identities to one new identity
- [x] Dissolution example drops below continuity threshold
- [x] Emergence example has no sufficient predecessor

### Summary

Implemented `src/pygrc/landscapes/motion_identity.py` with the Iteration 5
identity-continuity matcher:

- consumes `MotionWindowLoadResult` or loads a motion window directly from a
  telemetry artifact root
- groups checkpoint-local identity candidates by basin id, with node-local
  fallback groups
- reuses the representative selector from Iteration 4 for candidate
  representative continuity
- scores old/new candidate matches by mass overlap, representative continuity,
  representative-to-representative flux/path support, successor continuity,
  and hierarchy/provenance continuity when those compact checkpoint surfaces
  are available
- emits identity relationships: `stationary`, `drifted`, `walked`, `split`,
  `merged`, `collapsed`, `dissolved`, `emerged`, and `ambiguous`
- records competing interpretations on every non-stationary identity record,
  satisfying the Iteration 1 identity-motion contract
- preserves weak continuity as `ambiguous` rather than forcing identity walking
  or identity death
- keeps temporal identity-motion labels distinct from authored-vs-observed
  landscape comparison labels through explicit non-claims

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_identity tests.landscapes.test_motion_representative tests.landscapes.test_motion_coherence tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

Provisional parameters used by this matcher:

| Parameter | Value |
|---|---:|
| one-to-one minimum match score | `0.50` |
| branch minimum match score | `0.20` |
| strong match score | `0.75` |
| mass-overlap weight | `0.40` |
| representative-continuity weight | `0.10` |
| flux-path weight | `0.20` |
| successor-continuity weight | `0.20` |
| hierarchy/provenance weight | `0.10` |
| group-continuity weight | `0.10` |
| collapsed-vs-merged mass ratio | `0.75` |
| minimum path-edge flux | `1e-12` |
| diagnostic-only confidence cap | `0.25` |

These are recorded as provisional classifier defaults pending calibration from
reviewed motion evidence sessions.

Post-review refinement:

- representative-to-representative path support now requires every path edge
  to carry signed-flux magnitude above `1e-12`
- successor and hierarchy/provenance continuity are fractional scores, not
  binary any-hit gates
- identity records inherit checkpoint budget-accountability status when it is
  available
- explicit unit coverage was added for `drifted`, `merged`, proportional
  successor/provenance scoring, and multi-hop path flux validation

## Iteration 6. Boundary And Frontier Motion

Status: complete.

### Goal

Infer motion of basin boundaries, ridges, membranes, and GRC9/GRC9V3 port
frontiers.

### Checks

- [x] Compare basin membership changes across checkpoints
- [x] Reuse existing landscape-inference ridge classifier outputs across
      checkpoints
- [x] Compare ridge classifier outputs across checkpoints
- [x] Compare frontier/port-capacity changes across checkpoints
- [x] Compute or mark unavailable graph approximation of
      `V_n = -partial_t C / ||grad C||`
- [x] Detect boundary advance
- [x] Detect boundary recession
- [x] Detect boundary rupture
- [x] Detect boundary stabilization
- [x] Keep pressure-boundary provenance separate from inferred ridge/membrane
      claims
- [x] Use port overlays for GRC9/GRC9V3 frontier motion

### Verification

- [x] Boundary advance example emits `boundary` motion
- [x] Frontier growth example emits port-front motion
- [x] Global step-row aggregates alone do not produce per-node boundary claims
- [x] Bridge edges are excluded or explicitly flagged
- [x] Static ridge claims are not promoted to boundary motion without temporal
      delta evidence

### Summary

Implemented `src/pygrc/landscapes/motion_boundary.py` with the Iteration 6
boundary/frontier-motion observer:

- consumes `MotionWindowLoadResult` or loads a motion window directly from a
  telemetry artifact root
- extracts checkpoint-local boundary observations from per-node gradient norm,
  tensor anisotropy, and GRC9/GRC9V3 port-front overlays
- compares adjacent checkpoint observations and emits `boundary` motion records
  for boundary advance, recession, rupture, stabilization, and port-frontier
  advance/recession
- uses GRC9/GRC9V3 port-frontier direction consistently: occupied-port gain
  is frontier advance, occupied-port loss is frontier recession
- records basin-membership changes on persistent boundary nodes as
  `boundary_membership_shift` deltas
- computes the graph approximation of
  `V_n = -partial_t C / ||grad C||` with checkpoint runtime-time deltas when
  available, falling back to step deltas only when checkpoint time is missing
- uses the sign of available graph `V_n` to classify persistent geometric ridge
  advance or recession, and otherwise records explicit unavailable reasons
- keeps pressure-boundary/front-capacity provenance separate from inferred
  geometric ridge or membrane claims
- flags incident lowered bridge edges as degraded evidence rather than treating
  them as natural ridge evidence
- ignores global step-row aggregates for per-node boundary claims

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_boundary tests.landscapes.test_motion_identity tests.landscapes.test_motion_representative tests.landscapes.test_motion_coherence tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

Provisional parameters used by this observer:

| Parameter | Value |
|---|---:|
| ridge-gradient threshold | `1.0` |
| ridge-tensor-anisotropy threshold | `1.0` |
| normal-gradient epsilon | `1e-12` |
| stabilization confidence base | `0.78` |
| advance/recession confidence base | `0.70` |
| rupture confidence base | `0.62` |
| diagnostic-only confidence cap | `0.25` |

These are recorded as provisional classifier defaults pending calibration from
reviewed motion evidence sessions.

## Iteration 7. Topological Motion

Status: complete.

### Goal

Classify motion caused by support changes rather than smooth coherence
transport.

### Checks

- [x] Detect node birth
- [x] Detect edge birth
- [x] Detect node removal/pruning
- [x] Detect edge removal/pruning
- [x] Consume `events.jsonl` from the artifact loader when present
- [x] Match topology mutation records to event telemetry by step id
- [x] Prefer event-backed topology evidence over topology-only detection
- [x] Link topology mutations to events:
  - growth
  - spark
  - expansion
  - split
  - collapse
  - merge/prune
- [x] Distinguish topological motion from identity motion
- [x] Record whether identity continuity survived the topology change

### Verification

- [x] Growth example records topological motion
- [x] Spark/expansion example records support refinement
- [x] Collapse example records support contraction or carrier reassignment
- [x] Topology change without identity continuity does not claim identity
      walking
- [x] Topology-only mutation without matching event rows is marked as degraded
      evidence

### Summary

Implemented `src/pygrc/landscapes/motion_topological.py` with the Iteration 7
topological-motion observer:

- consumes `MotionWindowLoadResult` or loads a motion window directly from a
  telemetry artifact root
- reads adjacent checkpoint topology deltas from the Iteration 2 loader
- consumes event rows from the shared artifact loader and matches topology
  mutation events to checkpoint intervals by step id
- emits `topological` motion records for node/edge birth, node/edge removal,
  support refinement, support contraction, support split/merge, support prune,
  and support reconfiguration
- classifies event-backed topology deltas as stronger evidence than
  topology-only deltas
- preserves topology-only deltas as degraded evidence rather than dropping
  them
- supports event-only collapse/carrier-reassignment records when the event row
  indicates topology mutation but adjacent checkpoint carrier ids are stable
- treats event-only topology records as partial evidence because event
  provenance is present but checkpoint-local carrier birth/removal is absent
- maps generic support reassignment/reconfiguration to neutral `stationary`
  rather than the representative/identity `drifted` label
- records `identity_continuity_status` diagnostically and explicitly avoids
  identity-walking claims
- leaves explicit linkage to Iteration 5 identity-motion `motion_id` records
  as a future refinement

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_topological tests.landscapes.test_motion_boundary tests.landscapes.test_motion_identity tests.landscapes.test_motion_representative tests.landscapes.test_motion_coherence tests.landscapes.test_motion_loader tests.landscapes.test_motion_contract`

Provisional parameters used by this observer:

| Parameter | Value |
|---|---:|
| event-backed topology confidence base | `0.82` |
| event-only topology confidence base | `0.62` |
| topology-only confidence base | `0.45` |
| diagnostic-only confidence cap | `0.25` |

These are recorded as provisional classifier defaults pending calibration from
reviewed motion evidence sessions.

Post-review refinement:

- generic support reassignment/reconfiguration no longer uses `drifted`
- split, merge, and prune event-token coverage was added
- event-only confidence semantics were documented as partial evidence, not
  stronger checkpoint-local confirmation

## Iteration 8. Structural Examples

Status: complete.

### Goal

Build replayable examples that demonstrate motion categories before
visualization.

### Checks

- [x] Build coherence transfer example
- [x] Build representative drift example
- [x] Build identity walking example
- [x] Build split/merge/collapse motion example
- [x] Build GRC9 port/frontier motion example
- [x] Build GRC9V3 hybrid motion example
- [x] Build at least one GRC9/GRC9V3 coarse-grained motion diagnostic example
- [x] Record whether each GRC9/GRC9V3 example uses fine or column-coarse
      evidence
- [x] Store repeatable sessions under `outputs/motion/sessions/S####`
- [x] Record commands needed to rerun each example
- [x] Preserve negative controls

### Verification

- [x] Examples are deterministic
- [x] Examples use runtime evidence, not injected outcomes
- [x] Each example has telemetry/checkpoints sufficient for its motion claim
- [x] Failed or ambiguous examples are retained with explanation

### Summary

Implemented `src/pygrc/landscapes/motion_examples.py` with the Iteration 8
structural example runner:

- writes deterministic telemetry/checkpoint artifact packs under
  `outputs/motion/sessions/S0001/runs/<example_name>/...`
- runs the relevant motion observers over those artifacts and stores
  observer reports/summaries beside each telemetry run
- records `evidence_scale` for each example, including fine graph,
  fine graph plus port overlays, and column-coarse diagnostic evidence
- preserves a no-motion negative control with stationary representative and
  identity records but no non-stationary coherence/topological/boundary records
- records `README.md`, `session_manifest.json`, `run_report.json`,
  `rerun.sh`, per-example manifests, and per-example rerun commands

Default replay command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root outputs/motion --session-id S0001
```

Individual examples can be rerun with:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root outputs/motion --session-id S0001 --example identity_walking_control
```

Examples:

| Example | Family | Evidence scale | Primary observers |
|---|---|---|---|
| `coherence_transfer_control` | `grcv3` | fine graph | coherence |
| `representative_drift_control` | `grcv3` | fine graph | representative |
| `identity_walking_control` | `grc9v3` | fine graph | identity |
| `identity_split_control` | `grc9v3` | fine graph | identity, topological |
| `identity_merge_control` | `grc9v3` | fine graph | identity, topological |
| `identity_collapse_control` | `grc9v3` | fine graph | identity, topological |
| `grc9_port_frontier_motion` | `grc9` | fine graph port overlay | boundary |
| `grc9v3_hybrid_refinement_motion` | `grc9v3` | fine graph port overlay | boundary, topological |
| `grc9v3_column_coarse_motion_diagnostic` | `grc9v3` | column-coarse diagnostic | boundary |
| `no_motion_negative_control` | `grcv3` | fine graph | all observers |

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_examples`
- `PYTHONPATH=src ./.venv/bin/python -m unittest discover tests/landscapes`

The generated examples are synthetic runtime evidence surfaces, not
source-authored claims that motion happened. The observer reports are the only
place where motion relationships are inferred.

## Iteration 9. Visualization

Status: complete.

### Goal

Render motion evidence clearly without promoting visuals to runtime proof.

### Checks

- [x] Render old/new representatives
- [x] Render transferred coherence mass
- [x] Render flux arrows
- [x] Render basin overlap
- [x] Render identity walking path
- [x] Render split/merge/collapse relationships
- [x] Render boundary advance/recession
- [x] Render topology births/removals
- [x] Support static two-checkpoint rendering
- [x] Support temporal checkpoint-series rendering or explicitly defer it
- [x] Distinguish observed evidence from source-authored conditions

### Verification

- [x] Visuals link back to motion records
- [x] Visuals link back to source telemetry/checkpoints
- [x] Visuals do not create claims absent from the motion report
- [x] Dense and sparse graph cases remain legible
- [x] Motion trajectories link to record ids and checkpoint ids

### Summary

Implemented `src/pygrc/visualization/motion.py`.

The visualization review consumes Iteration 8 structural-example sessions and
renders one visual directory per example under
`outputs/motion/sessions/<session_id>/visualizations/<example_name>/`.

Each example receives:

- `motion_graph.png`: deterministic two-checkpoint graph overlay with
  old/new carrier highlighting, flux arrows, path/support edges, and a
  dense motion-record panel,
- `motion_timeline.png`: record timeline keyed by step window,
- `motion_visual_summary.json`: motion record ids, checkpoint ids, source
  telemetry paths, report paths, visual status, and explicit
  no-visual-only-promotion metadata.

Topological records receive explicit born/removed/evidence-node highlighting
separate from generic old/new carrier highlighting. Stationary records are
listed in the record panel and timeline but do not color graph carriers as
non-stationary motion.

The default graph layout uses `chart_center_hint` when available and otherwise
falls back to a deterministic circular layout. Dense or structurally specific
examples should provide `chart_center_hint` in checkpoint node payloads for
legible visual review.

Temporal checkpoint-series animation is explicitly deferred; Iteration 9
closes static two-checkpoint rendering and record-linked review artifacts.

Reproduce:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root outputs/motion --session-id S0001
PYTHONPATH=src python -m pygrc.visualization.motion --session-root outputs/motion/sessions/S0001
```

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_motion`

## Iteration 10. Motion Seed Library And Composite Examples

Status: complete.

### Goal

Convert controlled motion observer fixtures into authored seeds where possible,
then build composite runtime examples that produce multiple motion modes in one
run.

Iteration 8 remains the controlled observer-fixture layer. Iteration 10 is the
source-language/runtime-production layer.

### Checks

- [x] Convert the coherence transfer fixture into an authored seed when the
      target family can express the needed flux preconditions
- [x] Convert the representative drift fixture into an authored seed
- [x] Convert the identity walking fixture into an authored seed or document
      why the required continuity preconditions are not source-expressible yet
- [x] Convert split/merge/collapse fixtures into authored seeds where possible
- [x] Convert GRC9/GRC9V3 port-frontier motion fixtures into authored GRCL or
      landscape seeds
- [x] Add composite examples:
  - coherence transfer -> representative drift
  - representative drift -> identity walking
  - spark/expansion -> frontier advance -> topological refinement
  - split -> merge/collapse
  - identity walking plus boundary/frontier motion
- [x] Run authored seeds through runtime, telemetry, motion inference, and
      visualization
- [x] Compare authored conditions against observed motion outputs
- [x] Preserve failed and ambiguous composites with explanations
- [x] Record rerun commands for every authored seed and composite session

### Verification

- [x] Authored seeds do not contain runtime motion outcomes
- [x] Runtime evidence, not source metadata, drives motion records
- [x] Composite examples are replayable
- [x] Composite examples link source seed, telemetry, motion reports, and
      visuals
- [x] Failed composites remain available for future tuning and catalog review

### Summary

Implemented `src/pygrc/landscapes/motion_seed_examples.py`.

Iteration 10 adds a neutral authored motion-seed layer using `LandscapeSeed`
and `extensions.motion_seed`. Source seeds declare preconditions, intended
review modes, projection metadata, and non-claims; they do not declare runtime
motion relationships, motion record ids, telemetry rows, checkpoints, or
transferred mass.

Authored seeds:

- `motion_seed_coherence_transfer`
- `motion_seed_representative_drift`
- `motion_seed_identity_walking`
- `motion_seed_grc9_port_frontier`
- `motion_seed_grc9v3_hybrid_refinement`
- `motion_composite_walk_frontier_refinement`
- `motion_composite_split_merge_collapse`

The first five project controlled source preconditions onto single runtime
evidence examples. The final two are composite runtime projections:

- `motion_composite_walk_frontier_refinement`: identity walking followed by
  frontier/topology refinement; observed relationships include `walked`,
  `split`, `drifted`, `emerged`, and one neutral topological
  `stationary` support reconfiguration.
- `motion_composite_split_merge_collapse`: split, merge, and support
  contraction; identity collapse remains `ambiguous` while topological
  contraction is `collapsed`, preserving the disagreement for catalog review.

The runner writes source seeds under
`configs/landscapes/seed/motion/` as reusable YAML examples, copies session
snapshots under `outputs/motion/sessions/<session_id>/source_seeds/`, writes
projected telemetry under `runs/`, motion reports under `motion_reports/`, and
static visual artifacts under `visualizations/`.

Reproduce:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root outputs/motion --session-id S0002
```

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_seed_examples`

## Iteration 11. Long-Window Composite Motion Evidence

Status: complete.

### Goal

Create longer authored composite projections that require 20+ checkpoints to
achieve their motion patterns, then run them through telemetry, motion
inference, and static visualization.

### Checks

- [x] Compare Iteration 8 controlled observer fixtures against Iteration 10
      authored-seed outputs
- [x] Add long-window composites requiring at least 20 checkpoints
- [x] Identify examples suitable for animated visual review
- [x] Identify examples that need additional source/parameter tuning
- [x] Preserve rejected and ambiguous cases with explicit reasons
- [x] Record family-specific gaps for GRCV3, GRC9, and GRC9V3
- [x] Record whether each motion mode is source-produced, fixture-produced, or
      still diagnostic-only

### Verification

- [x] Review references replayable sessions
- [x] Review distinguishes controlled fixture evidence from authored-seed
      evidence
- [x] Review selects concrete candidates for Iteration 12 animation
- [x] Review does not promote ambiguous evidence into accepted catalog entries

### Summary

Implemented as Iteration 11 long-window mode in
`src/pygrc/landscapes/motion_seed_examples.py`.

The canonical session is `outputs/motion/sessions/S0003`, generated with:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root outputs/motion --session-id S0003 --long-composites
```

Long-window source seeds are also written under
`configs/landscapes/seed/motion/`:

- `motion_long_relay_walk_frontier.seed.yaml`
- `motion_long_split_merge_collapse_cascade.seed.yaml`
- `motion_long_failed_relay_broken_continuity.seed.yaml`
- `motion_long_no_motion_negative_control.seed.yaml`

Results:

- `motion_long_relay_walk_frontier`: 21 checkpoints, 4 delayed identity
  `walked` events, repeated frontier `drifted` records, and repeated
  topological `emerged` support changes. This is the clearest candidate for
  Iteration 12 animation because the motion unfolds as a relay.
- `motion_long_split_merge_collapse_cascade`: 24 checkpoints, delayed split,
  merge, and topological collapse. Identity classification preserves an
  `ambiguous` final collapse relation while topology records `collapsed`,
  matching the shorter Iteration 10 disagreement and keeping it available for
  catalog review.
- `motion_long_failed_relay_broken_continuity`: 21 checkpoints, relay-shaped
  endpoints, but no successor, flux-path, or provenance continuity across the
  handoff. Identity inference records dissolved/emerged evidence rather than
  `walked`.
- `motion_long_no_motion_negative_control`: 21 checkpoints with stable support,
  representative, and frontier state. Stationary identity records are allowed;
  representative and boundary observers emit only `stationary`, and
  topological non-stationary records are absent.

The long-window examples are GRC9V3 because they need identity continuity,
topology mutation, and frontier/boundary evidence together. GRCV3 and GRC9 remain
covered by Iterations 8-10 as simpler controls.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_seed_examples`

## Iteration 11.1. Failed And Negative Long-Window Controls

Status: complete.

### Goal

Close the Iteration 11 review gap by adding explicit failed and negative
long-window authored projections before animated visualization and catalog
review.

### Checks

- [x] Add a failed composite where source-like relay endpoints do not produce
      identity walking evidence
- [x] Add a long-window no-motion negative control
- [x] Verify failed relay does not emit `walked`
- [x] Verify no-motion control has no non-stationary representative,
      boundary, or topological records
- [x] Preserve source/runtime authority boundary and source non-claims
- [x] Document that Iterations 10-11.1 are structural projections, not live
      runtime seed executions

### Verification

- [x] Long-window suite still uses at least 20 checkpoints per seed
- [x] Session records positive, ambiguous, failed, and negative evidence
- [x] Reusable seeds are written under `configs/landscapes/seed/motion/`
- [x] Tests assert relationship outcomes for the failed and negative controls

### Summary

Iteration 11.1 extends the canonical `S0003` long-composite session with two
review controls:

- `motion_long_failed_relay_broken_continuity`
- `motion_long_no_motion_negative_control`

The failed relay records why relay-shaped source preconditions are insufficient
without continuity evidence. The stable negative control prevents the catalog
from confusing long observation windows with motion by default.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_seed_examples tests.visualization.test_motion`

## Iteration 12. Graph-Engine Animated Motion Visualization

Status: complete.

### Goal

Reuse the existing graph visualization engine, including checkpoint sequence
and animation support, to render motion as a live multi-checkpoint process.

Iteration 9 closes static two-checkpoint visualization. Iteration 12 extends
that work to graph-engine-backed sequence figures, HTML views, and animations
with motion overlays.

### Checks

- [x] Reuse `pygrc.visualization.graph_render` layout machinery where possible
- [x] Reuse graph sequence/contact-sheet rendering where possible
- [x] Reuse GIF animation output where possible
- [x] Render old/new representatives across more than two checkpoints
- [x] Animate coherence transfer and flux arrows when checkpoint cadence
      supports it
- [x] Animate identity walking paths
- [x] Animate split/merge/collapse support changes
- [x] Animate topology births/removals
- [x] Animate boundary/frontier advance and recession
- [x] Preserve deterministic layout across frames
- [x] Store frame/checkpoint-to-motion-record linkage metadata
- [x] Preserve `no_visual_only_promotion`

### Verification

- [x] Animated visuals reference motion record ids
- [x] Animated visuals reference checkpoint ids for every frame
- [x] Animated visuals do not create claims absent from motion reports
- [x] Two-checkpoint examples degrade to two-frame diagnostics
- [x] Longer examples render as multi-frame sequences
- [x] Dense examples remain legible or document layout limitations

### Summary

Implemented in `src/pygrc/visualization/motion.py` as
`render_motion_animated_visual_session(...)` and CLI flag `--animated`.

The animated renderer keeps the Iteration 9 static surfaces and adds graph
engine-backed sequence/animation outputs plus motion-overlay frames and GIFs.
It reuses `pygrc.visualization.graph_render` for deterministic union layout,
graph checkpoint contact sheets, HTML, and graph animation, then renders
motion-specific overlays with active motion records per frame.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.visualization.motion --session-root outputs/motion/sessions/S0003 --animated
```

Per-example animated outputs:

- `graph_engine/graph_sequence.png`
- `graph_engine/graph_animation.gif`
- `graph_engine/graph_html/final_graph.html`
- `motion_frames/frame_*.png`
- `motion_sequence.png`
- `motion_animation.gif`
- `motion_animated_summary.json`

The canonical `S0003` animated review renders four long-window examples:

- `motion_long_relay_walk_frontier`
- `motion_long_split_merge_collapse_cascade`
- `motion_long_failed_relay_broken_continuity`
- `motion_long_no_motion_negative_control`

Static and animated views now coexist. Static views remain compact
record-inspection artifacts; animated views show the multi-checkpoint temporal
unfolding and preserve frame-to-checkpoint-to-motion-record linkage.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_motion`

## Iteration 12.1. Motion Review Of Complex Landscape-Inference Examples

Status: complete.

### Goal

Reuse the complex Landscape Inference examples as motion evidence windows and
render the resulting motion records statically and as animations.

### Checks

- [x] Consume a Landscape Inference `session_manifest.json`
- [x] Reuse selected seed `artifact_root` telemetry/checkpoint artifacts
- [x] Run motion observers over each selected landscape example
- [x] Preserve Landscape Inference claims separately from Motion Inference
      claims
- [x] Write motion reports without creating new landscape primitive claims
- [x] Render static motion review surfaces
- [x] Render graph-engine-backed animated motion surfaces
- [x] Support dense real-session record counts without unbounded timeline
      figures
- [x] Record canonical commands and selected examples

### Verification

- [x] Bridge tests run without relying on checked-in large output folders
- [x] Bridge-style `runs` are accepted by the motion visualizer
- [x] Canonical S0013 bridge produces replayable S0004 motion session
- [x] Animated visuals reference checkpoint ids and motion record ids

### Summary

Implemented `src/pygrc/landscapes/motion_landscape_bridge.py`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge --landscape-manifest outputs/landscape_inference/sessions/S0013/session_manifest.json --output-root outputs/motion --session-id S0004
```

Selected Landscape Inference examples:

- `corrected_propagated_front_relay`
- `corrected_hybrid_full_composition`
- `grcv3_mediated_spill_branch_single_intermediate_probe`
- `corrected_multi_center_delayed_collapse_learning`

The bridge writes motion reports under each reused runtime artifact root and
stores the bridge session under `outputs/motion/sessions/S0004`. Static and
animated motion visuals are written under
`outputs/motion/sessions/S0004/visualizations`.

Dense real-session outputs can contain hundreds or thousands of motion records;
the timeline renderer now samples dense timelines while preserving complete
record ids and motion report linkage in JSON summaries.

Observed S0004 motion summary:

- `corrected_propagated_front_relay`: 101 checkpoints. Landscape inference
  found 70 primitives; motion inference found coherence drift, 1,374
  split-style identity records, 32 boundary/frontier drift records, 3 boundary
  emergence records, and 4 topological emergence records. Dense identity,
  representative, and boundary timelines are sampled in the visual panels.
- `corrected_hybrid_full_composition`: 4 checkpoints. Landscape inference
  found 133 primitives; motion inference found coherence drift, 39
  split-style identity records, 44 boundary drift records, and 1 topological
  emergence record.
- `grcv3_mediated_spill_branch_single_intermediate_probe`: 13 checkpoints.
  Landscape inference found 72 primitives; motion inference found 314
  coherence-drift records, 129 split-style identity records, and topological
  split/dissolve records. Boundary motion is absent because this GRCV3 artifact
  does not expose the GRC9/GRC9V3 port/frontier evidence surface.
- `corrected_multi_center_delayed_collapse_learning`: 21 checkpoints.
  Landscape inference found 85 primitives; motion inference found coherence
  drift, repeated split-style identity records, boundary drift, and 2
  topological collapse records.

Readable result artifacts:

- `outputs/motion/sessions/S0004/landscape_motion_summary.json`
- `outputs/motion/sessions/S0004/landscape_motion_summary.md`
- `outputs/motion/sessions/S0004/visualizations/animated_visual_manifest.json`

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_landscape_bridge tests.visualization.test_motion`

## Iteration 12.2. Motion Interpretation And Calibration

Status: complete.

### Goal

Interpret the Iteration 12.1 complex landscape-motion bridge outputs before
catalog closeout. This iteration converts raw observer counts into
catalog-preparation labels without creating new landscape, source, runtime, or
visual-only claims.

### Checks

- [x] Read existing `landscape_motion_summary.json` artifacts
- [x] Preserve the no-new-motion-record claim boundary
- [x] Produce accepted / ambiguous / diagnostic evidence labels
- [x] Flag dense identity split overproduction for catalog review
- [x] Flag GRCV3 boundary/frontier family limitations
- [x] Record knowledge-graph motion interpretation using the same landscape
      vocabulary
- [x] Write machine-readable and human-readable interpretation artifacts
- [x] Record canonical command and artifact paths

### Verification

- [x] Interpretation tests cover accepted coherence evidence
- [x] Interpretation tests cover dense identity split calibration
- [x] Interpretation tests cover GRCV3 family-limited boundary evidence
- [x] Canonical S0004 interpretation artifacts are generated
- [x] Interpretation reads existing summaries only

### Summary

Implemented `src/pygrc/landscapes/motion_interpretation.py`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation --session-root outputs/motion/sessions/S0004
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/motion_interpretation_summary.json`
- `outputs/motion/sessions/S0004/interpretation/motion_interpretation.md`
- `outputs/motion/sessions/S0004/interpretation/knowledge_graph_motion_case_study.md`

Observed interpretation:

- Coherence drift is the most stable cross-family motion signal.
- GRC9V3 port/frontier evidence makes boundary motion visible in complex
  landscape examples.
- Topological emergence/collapse is accepted as topology evidence when present.
- Dense identity windows currently overproduce split-style carrier records; the
  records are useful diagnostics, but catalog review must distinguish carrier
  branching from accepted identity fission.
- GRCV3 boundary motion is family-limited in this pass because the required
  port/frontier surface is absent.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_interpretation tests.landscapes.test_motion_landscape_bridge`

## Iteration 12.3. Dense-Window Motion Calibration

Status: complete.

### Goal

Convert the dense identity split caveat from Iteration 12.2 into a catalogable
calibration rule before closeout. Raw motion records remain unchanged; the
calibration only summarizes how to treat dense split-dominant windows.

### Checks

- [x] Read existing Iteration 12.2 interpretation summaries
- [x] Preserve raw identity motion records unchanged
- [x] Detect dense windows by total/identity record count
- [x] Detect identity split dominance by split ratio
- [x] Detect stationary-representative / branching-identity context
- [x] Emit catalog guidance for dense carrier branching
- [x] Keep accepted identity fission gated on future membership/provenance
      linkage
- [x] Write machine-readable and human-readable dense calibration artifacts

### Verification

- [x] Dense-window tests cover dense split-dominant identity output
- [x] Dense-window tests cover small split-dominant windows as review cases
- [x] Canonical S0004 dense calibration artifacts are generated
- [x] Calibration reads existing interpretation only

### Summary

Implemented dense-window calibration in
`src/pygrc/landscapes/motion_interpretation.py`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation --session-root outputs/motion/sessions/S0004 --dense-calibration
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/dense_window_calibration_summary.json`
- `outputs/motion/sessions/S0004/interpretation/dense_window_calibration.md`

Default thresholds:

- dense window: total motion records `>= 500` or identity records `>= 500`
- split dominance: identity `split` ratio `>= 0.80`
- stationary-representative context: representative `stationary` ratio
  `>= 0.80` while split dominance holds

Catalog rule:

- Dense split-dominant identity records are cataloged as carrier branching
  diagnostics, not accepted identity fission.
- Accepted identity fission requires a later membership/provenance linkage pass.
- Small split-dominant windows remain review cases rather than dense-window
  evidence.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_interpretation tests.landscapes.test_motion_landscape_bridge`

## Iteration 12.4. Identity Fission Promotion Gate

Status: complete.

### Goal

Implement the membership/provenance linkage pass needed to promote dense
carrier-branching diagnostics into accepted identity-fission candidates when
the evidence is strong enough.

### Checks

- [x] Read existing dense-window calibration artifacts
- [x] Read existing identity motion reports and summaries
- [x] Preserve raw identity motion records unchanged
- [x] Require compact daughter membership
- [x] Require strong confidence and strong evidence quality
- [x] Require positive transferred mass
- [x] Require provenance continuity to at least two daughter groups
- [x] Reject broad fan-out split records as carrier-branching diagnostics
- [x] Write promotion audit artifacts for catalog closeout

### Verification

- [x] Unit test promotes a compact provenance-linked split
- [x] Unit test rejects broad fan-out split records
- [x] Canonical S0004 promotion artifacts are generated
- [x] Promotion reads existing reports only

### Summary

Implemented identity-fission promotion in
`src/pygrc/landscapes/motion_interpretation.py`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation --session-root outputs/motion/sessions/S0004 --dense-calibration --promote-identity-fission
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/identity_fission_promotion_summary.json`
- `outputs/motion/sessions/S0004/interpretation/identity_fission_promotion.md`

Default promotion gates:

- compact daughters: `2 <= daughter_count <= 4`
- confidence: `>= 0.80`
- evidence quality: `strong`
- transferred mass: positive
- provenance continuity: at least two daughter matches with
  `hierarchy_provenance_continuity >= 0.75`

Observed S0004 result:

- No dense S0004 identity split records were promoted to accepted identity
  fission.
- The dense windows are confirmed as carrier-branching diagnostics because the
  split records are broad fan-out records and/or below the strong promotion
  threshold.
- This closes the 12.3 caveat for catalog purposes: S0004 dense identity splits
  should be cataloged as branching diagnostics, not accepted fission.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_interpretation tests.landscapes.test_motion_landscape_bridge`

## Iteration 12.5. Confirmed Dense Fission Seed Composition

Status: complete.

### Goal

Add a positive dense fission composition that passes the Iteration 12.4
promotion gate, while preserving the 12.3/12.4 rule that broad fan-out split
fields are diagnostic rather than automatically accepted as identity fission.

### Checks

- [x] Add authored dense fission seed under
      `configs/landscapes/seed/motion/`
- [x] Add dense fission projection to
      `pygrc.landscapes.motion_seed_examples`
- [x] Keep source seed authority limited to preconditions and non-claims
- [x] Generate dense runtime evidence over a long checkpoint sequence
- [x] Avoid the same-step all-pairs matcher pathology by composing density
      over time
- [x] Write `landscape_motion_summary.json` for seed-example sessions so
      interpretation passes can consume them
- [x] Run dense-window calibration on the dense fission session
- [x] Run identity-fission promotion on the dense fission session
- [x] Record the matcher performance boundary as future work for genuinely
      huge same-step fission fields

### Verification

- [x] Unit test confirms the dense seed promotes identity fission
- [x] Canonical S0005 session is generated
- [x] Canonical S0005 promotion artifacts are generated
- [x] S0005 promotes 501 compact provenance-linked fission candidates
- [x] Existing motion seed and interpretation tests still pass

### Summary

Implemented dense confirmed fission support in
`src/pygrc/landscapes/motion_seed_examples.py`.

Reusable seed:

- `configs/landscapes/seed/motion/motion_dense_confirmed_fission.seed.yaml`

Canonical commands:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root outputs/motion --session-id S0005 --dense-fission --no-visuals
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation --session-root outputs/motion/sessions/S0005 --dense-calibration --promote-identity-fission
```

Written artifacts:

- `outputs/motion/sessions/S0005/landscape_motion_summary.json`
- `outputs/motion/sessions/S0005/interpretation/dense_window_calibration_summary.json`
- `outputs/motion/sessions/S0005/interpretation/identity_fission_promotion_summary.json`
- `outputs/motion/sessions/S0005/interpretation/identity_fission_promotion.md`

Observed S0005 result:

- 501 reviewed split records
- 501 compact candidates
- 501 provenance-supported candidates
- 501 promoted identity-fission candidates
- promoted key: `motion_dense_confirmed_fission`

Performance note:

- 12.5 addresses the slow naive 501-parent case at the composition layer. The
  confirmed dense session is dense over time, with compact fission motifs in
  adjacent checkpoint windows.
- The identity matcher same-step performance issue is resolved by Iteration
  12.6.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_seed_examples tests.landscapes.test_motion_interpretation`
- `PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/motion_seed_examples.py tests/landscapes/test_motion_seed_examples.py`

## Iteration 12.6. Sparse Identity Matcher For Dense Same-Step Fields

Status: complete.

### Goal

Make dense same-step fission fields tractable by replacing all-old-groups by
all-new-groups identity matching with sparse evidence-indexed candidate
generation.

### Checks

- [x] Build candidate old/new edges from explicit continuity evidence
- [x] Use shared node ids as candidate evidence
- [x] Use successor-node linkage as candidate evidence
- [x] Use hierarchy-parent linkage as candidate evidence
- [x] Use provenance-token linkage as candidate evidence
- [x] Use representative-node continuity as candidate evidence
- [x] Use flux-reachable support as candidate evidence
- [x] Score only sparse candidate edges
- [x] Treat pairs without candidate evidence as unmatched
- [x] Preserve split/merge/collapse/walk/dissolve/emerge behavior
- [x] Emit matcher diagnostics in identity summaries
- [x] Add dense same-step fission regression coverage
- [x] Regenerate S0005 artifacts with matcher diagnostics

### Verification

- [x] Dense same-step test uses 501 old parent groups and 1002 daughter groups
- [x] Dense same-step test emits 501 split records
- [x] Dense same-step test avoids more than 500000 all-pairs comparisons
- [x] Existing identity matcher tests still pass
- [x] Existing dense seed and promotion tests still pass

### Summary

Implemented sparse evidence-indexed matching in
`src/pygrc/landscapes/motion_identity.py`.

The matcher now builds candidate old-to-new group edges only from local
continuity evidence:

- same group id
- shared node
- successor node
- hierarchy parent
- provenance token
- representative node
- flux-reachable support

It then computes the full match score only for those candidate edges. This
keeps the relationship semantics unchanged while avoiding expensive scoring of
unrelated old/new group pairs.

Regression result:

- old parent groups: `501`
- new daughter groups: `1002`
- naive all-pair comparisons: `502002`
- sparse candidate edges scored: `1002`
- all-pair comparisons avoided: `501000`
- emitted split records: `501`

Identity summaries now include `matcher_diagnostics` with aggregate and
per-checkpoint-pair counts:

- `candidate_generation_mode`
- `all_pair_count_total`
- `candidate_edge_count_total`
- `scored_pair_count_total`
- `all_pair_count_avoided_total`
- `candidate_reason_counts`

Canonical S0005 was regenerated after the matcher change. It still promotes
501 compact provenance-linked identity-fission candidates, and its identity
summary now records sparse matcher diagnostics.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_identity tests.landscapes.test_motion_seed_examples tests.landscapes.test_motion_interpretation`
- `PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/motion_identity.py tests/landscapes/test_motion_identity.py`

## Iteration 13. Reviewed Motion Catalog

Status: complete.

### Goal

Close the initial motion track with a reviewed catalog of accepted, rejected,
and ambiguous examples after controlled examples, authored seeds, composite
runs, static visuals, and animated visuals have all been reviewed.

### Checks

- [x] Create reviewed motion catalog artifact
- [x] Record accepted examples
- [x] Record rejected examples
- [x] Record ambiguous examples
- [x] Record family limitations:
  - GRCV3
  - GRC9
  - GRC9V3
- [x] Record authored-seed and composite-session outcomes
- [x] Record static and animated visual artifact references
- [x] Record remaining theory/runtime gaps
- [x] Add usage notes for future landscape crawlers and knowledge-graph
      exports

### Verification

- [x] Catalog references replayable sessions
- [x] Catalog references visual artifacts where available
- [x] Catalog distinguishes coherence motion from identity motion
- [x] Catalog distinguishes inferred motion from source-authored conditions
- [x] Catalog records which examples are fixture-backed vs. authored-seed-backed
- [x] Catalog includes animated visual evidence where available

### Summary

Implemented `src/pygrc/landscapes/motion_catalog.py` with canonical catalog
session `S0006`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_catalog --output-root outputs/motion --session-id S0006
```

Written artifacts:

- `outputs/motion/sessions/S0006/session_manifest.json`
- `outputs/motion/sessions/S0006/reviewed_motion_catalog.json`
- `outputs/motion/sessions/S0006/reviewed_motion_catalog.md`

Observed S0006 catalog counts:

- total entries: `26`
- accepted: `17`
- negative controls: `2`
- ambiguous: `2`
- diagnostic: `4`
- rejected: `1`
- runtime families: `grc9: 2`, `grc9v3: 18`, `grcv3: 6`
- source sessions: `S0001: 10`, `S0002: 7`, `S0003: 4`,
  `S0004: 4`, `S0005: 1`

Catalog decisions:

- S0001 controlled observer fixtures are accepted for their explicit motion
  kind, with no source-language claim.
- S0002 authored seed projections are accepted where runtime evidence matches
  the source preconditions; the split/merge/collapse composite remains
  ambiguous because identity and topology disagree.
- S0003 accepts the long relay/frontier composite, preserves the
  split/merge/collapse cascade as ambiguous, accepts the no-motion negative
  control, and rejects the broken-continuity relay as an identity-walking
  failure.
- S0004 complex Landscape Inference bridge results remain diagnostic for
  identity fission. Dense branching is cataloged as
  `keep_dense_branching_diagnostic_not_identity_fission`.
- S0005 is accepted as the positive dense identity-fission case:
  `motion_dense_confirmed_fission` promotes 501 compact provenance-linked
  fission candidates.

All catalog artifact paths were checked after generation; no missing referenced
paths were found.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_motion_catalog`
- `PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/motion_catalog.py tests/landscapes/test_motion_catalog.py src/pygrc/landscapes/__init__.py`
