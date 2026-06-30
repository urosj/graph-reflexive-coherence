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

Current scripts:

```text
build_n29_ecology_demand_extraction_i1.py
build_n29_agency_diagnostic_method_constraints_i2.py
build_n29_capability_atlas_i3.py
build_n29_bridge_schema_i4.py
build_n29_ecology_demand_matrix_i5.py
build_n29_capability_supply_atlas_i6.py
build_n29_demand_supply_coverage_debt_i7.py
build_n29_bridge_motif_library_i8.py
build_n29_motif_relabel_nulls_i9.py
build_n29_prototype_admission_schema_i10.py
build_n29_trace_pressure_loop_prototype_i11.py
build_n29_trace_pressure_loop_runtime_i11a.py
build_n29_trace_pressure_loop_runtime_controls_i11b.py
build_n29_trace_pressure_loop_replay_stress_i11c.py
build_n29_trace_pressure_loop_stronger_i111.py
```
