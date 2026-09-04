# GRCv4 Exploratory Side Tool Implementation Checklist

**Date:** 2026-08-28; successor update 2026-09-04
**Status:** Iterations 0-10 accepted; Iteration 11 UX candidate implemented;
downstream D11 specification propagation verified
**Plan:** [GRCV4ExploratorySideToolImplementationPlan.md](./GRCV4ExploratorySideToolImplementationPlan.md)
**Source investigation:** [GRC9V4 constitutive design](../../README.md)

## Usage Rules

- [x] Keep the tool under `implementation/investigations/`.
- [x] Treat accepted `decisions/*.json` records as immutable source authority.
- [x] Keep the 67 parent objects distinct from the 152 equation/contract rows.
- [x] Preserve 39 current claims, 29 historical claims, 29 transformed debts,
      and 11 verification obligations as distinct source-owned populations.
- [x] Preserve those D10 populations as the immutable ET-C2 historical base;
      admit the D11 `+2/+2/+7/+13/+31` claim/debt/obligation/object/contract
      population only through the ET-C10 append-only overlay.
- [x] Keep the 18 combined obligation nodes distinct from the 17 pending
      obligations: the D10 preclose provenance obligation remains historically
      satisfied, while ten D10 and seven D11 obligations remain forward work.
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
branch = spec/grcv4-grc9v4
plan = extended_by_accepted_post_closeout_successor_cycle
checklist = iterations_0_through_10_accepted_plus_iteration_11_UX_candidate
tool_code = iteration_10_D11_forensic_overlay_accepted_with_iteration_11_UX
historical_accepted_source_records_changed = false
D11_successor_source_records_admitted = 8
src_and_repository_tests_changed_by_ET_C10 = false
specifications_changed_by_ET_C10 = false
paper_propagation = pending_tooling_ready
scientific_claims_created_by_tool = false
accepted_D11_claims_exposed_by_tool = 2
implementation_gate = ET-C11_D11_API_notebook_browser_UX_candidate
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

**Status:** accepted

### Goal

Load every currently admitted source through schema-specific read-only adapters,
emit one deterministic source-bundle identity, and detect repository source
evolution without interpreting or auto-admitting it.

### Checks

- [x] Implement adapters for D10 claim topology and historical claim nodes.
- [x] Implement adapters for D10 debt transformations and verification
      obligations.
- [x] Implement adapters for D10.2 parent objects and equation/contracts.
- [x] Implement adapters for D9 debt, profile, lifecycle, and event records.
- [x] Implement adapters for D0-D10.2 decision records and predecessor digests.
- [x] Implement a read-only discovery scan that compares the admitted inventory
      against all observed decision-record files before load, build, report, or
      serve operations.
- [x] Keep the discovery observation receipt separate from scientific
      source-bundle identity.
- [x] Classify `current_bundle_exact`, `new_unprocessed_source_available`,
      `admitted_source_identity_changed`, `admitted_source_missing`, and
      `source_observation_unreadable` without interpreting unadmitted content.
- [x] For unadmitted files, record only repository-relative path, file SHA, and
      safely readable top-level schema/status/record-ID discovery metadata.
- [x] Preserve an older exact bundle as a historical snapshot while preventing
      it from being labeled the complete current repository state.
- [x] Block live rebuild on changed or missing admitted sources and prohibit
      automatic parsing, schema guessing, status promotion, or partial graph
      insertion for newly observed files.
- [x] Emit a named refresh requirement that identifies adapter admission, new
      bundle identity, graph-conformance audit, complete derived-artifact
      rebuild, and successor processing acceptance as separate required steps.
- [x] Derive all admitted population counts directly from authoritative source
      arrays; keep expected counts as separate admission assertions rather than
      observed values.
- [x] Resolve every source-recorded claim, parent-object, profile, equation, and
      contract reference needed for graph coverage; reject dangling or
      ambiguous references before graph construction.
- [x] Select digest fields per schema rather than assuming one common field.
- [x] Validate canonical payload digests exactly.
- [x] Validate declared file SHAs and source identities where present.
- [x] Reject missing, duplicate, stale, malformed, or non-accepted records.
- [x] Record source hashes before and after load.
- [x] Prove adapters do not write source files.
- [x] Emit deterministic source-bundle manifest and digest.
- [x] Rebuild twice and prove byte identity.
- [x] Derive canonical, duplicate-preserving relationship witnesses in the
      builder for every admitted cross-source relationship family.
- [x] Independently rederive the same relationship witnesses from raw accepted
      JSON without calling the builder validator or importing its witness code.
- [x] Require exact per-family count/digest and whole-population digest
      equivalence; do not treat equal aggregate populations as equivalence.
- [x] Add fixtures for an exact inventory, extra draft record, extra accepted
      record, changed admitted identity, missing admitted source, unreadable
      observation, wrong digest/SHA/reference, changed status, and unknown
      schema.
- [x] Add adversarial failure fixtures for every relationship-witness family,
      including reciprocal edges, lineage, lifecycle, carry-forward, contract
      references, coverage, and authorization partitioning.
- [x] Execute owned scenario D1.
- [x] Run focused adapter tests.
- [x] Run `git diff --check`.

### Gate

- [x] Accept `ET-C1_source_bundle_admitted`.
- [x] Do not build the graph from partially admitted inputs.

### Accepted Result

```text
status = accepted
admitted_source_records = 33
source_observation = current_bundle_exact
source_bundle_digest = 79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc
reference_checks = 3753_passed
accepted_populations = 39_current_claims_29_historical_claims_29_debts_11_obligations
provenance_populations = 67_parent_objects_152_equation_contracts
lifecycle_coverage = 10_profiles_26_operations_260_cells
embedded_identities = 70_local_byte_verified_4_external_attested
adapter_fixture_matrix = 29_passed
independent_ET_C1_audit = 2014_passed
independent_relationship_assertions = 3936_passed
independent_relationship_digest = 219b3413db9c7142653ddbf51539b78b5a0e2df24db7407a5e3d71ae2d85c661
relationship_witness_families = 14
relationship_witness_occurrences = 2073
relationship_witness_digest = 1793217d1f0726e8735a1c8d18c1b8c70148d30559037e293a33fc799b47997f
builder_auditor_relationship_witness_equivalence = exact_per_family_and_global
claim_authority_classification = 39_of_39_exact_agreement
embedded_identity_independent_recount = 70_local_4_external_1_external_predecessor_root
deterministic_artifact_rebuild = byte_identical_twice
accepted_source_byte_identity = unchanged
ET_C1_record_digest = 85a1dfd45d5c68f84aa63f06bc792d1b09075c1ad9fcaeeda953278dae3b0c35
graph_kernel_implemented = false
iteration_2_authorized = true
```

