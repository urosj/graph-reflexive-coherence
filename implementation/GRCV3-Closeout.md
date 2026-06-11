# GRCV3 Closeout

## Status

Phase 5 is closed.

This is a **Phase 5** closeout, not yet the full family closeout.

The overall family-level closeout for `GRCV3` should now be read as staged:

1. Phase 5 semantic/runtime baseline: closed
2. Phase T minimal behavior-facing telemetry: closed
3. Phase V behavior-facing visualization from saved telemetry: closed
4. later `GRCV3` graph telemetry and graph-visible visualization: closed
5. later rich-seed direct-translation evidence:
   - `grcv3.rich.v4` now has a saved artifact-backed spark/split/collapse lane
6. remaining open work: projector-side and `GRCL-v3` semantic refinement

`GRCV3` is now the semantic reference family for the graph-discrete RC line:

- basin attributes are explicit in public state
- signed-Hessian semantics are deterministic, serialized, and run-fixed after
  first valid calibration or restored snapshot state
- the Phase 5 runtime loop is explicit and documented
- spark completion is attractor-gated rather than transient-degeneracy-only
- hierarchy survives runtime, save/load, and replay
- choice/collapse state is explicit and deterministic when enabled
- representative runtime evidence exists in addition to unit-level semantics

This does **not** mean `GRCV3` is feature-complete forever. It means the Phase 5
baseline is now operational, reproducible, and semantically pinned down enough
that later work should inherit it rather than reopening its fundamentals
casually.

This document should therefore be read narrowly:

- it remains the authoritative **Phase 5 semantic/runtime** closeout
- it is no longer the authoritative source for telemetry/visualization status
- later Phase T and Phase V work has since closed the telemetry and
  visualization lanes end to end
- later `GRCL-v3` work has also produced a saved rich-v4 direct-translation
  lane with spark, split, and collapse visible in telemetry and graph
  visualization artifacts
- the remaining open `GRCV3` questions are now landscape/projector-side rather
  than baseline-runtime-side

## Guaranteed Baseline

The closed Phase 5 baseline guarantees:

1. Differential summaries:
   - `differential_summary = weighted_least_squares`
   - intrinsic local-frame differential summaries
   - post-flux `net_flux` semantics

2. Signed Hessian:
   - one global `hessian_sign`
   - deterministic initialization
   - `+1` tie-break on exact calibration ties
   - reuse of stored sign on later rebuilds

3. Metric and labels:
   - `metric = tensor_exponential`
   - analytic edge labels for geometric length, temporal delay, and flux
     coupling under the selected label surface

4. Identity and hierarchy:
   - sink/basin layer
   - geometric basin validation layer
   - basin-id keyed parent/child hierarchy
   - deterministic hierarchy serialization

5. Sparks and split progression:
   - `spark = signed_hessian_plus_attractor_delta`
   - soft split initialization
   - attractor-count confirmation
   - deterministic split progression and completion

6. Choice / collapse:
   - `choice = disabled`
   - `choice = sink_compatibility`
   - explicit `choice_detected`
   - explicit `choice_resolved`
   - explicit `collapse`
   - `registry_only` persistence as the current learning boundary

7. Runtime and persistence:
   - executable `step()` loop
   - deterministic save/load replay
   - reproducible snapshot digest under fixed inputs
   - dedicated representative reconstruction script

## Evidence

Closeout evidence used for Phase 5:

- test suite:
  - `./.venv/bin/python -m unittest tests.models.test_grc_v3_runtime tests.models.test_grc_v3_state tests.models.test_grc_v3_differential tests.models.test_grc_v3_metric_labels tests.models.test_grc_v3_hierarchy tests.models.test_grc_v3_sparks tests.models.test_grc_v3_choice tests.models.test_grc_v3_step tests.models.test_grc_v3_serialization`
  - result: `Ran 38 tests ... OK`
- representative runtime smoke:
  - `./.venv/bin/python scripts/run_grcv3_representative_smoke.py --experiment-id phase5-grcv3-closeout --steps 3`
  - artifact root:
    - `outputs/phase5-grcv3-closeout/grcv3/`
  - final snapshot digest:
    - `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`

