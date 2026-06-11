# Telemetry Reference Guide

This guide describes the telemetry artifacts written and loaded by PyGRC.
Telemetry is the evidence boundary for runtime behavior: step rows, event rows,
run summaries, graph checkpoints, selector reports, visual reviews, and
catalogs all derive from these artifacts.

## Scope

Use this guide when you want to:

- inspect runtime steps and events,
- load telemetry rows from a run directory,
- understand `family_extensions`,
- compare GRCV3, GRC9, GRC9V3, GRCL, landscape inference, and motion artifacts,
- locate graph checkpoints for visualization or inference,
- write scripts that summarize replay sessions.

Telemetry is observational. It should not be edited to make a run appear to
have produced an event or structure.

## Canonical Modules

| Module | Purpose |
|---|---|
| `src/pygrc/telemetry/schema.py` | Shared dataclasses for telemetry rows, summaries, and graph checkpoints. |
| `src/pygrc/telemetry/io.py` | Save/load helpers for JSON, JSONL, checkpoint packs, and artifact layouts. |
| `src/pygrc/telemetry/recorder.py` | Runtime capture boundary from step results into telemetry artifacts. |
| `src/pygrc/telemetry/grcv3_contract.py` | GRCV3 family extension contract. |
| `src/pygrc/telemetry/grc9_contract.py` | GRC9 family extension contract. |
| `src/pygrc/telemetry/grc9v3_contract.py` | GRC9V3 family extension contract. |
| `src/pygrc/telemetry/compare.py` | Shared run-summary comparison helper. |

## Core Record Types

PyGRC telemetry has three main runtime record types.

| Record | File | Meaning |
|---|---|---|
| `StepTelemetryRow` | `steps.jsonl` | One row per runtime step. Contains step index, time, event counts, observables, bookkeeping, and family extensions. |
| `EventTelemetryRow` | `events.jsonl` | One row per emitted runtime event. Contains event kind, event index, source family, payload, and family extensions. |
| `RunTelemetrySummary` | `run_summary.json` | One run-level summary. Contains initial/final observables, params, total event counts, status, and final family summaries. |

Graph-visible artifacts use:

| Record | File | Meaning |
|---|---|---|
| `GraphCheckpointArtifact` | `graph_checkpoints/<checkpoint_id>.json` or chunk JSONL | Node/edge records for one checkpoint. |
| `GraphCheckpointIndex` | `graph_checkpoints/index.json` | Selection policy and references to checkpoint files or chunks. |

Additional reports can include:

- `comparison_report.json`
- `experiment_report.json`
- selector manifests and selector reports,
- visual review reports,
- reviewed catalogs.

## Run Identity

Every step row, event row, summary, and checkpoint carries a
`RunTelemetryIdentity`.

Important identity fields:

- `run_id`
- `model_family`
- `params_identity`
- `seed_name`
- `seed_source_reference`
- `seed_path`
- `param_family`
- `rng_seed`
- `requested_steps`

`run_id` is deterministic over replay-critical inputs. It is not a human label;
session IDs such as `S0075` identify experiment folders, while `run_id`
identifies the replay configuration.

## Step Rows

Step rows contain compressed, per-step evidence.

Common fields:

- `identity`
- `step_index`
- `time`
- `event_count`
- `event_counts_by_kind`
- `observables`
- `bookkeeping`
- `family_extensions`

`observables` is the shared cross-family scalar surface. Family-specific
surfaces live under `family_extensions`.

Example field paths:

```text
observables.node_count
observables.edge_count
event_counts_by_kind.growth
bookkeeping.step_order
family_extensions.grc9v3.transport.flux_abs_sum
family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max
family_extensions.grcl9v3.expected_region_caches
```

## Event Rows

Event rows record lifecycle events emitted by the runtime.

Common fields:

- `identity`
- `step_index`
- `event_index`
- `event_kind`
- `source_family`
- `payload`
- `family_extensions`

Event rows are the strongest evidence for topology and lifecycle claims when
paired with checkpoint/summary consistency.

Example event kinds in current artifacts:

- `growth`
- `choice_detected`
- `collapse`
- `hybrid_spark_candidate`
- `hybrid_mechanical_expansion`
- `hybrid_spark_completed`

## Run Summaries

Run summaries aggregate one complete run.

Common fields:

- `completed_steps`
- `final_step_index`
- `initial_time`
- `final_time`
- `total_event_count`
- `event_counts_by_kind`
- `initial_observables`
- `final_observables`
- `resolved_params`
- `raw_params`
- `parameter_overrides`
- `status`
- `family_extensions`

Run summaries are the first place to inspect final counts and final state
summaries, but they are not a substitute for per-step and per-event review when
sequence matters.

## Graph Checkpoints

Graph checkpoints are checkpoint-local evidence used by visualization,
landscape inference, motion inference, and detailed replay review.

