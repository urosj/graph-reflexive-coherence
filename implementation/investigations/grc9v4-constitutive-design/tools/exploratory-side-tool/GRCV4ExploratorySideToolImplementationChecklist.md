# GRCv4 Exploratory Side Tool Implementation Checklist

**Date:** 2026-08-28
**Status:** Iteration 0 accepted; Iteration 1 authorized
**Plan:** [GRCV4ExploratorySideToolImplementationPlan.md](./GRCV4ExploratorySideToolImplementationPlan.md)
**Source investigation:** [GRC9V4 constitutive design](../../README.md)

## Usage Rules

- [x] Keep the tool under `implementation/investigations/`.
- [x] Treat accepted `decisions/*.json` records as immutable source authority.
- [x] Keep the 67 parent objects distinct from the 152 equation/contract rows.
- [x] Preserve 39 current claims, 29 historical claims, 29 transformed debts,
      and 11 verification obligations as distinct source-owned populations.
- [x] Treat V4-D as a rejected uninstantiated admission slot, not a complete
      fourth architecture.
- [x] Model gate history as a DAG with successor branches and corrections.
- [x] Keep browser behavior to rendering, search, filtering, and playback of
      precomputed tables.
- [x] Keep propagation and annotation edges in physically disjoint tables.
- [x] Treat verification obligations as forward work, never backward evidence.
- [x] Stop counterfactual propagation at the evidence frontier.
- [x] Never generate a positive result for a gate that has not been rerun.
- [x] Label forensic reconstruction and speculative counterfactual output
      separately.
- [x] Keep `src/`, `specs/`, accepted decision records, and repository tests
      outside the tool's write envelope.
- [x] Require source-bundle and scenario identities on every derived artifact.
- [x] Use `dependency_reach`, not an unsupported importance score.
- [x] Run every tool command under repository `.venv`; permit host Python only
      to create and immediately re-enter `.venv` during clean bootstrap.
- [x] Never invoke global Node or npm; use only the checksum-pinned tool-local
      runtime and its bundled package manager.
- [x] Do not begin Iteration 1 until Iteration 0 is reviewed and accepted.

## Current Status

```text
branch = investigation-GRCV4-exploratory-side-tool
plan = frozen
checklist = iteration_0_recorded
tool_code = iteration_0_setup_and_audit_only
accepted_source_records_changed = false
src_pygrc_changed = false
specifications_changed = false
scientific_claims_added = false
implementation_gate = ET-C0_accepted_I1_authorized
```

## Iteration 0. Baseline, Layout, And Source Contract Freeze

**Status:** accepted

### Goal

Freeze the portable compatibility, reproducible-build, source, and write
envelopes before introducing dependencies or code.

### Checks

- [x] Record branch, HEAD, and `git status --short`.
- [x] Record the exact accepted source-record list and expected statuses.
- [x] Record each source record's canonical digest field and file SHA policy.
- [x] Verify the accepted D10 topology audit passes unchanged.
- [x] Verify the accepted D10.1 audit passes unchanged.
- [x] Verify the accepted D10.2 audit passes unchanged.
- [x] Derive current source-bundle counts from authoritative arrays and match
      them against separate admission assertions: 39 current claims, 29
      historical claims, 29 transformed debts, 11 verification obligations,
      67 parent objects, and 152 equation/contracts.
- [x] Preserve the four D9 post-spec verification-obligation occurrences as
      predecessor lineage into the current 11-obligation D10 population rather
      than duplicating them as accepted evidence.
- [x] Freeze the lineage records required from D0 through D10.2, including all
      v2, correction, realization-family, comparison, hybrid, and provenance
      successors.
- [x] Inspect existing Python, notebook, Node, browser-test, and documentation
      dependencies before selecting new ones.
- [x] Declare the minimum supported Python version and a tested compatibility
      range; add an upper bound only for a known incompatibility.
- [x] Declare minimum Node and package-manager requirements only for rebuilding
      the static web bundle; keep prebuilt-bundle consumption independent of
      Node.
