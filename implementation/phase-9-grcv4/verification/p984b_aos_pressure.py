"""Focused scientific pressure on A_OS oracle expectations, not native runtime.

Keep the sixteen-case campaign immutable. Wrong-law controls are independently
evaluated, not arbitrary output offsets. Boundary probes have their own saved
inputs and are never promoted to admitted profile/event identities.
"""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
from importlib.metadata import version
import json
import math
import platform
import unittest

import numpy as np
import p984b_aos_oracle as oracle
from test_p980_os_effect_witness import infinity, number

common, aos = oracle.common, oracle.aos
SELF = common.HERE + "p984b_aos_pressure.py"
TEST = common.HERE + "test_p984b_aos_pressure.py"
RECORD = common.BASE + "P9-8.4b-AOSScientificPressure.json"
MODES = (
    "stale_predictor_current",
    "corrector_readback_disabled",
    "frozen_history",
    "writer_uses_incoming_C",
    "writer_uses_predictor_J",
    "regeneration_reuses_predictor_geometry",
)


def flat(value):
    return np.asarray(value, dtype=float).reshape(-1).tolist()


def represented(value):
    return list(map(float, value))


def stages(graph, state):
    c, w = state["C"], state["W_A"]
    common.require(
        len(c) == len(graph["live_node_ids"])
        and len(w) == len(graph["edges"])
        and all(math.isfinite(x) and x >= 0 for x in c)
        and all(math.isfinite(x) and x > 0 for x in w),
        "invalid pressure entry resources/history",
    )
    model = aos.StagedRows(graph["live_node_ids"], graph["edges"], aos.PARAMS)
    high = aos.IntervalRows(model)
    ci, wi = aos.vector(c), aos.vector(w)
    cn, wn, s = high.ordinary_os("A", ci, wi)
    return high, ci, wi, cn, wn, s


def exact_abs_lower(value):
    return max(aos.endpoint(value, 0), -aos.endpoint(value, 1), Q(0))


def compare_control(enabled, wrong, exact_enabled, exact_wrong, budget):
    """Separate wrong-law error, representability and the frozen error budget."""
    e, w = flat(enabled), flat(wrong)
    truth, control = (
        aos.IV.matrix(list(exact_enabled)),
        aos.IV.matrix(list(exact_wrong)),
    )
    common.require(len(e) == len(w) == truth.rows == control.rows, "control shape")
    error_e = aos.full_error(e, truth)
    error_w = aos.full_error(w, control)
    mismatch = aos.full_error(w, truth)
    delta = max(abs(Q(x) - Q(y)) for x, y in zip(e, w, strict=True))
    exact_lower = max(
        exact_abs_lower(x - y) for x, y in zip(truth, control, strict=True)
    )
    ulp = max(Q(math.ulp(x)) for x in e + w)
    threshold = 4 * (error_e + error_w) + 8 * ulp
    # A failing upper-error enclosure is not itself a proof of a wrong value.
    # Retain a lower bound too: distance from each represented wrong coordinate
    # to the independent enabled-law interval.
    wrong_error_lower = max(
        exact_abs_lower(number(x) - y) for x, y in zip(w, truth, strict=True)
    )
    return {
        "enabled": e,
        "control": w,
        "enabled_full_error": str(error_e),
        "control_full_error": str(error_w),
        "exact_law_difference_lower": str(exact_lower),
        "represented_difference": str(delta),
        "effect_threshold_4_errors_plus_8_ulp": str(threshold),
        "effect_separated": delta > threshold,
        "control_error_against_enabled_upper": str(mismatch),
        "control_error_against_enabled_lower": str(wrong_error_lower),
        "frozen_budget": str(budget),
        "frozen_budget_rejects": mismatch >= budget,
        "wrong_value_proved_outside_budget": wrong_error_lower >= budget,
    }


