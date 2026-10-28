"""Saved native state -> independent equations/rows -> complete classification."""

from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as Q
import itertools
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4
from pygrc.models import grc_9_v4_basin as b
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from tests.models.test_grc_9_v4 import configuration, seed, migration_request
from tests.models.test_grc_9_v4_crossing import step_request
from tests.models.test_grc_9_v4_basin import graph, synthetic
import p9101a_basin_oracle as oracle

EVIDENCE = {}


def base_config(family):
    old = GRC9V4.from_config(configuration(family)).configuration
    return replace(old, specialization=old.specialization.with_basin_policy())


def saved_state(model):
    state = model._operation._published.owner.state
    payload = deepcopy(state.to_payload())
    return type(state)(
        type(state.inputs).from_payload(payload["inputs"]),
        type(state.specialization)(**payload["specialization"]),
    )


def observe(model, label, *, retain=True):
    # Copy all authority before granting any producer access; no expectation
    # is reconstructed from a mutated producer-owned array after the call.
    saved = saved_state(model)
    before = deepcopy(saved.to_payload())
    reads = []
    native = b._read_once

    def spy(inputs, backend):
        read, point = native(inputs, backend)
        reads.append((read, point))
        return read, point

    with patch.object(b, "_read_once", side_effect=spy):
        public = model.compute_observables()
    oracle.require(len(reads) == 1, "one read for public observation")
    read, point = reads[0]
    value = public["basin_attributes"]
    projection = oracle.captured_inputs(saved, "current", value, read, point)
    oracle.require(public["basin_identity"] == projection, "public partial projection")
    current_eq = oracle.equation_check(saved, "current", point)
    reads.clear()
    with patch.object(b, "_read_once", side_effect=spy):
        snapshot = model.snapshot()
    oracle.require(len(reads) == 2, "two independent snapshot roles")
    extension = snapshot["owner"]["basin"]
    eq = []
    for role, (r, p) in zip(("current", "reset"), reads, strict=True):
        v = extension[role + "_observation"]
        oracle.captured_inputs(saved, role, v, r, p)
        eq.append(oracle.equation_check(saved, role, p))
    oracle.require(extension["current_observation"] == value, "repeated fresh capture")
    oracle.require(
        model._operation._published.owner.state.to_payload() == before,
        "observer mutated source authority",
    )
    result = dict(
        label=label,
        fixture_origin="reached_by_public_operations"
        if label.startswith("after_")
        else "supplied_native_state",
        selected_roots={
            role: oracle.root_payload(r, p)[0]
            for role, (r, p) in zip(("current", "reset"), reads, strict=True)
        },
        fixture_identity=oracle.digest(before),
        saved_native_state=before,
        observations=extension,
        expected_classification={
            role: oracle.classification(
                extension[role + "_observation"]["witness"],
                extension[role + "_observation"]["binding"]["graph_digest"],
            )
            for role in ("current", "reset")
        },
        current_equations=current_eq,
        role_equations=eq,
        public_partial_projection=projection,
    )
    if retain:
        EVIDENCE.setdefault("observations", []).append(result)
    return value, (read, point), result