Artifacts:

- [ETC1SourceAdapterAdmission.md](./records/ETC1SourceAdapterAdmission.md)
- [ETC1SourceAdapterAdmission.json](./records/ETC1SourceAdapterAdmission.json)
- [ETC1SourceBundleManifest.json](./records/ETC1SourceBundleManifest.json)

The external theory rows are checked as frozen source attestations rather than
resolved through a machine-local adjacent checkout. Repository-local identities
are verified against current bytes. A changed or newly observed decision record
therefore causes an explicit refresh requirement without weakening portability
or silently expanding the admitted source bundle.

`D10_1PreliminarySubstrateProvenance.json` is the sole filename-admitted legacy
schema record because the accepted source has no schema field. This absence is
explicit in the adapter contract: adding or changing its schema triggers source
identity change and requires readmission rather than changing adapters silently.

ET-C0 human acceptance is the explicit root of trust. ET-C1 independently
revalidates ET-C0 status, digest, source bytes, and relationships, but it does
not rederive the human acceptance decision. The browser is not implemented in
Iteration 1; Iteration 6 requires digest verification before rendering any
precomputed payload.

The builder and auditor now agree on every canonical relationship witness, not
only on population totals. A relationship substitution that preserves counts
changes its family digest and the global witness digest. This closes the known
pairwise-equivalence gap. It does not prove that two independently written
checkers cannot share the same conceptual mistake; the 29-case fixture matrix
therefore includes a fail-closed mutation for every witness family.

## Iteration 2. Validated Graph Kernel

**Status:** accepted

### Goal

Build the typed, deterministic, source-traceable graph without creating a
second scientific authority.

### Checks

- [x] Add distinct node classes for current claims and historical claims.
- [x] Add debt transformation and verification obligation nodes.
- [x] Model each unique `obligation_id` as one forward-only node without
      double-counting shared D9/D10 IDs.
- [x] Tag every `requires_verification_from` edge with originating gate ID,
      record ID/digest, and source JSON pointer; verify every shared ID's source
      occurrences remain recoverable.
- [x] Add gate records and accepted predecessor/supersession edges.
- [x] Add A/B/C candidate nodes and the precisely scoped V4-D slot.
- [x] Add realization and ten-profile nodes.
- [x] Add separate 67 parent-object and 152 equation/contract node layers.
- [x] Add source-record nodes and provenance edges.
- [x] Add annotation nodes with display-only authority.
- [x] Store `propagation_edges` and `annotation_edges` in physically disjoint
      tables with no shared rows or convertible authority flag.
- [x] Assert annotation-only input cannot contribute to reachability,
      invalidation, routing, or ripple output.
- [x] Add verification-obligation edges only in the forward
      `requires_verification_from` direction.
- [x] Verify backward reconstruction never treats a verification obligation as
      accepted support.
- [x] Preserve accepted claim/debt relation types.
- [x] Preserve transformation verbs rather than using generic production.
- [x] Type propagation support relations as required, one-of, conditional, or
      negative where the source supports that distinction; keep display-only
      relations exclusively in `annotation_edges`.
- [x] Return `indeterminate_requires_review` when support logic is not stated.
- [x] Build the full gate lineage DAG, including corrections and branches.
- [x] Validate current/historical claim disjointness.
- [x] Validate reciprocal claim/debt relations.
- [x] Validate no silent debt loss.
- [x] Validate all references and unique IDs.
- [x] Run an independent source-conformance audit that does not call kernel APIs
      and re-derives populations, IDs, reference coverage, reciprocal
      relations, and claim-to-contract coverage from accepted source records.
- [x] Fail if the 152-row equation/contract count is correct but any required
      claim-to-contract relationship is missing, unresolved, or only asserted
      by a literal.
- [x] Validate DAG acyclicity and predecessor digest consistency.
- [x] Validate annotations cannot affect propagation.
- [x] Emit deterministic canonical graph serialization.
- [x] Serialize with sorted keys/collections, fixed separators, no NaN, and the
      Iteration 0 finite-number policy.
- [x] Rebuild twice and prove byte identity.
- [x] Execute owned scenario F9.
- [x] Run focused kernel and invariant tests.
- [x] Run `git diff --check`.

### Result

- graph snapshot: `records/ETC2GraphSnapshot.json`
- accepted record: `records/ETC2ValidatedGraphKernel.json`
- accepted report: `records/ETC2ValidatedGraphKernel.md`
- graph digest: `2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae`
- accepted record digest: `10dc5cef2bffc764296cb9e38908cd1f992b9ce7c4c60d04a8ef6efda5d1453b`
- graph population: `436 nodes / 2,666 propagation edges / 4 annotation edges`
- independent audit: `117 checks / 436 exact nodes / 2,670 exact relationships`
- kernel invariants: `14/14 passed`
- focused fixture matrix: `14/14 fail-closed mutations passed`
- support semantics: `38 required / 31 conditional / 14 negative-boundary /`
  `1,147 indeterminate / 1,436 non-support-not-applicable / 0 inferred one-of`
- scenario F9: `passed_accepted_execution`
- source bundle: `unchanged; ET-C1 digest 79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc`
- Iteration 3: `authorized; not implemented`

### Gate

- [x] Accept `ET-C2_validated_graph_kernel`.
- [x] Block Iteration 3 if any propagation-bearing edge requires an
      unclassified hand-authored relation.

## Iteration 3. Forensic API And Notebook Recipes

**Status:** accepted

### Goal

Expose source-exact reconstruction through pure Python functions before visual
or counterfactual work.

### Checks

