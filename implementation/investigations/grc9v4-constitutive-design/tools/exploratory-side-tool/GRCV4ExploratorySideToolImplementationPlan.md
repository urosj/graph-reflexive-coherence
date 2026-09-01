# GRCv4 Exploratory Side Tool Implementation Plan

**Date:** 2026-08-28
**Status:** Iterations 0-6 accepted; Iteration 7 authorized
**Companion checklist:** [GRCV4ExploratorySideToolImplementationChecklist.md](./GRCV4ExploratorySideToolImplementationChecklist.md)
**Source investigation:** [GRC9V4 constitutive design](../../README.md)

**Iteration 0 record:** [ETC0SourceAndLayoutContract.md](./records/ETC0SourceAndLayoutContract.md)
**Iteration 1 record:** [ETC1SourceAdapterAdmission.md](./records/ETC1SourceAdapterAdmission.md)

## Purpose

Build a bounded exploratory side tool over the accepted D0-D10.2
constitutive-design investigation. The tool should make the investigation
easier to consume in two complementary ways:

1. a forensic Python/notebook surface for exact source tracing and report
   generation;
2. a navigational web surface for focused graph inspection and precomputed
   structural ripple visualization.

The tool does not alter the accepted investigation. It reconstructs and
validates existing relationships, then exposes derived views whose authority
never exceeds their source records.

## Product Boundary

The completed tool may support:

- source-bound claim, debt, gate, candidate, profile, object, and contract
  navigation;
- deterministic reconstruction of accepted lineage;
- exact identification of invalidated claims and reactivated debts when the
  accepted records already define that dependency;
- identification of the earliest accepted gate that must be reopened;
- explicit declaration that downstream results become unknown when the
  accepted records do not define the counterfactual continuation;
- deterministic scenario exchange between Python and the browser;
- static, focused visualizations over generated tables.

It may not support or claim:

- mutation of any accepted decision record;
- a new GRCv4 equation, edge, candidate, profile, or scientific result;
- prediction of what a reopened gate would conclude;
- numeric physical effects from structural counterfactuals;
- proof from a speculative scenario;
- browser-side scientific propagation;
- V4 runtime implementation, specification conformance, or model execution;
- replacement of the accepted build/audit scripts.

## Source Authority

### Primary machine authorities

| Source | Tool role |
| --- | --- |
| `D10NormativeClaimTopology.json` | 39 current claims, 29 historical claim nodes, claim categories, and reciprocal claim/debt edges. |
| `D10DebtClaimTransformationLedger.json` | 29 D9-to-D10 debt transformations, activation conditions, successor claims, and 11 verification obligations. |
| `D10_2FullSubstrateProvenanceAndPromotionAudit.json` | 67 normatively load-bearing parent objects, 152 normative equation/contract rows, profile links, claim links, and substrate provenance. |
| `D9ResidualDebtLedger.json` | Predecessor debt status and D9 residual lineage. |
| D0-D10.2 decision records | Gate identity, accepted predecessor digest, candidate disposition, realization lineage, controls, and claim ceilings. |
| D9 profile/lifecycle records | Ten current profiles, lifecycle surfaces, event semantics, profile-qualified state authority, and four predecessor post-spec verification-obligation occurrences carried into D10 lineage. |

### Authority rules

- Every scientific node and propagation-bearing edge must be extracted from a
  committed accepted machine record.
- The 67 D10.2 parent objects are not relabeled as 67 equations.
- The 152 D10.2 equation/contract rows remain a distinct graph layer; the 85
  expanded rows remain distinguishable from parent-atomic contracts.
- Human-friendly labels may live in a derived annotation sidecar only when the
  sidecar records its source object, source digest, annotation type, and
  non-authoritative status.
- Annotation-only edges may affect display but may never affect propagation.
- Per-schema canonical digest handling must reuse or exactly match the accepted
  builders/auditors. There is no single assumed digest field for all records.
- A source bundle is admitted only when every required file, digest, SHA where
  declared, reference, and expected accepted status validates.
- Human acceptance of ET-C0 is the explicit root of trust. Successor gates
  verify its accepted status and exact record digest, but do not claim to
  derive or replace the human acceptance decision.

## Versioned Immutable Source Contract

The kernel loads source records read-only and computes a source-bundle identity
before graph construction. It records source file hashes before and after every
build and fails if any source byte changes.

The admitted D0-D10.2 bundle is the current accepted snapshot, not a declaration
that the constitutive investigation is final. Bundle immutability and repository
evolution are separate contracts:

```text
admitted source bundle
  versioned, exact, immutable, reproducible

observed repository source inventory
  may acquire new records or new accepted successors
  may differ from the inventory admitted by the current bundle
```

Every tool entry point that can load, build, report, or serve a bundle first
performs a read-only discovery scan. Discovery compares the admitted source IDs,
paths, statuses, schemas, canonical digests, and file SHAs with the observed
decision-record inventory. It emits a separate deterministic observation
receipt with one of these source states:

```text
current_bundle_exact
new_unprocessed_source_available
admitted_source_identity_changed
admitted_source_missing
source_observation_unreadable
```

The observation receipt is not part of the accepted scientific source-bundle
identity and cannot add nodes or edges. For an unadmitted file it may record
only repository-relative path, file SHA, and safely readable top-level schema,
status, and record ID fields. These are discovery metadata, not an
interpretation or acceptance decision.

A newly observed record does not retroactively invalidate an older bundle as a
historical snapshot. It does prevent that bundle from being presented as the
complete current repository state. A changed or missing admitted source also
blocks a live rebuild against that bundle. No case permits automatic parsing,
schema guessing, status promotion, or partial graph insertion.

The refresh path is explicit:

```text
discover unprocessed source
  -> classify schema and authority without consuming scientific content
  -> implement or update the schema-specific adapter
  -> admit a successor source-bundle identity
  -> rerun reference and graph-conformance checks
  -> rebuild every derived graph/report/ripple/browser artifact
  -> accept the successor processing cycle
```

Notebook, report, build, and local-serving commands must surface the discovery
state before presenting results. A prebuilt static bundle records the source
bundle and observation receipt used at build time; when it cannot rescan the
repository, it must call itself a snapshot and must not claim to be current.

