"""Tenth-realization integration using the same native obligations as the first nine.

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
import p9_arg2b_campaign as source
from tests.models import test_grc_9_v4_owner as lifecycle
from tests.models import test_grc_9_v4_legacy as legacy
from tests.models import test_grc_9_v4_crossing as crossing
from tests.models import test_grc_9_v4 as public
import test_p995_public_conflict as conflict


def seed():
    m=source.read(source.INPUTS)
    companion=source.read(source.BASE+'D94Allocation.json');state=source.r.state(companion['source'])
    case=deepcopy(next(c for c in m['small_cases'] if c['request']['target_effective_degree']==45 and c['request']['module_chirality']==1))
    case['request'].update(target_effective_degree=52,growth_phase=1,resource_distribution=[float(source.r.Q(v)) for v in companion['selected']])
    case=source.rebind(state,case)
    return state,source.b.GRC9V4ExpansionRequestInput.from_payload(case['request'])


def legacy_config(family, *, prune=False):
    # The same independently specified legacy workload, bound to A_RG2b's own
    # exact profile/specialization; legacy dynamics have no V4 family selector.
    return legacy.config("C_OS" if family == "A_RG2b" else family, prune=prune)


class ARG2bLifecycle(lifecycle.EnabledLifecycleTests):
    FAMILY = "A_RG2b"

    @classmethod
    def setUpClass(cls):
        cls.seed, cls.expansion = seed()

    def test_ordinary_source_evolution_invalidates_old_event_binding(self):
        owner = self.owner()
        result = owner.step_v4(lifecycle.request("arg2b-source-beat"))
        self.assertTrue(result.committed, result.failure)
        before = owner.snapshot()
        pointer = owner._published
        self.assertFalse(owner.expand(self.expansion).committed)
        self.assertIs(owner._published, pointer)
        self.assertEqual(owner.snapshot(), before)
        fresh = replace(self.expansion, source_state_digest=owner.state.scientific_digest, history_policy=source.b.FrozenJSONMap(source.r.r.history_policy(owner.state)))
        self.assertTrue(owner.expand(fresh).committed)
        self.assertEqual(len(self.assertChain(owner)), 2)
        lifecycle.OBSERVATIONS.setdefault(self.FAMILY, {})["source_beat_then_bound_event"] = True


class ARG2bCompatibility(legacy.CompatibilityTests):
    FAMILY = "A_RG2b"

    @classmethod
    def setUpClass(cls):
        state, _ = seed()
        cls.bound = LegacyDelegateBinding(state.inputs.geometry.reference.profile, state.specialization)
        # Keep the provider independent of the patched name, with no native
        # producer replacement.
        original = legacy.config
        cls._patcher = patch.object(legacy, "config", lambda family, **kw: original("C_OS" if family == "A_RG2b" else family, **kw))
        cls._patcher.start()
        cls.addClassCleanup(cls._patcher.stop)


class ARG2bCrossing(crossing.CrossingTests):
    FAMILY = "A_RG2b"

    @classmethod
    def setUpClass(cls):
        cls.seed, _ = seed()
        cls.ref = cls.seed.inputs.geometry.reference
        cls._patcher = patch.object(crossing, "config", legacy_config)
        cls._patcher.start()
        cls.addClassCleanup(cls._patcher.stop)


class ARG2bPublic(public.PublicTests):
    FAMILY = "A_RG2b"

    @classmethod
    def setUpClass(cls):
        state, request = seed()
        cls.cfg = dict(initial=state.to_payload(), exact_backend="flint", numerical_policy="legacy_exact_v1")
        original = public.seed
        def fixture(family):
            if family != "A_RG2b":
                return original(family)
            return dict(initial=state.to_payload(), journal=[dict(kind="expand", request=request.to_payload())])
        for patcher in (patch.object(public, "seed", fixture), patch.object(public, "native_config", legacy_config)):
            patcher.start()
            cls.addClassCleanup(patcher.stop)

    def test_profile_migration_and_atomic_negative_paths(self):
        payload = deepcopy(public.configuration("C_OS")["initial"]["inputs"]["reference"])
        payload["graph"] = deepcopy(self.cfg["initial"]["inputs"]["reference"]["graph"])
        weights = {edge["edge_id"]: 1 for edge in payload["graph"]["edges"]}
        payload["reference_hodge"]["edge_weights"] = weights
        params = payload["profile"]["params_resolved"]
        params["candidate"]["W_C_tr"] = weights.copy()
        params["candidate"]["W_C_tr_content_digest"] = source.b.payload_identity(
            "wctr_identity_payload", dict(schema_version="grcv4-wctr-identity-v1", W_C_tr=weights))
        params["geometry"]["reference_hodge_digest"] = source.b.payload_identity(
            "reference_hodge_identity_payload", payload["reference_hodge"])
        identity = payload["profile"]["identity_payload"]
        identity["params_hash"] = source.b.payload_identity("resolved_params", params)
        payload["profile"] = source.b.resolve_profile(params, identity).to_payload()
        target = public.GRCV4ReferenceGeometry.from_payload(payload)
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
        self.assertEqual(following.current.C, incoming.current.C)
        self.assertEqual(following.reset.C, incoming.reset.C)
        self.assertIsNone(following.current.W_A)
        self.assertIsNone(following.reset.W_A)
        self.assertEqual(list(result.emitted_receipts[0].identity_payload["core"]["information_losses"]), ["candidate_history_loss"])
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
        public.EVIDENCE["profile_migration"] = dict(target_family="C_OS", committed=True,
            complete_profile_changed=True, both_resource_histories_preserved=True, candidate_loss_receipted=True, exact_replay=True,
            late_failure_atomic=True, stale_source_rejected=True, tampered_state_rejected=True,
            negative_duration_rejected=True)

    def test_arg2b_basin_requires_explicit_policy_successor(self):
        model = self.model()
        before = model.configuration
        self.assertNotIn("basin_attributes", model.compute_observables())
        result = model.migrate_basin_policy("arg2b-explicit-basin")
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(model.configuration.current, before.current)
        self.assertEqual(model.configuration.reset, before.reset)
        self.assertNotEqual(model.configuration.specialization.specialization_id,
                            before.specialization.specialization_id)
        self.assertIn("basin_attributes", model.compute_observables())
        self.assertFalse(model.support_status()["full_GRC9V4_conformance"])
        public.EVIDENCE["scope"] = dict(execution_families=list(GRC9V4.execution_scope()),
            A_RG2b_explicit_basin_successor=True, both_roles_preserved=True,
            full_GRC9V4_conformance=False)


class ARG2bConflict(conflict.ConflictTests):
    FAMILY = "A_RG2b"

    @classmethod
    def setUpClass(cls):
        ARG2bPublic.setUpClass.__func__(cls)


if __name__ == "__main__":
    unittest.main()
