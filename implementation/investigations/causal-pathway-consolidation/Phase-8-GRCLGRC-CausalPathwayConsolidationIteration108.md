# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 108

## Result

Iteration 108 passed as a directional composition and crossing-evidence matrix.

```text
composition rows = 26
lawful native = 10
lawful with explicit adapter = 1
diagnostic only = 2
producer mediated = 4
unsupported missing crossing = 3
invalid relabel = 6
selected crossing tests = 37 passed
runtime behavior changed = false
Iteration 109 ready = true
```

## Interpretation

I107 established source-and-test-grounded endpoints. I108 separately inspects
the relation between them. Endpoint tests are never counted as crossing
evidence. Native rows cite both source call/read semantics and a current test
that exercises the crossing. Missing relations remain unsupported; producer,
adapter, and diagnostic ownership remain visible; invalid promotions remain
blocked.

The matrix is representative rather than pairwise complete. It includes the
20 seed cases and six additional source-current crossings exposed by the I106
decomposition. Directionality is strict: no row implies its reverse.

Composition status is not maturity. A `lawful_native` crossing can remain
narrow, default-off, configured, or bounded by its recorded lifecycle and
portability evidence. Likewise, `unsupported_missing_crossing` records an
absent relation under the frozen source/evidence boundary; it is not automatic
authorization to implement a generic crossing.

## Remaining Boundary

Selection semantics, maintenance automation, and independent pressure-consumer
use remain I109-I111 work. No composition row establishes ecology, agency,
semantic choice, native Read-Back, or a universal causal-work API.