Generated files must remain inside this investigation package, under a derived
or scratch path selected during Iteration 0. They must never be written into:

```text
implementation/investigations/grc9v4-constitutive-design/decisions/
src/
specs/
tests/
```

Committed generated artifacts, if any are later selected, must include the
kernel schema version, source-bundle digest, builder version, deterministic
payload digest, and a statement that they are derived navigation surfaces.

### Deterministic serialization

Every emitted artifact, including graph projections, forensic reports, ripple
tables, scenario files, and browser bundles, must use one canonical serializer:

```text
UTF-8
sorted mapping keys
fixed JSON separators ("," and ":")
allow_nan = false
all unordered collections sorted before emission
one frozen finite-number formatting policy
```

The policy applies to payload bytes, not only digest computation. A semantic
match with different bytes is insufficient for a deterministic rebuild.

## One Kernel, Two Front Ends

```text
accepted records
  -> source adapters
  -> validated graph kernel
       -> forensic API and notebook recipes
       -> scenario validator
       -> ripple compiler
            -> static JSON bundle
                 -> Cytoscape.js renderer
```

All relationship interpretation and counterfactual classification lives in the
Python kernel. JavaScript may search, filter, select, animate, and render only.
It may not infer a missing edge, activate a claim, select a reopening gate, or
calculate a ripple.

## Kernel Data Model

### Node families

```text
current_claim             39 accepted D10 claim nodes
historical_claim          29 predecessor claim nodes retained by D10
debt_transformation       29 D9-to-D10 transformation rows
verification_obligation   11 current D10 obligations, preserving the four D9 source occurrences as lineage rather than duplicate evidence
gate_record               accepted D0-D10.2 records and named successors
candidate                 A, B, C, and the closed uninstantiated D slot
realization               CI, OS, RG-1/RG-2b, PC, CI+PC, comparison rows
profile                   ten current D9/D10 profiles
normative_object          67 D10.2 parent objects
equation_contract         152 D10.2 equation/contract rows
source_record             accepted file/digest identities
annotation                optional non-authoritative display metadata
```

Candidate D must be represented as a source-bounded admission slot rejected on
ontology because it remained uninstantiated and not materially distinct. It is
not shown as a fully formed fourth architecture that lost a later comparison.

### Verification-obligation node model

D9 post-spec obligations and D10 verification obligations share one
`obligation_id` namespace. The kernel creates one node per unique obligation ID,
not one node per source occurrence. Every forward-only
`requires_verification_from` edge carries:

```text
originating_gate_id
originating_record_id
originating_record_digest
source_json_pointer
```

This preserves each D9 and D10 occurrence without double-counting a shared
obligation. Verification obligations remain future work surfaces, not accepted
evidence. Backward provenance reconstruction stops before an obligation and
never traverses it as support for a claim, regardless of how many accepted
records reference the same obligation ID.

### Edge families

The kernel uses two physically disjoint edge tables that share node IDs but no
rows:

```text
propagation_edges
annotation_edges
```

`propagation_edges` contains only source-recorded relations that may affect
reachability, support, invalidation, routing, or lineage. Its relation families
include, where present in accepted sources:

```text
supported_by
blocked_by
conditioned_by
routed_through
negative_successor_of
successor_of
predecessor_claim
transformed_from
resolved_negative_by
accepted_at
supersedes
predecessor_record
parent_object
accepted_claim
active_in_profile
candidate_scope
realization_scope
source_identity
requires_verification_from
```

`annotation_edges` contains only display metadata and uses separate annotation
relation types. It cannot carry `required`, `one_of`, `conditional`, or
`negative_boundary` support semantics. No authority flag can convert an
annotation row into a propagation row; doing so requires rebuilding it from an
accepted source through a propagation adapter.

Gate effects must use transformation verbs from the accepted records, such as
admit, confirm, narrow, split, replace, route, supersede, resolve-negative, and
condition. A generic `gate produces claim` edge is insufficient when a gate
only narrows or routes an inherited claim.

### Support semantics

Reachability alone is not enough to classify a claim as supported or lost.
Every propagation-bearing support relation must state whether it is:

```text
required
one_of
conditional
negative_boundary
```

Display-only relations exist only in `annotation_edges` and are excluded from
all support evaluation.

If the source does not determine conjunction/disjunction semantics, the kernel
must return `indeterminate_requires_review` rather than guess.

## Lineage Model

The accepted investigation is a directed acyclic lineage, not a flat
`D0 -> D10.2` list. The kernel must represent:

- the D0-D7 primary chain;
- D4-v2 through D7-v2 candidate-completion successors;
- D7G-v1, D7G-v2, and the post-v2 Hodge correction;
- D8-A, coupled/implicit pressure, and architecture-local D8-B;
- operator-split, reconstructed-geometry, and persistent-carrier branches;
- comparative synthesis and the CI+PC hybrid;
- D9 lifecycle closure;
- D10 claim synthesis and D10.1/D10.2 provenance successors.

The web gate pipeline may project that DAG onto a readable spine, but the
kernel and scenario records must preserve branches, corrections, predecessor
digests, and supersession.

## Kernel Invariants

The initial accepted source bundle should fail closed unless all of these hold:

1. Current claims, historical claims, debt transformations, parent objects,
   and equation/contracts have the accepted counts and unique IDs.
2. Current and historical claim IDs are disjoint.
3. Every claim/debt relation has the accepted reciprocal typed counterpart.
4. Every debt disposition has a claim-ledger disposition.
5. Every predecessor debt is transformed, carried, routed, or resolved without
   silent disappearance.
6. All claim, debt, object, contract, profile, gate, candidate, realization,
   and source references resolve.
7. Gate predecessor relationships are acyclic and digest-consistent.
8. Every propagation-bearing equation/contract row names its parent object,
   accepted claim IDs, profile IDs, and source lineage as available.
9. Propagation and annotation edge tables are disjoint; annotation-only input
   cannot contribute to reachability, invalidation, routing, or ripple output.
10. Browser bundles contain no rule absent from the kernel-produced table.
11. Source bytes are unchanged by load, build, report, and precompute steps.
12. Stable ordering makes graph and ripple outputs byte-identical on rebuild.
13. Verification obligations are reachable only in the forward work direction
    and never appear in backward accepted-evidence reconstruction.
