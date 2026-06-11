"""Runtime tests for seed-driven GRCV3 landscape construction and execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from pygrc.core import (
    InvalidLandscapeSeedError,
    build_backend_selection,
    build_backend_selection_payload,
    digest_snapshot,
)
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    load_landscape_seed,
    PlateauSeedPrimitive,
    PRIMITIVE_SADDLE,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    ValleySeedPrimitive,
)
from pygrc.models import (
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    build_grcv3_from_landscape_seed,
    project_landscape_seed_to_grcv3_state,
    resolve_grcv3_landscape_params,
    run_grcv3_landscape_seed,
)
from pygrc.models import grc_v3_landscape as grc_v3_landscape_module
from pygrc.models.grc_v3_differential import symmetric_eigenvalues


_ROOT = Path(__file__).resolve().parents[2]
_CELL1_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-1.seed.yaml"
_CELL4_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-4.seed.yaml"
_GRCV3_RICH_JUNCTION_PROBE = (
    _ROOT / "configs" / "landscapes" / "seed" / "grcv3-rich-junction-probe.seed.yaml"
)
_GRCV3_RICH_COLLAPSE_EXAMPLE = (
    _ROOT / "configs" / "landscapes" / "seed" / "grcv3-rich-collapse-example.seed.yaml"
)
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


def _event_counts(run) -> dict[str, int]:
    counts: dict[str, int] = {}
    for step in run.step_results:
        for event in step.events:
            counts[event.kind] = counts.get(event.kind, 0) + 1
    return counts


def _hostless_junction_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="hostless-junction", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            budget_b=5.0,
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
    )


def _default_radius_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="default-radius", source_kind="unit"),
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
                id="seed_a",
                coherence_prior=1.0,
                chart_center_hint=[0.0, 0.0],
            ),
            BasinSeedPrimitive(
                id="seed_b",
                coherence_prior=1.0,
                chart_center_hint=[1.0, 0.0],
            ),
            ValleySeedPrimitive(
                id="bridge",
                from_id="seed_a",
                to_id="seed_b",
                coherence_prior=0.1,
            ),
        ],
    )


def _grcv3_rich_v2_junction_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="grcv3-rich-v2-junction", source_kind="unit"),
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
                chart_center_hint=[0.3, 0.5],
                chart_scale_hint={"radius": 0.08},
            ),
            BasinSeedPrimitive(
                id="right",
                coherence_prior=1.0,
                chart_center_hint=[0.7, 0.5],
                chart_scale_hint={"radius": 0.08},
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
                            "radius_scale": 0.5,
                            "branch_order": ["west", "east"],
                        },
                        "local_geometry": {
                            "frame_mode": "branch_ordered",
                            "weak_axis_role": "east",
                        },
                        "curvature_intent": {
                            "class": "near_degenerate",
                            "stable_axis_roles": ["west"],
                            "weak_axis_role": "east",
                            "ordering": "weak << stable",
                        },
                        "interfaces": {
                            "branch_targets": {"west": "left", "east": "right"},
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="left_route",
                from_id="left",
                to_id="routing",
                coherence_prior=0.2,
                waypoints=[[0.4, 0.5]],
            ),
            ValleySeedPrimitive(
                id="right_route",
                from_id="routing",
                to_id="right",
                coherence_prior=0.2,
                waypoints=[[0.6, 0.5]],
            ),
        ],
        extensions={"grcv3": {"contract_version": "grcv3.rich.v2", "rich_required": True}},
    )


def _grcv3_rich_v2_plateau_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="grcv3-rich-v2-plateau", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="double_well"),
        ),
        primitives=[
            PlateauSeedPrimitive(
                id="platform",
                coherence_prior=0.8,
                chart_center_hint=[0.5, 0.5],
                chart_scale_hint={"radius": 0.18},
                hosted_primitive_ids=["core"],
                extensions={
                    "grcv3": {
                        "local_geometry": {
                            "frame_mode": "axis_declared",
                            "axis_roles": ["north", "east", "south", "west"],
                            "weak_axis_role": "east",
                            "symmetry_class": "cross",
                            "center_role": "anchor",
                        },
                        "curvature_intent": {
                            "class": "stable_interior",
                            "stable_axis_roles": ["north", "south"],
                            "weak_axis_role": "east",
                            "ordering": "weak << stable",
                        },
                    }
                },
            ),
            BasinSeedPrimitive(
                id="core",
                parent_id="platform",
                coherence_prior=1.0,
                chart_center_hint=[0.5, 0.5],
                chart_scale_hint={"radius": 0.07},
            ),
            RidgeSeedPrimitive(
                id="cap",
                owner_id="platform",
                adjacent_ids=["core"],
                ridge_kind="boundary",
                thickness_hint=0.02,
                interior_coherence_hint=0.8,
                exterior_coherence_hint=0.4,
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
                            "preferred_attachment_sites": {"membrane_arc": "north"},
                        },
                    }
                },
            ),
        ],
        extensions={"grcv3": {"contract_version": "grcv3.rich.v2", "rich_required": True}},
    )


class GRCV3LandscapeRuntimeTest(unittest.TestCase):
    """Validate the seed-driven GRCV3 landscape bridge on real cells."""

    def test_rich_collapse_example_enters_choice_and_collapses(self) -> None:
        result = run_grcv3_landscape_seed(
            _GRCV3_RICH_COLLAPSE_EXAMPLE,
            profile_name="hot_exploratory",
            overrides={
                "constitutive_semantic_modes": {
                    "backend_selections": build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="choice",
                                name="sink_compatibility",
                                params={
                                    "epsilon_choice": 0.15,
                                    "epsilon_collapse": 0.14,
                                },
                            )
                        ]
                    )
                }
            },
            num_steps=3,
        )

        unique_events: set[tuple[int, str, str | int | None]] = set()
        for step in result.step_results:
            for event in step.events:
                payload = dict(event.payload)
                unique_events.add((step.step_index, event.kind, payload.get("node_id")))

        self.assertIn((1, "choice_detected", 10), unique_events)
        self.assertIn((1, "choice_detected", 15), unique_events)
        self.assertIn((3, "collapse", 10), unique_events)
        self.assertIn((3, "collapse", 15), unique_events)

        state = result.model.get_state()
        collapse_registry = state.collapse_registry
        self.assertEqual(2, len(collapse_registry))
        self.assertEqual("17", collapse_registry["10"]["collapsed_sink_id"])
        self.assertEqual("19", collapse_registry["15"]["collapsed_sink_id"])
        self.assertEqual("registry_only", collapse_registry["10"]["persistence_mode"])
        self.assertEqual("registry_only", collapse_registry["15"]["persistence_mode"])
        self.assertEqual(2, collapse_registry["10"]["collapsed_step_index"])
        self.assertEqual(2, collapse_registry["15"]["collapsed_step_index"])

    def test_projected_state_for_cell1_has_budget_and_semantic_basin_ids(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL1_SEED)
        state = project_landscape_seed_to_grcv3_state(_CELL1_SEED, params=params)

        self.assertEqual(10, len(tuple(state.topology.iter_live_node_ids())))
        self.assertEqual(15, len(tuple(state.topology.iter_live_edge_ids())))
        self.assertAlmostEqual(
            sum(attributes.coherence for attributes in state.nodes.values()),
            state.budget_target,
        )
        basin_ids = {attributes.basin_id for attributes in state.nodes.values() if attributes.coherence > 0.0}
        self.assertEqual({"cytoplasm", "nucleus"}, basin_ids)
        self.assertEqual(
            {"cytoplasm": 4, "nuclear_envelope": 2, "nucleus": 4},
            {
                primitive_id: len(node_ids)
                for primitive_id, node_ids in state.cached_quantities[
                    "landscape_node_ids_by_primitive_id"
                ].items()
            },
        )
        self.assertEqual(
            ["plasma_membrane"],
            state.cached_quantities["landscape_metadata_only_ridge_ids"],
        )
        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_v2",
            state.cached_quantities["landscape_realization_mode"],
        )
        self.assertEqual([], state.cached_quantities["landscape_skipped_patch_ids"])
        self.assertNotIn(
            "plasma_membrane",
            state.cached_quantities["landscape_node_ids_by_primitive_id"],
        )
        self.assertEqual(
            {"nuclear_envelope": 2},
            {
                primitive_id: len(node_ids)
                for primitive_id, node_ids in state.cached_quantities[
                    "landscape_ridge_support_node_ids_by_primitive_id"
                ].items()
            },
        )
        self.assertEqual(
            "compatibility",
            state.cached_quantities["landscape_lowering_lane"],
        )
        self.assertEqual(
            "grcv2_blueprint",
            state.cached_quantities["landscape_lowering_semantic_authority"],
        )
        self.assertEqual(
            "authoritative_semantic_intermediate",
            state.cached_quantities["landscape_compatibility_blueprint_usage"],
        )
        self.assertIsNone(
            state.cached_quantities["landscape_grcv3_native_surface_summary"],
        )

    def test_projected_state_for_cell4_has_expected_connected_runtime_surface(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL4_SEED)
        state = project_landscape_seed_to_grcv3_state(_CELL4_SEED, params=params)

        self.assertEqual(43, len(tuple(state.topology.iter_live_node_ids())))
        self.assertEqual(61, len(tuple(state.topology.iter_live_edge_ids())))
        self.assertIn(
            "routing_junction",
            state.cached_quantities["landscape_node_id_by_primitive_id"],
        )
        self.assertEqual(
            5,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["routing_junction"]),
        )
        self.assertEqual(
            4,
            len(
                state.cached_quantities["landscape_interface_node_ids_by_primitive_id"][
                    "routing_junction"
                ]
            ),
        )
        self.assertEqual(
            2,
            len(
                state.cached_quantities["landscape_node_ids_by_primitive_id"][
                    "channel_nucleus_to_junction"
                ]
            ),
        )
        self.assertEqual(
            3,
            len(
                state.cached_quantities["landscape_edge_ids_by_primitive_id"][
                    "channel_nucleus_to_junction"
                ]
            ),
        )
        self.assertEqual(
            3,
            len(
                state.cached_quantities["landscape_edge_ids_by_primitive_id"][
                    "routing_junction_ridge"
                ]
            ),
        )
        self.assertEqual(
            2,
            len(
                state.cached_quantities["landscape_ridge_support_node_ids_by_primitive_id"][
                    "routing_junction_ridge"
                ]
            ),
        )
        self.assertEqual(DEFAULT_GRCV3_LANDSCAPE_PROFILE, state.cached_quantities["landscape_profile_name"])
        self.assertAlmostEqual(
            state.budget_target,
            sum(attributes.coherence for attributes in state.nodes.values()),
        )
        self.assertEqual([], state.cached_quantities["landscape_skipped_patch_ids"])
        self.assertEqual(
            "compatibility_blueprint",
            state.cached_quantities["landscape_runtime_assembly_mode"],
        )
        self.assertEqual(
            "grcv2_landscape_projector",
            state.cached_quantities["landscape_runtime_assembly_summary"]["carrier_source"],
        )

    def test_grcv2_aligned_profile_resolves_for_grcv3_landscape(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL4_SEED, profile_name="balanced_baseline")

        self.assertEqual(
            "balanced_baseline",
            params.numerical_backend["landscape_param_profile"],
        )
        self.assertEqual(
            "grcv2_family_envelope",
            params.numerical_backend["profile_alignment_source"],
        )
        self.assertEqual(
            "induced_local_frame",
            params.constitutive_semantic_modes["frame_mode"],
        )

    def test_runner_executes_cell1_and_cell4_for_multiple_steps(self) -> None:
        cell1_run = run_grcv3_landscape_seed(_CELL1_SEED, num_steps=3)
        cell4_run = run_grcv3_landscape_seed(_CELL4_SEED, num_steps=3)

        self.assertEqual(3, len(cell1_run.step_results))
        self.assertEqual(3, len(cell4_run.step_results))
        self.assertIsNone(cell1_run.telemetry)
        self.assertIsNone(cell4_run.telemetry)
        self.assertEqual(3, cell1_run.model.get_state().step_index)
        self.assertEqual(3, cell4_run.model.get_state().step_index)
        self.assertIn("active_basin_count", cell4_run.final_observables)
        self.assertIn("max_hierarchy_depth", cell4_run.final_observables)

    def test_invalid_profile_name_is_rejected(self) -> None:
        with self.assertRaises(InvalidLandscapeSeedError):
            resolve_grcv3_landscape_params(_CELL1_SEED, profile_name="not-a-profile")

    def test_runner_allows_zero_steps_as_initial_state_probe(self) -> None:
        run = run_grcv3_landscape_seed(_CELL1_SEED, num_steps=0)

        self.assertEqual([], run.step_results)
        self.assertEqual(run.initial_observables, run.final_observables)
        self.assertEqual(0, run.model.get_state().step_index)

    def test_projected_hostless_junction_preserves_anchor_mode_and_branch_interfaces(self) -> None:
        seed = _hostless_junction_seed()
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        routing_node_ids = state.cached_quantities["landscape_node_ids_by_primitive_id"]["routing"]
        interface_node_ids = state.cached_quantities["landscape_interface_node_ids_by_primitive_id"][
            "routing"
        ]
        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["routing"]
        anchor_payload = state.topology.node_payload(anchor_node_id)

        self.assertEqual(3, len(routing_node_ids))
        self.assertEqual(2, len(interface_node_ids))
        self.assertTrue(anchor_payload["is_hostless"])
        self.assertEqual("standalone", anchor_payload["junction_anchor_mode"])
        self.assertEqual(
            {"left_route", "right_route"},
            set(anchor_payload["metadata"]["junction_incident_valley_ids"]),
        )

    def test_projection_uses_default_radius_for_basin_support_when_scale_hint_missing(self) -> None:
        seed = _default_radius_seed()
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["seed_a"]
        support_node_ids = state.cached_quantities["landscape_support_node_ids_by_primitive_id"]["seed_a"]
        anchor_center = state.topology.node_payload(anchor_node_id)["chart_center_hint"]
        self.assertEqual((0.0, 0.0), anchor_center)
        for support_node_id in support_node_ids:
            point = state.topology.node_payload(support_node_id)["chart_center_hint"]
            distance = ((point[0] - anchor_center[0]) ** 2 + (point[1] - anchor_center[1]) ** 2) ** 0.5
            self.assertAlmostEqual(0.0225, distance, places=7)

    def test_grcv3_rich_v2_junction_seed_uses_family_native_branch_lowering(self) -> None:
        seed = _grcv3_rich_v2_junction_seed()
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v2",
            state.cached_quantities["landscape_realization_mode"],
        )
        self.assertEqual(
            {"west", "east"},
            set(state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"]["routing"]),
        )
        branch_targets = state.cached_quantities["landscape_grcv3_branch_node_ids_by_target"]["routing"]
        self.assertEqual({"left", "right"}, set(branch_targets))
        self.assertTrue(
            state.topology.node_payload(state.cached_quantities["landscape_node_id_by_primitive_id"]["routing"])[
                "is_hostless"
            ]
        )
        self.assertEqual(
            "native_runtime_blueprint",
            state.cached_quantities["landscape_runtime_assembly_mode"],
        )
        self.assertEqual(
            "native_surface_runtime_carrier",
            state.cached_quantities["landscape_runtime_assembly_summary"]["carrier_source"],
        )

    def test_grcv3_rich_v2_plateau_seed_realizes_native_axes_and_containment(self) -> None:
        seed = _grcv3_rich_v2_plateau_seed()
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            {"north", "east", "south", "west"},
            set(state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"]["platform"]),
        )
        self.assertEqual(
            5,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["platform"]),
        )
        platform_payload = state.topology.node_payload(
            state.cached_quantities["landscape_node_id_by_primitive_id"]["platform"]
        )
        self.assertEqual(["core"], platform_payload["contained_primitive_ids"])
        self.assertEqual(
            [state.cached_quantities["landscape_node_id_by_primitive_id"]["core"]],
            platform_payload["contained_node_ids"],
        )

    def test_projection_is_deterministic_for_same_seed_and_params(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL4_SEED)
        first = build_grcv3_from_landscape_seed(_CELL4_SEED, params=params)
        second = build_grcv3_from_landscape_seed(_CELL4_SEED, params=params)

        self.assertEqual(digest_snapshot(first.snapshot()), digest_snapshot(second.snapshot()))

    def test_native_lane_is_deterministic_for_same_rich_v2_seed_and_params(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V2_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        first = build_grcv3_from_landscape_seed(seed, params=params)
        second = build_grcv3_from_landscape_seed(seed, params=params)

        self.assertEqual(digest_snapshot(first.snapshot()), digest_snapshot(second.snapshot()))

    def test_family_native_lane_does_not_call_grcv2_projector(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V2_PROBE)
        params = resolve_grcv3_landscape_params(seed)

        with mock.patch(
            "pygrc.models.grc_v3_landscape.realize_grcv2_landscape_blueprint",
            side_effect=AssertionError("compatibility projector should not be used"),
        ):
            state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])

    def test_compatibility_lane_still_calls_grcv2_projector(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL1_SEED)

        with mock.patch(
            "pygrc.models.grc_v3_landscape.realize_grcv2_landscape_blueprint",
            side_effect=AssertionError("compatibility projector invoked"),
        ):
            with self.assertRaisesRegex(AssertionError, "compatibility projector invoked"):
                project_landscape_seed_to_grcv3_state(_CELL1_SEED, params=params)

    def test_projected_model_save_load_roundtrip_preserves_topology_and_replay(self) -> None:
        params = resolve_grcv3_landscape_params(_CELL4_SEED)
        model = build_grcv3_from_landscape_seed(_CELL4_SEED, params=params)
        initial_digest = digest_snapshot(model.snapshot())

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "grcv3-landscape.json"
            model.save(str(path))
            restored = model.__class__.load(str(path))

        self.assertEqual(initial_digest, digest_snapshot(restored.snapshot()))

        left = build_grcv3_from_landscape_seed(_CELL4_SEED, params=params)
        right = restored
        for _ in range(2):
            left.step()
            right.step()
        self.assertEqual(digest_snapshot(left.snapshot()), digest_snapshot(right.snapshot()))

    def test_grcv3_rich_junction_probe_is_consumed_by_typed_lowering_path(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_JUNCTION_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v1",
            state.cached_quantities["landscape_realization_mode"],
        )
        self.assertEqual(
            "grcv3.rich.v1",
            state.cached_quantities["landscape_grcv3_rich_contract_version"],
        )
        self.assertTrue(state.cached_quantities["landscape_grcv3_rich_required"])
        self.assertEqual(
            ["decision_core"],
            state.cached_quantities["landscape_grcv3_rich_primitive_ids"],
        )
        self.assertEqual(
            5,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["decision_core"]),
        )
        self.assertEqual(
            4,
            len(
                state.cached_quantities["landscape_interface_node_ids_by_primitive_id"][
                    "decision_core"
                ]
            ),
        )
        branch_targets = state.cached_quantities["landscape_grcv3_branch_node_ids_by_target"][
            "decision_core"
        ]
        self.assertEqual(
            {"left_basin", "right_basin", "upper_basin", "lower_basin"},
            set(branch_targets),
        )
        right_branch_payload = state.topology.node_payload(branch_targets["right_basin"])
        self.assertEqual(
            "east",
            right_branch_payload["metadata"]["grcv3_rich_branch_role"],
        )
        self.assertEqual(
            "east",
            right_branch_payload["metadata"]["grcv3_rich_weak_axis_role"],
        )
        self.assertEqual(
            "compatibility",
            state.cached_quantities["landscape_lowering_lane"],
        )
        self.assertEqual(
            "grcv2_blueprint",
            state.cached_quantities["landscape_lowering_semantic_authority"],
        )
        self.assertEqual(
            "authoritative_semantic_intermediate",
            state.cached_quantities["landscape_compatibility_blueprint_usage"],
        )
        self.assertIsNone(
            state.cached_quantities["landscape_grcv3_native_surface_summary"],
        )

    def test_grcv3_rich_junction_probe_uses_explicit_branch_target_attachment(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_JUNCTION_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        branch_targets = state.cached_quantities["landscape_grcv3_branch_node_ids_by_target"][
            "decision_core"
        ]
        expectations = {
            "channel_left_to_core": branch_targets["left_basin"],
            "channel_core_to_right": branch_targets["right_basin"],
            "channel_upper_to_core": branch_targets["upper_basin"],
            "channel_core_to_lower": branch_targets["lower_basin"],
        }
        for primitive_id, expected_branch_node_id in expectations.items():
            edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"][primitive_id]
            attached_to_expected_branch = False
            for edge_id in edge_ids:
                endpoints = state.topology.edge_endpoints(edge_id)
                if expected_branch_node_id in endpoints:
                    attached_to_expected_branch = True
                    break
            self.assertTrue(
                attached_to_expected_branch,
                msg=f"{primitive_id} did not attach to expected rich branch node",
            )

    def test_grcv3_rich_v2_probe_realizes_role_aware_basin_channel_and_boundary_structure(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V2_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v2",
            state.cached_quantities["landscape_realization_mode"],
        )
        self.assertEqual(
            "grcv3.rich.v2",
            state.cached_quantities["landscape_grcv3_rich_contract_version"],
        )
        role_node_ids = state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"]
        self.assertEqual(
            {"north", "east", "south", "west"},
            set(role_node_ids["core_basin"]),
        )
        self.assertEqual(
            5,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["core_basin"]),
        )
        self.assertEqual(
            4,
            len(
                state.cached_quantities["landscape_interface_node_ids_by_primitive_id"][
                    "core_basin"
                ]
            ),
        )
        self.assertEqual(
            2,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["left_inlet"]),
        )
        self.assertEqual(
            2,
            len(state.cached_quantities["landscape_node_ids_by_primitive_id"]["right_outlet"]),
        )
        self.assertEqual(
            3,
            len(
                state.cached_quantities["landscape_ridge_support_node_ids_by_primitive_id"][
                    "upper_membrane"
                ]
            ),
        )
        self.assertIn(
            "attachment roles are resolved deterministically from preferred_attachment_sites first, then family-local role labels, then geometric fallback",
            state.cached_quantities["landscape_grcv3_lowering_notes"],
        )
        self.assertEqual(
            "family_native",
            state.cached_quantities["landscape_lowering_lane"],
        )
        self.assertEqual(
            "direct_seed_primitives",
            state.cached_quantities["landscape_lowering_semantic_authority"],
        )
        self.assertEqual(
            "implementation_carrier_reuse_only",
            state.cached_quantities["landscape_compatibility_blueprint_usage"],
        )
        native_surface_summary = state.cached_quantities[
            "landscape_grcv3_native_surface_summary"
        ]
        self.assertIsNotNone(native_surface_summary)
        self.assertEqual("grcv3.rich.v2", native_surface_summary["rich_contract_version"])
        self.assertEqual(
            {"core_basin", "left_reservoir", "right_reservoir", "exterior_shell"},
            set(native_surface_summary["primitive_ids_by_type"]["basin"]),
        )
        self.assertEqual(
            ("left_inlet", "right_outlet"),
            tuple(native_surface_summary["primitive_ids_by_type"]["valley"]),
        )
        self.assertEqual(
            ("upper_membrane",),
            tuple(native_surface_summary["primitive_ids_by_type"]["ridge"]),
        )
        self.assertIn(
            "_euclidean_length",
            native_surface_summary["temporary_blueprint_utility_functions"],
        )

    def test_grcv3_rich_v2_probe_uses_preferred_attachment_roles_for_channels_and_boundary(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V2_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        role_node_ids = state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"][
            "core_basin"
        ]
        expected_left_attach = role_node_ids["west"]
        expected_right_attach = role_node_ids["east"]
        expected_boundary_attach = role_node_ids["north"]

        left_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["left_inlet"]
        right_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["right_outlet"]
        ridge_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["upper_membrane"]

        self.assertTrue(
            any(expected_left_attach in state.topology.edge_endpoints(edge_id) for edge_id in left_edge_ids)
        )
        self.assertTrue(
            any(expected_right_attach in state.topology.edge_endpoints(edge_id) for edge_id in right_edge_ids)
        )
        self.assertTrue(
            any(expected_boundary_attach in state.topology.edge_endpoints(edge_id) for edge_id in ridge_edge_ids)
        )

    def test_grcv3_rich_v3_probe_realizes_interior_geometry_and_support_only_attachment(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v3",
            state.cached_quantities["landscape_realization_mode"],
        )
        interior_summary = state.cached_quantities["landscape_grcv3_interior_geometry_summary"]
        self.assertIn("spindle_core", interior_summary)
        self.assertEqual(
            "spindle",
            interior_summary["spindle_core"]["support_connectivity"],
        )
        self.assertEqual(
            "support_only",
            interior_summary["spindle_core"]["attachment_isolation"],
        )
        self.assertEqual(
            ["spindle_core"],
            state.cached_quantities["landscape_runtime_assembly_summary"][
                "interior_geometry_primitive_ids"
            ],
        )
        self.assertIn(
            "grcv3.rich.v3 interior_geometry changes realized support spacing, spoke coupling, support-support connectivity, and center-attachment fallback policy directly in the family-native assembly path",
            state.cached_quantities["landscape_grcv3_lowering_notes"],
        )

        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["spindle_core"]
        role_node_ids = state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"][
            "spindle_core"
        ]
        center = state.topology.node_payload(anchor_node_id)["chart_center_hint"]

        def _distance(node_id: int) -> float:
            point = state.topology.node_payload(node_id)["chart_center_hint"]
            return ((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2) ** 0.5

        self.assertLess(_distance(role_node_ids["north"]), _distance(role_node_ids["east"]))
        self.assertLess(_distance(role_node_ids["south"]), _distance(role_node_ids["west"]))

        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]
        motif_edge_roles = [
            state.topology.edge_payload(edge_id)["metadata"]["motif_edge_role"]
            for edge_id in spindle_edge_ids
        ]
        self.assertEqual(4, motif_edge_roles.count("basin_patch_support_spoke"))
        self.assertEqual(2, motif_edge_roles.count("basin_patch_spindle_pair"))
        self.assertNotIn("basin_patch_ring", motif_edge_roles)

        for primitive_id in ("left_inlet", "right_outlet", "upper_clamp", "lower_clamp"):
            edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"][primitive_id]
            self.assertFalse(
                any(anchor_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} unexpectedly attached through the semantic center",
            )

    def test_grcv3_rich_v3_partition_probe_realizes_two_tier_probe_and_load_shells(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_PARTITION_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v3",
            state.cached_quantities["landscape_realization_mode"],
        )
        self.assertEqual(
            ["spindle_core"],
            state.cached_quantities["landscape_runtime_assembly_summary"][
                "interior_partition_primitive_ids"
            ],
        )
        self.assertIn(
            "spindle_core",
            state.cached_quantities["landscape_grcv3_interior_partition_summary"],
        )

        spindle_node_ids = state.cached_quantities["landscape_node_ids_by_primitive_id"]["spindle_core"]
        self.assertEqual(9, len(spindle_node_ids))

        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["spindle_core"]
        probe_role_node_ids = state.cached_quantities[
            "landscape_grcv3_probe_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        load_role_node_ids = state.cached_quantities[
            "landscape_grcv3_load_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        self.assertEqual({"north", "east", "south", "west"}, set(probe_role_node_ids))
        self.assertEqual({"north", "east", "south", "west"}, set(load_role_node_ids))
        self.assertNotEqual(probe_role_node_ids["east"], load_role_node_ids["east"])
        self.assertEqual(
            load_role_node_ids,
            state.cached_quantities["landscape_grcv3_role_node_ids_by_primitive_id"]["spindle_core"],
        )

        center = state.topology.node_payload(anchor_node_id)["chart_center_hint"]

        def _distance(node_id: int) -> float:
            point = state.topology.node_payload(node_id)["chart_center_hint"]
            return ((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2) ** 0.5

        self.assertLess(_distance(probe_role_node_ids["north"]), _distance(load_role_node_ids["north"]))
        self.assertLess(_distance(probe_role_node_ids["east"]), _distance(load_role_node_ids["east"]))

        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]
        motif_edge_roles = [
            state.topology.edge_payload(edge_id)["metadata"]["motif_edge_role"]
            for edge_id in spindle_edge_ids
        ]
        self.assertEqual(4, motif_edge_roles.count("basin_patch_support_spoke"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_partition_transfer"))
        self.assertEqual(2, motif_edge_roles.count("basin_patch_spindle_pair"))

        for primitive_id, expected_attach_node_id in {
            "left_inlet": load_role_node_ids["west"],
            "right_outlet": load_role_node_ids["east"],
            "upper_clamp": load_role_node_ids["north"],
            "lower_clamp": load_role_node_ids["south"],
        }.items():
            edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"][primitive_id]
            self.assertTrue(
                any(expected_attach_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} did not attach through the expected load-shell node",
            )
            self.assertFalse(
                any(anchor_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} unexpectedly attached through the semantic center",
            )

    def test_grcv3_rich_v3_load_carrier_probe_realizes_noncoincident_carriers(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V3_LOAD_CARRIER_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            ["spindle_core"],
            state.cached_quantities["landscape_runtime_assembly_summary"][
                "interior_load_carrier_primitive_ids"
            ],
        )
        self.assertIn(
            "spindle_core",
            state.cached_quantities["landscape_grcv3_interior_load_carrier_summary"],
        )

        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["spindle_core"]
        probe_role_node_ids = state.cached_quantities[
            "landscape_grcv3_probe_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        carrier_role_node_ids = state.cached_quantities[
            "landscape_grcv3_carrier_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        load_role_node_ids = state.cached_quantities[
            "landscape_grcv3_load_role_node_ids_by_primitive_id"
        ]["spindle_core"]

        self.assertEqual({"north", "east", "south", "west"}, set(probe_role_node_ids))
        self.assertEqual({"north", "east", "south", "west"}, set(carrier_role_node_ids))
        self.assertEqual(carrier_role_node_ids, load_role_node_ids)

        center = state.topology.node_payload(anchor_node_id)["chart_center_hint"]

        def _distance(node_id: int) -> float:
            point = state.topology.node_payload(node_id)["chart_center_hint"]
            return ((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2) ** 0.5

        for role_label in ("north", "east", "south", "west"):
            self.assertGreater(
                _distance(carrier_role_node_ids[role_label]),
                _distance(probe_role_node_ids[role_label]),
            )

        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]
        motif_edge_roles = [
            state.topology.edge_payload(edge_id)["metadata"]["motif_edge_role"]
            for edge_id in spindle_edge_ids
        ]
        self.assertEqual(4, motif_edge_roles.count("basin_patch_support_spoke"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_load_carrier_transfer"))
        self.assertEqual(2, motif_edge_roles.count("basin_patch_spindle_pair"))
        self.assertEqual(0, motif_edge_roles.count("basin_patch_partition_transfer"))

        for primitive_id, expected_attach_node_id in {
            "left_inlet": carrier_role_node_ids["west"],
            "right_outlet": carrier_role_node_ids["east"],
            "upper_clamp": carrier_role_node_ids["north"],
            "lower_clamp": carrier_role_node_ids["south"],
        }.items():
            edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"][primitive_id]
            self.assertTrue(
                any(expected_attach_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} did not attach through the expected load-carrier node",
            )

    def test_grcv3_rich_v4_transfer_mediation_probe_realizes_guarded_transfer_surface(
        self,
    ) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        self.assertEqual(
            ["spindle_core"],
            state.cached_quantities["landscape_runtime_assembly_summary"][
                "transfer_mediation_primitive_ids"
            ],
        )
        self.assertEqual(
            "basin_patch_valley_channel_junction_ridge_grcv3_rich_v4",
            state.cached_quantities["landscape_realization_mode"],
        )

        mediation_summary = state.cached_quantities["landscape_grcv3_transfer_mediation_summary"][
            "spindle_core"
        ]
        self.assertEqual("guarded_pairs", mediation_summary["mediation_mode"])
        self.assertEqual("guarded_center", mediation_summary["probe_guard_class"])
        self.assertEqual("axis_locked", mediation_summary["lateral_spill_policy"])

        probe_role_node_ids = state.cached_quantities[
            "landscape_grcv3_probe_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        carrier_role_node_ids = state.cached_quantities[
            "landscape_grcv3_carrier_role_node_ids_by_primitive_id"
        ]["spindle_core"]
        anchor_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"]["spindle_core"]
        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]

        spoke_weights: dict[str, float] = {}
        motif_edge_roles: list[str] = []
        transfer_edge_metadata: list[dict[str, object]] = []
        for edge_id in spindle_edge_ids:
            payload = state.topology.edge_payload(edge_id)
            metadata = payload["metadata"]
            motif_edge_roles.append(metadata["motif_edge_role"])
            if metadata["motif_edge_role"] == "basin_patch_support_spoke":
                source_node_id, target_node_id = state.topology.edge_endpoints(edge_id)
                support_node_id = target_node_id if source_node_id == state.cached_quantities[
                    "landscape_node_id_by_primitive_id"
                ]["spindle_core"] else source_node_id
                role_label = state.topology.node_payload(support_node_id)["metadata"].get(
                    "grcv3_role_label"
                )
                if isinstance(role_label, str):
                    spoke_weights[role_label] = state.base_conductance[edge_id]
            if metadata["motif_edge_role"] in {
                "basin_patch_load_carrier_transfer",
                "basin_patch_transfer_mediation_spill",
            }:
                transfer_edge_metadata.append(metadata)

        self.assertEqual(4, motif_edge_roles.count("basin_patch_support_spoke"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_load_carrier_transfer"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_mediation_spill"))
        self.assertEqual(2, motif_edge_roles.count("basin_patch_spindle_pair"))

        self.assertLess(spoke_weights["north"], spoke_weights["east"])
        self.assertLess(spoke_weights["south"], spoke_weights["west"])

        pair_edges = [
            metadata
            for metadata in transfer_edge_metadata
            if metadata["motif_edge_role"] == "basin_patch_load_carrier_transfer"
        ]
        spill_edges = [
            metadata
            for metadata in transfer_edge_metadata
            if metadata["motif_edge_role"] == "basin_patch_transfer_mediation_spill"
        ]
        self.assertTrue(
            all(metadata.get("probe_guard_class") == "guarded_center" for metadata in pair_edges)
        )
        self.assertTrue(
            all(metadata.get("lateral_spill_policy") == "axis_locked" for metadata in spill_edges)
        )
        self.assertEqual(
            {
                ("north", "north", "medium"),
                ("south", "south", "medium"),
                ("east", "north", "weak"),
                ("west", "south", "weak"),
            },
            {
                (
                    str(metadata.get("carrier_role")),
                    str(metadata.get("probe_role")),
                    str(metadata.get("mediation_class")),
                )
                for metadata in pair_edges
            },
        )

        for primitive_id, expected_attach_node_id in {
            "left_inlet": carrier_role_node_ids["west"],
            "right_outlet": carrier_role_node_ids["east"],
            "upper_clamp": carrier_role_node_ids["north"],
            "lower_clamp": carrier_role_node_ids["south"],
        }.items():
            edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"][primitive_id]
            self.assertTrue(
                any(expected_attach_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} did not attach through the expected mediated load-carrier node",
            )
            self.assertFalse(
                any(anchor_node_id in state.topology.edge_endpoints(edge_id) for edge_id in edge_ids),
                msg=f"{primitive_id} unexpectedly attached through the semantic center",
            )

    def test_grcv3_rich_v4_transfer_mediation_breaks_the_rich_v3_plateau_under_baseline_gate(
        self,
    ) -> None:
        rich_v3_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V3_WEAK_TO_STABLE_PROBE,
            num_steps=50,
        )
        rich_v4_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )

        rich_v3_event_counts: dict[str, int] = {}
        for step in rich_v3_run.step_results:
            for event in step.events:
                rich_v3_event_counts[event.kind] = rich_v3_event_counts.get(event.kind, 0) + 1

        rich_v4_event_counts: dict[str, int] = {}
        for step in rich_v4_run.step_results:
            for event in step.events:
                rich_v4_event_counts[event.kind] = rich_v4_event_counts.get(event.kind, 0) + 1

        self.assertEqual(0, rich_v3_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, rich_v3_event_counts.get("spark", 0))
        self.assertGreaterEqual(rich_v4_event_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(rich_v4_event_counts.get("spark", 0), 1)
        self.assertGreaterEqual(rich_v4_event_counts.get("split_init", 0), 1)
        self.assertGreaterEqual(rich_v4_event_counts.get("split_complete", 0), 1)

    def test_grcv3_rich_v4_path_topology_probe_realizes_shared_fan_in_paths(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        mediation_summary = state.cached_quantities["landscape_grcv3_transfer_mediation_summary"][
            "spindle_core"
        ]
        self.assertEqual(
            [
                ["north", "north", "fan_in"],
                ["south", "south", "fan_in"],
                ["east", "north", "fan_in"],
                ["west", "south", "fan_in"],
            ],
            mediation_summary["path_topology"],
        )

        fan_in_node_ids = state.cached_quantities[
            "landscape_grcv3_transfer_fan_in_node_ids_by_probe_by_primitive_id"
        ]["spindle_core"]
        self.assertEqual({"north", "south"}, set(fan_in_node_ids))

        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]
        motif_edge_roles: list[str] = []
        path_ingress_metadata: list[dict[str, object]] = []
        path_egress_metadata: list[dict[str, object]] = []
        spill_metadata: list[dict[str, object]] = []
        for edge_id in spindle_edge_ids:
            metadata = state.topology.edge_payload(edge_id)["metadata"]
            motif_edge_role = str(metadata["motif_edge_role"])
            motif_edge_roles.append(motif_edge_role)
            if motif_edge_role == "basin_patch_transfer_path_ingress":
                path_ingress_metadata.append(metadata)
            elif motif_edge_role == "basin_patch_transfer_path_egress":
                path_egress_metadata.append(metadata)
            elif motif_edge_role == "basin_patch_transfer_mediation_spill":
                spill_metadata.append(metadata)

        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_path_ingress"))
        self.assertEqual(2, motif_edge_roles.count("basin_patch_transfer_path_egress"))
        self.assertEqual(0, motif_edge_roles.count("basin_patch_load_carrier_transfer"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_mediation_spill"))

        self.assertEqual(
            {
                ("north", "north", "fan_in"),
                ("south", "south", "fan_in"),
                ("east", "north", "fan_in"),
                ("west", "south", "fan_in"),
            },
            {
                (
                    str(metadata.get("carrier_role")),
                    str(metadata.get("probe_role")),
                    str(metadata.get("transfer_path_topology_class")),
                )
                for metadata in path_ingress_metadata
            },
        )
        self.assertEqual(
            {
                ("north", ("east", "north")),
                ("south", ("south", "west")),
            },
            {
                (
                    str(metadata.get("probe_role")),
                    tuple(sorted(str(role) for role in metadata.get("carrier_roles", []))),
                )
                for metadata in path_egress_metadata
            },
        )
        self.assertTrue(
            all(
                str(metadata.get("transfer_path_topology_class")) == "fan_in"
                for metadata in spill_metadata
            )
        )

    def test_grcv3_rich_v4_path_topology_probe_suppresses_the_baseline_spark_lane(self) -> None:
        baseline_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )
        path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE,
            num_steps=50,
        )

        baseline_event_counts: dict[str, int] = {}
        for step in baseline_run.step_results:
            for event in step.events:
                baseline_event_counts[event.kind] = baseline_event_counts.get(event.kind, 0) + 1

        path_event_counts: dict[str, int] = {}
        for step in path_run.step_results:
            for event in step.events:
                path_event_counts[event.kind] = path_event_counts.get(event.kind, 0) + 1

        self.assertGreaterEqual(baseline_event_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(baseline_event_counts.get("spark", 0), 1)
        self.assertEqual(0, path_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, path_event_counts.get("spark", 0))

    def test_grcv3_rich_v4_single_intermediate_probe_realizes_dedicated_pair_paths(self) -> None:
        seed = load_landscape_seed(_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        state = project_landscape_seed_to_grcv3_state(seed, params=params)

        self.assertEqual("family_native", state.cached_quantities["landscape_lowering_lane"])
        mediation_summary = state.cached_quantities["landscape_grcv3_transfer_mediation_summary"][
            "spindle_core"
        ]
        self.assertEqual(
            [
                ["north", "north", "single_intermediate"],
                ["south", "south", "single_intermediate"],
                ["east", "north", "single_intermediate"],
                ["west", "south", "single_intermediate"],
            ],
            mediation_summary["path_topology"],
        )

        pair_path_node_ids = state.cached_quantities[
            "landscape_grcv3_transfer_path_node_ids_by_pair_by_primitive_id"
        ]["spindle_core"]
        self.assertEqual(
            {"north->north", "south->south", "east->north", "west->south"},
            set(pair_path_node_ids),
        )

        spindle_edge_ids = state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]
        motif_edge_roles: list[str] = []
        path_ingress_metadata: list[dict[str, object]] = []
        path_egress_metadata: list[dict[str, object]] = []
        spill_metadata: list[dict[str, object]] = []
        for edge_id in spindle_edge_ids:
            metadata = state.topology.edge_payload(edge_id)["metadata"]
            motif_edge_role = str(metadata["motif_edge_role"])
            motif_edge_roles.append(motif_edge_role)
            if motif_edge_role == "basin_patch_transfer_path_ingress":
                path_ingress_metadata.append(metadata)
            elif motif_edge_role == "basin_patch_transfer_path_egress":
                path_egress_metadata.append(metadata)
            elif motif_edge_role == "basin_patch_transfer_mediation_spill":
                spill_metadata.append(metadata)

        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_path_ingress"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_path_egress"))
        self.assertEqual(0, motif_edge_roles.count("basin_patch_load_carrier_transfer"))
        self.assertEqual(4, motif_edge_roles.count("basin_patch_transfer_mediation_spill"))
        self.assertEqual(
            {
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            },
            {
                (
                    str(metadata.get("carrier_role")),
                    str(metadata.get("probe_role")),
                    str(metadata.get("transfer_path_topology_class")),
                )
                for metadata in path_ingress_metadata
            },
        )
        self.assertEqual(
            {
                ("north", "north", "single_intermediate"),
                ("south", "south", "single_intermediate"),
                ("east", "north", "single_intermediate"),
                ("west", "south", "single_intermediate"),
            },
            {
                (
                    str(metadata.get("carrier_role")),
                    str(metadata.get("probe_role")),
                    str(metadata.get("transfer_path_topology_class")),
                )
                for metadata in path_egress_metadata
            },
        )
        self.assertTrue(
            all(
                str(metadata.get("transfer_path_topology_class")) == "single_intermediate"
                for metadata in spill_metadata
            )
        )

    def test_grcv3_rich_v4_single_intermediate_probe_shows_suppression_is_general_to_intermediacy(
        self,
    ) -> None:
        baseline_seed = load_landscape_seed(_GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE)
        baseline_params = resolve_grcv3_landscape_params(baseline_seed)
        baseline_model = build_grcv3_from_landscape_seed(
            baseline_seed,
            params=baseline_params,
            validate_seed=False,
        )
        baseline_model.rebuild_basin_attributes()

        fan_in_seed = load_landscape_seed(_GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE)
        fan_in_params = resolve_grcv3_landscape_params(fan_in_seed)
        fan_in_model = build_grcv3_from_landscape_seed(
            fan_in_seed,
            params=fan_in_params,
            validate_seed=False,
        )
        fan_in_model.rebuild_basin_attributes()

        single_seed = load_landscape_seed(_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE)
        single_params = resolve_grcv3_landscape_params(single_seed)
        single_model = build_grcv3_from_landscape_seed(
            single_seed,
            params=single_params,
            validate_seed=False,
        )
        single_model.rebuild_basin_attributes()

        baseline_center = baseline_model.get_state().cached_quantities["landscape_node_id_by_primitive_id"][
            "spindle_core"
        ]
        fan_in_center = fan_in_model.get_state().cached_quantities["landscape_node_id_by_primitive_id"][
            "spindle_core"
        ]
        single_center = single_model.get_state().cached_quantities["landscape_node_id_by_primitive_id"][
            "spindle_core"
        ]

        baseline_gradient_norm = sum(
            value * value for value in baseline_model.get_state().nodes[baseline_center].gradient
        ) ** 0.5
        fan_in_gradient_norm = sum(
            value * value for value in fan_in_model.get_state().nodes[fan_in_center].gradient
        ) ** 0.5
        single_gradient_norm = sum(
            value * value for value in single_model.get_state().nodes[single_center].gradient
        ) ** 0.5

        self.assertEqual(baseline_gradient_norm, fan_in_gradient_norm)
        self.assertEqual(baseline_gradient_norm, single_gradient_norm)

        baseline_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )
        fan_in_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_PATH_TOPOLOGY_PROBE,
            num_steps=50,
        )
        single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        baseline_event_counts = _event_counts(baseline_run)
        fan_in_event_counts = _event_counts(fan_in_run)
        single_event_counts = _event_counts(single_run)

        self.assertGreaterEqual(baseline_event_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(baseline_event_counts.get("spark", 0), 1)
        self.assertEqual(0, fan_in_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, fan_in_event_counts.get("spark", 0))
        self.assertEqual(0, single_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, single_event_counts.get("spark", 0))

    def test_grcv3_rich_v4_single_intermediate_low_mass_diagnostic_only_changes_path_node_mass(
        self,
    ) -> None:
        baseline_seed = load_landscape_seed(_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE)
        baseline_params = resolve_grcv3_landscape_params(baseline_seed)
        baseline_state = project_landscape_seed_to_grcv3_state(
            baseline_seed,
            params=baseline_params,
        )

        with mock.patch.object(grc_v3_landscape_module, "_TRANSFER_PATH_NODE_MASS_SCALE", 0.2):
            low_mass_state = project_landscape_seed_to_grcv3_state(
                baseline_seed,
                params=baseline_params,
            )
            low_mass_run = run_grcv3_landscape_seed(
                _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE,
                num_steps=50,
            )

        path_node_ids = baseline_state.cached_quantities[
            "landscape_grcv3_transfer_path_node_ids_by_pair_by_primitive_id"
        ]["spindle_core"]
        for node_id in path_node_ids.values():
            self.assertLess(
                low_mass_state.nodes[node_id].basin_mass,
                baseline_state.nodes[node_id].basin_mass,
            )

        def _path_edge_weights(state) -> dict[tuple[str, str, str], float]:
            weights: dict[tuple[str, str, str], float] = {}
            for edge_id in state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]:
                metadata = state.topology.edge_payload(edge_id)["metadata"]
                motif_edge_role = str(metadata.get("motif_edge_role"))
                if motif_edge_role not in {
                    "basin_patch_transfer_path_ingress",
                    "basin_patch_transfer_path_egress",
                }:
                    continue
                weights[
                    (
                        motif_edge_role,
                        str(metadata.get("carrier_role")),
                        str(metadata.get("probe_role")),
                    )
                ] = state.base_conductance[edge_id]
            return weights

        self.assertEqual(
            _path_edge_weights(baseline_state),
            _path_edge_weights(low_mass_state),
        )

        low_mass_event_counts: dict[str, int] = {}
        for step in low_mass_run.step_results:
            for event in step.events:
                low_mass_event_counts[event.kind] = low_mass_event_counts.get(event.kind, 0) + 1
        self.assertEqual(0, low_mass_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, low_mass_event_counts.get("spark", 0))

    def test_grcv3_rich_v4_single_intermediate_strong_path_diagnostic_only_changes_path_edge_coupling(
        self,
    ) -> None:
        baseline_seed = load_landscape_seed(_GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE)
        baseline_params = resolve_grcv3_landscape_params(baseline_seed)
        baseline_state = project_landscape_seed_to_grcv3_state(
            baseline_seed,
            params=baseline_params,
        )

        strong_path_scale = 1.0 / 0.68
        with mock.patch.object(
            grc_v3_landscape_module,
            "_TRANSFER_PATH_EDGE_WEIGHT_SCALE",
            strong_path_scale,
        ):
            strong_path_state = project_landscape_seed_to_grcv3_state(
                baseline_seed,
                params=baseline_params,
            )
            strong_path_run = run_grcv3_landscape_seed(
                _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE,
                num_steps=50,
            )

        path_node_ids = baseline_state.cached_quantities[
            "landscape_grcv3_transfer_path_node_ids_by_pair_by_primitive_id"
        ]["spindle_core"]
        for node_id in path_node_ids.values():
            self.assertEqual(
                baseline_state.nodes[node_id].basin_mass,
                strong_path_state.nodes[node_id].basin_mass,
            )

        def _path_edge_weights(state) -> dict[tuple[str, str, str], float]:
            weights: dict[tuple[str, str, str], float] = {}
            for edge_id in state.cached_quantities["landscape_edge_ids_by_primitive_id"]["spindle_core"]:
                metadata = state.topology.edge_payload(edge_id)["metadata"]
                motif_edge_role = str(metadata.get("motif_edge_role"))
                if motif_edge_role not in {
                    "basin_patch_transfer_path_ingress",
                    "basin_patch_transfer_path_egress",
                }:
                    continue
                weights[
                    (
                        motif_edge_role,
                        str(metadata.get("carrier_role")),
                        str(metadata.get("probe_role")),
                    )
                ] = state.base_conductance[edge_id]
            return weights

        baseline_weights = _path_edge_weights(baseline_state)
        strong_path_weights = _path_edge_weights(strong_path_state)
        for key, baseline_weight in baseline_weights.items():
            self.assertGreater(strong_path_weights[key], baseline_weight)

        strong_path_event_counts: dict[str, int] = {}
        for step in strong_path_run.step_results:
            for event in step.events:
                strong_path_event_counts[event.kind] = strong_path_event_counts.get(event.kind, 0) + 1
        self.assertEqual(0, strong_path_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, strong_path_event_counts.get("spark", 0))

    def test_grcv3_rich_v4_center_coupling_probe_changes_support_spokes_without_leaving_transfer_mediation(
        self,
    ) -> None:
        baseline_seed = load_landscape_seed(_GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE)
        baseline_params = resolve_grcv3_landscape_params(baseline_seed)
        baseline_state = project_landscape_seed_to_grcv3_state(baseline_seed, params=baseline_params)
        baseline_model = build_grcv3_from_landscape_seed(
            baseline_seed,
            params=baseline_params,
            validate_seed=False,
        )
        baseline_model.rebuild_basin_attributes()

        blocked_seed = load_landscape_seed(_GRCV3_RICH_V4_CENTER_COUPLING_PROBE)
        blocked_params = resolve_grcv3_landscape_params(blocked_seed)
        blocked_state = project_landscape_seed_to_grcv3_state(blocked_seed, params=blocked_params)
        blocked_model = build_grcv3_from_landscape_seed(
            blocked_seed,
            params=blocked_params,
            validate_seed=False,
        )
        blocked_model.rebuild_basin_attributes()

        baseline_summary = baseline_state.cached_quantities["landscape_grcv3_transfer_mediation_summary"][
            "spindle_core"
        ]
        blocked_summary = blocked_state.cached_quantities["landscape_grcv3_transfer_mediation_summary"][
            "spindle_core"
        ]
        self.assertEqual([], baseline_summary["center_coupling_classes"])
        self.assertEqual(
            [["north", "blocked"], ["south", "blocked"]],
            blocked_summary["center_coupling_classes"],
        )

        baseline_anchor_node_id = baseline_state.cached_quantities["landscape_node_id_by_primitive_id"][
            "spindle_core"
        ]
        blocked_anchor_node_id = blocked_state.cached_quantities["landscape_node_id_by_primitive_id"][
            "spindle_core"
        ]
        baseline_spindle_edge_ids = baseline_state.cached_quantities["landscape_edge_ids_by_primitive_id"][
            "spindle_core"
        ]
        blocked_spindle_edge_ids = blocked_state.cached_quantities["landscape_edge_ids_by_primitive_id"][
            "spindle_core"
        ]

        def _support_spokes_by_role(state, anchor_node_id: int, edge_ids: list[int]) -> dict[str, float]:
            roles: dict[str, float] = {}
            for edge_id in edge_ids:
                payload = state.topology.edge_payload(edge_id)
                metadata = payload["metadata"]
                if metadata["motif_edge_role"] != "basin_patch_support_spoke":
                    continue
                source_node_id, target_node_id = state.topology.edge_endpoints(edge_id)
                support_node_id = target_node_id if source_node_id == anchor_node_id else source_node_id
                role_label = state.topology.node_payload(support_node_id)["metadata"].get("grcv3_role_label")
                if isinstance(role_label, str):
                    roles[role_label] = state.base_conductance[edge_id]
            return roles

        baseline_spokes = _support_spokes_by_role(
            baseline_state,
            baseline_anchor_node_id,
            baseline_spindle_edge_ids,
        )
        blocked_spokes = _support_spokes_by_role(
            blocked_state,
            blocked_anchor_node_id,
            blocked_spindle_edge_ids,
        )

        self.assertEqual({"north", "east", "south", "west"}, set(baseline_spokes))
        self.assertEqual({"east", "west"}, set(blocked_spokes))

        baseline_gradient_norm = sum(
            value * value for value in baseline_model.get_state().nodes[baseline_anchor_node_id].gradient
        ) ** 0.5
        blocked_gradient_norm = sum(
            value * value for value in blocked_model.get_state().nodes[blocked_anchor_node_id].gradient
        ) ** 0.5
        self.assertLess(blocked_gradient_norm, baseline_gradient_norm)

    def test_grcv3_rich_v4_center_coupling_probe_overguards_the_baseline_spark_lane(
        self,
    ) -> None:
        baseline_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )
        blocked_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_CENTER_COUPLING_PROBE,
            num_steps=50,
        )

        baseline_event_counts: dict[str, int] = {}
        for step in baseline_run.step_results:
            for event in step.events:
                baseline_event_counts[event.kind] = baseline_event_counts.get(event.kind, 0) + 1

        blocked_event_counts: dict[str, int] = {}
        for step in blocked_run.step_results:
            for event in step.events:
                blocked_event_counts[event.kind] = blocked_event_counts.get(event.kind, 0) + 1

        self.assertGreaterEqual(baseline_event_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(baseline_event_counts.get("spark", 0), 1)
        self.assertEqual(0, blocked_event_counts.get("spark_candidate", 0))
        self.assertEqual(0, blocked_event_counts.get("spark", 0))

    def test_grcv3_rich_v4_open_center_comparison_shows_guard_regime_and_path_topology_both_matter(
        self,
    ) -> None:
        guarded_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )
        guarded_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        open_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_OPEN_CENTER_CONTROL_PROBE,
            num_steps=50,
        )
        open_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        guarded_direct_counts = _event_counts(guarded_direct_run)
        guarded_single_counts = _event_counts(guarded_single_run)
        open_direct_counts = _event_counts(open_direct_run)
        open_single_counts = _event_counts(open_single_run)

        self.assertGreaterEqual(guarded_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(guarded_direct_counts.get("spark", 0), 1)
        self.assertEqual(0, guarded_single_counts.get("spark_candidate", 0))
        self.assertEqual(0, guarded_single_counts.get("spark", 0))
        self.assertEqual(0, open_direct_counts.get("spark_candidate", 0))
        self.assertEqual(0, open_direct_counts.get("spark", 0))
        self.assertEqual(0, open_single_counts.get("spark_candidate", 0))
        self.assertEqual(0, open_single_counts.get("spark", 0))

        open_direct_seed = load_landscape_seed(_GRCV3_RICH_V4_OPEN_CENTER_CONTROL_PROBE)
        open_direct_params = resolve_grcv3_landscape_params(open_direct_seed)
        open_direct_model = build_grcv3_from_landscape_seed(
            open_direct_seed,
            params=open_direct_params,
            validate_seed=False,
        )
        open_direct_model.rebuild_basin_attributes()
        open_direct_model.rebuild_identity_state()
        open_direct_step = open_direct_model.step()

        open_single_seed = load_landscape_seed(
            _GRCV3_RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_PROBE
        )
        open_single_params = resolve_grcv3_landscape_params(open_single_seed)
        open_single_model = build_grcv3_from_landscape_seed(
            open_single_seed,
            params=open_single_params,
            validate_seed=False,
        )
        open_single_model.rebuild_basin_attributes()
        open_single_model.rebuild_identity_state()
        open_single_step = open_single_model.step()

        self.assertEqual(1, open_direct_step.step_index)
        self.assertEqual(1, open_single_step.step_index)

        open_direct_center = open_direct_model.get_state().cached_quantities[
            "landscape_node_id_by_primitive_id"
        ]["spindle_core"]
        open_single_center = open_single_model.get_state().cached_quantities[
            "landscape_node_id_by_primitive_id"
        ]["spindle_core"]

        def _min_signed_eigenvalue(model, node_id: int) -> float:
            hessian_sign = model.get_state().cached_quantities["hessian_sign"]
            signed_hessian = [
                [float(hessian_sign) * float(value) for value in row]
                for row in model.get_state().nodes[node_id].hessian
            ]
            return min(symmetric_eigenvalues(signed_hessian))

        open_direct_min_eigenvalue = _min_signed_eigenvalue(
            open_direct_model,
            open_direct_center,
        )
        open_single_min_eigenvalue = _min_signed_eigenvalue(
            open_single_model,
            open_single_center,
        )
        self.assertLess(open_direct_min_eigenvalue, 0.0)
        self.assertGreater(open_single_min_eigenvalue, open_direct_min_eigenvalue)

        open_direct_state = open_direct_model.get_state()
        open_single_state = open_single_model.get_state()
        open_direct_flux = 0.0
        open_single_path_flux = 0.0
        for edge_id in open_direct_state.cached_quantities["landscape_edge_ids_by_primitive_id"][
            "spindle_core"
        ]:
            metadata = open_direct_state.topology.edge_payload(edge_id)["metadata"]
            if metadata["motif_edge_role"] != "basin_patch_load_carrier_transfer":
                continue
            source_node_id, _ = open_direct_state.topology.edge_endpoints(edge_id)
            open_direct_flux += abs(float(open_direct_state.flux.get((edge_id, source_node_id), 0.0)))
        for edge_id in open_single_state.cached_quantities["landscape_edge_ids_by_primitive_id"][
            "spindle_core"
        ]:
            metadata = open_single_state.topology.edge_payload(edge_id)["metadata"]
            if metadata["motif_edge_role"] != "basin_patch_transfer_path_egress":
                continue
            source_node_id, _ = open_single_state.topology.edge_endpoints(edge_id)
            open_single_path_flux += abs(
                float(open_single_state.flux.get((edge_id, source_node_id), 0.0))
            )
        self.assertGreater(open_direct_flux, 0.0)
        self.assertGreater(open_single_path_flux, 0.0)

    def test_grcv3_rich_v4_asymmetric_center_coupling_refinement_preserves_direct_spark_and_improves_path_geometry(
        self,
    ) -> None:
        guarded_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_TRANSFER_MEDIATION_PROBE,
            num_steps=50,
        )
        guarded_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        refined_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_PROBE,
            num_steps=50,
        )
        refined_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        guarded_direct_counts = _event_counts(guarded_direct_run)
        guarded_single_counts = _event_counts(guarded_single_run)
        refined_direct_counts = _event_counts(refined_direct_run)
        refined_single_counts = _event_counts(refined_single_run)

        self.assertGreaterEqual(guarded_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(guarded_direct_counts.get("spark", 0), 1)
        self.assertEqual(0, guarded_single_counts.get("spark_candidate", 0))
        self.assertEqual(0, guarded_single_counts.get("spark", 0))
        self.assertGreaterEqual(refined_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(refined_direct_counts.get("spark", 0), 1)
        self.assertEqual(0, refined_single_counts.get("spark_candidate", 0))
        self.assertEqual(0, refined_single_counts.get("spark", 0))

        def _step1_min_signed_eigenvalue(seed_path: Path) -> float:
            seed = load_landscape_seed(seed_path)
            params = resolve_grcv3_landscape_params(seed)
            model = build_grcv3_from_landscape_seed(
                seed,
                params=params,
                validate_seed=False,
            )
            model.rebuild_basin_attributes()
            model.rebuild_identity_state()
            model.step()
            state = model.get_state()
            center_node_id = state.cached_quantities["landscape_node_id_by_primitive_id"][
                "spindle_core"
            ]
            hessian_sign = state.cached_quantities["hessian_sign"]
            signed_hessian = [
                [float(hessian_sign) * float(value) for value in row]
                for row in state.nodes[center_node_id].hessian
            ]
            return min(symmetric_eigenvalues(signed_hessian))

        guarded_single_eig = _step1_min_signed_eigenvalue(
            _GRCV3_RICH_V4_SINGLE_INTERMEDIATE_PROBE
        )
        refined_direct_eig = _step1_min_signed_eigenvalue(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_PROBE
        )
        refined_single_eig = _step1_min_signed_eigenvalue(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_PROBE
        )

        self.assertGreater(guarded_single_eig, -1e-6)
        self.assertLess(refined_direct_eig, 0.0)
        self.assertLess(refined_single_eig, -0.1)
        self.assertLess(refined_single_eig, guarded_single_eig)

    def test_grcv3_rich_v4_asymmetric_pair_mediation_localizes_direct_spark_but_not_path_settlement(
        self,
    ) -> None:
        refined_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_PROBE,
            num_steps=50,
        )
        refined_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        localized_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_PROBE,
            num_steps=50,
        )
        localized_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        refined_direct_counts = _event_counts(refined_direct_run)
        refined_single_counts = _event_counts(refined_single_run)
        localized_direct_counts = _event_counts(localized_direct_run)
        localized_single_counts = _event_counts(localized_single_run)

        self.assertGreaterEqual(refined_direct_counts.get("spark_candidate", 0), 1)
        self.assertEqual(0, refined_single_counts.get("spark_candidate", 0))
        self.assertGreaterEqual(localized_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(localized_direct_counts.get("spark", 0), 1)
        self.assertEqual(0, localized_single_counts.get("spark_candidate", 0))
        self.assertEqual(0, localized_single_counts.get("spark", 0))
        self.assertLess(
            localized_direct_counts.get("spark_candidate", 0),
            refined_direct_counts.get("spark_candidate", 0),
        )

    def test_grcv3_rich_v4_mediated_spill_branch_restores_path_spark_at_path_node(
        self,
    ) -> None:
        localized_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_PROBE,
            num_steps=50,
        )
        localized_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        mediated_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_PROBE,
            num_steps=50,
        )
        mediated_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        localized_direct_counts = _event_counts(localized_direct_run)
        localized_single_counts = _event_counts(localized_single_run)
        mediated_direct_counts = _event_counts(mediated_direct_run)
        mediated_single_counts = _event_counts(mediated_single_run)

        self.assertGreaterEqual(localized_direct_counts.get("spark_candidate", 0), 1)
        self.assertEqual(0, localized_single_counts.get("spark_candidate", 0))
        self.assertGreaterEqual(mediated_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(mediated_single_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(mediated_single_counts.get("spark", 0), 1)

        seed = load_landscape_seed(_GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE)
        params = resolve_grcv3_landscape_params(seed)
        model = build_grcv3_from_landscape_seed(
            seed,
            params=params,
            validate_seed=False,
        )
        model.rebuild_basin_attributes()
        model.rebuild_identity_state()

        payload = None
        for _ in range(50):
            step = model.step()
            candidate_events = [event for event in step.events if event.kind == "spark_candidate"]
            if not candidate_events:
                continue
            node_id = int(candidate_events[0].payload["node_id"])
            payload = model.get_state().topology.node_payload(node_id)
            break

        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual("basin_transfer_path_node", payload["motif_role"])
        self.assertTrue(str(payload["realized_key"]).startswith("spindle_core::transfer_path:"))

    def test_grcv3_rich_v4_role_locked_spill_policy_suppresses_settlement_regimes(
        self,
    ) -> None:
        carrier_axis_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_PROBE,
            num_steps=50,
        )
        carrier_axis_path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        carrier_role_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_PROBE,
            num_steps=50,
        )
        carrier_role_path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        mediated_axis_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_PROBE,
            num_steps=50,
        )
        mediated_axis_path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        mediated_role_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_PROBE,
            num_steps=50,
        )
        mediated_role_path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        carrier_axis_direct_counts = _event_counts(carrier_axis_direct_run)
        carrier_axis_path_counts = _event_counts(carrier_axis_path_run)
        carrier_role_direct_counts = _event_counts(carrier_role_direct_run)
        carrier_role_path_counts = _event_counts(carrier_role_path_run)
        mediated_axis_direct_counts = _event_counts(mediated_axis_direct_run)
        mediated_axis_path_counts = _event_counts(mediated_axis_path_run)
        mediated_role_direct_counts = _event_counts(mediated_role_direct_run)
        mediated_role_path_counts = _event_counts(mediated_role_path_run)

        self.assertGreaterEqual(carrier_axis_direct_counts.get("spark_candidate", 0), 1)
        self.assertEqual(0, carrier_axis_path_counts.get("spark_candidate", 0))
        self.assertEqual(0, carrier_role_direct_counts.get("spark_candidate", 0))
        self.assertEqual(0, carrier_role_path_counts.get("spark_candidate", 0))
        self.assertGreaterEqual(mediated_axis_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(mediated_axis_path_counts.get("spark_candidate", 0), 1)
        self.assertEqual(0, mediated_role_direct_counts.get("spark_candidate", 0))
        self.assertEqual(0, mediated_role_path_counts.get("spark_candidate", 0))

    def test_grcv3_rich_v4_settlement_regime_makes_known_direct_and_path_regimes_executable(
        self,
    ) -> None:
        direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE,
            num_steps=12,
        )
        path_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_PROBE,
            num_steps=12,
        )

        direct_counts = _event_counts(direct_run)
        path_counts = _event_counts(path_run)

        self.assertGreaterEqual(direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(path_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(path_counts.get("split_complete", 0), 1)

        direct_seed = load_landscape_seed(_GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE)
        direct_params = resolve_grcv3_landscape_params(direct_seed)
        direct_model = build_grcv3_from_landscape_seed(
            direct_seed,
            params=direct_params,
            validate_seed=False,
        )
        direct_model.rebuild_basin_attributes()
        direct_payload = None
        for _ in range(12):
            step = direct_model.step()
            candidate_events = [event for event in step.events if event.kind == "spark_candidate"]
            if not candidate_events:
                continue
            direct_payload = direct_model.get_state().topology.node_payload(
                int(candidate_events[0].payload["node_id"])
            )
            break

        self.assertIsNotNone(direct_payload)
        assert direct_payload is not None
        self.assertEqual("basin_load_carrier", direct_payload["motif_role"])

        path_seed = load_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_PROBE
        )
        path_params = resolve_grcv3_landscape_params(path_seed)
        path_model = build_grcv3_from_landscape_seed(
            path_seed,
            params=path_params,
            validate_seed=False,
        )
        path_model.rebuild_basin_attributes()
        first_path_payload = None
        saw_split_child_candidate = False
        for _ in range(12):
            step = path_model.step()
            candidate_events = [event for event in step.events if event.kind == "spark_candidate"]
            if not candidate_events:
                continue
            node_payloads = [
                path_model.get_state().topology.node_payload(int(event.payload["node_id"]))
                for event in candidate_events
            ]
            if first_path_payload is None:
                first_path_payload = node_payloads[0]
            if any(payload.get("kind") == "split_child" for payload in node_payloads):
                saw_split_child_candidate = True

        self.assertIsNotNone(first_path_payload)
        assert first_path_payload is not None
        self.assertEqual("basin_transfer_path_node", first_path_payload["motif_role"])
        self.assertTrue(saw_split_child_candidate)

    def test_grcv3_rich_v4_settlement_regime_can_suppress_mismatched_path_lane(
        self,
    ) -> None:
        seed = deepcopy(
            load_landscape_seed(_GRCV3_RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_PROBE)
        )
        spindle_core = next(
            primitive for primitive in seed.primitives if primitive.id == "spindle_core"
        )
        assert isinstance(spindle_core, BasinSeedPrimitive)
        spindle_core.extensions["grcv3"]["settlement_regime"] = {
            "regime_class": "carrier_site_regime"
        }

        run = run_grcv3_landscape_seed(seed, num_steps=12)

        counts = _event_counts(run)

        self.assertEqual(0, counts.get("spark_candidate", 0))
        self.assertEqual(0, counts.get("spark", 0))

    def test_grcv3_rich_v4_settlement_regime_decomposition_separates_anchor_and_later_migration(
        self,
    ) -> None:
        inheriting_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE,
            num_steps=12,
        )
        anchored_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_PROBE,
            num_steps=12,
        )

        inheriting_counts = _event_counts(inheriting_run)
        anchored_counts = _event_counts(anchored_run)

        self.assertEqual(3, inheriting_counts.get("spark_candidate", 0))
        self.assertEqual(3, inheriting_counts.get("split_complete", 0))
        self.assertEqual(1, anchored_counts.get("spark_candidate", 0))
        self.assertEqual(1, anchored_counts.get("split_complete", 0))

        anchored_seed = load_landscape_seed(_GRCV3_RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_PROBE)
        anchored_params = resolve_grcv3_landscape_params(anchored_seed)
        anchored_model = build_grcv3_from_landscape_seed(
            anchored_seed,
            params=anchored_params,
            validate_seed=False,
        )
        anchored_model.rebuild_basin_attributes()
        anchored_model.rebuild_identity_state()

        first_candidate_payload = None
        saw_split_child_candidate = False
        for _ in range(12):
            step = anchored_model.step()
            candidate_events = [event for event in step.events if event.kind == "spark_candidate"]
            if not candidate_events:
                continue
            for event in candidate_events:
                payload = anchored_model.get_state().topology.node_payload(
                    int(event.payload["node_id"])
                )
                if first_candidate_payload is None:
                    first_candidate_payload = payload
                if payload.get("kind") == "split_child":
                    saw_split_child_candidate = True

        self.assertIsNotNone(first_candidate_payload)
        assert first_candidate_payload is not None
        self.assertEqual("basin_transfer_path_node", first_candidate_payload["motif_role"])
        self.assertFalse(saw_split_child_candidate)

    def test_grcv3_rich_v4_carrier_site_split_child_inheriting_does_not_create_repeating_split_child_regime(
        self,
    ) -> None:
        anchored_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_PROBE,
            num_steps=12,
        )
        inheriting_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE,
            num_steps=12,
        )

        anchored_counts = _event_counts(anchored_run)
        inheriting_counts = _event_counts(inheriting_run)

        self.assertEqual(1, anchored_counts.get("spark_candidate", 0))
        self.assertEqual(1, anchored_counts.get("split_complete", 0))
        self.assertEqual(1, inheriting_counts.get("spark_candidate", 0))
        self.assertEqual(1, inheriting_counts.get("split_complete", 0))

        inheriting_seed = load_landscape_seed(
            _GRCV3_RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_PROBE
        )
        inheriting_params = resolve_grcv3_landscape_params(inheriting_seed)
        inheriting_model = build_grcv3_from_landscape_seed(
            inheriting_seed,
            params=inheriting_params,
            validate_seed=False,
        )
        inheriting_model.rebuild_basin_attributes()
        inheriting_model.rebuild_identity_state()

        first_candidate_payload = None
        saw_split_child_candidate = False
        for _ in range(12):
            step = inheriting_model.step()
            candidate_events = [event for event in step.events if event.kind == "spark_candidate"]
            if not candidate_events:
                continue
            for event in candidate_events:
                payload = inheriting_model.get_state().topology.node_payload(
                    int(event.payload["node_id"])
                )
                if first_candidate_payload is None:
                    first_candidate_payload = payload
                if payload.get("kind") == "split_child":
                    saw_split_child_candidate = True

        self.assertIsNotNone(first_candidate_payload)
        assert first_candidate_payload is not None
        self.assertEqual("basin_load_carrier", first_candidate_payload["motif_role"])
        self.assertFalse(saw_split_child_candidate)

    def test_grcv3_rich_v4_path_node_regime_is_not_portable_to_fan_in(
        self,
    ) -> None:
        mediated_direct_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_PROBE,
            num_steps=50,
        )
        mediated_single_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_PROBE,
            num_steps=50,
        )
        mediated_fan_in_run = run_grcv3_landscape_seed(
            _GRCV3_RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_PROBE,
            num_steps=50,
        )

        def _event_counts(run) -> dict[str, int]:
            counts: dict[str, int] = {}
            for step in run.step_results:
                for event in step.events:
                    counts[event.kind] = counts.get(event.kind, 0) + 1
            return counts

        mediated_direct_counts = _event_counts(mediated_direct_run)
        mediated_single_counts = _event_counts(mediated_single_run)
        mediated_fan_in_counts = _event_counts(mediated_fan_in_run)

        self.assertGreaterEqual(mediated_direct_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(mediated_single_counts.get("spark_candidate", 0), 1)
        self.assertGreaterEqual(mediated_single_counts.get("spark", 0), 1)
        self.assertEqual(0, mediated_fan_in_counts.get("spark_candidate", 0))
        self.assertEqual(0, mediated_fan_in_counts.get("spark", 0))


if __name__ == "__main__":
    unittest.main()
