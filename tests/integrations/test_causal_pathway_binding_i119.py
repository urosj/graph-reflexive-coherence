"""Enforce the I119 binding-package and identity-provider boundary."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import ModuleType

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
import pygrc.causal_pathways.binding.identity as identity_api

ROOT = Path(__file__).resolve().parents[2]
BINDING_MODULE_PATH = ROOT / "src/pygrc/causal_pathways/binding.py"
BINDING_PACKAGE_PATH = ROOT / "src/pygrc/causal_pathways/binding"
FACADE_PATH = BINDING_PACKAGE_PATH / "__init__.py"
IDENTITY_PATH = BINDING_PACKAGE_PATH / "identity.py"
LEGACY_PATH = BINDING_PACKAGE_PATH / "_legacy.py"

PUBLIC_IDENTITY_NAMES = {
    "AuthorityDriftError",
    "CallableIdentity",
    "CausalPathwayBindingError",
    "CompositionCrossingBinding",
    "SourceSymbolBinding",
    "SymbolBindingError",
    "binding_semantics_digest",
    "binding_source_manifest_digest",
    "canonical_digest",
    "sha256_file",
}
PRIVATE_IDENTITY_NAMES = {
    "_CallableIdentityGuard",
    "_VerifiedSourceFile",
    "_callable_bound_owner",
    "_callable_definition",
    "_canonical_value_digest",
}
IDENTITY_NAMES = PUBLIC_IDENTITY_NAMES | PRIVATE_IDENTITY_NAMES


def _syntax(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _top_level_definitions(path: Path) -> set[str]:
    return {
        node.name
        for node in _syntax(path).body
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
    }


def _relative_imports(path: Path) -> set[str]:
    return {
        node.module or ""
        for node in ast.walk(_syntax(path))
        if isinstance(node, ast.ImportFrom) and node.level > 0
    }


def _assert_owned_by(
    test: unittest.TestCase,
    module: ModuleType,
    names: set[str],
) -> None:
    for name in sorted(names):
        with test.subTest(name=name):
            value = getattr(module, name)
            test.assertEqual(identity_api.__name__, value.__module__)


class CausalPathwayBindingI119Test(unittest.TestCase):
    """Keep the first modular boundary explicit and behaviorally compatible."""

    def test_binding_module_was_atomically_replaced_by_package(self) -> None:
        self.assertFalse(BINDING_MODULE_PATH.exists())
        self.assertTrue(FACADE_PATH.is_file())
        self.assertTrue(IDENTITY_PATH.is_file())
        self.assertTrue(LEGACY_PATH.is_file())
        self.assertEqual(FACADE_PATH.resolve(), Path(binding_api.__file__).resolve())

    def test_identity_is_a_session_independent_leaf_provider(self) -> None:
        self.assertEqual(set(), _relative_imports(IDENTITY_PATH))
        self.assertNotIn("PathwayBindingSession", IDENTITY_PATH.read_text())
        self.assertTrue(IDENTITY_NAMES <= _top_level_definitions(IDENTITY_PATH))
        self.assertTrue(
            IDENTITY_NAMES.isdisjoint(_top_level_definitions(LEGACY_PATH))
        )
        self.assertIn("identity", _relative_imports(LEGACY_PATH))

    def test_public_identity_exports_are_owned_by_identity_provider(self) -> None:
        self.assertEqual(PUBLIC_IDENTITY_NAMES, set(identity_api.__all__))
        _assert_owned_by(self, identity_api, PUBLIC_IDENTITY_NAMES)
        for name in sorted(PUBLIC_IDENTITY_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(identity_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_compatibility_facade_preserves_complete_public_surface(self) -> None:
        self.assertEqual(public_api.__all__, binding_api.__all__)
        for name in public_api.__all__:
            with self.subTest(name=name):
                self.assertIs(getattr(public_api, name), getattr(binding_api, name))

    def test_tests_no_longer_patch_private_monolith_hooks(self) -> None:
        self.assertFalse(hasattr(binding_api, "_load_json"))
        self.assertFalse(hasattr(binding_api, "inspect"))
        focused_source = (
            ROOT / "tests/integrations/test_causal_pathway_binding.py"
        ).read_text(encoding="utf-8")
        private_load_hook = "causal_pathways.binding" + "._load_json"
        private_inspect_hook = "binding_module" + ".inspect"
        self.assertNotIn(private_load_hook, focused_source)
        self.assertNotIn(private_inspect_hook, focused_source)


if __name__ == "__main__":
    unittest.main()
