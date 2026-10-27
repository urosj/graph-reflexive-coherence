"""Independent exact-delegate surfaces, not an enabled/disabled migration test."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pygrc.core import SnapshotCompatibilityError
from pygrc.models.grc_9_v3 import GRC9V3
from pygrc.models.grc_9_v4_legacy import (
    GRC9V4LegacyDelegate,
    LegacyDelegateBinding,
    LegacyExpansionTargetUndefined,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_profile import GRCV4Profile
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "implementation/phase-9-grcv4/tranche-9"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
EVIDENCE = {}


def binding(family):
    # Exact accepted complete profile and specialization; no fixture solver run.
    row = json.loads((BASE / f"P9-9.1b-{family}.json").read_bytes())
    state = row["evidence"]["mixed_snapshot"]["initial"]
    profile = GRCV4Profile.from_canonical_bytes(
        canonical_json_bytes(state["inputs"]["reference"]["profile"])
    )
    spec = state["specialization"]
    return LegacyDelegateBinding(
        profile,
        GRC9V4Specialization(
            FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
        ),
    )


def config(family, *, prune=False):
    offset = FAMILIES.index(family) / 8
    # Four vertices, four nonuniform occupied edges, distinct rows/columns.
    placements = ((0, 1, 1, 4), (1, 2, 2, 7), (2, 3, 3, 6), (0, 8, 3, 9))
    edges, port_edges, incidence = [], {}, {str(i): [] for i in range(4)}
    for i, (u, pu, v, pv) in enumerate(placements):
        edges.append(
            dict(
                edge_id=i,
                endpoint_a=dict(node_id=u, slot=pu - 1),
                endpoint_b=dict(node_id=v, slot=pv - 1),
                payload={},
            )
        )
        port_edges[str(i)] = dict(
            node_u=u,
            port_u=pu,
            node_v=v,
            port_v=pv,
            conductance=0.5 + i / 4,
            flux_uv=0.0,
        )
        incidence[str(u)].append(i)
        incidence[str(v)].append(i)
    return dict(
        dt=0.03125,
        seed=19,
        evolution=dict(
            alpha=1e-12,
            beta=1e-12,
            gamma=1e-12,
            eta=1.0,
            kappa_c=1.0,
            v0=1.0,
            rho=1.0,
            eps_tau=1e-12,
            site_potential_selection="quadratic",
            site_potential_params=dict(mu=0.0, scale=0.0),
            eps_gradient=0.01,
            eps_hessian=0.01,
            eps_spark=0.0,
        ),
        constitutive_semantic_modes=dict(
            boundary_mode="prune", hessian_backend="row_basis_diagonal"
        ),
        state=dict(
            topology=dict(
                nodes=[dict(node_id=i, payload={"label": str(i)}) for i in range(4)],
                edges=edges,
                incidence=incidence,
                port_structure={},
            ),
            nodes={
                str(i): dict(coherence=c, basin_mass=c, basin_id=i, depth=i % 2)
                for i, c in enumerate(
                    (1 + offset, 3.0, 2.0, 0.0 if prune else 4 - offset)
                )
            },
            port_edges=port_edges,
            coarse_cache={"initial": {"nested": [1, 2]}},
            hierarchy={"root": ["child"]},
        ),
    )


def equal_snapshot(test, wrapped, oracle):
    test.assertEqual(wrapped.snapshot(), oracle.snapshot())
    test.assertEqual(
        json.dumps(wrapped.snapshot(), sort_keys=True),
        json.dumps(oracle.snapshot(), sort_keys=True),
    )
    test.assertEqual(wrapped.compute_observables(), oracle.compute_observables())


class CompatibilityTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select a family")
        cls.bound = binding(cls.FAMILY)

    def pair(self, *, prune=False):
        seed = GRC9V3.from_config(config(self.FAMILY, prune=prune))
        snapshot = seed.snapshot()
        return (
            GRC9V4LegacyDelegate(self.bound, snapshot),
            GRC9V3._from_snapshot(deepcopy(snapshot), restore_reset_baseline=True),
        )

    def record(self, surface, **evidence):
        EVIDENCE[surface] = dict(
            profile_family=self.FAMILY,
            complete_profile_id=self.bound.profile.complete_profile_id,
            model_identity=self.bound.model_identity,
            contract_id=f"D10.2-EC-DISABLED-{self.FAMILY}-{surface.upper()}",
            target_spec_version="grc9v3-spec-2026-09-v1",
            outcome="passed",
            **evidence,
        )

    def test_transition(self):
        wrapped, oracle = self.pair()
        seed = wrapped.snapshot()
        observations = []
        # There must be no enabled V4 numerical path, including CI/PC writers.
        with patch(
            "pygrc.models.grc_v4_lifecycle._profile_step",
            side_effect=AssertionError("enabled kernel leaked into delegate"),
        ):
            for _ in range(4):
                actual, expected = wrapped.step(), oracle.step()
                self.assertEqual(asdict(actual), asdict(expected))
                equal_snapshot(self, wrapped, oracle)
                observations.append(asdict(actual))
        self.assertNotEqual(seed["dynamics"], wrapped.snapshot()["dynamics"])
        edge_cases = []
        for kind in ("empty", "isolated"):
            cfg = config(self.FAMILY)
            ids = [] if kind == "empty" else [0]
            cfg["state"] = dict(
                topology=dict(
                    nodes=[dict(node_id=i, payload={}) for i in ids],
                    edges=[],
                    incidence={str(i): [] for i in ids},
                    port_structure={},
                ),
                nodes={
                    str(i): dict(coherence=1.0, basin_mass=1.0, basin_id=i) for i in ids
                },
                port_edges={},
            )
            direct = GRC9V3.from_config(cfg)
            adapter = GRC9V4LegacyDelegate(self.bound, direct.snapshot())
            a, b = adapter.step(), direct.step()
            self.assertEqual(asdict(a), asdict(b))
            equal_snapshot(self, adapter, direct)
            self.assertEqual(
                adapter.snapshot(),
                GRC9V4LegacyDelegate.from_checkpoint(adapter.checkpoint()).snapshot(),
            )
            edge_cases.append(
                dict(case=kind, output=asdict(a), snapshot=adapter.snapshot())
            )
        self.record(
            "transition",
            fixture=config(self.FAMILY),
            steps=observations,
            initial_snapshot=seed,
            final_snapshot=wrapped.snapshot(),
            edge_cases=edge_cases,
            exact_transition_and_full_snapshot=True,
        )

    def test_state(self):
        wrapped, oracle = self.pair()
        wrapped.step()
        oracle.step()
        actual, expected = wrapped.get_state(), oracle.get_state()
        # Compare every dataclass field except the graph object, whose complete
        # serialization is compared separately; no selected-field equality.
        from dataclasses import fields

        names = []
        for field in fields(actual):
            if field.name != "topology":
                self.assertEqual(
                    getattr(actual, field.name),
                    getattr(expected, field.name),
                    field.name,
                )
                names.append(field.name)
        self.assertEqual(wrapped.snapshot()["topology"], oracle.snapshot()["topology"])
        before = wrapped.snapshot()
        actual.nodes[0].coherence = 123.0
        actual.hierarchy["root"].append("foreign")
        self.assertEqual(wrapped.snapshot(), before)
        frozen = wrapped.state
        with self.assertRaises(TypeError):
            frozen["metadata"]["params_hash"] = "mutated"
        self.assertFalse(hasattr(wrapped.get_state(), "W_A"))
        self.assertFalse(hasattr(wrapped.get_state(), "Z_4"))
        # State replacement follows native semantics and keeps native baseline.
        target = oracle.get_state()
        target.nodes[0].coherence += 0.125
        oracle.set_state(target)
        wrapped.set_state(target)
        target.nodes[0].coherence = 321.0
        equal_snapshot(self, wrapped, oracle)
        self.record(
            "state",
            fixture=config(self.FAMILY),
            fields_compared=names + ["topology"],
            final_snapshot=wrapped.snapshot(),
            detached_projection=True,
            immutable_owner_view=True,
            V4_history_in_delegate=False,
            enabled_to_disabled_mapping_executed=False,
        )

    def test_observable(self):
        wrapped, oracle = self.pair()
        views = []
        for stage in ("initial", "after_step", "after_reset"):
            if stage == "after_step":
                wrapped.step()
                oracle.step()
            if stage == "after_reset":
                wrapped.reset()
                oracle.reset()
            before = wrapped.snapshot()
            a = wrapped.compute_observables()
            b = oracle.compute_observables()
            self.assertEqual(a, b)
            self.assertEqual(set(a), set(b))
            self.assertEqual(wrapped.snapshot(), before)
            for forbidden in (
                "active_model_identity",
                "complete_profile_id",
                "solver_disposition",
                "receipt_ledger",
                "abundance_status",
            ):
                self.assertNotIn(forbidden, a)
            views.append(dict(stage=stage, values=deepcopy(a)))
            a["injected"] = 1
            self.assertNotIn("injected", wrapped.compute_observables())
        self.record(
            "observable",
            fixture=config(self.FAMILY),
            observations=views,
            exact_native_key_set=True,
        )

    def test_lifecycle(self):
        wrapped, oracle = self.pair()
        baseline = wrapped.snapshot()
        wrapped.step()
        oracle.step()
        different = wrapped.snapshot()
        equal_snapshot(self, wrapped, oracle)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            wrapped.save(path)
            wrapped = GRC9V4LegacyDelegate.load(self.bound, path)
            oracle = GRC9V3.load(str(path))
        equal_snapshot(self, wrapped, oracle)
        self.assertEqual(wrapped.apply_hybrid_sparks(), oracle.apply_hybrid_sparks())
        equal_snapshot(self, wrapped, oracle)
        clone = wrapped.duplicate()
        clone.step()
        self.assertNotEqual(clone.snapshot(), wrapped.snapshot())
        wrapped.reset()
        oracle.reset()
        equal_snapshot(self, wrapped, oracle)
        self.assertEqual(wrapped.snapshot(), baseline)
        self.assertEqual(wrapped.get_state().step_index, 0)  # Exact legacy clock reset.
        wrapped.step()
        oracle.step()
        wrapped.rebase_reset_baseline()
        oracle.rebase_reset_baseline()
        rebased = wrapped.snapshot()
        wrapped.step()
        oracle.step()
        wrapped.reset()
        oracle.reset()
        self.assertEqual(wrapped.snapshot(), rebased)
        equal_snapshot(self, wrapped, oracle)
        restored = GRC9V4LegacyDelegate.from_checkpoint(wrapped.checkpoint())
        equal_snapshot(
            self,
            restored,
            GRC9V3._from_snapshot(wrapped.snapshot(), restore_reset_baseline=True),
        )
        raw = wrapped.snapshot()
        pointer = wrapped._delegate
        # Late unexpected errors on the private transaction leave all authority,
        # legacy caches, event history and baseline in the old live publication.
        original_step = GRC9V3.step

        def fail_after_execution(delegate):
            original_step(delegate)
            raise RuntimeError("late native error")

        with patch.object(GRC9V3, "step", fail_after_execution):
            with self.assertRaisesRegex(RuntimeError, "late native"):
                wrapped.step()
        self.assertIs(wrapped._delegate, pointer)
        self.assertEqual(wrapped.snapshot(), raw)
        malformed = wrapped.get_state()
        malformed.port_edges.clear()
        with self.assertRaises(SnapshotCompatibilityError):
            wrapped.set_state(malformed)
        self.assertIs(wrapped._delegate, pointer)
        # Legacy's zero-resource boundary currently records prune_noop. Keep
        # that exact behavior instead of implementing a V4 repair here.
        pruning, direct = self.pair(prune=True)
        a, b = pruning.step(), direct.step()
        self.assertEqual(asdict(a), asdict(b))
        equal_snapshot(self, pruning, direct)
        self.assertEqual(
            pruning.get_state().cached_quantities["boundary_behavior_mode"],
            "prune_noop",
        )
        self.assertEqual(len(pruning.get_state().nodes), 4)
        self.record(
            "lifecycle",
            fixture=config(self.FAMILY),
            after_step=different,
            final_snapshot=wrapped.snapshot(),
            native_reset_rewinds_clock=True,
            save_load_reset_baseline_exact=True,
            rebase_exact=True,
            duplicate_detached=True,
            rollback_exact=True,
            event_call_equal=True,
            zero_resource_boundary=asdict(a),
            crossing_executed=False,
        )


class COSCompatibility(CompatibilityTests):
    FAMILY = "C_OS"


class CCICompatibility(CompatibilityTests):
    FAMILY = "C_CI"


class ACICompatibility(CompatibilityTests):
    FAMILY = "A_CI"


class APCCompatibility(CompatibilityTests):
    FAMILY = "A_PC"


class DelegateBoundaryTests(unittest.TestCase):
    def test_undefined_spark_is_atomic_without_patching_legacy(self):
        from tests.models.test_grc_9_v3_sparks import (
            _saturated_candidate_state,
            _spark_params,
        )

        seed = GRC9V3.from_state(_saturated_candidate_state(), _spark_params())
        self.assertTrue(seed.detect_hybrid_spark_candidates())
        wrapper = GRC9V4LegacyDelegate(binding("C_OS"), seed.snapshot())
        raw = wrapper.snapshot()
        pointer = wrapper._delegate
        with self.assertRaises(LegacyExpansionTargetUndefined):
            wrapper.apply_hybrid_sparks()
        self.assertEqual(raw, wrapper.snapshot())
        self.assertIs(pointer, wrapper._delegate)
        self.assertTrue(seed.detect_hybrid_spark_candidates())

    def test_wrong_branch_version_and_context_identity_reject(self):
        wrapped = GRC9V4LegacyDelegate(
            binding("A_PC"), GRC9V3.from_config(config("A_PC")).snapshot()
        )
        payload = wrapped.checkpoint()
        for field, value in [
            ("target_spec_version", "other"),
            ("active_model_identity", "wrong"),
        ]:
            bad = deepcopy(payload)
            bad["binding"][field] = value
            with self.assertRaises(ValueError):
                GRC9V4LegacyDelegate.from_checkpoint(bad)
        bad = deepcopy(payload)
        bad["enabled_state"] = {}
        with self.assertRaises(ValueError):
            GRC9V4LegacyDelegate.from_checkpoint(bad)
