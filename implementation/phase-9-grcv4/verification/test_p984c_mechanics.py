"""Shared boundary mechanics and controlled receiver routing, not numerical admission.

--run emits a compact completed test record. --check authenticates that record
and current source bindings only. Neither path runs a native solver or commits
an event. Receiver probes mock numerical reads, detection and target creation;
their only claim is dispatch/failure classification and unchanged publication.
"""

from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
import io
import json
import math
import platform
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import prepare_p984c_boundaries as contract

sys.path.insert(0, str(contract.ROOT))
from pygrc.models import grc_9_v4_expansion as expansion  # noqa: E402
from pygrc.models import grc_9_v4_lifecycle as lifecycle  # noqa: E402
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph as Graph  # noqa: E402
from pygrc.models.grc_v4_codec import V4SchemaError, V4WireError, canonical_json_bytes, decode_json  # noqa: E402
from pygrc.models.grc_v4_geometry import GeometryStageInputs  # noqa: E402
from pygrc.models.grc_v4_state import FrozenJSONMap  # noqa: E402
from tests.models.test_grc_9_v4_expansion import independent_tree  # noqa: E402

SELF = contract.HERE + "test_p984c_mechanics.py"
RESULT = contract.BASE + "P9-8.4c-MechanicalChecks.json"
REVIEW = contract.BASE + "P9-8.4c-MechanicalReview.md"
SUFFIXES = dict(C_OS="COS", A_OS="AOS", C_CI="CCI", A_CI="ACI", C_PC="CPC",
                A_PC="APC", C_CI_PC="CCIPC", A_CI_PC="ACIPC", C_RG2b="CRG2b", A_RG2b="ARG2b")
OBSERVATIONS = {}


def read(name):
    return json.loads((contract.ROOT / name).read_bytes())


def checked_geometry(degree, chirality, phase):
    """Successor wire-domain fence; the accepted arithmetic record is unchanged."""
    if type(degree) is not int or not 9 <= degree <= 2**53 - 1:
        raise ValueError("degree outside wire range")
    return contract.geometry(degree, chirality, phase)


class Subjects:
    def __init__(self):
        self.contract = read(contract.OUTPUT)
        self.layouts = {r["id"]: r for r in self.contract["layouts"]}
        self.families = {r["family"]: r for r in self.contract["families"]}
        self.cases = {(r["layout"], r["family"]): r for r in self.contract["cases"]}
        self.cache = {}

    def document(self, name):
        if name not in self.cache:
            self.cache[name] = read(name)
        return self.cache[name]

    def setup(self, layout, family="C_OS"):
        case = self.cases[layout, family]
        manifest = self.document(self.families[family]["initial_inputs"]["path"])
        inputs = manifest["initial_inputs"]
        spec = manifest.get("specialization") or manifest.get("expected_source", manifest.get("nominal_source"))["specialization"]
        graph = Graph.from_payload(inputs["reference"]["graph"])
        policy = expansion.GRC9ExpansionPolicy.from_payload(spec["resolved"]["expansion"])
        ref = case["request_recipe"]["template"]
        raw = self.document(ref["path"])
        for key in ref["pointer"].strip("/").split("/"):
            raw = raw[int(key)] if isinstance(raw, list) else raw[key]
        request = deepcopy(raw)
        request.update(case["request_recipe"]["overrides"], expected_event_id=None, expected_target_graph_digest=None)
        return graph, policy, request, inputs, spec

    @staticmethod
    def plan(graph, policy, raw):
        request = expansion.GRC9V4ExpansionRequestInput.from_payload(raw)
        return expansion.GRC9V4ExpansionPlan(graph, request.source_state_digest, request, policy)


class SharedMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Subjects()

    def test_all_layouts_against_independent_tree_and_boundary_map(self):
        groups = {}
        for name, row in self.s.layouts.items():
            with self.subTest(layout=name):
                graph, policy, raw, _, _ = self.s.setup(name)
                before = canonical_json_bytes(graph.to_payload())
                plan = self.s.plan(graph, policy, raw)
                e = row["expected"]
                self.assertEqual(checked_geometry(row["degree"], row["chirality"], row["phase"]), e)
                self.assertEqual(len(plan.module_node_ids), e["module_nodes"])
                self.assertEqual(plan.external_capacity, e["capacity"])
                self.assertEqual(plan.branch_extra_counts, tuple(e["branch_extras"]))
                target = plan.target_graph
                self.assertEqual((len(target.live_node_ids), len(target.edges)), (e["target_vertices"], e["target_edges"]))
                prefix = plan.event_id + "/"
                edges = {ed.edge_id: ed for ed in target.edges}
                internal = [edges[i] for i in plan.internal_edge_ids]
                actual = sorted((ed.edge_id.removeprefix(prefix), ed.tail.node_id.removeprefix(prefix),
                                 ed.head.node_id.removeprefix(prefix), ed.tail.port) for ed in internal)
                self.assertEqual(actual, independent_tree(tuple(e["branch_extras"]), row["chirality"]))
                self.assertTrue(all(ed.tail.port == ed.head.port for ed in internal))
                tokens = [(ep.node_id, ep.port) for ed in target.edges for ep in (ed.tail, ed.head)]
                self.assertEqual(len(tokens), len(set(tokens)))
                module = set(plan.module_node_ids)
                # D is desired capacity, not the number of attached old edges.
                self.assertEqual(9*len(module) - sum(n in module for n, _ in tokens), e["capacity"] - 9)
                reached = {prefix + "core"}
                while True:
                    enlarged = reached | {ed.head.node_id for ed in internal if ed.tail.node_id in reached}
                    if enlarged == reached:
                        break
                    reached = enlarged
                self.assertEqual(reached, module)
                self.assertEqual(len(internal), len(module) - 1)
                for axis in (lambda p: (p-1)//3, lambda p: (p-1)%3):
                    counts = Counter(axis(ed.tail.port) for ed in internal)
                    self.assertLessEqual(max(counts[i] for i in range(3)) - min(counts[i] for i in range(3)), 1)
                for old in graph.edges:
                    new = edges[old.edge_id]
                    self.assertEqual(old.kind, new.kind)
                    for a, b in ((old.tail, new.tail), (old.head, new.head)):
                        self.assertEqual(a.port, b.port)
                        expected = prefix + f"satellite/{(a.port-1)%3+1}" if a.node_id == raw["source_node_id"] else a.node_id
                        self.assertEqual(b.node_id, expected)
                key = (e["module_nodes"], row["chirality"], row["phase"])
                groups.setdefault(key, []).append((plan.event_id, actual))
                self.assertEqual(before, canonical_json_bytes(graph.to_payload()))
        self.assertEqual(len(groups), 14)
        for members in groups.values():
            self.assertEqual(len({event for event, _ in members}), len(members))
            self.assertTrue(all(tree == members[0][1] for _, tree in members))
        OBSERVATIONS["shared_layouts"] = 32
        OBSERVATIONS["normalized_module_classes"] = 14

    def test_all_family_resource_maps_without_numerical_admission(self):
        count = 0
        for family in self.s.families:
            # One representative per size; the 32-layout allocation sweep is shared.
            for name in ("P984C-D37-E1-P1", "P984C-D44-E-1-P2", "P984C-D45-E1-P0"):
                graph, policy, raw, inputs, _ = self.s.setup(name, family)
                plan = self.s.plan(graph, policy, raw)
                transform = expansion._resource_transform(plan)
                coefficients = transform["row_major_coefficients"]
                width = len(graph.live_node_ids)
                self.assertEqual(transform["target_increment"], [0.0]*len(plan.target_graph.live_node_ids))
                for i in range(width):
                    self.assertEqual(sum(map(Fraction, coefficients[i::width])), 1)
                for role in ("current", "reset"):
                    old = dict(zip(graph.live_node_ids, inputs[role]["C"], strict=True))
                    image = []
                    for i, node in enumerate(plan.target_graph.live_node_ids):
                        value = sum(Fraction(a)*Fraction(x) for a, x in zip(coefficients[i*width:(i+1)*width], old.values(), strict=True))
                        expected = (Fraction(old[raw["source_node_id"]])*Fraction(raw["resource_distribution"][int(node[-1])-1])
                                    if isinstance(node, str) and node.startswith(plan.event_id + "/satellite/") else Fraction(old.get(node, 0)))
                        self.assertEqual(value, expected)
                        self.assertGreaterEqual(value, 0)
                        image.append(value)
                    self.assertEqual(sum(image), sum(map(Fraction, old.values())))
                    count += 1
        OBSERVATIONS["exact_real_resource_maps"] = count

    def test_all_frozen_negative_recipes_reject_at_the_declared_layer(self):
        for fault in self.s.contract["negative_recipes"]:
            with self.subTest(fault=fault["id"]):
                graph, policy, raw, _, _ = self.s.setup(fault["base_layout"])
                if fault["operation"] == "remove":
                    del raw[fault["field"]]
                else:
                    raw[fault["field"]] = json.loads(fault["value"]) if fault["operation"] == "replace_raw_json_token" else fault["value"]
                with patch.object(expansion, "_allocate", side_effect=AssertionError("negative reached allocation")):
                    if fault["expected_stage"] == "wire_decode":
                        with self.assertRaises((V4SchemaError, V4WireError)):
                            expansion.GRC9V4ExpansionRequestInput.from_payload(raw)
                    else:
                        typed = expansion.GRC9V4ExpansionRequestInput.from_payload(raw)
                        with self.assertRaises(expansion.GRC9V4ExpansionError) as raised:
                            expansion.GRC9V4ExpansionPlan(graph, typed.source_state_digest, typed, policy)
                        self.assertEqual(raised.exception.code, fault["expected_code"])
        OBSERVATIONS["shared_negative_recipes"] = 31

    def test_integer_limits_simplex_corners_and_near_misses(self):
        for degree in (*range(9, 200), 2**53-4, 2**53-3, 2**53-2, 2**53-1):
            expected = max(4, math.ceil(Fraction(degree-2, 7)))
            self.assertEqual(expansion.canonical_module_node_count(degree), expected)
            phase = None if (expected-4)%3 == 0 else 1
            self.assertEqual(checked_geometry(degree, 1, phase)["module_nodes"], expected)
        for bad in (True, 8, 37.5, 2**53, 10**100, float("nan"), float("inf")):
            with self.assertRaises((ValueError, TypeError)):
                expansion.canonical_module_node_count(bad)
            with self.assertRaises(ValueError):
                checked_geometry(bad, 1, 1)
        graph, policy, raw, _, _ = self.s.setup("P984C-D37-E1-P1")
        for i in range(3):
            shares = [0.0]*3
            shares[i] = 1.0
            self.s.plan(graph, policy, {**raw, "resource_distribution": shares})
        for shares in ([1, math.nextafter(0, 1), 0], [.5, .25, math.nextafter(.25, 1)]):
            with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, "invalid_resource_distribution"):
                self.s.plan(graph, policy, {**raw, "resource_distribution": shares})
        for shares in ([-math.nextafter(0, 1), .5, .5], [float("nan"), .5, .5], [float("inf"), 0, 0], [.5, .5]):
            with self.assertRaises((V4SchemaError, V4WireError)):
                self.s.plan(graph, policy, {**raw, "resource_distribution": shares})
        normalized = self.s.plan(graph, policy, {**raw, "target_effective_degree": 37., "growth_phase": 1., "module_chirality": 1.})
        self.assertEqual(normalized.request.target_effective_degree, 37)
        for wire in ('{"growth_phase":1,"growth_phase":2}', '{"growth_phase":NaN}', '{"growth_phase":Infinity}'):
            with self.assertRaises(V4WireError):
                decode_json(wire)
        OBSERVATIONS["safe_integer_cases"] = 195
        OBSERVATIONS["scalar_outliers"] = 20

    def test_unsaturated_loop_and_stale_identities(self):
        graph, policy, raw, _, _ = self.s.setup("P984C-D37-E1-P1")
        for field, code in (("source_graph_digest", "source_graph_digest_mismatch"),
                            ("expected_event_id", "expected_event_id_mismatch"),
                            ("expected_target_graph_digest", "expected_target_graph_digest_mismatch")):
            value = ("grc-event-sha256:" if field == "expected_event_id" else "grc-graph-sha256:") + "0"*64
            with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, code):
                self.s.plan(graph, policy, {**raw, field: value})
        request = expansion.GRC9V4ExpansionRequestInput.from_payload(raw)
        with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, "source_state_digest_mismatch"):
            expansion.GRC9V4ExpansionPlan(graph, "grcv4-state-sha256:" + "0"*64, request, policy)
        history = deepcopy(raw["history_policy"])
        history["candidate_history_policy_digest"] = history["candidate_history_policy_digest"][:-64] + "0"*64
        with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, "history_policy_digest_mismatch"):
            self.s.plan(graph, policy, {**raw, "history_policy": history})
        under = replace(graph, edges=graph.edges[:-1])
        with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, "source_not_saturated"):
            self.s.plan(under, policy, {**raw, "source_graph_digest": under.graph_digest})
        payload = graph.to_payload()
        payload["edges"] = payload["edges"][2:] + [dict(edge_id="loop", kind="boundary",
            tail=dict(node_id=raw["source_node_id"], port=1), head=dict(node_id=raw["source_node_id"], port=2))]
        loop = Graph.from_payload(payload)
        with self.assertRaisesRegex(expansion.GRC9V4ExpansionError, "source_self_loop_unsupported"):
            self.s.plan(loop, policy, {**raw, "source_graph_digest": loop.graph_digest})
        OBSERVATIONS["identity_and_source_rejections"] = 7

    def test_each_receiver_dispatch_and_failure_stage_without_native_solves(self):
        observations = []
        for family, suffix in SUFFIXES.items():
            with self.subTest(family=family):
                _, _, raw, initial, spec = self.s.setup("P984C-D44-E-1-P2", family)
                state_type = getattr(lifecycle, "GRC9V4" + suffix + "State")
                owner_type = getattr(lifecycle, "GRC9V4" + suffix + "Operation")
                # Synthetic postbeat marker is for receiver unit control flow only.
                # No source trajectory, trigger truth or target admission is claimed.
                inputs = replace(GeometryStageInputs.from_payload(initial), step_index=1)
                state = state_type(inputs, lifecycle.GRC9V4Specialization(FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])))
                history = (expansion.apc_history_policy if family in ("A_PC", "A_CI_PC") else
                           expansion.aos_history_policy if family.startswith("A_") else
                           expansion.cpc_history_policy if family in ("C_PC", "C_CI_PC") else None)
                if history:
                    raw["history_policy"] = history(state.inputs.current, state.inputs.reset)
                raw.update(source_state_digest=state.scientific_digest, target_specialization_id=state.specialization.specialization_id)
                typed = expansion.GRC9V4ExpansionRequestInput.from_payload(raw)
                zeros = SimpleNamespace(values=(0.,)*len(state.inputs.geometry.reference.graph.live_edge_ids))
                with patch.object(lifecycle, "_event_readmit", return_value=(zeros, zeros)) as admission:
                    owner = owner_type(state)
                    published = owner._published
                    admission.reset_mock()
                    for changes, code in (({"growth_phase": None}, "module_growth_phase_required"),
                                          ({"module_chirality": None}, "module_chirality_required"),
                                          ({"target_effective_degree": 45}, "reject_noncanonical_inactive_growth_phase")):
                        with patch.object(expansion, "_allocate", side_effect=AssertionError("semantic failure allocated")):
                            result = owner.expand(replace(typed, **changes))
                        self.assertFalse(result.committed)
                        self.assertEqual((result.failure.stage, result.failure.code), ("admission", code))
                        self.assertIs(owner._published, published)
                    admission.assert_not_called()
                    with self.assertRaises(V4SchemaError):
                        expansion.GRC9V4ExpansionRequestInput.from_payload({**raw, "growth_phase": True})
                    with patch.object(lifecycle, "GRC9V4CandidateDetection", return_value=SimpleNamespace(candidate_node_ids=lambda: (raw["source_node_id"],))):
                        # Guard every sibling: wrong dispatch is an uncaught assertion.
                        with ExitStack() as stack:
                            routes = {}
                            for other in SUFFIXES.values():
                                routes[other] = stack.enter_context(patch.object(lifecycle, "GRC9V4"+other+"Expansion",
                                    side_effect=ValueError("selected dispatch probe") if other == suffix else AssertionError("wrong sibling")))
                            result = owner.expand(typed)
                            routes[suffix].assert_called_once()
                            self.assertEqual((result.failure.stage, result.failure.code), ("target_construction", "invalid_topology_event"))
                        # PC must retain its carrier-derived geometry even in this
                        # routing double; substituting reference H fails earlier.
                        fake_target = SimpleNamespace(target=SimpleNamespace(geometry=lambda: state.inputs.geometry), transfer=lambda role: role)
                        with patch.object(lifecycle, "GRC9V4"+suffix+"Expansion", return_value=fake_target), patch.object(
                            lifecycle, "_event_readmit", side_effect=[(zeros, zeros), ValueError("injected target numerical rejection")]):
                            result = owner.expand(typed)
                        self.assertEqual((result.failure.stage, result.failure.code), ("target_readmission", "target_readmission_failure"))
                        self.assertFalse(result.committed)
                        self.assertIs(owner._published, published)
                        self.assertEqual(owner.receipts, ())
                observations.append(dict(family=family, semantic_rejections=3, malformed_wire=1,
                    dispatch="correct_sibling", injected_target_readmission="correct_failure_stage",
                    numerical_reads_mocked=True, candidate_detection_mocked=True, target_construction_mocked=True))
        OBSERVATIONS["receiver_probes"] = observations


