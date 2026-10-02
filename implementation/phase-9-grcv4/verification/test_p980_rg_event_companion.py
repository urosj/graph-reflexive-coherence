"""Bounded A/C RG2b source -> event -> target, with graph-specific sections.

Reuses accepted finite-chain certificates, exact resource/W maps and entry-owned
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
import test_p980_rg2b_numerical as numerical
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
    Path(__file__).resolve().parents[1] / "tranche-8/P9-8.0-RG-ConstructionInputs.json"
)
require = common.require


def validate_inputs(case, shared, a_case):
    common.validate_inputs(shared)
    a_event.validate_inputs(a_case, shared)
    require(
        case
        == {
            "research_case_id": "P9-8.0-RG-SOURCE-D52-POSITIVE-PHASE-3",
            "shared_input_record": common.INPUT_PATH.name,
            "A_input_record": a_event.INPUT_PATH.name,
            "inherited_A_fields": [
                "parameters",
                "source_W",
                "event_history",
                "row_detection",
            ],
            "profiles": ["A_RG2b", "C_RG2b"],
            "completion": {
                "resources": ["-1", "5"],
                "scaled_log_history": ["-1", "1"],
                "history_scale": "512",
                "application": "arguments_only_at_every_inverse_depth",
                "section_radius": "1/4096",
                "section_lipschitz": "1/1024",
                "terminal_section": "identity",
                "depth": {"A": 4, "C": 6},
                "graph_binding": "reconstruct_each_graph_own_completion_relative_section",
            },
            "source_schedule": {"current_physical_steps": 1, "reset_physical_steps": 0},
            "target_steps": bounds.HORIZON,
            "reference_current": "fresh_role_event_entry_RG_section_read",
            "new_reference_current": "exact_zero",
            "carrier_history": "not_applicable",
            "Z": None,
            "archive": None,
            "candidate_information_loss": [],
            "carrier_information_loss": [],
            "identity_scope": "research_operands_only_no_native_receipt_or_registration",
        },
        "RG input recipe mismatch",
    )

    completion = numerical.rg
    require(
        (
            completion.C_LOW,
            completion.C_HIGH,
            completion.Y_LOW,
            completion.Y_HIGH,
            completion.SCALE,
            completion.RHO,
            completion.SECTION_LIP,
        )
        == (Q(-1), Q(5), Q(-1), Q(1), Q(512), Q(1, 4096), Q(1, 1024))
        and numerical.DEPTH == {"A": 4, "C": 6},
        "frozen RG completion mismatch",
    )


def evaluate(model, candidate, realization, c, w, z, *, ci=None, wi=None):
    """Owned point certificate plus optional composed intended-exact branch.

    Recompute the returned chain's certificate against saved entry inputs;
    never take the producer's exact-read/after fields as the expected result.
    """
    require(realization == "RG2b" and z is None, "RG realization/carrier mismatch")
    c = numerical.finite_array(c, (len(model.nodes),)).copy()
    if candidate == "A":
        w = numerical.finite_array(w, (len(model.edges),)).copy()
        require(np.all(w > 0), "positive A history required")
    else:
        require(
            candidate == "C" and w is None and wi is None, "C history must be absent"
        )
    pc, pw = vector(c), vector(w) if w is not None else None
    point_query = numerical.rg.state(candidate, pc, pw)
    ci = None if ci is None else ci.copy()
    wi = None if wi is None else wi.copy()
    require(
        (ci is None and wi is None)
        or (ci is not None and (candidate == "C" or wi is not None)),
        "complete intended-exact input required",
    )
    after, wn, stage = numerical.ordinary(
        model, candidate, c.copy(), None if w is None else w.copy()
    )
    require(
        len(stage["chain"].x) == numerical.DEPTH[candidate] + 1,
        "section depth mismatch",
    )
    high = IntervalRows(model)
    hi, cert = numerical.certify_chain(
        numerical.rg.auxiliary(model), candidate, stage["chain"], point_query
    )
    require(
        np.array_equal(stage["H"], stage["chain"].h[0]),
        "returned section geometry mismatch",
    )

    def literal(cc, ww, hh, certificate):
        require(
            all(0 <= endpoint(v, 0) <= endpoint(v, 1) < 4 for v in cc),
            "physical resource domain mismatch",
        )
        if ww is not None:
            require(
                all(
                    Q(-5, 8)
                    < endpoint(number(numerical.rg.SCALE) * IV.ln(v), 0)
                    <= endpoint(number(numerical.rg.SCALE) * IV.ln(v), 1)
                    < Q(5, 8)
                    for v in ww
                ),
                "physical history domain mismatch",
            )
        read = high.read(candidate, cc, ww, hh)
        cn = cc - number(bounds.DT) * high.B * read["J"]
        wh = high.write(cn, ww, read["J"]) if ww is not None else None
        return {
            "high": high,
            "c": cc,
            "w": ww,
            "H": hh,
            "read": read,
            "after": cn,
            "history": wh,
            "certificate": certificate,
        }

    point = literal(pc, pw, hi, cert)
    errors = {
        "current_error": full_error(stage["read"]["J"], point["read"]["J"]),
        "baseline_error": full_error(
            stage["read"]["baseline"], point["read"]["baseline"]
        ),
        "source_error": full_error(
            numerical.finite_array(stage["read"]["source"], model.I.shape).ravel(),
            IV.matrix(list(point["read"]["source"])),
        ),
        "resource_error": full_error(after, point["after"]),
        "history_error": full_error(wn, point["history"]) if w is not None else Q(0),
    }
    require(
        max(errors["current_error"], errors["baseline_error"], errors["resource_error"])
        < numerical.RESOURCE_ERROR_LIMIT
        and errors["history_error"] < numerical.HISTORY_ERROR_LIMIT
        and errors["source_error"] < Q(1, 2**64),
        "full RG evaluation error relative to entry unresolved",
    )
    require(candidate == "A" or wn is None, "C history output must be absent")
    point["certificate"] = {**cert, **errors}
    truth = point
    if ci is not None:
        intended_query = numerical.rg.state(candidate, ci, wi)
        intended_h, intended_cert = numerical.certify_chain(
            numerical.rg.auxiliary(model), candidate, stage["chain"], intended_query
        )
        truth = literal(ci, wi, intended_h, {**intended_cert, **errors})
    return {
        "after": after,
        "history": wn,
        "H": stage["H"],
        "read": stage["read"],
        "carrier": None,
        "chain": stage["chain"],
    }, truth


def reference_current(model, candidate, realization, c, w, z):
    return evaluate(model, candidate, realization, c, w, z)[0]["read"]["J"].copy()


def build_models(shared):
    return tuple(
        numerical.RepresentedAuxiliary(shared[k]["nodes"], shared[k]["edges"], PARAMS)
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
    require(candidate in ("A", "C"), "unsupported RG candidate")
    c = numerical.finite_array(c, (len(source.nodes),)).copy()
    reference = numerical.finite_array(reference, (len(source.edges),)).copy()
    if candidate == "A":
        w = numerical.finite_array(w, (len(source.edges),)).copy()
    else:
        require(w is None, "C history must be absent")
    _, truth = evaluate(source, candidate, "RG2b", c, w, None)
    require(
        full_error(reference, truth["read"]["J"]) < numerical.RESOURCE_ERROR_LIMIT,
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
        "RG history channels mismatch",
    )
    charge = abs(sum(Q(float(v)) for v in out["c"]) - sum(Q(float(v)) for v in c))
    require(charge <= len(target.nodes) * error, "event charge error unresolved")
    return out, {"resource_error": float(error), "charge_error": float(charge)}


class RGEventCompanionTests(unittest.TestCase):
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
            out, _ = evaluate(self.source, candidate, "RG2b", c, w, None)
            c, w = out["after"], out["history"]
            rows = IntervalRows(self.source).rows(
                vector(c),
                vector(w) if w is not None else vector([1] * len(self.source.edges)),
            )[self.source.index["source-s"]]
            self.assertTrue(all(endpoint(v, 0) > 0 for v in rows))
            self.assertLess(sum(upper_abs(v) ** 2 for v in rows), Q(1, 4))
        # The read helper exposes only J; its hypothetical writes stay private.
        return c, w, reference_current(self.source, candidate, "RG2b", c, w, None)

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
            out, _ = evaluate(self.source, candidate, "RG2b", c, w, None)
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
                event, event_cert = self.event(candidate, role)
                c, w = event["c"], event["w"]
                steps = []
                for k in range(bounds.HORIZON):
                    out, truth = evaluate(self.target, candidate, "RG2b", c, w, None)
                    low = min(endpoint(v, 0) for v in truth["after"])
                    self.assertGreater(low, Q(1, 16384))
                    self.assertLess(max(endpoint(v, 1) for v in truth["after"]), 4)
                    self.assertIsNone(out["carrier"])
                    if k == 0:
                        global_bounds = numerical.rg.global_bounds(candidate)
                        sb = numerical.rg.section_budgets(global_bounds)
                        cert = truth["certificate"]
                        inverse_tail = (
                            sb["inverse_lip"]
                            * global_bounds["A_H"]
                            * sb["q_section"] ** (numerical.DEPTH[candidate] - 1)
                            * sb["value_radius"]
                        )
                        inverse_input = (
                            sb["inverse_lip"]
                            * cert["input_error"]
                            / numerical.rg.SECTION_LIP
                        )
                        inverse_upper = (
                            Q(float(out["chain"].x[1][self.target.index["core"]]))
                            + cert["state_error"]
                            + inverse_tail
                            + inverse_input
                        )
                        self.assertLess(inverse_upper, 0)
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
                _, final = evaluate(self.target, candidate, "RG2b", c, w, None)
                report[candidate + "_RG2b_" + role] = {
                    "event": event_cert,
                    "first_inverse_core_upper": float(inverse_upper),
                    "steps": steps,
                    "final_current_error": float(final["certificate"]["current_error"]),
                }
        type(self).continuation_report = report

    def test_target_section_and_history_effects(self):
        effects = {}

        def compare(key, *args):
            try:
                effects[key] = numerical.separation(*args)
            except AssertionError as exc:
                raise AssertionError(f"{key}: {exc}") from exc

        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                key = candidate + "_RG2b_" + role
                event, _ = self.event(candidate, role)
                c, w = event["c"], event["w"]
                out, truth = evaluate(self.target, candidate, "RG2b", c, w, None)
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
                # RG geometry has a time shift, unlike an instantaneous CI root.
                instantaneous_i = (
                    high.I + number(bounds.KAPPA_H) * truth["read"]["source"]
                )
                instantaneous = (
                    self.target.I + float(bounds.KAPPA_H) * out["read"]["source"]
                )
                compare(
                    key + "_not_ci_root",
                    out["H"].ravel(),
                    instantaneous.ravel(),
                    IV.matrix(list(truth["H"])),
                    IV.matrix(list(instantaneous_i)),
                )
                os_i = high.ordinary_os(candidate, truth["c"], truth["w"])[2]
                os = self.target.ordinary_os(
                    candidate, c.copy(), None if w is None else w.copy()
                )[2]
                compare(
                    key + "_versus_os_current",
                    out["read"]["J"],
                    os["read"]["J"],
                    truth["read"]["J"],
                    os_i["read"]["J"],
                )
                _, next_hi, _, _ = numerical.section(
                    self.target,
                    candidate,
                    out["after"].copy(),
                    None if out["history"] is None else out["history"].copy(),
                    exact_c=truth["after"],
                    exact_w=truth["history"],
                )
                for defect in next_hi - instantaneous_i:
                    self.assertLessEqual(endpoint(defect, 0), 0)
                    self.assertGreaterEqual(endpoint(defect, 1), 0)
                if candidate == "A":
                    nxt, ni = evaluate(
                        self.target,
                        candidate,
                        "RG2b",
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
                        off, oi = evaluate(
                            self.target,
                            candidate,
                            "RG2b",
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
        self.assertEqual(len(effects), 26)
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
                            probe, _ = evaluate(
                                self.source, candidate, "RG2b", c, w, None
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

    def test_section_consumer_ownership_and_substitution(self):
        raw = numerical.ordinary
        for candidate in ("A", "C"):
            event, _ = self.event(candidate, "reset")
            c, w = event["c"], event["w"]
            saved_c, saved_w = c.copy(), None if w is None else w.copy()
            for operand in ["C", "W"] if candidate == "A" else ["C"]:

                def shifted(model, candidate, cc, ww=None, operand=operand):
                    (cc if operand == "C" else ww)[:] += (
                        0.125 if operand == "C" else 2**-20
                    )
                    return raw(model, candidate, cc, ww)

                with (
                    patch.object(numerical, "ordinary", side_effect=shifted),
                    self.assertRaises(ValueError),
                ):
                    evaluate(self.target, candidate, "RG2b", c, w, None)
                np.testing.assert_array_equal(c, saved_c)
                if w is not None:
                    np.testing.assert_array_equal(w, saved_w)

            def scratch(model, candidate, cc, ww=None):
                result = raw(model, candidate, cc, ww)
                cc.fill(0)
                if ww is not None:
                    ww.fill(0)
                return result

            with patch.object(numerical, "ordinary", side_effect=scratch):
                evaluate(self.target, candidate, "RG2b", c, w, None)
            np.testing.assert_array_equal(c, saved_c)
            if w is not None:
                np.testing.assert_array_equal(w, saved_w)
            good = raw(
                self.target, candidate, c.copy(), None if w is None else w.copy()
            )
            source_c, source_w = self.initial(candidate, "reset")
            source_chain = raw(self.source, candidate, source_c, source_w)[2]["chain"]
            for mode in ("wrong_chain", "source_chain", "identity_geometry", "current"):
                bad = copy.deepcopy(good)
                if mode == "wrong_chain":
                    bad[2]["chain"].x[-1][-1] += 0.01
                elif mode == "source_chain":
                    bad[2]["chain"] = copy.deepcopy(source_chain)
                elif mode == "identity_geometry":
                    bad[2]["H"] = self.target.I.copy()
                else:
                    bad[2]["read"]["J"][-1] += 0.125
                with (
                    patch.object(numerical, "ordinary", return_value=bad),
                    self.assertRaises(ValueError),
                ):
                    evaluate(self.target, candidate, "RG2b", c, w, None)

    def test_recipe_and_consumed_model_binding(self):
        for field, value in (
            ("profiles", ["A_OS", "C_OS"]),
            ("completion", "identity"),
            ("Z", []),
            ("carrier_information_loss", ["carrier_history_loss"]),
        ):
            bad = copy.deepcopy(self.case)
            bad[field] = value
            with self.assertRaisesRegex(ValueError, "RG input recipe"):
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

            probe = type("RGSetupProbe", (RGEventCompanionTests,), {})
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
            ref = reference_current(self.source, candidate, "RG2b", c, w, None)

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
                    "continuation": RGEventCompanionTests.continuation_report,
                    "effects": RGEventCompanionTests.effect_report,
                },
                indent=2,
            )
        )
    sys.exit(not result.result.wasSuccessful())