def mechanism_pressure(case, role):
    graph = case["target"]["port_graph"]
    state = case["target"]["roles"][role]["authoritative"]
    paper = aos.PaperAOS(graph)
    c, w = state["C"], state["W_A"]
    prediction = oracle.evaluate(paper, state, "pressure_probe", role, 1)
    high, ci, wi, cn, wn, s = stages(graph, state)
    p = paper.read(c, w)
    h = paper.I + p["source"] / 2
    r = paper.read(c, w, h)
    next_c = paper.mp.matrix(c) - paper.mp.mpf(aos.DT) * paper.B * r["current"]
    truths = {
        "current": s["read"]["J"],
        "W_A": wn,
        "regenerated": high.I + s["read"]["source"] / 2,
    }
    variants = {
        "stale_predictor_current": ("current", p["current"], s["predictor"]["J"]),
        "corrector_readback_disabled": (
            "current",
            paper.read(c, w, h, feedback=False)["current"],
            high.read("A", ci, wi, s["H"], feedback=False)["J"],
        ),
        "frozen_history": ("W_A", w, wi),
        "writer_uses_incoming_C": (
            "W_A",
            paper.write(c, w, r["current"]),
            high.write(ci, wi, s["read"]["J"]),
        ),
        "writer_uses_predictor_J": (
            "W_A",
            paper.write(next_c, w, p["current"]),
            high.write(cn, wi, s["predictor"]["J"]),
        ),
        "regeneration_reuses_predictor_geometry": ("regenerated", h, s["H"]),
    }
    controls = {}
    for name, (field, value, exact) in variants.items():
        wrong = represented(value)
        enabled = flat(prediction["output"][field])
        result = compare_control(
            enabled, wrong, truths[field], exact, oracle.LIMITS[field]
        )
        result["field"] = field
        # Exercise the actual oracle gate, not just a reconstructed comparison.
        mutated = deepcopy(prediction["output"])
        mutated[field] = (
            np.array(wrong).reshape(np.asarray(mutated[field]).shape).tolist()
        )
        try:
            oracle.interval_certificate(graph, c, w, mutated)
            result["oracle_gate_rejected"] = False
            result["rejection"] = None
        except ValueError as exc:
            common.require(
                "full formula error exceeds bound: " + field in str(exc),
                "wrong-law control rejected for unrelated reason: " + str(exc),
            )
            result["oracle_gate_rejected"] = True
            result["rejection"] = str(exc)
        common.require(
            result["oracle_gate_rejected"] == result["frozen_budget_rejects"],
            "oracle gate/control comparison disagreement",
        )
        controls[name] = result
    return {
        "fixture_id": case["fixture_id"],
        "role": role,
        "entry": state,
        "enabled_certificate": prediction["certificate"],
        "controls": controls,
    }


def nearby_pressure(cases):
    rows = []
    for case in cases:
        graph = case["target"]["port_graph"]
        for role in oracle.ROLES:
            base = case["target"]["roles"][role]["authoritative"]
            for cs, ws in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                state = aos.authority(
                    [float(Q(x) * (1 + cs * Q(1, 2**10))) for x in base["C"]],
                    [float(Q(x) + ws * Q(1, 2**12)) for x in base["W_A"]],
                )
                result = oracle.evaluate(
                    aos.PaperAOS(graph), state, "nearby_probe", role, 1
                )
                rows.append(
                    {
                        "fixture_id": case["fixture_id"],
                        "role": role,
                        "resource_relative_shift": str(cs * Q(1, 2**10)),
                        "history_additive_shift": str(ws * Q(1, 2**12)),
                        "entry": state,
                        "certificate": result["certificate"],
                    }
                )
    return rows


