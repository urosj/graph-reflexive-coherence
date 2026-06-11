"""I/O tests for normalized landscape seeds."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    landscape_seed_from_data,
    landscape_seed_to_canonical_json,
    landscape_seed_to_data,
    load_landscape_seed,
    save_landscape_seed,
)


def _build_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(
            name="fixture",
            source_kind="translated_seed",
            translation_mode="lossless_source_normalization",
        ),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.5,
            zeta_c=0.8,
            kappa_c=0.6,
            dt=0.05,
            potential=SeedPotential(type="double_well", params={"a": 1.0}),
        ),
        primitives=[
            BasinSeedPrimitive(
                id="cytoplasm",
                coherence_prior=0.85,
                depth_hint=0,
                chart_center_hint=[0.5, 0.5],
                chart_scale_hint={"radius": 0.3},
            )
        ],
        geometry_hints=SeedGeometryHints(source_chart="planar_hint"),
        extensions={"source_pde": {"meta": {"author": "fixture"}}},
    )


class LandscapeSeedIOTest(unittest.TestCase):
    """Validate the Phase L seed I/O surface."""

    def test_seed_to_data_and_from_data_roundtrip(self) -> None:
        seed = _build_seed()

        data = landscape_seed_to_data(seed)
        restored = landscape_seed_from_data(data)

        self.assertEqual(data, landscape_seed_to_data(restored))

    def test_load_and_save_yaml_roundtrip(self) -> None:
        seed = _build_seed()

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "fixture.seed.yaml"
            save_landscape_seed(seed, path)
            restored = load_landscape_seed(path)

        self.assertEqual(landscape_seed_to_data(seed), landscape_seed_to_data(restored))

    def test_load_and_save_json_roundtrip(self) -> None:
        seed = _build_seed()

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "fixture.seed.json"
            save_landscape_seed(seed, path)
            restored = load_landscape_seed(path)

        self.assertEqual(landscape_seed_to_data(seed), landscape_seed_to_data(restored))

    def test_canonical_json_is_derived_from_normalized_data(self) -> None:
        seed = _build_seed()

        rendered = landscape_seed_to_canonical_json(seed)
        decoded = json.loads(rendered)

        self.assertEqual(landscape_seed_to_data(seed), decoded)

    def test_from_data_rejects_missing_required_keys(self) -> None:
        data = landscape_seed_to_data(_build_seed())
        data.pop("meta")

        with self.assertRaises(InvalidLandscapeSeedError):
            landscape_seed_from_data(data)

    def test_from_data_rejects_unknown_primitive_type(self) -> None:
        data = landscape_seed_to_data(_build_seed())
        data["primitives"][0]["type"] = "unknown"

        with self.assertRaises(InvalidLandscapeSeedError):
            landscape_seed_from_data(data)

    def test_load_rejects_non_mapping_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "fixture.seed.yaml"
            path.write_text("- not-a-seed\n", encoding="utf-8")

            with self.assertRaises(InvalidLandscapeSeedError):
                load_landscape_seed(path)

    def test_load_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "fixture.seed.json"
            path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaises(InvalidLandscapeSeedError):
                load_landscape_seed(path)

    def test_unsupported_seed_file_suffix_is_rejected(self) -> None:
        seed = _build_seed()

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "fixture.seed.txt"
            with self.assertRaises(ValueError):
                save_landscape_seed(seed, path)
