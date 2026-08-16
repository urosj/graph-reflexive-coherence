# Implementation Investigations

This directory contains bounded engineering investigations that inspect current
runtime contracts, execute gated evidence, and shape later implementation or
conformance work without themselves changing runtime behavior.

An investigation belongs here when it:

- studies an implementation boundary or candidate extension;
- preserves source, test, and example behavior;
- records positive or negative evidence under explicit gates;
- closes without claiming that the investigated runtime mechanism was added;
- may motivate a separate implementation, specification, or consolidation
  tranche.

Current investigations:

- [Event-local geometry integration](./event-local-geometry-integration/README.md):
  closed without runtime change after gated C0/C1 evidence exposed a recurring
  causal-work admission and ownership pattern. Its result motivated the
  separate GRC/LGRC causal-pathway contract-consolidation tranche.

Corrections to existing behavior remain under
[`implementation/corrections/`](../corrections/README.md). Active implementation
plans and checklists remain at the top level of `implementation/`.
