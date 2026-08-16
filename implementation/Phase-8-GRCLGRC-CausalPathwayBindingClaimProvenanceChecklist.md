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
- [ ] Require composition-specific crossing evidence for B-03.
- [ ] Replace string-only candidate-use attestation for B-04.
- [ ] Enforce selection-scoped dynamic alternatives for B-05.
- [ ] Add the independent acceptance anchor for B-06.
- [ ] Add mechanism-specific effect outcome vocabulary for M-01.
- [ ] Re-run the independently updated full adversarial audit with zero blockers
      and zero unresolved majors.
