"""Builder tests for GRC9V3 telemetry extension payloads."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult, canonicalize_json_value, digest_snapshot
from pygrc.telemetry._grc9v3_extensions import (
    _build_grc9v3_event_extension,
    _build_grc9v3_event_extensions,
    _build_grc9v3_run_summary_extension,
    _build_grc9v3_step_extension,
)
from pygrc.telemetry.grcl9v3_replay import _checkpoint_node_overlay
from tests.models.test_grc_9_v3_column_h_assisted import _column_h_state, _config
from scripts.run_grc9v3_representative_runtime import (
    DEFAULT_FIXTURE_NAME,
    build_appendix_e_cell_division_params,
    build_appendix_e_cell_division_state,
    build_representative_hybrid_model,
)


class GRC9V3TelemetryExtensionBuilderTest(unittest.TestCase):
    """Validate private Phase T-GRC9V3 telemetry builders."""

    def test_step_extension_from_representative_state_is_deterministic_and_json_safe(
        self,
    ) -> None:
        model = build_representative_hybrid_model()
        step_result = model.step()
        before_digest = digest_snapshot(model.snapshot())
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            fixture_name=DEFAULT_FIXTURE_NAME,
            run_role="representative",
            experiment_id="phase_t_grc9v3_iter2_builder",
            representative_lane_name="appendix_e_cell_division",
        )

        extension_a = _build_grc9v3_step_extension(model, lane_context=lane_context)
        extension_b = _build_grc9v3_step_extension(model, lane_context=lane_context)
        self.assertEqual(extension_a.to_mapping(), extension_b.to_mapping())
        self.assertEqual(before_digest, digest_snapshot(model.snapshot()))

        family_extensions = telemetry.grc9v3_step_family_extensions(extension_a)
        payload = family_extensions["grc9v3"]
        self.assertEqual(
            telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        self.assertEqual(
            "custom",
            payload["backend_config"]["expansion_distribution_mode"],
        )
        self.assertEqual(
            telemetry.GRC9V3_CURRENT_HYBRID_SIGNED_HESSIAN_SPARK_LANE,
            payload["backend_config"]["spark_lane"],
        )
        self.assertNotIn("spark_lane_version", payload["backend_config"])
        self.assertEqual(
            "reserved_until_boundary_barrier_capability",
            payload["backend_config"]["reserved_modes"]["boundary_barrier"],
        )
        self.assertEqual(
            "row_basis_diagonal",
            payload["row_basis_differential"]["hessian_backend"],
        )
        self.assertFalse(
            payload["row_basis_differential"]["weighted_least_squares_hessian_available"]
        )
        self.assertEqual(1, payload["row_basis_differential"]["hessian_sign"])
        self.assertGreater(payload["port_chart"]["num_nodes"], 0)
        self.assertEqual(1, payload["hybrid_spark_state"]["completed_hybrid_spark_count"])
        self.assertTrue(payload["hybrid_spark_state"]["last_child_stabilization_pass"])
        self.assertGreaterEqual(payload["identity_basin"]["daughter_sink_count"], 1)
        self.assertTrue(
            payload["budget_correction"]["post_expansion_budget_check_available"]
        )
        self.assertEqual(
            "post_semantic_update",
            payload["coarse_cache"]["coarse_cache_invalidation_reason"],
        )

        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9v3-iter2-builder",
            model_family="grc9v3",
            params_identity=model.get_params().params_hash,
            seed_name=DEFAULT_FIXTURE_NAME,
            seed_source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            seed_path="synthetic/grc9v3/appendix_e_cell_division",
            rng_seed=0,
            requested_steps=1,
        )
        row = telemetry.step_row_from_step_result(
            step_result,
            identity=identity,
            family_extensions=family_extensions,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            step_path = Path(temp_dir) / "steps.jsonl"
            telemetry.save_step_rows(step_path, (row,))
            loaded_row = telemetry.load_step_rows(step_path)[0]

        self.assertEqual(
            canonicalize_json_value(payload),
            canonicalize_json_value(loaded_row.family_extensions["grc9v3"]),
        )

    def test_step_extension_with_missing_runtime_caches_uses_explicit_availability_fields(
        self,
    ) -> None:
        model = build_representative_hybrid_model()
        before_digest = digest_snapshot(model.snapshot())

        extension = _build_grc9v3_step_extension(model)
        payload = telemetry.grc9v3_step_family_extensions(extension)["grc9v3"]

        self.assertEqual(before_digest, digest_snapshot(model.snapshot()))
        self.assertEqual(0.0, payload["row_basis_differential"]["gradient_norm_mean"])
        self.assertEqual(
            False,
            payload["row_basis_differential"]["weighted_least_squares_hessian_available"],
        )
        self.assertEqual(0.0, payload["hybrid_tensor"]["tensor_trace_mean"])
        self.assertFalse(
            payload["transport"]["label_availability"]["geometric_length_available"]
        )
        self.assertFalse(
            payload["transport"]["label_availability"]["temporal_delay_available"]
        )
        self.assertEqual(0, payload["hybrid_spark_state"]["hybrid_spark_candidate_count"])
        self.assertEqual("unavailable", payload["growth_state"]["birth_rule_mode"])
        self.assertEqual("empty", payload["coarse_cache"]["coarse_cache_state"])
        self.assertEqual("none", payload["coarse_cache"]["coarse_cache_invalidation_reason"])
        self.assertEqual(
            "initial_state_sum",
            payload["budget_correction"]["budget_target_source"],
        )

    def test_step_extension_reports_operator_backed_coarse_cache_fields(self) -> None:
        model = build_representative_hybrid_model()
        model.coarse_grain_columns("conductance")

        payload = telemetry.grc9v3_step_family_extensions(
            _build_grc9v3_step_extension(model)
        )["grc9v3"]

        coarse_cache = payload["coarse_cache"]
        self.assertEqual("warm", coarse_cache["coarse_cache_state"])
        self.assertFalse(coarse_cache["coarse_cache_invalidated"])
        self.assertEqual("none", coarse_cache["coarse_cache_invalidation_reason"])
        self.assertEqual("operator_backed", coarse_cache["coarse_cache_refresh_mode"])
        self.assertEqual(["conductance"], coarse_cache["coarse_fields_list"])
        self.assertEqual(
            {"conductance": "nonnegative"},
            coarse_cache["coarse_field_types"],
        )

    def test_step_extension_records_weighted_hessian_backend_availability(self) -> None:
        params = build_appendix_e_cell_division_params()
        params["constitutive_semantic_modes"]["hessian_backend"] = "weighted_least_squares"
        weighted_model = build_representative_hybrid_model().from_state(
            build_appendix_e_cell_division_state(),
            params=params,
        )
        weighted_model.step()

        payload = telemetry.grc9v3_step_family_extensions(
            _build_grc9v3_step_extension(weighted_model)
        )["grc9v3"]

        self.assertEqual(
            "weighted_least_squares",
            payload["row_basis_differential"]["hessian_backend"],
        )
        self.assertTrue(
            payload["row_basis_differential"]["weighted_least_squares_hessian_available"]
        )

    def test_event_extensions_cover_representative_event_taxonomy(self) -> None:
        model = build_representative_hybrid_model()
        first_step = model.step()
        second_step = model.step()
        events = tuple(first_step.events + second_step.events)
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            fixture_name=DEFAULT_FIXTURE_NAME,
            run_role="representative",
        )

        extensions = _build_grc9v3_event_extensions(
            model,
            events,
            lane_context=lane_context,
        )
        family_extensions = tuple(
            telemetry.grc9v3_event_family_extensions(extension)
            for extension in extensions
        )

        self.assertEqual(len(events), len(extensions))
        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9v3-iter3-events",
            model_family="grc9v3",
            params_identity=model.get_params().params_hash,
            seed_name=DEFAULT_FIXTURE_NAME,
            seed_source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            requested_steps=2,
        )
        event_rows = telemetry.event_rows_from_events(
            events,
            identity=identity,
            family_extensions_by_event=family_extensions,
        )
        self.assertEqual([event.kind for event in events], [row.event_kind for row in event_rows])
        self.assertEqual(
            DEFAULT_FIXTURE_NAME,
            event_rows[0].family_extensions["grc9v3"]["lane_context"]["fixture_name"],
        )

        by_kind = {
            row.event_kind: row.family_extensions["grc9v3"]
            for row in event_rows
        }
        self.assertEqual("spark", by_kind["hybrid_spark_candidate"]["event_domain"])
        self.assertEqual("candidate", by_kind["hybrid_spark_candidate"]["lifecycle_stage"])
        self.assertEqual(0, by_kind["hybrid_spark_candidate"]["primary_node_id"])
        self.assertTrue(
            by_kind["hybrid_spark_candidate"]["spark_evidence"]["saturation_gate"]
        )

        expansion = by_kind["hybrid_mechanical_expansion"]
        self.assertEqual("expansion", expansion["event_domain"])
        self.assertEqual("module_created", expansion["lifecycle_stage"])
        self.assertTrue(expansion["topology_mutation"])
        self.assertTrue(expansion["budget_mutation"])
        self.assertEqual(
            "hybrid-spark-0-0",
            expansion["expansion_id"],
        )
        self.assertEqual(
            (12, 13, 14, 15, 16),
            expansion["expansion_evidence"]["module_node_ids"],
        )
        self.assertEqual(
            "expansion_transfer_unit_measure",
            expansion["expansion_evidence"]["budget_preservation_path"],
        )

        completed = by_kind["hybrid_spark_completed"]
        self.assertEqual("spark", completed["event_domain"])
        self.assertEqual("completed", completed["lifecycle_stage"])
        self.assertTrue(completed["hierarchy_mutation"])
        self.assertEqual(
            (12, 16),
            completed["completion_evidence"]["stabilized_child_node_ids"],
        )

        choice = by_kind["choice_detected"]
        self.assertEqual("choice", choice["event_domain"])
        self.assertEqual("detected", choice["lifecycle_stage"])
        self.assertIn("16", choice["choice_collapse_evidence"]["viable_sink_ids"])

        collapse = by_kind["collapse"]
        self.assertEqual("collapse", collapse["event_domain"])
        self.assertEqual("collapsed", collapse["lifecycle_stage"])
        self.assertEqual("12", collapse["choice_collapse_evidence"]["collapsed_sink_id"])

    def test_lane_b_event_and_step_extensions_expose_column_h_evidence(self) -> None:
        from pygrc.models import GRC9V3

        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        events = tuple(model.apply_hybrid_sparks())

        event_payloads = [
            telemetry.grc9v3_event_family_extensions(
                _build_grc9v3_event_extension(model, event)
            )["grc9v3"]
            for event in events
        ]
        candidate_payload = event_payloads[0]["spark_evidence"]

        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            candidate_payload["spark_lane"],
        )
        self.assertEqual([-1.5, 1.0, -2.5], candidate_payload["column_h"])
        self.assertEqual(1.0, candidate_payload["min_abs_column_h"])
        self.assertEqual(2, candidate_payload["min_abs_column_h_column"])
        self.assertTrue(candidate_payload["column_h_branch_hit"])
        self.assertEqual(["column_h_threshold_hit"], candidate_payload["gate_reasons"])

        step_payload = telemetry.grc9v3_step_family_extensions(
            _build_grc9v3_step_extension(model)
        )["grc9v3"]
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            step_payload["backend_config"]["spark_lane"],
        )
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE_VERSION,
            step_payload["backend_config"]["spark_lane_version"],
        )
        spark_state = step_payload["hybrid_spark_state"]
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            spark_state["last_candidate_spark_lane"],
        )
        self.assertEqual([-1.5, 1.0, -2.5], spark_state["last_candidate_column_h"])
        self.assertTrue(spark_state["last_candidate_column_h_branch_hit"])
        self.assertEqual(
            ["column_h_threshold_hit"],
            spark_state["last_candidate_column_h_gate_reasons"],
        )

    def test_lane_b_checkpoint_node_overlay_exposes_column_h_diagnostics(self) -> None:
        from pygrc.models import GRC9V3

        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                evolution_overrides={"eps_column_h": 1.1},
            ),
        )
        candidate = model.detect_hybrid_spark_candidates()[0]
        model.get_state().event_log.append(candidate)

        overlay = _checkpoint_node_overlay(model)

        self.assertIn("0", overlay)
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            overlay["0"]["spark_lane"],
        )
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_COMPUTATION_VERSION,
            overlay["0"]["column_h_computation_version"],
        )
        self.assertEqual([-1.5, 1.0, -2.5], overlay["0"]["column_h"])
        self.assertEqual(1.0, overlay["0"]["min_abs_column_h"])
        self.assertEqual(2, overlay["0"]["min_abs_column_h_column"])
        self.assertTrue(overlay["0"]["column_h_branch_hit"])
        self.assertEqual(["column_h_threshold_hit"], overlay["0"]["column_h_gate_reasons"])
        self.assertEqual(
            "latest_candidate_event",
            overlay["0"]["column_h_diagnostic_source"],
        )

    def test_lane_b_checkpoint_node_overlay_cache_fallback_has_lane_and_version(self) -> None:
        from pygrc.models import GRC9V3
        from pygrc.models.grc_9_v3_sparks import refresh_column_h_history

        model = GRC9V3.from_state(
            state=_column_h_state(),
            params=_config(
                spark_lane="grc9v3_column_h_assisted",
                enable_column_h_sign_crossing=True,
                store_previous_column_h=True,
            ),
        )
        params = model.get_params()
        refresh_column_h_history(
            model.get_state(),
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )

        overlay = _checkpoint_node_overlay(model)

        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_ASSISTED_SPARK_LANE,
            overlay["0"]["spark_lane"],
        )
        self.assertEqual(
            telemetry.GRC9V3_COLUMN_H_COMPUTATION_VERSION,
            overlay["0"]["column_h_computation_version"],
        )
        self.assertEqual([-1.5, 1.0, -2.5], overlay["0"]["column_h"])
        self.assertEqual(1.0, overlay["0"]["min_abs_column_h"])
        self.assertEqual(2, overlay["0"]["min_abs_column_h_column"])
        self.assertEqual(
            "current_column_h_cache",
            overlay["0"]["column_h_diagnostic_source"],
        )

    def test_event_builder_classifies_choice_resolved_growth_and_unknown_events(
        self,
    ) -> None:
        model = build_representative_hybrid_model()
        synthetic_events = (
            GRCEvent(
                kind="choice_resolved",
                step_index=2,
                source_family="GRC9V3",
                payload={
                    "node_id": 4,
                    "winner_sink_id": "12",
                    "winner_margin": 0.25,
                    "epsilon_choice": 0.001,
                    "epsilon_collapse": 0.001,
                },
            ),
            GRCEvent(
                kind="growth",
                step_index=3,
                source_family="GRC9V3",
                payload={
                    "parent_node_id": 7,
                    "child_node_id": 17,
                    "parent_port_id": 9,
                    "child_port_id": 1,
                    "outward_flux_pressure": 2.0,
                    "birth_probability": 0.5,
                    "rng_sample": 0.25,
                    "coherence_transfer": 0.1,
                },
            ),
            GRCEvent(
                kind="unmapped_event",
                step_index=4,
                source_family="GRC9V3",
                payload={"primary_edge_id": 11},
            ),
        )

        payloads = [
            telemetry.grc9v3_event_family_extensions(
                _build_grc9v3_event_extension(model, event)
            )["grc9v3"]
            for event in synthetic_events
        ]

        self.assertEqual("choice", payloads[0]["event_domain"])
        self.assertEqual("resolved", payloads[0]["lifecycle_stage"])
        self.assertEqual(4, payloads[0]["choice_collapse_evidence"]["node_id"])
        self.assertEqual("growth", payloads[1]["event_domain"])
        self.assertEqual("child_attached", payloads[1]["lifecycle_stage"])
        self.assertTrue(payloads[1]["topology_mutation"])
        self.assertEqual(7, payloads[1]["primary_node_id"])
        self.assertEqual(17, payloads[1]["growth_evidence"]["child_node_id"])
        self.assertEqual("other", payloads[2]["event_domain"])
        self.assertEqual("other", payloads[2]["lifecycle_stage"])
        self.assertEqual(11, payloads[2]["primary_edge_id"])

    def test_event_extensions_empty_sequence_returns_empty_tuple(self) -> None:
        model = build_representative_hybrid_model()

        self.assertEqual((), _build_grc9v3_event_extensions(model, ()))

    def test_run_summary_extension_matches_final_state_and_event_counts(self) -> None:
        model = build_representative_hybrid_model()
        initial_observables = model.compute_observables()
        step_results = tuple(model.step() for _ in range(2))
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            fixture_name=DEFAULT_FIXTURE_NAME,
            run_role="representative",
            experiment_id="phase_t_grc9v3_iter4_run_summary",
        )

        extension = _build_grc9v3_run_summary_extension(
            model,
            step_results,
            lane_context=lane_context,
            replay_digest_match=True,
        )
        family_extensions = telemetry.grc9v3_run_summary_family_extensions(extension)
        payload = family_extensions["grc9v3"]

        self.assertEqual(1, payload["lifecycle_event_counts"]["hybrid_spark_candidate_count"])
        self.assertEqual(
            1,
            payload["lifecycle_event_counts"]["hybrid_mechanical_expansion_count"],
        )
        self.assertEqual(1, payload["lifecycle_event_counts"]["hybrid_spark_completed_count"])
        self.assertEqual(1, payload["lifecycle_event_counts"]["choice_detected_count"])
        self.assertEqual(1, payload["lifecycle_event_counts"]["collapse_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["choice_resolved_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["growth_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["front_capacity_growth_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["pressure_boundary_growth_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["legacy_broad_growth_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["budget_correction_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["coarse_invalidation_count"])
        self.assertEqual(0, payload["lifecycle_event_counts"]["boundary_event_count"])
        self.assertEqual(
            len(tuple(model.get_state().topology.iter_live_node_ids())),
            payload["final_port_chart_summary"]["num_nodes"],
        )
        self.assertEqual(
            len(model.get_state().sink_set),
            payload["final_identity_basin_summary"]["sink_count"],
        )
        self.assertEqual(
            len(model.get_state().hierarchy),
            payload["final_hierarchy_summary"]["hierarchy_root_count"],
        )
        self.assertEqual(
            len(model.get_state().collapse_registry),
            payload["final_choice_collapse_summary"]["collapse_registry_count"],
        )
        self.assertLessEqual(
            abs(payload["final_budget_summary"]["budget_error"]),
            1e-9,
        )

        appendix = payload["representative_appendix_e_summary"]
        self.assertTrue(appendix["spark_completed"])
        self.assertEqual(2, appendix["daughter_sink_count"])
        self.assertEqual([12, 16], appendix["daughter_sink_node_ids"])
        self.assertEqual("root", appendix["hierarchy_parent"])
        self.assertEqual(["12", "16"], appendix["hierarchy_children"])
        self.assertTrue(appendix["budget_preserved"])
        self.assertTrue(appendix["replay_digest_match"])

        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9v3-iter4-run-summary",
            model_family="grc9v3",
            params_identity=model.get_params().params_hash,
            seed_name=DEFAULT_FIXTURE_NAME,
            seed_source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            requested_steps=2,
        )
        summary = telemetry.run_summary_from_step_results(
            step_results,
            identity=identity,
            initial_observables=initial_observables,
            final_observables=model.compute_observables(),
            family_extensions=family_extensions,
        )
        self.assertEqual(
            canonicalize_json_value(payload),
            canonicalize_json_value(summary.family_extensions["grc9v3"]),
        )

    def test_run_summary_without_appendix_fixture_omits_appendix_summary(self) -> None:
        model = build_representative_hybrid_model()
        step_results = tuple(model.step() for _ in range(1))
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            fixture_name="non_appendix_fixture",
            run_role="smoke",
        )

        payload = telemetry.grc9v3_run_summary_family_extensions(
            _build_grc9v3_run_summary_extension(
                model,
                step_results,
                lane_context=lane_context,
            )
        )["grc9v3"]

        self.assertNotIn("representative_appendix_e_summary", payload)

    def test_run_summary_default_replay_digest_match_is_false(self) -> None:
        model = build_representative_hybrid_model()
        step_results = tuple(model.step() for _ in range(1))
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-7-RepresentativeRuntime.md",
            fixture_name=DEFAULT_FIXTURE_NAME,
            run_role="representative",
        )

        payload = telemetry.grc9v3_run_summary_family_extensions(
            _build_grc9v3_run_summary_extension(
                model,
                step_results,
                lane_context=lane_context,
            )
        )["grc9v3"]

        self.assertFalse(
            payload["representative_appendix_e_summary"]["replay_digest_match"]
        )

    def test_run_summary_empty_step_results_have_zero_lifecycle_counts(self) -> None:
        model = build_representative_hybrid_model()
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/Phase-T-GRC9V3-TelemetryContract.md",
            fixture_name="initial_state",
            run_role="empty",
        )

        payload = telemetry.grc9v3_run_summary_family_extensions(
            _build_grc9v3_run_summary_extension(
                model,
                (),
                lane_context=lane_context,
            )
        )["grc9v3"]

        self.assertEqual(
            {
                "hybrid_spark_candidate_count": 0,
                "hybrid_mechanical_expansion_count": 0,
                "hybrid_spark_completed_count": 0,
                "choice_detected_count": 0,
                "choice_resolved_count": 0,
                "collapse_count": 0,
                "growth_count": 0,
                "front_capacity_growth_count": 0,
                "pressure_boundary_growth_count": 0,
                "legacy_broad_growth_count": 0,
                "budget_correction_count": 0,
                "coarse_invalidation_count": 0,
                "boundary_event_count": 0,
            },
            payload["lifecycle_event_counts"],
        )
        self.assertEqual(
            len(tuple(model.get_state().topology.iter_live_node_ids())),
            payload["final_port_chart_summary"]["num_nodes"],
        )
        self.assertNotIn("representative_appendix_e_summary", payload)

    def test_run_summary_counts_pressure_boundary_growth_separately(self) -> None:
        model = build_representative_hybrid_model()
        lane_context = telemetry.GRC9V3LaneContext(
            source_reference="implementation/PressureBoundary-ImplementationPlan.md",
            fixture_name="pressure_boundary_growth_fixture",
            run_role="positive_control",
            experiment_id="phase_t_grc9v3_pressure_boundary_count",
        )
        step_results = (
            StepResult(
                step_index=0,
                time=0.0,
                events=[
                    GRCEvent(
                        kind="growth",
                        step_index=0,
                        source_family="GRC9V3",
                        payload={
                            "growth_parent_eligibility_mode": "grcl9v3_front_capacity",
                            "growth_parent_capacity_source": "pressure_boundary",
                        },
                    ),
                    GRCEvent(
                        kind="growth",
                        step_index=0,
                        source_family="GRC9V3",
                        payload={
                            "growth_parent_eligibility_mode": "grcl9v3_front_capacity",
                            "growth_parent_capacity_source": "spark_expansion_front",
                        },
                    ),
                    GRCEvent(
                        kind="growth",
                        step_index=0,
                        source_family="GRC9V3",
                        payload={
                            "growth_parent_eligibility_mode": "legacy_any_inactive_port",
                        },
                    ),
                ],
                observables={},
            ),
        )

        payload = telemetry.grc9v3_run_summary_family_extensions(
            _build_grc9v3_run_summary_extension(
                model,
                step_results,
                lane_context=lane_context,
            )
        )["grc9v3"]

        lifecycle = payload["lifecycle_event_counts"]
        self.assertEqual(3, lifecycle["growth_count"])
        self.assertEqual(2, lifecycle["front_capacity_growth_count"])
        self.assertEqual(1, lifecycle["pressure_boundary_growth_count"])
        self.assertEqual(1, lifecycle["legacy_broad_growth_count"])


if __name__ == "__main__":
    unittest.main()