- [x] Select the package-manager family and lockfile format, and pin direct and
      transitive dependencies for reproducible builds without binding support
      to one host OS or patch version.
- [x] Add and verify the investigation-local `.gitignore` before any dependency
      or runtime installation; include it in the accepted Iteration 0 commit.
- [x] Use the ignored repository-root `.venv` for Python; do not create a second
      tool-specific environment or install global/user-site Python packages.
- [x] Resolve the committed tool dependency set against the repository
      environment; fail on conflicts rather than silently upgrading,
      downgrading, or replacing repository packages.
- [x] Freeze `tool/.tooling/` roots for managed Node, Corepack state, and future
      Playwright browsers; place the currently admitted Node runtime there and
      forbid global Node/npm installation.
- [x] Place frontend dependencies under `tool/web/node_modules/` and all package
      manager, notebook, and test caches under `tool/.cache/` or another
      explicitly ignored tool-local path.
- [x] Configure setup wrappers so pip, npm/package-manager, Corepack, and
      Playwright cannot write installation/cache state into the user's home
      directory.
- [x] Make every non-bootstrap Python entry point fail closed outside the
      repository `.venv`.
- [x] Verify bootstrap re-enters `.venv` before dependency, audit, doctor, or
      managed-runtime work begins.
- [x] Verify no command resolves global Node/npm even when incompatible global
      installations are present on the host.
- [x] Keep manifests, lockfiles, source, configuration, and setup scripts
      tracked while ignoring installed and generated state.
- [x] Verify representative local install paths with `git check-ignore`.
- [x] Run the setup procedure and verify `git status --short` exposes no
      installed runtime, dependency, browser, cache, or generated-build file.
- [x] Record the current builder environment as diagnostic metadata only, not
      source-bundle, scenario, or scientific identity.
- [x] Require repository-root discovery, structured path APIs, and
      repository-relative artifact paths; reject machine-local absolute paths.
- [x] Plan conformance on the minimum supported version and at least one later
      supported version where CI capacity permits.
- [x] Freeze one documented clean-checkout command:
      `python tool/scripts/bootstrap.py`.
- [x] Require bootstrap to discover roots from its own file location rather
      than the caller's working directory or an absolute path.
- [x] Add committed `toolchain.toml` metadata for Python compatibility floors,
      the canonical managed Node release/checksums, lockfile identities, and
      supported platform/architecture rows.
- [x] Require checksum verification for every downloaded runtime or installer.
- [x] Make bootstrap idempotent and prohibit implicit lockfile, dependency, or
      managed-runtime upgrades.
- [x] Make an incomplete pre-existing `.venv` fail closed and create a missing
      `.venv` through a verified temporary environment plus atomic rename.
- [x] Add `doctor.py` checks for local paths, versions, locks, runtime identity,
      source readability, derived-directory writes, and global/user-site
      contamination.
- [x] Make wrapper commands set cache, runtime, and browser paths so setup
      requires no manual environment-variable exports.
- [x] Print exact post-bootstrap commands for admitted setup/audit surfaces and
      explicit owning-iteration blockers for notebooks, web build, and static
      serving that do not exist yet.
- [x] Test setup from a clean checkout at a different temporary repository path.
- [x] Rerun bootstrap and prove it is a no-op when the admitted environment is
      already present.
- [x] Document an optional checksum-verified offline-cache path if supported;
      otherwise state the first-run network requirement clearly.
- [x] Freeze the investigation-local tool layout.
- [x] Freeze generated scratch and selected committed artifact policies.
- [x] Freeze the 35-scenario UX acceptance record and assign each scenario to
      one owning iteration.
- [x] Freeze one canonical serializer for every derived artifact: UTF-8,
      sorted keys and unordered collections, fixed separators, no NaN, and a
      finite-number formatting policy.
- [x] Freeze the read-only source rule and before/after hash check.
- [x] Freeze `forensic_evidence_trace` and
      `speculative_structural_counterfactual` output classes.
- [x] Freeze the non-claims for runtime, specification, evidence, and reopened
      gate prediction.
