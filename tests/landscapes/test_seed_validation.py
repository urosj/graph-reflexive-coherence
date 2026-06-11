"""Validation tests for normalized landscape seeds."""

from __future__ import annotations

import math
import unittest

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_SADDLE,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
    validate_landscape_seed,
)


def _build_valid_seed() -> LandscapeSeed:
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
            ),
            BasinSeedPrimitive(
                id="nucleus",
                parent_id="cytoplasm",
                coherence_prior=0.94,
                depth_hint=1,
                chart_center_hint=[0.46, 0.54],
                chart_scale_hint={"radius": 0.12},
            ),
            ValleySeedPrimitive(
                id="channel",
                from_id="cytoplasm",
                to_id="nucleus",
                width_hint=0.02,
            ),
            JunctionSeedPrimitive(
                id="routing",
                type=PRIMITIVE_SADDLE,
                host_id="cytoplasm",
                branch_target_ids=["nucleus"],
            ),
        ],
        transport_intent=[
            SeedTransportIntent(
                id="t0",
                mode="directed_bias",
                sources=["cytoplasm"],
                targets=["nucleus"],
                carrier_id="channel",
            )
        ],
        geometry_hints=SeedGeometryHints(source_chart="planar_hint"),
        extensions={"future_family": {"some": "payload"}},
    )


class LandscapeSeedValidationTest(unittest.TestCase):
    """Validate the Phase L normalized seed validation boundary."""

    def test_validate_landscape_seed_accepts_representative_valid_seed(self) -> None:
        seed = _build_valid_seed()

        validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_duplicate_primitive_ids(self) -> None:
        seed = _build_valid_seed()
        seed.primitives.append(BasinSeedPrimitive(id="cytoplasm"))

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_unknown_cross_reference(self) -> None:
        seed = _build_valid_seed()
        valley = seed.primitives[2]
        assert isinstance(valley, ValleySeedPrimitive)
        valley.to_id = "missing"

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_hierarchy_cycle(self) -> None:
        seed = _build_valid_seed()
        cytoplasm = seed.primitives[0]
        assert isinstance(cytoplasm, BasinSeedPrimitive)
        cytoplasm.parent_id = "nucleus"

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_depth_hint_contradiction(self) -> None:
        seed = _build_valid_seed()
        nucleus = seed.primitives[1]
        assert isinstance(nucleus, BasinSeedPrimitive)
        nucleus.depth_hint = 2

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_non_positive_budget_when_present(
        self,
    ) -> None:
        seed = _build_valid_seed()
        seed.constitutive_profile.budget_b = 0.0

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_nan_coherence_prior(self) -> None:
        seed = _build_valid_seed()
        cytoplasm = seed.primitives[0]
        assert isinstance(cytoplasm, BasinSeedPrimitive)
        cytoplasm.coherence_prior = math.nan

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_infinite_dt(self) -> None:
        seed = _build_valid_seed()
        seed.constitutive_profile.dt = math.inf

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_keeps_unknown_extension_namespaces_permissive(
        self,
    ) -> None:
        seed = _build_valid_seed()
        seed.extensions["unknown_namespace"] = {"ok": True}

        validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_unknown_basin_boundary_id(self) -> None:
        seed = _build_valid_seed()
        cytoplasm = seed.primitives[0]
        assert isinstance(cytoplasm, BasinSeedPrimitive)
        cytoplasm.boundary_ids = ["missing_boundary"]

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_unknown_plateau_hosted_primitive_id(
        self,
    ) -> None:
        seed = _build_valid_seed()
        seed.primitives.append(
            PlateauSeedPrimitive(
                id="plateau",
                parent_id="cytoplasm",
                depth_hint=1,
                hosted_primitive_ids=["missing_host"],
            )
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_rejects_truly_floating_hostless_junction(self) -> None:
        seed = _build_valid_seed()
        seed.primitives.append(
            JunctionSeedPrimitive(
                id="floating",
                type=PRIMITIVE_SADDLE,
                branch_target_ids=[],
            )
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            validate_landscape_seed(seed)

    def test_validate_landscape_seed_accepts_hostless_junction_with_branch_targets(self) -> None:
        seed = _build_valid_seed()
        seed.primitives.append(
            JunctionSeedPrimitive(
                id="hostless",
                type=PRIMITIVE_SADDLE,
                branch_target_ids=["cytoplasm", "nucleus"],
            )
        )

        validate_landscape_seed(seed)
