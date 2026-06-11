# Landscape Compiler And Lowering Reference Guide

This guide describes how authored landscape examples and normalized
`LandscapeSeed` files are compiled into family-specific GRCL source documents,
lowered into native runtime states, and replayed into telemetry artifacts.

The compiler/lowering layer is a source-to-runtime initialization bridge. It
does not create runtime evidence by itself. Evidence still comes from replayed
runtime telemetry, graph checkpoints, selector validation, visualization, and
reviewed catalogs.

## Scope

Use this guide when you want to:

- compile GRCL landscape examples into source documents,
- extract GRCL source documents from seed-backed examples,
- lower GRCL-9 documents into `GRC9State`,
- lower GRCL-9V3 documents into `GRC9V3State`,
- run replayable lowered-source sessions,
- inspect provenance and expected-region caches,
- understand legacy growth quarantine and corrected front-growth semantics.

This guide focuses on GRCL-9 and GRCL-9V3 because those are the current
source/lowering stacks in the repository.

## Pipeline

The full path is:

```text
LandscapeSeed or landscape example
-> GRCL source document
-> family-native lowered state
-> runtime replay
-> telemetry/checkpoints
-> selector validation
-> visual review
-> reviewed catalog
```

The important boundary is:

```text
source declaration != runtime evidence
```

A source fixture may declare a growth locus, spark candidate, choice region, or
Appendix E cell-division precondition. Only replay telemetry can show whether
growth, spark, choice, collapse, expansion, or division actually happened.

## Main Modules

| Layer | GRCL-9 | GRCL-9V3 |
|---|---|---|
| Landscape extension package | `pygrc.landscapes.extensions.grcl9` | `pygrc.landscapes.extensions.grcl9v3` |
| Source schema | `src/pygrc/landscapes/extensions/grcl9/schema.py` | `src/pygrc/landscapes/extensions/grcl9v3/schema.py` |
| Manifest | `src/pygrc/landscapes/extensions/grcl9/manifest.py` | `src/pygrc/landscapes/extensions/grcl9v3/manifest.py` |
| Built-in source fixtures | `src/pygrc/landscapes/extensions/grcl9/fixtures.py` | `src/pygrc/landscapes/extensions/grcl9v3/fixtures.py` |
| Landscape example compiler | `src/pygrc/landscapes/extensions/grcl9/examples.py` | `src/pygrc/landscapes/extensions/grcl9v3/examples.py` |
| Native lowerer | `src/pygrc/models/grc_9_grcl9_lowering.py` | `src/pygrc/models/grc_9_v3_grcl9v3_lowering.py` |
| Provenance helpers | `src/pygrc/models/grc_9_grcl9_provenance.py` | `src/pygrc/models/grc_9_v3_grcl9v3_provenance.py` |
| Replay runner | `src/pygrc/telemetry/grcl9_replay.py` | `src/pygrc/telemetry/grcl9v3_replay.py` |
| Selector validation | `src/pygrc/telemetry/grcl9_selector_validation.py` | `src/pygrc/telemetry/grcl9v3_selector_validation.py` |
| Visual review | `src/pygrc/visualization/grcl9_lowering.py` | `src/pygrc/visualization/grcl9v3_lowering.py` |

## Source Documents

GRCL source documents are typed, family-specific source documents. They are
more mechanical than neutral `LandscapeSeed` files, but still source-side.

GRCL-9 source constructs include:

- `GRCL9SparkCandidateRegion`
- `GRCL9ColumnProxyProfile`
- `GRCL9InstabilityProfile`
- `GRCL9ExpansionRefinementRegion`
- `GRCL9GrowthLocus`
- `GRCL9PostExpansionFissionGeometry`

GRCL-9V3 source constructs include:

- `GRCL9V3HybridSparkRegion`
- `GRCL9V3RowBasisHessianProfile`
- `GRCL9V3HybridTensorProfile`
- `GRCL9V3ColumnProxyFallbackProfile`
- `GRCL9V3ExpansionRefinementRegion`
- `GRCL9V3ChoiceCollapseRegion`
- `GRCL9V3GrowthLocus`
- `GRCL9V3TransportReroutingRegion`
- `GRCL9V3AppendixEDivisionRegion`
- `GRCL9V3QuiescentHybridRegion`

The source schemas also carry:

- bridge policy,
- budget policy,
- provenance policy,
- manifest linkage,
- non-claims,
- source construct IDs.

## Manifests

Lowering manifests define what source constructs mean to the lowering layer.
They are not replay artifacts and are not runtime telemetry.

Useful APIs:

```python
from pygrc.landscapes.extensions.grcl9 import default_grcl9_lowering_manifest
from pygrc.landscapes.extensions.grcl9v3 import default_grcl9v3_lowering_manifest

grcl9_manifest = default_grcl9_lowering_manifest()
grcl9v3_manifest = default_grcl9v3_lowering_manifest()

print(grcl9_manifest.manifest_version)
print(grcl9v3_manifest.manifest_version)
```

GRCL-9V3 also exposes:

```python
from pygrc.landscapes.extensions.grcl9v3 import validate_grcl9v3_manifest_against_handoff

validate_grcl9v3_manifest_against_handoff()
```

That validation guards against drift from the GRC9V3 discovery handoff used to
anchor the first source-language manifest.

## Compiling Landscape Examples

Landscape examples are higher-level, Morse/landscape-facing source documents.
They compile into GRCL source documents.

GRCL-9:

```python
from pygrc.landscapes.extensions.grcl9 import (
    compile_default_grcl9_landscape_examples_to_sources,
    compile_default_grcl9_landscape_seed_examples_to_sources,
)

mechanical_sources = compile_default_grcl9_landscape_examples_to_sources()
seed_backed_sources = compile_default_grcl9_landscape_seed_examples_to_sources()

print(len(mechanical_sources), len(seed_backed_sources))
```

GRCL-9V3:

```python
from pygrc.landscapes.extensions.grcl9v3 import (
    compile_default_grcl9v3_landscape_examples_to_sources,
    compile_default_grcl9v3_landscape_seed_examples_to_sources,
)

mechanical_sources = compile_default_grcl9v3_landscape_examples_to_sources()
seed_backed_sources = compile_default_grcl9v3_landscape_seed_examples_to_sources()

print(len(mechanical_sources), len(seed_backed_sources))
```

Seed-backed examples are extracted from files in `configs/landscapes/seed/`.
They preserve `LandscapeSeed` authorship while producing family-native source
constructs for lowering.

## Lowering To Native Runtime State

Lowering returns a result object with:

- `source`
- `state`
- `node_id_by_role`
- `edge_id_by_role`

`source` is the validated GRCL source document that was lowered. `state` is
the family-native runtime state (`GRC9State` or `GRC9V3State`). The role maps
connect source/lowering roles such as `candidate`, `neighbor_port_1`, or
`front_parent` to concrete runtime node and edge IDs. Runtime source
provenance, expected regions, and growth/front-capacity metadata are also
mirrored into `state.cached_quantities` and node/edge payloads.

GRCL-9 example:

```python
from pygrc.models.grc_9_grcl9_lowering import lower_grcl9_fixture_by_name

result = lower_grcl9_fixture_by_name("spark_to_expansion_d_eff_high")

print(type(result.state).__name__)
print(result.node_id_by_role)
print(result.edge_id_by_role)
```

GRCL-9V3 example:

```python
from pygrc.models.grc_9_v3_grcl9v3_lowering import lower_grcl9v3_fixture_by_name

result = lower_grcl9v3_fixture_by_name("hybrid_spark_gate_positive_control")

print(type(result.state).__name__)
print(result.node_id_by_role)
print(result.edge_id_by_role)
```

Lowering performs deterministic graph assembly and validates that the resulting
state is accepted by the target runtime model.

## Provenance And Expected Caches

Lowered states carry source/runtime links in cached quantities and payloads.
Typical records include:

- `grcl9_provenance` or `grcl9v3_provenance`,
- source construct IDs,
- lowered node and edge roles,
- motif registry records,
- expected-region caches,
- growth/front-capacity provenance,
- RNG seed provenance where deterministic replay needs it.

Expected-region caches are not observed evidence. They are source/lowering
expectations used later to compare source intent with runtime observations.

## Replay Sessions

Replay sessions run lowered source documents through the runtime and write
artifacts under:

- `outputs/grcl9/lowering/sessions/<session_id>/`
- `outputs/grcl9v3/lowering/sessions/<session_id>/`

Typical contents:

- `session_manifest.json`
- `README.md`
- source fixture copies,
- lowered state payloads,
- lane reports,
- `steps.jsonl`
- `events.jsonl`
- `run_summary.json`
- graph checkpoints,
- replay commands.

### GRCL-9 Replay Command

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay \
  --session-id S_DOC_GRCL9 \
  --requested-steps 3 \
  --source-mode landscape_seed_examples \
  --fixture corrected_front_growth_positive_high
```

GRCL-9 uses `--requested-steps`.

GRCL-9 source modes:

- `fixtures`
- `landscape_examples`
- `landscape_seed_examples`
- `legacy_growth_landscape_seed_examples`

Pass `--fixture <name>` once or multiple times to replay only selected
fixtures within the chosen source mode. Omit `--fixture` to replay the full
mode.

Legacy growth replay requires:

```bash
--force-legacy-growth
```

Legacy broad-growth outputs remain diagnostic non-evidence.

### GRCL-9V3 Replay Command

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S_DOC_GRCL9V3 \
  --steps 3 \
  --source-mode landscape_seed_examples \
  --fixture corrected_hybrid_full_composition
```

GRCL-9V3 uses `--steps`, not `--requested-steps`.

Pass `--fixture <name>` once or multiple times to replay only selected
fixtures within the chosen source mode. Omit `--fixture` to replay the full
mode.

GRCL-9V3 source modes:

| Mode | Use |
|---|---|
| `fixtures` | Built-in typed source fixtures. |
| `landscape_examples` | Authored landscape/Morse examples compiled to source documents. |
| `landscape_seed_examples` | Seed-backed landscape examples compiled to source documents. |
| `legacy_growth_landscape_seed_examples` | Quarantined historical standalone-growth diagnostics. |
| `hessian_backend_probe` | Paired row-basis vs. weighted least-squares Hessian backend diagnostics. |
| `collapse_learning_probe` | Collapse/learning source probes. |
| `growth_collapse_relay_probe` | Growth/collapse relay source probes. |
| `relay_port_probe` | Relay-port geometry and front propagation probes. |
| `pressure_boundary_probe` | Pressure-boundary/front-capacity source probes. |

Current paper-facing growth evidence should use corrected front-capacity or
pressure-boundary semantics, not legacy standalone broad growth.

## Selector Validation And Visual Review

After replay, selector validation checks field-backed evidence surfaces.

GRCL-9V3 selector example:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation \
  --session-id S_DOC_GRCL9V3_SELECTORS \
  --source-session-ids S_DOC_GRCL9V3 \
  --output-root outputs/grcl9v3/lowering
```

GRCL-9V3 visual review example:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering \
  --session-id S_DOC_GRCL9V3_VISUALS \
  --selector-session-id S_DOC_GRCL9V3_SELECTORS \
  --output-root outputs/grcl9v3/lowering
```

Visuals are supporting evidence only. They do not promote source claims into
accepted runtime claims.

## Practical API Examples

### List Built-In Source Fixture Names

```python
from pygrc.landscapes.extensions.grcl9 import GRCL9_SOURCE_FIXTURE_NAMES
from pygrc.landscapes.extensions.grcl9v3 import GRCL9V3_SOURCE_FIXTURE_NAMES

print(GRCL9_SOURCE_FIXTURE_NAMES)
print(GRCL9V3_SOURCE_FIXTURE_NAMES)
```

Current built-in GRCL-9 source fixtures:

- `spark_column_proxy_eps_pass`
- `spark_column_proxy_eps_fail`
- `spark_instability_tau_pass`
- `spark_instability_tau_fail`
- `spark_to_expansion_d_eff_low`
- `spark_to_expansion_d_eff_high`
- `growth_pressure_lambda_high`
- `growth_pressure_lambda_low`
- `post_expansion_fission_min_mass_pass`
- `post_expansion_fission_min_mass_fail`

Current built-in GRCL-9V3 source fixtures:

- `hybrid_spark_gate_positive_control`
- `hybrid_spark_gate_negative_control`
- `spark_to_expansion_positive_control`
- `spark_to_expansion_negative_control`
- `appendix_e_cell_division_positive_control`
- `appendix_e_cell_division_negative_control`
- `choice_collapse_positive_control`
- `choice_collapse_negative_control`
- `growth_pressure_positive_control`
- `growth_pressure_negative_control`
- `transport_basin_rerouting_positive_control`
- `quiescent_hybrid_control_no_event_control`

