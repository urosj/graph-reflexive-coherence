"""Tests for GRCL/Morse-facing GRCL-9V3 landscape examples."""

from __future__ import annotations

from collections import deque
import json
import unittest
from typing import Any

from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_LANDSCAPE_EXAMPLE_NAMES,
    GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9V3_LANDSCAPE_EXAMPLE_VERSION,
    GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
    GRCL9V3AppendixECellDivisionRegion,
    GRCL9V3BoundaryStratum,
    GRCL9V3CriticalRegion,
    GRCL9V3LandscapeExampleDocument,
    GRCL9V3SourceDocument,
    GRCL9V3TensorHessianProfile,
    compile_default_grcl9v3_landscape_examples_to_sources,
    compile_default_grcl9v3_landscape_seed_examples_to_sources,
    compile_grcl9v3_landscape_example_to_source,
    compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources,
    default_grcl9v3_landscape_examples,
    default_grcl9v3_landscape_seed_examples,
    grcl9v3_landscape_example_by_name,
    grcl9v3_landscape_seed_example_path_by_name,
    legacy_grcl9v3_growth_landscape_seed_example_path_by_name,
    legacy_grcl9v3_growth_landscape_seed_examples,
    validate_grcl9v3_source_document_against_manifest,
)
from pygrc.models import lower_grcl9v3_source_to_grc9v3_state


FORBIDDEN_EXAMPLE_KEYS = {
    "choice_happened",
    "collapse_happened",
    "current_flux",
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
    "solved_hessian",
    "solved_tensor",
    "spark_happened",
    "step_rows",
    "telemetry_summary",
    "topology",
}


