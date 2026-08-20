"""Enforce the I121 candidate-provider and runtime-host boundary."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import ModuleType

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
import pygrc.causal_pathways.binding.candidates as candidates_api

ROOT = Path(__file__).resolve().parents[2]
BINDING_PACKAGE_PATH = ROOT / "src/pygrc/causal_pathways/binding"
FACADE_PATH = BINDING_PACKAGE_PATH / "__init__.py"
CANDIDATES_PATH = BINDING_PACKAGE_PATH / "candidates.py"
LEGACY_PATH = BINDING_PACKAGE_PATH / "_legacy.py"
FOCUSED_TEST_PATH = ROOT / "tests/integrations/test_causal_pathway_binding.py"

PUBLIC_CANDIDATE_NAMES = {
    "AUTHORITY_COORDINATES",
    "INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT",
    "CandidateDeclaration",
    "CandidateMechanismEvidence",
    "CandidateRelationReview",
    "CandidateUseRecord",
    "InvalidCandidateError",
}
CANDIDATE_CLASS_OWNERS = {
    "CandidateDeclaration",
    "CandidateMechanismEvidence",
    "CandidateRelationReview",
    "CandidateUseRecord",
    "InvalidCandidateError",
    "VerifiedCandidateMechanism",
}
PRIVATE_CANDIDATE_DEFINITIONS = {
    "_CandidateExecutionScope",
    "_CandidateMechanismEvent",
    "_CandidateRequestError",
    "_CandidateRequestFloat",
    "_CandidateRequestInt",
    "_CandidateRequestMapping",
    "_CandidateRequestStr",
    "_build_candidate_declaration",
    "_candidate_exercise_witness",
    "_candidate_request_payload",
    "_candidate_target_request_flow",
    "_claim_semantic_tokens",
    "_load_candidate_evidence_json",
    "_normalized_claim_text",
    "_resolve_candidate_symbol",
    "_restates_blocked_relabel",
    "_reviewed_candidate_dataflow_witness",
    "_safe_source_expression",
    "_safe_source_parameter_default",
    "_source_default_digest",
    "_source_default_payload",
    "_source_dependent_request_proof",
    "_source_parameter_default_contract",
}
CANDIDATE_HOST_METHODS = {
    "_assert_candidate_mechanism_invocation_allowed",
    "_callable_identity_guard",
    "_candidate_evidence_scope",
    "_candidate_mechanism",
    "_record_candidate_mechanism_event",
    "_runtime_object_flow",
}
R4_TO_R8_PRESSURE_TESTS = {
    "test_reviewed_cmp05_candidate_result_must_supply_target_request",
    "test_reviewed_cmp05_source_cannot_hide_in_unused_context",
    "test_reviewed_cmp05_syntactic_source_noop_cannot_form_edge",
    "test_reviewed_cmp05_source_omission_uses_frozen_default",
    "test_reviewed_cmp05_source_omission_preserves_tuple_type",
}
CANDIDATE_MUTATION_TESTS = {
    "test_candidate_alias_detection_ignores_forged_module_name",
    "test_candidate_rejects_cmp05_semantic_paraphrase",
    "test_candidate_rejects_metadata_only_mechanism_artifact",
    "test_candidate_rejects_stale_mechanism_content_address",
    "test_reviewed_cmp05_synonym_noop_cannot_form_candidate_edge",
}


def _syntax(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _top_level_definitions(path: Path) -> set[str]:
    return {
        node.name
        for node in _syntax(path).body
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
    }


def _top_level_assignments(path: Path) -> set[str]:
    names: set[str] = set()
    for node in _syntax(path).body:
        if isinstance(node, ast.Assign):
            names.update(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


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


def _class_method_names(path: Path, name: str) -> set[str]:
    return {
        node.name
        for node in _class_definition(path, name).body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }


def _assert_owned_by(
    test: unittest.TestCase,
    module: ModuleType,
    names: set[str],
) -> None:
    for name in sorted(names):
        with test.subTest(name=name):
            test.assertEqual(module.__name__, getattr(module, name).__module__)


class CausalPathwayBindingI121Test(unittest.TestCase):
    """Keep candidate proof semantics cohesive and session-independent."""

    def test_candidate_provider_is_acyclic_and_uses_a_structural_host(self) -> None:
        self.assertEqual(
            {"authority", "identity"},
            _relative_imports(CANDIDATES_PATH),
        )
        self.assertNotIn("_legacy", _relative_imports(CANDIDATES_PATH))
        host = _class_definition(CANDIDATES_PATH, "PathwayBindingSession")
        self.assertEqual(
            ["Protocol"],
            [base.id for base in host.bases if isinstance(base, ast.Name)],
        )
        self.assertEqual(
            CANDIDATE_HOST_METHODS,
            _class_method_names(CANDIDATES_PATH, "PathwayBindingSession"),
        )

    def test_candidate_provider_owns_public_candidate_objects(self) -> None:
        self.assertEqual(PUBLIC_CANDIDATE_NAMES, set(candidates_api.__all__))
        _assert_owned_by(self, candidates_api, CANDIDATE_CLASS_OWNERS)
        for name in sorted(PUBLIC_CANDIDATE_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(candidates_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_candidate_logic_is_absent_from_legacy_module(self) -> None:
        extracted = CANDIDATE_CLASS_OWNERS | PRIVATE_CANDIDATE_DEFINITIONS
        self.assertTrue(extracted <= _top_level_definitions(CANDIDATES_PATH))
        self.assertTrue(extracted.isdisjoint(_top_level_definitions(LEGACY_PATH)))
        legacy_assignments = _top_level_assignments(LEGACY_PATH)
        self.assertNotIn("AUTHORITY_COORDINATES", legacy_assignments)
        self.assertNotIn(
            "INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT",
            legacy_assignments,
        )

    def test_session_declaration_is_a_thin_candidate_factory_adapter(self) -> None:
        session = _class_definition(LEGACY_PATH, "PathwayBindingSession")
        declaration = next(
            node
            for node in session.body
            if isinstance(node, ast.FunctionDef) and node.name == "declare_candidate"
        )
        calls = {
            node.func.id
            for node in ast.walk(declaration)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertEqual({"_build_candidate_declaration"}, calls)
        attributes = {
            node.attr
            for node in ast.walk(declaration)
            if isinstance(node, ast.Attribute)
        }
        self.assertEqual(
            {
                "_candidate_mechanism_handles",
                "_candidates",
                "_require_declaration_phase",
                "authority",
            },
            attributes,
        )

    def test_focused_suite_retains_round_four_to_eight_pressures(self) -> None:
        focused_methods = _class_method_names(
            FOCUSED_TEST_PATH,
            "CausalPathwayBindingTest",
        )
        self.assertTrue(R4_TO_R8_PRESSURE_TESTS <= focused_methods)
        self.assertTrue(CANDIDATE_MUTATION_TESTS <= focused_methods)


if __name__ == "__main__":
    unittest.main()
