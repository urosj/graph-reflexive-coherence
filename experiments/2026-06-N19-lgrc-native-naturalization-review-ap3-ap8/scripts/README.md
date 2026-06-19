# N19 Scripts

Deterministic builders and validators for N19 are written here.

Initial expected builders:

```text
build_n19_ap3_ap8_source_inventory.py
build_n19_naturalization_schema_v1.py
build_n19_candidate_classification_matrix.py
build_n19_phase8_readiness_matrix.py
build_n19_closeout_and_handoff.py
```

Initial expected validators:

```text
validate_n19_naturalization_row.py
```

Current builders:

```text
build_n19_ap3_ap8_source_inventory.py
build_n19_naturalization_schema_v1.py
```

Scripts should write only experiment-local outputs and reports. N19 must not
edit `src/*`.
