# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Checklist

**Status:** Iteration 118 complete; Iterations 119-125 planned and not started.
Checked Iteration 112-117 items retain their historical acceptance meaning.

## Global Boundaries

- [x] Use a separate tranche identity beginning at Iteration 112.
- [x] Keep Iterations 105-111 authoritative and unchanged.
- [x] Keep Event-Local Geometry Integration, N32, and RCAE L04 separate.
- [x] Preserve backward-compatible unbound runtime execution.
- [x] Prevent unbound execution from producing claim-qualified provenance.
- [x] Do not create a runtime dispatcher, intent router, or shared mechanism API.
- [x] Do not automate candidate promotion.

## Iteration 112: Pressure And Baseline

- [x] Freeze final accepted registry, crosswalk, matrix, selector, and policy digests.
- [x] Freeze current claim/reference and Iteration 111 authority hashes.
- [x] Freeze `src`, `tests`, and `examples` tree identities and aggregate hashes.
- [x] Verify protected source/test/example diff is empty.
- [x] Run accepted 20-rule consolidation conformance.
- [x] Run the 528-test focused GRC/LGRC suite before source change.
- [x] Run the 1,211-test full suite before source change.
- [x] Pressure admitted pathway-only use.
- [x] Pressure producer-mediated `CMP-20` use.
- [x] Pressure a distinct unregistered candidate.
- [x] Reject designs that require generic dispatch or implicit tracing.
- [x] Accept a verified mechanism-specific callable linker model.
- [x] Record no runtime/source behavior change in I112.

## Iteration 113: Binding Map And Minimal Linker

- [x] Add separate human and machine binding-symbol maps.
- [x] Map all 23 pathways and 52 stages to exact current source symbols.
- [x] Preserve multiple symbols/stages/pathways per source file.
- [x] Validate module, qualified symbol, call kind, and source hash.
- [x] Add immutable authority loading.
- [x] Add exact pathway binding.
- [x] Add exact registered-composition binding.
- [x] Reject unsupported and invalid compositions as admitted bindings.
- [x] Add explicit candidate declaration with authority/residue debt.
- [x] Add explicit allowed A/B alternatives and selection authority.
- [x] Add verified callable wrappers without generic execution dispatch.
- [x] Run focused I113 tests.

## Iteration 114: Use Graph, Lock, Receipt, And Claims

- [x] Freeze authority, source-link, declaration, residue, and claim data in a lock.
- [x] Require lock finalization before any claim-bearing bound invocation.
- [x] Record actual invoked pathway/stage/symbol and invocation outcome.
- [x] Build admitted and candidate-distinct use-graph nodes and edges.
- [x] Do not synthesize an edge from endpoint co-use.
- [x] Record declared-but-unused bindings.
- [x] Fail closed on bound use absent from the lock.
- [x] Link receipts to the exact lock digest.
- [x] Derive pathway-only claims from pathway authority.
- [x] Derive registered crossing claims from matrix authority.
- [x] Retain producer and adapter cuts.
- [x] Force candidate-containing envelopes to `experimental_unregistered`.
- [x] Prevent chained-composition ceiling synthesis.
- [x] Pressure dynamic A/B choice.

## Iteration 115: Conformance And Negative Controls

- [x] Add prospective binding conformance rules.
- [x] Add stale-to-pending-review handling for binding-map/symbol drift.
- [x] Add all 20 required deliberate negative controls.
- [x] Demonstrate target-only semantic rule isolation.
- [x] Classify unbound direct execution as non-qualified.
- [x] Run new focused tests.
- [x] Run affected GRC/LGRC tests.
- [x] Run accepted consolidation checker.
- [x] Run the full suite.
- [x] Verify no GRC/LGRC numerical behavior changed.

## Iteration 116: Consumer Dry Runs And Closeout

