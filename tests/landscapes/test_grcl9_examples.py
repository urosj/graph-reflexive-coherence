"""Tests for GRCL/Morse-facing GRCL-9 landscape examples."""

from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import tempfile
import unittest
from typing import Any

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_LANDSCAPE_EXAMPLE_NAMES,
    GRCL9_LANDSCAPE_EXAMPLE_VERSION,
    GRCL9BoundaryStratum,
    GRCL9CriticalRegion,
    GRCL9GradientPressure,
    GRCL9LandscapeExampleDocument,
    GRCL9SourceDocument,
    compile_default_grcl9_landscape_examples_to_sources,
    compile_grcl9_landscape_example_to_source,
    default_grcl9_landscape_examples,
    grcl9_landscape_example_by_name,
)
from pygrc.models import lower_grcl9_source_to_grc9_state
from pygrc.telemetry import run_grcl9_lowering_replay_session


FORBIDDEN_EXAMPLE_KEYS = {
    "edge_id",
    "event_counts_by_kind",
    "event_history",
    "event_rows",
    "flux_uv",
    "node_id",
    "port_edges",
    "runtime_events",
    "solved_diagnostic",
    "solved_flux",
    "spark_happened",
    "step_rows",
    "telemetry_summary",
    "topology",
}


class GRCL9LandscapeExamplesTest(unittest.TestCase):
    def test_default_examples_are_complete_and_ordered(self) -> None:
        examples = default_grcl9_landscape_examples()

        self.assertEqual(
            GRCL9_LANDSCAPE_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        self.assertEqual(len(GRCL9_LANDSCAPE_EXAMPLE_NAMES), len(examples))
        self.assertEqual(set(GRCL9_LANDSCAPE_EXAMPLE_NAMES), set(grcl9_landscape_example_by_name()))

    def test_examples_round_trip_through_json_safe_mappings(self) -> None:
        for example in default_grcl9_landscape_examples():
            with self.subTest(example=example.example_name):
                payload = example.to_mapping()
                restored = GRCL9LandscapeExampleDocument.from_mapping(
                    json.loads(json.dumps(payload))
                )

                self.assertEqual(payload, restored.to_mapping())
                self.assertEqual(GRCL9_LANDSCAPE_EXAMPLE_VERSION, restored.example_schema_version)
                self.assertTrue(restored.grcl9_required)

    def test_examples_do_not_embed_raw_grc9_or_runtime_payloads(self) -> None:
        for example in default_grcl9_landscape_examples():
            with self.subTest(example=example.example_name):
                self.assertEqual([], _forbidden_paths(example.to_mapping()))

    def test_required_lowering_guard_is_enforced(self) -> None:
        example = grcl9_landscape_example_by_name()["growth_pressure_lambda_high"]
        payload = dict(example.to_mapping())
        payload.pop("grcl9_required")

        with self.assertRaisesRegex(ValueError, "grcl9_required = true"):
            GRCL9LandscapeExampleDocument.from_mapping(payload)

        with self.assertRaisesRegex(ValueError, "grcl9_required = true"):
            GRCL9LandscapeExampleDocument(
                example_name="bad_example",
                manifest_entry_id=example.manifest_entry_id,
                grcl9_required=False,
                terms=example.terms,
            )

    def test_compiler_maps_morse_terms_to_expected_mechanical_constructs(self) -> None:
        expected = {
            "spark_column_proxy_eps_pass": (
                "spark_candidate_region",
                "column_proxy_profile",
            ),
            "spark_instability_tau_pass": (
                "spark_candidate_region",
                "instability_profile",
            ),
            "spark_to_expansion_d_eff_high": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
            ),
            "growth_pressure_lambda_high": ("growth_locus",),
            "post_expansion_fission_min_mass_pass": (
                "post_expansion_fission_geometry",
            ),
            "cell_refinement_budget_partition_expansion_high": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
            ),
            "cell_internal_valley_transport_growth_high": ("growth_locus",),
            "cell_membrane_rupture_structural_probe": (
                "spark_candidate_region",
                "column_proxy_profile",
            ),
            "cell_basin_merge_before_persistence_probe": (
                "post_expansion_fission_geometry",
            ),
            "cell_basin_merge_runtime_collapse_probe": (
                "post_expansion_fission_geometry",
            ),
            "cell_basin_merge_runtime_stability_control": (
                "post_expansion_fission_geometry",
            ),
            "cell_developed_basin_centroid_collapse_long_window": (
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_phenomenology_cascade": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_low_growth": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_high_growth": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_no_merge_bridge": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_weak_merge_bridge": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_isolated_bridge": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_larger_basin_support": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_no_refinement": (
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_no_growth": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_balanced_basins": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_mild_asymmetry": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_threshold_asymmetry": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_deep_collapse": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_full_capacity_cascade_isolated_threshold": (
                "spark_candidate_region",
                "column_proxy_profile",
                "expansion_refinement_region",
                "growth_locus",
                "post_expansion_fission_geometry",
            ),
            "cell_support_loss_identity_decay_probe": ("growth_locus",),
            "cell_saddle_choice_pressure_structural_probe": (
                "spark_candidate_region",
                "instability_profile",
            ),
        }
        examples = grcl9_landscape_example_by_name()

        for name, construct_kinds in expected.items():
            with self.subTest(example=name):
                source = compile_grcl9_landscape_example_to_source(examples[name])
                self.assertEqual(
                    construct_kinds,
                    tuple(construct.construct_kind for construct in source.constructs),
                )
                provenance = source.compiled_source_provenance or {}
                self.assertEqual(name, provenance["source_example_name"])
                self.assertTrue(provenance["source_term_ids_by_construct_id"])

    def test_compiler_is_deterministic_and_does_not_mutate_examples(self) -> None:
        example = grcl9_landscape_example_by_name()["spark_column_proxy_eps_pass"]
        before = example.to_mapping()

        first = compile_grcl9_landscape_example_to_source(example)
        second = compile_grcl9_landscape_example_to_source(example)

        self.assertEqual(before, example.to_mapping())
        self.assertEqual(first.to_mapping(), second.to_mapping())
        self.assertIsInstance(GRCL9SourceDocument.from_mapping(first.to_mapping()), GRCL9SourceDocument)

    def test_compiled_sources_validate_and_lower_to_connected_grc9_states(self) -> None:
        sources = compile_default_grcl9_landscape_examples_to_sources()

        self.assertEqual(
            GRCL9_LANDSCAPE_EXAMPLE_NAMES,
            tuple(source.fixture_name for source in sources),
        )
        for source in sources:
            with self.subTest(source=source.fixture_name):
                restored = GRCL9SourceDocument.from_mapping(source.to_mapping())
                result = lower_grcl9_source_to_grc9_state(restored)
                self.assertTrue(_is_connected(result.state))

    def test_replay_can_store_authored_examples_and_compiled_sources_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_grcl9_lowering_replay_session(
                session_id="S9201",
                output_root=Path(temp_dir) / "grcl9" / "lowering",
                fixture_names=("spark_column_proxy_eps_fail",),
                requested_steps=1,
                source_mode="landscape_examples",
            )

            lane = result.lanes[0]
            example_path = (
                result.session_root
                / "grcl_landscape_examples"
                / "spark_column_proxy_eps_fail.json"
            )
            compiled_source = GRCL9SourceDocument.from_mapping(
                _read_json(Path(lane.source_fixture_path))
            )
            manifest = _read_json(result.session_manifest_path)

            self.assertTrue(example_path.exists())
            self.assertEqual("landscape_examples", manifest["source_mode"])
            self.assertIn("compiled_source_provenance", compiled_source.to_mapping())
            self.assertTrue(compiled_source.compiled_source_provenance)

    def test_runtime_result_smuggling_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "not allowed in GRCL-9 examples"):
            GRCL9CriticalRegion(
                term_id="bad_critical_region",
                motif_id="spark_column_proxy",
                region_id="candidate",
                coherence_profile={"node_id": 1},
            )

        with self.assertRaisesRegex(ValueError, "not allowed in GRCL-9 examples"):
            GRCL9LandscapeExampleDocument(
                example_name="bad_growth_example",
                manifest_entry_id="grcl9_lowering_growth_pressure_v1",
                terms=(
                    GRCL9BoundaryStratum(
                        term_id="boundary",
                        motif_id="growth_pressure",
                        stratum_id="growth_boundary",
                        parent_region_id="parent",
                    ),
                    GRCL9GradientPressure(
                        term_id="pressure",
                        motif_id="growth_pressure",
                        pressure_id="pressure",
                        boundary_stratum_id="growth_boundary",
                    ),
                ),
                notes="spark_happened",
            )


def _forbidden_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        paths: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_EXAMPLE_KEYS:
                paths.append(path)
            paths.extend(_forbidden_paths(item, path))
        return paths
    if isinstance(value, list):
        paths = []
        for index, item in enumerate(value):
            paths.extend(_forbidden_paths(item, f"{prefix}[{index}]"))
        return paths
    return []


def _is_connected(state: Any) -> bool:
    node_ids = tuple(state.topology.iter_live_node_ids())
    if not node_ids:
        return False
    seen = {node_ids[0]}
    queue: deque[int] = deque([node_ids[0]])
    while queue:
        node_id = queue.popleft()
        for neighbor in state.topology.neighbors(node_id):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == set(node_ids)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
