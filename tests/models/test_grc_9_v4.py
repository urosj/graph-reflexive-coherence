"""Public API integration against retained small native fixtures, four families."""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4, GRCV4
from pygrc.models.grc_9_v4 import (
    GRC9V4State,
    GRC9V4BranchRequest,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_v4 import (
    GRCV4MigrationRequest,
    MissingV4StepRequest,
)
from pygrc.models.grc_v4_migration import migration_history_policy
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_profile import resolve_profile
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_9_v4_crossing import step_request, config as native_config

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "implementation/phase-9-grcv4/tranche-9"
EVIDENCE = {}


def seed(family):
    return json.loads((BASE / f"P9-9.1b-{family}.json").read_bytes())["evidence"][
        "mixed_snapshot"
    ]


def configuration(family):
    return dict(
        initial=seed(family)["initial"],
        exact_backend="flint",
        numerical_policy="legacy_exact_v1",
    )


def branch_request(model, direction, target=None):
    if direction == "enable":
        d = dict(target_reference=target.to_payload())
    else:
        count = len(model._operation._published.reference.graph.live_edge_ids)
        cfg = native_config(
            model._operation._published.reference.profile.identity_payload.profile_family_id
        )
        del cfg["state"]
        cfg["dt"] = 2**-12
        d = dict(
            legacy_config=cfg,
            current_incoming_weights=[1.0] * count,
            reset_incoming_weights=[0.75] * count,
            current_incoming_flux=[0.01] * count,
            reset_incoming_flux=[0.02] * count,
        )
    return GRC9V4BranchRequest(
        direction + ":" + model.lifecycle_digest, model.lifecycle_digest, direction, d
    )


def migration_request(m, target):
    old = m._operation._published.owner.state
    policy = migration_history_policy(old.inputs, target)
    return GRCV4MigrationRequest.from_payload(
        dict(
            schema_version="grcv4-migration-request-v1",
            operation_id="profile-migration",
            source_state_digest=old.scientific_digest,
            target_profile_id=target.profile.complete_profile_id,
            migration_policy=dict(
                schema_version="grcv4-migration-policy-v1",
                policy_id="typed_bidirectional_profile_migration_v1",
                resource_policy_id="identity_resource_transport_v1",
                target_readmission_policy_id="full_target_fail_closed_v1",
            ),
            history_policy=policy.to_payload(),
            target_context_value={},
        )
    )


class PublicTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select a bounded family")
        cls.cfg = configuration(cls.FAMILY)

    def model(self):
        return GRC9V4.from_config(deepcopy(self.cfg))

    def test_public_construction_step_default_and_discovery(self):
        m = self.model()
        self.assertIsInstance(m, GRCV4)
        self.assertIsInstance(m.state, GRC9V4State)
        state = m.state.lifecycle
        self.assertEqual(state.family.profile_family_id, self.FAMILY)
        self.assertEqual(
            state.current, m._operation._published.owner.state.inputs.current
        )
        self.assertEqual(
            state.reset.authoritative, m._operation._published.owner.state.inputs.reset
        )
        configured = GRC9V4.from_config(m.configuration)
        self.assertEqual(
            configured.state.scientific_state_digest, m.state.scientific_state_digest
        )
        self.assertEqual(
            type(configured.configuration.profile.params_resolved.realization),
            m.describe_family(self.FAMILY).realization_parameters,
        )
        self.assertEqual(m.active_model_identity, self.cfg["initial"]["model_identity"])
        self.assertEqual(m.list_supported_model_identities(), {m.active_model_identity})
        self.assertEqual(m.list_supported_profiles(), {m.active_profile_id})
        self.assertNotIn("grc9v3_disabled_compatibility", m.list_capabilities())
        self.assertNotIn("hierarchy_tracking", m.list_capabilities())
        self.assertFalse(m.support_status()["full_GRC9V4_conformance"])
        before = m.snapshot()
        with self.assertRaises(MissingV4StepRequest):
            m.step()
        with self.assertRaises(TypeError):
            m.run(True)
        self.assertEqual(m.run(0), [])
        self.assertEqual(m.snapshot(), before)
        obs = m.compute_observables()
        self.assertEqual(m.snapshot(), before)
        self.assertEqual(obs["active_model_identity"], m.active_model_identity)
        self.assertEqual(len(obs["port_occupancy"]), 10)
        self.assertEqual(len(obs["coarse_columns"]), 10)
        self.assertIsNone(obs["hybrid_spark_candidates"])
        result = m.step_v4_input(step_request("positive"))
        self.assertTrue(result.committed, result.failure)
        self.assertIn("row_gradient", result.observables)
        self.assertEqual(
            result.to_payload()["observables"]["receipt_ledger"],
            [r.to_payload() for r in m.receipt_ledger],
        )
        self.assertEqual(
            result.observables["authoritative_current"]["consumed_by_continuity"], True
        )
        self.assertEqual(result.active_model_identity, m.active_model_identity)
        # Serialized default is an identity-bearing profile choice, never a facade dt.
        from pygrc.models import grc_9_v4_owner as n

        state = n._decode_state(self.cfg["initial"], self.FAMILY)
        ref = state.inputs.geometry.reference
        params = ref.profile.params_resolved.to_payload()
        identity = ref.profile.identity_payload.to_payload()
        default = dict(
            schema_version="grcv4-step-request-v1",
            operation_id="declared-default",
            dt=2**-12,
            context_value={},
            boundary_input=None,
            external_source=None,
        )
        params["common"]["default_step_request"] = default
        reidentify(params, identity)
        newref = replace(ref, profile=resolve_profile(params, identity))
        inputs = replace(state.inputs, geometry=newref.geometry())
        from pygrc.models.grc_v4_lifecycle import _fresh_geometry

        inputs = _fresh_geometry(inputs)
        newstate = type(state)(inputs, state.specialization)
        cfg = dict(self.cfg, initial=newstate.to_payload())
        d = GRC9V4.from_config(cfg)
        original_id = d.active_profile_id
        self.assertNotEqual(original_id, m.active_profile_id)
        out = d.run(2)
        self.assertTrue(all(r.committed for r in out))
        self.assertEqual(d.active_profile_id, original_id)
        EVIDENCE["construction"] = dict(
            active_model_identity=m.active_model_identity,
            explicit_positive_step=True,
            serialized_default_steps=2,
            capabilities=sorted(m.list_capabilities()),
            no_implicit_default=True,
        )

    def test_public_expansion_reset_rebase_and_replay(self):
        m = self.model()
        record = seed(self.FAMILY)
        action = next(a for a in record["journal"] if a["kind"] == "expand")
        self.assertTrue(m.step_v4_input(step_request("prefix", 0)).committed)
        event = m.expand(GRC9V4ExpansionRequestInput.from_payload(action["request"]))
        self.assertTrue(event.committed, event.failure)
        self.assertEqual(m.compute_observables()["num_nodes"], 17)
        self.assertEqual(m.compute_observables()["mechanical_expansions"], 1)
        self.assertTrue(m.step_v4_input(step_request("after-event")).committed)
        clock = (m.state.step_index, m.state.time)
        m.reset()
        self.assertEqual((m.state.step_index, m.state.time), clock)
        self.assertTrue(m.step_v4_input(step_request("before-rebase")).committed)
        m.rebase_reset_baseline()
        baseline = m._operation._published.owner.state.inputs.current
        m.reset()
        self.assertEqual(m._operation._published.owner.state.inputs.current, baseline)
        snap = m.snapshot()
        clone = m.duplicate()
        self.assertEqual(clone.snapshot(), snap)
        clone.step_v4_input(step_request("clone-zero", 0))
        self.assertEqual(m.snapshot(), snap)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.json"
            m.save(path)
            restored = GRC9V4.load(path)
            self.assertEqual(restored.snapshot(), snap)
        m.set_state(m.state)
        self.assertEqual(m.snapshot(), snap)
        with self.assertRaises(ValueError):
            GRC9V4.from_state(snap, {"wrong": True})
        EVIDENCE["expansion_replay"] = dict(
            final_checkpoint=snap,
            event_committed=True,
            positive_target_step=True,
            reset_rebase_clock_preserved=True,
            save_load_replay=True,
            duplicate_independent=True,
        )

    def test_public_branch_migrations_and_exact_disabled_projection(self):
        m = self.model()
        ref = m._operation._published.reference
        self.assertTrue(m.migrate_branch(branch_request(m, "disable")).committed)
        native = m._operation._published.owner.duplicate()
        self.assertEqual(m.compute_observables(), native.compute_observables())
        self.assertEqual(m.step(), native.step())
        self.assertEqual(m.compute_observables(), native.compute_observables())
        with self.assertRaises(ValueError):
            m.step_v4_input(step_request("not-silently-ignored"))
        m.rebase_reset_baseline()
        native.rebase_reset_baseline()
        m.reset()
        native.reset()
        self.assertEqual(m.compute_observables(), native.compute_observables())
        disabled = m.snapshot()
        legacy = m.state.lifecycle
        self.assertEqual(legacy.branch, "disabled_grc9v3")
        detached = legacy.delegate_snapshot
        detached.clear()
        self.assertTrue(legacy.delegate_snapshot)
        self.assertFalse(hasattr(legacy, "current"))
        self.assertEqual(GRC9V4.from_state(disabled).snapshot(), disabled)
        m.step()
        native.step()
        self.assertTrue(m.migrate_branch(branch_request(m, "enable", ref)).committed)
        r = m.step_v4_input(step_request("back-enabled"))
        self.assertTrue(r.committed, r.failure)
        self.assertEqual(m.duplicate().snapshot(), m.snapshot())
        EVIDENCE["branch_crossings"] = dict(
            both_directions=True,
            native_step_observables_equal=True,
            disabled_checkpoint=disabled,
            enabled_continuation=True,
            typed_request_not_discarded=True,
        )

    def test_profile_migration_and_atomic_negative_paths(self):
        targetfamily = {"C_OS": "C_CI", "C_CI": "C_OS", "A_CI": "A_PC", "A_PC": "A_CI"}[
            self.FAMILY
        ]
        target = GRCV4ReferenceGeometry.from_payload(
            configuration(targetfamily)["initial"]["inputs"]["reference"]
        )
        cfg = dict(self.cfg, targets=[target.to_payload()])
        m = GRC9V4.from_config(cfg)
        exclusion = None
        if self.FAMILY == "A_PC":
            before = m.snapshot()
            denied = m.migrate_profile(migration_request(m, target))
            self.assertFalse(denied.committed)
            self.assertEqual(m.snapshot(), before)
            exclusion = denied.to_payload()
            # Native PC fixture is outside this CI domain. Exercise the lawful
            # CI->PC->CI companion with unchanged kernels and CI parameters.
            pc = m._operation._published.reference
            m = GRC9V4.from_config(
                dict(
                    configuration("A_CI"),
                    targets=[pc.to_payload(), target.to_payload()],
                )
            )
            self.assertTrue(m.migrate_profile(migration_request(m, pc)).committed)
        req = migration_request(m, target)
        before = m.snapshot()
        pointer = m._operation._published
        with patch.object(
            m._operation, "_publish", side_effect=RuntimeError("late publication")
        ):
            with self.assertRaises(RuntimeError):
                m.migrate_profile(req)
        self.assertIs(m._operation._published, pointer)
        self.assertEqual(m.snapshot(), before)
        result = m.migrate_profile(req)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(m.active_profile_id, target.profile.complete_profile_id)
        migrated = m.snapshot()
        self.assertEqual(m.duplicate().snapshot(), migrated)
        self.assertFalse(m.migrate_profile(req).committed)
        self.assertEqual(m.snapshot(), migrated)
        failed = m.step_v4_input(step_request("negative-duration", -1))
        self.assertFalse(failed.committed)
        self.assertEqual(m.snapshot(), migrated)
        tamper = deepcopy(migrated)
        tamper["owner"]["receipts"][0]["receipt_id"] = "grc-receipt-sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            m.set_state(replace(m.state, checkpoint=json.dumps(tamper).encode()))
        self.assertEqual(m.snapshot(), migrated)
        with self.assertRaises(TypeError):
            m.apply_topology_event({})
        EVIDENCE["profile_migration"] = dict(
            target_family=targetfamily,
            native_fixture_exclusion=exclusion,
            source_path="CI_to_PC_companion"
            if self.FAMILY == "A_PC"
            else "retained_native_seed",
            committed=True,
            late_failure_atomic=True,
            stale_source_rejected=True,
            tampered_state_rejected=True,
            negative_duration_rejected=True,
        )


class COSPublic(PublicTests):
    FAMILY = "C_OS"


class CCIPublic(PublicTests):
    FAMILY = "C_CI"


class ACIPublic(PublicTests):
    FAMILY = "A_CI"


class APCPublic(PublicTests):
    FAMILY = "A_PC"


class BoundaryPublic(unittest.TestCase):
    def test_configuration_and_target_registry(self):
        cfg = configuration("C_OS")
        for changes in (
            {"exact_backend": "automatic"},
            {"numerical_policy": "fallback"},
            {"extra": True},
            {"targets": {}},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                GRC9V4.from_config(dict(cfg, **changes))
        with self.assertRaises(ValueError):
            GRC9V4.from_config({"initial": cfg["initial"]})
        target = cfg["initial"]["inputs"]["reference"]
        with self.assertRaises(ValueError):
            GRC9V4.from_config(dict(cfg, targets=[target, target]))
        wrong_graph = configuration("A_PC")["initial"]["inputs"]["reference"]
        with self.assertRaises(ValueError):
            GRC9V4.from_config(dict(cfg, targets=[wrong_graph]))
        m = GRC9V4.from_config(cfg)
        snap = m.snapshot()
        snap["targets"] = [wrong_graph]
        with self.assertRaises(ValueError):
            GRC9V4.from_state(snap)
        a = configuration("A_PC")
        target = deepcopy(a["initial"]["inputs"]["reference"])
        profile = target["profile"]
        profile["params_resolved"]["candidate"]["descriptor_backend_id"] = (
            "grcv4-a-descriptor-sha256:" + "0" * 64
        )
        reidentify(profile["params_resolved"], profile["identity_payload"])
        profile["complete_profile_id"] = resolve_profile(
            profile["params_resolved"], profile["identity_payload"]
        ).complete_profile_id
        with self.assertRaisesRegex(ValueError, "fixed-row"):
            GRC9V4.from_config(dict(a, targets=[target]))

    def test_publication_failure_and_typed_boundaries(self):
        m = GRC9V4.from_config(configuration("C_OS"))
        pointer = m._operation._published
        before = m.snapshot()
        with patch.object(
            m._operation, "observables", side_effect=RuntimeError("postread reporting")
        ):
            with self.assertRaisesRegex(RuntimeError, "postread"):
                m.step_v4_input(step_request("late-error", 0))
        self.assertIs(m._operation._published, pointer)
        self.assertEqual(m.snapshot(), before)
        for method in (
            m.migrate_profile,
            m.step_v4_input,
            m.step_v4,
            m.apply_topology_event,
        ):
            with self.assertRaises(TypeError):
                method({})
        for method in (m.reconstruct_topology_event, m.transport_representation):
            with self.assertRaises(ValueError):
                method({})
        with self.assertRaises(ValueError):
            GRC9V4.from_state(
                replace(m.state, lifecycle=replace(m.state.lifecycle, time=1))
            )
        self.assertEqual(m.snapshot(), before)

    def test_direct_c_to_a_never_uses_generic_initializer(self):
        # The guard is tested before native constructor/readmission, on a
        # same-topology C source and a valid fixed-row A declaration.
        from pygrc.models import grc_9_v4_api_lifecycle as public

        m = GRC9V4.from_config(configuration("A_CI"))
        target = m._operation._published.reference
        original = public.branch.enabled._OWNERS["A_CI"].STATE
        with patch.object(
            public,
            "map_migration",
            side_effect=AssertionError("generic initializer used"),
        ):
            before = m._operation._published
            state = before.owner.state
            # Replace only the immutable source record for this defensive guard;
            # this is mutation pressure, not an admitted source fixture.
            from types import SimpleNamespace

            fake = SimpleNamespace(
                inputs=SimpleNamespace(current=SimpleNamespace(W_A=None)),
                scientific_digest=state.scientific_digest,
            )
            request = migration_request(m, target)
            with patch.object(
                type(before.owner),
                "state",
                new_callable=__import__(
                    "unittest.mock", fromlist=["PropertyMock"]
                ).PropertyMock,
                return_value=fake,
            ):
                # Failure endpoints must remain the real native state.
                with patch.object(m._operation, "_failure", return_value="rejected"):
                    self.assertEqual(
                        m._operation.profile_migrate(request, target), "rejected"
                    )
        self.assertEqual(original, public.branch.enabled._OWNERS["A_CI"].STATE)

    def test_saved_selection_is_checked_before_public_execution(self):
        from examples.grcv4.catalog import Catalog, CatalogError
        from examples.grcv4.run_selection import construct

        catalog = Catalog()
        for family in ("C_OS", "C_CI", "A_CI", "A_PC"):
            with self.subTest(family=family):
                saved = catalog.selection("native-small-" + family, "source")
                m = construct(
                    saved, exact_backend="flint", numerical_policy="legacy_exact_v1"
                )
                self.assertIsInstance(m, GRC9V4)
                self.assertEqual(
                    m.active_model_identity, saved["configuration"]["model_identity"]
                )
                self.assertTrue(
                    m.step_v4_input(step_request("selection-zero", 0)).committed
                )
                changed = deepcopy(saved)
                changed["configuration"]["model_identity"] = "wrong"
                with patch.object(
                    GRC9V4,
                    "from_config",
                    side_effect=AssertionError("constructed before verification"),
                ):
                    with self.assertRaises(CatalogError):
                        construct(
                            changed,
                            exact_backend="flint",
                            numerical_policy="legacy_exact_v1",
                        )
