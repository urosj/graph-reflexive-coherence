"""C_RG2b boundary pressure: new charts, signed completion and saved-chain consumers.

Saved-operand tests disable native producers. They do not repeat trajectories.
The two preparation tests separately probe literal laws and equilibrium domains.
"""
import math
import unittest
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984c_crg2b_runtime as runtime
from test_p980_os_effect_witness import IV, number, vector, endpoint

r, b = runtime.r, runtime.b


class PreparationTests(unittest.TestCase):
    def test_frozen_graphs_and_contracts(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        seed = r.state(manifest["expected_source"])
        with ExitStack() as stack:
            for module, name in ((r.rg, "CandidateRG2bSection"), (r.rg, "ProvisionalCandidateRG2bStep"),
                    (r, "CandidateCCurrent"), (r.native, "GRC9V4CRG2bOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("producer forbidden")))
            for case in manifest["cases"]:
                runtime.bind_case(seed, case, manifest)
                target = b.independent_target({"expected_source": seed.to_payload()}, case)
                chart = r.chart_record(target)
                self.assertEqual(chart, case["independent_graph_chart"])
                self.assertEqual(chart["vertices"], chart["edges"] + 1)
                self.assertLessEqual(Q(chart["incidence_norm"]), 9)
                self.assertEqual(r.rg.RG2bCertificate(target).bounds.to_dict(), r.global_record()["native_bounds"])
                for role in r.ROLES:
                    before, after = getattr(seed.inputs, role), getattr(target, role)
                    self.assertEqual(sum(map(Q, before.C)), sum(map(Q, after.C)))
                    self.assertIsNone(after.W_A)
                    self.assertIsNone(after.Z_4)
                    self.assertGreaterEqual(min(after.C), 0)
        import verify_p983crg2b_native as claims
        old, _ = runtime.predecessor()
        self.assertEqual(claims.provenance(), old["claim_traces"])
        self.assertEqual(len(old["claim_traces"]["contracts"]), 8)
        self.assertIn("GTRS-RG-DEBT-C1-SECTION-REGULARITY", old["claim_traces"]["debts"])
        for kind in ("population", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "population":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["C"][0] += 0.01
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    def test_chain_context_storage_is_exact_and_reduces_repetition(self):
        from p984c_cci_runtime import compact as matrix_compact
        _, old = runtime.predecessor()
        case = next(c for c in old["cases"] if c["executed_case"]["request"]["target_effective_degree"] == 45)
        packed = runtime.compact(case)
        self.assertEqual(runtime.expand(packed), case)
        self.assertLess(len(b.canonical_json_bytes(packed)), len(b.canonical_json_bytes(matrix_compact(case))))
        wrong = deepcopy(packed)
        token = next(k for k, v in wrong["contexts"].items() if isinstance(v, dict) and "x" in v and "h" in v)
        wrong["contexts"][token]["x"][1][0] += 2**-12
        with self.assertRaisesRegex(ValueError, "context digest"):
            runtime.expand(wrong)

    def test_signed_faces_noncommuting_H_and_nested_physical_domains(self):
        manifest = runtime.make_manifest()
        case = next(c for c in manifest["cases"] if c["request"]["target_effective_degree"] == 38)
        inputs = b.independent_target({"expected_source": manifest["expected_source"]}, case)
        cert = r.rg.RG2bCertificate(inputs)
        high = r.proof.auxiliary(r.model(inputs))
        m = len(cert.graph_data.gram)
        hd = np.eye(m) + np.diag([(-1)**i * 2**-12 for i in range(m)])
        gram = np.asarray(cert.graph_data.gram, dtype=float)
        self.assertGreater(np.max(np.abs(hd @ gram - gram @ hd)), 0)
        for value in (-1., math.nextafter(-1., -math.inf), math.nextafter(-1., math.inf),
                5., math.nextafter(5., math.inf), math.nextafter(5., -math.inf), -1e100, 1e100):
            query = tuple(value if i % 2 else 2. for i in range(len(inputs.current.C)))
            f, g, _ = r.signed.literal(cert, query, hd.tolist())
            expected_f, expected_s = high.increment("C", vector(query), IV.matrix(hd.tolist()))
            expected_g = high.I + number(Q(1, 2))*expected_s
            for native, reference in list(zip(f, expected_f, strict=True)) + list(zip((v for row in g for v in row), expected_g, strict=True)):
                self.assertLessEqual(Q(str(native.lo)), endpoint(reference, 1))
                self.assertGreaterEqual(Q(str(native.hi)), endpoint(reference, 0))
        for value in (0., 17/4, math.nextafter(17/4, math.inf), 9/2):
            authority = replace(inputs.current, C=(value,)*len(inputs.current.C))
            constant = replace(inputs, current=authority, reset=authority, Q_target=value*len(authority.C), dt=0)
            section = r.rg.CandidateRG2bSection(constant)
            self.assertEqual(section.geometry, constant.geometry.reference.geometry())
            if value <= 17/4:
                self.assertEqual(r.rg.ProvisionalCandidateRG2bStep(constant).next_inputs, constant)
            else:
                with self.assertRaisesRegex(ValueError, "K_minus"):
                    r.rg.ProvisionalCandidateRG2bStep(constant)
        outside = replace(constant, current=replace(authority, C=(math.nextafter(9/2, math.inf),)*len(authority.C)))
        with self.assertRaisesRegex(ValueError, "outside K"):
            r.rg.CandidateRG2bSection(outside)


class SavedOperandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.record = b.read(runtime.INPUTS), b.read(runtime.RESULTS)
        cls.execution = runtime.materialize(cls.manifest, cls.record)
        cls.shared = cls.execution["shared"]
        cls.seed = r.state(cls.shared["actual_source"])
        cls.case = next(c for c in cls.manifest["cases"] if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        cls.row = next(v for v in cls.execution["cases"] if v["case_id"] == cls.case["case_id"])
        cls.event = cls.row["event"]
        cls.target = r.check_event(cls.seed, cls.case, cls.event)
        cls.before = replace(cls.target.inputs, dt=b.DT)
        cls.step = cls.row["continuation"][0]["step"]

    def setUp(self):
        for module, name in ((r.rg, "CandidateRG2bSection"), (r.rg, "ProvisionalCandidateRG2bStep"),
                (r, "CandidateCCurrent"), (r.native, "GRC9V4CRG2bOperation")):
            self.enterContext(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))

    def test_compaction_scope_schedule_and_exact_reuse(self):
        record, manifest = self.record, self.manifest
        raw = runtime.expand(record["execution"])
        self.assertEqual(runtime.expand(runtime.compact(raw)), raw)
        corrupt = deepcopy(record["execution"])
        corrupt["contexts"][next(iter(corrupt["contexts"]))] = []
        with self.assertRaisesRegex(ValueError, "context digest"):
            runtime.expand(corrupt)
        for kind in ("population", "scope", "event_vs_case", "reuse", "reset_schedule"):
            changed = deepcopy(record)
            value = runtime.expand(changed["execution"])
            if kind == "population":
                value["cases"].pop()
            elif kind == "scope":
                value["cases"][0]["user_accepted"] = True
            elif kind == "event_vs_case":
                value["cases"][0]["case_passed"] = False
            elif kind == "reset_schedule":
                value["cases"][0]["continuation"].pop()
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            changed["execution"] = runtime.compact(b.seal(value))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.status(manifest, b.seal(changed))

    def test_both_role_chain_bridges_lagged_effects_and_physical_continuations(self):
        self.assertEqual(self.row["predictions"], r.preflight(self.target))
        for role in r.ROLES:
            rows = [v for v in self.row["continuation"] if v["role"] == role]
            before = replace(self.target.inputs, current=getattr(self.target.inputs, role), dt=b.DT)
            first = rows[0]["step"]
            r.check_effects(before, first["read"], self.row["entry_effects"][role], numerics=True)
            self.assertTrue(any(Q(v) < 0 for v in first["read"]["independent_certificate"]["zero_core_first_predecessor_upper"].values()))
            second_before = b.GeometryStageInputs.from_payload(first["poststate"])
            r.check_step(second_before, rows[1]["step"], numerics=True)
            final = replace(b.GeometryStageInputs.from_payload(rows[-1]["step"]["poststate"]), dt=0)
            r.check_read(final, self.row["final_reads"][role], numerics=True)
            r.check_effects(final, self.row["final_reads"][role], self.row["final_effects"][role], numerics=True)
            for entry in rows:
                self.assertGreaterEqual(min(entry["step"]["poststate"]["current"]["C"]), 0)
                self.assertIsNone(entry["step"]["poststate"]["current"]["W_A"])
                self.assertIsNone(entry["step"]["poststate"]["current"]["Z_4"])

    @staticmethod
    def reseal(value):
        certificate = value.pop("independent_certificate")
        value = r.b.seal(value)
        certificate["selected_read_digest"] = value["record_digest"]
        value["independent_certificate"] = certificate
        return value


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



if __name__ == "__main__":
    unittest.main()