def bindings():
    paths = {SELF, contract.OUTPUT, contract.SELF, "tests/models/test_grc_9_v4_expansion.py", "specs/grc-v4-contract-schema.json"}
    paths.update(r["path"] for r in read(contract.OUTPUT)["source_bindings"])
    for pattern in ("grc_v4*.py", "grc_9_v4*.py"):
        paths.update(str(p.relative_to(contract.ROOT)) for p in (contract.ROOT / "src/pygrc/models").glob(pattern))
    return [dict(path=p, sha256=hashlib.sha256((contract.ROOT/p).read_bytes()).hexdigest()) for p in sorted(paths)]


def check(value):
    contract.require(value == contract.seal(value), "mechanical evidence digest drift")
    contract.require(value["source_bindings"] == bindings(), "mechanical evidence source drift")
    contract.require(value["contract_digest"] == read(contract.OUTPUT)["record_digest"], "boundary contract drift")
    roster = unittest.defaultTestLoader.getTestCaseNames(SharedMechanicsTests)
    contract.require(value["tests"] == roster and value["tests_passed"] == len(roster), "test roster drift")
    contract.require(value["schema"] == "p984c-shared-mechanics-v1" and value["scope"] == "mechanical_tests_and_mocked_receiver_control_flow_only", "mechanical scope drift")
    for field in ("native_numerical_steps", "committed_events", "numerical_history_credit"):
        contract.require(type(value[field]) is int and value[field] == 0, "numerical scope promotion")
    contract.require(value["user_accepted"] is False, "execution record cannot accept itself")
    expected = dict(shared_layouts=32, normalized_module_classes=14, exact_real_resource_maps=60,
                    shared_negative_recipes=31, safe_integer_cases=195, scalar_outliers=20, identity_and_source_rejections=7)
    for key, count in expected.items():
        contract.require(value["observations"][key] == count, "mechanical counts drift")
    rows = value["observations"]["receiver_probes"]
    contract.require(len(rows) == 10 and {r["family"] for r in rows} == set(SUFFIXES), "receiver population drift")
    for row in rows:
        contract.require(row == dict(family=row["family"], semantic_rejections=3, malformed_wire=1,
            dispatch="correct_sibling", injected_target_readmission="correct_failure_stage",
            numerical_reads_mocked=True, candidate_detection_mocked=True, target_construction_mocked=True), "receiver scope drift")
    return {"retained_integrity": "passed", "test_methods": len(roster), "tests_rerun": False, "native_numerical_steps": 0}


