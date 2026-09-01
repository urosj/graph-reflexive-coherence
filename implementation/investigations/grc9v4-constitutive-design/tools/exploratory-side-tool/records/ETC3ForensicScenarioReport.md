# ET-C3 Forensic Scenario Report

**Status:** Accepted

The report reconstructs accepted-source relations through pure Python
functions. It adds no scientific claims and performs no counterfactual
mutation.

## Scenarios

- `F1` top_normative_claim: `1` rows, digest `e644b8a98a6e62245eea6c44e664df7a323d89ae64c9b4b21b98a43dda853064`
- `F2` debt_pressure_to_transformation: `2` rows, digest `0febc01c75f4576eb767a1081461960b7014f030d298facc6956b9608d13d2be`
- `F3A` D7v2_gate_act: `2` rows, digest `ab6fb92b2e44091e44b7c5b596b9b658402edf8223f2ae2e4bd8718dcbdd1909`
- `F3B` D7v2_gate_contribution: `10` rows, digest `34cba2c3416dbe421e72fd5ea6c2248e0e1858415118aaf38c9eaa5396c2fd4e`
- `F4` candidate_A_career: `12` rows, digest `8e39c36d556490be2fe31d162bdfbec5a9e31338b8c67e8b05a3ca79939e8181`
- `F5` candidate_B_routed_boundary: `13` rows, digest `d5e4f811093210d01a0953f2571411c15184079e6f9b225a1199e5e7967fa234`
- `F6` V4_D_admission_slot: `18` rows, digest `b402f242abcd447dc772039f9c46c24bfc225801cc43db0df366474597f39ea6`
- `F7` blocked_overreads: `14` rows, digest `f8887156d233772b858dd18980bbfd67782076fc5f424f7b5e50dbf318a51cc3`
- `F8A` contract_support: `1` rows, digest `3bdb1526bd4bfceaa5e61049c8c6c7c705c31f27a2885cb6670872f1e49cf79b`
- `F8B` object_dependents: `1` rows, digest `cf4797fccbf473a0db3d249e99a370d8512c83ccc74ae66fd6f59b2b1c9009dc`
- `E3` candidate_B_readmission_path: `13` rows, digest `d5e4f811093210d01a0953f2571411c15184079e6f9b225a1199e5e7967fa234`
- `E4` accepted_negative_claims: `14` rows, digest `f8887156d233772b858dd18980bbfd67782076fc5f424f7b5e50dbf318a51cc3`

Every row names its admitted source record, canonical source digest,
JSON pointer, and exact ET-C2 propagation-edge references. Forward
verification obligations are reported as work routing and are never
used as backward accepted support.

## Accepted Residual Boundaries

- The focused ET-C3 matrix is intentionally lighter than ET-C2;
  graph invariant enforcement remains owned by ET-C2, while the I3
  auditor checks every emitted source pointer and edge witness.
- ET-C3 uses chained trust rooted in accepted ET-C2 and revalidates
  ET-C2, ET-C1, and source identity on every context load.
- Candidate A has one explicit, source-bounded D10.2 hardening
  projection. It is not a generic candidate rule and must be reopened
  if another candidate requires equivalent special handling.

Report digest: `ddd91b4ec63894f955b9423caf71f4fc27df559ac74d54a822d4f32042055f14`
