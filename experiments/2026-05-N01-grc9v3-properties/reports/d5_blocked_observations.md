# D5 Blocked Observations

| Observation | Status | Artifact Source | Reconstruction Attempt | Notes |
| --- | --- | --- | --- | --- |
| post-refinement flux window by old boundary edge | blocked | Experiment D persistence rows | Searched available D rows for per-edge post-event flux windows. | D exposes reassignment rows and child sink/basin runtime snapshots, not per-edge post-event flux windows. |
| checkpoint-window interface memory | inconclusive | Experiment D runtime-state persistence rows | Compared runtime persistence rows with persisted checkpoint requirement. | D5 uses experiment-local runtime snapshots; persisted checkpoint observer windows remain a later addendum. |
| dynamic interface memory for module-center endpoint | inconclusive | Experiment D child persistence rows | Joined reassignment endpoint node ids to persistent child sink nodes. | Module node 414 is a reassignment endpoint but is not a child sink row in the persistence table. |
| landscape-general interface memory | inconclusive | clean raw Experiment D fixtures | Reviewed fixture scope. | D5 inherits the clean raw fixture scope; landscape/seed robustness is not tested. |
