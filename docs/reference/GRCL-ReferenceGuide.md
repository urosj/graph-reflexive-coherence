# GRCL Reference Guide

This guide describes the GRCL source-language layers that compile into runtime
GRC states and replayable telemetry evidence.

GRCL is a source/lowering layer. It declares intended structures, controls, and
non-claims. It does not itself prove that a runtime event happened. Runtime
evidence must come from replay telemetry, graph checkpoints, selector
validation, reviewed catalogs, or motion/landscape inference.

## Scope

This guide covers:

- GRCL-9 source documents and fixtures,
- GRCL-9V3 source documents and fixtures,
- lowering manifests and controls,
- landscape example and seed-backed compilation modes,
- replay commands,
- selector validation,
- corrected front-capacity and pressure-boundary growth semantics,
- legacy growth quarantine.

For neutral landscape seed syntax, see `LandscapeLanguage-ReferenceGuide.md`.
For source-to-runtime lowering internals, see
`LandscapeCompiler-ReferenceGuide.md`.

## Prerequisites

Run examples from the repository root with the project virtual environment:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --help
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --help
```

The examples use explicit session ids such as `S9001`. Session ids are
`S` followed by digits. Use a fresh id for new local runs to avoid overwriting
an existing session directory.

## Quick Start

This minimal run lowers one GRCL-9V3 fixture, replays it for five steps, then
validates selectors over the produced telemetry:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S9001 \
  --source-mode fixtures \
  --fixture hybrid_spark_gate_positive_control \
  --steps 5

PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation \
  --session-id S9010 \
  --source-session-ids S9001
```

Expected outputs include:

- `outputs/grcl9v3/lowering/sessions/S9001/session_manifest.json`
- `outputs/grcl9v3/lowering/sessions/S9001/run_report.json`
- `outputs/grcl9v3/lowering/sessions/S9010/reports/selector_validation_summary.md`

The replay step creates runtime evidence. The selector step decides which
source-facing expectations were observed, failed, or missing from telemetry.

## Canonical Modules

| Layer | GRCL-9 | GRCL-9V3 |
|---|---|---|
| Source schema | `src/pygrc/landscapes/extensions/grcl9/schema.py` | `src/pygrc/landscapes/extensions/grcl9v3/schema.py` |
| Lowering manifest | `src/pygrc/landscapes/extensions/grcl9/manifest.py` | `src/pygrc/landscapes/extensions/grcl9v3/manifest.py` |
| Built-in fixtures | `src/pygrc/landscapes/extensions/grcl9/fixtures.py` | `src/pygrc/landscapes/extensions/grcl9v3/fixtures.py` |
| Landscape examples | `src/pygrc/landscapes/extensions/grcl9/examples.py` | `src/pygrc/landscapes/extensions/grcl9v3/examples.py` |
| Runtime lowerer | `src/pygrc/models/grc_9_grcl9_lowering.py` | `src/pygrc/models/grc_9_v3_grcl9v3_lowering.py` |
| Provenance helpers | `src/pygrc/models/grc_9_grcl9_provenance.py` | `src/pygrc/models/grc_9_v3_grcl9v3_provenance.py` |
| Replay runner | `src/pygrc/telemetry/grcl9_replay.py` | `src/pygrc/telemetry/grcl9v3_replay.py` |
| Selector validation | `src/pygrc/telemetry/grcl9_selector_validation.py` | `src/pygrc/telemetry/grcl9v3_selector_validation.py` |
| Reviewed catalog builder | `src/pygrc/telemetry/grcl9_lowered_motif_catalog.py` | `src/pygrc/telemetry/grcl9v3_lowered_motif_catalog.py` |

Engineering records:

- `implementation/GRCL-9-ImplementationPlan.md`
- `implementation/GRCL-9-ImplementationChecklist.md`
- `implementation/GRCL-9V3-ImplementationPlan.md`
- `implementation/GRCL-9V3-ImplementationChecklist.md`
- `implementation/GRC9-GRCL9-GrowthCorrection-Plan.md`
- `implementation/GRC9-GRCL9-GrowthCorrection-Checklist.md`
- `implementation/PressureBoundary-ImplementationPlan.md`
- `implementation/PressureBoundary-ImplementationChecklist.md`

## Authority Model

GRCL documents can claim:

- a source construct exists,
- the construct is intended to lower into a runtime state,
- the construct has expected selector ids,
- the construct has non-claims,
- lowering controls should create runtime preconditions.

GRCL documents must not claim:

- a spark happened,
- growth happened,
- a daughter sink stabilized,
- a choice/collapse event occurred,
- a runtime selector passed,
- an observed motif was accepted.

The schemas reject many runtime-smuggling keys such as `spark_happened`,
`growth_count`, `runtime_events`, `solved_flux`, and `event_counts_by_kind`.

## Source Document Shape

Both families use the same broad document shape:

```yaml
source_schema_version: grcl9.source.v1
fixture_name: spark_to_expansion_d_eff_high
manifest_entry_id: grcl9_lowering_expansion_refinement_v1
motif_id: optional-human-or-reviewed-id
constructs:
  - construct_kind: spark_candidate_region
    construct_id: spark_region
    motif_id: expansion_refinement
    executable: true
    candidate_id: candidate
    coherence_allocation:
      candidate: 1.0
      neighbors: 0.5
    neighbor_coherence_profile:
      port_occupancy: all_nine_ports
    spark_gate_intent: saturation_column_proxy
expected_selector_ids:
  - expansion_module_size
non_claims:
  - no_runtime_event_injection
  - no_solved_flux
notes: {}
```

The exact dataclasses are:

- `GRCL9SourceDocument`
- `GRCL9V3SourceDocument`

## GRCL-9 Constructs

GRCL-9 targets the GRC9 mechanical runtime.

Construct dataclasses:

| Construct | Purpose |
|---|---|
| `GRCL9SparkCandidateRegion` | Source preconditions for a GRC9 spark candidate. |
| `GRCL9ColumnProxyProfile` | Column diagnostic/proxy source profile. |
| `GRCL9InstabilityProfile` | Mechanical instability profile for spark triggering. |
| `GRCL9ExpansionRefinementRegion` | Mechanical expansion/refinement source region. |
| `GRCL9GrowthLocus` | Growth source locus; paper-facing evidence must use front-capacity semantics. |
| `GRCL9PostExpansionFissionGeometry` | Post-expansion two-sink/fission geometry preconditions. |

Built-in fixture names:

```text
spark_column_proxy_eps_pass
spark_column_proxy_eps_fail
spark_instability_tau_pass
spark_instability_tau_fail
spark_to_expansion_d_eff_low
spark_to_expansion_d_eff_high
growth_pressure_lambda_high
growth_pressure_lambda_low
post_expansion_fission_min_mass_pass
post_expansion_fission_min_mass_fail
```

## GRCL-9V3 Constructs

GRCL-9V3 targets the hybrid GRC9V3 runtime.

Construct dataclasses:

| Construct | Purpose |
|---|---|
| `GRCL9V3HybridSparkRegion` | Hybrid spark preconditions. |
| `GRCL9V3RowBasisHessianProfile` | Row-basis or weighted least-squares Hessian profile. |
| `GRCL9V3HybridTensorProfile` | Tensor evidence profile. |
| `GRCL9V3ColumnProxyFallbackProfile` | GRC9 column proxy fallback profile. |
| `GRCL9V3ExpansionRefinementRegion` | Mechanical expansion region. |
| `GRCL9V3ChoiceCollapseRegion` | Choice/collapse source preconditions. |
| `GRCL9V3GrowthLocus` | Hybrid growth source locus; paper-facing evidence must use front-capacity semantics. |
| `GRCL9V3TransportReroutingRegion` | Transport rerouting source region. |
| `GRCL9V3AppendixEDivisionRegion` | Appendix E cell-division fixture region. |
| `GRCL9V3QuiescentHybridRegion` | No-event/quiescent hybrid control. |

Built-in fixture names:

```text
hybrid_spark_gate_positive_control
hybrid_spark_gate_negative_control
spark_to_expansion_positive_control
spark_to_expansion_negative_control
appendix_e_cell_division_positive_control
appendix_e_cell_division_negative_control
choice_collapse_positive_control
choice_collapse_negative_control
growth_pressure_positive_control
growth_pressure_negative_control
transport_basin_rerouting_positive_control
quiescent_hybrid_control_no_event_control
```

## Lowering Manifests

Lowering manifests map source constructs to runtime preconditions and expected
telemetry surfaces.

