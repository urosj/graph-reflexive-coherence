# GRC Library Specifications

This directory defines the specification for a Python library that implements
the synchronous Graph Reflexive Coherence model families and the first planned
Lorentzian/event-driven nine-port target.

1. `GRCV2`
2. `GRCV3`
3. `GRCV4`
4. `GRC9`
5. `GRC9V3`
6. `GRC9V4`
7. `LGRC9V3`

The papers are the semantic source of truth. These specs translate that theory into a Python implementation contract.

The specification is split into two layers:

1. core model specifications for the best direct implementation of the papers,
2. integration specifications for downstream environments such as `ril_v0` and `ide_v0`.

The implementation strategy assumed by these specs is:

- core graph and port-graph backends are implemented in-house,
- core models depend on backend protocols rather than third-party graph libraries,
- and external tools such as `networkx` or `pyvis` may be added later only as adapters, interchange helpers, or visualization layers.

## GRCV4 phase boundary

The [post-D10 boundary manifest](../implementation/investigations/grc9v4-constitutive-design/specification/PostD10SpecificationBoundary.json)
hash-freezes every pre-existing normative file in this directory except this
registry. The active `specification_correction` phase is hash-bound to the
committed D11-integrated paper, the accepted D11-C/D11-G9 authority, and the
implementation-readiness audit. It permits changes only to the V4
specification outputs, their schemas/builders, governance records, and this
registry while freezing the accepted proposal, paper, older specifications,
`src/`, and `tests/`. A later implementation phase may change `src/` and
`tests/`, but only after a successor authority explicitly activates
`GRCV4_GRC9V4_implementation`. The pre-existing-spec hashes remain enforced in
every phase.