14. Every emitted JSON artifact uses the canonical deterministic serializer;
    NaN, unsorted sets, and implementation-dependent ordering fail closed.

Accepted counts are source-bundle identity checks, not permanent assumptions
for future revisions. A source change requires explicit adapter re-admission
and a new source-bundle identity.

## Forensic API

Implement pure functions before notebook presentation:

| Function | Result |
| --- | --- |
| `gate_act(record_id)` | Accepted gate restriction, obligation, question, authority, claim transformations, and predecessor identity. |
| `debt_lifecycle(debt_id)` | Predecessor state, transformation, current claims, activation condition, and verification routing. |
| `reconstruction_path(claim_id)` | Backward trace through claims, debts, gates, objects, contracts, and source records. |
| `candidate_career(candidate_id)` | Candidate disposition across the lineage DAG without flattening routed and rejected states. |
| `pruned_choices_at(record_id)` | Source-recorded exclusions, alternatives, and blocked relabels. |
| `negative_claims()` | Accepted negative claims and the exact stronger relabel they prevent. |
| `object_dependents(object_id)` | Claims, profiles, contracts, candidates, and gates that depend on a parent object. |
| `contract_provenance(contract_id)` | Parent objects, accepted claims, profiles, source lineage, and blocked overreads. |
| `gate_contribution(record_id)` | Added, inherited, narrowed, routed, superseded, and resolved-negative content. |

Outputs are classified as either:

```text
forensic_evidence_trace
speculative_structural_counterfactual
```

Only the first is an accepted-source reconstruction. Neither class creates new
scientific evidence.

## Counterfactual Mutation Algebra

Use typed mutations rather than generic `weaken` and `strengthen` labels:

```text
remove_term
replace_operator
change_authority
change_stage
change_normalization
change_profile_parameterization
add_derivation
remove_derivation
change_candidate_disposition
```

Every mutation includes:

```text
target_id
target_kind
mutation_type
baseline_record_id
baseline_record_digest
profile_scope
candidate_scope
realization_scope
declared_payload
```

The kernel may return only:

```text
exact_invalidation
exact_debt_reactivation
exact_negative_activation
exact_route_change
no_propagation_bearing_effect
requires_reexecution_from_gate
unknown_beyond_evidence_frontier
indeterminate_requires_review
invalid_mutation
```

The critical rule is:

> Reopening a gate invalidates downstream accepted authority; it does not
> predict what the rerun will conclude.

For example, admitting Candidate B as complete at D7-v2 can identify the
earliest invalidated successor and missing B-specific work. It cannot synthesize
B-specific D7G-D10 claims because those accepted results do not exist.

### Existing-surface and reopening-boundary mutations

The mutation algebra admits these target kinds at minimum:

```text
equation_contract
normative_object
gate_record
candidate
```

Equation/contract and parent-object mutations operate on existing
propagation-bearing paths. The ripple sparsity rule applies directly: an
annotation-only or otherwise non-load-bearing target returns
`no_propagation_bearing_effect`.

Gate and candidate-disposition mutations are different. They need not have an
existing accepted claim path from the proposed disposition, because the source
may have routed or rejected that disposition. Instead, the mutation must name a
source-recorded gate/disposition and open its **reopening boundary**. Frontier
propagation then starts at that accepted gate and follows its accepted
successor, condition, transformation, and support edges. Missing work may be
reported only when the accepted route/debt records name it.

Thus `change_candidate_disposition` for Candidate B at D7-v2 must reopen D7-v2
and produce a non-empty bounded frontier even though no accepted B
equation/contract exists. It must not be rejected by equation-level sparsity,
and it still cannot invent the absent B writer, lifecycle, or D7G-D10 results.

### Evidence-frontier computation

A mutation invalidates a DAG region, not a fixed suffix of a linear gate list.
The kernel computes the boundary from `propagation_edges` only:

1. Evaluate the mutated target's source-recorded support predicates and collect
   every node whose required support is unsatisfied or whose recorded
   activation condition is falsified.
2. Reduce that set to the minimal invalidation-root antichain: remove any root
   already downstream of another invalid root. A mutation may therefore have
   more than one earliest invalidated node or reopening gate.
3. Form the tentative frontier from all propagation-bearing descendants of the
   minimal roots through accepted successor, condition, transformation, and
   support relations.
4. Subtract a descendant only when its complete support predicate remains
   satisfied by accepted support outside every mutated subtree. Merely finding
   another incoming edge is insufficient; `required`, `one_of`, `conditional`,
   and negative-boundary semantics must still pass.
5. Classify the minimal roots as exact invalidations when the accepted graph
   determines the result, or as `requires_reexecution_from_gate` when it does
   not. Remaining unsupported descendants are
   `unknown_beyond_evidence_frontier`.

The output records `earliest_gates_to_reopen` as a deterministically ordered
set. A singular convenience field may be emitted only when that set has one
member. Independently established candidate/profile branches remain known.

#### Claim support predicate

A claim's support is evaluated from its source fields, not graph reachability:

- every `evidence_refs` entry must resolve to its accepted gate or source
  record with the admitted identity;
- every `bearing_debt_ids` and `debt_edges` entry must retain the accepted
  transformed disposition that supports, narrows, conditions, routes, or
  negatively bounds the claim, with no exact reactivation that invalidates that
  disposition;
- the claim's `activation_condition` must hold. `always` adds no further
  condition, while every other condition must be evaluated only from its
  source-recorded semantics.

A descendant is subtracted from the frontier only when this complete predicate
still passes through accepted support outside every mutated subtree. An
alternative incoming edge alone is insufficient.

### Debt-reactivation classification

A reopening is `exact_debt_reactivation` only when an accepted transformation
records a conditional closing with an explicit precondition and the mutation
falsifies that precondition. The reactivation is then a deterministic
consequence of accepted source semantics.

If a transformation is recorded as confirmed, narrowed, split, routed, or
resolved-negative without such a conditional reopening rule, a mutation may
only return `requires_reexecution_from_gate`. Historical
`must_close_before_D10` metadata is not current D10 authority and cannot make a
reactivation exact.