- [x] Define the Iteration 0 baseline record and deterministic digest.
- [x] Run Ruff formatting/lint and strict mypy over every Iteration 0 script.
- [x] Run `git diff --check`.

### Gate

- [x] Accept `ET-C0_source_and_layout_contract_frozen`.
- [x] Keep Iteration 1 closed if any source identity or write boundary is
      ambiguous.
- [x] Keep Iteration 1 closed if the setup requires the author's exact Python,
      Node, OS, username, virtual-environment path, or repository location.
- [x] Keep Iteration 1 closed if Python is installed outside the repository
      `.venv`, non-Python installed state escapes the tool directory, or setup
      requires a global/user-site package installation.
- [x] Keep Iteration 1 closed if any tool action other than clean-checkout venv
      creation executes under host Python, or if global Node/npm is invoked.

### Result

```text
branch = investigation-GRCV4-exploratory-side-tool
start_HEAD = a0de777c28c3d5c1a56238e6ebfbac53eafc8a3f
record = records/ETC0SourceAndLayoutContract.json
record_status = accepted
record_digest = 2cd1b8c313ee86dba807d4f57e7db7eae3c8596fed457fabfa1bdc0ec4ab1028
source_record_count = 33
source_bundle_candidate_digest = 878aa1a0ebe2f6d00ecb263b0878bd9d0717818ff9a622249a99abc5cb95f065
accepted_source_bytes_unchanged = true
source_population_counts_derived_independently = true
accepted_D10_topology_audit = 1606_of_1606_passed
accepted_D10_1_audit = 113_of_113_passed
accepted_D10_2_audit = 289_of_289_passed
ET_C0_audit = 204_of_204_passed
ruff = passed
strict_mypy = passed
python_environment = repository_root_.venv
python_iteration_0_tested = 3.12.3
non_bootstrap_global_python_rejected = true
managed_node = 22.23.2_tool_local_checksum_verified
managed_npm = 10.9.8_tool_local
global_node_12_and_npm_6_consumed = false
bootstrap_idempotence = passed
partial_venv_fail_closed = passed
record_byte_identity_on_rebuild = passed
managed_node_binary_identity_on_rerun = passed
installed_state_hidden_from_git_status = passed
relocated_clean_bootstrap = passed_twice
scenario_ownership = 35_unique_scenarios
iteration_1_authorized = true
```

Interpretation:

Iteration 0 freezes a portable setup and exact source contract without adding
source adapters or scientific interpretation. All 33 accepted machine records
retain exact canonical digests and file hashes. Population counts are derived
from the authoritative arrays by the builder and independently re-derived by
the auditor; expected counts remain separate admission assertions. The
repository `.venv` is the only Python execution environment after the
bootstrap-only host entry, and the obsolete host Node/npm pair is bypassed by
explicit managed-runtime paths.

## Iteration 1. Source Adapters And Bundle Identity

**Status:** authorized; not started

### Goal

Load every accepted source through schema-specific read-only adapters and emit
one deterministic source-bundle identity.

### Checks

- [ ] Implement adapters for D10 claim topology and historical claim nodes.
- [ ] Implement adapters for D10 debt transformations and verification
      obligations.
- [ ] Implement adapters for D10.2 parent objects and equation/contracts.
- [ ] Implement adapters for D9 debt, profile, lifecycle, and event records.
- [ ] Implement adapters for D0-D10.2 decision records and predecessor digests.
- [ ] Derive all admitted population counts directly from authoritative source
      arrays; keep expected counts as separate admission assertions rather than
      observed values.
- [ ] Resolve every source-recorded claim, parent-object, profile, equation, and
      contract reference needed for graph coverage; reject dangling or
      ambiguous references before graph construction.
