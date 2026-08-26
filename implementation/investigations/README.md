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

- [GRC9V4 constitutive design](./grc9v4-constitutive-design/README.md):
  accepted bounded through D10.2. It closes the bounded current-population
  investigation of retained representation, continuation, directional
  Read-Back, current closure, write-back, realization, lifecycle, and
  substrate provenance. It earns the GRCv4-to-GRC9v4-to-disabled-GRC9v3
  factorization and authorizes GRCv4-first specification writing while leaving
  all runtime implementation unauthorized.
- [Causal-pathway consolidation](./causal-pathway-consolidation/README.md):
  accepted source-audit and I106-I111 supporting evidence for the completed
  documentation/conformance tranche. The essential plan, checklist, baseline
  freeze, and closeout remain at the `implementation/` root, and the
  reproducibility builders live under `scripts/`.
- [Event-local geometry integration](./event-local-geometry-integration/README.md):
  closed without runtime change after gated C0/C1 evidence exposed a recurring
  causal-work admission and ownership pattern. Its result motivated the
  separate GRC/LGRC causal-pathway contract-consolidation tranche.

Corrections to existing behavior remain under
[`implementation/corrections/`](../corrections/README.md). Active implementation
plans and checklists remain at the top level of `implementation/`.
