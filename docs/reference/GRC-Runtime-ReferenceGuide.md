# GRC Runtime Reference Guide

This guide describes the executable GRC runtime families in PyGRC: how to
construct them, run `.step()`, inspect capabilities, use growth and
coarse-graining surfaces, and capture runtime telemetry.

Use this guide when you want the runtime API itself. Use the telemetry,
landscape compiler, GRCL, and visualization guides for artifact review and
source-language workflows.

## Scope

This guide covers:

- `GRCV2`
- `GRCV3`
- `GRC9`
- `GRC9V3`
- the shared `GRCModel` interface,
- runtime parameter conventions,
- accepted front/pressure-boundary growth behavior,
- legacy growth warnings,
- column coarse-graining and Split support,
- minimal API and script examples.

Runtime models produce behavior. Telemetry, inference, motion, catalogs, and
visuals observe that behavior. Do not treat source-language declarations or
visual overlays as runtime evidence unless they are backed by step/event/checkpoint
artifacts.

## Canonical Modules

| Module | Purpose |
|---|---|
| `src/pygrc/core/interfaces.py` | Shared `GRCModel` API. |
| `src/pygrc/core/types.py` | Shared `GRCState` and `StepResult` dataclasses. |
| `src/pygrc/core/params.py` | Immutable `GRCParams` and canonical parameter identity. |
| `src/pygrc/core/capabilities.py` | Capability vocabulary and family profiles. |
| `src/pygrc/models/grc_v2.py` | GRCV2 runtime. |
| `src/pygrc/models/grc_v3.py` | GRCV3 runtime. |
| `src/pygrc/models/grc_9.py` | GRC9 runtime. |
| `src/pygrc/models/grc_9_v3.py` | GRC9V3 runtime. |
| `src/pygrc/models/grc_9_coarse.py` | Pure GRC9 column coarse-graining/Split helpers. |
| `src/pygrc/telemetry/recorder.py` | Capture step results into telemetry rows and summaries. |

Related engineering records:

- `implementation/Phase-5-ImplementationChecklist.md`
- `implementation/Phase-6-ImplementationChecklist.md`
- `implementation/Phase-7-ImplementationChecklist.md`
- `implementation/PressureBoundary-ImplementationPlan.md`
- `implementation/PressureBoundary-ImplementationChecklist.md`

## Shared Runtime API

Every runtime family implements `GRCModel`.

Common methods:

| Method | Meaning |
|---|---|
| `from_config(config)` | Build from JSON/YAML-friendly params and optional state. |
| `from_state(state, params)` | Restore from serialized state plus params. |
| `load(path)` | Load a saved snapshot. |
| `get_state()` | Return the family state object. |
| `set_state(state)` | Replace state after validation. |
| `get_params()` | Return resolved immutable `GRCParams`. |
| `list_capabilities()` | Return advertised capability strings. |
| `compute_observables()` | Compute current family observables. |
| `step()` | Advance exactly one runtime step. |
| `run(num_steps)` | Call `step()` repeatedly. |
| `reset()` | Restore construction-time state. |
| `snapshot()` | Return a serialization-safe `BaseSnapshot` per the shared interface. Current concrete runtime families serialize snapshots as JSON-safe mappings. |
| `save(path)` | Persist a model snapshot. |

`step()` returns `StepResult`:

```python
@dataclass
class StepResult:
    step_index: int
    time: float
    events: list[GRCEvent]
    observables: dict[str, object]
    bookkeeping: dict[str, object]
```

`bookkeeping["step_order"]` records the actual loop stages for that step. This
is the first place to check when validating which runtime stages ran.

Each concrete runtime also exposes `MODEL_FAMILY`, such as `GRCV3`, `GRC9`, or
`GRC9V3`. Telemetry capture uses this family token to label runtime artifacts.

## Runtime Families

| Family | Main Role | Current Status |
|---|---|---|
| `GRCV2` | Early weighted-edge identity, proxy spark, soft split, front birth, and budget-preservation runtime. | Supported for historical and comparative runs. Requires explicit full parameter maps. |
| `GRCV3` | Semantic basin/hierarchy/choice/collapse runtime with geometric/Hessian evidence and optional pressure-boundary frontier birth. | Supported Phase 5 family. Birth is disabled unless explicitly enabled. |
| `GRC9` | Nine-port mechanical runtime with spark expansion, corrected front-capacity growth, pressure-boundary provenance, budget closure, and column coarse-graining. | Supported Phase 6 family. Legacy broad growth is diagnostic only. |
| `GRC9V3` | Hybrid runtime combining GRC9 nine-port mechanics with GRCV3 semantic basin, choice/collapse, quadrature budget, transport, Hessian, and coarse-graining surfaces. | Supported Phase 7 family. Preferred hybrid family for paper-facing GRC9V3 evidence. |

