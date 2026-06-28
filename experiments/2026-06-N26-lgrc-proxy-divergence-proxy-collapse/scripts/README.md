# N26 Scripts

Builder scripts for N26 artifacts belong here.

Current scripts:

```text
build_n26_source_inventory_and_scoped_substrate_admission.py
build_n26_proxy_divergence_collapse_schema_and_controls.py
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
