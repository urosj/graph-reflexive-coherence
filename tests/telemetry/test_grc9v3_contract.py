"""Contract tests for the GRC9V3 telemetry extension surface."""

from __future__ import annotations

import json
import unittest

from pygrc import telemetry


def _lane_context() -> telemetry.GRC9V3LaneContext:
    return telemetry.GRC9V3LaneContext(
        source_reference="implementation/Phase-7-RepresentativeRuntime.md",
        fixture_name="appendix_e_cell_division",
        run_role="primary",
        experiment_id="phase-t-grc9v3-test",
    )


def _backend() -> telemetry.GRC9V3BackendConfigTelemetry:
    return telemetry.GRC9V3BackendConfigTelemetry(
        frame_mode="fixed_port_chart",
        hessian_backend="row_basis_diagonal",
        curvature_backend="none",
        choice_backend="sink_compatibility",
        boundary_mode="prune",
        quadrature_mode="unit_measure",
        budget_correction_method="simplex_projection",
        expansion_distribution_mode="custom",
        edge_label_selection="all",
        spark_signed_crossing=False,
        spark_lane=telemetry.GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE,
        default_evolution_provenance={"alpha": "GRCV3 metric law default"},
    )


def _port_chart() -> telemetry.GRC9V3PortChartSummary:
    return telemetry.GRC9V3PortChartSummary(
        num_nodes=16,
        num_port_edges=22,
        active_degree_histogram={1: 8, 2: 4, 3: 2, 4: 2},
        inactive_port_count=122,
        saturated_node_count=0,
        saturated_node_ids_sample=(),
        row_occupancy_totals=(8, 7, 7),
        column_occupancy_totals=(7, 8, 7),
        module_node_count=5,
    )


def _differential() -> telemetry.GRC9V3RowBasisDifferentialSummary:
    return telemetry.GRC9V3RowBasisDifferentialSummary(
        gradient_norm_min=0.0,
        gradient_norm_max=12.0,
        gradient_norm_mean=3.5,
        signed_hessian_min=-1.0,
        signed_hessian_max=4.0,
        signed_hessian_mean=0.75,
        current_min_signed_hessian_min=-1.0,
        hessian_backend="row_basis_diagonal",
        hessian_sign=1,
        previous_min_signed_hessian_available=True,
        weighted_least_squares_hessian_available=True,
        geometric_seed_count=2,
    )


def _identity() -> telemetry.GRC9V3IdentityBasinSummary:
    return telemetry.GRC9V3IdentityBasinSummary(
        sink_count=2,
        basin_count=2,
        basin_size_min=2,
        basin_size_max=5,
        basin_size_mean=3.5,
        geometric_seed_count=2,
        validated_basin_count=2,
        successor_self_loop_count=2,
        module_sink_count=2,
        daughter_sink_count=2,
        basin_mass_summary={"12": 72.0, "16": 36.0},
    )


def _budget() -> telemetry.GRC9V3BudgetCorrectionSummary:
    return telemetry.GRC9V3BudgetCorrectionSummary(
        quadrature_mode="unit_measure",
        budget_correction_method="simplex_projection",
        budget_target=108.0,
        budget_before=108.0,
        budget_after=108.0,
        budget_error=0.0,
        negative_mass_correction=0.0,
        post_expansion_budget_check_available=True,
        budget_target_source="initial_state_sum",
    )