## Capabilities

Capabilities are family-level claims validated by `CapabilityProfile`.

Common capability strings:

- `single_weight_edges`
- `multi_metric_edges`
- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`
- `basin_attributes`
- `hierarchy_tracking`
- `choice_collapse_semantics`
- `quadrature_budget`
- `intrinsic_frame`
- `host_embedding_frame`
- `boundary_barrier`
- `identity_basins`
- `proxy_sparks`
- `soft_split`
- `front_birth`
- `budget_preservation`

Example:

```python
from pygrc.models import GRC9V3

model = GRC9V3.from_config({"dt": 0.1})
print(sorted(model.list_capabilities()))
```

## Parameters

Runtime params are resolved into immutable `GRCParams`.

Top-level parameter domains:

- `dt`
- `evolution`
- `constitutive_semantic_modes`
- `numerical_backend`

The core params object rejects runtime/tooling/observer domains. Keep run
output paths, visualization options, and telemetry settings outside runtime
params.

`GRCV3`, `GRC9`, and `GRC9V3` merge family defaults before validation. `GRCV2`
is stricter and requires explicit evolution and mode parameters.

For GRCV2 spark thresholding, provide either `evolution.eps_spark` or
`evolution.h_thr`. The explicit example below uses `eps_spark`.

## Minimal Step Examples

### GRCV3

```python
from pygrc.models import GRCV3

model = GRCV3.from_config({"dt": 0.1})
result = model.step()

print(result.step_index, result.time)
print(result.events)
print(result.observables)
print(result.bookkeeping["step_order"])
```

### GRC9

```python
from pygrc.models import GRC9

model = GRC9.from_config({"dt": 0.1})
results = model.run(3)

print(results[-1].step_index)
print(model.compute_observables())
print(sorted(model.list_capabilities()))
```

### GRC9V3

```python
from pygrc.models import GRC9V3

model = GRC9V3.from_config({"dt": 0.1})
result = model.step()

print(result.bookkeeping["step_order"])
print(result.observables)
print(model.get_state().cached_quantities.get("coarse_cache_state"))
```

#### GRC9V3 Spark Lanes

GRC9V3 currently exposes two spark lanes.

| Lane | Config value | Meaning |
|---|---|---|
| Lane A | `current_hybrid_signed_hessian` | Default baseline. Uses active-degree saturation, the small-gradient basin-interior envelope, and the signed-Hessian branch. Column-H may be analyzed as a derived diagnostic, but it does not gate candidates. |
| Lane B v1 | `grc9v3_column_h_assisted` | Opt-in lane. Keeps the GRC9V3 saturation and small-gradient envelope, then allows either the signed-Hessian branch or a direct runtime-computed column-H proxy branch to produce candidates. |

Enable Lane B explicitly:

```python
from pygrc.models import GRC9V3

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

Lane B v1 applies this predicate shape:

```text
active_degree(s) == 9
AND gradient_norm(s) < eps_gradient
AND (
    min_signed_hessian(s) < eps_signed_hessian
    OR min_b abs(H_s[b]) < eps_column_h
    OR column_h_sign_crossing_hit(s)
)
```

with:

```text
H_s[b] = sum_a w_s[a,b] * (C_neighbor(s,a,b) - C_s)
```

Lane B does not make `H_s[b]` the true geometric Hessian. It emits direct
runtime evidence that the column-H proxy branch fired when the candidate event
payload has `spark_lane = "grc9v3_column_h_assisted"` and
`column_h_branch_hit = true`. A Lane B candidate may also fire by
`signed_hessian_hit` alone, so distinguish the full lane candidate from the
column-H branch.

Lane B v1 remains sink-only, degree-9-only, and non-identity-producing. Degree-8
near-saturation, virtual zero-conductance stubs, broader non-sink candidate
scope, mechanical expansion changes, and identity acceptance changes are not
part of this runtime lane.

### GRCV2

