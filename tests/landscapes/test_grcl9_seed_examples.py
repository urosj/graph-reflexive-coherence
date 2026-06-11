"""Tests for seed-backed GRCL-9 landscape examples."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import load_landscape_seed
from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS,
    compile_default_grcl9_landscape_seed_examples_to_sources,
    default_grcl9_landscape_seed_examples,
    extract_grcl9_landscape_example_from_seed,
    grcl9_landscape_seed_example_path_by_name,
    legacy_grcl9_growth_landscape_seed_example_path_by_name,
    legacy_grcl9_growth_landscape_seed_examples,
)
from pygrc.models import lower_grcl9_source_to_grc9_state
from pygrc.telemetry import run_grcl9_lowering_replay_session


ROOT = Path(__file__).resolve().parents[2]


class GRCL9SeedExamplesTest(unittest.TestCase):
    def test_seed_example_paths_are_complete_and_ordered(self) -> None:
        self.assertEqual(51, len(GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS))
        examples = default_grcl9_landscape_seed_examples(root=ROOT)

        self.assertEqual(
            GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        for path in GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS:
            self.assertTrue((ROOT / path).exists(), path)

    def test_legacy_growth_seed_examples_load_through_diagnostic_path(self) -> None:
        examples = legacy_grcl9_growth_landscape_seed_examples(root=ROOT)
        paths = legacy_grcl9_growth_landscape_seed_example_path_by_name(root=ROOT)

        self.assertEqual(
            GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        self.assertEqual(
            set(GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES),
            set(paths),
        )
        self.assertTrue(
            all("legacy/grcl9-overaggressive-growth" in str(path) for path in paths.values())
        )
        default_paths = grcl9_landscape_seed_example_path_by_name(root=ROOT)
        self.assertFalse(
            set(GRCL9_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES) & set(default_paths)
        )

    def test_composing_cells_seed_examples_use_cell_primitives(self) -> None:
        path_by_name = grcl9_landscape_seed_example_path_by_name(root=ROOT)
        expected_names = {
            "cell_boundary_ridge_membrane_spark_pass",
            "cell_basin_merge_before_persistence_probe",
            "cell_developed_basin_centroid_collapse_long_window",
            "cell_basin_merge_runtime_collapse_probe",
            "cell_basin_merge_runtime_stability_control",
            "cell_membrane_rupture_structural_probe",
            "cell_plateau_nested_basins_fission_pass",
            "cell_saddle_branch_instability_pass",
            "cell_saddle_choice_pressure_structural_probe",
            "cell_refinement_budget_partition_expansion_high",
        }

        self.assertTrue(expected_names.issubset(path_by_name))
        for name in expected_names:
            with self.subTest(seed=name):
                seed = load_landscape_seed(path_by_name[name])
                primitive_types = {primitive.type for primitive in seed.primitives}

                self.assertTrue({"basin", "plateau", "ridge", "valley", "saddle"} & primitive_types)
                self.assertTrue(seed.extensions["grcl9"]["grcl9_required"])
                self.assertTrue(seed.extensions["grcl9"]["expected_selector_ids"])

    def test_seed_extensions_extract_to_landscape_examples(self) -> None:
        path_by_name = grcl9_landscape_seed_example_path_by_name(root=ROOT)

        for name in GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES:
            with self.subTest(seed=name):
                path = path_by_name[name]
                seed = load_landscape_seed(path)
                example = extract_grcl9_landscape_example_from_seed(
                    seed,
                    seed_path=path,
                )

                self.assertIsNotNone(example)
                assert example is not None
                self.assertEqual(name, example.example_name)
                self.assertEqual(str(path), example.source_seed_reference)
                self.assertTrue(example.grcl9_required)
                self.assertTrue(example.terms)

    def test_seed_compiled_sources_validate_and_lower_to_connected_grc9_states(self) -> None:
        sources = compile_default_grcl9_landscape_seed_examples_to_sources(root=ROOT)

        self.assertEqual(
            GRCL9_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(source.fixture_name for source in sources),
        )
        for source in sources:
            with self.subTest(source=source.fixture_name):
                result = lower_grcl9_source_to_grc9_state(source)
                self.assertGreaterEqual(len(result.state.node_coherence), 1)
                provenance = source.compiled_source_provenance or {}
            self.assertTrue(str(provenance["source_seed_reference"]).endswith(".seed.yaml"))

    def test_corrected_front_growth_seed_sources_use_front_capacity_semantics(self) -> None:
        sources = {
            source.fixture_name: source
            for source in compile_default_grcl9_landscape_seed_examples_to_sources(root=ROOT)
        }

        for name, expected_lambda in (
            ("corrected_front_growth_positive_high", 100.0),
            ("corrected_pressure_boundary_positive_high", 100.0),
            ("corrected_front_growth_no_growth_low", 0.0),
            ("corrected_front_growth_no_front_fail", 100.0),
            ("corrected_front_growth_closed_front_fail", 100.0),
        ):
            with self.subTest(source=name):
                source = sources[name]
                growth = next(
                    construct
                    for construct in source.constructs
                    if construct.construct_kind == "growth_locus"
                )
                self.assertEqual("front_capacity", growth.growth_semantics)
                if name == "corrected_front_growth_no_front_fail":
                    self.assertEqual("preexisting_front", growth.front_capacity_source)
                    self.assertIsNone(growth.front_source_construct_id)
                elif name == "corrected_pressure_boundary_positive_high":
                    self.assertEqual("pressure_boundary", growth.front_capacity_source)
                    self.assertIsNone(growth.front_source_construct_id)
                    self.assertIn(
                        "pressure_boundary_growth_provenance",
                        source.expected_selector_ids,
                    )
                else:
                    self.assertEqual("spark_expansion_front", growth.front_capacity_source)
                    self.assertEqual(
                        f"{name}_expansion_region",
                        growth.front_source_construct_id,
                )
                self.assertEqual(expected_lambda, growth.lambda_birth)

    def test_corrected_composite_seed_sources_use_front_capacity_semantics(self) -> None:
        sources = {
            source.fixture_name: source
            for source in compile_default_grcl9_landscape_seed_examples_to_sources(root=ROOT)
        }
        corrected_composites = tuple(
            source
            for name, source in sources.items()
            if name.startswith("corrected_cell_")
        )

        self.assertEqual(28, len(corrected_composites))
        for source in corrected_composites:
            growth_constructs = tuple(
                construct
                for construct in source.constructs
                if construct.construct_kind == "growth_locus"
            )
            for growth in growth_constructs:
                with self.subTest(source=source.fixture_name, construct=growth.construct_id):
                    self.assertEqual("front_capacity", growth.growth_semantics)
                    self.assertNotEqual(
                        "legacy_source_growth_locus",
                        growth.front_capacity_source,
                    )

    def test_seed_extraction_requires_lowering_guard(self) -> None:
        seed = load_landscape_seed(ROOT / GRCL9_LANDSCAPE_SEED_EXAMPLE_PATHS[0])
        seed.extensions["grcl9"]["grcl9_required"] = False

        with self.assertRaisesRegex(InvalidLandscapeSeedError, "grcl9_required"):
            extract_grcl9_landscape_example_from_seed(seed)

    def test_replay_can_store_seed_examples_authored_examples_and_compiled_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9202",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=("spark_column_proxy_eps_fail",),
                requested_steps=1,
                source_mode="landscape_seed_examples",
            )

            manifest = _read_json(result.session_manifest_path)
            self.assertEqual("landscape_seed_examples", manifest["source_mode"])
            self.assertTrue(
                (
                    result.session_root
                    / "grcl_landscape_seeds"
                    / "grcl9-spark-column-proxy-eps-fail.seed.yaml"
                ).exists()
            )
            self.assertTrue(
                (
                    result.session_root
                    / "grcl_landscape_examples"
                    / "spark_column_proxy_eps_fail.json"
                ).exists()
            )
            self.assertEqual("passed", result.lanes[0].selector_status)

    def test_corrected_front_growth_seed_replay_uses_front_capacity_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9204",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=(
                    "corrected_front_growth_positive_high",
                    "corrected_pressure_boundary_positive_high",
                    "corrected_front_growth_no_growth_low",
                    "corrected_front_growth_no_front_fail",
                    "corrected_front_growth_closed_front_fail",
                ),
                requested_steps=3,
                source_mode="landscape_seed_examples",
            )

            by_name = {lane.fixture_name: lane for lane in result.lanes}
            positive = by_name["corrected_front_growth_positive_high"]
            pressure = by_name["corrected_pressure_boundary_positive_high"]
            no_growth = by_name["corrected_front_growth_no_growth_low"]
            no_front = by_name["corrected_front_growth_no_front_fail"]
            closed_front = by_name["corrected_front_growth_closed_front_fail"]

            self.assertEqual("passed", positive.selector_status)
            self.assertEqual("passed", pressure.selector_status)
            self.assertEqual("passed", no_growth.selector_status)
            self.assertEqual("passed", no_front.selector_status)
            self.assertEqual("passed", closed_front.selector_status)
            self.assertEqual("front_capacity", positive.growth_semantics_status)
            self.assertEqual("front_capacity", pressure.growth_semantics_status)
            self.assertEqual("front_capacity", no_growth.growth_semantics_status)
            self.assertEqual("front_capacity", no_front.growth_semantics_status)
            self.assertEqual("front_capacity", closed_front.growth_semantics_status)
            self.assertEqual("grc9_front_capacity", positive.growth_parent_eligibility_mode)
            self.assertEqual("grc9_front_capacity", pressure.growth_parent_eligibility_mode)
            self.assertEqual("grc9_front_capacity", no_growth.growth_parent_eligibility_mode)
            self.assertEqual("grc9_front_capacity", no_front.growth_parent_eligibility_mode)
            self.assertEqual("grc9_front_capacity", closed_front.growth_parent_eligibility_mode)
            self.assertGreater(positive.event_counts_by_kind.get("growth", 0), 0)
            self.assertEqual(0, no_growth.event_counts_by_kind.get("growth", 0))
            self.assertEqual(0, no_front.event_counts_by_kind.get("growth", 0))
            self.assertEqual(0, closed_front.event_counts_by_kind.get("growth", 0))

            positive_report = _read_json(Path(positive.selector_report_path))
            no_growth_report = _read_json(Path(no_growth.selector_report_path))
            no_front_report = _read_json(Path(no_front.selector_report_path))
            closed_front_report = _read_json(Path(closed_front.selector_report_path))
            self.assertEqual("passed", positive_report["status"])
            self.assertEqual("passed", no_growth_report["status"])
            self.assertEqual("passed", no_front_report["status"])
            self.assertEqual("passed", closed_front_report["status"])

    def test_seed_examples_emit_expected_lifecycle_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9203",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                requested_steps=6,
                requested_steps_by_fixture={
                    "cell_basin_merge_runtime_collapse_probe": 1,
                    "cell_basin_merge_runtime_stability_control": 1,
                    "cell_developed_basin_centroid_collapse_long_window": 24,
                    "cell_full_capacity_phenomenology_cascade": 24,
                    "cell_full_capacity_cascade_low_growth": 24,
                    "cell_full_capacity_cascade_high_growth": 24,
                    "cell_full_capacity_cascade_no_merge_bridge": 24,
                    "cell_full_capacity_cascade_weak_merge_bridge": 24,
                    "cell_full_capacity_cascade_isolated_bridge": 24,
                    "cell_full_capacity_cascade_larger_basin_support": 24,
                    "cell_full_capacity_cascade_no_refinement": 24,
                    "cell_full_capacity_cascade_no_growth": 24,
                    "cell_full_capacity_cascade_balanced_basins": 24,
                    "cell_full_capacity_cascade_mild_asymmetry": 24,
                    "cell_full_capacity_cascade_threshold_asymmetry": 24,
                    "cell_full_capacity_cascade_deep_collapse": 24,
                    "cell_full_capacity_cascade_isolated_threshold": 24,
                    "cell_full_capacity_phase_balanced_no_growth": 24,
                    "cell_full_capacity_phase_balanced_low_growth": 24,
                    "cell_full_capacity_phase_balanced_nominal_growth": 24,
                    "cell_full_capacity_phase_mild_no_growth": 24,
                    "cell_full_capacity_phase_mild_low_growth": 24,
                    "cell_full_capacity_phase_mild_nominal_growth": 24,
                    "cell_full_capacity_phase_threshold_no_growth": 24,
                    "cell_full_capacity_phase_threshold_low_growth": 24,
                    "cell_full_capacity_phase_threshold_nominal_growth": 24,
                    "cell_full_capacity_phase_deep_no_growth": 24,
                    "cell_full_capacity_phase_deep_low_growth": 24,
                    "cell_full_capacity_phase_deep_nominal_growth": 24,
                },
                source_mode="legacy_growth_landscape_seed_examples",
                force_legacy_growth=True,
            )

            self.assertEqual(30, len(result.lanes))
            robustness_names = {
                "cell_full_capacity_cascade_low_growth",
                "cell_full_capacity_cascade_high_growth",
                "cell_full_capacity_cascade_no_merge_bridge",
                "cell_full_capacity_cascade_weak_merge_bridge",
                "cell_full_capacity_cascade_isolated_bridge",
                "cell_full_capacity_cascade_larger_basin_support",
                "cell_full_capacity_cascade_no_refinement",
                "cell_full_capacity_cascade_no_growth",
                "cell_full_capacity_cascade_balanced_basins",
                "cell_full_capacity_cascade_mild_asymmetry",
                "cell_full_capacity_cascade_threshold_asymmetry",
                "cell_full_capacity_cascade_deep_collapse",
                "cell_full_capacity_cascade_isolated_threshold",
            }
            self.assertTrue(
                all(
                    lane.selector_status == "passed"
                    for lane in result.lanes
                    if lane.fixture_name not in robustness_names
                ),
                [lane.to_mapping() for lane in result.lanes],
            )
            by_name = {lane.fixture_name: lane for lane in result.lanes}
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_low_growth"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_high_growth"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_no_merge_bridge"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_weak_merge_bridge"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_isolated_bridge"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_larger_basin_support"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_no_refinement"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_no_growth"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_balanced_basins"].selector_status)
            self.assertEqual("missed", by_name["cell_full_capacity_cascade_mild_asymmetry"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_threshold_asymmetry"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_deep_collapse"].selector_status)
            self.assertEqual("passed", by_name["cell_full_capacity_cascade_isolated_threshold"].selector_status)
            for phase_name in (
                "cell_full_capacity_phase_balanced_no_growth",
                "cell_full_capacity_phase_balanced_low_growth",
                "cell_full_capacity_phase_balanced_nominal_growth",
                "cell_full_capacity_phase_mild_no_growth",
                "cell_full_capacity_phase_mild_low_growth",
                "cell_full_capacity_phase_mild_nominal_growth",
                "cell_full_capacity_phase_threshold_no_growth",
                "cell_full_capacity_phase_threshold_low_growth",
                "cell_full_capacity_phase_threshold_nominal_growth",
                "cell_full_capacity_phase_deep_no_growth",
                "cell_full_capacity_phase_deep_low_growth",
                "cell_full_capacity_phase_deep_nominal_growth",
            ):
                self.assertEqual("passed", by_name[phase_name].selector_status)
            self.assertGreater(
                by_name["growth_pressure_lambda_high"].event_counts_by_kind["growth"],
                0,
            )
            self.assertGreater(
                by_name["cell_internal_valley_transport_growth_high"].event_counts_by_kind["growth"],
                0,
            )
            cascade_report = _read_json(
                Path(by_name["cell_full_capacity_phenomenology_cascade"].selector_report_path)
            )
            cascade_results = {
                result["selector_id"]: result
                for result in cascade_report["selector_results"]
            }
            self.assertEqual("passed", cascade_report["status"])
            self.assertEqual(1, cascade_results["spark_column_proxy_count"]["observed_value"])
            self.assertGreater(
                cascade_results["expansion_module_size"]["observed_value"],
                0,
            )
            self.assertGreater(cascade_results["growth_count"]["observed_value"], 0)
            self.assertTrue(
                cascade_results["runtime_collapse_like_long_window"]["observed_value"][
                    "runtime_collapse_like_long_window"
                ]
            )


def _read_json(path: Path) -> dict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
