"""Pressure C_RG2b graph completion, captured chains and event consumers."""

import math
import unittest
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984b_crg2b_runtime as r
from test_p980_os_effect_witness import IV, number


class CRG2bPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = r.b.exact_backend(r.b.ExactBackend.FLINT)
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        cls.manifest = r.make_manifest()
        cls.shared, cls.seed = r.run_source(cls.manifest)
        cls.case = r.bind_case(
            cls.seed,
            next(c for c in cls.manifest["cases"] if c["fixture_id"] == r.b.PINNED),
        )
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

    def test_all_sixteen_graphs_and_32_distinct_history_cells(self):
        cells = [
            i for c in self.manifest["cases"] for i in c["coverage_binding"]["cell_ids"]
        ]
        self.assertEqual(len(cells), len(set(cells)))
        self.assertEqual(len(cells), 32)
        for case in self.manifest["cases"]:
            case = r.bind_case(self.seed, case)
            target = r.b.independent_target(
                {"expected_source": self.seed.to_payload()}, case
            )
            chart = r.chart_record(target)
            self.assertEqual(chart, case["independent_graph_chart"])
            cert = r.rg.RG2bCertificate(target)
            self.assertEqual(cert.bounds.to_dict(), r.global_record()["native_bounds"])
            self.assertLessEqual(Q(chart["incidence_norm"]), 9)
            self.assertEqual(chart["vertices"], chart["edges"] + 1)
        self.assertEqual(len(self.manifest["claim_traces"]["contracts"]), 8)
        self.assertIn(
            "GTRS-RG-DEBT-C1-SECTION-REGULARITY", self.manifest["claim_traces"]["debts"]
        )

    def test_all_layout_first_continuations_are_independently_admitted(self):
        for original in self.manifest["cases"]:
            case = r.bind_case(self.seed, original)
            target = r.b.independent_target(
                {"expected_source": self.seed.to_payload()}, case
            )
            m = r.model(target)
            for role in r.ROLES:
                c = np.asarray(getattr(target, role).C)
                after, _, truth = r.oracle.ordinary(m, "C", c)
                self.assertGreaterEqual(min(after), 0, (case["case_id"], role))
                self.assertLessEqual(max(after), 4.25)
                self.assertLess(truth["certificate"]["total_error"], Q(1, 2**48))

    def test_every_inverse_level_is_recomputed_after_rehash(self):
        for level in range(1, 7):
            value = deepcopy(self.step["read"])
            value["chain"]["x"][level][0] += 2**-12
            value = self.reseal(value)
            with self.subTest(level=level), self.assertRaises(ValueError):
                r.check_read(self.before, value, numerics=True)

    def test_terminal_query_depth_and_row_sum_are_distinct_guards(self):
        original = self.step["read"]
        m = r.model(self.before)
        mutations = []
        x = deepcopy(original)
        x["chain"]["x"][0][0] += 1
        mutations.append(x)
        x = deepcopy(original)
        x["chain"]["h"][-1][0][0] += 2**-20
        mutations.append(x)
        x = deepcopy(original)
        x["chain"]["h"].pop()
        mutations.append(x)
        x = deepcopy(original)
        x["chain"]["h"][2] = (np.eye(len(m.edges)) + 2**-13 * (m.mask != 0)).tolist()
        mutations.append(x)
        x = deepcopy(original)
        x["evaluations"] = 221
        mutations.append(x)
        for x in mutations:
            with self.assertRaises(ValueError):
                r.check_read(self.before, self.reseal(x), numerics=True)

    def test_false_residual_and_wrong_first_inverse_tail_fail_closed(self):
        original = self.step["read"]
        x = deepcopy(original)
        x["chain"]["native_chain_bounds"]["state_residual"] = "0"
        with self.assertRaises(ValueError):
            r.check_read(self.before, self.reseal(x))
        x = deepcopy(original)
        cert = x["independent_certificate"]
        cert["first_inverse_tail"] = str(
            Q(cert["first_inverse_tail"])
            * Q(r.global_record()["section_bounds"]["q_section"])
        )
        with self.assertRaisesRegex(ValueError, "first predecessor tail"):
            r.check_read(self.before, x)
        self.assertTrue(
            any(
                Q(v) < 0
                for v in original["independent_certificate"][
                    "zero_core_first_predecessor_upper"
                ].values()
            )
        )
        self.assertGreater(
            Q(original["independent_certificate"]["first_inverse_tail"]), 0
        )

    def test_signed_vectors_cannot_hide_behind_an_unchanged_outer_product(self):
        x = deepcopy(self.step["read"])
        x["readback"] = [-v for v in x["readback"]]
        x["flat"] = [-v for v in x["flat"]]
        x = self.reseal(x)
        r.check_read(self.before, x)
        with self.assertRaisesRegex(ValueError, "independent section equations"):
            r.check_read(self.before, x, numerics=True)

    def test_selected_current_baseline_and_source_are_independent_outputs(self):
        for name in ("J", "baseline", "source"):
            x = deepcopy(self.step["read"])
            if name == "source":
                x[name][0][0] += 2**-20
            else:
                x[name][0] += 2**-20
            if name == "J":
                x["read_current"] = x["J"].copy()
            with self.subTest(name=name), self.assertRaises(ValueError):
                r.check_read(self.before, self.reseal(x), numerics=True)

    def test_chain_input_error_is_propagated_not_confused_with_point_error(self):
        read = self.step["read"]
        work = r.chain(read)
        m = r.proof.auxiliary(r.model(self.before))
        pad = Q(1, 2**40)
        intended = IV.matrix(
            [
                IV.mpf([(number(c) - number(pad)).a, (number(c) + number(pad)).b])
                for c in self.before.current.C
            ]
        )
        _, cert = r.oracle.certify_chain(m, "C", work, intended)
        self.assertGreaterEqual(cert["input_error"], r.proof.SECTION_LIP * pad)
        self.assertGreater(
            cert["total_error"],
            Q(read["independent_certificate"]["chain"]["total_error"]),
        )
        wide = IV.matrix(
            [
                IV.mpf(
                    [
                        (number(c) - number(Q(1, 2**30))).a,
                        (number(c) + number(Q(1, 2**30))).b,
                    ]
                )
                for c in self.before.current.C
            ]
        )
        with self.assertRaisesRegex(ValueError, "section error budget"):
            r.oracle.certify_chain(m, "C", work, wide)

    def test_resource_writer_clock_and_reset_have_exact_consumption(self):
        original = self.step
        for mutate in (
            lambda x: x["poststate"]["current"]["C"].__setitem__(
                0, x["poststate"]["current"]["C"][0] + 2**-20
            ),
            lambda x: x["poststate"].__setitem__(
                "step_index", x["poststate"]["step_index"] + 1
            ),
            lambda x: x["diagnostics"].__setitem__("continuity_evaluations", 2),
            lambda x: x["diagnostics"].__setitem__("carrier_writes", 1),
            lambda x: x["generated"][0].__setitem__(0, x["generated"][0][0] + 2**-20),
        ):
            x = deepcopy(original)
            mutate(x)
            with self.assertRaises(ValueError):
                r.check_step(self.before, x)
        self.assertEqual(original["poststate"]["reset"], original["prestate"]["reset"])
        self.assertIsNone(original["poststate"]["current"]["W_A"])
        self.assertIsNone(original["poststate"]["current"]["Z_4"])

    def test_current_bridge_uses_euclidean_not_max_coordinate_error(self):
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

    def test_event_transfer_reference_and_history_channels_are_separate(self):
        for mutate in (
            lambda x: x["checkpoint"]["reference_currents"][0]["roles"]["reset"][
                "source"
            ].__setitem__(0, 99),
            lambda x: x["actual_target"]["inputs"]["current"]["C"].__setitem__(0, 1),
            lambda x: x["publication"][0].__setitem__("admission_pairs", 1),
            lambda x: x.__setitem__("admission_reads", x["admission_reads"][:1]),
            lambda x: x["detections"][0]["current"].__setitem__(0, 99),
            lambda x: x["checkpoint"].__setitem__("carrier_archives", []),
        ):
            x = deepcopy(self.event)
            mutate(x)
            with self.assertRaises(ValueError):
                r.check_event(self.seed, self.case, x)
        for role in r.ROLES:
            source = getattr(self.seed.inputs, role)
            target = getattr(self.target.inputs, role)
            self.assertEqual(sum(map(Q, source.C)), sum(map(Q, target.C)))

    def test_late_receipt_and_reference_failure_preserve_complete_owner(self):
        for name in ("receipt", "reference"):
            owner = r.native.GRC9V4CRG2bOperation(self.seed)
            before = owner.checkpoint()
            state = owner.state
            target = r.native if name == "receipt" else r.native.GRC9V4CRG2bExpansion
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

    def test_reset_only_K_failure_cannot_publish_current_success(self):
        current = self.seed.inputs.reset.C
        delta = math.nextafter(4.5, math.inf) - current[0]
        bad = replace(
            self.seed.inputs.reset,
            C=(math.nextafter(4.5, math.inf), current[1] - delta, *current[2:]),
        )
        seed = replace(self.seed, inputs=replace(self.seed.inputs, reset=bad))
        # Invalid initial reset authority is rejected before an owner exists.
        with self.assertRaisesRegex(ValueError, "outside K"):
            r.native.GRC9V4CRG2bOperation(seed)
        owner = r.native.GRC9V4CRG2bOperation(self.seed)
        checkpoint, state = owner.checkpoint(), owner.state
        real = r.rg.CandidateRG2bSection

        def reset_fault(inputs, *args, **kwargs):
            if inputs.current == self.target.inputs.reset:
                c = inputs.current.C
                delta = math.nextafter(4.5, math.inf) - c[0]
                outside = replace(
                    inputs.current,
                    C=(math.nextafter(4.5, math.inf), c[1] - delta, *c[2:]),
                )
                inputs = replace(inputs, current=outside)
            return real(inputs, *args, **kwargs)

        # An actual K check rejects a corrupted target reset section after the
        # valid target current has admitted. This is a consumer-fault probe.
        with patch.object(r.rg, "CandidateRG2bSection", side_effect=reset_fault):
            outcome = owner.expand(self.request)
        self.assertFalse(outcome.committed)
        self.assertIs(owner.state, state)
        self.assertEqual(owner.checkpoint(), checkpoint)
        self.assertEqual(outcome.failure.stage, "target_readmission")
        self.assertIn("outside K", outcome.failure.message)

    def test_K_readmission_is_not_K_minus_ordinary_entry_even_at_zero_dt(self):
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
        admitted = replace(self.target, inputs=inputs)
        currents = r.native._crg2b_readmit(admitted)
        self.assertTrue(all(j == 0 for flux in currents for j in flux.values))
        with self.assertRaisesRegex(ValueError, "K_minus"):
            r.rg.ProvisionalCandidateRG2bStep(inputs)

    def test_fixed_section_controls_and_instantaneous_image_are_resolved(self):
        for role, key in (("current", "read"), ("reset", "reset_read")):
            before = replace(self.before, current=getattr(self.before, role))
            controls = r.effect_checks(before, self.step[key])
            r.check_effects(before, self.step[key], controls)
            self.assertEqual(len(controls), 6)

    def test_retained_equations_require_no_native_section_or_candidate(self):
        forbidden = AssertionError("native execution forbidden")
        with (
            patch.object(r.rg, "CandidateRG2bSection", side_effect=forbidden),
            patch.object(r.rg, "ProvisionalCandidateRG2bStep", side_effect=forbidden),
            patch.object(r.signed, "propose", side_effect=forbidden),
            patch.object(r.signed, "certify_chain", side_effect=forbidden),
            patch.object(r.signed, "literal", side_effect=forbidden),
            patch.object(r, "CandidateCCurrent", side_effect=forbidden),
        ):
            r.check_step(self.before, self.step, numerics=True)
            r.check_event(self.seed, self.case, self.event, numerics=True)
