# Landscape Inference Reference Guide

This document is the operator guide for the Landscape Inference layer. It is a
mixture of reference, usage notes, and examples.

Landscape Inference observes runtime artifacts and maps evolved geometry back
into the existing `LandscapeSeed` primitive language. It does not define a
separate knowledge-graph ontology, and it does not mutate runtime dynamics.

## Scope

Landscape Inference answers questions like:

- Which identity basins are present in this evolved graph?
- Which persistent paths behave like valley channels?
- Which paths carry repeated activity and should be marked as pheromone or
  path-memory evidence?
- Which nodes behave like ridges, junctions, saddles, gates, or collapse sites?
- Which authored seed primitives were preserved, transformed, split,
  collapsed, dissolved, or replaced by emerged runtime structure?
- What dynamic knowledge-graph view can be exported from the observed
  landscape?

Landscape Inference does not:

- create runtime events,
- change coherence, flux, topology, budgets, or growth policy,
- promote pheromone markers into identity basins without basin evidence,
- classify pressure/frontier labels as ridges without checkpoint-local
  ridge evidence,
- turn authored source intent into proof that the runtime preserved it.

## Supported Families

Current loaders and classifiers support these telemetry families:

| Family | Support Level | Notes |
|---|---|---|
| `grcv3` | full geometric/hybrid inference when checkpoints expose geometry | Used in S0012-S0014 probes. |
| `grc9v3` | full hybrid inference when checkpoints expose port, basin, tensor, and event evidence | Strongest current synthetic probe family. |
| `grc9` | topology/mechanical inference with weaker geometric claims | No-event artifacts can still be useful as availability or negative cases. |

The artifact loader detects the family from telemetry family extensions, then
falls back to run identity if needed.

## Authority Model

Every inferred primitive is a normal `LandscapeSeed` primitive with inference
metadata in `primitive.extensions.landscape_inference`.

Authority values:

- `authored`: source seed primitive
- `lowered`: concrete runtime construction from a source/lowering layer
- `observed`: inferred primitive from runtime artifacts

Relationship values:

- `preserved`
- `transformed`
- `split`
- `collapsed`
- `emerged`
- `dissolved`
- `unknown`

The authority order is:

```text
runtime dynamics -> checkpoint/telemetry evidence -> observed classifier output -> KG/export view
```

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

Checkpoint evidence is the strongest local evidence source. Step-row and
run-summary aggregates are useful for selection and fallback, but they are not
enough for local basin, ridge, junction, valley, or pheromone claims.

## Core Python API

Import surface:

```python
from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    build_landscape_inference_evidence_substrate,
    infer_landscape_basin_seed,
    infer_landscape_valley_seed,
    infer_landscape_ridge_seed,
    infer_landscape_junction_seed,
    infer_landscape_pheromone_seed,
    infer_combined_observed_landscape_seed,
    write_inferred_landscape_and_kg_view,
    compare_landscape_seed_files,
    run_landscape_inference_revival_probe,
)
```

Most workflows should use:

1. `load_landscape_inference_artifacts(...)`
2. `build_landscape_inference_evidence_substrate(...)`
3. one or more `infer_landscape_*_seed(...)` functions
4. optionally `write_inferred_landscape_and_kg_view(...)`

## Loader Parameters

Function:

```python
load_landscape_inference_artifacts(
    path,
    *,
    window_policy="whole_run",
    start_step=None,
    end_step=None,
    final_step_count=None,
    event_step=None,
    radius=None,
)
```

Window policies:

| Policy | Parameters | Use |
|---|---|---|
| `whole_run` | none | Use the whole loaded artifact step range. |
| `explicit` | `start_step`, `end_step` | Use an exact inclusive step window. |
| `final` | `final_step_count` | Use the final N steps. |
| `event_centered` | `event_step`, `radius` | Use `event_step +/- radius`. |

Example:

```python
load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition",
    window_policy="whole_run",
)
```

## Evidence Substrate Parameters

Function:

```python
build_landscape_inference_evidence_substrate(
    load_result,
    *,
    allow_short_persistence_window=False,
)
```

Use `allow_short_persistence_window=True` for short diagnostic runs or examples
where fewer than three checkpoints are acceptable. Persistence-sensitive
classifiers should prefer at least three checkpoints.

The substrate normalizes:

- checkpoint nodes and edges,
- adjacency,
- bridge-edge tags,
- path candidates,
- path persistence and rupture,
- path flux-stability,
- port matrices,
- provenance and lowering tags,
- budget-audit evidence.

## Classifier Capabilities

Capability matrix:

| Capability | Classifier/Probe Id | Version | Emits |
|---|---|---|---|
| Basin inference | `landscape_inference_basin_classifier` | `landscape_inference_iter3_v1` | `basin` primitives |
| Valley/path inference | `landscape_inference_valley_classifier` | `landscape_inference_iter4_v1` | `valley` primitives |
| Ridge/boundary inference | `landscape_inference_ridge_classifier` | `landscape_inference_iter5_v1` | `ridge` primitives |
| Junction/saddle inference | `landscape_inference_junction_classifier` | `landscape_inference_iter6_v1` | `junction` and `saddle` primitives |
| Pheromone/path-memory inference | `landscape_inference_pheromone_classifier` | `landscape_inference_iter7_v1` | `valley` primitives with `role = "pheromone_marker"` |
| Authored-vs-observed comparison | `landscape_inference_primitive_comparison` | `landscape_inference_iter8_v1` | comparison report |
| Dynamic KG export | `dynamic_knowledge_graph_export` | `landscape_inference_iter9_v1` | KG-view JSON |
| Pheromone revival probe | `landscape_inference_pheromone_revival_probe` | `landscape_inference_optional_revival_v1` | diagnostic report |

### Basin Classifier

Functions:

```python
classify_landscape_basin_candidates(substrate, *, runtime_family)
infer_landscape_basin_seed(load_result, *, substrate=None, authored_seed=None)
```

Emits: `basin` primitives.

Evidence used:

- basin id or sink flag,
- member node persistence,
- basin mass or coherence fallback,
- gradient/Hessian evidence when available.

Output summary extension:

```text
seed.extensions.landscape_inference_basin_summary
```

Typical use:

```python
substrate = build_landscape_inference_evidence_substrate(load_result)
basin_seed = infer_landscape_basin_seed(load_result, substrate=substrate)
```

### Valley Classifier

Functions:

```python
classify_landscape_valley_candidates(
    substrate,
    *,
    runtime_family,
    max_paths_per_pair=8,
)
infer_landscape_valley_seed(
    load_result,
    *,
    substrate=None,
    authored_seed=None,
    max_valleys_per_endpoint_pair=1,
)
```

Emits: `valley` primitives with `role = "valley_channel"`.

Evidence used:

- checkpoint paths between basin endpoint sets,
- path persistence,
- path rupture,
- bottleneck conductance,
- mean absolute flux,
- directionality,
- bridge ambiguity tier,
- flux-stability score.

Important behavior:

- Bridge-only paths are not silently promoted to natural valleys.
- Low-significance paths can remain diagnostic-only.
- Emission is endpoint-deduplicated by default.

### Ridge Classifier

Functions:

```python
classify_landscape_ridge_candidates(
    substrate,
    *,
    runtime_family,
    gradient_threshold=1.0,
    tensor_anisotropy_threshold=1.0,
    low_throughflow_threshold=0.1,
)
infer_landscape_ridge_seed(load_result, *, substrate=None)
```

Emits: `ridge` primitives.

Evidence used:

- checkpoint-local gradient norm,
- tensor anisotropy or tensor trace,
- low throughflow,
- boundary/port evidence when available.

Important behavior:

- Pressure-boundary or frontier labels alone are not enough.
- Ridge inference is intentionally conservative.

### Junction And Saddle Classifier

Functions:

```python
classify_landscape_junction_candidates(
    load_result,
    *,
    substrate=None,
    active_flux_threshold=1e-12,
    curvature_degeneracy_threshold=1e-6,
)
infer_landscape_junction_seed(load_result, *, substrate=None)
```

Emits: `junction` and `saddle` primitives.

Evidence used:

- port matrix and active/free port state,
- incident edge and active flux counts,
- curvature degeneracy,
- event-backed collapse/choice evidence.

Roles include:

- `router`
- `gate`
- `collapse_site`
- saddle-like curvature sites

### Pheromone Classifier

Functions:

```python
classify_landscape_pheromone_candidates(
    load_result,
    *,
    substrate=None,
    max_paths_per_pair=8,
    min_flux_observed_steps=3,
    min_flux_observed_fraction=0.6,
)
infer_landscape_pheromone_seed(
    load_result,
    *,
    substrate=None,
    max_markers_per_endpoint_pair=1,
)
```

Emits: `valley` primitives with `role = "pheromone_marker"`.

Evidence used:

- repeated path activity,
- flux-observed step count,
- flux-observed fraction,
- path persistence,
- path flux-stability,
- event emphasis when available.

Important behavior:

- Pheromone markers are path-memory evidence.
- They are not identity basins.
- Promotion is reported only as a policy suggestion.

### Authored-Vs-Observed Comparison

Functions:

```python
compare_landscape_seeds(authored_seed, observed_seed, *, role_fallback_min_score=0.4)
compare_landscape_seed_files(authored_path, observed_path)
write_landscape_inference_comparison_report(report, output_root)
```

Outputs relationship records:

- `preserved`
- `transformed`
- `split`
- `collapsed`
- `emerged`
- `dissolved`
- `unknown`

Use this after creating an observed seed from a runtime artifact.

### Combined Observed Seed And KG View

Functions:

```python
infer_combined_observed_landscape_seed(
    load_result,
    *,
    authored_seed=None,
    substrate=None,
)

write_inferred_landscape_and_kg_view(
    load_result,
    output_root,
    *,
    authored_seed=None,
    source_seed_path=None,
)
```

Outputs:

```text
observed_landscape_seed.json
dynamic_kg_view.json
authored_vs_observed_comparison.json  # only when authored_seed is provided
```

The KG view is a projection of the observed `LandscapeSeed`. It is not a new
ontology.

### Pheromone Revival Probe

Functions:

```python
run_landscape_inference_revival_probe(
    load_result,
    *,
    substrate=None,
    revival_delta_threshold=1e-9,
)

write_landscape_inference_revival_probe_report(report, output_root)
```

This is a diagnostic probe, not a classifier that emits primitives.

It groups `choice_detected` and `collapse` emphasis events by primary node,
then checks whether the emphasized node later regains checkpoint-local
activity:

```text
activity = node.coherence + incident_abs_flux
```

Statuses:

- `revived_with_path_memory`
- `revived_without_path_memory`
- `path_memory_without_revival`
- `monitored_no_revival`

It does not apply path-memory feedback. Suppression/delay experiments require
a future runtime policy hook.

## Common Workflows

The examples below show both Python API usage and script-style terminal usage.
There is no standalone CLI wrapper for every capability yet, so script
examples use `PYTHONPATH=src ./.venv/bin/python - <<'PY'`.

### 1. Inspect An Artifact And Build The Evidence Substrate

API:

```python
from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    build_landscape_inference_evidence_substrate,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition",
    window_policy="whole_run",
)
substrate = build_landscape_inference_evidence_substrate(load_result)

print(load_result.source_runtime_family)
print(load_result.inference_window.to_mapping())
print(len(substrate.checkpoint_graphs))
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import (
    build_landscape_inference_evidence_substrate,
    load_landscape_inference_artifacts,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition",
    window_policy="whole_run",
)
substrate = build_landscape_inference_evidence_substrate(load_result)

print("runtime:", load_result.source_runtime_family)
print("window:", load_result.inference_window.to_mapping())
print("checkpoints:", len(substrate.checkpoint_graphs))
print("diagnostic_only:", substrate.diagnostic_only)
PY
```

### 2. Infer A Full Observed Landscape And KG View

API:

```python
from pathlib import Path

from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    load_landscape_seed,
    write_inferred_landscape_and_kg_view,
)

source_seed_path = Path(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)
load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition",
    window_policy="whole_run",
)
summary = write_inferred_landscape_and_kg_view(
    load_result,
    "outputs/landscape_inference/example_full_composition",
    authored_seed=load_landscape_seed(source_seed_path),
    source_seed_path=source_seed_path,
)
print(summary)
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pathlib import Path

from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    load_landscape_seed,
    write_inferred_landscape_and_kg_view,
)

source_seed_path = Path(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)
load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition",
    window_policy="whole_run",
)
summary = write_inferred_landscape_and_kg_view(
    load_result,
    "outputs/landscape_inference/examples/full_composition",
    authored_seed=load_landscape_seed(source_seed_path),
    source_seed_path=source_seed_path,
)
print(summary)
PY
```

Outputs:

```text
outputs/landscape_inference/examples/full_composition/observed_landscape_seed.json
outputs/landscape_inference/examples/full_composition/dynamic_kg_view.json
outputs/landscape_inference/examples/full_composition/authored_vs_observed_comparison.json
```

### 3. Run Only One Classifier

API:

```python
from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    build_landscape_inference_evidence_substrate,
    infer_landscape_valley_seed,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0068/lanes/corrected_propagated_front_relay"
)
substrate = build_landscape_inference_evidence_substrate(load_result)
valley_seed = infer_landscape_valley_seed(
    load_result,
    substrate=substrate,
    max_valleys_per_endpoint_pair=1,
)
print(valley_seed.extensions["landscape_inference_valley_summary"])
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pathlib import Path
import json

from pygrc.landscapes import (
    build_landscape_inference_evidence_substrate,
    infer_landscape_valley_seed,
    landscape_seed_to_data,
    load_landscape_inference_artifacts,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0068/lanes/corrected_propagated_front_relay"
)
substrate = build_landscape_inference_evidence_substrate(load_result)
seed = infer_landscape_valley_seed(
    load_result,
    substrate=substrate,
    max_valleys_per_endpoint_pair=1,
)

out = Path("outputs/landscape_inference/examples/valley_only")
out.mkdir(parents=True, exist_ok=True)
(out / "observed_valleys.seed.json").write_text(
    json.dumps(landscape_seed_to_data(seed), indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(seed.extensions["landscape_inference_valley_summary"])
PY
```

The same pattern works for:

```python
infer_landscape_basin_seed(...)
infer_landscape_ridge_seed(...)
infer_landscape_junction_seed(...)
infer_landscape_pheromone_seed(...)
```

### 4. Compare Authored And Observed Seeds

API:

```python
from pygrc.landscapes import (
    compare_landscape_seed_files,
    write_landscape_inference_comparison_report,
)

report = compare_landscape_seed_files(
    "configs/landscapes/seed/grcl9v3-corrected-propagated-front-relay.seed.yaml",
    "outputs/landscape_inference/sessions/S0013/corrected_propagated_front_relay/observed_landscape_seed.json",
)
write_landscape_inference_comparison_report(
    report,
    "outputs/landscape_inference/example_comparison",
)
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import (
    compare_landscape_seed_files,
    write_landscape_inference_comparison_report,
)

report = compare_landscape_seed_files(
    "configs/landscapes/seed/grcl9v3-corrected-propagated-front-relay.seed.yaml",
    "outputs/landscape_inference/sessions/S0013/corrected_propagated_front_relay/observed_landscape_seed.json",
)
json_path, markdown_path = write_landscape_inference_comparison_report(
    report,
    "outputs/landscape_inference/examples/comparison",
)
print("json:", json_path)
print("markdown:", markdown_path)
print("relationships:", report.to_mapping()["relationship_counts"])
PY
```

### 5. Run The Revival Probe

API:

```python
from pygrc.landscapes import (
    load_landscape_inference_artifacts,
    build_landscape_inference_evidence_substrate,
    run_landscape_inference_revival_probe,
    write_landscape_inference_revival_probe_report,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0055/lanes/corrected_multi_center_delayed_collapse_learning"
)
substrate = build_landscape_inference_evidence_substrate(load_result)
report = run_landscape_inference_revival_probe(load_result, substrate=substrate)
write_landscape_inference_revival_probe_report(
    report,
    "outputs/landscape_inference/example_revival_probe",
)
```

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import (
    build_landscape_inference_evidence_substrate,
    load_landscape_inference_artifacts,
    run_landscape_inference_revival_probe,
    write_landscape_inference_revival_probe_report,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0055/lanes/corrected_multi_center_delayed_collapse_learning"
)
substrate = build_landscape_inference_evidence_substrate(load_result)
report = run_landscape_inference_revival_probe(load_result, substrate=substrate)
json_path, markdown_path = write_landscape_inference_revival_probe_report(
    report,
    "outputs/landscape_inference/examples/revival_probe",
)
print("json:", json_path)
print("markdown:", markdown_path)
print("candidates:", report.candidate_count)
print("revived:", report.revived_candidate_count)
print("path-memory associated:", report.pheromone_associated_candidate_count)
PY
```

Replay the recorded S0014 probe:

```bash
PYTHONPATH=src ./.venv/bin/python outputs/landscape_inference/sessions/S0014/replay_revival_probe.py
```

### 6. Run Candidate Classification Without Emitting A Seed

Use this when tuning thresholds or inspecting why a classifier did or did not
emit primitives.

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import (
    build_landscape_inference_evidence_substrate,
    classify_landscape_ridge_candidates,
    load_landscape_inference_artifacts,
)

load_result = load_landscape_inference_artifacts(
    "outputs/grcl9v3/lowering/sessions/S0046/lanes/corrected_hybrid_full_composition"
)
substrate = build_landscape_inference_evidence_substrate(load_result)
candidates = classify_landscape_ridge_candidates(
    substrate,
    runtime_family=load_result.source_runtime_family,
    gradient_threshold=1.0,
    tensor_anisotropy_threshold=1.0,
    low_throughflow_threshold=0.1,
)

print("candidate_count:", len(candidates))
print("accepted:", sum(1 for c in candidates if c.status == "accepted"))
for candidate in candidates[:5]:
    print(candidate.to_mapping())
PY
```

