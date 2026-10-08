"""A_RG2b boundary pressure on independent coupled chains and W lifecycle.

Preparation probes the declared chart. Saved-operand checks forbid native
producers and exercise the new two-remainder targets rather than rerun old cases.
"""
import math
import unittest
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984c_arg2b_runtime as runtime
from test_p980_os_effect_witness import IV, number, vector, endpoint

r, b = runtime.r, runtime.b


class PreparationTests(unittest.TestCase):
    def test_all_graphs_exact_C_W_lineage_claims_and_frozen_scope(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        seed = r.state(manifest["expected_source"])
        with r.native_disabled():
            for case in manifest["cases"]:
                runtime.bind_case(seed, case, manifest)
                target = r.independent_target(seed, case)
                self.assertEqual(r.chart_record(target.inputs), case["independent_graph_chart"])
                cert = r.rg.RG2bCertificate(target.inputs, r.backend(target.inputs))
                self.assertEqual(cert.bounds.to_dict(), r.global_record()["native_bounds"])
                ids = target.inputs.geometry.reference.graph.live_edge_ids
                old_ids = seed.inputs.geometry.reference.graph.live_edge_ids
                self.assertTrue(all(type(n) is str for n in target.inputs.geometry.reference.graph.live_node_ids))
                for role in r.ROLES:
                    old, new = getattr(seed.inputs, role), getattr(target.inputs, role)
                    self.assertEqual(sum(map(Q, old.C)), sum(map(Q, new.C)))
                    old_w = dict(zip(old_ids, old.W_A, strict=True))
                    self.assertEqual(tuple(old_w.get(e, 1.0) for e in ids), new.W_A)
                    self.assertGreaterEqual(min(new.C), 0)
                    self.assertIsNone(new.Z_4)
        old, _ = runtime.predecessor()
        self.assertEqual(r.a_oracle.provenance(), old["claim_traces"])
        self.assertEqual(len(old["claim_traces"]["contracts"]), 11)
        self.assertIn("GTRS-RG-DEBT-C1-SECTION-REGULARITY", old["claim_traces"]["debts"])
        for kind in ("population", "shares", "budget", "source", "history"):
            changed = deepcopy(manifest)
            if kind == "population":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            elif kind == "history":
                changed["expected_source"]["inputs"]["reset"]["W_A"][0] += 0.001
            else:
                changed["expected_source"]["inputs"]["current"]["C"][0] += 0.01
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    def test_chain_storage_is_exact_and_tamper_evident(self):
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

    def test_signed_C_Y_faces_noncommuting_geometry_and_K_gates(self):
        manifest = runtime.make_manifest()
        seed = r.state(manifest["expected_source"])
        case = next(c for c in manifest["cases"] if c["request"]["target_effective_degree"] == 38)
        target = r.independent_target(seed, case)
        inputs = target.inputs
        cert = r.rg.RG2bCertificate(inputs, r.backend(inputs))
        high = r.proof.auxiliary(r.model(inputs))
        m, n = len(inputs.current.W_A), len(inputs.current.C)
        hd = np.eye(m) + np.diag([(-1)**i * 2**-12 for i in range(m)])
        gram = np.asarray(cert.graph_data.gram, dtype=float)
        self.assertGreater(np.max(np.abs(hd @ gram - gram @ hd)), 0)
        for value in (-1., math.nextafter(-1., -math.inf), math.nextafter(-1., math.inf),
                1., math.nextafter(1., -math.inf), math.nextafter(1., math.inf),
                5., math.nextafter(5., math.inf), math.nextafter(5., -math.inf), -1e100, 1e100):
            query = tuple(value if i % 2 else 2. for i in range(n)) + (value,)*m
            f, g, _ = r.signed.literal(cert, query, hd.tolist())
            expected_f, expected_s = high.increment("A", vector(query), IV.matrix(hd.tolist()))
            expected_g = high.I + number(Q(1, 2))*expected_s
            for native, reference in list(zip(f, expected_f, strict=True)) + list(zip((v for row in g for v in row), expected_g, strict=True)):
                self.assertLessEqual(Q(str(native.lo)), endpoint(reference, 1))
                self.assertGreaterEqual(Q(str(native.hi)), endpoint(reference, 0))
        for value in (0., 17/4, math.nextafter(17/4, math.inf), 9/2):
            authority = replace(inputs.current, C=(value,)*n, W_A=(1.,)*m)
            constant = replace(inputs, current=authority, reset=authority, Q_target=value*n, dt=0)
            r.rg.CandidateRG2bSection(constant, r.backend(constant))
            if value <= 17/4:
                self.assertEqual(r.rg.ProvisionalCandidateRG2bStep(constant, r.backend(constant)).next_inputs, constant)
            else:
                with self.assertRaisesRegex(ValueError, "K_minus"):
                    r.rg.ProvisionalCandidateRG2bStep(constant, r.backend(constant))
        for y, ordinary, section in ((0.624, True, True), (0.626, False, True), (-0.7, False, True), (0.7, False, True), (0.751, False, False)):
            authority = replace(inputs.current, C=(2.,)*n, W_A=(math.exp(y/512),)*m)
            constant = replace(inputs, current=authority, reset=authority, Q_target=2*n, dt=0)
            if section:
                r.rg.CandidateRG2bSection(constant, r.backend(constant))
            else:
                with self.assertRaisesRegex(ValueError, "outside K"):
                    r.rg.CandidateRG2bSection(constant, r.backend(constant))
            if ordinary:
                self.assertEqual(r.rg.ProvisionalCandidateRG2bStep(constant, r.backend(constant)).next_inputs, constant)
            else:
                with self.assertRaisesRegex(ValueError, "K_minus"):
                    r.rg.ProvisionalCandidateRG2bStep(constant, r.backend(constant))


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
        cls.after = r.following_inputs(cls.before, cls.step)

    def setUp(self):
        self.enterContext(r.native_disabled())

    def test_both_roles_new_graphs_coupled_bridges_and_W_writer_effects(self):
        self.assertEqual(self.row["predictions"], r.preflight(self.target))
        for role in r.ROLES:
            rows = [v for v in self.row["continuation"] if v["role"] == role]
            before = replace(self.target.inputs, current=getattr(self.target.inputs, role), dt=b.DT)
            first = rows[0]["step"]
            r.check_effects(before, first["read"], self.row["entry_effects"][role], numerics=True)
            self.assertEqual(r.writer_effects(before, first), self.row["writer_effects"][role])
            self.assertTrue(any(Q(v) < 0 for v in first["read"]["independent_certificate"]["zero_core_first_predecessor_upper"].values()))
            second = r.following_inputs(before, first)
            r.check_step(second, rows[1]["step"], numerics=True)
            for entry in rows:
                before = r.following_inputs(before, entry["step"])
                self.assertGreaterEqual(min(before.current.C), 0)
                self.assertGreater(min(before.current.W_A), 0)
                self.assertEqual(before.reset, self.target.inputs.reset)
            final = replace(before, dt=0)
            r.check_read(final, self.row["final_reads"][role], numerics=True)
            r.check_effects(final, self.row["final_reads"][role], self.row["final_effects"][role], numerics=True)

    def test_compaction_scope_schedule_and_exact_reuse(self):
        record, manifest = self.record, self.manifest
        raw = runtime.expand(record["execution"])
        self.assertEqual(runtime.expand(runtime.compact(raw)), raw)
        for kind in ("population", "scope", "event_vs_case", "reuse", "reset_schedule", "W_lineage"):
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
            elif kind == "W_lineage":
                value["shared"]["actual_source"]["inputs"]["reset"]["W_A"][0] += 0.001
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            changed["execution"] = runtime.compact(b.seal(value))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.status(manifest, b.seal(changed))

    @staticmethod
    def reseal(value):
        certificate = value.pop("independent_certificate")
        value = r.b.seal(value)
        certificate["selected_read_digest"] = value["record_digest"]
        value["independent_certificate"] = certificate
        return value

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
