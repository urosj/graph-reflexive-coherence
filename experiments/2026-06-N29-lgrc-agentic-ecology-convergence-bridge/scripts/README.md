# N29 Scripts

N29 scripts will build deterministic demand, capability, coverage, motif,
prototype, and handoff artifacts.

Expected script families:

```text
build_n29_ecology_demand_*.py
build_n29_capability_atlas_*.py
build_n29_coverage_debt_*.py
build_n29_bridge_motif_*.py
build_n29_prototype_*.py
build_n29_composition_*.py
build_n29_closeout_*.py
```

Scripts must not write outside the N29 experiment tree unless a later
iteration explicitly defines a cross-repository handoff export.