- [ ] Select digest fields per schema rather than assuming one common field.
- [ ] Validate canonical payload digests exactly.
- [ ] Validate declared file SHAs and source identities where present.
- [ ] Reject missing, duplicate, stale, malformed, or non-accepted records.
- [ ] Record source hashes before and after load.
- [ ] Prove adapters do not write source files.
- [ ] Emit deterministic source-bundle manifest and digest.
- [ ] Rebuild twice and prove byte identity.
- [ ] Add negative fixtures for wrong digest, wrong SHA, missing reference,
      changed status, and unknown schema.
- [ ] Execute owned scenario D1.
- [ ] Run focused adapter tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C1_source_bundle_admitted`.
- [ ] Do not build the graph from partially admitted inputs.

## Iteration 2. Validated Graph Kernel

**Status:** blocked on Iteration 1

### Goal

Build the typed, deterministic, source-traceable graph without creating a
second scientific authority.

### Checks

- [ ] Add distinct node classes for current claims and historical claims.
- [ ] Add debt transformation and verification obligation nodes.
- [ ] Model each unique `obligation_id` as one forward-only node without
      double-counting shared D9/D10 IDs.
- [ ] Tag every `requires_verification_from` edge with originating gate ID,
      record ID/digest, and source JSON pointer; verify every shared ID's source
      occurrences remain recoverable.
- [ ] Add gate records and accepted predecessor/supersession edges.
- [ ] Add A/B/C candidate nodes and the precisely scoped V4-D slot.
- [ ] Add realization and ten-profile nodes.
- [ ] Add separate 67 parent-object and 152 equation/contract node layers.
- [ ] Add source-record nodes and provenance edges.
- [ ] Add annotation nodes with display-only authority.
- [ ] Store `propagation_edges` and `annotation_edges` in physically disjoint
      tables with no shared rows or convertible authority flag.
- [ ] Assert annotation-only input cannot contribute to reachability,
      invalidation, routing, or ripple output.
- [ ] Add verification-obligation edges only in the forward
      `requires_verification_from` direction.
- [ ] Verify backward reconstruction never treats a verification obligation as
      accepted support.
- [ ] Preserve accepted claim/debt relation types.
- [ ] Preserve transformation verbs rather than using generic production.
- [ ] Type propagation support relations as required, one-of, conditional, or
      negative where the source supports that distinction; keep display-only
      relations exclusively in `annotation_edges`.
- [ ] Return `indeterminate_requires_review` when support logic is not stated.
- [ ] Build the full gate lineage DAG, including corrections and branches.
- [ ] Validate current/historical claim disjointness.
- [ ] Validate reciprocal claim/debt relations.
- [ ] Validate no silent debt loss.
- [ ] Validate all references and unique IDs.
- [ ] Run an independent source-conformance audit that does not call kernel APIs
      and re-derives populations, IDs, reference coverage, reciprocal
      relations, and claim-to-contract coverage from accepted source records.
- [ ] Fail if the 152-row equation/contract count is correct but any required
      claim-to-contract relationship is missing, unresolved, or only asserted
      by a literal.
- [ ] Validate DAG acyclicity and predecessor digest consistency.
- [ ] Validate annotations cannot affect propagation.
- [ ] Emit deterministic canonical graph serialization.
- [ ] Serialize with sorted keys/collections, fixed separators, no NaN, and the
      Iteration 0 finite-number policy.
- [ ] Rebuild twice and prove byte identity.
- [ ] Execute owned scenario F9.
- [ ] Run focused kernel and invariant tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C2_validated_graph_kernel`.
- [ ] Block Iteration 3 if any propagation-bearing edge requires an
      unclassified hand-authored relation.

## Iteration 3. Forensic API And Notebook Recipes

**Status:** blocked on Iteration 2

### Goal

Expose source-exact reconstruction through pure Python functions before visual
or counterfactual work.

### Checks

- [ ] Implement `gate_act(record_id)`.
- [ ] Implement `debt_lifecycle(debt_id)`.
- [ ] Implement `reconstruction_path(claim_id)`.
- [ ] Implement `candidate_career(candidate_id)`.
- [ ] Implement `pruned_choices_at(record_id)`.
- [ ] Implement `negative_claims()`.
- [ ] Implement `object_dependents(object_id)`.
- [ ] Implement `contract_provenance(contract_id)`.
- [ ] Implement `gate_contribution(record_id)`.
- [ ] Ensure each row includes source record, digest, and exact edge references.
- [ ] Distinguish added, inherited, narrowed, routed, superseded, conditioned,
      and resolved-negative content.