### Blocked-overread risk

A mutation may remove or make inapplicable the exact premise used to guard a
blocked overread. The kernel reports the affected overread ID and its
source-recorded hardening statement in `blocked_overreads_at_risk`. This is a
warning about a speculative scenario, never activation of the stronger claim;
the overread remains blocked until a source-authorized successor establishes
otherwise.

## Ripple Table Contract

Ripple rows are keyed by more than an object and a generic change label:

```text
source_bundle_digest
baseline_record_id
baseline_record_digest
target_id
target_kind
mutation_type
profile_id or all_profiles_aggregate
candidate_scope
realization_scope
```

Each row records direct and transitive consequences separately:

```text
claims_invalidated
debts_reactivated
negative_claims_activated
routes_changed
earliest_gates_to_reopen
profiles_affected
candidates_affected
realizations_affected
known_through_evidence_frontier
unknown_beyond_evidence_frontier
blocked_overreads_at_risk
verification_obligations_at_risk
source_edge_refs
```

Rows must be deterministic kernel output. The web client receives no rule
tables and no graph algorithm that can calculate new scientific effects.
`verification_obligations_at_risk` is a forward-work impact list. It does not
support a claim, reopen a scientific debt, or turn an unexecuted obligation into
accepted evidence.

### Profile-scoped propagation

A mutation propagates only through profiles named by the target's accepted
`profile_ids`, disabled-reduction profile rows, candidate scope, realization
scope, and other source-recorded activation conditions. D10.2 family counts are
coverage counts, not profile counts, and must not be used as propagation
shortcuts. An empty profile list is not silently interpreted as all profiles;
the adapter must resolve a source-backed common scope or classify the scope as
indeterminate.

The compiler emits one profile-local row for every affected profile.
`all_profiles_aggregate` is a deterministic projection over the complete local
row set and is never an independent input. Candidate A-only contracts cannot
produce Candidate C rows, and the converse applies, unless an accepted common
contract explicitly connects them.

### Ripple sparsity and partitioning

For equation/contract and parent-object mutations, the compiler precomputes
only admitted typed mutations whose targets have a propagation-bearing path to
an accepted or historical claim, negative boundary, blocked overread, route, or
transformed debt. An annotation-only or otherwise non-load-bearing existing
surface returns `no_propagation_bearing_effect` and does not create a ripple
row. Gate/candidate-disposition mutations use the separate source-recorded
reopening-boundary rule and remain eligible when the reopened gate has accepted
descendants, even if the proposed disposition has no existing claim path.

Authoritative profile-local rows are never truncated. If the bundle becomes
large, rows are partitioned into deterministically named shards with a
canonical index and aggregate projection. Sharding may change delivery, not
scientific coverage. Each shard records target range, profile coverage, row
count, payload digest, and source-bundle identity.

## Dependency Reach, Not Importance Score

The UI may report direct and transitive dependent counts for debts, objects,
and contracts. It must call these `dependency_reach`, not load, importance,
severity, or scientific priority. Propagation counts must distinguish required,
one-of, conditional, and negative-boundary relationships. Annotation/display
reach is reported separately and never added to propagation reach.

Historical `must_close_before_D10` status may be displayed as predecessor
metadata. Current D10 debt transformations and verification obligations must
remain separate. A transformed debt does not glow as an unresolved pre-D10
blocker merely because it once carried that role.

## Scenario Contract

The shared scenario format should contain:

```json
{
  "schema_version": "grcv4_exploratory_scenario_v1",
  "kernel_schema_version": "...",
  "source_bundle_digest": "...",
  "baseline_record_id": "...",
  "baseline_record_digest": "...",
  "profile_id": "...",
  "mutations": [],
  "result_class": "speculative_structural_counterfactual"
}
```

Scenarios are immutable mutation descriptions, not arbitrary graph-state
patches. Unknown fields, stale source identities, missing scopes, or mutations
outside the admitted algebra fail closed. Notebook-to-web and web-to-notebook
round trips must be canonical and lossless.

The browser cannot author a mutation or recompute a ripple. The round trip is:

```text
load canonical scenario
  -> select its precomputed ripple row
  -> play back that row
  -> serialize the selected row as the same canonical scenario
```

Web-to-notebook export is read-back of a selected precomputed row, not an
edit-and-reserialize workflow. The resulting scenario bytes must equal the
original canonical scenario bytes.

## Web Surface

Use Cytoscape.js for focused graph rendering. Build the actual exploration
surface, not a landing page.

### Required views

1. **Focused navigator:** search or select one object and render a bounded
   neighborhood, never the unfiltered full graph.
2. **Family navigation:** enter through D10.2's nine
   `coverage_contract.required_families` and filter to that family's claims,
   objects, contracts, and source-recorded edges.
3. **Triangulation:** show node-family-specific lenses rather than one generic
   panel for every selection.
4. **Dependency reach:** direct/transitive dependent counts by relation class.
5. **Claim ceiling:** locked negative/blocked relabel surfaces with exact source
   reason and reopening boundary.
6. **Alternative layer:** display routed, rejected, conditional, and historical
   nodes without presenting them as accepted peers.
7. **Lineage scrubber:** traverse accepted record identities along the DAG
   projection and preserve corrections/branches.
8. **Ripple view:** animate only a precomputed row and mark the evidence
   frontier explicitly.

### Family navigation

The primary coarse-grained entry points come directly from D10.2:

```text
core_resource = 7
legacy_transport = 9
candidate_A = 7
candidate_C = 5
geometry = 8
realization = 5
complete_step_lifecycle = 12
GRC9_specialization = 7
specification_grammar = 7
```

These values validate object-family coverage only. They do not rank families
and do not define profile propagation. Triangulation refines a selected family
into source-exact node relationships.

### Family-specific triangulation

The visible lenses depend on the selected node family:

- **Claim:** supporting objects, instantiating contracts, accepting or
  transforming gates, and debts transformed by the claim.
- **Debt transformation:** claims blocked historically, accepted
  transformation, closing/routing gate, and forward verification obligations.
- **Gate:** added, inherited, narrowed, routed, superseded, and
  resolved-negative content; predecessor identity; successor branches.
- **Profile:** active charge, lifecycle, event, candidate, realization, and
  disabled-reduction contracts.
