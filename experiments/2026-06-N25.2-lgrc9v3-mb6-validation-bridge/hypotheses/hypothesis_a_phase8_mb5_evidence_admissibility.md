# Hypothesis A - Phase 8 MB5 Evidence Admissibility

## Claim

N25.2 can verify that the Phase 8 LGRC9V3 multi-basin formation tranche is
source-backed, replay-clean, control-clean, producer-audited, and claim-clean
at the declared MB5 ceiling.

## Expected Support

Hypothesis A is supported only if N25.2 records:

```text
Phase 8 multi-basin closeout artifacts exist and parse
Phase 8 closeout reports MB5 as the supported ceiling
Phase 8 closeout keeps MB6 false
runtime surfaces are default-off
runtime evidence is source-backed
replay validation exists
merge/leakage controls exist and fail closed
producer compatibility audit exists
telemetry/examples match the closeout interpretation
focused tests pass or prior test results are source-backed
unsafe claims remain false
```

N25.2 may additionally validate MB5 admissibility by running the closed
LGRC9V3 runtime and comparing runtime-emitted records against the Phase 8
closeout claims. Runtime execution validates the closed implementation; it does
not modify, repair, or retune the implementation.

## Failure Conditions

Hypothesis A fails if:

```text
source artifact missing or unreadable
digest/admissibility check fails
MB5 is asserted without replay/control evidence
producer scheduling is treated as native support
telemetry/examples contradict closeout claims
MB6 is already claimed without an N25.2 gate
unsafe claim flag is true
runtime evidence requires an implementation change inside N25.2
```

## Claim Boundary

Hypothesis A can support Phase 8 MB5 evidence admissibility. It cannot support
MB6, N26-ready substrate evidence, native support, agency, sentience, ant
ecology, or Phase 8 completion.