def phase_one_share_controls(cases):
    """The old share recipe is tested as A, never inferred from C failures."""
    rows = []
    for case in cases:
        graph = case["target"]["port_graph"]
        for role in oracle.ROLES:
            state = deepcopy(case["target"]["roles"][role]["authoritative"])
            positions = [
                i for i, n in enumerate(graph["live_node_ids"]) if "/satellite/" in n
            ]
            total = sum(Q(state["C"][i]) for i in positions)
            for i, fraction in zip(positions, (Q(1, 2), Q(1, 4), Q(1, 4)), strict=True):
                state["C"][i] = float(total * fraction)
            high, _, _, cn, wn, s = stages(graph, state)
            negative_upper = min(aos.endpoint(x, 1) for x in cn)
            point = aos.PaperAOS(graph).step(state["C"], state["W_A"])
            rows.append(
                {
                    "fixture_id": case["fixture_id"],
                    "role": role,
                    "entry": state,
                    "shares": [0.5, 0.25, 0.25],
                    "C_min_upper": str(negative_upper),
                    "C_min_lower": str(min(aos.endpoint(x, 0) for x in cn)),
                    "W_min_lower": str(min(aos.endpoint(x, 0) for x in wn)),
                    "split_upper": str(s["split_bound"]),
                    "represented_C_min": min(point["C"]),
                    "proved_negative_resource": negative_upper < 0,
                    "identity_scope": "role_normalized_numeric_control_not_an_event",
                }
            )
    return rows


def interval_positive_definite(matrix):
    """Sufficient exact-real positivity via interval LDL, not float eigenvalues."""
    a = [[matrix[i, j] for j in range(matrix.cols)] for i in range(matrix.rows)]
    pivots = []
    for k in range(len(a)):
        pivot = a[k][k]
        if aos.endpoint(pivot, 0) <= 0:
            return False, pivots
        pivots.append(str(aos.endpoint(pivot, 0)))
        for i in range(k + 1, len(a)):
            for j in range(i, len(a)):
                a[i][j] -= a[i][k] * a[k][j] / pivot
                a[j][i] = a[i][j]
    return True, pivots


def split_probe(graph, state):
    high, _, _, cn, wn, s = stages(graph, state)
    defect = s["H"] - high.I - s["read"]["source"] / 2
    plus = interval_positive_definite(number(Q(aos.SPLIT)) * high.I + defect)
    minus = interval_positive_definite(number(Q(aos.SPLIT)) * high.I - defect)
    mid = np.array([[float(x.mid) for x in row] for row in defect.tolist()])
    values, directions = np.linalg.eigh(mid)
    direction = directions[:, int(np.argmax(np.abs(values)))].tolist()
    v = aos.vector(direction)
    rayleigh = (v.T * defect * v)[0] / (v.T * v)[0]
    lower = exact_abs_lower(rayleigh)
    point = aos.PaperAOS(graph).step(state["C"], state["W_A"])
    represented_pass = aos.split_admitted(
        point["H"], point["regenerated"], np.eye(len(graph["edges"])), Q(aos.SPLIT)
    )
    disposition = (
        "inside"
        if plus[0] and minus[0]
        else "outside"
        if lower > Q(aos.SPLIT)
        else "unresolved"
    )
    common.require(disposition != "unresolved", "split boundary enclosure unresolved")
    common.require(
        represented_pass == (disposition == "inside"),
        "represented/real split decisions diverge",
    )
    return {
        "entry": state,
        "disposition": disposition,
        "represented_split_admitted": represented_pass,
        "split_row_upper": str(infinity(defect)),
        "rayleigh_absolute_lower": str(lower),
        "rayleigh_direction": direction,
        "positive_pivots_plus": plus[1],
        "positive_pivots_minus": minus[1],
        "C_min_lower": str(min(aos.endpoint(x, 0) for x in cn)),
        "W_min_lower": str(min(aos.endpoint(x, 0) for x in wn)),
        "geometry_upper": str(s["geometry_bound"]),
        "regularity_lower": str(s["read"]["regularity"]),
    }