`GraphCheckpointArtifact` fields include:

- `checkpoint_id`
- `step_index`
- `time`
- `checkpoint_label`
- `graph_kind`
- `node_count`
- `edge_count`
- `node_records`
- `edge_records`
- `checkpoint_reason`
- `event_step_range`
- `event_count_window`
- `event_counts_by_kind_window`
- `flow_representation`
- `layout_mode`
- `layout_hints`
- `topology_extensions`
- `family_extensions`

Checkpoint records are intentionally richer than step-row aggregates. Use
checkpoints for per-node and per-edge questions.

## Family Extensions

Shared telemetry rows stay small and family-neutral. Family-specific evidence
is stored under `family_extensions.<family>`.

Current main runtime contracts:

| Family | Contract Version | Module |
|---|---|---|
| `grcv3` | `phase_t_iter26_v1` | `grcv3_contract.py` |
| `grc9` | `phase_t_grc9_iter1_v1` | `grc9_contract.py` |
| `grc9v3` | `phase_t_grc9v3_iter1_v1` | `grc9v3_contract.py` |

GRCL replay layers also add source/lowering namespaces such as:

- `family_extensions.grcl9`
- `family_extensions.grcl9v3`

These are not runtime families; they link lowered source intent to runtime
evidence surfaces.

## GRCV3 Extension Surface

GRCV3 telemetry focuses on semantic basin, Hessian, spark, hierarchy, choice,
frontier birth, and transient landscape surfaces.

Common groups:

- `backend`
- `basin_summary`
- `signed_hessian`
- `spark_state`
- `hierarchy`
- `choice_state`
- `frontier_birth_summary`
- `transient_landscape`

GRCV3 frontier birth is opt-in through explicit frontier-birth configuration.
Without that mode, old GRCV3 runs remain compatible but birth is disabled.

## GRC9 Extension Surface

GRC9 telemetry focuses on port charts, row tensors, spark calibration,
transport, identity/abundance, coarse graining, budget correction, expansion,
and growth.

Common groups:

- `backend_config`
- `port_chart`
- `row_tensor`
- `spark_calibration`
- `column_diagnostic`
- `transport`
- `identity_abundance`
- `coarse_graining`
- `budget_correction`
- `growth_summary`
- `expansion_summary`

Growth telemetry distinguishes corrected front-capacity growth, pressure
boundary growth, and legacy broad growth where those modes are present.

## GRC9V3 Extension Surface

GRC9V3 combines GRC9 mechanical surfaces with GRCV3 semantic surfaces and
hybrid interactions.

Common step groups:

- `backend_config`
- `port_chart`
- `row_basis_differential`
- `hybrid_tensor`
- `transport`
- `identity_basin`
- `hybrid_spark_state`
- `hierarchy_state`
- `choice_collapse`
- `growth_state`
- `budget_correction`
- `coarse_cache`
- `lane_context`

Common run-summary groups:

- `backend_summary`
- `final_port_chart_summary`
- `final_differential_summary`
- `final_identity_basin_summary`
- `final_hierarchy_summary`
- `final_choice_collapse_summary`
- `final_budget_summary`
- `lifecycle_event_counts`
- `representative_appendix_e_summary`

### GRC9V3 Spark Lane Telemetry

GRC9V3 spark lanes are recorded as runtime configuration and event evidence.
Do not infer the lane from `event_kind` alone: Lane A and Lane B both use
`hybrid_spark_candidate` for candidate events.

Backend configuration telemetry records the selected lane:

```text
family_extensions.grc9v3.backend_config.spark_lane
family_extensions.grc9v3.backend_config.spark_lane_version
```

Current values are:

| Value | Meaning |
|---|---|
| `current_hybrid_signed_hessian` | Lane A default baseline. |
| `grc9v3_column_h_assisted` | Lane B v1 opt-in column-H-assisted lane. |