- [x] Exercise simple admitted pathway-only use.
- [x] Exercise producer-mediated `CMP-20`.
- [x] Exercise explicit adapter `CMP-26`.
- [x] Exercise diagnostic-only use.
- [x] Preserve ambiguous crossing non-selection.
- [x] Reject unsupported crossing as admitted.
- [x] Reject invalid relabel.
- [x] Exercise unregistered candidate use.
- [x] Exercise dynamic A/B declared alternatives.
- [x] Exercise multi-edge use graph without claim synthesis.
- [x] Freeze and validate one low-context replay with a separate oracle.
- [x] Add the Knowledge/Binding/Execution reference guide.
- [x] Update contribution, reference, specification, and implementation indexes.
- [x] Run `ruff`, `mypy`, compile checks, `git diff --check`, and final tests.
- [x] Publish closeout with exact remaining boundaries.

## Iteration 117: Independent Audit Corrections

- [x] Preserve the audited candidate at checkpoint commit `976c660`.
- [x] Reopen the tranche and supersede the pre-audit closeout.
- [x] Freeze a correction contract for B-01 through B-06, M-01, and N-01.
- [x] Scope locks and receipts to recorded bound invocations.
- [x] Disclaim whole-run closure and untracked-execution observability.
- [x] Freeze definition-level callable identities in locks and receipts.
- [x] Re-resolve callable identity immediately before every invocation.
- [x] Reject post-load and post-lock P1-to-P2 substitution before delegation.
- [x] Extend BCF-016 and BCF-020 for callable identity and receipt scope.
- [x] Regenerate I115/I116 evidence with the corrected schema.
- [x] Run focused tests, both conformance checkers, lint, typing, and full suite.
- [x] Require ordered composition-specific crossing evidence for B-03.
- [x] Bind CMP-26 source and target stages through the real registered adapter
      object flow.
- [x] Reject endpoint-only, missing-adapter, and forged-adapter composition
      evidence.
- [x] Replace string-only candidate-use attestation with pre-lock,
      content-addressed mechanism evidence for B-04.
- [x] Require candidate-specific constituent execution scopes and reject
      unscoped endpoint co-use.
- [x] Reject renamed invalid-relabel restatements and require a distinct
      mechanism for candidates over known invalid endpoint pairs.
- [x] Extend BCF-004 and BCF-011 to reconstruct candidate evidence and
      invalid-row conflicts independently.
- [x] Enforce consumer-owned selection scopes for dynamic alternatives in
      B-05.
- [x] Reject an out-of-set pathway or a second alternative before delegation.
- [x] Preserve unrelated bound work outside the selection scope.
- [x] Extend BCF-017 to reconstruct exact scope and invocation witnesses.
- [x] Add the independent acceptance anchor for B-06.
- [x] Add mechanism-specific effect outcome vocabulary for M-01.
- [x] Run the second independent adversarial audit; record its
      `reject_pending_correction` disposition and three round-two blockers.

## Round-Two Independent Audit Corrections

- [x] R2-B01: require exact runtime dataflow closure for every registered
      composition edge.
- [x] Preserve CMP-26's exact adapter-source/result-reference flow rule.
- [x] Require non-explicit compositions to share one exact directly bound
      runtime owner across a qualifying source/target invocation pair.
- [x] Keep CMP-04 declared-but-unused when its ordered endpoint calls act on
      unrelated runtime objects.
- [x] Extend BCF-019 and add runtime/checker adversarial controls for forged or
      unrelated object flow.
- [x] R2-B02: require candidate-specific mechanism execution and close semantic
      invalid-relabel paraphrases.
- [x] Reject metadata-only candidate evidence and freeze one exact executable,
      source, definition, and callable identity before lock.
- [x] Require exactly one returned candidate-mechanism invocation inside its
      completed scope and, for compositions, between source and target calls.
- [x] Reject candidate mechanisms that alias an admitted stage or registered
      crossing callable.
- [x] Retain exact invalid-row conflicts and blocked relabels structurally;
      classify proposed relation prose as descriptive and non-claim-qualified.
- [x] Extend BCF-004/BCF-011 and runtime controls for missing, forged,
      metadata-only, and semantically paraphrased candidate evidence.
- [x] R2-B03: independently canonicalize every claim-envelope field.
- [x] Derive the lock envelope from current authority and exact declarations,
      without consulting the submitted envelope.
