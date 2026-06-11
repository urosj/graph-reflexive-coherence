# GRC9V3 Column-H Assisted Spark Implementation Checklist

Date: 2026-05-06

Status: complete through Iteration 10

Companion plan:
[GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md)

Read first:

- [papers/2026-04-GRC-9.md](../papers/2026-04-GRC-9.md)
- [specs/grc-9-spec.md](../specs/grc-9-spec.md)
- [specs/grc-9-v3-spec.md](../specs/grc-9-v3-spec.md)
- [GRC9V3-Hessian-Handoff.md](./GRC9V3-Hessian-Handoff.md)
- [GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)
- [GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)
- [GRC9V3-CanonicalColumnH-LaneDecision.md](./GRC9V3-CanonicalColumnH-LaneDecision.md)
- [GRC9V3-LaneA-SparkGateTraceSchema.md](./GRC9V3-LaneA-SparkGateTraceSchema.md)
- [GRC9V3-ArtifactSurfaceHardening.md](./GRC9V3-ArtifactSurfaceHardening.md)

## Completion Rule

Lane B is complete only when it is opt-in, directly computes column-H from
runtime state, emits lane-tagged gate evidence, preserves Lane A golden
behavior, and keeps identity claims post-event / basin-based.

## Iteration 0. Decision Record And Scope Lock

Status: complete

- [x] Record the implementation lane id as `grc9v3_column_h_assisted`.
- [x] Record that this implementation is Lane B v1.
- [x] Add a Lane B V1 Scope Contract section to the plan.
- [x] Add a `V1 Design Choices Versus The Pure Equation` section to the plan.
- [x] State explicitly that Lane B v1 is not the bare GRC-9 Eq. 12 trigger.
- [x] State explicitly that the small-gradient envelope is a GRC9V3 v1 design
      choice.
- [x] State explicitly that a pure Eq. 12 implementation may be opened later as
      a separate lane or regime.
- [x] State explicitly that Lane B v1 results must not be reinterpreted as
      pure-equation results.
- [x] Record what Lane B v1 implements.
- [x] Record what Lane B v1 deliberately excludes.
- [x] Record explicit out-of-scope surfaces:
      near-saturation,
      virtual stubs,
      inflow-weighted transfer,
      broader candidate scope,
      mechanical expansion changes,
      identity acceptance changes,
      landscape robustness.
- [x] Record that future changes must be explicit implementation tasks,
      separate lanes, or comparison passes, not silent changes to Lane B v1.
- [x] Record that Lane B v1 is not plain `canonical_column_h`; it is
      `grc9v3_column_h_assisted`.
- [x] Record `canonical_column_h` as the conceptual diagnostic source, not the
      plain implementation lane name.
- [x] Confirm Lane A id remains `current_hybrid_signed_hessian`.
- [x] Confirm Lane A remains default.
- [x] Confirm Lane C comparison remains separate from Lane B implementation
      until Lane B exists.
- [x] Mark degree-8 near-saturation out of scope for Lane B v1.
- [x] Mark virtual zero-conductance stubs out of scope for Lane B v1.
- [x] Mark identity fission rules out of scope.
- [x] Mark mechanical expansion operator changes out of scope.
- [x] Record source files expected to be touched before editing.
- [x] Expected source-code touch list is reviewed and adjusted:
      `src/pygrc/models/grc_9_v3.py`,
      `src/pygrc/models/grc_9_v3_sparks.py`,
      `src/pygrc/models/grc_9_v3_runtime.py`,
      `src/pygrc/models/grc_9_v3_state.py`,
      `src/pygrc/models/grc_9_checkpoints.py` if checkpoint serialization
      needs Lane B overlays,
      `src/pygrc/telemetry/grc9v3_contract.py`,
      `src/pygrc/telemetry/_grc9v3_extensions.py` if family-extension telemetry
      rows carry Lane B evidence,
      `tests/models/test_grc_9_v3_column_h_assisted.py`,
      `tests/models/test_grc_9_v3_hessian_readiness.py`,
      `tests/models/test_grc_9_v3_sparks.py` if shared spark fixtures need
      coverage,
      `tests/telemetry/test_grc9v3_contract.py`,
      and `tests/telemetry/test_grc9v3_extensions.py`.

Exit criteria:

- [x] Plan and checklist are reviewed.
- [x] Lane naming is unambiguous.
- [x] No runtime behavior has changed.

Summary:

Iteration 0 completed as a documentation and scope-lock pass. Lane B v1 is
recorded as the opt-in `grc9v3_column_h_assisted` runtime lane, with
`canonical_column_h` retained only as the conceptual GRC9 diagnostic source.
Lane A remains the frozen default baseline. No runtime code was changed.

## Iteration 1. Config And Lane Enum

Status: complete

- [x] Add explicit spark lane config with values:
      `current_hybrid_signed_hessian` and `grc9v3_column_h_assisted`.
- [x] Keep default value `current_hybrid_signed_hessian`.
- [x] Add Lane B parameter `enable_column_h_threshold`.
- [x] Add Lane B parameter `eps_column_h`.
- [x] Add Lane B parameter `enable_column_h_sign_crossing`.
- [x] Add Lane B parameter `column_h_sign_crossing_mode`, default
      `theory_product`.
