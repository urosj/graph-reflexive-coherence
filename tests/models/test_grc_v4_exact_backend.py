"""Backend selection preserves V4 public bytes and private fact ownership."""

import ast
import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from pygrc.models import grc_v4_exact
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_exact import (
    ExactBackend,
    current_exact_backend,
    exact_number,
    integer_ratio,
)


class LegacyExactBackendTests(unittest.TestCase):
    def test_default_and_scope_restoration(self):
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)
        self.assertIsInstance(exact_number(0.1), Fraction)
        with self.assertRaisesRegex(TypeError, "ExactBackend"):
            with numerics.exact_backend("flint"):
                self.fail("invalid backend entered the scope")
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)

    def test_v4_exact_scalars_are_constructed_only_through_backend_boundary(self):
        # This source-level guard runs without FLINT. A direct Fraction import
        # would otherwise pass every default-backend numerical test and fail
        # only when a FLINT owner exercises the new path.
        source_dir = Path(grc_v4_exact.__file__).parent
        sources = sorted(set(source_dir.glob("grc_v4*.py")) | set(source_dir.glob("_grc_v4*.py")))
        self.assertTrue(sources)
        violations = []
        for source in sources:
            if source.name == "grc_v4_exact.py":
                continue
            for node in ast.walk(ast.parse(source.read_text(), filename=str(source))):
                if isinstance(node, ast.ImportFrom) and node.module == "fractions":
                    violations.append(f"{source.name}:{node.lineno}: direct fractions import")
                elif isinstance(node, ast.Import) and any(
                    alias.name == "fractions" for alias in node.names
                ):
                    violations.append(f"{source.name}:{node.lineno}: direct fractions import")
                elif isinstance(node, ast.Name) and node.id == "Fraction":
                    violations.append(f"{source.name}:{node.lineno}: direct Fraction reference")
                elif isinstance(node, ast.Attribute) and node.attr == "Fraction":
                    violations.append(f"{source.name}:{node.lineno}: direct Fraction reference")
        self.assertFalse(violations, "\n".join(violations))

    def test_optional_dependency_fails_before_entering_scope(self):
        with patch("pygrc.models.grc_v4_exact._flint_module", side_effect=ImportError):
            with self.assertRaisesRegex(RuntimeError, "python-flint"):
                with numerics.exact_backend(ExactBackend.FLINT):
                    self.fail("missing FLINT entered the scope")
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)


@unittest.skipUnless(importlib.util.find_spec("flint"), "python-flint is optional")
class FlintExactBackendTests(unittest.TestCase):
    def test_native_scalars_and_strict_numeric_failures(self):
        from flint import fmpq

        with numerics.exact_backend(ExactBackend.FLINT):
            value = exact_number(0.1)
            self.assertIsInstance(value, fmpq)
            self.assertEqual(integer_ratio(value), (3602879701896397, 36028797018963968))
            self.assertEqual(exact_number("0.1"), fmpq(1, 10))
            self.assertIs(exact_number(value), value)
            matrix = numerics.exact_matrix(((1.0, 1.0), (1.0, 1.0)))
            with self.assertRaisesRegex(numerics.MatrixError, "singular C stage block") as caught:
                numerics.inverse(matrix)
            self.assertEqual(caught.exception.disposition, "singular")
            with self.assertRaisesRegex(numerics.MatrixError, "conditioning limit") as caught:
                numerics.condition_bound(
                    numerics.exact_matrix(((3.0, 1.0), (1.0, 3.0))),
                    1.5,
                    "strict",
                )
            self.assertEqual(caught.exception.disposition, "conditioning_failure")
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)

    def test_continuation_rejects_another_backend(self):
        matrix = ((3.0, 1.0), (1.0, 3.0))
        with numerics.exact_backend(ExactBackend.FLINT), numerics.matrix_operation():
            exact = numerics.exact_matrix(matrix)
            numerics.inverse(exact)
            # Use the operation-owned fact store, which is the only source of
            # continued facts in a public step.
            from pygrc.models.grc_v4_codec import _OPERATION_CONTEXT
            facts = _OPERATION_CONTEXT.get().matrix_facts
            continuation = facts.retain(exact, exact, exact_number(1e8))
            self.assertTrue(continuation.facts)
            self.assertIs(continuation.backend, ExactBackend.FLINT)
        with numerics.matrix_operation():
            with self.assertRaisesRegex(TypeError, "another exact backend"):
                _OPERATION_CONTEXT.get().matrix_facts.seed(continuation)

    def test_owner_keeps_backend_after_declaration_scope(self):
        from examples.grcv4.grid_realizations_c import make_inputs
        from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
        from pygrc.models.grc_v4_state import FrozenJSONMap

        python_inputs, python_reference, _ = make_inputs("PC", 3, 4)
        python_owner = GRCV4(
            python_inputs, differential_reference=python_reference
        )
        with numerics.exact_backend(ExactBackend.FLINT):
            flint_inputs, flint_reference, _ = make_inputs("PC", 3, 4)
            flint_owner = GRCV4(
                flint_inputs, differential_reference=flint_reference
            )
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)
        self.assertEqual(python_inputs.to_payload(), flint_inputs.to_payload())
        self.assertIs(
            flint_owner.duplicate()._operation._exact_backend_choice,
            ExactBackend.FLINT,
        )
        self.assertEqual(
            python_owner.compute_observables(), flint_owner.compute_observables()
        )
        flint_owner.set_state(flint_owner.state)
        request = GRCV4StepRequestInput(
            "grcv4-step-request-input-v1",
            "backend-parity-0",
            python_inputs.dt,
            FrozenJSONMap({}),
        )
        python_result = python_owner.step_v4_input(request)
        flint_result = flint_owner.step_v4_input(request)
        self.assertTrue(python_result.committed, python_result.failure)
        self.assertEqual(
            python_result.to_canonical_bytes(), flint_result.to_canonical_bytes()
        )
        self.assertEqual(python_owner.snapshot(), flint_owner.snapshot())
        python_owner.reset()
        flint_owner.reset()
        self.assertEqual(python_owner.snapshot(), flint_owner.snapshot())
        self.assertIs(
            flint_owner._operation._exact_backend_choice, ExactBackend.FLINT
        )
