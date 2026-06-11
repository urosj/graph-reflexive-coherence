"""Policy tests for the baseline GRCV2 landscape realization blueprint."""

from __future__ import annotations

from pathlib import Path
import unittest

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_SADDLE,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    ValleySeedPrimitive,
)
from pygrc.models import realize_grcv2_landscape_blueprint


_ROOT = Path(__file__).resolve().parents[2]
_CELL1_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-1.seed.yaml"
_CELL4_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-4.seed.yaml"


def _minimal_seed(*, primitives: list[object]) -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="test", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="double_well"),
        ),
        primitives=list(primitives),  # type: ignore[list-item]
    )


class GRCV2LandscapeBlueprintTest(unittest.TestCase):
    """Validate the deterministic primitive-to-topology blueprint policy."""

    def test_cell1_realization_keeps_root_boundary_ridge_as_explicit_metadata_only_marker(
        self,
    ) -> None:
        blueprint = realize_grcv2_landscape_blueprint(_CELL1_SEED)

        self.assertEqual(("cytoplasm", "nucleus"), blueprint.node_primitive_ids)
        self.assertEqual(("nuclear_envelope",), blueprint.edge_primitive_ids)
        self.assertEqual(("plasma_membrane",), blueprint.ridge_ids_by_owner["cytoplasm"])
        self.assertEqual(("nuclear_envelope",), blueprint.ridge_ids_by_owner["nucleus"])
        self.assertEqual(("plasma_membrane",), blueprint.metadata_only_ridge_ids)

    def test_cell4_realization_uses_valleys_as_edges_and_routing_hub_as_node(self) -> None:
        blueprint = realize_grcv2_landscape_blueprint(_CELL4_SEED)

        self.assertEqual(
            (
                "cytoplasm",
                "nucleus",
                "mitochondrion_1",
                "mitochondrion_2",
                "mitochondrion_3",
                "routing_junction",
            ),
            blueprint.node_primitive_ids,
        )
        self.assertEqual(
            (
                "nuclear_envelope",
                "mito_membrane_1",
                "mito_membrane_2",
                "mito_membrane_3",
                "routing_junction_ridge",
                "channel_nucleus_to_junction",
                "channel_junction_to_mito1",
                "channel_junction_to_mito2",
                "channel_junction_to_mito3",
            ),
            blueprint.edge_primitive_ids,
        )
        self.assertEqual(("routing_junction_ridge",), blueprint.ridge_ids_by_owner["routing_junction"])
        junction_edge = next(
            edge for edge in blueprint.edge_blueprints if edge.primitive_id == "channel_nucleus_to_junction"
        )
        self.assertEqual("nucleus", junction_edge.source_primitive_id)
        self.assertEqual("routing_junction", junction_edge.target_primitive_id)
        support_edge = next(
            edge for edge in blueprint.edge_blueprints if edge.primitive_id == "nuclear_envelope"
        )
        self.assertEqual("nucleus", support_edge.source_primitive_id)
        self.assertEqual("cytoplasm", support_edge.target_primitive_id)

    def test_plateau_is_a_node_carrier_in_baseline_grcv2_projection(self) -> None:
        seed = _minimal_seed(
            primitives=[
                PlateauSeedPrimitive(
                    id="plateau_core",
                    coherence_prior=0.5,
                    hosted_primitive_ids=[],
                )
            ]
        )

        blueprint = realize_grcv2_landscape_blueprint(seed)

        self.assertEqual(("plateau_core",), blueprint.node_primitive_ids)
        self.assertEqual((), blueprint.edge_primitive_ids)

    def test_rejects_valley_endpoint_that_is_not_a_node_carrier(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="a", coherence_prior=0.8),
                RidgeSeedPrimitive(id="ridge", owner_id="a"),
                ValleySeedPrimitive(id="bad_channel", from_id="a", to_id="ridge"),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed)

    def test_rejects_basin_boundary_reference_that_is_not_a_ridge(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="a", boundary_ids=["b"]),
                BasinSeedPrimitive(id="b"),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed)

    def test_rejects_duplicate_primitive_ids_even_when_seed_validation_is_disabled(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="dup", coherence_prior=0.4),
                BasinSeedPrimitive(id="dup", coherence_prior=0.6),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed, validate_seed=False)

    def test_rejects_unresolved_non_boundary_ridge_without_support_target(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="root", coherence_prior=1.0),
                RidgeSeedPrimitive(
                    id="floating_internal_ridge",
                    owner_id="root",
                    ridge_kind="internal",
                    thickness_hint=0.02,
                ),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed)

    def test_rejects_ridge_that_would_realize_to_duplicate_edge_blueprint_ids(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="owner", coherence_prior=1.0),
                BasinSeedPrimitive(id="left", coherence_prior=0.5),
                BasinSeedPrimitive(id="right", coherence_prior=0.5),
                RidgeSeedPrimitive(
                    id="ambiguous_ridge",
                    owner_id="owner",
                    adjacent_ids=["left", "right"],
                    ridge_kind="boundary",
                    thickness_hint=0.02,
                ),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed)

    def test_rejects_hostless_junction_without_chart_center_or_incident_valley(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="left", coherence_prior=0.5),
                BasinSeedPrimitive(id="right", coherence_prior=0.5),
                JunctionSeedPrimitive(
                    id="floating_junction",
                    type=PRIMITIVE_SADDLE,
                    branch_target_ids=["left", "right"],
                ),
            ]
        )

        with self.assertRaises(InvalidLandscapeSeedError):
            realize_grcv2_landscape_blueprint(seed)

    def test_accepts_hostless_junction_with_chart_center_as_standalone_routing_site(self) -> None:
        seed = _minimal_seed(
            primitives=[
                BasinSeedPrimitive(id="left", coherence_prior=0.5),
                BasinSeedPrimitive(id="right", coherence_prior=0.5),
                JunctionSeedPrimitive(
                    id="standalone_junction",
                    type=PRIMITIVE_SADDLE,
                    branch_target_ids=["left", "right"],
                    coherence_prior=0.2,
                    chart_center_hint=[0.5, 0.5],
                ),
            ]
        )

        blueprint = realize_grcv2_landscape_blueprint(seed)

        self.assertEqual(("left", "right", "standalone_junction"), blueprint.node_primitive_ids)