class GRCL9V3LandscapeExamplesTest(unittest.TestCase):
    def test_default_examples_are_complete_and_ordered(self) -> None:
        examples = default_grcl9v3_landscape_examples()

        self.assertEqual(
            GRCL9V3_LANDSCAPE_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        self.assertEqual(13, len(examples))
        self.assertEqual(
            set(GRCL9V3_LANDSCAPE_EXAMPLE_NAMES),
            set(grcl9v3_landscape_example_by_name()),
        )

    def test_examples_round_trip_through_json_safe_mappings(self) -> None:
        for example in default_grcl9v3_landscape_examples():
            with self.subTest(example=example.example_name):
                payload = example.to_mapping()
                restored = GRCL9V3LandscapeExampleDocument.from_mapping(
                    json.loads(json.dumps(payload))
                )

                self.assertEqual(payload, restored.to_mapping())
                self.assertEqual(
                    GRCL9V3_LANDSCAPE_EXAMPLE_VERSION,
                    restored.example_schema_version,
                )
                self.assertTrue(restored.grcl9v3_required)

    def test_examples_do_not_embed_raw_grc9v3_or_runtime_payloads(self) -> None:
        for example in default_grcl9v3_landscape_examples():
            with self.subTest(example=example.example_name):
                self.assertEqual([], _forbidden_paths(example.to_mapping()))

    def test_required_lowering_guard_is_enforced(self) -> None:
        example = grcl9v3_landscape_example_by_name()["growth_pressure_positive_control"]
        payload = dict(example.to_mapping())
        payload.pop("grcl9v3_required")

        with self.assertRaisesRegex(ValueError, "grcl9v3_required = true"):
            GRCL9V3LandscapeExampleDocument.from_mapping(payload)

        with self.assertRaisesRegex(ValueError, "grcl9v3_required = true"):
            GRCL9V3LandscapeExampleDocument(
                example_name="bad_example",
                manifest_entry_id=example.manifest_entry_id,
                motif_id=example.motif_id,
                expected_selector_ids=example.expected_selector_ids,
                grcl9v3_required=False,
                terms=example.terms,
            )

    def test_compiler_maps_morse_terms_to_expected_mechanical_constructs(self) -> None:
        expected = {
            "hybrid_spark_gate_positive_control": (
                "hybrid_spark_region",
                "row_basis_hessian_profile",
                "hybrid_tensor_profile",
                "column_proxy_fallback_profile",
            ),
            "spark_to_expansion_positive_control": (
                "hybrid_spark_region",
                "expansion_refinement_region",
            ),
            "appendix_e_cell_division_positive_control": (
                "hybrid_spark_region",
                "expansion_refinement_region",
                "appendix_e_division_region",
            ),
            "choice_collapse_positive_control": ("choice_collapse_region",),
            "growth_pressure_positive_control": ("growth_locus",),
            "pressure_boundary_positive_control": ("growth_locus",),
            "transport_basin_rerouting_positive_control": (
                "transport_rerouting_region",
            ),
            "quiescent_hybrid_control_no_event_control": (
                "quiescent_hybrid_region",
            ),
        }
        examples = grcl9v3_landscape_example_by_name()

        for name, construct_kinds in expected.items():
            with self.subTest(example=name):
                source = compile_grcl9v3_landscape_example_to_source(examples[name])
                self.assertEqual(
                    construct_kinds,
                    tuple(construct.construct_kind for construct in source.constructs),
                )
                provenance = source.compiled_source_provenance or {}
                self.assertEqual(name, provenance["source_example_name"])
                self.assertTrue(provenance["source_term_ids_by_construct_id"])

    def test_compiler_is_deterministic_and_does_not_mutate_examples(self) -> None:
        example = grcl9v3_landscape_example_by_name()["hybrid_spark_gate_positive_control"]
        before = example.to_mapping()

        first = compile_grcl9v3_landscape_example_to_source(example)
        second = compile_grcl9v3_landscape_example_to_source(example)

        self.assertEqual(before, example.to_mapping())
        self.assertEqual(first.to_mapping(), second.to_mapping())
        self.assertIsInstance(
            GRCL9V3SourceDocument.from_mapping(first.to_mapping()),
            GRCL9V3SourceDocument,
        )

    def test_compiler_uses_authored_term_profiles_not_fixture_lookup(self) -> None:
        example = grcl9v3_landscape_example_by_name()["hybrid_spark_gate_positive_control"]
        rewritten_terms = []
        for term in example.terms:
            if isinstance(term, GRCL9V3CriticalRegion):
                profile = dict(term.profile or {})
                saturation = dict(profile.get("saturation", {}))
                saturation["active_degree"] = 6
                profile["saturation"] = saturation
                rewritten_terms.append(
                    GRCL9V3CriticalRegion(
                        term_id=term.term_id,
                        region_id=term.region_id,
                        source_role=term.source_role,
                        profile=profile,
                    )
                )
            else:
                rewritten_terms.append(term)
        rewritten = GRCL9V3LandscapeExampleDocument(
            example_name=example.example_name,
            manifest_entry_id=example.manifest_entry_id,
            motif_id=example.motif_id,
            expected_selector_ids=example.expected_selector_ids,
            terms=tuple(rewritten_terms),
            notes=example.notes,
        )

        source = compile_grcl9v3_landscape_example_to_source(rewritten)

        spark_region = source.constructs[0]
        self.assertEqual("hybrid_spark_region", spark_region.construct_kind)
        self.assertEqual(6, spark_region.saturation_profile["active_degree"])

    def test_pressure_boundary_example_compiles_to_front_capacity_source(self) -> None:
        example = grcl9v3_landscape_example_by_name()[
            "pressure_boundary_positive_control"
        ]
        source = compile_grcl9v3_landscape_example_to_source(example)

        self.assertEqual(
            "composed_grcl9v3_hybrid_composition_v1",
            source.manifest_entry_id,
        )
        self.assertEqual(
            ("pressure_boundary_growth_provenance",),
            source.expected_selector_ids,
        )
        self.assertEqual(1, len(source.constructs))
        growth = source.constructs[0]
        self.assertEqual("growth_locus", growth.construct_kind)
        self.assertEqual("front_capacity", growth.growth_semantics)
        self.assertEqual("pressure_boundary", growth.front_capacity_source)
        self.assertEqual(6, growth.inactive_parent_port)
        provenance = source.compiled_source_provenance or {}
        self.assertEqual(
            ["pressure_boundary", "growth_pressure"],
            provenance["composed_source_ancestry"],
        )

        state = lower_grcl9v3_source_to_grc9v3_state(source).state
        self.assertIn(
            "grcl9v3_expected_pressure_boundary_region_ids",
            state.cached_quantities,
        )

    def test_compiled_sources_validate_and_lower_to_connected_grc9v3_states(self) -> None:
        sources = compile_default_grcl9v3_landscape_examples_to_sources()

        self.assertEqual(
            GRCL9V3_LANDSCAPE_EXAMPLE_NAMES,
            tuple(source.fixture_name for source in sources),
        )
        for source in sources:
            with self.subTest(source=source.fixture_name):
                validate_grcl9v3_source_document_against_manifest(
                    source,
                    allow_future_vocabulary=True,
                )
                state = lower_grcl9v3_source_to_grc9v3_state(source).state
                self.assertTrue(_is_connected(state))

    def test_seed_backed_examples_load_compile_and_lower(self) -> None:
        examples = default_grcl9v3_landscape_seed_examples()
        paths = grcl9v3_landscape_seed_example_path_by_name()
        sources = compile_default_grcl9v3_landscape_seed_examples_to_sources()

        self.assertEqual(
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        self.assertEqual(set(GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES), set(paths))
        self.assertEqual(
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(source.fixture_name for source in sources),
        )
        for source in sources:
            with self.subTest(source=source.fixture_name):
                provenance = source.compiled_source_provenance or {}
                self.assertIn("configs/landscapes/seed/grcl9v3-", provenance["source_seed_reference"])
                validate_grcl9v3_source_document_against_manifest(
                    source,
                    allow_future_vocabulary=True,
                )
                self.assertTrue(
                    _is_connected(lower_grcl9v3_source_to_grc9v3_state(source).state)
                )

    def test_default_seed_examples_exclude_quarantined_legacy_growth(self) -> None:
        self.assertNotIn(
            "multi_center_collapse_learning",
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
        )
        self.assertNotIn(
            "growth_pressure_positive_control",
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
        )
        self.assertIn(
            "corrected_multi_center_collapse_learning",
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
        )
        self.assertIn(
            "corrected_front_growth_positive_control",
            GRCL9V3_LANDSCAPE_SEED_EXAMPLE_NAMES,
        )

    def test_legacy_growth_seed_examples_load_through_diagnostic_path(self) -> None:
        examples = legacy_grcl9v3_growth_landscape_seed_examples()
        paths = legacy_grcl9v3_growth_landscape_seed_example_path_by_name()
        sources = compile_legacy_grcl9v3_growth_landscape_seed_examples_to_sources()

        self.assertEqual(
            GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(example.example_name for example in examples),
        )
        self.assertEqual(
            set(GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES),
            set(paths),
        )
        self.assertEqual(
            GRCL9V3_LEGACY_GROWTH_LANDSCAPE_SEED_EXAMPLE_NAMES,
            tuple(source.fixture_name for source in sources),
        )
        self.assertTrue(
            all("legacy/grcl9v3-overaggressive-growth" in str(path) for path in paths.values())
        )

    def test_multi_center_seed_compiles_repeated_growth_and_choice_constructs(self) -> None:
        examples = {
            example.example_name: example
            for example in legacy_grcl9v3_growth_landscape_seed_examples()
        }
        source = compile_grcl9v3_landscape_example_to_source(
            examples["multi_center_collapse_learning"]
        )
        construct_kinds = [construct.construct_kind for construct in source.constructs]

        self.assertEqual(2, construct_kinds.count("growth_locus"))
        self.assertEqual(2, construct_kinds.count("choice_collapse_region"))

        state = lower_grcl9v3_source_to_grc9v3_state(source).state
        caches = state.cached_quantities
        self.assertGreaterEqual(
            len(caches["grcl9v3_expected_growth_locus_ids"]),
            2,
        )
        self.assertGreaterEqual(
            len(caches["grcl9v3_expected_choice_region_ids"]),
            4,
        )

    def test_example_terms_cover_expected_grcl_morse_vocabulary(self) -> None:
        examples = grcl9v3_landscape_example_by_name()

        spark_terms = examples["hybrid_spark_gate_positive_control"].terms
        self.assertTrue(any(isinstance(term, GRCL9V3CriticalRegion) for term in spark_terms))
        self.assertTrue(any(isinstance(term, GRCL9V3TensorHessianProfile) for term in spark_terms))

        growth_terms = examples["growth_pressure_positive_control"].terms
        self.assertTrue(any(isinstance(term, GRCL9V3BoundaryStratum) for term in growth_terms))

        pressure_terms = examples["pressure_boundary_positive_control"].terms
        pressure_growth = [
            term
            for term in pressure_terms
            if term.to_mapping()["term_kind"] == "growth_locus"
        ][0]
        self.assertEqual(
            "front_capacity",
            pressure_growth.profile["growth_semantics"],
        )
        self.assertEqual(
            "pressure_boundary",
            pressure_growth.profile["front_capacity_source"],
        )

        appendix_terms = examples["appendix_e_cell_division_positive_control"].terms
        self.assertTrue(
            any(isinstance(term, GRCL9V3AppendixECellDivisionRegion) for term in appendix_terms)
        )

    def test_runtime_smuggling_is_rejected(self) -> None:
        example = grcl9v3_landscape_example_by_name()["growth_pressure_positive_control"]
        payload = dict(example.to_mapping())
        term = dict(payload["terms"][0])
        term["profile"] = {"event_counts_by_kind": {"growth": 1}}
        payload["terms"] = [term, *payload["terms"][1:]]

        with self.assertRaisesRegex(ValueError, "event_counts_by_kind"):
            GRCL9V3LandscapeExampleDocument.from_mapping(payload)


def _is_connected(state: Any) -> bool:
    node_ids = set(state.topology.iter_live_node_ids())
    if not node_ids:
        return False
    start = next(iter(node_ids))
    visited = {start}
    queue: deque[int] = deque([start])
    while queue:
        node_id = queue.popleft()
        for edge_id in state.topology.incident_edge_ids(node_id):
            endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
            other = endpoint_b[0] if endpoint_a[0] == node_id else endpoint_a[0]
            if other not in visited:
                visited.add(other)
                queue.append(other)
    return visited == node_ids


def _forbidden_paths(payload: Any) -> list[str]:
    paths: list[str] = []
    queue: deque[tuple[str, Any]] = deque([("$", payload)])
    while queue:
        path, value = queue.popleft()
        if isinstance(value, dict):
            for key, item in value.items():
                key_text = str(key)
                child_path = f"{path}.{key_text}"
                if key_text in FORBIDDEN_EXAMPLE_KEYS:
                    paths.append(child_path)
                queue.append((child_path, item))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                queue.append((f"{path}[{index}]", item))
    return paths


if __name__ == "__main__":
    unittest.main()
