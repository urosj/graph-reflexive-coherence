# Hypothesis D - Downstream Contract Enforceability

N20 can define a contract that N21-N28 must consume without redefining basin
signature, continuation-function descriptor, proxy-only success, or
producer-residue classification in order to pass.

Expected support:

```text
contract_status enum frozen
row_decision enum frozen
complete rows are the only consumable rows
primitive dependency map defined
N21 readiness inputs defined
later experiments cannot move basin signature criteria to pass
later experiments cannot move proxy-only success blockers to pass
later experiments cannot relabel producer residue as substrate-carried state
```

Failure condition:

```text
a later primitive can be counted as supported by changing the N20 basin
signature, continuation condition, proxy-only success blocker, or
producer-residue classification instead of recording a source-backed
naturalization result
```
