"""A_OS research event: exact old-edge W lineage and positive bond seeds.

Reuses the accepted graph/charge construction and OS arithmetic. This is not
the history-free GRC9V3 initializer, a native event planner or a new profile.
"""

import copy
import json
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np
import test_p980_event_companion as common
from test_p980_os_effect_witness import (
    HISTORY_OFFSET,
    HISTORY_RADIUS,
    HISTORY_ROUND_BUDGET,
    IV,
    PARAMS,
    RESOURCE_RADIUS,
    RESOURCE_ROUND_BUDGET,
    SPLIT_TOLERANCE,
    IntervalRows,
    bounds,
    check_geometry_stages,
    endpoint,
    full_error,
    inflate,
    number,
    separation,
    split_admitted,
    staged_write,
    upper_abs,
    vector,
)

INPUT_PATH = (
    Path(__file__).resolve().parents[1] / "tranche-8/P9-8.0-AOS-ConstructionInputs.json"
)
require = common.require


def validate_inputs(case, shared):
    common.validate_inputs(shared)
    require(
        case["research_case_id"] == "P9-8.0-A_OS-SOURCE-D52-POSITIVE-PHASE-3"
        and case["candidate"] == "A"
        and case["realization"] == "OS",
        "A_OS binding mismatch",
    )
    require(
        case["shared_input_record"] == common.INPUT_PATH.name, "shared input mismatch"
    )
    require(
        case["shared_fields"]
        == [
            "identity_scope",
            "topology_fixture",
            "request",
            "source_graph",
            "expected_target_roles",
            "unit_vertex_measure",
            "geometry",
            "ordinary",
            "roles",
            "resource_initial_radius",
        ],
        "shared scope mismatch",
    )
    require(
        case["parameters"]
        == {
            "eta": "1",
            "kappa_c": "1",
            "kappa_Ah": str(bounds.KAPPA_AH),
            "kappa_H": str(bounds.KAPPA_H),
            "alpha_A": str(PARAMS.coefficient),
            "beta_A": str(PARAMS.coefficient),
            "gamma_A": str(PARAMS.coefficient),
            "chi_A": str(PARAMS.chi_a),
            "zeta_A": str(PARAMS.zeta_a),
            "W_floor": "1/2",
            "tau_A": "1",
            "site_potential": "zero",
            "external_forcing": "zero",
            "K4_base": "zero",
        },
        "A parameters mismatch",
    )
    require(
        case["row_detection"]
        == {**shared["row_detection"], "weights": "committed_postbeat_W_A"},
        "A row stage mismatch",
    )
    require(
        case["source_W"]
        == {
            role: {
                e["edge_id"]: str(1 - HISTORY_OFFSET)
                for e in shared["source_graph"]["edges"]
            }
            for role in ("current", "reset")
        },
        "supplied source W mismatch",
    )
    require(
        Q(case["history_initial_radius"]) == HISTORY_RADIUS, "history radius mismatch"
    )
    require(
        case["event_history"]
        == {
            "policy": "exact_old_edge_lineage_and_positive_bond_seed",
            "old_edges": "copy_role_event_entry_W_by_stable_edge_id",
            "new_edges": "event_bond_seed",
            "whole_target_history_free_initializer": False,
            "candidate_information_loss": [],
        },
        "A event history policy mismatch",
    )
    require(
        case["reference_current"]
        == {
            "source_stage": "fresh_role_event_entry_OS_corrector_read",
            "old_edges": "preserve_signed_source_current_by_stable_edge_id",
            "new_edges": "exact_zero",
            "used_to_initialize_W": False,
        },
        "reference-current recipe mismatch",
    )
    require(
        case["carrier_history"] == "not_applicable"
        and case["Z"] is None
        and case["carrier_information_loss"] == [],
        "A_OS carrier mismatch",
    )


def build_models(shared):
    return common.models(shared)