def run():
    OBSERVATIONS.clear()
    log = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SharedMechanicsTests)
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError(log.getvalue())
    value = contract.seal(dict(schema="p984c-shared-mechanics-v1", date="2026-10-07",
        contract_digest=read(contract.OUTPUT)["record_digest"], source_bindings=bindings(),
        scope="mechanical_tests_and_mocked_receiver_control_flow_only", python=platform.python_version(),
        tests=unittest.defaultTestLoader.getTestCaseNames(SharedMechanicsTests), tests_passed=result.testsRun,
        observations=OBSERVATIONS, native_numerical_steps=0, committed_events=0, numerical_history_credit=0,
        user_accepted=False))
    check(value)
    return value


class MechanicalRecordTests(unittest.TestCase):
    def test_retained_scope_and_resealed_promotions(self):
        value = read(RESULT)
        self.assertEqual(check(value)["retained_integrity"], "passed")
        for key, replacement in (("committed_events", 1), ("native_numerical_steps", 1),
                                 ("numerical_history_credit", 640), ("user_accepted", True),
                                 ("source_bindings", []), ("tests", [])):
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(contract.seal({**value, key: replacement}))
        for field in ("numerical_reads_mocked", "candidate_detection_mocked", "target_construction_mocked"):
            bad = deepcopy(value)
            bad["observations"]["receiver_probes"][0][field] = False
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "receiver scope drift"):
                check(contract.seal(bad))


if __name__ == "__main__":
    if sys.argv[1:] == ["--run"]:
        print(json.dumps(run(), indent=2))
    elif sys.argv[1:] == ["--check"]:
        print(json.dumps(check(read(RESULT)), indent=2))
    else:
        unittest.main()