- [x] Add Lane B parameter `eps_column_h_crossing_zero`, default `0.0`.
- [x] Add Lane B parameter `store_previous_column_h`.
- [x] Add Lane B parameter `require_sink_for_column_h_spark`.
- [x] Add Lane B parameter `require_active_degree_9`.
- [x] Add Lane B parameter `enable_near_saturation`, default `false`.
- [x] Add Lane B parameter `near_saturation_degree`, default `8`, but keep
      inactive for v1.
- [x] If sign crossing is supported, record `column_h_sign_crossing_mode`.
- [x] If `zero_band` mode is supported, record
      `eps_column_h_crossing_zero`.
- [x] Document that `theory_product` mode is the pure-equation sign-crossing
      behavior.
- [x] Document that nonzero `zero_band` is a numerical-stability extension.
- [x] Document the mapping between theory `eps_spark` and Lane B
      `eps_column_h`.
- [x] Document whether default sign-crossing mode is theory-product-equivalent
      or zero-band.
- [x] Document how `eps_column_h` maps to the theory's `eps_spark` /
      column-H calibration scale.
- [x] Document how `eps_signed_hessian` maps to the existing Lane A
      signed-Hessian threshold.
- [x] Preserve existing Lane A gradient and signed-Hessian parameters.
- [x] Ensure unsupported lane ids fail clearly.
- [x] Reject `enable_near_saturation=true` in Lane B v1.
- [x] Reject `require_active_degree_9=false` in Lane B v1.
- [x] Reject `require_sink_for_column_h_spark=false` in Lane B v1.
- [x] Require `eps_column_h` when `enable_column_h_threshold=true`.
- [x] Reject `enable_column_h_sign_crossing=true` unless previous-H storage is
      enabled or auto-enabled with an explicit recorded config result.
- [x] Reject Lane B config where both column-H threshold and sign crossing are
      disabled, unless a separate signed-Hessian-only diagnostic mode is
      explicitly introduced.

Tests:

- [x] Default config still selects Lane A.
- [x] Explicit Lane B config is accepted.
- [x] Unknown lane config is rejected.
- [x] Lane B near-saturation config is rejected in v1.
- [x] Lane B `require_active_degree_9=false` config is rejected in v1.
- [x] Lane B `require_sink_for_column_h_spark=false` config is rejected in v1.
- [x] Lane B sign-crossing without previous-H storage is rejected or
      auto-enables storage explicitly.
- [x] Lane B with all column-H branches disabled is rejected unless a separate
      diagnostic mode exists.
- [x] Lane B config alone does not change behavior before the predicate is
      wired.

Exit criteria:

- [x] No behavior change under default config.
- [x] Config names appear in artifacts or traces where params are recorded.

Summary:

Iteration 1 added the opt-in Lane B v1 configuration surface and validation in
`src/pygrc/models/grc_9_v3.py`. Default `spark_lane` remains
`current_hybrid_signed_hessian`. The new config is recorded in resolved params
and backend-selection payload parameters, but candidate detection remains Lane
A until the Lane B predicate iteration.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3.py tests/models/test_grc_9_v3_column_h_assisted.py`
- `.venv/bin/python -m ruff check src/pygrc/models/grc_9_v3.py tests/models/test_grc_9_v3_column_h_assisted.py`
- scoped `git diff --check`
- `.venv/bin/python -m json.tool outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json`
- `.venv/bin/python -m json.tool outputs/grc9v3/hessian_readiness/readiness_gate.json`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_hessian_readiness`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`

Additional artifact regeneration:

- Regenerated ignored Hessian readiness outputs under
  `outputs/grc9v3/hessian_readiness/` from
  `implementation/GRC9V3-Hessian-ImplementationChecklist.md`.
- Regenerated `theory_runtime_gap_ledger.json` and `.md`.
- Regenerated `readiness_gate.json` and `.md`.
- Regenerated `current_hybrid_baseline.md`.
- Full readiness suite now passes: `Ran 75 tests in 0.750s OK`.

## Iteration 2. Direct Column-H Computation

Status: complete.

- [x] Add a single canonical runtime function for direct column-H computation.
- [x] Compute `H_s[b] = sum_a w_s[a,b] * (C_neighbor - C_s)` for columns 1..3.
- [x] Define the state epoch used for conductance/coherence in `H_s[b]`.
- [x] Compute column-H from the same state snapshot used for `gradient_norm`
      and `signed_hessian_min`.
- [x] Use local endpoint ports to group by candidate-local column.
- [x] Ensure endpoint order does not affect candidate-local grouping.
- [x] Ensure remote endpoint port does not affect candidate-local grouping.
- [x] Use base conductance intended for the diagnostic.
- [x] Do not use `flux_coupling` in canonical `H_s[b]`.
- [x] Do not use signed flux in canonical `H_s[b]`.
- [x] Do not normalize `H_s[b]` for the Lane B gate.
- [x] Return `column_h_values`.
- [x] Return `state_epoch`.
- [x] Return `min_abs_column_h`.
- [x] Return `min_abs_column_h_column`.
- [x] Return `column_h_threshold_hit`.
- [x] Return `column_h_branch_hit` for threshold/sign-crossing branch status.
- [x] Return transitional `column_h_gate_hit` as a branch-hit alias until
      Iteration 4 introduces the full `lane_b_candidate_hit` predicate result.
- [x] Return `column_h_gate_reasons`.
- [x] Return `column_h_computation_version`.
- [x] Defer `lane_b_candidate_hit` until Iteration 4, when the full predicate
      is evaluated.
- [x] Optionally return contribution-level `column_h_terms` behind a debug or
      audit flag.
- [x] Keep inactive-port behavior non-gating under Lane B v1 because degree 9
      is required.
- [x] Reject duplicate candidate-local occupied ports in Lane B v1.
- [x] Fail clearly on missing or non-finite coherence/conductance.

Tests:

- [x] Known saturated fixture computes expected `H[1]`.
- [x] Known saturated fixture computes expected `H[2]`.
- [x] Known saturated fixture computes expected `H[3]`.
- [x] Port-to-column grouping is correct.
- [x] Reversed edge endpoint orientation still groups by candidate-local port.
- [x] Remote endpoint port does not determine the candidate-local column.
- [x] Row order within each column is summed correctly.
- [x] Base conductance changes affect `H_s[b]` as expected.
- [x] `flux_coupling` changes do not affect canonical `H_s[b]` unless base
      conductance also changes.
- [x] Non-unit conductance changes only the intended column contribution.
- [x] Duplicate local port is rejected.
- [x] `min_abs_column_h_column` is 1-based.
- [x] Missing/NaN coherence or conductance fails clearly.
- [x] Degree-8 legitimate partial occupancy computes a diagnostic without
      becoming a full Lane B candidate.
- [x] Negative `eps_column_h` is rejected even when threshold mode is disabled.

Exit criteria:

- [x] Column-H values are direct runtime diagnostics.
- [x] Tests cover all three columns.
- [x] Lane A still does not gate on column-H.

Summary:

Iteration 2 added `ColumnHTerm`, `ColumnHResult`, and
`compute_column_hessian_proxy` in `src/pygrc/models/grc_9_v3_sparks.py`.
The helper computes direct runtime column-H proxy values from the current state
snapshot at `state.step_index`, groups by the candidate node's local port
column, uses base conductance, ignores flux-coupling and signed flux, and
returns auditable branch diagnostic fields plus optional contribution terms.

`column_h_branch_hit` is the precise Iteration 2 field for
threshold/sign-crossing branch status. `column_h_gate_hit` remains as a
temporary synonym for compatibility with the earlier checklist wording, but it
is not the full Lane B candidate predicate. Iteration 4 will introduce the full
candidate result inside the degree-9 / sink / gradient envelope.

The helper is diagnostic-only in Iteration 2. It does not mutate state and does
not change Lane A spark candidate detection.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`
- `.venv/bin/python -m ruff check src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`

## Iteration 3. Previous Column-H And Sign Crossing

Status: complete.

- [x] Add previous-column-H storage only when configured.
- [x] Implement default sign-crossing mode `theory_product` as
      `H_prev[b] * H_now[b] < 0`.
- [x] Implement optional `zero_band` sign-crossing mode as a documented
      numerical-stability extension.
- [x] Store previous values by node id or stable runtime node key.
- [x] Report `previous_column_h_values` when available.
- [x] Report `previous_column_h_status`.
- [x] Report `column_h_sign_crossing_enabled`.
- [x] Report `column_h_sign_crossing_mode`.
- [x] Report `eps_column_h_crossing_zero`.
- [x] Report `column_h_sign_crossing_hit`.
- [x] Report `column_h_sign_crossing_columns`.
- [x] Make first-step sign crossing false or unavailable, not guessed.
- [x] Keep threshold and sign-crossing reasons separate.
- [x] Add a zero-band sign function for crossing detection.
- [x] Clear or invalidate previous-column-H values for nodes that are expanded,
      removed, or replaced by a module.
- [x] Do not carry previous-H across node-id reuse unless lineage explicitly
      says it is the same runtime node.
- [x] Record whether previous-H was unavailable because the node is new or
      because storage was disabled.

Tests:

- [x] Previous values unavailable produces no sign-crossing hit.
- [x] Invalid explicit previous values report `invalid_unavailable` and produce
      no sign-crossing hit.
- [x] `theory_product` mode fires on direct opposite-sign products.
- [x] Positive-to-negative crossing produces sign-crossing hit.
- [x] Negative-to-positive crossing produces sign-crossing hit.
- [x] Touching zero without sign change does not falsely record sign crossing.
- [x] Floating-point noise inside the zero band does not produce crossing when
      `column_h_sign_crossing_mode == "zero_band"`.
- [x] Nonzero zero-band value is serialized and visible in diagnostic evidence.
- [x] Previous-H is invalidated after topology changes.
- [x] Threshold hit and sign-crossing hit can be reported independently.