- **Object/equation contract:** accepted claims, profile/candidate/realization
  scopes, blocked overreads, and parent/child relation.
- **Source record:** digest, acceptance status, predecessor identity, and
  supersession edges.

Unsupported lenses are omitted rather than filled with inferred relations.

### Claim ceiling and lock reasons

Blocked overreads use exact source fields as their lock reasons. In particular,
the claim-ceiling view admits the complete D10.2
`targeted_type_and_provenance_hardening` map:

```text
core_K_vs_graph_K4
M4_ontology
Candidate_A_profile_scope
Candidate_A_future_curvature_rule
migration_split
reference_Hodge_embedding
differential_backend_scope
destination_semantics
```

The machine value and source record are always shown. A human-readable
paraphrase may accompany them only as a non-authoritative annotation. Generic
reasons such as `needs_evidence` or `contradicts_record` are permitted only when
no more specific source statement exists; the UI may not invent a lock reason.
Each compiled lock surface therefore carries `blocked_overread_id`,
`lock_reason_source_key`, `lock_reason_machine_value`, `source_record_id`, and
`source_record_digest`; missing required provenance fails the lock compilation.

### Progressive ghost layer

The alternatives slider controls visibility and opacity only. At zero, only
accepted nodes render. Increasing it progressively materializes rejected
candidates, blocked relabels, conditional alternatives, and historical claims.
Ghost nodes retain dashed/non-color-only distinction at every level and can
never become accepted through selection, dragging, filtering, or playback.
The slider cannot alter propagation, classification, or scenario output.

### Fork-in-time playback

The lineage scrubber can freeze at an accepted record and play a precomputed
mutation from that point. The accepted unaffected subtree remains solid; the
minimal invalidation roots and evidence frontier are labeled; descendants
beyond the frontier fade to an unresolved dashed state. The animation shows a
structural fork without predicting the rerun branch and contains no browser-side
propagation logic.

### Cross-surface identity

For an identical source bundle and selection, the forensic API projection and
the browser bundle payload must be byte-identical for node IDs, edge rows,
support classifications, scopes, and selected ripple row. This integration
assertion enforces one kernel/two front ends and fails if JavaScript or notebook
presentation introduces a divergent scientific projection.

### Interaction and accessibility

- Stable dimensions must prevent graph and control layout shifts.
- Use icons and tooltips for graph operations, tabs for views, and segmented
  controls for source versus speculative mode.
- Keyboard selection, focus visibility, text alternatives, reduced-motion
  behavior, and responsive desktop/mobile layouts are required.
- Speculative state must remain visibly distinct without relying on color alone.
- Long IDs and claims must wrap or use expandable detail panels without
  overlapping graph controls.

## User Scenario Acceptance Contract

The implementation-facing UX contract is
[GRCV4ExploratorySideToolUserScenarios.md](./GRCV4ExploratorySideToolUserScenarios.md).
It records 35 normalized scenarios across forensic reconstruction, static
navigation, structural counterfactuals, fail-closed pressure, and onboarding.
The scenario record is derived design guidance, not scientific authority.

Every scenario has one owning iteration and may name supporting iterations. A
gate cannot close until its owned scenarios have executable acceptance evidence
or an explicit fail-closed disposition. Iteration 9 reruns the complete suite
and reconciles its coverage matrix. Scenario text cannot widen the mutation
algebra, source authority, or maximum claim defined by this plan.

## Proposed Investigation-Local Layout

All implementation remains under this investigation:

```text
implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/
  README.md
  GRCV4ExploratorySideToolImplementationPlan.md
  GRCV4ExploratorySideToolImplementationChecklist.md
  tool/
    pyproject.toml
    toolchain.toml
    <committed Python lockfile>
    src/grcv4_explorer/
      adapters/
      kernel/
      forensic/
      scenarios/
      ripple/
    tests/
    notebooks/
    web/
      package.json
      <committed frontend lockfile>
    scripts/
      bootstrap.py
      doctor.py
      run.py
    generated/
```

Iteration 0 selected npm/package-lock for the future frontend scaffold and a
hash-pinned, repository-compatible Python lock for future additions. Both locks
are empty at this gate because no third-party side-tool dependency is needed by
the setup/source-contract surface. An owning later iteration must explicitly
admit and lock a package before using it. Generated scratch output is ignored;
selected committed examples require explicit provenance and reconstruction
commands.

### Portability and reproducibility

The tool distinguishes three contracts:

```text
portable compatibility
  minimum Python/browser versions
  minimum Node/package-manager versions only for rebuilding the web bundle
  tested version ranges
  platform-neutral repository-root discovery and relative paths
  no global or user-site package installation

reproducible build
  committed dependency lockfiles
  frozen lockfile format and canonical builder metadata
  deterministic serializer and generated-artifact digests
  repository-root Python environment
  tool-local Node runtime, dependency trees, caches, and browser binaries

scientific/source identity
  accepted source IDs, record digests, file SHAs, schema versions,
  and canonical derived payloads
```

The current host OS, username, repository location, virtual-environment path,
Python patch version, and Node patch version are diagnostic metadata, not source
or scenario identity. A supported environment must not fail because it differs
from the machine that generated the committed example.

Python packaging uses `requires-python` with a minimum version and adds an upper
bound only for a known incompatibility. Node and its package manager are build
dependencies for the static browser bundle, not requirements for consuming a
prebuilt bundle. Lockfiles may pin direct and transitive package versions for a
reproducible build without narrowing the supported interpreter or OS to one
machine.

### Repository-local installation boundary

Python uses the repository's existing environment boundary; all other installed
or downloaded state stays below the `tool/` package:

```text
<repository>/.venv/          shared repository Python environment and packages
tool/.tooling/node/          downloaded Node runtime
tool/.tooling/corepack/      package-manager bootstrap state
tool/.tooling/playwright/    browser binaries
tool/web/node_modules/       frontend dependencies
tool/.cache/                 pip/npm/package-manager/notebook caches
tool/generated/              derived graph, ripple, and report output
tool/web/dist/               generated static browser bundle
```

