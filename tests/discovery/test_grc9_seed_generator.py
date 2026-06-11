"""Tests for deterministic GRC9 phenomenology seed generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import (
    GRC9_COMPLEX_EVENT_STABILITY_NAMES,
    GRC9_CORRECTED_GROWTH_COMBO_NAMES,
    GRC9_CORRECTED_GROWTH_COMPLEX_NAMES,
    GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES,
    GRC9_LIFECYCLE_COMBO_NAMES,
    GRC9_LIFECYCLE_EMITTER_NAMES,
    GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES,
    GRC9_TARGETED_DIAGNOSTIC_NAMES,
    GRC9GeneratedSeed,
    generate_grc9_complex_event_stability_fixture,
    generate_grc9_corrected_growth_combo_fixture,
    generate_grc9_corrected_growth_complex_fixture,
    generate_grc9_corrected_growth_elementary_fixture,
    default_grc9_hypothesis_catalog,
    generate_grc9_lifecycle_combo,
    generate_grc9_lifecycle_emitter,
    generate_grc9_lifecycle_emitter_perturbation,
    generate_grc9_seed,
    generate_grc9_seed_perturbation,
    generate_grc9_targeted_diagnostic_fixture,
    perturbation_lane_name,
)
from pygrc.discovery.grc9_discovery_runner import (
    _validate_step_count_coverage,
    run_grc9_discovery_control_session,
)
from pygrc.models import GRC9
from pygrc.telemetry._grc9_extensions import (
    _build_grc9_run_summary_extension,
    _capture_grc9_identity_fission_observation,
)
from pygrc.telemetry.grc9_contract import grc9_run_summary_family_extensions


class GRC9SeedGeneratorTest(unittest.TestCase):
    def test_same_seed_parameters_produce_identical_payloads(self) -> None:
        first = generate_grc9_seed("spark_precursor")
        second = generate_grc9_seed("spark_precursor")

        self.assertEqual(first.to_mapping(), second.to_mapping())

    def test_all_scheduled_controls_generate_grc9_ready_state_payloads(self) -> None:
        catalog = default_grc9_hypothesis_catalog()

        generated: list[GRC9GeneratedSeed] = []
        for family in catalog.seed_families:
            if not family.scheduled_for_generation:
                continue
            for control in (*family.positive_controls, *family.negative_controls):
                generated.append(
                    generate_grc9_seed(
                        family.seed_family,
                        control.control_role,
                        catalog=catalog,
                    )
                )

        self.assertGreater(len(generated), 0)
        for seed in generated:
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            state = model.get_state()
            self.assertEqual(
                set(state.topology.iter_live_edge_ids()),
                set(state.port_edges),
            )
            self.assertEqual(
                len(tuple(state.topology.iter_live_node_ids())),
                int(seed.seed_parameters["resolved_node_count"]),
            )

    def test_positive_and_negative_controls_record_documented_parameter_difference(self) -> None:
        positive = generate_grc9_seed("spark_precursor", "positive_control")
        negative = generate_grc9_seed("spark_precursor", "negative_control")

        self.assertEqual(9, positive.seed_parameters["active_degree"])
        self.assertEqual(8, negative.seed_parameters["active_degree"])
        self.assertEqual(positive.lane_name, negative.negative_control_of)
        self.assertLess(
            len(negative.state_payload["topology"]["edges"]),
            len(positive.state_payload["topology"]["edges"]),
        )

    def test_deferred_seed_family_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "not currently testable"):
            generate_grc9_seed("adiabatic_expansion")

    def test_perturbation_generation_is_deterministic_and_references_parent_lane(self) -> None:
        first = generate_grc9_seed_perturbation(
            "expansion_module",
            "target_effective_degree",
            "+7",
        )
        second = generate_grc9_seed_perturbation(
            "expansion_module",
            "target_effective_degree",
            "+7",
        )

        self.assertEqual(first.to_mapping(), second.to_mapping())
        self.assertEqual("expansion_module_positive_control", first.perturbation_of)
        self.assertEqual(37.0, first.seed_parameters["target_effective_degree"])
        self.assertEqual(
            37,
            first.expected_runtime_config["evolution"]["D_eff_target"],
        )

    def test_perturbation_lane_name_matches_convention(self) -> None:
        seed = generate_grc9_seed_perturbation(
            "spark_precursor",
            "spark_threshold",
            "-10%",
        )

        self.assertEqual(
            perturbation_lane_name(
                "spark_precursor",
                "positive_control",
                "spark_threshold",
                "-10%",
            ),
            seed.lane_name,
        )

    def test_perturbation_rejects_unknown_parameter(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown GRC9 seed parameter"):
            generate_grc9_seed_perturbation(
                "spark_precursor",
                "not_a_seed_parameter",
                "+1",
            )

    def test_perturbation_rejects_non_numeric_base_parameter(self) -> None:
        with self.assertRaisesRegex(ValueError, "numeric base parameters"):
            generate_grc9_seed_perturbation(
                "budget_correction",
                "budget_error",
                "-10%",
            )

    def test_discovery_runner_rejects_missing_step_count_for_planned_lane(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing GRC9 discovery step counts"):
            _validate_step_count_coverage(
                {"known_fixture": 3},
                ("known_fixture", "missing_fixture"),
            )

    def test_column_diagnostic_seed_encodes_near_cancellation(self) -> None:
        positive = generate_grc9_seed("column_diagnostic_regime", "positive_control")
        negative = generate_grc9_seed("column_diagnostic_regime", "negative_control")

        positive_model = GRC9.from_state(
            state=dict(positive.state_payload),
            params=dict(positive.expected_runtime_config),
        )
        negative_model = GRC9.from_state(
            state=dict(negative.state_payload),
            params=dict(negative.expected_runtime_config),
        )

        positive_diagnostic = positive_model._compute_column_diagnostic(node_id=0)
        negative_diagnostic = negative_model._compute_column_diagnostic(node_id=0)
        self.assertAlmostEqual(0.0, positive_diagnostic[1])
        self.assertGreater(min(abs(value) for value in negative_diagnostic), 0.0)

    def test_topology_exposes_edge_roles_for_selector_visibility(self) -> None:
        seed = generate_grc9_seed("transport_pathway", "positive_control")
        edge_roles = seed.state_payload["topology"]["edge_roles"]

        self.assertIn("short_path", set(edge_roles.values()))
        self.assertIn("long_path", set(edge_roles.values()))

    def test_quiescent_seed_derives_active_degree_from_catalog_pattern(self) -> None:
        seed = generate_grc9_seed("quiescent_basin", "no_event_control")

        self.assertEqual(
            5,
            len(seed.seed_parameters["active_inactive_port_pattern"]["active_ports"]),
        )
        self.assertEqual(5, len(seed.state_payload["topology"]["edges"]))

    def test_budget_error_magnitude_is_explicit_seed_parameter(self) -> None:
        seed = generate_grc9_seed(
            "budget_correction",
            "positive_control",
            parameter_overrides={"budget_error_magnitude": 0.5},
        )

        budget_current = sum(float(value) for value in seed.state_payload["node_coherence"].values())
        self.assertAlmostEqual(0.5, budget_current - seed.state_payload["budget_target"])

    def test_lifecycle_emitters_generate_grc9_ready_payloads(self) -> None:
        for emitter_name in GRC9_LIFECYCLE_EMITTER_NAMES:
            seed = generate_grc9_lifecycle_emitter(emitter_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            self.assertGreater(
                len(tuple(model.get_state().topology.iter_live_node_ids())),
                0,
            )
            self.assertTrue(_state_payload_graph_is_connected(seed.state_payload))

    def test_lifecycle_emitter_perturbations_generate_grc9_ready_payloads(self) -> None:
        for perturbation_name in GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES:
            seed = generate_grc9_lifecycle_emitter_perturbation(perturbation_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            self.assertEqual("perturbation_control", seed.control_role)
            self.assertIsNotNone(seed.perturbation_of)
            self.assertGreater(
                len(tuple(model.get_state().topology.iter_live_node_ids())),
                0,
            )

    def test_lifecycle_combos_generate_grc9_ready_payloads(self) -> None:
        for combo_name in GRC9_LIFECYCLE_COMBO_NAMES:
            seed = generate_grc9_lifecycle_combo(combo_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            self.assertEqual("combo_control", seed.control_role)
            self.assertGreater(
                len(tuple(model.get_state().topology.iter_live_node_ids())),
                0,
            )
            self.assertTrue(_state_payload_graph_is_connected(seed.state_payload))

    def test_targeted_diagnostic_fixtures_generate_grc9_ready_payloads(self) -> None:
        for fixture_name in GRC9_TARGETED_DIAGNOSTIC_NAMES:
            seed = generate_grc9_targeted_diagnostic_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            self.assertEqual("diagnostic_control", seed.control_role)
            self.assertEqual(fixture_name, seed.lane_name)
            self.assertGreater(
                len(tuple(model.get_state().topology.iter_live_node_ids())),
                0,
            )

    def test_targeted_coarse_fixtures_start_with_warm_contrastive_cache(self) -> None:
        sparse = generate_grc9_targeted_diagnostic_fixture(
            "coarse_cache_populated_sparse_profile_control"
        )
        dense = generate_grc9_targeted_diagnostic_fixture(
            "coarse_cache_populated_dense_profile_control"
        )

        sparse_cache = sparse.state_payload["coarse_cache"]["exact_column_profile:conductance"]
        dense_cache = dense.state_payload["coarse_cache"]["exact_column_profile:conductance"]
        self.assertEqual("conductance", sparse_cache["field_name"])
        self.assertGreater(
            sparse_cache["by_node"]["0"]["column_totals"].count(0.0),
            dense_cache["by_node"]["0"]["column_totals"].count(0.0),
        )

    def test_targeted_budget_fixtures_exercise_distinct_correction_directions(self) -> None:
        uniform = generate_grc9_targeted_diagnostic_fixture(
            "budget_uniform_shift_trigger_control"
        )
        negative = generate_grc9_targeted_diagnostic_fixture(
            "budget_simplex_projection_trigger_control"
        )
        uniform_model = GRC9.from_state(
            state=dict(uniform.state_payload),
            params=dict(uniform.expected_runtime_config),
        )
        negative_model = GRC9.from_state(
            state=dict(negative.state_payload),
            params=dict(negative.expected_runtime_config),
        )

        uniform_model.step()
        negative_model.step()

        self.assertEqual(
            "uniform_shift",
            uniform_model.get_state().cached_quantities["budget_positive_correction_mode"],
        )
        self.assertNotIn(
            "budget_positive_correction_mode",
            negative_model.get_state().cached_quantities,
        )

    def test_targeted_transport_fixtures_separate_short_and_long_path_dominance(self) -> None:
        short = generate_grc9_targeted_diagnostic_fixture(
            "transport_short_path_dominant_control"
        )
        long = generate_grc9_targeted_diagnostic_fixture(
            "transport_long_path_dominant_control"
        )
        observed_top_edges = []
        for seed in (short, long):
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            for _ in range(2):
                model.step()
            top_edge = max(
                model.get_state().port_edges.items(),
                key=lambda item: abs(item[1].flux_uv),
            )[0]
            observed_top_edges.append(top_edge)

        self.assertIn(observed_top_edges[0], {0, 1})
        self.assertIn(observed_top_edges[1], {2, 3, 4, 5})

    def test_complex_event_stability_fixtures_generate_grc9_ready_payloads(self) -> None:
        for fixture_name in GRC9_COMPLEX_EVENT_STABILITY_NAMES:
            seed = generate_grc9_complex_event_stability_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            self.assertEqual("complex_control", seed.control_role)
            self.assertGreater(
                len(tuple(model.get_state().topology.iter_live_node_ids())),
                0,
            )
            self.assertTrue(_state_payload_graph_is_connected(seed.state_payload))

    def test_complex_event_stability_fixtures_emit_all_lifecycle_families(self) -> None:
        for fixture_name in GRC9_COMPLEX_EVENT_STABILITY_NAMES:
            seed = generate_grc9_complex_event_stability_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            event_kinds = []
            step_results = []
            observations = []
            for _ in range(6):
                step_result = model.step()
                step_results.append(step_result)
                observations.append(_capture_grc9_identity_fission_observation(model))
                event_kinds.extend(event.kind for event in step_result.events)

            summary = grc9_run_summary_family_extensions(
                _build_grc9_run_summary_extension(
                    model,
                    step_results,
                    identity_fission_observations=observations,
                )
            )["grc9"]["expansion_summary"]
            self.assertGreaterEqual(event_kinds.count("spark"), 2)
            self.assertGreaterEqual(event_kinds.count("expansion"), 2)
            self.assertIn("growth", event_kinds)
            self.assertGreater(summary["identity_fission_confirmed_count"], 0)

    def test_corrected_growth_elementary_fixtures_generate_grc9_ready_payloads(self) -> None:
        for fixture_name in GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES:
            seed = generate_grc9_corrected_growth_elementary_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            self.assertEqual("growth_correction_control", seed.control_role)
            self.assertEqual(fixture_name, seed.lane_name)
            self.assertEqual(
                "grc9_front_capacity",
                model.get_params().constitutive_semantic_modes[
                    "growth_parent_eligibility"
                ],
            )
            self.assertTrue(_state_payload_graph_is_connected(seed.state_payload))

    def test_corrected_growth_positive_emits_with_front_capacity_provenance(self) -> None:
        for fixture_name, expected_source in (
            (
                "front_capacity_growth_positive_control",
                "spark_refinement_boundary_front",
            ),
            (
                "front_capacity_growth_pressure_boundary_positive_control",
                "pressure_boundary",
            ),
        ):
            with self.subTest(fixture=fixture_name):
                seed = generate_grc9_corrected_growth_elementary_fixture(fixture_name)
                model = GRC9.from_state(
                    state=dict(seed.state_payload),
                    params=dict(seed.expected_runtime_config),
                )

                step_result = model.step()
                growth_events = [
                    event for event in step_result.events if event.kind == "growth"
                ]
                summary = grc9_run_summary_family_extensions(
                    _build_grc9_run_summary_extension(model, [step_result])
                )["grc9"]["growth_summary"]

                self.assertEqual(1, len(growth_events))
                self.assertEqual(0, growth_events[0].payload["parent_node_id"])
                self.assertEqual(3, growth_events[0].payload["parent_port_id"])
                self.assertEqual(
                    "grc9_front_capacity",
                    growth_events[0].payload["growth_parent_eligibility_mode"],
                )
                self.assertEqual(
                    expected_source,
                    growth_events[0].payload["growth_parent_capacity_source"],
                )
                self.assertEqual(
                    1 if expected_source == "pressure_boundary" else 0,
                    summary["pressure_boundary_growth_count"],
                )

    def test_corrected_growth_controls_suppress_non_front_births(self) -> None:
        for fixture_name in (
            "front_capacity_growth_no_front_control",
            "front_capacity_growth_zero_birth_control",
            "front_capacity_growth_pressure_boundary_zero_pressure_control",
            "front_capacity_growth_closed_front_control",
        ):
            seed = generate_grc9_corrected_growth_elementary_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )

            for _ in range(3):
                step_result = model.step()
                self.assertNotIn("growth", [event.kind for event in step_result.events])

    def test_corrected_growth_runner_mode_records_pressure_boundary_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "S0001"
            session = run_grc9_discovery_control_session(
                session_id="S0001",
                session_root=root,
                corrected_growth_elementary=True,
            )

            self.assertEqual(
                "I03_1_elementary_corrected_grc9_growth",
                session.iteration,
            )
            self.assertEqual(
                tuple(GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES),
                tuple(lane.seed.lane_name for lane in session.lanes),
            )
            self.assertEqual(
                2,
                sum(
                    lane.event_counts_by_kind.get("growth", 0)
                    for lane in session.lanes
                ),
            )
            manifest = (root / "session_manifest.json").read_text(encoding="utf-8")
            self.assertIn("--corrected-growth-elementary", manifest)
            pressure_lane = next(
                lane
                for lane in session.lanes
                if lane.seed.lane_name
                == "front_capacity_growth_pressure_boundary_positive_control"
            )
            summary = _read_json(
                Path(pressure_lane.artifact_root) / "telemetry" / "run_summary.json"
            )
            self.assertEqual(
                1,
                summary["family_extensions"]["grc9"]["growth_summary"][
                    "pressure_boundary_growth_count"
                ],
            )

    def test_corrected_growth_combo_fixtures_emit_bounded_front_growth(self) -> None:
        for fixture_name in GRC9_CORRECTED_GROWTH_COMBO_NAMES:
            seed = generate_grc9_corrected_growth_combo_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            event_kinds = []
            growth_events = []
            for _ in range(6):
                step_result = model.step()
                event_kinds.extend(event.kind for event in step_result.events)
                growth_events.extend(
                    event for event in step_result.events if event.kind == "growth"
                )

            self.assertEqual("growth_correction_combo", seed.control_role)
            self.assertEqual(1, len(growth_events), fixture_name)
            self.assertEqual(
                "grc9_front_capacity",
                growth_events[0].payload["growth_parent_eligibility_mode"],
            )
            expected_source = (
                "pressure_boundary"
                if fixture_name == "corrected_spark_pressure_boundary_growth_combo"
                else "spark_refinement_boundary_front"
            )
            self.assertEqual(
                expected_source,
                growth_events[0].payload["growth_parent_capacity_source"],
            )
            if "spark" in fixture_name:
                self.assertIn("spark", event_kinds)
                self.assertIn("expansion", event_kinds)

    def test_corrected_spark_growth_fission_restores_fission_confirmation(self) -> None:
        seed = generate_grc9_corrected_growth_combo_fixture(
            "corrected_spark_growth_fission_combo"
        )
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_results = []
        observations = []
        for _ in range(6):
            step_result = model.step()
            step_results.append(step_result)
            observations.append(_capture_grc9_identity_fission_observation(model))

        summary = grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                identity_fission_observations=observations,
            )
        )["grc9"]["expansion_summary"]
        self.assertGreaterEqual(summary["identity_fission_confirmed_count"], 1)
        self.assertGreaterEqual(summary["identity_fission_max_persistence_steps"], 3)

    def test_corrected_growth_combo_runner_mode_records_pressure_boundary_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "S0001"
            session = run_grc9_discovery_control_session(
                session_id="S0001",
                session_root=root,
                corrected_growth_combo=True,
            )

            self.assertEqual("I03_2_corrected_grc9_growth_combos", session.iteration)
            self.assertEqual(
                tuple(GRC9_CORRECTED_GROWTH_COMBO_NAMES),
                tuple(lane.seed.lane_name for lane in session.lanes),
            )
            self.assertEqual(
                len(GRC9_CORRECTED_GROWTH_COMBO_NAMES),
                sum(
                    lane.event_counts_by_kind.get("growth", 0)
                    for lane in session.lanes
                ),
            )
            manifest = (root / "session_manifest.json").read_text(encoding="utf-8")
            self.assertIn("--corrected-growth-combo", manifest)

    def test_corrected_growth_complex_fixtures_emit_bounded_all_event_evidence(self) -> None:
        for fixture_name in GRC9_CORRECTED_GROWTH_COMPLEX_NAMES:
            seed = generate_grc9_corrected_growth_complex_fixture(fixture_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            event_kinds = []
            growth_events = []
            step_results = []
            observations = []
            for _ in range(6):
                step_result = model.step()
                step_results.append(step_result)
                observations.append(_capture_grc9_identity_fission_observation(model))
                event_kinds.extend(event.kind for event in step_result.events)
                growth_events.extend(
                    event for event in step_result.events if event.kind == "growth"
                )

            summary = grc9_run_summary_family_extensions(
                _build_grc9_run_summary_extension(
                    model,
                    step_results,
                    identity_fission_observations=observations,
                )
            )["grc9"]
            self.assertEqual("growth_correction_complex", seed.control_role)
            self.assertEqual(1, len(growth_events), fixture_name)
            self.assertEqual(
                "grc9_front_capacity",
                growth_events[0].payload["growth_parent_eligibility_mode"],
            )
            self.assertEqual(
                "spark_refinement_boundary_front",
                growth_events[0].payload["growth_parent_capacity_source"],
            )
            self.assertGreaterEqual(event_kinds.count("spark"), 2, fixture_name)
            self.assertGreaterEqual(event_kinds.count("expansion"), 2, fixture_name)
            self.assertGreaterEqual(
                summary["expansion_summary"]["identity_fission_confirmed_count"],
                1,
                fixture_name,
            )
            self.assertEqual(
                0,
                summary["growth_summary"]["legacy_broad_growth_count"],
                fixture_name,
            )

    def test_corrected_growth_complex_runner_mode_records_five_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "S0001"
            session = run_grc9_discovery_control_session(
                session_id="S0001",
                session_root=root,
                corrected_growth_complex=True,
            )

            self.assertEqual("I03_3_corrected_grc9_full_complex", session.iteration)
            self.assertEqual(
                tuple(GRC9_CORRECTED_GROWTH_COMPLEX_NAMES),
                tuple(lane.seed.lane_name for lane in session.lanes),
            )
            self.assertEqual(
                len(GRC9_CORRECTED_GROWTH_COMPLEX_NAMES),
                sum(
                    lane.event_counts_by_kind.get("growth", 0)
                    for lane in session.lanes
                ),
            )
            manifest = (root / "session_manifest.json").read_text(encoding="utf-8")
            self.assertIn("--corrected-growth-complex", manifest)

    def test_repaired_spark_emitters_emit_spark_and_expansion(self) -> None:
        for emitter_name in (
            "spark_column_proxy_emitter",
            "spark_instability_emitter",
            "spark_to_expansion_emitter",
        ):
            seed = generate_grc9_lifecycle_emitter(emitter_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            step_result = model.step()
            event_kinds = [event.kind for event in step_result.events]
            self.assertIn("spark", event_kinds)
            self.assertIn("expansion", event_kinds)

    def test_repaired_growth_emitter_births_from_intended_parent(self) -> None:
        seed = generate_grc9_lifecycle_emitter("growth_pressure_emitter")
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_result = model.step()

        growth_events = [event for event in step_result.events if event.kind == "growth"]
        self.assertEqual(1, len(growth_events))
        self.assertEqual(0, growth_events[0].payload["parent_node_id"])
        self.assertEqual(3, growth_events[0].payload["parent_port_id"])

    def test_repaired_fission_emitter_confirms_without_growth(self) -> None:
        seed = generate_grc9_lifecycle_emitter("post_expansion_fission_emitter")
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_results = []
        observations = []
        for _ in range(6):
            step_result = model.step()
            step_results.append(step_result)
            observations.append(_capture_grc9_identity_fission_observation(model))
            self.assertNotIn("growth", [event.kind for event in step_result.events])

        summary = grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                identity_fission_observations=observations,
            )
        )["grc9"]["expansion_summary"]
        self.assertEqual(1, summary["identity_fission_confirmed_count"])
        self.assertGreaterEqual(summary["identity_fission_max_persistence_steps"], 3)

    def test_column_proxy_threshold_perturbation_suppresses_spark(self) -> None:
        seed = generate_grc9_lifecycle_emitter_perturbation(
            "spark_column_proxy_eps_fail"
        )
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_result = model.step()

        self.assertNotIn("spark", [event.kind for event in step_result.events])

    def test_instability_threshold_perturbation_suppresses_spark(self) -> None:
        seed = generate_grc9_lifecycle_emitter_perturbation(
            "spark_instability_tau_fail"
        )
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_result = model.step()

        self.assertNotIn("spark", [event.kind for event in step_result.events])

    def test_growth_lambda_perturbation_suppresses_birth(self) -> None:
        seed = generate_grc9_lifecycle_emitter_perturbation(
            "growth_pressure_lambda_low"
        )
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )

        for _ in range(5):
            step_result = model.step()
            self.assertNotIn("growth", [event.kind for event in step_result.events])

    def test_expansion_effective_degree_perturbation_changes_module_size(self) -> None:
        low = generate_grc9_lifecycle_emitter_perturbation(
            "spark_to_expansion_d_eff_low"
        )
        high = generate_grc9_lifecycle_emitter_perturbation(
            "spark_to_expansion_d_eff_high"
        )
        low_model = GRC9.from_state(
            state=dict(low.state_payload),
            params=dict(low.expected_runtime_config),
        )
        high_model = GRC9.from_state(
            state=dict(high.state_payload),
            params=dict(high.expected_runtime_config),
        )

        low_expansion = [
            event for event in low_model.step().events if event.kind == "expansion"
        ][0]
        high_expansion = [
            event for event in high_model.step().events if event.kind == "expansion"
        ][0]
        self.assertLess(
            len(low_expansion.payload["module_node_ids"]),
            len(high_expansion.payload["module_node_ids"]),
        )

    def test_fission_min_mass_perturbation_suppresses_confirmation(self) -> None:
        seed = generate_grc9_lifecycle_emitter_perturbation(
            "post_expansion_fission_min_mass_fail"
        )
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_results = []
        observations = []
        for _ in range(6):
            step_result = model.step()
            step_results.append(step_result)
            observations.append(_capture_grc9_identity_fission_observation(model))

        summary = grc9_run_summary_family_extensions(
            _build_grc9_run_summary_extension(
                model,
                step_results,
                identity_fission_observations=observations,
            )
        )["grc9"]["expansion_summary"]
        self.assertEqual(0, summary["identity_fission_confirmed_count"])

    def test_spark_growth_combo_emits_both_event_families(self) -> None:
        seed = generate_grc9_lifecycle_combo("spark_growth_combo")
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_result = model.step()
        event_kinds = [event.kind for event in step_result.events]

        self.assertIn("spark", event_kinds)
        self.assertIn("expansion", event_kinds)
        self.assertIn("growth", event_kinds)

    def test_dual_spark_combo_emits_two_expansions(self) -> None:
        seed = generate_grc9_lifecycle_combo("dual_spark_combo")
        model = GRC9.from_state(
            state=dict(seed.state_payload),
            params=dict(seed.expected_runtime_config),
        )
        step_result = model.step()

        self.assertEqual(2, sum(1 for event in step_result.events if event.kind == "spark"))
        self.assertEqual(
            2,
            sum(1 for event in step_result.events if event.kind == "expansion"),
        )

    def test_combo_fission_examples_confirm_persistence(self) -> None:
        for combo_name in (
            "spark_fission_combo",
            "growth_fission_combo",
            "spark_growth_fission_combo",
        ):
            seed = generate_grc9_lifecycle_combo(combo_name)
            model = GRC9.from_state(
                state=dict(seed.state_payload),
                params=dict(seed.expected_runtime_config),
            )
            step_results = []
            observations = []
            for _ in range(6):
                step_result = model.step()
                step_results.append(step_result)
                observations.append(_capture_grc9_identity_fission_observation(model))

            summary = grc9_run_summary_family_extensions(
                _build_grc9_run_summary_extension(
                    model,
                    step_results,
                    identity_fission_observations=observations,
                )
            )["grc9"]["expansion_summary"]
            self.assertGreaterEqual(summary["identity_fission_confirmed_count"], 1)

def _state_payload_graph_is_connected(state_payload: dict[str, object]) -> bool:
    topology = state_payload["topology"]
    assert isinstance(topology, dict)
    nodes = topology["nodes"]
    edges = topology["edges"]
    assert isinstance(nodes, list)
    assert isinstance(edges, list)
    node_ids = {
        int(node["node_id"])
        for node in nodes
        if isinstance(node, dict) and "node_id" in node
    }
    if not node_ids:
        return True
    adjacency = {node_id: set() for node_id in node_ids}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        endpoint_a = edge["endpoint_a"]
        endpoint_b = edge["endpoint_b"]
        assert isinstance(endpoint_a, dict)
        assert isinstance(endpoint_b, dict)
        node_a = int(endpoint_a["node_id"])
        node_b = int(endpoint_b["node_id"])
        adjacency[node_a].add(node_b)
        adjacency[node_b].add(node_a)
    start = next(iter(node_ids))
    seen = {start}
    stack = [start]
    while stack:
        node_id = stack.pop()
        for neighbor in adjacency[node_id]:
            if neighbor in seen:
                continue
            seen.add(neighbor)
            stack.append(neighbor)
    return seen == node_ids


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
