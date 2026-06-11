# Motion Reference Guide

This document is the operator guide for the Motion Inference layer. It is a
mixture of reference, usage notes, and examples.

Motion Inference observes runtime checkpoint and telemetry artifacts and
classifies how coherence, representatives, identities, boundaries, and graph
support change over time. It does not define a new GRC family, does not mutate
runtime dynamics, and does not turn authored source preconditions into proof
that motion happened.

## Scope

Motion Inference answers questions like:

- Did coherence transfer between graph carriers?
- Did a basin representative drift while the identity stayed on the same
  carrier?
- Did an identity walk, split, merge, collapse, dissolve, or emerge?
- Did a boundary/ridge/frontier advance, recede, rupture, or stabilize?
- Did topology change through support birth, removal, refinement, contraction,
  split, merge, or event-backed collapse?
- Which dense identity split fields are diagnostic carrier branching and which
  are accepted identity fission?
- Which motion examples are accepted, rejected, ambiguous, or retained as
  diagnostic evidence for catalog review?

Motion Inference does not:

- create runtime events,
- change coherence, flux, topology, budgets, boundary policy, or growth policy,
- claim that source-authored seeds produced motion without observer evidence,
- accept visual-only claims,
- promote broad dense branching to identity fission without the promotion gate,
- replace Landscape Inference. Landscape Inference classifies evolved
  structure; Motion Inference classifies temporal change over runtime
  structure.

## Supported Families

Current loaders and observers support these telemetry families:

| Family | Support Level | Notes |
|---|---|---|
| `grcv3` | coherence, representative, identity, topology, and checkpoint-local geometric motion when artifacts expose the evidence | Boundary/frontier claims are family-limited because GRCV3 has no nine-port frontier surface. |
| `grc9` | mechanical/topological and port-frontier motion | Identity/semantic claims are weaker than GRC9V3. |
| `grc9v3` | strongest current family for combined identity, boundary/frontier, topology, dense fission, and source/landscape bridge examples | Preferred for complex examples. |

The motion loader reuses the Landscape Inference artifact loader, so it detects
runtime family from telemetry family extensions and then falls back to run
identity when needed.

## Authority Model

The authority order is:

```text
runtime dynamics -> telemetry/checkpoints -> motion observer records -> interpretation/promotion -> reviewed catalog
```

Motion records use `authority = observed`.

Source seeds can declare preconditions and intended review modes, but they must
not claim that motion occurred. Visualizations can show evidence, but they must
not promote an unsupported claim. Catalog entries review already-written
motion records and interpretation artifacts.

## Motion Kinds

Motion records use these `motion_kind` values:

| Kind | Meaning | Typical Observer |
|---|---|---|
| `coherence` | coherence mass transfers or drifts between carriers | `infer_coherence_motion` |
| `representative` | selected representative changes or remains stable | `infer_representative_motion` |
| `identity` | identity continuity across checkpoint windows | `infer_identity_motion` |
| `boundary` | geometric ridge or GRC9/GRC9V3 port-frontier motion | `infer_boundary_motion` |
| `topological` | support birth/removal/refinement/contraction/split/merge/collapse | `infer_topological_motion` |

Relationship labels include:

- `stationary`
- `drifted`
- `walked`
- `split`
- `merged`
- `collapsed`
- `dissolved`
- `emerged`
- `ambiguous`

The same relationship word is interpreted within its `motion_kind`. For
example, `identity/split` is not the same claim as `topological/split`.

## Artifact Requirements

The preferred input is a run or lane directory containing:

```text
telemetry/
  run_summary.json
  steps.jsonl
  events.jsonl
  graph_checkpoints/
    index.json
    *.json
```

The loader accepts either the run directory or the `telemetry/` directory.

Checkpoint series are the primary evidence source. Step rows and run summaries
are useful for selection, event linkage, and interpretation, but local motion
claims require checkpoint-local node, edge, topology, flux, provenance, and
port evidence.

## Core Python API

Import surface for common observer work:

```python
from pygrc.landscapes import (
    load_motion_window,
    infer_coherence_motion,
    infer_representative_motion,
    infer_identity_motion,
    infer_boundary_motion,
    infer_topological_motion,
)
```

Session, interpretation, visualization, and catalog helpers live in their
implementation modules:

```python
from pygrc.landscapes.motion_examples import run_motion_structural_examples
from pygrc.landscapes.motion_seed_examples import (
    run_motion_authored_seed_examples,
    run_motion_long_composite_examples,
    run_motion_dense_fission_examples,
)
from pygrc.landscapes.motion_landscape_bridge import run_motion_landscape_bridge_session
from pygrc.landscapes.motion_interpretation import (
    run_motion_interpretation_session,
    run_motion_dense_window_calibration_session,
    run_motion_identity_fission_promotion_session,
)
from pygrc.landscapes.motion_catalog import run_motion_reviewed_catalog_session
from pygrc.visualization.motion import (
    render_motion_visual_session,
    render_motion_animated_visual_session,
)
```

Most low-level workflows use:

1. `load_motion_window(...)`
2. one or more `infer_*_motion(...)` observers
3. `result.to_report(...)` or `result.to_summary_mapping()`
4. optional visualization, interpretation, promotion, and catalog review

## Loader Parameters

Function:

```python
load_motion_window(
    path,
    *,
    window_policy="whole_run",
    start_step=None,
    end_step=None,
    final_step_count=None,
    event_step=None,
    radius=None,
    allow_short_persistence_window=False,
)
```

Window policies are inherited from Landscape Inference:

| Policy | Parameters | Use |
|---|---|---|
| `whole_run` | none | Use the whole loaded artifact step range. |
| `explicit` | `start_step`, `end_step` | Use an exact inclusive step window. |
| `final` | `final_step_count` | Use the final N steps. |
| `event_centered` | `event_step`, `radius` | Use `event_step +/- radius`. |

Example:

```python
load_result = load_motion_window(
    "outputs/motion/sessions/S0005/runs/motion_dense_confirmed_fission/grc9v3_motion_dense_confirmed_fission",
    window_policy="whole_run",
    allow_short_persistence_window=True,
)
```

The loaded result includes:

- normalized motion window metadata,
- checkpoint evidence,
- topology deltas,
- landscape evidence substrate,
- quadrature mode,
- availability and diagnostic-only flags.

## Observer Capabilities

Capability matrix:

| Capability | Observer Id | Version | Emits |
|---|---|---|---|
| Coherence motion | `motion_coherence_observer` | `motion_inference_iter3_v1` | `coherence` records |
| Representative motion | `motion_representative_observer` | `motion_inference_iter4_v1` | `representative` records |
| Identity continuity | `motion_identity_continuity_matcher` | `motion_inference_iter5_v1` | `identity` records |
| Boundary/frontier motion | `motion_boundary_frontier_observer` | `motion_inference_iter6_v1` | `boundary` records |
| Topological motion | `motion_topological_observer` | `motion_inference_iter7_v1` | `topological` records |
| Interpretation | `motion_interpretation_iter12_2_v1` | interpretation layer | summary labels |
| Dense-window calibration | `motion_dense_window_calibration_iter12_3_v1` | interpretation layer | dense guidance |
| Identity-fission promotion | `motion_identity_fission_promotion_iter12_4_v1` | promotion layer | promotion audit |
| Reviewed catalog | `motion_reviewed_catalog_iter13_v1` | catalog layer | catalog JSON/Markdown |

### Coherence Observer

Functions:

```python
infer_coherence_motion(
    path_or_result,
    *,
    min_coherence_delta=1e-9,
    min_flux_support=1e-12,
    budget_leak_threshold=1e-8,
    continuity_tolerance=1e-8,
)
infer_coherence_motion_report(path_or_result, **kwargs)
```

Evidence used:

- node coherence deltas,
- edge flux support,
- continuity deltas when available,
- budget audit status,
- basin drift estimates.

Important behavior:

- Coherence motion is not automatically identity motion.
- Budget leaks degrade evidence quality.
- Direct flux support is stronger than ambiguous/no-flux transfer.

### Representative Observer

Functions:

```python
infer_representative_motion(path_or_result)
infer_representative_motion_report(path_or_result)
select_representatives_for_checkpoint(checkpoint)
```

Representative priority:

1. sink node,
2. centroid when coordinates exist,
3. peak coherence,
4. port-front candidate,
5. graph medoid proxy,
6. fallback node.

Important behavior:

- Representative drift is a carrier/representative change, not proof of
  identity walking.
- Stationary representative context is useful when reviewing dense identity
  split fields.

### Identity Continuity Matcher

Functions:

```python
infer_identity_motion(
    path_or_result,
    *,
    min_match_score=0.50,
)
infer_identity_motion_report(path_or_result, **kwargs)
```

Evidence used:

- mass overlap,
- representative continuity,
- flux-path support,
- successor continuity,
- hierarchy/provenance continuity,
- group-id continuity.

The matcher is sparse and evidence-indexed. It creates candidate old-to-new
edges only when continuity evidence exists:

- same group id,
- shared node,
- successor-node linkage,
- hierarchy-parent linkage,
- provenance-token linkage,
- representative-node continuity,
- flux-reachable support.

Pairs without candidate evidence are treated as unmatched. This avoids the
old all-old-groups by all-new-groups path for dense same-step fission fields.

Identity summary diagnostics include:

- `candidate_generation_mode`
- `all_pair_count_total`
- `candidate_edge_count_total`
- `scored_pair_count_total`
- `all_pair_count_avoided_total`
- `candidate_reason_counts`

### Boundary And Frontier Observer

Functions:

```python
infer_boundary_motion(path_or_result)
infer_boundary_motion_report(path_or_result)
```

Evidence used:

- checkpoint-local gradient norm,
- tensor anisotropy or trace,
- basin membership changes,
- port occupancy/frontier overlays,
- incident bridge edges,
- graph approximation of `V_n = -partial_t C / ||grad C||`.

Important behavior:

- Pressure-boundary provenance is separate from geometric ridge evidence.
- Global step-row aggregates cannot create per-node boundary claims.
- GRC9/GRC9V3 port-frontier advance means occupied ports increase and free
  ports decrease.

### Topological Observer

Functions:

```python
infer_topological_motion(path_or_result)
infer_topological_motion_report(path_or_result)
```

Evidence used:

- node and edge births/removals across checkpoint pairs,
- event rows matched by step window,
- support refinement/contraction/split/merge/prune signals.

Important behavior:

- Event-backed topology is stronger than topology-only evidence.
- Event-only topology remains partial evidence.
- Topological support change is not identity continuity. Identity survival is
  decided by the identity matcher.

## Common Workflows

The examples below show both Python API usage and script-style terminal usage.

### 1. Inspect A Motion Window

API:

```python
from pygrc.landscapes import load_motion_window

load_result = load_motion_window(
    "outputs/motion/sessions/S0001/runs/identity_walking_control/grc9v3_identity_walking_control",
    allow_short_persistence_window=True,
)

print(load_result.landscape_load_result.source_runtime_family)
print(load_result.motion_window.to_mapping())
print(len(load_result.checkpoint_evidence))
print(len(load_result.topology_deltas))
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import load_motion_window

load_result = load_motion_window(
    "outputs/motion/sessions/S0001/runs/identity_walking_control/grc9v3_identity_walking_control",
    allow_short_persistence_window=True,
)

print("runtime:", load_result.landscape_load_result.source_runtime_family)
print("window:", load_result.motion_window.to_mapping())
print("checkpoints:", len(load_result.checkpoint_evidence))
print("topology deltas:", len(load_result.topology_deltas))
PY
```

### 2. Run All Core Observers On One Artifact

API:

```python
from pygrc.landscapes import (
    load_motion_window,
    infer_boundary_motion,
    infer_coherence_motion,
    infer_identity_motion,
    infer_representative_motion,
    infer_topological_motion,
)

artifact = "outputs/motion/sessions/S0005/runs/motion_dense_confirmed_fission/grc9v3_motion_dense_confirmed_fission"
window = load_motion_window(artifact, allow_short_persistence_window=True)

results = {
    "coherence": infer_coherence_motion(window),
    "representative": infer_representative_motion(window),
    "identity": infer_identity_motion(window),
    "boundary": infer_boundary_motion(window),
    "topological": infer_topological_motion(window),
}

for name, result in results.items():
    print(name, len(result.records))
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import (
    load_motion_window,
    infer_boundary_motion,
    infer_coherence_motion,
    infer_identity_motion,
    infer_representative_motion,
    infer_topological_motion,
)

artifact = "outputs/motion/sessions/S0005/runs/motion_dense_confirmed_fission/grc9v3_motion_dense_confirmed_fission"
window = load_motion_window(artifact, allow_short_persistence_window=True)

for name, fn in {
    "coherence": infer_coherence_motion,
    "representative": infer_representative_motion,
    "identity": infer_identity_motion,
    "boundary": infer_boundary_motion,
    "topological": infer_topological_motion,
}.items():
    result = fn(window)
    print(name, "records:", len(result.records))
    if name == "identity":
        print("matcher diagnostics:", result.matcher_diagnostics)
PY
```