Main APIs:

```python
from pygrc.landscapes.extensions.grcl9 import default_grcl9_lowering_manifest
from pygrc.landscapes.extensions.grcl9v3 import default_grcl9v3_lowering_manifest

grcl9_manifest = default_grcl9_lowering_manifest()
grcl9v3_manifest = default_grcl9v3_lowering_manifest()

print(len(grcl9_manifest.entries))
print(len(grcl9v3_manifest.entries))
```

Manifest entries include:

- schema version,
- entry id,
- seed family,
- lowered runtime family,
- constructs,
- controls,
- telemetry expectations,
- non-claims.

`GRCL9V3LoweringControl` also carries ownership tags aligned to GRC9
mechanical, GRCV3 semantic, or hybrid surfaces.

## Compilation Modes

GRCL sources can be obtained from:

- built-in mechanical fixtures,
- compiled landscape examples,
- compiled landscape seed examples,
- legacy growth seed examples for quarantined diagnostics.

GRCL-9V3 also exposes diagnostic probe modes for targeted investigation:

| GRCL-9V3 Source Mode | Meaning |
|---|---|
| `fixtures` | Built-in source fixtures. |
| `landscape_examples` | Authored landscape examples compiled to source documents. |
| `landscape_seed_examples` | `LandscapeSeed` examples compiled to source documents. |
| `legacy_growth_landscape_seed_examples` | Quarantined legacy growth seed examples. |
| `hessian_backend_probe` | Row-basis vs weighted least-squares Hessian diagnostic probes. |
| `collapse_learning_probe` | Long-window collapse/learning diagnostic probes. |
| `growth_collapse_relay_probe` | Growth/collapse relay diagnostic probes. |
| `relay_port_probe` | Relay-port growth/front-capacity probes. |
| `pressure_boundary_probe` | Pressure-boundary front-capacity probes. |

## Lowering To Runtime State

Use the lowerer APIs when you need a state object without running a replay
session.

```python
from pygrc.models import lower_grcl9_fixture_by_name, lower_grcl9v3_fixture_by_name

grcl9_lowered = lower_grcl9_fixture_by_name("spark_to_expansion_d_eff_high")
grcl9v3_lowered = lower_grcl9v3_fixture_by_name("hybrid_spark_gate_positive_control")

print(grcl9_lowered.state.step_index)
print(grcl9_lowered.node_id_by_role)
print(grcl9v3_lowered.state.cached_quantities.keys())
```

Lowering results contain:

- `source`: the source document,
- `state`: the lowered `GRC9State` or `GRC9V3State`,
- `node_id_by_role`: source/provenance role to runtime node id,
- `edge_id_by_role`: source/provenance role to runtime edge id.

Source provenance is also mirrored into cached quantities and checkpoint
payloads where available.

GRCL-9V3 source constructs and manifest controls carry ownership tags such as
`grc9_mechanical`, `grcv3_semantic`, `grc9v3_hybrid`, and `shared_runtime`.
Plain GRCL-9 does not use the same hybrid ownership-tag contract.

## Growth Semantics

GRCL growth has two schema modes:

- `front_capacity`
- `legacy_growth_locus`

Paper-facing growth evidence must use `front_capacity`.

Allowed front-capacity sources:

- `spark_expansion_front`
- `refinement_boundary_capacity`
- `preexisting_front`
- `pressure_boundary`

`legacy_source_growth_locus` is valid only with `legacy_growth_locus`.

Validation helpers:

```python
from pygrc.landscapes.extensions.grcl9 import (
    grcl9_source_fixture_by_name,
    validate_grcl9_paper_facing_growth_semantics,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    grcl9v3_source_fixture_by_name,
    validate_grcl9v3_paper_facing_growth_semantics,
)

doc = grcl9_source_fixture_by_name()["growth_pressure_lambda_high"]
print(validate_grcl9_paper_facing_growth_semantics(doc))

v3_doc = grcl9v3_source_fixture_by_name()["growth_pressure_positive_control"]
print(validate_grcl9v3_paper_facing_growth_semantics(v3_doc))
```

If a document contains executable `legacy_growth_locus`, these helpers raise.

## Legacy Growth Quarantine

Legacy broad growth treated any inactive port too broadly and is no longer
accepted as paper-facing evidence. It remains available only for historical
diagnostic replay.

