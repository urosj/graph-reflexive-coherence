"""Bounded A/C CI source -> event -> target research, with no persistent Z.

Reuses accepted joint-root certificates, exact resource/W maps and entry-owned
writer controls. No native event API, profile registration or receipt.
"""

import copy
import json
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np
import test_p980_a_event_companion as a_event
import test_p980_event_companion as common
import test_p980_realization_numerical as numerical
from test_p980_carrier_event_companion import reference_current
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    bounds,
    endpoint,
    full_error,
    number,
    upper_abs,
    vector,
)

INPUT_PATH = (
    Path(__file__).resolve().parents[1] / "tranche-8/P9-8.0-CI-ConstructionInputs.json"
)
require = common.require


def validate_inputs(case, shared, a_case):
    common.validate_inputs(shared)
    a_event.validate_inputs(a_case, shared)
    require(
        case
        == {
            "research_case_id": "P9-8.0-CI-SOURCE-D52-POSITIVE-PHASE-3",
            "shared_input_record": common.INPUT_PATH.name,
            "A_input_record": a_event.INPUT_PATH.name,
            "inherited_A_fields": [
                "parameters",
                "source_W",
                "event_history",
                "row_detection",
            ],
            "profiles": ["A_CI", "C_CI"],
            "root_equation": "H=I+kappa_H*S(C,W,H)",
            "geometry_radius": str(numerical.exact.GEOMETRY_RADIUS),
            "source_schedule": {"current_physical_steps": 1, "reset_physical_steps": 0},
            "target_steps": bounds.HORIZON,
            "reference_current": "fresh_role_event_entry_CI_root_read",
            "new_reference_current": "exact_zero",
            "carrier_history": "not_applicable",
            "Z": None,
            "archive": None,
            "candidate_information_loss": [],
            "carrier_information_loss": [],
            "identity_scope": "research_operands_only_no_native_receipt_or_registration",
        },
        "CI input recipe mismatch",
    )


def build_models(shared):
    return tuple(
        numerical.RepresentedRows(shared[k]["nodes"], shared[k]["edges"], PARAMS)
        for k in ("source_graph", "expected_target_roles")
    )


def produce_event(shared, candidate, c, w, reference):
    source_ids = [edge["edge_id"] for edge in shared["source_graph"]["edges"]]
    ids = [edge["edge_id"] for edge in shared["expected_target_roles"]["edges"]]
    resources = common.produce_target(
        shared, dict(zip(shared["source_graph"]["nodes"], c, strict=True))
    )["resources"]
    old_w = dict(zip(source_ids, w, strict=True)) if w is not None else {}
    refs = dict(zip(source_ids, reference, strict=True))
    return {
        "c": np.array([resources[n] for n in shared["expected_target_roles"]["nodes"]]),
        "w": np.array([old_w.get(edge, 1.0) for edge in ids])
        if candidate == "A"
        else None,
        "reference": np.array([refs.get(edge, 0.0) for edge in ids]),
        "C_references": copy.deepcopy(shared["target_reference_weights"])
        if candidate == "C"
        else None,
        "candidate_history": "exact_old_edge_lineage_and_positive_bond_seed"
        if candidate == "A"
        else "rederived",
        "carrier_history": "not_applicable",
        "z": None,
        "archive": None,
        "candidate_information_loss": [],
        "carrier_information_loss": [],
    }


