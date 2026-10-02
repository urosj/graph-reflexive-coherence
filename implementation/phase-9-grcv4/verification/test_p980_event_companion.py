"""Bounded C_OS event companion; research inputs, no native event planner.

The represented resource transfer is checked against an independent rational
matrix. Existing OS kernels certify the actual transferred states. Frozen
vectors supply topology only; no frozen numerical/event identity is reused.
"""

import copy
import json
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np
import test_p980_boundary_continuation as boundary
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    RESOURCE_RADIUS,
    RESOURCE_ROUND_BUDGET,
    SPLIT_TOLERANCE,
    IntervalRows,
    StagedRows,
    bounds,
    check_geometry_stages,
    endpoint,
    full_error,
    inflate,
    number,
    separation,
    split_admitted,
    upper_abs,
    vector,
)

INPUT_PATH = (
    Path(__file__).resolve().parents[1] / "tranche-8/P9-8.0-COS-ConstructionInputs.json"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_inputs(case):
    """Bind every supplied numerical/stage operand to the supported recipe."""
    require(
        case["candidate"] == "C" and case["realization"] == "OS",
        "C_OS binding required",
    )
    require(
        case["research_case_id"] == "P9-8.0-C_OS-SOURCE-D52-POSITIVE-PHASE-3",
        "research identity mismatch",
    )
    require(
        case["identity_scope"] == "research_role_names_without_native_event_namespace",
        "native identity is not supplied",
    )
    require(
        case["topology_fixture"] == boundary.D52_FIXTURE_ID, "topology fixture mismatch"
    )
    require(
        case["request"]
        == {
            "source_node_id": "source-s",
            "target_effective_degree": 52,
            "module_chirality": 1,
            "growth_phase": 3,
            "resource_distribution": ["1/3"] * 3,
            "bond_seed": "1",
        },
        "request scope mismatch",
    )
    boundary.BoundaryContinuationTests.setUpClass()
    frozen = boundary.BoundaryContinuationTests
    layout = boundary.enabled_d52_layout(frozen.layouts)
    edges, nodes = boundary.normalized_target(layout)
    require(
        case["source_graph"]
        == {"nodes": frozen.source["live_node_ids"], "edges": frozen.source["edges"]},
        "source graph mismatch",
    )
    require(
        case["expected_target_roles"] == {"nodes": sorted(nodes), "edges": edges},
        "target role transcript mismatch",
    )
    for graph_key, map_key in (
        ("source_graph", "source_reference_weights"),
        ("expected_target_roles", "target_reference_weights"),
    ):
        require(
            case[map_key] == {e["edge_id"]: "1" for e in case[graph_key]["edges"]},
            "complete unit C references required",
        )
    require(case["unit_vertex_measure"] == "1", "unit measure required")
    require(
        case["new_edge_incoming_reference_current"]
        == {e["edge_id"]: "0" for e in edges if e["edge_id"].startswith("internal/")},
        "new reference current must be zero",
    )
    require(
        case["parameters"]
        == {
            "eta_C": "1",
            "kappa_Phi_C": "1",
            "chi_C": str(PARAMS.chi_c),
            "zeta_C": str(PARAMS.zeta_c),
            "kappa_H": str(bounds.KAPPA_H),
            "kappa_M_C": str(bounds.KAPPA_M),
            "Lambda_C": "1/512",
            "C_ref": "1",
            "tau_C": "1",
            "site_potential": "zero",
            "external_forcing": "zero",
            "K4_base": "zero",
        },
        "C equation parameters mismatch",
    )
    require(
        case["geometry"]
        == {
            "reference": "identity",
            "star_cover": "vertex_stars",
            "overlap_weight": "1/sqrt(2)",
            "tensor_adapter": "identity",
            "source_mask_diagonal": "1",
            "source_mask_shared_vertex": "1/2",
            "source_mask_disjoint": "0",
        },
        "geometry recipe mismatch",
    )
    require(
        case["row_detection"]
        == {
            "frame": "fixed_port_chart",
            "backend": "row_basis_diagonal",
            "weights": "stable_edge_W_C_tr",
            "stage": "fresh_postbeat_candidate_detection",
            "hessian_sign": -1,
            "epsilon_gradient": "1/2",
            "epsilon_spark": "0",
        },
        "detection recipe mismatch",
    )
    require(
        case["ordinary"]
        == {
            "duration": str(bounds.DT),
            "target_steps": bounds.HORIZON,
            "source_current_steps": 1,
            "source_reset_steps": 0,
            "split_metric": "edge_l2_v1",
            "split_tolerance": str(SPLIT_TOLERANCE),
        },
        "ordinary stage mismatch",
    )
    source_nodes = case["source_graph"]["nodes"]
    for role, center in (("current", Q(3)), ("reset", Q(2))):
        desired = {
            n: center if n == "source-s" else center + bounds.OUTSIDE_OFFSET
            for n in source_nodes
        }
        initial = (
            bounds.preimage(case["source_graph"]["edges"], desired)
            if role == "current"
            else desired
        )
        require(
            case["roles"][role]["initial_resources"]
            == {n: str(initial[n]) for n in source_nodes},
            "role input mismatch",
        )
        require(
            case["roles"][role]["input_recipe"]
            == (
                "reference_preimage_center_3"
                if role == "current"
                else "independently_supplied_center_2"
            ),
            "role recipe mismatch",
        )
    require(set(case["roles"]) == {"current", "reset"}, "role population mismatch")
    require(
        Q(case["resource_initial_radius"]) == RESOURCE_RADIUS, "initial radius mismatch"
    )
    require(
        case["candidate_history"] == "rederived"
        and case["carrier_history"] == "not_applicable"
        and case["W"] is None
        and case["Z"] is None
        and case["information_loss"] == [],
        "C_OS history mismatch",
    )


def models(case):
    return tuple(
        StagedRows(case[key]["nodes"], case[key]["edges"], PARAMS)
        for key in ("source_graph", "expected_target_roles")
    )


def assert_model_binding(case, key, model):
    """EC-F1: independent assembly from validated inputs, not model fields."""
    graph = case[key]
    nodes, edges = tuple(graph["nodes"]), tuple(graph["edges"])
    require(
        tuple(model.nodes) == nodes and tuple(model.edges) == edges,
        "consumed model roles/ports differ from input record",
    )
    index = {node: i for i, node in enumerate(nodes)}
    require(
        model.index == index and model.params == PARAMS,
        "consumed model index/parameters differ from input record",
    )
    n, m = len(nodes), len(edges)
    require(
        len(index) == n and len({edge["edge_id"] for edge in edges}) == m,
        "duplicate model identifiers",
    )
    incidence = [[0] * m for _ in nodes]
    endpoints = []
    for j, edge in enumerate(edges):
        u, v = edge["tail"]["node_id"], edge["head"]["node_id"]
        incidence[index[u]][j] += 1
        incidence[index[v]][j] -= 1
        endpoints.append({u, v})
    gram = [
        [sum(incidence[k][i] * incidence[k][j] for k in range(n)) for j in range(m)]
        for i in range(m)
    ]
    identity = [[int(i == j) for j in range(m)] for i in range(m)]
    mask = [
        [
            1 if i == j else Q(1, 2) if endpoints[i] & endpoints[j] else 0
            for j in range(m)
        ]
        for i in range(m)
    ]
    for field, expected in (
        ("B", incidence),
        ("D", gram),
        ("I", identity),
        ("mask", mask),
    ):
        actual = np.asarray(getattr(model, field))
        wanted = np.asarray(expected, dtype=float)
        require(
            actual.shape == wanted.shape
            and actual.dtype.kind in "fiu"
            and np.isfinite(actual).all()
            and np.array_equal(actual, wanted),
            f"consumed model {field} differs from independent assembly",
        )


def checked_read_only(model, incoming, enclosure):
    """EC-F2: certify OS reconstruction against owned entry operands.

    The kernel's resource update is discarded, not counted as a physical beat.
    Intended-exact enclosures need not contain rounded point operands.
    """
    saved = np.array(incoming, dtype=float, copy=True)
    require(
        saved.shape == (len(model.nodes),) and np.isfinite(saved).all(),
        "invalid read input",
    )
    high = IntervalRows(model)
    truth = high.ordinary_os("C", vector(saved), None)[2]
    tube = high.ordinary_os("C", enclosure.copy(), None)[2]
    stages = model.ordinary_os("C", saved.copy(), None)[2]
    check_geometry_stages(stages, len(model.edges))
    error = full_error(stages["read"]["J"], truth["read"]["J"])
    require(
        error < Q(1, 2**40),
        "read-only current error relative to entry input unresolved",
    )
    require(
        tube["split_bound"] < SPLIT_TOLERANCE
        and tube["read"]["regularity"] > Q(1, 2)
        and tube["geometry_bound"] < Q(1, 2),
        "read-only tube admission unresolved",
    )
    require(
        split_admitted(stages["H"], stages["regenerated"], model.I, SPLIT_TOLERANCE),
        "read-only represented split rejected",
    )
    return stages, truth, error


def transfer_matrix(source, target):
    """Exact oracle coefficients, independent of represented division/dispatch."""
    matrix = [[Q(0) for _ in source.nodes] for _ in target.nodes]
    for node in source.nodes:
        if node != "source-s":
            matrix[target.index[node]][source.index[node]] = Q(1)
    for branch in range(1, 4):
        matrix[target.index[f"satellite/{branch}"]][source.index["source-s"]] = Q(1, 3)
    require(
        all(sum(row[j] for row in matrix) == 1 for j in range(len(source.nodes))),
        "event charge map mismatch",
    )
    return matrix


def produce_target(case, source_values):
    """Small represented research transfer, not a production event builder."""
    request = case["request"]
    resources = {}
    for node in case["expected_target_roles"]["nodes"]:
        if node.startswith("outside-"):
            resources[node] = source_values[node]
        elif node.startswith("satellite/"):
            resources[node] = source_values[request["source_node_id"]] / 3.0
        else:
            resources[node] = 0.0
    return {
        "resources": resources,
        "reference_weights": copy.deepcopy(case["target_reference_weights"]),
        "new_reference_current": copy.deepcopy(
            case["new_edge_incoming_reference_current"]
        ),
        "W": None,
        "Z": None,
        "candidate_history": "rederived",
        "carrier_history": "not_applicable",
        "information_loss": [],
    }


def checked_target(case, source, target, incoming):
    """Consume actual producer output against untouched entry operands."""
    validate_inputs(case)
    require(set(incoming) == set(source.nodes), "source resource IDs mismatch")
    saved = dict(incoming)
    output = produce_target(copy.deepcopy(case), dict(saved))
    require(
        set(output["resources"]) == set(target.nodes), "target resource IDs mismatch"
    )
    require(
        output["reference_weights"] == {e["edge_id"]: "1" for e in target.edges},
        "complete unit C references required",
    )
    require(
        output["new_reference_current"]
        == {
            e["edge_id"]: "0"
            for e in target.edges
            if e["edge_id"].startswith("internal/")
        },
        "new reference current mismatch",
    )
    require(
        output["W"] is None
        and output["Z"] is None
        and output["candidate_history"] == "rederived"
        and output["carrier_history"] == "not_applicable"
        and output["information_loss"] == [],
        "C_OS history output mismatch",
    )
    coeffs = transfer_matrix(source, target)
    expected = [
        sum(row[j] * Q(saved[n]) for j, n in enumerate(source.nodes)) for row in coeffs
    ]
    point = target.vector(output["resources"])
    error = full_error(point, vector(expected))
    require(error < RESOURCE_ROUND_BUDGET, "event resource error unresolved")
    for node, value in output["resources"].items():
        if node == "core" or node.startswith("extra/"):
            require(value == 0, "zero-resource role changed")
        elif node.startswith("outside-"):
            require(value == saved[node], "exterior resource changed")
    charge_error = abs(
        sum(Q(float(x)) for x in point) - sum(Q(x) for x in saved.values())
    )
    require(
        charge_error <= len(target.nodes) * error, "represented charge error unresolved"
    )
    return point, {"resource_error": error, "charge_error": charge_error}


def advance(model, point, enclosure):
    high = IntervalRows(model)
    exact_point, _, exact_stages = high.ordinary_os("C", vector(point), None)
    after, history, stages = model.ordinary_os("C", point.copy(), None)
    require(history is None, "C history appeared")
    check_geometry_stages(stages, len(model.edges))
    error = full_error(after, exact_point)
    require(error < RESOURCE_ROUND_BUDGET, "ordinary resource error unresolved")
    current_error = full_error(stages["read"]["J"], exact_stages["read"]["J"])
    require(current_error < Q(1, 2**40), "ordinary selected-current error unresolved")
    require(
        split_admitted(stages["H"], stages["regenerated"], model.I, SPLIT_TOLERANCE),
        "represented OS split rejected",
    )
    exact_box, _, box_stages = high.ordinary_os("C", enclosure, None)
    require(box_stages["split_bound"] < SPLIT_TOLERANCE, "interval OS split unresolved")
    require(box_stages["read"]["regularity"] > Q(1, 2), "current regularity unresolved")
    require(
        box_stages["geometry_bound"] < Q(1, 2), "selector geometry domain unresolved"
    )
    require(
        Q(1, len(model.nodes) * (len(model.nodes) - 1)) > Q(1, 512),
        "constant selector gap unresolved",
    )
    widened = inflate(exact_box, RESOURCE_ROUND_BUDGET)
    for represented, exact in zip(after, widened, strict=True):
        require(
            endpoint(exact, 0) <= Q(float(represented)) <= endpoint(exact, 1),
            "represented continuation left enclosure",
        )
    return (
        after,
        widened,
        {
            "resource_error": float(error),
            "current_error": float(current_error),
            "resource_lower": float(min(endpoint(x, 0) for x in widened)),
            "resource_upper": float(max(endpoint(x, 1) for x in widened)),
            "geometry_bound": float(box_stages["geometry_bound"]),
            "split_bound": float(box_stages["split_bound"]),
        },
    )


class EventCompanionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(INPUT_PATH.read_text())
        validate_inputs(cls.case)
        # The constructor also gets private graph dictionaries: its returned
        # edges must not alias the validated record used by the binding guard.
        cls.source, cls.target = models(copy.deepcopy(cls.case))
        assert_model_binding(cls.case, "source_graph", cls.source)
        assert_model_binding(cls.case, "expected_target_roles", cls.target)

    def test_shared_inputs_and_exact_event_charge(self):
        matrix = transfer_matrix(self.source, self.target)
        self.assertEqual((len(matrix), len(matrix[0])), (17, 10))
        self.assertTrue(all(x >= 0 for row in matrix for x in row))
        for j in range(len(self.source.nodes)):
            self.assertEqual(sum(row[j] for row in matrix), 1)
        self.assertEqual(len(self.target.edges), 16)
        occupied = [
            (end["node_id"], end["port"])
            for edge in self.target.edges
            for end in (edge["tail"], edge["head"])
        ]
        self.assertEqual(len(occupied), len(set(occupied)))
        self.assertNotIn("source-s", self.target.nodes)
        self.assertEqual(9 * 8 - 2 * 7, 58)

    def test_binding_rejects_incomplete_or_different_recipes(self):
        corruptions = []
        for section, field, value in (
            ("request", "resource_distribution", ["1/2", "1/4", "1/4"]),
            ("request", "module_chirality", -1),
            ("request", "growth_phase", 2),
            ("parameters", "zeta_C", "1/2"),
            ("row_detection", "weights", "retained_Hodge"),
            ("row_detection", "stage", "pre_continuity"),
            ("ordinary", "source_reset_steps", 1),
        ):
            changed = copy.deepcopy(self.case)
            changed[section][field] = value
            corruptions.append(changed)
        changed = copy.deepcopy(self.case)
        del changed["target_reference_weights"]["old-9"]
        corruptions.append(changed)
        changed = copy.deepcopy(self.case)
        changed["roles"]["reset"] = copy.deepcopy(changed["roles"]["current"])
        corruptions.append(changed)
        changed = copy.deepcopy(self.case)
        changed["Z"] = [[0.0]]
        corruptions.append(changed)
        for changed in corruptions:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_inputs(changed)

    def test_actual_transfer_consumer_rejects_wrong_resources_and_channels(self):
        incoming = {
            n: float(Q(v))
            for n, v in self.case["roles"]["reset"]["initial_resources"].items()
        }
        saved = dict(incoming)
        good = produce_target(self.case, incoming)
        cases = []
        for node in ("core", "extra/3/2", "outside-9", "satellite/3"):
            bad = copy.deepcopy(good)
            bad["resources"][node] += 0.125
            cases.append(bad)
        bad = copy.deepcopy(good)
        del bad["resources"]["outside-9"]
        cases.append(bad)
        bad = copy.deepcopy(good)
        bad["reference_weights"]["internal/3"] = "2"
        cases.append(bad)
        bad = copy.deepcopy(good)
        del bad["reference_weights"]["old-9"]
        cases.append(bad)
        for field, value in (
            ("Z", [[0.0]]),
            ("W", [1.0]),
            ("information_loss", ["carrier_history_loss"]),
            ("carrier_history", "reset"),
        ):
            bad = copy.deepcopy(good)
            bad[field] = value
            cases.append(bad)
        bad = copy.deepcopy(good)
        bad["new_reference_current"]["internal/1"] = "1"
        cases.append(bad)
        for bad in cases:
            with (
                patch(__name__ + ".produce_target", return_value=bad),
                self.assertRaises(ValueError),
            ):
                checked_target(self.case, self.source, self.target, incoming)
        self.assertEqual(incoming, saved)
        self.assertEqual(len(cases), 12)
        producer = produce_target

        def shifted_input(case, working):
            working["source-s"] += 0.125
            return producer(case, working)

        with (
            patch(__name__ + ".produce_target", side_effect=shifted_input),
            self.assertRaisesRegex(ValueError, "event resource error unresolved"),
        ):
            checked_target(self.case, self.source, self.target, incoming)
        self.assertEqual(incoming, saved)

    def test_consuming_setup_rejects_altered_models(self):
        constructor = models
        count = 0
        for which in (0, 1):
            modes = ["parameters", "index", "B", "D", "I", "mask"]
            if which == 1:
                modes.append("ports")
            for mode in modes:

                def altered(case, which=which, mode=mode):
                    pair = constructor(case)
                    model = pair[which]
                    if mode == "parameters":
                        model.params = replace(
                            model.params, chi_c=2 * model.params.chi_c
                        )
                    elif mode == "index":
                        a, b = model.nodes[:2]
                        model.index[a], model.index[b] = model.index[b], model.index[a]
                    elif mode == "ports":
                        # These edge dictionaries alias the constructor's work
                        # record, so setup must retain a separate reference.
                        model.edges[0]["tail"]["port"] = 5
                        model.edges[0]["head"]["port"] = 5
                    else:
                        getattr(model, mode)[-1, -1] += 0.125
                    return pair

                probe = type("BindingProbe", (EventCompanionTests,), {})
                with (
                    self.subTest(graph=which, mode=mode),
                    patch(__name__ + ".models", side_effect=altered),
                    self.assertRaisesRegex(ValueError, "consumed model"),
                ):
                    probe.setUpClass()
                self.assertEqual(probe.case, self.case)
                count += 1
        self.assertEqual(count, 13)

    def role_target_trajectory(self, role):
        values = {
            n: Q(v) for n, v in self.case["roles"][role]["initial_resources"].items()
        }
        source_point = self.source.vector(values)
        if role == "current":
            source_point = self.source.ordinary_os("C", source_point, None)[0]
        first, _ = checked_target(
            self.case,
            self.source,
            self.target,
            dict(zip(self.source.nodes, map(float, source_point), strict=True)),
        )
        trajectory = [first]
        for _ in range(bounds.HORIZON):
            trajectory.append(
                self.target.ordinary_os("C", trajectory[-1].copy(), None)[0]
            )
        return trajectory

    def test_read_only_entry_ownership_for_final_and_effect_inputs(self):
        trajectories = {
            role: self.role_target_trajectory(role) for role in ("current", "reset")
        }
        source_initial = self.source.vector(
            {
                n: Q(v)
                for n, v in self.case["roles"]["current"]["initial_resources"].items()
            }
        )
        cases = [
            ("source_effect", self.source, source_initial),
            ("target_effect", self.target, trajectories["current"][0]),
        ]
        cases += [
            (role + "_final", self.target, trajectory[-1])
            for role, trajectory in trajectories.items()
        ]
        for label, model, incoming in cases:
            saved = incoming.copy()
            enclosure = vector(incoming)
            producer = model.ordinary_os
            checked_read_only(model, incoming, enclosure)

            def shifted(candidate, c, w, producer=producer):
                c += 0.125
                return producer(candidate, c, w)

            def lawful_scratch(candidate, c, w, producer=producer):
                output = producer(candidate, c, w)
                c.fill(0)
                return output

            with self.subTest(stage=label):
                with (
                    patch.object(model, "ordinary_os", side_effect=shifted),
                    self.assertRaisesRegex(ValueError, "relative to entry input"),
                ):
                    checked_read_only(model, incoming, enclosure)
                np.testing.assert_array_equal(incoming, saved)
                with patch.object(model, "ordinary_os", side_effect=lawful_scratch):
                    checked_read_only(model, incoming, enclosure)
                np.testing.assert_array_equal(incoming, saved)

    def test_final_mutation_rejected_through_actual_continuation(self):
        trajectory = self.role_target_trajectory("current")
        k = self.target.index["core"]
        threshold = float(
            (Q(float(trajectory[-2][k])) + Q(float(trajectory[-1][k]))) / 2
        )
        self.assertTrue(all(point[k] < threshold for point in trajectory[:-1]))
        self.assertGreater(trajectory[-1][k], threshold)
        producer = self.target.ordinary_os
        calls = []

        def final_shift(candidate, c, w):
            if c[k] > threshold:
                calls.append(c.copy())
                c += 0.125
            return producer(candidate, c, w)

        with (
            patch.object(self.target, "ordinary_os", side_effect=final_shift),
            self.assertRaisesRegex(ValueError, "relative to entry input"),
        ):
            self.test_both_role_event_outputs_and_bounded_continuation()
        self.assertEqual(len(calls), 1)
        np.testing.assert_array_equal(calls[0], trajectory[-1])

    def test_both_role_event_outputs_and_bounded_continuation(self):
        source, target = self.source, self.target
        transfer = IV.matrix(
            [[number(x) for x in row] for row in transfer_matrix(source, target)]
        )
        report, effects, targets = {}, {}, {}
        for role in ("current", "reset"):
            values = {
                n: Q(x)
                for n, x in self.case["roles"][role]["initial_resources"].items()
            }
            point = source.vector(values)
            self.assertLess(
                full_error(point, vector([values[n] for n in source.nodes])),
                RESOURCE_ROUND_BUDGET,
            )
            enclosure = vector([values[n] for n in source.nodes], RESOURCE_RADIUS)
            if role == "current":
                initial = point.copy()
                point, enclosure, source_report = advance(source, point, enclosure)
                # The candidate is evaluated freshly on post-beat C and the
                # complete stable-edge reference weights, not predictor data.
                rows = IntervalRows(source).rows(
                    enclosure, vector([1] * len(source.edges))
                )[source.index["source-s"]]
                self.assertTrue(all(endpoint(x, 0) > 0 for x in rows))
                self.assertLess(sum(upper_abs(x) ** 2 for x in rows), Q(1, 4))
                self.assertEqual(len(source.edges), 9)
            incoming = dict(zip(source.nodes, map(float, point), strict=True))
            target_point, certificate = checked_target(
                self.case, source, target, incoming
            )
            targets[role] = target_point.copy()
            target_box = transfer * enclosure
            # Only the three divided coordinates round at the event. Zero
            # and copied exterior coordinates remain exactly as specified.
            for n in target.nodes:
                if n.startswith("satellite/"):
                    i = target.index[n]
                    target_box[i] = inflate(
                        IV.matrix([target_box[i]]), RESOURCE_ROUND_BUDGET
                    )[0]
            for n, point_value, exact in zip(
                target.nodes, target_point, target_box, strict=True
            ):
                self.assertLessEqual(endpoint(exact, 0), Q(float(point_value)))
                self.assertGreaterEqual(endpoint(exact, 1), Q(float(point_value)))
                if n == "core" or n.startswith("extra/"):
                    self.assertEqual((endpoint(exact, 0), endpoint(exact, 1)), (0, 0))
            first_target = target_point.copy()
            steps = []
            for _ in range(bounds.HORIZON):
                target_point, target_box, item = advance(
                    target, target_point, target_box
                )
                self.assertGreater(
                    item["resource_lower"], float(bounds.RESOURCE_MARGIN / 2)
                )
                self.assertLess(item["resource_upper"], 4)
                steps.append(item)
            # Final reconstruction without crediting an extra ordinary beat.
            _, _, final_error = checked_read_only(target, target_point, target_box)
            report[role] = {
                "event": {k: float(v) for k, v in certificate.items()},
                "target_initial": dict(
                    zip(target.nodes, map(float, first_target), strict=True)
                ),
                "steps": steps,
                "final_read_current_error": float(final_error),
            }
            if role == "current":
                report[role]["source"] = source_report
                # Reuse the accepted named-stage effect scope: current source
                # and first current target. Reset gets continuation, not an
                # unproved extension of the original OS effect claims.
                for label, model, c in (
                    ("source", source, initial),
                    ("target", target, first_target),
                ):
                    hi = IntervalRows(model)
                    stages, truth, _ = checked_read_only(model, c, vector(c))
                    for name, flags in (
                        ("geometry", {"geometry": False}),
                        ("readback", {"feedback": False}),
                        ("modulation", {"modulation": False}),
                    ):
                        offi = hi.read("C", vector(c), None, truth["H"], **flags)
                        off = model.read(
                            "C", c.copy(), None, stages["H"].copy(), **flags
                        )
                        self.assertLess(full_error(off["J"], offi["J"]), Q(1, 2**40))
                        effects[label + "_" + name] = separation(
                            stages["read"]["J"], off["J"], truth["read"]["J"], offi["J"]
                        )
        self.assertFalse(np.array_equal(targets["current"], targets["reset"]))
        self.assertGreater(
            targets["current"][target.index["satellite/1"]],
            targets["reset"][target.index["satellite/1"]],
        )
        self.assertEqual(len(effects), 6)
        type(self).report = {"roles": report, "effects": effects}


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(json.dumps(getattr(EventCompanionTests, "report", {}), indent=2))
    sys.exit(not result.result.wasSuccessful())