`GRCV2` does not currently provide broad defaults. Use an explicit config:

```python
from pygrc.models import GRCV2

config = {
    "dt": 0.1,
    "evolution": {
        "alpha": 1.0,
        "beta": 1.0,
        "gamma": 1.0,
        "delta": 1.0,
        "eta": 1.0,
        "kappa_c": 1.0,
        "lambda_c": 0.0,
        "xi_c": 0.0,
        "zeta_c": 0.0,
        "tau_split": 1.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.0,
        "eps_prune": 0.0,
        "eps_spark": 0.0,
        "site_potential_selection": "quadratic",
        "site_potential_params": {},
    },
    "constitutive_semantic_modes": {
        "curvature_backend": "none",
        "frame_mode": "combinatorial",
        "boundary_mode": "prune",
        "split_distribution_mode": "equal",
        "edge_label_selection": "all",
    },
}

model = GRCV2.from_config(config)
result = model.step()
print(result.observables)
```

## Step Loop Shapes

Runtime families share the same `step()` contract but do not share the same
internal stages.

### GRCV3

The Phase 5 loop computes differential summaries, tensors, metric, labels,
potential, flux, identities, spark/split/choice state, optional frontier birth,
continuity, budget, and final refresh.

Default step order:

1. `compute_differential_summary_pre_flux`
2. `compute_node_tensors`
3. `compute_metric`
4. `compute_edge_labels_pre_flux`
5. `compute_potential`
6. `compute_flux`
7. `compute_edge_labels_post_flux`
8. `refresh_differential_summary_post_flux`
9. `detect_identities`
10. `detect_sparks`
11. `advance_splits`
12. `update_choice_state`
13. `apply_continuity`
14. `enforce_budget`
15. `refresh_runtime_state`
16. `compute_observables`

Frontier birth stage:

- runs only when `constitutive_semantic_modes.frontier_birth_mode` is
  `active_frontier_pressure`,
- inserts `apply_frontier_birth` after `update_choice_state`,
- remains disabled when the mode is missing or explicitly `disabled`,
- warns or errors on disabled modes with declared candidates according to
  `frontier_birth_strict`.

### GRC9

The Phase 6 loop computes row tensor, metric, edge labels, potential, flux,
identities, spark detection, mechanical expansion, growth, boundary behavior,
continuity, budget, coarse-cache refresh/invalidation, and observables.

Accepted growth evidence must use corrected front-capacity semantics.

### GRC9V3

The Phase 7 loop computes row-basis differential state, scalar transport,
post-flux differential refresh, flux-topology and geometric identities, hybrid
spark candidate/expansion/stabilization, choice/collapse/learning, growth,
boundary behavior, continuity, quadrature budget, final refresh, coarse-cache
refresh/invalidation, and observables.

Full step order:

1. `compute_row_basis_gradient_pre_flux`
2. `compute_signed_hessian_row_basis_pre_flux`
3. `compute_net_flux_summary_pre_flux`
4. `compute_node_tensors`
5. `compute_base_conductance`
6. `compute_edge_labels_pre_flux`
7. `compute_potential`
8. `compute_flux`
9. `compute_edge_labels_post_flux`
10. `refresh_differential_summary_post_flux`
11. `detect_flux_topology_identities`
12. `validate_geometric_basin_seeds`
13. `compute_effective_basin_masses`
14. `detect_hybrid_spark_candidates`
15. `apply_mechanical_expansion`
16. `refresh_after_expansion`
17. `evaluate_child_basin_stabilization`
18. `register_completed_hybrid_sparks`
19. `update_hierarchy`
20. `update_choice_collapse_learning`
21. `apply_growth`
22. `apply_boundary_behavior`
23. `apply_continuity`
24. `enforce_quadrature_budget`
25. `refresh_runtime_state_final`
26. `refresh_or_invalidate_coarse_cache`
27. `compute_observables`

GRC9V3 inherits the GRC9 column coarse-graining contract and adds hybrid
transport and semantic evidence surfaces.

## Growth Semantics

The current accepted growth model is conservative:

1. A birth/growth event may be probabilistic under outward flux pressure.
2. Once a birth is selected, attachment is to a frontier/front-capacity parent.
3. For nine-port families, attachment fills the lowest-indexed eligible inactive
   port of that parent.
4. Telemetry records provenance so corrected front-capacity growth,
   pressure-boundary growth, and legacy broad growth can be distinguished.

