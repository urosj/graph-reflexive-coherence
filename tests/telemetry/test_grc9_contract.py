"""Contract tests for the GRC9 telemetry extension surface."""

from __future__ import annotations

import unittest

from pygrc import telemetry


def _lane_context() -> telemetry.GRC9LaneContext:
    return telemetry.GRC9LaneContext(
        source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
        lane_name="phase_t_grc9_contract_smoke",
        role="primary",
    )


def _backend_config() -> telemetry.GRC9BackendConfigTelemetry:
    return telemetry.GRC9BackendConfigTelemetry(
        frame_mode="fixed_port_chart",
        curvature_backend="none",
        metric_backend="tensor_exponential",
        spark_backend="mechanical_saturation_with_instability_or_column_proxy",
        birth_backend="outward_flux_parent_selection",
        growth_parent_eligibility_mode="legacy_any_inactive_port",
        coarse_graining_backend="exact_column_profile",
        boundary_mode="prune",
        budget_preservation_policy="uniform_shift_with_positive_fallback",
        expansion_distribution_mode="equal",
        expansion_schedule="instantaneous",
        edge_label_selection="all",
    )


def _port_chart() -> telemetry.GRC9PortChartSummary:
    return telemetry.GRC9PortChartSummary(
        num_nodes=4,
        num_port_edges=3,
        active_degree_histogram={0: 1, 1: 2, 9: 1},
        inactive_port_count=33,
        saturated_node_count=1,
        near_saturated_node_count=0,
        row_occupancy_totals=(1, 1, 1),
        column_occupancy_totals=(1, 1, 1),
        saturated_node_ids_sample=(7,),
        inactive_capacity_by_column=(11, 11, 11),
    )


def _row_tensor() -> telemetry.GRC9RowTensorSummary:
    return telemetry.GRC9RowTensorSummary(
        row_tensor_min=0.1,
        row_tensor_max=3.0,
        row_tensor_mean=1.4,
        row_tensor_anisotropy_max=2.9,
        density_term_mean=0.5,
        row_mismatch_term_max=1.75,
        flux_feedback_term_mean=0.2,
        row_tensor_by_node_sample={7: (0.1, 0.2, 0.3)},
    )


def _column_diagnostic() -> telemetry.GRC9ColumnDiagnosticSummary:
    return telemetry.GRC9ColumnDiagnosticSummary(
        column_diagnostic_min_abs=0.001,
        column_diagnostic_mean_abs=0.25,
        column_proxy_candidate_count=1,
        sign_crossing_candidate_count=0,
        column_profile_sparsity=0.6,
        column_diagnostic_by_candidate={7: (0.001, 0.2, 0.3)},
        spark_calibration=telemetry.GRC9SparkCalibrationTelemetry(
            spark_threshold=0.01,
            spark_threshold_mode="absolute",
            burn_in_M_H=1.0,
            burn_in_M_C=0.5,
        ),
    )


def _transport() -> telemetry.GRC9TransportSummary:
    return telemetry.GRC9TransportSummary(
        conductance_min=0.1,
        conductance_max=1.0,
        conductance_mean=0.4,
        flux_abs_sum=2.5,
        flux_signed_balance=-0.2,
        positive_flux_edge_count=2,
        negative_flux_edge_count=1,
        strongest_flux_edges_sample=(
            {"edge_id": 3, "flux": 1.5, "from_node_id": 1, "to_node_id": 7},
        ),
        potential_min=-1.0,
        potential_max=2.0,
        potential_range=3.0,
        label_availability=telemetry.GRC9LabelAvailability(
            overall="all",
            geometric_length_available=True,
            temporal_delay_available=True,
            flux_coupling_available=True,
        ),
        label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "fixed_port_chart",
            "flux_coupling": "flux_magnitude",
        },
    )


def _identity() -> telemetry.GRC9IdentityAbundanceSummary:
    return telemetry.GRC9IdentityAbundanceSummary(
        sink_count=2,
        basin_count=2,
        basin_size_min=1,
        basin_size_max=3,
        basin_size_mean=2.0,
        scale_weighted_abundance=4.0,
        scale_weighted_abundance_gamma=1.5,
        successor_self_loop_count=2,
        successor_tie_count=1,
        successor_tie_break_policy="ascending_neighbor_then_edge_id",
    )


