"""Production policy proofs, stage parity, lifecycle ownership and rollback."""

from dataclasses import replace
import math
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from unittest.mock import patch

from pygrc.models import grc_v4_certification as cert
from pygrc.models import grc_v4_numerics as num
from pygrc.models import grc_v4_realizations as real
from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend, exact_number as q
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_os_pass_probe import before, compare_point
from tests.models.test_grc_v4_realizations import a_os_fixture


MODE = cert.NumericalPolicy.CERTIFIED_ARB_256


class CertifiedPolicyTests(unittest.TestCase):
    def test_explicit_policy_requires_backend_and_restores(self):
        self.assertIs(
            cert.current_numerical_policy(), cert.NumericalPolicy.LEGACY_EXACT
        )
        with self.assertRaises(TypeError), cert.numerical_policy("certified"):
            pass
        with self.assertRaises(ValueError), cert.numerical_policy(MODE):
            pass
        with exact_backend(ExactBackend.FLINT):
            with cert.numerical_policy(MODE):
                self.assertIs(cert.current_numerical_policy(), MODE)
            self.assertIs(
                cert.current_numerical_policy(), cert.NumericalPolicy.LEGACY_EXACT
            )

    def test_rounding_cells_and_fixed_precision_no_fallback(self):
        import flint

        with exact_backend(ExactBackend.FLINT):
            for x in (
                q(1) + q(2) ** -53,
                q(1) + 3 * q(2) ** -53,
                q(2) ** -1075,
                -(q(2) ** -1075),
                q(float.fromhex("0x1.fffffffffffffp+1023")),
            ):
                self.assertEqual(cert.round_interval(x, x), float(x))
            midpoint = q(1) + q(2) ** -53
            for lo, hi in (
                (midpoint - q(2) ** -200, midpoint + q(2) ** -200),
                (q(2) ** 1024, q(2) ** 1024),
            ):
                with self.assertRaises(cert.CertificationInconclusive):
                    cert.round_interval(lo, hi)
            old = flint.ctx.prec
            with self.assertRaises(cert.CertificationInconclusive):
                cert.rounded_solve(((q(1) + q(2) ** -300, 1), (0, 1)), ((1,), (1,)))
            self.assertEqual(flint.ctx.prec, old)
            for a in (
                ((0, 1), (1, 0)),
                ((2, 0.125), (0.25, 3)),
                ((1, 1), (1, 1 + 2**-50)),
            ):
                rhs = ((1.0, 2.0), (-3.0, 0.5))
                expected = num.binary64_matrix(
                    num.matmul(num.inverse(num.exact_matrix(a)), num.exact_matrix(rhs))
                )
                with patch.object(
                    num._backend,
                    "inverse",
                    side_effect=AssertionError("hidden inverse"),
                ):
                    self.assertEqual(cert.rounded_solve(a, rhs), expected)

    def test_condition_and_residual_are_separate_from_rounding(self):
        with exact_backend(ExactBackend.FLINT):
            b = before()
            policy = b.geometry.reference.profile.params_resolved.solver
            strict = replace(policy, absolute_tolerance=1e-20, relative_tolerance=1e-20)
            with cert.numerical_policy(MODE):
                with self.assertRaises(num.MatrixError):
                    num.solve(((1.5,),), ((1.0,),), strict, "pressure", [])
                with patch.object(
                    cert,
                    "rounded_solve",
                    side_effect=AssertionError("solve after failed condition"),
                ):
                    with self.assertRaises(cert.CertificationInconclusive):
                        num.solve(
                            ((0, 1), (1, 0)), ((1,), (2,)), policy, "pressure", []
                        )
                # This API is still exact rational inversion, not Arb-rounded output.
                self.assertEqual(num.inverse(((q(3),),))[0][0], q(1) / 3)

    def test_positive_and_weighted_split_proofs_against_inertia(self):
        with exact_backend(ExactBackend.FLINT):
            for a in (
                ((1.0, 0.25), (0.25, 2.0)),
                ((4.0, -1.0), (-1.0, 2.0)),
                ((2**-1000, 0), (0, 2**1000)),
            ):
                cert.positive_definite(a)
                self.assertEqual(num.inertia(num.exact_matrix(a)), (0, 0, 2))
            # SPD but outside strict row dominance is unresolved, never rejected.
            a = ((1.0, 1.5), (1.5, 4.0))
            self.assertEqual(num.inertia(num.exact_matrix(a)), (0, 0, 2))
            with self.assertRaises(cert.CertificationInconclusive):
                cert.positive_definite(a)
            d = ((1.0, 0.0), (0.0, 4.0))
            for value in (math.nextafter(0.5, 0.0), 0.5):
                r = ((value, 0.0), (0.0, -4 * value))
                cert.weighted_split(r, d, 0.5)
                for sign in (-1, 1):
                    bound = tuple(
                        tuple(q(0.5) * q(x) + sign * q(y) for x, y in zip(dr, rr))
                        for dr, rr in zip(d, r)
                    )
                    self.assertEqual(num.inertia(bound)[0], 0)
            for r in (
                ((math.nextafter(0.5, 1.0), 0.0), (0.0, 0.0)),
                ((0.0, 1.0), (1.0, 0.0)),
            ):
                with self.assertRaises(cert.CertificationInconclusive):
                    cert.weighted_split(r, d, 0.5)
            with self.assertRaises(cert.CertificationInconclusive):
                cert.weighted_split(((q(2) ** -1075,),), ((1,),), 0)

    def test_gram_bound_weighted_vertex_and_nonconstant_retained_hodge(self):
        with exact_backend(ExactBackend.FLINT):
            b = ((1, 0), (-1, 1), (0, -1))
            v = ((1, 0, 0), (0, 2, 0), (0, 0, 4))
            h = ((1.0, 0.01), (0.01, 1.01))
            bm, vm, hm = map(cert._matrix, (b, v, h))
            f = cert._flint_module()
            eye = f.fmpq_mat([[1, 0], [0, 1]])
            a = eye + q(0.125) * bm.transpose() * vm.inv() * bm * hm
            bound = cert.condition_bound(a.tolist(), 10, gram_witness=(b, v, h, 0.125))
            self.assertLessEqual(bound, 100)
            for beta in (0, q(1) - q(2) ** -52):
                cert.c_regularity(beta, 0.125, h, v)
                self.assertNotEqual(
                    (
                        (1 - beta) * eye
                        + q(0.125) * bm.transpose() * vm.inv() * bm * hm
                    ).det(),
                    0,
                )
            with self.assertRaises(cert.CertificationInconclusive):
                cert.c_regularity(1, 0.125, h, v)
            with self.assertRaises(cert.CertificationInconclusive):
                cert.condition_bound(a.tolist(), 1, gram_witness=(b, v, h, 0.125))

    def test_complete_c_pass_matches_without_monkeypatching_production(self):
        with exact_backend(ExactBackend.FLINT):
            for tau in (0, 1):
                b = before(tau)
                expected = real.CandidateCOSPass(b)
                with cert.numerical_policy(MODE):
                    actual = real.CandidateCOSPass(b)
                compare_point(self, actual.predictor, expected.predictor)
                compare_point(self, actual.corrector, expected.corrector)
                self.assertEqual(actual.residual, expected.residual)
                self.assertIsNotNone(actual.residual.execution_certificate)
                self.assertEqual(
                    actual.selector_path_segments, expected.selector_path_segments
                )

    def test_c_current_nonunit_weights_and_nonconstant_selector(self):
        from tests.models.test_grc_v4_candidate_c import current_fixture
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge

        graph = GRCV4Graph(
            ("a", "b", "c"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("bc", "b", "c"),
                OrientedEdge("ca", "c", "a"),
            ),
        )
        with exact_backend(ExactBackend.FLINT):
            b = current_fixture(
                graph=graph,
                weights={"ab": 1.0, "bc": 1.5, "ca": 0.75},
                resource=(2.0, 1.5, 1.0),
                changes={"candidate": {"Lambda_C": 8.0, "kappa_M_C": 0.01}},
            )
            native = CandidateCCurrent(b)
            self.assertGreater(native.algebra.selector.rank, 1)
            self.assertGreater(len(set(native.algebra.selector.selected.values)), 1)
            with cert.numerical_policy(MODE):
                updated = CandidateCCurrent(b)
            compare_point(self, updated, native)

    def test_a_and_c_public_steps_reset_replay_owner_policy_and_bytes(self):
        with exact_backend(ExactBackend.FLINT):
            for family in ("C", "A"):
                with self.subTest(family=family):
                    b, backend = (
                        (before(), None) if family == "C" else a_os_fixture(gamma=0.125)
                    )
                    legacy = GRCV4(b, differential_reference=backend)
                    with cert.numerical_policy(MODE):
                        owner = GRCV4(b, differential_reference=backend)
                    self.assertIs(owner.numerical_policy, MODE)
                    request = GRCV4StepRequestInput(
                        "grcv4-step-request-input-v1",
                        "policy-parity-" + family,
                        b.dt,
                        FrozenJSONMap({}),
                    )
                    left, right = (
                        legacy.step_v4_input(request),
                        owner.step_v4_input(request),
                    )
                    self.assertTrue(left.committed, left.failure)
                    self.assertTrue(right.committed, right.failure)
                    self.assertEqual(
                        left.to_canonical_bytes(), right.to_canonical_bytes()
                    )
                    self.assertEqual(legacy.snapshot(), owner.snapshot())
                    self.assertEqual(
                        legacy.compute_observables(), owner.compute_observables()
                    )
                    duplicate = owner.duplicate()
                    self.assertIs(duplicate.numerical_policy, MODE)
                    self.assertEqual(duplicate.snapshot(), owner.snapshot())
                    with cert.numerical_policy(MODE):
                        restored = GRCV4.from_state(
                            owner.snapshot(), owner.get_params().to_payload()
                        )
                    self.assertIs(restored.numerical_policy, MODE)
                    owner.reset()
                    legacy.reset()
                    self.assertEqual(owner.snapshot(), legacy.snapshot())
        # Owner retains FLINT and policy after both ambient scopes have exited.
        self.assertIs(owner.numerical_policy, MODE)
        owner.compute_observables()

    def test_inconclusive_full_step_rolls_back_and_cache_cannot_cross_policy(self):
        from pygrc.models.grc_v4_codec import _OPERATION_CONTEXT

        with exact_backend(ExactBackend.FLINT), cert.numerical_policy(MODE):
            owner = GRCV4(before())
            snapshot = owner.snapshot()
            request = GRCV4StepRequestInput(
                "grcv4-step-request-input-v1", "inconclusive", 0.01, FrozenJSONMap({})
            )
            with patch.object(
                cert,
                "rounded_solve",
                side_effect=cert.CertificationInconclusive("pressure"),
            ):
                with self.assertRaisesRegex(cert.CertificationInconclusive, "pressure"):
                    owner.step_v4_input(request)
            self.assertEqual(owner.snapshot(), snapshot)
            with num.matrix_operation():
                matrix = ((q(1),),)
                num.condition_bound(matrix, 1e8, "fact")
                facts = _OPERATION_CONTEXT.get().matrix_facts
                saved = facts.retain(matrix, matrix, q(1e8))
                self.assertIs(saved.numerical_policy, MODE)
            with (
                cert.numerical_policy(cert.NumericalPolicy.LEGACY_EXACT),
                num.matrix_operation(),
            ):
                with self.assertRaisesRegex(TypeError, "another numerical policy"):
                    _OPERATION_CONTEXT.get().matrix_facts.seed(saved)

    def test_nine_port_event_and_checkpoint_preserve_policy_and_bytes(self):
        from pygrc.models.grc_9_v4_lifecycle import GRC9V4COSOperation
        from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture

        with exact_backend(ExactBackend.FLINT):
            seed, request = native_cos_fixture()
            legacy = GRC9V4COSOperation(seed)
            with cert.numerical_policy(MODE):
                owner = GRC9V4COSOperation(seed)
        # Neither ambient choice remains active; the receiver owns both choices.
        self.assertIs(owner.numerical_policy, MODE)
        left, right = legacy.expand(request), owner.expand(request)
        self.assertTrue(left.committed, left.failure)
        self.assertTrue(right.committed, right.failure)
        self.assertEqual(left.emitted_receipts, right.emitted_receipts)
        self.assertEqual(legacy.checkpoint(), owner.checkpoint())
        with exact_backend(ExactBackend.FLINT), cert.numerical_policy(MODE):
            restored = GRC9V4COSOperation.replay(owner.checkpoint())
        self.assertIs(restored.numerical_policy, MODE)
        self.assertEqual(restored.checkpoint(), owner.checkpoint())

    def test_retained_production_record_integrity_not_large_rerun(self):
        import hashlib
        import json
        from pathlib import Path
        from scripts.benchmark_grcv4_certified_native import digest, PREDECESSOR

        root = Path(__file__).resolve().parents[2]
        path = (
            root
            / "implementation/evidence/grcv4-performance/certified_native_os_pass.json"
        )
        record = json.loads(path.read_text())
        self.assertLessEqual(path.stat().st_size, 1_000_000)
        self.assertEqual(
            record["record_digest"],
            digest({k: v for k, v in record.items() if k != "record_digest"}),
        )
        for name, expected in record["source_bindings"].items():
            self.assertFalse(Path(name).is_absolute())
            if name in ('src/pygrc/models/grc_v4_ci.py',
                        'src/pygrc/models/grc_v4_linear.py',
                        'src/pygrc/models/grc_v4_numerics.py',
                        'src/pygrc/models/grc_v4_exact.py',
                        'src/pygrc/models/_grc_v4_matrix.py',
                        'src/pygrc/models/grc_v4_certification.py',
                        'specs/grc-v4-numerical-policy.md'):
                # The accepted OS run predates the explicit CI interval
                # extension and solve reuse. Authenticate its actual source,
                # never rebind it to later implementation.
                import subprocess
                raw = subprocess.check_output(['git','show','e1d61021:'+name], cwd=root)
            else:
                raw = (root / name).read_bytes()
            self.assertEqual(
                hashlib.sha256(raw).hexdigest(), expected, name
            )
        self.assertEqual(record["execution_policy"], MODE.value)
        self.assertEqual(
            (record["outcome"], record["worker_exitcode"]), ("completed", 0)
        )
        self.assertTrue(record["production_code_path"])
        for key in (
            "cleanup_terminated",
            "research_callbacks",
            "fallback_attempted",
            "aggregate_closed",
        ):
            self.assertFalse(record[key])
        self.assertEqual((record["native_steps"], record["native_events"]), (0, 0))
        prior = json.loads((root / PREDECESSOR).read_text())
        self.assertEqual(record["predecessor_record_digest"], prior["record_digest"])
        result = record["result"]
        for key in (
            "predictor",
            "corrector",
            "split_exact_values_digest",
            "selector_path_segments",
        ):
            self.assertEqual(result[key], prior["result"][key])
        for key in ("complete_os_pass", "matches_research_points", "split_admitted"):
            self.assertTrue(result[key])
        # Prior retained tests reconstruct these operands from the stage outputs;
        # matching them here is linkage, not another trajectory or enclosure.
        proof = prior["result"]["operations"][-1]["certificate"]
        for key in ("weighted_row_bound", "tolerance_exact"):
            self.assertEqual(result["split_certificate"][key], proof[key])
        with exact_backend(ExactBackend.FLINT):
            self.assertEqual(
                q(result["split_certificate"]["margin_lower"]),
                q(proof["tolerance_exact"]) - q(proof["weighted_row_bound"]),
            )


if __name__ == "__main__":
    unittest.main()