Rules:

- Active evidence should use `front_capacity`.
- `legacy_growth_landscape_seed_examples` is quarantined.
- GRCL-9 replay and selector validation require `--force-legacy-growth` for
  legacy mode.
- Forced legacy outputs remain diagnostic non-evidence.
- Reviewed catalogs refuse legacy broad-growth source sessions unless forced for
  historical rebuilds.

## Replay Commands

Replay sessions write source fixtures, lowered states, telemetry rows, graph
checkpoints, selector reports, manifests, and summaries under:

- `outputs/grcl9/lowering/sessions/<session_id>/`
- `outputs/grcl9v3/lowering/sessions/<session_id>/`

### GRCL-9 Replay

Run all built-in fixtures:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay \
  --session-id S9001 \
  --source-mode fixtures \
  --requested-steps 5
```

Run one fixture:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay \
  --session-id S9002 \
  --source-mode fixtures \
  --fixture spark_to_expansion_d_eff_high \
  --requested-steps 5
```

Run corrected seed-backed examples:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay \
  --session-id S9003 \
  --source-mode landscape_seed_examples \
  --requested-steps 8
```

Run quarantined legacy examples only when intentionally reviewing history:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay \
  --session-id S9004 \
  --source-mode legacy_growth_landscape_seed_examples \
  --requested-steps 8 \
  --force-legacy-growth
```

GRCL-9 uses `--requested-steps`.

### GRCL-9V3 Replay

Run all built-in fixtures:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S9001 \
  --source-mode fixtures \
  --steps 5
```

Run one fixture:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S9002 \
  --source-mode fixtures \
  --fixture hybrid_spark_gate_positive_control \
  --steps 5
```

Run seed-backed examples:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S9003 \
  --source-mode landscape_seed_examples \
  --steps 8
```

Run a diagnostic pressure-boundary probe:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay \
  --session-id S9004 \
  --source-mode pressure_boundary_probe \
  --steps 8
```

GRCL-9V3 uses `--steps`.

Both replay CLIs accept `--fixture` to run a subset rather than every fixture
in a source mode.

## Selector Validation

Selector validation converts replay telemetry into field-backed pass/fail or
missing-surface records.

### GRCL-9

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation \
  --session-id S9010 \
  --source-session-id S9001
```

Multiple source sessions:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation \
  --session-id S9011 \
  --source-session-id S9001 \
  --source-session-id S9003
```

Legacy source sessions require:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation \
  --session-id S9012 \
  --source-session-id S9004 \
  --force-legacy-growth
```

### GRCL-9V3

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation \
  --session-id S9010 \
  --source-session-ids S9001
```

Multiple source sessions are comma-separated:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation \
  --session-id S9011 \
  --source-session-ids S9001,S9003
```

GRCL-9V3 source selector ids remain vocabulary-facing. The validation layer
expands them into concrete GRC9V3 telemetry selectors via
`selector_expansions.py`.

## Output Artifacts

A replay session typically contains:

- `session_manifest.json`
- `run_report.json`
- `README.md`
- `ExperimentalLog.md` at the lowering root
- `source_fixtures/<fixture>.json`
- `lowered_states/<fixture>.json`
- runtime telemetry under lane artifact roots
- graph checkpoints
- per-lane selector reports

A selector validation session contains:

- `selector_manifest.json`
- `reports/selector_validation_report.json`
- `reports/selector_validation_summary.md`
- `README.md`

See `Telemetry-ReferenceGuide.md` for row and checkpoint layouts.

Reviewed catalog sessions add:

- `reviewed_grcl9_lowered_motif_catalog.json` or
  `reviewed_grcl9v3_lowered_motif_catalog.json`
- `reports/reviewed_*_lowered_motif_catalog_report.json`
- `reports/reviewed_*_lowered_motif_catalog_summary.md`

## API Examples

List fixture names:

```python
from pygrc.landscapes.extensions.grcl9 import GRCL9_SOURCE_FIXTURE_NAMES
from pygrc.landscapes.extensions.grcl9v3 import GRCL9V3_SOURCE_FIXTURE_NAMES