class GRC9V3TelemetryContractTest(unittest.TestCase):
    """Validate Phase T-GRC9V3 Iteration 1 typed contract behavior."""

    def test_step_extension_mapping_is_wrapped_under_grc9v3_family_key(self) -> None:
        extension = telemetry.GRC9V3StepTelemetryExtension(
            lane_context=_lane_context(),
            backend_config=_backend(),
            port_chart=_port_chart(),
            row_basis_differential=_differential(),
            hybrid_tensor=telemetry.GRC9V3HybridTensorSummary(
                tensor_trace_min=1.0,
                tensor_trace_max=8.0,
                tensor_trace_mean=4.0,
                tensor_anisotropy_max=3.0,
                row_mismatch_sum_max=2.0,
                flux_feedback_sum_mean=0.5,
                tensor_hotspot_node_ids_sample=(12, 16),
            ),
            transport=telemetry.GRC9V3TransportSummary(
                base_conductance_min=0.1,
                base_conductance_max=1.0,
                base_conductance_mean=0.6,
                potential_min=-2.0,
                potential_max=3.0,
                flux_abs_sum=12.5,
                positive_flux_edge_count=9,
                negative_flux_edge_count=8,
                label_availability=telemetry.GRC9V3LabelAvailability(
                    geometric_length_available=True,
                    temporal_delay_available=True,
                    flux_coupling_available=True,
                ),
                label_computation_mode={"temporal_delay": "transport_ratio"},
            ),
            identity_basin=_identity(),
            hybrid_spark_state=telemetry.GRC9V3HybridSparkStateSummary(
                hybrid_spark_candidate_count=1,
                completed_hybrid_spark_count=1,
                last_candidate_saturation_gate=True,
                last_candidate_basin_interior_gate=True,
                last_candidate_signed_hessian_gate=True,
                last_child_stabilization_pass=True,
                evaluated_candidate_count=1,
                candidate_pass_rate=1.0,
                last_stabilized_child_node_ids=(12, 16),
                last_module_sink_node_ids=(12, 16),
            ),
            hierarchy_state=telemetry.GRC9V3HierarchyStateSummary(
                hierarchy_root_count=1,
                hierarchy_child_link_count=2,
                max_hierarchy_depth=1,
                last_hierarchy_parent="root",
                last_hierarchy_children=("12", "16"),
            ),
            choice_collapse=telemetry.GRC9V3ChoiceCollapseSummary(
                choice_backend="sink_compatibility",
                choice_regime_count=1,
                collapse_registry_count=1,
                evaluated_node_count=4,
                learning_state_count=1,
                last_collapse_node_id=10,
                last_collapsed_sink_id="12",
            ),
            growth_state=telemetry.GRC9V3GrowthStateSummary(
                birth_rule_mode="outward_flux_pressure",
                parent_selection_mode="deterministic_scan_with_rng_acceptance",
                growth_event_count=0,
            ),
            budget_correction=_budget(),
            coarse_cache=telemetry.GRC9V3CoarseCacheSummary(
                coarse_cache_state="empty",
                coarse_cache_invalidated=True,
                coarse_cache_invalidation_reason="post_semantic_update",
            ),
        )

        family_extensions = telemetry.grc9v3_step_family_extensions(extension)
        payload = family_extensions["grc9v3"]

        self.assertEqual(
            telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        self.assertEqual("appendix_e_cell_division", payload["lane_context"]["fixture_name"])
        self.assertEqual("shared_runtime", payload["backend_config"]["ownership"])
        self.assertEqual("grc9_mechanical", payload["port_chart"]["ownership"])
        self.assertEqual(
            "grcv3_semantic",
            payload["row_basis_differential"]["ownership"],
        )
        self.assertTrue(
            payload["row_basis_differential"][
                "weighted_least_squares_hessian_available"
            ]
        )
        self.assertEqual(2, payload["identity_basin"]["daughter_sink_count"])
        self.assertEqual(
            [12, 16],
            payload["hybrid_spark_state"]["last_stabilized_child_node_ids"],
        )
        json.dumps(payload, sort_keys=True)

    def test_classifier_maps_phase7_event_kinds_to_domain_stage_and_ownership(self) -> None:
        lane_b_candidate = telemetry.classify_grc9v3_event_extension(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_CANDIDATE_EVENT_KIND,
            {
                "candidate_node_id": 0,
                "sink_node_id": 0,
                "spark_lane": telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
                "active_degree": 9,
                "saturation_gate": True,
                "basin_interior_gate": True,
                "gradient_norm": 0.0,
                "signed_hessian_degeneracy_gate": False,
                "min_signed_hessian": 1.0,
                "column_h": [-1.5, 1.0, -2.5],
                "min_abs_column_h": 1.0,
                "min_abs_column_h_column": 2,
                "column_h_threshold_hit": True,
                "column_h_sign_crossing_enabled": False,
                "column_h_sign_crossing_mode": "theory_product",
                "eps_column_h_crossing_zero": 0.0,
                "previous_column_h_status": "unavailable_storage_disabled",
                "previous_column_h_values": None,
                "column_h_sign_crossing_hit": False,
                "column_h_sign_crossing_columns": [],
                "column_h_branch_hit": True,
                "column_h_gate_hit": True,
                "lane_b_candidate_hit": True,
                "gate_reasons": ["column_h_threshold_hit"],
            },
            lane_context=_lane_context(),
        )
        candidate_payload = telemetry.grc9v3_event_family_extensions(
            lane_b_candidate
        )["grc9v3"]

        self.assertEqual("spark", candidate_payload["event_domain"])
        self.assertEqual("candidate", candidate_payload["lifecycle_stage"])
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            candidate_payload["spark_evidence"]["spark_lane"],
        )
        self.assertEqual(
            [-1.5, 1.0, -2.5],
            candidate_payload["spark_evidence"]["column_h"],
        )
        self.assertTrue(candidate_payload["spark_evidence"]["column_h_branch_hit"])
        self.assertEqual(
            ["column_h_threshold_hit"],
            candidate_payload["spark_evidence"]["gate_reasons"],
        )

        expansion = telemetry.classify_grc9v3_event_extension(
            "hybrid_mechanical_expansion",
            {
                "sink_node_id": 0,
                "expansion_id": "hybrid-spark-0-0",
                "target_effective_degree": 16,
                "requested_node_count": 2,
                "module_node_ids": [12, 13, 14, 15, 16],
                "internal_edge_ids": [21, 22],
                "distribution_weights": [0.5, 0.0, 0.5],
                "budget_before": 108.0,
                "budget_after": 108.0,
                "budget_error": 0.0,
                "reassignment_map": {"1": {"to_node_id": 13}},
            },
            lane_context=_lane_context(),
        )

        payload = telemetry.grc9v3_event_family_extensions(expansion)["grc9v3"]

        self.assertEqual("expansion", payload["event_domain"])
        self.assertEqual("module_created", payload["lifecycle_stage"])
        self.assertEqual("grc9_mechanical", payload["ownership"])
        self.assertTrue(payload["topology_mutation"])
        self.assertTrue(payload["budget_mutation"])
        self.assertEqual("hybrid-spark-0-0", payload["expansion_id"])
        self.assertEqual(5, len(payload["expansion_evidence"]["module_node_ids"]))
        self.assertEqual(1, payload["expansion_evidence"]["reassignment_count"])

    def test_completed_spark_and_collapse_have_semantic_ownership(self) -> None:
        completed = telemetry.classify_grc9v3_event_extension(
            "hybrid_spark_completed",
            {
                "stabilized_child_node_ids": [12, 16],
                "stable_child_basin_count": 2,
                "hierarchy_parent": "root",
                "hierarchy_children": ["12", "16"],
            },
        ).to_mapping()
        collapse = telemetry.classify_grc9v3_event_extension(
            "collapse",
            {
                "node_id": 10,
                "collapsed_sink_id": "12",
                "epsilon_choice": 0.001,
                "epsilon_collapse": 0.001,
                "winner_margin": 0.9,
            },
        ).to_mapping()

        self.assertEqual("grc9v3_hybrid", completed["ownership"])
        self.assertEqual("spark", completed["event_domain"])
        self.assertEqual("completed", completed["lifecycle_stage"])
        self.assertEqual("grcv3_semantic", collapse["ownership"])
        self.assertEqual("collapse", collapse["event_domain"])
        self.assertEqual("collapsed", collapse["lifecycle_stage"])

    def test_unknown_event_classifies_to_other_without_subjects(self) -> None:
        payload = telemetry.classify_grc9v3_event_extension(
            "transport_refresh",
            {},
        ).to_mapping()

        self.assertEqual("other", payload["event_domain"])
        self.assertEqual("other", payload["lifecycle_stage"])
        self.assertEqual("shared_runtime", payload["ownership"])
        self.assertFalse(payload["topology_mutation"])
        self.assertFalse(payload["hierarchy_mutation"])
        self.assertFalse(payload["budget_mutation"])
        self.assertNotIn("primary_node_id", payload)

    def test_run_summary_extension_has_fixed_lifecycle_and_appendix_e_surface(self) -> None:
        extension = telemetry.GRC9V3RunSummaryExtension(
            lane_context=_lane_context(),
            backend_summary=_backend(),
            final_port_chart_summary=_port_chart(),
            final_differential_summary=_differential(),
            final_identity_basin_summary=_identity(),
            final_hierarchy_summary=telemetry.GRC9V3HierarchyStateSummary(
                hierarchy_root_count=1,
                hierarchy_child_link_count=2,
                max_hierarchy_depth=1,
                last_hierarchy_parent="root",
                last_hierarchy_children=("12", "16"),
            ),
            final_choice_collapse_summary=telemetry.GRC9V3ChoiceCollapseSummary(
                choice_backend="sink_compatibility",
                choice_regime_count=1,
                collapse_registry_count=1,
                evaluated_node_count=4,
                learning_state_count=1,
            ),
            final_budget_summary=_budget(),
            lifecycle_event_counts=telemetry.GRC9V3LifecycleEventCounts(
                hybrid_spark_candidate_count=1,
                hybrid_mechanical_expansion_count=1,
                hybrid_spark_completed_count=1,
                choice_detected_count=3,
                collapse_count=1,
                growth_count=3,
                front_capacity_growth_count=2,
                pressure_boundary_growth_count=1,
                legacy_broad_growth_count=1,
            ),
            representative_appendix_e_summary=telemetry.GRC9V3AppendixESummary(
                fixture_name="appendix_e_cell_division",
                spark_completed=True,
                daughter_sink_count=2,
                daughter_sink_node_ids=(12, 16),
                module_basin_mass={"12": 72.0, "16": 36.0},
                hierarchy_parent="root",
                hierarchy_children=("12", "16"),
                budget_preserved=True,
                replay_digest_match=True,
            ),
        )

        payload = telemetry.grc9v3_run_summary_family_extensions(extension)["grc9v3"]

        self.assertEqual(1, payload["lifecycle_event_counts"]["collapse_count"])
        self.assertEqual(2, payload["lifecycle_event_counts"]["front_capacity_growth_count"])
        self.assertEqual(
            1,
            payload["lifecycle_event_counts"]["pressure_boundary_growth_count"],
        )
        self.assertEqual(1, payload["lifecycle_event_counts"]["legacy_broad_growth_count"])
        self.assertEqual(
            [12, 16],
            payload["representative_appendix_e_summary"]["daughter_sink_node_ids"],
        )
        self.assertTrue(
            payload["representative_appendix_e_summary"]["replay_digest_match"]
        )

    def test_validation_rejects_invalid_contract_values(self) -> None:
        with self.assertRaises(ValueError):
            telemetry.GRC9V3RowBasisDifferentialSummary(
                gradient_norm_min=0.0,
                gradient_norm_max=1.0,
                gradient_norm_mean=0.5,
                signed_hessian_min=-1.0,
                signed_hessian_max=1.0,
                signed_hessian_mean=0.0,
                current_min_signed_hessian_min=-1.0,
                hessian_backend="row_basis_diagonal",
                hessian_sign=0,
            )
        with self.assertRaises(ValueError):
            telemetry.GRC9V3HybridSparkStateSummary(
                hybrid_spark_candidate_count=1,
                completed_hybrid_spark_count=0,
                last_candidate_saturation_gate=False,
                last_candidate_basin_interior_gate=None,
                last_candidate_signed_hessian_gate=None,
                last_child_stabilization_pass=False,
                candidate_pass_rate=1.5,
            )


if __name__ == "__main__":
    unittest.main()
