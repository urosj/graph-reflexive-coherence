# Phase 7 Closeout

## Purpose

This note closes core **Phase 7: `GRC9V3` Hybrid**.

The closeout claim is deliberately scoped: `GRC9V3` now has an executable,
deterministic core runtime with representative evidence. It does not yet claim
the later telemetry, visualization, phenomenology-discovery, or GRCL/source
layers that made the completed `GRC9` family cycle fully usable.

## What Was Implemented

Phase 7 now provides:

- a concrete `GRC9V3` model instead of a family stub,
- typed `GRC9V3State` and `GRC9V3NodeState`,
- nine-slot `PortGraphBackend` substrate reuse from `GRC9`,
- row-basis gradient summaries,
- row-basis signed-Hessian summaries,
- two Hessian backends:
  - `row_basis_diagonal` as the default GRC9V3 Eq. G3 backend,
  - `weighted_least_squares` as a GRCV3 comparison backend,
- net-flux row summaries,
- GRC9 Eq. (1) hybrid node tensors in the fixed row basis,
- scalar base conductance on occupied port-pairs,
- analytic edge labels:
  - `geometric_length`,
  - `temporal_delay`,
  - `flux_coupling`,
- potential and antisymmetric port flux,
- flux-topology identities and basin diagnostics,
- geometric basin-seed validation,
- saturation plus basin-interior signed-Hessian spark candidates,
- mechanical expansion through the GRC9 core/satellite module,
- immediate post-expansion quadrature budget enforcement,
- post-expansion child-basin stabilization,
- completed hybrid spark registration,
- hierarchy update from completed hybrid sparks,
- sink-compatibility choice detection,
- collapse and persistent learning state,
- inactive-port growth from outward flux pressure,
- prune-mode boundary behavior,
- unit-measure quadrature budget closure with:
  - `uniform_shift`,
  - `simplex_projection`,
- coarse-cache invalidation after topology/value changes,
- an executable canonical `GRC9V3.step()` loop,
- deterministic save/load snapshots,
- and a representative replayable runtime lane.

## Ownership Boundary

The implementation preserves the Phase 7 ownership rule.

GRC9-owned mechanics remain separately inspectable:

- nine-slot port graph,
- occupied port-pair records,
- expansion module construction,
- boundary edge reassignment by column,
- coherence transfer ratios,
- growth through inactive ports,
- and column/coarse-cache invalidation boundaries.

GRCV3-owned semantics remain separately inspectable:

- basin attributes,
- row-basis gradient/Hessian summaries,
- comparison weighted least-squares Hessian,
- basin seed criteria,
- hierarchy,
- choice/collapse/learning state,
- and quadrature budget interpretation.

Hybrid-only behavior is named explicitly:

- `hybrid_spark_candidate`,
- `hybrid_mechanical_expansion`,
- `hybrid_spark_completed`,
- child-basin stabilization after mechanical refinement,
- and choice/collapse over the GRC9 port-flux successor structure.

## Representative Evidence

The representative runtime lane is documented in:

- [Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)

Replay command:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_runtime.py --outputs-root outputs --experiment-id phase7-grc9v3-representative --steps 3
```

Artifact root:

```text
outputs/phase7-grc9v3-representative/grc9v3/appendix_e_cell_division/
```

The lane produced:

- one `hybrid_spark_candidate`,
- one `hybrid_mechanical_expansion`,
- one `hybrid_spark_completed`,
- three `choice_detected` events,
- one `collapse` event,
- two stabilized daughter sinks: `12`, `16`,
- hierarchy update: `root -> [12, 16]`,
- budget target: `108.0`,
- final budget: `108.0`,
- matching replay step rows,
- matching replay event rows,
- matching replay final digest.

Final representative digest:

```text
8e596eba7c37d1dc6465768c2ff10139ec12e8ebfec51f34aecbfafd8018cdfb
```

This is Appendix E-style evidence: the spark action creates a mechanical module,
and the post-expansion reflexive loop stabilizes two daughter identities. The
event does not directly impose daughter sinks.

## Verification

Focused Phase 7 verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_state tests.models.test_family_stubs
```

Current result:

```text
46 tests OK
```

Coverage includes:

- state construction and snapshot shape,
- parameter validation,
- parent-family default provenance,
- budget target initialization and explicit-zero preservation,
- row-basis differential summaries,
- Hessian backend selection,
- transport labels and flux,
- identity diagnostics,
- hybrid spark and expansion behavior,
- child-basin stabilization,
- choice/collapse/learning,
- growth,
- boundary/coarse-cache behavior,
- step-loop ordering,
- representative artifact replay.

## Deferred Boundary

The following remain explicitly outside core Phase 7 closeout:

- Phase T-GRC9V3 telemetry contract and artifact replay surface,
- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery catalogs,
- reviewed GRC9V3 motif catalogs,
- GRCL/source-seed lowering for GRC9V3,
- barrier and ghost boundary modes,
- Lorentzian causal semantics,
- anisotropic edge transport,
- multiscale sigma fields,
- non-unit quadrature measures,
- richer curvature backends beyond the current `none` path,
- and adiabatic expansion execution beyond preserved schedule storage.

These are not hidden failures of core Phase 7. They are the next tracks after
runtime closeout.

## Closeout Result

Phase 7 can now be treated as the authoritative core `GRC9V3` hybrid runtime
for the implemented loop surfaces:

- executable,
- deterministic,
- replayable,
- artifact-backed,
- distinct from both parent families,
- and honest about its downstream boundaries.

Correctness qualification, May 2026: downstream landscape-inference work found
that the GRC9V3 identity layer did not maintain Appendix G effective basin mass
`M_i` as a current derived runtime quantity. Iteration 9.1 repaired this for
new runtime/checkpoint evidence by recomputing mass from current basin
membership after identity extraction. Older Phase 7 evidence that depends on
basin mass, full geometric basins, or child-basin-mass interpretation remains
incomplete historical evidence unless rerun.

The next correct sequence is:

1. Phase T-GRC9V3 telemetry,
2. Phase V-GRC9V3 visualization,
3. GRC9V3 phenomenology discovery,
4. reviewed motif evidence,
5. then GRCL/source-seed lowering for GRC9V3.

## Post-Core Completion Update

The downstream Phase 7 completion track has now been carried through the same
family closure pattern used for GRC9:

- Phase T-GRC9V3 telemetry is implemented and closed.
- Phase V-GRC9V3 visualization is implemented and closed over representative
  and discovery artifacts.
- GRC9V3 phenomenology discovery produced reviewed runtime motif evidence and
  a source-language handoff.
- GRCL-9V3 Revision 1 is implemented as a source/lowering layer with replay,
  selector validation, visualization, corrected front-growth semantics, and a
  reviewed lowered-source catalog.

Final GRCL-9V3 handoff:

- [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md)

Final GRCL-9V3 reviewed lowered-source catalog:

```text
outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json
```

This update does not widen the original core runtime claim. It records that the
post-core evidence and source-seed layers are now complete, while preserving
the same ownership boundary: GRCL-9V3 source declares preconditions, and
GRC9V3 telemetry provides runtime evidence.

The later basin-mass correctness repair narrows only the relevant
identity-mass claims for older artifacts. It does not invalidate the entire
step loop, but GRC9V3 basin-mass and full-geometric-basin results should use
post-Iteration-9.1 artifacts when cited as final evidence.