Exit criteria:

- [x] Sign crossing is deterministic and auditable.
- [x] Sign crossing remains disabled unless explicitly configured.

Summary:

Iteration 3 added `refresh_column_h_history` and
`invalidate_previous_column_h_cache` in
`src/pygrc/models/grc_9_v3_sparks.py`. Previous column-H values are stored only
when `store_previous_column_h=true`. History storage is keyed by
`state.step_index`, so repeated candidate detection within the same step does
not shift the same current values into previous values more than once. The
diagnostic may still be recomputed on repeated calls; the idempotency claim is
about history storage, not result caching.

Iteration 3 is state-modifying only for history bookkeeping:
`refresh_column_h_history` writes previous/current column-H history and status
fields into `state.cached_quantities`, and topology-changing expansion clears
that history to avoid carrying values across removed or replaced nodes.
Sign-crossing detection itself remains non-gating and diagnostic-only. The
default `theory_product` mode uses the pure product rule, and optional
`zero_band` mode remains a documented numerical-stability extension.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`
- `.venv/bin/python -m ruff check src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`

## Iteration 4. Lane B Candidate Predicate

Status: complete.

- [x] Implement Lane B predicate under `spark_lane == "grc9v3_column_h_assisted"`.
- [x] Require candidate scope / sink status when configured.
- [x] Require `active_degree == 9`.
- [x] Require `gradient_norm < eps_gradient`.
- [x] Compute `signed_hessian_hit`.
- [x] Compute `column_h_threshold_hit`.
- [x] Compute `column_h_sign_crossing_hit`.
- [x] Compute `column_h_branch_hit` as threshold hit OR sign-crossing hit.
- [x] Keep any `column_h_gate_hit` field as a branch-hit alias, not the full
      candidate decision.
- [x] Compute `lane_b_candidate_hit` as the full Lane B predicate.
- [x] Emit candidate when signed-Hessian hit OR column-H threshold hit OR
      column-H sign-crossing hit inside the saturation/gradient envelope.
- [x] Record `gate_reasons`.
- [x] Emit one candidate per node per step with multiple reasons when multiple
      branches hit.
- [x] Preserve Lane A predicate unchanged.
- [x] Do not blend Lane B into Lane A.

Positive tests:

- [x] Degree 9 + small gradient + signed-Hessian hit + no column-H hit emits
      candidate by `signed_hessian_hit`.
- [x] Degree 9 + small gradient + no signed-Hessian hit + column-H threshold
      hit emits candidate by `column_h_threshold_hit`.
- [x] Degree 9 + small gradient + no signed-Hessian hit + sign crossing emits
      candidate by `column_h_sign_crossing_hit`, if enabled.

Negative tests:

- [x] Degree 8 + small gradient + column-H hit emits no candidate in v1.
      Reason: canonical degree-9 saturation is required; degree-8
      near-saturation is a future extension.
- [x] Degree 9 + large gradient + column-H hit emits no candidate.
      Reason: this is the GRC9V3 v1 envelope rule, not bare Eq. 12 behavior.
- [x] Degree 9 + small gradient + no signed-Hessian hit + no column-H hit
      emits no candidate.
      Reason: no spark branch fired; fullness and small-gradient status alone
      are insufficient.
- [x] Degree 9 fullness only emits no candidate.
- [x] Non-sink emits no candidate when sink is required.
- [x] Equality boundary: `gradient_norm == eps_gradient` follows strict `<`.
- [x] Equality boundary: `min_abs_column_h == eps_column_h` follows strict `<`.
- [x] Equality boundary: `min_signed_hessian == eps_signed_hessian` follows
      strict `<`.
- [x] Signed-Hessian hit plus column-H hit produces one event with both reasons.
- [x] Candidate detection alone does not imply expansion or mutate topology.

Exit criteria:

- [x] Column-H threshold-only positive case proves Lane B is not just Lane A
      telemetry.
- [x] Lane A golden behavior is unchanged.

Summary:

Iteration 4 wired the opt-in Lane B candidate predicate in
`detect_hybrid_spark_candidates`. Lane A remains on the existing
`current_hybrid_signed_hessian` path. Lane B uses the v1 predicate:

```text
sink scope
AND active_degree == 9
AND gradient_norm < eps_gradient
AND (
    signed_hessian_hit
    OR column_h_threshold_hit
    OR column_h_sign_crossing_hit
)
```

Lane B emits the existing `hybrid_spark_candidate` event kind for expansion
compatibility and records `spark_lane`, `lane_b_candidate_hit`,
`column_h_branch_hit`, and `gate_reasons` in the payload. Full event schema
hardening remains Iteration 5.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`
- `.venv/bin/python -m ruff check src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py`

## Iteration 5. Candidate Event Evidence

Status: complete

- [x] Add Lane B lane-tagged candidate payload.
- [x] Keep shared event kind `hybrid_spark_candidate` because the existing
      expansion router consumes that event kind.
