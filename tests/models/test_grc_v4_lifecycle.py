"""C_OS ordinary operations and lifecycle: independent oracles and atomic pressure.

Fault-injection tests are explicitly controls, separate from native failures.
No complete facade/profile conformance, full lineage/replay or migration claim.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from fractions import Fraction
import math
from typing import Any, cast
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from pygrc.models.grc_v4_codec import V4IdentityError, canonical_json_bytes
from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
from pygrc.models.grc_v4_realizations import CandidateCOSPass
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
from pygrc.models.grc_v4_state import (
    FrozenJSONMap,
    GRCV4AuthoritativeState,
    SolverDisposition,
)
from tests.models.grcv4_reference_oracles import (
    expected_negative,
    identity,
    lifecycle_id,
    scientific_id,
)
from tests.models.test_grc_v4_candidate_c import current_fixture
from tests.models.test_grc_v4_realizations import dense_pass, os_fixture, scalar_pass


def request(dt: float, operation_id: str = "ordinary") -> GRCV4StepRequestInput:
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", operation_id, dt, FrozenJSONMap({})
    )


def primitive(value: Any) -> Any:
    if isinstance(value, FrozenJSONMap):
        return value.to_dict()
    if is_dataclass(value):
        return {f.name: primitive(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple):
        return [primitive(x) for x in value]
    return value


def owned_bytes(owner: CandidateCOSOperation) -> bytes:
    return canonical_json_bytes(primitive(owner.state))


def dyadic_fixture() -> GeometryStageInputs:
    return replace(
        os_fixture(
            candidate={"tau_C": 0, "chi_C": 1, "zeta_C": 3},
            geometry={"kappa_H": 0},
            solver={"absolute_tolerance": 0, "relative_tolerance": 0},
            charge={"absolute_tolerance": 0, "relative_tolerance": 0},
        ),
        dt=0.125,
    )


def charge_fixture(tolerance: float) -> GeometryStageInputs:
    return cast(
        GeometryStageInputs,
        replace(
            current_fixture(
                graph=GRCV4Graph(("a", "b", "c", "d"), (OrientedEdge("e", "a", "d"),)),
                weights={"e": 1},
                resource=(float(2**53), 1, 1, 1),
                changes={
                    "candidate": {
                        "eta_C": 2**-53,
                        "tau_C": 0,
                        "chi_C": 1,
                        "zeta_C": 3,
                        "kappa_M_C": 0,
                        "Lambda_C": 3,
                    },
                    "geometry": {"kappa_H": 0},
                    "charge": {
                        "absolute_tolerance": tolerance,
                        "relative_tolerance": 0,
                    },
                },
            ),
            Q_target=float(2**53 + 2),
            dt=1,
            receipt_ids=(),
        ),
    )


class CandidateCOSOperationTests(unittest.TestCase):
    def test_capture_rejects_same_file_method_slot_substitution(self) -> None:
        import hashlib
        import importlib
        from pathlib import Path
        import subprocess
        from tests.models.test_grc_v4_candidate_c import _p941_loaded_sources

        # The inherited checker also requires the shared transport test owner,
        # including when this control is invoked as a standalone reproducer.
        importlib.import_module("tests.models.test_grc_v4_transport")
        root = Path(__file__).resolve().parents[2]
        names = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            text=True,
        ).splitlines()
        hashes = {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest()
            for n in set(names)
            if (root / n).is_file()
        }
        modules = frozenset(
            {"pygrc.models.grc_v4_lifecycle", "tests.models.test_grc_v4_lifecycle"}
        )
        _p941_loaded_sources(root, hashes, extra_modules=modules)
        # Both replacement methods originate in the correct file and compile
        # from it. Checking only live code by its own qualname would miss this.
        for cls, name, other in (
            (CandidateCOSOperation, "step_v4", "_execute"),
            (
                CandidateCOSOperationTests,
                "test_native_corrector_conditioning_failure",
                "test_fresh_owner_rejects_unauthenticated_ledger_and_foreign_domains",
            ),
        ):
            with (
                patch.object(cls, name, getattr(cls, other)),
                self.assertRaisesRegex(
                    RuntimeError, "loaded code differs from snapshot"
                ),
            ):
                _p941_loaded_sources(root, hashes, extra_modules=modules)
        _p941_loaded_sources(root, hashes, extra_modules=modules)

    def test_native_reference_only_poststate_singularity_rejects_after_valid_consumed_final(
        self,
    ) -> None:
        # Full selector, kappa_M=.5: literal retained Hodge at reference h=2
        # and C=(3,1), using the declared binary64 exponential then exact
        # congruence and one rounding. Choose beta so 1-beta+2*tau*H_M=0
        # EXACTLY on those stored values; this is not a near-singular label.
        deformation = math.exp(0.25 * (0.5 * (math.tanh(3) + math.tanh(1))))
        retained = float(2 * Fraction(deformation) ** 2)
        beta = 1 + 2 * retained
        self.assertEqual(1 - Fraction(beta) + 2 * Fraction(retained), 0)
        initial = GRCV4AuthoritativeState((4, 0), None, None)
        inputs = replace(
            os_fixture(
                candidate={
                    "kappa_M_C": 0.5,
                    "tau_C": 1,
                    "chi_C": 1,
                    "zeta_C": beta,
                    "Lambda_C": 10,
                },
                geometry={"kappa_H": 0.0001},
                charge={"absolute_tolerance": 0},
            ),
            current=initial,
            reset=initial,
        )
        # The actual corrector determines a positive duration giving the exact
        # stored target (3,1). No current/source/geometry is injected.
        current = CandidateCOSPass(inputs).corrector.current.values[0]
        self.assertGreater(current, 0)
        dt = 1 / current
        provisional = ProvisionalCandidateCOSStep(replace(inputs, dt=dt))
        self.assertEqual(provisional.next_inputs.current.C, (3, 1))
        self.assertIsNotNone(provisional.final)
        assert provisional.final is not None
        self.assertNotEqual(provisional.final.inputs.geometry, inputs.geometry)
        with self.assertRaisesRegex(CandidateCStageError, "singular"):
            CandidateCCurrent(provisional.next_inputs)
        owner = CandidateCOSOperation(inputs)
        self.assert_atomic(
            owner, request(dt), "final_reconstruction", "valid_root", "domain_failure"
        )

    def test_empty_edge_declarations_reject_and_loop_only_operation_commits(
        self,
    ) -> None:
        for graph, weights, resource in (
            (GRCV4Graph((), ()), {}, ()),
            (GRCV4Graph(("v",), ()), {}, (3,)),
            (
                GRCV4Graph(("v",), (OrientedEdge("loop", "v", "v"),)),
                {"loop": 2.0},
                (3,),
            ),
        ):
            if not graph.oriented_edges:
                # Frozen reference-Hodge schema requires a nonempty W map;
                # the numerical empty-space helpers do not expand that domain.
                with self.assertRaisesRegex(ValueError, "edge_weights.*non-empty"):
                    current_fixture(graph=graph, weights=weights, resource=resource)
                continue
            inputs = current_fixture(graph=graph, weights=weights, resource=resource)
            owner = CandidateCOSOperation(inputs)
            result = owner.step_v4(request(0.125))
            self.assertTrue(result.committed)
            self.assertEqual(owner.state.current.C, resource)
            self.assertEqual(len(owner.state.receipt_ledger), 4)

    def test_dense_nonidentity_multigraph_operation_and_signed_covariance(self) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("ac", "a", "c"),
                OrientedEdge("parallel", "a", "b"),
                OrientedEdge("loop", "c", "c"),
            ),
        )
        changes: dict[str, dict[str, Any]] = {
            "candidate": {"Lambda_C": 1, "kappa_M_C": 0.4},
            "geometry": {"kappa_H": 0.0001},
            "realization": {"tolerance": 1},
            "charge": {"absolute_tolerance": 1e-11},
        }
        weights: dict[str, float] = {"ab": 2, "ac": 3, "parallel": 4, "loop": 5}
        inputs = replace(
            current_fixture(
                graph=graph, weights=weights, resource=(1, 2, 4, 7), changes=changes
            ),
            dt=1e-6,
        )
        expected = dense_pass(inputs)
        owner = CandidateCOSOperation(inputs)
        result: Any = owner.step_v4(request(inputs.dt))
        self.assertTrue(result.committed)
        np.testing.assert_allclose(
            result.observables["os"]["current"],
            expected["corrector"]["current"],
            rtol=2e-12,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            owner.state.current.C, expected["resource"], rtol=2e-14, atol=0
        )
        self.assertEqual(owner.state.current.C[3], 7)
        edge_order, vertex_order, signs = (3, 1, 0, 2), (2, 0, 3, 1), (-1, 1, -1, 1)
        transformed = GRCV4Graph(
            tuple(graph.live_node_ids[i] for i in vertex_order),
            tuple(
                OrientedEdge(
                    graph.oriented_edges[i].edge_id,
                    graph.oriented_edges[i].tail_node_id
                    if sign == 1
                    else graph.oriented_edges[i].head_node_id,
                    graph.oriented_edges[i].head_node_id
                    if sign == 1
                    else graph.oriented_edges[i].tail_node_id,
                )
                for i, sign in zip(edge_order, signs)
            ),
        )
        other = CandidateCOSOperation(
            current_fixture(
                graph=transformed,
                weights=weights,
                resource=tuple(inputs.current.C[i] for i in vertex_order),
                changes=changes,
            )
        )
        moved: Any = other.step_v4(request(inputs.dt))
        self.assertTrue(moved.committed)
        np.testing.assert_allclose(
            other.state.current.C,
            [owner.state.current.C[i] for i in vertex_order],
            rtol=2e-14,
            atol=0,
        )
        np.testing.assert_allclose(
            moved.observables["os"]["current"],
            [
                result.observables["os"]["current"][i] * sign
                for i, sign in zip(edge_order, signs)
            ],
            rtol=2e-12,
            atol=1e-12,
        )
        # Coordinate-reordered graphs have different content IDs; covariance
        # compares physical fields, never digests or eigenvector signs.
        self.assertNotEqual(
            other.state.scientific_state_digest, owner.state.scientific_state_digest
        )

    def test_repeated_cluster_projector_and_near_conditioning_boundary_operations(
        self,
    ) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (OrientedEdge("e", "a", "b"), OrientedEdge("f", "c", "d")),
        )
        for cutoff in (2, 8):
            inputs = current_fixture(
                graph=graph,
                weights={"e": 2, "f": 2},
                resource=(3, 1, 3, 1),
                changes={
                    "candidate": {
                        "Lambda_C": cutoff,
                        "tau_C": 0,
                        "kappa_M_C": 0,
                        "chi_C": 1,
                        "zeta_C": 3,
                    },
                    "geometry": {"kappa_H": 0},
                    "solver": {"conditioning_limit": 1},
                },
            )
            expected = (
                np.eye(4) if cutoff == 8 else np.kron(np.eye(2), np.ones((2, 2)) / 2)
            )
            # Two repeated zero modes and two repeated eigenvalue-4 modes.
            np.testing.assert_allclose(
                CandidateCCurrent(inputs).algebra.selector.projector,
                expected,
                rtol=0,
                atol=2e-15,
            )
            owner = CandidateCOSOperation(inputs)
            self.assertTrue(owner.step_v4(request(0.125)).committed)
            self.assertEqual(
                owner.state.current.C,
                (2.5, 1.5, 2.5, 1.5),
            )
        for limit, admitted in (
            (math.nextafter(4, math.inf), True),
            (math.nextafter(4, 0), False),
        ):
            inputs = current_fixture(
                graph=graph,
                weights={"e": 2, "f": 8},
                resource=(2, 2, 2, 2),
                changes={
                    "candidate": {
                        "Lambda_C": 20,
                        "tau_C": 0,
                        "kappa_M_C": 0,
                        "chi_C": 0,
                    },
                    "geometry": {"kappa_H": 0},
                    "solver": {"conditioning_limit": limit},
                },
            )
            if admitted:
                owner = CandidateCOSOperation(inputs)
                self.assertTrue(owner.step_v4(request(0.125)).committed)
            else:
                with self.assertRaisesRegex(ValueError, "conditioning"):
                    CandidateCOSOperation(inputs)

    def test_connected_repeated_cluster_uses_general_certificate_and_covaries(
        self,
    ) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            tuple(
                OrientedEdge(str(i), a, b)
                for i, (a, b) in enumerate(zip("abcd", "bcda"))
            ),
        )
        changes: dict[str, dict[str, Any]] = {
            "candidate": {
                "Lambda_C": 3,
                "kappa_M_C": 0.25,
                "chi_C": 0.5,
                "zeta_C": 0.5,
            },
            "geometry": {"kappa_H": 0.0001},
            "realization": {"tolerance": 1},
            "charge": {"absolute_tolerance": 1e-11},
        }
        weights = {str(i): 1.0 for i in range(4)}
        inputs = current_fixture(
            graph=graph, weights=weights, resource=(3, 2, 1, 2), changes=changes
        )
        # Connected cycle: spectrum 0,2,2,4; exclude alternating unit mode.
        alternating = np.array([1, -1, 1, -1]) / 2
        expected_projector = np.eye(4) - np.outer(alternating, alternating)
        current = CandidateCCurrent(inputs)
        selector = current.algebra.selector
        self.assertEqual(selector.rank, 3)
        self.assertEqual(
            selector.certificate["method"],
            "exact_inertia_and_generalized_eigen_residual",
        )
        self.assertGreater(Fraction(str(selector.certificate["gap_lower"])), 0)
        np.testing.assert_allclose(
            selector.projector, expected_projector, rtol=0, atol=2e-15
        )
        expected = dense_pass(replace(inputs, dt=1e-6))
        owner = CandidateCOSOperation(inputs)
        result: Any = owner.step_v4(request(1e-6))
        self.assertTrue(result.committed)
        np.testing.assert_allclose(
            owner.state.current.C, expected["resource"], rtol=2e-14, atol=0
        )
        vertex_order, edge_order, signs = (2, 0, 3, 1), (3, 1, 0, 2), (-1, 1, -1, 1)
        transformed = GRCV4Graph(
            tuple(graph.live_node_ids[i] for i in vertex_order),
            tuple(
                OrientedEdge(
                    graph.oriented_edges[i].edge_id,
                    graph.oriented_edges[i].tail_node_id
                    if sign == 1
                    else graph.oriented_edges[i].head_node_id,
                    graph.oriented_edges[i].head_node_id
                    if sign == 1
                    else graph.oriented_edges[i].tail_node_id,
                )
                for i, sign in zip(edge_order, signs)
            ),
        )
        other_inputs = current_fixture(
            graph=transformed,
            weights=weights,
            resource=tuple(inputs.current.C[i] for i in vertex_order),
            changes=changes,
        )
        other_selector = CandidateCCurrent(other_inputs).algebra.selector
        self.assertEqual(
            other_selector.certificate["method"], selector.certificate["method"]
        )
        np.testing.assert_allclose(
            other_selector.projector,
            expected_projector[np.ix_(vertex_order, vertex_order)],
            rtol=0,
            atol=2e-15,
        )
        other = CandidateCOSOperation(other_inputs)
        moved: Any = other.step_v4(request(1e-6))
        self.assertTrue(moved.committed)
        np.testing.assert_allclose(
            other.state.current.C,
            np.array(owner.state.current.C)[list(vertex_order)],
            rtol=2e-14,
            atol=0,
        )
        np.testing.assert_allclose(
            moved.observables["os"]["current"],
            np.array(result.observables["os"]["current"])[list(edge_order)] * signs,
            rtol=2e-12,
            atol=1e-12,
        )

    def test_dense_conditioning_certificate_operation_inside_and_outside_limit(
        self,
    ) -> None:
        import pygrc.models.grc_v4_candidate_c as module

        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            tuple(
                OrientedEdge(str(i), a, b)
                for i, (a, b) in enumerate(zip("abcd", "bcda"))
            ),
        )
        # Analytic cycle modes: predictor J=(-4,4,-4,4), causal flat=J/2.
        # Star gives H1=I+(B^T B)/256 exactly. Resolvent input has eigenvalues
        # 1, 385/256,385/256,129/64. Its condition is exactly 129/64.
        # Margins exceed eigensolver rounding; they do not relax the policy.
        boundary = 129 / 64
        for limit, admitted in ((boundary + 2**-35, True), (boundary - 2**-35, False)):
            inputs = current_fixture(
                graph=graph,
                weights={str(i): 1 for i in range(4)},
                resource=(3, 1, 3, 1),
                changes={
                    "candidate": {
                        "Lambda_C": 10,
                        "kappa_M_C": 0,
                        "tau_C": 0.25,
                        "eta_C": 0.375,
                        "chi_C": 1,
                        "zeta_C": 0.5,
                    },
                    "geometry": {"kappa_H": 2**-8},
                    "realization": {"tolerance": 1},
                    "solver": {"conditioning_limit": limit},
                    "charge": {"absolute_tolerance": 1e-11},
                },
            )
            owner = CandidateCOSOperation(inputs)
            observed: list[Any] = []
            original = module._c_condition

            def observe(matrix: Any, declared: float, label: str) -> Any:
                if label == "retained resolvent":
                    observed.append(matrix)
                return original(matrix, declared, label)

            with (
                self.subTest(limit=limit),
                patch.object(module, "_c_condition", side_effect=observe),
                patch.object(np.linalg, "svd", wraps=np.linalg.svd) as svd,
                patch.object(module, "_c_inertia", wraps=module._c_inertia) as inertia,
            ):
                if admitted:
                    result = owner.step_v4(request(2**-12))
                    self.assertTrue(result.committed)
                else:
                    self.assert_atomic(
                        owner,
                        request(2**-12),
                        "candidate_solve",
                        "conditioning_failure",
                        "conditioning_failure",
                    )
                self.assertTrue(
                    any(
                        np.asarray(call.args[0]).shape == (4, 4)
                        for call in svd.call_args_list
                    )
                )
                self.assertGreater(inertia.call_count, 0)
            b = np.array(graph.incidence)
            delta = b.T @ b
            expected = np.eye(4) + 0.25 * delta @ (np.eye(4) + delta / 256)
            self.assertTrue(
                any(np.array_equal(matrix, expected) for matrix in observed)
            )
            self.assertTrue(np.any(expected - np.diag(np.diag(expected))))

    def test_native_corrector_conditioning_failure(self) -> None:
        inputs = current_fixture(
            graph=GRCV4Graph(
                ("a", "b", "c", "d"),
                (OrientedEdge("e", "a", "b"), OrientedEdge("f", "c", "d")),
            ),
            weights={"e": 1, "f": 1},
            resource=(3, 1, 2, 2),
            changes={
                "candidate": {
                    "tau_C": 0,
                    "chi_C": 1,
                    "zeta_C": 3,
                    "kappa_M_C": 0,
                    "Lambda_C": 10,
                },
                "geometry": {"kappa_H": 1},
                "solver": {"conditioning_limit": 2},
                "realization": {"tolerance": 100},
            },
        )
        owner = CandidateCOSOperation(inputs)
        self.assert_atomic(
            owner,
            request(0.001),
            "candidate_solve",
            "conditioning_failure",
            "conditioning_failure",
        )

    def assert_atomic(
        self,
        owner: CandidateCOSOperation,
        req: GRCV4StepRequestInput,
        stage: str,
        solver: str | None,
        code: str,
    ) -> Any:
        before, encoded = owner.state, owned_bytes(owner)
        reference = owner.reference
        reference_bytes = canonical_json_bytes(reference.to_payload())
        reference_id = reference.identity
        result: Any = owner.step_v4(req)
        self.assertFalse(result.committed)
        self.assertEqual(result.operation_disposition, "rejected")
        self.assertEqual(result.solver_disposition, solver)
        self.assertIsNone(result.commit_id)
        self.assertIsNotNone(result.failure)
        assert result.failure is not None
        self.assertEqual((result.failure.stage, result.failure.code), (stage, code))
        self.assertEqual(result.failure.prestate_digest, before.scientific_state_digest)
        self.assertEqual(
            result.failure.poststate_digest, before.scientific_state_digest
        )
        self.assertEqual(result.failure.pre_lifecycle_digest, before.lifecycle_digest)
        self.assertEqual(result.failure.post_lifecycle_digest, before.lifecycle_digest)
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertEqual(
            result.emitted_receipts[0].identity_payload.operation_id, req.operation_id
        )
        self.assertIs(owner.state, before)
        self.assertEqual(owned_bytes(owner), encoded)
        self.assertIs(owner.reference, reference)
        self.assertEqual(owner.reference.identity, reference_id)
        self.assertEqual(
            canonical_json_bytes(owner.reference.to_payload()), reference_bytes
        )
        return result

    def test_positive_nonzero_split_matches_rational_oracle_and_one_publication(
        self,
    ) -> None:
        import pygrc.models.grc_v4_step as step_module
        import pygrc.models.grc_v4_realizations as os_module
        import pygrc.models.grc_v4_lifecycle as owner_module

        inputs = os_fixture()
        expected = scalar_pass(inputs)
        owner = CandidateCOSOperation(inputs)
        before = owned_bytes(owner)
        stages: list[GeometryStageInputs] = []
        original = CandidateCCurrent

        def observe(x: GeometryStageInputs) -> CandidateCCurrent:
            self.assertEqual(owned_bytes(owner), before)
            stages.append(x)
            return original(x)

        with (
            patch.object(os_module, "CandidateCCurrent", side_effect=observe),
            patch.object(step_module, "CandidateCCurrent", side_effect=observe),
            patch.object(owner_module, "CandidateCCurrent", side_effect=observe),
            patch.object(
                step_module,
                "provisional_continuity",
                wraps=getattr(step_module, "provisional_continuity"),
            ) as writer,
            patch.object(
                os_module, "H_profile", wraps=getattr(os_module, "H_profile")
            ) as geometry,
        ):
            result: Any = owner.step_v4(request(inputs.dt))
        self.assertTrue(result.committed)
        self.assertEqual(result.solver_disposition, "valid_root")
        self.assertEqual(writer.call_count, 1)
        self.assertEqual(geometry.call_count, 2)  # update and residual operand only
        observed = result.observables.to_dict()
        self.assertAlmostEqual(
            observed["os"]["current"][0], float(expected["corrector"]), delta=2e-14
        )
        self.assertAlmostEqual(
            observed["os"]["split_residual"][0][0],
            float(expected["residual"]),
            delta=2e-14,
        )
        self.assertNotEqual(observed["os"]["split_residual"], [[0]])
        # Canonical incidence is (+tail, -head); use the consumed binary64 J
        # for the declared once-rounded resource arithmetic, not exact rational J.
        j = Fraction(observed["os"]["current"][0])
        expected_c = tuple(
            float(Fraction(c) - Fraction(inputs.dt) * sign * j)
            for c, sign in zip((3, 1), (1, -1))
        )
        self.assertEqual(owner.state.current.C, expected_c)
        self.assertEqual(
            [s.stage for s in stages],
            [
                "reset_readmission",
                "os_predictor",
                "os_corrector",
                "post_continuity",
                "pre_read",
            ],
        )
        self.assertEqual(stages[-1].geometry, inputs.geometry.reference.geometry())
        self.assertNotEqual(stages[-2].geometry, stages[-1].geometry)
        self.assertEqual(stages[-1].current, owner.state.current)
        self.assertNotEqual(stages[-1].current, inputs.current)
        self.assertEqual(owner.state.reset.authoritative, inputs.reset)
        self.assertEqual(len(owner.state.receipt_ledger), 4)

    def test_exact_dyadic_receipts_commit_and_whole_state_identity(self) -> None:
        inputs = dyadic_fixture()
        owner = CandidateCOSOperation(inputs)
        source: Any = inputs.scientific_state_preimage
        result: Any = owner.step_v4(request(0.125, "dyadic"))
        self.assertTrue(result.committed)
        self.assertEqual(owner.state.current.C, (2.5, 1.5))
        target: Any = replace(
            inputs,
            current=GRCV4AuthoritativeState((2.5, 1.5), None, None),
            step_index=1,
            time=0.125,
        ).scientific_state_preimage
        # The independent ASCII/dyadic codec covers scientific/receipt/commit
        # preimages here; arbitrary profile parameter serialization is not claimed.
        self.assertEqual(owner.state.scientific_state_digest, scientific_id(target))
        envelopes = [r.to_payload() for r in result.emitted_receipts]
        ids = []
        for envelope in envelopes:
            payload = envelope["identity_payload"]
            ids.append(identity("grc-receipt-sha256", payload))
            self.assertEqual(envelope["receipt_id"], ids[-1])
            core = payload["core"]
            self.assertEqual(core["operation_id"], "dyadic")
            self.assertEqual(core["source_state_digest"], scientific_id(source))
            self.assertEqual(core["target_state_digest"], scientific_id(target))
            for prefix, preimage in (("source", source), ("target", target)):
                self.assertEqual(
                    core[prefix + "_authoritative_digest"],
                    identity(
                        "grcv4-authoritative-sha256",
                        {
                            "schema_version": "grcv4-authoritative-state-identity-v1",
                            "authoritative": preimage["authoritative"],
                        },
                    ),
                )
                self.assertEqual(core[prefix + "_reset_digest"], inputs.reset_id)
                self.assertEqual(
                    core[prefix + "_graph_digest"],
                    inputs.geometry.reference.graph.graph_digest,
                )
                self.assertEqual(
                    core[prefix + "_model_identity"],
                    inputs.geometry.reference.profile.complete_profile_id,
                )
            self.assertEqual(core["actual_charge_delta"], 0)
            self.assertEqual(core["parent_receipt_ids"], [])
            self.assertEqual(core["information_losses"], [])
            relocation = {
                "schema_version": "grcv4-resource-transform-identity-v1",
                "transform": {
                    "schema_version": "grcv4-resource-event-transform-v1",
                    "policy_id": "identity_resource_transport_v1",
                    "source_vertex_ids": ["u", "v"],
                    "target_vertex_ids": ["u", "v"],
                    "row_major_coefficients": [1, 0, 0, 1],
                    "target_increment": [0, 0],
                },
            }
            self.assertEqual(
                core["resource_transform_digest"],
                identity("grcv4-resource-transform-sha256", relocation),
            )
            history: dict[str, Any] = {
                "schema_version": "grcv4-history-bundle-policy-v1"
            }
            for subject, policy, disposition in (
                (
                    "candidate",
                    inputs.geometry.reference.profile.params_resolved.lifecycle.history_policy_id,
                    "rederived",
                ),
                ("carrier", "no_persistent_carrier_v1", "not_applicable"),
            ):
                history[subject] = {
                    "schema_version": "grcv4-history-channel-policy-v1",
                    "subject": subject,
                    "policy_id": policy,
                    "disposition": disposition,
                    "source_history_digest": None,
                    "target_initializer_id": None,
                    "information_loss": "none",
                }
            self.assertEqual(
                core["history_bundle_digest"],
                identity(
                    "grcv4-history-map-sha256",
                    {
                        "schema_version": "grcv4-history-bundle-identity-v1",
                        "history_bundle": history,
                    },
                ),
            )
        expected_commit = identity(
            "grc-commit-sha256",
            {
                "schema_version": "grcv4-commit-payload-v1",
                "operation_id": "dyadic",
                "source_state_digest": scientific_id(source),
                "target_state_digest": scientific_id(target),
                "emitted_receipt_ids": ids,
                "target_step_index": 1,
                "target_time": 0.125,
            },
        )
        self.assertEqual(result.commit_id, expected_commit)
        self.assertTrue(all(e["commit_id"] == expected_commit for e in envelopes))
        self.assertEqual([r.to_dict() for r in owner.state.receipt_ledger], envelopes)
        self.assertEqual(owner.state.lifecycle_digest, lifecycle_id(target, envelopes))
        self.assertEqual(result.observables["reference_current"]["values"], (2,))
        self.assertEqual(
            [e["identity_payload"]["schema_version"] for e in envelopes],
            [
                "grcv4-step-commit-receipt-v1",
                "grcv4-charge-receipt-v1",
                "grcv4-history-disposition-receipt-v1",
                "grcv4-history-disposition-receipt-v1",
            ],
        )
        self.assertEqual(
            [e["identity_payload"].get("history_disposition") for e in envelopes[2:]],
            ["rederived", "not_applicable"],
        )
        self.assertEqual(
            {k: v for k, v in envelopes[1]["identity_payload"].items() if k != "core"},
            {
                "schema_version": "grcv4-charge-receipt-v1",
                "target_charge": 4,
                "admitted_charge": 4,
                "residual": 0,
            },
        )

    def test_two_beats_use_actual_request_poststate_ledger_and_reference(self) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        first: Any = owner.step_v4(request(0.125, "first"))
        first_state = owner.state
        import pygrc.models.grc_v4_realizations as module

        with patch.object(
            module, "CandidateCCurrent", wraps=CandidateCCurrent
        ) as rebuilt:
            second: Any = owner.step_v4(request(0.25, "second"))
        predictor = rebuilt.call_args_list[0].args[0]
        self.assertEqual(predictor.current, first_state.current)
        self.assertEqual(predictor.operation_id, "second")
        self.assertEqual(predictor.dt, 0.25)
        self.assertEqual(
            predictor.receipt_ids,
            tuple(r["receipt_id"] for r in first_state.receipt_ledger),
        )
        self.assertEqual(predictor.geometry, owner.reference.geometry())
        self.assertTrue(second.committed)
        self.assertEqual(owner.state.current.C, (2, 2))
        self.assertEqual((owner.state.step_index, owner.state.time), (2, 0.375))
        self.assertEqual(len(owner.state.receipt_ledger), 8)
        self.assertEqual(len(second.emitted_receipts), 4)
        for receipt in second.emitted_receipts:
            core = receipt.identity_payload["core"]
            self.assertEqual(core["operation_id"], "second")
            self.assertEqual(
                core["source_state_digest"], first_state.scientific_state_digest
            )
            self.assertEqual(
                core["parent_receipt_ids"], (first.emitted_receipts[0].receipt_id,)
            )
        self.assertEqual(second.observables["os"]["current"], (2,))

    def test_zero_duration_identity_no_writer_but_authenticated_receipt_delta(
        self,
    ) -> None:
        import pygrc.models.grc_v4_step as module

        owner = CandidateCOSOperation(dyadic_fixture())
        source = owner.state
        with (
            patch.object(module, "CandidateCOSPass", side_effect=AssertionError("OS")),
            patch.object(
                module, "provisional_continuity", side_effect=AssertionError("writer")
            ),
        ):
            result: Any = owner.step_v4(request(0))
            repeat: Any = owner.step_v4(request(0))  # no unspecified unique-ID policy
        self.assertTrue(result.committed and repeat.committed)
        self.assertEqual(owner.state.current, source.current)
        self.assertEqual(
            owner.state.scientific_state_digest, source.scientific_state_digest
        )
        self.assertNotEqual(owner.state.lifecycle_digest, source.lifecycle_digest)
        self.assertNotEqual(result.commit_id, repeat.commit_id)
        self.assertEqual((owner.state.step_index, owner.state.time), (0, 0))
        self.assertEqual(result.observables["continuity_evaluations"], 0)
        self.assertNotIn("os", result.observables)
        self.assertEqual(len(owner.state.receipt_ledger), 8)

    def test_negative_duration_and_closed_external_inputs_fail_before_solver(
        self,
    ) -> None:
        import pygrc.models.grc_v4_lifecycle as module

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        post: Any = replace(
            dyadic_fixture(), current=owner.state.current, step_index=1, time=0.125
        ).scientific_state_preimage
        ledger: Any = [r.to_dict() for r in owner.state.receipt_ledger]
        with patch.object(
            module, "ProvisionalCandidateCOSStep", side_effect=AssertionError("solver")
        ):
            for dt in (-1, -math.ulp(0.0), -1.7e308):
                result = self.assert_atomic(
                    owner, request(dt), "admission", None, "invalid_duration"
                )
                expected = expected_negative(
                    cast(Any, request(dt).to_payload()), post, ledger
                )
                self.assertEqual(
                    [r.to_payload() for r in result.emitted_receipts],
                    expected["emitted_receipts"],
                )
                self.assertEqual(
                    owner.state.lifecycle_digest, expected["post_lifecycle_digest"]
                )
            for field in ("context_value", "boundary_input", "external_source"):
                self.assert_atomic(
                    owner,
                    GRCV4StepRequestInput.from_payload(
                        {**request(0).to_payload(), field: {"foreign": 1}}
                    ),
                    "admission",
                    None,
                    "domain_failure",
                )

    def test_duration_and_clock_extremes_keep_classification_and_atomicity(
        self,
    ) -> None:
        owner = CandidateCOSOperation(replace(dyadic_fixture(), time=1))
        result: Any = owner.step_v4(request(math.ulp(0.0)))
        self.assertTrue(result.committed)
        self.assertEqual(result.observables["continuity_evaluations"], 1)
        self.assertEqual((owner.state.step_index, owner.state.time), (1, 1))
        self.assertEqual(owner.state.current.C, (3, 1))
        owner = CandidateCOSOperation(replace(dyadic_fixture(), step_index=2**53 - 1))
        self.assert_atomic(
            owner, request(math.ulp(0.0)), "admission", None, "domain_failure"
        )
        self.assertTrue(owner.step_v4(request(0)).committed)
        owner = CandidateCOSOperation(replace(dyadic_fixture(), time=1.7e308))
        self.assert_atomic(
            owner, request(1.7e308), "admission", None, "nonfinite_value"
        )
        owner = CandidateCOSOperation(
            replace(
                dyadic_fixture(), current=GRCV4AuthoritativeState((2, 2), None, None)
            )
        )
        result = owner.step_v4(request(float.fromhex("0x1.fffffffffffffp+1023")))
        self.assertTrue(result.committed)
        self.assertEqual(owner.state.current.C, (2, 2))
        self.assertEqual(result.observables["continuity_evaluations"], 1)

    def test_native_solver_geometry_selector_and_split_failures_are_atomic(
        self,
    ) -> None:
        cases = [
            (os_fixture(geometry={"kappa_H": -4}), "domain_failure", "domain_failure"),
            (
                os_fixture(
                    candidate={"zeta_C": 3, "chi_C": 1}, geometry={"kappa_H": 1 / 24}
                ),
                "singular",
                "singular_solver",
            ),
            (os_fixture(geometry={"kappa_H": 1.7e308}), "nonfinite", "nonfinite_value"),
            (
                os_fixture(candidate={"Lambda_C": 4.1}),
                "domain_failure",
                "domain_failure",
            ),
            (
                os_fixture(realization={"tolerance": 0}),
                "domain_failure",
                "domain_failure",
            ),
            (
                replace(
                    os_fixture(
                        solver={"absolute_tolerance": 0, "relative_tolerance": 0}
                    ),
                    current=GRCV4AuthoritativeState((8, 1), None, None),
                    reset=GRCV4AuthoritativeState((8, 1), None, None),
                    Q_target=9,
                ),
                "no_admitted_root",
                "no_admitted_root",
            ),
        ]
        for inputs, solver, code in cases:
            with self.subTest(solver=solver, code=code):
                owner = CandidateCOSOperation(inputs)
                self.assert_atomic(
                    owner, request(inputs.dt), "candidate_solve", solver, code
                )

    def test_native_postsolve_resource_domain_overflow_and_charge_failures(
        self,
    ) -> None:
        for dt, stage, code in (
            (1, "charge_admission", "domain_failure"),
            (1.7e308, "continuity", "nonfinite_value"),
        ):
            owner = CandidateCOSOperation(os_fixture())
            self.assert_atomic(owner, request(dt), stage, "valid_root", code)
        owner = CandidateCOSOperation(charge_fixture(0))
        self.assert_atomic(
            owner, request(1), "charge_admission", "valid_root", "charge_failure"
        )
        # Failed attempts do not append their failure receipt; a valid retry
        # operates from precisely the original state and empty ledger.
        self.assertTrue(owner.step_v4(request(0, "retry")).committed)
        self.assertEqual(len(owner.state.receipt_ledger), 4)

    def test_native_charge_tolerance_boundary_commits_without_resource_repair(
        self,
    ) -> None:
        owner = CandidateCOSOperation(charge_fixture(2))
        result: Any = owner.step_v4(request(1))
        self.assertTrue(result.committed)
        self.assertEqual(owner.state.current.C, (float(2**53 - 1), 1, 1, 2))
        charge = result.emitted_receipts[1].identity_payload
        self.assertEqual(charge["residual"], 2)
        self.assertEqual(charge["core"]["actual_charge_delta"], 2)
        self.assertEqual(owner.state.Q_target, float(2**53 + 2))
        self.assertEqual(owner.state.reset.authoritative.C, (float(2**53), 1, 1, 1))

    def test_fault_controls_final_consumed_and_reference_readmission_are_atomic(
        self,
    ) -> None:
        import pygrc.models.grc_v4_lifecycle as owner_module
        import pygrc.models.grc_v4_step as step_module

        for reference in (False, True):
            for disposition, code in (
                ("singular", "domain_failure"),
                ("nonfinite", "nonfinite_value"),
            ):
                owner = CandidateCOSOperation(os_fixture())
                before = owner.state
                original = CandidateCCurrent

                def fail(x: GeometryStageInputs) -> CandidateCCurrent:
                    if x.current != before.current and (
                        reference or x.stage == "post_continuity"
                    ):
                        raise CandidateCStageError(
                            cast(SolverDisposition, disposition),
                            "singular nonfinite valid_root",
                        )
                    return original(x)

                with (
                    self.subTest(reference=reference, disposition=disposition),
                    patch.object(
                        owner_module if reference else step_module,
                        "CandidateCCurrent",
                        side_effect=fail,
                    ),
                ):
                    self.assert_atomic(
                        owner,
                        request(2**-10),
                        "final_reconstruction",
                        "valid_root",
                        code,
                    )
                self.assertTrue(owner.step_v4(request(0)).committed)

    def test_fault_controls_charge_types_override_hostile_text(self) -> None:
        import pygrc.models.grc_v4_transport as transport
        from pygrc.models.grc_v4_geometry import NonfiniteGeometryError, VertexScalar

        # Originating arithmetic boundaries, with no message classifier.
        graph = GRCV4Graph(("a", "b"), (OrientedEdge("e", "a", "b"),))
        with self.assertRaises(transport.ChargeDomainError):
            transport.unit_charge(VertexScalar(graph, (-1, 2)))
        with self.assertRaises(NonfiniteGeometryError):
            transport.unit_charge(VertexScalar(graph, (1.7e308, 1.7e308)))
        with self.assertRaises(NonfiniteGeometryError):
            transport.ChargeEvaluation(
                VertexScalar(graph, (1.7e308, 0)),
                -1.7e308,
                os_fixture().geometry.reference.profile,
            )
        for kind, code in (
            (transport.ChargeDomainError, "domain_failure"),
            (NonfiniteGeometryError, "nonfinite_value"),
        ):
            owner = CandidateCOSOperation(dyadic_fixture())
            before = owner.state.current.C
            original = transport.unit_charge

            def fail(resource: VertexScalar) -> float:
                if resource.values != before:
                    raise kind("singular nonfinite valid_root")
                return original(resource)

            with (
                self.subTest(kind=kind),
                patch.object(transport, "unit_charge", side_effect=fail),
            ):
                self.assert_atomic(
                    owner, request(0.125), "charge_admission", "valid_root", code
                )

    def test_fault_controls_every_solver_disposition_has_typed_provenance(self) -> None:
        import pygrc.models.grc_v4_realizations as module

        for disposition, code in (
            ("domain_failure", "domain_failure"),
            ("singular", "singular_solver"),
            ("conditioning_failure", "conditioning_failure"),
            ("nonfinite", "nonfinite_value"),
            ("no_admitted_root", "no_admitted_root"),
            ("multiple_admitted_roots", "multiple_admitted_roots"),
        ):
            owner = CandidateCOSOperation(os_fixture())
            # Same deliberately misleading message for all typed causes.
            with (
                self.subTest(disposition=disposition),
                patch.object(
                    module,
                    "CandidateCCurrent",
                    side_effect=CandidateCStageError(
                        cast(SolverDisposition, disposition),
                        "singular nonfinite valid_root",
                    ),
                ),
            ):
                self.assert_atomic(
                    owner, request(2**-10), "candidate_solve", disposition, code
                )

        # A nonfinite backend intermediate is not a finite loss of a declared
        # conditioning margin. Test the originating numerical classifier.
        from pygrc.models.grc_v4_candidate_c import _c_condition

        with (
            patch.object(np.linalg, "svd", return_value=np.array([float("nan"), 1, 1])),
            self.assertRaises(CandidateCStageError) as failure,
        ):
            _c_condition(((1, 0.5, 0), (0, 1, 0.5), (0, 0, 1)), 100, "control")
        self.assertEqual(failure.exception.disposition, "nonfinite")
        # Reset readmission precedes the candidate solve. Its nonfinite cause
        # remains visible while the solver disposition stays null.
        import pygrc.models.grc_v4_step as step_module

        owner = CandidateCOSOperation(os_fixture())
        with patch.object(
            step_module,
            "CandidateCCurrent",
            side_effect=CandidateCStageError("nonfinite", "injected reset nonfinite"),
        ):
            self.assert_atomic(
                owner,
                request(2**-10),
                "pre_read_reconstruction",
                None,
                "nonfinite_value",
            )

    def test_fault_controls_receipt_construction_binding_and_exceptions_before_publish(
        self,
    ) -> None:
        import pygrc.models.grc_v4_lifecycle as module
        import pygrc.models.grc_v4_realizations as os_module
        import pygrc.models.grc_v4_step as step_module

        for target, name in (
            *(
                (module, name)
                for name in (
                    "_ordinary_receipts",
                    "make_commit_receipts",
                    "_lifecycle_state",
                    "GRCV4StepResult",
                    "bind_step_result",
                )
            ),
            (os_module, "CandidateCCurrent"),
            (step_module, "CandidateCCurrent"),
            (step_module, "ChargeEvaluation"),
            (step_module, "provisional_continuity"),
        ):
            for kind in (ValueError, V4IdentityError, RuntimeError):
                owner = CandidateCOSOperation(dyadic_fixture())
                before, encoded = owner.state, owned_bytes(owner)
                reference = owner.reference
                reference_bytes = canonical_json_bytes(reference.to_payload())
                fault = kind("injected prepublication failure")
                with (
                    self.subTest(name=name, kind=kind),
                    patch.object(target, name, side_effect=fault),
                    self.assertRaises(kind) as raised,
                ):
                    owner.step_v4(request(0.125))
                self.assertIs(raised.exception, fault)
                self.assertIs(owner.state, before)
                self.assertEqual(owned_bytes(owner), encoded)
                self.assertIs(owner.reference, reference)
                self.assertEqual(
                    canonical_json_bytes(owner.reference.to_payload()), reference_bytes
                )

    def test_no_cache_input_and_immutable_detached_observations(self) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        encoded = owned_bytes(owner)
        with self.assertRaises(AttributeError):
            owner.cached_current = [999]  # type: ignore[attr-defined]
        with self.assertRaises(FrozenInstanceError):
            owner.state.time = 7  # type: ignore[misc]
        profile: Any = owner.state.profile.to_dict()
        profile["params_resolved"]["candidate"]["chi_C"] = 999
        self.assertEqual(owned_bytes(owner), encoded)
        result: Any = owner.step_v4(request(0.125))
        payload = result.emitted_receipts[0].to_payload()
        payload["identity_payload"]["core"]["operation_id"] = "forged"
        self.assertEqual(
            cast(Any, owner.state.receipt_ledger[0])["identity_payload"]["core"][
                "operation_id"
            ],
            "ordinary",
        )
        for malformed in (request(0).to_payload(), None, object()):
            encoded = owned_bytes(owner)
            with self.assertRaises(TypeError):
                owner.step_v4(malformed)  # type: ignore[arg-type]
            self.assertEqual(owned_bytes(owner), encoded)
        forged = request(0)
        object.__setattr__(forged, "dt", float("nan"))
        with self.assertRaises(ValueError):
            owner.step_v4(forged)
        self.assertEqual(owned_bytes(owner), encoded)

    def test_fresh_owner_rejects_unauthenticated_ledger_and_foreign_domains(
        self,
    ) -> None:
        for inputs in (
            replace(dyadic_fixture(), receipt_ids=("grc-receipt-sha256:" + "0" * 64,)),
            replace(dyadic_fixture(), Q_target=9),
            current_fixture(realization="CI"),
            replace(
                dyadic_fixture(), reset=GRCV4AuthoritativeState((5, 1), None, None)
            ),
        ):
            with (
                self.subTest(inputs=inputs.operation_id),
                self.assertRaises(ValueError),
            ):
                CandidateCOSOperation(inputs)


def _p946_rehash(snapshot: dict[str, Any]) -> None:
    """Independent ASCII/dyadic identity oracle, for coherent hostile inputs."""
    snapshot["reset_digest"] = identity("grcv4-reset-sha256", snapshot["reset"])
    snapshot["scientific_state"]["reset_digest"] = snapshot["reset_digest"]
    snapshot["scientific_state_digest"] = scientific_id(snapshot["scientific_state"])
    snapshot["lifecycle"]["scientific_state_digest"] = snapshot[
        "scientific_state_digest"
    ]
    snapshot["lifecycle"]["receipt_ids"] = [
        r["receipt_id"] for r in snapshot["receipt_ledger"]
    ]
    snapshot["lifecycle_digest"] = lifecycle_id(
        snapshot["scientific_state"], snapshot["receipt_ledger"]
    )


def _p946_assignment(
    owner: CandidateCOSOperation, C: tuple[float, ...], **clock: Any
) -> Any:
    state = replace(
        owner.state, current=GRCV4AuthoritativeState(C, None, None), **clock
    )
    scientific = owner.snapshot()["scientific_state"]
    scientific.update(
        authoritative={"C": list(C), "W_A": None, "Z_4": None},
        step_index=state.step_index,
        time=state.time,
    )
    sid = scientific_id(scientific)
    return replace(
        state,
        scientific_state_digest=sid,
        lifecycle_digest=lifecycle_id(
            scientific, [r.to_dict() for r in state.receipt_ledger]
        ),
    )


class CandidateCOSLifecycleTests(unittest.TestCase):
    def assert_snapshot(self, owner: CandidateCOSOperation, expected: bytes) -> None:
        self.assertEqual(canonical_json_bytes(owner.snapshot()), expected)

    def test_dyadic_snapshot_embeds_exact_preimages_and_acyclic_identities(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        self.assertTrue(owner.step_v4(request(0.125)).committed)
        snap = owner.snapshot()
        self.assertEqual(
            snap["scientific_state"]["authoritative"],
            {"C": [2.5, 1.5], "W_A": None, "Z_4": None},
        )
        self.assertEqual(snap["reset"]["authoritative"]["C"], [3, 1])
        self.assertNotIn("time", snap["reset"])
        self.assertNotIn("receipt_ledger", snap["reset"])
        self.assertEqual(
            snap["scientific_state_digest"], scientific_id(snap["scientific_state"])
        )
        self.assertEqual(
            snap["reset_digest"], identity("grcv4-reset-sha256", snap["reset"])
        )
        self.assertEqual(
            snap["lifecycle_digest"],
            lifecycle_id(
                snap["scientific_state"],
                snap["receipt_ledger"],
            ),
        )
        record = snap["commit_records"][0]
        self.assertEqual(
            record["commit_id"], identity("grc-commit-sha256", record["payload"])
        )
        self.assertEqual(record["payload"]["target_time"], 0.125)
        for receipt in snap["receipt_ledger"]:
            self.assertEqual(
                receipt["receipt_id"],
                identity("grc-receipt-sha256", receipt["identity_payload"]),
            )
            self.assertEqual(receipt["commit_id"], record["commit_id"])
        restored = CandidateCOSOperation.from_state(
            snap, owner.reference.profile.params_resolved.to_payload()
        )
        self.assertEqual(restored.snapshot(), snap)

    def test_reset_after_ordinary_preserves_lineage_clock_profile_and_charge(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        before = owner.snapshot()
        owner.reset()
        after = owner.snapshot()
        self.assertEqual(owner.state.current.C, (3, 1))
        self.assertEqual((owner.state.step_index, owner.state.time), (1, 0.125))
        self.assertEqual(after["reset"], before["reset"])
        self.assertEqual(after["reference"], before["reference"])
        self.assertEqual(after["receipt_ledger"][:4], before["receipt_ledger"])
        emitted = after["receipt_ledger"][4:]
        self.assertEqual(len(emitted), 4)
        primary = emitted[0]["identity_payload"]
        self.assertEqual(primary["schema_version"], "grcv4-reset-receipt-v1")
        self.assertEqual(primary["reset_baseline_digest"], before["reset_digest"])
        self.assertEqual(
            primary["core"]["parent_receipt_ids"],
            [before["receipt_ledger"][0]["receipt_id"]],
        )
        for row in emitted:
            core = row["identity_payload"]["core"]
            self.assertEqual(
                core["source_state_digest"], before["scientific_state_digest"]
            )
            self.assertEqual(
                core["target_state_digest"], scientific_id(after["scientific_state"])
            )
            self.assertEqual(core["actual_charge_delta"], 0)
        self.assertEqual(CandidateCOSOperation.from_state(after).snapshot(), after)

    def test_rebase_reset_and_assignment_have_distinct_exact_effects(self) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        before = owner.snapshot()
        owner.rebase_reset_baseline()
        rebased = owner.snapshot()
        self.assertEqual(owner.state.current.C, (2.5, 1.5))
        self.assertEqual(owner.state.reset.authoritative.C, (2.5, 1.5))
        self.assertEqual(owner.state.Q_target, 4)
        self.assertEqual((owner.state.step_index, owner.state.time), (1, 0.125))
        p = rebased["receipt_ledger"][4]["identity_payload"]
        self.assertEqual(
            (p["old_reset_digest"], p["new_reset_digest"]),
            (before["reset_digest"], rebased["reset_digest"]),
        )
        owner.set_state(_p946_assignment(owner, (4, 0)))
        self.assertEqual(owner.state.reset.authoritative.C, (2.5, 1.5))
        self.assertEqual(owner.snapshot()["receipt_ledger"], rebased["receipt_ledger"])
        self.assertEqual(owner.snapshot()["commit_records"], rebased["commit_records"])
        # Current assignment may break adjacency to the latest commit's state.
        # It must still be restorable without inventing a commit for assignment.
        owner = CandidateCOSOperation.from_state(owner.snapshot())
        owner.reset()
        self.assertEqual(owner.state.current.C, (2.5, 1.5))
        self.assertEqual((owner.state.step_index, owner.state.time), (1, 0.125))

    def test_repeated_identity_operations_append_distinct_commits_without_writers(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        before = owner.snapshot()
        with patch(
            "pygrc.models.grc_v4_step.CandidateCOSPass",
            side_effect=AssertionError("administration must not execute OS"),
        ):
            for action in (
                owner.reset,
                owner.reset,
                owner.rebase_reset_baseline,
                owner.rebase_reset_baseline,
            ):
                action()
                self.assertEqual(
                    owner.state.scientific_state_digest,
                    before["scientific_state_digest"],
                )
            self.assertTrue(owner.step_v4(request(0)).committed)
        ledger = owner.snapshot()["receipt_ledger"]
        self.assertEqual(len(ledger), 20)
        self.assertEqual(len({r["receipt_id"] for r in ledger}), 20)
        self.assertEqual(len({r["commit_id"] for r in ledger}), 5)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_deep_independence_of_snapshot_duplicate_copy_and_retained_state(
        self,
    ) -> None:
        from copy import copy, deepcopy

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        old_state = owner.get_state()
        original = canonical_json_bytes(owner.snapshot())
        for duplicate in (owner.duplicate(), copy(owner), deepcopy(owner)):
            self.assertEqual(duplicate.snapshot(), owner.snapshot())
            self.assertIsNot(duplicate.reference, owner.reference)
            self.assertIsNot(duplicate.state, owner.state)
            self.assertIsNot(
                duplicate.state.receipt_ledger[0], old_state.receipt_ledger[0]
            )
            duplicate.rebase_reset_baseline()
            duplicate.set_state(_p946_assignment(duplicate, (4, 0)))
            self.assert_snapshot(owner, original)
        snapshot = owner.snapshot()
        for path in (
            ("reference", "graph", "live_node_ids"),
            ("scientific_state", "authoritative", "C"),
            ("reset", "authoritative", "C"),
            ("commit_records", 0, "payload", "emitted_receipt_ids"),
            ("receipt_ledger", 0, "identity_payload", "core", "parent_receipt_ids"),
        ):
            value: Any = snapshot
            for key in path:
                value = value[key]
            value.append("mutated")
        snapshot["reference"]["profile"]["params_resolved"]["candidate"]["W_C_tr"][
            "e"
        ] = 999
        self.assert_snapshot(owner, original)
        owner.reset()
        self.assertEqual(old_state.current.C, (2.5, 1.5))
        self.assertEqual(len(old_state.receipt_ledger), 4)
        with self.assertRaises((TypeError, AttributeError, FrozenInstanceError)):
            old_state.current.C[0] = 0  # type: ignore[index]
        immutable_receipt: Any = old_state.receipt_ledger[0]
        with self.assertRaises(TypeError):
            immutable_receipt["identity_payload"]["core"]["operation_id"] = "mutated"

    def test_restoration_detaches_caller_payload_and_asserts_parameters(self) -> None:
        source = CandidateCOSOperation(dyadic_fixture()).snapshot()
        target = CandidateCOSOperation.from_state(source)
        expected = canonical_json_bytes(target.snapshot())
        source["reference"]["K4_base"][0][0] = 99
        source["reset"]["authoritative"]["C"][0] = 99
        self.assert_snapshot(target, expected)
        params: Any = target.reference.profile.params_resolved.to_payload()
        params["candidate"]["eta_C"] = 99
        with self.assertRaises(V4IdentityError):
            CandidateCOSOperation.from_state(target.snapshot(), params)

    def test_closed_snapshot_requires_every_field_and_rejects_extra_authority(
        self,
    ) -> None:
        from copy import deepcopy

        original = CandidateCOSOperation(dyadic_fixture()).snapshot()
        for field in original:
            altered = deepcopy(original)
            del altered[field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)
        for field in (
            "T_C",
            "J",
            "h",
            "H1_form",
            "previous_root",
            "inspection_cache",
            "telemetry",
            "file",
            "rng",
        ):
            altered = deepcopy(original)
            altered[field] = {}
            with self.subTest(extra=field), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)
        for field in ("schema_version", "model_family", "implementation_layout_id"):
            for bad in (None, "GRC9V3", "unknown", 1, False):
                altered = deepcopy(original)
                altered[field] = bad
                with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                    CandidateCOSOperation.from_state(altered)

    def test_null_wrong_typed_and_stale_digest_fields_never_disable_verification(
        self,
    ) -> None:
        from copy import deepcopy

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        original = owner.snapshot()
        bad: Any
        for path in (
            ("scientific_state_digest",),
            ("reset_digest",),
            ("lifecycle_digest",),
            ("commit_records", 0, "commit_id"),
            ("receipt_ledger", 0, "receipt_id"),
            ("receipt_ledger", 0, "commit_id"),
        ):
            for bad in (None, False, 0, {}, [], "grcv4-state-sha256:" + "0" * 64):
                altered = deepcopy(original)
                value: Any = altered
                for key in path[:-1]:
                    value = value[key]
                value[path[-1]] = bad
                with (
                    self.subTest(path=path, bad=bad),
                    self.assertRaises((ValueError, TypeError)),
                ):
                    CandidateCOSOperation.from_state(altered)
        self.assertEqual(owner.snapshot(), original)

    def test_rehashed_cross_identity_mismatch_still_rejects(self) -> None:
        from copy import deepcopy

        original = CandidateCOSOperation(dyadic_fixture()).snapshot()
        fields = {
            "active_model_identity": "grcv4-profile-sha256:" + "0" * 64,
            "graph_digest": "grc-graph-sha256:" + "0" * 64,
            "orientation_identity": "foreign",
            "context_contract_id": "foreign",
            "Q_target": 5,
        }
        for group in ("scientific_state", "reset"):
            for field, bad in fields.items():
                altered = deepcopy(original)
                altered[group][field] = bad
                _p946_rehash(altered)
                with (
                    self.subTest(group=group, field=field),
                    self.assertRaises(ValueError),
                ):
                    CandidateCOSOperation.from_state(altered)
        altered = deepcopy(original)
        altered["scientific_state"]["context_value_digest"] = (
            "grcv4-context-sha256:" + "0" * 64
        )
        _p946_rehash(altered)
        with self.assertRaises(ValueError):
            CandidateCOSOperation.from_state(altered)

    def test_rehashed_negative_history_shape_and_charge_inputs_fail_readmission(
        self,
    ) -> None:
        from copy import deepcopy

        original = CandidateCOSOperation(dyadic_fixture()).snapshot()
        for group in ("scientific_state", "reset"):
            for field, bad in (
                ("C", [-1, 5]),
                ("C", [3]),
                ("C", [2, 1]),
                ("W_A", [1]),
                ("Z_4", [0]),
            ):
                altered = deepcopy(original)
                altered[group]["authoritative"][field] = bad
                _p946_rehash(altered)
                with (
                    self.subTest(group=group, field=field, value=bad),
                    self.assertRaises(ValueError),
                ):
                    CandidateCOSOperation.from_state(altered)

    def test_native_singular_current_and_reset_reject_even_with_coherent_hashes(
        self,
    ) -> None:
        from copy import deepcopy

        deformation = math.exp(0.25 * (0.5 * (math.tanh(3) + math.tanh(1))))
        retained = float(2 * Fraction(deformation) ** 2)
        beta = 1 + 2 * retained
        self.assertEqual(1 - Fraction(beta) + 2 * Fraction(retained), 0)
        state = GRCV4AuthoritativeState((4, 0), None, None)
        inputs = replace(
            os_fixture(
                candidate={
                    "kappa_M_C": 0.5,
                    "tau_C": 1,
                    "chi_C": 1,
                    "zeta_C": beta,
                    "Lambda_C": 10,
                },
                geometry={"kappa_H": 0.0001},
            ),
            current=state,
            reset=state,
        )
        owner = CandidateCOSOperation(inputs)
        original = owner.snapshot()
        for group in ("scientific_state", "reset"):
            altered = deepcopy(original)
            altered[group]["authoritative"]["C"] = [3, 1]
            _p946_rehash(altered)
            with (
                self.subTest(group=group),
                self.assertRaises(CandidateCStageError) as raised,
            ):
                CandidateCOSOperation.from_state(altered)
            self.assertEqual(raised.exception.disposition, "singular")
        with self.assertRaises(CandidateCStageError):
            owner.set_state(_p946_assignment(owner, (3, 1)))
        self.assertEqual(owner.snapshot(), original)

    def test_set_state_validates_full_target_and_forbids_lifecycle_replacement(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        original = canonical_json_bytes(owner.snapshot())
        for changes in (
            {"scientific_state_digest": "x"},
            {"lifecycle_digest": "x"},
            {"context_value_digest": "x"},
            {"current": GRCV4AuthoritativeState((3, 1), None, None)},
            {"receipt_ledger": ()},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                owner.set_state(replace(owner.state, **changes))
            self.assert_snapshot(owner, original)
        for clock in ({"step_index": 7}, {"time": 3.5}):
            with self.subTest(clock=clock), self.assertRaises(ValueError):
                owner.set_state(_p946_assignment(owner, (4, 0), **clock))
            self.assert_snapshot(owner, original)
        with self.assertRaises(ValueError):
            owner.set_state(_p946_assignment(owner, (4, 1)))
        foreign = CandidateCOSOperation(os_fixture())
        with self.assertRaises(ValueError):
            owner.set_state(foreign.state)
        twin = owner.duplicate()
        twin.rebase_reset_baseline()
        with self.assertRaises(ValueError):
            owner.set_state(twin.state)
        with self.assertRaises(TypeError):
            owner.set_state(owner.snapshot())  # type: ignore[arg-type]
        self.assert_snapshot(owner, original)

    def test_load_verifies_historical_commit_preimages_and_order(self) -> None:
        from copy import deepcopy

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        owner.rebase_reset_baseline()
        owner.step_v4(request(0.125))
        owner.reset()
        original = owner.snapshot()
        for field in ("commit_records", "receipt_ledger"):
            for operation in (
                lambda rows: rows.pop(0),
                lambda rows: rows.reverse(),
                lambda rows: rows.append(deepcopy(rows[0])),
                lambda rows: rows.clear(),
            ):
                altered = deepcopy(original)
                cast(Any, operation)(altered[field])
                _p946_rehash(altered)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    CandidateCOSOperation.from_state(altered)
        for field in (
            "target_time",
            "target_step_index",
            "operation_id",
            "source_state_digest",
            "target_state_digest",
        ):
            altered = deepcopy(original)
            record = altered["commit_records"][0]["payload"]
            record[field] = (
                42 if field in ("target_time", "target_step_index") else "bad"
            )
            with self.subTest(field=field), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)

        # Coherently rehash the changed historical commit. Receipt IDs and final
        # scientific/lifecycle identities remain valid. This must fail on the
        # local clock transition, not a stale hash or unrelated schema error.
        self.assertEqual(
            CandidateCOSOperation.from_state(original).snapshot(), original
        )
        for index, field, value in (
            (0, "target_time", 0.5),
            (0, "target_step_index", 3),
            (1, "target_time", 0.25),
            (1, "target_step_index", 2),
            (2, "target_step_index", 4),
            (2, "target_time", 0),
        ):
            altered = deepcopy(original)
            record = altered["commit_records"][index]
            record["payload"][field] = value
            record["commit_id"] = identity("grc-commit-sha256", record["payload"])
            for row in altered["receipt_ledger"][4 * index : 4 * (index + 1)]:
                row["commit_id"] = record["commit_id"]
            with (
                self.subTest(index=index, field=field),
                self.assertRaisesRegex(V4IdentityError, "clock transition"),
            ):
                CandidateCOSOperation.from_state(altered)

    def test_reference_content_and_every_nested_identity_are_load_bearing(self) -> None:
        from copy import deepcopy

        original = CandidateCOSOperation(dyadic_fixture()).snapshot()
        for path, value in (
            (("K4_base",), [[9]]),
            (("reference_hodge", "edge_weights"), {"e": 99}),
            (("graph", "live_node_ids"), ["a", "a"]),
            (("graph", "oriented_edges", 0, "tail_node_id"), "absent"),
            (("profile", "complete_profile_id"), "grcv4-profile-sha256:" + "0" * 64),
            (
                ("profile", "identity_payload", "params_hash"),
                "grcv4-params-sha256:" + "0" * 64,
            ),
            (("profile", "params_resolved", "candidate", "W_C_tr"), {"e": 5}),
            (
                ("profile", "params_resolved", "candidate", "W_C_tr_content_digest"),
                "grcv4-wctr-sha256:" + "0" * 64,
            ),
            (("context", "value"), {"x": 1}),
        ):
            altered = deepcopy(original)
            ref = altered["reference"]
            for key in path[:-1]:
                ref = ref[key]
            ref[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)

    def test_charge_tolerance_reset_receipt_reports_actual_negative_delta(self) -> None:
        owner = CandidateCOSOperation(charge_fixture(2))
        self.assertTrue(owner.step_v4(request(1)).committed)
        before = owner.snapshot()
        owner.reset()
        after = owner.snapshot()
        self.assertEqual(
            after["receipt_ledger"][4]["identity_payload"]["core"][
                "actual_charge_delta"
            ],
            -2,
        )
        self.assertEqual(after["receipt_ledger"][5]["identity_payload"]["residual"], 0)
        self.assertEqual(after["scientific_state"]["Q_target"], float(2**53 + 2))
        self.assertEqual(after["reset"], before["reset"])
        self.assertEqual(owner.duplicate().snapshot(), after)

    def test_loop_parallel_isolated_and_permuted_graphs_roundtrip_with_exact_maps(
        self,
    ) -> None:
        for graph, resource, weights in (
            (
                GRCV4Graph(("node",), (OrientedEdge("loop", "node", "node"),)),
                (4,),
                {"loop": 3},
            ),
            (
                GRCV4Graph(
                    (9, "a", "isolate"),
                    (
                        OrientedEdge("z", "a", 9),
                        OrientedEdge("a", 9, "a"),
                        OrientedEdge("l", 9, 9),
                    ),
                ),
                (3, 1, 0),
                {"z": 3, "a": 7, "l": 2},
            ),
        ):
            inputs = current_fixture(
                graph=graph,
                resource=resource,
                weights={k: float(v) for k, v in weights.items()},
                changes={"candidate": {"chi_C": 0}, "geometry": {"kappa_H": 0}},
            )
            owner = CandidateCOSOperation(replace(inputs, receipt_ids=()))
            self.assertTrue(owner.step_v4(request(0)).committed)
            copy = owner.duplicate()
            self.assertEqual(copy.reference.graph, graph)
            self.assertEqual(
                cast(Any, copy.reference.profile.params_resolved.to_payload())[
                    "candidate"
                ]["W_C_tr"],
                weights,
            )
            self.assertEqual(copy.snapshot(), owner.snapshot())
            copy.reset()
            self.assertEqual(copy.state.current.C, resource)

    def test_canonical_save_load_rejects_duplicate_keys_nonfinite_and_negative_zero(
        self,
    ) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from pygrc.models.grc_v4_codec import V4WireError

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        with TemporaryDirectory(prefix="p946 snapshot ") as directory:
            path = Path(directory) / "state with spaces.json"
            owner.save(str(path))
            content = path.read_bytes()
            self.assertEqual(content, canonical_json_bytes(owner.snapshot()))
            self.assertEqual(
                CandidateCOSOperation.load(str(path)).snapshot(), owner.snapshot()
            )
            for invalid in (
                content + b"\n",
                b'{"model_family":"GRCV4",' + content[1:],
                content.replace(b'"time":0.125', b'"time":-0'),
                content.replace(b'"time":0.125', b'"time":NaN'),
                content.replace(b'"time":0.125', b'"time":1e-999'),
                content.replace(b'"step_index":1', b'"step_index":9007199254740993'),
            ):
                self.assertNotEqual(invalid, content)
                path.write_bytes(invalid)
                with self.assertRaises((V4WireError, ValueError)):
                    CandidateCOSOperation.load(str(path))

    def test_save_load_fresh_process_and_large_canonical_clock_tokens(self) -> None:
        import os
        import subprocess
        import sys
        from pathlib import Path
        from tempfile import TemporaryDirectory

        # Clock extremes are legitimate lifecycle values, independent of dt.
        owner = CandidateCOSOperation(
            replace(dyadic_fixture(), step_index=2**53 - 1, time=1e308)
        )
        with TemporaryDirectory(prefix="p946 portable ") as directory:
            path = Path(directory) / "snapshot.json"
            owner.save(str(path))
            script = "from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation; import sys; x=CandidateCOSOperation.load(sys.argv[1]); x.save(sys.argv[2]); assert x.state.time==1e308 and x.state.step_index==2**53-1; x.reset(); assert x.state.time==1e308"
            output = path.with_name("restored.json")
            env = dict(os.environ, PYTHONHASHSEED="946")
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
            process = subprocess.run(
                [sys.executable, "-c", script, str(path), str(output)],
                cwd=directory,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(path.read_bytes(), output.read_bytes())

    def test_all_administrative_faults_keep_state_and_commit_preimages_atomic(
        self,
    ) -> None:
        from pygrc.models.grc_v4_step import ResourceBoundaryError

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        original = canonical_json_bytes(owner.snapshot())
        for method in (owner.reset, owner.rebase_reset_baseline):
            for name in (
                "_os_inputs",
                "ProvisionalCandidateCOSStep",
                "_ordinary_receipts",
                "make_commit_receipts",
                "_lifecycle_state",
                "_OwnedCOS",
            ):
                for error in (
                    ValueError("programmer"),
                    RuntimeError("programmer"),
                    V4IdentityError("internal identity"),
                    ResourceBoundaryError(
                        "target_readmission",
                        "domain_failure",
                        "native typed boundary control",
                    ),
                ):

                    def fail(*args: Any, **kwargs: Any) -> Any:
                        self.assert_snapshot(owner, original)
                        raise error

                    with (
                        self.subTest(
                            method=method.__name__,
                            name=name,
                            error=type(error).__name__,
                        ),
                        patch(
                            "pygrc.models.grc_v4_lifecycle." + name, side_effect=fail
                        ),
                        self.assertRaises(type(error)) as raised,
                    ):
                        method()
                    self.assertIs(raised.exception, error)
                    self.assert_snapshot(owner, original)

    def test_restoration_and_assignment_do_not_publish_before_final_readmission(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        original = canonical_json_bytes(owner.snapshot())
        assigned = _p946_assignment(owner, (4, 0))
        for name in (
            "_os_inputs",
            "ProvisionalCandidateCOSStep",
            "_lifecycle_state",
            "_OwnedCOS",
        ):
            with (
                self.subTest(name=name),
                patch(
                    "pygrc.models.grc_v4_lifecycle." + name,
                    side_effect=RuntimeError("late failure"),
                ),
            ):
                with self.assertRaises(RuntimeError):
                    owner.set_state(assigned)
                with self.assertRaises(RuntimeError):
                    CandidateCOSOperation.from_state(owner.snapshot())
            self.assert_snapshot(owner, original)

    def test_rehashed_receipt_semantic_contradictions_reject(self) -> None:
        from copy import deepcopy

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        original = owner.snapshot()

        def resign(snap: dict[str, Any]) -> None:
            record = snap["commit_records"][0]
            for r in snap["receipt_ledger"]:
                r["receipt_id"] = identity("grc-receipt-sha256", r["identity_payload"])
            record["payload"]["emitted_receipt_ids"] = [
                r["receipt_id"] for r in snap["receipt_ledger"]
            ]
            record["commit_id"] = identity("grc-commit-sha256", record["payload"])
            for r in snap["receipt_ledger"]:
                r["commit_id"] = record["commit_id"]
            _p946_rehash(snap)

        unchanged = deepcopy(original)
        resign(unchanged)
        self.assertEqual(unchanged, original)
        self.assertEqual(
            CandidateCOSOperation.from_state(unchanged).snapshot(), original
        )
        for field, bad in (
            (
                "resource_transform_digest",
                "grcv4-resource-transform-sha256:" + "0" * 64,
            ),
            ("history_bundle_digest", "grcv4-history-map-sha256:" + "0" * 64),
            ("target_authoritative_digest", "grcv4-authoritative-sha256:" + "0" * 64),
            ("parent_receipt_ids", [original["receipt_ledger"][0]["receipt_id"]]),
        ):
            altered = deepcopy(original)
            for r in altered["receipt_ledger"]:
                r["identity_payload"]["core"][field] = bad
            resign(altered)
            with self.subTest(field=field), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)
        for field, value in (
            ("admitted_charge", -4),
            ("residual", 1),
            ("target_charge", 5),
        ):
            altered = deepcopy(original)
            altered["receipt_ledger"][1]["identity_payload"][field] = value
            resign(altered)
            with self.subTest(charge=field), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)
        altered = deepcopy(original)
        altered["commit_records"][0]["payload"]["target_time"] = 0.25
        resign(altered)
        with self.assertRaises(V4IdentityError):
            CandidateCOSOperation.from_state(altered)

    def test_restored_positive_continuation_has_literal_dyadic_resource(self) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125, "first"))
        owner.rebase_reset_baseline()
        restored = owner.duplicate()
        left, right = (
            owner.step_v4(request(0.125, "second")),
            restored.step_v4(request(0.125, "second")),
        )
        self.assertTrue(left.committed)
        self.assertTrue(right.committed)
        self.assertEqual(owner.state.current.C, (2.25, 1.75))
        self.assertEqual(owner.state.reset.authoritative.C, (2.5, 1.5))
        self.assertEqual(owner.snapshot(), restored.snapshot())
        self.assertEqual(left.commit_id, right.commit_id)

    def test_snapshot_during_admission_observes_one_state_and_commit_generation(
        self,
    ) -> None:
        from threading import Event, Thread
        import pygrc.models.grc_v4_lifecycle as lifecycle

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        old = owner.snapshot()
        ready, release = Event(), Event()
        errors: list[BaseException] = []
        real = lifecycle._lifecycle_state

        def pause(*args: Any, **kwargs: Any) -> Any:
            target = real(*args, **kwargs)
            ready.set()
            if not release.wait(10):
                raise RuntimeError("publication test timed out")
            return target

        def worker() -> None:
            try:
                owner.reset()
            except BaseException as exc:
                errors.append(exc)

        with patch.object(lifecycle, "_lifecycle_state", side_effect=pause):
            thread = Thread(target=worker)
            thread.start()
            try:
                self.assertTrue(ready.wait(10))
                self.assertEqual(owner.snapshot(), old)
            finally:
                release.set()
                thread.join(10)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(len(owner.snapshot()["commit_records"]), 2)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())


class CandidateCOSReplayTests(unittest.TestCase):
    """Actual-operation pressure; fault controls are separately named."""

    def seeded(self) -> CandidateCOSOperation:
        owner = CandidateCOSOperation(dyadic_fixture())
        self.assertTrue(owner.step_v4(request(0.125, "seed1")).committed)
        owner.rebase_reset_baseline()
        self.assertTrue(owner.step_v4(request(0.125, "seed2")).committed)
        self.assertEqual(owner.state.current.C, (2.25, 1.75))
        self.assertEqual(owner.state.reset.authoritative.C, (2.5, 1.5))
        return owner

    def test_live_clock_and_resource_against_rational_oracle(self) -> None:
        for time in (0, 0.75, 1e308):
            for dt in (0, 5e-324, 0.125, 0.25):
                with self.subTest(time=time, dt=dt):
                    owner = CandidateCOSOperation(replace(dyadic_fixture(), time=time))
                    result = owner.step_v4(request(dt))
                    self.assertTrue(result.committed)
                    self.assertEqual(owner.state.step_index, int(dt > 0))
                    self.assertEqual(
                        owner.state.time, float(Fraction(time) + Fraction(dt))
                    )
                    self.assertEqual(
                        owner.state.current.C,
                        (
                            float(Fraction(3) - 4 * Fraction(dt)),
                            float(Fraction(1) + 4 * Fraction(dt)),
                        ),
                    )
                    self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_four_invalid_live_transition_controls_cannot_publish(self) -> None:
        import pygrc.models.grc_v4_lifecycle as module

        real = ProvisionalCandidateCOSStep
        for name, dt, changes, message in (
            ("wrong_elapsed_time", 0.125, {"time": 99}, "clock transition"),
            ("unchanged_index", 0.125, {"step_index": 2}, "clock transition"),
            ("backward_clock", 0.125, {"step_index": 1, "time": 0}, "clock transition"),
            (
                "zero_dt_changed_state",
                0,
                {"current": GRCV4AuthoritativeState((2, 2), None, None)},
                "zero-duration",
            ),
        ):
            owner = self.seeded()
            original = owner.snapshot()

            def corrupt(inputs: GeometryStageInputs) -> Any:
                step = real(inputs)
                object.__setattr__(
                    step, "next_inputs", replace(step.next_inputs, **changes)
                )
                return step

            with (
                self.subTest(case=name),
                patch.object(
                    module, "ProvisionalCandidateCOSStep", side_effect=corrupt
                ),
            ):
                with self.assertRaisesRegex(V4IdentityError, message):
                    owner.step_v4(request(dt, name))
            self.assertEqual(owner.snapshot(), original)
            self.assertTrue(owner.step_v4(request(0.125, name)).committed)

    def test_complete_authority_replacement_controls_cannot_publish(self) -> None:
        import pygrc.models.grc_v4_lifecycle as module

        real = ProvisionalCandidateCOSStep
        for field in ("reset", "Q_target", "receipt_ids", "operation_id"):
            owner = self.seeded()
            original = owner.snapshot()

            def corrupt(inputs: GeometryStageInputs) -> Any:
                step = real(inputs)
                value: Any = {
                    "reset": inputs.current,
                    "Q_target": 5,
                    "receipt_ids": (),
                    "operation_id": "foreign",
                }[field]
                object.__setattr__(
                    step, "next_inputs", replace(step.next_inputs, **{field: value})
                )
                return step

            with (
                self.subTest(field=field),
                patch.object(
                    module, "ProvisionalCandidateCOSStep", side_effect=corrupt
                ),
            ):
                with self.assertRaisesRegex(V4IdentityError, "lifecycle authority"):
                    owner.step_v4(request(0.125))
            self.assertEqual(owner.snapshot(), original)

    def test_failed_operations_preserve_seeded_tuple_and_recovery_replay(self) -> None:
        for incoming, code, solver in (
            (request(-0.125, "negative"), "invalid_duration", None),
            (request(4, "negative_resource"), "domain_failure", "valid_root"),
            (
                replace(
                    request(0, "impulse"), external_source=FrozenJSONMap({"C": [1, 0]})
                ),
                "domain_failure",
                None,
            ),
            (
                replace(
                    request(0.125, "context"), context_value=FrozenJSONMap({"x": 1})
                ),
                "domain_failure",
                None,
            ),
            (
                replace(request(0.125, "boundary"), boundary_input=FrozenJSONMap({})),
                "domain_failure",
                None,
            ),
        ):
            owner = self.seeded()
            old, snapshot = owner.state, owner.snapshot()
            independent = owner.duplicate()
            result = owner.step_v4(incoming)
            with self.subTest(code=code, incoming=incoming.operation_id):
                self.assertFalse(result.committed)
                self.assertIsNotNone(result.failure)
                assert result.failure is not None
                self.assertEqual(result.failure.code, code)
                self.assertEqual(result.solver_disposition, solver)
                self.assertEqual(result.events, ())
                self.assertEqual(len(result.emitted_receipts), 1)
                self.assertEqual(
                    result.failure.prestate_digest, result.failure.poststate_digest
                )
                self.assertEqual(
                    result.failure.pre_lifecycle_digest,
                    result.failure.post_lifecycle_digest,
                )
                self.assertIs(owner.state, old)
                self.assertEqual(owner.snapshot(), snapshot)
                self.assertEqual(
                    owner.step_v4(request(0.125, "recover")),
                    independent.step_v4(request(0.125, "recover")),
                )
                self.assertEqual(owner.snapshot(), independent.snapshot())

    def test_native_solver_failure_preserves_existing_ledger_and_reset(self) -> None:
        owner = CandidateCOSOperation(
            os_fixture(
                candidate={"zeta_C": 3, "chi_C": 1}, geometry={"kappa_H": 1 / 24}
            )
        )
        owner.step_v4(request(0, "seed"))
        owner.rebase_reset_baseline()
        original = owner.snapshot()
        result = owner.step_v4(request(1, "singular"))
        self.assertFalse(result.committed)
        self.assertEqual(result.solver_disposition, "singular")
        self.assertEqual(owner.snapshot(), original)
        self.assertEqual(owner.duplicate().snapshot(), original)

    def test_failure_receipts_never_become_persistent_authority(self) -> None:
        from copy import deepcopy

        owner = self.seeded()
        original = owner.snapshot()
        result = owner.step_v4(request(-1))
        bad = deepcopy(original)
        bad["receipt_ledger"].append(result.emitted_receipts[0].to_payload())
        _p946_rehash(bad)
        with self.assertRaises(ValueError):
            CandidateCOSOperation.from_state(bad)
        self.assertEqual(owner.snapshot(), original)

    def test_interleaved_ledger_deltas_and_parent_scope(self) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        last_step = None
        for action in ("step", "reset", "rebase", "step", "zero", "reset", "step"):
            before = owner.snapshot()
            if action in ("step", "zero"):
                result = owner.step_v4(
                    request(0 if action == "zero" else 0.125, "same-id")
                )
                self.assertTrue(result.committed)
                self.assertEqual(result.events, ())
                delta = [
                    cast(dict[str, Any], r.to_payload())
                    for r in result.emitted_receipts
                ]
                parent = last_step
                last_step = delta[0]["receipt_id"]
            else:
                parent = (
                    before["receipt_ledger"][-4]["receipt_id"]
                    if before["receipt_ledger"]
                    else None
                )
                getattr(
                    owner, "reset" if action == "reset" else "rebase_reset_baseline"
                )()
                delta = owner.snapshot()["receipt_ledger"][
                    len(before["receipt_ledger"]) :
                ]
            after = owner.snapshot()
            self.assertEqual(len(delta), 4)
            self.assertEqual(after["receipt_ledger"], before["receipt_ledger"] + delta)
            for row in delta:
                self.assertEqual(
                    row["identity_payload"]["core"]["parent_receipt_ids"],
                    [] if parent is None else [parent],
                )
            self.assertEqual(owner.duplicate().snapshot(), after)
        ids = [r["receipt_id"] for r in owner.snapshot()["receipt_ledger"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_missing_foreign_and_reordered_parents_reject_after_coherent_rehash(
        self,
    ) -> None:
        from copy import deepcopy

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125, "first"))
        owner.reset()
        owner.step_v4(request(0.125, "last"))
        original = owner.snapshot()
        parents = [original["receipt_ledger"][i]["receipt_id"] for i in (0, 4)]
        for bad_parents in (
            [],
            [parents[1]],
            parents,
            list(reversed(parents)),
            ["grc-receipt-sha256:" + "f" * 64],
        ):
            altered = deepcopy(original)
            for row in altered["receipt_ledger"][-4:]:
                row["identity_payload"]["core"]["parent_receipt_ids"] = bad_parents
                row["receipt_id"] = identity(
                    "grc-receipt-sha256", row["identity_payload"]
                )
            record = altered["commit_records"][-1]
            record["payload"]["emitted_receipt_ids"] = [
                r["receipt_id"] for r in altered["receipt_ledger"][-4:]
            ]
            record["commit_id"] = identity("grc-commit-sha256", record["payload"])
            for row in altered["receipt_ledger"][-4:]:
                row["commit_id"] = record["commit_id"]
            _p946_rehash(altered)
            with (
                self.subTest(parents=bad_parents),
                self.assertRaisesRegex(V4IdentityError, "parent convention"),
            ):
                CandidateCOSOperation.from_state(altered)

    def test_deterministic_replay_every_checkpoint_with_rational_expected_states(
        self,
    ) -> None:
        import tempfile
        from pathlib import Path

        owner = CandidateCOSOperation(dyadic_fixture())
        actions = [
            ("step", 0.125),
            ("rebase", 0),
            ("step", 0.125),
            ("failed", -1),
            ("reset", 0),
            ("zero", 0),
            ("step", 0.125),
        ]
        expected = [
            (2.5, 1.5),
            (2.5, 1.5),
            (2.25, 1.75),
            (2.25, 1.75),
            (2.5, 1.5),
            (2.5, 1.5),
            (2.25, 1.75),
        ]
        with tempfile.TemporaryDirectory(prefix="p947 replay ") as scratch:
            for i, (action, dt) in enumerate(actions):
                path = Path(scratch) / "state with spaces.json"
                owner.save(str(path))
                replay = CandidateCOSOperation.load(str(path))
                for receiver in (owner, replay):
                    if action in ("reset", "rebase"):
                        getattr(
                            receiver,
                            "reset" if action == "reset" else "rebase_reset_baseline",
                        )()
                    else:
                        result = receiver.step_v4(request(dt, str(i)))
                        self.assertEqual(result.committed, action != "failed")
                self.assertEqual(owner.state.current.C, expected[i])
                self.assertEqual(owner.snapshot(), replay.snapshot())

    def test_replay_does_not_consume_saved_observables_or_old_results(self) -> None:
        owner = self.seeded()
        snapshot = owner.snapshot()
        result = owner.step_v4(request(0.125, "next"))
        altered = result.to_payload()
        altered["observables"].clear()
        altered["observables"]["cache"] = [999]
        altered["emitted_receipts"].clear()
        replay = CandidateCOSOperation.from_state(snapshot)
        repeated = replay.step_v4(request(0.125, "next"))
        self.assertEqual(repeated, result)
        self.assertEqual(owner.snapshot(), replay.snapshot())

    def test_seeded_programmer_failures_preserve_reference_and_commit_archive(
        self,
    ) -> None:
        import pygrc.models.grc_v4_lifecycle as module

        for name in (
            "_ordinary_receipts",
            "make_commit_receipts",
            "_lifecycle_state",
            "bind_step_result",
            "_OwnedCOS",
        ):
            owner = self.seeded()
            original, reference = owner.snapshot(), owner.reference
            error = RuntimeError("explicit control at " + name)
            with (
                self.subTest(stage=name),
                patch.object(module, name, side_effect=error),
            ):
                with self.assertRaises(RuntimeError) as caught:
                    owner.step_v4(request(0.125))
            self.assertIs(caught.exception, error)
            self.assertEqual(owner.snapshot(), original)
            self.assertIs(owner.reference, reference)
            self.assertEqual(owner.duplicate().snapshot(), original)


_P945_METHODS = (
    "test_capture_rejects_same_file_method_slot_substitution",
    "test_native_reference_only_poststate_singularity_rejects_after_valid_consumed_final",
    "test_empty_edge_declarations_reject_and_loop_only_operation_commits",
    "test_dense_nonidentity_multigraph_operation_and_signed_covariance",
    "test_repeated_cluster_projector_and_near_conditioning_boundary_operations",
    "test_connected_repeated_cluster_uses_general_certificate_and_covaries",
    "test_dense_conditioning_certificate_operation_inside_and_outside_limit",
    "test_native_corrector_conditioning_failure",
    "test_positive_nonzero_split_matches_rational_oracle_and_one_publication",
    "test_exact_dyadic_receipts_commit_and_whole_state_identity",
    "test_two_beats_use_actual_request_poststate_ledger_and_reference",
    "test_zero_duration_identity_no_writer_but_authenticated_receipt_delta",
    "test_negative_duration_and_closed_external_inputs_fail_before_solver",
    "test_duration_and_clock_extremes_keep_classification_and_atomicity",
    "test_native_solver_geometry_selector_and_split_failures_are_atomic",
    "test_native_postsolve_resource_domain_overflow_and_charge_failures",
    "test_native_charge_tolerance_boundary_commits_without_resource_repair",
    "test_fault_controls_final_consumed_and_reference_readmission_are_atomic",
    "test_fault_controls_charge_types_override_hostile_text",
    "test_fault_controls_every_solver_disposition_has_typed_provenance",
    "test_fault_controls_receipt_construction_binding_and_exceptions_before_publish",
    "test_no_cache_input_and_immutable_detached_observations",
    "test_fresh_owner_rejects_unauthenticated_ledger_and_foreign_domains",
)


def capture_p945(output: str) -> int:
    """One source-bound focused run; replay source comes from Git history."""
    from datetime import datetime, timezone
    import hashlib
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import subprocess
    from tests.models.test_grc_v4_candidate_c import _p941_execute

    root = Path(__file__).resolve().parents[2]
    generated = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    )
    destination = (root / output).resolve()
    if (
        not destination.is_relative_to(generated.resolve())
        or destination == generated.resolve()
        or destination.exists()
    ):
        raise ValueError(
            "capture requires a fresh repository-local generated destination"
        )
    base = "175242621cd5a37625835a9ce95044f0b8a3837d"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=root, check=True
    )
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    ]
    overrides = {
        "src/pygrc/models/grc_v4_geometry.py",
        "src/pygrc/models/grc_v4_transport.py",
        "src/pygrc/models/grc_v4_realizations.py",
        "src/pygrc/models/grc_v4_candidate_c.py",
        "src/pygrc/models/grc_v4_step.py",
        "src/pygrc/models/grc_v4_lifecycle.py",
        "tests/models/test_grc_v4_lifecycle.py",
        "tests/models/test_grc_v4_candidate_c.py",
        "tests/models/test_grc_v4_realizations.py",
    }

    def snapshot() -> dict[str, str]:
        names = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                *scopes,
            ],
            cwd=root,
            text=True,
        ).splitlines()
        return {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest()
            for n in sorted(set(names))
        }

    before = snapshot()
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    base_names = set(
        subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", base, "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | (set(before) - base_names)) - overrides or base_names - set(before):
        raise ValueError("source differs outside the P9-4.5 reconstruction envelope")
    prior_path = "implementation/phase-9-grcv4/evidence/P9-4.4/audit-followup/run.json"
    prior = json.loads(
        subprocess.check_output(["git", "show", base + ":" + prior_path], cwd=root)
    )
    # Base-commit tests are independently pinned by Git, not current discovery.
    import ast

    base_tests = ast.parse(
        subprocess.check_output(
            ["git", "show", base + ":tests/models/test_grc_v4_step.py"], cwd=root
        )
    )
    shared = {
        "tests.models.test_grc_v4_step." + c.name + "." + n.name
        for c in base_tests.body
        if isinstance(c, ast.ClassDef)
        and c.name
        in {"StepAdmissionTests", "ResultCompositionTests", "AuditBoundaryTests"}
        for n in c.body
        if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
    }
    required = (
        set(prior["required_ids"])
        | shared
        | {
            "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests." + n
            for n in _P945_METHODS
        }
    )
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    started = datetime.now(timezone.utc).isoformat()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.5",
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Overlay only the listed hash-matching source files from the commit containing this run onto base_commit; verify the scoped manifest. Before commit, use the reviewed working tree.",
        },
        "required_ids": sorted(required),
        "started_utc": started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            key: os.environ.get(key)
            for key in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_lifecycle",
            "--capture-p945",
            str(destination.relative_to(root)),
        ],
        "claim_ceiling": "Bounded actual C_OS ordinary commits, receipt binding and atomic negative vectors. No complete facade/profile conformance, snapshot/load/reset/migration or cross-platform bitwise claim.",
        "numerical_policy": "Inherited C stage/star/geometry binary64 policy; exact reference-relative split tolerance via symmetric inertia; fixed-rank affine selector path certification with a 256-bisection fail-closed ceiling. Positive subnormal durations are never classified as zero.",
    }
    record.update(
        _p941_execute(
            root,
            before,
            required,
            suite,
            snapshot,
            extra_modules=frozenset(
                {
                    "pygrc.models.grc_v4_geometry",
                    "pygrc.models.grc_v4_transport",
                    "pygrc.models.grc_v4_step",
                    "pygrc.models.grc_v4_realizations",
                    "pygrc.models.grc_v4_lifecycle",
                    "tests.models.test_grc_v4_lifecycle",
                    "tests.models.test_grc_v4_realizations",
                }
            ),
        )
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["live_source_check_limits"] = (
        "Same before/after live-code and disk attribution checks as accepted P9-4.3 capture; not hostile-interpreter attestation. Existing dependency environment, no fresh dependency installation."
    )
    if record.get("loaded_sources_before") == record.get("loaded_sources_after"):
        record["loaded_sources"] = record.pop("loaded_sources_before")
        record.pop("loaded_sources_after")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print("P9-4.5", record["status"], json.dumps(record.get("results", {})), flush=True)
    if record["status"] != "passed":
        print(record.get("capture_error", record.get("failure_output", "")), flush=True)
    return 0 if record["status"] == "passed" else 1


class CandidateCOSAuditCorrectionTests(unittest.TestCase):
    def test_schema_valid_administrative_corruption_never_publishes(self) -> None:
        import copy
        import pygrc.models.grc_v4_lifecycle as module

        from pygrc.models.grc_v4_step import make_commit_receipts as real

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))  # distinct current/reset; nonempty ledger
        for kind in ("reset", "rebase"):
            for defect in (
                "baseline",
                "authority",
                "parent",
                "history",
                "charge",
                "clock",
                "kind",
            ):
                before = canonical_json_bytes(owner.snapshot())
                old_state, old_reference = owner.state, owner.reference

                def corrupted(payloads: Any, **kwargs: Any) -> Any:
                    payloads = copy.deepcopy(payloads)
                    core = payloads[0]["core"]
                    if defect == "baseline":
                        if kind == "reset":
                            payloads[0]["reset_baseline_digest"] = (
                                "grcv4-reset-sha256:" + "0" * 64
                            )
                        else:
                            p = payloads[0]
                            p["old_reset_digest"], p["new_reset_digest"] = (
                                p["new_reset_digest"],
                                p["old_reset_digest"],
                            )
                    elif defect == "authority":
                        core["source_authoritative_digest"] = core[
                            "target_authoritative_digest"
                        ] = "grcv4-authoritative-sha256:" + "0" * 64
                    elif defect == "parent":
                        core["parent_receipt_ids"] = []
                    elif defect == "history":
                        payloads[2], payloads[3] = payloads[3], payloads[2]
                    elif defect == "charge":
                        core["actual_charge_delta"] = 0.5
                    elif defect == "clock":
                        kwargs["target_time"] += 1
                    else:
                        payloads[0] = {
                            "schema_version": "grcv4-step-commit-receipt-v1",
                            "core": core,
                        }
                    # Factory succeeds: every identity binds the wrong bytes.
                    result = real(payloads, **kwargs)
                    self.assertEqual(len(result[1]), 4)
                    return result

                with (
                    self.subTest(kind=kind, defect=defect),
                    patch.object(module, "make_commit_receipts", side_effect=corrupted),
                    self.assertRaises(V4IdentityError),
                ):
                    owner.reset() if kind == "reset" else owner.rebase_reset_baseline()
                self.assertIs(owner.state, old_state)
                self.assertIs(owner.reference, old_reference)
                self.assertEqual(canonical_json_bytes(owner.snapshot()), before)
        owner.rebase_reset_baseline()
        owner.reset()
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_administrative_returned_target_cannot_exploit_empty_ledger(self) -> None:
        import pygrc.models.grc_v4_lifecycle as module

        from pygrc.models.grc_v4_realizations import _os_inputs as real

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.set_state(_p946_assignment(owner, (1, 3)))
        self.assertEqual(owner.state.receipt_ledger, ())
        for method in (owner.reset, owner.rebase_reset_baseline):
            for defect in ("clock", "current"):
                before = owner.snapshot()

                def corrupt(inputs: Any) -> Any:
                    valid = real(inputs)
                    return (
                        replace(valid, time=0.125)
                        if defect == "clock"
                        else replace(
                            valid, current=GRCV4AuthoritativeState((2, 2), None, None)
                        )
                    )

                with (
                    self.subTest(method=method.__name__, defect=defect),
                    patch.object(module, "_os_inputs", side_effect=corrupt),
                    self.assertRaisesRegex(V4IdentityError, "administrative target"),
                ):
                    method()
                self.assertEqual(owner.snapshot(), before)
        owner.reset()
        self.assertEqual(owner.state.current.C, (3, 1))
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_exact_audit_zero_then_minimum_positive_clock_cases(self) -> None:
        for start in (0, 0.125, 1e308):
            with self.subTest(start=start):
                owner = CandidateCOSOperation(replace(dyadic_fixture(), time=start))
                zero = owner.step_v4(request(0, "zero"))
                self.assertTrue(zero.committed)
                self.assertEqual((owner.state.step_index, owner.state.time), (0, start))
                positive = owner.step_v4(request(5e-324, "minimum-positive"))
                self.assertTrue(positive.committed)
                self.assertEqual(
                    (owner.state.step_index, owner.state.time),
                    (1, float(Fraction(start) + Fraction(5e-324))),
                )
                self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_unreceipted_assignment_preserves_snapshot_continuation_replay(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0.125))
        historic = owner.snapshot()["commit_records"][-1]["payload"][
            "target_state_digest"
        ]
        owner.set_state(_p946_assignment(owner, (1, 3)))
        self.assertNotEqual(historic, owner.state.scientific_state_digest)
        restored = owner.duplicate()
        for actor in (owner, restored):
            self.assertTrue(actor.step_v4(request(0.125, "after-assignment")).committed)
            self.assertEqual(actor.state.current.C, (1.5, 2.5))
        self.assertEqual(owner.snapshot(), restored.snapshot())


def crossing_history() -> dict[str, Any]:
    return {
        "schema_version": "grcv4-history-bundle-policy-v1",
        **{
            subject: {
                "schema_version": "grcv4-history-channel-policy-v1",
                "subject": subject,
                "policy_id": policy,
                "disposition": disposition,
                "source_history_digest": None,
                "target_initializer_id": None,
                "information_loss": "none",
            }
            for subject, policy, disposition in (
                ("candidate", "candidate_c_rederive_no_history_v1", "rederived"),
                ("carrier", "no_persistent_carrier_v1", "not_applicable"),
            )
        },
    }


def migration_request(owner: CandidateCOSOperation, target: Any, **changes: Any) -> Any:
    from pygrc.models.grc_v4 import GRCV4MigrationRequest

    return GRCV4MigrationRequest.from_payload(
        {
            "schema_version": "grcv4-migration-request-v1",
            "operation_id": "migrate",
            "source_state_digest": owner.state.scientific_state_digest,
            "target_profile_id": target.profile.complete_profile_id,
            "migration_policy": {
                "schema_version": "grcv4-migration-policy-v1",
                "policy_id": "typed_bidirectional_profile_migration_v1",
                "resource_policy_id": "identity_resource_transport_v1",
                "target_readmission_policy_id": "full_target_fail_closed_v1",
            },
            "history_policy": crossing_history(),
            "target_context_value": {},
            **changes,
        }
    )


def event_request(
    owner: CandidateCOSOperation,
    target: Any,
    coefficients: list[float],
    increment: list[float],
    **changes: Any,
) -> Any:
    from pygrc.models.grc_v4 import GRCV4MappedTopologyEventRequest

    return GRCV4MappedTopologyEventRequest.from_payload(
        {
            "schema_version": "grcv4-mapped-topology-event-request-v1",
            "operation_id": "event",
            "source_state_digest": owner.state.scientific_state_digest,
            "source_graph_digest": owner.state.graph_digest,
            "target_graph": target.graph.to_payload(),
            "target_profile_id": target.profile.complete_profile_id,
            "resource_transform": {
                "schema_version": "grcv4-resource-event-transform-v1",
                "policy_id": "caller_affine_resource_transport_v1",
                "source_vertex_ids": list(owner.reference.graph.live_node_ids),
                "target_vertex_ids": list(target.graph.live_node_ids),
                "row_major_coefficients": coefficients,
                "target_increment": increment,
            },
            "history_policy": crossing_history(),
            "metadata": {},
            **changes,
        }
    )


def event_target() -> Any:
    from tests.models.test_grc_v4_geometry import stage_reference_fixture

    return stage_reference_fixture(
        graph=GRCV4Graph(
            ("u", "v", "w"), (OrientedEdge("e", "u", "v"), OrientedEdge("f", "v", "w"))
        ),
        weights={"e": 2, "f": 2},
        gain=0,
        changes={
            "candidate": {"tau_C": 0, "chi_C": 0, "zeta_C": 0, "kappa_M_C": 0},
            "charge": {"absolute_tolerance": 0, "relative_tolerance": 0},
        },
    )


class CandidateCOSCrossingTests(unittest.TestCase):
    def test_parameter_migration_preserves_both_states_and_reset_after_migration(
        self,
    ) -> None:
        target = os_fixture(
            candidate={"chi_C": 0, "zeta_C": 0}, geometry={"kappa_H": 0}
        ).geometry.reference
        owner = CandidateCOSOperation(dyadic_fixture(), targets=(target,))
        owner.set_state(_p946_assignment(owner, (1, 3)))
        old = owner.state
        result = owner.migrate_profile(migration_request(owner, target))
        self.assertTrue(result.committed, result)
        self.assertEqual(owner.reference, target)
        self.assertEqual(owner.state.current.C, (1, 3))
        self.assertEqual(owner.state.reset.authoritative.C, (3, 1))
        self.assertNotEqual(owner.state.reset.reset_digest, old.reset.reset_digest)
        self.assertEqual(
            (owner.state.time, owner.state.step_index, owner.state.Q_target), (0, 0, 4)
        )
        self.assertEqual(len(result.emitted_receipts), 4)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        owner.reset()
        self.assertEqual(owner.state.current.C, (3, 1))
        self.assertEqual(owner.reference, target)

    def test_affine_increment_maps_distinct_live_and_reset_then_replays(self) -> None:
        target = event_target()
        owner = CandidateCOSOperation(dyadic_fixture(), targets=(target,))
        owner.set_state(_p946_assignment(owner, (1, 3)))
        result = owner.apply_topology_event(
            event_request(owner, target, [1, 0, 0, 1, 0, 0], [0, 0, 0.5])
        )
        self.assertTrue(result.committed, result)
        self.assertEqual(owner.state.current.C, (1, 3, 0.5))
        self.assertEqual(owner.state.reset.authoritative.C, (3, 1, 0.5))
        self.assertEqual(owner.state.Q_target, 4.5)
        core = cast(Any, result.emitted_receipts[0].to_payload())["identity_payload"][
            "core"
        ]
        self.assertEqual(core["actual_charge_delta"], 0.5)
        clone = owner.duplicate()
        for actor in (owner, clone):
            actor.reset()
            self.assertEqual(actor.state.current.C, (3, 1, 0.5))
            self.assertTrue(actor.step_v4(request(1 / 1024)).committed)
            # eta=1/2, Phi=L C: L Phi=(14,-18,4), so -B J0=(7,-9,2).
            self.assertEqual(
                actor.state.current.C, (3 + 7 / 1024, 1 - 9 / 1024, 0.5 + 2 / 1024)
            )
        self.assertEqual(owner.snapshot(), clone.snapshot())

    def assert_rejected(
        self,
        owner: CandidateCOSOperation,
        declaration: Any,
        code: str,
        stage: str = "admission",
    ) -> None:
        from pygrc.models.grc_v4 import GRCV4MigrationRequest

        before, old_ref = owner.snapshot(), owner.reference
        result = (
            owner.migrate_profile(declaration)
            if type(declaration) is GRCV4MigrationRequest
            else owner.apply_topology_event(declaration)
        )
        self.assertFalse(result.committed)
        self.assertIsNotNone(result.failure)
        failure = cast(Any, result.failure)
        self.assertEqual((failure.code, failure.stage), (code, stage))
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertIsNone(failure.solver_disposition)
        self.assertEqual(failure.prestate_digest, failure.poststate_digest)
        self.assertEqual(owner.snapshot(), before)
        self.assertIs(owner.reference, old_ref)

    def test_unregistered_target_families_and_stale_identity_are_explicit(self) -> None:
        from tests.models.test_grc_v4_profile import family_fixture, reidentify
        from pygrc.models.grc_v4_profile import resolve_profile

        owner = CandidateCOSOperation(dyadic_fixture())
        for candidate in ("C", "A"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                params, identifier = family_fixture(candidate, realization)
                reidentify(params, identifier)
                profile = resolve_profile(params, identifier)
                self.assert_rejected(
                    owner,
                    migration_request(
                        owner,
                        owner.reference,
                        target_profile_id=profile.complete_profile_id,
                    ),
                    "unsupported_profile",
                )
        self.assert_rejected(
            owner,
            migration_request(
                owner,
                owner.reference,
                source_state_digest="grcv4-state-sha256:" + "0" * 64,
            ),
            "invalid_identity",
        )
        self.assert_rejected(
            owner,
            migration_request(
                owner, owner.reference, target_context_value={"foreign": 1}
            ),
            "invalid_migration",
        )
        self.assert_rejected(
            owner,
            event_request(
                owner,
                owner.reference,
                [1, 0, 0, 1],
                [0, 0],
                source_graph_digest="grc-graph-sha256:" + "0" * 64,
            ),
            "invalid_identity",
        )

    def test_separate_history_channels_reject_invented_retention_loss_and_initializers(
        self,
    ) -> None:
        import copy

        owner = CandidateCOSOperation(dyadic_fixture())
        for subject in ("candidate", "carrier"):
            for field, value in (
                ("disposition", "exact_transport"),
                ("disposition", "target_initializer"),
                ("information_loss", subject + "_history_loss"),
                ("policy_id", "unregistered_policy"),
                ("source_history_digest", "grcv4-history-content-sha256:" + "0" * 64),
                ("target_initializer_id", "missing_initializer"),
            ):
                bundle = copy.deepcopy(crossing_history())
                bundle[subject][field] = value
                if subject == "carrier" and field in (
                    "source_history_digest",
                    "target_initializer_id",
                    "information_loss",
                ):
                    bundle[subject]["disposition"] = "whole_carrier_map"
                with self.subTest(subject=subject, field=field, value=value):
                    self.assert_rejected(
                        owner,
                        migration_request(
                            owner, owner.reference, history_policy=bundle
                        ),
                        "invalid_migration",
                    )
                    self.assert_rejected(
                        owner,
                        event_request(
                            owner,
                            owner.reference,
                            [1, 0, 0, 1],
                            [0, 0],
                            history_policy=bundle,
                        ),
                        "invalid_topology_event",
                    )

    def test_map_shape_conservation_order_and_numeric_wire_domains(self) -> None:
        import copy
        from pygrc.models.grc_v4 import (
            GRCV4MappedTopologyEventRequest,
            decode_mapped_topology_event_request,
        )

        owner = CandidateCOSOperation(dyadic_fixture())
        good = event_request(owner, owner.reference, [1, 0, 0, 1], [0, 0])
        for field, value in (
            ("source_vertex_ids", ["v", "u"]),
            ("target_vertex_ids", ["v", "u"]),
            ("row_major_coefficients", [1, 0, 0]),
            ("row_major_coefficients", [1, 0, 0, 0.5]),
            ("row_major_coefficients", [1, 5e-324, 0, 1]),
            ("target_increment", [0]),
        ):
            data = good.to_payload()
            data["resource_transform"][field] = value
            with self.subTest(field=field, value=value):
                self.assert_rejected(
                    owner,
                    GRCV4MappedTopologyEventRequest.from_payload(data),
                    "invalid_topology_event",
                )
        for invalid in (True, float("nan"), float("inf"), -0.0, -1, 2**53 + 1):
            data = copy.deepcopy(good.to_payload())
            data["resource_transform"]["row_major_coefficients"][0] = invalid
            with self.subTest(invalid=repr(invalid)), self.assertRaises(ValueError):
                GRCV4MappedTopologyEventRequest.from_payload(data)
        for field in ("source_vertex_ids", "target_vertex_ids"):
            data = good.to_payload()
            data["resource_transform"][field] = ["u", "u"]
            self.assert_rejected(
                owner,
                GRCV4MappedTopologyEventRequest.from_payload(data),
                "invalid_topology_event",
            )
        self.assertEqual(
            decode_mapped_topology_event_request(
                canonical_json_bytes(good.to_payload()), encoding="canonical"
            ),
            good,
        )
        detached = good.to_payload()
        detached["resource_transform"]["row_major_coefficients"][0] = 99
        self.assertEqual(good.resource_transform.row_major_coefficients, (1, 0, 0, 1))

    def test_native_negative_reset_and_unrepresentable_affine_charge_fail_atomically(
        self,
    ) -> None:
        owner = CandidateCOSOperation(dyadic_fixture())
        owner.set_state(_p946_assignment(owner, (1, 3)))
        # The live image (1,1) is nonnegative; reset maps to (3,-1).
        self.assert_rejected(
            owner,
            event_request(owner, owner.reference, [1, 0, 0, 1], [0, -2]),
            "domain_failure",
            "target_construction",
        )
        # Finite mapped coordinates but exact Q change cannot fit binary64.
        self.assert_rejected(
            owner,
            event_request(owner, owner.reference, [1, 0, 0, 1], [1e20, 0]),
            "charge_failure",
            "target_construction",
        )
        # Two individually finite coordinates overflow the prescribed charge sum.
        self.assert_rejected(
            owner,
            event_request(owner, owner.reference, [1, 0, 0, 1], [1e308, 1e308]),
            "charge_failure",
            "target_construction",
        )
        result = owner.apply_topology_event(
            event_request(owner, owner.reference, [1, 0, 0, 1], [5e-324, 0])
        )
        self.assertTrue(result.committed)
        self.assertEqual(owner.state.current.C, (1, 3))
        self.assertEqual(
            cast(Any, result.emitted_receipts[0]).identity_payload["core"][
                "actual_charge_delta"
            ],
            0,
        )

    def test_native_target_current_and_reset_singularities_have_distinct_pressure(
        self,
    ) -> None:
        deformation = math.exp(0.25 * (0.5 * (math.tanh(3) + math.tanh(1))))
        retained = float(2 * Fraction(deformation) ** 2)
        beta = 1 + 2 * retained
        self.assertEqual(1 - Fraction(beta) + 2 * Fraction(retained), 0)
        target = os_fixture(
            candidate={
                "kappa_M_C": 0.5,
                "tau_C": 1,
                "chi_C": 1,
                "zeta_C": beta,
                "Lambda_C": 10,
            },
            geometry={"kappa_H": 0.0001},
        ).geometry.reference
        for current, reset in (((3, 1), (4, 0)), ((4, 0), (3, 1))):
            source = replace(
                dyadic_fixture(),
                current=GRCV4AuthoritativeState(current, None, None),
                reset=GRCV4AuthoritativeState(reset, None, None),
            )
            owner = CandidateCOSOperation(source, targets=(target,))
            with self.subTest(current=current, reset=reset):
                self.assert_rejected(
                    owner,
                    migration_request(owner, target),
                    "target_readmission_failure",
                    "target_readmission",
                )
                self.assert_rejected(
                    owner,
                    event_request(owner, target, [1, 0, 0, 1], [0, 0]),
                    "target_readmission_failure",
                    "target_readmission",
                )

    def test_split_removal_negative_increment_and_stable_identifier_permutation(
        self,
    ) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        graph = GRCV4Graph(
            ("w", "v", "u"), (OrientedEdge("f", "v", "w"), OrientedEdge("e", "u", "v"))
        )
        target = stage_reference_fixture(
            graph=graph,
            weights={"e": 2, "f": 2},
            gain=0,
            changes={
                "candidate": {"chi_C": 0, "zeta_C": 0, "kappa_M_C": 0},
                "charge": {"absolute_tolerance": 0, "relative_tolerance": 0},
            },
        )
        owner = CandidateCOSOperation(dyadic_fixture(), targets=(target,))
        original_ref = owner.reference
        owner.set_state(_p946_assignment(owner, (1, 3)))
        # Declared target order w,v,u. Half u is split to w; v loses 1/2.
        result = owner.apply_topology_event(
            event_request(owner, target, [0.5, 0, 0, 1, 0.5, 0], [0, -0.5, 0])
        )
        self.assertTrue(result.committed, result)
        self.assertEqual(owner.state.current.C, (0.5, 2.5, 0.5))
        self.assertEqual(owner.state.reset.authoritative.C, (1.5, 0.5, 1.5))
        self.assertEqual(owner.state.Q_target, 3.5)
        # Merge w back into u, restore the removed external charge.
        result = owner.apply_topology_event(
            event_request(owner, original_ref, [1, 0, 1, 0, 1, 0], [0, 0.5])
        )
        self.assertTrue(result.committed, result)
        self.assertEqual(owner.state.current.C, (1, 3))
        self.assertEqual(owner.state.reset.authoritative.C, (3, 1))
        self.assertEqual(owner.state.Q_target, 4)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_metadata_exclusion_and_crossing_receipt_semantic_corruption(self) -> None:
        import copy
        import pygrc.models.grc_v4_lifecycle as module
        from pygrc.models.grc_v4_step import make_commit_receipts as real

        owner = CandidateCOSOperation(dyadic_fixture())
        owner.step_v4(request(0))
        original = owner.snapshot()
        for operation in ("migration", "event"):
            for defect in (
                "parent",
                "history",
                "authority",
                "operation_kind",
                "event_id",
            ):
                if operation == "migration" and defect == "event_id":
                    continue

                def corrupt(payloads: Any, **kwargs: Any) -> Any:
                    data = copy.deepcopy(payloads)
                    if defect == "parent":
                        data[0]["core"]["parent_receipt_ids"] = []
                    elif defect == "history":
                        data[2], data[3] = data[3], data[2]
                    elif defect == "authority":
                        data[0]["core"]["target_authoritative_digest"] = (
                            "grcv4-authoritative-sha256:" + "0" * 64
                        )
                    elif defect == "event_id":
                        data[0]["event_id"] = "grc-event-sha256:" + "0" * 64
                    else:
                        data[0] = {
                            "schema_version": "grcv4-step-commit-receipt-v1",
                            "core": data[0]["core"],
                        }
                    return real(data, **kwargs)

                with (
                    self.subTest(operation=operation, defect=defect),
                    patch.object(module, "make_commit_receipts", side_effect=corrupt),
                    self.assertRaises(V4IdentityError),
                ):
                    if operation == "migration":
                        owner.migrate_profile(migration_request(owner, owner.reference))
                    else:
                        owner.apply_topology_event(
                            event_request(owner, owner.reference, [1, 0, 0, 1], [0, 0])
                        )
                self.assertEqual(owner.snapshot(), original)
        clone = owner.duplicate()
        first = owner.apply_topology_event(
            event_request(
                owner, owner.reference, [1, 0, 0, 1], [0, 0], metadata={"note": "first"}
            )
        )
        second = clone.apply_topology_event(
            event_request(
                clone,
                clone.reference,
                [1, 0, 0, 1],
                [0, 0],
                metadata={"note": "different"},
            )
        )
        self.assertEqual(first, second)
        self.assertEqual(owner.snapshot(), clone.snapshot())
        self.assertEqual(
            owner.snapshot()["transition_records"][-1]["request"]["metadata"], {}
        )

    def test_extended_snapshot_archive_tampering_and_duplicate_independence(
        self,
    ) -> None:
        import copy

        target = event_target()
        owner = CandidateCOSOperation(dyadic_fixture(), targets=(target,))
        before_crossing = owner.snapshot()
        self.assertEqual(owner.duplicate().snapshot(), before_crossing)
        owner.apply_topology_event(
            event_request(owner, target, [1, 0, 0, 1, 0, 0], [0, 0, 0.5])
        )
        original = owner.snapshot()
        for defect in (
            "missing",
            "duplicate",
            "commit",
            "map",
            "reset",
            "metadata",
            "registry",
            "duplicate_reference",
            "extra",
            "foreign_layout",
        ):
            altered = copy.deepcopy(original)
            row = altered["transition_records"][0]
            if defect == "missing":
                altered["transition_records"] = []
            elif defect == "duplicate":
                altered["transition_records"].append(copy.deepcopy(row))
            elif defect == "commit":
                row["commit_id"] = "grcv4-commit-sha256:" + "0" * 64
            elif defect == "map":
                row["request"]["resource_transform"]["target_increment"][-1] = 1
            elif defect == "reset":
                row["source_reset"]["authoritative"]["C"] = [1, 3]
            elif defect == "metadata":
                row["request"]["metadata"] = {"unowned": True}
            elif defect == "registry":
                altered["reference_registry"] = altered["reference_registry"][1:]
            elif defect == "duplicate_reference":
                altered["reference_registry"].append(altered["reference_registry"][0])
            elif defect == "extra":
                row["cache"] = 1
            else:
                altered["implementation_layout_id"] = "pygrc-c-os-snapshot-v1"
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                CandidateCOSOperation.from_state(altered)
            self.assertEqual(owner.snapshot(), original)
        clone = owner.duplicate()
        clone.set_state(_p946_assignment(clone, (1, 3, 0.5)))
        clone.rebase_reset_baseline()
        self.assertEqual(owner.snapshot(), original)
        clone.snapshot()["reference_registry"].clear()
        self.assertEqual(owner.snapshot(), original)
        self.assertEqual(clone.duplicate().snapshot(), clone.snapshot())

    def test_publication_checks_returned_crossing_map_and_atomic_reference_observation(
        self,
    ) -> None:
        import threading
        import pygrc.models.grc_v4_lifecycle as module

        target = event_target()
        owner = CandidateCOSOperation(dyadic_fixture(), targets=(target,))
        original = owner.snapshot()
        declaration = event_request(owner, target, [1, 0, 0, 1, 0, 0], [0, 0, 0.5])
        real = module._prepare_crossing
        for defect in ("current", "reset", "clock", "charge", "operation"):

            def corrupt(*args: Any) -> Any:
                valid = real(*args)
                return {
                    "current": replace(
                        valid, current=GRCV4AuthoritativeState((1, 3, 0.5), None, None)
                    ),
                    "reset": replace(
                        valid, reset=GRCV4AuthoritativeState((1, 3, 0.5), None, None)
                    ),
                    "clock": replace(valid, time=1),
                    "charge": replace(valid, Q_target=5),
                    "operation": replace(valid, operation_id="foreign"),
                }[defect]

            with (
                self.subTest(defect=defect),
                patch.object(module, "_prepare_crossing", side_effect=corrupt),
                self.assertRaises(ValueError),
            ):
                owner.apply_topology_event(declaration)
            self.assertEqual(owner.snapshot(), original)
        arrived, release = threading.Event(), threading.Event()
        errors: list[BaseException] = []
        real_validate = module._validate_publication

        def pause(*args: Any, **kwargs: Any) -> None:
            real_validate(*args, **kwargs)
            arrived.set()
            if not release.wait(30):
                raise TimeoutError("observation control was not released")

        def execute() -> None:
            try:
                owner.apply_topology_event(declaration)
            except BaseException as exc:
                errors.append(exc)

        with patch.object(module, "_validate_publication", side_effect=pause):
            worker = threading.Thread(target=execute)
            worker.start()
            try:
                self.assertTrue(arrived.wait(30))
                self.assertEqual(owner.snapshot(), original)
                self.assertEqual(
                    owner.reference.graph.graph_digest,
                    original["scientific_state"]["graph_digest"],
                )
            finally:
                release.set()
                worker.join(30)
            self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(owner.reference, target)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_published_affine_vector_identities_and_admitted_runtime_companion(
        self,
    ) -> None:
        import json
        import runpy
        import subprocess
        from pathlib import Path
        from pygrc.models.grc_v4 import GRCV4MappedTopologyEventRequest
        from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry, GRCV4Context
        from pygrc.models.grc_v4_profile import resolve_profile
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        root = Path(__file__).resolve().parents[2]
        vector = json.loads(
            subprocess.check_output(["git", "show",
                "f10d105bbed71da7e9a58d851b18e9799a952e0c:specs/grc-v4-conformance-vectors.json"], cwd=root)
        )["grcv4_mapped_topology_event_vectors"][0]
        declaration = GRCV4MappedTopologyEventRequest.from_payload(vector["request"])
        self.assertEqual(
            identity("grc-event-sha256", vector["event_identity_payload"]),
            vector["expected"]["event_id"],
        )
        self.assertEqual(
            canonical_json_bytes(vector["event_identity_payload"]).decode(),
            vector["event_identity_canonical_jcs_utf8"],
        )
        # Recover the exact published profile; the supplied K4 preimage is 2x2
        # for a one-edge source. This edge-coordinate backend cannot instantiate
        # that exact profile. Keep this applicability limit visible, not waived.
        builder = runpy.run_path(
            str(
                root
                / "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py"
            )
        )
        params = builder["resolved_params"]({"e-uv": 1})
        profile_data = builder["profile_payload"](
            builder["identity"]("grcv4-params-sha256", params)
        )
        profile = resolve_profile(params, profile_data)
        source_graph = GRCV4Graph(("u", "v"), (OrientedEdge("e-uv", "u", "v"),))
        self.assertEqual(source_graph.graph_digest, declaration.source_graph_digest)
        source_reset = {
            "schema_version": "grcv4-reset-baseline-v1",
            "active_model_identity": profile.complete_profile_id,
            "graph_digest": source_graph.graph_digest,
            "orientation_identity": "tail_to_head_edge_id_order_v1",
            "authoritative": {"C": [1, 2], "W_A": None, "Z_4": None},
            "Q_target": 3,
            "context_contract_id": "constant_zero_context_v1",
        }
        source_science = {
            "schema_version": "grcv4-scientific-state-v1",
            **{k: v for k, v in source_reset.items() if k not in ("schema_version",)},
            "reset_digest": identity("grcv4-reset-sha256", source_reset),
            "step_index": 0,
            "time": 0,
            "context_value_digest": None,
        }
        self.assertEqual(scientific_id(source_science), declaration.source_state_digest)
        with self.assertRaisesRegex(ValueError, "K4|dimension|shape|coordinate"):
            GRCV4ReferenceGeometry(
                source_graph,
                profile,
                GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
                ((1, 0), (0, 1)),
                FrozenJSONMap({"e-uv": 1}),
            )
        # Same graph/map/resources, independently admitted complete references.
        changes = {
            "candidate": {"chi_C": 0, "zeta_C": 0, "tau_C": 0, "kappa_M_C": 0},
            "charge": {"absolute_tolerance": 0, "relative_tolerance": 0},
        }
        source = current_fixture(
            graph=source_graph,
            weights={"e-uv": 1},
            resource=(1, 2),
            changes={**changes, "geometry": {"kappa_H": 0}},
        )
        target = stage_reference_fixture(
            graph=GRCV4Graph.from_payload(declaration.target_graph),
            weights={"e-uv": 1, "e-vw": 2},
            gain=0,
            changes=changes,
        )
        owner = CandidateCOSOperation(source, targets=(target,))
        runtime = GRCV4MappedTopologyEventRequest.from_payload(
            {
                **vector["request"],
                "source_state_digest": owner.state.scientific_state_digest,
                "target_profile_id": target.profile.complete_profile_id,
            }
        )
        result = owner.apply_topology_event(runtime)
        self.assertTrue(result.committed, result)
        self.assertEqual(
            list(owner.state.current.C), vector["expected"]["target_resource"]
        )
        self.assertEqual(owner.state.Q_target, vector["expected"]["target_Q_target"])
        primary = cast(Any, result.emitted_receipts[0]).identity_payload
        self.assertNotEqual(primary["event_id"], vector["expected"]["event_id"])
        self.assertEqual(
            primary["core"]["resource_transform_digest"],
            vector["expected"]["resource_transform_digest"],
        )
        self.assertEqual(
            primary["core"]["history_bundle_digest"],
            vector["expected"]["history_bundle_digest"],
        )
        self.assertEqual(primary["core"]["actual_charge_delta"], 0.5)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_target_charge_readmission_checks_reset_independently(self) -> None:
        target = dyadic_fixture().geometry.reference
        source = replace(
            os_fixture(
                candidate={"tau_C": 0, "chi_C": 1, "zeta_C": 3},
                geometry={"kappa_H": 0},
                charge={"absolute_tolerance": 0.5, "relative_tolerance": 0},
            ),
            reset=GRCV4AuthoritativeState((3, 1.5), None, None),
        )
        owner = CandidateCOSOperation(source, targets=(target,))
        # Same live C=3,1 and Q=4 is admitted by the tight target, but reset's
        # Q_actual=4.5 is admitted only by the source tolerance.
        CandidateCOSOperation(dyadic_fixture())
        self.assert_rejected(
            owner,
            migration_request(owner, target),
            "target_readmission_failure",
            "target_readmission",
        )
        self.assert_rejected(
            owner,
            event_request(owner, target, [1, 0, 0, 1], [0, 0]),
            "target_readmission_failure",
            "target_readmission",
        )

    def test_registry_requires_unique_complete_reference_preimages(self) -> None:
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        inputs = dyadic_fixture()
        with self.assertRaisesRegex(ValueError, "duplicate|ambiguous"):
            CandidateCOSOperation(inputs, targets=(inputs.geometry.reference,))
        target = event_target()
        for weights in ({"e": 2.0}, {"e": 2.0, "f": 2.0, "foreign": 1.0}):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                stage_reference_fixture(graph=target.graph, weights=weights)
        with self.assertRaisesRegex(ValueError, "C_OS"):
            CandidateCOSOperation(inputs, targets=(stage_reference_fixture("A", "OS"),))
        # A valid profile registered for another graph does not authorize
        # ordinary migration to that graph. Only the event route supplies a map.
        owner = CandidateCOSOperation(inputs, targets=(target,))
        self.assert_rejected(
            owner, migration_request(owner, target), "unsupported_profile"
        )


_P946_METHODS = (
    "test_dyadic_snapshot_embeds_exact_preimages_and_acyclic_identities",
    "test_reset_after_ordinary_preserves_lineage_clock_profile_and_charge",
    "test_rebase_reset_and_assignment_have_distinct_exact_effects",
    "test_repeated_identity_operations_append_distinct_commits_without_writers",
    "test_deep_independence_of_snapshot_duplicate_copy_and_retained_state",
    "test_restoration_detaches_caller_payload_and_asserts_parameters",
    "test_closed_snapshot_requires_every_field_and_rejects_extra_authority",
    "test_null_wrong_typed_and_stale_digest_fields_never_disable_verification",
    "test_rehashed_cross_identity_mismatch_still_rejects",
    "test_rehashed_negative_history_shape_and_charge_inputs_fail_readmission",
    "test_native_singular_current_and_reset_reject_even_with_coherent_hashes",
    "test_set_state_validates_full_target_and_forbids_lifecycle_replacement",
    "test_load_verifies_historical_commit_preimages_and_order",
    "test_reference_content_and_every_nested_identity_are_load_bearing",
    "test_charge_tolerance_reset_receipt_reports_actual_negative_delta",
    "test_loop_parallel_isolated_and_permuted_graphs_roundtrip_with_exact_maps",
    "test_canonical_save_load_rejects_duplicate_keys_nonfinite_and_negative_zero",
    "test_save_load_fresh_process_and_large_canonical_clock_tokens",
    "test_all_administrative_faults_keep_state_and_commit_preimages_atomic",
    "test_restoration_and_assignment_do_not_publish_before_final_readmission",
    "test_rehashed_receipt_semantic_contradictions_reject",
    "test_restored_positive_continuation_has_literal_dyadic_resource",
    "test_snapshot_during_admission_observes_one_state_and_commit_generation",
)


def capture_p946(output: str) -> int:
    """One source-bound focused run; replay source comes from Git history."""
    from datetime import datetime, timezone
    import hashlib
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import subprocess
    from tests.models.test_grc_v4_candidate_c import _p941_execute

    root = Path(__file__).resolve().parents[2]
    generated = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    )
    destination = (root / output).resolve()
    if (
        not destination.is_relative_to(generated.resolve())
        or destination == generated.resolve()
        or destination.exists()
    ):
        raise ValueError(
            "capture requires a fresh repository-local generated destination"
        )
    base = "ec9f8662d08eafc5346837ddbbb74c9a4359a9b4"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=root, check=True
    )
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    ]
    overrides = {
        "src/pygrc/models/grc_v4_codec.py",
        "src/pygrc/models/grc_v4_lifecycle.py",
        "tests/models/test_grc_v4_lifecycle.py",
    }

    def snapshot() -> dict[str, str]:
        names = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                *scopes,
            ],
            cwd=root,
            text=True,
        ).splitlines()
        return {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest()
            for n in sorted(set(names))
        }

    before = snapshot()
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    base_names = set(
        subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", base, "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | (set(before) - base_names)) - overrides or base_names - set(before):
        raise ValueError("source differs outside the P9-4.6 reconstruction envelope")
    import ast

    # Accepted predecessor source pins shared test names; current discovery
    # cannot turn a renamed/skipped test into a smaller successful obligation.
    shared: set[str] = set()
    for module, classes in {
        "test_grc_v4_lifecycle": {"CandidateCOSOperationTests"},
        "test_grc_v4_codec": {"CodecTests"},
        "test_grc_v4_state": {"FrozenJSONTests", "LifecycleOwnershipTests"},
    }.items():
        base_tests = ast.parse(
            subprocess.check_output(
                ["git", "show", base + ":tests/models/" + module + ".py"], cwd=root
            )
        )
        shared.update(
            "tests.models." + module + "." + c.name + "." + n.name
            for c in base_tests.body
            if isinstance(c, ast.ClassDef) and c.name in classes
            for n in c.body
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        )
    required = shared | {
        "tests.models.test_grc_v4_lifecycle.CandidateCOSLifecycleTests." + n
        for n in _P946_METHODS
    }
    import importlib

    importlib.import_module("tests.models.test_grc_v4_transport")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    started = datetime.now(timezone.utc).isoformat()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.6",
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Overlay only the listed hash-matching source files from the commit containing this run onto base_commit; verify the scoped manifest. Before commit, use the reviewed working tree.",
        },
        "required_ids": sorted(required),
        "started_utc": started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            key: os.environ.get(key)
            for key in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_lifecycle",
            "--capture-p946",
            str(destination.relative_to(root)),
        ],
        "claim_ceiling": "Bounded C_OS snapshot/load/reset/rebase/set-state and deep independence, plus accepted ordinary-operation and codec/immutable-state regression. P9-7.1-C_OS slice only; no full replay/receipt-ownership, event/migration, public facade/profile conformance or cross-platform bitwise claim.",
        "numerical_policy": "Inherited C stage/star/geometry binary64 policy; exact reference-relative split tolerance via symmetric inertia; fixed-rank affine selector path certification with a 256-bisection fail-closed ceiling. Positive subnormal durations are never classified as zero.",
    }
    record.update(
        _p941_execute(
            root,
            before,
            required,
            suite,
            snapshot,
            extra_modules=frozenset(
                {
                    "pygrc.models.grc_v4_codec",
                    "tests.models.test_grc_v4_codec",
                    "pygrc.models.grc_v4_state",
                    "tests.models.test_grc_v4_state",
                    "pygrc.models.grc_v4_geometry",
                    "pygrc.models.grc_v4_transport",
                    "pygrc.models.grc_v4_step",
                    "pygrc.models.grc_v4_realizations",
                    "pygrc.models.grc_v4_lifecycle",
                    "tests.models.test_grc_v4_lifecycle",
                    "tests.models.test_grc_v4_realizations",
                }
            ),
        )
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["live_source_check_limits"] = (
        "Inherited source-slot, live-code, before/after disk and exact executed-roster checks; not hostile-interpreter attestation. Relocated checkout and fresh interpreter reuse the installed dependency environment; no fresh-install or different-platform claim."
    )
    if record.get("loaded_sources_before") == record.get("loaded_sources_after"):
        record["loaded_sources"] = record.pop("loaded_sources_before")
        record.pop("loaded_sources_after")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print("P9-4.6", record["status"], json.dumps(record.get("results", {})), flush=True)
    if record["status"] != "passed":
        print(record.get("capture_error", record.get("failure_output", "")), flush=True)
    return 0 if record["status"] == "passed" else 1


_P947AB_METHODS = {
    "CandidateCOSReplayTests": (
        "test_live_clock_and_resource_against_rational_oracle",
        "test_four_invalid_live_transition_controls_cannot_publish",
        "test_complete_authority_replacement_controls_cannot_publish",
        "test_failed_operations_preserve_seeded_tuple_and_recovery_replay",
        "test_native_solver_failure_preserves_existing_ledger_and_reset",
        "test_failure_receipts_never_become_persistent_authority",
        "test_interleaved_ledger_deltas_and_parent_scope",
        "test_missing_foreign_and_reordered_parents_reject_after_coherent_rehash",
        "test_deterministic_replay_every_checkpoint_with_rational_expected_states",
        "test_replay_does_not_consume_saved_observables_or_old_results",
        "test_seeded_programmer_failures_preserve_reference_and_commit_archive",
    ),
    "CandidateCOSAuditCorrectionTests": (
        "test_administrative_returned_target_cannot_exploit_empty_ledger",
        "test_schema_valid_administrative_corruption_never_publishes",
        "test_exact_audit_zero_then_minimum_positive_clock_cases",
        "test_unreceipted_assignment_preserves_snapshot_continuation_replay",
    ),
    "CandidateCOSCrossingTests": (
        "test_target_charge_readmission_checks_reset_independently",
        "test_registry_requires_unique_complete_reference_preimages",
        "test_parameter_migration_preserves_both_states_and_reset_after_migration",
        "test_affine_increment_maps_distinct_live_and_reset_then_replays",
        "test_unregistered_target_families_and_stale_identity_are_explicit",
        "test_separate_history_channels_reject_invented_retention_loss_and_initializers",
        "test_map_shape_conservation_order_and_numeric_wire_domains",
        "test_native_negative_reset_and_unrepresentable_affine_charge_fail_atomically",
        "test_native_target_current_and_reset_singularities_have_distinct_pressure",
        "test_split_removal_negative_increment_and_stable_identifier_permutation",
        "test_metadata_exclusion_and_crossing_receipt_semantic_corruption",
        "test_extended_snapshot_archive_tampering_and_duplicate_independence",
        "test_publication_checks_returned_crossing_map_and_atomic_reference_observation",
        "test_published_affine_vector_identities_and_admitted_runtime_companion",
    ),
}


def capture_p947ab(output: str) -> int:
    """One source-bound focused run; replay source comes from Git history."""
    from datetime import datetime, timezone
    import hashlib
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import subprocess
    from tests.models.test_grc_v4_candidate_c import _p941_execute

    root = Path(__file__).resolve().parents[2]
    generated = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    )
    destination = (root / output).resolve()
    if (
        not destination.is_relative_to(generated.resolve())
        or destination == generated.resolve()
        or destination.exists()
    ):
        raise ValueError(
            "capture requires a fresh repository-local generated destination"
        )
    base = "f10d105bbed71da7e9a58d851b18e9799a952e0c"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=root, check=True
    )
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
        "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py",
    ]
    overrides = {
        "src/pygrc/models/grc_v4.py",
        "src/pygrc/models/grc_v4_codec.py",
        "src/pygrc/models/grc_v4_lifecycle.py",
        "tests/models/test_grc_v4_lifecycle.py",
    }

    def snapshot() -> dict[str, str]:
        names = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                *scopes,
            ],
            cwd=root,
            text=True,
        ).splitlines()
        return {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest()
            for n in sorted(set(names))
        }

    before = snapshot()
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    base_names = set(
        subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", base, "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | (set(before) - base_names)) - overrides or base_names - set(before):
        raise ValueError("source differs outside the P9-4.7ab reconstruction envelope")
    import ast

    # Accepted predecessor source pins shared test names; current discovery
    # cannot turn a renamed/skipped test into a smaller successful obligation.
    shared: set[str] = set()
    for module, classes in {
        "test_grc_v4_lifecycle": {
            "CandidateCOSOperationTests",
            "CandidateCOSLifecycleTests",
        },
        "test_grc_v4": {"FoundationIntegrationTests", "RequestTests"},
        "test_grc_v4_codec": {"CodecTests"},
        "test_grc_v4_state": {"FrozenJSONTests", "LifecycleOwnershipTests"},
    }.items():
        base_tests = ast.parse(
            subprocess.check_output(
                ["git", "show", base + ":tests/models/" + module + ".py"], cwd=root
            )
        )
        shared.update(
            "tests.models." + module + "." + c.name + "." + n.name
            for c in base_tests.body
            if isinstance(c, ast.ClassDef) and c.name in classes
            for n in c.body
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        )
    required = shared | {
        "tests.models.test_grc_v4_lifecycle." + cls + "." + name
        for cls, methods in _P947AB_METHODS.items()
        for name in methods
    }
    import importlib

    importlib.import_module("tests.models.test_grc_v4_transport")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    started = datetime.now(timezone.utc).isoformat()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.7ab",
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Overlay only the listed hash-matching source files from the commit containing this run onto base_commit; verify the scoped manifest. Before commit, use the reviewed working tree.",
        },
        "required_ids": sorted(required),
        "started_utc": started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            key: os.environ.get(key)
            for key in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_lifecycle",
            "--capture-p947ab",
            str(destination.relative_to(root)),
        ],
        "claim_ceiling": "C_OS failed-step atomicity, local receipt ownership, snapshot continuation replay, registered same-candidate nonhistory migration and affine mapped events over current AND reset; P9-4.6 audit correction regressions. Exact published mapped-vector backend applicability remains unresolved; the admitted runtime companion has rederived profile/event identities. No historical truth authentication, full parent-DAG conformance, public facade/profile acceptance or cross-platform bitwise claim.",
        "numerical_policy": "Inherited C stage/star/geometry binary64 policy; exact reference-relative split tolerance via symmetric inertia; fixed-rank affine selector path certification with a 256-bisection fail-closed ceiling. Positive subnormal durations are never classified as zero.",
    }
    record.update(
        _p941_execute(
            root,
            before,
            required,
            suite,
            snapshot,
            extra_modules=frozenset(
                {
                    "pygrc.models.grc_v4",
                    "tests.models.test_grc_v4",
                    "pygrc.models.grc_v4_codec",
                    "tests.models.test_grc_v4_codec",
                    "pygrc.models.grc_v4_state",
                    "tests.models.test_grc_v4_state",
                    "pygrc.models.grc_v4_geometry",
                    "pygrc.models.grc_v4_transport",
                    "pygrc.models.grc_v4_step",
                    "pygrc.models.grc_v4_realizations",
                    "pygrc.models.grc_v4_lifecycle",
                    "tests.models.test_grc_v4_lifecycle",
                    "tests.models.test_grc_v4_realizations",
                }
            ),
        )
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["live_source_check_limits"] = (
        "Inherited source-slot, live-code, before/after disk and exact executed-roster checks; not hostile-interpreter attestation. Relocated checkout and fresh interpreter reuse the installed dependency environment; no fresh-install or different-platform claim."
    )
    if record.get("loaded_sources_before") == record.get("loaded_sources_after"):
        record["loaded_sources"] = record.pop("loaded_sources_before")
        record.pop("loaded_sources_after")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(
        "P9-4.7ab", record["status"], json.dumps(record.get("results", {})), flush=True
    )
    if record["status"] != "passed":
        print(record.get("capture_error", record.get("failure_output", "")), flush=True)
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p945":
        raise SystemExit(capture_p945(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p946":
        raise SystemExit(capture_p946(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p947ab":
        raise SystemExit(capture_p947ab(sys.argv[2]))
    unittest.main()
