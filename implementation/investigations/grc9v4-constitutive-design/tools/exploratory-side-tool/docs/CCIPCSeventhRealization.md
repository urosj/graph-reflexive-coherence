# C_CI+PC seventh realization in the Phase 9 side-tool

C_CI_PC continues on `work/p9-aos-tranches-8-9`, after the accepted C_PC sixth
realization. The new panel covers sixteen checkpoint rows from P9-8.4d through
applicable P9-9.6. C_CI_PC's earlier G2, P9-8.3 and P9-8.4b/c acceptance and all
six completed predecessors remain separate.

The read-only `/api/ccipc` endpoint, browser panel and `query-ccipc` notebook
cell consume retained evidence. Before the complete checked review exists,
rows remain pending; file presence alone grants no execution credit. A complete
review retains `passed_pending_acceptance`. The explicit user decision on
2026-10-29 accepts implementation `f90c5344`; the API, browser and notebook
project all sixteen rows as `bounded_accepted` while preserving the original
execution and validation bytes. Acceptance is never inferred from passing tests.

Source links use `/api/ccipc/source?path=...` and the checked source index.
Unknown paths, directory escapes, duplicate parameters and source drift fail
closed. The browser clears stale results on failure; the notebook clears its
result before loading new evidence. API and notebook reads do not run native
trajectories. A clean checkout restores the deep preflight from its verified
compressed artifact without overwriting changed local bytes.

The large fixture history distinguishes three subjects:

- The frozen original target has independently proved negative resources in
  both histories and no native credit.
- The first companion passes initial feasibility, but its actual evolved split
  loses `2^-53` of represented current charge. Its prepared-target steps remain
  separate evidence.
- The selected `(5/16, 5/16, 3/8)` companion preserves both actual charges. Only
  its unchanged source steps are reused by exact digest; target evidence uses
  separate `CCIPCCharge` paths and unchanged tolerances.

Large native caps are one hour per segment. FLINT/Arb, verified matrix/schema/
canonical-byte reuse, vertex-reduced independent equations and resumable
segments support the campaign. Thirty saved-input physical-update enclosures
are pointwise bounds, not a uniform exact-trajectory claim.

The compatibility execution matrix has 24 accepted predecessor cells, four
new passing cells pending acceptance, and twelve unselected cells. The accepted
view separately reports 28 accepted / 0 pending / 12 unselected cells. The four
new disabled compatibility authorities remain `indeterminate_requires_review`.
Expanded-target compatibility, optional completion, basin support, all-ten
closure and Tranche 10 are not inferred from this bounded implementation.

Use `tool/scripts/run_phase9_notebook.py --ccipc-only` for the focused notebook
check. The retained review and validation programs live in
`implementation/phase-9-grcv4/verification/p9_ccipc_review.py` and
`validate_ccipc.py`; status inspection uses the cheap integrity checker.


The large covariance subset is prioritized: `combined`, `reflect`, then
`rotate`, each with both histories. The separate `edge_order`, `node_order`,
`relabel`, `signed` and `rotate_twice` large events remain deferred and
unexecuted unless a failure calls for diagnosis. Full small covariance coverage
is retained. The review's large scope and counts expose this distinction.
