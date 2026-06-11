"""Phase 0 smoke tests for package bootstrap."""

from __future__ import annotations

import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class ImportSmokeTest(unittest.TestCase):
    """Verify that the Phase 0 package skeleton imports cleanly."""

    def test_package_imports(self) -> None:
        import pygrc
        import pygrc.core
        import pygrc.integrations
        import pygrc.landscapes
        import pygrc.models
        import pygrc.utils

        self.assertIsNotNone(pygrc)
        self.assertIsNotNone(pygrc.core)
        self.assertIsNotNone(pygrc.integrations)
        self.assertIsNotNone(pygrc.landscapes)
        self.assertIsNotNone(pygrc.models)
        self.assertIsNotNone(pygrc.utils)