def checked_os(model, c, w, ci=None, wi=None):
    """Entry-owned complete OS step/read, with independent point and tube laws."""
    c, w = np.array(c, copy=True), np.array(w, copy=True)
    require(
        c.shape == (len(model.nodes),)
        and w.shape == (len(model.edges),)
        and np.isfinite(c).all()
        and np.isfinite(w).all()
        and np.all(w > 0),
        "invalid A input",
    )
    high = IntervalRows(model)
    exact_c, exact_w, exact = high.ordinary_os("A", vector(c), vector(w))
    if ci is None and wi is None:
        tube_c, tube_w, tube = exact_c, exact_w, exact
    else:
        require(
            ci is not None and wi is not None, "both exact input enclosures required"
        )
        tube_c, tube_w, tube = high.ordinary_os("A", ci.copy(), wi.copy())
    after, wn, stages = model.ordinary_os("A", c.copy(), w.copy())
    check_geometry_stages(stages, len(model.edges))
    errors = {
        "resource": full_error(after, exact_c),
        "history": full_error(wn, exact_w),
        "current": full_error(stages["read"]["J"], exact["read"]["J"]),
    }
    require(
        errors["resource"] < RESOURCE_ROUND_BUDGET
        and errors["history"] < HISTORY_ROUND_BUDGET
        and errors["current"] < Q(1, 2**40),
        "A evaluation error relative to entry input unresolved",
    )
    require(
        split_admitted(stages["H"], stages["regenerated"], model.I, SPLIT_TOLERANCE),
        "A represented split rejected",
    )
    require(
        tube["split_bound"] < SPLIT_TOLERANCE
        and tube["geometry_bound"] < Q(1, 2)
        and tube["read"]["regularity"] > Q(1, 2),
        "A interval admission unresolved",
    )
    return (
        {"c": after, "w": wn, "stages": stages},
        {"c": exact_c, "w": exact_w, "stages": exact},
        {"c": tube_c, "w": tube_w, "stages": tube},
        errors,
    )


def checked_counterfactual_writer(model, c, w, j):
    """Certify the writer at saved point operands, allowing private scratch writes.

    Composed effects retain their own intended-exact reference, constructed by
    the caller before this producer runs. It need not contain rounded points.
    """
    c, w, j = (np.array(a, dtype=float, copy=True) for a in (c, w, j))
    require(
        c.shape == (len(model.nodes),)
        and w.shape == j.shape == (len(model.edges),)
        and all(np.isfinite(a).all() for a in (c, w, j))
        and np.all(w > 0),
        "invalid counterfactual writer input",
    )
    expected = IntervalRows(model).write(vector(c), vector(w), vector(j))
    result = staged_write(model, c.copy(), w.copy(), j.copy())
    require(
        full_error(result, expected) < HISTORY_ROUND_BUDGET,
        "counterfactual writer error relative to entry input unresolved",
    )
    return result


def advance(model, c, w, ci, wi):
    out, _exact, tube, errors = checked_os(model, c, w, ci, wi)
    cn, wn = (
        inflate(tube["c"], RESOURCE_ROUND_BUDGET),
        inflate(tube["w"], HISTORY_ROUND_BUDGET),
    )
    for point, enclosure in ((out["c"], cn), (out["w"], wn)):
        require(
            all(
                endpoint(x, 0) <= Q(float(y)) <= endpoint(x, 1)
                for y, x in zip(point, enclosure, strict=True)
            ),
            "A point left enclosure",
        )
    return out, cn, wn, errors


def history_embedding(source, target):
    """Exact edge-ID embedding; its old-edge projection is a left inverse."""
    ids = {edge["edge_id"]: j for j, edge in enumerate(source.edges)}
    rows, seed = [], []
    for edge in target.edges:
        key = edge["edge_id"]
        rows.append([Q(key == old["edge_id"]) for old in source.edges])
        seed.append(Q(key not in ids))
    require(
        all(sum(row[j] for row in rows) == 1 for j in range(len(source.edges))),
        "W lineage is not injective",
    )
    return rows, seed


