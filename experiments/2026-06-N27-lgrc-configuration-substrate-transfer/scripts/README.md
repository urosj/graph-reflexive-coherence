# N27 Scripts

Builder scripts for N27 artifacts belong here.

Current scripts:

```text
build_n27_source_inventory_and_transfer_contract_admission.py
build_n27_transfer_schema_and_controls.py
build_n27_active_nulls_and_failure_baselines.py
build_n27_minimal_configuration_transfer_probe.py
build_n27_topology_fixture_variant_transfer_probe.py
build_n27_transfer_side_effect_observation_probe.py
build_n27_replay_same_basin_mapping_matrix.py
build_n27_artifact_only_reconstruction_replay_probe.py
build_n27_transfer_side_effect_replay_probe.py
build_n27_stress_mapping_variant_transfer_matrix.py
build_n27_n28_precursor_side_effect_evaluation_matrix.py
build_n27_controls_ap_dependency_claim_classification.py
build_n27_n28_precursor_side_effect_claim_classification.py
```

Planned scripts:

```text
build_n27_closeout_and_n28_handoff.py
```

Scripts should:

```text
write deterministic JSON and Markdown artifacts
declare mappings before use
record source-current pre/post basin signature traces
record boundary mapping and support/coherence preservation
record artifact manifests with SHA-256 hashes
run fail-closed transfer, AP4/AP5, and claim-boundary controls
avoid local absolute paths
```

Scripts must not use semantic identity, choice, agency, native support,
sentience, Phase 8 completion, or ant ecology as evidence.
