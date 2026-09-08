"""Actual C_OS ordinary operations: independent oracles and atomic pressure.

Fault-injection tests are explicitly controls, separate from native failures.
No complete facade, reset/load/migration or global profile conformance claim.
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p945":
        raise SystemExit(capture_p945(sys.argv[2]))
    unittest.main()
