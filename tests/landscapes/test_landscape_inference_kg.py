from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    ValleySeedPrimitive,
    landscape_seed_to_dynamic_kg_view,
    write_dynamic_kg_view,
)


def _seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="landscape_seed.v1",
        seed_version="test",
        meta=SeedDocumentMeta(name="kg_seed", source_kind="test"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=0.0,
            kappa_c=0.0,
            dt=0.1,
            potential=SeedPotential(type="test"),
        ),
        primitives=[
            BasinSeedPrimitive(
                id="basin_a",
                role="identity_basin",
                boundary_ids=["ridge_ab"],
                extensions={"landscape_inference_endpoint": {"classifier_id": "test"}},
            ),
            BasinSeedPrimitive(id="basin_b", role="identity_basin"),
            RidgeSeedPrimitive(
                id="ridge_ab",
                role="boundary_ridge",
                adjacent_ids=["basin_a", "basin_b"],
            ),
            ValleySeedPrimitive(
                id="valley_ab",
                role="valley_channel",
                from_id="basin_a",
                to_id="basin_b",
            ),
            JunctionSeedPrimitive(
                id="junction_a",
                role="router",
                host_id="basin_a",
                branch_target_ids=["basin_b"],
            ),
        ],
    )


class LandscapeInferenceKgViewTest(unittest.TestCase):
    def test_kg_view_reuses_landscape_primitives_without_new_ontology(self) -> None:
        view = landscape_seed_to_dynamic_kg_view(_seed())

        self.assertEqual("dynamic_knowledge_graph_export", view["view_kind"])
        self.assertEqual("pygrc_landscape_seed_primitives", view["ontology_source"])
        self.assertFalse(view["introduces_new_ontology"])
        self.assertEqual(5, view["node_count"])
        basin_node = next(node for node in view["nodes"] if node["id"] == "basin_a")
        self.assertEqual(["landscape_inference_endpoint"], basin_node["inference_extension_keys"])
        relations = {edge["relation"] for edge in view["edges"]}
        self.assertIn("channels_to", relations)
        self.assertIn("hosts_junction", relations)
        self.assertIn("separates_or_touches", relations)

    def test_kg_view_is_deterministic(self) -> None:
        first = landscape_seed_to_dynamic_kg_view(_seed())
        second = landscape_seed_to_dynamic_kg_view(_seed())

        self.assertEqual(first, second)

    def test_write_dynamic_kg_view(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = write_dynamic_kg_view(
                _seed(),
                Path(tmp) / "dynamic_kg_view.json",
                source_seed_path="configs/landscapes/seed/example.seed.yaml",
            )

            self.assertTrue(output_path.exists())
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("configs/landscapes/seed/example.seed.yaml", payload["source_seed_path"])
            self.assertEqual("kg_seed", payload["seed_name"])


if __name__ == "__main__":
    unittest.main()