class GraphOraclePressure(unittest.TestCase):
    def test_complete_reachability_oracle_and_plausible_classifier_faults(self):
        nodes = (0, 1, 2)
        pairs = tuple(itertools.permutations(nodes, 2))
        g = graph(nodes, pairs)
        for mask in range(64):
            oracle.compare_classification(
                synthetic(g, tuple(float(bool(mask & (1 << i))) for i in range(6)))
            )
        cases = (
            (("a", "s"), (("a", "s"),), (1.0,)),
            (("a", "s1", "s2"), (("a", "s1"), ("a", "s2")), (100.0, 5e-324)),
            (
                ("r", "a", "b", "s"),
                (("r", "a"), ("r", "b"), ("a", "s"), ("b", "s")),
                (1.0, 1.0, 1.0, 1.0),
            ),
            (("a", "b", "c"), (("a", "b"), ("b", "c"), ("c", "a")), (1.0, 1.0, 1.0)),
            (("x", "a", "b"), (("x", "a"), ("a", "b"), ("b", "a")), (1.0, 1.0, 1.0)),
            (("a", "b", "s"), (("a", "b"), ("b", "a"), ("b", "s")), (1.0, 1.0, 1.0)),
            (
                ("x", "a", "b", "s"),
                (("x", "s"), ("x", "a"), ("a", "b"), ("b", "a")),
                (1.0, 1.0, 1.0, 1.0),
            ),
            ((0, "0", ""), ((0, "0"), (0, "0"), ("", "")), (5e-324, -5e-324, -0.0)),
            (("a",), (("a", "a"),), (1.0,)),
            (("a", "b"), (("a", "b"),), (-0.0,)),
            ((), (), ()),
        )
        for ns, es, js in cases:
            oracle.compare_classification(synthetic(graph(ns, es), js))
        for g0, ht, gt in (((0.5, 0.5, 0.5), 0.5, 1.0), ((1.0, 2.0, 2.0), 0.5, 3.0)):
            eq = synthetic(graph((0,), ()), (), gradient=g0, ht=ht, gt=gt)
            oracle.compare_classification(eq)
            self.assertFalse(eq["nodes"][0]["seed"])
        value = synthetic(graph((0, 1, 2), ((0, 1), (0, 2))), (1.0, 5e-324))
        for field in ("components", "nodes", "regions"):
            bad = deepcopy(value)
            bad[field].pop()
            with self.assertRaisesRegex(AssertionError, "independent classification"):
                oracle.compare_classification(bad)
        zero = synthetic(
            graph(("s",), ()), (), gradient=(0.5, 0.5, 0.5), gt=1.0, ht=0.25
        )
        oracle.compare_classification(zero)
        self.assertTrue(zero["nodes"][0]["seed"])
        self.assertEqual(zero["regions"], [])
        EVIDENCE["classifier"] = dict(
            enumerated_supports=64,
            named_cases=len(cases),
            full_fields=True,
            independent_algorithm="Boolean transitive closure",
            native_occurrence_claimed=False,
        )


