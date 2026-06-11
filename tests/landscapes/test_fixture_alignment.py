"""Canonical fixture verification for PDE-to-seed translation."""

from __future__ import annotations

import unittest
from pathlib import Path

from pygrc.landscapes import (
    landscape_seed_to_data,
    load_landscape_seed,
    translate_pde_landscape_data,
)

try:
    from .pde_source_examples import (
        build_fixture_cell1_source,
        build_fixture_cell4_source,
        build_fixture_s6_source,
    )
except ImportError:  # pragma: no cover - supports direct directory discovery.
    from pde_source_examples import (  # type: ignore[no-redef]
        build_fixture_cell1_source,
        build_fixture_cell4_source,
        build_fixture_s6_source,
    )


_FIXTURE_DIR = Path("configs/landscapes/seed")


class LandscapeFixtureAlignmentTest(unittest.TestCase):
    """Verify translator output against canonical normalized seed fixtures."""

    def _assert_fixture_matches_translation(
        self,
        fixture_name: str,
        source: dict[str, object],
        *,
        source_reference: str,
    ) -> None:
        fixture = load_landscape_seed(_FIXTURE_DIR / fixture_name)
        translated = translate_pde_landscape_data(source, source_reference=source_reference)

        self.assertEqual(
            landscape_seed_to_data(fixture),
            landscape_seed_to_data(translated),
        )

    def test_cell1_fixture_matches_translation(self) -> None:
        self._assert_fixture_matches_translation(
            "cell-1.seed.yaml",
            build_fixture_cell1_source(),
            source_reference="rc-sim/configs/landscapes/cell-1.json",
        )

    def test_cell4_fixture_matches_translation(self) -> None:
        self._assert_fixture_matches_translation(
            "cell-4.seed.yaml",
            build_fixture_cell4_source(),
            source_reference="rc-sim/configs/landscapes/cell-4.json",
        )

    def test_s6_fixture_matches_translation(self) -> None:
        self._assert_fixture_matches_translation(
            "s6-periodic-seam-ring.seed.yaml",
            build_fixture_s6_source(),
            source_reference="rc-sim/configs/landscapes/s6-periodic-seam-ring.json",
        )


if __name__ == "__main__":
    unittest.main()
