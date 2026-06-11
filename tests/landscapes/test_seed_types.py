"""Contract tests for normalized landscape seed runtime types."""

from __future__ import annotations

import unittest

from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LANDSCAPE_PRIMITIVE_TYPES,
    LandscapeSeed,
    PRIMITIVE_BASIN,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_RIDGE,
    PRIMITIVE_SADDLE,
    PRIMITIVE_VALLEY,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
    TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
    TRANSLATION_MODES,
    ValleySeedPrimitive,
)


class LandscapeSeedTypesTest(unittest.TestCase):
    """Validate the Phase L runtime seed type surface."""

    def test_translation_modes_are_exposed(self) -> None:
        self.assertEqual(
            (
                TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
                TRANSLATION_MODE_SEMANTIC_ENRICHMENT,
            ),
            TRANSLATION_MODES,
        )

    def test_primitive_type_catalog_is_exposed(self) -> None:
        self.assertEqual(
            (
                PRIMITIVE_BASIN,
                PRIMITIVE_PLATEAU,
                PRIMITIVE_RIDGE,
                PRIMITIVE_VALLEY,
                PRIMITIVE_JUNCTION,
                PRIMITIVE_SADDLE,
            ),
            LANDSCAPE_PRIMITIVE_TYPES,
        )

    def test_landscape_seed_can_be_constructed_with_representative_runtime_objects(
        self,
    ) -> None:
        seed = LandscapeSeed(
            seed_schema="pygrc.landscape_seed",
            seed_version="0.1",
            meta=SeedDocumentMeta(
                name="fixture",
                source_kind="translated_seed",
                translation_mode=TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION,
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
                    chart_center_hint=[0.5, 0.5],
                    chart_scale_hint={"radius": 0.3},
                ),
                RidgeSeedPrimitive(
                    id="membrane",
                    owner_id="cytoplasm",
                    thickness_hint=0.02,
                    chart_principal_axis_hint=[0.0, 1.0],
                ),
                ValleySeedPrimitive(
                    id="channel",
                    from_id="cytoplasm",
                    to_id="cytoplasm",
                    path_hint="straight",
                ),
                JunctionSeedPrimitive(
                    id="routing",
                    type=PRIMITIVE_SADDLE,
                    host_id="cytoplasm",
                    branch_target_ids=["cytoplasm"],
                ),
            ],
            transport_intent=[
                SeedTransportIntent(
                    id="t0",
                    mode="directed_bias",
                    sources=["cytoplasm"],
                    targets=["cytoplasm"],
                )
            ],
            geometry_hints=SeedGeometryHints(source_chart="planar_hint"),
            extensions={"source_pde": {"meta": {"author": "fixture"}}},
        )

        self.assertEqual("pygrc.landscape_seed", seed.seed_schema)
        self.assertEqual("fixture", seed.meta.name)
        self.assertEqual(4, len(seed.primitives))
        self.assertEqual([0.5, 0.5], seed.primitives[0].chart_center_hint)
        self.assertEqual([0.0, 1.0], seed.primitives[1].chart_principal_axis_hint)
        self.assertEqual(PRIMITIVE_SADDLE, seed.primitives[3].type)
        self.assertEqual("planar_hint", seed.geometry_hints.source_chart)

    def test_extension_containers_default_to_independent_mutable_objects(self) -> None:
        left = BasinSeedPrimitive(id="left")
        right = BasinSeedPrimitive(id="right")

        left.extensions["source_pde"] = {"x": 1}

        self.assertEqual({}, right.extensions)
        self.assertEqual([], right.tags)
        self.assertEqual({}, right.hints)
