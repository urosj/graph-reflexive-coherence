"""Translation tests for PDE landscape DSL normalization."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    PlateauSeedPrimitive,
    PRIMITIVE_SADDLE,
    TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
    RidgeSeedPrimitive,
    TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
    ValleySeedPrimitive,
    landscape_seed_to_data,
    translate_pde_landscape_data,
    translate_pde_landscape_json,
)
try:
    from .pde_source_examples import (
        build_cell_like_source,
        build_cell4_like_source,
        build_explicit_plateau_and_saddle_source,
        build_periodic_source,
        build_routing_source,
    )
except ImportError:  # pragma: no cover - supports direct directory discovery.
    from pde_source_examples import (  # type: ignore[no-redef]
        build_cell_like_source,
        build_cell4_like_source,
        build_explicit_plateau_and_saddle_source,
        build_periodic_source,
        build_routing_source,
    )


class PDELandscapeTranslationTest(unittest.TestCase):
    """Validate conservative PDE DSL to seed translation."""

    def test_translate_pde_landscape_data_maps_top_level_and_primitives(self) -> None:
        translated = translate_pde_landscape_data(
            build_cell_like_source(),
            source_reference="rc-sim/configs/landscapes/cell-like.json",
        )

        self.assertEqual("pygrc.landscape_seed", translated.seed_schema)
        self.assertEqual("Cell-Like", translated.meta.name)
        self.assertEqual(
            "rc-sim/configs/landscapes/cell-like.json",
            translated.meta.source_reference,
        )
        self.assertEqual("pde_landscape_dsl", translated.meta.source_kind)
        self.assertEqual(
            TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
            translated.meta.translation_mode,
        )
        self.assertEqual(["cell", "fixture"], translated.meta.tags)
        self.assertEqual("planar_hint", translated.geometry_hints.source_chart)

        self.assertEqual(4, len(translated.primitives))
        self.assertIsInstance(translated.primitives[0], BasinSeedPrimitive)
        self.assertIsInstance(translated.primitives[1], RidgeSeedPrimitive)
        self.assertIsInstance(translated.primitives[3], ValleySeedPrimitive)
        self.assertEqual(0, translated.primitives[0].depth_hint)
        self.assertEqual(1, translated.primitives[2].depth_hint)
        self.assertAlmostEqual(0.03, translated.primitives[1].thickness_hint)
        self.assertEqual(
            {"shape_mode": "ellipse"},
            translated.primitives[1].anisotropy_hint,
        )

        source_extension = translated.extensions["source_pde"]
        self.assertEqual(
            {"author": "RC Landscape Iteration 1", "date": "2026-02-16"},
            source_extension["meta"],
        )
        self.assertIn("compile", source_extension)
        self.assertEqual(
            {"profile_transform": "none"},
            source_extension["potential_compile_policy"],
        )
        self.assertEqual([], translated.transport_intent)

    def test_translate_pde_landscape_data_keeps_default_translation_conservative(self) -> None:
        translated = translate_pde_landscape_data(build_routing_source())

        primitive_types = [primitive.type for primitive in translated.primitives]
        self.assertEqual(["basin", "basin", "basin", "valley"], primitive_types)
        self.assertNotIn(PRIMITIVE_SADDLE, primitive_types)
        self.assertEqual(1, len(translated.transport_intent))
        self.assertEqual(
            "channel_preference",
            translated.transport_intent[0].mode,
        )
        self.assertEqual(
            "channel_junction_to_mito1",
            translated.transport_intent[0].carrier_id,
        )

    def test_translate_pde_landscape_data_maps_periodic_geometry_and_budget(self) -> None:
        translated = translate_pde_landscape_data(build_periodic_source())

        self.assertEqual(12.5, translated.constitutive_profile.budget_b)
        self.assertIsNotNone(translated.geometry_hints)
        self.assertEqual("planar_periodic_hint", translated.geometry_hints.source_chart)
        self.assertEqual({"x": True, "y": True}, translated.geometry_hints.periodicity)
        self.assertEqual("unit_box", translated.geometry_hints.scale_units)
        self.assertEqual(
            {
                "distance_mode": "periodic_torus",
                "period_x": 1.0,
                "period_y": 1.0,
            },
            translated.extensions["source_pde"]["geometry"],
        )

    def test_translate_pde_landscape_data_passes_through_explicit_plateau_and_saddle(self) -> None:
        translated = translate_pde_landscape_data(build_explicit_plateau_and_saddle_source())

        plateau = next(
            primitive
            for primitive in translated.primitives
            if isinstance(primitive, PlateauSeedPrimitive)
        )
        saddle = next(
            primitive
            for primitive in translated.primitives
            if isinstance(primitive, JunctionSeedPrimitive) and primitive.type == "saddle"
        )

        self.assertEqual("routing_plateau", plateau.id)
        self.assertEqual("cytoplasm", plateau.parent_id)
        self.assertEqual(1, plateau.depth_hint)
        self.assertEqual(["nucleus", "decision_saddle"], plateau.hosted_primitive_ids)
        self.assertEqual("neutral", plateau.stability_class)
        self.assertEqual("routing_surface", plateau.role)
        self.assertEqual("decision_saddle", saddle.id)
        self.assertEqual("routing_plateau", saddle.host_id)
        self.assertEqual(["nucleus", "cytoplasm"], saddle.branch_target_ids)
        self.assertEqual("decision_point", saddle.junction_role)
        self.assertEqual([0.52, 0.5], saddle.chart_center_hint)

    def test_translate_pde_landscape_data_tolerates_unit_box_rounding_drift(self) -> None:
        source = build_periodic_source()
        source["geometry"]["period_x"] = 1.0 + 1e-10  # type: ignore[index]
        source["geometry"]["period_y"] = 1.0 - 1e-10  # type: ignore[index]

        translated = translate_pde_landscape_data(source)

        self.assertEqual("unit_box", translated.geometry_hints.scale_units)

    def test_translate_pde_landscape_data_snaps_quadrant_axis_hints(self) -> None:
        translated = translate_pde_landscape_data(build_cell_like_source())
        ridge = translated.primitives[1]
        assert isinstance(ridge, RidgeSeedPrimitive)

        self.assertEqual([0.0, 1.0], ridge.chart_principal_axis_hint)

    def test_translate_pde_landscape_json_reads_file(self) -> None:
        source = build_cell_like_source()

        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "fixture.json"
            source_path.write_text(
                json.dumps(source),
                encoding="utf-8",
            )
            translated = translate_pde_landscape_json(source_path)

        self.assertEqual(str(source_path), translated.meta.source_reference)
        self.assertEqual(
            landscape_seed_to_data(translate_pde_landscape_data(source, source_reference=str(source_path))),
            landscape_seed_to_data(translated),
        )

    def test_translate_pde_landscape_data_rejects_unknown_source_primitive(self) -> None:
        source = build_cell_like_source()
        source["primitives"].append({"type": "wormhole", "name": "unsupported"})  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_rejects_non_finite_source_numbers(self) -> None:
        source = build_cell_like_source()
        source["primitives"][0]["coherence"] = math.nan  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_rejects_invalid_ridge_radius_order(self) -> None:
        source = build_cell_like_source()
        source["primitives"][1]["inner_radius"] = 0.4  # type: ignore[index]
        source["primitives"][1]["outer_radius"] = 0.3  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_rejects_unknown_transport_direction(self) -> None:
        source = build_routing_source()
        source["initial_flux"]["direction"] = "oscillatory"  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_rejects_ambiguous_valley_carrier(self) -> None:
        source = build_routing_source()
        source["primitives"].append(  # type: ignore[index]
            {
                "type": "valley",
                "name": "channel_junction_to_mito1_alt",
                "from": "routing_junction",
                "to": "mitochondrion_1",
                "path_type": "bezier",
                "width": 0.02,
                "coherence": 0.5,
                "control_points": [[0.45, 0.52], [0.39, 0.47]],
            }
        )
        source["initial_flux"]["channels"][0]["name"] = "unmatched_channel_name"  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_rejects_whitespace_only_primitive_name(self) -> None:
        source = build_cell_like_source()
        source["primitives"][0]["name"] = "   "  # type: ignore[index]

        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(source)

    def test_translate_pde_landscape_data_deep_copies_source_extensions(self) -> None:
        source = build_cell_like_source()
        source["primitives"][0]["custom_extension"] = {  # type: ignore[index]
            "nested": [1, 2, 3]
        }
        translated = translate_pde_landscape_data(source)

        source["compile"]["value_range"]["min"] = -1.0  # type: ignore[index]
        source["potential"]["compile_policy"]["profile_transform"] = "changed"  # type: ignore[index]
        source["primitives"][0]["custom_extension"]["nested"][0] = 99  # type: ignore[index]

        self.assertEqual(
            0.0,
            translated.extensions["source_pde"]["compile"]["value_range"]["min"],
        )
        self.assertEqual(
            "none",
            translated.extensions["source_pde"]["potential_compile_policy"]["profile_transform"],
        )
        primitive = translated.primitives[0]
        assert isinstance(primitive, BasinSeedPrimitive)
        self.assertEqual(
            {"nested": [1, 2, 3]},
            primitive.extensions["source_pde"]["custom_extension"],
        )

    def test_translate_pde_landscape_data_annotates_saddle_like_routing_hub(self) -> None:
        translated = translate_pde_landscape_data(build_cell4_like_source())

        routing = next(
            primitive
            for primitive in translated.primitives
            if isinstance(primitive, BasinSeedPrimitive) and primitive.id == "routing_junction"
        )
        source_pde_extension = routing.extensions["source_pde"]
        self.assertEqual("saddle_like_hub", source_pde_extension["implied_role"])
        self.assertEqual(
            ["channel_junction_to_mito1", "channel_junction_to_mito2", "channel_junction_to_mito3"],
            source_pde_extension["implied_structure"]["outgoing_valley_ids"],
        )
        self.assertEqual(
            ["channel_nucleus_to_junction"],
            source_pde_extension["implied_structure"]["incoming_valley_ids"],
        )
        self.assertEqual(
            ["routing_junction_ridge"],
            source_pde_extension["implied_structure"]["owned_ridge_ids"],
        )
        self.assertTrue(
            any("routing_junction" in note for note in translated.meta.translation_notes)
        )
        self.assertTrue(
            any("no explicit saddle primitive" in note for note in translated.meta.translation_notes)
        )

    def test_translate_pde_landscape_data_does_not_synthesize_plateau_or_saddle_in_lossless_mode(
        self,
    ) -> None:
        translated = translate_pde_landscape_data(build_cell4_like_source())

        self.assertNotIn("plateau", [primitive.type for primitive in translated.primitives])
        self.assertNotIn("saddle", [primitive.type for primitive in translated.primitives])

    def test_translate_pde_landscape_data_keeps_semantic_enrichment_deferred(self) -> None:
        with self.assertRaises(InvalidLandscapeSeedError):
            translate_pde_landscape_data(
                build_cell4_like_source(),
                translation_mode=TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
            )


if __name__ == "__main__":
    unittest.main()