- [x] Derive the receipt envelope from qualifying invocations, valid
      composition witnesses, and valid candidate-mechanism witnesses.
- [x] Require exact structural equality for every constituent, qualifier,
      status, flag, aggregate block, and non-synthesis field.
- [x] Canonicalize top-level blocked-claim and producer/adapter projections
      against the same independently derived envelope.
- [x] Add target-only BCF-015 controls for every top-level/qualifier envelope
      field, the exact audit diagnostic widening, ownership-cut deletion, and
      replay-block deletion.
- [ ] Re-run a new full independent adversarial audit with zero blockers and
      zero unresolved majors against the complete author-corrected branch.

## Round-Three Independent Audit Corrections

- [x] Record the round-three `reject_pending_correction` disposition: R3-B01,
      R3-B02, and R3-M01.
- [x] R3-B01: digest the lock-linked raw execution transcript independently of
      its witness, graph, and claim-envelope projections.
- [x] Require an externally supplied trusted transcript digest before BCF-019
      accepts any registered composition witness.
- [x] Reproduce the coordinated CMP-20 runtime-instance/object-flow rewrite,
      reseal both artifacts, and prove it cannot reuse the honest digest.
- [x] R3-M01: freeze an independently derived stage/port dataflow contract for
      every executable composition row.
- [x] Cover module-function arguments/results for CMP-01, CMP-02, CMP-03,
      CMP-04, CMP-17, and CMP-21.
- [x] Add a consumer-bound, equivalent-state-copy target reference so CMP-04
      is executable without binder dispatch or a false object-identity claim.
- [x] Regenerate I115/I116 evidence; exercise CMP-04 as a diagnostic-only edge.
- [x] R3-B02: require independently reviewed structural distinction for a
      candidate over an invalid endpoint pair; a synonym/no-op candidate must
      not produce an exercised edge.
- [x] Bind the external review to the exact candidate, endpoints, relation,
      invalid-row blocks, and mechanism content address.
- [x] Require a distinct nonempty mapping result and retain its review digest
      and structural predicate in the raw execution transcript.
- [x] Reject the exact synonym-renamed `return None` mechanism at runtime and
      under coherently resealed checker artifacts with all trust inputs.
- [x] Retain the trusted review in candidate receipt and graph projections.
- [x] Re-run a full independent adversarial audit after R3-B02 closes; record
      its round-four `reject_pending_correction` disposition.

## Round-Four Independent Audit Correction

- [x] Record the round-four `reject_pending_correction` disposition with the
      remaining R4-B01 reviewed-candidate continuity blocker.
- [x] Preserve `target(**request)` while exposing reviewed candidate results as
      read-only provenance-carrying JSON mappings.
- [x] Record source-result to candidate-argument identity in the raw candidate
      invocation and candidate-result to target-request derivation in the raw
      target invocation.
- [x] Require the reviewed candidate witness to identify exact source,
      candidate, and target invocation indices plus matching runtime-object and
      canonical request digests.
- [x] Make BCF-011/BCF-019 independently reconstruct the complete raw flow
      before accepting the experimental edge.
- [x] Cover the flowed mapping, ignored mapping with equivalent hard-coded
      arguments, and coherently resealed missing-flow transcript controls.
- [x] Re-run a full independent adversarial audit after R4-B01 closes; record
      its round-five `reject_pending_correction` disposition.

## Round-Five Independent Audit Correction

- [x] Record R4-B01 as independently closed and R5-B01 as the remaining
      source-role continuity blocker.
- [x] Version the trusted relation review to v2 and bind the source role to one
      exact `source_result_parameter`.
- [x] Require that parameter to exist in the pinned candidate callable before
      runtime execution.
- [x] Require the qualifying source-result descriptor at that exact argument;
      do not search arbitrary candidate arguments for a matching object.
- [x] Make the checker prove that the pinned nonempty mapping return references
      the reviewed parameter and that the raw witness uses the same name.
- [x] Cover the honest reviewed source parameter, the exact unused-`context`
      decoy, and a coherently resealed checker transcript naming `context`.