Run the separate claim, contract, phase-boundary, link, and rendering audit
with the repository virtual environment:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py verify-post-d10-specifications
```

The full `verify-iteration9` command detects the same hash-bound D10.2 entry
state automatically and includes this successor audit when it is active.

## Documents

- `grc-common-interface.md`
  Common abstract model interface, shared datatypes, lifecycle, events, diagnostics, and capability model.
- `grc-common-interface-v4-ext.md`
  Additive, non-retroactive V4 interface extension. It registers the V4 class
  hierarchy and strengthens state authority, complete-profile identity,
  graph/differential backends, lifecycle, capabilities, serialization, and
  atomic failure semantics for `GRCV4` and `GRC9V4` only. It also exposes the
  accepted D11-C reference-map identity and D11-G9 chirality/phase event
  request and failure surfaces.
- `grc-v2-spec.md`
  Baseline graph Reflexive Coherence implementation from `papers/2025-12-GRC-V2.md`, with single dynamical conductance and shared analytic edge labels.
- `grc-v3-spec.md`
  Basin-attribute and multi-metric implementation from `papers/2026-02-GRC-V3.md`.
- `grc-v4-spec.md`
  Normative graph-generic, profile-explicit V4 substrate for D10-plus-D11
  surfaces. It defines the common resource, authority, structural-Hodge,
  complete-step, lifecycle, and claim-ceiling contracts plus the current
  optional A/C by CI/OS/RG2b/PC/CI+PC profile population. Candidate C binds
  the accepted `C-HM-STIFFNESS-BASELINE-v1` reference field, mobility,
  retained-Hodge potential, baseline current, control, derivative,
  realization-stage, and lifecycle contracts.
- `grc-v4-source-manifest.json`
  Machine-readable, path/commit/hash-bound identity of the paper, proposal,
  D10/D10.2 records, accepted D11 resolutions and provenance supplements,
  unchanged common interface, read-only GRC9V3 reduction target, and
  historical G-RC-9 mechanics source used by the V4 stack.
- `grc-v4-contract-schema.json`
  Closed JSON Schema 2020-12 definitions for identity-bearing parameters,
  candidate-discriminated profiles, pre-admission and admitted requests,
  affine mapped events, two-channel history, operation/solver results,
  subdigest preimages, the port-graph payload/digest envelope, canonically
  ordered information-loss tuples, state, reset, event, commit, and receipt
  payloads.
- `grc-v4-conformance-fixtures.json`
  Normative preimplementation coverage catalog for D10-plus-D11 generic,
  Candidate C, realization, lifecycle, exact chiral same-port expansion, and
  independent $10\times4$ disabled-compatibility cases. It is not an execution
  oracle and does not claim that a runtime executed it.
- `grc-v4-conformance-vectors.json`
  Deterministically generated concrete canonicalization, identity, D11-C
  algebra, generic affine event, GRC9V4 expansion, persistent-carrier,
  executable second-depth/covariance, rollback, result-status, subdigest,
  schema-negative, and post-schema semantic-admission vectors plus the
  port-graph envelope and two-channel migration-policy coverage matrices. Its explicit
  `coverage_holds` prevent absent per-profile, RG2b, child-stabilization, and
  legacy-delegate vectors—and absent lifecycle, generic-event, charge-edge,
  and deep-immutability runtime tests—from being misreported as conformance.
  Candidate A target-template identity is defined, but Candidate A GRC9V4
  expansion remains explicitly unadvertised pending its own concrete vector.
- `grc-v4-specification-release.json` and
  `grc-v4-specification-release.sha256`
  Content-addressed release manifest and detached checksum binding the exact
  specifications, schema, catalog, concrete vectors, registry, and controlling
  source bytes, plus the exact readiness- and pressure-audit digests. The
  release is a preimplementation contract, not execution evidence.
- `grc-9-spec.md`
  Nine-slot mechanical substrate implementation from `papers/2026-04-GRC-9.md`, with single dynamical conductance and shared analytic edge labels.
- `grc-9-v3-spec.md`
  Normative legacy hybrid implementation: G‑RC‑9 substrate with GRC‑v3
  semantic lift, especially basin attributes, signed-Hessian hybrid spark
  semantics, immediate constitutive recurrence, complete-step causal-state
  boundaries, and explicit separation between default Lane A and the opt-in
  `grc9v3_column_h_assisted` spark lane.
- `grc-9-v4-spec.md`
  Normative nine-port specialization of `GRCV4`. It adds the fixed port chart
  and row backend, the accepted V4-owned
  `grc9v4_axis_preserving_chiral_same_port_expansion_v1` event, hybrid spark,
  optional gated child-basin completion, column coarse-graining, the exact Candidate-A
  initializer binding, and four independently scoped disabled reductions to
  an embedded read-only `GRC9V3` target for every supported profile, bounded
  by the exact legacy-defined domain.
- `grc-9-v3-evidence-profile.md`
  Bounded Phase 7, B1-GR, and B2-GR verification basis for the GRC9V3
  causal-state, persistence, retention, and Read-Back boundaries. Experimental
  counts and negative searches remain here rather than becoming universal
  normative semantics.
- `lgrc-9-v3-spec.md`
  Lorentzian/event-driven nine-port V3 target. The file uses the hyphenated
  paper/spec naming convention, while the executable runtime name is
  `LGRC9V3`. The first implementation level is LGRC-0 annotation/timing
  evidence over `GRC9V3`; behavior-changing LGRC-1 is opt-in and semi-causal
  unless causal availability buffers exist.
- `grc-lgrc-causal-pathway-contracts.md`
  Iteration 106-frozen V1 contract for GRC/LGRC execution, diagnostic,
  producer, and restoration pathways. It exposes stage-local time, scope,
  distributed authority, configured residue, and claim ceilings without
  introducing a universal runtime API.
- `grc-lgrc-causal-pathway-contracts.json`
  Machine-readable 23-pathway, 52-stage registry for the Phase 8
  causal-pathway consolidation tranche. It is a conformance input, not an
  evidence source or runtime dispatcher.
- `grc-lgrc-causal-pathway-evidence-crosswalk.json`
  Iteration 107-frozen stage-local source, specification, test, historical
  evidence, negative-control, migration, ownership, and claim-ceiling map over
  all 52 stages. It records evidence status but does not establish composition.
- `grc-lgrc-causal-pathway-composition-matrix.json`
  Iteration 108-frozen 26-row directional crossing matrix. It separates endpoint
  grounding from crossing evidence and records compatibility, authority,
  adapter ownership, information loss, controls, claim ceilings, missing
  crossings, and invalid relabels.
- `grc-lgrc-causal-pathway-selection-guide.json`
  Iteration 109-frozen machine selection surface derived from the registry,
  crosswalk, and directional matrix. Its worked cases preserve owner, residue,
  claim ceiling, unregistered-pair, and ambiguity boundaries; it is not a
  runtime dispatcher or evidence source.
- `grc-lgrc-causal-pathway-conformance.json`
  Iteration 110-frozen maintenance policy for the registry, crosswalk,
  composition matrix, and selection guide. The reusable checker validates
  identities, references, ownership, staleness, rule isolation, legal
  re-admission, and claim boundaries without executing pathways or changing
  runtime behavior. Iteration 111 validates the frozen selection surfaces
  against 22 expert-normalized pressure descriptions, seven raw-domain demands,
  and one answer-free blind replay frozen before separate oracle validation.
  The raw layer preserves pathway-only and genuinely unregistered results
  without changing this policy or introducing a dispatcher. I106-I111
  reproducibility builders are stored under `scripts/`; the generated evidence
  package is indexed under
  `implementation/investigations/causal-pathway-consolidation/`, and its chain
  records the resulting path-only bundle transitions.
- `grc-lgrc-causal-pathway-bindings.json` and
  `grc-lgrc-causal-pathway-bindings.md`
  Separate Python linkage authority for all 23 admitted pathways and 52 stages,
  extended at the Iteration 117 B-03 correction with the exact CMP-26 adapter
  crossing. It records modules, qualified symbols, call kinds, binding roles,
  source paths, and source hashes without adding Python linkage fields to the
  semantic registry or creating a dispatcher.
- `grc-lgrc-causal-pathway-binding-conformance.json`
  Iteration 115-frozen prospective policy for exact locks, receipts, use
  graphs, candidates, and structured claim envelopes. Its separate checker
  enforces 20 rules and stale-to-pending-review behavior without executing
  causal mechanisms. Operator-facing use is documented in the
  [binding reference](../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md),
  [user and agent guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md),
  and [runnable examples](../examples/causal_pathway_binding/README.md).
  The binding tranche is accepted through Iteration 125; the
  [closeout](../implementation/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceCloseout.md)
  and [iteration/audit evidence index](../implementation/evidence/causal-pathway-binding-iterations/README.md)
  record the preserved public, artifact, runtime, checker, and claim boundaries
  and the nonblocking I125-N01 evidence-retention debt.
- `lgrc-9-v3-restoration-identity.md`
  Implemented and validated versioned LGRC9V3 restoration-identity contract
  over LGRC runtime state and a read-only projection of its embedded GRC9V3
  state. V1 identifies current state; v2 additionally identifies the persisted
  reset baseline. Both remain distinct from raw snapshot identity.
- `grc-reset-baseline-persistence.md`
  Repository-wide save/load/reset lifecycle contract for all concrete model
  families. It adds a versioned reset-baseline snapshot group without changing
  the shared snapshot schema version or runtime dynamics.
- `grc-integration-layer.md`
  Adapter-layer contract for exposing core models to downstream runtimes without constraining core model design.
- `grc-machine-driver.md`
  Machine-driver contract for IDE-style inspection, snapshotting, patching, and deterministic tooling workflows.
- `grc-embedding-profile.md`
  Lightweight embedding profile for external projects that want to adopt a GRC-backed graph and `step()` loop first, with optional later IDE attachment.

## Family Capability Matrix

| Family | Dynamic transport | Analytic edge labels | Frame baseline | Boundary baseline | Semantic depth |
| --- | --- | --- | --- | --- | --- |
| `GRCV2` | single scalar conductance | shared three-label family, selectable | graph-derived or host-supplied, explicit by `frame_mode` | `prune` by default, richer modes optional | minimal graph realization |
| `GRCV3` | single scalar base conductance | shared three-label family, selectable | graph-derived or host-supplied, explicit by `frame_mode` | explicit `boundary_mode` | basin-attribute / hierarchy semantics |
| `GRCV4` | complete-profile-specific; retained A mobility or C-specific derived factorization | profile-selected; common names remain available when advertised | explicit graph differential and structural-Hodge profile | typed boundary/profile migration and topology-event contract | profile-explicit retention, Read-Back, structural geometry, and lifecycle semantics |
| `GRC9` | single scalar conductance per occupied port-pair | shared three-label family, selectable | fixed intrinsic nine-slot chart | no dedicated pass required; optional `boundary_mode` | mechanical substrate semantics |
| `GRC9V3` | single scalar base conductance per occupied port-pair | shared three-label family, selectable | fixed intrinsic nine-slot chart | explicit `boundary_mode` | combined mechanical + semantic lift |
| `GRC9V4` | inherited complete-profile-specific `GRCV4` transport on a port graph | inherited profile labels plus GRC9 chart diagnostics | fixed intrinsic nine-slot chart and row-basis backend | typed V4 lifecycle plus GRC9 mechanical expansion | substantive nine-port V4 specialization with exact profile-scoped GRC9V3 disabled compatibility |
| `LGRC9V3` | inherited `GRC9V3` transport in LGRC-0; future causal transport only with explicit accounting | inherited labels plus causal delay policy | fixed intrinsic nine-slot chart plus causal-history timing fields | inherited `GRC9V3` boundary in LGRC-0 | causal-history annotation / semi-causal fixed-topology eligibility |

Across the whole family matrix, the broader extension capabilities are shared vocabulary rather than `v3`-only concepts:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

Not every family must implement them by default, and they should not be used to erase family boundaries. The point of the shared vocabulary is:

- every family can state clearly which of these extensions it may support,
- every family can state clearly which it must not claim,
- and any family that does implement one must expose it under the same name and serialize the constitutive choices that make it meaningful.

## Intended Package Shape

The specs assume a package shaped roughly like:

```text
pygrc/
  __init__.py
  core/
    interfaces.py
    types.py
    events.py
    graph.py
    observables.py
  models/
    grc_v2.py
    grc_v3.py
    grc_v4.py
    grc_9.py
    grc_9_v3.py
    grc_9_v4.py
    lgrc_9_v3.py
  integrations/
    ril_v0/
    ide_v0/
  utils/
    curvature.py
    shortest_paths.py
    simplex.py
    serialization.py
```

This layout is guidance, not a hard requirement. The hard requirements are:

- all implemented model families expose the common interface specified in
  `grc-common-interface.md`,
- the core package remains independent of downstream integrations,
- and integration adapters depend on core models rather than the reverse.
