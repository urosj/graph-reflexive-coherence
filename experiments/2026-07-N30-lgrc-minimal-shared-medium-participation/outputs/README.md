# N30 Outputs

Selected N30 output artifacts will be stored here when they are part of the
historical evidence record.

## Iteration Artifacts

- `n30_source_inventory_i1.json`: source inventory and method admission. It
  pins shared-medium method documents by digest and keeps positive N30 evidence
  closed.
- `n30_schema_control_freeze_i2.json`: participant/medium schema freeze. It
  freezes P0-P7, M0-M6, N30-C0-N30-C6, required candidate fields, controls,
  replay gates, medium debt, and claim boundaries.
- `n30_active_nulls_i3.json`: active-null and failure-baseline matrix. It
  instantiates the I2 control IDs, maps each null to a blocked gate/rung and
  dependent hypothesis, and keeps positive N30 evidence closed.