### 7. Use A Different Inference Window

Script:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes import load_landscape_inference_artifacts

for policy, kwargs in (
    ("whole_run", {}),
    ("final", {"final_step_count": 5}),
    ("explicit", {"start_step": 4, "end_step": 10}),
    ("event_centered", {"event_step": 8, "radius": 2}),
):
    load_result = load_landscape_inference_artifacts(
        "outputs/grcl9v3/lowering/sessions/S0055/lanes/corrected_multi_center_delayed_collapse_learning",
        window_policy=policy,
        **kwargs,
    )
    print(policy, load_result.inference_window.to_mapping())
PY
```

## Replayable Reference Sessions

| Session | Purpose | Important Result |
|---|---|---|
| `outputs/landscape_inference/sessions/S0012` | Full observed seed and KG export over four selected synthetic probes | First full dynamic KG milestone. |
| `outputs/landscape_inference/sessions/S0013` | Valley significance, bridge ambiguity, and flux-stability refinements | Evidence quality improved without changing high-level primitive counts. |
| `outputs/landscape_inference/sessions/S0014` | Pheromone revival diagnostic | Found revival candidates and path-memory association in existing GRC9V3/GRCV3 long-window artifacts. |

Replay S0014:

```text
PYTHONPATH=src ./.venv/bin/python outputs/landscape_inference/sessions/S0014/replay_revival_probe.py
```

## Interpreting Results

### Primitive Counts

Primitive counts summarize the observed evolved geometry, not the authored
seed. For example, S0012 `corrected_hybrid_full_composition` produced:

```text
basin: 19
junction: 34
ridge: 19
saddle: 29
valley: 32
```

This means the runtime artifact supports a rich observed geometry. It does not
mean all authored primitives were preserved one-to-one.

### Relationship Counts

`split`, `dissolved`, and `emerged` relationships are normal in evolved
runtime artifacts. They often mean the runtime transformed or densified the
source geometry.

Do not treat `dissolved` as automatic failure. It means the observed classifier
did not find direct preservation evidence for that authored primitive id.

### Conservative Classifiers

Some classifiers are intentionally conservative:

- Ridge requires local gradient/tensor and low-throughflow evidence.
- Pheromone requires repeated path activity and remains a valley/path-memory
  marker.
- GRC9 mechanical-only runs may not support full geometric claims.

### Bridge Ambiguity

GRCL-lowered composite structures often contain bridge edges. The valley
classifier records bridge ambiguity tiers so bridge-mediated connections are
not silently claimed as natural runtime valleys.

Bridge tiers include:

- `none`
- `bridge_only`
- `bridge_at_endpoint`
- `bridge_in_middle`
- `bridge_mixed`

## Output Structure

Observed seed:

```text
observed_landscape_seed.json
```

Dynamic KG view:

```text
dynamic_kg_view.json
```

Authored-vs-observed comparison:

```text
authored_vs_observed_comparison.json
```

Revival probe:

```text
revival_probe_report.json
README.md
```

## Validation Commands

Focused landscape inference suite:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests/landscapes -p 'test_landscape_inference*.py'
```

Import smoke:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_import_smoke
```

## Current Limitations

- There is no standalone CLI wrapper for every capability yet; examples use
  the Python API and replay scripts.
- There is no dedicated plateau classifier yet. Plateau remains part of the
  neutral `LandscapeSeed` vocabulary, but current observed inference emits
  basins, valleys, ridges, junctions, saddles, pheromone markers, comparisons,
  KG views, and revival diagnostics.
- Pheromone revival feedback is not implemented. S0014 is diagnostic only.
- Ridge inference depends on checkpoint-local gradient/tensor evidence.
- GRC9-only artifacts can support topology/mechanical inference but not full
  GRCV3/GRC9V3 geometric claims when those fields are absent.
- Authored-vs-observed matching is conservative and may report `dissolved` or
  `emerged` where a human sees a looser conceptual continuity.

## Recommended Operator Flow

1. Choose a runtime artifact with checkpoints.
2. Load it with `load_landscape_inference_artifacts`.
3. Build a substrate with `build_landscape_inference_evidence_substrate`.
4. Run individual classifiers if debugging, or
   `write_inferred_landscape_and_kg_view` for the full output.
5. Compare against an authored seed when one exists.
6. Inspect summary extensions before reading every primitive.
7. Treat results as observed geometry, not as source-language claims.