def split_boundary(case):
    """Bracket a genuine split rejection, retaining positive C/W and regular J."""
    graph = case["target"]["port_graph"]
    base = case["target"]["roles"]["current"]["authoritative"]

    def probe(offset):
        state = deepcopy(base)
        state["W_A"] = [
            float(1 - offset)
            if not e["edge_id"].startswith(case["event_id"] + "/")
            else 1.0
            for e in graph["edges"]
        ]
        value = split_probe(graph, state)
        value["old_edge_history_offset"] = str(offset)
        return value

    left, right = Q(1, 2**10), Q(1, 100)
    inside, outside = probe(left), probe(right)
    common.require(
        inside["disposition"] == "inside" and outside["disposition"] == "outside",
        "split initial bracket not established",
    )
    search = []
    for _ in range(12):
        midpoint = (left + right) / 2
        row = probe(midpoint)
        search.append({"offset": str(midpoint), "disposition": row["disposition"]})
        if row["disposition"] == "inside":
            left, inside = midpoint, row
        else:
            right, outside = midpoint, row
    return {
        "fixture_id": case["fixture_id"],
        "role": "current",
        "inside": inside,
        "outside": outside,
        "search": search,
        "offset_bracket_width": str(right - left),
        "scope": "two_certified_points_not_monotonicity_or_a_uniform_boundary_theorem",
    }


def resource_boundary(case):
    """Vary dt only after a fixed admitted read; frozen production dt unchanged."""
    graph = case["target"]["port_graph"]
    state = case["target"]["roles"]["current"]["authoritative"]
    high, ci, _, _, _, s = stages(graph, state)
    flux = high.B * s["read"]["J"]
    paper = aos.PaperAOS(graph)
    pred = paper.read(state["C"], state["W_A"])
    read = paper.read(state["C"], state["W_A"], paper.I + pred["source"] / 2)
    rate = paper.B * read["current"]
    critical = min(
        paper.mp.mpf(c) / q for c, q in zip(state["C"], rate, strict=True) if q > 0
    )
    rows = []
    for sign in (-1, 1):
        dt = float(critical * (1 + paper.mp.mpf(sign) / 2**20))
        after = ci - number(dt) * flux
        point = paper.mp.matrix(state["C"]) - paper.mp.mpf(dt) * rate
        rows.append(
            {
                "dt": dt,
                "side": "below" if sign < 0 else "above",
                "C_min_lower": str(min(aos.endpoint(x, 0) for x in after)),
                "C_min_upper": str(min(aos.endpoint(x, 1) for x in after)),
                "represented_C": represented(point),
                "full_C_error": str(aos.full_error(represented(point), after)),
            }
        )
    return {
        "fixture_id": case["fixture_id"],
        "entry": state,
        "fixed_dt": aos.DT,
        "point_estimate_critical_dt": float(critical),
        "probes": rows,
        "scope": "continuity_domain_only_no_writer_or_native_step_at_changed_dt",
    }


