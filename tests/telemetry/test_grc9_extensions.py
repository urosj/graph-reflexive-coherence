"""Builder tests for GRC9 telemetry extension payloads."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.core import GRCEvent, StepResult, canonicalize_json_value, digest_snapshot
from pygrc.telemetry._grc9_extensions import (
    _build_grc9_event_extension,
    _build_grc9_run_summary_extension,
    _build_grc9_step_extension,
    _capture_grc9_identity_fission_observation,
    _evaluate_grc9_identity_fission_persistence,
)
from pygrc.telemetry.experiments import _build_grc9_representative_model


class GRC9TelemetryExtensionBuilderTest(unittest.TestCase):
    """Validate private Phase T-GRC9 telemetry builders."""

    def test_step_extension_from_representative_state_is_deterministic_and_json_safe(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        step_result = model.step()
        model.coarse_grain_columns("conductance")
        model.coarse_grain_columns("signed_flux")
        before_digest = digest_snapshot(model.snapshot())
        lane_context = telemetry.GRC9LaneContext(
            source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
            lane_name="phase_t_grc9_iter3_builder",
            role="primary",
        )

        extension_a = _build_grc9_step_extension(model, lane_context=lane_context)
        extension_b = _build_grc9_step_extension(model, lane_context=lane_context)
        self.assertEqual(extension_a.to_mapping(), extension_b.to_mapping())
        self.assertEqual(before_digest, digest_snapshot(model.snapshot()))

        family_extensions = telemetry.grc9_step_family_extensions(extension_a)
        payload = family_extensions["grc9"]
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        self.assertEqual(
            "equal",
            payload["backend_config"]["expansion_distribution_mode"],
        )
        self.assertEqual(
            "legacy_any_inactive_port",
            payload["backend_config"]["growth_parent_eligibility_mode"],
        )
        self.assertIn(
            payload["transport"]["label_availability"]["overall"],
            ("all", "partial", "none"),
        )
        self.assertIn("conductance", payload["coarse_graining"]["coarse_fields_list"])
        self.assertIn("signed_flux", payload["coarse_graining"]["coarse_fields_list"])
        self.assertGreater(payload["port_chart"]["num_nodes"], 0)
        self.assertGreaterEqual(
            payload["column_diagnostic"]["spark_calibration"]["spark_threshold"],
            0.0,
        )
        self.assertEqual(
            "topology_updated_current_flux_diagnostic",
            payload["identity_abundance"]["abundance_contract"],
        )

        identity = telemetry.RunTelemetryIdentity(
            run_id="grc9-iter3-builder",
            model_family="grc9",
            params_identity=model.get_params().params_hash,
            seed_name="representative",
            seed_source_reference="implementation/Phase-T-GRC9-TelemetryContract.md",
            seed_path="synthetic/grc9/iter3",
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
            canonicalize_json_value(loaded_row.family_extensions["grc9"]),
        )

    def test_step_extension_with_missing_optional_caches_uses_explicit_empty_payloads(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        before_digest = digest_snapshot(model.snapshot())

        extension = _build_grc9_step_extension(model)
        payload = telemetry.grc9_step_family_extensions(extension)["grc9"]

        self.assertEqual(before_digest, digest_snapshot(model.snapshot()))
        self.assertEqual(0.0, payload["row_tensor"]["row_tensor_mean"])
        self.assertEqual(
            {},
            payload["row_tensor"]["row_tensor_by_node_sample"],
        )
        self.assertEqual(
            {},
            payload["column_diagnostic"]["column_diagnostic_by_candidate"],
        )
        self.assertEqual("none", payload["transport"]["label_availability"]["overall"])
        self.assertEqual([], payload["coarse_graining"]["coarse_fields_list"])
        self.assertEqual("empty", payload["coarse_graining"]["coarse_cache_state"])
        self.assertEqual("none", payload["budget_correction"]["last_budget_correction_path"])

    def test_identity_summary_counts_successor_ties_and_scale_weighted_abundance(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        state = model.get_state()
        state.basins = {0: {0, 1}, 10: {10}}
        state.sink_set = {0, 10}
        state.port_edges[0] = replace(state.port_edges[0], flux_uv=-0.5)
        state.port_edges[9] = replace(state.port_edges[9], flux_uv=0.5)

        payload = telemetry.grc9_step_family_extensions(
            _build_grc9_step_extension(model)
        )["grc9"]
        identity = payload["identity_abundance"]

        self.assertEqual(1, identity["successor_tie_count"])
        self.assertEqual(
            "max_positive_flux_then_neighbor_id_then_edge_id",
            identity["successor_tie_break_policy"],
        )
        self.assertEqual(1.0, identity["scale_weighted_abundance_gamma"])
        self.assertEqual(3.0, identity["scale_weighted_abundance"])

    def test_event_builder_enriches_runtime_expansion_and_growth_events(self) -> None:
        model = _build_grc9_representative_model()
        events_by_kind = {}
        for _ in range(4):
            for event in model.step().events:
                events_by_kind.setdefault(event.kind, event)

        expansion = _build_grc9_event_extension(model, events_by_kind["expansion"])
        expansion_payload = telemetry.grc9_event_family_extensions(expansion)["grc9"]
        expansion_evidence = expansion_payload["expansion_evidence"]

        self.assertEqual("expansion", expansion_payload["event_domain"])
        self.assertEqual(
            "equal",
            expansion_evidence["coherence_transfer_mode"],
        )
        self.assertEqual(
            {"1": 3, "2": 3, "3": 3},
            expansion_evidence["reassigned_edge_count_by_column"],
        )
        self.assertEqual("column_geometric_mean", expansion_evidence["bond_weight_mode"])
        self.assertIn("mean", expansion_evidence["internal_conductance_stats"])
        self.assertEqual("instantaneous", expansion_evidence["expansion_schedule"])
        self.assertEqual(1, expansion_evidence["expansion_substeps"])

        growth = _build_grc9_event_extension(model, events_by_kind["growth"])
        growth_payload = telemetry.grc9_event_family_extensions(growth)["grc9"]
        growth_evidence = growth_payload["growth_evidence"]

        self.assertEqual("growth", growth_payload["event_domain"])
        self.assertGreaterEqual(growth_evidence["selected_parent_port"], 1)
        self.assertEqual("bernoulli_probability", growth_evidence["birth_rule"])
        self.assertEqual(
            "legacy_any_inactive_port",
            growth_evidence["parent_eligibility_mode"],
        )
        self.assertEqual(
            "legacy_any_inactive_port",
            growth_evidence["parent_capacity_source"],
        )
        self.assertFalse(growth_evidence["front_growth_provenance_present"])
        self.assertTrue(growth_evidence["legacy_broad_growth"])
        self.assertGreaterEqual(growth_evidence["birth_probability"], 0.0)
        self.assertGreater(growth_evidence["outward_flux_pressure"], 0.0)

    def test_event_builder_enriches_spark_prediction_fields(self) -> None:
        model = _build_grc9_representative_model()
        event = GRCEvent(
            kind="spark",
            step_index=0,
            payload={
                "sink_node_id": 0,
                "spark_kind": "saturation_column_proxy",
                "active_degree": 9,
                "instability": 0.0,
                "min_abs_column": 0.0,
            },
            source_family="GRC9",
        )

        payload = telemetry.grc9_event_family_extensions(
            _build_grc9_event_extension(model, event)
        )["grc9"]
        spark_evidence = payload["spark_evidence"]

        self.assertEqual("spark", payload["event_domain"])
        self.assertTrue(spark_evidence["saturation_gate_pass"])
        self.assertTrue(spark_evidence["column_proxy_gate_pass"])
        self.assertFalse(spark_evidence["instability_gate_pass"])
        self.assertEqual(30, spark_evidence["predicted_D_eff"])
        self.assertEqual(4, spark_evidence["predicted_module_size"])
        self.assertEqual(3, spark_evidence["predicted_satellite_count"])

    def test_public_spark_classifier_distinguishes_trigger_kinds(self) -> None:
        cases = (
            ("saturation_instability", "instability_gate_pass"),
            ("saturation_column_proxy", "column_proxy_gate_pass"),
            ("saturation_sign_crossing", "sign_crossing_gate_pass"),
        )
        for spark_kind, expected_gate in cases:
            with self.subTest(spark_kind=spark_kind):
                extension = telemetry.classify_grc9_event_extension(
                    "spark",
                    {
                        "sink_node_id": 1,
                        "spark_kind": spark_kind,
                        "active_degree": 9,
                        "instability": 0.75,
                        "tau_instability": 0.5,
                        "min_abs_column": 0.001,
                        "eps_spark": 0.01,
                        "sign_crossing": spark_kind == "saturation_sign_crossing",
                        "target_effective_degree": 30,
                    },
                )
                evidence = extension.to_mapping()["spark_evidence"]
                self.assertTrue(evidence[expected_gate])
                self.assertEqual(4, evidence["predicted_module_size"])

    def test_run_summary_builder_covers_lifecycle_expansion_and_growth_totals(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        step_results = [model.step() for _ in range(4)]
        before_digest = digest_snapshot(model.snapshot())

        extension = _build_grc9_run_summary_extension(model, step_results)
        payload = telemetry.grc9_run_summary_family_extensions(extension)["grc9"]

        self.assertEqual(before_digest, digest_snapshot(model.snapshot()))
        self.assertEqual(
            telemetry.GRC9_TELEMETRY_CONTRACT_VERSION,
            payload["contract_version"],
        )
        lifecycle = payload["lifecycle_event_counts"]
        self.assertEqual(1, lifecycle["spark_confirmed_count"])
        self.assertEqual(1, lifecycle["spark_candidate_count"])
        self.assertEqual(1, lifecycle["spark_column_proxy_count"])
        self.assertEqual(1, lifecycle["expansion_count"])
        self.assertGreater(lifecycle["growth_count"], 0)

        expansion = payload["expansion_summary"]
        self.assertEqual(1, expansion["final_expansion_registry_size"])
        self.assertEqual(9, expansion["total_boundary_reassignments"])
        self.assertGreaterEqual(expansion["max_module_node_count"], 4)
        self.assertEqual(0, expansion["identity_fission_confirmed_count"])
        self.assertEqual(0, expansion["identity_fission_max_persistence_steps"])

        growth = payload["growth_summary"]
        self.assertEqual(lifecycle["growth_count"], growth["growth_count"])
        self.assertGreater(growth["unique_growth_parent_count"], 0)
        self.assertGreater(growth["lowest_port_attachment_count"], 0)
        self.assertEqual(0, growth["front_capacity_growth_count"])
        self.assertEqual(0, growth["pressure_boundary_growth_count"])
        self.assertEqual(lifecycle["growth_count"], growth["legacy_broad_growth_count"])
        self.assertIn("birth_probability_mean", growth)

        calibration = payload["calibration_summary"]
        self.assertEqual("absolute", calibration["spark_threshold_mode"])
        self.assertEqual(0.25, calibration["spark_rate_observed"])

    def test_identity_fission_evaluator_keeps_candidate_only_unconfirmed(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        step_results = [model.step()]
        self._force_identity_fission_candidate(model, basin_mass=0.5)
        observations = (
            _capture_grc9_identity_fission_observation(model),
        )

        evaluation = _evaluate_grc9_identity_fission_persistence(
            observations,
            delta=2,
            min_basin_mass=0.1,
        )
        payload = telemetry.grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                identity_fission_observations=observations,
                identity_fission_persistence_delta=2,
                identity_fission_min_basin_mass=0.1,
            )
        )["grc9"]

        self.assertEqual(0, evaluation["identity_fission_confirmed_count"])
        self.assertEqual(1, evaluation["identity_fission_max_persistence_steps"])
        expansion = payload["expansion_summary"]
        self.assertEqual(1, expansion["identity_fission_candidate_count"])
        self.assertEqual(0, expansion["identity_fission_confirmed_count"])
        self.assertEqual(1, expansion["identity_fission_max_persistence_steps"])
        self.assertEqual(
            "artifact_backed",
            payload["diagnostic_status_summary"]["identity_fission_confirmed"],
        )

    def test_identity_fission_evaluator_confirms_persistent_two_sink_window(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        step_results = [model.step()]
        self._force_identity_fission_candidate(model, basin_mass=0.5)
        first_observation = _capture_grc9_identity_fission_observation(model)
        second_observation = dict(first_observation)
        second_observation["step_index"] = int(first_observation["step_index"]) + 1
        observations = (first_observation, second_observation)

        evaluation = _evaluate_grc9_identity_fission_persistence(
            observations,
            delta=2,
            min_basin_mass=0.1,
        )
        payload = telemetry.grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                identity_fission_observations=observations,
                identity_fission_persistence_delta=2,
                identity_fission_min_basin_mass=0.1,
            )
        )["grc9"]

        self.assertEqual(1, evaluation["identity_fission_confirmed_count"])
        self.assertEqual(2, evaluation["identity_fission_max_persistence_steps"])
        expansion = payload["expansion_summary"]
        self.assertEqual(1, expansion["identity_fission_candidate_count"])
        self.assertEqual(1, expansion["identity_fission_confirmed_count"])
        self.assertEqual(2, expansion["identity_fission_max_persistence_steps"])

    def test_identity_fission_evaluator_enforces_minimum_basin_mass(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        model.step()
        self._force_identity_fission_candidate(model, basin_mass=0.25)
        first_observation = _capture_grc9_identity_fission_observation(model)
        second_observation = dict(first_observation)
        second_observation["step_index"] = int(first_observation["step_index"]) + 1
        observations = (first_observation, second_observation)

        evaluation = _evaluate_grc9_identity_fission_persistence(
            observations,
            delta=2,
            min_basin_mass=0.5,
        )

        self.assertEqual(0, evaluation["identity_fission_confirmed_count"])
        self.assertEqual(0, evaluation["identity_fission_max_persistence_steps"])

    def test_identity_fission_evaluator_requires_same_sink_pair_to_persist(
        self,
    ) -> None:
        model = _build_grc9_representative_model()
        model.step()
        state = model.get_state()
        expansion_record = next(iter(state.expansion_registry.values()))
        sink_a, sink_b, sink_c = tuple(expansion_record.module_node_ids[:3])
        state.sink_set = {sink_a, sink_b}
        state.basins = {sink_a: {sink_a}, sink_b: {sink_b}}
        state.node_coherence[sink_a] = 0.5
        state.node_coherence[sink_b] = 0.5
        state.node_coherence[sink_c] = 0.5
        first_observation = _capture_grc9_identity_fission_observation(model)

        state.sink_set = {sink_b, sink_c}
        state.basins = {sink_b: {sink_b}, sink_c: {sink_c}}
        second_observation = dict(_capture_grc9_identity_fission_observation(model))
        second_observation["step_index"] = int(first_observation["step_index"]) + 1

        evaluation = _evaluate_grc9_identity_fission_persistence(
            (first_observation, second_observation),
            delta=2,
            min_basin_mass=0.1,
        )

        self.assertEqual(0, evaluation["identity_fission_confirmed_count"])
        self.assertEqual(1, evaluation["identity_fission_max_persistence_steps"])

    def test_run_summary_builder_splits_budget_counts_and_fission_fields(self) -> None:
        model = _build_grc9_representative_model()
        model.step()
        state = model.get_state()
        expansion_record = next(iter(state.expansion_registry.values()))
        state.sink_set = set(expansion_record.module_node_ids[:2])
        state.cached_quantities["identity_fission_confirmed_count"] = 1
        state.cached_quantities["identity_fission_max_persistence_steps"] = 3
        budget_events = [
            GRCEvent(
                kind="budget_correction",
                step_index=1,
                payload={
                    "correction_path": "uniform_shift",
                    "budget_error_before": 0.2,
                    "budget_error_after": 0.0,
                },
                source_family="GRC9",
            ),
            GRCEvent(
                kind="budget_correction",
                step_index=2,
                payload={
                    "correction_path": "simplex_projection",
                    "simplex_projection_applied": True,
                    "budget_error_before": -0.1,
                    "budget_error_after": 0.0,
                },
                source_family="GRC9",
            ),
        ]
        step_results = (
            StepResult(
                step_index=1,
                time=0.1,
                events=budget_events,
                observables={},
            ),
        )

        payload = telemetry.grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(model, step_results)
        )["grc9"]

        lifecycle = payload["lifecycle_event_counts"]
        self.assertEqual(2, lifecycle["budget_correction_count"])
        self.assertEqual(1, lifecycle["budget_uniform_correction_count"])
        self.assertEqual(1, lifecycle["budget_simplex_correction_count"])

        expansion = payload["expansion_summary"]
        self.assertEqual(1, expansion["identity_fission_candidate_count"])
        self.assertEqual(1, expansion["identity_fission_confirmed_count"])
        self.assertEqual(3, expansion["identity_fission_max_persistence_steps"])
        self.assertEqual(
            "artifact_backed",
            payload["diagnostic_status_summary"]["identity_fission_confirmed"],
        )

    def _force_identity_fission_candidate(
        self,
        model: object,
        *,
        basin_mass: float,
    ) -> None:
        state = model.get_state()
        expansion_record = next(iter(state.expansion_registry.values()))
        candidate_sinks = tuple(expansion_record.module_node_ids[:2])
        state.sink_set = set(candidate_sinks)
        state.basins = {
            candidate_sinks[0]: {candidate_sinks[0]},
            candidate_sinks[1]: {candidate_sinks[1]},
        }
        state.node_coherence[candidate_sinks[0]] = basin_mass
        state.node_coherence[candidate_sinks[1]] = basin_mass


if __name__ == "__main__":
    unittest.main()