- [x] Implement `gate_act(record_id)`.
- [x] Implement `debt_lifecycle(debt_id)`.
- [x] Implement `reconstruction_path(claim_id)`.
- [x] Implement `candidate_career(candidate_id)`.
- [x] Implement `pruned_choices_at(record_id)`.
- [x] Implement `negative_claims()`.
- [x] Implement `object_dependents(object_id)`.
- [x] Implement `contract_provenance(contract_id)`.
- [x] Implement `gate_contribution(record_id)`.
- [x] Ensure each row includes source record, digest, and exact edge references.
- [x] Distinguish added, inherited, narrowed, routed, superseded, conditioned,
      and resolved-negative content.
- [x] Add stable Markdown and JSON forensic reports.
- [x] Add a minimal notebook that calls the pure functions without duplicating
      logic.
- [x] Verify notebook execution writes only to the derived output envelope.
- [x] Verify forensic output contains no speculative claims.
- [x] Execute owned scenarios F1-F8 and E3-E4.
- [x] Rebuild representative reports twice and prove byte identity.
- [x] Run focused forensic and notebook tests.
- [x] Run `git diff --check`.

### Result

- scenario report: `records/ETC3ForensicScenarioReport.json`
- candidate record: `records/ETC3ForensicReconstructionSurface.json`
- scenario report digest: `ddd91b4ec63894f955b9423caf71f4fc27df559ac74d54a822d4f32042055f14`
- candidate record digest: `250723350ac838abcdb83ec96a48b4eaa734dfb3c287c9e19183bbc2b4b4eef9`
- forensic APIs: `9 implemented`
- owned scenarios: `12/12 passed candidate execution`
- independent audit: `10,018 checks / 101 rows / 1,205 exact edge references`
- focused API/notebook matrix: `15/15 passed`
- notebook recipes: `2 passed; non-generated file hashes unchanged`
- deterministic rebuild: `2/2 byte-identical`
- output class: `forensic_evidence_trace only`
- source bundle and graph: `unchanged ET-C1 / accepted ET-C2`
- accepted residual boundaries:
  `lighter_I3_matrix_with_ET_C2_invariant_ownership`,
  `ET_C2_chained_trust_with_revalidation`, and
  `source_bounded_Candidate_A_D10_2_hardening_projection`
- residual reopening triggers: `forensic authority mutation or uncovered
  payload`, `ET-C2 identity/authority change`, or `another candidate-specific
  hardening projection`
- Iteration 4: `accepted`

### Gate

- [x] Accept `ET-C3_forensic_reconstruction_surface`.
- [x] Keep counterfactual and browser claims closed.

## Iteration 4. Counterfactual Mutation And Evidence Frontier

**Status:** accepted

### Goal

Support conservative structural counterfactuals without pretending to rerun
the investigation.

### Checks

- [x] Freeze typed mutation IDs and schemas.
- [x] Require target kind, baseline record/digest, profile, candidate,
      realization, and declared payload scopes.
- [x] Admit `equation_contract`, `normative_object`, `gate_record`, and
      `candidate` target kinds with type-specific validation.
- [x] Apply existing-path sparsity to equation/contract and parent-object
      mutations; return `no_propagation_bearing_effect` when no
      propagation-bearing path exists.
- [x] For gate/candidate-disposition mutations, open a source-recorded reopening
      boundary and propagate over accepted descendants of the reopened gate
      without requiring an existing path from the proposed disposition.
- [x] Implement required-support invalidation.
- [x] Implement explicit one-of support behavior.
- [x] Implement conditional activation only from source-recorded conditions.
- [x] Implement exact debt reactivation only when a recorded conditional
      closing names a precondition that the mutation falsifies.
- [x] Return `requires_reexecution_from_gate` when a mutation only suggests
      reopening an unconditional transformation.
- [x] Verify historical `must_close_before_D10` metadata is never read back as
      current unresolved authority.
- [x] Implement exact negative-claim activation where accepted edges permit.
- [x] Implement exact route changes where accepted edges permit.
- [x] Compute minimal invalidation roots as a DAG antichain rather than a linear
      suffix boundary.
- [x] Form the tentative frontier from propagation-bearing descendants only.
- [x] Subtract descendants whose complete support predicate remains satisfied
      by accepted support outside every mutated subtree.
- [x] Compute each claim predicate from accepted `evidence_refs`, the accepted
      transformed dispositions of `bearing_debt_ids`/`debt_edges`, and its
      source-recorded `activation_condition`.
- [x] Verify a conditional claim remains outside the frontier when its full
      predicate still passes through independent accepted support.
- [x] Verify a multiply supported claim remains known when one support is
      removed and its complete support predicate still passes.
- [x] Identify the deterministically ordered earliest accepted gate set affected
      by a mutation.
- [x] Mark all unevaluated downstream results
      `unknown_beyond_evidence_frontier`.
- [x] Return `requires_reexecution_from_gate` instead of generating a new result.
- [x] Return `indeterminate_requires_review` for incomplete support semantics.
- [x] Reject arbitrary field patches and unknown mutation types.
- [x] Verify Candidate B completion scenarios do not synthesize B-specific
      D7G-D10 claims.
- [x] Verify `change_candidate_disposition` for Candidate B at D7-v2 produces a
      non-empty reopening frontier and named missing B work rather than
      `no_propagation_bearing_effect`.
- [x] Verify a Candidate B mutation at D7-v2 leaves source-confirmed,
      Candidate C-only claims outside the frontier when no accepted dependency
      connects them.
- [x] Verify V4-D scenarios preserve its uninstantiated-slot identity.
- [x] Verify profile-local changes do not leak into unrelated profiles.
- [x] Detect when a mutation neutralizes a D10.2 provenance-hardening reason and
      list the blocked overread at risk without activating it.
- [x] Verify no numeric prediction appears in structural output.
- [x] Add adversarial tests for false support, false closure, false ranking,
      and fabricated downstream claims.
- [x] Execute owned scenarios C1, C4-C6, and D2-D6; execute the semantic
      classification portions of supporting scenarios C2-C3 and C7.
- [x] Run deterministic replay tests.
- [x] Run `git diff --check`.

### Result

