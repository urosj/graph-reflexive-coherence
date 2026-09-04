# ET-C10 D11 Forensic Admission

Status: **accepted**

ET-C10 admits the eight hash-bound D11 JSON records through an append-only
successor layer. It does not rewrite the historical ET-C0 source contract,
ET-C1 bundle, ET-C2 graph, or the accepted ET-C3 through ET-C9 artifacts.

## Accepted identities

- D11 source-contract digest:
  `afab36a86604fcea50332375781be3c82427e72e3e8c10d7f2cb9c7814f40f81`
- D11 source-bundle digest:
  `98c273b3cc097f0d95adfba98ed7dfac0ac494dce9e779bb4b04fe79fef4f6aa`
- D11 graph digest:
  `44d8c7d33950af5e5f7c61caa4fe6fbd14fc9aedf14218d0a11de7c705542e09`
- ET-C10 admission digest:
  `833acc5988761f8ba68ca573ad270bf7c87cf2fe32061336a71e42647968630a`
- Immutable historical ET-C2 graph digest:
  `2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae`

## Admitted successor population

ET-C10 adds two current claims, two local debt transformations, seven forward
verification obligations, 13 normative objects, and 31 equation contracts.
The combined graph therefore contains 41 current claims, 29 historical claims,
31 debt transformations, 18 verification-obligation nodes, 80 normative
objects, and 183 equation contracts. Seventeen obligations remain pending:
the ten carried D10 obligations plus the seven new D11 obligations.

The D11-C and D11-G9 local debts are queryable as lifecycles. Their accepted
design-level resolutions and their still-forward paper, specification, and
runtime obligations remain distinct rows.

Six append-only successor scenarios (S1-S6) exercise the D11 claims, debts,
objects/contracts, dual-loader boundary, and two-state paper audit. The
historical ET-C9 35-scenario contract and receipt remain byte-identical.

## Query boundary

Use `load_successor_forensic_context` for the current post-D11 authority graph.
Use `load_forensic_context` only for an explicitly historical D10/ET-C2 query.
Both loaders fail closed on source or graph identity drift.

ET-C10 does not establish paper propagation, specification propagation,
implementation conformance, or any GRC9/GRC9V3 repair. Those remain outside
this tooling admission.