def checked_event(case, shared, a_case, source, target, candidate, c, w, reference):
    validate_inputs(case, shared, a_case)
    require(candidate in ("A", "C"), "unsupported CI candidate")
    c = numerical.finite_array(c, (len(source.nodes),)).copy()
    reference = numerical.finite_array(reference, (len(source.edges),)).copy()
    if candidate == "A":
        w = numerical.finite_array(w, (len(source.edges),)).copy()
    else:
        require(w is None, "C history must be absent")
    _, truth = numerical.evaluate(source, candidate, "CI", c, w, None)
    require(
        full_error(reference, truth["read"]["J"]) < numerical.CURRENT_ERROR_LIMIT,
        "source reference-current recipe mismatch",
    )
    p = IV.matrix(
        [[number(v) for v in row] for row in common.transfer_matrix(source, target)]
    )
    ci = p * vector(c)
    embedding, seed = a_event.history_embedding(source, target)
    e = IV.matrix([[number(v) for v in row] for row in embedding])
    wi = e * vector(w) + vector(seed) if w is not None else None
    ji = e * vector(reference)
    out = produce_event(
        copy.deepcopy(shared),
        candidate,
        c.copy(),
        None if w is None else w.copy(),
        reference.copy(),
    )
    require(
        set(out)
        == {
            "c",
            "w",
            "reference",
            "C_references",
            "candidate_history",
            "carrier_history",
            "z",
            "archive",
            "candidate_information_loss",
            "carrier_information_loss",
        },
        "event fields mismatch",
    )
    error = full_error(out["c"], ci)
    require(error < numerical.RESOURCE_ERROR_LIMIT, "event resource error unresolved")
    for i, n in enumerate(target.nodes):
        if n.startswith("outside-"):
            require(out["c"][i] == c[source.index[n]], "exterior resource changed")
        elif n == "core" or n.startswith("extra/"):
            require(out["c"][i] == 0, "zero resource face changed")
    if candidate == "A":
        require(full_error(out["w"], wi) == 0, "W lineage changed")
        require(
            out["candidate_history"] == "exact_old_edge_lineage_and_positive_bond_seed"
            and out["C_references"] is None,
            "A history channel mismatch",
        )
    else:
        require(
            out["w"] is None
            and out["candidate_history"] == "rederived"
            and out["C_references"] == shared["target_reference_weights"],
            "C reference channel mismatch",
        )
    require(full_error(out["reference"], ji) == 0, "reference lineage changed")
    require(
        out["z"] is None
        and out["archive"] is None
        and out["carrier_history"] == "not_applicable"
        and out["candidate_information_loss"] == []
        and out["carrier_information_loss"] == [],
        "CI history channels mismatch",
    )
    charge = abs(sum(Q(float(v)) for v in out["c"]) - sum(Q(float(v)) for v in c))
    require(charge <= len(target.nodes) * error, "event charge error unresolved")
    return out, {"resource_error": float(error), "charge_error": float(charge)}


class CIEventCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(INPUT_PATH.read_text())
        cls.shared = json.loads(common.INPUT_PATH.read_text())
        cls.a_case = json.loads(a_event.INPUT_PATH.read_text())
        validate_inputs(cls.case, cls.shared, cls.a_case)
        cls.source, cls.target = build_models(copy.deepcopy(cls.shared))
        for key, model in zip(
            ("source_graph", "expected_target_roles"),
            (cls.source, cls.target),
            strict=True,
        ):
            common.assert_model_binding(cls.shared, key, model)

    def initial(self, candidate, role):
        c = self.source.vector(
            {
                n: Q(v)
                for n, v in self.shared["roles"][role]["initial_resources"].items()
            }
        )
        w = (
            np.array(
                [
                    float(Q(self.a_case["source_W"][role][e["edge_id"]]))
                    for e in self.source.edges
                ]
            )
            if candidate == "A"
            else None
        )
        return c, w

    def entry(self, candidate, role):
        c, w = self.initial(candidate, role)
        if role == "current":
            out, _ = numerical.evaluate(self.source, candidate, "CI", c, w, None)
            c, w = out["after"], out["history"]
            rows = IntervalRows(self.source).rows(
                vector(c),
                vector(w) if w is not None else vector([1] * len(self.source.edges)),
            )[self.source.index["source-s"]]
            self.assertTrue(all(endpoint(v, 0) > 0 for v in rows))
            self.assertLess(sum(upper_abs(v) ** 2 for v in rows), Q(1, 4))
        # The read helper exposes only J; its hypothetical writes stay private.
        return c, w, reference_current(self.source, candidate, "CI", c, w, None)

    def declared_source_stage(self, candidate, role):
        # CEC-F1: independent rational-record construction, not initial()/entry().
        graph = self.shared["source_graph"]
        c = np.array(
            [
                float(Q(self.shared["roles"][role]["initial_resources"][n]))
                for n in graph["nodes"]
            ]
        )
        w = (
            np.array(
                [
                    float(Q(self.a_case["source_W"][role][e["edge_id"]]))
                    for e in graph["edges"]
                ]
            )
            if candidate == "A"
            else None
        )
        if role == "current":
            out, _ = numerical.evaluate(self.source, candidate, "CI", c, w, None)
            c, w = out["after"], out["history"]
        return c.copy(), None if w is None else w.copy()

    def event(self, candidate, role):
        expected_c, expected_w = self.declared_source_stage(candidate, role)
        c, w, reference = self.entry(candidate, role)
        require(
            np.array_equal(c, expected_c),
            "resource stage differs from declared physical entry",
        )
        require(
            (w is None and expected_w is None)
            or (
                w is not None
                and expected_w is not None
                and np.array_equal(w, expected_w)
            ),
            "W stage differs from declared physical entry",
        )
        return checked_event(
            self.case,
            self.shared,
            self.a_case,
            self.source,
            self.target,
            candidate,
            c,
            w,
            reference,
        )

    def test_both_candidates_roles_ten_target_steps(self):
        report = {}
        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                event, cert = self.event(candidate, role)
                c, w = event["c"], event["w"]
                steps = []
                for k in range(bounds.HORIZON):
                    out, truth = numerical.evaluate(
                        self.target, candidate, "CI", c, w, None
                    )
                    low = min(endpoint(v, 0) for v in truth["after"])
                    self.assertGreater(low, Q(1, 16384))
                    self.assertLess(max(endpoint(v, 1) for v in truth["after"]), 4)
                    self.assertIsNone(out["carrier"])
                    if k == 0:
                        for i, edge in enumerate(self.target.edges):
                            if edge["edge_id"].startswith("internal/"):
                                self.assertEqual(event["reference"][i], 0)
                                self.assertGreater(abs(out["read"]["J"][i]), 1e-4)
                    steps.append(
                        {
                            "resource_lower": float(low),
                            **{
                                name: float(v)
                                for name, v in truth["certificate"].items()
                            },
                        }
                    )
                    c, w = out["after"], out["history"]
                _, final = numerical.evaluate(self.target, candidate, "CI", c, w, None)
                report[candidate + "_CI_" + role] = {
                    "event": cert,
                    "steps": steps,
                    "final_current_error": float(final["certificate"]["current_error"]),
                }
        type(self).continuation_report = report

    def test_target_root_and_history_effects(self):
        effects = {}

        def compare(key, *args):
            effects[key] = numerical.checked_separation(key, *args)

        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                key = candidate + "_CI_" + role
                event, _ = self.event(candidate, role)
                c, w = event["c"], event["w"]
                out, truth = numerical.evaluate(
                    self.target, candidate, "CI", c, w, None
                )
                high = truth["high"]
                controls = [
                    ("geometry", {"geometry": False}),
                    ("readback", {"feedback": False}),
                ]
                if candidate == "C":
                    controls.append(("modulation", {"modulation": False}))
                for name, flags in controls:
                    off_i = high.read(
                        candidate, truth["c"], truth["w"], truth["H"], **flags
                    )
                    off = self.target.read(
                        candidate,
                        c.copy(),
                        None if w is None else w.copy(),
                        out["H"].copy(),
                        **flags,
                    )
                    compare(
                        key + "_" + name,
                        out["read"]["J"],
                        off["J"],
                        truth["read"]["J"],
                        off_i["J"],
                    )
                # Remove the instantaneous source from the entire root law,
                # giving H=I. This is a fixed-H control, not a PC state.
                off_i = high.read(candidate, truth["c"], truth["w"], high.I)
                off = self.target.read(
                    candidate,
                    c.copy(),
                    None if w is None else w.copy(),
                    self.target.I.copy(),
                )
                compare(
                    key + "_instantaneous_source",
                    out["read"]["J"],
                    off["J"],
                    truth["read"]["J"],
                    off_i["J"],
                )
                if candidate == "A":
                    nxt, ni = numerical.evaluate(
                        self.target,
                        candidate,
                        "CI",
                        out["after"],
                        out["history"],
                        None,
                        ci=truth["after"],
                        wi=truth["history"],
                    )
                    for mode in ("baseline_current", "stale_resource"):
                        wc_i = high.write(
                            truth["after"]
                            if mode == "baseline_current"
                            else truth["c"],
                            truth["w"],
                            truth["read"]["baseline"]
                            if mode == "baseline_current"
                            else truth["read"]["J"],
                        )
                        wc = a_event.checked_counterfactual_writer(
                            self.target,
                            out["after"] if mode == "baseline_current" else c,
                            w,
                            out["read"]["baseline"]
                            if mode == "baseline_current"
                            else out["read"]["J"],
                        )
                        compare(
                            key + "_" + mode + "_W",
                            out["history"],
                            wc,
                            truth["history"],
                            wc_i,
                        )
                        off, oi = numerical.evaluate(
                            self.target,
                            candidate,
                            "CI",
                            out["after"],
                            wc,
                            None,
                            ci=truth["after"],
                            wi=wc_i,
                        )
                        compare(
                            key + "_" + mode + "_next_current",
                            nxt["read"]["J"],
                            off["read"]["J"],
                            ni["read"]["J"],
                            oi["read"]["J"],
                        )
        self.assertEqual(len(effects), 22)
        type(self).effect_report = effects

    def test_source_stage_is_bound_through_event(self):
        original = self.entry
        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                self.event(candidate, role)
                controls = ["probe_resources"]
                if candidate == "A":
                    controls.append("probe_history")
                if role == "current":
                    controls.append("drop_source_step")
                for mode in controls:

                    def wrong_stage(candidate, role, mode=mode):
                        c, w, ref = original(candidate, role)
                        if mode == "drop_source_step":
                            c, w = self.initial(candidate, role)
                        else:
                            probe, _ = numerical.evaluate(
                                self.source, candidate, "CI", c, w, None
                            )
                            if mode == "probe_resources":
                                c = probe["after"]
                            else:
                                w = probe["history"]
                        return c, w, ref

                    with (
                        self.subTest(candidate=candidate, role=role, mode=mode),
                        patch.object(self, "entry", side_effect=wrong_stage),
                        self.assertRaisesRegex(ValueError, "declared physical entry"),
                    ):
                        self.event(candidate, role)

    def test_recipe_and_consumed_model_binding(self):
        for field, value in (
            ("profiles", ["A_OS", "C_OS"]),
            ("root_equation", "H=I"),
            ("Z", []),
            ("carrier_information_loss", ["carrier_history_loss"]),
        ):
            bad = copy.deepcopy(self.case)
            bad[field] = value
            with self.assertRaisesRegex(ValueError, "CI input recipe"):
                validate_inputs(bad, self.shared, self.a_case)
        raw = build_models
        for mode in ("ports", "parameters", "mask"):

            def corrupt(shared, mode=mode):
                source, target = raw(shared)
                if mode == "ports":
                    target.edges[0]["tail"]["port"] = 5
                elif mode == "parameters":
                    target.params = replace(target.params, chi_a=2 * PARAMS.chi_a)
                else:
                    target.mask[-1, -1] = 0
                return source, target

            probe = type("CISetupProbe", (CIEventCompanionTests,), {})
            with (
                patch(__name__ + ".build_models", side_effect=corrupt),
                self.assertRaisesRegex(ValueError, "consumed model"),
            ):
                probe.setUpClass()
            self.assertEqual(probe.shared, self.shared)

    def test_event_channels_and_nonuniform_history_controls(self):
        for candidate in ("A", "C"):
            c, w, _ = self.entry(candidate, "reset")
            # Transfer-only A probe exposes swaps hidden by uniform nominal W.
            if w is not None:
                w += np.arange(-4, 5) * 2**-40
            ref = reference_current(self.source, candidate, "CI", c, w, None)

            def consume(reference=ref, candidate=candidate, c=c, w=w):
                return checked_event(
                    self.case,
                    self.shared,
                    self.a_case,
                    self.source,
                    self.target,
                    candidate,
                    c,
                    w,
                    reference,
                )

            with self.assertRaisesRegex(ValueError, "source reference-current recipe"):
                consume(reference=-ref)
            good, _ = consume()
            for mode in (
                "z",
                "archive",
                "carrier_policy",
                "carrier_loss",
                "candidate_loss",
                "resource",
                "reference",
                "candidate_state",
            ):
                bad = copy.deepcopy(good)
                if mode == "z":
                    bad["z"] = np.zeros(
                        (len(self.target.edges), len(self.target.edges))
                    )
                elif mode == "archive":
                    bad["archive"] = []
                elif mode == "carrier_policy":
                    bad["carrier_history"] = "reset"
                elif mode == "carrier_loss":
                    bad["carrier_information_loss"] = ["carrier_history_loss"]
                elif mode == "candidate_loss":
                    bad["candidate_information_loss"] = ["history_loss"]
                elif mode == "resource":
                    bad["c"][self.target.index["core"]] = 0.125
                elif mode == "reference":
                    bad["reference"][-1] += 0.125
                elif candidate == "A":
                    ids = {e["edge_id"]: i for i, e in enumerate(self.target.edges)}
                    i, j = ids["old-1"], ids["old-9"]
                    bad["w"][i], bad["w"][j] = bad["w"][j], bad["w"][i]
                else:
                    bad["C_references"]["old-1"] = "2"
                with (
                    self.subTest(candidate=candidate, mode=mode),
                    patch(__name__ + ".produce_event", return_value=bad),
                    self.assertRaises(ValueError),
                ):
                    consume()

    def test_event_input_ownership_and_scratch(self):
        c, w, reference = self.entry("A", "current")
        saved = [a.copy() for a in (c, w, reference)]
        raw = produce_event

        def consume():
            return checked_event(
                self.case,
                self.shared,
                self.a_case,
                self.source,
                self.target,
                "A",
                c,
                w,
                reference,
            )

        for operand in range(3):

            def shifted(shared, candidate, cc, ww, ref, operand=operand):
                (cc, ww, ref)[operand].flat[0] += 0.125
                return raw(shared, candidate, cc, ww, ref)

            with (
                patch(__name__ + ".produce_event", side_effect=shifted),
                self.assertRaises(ValueError),
            ):
                consume()
            for actual, original in zip((c, w, reference), saved, strict=True):
                np.testing.assert_array_equal(actual, original)

        def scratch(shared, candidate, cc, ww, ref):
            out = raw(shared, candidate, cc, ww, ref)
            for a in (cc, ww, ref):
                a.fill(0)
            return out

        with patch(__name__ + ".produce_event", side_effect=scratch):
            consume()
        for actual, original in zip((c, w, reference), saved, strict=True):
            np.testing.assert_array_equal(actual, original)


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(
            json.dumps(
                {
                    "continuation": CIEventCompanionTests.continuation_report,
                    "effects": CIEventCompanionTests.effect_report,
                },
                indent=2,
            )
        )
    sys.exit(not result.result.wasSuccessful())
