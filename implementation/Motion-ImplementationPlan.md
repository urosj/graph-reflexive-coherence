# Motion Implementation Plan

## Purpose

This document defines the implementation track for **motion** in RC/GRC
systems.

Motion is not a new runtime family and not a source-language outcome. It is an
inferred temporal relationship over existing runtime evidence:

```text
runtime evolution
-> telemetry/checkpoints
-> landscape inference
-> motion inference
```

The purpose is to make explicit what it means for coherence, basins,
boundaries, or identities to move across GRC systems, and then build structural
and visual examples that demonstrate those distinctions.

Operator reference:

- [`Motion-ReferenceGuide.md`](../docs/reference/Motion-ReferenceGuide.md)

## Source Anchors

- [`../papers/2026-01-RC-Distance-v4.md`](../papers/2026-01-RC-Distance-v4.md)
  - Appendix C: motion of identities
  - basin representatives, centroid/peak tracking, drift velocity
- [`../papers/2025-11-RC-IdentityChoiceAbundance.md`](../papers/2025-11-RC-IdentityChoiceAbundance.md)
  - identity, choice, abundance, persistence
- [`../papers/2026-02-GRC-V3.md`](../papers/2026-02-GRC-V3.md)
  - basin semantics, split/collapse, hierarchy and persistence
