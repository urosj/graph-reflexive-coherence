"""Contract tests for the shared parameter architecture."""

from __future__ import annotations

from types import MappingProxyType
import unittest

from pygrc.core import CORE_PARAM_DOMAINS, EXCLUDED_PARAM_DOMAINS, GRCParams


class ParamsContractTest(unittest.TestCase):
    """Validate the Phase 1 parameter contract surface."""

    def test_from_mapping_builds_immutable_core_params(self) -> None:
        params = GRCParams.from_mapping(
            {
                "dt": 0.25,
                "evolution": {"alpha": 1.0},
                "constitutive_semantic_modes": {
                    "frame_mode": "induced_local_frame"
                },
                "numerical_backend": {"regularization": 1e-9},
            }
        )

        self.assertIsInstance(params.evolution, MappingProxyType)
        self.assertIsInstance(params.constitutive_semantic_modes, MappingProxyType)
        self.assertIsInstance(params.numerical_backend, MappingProxyType)

        with self.assertRaises(TypeError):
            params.evolution["alpha"] = 2.0  # type: ignore[index]

    def test_raw_config_and_resolved_config_are_distinct(self) -> None:
        params = GRCParams.from_mapping(
            {
                "dt": 1,
                "evolution": {"alpha": 1},
            }
        )

        self.assertEqual(1, params.raw_config["dt"])
        self.assertEqual(1.0, params.resolved_config["dt"])
        self.assertEqual(1, params.raw_config["evolution"]["alpha"])
        self.assertEqual(1, params.resolved_config["evolution"]["alpha"])

    def test_core_param_hash_is_stable_for_equivalent_mappings(self) -> None:
        left = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "boundary_mode": "ghost",
                    "frame_mode": "combinatorial",
                },
                "evolution": {"beta": 2.0, "alpha": 1.0},
            }
        )
        right = GRCParams.from_mapping(
            {
                "evolution": {"alpha": 1.0, "beta": 2.0},
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "frame_mode": "combinatorial",
                    "boundary_mode": "ghost",
                },
            }
        )

        self.assertEqual(left.canonical_identity(), right.canonical_identity())

    def test_excluded_domains_are_rejected_from_core_params(self) -> None:
        for domain in EXCLUDED_PARAM_DOMAINS:
            with self.subTest(domain=domain):
                with self.assertRaises(ValueError):
                    GRCParams.from_mapping({"dt": 0.1, domain: {"enabled": True}})

    def test_core_domains_are_exposed_centrally(self) -> None:
        self.assertEqual(
            ("evolution", "constitutive_semantic_modes", "numerical_backend"),
            CORE_PARAM_DOMAINS,
        )
