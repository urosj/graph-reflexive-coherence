"""Import and boundary smoke tests for the GRCV2 landscape projector module."""

from __future__ import annotations

from pathlib import Path
import unittest

from pygrc.core import GRCParams
from pygrc.landscapes import LandscapeSeed
from pygrc.models import (
    GRCV2LandscapeBlueprint,
    GRCV2LandscapeParamFamily,
    GRCV2LandscapeProjectionRequest,
    GRCV2LandscapeRunResult,
    build_grcv2_from_landscape_family,
    build_grcv2_from_landscape_seed,
    get_grcv2_landscape_param_family,
    list_grcv2_landscape_param_families,
    prepare_grcv2_landscape_projection,
    realize_grcv2_landscape_blueprint,
    project_landscape_seed_to_grcv2_state,
    resolve_grcv2_landscape_params,
    run_grcv2_landscape_seed,
)


_ROOT = Path(__file__).resolve().parents[2]
_CELL1_SEED = _ROOT / "configs" / "landscapes" / "seed" / "cell-1.seed.yaml"


def _valid_grcv2_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "eta": 1.0,
            "kappa_c": 1.0,
            "lambda_c": 1.0,
            "xi_c": 1.0,
            "zeta_c": 1.0,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0},
            "eps_spark": 0.01,
            "tau_split": 2.0,
            "lambda_birth": 0.25,
            "alpha_seed": 0.5,
            "eps_prune": 0.001,
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRCV2LandscapeImportSmokeTest(unittest.TestCase):
    """Verify the family-local projector boundary imports and normalizes inputs."""

    def test_models_package_exports_grcv2_landscape_boundary(self) -> None:
        import pygrc.models as models
        import pygrc.models.grc_v2_landscape as grc_v2_landscape

        self.assertIn("GRCV2LandscapeProjectionRequest", models.__all__)
        self.assertIn("GRCV2LandscapeBlueprint", models.__all__)
        self.assertIn("GRCV2LandscapeParamFamily", models.__all__)
        self.assertIn("GRCV2LandscapeRunResult", models.__all__)
        self.assertIn("prepare_grcv2_landscape_projection", models.__all__)
        self.assertIn("realize_grcv2_landscape_blueprint", models.__all__)
        self.assertIn("project_landscape_seed_to_grcv2_state", models.__all__)
        self.assertIn("resolve_grcv2_landscape_params", models.__all__)
        self.assertIn("list_grcv2_landscape_param_families", models.__all__)
        self.assertIn("get_grcv2_landscape_param_family", models.__all__)
        self.assertIn("build_grcv2_from_landscape_family", models.__all__)
        self.assertIn("build_grcv2_from_landscape_seed", models.__all__)
        self.assertIn("run_grcv2_landscape_seed", models.__all__)
        self.assertIsNotNone(grc_v2_landscape)
        self.assertIsNotNone(models.GRCV2LandscapeProjectionRequest)
        self.assertIsNotNone(models.GRCV2LandscapeBlueprint)
        self.assertIsNotNone(models.GRCV2LandscapeParamFamily)
        self.assertIsNotNone(models.GRCV2LandscapeRunResult)
        self.assertIsNotNone(models.prepare_grcv2_landscape_projection)
        self.assertIsNotNone(models.realize_grcv2_landscape_blueprint)
        self.assertIsNotNone(models.project_landscape_seed_to_grcv2_state)
        self.assertIsNotNone(models.resolve_grcv2_landscape_params)
        self.assertIsNotNone(models.list_grcv2_landscape_param_families)
        self.assertIsNotNone(models.get_grcv2_landscape_param_family)
        self.assertIsNotNone(models.build_grcv2_from_landscape_family)
        self.assertIsNotNone(models.build_grcv2_from_landscape_seed)
        self.assertIsNotNone(models.run_grcv2_landscape_seed)

    def test_prepare_projection_accepts_seed_path_and_valid_grcv2_config(self) -> None:
        request = prepare_grcv2_landscape_projection(
            _CELL1_SEED,
            params=_valid_grcv2_config(),
        )

        self.assertIsInstance(request, GRCV2LandscapeProjectionRequest)
        self.assertIsInstance(request.seed, LandscapeSeed)
        self.assertIsInstance(request.params, GRCParams)
        self.assertEqual(_CELL1_SEED, request.seed_path)

    def test_prepare_projection_accepts_runtime_seed_and_params_object(self) -> None:
        first_request = prepare_grcv2_landscape_projection(
            _CELL1_SEED,
            params=_valid_grcv2_config(),
        )

        second_request = prepare_grcv2_landscape_projection(
            first_request.seed,
            params=first_request.params,
        )

        self.assertIs(first_request.seed, second_request.seed)
        self.assertIs(first_request.params, second_request.params)
        self.assertIsNone(second_request.seed_path)

    def test_projection_and_build_entry_points_remain_explicitly_deferred(self) -> None:
        blueprint = realize_grcv2_landscape_blueprint(_CELL1_SEED)

        self.assertIsInstance(blueprint, GRCV2LandscapeBlueprint)

        state = project_landscape_seed_to_grcv2_state(
            _CELL1_SEED,
            params=_valid_grcv2_config(),
        )
        model = build_grcv2_from_landscape_seed(
            _CELL1_SEED,
            params=_valid_grcv2_config(),
        )

        self.assertGreaterEqual(len(state.nodes), 1)
        self.assertGreaterEqual(len(tuple(state.topology.iter_live_node_ids())), 1)
        self.assertGreaterEqual(len(tuple(model.get_state().topology.iter_live_node_ids())), 1)

    def test_param_family_surface_and_runner_imports_are_executable(self) -> None:
        family_names = list_grcv2_landscape_param_families()
        family = get_grcv2_landscape_param_family("balanced_baseline")
        params = resolve_grcv2_landscape_params(_CELL1_SEED, family_name="balanced_baseline")
        model = build_grcv2_from_landscape_family(
            _CELL1_SEED,
            family_name="balanced_baseline",
        )
        run = run_grcv2_landscape_seed(
            _CELL1_SEED,
            family_name="balanced_baseline",
            num_steps=1,
        )

        self.assertIn("balanced_baseline", family_names)
        self.assertIsInstance(family, GRCV2LandscapeParamFamily)
        self.assertIsNotNone(params.params_hash)
        self.assertIsNotNone(model.get_state())
        self.assertIsInstance(run, GRCV2LandscapeRunResult)
