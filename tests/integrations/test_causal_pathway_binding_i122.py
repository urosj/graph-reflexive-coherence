"""Enforce the I122 runtime-scope provider and state-owner boundary."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import ModuleType

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
import pygrc.causal_pathways.binding.scopes as scopes_api

ROOT = Path(__file__).resolve().parents[2]
BINDING_PACKAGE_PATH = ROOT / "src/pygrc/causal_pathways/binding"
SCOPES_PATH = BINDING_PACKAGE_PATH / "scopes.py"
SESSION_PATH = BINDING_PACKAGE_PATH / "session.py"
FOCUSED_TEST_PATH = ROOT / "tests/integrations/test_causal_pathway_binding.py"

PUBLIC_SCOPE_NAMES = {
    "ATTESTED_OBJECT_FLOW_DATAFLOW",
    "AllowedPathwayAlternatives",
    "AlternativeSelectionScope",
    "BindingStateError",
    "CandidateExecutionScope",
    "CompositionExecutionScope",
    "CrossingInvocationRecord",
    "CrossingResultReference",
    "FlowDerivedInstanceReference",
    "InvocationRecord",
    "composition_dataflow_contract",
}
SCOPE_CLASS_OWNERS = {
    "AllowedPathwayAlternatives",
    "AlternativeSelectionScope",
    "BindingStateError",
    "CandidateExecutionScope",
    "CompositionExecutionScope",
    "CrossingInvocationRecord",
    "CrossingResultReference",
    "FlowDerivedInstanceReference",
    "InvocationRecord",
}
EXTRACTED_SCOPE_DEFINITIONS = SCOPE_CLASS_OWNERS | {
    "CandidateMechanismInvocationRecord",
    "_BindingLock",
    "_BoundComposition",
    "_BoundPathway",
    "_RuntimeScopeHost",
    "_RuntimeScopeState",
    "composition_dataflow_contract",
}
RUNTIME_STATE_FIELDS = {
    "_active_alternative_selection_scope",
    "_active_candidate_scope",
    "_active_composition_scope",
    "_alternative_selection_scopes",
    "_candidate_mechanism_invocations",
    "_candidate_scopes",
    "_composition_scopes",
    "_crossing_invocations",
    "_direct_runtime_instances",
    "_execution_event_count",
    "_invocation_results",
    "_invocations",
    "_runtime_flow_objects",
}
SCOPE_CLASSES = {
    "AlternativeSelectionScope",
    "CandidateExecutionScope",
    "CompositionExecutionScope",
    "FlowDerivedInstanceReference",
}
COMPOSITION_FLOW_PRESSURES = {
    "test_cmp02_module_argument_flow_creates_attested_edge",
    "test_cmp04_consumer_binds_exact_flow_derived_target",
    "test_cmp04_flow_derived_target_rejects_distinct_carrier",
    "test_cmp04_flow_derived_target_rejects_wrong_source_result",
    "test_cmp26_requires_and_records_exact_adapter_crossing",
    "test_every_registered_composition_has_a_representable_flow_contract",
}
DYNAMIC_CHOICE_PRESSURES = {
    "test_dynamic_alternatives_declare_but_do_not_select",
    "test_dynamic_choice_records_actual_branch_and_unused_alternative",
    "test_dynamic_choice_rejects_c_inside_ab_scope_before_execution",
    "test_dynamic_scope_rejects_two_different_allowed_branches",
}
OWNER_AND_CO_USE_PRESSURES = {
    "test_cmp04_unrelated_endpoint_objects_do_not_create_edge",
    "test_cmp20_distinct_endpoint_owners_do_not_create_edge",
    "test_cmp26_rejects_target_endpoints_bound_outside_adapter_flow",
    "test_endpoint_co_use_outside_scope_does_not_claim_composition",
    "test_out_of_order_composition_scope_does_not_claim_edge",
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


def _assigned_self_attributes(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for assignment in ast.walk(node):
        if isinstance(assignment, ast.Assign):
            names.update(
                target.attr
                for target in assignment.targets
                if isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            )
        elif isinstance(assignment, ast.AnnAssign):
            target = assignment.target
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                names.add(target.attr)
    return names


def _assert_owned_by(
    test: unittest.TestCase,
    module: ModuleType,
    names: set[str],
) -> None:
    for name in sorted(names):
        with test.subTest(name=name):
            test.assertEqual(module.__name__, getattr(module, name).__module__)


class CausalPathwayBindingI122Test(unittest.TestCase):
    """Keep runtime execution state cohesive and scope dependencies narrow."""

    def test_scope_provider_is_acyclic_and_uses_a_structural_host(self) -> None:
        self.assertEqual({"candidates", "identity"}, _relative_imports(SCOPES_PATH))
        host = _class_definition(SCOPES_PATH, "PathwayBindingSession")
        self.assertEqual(
            ["Protocol"],
            [base.id for base in host.bases if isinstance(base, ast.Name)],
        )
        self.assertEqual(
            {"_runtime_scope_state"},
            _class_method_names(SCOPES_PATH, "PathwayBindingSession"),
        )

    def test_scope_provider_owns_public_records_references_and_scopes(self) -> None:
        self.assertEqual(PUBLIC_SCOPE_NAMES, set(scopes_api.__all__))
        _assert_owned_by(self, scopes_api, SCOPE_CLASS_OWNERS)
        for name in sorted(PUBLIC_SCOPE_NAMES):
            with self.subTest(name=name):
                self.assertIs(getattr(scopes_api, name), getattr(binding_api, name))
                self.assertIs(getattr(binding_api, name), getattr(public_api, name))

    def test_extracted_scope_logic_is_absent_from_session_module(self) -> None:
        self.assertTrue(
            EXTRACTED_SCOPE_DEFINITIONS <= _top_level_definitions(SCOPES_PATH)
        )
        self.assertTrue(
            EXTRACTED_SCOPE_DEFINITIONS.isdisjoint(_top_level_definitions(SESSION_PATH))
        )
        session_assignments = _top_level_assignments(SESSION_PATH)
        self.assertNotIn("ATTESTED_OBJECT_FLOW_DATAFLOW", session_assignments)
        self.assertNotIn("EXPLICIT_ADAPTER_DATAFLOW", session_assignments)
        self.assertNotIn("_SPECIAL_COMPOSITION_DATAFLOW_PORTS", session_assignments)

    def test_runtime_state_owner_holds_ledgers_identity_and_active_scopes(self) -> None:
        runtime_state = _class_definition(SCOPES_PATH, "_RuntimeScopeState")
        runtime_init = next(
            node
            for node in runtime_state.body
            if isinstance(node, ast.FunctionDef) and node.name == "__init__"
        )
        self.assertEqual(
            RUNTIME_STATE_FIELDS | {"_host"},
            _assigned_self_attributes(runtime_init),
        )

        session = _class_definition(SESSION_PATH, "PathwayBindingSession")
        session_init = next(
            node
            for node in session.body
            if isinstance(node, ast.FunctionDef) and node.name == "__init__"
        )
        session_fields = _assigned_self_attributes(session_init)
        self.assertIn("_runtime", session_fields)
        self.assertTrue(RUNTIME_STATE_FIELDS.isdisjoint(session_fields))
        session_attributes = {
            node.attr
            for node in ast.walk(session)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        }
        self.assertTrue(RUNTIME_STATE_FIELDS.isdisjoint(session_attributes))

    def test_wrappers_and_scopes_use_narrow_runtime_collaborators(self) -> None:
        for class_name in sorted(SCOPE_CLASSES):
            with self.subTest(class_name=class_name):
                definition = _class_definition(SCOPES_PATH, class_name)
                attributes = {
                    node.attr
                    for node in ast.walk(definition)
                    if isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "self"
                }
                self.assertNotIn("_session", attributes)
                self.assertIn("_runtime", attributes)

        for class_name in ("VerifiedCallable", "VerifiedCompositionCrossing"):
            with self.subTest(class_name=class_name):
                definition = _class_definition(SESSION_PATH, class_name)
                attributes = {
                    node.attr
                    for node in ast.walk(definition)
                    if isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "self"
                }
                self.assertNotIn("_session", attributes)
                self.assertIn("_runtime", attributes)

        session_source = SESSION_PATH.read_text(encoding="utf-8")
        for private_read in (
            "source._binding_id",
            "source._composition_ids",
            "source._pathway_id",
            "source._session",
            "source._stage_id",
        ):
            with self.subTest(private_read=private_read):
                self.assertNotIn(private_read, session_source)

    def test_focused_suite_retains_runtime_scope_pressures(self) -> None:
        focused_methods = _class_method_names(
            FOCUSED_TEST_PATH,
            "CausalPathwayBindingTest",
        )
        retained = (
            COMPOSITION_FLOW_PRESSURES
            | DYNAMIC_CHOICE_PRESSURES
            | OWNER_AND_CO_USE_PRESSURES
        )
        self.assertTrue(retained <= focused_methods)


if __name__ == "__main__":
    unittest.main()