class NativePressure(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select family")
        cls.config = base_config(cls.FAMILY)

    def model(self):
        return GRC9V4(self.config)

    def test_saved_poststate_and_realization_specific_freshness(self):
        m = self.model()
        initial, (old_read, old_point), _ = observe(m, "initial")
        incoming = m.configuration.current
        step = m.step_v4_input(step_request("pressure-positive"))
        self.assertTrue(step.committed, step.failure)
        current, (read, point), _ = observe(m, "after_positive_step")
        self.assertNotEqual(initial["witness"]["edges"], current["witness"]["edges"])
        consumed = step.observables["authoritative_current"]["values"]
        self.assertNotEqual(
            tuple(map(float.hex, map(float, consumed))),
            tuple(e["current"] for e in current["witness"]["edges"]),
        )
        if self.FAMILY == "C_OS":
            self.assertEqual(
                point.inputs.geometry, point.inputs.geometry.reference.geometry()
            )
            from pygrc.models.grc_v4_realizations import CandidateCOSPass
            from pygrc.models.grc_v4_exact import exact_backend, ExactBackend

            with exact_backend(ExactBackend.FLINT):
                wrong = CandidateCOSPass(replace(read.inputs, dt=2**-12)).corrector
            self.assertNotEqual(wrong.current.values, point.current.values)
            with patch.object(b, "_read_once", return_value=(wrong, wrong)):
                with self.assertRaisesRegex(ValueError, "captured role inputs"):
                    m.compute_observables()
        if self.FAMILY == "A_CI":
            self.assertNotEqual(incoming.W_A, m.configuration.current.W_A)
            self.assertGreater(len(set(incoming.W_A)), 1)
            self.assertNotEqual(
                point.W_hat_A,
                m.configuration.current.W_A,
            )
        if self.FAMILY == "A_PC":
            self.assertNotEqual(incoming.Z_4, m.configuration.current.Z_4)
            self.assertNotEqual(incoming.W_A, m.configuration.current.W_A)
            self.assertNotEqual(
                tuple(x for row in read.structural_source.increment for x in row),
                m.configuration.current.Z_4,
            )
        with patch.object(b, "_read_once", return_value=(old_read, old_point)):
            with self.assertRaisesRegex(ValueError, "captured role inputs"):
                m.compute_observables()
        if self.FAMILY.endswith("CI"):
            mixed = deepcopy(current)
            mixed["binding"]["root_certificate_binding"] = initial["binding"][
                "root_certificate_binding"
            ]
            with self.assertRaisesRegex(AssertionError, "full capture binding"):
                oracle.captured_inputs(
                    m._operation._published.owner.state, "current", mixed, read, point
                )
            # Current alone is insufficient: preserve J but corrupt the last
            # geometry coordinate. The independent constitutive check must fail.
            from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge

            bad = copy(point)
            h = [list(row) for row in point.inputs.geometry.one_form_hodge.matrix]
            h[-1][-1] += 2**-8
            bad_inputs = replace(
                point.inputs,
                geometry=GRCV4Geometry(
                    point.inputs.geometry.reference,
                    OneFormHodge(
                        point.inputs.geometry.reference.graph, tuple(map(tuple, h))
                    ),
                ),
            )
            object.__setattr__(bad, "inputs", bad_inputs)
            self.assertEqual(bad.current, point.current)
            with self.assertRaisesRegex(
                AssertionError, "independent (current|geometry) equation"
            ):
                oracle.equation_check(saved_state(m), "current", bad)
        EVIDENCE["freshness"] = dict(
            incoming_and_returned_operands_differ=True,
            consumed_current_rejected=True,
            stale_read_rejected=True,
            stage="fresh_reference_restart"
            if self.FAMILY == "C_OS"
            else "fresh_selected_joint_root"
            if self.FAMILY.endswith("CI")
            else "fresh_committed_W_Z_read",
        )

    def test_native_category_occurrence_and_history_discrimination(self):
        cfg = self.config
        nodes = cfg.reference.graph.live_node_ids
        center_id = max(
            nodes,
            key=lambda n: sum(
                n in (e.tail.node_id, e.head.node_id)
                for e in cfg.reference.graph.port_graph.edges
            ),
        )
        center = nodes.index(center_id)
        leaf = next(i for i in range(len(nodes)) if i != center)
        values = list(cfg.current.C)
        values[center], values[leaf] = values[leaf], values[center]
        assigned = GRC9V4(replace(cfg, current=replace(cfg.current, C=tuple(values))))
        v, _, _ = observe(assigned, "assigned_supplied_state")
        self.assertEqual({n["status"] for n in v["nodes"]}, {"sink"})
        self.assertEqual(len(v["regions"]), 1)
        mean = float(sum(map(Q, cfg.current.C)) / len(nodes))
        quiescent = GRC9V4(
            replace(cfg, current=replace(cfg.current, C=(mean,) * len(nodes)))
        )
        z, _, _ = observe(quiescent, "quiescent_supplied_state")
        self.assertEqual({n["status"] for n in z["nodes"]}, {"quiescent"})
        thresholds = cfg.specialization.resolved["spark"]
        self.assertLessEqual(
            Q(thresholds["gradient_tolerance"]) ** 2,
            3 * Q(thresholds["basin_hessian_tolerance"]) ** 2,
        )
        # Deliberately distinct neighbors within a multi-edge row. W does not
        # cancel as it would in a one-edge or equal-neighbor row.
        varied = list(cfg.current.C)
        indices = [
            nodes.index(
                e.head.node_id if e.tail.node_id == center_id else e.tail.node_id
            )
            for e in cfg.reference.graph.port_graph.edges[:2]
        ]
        varied[indices[0]] += 2**-8
        varied[indices[1]] -= 2**-8
        history = cfg.current.W_A
        if history is not None:
            middle = 0.999 if self.FAMILY == "A_CI" else 0.9375
            history = tuple(middle + (i - 4) * 2**-13 for i in range(len(history)))
        varied_cfg = replace(
            cfg, current=replace(cfg.current, C=tuple(varied), W_A=history)
        )
        m = GRC9V4(varied_cfg)
        v, (r, p), _ = observe(m, "weighted_multi_edge_rows")
        if history is not None:
            other = replace(
                m._operation._published.owner.state,
                inputs=replace(
                    m._operation._published.owner.state.inputs,
                    current=replace(
                        m.configuration.current, W_A=tuple(reversed(history))
                    ),
                ),
            )
            self.assertNotEqual(
                oracle.row_witness(other, "current", p.current.values),
                v["witness"]["rows"],
            )
        comparisons = []
        if history is None:
            from tests.models.test_grc_v4_profile import reidentify
            from pygrc.models.grc_v4_profile import resolve_profile
            from pygrc.models.grc_v4_codec import payload_identity

            params = varied_cfg.reference.profile.params_resolved.to_payload()
            identity = varied_cfg.reference.profile.identity_payload.to_payload()
            weights = {
                e.edge_id: 1 + (i - 4) * 2**-10
                for i, e in enumerate(cfg.reference.graph.port_graph.edges)
            }
            params["candidate"]["W_C_tr"] = weights
            params["candidate"]["W_C_tr_content_digest"] = payload_identity(
                "wctr_identity_payload",
                dict(schema_version="grcv4-wctr-identity-v1", W_C_tr=weights),
            )
            params["geometry"]["reference_hodge_digest"] = payload_identity(
                "reference_hodge_identity_payload",
                dict(varied_cfg.reference.hodge_preimage, edge_weights=weights),
            )
            reidentify(params, identity)
            weighted = GRC9V4(
                replace(
                    varied_cfg,
                    reference=replace(
                        varied_cfg.reference,
                        profile=resolve_profile(params, identity),
                        edge_weights=weights,
                    ),
                )
            )
            wv, (_, wp), _ = observe(weighted, "nonuniform_C_reference_rows")
            # Same C and J, wrong uniform reference: reject the weighting, not
            # a changed current or a stale digest.
            self.assertNotEqual(
                oracle.row_witness(saved_state(m), "current", wp.current.values),
                wv["witness"]["rows"],
            )
            comparisons.append(
                dict(
                    channel="W_C_tr",
                    independently_admitted=True,
                    nonuniform_stable_reference_weighting_checked=True,
                )
            )
        if self.FAMILY == "A_PC":
            for channel, new in (
                ("Z_4", tuple(x / 2 for x in m.configuration.current.Z_4)),
                ("W_A", tuple(x * 1.001 for x in history)),
            ):
                altered = GRC9V4(
                    replace(
                        varied_cfg,
                        current=replace(varied_cfg.current, **{channel: new}),
                    )
                )
                av, _, _ = observe(altered, "matched_" + channel)
                self.assertNotEqual(v["witness"]["edges"], av["witness"]["edges"])
                self.assertNotEqual(v["observation_digest"], av["observation_digest"])
                comparisons.append(
                    dict(
                        channel=channel,
                        independently_admitted=True,
                        operands_differ=True,
                        label_change_required=False,
                    )
                )
            # One plausible, shape-correct corruption at the final carrier
            # coordinate must be visible in the independent geometry equation.
            saved = saved_state(m)
            z = list(saved.inputs.current.Z_4)
            z[-1] += 1.0
            wrong = copy(saved)
            object.__setattr__(
                wrong,
                "inputs",
                replace(
                    saved.inputs, current=replace(saved.inputs.current, Z_4=tuple(z))
                ),
            )
            with self.assertRaisesRegex(
                AssertionError, "independent geometry equation"
            ):
                oracle.equation_check(wrong, "current", p)
        EVIDENCE["occurrence"] = dict(
            supplied_native_categories=["sink", "ambiguous", "quiescent"],
            native_cycles="not observed; A positive-denominator exact fixed-geometry exclusion checked separately",
            seed_positive="excluded by declared epsilon_gradient^2 <= 3 epsilon_hessian^2",
            thresholds_unchanged=True,
            matched_comparisons=comparisons,
        )

    def test_lifecycle_roles_assignment_expansion_and_noninterference(self):
        a = self.model()
        control = self.model()
        for _ in range(3):
            a.compute_observables()
        req = step_request("same-observer-control")
        self.assertTrue(a.step_v4_input(req).committed)
        self.assertTrue(control.step_v4_input(req).committed)
        self.assertEqual(a._operation.snapshot(), control._operation.snapshot())
        before = a.snapshot()["owner"]["basin"]
        a.reset()
        reset, _, _ = observe(a, "after_reset")
        self.assertEqual(reset["witness"], before["reset_observation"]["witness"])
        self.assertNotEqual(reset["binding"], before["reset_observation"]["binding"])
        a.rebase_reset_baseline()
        rebased, _, _ = observe(a, "after_rebase")
        self.assertEqual(reset["witness"], rebased["witness"])
        a.set_state(control.state)
        observe(a, "after_different_state_assignment")
        result = a.migrate_profile(migration_request(a, a.configuration.reference))
        self.assertTrue(result.committed, result.failure)
        observe(a, "after_supported_profile_migration")
        # Only one replay per mode; the preceding suite owns the larger replay
        # matrix. These checks independently verify the resulting operands.
        for mode in ("state_only", "exact_observation"):
            restored = GRC9V4.from_state(a.snapshot(replay_mode=mode))
            observe(restored, "after_" + mode + "_load")
        expanded = self.model()
        self.assertTrue(expanded.step_v4_input(step_request("prefix", 0)).committed)
        source = expanded.snapshot()["owner"]["basin"]["current_observation"]
        request = dict(
            next(r for r in seed(self.FAMILY)["journal"] if r["kind"] == "expand")[
                "request"
            ],
            target_specialization_id=expanded.configuration.specialization.specialization_id,
            source_state_digest=expanded._operation._published.owner.state.scientific_digest,
        )
        result = expanded.expand(GRC9V4ExpansionRequestInput.from_payload(request))
        self.assertTrue(result.committed, result.failure)
        target, _, _ = observe(expanded, "after_supported_expansion")
        self.assertEqual(len(target["nodes"]), 17)
        self.assertNotEqual(
            target["binding"]["graph_digest"], source["binding"]["graph_digest"]
        )
        self.assertNotEqual(
            target["binding"]["read_identity"], source["binding"]["read_identity"]
        )
        EVIDENCE["lifecycle"] = dict(
            noninterference=True,
            distinct_role_rebinding=True,
            assignment_changed_state=True,
            expansion_target_independently_checked=True,
            thresholds_or_support_changed=False,
        )

    def test_plausible_forgery_and_failure_before_publication(self):
        m = self.model()
        v, (read, point), _ = observe(m, "fault_subject")
        saved = saved_state(m)
        forged = deepcopy(v)
        forged["witness"]["edges"][-1]["current"] = (
            -float.fromhex(forged["witness"]["edges"][-1]["current"])
        ).hex()
        forged = b.observation(forged["binding"], forged["witness"])
        # All hashes and classifications agree. Saved-state provenance must not.
        b.validate_observation(forged, saved.inputs.geometry.reference.graph.port_graph)
        oracle.compare_classification(forged)
        with self.assertRaisesRegex(AssertionError, "native edge witness"):
            oracle.captured_inputs(saved, "current", forged, read, point)
        with self.assertRaisesRegex(ValueError, "fresh captured native read"):
            b.validate_observation(
                forged,
                saved.inputs.geometry.reference.graph.port_graph,
                binding=v["binding"],
                witness=v["witness"],
            )
        row_forged = deepcopy(v)
        row_forged["witness"]["rows"][-1]["gradient"][0] = (1.0).hex()
        row_forged["witness"]["rows"][-1]["signed_hessian_diagonal"][0] = float(
            row_forged["witness"]["hessian_sign"]
        ).hex()
        row_forged = b.observation(row_forged["binding"], row_forged["witness"])
        oracle.compare_classification(row_forged)
        with self.assertRaisesRegex(AssertionError, "native row witness"):
            oracle.captured_inputs(saved, "current", row_forged, read, point)
        swapped = m.snapshot()["owner"]["basin"]["reset_observation"]
        self.assertNotEqual(swapped["witness"]["edges"], v["witness"]["edges"])
        with self.assertRaisesRegex(AssertionError, "native edge witness"):
            oracle.captured_inputs(saved, "current", swapped, read, point)
        pointer = m._operation._published
        capture = b.capture

        def fail_reset(state, role):
            out = capture(state, role)
            if role == "reset":
                raise ValueError("after current before reset publication")
            return out

        for target, kwargs in (
            ("capture", dict(side_effect=fail_reset)),
            ("_classification", dict(side_effect=ValueError("classifier failure"))),
            ("_read_once", dict(side_effect=ValueError("read failure"))),
            (
                "canonical_json_bytes",
                dict(side_effect=ValueError("serialization failure")),
            ),
        ):
            with patch.object(b, target, **kwargs):
                with self.assertRaises(ValueError):
                    m.step_v4_input(step_request("reject-" + target))
            self.assertIs(m._operation._published, pointer)

        def mutate(inputs, backend):
            inputs.current.C = (0.0,) * len(inputs.current.C)

        with patch.object(b, "_read_once", side_effect=mutate):
            with self.assertRaises(FrozenInstanceError):
                m.compute_observables()
        self.assertIs(m._operation._published, pointer)
        self.assertEqual(
            m._operation._published.owner.state.to_payload(), saved.to_payload()
        )
        EVIDENCE["faults"] = dict(
            coherent_rehashed_last_edge_forgery_rejected_by_saved_capture=True,
            coherent_last_node_forgery_rejected=True,
            role_swap_rejected=True,
            read_failure_atomic=True,
            classifier_failure_atomic=True,
            serialization_failure_atomic=True,
            reset_only_failure_atomic=True,
            producer_mutation_rejected=True,
        )


class COSPressure(NativePressure):
    FAMILY = "C_OS"


class CCIPressure(NativePressure):
    FAMILY = "C_CI"


class ACIPressure(NativePressure):
    FAMILY = "A_CI"


class APCPressure(NativePressure):
    FAMILY = "A_PC"


if __name__ == "__main__":
    unittest.main()