- [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
  - port-local transport, spark expansion, front growth, column structure
- [`LandscapeInference-ImplementationPlan.md`](./LandscapeInference-ImplementationPlan.md)
- [`LandscapeInference-ReferenceGuide.md`](../docs/reference/LandscapeInference-ReferenceGuide.md)
- Phase T telemetry contracts for `GRCV3`, `GRC9`, and `GRC9V3`
- Phase V graph checkpoint artifacts

## Core Position

In continuum RC, motion means coherence-flow-induced change of an identity
region:

```text
coherence density C changes by flux J
identity representatives, centroids, and basin boundaries change over time
```

In graph GRC systems, motion is the graph-discrete version of that idea:

```text
coherence flux changes node values
-> sinks, representatives, basins, paths, boundaries, or topology change
-> an observer infers motion
```

A graph node is a carrier. It is not necessarily the identity itself. Identity
motion can therefore look like an identity "walking" from one node to another
when continuity evidence is strong enough.

## Motion Categories

Motion inference should distinguish the following categories.

### 1. Coherence Motion

Coherence mass changes carriers because continuity and flux move value across
edges.

Evidence:

- edge flux,
- continuity deltas,
- node coherence before/after,
- budget preservation.

Claim strength:

- can be inferred without any identity claim.

### 2. Representative Motion

A basin representative changes while the basin remains related across time.

Representative choices may include:

- sink node,
- peak coherence node,
- checkpoint-local centroid when coordinates exist,
- graph centroid or medoid proxy when coordinates do not exist,
- GRC9/GRC9V3 port-front representative.

Claim strength:

- stronger than coherence motion,
- weaker than full identity motion unless continuity of identity is proven.

### 3. Identity Motion

A persistent identity changes carriers while preserving enough continuity
evidence.

Evidence:

- mass overlap between old and new basins,
- flux path from old representative to new representative,
- successor-map continuity,
- hierarchy/provenance continuity,
- persistence across a motion window,
- absence of a stronger competing continuity claim.

Possible relationship labels:

- `stationary`
- `drifted`
- `walked`
- `split`
- `merged`
- `collapsed`
- `dissolved`
- `emerged`
- `ambiguous`

### 4. Boundary Motion

Basin boundaries, ridges, membranes, frontiers, or port-fronts advance,
recede, rupture, or stabilize.

Evidence:

- basin membership changes,
- ridge/valley classifier changes,
- frontier/port capacity changes,
- pressure-boundary provenance,
- path rupture or persistence.

### 5. Topological Motion

The support itself changes by growth, spark, split, expansion, collapse,
pruning, or merge.

Evidence:

- topology events,
- checkpoint node/edge births and removals,
- expansion registries,
- collapse registries,
- front-growth provenance.

Topological motion may accompany identity motion, but it is not identical to
identity motion.

## Authority Model

Motion follows the landscape-inference authority order:

```text
dynamics
-> telemetry/checkpoint evidence
-> observed landscape primitives
-> motion inference
-> diagnostics, visualization, export, or policy suggestions
```

Seeds and GRCL documents may declare conditions that can lead to motion:

- flux pressure,
- basin adjacency,
- ridge softness,
- path conductance,
- front capacity,
- spark preconditions,
- collapse/choice ambiguity.

They must not declare that motion happened. Motion is observer-inferred.

## Output Shape

The primary output is a motion-inference report rooted in existing artifacts,
plus optional inferred landscape extensions.

Top-level motion report:

```yaml
motion_contract_version: motion_inference_iter1_v1
source_session_id: S....
source_runtime_family: grcv3 | grc9 | grc9v3
source_artifact_paths: [...]
motion_window:
  start_step: int
  end_step: int
  checkpoint_ids: [...]
records:
  - motion_id: string
    authority: observed
    classifier_id: string
    classifier_version: string
    motion_kind: coherence | representative | identity | boundary | topological
    relationship: stationary | drifted | walked | split | merged | collapsed | dissolved | emerged | ambiguous
    confidence: float
    evidence_quality: strong | partial | degraded | missing_surface | diagnostic_only
    step_ids: [...]
    old_carriers: [...]
    new_carriers: [...]
    transferred_mass: float | null
    competing_claims: [...]
    evidence: {...}
```

The Iteration 1 contract should be implemented as typed Python dataclasses or
equivalent schema helpers before any observer emits records. The schema should
follow the landscape-inference pattern:

- `classifier_id` and `classifier_version` are required on every record.
- `authority` is always `observed` for inferred motion records.
- per-record `step_ids` or equivalent time metadata must be present even when
  a top-level window is present.
- `competing_claims` is required for identity motion and optional for other
  motion kinds.
- `evidence_quality` and missing/degraded-surface flags are required so weak
  motion claims are not confused with fully observed claims.

When exported into a `LandscapeSeed`, motion appears only as metadata under
extensions, not as a new primitive type:

```yaml
extensions:
  motion_inference:
    authority: observed
    motion_id: ...
    motion_kind: identity
    relationship: walked
    source_window: [start_step, end_step]
```

A single inferred `LandscapeSeed` may carry both
`extensions.landscape_inference` and `extensions.motion_inference`. Landscape
inference describes observed primitives in one or more windows; motion
inference describes temporal relationships between observed carriers or
primitives across windows. Motion records may reference primitive ids, but they
do not create new primitive types.

## Confidence And Evidence Quality

Confidence is a deterministic float in `[0.0, 1.0]`.

The baseline scoring factors are:

- checkpoint count and window span,
- availability of required local fields,
- mass-overlap strength,
- flux/path support,
- continuity-delta agreement,
- budget preservation or leak status,
- hierarchy/provenance continuity,
- competing-claim strength,
- family-specific evidence completeness.

Suggested labels:

| Range | Meaning |
|---|---|
| `>= 0.80` | strong observed motion claim |
| `0.50..0.79` | partial/candidate claim |
| `0.40..0.49` | degraded claim due to budget leak or corrupted/incomplete surfaces |
| `0.25..0.39` | diagnostic-only weak claim |
| `< 0.25` | rejected or insufficient evidence |

Missing local evidence should degrade confidence and set `evidence_quality`;
it should not silently pass. Diagnostic-only records may be useful in reports
but should not enter accepted motion catalogs without review.

Current contract thresholds:

| Label | Threshold |
|---|---:|
| `strong` | `0.80` |
| `partial` | `0.50` |
| `degraded` | `0.40` |
| `diagnostic_only` | `0.25` |

These thresholds are implementation parameters, not paper-derived constants.
They are intentionally exposed here so future evidence runs can calibrate or
replace them without reverse-engineering code.

## Provisional Classifier Parameters

The first motion observers use conservative fixed values until we have enough
reviewed motion sessions to fit thresholds empirically. These values are
allowed to change after catalog review, but changes must be recorded here and
in the relevant checklist summary.

### Coherence Motion Observer

`src/pygrc/landscapes/motion_coherence.py` currently uses:

| Parameter | Value | Purpose |
|---|---:|---|
| `min_coherence_delta` | `1e-9` | Ignore checkpoint-local coherence changes at numerical-noise scale. |
| `min_flux_support` | `1e-12` | Require nonzero signed edge-flux evidence for a direct transfer claim. |
| `budget_leak_threshold` | `1e-9` | Treat larger checkpoint-budget error as leak evidence. |
| `continuity_tolerance` | `1e-6` | Compare observed coherence delta against stored continuity delta. |
| direct-transfer confidence base | `0.85` | Starting confidence for direct edge-supported coherence transfer. |
| ambiguous-transfer confidence base | `0.55` | Starting confidence for indirect or multi-edge-supported transfer. |
| diagnostic-only confidence cap | `0.25` | Cap records from too-short/checkpoint-degraded windows. |
| budget-leak confidence cap | `0.45` | Cap records when budget audit detects leak evidence. |
| generic degradation confidence cap | `0.65` | Cap records with missing/mismatched continuity or other degraded surfaces. |

Interpretation caveat: these values are pragmatic classifier defaults. They are
not claims that RC/GRC theory fixes these numerical thresholds.

### Representative Motion Observer

`src/pygrc/landscapes/motion_representative.py` currently uses:

| Parameter | Value | Purpose |
|---|---:|---|
| stable-representative confidence base | `0.80` | Starting confidence when the same representative carrier is selected across a checkpoint pair. |
| representative-drift confidence base | `0.70` | Starting confidence when a basin/group representative changes carrier. |
| ambiguous/degraded confidence cap | `0.55` | Cap when representative evidence falls back to degraded selection surfaces. |
| partial-representative confidence cap | `0.65` | Cap when representative selection uses partial evidence such as graph medoid or port/front proxy. |
| diagnostic-only confidence cap | `0.25` | Cap records from too-short/checkpoint-degraded windows. |

Representative selection priority is deterministic:

1. sink node,
2. nearest node to coherence-weighted centroid when coordinates exist,
3. peak coherence node,
4. GRC9/GRC9V3 port/front candidate,
5. graph medoid proxy when coordinates are absent,
6. lowest-node-id fallback.

Interpretation caveat: representative motion is not identity motion. A changed
representative remains a representative-level observation until the identity
continuity matcher proves stronger continuity.

### Identity Continuity Matcher

`src/pygrc/landscapes/motion_identity.py` currently uses:

| Parameter | Value | Purpose |
|---|---:|---|
| one-to-one minimum match score | `0.50` | Minimum continuity score for stationary/drifted/walked one-to-one identity matches. |
| branch minimum match score | `0.20` | Lower per-branch threshold for split/merge/collapse where continuity is distributed across branches. |
| strong match score | `0.75` | Threshold for strong stationary/walked identity continuity. |
| mass-overlap weight | `0.40` | Contribution from old/new basin mass overlap. |
| representative-continuity weight | `0.10` | Contribution from stable old/new representative carrier. |
| flux-path weight | `0.20` | Contribution from representative-to-representative path support. |
| successor-continuity weight | `0.20` | Contribution from checkpoint-local successor-map evidence when available. |
| hierarchy/provenance weight | `0.10` | Contribution from shared hierarchy parent or source-provenance tokens when available. |
| group-continuity weight | `0.10` | Contribution from stable old/new basin/group id. |
| collapsed-vs-merged mass ratio | `0.75` | Many-to-one continuity is classified as `collapsed` when new mass is below this ratio of old mass. |
| minimum path-edge flux | `1e-12` | Every edge in a representative-to-representative path must exceed this signed-flux magnitude. |
| diagnostic-only confidence cap | `0.25` | Cap records from too-short/checkpoint-degraded windows. |

Identity matching is deterministic but provisional. It favors mass overlap,
flux/path support, successor continuity, hierarchy/provenance continuity,
group continuity, and representative continuity. Split/merge/collapse branches
intentionally allow lower per-branch scores than one-to-one walking because
continuity may be distributed across multiple children or parents.

Path support is flux-backed: every edge in a multi-hop representative path
must carry signed-flux magnitude above the path-edge threshold. Successor and
hierarchy/provenance continuity are fractional scores rather than binary
"any-hit" gates, so large groups are not over-scored by a single matching
node or token.

### Boundary And Frontier Motion Observer

`src/pygrc/landscapes/motion_boundary.py` currently uses:

| Parameter | Value | Purpose |
|---|---:|---|
| ridge-gradient threshold | `1.0` | Checkpoint-local gradient norm required for geometric ridge evidence. |
| ridge-tensor-anisotropy threshold | `1.0` | Checkpoint-local tensor anisotropy required for tensor ridge evidence. |
| normal-gradient epsilon | `1e-12` | Minimum gradient denominator for graph approximation of `V_n`. |
| stabilization confidence base | `0.78` | Starting confidence for boundary persistence across a checkpoint pair. |
| advance/recession confidence base | `0.70` | Starting confidence for boundary/frontier appearance or port-capacity change. |
| rupture confidence base | `0.62` | Starting confidence for boundary disappearance with topology change. |
| diagnostic-only confidence cap | `0.25` | Cap records from too-short/checkpoint-degraded windows. |

Boundary motion uses checkpoint-local evidence only. Global step-row aggregates
may select candidate sessions but cannot produce per-node boundary claims.
Pressure-boundary provenance is recorded separately and is not sufficient by
itself for a geometric ridge claim. Bridge edges are not used as natural
boundary evidence; if present on incident boundary edges they are explicitly
flagged in degradation reasons.

GRC9/GRC9V3 port-frontier direction is defined by active transport capacity:
frontier advance means occupied ports increase and free ports decrease;
frontier recession means occupied ports decrease and free ports increase.
Boundary normal velocity uses checkpoint runtime-time deltas when available,
falling back to step-index deltas only when checkpoint time is unavailable.
For persistent geometric ridges, the sign of the graph `V_n` approximation can
emit boundary advance or recession even when the carrier node id is stable.

### Topological Motion Observer

`src/pygrc/landscapes/motion_topological.py` currently uses:

| Parameter | Value | Purpose |
|---|---:|---|
| event-backed topology confidence base | `0.82` | Starting confidence when checkpoint topology deltas match topology event rows. |
| event-only topology confidence base | `0.62` | Starting confidence when an event marks topology mutation but adjacent checkpoints do not show carrier birth/removal. |
| topology-only confidence base | `0.45` | Starting confidence for checkpoint topology deltas without matching event rows. |
| diagnostic-only confidence cap | `0.25` | Cap records from too-short/checkpoint-degraded windows. |

Topological motion uses adjacent checkpoint node/edge births and removals as
the local support-change surface. Event rows are matched by step window and
are preferred when present. Event-backed records are stronger than
topology-only records; topology-only mutations are preserved but degraded
because the runtime event provenance is missing. Event-only topology mutations
are allowed for collapse/carrier-reassignment cases where the event stream
records the mutation but the checkpoint pair preserves the same carrier ids.
They remain partial evidence rather than strong evidence: the event row is
runtime provenance for a mutation, but checkpoint-local carrier birth/removal
has not confirmed the support change.

Topological motion is not identity motion. The observer records
`identity_continuity_status` as a diagnostic and leaves identity preservation
to the Iteration 5 identity matcher. Generic support reassignment or
reconfiguration uses the neutral `stationary` relationship label in the motion
contract; it must not reuse `drifted`, which is reserved for representative or
identity carrier displacement.

## Evidence Requirements

Motion inference is checkpoint-series-first.

Step rows and run summaries can select candidate sessions, but local motion
claims require comparing at least two graph states. Persistence-sensitive
claims should generally use at least three checkpoints.

Required normalized surfaces:

- node coherence by checkpoint,
- edge flux by checkpoint when available,
- continuity delta when available,
- basin membership by checkpoint,
- representative node by checkpoint,
- node/edge birth and removal,
- provenance/lowering tags when available,
- graph coordinates when available,
- GRC9/GRC9V3 port-state overlays when relevant.

Checkpoint spacing must be recorded. If checkpoints are irregularly spaced,
motion velocities should use actual step/time deltas when available. If only
checkpoint order is available, records must use ordinal motion language
(`changed between checkpoints`) rather than velocity language. Step rows may
support weak sub-checkpoint diagnostics, but not strong local motion claims
without checkpoint-local evidence.

Budget evidence should reuse the landscape-inference budget audit where
possible. Unit-measure budgets are valid for current GRC9V3 artifacts; future
non-unit quadrature requires checkpoint-local weights. Budget leak thresholds
must be explicit in classifier params and must degrade confidence rather than
being ignored.

## Mathematical Observables

The continuum RC motion formulas provide the target interpretation, but graph
families may only approximate them when embeddings or local gradients are
available.

### Drift Velocity

Continuum target:

```text
v_bar_i = integral_B v_C C dV_g / integral_B C dV_g
```

Graph approximation:

- use edge flux and node coherence to estimate a basin-level directed drift,
- use centroid/medoid displacement when graph coordinates exist,
- otherwise report representative-carrier change without Euclidean velocity.

### Boundary Normal Velocity

Continuum target:

```text
V_n = -partial_t C / ||grad C||
```

Graph approximation:

- use checkpoint-local gradient/tensor evidence when present,
- compare ridge classifier outputs across checkpoints,
- compare basin membership changes at the boundary,
- report `boundary_velocity_unavailable` when neither gradients nor an
  embedding-supported boundary are present.

## Reuse Of Existing Inference Components

Motion should reuse existing landscape inference modules instead of creating
parallel classifiers.

- Boundary motion reuses the ridge classifier output as its static boundary
  evidence, then compares ridge state across checkpoints.
- Valley/path motion uses the existing path extraction and bridge-exclusion
  substrate.
- Topological motion consumes `events.jsonl` when available and matches event
  rows to checkpoint topology deltas by step id. Event-backed topology motion
  is stronger than topology-only inference.
- Pheromone/path-memory outputs may be used as persistence evidence but do not
  by themselves prove identity motion.

## Relationship To Authored-Vs-Observed Comparison

Motion relationships are temporal runtime-to-runtime relationships.
Landscape authored-vs-observed relationships are source-to-runtime
relationships. They must remain distinct.

| Layer | Compares | Example labels |
|---|---|---|
| authored-vs-observed | source primitive -> observed primitive | `preserved`, `transformed`, `split`, `collapsed`, `emerged`, `dissolved`, `unknown` |
| motion inference | observed state at t0 -> observed state at t1 | `stationary`, `drifted`, `walked`, `split`, `merged`, `collapsed`, `dissolved`, `emerged`, `ambiguous` |

Authored-vs-observed comparison may consume motion records as evidence, but it
must not reuse motion labels as source-comparison labels without an explicit
mapping.

## Multiscale And Coarse-Grained Motion

GRC9 and GRC9V3 support exact column coarse-graining/Split for supported port
fields. Motion should eventually support multiscale reports:

- fine port/node motion,
- column-coarse motion,
- basin-level motion,
- graph-level/topological motion.

A structure may walk at fine scale while appearing stationary at a coarser
scale. The first implementation may record only fine-scale motion, but it
should preserve enough metadata for later multiscale reports. GRC9/GRC9V3
examples should explicitly state whether coarse-grained views were computed.

## Family Support

### GRCV3

Strongest support for semantic identity motion:

- basin attributes,
- signed Hessian/gradient evidence,
- split/collapse/hierarchy events,
- checkpoint geometry when available.

GRCV3 can support coherence motion, representative motion, identity walking,
split/merge/collapse, and boundary motion.

### GRC9

Mechanical/topological support:

- port-local flux,
- successor maps,
- sinks/basins,
- spark expansion,
- front growth,
- column coarse-graining.

GRC9 identity motion is weaker unless supported by basin continuity and
successor-map evidence. Port/frontier motion is first-class.

### GRC9V3

Hybrid support:

- GRC9 port-local motion,
- GRCV3 semantic basin lift,
- hybrid spark/expansion/completion,
- choice/collapse,
- front growth,
- column coarse-graining/Split for transport diagnostics.

GRC9V3 is the preferred family for examples that combine port-local coherence
motion with identity walking and topological change.

## Non-Claims

Motion inference must not claim:

- Euclidean translation unless coordinates or embeddings are present,
- proper-time or causal-cone bounded motion; Lorentzian/proper-time motion is
  out of scope for Iterations 1-10 unless a later phase adds the causal layer,
- FRC scale-indexed motion; scale-specific `C(x,t;sigma)` motion is a future
  refinement, not part of the baseline motion contract,
- observer-local/partial-graph completeness; partial-observer motion should
  use an explicit `observer_scope` future extension,
- identity preservation from node-id equality alone,
- identity death from representative change alone,
- valley/path motion from bridge edges alone,
- boundary motion from global summary aggregates alone,
- source-authored motion outcomes.

## Planned Artifacts

- `src/pygrc/landscapes/motion.py`
- `src/pygrc/landscapes/motion_loader.py`
- `src/pygrc/landscapes/motion_coherence.py`
- `src/pygrc/landscapes/motion_identity.py`
- `src/pygrc/landscapes/motion_boundary.py`
- `src/pygrc/landscapes/motion_topological.py`
- `src/pygrc/visualization/motion.py`
- `outputs/motion/sessions/S0001/...`

The exact file names may change, but the observer-only and checkpoint-series
authority should not.

## Iteration Plan

### Iteration 1. Contract And Definitions

Define motion kinds, relationship labels, evidence fields, confidence fields,
record schema, confidence scoring, scope boundaries, and non-claims.

### Iteration 2. Motion Window Loader

Reuse landscape inference artifact loading and checkpoint substrate to produce
motion windows over checkpoint series.

### Iteration 3. Coherence Motion Observer

Infer node-to-node coherence motion from flux, continuity deltas, and
before/after coherence changes.

### Iteration 4. Representative Motion Observer

Track basin sinks, peaks, centroids/medoids, and representative changes across
checkpoints.

### Iteration 5. Identity Continuity Matcher

Infer stationary/drifted/walked/split/merged/collapsed/dissolved/emerged
relationships from basin overlap, flux support, hierarchy continuity, and
persistence.

### Iteration 6. Boundary And Frontier Motion

Infer ridge/frontier/port-boundary advance, recession, rupture, and
stabilization by comparing existing ridge/frontier classifier outputs across
motion windows.

### Iteration 7. Topological Motion

Classify motion induced by spark, growth, expansion, split, collapse, pruning,
or merge events, preferring event-backed telemetry over topology-only
inference when both are available.

### Iteration 8. Structural Examples

Build simple replayable examples:

- pure coherence transfer without identity motion,
- representative drift,
- identity walking across carriers,
- split/merge/collapse motion,
- frontier/port motion in GRC9/GRC9V3.
- GRC9V3 hybrid refinement motion.
- GRC9/GRC9V3 coarse-grained motion diagnostics.

The Iteration 8 example runner is `src/pygrc/landscapes/motion_examples.py`.
It writes synthetic telemetry/checkpoint artifacts and then runs the motion
observers over those artifacts. The examples are runtime evidence fixtures,
not source-authored motion outcomes.

Replay command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples --output-root outputs/motion --session-id S0001
```

Individual examples can be rerun with repeated `--example <name>` arguments.

### Iteration 9. Visualization

Render motion overlays:

- old/new representatives,
- transferred mass,
- flux arrows,
- basin overlap,
- boundary advance/recession,
- topology births/removals.

Visualizations may be static two-checkpoint comparisons or temporal
checkpoint-series animations, but every visual artifact must link back to the
motion record ids and source checkpoint ids it depicts.

Revision 1 implements static two-checkpoint visualization through
`pygrc.visualization.motion`. The renderer consumes the existing Iteration 8
motion example artifacts, writes per-example graph overlays and timelines, and
stores explicit visual summaries that link back to motion report ids,
checkpoint ids, and telemetry paths. Temporal checkpoint-series animation is
deferred and recorded as such in the visual summaries.

The graph overlay uses checkpoint-local `chart_center_hint` coordinates when
available and otherwise uses a deterministic circular fallback. Dense examples
should provide chart hints in checkpoint node payloads. Topological
birth/removal/evidence nodes are highlighted separately from generic old/new
motion carriers, while stationary records remain listed without promoting graph
carriers to non-stationary visual highlights.

Reproduce:

```bash
PYTHONPATH=src python -m pygrc.visualization.motion --session-root outputs/motion/sessions/S0001
```

### Iteration 10. Motion Seed Library And Composite Examples

Convert the Iteration 8 observer fixtures into authored seed examples where
the source languages can express the required preconditions, then run those
seeds through runtime, telemetry, motion inference, visualization, and catalog
review.

This iteration has a different authority target than Iteration 8:

- Iteration 8 proves that the observers classify controlled runtime evidence.
- Iteration 10 tests whether authored seeds and source languages can produce
  those evidence patterns dynamically.

Initial seed targets:

- coherence transfer -> representative drift,
- representative drift -> identity walking,
- spark/expansion -> frontier advance -> topological refinement,
- split -> merge or collapse,
- identity walking with boundary/frontier motion,
- GRC9/GRC9V3 coarse-grained motion diagnostics.

Composite runs should preserve failed and ambiguous cases. A failed composite
is useful evidence about which source-level conditions do not actually produce
the intended runtime motion.

Revision 1 implements this layer in `pygrc.landscapes.motion_seed_examples`.
The module uses the neutral `LandscapeSeed` vocabulary with
`extensions.motion_seed` metadata. Authored seeds declare preconditions and
target review modes only; projected telemetry and motion observer reports are
the authority for runtime relationships.

Reusable authored seeds are written under `configs/landscapes/seed/motion/`.
Each replay session also stores JSON source-seed snapshots under
`outputs/motion/sessions/<session_id>/source_seeds/` for provenance.

The initial authored seed set covers:

- coherence transfer,
- representative drift,
- identity walking,
- GRC9 port-frontier motion,
- GRC9V3 hybrid refinement,
- a walk -> frontier/refinement composite,
- a split -> merge -> collapse composite.

The composite split/merge/collapse projection intentionally preserves a
disagreement: topology observes the final support contraction as `collapsed`,
while identity continuity classifies the corresponding identity relationship
as `ambiguous`. This remains useful evidence for Iteration 11 review.

Reproduce:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root outputs/motion --session-id S0002
```

### Iteration 11. Long-Window Composite Motion Evidence

Create longer authored composite projections that require 20+ checkpoints to
achieve their motion patterns, then review them before final cataloging and
animated visualization.

This iteration should compare:

- controlled Iteration 8 observer fixtures,
- authored-seed outputs from Iteration 10,
- composite runs that combine multiple motion modes,
- negative controls and failed composites.

The goal is not to close the catalog yet. The goal is to create and review
longer unfolding examples, decide which examples deserve animated visual
review, which need more seed tuning, and which should remain recorded as
rejected or ambiguous evidence.

Revision 1 adds two long-window GRC9V3 composites through
`pygrc.landscapes.motion_seed_examples --long-composites`:

- `motion_long_relay_walk_frontier`: 21 checkpoints, repeated delayed
  identity walking and frontier/topology changes.
- `motion_long_split_merge_collapse_cascade`: 24 checkpoints, delayed split,
  merge, frontier changes, and topological collapse with an identity-level
  ambiguous collapse relation preserved.

Reproduce:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples --output-root outputs/motion --session-id S0003 --long-composites
```

### Iteration 11.1. Failed And Negative Long-Window Controls

Add explicit long-window controls that do not produce the intended
non-stationary motion. This closes the review gap that Iteration 11 initially
had only positive composites plus an ambiguous collapse case.

Revision 2 extends `--long-composites` with:

- `motion_long_failed_relay_broken_continuity`: a 21-checkpoint relay-shaped
  source projection whose handoff deliberately lacks successor, flux-path, and
  provenance continuity. Identity inference should record dissolved/emerged
  evidence rather than `walked`.
- `motion_long_no_motion_negative_control`: a 21-checkpoint stable support
  control. Stationary identity records are allowed, but representative,
  boundary, and topological non-stationary records should remain absent.

These sessions remain structural projections. The authored `LandscapeSeed`
documents declare source preconditions and non-claims; synthetic checkpoint
series supply the projected runtime evidence. They are not yet live
`LandscapeSeed -> GRC runtime -> telemetry` executions. The live runtime path
is reserved for a later implementation pass once motion seed lowering and
family-specific runtime execution are ready.

### Iteration 12. Graph-Engine Animated Motion Visualization

Reuse the existing checkpoint graph visualization engine where possible,
including sequence figures and GIF animation, to show motion as a live
multi-checkpoint process instead of only as a two-checkpoint comparison.

This iteration should:

- consume the same motion reports and telemetry packs as Iteration 9,
- render graph checkpoint sequences with motion overlays,
- animate old/new representative movement,
- animate coherence transfer and flux arrows when checkpoint cadence supports
  it,
- animate topology births/removals and boundary/frontier changes,
- keep every animated frame linked to motion record ids and checkpoint ids,
- preserve the no-visual-only-promotion rule.

The implementation should prefer reusing `pygrc.visualization.graph_render`
layout, sequence, HTML, and animation machinery, then layer motion overlays and
record metadata on top. If a run has only two checkpoints, the animation may be
a two-frame diagnostic; richer examples should use longer checkpoint windows.

Revision 1 implements this through
`pygrc.visualization.motion --animated`. The renderer first produces the
standard static Iteration 9 surfaces, then calls the graph checkpoint renderer
for graph-engine sequence figures, HTML, and GIF animation. It reuses the
graph-engine union layout for motion-overlay frames and writes:

- `graph_engine/graph_sequence.png`,
- `graph_engine/graph_animation.gif`,
- `graph_engine/graph_html/final_graph.html`,
- `motion_frames/frame_*.png`,
- `motion_sequence.png`,
- `motion_animation.gif`,
- `motion_animated_summary.json`.

The canonical animated session is the Iteration 11.1 long-window session:

```bash
PYTHONPATH=src python -m pygrc.visualization.motion --session-root outputs/motion/sessions/S0003 --animated
```

Static and animated analysis now coexist: static visualizations remain the
best record-inspection surface, while animated graph-engine and motion-overlay
surfaces show multi-checkpoint unfolding.

### Iteration 12.1. Motion Review Of Complex Landscape-Inference Examples

Apply the motion observer and visualization stack to the most complex
Landscape Inference examples from `outputs/landscape_inference/sessions/S0013`.
This asks a different question than Iterations 8-12: given landscapes already
inferred as basins, valleys, ridges, junctions, and pheromone/path-memory
surfaces, what motion is visible over the same runtime checkpoint evidence?

Revision 1 implements this bridge in
`pygrc.landscapes.motion_landscape_bridge`. The bridge reads a Landscape
Inference `session_manifest.json`, reuses each selected seed's
`artifact_root`, writes motion reports next to those telemetry artifacts, and
creates a motion session whose visualizer can consume the same roots.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge \
  --landscape-manifest outputs/landscape_inference/sessions/S0013/session_manifest.json \
  --output-root outputs/motion \
  --session-id S0004
```

Selected complex examples:

- `corrected_propagated_front_relay`,
- `corrected_hybrid_full_composition`,
- `grcv3_mediated_spill_branch_single_intermediate_probe`,
- `corrected_multi_center_delayed_collapse_learning`.

The authority boundary is unchanged: Landscape Inference classifies observed
landscape primitives, Motion Inference classifies temporal changes over the
same checkpoint series, and visualization remains supporting evidence only.

### Iteration 12.2. Motion Interpretation And Calibration

Add a review-facing interpretation layer over the Iteration 12.1 bridge
outputs. This is not a new observer and must not create new motion records,
landscape primitives, source claims, or visual-only claims. It reads existing
`landscape_motion_summary.json` artifacts and classifies their evidence into
catalog-preparation labels:

- accepted evidence, such as coherence drift, topological emergence/collapse,
  and GRC9/GRC9V3 boundary/frontier motion;
- ambiguous or review-needed evidence, especially dense identity windows where
  the current identity observer emits many split-style carrier records;
- diagnostic or family-limited evidence, such as GRCV3 boundary motion where
  port/frontier surfaces are not present.

Revision 1 implements this in `pygrc.landscapes.motion_interpretation`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation \
  --session-root outputs/motion/sessions/S0004
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/motion_interpretation_summary.json`,
- `outputs/motion/sessions/S0004/interpretation/motion_interpretation.md`,
- `outputs/motion/sessions/S0004/interpretation/knowledge_graph_motion_case_study.md`.

The key calibration outcome is that the complex S0004 examples already show
useful knowledge-graph motion: coherence drift is robust across families,
topological emergence/collapse is accepted when event/checkpoint evidence
exists, and GRC9V3 exposes boundary/frontier motion. Dense identity split
records are retained as diagnostic evidence but require catalog review before
being promoted to accepted identity fission.

### Iteration 12.3. Dense-Window Motion Calibration

Close the dense-window caveat exposed by Iteration 12.2 before cataloging. The
raw motion observer records remain authoritative and unchanged; this iteration
adds a calibration summary that tells Iteration 13 how to read split-dominant
identity output in large checkpoint windows.

Revision 1 extends `pygrc.landscapes.motion_interpretation` with dense-window
calibration. The calibration reads the existing Iteration 12.2 interpretation
summary and writes explicit labels for:

- `dense_branching_field`,
- `identity_split_dominant`,
- `representative_stationary_identity_branching`,
- `catalog_as_dense_carrier_branching_not_fission`,
- `needs_identity_membership_linkage`,
- `split_dominant_small_window_review`.

Default thresholds:

- dense window: total motion records `>= 500` or identity records `>= 500`,
- split dominance: identity `split` ratio `>= 0.80`,
- representative stationary context: representative `stationary` ratio
  `>= 0.80` while identity split dominance holds.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation \
  --session-root outputs/motion/sessions/S0004 \
  --dense-calibration
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/dense_window_calibration_summary.json`,
- `outputs/motion/sessions/S0004/interpretation/dense_window_calibration.md`.

Catalog rule: dense split-dominant identity records are treated as carrier
branching diagnostics unless a later identity-membership/provenance linkage
pass promotes them to accepted identity fission.

### Iteration 12.4. Identity Fission Promotion Gate

Implement the membership/provenance linkage pass referenced by Iteration 12.3.
This is still a review layer, not a raw observer rewrite. It reads existing
identity motion reports and summaries, then decides whether any split-dominant
records are strong enough to promote from diagnostic carrier branching to
accepted identity-fission candidates.

Revision 1 extends `pygrc.landscapes.motion_interpretation` with an identity
fission promotion audit. Promotion is deliberately conservative:

- one old basin must split into a compact daughter set;
- default daughter count must be between `2` and `4`;
- confidence must be at least `0.80`;
- evidence quality must be `strong`;
- transferred mass must be positive;
- identity summary matches must show provenance continuity from the old group
  to at least two daughter groups, with continuity `>= 0.75`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation \
  --session-root outputs/motion/sessions/S0004 \
  --dense-calibration \
  --promote-identity-fission
```

Written artifacts:

- `outputs/motion/sessions/S0004/interpretation/identity_fission_promotion_summary.json`,
- `outputs/motion/sessions/S0004/interpretation/identity_fission_promotion.md`.

Catalog rule: broad fan-out split records remain carrier-branching diagnostics.
Only compact, strong, provenance-linked daughter splits can be promoted as
accepted identity-fission candidates.

### Iteration 12.5. Confirmed Dense Fission Seed Composition

Create a seed-backed dense session that does satisfy the Iteration 12.4
promotion gate. This complements S0004: S0004 teaches that broad dense
branching should stay diagnostic, while S0005 gives a positive dense fission
composition with compact daughters and provenance continuity.

Revision 1 extends `pygrc.landscapes.motion_seed_examples` with
`--dense-fission` and a reusable source seed:

- `configs/landscapes/seed/motion/motion_dense_confirmed_fission.seed.yaml`.

The session is dense over time, not dense by placing hundreds of unrelated
parents in the same checkpoint pair. The confirmed composition uses 501
compact parent-to-two-daughter fission motifs across a long checkpoint
sequence. This avoids the identity matcher's pathological all-old-groups by
all-new-groups comparison case while still proving dense confirmed fission.
Iteration 12.6 resolves the matcher-side same-step performance issue.

Canonical commands:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples \
  --output-root outputs/motion \
  --session-id S0005 \
  --dense-fission \
  --no-visuals

PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation \
  --session-root outputs/motion/sessions/S0005 \
  --dense-calibration \
  --promote-identity-fission
```

Written artifacts:

- `outputs/motion/sessions/S0005/landscape_motion_summary.json`,
- `outputs/motion/sessions/S0005/interpretation/dense_window_calibration_summary.json`,
- `outputs/motion/sessions/S0005/interpretation/identity_fission_promotion_summary.json`,
- `outputs/motion/sessions/S0005/interpretation/identity_fission_promotion.md`.

Observed S0005 result:

- 501 reviewed split records;
- 501 compact candidates;
- 501 provenance-supported candidates;
- 501 promoted identity-fission candidates;
- promoted key: `motion_dense_confirmed_fission`.

Catalog rule: compact, strong, provenance-linked dense splits can be promoted
as accepted identity fission. Broad same-window fan-out remains carrier
branching diagnostic evidence unless a future membership/provenance pass
proves otherwise.

### Iteration 12.6. Sparse Identity Matcher For Dense Same-Step Fields

Resolve the performance issue left visible by Iteration 12.5: a naive dense
same-step fission field can contain hundreds of old parent groups and thousands
of new daughter groups in one checkpoint pair. The original identity matcher
scored every old/new group pair, even when most pairs had no possible
continuity evidence.

Revision 1 changes `pygrc.landscapes.motion_identity` from all-pairs scoring
to sparse evidence-indexed candidate generation. Candidate old-to-new edges are
created only when there is at least one local continuity signal:

- same group id,
- shared node,
- successor-node linkage,
- hierarchy-parent linkage,
- provenance-token linkage,
- representative-node continuity,
- flux-reachable support.

The matcher then scores only those candidate edges. This preserves correctness
because pairs without any candidate evidence are treated as unmatched, not as
weak matches that deserve expensive scoring.

The identity summary now includes matcher diagnostics:

- `candidate_generation_mode`,
- `all_pair_count_total`,
- `candidate_edge_count_total`,
- `scored_pair_count_total`,
- `all_pair_count_avoided_total`,
- `candidate_reason_counts`,
- per-checkpoint-pair diagnostics.

Regression coverage includes a single checkpoint-pair dense fission field with
501 old parent groups and 1002 new daughter groups. The sparse matcher sees
502002 possible all-pairs comparisons, scores only 1002 candidate edges, avoids
501000 comparisons, and still emits 501 split records.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_motion_identity \
  tests.landscapes.test_motion_seed_examples \
  tests.landscapes.test_motion_interpretation
```

### Iteration 13. Reviewed Motion Catalog

Final closeout. Record accepted examples, rejected examples, ambiguous cases,
family limitations, authored-seed outcomes, composite-session outcomes, static
visuals, and animated visual evidence.

Revision 1 implements the reviewed catalog through
`pygrc.landscapes.motion_catalog` and publishes canonical catalog session
`S0006`.

Canonical command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_catalog \
  --output-root outputs/motion \
  --session-id S0006
```

Written artifacts:

- `outputs/motion/sessions/S0006/session_manifest.json`,
- `outputs/motion/sessions/S0006/reviewed_motion_catalog.json`,
- `outputs/motion/sessions/S0006/reviewed_motion_catalog.md`.

Catalog sources:

- `S0001`: controlled structural examples and static visuals,
- `S0002`: authored seed projections and static visuals,
- `S0003`: long-window composites and animated visuals,
- `S0004`: complex Landscape Inference bridge examples after the 12.6 matcher
  rerun,
- `S0005`: dense confirmed fission seed and promotion evidence.

Observed S0006 closeout:

- total entries: `26`;
- accepted: `17`;
- accepted negative controls: `2`;
- ambiguous: `2`;
- diagnostic: `4`;
- rejected: `1`;
- accepted dense fission: `motion_dense_confirmed_fission`;
- S0004 dense branching remains diagnostic:
  `keep_dense_branching_diagnostic_not_identity_fission`.

Catalog rule: motion catalog entries review existing observed artifacts only.
They do not create new runtime motion records, do not promote source-authored
preconditions into outcomes, and do not accept visual-only claims.
