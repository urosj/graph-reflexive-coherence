# Phase T GRC9V3 Closeout

## Purpose

This note closes **Phase T-GRC9V3: GRC9V3 Hybrid Telemetry Extension**.

The closeout claim is deliberately scoped: the completed Phase 7 `GRC9V3`
runtime now has an artifact-backed telemetry surface. This phase does not claim
Phase V visualization, new phenomenology discovery, reviewed motif catalogs, or
GRCL/source-seed lowering.

Current status: those downstream tracks are now complete. This closeout remains
the telemetry-surface closeout; the later source/lowering completion is recorded
in [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

Post-Lane-B status: core `GRC9V3` now also supports the opt-in
`grc9v3_column_h_assisted` spark lane. Phase T event, step, and checkpoint
surfaces can carry Lane B candidate evidence through shared
`hybrid_spark_candidate` payloads, `hybrid_spark_state`, and node overlays.
Backend/config telemetry records `spark_lane`, so lane selection remains
visible even before any candidate event has appeared.

## Implemented Contract

The implemented telemetry family key is:

```text
grc9v3
```

The implemented contract version is:

```text
phase_t_grc9v3_iter1_v1
```

The field-level contract is recorded in:

- [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)

The typed implementation is:

- `src/pygrc/telemetry/grc9v3_contract.py`
- `src/pygrc/telemetry/_grc9v3_extensions.py`

The contract includes:

- step-row extension groups,
- event-row extension taxonomy and evidence groups,
- run-summary extension groups,
- optional graph checkpoint overlays,
- Lane B candidate and column-H proxy-branch evidence when emitted by the core
  runtime,
- ownership tagging,
- compression rules,
- and explicit boundary rules for deferred semantics.

## Implemented Builders

Phase T-GRC9V3 now builds `family_extensions["grc9v3"]` for:

- step rows,
- event rows,
- run summaries,
- graph checkpoint artifacts,
- and graph checkpoint index metadata.

Step rows expose compact runtime summaries:

- lane context,
- backend configuration,
- port-chart summary,
- row-basis differential summary,
- hybrid tensor summary,
- transport summary,
- identity/basin summary,
- hybrid spark state,
- hierarchy state,
- choice/collapse state,
- growth state,
- budget correction summary,
- coarse-cache state.

Event rows classify raw runtime events into the stable telemetry taxonomy:

- `spark` / `candidate`,
- `expansion` / `module_created`,
- `spark` / `completed`,
- `choice` / `detected`,
- `choice` / `resolved`,
- `collapse` / `collapsed`,
- `growth` / `child_attached`,
- `other` / `other`.

Run summaries include:

- final backend summary,
- final port-chart summary,
- final differential summary,
- final identity/basin summary,
- final hierarchy summary,
- final choice/collapse summary,
- final budget summary,
- lifecycle event counts,
- and Appendix E representative fixture summary when applicable.

Graph checkpoints now optionally include:

- `node_overlay`,
- `port_overlay`,
- `edge_overlay`,
- `module_overlay`,
- `choice_overlay`.

The overlays are enabled by default in the representative telemetry runner and
can be disabled with `--disable-checkpoint-overlays`.

## Representative Evidence

The representative telemetry lane is documented in:

- [Phase-T-GRC9V3-RepresentativeTelemetry.md](./Phase-T-GRC9V3-RepresentativeTelemetry.md)

Replay command:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_telemetry.py --outputs-root outputs --steps 3
```

Current artifact root:

```text
outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/
```

The current artifact run contains:

- `3` step rows,
- `7` event rows,
- one run summary,
- one experiment report,
- initial and final snapshots,
- `4` graph checkpoints,
- GRC9V3 checkpoint overlays enabled,
- Appendix E daughter sinks `12` and `16`,
- replay step rows match: `true`,
- replay event rows match: `true`,
- replay final digest match: `true`.

Final representative digest:

```text
8e596eba7c37d1dc6465768c2ff10139ec12e8ebfec51f34aecbfafd8018cdfb
```

## Ownership Boundary

The telemetry surface preserves the parent/hybrid ownership boundary.

GRC9-owned mechanics remain inspectable as mechanics:

- fixed nine-slot port chart,
- port occupancy,
- mechanical expansion modules,
- edge labels,
- inactive-port growth,
- topology mutation,
- and port-graph checkpoints.

GRCV3-owned semantics remain inspectable as semantics:

- row-basis differential state,
- signed-Hessian convention,
- geometric basin seeds,
- hierarchy,
- choice/collapse/learning,
- and quadrature budget interpretation.

GRC9V3-only hybrid behavior is named explicitly:

- hybrid spark candidates,
- mechanical expansion as the refinement action,
- child-basin stabilization as a post-expansion condition,
- completed hybrid sparks,
- Appendix E daughter sinks,
- and choice/collapse over GRC9 port-flux successor structure.

No telemetry payload claims that the same field is simultaneously pure GRC9,
pure GRCV3, and GRC9V3. The `ownership` fields and group names preserve the
distinction.

## Verification

Current verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry tests.telemetry.test_grc9_extensions tests.telemetry.test_grcv3_contract
```

Current result:

```text
37 tests OK
```

Coverage includes:

- typed contract validation,
- enum/status validation,
- unknown event fallback,
- step builder determinism,
- step-row JSON round-trip,
- no state mutation,
- missing-cache explicit availability fields,
- event taxonomy and evidence extraction,
- run-summary lifecycle counts,
- Appendix E summary behavior,
- representative telemetry artifacts,
- replay step/event/final digest checks,
- checkpoint overlays,
- disabled checkpoint-overlay mode,
- and deterministic overlay payloads.

## Deferred Boundary

The following remain outside Phase T-GRC9V3:

- Phase V-GRC9V3 visualization,
- GRC9V3 graph visualization suites,
- GRC9V3 phenomenology discovery,
- reviewed GRC9V3 motif catalogs,
- GRCL/source-seed lowering for GRC9V3,
- barrier and ghost boundary runtime behavior,
- Lorentzian causal semantics,
- anisotropic edge transport,
- multiscale sigma fields,
- non-unit quadrature measures,
- adiabatic expansion execution,
- and broader GRC9V3 discovery seed families.

These are not hidden telemetry failures. They are downstream tracks that now
have a stable telemetry surface to consume.

Current status: Phase V-GRC9V3, GRC9V3 phenomenology discovery, reviewed motif
cataloging, and GRCL-9V3 Revision 1 have consumed this telemetry surface and
are closed as downstream tracks.

## Next Layer

At Phase T closeout time, the next natural layer was **Phase V-GRC9V3
visualization**.

Phase V-GRC9V3 should consume the telemetry and checkpoint artifacts produced
here rather than reaching around the telemetry surface into runtime internals.
The first visualization pass should prioritize:

- the Appendix E representative lane,
- checkpoint overlays,
- expansion module structure,
- child-basin stabilization,
- hierarchy update,
- and choice/collapse evidence.

After Lane B, Phase V should also make the spark cause legible by distinguishing
Lane A signed-Hessian candidates, Lane B signed-Hessian-only candidates, and
Lane B column-H proxy-branch candidates when those payload fields are present.

## Closeout Result

Phase T-GRC9V3 is closed.

`GRC9V3` now has:

- a core runtime from Phase 7,
- typed telemetry contract,
- step/event/run-summary extension builders,
- replayable representative telemetry artifacts,
- checkpoint overlays,
- Lane B-aware candidate/checkpoint evidence surfaces,
- and documented downstream boundaries.

The family telemetry surface was ready for Phase V-GRC9V3 visualization, and
that downstream visualization/source-evidence track is now complete through
GRCL-9V3 Revision 1.
