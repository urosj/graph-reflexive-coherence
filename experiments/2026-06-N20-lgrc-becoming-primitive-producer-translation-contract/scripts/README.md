# N20 Scripts

N20 scripts should reconstruct contract artifacts and reports.

Expected script sequence:

```text
build_n20_source_method_inventory.py
build_n20_translation_schema_v1.py
build_n20_producer_residue_ledger.py
build_n20_native_function_proxy_contract.py
build_n20_same_basin_continuation_contract.py
build_n20_closeout_and_n21_handoff.py
```

Scripts must write portable records, avoid local absolute paths, and keep
primitive evidence unopened until later experiments.

Scripts should fail closed if any primitive row lacks a complete contract,
opens an unsafe claim, omits an applicable AP4/AP5 gap, or uses local absolute
paths.
