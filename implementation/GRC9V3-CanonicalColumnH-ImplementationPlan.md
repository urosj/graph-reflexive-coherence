# GRC9V3 Column-H Assisted Spark Implementation Plan

Date: 2026-05-06

Status: implementation complete through Iteration 10; Lane C comparison
executed from the experiment family

## Purpose

This plan defines the repo-level implementation lane that adds direct
column-H spark evidence to GRC9V3 without changing the current Lane A baseline.

Lane B is core runtime work, not an experiment-local patch. It must add
configuration, tests, direct event evidence, telemetry/checkpoint surfaces, and
before/after reporting before any experiment is reinterpreted.

Lane B v1 is not the bare GRC9 Eq. 12 trigger. It is the GRC9V3-specific
column-H-assisted spark interpretation:

- saturation,
- sink-only candidate scope,
- basin-interior / small-gradient envelope,
- signed-Hessian or direct runtime-computed column-H proxy branch.

## Read First

Read these documents before implementing Lane B:

Core theory and specs:

1. [papers/2026-04-GRC-9.md](../papers/2026-04-GRC-9.md)
2. [specs/grc-9-spec.md](../specs/grc-9-spec.md)
3. [specs/grc-9-v3-spec.md](../specs/grc-9-v3-spec.md)
4. [specs/README.md](../specs/README.md)

GRC9V3 Hessian readiness and lane boundary:

1. [GRC9V3-Hessian-Handoff.md](./GRC9V3-Hessian-Handoff.md)
2. [GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)
3. [GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)
4. [GRC9V3-CanonicalColumnH-LaneDecision.md](./GRC9V3-CanonicalColumnH-LaneDecision.md)
5. [GRC9V3-LaneA-SparkGateTraceSchema.md](./GRC9V3-LaneA-SparkGateTraceSchema.md)
6. [GRC9V3-ArtifactSurfaceHardening.md](./GRC9V3-ArtifactSurfaceHardening.md)

Current readiness outputs:

1. `outputs/grc9v3/hessian_readiness/current_hybrid_baseline.md`
2. `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.md`
3. `outputs/grc9v3/hessian_readiness/readiness_gate.md`

This plan supersedes the older shorthand of treating Lane B as a plain
`canonical_column_h` lane. The core GRC9 column diagnostic still comes from the
GRC9 theory/spec, but the GRC9V3 implementation lane is
`grc9v3_column_h_assisted`.

## Lane Decision

Use these lane meanings consistently:

| Lane | Lane id | Meaning |
| --- | --- | --- |
| Lane A | `current_hybrid_signed_hessian` | Current default baseline: active-degree saturation plus small-gradient / signed-Hessian degeneracy evidence. |
| Lane B | `grc9v3_column_h_assisted` | New opt-in GRC9V3 spark lane: Lane A basin/saturation envelope plus direct runtime-computed column-H proxy threshold or sign-crossing branch. |
| Lane C | `comparison` | Completed analysis lane comparing Lane A and Lane B after Lane B exists. |

The older handoff name `canonical_column_h` is retained as the conceptual
source of the new diagnostic, but the implementation lane should not be plain
column-H-only. The GRC9V3 target is `grc9v3_column_h_assisted`.

## Lane B V1 Scope Contract

This implementation is **Lane B v1**.

Lane B v1 is the first GRC9V3-specific implementation of direct column-H
assisted spark detection. It keeps Lane A as the default baseline, preserves
the existing mechanical expansion and identity rules, and adds an opt-in
runtime predicate where the directly computed column-H proxy can trigger a
spark candidate inside the active-degree-9 and small-gradient envelope.

It is not a plain column-H-only lane, not a near-saturation lane, not a new
identity rule, and not a landscape-robustness claim. Future versions may add
near-saturation, virtual stubs, inflow-weighted transfer, stricter
column-H/signed-Hessian corroboration, weighted composite spark scores, broader
candidate scopes, and robustness suites. Lane C comparison is complete as a
post-implementation analysis pass.

Implementation lane id:

```text
grc9v3_column_h_assisted
```

Conceptual diagnostic source:

```text
canonical column-H / H_s^(b)
```