- [x] Do not add a distinct event kind in Iteration 5.
- [x] If a shared event kind is used, require `spark_lane` to distinguish Lane B.
- [x] Include `event_schema_version`.
- [x] Include implementation version, e.g. `spark_lane_version = "v1"`.
- [x] Include `candidate_event_id`.
- [x] Include `step_index`.
- [x] Include `state_epoch`.
- [x] Include `column_h_computation_version`.
- [x] Include `spark_lane`.
- [x] Candidate payload records Lane B v1 through
      `spark_lane = "grc9v3_column_h_assisted"`.
- [x] Include `node_id`.
- [x] Include `active_degree`.
- [x] Include `require_active_degree_9`.
- [x] Include `sink_status`.
- [x] Include `require_sink_for_column_h_spark`.
- [x] Include `candidate_scope_status`.
- [x] Include `gradient_norm` and `eps_gradient`.
- [x] Include `signed_hessian_min` and `eps_signed_hessian`.
- [x] Include `signed_hessian_hit`.
- [x] Include `column_h`.
- [x] Include `min_abs_column_h`.
- [x] Include `min_abs_column_h_column`.
- [x] Include `eps_column_h`.
- [x] Include `column_h_threshold_hit`.
- [x] Include `column_h_sign_crossing_enabled`.
- [x] Include `column_h_sign_crossing_mode`.
- [x] Include `eps_column_h_crossing_zero`.
- [x] Include `column_h_sign_crossing_hit`.
- [x] Include `column_h_sign_crossing_columns`.
- [x] Include `column_h_branch_hit`.
- [x] Include `column_h_gate_hit` only as a branch-hit compatibility alias if
      needed by existing payload consumers.
- [x] Include `lane_b_candidate_hit`.
- [x] Include `gate_reasons`.
- [x] Include `near_saturation_enabled`.
- [x] Include `virtual_stubs_used`.
- [x] Include `linked_expansion_event_id` when expansion follows or `null`
      otherwise.
- [x] Candidate payload records sign-crossing mode and zero-band value if sign
      crossing is enabled.
- [x] Candidate payload is sufficient to distinguish signed-Hessian-only,
      column-H-threshold, column-H-sign-crossing, and both-hit candidates.
- [x] Ensure payload can prove the gate without report-time inference.
- [x] Ensure event payload uses the same captured `ColumnHResult` as the
      predicate.
- [x] Ensure event payload distinguishes the direct runtime-computed column-H
      proxy branch from the primary signed-Hessian branch.

Tests:

- [x] Lane B event payload contains all required fields.
- [x] Gate reasons match the branch that fired.
- [x] Runtime event kind and gate reason strings align with telemetry contract
      constants.
- [x] Payload JSON round-trips.
- [x] Payload `column_h` length is exactly 3.
- [x] Event payload values match the captured `ColumnHResult`.
- [x] Candidate id is deterministic for repeated deterministic runs.
- [x] Lane B signed-Hessian-only candidate has `column_h_branch_hit=false`.
- [x] Lane A candidate payloads remain compatible.
- [x] Lane A payloads do not imply direct column-H proxy-branch gating.

Exit criteria:

- [x] Future reports can distinguish Lane A derived proxy from Lane B direct
      runtime column-H proxy-branch gate evidence.

Summary:

Iteration 5 hardened the Lane B candidate event payload while keeping the
shared `hybrid_spark_candidate` event kind for expansion compatibility. Lane B
events now carry schema/version fields, a deterministic candidate event id,
step and state epoch, the captured column-H diagnostic version, branch
attribution fields, sign-crossing mode/zero-band fields, and a
`linked_expansion_event_id` slot that is populated when the existing mechanical
expansion path consumes the candidate. Candidate payloads JSON-round-trip, use
deterministic ids, and are tested against the telemetry contract's required
field list, event kind, spark lane, version, computation version, and allowed
gate reasons.

The published evidence contract lives in `src/pygrc/telemetry/grc9v3_contract.py`
and is re-exported by `src/pygrc/telemetry/__init__.py`. Runtime spark code keeps
its local constants in `src/pygrc/models/grc_9_v3_sparks.py` to avoid a model
layer dependency on telemetry; tests assert the runtime payload stays aligned
with the telemetry contract constants.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/__init__.py`
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/__init__.py`
- `git diff --check`

Post-Iteration 6 hardening validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/__init__.py`
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/models/grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/__init__.py`
- `git diff --check`

## Iteration 6. Expansion Integration

Status: complete

- [x] Route Lane B candidates into existing expansion policy when policy
      permits.
- [x] Ensure the expansion router accepts the chosen Lane B event kind or
      lane-tagged shared candidate event.
- [x] Reuse existing mechanical expansion operator.
- [x] Preserve column-preserving reassignment.
- [x] Preserve `reassignment_map` payload.
- [x] Preserve unit/budget accounting.
- [x] Do not add identity acceptance during expansion.

Tests:

- [x] Lane B positive candidate can lead to mechanical expansion.
- [x] Candidate-only detection does not imply expansion.
- [x] Expansion payload includes `reassignment_map`.
- [x] Expansion reassignment uses old pre-expansion boundary ports.
- [x] Old boundary columns match new endpoint columns.
- [x] Budget is preserved within tolerance.
- [x] Lane B candidate links to expansion event id when expansion follows.
- [x] Lane B expansion event links back to the source candidate id.
- [x] Remote endpoint is unchanged during boundary-edge reassignment.
- [x] Candidate-only event is not treated as identity.
- [x] Mechanical expansion is not treated as identity.

Exit criteria:

- [x] Spark detection changed; expansion semantics did not.

Summary:

Iteration 6 added expansion-side tests for the existing shared
`hybrid_spark_candidate` routing path. The tests cover Lane B candidates
emitted by signed-Hessian-only, column-H-threshold, and column-H-sign-crossing
branches. All three route into the existing `hybrid_mechanical_expansion`
operator without a distinct event router.

The expansion audit verifies that the payload preserves `reassignment_map`,
budget error remains zero in the clean fixture, candidate events receive the
linked expansion id, expansion events link back to the source candidate id, and
reassignment uses the old pre-expansion parent port while preserving the old
parent column in the new endpoint port and leaving the remote endpoint
unchanged. Candidate detection alone leaves topology and event log unchanged,
and mechanical expansion is not counted as identity acceptance.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/ruff check tests/models/test_grc_9_v3_column_h_assisted.py`
- `PYTHONPATH=src .venv/bin/python -m py_compile tests/models/test_grc_9_v3_column_h_assisted.py src/pygrc/models/grc_9_v3_sparks.py`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`

## Iteration 7. Telemetry And Checkpoint Surfaces

Status: complete

- [x] Add telemetry fields for direct Lane B column-H diagnostics.
- [x] Add telemetry fields for direct Lane B gate hit and gate reasons.
- [x] Add checkpoint node overlay field `spark_lane`.
- [x] Add checkpoint node overlay field `column_h`.
- [x] Add checkpoint node overlay field `min_abs_column_h`.
- [x] Add checkpoint node overlay field `min_abs_column_h_column`.
- [x] Add checkpoint node overlay field `column_h_computation_version`.
- [x] Add checkpoint node overlay field `column_h_branch_hit`.
- [x] Add checkpoint node overlay field `column_h_gate_reasons`.
- [x] Preserve distinction between direct runtime diagnostic, direct
      proxy-branch gate, and derived analysis.

Tests:

- [x] Telemetry rows expose Lane B direct diagnostic values.
- [x] Telemetry rows expose Lane B gate reasons.
- [x] Checkpoint overlays expose Lane B diagnostic values when enabled.
- [x] Checkpoint overlays expose Lane B computation version when enabled.
- [x] Checkpoint cache fallback records spark lane and min-column diagnostics.
- [x] Lane A telemetry remains compatible.

Exit criteria:

- [x] Event payload is still the primary gate evidence.
- [x] Checkpoints provide supporting diagnostic state.

Summary:

Iteration 7 extended the GRC9V3 telemetry contract and builders so Lane B
column-H evidence is visible in event rows and step summaries. Candidate event
extensions now expose `spark_lane`, `column_h`, `min_abs_column_h`,
`min_abs_column_h_column`, column-H threshold/sign-crossing fields,
`column_h_branch_hit`, `column_h_gate_hit`, `lane_b_candidate_hit`, and
`gate_reasons`. Step spark summaries mirror the latest candidate's Lane B
column-H diagnostics when present.

Checkpoint support remains secondary evidence: the existing GRC9V3 checkpoint
node overlay path records `spark_lane`, `column_h`, `min_abs_column_h`,
`min_abs_column_h_column`, `column_h_computation_version`,
`column_h_branch_hit`, `column_h_gate_reasons`, and a
`column_h_diagnostic_source` marker when the latest candidate event or current
column-H cache is available. The current-cache fallback now records the
`current_column_h_spark_lane` value written by the history refresh path and
computes the same min-column summary fields used by the latest-candidate path.
The event payload remains the primary causal gate evidence.

Post-review hardening:

- Fixed the checkpoint fallback path so `current_column_h_spark_lane` is
  written when column-H history is refreshed.
- Added `column_h_computation_version` to checkpoint node overlays.
- Added tests for checkpoint latest-candidate and current-cache evidence.
- Clarified in code that `column_h_gate_hit` is a compatibility alias for a
  column-H branch hit, not the full Lane B candidate predicate.
- Left `require_active_degree_9` hardcoded to degree 9 in the v1 predicate by
  design; the config remains a v1 scope-lock parameter.
- Left same-epoch recomputation in `refresh_column_h_history` as a future
  optimization; current idempotency only protects history shifting.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/grcl9v3_replay.py tests/telemetry/test_grc9v3_contract.py tests/telemetry/test_grc9v3_extensions.py`
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/grcl9v3_replay.py tests/telemetry/test_grc9v3_contract.py tests/telemetry/test_grc9v3_extensions.py`
- `git diff --check`

Post-review hardening validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `git diff --check`

## Iteration 8. Lane A No-Regression Suite

Status: complete

