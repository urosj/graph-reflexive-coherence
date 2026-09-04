# GRCv4 Exploratory Side Tool D11 Successor Scenarios

**Date:** 2026-09-04
**Status:** ET-C10 accepted
**Historical scenario contract:** [GRCV4ExploratorySideToolUserScenarios.md](./GRCV4ExploratorySideToolUserScenarios.md)
**Plan:** [GRCV4ExploratorySideToolImplementationPlan.md](./GRCV4ExploratorySideToolImplementationPlan.md)
**Checklist:** [GRCV4ExploratorySideToolImplementationChecklist.md](./GRCV4ExploratorySideToolImplementationChecklist.md)

## Authority and count boundary

This append-only contract defines six ET-C10 successor-forensic scenarios. It
does not modify the accepted ET-C9 browser, counterfactual, or 35-scenario
closeout artifacts.

```text
accepted historical ET-C9 scenarios    35
accepted ET-C10 successor scenarios      6
current governed scenarios              41
```

The scenarios consume accepted D11 authority; they do not create scientific
evidence. Their outputs are source-bound `forensic_evidence_trace` values or
deterministic verification receipts around those traces. Forward paper,
specification, and runtime obligations remain future work.

## S1. Reconstruct the accepted Candidate C transport claim

Load the successor context and query `D11-C-CL-O-001` with
`reconstruction_path`. Reach the accepted D11-C local debt, predecessor D10
claims, T3a resolution, and companion provenance supplement. Exclude all three
new forward obligations from backward support and preserve the
`optional_profile_normative` claim class.

**Output:** `forensic_evidence_trace`

## S2. Separate the Candidate C debt resolution from forward work

Query `D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY` with `debt_lifecycle`. Return
the preregistered opening, `resolved_bounded_by_D11_C_T3a` disposition, and the
three still-forward paper/specification, serialization/readmission, and
implementation/covariance obligations as five separately classified rows.

**Output:** `forensic_evidence_trace`

## S3. Audit the exact Candidate C current contract

Query `D11-C-EC-C-J0-CURRENT` with `contract_provenance` and
`C-BASELINE-CURRENT` with `object_dependents`. Preserve the exact provenance
supplement pointer, `accepted_bounded_D11_C_successor` support semantic, and
the distinction between accepted design equations and pending runtime solver
or endpoint-effect evidence.

**Output:** `forensic_evidence_trace`

## S4. Reconstruct the accepted GRC9V4 expansion claim

Query `D11-G9-CL-N-001` with `reconstruction_path`. Reach the P4a resolution,
the GRC9V4-only local debt, the nine reciprocal predecessor-claim edges, and
the append-only provenance supplement. Do not describe the result as a GRC9 or
GRC9V3 repair, a physical chirality selection, or runtime conformance.

**Output:** `forensic_evidence_trace`

## S5. Audit GRC9V4 port allocation and its legacy boundary

Query `D11-G9-DEBT-CANONICAL-PORT-ALLOCATION` with `debt_lifecycle`, then query
`D11-G9-EC-EXACT-OLD-PORT-MAP` and
`D11-G9-EC-LEGACY-DEFINED-DOMAIN` with `contract_provenance`. Keep the bounded
resolution separate from four forward obligations and preserve the disabled
legacy defined-domain/fail-closed ceiling.

**Output:** `forensic_evidence_trace`

## S6. Enforce the historical/current loader and paper boundary

Require `load_forensic_context` to reject D11 claim IDs and
`load_successor_forensic_context` to accept them while still rejecting the
record-local non-node `D10_2_CL_N_001`. Rebuild the ET-C10 manifest and graph
byte-exactly. Before paper editing, require the paper audit to report
`pending_tooling_ready`; after any paper-byte change, require complete coverage
of both D11 claims, all 13 objects, all 31 contracts, both selected profiles,
and the key equations before reporting `propagated`.

**Output:** fail-closed audit result plus source-bound forensic traces

## Executable coverage

| Scenario | Primary surface | ET-C10 evidence |
| --- | --- | --- |
| S1 | `reconstruction_path` | D11-C claim reconstruction and forward-obligation exclusion |
| S2 | `debt_lifecycle` | five classified D11-C lifecycle rows |
| S3 | `contract_provenance`, `object_dependents` | source-exact Candidate C support |
| S4 | `reconstruction_path` | D11-G9 claim reconstruction and GRC9V4-only ceiling |
| S5 | `debt_lifecycle`, `contract_provenance` | six lifecycle rows and defined-domain boundary |
| S6 | both context loaders and paper audit | exact rebuild, fail-closed non-node, pending/propagated state machine |

`audit_iteration10_d11.py` and `test_iteration10_d11.py` execute this coverage.
The normal verifier reruns both alongside the immutable historical audits. No
browser rebuild or new counterfactual mutation algebra is claimed.
