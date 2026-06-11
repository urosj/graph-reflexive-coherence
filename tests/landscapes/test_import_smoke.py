"""Import smoke coverage for the Phase L landscape package boundary."""

from __future__ import annotations

import unittest


class LandscapeImportSmokeTest(unittest.TestCase):
    """Verify that the landscape package and its initial modules import cleanly."""

    def test_landscape_package_imports(self) -> None:
        import pygrc.landscapes
        import pygrc.landscapes.pde_translation
        import pygrc.landscapes.seed
        import pygrc.landscapes.validation

        self.assertIsNotNone(pygrc.landscapes)
        self.assertIsNotNone(pygrc.landscapes.pde_translation)
        self.assertIsNotNone(pygrc.landscapes.seed)
        self.assertIsNotNone(pygrc.landscapes.validation)

    def test_landscape_package_exports_module_surface(self) -> None:
        import pygrc.landscapes as landscapes

        self.assertIn("LandscapeSeed", landscapes.__all__)
        self.assertIn("BasinSeedPrimitive", landscapes.__all__)
        self.assertIn("TRANSLATION_MODE_LOSSLESS_SOURCE_NORMALIZATION", landscapes.__all__)
        self.assertIn("load_landscape_seed", landscapes.__all__)
        self.assertIn("save_landscape_seed", landscapes.__all__)
        self.assertIn("translate_pde_landscape_data", landscapes.__all__)
        self.assertIn("translate_pde_landscape_json", landscapes.__all__)
        self.assertIn("validate_pde_seed_translation_equivalence", landscapes.__all__)
        self.assertIn("validate_landscape_seed", landscapes.__all__)
        self.assertIn("pde_translation", landscapes.__all__)
        self.assertNotIn("seed", landscapes.__all__)
        self.assertNotIn("validation", landscapes.__all__)
        self.assertIsNotNone(landscapes.pde_translation)
        self.assertIsNotNone(landscapes.LandscapeSeed)
        self.assertIsNotNone(landscapes.load_landscape_seed)
        self.assertIsNotNone(landscapes.save_landscape_seed)
        self.assertIsNotNone(landscapes.translate_pde_landscape_data)
        self.assertIsNotNone(landscapes.translate_pde_landscape_json)
        self.assertIsNotNone(landscapes.validate_pde_seed_translation_equivalence)
        self.assertIsNotNone(landscapes.validate_landscape_seed)
