# N26 Scripts

Builder scripts for N26 artifacts belong here.

Current scripts:

```text
build_n26_source_inventory_and_scoped_substrate_admission.py
build_n26_proxy_divergence_collapse_schema_and_controls.py
build_n26_active_nulls_and_failure_baselines.py
build_n26_source_current_proxy_derivation_probe.py
build_n26_proxy_derivation_sensitivity_probe.py
build_n26_proxy_divergence_contrast_matrix.py
build_n26_alternative_proxy_surface_divergence_probe.py
build_n26_fixed_surface_divergence_search.py
build_n26_same_route_score_dose_divergence_probe.py
build_n26_proxy_collapse_perturbation_matrix.py
build_n26_replay_controls_and_ap5_gate.py
build_n26_closeout_and_n27_handoff.py
render_n26_proxy_divergence_collapse_visualization.py
```

Scripts should:

```text
write deterministic JSON and Markdown artifacts
declare proxy metrics and target digests before use
consume N25.2 only as scoped MB6 substrate evidence
record artifact manifests with SHA-256 hashes
run fail-closed proxy, AP5, and claim-boundary controls
avoid local absolute paths
```

Scripts must not use semantic goals, choice, intention, agency, native support,
sentience, Phase 8 completion, or ant ecology as evidence.