- [ ] Add stable Markdown and JSON forensic reports.
- [ ] Add a minimal notebook that calls the pure functions without duplicating
      logic.
- [ ] Verify notebook execution writes only to the derived output envelope.
- [ ] Verify forensic output contains no speculative claims.
- [ ] Execute owned scenarios F1-F8 and E3-E4.
- [ ] Rebuild representative reports twice and prove byte identity.
- [ ] Run focused forensic and notebook tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C3_forensic_reconstruction_surface`.
- [ ] Keep counterfactual and browser claims closed.

## Iteration 4. Counterfactual Mutation And Evidence Frontier

**Status:** blocked on Iteration 3

### Goal

Support conservative structural counterfactuals without pretending to rerun
the investigation.

### Checks

- [ ] Freeze typed mutation IDs and schemas.
- [ ] Require target kind, baseline record/digest, profile, candidate,
      realization, and declared payload scopes.
- [ ] Admit `equation_contract`, `normative_object`, `gate_record`, and
      `candidate` target kinds with type-specific validation.
- [ ] Apply existing-path sparsity to equation/contract and parent-object
      mutations; return `no_propagation_bearing_effect` when no
      propagation-bearing path exists.
- [ ] For gate/candidate-disposition mutations, open a source-recorded reopening
      boundary and propagate over accepted descendants of the reopened gate
      without requiring an existing path from the proposed disposition.
- [ ] Implement required-support invalidation.
- [ ] Implement explicit one-of support behavior.
- [ ] Implement conditional activation only from source-recorded conditions.
- [ ] Implement exact debt reactivation only when a recorded conditional
      closing names a precondition that the mutation falsifies.
- [ ] Return `requires_reexecution_from_gate` when a mutation only suggests
      reopening an unconditional transformation.
- [ ] Verify historical `must_close_before_D10` metadata is never read back as
      current unresolved authority.
- [ ] Implement exact negative-claim activation where accepted edges permit.
- [ ] Implement exact route changes where accepted edges permit.
- [ ] Compute minimal invalidation roots as a DAG antichain rather than a linear
      suffix boundary.
- [ ] Form the tentative frontier from propagation-bearing descendants only.
- [ ] Subtract descendants whose complete support predicate remains satisfied
      by accepted support outside every mutated subtree.
- [ ] Compute each claim predicate from accepted `evidence_refs`, the accepted
      transformed dispositions of `bearing_debt_ids`/`debt_edges`, and its
      source-recorded `activation_condition`.
- [ ] Verify a conditional claim remains outside the frontier when its full
      predicate still passes through independent accepted support.
- [ ] Verify a multiply supported claim remains known when one support is
      removed and its complete support predicate still passes.
- [ ] Identify the deterministically ordered earliest accepted gate set affected
      by a mutation.
- [ ] Mark all unevaluated downstream results
      `unknown_beyond_evidence_frontier`.
- [ ] Return `requires_reexecution_from_gate` instead of generating a new result.
- [ ] Return `indeterminate_requires_review` for incomplete support semantics.
- [ ] Reject arbitrary field patches and unknown mutation types.
- [ ] Verify Candidate B completion scenarios do not synthesize B-specific
      D7G-D10 claims.
- [ ] Verify `change_candidate_disposition` for Candidate B at D7-v2 produces a
      non-empty reopening frontier and named missing B work rather than
      `no_propagation_bearing_effect`.
- [ ] Verify a Candidate B mutation at D7-v2 leaves source-confirmed,
      Candidate C-only claims outside the frontier when no accepted dependency
      connects them.
- [ ] Verify V4-D scenarios preserve its uninstantiated-slot identity.
- [ ] Verify profile-local changes do not leak into unrelated profiles.
- [ ] Detect when a mutation neutralizes a D10.2 provenance-hardening reason and
      list the blocked overread at risk without activating it.
- [ ] Verify no numeric prediction appears in structural output.
- [ ] Add adversarial tests for false support, false closure, false ranking,
      and fabricated downstream claims.
- [ ] Execute owned scenarios C1, C4-C6, and D2-D6; execute the semantic
      classification portions of supporting scenarios C2-C3 and C7.
- [ ] Run deterministic replay tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C4_bounded_counterfactual_kernel`.
- [ ] Reject the iteration if any scenario crosses the evidence frontier as a
      positive claim.

