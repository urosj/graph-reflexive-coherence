"""Tests for the typed `GRCL-v3` extension boundaries."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    PRIMITIVE_SADDLE,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    ValleySeedPrimitive,
    load_landscape_seed,
)
from pygrc.landscapes.extensions.grcv3 import (
    GRCV3_RICH_V1_CONTRACT_VERSION,
    GRCV3_RICH_V2_CONTRACT_VERSION,
    GRCV3_RICH_V3_CONTRACT_VERSION,
    GRCV3_RICH_V4_CONTRACT_VERSION,
    extract_grcv3_seed_extension,
)


_ROOT = Path(__file__).resolve().parents[2]
_CELL_1_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-1.seed.yaml"
_GRCV3_RICH_V2_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-basin-boundary-channel-probe.seed.yaml"
)
_GRCV3_RICH_V3_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-interior-spindle-probe.seed.yaml"
)
_GRCV3_RICH_V3_PARTITION_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-partitioned-spindle-probe.seed.yaml"
)
_GRCV3_RICH_V3_LOAD_CARRIER_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml"
)
_GRCV3_RICH_V3_WEAK_TO_STABLE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml"
)
_GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-transfer-mediation-probe.seed.yaml"
)
_GRCV3_RICH_V4_CENTER_COUPLING_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-center-coupling-probe.seed.yaml"
)
_GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-topology-probe.seed.yaml"
)
_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_OPEN_CENTER_CONTROL_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-open-center-control-probe.seed.yaml"
)
_GRCV3_RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-open-center-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml"
)
_GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-pair-mediation-probe.seed.yaml"
)
_GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml"
)
_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-settlement-regime-probe.seed.yaml"
)
_GRCV3_RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml"
)
_GRCV3_RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-settlement-regime-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml"
)
_GRCV3_RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-anchored-settlement-probe.seed.yaml"
)
_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-fan-in-probe.seed.yaml"
)
_GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-asymmetric-pair-mediation-probe.seed.yaml"
)
_GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-mediated-spill-branch-probe.seed.yaml"
)
_GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-mediated-spill-branch-single-intermediate-probe.seed.yaml"
)
_GRCV3_RICH_V4_INVALID_MEDIATION_PROBE = (
    _ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-invalid-underdetermined-mediation.seed.yaml"
)


def _build_rich_v1_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="grcv3-rich-v1", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="double_well"),
        ),
        primitives=[
            BasinSeedPrimitive(
                id="left",
                coherence_prior=1.0,
                chart_center_hint=[0.25, 0.5],
            ),
            BasinSeedPrimitive(
                id="right",
                coherence_prior=1.0,
                chart_center_hint=[0.75, 0.5],
            ),
            JunctionSeedPrimitive(
                id="routing",
                type=PRIMITIVE_SADDLE,
                host_id=None,
                branch_target_ids=["left", "right"],
                coherence_prior=0.5,
                chart_center_hint=[0.5, 0.5],
                extensions={
                    "grcv3": {
                        "realization": {
                            "kind": "junction_motif",
                            "support_count": 2,
                            "radius_scale": 0.45,
                            "branch_order": ["west", "east"],
                        },
                        "local_geometry": {
                            "frame_mode": "branch_ordered",
                            "weak_axis_role": "east",
                        },
                        "interfaces": {
                            "branch_targets": {
                                "west": "left",
                                "east": "right",
                            }
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="left_route",
                from_id="left",
                to_id="routing",
                coherence_prior=0.25,
            ),
            ValleySeedPrimitive(
                id="right_route",
                from_id="routing",
                to_id="right",
                coherence_prior=0.25,
            ),
        ],
        extensions={
            "grcv3": {
                "contract_version": GRCV3_RICH_V1_CONTRACT_VERSION,
                "rich_required": True,
            }
        },
    )


def _build_rich_v2_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="grcv3-rich-v2", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="double_well"),
        ),
        primitives=[
            BasinSeedPrimitive(
                id="left",
                coherence_prior=0.5,
                chart_center_hint=[0.2, 0.5],
            ),
            BasinSeedPrimitive(
                id="core",
                coherence_prior=1.0,
                chart_center_hint=[0.5, 0.5],
                extensions={
                    "grcv3": {
                        "local_geometry": {
                            "frame_mode": "axis_declared",
                            "axis_roles": ["north", "east", "south", "west"],
                            "weak_axis_role": "east",
                            "symmetry_class": "cross",
                            "center_role": "interior_probe",
                        },
                        "curvature_intent": {
                            "class": "near_degenerate",
                            "stable_axis_roles": ["north", "south"],
                            "weak_axis_role": "east",
                            "ordering": "weak << stable",
                        },
                        "interfaces": {
                            "boundary_roles": ["membrane_arc"],
                            "channel_roles": ["inlet", "outlet"],
                            "preferred_attachment_sites": {
                                "membrane_arc": "north",
                                "inlet": "west",
                                "outlet": "east",
                            },
                        },
                    }
                },
            ),
            BasinSeedPrimitive(
                id="right",
                coherence_prior=0.5,
                chart_center_hint=[0.8, 0.5],
            ),
            BasinSeedPrimitive(
                id="outside",
                coherence_prior=0.2,
                chart_center_hint=[0.5, 0.8],
            ),
            RidgeSeedPrimitive(
                id="membrane",
                owner_id="core",
                adjacent_ids=["outside"],
                thickness_hint=0.03,
                extensions={
                    "grcv3": {
                        "boundary_geometry": {
                            "realization_kind": "support_arc",
                            "normal_role": "north",
                            "tangent_role": "east",
                            "arc_span": 0.4,
                            "support_distribution": "uniform",
                        },
                        "interfaces": {
                            "boundary_roles": ["membrane_arc"],
                            "preferred_attachment_sites": {
                                "membrane_arc": "north",
                            },
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="inlet",
                from_id="left",
                to_id="core",
                coherence_prior=0.2,
                extensions={
                    "grcv3": {
                        "channel_geometry": {
                            "realization_kind": "curved_chain",
                            "interior_count": 2,
                            "waypoint_policy": "preserve_all",
                            "entry_role": "west",
                            "exit_role": "east",
                        },
                        "interfaces": {
                            "channel_roles": ["inlet"],
                            "preferred_attachment_sites": {
                                "inlet": "west",
                            },
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="outlet",
                from_id="core",
                to_id="right",
                coherence_prior=0.2,
                extensions={
                    "grcv3": {
                        "channel_geometry": {
                            "realization_kind": "curved_chain",
                            "interior_count": 2,
                            "waypoint_policy": "midpoint_only",
                            "entry_role": "west",
                            "exit_role": "east",
                        },
                        "interfaces": {
                            "channel_roles": ["outlet"],
                            "preferred_attachment_sites": {
                                "outlet": "east",
                            },
                        },
                    }
                },
            ),
        ],
        extensions={
            "grcv3": {
                "contract_version": GRCV3_RICH_V2_CONTRACT_VERSION,
                "rich_required": True,
            }
        },
    )


def _build_rich_v3_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="grcv3-rich-v3", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.5,
            zeta_c=0.8,
            kappa_c=1.0,
            dt=0.001,
            potential=SeedPotential(type="double_well"),
        ),
        primitives=[
            BasinSeedPrimitive(
                id="left_reservoir",
                coherence_prior=0.5,
                chart_center_hint=[0.18, 0.5],
            ),
            BasinSeedPrimitive(
                id="core",
                coherence_prior=0.8,
                chart_center_hint=[0.5, 0.5],
                extensions={
                    "grcv3": {
                        "local_geometry": {
                            "frame_mode": "axis_declared",
                            "axis_roles": ["north", "east", "south", "west"],
                            "weak_axis_role": "east",
                            "symmetry_class": "bilateral",
                            "center_role": "interior_probe",
                        },
                        "curvature_intent": {
                            "class": "near_degenerate",
                            "stable_axis_roles": ["north", "south"],
                            "weak_axis_role": "east",
                            "ordering": "weak << stable",
                        },
                        "interfaces": {
                            "boundary_roles": ["clamp_north", "clamp_south"],
                            "channel_roles": ["inlet", "outlet"],
                            "preferred_attachment_sites": {
                                "clamp_north": "north",
                                "clamp_south": "south",
                                "inlet": "west",
                                "outlet": "east",
                            },
                        },
                        "interior_geometry": {
                            "probe_mode": "interior_candidate",
                            "support_profile": {
                                "north": "tight",
                                "east": "loose",
                                "south": "tight",
                                "west": "loose",
                            },
                            "attachment_isolation": "support_only",
                            "interior_clearance_class": "shielded",
                            "support_connectivity": "spindle",
                            "support_role_groups": {
                                "stable": ["north", "south"],
                                "weak": ["east", "west"],
                            },
                        },
                    }
                },
            ),
            BasinSeedPrimitive(
                id="right_reservoir",
                coherence_prior=0.5,
                chart_center_hint=[0.82, 0.5],
            ),
            RidgeSeedPrimitive(
                id="upper_clamp",
                owner_id="core",
                adjacent_ids=["right_reservoir"],
                thickness_hint=0.03,
                extensions={
                    "grcv3": {
                        "boundary_geometry": {
                            "realization_kind": "support_arc",
                            "normal_role": "north",
                            "tangent_role": "east",
                            "arc_span": "tight",
                            "support_distribution": "uniform",
                        },
                        "interfaces": {
                            "boundary_roles": ["clamp_north"],
                            "preferred_attachment_sites": {
                                "clamp_north": "north",
                            },
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="left_inlet",
                from_id="left_reservoir",
                to_id="core",
                coherence_prior=0.2,
                extensions={
                    "grcv3": {
                        "channel_geometry": {
                            "realization_kind": "single_channel",
                            "interior_count": 1,
                            "waypoint_policy": "midpoint_only",
                            "entry_role": "east",
                            "exit_role": "west",
                        },
                        "interfaces": {
                            "channel_roles": ["inlet"],
                            "preferred_attachment_sites": {
                                "inlet": "west",
                            },
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="right_outlet",
                from_id="core",
                to_id="right_reservoir",
                coherence_prior=0.2,
                extensions={
                    "grcv3": {
                        "channel_geometry": {
                            "realization_kind": "single_channel",
                            "interior_count": 1,
                            "waypoint_policy": "midpoint_only",
                            "entry_role": "east",
                            "exit_role": "west",
                        },
                        "interfaces": {
                            "channel_roles": ["outlet"],
                            "preferred_attachment_sites": {
                                "outlet": "east",
                            },
                        },
                    }
                },
            ),
        ],
        extensions={
            "grcv3": {
                "contract_version": GRCV3_RICH_V3_CONTRACT_VERSION,
                "rich_required": True,
            }
        },
    )


def _build_rich_v3_partition_seed() -> LandscapeSeed:
    seed = _build_rich_v3_seed()
    core = seed.primitives[1]
    assert isinstance(core, BasinSeedPrimitive)
    core.extensions["grcv3"]["interior_partition"] = {
        "partition_mode": "two_tier_probe_shell",
        "load_role_groups": {
            "clamp": ["north", "south"],
            "transport": ["east", "west"],
        },
        "load_transfer_mode": "support_mediated",
        "probe_protection_class": "shielded",
        "attachment_transfer_roles": ["north", "south", "east", "west"],
    }
    return seed


def _build_rich_v3_load_carrier_seed() -> LandscapeSeed:
    seed = _build_rich_v3_partition_seed()
    core = seed.primitives[1]
    assert isinstance(core, BasinSeedPrimitive)
    core.extensions["grcv3"]["interior_load_carriers"] = {
        "carrier_layout_mode": "group_midpoints",
        "carrier_anchor_policy": "group_centroid",
        "transfer_topology_mode": "group_bridge",
        "transfer_role_pairs": [
            ["north", "north"],
            ["south", "south"],
            ["east", "east"],
            ["west", "west"],
        ],
        "carrier_attachment_roles": ["north", "south", "east", "west"],
    }
    return seed


def _build_rich_v4_seed() -> LandscapeSeed:
    seed = _build_rich_v3_load_carrier_seed()
    seed.extensions["grcv3"] = {
        "contract_version": GRCV3_RICH_V4_CONTRACT_VERSION,
        "rich_required": True,
    }
    core = seed.primitives[1]
    assert isinstance(core, BasinSeedPrimitive)
    core.extensions["grcv3"]["interior_load_carriers"]["transfer_topology_mode"] = (
        "paired_role_bridge"
    )
    core.extensions["grcv3"]["interior_load_carriers"]["transfer_role_pairs"] = [
        ["north", "north"],
        ["south", "south"],
        ["east", "north"],
        ["west", "south"],
    ]
    core.extensions["grcv3"]["transfer_mediation"] = {
        "mediation_mode": "guarded_pairs",
        "pair_mediation_classes": [
            ["north", "north", "medium"],
            ["south", "south", "medium"],
            ["east", "north", "weak"],
            ["west", "south", "weak"],
        ],
        "probe_guard_class": "guarded_center",
        "lateral_spill_policy": "axis_locked",
    }
    return seed


def _build_rich_v4_path_topology_seed() -> LandscapeSeed:
    seed = _build_rich_v4_seed()
    core = seed.primitives[1]
    assert isinstance(core, BasinSeedPrimitive)
    core.extensions["grcv3"]["transfer_mediation"]["path_topology"] = [
        ["north", "north", "fan_in"],
        ["south", "south", "fan_in"],
        ["east", "north", "fan_in"],
        ["west", "south", "fan_in"],
    ]
    return seed


def _build_rich_v4_single_intermediate_seed() -> LandscapeSeed:
    seed = _build_rich_v4_seed()
    core = seed.primitives[1]
    assert isinstance(core, BasinSeedPrimitive)
    core.extensions["grcv3"]["transfer_mediation"]["path_topology"] = [
        ["north", "north", "single_intermediate"],
        ["south", "south", "single_intermediate"],
        ["east", "north", "single_intermediate"],
        ["west", "south", "single_intermediate"],
    ]
    return seed


class GRCV3ExtensionTest(unittest.TestCase):
    """Validate typed extraction and rejection behavior for v1 and v2."""

    def test_extract_supported_rich_v1_seed_extension(self) -> None:
        seed = _build_rich_v1_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V1_CONTRACT_VERSION, extension.contract_version)
        self.assertTrue(extension.rich_required)
        primitive_extension = extension.primitive_extensions["routing"]
        assert primitive_extension.realization is not None
        assert primitive_extension.local_geometry is not None
        assert primitive_extension.interfaces is not None
        self.assertEqual("junction_motif", primitive_extension.realization.kind)
        self.assertEqual(("west", "east"), primitive_extension.realization.branch_order)
        self.assertEqual("east", primitive_extension.local_geometry.weak_axis_role)
        self.assertEqual("left", primitive_extension.interfaces.branch_targets["west"])

    def test_extract_supported_rich_v2_seed_extension(self) -> None:
        seed = _build_rich_v2_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V2_CONTRACT_VERSION, extension.contract_version)
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.local_geometry is not None
        assert core_extension.curvature_intent is not None
        assert core_extension.interfaces is not None
        self.assertEqual(
            ("north", "east", "south", "west"),
            core_extension.local_geometry.axis_roles,
        )
        self.assertEqual("cross", core_extension.local_geometry.symmetry_class)
        self.assertEqual(
            ("north", "south"),
            core_extension.curvature_intent.stable_axis_roles,
        )
        self.assertEqual(
            "north",
            core_extension.interfaces.preferred_attachment_sites["membrane_arc"],
        )

        membrane_extension = extension.primitive_extensions["membrane"]
        assert membrane_extension.boundary_geometry is not None
        self.assertEqual(
            "support_arc",
            membrane_extension.boundary_geometry.realization_kind,
        )

        inlet_extension = extension.primitive_extensions["inlet"]
        assert inlet_extension.channel_geometry is not None
        self.assertEqual(2, inlet_extension.channel_geometry.interior_count)
        self.assertEqual(
            "preserve_all",
            inlet_extension.channel_geometry.waypoint_policy,
        )

    def test_unknown_contract_is_ignored_when_not_required(self) -> None:
        seed = _build_rich_v1_seed()
        seed.extensions["grcv3"] = {
            "contract_version": "future.contract",
            "rich_required": False,
        }

        self.assertIsNone(extract_grcv3_seed_extension(seed))

    def test_unknown_contract_is_rejected_when_required(self) -> None:
        seed = _build_rich_v1_seed()
        seed.extensions["grcv3"] = {
            "contract_version": "future.contract",
            "rich_required": True,
        }

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_extract_supported_rich_v3_seed_extension(self) -> None:
        seed = _build_rich_v3_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V3_CONTRACT_VERSION, extension.contract_version)
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.interior_geometry is not None
        self.assertEqual(
            "interior_candidate",
            core_extension.interior_geometry.probe_mode,
        )
        self.assertEqual(
            "tight",
            core_extension.interior_geometry.support_profile["north"],
        )
        self.assertEqual(
            ("north", "south"),
            core_extension.interior_geometry.support_role_groups["stable"],
        )
        self.assertEqual(
            "support_only",
            core_extension.interior_geometry.attachment_isolation,
        )

    def test_extract_supported_rich_v3_partition_seed_extension(self) -> None:
        seed = _build_rich_v3_partition_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.interior_partition is not None
        self.assertEqual(
            "two_tier_probe_shell",
            core_extension.interior_partition.partition_mode,
        )
        self.assertEqual(
            ("north", "south"),
            core_extension.interior_partition.load_role_groups["clamp"],
        )
        self.assertEqual(
            "shielded",
            core_extension.interior_partition.probe_protection_class,
        )
        self.assertEqual(
            ("north", "south", "east", "west"),
            core_extension.interior_partition.attachment_transfer_roles,
        )

    def test_extract_supported_rich_v3_load_carrier_seed_extension(self) -> None:
        seed = _build_rich_v3_load_carrier_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.interior_load_carriers is not None
        self.assertEqual(
            "group_midpoints",
            core_extension.interior_load_carriers.carrier_layout_mode,
        )
        self.assertEqual(
            "group_centroid",
            core_extension.interior_load_carriers.carrier_anchor_policy,
        )
        self.assertEqual(
            "group_bridge",
            core_extension.interior_load_carriers.transfer_topology_mode,
        )
        self.assertEqual(
            (("north", "north"), ("south", "south"), ("east", "east"), ("west", "west")),
            core_extension.interior_load_carriers.transfer_role_pairs,
        )
        self.assertEqual(
            ("north", "south", "east", "west"),
            core_extension.interior_load_carriers.carrier_attachment_roles,
        )

    def test_extract_supported_rich_v4_seed_extension(self) -> None:
        seed = _build_rich_v4_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V4_CONTRACT_VERSION, extension.contract_version)
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "guarded_pairs",
            core_extension.transfer_mediation.mediation_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "medium"),
                ("south", "south", "medium"),
                ("east", "north", "weak"),
                ("west", "south", "weak"),
            ),
            core_extension.transfer_mediation.pair_mediation_classes,
        )
        self.assertEqual(
            "guarded_center",
            core_extension.transfer_mediation.probe_guard_class,
        )
        self.assertEqual(
            "axis_locked",
            core_extension.transfer_mediation.lateral_spill_policy,
        )
        self.assertEqual((), core_extension.transfer_mediation.center_coupling_classes)

    def test_extract_supported_rich_v4_center_coupling_probe_extension(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_CENTER_COUPLING_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (("north", "blocked"), ("south", "blocked")),
            core_extension.transfer_mediation.center_coupling_classes,
        )

    def test_extract_supported_rich_v4_path_topology_probe_extension(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "fan_in"),
                ("south", "south", "fan_in"),
                ("east", "north", "fan_in"),
                ("west", "south", "fan_in"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_single_intermediate_probe_extension(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_open_center_control_probe_extension(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_OPEN_CENTER_CONTROL_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "attenuated_pairs",
            core_extension.transfer_mediation.mediation_mode,
        )
        self.assertEqual(
            "open_center",
            core_extension.transfer_mediation.probe_guard_class,
        )
        self.assertEqual((), core_extension.transfer_mediation.path_topology)

    def test_extract_supported_rich_v4_open_center_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "attenuated_pairs",
            core_extension.transfer_mediation.mediation_mode,
        )
        self.assertEqual(
            "open_center",
            core_extension.transfer_mediation.probe_guard_class,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_asymmetric_center_coupling_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (("north", "strong"), ("south", "weak")),
            core_extension.transfer_mediation.center_coupling_classes,
        )

    def test_extract_supported_rich_v4_asymmetric_center_coupling_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (("north", "strong"), ("south", "weak")),
            core_extension.transfer_mediation.center_coupling_classes,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_asymmetric_pair_mediation_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "strong"),
                ("south", "south", "blocked"),
                ("east", "north", "weak"),
                ("west", "south", "blocked"),
            ),
            core_extension.transfer_mediation.pair_mediation_classes,
        )
        self.assertEqual(
            (("north", "strong"), ("south", "weak")),
            core_extension.transfer_mediation.center_coupling_classes,
        )

    def test_extract_supported_rich_v4_asymmetric_pair_mediation_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "strong"),
                ("south", "south", "blocked"),
                ("east", "north", "weak"),
                ("west", "south", "blocked"),
            ),
            core_extension.transfer_mediation.pair_mediation_classes,
        )
        self.assertEqual(
            (("north", "strong"), ("south", "weak")),
            core_extension.transfer_mediation.center_coupling_classes,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_mediated_spill_branch_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "mediated_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "strong"),
                ("south", "south", "blocked"),
                ("east", "north", "weak"),
                ("west", "south", "blocked"),
            ),
            core_extension.transfer_mediation.pair_mediation_classes,
        )

    def test_extract_supported_rich_v4_mediated_spill_branch_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "mediated_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_carrier_site_settlement_regime_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.settlement_regime is not None
        self.assertEqual(
            "carrier_site_regime",
            core_extension.settlement_regime.regime_class,
        )

    def test_extract_supported_rich_v4_carrier_site_split_child_inheriting_settlement_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.settlement_regime is not None
        self.assertIsNone(core_extension.settlement_regime.regime_class)
        self.assertEqual(
            "carrier_site",
            core_extension.settlement_regime.initial_locus_class,
        )
        self.assertEqual(
            "split_child_inheriting",
            core_extension.settlement_regime.split_inheritance_mode,
        )

    def test_extract_supported_rich_v4_path_node_settlement_regime_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.settlement_regime is not None
        self.assertEqual(
            "path_node_regime",
            core_extension.settlement_regime.regime_class,
        )
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_path_node_split_child_inheriting_settlement_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.settlement_regime is not None
        self.assertIsNone(core_extension.settlement_regime.regime_class)
        self.assertEqual(
            "path_node",
            core_extension.settlement_regime.initial_locus_class,
        )
        self.assertEqual(
            "split_child_inheriting",
            core_extension.settlement_regime.split_inheritance_mode,
        )

    def test_extract_supported_rich_v4_path_node_anchored_settlement_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.settlement_regime is not None
        self.assertIsNone(core_extension.settlement_regime.regime_class)
        self.assertEqual(
            "path_node",
            core_extension.settlement_regime.initial_locus_class,
        )
        self.assertEqual(
            "anchored",
            core_extension.settlement_regime.split_inheritance_mode,
        )

    def test_extract_supported_rich_v4_mediated_spill_branch_fan_in_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "mediated_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "fan_in"),
                ("south", "south", "fan_in"),
                ("east", "north", "fan_in"),
                ("west", "south", "fan_in"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_role_locked_asymmetric_pair_mediation_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "role_locked",
            core_extension.transfer_mediation.lateral_spill_policy,
        )
        self.assertEqual(
            "carrier_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )

    def test_extract_supported_rich_v4_role_locked_asymmetric_pair_mediation_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "role_locked",
            core_extension.transfer_mediation.lateral_spill_policy,
        )
        self.assertEqual(
            "carrier_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_extract_supported_rich_v4_role_locked_mediated_spill_branch_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "role_locked",
            core_extension.transfer_mediation.lateral_spill_policy,
        )
        self.assertEqual(
            "mediated_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )

    def test_extract_supported_rich_v4_role_locked_mediated_spill_branch_single_intermediate_probe_extension(
        self,
    ) -> None:
        seed = load_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE
        )

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["spindle_core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            "role_locked",
            core_extension.transfer_mediation.lateral_spill_policy,
        )
        self.assertEqual(
            "mediated_branch",
            core_extension.transfer_mediation.spill_branch_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_invalid_weak_axis_role_is_rejected_in_v1(self) -> None:
        seed = _build_rich_v1_seed()
        junction = seed.primitives[2]
        assert isinstance(junction, JunctionSeedPrimitive)
        junction.extensions["grcv3"]["local_geometry"]["weak_axis_role"] = "north"

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_support_profile_must_cover_role_universe(self) -> None:
        seed = _build_rich_v3_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        del core.extensions["grcv3"]["interior_geometry"]["support_profile"]["west"]

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_probe_mode_must_match_center_role(self) -> None:
        seed = _build_rich_v3_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["local_geometry"]["center_role"] = "anchor"

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_support_role_groups_must_not_overlap(self) -> None:
        seed = _build_rich_v3_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interior_geometry"]["support_role_groups"] = {
            "stable": ["north", "south"],
            "weak": ["south", "west"],
        }

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_partition_requires_attachment_roles_to_belong_to_load_groups(self) -> None:
        seed = _build_rich_v3_partition_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interior_partition"]["load_role_groups"] = {
            "clamp": ["north", "south"],
            "transport": ["east"],
        }

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_partition_rejects_shielded_direct_open_contradiction(self) -> None:
        seed = _build_rich_v3_partition_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interior_partition"]["load_transfer_mode"] = "direct_open"

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v3_load_carriers_require_partition_before_use(self) -> None:
        seed = _build_rich_v3_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interior_load_carriers"] = {
            "carrier_layout_mode": "group_midpoints",
            "carrier_anchor_policy": "group_centroid",
            "transfer_topology_mode": "group_bridge",
            "transfer_role_pairs": [
                ["north", "north"],
                ["south", "south"],
                ["east", "east"],
                ["west", "west"],
            ],
            "carrier_attachment_roles": ["north", "south", "east", "west"],
        }

        with self.assertRaisesRegex(InvalidLandscapeSeedError, "requires interior_partition"):
            extract_grcv3_seed_extension(seed)

    def test_v3_load_carriers_reject_group_bridge_cross_group_pairs(self) -> None:
        seed = _build_rich_v3_load_carrier_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interior_load_carriers"]["transfer_role_pairs"] = [
            ["north", "east"],
            ["south", "south"],
            ["east", "west"],
            ["west", "north"],
        ]

        with self.assertRaisesRegex(InvalidLandscapeSeedError, "group_bridge"):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_requires_load_carriers_before_use(self) -> None:
        seed = _build_rich_v3_partition_seed()
        seed.extensions["grcv3"] = {
            "contract_version": GRCV3_RICH_V4_CONTRACT_VERSION,
            "rich_required": True,
        }
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"] = {
            "mediation_mode": "guarded_pairs",
            "pair_mediation_classes": [
                ["north", "north", "medium"],
                ["south", "south", "medium"],
            ],
            "probe_guard_class": "guarded_center",
            "lateral_spill_policy": "axis_locked",
        }

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "requires interior_load_carriers",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_rejects_underdetermined_pair_coverage(self) -> None:
        seed = _build_rich_v4_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"]["pair_mediation_classes"] = [
            ["north", "north", "medium"],
            ["south", "south", "medium"],
            ["east", "north", "weak"],
        ]

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "must cover exactly the declared transfer_role_pairs",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_rejects_transport_override_style_payload(self) -> None:
        seed = _build_rich_v4_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"]["constitutive_weight_override"] = {
            "north->north": 0.25
        }

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "includes unsupported keys",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v2_invalid_stable_axis_role_is_rejected(self) -> None:
        seed = _build_rich_v2_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["curvature_intent"]["stable_axis_roles"] = [
            "north",
            "diagonal",
        ]

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_rejects_center_coupling_role_outside_probe_roles(self) -> None:
        seed = _build_rich_v4_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"]["center_coupling_classes"] = [
            ["east", "blocked"],
        ]

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_rejects_partial_path_topology_coverage(self) -> None:
        seed = _build_rich_v4_path_topology_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"]["path_topology"] = [
            ["north", "north", "fan_in"],
            ["south", "south", "fan_in"],
        ]

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "must cover exactly the declared transfer_role_pairs",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_rejects_partial_fan_in_group(self) -> None:
        seed = _build_rich_v4_path_topology_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["transfer_mediation"]["path_topology"] = [
            ["north", "north", "fan_in"],
            ["south", "south", "fan_in"],
            ["east", "north", "direct"],
            ["west", "south", "fan_in"],
        ]

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "must assign fan_in to all declared pairs targeting that probe role",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v4_settlement_regime_rejects_path_node_regime_without_non_direct_path(
        self,
    ) -> None:
        seed = deepcopy(load_landscape_seed(_GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE))
        spindle_core = next(
            primitive for primitive in seed.primitives if primitive.id == "spindle_core"
        )
        assert isinstance(spindle_core, BasinSeedPrimitive)
        spindle_core.extensions["grcv3"]["settlement_regime"] = {
            "regime_class": "path_node_regime"
        }

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "initial_locus_class='path_node' requires at least one non-direct transfer_mediation.path_topology assignment",
        ):
            extract_grcv3_seed_extension(seed)

    def test_v4_transfer_mediation_accepts_single_intermediate_for_full_pair_coverage(self) -> None:
        seed = _build_rich_v4_single_intermediate_seed()

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        core_extension = extension.primitive_extensions["core"]
        assert core_extension.transfer_mediation is not None
        self.assertEqual(
            (
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            ),
            core_extension.transfer_mediation.path_topology,
        )

    def test_v2_invalid_preferred_attachment_site_is_rejected(self) -> None:
        seed = _build_rich_v2_seed()
        core = seed.primitives[1]
        assert isinstance(core, BasinSeedPrimitive)
        core.extensions["grcv3"]["interfaces"]["preferred_attachment_sites"][
            "membrane_arc"
        ] = "diagonal"

        with self.assertRaises(InvalidLandscapeSeedError):
            extract_grcv3_seed_extension(seed)

    def test_v2_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V2_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V2_CONTRACT_VERSION, extension.contract_version)
        self.assertIn("core_basin", extension.primitive_extensions)
        self.assertIn("upper_membrane", extension.primitive_extensions)
        self.assertIn("left_inlet", extension.primitive_extensions)

    def test_v3_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V3_CONTRACT_VERSION, extension.contract_version)
        self.assertIn("spindle_core", extension.primitive_extensions)
        spindle_extension = extension.primitive_extensions["spindle_core"]
        assert spindle_extension.interior_geometry is not None
        self.assertEqual(
            "spindle",
            spindle_extension.interior_geometry.support_connectivity,
        )

    def test_v3_partition_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_PARTITION_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        spindle_extension = extension.primitive_extensions["spindle_core"]
        assert spindle_extension.interior_partition is not None
        self.assertEqual(
            "two_tier_probe_shell",
            spindle_extension.interior_partition.partition_mode,
        )
        self.assertEqual(
            "support_mediated",
            spindle_extension.interior_partition.load_transfer_mode,
        )

    def test_v3_load_carrier_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_LOAD_CARRIER_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        spindle_extension = extension.primitive_extensions["spindle_core"]
        assert spindle_extension.interior_load_carriers is not None
        self.assertEqual(
            "group_midpoints",
            spindle_extension.interior_load_carriers.carrier_layout_mode,
        )
        self.assertEqual(
            "group_centroid",
            spindle_extension.interior_load_carriers.carrier_anchor_policy,
        )
        self.assertEqual(
            "group_bridge",
            spindle_extension.interior_load_carriers.transfer_topology_mode,
        )

    def test_v3_weak_to_stable_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_WEAK_TO_STABLE_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        spindle_extension = extension.primitive_extensions["spindle_core"]
        assert spindle_extension.interior_load_carriers is not None
        self.assertEqual(
            "paired_role_bridge",
            spindle_extension.interior_load_carriers.transfer_topology_mode,
        )
        self.assertEqual(
            (
                ("north", "north"),
                ("south", "south"),
                ("east", "north"),
                ("west", "south"),
            ),
            spindle_extension.interior_load_carriers.transfer_role_pairs,
        )

    def test_v4_yaml_fixture_parses_deterministically(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE)

        extension = extract_grcv3_seed_extension(seed)

        self.assertIsNotNone(extension)
        assert extension is not None
        self.assertEqual(GRCV3_RICH_V4_CONTRACT_VERSION, extension.contract_version)
        spindle_extension = extension.primitive_extensions["spindle_core"]
        assert spindle_extension.transfer_mediation is not None
        self.assertEqual(
            "guarded_pairs",
            spindle_extension.transfer_mediation.mediation_mode,
        )
        self.assertEqual(
            (
                ("north", "north", "medium"),
                ("south", "south", "medium"),
                ("east", "north", "weak"),
                ("west", "south", "weak"),
            ),
            spindle_extension.transfer_mediation.pair_mediation_classes,
        )

    def test_v4_invalid_yaml_fixture_fails_explicitly(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_INVALID_MEDIATION_PROBE)

        with self.assertRaisesRegex(
            InvalidLandscapeSeedError,
            "must cover exactly the declared transfer_role_pairs",
        ):
            extract_grcv3_seed_extension(seed)

    def test_common_seed_without_grcv3_extension_remains_backward_compatible(self) -> None:
        seed = load_landscape_seed(_CELL_1_SEED)

        self.assertIsNone(extract_grcv3_seed_extension(seed))


if __name__ == "__main__":
    unittest.main()