The host may supply a compatible shell and bootstrap Python executable, but
setup may not install or modify global packages, user-site packages, global
Node/npm state, or home-directory caches. Bootstrap creates the repository-root
`.venv` when absent or validates it when present; it does not download a second
Python runtime or create a tool-specific Python environment. Tool Python
dependencies are resolved against the repository environment and may not
silently upgrade, downgrade, or replace incompatible repository packages. A
dependency conflict fails with an actionable diagnostic. Downloaded Node stays
under `tool/.tooling/`. Wrapper scripts set cache and runtime environment
variables (`PIP_CACHE_DIR`, npm/package-manager cache, `COREPACK_HOME`, and
`PLAYWRIGHT_BROWSERS_PATH`) to tool-local paths.

Global runtimes are not valid tool executors. A compatible host Python may only
enter the bootstrap script when `.venv` does not yet exist; its sole permitted
actions are creating `.venv` and re-executing the same bootstrap under that
environment. All setup work after that point, plus every build, audit, test,
notebook, report, and serving command, runs under repository `.venv`. Global
Node/npm have no exception: bootstrap and wrappers invoke only the
checksum-pinned Node and bundled npm below `tool/.tooling/`.

The repository `.gitignore` already covers `/.venv/`. The investigation-local
`.gitignore` is committed before setup runs and covers the Node runtime,
dependency trees, caches, browser binaries, test reports, and generated build
directories. Manifests, lockfiles, source, configuration, and bootstrap scripts
remain tracked. Iteration 0 verifies representative paths with
`git check-ignore` and verifies setup leaves no install artifact visible in
`git status --short`.

### Reproducible setup interface

A clean checkout uses one documented bootstrap command:

```text
python tool/scripts/bootstrap.py
```

This is the only command allowed to begin under compatible host Python when the
repository `.venv` is absent. It immediately creates and re-enters `.venv` before
performing setup. When `.venv` already exists, the preferred invocation is
`.venv/bin/python tool/scripts/bootstrap.py` (or the platform-equivalent
environment executable). The script is idempotent and performs these steps
without global installation:

1. discover repository and tool roots from its own location;
2. validate the bootstrap compatibility floor;
3. create or validate the repository-root `.venv`;
4. verify that the committed tool dependency set is compatible with the
   repository environment, then install missing locked dependencies without
   implicit package replacement or upgrades;
5. download and checksum the selected portable Node runtime into
   `tool/.tooling/node/` when web rebuilding is requested;
6. provision package-manager state, frontend dependencies, and Playwright
   browsers into ignored tool-local paths;
7. write an ignored diagnostic environment receipt;
8. run a fast doctor check and print exact commands for tests, notebook launch,
   web build, and static serving.

Committed `toolchain.toml` records Python compatibility floors, the canonical
managed Node release and checksums used by the reproducible builder, lockfile
identities, and supported platform/architecture rows. The canonical Node
version is a reproducible setup choice, not the only compatible host version.
Every downloaded runtime or installer is checksum-verified before use.

`tool/scripts/doctor.py` verifies that Python resolves from the repository
`.venv`, that no package resolves from the global or user site, and that local
paths, supported versions, lockfile/runtime identities, source-bundle
readability, and writable derived directories are valid. Wrapper commands set
all required environment variables; users do not manually export cache or
runtime paths.

Bootstrap must be safe to rerun, must not silently upgrade locks or managed
runtimes, and must fail with an actionable message when a supported artifact is
unavailable. A missing `.venv` is first built and verified under a temporary
repository-local name, then atomically renamed; a pre-existing incomplete
environment fails closed rather than being repaired implicitly. A clean-checkout
test runs setup from a different temporary repository path and confirms the same
admitted dependency/runtime identities and deterministic smoke-test output. An
optional offline path may consume a prepopulated checksum-verified local cache;
otherwise the first-run network requirement must be stated clearly.

All path handling uses repository-root discovery and structured path APIs. No
generated artifact may contain a machine-local absolute path. Where CI capacity
permits, conformance runs on the minimum supported version and at least one
later supported version; exact host-version equality is never an admission
gate.

## Architectural Tradeoffs Carried Forward

Iteration 0 chooses one validated semantic kernel for both front ends. This
trades implementation redundancy for cross-surface consistency: a kernel error
could affect notebook and web output identically. Iteration 2 therefore requires
an independent source-conformance auditor that derives populations, identifiers,
reference coverage, and reciprocal relations directly from accepted source
records without calling kernel APIs.

Iteration 1 applies the same discipline before graph construction. The builder
and independent auditor separately derive canonical relationship-witness sets
for claim/debt edges, claim and debt evidence, debt claim and verification
targets, predecessor lineage, lifecycle cells, D9 obligation carry-forward,
equation-contract references, coverage, and authorization classes. Acceptance
requires exact per-family counts and digests plus one exact population digest;
aggregate population agreement is insufficient. Adversarial fixtures must also
prove that every relationship family fails closed when its target, reciprocal
edge, carry-forward, coverage, or partition is damaged. Exact agreement does not
turn the two implementations into independent scientific authorities or rule
out a shared conceptual mistake in the admitted source contract.

The D10.2 equation/contract registry is accepted source material, but its 152
rows are human-authored. Its row count alone is not a coverage proof. Iterations
1 and 2 must verify that referenced claims, parent objects, profiles, contracts,
and propagation relations resolve and that no source-recorded claim-to-contract
relationship required by the tool is silently omitted.

Generated graph and ripple tables are source-bundle products, not adaptive
runtime knowledge. Any newly accepted or changed source record requires adapter
readmission, a new source-bundle identity, a complete deterministic rebuild, and
re-audit before either front end may consume it.

Iteration 0 proves deterministic behavior on Python 3.12.3 only. The declared
3.11-3.13 support range remains a closeout obligation: canonical fixtures must
be rebuilt on admitted supported versions and compared byte-for-byte, or the
tested compatibility range must be narrowed honestly before acceptance.

## Iteration Sequence

### Iteration 0. Baseline, Layout, And Source Contract Freeze

Freeze minimum compatibility requirements, tested ranges, lockfile/reproducible
builder policy, investigation-local layout, source files, accepted digests,
output policy, repository-local installation/gitignore boundary, portability rules,
and exact non-authority language. Do not bind the tool to the current host's
Python, Node, OS, username, or repository path. No kernel logic or UI is written
before this gate closes.

