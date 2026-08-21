"""Enforce the I120 effect and authority provider boundaries."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, cast

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
import pygrc.causal_pathways.binding.authority as authority_api
import pygrc.causal_pathways.binding.effects as effects_api

ROOT = Path(__file__).resolve().parents[2]
BINDING_PACKAGE_PATH = ROOT / "src/pygrc/causal_pathways/binding"
FACADE_PATH = BINDING_PACKAGE_PATH / "__init__.py"
IDENTITY_PATH = BINDING_PACKAGE_PATH / "identity.py"
EFFECTS_PATH = BINDING_PACKAGE_PATH / "effects.py"
AUTHORITY_PATH = BINDING_PACKAGE_PATH / "authority.py"
CANDIDATES_PATH = BINDING_PACKAGE_PATH / "candidates.py"
SCOPES_PATH = BINDING_PACKAGE_PATH / "scopes.py"
ARTIFACTS_PATH = BINDING_PACKAGE_PATH / "artifacts.py"
SESSION_PATH = BINDING_PACKAGE_PATH / "session.py"
ACCEPTANCE_ANCHOR_PATH = (
    ROOT / "implementation/evidence/causal-pathway-binding/"
    "binding-acceptance-anchor.json"
)
TRUSTED_ACCEPTANCE_ANCHOR_DIGEST = (
    "127382ebd0b8f70a5990971190bec5de614f39f03b47c7ffaffe4f53e5970ae2"
)

PUBLIC_EFFECT_NAMES = {
    "CLAIM_QUALIFYING_EFFECT_OUTCOMES",
    "EFFECT_OUTCOMES",
    "RETURN_CATEGORIES",
    "EffectOutcomeContract",
}
PRIVATE_EFFECT_DEFINITIONS = {
    "_EffectContractProvider",
    "_classify_returned_effect",
    "_return_category",
}
PUBLIC_AUTHORITY_NAMES = {
    "BindingAcceptanceAnchor",
    "CausalPathwayAuthority",
    "UnknownCompositionError",
    "UnknownPathwayError",
}
PRIVATE_AUTHORITY_DEFINITIONS = {"_index_unique", "_load_json"}


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
            test.assertEqual(module.__name__, value.__module__)


class CausalPathwayBindingI120Test(unittest.TestCase):
    """Keep effects and authority acyclic, cohesive, and behaviorally stable."""

    def test_permanent_provider_dependency_graph_is_acyclic(self) -> None:
        self.assertEqual(set(), _relative_imports(IDENTITY_PATH))
        self.assertEqual({"identity"}, _relative_imports(EFFECTS_PATH))
        self.assertEqual({"effects", "identity"}, _relative_imports(AUTHORITY_PATH))
        self.assertEqual(
            {"authority", "identity"},
            _relative_imports(CANDIDATES_PATH),
        )
        self.assertEqual(
            {"candidates", "identity"},
            _relative_imports(SCOPES_PATH),
        )
        self.assertEqual(
            {"authority", "candidates", "effects", "identity", "scopes"},
            _relative_imports(ARTIFACTS_PATH),
        )
        self.assertEqual(
            {
                "artifacts",
                "authority",
                "candidates",
                "effects",
                "identity",
                "scopes",
            },
            _relative_imports(SESSION_PATH),
        )
        self.assertEqual(
            {
                "artifacts",
                "authority",
                "candidates",
                "effects",
                "identity",
                "scopes",
                "session",
            },
            _relative_imports(FACADE_PATH),
        )
        self.assertNotIn("PathwayBindingSession", EFFECTS_PATH.read_text())
        self.assertNotIn("PathwayBindingSession", AUTHORITY_PATH.read_text())

    def test_effect_provider_owns_its_public_and_private_behavior(self) -> None:
        self.assertEqual(PUBLIC_EFFECT_NAMES, set(effects_api.__all__))
        _assert_owned_by(self, effects_api, {"EffectOutcomeContract"})
        self.assertTrue(
            PRIVATE_EFFECT_DEFINITIONS <= _top_level_definitions(EFFECTS_PATH)
        )
        for name in sorted(PUBLIC_EFFECT_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(effects_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_authority_provider_owns_admission_and_lookup(self) -> None:
        self.assertEqual(PUBLIC_AUTHORITY_NAMES, set(authority_api.__all__))
        _assert_owned_by(self, authority_api, PUBLIC_AUTHORITY_NAMES)
        self.assertTrue(
            PRIVATE_AUTHORITY_DEFINITIONS <= _top_level_definitions(AUTHORITY_PATH)
        )
        for name in sorted(PUBLIC_AUTHORITY_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(authority_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_extracted_definitions_are_absent_from_session_module(self) -> None:
        extracted = (
            {"EffectOutcomeContract"}
            | PRIVATE_EFFECT_DEFINITIONS
            | PUBLIC_AUTHORITY_NAMES
            | PRIVATE_AUTHORITY_DEFINITIONS
        )
        self.assertTrue(extracted.isdisjoint(_top_level_definitions(SESSION_PATH)))
        session_source = SESSION_PATH.read_text(encoding="utf-8")
        self.assertNotIn("RETURN_CATEGORIES:", session_source)
        self.assertNotIn("AUTHORITY_PATHS:", session_source)

    def test_loaded_authority_state_is_read_only_and_defensively_returned(
        self,
    ) -> None:
        anchor_record = json.loads(ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8"))
        authority = authority_api.CausalPathwayAuthority.load(
            ROOT,
            acceptance_anchor=anchor_record,
            trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
        )
        for attribute in (
            "_documents",
            "_pathways",
            "_compositions",
            "_stage_symbols",
            "_composition_crossings",
        ):
            with self.subTest(attribute=attribute):
                self.assertIsInstance(getattr(authority, attribute), MappingProxyType)

        pathway_id = "lgrc9v3.explicit_packet_transport"
        pathway = cast(dict[str, Any], authority.pathway(pathway_id))
        pathway.clear()
        self.assertTrue(authority.pathway(pathway_id))

        composition = cast(dict[str, Any], authority.composition("CMP-20"))
        composition.clear()
        self.assertTrue(authority.composition("CMP-20"))

        identities = authority.artifact_identities()
        with self.assertRaises(TypeError):
            identities["registry_digest"] = "0" * 64  # type: ignore[index]

        anchor = authority_api.BindingAcceptanceAnchor.from_record(
            anchor_record,
            trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
        )
        copied_record = anchor.to_record()
        copied_record["status"] = "rejected"
        self.assertEqual("accepted", anchor.to_record()["status"])


if __name__ == "__main__":
    unittest.main()
