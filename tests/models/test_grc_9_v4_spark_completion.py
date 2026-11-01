"""Bounded native SC-3 checks; no source-to-entry trajectory is claimed here."""

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify, terminal_roster
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_codec import CompletionPolicy, digest, validate
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
from pygrc.models.grc_9_v4_spark_contracts import (
    GRC9V4SparkConfiguration,
    SparkReference,
)
from pygrc.models.grc_v4_codec import payload_identity
from pygrc.models.grc_v4_spark_cos import _rows
from pygrc.models.grc_v4_spark_state import ExactResources, QuarticSite, rational
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from p991a2_native_spark_numerics import profile, row_oracle, subjects


def configuration():
    _, graph, states, _ = subjects()
    vectors = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_text())
    declarations = {v["vector_id"]: v["payload"] for v in vectors["identity_vectors"]}
    params = declarations["IDENTITY-GRC9V4-PARAMS"]
    params["expansion"]["bond_seed"] = 1
    params["spark"].update(
        gradient_tolerance=4,
        spark_hessian_tolerance=1 / 8,
        basin_hessian_tolerance=1 / 4,
    )
    identity = declarations["IDENTITY-GRC9V4-SPECIALIZATION"]
    identity.update(
        hessian_sign=-1,
        specialization_params_hash=payload_identity("resolved_specialization", params),
    )
    spec = GRC9V4Specialization(
        FrozenJSONMap(params), FrozenJSONMap(identity)
    ).with_completion_policy(CompletionPolicy())
    p = replace(
        profile(graph), site=QuarticSite(units_id="resource_potential_site_units_v1")
    )
    return GRC9V4SparkConfiguration(
        SparkReference(graph, p), spec, states["current"], states["reset"]
    )