### GRC9 And GRC9V3

Accepted parent eligibility modes:

- `grc9_front_capacity` for GRC9,
- `grcl9v3_front_capacity` in lowered GRCL-9V3 contexts,
- source records may use `front_capacity_source = pressure_boundary`.

`pressure_boundary` is a front-capacity provenance label. It is not a separate
free-growth rule. It means the eligible frontier was produced/declared as a
pressure boundary source and is then handled by the same front-capacity growth
surface.

Legacy mode:

- `legacy_any_inactive_port` is retained for historical replay and diagnostic
  comparison.
- It is over-aggressive relative to the corrected paper-facing semantics.
- Legacy broad-growth runs should not be used as accepted evidence.
- Catalog/replay tooling may require explicit `--force-legacy-growth` when
  rebuilding historical diagnostic catalogs.

### GRCV3

GRCV3 birth is opt-in:

- missing `frontier_birth_mode` means disabled,
- `frontier_birth_mode = disabled` means disabled,
- `frontier_birth_mode = active_frontier_pressure` enables the pressure-boundary
  frontier birth stage,
- `frontier_birth_strict = warn | error | allow` controls disabled-mode handling
  when frontier birth candidates are present.

Preferred new evidence uses explicit `frontier_birth_mode =
active_frontier_pressure` in the seed/runtime params. Old no-mode commands still
run for compatibility and preserve no-birth behavior.

## Coarse-Graining And Split

GRC9 and GRC9V3 support exact column coarse-graining and Split for supported
port fields.

Runtime methods:

```python
coarse_state = model.coarse_grain_columns("conductance")
print(coarse_state["mode"])  # exact_column_profile
fine_state = model.split_columns(coarse_state)
```

`coarse_grain_columns()` returns the `mode` and `field_name` keys required by
`split_columns()`. Passing a hand-written coarse-state mapping must preserve
those keys.

Accepted fields:

| Field | Coarse Mode | Notes |
|---|---|---|
| `conductance` | `exact_column_profile` | Nonnegative port conductance. |
| `geometric_length` | `exact_column_profile` | Nonnegative edge length label. |
| `temporal_delay` | `exact_column_profile` | Nonnegative edge delay label. |
| `flux_coupling` | `exact_column_profile` | Nonnegative coupling label. |
| `abs_flux` | `exact_column_profile` | Absolute oriented flux. |
| `signed_flux` | `signed_flux_split` | Signed oriented flux reconstructed through `J+` / `J-`. |

Supported modes:

| Mode | Meaning |
|---|---|
| `exact_column_profile` | Nonnegative port field pooled by column with intra-column row profiles. |
| `signed_flux_split` | Signed field split into nonnegative `J+` and `J-` components, each coarse-grained exactly, then reconstructed by subtraction. |

The `J+` / `J-` split matters for signed flux. A direct column sum can cancel
opposite-direction flows and lose reconstructability. Splitting positive and
negative support preserves the directional transport field exactly for supported
fine fields.

GRC9V3 stores operator-backed coarse states in `state.coarse_cache` and reports
operator-backed refresh metadata through coarse-cache telemetry when populated.

Script example:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/demo_grc9_coarse_graining.py
PYTHONPATH=src ./.venv/bin/python scripts/demo_grc9_coarse_graining.py --family grc9v3
```

## Maintenance And Analysis Methods

The step loop is the canonical runtime path. Some families also expose public
methods for ad hoc analysis, probes, and controlled repairs. These methods are
runtime operations, not observer claims; several mutate runtime state.

GRCV3:

- `rebuild_basin_attributes()`
- `rebuild_transport_state()`
- `rebuild_identity_state()`
- `rebuild_choice_state()`
- `detect_spark_candidates()`
- `apply_spark_candidates(candidates)`
- `rebuild_spark_state()`

GRC9V3:

- `rebuild_differential_state()`
- `rebuild_transport_state()`
- `rebuild_identity_state()`
- `detect_hybrid_spark_candidates()`
- `apply_hybrid_sparks()`
- `rebuild_choice_state()`
- `coarse_grain_columns(field_name)`
- `split_columns(coarse_state)`
- `apply_growth()`
- `apply_boundary_behavior()`
- `apply_continuity()`

Prefer `.step()` for evidence runs. Use these methods when constructing narrow
debug probes or checking a specific runtime surface.

## Telemetry Capture

For ad hoc scripts, call `.step()` and then pass the resulting `StepResult`
sequence to `capture_run_telemetry`.

```python
from pygrc.models import GRC9V3
from pygrc.telemetry.recorder import capture_run_telemetry