def floor_and_history_boundaries(case):
    graph = case["target"]["port_graph"]
    paper = aos.PaperAOS(graph)
    model = aos.StagedRows(graph["live_node_ids"], graph["edges"], aos.PARAMS)
    high = aos.IntervalRows(model)
    threshold = float(paper.mp.log(2) * 2**24)
    floor_rows = []
    for side, cvalue in (
        ("below", math.nextafter(threshold, -math.inf)),
        ("above", math.nextafter(threshold, math.inf)),
    ):
        c, w = [cvalue] * len(graph["live_node_ids"]), [1.0] * len(graph["edges"])
        smooth = aos.IV.exp(-number(cvalue) / 2**24)
        try:
            high.conductance(aos.vector(c), aos.vector(w), aos.vector([0] * len(w)))
            disposition = "certified_inactive_floor"
        except ValueError as exc:
            common.require("inactive-floor" in str(exc), "unexpected floor error")
            disposition = "outside_smooth_certificate"
        point = paper.read(c, w)
        floor_rows.append(
            {
                "side": side,
                "uniform_C": cvalue,
                "smooth_drive_lower": str(aos.endpoint(smooth, 0)),
                "smooth_drive_upper": str(aos.endpoint(smooth, 1)),
                "disposition": disposition,
                "clipped_drive": represented(point["drive"]),
                "current": represented(point["current"]),
            }
        )
    base = case["target"]["roles"]["current"]["authoritative"]
    tiny = aos.authority(base["C"], [2**-40] * len(graph["edges"]))
    tiny_row = oracle.evaluate(paper, tiny, "positive_history_probe", "current", 1)
    invalid = []
    for value in (0.0, -(2**-40)):
        state = deepcopy(tiny)
        state["W_A"][0] = value
        try:
            paper.read(state["C"], state["W_A"])
        except ValueError as exc:
            common.require("positive W" in str(exc), "unexpected history rejection")
        else:
            raise AssertionError("paper read admitted nonpositive W")
        try:
            high.rows(aos.vector(state["C"]), aos.vector(state["W_A"]))
        except ValueError as exc:
            common.require(
                "positive descriptor weights" in str(exc), "unexpected row rejection"
            )
        else:
            raise AssertionError("interval read admitted nonpositive W")
        invalid.append(
            {"W_first": value, "paper_rejected": True, "interval_rejected": True}
        )
    return {
        "fixture_id": case["fixture_id"],
        "floor": floor_rows,
        "tiny_positive_history": {
            "entry": tiny,
            "certificate": tiny_row["certificate"],
        },
        "nonpositive_history": invalid,
        "scope": "floor_clipped_law_is_valid_but_outside_this_inactive_floor_certificate",
    }


def sources():
    manifest = common.read(oracle.INPUTS)
    return sorted(
        {r["path"] for r in manifest["source_bindings"]}
        | {oracle.INPUTS, oracle.RESULTS, SELF, TEST}
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--output", default=RECORD)
    args = parser.parse_args()
    path = common.Path(args.output)
    common.require(
        not path.is_absolute() and ".." not in path.parts, "relative path required"
    )
    target = common.ROOT / path
    if args.check_retained:
        record = common.read(str(path))
        common.check_digest(record)
        common.check_bindings(record["source_bindings"])
        common.require(
            record["source_bindings"] == common.bind(sources()), "pressure roster drift"
        )
        common.require(
            record["tests"]["successful"]
            and record["tests"]["run"] == 8
            and record["tests"]["failures"]
            == record["tests"]["errors"]
            == record["tests"]["skips"]
            == 0
            and record["campaign_record_digest"]
            == common.read(oracle.RESULTS)["record_digest"]
            and set(record["evidence"])
            == {
                "mechanisms",
                "mechanism_summary",
                "nearby",
                "original_share_controls",
                "split_boundary",
                "resource_boundary",
                "floor_and_history",
                "zero_current_controls",
                "stage_consumption",
            }
            and not record["native_runtime_executed"]
            and not record["user_accepted"],
            "pressure disposition drift",
        )
        print(
            json.dumps(
                {
                    "retained_integrity": "passed",
                    "numerics_reexecuted": False,
                    "native_runtime_executed": False,
                },
                indent=2,
            )
        )
        return
    common.require(not target.exists(), "refusing to overwrite pressure evidence")
    from test_p984b_aos_pressure import EVIDENCE, ScientificPressureTests

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScientificPressureTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = common.seal(
        {
            "schema": "p984b-aos-scientific-pressure-v1",
            "source_bindings": common.bind(sources()),
            "campaign_record_digest": common.read(oracle.RESULTS)["record_digest"],
            "environment": {
                "python": platform.python_version(),
                "numpy": version("numpy"),
                "mpmath": version("mpmath"),
                "paper_digits": 100,
                "interval_digits": 60,
            },
            "tests": {
                "run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skips": len(result.skipped),
                "successful": result.wasSuccessful(),
            },
            "evidence": EVIDENCE,
            "native_runtime_executed": False,
            "user_accepted": False,
            "scope": "focused_wrong_law_and_domain_pressure_not_all_graphs_parameters_or_native_conformance",
        }
    )
    common.write_new(str(path), record)
    print(json.dumps(record["tests"], indent=2))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