- scenario report: `records/ETC4CounterfactualScenarioReport.json`
- accepted record: `records/ETC4BoundedCounterfactualKernel.json`
- scenario report digest: `fbcb0471725157f42daae0954889082b03e164659df14cb6bdc5c5205f8ea15c`
- accepted record digest: `4eea388fd9ee610a19d17efe48ed3512b2afb81f0f6fefcae89d5494dad46f89`
- mutation algebra: `9 mutation types / 4 target kinds / 9 result statuses`
- scenario matrix: `13/13 passed candidate execution`
- source-bound exact results: `1 routed Candidate B debt / 0 exact debt
  reactivations / 0 exact negative activations`
- independent audit: `1,775 checks / 169 exact edge references`
- focused/adversarial matrix: `38/38 passed`
- deterministic rebuild: `2/2 byte-identical`
- predecessor regression: `ET-C3 full verification passed`
- claim boundary: `0 numeric predictions / 0 positive claims beyond frontier /
  0 fabricated successor claims`
- Iteration 5: `authorized; not implemented`

### Gate

- [x] Accept `ET-C4_bounded_counterfactual_kernel`.
- [x] Reject the iteration if any scenario crosses the evidence frontier as a
      positive claim.

## Iteration 5. Ripple Compiler And Scenario Round Trip

**Status:** accepted

### Goal

Compile profile-qualified ripple lookups and a canonical notebook/web scenario
format.

### Checks

- [x] Freeze scenario schema and kernel schema versions.
- [x] Bind every scenario to source-bundle and baseline-record digests.
- [x] Store typed immutable mutations rather than graph-state patches.
- [x] Freeze ripple keys with profile, candidate, realization, and baseline
      scope.
- [x] Derive propagation scope from accepted `profile_ids`, disabled-reduction
      rows, candidate scope, realization scope, and activation conditions.
- [x] Never substitute D10.2 object-family counts for profile scope.
- [x] Fail closed when an empty profile list cannot be resolved to an explicit
      common or profile-independent scope.
- [x] Emit one row per affected profile and zero rows for unrelated profiles.
- [x] Verify a Candidate A-only mutation emits no Candidate C ripple row unless
      an accepted common contract explicitly connects them.
- [x] Separate direct from transitive consequences.
- [x] Include exact source-edge references in every consequence.
- [x] Include the deterministically ordered earliest reopening-gate set and
      evidence frontier.
- [x] Include `unknown_beyond_evidence_frontier` status explicitly.
- [x] Include blocked-overread risks without inventing new negative claims.
- [x] Include forward `verification_obligations_at_risk` separately from claim,
      debt, and evidence consequences.
- [x] Verify an obligation-at-risk is never traversed backward as evidence or
      relabeled as a reopened scientific debt.
- [x] Emit all-profile aggregates only as projections over the complete
      profile-local row set.
- [x] Precompute existing-surface mutations only with propagation-bearing reach,
      and gate/candidate-disposition mutations only with a source-recorded
      reopening boundary and accepted descendants.
- [x] Return `no_propagation_bearing_effect` and emit no ripple row for
      annotation-only or otherwise non-load-bearing equation/contract or
      parent-object targets.
- [x] Partition large ripple output into deterministic shards with a canonical
      index; never truncate profile-local scientific coverage.
- [x] Record target range, profile coverage, row count, digest, and source-bundle
      identity for every shard.
- [x] Validate stale, malformed, missing-scope, and unknown-field scenarios fail.
- [x] Prove notebook-to-web load/serialize/select/playback identity.
- [x] Prove web-to-notebook serialization of a selected precomputed row
      reproduces the canonical scenario byte-for-byte.
- [x] Verify the browser round trip cannot author or alter a mutation.
- [x] Prove ripple-table rebuild byte identity.
- [x] Apply the canonical serializer to scenarios, ripple rows, shard indexes,
      and aggregate projections.
- [x] Verify source records remain byte-identical.
- [x] Execute owned scenarios C2-C3, C7, and C9; rerun C4-C6 through the
      serialized ripple surface.
- [x] Run focused compiler and scenario tests.
- [x] Run `git diff --check`.

### Result

- scenario bundle: `records/ETC5ScenarioBundle.json`
- all-profile projection: `records/ETC5AllProfilesAggregate.json`
- shard index: `records/ETC5RippleShardIndex.json`
- accepted record: `records/ETC5RippleAndScenarioContract.json`
- scenario bundle digest: `52630207a8e2d2510c799d81de313a2515088ba5790d0f383fadd7eb827dfee3`
- all-profile aggregate digest: `e8f067860bb62c6263fd213ca10e605f5ea088557f3d6ca98a0bd2d6fc542c2b`
- shard index digest: `882d4e3e2e254083fcef8b249b640e60f4561cad4b0ca7acffa440cbd9a8ba4e`
- accepted record digest: `1da09db7cea385d8e7818e38c0c8f2c7a6b2c77ee8fa4518415cdd7d02ba33fa`
- canonical scenarios: `25` across C1-C7
- profile-local rows: `24`; C6 serializes but emits no ripple
- deterministic delivery: `3 shards x 8 rows`; no truncation
- independent audit: `4,133 checks / 836 consequence-edge witnesses`
- focused/adversarial matrix: `89/89 passed`
- round trip: `24/24 selected rows reproduce canonical scenario bytes`
- predecessor regression: `ET-C4 full verification passed`
- claim boundary: `browser absent / no embedded propagation rule / no new
  scientific evidence / no result past the evidence frontier`
- Iteration 6: `authorized; not implemented`

### Gate

- [x] Accept `ET-C5_ripple_and_scenario_contract`.
- [x] Keep the browser closed until the static bundle has no embedded
      propagation rule.

## Iteration 6. Web Foundation, Triangulation, And Dependency Reach

**Status:** accepted

### Goal

Build the static navigation client over validated, precomputed data.

### Checks

- [x] Freeze frontend framework, build tooling, Cytoscape.js version, and local
      dependency policy.
- [x] Build the actual exploration surface as the first page.
- [x] Load only source manifests, validated graph projections, scenarios, and
      ripple tables produced by Python.
- [x] Verify manifest, projection, scenario, and ripple payload digests before
      rendering; reject missing or mismatched bindings rather than relying on a
      prior audit having been run.