model = GRC9V3.from_config({"dt": 0.1})
initial_observables = model.compute_observables()
steps = model.run(3)
final_observables = model.compute_observables()
params = model.get_params()

pack = capture_run_telemetry(
    model_family=model.MODEL_FAMILY,
    params_identity=params.params_hash,
    seed_name="manual_grc9v3_smoke",
    seed_source_reference=None,
    seed_path=None,
    param_family=None,
    rng_seed=None,
    requested_steps=3,
    initial_observables=initial_observables,
    step_results=steps,
    final_observables=final_observables,
    resolved_params=dict(params.resolved_config),
    raw_params=dict(params.raw_config),
)

print(len(pack.step_rows), len(pack.event_rows), pack.run_summary.status)
```

Set `TelemetryCaptureConfig(write_artifacts=True, ...)` when you want files
written to disk. See `Telemetry-ReferenceGuide.md` for artifact layouts and
loading examples.

## Snapshots

Use snapshots for runtime state persistence:

```python
model.save("tmp/grc9v3-snapshot.json")
restored = GRC9V3.load("tmp/grc9v3-snapshot.json")
```

Snapshots include metadata, topology, dynamics, observables, events, and family
state groups. Graph checkpoints are telemetry artifacts, not runtime snapshots.

## Source And Landscape Helpers

For most authored examples, prefer the source/landscape workflows instead of
hand-assembling states:

- `build_grcv3_from_landscape_seed`
- `build_grc9_from_landscape_seed`
- `lower_grcl9_fixture_by_name`
- `lower_grcl9v3_fixture_by_name`
- `run_grcv3_landscape_seed`
- `run_grc9_landscape_seed`

These helpers are exported from `pygrc.models`.

See `LandscapeLanguage-ReferenceGuide.md` and
`LandscapeCompiler-ReferenceGuide.md`.

## Validation Commands

Smoke-test the defaulted runtime families:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.models import GRCV3, GRC9, GRC9V3

for family in (GRCV3, GRC9, GRC9V3):
    model = family.from_config({"dt": 0.1})
    result = model.step()
    print(family.__name__, result.step_index, len(result.events), sorted(result.observables)[:4])
PY
```

Smoke-test GRCV2 with explicit params:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.models import GRCV2

config = {
    "dt": 0.1,
    "evolution": {
        "alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0,
        "eta": 1.0, "kappa_c": 1.0, "lambda_c": 0.0,
        "xi_c": 0.0, "zeta_c": 0.0, "tau_split": 1.0,
        "lambda_birth": 0.0, "alpha_seed": 0.0, "eps_prune": 0.0,
        "eps_spark": 0.0, "site_potential_selection": "quadratic",
        "site_potential_params": {},
    },
    "constitutive_semantic_modes": {
        "curvature_backend": "none", "frame_mode": "combinatorial",
        "boundary_mode": "prune", "split_distribution_mode": "equal",
        "edge_label_selection": "all",
    },
}

model = GRCV2.from_config(config)
print(model.step().observables)
PY
```

Run coarse-graining examples:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/demo_grc9_coarse_graining.py
```

## Limitations And Boundaries

- GRCV2 is supported but older and requires explicit full params.
- GRCV3 pressure-boundary frontier birth is opt-in; missing mode means disabled.
- Legacy broad growth exists only for historical diagnostics and guarded replay.
- GRC9/GRC9V3 coarse-graining is exact for supported port fields, not an
  arbitrary graph quotient.
- Lorentzian/causal-layer and multiscale-sigma capabilities remain optional
  capability boundaries unless a family explicitly advertises and implements
  them.
- Runtime `.step()` emits behavior; inference and visualization are observers
  and must not feed claims back into runtime evidence.

## Related Guides

- `Telemetry-ReferenceGuide.md`
- `LandscapeLanguage-ReferenceGuide.md`
- `LandscapeCompiler-ReferenceGuide.md`
- `LandscapeInference-ReferenceGuide.md`
- `Motion-ReferenceGuide.md`
- `GraphVisualization-ReferenceGuide.md`
