# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 115

**Status:** Passed

## Result

Iteration 115 adds prospective machine conformance for binding locks, receipts,
use graphs, and claim envelopes, with one deliberate fail-closed mutation and
one target-only isolation run for every rule.

```text
binding conformance rules = 20 / 20 passed
deliberate negative controls = 20 / 20 failed closed
target-only rule-isolation controls = 20 / 20 failed closed
failed-open controls = 0
binding source drift = stale_pending_review and claims blocked
accepted consolidation conformance = 20 / 20 passed
affected GRC/LGRC tests = 528 / 528 passed
full repository tests = 1,234 / 1,234 passed
runtime numerical behavior changed = false
```

## Prospective Enforcement

The binding conformance policy freezes the accepted registry, crosswalk,
matrix, selector, consolidation policy, and binding-map digests. The checker
validates current binding-map stage closure, every concrete symbol and source
hash, exact lock and receipt digests, exact lock-to-receipt identity, declared
and actual stage/symbol use, declared-but-unused reporting, composition-stage
exercise, use-graph closure, and conservative claim projections.

The semantic rules separately enforce admitted pathway and composition
identity, explicit candidate identity, candidate non-promotion, producer and
adapter ownership, diagnostic boundaries, configured-versus-formed route
semantics, arbitration-versus-candidate-formation semantics, unsupported and
invalid crossings, allowed dynamic alternatives, ambiguity non-selection,
chain non-synthesis, and unbound non-qualification.

Binding-map, source-symbol, or source-file drift yields:

```text
binding_staleness_state = stale_pending_review
claim_qualified_artifacts_blocked = true
```

The binding layer cannot self-readmit after drift. Current versioned authority
and evidence review remain prerequisites to a successor binding map or policy.

## Negative Controls

The 20 controls correspond directly to the required adversarial cases:

1. unknown pathway;
2. unknown composition;
3. unregistered relation without a candidate;
4. candidate described as native/promoted;
5. erased CMP-20 producer identity;
6. erased explicit adapter identity;
7. diagnostic-as-behavioral relabel;
8. configured-as-formed route relabel;
9. arbitration-as-candidate-formation relabel;
10. unsupported crossing treated as existing;
11. invalid relabel reused as candidate identity;
12. stale registry digest;
13. stale matrix digest;
14. stale binding/source-symbol digest;
15. undeclared receipt symbol;
16. wrapper pathway mismatch;
17. undeclared dynamic branch;
18. binder ambiguity resolution;
19. synthesized chained-composition claim;
20. unbound claim-qualified evidence.

Every mutation first runs against the full checker. It then runs with only its
target `BCF-*` rule active, so an unrelated lock/receipt digest finding cannot
stand in for the semantic rejection. All 20 isolated controls reject through
their intended rule.

## Frozen Evidence

The positive prospective fixture is a real explicit-packet lock and receipt
created by the public binding API. The policy, fixture, execution record, and
negative-control record are frozen under
`implementation/evidence/causal-pathway-binding/` and validate canonically.

## Verification

```text
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_binding_conformance.py
  = 20 passed, 0 issues
.venv/bin/python scripts/check_grc_lgrc_causal_pathway_conformance.py
  = 20 passed, 0 issues
PYTHONPATH=src .venv/bin/python -m unittest -q
  focused binding/conformance/import modules = 24 passed
PYTHONPATH=src .venv/bin/python -m unittest -q
  20 accepted affected GRC/LGRC modules = 528 passed in 6.781 seconds
PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
  = 1,234 passed in 223.028 seconds
.venv/bin/ruff check selected source/tests/scripts = passed
.venv/bin/mypy --python-version 3.12 selected source/tests/scripts = passed
```

The historical I107 execution record names `pytest`, but `pytest` is not a
declared `pyproject.toml` dependency. The accepted I115 rerun therefore uses
the repository's available `unittest` runner in `.venv`, matching the I112
baseline environment and exercising the same 20 modules and 528 tests.

No GRC9V3 or LGRC9V3 mechanism source changed. Iteration 116 still owns the ten
consumer dry runs, blind low-context replay, reference/contribution guidance,
indexes, and final closeout verification.