Lane selection is not the same thing as a column-H branch firing. For Lane B
candidate events, inspect the event payload and event family extension:

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
payload.column_h_sign_crossing_mode
payload.eps_column_h_crossing_zero
family_extensions.grc9v3.spark_evidence.spark_lane
family_extensions.grc9v3.spark_evidence.column_h_branch_hit
```

Use these distinctions:

| Field | Interpretation |
|---|---|
| `spark_lane` | Which predicate lane produced or configured the evidence. |
| `lane_b_candidate_hit` | Full Lane B v1 predicate was satisfied. |
| `signed_hessian_hit` | Signed-Hessian branch fired. |
| `column_h_branch_hit` | Column-H threshold or sign-crossing branch fired. |
| `gate_reasons` | Branch-level reason list; may include both signed-Hessian and column-H reasons. |

Step telemetry carries the latest candidate summary when available:

```text
family_extensions.grc9v3.hybrid_spark_state.last_candidate_spark_lane
family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h
family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h
family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h_column
family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit
family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_gate_reasons
```

Graph checkpoint node overlays may include supporting Lane B diagnostics:

```text
family_extensions.grc9v3.node_overlay.<node_id>.spark_lane
family_extensions.grc9v3.node_overlay.<node_id>.column_h_computation_version
family_extensions.grc9v3.node_overlay.<node_id>.column_h
family_extensions.grc9v3.node_overlay.<node_id>.min_abs_column_h
family_extensions.grc9v3.node_overlay.<node_id>.min_abs_column_h_column
family_extensions.grc9v3.node_overlay.<node_id>.column_h_branch_hit
family_extensions.grc9v3.node_overlay.<node_id>.column_h_gate_reasons
family_extensions.grc9v3.node_overlay.<node_id>.column_h_diagnostic_source
```

Event rows are the primary causal evidence that a branch fired. Checkpoint
overlays are supporting evidence for replay, visualization, and node-local
inspection. Lane B direct evidence means direct runtime evidence that the
column-H proxy branch fired; `H_s[b]` remains a proxy diagnostic.

## GRCL Source/Lowering Extensions

GRCL-9 and GRCL-9V3 replay sessions add source/lowering metadata alongside
runtime family extensions.

Typical fields:

- `fixture_name`
- `replay_version`
- `source_schema_version`
- `lowering_manifest_version`
- `lowering_mode`
- `projector_revision`
- `source_construct_kinds`
- `expected_selector_ids`
- `expected_region_cache_names`
- `expected_region_caches`
- `growth_parent_eligibility_mode`
- `growth_parent_capacity_sources`
- `legacy_growth_locus_ids`

Expected-region caches are source/lowering expectations. They must be compared
against observed runtime telemetry before they become evidence.

## Artifact Layouts

Many sessions use this per-lane shape:

```text
<session_root>/
  session_manifest.json
  lanes/<lane_name>/
    telemetry/
      steps.jsonl
      events.jsonl
      run_summary.json
      graph_checkpoints/
        index.json
        step-00000000.json
        step-00000001.json
    snapshots/
      initial_snapshot.json
      final_snapshot.json
```

Some generic telemetry packs are stored through `TelemetryArtifactLayout`, with
the same logical files under a deterministic run directory.

Dense checkpoint captures may store checkpoints as chunked JSONL files. In
that case the `GraphCheckpointIndex` reference has
`storage_kind: "jsonl_chunk"` and a `chunk_line_index`.

## Loading Telemetry

### Load Step Rows

```python
from pygrc.telemetry.io import load_step_rows

steps = load_step_rows(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/steps.jsonl"
)

print(len(steps))
print(steps[0].step_index, steps[0].event_counts_by_kind)
```

### Load Event Rows

```python
from pygrc.telemetry.io import load_event_rows

events = load_event_rows(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/events.jsonl"
)

print([event.event_kind for event in events])
```

### Load A Run Summary

```python
from pygrc.telemetry.io import load_run_summary

summary = load_run_summary(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/run_summary.json"
)

print(summary.status)
print(summary.event_counts_by_kind)
print(summary.family_extensions["grc9v3"]["contract_version"])
```

### Load Graph Checkpoints

For direct file-backed checkpoints:

```python
from pathlib import Path
from pygrc.telemetry.io import load_graph_checkpoint, load_graph_checkpoint_index

telemetry_root = Path(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry"
)
index = load_graph_checkpoint_index(telemetry_root / "graph_checkpoints/index.json")
first_ref = index.checkpoints[0]
checkpoint = load_graph_checkpoint(telemetry_root / "graph_checkpoints" / first_ref.path)

print(checkpoint.checkpoint_id, checkpoint.node_count, checkpoint.edge_count)
```

For chunk-backed checkpoint captures, use `load_graph_checkpoint_from_reference`
with a full `TelemetryArtifactLayout`.

## Script Examples

### Summarize One Lane

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.telemetry.io import load_event_rows, load_run_summary, load_step_rows

root = (
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry"
)
steps = load_step_rows(f"{root}/steps.jsonl")
events = load_event_rows(f"{root}/events.jsonl")
summary = load_run_summary(f"{root}/run_summary.json")

print("steps", len(steps))
print("events", [event.event_kind for event in events])
print("summary_counts", dict(summary.event_counts_by_kind))
print("families", sorted(summary.family_extensions))
PY
```

### Read A Nested Field Path

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.telemetry.io import load_run_summary

def get_path(payload, path, default=None):
    value = payload
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value