- [x] Verify no propagation or scientific rule exists in JavaScript.
- [x] Add focused search and selection.
- [x] Enforce bounded-neighborhood rendering rather than full-graph sprawl.
- [x] Add a family filter sourced from D10.2
      `coverage_contract.required_families`.
- [x] Verify all nine family names and object counts match the accepted source.
- [x] Keep family coverage separate from profile propagation and scientific
      ranking.
- [x] Add node-family-specific triangulation for claims, debts, gates, profiles,
      objects/contracts, and source records.
- [x] Verify debt views do not show claim-only lenses and claim views do not
      show debt-only or forward-work lenses.
- [x] Add direct/transitive dependency reach by relation type.
- [x] Avoid labeling dependency counts as importance or scientific priority.
- [x] Add source record and digest details.
- [x] Show whether the loaded bundle is current, historical-with-new-unprocessed
      source, stale from changed/missing admitted source, or observation-blocked.
- [x] Require notebook/build/serve launchers to refresh discovery state; label a
      standalone static bundle as a build-time snapshot when live rescan is
      unavailable.
- [x] Add source versus speculative segmented mode control.
- [x] Add stable responsive layout and non-overlapping controls.
- [x] Add keyboard navigation, focus states, text alternatives, tooltips, and
      reduced-motion behavior.
- [x] Verify long IDs and claims remain readable on desktop and mobile.
- [x] Add component and bundle-contract tests.
- [x] Execute owned scenarios N1-N3 and the browser projections of F1, F4-F5,
      and F8.
- [x] Assert browser payload and forensic API output are byte-identical for the
      same source bundle and selection, including nodes, edges, support types,
      scopes, and ripple row.
- [x] Run initial Playwright desktop/mobile screenshots.
- [x] Run `git diff --check`.

### Result

- status: `accepted`
- static bundle: `436 nodes / 436 bounded selection projections`
- focus ceiling: `32 nodes / 72 relationships`
- D10.2 family coverage: `9 families / 67 objects`, exact counts
- ripple/scenario payload: `25 scenarios / 24 precompiled rows / 3 shards`
- cross-surface parity: `7/7 representative projections byte-identical`
- independent audit: `44,895 checks passed`
- focused tests: `47 Python checks / 8 Node tests passed`
- browser pressure: `desktop + mobile Playwright passed; screenshots inspected`
- deterministic rebuild: `2/2 byte-identical`
- predecessor regression: `ET-C5 full verification passed`
- static bundle digest:
  `45a96e782a1ecdd5fb693e171052a020bfdbffa76d21ca07e0a307b9cc96684c`
- parity digest:
  `341efa17d6c03c6235aca45141736302d418c162dd88ac6bd7a4cb7d50170b20`
- web build manifest digest:
  `20f1dca4094c3ff3c8743694455d545ca0c56c7f5bd1fc7c786a6ce9047a03c2`
- accepted record digest:
  `6353caaf1cb67b4228bfd9d74a4898a72a8ba886dcb84b55757d019b0d1c3629`
- authority boundary: `Python-compiled scientific projections only; browser
  verifies and presents; no browser mutation, propagation, ripple compilation,
  ranking, or new scientific claim`
- Iteration 7: `accepted; Iteration 8 authorized`

### Gate

- [x] Accept `ET-C6_static_navigation_surface`.
- [x] Reject the iteration if client code can derive an uncompiled ripple; no
      such derivation exists in the candidate.

## Iteration 7. Claim Ceilings And Alternative Layer

**Status:** accepted

### Goal

Expose blocked claims and pruned alternatives without flattening their accepted
statuses.

### Checks

- [x] Render accepted negative claims and blocked overreads as locked surfaces.
- [x] Show the stronger blocked claim, bearing debt, source reason, and earliest
      reopening boundary set.
- [x] Distinguish evidence, derivation, contradiction, routing, and
      out-of-scope lock reasons only where sourced.
- [x] Map lock reasons to the exact D10.2
      `targeted_type_and_provenance_hardening` key and machine value where one
      exists.
- [x] Cover all eight accepted hardening keys, including the separate Candidate
      A future-curvature rule.
- [x] Mark readable lock paraphrases as non-authoritative annotations and reject
      any lock reason absent from source.
- [x] Render A/B/C candidate careers with routed and conditional states intact.
- [x] Render V4-D as a closed uninstantiated admission slot.
- [x] Render historical claims and predecessor debt state as history, not
      current authority.
- [x] Keep current debt transformations and verification obligations separate.
- [x] Implement the alternatives slider as progressive visibility/opacity over
      rejected candidates, blocked relabels, conditional alternatives, and
      historical claims.
- [x] Preserve dashed/non-color-only ghost distinction at every slider value.
- [x] Verify ghost nodes cannot become accepted through selection, dragging,
      filtering, playback, or any other UI action.
- [x] Verify slider position never changes propagation, classification, or
      scenario serialization.
- [x] Verify no hidden score ranks candidates, claims, gates, or alternatives.
- [x] Add source-mode and speculative-mode visual tests.
- [x] Execute owned scenarios N5-N6, D7, and E2 plus the browser projections of
      F6-F7 and E3.
- [x] Run Playwright screenshots and interaction tests.
- [x] Run `git diff --check`.

### Result

- status: `accepted`
- locked surfaces: `90` (`6` accepted negatives, `8` targeted hardenings,
  `76` other source-exact blocked surfaces)
- alternatives: `144` (`96` blocked relabels, `29` historical claims, `12`
  conditional claims, `5` rejected alternatives, `1` routed candidate, `1`
  rejected candidate)
- candidate careers: `3` (`A`, `B`, `C`)
- authority populations: `29 current transformations / 11 verification
  obligations / 29 historical claims`
- independent audit: `2,173 checks passed`
- focused tests: `477 Python checks / 12 Node tests passed`
- browser pressure: `4 Playwright tests / desktop + mobile / 6 screenshots`
- visual inspection: `passed; no overlap or accepted/ghost conflation`
- deterministic rebuild: `2/2 byte-identical`
- predecessor regression: `ET-C6 focused 47-check suite passed`
- layer digest:
  `6d694de0e7ffbdea653543668472534ac6fde4be0ea1e1aedc6e1cf561cecc9f`
- web build manifest digest:
  `d63a69d4c65fcc5a159df3f74f030c23100c692cad9a4824fad3f0e043864db6`