The lane id should not be renamed to `canonical_column_h`, because v1 is not a
plain column-H-only trigger. It is a GRC9V3-specific assisted spark lane.

### What V1 Implements

Lane B v1 implements:

```text
active_degree(s) == 9
AND gradient_norm(s) < eps_gradient
AND (
    min_signed_hessian(s) < eps_signed_hessian
    OR min_b abs(H_s[b]) < eps_column_h
    OR column_h_sign_crossing_hit(s)
)
```

where:

```text
H_s[b] = sum_a w_s[a,b] * (C_neighbor(s,a,b) - C_s)
```

In v1, column-H becomes a direct runtime-computed proxy branch in the spark
predicate. It is no longer merely a report-time derived proxy when
`spark_lane == "grc9v3_column_h_assisted"`.

### What V1 Does Not Implement

Lane B v1 does not implement:

- default behavior change
- degree-8 near-saturation
- virtual zero-conductance stubs
- inflow-weighted expansion transfer
- identity-fission acceptance rules
- changes to the mechanical expansion operator
- a plain column-H-only lane
- a stricter signed-Hessian AND column-H corroboration lane
- weighted modifier / score-combination spark logic
- broader non-sink candidate scope
- landscape-general validation
- full Lane C comparison

### What V1 Claims

A v1 run may claim:

- the runtime directly computed `H_s[b]`
- the Lane B event payload records whether the column-H proxy branch fired
- the candidate event is auditable through direct event evidence

A v1 run must not claim:

- column-H is the true geometric Hessian
- column-H alone can spark outside the v3 saturation / gradient envelope
- mechanical expansion is identity fission
- degree-8 near-saturation is implemented
- the result is landscape-general

Precise safe wording:

> Lane B v1 provides direct runtime evidence that the column-H proxy branch
> fired inside the GRC9V3 saturation / basin-interior envelope.

Unsafe wording:

> Column-H is now the whole spark theory.

## Future Extension Surfaces

The following are not part of Lane B v1. They may be opened later as explicit
implementation tasks, lanes, or comparison passes. They must not silently
change Lane B v1 semantics.

| Surface | Why it is not in v1 |
| --- | --- |
| Degree-8 near-saturation / virtual stubs | Changes event gating. |
| Inflow-weighted expansion transfer | Changes state-transfer policy, not spark detection. |
| Corroborated column-H lane | Uses `signed_hessian_hit AND column_h_gate_hit`, a stricter causal model. |
| Weighted composite spark score | Replaces branch logic with calibrated scoring. |
| Broader non-sink candidate scope | Changes candidate semantics. |
| Additional Lane C comparison packs | Analysis after Lane B exists, not part of implementation semantics. The first Lane C pass is complete. |
| Landscape robustness / held-out CV | Validation suite, not runtime predicate. |
| Checkpoint-window identity persistence | Observer/evidence extension, not spark predicate. |

## Expected Source-Code Touch List

Before editing runtime code, expect the implementation to touch this bounded
set of files. Adjust this list only after reading the code and recording why
the ownership boundary changed.

Runtime/model files:

- `src/pygrc/models/grc_9_v3.py`
- `src/pygrc/models/grc_9_v3_sparks.py`
- `src/pygrc/models/grc_9_v3_runtime.py`
- `src/pygrc/models/grc_9_v3_state.py`
- `src/pygrc/models/grc_9_checkpoints.py`, if checkpoint serialization needs
  Lane B overlays

Telemetry files:

- `src/pygrc/telemetry/grc9v3_contract.py`
- `src/pygrc/telemetry/_grc9v3_extensions.py`, if family-extension telemetry
  rows carry Lane B evidence

Test files:

- `tests/models/test_grc_9_v3_column_h_assisted.py`
- `tests/models/test_grc_9_v3_hessian_readiness.py`
- `tests/models/test_grc_9_v3_sparks.py`, if existing spark integration tests
  need shared fixtures
- `tests/telemetry/test_grc9v3_contract.py`
- `tests/telemetry/test_grc9v3_extensions.py`

Do not edit experiment outputs to make Lane B pass. Lane B is core runtime
work.

## Non-Negotiable Boundaries

