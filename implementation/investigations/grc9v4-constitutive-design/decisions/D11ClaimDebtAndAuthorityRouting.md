# D11 Claim, Debt, Verification, and Contract Routing

**Gate:** D11-ROUTE
**Status:** Accepted bounded routing contract
**Predecessor:** `GRC9V4-CD-D11-OPEN-v1`
**Decision digest:** `63cc407bffefef85602c28ead6c3da6b846778d3be9f78952db11cb10275c78d`
**Scientific result:** None

## Purpose

This record makes the D11 inheritance boundary explicit. D11 does not begin
with only the last D10.2 decision digest: it consumes the complete accepted
D10 claim topology, debt-transformation topology, verification-obligation
registry, and D10.2 object/equation-contract population.

The two specification-audit findings are additional successor debts. They do
not replace, silently resolve, or reclassify anything accumulated through
D10.2.

## Exact Carry-Forward

| Accepted population | Count | D11-entry disposition |
|---|---:|---|
| Current D10 claims | 39 | Immutable; no addition, removal, or reclassification |
| Historical claim nodes | 29 | Immutable |
| Total claim nodes | 68 | Exact set equality required |
| D10 debt transformations | 29 | Original transformation and claim-edge dispositions retained |
| Verification obligations | 11 | Ten remain pending; the provenance preclose is satisfied only for the current D10 population |
| Normatively load-bearing objects | 67 | Current-population D10.2 authority retained |
| Normative equation contracts | 152 | Current-population D10.2 authority retained |
| Explicit equation contracts | 85 | Current-population D10.2 authority retained |
| Disabled-reduction rows | 40 | Current-population D10.2 authority retained |
| Independent GRC derivations | 12 | Current-population D10.2 result retained |

The current claim classes remain exactly:

```text
normative = 9
optional = 7
conditional = 12
open = 5
negative = 6
```

The machine-readable record carries every current claim ID, historical claim
ID, debt ID, and verification-obligation ID. The D11 audit compares those
inventories to their accepted D10 sources by set equality.

## Verification Obligations

The ten runtime, numeric, analysis, and implementation verification
obligations remain pending. Opening D11 does not discharge any of them.

`D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT` has a narrower disposition: D10.2
satisfied it for the current initial specification population. It must be
reopened for every materially distinct successor profile. The accepted
`D10.2-CL-N-001` text is therefore recorded as a D10.2-local successor
reference; it is not silently inserted as a fortieth node in the D10 claim
topology.

## Additive D11 Debts

### D11-C — Baseline transport authority

`D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY` is active. Its bearing spans the
Candidate C authority/current chain, all five C realization consumers,
mobility typing, lifecycle/event reconstruction, controls, units, covariance,
and the inherited claim ceilings. “Bearing” means that the accepted D11-C
result must remain consistent with those claims; it does not change their
status at opening.

### D11-G9 — Canonical port allocation

`D11-G9-DEBT-CANONICAL-PORT-ALLOCATION` is queued behind accepted D11-C. Its
bearing spans only the GRC9V4 specialization and bounded common lifecycle,
event, receipt, and conformance consequences. GRC9 and GRC9V3 remain read-only.

## Transformation Rule

Only a separately accepted D11 scientific successor may introduce a new claim
or transform an existing claim/debt disposition. Such a record must state the
exact predecessor and successor IDs and reciprocal edges. Until then:

```text
D10 claim status changes = 0
D10 debt disposition changes = 0
verification obligations discharged by D11 opening = 0
D11 scientific results accepted = 0
```