print(GRCL9_SOURCE_FIXTURE_NAMES)
print(GRCL9V3_SOURCE_FIXTURE_NAMES)
```

Compile landscape examples to GRCL source:

```python
from pygrc.landscapes.extensions.grcl9 import (
    compile_default_grcl9_landscape_examples_to_sources,
)
from pygrc.landscapes.extensions.grcl9v3 import (
    compile_default_grcl9v3_landscape_examples_to_sources,
)

grcl9_sources = compile_default_grcl9_landscape_examples_to_sources()
grcl9v3_sources = compile_default_grcl9v3_landscape_examples_to_sources()

print([source.fixture_name for source in grcl9_sources])
print([source.fixture_name for source in grcl9v3_sources])
```

Run replay from Python:

```python
from pygrc.telemetry.grcl9_replay import run_grcl9_lowering_replay_session
from pygrc.telemetry.grcl9v3_replay import run_grcl9v3_lowering_replay_session

grcl9_session = run_grcl9_lowering_replay_session(
    session_id="S9001",
    fixture_names=("spark_to_expansion_d_eff_high",),
    requested_steps=5,
    source_mode="fixtures",
)

grcl9v3_session = run_grcl9v3_lowering_replay_session(
    session_id="S9002",
    fixture_names=("hybrid_spark_gate_positive_control",),
    requested_steps=5,
    source_mode="fixtures",
)

print(grcl9_session.session_root)
print(grcl9v3_session.session_root)
```

## Validation Commands

Import fixture and manifest surfaces:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes.extensions.grcl9 import GRCL9_SOURCE_FIXTURE_NAMES, default_grcl9_lowering_manifest
from pygrc.landscapes.extensions.grcl9v3 import GRCL9V3_SOURCE_FIXTURE_NAMES, default_grcl9v3_lowering_manifest

print(len(GRCL9_SOURCE_FIXTURE_NAMES), len(default_grcl9_lowering_manifest().entries))
print(len(GRCL9V3_SOURCE_FIXTURE_NAMES), len(default_grcl9v3_lowering_manifest().entries))
PY
```

## Troubleshooting

Common issues:

- `invalid session id`: use `S` followed by digits, for example `S9020`.
- `session already exists` or confusing stale outputs: choose a fresh session id
  or move the old local session aside.
- `legacy growth requires --force-legacy-growth`: the selected source mode is
  quarantined diagnostic history. Add `--force-legacy-growth` only when
  intentionally rebuilding legacy evidence.
- Selector records with `failure_kind = missing_surface`: the replay telemetry
  did not expose the field required by that selector. Inspect the replay
  `run_report.json`, graph checkpoint index, and selector summary before
  treating it as a mechanism failure.
- Selector records with `failure_kind = predicate_failed`: the required field
  was present, but the observed value did not satisfy the selector.
- Lowering errors about disconnected graphs or invalid ports usually mean the
  source construct lowered into an invalid runtime precondition. Inspect
  `lowered_states/<fixture>.json` and the source fixture copy in the session.
- GRCL-9 and GRCL-9V3 use different step flags. Use `--requested-steps` for
  GRCL-9 and `--steps` for GRCL-9V3.

Smoke-test one lowering path per family:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.models import lower_grcl9_fixture_by_name, lower_grcl9v3_fixture_by_name

g9 = lower_grcl9_fixture_by_name("spark_to_expansion_d_eff_high")
g9v3 = lower_grcl9v3_fixture_by_name("hybrid_spark_gate_positive_control")

print(g9.source.fixture_name, len(g9.node_id_by_role))
print(g9v3.source.fixture_name, len(g9v3.node_id_by_role))
PY
```

## Limitations

- GRCL sources are not runtime proof.
- Selectors can fail because a predicate failed or because a telemetry surface
  is missing; inspect `failure_kind`.
- Legacy broad-growth source modes are diagnostic only.
- GRCL-9 and GRCL-9V3 replay CLIs differ: GRCL-9 uses `--requested-steps`,
  GRCL-9V3 uses `--steps`.
- Probe modes can be useful for investigation but should not be promoted to
  accepted catalog evidence without selector-backed review.

## Related Guides

- `LandscapeLanguage-ReferenceGuide.md`
- `LandscapeCompiler-ReferenceGuide.md`
- `GRC-Runtime-ReferenceGuide.md`
- `Telemetry-ReferenceGuide.md`
- `GraphVisualization-ReferenceGuide.md`
- `Catalogs-And-Evidence-ReferenceGuide.md`