- accepted record digest:
  `504e8474166c9f71018304f81251d1a65c9777b9e8eb70e71a7b5edb360ba688`
- verification receipt digest:
  `1eefce7345bc315022f15061ebeffd8f5c51d8d5fb8df47b1f6c53116dbe14be`
- authority boundary: `Python compiles source-exact lock, career, and
  alternative projections; the browser verifies and presents them; no browser
  promotion, propagation, serialization, ranking, or new scientific claim`
- Iteration 8: `authorized; not implemented`

### Gate

- [x] Accept `ET-C7_claim_ceiling_and_alternative_navigation`.

## Iteration 8. Lineage Scrubbing And Ripple Playback

**Status:** accepted

### Goal

Navigate accepted lineage and play precomputed counterfactual effects without
collapsing history into a false linear timeline.

### Checks

- [x] Build a readable spine projection over the lineage DAG.
- [x] Preserve visible branches, corrections, and supersession markers.
- [x] Bind every scrub position to an accepted record ID and digest.
- [x] Support backward reconstruction from any visible claim.
- [x] Load canonical scenarios without editing source graph state.
- [x] Animate only a selected precomputed ripple row.
- [x] Mark direct effects, transitive effects, reopening gate, and evidence
      frontier separately.
- [x] Keep unknown downstream regions visibly unresolved.
- [x] Freeze the scrubber at an accepted gate and animate a precomputed
      counterfactual fork from that point.
- [x] Keep unaffected accepted branches solid while minimal invalidation roots
      and frontier are labeled and unresolved descendants fade/dash.
- [x] Verify fork playback contains no browser-side propagation or rerun
      prediction.
- [x] Prevent ripple playback from altering accepted source mode.
- [x] Verify the same scenario produces identical notebook and web reports.
- [x] Add route, correction, branch, and stale-scenario tests.
- [x] Execute owned scenarios N4, C8, and E1 plus playback integration for C1-C2
      and C9.
- [x] Run Playwright desktop/mobile screenshots and overlap checks.
- [x] Run `git diff --check`.

### Result

- status: `accepted`
- accepted lineage: `33 gate records / 27 predecessor links`
- readable projection: `26 scrub positions / 7 companion branches`
- typed overlays: `4 v2 supersessions / 1 post-v2 correction`
- backward reconstruction: `68 visible claims`
- playback: `24 ET-C5 rows / 4 precomputed frames per row`
- source authority: `immutable; 0 browser propagation rules / 0 rerun predictions`
- deterministic rebuild: `2/2 byte-identical`
- independent audit: `34,241 checks passed` (`1,049` structural + `33,192`
  per-edge-reference assertions over `11,064` reconstruction links)
- focused tests: `185 Python checks / 17 Node tests passed`
- browser pressure: `8 Playwright tests / desktop + mobile / 10 screenshots`
- visual inspection: `passed; no overlap, clipping, or authority conflation`
- predecessor regression: `ET-C7 focused 477-check suite passed`
- shared-dist boundary: `web/dist is the latest ET-C8 build; the historical
  ET-C7 full-dist manifest is not a validator for newer asset hashes`
- layer digest:
  `5c5c29a9c636c5a91e2cf37921c323f97ef42ddb9d21442b4e44e17426b50faa`
- web build manifest digest:
  `dc1456e975c0851d1ecc817422f2cedb9c25e0b182c3cbca2147b4d634f7bee7`
- accepted record digest:
  `a11d390de18469210c82e85fe7c8d2e41eddb20ae811541923db0325fb3a2c20`
- verification receipt digest:
  `7fcd3f3df3a8f2a0c14c1ffcb2aa05d98db85f310c3b73772326556e8430e608`
- authority boundary: `Python compiles accepted lineage and exact ET-C5
  frames; the browser verifies and presents them; source mode cannot change and
  speculative descendants beyond the recorded frontier remain unresolved`
- Iteration 9: `authorized; not implemented`

### Gate

- [x] Accept `ET-C8_lineage_and_ripple_navigation`.

## Iteration 9. Independent Validation And Closeout

**Status:** accepted

### Goal

Validate that the completed side tool is deterministic, useful, and bounded by
the accepted investigation.

### Checks

- [x] Re-run D10 topology, D10.1, and D10.2 accepted audits unchanged.
- [x] Run the complete investigation-local Python test suite.
- [x] Run the complete investigation-local web test suite.
- [x] Rebuild graph, reports, scenarios, and ripple tables twice.
- [x] Confirm byte-identical derived artifacts.
- [x] Rebuild canonical fixtures on the admitted minimum and later supported
      Python versions (3.11 and 3.13 where available) and compare bytes; if that
      conformance cannot be established, narrow the tested compatibility range
      before acceptance.
- [x] Confirm accepted source bytes are unchanged.
- [x] Confirm no writes occurred under `src/`, `specs/`, repository tests, or
      accepted decision records.
- [x] Audit JavaScript for propagation logic or duplicated scientific rules.
- [x] Re-run cross-surface identity assertions for representative claim, debt,
      gate, profile, object/contract, source, and ripple selections.
- [x] Audit annotations for accidental propagation authority.
- [x] Audit every counterfactual for evidence-frontier enforcement.
- [x] Audit every source and speculative label.
- [x] Pressure malformed, stale, contradictory, and out-of-scope scenarios.
- [x] Pressure added, changed, missing, and unreadable source inventories and
      prove none can silently alter the admitted graph.
- [x] Prove a newly accepted source requires adapter/readmission, a successor
      bundle identity, full rebuild, and re-audit before current-state labeling.
- [x] Pressure candidate, profile, realization, topology-event, and correction
      lineage views.
- [x] Run Playwright screenshots on desktop and mobile.
- [x] Verify no blank graph, clipped controls, overlapping text, or unreadable
      long identifiers.
- [x] Perform a forensic-task usability pass.
- [x] Perform a navigational-task usability pass.
- [x] Execute and reconcile all 35 normalized user scenarios against the
      scenario coverage matrix.
- [x] Verify the nine forensic API functions and all eight required web views
      are exercised by at least one scenario.
