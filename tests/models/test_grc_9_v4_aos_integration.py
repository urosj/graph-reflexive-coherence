"""Fifth-realization integration using the same native obligations as the first four.

Only fixture providers are adapted. Native kernels, delegates, operation owners,
receipts, and independent parity comparisons execute unchanged.
"""

from copy import deepcopy
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4
from pygrc.models.grc_9_v4_legacy import LegacyDelegateBinding
from pygrc.models.grc_v4_numerics import ExactBackend, NumericalPolicy, exact_backend, numerical_policy
from tests.models import test_grc_9_v4_aos as source
from tests.models import test_grc_9_v4_owner as lifecycle
from tests.models import test_grc_9_v4_legacy as legacy
from tests.models import test_grc_9_v4_crossing as crossing
from tests.models import test_grc_9_v4 as public
import test_p995_public_conflict as conflict


def seed():
    with exact_backend(ExactBackend.FLINT), numerical_policy(NumericalPolicy.LEGACY_EXACT):
        return source.fixture(json.loads(source.RECORD.read_bytes()))


def legacy_config(family, *, prune=False):
    # The same independently specified legacy workload, bound to A_OS's own
    # exact profile/specialization; legacy dynamics have no V4 family selector.
    return legacy.config("A_CI" if family == "A_OS" else family, prune=prune)


class AOSLifecycle(lifecycle.EnabledLifecycleTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        cls.seed, cls.expansion = seed()

    def test_ordinary_source_evolution_invalidates_old_event_binding(self):
        owner = self.owner()
        result = owner.step_v4(lifecycle.request("aos-source-beat"))
        self.assertTrue(result.committed, result.failure)
        before = owner.snapshot()
        pointer = owner._published
        self.assertFalse(owner.expand(self.expansion).committed)
        self.assertIs(owner._published, pointer)
        self.assertEqual(owner.snapshot(), before)
        fresh = source.request_for(owner.state, self.expansion)
        self.assertTrue(owner.expand(fresh).committed)
        self.assertEqual(len(self.assertChain(owner)), 2)
        lifecycle.OBSERVATIONS.setdefault(self.FAMILY, {})["source_beat_then_bound_event"] = True


class AOSCompatibility(legacy.CompatibilityTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        state, _ = seed()
        cls.bound = LegacyDelegateBinding(state.inputs.geometry.reference.profile, state.specialization)
        # Keep the provider independent of the patched name, with no native
        # producer replacement.
        original = legacy.config
        cls._patcher = patch.object(legacy, "config", lambda family, **kw: original("A_CI" if family == "A_OS" else family, **kw))
        cls._patcher.start()
        cls.addClassCleanup(cls._patcher.stop)


class AOSCrossing(crossing.CrossingTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        cls.seed, _ = seed()
        cls.ref = cls.seed.inputs.geometry.reference
        cls._patcher = patch.object(crossing, "config", legacy_config)
        cls._patcher.start()
        cls.addClassCleanup(cls._patcher.stop)


class AOSPublic(public.PublicTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        state, request = seed()
        cls.cfg = dict(initial=state.to_payload(), exact_backend="flint", numerical_policy="legacy_exact_v1")
        original = public.seed
        def fixture(family):
            if family != "A_OS":
                return original(family)
            return dict(initial=state.to_payload(), journal=[dict(kind="expand", request=request.to_payload())])
        for patcher in (patch.object(public, "seed", fixture), patch.object(public, "native_config", legacy_config)):
            patcher.start()
            cls.addClassCleanup(patcher.stop)

    def test_profile_migration_and_atomic_negative_paths(self):
        target = public.GRCV4ReferenceGeometry.from_payload(
            public.configuration("A_CI")["initial"]["inputs"]["reference"]
        )
        model = GRC9V4.from_config(dict(self.cfg, targets=[target.to_payload()]))
        self.assertNotEqual(model.active_profile_id, target.profile.complete_profile_id)
        incoming = model._operation._published.owner.state.inputs
        request = public.migration_request(model, target)
        before = model.snapshot()
        pointer = model._operation._published
        with patch.object(model._operation, "_publish", side_effect=RuntimeError("late publication")):
            with self.assertRaises(RuntimeError):
                model.migrate_profile(request)
        self.assertIs(model._operation._published, pointer)
        self.assertEqual(model.snapshot(), before)
        result = model.migrate_profile(request)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(model.active_profile_id, target.profile.complete_profile_id)
        following = model._operation._published.owner.state.inputs
        self.assertEqual(following.current, incoming.current)
        self.assertEqual(following.reset, incoming.reset)
        migrated = model.snapshot()
        self.assertEqual(model.duplicate().snapshot(), migrated)
        self.assertFalse(model.migrate_profile(request).committed)
        self.assertEqual(model.snapshot(), migrated)
        self.assertFalse(model.step_v4_input(public.step_request("negative-duration", -1)).committed)
        self.assertEqual(model.snapshot(), migrated)
        tamper = deepcopy(migrated)
        tamper["owner"]["receipts"][0]["receipt_id"] = "grc-receipt-sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            model.set_state(replace(model.state, checkpoint=json.dumps(tamper).encode()))
        self.assertEqual(model.snapshot(), migrated)
        with self.assertRaises(TypeError):
            model.apply_topology_event({})
        public.EVIDENCE["profile_migration"] = dict(target_family="A_CI", committed=True,
            complete_profile_changed=True, both_histories_preserved=True, exact_replay=True,
            late_failure_atomic=True, stale_source_rejected=True, tampered_state_rejected=True,
            negative_duration_rejected=True)

    def test_aos_scope_does_not_enable_remaining_families_or_basin_policy(self):
        self.assertEqual(set(GRC9V4.execution_scope()), {"C_OS", "C_CI", "A_CI", "A_PC", "A_OS", "C_PC", "C_CI_PC"})
        model = self.model()
        self.assertFalse(model.support_status()["full_GRC9V4_conformance"])
        before = model.snapshot()
        try:
            result = model.migrate_basin_policy("aos-unselected-basin")
        except ValueError:
            pass
        else:
            self.assertFalse(result.committed)
        self.assertEqual(model.snapshot(), before)
        public.EVIDENCE["scope"] = dict(execution_families=list(GRC9V4.execution_scope()),
            A_OS_basin_migration_rejected=True, whole_publication_unchanged=True,
            full_GRC9V4_conformance=False)


class AOSConflict(conflict.ConflictTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        AOSPublic.setUpClass.__func__(cls)


if __name__ == "__main__":
    unittest.main()
