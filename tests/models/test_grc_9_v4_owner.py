"""P9-9.1b mixed-owner lifecycle pressure; four independent family suites."""

from copy import deepcopy
from dataclasses import replace
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pygrc.models import grc_9_v4_owner as native
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_certification import (
    NumericalPolicy,
    numerical_policy,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_state import FrozenJSONMap

OBSERVATIONS = {}


def fixture(family):
    if family == "C_OS":
        from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture

        return native_cos_fixture()
    module = importlib.import_module(
        "tests.models.test_grc_9_v4_"
        + {"C_CI": "cci", "A_CI": "aci", "A_PC": "apc"}[family]
    )
    return (
        module.fixture()[:2]
        if family == "C_CI"
        else module.fixture(json.loads(module.RECORD.read_bytes()))
    )


def request(name, dt=2**-12, **kw):
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", name, dt, FrozenJSONMap({}), **kw
    )


class EnabledLifecycleTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select one of the four concrete family suites")
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            cls.seed, cls.expansion = fixture(cls.FAMILY)

    def owner(self):
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.LEGACY_EXACT),
        ):
            return native.GRC9V4EnabledOperation(self.seed)

    def assertChain(self, owner):
        groups = []
        for r in owner.receipts:
            if not groups or groups[-1][0].commit_id != r.commit_id:
                groups.append([])
            groups[-1].append(r)
        self.assertEqual(
            len({r.receipt_id for r in owner.receipts}), len(owner.receipts)
        )
        for i, group in enumerate(groups):
            parent = [] if not i else [groups[i - 1][0].receipt_id]
            for r in group:
                self.assertEqual(
                    list(r.identity_payload["core"]["parent_receipt_ids"]), parent
                )
                for role in ("source", "target"):
                    self.assertTrue(
                        r.identity_payload["core"][role + "_model_identity"].startswith(
                            "grc9v4-"
                        )
                    )
        return groups

    def test_mixed_event_step_reset_rebase_replay(self):
        owner = self.owner()
        initial = owner.snapshot()
        # Zero success advances the receipt head without changing scientific
        # state. The subsequent event must inherit that head, not start over.
        zero = owner.step_v4(request("zero", 0))
        self.assertTrue(zero.committed, zero.failure)
        self.assertEqual(owner.state.scientific_digest, self.seed.scientific_digest)
        event = owner.expand(self.expansion)
        self.assertTrue(event.committed, event.failure)
        target = owner.state
        event_clock = (target.inputs.step_index, target.inputs.time)
        self.assertEqual(
            event_clock, (self.seed.inputs.step_index, self.seed.inputs.time)
        )
        self.assertNotEqual(target.inputs.current, target.inputs.reset)
        step = owner.step_v4(request("target-step"))
        self.assertTrue(step.committed, step.failure)
        self.assertEqual(step.active_model_identity, owner.state.model_identity)
        self.assertNotEqual(step.active_model_identity, step.active_profile_id)
        self.assertEqual(
            step.observables["abundance_status"], "unavailable_no_admitted_definition"
        )
        self.assertIsNone(step.observables["abundance"])
        self.assertNotEqual(owner.state.inputs.current, target.inputs.current)
        if self.FAMILY.startswith("A_"):
            self.assertNotEqual(
                owner.state.inputs.current.W_A, target.inputs.current.W_A
            )
        if self.FAMILY in ("A_PC", "C_PC", "A_CI_PC", "C_CI_PC"):
            self.assertNotEqual(
                owner.state.inputs.current.Z_4, target.inputs.current.Z_4
            )
            self.assertTrue(owner._published.archives)
        clock = (owner.state.inputs.step_index, owner.state.inputs.time)
        owner.reset()
        self.assertEqual(owner.state.inputs.current, target.inputs.reset)
        self.assertEqual(
            (owner.state.inputs.step_index, owner.state.inputs.time), clock
        )
        # Evolve the restored baseline, then rebase a genuinely different
        # current value. Rebase changes no clock or current authority.
        self.assertTrue(owner.step_v4(request("after-reset")).committed)
        rebased = owner.state.inputs.current
        self.assertNotEqual(rebased, target.inputs.reset)
        rebase_clock = (owner.state.inputs.step_index, owner.state.inputs.time)
        owner.rebase()
        self.assertEqual(owner.state.inputs.reset, rebased)
        self.assertEqual(
            (owner.state.inputs.step_index, owner.state.inputs.time), rebase_clock
        )
        owner.reset()
        self.assertEqual(owner.state.inputs.current, rebased)
        groups = self.assertChain(owner)
        self.assertEqual(len(groups), 7)
        raw = owner.snapshot()
        clone = owner.duplicate()
        self.assertEqual(clone.snapshot(), raw)
        clone.step_v4(request("clone-only-zero", 0))
        self.assertEqual(owner.snapshot(), raw)
        self.assertNotEqual(clone.snapshot(), raw)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            owner.save(path)
            loaded = native.GRC9V4EnabledOperation.load(path)
            self.assertEqual(loaded.snapshot(), raw)
        owner.set_state(initial)
        self.assertEqual(owner.snapshot(), initial)
        OBSERVATIONS[self.FAMILY] = dict(
            mixed_snapshot=json.loads(raw),
            successful_groups=7,
            event_commits=1,
            positive_target_steps=2,
            both_roles_distinct=True,
            full_reset_restored=True,
            exact_replay=True,
        )

    def test_rejection_and_unexpected_failure_are_atomic(self):
        owner = self.owner()
        raw, pointer = owner.snapshot(), owner._published
        for bad in (
            request("negative", -1),
            request("external", external_source=FrozenJSONMap({"bad": 1})),
        ):
            result = owner.step_v4(bad)
            self.assertFalse(result.committed)
            self.assertEqual(
                result.failure.prestate_digest, self.seed.scientific_digest
            )
            self.assertEqual(
                result.failure.pre_lifecycle_digest,
                result.failure.post_lifecycle_digest,
            )
            self.assertEqual(result.emitted_receipts, (result.failure.failure_receipt,))
            self.assertIs(owner._published, pointer)
            self.assertEqual(owner.snapshot(), raw)
        # Missing allocation/source identity is a real event-admission failure.
        bad_event = replace(
            self.expansion,
            source_state_digest=self.expansion.source_state_digest.rsplit(":", 1)[0]
            + ":"
            + "0" * 64,
        )
        result = owner.expand(bad_event)
        self.assertFalse(result.committed)
        self.assertIs(owner._published, pointer)
        with patch.object(
            native, "_bind_result", side_effect=RuntimeError("late binding error")
        ):
            with self.assertRaisesRegex(RuntimeError, "late binding"):
                owner.step_v4(request("late", 0))
        with patch.object(
            native.generic,
            "_profile_step",
            side_effect=CertificationInconclusive("explicitly inconclusive"),
        ):
            with self.assertRaises(CertificationInconclusive):
                owner.step_v4(request("inconclusive"))
        self.assertIs(owner._published, pointer)
        self.assertEqual(owner.snapshot(), raw)

    def test_reset_and_event_late_failures_preserve_whole_publication(self):
        owner = self.owner()
        pointer, raw = owner._published, owner.snapshot()
        with patch.object(
            native.GRC9V4EnabledOperation,
            "_publish",
            side_effect=RuntimeError("late publication"),
        ):
            for operation in (
                owner.reset,
                owner.rebase,
                lambda: owner.expand(self.expansion),
            ):
                with self.assertRaisesRegex(RuntimeError, "late publication"):
                    operation()
                self.assertIs(owner._published, pointer)
                self.assertEqual(owner.snapshot(), raw)

    def test_snapshot_tampering_and_set_state_rollback(self):
        owner = self.owner()
        self.assertTrue(owner.step_v4(request("bound-zero", 0)).committed)
        raw, pointer = owner.snapshot(), owner._published
        payload = json.loads(raw)
        mutations = [
            lambda p: p["receipts"].pop(),
            lambda p: p["journal"].clear(),
            lambda p: p["state"].update(
                model_identity=self.seed.inputs.geometry.reference.profile.complete_profile_id
            ),
            lambda p: p["state"]["inputs"]["current"]["C"].__setitem__(0, 0),
            lambda p: p.update(unowned_generic_graph={}),
            lambda p: p["journal"][0].update(derived_cache={}),
        ]
        for change in mutations:
            corrupted = deepcopy(payload)
            change(corrupted)
            with self.assertRaises((ValueError, TypeError)):
                owner.set_state(canonical_json_bytes(corrupted))
            self.assertIs(owner._published, pointer)
            self.assertEqual(owner.snapshot(), raw)

    def test_native_result_binding_rejects_generic_model_and_wrong_profile(self):
        owner = self.owner()
        captured = native._bind_result
        before = owner.state
        result = owner.step_v4(request("bound", 0))
        # Use the actual successful commit and endpoints. Merely constructing
        # valid schema records is insufficient to pass native owner binding.
        from pygrc.models.grc_v4_step import CommitPayload

        commit = CommitPayload(
            "grcv4-commit-payload-v1",
            "bound",
            before.scientific_digest,
            owner.state.scientific_digest,
            tuple(r.receipt_id for r in result.emitted_receipts),
            owner.state.inputs.step_index,
            owner.state.inputs.time,
        )
        for profile, model in (
            (result.active_profile_id, result.active_profile_id),
            ("grcv4-profile-sha256:" + "0" * 64, result.active_model_identity),
        ):
            wrong = type(result)(
                result.step_index,
                result.time,
                result.events,
                result.observables,
                profile,
                model,
                result.operation_disposition,
                result.solver_disposition,
                result.committed,
                result.commit_id,
                result.failure,
                result.emitted_receipts,
            )
            with self.assertRaisesRegex(ValueError, "model/profile/clock"):
                captured(
                    wrong, request("bound", 0), before, owner.state, (), commit=commit
                )

    def test_ordinary_source_evolution_invalidates_old_event_binding(self):
        owner = self.owner()
        result = owner.step_v4(request("source-beat"))
        self.assertTrue(result.committed, result.failure)
        self.assertNotEqual(owner.state.scientific_digest, self.seed.scientific_digest)
        pointer, raw = owner._published, owner.snapshot()
        stale = owner.expand(self.expansion)
        self.assertFalse(stale.committed)
        self.assertIs(owner._published, pointer)
        self.assertEqual(owner.snapshot(), raw)
        if self.FAMILY == "C_OS":
            fresh = replace(
                self.expansion, source_state_digest=owner.state.scientific_digest
            )
        else:
            module = importlib.import_module(
                "tests.models.test_grc_9_v4_"
                + {"C_CI": "cci", "A_CI": "aci", "A_PC": "apc"}[self.FAMILY]
            )
            fresh = module.request_for(owner.state, self.expansion)
        admitted = owner.expand(fresh)
        self.assertTrue(admitted.committed, admitted.failure)
        self.assertEqual(len(self.assertChain(owner)), 2)
        OBSERVATIONS.setdefault(self.FAMILY, {})["source_beat_then_bound_event"] = True


class COSLifecycle(EnabledLifecycleTests):
    FAMILY = "C_OS"


class CCILifecycle(EnabledLifecycleTests):
    FAMILY = "C_CI"


class ACILifecycle(EnabledLifecycleTests):
    FAMILY = "A_CI"


class APCLifecycle(EnabledLifecycleTests):
    FAMILY = "A_PC"