- [x] Write a user guide with 13 complete start/action/endpoint/stop workflows,
      including the governed notebook-to-browser path, verified screenshots,
      and a link to the canonical 35-scenario contract without duplicating its
      catalog.
- [x] Write an agentic guide with complete forensic, counterfactual, and source
      evolution workflows.
- [x] Document the accepted two-recipe notebook runner, output envelope,
      browser cross-check, non-Jupyter execution boundary, and absence of a
      second admitted counterfactual-authoring notebook.
- [x] Execute a tracked nine-query walkthrough under repository `.venv` and
      keep its canonical outputs under the ignored generated-output tree.
- [x] Write final reconstruction commands and artifact policy.
- [x] Write closeout report and machine disposition.
- [x] Run `git diff --check`.

### Closeout dispositions

- [x] `accepted_bounded_read_only_exploratory_tool`
- [ ] `accepted_forensic_only_web_not_authorized`
- [ ] `accepted_navigation_only_counterfactual_not_authorized`
- [ ] `blocked_source_schema_insufficient`
- [ ] `blocked_counterfactual_semantics_require_new_authority`
- [ ] `closed_without_tool_implementation`

### Maximum claim

- [x] Freeze that successful closeout supports a deterministic read-only
      exploration and bounded structural-counterfactual surface only.
- [x] Block new V4 evidence, reopened-gate prediction, runtime implementation,
      specification conformance, and scientific claim promotion.

### Result

- status: `accepted`
- selected disposition: `accepted_bounded_read_only_exploratory_tool`
- scenario reconciliation: `35/35; one accepted owning gate per row`
- forensic API coverage: `9/9`
- required web-view coverage: `8/8`
- independent closeout audit: `374 checks passed`
- focused/adversarial closeout matrix: `15 checks passed`
- documentation: `canonical 35-scenario contract; 13 complete user workflows;
  12 complete agentic workflows; governed two-recipe notebook path; 9/9
  executable forensic queries; 6 tracked verified screenshots; shared glossary
  and ET-C8/ET-C9 boundary`
- Python suite: `24 commands including the agentic walkthrough`
- Node suite: `17 tests`
- accepted reconstruction: `2/2 byte-identical cycles`
- closeout reconstruction: `2/2 byte-identical cycles`
- historical web stages: `ET-C6/ET-C7 source/layer and canonical manifest
  metadata audited; superseded shared-dist bytes excluded; ET-C8 latest dist
  audited exactly`
- browser pressure: `12 Playwright tests / desktop + mobile / 14 screenshots`
- visual inspection: `passed; no blank graph, clipping, overlap, unreadable long
  identifier, or authority conflation`
- portability: `relocated clean bootstrap passed with network-permitted locked
  dependency restoration`
- Python conformance: `3.12.3 tested; 3.11 and 3.13 unavailable and unclaimed`
- source/protected paths: `byte-identical`
- scenario coverage digest:
  `a4608d728c9b9e356421adb2d6b98390794c0916e90c299ad88467720f3c7404`
- environment conformance digest:
  `6e97213f1dd5f471a97a1e502d851d48de11903ad952c9a8b7698014b30c49ca`
- accepted closeout digest:
  `7e9fb5a8dada805b1cd1b86e877bf1d23cfc16c4a6c0a1ef97d8f518e6ee0288`
- verification receipt digest:
  `c0ae8b45a0d501d988845ce9565a3c89752a815a9a77676551c503870953266a`
- authority boundary: `no source admission, scientific promotion, rerun
  prediction, runtime implementation, or specification conformance`

### Gate

- [x] Human review accepts one closeout disposition.

## Iteration 10. D11 Append-Only Source And Forensic Admission

**Status:** accepted

### Goal

Admit accepted D11 authority without rewriting the historical ET-C0 through
ET-C9 artifacts, and make the D11 results queryable before paper propagation.

### Checks

- [x] Freeze a separate eight-record D11 source contract with exact schemas,
      statuses, canonical digest fields, canonical digests, and file SHAs.
- [x] Bind the successor contract to the accepted ET-C0 record, ET-C1 bundle,
      ET-C2 admission, and ET-C2 graph digests.
- [x] Keep open and queued preregistrations as lineage/candidate history rather
      than accepted scientific claim authority.
- [x] Require combined discovery to report `current_bundle_exact` for all 41
      historical plus D11 decision JSON records.
- [x] Rebuild the D11 source manifest and graph in memory and compare canonical
      bytes with the accepted ET-C10 artifacts.
- [x] Prove that every historical ET-C2 node, propagation edge, and annotation
      edge survives unchanged.
- [x] Admit exactly two D11 claims, two local debt transformations, seven
      forward obligations, 13 normative objects, and 31 equation contracts.
- [x] Preserve the combined counts `41/29/31/18/80/183` and record that 17 of
      the 18 obligation nodes remain pending.
- [x] Expose the 12 D11 investigation candidates and two selected profile
      identities without changing the D10 substrate candidate or realization
      populations.
- [x] Make D11-C and D11-G9 claims available to `reconstruction_path` with
      forward obligations excluded from backward evidence.
- [x] Make both local D11 debts available to `debt_lifecycle` with opening,
      bounded resolution, and forward obligations in separate classified rows.
- [x] Make representative D11 objects and all D11 contracts available to
      `object_dependents` and `contract_provenance` with exact source pointers
      and support semantics.
- [x] Preserve `load_forensic_context` as the historical D10/ET-C2 loader and
      add `load_successor_forensic_context` for current D11 queries.
- [x] Verify the historical loader rejects D11 IDs and the successor loader
      still rejects `D10_2_CL_N_001` as a record-local provenance reference.
- [x] Add the six S1-S6 successor scenarios without rewriting the accepted
      ET-C9 `35/35` scenario receipt.
- [x] Add a two-state paper-propagation audit: exact pre-propagation paper bytes
      pass as pending; changed bytes must contain the complete D11 authority
      population and key equation/profile markers.
- [x] Advance the phase boundary to `paper_propagation` under the hash-bound
      accepted D11-G9 resolution while freezing specifications, `src/`, tests,
      GRC9, and GRC9V3.
- [x] Add build, audit, test, paper-audit, and normal verification commands to
      the admitted runner.
