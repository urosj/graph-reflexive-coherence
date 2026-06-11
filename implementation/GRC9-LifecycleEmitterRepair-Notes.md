# GRC9 Lifecycle Emitter Repair Notes

## Purpose

S0004 established that the first generated discovery structures were valid
GRC9 port graphs, but were too generic to reliably emit the lifecycle events
we want to study. This note records the corrective theory-first design before
implementation.

The next pass should not start with random perturbations. It should construct
graphs backward from:

1. the GRC9 paper mechanism,
2. the current runtime predicate,
3. the telemetry field expected to confirm the mechanism.

## S0004 Baseline

- Session: `outputs/grc9/phenomenology_discovery/sessions/S0004/`
- Lanes: 22 generated controls
- Total steps: 198
- Graph checkpoints: 220
- Events: 6 total
- Event kind observed: `growth`
- Eventful lanes:
  - `fission_candidate_positive_control`
  - `fission_candidate_negative_control`
- Missing lifecycle events:
  - `spark`
  - `expansion`
  - reassignment evidence downstream of expansion
  - intended growth-pressure birth
  - confirmed fission without accidental growth

## Runtime Gates

### Spark

Runtime spark detection iterates over `state.sink_set` after flux and identity
recomputation. A seed can have a manually assigned sink at load time, but that
is not enough.

Required runtime predicates:

- the intended source node remains an identity sink after `_detect_identities`,
- `active_degree == 9`,
- one of:
  - instability gate passes:
    `cut_out / max(cut_out + support_in, eps) >= tau_instability`,
  - column proxy gate passes:
    `min_b |H_s^(b)| < eps_spark`,
  - sign crossing gate passes when enabled.

Design implications:

- For column-proxy sparks, construct the saturated center and neighbor
  coherences/conductances so `H_s^(b)` cancels in one column after metric
  recomputation.
- For instability sparks, the saturated patch needs actual cut edges to
  outside reservoir nodes. A pure star around the sink has no external cut from
  the patch and therefore cannot pass the instability proxy.
- Runtime metric/potential parameters must preserve the intended flux
  direction. If metric recomputation erases the conductance landscape, tune
  `alpha`, `beta`, `gamma`, `delta`, `kappa_c`, and site-potential parameters
  explicitly in the seed runtime config.

### Expansion And Reassignment

Expansion is downstream of spark. A standalone expansion-like graph is not an
expansion emitter unless it first produces a spark event or is explicitly
marked as post-expansion diagnostic context.

Required runtime predicates:

- a `spark` event exists,
- `_apply_topology_changes` receives that spark,
- expansion creates module nodes,
- old boundary edges exist and can be reassigned by source port column.

Design implications:

- Use one canonical `spark_to_expansion_emitter` for both expansion and
  reassignment tests.
- Preserve old boundary edges by column before spark.
- Set `D_eff_target`, coherence transfer ratios, and internal bond policy
  explicitly.

### Growth

Growth is independent of spark. It requires birth pressure on a node with
inactive ports.

Required runtime predicates:

- `lambda_birth > 0`,
- parent has at least one inactive port,
- `_outward_flux_pressure(parent) > 0`,
- sampled Bernoulli birth succeeds.

Design implications:

- Use a low-degree parent with inactive capacity.
- Construct the potential gradient so the parent has positive outward flux.
- Use high `lambda_birth` for deterministic low-step emission.
- Do not rely on the fission geometry as the growth emitter.

### Fission

Fission telemetry is a post-expansion persistence diagnostic. It should not be
validated by accidental growth.

Required runtime predicates:

- unrelated growth disabled with `lambda_birth = 0`,
- post-expansion module context exists, either via a spark-to-expansion prelude
  or an initial `expansion_registry` record,
- two sink basins persist for `identity_fission_persistence_delta`,
- basin masses exceed `identity_fission_min_basin_mass`.

Design implications:

- Build a `post_expansion_fission_emitter` with a module registry entry and two
  stable sink basins.
- Run for `persistence_delta + buffer`.

## Emitter Targets

### `spark_column_proxy_emitter`

Purpose: force a saturated identity sink with `min_b |H_s^(b)| < eps_spark`.

Expected telemetry:

- event row:
  - `family_extensions.grc9.event_domain == "spark"`
  - `family_extensions.grc9.spark_evidence.column_proxy_gate_pass == true`
- step row:
  - `column_diagnostic.column_proxy_candidate_count > 0`

### `spark_instability_emitter`

Purpose: force a saturated identity sink with high patch cut ratio.

Expected telemetry:

- event row:
  - `family_extensions.grc9.event_domain == "spark"`
  - `family_extensions.grc9.spark_evidence.instability_gate_pass == true`
- checkpoint:
  - saturated source with external cut edges visible around the patch

### `spark_to_expansion_emitter`

Purpose: produce spark and expansion, with boundary reassignment by column.

Expected telemetry:

- event rows:
  - `spark`
  - `expansion`
- event extension:
  - `expansion_evidence.reassigned_edge_count > 0`
  - `expansion_evidence.internal_edge_count > 0`
  - `expansion_evidence.coherence_transfer_ratios`
- checkpoint:
  - module overlay and reassigned boundary edges

### `growth_pressure_emitter`

Purpose: force one intended parent to produce growth from outward flux pressure.

Expected telemetry:

- event row:
  - `family_extensions.grc9.event_domain == "growth"`
  - `growth_evidence.birth_probability > 0`
  - `growth_evidence.selected_parent_port` matches the intended inactive port
- checkpoint:
  - new child attached to the parent

### `post_expansion_fission_emitter`

Purpose: validate identity fission persistence without accidental growth.

Expected telemetry:

- run summary:
  - `expansion_summary.identity_fission_candidate_count > 0`
  - `expansion_summary.identity_fission_confirmed_count > 0`
  - `expansion_summary.identity_fission_max_persistence_steps >= delta`
- event rows:
  - no unrelated `growth` events

## Budget And Coarse Events

Budget correction and coarse-cache invalidation should remain diagnostic
selector targets unless the runtime is changed to emit explicit lifecycle event
rows. For the repaired emitter pass, do not require event rows for these
surfaces.

## Next Session

Use S0005 for repaired lifecycle emitters.

Replay expectation:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0005 --emitter-repair
```

The exact CLI flag can change during implementation, but S0005 must record the
final replay command in its session manifest.