def _coarse() -> telemetry.GRC9CoarseGrainingSummary:
    return telemetry.GRC9CoarseGrainingSummary(
        coarse_fields_list=("conductance", "signed_flux"),
        coarse_cache_state="warm",
        coarse_cache_invalidation_reason="flux_recomputation",
        exact_split_supported_fields=("conductance", "signed_flux"),
        signed_flux_mode="signed_flux_split",
        coarse_field_types={
            "conductance": "nonnegative",
            "signed_flux": "signed_lossless",
        },
        max_reconstruction_error_by_field={"conductance": 0.0},
        column_total_sparsity_by_field={"conductance": 0.25},
        dominant_mode_profile_count=1,
        profile_compression_mode="full",
    )


def _budget() -> telemetry.GRC9BudgetCorrectionSummary:
    return telemetry.GRC9BudgetCorrectionSummary(
        budget_current=10.0,
        budget_target=10.0,
        budget_error=0.0,
        budget_preservation_policy="uniform_shift_with_positive_fallback",
        last_budget_correction_path="uniform_shift",
        uniform_shift_delta=0.0,
        simplex_projection_applied=False,
        negative_clamp_count=0,
    )


class GRC9TelemetryContractTest(unittest.TestCase):
    """Validate the Phase T-GRC9 Iteration 2 contract module."""

    def test_step_extension_mapping_is_explicit_and_wrapped_under_family_key(self) -> None:
        extension = telemetry.GRC9StepTelemetryExtension(
            lane_context=_lane_context(),
            backend_config=_backend_config(),
            port_chart=_port_chart(),
            row_tensor=_row_tensor(),
            column_diagnostic=_column_diagnostic(),
            transport=_transport(),
            identity_abundance=_identity(),
            coarse_graining=_coarse(),
            budget_correction=_budget(),
        )

        family_extensions = telemetry.grc9_step_family_extensions(extension)
        payload = family_extensions["grc9"]

        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        self.assertEqual(
            "fixed_port_chart",
            payload["backend_config"]["frame_mode"],
        )
        self.assertEqual("equal", payload["backend_config"]["expansion_distribution_mode"])
        self.assertEqual([1, 1, 1], payload["port_chart"]["row_occupancy_totals"])
        self.assertEqual([1, 1, 1], payload["port_chart"]["column_occupancy_totals"])
        self.assertEqual(2.9, payload["row_tensor"]["row_tensor_anisotropy_max"])
        self.assertEqual(
            0.01,
            payload["column_diagnostic"]["spark_calibration"]["spark_threshold"],
        )
        self.assertTrue(
            payload["transport"]["label_availability"]["temporal_delay_available"]
        )
        self.assertEqual(1, payload["identity_abundance"]["successor_tie_count"])
        self.assertEqual(
            "signed_lossless",
            payload["coarse_graining"]["coarse_field_types"]["signed_flux"],
        )
        self.assertEqual(
            "uniform_shift",
            payload["budget_correction"]["last_budget_correction_path"],
        )

    def test_event_classification_extracts_spark_expansion_and_growth_evidence(self) -> None:
        spark = telemetry.classify_grc9_event_extension(
            "spark",
            {
                "sink_node_id": 7,
                "spark_kind": "saturation_column_proxy",
                "active_degree": 9,
                "instability": 0.42,
                "min_abs_column": 0.001,
                "target_effective_degree": 30,
            },
            lane_context=_lane_context(),
        )
        spark_payload = telemetry.grc9_event_family_extensions(spark)["grc9"]

        self.assertEqual("spark", spark_payload["event_domain"])
        self.assertEqual("confirmed", spark_payload["lifecycle_stage"])
        self.assertEqual(7, spark_payload["primary_node_id"])
        self.assertTrue(spark_payload["spark_evidence"]["saturation_gate_pass"])
        self.assertEqual(
            "saturation_column_proxy",
            spark_payload["spark_evidence"]["spark_kind"],
        )

        expansion = telemetry.classify_grc9_event_extension(
            "expansion",
            {
                "sink_node_id": 7,
                "expansion_id": "spark-0-7",
                "target_effective_degree": 30,
                "module_node_ids": [10, 11, 12, 13],
                "internal_edge_ids": [20, 21, 22],
                "distribution_weights": [1 / 3, 1 / 3, 1 / 3],
                "budget_error": 0.0,
                "reassignment_map": {"1": {"to_node_id": 11}},
            },
        )
        expansion_payload = expansion.to_mapping()

        self.assertEqual("expansion", expansion_payload["event_domain"])
        self.assertTrue(expansion_payload["port_mutation"])
        self.assertEqual("spark-0-7", expansion_payload["registry_key"])
        self.assertEqual(
            [11, 12, 13],
            expansion_payload["expansion_evidence"]["satellite_node_ids"],
        )
        self.assertAlmostEqual(
            1.0,
            expansion_payload["expansion_evidence"]["coherence_transfer_ratios_sum"],
        )

        growth = telemetry.classify_grc9_event_extension(
            "growth",
            {
                "parent_node_id": 3,
                "child_node_id": 8,
                "parent_port_id": 2,
                "child_port_id": 1,
                "outward_flux": 0.75,
                "birth_probability": 0.9,
                "growth_parent_eligibility_mode": "grc9_front_capacity",
                "growth_parent_capacity_source": "spark_refinement_front",
            },
        )
        growth_payload = growth.to_mapping()

        self.assertEqual("growth", growth_payload["event_domain"])
        self.assertEqual("child_attached", growth_payload["lifecycle_stage"])
        self.assertEqual(2, growth_payload["growth_evidence"]["selected_parent_port"])
        self.assertEqual(0.9, growth_payload["growth_evidence"]["birth_probability"])
        self.assertEqual(
            "grc9_front_capacity",
            growth_payload["growth_evidence"]["parent_eligibility_mode"],
        )
        self.assertEqual(
            "spark_refinement_front",
            growth_payload["growth_evidence"]["parent_capacity_source"],
        )
        self.assertTrue(
            growth_payload["growth_evidence"]["front_growth_provenance_present"]
        )
        self.assertFalse(growth_payload["growth_evidence"]["legacy_broad_growth"])

        missing_provenance = telemetry.classify_grc9_event_extension(
            "growth",
            {
                "parent_node_id": 3,
                "child_node_id": 8,
                "parent_port_id": 2,
                "child_port_id": 1,
                "outward_flux": 0.75,
                "birth_probability": 0.9,
                "growth_parent_eligibility_mode": "grc9_front_capacity",
            },
        ).to_mapping()
        self.assertFalse(
            missing_provenance["growth_evidence"]["front_growth_provenance_present"]
        )
        self.assertEqual(
            "legacy_any_inactive_port",
            missing_provenance["growth_evidence"]["parent_capacity_source"],
        )

        pressure_boundary = telemetry.classify_grc9_event_extension(
            "growth",
            {
                "parent_node_id": 7,
                "child_node_id": 9,
                "parent_port_id": 4,
                "child_port_id": 1,
                "outward_flux": 2.0,
                "birth_probability": 0.75,
                "growth_parent_eligibility_mode": "grc9_front_capacity",
                "growth_parent_capacity_source": "pressure_boundary",
            },
            lane_context=_lane_context(),
        )
        pressure_payload = telemetry.grc9_event_family_extensions(pressure_boundary)[
            "grc9"
        ]

        self.assertEqual(
            "pressure_boundary",
            pressure_payload["growth_evidence"]["parent_capacity_source"],
        )
        self.assertTrue(
            pressure_payload["growth_evidence"]["front_growth_provenance_present"]
        )
        self.assertFalse(pressure_payload["growth_evidence"]["legacy_broad_growth"])

    def test_unknown_event_classifies_to_other_without_subjects(self) -> None:
        extension = telemetry.classify_grc9_event_extension("transport_refresh", {})
        payload = extension.to_mapping()

        self.assertEqual("other", payload["event_domain"])
        self.assertEqual("other", payload["lifecycle_stage"])
        self.assertFalse(payload["topology_mutation"])
        self.assertFalse(payload["port_mutation"])
        self.assertNotIn("primary_node_id", payload)
        self.assertNotIn("spark_evidence", payload)

    def test_budget_and_coarse_event_classification_preserves_reserved_taxonomy(
        self,
    ) -> None:
        budget = telemetry.classify_grc9_event_extension(
            "budget_correction",
            {
                "budget_preservation_policy": "uniform_shift_with_positive_fallback",
                "correction_path": "uniform_shift",
                "uniform_shift_delta": 0.125,
                "simplex_projection_applied": False,
                "budget_error_before": 0.25,
                "budget_error_after": 0.0,
            },
        )
        budget_payload = budget.to_mapping()

        self.assertEqual("budget", budget_payload["event_domain"])
        self.assertEqual("corrected", budget_payload["lifecycle_stage"])
        self.assertTrue(budget_payload["budget_mutation"])
        self.assertEqual(
            "uniform_shift",
            budget_payload["budget_evidence"]["correction_path"],
        )
        self.assertEqual(0.0, budget_payload["budget_evidence"]["budget_error_after"])

        coarse = telemetry.classify_grc9_event_extension(
            "coarse_cache_invalidation",
            {"cache_key": "exact_column_profile:conductance"},
        )
        coarse_payload = coarse.to_mapping()

        self.assertEqual("coarse", coarse_payload["event_domain"])
        self.assertEqual("invalidated", coarse_payload["lifecycle_stage"])
        self.assertEqual("exact_column_profile:conductance", coarse_payload["registry_key"])

    def test_run_summary_extension_has_fixed_lifecycle_and_mechanical_summaries(
        self,
    ) -> None:
        extension = telemetry.GRC9RunSummaryExtension(
            lane_context=_lane_context(),
            backend_summary=_backend_config(),
            final_port_chart_summary=_port_chart(),
            final_row_tensor_summary=_row_tensor(),
            final_column_diagnostic_summary=_column_diagnostic(),
            final_transport_summary=_transport(),
            final_identity_summary=_identity(),
            final_coarse_graining_summary=_coarse(),
            lifecycle_event_counts=telemetry.GRC9LifecycleEventCounts(
                spark_candidate_count=2,
                spark_confirmed_count=1,
                spark_column_proxy_count=1,
                expansion_count=1,
                growth_count=2,
                budget_uniform_correction_count=3,
            ),
            expansion_summary=telemetry.GRC9ExpansionSummary(
                final_expansion_registry_size=1,
                total_module_nodes_created=4,
                total_boundary_reassignments=9,
                max_module_node_count=4,
                identity_fission_candidate_count=1,
                identity_fission_confirmed_count=0,
                identity_fission_max_persistence_steps=0,
            ),
            growth_summary=telemetry.GRC9GrowthSummary(
                growth_count=2,
                unique_growth_parent_count=2,
                lowest_port_attachment_count=2,
                front_capacity_growth_count=1,
                pressure_boundary_growth_count=1,
                legacy_broad_growth_count=1,
                birth_probability_min=0.25,
                birth_probability_max=0.9,
                birth_probability_mean=0.575,
            ),
            calibration_summary=telemetry.GRC9CalibrationSummary(
                spark_threshold=0.01,
                spark_threshold_mode="absolute",
                burn_in_M_H=1.0,
                burn_in_M_C=0.5,
                spark_rate_observed=0.25,
            ),
            diagnostic_status_summary={
                "boundary_barrier": "reserved_future",
                "temporal_delay": "artifact_backed",
            },
        )

        family_extensions = telemetry.grc9_run_summary_family_extensions(extension)
        payload = family_extensions["grc9"]

        self.assertEqual(1, payload["lifecycle_event_counts"]["expansion_count"])
        self.assertEqual(4, payload["expansion_summary"]["max_module_node_count"])
        self.assertEqual(
            0,
            payload["expansion_summary"]["identity_fission_confirmed_count"],
        )
        self.assertEqual(2, payload["growth_summary"]["lowest_port_attachment_count"])
        self.assertEqual(1, payload["growth_summary"]["front_capacity_growth_count"])
        self.assertEqual(1, payload["growth_summary"]["pressure_boundary_growth_count"])
        self.assertEqual(1, payload["growth_summary"]["legacy_broad_growth_count"])
        self.assertEqual(0.25, payload["calibration_summary"]["spark_rate_observed"])
        self.assertEqual(
            "reserved_future",
            payload["diagnostic_status_summary"]["boundary_barrier"],
        )

    def test_budget_evidence_and_calibration_validation_are_directly_covered(self) -> None:
        evidence = telemetry.GRC9BudgetEvidence(
            budget_preservation_policy="uniform_shift_with_positive_fallback",
            correction_path="uniform_shift",
            uniform_shift_delta=0.1,
            simplex_projection_applied=False,
            budget_error_before=0.1,
            budget_error_after=0.0,
        )
        self.assertEqual(0.1, evidence.to_mapping()["budget_error_before"])

        calibration = telemetry.GRC9CalibrationSummary(
            spark_threshold=0.01,
            spark_threshold_mode="absolute",
            burn_in_M_H=1.0,
            burn_in_M_C=0.5,
            spark_rate_observed=0.25,
        )
        self.assertEqual("absolute", calibration.to_mapping()["spark_threshold_mode"])

        with self.assertRaises(ValueError):
            telemetry.GRC9BudgetEvidence(budget_error_before=float("nan"))

        with self.assertRaises(ValueError):
            telemetry.GRC9CalibrationSummary(
                spark_threshold=0.01,
                spark_threshold_mode="",
            )

        with self.assertRaises(ValueError):
            telemetry.GRC9CalibrationSummary(
                spark_threshold=0.01,
                spark_threshold_mode="absolute",
                spark_rate_observed=-0.1,
            )

    def test_validation_rejects_negative_counts_invalid_modes_and_bad_ratios(self) -> None:
        with self.assertRaises(ValueError):
            telemetry.GRC9PortChartSummary(
                num_nodes=-1,
                num_port_edges=0,
                active_degree_histogram={},
                inactive_port_count=0,
                saturated_node_count=0,
                near_saturated_node_count=0,
                row_occupancy_totals=(0, 0, 0),
                column_occupancy_totals=(0, 0, 0),
            )

        with self.assertRaises(ValueError):
            telemetry.GRC9BackendConfigTelemetry(
                frame_mode="fixed_port_chart",
                curvature_backend="none",
                metric_backend="tensor_exponential",
                spark_backend="mechanical",
                birth_backend="outward_flux_parent_selection",
                growth_parent_eligibility_mode="legacy_any_inactive_port",
                coarse_graining_backend="exact_column_profile",
                boundary_mode="prune",
                budget_preservation_policy="uniform",
                expansion_distribution_mode="equal",
                expansion_schedule="slow",
                edge_label_selection="all",
            )

        with self.assertRaises(ValueError):
            telemetry.GRC9ExpansionEvidence(
                coherence_transfer_ratios=(0.2, 0.2, 0.2),
                coherence_transfer_ratios_sum=0.6,
            )

        with self.assertRaises(ValueError):
            telemetry.GRC9RunSummaryExtension(
                lane_context=_lane_context(),
                backend_summary=_backend_config(),
                final_port_chart_summary=_port_chart(),
                final_row_tensor_summary=_row_tensor(),
                final_column_diagnostic_summary=_column_diagnostic(),
                final_transport_summary=_transport(),
                final_identity_summary=_identity(),
                final_coarse_graining_summary=_coarse(),
                lifecycle_event_counts=telemetry.GRC9LifecycleEventCounts(),
                expansion_summary=telemetry.GRC9ExpansionSummary(0, 0, 0, 0, 0, 0, 0),
                growth_summary=telemetry.GRC9GrowthSummary(0, 0, 0),
                diagnostic_status_summary={"boundary_barrier": "maybe"},
            )


if __name__ == "__main__":
    unittest.main()