## Iteration 5. Ripple Compiler And Scenario Round Trip

**Status:** blocked on Iteration 4

### Goal

Compile profile-qualified ripple lookups and a canonical notebook/web scenario
format.

### Checks

- [ ] Freeze scenario schema and kernel schema versions.
- [ ] Bind every scenario to source-bundle and baseline-record digests.
- [ ] Store typed immutable mutations rather than graph-state patches.
- [ ] Freeze ripple keys with profile, candidate, realization, and baseline
      scope.
- [ ] Derive propagation scope from accepted `profile_ids`, disabled-reduction
      rows, candidate scope, realization scope, and activation conditions.
- [ ] Never substitute D10.2 object-family counts for profile scope.
- [ ] Fail closed when an empty profile list cannot be resolved to an explicit
      common or profile-independent scope.
- [ ] Emit one row per affected profile and zero rows for unrelated profiles.
- [ ] Verify a Candidate A-only mutation emits no Candidate C ripple row unless
      an accepted common contract explicitly connects them.
- [ ] Separate direct from transitive consequences.
- [ ] Include exact source-edge references in every consequence.
- [ ] Include the deterministically ordered earliest reopening-gate set and
      evidence frontier.
- [ ] Include `unknown_beyond_evidence_frontier` status explicitly.
- [ ] Include blocked-overread risks without inventing new negative claims.
- [ ] Include forward `verification_obligations_at_risk` separately from claim,
      debt, and evidence consequences.
- [ ] Verify an obligation-at-risk is never traversed backward as evidence or
      relabeled as a reopened scientific debt.
- [ ] Emit all-profile aggregates only as projections over the complete
      profile-local row set.
- [ ] Precompute existing-surface mutations only with propagation-bearing reach,
      and gate/candidate-disposition mutations only with a source-recorded
      reopening boundary and accepted descendants.
- [ ] Return `no_propagation_bearing_effect` and emit no ripple row for
      annotation-only or otherwise non-load-bearing equation/contract or
      parent-object targets.
- [ ] Partition large ripple output into deterministic shards with a canonical
      index; never truncate profile-local scientific coverage.
- [ ] Record target range, profile coverage, row count, digest, and source-bundle
      identity for every shard.
- [ ] Validate stale, malformed, missing-scope, and unknown-field scenarios fail.
- [ ] Prove notebook-to-web load/serialize/select/playback identity.
- [ ] Prove web-to-notebook serialization of a selected precomputed row
      reproduces the canonical scenario byte-for-byte.
- [ ] Verify the browser round trip cannot author or alter a mutation.
- [ ] Prove ripple-table rebuild byte identity.
- [ ] Apply the canonical serializer to scenarios, ripple rows, shard indexes,
      and aggregate projections.
- [ ] Verify source records remain byte-identical.
- [ ] Execute owned scenarios C2-C3, C7, and C9; rerun C4-C6 through the
      serialized ripple surface.
