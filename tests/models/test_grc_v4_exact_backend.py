"""Backend selection preserves V4 public bytes and private fact ownership."""

import ast
import importlib.util
import math
import random
import sys
import unittest
from dataclasses import replace
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
        with (
            self.assertRaisesRegex(TypeError, "ExactBackend"),
            numerics.exact_backend("flint"),
        ):
            self.fail("invalid backend entered the scope")
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)

    def test_v4_exact_scalars_are_constructed_only_through_backend_boundary(self):
        # This source-level guard runs without FLINT. A direct Fraction import
        # would otherwise pass every default-backend numerical test and fail
        # only when a FLINT owner exercises the new path.
        source_dir = Path(grc_v4_exact.__file__).parent
        sources = sorted(
            set(source_dir.glob("grc_v4*.py"))
            | set(source_dir.glob("_grc_v4*.py"))
            | set(source_dir.glob("grc_9_v4*.py"))
            | set(source_dir.glob("_grc_9_v4*.py"))
        )
        self.assertTrue(sources)
        self.assertIn(source_dir / "grc_9_v4_topology.py", sources)
        self.assertIn(source_dir / "grc_9_v4_lifecycle.py", sources)
        violations = []
        for source in sources:
            if source.name == "grc_v4_exact.py":
                continue
            for node in ast.walk(ast.parse(source.read_text(), filename=str(source))):
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.module == "fractions"
                    or isinstance(node, ast.Import)
                    and any(alias.name == "fractions" for alias in node.names)
                ):
                    violations.append(
                        f"{source.name}:{node.lineno}: direct fractions import"
                    )
                elif (
                    isinstance(node, ast.Name)
                    and node.id == "Fraction"
                    or isinstance(node, ast.Attribute)
                    and node.attr == "Fraction"
                ):
                    violations.append(
                        f"{source.name}:{node.lineno}: direct Fraction reference"
                    )
        self.assertFalse(violations, "\n".join(violations))

    def test_optional_dependency_fails_before_entering_scope(self):
        with (
            patch("pygrc.models.grc_v4_exact._flint_module", side_effect=ImportError),
            self.assertRaisesRegex(RuntimeError, "python-flint"),
            numerics.exact_backend(ExactBackend.FLINT),
        ):
            self.fail("missing FLINT entered the scope")
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)


