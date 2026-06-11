# GRC9V3 Examples

This directory is the first usage-focused example lane for PyGRC.

The goal is not to restate the reference guides. The goal is to make the
documented surfaces easy to run and inspect.

## Questions These Examples Should Answer

### How do I construct and run `GRC9V3`?

The baseline example should show the smallest useful runtime path:

```python
from pygrc.models import GRC9V3

model = GRC9V3.from_config({"dt": 0.1})
result = model.step()
print(result.step_index)
print(result.events)
print(result.observables)
```

Reference:
[GRC Runtime Reference Guide](../../docs/reference/GRC-Runtime-ReferenceGuide.md)

### How do I select Lane A or Lane B?

Lane A is the default:

```text
spark_lane = current_hybrid_signed_hessian
```

Lane B is opt-in:

```python
model = GRC9V3.from_config(
    {
        "dt": 0.1,
        "constitutive_semantic_modes": {
            "spark_lane": "grc9v3_column_h_assisted",
        },
        "evolution": {
            "eps_column_h": 1e-4,
        },
    }
)
```

The example should make this distinction observable:

```text
Lane A:
    signed-Hessian baseline, column-H non-gating

Lane B:
    direct runtime evidence that the column-H proxy branch may fire
```

Reference:
[GRC Runtime Reference Guide - GRC9V3 Spark Lanes](../../docs/reference/GRC-Runtime-ReferenceGuide.md#grc9v3-spark-lanes)

### How do I inspect candidate event evidence?

The event evidence example should inspect `hybrid_spark_candidate` payloads.
Do not infer Lane A versus Lane B from the event kind alone.

Important fields:

```text
payload.spark_lane
payload.lane_b_candidate_hit
payload.signed_hessian_hit
payload.column_h_branch_hit
payload.column_h_threshold_hit
payload.column_h_sign_crossing_hit
payload.gate_reasons
payload.column_h
payload.min_abs_column_h
payload.min_abs_column_h_column
```

Interpretation:

```text
lane_b_candidate_hit:
    full Lane B v1 predicate fired

column_h_branch_hit:
    column-H threshold or sign-crossing branch fired

signed_hessian_hit:
    signed-Hessian branch fired
```

A Lane B candidate can be signed-Hessian-only. Only call it a direct column-H
proxy-branch event when `column_h_branch_hit` is true or a column-H reason is
present in `gate_reasons`.

Reference:
[Telemetry Reference Guide - GRC9V3 Spark Lane Telemetry](../../docs/reference/Telemetry-ReferenceGuide.md#grc9v3-spark-lane-telemetry)

### How do I capture telemetry?

The telemetry example should:

1. construct a `GRC9V3` model;
2. compute initial observables;
3. run a small number of steps;
4. compute final observables;
5. call `capture_run_telemetry`;
6. write artifacts under `outputs/examples/`.

Key outputs:

```text
steps.jsonl
events.jsonl
run_summary.json
graph_checkpoints/
```

Reference:
[Telemetry Reference Guide](../../docs/reference/Telemetry-ReferenceGuide.md)

### How do I render the visual bundle?

The visual example should load a telemetry artifact pack and render:

```text
trajectories.png
events.png
report_panel.png
graph_snapshots/
graph_html/final_graph.html
graph_sequence.png
graph_animation.gif
```

For Lane B, visual interpretation should distinguish:

```text
lane_a_signed_hessian_candidate
lane_b_signed_hessian_candidate
lane_b_column_h_branch_candidate
```

Visuals remain supporting evidence. Event payloads and telemetry contracts
remain authoritative.

Reference:
[Graph Visualization Reference Guide - GRC9V3 Lane B Visuals](../../docs/reference/GraphVisualization-ReferenceGuide.md#grc9v3-lane-b-visuals)

### Which imports feel stable enough to document?

Examples should prefer imports that are likely to remain stable:

```python
from pygrc.models import GRC9V3
from pygrc.telemetry.recorder import capture_run_telemetry
from pygrc.telemetry.io import build_telemetry_artifact_layout
from pygrc.visualization import render_run_visual_bundle
```

If an example needs a deep internal import, that is useful pressure. It means
the workflow may need a public helper before PyGRC is treated as a stable
library.

## GRC9V3 Examples

Run the first batch from the repository checkout with the project virtualenv:

```bash
.venv/bin/python examples/grc9v3/lane_a_baseline.py
.venv/bin/python examples/grc9v3/lane_b_column_h.py
.venv/bin/python examples/grc9v3/lane_a_vs_lane_b.py
```

| Example | Status | Purpose |
|---|---|---|
| `lane_a_baseline.py` | Available | Load a small `GRC9V3` fixture, print its model/topology shape, then run default Lane A. |
| `lane_b_column_h.py` | Available | Minimal opt-in Lane B candidate and event evidence inspection. |
| `lane_a_vs_lane_b.py` | Available | Side-by-side Lane A/Lane B comparison on a small fixture. |
| `telemetry_capture.py` | Available | Capture a Lane B spark-layer run into standard telemetry artifacts. |
| `visual_bundle.py` | Available | Render behavior and graph visuals from the telemetry artifacts. |

Keep each script short enough to read without knowing the experiment history.

## Shared Fixture Contract

The first examples use a local helper:

```text
examples/grc9v3/_fixtures.py
```

This helper is not meant to be a hidden model loader or a stable public API.
It is a small, deterministic runtime fixture so the example scripts can focus
on how to use `GRC9V3`.

### What The Fixture Does

The fixture builds a runtime `GRC9V3` state directly, then loads it with:

```python
GRC9V3.from_state(state, config)
```

The loaded model is:

```text
model:
    GRC9V3

center node:
    node 0

topology:
    10 nodes
    9 edges
    node 0 connected to neighbors 1..9
    node 0 occupies ports 1..9

sink set:
    [0]

center node fields:
    coherence = 10.0
    gradient_row_basis = [0.0, 0.0, 0.0]
    signed_hessian_row_basis = [1.0, 1.0, 1.0]
```

The fixture is saturated by construction:

```text
active_degree(node 0) == 9
```

It is also inside the small-gradient envelope:

```text
gradient_norm(node 0) == 0.0
```

But it does not satisfy the Lane A signed-Hessian branch:

```text
signed_hessian_min(node 0) == 1.0
eps_spark == 0.0
Lane A candidate -> no
```

### Port Table

The fixture attaches one neighbor per local port.

| Port | Row | Column | Neighbor | Neighbor coherence | Base conductance | Contribution to `H[column]` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 13.0 | 0.5 | 1.5 |
| 2 | 1 | 2 | 2 | 9.0 | 1.0 | -1.0 |
| 3 | 1 | 3 | 3 | 7.0 | 1.0 | -3.0 |
| 4 | 2 | 1 | 4 | 8.0 | 2.0 | -4.0 |
| 5 | 2 | 2 | 5 | 11.0 | 2.0 | 2.0 |
| 6 | 2 | 3 | 6 | 10.0 | 2.0 | 0.0 |
| 7 | 3 | 1 | 7 | 10.25 | 4.0 | 1.0 |
| 8 | 3 | 2 | 8 | 10.0 | 5.0 | 0.0 |
| 9 | 3 | 3 | 9 | 12.0 | 0.25 | 0.5 |

Using:

```text
H_s[b] = sum_a w_s[a,b] * (C_neighbor(s,a,b) - C_s)
```

the expected column-H vector is:

```text
H = [-1.5, 1.0, -2.5]
min_abs_column_h = 1.0
min_abs_column_h_column = 2
```

The examples use:

```text
eps_column_h = 1.1
```

So Lane B can fire through:

```text
column_h_threshold_hit
```

while Lane A still does not fire.

### What The Fixture Needs

The fixture needs:

- a Python environment with PyGRC dependencies installed;
- access to `src/pygrc`;
- the `GRC9V3` runtime model;
- a direct runtime state dictionary with topology, node state, port-edge
  records, base conductance, sink set, and basin membership;
- a config dictionary selecting Lane A or Lane B.

Run examples from the repository root:

```bash
.venv/bin/python examples/grc9v3/lane_a_baseline.py
```

The helper inserts `src/` into `sys.path` only so examples can run from a
checkout before packaging is finalized. That is example scaffolding, not a
recommended public import pattern.

## Telemetry And Visual Output

The telemetry example writes to:

```text
outputs/examples/grc9v3/lane_b_column_h_telemetry/
```

Key files:

```text
telemetry/steps.jsonl
telemetry/events.jsonl
telemetry/run_summary.json
telemetry/graph_checkpoints/index.json
```

The visual example reads that artifact pack and writes:

```text
outputs/examples/grc9v3/lane_b_column_h_telemetry/visualization/
```

Key files:

```text
trajectories.png
events.png
graph_sequence.png
graph_html/final_graph.html
graph_layouts.json
graph_animation.gif
```

`visual_bundle.py` will run `telemetry_capture.py` first if the telemetry
artifacts are missing.

### Why This Is Not A Landscape Example

This fixture is already runtime state. It is not authored landscape source.

That is intentional for the first batch because the first question is:

```text
How do I construct and inspect a GRC9V3 runtime model?
```

Landscape examples should answer a different question:

```text
How do I author/load/validate/lower a source landscape into a runtime model?
```

Those examples will live under:

```text
examples/grc9v3/landscapes/
```

### Alternatives To This Fixture

Use:

| Need | Use |
|---|---|
| Small default model | `GRC9V3.from_config(...)` |
| Explicit runtime state | `GRC9V3.from_state(...)` |
| Saved runtime snapshot | `GRC9V3.load(...)` |
| Authored source landscape | landscape seed loading and lowering |
| Full experiment evidence | reports under `experiments/` |

The fixture should remain local to examples unless repeated usage creates real
pressure for a public helper.

## Landscapes

GRC9V3 can be run from authored or normalized landscape sources rather than
hand-assembled runtime states.

This examples area should include a GRC9V3 landscape path that answers:

- How do I define a landscape seed?
- How do I load an existing seed?
- How do I validate it?
- How do I lower or project it into `GRC9V3`?
- How do I run the resulting model?
- How do I capture telemetry and visuals for that run?

### Defining A Landscape

Normalized landscape seeds live under:

```text
configs/landscapes/seed/
```

They are source-side descriptions. They are not runtime evidence until they are
loaded, validated, lowered/projected, and executed.

Reference:
[Landscape Language Reference Guide](../../docs/reference/LandscapeLanguage-ReferenceGuide.md)

### Loading A Landscape

The basic loading path is:

```python
from pygrc.landscapes.io import load_landscape_seed

seed = load_landscape_seed(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)
print(seed.meta.name)
```

### Running A Landscape Through GRC9V3

Use the landscape compiler/lowering route when the source is GRCL-9V3-facing,
or the model landscape helpers when running a seed-backed runtime projection.

Relevant reference surfaces:

- [Landscape Compiler And Lowering Reference Guide](../../docs/reference/LandscapeCompiler-ReferenceGuide.md)
- [GRC Runtime Reference Guide - Source And Landscape Helpers](../../docs/reference/GRC-Runtime-ReferenceGuide.md#source-and-landscape-helpers)

Planned landscape examples:

| Example | Purpose |
|---|---|
| `landscapes/load_seed.py` | Load and inspect a normalized landscape seed. |
| `landscapes/run_seed.py` | Build/run a GRC9V3 model from a landscape source. |
| `landscapes/telemetry_and_visuals.py` | Capture telemetry and render visuals for the landscape run. |

## Claim Boundary

Examples are usage checks. They do not establish new theory claims.

Use examples to learn the runtime and discover API friction. Use telemetry,
reports, and experiment artifacts for evidence claims.
