"""All-ten bounded cross-contract review; no native event/receipt implementation.

Independent event algebra and exact rational charge bookkeeping surround the
actual companion consumers. Their interval numerical oracles remain the owners
of point read/write errors; this is not another independent dynamics oracle.
"""

import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from itertools import product
from unittest.mock import patch

import numpy as np
import test_p980_a_event_companion as aos
import test_p980_carrier_event_companion as pc
import test_p980_ci_event_companion as ci
import test_p980_event_companion as cos
import test_p980_rg_event_companion as rg
from test_p980_os_effect_witness import IntervalRows, endpoint, vector

PROFILES = tuple(
    (c, r) for r in ("OS", "CI", "PC", "CI_PC", "RG2b") for c in ("C", "A")
)
LIMIT = Q(1, 2**40)


def total(c):
    return sum(Q(float(v)) for v in c)


class AggregateReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = json.loads(cos.INPUT_PATH.read_text())
        cls.a = json.loads(aos.INPUT_PATH.read_text())
        cls.recipes = {
            r: json.loads(m.INPUT_PATH.read_text())
            for r, m in [("CI", ci), ("PC", pc), ("CI_PC", pc), ("RG2b", rg)]
        }
        cos.validate_inputs(cls.shared)
        aos.validate_inputs(cls.a, cls.shared)
        for r, m in [("CI", ci), ("PC", pc), ("CI_PC", pc), ("RG2b", rg)]:
            m.validate_inputs(cls.recipes[r], cls.shared, cls.a)

    def models(self, r):
        if r == "OS":
            return cos.models(copy.deepcopy(self.shared))
        if r == "RG2b":
            return rg.build_models(copy.deepcopy(self.shared))
        return ci.build_models(copy.deepcopy(self.shared))

    def initial(self, source, candidate, role, r):
        c = np.array(
            [
                float(Q(self.shared["roles"][role]["initial_resources"][n]))
                for n in source.nodes
            ]
        )
        w = (
            np.array(
                [float(Q(self.a["source_W"][role][e["edge_id"]])) for e in source.edges]
            )
            if candidate == "A"
            else None
        )
        z = None
        if r in ("PC", "CI_PC"):
            # Assemble support from incidence endpoints, not the numerical mask.
            ends = [{e["tail"]["node_id"], e["head"]["node_id"]} for e in source.edges]
            radius = Q(self.recipes[r]["source_carrier"]["radius"])
            sign = 1 if role == "current" else -1
            z = np.array(
                [
                    [
                        float(
                            sign
                            * radius
                            / 16
                            * (-1) ** (i + j)
                            * (1 if i == j else Q(1, 2) if a & b else 0)
                        )
                        for j, b in enumerate(ends)
                    ]
                    for i, a in enumerate(ends)
                ]
            )
        return c, w, z

    def evaluate(self, model, candidate, r, c, w, z):
        saved = [None if a is None else a.copy() for a in (c, w, z)]
        if r == "OS" and candidate == "A":
            out, truth, _, errors = aos.checked_os(model, c, w)
            result = out["c"], out["w"], None, out["stages"]["read"]["J"]
            low = min(endpoint(v, 0) for v in truth["c"])
            error = errors["resource"]
        elif r == "OS":
            after, _, cert = cos.advance(model, c, vector(c))
            read, _, _ = cos.checked_read_only(model, c, vector(c))
            result = after, None, None, read["read"]["J"]
            low, error = Q(cert["resource_lower"]), Q(cert["resource_error"])
        else:
            evaluator = rg.evaluate if r == "RG2b" else pc.numerical.evaluate
            out, truth = evaluator(model, candidate, r, c, w, z)
            result = out["after"], out["history"], out["carrier"], out["read"]["J"]
            low = min(endpoint(v, 0) for v in truth["after"])
            error = truth["certificate"]["resource_error"]
        for before, after in zip(saved, (c, w, z), strict=True):
            if before is None:
                self.assertIsNone(after)
            else:
                np.testing.assert_array_equal(before, after)
        self.assertLess(error, LIMIT)
        self.assertLessEqual(abs(total(result[0]) - total(c)), len(c) * LIMIT)
        return result, low, error

    def event(self, source, target, candidate, r, c, w, z, reference):
        if r == "OS":
            cm = dict(zip(source.nodes, map(float, c), strict=True))
            if candidate == "C":
                cn, cert = cos.checked_target(self.shared, source, target, cm)
                return {"c": cn, "w": None, "z": None, "archive": None}, cert
            ids = [e["edge_id"] for e in source.edges]
            cn, wn, refs, cert = aos.checked_event(
                self.a,
                self.shared,
                source,
                target,
                cm,
                dict(zip(ids, map(float, w), strict=True)),
                dict(zip(ids, map(float, reference), strict=True)),
            )
            return {
                "c": cn,
                "w": wn,
                "z": None,
                "archive": None,
                "reference": refs,
            }, cert
        if r in ("PC", "CI_PC"):
            return pc.checked_event(
                self.recipes[r],
                self.shared,
                self.a,
                source,
                target,
                candidate,
                r,
                c,
                w,
                z,
                reference,
            )
        module = rg if r == "RG2b" else ci
        return module.checked_event(
            self.recipes[r],
            self.shared,
            self.a,
            source,
            target,
            candidate,
            c,
            w,
            reference,
        )

    def audit_transfer(self, source, target, candidate, r, before, event):
        c, w, z, reference = before
        # This oracle doesn't call any companion transfer/embedding helper.
        for i, node in enumerate(target.nodes):
            if node in source.nodes:
                self.assertEqual(event["c"][i], c[source.nodes.index(node)])
            elif node.startswith("satellite/"):
                self.assertLess(
                    abs(
                        Q(float(event["c"][i]))
                        - Q(float(c[source.nodes.index("source-s")])) / 3
                    ),
                    LIMIT,
                )
            else:
                self.assertEqual(event["c"][i], 0)
        self.assertEqual(np.count_nonzero(event["c"] == 0), 5)
        self.assertGreaterEqual(min(event["c"]), 0)
        old_ids = [e["edge_id"] for e in source.edges]
        for i, edge in enumerate(target.edges):
            j = old_ids.index(edge["edge_id"]) if edge["edge_id"] in old_ids else None
            if candidate == "A":
                self.assertEqual(event["w"][i], w[j] if j is not None else 1)
            if "reference" in event:
                self.assertEqual(
                    event["reference"][i], reference[j] if j is not None else 0
                )
        if candidate == "C":
            self.assertIsNone(event["w"])
        if r in ("PC", "CI_PC"):
            np.testing.assert_array_equal(event["archive"], z)
            self.assertGreater(np.linalg.norm(event["archive"]), 0)
            np.testing.assert_array_equal(
                event["z"], np.zeros((len(target.edges),) * 2)
            )
            self.assertEqual(event["candidate_information_loss"], [])
            self.assertEqual(
                event["carrier_information_loss"], ["carrier_history_loss"]
            )
            self.assertFalse(np.shares_memory(event["archive"], z))
        else:
            self.assertIsNone(event["z"])
            self.assertIsNone(event["archive"])
        self.assertLessEqual(abs(total(event["c"]) - total(c)), 17 * LIMIT)

    def pressure(self, source, target, candidate, r, entry, controls=None):
        """Inject defects into actual event producers, not a report-only oracle."""
        if r == "OS":
            module, name = (
                (aos, "produce_event") if candidate == "A" else (cos, "produce_target")
            )
        else:
            module, name = (
                {"CI": ci, "PC": pc, "CI_PC": pc, "RG2b": rg}[r],
                "produce_event",
            )
        original = getattr(module, name)
        if controls is None:
            controls = ["negative_core", "role_resource", "history", "carrier", "loss"]
            if r in ("PC", "CI_PC"):
                controls += ["archive_stage", "archive_order"]
            elif r != "OS" or candidate == "A":
                controls += ["reference_sign"]
        for control in controls:

            def bad(*args, control=control, **kwargs):
                out = original(*args, **kwargs)
                if control in (
                    "nan_resource",
                    "infinite_resource",
                    "extreme_resource",
                    "resource_shape",
                ):
                    if r == "OS":
                        if control == "resource_shape":
                            del out["resources"]["satellite/1"]
                        else:
                            out["resources"]["satellite/1"] = {
                                "nan_resource": np.nan,
                                "infinite_resource": np.inf,
                                "extreme_resource": np.finfo(float).max,
                            }[control]
                    elif control == "resource_shape":
                        out["c"] = out["c"][:-1]
                    else:
                        out["c"][target.nodes.index("satellite/1")] = {
                            "nan_resource": np.nan,
                            "infinite_resource": np.inf,
                            "extreme_resource": np.finfo(float).max,
                        }[control]
                elif control in ("negative_core", "role_resource"):
                    node = "core" if control == "negative_core" else "satellite/1"
                    value = -float(Q(1, 2**45)) if control == "negative_core" else 1.0
                    if r == "OS":
                        out["resources"][node] = value
                    else:
                        out["c"][target.nodes.index(node)] = value
                elif control == "history":
                    key = "W" if r == "OS" else "w"
                    if candidate == "C":
                        out[key] = np.ones(len(target.edges))
                    elif r == "OS":
                        out[key]["old-1"] = 1.0
                    else:
                        out[key][
                            next(
                                i
                                for i, e in enumerate(target.edges)
                                if e["edge_id"] == "old-1"
                            )
                        ] = 1.0
                elif control == "carrier":
                    key = "Z" if r == "OS" else "z"
                    out[key] = None if r in ("PC", "CI_PC") else np.zeros((16, 16))
                elif control == "loss":
                    key = (
                        "information_loss"
                        if r == "OS" and candidate == "C"
                        else "candidate_information_loss"
                    )
                    out[key] = ["carrier_history_loss"]
                elif control == "archive_stage":
                    out["archive"] *= -1
                elif control == "archive_order":
                    out["archive_edges"] = out["archive_edges"][::-1]
                else:
                    if r == "OS":
                        out["reference_current"]["old-1"] *= -1
                    else:
                        out["reference"][
                            next(
                                i
                                for i, e in enumerate(target.edges)
                                if e["edge_id"] == "old-1"
                            )
                        ] *= -1
                return out

            with (
                self.subTest(profile=candidate + "_" + r, control=control),
                patch.object(module, name, bad),
                self.assertRaises((ValueError, AssertionError)),
            ):
                self.event(source, target, candidate, r, *entry)
        return controls

    def test_all_ten_nonfinite_extreme_and_incomplete_event_outputs(self):
        for candidate, r in PROFILES:
            source, target = self.models(r)
            c, w, z = self.initial(source, candidate, "reset", r)
            probe, _, _ = self.evaluate(source, candidate, r, c, w, z)
            self.pressure(
                source,
                target,
                candidate,
                r,
                (c, w, z, probe[3]),
                [
                    "nan_resource",
                    "infinite_resource",
                    "extreme_resource",
                    "resource_shape",
                ],
            )

    def test_resource_box_corners_and_signed_coarse_boundary(self):
        # Exhaust the vertices of each declared *initial* resource box. These
        # check transfer algebra only, not nonlinear dynamics on 2,048 paths.
        count = 0
        radius = Q(self.shared["resource_initial_radius"])
        for role in ("current", "reset"):
            center = self.shared["roles"][role]["initial_resources"]
            for signs in product((-1, 1), repeat=10):
                exact = {
                    n: Q(center[n]) + sign * radius
                    for n, sign in zip(
                        self.shared["source_graph"]["nodes"], signs, strict=True
                    )
                }
                incoming = {n: float(v) for n, v in exact.items()}
                out = cos.produce_target(copy.deepcopy(self.shared), incoming)[
                    "resources"
                ]
                intended = {
                    n: (
                        exact[n]
                        if n in exact
                        else exact["source-s"] / 3
                        if n.startswith("satellite/")
                        else Q(0)
                    )
                    for n in out
                }
                self.assertEqual(sum(intended.values()), sum(exact.values()))
                self.assertTrue(all(v >= 0 for v in intended.values()))
                self.assertLess(max(abs(Q(out[n]) - intended[n]) for n in out), LIMIT)
                self.assertLessEqual(
                    abs(sum(map(Q, out.values())) - sum(map(Q, incoming.values()))),
                    17 * LIMIT,
                )
                count += 1
        self.assertEqual(count, 2048)

        # Normative rational identities only; the native coarse operator is
        # still P9-8.1d work. Zero total and cancellation need different encodings.
        def encode(values):
            charge = sum(values)
            return charge, tuple(v / charge for v in values) if charge else (
                Q(1, 3),
            ) * 3

        def decode(encoded):
            charge, shares = encoded
            return tuple(charge * v for v in shares)

        cases = [
            (Q(0),) * 3,
            (Q(1), Q(0), Q(0)),
            (Q(2**80), Q(1, 2**80), Q(3)),
            (Q(1), Q(-1), Q(0)),
            (Q(2**80), Q(-(2**80)), Q(1, 2**80)),
        ]
        for values in cases:
            positive = tuple(max(v, 0) for v in values)
            negative = tuple(max(-v, 0) for v in values)
            self.assertEqual(
                tuple(
                    a - b
                    for a, b in zip(
                        decode(encode(positive)), decode(encode(negative)), strict=True
                    )
                ),
                values,
            )
        cancelled = cases[3]
        self.assertNotEqual(
            tuple(
                sum(cancelled) * abs(v) / sum(map(abs, cancelled)) for v in cancelled
            ),
            cancelled,
        )

    def test_all_ten_both_roles_charge_history_and_continuation(self):
        report = {}
        for candidate, r in PROFILES:
            source, target = self.models(r)
            for key, model in [
                ("source_graph", source),
                ("expected_target_roles", target),
            ]:
                cos.assert_model_binding(self.shared, key, model)
            for role in ("current", "reset"):
                with self.subTest(profile=candidate + "_" + r, role=role):
                    c, w, z = self.initial(source, candidate, role, r)
                    initial_charge = total(c)
                    encoded_error = abs(
                        initial_charge - (Q(30 if role == "current" else 20) + Q(9, 64))
                    )
                    self.assertLess(encoded_error, 10 * LIMIT)
                    if role == "current":
                        (c, w, z, _), _, _ = self.evaluate(
                            source, candidate, r, c, w, z
                        )
                        rows = IntervalRows(source).rows(
                            vector(c), vector(w if w is not None else np.ones(9))
                        )[source.index["source-s"]]
                        self.assertTrue(all(endpoint(x, 0) > 0 for x in rows))
                        self.assertLess(
                            sum(
                                max(abs(endpoint(x, 0)), abs(endpoint(x, 1))) ** 2
                                for x in rows
                            ),
                            Q(1, 4),
                        )
                    # Read-only source reference: discard all hypothetical outputs.
                    probe, _, _ = self.evaluate(source, candidate, r, c, w, z)
                    entry = (
                        c.copy(),
                        None if w is None else w.copy(),
                        None if z is None else z.copy(),
                        probe[3].copy(),
                    )
                    event, _cert = self.event(source, target, candidate, r, *entry)
                    self.audit_transfer(source, target, candidate, r, entry, event)
                    controls = (
                        self.pressure(source, target, candidate, r, entry)
                        if role == "reset"
                        else []
                    )
                    c, w, z = event["c"], event["w"], event["z"]
                    event_charge_error = abs(total(c) - total(entry[0]))
                    steps = []
                    for k in range(10):
                        (c, w, z, _j), low, error = self.evaluate(
                            target, candidate, r, c, w, z
                        )
                        self.assertGreater(low, Q(1, 16384))
                        self.assertGreater(min(c), 0)
                        self.assertLess(max(c), 4)
                        if w is not None:
                            self.assertGreater(min(w), 0.99)
                            self.assertLess(max(w), 1.001)
                        steps.append(
                            {
                                "resource_lower": float(low),
                                "resource_error": float(error),
                                "charge_discrepancy": str(
                                    abs(total(c) - initial_charge)
                                ),
                            }
                        )
                    final, _, _ = self.evaluate(target, candidate, r, c, w, z)
                    charge_error = abs(total(c) - initial_charge)
                    charge_limit = (197 if role == "current" else 187) * LIMIT
                    self.assertLessEqual(charge_error, charge_limit)
                    report[candidate + "_" + r + "_" + role] = {
                        "physical_source_steps": int(role == "current"),
                        "physical_target_steps": 10,
                        "read_only_source_and_final_probes": 2,
                        "initial_encoding_charge_error": str(encoded_error),
                        "event_charge_error": str(event_charge_error),
                        "charge_error": str(charge_error),
                        "charge_limit": str(charge_limit),
                        "steps": steps,
                        "final_current_max": float(max(abs(final[3]))),
                        "rejected_event_controls": controls,
                        "old_reference_channel_checked": r != "OS" or candidate == "A",
                    }
                    print(
                        candidate + "_" + r + "_" + role + " passed",
                        file=sys.stderr,
                        flush=True,
                    )
        self.assertEqual(len(report), 20)
        type(self).report = report


if __name__ == "__main__":
    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    run = unittest.main(exit=False)
    if reporting and run.result.wasSuccessful():
        print(json.dumps(AggregateReviewTests.report, indent=2, sort_keys=True))
    sys.exit(not run.result.wasSuccessful())