- Lane A remains default.
- Lane A candidate behavior must remain unchanged on golden fixtures.
- Lane B is opt-in by explicit configuration.
- Lane B changes spark candidate detection, not mechanical expansion semantics.
- Column-H remains a proxy, but under Lane B it becomes a direct
  runtime-computed proxy branch in the spark predicate.
- Lane B emits direct event evidence that the column-H proxy branch fired only
  when that branch actually fires.
- Derived column-H analysis must still not trigger Lane A.
- Degree-8 near-saturation is out of scope for Lane B v1.
- Non-sink candidate scope is out of scope for Lane B v1.
- Identity fission rules are out of scope.
- Mechanical refinement is not identity emergence.

## Lane B V1 Predicate

For a candidate sink node `s`, compute direct column diagnostics:

```text
H_s[b] = sum_a w_s[a,b] * (C_neighbor(s,a,b) - C_s)
```

where `a` is row `1..3`, `b` is column `1..3`, `w_s[a,b]` is the base
conductance for the edge occupying local port `(a,b)`, `C_s` is the candidate
node coherence, and `C_neighbor(s,a,b)` is the coherence of the neighbor at
that local port.

Lane B v1 emits a spark candidate when:

```text
active_degree(s) == 9
AND gradient_norm(s) < eps_gradient
AND (
    min_signed_hessian(s) < eps_signed_hessian
    OR min_b abs(H_s[b]) < eps_column_h
    OR column_h_sign_crossing_hit(s)
)
```

`column_h_sign_crossing_hit` is enabled only when previous `H_s[b]` values are
available:

```text
any_b H_prev_s[b] * H_now_s[b] < 0
```

This makes Lane B a GRC9V3 column-H-assisted spark lane. Column-H is still a
proxy for local instability, but it is computed directly by the runtime and can
be a direct predicate branch inside the v3 saturation and basin-interior
envelope. It is not a plain column-H-only lane.

## V1 Design Choices Versus The Pure Equation

Lane B v1 is a GRC9V3-specific implementation policy. It is not the bare GRC-9
Eq. 12 trigger.

The pure GRC-9 column-H trigger is:

```text
deg_act(s) == 9
AND (
    Instability(s)
    OR min_b abs(H_s[b]) < eps_spark
)
```

with optional sign crossing:

```text
H_prev_s[b] * H_now_s[b] < 0
```

Lane B v1 instead implements the GRC9V3 column-H-assisted spark policy:

```text
active_degree(s) == 9
AND gradient_norm(s) < eps_gradient
AND (
    min_signed_hessian(s) < eps_signed_hessian
    OR min_b abs(H_s[b]) < eps_column_h
    OR column_h_sign_crossing_hit(s)
)
```

This introduces several deliberate design choices.

| Design point | Pure equation | Lane B v1 |
| --- | --- | --- |
| Candidate scope | Saturated sink in the core GRC-9 rule | Sink-only GRC9V3 basin-chart candidate |
| Degree condition | `deg_act(s) == 9` | Same; degree-8 near-saturation is out of scope |
| Basin-interior envelope | Not explicit in bare Eq. 12 | Required through `gradient_norm < eps_gradient` |
| Instability branch | Abstract `Instability(s)` | Existing signed-Hessian branch: `min_signed_hessian < eps_signed_hessian` |
| Column-H threshold | `min_b abs(H_s[b]) < eps_spark` | `min_b abs(H_s[b]) < eps_column_h` |
| Column-H role | Fast local proxy in the core trigger | Direct runtime-computed proxy branch inside the GRC9V3 envelope |
| Branch logic | `Instability OR column-H` | `signed-Hessian OR column-H threshold OR column-H sign crossing` |
| Sign crossing | Direct product test | `theory_product` mode matches product test; optional `zero_band` is numerical stabilization |
| Identity | Not implied by trigger | Not implied by trigger; identity remains post-event basin persistence |

### Why Lane B V1 Requires The Gradient Envelope

The large-gradient negative case is intentional:

```text
degree 9 + large gradient + column-H hit -> no candidate
```

This is not the bare Eq. 12 behavior. It is the GRC9V3 v1 envelope rule.

