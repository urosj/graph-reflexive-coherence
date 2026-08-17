# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Checklist

**Status:** Reopened at Iteration 117. Checked Iteration 112-116 items describe
the pre-audit checkpoint and do not constitute current tranche acceptance.

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
- [ ] Re-run a new full independent adversarial audit after R4-B01 closes.