- [ ] Re-run a new full independent adversarial audit after R5-B01 closes.

## Round-Six Independent Audit Correction

- [x] Record R5-B01 as independently closed and R6-B01 as the remaining
      semantic source-dependence blocker.
- [x] Bind the dependency proof to the exact candidate-result submapping used
      as the target request, not to an arbitrary source mention elsewhere.
- [x] Safely derive source-present and source-absent canonical request digests
      from the pinned candidate definition and require them to differ.
- [x] Require the source-present digest to equal the request observed at the
      declared target invocation.
- [x] Freeze the proof path, reviewed parameter, and both digests in the raw
      request-flow transcript.
- [x] Make the checker independently reconstruct the same proof from pinned
      source and reject unsupported or degenerate expressions.
- [x] Cover honest flow and the exact equal-branch Round 6 falsifier at both
      runtime and checker surfaces.
- [ ] Re-run a new full independent adversarial audit after R6-B01 closes.

## Round-Seven Independent Audit Correction

- [x] Record R6-B01 as independently closed and R7-B01 as the remaining
      omission-oracle blocker.
- [x] Replace synthetic `None` absence with the reviewed parameter's exact
      frozen callable default.
- [x] Require the default to be safely reconstructable and to match the loaded
      callable signature; fail closed for required or unsupported defaults.
- [x] Version the raw proof and freeze the default, source-present request, and
      source-omitted request digests.
- [x] Require the live request to match the present digest and differ from the
      real omitted-request digest.
- [x] Make the checker independently reconstruct the frozen default and omitted
      request from content-addressed source.
- [x] Cover honest `default=None`, exact `default=1`, missing-default, and
      unsafe-default controls while retaining all Round 6 pressures.
- [x] Re-run a full independent adversarial audit after R7-B01 closes (Round
      8: 56 passed, 2 failed, 0 errors; R8-B01 isolated).

## Round-Eight Independent Audit Correction

- [x] Record the scalar-default R7-B01 case as independently closed and R8-B01
      as the remaining type-erasing omission blocker.
- [x] Evaluate AST list and tuple literals as their distinct Python types.
- [x] Bind the source default to a recursive type-preserving digest at both the
      loaded runtime signature and independent checker surfaces.
- [x] Admit only `None`, scalar, list, tuple, and string-keyed mapping defaults
      whose nested values can be represented without type loss.
- [x] Apply canonical request serialization only after Python expression
      evaluation; type-sensitive equality and concatenation must agree with
      direct Python or fail closed.
- [x] Cover the exact tuple/list falsifier, the frozen supported-default matrix,
      recursive type distinctions, and unsupported concatenation.
- [x] Re-run the supplied 58-case Round 8 independent adversarial audit.
- [x] Obtain a new full independent audit after R8-B01 closes (Round 9:
      `accept`, 68 passed, 0 failed, 0 errors, no findings).

## Post-Acceptance Callable-Identity Cache

- [x] Cache each resolved source path, successful SHA-256 verification,
      definition identity, and canonical callable-identity record per session.
- [x] Preserve per-invocation registered-symbol re-resolution and callable
      object-identity checks.
- [x] Use `(st_mtime_ns, st_size)` as the unchanged-source fast-path guard.
- [x] Re-hash before delegation on stamp drift and reject mismatched content.
- [x] Refresh the cached stamp only after identical pinned content re-verifies.
- [x] Cover unchanged cache hits, identical-content stamp invalidation, and
      changed-content refusal without mutating repository files in tests.

## Iterations 118-125: Modular Binder Architecture And Guidance

Execute each iteration with a clean checkpoint commit before proceeding to the
next.

## Iteration 118: Compatibility And Refactor Baseline

- [x] Treat Iterations 118-125 as a refactor and usability tranche; preserve
      the accepted mechanism-specific architecture and
      `semantic_selection_performed_by_binder = false` boundary.
- [x] Freeze before-refactor public symbol names, import paths, class/function
      and method signatures, exception types and important conditions,
      context-manager behavior, and return object types in a machine-readable
      `I118PublicAPICompatibilityFreeze.json` or equivalent.