Lane B v1 treats column-H as an assisted branch inside the saturation /
basin-interior regime. Column-H may substitute for signed-Hessian degeneracy
inside that envelope, but it may not bypass the envelope.

A future pure-equation lane could implement the bare Eq. 12 behavior without
the small-gradient envelope.

### Why Lane B V1 Uses OR Inside The Envelope

Lane B v1 interprets "possibly aided by" as a substitutive branch:

```text
signed_hessian_hit OR column_h_gate_hit
```

inside the active-degree and gradient envelope.

This is a design choice. It gives column-H a real causal role and makes Lane B
more than Lane A with telemetry.

A future stricter lane could require corroboration instead:

```text
signed_hessian_hit AND column_h_gate_hit
```

Such a lane should use a separate id, for example:

```text
grc9v3_column_h_corroborated
```

### Pure-Equation Lane As A Future Regime

If the project later wants to test the bare GRC-9 Eq. 12 behavior directly, it
should be implemented as a separate lane or regime, not by silently changing
Lane B v1.

Possible future lane id:

```text
grc9_core_column_h
```

or:

```text
grc9_eq12_column_h
```

That lane would test:

```text
deg_act(s) == 9
AND (
    instability_hit
    OR min_b abs(H_s[b]) < eps_spark
    OR sign_crossing_hit
)
```

without the GRC9V3 small-gradient envelope, unless explicitly configured.

Lane B v1 remains:

```text
grc9v3_column_h_assisted
```

and should not be reinterpreted after results are generated.

### Sign-Crossing Modes

The pure theory sign-crossing criterion is:

```text
H_prev_s[b] * H_now_s[b] < 0
```

Lane B v1 treats this as the default `theory_product` mode.

If `zero_band` mode is enabled, it is a numerical-stability extension:

```text
+1 if H > eps_column_h_crossing_zero
-1 if H < -eps_column_h_crossing_zero
 0 otherwise
```

and crossing occurs only when:

```text
sign_prev * sign_now == -1
```

A nonzero zero band can suppress crossings that the pure product test would
detect. Therefore, reports must record `column_h_sign_crossing_mode` and
`eps_column_h_crossing_zero`.

### Threshold Mapping

The pure equation uses `eps_spark` for the column-H proxy scale.

Lane B v1 splits thresholds because the quantities have different roles:

```text
eps_gradient:
    basin-interior / small-gradient threshold

eps_signed_hessian:
    signed-Hessian degeneracy threshold

eps_column_h:
    column-H proxy threshold, mapped to the theory's column-H eps_spark scale
```

When theory-facing calibration is available, use:

```text
eps_column_h = q_H * median_i median_b abs(H_i[b])
```

Otherwise `eps_column_h` must be explicit in params and serialized in
artifacts.

## Why OR Inside The Envelope

The gate uses:

```text
signed_hessian_hit OR column_h_threshold_hit OR column_h_sign_crossing_hit
```

inside the active-degree and gradient envelope.

Lane B v1 interprets the theory phrase "possibly aided by" as an OR/substitute
branch inside the v3 saturation/gradient envelope. This is an implementation
policy, not the only possible reading. A future stricter corroboration lane
could require:

```text
signed_hessian_hit AND column_h_gate_hit
```

and should use a distinct lane id such as `grc9v3_column_h_corroborated`.

The OR policy gives column-H a real causal role without allowing column-H alone
to fire outside the v3 basin/saturation regime. It also preserves useful
auditability: candidate events can distinguish signed-Hessian-only,
column-H-only, and both-hit cases through `gate_reasons`.

Do not require both signed-Hessian and column-H in Lane B v1. That would be a
different stricter lane.

## Out Of Scope For V1

- Default behavior change.
- Degree-8 near-saturation.
- Virtual zero-conductance stubs.
- Inflow-weighted transfer.
- Identity emergence acceptance rules.
- Changing the mechanical expansion operator.
- Making `weighted_least_squares` the default Hessian backend.
- Landscape robustness or broader Lane C comparison.

## Configuration

Add an explicit spark-lane configuration field:

```python
spark_lane: Literal[
    "current_hybrid_signed_hessian",
    "grc9v3_column_h_assisted",
]
```

Default:

```python
spark_lane = "current_hybrid_signed_hessian"
```

Lane B parameters:

```python
enable_column_h_threshold: bool = True
eps_column_h: float

enable_column_h_sign_crossing: bool = False
column_h_sign_crossing_mode: Literal["theory_product", "zero_band"] = "theory_product"
eps_column_h_crossing_zero: float = 0.0
store_previous_column_h: bool = False

require_sink_for_column_h_spark: bool = True
require_active_degree_9: bool = True

enable_near_saturation: bool = False
near_saturation_degree: int = 8
```

Reuse existing Lane A gradient and signed-Hessian parameters where they already
exist, but expose them in Lane B candidate evidence with unambiguous names:
`eps_gradient` and `eps_signed_hessian`.

### Threshold Calibration Mapping

The GRC9 theory uses `eps_spark` for the column-H proxy trigger scale. Lane B
splits implementation thresholds because the quantities have different units
and roles:

- `eps_column_h` maps to the theory's column-H `eps_spark` scale.
- `eps_signed_hessian` maps to the existing Lane A signed-Hessian threshold, or
  to a separately calibrated signed-Hessian scale.
- `eps_gradient` maps to the existing Lane A basin-interior / gradient
  threshold.

Default column-H calibration should follow the theory-facing scale when
available:

```text
eps_column_h = q_H * median_i median_b |H_i^(b)|
```

where `q_H` is a documented dimensionless factor. If no calibration sample is
available, `eps_column_h` must be explicit in params and serialized in
artifacts.

### Config Validation

Reject invalid Lane B v1 configurations early:

- `enable_near_saturation == true` is invalid in v1.
- `require_active_degree_9 == false` is invalid in v1.
- `require_sink_for_column_h_spark == false` is invalid in v1.
- `enable_column_h_threshold == true` requires `eps_column_h`.
- `enable_column_h_sign_crossing == true` requires previous-column-H storage,
  either by rejecting `store_previous_column_h == false` or auto-enabling it
  with an explicit recorded config result.
- `enable_column_h_threshold == false` and
  `enable_column_h_sign_crossing == false` is not a valid
  `grc9v3_column_h_assisted` lane. Reject it unless a separate
  signed-Hessian-only diagnostic mode is explicitly introduced.

These checks prevent Lane B from silently becoming Lane A with a different
event name.

## Step-Loop Timing Contract

Column-H must be computed from the same state snapshot used for
`gradient_norm` and `signed_hessian_min` in the spark predicate.

The `ColumnHResult` used for predicate evaluation must be the same object whose
values are emitted in candidate event payloads, telemetry, and checkpoint
overlays. Do not recompute column-H after expansion or after any state mutation
when filling the candidate payload.

For Lane B v1, `w_s[a,b]` means the current-step base conductance snapshot used
by the Lane B spark-gate computation. If the runtime has separate pre-update
and post-update conductance epochs, the Lane B implementation must name and
serialize the epoch used.

Strict threshold rules:

- `gradient_norm < eps_gradient`
- `min_signed_hessian < eps_signed_hessian`
- `min_abs_column_h < eps_column_h`

Equality at the threshold does not hit unless a future lane explicitly changes
the comparison.

Signed-Hessian convention:

- `signed_hessian_hit` means `min_signed_hessian < eps_signed_hessian`.
- Stable basin interiors are interpreted under the configured sign convention.
- Near-zero, negative, or degenerate directions may hit when the configured
  threshold is positive.

## Column-H Computation Contract

Implement one canonical runtime computation entry point, for example:

```python
compute_column_h(state, node_id, params) -> ColumnHResult
```

The result should include:

- `column_h_values`: tuple/list of three floats `[H1, H2, H3]`
- `min_abs_column_h`: float
- `min_abs_column_h_column`: `1`, `2`, or `3`
- `column_h_threshold_hit`: bool
- `column_h_sign_crossing_enabled`: bool
- `column_h_sign_crossing_hit`: bool
- `column_h_sign_crossing_columns`: list of column ids
- `column_h_sign_crossing_mode`: string
- `eps_column_h_crossing_zero`: float
- `previous_column_h_values`: optional tuple/list of three floats
- `column_h_gate_hit`: bool
- `column_h_gate_reasons`: list of reason strings
- `lane_b_candidate_hit`: bool when evaluated inside the full Lane B predicate
- `column_h_computation_version`: string
- optional `column_h_terms`: contribution-level audit rows

