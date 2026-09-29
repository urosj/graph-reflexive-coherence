"""Bounded numerical continuation never replaces state or publication admission."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from unittest.mock import patch

from pygrc.models import _grc_v4_matrix as arithmetic
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models import grc_v4_pc as pc
from pygrc.models import grc_v4_rg2b as rg
from pygrc.models import grc_v4_rg2b_graph as rg_graph
from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_linear import (
    _ConditionFact,
    _InverseFact,
    _MatrixContinuation,
    _MatrixFacts,
)
from tests.models.test_grc_v4_cipc import fixture as cipc_fixture
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_pc import fixture
from tests.models.test_grc_v4_rg2b_graph import graph_fixture


class MatrixContinuationTests(unittest.TestCase):
    def test_continuation_rejects_more_than_four_facts_or_two_matrices(self):
        facts = tuple(
            _InverseFact(((Fraction(i),),), ((Fraction(1, i),),))
            for i in range(1, 4)
        )
        with self.assertRaisesRegex(ValueError, "two matrices"):
            _MatrixContinuation(facts)
        with self.assertRaisesRegex(ValueError, "four facts"):
            _MatrixContinuation((facts[0],) * 5)
        with self.assertRaises(TypeError):
            _MatrixContinuation((object(),))
        continuation = _MatrixContinuation((facts[0],))
        with self.assertRaises(FrozenInstanceError):
            continuation.facts = ()

    def test_retention_selects_only_named_matrices_and_the_current_limit(self):
        store = _MatrixFacts()
        matrices = [((Fraction(i),),) for i in (1, 2, 3)]
        for matrix in matrices:
            store.remember(_InverseFact(matrix, ((1 / matrix[0][0],),)))
            for limit in (Fraction(2), Fraction(3)):
                store.remember(_ConditionFact(matrix, limit, Fraction(1)))
        retained = store.retain(matrices[0], matrices[1], Fraction(2))
        self.assertEqual(len(retained.facts), 4)
        fresh = _MatrixFacts()
        fresh.seed(retained)
        for matrix in matrices[:2]:
            self.assertIsNotNone(fresh.find(matrix))
            self.assertIsNotNone(fresh.find(matrix, Fraction(2)))
            self.assertIsNone(fresh.find(matrix, Fraction(3)))
        self.assertIsNone(fresh.find(matrices[2]))
        self.assertEqual(
            len(store.retain(matrices[0], matrices[0], Fraction(2)).facts), 2
        )
        self.assertFalse(_MatrixFacts().retain(*matrices[:2], Fraction(2)).facts)

    def test_seeded_facts_still_check_current_limits_coefficients_and_rhs(self):
        policy = fixture("A")[0].geometry.reference.profile.params_resolved.solver
        matrix = ((3.0, 1.0), (1.0, 3.0))
        exact = numerics.exact_matrix(matrix)
        admitted = replace(policy, conditioning_limit=2.0)
        with codec._operation_contract_assets() as operation:
            numerics.solve(matrix, ((1.0,), (2.0,)), admitted, "old", [])
            retained = operation.matrix_facts.retain(exact, exact, Fraction(2))
        with (
            codec._operation_contract_assets() as operation,
            patch.object(arithmetic, "inverse", wraps=arithmetic.inverse
            ) as inverse,
            patch.object(arithmetic, "condition_bound",
                wraps=arithmetic.condition_bound,
            ) as condition,
        ):
            operation.matrix_facts.seed(retained)
            certificates = []
            numerics.solve(matrix, ((2.0,), (1.0,)), admitted, "new", certificates)
            self.assertEqual(certificates[0]["block"], "new")
            self.assertEqual((inverse.call_count, condition.call_count), (0, 0))
            for label in ("strict", "strict retry"):
                with self.assertRaisesRegex(ValueError, "conditioning limit exceeded: " + label):
                    numerics.solve(
                        matrix, ((1.0,), (2.0,)),
                        replace(policy, conditioning_limit=1.5), label, [],
                    )
            self.assertEqual(condition.call_count, 2)
            changed = ((4.0, 1.0), (1.0, 3.0))
            numerics.solve(changed, ((1.0,), (2.0,)), policy, "changed", [])
            self.assertEqual(inverse.call_count, 1)
        with codec._operation_contract_assets() as operation:
            numerics.solve(((3.0,),), ((1.0,),), policy, "warm third", [])
            retained = operation.matrix_facts.retain(
                ((Fraction(3),),), ((Fraction(3),),), Fraction(policy.conditioning_limit)
            )
        with codec._operation_contract_assets() as operation:
            operation.matrix_facts.seed(retained)
            with self.assertRaisesRegex(ValueError, "residual tolerance failed: fresh RHS"):
                numerics.solve(
                    ((3.0,),), ((5e-324,),),
                    replace(policy, absolute_tolerance=0.0, relative_tolerance=0.0),
                    "fresh RHS", [],
                )


class PCContinuationTests(unittest.TestCase):
    initial_condition_computations = 3
    later_condition_computations = 1

    def owner(self, candidate="A"):
        before, backend = fixture(candidate, reset_z=(0.125,))
        return before, GRCV4(before, differential_reference=backend)

    def step(self, before, owner, index, duration=None):
        result = owner.step_v4_input(request(
            before.dt if duration is None else duration, f"continuation-{index}"
        ))
        self.assertTrue(result.committed, result.failure)
        return result

    def test_public_steps_reuse_only_reset_and_previous_final_and_match_cold(self):
        before, warm = self.owner()
        _, cold = self.owner()
        ordinary_condition = arithmetic.condition_bound
        large_computations = []

        def condition(matrix, limit, label):
            large_computations.append(matrix)
            return ordinary_condition(matrix, limit, label)

        with patch.object(arithmetic, "condition_bound", side_effect=condition):
            for index in range(3):
                start = len(large_computations)
                actual = self.step(before, warm, index)
                self.assertEqual(len(large_computations) - start, self.initial_condition_computations if index == 0 else self.later_condition_computations)
                continuation = warm._operation._owned.matrix_continuation
                self.assertEqual(len(continuation.facts), 4)
                self.assertEqual(len({f.matrix for f in continuation.facts}), 2)
                with patch.object(_MatrixFacts, "retain", return_value=_MatrixContinuation()):
                    expected = self.step(before, cold, index)
                self.assertEqual(actual.to_canonical_bytes(), expected.to_canonical_bytes())
                self.assertEqual(warm.snapshot(), cold.snapshot())

    def test_zero_and_negative_duration_retain_correctness(self):
        for candidate in ("A", "C"):
            with self.subTest(candidate=candidate):
                before, warm = self.owner(candidate)
                _, cold = self.owner(candidate)
                self.step(before, warm, "warm")
                with patch.object(_MatrixFacts, "retain", return_value=_MatrixContinuation()):
                    self.step(before, cold, "warm")
                for index, dt in enumerate((0.0, -before.dt, before.dt)):
                    command = request(dt, f"mixed-continuation-{index}")
                    publication = warm._operation._owned
                    actual = warm.step_v4_input(command)
                    with patch.object(_MatrixFacts, "retain", return_value=_MatrixContinuation()):
                        expected = cold.step_v4_input(command)
                    self.assertEqual(actual.to_canonical_bytes(), expected.to_canonical_bytes())
                    self.assertEqual(warm.snapshot(), cold.snapshot())
                    if dt < 0:
                        self.assertIs(warm._operation._owned, publication)

    def test_asset_failure_cannot_publish_new_facts_and_retry_recalculates(self):
        before, owner = self.owner()
        self.step(before, owner, "warm")
        publication = owner._operation._owned
        snapshot = codec.canonical_json_bytes(owner.snapshot())
        with (
            patch.object(arithmetic, "condition_bound",
                         wraps=arithmetic.condition_bound) as condition,
            patch.object(lifecycle, "_verify_contract_assets",
                         side_effect=codec.V4AssetError("changed asset")),
            self.assertRaisesRegex(codec.V4AssetError, "changed asset"),
        ):
            owner.step_v4_input(request(before.dt, "failed-publication"))
        self.assertEqual(condition.call_count, self.later_condition_computations)
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(codec.canonical_json_bytes(owner.snapshot()), snapshot)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())
        with patch.object(arithmetic, "condition_bound",
                          wraps=arithmetic.condition_bound) as retry:
            self.step(before, owner, "retry")
        self.assertEqual(retry.call_count, self.later_condition_computations)

    def numerical_failure(self):
        return patch.object(pc, "scalar_zoh", side_effect=pc.PCStageError(
            "no_admitted_root", "unresolved writer"
        ))

    def test_numerical_failure_leaves_publication_and_continuation_unchanged(self):
        before, owner = self.owner()
        self.step(before, owner, "warm")
        publication = owner._operation._owned
        with self.numerical_failure():
            result = owner.step_v4_input(request(before.dt, "failed-writer"))
        self.assertFalse(result.committed)
        self.assertIs(owner._operation._owned, publication)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())
        self.step(before, owner, "retry")

    def test_restore_duplicate_reset_rebase_and_set_state_start_cold(self):
        for action in ("restore", "duplicate", "reset", "rebase", "set_state"):
            with self.subTest(action=action):
                before, owner = self.owner()
                self.step(before, owner, "warm")
                snapshot = owner.snapshot()
                if action == "restore":
                    owner = restore(snapshot)
                    self.assertEqual(owner.snapshot(), snapshot)
                elif action == "duplicate":
                    owner = owner.duplicate()
                    self.assertEqual(owner.snapshot(), snapshot)
                elif action == "reset":
                    owner.reset()
                elif action == "rebase":
                    owner.rebase_reset_baseline()
                else:
                    owner.set_state(owner.state)
                self.assertFalse(owner._operation._owned.matrix_continuation.facts)
                self.step(before, owner, "after-change")
                self.assertTrue(owner._operation._owned.matrix_continuation.facts)

    def test_new_owners_and_concurrent_steps_do_not_share_continuations(self):
        before, first = self.owner()
        _, other = self.owner()
        self.step(before, first, "warm")
        self.assertFalse(other._operation._owned.matrix_continuation.facts)
        _, serial = self.owner()
        _, concurrent = self.owner()
        for index in range(3):
            self.step(before, serial, "shared-request")
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(
                lambda _: concurrent.step_v4_input(request(before.dt, "continuation-shared-request")),
                range(3),
            ))
        self.assertTrue(all(result.committed for result in results))
        self.assertEqual(concurrent.snapshot(), serial.snapshot())
        self.assertEqual(len(concurrent._operation._owned.matrix_continuation.facts), 4)


class CIPCContinuationTests(PCContinuationTests):
    initial_condition_computations = 4
    later_condition_computations = 2

    def owner(self, candidate="A"):
        before, backend = cipc_fixture(candidate, reset_z=(0.125,))
        return before, GRCV4(before, differential_reference=backend)

    def test_warm_facts_leave_root_envelopes_trials_and_carrier_writes_fresh(self):
        before, warm = self.owner()
        _, cold = self.owner()

        def execute(owner, disable):
            with (
                patch.object(ci.CIContractionCertificate, "__post_init__",
                             autospec=True, side_effect=ci.CIContractionCertificate.__post_init__) as contraction,
                patch.object(ci.CITrial, "__post_init__",
                             autospec=True, side_effect=ci.CITrial.__post_init__) as trial,
                patch.object(pc.PCEnvelopeCertificate, "__post_init__",
                             autospec=True, side_effect=pc.PCEnvelopeCertificate.__post_init__) as envelope,
                patch.object(pc, "scalar_zoh", wraps=pc.scalar_zoh) as writer,
            ):
                for index in range(3):
                    with (patch.object(_MatrixFacts, "retain", return_value=_MatrixContinuation())
                          if disable else nullcontext()):
                        self.step(before, owner, index)
            return contraction.call_count, trial.call_count, envelope.call_count, writer.call_count

        actual = execute(warm, False)
        self.assertEqual(actual, execute(cold, True))
        self.assertEqual((actual[0], actual[2], actual[3]), (9, 9, 3))
        self.assertGreaterEqual(actual[1], 18)
        self.assertEqual(warm.snapshot(), cold.snapshot())

    def test_warm_facts_cannot_bypass_root_domain_admission(self):
        before, owner = self.owner()
        self.step(before, owner, "warm")
        publication = owner._operation._owned
        with patch.object(ci.CIContractionCertificate, "__post_init__",
                          side_effect=ci.CIStageError("domain_failure", "uncertified root domain")):
            result = owner.step_v4_input(request(before.dt, "failed-domain"))
        self.assertFalse(result.committed)
        self.assertIs(owner._operation._owned, publication)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())
        self.step(before, owner, "retry")


class RG2bContinuationTests(PCContinuationTests):
    initial_condition_computations = 4
    later_condition_computations = 2

    def owner(self, candidate="A"):
        before, backend = graph_fixture(candidate, n=3, tolerance=1e-8)
        resources = list(before.current.C)
        resources[0] += 2**-12
        resources[-1] -= 2**-12
        weights = (
            None if before.current.W_A is None
            else tuple(w - 2**-12 for w in before.current.W_A)
        )
        reset = type(before.current)(tuple(resources), weights, None)
        before = replace(before, reset=reset)
        return before, GRCV4(before, differential_reference=backend)

    def numerical_failure(self):
        return patch.object(rg_graph, "native_bridge", side_effect=rg.RG2bStageError(
            "uncertified native bridge"
        ))

    def test_warm_facts_leave_sections_certificates_and_bridges_fresh(self):
        before, owner = self.owner()
        with (
            patch.object(rg_graph, "section", wraps=rg_graph.section) as section,
            patch.object(rg.RG2bCertificate, "__post_init__",
                         autospec=True, side_effect=rg.RG2bCertificate.__post_init__) as certificate,
            patch.object(rg_graph, "native_bridge", wraps=rg_graph.native_bridge) as bridge,
        ):
            for index in range(3):
                self.step(before, owner, index)
        self.assertEqual(section.call_count, 9)
        self.assertEqual(certificate.call_count, 9)
        self.assertEqual(bridge.call_count, 3)

    def test_warm_facts_do_not_admit_a_different_frozen_beat_duration(self):
        before, owner = self.owner()
        self.step(before, owner, "warm")
        publication = owner._operation._owned
        result = owner.step_v4_input(request(before.dt * 2, "invalid-beat"))
        self.assertFalse(result.committed)
        self.assertIs(owner._operation._owned, publication)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())


if __name__ == "__main__":
    unittest.main()
