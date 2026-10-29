# C_PC sixth-realization evidence

The Phase 9 web view includes a C_PC section for P9-8.4d through P9-9.6.
Use its refresh button to check the retained evidence and inspect all sixteen
checkpoint rows. The existing A_OS section continues to show the accepted
fifth realization. The project remains on `work/p9-aos-tranches-8-9`.

`GET /api/cpc` returns the checked scope, checkpoint evidence, inherited limits,
and source index. `GET /api/cpc/source?path=...` reads only an indexed repository
source and verifies its SHA-256. Both endpoints are read-only, reject extra or
ambiguous query parameters, and clear successful presentation on a failed
refresh. Source drift fails closed. File presence during a campaign is shown
only as pending progress, never as a passing checkpoint.

The notebook's `query-cpc` cell uses the same API model. Run the real cell with
`python scripts/run_phase9_notebook.py --cpc-only` from the tool directory using
the repository environment. The runner checks the cell against the API model
and emits `PHASE9_CPC_NOTEBOOK_PASS`.

C_PC's bounded results were explicitly accepted on 2026-10-29. The separate
acceptance decision binds implementation commit `1e720983`, preserving the
original review and validation records. All sixteen checkpoint rows are
accepted. The current compatibility view has 24 accepted cells and sixteen
unselected cells; the original execution matrix remains intact. Original large C_PC target histories are
excluded; the separately declared companion is identified in the scientific
review. Optional completion, C_PC basin migration, Tranche 10, and full GRC9V4
conformance are not granted by this view.