- [x] Update the implementation plan, checklist, scenarios, and agentic guide.
- [x] Run Ruff format/lint and `git diff --check`.
- [x] Run the complete normal verifier with the historical audits and ET-C10
      in-memory overlay audit/test.

### Result

- source contract: `records/ETC10D11SourceContract.json`
- source contract digest:
  `afab36a86604fcea50332375781be3c82427e72e3e8c10d7f2cb9c7814f40f81`
- source manifest: `records/ETC10D11SourceBundleManifest.json`
- source-bundle digest:
  `98c273b3cc097f0d95adfba98ed7dfac0ac494dce9e779bb4b04fe79fef4f6aa`
- graph snapshot: `records/ETC10D11GraphSnapshot.json`
- graph digest:
  `44d8c7d33950af5e5f7c61caa4fe6fbd14fc9aedf14218d0a11de7c705542e09`
- forensic admission: `records/ETC10D11ForensicAdmission.json`
- combined scientific populations: `41/29/31/18/80/183`
- pending forward obligations: `17`
- successor scenarios: `6/6 passed`
- successor scenario contract:
  `GRCV4ExploratorySideToolD11SuccessorScenarios.md`
- focused audit: `passed`
- focused fail-closed test: `12 checks passed`
- normal verifier: `ET_C10_D11_VERIFY_PASS`
- paper audit: `pending_tooling_ready`
- historical graph rewritten: `false`
- paper changed by ET-C10: `false`
- specifications changed by ET-C10: `false`
- runtime or repository tests changed by ET-C10: `false`
- GRC9 or GRC9V3 changed: `false`

### Gate

- [x] Accept `ET-C10_D11_append_only_forensic_admission`.
- [x] Authorize paper propagation only through the D11-aware paper audit.
- [x] Mark paper propagation verified against the committed D11-integrated
      paper.
- [x] Authorize D11 specification propagation through the hash-bound
      specification-extraction gate.
- [ ] Authorize runtime implementation.

## Iteration 11. D11 API, Notebook, And Browser UX

**Status:** candidate implemented and verified; human acceptance pending

### Goal

Make accepted D11 authority usable through the actual Python API, notebook,
and browser surfaces without rewriting historical ET-C0 through ET-C10
authority or satisfying downstream scientific obligations.

### Checks

- [x] Build a deterministic ET-C10-bound presentation bundle from
      `load_successor_forensic_context`.
- [x] Expose all 69 D11 authority entries: `2/2/2/12/13/31/7`
      claims/debts/profiles/candidates/objects/contracts/obligations.
- [x] Preserve 60 pure forensic API outputs byte-exactly in the browser bundle.
- [x] Use nine source-bound node projections only where there is no dedicated
      profile or verification-obligation forensic operation.
- [x] Add a real browser **D11** workspace with scope and kind filters, search,
      trace rows, source receipts, output digests, support relationships, and
      an explicit authority ceiling.
- [x] Keep inference, propagation, rerun prediction, and claim promotion out of
      JavaScript.
- [x] Add a separate runnable D11 notebook with six D11-C/D11-G9 recipes rather
      than changing the historical two-recipe ET-C3 notebook.
- [x] Require all six direct API, notebook, and browser results to be
      canonically byte-identical.
- [x] Add eight append-only ET-C11 UX scenarios without changing the accepted
      ET-C9 35-scenario contract or ET-C10 six-scenario contract.
- [x] Add Python and Node fail-closed tests for stale authority, missing views,
      count drift, trace tampering, and authority widening.
- [x] Run all 16 Playwright tests on desktop and mobile: four D11 executions
      plus 12 historical regression executions.
- [x] Visually inspect desktop provenance and mobile obligation views for
      clipping, unreadable authority status, or source/projection conflation.
- [x] Make the normal verification entry point rebuild, audit, run the
      notebook, run component tests, and run browser pressure for ET-C11.
- [x] Add build, audit, test, notebook, browser, and serve commands to the
      admitted dispatcher.
- [x] Update the plan, checklist, scenario contract, README, agentic guide, and
      D11 UX usage guide.

### Result

- D11 UX bundle: `records/ETC11D11SuccessorUXBundle.json`
- bundle digest:
  `59e8f37cf9fb61afdd1b999124e7c1842300c618fc33cb3c91ed0af0bfcfe39e`
- candidate record: `records/ETC11D11SuccessorUXCandidate.json`
- candidate record digest:
  `95b5f928c8b90eb9bdad6a788c72af871ce13c4f6daffe8c56db7dab5d2a3b5a`
- latest web-build manifest digest:
  `da11d3004b1448e614cf6f97c0d9bf66505709f867e1cc206538446303335e40`
- browser catalog: `69/69`
- direct forensic API outputs: `60`
- source-bound node projections: `9`
- notebook recipes: `6/6 API/notebook/browser byte-identical`
- Node component files: `5/5 passed`
- Playwright: `16/16 desktop/mobile executions passed`
- historical browser regressions: `12/12 passed`
- paper changed by ET-C11: `false`
- specifications or runtime changed by ET-C11: `false`
- GRC9 or GRC9V3 changed: `false`

### Gate

- [x] Implement and verify the `ET-C11-D11-UX` candidate.
- [ ] Record human acceptance of the ET-C11 UX candidate.
- [x] Record downstream D11 paper propagation through the existing paper
      audit without changing ET-C11 authority.

## Downstream D11 Specification Propagation

**Status:** verified; no runtime implementation authorized

- [x] Bind the phase authority to the committed D11-integrated paper and both
      accepted D11 decision digests.
- [x] Advance the boundary to `specification_propagation` while leaving `src/`,
      tests, GRC9, GRC9V3, the proposal, and the paper frozen.
- [x] Replace the provisional Candidate C and GRC9V4 expansion contracts only
      in the authorized V4 specifications, fixtures, manifest, extension, and
      registry.
- [x] Preserve the exact D11 claim subclasses and contract-specific support
      dispositions instead of flattening them into generic acceptance.
- [x] Make the normal verifier select the append-only D11 verification branch
      during `specification_propagation` and future authorized
      `implementation` phases.
- [x] Pass the phase-aware specification audit and the complete API, notebook,
      Node, and browser verification path.
- [ ] Authorize runtime implementation.