- [ ] Run focused compiler and scenario tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C5_ripple_and_scenario_contract`.
- [ ] Keep the browser closed until the static bundle has no embedded
      propagation rule.

## Iteration 6. Web Foundation, Triangulation, And Dependency Reach

**Status:** blocked on Iteration 5

### Goal

Build the static navigation client over validated, precomputed data.

### Checks

- [ ] Freeze frontend framework, build tooling, Cytoscape.js version, and local
      dependency policy.
- [ ] Build the actual exploration surface as the first page.
- [ ] Load only source manifests, validated graph projections, scenarios, and
      ripple tables produced by Python.
- [ ] Verify no propagation or scientific rule exists in JavaScript.
- [ ] Add focused search and selection.
- [ ] Enforce bounded-neighborhood rendering rather than full-graph sprawl.
- [ ] Add a family filter sourced from D10.2
      `coverage_contract.required_families`.
- [ ] Verify all nine family names and object counts match the accepted source.
- [ ] Keep family coverage separate from profile propagation and scientific
      ranking.
- [ ] Add node-family-specific triangulation for claims, debts, gates, profiles,
      objects/contracts, and source records.
- [ ] Verify debt views do not show claim-only lenses and claim views do not
      show debt-only or forward-work lenses.
- [ ] Add direct/transitive dependency reach by relation type.
- [ ] Avoid labeling dependency counts as importance or scientific priority.
- [ ] Add source record and digest details.
- [ ] Add source versus speculative segmented mode control.
- [ ] Add stable responsive layout and non-overlapping controls.
- [ ] Add keyboard navigation, focus states, text alternatives, tooltips, and
      reduced-motion behavior.
- [ ] Verify long IDs and claims remain readable on desktop and mobile.
- [ ] Add component and bundle-contract tests.
- [ ] Execute owned scenarios N1-N3 and the browser projections of F1, F4-F5,
      and F8.
- [ ] Assert browser payload and forensic API output are byte-identical for the
      same source bundle and selection, including nodes, edges, support types,
      scopes, and ripple row.
- [ ] Run initial Playwright desktop/mobile screenshots.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C6_static_navigation_surface`.
- [ ] Reject the iteration if client code can derive an uncompiled ripple.

## Iteration 7. Claim Ceilings And Alternative Layer

**Status:** blocked on Iteration 6

### Goal

Expose blocked claims and pruned alternatives without flattening their accepted
statuses.

### Checks

- [ ] Render accepted negative claims and blocked overreads as locked surfaces.
- [ ] Show the stronger blocked claim, bearing debt, source reason, and earliest
      reopening boundary set.
- [ ] Distinguish evidence, derivation, contradiction, routing, and
      out-of-scope lock reasons only where sourced.
- [ ] Map lock reasons to the exact D10.2
      `targeted_type_and_provenance_hardening` key and machine value where one
      exists.
- [ ] Cover all eight accepted hardening keys, including the separate Candidate
      A future-curvature rule.
- [ ] Mark readable lock paraphrases as non-authoritative annotations and reject
      any lock reason absent from source.
- [ ] Render A/B/C candidate careers with routed and conditional states intact.
- [ ] Render V4-D as a closed uninstantiated admission slot.
- [ ] Render historical claims and predecessor debt state as history, not
      current authority.
- [ ] Keep current debt transformations and verification obligations separate.
- [ ] Implement the alternatives slider as progressive visibility/opacity over
      rejected candidates, blocked relabels, conditional alternatives, and
      historical claims.
- [ ] Preserve dashed/non-color-only ghost distinction at every slider value.
- [ ] Verify ghost nodes cannot become accepted through selection, dragging,
      filtering, playback, or any other UI action.
- [ ] Verify slider position never changes propagation, classification, or
      scenario serialization.
- [ ] Verify no hidden score ranks candidates, claims, gates, or alternatives.
- [ ] Add source-mode and speculative-mode visual tests.
- [ ] Execute owned scenarios N5-N6, D7, and E2 plus the browser projections of
      F6-F7 and E3.