### Compile Seed-Backed Examples And Lower One

```python
from pygrc.landscapes.extensions.grcl9v3 import (
    compile_default_grcl9v3_landscape_seed_examples_to_sources,
)
from pygrc.models.grc_9_v3_grcl9v3_lowering import (
    lower_grcl9v3_source_to_grc9v3_state,
)

sources = compile_default_grcl9v3_landscape_seed_examples_to_sources()
source = next(item for item in sources if item.fixture_name == "corrected_hybrid_full_composition")
lowered = lower_grcl9v3_source_to_grc9v3_state(source)

print(lowered.source.fixture_name)
print(len(tuple(lowered.state.topology.iter_live_node_ids())))
```

### Inspect Expected Region Caches

```python
from pygrc.models.grc_9_v3_grcl9v3_lowering import lower_grcl9v3_fixture_by_name

lowered = lower_grcl9v3_fixture_by_name("hybrid_spark_gate_positive_control")
caches = {
    key: value
    for key, value in lowered.state.cached_quantities.items()
    if key.startswith("grcl9v3_expected_")
}

print(sorted(caches))
```

## Script Examples

### Smoke-Test GRCL-9 Lowering

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.models.grc_9_grcl9_lowering import lower_grcl9_fixture_by_name

result = lower_grcl9_fixture_by_name("spark_to_expansion_d_eff_high")
print("nodes", len(tuple(result.state.topology.iter_live_node_ids())))
print("roles", sorted(result.node_id_by_role))
PY
```

### Smoke-Test GRCL-9V3 Lowering

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.models.grc_9_v3_grcl9v3_lowering import lower_grcl9v3_fixture_by_name

result = lower_grcl9v3_fixture_by_name("hybrid_spark_gate_positive_control")
print("nodes", len(tuple(result.state.topology.iter_live_node_ids())))
print("roles", sorted(result.node_id_by_role))
PY
```

### Run One GRCL-9V3 Seed-Backed Replay

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S_DOC_GRCL9V3 \
  --steps 3 \
  --source-mode landscape_seed_examples \
  --fixture corrected_hybrid_full_composition
```

## Current Evidence Anchors

Representative session roots:

- `outputs/grcl9/lowering/sessions/`
- `outputs/grcl9v3/lowering/sessions/`

Session folders are generated artifacts. Use the `session_manifest.json` inside
each session as the durable description of source mode, replay command, input
fixtures, and output paths.

Recent GRCL-9V3 pressure-boundary/lowering evidence in this workspace includes:

- `outputs/grcl9v3/lowering/sessions/S0075`
- `outputs/grcl9v3/lowering/sessions/S0076`

The exact meaning of each session is recorded in its `session_manifest.json`.

## Corrected Growth And Legacy Quarantine

Earlier GRCL-9 and GRCL-9V3 exploratory runs used an over-aggressive
standalone growth-locus interpretation. Those seeds are quarantined under:

- `configs/landscapes/seed/legacy/grcl9-overaggressive-growth/`
- `configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/`

Current paper-facing growth evidence should use:

- spark/refinement-created front capacity,
- closed front-capacity controls,
- pressure-boundary front-capacity provenance where explicitly authored,
- lowest-port attachment rules in the runtime.

Legacy replay remains useful for history and comparison, but it is not accepted
front-growth evidence.

## Related Guides

- [Landscape Language Reference Guide](LandscapeLanguage-ReferenceGuide.md)
- [Landscape Inference Reference Guide](LandscapeInference-ReferenceGuide.md)
- [Motion Reference Guide](Motion-ReferenceGuide.md)
- [GRCL Reference Guide](GRCL-ReferenceGuide.md) covers the source-language
  vocabulary in more detail.
- [Telemetry Reference Guide](Telemetry-ReferenceGuide.md) covers step rows,
  event rows, summaries, and checkpoints in more detail.

## Limitations

- Lowering is deterministic initialization, not a runtime proof.
- Source documents may carry expected regions; selectors decide whether
  observed telemetry supports them.
- GRCL-9 and GRCL-9V3 source constructs are related but not interchangeable.
- Visual review is diagnostic/supporting evidence only.
- Legacy growth requires explicit opt-in and remains diagnostic-only.
- Unknown fixture names raise `ValueError` at lowering/replay boundaries.
- Replay runners reject invalid source modes and non-positive step counts.