@unittest.skipUnless(importlib.util.find_spec("flint"), "python-flint is optional")
class FlintExactBackendTests(unittest.TestCase):
    def test_nine_port_row_trigger_and_coarse_native_parity(self):
        from flint import fmpq

        from pygrc.models.grc_9_v4_lifecycle import GRC9V4CandidateDetection
        from pygrc.models.grc_9_v4_topology import (
            GRC9V4ColumnProfile,
            GRC9V4PortField,
            GRC9V4PortGraph,
            GRC9V4RowDifferential,
            coarse_grain_columns,
            split_columns,
        )
        from tests.models.test_grc_9_v4_lifecycle import policy, star_inputs

        def exercise():
            native = (
                Fraction if current_exact_backend() is ExactBackend.PYTHON else fmpq
            )
            results = []
            tiny, huge = math.ulp(0.0), sys.float_info.max
            for g, tolerance in (
                ((3, 4, 0), 5),
                ((3, 4, 0), math.nextafter(5, math.inf)),
                ((math.nextafter(1, 0), math.nextafter(2**-26, 0), 0), 1),
                ((tiny, tiny, 0), tiny),
                ((huge / 2, huge / 2, 0), huge),
            ):
                for sign in (-1, 1):
                    inputs = star_inputs(gradients=g, sign=sign)
                    backend = GRC9V4RowDifferential(inputs.port_graph, sign)
                    terms = backend._terms(
                        inputs.committed.C, inputs.weights, inputs.physical_current
                    )
                    self.assertTrue(
                        all(
                            type(x) is native
                            for node in terms
                            for row in node
                            for term in row
                            for x in term
                        )
                    )
                    rows = inputs.evaluate()
                    detector = GRC9V4CandidateDetection(
                        inputs, policy(gradient_tolerance=tolerance)
                    )
                    results.append(
                        (
                            tuple(
                                (r.gradient, r.net_flux, r.signed_hessian) for r in rows
                            ),
                            detector.identity,
                            detector.candidate_node_ids(),
                        )
                    )
            inputs = star_inputs(gradients=(0.125, 0.25, 0.5))
            results.append(
                GRC9V4RowDifferential(inputs.port_graph, -1).legacy_node_tensors(
                    inputs.committed.C,
                    inputs.weights,
                    inputs.physical_current,
                    lambda_c=0.1,
                    xi_c=0.2,
                    zeta_c=0.3,
                )
            )
            rng = random.Random(9815)
            cases = [
                (tiny, huge, 1, huge, tiny, math.nextafter(1, 0), 0, 0, 0),
                (huge,) * 9,
                (0,) * 9,
            ]
            cases += [
                tuple(
                    math.ldexp(rng.randrange(1, 2**20), rng.randrange(-1074, 1003))
                    for _ in range(9)
                )
                for _ in range(80)
            ]
            graph = GRC9V4PortGraph(("s",), ())
            # Exact subjects generated from accepted .d at a2d3d36, before
            # this backend correction; they pin default-backend identity too.
            golden = {
                "nonnegative": "grc9v4-coarse-field-sha256:fd825e52ae30bea56729f92ed9de779e632f470af5db810dd38da0cc0369e9ad",
                "signed_flux": "grc9v4-coarse-field-sha256:dea517a9b07dda16e584d720cd6d02f4960d0af43561dcf2cf42f6cc8ff4d9e6",
            }
            for case_index, row in enumerate(cases):
                for family in ("nonnegative", "signed_flux"):
                    values = tuple(
                        -x if family == "signed_flux" and i % 2 and x else x
                        for i, x in enumerate(row)
                    )
                    fine = GRC9V4PortField(graph, family, (values,))
                    coarse = coarse_grain_columns(fine, field_family=family)
                    if case_index == 0:
                        self.assertEqual(coarse.identity, golden[family])
                    for column in coarse.columns[0]:
                        for channel in (
                            (column,)
                            if type(column) is GRC9V4ColumnProfile
                            else (column.positive, column.negative)
                        ):
                            self.assertIs(type(channel.total), native)
                            self.assertTrue(
                                all(type(x) is native for x in channel.profile)
                            )
                    restored = split_columns(
                        coarse, field_family=family, port_graph=graph
                    )
                    self.assertEqual(restored.identity, fine.identity)
                    self.assertEqual(restored.values, fine.values)
                    self.assertEqual(
                        coarse_grain_columns(restored, field_family=family).identity,
                        coarse.identity,
                    )
                    results.append((coarse.identity, restored.identity))
            return results

        with numerics.exact_backend(ExactBackend.PYTHON):
            python_result = exercise()
        with numerics.exact_backend(ExactBackend.FLINT):
            flint_result = exercise()
        self.assertEqual(flint_result, python_result)
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)

    def test_nine_port_retained_scalars_own_backend_and_reject_mixing(self):
        from flint import fmpq

        from pygrc.models.grc_9_v4_topology import (
            GRC9V4ColumnProfile,
            GRC9V4PortField,
            GRC9V4PortGraph,
            GRC9V4SignedColumn,
            coarse_grain_columns,
            split_columns,
        )

        fine = GRC9V4PortField(GRC9V4PortGraph((1,), ()), "nonnegative", ((1,) * 9,))
        python_value = coarse_grain_columns(fine, field_family="nonnegative")
        with numerics.exact_backend(ExactBackend.FLINT):
            flint_value = coarse_grain_columns(fine, field_family="nonnegative")
            with self.assertRaisesRegex(TypeError, "selected exact backend"):
                GRC9V4ColumnProfile(Fraction(3), (Fraction(1, 3),) * 3)
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)
        self.assertEqual(flint_value.identity, python_value.identity)
        self.assertIs(flint_value.backend, ExactBackend.FLINT)
        self.assertEqual(flint_value.columns[0][0].split(), (1, 1, 1))
        copied = replace(flint_value)
        self.assertIs(type(copied.columns[0][0].total), fmpq)
        self.assertEqual(
            split_columns(
                copied, field_family="nonnegative", port_graph=fine.port_graph
            ).identity,
            fine.identity,
        )
        with self.assertRaisesRegex(TypeError, "another exact backend"):
            replace(flint_value, backend=ExactBackend.PYTHON)
        with self.assertRaisesRegex(TypeError, "different exact backends"):
            GRC9V4SignedColumn(python_value.columns[0][0], flint_value.columns[0][0])
        with self.assertRaisesRegex(TypeError, "selected exact backend"):
            replace(flint_value.columns[0][0], backend=ExactBackend.PYTHON)
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            replace(flint_value.columns[0][0], total=math.nan)
        self.assertIs(current_exact_backend(), ExactBackend.PYTHON)
        with numerics.exact_backend(ExactBackend.FLINT):
            self.assertEqual(
                split_columns(
                    python_value, field_family="nonnegative", port_graph=fine.port_graph
                ).values,
                fine.values,
            )
            self.assertIs(current_exact_backend(), ExactBackend.FLINT)

    def test_nine_port_domain_and_rounding_parity(self):
        from pygrc.models.grc_9_v4_topology import (
            CoarseDomainError,
            GRC9V4ColumnProfile,
            _rounded,
        )

        for backend in ExactBackend:
            with self.subTest(backend=backend), numerics.exact_backend(backend):
                for n in (2**53 + 1, 2**53 + 3):
                    self.assertEqual(
                        _rounded(exact_number(n, 2**53)), float(Fraction(n, 2**53))
                    )
                self.assertEqual(_rounded(exact_number(1, 2**1074)), math.ulp(0.0))
                self.assertEqual(_rounded(exact_number(-1, 2**1075)).hex(), "0x0.0p+0")
                for total, shares in (
                    (exact_number(1), (exact_number(1, 3),) * 3),
                    (
                        exact_number(math.ulp(0.0)),
                        (exact_number(1, 2), exact_number(1, 2), exact_number()),
                    ),
                    (
                        2 * exact_number(sys.float_info.max),
                        (exact_number(1), exact_number(), exact_number()),
                    ),
                    (exact_number(), (exact_number(1), exact_number(), exact_number())),
                ):
                    with self.assertRaises(CoarseDomainError):
                        GRC9V4ColumnProfile(total, shares)
                for bad in (True, -0.0, math.nan, math.inf, 2**53, "3"):
                    with self.assertRaises((TypeError, ValueError)):
                        GRC9V4ColumnProfile(bad, (exact_number(1, 3),) * 3)

    def test_p980_production_entry_probes_on_both_backends(self):
        # The other P9-8.0 modules are independent proof/represented-research
        # code. These two alone import pygrc; retain their historical oracles.
        verification = (
            Path(__file__).resolve().parents[2]
            / "implementation/phase-9-grcv4/verification"
        )
        previous_path = sys.path[:]
        try:
            sys.path.insert(0, str(verification))
            for backend in ExactBackend:
                with self.subTest(backend=backend), numerics.exact_backend(backend):
                    suite = unittest.defaultTestLoader.loadTestsFromNames(
                        ("test_p980_feasibility", "test_p980_readiness")
                    )
                    result = unittest.TestResult()
                    suite.run(result)
                    self.assertEqual(result.testsRun, 7)
                    self.assertFalse(result.skipped)
                    self.assertTrue(
                        result.wasSuccessful(), str(result.errors + result.failures)
                    )
        finally:
            sys.path[:] = previous_path

    def test_native_scalars_and_strict_numeric_failures(self):
        from flint import fmpq

        with numerics.exact_backend(ExactBackend.FLINT):
            value = exact_number(0.1)
            self.assertIsInstance(value, fmpq)
            self.assertEqual(
                integer_ratio(value), (3602879701896397, 36028797018963968)
            )
            self.assertEqual(exact_number("0.1"), fmpq(1, 10))
            self.assertIs(exact_number(value), value)
            matrix = numerics.exact_matrix(((1.0, 1.0), (1.0, 1.0)))
            with self.assertRaisesRegex(
                numerics.MatrixError, "singular C stage block"
            ) as caught:
                numerics.inverse(matrix)
            self.assertEqual(caught.exception.disposition, "singular")
            with self.assertRaisesRegex(
                numerics.MatrixError, "conditioning limit"
            ) as caught:
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
        with (
            numerics.matrix_operation(),
            self.assertRaisesRegex(TypeError, "another exact backend"),
        ):
            _OPERATION_CONTEXT.get().matrix_facts.seed(continuation)

    def test_owner_keeps_backend_after_declaration_scope(self):
        from examples.grcv4.grid_realizations_c import make_inputs
        from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
        from pygrc.models.grc_v4_state import FrozenJSONMap

        python_inputs, python_reference, _ = make_inputs("PC", 3, 4)
        python_owner = GRCV4(python_inputs, differential_reference=python_reference)
        with numerics.exact_backend(ExactBackend.FLINT):
            flint_inputs, flint_reference, _ = make_inputs("PC", 3, 4)
            flint_owner = GRCV4(flint_inputs, differential_reference=flint_reference)
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
        self.assertIs(flint_owner._operation._exact_backend_choice, ExactBackend.FLINT)