def request(model, chirality=1):
    vectors = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_text())
    value = vectors["grc9_expansion_vectors"][0]["request"]
    config = model.configuration
    value.update(
        schema_version="grc9v4-expansion-event-request-input-v1",
        operation_id="native-spark-event",
        source_state_digest=config.scientific_digest,
        source_graph_digest=config.reference.graph.graph_digest,
        source_node_id="v",
        target_profile_template_id=owner.profile_template(config),
        target_specialization_id=config.specialization.specialization_id,
        target_effective_degree=9,
        module_chirality=chirality,
        growth_phase=None,
        resource_distribution=[1 / 64, 31 / 32, 1 / 64],
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    return GRC9V4ExpansionRequestInput.from_payload(value)


def certificate_pair(model):
    from flint import fmpq as Q
    from flint import fmpq_mat as M

    _, _, _, domain = subjects()
    config = model.configuration
    graph = config.reference.graph
    nodes = domain["graphs"]["1"]["live_node_ids"]
    event = model._operation._published.completion.event
    mapping = {x: x for x in nodes}
    for old, new in zip(
        (
            "sc2-positive-module/core",
            *["sc2-positive-module/satellite/" + str(i) for i in (1, 2, 3)],
        ),
        event["module"],
    ):
        mapping[old] = new
    order = [
        next(i for i, x in enumerate(nodes) if mapping[x] == y)
        for y in graph.live_node_ids
    ]
    n, d = len(nodes), len(nodes) - 1
    T = M([[Q(x) for x in row] for row in domain["basis"]])
    radii = list(map(Q, domain["axis_radii"]))
    D = M([[radii[i] if i == j else 0 for j in range(d)] for i in range(d)])
    S = M([[int(i == j) if i < d else -1 for j in range(d)] for i in range(n)]) * T * D
    U = D.inv() * T.inv() * M([[int(i == j) for j in range(n)] for i in range(d)])
    S, U = (
        M([[S[i, j] for j in range(d)] for i in order]),
        M([[U[i, j] for j in order] for i in range(d)]),
    )
    center = ExactResources(
        graph, tuple(domain["center"][nodes[i]] for i in order), "21"
    )
    pair = tuple(
        CompletionCertificate.create(
            owner.kernel(config), config.policy, role, center, _rows(S), _rows(U)
        )
        for role in ("current", "reset")
    )
    return pair, center


class NativeSparkCompletionTests(unittest.TestCase):
    def test_independent_full_jacobian_at_exact_center(self):
        from flint import arb_mat, ctx

        from pygrc.models.grc_9_v4_completion_certificate import _analytic
        from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

        research = (
            ROOT / "implementation/investigations/grc9v4-constitutive-design/research"
        )
        sys.path.insert(0, str(research))
        sys.path.insert(
            0,
            str(
                research.parent
                / "evidence/spark-completion/review/constructive-candidate"
            ),
        )
        from spark_completion_os_reference import COSReference
        from spark_completion_positive import full_jacobian

        independent = COSReference(self.center.graph.to_payload(), "rational")
        values = dict(zip(self.center.graph.live_node_ids, self.center.C, strict=True))
        expected = full_jacobian(independent, independent.vector(values))
        with _ARB_CONTEXT_LOCK, ctx.workprec(512):
            _, actual, _, _ = _analytic(
                owner.kernel(self.event_model.configuration),
                arb_mat([[rational(x)] for x in self.center.C]),
            )
            self.assertTrue(
                all(
                    a.lower().fmpq() <= b <= a.upper().fmpq()
                    for a, b in zip(actual.entries(), expected.entries(), strict=True)
                )
            )

    def test_concurrent_duplicate_completion_is_one_atomic_claim(self):
        from concurrent.futures import ThreadPoolExecutor

        first = self.synthetic_window_fixture()
        first.step()
        first.step()
        second = first.duplicate()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda model: model.step(), (first, second)))
        self.assertTrue(all(r.committed for r in results))
        self.assertEqual(sum(r.local_gain for r in results), 1)
        self.assertEqual(len(first.compute_observables()["completion"]["children"]), 1)

    def test_wrong_role_pair_and_forced_requests_cannot_advance(self):
        from pygrc.models.grc_v4 import GRCV4StepRequestInput

        model = self.synthetic_window_fixture()
        before = model.snapshot()
        self.assertFalse(
            model.install_completion_certificates(
                *reversed(self.certificates)
            ).committed
        )
        request = GRCV4StepRequestInput(
            "grcv4-step-request-input-v1", "zero", 0, FrozenJSONMap({})
        )
        self.assertFalse(model.step_v4_input(request).committed)
        self.assertEqual(model.snapshot(), before)

    @classmethod
    def setUpClass(cls):
        cls.config = configuration()
        cls.source_model = GRC9V4(cls.config)
        result = cls.source_model.step()
        if not result.committed:
            raise AssertionError(result.reason)
        cls.event_model = cls.source_model.duplicate()
        result = cls.event_model.expand(request(cls.event_model))
        if not result.committed:
            raise AssertionError(result.reason)
        cls.certificates, cls.center = certificate_pair(cls.event_model)

    def synthetic_window_fixture(self):
        """Private unit seam: real map near K, real event provenance, no prefix.

        This fixture is deliberately unavailable through the public API. It
        exercises publication/window semantics without running 374 beats or
        falsely claiming that the source actually reached this center.
        """
        config = replace(
            self.event_model.configuration, current=self.center, reset=self.center
        )
        model = GRC9V4(config)
        scope = model._operation._spark_scope
        p = replace(
            model._operation._published,
            completion=replace(
                self.event_model._operation._published.completion,
                certificates=self.certificates,
            ),
        )
        scope.published = replace(
            scope.published,
            branches=((model._operation._spark_branch, p),),
            admitted=((owner.publication_id(p), p),),
        )
        return model

    def test_optional_schema_static_v3_and_round_trip(self):
        view = self.source_model.state
        self.assertEqual(view.compatibility_branch, "enabled_spark_v4")
        self.assertEqual(
            view.active_model_identity, self.source_model.active_model_identity
        )
        self.assertEqual(GRC9V4.from_state(view).state.lifecycle, view.lifecycle)
        config = GRC9V4SparkConfiguration.from_payload(self.config.to_payload())
        self.assertEqual(config, self.config)
        off = replace(
            config, specialization=config.specialization.with_completion_policy(None)
        )
        self.assertNotEqual(off.model_identity, config.model_identity)
        self.assertIsNone(off.policy)
        validate(config.reference.profile.site.to_payload())
        changed = config.to_payload()
        changed["unknown"] = 0
        with self.assertRaises(ValueError):
            GRC9V4SparkConfiguration.from_payload(changed)

    def test_full_domain_mathematics_and_exact_membership(self):
        cert = self.certificates[0]
        self.assertTrue(cert.membership(self.center)[0])
        self.assertLess(rational(cert.proof["q"]), 1)
        self.assertGreater(
            rational(cert.proof["image_margin"]),
            rational(cert.proof["full_step_error"]),
        )
        native = classify(self.center, self.config.policy)
        independent = row_oracle(self.center)["complete_basins_oracle"]
        self.assertEqual({a: sorted(b) for a, b in native.basins}, independent)
        self.assertFalse(cert.membership(self.event_model.configuration.current)[0])
        self.assertEqual(CompletionCertificate.from_payload(cert.to_payload()), cert)

    def test_certificate_tampering_full_coordinates_and_bindings(self):
        payload = self.certificates[0].to_payload()
        changes = [
            lambda x: x["proof"].update(q="0"),
            lambda x: x["operands"]["S"].pop(),
            lambda x: x["operands"]["U"][0].__setitem__(0, "0"),
            lambda x: x["operands"]["binding"].update(
                context={"evaluator": "other", "parameters": {}}
            ),
            lambda x: x["operands"]["binding"].update(state_channels=["C", "Z_4"]),
            lambda x: x["operands"]["binding"].update(charge="22"),
            lambda x: x["operands"]["binding"].update(duration="16"),
        ]
        for change in changes:
            with self.subTest(change=change):
                bad = deepcopy(payload)
                change(bad)
                with self.assertRaises((ValueError, RuntimeError, IndexError)):
                    CompletionCertificate.from_payload(bad)
        with self.assertRaises(ValueError):
            self.certificates[0].require_binding(
                owner.kernel(self.event_model.configuration),
                self.config.policy,
                "reset",
                "21",
            )

    def test_all_terminal_paths_excluded_anchors_and_ties(self):
        nodes = ("a", "b", "u", "v")
        down = {"a": set(), "b": set(), "u": {"a", "b"}, "v": {"a"}}
        basins, terminals = terminal_roster(nodes, down, {"a"})
        self.assertEqual(basins, (("a", ("a", "v")),))
        self.assertEqual(dict(terminals)["u"], ("a", "b"))
        # No edge is introduced between equal levels to select a terminal.
        self.assertEqual(dict(terminals)["b"], ("b",))

    def test_lawful_source_event_preserves_both_exact_roles(self):
        model = self.event_model
        cp = model._operation._published.completion
        self.assertEqual(model.configuration.current.charge, "21")
        self.assertEqual(model.configuration.reset.charge, "21")
        self.assertEqual(len(model.configuration.current.C), 15)
        self.assertEqual(
            cp.event["source_receipt"]["receipt_id"],
            self.source_model.receipt_ledger[-1].receipt_id,
        )
        self.assertTrue(cp.event["event_id"].startswith("grc-event-sha256:"))
        self.assertNotIn("sc2-positive-module", " ".join(cp.event["module"]))
        self.assertEqual(model.compute_observables()["completion"]["children"], [])
        bad = replace(
            request(self.source_model),
            source_state_digest=self.config.scientific_digest,
        )
        snapshot = self.source_model.snapshot()
        self.assertFalse(self.source_model.expand(bad).committed)
        self.assertEqual(snapshot, self.source_model.snapshot())

    def test_opposite_chiral_event_uses_actual_graph_certificate(self):
        mirror = self.source_model.duplicate()
        result = mirror.expand(request(mirror, -1))
        self.assertTrue(result.committed, result.reason)
        pair, center = certificate_pair(mirror)
        self.assertTrue(mirror.install_completion_certificates(*pair).committed)
        self.assertTrue(pair[0].membership(center)[0])
        self.assertEqual(
            sorted(len(b) for _, b in classify(center, self.config.policy).basins),
            [2, 3],
        )
        self.assertNotEqual(pair[0].certificate_id, self.certificates[0].certificate_id)

    def test_two_positive_beats_after_entry_and_atomic_child(self):
        model = self.synthetic_window_fixture()
        gains = []
        for _ in range(3):
            result = model.step()
            self.assertTrue(result.committed, result.reason)
            gains.append(result.local_gain)
        self.assertEqual(gains, [0, 0, 1])
        obs = model.compute_observables()["completion"]
        validate(obs["evidence"])
        self.assertEqual(len(obs["children"]), 1)
        self.assertEqual(
            obs["children"][0]["anchor"], obs["evidence"]["new_child_anchors"][0]
        )
        self.assertNotEqual(
            obs["children"][0]["anchor"], obs["evidence"]["parent"]["anchor"]
        )
        times = [r["time"] for r in obs["evidence"]["observations"]]
        self.assertEqual(rational(times[-1]) - rational(times[0]), 64)
        objects = {
            o["reference"]["sha256"]: o["value"]
            for o in model._operation._published.completion.to_payload()["objects"]
        }

        def references(value):
            if isinstance(value, dict):
                if set(value) == {"path", "sha256"}:
                    self.assertEqual(digest(objects[value["sha256"]]), value["sha256"])
                else:
                    for x in value.values():
                        references(x)
            elif isinstance(value, list):
                for x in value:
                    references(x)

        references(obs["evidence"])

    def test_duplicate_before_completion_single_shared_credit(self):
        original = self.synthetic_window_fixture()
        fork = original.duplicate()
        gains = []
        for model in (original, fork):
            for _ in range(3):
                result = model.step()
                self.assertTrue(result.committed, result.reason)
                gains.append(result.local_gain)
        self.assertEqual(sum(gains), 1)
        self.assertEqual(
            original.compute_observables()["completion"]["children"],
            fork.compute_observables()["completion"]["children"],
        )

    def test_late_failure_rolls_back_state_window_consumption_and_children(self):
        model = self.synthetic_window_fixture()
        model.step()
        model.step()
        before = model.snapshot()
        with patch.object(
            type(model._operation),
            "_publish",
            side_effect=ValueError("injected late failure"),
        ):
            result = model.step()
        self.assertFalse(result.committed)
        self.assertEqual(before, model.snapshot())
        self.assertEqual(model.step().local_gain, 1)

    def test_zero_inspection_failure_reset_rebase_and_policy_replacement(self):
        model = self.synthetic_window_fixture()
        model.step()
        before = model.snapshot()
        model.compute_observables()
        model.compute_observables()
        self.assertEqual(before, model.snapshot())
        self.assertFalse(
            owner.transact(
                model._operation, {"kind": "step", "duration": "0"}
            ).committed
        )
        self.assertEqual(before, model.snapshot())
        self.assertTrue(
            model.install_completion_certificates(*self.certificates).committed
        )
        self.assertEqual(
            model.compute_observables()["completion"]["window_observations"], 0
        )
        self.assertTrue(model.reset().committed)
        self.assertIsNone(model._operation._published.completion.event)
        self.assertTrue(model.rebase_reset_baseline().committed)
        config = model.configuration
        off = replace(
            config, specialization=config.specialization.with_completion_policy(None)
        )
        self.assertTrue(model.migrate_spark_configuration(off).committed)
        self.assertEqual(
            model.compute_observables()["completion"]["window_observations"], 0
        )

    def test_save_load_replay_and_stale_import_reconcile_occurrence(self):
        model = self.synthetic_window_fixture()
        stale = model.snapshot()
        for _ in range(3):
            model.step()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            model.save(path)
            loaded = GRC9V4.load(path)
            self.assertEqual(loaded.compute_observables(), model.compute_observables())
        restored = GRC9V4.from_state(stale)
        for _ in range(3):
            self.assertEqual(restored.step().local_gain, 0)
        self.assertEqual(
            len(restored.compute_observables()["completion"]["children"]), 1
        )
        self.assertTrue(model.reset().committed)
        self.assertEqual(
            len(model.compute_observables()["completion"]["consumed_occurrences"]), 1
        )
        claim = model.compute_observables()["completion"]["consumed_occurrences"][0]
        ref = claim["receipt"]["identity_payload"]["evidence"]["proof"]["certificate"]
        self.assertEqual(
            model.completion_evidence_object(ref), self.certificates[0].to_payload()
        )

    def test_cold_checkpoint_replay_actual_source_and_event(self):
        checkpoint = self.event_model.snapshot()
        origin = checkpoint["owner"]["origin"]
        with owner._SCOPES_LOCK:
            scope = owner._SCOPES.pop(origin)
        try:
            restored = GRC9V4.from_state(checkpoint)
            self.assertEqual(restored.snapshot(), checkpoint)
            changed = deepcopy(checkpoint)
            changed["owner"]["publication"]["configuration"]["time"] = "99"
            with self.assertRaises(ValueError):
                GRC9V4.from_state(changed)
        finally:
            owner._SCOPES[origin] = scope


if __name__ == "__main__":
    unittest.main()
