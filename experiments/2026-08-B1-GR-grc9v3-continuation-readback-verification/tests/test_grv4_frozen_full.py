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
from pygrc.models import GRC9V3  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