summary = load_run_summary(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/run_summary.json"
)
payload = {"family_extensions": dict(summary.family_extensions)}
print(get_path(payload, "family_extensions.grc9v3.lifecycle_event_counts.growth_count"))
print(get_path(payload, "family_extensions.grc9v3.lifecycle_event_counts.pressure_boundary_growth_count"))
PY
```

### Count Events Across A Session

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from collections import Counter
from pathlib import Path
from pygrc.telemetry.io import load_event_rows

session = Path("outputs/grcl9v3/lowering/sessions/S0075")
counts = Counter()
for path in sorted(session.glob("lanes/*/telemetry/events.jsonl")):
    counts.update(event.event_kind for event in load_event_rows(path))

print(dict(sorted(counts.items())))
PY
```

### Find And Reuse A Replay Command

Most replay sessions record a runnable command in `session_manifest.json` and
often provide `replay.sh`.

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

manifest = json.loads(
    Path("outputs/grcl9v3/lowering/sessions/S0075/session_manifest.json")
    .read_text(encoding="utf-8")
)
print(manifest["replay_command"])
PY
```

When a session has `replay.sh`, rerun it from the repository root:

```bash
bash outputs/grcl9v3/lowering/sessions/S0075/replay.sh
```

### Inspect Checkpoint Sizes

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pathlib import Path
from pygrc.telemetry.io import load_graph_checkpoint, load_graph_checkpoint_index

root = Path(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry"
)
index = load_graph_checkpoint_index(root / "graph_checkpoints/index.json")
for ref in index.checkpoints:
    if ref.storage_kind != "file":
        print(ref.checkpoint_id, ref.storage_kind)
        continue
    checkpoint = load_graph_checkpoint(root / "graph_checkpoints" / ref.path)
    print(ref.checkpoint_id, checkpoint.node_count, checkpoint.edge_count)
PY
```

### Compare Two Run Summaries

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.telemetry.compare import compare_run_summaries
from pygrc.telemetry.io import load_run_summary

left = load_run_summary(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/run_summary.json"
)
right = load_run_summary(
    "outputs/grcl9v3/lowering/sessions/S0075/lanes/"
    "pressure_boundary_positive_control/telemetry/run_summary.json"
)
report = compare_run_summaries(left, right)
print(report.common["total_event_count_right_minus_left"])
print(dict(report.common["event_counts_by_kind_right_minus_left"]))
PY
```

## Writing Telemetry

Most users should not write telemetry rows by hand. Runtime/session runners
call `capture_run_telemetry(...)`, which:

1. builds a deterministic run identity,
2. converts ordered step results into step rows,
3. converts emitted events into event rows,
4. builds the run summary,
5. merges shared, per-step, per-event, and summary family extensions,
6. optionally writes artifacts with `TelemetryCaptureConfig(write_artifacts=True)`.

When adding a new runner, prefer:

```python
from pygrc.telemetry.recorder import capture_run_telemetry
```

and provide family extensions through the relevant contract helpers, for
example:

```python
from pygrc.telemetry.grc9v3_contract import (
    grc9v3_event_family_extensions,
    grc9v3_run_summary_family_extensions,
    grc9v3_step_family_extensions,
)
```

## Selector And Catalog Use

Selectors usually address telemetry with dot paths such as:

```text
family_extensions.grc9v3.transport.flux_abs_sum
family_extensions.grc9v3.lifecycle_event_counts.growth_count
family_extensions.grcl9v3.expected_region_caches
```

Selector reports should distinguish:

- field present and predicate passed,
- field present and predicate failed,
- missing telemetry surface,
- capability disabled,
- diagnostic-only legacy evidence.

Reviewed catalogs should cite source session IDs, selector manifests, run
summary fields, event rows, and checkpoint artifacts rather than duplicating
full telemetry payloads.

## Troubleshooting

Common issues:

- Missing `steps.jsonl`, `events.jsonl`, or `run_summary.json`: the run did not
  write a standard telemetry pack.
- Missing graph checkpoints: the runner did not enable checkpoint capture, or
  the session stores only snapshots.
- Empty `events.jsonl`: no events were emitted; inspect step rows and final
  summaries before assuming a failure.
- Missing `family_extensions.<family>`: the runner did not attach a family
  contract extension, or the artifact belongs to a different family.
- Contract version mismatch: use the family contract module to determine which
  fields are valid for that artifact.
- Legacy growth fields present: check whether the session is diagnostic-only.

## Related Guides

- [Landscape Compiler And Lowering Reference Guide](LandscapeCompiler-ReferenceGuide.md)
- [Landscape Inference Reference Guide](LandscapeInference-ReferenceGuide.md)
- [Motion Reference Guide](Motion-ReferenceGuide.md)
- [Graph Visualization Reference Guide](GraphVisualization-ReferenceGuide.md)
  covers rendering checkpoint and telemetry graph artifacts.
- [Catalogs And Evidence Reference Guide](Catalogs-And-Evidence-ReferenceGuide.md)
  covers selector and reviewed catalog interpretation.
