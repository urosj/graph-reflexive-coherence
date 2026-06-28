# Hypothesis B - MB6 / N26 Substrate Bridge Validation

## Claim

N25.2 can classify whether the validated Phase 8 MB5 evidence is sufficient for
the MB6 handoff rung:

```text
MB6 = N26-ready multi-basin substrate evidence
```

## Expected Support

Hypothesis B is supported only if N25.2 shows that the Phase 8 evidence chain
provides:

```text
source-backed multi-basin runtime surfaces
source-backed child-basin state records
replay-backed child-basin persistence
fail-closed merge/leakage controls
producer/native mutation ownership discipline
front-capacity boundary-birth provenance where used
no hidden producer basin insertion
no label-only basin formation
no old-basin thickening relabel
no transient flow sink relabel
no graph-visual-only success
N26 consumption rule with explicit scope
```

MB6 support may consume N25.2-generated native runtime execution artifacts, but
only if they are produced by the closed implementation, source/digest grounded,
replay-backed, control-clean, stress/variant checked, and claim-clean.
Reconstruction may validate runtime-emitted records; it cannot create the
original child-basin or multi-basin evidence.

If any required MB6 gate is missing, Hypothesis B should not be forced to pass.
Instead, N25.2 should classify:

```text
MB6 blocked with exact blocker list
N26 unscoped multi-basin substrate consumption blocked
N26 may consume only scoped/provisional context if allowed
```

## Failure Conditions

Hypothesis B fails if:

```text
MB6 is inferred from MB5 without an independent N25.2 gate
visual topology growth is treated as multi-basin persistence by itself
collapse/reabsorption telemetry is treated as independent new-basin formation
front-capacity companion evidence backfills unrelated MB5 rows
N26 consumption is allowed without a source-backed MB6 classification
replay/reconstruction is used as a replacement for native runtime execution
runtime execution relies on source, spec, test, example, or implementation edits
inside N25.2
```

## Claim Boundary

Hypothesis B may support an MB6 bridge only if all gates pass. If the gates do
not pass, a clean blocker classification is still a valid N25.2 result.
