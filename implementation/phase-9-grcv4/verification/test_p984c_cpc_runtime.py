"""C_PC boundary pressure: independent laws, signed reads and carrier lifecycle."""

from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np
import p984c_cpc_runtime as runtime

r, b = runtime.r, runtime.b


class CPCBoundaryTests(unittest.TestCase):
    def test_contract_targets_domains_and_nominal_continuation(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
        self.assertNotEqual(source.current.Z_4, source.reset.Z_4)
        with ExitStack() as stack:
            for module, name in ((r, "CandidatePCRead"), (r, "ProvisionalCandidatePCStep"), (r.native, "GRC9V4CPCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))
            for case in manifest["cases"]:
                target = r.independent_target(manifest, case)
                self.assertEqual(set(target.geometry.reference.profile.params_resolved.candidate.W_C_tr), set(target.geometry.reference.graph.live_edge_ids))
                for role in r.ROLES:
                    authority = getattr(target, role)
                    self.assertEqual(sum(map(r.Q, authority.C)), sum(map(r.Q, getattr(source, role).C)))
                    self.assertTrue(all(z == 0 for z in authority.Z_4))
                    self.assertIsNone(authority.W_A)
                    r.truth(r.role_input(target, role))  # connected-tree whole-ball spectral proof
                prediction = r.preflight(target)
                self.assertEqual([len(prediction[k]) for k in r.ROLES], [10, 10])
                self.assertTrue(all(min(v["C"]) >= 0 for values in prediction.values() for v in values))
        for kind in ("population", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "population":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["Z_4"][0] += 0.01
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    @classmethod
    def retained(cls):
        manifest, record = b.read(runtime.INPUTS), b.read(runtime.RESULTS)
        return manifest, record, runtime.materialize(manifest, record)

    def test_compaction_roster_scope_and_exact_reuse(self):
        manifest, record, _ = self.retained()
        raw = runtime.expand(record["execution"])
        self.assertEqual(runtime.expand(runtime.compact(raw)), raw)
        corrupt = deepcopy(record["execution"])
        corrupt["contexts"][next(iter(corrupt["contexts"]))] = []
        with self.assertRaisesRegex(ValueError, "context digest"):
            runtime.expand(corrupt)
        for kind in ("population", "scope", "event_vs_case", "reuse", "reset_schedule"):
            changed = deepcopy(record)
            execution = runtime.expand(changed["execution"])
            if kind == "population":
                execution["cases"].pop()
            elif kind == "scope":
                execution["cases"][0]["user_accepted"] = True
            elif kind == "event_vs_case":
                execution["cases"][0]["case_passed"] = False
            elif kind == "reset_schedule":
                execution["cases"][0]["continuation"].pop()
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            changed["execution"] = runtime.compact(b.seal(execution))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.status(manifest, b.seal(changed))

    def test_carrier_read_write_and_both_role_event_pressure(self):
        manifest, _, execution = self.retained()
        i = next(i for i, c in enumerate(manifest["cases"]) if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        row, case = execution["cases"][i], manifest["cases"][i]
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        for role in r.ROLES:
            # The second beat consumes a genuinely nonzero formed carrier.
            first = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            before = b.GeometryStageInputs.from_payload(first["poststate"])
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 2)
            self.assertTrue(any(z != 0 for z in before.current.Z_4))
            r.check_step(before, step, numerics=True)
            runtime.signed.check_vectors(before, step["read"])
            for kind in ("double_write", "post_source", "old_reset", "wrong_current", "stale_restart", "reset_overwrite", "whole_chart", "geometry"):
                value = deepcopy(step)
                if kind == "double_write":
                    value["carrier_calls"] *= 2
                elif kind == "post_source":
                    value["carrier_calls"][0]["source"] = [x for v in value["restart"]["source"] for x in v]
                elif kind == "old_reset":
                    value["carrier_calls"][0]["Z"] = list(before.reset.Z_4)
                elif kind == "wrong_current":
                    value["selection_current"] = value["read"]["baseline"]
                elif kind == "stale_restart":
                    value["restart"] = value["read"]
                elif kind == "reset_overwrite":
                    value["poststate"]["reset"] = value["poststate"]["current"]
                else:
                    if kind == "whole_chart":
                        value["read"]["bounds"]["selector_gap_lower"] = "0"
                    else:
                        value["read"]["H"][0][0] += 2**-20
                    raw = {k: v for k, v in value["read"].items() if k != "independent_certificate"}
                    value["read"]["record_digest"] = b.seal(raw)["record_digest"]
                    value["read"]["independent_certificate"]["selected_read_digest"] = value["read"]["record_digest"]
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_step(before, value)
        self.assertNotEqual(target.inputs.current.C, target.inputs.reset.C)
        for kind in ("reset_archive", "archive_order", "reset_read", "publication", "replay", "target_carrier"):
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
            else:
                value["replay_identical"] = False
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                r.check_event(seed, case, value)

    def test_signed_intermediates_wrong_laws_and_finite_boundaries(self):
        manifest, record, execution = self.retained()
        seed = r.state(execution["shared"]["actual_source"])
        for role in r.ROLES:
            before = r.role_input(seed.inputs, role)
            value = execution["cases"][0]["event"]["admission_reads"][0]["read" if role == "current" else "reset_read"]
            exact = r.truth(before)
            for channel in ("geometry", "feedback", "modulation"):
                control = exact["high"].read("C", exact["c"], None, exact["H"], **{channel: False})
                wrong = deepcopy(value)
                wrong["J"] = [float(x.mid) for x in control["J"]]
                r.separation(np.array(value["J"]), np.array(wrong["J"]), exact["read"]["J"], control["J"])
                cert = r.independent_certificate(before, wrong)
                self.assertGreater(r.Q(cert["bounds"]["current_error"]), r.LIMITS["current_error"])
            for key in ("flat", "readback"):
                wrong = deepcopy(value)
                wrong[key] = [-x for x in wrong[key]]
                self.assertEqual(wrong["source"], value["source"])
                with self.subTest(role=role, key=key), self.assertRaisesRegex(ValueError, "signed intermediate"):
                    runtime.signed.check_vectors(before, wrong)
        for bad in ("-1", "NaN", "Infinity", str(runtime.signed.LIMIT)):
            certificates = deepcopy(record["signed_read_certificates"])
            first = next(iter(certificates))
            certificates[first]["flat_error"] = bad
            with self.subTest(bad=bad), self.assertRaises((ValueError, OverflowError)):
                runtime.vectors(manifest, execution, certificates)
        certificates = deepcopy(record["signed_read_certificates"])
        certificates.pop(next(iter(certificates)))
        with self.assertRaises(KeyError):
            runtime.vectors(manifest, execution, certificates)


if __name__ == "__main__":
    unittest.main()
