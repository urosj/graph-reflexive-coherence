from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "implementation/GRC9V3ContinuationReadBackVerificationSpecification.md"
EXPECTED_SHA = "7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44"


class SpecificationPropagationTest(unittest.TestCase):
    def test_controlling_digest_propagates(self) -> None:
        self.assertEqual(EXPECTED_SHA, hashlib.sha256(SPEC.read_bytes()).hexdigest())
        for path in (ROOT / "README.md", ROOT / "implementation/GRC9V3ContinuationReadBackVerificationImplementationPlan.md", ROOT / "implementation/GRC9V3ContinuationReadBackVerificationImplementationChecklist.md", ROOT / "configs/baseline.json"):
            self.assertIn(EXPECTED_SHA, path.read_text(encoding="utf-8"), path.name)

    def test_complete_named_package_is_materialized(self) -> None:
        required = [
            "hypotheses/README.md", "hypotheses/claim_ledger.md", "hypotheses/assumption_registry.md", "hypotheses/derivation_status_appendix.md", "hypotheses/theory_debt_register.md", "hypotheses/theory_test_traceability.md", "hypotheses/gate_dependency_map.md",
            "configs/p0_manifest.json", "configs/baseline.json", "configs/numerical_tolerances.json", "configs/cycle_space.json", "configs/fixture_registry.json", "configs/preregistration.json", "configs/branch_search.json", "configs/orbit_search.json", "configs/nonnormal_control.json", "configs/fast_slow_control.json", "configs/persistence_protocol.json",
            "fixtures/two_node_transport.json", "fixtures/two_node_homogeneous_branch.json", "fixtures/two_node_nonuniform_seed.json", "fixtures/triangle_same_row_seed.json", "fixtures/triangle_port_controls.json",
            "scripts/artifact_io.py", "scripts/state_codec.py", "scripts/tangent_basis.py", "scripts/interventions.py", "scripts/gate_receipts.py", "scripts/numerical_convergence.py", "scripts/branch_continuation.py", "scripts/edge_space.py", "scripts/serialize_theory_contract.py", "scripts/capture_repository_baseline.py", "scripts/validate_instrumentation.py", "scripts/solve_strong_fixed_branches.py", "scripts/compute_complete_step_jacobian.py", "scripts/compare_frozen_and_full_dynamics.py", "scripts/run_preparation_persistence_probe.py", "scripts/search_return_orbits.py", "scripts/sweep_temporal_and_spatial_thresholds.py", "scripts/classify_claims_and_extensions.py", "scripts/route_contradictions_and_theory_reopening.py", "scripts/build_lgrc_handoff.py", "scripts/run_all.py",
            "requirements-experiment.txt",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_grv0_obligations_and_gate_names_are_current(self) -> None:
        combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in ("README.md", "implementation/GRC9V3ContinuationReadBackVerificationImplementationPlan.md", "implementation/GRC9V3ContinuationReadBackVerificationImplementationChecklist.md"))
        for gate in [f"GRV{index}" for index in range(9)]:
            self.assertIn(gate, combined)
        for obligation in ("protected_path_manifest_v0", "experiment_path_manifest.json", "theory_source_manifest.json", "numerical_environment.json", "grv0_result_receipt.json", "grv0_acceptance_anchor.json", "test_edge_space.py", "test_spec_propagation.py"):
            self.assertIn(obligation, combined)


if __name__ == "__main__":
    unittest.main()
