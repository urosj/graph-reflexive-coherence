"""A_CI_PC boundary pressure at actual saved operands; no duplicate native campaign."""

from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np
import p984c_acipc_runtime as runtime

r, b = runtime.r, runtime.b


class ACIPCBoundaryTests(unittest.TestCase):
    def setUp(self):
        # Retained pressure must not silently reproduce the native campaign.
        for module, name in ((r, "CandidateCIRoot"), (r, "ProvisionalCandidateCIStep"),
                (r.native, "GRC9V4ACIPCOperation")):
            self.enterContext(patch.object(module, name,
                side_effect=AssertionError("native producer forbidden")))

    def test_contract_targets_and_whole_chart(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        seed = r.state(manifest["expected_source"])
        self.assertNotEqual(seed.inputs.current.Z_4, seed.inputs.reset.Z_4)
        self.assertNotEqual(seed.inputs.current.W_A, seed.inputs.reset.W_A)
        with ExitStack() as stack:
            for module, name in ((r, "CandidateCIRoot"), (r, "ProvisionalCandidateCIStep"), (r.native, "GRC9V4ACIPCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))
            for case in manifest["cases"]:
                runtime.bind_case(seed, case, manifest)
                target = r.independent_target(seed, case)
                self.assertEqual(case["independent_whole_chart"], r.oracle.whole_chart(case["oracle"]["target_graph"]))
                for role in r.ROLES:
                    old, new = getattr(seed.inputs, role), getattr(target.inputs, role)
                    histories = dict(zip(seed.inputs.geometry.reference.graph.live_edge_ids, old.W_A, strict=True))
                    expected = tuple(histories.get(e, seed.specialization.resolved["expansion"]["bond_seed"])
                        for e in target.inputs.geometry.reference.graph.live_edge_ids)
                    self.assertEqual(new.W_A, expected)
                    self.assertFalse(any(new.Z_4))
                    self.assertTrue(r.charge_record(seed.inputs, new))
                    self.assertGreaterEqual(min(new.C), 0)
        graph = manifest["cases"][0]["oracle"]["target_graph"]
        with self.assertRaisesRegex(ValueError, "B_2R"):
            r.oracle.whole_chart(graph, geometry_radius=r.Q(np.nextafter(r.oracle.ROOT_RADIUS, 0)))
        with self.assertRaisesRegex(ValueError, "strict uniform source envelope slack"):
            r.oracle.whole_chart(graph, radius=r.Q(1, 10**30))
        target = r.independent_target(seed, manifest["cases"][0]).inputs.current
        z = np.zeros((len(graph["edges"]),)*2)
        for sign in (-1, 1):
            z[0, 0] = sign*r.oracle.RADIUS
            self.assertEqual(r.oracle.carrier_admitted(graph, z), r.oracle.RADIUS**2)
            z[0, 0] = sign*np.nextafter(float(r.oracle.RADIUS), np.inf)
            with self.assertRaisesRegex(ValueError, "Frobenius ball"):
                r.oracle.carrier_admitted(graph, z)
        for bad in (np.nan, np.inf):
            z[0, 0] = bad
            with self.assertRaisesRegex(ValueError, "finite"):
                r.oracle.carrier_admitted(graph, z)
        z[0, 0] = 0
        for bad in (-1, np.nan, np.inf, np.nextafter(16.0, np.inf)):
            c = list(target.C)
            c[0] = bad
            with self.subTest(resource=bad), self.assertRaisesRegex(ValueError, "resource chart"):
                r.oracle.check_step(graph, c, target.W_A, z, {})
        for bad in (0, np.nan, np.inf, np.nextafter(r.oracle.W_MIN, 0),
                np.nextafter(r.oracle.W_MAX, np.inf)):
            w = list(target.W_A)
            w[0] = bad
            with self.subTest(weight=bad), self.assertRaisesRegex(ValueError, "W chart"):
                r.oracle.check_step(graph, target.C, w, z, {})
        for kind in ("population", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "population":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["W_A"][0] += 0.01
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    @classmethod
    def retained(cls):
        manifest, record = b.read(runtime.INPUTS), b.read(runtime.RESULTS)
        return manifest, record, runtime.materialize(manifest, record)

    def test_compaction_roster_scope_and_exact_reuse(self):
        manifest, record, execution = self.retained()
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
        for row in execution["cases"]:
            self.assertTrue(all(min(v["C"]) >= 0 and min(v["W_A"]) > 0
                for predictions in row["predictions"].values() for v in predictions))

    def test_both_writers_history_and_event_pressure(self):
        manifest, _, execution = self.retained()
        i = next(i for i, c in enumerate(manifest["cases"]) if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        row, case = execution["cases"][i], manifest["cases"][i]
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        self.assertEqual(row["predictions"], r.preflight(r.independent_target(seed, case)))
        for role in r.ROLES:
            first = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            entry = r.role_input(target.inputs, role, dt=b.DT)
            self.assertFalse(any(entry.current.Z_4))
            self.assertNotEqual(first["read"]["H"], np.eye(len(first["read"]["J"])).tolist())
            self.assertEqual(row["entry_effects"][role], r.writer_effects(entry, first))
            before = b.GeometryStageInputs.from_payload(first["poststate"])
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 2)
            self.assertTrue(any(before.current.Z_4))
            self.assertNotEqual(entry.current.W_A, before.current.W_A)
            r.check_step(before, step, numerics=True)
            final = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 10)
            self.assertEqual(final["restart"], row["final_reads"][role])
            last = replace(b.GeometryStageInputs.from_payload(final["poststate"]), dt=0)
            self.assertEqual(row["final_effects"][role], r.effect_checks(last, row["final_reads"][role]))
            for kind in ("double_z", "post_source", "wrong_z", "wrong_current", "stale_restart", "reset_overwrite", "double_w", "stale_c", "wrong_w", "whole_chart"):
                value = deepcopy(step)
                if kind == "double_z":
                    value["carrier_calls"] *= 2
                elif kind == "post_source":
                    value["carrier_calls"][0]["source"] = [x for v in value["restart"]["source"] for x in v]
                elif kind == "wrong_z":
                    value["carrier_calls"][0]["Z"] = list(before.reset.Z_4)
                elif kind == "wrong_current":
                    value["selection_current"] = value["read"]["baseline"]
                elif kind == "stale_restart":
                    value["restart"] = value["read"]
                elif kind == "reset_overwrite":
                    value["poststate"]["reset"] = value["poststate"]["current"]
                elif kind == "double_w":
                    value["log_writes"] *= 2
                elif kind == "stale_c":
                    value["writer_targets"][0]["C"] = list(before.current.C)
                elif kind == "wrong_w":
                    value["log_writes"][0]["old"] = list(before.reset.W_A)
                else:
                    value["read"]["bounds"]["carrier_radius"] = "1"
                    raw = {k: v for k, v in value["read"].items() if k != "independent_certificate"}
                    value["read"]["record_digest"] = b.seal(raw)["record_digest"]
                    value["read"]["independent_certificate"]["selected_read_digest"] = value["read"]["record_digest"]
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_step(before, value)
        self.assertNotEqual(target.inputs.current.C, target.inputs.reset.C)
        for kind in ("reset_archive", "archive_order", "reset_read", "publication", "replay", "target_carrier", "target_w", "reference", "loss"):
            value = deepcopy(row["event"])
            if kind == "reset_archive":
                value["checkpoint"]["carrier_archives"][0]["history_content"]["content"][-1] += 0.01
            elif kind == "archive_order":
                value["checkpoint"]["carrier_archives"][0]["source_edge_ids"].reverse()
            elif kind == "reset_read":
                value["admission_reads"][1]["reset_read"] = value["admission_reads"][1]["read"]
            elif kind == "publication":
                value["publication"][0]["admission_pairs"] = 1
            elif kind == "target_carrier":
                value["actual_target"]["inputs"]["reset"]["Z_4"][0] = 1/16
            elif kind == "reference":
                value["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][-1] += 0.125
            elif kind == "loss":
                value["receipts"][0]["identity_payload"]["core"]["information_losses"] = []
            elif kind == "target_w":
                value["actual_target"]["inputs"]["reset"]["W_A"][0] += 0.125
            else:
                value["replay_identical"] = False
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                r.check_event(seed, case, value)

    def test_signed_reads_wrong_laws_and_finite_boundaries(self):
        _, _, execution = self.retained()
        seed = r.state(execution["shared"]["actual_source"])
        for role in r.ROLES:
            before = r.role_input(seed.inputs, role)
            value = execution["cases"][0]["event"]["admission_reads"][0]["read" if role == "current" else "reset_read"]
            wrong = deepcopy(value)
            wrong["H"] = np.eye(len(wrong["J"])).tolist()
            wrong.pop("independent_certificate")
            wrong = b.seal(wrong)
            cert = r.independent_certificate(before, wrong)
            self.assertGreater(r.Q(cert["bounds"]["geometry_error"]), r.LIMITS["geometry_error"])
            wrong["independent_certificate"] = cert
            with self.assertRaises(ValueError):
                r.check_read(before, wrong)
            for key in ("flat", "readback"):
                wrong = deepcopy(value)
                wrong[key] = [-x for x in wrong[key]]
                self.assertEqual(wrong["source"], value["source"])
                cert = r.independent_certificate(before, wrong)
                self.assertGreater(r.Q(cert["bounds"][key + "_error"]), r.LIMITS[key + "_error"])
            original = value
            for kind in ("old_z_omitted", "gain_folded_into_instant", "slack", "root_count", "residual", "contraction"):
                value = deepcopy(original)
                cert = value.pop("independent_certificate")
                value.pop("record_digest")
                if kind in ("old_z_omitted", "gain_folded_into_instant"):
                    m = len(value["J"])
                    value["generated"] = [[float(r.Q(int(i == j)) + r.Q(r.oracle.KAPPA_H)*
                        ((0 if kind == "old_z_omitted" else r.Q(before.current.Z_4[i*m+j])) +
                         (2 if kind == "gain_folded_into_instant" else 1)*r.Q(x)))
                        for j,x in enumerate(row)] for i,row in enumerate(value["source"])]
                elif kind == "slack":
                    value["bounds"]["uniform_source_slack"] = "0"
                elif kind == "root_count":
                    value["evaluations"] = 0
                elif kind == "residual":
                    value["residual_squared"] = "1"
                else:
                    value["bounds"]["contraction_upper"] = "1"
                value = b.seal(value)
                value["independent_certificate"] = {**cert, "selected_read_digest": value["record_digest"]}
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_read(before, value)
            for bad in ("-1", "NaN", "Infinity", str(r.LIMITS["flat_error"])):
                wrong = deepcopy(original)
                wrong["independent_certificate"]["bounds"]["flat_error"] = bad
                with self.subTest(role=role, bad=bad), self.assertRaises((ValueError, OverflowError)):
                    r.check_read(before, wrong)


if __name__ == "__main__":
    unittest.main()
