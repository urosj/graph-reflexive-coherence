# N20 Outputs

Generated N20 JSON artifacts belong here.

Expected artifact sequence:

```text
n20_source_method_inventory.json
n20_translation_schema_v1.json
n20_producer_residue_ledger.json
n20_native_function_proxy_contract.json
n20_same_basin_continuation_contract.json
n20_closeout_and_n21_handoff.json
```

Outputs must use relative paths only and must not contain local machine state.

Each output should include the N20 invariant block:

```text
primitive_evidence_opened = false
agency_claim_opened = false
phase8_opened = false
native_support_opened = false
sentience_opened = false
ant_ecology_spec_opened = false
src_diff_empty_required = true
```
