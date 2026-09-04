# GRCv4 Exploratory Side Tool D11 UX Scenarios

**Date:** 2026-09-04
**Status:** ET-C11 candidate
**Accepted authority predecessor:** [ETC10D11ForensicAdmission.md](./records/ETC10D11ForensicAdmission.md)
**Historical scenario contract:** [GRCV4ExploratorySideToolUserScenarios.md](./GRCV4ExploratorySideToolUserScenarios.md)
**D11 forensic scenarios:** [GRCV4ExploratorySideToolD11SuccessorScenarios.md](./GRCV4ExploratorySideToolD11SuccessorScenarios.md)

## Boundary

ET-C11 makes the accepted ET-C10 D11 authority reachable through the actual
Python API, notebook, and browser interfaces. It adds presentation and
interaction only. It does not change the D11 graph, infer new relations, run
scientific propagation in the browser, or satisfy paper, specification, or
runtime obligations.

```text
accepted historical ET-C9 scenarios      35
accepted ET-C10 forensic scenarios         6
candidate ET-C11 UX scenarios              8
current governed scenario total           49
```

## UX1. Browse the complete D11 authority population

Open the browser's **D11** surface. Switch between D11-C and D11-G9, filter by
kind, and search identifiers or labels. The catalog exposes exactly two
claims, two local debts, two selected profiles, 12 investigated candidates,
13 normative objects, 31 equation contracts, and seven forward obligations.

**Surface:** browser

## UX2. Inspect a D11 claim without flattening its status

Select `D11-C-CL-O-001` or `D11-G9-CL-N-001`. The browser displays the
precomputed `reconstruction_path` trace, claim class, source record and JSON
pointer, trace digest, support edges, and explicit authority ceiling.

**Surface:** browser and Python API

## UX3. Inspect object and equation provenance

Select `C-BASELINE-CURRENT`, `D11-C-EC-C-J0-CURRENT`,
`GRC9-EXPANSION-EXACT-BOUNDARY-MAP`, or
`D11-G9-EC-EXACT-OLD-PORT-MAP`. The browser renders the byte-bound output of
`object_dependents` or `contract_provenance` and never recomputes support.

**Surface:** browser and Python API

## UX4. Keep resolved debt separate from forward obligations

Inspect either D11 local debt and its full lifecycle. Then filter to forward
obligations. Resolved local authority, unsatisfied propagation/conformance
work, and the GRC9V4-only ceiling remain visibly distinct.

**Surface:** browser and Python API

## UX5. Run the Candidate C notebook recipes

Execute the supported D11 notebook runner. It emits source-bound traces for
the Candidate C claim, debt, and baseline-current equation contract into the
generated output envelope.

**Surface:** notebook and Python API

## UX6. Run the GRC9V4 notebook recipes

The same notebook emits the GRC9V4 claim, debt, and exact old-port-map contract
traces while retaining the no-GRC9/no-GRC9V3-repair boundary.

**Surface:** notebook and Python API

## UX7. Prove API, notebook, and browser trace identity

For all six notebook recipes, require canonical byte equality between the
direct Python API result, notebook output file, and precomputed browser view.

**Surface:** cross-surface verification

## UX8. Fail closed on stale or tampered presentation data

Reject a changed ET-C10 predecessor digest, changed D11 trace digest, missing
catalog view, altered population, or any browser authority flag that enables
inference, propagation, rerun prediction, or claim promotion.

**Surface:** Python and browser component tests

## Candidate acceptance matrix

| Scenario | Executable evidence |
| --- | --- |
| UX1 | Python population audit plus desktop/mobile browser traversal |
| UX2 | claim trace component test and browser source-receipt assertion |
| UX3 | object/contract component test and browser provenance assertion |
| UX4 | debt/obligation component test and browser authority-ceiling assertion |
| UX5 | Candidate C notebook output validation |
| UX6 | GRC9V4 notebook output validation |
| UX7 | six canonical API/notebook/browser byte comparisons |
| UX8 | Python and JavaScript tamper tests |
