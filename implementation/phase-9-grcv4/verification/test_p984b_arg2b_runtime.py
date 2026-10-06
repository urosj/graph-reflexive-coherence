"""A_RG2b pressure: signed C/Y chains, retained operands and atomic events."""

import math
import unittest
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984b_arg2b_runtime as r
from test_p980_os_effect_witness import IV, number, vector


class ARG2bPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = r.b.exact_backend(r.b.ExactBackend.FLINT)
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        cls.manifest = r.make_manifest()
        cls.shared, cls.seed = r.run_source(cls.manifest)
        cls.case = r.bind_case(cls.seed, cls.manifest["cases"][0])
        cls.request = r.b.GRC9V4ExpansionRequestInput.from_payload(cls.case["request"])
        cls.owner, outcome, cls.event = r.event_capture(cls.seed, cls.request)
        assert outcome.committed, cls.event["failure"]
        cls.target = r.check_event(cls.seed, cls.case, cls.event)
        cls.before = replace(cls.target.inputs, dt=r.b.DT)
        cls.step, cls.after = r.perform_step(cls.before)

    @staticmethod
    def reseal(value):
        certificate = value.pop("independent_certificate")
        value = r.b.seal(value)
        certificate["selected_read_digest"] = value["record_digest"]
        value["independent_certificate"] = certificate
        return value

    def test_all_graphs_preserve_typed_node_identity_and_C_W_lineage(self):
        cells = [
            i for c in self.manifest["cases"] for i in c["coverage_binding"]["cell_ids"]
        ]
        self.assertEqual(len(cells), 32)
        self.assertEqual(len(set(cells)), 32)
        for original in self.manifest["cases"]:
            case = r.bind_case(self.seed, original)
            target = r.independent_target(self.seed, case)
            self.assertEqual(
                r.chart_record(target.inputs), case["independent_graph_chart"]
            )
            cert = r.rg.RG2bCertificate(target.inputs, r.backend(target.inputs))
            self.assertEqual(cert.bounds.to_dict(), r.global_record()["native_bounds"])
            self.assertTrue(
                all(
                    type(n) is str
                    for n in target.inputs.geometry.reference.graph.live_node_ids
                )
            )
            old_ids = self.seed.inputs.geometry.reference.graph.live_edge_ids
            ids = target.inputs.geometry.reference.graph.live_edge_ids
            for role in r.ROLES:
                old, new = getattr(self.seed.inputs, role), getattr(target.inputs, role)
                self.assertEqual(sum(map(Q, old.C)), sum(map(Q, new.C)))
                old_w = dict(zip(old_ids, old.W_A, strict=True))
                self.assertEqual(tuple(old_w.get(e, 1.0) for e in ids), new.W_A)
                self.assertIsNone(new.Z_4)
        self.assertEqual(len(self.manifest["claim_traces"]["contracts"]), 11)
        self.assertIn(
            "GTRS-RG-DEBT-C1-SECTION-REGULARITY", self.manifest["claim_traces"]["debts"]
        )

    def test_all_layouts_have_independently_admitted_first_C_W_continuations(self):
        for original in self.manifest["cases"]:
            target = r.independent_target(self.seed, r.bind_case(self.seed, original))
            for role in r.ROLES:
                authority = getattr(target.inputs, role)
                c, w, truth = r.oracle.ordinary(
                    r.model(target.inputs),
                    "A",
                    np.array(authority.C),
                    np.array(authority.W_A),
                )
                r.a_oracle.chart_admitted(c, w, ordinary=True)
                self.assertGreaterEqual(min(c), 0)
                self.assertLess(truth["certificate"]["total_error"], Q(1, 2**48))

    def test_every_C_and_Y_inverse_level_is_recomputed_after_rehash(self):
        for level in range(1, 5):
            for coordinate in (0, len(self.before.current.C)):
                value = deepcopy(self.step["read"])
                value["chain"]["x"][level][coordinate] += 2**-12
                with (
                    self.subTest(level=level, coordinate=coordinate),
                    self.assertRaises(ValueError),
                ):
                    r.check_read(self.before, self.reseal(value), numerics=True)

    def test_query_terminal_depth_row_sum_and_evaluation_guards(self):
        original = self.step["read"]
        m = r.model(self.before)
        edits = [
            lambda x: x["chain"]["x"][0].__setitem__(0, 99),
            lambda x: x["chain"]["h"][-1][0].__setitem__(0, 1 + 2**-20),
            lambda x: x["chain"]["h"].pop(),
            lambda x: x["chain"]["h"].__setitem__(
                2, (np.eye(len(m.edges)) + 2**-13 * (m.mask != 0)).tolist()
            ),
            lambda x: x.__setitem__("evaluations", 147),
            lambda x: x["chain"]["x"][2].__setitem__(0, math.inf),
        ]
        for edit in edits:
            value = deepcopy(original)
            edit(value)
            with self.assertRaises((ValueError, TypeError)):
                r.check_read(self.before, self.reseal(value), numerics=True)

    def test_native_residual_and_first_predecessor_tail_cannot_be_understated(self):
        value = deepcopy(self.step["read"])
        value["chain"]["native_chain_bounds"]["state_residual"] = "0"
        with self.assertRaises(ValueError):
            r.check_read(self.before, self.reseal(value))
        value = deepcopy(self.step["read"])
        cert = value["independent_certificate"]
        cert["first_inverse_tail"] = str(
            Q(cert["first_inverse_tail"])
            * Q(r.global_record()["section_bounds"]["q_section"])
        )
        with self.assertRaisesRegex(ValueError, "first predecessor tail"):
            r.check_read(self.before, value)
        self.assertTrue(
            any(
                Q(x) < 0
                for x in self.step["read"]["independent_certificate"][
                    "zero_core_first_predecessor_upper"
                ].values()
            )
        )

    def test_input_uncertainty_is_propagated_in_scaled_log_coordinates(self):
        work = r.chain(self.step["read"])
        m = r.proof.auxiliary(r.model(self.before))
        intended = r.proof.state(
            "A", vector(self.before.current.C), vector(self.before.current.W_A)
        )
        pad = Q(1, 2**40)
        for i in range(len(self.before.current.C), len(intended)):
            intended[i] += IV.mpf([-number(pad).b, number(pad).b])
        _, cert = r.oracle.certify_chain(m, "A", work, intended)
        self.assertGreaterEqual(cert["input_error"], r.proof.SECTION_LIP * pad)
        self.assertGreater(
            cert["total_error"],
            Q(self.step["read"]["independent_certificate"]["chain"]["total_error"]),
        )
        n = len(self.before.current.C)
        intended[n] += IV.mpf([-number(Q(1, 2**30)).b, number(Q(1, 2**30)).b])
        with self.assertRaisesRegex(ValueError, "section error budget"):
            r.oracle.certify_chain(m, "A", work, intended)

    def test_signed_vectors_cannot_hide_behind_the_outer_product(self):
        value = deepcopy(self.step["read"])
        for field in ("readback", "flat"):
            value[field] = [-x for x in value[field]]
        value = self.reseal(value)
        r.check_read(self.before, value)
        with self.assertRaisesRegex(ValueError, "independent section equations"):
            r.check_read(self.before, value, numerics=True)

    def test_baseline_selected_current_and_source_are_independent_outputs(self):
        for field in ("J", "baseline", "source"):
            value = deepcopy(self.step["read"])
            if field == "source":
                value[field][0][0] += 2**-20
            else:
                value[field][0] += 2**-20
            if field == "J":
                value["read_current"] = value["J"].copy()
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_read(self.before, self.reseal(value), numerics=True)

    def test_compact_poststate_and_fresh_C_selected_J_single_W_writer(self):
        edits = [
            lambda x: x["poststate"]["C"].__setitem__(0, 99),
            lambda x: x["poststate"]["W_A"].__setitem__(0, 1),
            lambda x: x["poststate"].__setitem__("Z_4", []),
            lambda x: x["writer_targets"][0].__setitem__(
                "C", list(self.before.current.C)
            ),
            lambda x: x["writer_targets"][0].__setitem__("J", x["read"]["baseline"]),
            lambda x: x["log_writes"].append(deepcopy(x["log_writes"][0])),
            lambda x: x["diagnostics"].__setitem__("continuity_evaluations", 2),
            lambda x: x["diagnostics"].__setitem__("carrier_writes", 1),
            lambda x: x["generated"][0].__setitem__(0, 2),
            lambda x: x.__setitem__("prestate_identity", self.after.identity),
        ]
        for edit in edits:
            value = deepcopy(self.step)
            edit(value)
            with self.assertRaises(ValueError):
                r.check_step(self.before, value)
        self.assertEqual(self.after.reset, self.before.reset)

    def test_current_bridge_uses_L2_and_state_bridge_uses_Y(self):
        before = r.b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        value = deepcopy(self.shared["source_step"])
        value["read"]["J"] = [v + 8e-12 for v in value["read"]["J"]]
        independent = r.bridge(before, value)
        solver = before.geometry.reference.profile.params_resolved.solver
        tolerance = Q(solver.absolute_tolerance) + Q(solver.relative_tolerance) * Q(
            independent["current_l2_upper"]
        )
        self.assertLess(Q(8e-12), tolerance)
        self.assertGreater(Q(independent["current_l2_error"]), tolerance)
        value = deepcopy(self.shared["source_step"])
        value["poststate"]["W_A"][0] += 2**-40
        error = Q(r.bridge(before, value)["state_error"])
        self.assertGreater(error, 500 * Q(1, 2**40))

    def test_event_reference_history_and_publication_are_independent(self):
        edits = [
            lambda x: x["checkpoint"]["reference_currents"][0]["roles"]["reset"][
                "source"
            ].__setitem__(0, 99),
            lambda x: x["actual_target"]["inputs"]["current"]["W_A"].__setitem__(
                -1, 0.5
            ),
            lambda x: x["publication"][0].__setitem__("admission_pairs", 1),
            lambda x: x.__setitem__("admission_reads", x["admission_reads"][:1]),
            lambda x: x["detections"][0]["current"].__setitem__(0, 99),
            lambda x: x["checkpoint"].__setitem__("carrier_archives", []),
        ]
        for edit in edits:
            value = deepcopy(self.event)
            edit(value)
            with self.assertRaises(ValueError):
                r.check_event(self.seed, self.case, value)

    def test_late_receipt_and_reference_failures_preserve_complete_owner(self):
        for name in ("receipt", "reference"):
            owner = r.native.GRC9V4ARG2bOperation(self.seed)
            before, state = owner.checkpoint(), owner.state
            target = r.native if name == "receipt" else r.native.GRC9V4ARG2bExpansion
            attribute = (
                "make_commit_receipts"
                if name == "receipt"
                else "transfer_reference_current"
            )
            with patch.object(target, attribute, side_effect=ValueError("late fault")):
                outcome = owner.expand(self.request)
            self.assertFalse(outcome.committed)
            self.assertIs(owner.state, state)
            self.assertEqual(owner.checkpoint(), before)

    def test_reset_only_W_chart_failure_is_atomic(self):
        owner = r.native.GRC9V4ARG2bOperation(self.seed)
        before, state = owner.checkpoint(), owner.state
        real = r.rg.CandidateRG2bSection

        def corrupt(inputs, *args, **kwargs):
            if inputs.current == self.target.inputs.reset:
                inputs = replace(
                    inputs,
                    current=replace(inputs.current, W_A=(2.0, *inputs.current.W_A[1:])),
                )
            return real(inputs, *args, **kwargs)

        with patch.object(r.rg, "CandidateRG2bSection", side_effect=corrupt):
            outcome = owner.expand(self.request)
        self.assertFalse(outcome.committed)
        self.assertIs(owner.state, state)
        self.assertEqual(owner.checkpoint(), before)
        self.assertEqual(outcome.failure.stage, "target_readmission")

    def test_K_readmission_is_not_K_minus_entry_even_at_zero_dt(self):
        v = math.nextafter(4.25, math.inf)
        authority = replace(
            self.target.inputs.current, C=(v,) * len(self.target.inputs.current.C)
        )
        inputs = replace(
            self.target.inputs,
            current=authority,
            reset=authority,
            Q_target=v * len(authority.C),
            dt=0,
        )
        currents = r.native._arg2b_readmit(replace(self.target, inputs=inputs))
        self.assertTrue(all(j == 0 for flux in currents for j in flux.values))
        with self.assertRaisesRegex(ValueError, "K_minus"):
            r.rg.ProvisionalCandidateRG2bStep(inputs, r.backend(inputs))
        w = math.exp(0.7 / 512)
        authority = replace(
            self.target.inputs.current, W_A=(w,) * len(self.target.inputs.current.W_A)
        )
        inputs = replace(self.target.inputs, current=authority, reset=authority, dt=0)
        r.native._arg2b_readmit(replace(self.target, inputs=inputs))
        with self.assertRaisesRegex(ValueError, "K_minus"):
            r.rg.ProvisionalCandidateRG2bStep(inputs, r.backend(inputs))

    def test_fixed_section_and_composed_writer_controls_are_resolved(self):
        controls = r.effect_checks(self.before, self.step["read"])
        r.check_effects(self.before, self.step["read"], controls)
        self.assertEqual(len(controls), 7)
        controls = r.writer_effects(self.before, self.step)
        self.assertEqual(len(controls), 6)
        self.assertTrue(all(x["minimum_margin_ratio"] > 1 for x in controls.values()))

    def test_retained_equations_require_no_native_section_or_candidate(self):
        with r.native_disabled():
            r.check_step(self.before, self.step, numerics=True)
            r.check_event(self.seed, self.case, self.event, numerics=True)