Implementation rules:

- Use local endpoint ports to group terms by the candidate node's local column.
- Endpoint order must not matter. The candidate-local endpoint port is the
  source of row/column grouping, not the remote endpoint's port.
- Use base conductance intended for the diagnostic, not `flux_coupling`.
- Use node coherence values, not signed flux, in the canonical `H_s[b]`.
- Use signed flux only if a future lane explicitly defines a flux-weighted
  diagnostic.
- Do not normalize `H_s[b]` for the gate in Lane B v1.
- Additional normalized diagnostics may be reported, but they are not the gate.
- Inactive ports do not matter in Lane B v1 because active degree 9 is required.
- Duplicate candidate-local occupied ports must be rejected in Lane B v1 unless
  a future lane defines deterministic aggregation.
- Missing or non-finite coherence/conductance values must fail clearly rather
  than silently producing a gate result.

Optional contribution audit rows should have this shape:

```json
{
  "port": 1,
  "row": 1,
  "column": 1,
  "neighbor_id": "j",
  "base_conductance": 0.7,
  "c_node": 0.5,
  "c_neighbor": 0.4,
  "delta_c": -0.1,
  "contribution": -0.07
}
```

This table can be debug-gated. The minimal candidate payload proves that the
gate fired; contribution rows prove how `H_s[b]` was assembled.

## Previous-H Cache Contract

When sign crossing is enabled:

- Store previous column-H values by stable runtime node id.
- Clear or invalidate previous values for nodes that are expanded, removed, or
  replaced by a module.
- Do not carry previous values across node-id reuse unless lineage explicitly
  says it is the same runtime node.
- Record whether previous values were unavailable because the node is new or
  because storage was disabled.
- The default theory-equivalent sign-crossing mode is `theory_product`:
  `H_prev[b] * H_now[b] < 0`.
- The optional numerical-defense mode is `zero_band`. This mode is not the
  pure theory formula; it suppresses crossings inside the configured zero band.
- In `zero_band` mode, use this sign function:
  - `+1` if `x > eps_column_h_crossing_zero`
  - `-1` if `x < -eps_column_h_crossing_zero`
  - `0` otherwise
- A `zero_band` sign crossing occurs only when `sign_prev * sign_now == -1`.
- When `eps_column_h_crossing_zero == 0.0`, zero-band mode is theory-equivalent
  except for exact zero, which does not fire under the direct product test
  either.
- Any nonzero zero band must be serialized and reported as a numerical-stability
  extension.

## Candidate Event Contract

Lane B candidate events must prove why the gate fired. Use a distinct event
kind or a lane-tagged existing candidate kind. Preferred event kind:
`column_h_spark_candidate`.

If a distinct event kind is used, the expansion router must consume that event
kind. If the existing `hybrid_spark_candidate` kind is reused, the payload must
carry `spark_lane = "grc9v3_column_h_assisted"`.

When multiple branches hit for one node in one step, emit one candidate event
with multiple `gate_reasons`, not duplicate candidate events.

Minimum payload:

```json
{
  "event_schema_version": 1,
  "candidate_event_id": "candidate-...",
  "step_index": 12,
  "state_epoch": "pre_expansion_spark_gate",
  "spark_lane": "grc9v3_column_h_assisted",
  "column_h_computation_version": "grc9v3_column_h_v1",
  "node_id": "s",
  "active_degree": 9,
  "require_active_degree_9": true,
  "sink_status": true,
  "require_sink_for_column_h_spark": true,
  "candidate_scope_status": "sink",
  "gradient_norm": 0.00001,
  "eps_gradient": 0.0001,
  "signed_hessian_min": -0.002,
  "eps_signed_hessian": 0.001,
  "signed_hessian_hit": false,
  "column_h": [0.24, -0.00003, 0.18],
  "min_abs_column_h": 0.00003,
  "min_abs_column_h_column": 2,
  "eps_column_h": 0.0001,
  "column_h_threshold_hit": true,
  "column_h_sign_crossing_enabled": false,
  "column_h_sign_crossing_mode": "theory_product",
  "eps_column_h_crossing_zero": 0.0,
  "column_h_sign_crossing_hit": false,
  "column_h_sign_crossing_columns": [],
  "column_h_gate_hit": true,
  "lane_b_candidate_hit": true,
  "gate_reasons": ["column_h_threshold_hit"],
  "near_saturation_enabled": false,
  "virtual_stubs_used": false,
  "linked_expansion_event_id": null
}
```