### Iteration 1. Source Adapters And Bundle Identity

Implement schema-specific read-only adapters, canonical digest validation,
reference checks, source-bundle identity, source-evolution discovery,
stale-source failure, before/after immutability verification, and independently
derived exact relationship-witness equivalence.

### Iteration 2. Validated Graph Kernel

Build typed nodes/edges, lineage DAG, support semantics, invariant checks, and
deterministic serialization. Keep propagation and annotation edges physically
disjoint, and route verification obligations forward only. Reproduce accepted
counts and reciprocal-edge rules without creating a new authority.

The accepted implementation reconstructs 436 typed nodes, 2,666 propagation
edges, and four physically separate annotation edges from the exact ET-C1
bundle. The source-owned populations are 39 current claims, 29 historical
claims, 29 debt transformations, 11 shared verification obligations, 67 parent
objects, and 152 equation-contracts. It preserves 33 accepted gate records,
four candidate rows, ten profiles, 20 realization/comparison rows, and 38
physical source identities.

Support classification is conservative. Explicit conditions and negative
transformations retain `conditional` and `negative_boundary`; verification
obligations are `required` forward work. Contract/object and other support
relations whose conjunction/disjunction logic is not stated remain
`indeterminate_requires_review`. No `one_of` relation is inferred merely from
multiple incoming edges. Lineage, scope, identity, and non-support
transformation relations are typed `not_applicable` for support evaluation
rather than being promoted into evidence.

The independent ET-C2 auditor does not import the kernel. It rebuilds the full
node and relationship witness from raw admitted JSON and compares every one of
the 436 nodes and 2,670 total relationships, including annotations, exactly.
The focused fixture matrix contains 14 fail-closed mutations, including a
count-preserving claim/debt relation substitution and a missing
contract-to-claim edge. ET-C2 is accepted at this validated-graph ceiling, and
Iteration 3 is authorized without extending ET-C2's scientific authority.

### Iteration 3. Forensic API And Notebook Recipes

Implement pure forensic functions, stable reports, negative-claim tracing,
candidate careers, object/contract provenance, and a minimal notebook that
only orchestrates those APIs.

The accepted implementation uses a two-part accepted context: ET-C2 owns typed
relationship semantics, while the ET-C1-admitted source documents own exact
gate, candidate, debt, object, and contract payloads. Every emitted row binds
both surfaces through a source record/digest/JSON pointer and exact graph-edge
references. The independent auditor checks 101 rows and 1,205 edge references
without importing the forensic implementation. The notebook executes two
orchestration-only recipes and hashes all non-generated tool files before and
after execution. Its three accepted residual boundaries record the intentionally
lighter I3 fixture matrix, the accepted ET-C2 chained-trust root, and the one
source-bounded Candidate A hardening projection. Counterfactual and browser
work remain closed; Iteration 4 is authorized but not implemented.

### Iteration 4. Counterfactual Mutation And Evidence Frontier

Freeze typed mutations and implement conservative invalidation, debt
reactivation, negative activation, route changes, earliest-gate reopening, and
unknown-frontier behavior. Compute the frontier from minimal invalidation roots,
complete support predicates, and independent-support subtraction. Detect
blocked-overread risk without activating the blocked claim. Distinguish
existing-surface sparsity from gate/candidate-disposition reopening so routed
alternatives remain testable without fabricated equations. No new positive
downstream claims are generated.

The candidate implementation freezes nine typed mutations over four target
kinds. Every mutation binds an accepted baseline record and digest plus exact
profile, candidate, realization, and structural payload scopes. Invalid or
stale inputs fail closed before graph evaluation. Profile ownership is derived
through accepted profile-to-candidate edges, and realization ownership must
agree with the declared candidate scope.

The kernel keeps two operations distinct. Existing equation/contract and
parent-object mutations follow only accepted propagation-bearing paths. A
gate/candidate disposition mutation instead opens a source-recorded gate
boundary and marks accepted descendants unknown without inventing the rerun's
result. Candidate B therefore reopens at D7-v2, names the missing `U_B` writer
and reopening condition, preserves independently grounded Candidate-C-only
claims, and produces no B-specific D7G-D10 claim. V4-D remains an
uninstantiated slot and can reopen only through the source-recorded D0-successor
route.

Current accepted edges provide no exact one-of support row, exact conditional
debt-closing precondition, or exact negative-activation path. The candidate
therefore emits zero such source results and pressure-tests their fail-closed
support behavior with synthetic fixtures. It does not infer them from multiple
incoming edges, historical `must_close_before_D10` metadata, or blocked
overreads. A neutralized provenance lock reports only the blocked overread at
risk. Numerical effects, positive reopened-gate outcomes, and fabricated
successor claims remain prohibited.

The accepted 13-scenario matrix covers C1-C7 and D2-D6, including separate Candidate B
and V4-D D5 cases. Its independent auditor does not import the counterfactual
implementation and verifies result/mutation digests, raw source pointers,
source digests, and 169 exact ET-C2 edge references. Two builds are
byte-identical; 1,775 independent audit checks and 38 focused/adversarial checks
pass; the accepted ET-C3 verification suite also passes unchanged. ET-C4 is
accepted at the bounded structural-counterfactual ceiling, and Iteration 5 is
authorized without being implemented by this gate.

### Iteration 5. Ripple Compiler And Scenario Round Trip

Emit deterministic profile-qualified ripple tables, validate canonical
scenarios, compile only propagation-bearing targets, shard without truncating
scientific coverage where needed, and prove load/serialize/select/playback
scenario round-trip identity.

The accepted implementation freezes one scenario schema, one ET-C4 kernel
schema binding, a profile-local ripple schema, deterministic shard/index
schemas, and a projection-only aggregate schema. C1-C7 expand into 25 canonical
scenarios and 24 ripple rows: C3 and C4 each cover all ten admitted profiles;
C2, C5, and C7 remain isolated to Candidate A and `A_CI`; C1 is explicitly
profile-independent; and the non-load-bearing C6 fixture serializes but emits
no ripple.