- [x] Freeze before-refactor canonical bytes and digests for the full practical
      accepted I115/I116 binder fixture corpus.
- [x] Cover native pathways; producer, adapter, and diagnostic compositions;
      dynamic choice; candidate pathways and compositions; reviewed
      invalid-pair candidates; unused declarations; non-qualifying and raised
      effects; negative controls; and multi-edge graphs in that corpus.
- [x] Add public behavioral-API compatibility, runtime-observation, and full
      practical-corpus golden-byte tests before moving production code.
- [x] Add a guard that prevents the independent binding conformance checker
      from importing load-bearing binder derivation or validation logic.
- [x] Record the pre-refactor focused and full-project baselines using the
      repository `.venv`; do not change binder runtime code in this iteration.

## Iteration 119: Package Boundary And Identity Foundation

- [ ] Atomically replace `binding.py` with the `binding/` package; never leave
      the same import name present as both a module and package.
- [ ] Preserve the unchanged monolith temporarily as a private implementation
      module behind `binding/__init__.py` so package creation and semantic
      extraction remain separate reviewable changes.
- [ ] Establish `binding/__init__.py` as the compatibility facade and add the
      first permanent provider module, `identity.py`; later iterations complete
      the target package.
- [ ] Preserve every existing public export from `pygrc.causal_pathways` and
      behavioral compatibility from `pygrc.causal_pathways.binding`; mark new
      internal module paths explicitly non-contractual.
- [ ] Extract canonical digests, source verification, callable identities,
      source-symbol and crossing bindings, source manifests, and cached
      callable guards into `identity.py` without claim interpretation.
- [ ] Move tests away from private monolith patch points such as
      `binding.inspect` and `binding._load_json`; do not add them to the public
      compatibility contract.
- [ ] Pass the focused binder, API-freeze, golden-corpus, conformance, and
      static gates before continuing.

## Iteration 120: Effects And Authority

- [ ] Extract effect contracts, return/effect classification, evidence, and
      genuinely effect-level runtime descriptors into `effects.py`.
- [ ] Extract authority and acceptance-anchor loading, admission lookup,
      source-map semantics, accepted effect contracts, and staleness into
      `authority.py`; keep loaded authority state mostly immutable.
- [ ] Establish and test the permanent dependency chain `identity -> effects
      -> authority` without changing session behavior.
- [ ] Pass the focused binder, API-freeze, golden-corpus, conformance, and
      static gates before continuing.

## Iteration 121: Candidate Subsystem

- [ ] Make candidate declarations, relation reviews, request provenance,
      invalid-relabel constraints, source-consumption proofs, omission
      counterfactuals, typed defaults, and witnesses the responsibility of the
      first-class `candidates.py` subsystem.
- [ ] Move verified candidate mechanisms, candidate request wrappers, AST and
      type-preserving default evaluation, and candidate execution proof
      primitives into that subsystem.
- [ ] Introduce only the narrow factory or recorder protocol required to avoid
      candidate/session/scope cycles; do not introduce a concrete session
      dependency.
- [ ] Replay the candidate-focused R4-B01 through R8-B01 regressions and
      candidate mutation falsifiers before continuing.
- [ ] Pass the focused binder, API-freeze, golden-corpus, conformance, and
      static gates before continuing.

## Iteration 122: Runtime Scopes And State Ownership

- [ ] Extract invocation, crossing, and candidate records; crossing and
      flow-derived references; and composition, alternative-selection, and
      candidate execution scopes into `scopes.py`.
- [ ] Give invocation ledgers, object-flow identity, and active-scope state
      cohesive owners instead of retaining unrelated mutable fields on one
      class.
- [ ] Replace cross-object `_`-attribute reads and broad session fan-out with
      narrow internal collaborator methods or protocols.
- [ ] Keep concrete `PathwayBindingSession` dependencies out of scope, effect,
      and artifact collaborators; scopes use narrow recorder/provenance
      protocols.
