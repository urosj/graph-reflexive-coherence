"""Equivalence tests for PDE-to-seed translation invariants."""

from __future__ import annotations

import unittest

from pygrc.core import LandscapeTranslationEquivalenceError
from pygrc.landscapes import (
    translate_pde_landscape_data,
    validate_pde_seed_translation_equivalence,
)

try:
    from .pde_source_examples import (
        build_cell_like_source,
        build_explicit_plateau_and_saddle_source,
        build_periodic_source,
        build_routing_source,
    )
except ImportError:  # pragma: no cover - supports direct directory discovery.
    from pde_source_examples import (  # type: ignore[no-redef]
        build_cell_like_source,
        build_explicit_plateau_and_saddle_source,
        build_periodic_source,
        build_routing_source,
    )


class PDELandscapeEquivalenceTest(unittest.TestCase):
    """Validate seed-layer mathematical invariants against PDE source examples."""

    def test_equivalence_validator_accepts_cell_like_translation(self) -> None:
        source = build_cell_like_source()
        seed = translate_pde_landscape_data(
            source,
            source_reference="rc-sim/configs/landscapes/cell-like.json",
        )

        validate_pde_seed_translation_equivalence(
            source,
            seed,
            expected_source_reference="rc-sim/configs/landscapes/cell-like.json",
        )

    def test_equivalence_validator_accepts_routing_translation_without_enrichment(self) -> None:
        source = build_routing_source()
        seed = translate_pde_landscape_data(source)

        validate_pde_seed_translation_equivalence(source, seed)

    def test_equivalence_validator_accepts_periodic_translation(self) -> None:
        source = build_periodic_source()
        seed = translate_pde_landscape_data(source)

        validate_pde_seed_translation_equivalence(source, seed)

    def test_equivalence_validator_accepts_explicit_plateau_and_saddle_passthrough(self) -> None:
        source = build_explicit_plateau_and_saddle_source()
        seed = translate_pde_landscape_data(source)

        validate_pde_seed_translation_equivalence(source, seed)

    def test_equivalence_validator_rejects_primitive_geometry_drift(self) -> None:
        source = build_cell_like_source()
        seed = translate_pde_landscape_data(source)
        seed.primitives[0].chart_scale_hint["radius"] = 0.5

        with self.assertRaises(LandscapeTranslationEquivalenceError):
            validate_pde_seed_translation_equivalence(source, seed)

    def test_equivalence_validator_rejects_hidden_enrichment_in_lossless_mode(self) -> None:
        source = build_cell_like_source()
        seed = translate_pde_landscape_data(source)
        seed.primitives[0].type = "saddle"

        with self.assertRaises(LandscapeTranslationEquivalenceError):
            validate_pde_seed_translation_equivalence(source, seed)

    def test_equivalence_validator_rejects_transport_mapping_drift(self) -> None:
        source = build_routing_source()
        seed = translate_pde_landscape_data(source)
        seed.transport_intent[0].carrier_id = None

        with self.assertRaises(LandscapeTranslationEquivalenceError):
            validate_pde_seed_translation_equivalence(source, seed)


if __name__ == "__main__":
    unittest.main()
