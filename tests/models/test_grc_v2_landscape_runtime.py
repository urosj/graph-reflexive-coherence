"""Runtime tests for seed-driven GRCV2 construction, families, and replay."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_SADDLE,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
)
from pygrc.models import (
    build_grcv2_from_landscape_family,
    get_grcv2_landscape_param_family,
    project_landscape_seed_to_grcv2_state,
    resolve_grcv2_landscape_params,
    run_grcv2_landscape_seed,
)


_ROOT = Path(__file__).resolve().parents[2]
_CELL1_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-1.seed.yaml"
_CELL4_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-4.seed.yaml"


def _transport_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="transport", source_kind="unit"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=1.0,
            kappa_c=1.0,
            dt=0.1,
            budget_b=10.0,
            potential=SeedPotential(type="double_well", params={"a": 1.0, "b": 1.2}),
        ),
        primitives=[
            BasinSeedPrimitive(id="a", coherence_prior=2.0),
            BasinSeedPrimitive(id="b", coherence_prior=3.0),
            ValleySeedPrimitive(id="channel", from_id="a", to_id="b", coherence_prior=0.5),
        ],
        transport_intent=[
            SeedTransportIntent(
                id="intent",
                mode="directed_bias",
                sources=["a"],
                targets=["b"],
                carrier_id="channel",
                magnitude_hint=0.5,
                priority=0.25,
            )
        ],
    )


def _plateau_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="plateau", source_kind="unit"),
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
                id="plateau_core",
                coherence_prior=1.0,
                hosted_primitive_ids=["inner_basin", "routing"],
            ),
            BasinSeedPrimitive(
                id="inner_basin",
                parent_id="plateau_core",
                coherence_prior=2.0,
            ),
            JunctionSeedPrimitive(
                id="routing",
                type=PRIMITIVE_SADDLE,
                host_id=None,
                branch_target_ids=["inner_basin"],
                coherence_prior=0.5,
                chart_center_hint=[0.5, 0.5],
            ),
            ValleySeedPrimitive(
                id="channel",
                from_id="routing",
                to_id="inner_basin",
                coherence_prior=0.25,
            ),
        ],
    )


class GRCV2LandscapeRuntimeTest(unittest.TestCase):
    """Validate Iterations 3-7 of the Phase L1 runtime path."""

    def test_projected_state_for_cell1_has_budget_and_support_edge(self) -> None:
        params = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="balanced_baseline")
        state = project_landscape_seed_to_grcv2_state(_CELL1_SEED, params=params)

        self.assertEqual(2, len(tuple(state.topology.iter_live_node_ids())))
        self.assertEqual(1, len(tuple(state.topology.iter_live_edge_ids())))
        self.assertAlmostEqual(sum(state.nodes.values()), state.budget_target)
        self.assertEqual("sum_of_node_priors", state.cached_quantities["landscape_budget_mode"])
        self.assertEqual(
            ["plasma_membrane"],
            state.cached_quantities["landscape_metadata_only_ridge_ids"],
        )

    def test_projected_state_for_cell4_has_expected_connected_runtime_surface(self) -> None:
        params = resolve_grcv2_landscape_params(_CELL4_SEED, family_name="balanced_baseline")
        state = project_landscape_seed_to_grcv2_state(_CELL4_SEED, params=params)

        self.assertEqual(6, len(tuple(state.topology.iter_live_node_ids())))
        self.assertEqual(9, len(tuple(state.topology.iter_live_edge_ids())))
        self.assertIn("routing_junction", state.cached_quantities["landscape_node_id_by_primitive_id"])
        self.assertIn(
            "channel_junction_to_mito1",
            state.cached_quantities["landscape_edge_id_by_primitive_id"],
        )

    def test_transport_intent_biases_initial_edge_weight_without_setting_flux(self) -> None:
        seed = _transport_seed()
        params = resolve_grcv2_landscape_params(seed, family_name="balanced_baseline")
        state = project_landscape_seed_to_grcv2_state(seed, params=params)

        edge_id = next(iter(state.topology.iter_live_edge_ids()))
        self.assertGreater(state.edges[edge_id], 0.5)
        self.assertEqual({}, state.flux)
        self.assertEqual(
            "carrier_edge_weight_multiplier",
            state.cached_quantities["landscape_transport_bias_mode"],
        )
        self.assertAlmostEqual(
            state.topology.edge_payload(edge_id)["landscape_base_conductance"] * 1.75,
            state.edges[edge_id],
        )
        self.assertEqual(1.75, state.topology.edge_payload(edge_id)["transport_intent_multiplier"])
        self.assertAlmostEqual(
            2.0,
            state.cached_quantities["landscape_mass_scale"],
        )

    def test_projection_adds_explicit_plateau_containment_and_hostless_junction_flags(self) -> None:
        seed = _plateau_seed()
        params = resolve_grcv2_landscape_params(seed, family_name="balanced_baseline")
        state = project_landscape_seed_to_grcv2_state(seed, params=params)

        node_ids = state.cached_quantities["landscape_node_id_by_primitive_id"]
        plateau_payload = state.topology.node_payload(node_ids["plateau_core"])
        routing_payload = state.topology.node_payload(node_ids["routing"])

        self.assertEqual(
            ["inner_basin", "routing"],
            plateau_payload["contained_primitive_ids"],
        )
        self.assertEqual(
            [node_ids["inner_basin"], node_ids["routing"]],
            plateau_payload["contained_node_ids"],
        )
        self.assertIsNone(routing_payload["parent_id"])
        self.assertTrue(routing_payload["is_hostless"])
        self.assertEqual("standalone", routing_payload["junction_anchor_mode"])

    def test_projection_rejects_invalid_seed_even_when_validation_is_disabled(self) -> None:
        seed = LandscapeSeed(
            seed_schema="pygrc.landscape_seed",
            seed_version="0.1",
            meta=SeedDocumentMeta(name="cycle", source_kind="unit"),
            constitutive_profile=SeedConstitutiveProfile(
                lambda_c=1.0,
                xi_c=1.0,
                zeta_c=1.0,
                kappa_c=1.0,
                dt=0.1,
                potential=SeedPotential(type="double_well"),
            ),
            primitives=[
                BasinSeedPrimitive(id="a", parent_id="b", coherence_prior=1.0),
                BasinSeedPrimitive(id="b", parent_id="a", coherence_prior=1.0),
            ],
        )
        params = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="balanced_baseline")

        with self.assertRaises(InvalidLandscapeSeedError):
            project_landscape_seed_to_grcv2_state(seed, params=params, validate_seed=False)

    def test_projection_rejects_duplicate_primitive_ids_even_when_validation_is_disabled(
        self,
    ) -> None:
        seed = LandscapeSeed(
            seed_schema="pygrc.landscape_seed",
            seed_version="0.1",
            meta=SeedDocumentMeta(name="duplicate", source_kind="unit"),
            constitutive_profile=SeedConstitutiveProfile(
                lambda_c=1.0,
                xi_c=1.0,
                zeta_c=1.0,
                kappa_c=1.0,
                dt=0.1,
                potential=SeedPotential(type="double_well"),
            ),
            primitives=[
                BasinSeedPrimitive(id="dup", coherence_prior=1.0),
                BasinSeedPrimitive(id="dup", coherence_prior=2.0),
            ],
        )
        params = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="balanced_baseline")

        with self.assertRaises(InvalidLandscapeSeedError):
            project_landscape_seed_to_grcv2_state(seed, params=params, validate_seed=False)

    def test_param_family_resolution_uses_seed_constitutive_profile_and_distinguishes_families(
        self,
    ) -> None:
        quiet = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="quiet_conservative")
        hot = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="hot_exploratory")
        balanced = get_grcv2_landscape_param_family("balanced_baseline")

        self.assertEqual(0.001, quiet.dt)
        self.assertEqual(0.001, hot.dt)
        self.assertNotEqual(
            quiet.evolution["lambda_birth"],
            hot.evolution["lambda_birth"],
        )
        self.assertEqual("balanced_baseline", balanced.name)

    def test_runner_executes_cell1_and_cell4_for_multiple_steps(self) -> None:
        cell1_run = run_grcv2_landscape_seed(
            _CELL1_SEED,
            family_name="balanced_baseline",
            rng_seed=7,
            num_steps=3,
        )
        cell4_run = run_grcv2_landscape_seed(
            _CELL4_SEED,
            family_name="balanced_baseline",
            rng_seed=7,
            num_steps=3,
        )

        self.assertEqual(3, len(cell1_run.step_results))
        self.assertEqual(3, len(cell4_run.step_results))
        self.assertIsNotNone(cell1_run.telemetry)
        self.assertIsNotNone(cell4_run.telemetry)
        assert cell4_run.telemetry is not None
        self.assertEqual(3, len(cell4_run.telemetry.step_rows))
        self.assertEqual(
            cell4_run.telemetry.run_summary.completed_steps,
            len(cell4_run.step_results),
        )
        self.assertIsNone(cell4_run.telemetry.artifact_layout)
        self.assertEqual(3, cell1_run.model.get_state().step_index)
        self.assertEqual(3, cell4_run.model.get_state().step_index)
        self.assertGreaterEqual(cell4_run.final_observables["num_edges"], 1)
        self.assertNotEqual(
            cell4_run.initial_observables["average_conductance"],
            cell4_run.final_observables["average_conductance"],
        )

    def test_fixed_seed_and_family_replay_is_deterministic(self) -> None:
        first = run_grcv2_landscape_seed(
            _CELL4_SEED,
            family_name="balanced_baseline",
            rng_seed=11,
            num_steps=4,
        )
        second = run_grcv2_landscape_seed(
            _CELL4_SEED,
            family_name="balanced_baseline",
            rng_seed=11,
            num_steps=4,
        )

        self.assertEqual(first.final_observables, second.final_observables)
        self.assertEqual(
            [result.observables for result in first.step_results],
            [result.observables for result in second.step_results],
        )
        self.assertEqual(
            [len(result.events) for result in first.step_results],
            [len(result.events) for result in second.step_results],
        )
        assert first.telemetry is not None
        assert second.telemetry is not None
        self.assertEqual(first.telemetry.identity.run_id, second.telemetry.identity.run_id)
        self.assertEqual(
            [row.observables for row in first.telemetry.step_rows],
            [row.observables for row in second.telemetry.step_rows],
        )

    def test_runner_can_write_telemetry_artifacts_without_changing_runtime_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run = run_grcv2_landscape_seed(
                _CELL1_SEED,
                family_name="balanced_baseline",
                rng_seed=13,
                num_steps=2,
                telemetry_root=Path(temp_dir) / "outputs",
                telemetry_experiment_path=Path("grcv2") / "runtime-smoke" / "cell-1",
            )

            assert run.telemetry is not None
            self.assertIsNotNone(run.telemetry.artifact_layout)
            layout = run.telemetry.artifact_layout
            assert layout is not None
            self.assertEqual(
                Path(temp_dir)
                / "outputs"
                / "grcv2"
                / "runtime-smoke"
                / "cell-1",
                layout.root_dir,
            )
            loaded_pack = telemetry.load_telemetry_artifact_pack(layout)

        self.assertEqual(2, len(loaded_pack.step_rows))
        self.assertEqual(
            loaded_pack.run_summary.final_observables,
            run.telemetry.run_summary.final_observables,
        )

    def test_projected_model_save_load_roundtrip_preserves_runtime_progression(self) -> None:
        model = build_grcv2_from_landscape_family(
            _CELL4_SEED,
            family_name="balanced_baseline",
            rng_seed=5,
        )
        model.step()
        model.step()

        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot_path = Path(temp_dir) / "projected-grcv2.json"
            model.save(str(snapshot_path))
            restored = model.__class__.load(str(snapshot_path))

        self.assertEqual(model.get_state().step_index, restored.get_state().step_index)
        self.assertEqual(model.get_state().nodes, restored.get_state().nodes)
        self.assertEqual(model.get_state().edges, restored.get_state().edges)
        self.assertEqual(
            tuple(model.get_state().topology.iter_live_edge_ids()),
            tuple(restored.get_state().topology.iter_live_edge_ids()),
        )