### 3. Generate Controlled Structural Examples

Command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples \
  --output-root outputs/motion \
  --session-id S0001
```

Run one example:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_examples \
  --output-root outputs/motion \
  --session-id S0001 \
  --example identity_walking_control
```

Output:

```text
outputs/motion/sessions/S0001/
  run_report.json
  runs/<example_name>/
  visualizations/<example_name>/
```

### 4. Generate Authored Seed Projections

Command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples \
  --output-root outputs/motion \
  --session-id S0002
```

This writes reusable seeds under:

```text
configs/landscapes/seed/motion/
```

and session-local snapshots under:

```text
outputs/motion/sessions/S0002/source_seeds/
```

Important boundary:

- authored seeds declare preconditions,
- projected telemetry/checkpoints provide runtime evidence,
- observers decide whether motion happened.

### 5. Generate Long-Window Composites And Animated Visuals

Long-window composites:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_seed_examples \
  --output-root outputs/motion \
  --session-id S0003 \
  --long-composites
```

Animated visual review:

```bash
PYTHONPATH=src python -m pygrc.visualization.motion \
  --session-root outputs/motion/sessions/S0003 \
  --animated
```

Output includes:

```text
outputs/motion/sessions/S0003/visualizations/<example>/
  motion_graph.png
  motion_timeline.png
  motion_sequence.png
  motion_animation.gif
  motion_animated_summary.json
```

### 6. Bridge Complex Landscape Inference Examples Into Motion

Command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_landscape_bridge \
  --landscape-manifest outputs/landscape_inference/sessions/S0013/session_manifest.json \
  --output-root outputs/motion \
  --session-id S0004
```

Then interpret, calibrate dense windows, and run fission promotion:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_interpretation \
  --session-root outputs/motion/sessions/S0004 \
  --dense-calibration \
  --promote-identity-fission
```

Current S0004 catalog interpretation:

- useful complex motion evidence exists,
- dense identity split fields remain diagnostic carrier branching,
- no S0004 run is promoted to accepted identity fission,
- `corrected_multi_center_delayed_collapse_learning` is accepted for
  topological collapse with identity calibration.

### 7. Generate The Dense Confirmed-Fission Positive Control

Command:

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

Current S0005 result:

- 501 reviewed split records,
- 501 compact candidates,
- 501 provenance-supported candidates,
- 501 promoted identity-fission candidates,
- catalog guidance: `promote_supported_identity_fission_candidates`.

### 8. Build The Reviewed Motion Catalog

Command:

```bash
PYTHONPATH=src python -m pygrc.landscapes.motion_catalog \
  --output-root outputs/motion \
  --session-id S0006
```

Output:

```text
outputs/motion/sessions/S0006/
  session_manifest.json
  reviewed_motion_catalog.json
  reviewed_motion_catalog.md
```

Current S0006 counts:

- total entries: `26`,
- accepted: `17`,
- negative controls: `2`,
- ambiguous: `2`,
- diagnostic: `4`,
- rejected: `1`.

## Interpretation And Catalog Rules

### Dense Branching Versus Identity Fission

Dense identity split output is not automatically accepted as identity fission.

The dense-window calibration layer labels dense fields and decides whether a
promotion pass is needed. The identity-fission promotion gate accepts only
compact, strong, provenance-linked splits.

S0004 is the diagnostic contrast:

```text
keep_dense_branching_diagnostic_not_identity_fission
```

S0005 is the accepted positive case:

```text
promote_supported_identity_fission_candidates
```

### Static Versus Animated Visuals

Static visuals are best for record inspection:

```text
motion_graph.png
motion_timeline.png
motion_visual_summary.json
```

Animated visuals are best for long-window review:

```text
motion_sequence.png
motion_animation.gif
motion_animated_summary.json
```

Visuals are supporting evidence only. They must link back to motion record ids
and checkpoint ids, and they must not create claims absent from observer
reports.

### Source Seeds Versus Observed Motion

Source seeds and `LandscapeSeed` documents can express conditions such as:

- a coherence transfer setup,
- a representative drift setup,
- an identity continuity setup,
- a frontier/boundary setup,
- a long-window relay setup,
- a dense fission setup.

They cannot assert that motion happened. Runtime evidence and observer records
decide that.

## Output Structure

Motion report directories normally contain:

```text
motion_reports/
  coherence_report.json
  coherence_summary.json
  representative_report.json
  representative_summary.json
  identity_report.json
  identity_summary.json
  boundary_report.json
  boundary_summary.json
  topological_report.json
  topological_summary.json
```

Session-level artifacts include:

```text
outputs/motion/sessions/S0001/run_report.json
outputs/motion/sessions/S0002/source_seeds/*.seed.json
outputs/motion/sessions/S0003/visualizations/*/motion_animation.gif
outputs/motion/sessions/S0004/interpretation/*.json
outputs/motion/sessions/S0005/interpretation/identity_fission_promotion_summary.json
outputs/motion/sessions/S0006/reviewed_motion_catalog.json
```

## Current Canonical Sessions

| Session | Purpose | Status |
|---|---|---|
| `S0001` | controlled structural examples | accepted observer fixtures and negative control |
| `S0002` | authored seed projections | accepted where runtime evidence matches; one composite ambiguous |
| `S0003` | long-window composites and animations | accepted/ambiguous/rejected/negative-control mix |
| `S0004` | complex Landscape Inference bridge examples | diagnostic for dense fission; useful complex motion evidence |
| `S0005` | dense confirmed fission positive control | accepted dense identity-fission evidence |
| `S0006` | reviewed motion catalog | closeout catalog |

## Validation Commands

Focused motion suite:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest \
  tests.landscapes.test_motion_catalog \
  tests.landscapes.test_motion_interpretation \
  tests.landscapes.test_motion_identity \
  tests.landscapes.test_motion_seed_examples
```

All motion-specific landscape tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest discover \
  -s tests/landscapes \
  -p 'test_motion*.py'
```

Visualization tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_motion
```

Compile check for the main motion modules:

```bash
PYTHONPATH=src ./.venv/bin/python -m py_compile \
  src/pygrc/landscapes/motion.py \
  src/pygrc/landscapes/motion_loader.py \
  src/pygrc/landscapes/motion_coherence.py \
  src/pygrc/landscapes/motion_representative.py \
  src/pygrc/landscapes/motion_identity.py \
  src/pygrc/landscapes/motion_boundary.py \
  src/pygrc/landscapes/motion_topological.py \
  src/pygrc/landscapes/motion_interpretation.py \
  src/pygrc/landscapes/motion_catalog.py
```

## Current Limitations

- Live `LandscapeSeed -> runtime -> telemetry` execution for motion seeds is
  not implemented yet. Current seed sessions are structural projections.
- Dense visual timelines can still be sampled for readability; visuals are not
  evidence promotion.
- Partial-graph/local-observer ignorance is not implemented.
- Lorentzian/proper-time motion and scale-indexed FRC motion are out of scope
  for the initial catalog.
- GRC9-only artifacts support mechanical/topological motion but not full
  GRCV3/GRC9V3 geometric identity semantics when those fields are absent.
- Boundary motion requires checkpoint-local evidence. Pressure-boundary or
  frontier labels alone are not geometric ridge proof.

## Recommended Operator Flow

1. Choose a telemetry artifact with checkpoints.
2. Load it with `load_motion_window`.
3. Run the observer matching the question:
   - coherence transfer,
   - representative drift,
   - identity continuity,
   - boundary/frontier motion,
   - topological support change.
4. Inspect `MotionRecord` evidence, competing claims, and degradation reasons.
5. Use static or animated visuals only as supporting review surfaces.
6. For dense identity split fields, run dense calibration and fission
   promotion before cataloging.
7. Use `S0006` as the current reviewed catalog of accepted, diagnostic,
   ambiguous, rejected, and negative-control motion cases.