The event payload is the primary causal evidence. It says this gate fired at
this timestep for this node. Checkpoint overlays are supporting evidence.

Field distinction:

- `column_h_gate_hit` means `column_h_threshold_hit OR
  column_h_sign_crossing_hit`.
- `lane_b_candidate_hit` means the full Lane B predicate hit inside the
  saturation/gradient envelope.
- A Lane B candidate can fire by `signed_hessian_hit` with
  `column_h_gate_hit == false`; reports must not call that a direct column-H
  proxy-branch hit.

## Expansion And Identity

Lane B should reuse the existing mechanical expansion path:

- core plus three primary satellites
- column-preserving reassignment
- reassignment map payload
- budget preservation

Lane B candidate events do not imply identity fission. A completed identity
claim still requires post-event child sink/basin persistence, lineage, basin
mass thresholds, and budget evidence.

## Telemetry And Checkpoint Contract

Telemetry and checkpoints must distinguish:

- direct runtime diagnostic: column-H values computed during the Lane B run
- direct proxy-branch gate: event payload records column-H gate hit and gate
  reasons
- derived analysis: experiment-local recomputation from snapshots

Recommended checkpoint node overlay:

- `spark_lane`
- `column_h`
- `min_abs_column_h`
- `min_abs_column_h_column`
- `column_h_gate_hit`
- `column_h_gate_reasons`

Event payloads remain the source of truth for direct runtime proxy-branch gate
claims.

## Implementation Order

1. Add this plan and checklist.
2. Add config and lane enum with no behavior change.
3. Implement direct column-H computation and unit tests.
4. Add optional previous-column-H storage for sign crossing.
5. Implement Lane B predicate and lane-tagged candidate event payload.
6. Integrate Lane B candidates with the existing expansion policy.
7. Add telemetry/checkpoint surfaces.
8. Add Lane A no-regression and Lane B positive/negative tests.
9. Update documentation and artifact-surface language.
10. Run a small Lane C comparison only after Lane B is stable.

## Required Tests

### Lane A No-Regression

- Lane A remains default.
- Lane A candidate counts are unchanged on golden fixtures.
- Lane A event payloads remain compatible.
- Derived column-H proxy alone does not trigger Lane A.
- If column-H diagnostics are computed globally, they are marked non-gating
  when `spark_lane != "grc9v3_column_h_assisted"`.

### Direct Column-H Computation

Use saturated central-node fixtures with known coherence and conductance.

Verify:

- `H[1]`, `H[2]`, and `H[3]` match hand calculation.
- Port-to-column grouping is correct.
- Reversed edge endpoint orientation still groups by the candidate-local port.
- The remote endpoint port never determines the candidate-local column.
- Row order inside each column is summed correctly.
- Base conductance is used.
- Non-unit conductance changes only the intended column contribution.
- `min_abs_column_h_column` is 1-based.
- Duplicate candidate-local ports are rejected.
- Missing or non-finite coherence/conductance fails clearly.
- Inactive ports do not affect Lane B v1 gate behavior.

### Lane B Positive Cases

- Degree 9, gradient below threshold, signed-Hessian hit, column-H not hit:
  candidate by `signed_hessian_hit`.
- Degree 9, gradient below threshold, signed-Hessian not hit, column-H
  threshold hit: candidate by `column_h_threshold_hit`.
- Degree 9, gradient below threshold, signed-Hessian not hit, column-H sign
  crossing hit: candidate by `column_h_sign_crossing_hit`, if enabled.