- [x] Run existing GRC9V3 unit suite under default config.
- [x] Run Hessian readiness tests under default config.
- [x] Add golden Lane A spark-count tests where missing.
- [x] Verify Lane A candidate counts are unchanged on golden fixtures.
- [x] Verify Lane A event kinds and required payload fields remain compatible.
- [x] Verify derived column-H proxy alone does not trigger Lane A.
- [x] Verify any added diagnostics are marked non-gating under Lane A.
- [x] Verify same-fixture Lane A/Lane B contrast:
      signed-Hessian inactive plus column-H threshold active emits no Lane A
      candidate but emits a Lane B candidate with
      `gate_reasons = ["column_h_threshold_hit"]`.
- [x] Verify default Lane A does not consume or update existing column-H
      history cache entries.

Validation:

- [x] `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_hessian_readiness`
- [x] Broader GRC9V3 suite passes.
- [x] `.venv/bin/python -m ruff check <touched python files>`

Exit criteria:

- [x] Lane A is still the frozen default baseline.

Summary:

Iteration 8 added explicit Lane A no-regression assertions to the shared
GRC9V3 spark tests. The default config is locked to
`current_hybrid_signed_hessian`; the golden saturated fixture still emits one
`hybrid_spark_candidate` by the Lane A signed-Hessian path; Lane A candidate
payloads remain backward-compatible and do not include `spark_lane`,
`lane_b_candidate_hit`, or `column_h`; and a column-H-like threshold condition
does not trigger Lane A when the signed-Hessian branch is inactive. Candidate
detection also leaves the column-H history cache absent under default Lane A.
The final cross-lane contrast uses the same saturated small-gradient fixture
with signed-Hessian inactive and column-H threshold active: Lane A emits no
candidate, while explicit Lane B emits one `column_h_threshold_hit` candidate.
An additional history-isolation test verifies that default Lane A does not
consume or refresh pre-existing column-H history cache entries.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/ruff check tests/models/test_grc_9_v3_column_h_assisted.py`
- `PYTHONPATH=src .venv/bin/python -m py_compile tests/models/test_grc_9_v3_column_h_assisted.py`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/ruff check tests/models/test_grc_9_v3_sparks.py`
- `PYTHONPATH=src .venv/bin/python -m py_compile tests/models/test_grc_9_v3_sparks.py`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry`
- `git diff --check`

## Iteration 9. Documentation And Artifact Surface Updates

Status: complete

- [x] Update `implementation/GRC9V3-Hessian-ImplementationPlan.md`.
- [x] Update `implementation/GRC9V3-Hessian-ImplementationChecklist.md`.
- [x] Update `specs/grc-9-v3-spec.md`.
- [x] Update telemetry contract docs.
- [x] Update artifact surface inventory.
- [x] Update GRC9V3 ports reference guide.
- [x] Update GRC9V3 conceptual/design guide.
- [x] Update experiment handoff notes.
- [x] State that direct column-H proxy-branch gating exists only under
      `spark_lane == "grc9v3_column_h_assisted"`.
- [x] State that Lane A column-H remains derived/non-gating.

Exit criteria:

- [x] Documentation does not retroactively reinterpret Lane A experiments.
- [x] Documentation names Lane B evidence as direct only for Lane B runs.

Summary:

Iteration 9 aligned the implementation, spec, telemetry, artifact inventory,
ports guide, conceptual/design guide, and experiment handoff documentation
after Lane B v1 implementation. The docs now consistently use
`grc9v3_column_h_assisted` as the implementation lane id and reserve
`canonical_column_h` for the conceptual core GRC9 diagnostic source. Lane A is
still documented as `current_hybrid_signed_hessian`, with column-H/cancellation
derived and non-gating. Direct runtime-computed column-H proxy-branch gate
evidence is documented as valid only for explicit Lane B runs whose candidate
payload records `spark_lane == "grc9v3_column_h_assisted"` and a column-H
branch reason.

Validation:

- targeted documentation stale-language scan for old future-Lane-B wording
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/telemetry/grc9v3_contract.py`
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/telemetry/grc9v3_contract.py`
- `PYTHONPATH=src .venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `git diff --check`

## Iteration 10. Lane C Seed Comparison Setup

Status: complete as setup; comparison execution later completed in the
experiment family.

- [x] Defer until Lane B tests pass.
- [x] Select small shared fixture subset.
- [x] Include Experiment B column-interface cancellation.
- [x] Include Experiment C / D4 saturation and spark gating.
- [x] Include Experiment D / D5 refinement mapping and interface memory.
- [x] Include D8 only if Lane B produces refinement events.
- [x] Include D1 / D3 near Lane B candidate events.
- [x] Record shared fixture ids, seeds, params, artifact schema, and lane ids.
- [x] Report Lane A derived proxy separately from Lane B direct runtime
      proxy-branch gate evidence.
- [x] Record that this iteration prepares Lane C only.
- [x] Record that actual Lane C execution belongs to the experiment track.
- [x] Run Lane C comparison artifacts under
      `experiments/2026-05-N01-grc9v3-properties/`.