Every row carries a scope receipt derived from accepted profile IDs, the
profile's disabled-reduction identity, localized candidate/realization scope,
and the ET-C4 claim activation conditions consulted. D10.2 family-coverage
counts are explicitly excluded from propagation scope. Direct and transitive
consequences remain separate, every consequence has an exact ET-C2 source-edge
witness, blocked overreads remain risk-only, and verification obligations stay
in a forward-work-only channel outside claim/debt consequences.

The compiler writes three deterministic eight-row shards plus a canonical
index; sharding changes delivery only and preserves all 24 rows. A selected row
contains its immutable canonical scenario, and read-back reproduces the input
bytes exactly. Browser mutation authoring and browser-side propagation remain
absent. Two complete rebuilds are byte-identical; 4,133 independent checks, 89
focused/adversarial checks, and the complete accepted ET-C4 regression pass.
ET-C5 is accepted at the bounded static ripple/scenario compiler ceiling.
Iteration 6 is authorized but is not implemented by this gate.

### Iteration 6. Web Foundation, Triangulation, And Dependency Reach

Create the Cytoscape.js shell, focused navigation, source details,
family navigation, node-specific triangulation, dependency reach, responsive
layout, and accessibility baseline. The client loads generated tables only and
must match the forensic projection byte-for-byte for identical selections.

**Implementation result (accepted).** Python now compiles
one canonical static bundle containing the admitted ET-C1 source manifest,
ET-C2 graph projection, ET-C5 scenarios/ripples, 436 bounded selection
projections, and the exact nine-family D10.2 coverage surface. The client only
verifies, dereferences, searches, filters, lays out, and presents these compiled
rows. It contains no mutation evaluator, propagation traversal, or ripple
compiler.

Each selection is capped at 32 nodes and 72 relationships. Family coverage is
explicitly not profile scope or scientific ranking. Dependency reach is split
by source support semantics and labeled as dependency count rather than
importance. Claim, debt, gate, profile, object/contract, and source records use
family-specific lenses; unsupported lenses are absent. Current, historical
with new unprocessed source, stale, and observation-blocked states are distinct,
while the standalone browser is labeled as a build-time snapshot.

The responsive Cytoscape workbench passes desktop and mobile Playwright flows,
including long-identifier containment and source/speculative mode separation.
The Python/JavaScript projection parity set is byte-identical for seven
representative node families. Two rebuilds are byte-identical; the independent
audit passes 44,895 checks, focused Python tests pass 47 checks, all eight Node
component tests pass, and the complete ET-C5 verification remains green. The
accepted bundle digest is
`45a96e782a1ecdd5fb693e171052a020bfdbffa76d21ca07e0a307b9cc96684c`;
the accepted gate digest is
`6353caaf1cb67b4228bfd9d74a4898a72a8ba886dcb84b55757d019b0d1c3629`.
Iteration 7 is authorized but is not implemented by this gate.

### Iteration 7. Claim Ceilings And Alternative Layer

**Status:** authorized; not implemented

Add locked-claim navigation, blocked overreads, routed/rejected/historical
alternatives, source-exact hardening reasons, progressive ghost
materialization, and precise V4-D representation.

### Iteration 8. Lineage Scrubbing And Precomputed Ripple Playback

Add DAG-aware time navigation, source/speculative mode separation, scenario
loading, and precomputed ripple animation with explicit evidence-frontier
markers. Include a fork-in-time view that leaves accepted unaffected history
solid and fades only the unresolved counterfactual descendants.

### Iteration 9. Independent Validation And Closeout

Run deterministic rebuilds, source-immutability checks, negative/adversarial
scenario tests, browser tests, Playwright desktop/mobile screenshots, usability
pressure, documentation review, and final claim classification.

## Verification Strategy

### Kernel and adapter tests

- accepted source count and digest fixtures;
- schema-specific digest-field selection;
- 39/29/29/11/67/152 accepted-bundle counts;
- reciprocal claim/debt edges;
- no silent debt loss;
- unresolved reference and duplicate-ID failures;
- lineage acyclicity and predecessor digest checks;
- physically disjoint propagation and annotation tables;
- one node per unique verification-obligation ID with source-occurrence tags;
- forward-only verification-obligation edges;
- annotation non-authority;
- source before/after byte identity;
- deterministic graph serialization.

### Counterfactual tests

- required-support removal invalidates the expected claim;
- one-of support does not fail from one removal when alternatives are explicit;
- unclear support returns `indeterminate_requires_review`;
- frontier roots form the minimal invalidation antichain;
- independently supported descendants remain outside the frontier;
- claim predicates use accepted evidence references, transformed debt
  dispositions, and source-recorded activation conditions;
- exact debt reactivation requires a recorded conditional closing;
- reopened gates yield `unknown_beyond_evidence_frontier` downstream;
- routed gate/candidate-disposition mutations open a source-recorded reopening
  boundary rather than failing existing-path sparsity;
- profile-local propagation does not cross candidate/profile scope;
- a neutralized lock reason flags overread risk without activating the overread;
- Candidate B and V4-D controls do not fabricate successor claims;
- profile-local mutations do not leak into unrelated profiles;
- stale or malformed scenarios fail closed;
- no numeric effect appears in structural output.

### Web tests

- browser bundle contains no propagation rules;
- focused subgraph limits prevent full-graph sprawl;
- family counts and family filters reproduce D10.2 source coverage;
- node-family-specific triangulation omits unsupported lenses;
- source/speculative modes remain visually and semantically distinct;
- progressive ghost visibility never changes source classification;
- long labels and IDs remain readable;
- keyboard and reduced-motion behavior works;
- scenario playback reproduces the selected precomputed row exactly;
- fork playback preserves unaffected accepted branches and fades only the
  precomputed unresolved frontier;
- browser payload equals the forensic projection for identical selections;
- Playwright screenshots pass on desktop and mobile viewports.

## Completion Boundary

Successful closeout may claim:

> A deterministic read-only exploratory tool reconstructs the accepted
> GRCv4/GRC9v4 constitutive-design claim topology and supports bounded,
> source-traceable structural counterfactual navigation up to the explicit
> evidence frontier.

It may not claim that the tool proves a new V4 result, predicts reopened-gate
outcomes, implements GRCv4, or authorizes specification/runtime changes.
