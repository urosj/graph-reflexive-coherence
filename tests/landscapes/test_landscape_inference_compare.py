from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    BasinSeedPrimitive,
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    ValleySeedPrimitive,
    compare_landscape_seeds,
    write_landscape_inference_comparison_report,
)


def _seed(name: str, primitives: list) -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="landscape_seed.v1",
        seed_version="test",
        meta=SeedDocumentMeta(name=name, source_kind="test"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=0.0,
            kappa_c=0.0,
            dt=0.1,
            potential=SeedPotential(type="test"),
        ),
        primitives=primitives,
    )


def _observed_extension(authored_id: str) -> dict[str, object]:
    return {
        "landscape_inference": {
            "authority": "observed",
            "matched_authored_primitive_id": authored_id,
        }
    }


class LandscapeInferenceComparisonTest(unittest.TestCase):
    def test_provenance_match_is_preserved(self) -> None:
        authored = _seed(
            "authored",
            [BasinSeedPrimitive(id="source_basin", role="identity_basin", depth_hint=0)],
        )
        observed = _seed(
            "observed",
            [
                BasinSeedPrimitive(
                    id="observed_basin",
                    role="identity_basin",
                    depth_hint=0,
                    extensions=_observed_extension("source_basin"),
                )
            ],
        )

        report = compare_landscape_seeds(authored, observed)

        self.assertEqual(1, len(report.records))
        record = report.records[0]
        self.assertEqual("preserved", record.relationship)
        self.assertEqual(("source_basin",), record.authored_ids)
        self.assertEqual(("observed_basin",), record.observed_ids)
        self.assertEqual("provenance", record.match_mode)
        self.assertTrue(record.provenance_available)

    def test_split_and_collapse_are_explicit(self) -> None:
        authored = _seed(
            "authored",
            [
                ValleySeedPrimitive(
                    id="source_route",
                    role="valley_channel",
                    from_id="a",
                    to_id="b",
                ),
                ValleySeedPrimitive(
                    id="source_route_alt",
                    role="valley_channel",
                    from_id="a",
                    to_id="b",
                ),
            ],
        )
        observed = _seed(
            "observed",
            [
                ValleySeedPrimitive(
                    id="observed_route_1",
                    role="valley_channel",
                    from_id="a",
                    to_id="b",
                ),
                ValleySeedPrimitive(
                    id="observed_route_2",
                    role="valley_channel",
                    from_id="a",
                    to_id="b",
                ),
            ],
        )

        report = compare_landscape_seeds(authored, observed)
        relationships = {record.relationship for record in report.records}

        self.assertIn("split", relationships)
        self.assertIn("collapsed", relationships)
        self.assertTrue(any(len(record.observed_ids) > 1 for record in report.records))
        self.assertTrue(any(len(record.authored_ids) > 1 for record in report.records))

    def test_unmatched_primitives_are_emerged_and_dissolved(self) -> None:
        authored = _seed(
            "authored",
            [BasinSeedPrimitive(id="lost_basin", role="identity_basin", depth_hint=0)],
        )
        observed = _seed(
            "observed",
            [ValleySeedPrimitive(id="new_path", role="pheromone_marker", from_id="x", to_id="y")],
        )

        report = compare_landscape_seeds(authored, observed)
        relationships = {record.relationship for record in report.records}

        self.assertIn("emerged", relationships)
        self.assertIn("dissolved", relationships)

    def test_comparison_is_deterministic_and_writes_reports(self) -> None:
        authored = _seed(
            "authored",
            [BasinSeedPrimitive(id="source_basin", role="identity_basin", depth_hint=0)],
        )
        observed = _seed(
            "observed",
            [
                BasinSeedPrimitive(
                    id="observed_basin",
                    role="identity_basin",
                    depth_hint=0,
                    extensions=_observed_extension("source_basin"),
                )
            ],
        )

        first = compare_landscape_seeds(authored, observed).to_mapping()
        second = compare_landscape_seeds(authored, observed).to_mapping()

        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as tmp:
            json_path, markdown_path = write_landscape_inference_comparison_report(
                compare_landscape_seeds(authored, observed),
                Path(tmp),
            )
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertIn("preserved", json_path.read_text(encoding="utf-8"))
            self.assertIn("Landscape Inference", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