The threshold-only column-H case proves Lane B is not merely Lane A with extra
telemetry.

### Lane B Negative Cases

- Degree 8, gradient small, column-H hit: no candidate under Lane B v1.
- Degree 9, gradient too large, column-H hit: no candidate.
- Degree 9, gradient small, no signed-Hessian hit, no column-H hit: no
  candidate.
- Degree 9 fullness only: no candidate.
- Degree 9 but not sink: no candidate when `require_sink_for_column_h_spark`
  is true.
- Equality boundary: `gradient_norm == eps_gradient` does not hit.
- Equality boundary: `min_signed_hessian == eps_signed_hessian` does not hit.
- Equality boundary: `min_abs_column_h == eps_column_h` does not hit.
- Signed-Hessian hit plus column-H hit emits one candidate event with both
  reasons, not duplicate events.

### Sign-Crossing Cases

- Previous `H` unavailable: no sign-crossing hit.
- Previous/current values cross sign: sign-crossing hit.
- Touches zero without sign change: threshold may hit, but sign-crossing reason
  must be reported separately.
- Zero-band floating-point noise does not create a false crossing.
- Previous-H values are invalidated after expansion, removal, replacement, or
  unsupported node-id reuse.

### Expansion Integration

- Lane B candidate can produce mechanical expansion when policy permits.
- Candidate-only mode does not imply expansion if expansion policy blocks it.
- The expansion router consumes the Lane B candidate event kind or lane-tagged
  shared event.
- Expansion payload includes `reassignment_map`.
- Old boundary columns match new endpoint columns.
- Budget is preserved within tolerance.
- A Lane B candidate that expands records or can be linked to the expansion
  event id.

### Identity Discipline

- Candidate event does not count as identity.
- Mechanical expansion does not count as identity.
- Identity is accepted only if post-event basin persistence passes.

## Documentation Updates

If Lane B is implemented, update:

- `implementation/GRC9V3-Hessian-ImplementationPlan.md`
- `implementation/GRC9V3-Hessian-ImplementationChecklist.md`
- `specs/grc-9-v3-spec.md`
- telemetry contract
- artifact surface inventory
- GRC9V3 ports reference guide
- GRC9V3 conceptual/design guide
- experiment handoff notes

The key language change is:

Before Lane B:

- column-H is derived under Lane A.

After Lane B:

- column-H diagnostic may be direct runtime evidence.
- direct column-H proxy-branch gating exists only when
  `spark_lane == "grc9v3_column_h_assisted"`.

## Lane C Comparison After Implementation

Do not rerun everything. Compare a small subset first:

- Experiment B: column-interface cancellation
- Experiment C / D4: saturation and spark gating
- Experiment D / D5: refinement mapping and interface memory
- D8: configured-window identity emergence, if Lane B produces refinement
  events
- D1 / D3: factorization and transpose near Lane B candidate events

Lane C should answer:

- Which column effects were already visible under Lane A as derived proxies?
- Which effects become direct spark-gating effects only under Lane B?
- Does Lane B change refinement frequency, column memory, or child-basin
  outcomes?

Prepared setup:

- [GRC9V3-LaneC-ComparisonSetup.md](./GRC9V3-LaneC-ComparisonSetup.md)

## Minimal Acceptance Criteria

Lane B is ready when:

- Lane A remains default and unchanged on golden tests.
- Lane B is opt-in by explicit config.
- `H_s[b]` is computed directly from runtime state.
- Candidate events include direct column-H proxy-branch gate evidence.
- Degree 9 is required in Lane B v1.
- Degree 8 near-saturation remains blocked.
- Positive threshold and sign-crossing fixtures trigger as expected.
- Negative controls do not trigger.
- Invalid Lane B v1 configurations are rejected.
- Threshold equality behavior is tested and follows strict `<`.
- Column-H computation uses one captured `ColumnHResult` for predicate, event
  payload, telemetry, and checkpoint overlays.
- Expansion mapping and budget preservation still pass.
- Reports can distinguish Lane A derived column proxy from Lane B direct
  runtime proxy-branch gate evidence.
