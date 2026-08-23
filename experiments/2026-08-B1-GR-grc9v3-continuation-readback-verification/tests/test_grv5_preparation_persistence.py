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

from artifact_io import assert_payload_digest  # noqa: E402
from grv5_methods import (  # noqa: E402
    activity_amplitude_from_target,
    activity_write_stage_trace,
    activity_write_stage,
    canonical_edge_direction,
    coherence_vector,
    conductance_surface_consistency,
    conductance_vector,
    difference_in_differences,
    direct_conductance_intervention,
    equal_carrier_preserving_reached_state,
    match_C_and_J_preserving_W,
    matching_audit,
    old_current_intervention,
    reset_carrier,
    signed_sweep_fit,
    swap_carrier,
)
from run_preparation_persistence_probe import (  # noqa: E402
    branch_relocation_audit,
    build_36_point_review_audit,
    intervention_registry,
    preparation_pairs,
    reachability_classification,
    transient_W_mediation_classification,
)
from pygrc.models import GRC9V3  # noqa: E402


class GRV5PreparationPersistenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv5_preparation_persistence.json").read_text(
                encoding="utf-8"
            )
        )
        registry = json.loads(
            (ROOT / "outputs/fixed_branch_registry.json").read_text(encoding="utf-8")
        )["payload"]
        cls.branch = registry["branches"][0]
        cls.model = GRC9V3.load(str(REPO_ROOT / cls.branch["state_snapshot_path"]))
        cls.nonuniform_branch = next(
            row for row in registry["branches"] if row["branch_id"] == "grv2-f2-017"
        )
        cls.nonuniform_model = GRC9V3.load(
            str(REPO_ROOT / cls.nonuniform_branch["state_snapshot_path"])
        )
        grv3 = json.loads(
            (ROOT / "outputs/complete_step_jacobians.json").read_text(
                encoding="utf-8"
            )
        )["payload"]
        cls.nonuniform_grv3 = next(
            row
            for row in grv3["branches"]
            if row["branch_id"] == cls.nonuniform_branch["branch_id"]
        )

    def test_method_is_all_branch_and_claim_bounded(self) -> None:
        self.assertEqual(48, self.config["source_scope"]["expected_branch_count"])
        self.assertEqual(
            144, self.config["source_scope"]["expected_candidate_row_count"]
        )
        self.assertEqual(
            "all_certified_branches_no_post_outcome_selection",
            self.config["source_scope"]["branch_selection"],
        )
        self.assertFalse(
            self.config["present_current_convention"][
                "native_external_present_current_input_available"
            ]
        )
        self.assertFalse(self.config["claim_boundary"]["native_readback_supported"])
        self.assertFalse(
            self.config["claim_boundary"]["frozen_W_result_can_upgrade_native"]
        )

    def test_direct_conductance_intervention_is_clone_first(self) -> None:
        before_c = coherence_vector(self.model).copy()
        before_w = conductance_vector(self.model).copy()
        changed = direct_conductance_intervention(
            self.model,
            signed_relative_amplitude=self.config["preparation"][
                "direct_conductance_relative_amplitude"
            ],
        )
        self.assertTrue(np.array_equal(before_c, coherence_vector(changed)))
        self.assertFalse(np.array_equal(before_w, conductance_vector(changed)))
        self.assertTrue(np.array_equal(before_w, conductance_vector(self.model)))

    def test_activity_write_is_stage_local_sign_even_and_not_complete_step_retained(
        self,
    ) -> None:
        amplitude = activity_amplitude_from_target(
            self.model,
            self.config["preparation"][
                "activity_write_target_log_conductance_exponent"
            ],
        )
        positive = activity_write_stage(self.model, amplitude=amplitude)
        negative = activity_write_stage(self.model, amplitude=-amplitude)
        zero = activity_write_stage(self.model, amplitude=0.0)
        self.assertTrue(
            np.allclose(
                conductance_vector(positive),
                conductance_vector(negative),
                atol=1e-14,
                rtol=0.0,
            )
        )
        self.assertGreater(
            np.linalg.norm(conductance_vector(positive) - conductance_vector(zero)),
            1e-6,
        )
        full_positive = old_current_intervention(self.model, amplitude=amplitude)
        full_zero = old_current_intervention(self.model, amplitude=0.0)
        full_positive.step()
        full_zero.step()
        self.assertTrue(
            np.allclose(
                conductance_vector(full_positive),
                conductance_vector(full_zero),
                atol=1e-10,
                rtol=0.0,
            )
        )

    def test_activity_ladder_has_exact_per_edge_quadratic_shape(self) -> None:
        direction_squared = np.square(canonical_edge_direction(self.nonuniform_model))
        for target in self.config["preparation"][
            "activity_write_target_exponent_ladder"
        ]:
            amplitude = activity_amplitude_from_target(self.nonuniform_model, target)
            positive = activity_write_stage(self.nonuniform_model, amplitude=amplitude)
            negative = activity_write_stage(self.nonuniform_model, amplitude=-amplitude)
            zero = activity_write_stage(self.nonuniform_model, amplitude=0.0)
            observed = np.log(conductance_vector(positive) / conductance_vector(zero))
            self.assertTrue(
                np.allclose(observed, -target * direction_squared, atol=1e-12)
            )
            self.assertTrue(
                np.allclose(
                    conductance_vector(positive),
                    conductance_vector(negative),
                    atol=1e-14,
                )
            )

    def test_preparation_stage_trace_has_all_frozen_boundaries(self) -> None:
        amplitude = activity_amplitude_from_target(
            self.nonuniform_model,
            self.config["preparation"][
                "activity_write_target_log_conductance_exponent"
            ],
        )
        trace = activity_write_stage_trace(self.nonuniform_model, amplitude=amplitude)
        self.assertTrue(
            set(
                self.config["p5_3_review_hardening"]["preparation_boundary"][
                    "required_stage_records"
                ]
            ).issubset(trace)
        )
        self.assertNotEqual(
            trace["after_first_native_transport_write"]["W"],
            trace["before_preparation"]["W"],
        )

    def test_matching_receipt_preserves_authoritative_W_and_noncarrier_state(
        self,
    ) -> None:
        amplitude = self.config["preparation"]["direct_conductance_relative_amplitude"]
        first = direct_conductance_intervention(
            self.nonuniform_model, signed_relative_amplitude=amplitude
        )
        second = direct_conductance_intervention(
            self.nonuniform_model, signed_relative_amplitude=-amplitude
        )
        matched = match_C_and_J_preserving_W(first, second)
        audit = matching_audit(
            first,
            second,
            matched[0],
            matched[1],
            tolerance=1e-10,
        )
        self.assertTrue(audit["passed"])
        self.assertTrue(
            conductance_surface_consistency(matched[0])["surfaces_consistent"]
        )

    def test_reset_swap_and_equal_controls_are_exact_on_authoritative_W(self) -> None:
        amplitude = self.config["preparation"]["direct_conductance_relative_amplitude"]
        first = direct_conductance_intervention(
            self.nonuniform_model, signed_relative_amplitude=amplitude
        )
        second = direct_conductance_intervention(
            self.nonuniform_model, signed_relative_amplitude=-amplitude
        )
        baseline_w = conductance_vector(self.nonuniform_model)
        reset = reset_carrier(first, second, self.nonuniform_model)
        self.assertTrue(np.array_equal(baseline_w, conductance_vector(reset[0])))
        self.assertTrue(np.array_equal(baseline_w, conductance_vector(reset[1])))
        swapped = swap_carrier(first, second)
        self.assertTrue(
            np.array_equal(conductance_vector(second), conductance_vector(swapped[0]))
        )
        self.assertTrue(
            np.array_equal(conductance_vector(first), conductance_vector(swapped[1]))
        )
        equal = equal_carrier_preserving_reached_state(first, second)
        self.assertTrue(
            np.array_equal(conductance_vector(equal[0]), conductance_vector(equal[1]))
        )
        self.assertTrue(
            all(
                conductance_surface_consistency(model)["surfaces_consistent"]
                for model in (*reset, *swapped, *equal)
            )
        )

    def test_matched_pair_preserves_W_but_native_stage_reconstructs_it(self) -> None:
        amplitude = self.config["preparation"]["direct_conductance_relative_amplitude"]
        first = direct_conductance_intervention(
            self.model, signed_relative_amplitude=amplitude
        )
        second = direct_conductance_intervention(
            self.model, signed_relative_amplitude=-amplitude
        )
        first, second = match_C_and_J_preserving_W(first, second)
        self.assertTrue(
            np.array_equal(coherence_vector(first), coherence_vector(second))
        )
        self.assertFalse(
            np.array_equal(conductance_vector(first), conductance_vector(second))
        )
        native = difference_in_differences(
            first,
            second,
            lane="native_immediate_transport_stage_probe",
            probe_kind="coherence_or_potential_probe",
            amplitude=0.002,
        )
        reduced = difference_in_differences(
            first,
            second,
            lane="frozen_W_probe",
            probe_kind="coherence_or_potential_probe",
            amplitude=0.002,
        )
        self.assertLessEqual(native["difference_in_differences_l2"], 1e-10)
        self.assertGreater(reduced["difference_in_differences_l2"], 1e-10)
        self.assertEqual("substrate_reduced", reduced["substrate_class"])
        self.assertEqual(4, len(reduced["cell_receipts"]))
        fit = signed_sweep_fit(
            [
                difference_in_differences(
                    first,
                    second,
                    lane="frozen_W_probe",
                    probe_kind="coherence_or_potential_probe",
                    amplitude=value,
                )
                for value in (-0.002, -0.001, 0.0, 0.001, 0.002)
            ],
            tolerance=0.05,
        )
        self.assertEqual(2, len(fit["odd_even_decomposition"]))

    def test_complete_step_activity_lane_keeps_joint_C_consequence_separate_from_W(
        self,
    ) -> None:
        amplitude = activity_amplitude_from_target(
            self.nonuniform_model,
            self.config["preparation"][
                "activity_write_target_log_conductance_exponent"
            ],
        )
        activity = old_current_intervention(self.nonuniform_model, amplitude=amplitude)
        zero = old_current_intervention(self.nonuniform_model, amplitude=0.0)
        activity.step()
        zero.step()
        self.assertGreater(
            np.linalg.norm(coherence_vector(activity) - coherence_vector(zero)),
            1e-6,
        )
        self.assertLessEqual(
            np.linalg.norm(conductance_vector(activity) - conductance_vector(zero)),
            1e-10,
        )

    def test_p5_4_reachability_and_transient_W_claims_fail_closed(self) -> None:
        reachability = reachability_classification(
            "P-J-activity-complete-step-vs-zero"
        )
        self.assertEqual(
            "produced_by_unchanged_runtime_from_synthetic_intervention",
            reachability["post_intervention_state_status"],
        )
        self.assertFalse(
            reachability["reachable_from_accepted_branch_by_unchanged_runtime_alone"]
        )
        self.assertFalse(reachability["runtime_reached_shorthand_allowed"])
        mediation = transient_W_mediation_classification(
            "P-J-activity-complete-step-vs-zero"
        )
        self.assertEqual("not_established", mediation["status"])
        self.assertFalse(mediation["stage_matched_W_only_mediation_control_run"])
        self.assertFalse(
            mediation["later_C_mediation_specifically_by_transient_W_supported"]
        )

    def test_p5_4_branch_relocation_rival_is_machine_visible(self) -> None:
        result = json.loads(
            (ROOT / "outputs/conductance_retention_probe.json").read_text(
                encoding="utf-8"
            )
        )["payload"]
        row = next(
            candidate
            for candidate in result["candidate_rows"]
            if candidate["branch_id"] == self.nonuniform_branch["branch_id"]
            and candidate["preparation_id"]
            == "P-J-activity-complete-step-vs-zero"
        )
        audit = branch_relocation_audit(
            self.nonuniform_model,
            row["horizon_rows"],
            self.nonuniform_grv3,
            required_horizon=10,
            tolerance=1e-10,
        )
        self.assertTrue(audit["all_offsets_within_admitted_C_coordinate_to_tolerance"])
        self.assertEqual(
            "branch_relocation_rival_unresolved_not_excluded",
            audit["branch_relocation_rival_status"],
        )
        self.assertFalse(audit["transverse_branch_relative_retention_supported"])

    def test_review_artifact_remains_bounded_when_present(self) -> None:
        path = ROOT / "outputs/conductance_retention_probe.json"
        if not path.exists():
            self.skipTest("GRV5 has not executed from its clean P5 revision")
        envelope = json.loads(path.read_text(encoding="utf-8"))
        assert_payload_digest(envelope)
        payload = envelope["payload"]
        self.assertFalse(payload["summary"]["native_readback_supported"])
        self.assertFalse(payload["summary"]["closed_loop_supported"])
        self.assertTrue(
            payload["claim_boundary"]["frozen_W_sensitivity_does_not_upgrade_native"]
        )
        if envelope["schema_version"] == "b1_grv5_conductance_retention_probe_v2":
            self.assertFalse(
                payload["summary"][
                    "later_C_mediation_specifically_by_transient_W_supported"
                ]
            )
            self.assertFalse(
                payload["summary"][
                    "complete_step_state_reachable_from_accepted_branch_by_unchanged_runtime_alone"
                ]
            )
            self.assertEqual(
                32,
                payload["summary"][
                    "branch_relocation_rival_unresolved_GRR2_row_count"
                ],
            )
        if (
            envelope["schema_version"]
            == "b1_grv5_conductance_retention_probe_v2"
            and payload["summary"].get(
                "all_36_review_points_mechanically_accounted_for", False
            )
        ):
            audit = build_36_point_review_audit(payload, self.config)
            self.assertEqual(36, audit["review_point_count"])
            self.assertTrue(audit["all_review_points_mechanically_accounted_for"])

    def test_grv5_intervention_registry_has_the_canonical_fields(self) -> None:
        _, controls = preparation_pairs(
            self.nonuniform_model,
            self.config,
            base_snapshot_sha256=self.nonuniform_branch["state_snapshot_sha256"],
        )
        registry = intervention_registry(
            [{"branch_id": self.nonuniform_branch["branch_id"], **controls}]
        )
        required = {
            "intervention_id",
            "base_snapshot_sha256",
            "coordinate_semantics",
            "fields_directly_changed",
            "fields_explicitly_held_fixed",
            "fields_rebuilt_afterward",
            "rebuild_order",
            "validity_checks",
            "reachability_status",
            "reachability_classification",
            "physical_projection_before",
            "physical_projection_after",
            "causal_state_projection_before",
            "causal_state_projection_after",
        }
        self.assertEqual(4, len(registry["interventions"]))
        self.assertTrue(
            all(required.issubset(row) for row in registry["interventions"])
        )


if __name__ == "__main__":
    unittest.main()