Exit criteria:

- [x] Lane C comparison is prepared but does not block Lane B implementation.
- [x] Lane C comparison results are produced.

Summary:

Iteration 10 added [GRC9V3-LaneC-ComparisonSetup.md](./GRC9V3-LaneC-ComparisonSetup.md).
Lane C is defined as an analysis/comparison setup, not a runtime predicate.
The setup selects a small seed-0 fixture subset from Experiment B, Experiment
C/D4, Experiment D/D5, conditional D8, and D1/D3 transform artifacts. It records
the paired Lane A/Lane B lane ids, runtime params, artifact schema
`grc9v3_lane_c_comparison_v1`, expected output paths, evidence labels, and
non-claims. Lane A column evidence remains `derived_non_gating`; Lane B column-H
evidence may be labeled `direct_runtime_proxy_branch` only when
`spark_lane == "grc9v3_column_h_assisted"` and a column-H branch reason is
recorded.

This iteration originally prepared Lane C only. The comparison was later run
from the experiment family as
`experiments/2026-05-N01-grc9v3-properties/scripts/run_lane_c_comparison.py`.

Generated:

- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_comparison_manifest.json`
- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_candidate_comparison.csv`
- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_refinement_comparison.csv`
- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_identity_comparison.csv`
- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_branch_attribution.csv`
- `../experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_summary.json`
- `../experiments/2026-05-N01-grc9v3-properties/reports/lane_c_comparison_report.md`
- `../experiments/2026-05-N01-grc9v3-properties/reports/lane_c_blocked_observations.md`

Result:

- comparison rows: `60`;
- direct Lane B column-H proxy-branch rows: `15`;
- candidate/refinement delta rows: `15 / 15`;
- degree-8 near-saturation remains blocked.

Classification:
    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

Validation:

- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/telemetry/grc9v3_contract.py`
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/telemetry/grc9v3_contract.py`
- targeted stale-language scan for Lane B/Lane C boundary wording
- `git diff --check`

## Final Acceptance Gate

Status: complete

- [x] Lane A remains default.
- [x] Lane A golden behavior is unchanged.
- [x] Lane B is opt-in.
- [x] Direct `H_s[b]` values are computed from runtime state.
- [x] Lane B candidate events include direct column-H proxy-branch gate
      evidence.
- [x] Degree 9 is required in Lane B v1.
- [x] Degree 8 near-saturation remains blocked.
- [x] Invalid Lane B v1 configurations are rejected.
- [x] Threshold equality behavior follows the documented strict `<` rules.
- [x] Column-H computation uses one captured `ColumnHResult` for predicate,
      payload, telemetry, and checkpoint overlays.
- [x] Positive signed-Hessian, threshold, and sign-crossing cases pass.
- [x] Negative controls do not trigger.
- [x] Expansion mapping and budget tests pass.
- [x] Identity remains post-event / basin-based.
- [x] Telemetry and checkpoints distinguish direct runtime proxy-branch gate
      evidence from derived analysis.
- [x] Documentation is updated.
- [x] Lane C setup is documented; post-acceptance Lane C execution and result
      artifacts were later produced in the experiment family.
- [x] `git diff --check` passes.

Summary:

Lane B v1 is accepted as `grc9v3_column_h_assisted`. Lane A remains the default
`current_hybrid_signed_hessian` baseline with golden behavior preserved. Direct
column-H proxy-branch gate evidence is available only under explicit Lane B and
is carried by event payloads, telemetry extensions, and checkpoint overlays.
Degree 9 remains required, degree-8 near-saturation remains blocked, and
mechanical expansion / identity acceptance semantics remain unchanged.

Lane C comparison setup is complete in
`implementation/GRC9V3-LaneC-ComparisonSetup.md`. Lane C execution was not part
of the original implementation acceptance gate, but the experiment-side
comparison artifacts were later produced.

Validation:

- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_column_h_assisted`
  - `49` tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
  - `89` tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.models.test_grc_9_v3_column_h_assisted`
  - `107` tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_column_h_assisted tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry`
  - `92` tests passed.
- `PYTHONPATH=src .venv/bin/ruff check src/pygrc/models/grc_9_v3.py src/pygrc/models/grc_9_v3_sparks.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/grcl9v3_replay.py tests/models/test_grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py tests/telemetry/test_grc9v3_contract.py tests/telemetry/test_grc9v3_extensions.py`
  - passed.
- `PYTHONPATH=src .venv/bin/python -m py_compile src/pygrc/models/grc_9_v3.py src/pygrc/models/grc_9_v3_sparks.py src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/grcl9v3_replay.py tests/models/test_grc_9_v3_sparks.py tests/models/test_grc_9_v3_column_h_assisted.py tests/telemetry/test_grc9v3_contract.py tests/telemetry/test_grc9v3_extensions.py`
  - passed.
- Targeted stale-language scan for Lane B/Lane C boundary wording.
  - no matches.
- `git diff --check`
  - passed.

Final classification when complete:

`grc9v3_column_h_assisted_lane_b_implemented_with_lane_a_default_preserved`
