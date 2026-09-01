# ET-C2 Validated Graph Kernel

**Status:** Accepted

Iteration 2 constructs a deterministic, source-traceable graph over the
accepted ET-C1 bundle. It does not add scientific authority or implement
forensic, counterfactual, or browser behavior.

## Result

- graph digest: `2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae`
- nodes: `436`
- propagation edges: `2666`
- display-only annotation edges: `4`
- invariants: `14/14 passed`
- source-owned populations: `39 current claims / 29 historical claims / 29 debt transformations / 11 verification obligations / 67 parent objects / 152 equation-contracts`
- gate records: `33`
- candidate nodes: `4`
- profile nodes: `10`
- realization rows: `20`
- physical source identities: `38`
- record digest: `10dc5cef2bffc764296cb9e38908cd1f992b9ce7c4c60d04a8ef6efda5d1453b`

## Semantic Boundary

Propagation and annotation rows are physically separate. Verification
obligations are forward-only work targets and are excluded from backward
evidence reconstruction. Source relations without explicit conjunction or
disjunction semantics remain `indeterminate_requires_review`; the kernel
does not infer `one_of` support from population shape.

SHA-only normative/runtime source identities remain valid source nodes.
A semantic record digest is required only where the source is itself a
decision record; no digest is synthesized for specifications or code.

## Acceptance Boundary

The independent raw-source auditor passed 117 checks and matched all
436 nodes and 2,670 relationships exactly. The focused kernel matrix
passed 14 fail-closed mutations, and deterministic rebuild checks passed.
These verification results were reviewed before gate acceptance.

ET-C2 is accepted at the validated-graph ceiling. Iteration 3 is
authorized, but forensic APIs remain unimplemented by this record.
