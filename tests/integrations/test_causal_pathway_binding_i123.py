"""Enforce the complete I123 binder provider DAG and ownership boundaries."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import ModuleType

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
import pygrc.causal_pathways.binding.artifacts as artifacts_api
import pygrc.causal_pathways.binding.session as session_api

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
LEGACY_PATH = BINDING_PACKAGE_PATH / "_legacy.py"
BINDING_CHECKER_PATH = (
    ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
)

PUBLIC_ARTIFACT_NAMES = {
    "EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT",
    "BindingLock",
    "BindingReceipt",
    "execution_transcript_digest",
    "unbound_execution_classification",
}
ARTIFACT_OWNERS = {
    "BindingLock",
    "BindingReceipt",
    "execution_transcript_digest",
    "unbound_execution_classification",
}
PRIVATE_ARTIFACT_DEFINITIONS = {
    "BindingArtifact",
    "_BoundComposition",
    "_BoundPathway",
    "_alternative_use_records",
    "_binding_record",
    "_candidate_graph_record",
    "_candidate_mechanism_invocation_records",
    "_composition_record",
    "_crossing_invocation_records",
    "_derive_claim_envelope",
    "_effect_outcome_summary",
    "_stage_invocation_records",
    "_use_graph",
    "build_binding_lock",
    "build_binding_receipt",
}
PUBLIC_SESSION_NAMES = {
    "EXECUTABLE_COMPOSITION_STATUSES",
    "BoundComposition",
    "BoundPathway",
    "PathwayBindingSession",
    "UnbindableCompositionError",
    "VerifiedCallable",
    "VerifiedCompositionCrossing",
}
SESSION_OWNERS = PUBLIC_SESSION_NAMES - {"EXECUTABLE_COMPOSITION_STATUSES"}
STATE_OWNER_FIELDS = {
    "_SessionPhaseState": {"value"},
    "_DeclarationState": {
        "alternatives",
        "candidate_mechanism_handles",
        "candidates",
        "composition_bindings",
        "pathway_bindings",
    },
    "_LinkState": {"crossing_runtime", "crossings", "instances", "symbols"},
    "_ArtifactState": {"candidate_uses", "lock"},
    "_IdentityCacheState": {
        "callable_identity_guards",
        "resolved_source_paths",
        "verified_source_files",
    },
}
FORMER_SESSION_FIELDS = {
    "_alternatives",
    "_callable_identity_guards",
    "_candidate_mechanism_handles",
    "_candidate_uses",
    "_candidates",
    "_composition_bindings",
    "_crossing_links",
    "_crossing_runtime_links",
    "_linked_instances",
    "_linked_symbols",
    "_lock",
    "_pathway_bindings",
    "_phase",
    "_resolved_source_paths",
    "_verified_source_files",
}


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


def _class_definition(path: Path, name: str) -> ast.ClassDef:
    return next(
        node
        for node in _syntax(path).body
        if isinstance(node, ast.ClassDef) and node.name == name
    )


def _class_field_names(path: Path, name: str) -> set[str]:
    return {
        node.target.id
        for node in _class_definition(path, name).body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }


def _class_method(path: Path, class_name: str, method_name: str) -> ast.FunctionDef:
    return next(
        node
        for node in _class_definition(path, class_name).body
        if isinstance(node, ast.FunctionDef) and node.name == method_name
    )


def _assigned_self_attributes(node: ast.AST) -> set[str]:
    attributes: set[str] = set()
    for assignment in ast.walk(node):
        targets: tuple[ast.expr, ...]
        if isinstance(assignment, ast.Assign):
            targets = tuple(assignment.targets)
        elif isinstance(assignment, ast.AnnAssign):
            targets = (assignment.target,)
        else:
            continue
        attributes.update(
            target.attr
            for target in targets
            if isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
        )
    return attributes


def _assert_owned_by(
    test: unittest.TestCase,
    module: ModuleType,
    names: set[str],
) -> None:
    for name in sorted(names):
        with test.subTest(name=name):
            test.assertEqual(module.__name__, getattr(module, name).__module__)


class CausalPathwayBindingI123Test(unittest.TestCase):
    """Keep the structurally complete binder modular and byte-compatible."""

    def test_complete_provider_dependency_dag_and_no_legacy_module(self) -> None:
        self.assertEqual(set(), _relative_imports(IDENTITY_PATH))
        self.assertEqual({"identity"}, _relative_imports(EFFECTS_PATH))
        self.assertEqual({"effects", "identity"}, _relative_imports(AUTHORITY_PATH))
        self.assertEqual({"authority", "identity"}, _relative_imports(CANDIDATES_PATH))
        self.assertEqual({"candidates", "identity"}, _relative_imports(SCOPES_PATH))
        self.assertEqual(
            {"authority", "candidates", "effects", "identity", "scopes"},
            _relative_imports(ARTIFACTS_PATH),
        )
        self.assertEqual(
            {"artifacts", "authority", "candidates", "effects", "identity", "scopes"},
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
        self.assertFalse(LEGACY_PATH.exists())

    def test_artifact_provider_owns_public_artifacts_and_serialization(self) -> None:
        self.assertEqual(PUBLIC_ARTIFACT_NAMES, set(artifacts_api.__all__))
        _assert_owned_by(self, artifacts_api, ARTIFACT_OWNERS)
        for name in sorted(PUBLIC_ARTIFACT_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(artifacts_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_artifact_derivation_is_session_independent_and_not_duplicated(
        self,
    ) -> None:
        self.assertTrue(
            PRIVATE_ARTIFACT_DEFINITIONS <= _top_level_definitions(ARTIFACTS_PATH)
        )
        self.assertTrue(
            PRIVATE_ARTIFACT_DEFINITIONS.isdisjoint(
                _top_level_definitions(SESSION_PATH)
            )
        )
        artifact_source = ARTIFACTS_PATH.read_text(encoding="utf-8")
        self.assertNotIn("PathwayBindingSession", artifact_source)
        session_source = SESSION_PATH.read_text(encoding="utf-8")
        for artifact_field in (
            '"claim_envelope"',
            '"lock_digest"',
            '"pathway_use_graph"',
            '"receipt_digest"',
        ):
            with self.subTest(artifact_field=artifact_field):
                self.assertNotIn(artifact_field, session_source)

    def test_session_provider_owns_handles_and_orchestration(self) -> None:
        self.assertEqual(PUBLIC_SESSION_NAMES, set(session_api.__all__))
        _assert_owned_by(self, session_api, SESSION_OWNERS)
        for name in sorted(PUBLIC_SESSION_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(session_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_session_mutable_state_has_cohesive_owners(self) -> None:
        for owner, fields in STATE_OWNER_FIELDS.items():
            with self.subTest(owner=owner):
                self.assertEqual(fields, _class_field_names(SESSION_PATH, owner))

        initializer = _class_method(SESSION_PATH, "PathwayBindingSession", "__init__")
        self.assertEqual(
            {
                "_artifacts",
                "_declarations",
                "_identity_cache",
                "_links",
                "_phase_state",
                "_runtime",
                "authority",
            },
            _assigned_self_attributes(initializer),
        )
        session = _class_definition(SESSION_PATH, "PathwayBindingSession")
        direct_attributes = {
            node.attr
            for node in ast.walk(session)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        }
        self.assertTrue(FORMER_SESSION_FIELDS.isdisjoint(direct_attributes))

    def test_lock_and_receipt_methods_delegate_canonical_construction(self) -> None:
        expected = {
            "freeze_lock": "build_binding_lock",
            "build_receipt": "build_binding_receipt",
        }
        for method_name, builder_name in expected.items():
            with self.subTest(method_name=method_name):
                method = _class_method(
                    SESSION_PATH, "PathwayBindingSession", method_name
                )
                calls = [
                    node.func.id
                    for node in ast.walk(method)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id.startswith("build_binding_")
                ]
                self.assertEqual([builder_name], calls)

    def test_independent_checker_does_not_import_production_derivations(self) -> None:
        imported_modules: set[str] = set()
        for node in ast.walk(_syntax(BINDING_CHECKER_PATH)):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)
        self.assertFalse(
            any(
                module.startswith("pygrc.causal_pathways")
                for module in imported_modules
            )
        )


if __name__ == "__main__":
    unittest.main()