## Baseline Boundary

What Phase 5 closes:

- the meaning of the baseline `GRCV3` family
- the canonical Phase 5 step loop
- the first executable runtime lane
- the persistence and replay contract

What Phase 5 does **not** close as mandatory baseline behavior:

- alternative Hessian realizations such as a raw-moment paper-literal backend
- alternative choice-score backends
- persistent geometric deformation after collapse
- telemetry-rich or phenomenology-rich experiment programs
- broader host-embedding or multi-backend comparison work

Those belong to later comparative or extension phases unless a future paper or
spec explicitly promotes them into baseline requirements.

## Non-Blocking Future Work

These remain open, but none is a Phase 5 blocker:

1. Add a paper-literal raw-moment Hessian backend for direct comparison against
   the weighted least-squares reference backend.
2. Add alternative choice-score backends based on potential, temporal delay, or
   weighted combinations.
3. Replace `registry_only` persistence with an actual persistent geometric
   deformation update path if Appendix A.4 becomes baseline-critical.
4. Build richer representative experiments where sparks, hierarchy growth, and
   choice/collapse all occur in one executable lane.
5. Compare budget-closure heuristics if a less node-order-sensitive closure rule
   becomes important experimentally.

## Short Retrospective

The main Phase 5 lesson is that `GRCV3` runtime closure and `GRCV3`
seed/lowering closure are different things.

What Phase 5 proved successfully:

- the baseline runtime semantics are executable
- the step loop is explicit enough to defend
- the family can be replayed and serialized deterministically
- choice/collapse and spark/split semantics can be made explicit rather than
  implicit

What later work exposed:

- a correct runtime does not guarantee that weaker shared seeds preserve enough
  geometry to reach the same constitutive regime
- representative runtime lanes are necessary, but they are not evidence that
  real seed-driven lanes are already truthful
- artifact-backed telemetry/visualization review is part of semantic validation,
  not just presentation
- once direct rich-seed semantics became strong enough, the family could be
  closed on a richer evidence ladder than the original Phase 5 baseline:
  saved rich-v4 artifacts now show not only spark/split reachability but also a
  concrete collapse-capable trajectory

## Post-Phase Evidence Note

Later work after the original Phase 5 closeout added a stronger family-level
evidence lane than this document originally had:

- `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/`
- seed:
  - `configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- runtime horizon:
  - `150` steps
- saved outputs include:
  - behavior-facing telemetry/report artifacts
  - dense graph checkpoints
  - graph snapshots
  - graph animation
  - final interactive graph HTML

The recorded event counts in that saved lane include:

- `spark_candidate = 2`
- `spark = 2`
- `split_init = 2`
- `split_complete = 2`
- `collapse = 2`

That matters because it upgrades the status of `GRCV3` rich-seed evidence from:

- “spark-capable under targeted probes”

to:

- “artifact-backed seed-driven spark/split/collapse trajectory exists and is
  visually inspectable”

This does not change the narrow purpose of the current document as a Phase 5
baseline closeout. It does change how later phases should read the family:

- baseline runtime semantics are closed
- telemetry/visualization are closed
- and at least one rich-v4 source lane now carries nontrivial reflexive
  behavior end to end through saved artifacts

So the main handoff rule after Phase 5 is:

- inherit the runtime baseline as closed
- but treat projector/source semantics as a separate validation surface rather
  than assuming they are solved automatically by runtime closure

For the fuller post-phase retrospective, read:

- [GRCV3-Retrospective.md](./GRCV3-Retrospective.md)

## Handoff Rule

Any later phase that builds on `GRCV3` should start from:

1. [GRCV3-Closeout.md](./GRCV3-Closeout.md)
2. [GRCV3-Retrospective.md](./GRCV3-Retrospective.md)
3. [Phase-5-StepLoop.md](./Phase-5-StepLoop.md)
4. [Phase-5-ConstitutiveReview.md](./Phase-5-ConstitutiveReview.md)
5. [Phase-5-RepresentativeRuntime.md](./Phase-5-RepresentativeRuntime.md)

If later work wants to change baseline `GRCV3` semantics, it should do so
explicitly and record the reason, rather than drifting through implementation.