- [ ] Replay composition-flow, dynamic-choice, producer/adapter-owner, and
      endpoint-co-use-without-flow pressures before continuing.
- [ ] Pass the focused binder, API-freeze, golden-corpus, conformance, and
      static gates before continuing.

## Iteration 123: Artifacts And Session Consolidation

- [ ] Complete the internal package with `identity.py`, `effects.py`,
      `authority.py`, `candidates.py`, `scopes.py`, `artifacts.py`, and
      `session.py` behind the compatibility `binding/__init__.py`.
- [ ] Extract lock, receipt, pathway-use graph, execution-transcript digest,
      claim-envelope, and canonical serialization construction into
      `artifacts.py` as near-pure operations over immutable records.
- [ ] Keep identity free of claim interpretation, authority mostly immutable,
      artifact derivation near-pure over immutable records, and session limited
      to orchestration.
- [ ] Reduce `session.py` to phase control, declarations, linking, active-scope
      orchestration, runtime-state ownership, binding handles, freeze, and seal.
- [ ] Give phase, declaration, link, and artifact state cohesive owners within
      the remaining orchestration boundary.
- [ ] Remove the temporary monolith.
- [ ] Freeze and test the complete dependency-provider-first order: `identity
      -> effects -> authority -> candidates -> scopes -> artifacts -> session`;
      each module may import only preceding layers, though it may skip layers.
- [ ] Keep the independent binding conformance checker independently
      implemented after extraction; schemas and harmless constants may be
      shared, but load-bearing derivations may not.
- [ ] Pass the focused binder, API-freeze, golden-corpus, conformance, and
      static gates after removing the temporary monolith.
- [ ] Run the full project suite after the production refactor becomes
      structurally complete.

## Iteration 124: Binder Examples And Guidance

- [ ] State prominently that `bound_invocations_only` receipts certify only
      represented bound operations, not whole-run causal closure or the absence
      of unbound influences.
- [ ] Add runnable examples for an admitted pathway, registered composition,
      explicit dynamic choice, conservative unregistered candidate flow, and
      valid direct-unbound/non-claim-qualified use.
- [ ] Build the user-and-agent guide around `select -> bind -> lock -> execute
      -> seal -> validate`, with selection consumer-owned and candidate
      declaration leading only to experimental provenance.
- [ ] Cover authority loading, declarations, scopes, conformance, failure
      interpretation, debugging, and safe extension practices in the guide.
- [ ] Revise the binding reference guide for the stable public API and exact
      artifact schemas without making internal module layout contractual.
- [ ] Describe the final candidate contract directly in stable guidance; keep
      R4-B01 through R8-B01 chronology in implementation and audit evidence.
- [ ] Update the root README, docs indexes, claim-boundary index, examples
      index, specs index, and any new local example/reference indexes.

## Iteration 125: Independent Pressure And Closeout

- [ ] Recheck the complete public behavioral API freeze after all refactoring.
- [ ] Confirm artifact schema versions, field names and values, canonical
      ordering, serialized bytes, and digests remain unchanged.
- [ ] Confirm runtime state, results, return types, exception behavior, and
      context-manager behavior remain unchanged for identical bound executions.
- [ ] Compare the full practical before/after corpus byte-for-byte, including
      locks, receipts, conformance results, negative controls, schemas, field
      ordering, and digests.
- [ ] Compare bound-before and bound-after runtime state and results.
- [ ] Replay mutation falsifiers for owner erasure, symbol substitution,
      candidate promotion, prohibited relabels, unsupported composition,
      dynamic branching, claim widening, endpoint co-use without flow,
      hard-coded or source-unused candidate requests, and stale source content;
      require the relevant independent gates to fail closed.
- [ ] Run all binder examples and focused binding/conformance/I116 tests.
- [ ] Run the full project suite (current baseline: 1,320 tests).
- [ ] Replay the accepted 68-case independent semantic gate.
- [ ] Pass both 20-rule conformance policies, Ruff, mypy, compileall, and
      `git diff --check` before closing Iteration 125.
- [ ] Close only with zero semantic, artifact, or runtime differences
      attributable to the refactor.
