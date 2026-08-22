from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from compare_frozen_and_full_dynamics import (  # noqa: E402
    frozen_components,
    functional_value,
    potential_and_site_audit,
    runtime_compatible_frozen_step,
    sign_audit_rows,
)
from artifact_io import assert_payload_digest  # noqa: E402
from gate_receipts import validate_receipt  # noqa: E402
from pygrc.models import GRC9V3  # noqa: E402
from grv4_hardening import conjugacy_errors, real_invariant_basis  # noqa: E402


class GRV4FrozenFullTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        registry = json.loads(
            (ROOT / "outputs/fixed_branch_registry.json").read_text(encoding="utf-8")
        )["payload"]
        cls.branch = next(
            row for row in registry["branches"] if row["branch_id"] == "grv2-f2-017"
        )
        cls.model = GRC9V3.load(str(REPO_ROOT / cls.branch["state_snapshot_path"]))

    def test_frozen_comparator_uses_the_grv3_zero_sum_basis(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        basis = components["basis"]
        self.assertTrue(np.allclose(basis.T @ basis, np.eye(basis.shape[1]), atol=1e-12))
        self.assertTrue(np.allclose(np.ones(basis.shape[0]) @ basis, 0.0, atol=1e-12))
        self.assertTrue(
            np.allclose(
                components["hessian_tangent"],
                components["hessian_tangent"].T,
                atol=1e-12,
            )
        )
        self.assertTrue(
            np.allclose(
                components["h_cont_tangent"],
                -components["h_p_tangent"],
                atol=1e-12,
            )
        )
        self.assertTrue(
            np.allclose(
                components["mobility_tangent"],
                components["mobility_tangent"].T,
                atol=1e-12,
            )
        )

    def test_staged_runtime_matches_the_explicit_frozen_map(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        coherence = components["coherence"] + 0.01 * components["basis"][:, 0]
        gradient = components["kappa"] * components["laplacian"] @ coherence - (
            2.0 * components["scale"] * coherence + components["mu"]
        )
        expected = coherence + components["dt"] * components["mobility"] @ gradient
        staged = runtime_compatible_frozen_step(
            components, coherence, components["dt"]
        )
        self.assertTrue(np.allclose(expected, staged["coherence"], atol=1e-12, rtol=0.0))

    def test_functional_sign_is_weakly_increasing_for_reference_probe(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        coherence = components["coherence"] + 0.01 * components["basis"][:, 0]
        gradient = components["kappa"] * components["laplacian"] @ coherence - (
            2.0 * components["scale"] * coherence + components["mu"]
        )
        updated = coherence + components["dt"] * components["mobility"] @ gradient
        self.assertGreaterEqual(
            functional_value(updated, components)
            - functional_value(coherence, components),
            -1e-12,
        )

    def test_method_freeze_prevents_post_spectrum_selection(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(48, config["branch_scope"]["expected_branch_count"])
        self.assertEqual(
            32, config["branch_scope"]["expected_primary_full_comparison_count"]
        )
        self.assertFalse(config["branch_scope"]["post_spectrum_selection_allowed"])
        self.assertFalse(config["claim_boundary"]["W_eliminability_claim_allowed"])
        self.assertFalse(
            config["claim_boundary"]["full_core_continuation_operator_claim_allowed"]
        )
        self.assertEqual(
            "clamped_counterfactual_only",
            config["frozen_comparator"]["reduction_classification"],
        )
        self.assertFalse(config["hardening"]["frozen_W_is_eliminated_W"])
        self.assertFalse(config["hardening"]["frozen_W_is_fast_slaved_W"])
        self.assertFalse(
            config["full_map_comparison"][
                "deadbeat_overwrite_modes_are_slow_disagreement"
            ]
        )

    def test_runtime_potential_and_site_hessian_match_finite_differences(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        _, _, directions = sign_audit_rows("test-branch", components, config)
        audit = potential_and_site_audit(components, directions, config)
        self.assertTrue(
            audit["h_p_relative_error"]
            <= config["hardening"]["h_p_finite_difference_relative_error_max"]
            or (
                np.linalg.norm(components["h_p_tangent"], ord=np.inf)
                <= config["hardening"]["h_p_near_zero_norm_threshold"]
                and audit["h_p_absolute_linf_error"]
                <= config["hardening"][
                    "h_p_finite_difference_absolute_linf_error_max"
                ]
            )
        )
        self.assertLessEqual(
            audit["maximum_directional_functional_error"],
            config["hardening"]["directional_functional_error_max"],
        )

    def test_temporal_operator_is_mobility_times_restoring_hessian(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        expected = (
            np.eye(components["h_cont_tangent"].shape[0])
            - components["dt"]
            * components["mobility_tangent"]
            @ components["h_cont_tangent"]
        )
        self.assertTrue(np.allclose(expected, components["multiplier"], atol=1e-12))
        structural = components["structural_temporal_diagnostics"]
        self.assertEqual("H_cont=-H_P", structural["restoring_sign_relation"])
        self.assertIn("mode_mapping_rule", structural)
        self.assertIn("projector_mapping_rule", structural)

    def test_semidiscrete_generator_has_the_opposite_relaxation_sign(self) -> None:
        config = json.loads(
            (ROOT / "configs/grv4_frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        components = frozen_components(self.model, config["hardening"])
        relaxation = (
            components["mobility_tangent"] @ components["h_cont_tangent"]
        )
        self.assertTrue(np.allclose(components["generator"], -relaxation, atol=1e-12))
        self.assertTrue(
            np.allclose(
                components["multiplier"],
                np.eye(relaxation.shape[0]) - components["dt"] * relaxation,
                atol=1e-12,
            )
        )

    def test_reviewed_artifact_uses_unambiguous_generator_and_relation_names(self) -> None:
        envelope = json.loads(
            (ROOT / "outputs/frozen_full_comparison.json").read_text(
                encoding="utf-8"
            )
        )
        assert_payload_digest(envelope)
        self.assertEqual("b1_grv4_frozen_full_comparison_v2", envelope["schema_version"])
        payload = envelope["payload"]
        self.assertFalse(payload["summary"]["primary_equivalence_supported"])
        self.assertNotIn("primary_agreement_count", payload["summary"])
        for branch in payload["branch_rows"]:
            self.assertNotIn("frozen_semidiscrete_rates", branch)
            self.assertIn("frozen_semidiscrete_generator_eigenvalues", branch)
            generator = np.asarray(branch["semidiscrete_generator"], dtype=float)
            relaxation = np.asarray(
                branch["structural_temporal_separation"][
                    "temporal_relaxation_operator"
                ],
                dtype=float,
            )
            self.assertTrue(np.allclose(generator, -relaxation, atol=1e-14, rtol=0.0))
            comparison = branch["primary_C_full_recurrence_comparison"]
            if comparison["status"] == "compared":
                self.assertIn(
                    comparison["bounded_relation"],
                    {
                        "no_resolved_difference_within_uncertainty",
                        "resolved_bounded_difference",
                    },
                )

    def test_grv4_receipt_uses_the_accepted_prerequisite_anchor(self) -> None:
        receipt = json.loads(
            (ROOT / "outputs/gates/grv4_result_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        validate_receipt(receipt)
        self.assertEqual("accepted", receipt["prerequisite_acceptance_status"])
        self.assertNotIn("prerequisite_receipt_status", receipt)
        self.assertEqual("awaiting_scientific_review", receipt["status"])
        self.assertFalse(
            receipt["artifact_semantics_correction"][
                "numerical_recomputation_performed"
            ]
        )

    def test_near_real_conjugate_pair_remains_a_real_invariant_plane(self) -> None:
        matrix = np.asarray(
            [[1.0, 1.57009415e-12], [-9.06511601e-13, 1.0]], dtype=float
        )
        basis, records = real_invariant_basis(
            matrix, minimum_magnitude=0.9, complex_tolerance=1e-10
        )
        self.assertEqual(2, basis.shape[1])
        self.assertEqual(
            "complex_conjugate_real_invariant_plane", records[0]["kind"]
        )

    def test_near_zero_conjugacy_retains_absolute_error(self) -> None:
        source = np.asarray([[2e-11, 0.0], [0.0, -2e-11]])
        transport = np.asarray([[0.0, -1.0], [1.0, 0.0]])
        target = transport @ source @ np.linalg.inv(transport) + 1e-12 * np.eye(2)
        errors = conjugacy_errors(source, target, transport)
        self.assertGreater(errors["relative"], 1e-6)
        self.assertLessEqual(errors["absolute_linf"], 1e-8)


if __name__ == "__main__":
    unittest.main()