- [ ] Run Playwright screenshots and interaction tests.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C7_claim_ceiling_and_alternative_navigation`.

## Iteration 8. Lineage Scrubbing And Ripple Playback

**Status:** blocked on Iteration 7

### Goal

Navigate accepted lineage and play precomputed counterfactual effects without
collapsing history into a false linear timeline.

### Checks

- [ ] Build a readable spine projection over the lineage DAG.
- [ ] Preserve visible branches, corrections, and supersession markers.
- [ ] Bind every scrub position to an accepted record ID and digest.
- [ ] Support backward reconstruction from any visible claim.
- [ ] Load canonical scenarios without editing source graph state.
- [ ] Animate only a selected precomputed ripple row.
- [ ] Mark direct effects, transitive effects, reopening gate, and evidence
      frontier separately.
- [ ] Keep unknown downstream regions visibly unresolved.
- [ ] Freeze the scrubber at an accepted gate and animate a precomputed
      counterfactual fork from that point.
- [ ] Keep unaffected accepted branches solid while minimal invalidation roots
      and frontier are labeled and unresolved descendants fade/dash.
- [ ] Verify fork playback contains no browser-side propagation or rerun
      prediction.
- [ ] Prevent ripple playback from altering accepted source mode.
- [ ] Verify the same scenario produces identical notebook and web reports.
- [ ] Add route, correction, branch, and stale-scenario tests.
- [ ] Execute owned scenarios N4, C8, and E1 plus playback integration for C1-C2
      and C9.
- [ ] Run Playwright desktop/mobile screenshots and overlap checks.
- [ ] Run `git diff --check`.

### Gate

- [ ] Accept `ET-C8_lineage_and_ripple_navigation`.

## Iteration 9. Independent Validation And Closeout

**Status:** blocked on Iteration 8

### Goal

Validate that the completed side tool is deterministic, useful, and bounded by
the accepted investigation.

### Checks

- [ ] Re-run D10 topology, D10.1, and D10.2 accepted audits unchanged.
- [ ] Run the complete investigation-local Python test suite.
- [ ] Run the complete investigation-local web test suite.
- [ ] Rebuild graph, reports, scenarios, and ripple tables twice.
- [ ] Confirm byte-identical derived artifacts.
- [ ] Rebuild canonical fixtures on the admitted minimum and later supported
      Python versions (3.11 and 3.13 where available) and compare bytes; if that
      conformance cannot be established, narrow the tested compatibility range
      before acceptance.
- [ ] Confirm accepted source bytes are unchanged.
- [ ] Confirm no writes occurred under `src/`, `specs/`, repository tests, or
      accepted decision records.
- [ ] Audit JavaScript for propagation logic or duplicated scientific rules.
- [ ] Re-run cross-surface identity assertions for representative claim, debt,
      gate, profile, object/contract, source, and ripple selections.
- [ ] Audit annotations for accidental propagation authority.
- [ ] Audit every counterfactual for evidence-frontier enforcement.
- [ ] Audit every source and speculative label.
- [ ] Pressure malformed, stale, contradictory, and out-of-scope scenarios.
- [ ] Pressure candidate, profile, realization, topology-event, and correction
      lineage views.
- [ ] Run Playwright screenshots on desktop and mobile.
- [ ] Verify no blank graph, clipped controls, overlapping text, or unreadable
      long identifiers.
- [ ] Perform a forensic-task usability pass.
- [ ] Perform a navigational-task usability pass.
- [ ] Execute and reconcile all 35 normalized user scenarios against the
      scenario coverage matrix.
- [ ] Verify the nine forensic API functions and all eight required web views
      are exercised by at least one scenario.
- [ ] Write final reconstruction commands and artifact policy.
- [ ] Write closeout report and machine disposition.
- [ ] Run `git diff --check`.

### Closeout dispositions

- [ ] `accepted_bounded_read_only_exploratory_tool`
- [ ] `accepted_forensic_only_web_not_authorized`
- [ ] `accepted_navigation_only_counterfactual_not_authorized`
- [ ] `blocked_source_schema_insufficient`
- [ ] `blocked_counterfactual_semantics_require_new_authority`
- [ ] `closed_without_tool_implementation`

### Maximum claim

- [ ] Freeze that successful closeout supports a deterministic read-only
      exploration and bounded structural-counterfactual surface only.
- [ ] Block new V4 evidence, reopened-gate prediction, runtime implementation,
      specification conformance, and scientific claim promotion.
