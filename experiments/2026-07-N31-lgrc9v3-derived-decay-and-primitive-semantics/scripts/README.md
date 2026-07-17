# N31 Scripts

No N31 execution script is admitted yet.

Scripts should be deterministic, use repository-relative paths, consume exact
source artifacts, and keep candidate-specific topology and invariants explicit.
Experiment scripts may construct fixtures and invoke public runtime operations;
they must not modify `src/` or implement hidden load-bearing D0 decay updates.
