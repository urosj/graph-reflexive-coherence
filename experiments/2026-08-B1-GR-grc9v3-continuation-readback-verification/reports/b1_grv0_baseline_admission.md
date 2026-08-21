# B1-GR GRV0 Baseline Admission

## Result

```text
gate = GRV0
mechanical_status = passed
scientific_acceptance = awaiting_human_review
candidate_closeout_ceiling = GRV-C1
positive_evidence_opened = false
runtime_change_authorized = false
```

GRV0 admits only the exact specification, source identities, clean test
baseline, package schemas, numerical policy, and preregistered envelope.
It provides no continuation, retention, read-back, or write-back evidence.

## Baseline

- Execution revision: `5f9297378a26b8093f523cd11f8cb9f0f0aef723`
- Substrate base revision: `589f933e5649c34d3ad54a5f8dbdba2a20e968d7`
- Theory revision: `5a8b01ae60165054da617db649c5a039755a18ec`
- Specification SHA-256: `7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44`
- Existing tests: `passed` (1354 run, 0 skipped)
- Test log: `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/logs/grv0_existing_tests.log`

## Acceptance Boundary

The result receipt is mechanical provenance, not scientific acceptance.
GRV1 remains blocked until an authorized human reviews the committed GRV0
result revision and records a separate accepted anchor.

## Emitted Artifacts

- `outputs/baseline_manifest.json`
- `outputs/contradiction_register.json`
- `outputs/experiment_path_manifest.json`
- `outputs/fixed_topology_envelope.json`
- `outputs/gate_dependency_map.json`
- `outputs/logs/grv0_existing_tests.log`
- `outputs/numerical_environment.json`
- `outputs/proof_note_registry.json`
- `outputs/protected_path_manifest_v0.json`
- `outputs/tangent_basis_registry.json`
- `outputs/theory_assumption_registry.json`
- `outputs/theory_claim_ledger.json`
- `outputs/theory_contract_identity.json`
- `outputs/theory_debt_register.json`
- `outputs/theory_derivation_status.json`
- `outputs/theory_source_manifest.json`
- `outputs/theory_test_traceability.json`
