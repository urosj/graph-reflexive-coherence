"""Contract tests for the GRCV3 telemetry extension surface."""

from __future__ import annotations

import unittest

from pygrc import telemetry


class GRCV3TelemetryContractTest(unittest.TestCase):
    """Validate the Phase T Iteration 16 GRCV3 telemetry contract."""

    def test_step_extension_mapping_is_explicit_and_wrapped_under_family_key(self) -> None:
        extension = telemetry.GRCV3StepTelemetryExtension(
            backend_summary=telemetry.GRCV3BackendTelemetry(
                geometry_backend="induced_local_frame",
                differential_backend="weighted_least_squares",
                metric_backend="tensor_exponential",
                spark_backend="signed_hessian_plus_attractor_delta",
                hierarchy_backend="basin_parent_child",
                choice_backend="sink_compatibility",
            ),
            signed_hessian=telemetry.GRCV3SignedHessianTelemetry(hessian_sign=1),
            basin_summary=telemetry.GRCV3BasinSummary(
                attributed_node_count=7,
                active_basin_count=3,
                geometric_seed_count=2,
                geometric_validated_basin_count=2,
                max_hierarchy_depth=1,
            ),
            spark_state=telemetry.GRCV3SparkStateSummary(
                split_registry_size=2,
                active_split_count=1,
                confirmed_split_count=1,
                pending_spark_count=1,
            ),
            hierarchy_state=telemetry.GRCV3HierarchySummary(
                hierarchy_root_count=1,
                hierarchy_node_count=3,
                child_basin_link_count=2,
            ),
            choice_state=telemetry.GRCV3ChoiceStateSummary(
                choice_regime_count=1,
                collapse_registry_count=0,
                evaluated_node_count=4,
            ),
            frontier_birth_state=telemetry.GRCV3FrontierBirthStateSummary(
                frontier_birth_mode="disabled",
                frontier_birth_rule="disabled",
                frontier_candidate_count=0,
                pressure_boundary_candidate_count=0,
                frontier_birth_count=0,
                pressure_boundary_birth_count=0,
            ),
            transient_landscape=telemetry.GRCV3TransientLandscapeStepSummary(
                monitoring_surface_kind="transfer_mediation",
                observed_sites=(
                    telemetry.GRCV3ObservedInteriorSite(
                        primitive_id="spindle_core",
                        node_id=7,
                        gradient_norm=2.5e-4,
                        min_signed_eigenvalue=7.5e-4,
                        max_signed_eigenvalue=1.2,
                        weak_mode_signed_curvature=7.5e-4,
                        gradient_gate_pass=True,
                        geometric_validation_pass=False,
                        spark_candidate_regime=True,
                    ),
                ),
            ),
        )

        family_extensions = telemetry.grcv3_step_family_extensions(extension)
        payload = family_extensions["grcv3"]

        self.assertEqual(
            telemetry.GRCV3_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        self.assertEqual(
            "weighted_least_squares",
            payload["backend_summary"]["differential_backend"],
        )
        self.assertEqual(1, payload["signed_hessian"]["hessian_sign"])
        self.assertEqual(3, payload["basin_summary"]["active_basin_count"])
        self.assertEqual(2, payload["spark_state"]["split_registry_size"])
        self.assertEqual(2, payload["hierarchy_state"]["child_basin_link_count"])
        self.assertEqual(4, payload["choice_state"]["evaluated_node_count"])
        self.assertEqual(
            "disabled",
            payload["frontier_birth_state"]["frontier_birth_mode"],
        )
        self.assertEqual(
            "transfer_mediation",
            payload["transient_landscape"]["monitoring_surface_kind"],
        )
        self.assertEqual(
            "spindle_core",
            payload["transient_landscape"]["observed_sites"][0]["primitive_id"],
        )

    def test_event_extension_classification_extracts_domain_stage_and_subjects(self) -> None:
        extension = telemetry.classify_grcv3_event_extension(
            "split_init",
            {
                "parent_node_id": 9,
                "parent_basin_id": "basin-9",
                "registry_key": "split:4:9:0",
            },
        )

        payload = telemetry.grcv3_event_family_extensions(extension)["grcv3"]

        self.assertEqual("split", payload["event_domain"])
        self.assertEqual("init", payload["lifecycle_stage"])
        self.assertTrue(payload["topology_mutation"])
        self.assertTrue(payload["hierarchy_mutation"])
        self.assertEqual(9, payload["primary_node_id"])
        self.assertEqual("basin-9", payload["primary_basin_id"])
        self.assertEqual("split:4:9:0", payload["registry_key"])

    def test_frontier_birth_event_classifies_to_birth_domain(self) -> None:
        extension = telemetry.classify_grcv3_event_extension(
            "frontier_birth",
            {
                "parent_node_id": 9,
                "child_node_id": 10,
                "frontier_source": "pressure_boundary",
            },
        )

        payload = telemetry.grcv3_event_family_extensions(extension)["grcv3"]

        self.assertEqual("birth", payload["event_domain"])
        self.assertEqual("created", payload["lifecycle_stage"])
        self.assertTrue(payload["topology_mutation"])
        self.assertTrue(payload["hierarchy_mutation"])
        self.assertEqual(9, payload["primary_node_id"])

    def test_unknown_event_classifies_to_other_without_subjects(self) -> None:
        extension = telemetry.classify_grcv3_event_extension("transport_refresh", {})
        payload = extension.to_mapping()

        self.assertEqual("other", payload["event_domain"])
        self.assertEqual("other", payload["lifecycle_stage"])
        self.assertFalse(payload["topology_mutation"])
        self.assertFalse(payload["hierarchy_mutation"])
        self.assertNotIn("primary_node_id", payload)
        self.assertNotIn("primary_basin_id", payload)

    def test_run_summary_extension_has_fixed_lifecycle_event_count_surface(self) -> None:
        extension = telemetry.GRCV3RunSummaryExtension(
            backend_summary=telemetry.GRCV3BackendTelemetry(
                geometry_backend="induced_local_frame",
                differential_backend="weighted_least_squares",
                metric_backend="tensor_exponential",
                spark_backend="signed_hessian_plus_attractor_delta",
                hierarchy_backend="basin_parent_child",
                choice_backend="sink_compatibility",
            ),
            signed_hessian=telemetry.GRCV3SignedHessianTelemetry(hessian_sign=-1),
            final_basin_summary=telemetry.GRCV3BasinSummary(
                attributed_node_count=5,
                active_basin_count=2,
                geometric_seed_count=2,
                geometric_validated_basin_count=2,
                max_hierarchy_depth=1,
            ),
            final_spark_state=telemetry.GRCV3SparkStateSummary(
                split_registry_size=1,
                active_split_count=0,
                confirmed_split_count=1,
                pending_spark_count=0,
            ),
            final_hierarchy_state=telemetry.GRCV3HierarchySummary(
                hierarchy_root_count=1,
                hierarchy_node_count=2,
                child_basin_link_count=1,
            ),
            final_choice_state=telemetry.GRCV3ChoiceStateSummary(
                choice_regime_count=0,
                collapse_registry_count=1,
                evaluated_node_count=3,
            ),
            frontier_birth_summary=telemetry.GRCV3FrontierBirthStateSummary(
                frontier_birth_mode="active_frontier_pressure",
                frontier_birth_rule="bernoulli_outward_flux_pressure",
                frontier_candidate_count=1,
                pressure_boundary_candidate_count=1,
                frontier_birth_count=1,
                pressure_boundary_birth_count=1,
                frontier_sources_observed=("pressure_boundary",),
                outward_flux_pressure_min=2.0,
                outward_flux_pressure_max=2.0,
                outward_flux_pressure_mean=2.0,
                birth_probability_min=0.9,
                birth_probability_max=0.9,
                birth_probability_mean=0.9,
            ),
            lifecycle_event_counts=telemetry.GRCV3LifecycleEventCounts(
                spark_candidate_count=2,
                spark_pending_count=1,
                spark_confirmed_count=1,
                split_init_count=1,
                split_progress_count=2,
                split_complete_count=1,
                choice_detected_count=1,
                choice_resolved_count=1,
                collapse_count=1,
                frontier_birth_count=1,
            ),
            transient_landscape=telemetry.GRCV3TransientLandscapeRunSummary(
                monitoring_surface_kind="transfer_mediation",
                monitored_node_ids_by_primitive_id={"spindle_core": 7},
                surface_realization_summary={
                    "spindle_core": {
                        "mediation_mode": "guarded_pairs",
                        "probe_guard_class": "guarded_center",
                    }
                },
                primitive_summaries=(
                    telemetry.GRCV3TransientLandscapePrimitiveSummary(
                        primitive_id="spindle_core",
                        node_id=7,
                        initial_gradient_norm=0.45,
                        min_gradient_norm=2.5e-4,
                        final_gradient_norm=3.0e-4,
                        initial_min_signed_eigenvalue=0.9,
                        min_signed_eigenvalue=7.5e-4,
                        final_min_signed_eigenvalue=1.1e-3,
                        initial_weak_mode_signed_curvature=0.9,
                        min_weak_mode_signed_curvature=7.5e-4,
                        final_weak_mode_signed_curvature=1.1e-3,
                        first_gradient_gate_pass_step=2,
                        first_spark_candidate_step=2,
                        first_spark_step=2,
                        first_split_init_step=2,
                    ),
                ),
                event_aligned_observations=(
                    telemetry.GRCV3EventAlignedLandscapeObservation(
                        event_kind="spark_candidate",
                        step_index=2,
                        observed_sites=(
                            telemetry.GRCV3ObservedInteriorSite(
                                primitive_id="spindle_core",
                                node_id=7,
                                gradient_norm=2.5e-4,
                                min_signed_eigenvalue=7.5e-4,
                                max_signed_eigenvalue=1.2,
                                weak_mode_signed_curvature=7.5e-4,
                                gradient_gate_pass=True,
                                geometric_validation_pass=False,
                                spark_candidate_regime=True,
                            ),
                        ),
                    ),
                ),
            ),
        )

        family_extensions = telemetry.grcv3_run_summary_family_extensions(extension)
        payload = family_extensions["grcv3"]

        self.assertEqual(-1, payload["signed_hessian"]["hessian_sign"])
        self.assertEqual(1, payload["final_hierarchy_state"]["hierarchy_root_count"])
        self.assertEqual(2, payload["lifecycle_event_counts"]["spark_candidate_count"])
        self.assertEqual(1, payload["lifecycle_event_counts"]["collapse_count"])
        self.assertEqual(1, payload["lifecycle_event_counts"]["frontier_birth_count"])
        self.assertEqual(
            1,
            payload["frontier_birth_summary"]["pressure_boundary_birth_count"],
        )
        self.assertEqual(
            "transfer_mediation",
            payload["transient_landscape"]["monitoring_surface_kind"],
        )
        self.assertEqual(
            2,
            payload["transient_landscape"]["event_aligned_observations"][0]["step_index"],
        )

    def test_hessian_sign_validation_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            telemetry.GRCV3SignedHessianTelemetry(hessian_sign=0)


if __name__ == "__main__":
    unittest.main()