def produce_event(case, shared, c, w, reference):
    resources = common.produce_target(shared, c)["resources"]
    ids = [edge["edge_id"] for edge in shared["expected_target_roles"]["edges"]]
    return {
        "resources": resources,
        "W": {
            edge: w[edge] if edge in w else float(Q(shared["request"]["bond_seed"]))
            for edge in ids
        },
        "reference_current": {edge: reference.get(edge, 0.0) for edge in ids},
        "candidate_history": case["event_history"]["policy"],
        "candidate_information_loss": [],
        "Z": None,
        "carrier_history": "not_applicable",
        "carrier_information_loss": [],
    }


def checked_event(case, shared, source, target, c, w, reference):
    validate_inputs(case, shared)
    # Verifier records and operands never alias constructor/producer work data.
    cs, ws, refs = dict(c), dict(w), dict(reference)
    source_ids = {edge["edge_id"] for edge in source.edges}
    require(
        set(cs) == set(source.nodes)
        and set(ws) == source_ids
        and set(refs) == source_ids,
        "event source keys mismatch",
    )
    # Bind the supplied source reference channel to this role's fresh entry
    # state, not just to another copy of a caller-supplied vector.
    reference_truth = IntervalRows(source).ordinary_os(
        "A",
        vector([cs[n] for n in source.nodes]),
        vector([ws[edge["edge_id"]] for edge in source.edges]),
    )[2]["read"]["J"]
    require(
        full_error(
            np.array([refs[edge["edge_id"]] for edge in source.edges]), reference_truth
        )
        < Q(1, 2**40),
        "source reference-current recipe mismatch",
    )
    out = produce_event(
        copy.deepcopy(case), copy.deepcopy(shared), dict(cs), dict(ws), dict(refs)
    )
    target_ids = [edge["edge_id"] for edge in target.edges]
    require(
        set(out["resources"]) == set(target.nodes)
        and set(out["W"]) == set(target_ids)
        and set(out["reference_current"]) == set(target_ids),
        "event target keys mismatch",
    )
    matrix = common.transfer_matrix(source, target)
    exact_c = [
        sum(row[j] * Q(cs[n]) for j, n in enumerate(source.nodes)) for row in matrix
    ]
    cnew = target.vector(out["resources"])
    error = full_error(cnew, vector(exact_c))
    require(error < RESOURCE_ROUND_BUDGET, "event resource error unresolved")
    for n in target.nodes:
        if n == "core" or n.startswith("extra/"):
            require(out["resources"][n] == 0, "event zero changed")
        elif n.startswith("outside-"):
            require(out["resources"][n] == cs[n], "event exterior changed")
    embedding, seed = history_embedding(source, target)
    exact_w = [
        sum(row[j] * Q(ws[e["edge_id"]]) for j, e in enumerate(source.edges)) + b
        for row, b in zip(embedding, seed, strict=True)
    ]
    exact_ref = [
        sum(row[j] * Q(refs[e["edge_id"]]) for j, e in enumerate(source.edges))
        for row in embedding
    ]
    wnew = np.array([out["W"][edge] for edge in target_ids])
    rnew = np.array([out["reference_current"][edge] for edge in target_ids])
    require(
        wnew.shape == (len(target.edges),)
        and np.isfinite(wnew).all()
        and all(Q(float(x)) == y for x, y in zip(wnew, exact_w, strict=True)),
        "exact W lineage/seed mismatch",
    )
    require(
        rnew.shape == (len(target.edges),)
        and np.isfinite(rnew).all()
        and all(Q(float(x)) == y for x, y in zip(rnew, exact_ref, strict=True)),
        "reference-current lineage mismatch",
    )
    require(
        out["candidate_history"] == "exact_old_edge_lineage_and_positive_bond_seed"
        and out["candidate_information_loss"] == []
        and out["Z"] is None
        and out["carrier_history"] == "not_applicable"
        and out["carrier_information_loss"] == [],
        "event history channels mismatch",
    )
    charge = abs(sum(Q(float(x)) for x in cnew) - sum(Q(v) for v in cs.values()))
    require(charge <= len(target.nodes) * error, "event charge error unresolved")
    return (
        cnew,
        wnew,
        rnew,
        {"resource_error": float(error), "charge_error": float(charge)},
    )


class AEventCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(INPUT_PATH.read_text())
        cls.shared = json.loads(common.INPUT_PATH.read_text())
        validate_inputs(cls.case, cls.shared)
        cls.source, cls.target = build_models(copy.deepcopy(cls.shared))
        common.assert_model_binding(cls.shared, "source_graph", cls.source)
        common.assert_model_binding(cls.shared, "expected_target_roles", cls.target)

    def initial(self, role):
        c = self.source.vector(
            {
                n: Q(v)
                for n, v in self.shared["roles"][role]["initial_resources"].items()
            }
        )
        w = np.array(
            [
                float(Q(self.case["source_W"][role][e["edge_id"]]))
                for e in self.source.edges
            ]
        )
        return c, w

    def test_input_binding_and_actual_model_guard(self):
        for key, field, value in (
            ("event_history", "whole_target_history_free_initializer", True),
            ("reference_current", "source_stage", "stale_source_read"),
            ("row_detection", "weights", "unit_reference"),
            ("parameters", "alpha_A", "0"),
        ):
            bad = copy.deepcopy(self.case)
            bad[key][field] = value
            with self.assertRaises(ValueError):
                validate_inputs(bad, self.shared)
        constructor = build_models
        for mode in ("ports", "parameters", "mask"):

            def corrupt(shared, mode=mode):
                source, target = constructor(shared)
                if mode == "ports":
                    target.edges[0]["tail"]["port"] = 5
                    target.edges[0]["head"]["port"] = 5
                elif mode == "parameters":
                    target.params = replace(target.params, chi_a=2 * PARAMS.chi_a)
                else:
                    target.mask[-1, -1] = 0
                return source, target

            probe = type("ASetupProbe", (AEventCompanionTests,), {})
            with (
                patch(__name__ + ".build_models", side_effect=corrupt),
                self.assertRaisesRegex(ValueError, "consumed model"),
            ):
                probe.setUpClass()
            self.assertEqual(probe.shared, self.shared)

    def test_event_consumer_preserves_nonuniform_history_and_rejects_substitutions(
        self,
    ):
        c, w = self.initial("reset")
        cs = dict(zip(self.source.nodes, map(float, c), strict=True))
        ids = [e["edge_id"] for e in self.source.edges]
        # Within the source W neighborhood; this exposes swaps hidden by a
        # uniform seed. Reference currents are reconstructed on this input.
        ws = {
            edge: float(Q(float(w[j])) + (j - 4) * Q(1, 2**40))
            for j, edge in enumerate(ids)
        }
        read, _, _, _ = checked_os(self.source, c, np.array([ws[edge] for edge in ids]))
        refs = dict(zip(ids, map(float, read["stages"]["read"]["J"]), strict=True))
        saved = copy.deepcopy((cs, ws, refs))
        wrong_reference = {edge: -value for edge, value in refs.items()}
        with self.assertRaisesRegex(ValueError, "source reference-current recipe"):
            checked_event(
                self.case,
                self.shared,
                self.source,
                self.target,
                cs,
                ws,
                wrong_reference,
            )
        checked_event(self.case, self.shared, self.source, self.target, cs, ws, refs)
        raw = produce_event
        mutations = []
        good = raw(self.case, self.shared, cs, ws, refs)
        for field, key, value in (
            ("W", "old-1", 1.0),
            ("W", "internal/1", 0.9),
            ("reference_current", "internal/1", 0.125),
            ("reference_current", "old-9", 0.0),
            ("resources", "core", 0.125),
        ):
            bad = copy.deepcopy(good)
            bad[field][key] = value
            mutations.append(bad)
        bad = copy.deepcopy(good)
        bad["W"]["old-1"], bad["W"]["old-9"] = bad["W"]["old-9"], bad["W"]["old-1"]
        mutations.append(bad)
        for field, value in (
            ("Z", [[0.0]]),
            ("candidate_information_loss", ["history_loss"]),
            ("candidate_history", "full_target_history_free"),
            ("carrier_history", "reset"),
        ):
            bad = copy.deepcopy(good)
            bad[field] = value
            mutations.append(bad)
        bad = copy.deepcopy(good)
        del bad["W"]["old-9"]
        mutations.append(bad)
        for bad in mutations:
            with (
                patch(__name__ + ".produce_event", return_value=bad),
                self.assertRaises(ValueError),
            ):
                checked_event(
                    self.case, self.shared, self.source, self.target, cs, ws, refs
                )
        for operand in ("C", "W", "J"):

            def shifted(case, shared, c, w, reference, operand=operand):
                if operand == "C":
                    c["source-s"] += 0.125
                elif operand == "W":
                    w["old-9"] += 0.125
                else:
                    reference["old-9"] += 0.125
                return raw(case, shared, c, w, reference)

            with (
                patch(__name__ + ".produce_event", side_effect=shifted),
                self.assertRaises(ValueError),
            ):
                checked_event(
                    self.case, self.shared, self.source, self.target, cs, ws, refs
                )
        self.assertEqual((cs, ws, refs), saved)
        self.assertEqual(len(mutations), 11)

    def test_step_and_read_input_ownership(self):
        c, w = self.initial("current")
        saved_c, saved_w = c.copy(), w.copy()
        raw = self.source.ordinary_os
        for operand in ("C", "W"):

            def shifted(candidate, c, w, operand=operand):
                if operand == "C":
                    c[0] += 0.125
                else:
                    w[-1] += 0.125
                return raw(candidate, c, w)

            with (
                patch.object(self.source, "ordinary_os", side_effect=shifted),
                self.assertRaisesRegex(ValueError, "entry input"),
            ):
                checked_os(self.source, c, w)
            np.testing.assert_array_equal(c, saved_c)
            np.testing.assert_array_equal(w, saved_w)

        def scratch(candidate, c, w):
            out = raw(candidate, c, w)
            c.fill(0)
            w.fill(0)
            return out

        with patch.object(self.source, "ordinary_os", side_effect=scratch):
            checked_os(self.source, c, w)
        np.testing.assert_array_equal(c, saved_c)
        np.testing.assert_array_equal(w, saved_w)

    def test_counterfactual_writer_input_ownership(self):
        raw = staged_write
        for role in ("current", "reset"):
            c, w = self.initial(role)
            if role == "current":
                out = checked_os(self.source, c, w)[0]
                c, w = out["c"], out["w"]
            reference = checked_os(self.source, c, w)[0]["stages"]["read"]["J"]
            ids = [edge["edge_id"] for edge in self.source.edges]
            c, w, _, _ = checked_event(
                self.case,
                self.shared,
                self.source,
                self.target,
                dict(zip(self.source.nodes, map(float, c), strict=True)),
                dict(zip(ids, map(float, w), strict=True)),
                dict(zip(ids, map(float, reference), strict=True)),
            )
            on = checked_os(self.target, c, w)[0]
            for mode in ("baseline_current", "stale_resource"):
                cp = on["c"] if mode == "baseline_current" else c
                jp = on["stages"]["read"][
                    "baseline" if mode == "baseline_current" else "J"
                ]
                saved = tuple(a.copy() for a in (cp, w, jp))
                expected = raw(self.target, cp.copy(), w.copy(), jp.copy())
                np.testing.assert_array_equal(
                    checked_counterfactual_writer(self.target, cp, w, jp), expected
                )
                for operand in ("C", "W", "J"):

                    def shifted(model, cc, ww, jj, operand=operand):
                        inputs = {"C": cc, "W": ww, "J": jj}
                        inputs[operand][:] += 2**-20 if operand == "W" else 0.125
                        return raw(model, cc, ww, jj)

                    with (
                        self.subTest(role=role, mode=mode, operand=operand),
                        patch(__name__ + ".staged_write", side_effect=shifted),
                        self.assertRaisesRegex(
                            ValueError, "writer error relative to entry"
                        ),
                    ):
                        checked_counterfactual_writer(self.target, cp, w, jp)
                    for actual, original in zip((cp, w, jp), saved, strict=True):
                        np.testing.assert_array_equal(actual, original)

                def scratch(model, cc, ww, jj):
                    out = raw(model, cc, ww, jj)
                    for a in (cc, ww, jj):
                        a.fill(0)
                    return out

                with patch(__name__ + ".staged_write", side_effect=scratch):
                    np.testing.assert_array_equal(
                        checked_counterfactual_writer(self.target, cp, w, jp), expected
                    )
                for actual, original in zip((cp, w, jp), saved, strict=True):
                    np.testing.assert_array_equal(actual, original)

    def test_effect_consumer_rejects_writer_input_mutation(self):
        raw = staged_write

        def shifted(model, c, w, j):
            w += 2**-20
            return raw(model, c, w, j)

        with (
            patch(__name__ + ".staged_write", side_effect=shifted) as producer,
            self.assertRaisesRegex(ValueError, "writer error relative to entry"),
        ):
            self.test_both_role_lineage_continuation_and_history_effects()
        self.assertEqual(producer.call_count, 1)

    def test_both_role_lineage_continuation_and_history_effects(self):
        source, target = self.source, self.target
        p = IV.matrix(
            [[number(x) for x in row] for row in common.transfer_matrix(source, target)]
        )
        embedding, seed = history_embedding(source, target)
        e = IV.matrix([[number(x) for x in row] for row in embedding])
        reports, effects, entries = {}, {}, {}
        for role in ("current", "reset"):
            c, w = self.initial(role)
            ci = vector(
                [
                    Q(self.shared["roles"][role]["initial_resources"][n])
                    for n in source.nodes
                ],
                RESOURCE_RADIUS,
            )
            wi = vector(
                [
                    Q(self.case["source_W"][role][edge["edge_id"]])
                    for edge in source.edges
                ],
                HISTORY_RADIUS,
            )
            initial_c, initial_w = c.copy(), w.copy()
            if role == "current":
                out, ci, wi, _ = advance(source, c, w, ci, wi)
                c, w = out["c"], out["w"]
                rows = IntervalRows(source).rows(ci, wi)[source.index["source-s"]]
                self.assertTrue(all(endpoint(x, 0) > 0 for x in rows))
                self.assertLess(sum(upper_abs(x) ** 2 for x in rows), Q(1, 4))
            # Explicit reference recipe: fresh read of this role's event-entry
            # state. Discard the hypothetical update; reset is never advanced.
            reference, _ref_exact, _, _ = checked_os(source, c, w, ci, wi)
            source_ref = reference["stages"]["read"]["J"]
            cs = dict(zip(source.nodes, map(float, c), strict=True))
            ws = dict(
                zip(
                    (edge["edge_id"] for edge in source.edges),
                    map(float, w),
                    strict=True,
                )
            )
            refs = dict(
                zip(
                    (edge["edge_id"] for edge in source.edges),
                    map(float, source_ref),
                    strict=True,
                )
            )
            c, w, jref, event = checked_event(
                self.case, self.shared, source, target, cs, ws, refs
            )
            ci = p * ci
            wi = e * wi + vector(seed)
            for n in target.nodes:
                if n.startswith("satellite/"):
                    k = target.index[n]
                    ci[k] = inflate(IV.matrix([ci[k]]), RESOURCE_ROUND_BUDGET)[0]
                elif n == "core" or n.startswith("extra/"):
                    self.assertEqual(
                        (
                            endpoint(ci[target.index[n]], 0),
                            endpoint(ci[target.index[n]], 1),
                        ),
                        (0, 0),
                    )
            for point, interval in ((c, ci), (w, wi)):
                self.assertTrue(
                    all(
                        endpoint(x, 0) <= Q(float(y)) <= endpoint(x, 1)
                        for y, x in zip(point, interval, strict=True)
                    )
                )
            first_c, first_w = c.copy(), w.copy()
            entries[role] = w.copy()
            first, _first_exact, _, _ = checked_os(target, c, w, ci, wi)
            for k, edge in enumerate(target.edges):
                if edge["edge_id"].startswith("internal/"):
                    self.assertEqual(w[k], 1)
                    self.assertEqual(jref[k], 0)
                    self.assertGreater(abs(first["stages"]["read"]["J"][k]), 1e-4)
            # Full W lineage is recoverable by the nine stable source IDs.
            lookup = {edge["edge_id"]: i for i, edge in enumerate(target.edges)}
            self.assertEqual(
                [w[lookup[edge["edge_id"]]] for edge in source.edges],
                [ws[edge["edge_id"]] for edge in source.edges],
            )
            steps = []
            for _ in range(bounds.HORIZON):
                out, ci, wi, errors = advance(target, c, w, ci, wi)
                c, w = out["c"], out["w"]
                low = min(endpoint(x, 0) for x in ci)
                whi = max(endpoint(x, 1) for x in wi)
                wlo = min(endpoint(x, 0) for x in wi)
                self.assertGreater(low, bounds.RESOURCE_MARGIN / 2)
                self.assertLess(max(endpoint(x, 1) for x in ci), 4)
                self.assertGreater(wlo, Q(99, 100))
                self.assertLess(whi, Q(1001, 1000))
                steps.append(
                    {
                        "resource_lower": float(low),
                        "W_lower": float(wlo),
                        "W_upper": float(whi),
                        **{k + "_error": float(v) for k, v in errors.items()},
                    }
                )
            _, _, _, final_errors = checked_os(target, c, w, ci, wi)
            reports[role] = {
                "event": event,
                "initial_W": list(map(float, first_w)),
                "reference_current": list(map(float, jref)),
                "steps": steps,
                "final_current_error": float(final_errors["current"]),
            }
            if role == "current":
                # Preserve the original OS named-stage effect scope.
                for label, model, cp, wp in (
                    ("source", source, initial_c, initial_w),
                    ("target", target, first_c, first_w),
                ):
                    on, truth, _, _ = checked_os(model, cp, wp)
                    high = IntervalRows(model)
                    for name, flags in (
                        ("geometry", {"geometry": False}),
                        ("readback", {"feedback": False}),
                    ):
                        offi = high.read(
                            "A", vector(cp), vector(wp), truth["stages"]["H"], **flags
                        )
                        off = model.read(
                            "A", cp.copy(), wp.copy(), on["stages"]["H"].copy(), **flags
                        )
                        self.assertLess(full_error(off["J"], offi["J"]), Q(1, 2**40))
                        effects[label + "_" + name] = separation(
                            on["stages"]["read"]["J"],
                            off["J"],
                            truth["stages"]["read"]["J"],
                            offi["J"],
                        )
                on, truth, _, _ = checked_os(target, first_c, first_w)
                high = IntervalRows(target)
                for mode in ("baseline_current", "stale_resource"):
                    # Preserve the composed intended-exact branch before the
                    # represented writer; its point-error guard is separate.
                    wci = high.write(
                        truth["c"] if mode == "baseline_current" else vector(first_c),
                        vector(first_w),
                        truth["stages"]["read"]["baseline"]
                        if mode == "baseline_current"
                        else truth["stages"]["read"]["J"],
                    )
                    wc = checked_counterfactual_writer(
                        target,
                        on["c"] if mode == "baseline_current" else first_c,
                        first_w,
                        on["stages"]["read"]["baseline"]
                        if mode == "baseline_current"
                        else on["stages"]["read"]["J"],
                    )
                    effects[mode + "_W"] = separation(on["w"], wc, truth["w"], wci)
                    nxt, _, nxt_t, _ = checked_os(
                        target, on["c"], on["w"], truth["c"], truth["w"]
                    )
                    off, _, off_t, _ = checked_os(target, on["c"], wc, truth["c"], wci)
                    # The supplied exact operands can exclude the rounded point;
                    # use the tube results for this composed-error comparison.
                    effects[mode + "_next_J"] = separation(
                        nxt["stages"]["read"]["J"],
                        off["stages"]["read"]["J"],
                        nxt_t["stages"]["read"]["J"],
                        off_t["stages"]["read"]["J"],
                    )
        self.assertFalse(np.array_equal(entries["current"], entries["reset"]))
        self.assertEqual(len(effects), 8)
        type(self).report = {"roles": reports, "effects": effects}


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(json.dumps(getattr(AEventCompanionTests, "report", {}), indent=2))
    sys.exit(not result.result.wasSuccessful())
