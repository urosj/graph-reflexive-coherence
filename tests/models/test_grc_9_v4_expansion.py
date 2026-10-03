"""Independent mechanical allocation checks; no numerical lifecycle claim."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import unittest
from collections import Counter
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from pygrc.models import grc_9_v4_expansion as expansion
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ExpansionError,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    canonical_module_node_count,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortEdge as Edge,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortEndpoint as Endpoint,
)
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortGraph as Graph,
)
from pygrc.models.grc_v4_codec import (
    V4SchemaError,
    canonical_json_bytes,
    payload_identity,
)
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend

ROOT = Path(__file__).resolve().parents[2]


def independent_tree(
    extras: tuple[int, ...], chirality: int
) -> list[tuple[str, str, str, int]]:
    """Literal chart + full creation-order scan, independent of production FIFO."""
    rows = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
    spines = (2, 6, 7) if chirality == 1 else (3, 4, 8)
    result = []
    for branch in (1, 2, 3):
        satellite = f"satellite/{branch}"
        port = spines[branch - 1]
        result.append((f"internal/{branch}", "core", satellite, port))
        used = {satellite: {branch, branch + 3, branch + 6, port}}
        creation = [(satellite, port)]
        width = len(str(sum(extras)))
        for ordinal in range(1, extras[branch - 1] + 1):
            options: list[tuple[str, int]] = []
            for parent, incoming in creation:
                index = rows[branch - 1].index(incoming)
                candidates = [
                    rows[branch - 1][(index + chirality) % 3],
                    rows[branch - 1][(index - chirality) % 3],
                ]
                options.extend((parent, p) for p in candidates if p not in used[parent])
            parent, p = options[0]
            child = f"extra/{branch}/{ordinal:0{width}d}"
            result.append(("internal/" + child, parent, child, p))
            used[parent].add(p)
            used[child] = {p}
            creation.append((child, p))
    return sorted(result)


class ExpansionTests(unittest.TestCase):
    vectors: dict[str, Any]
    graph: Graph
    policy_data: dict[str, Any]
    policy: GRC9ExpansionPolicy
    base: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.vectors = json.loads(
            (ROOT / "specs/grc-v4-conformance-vectors.json").read_text()
        )
        cls.graph = Graph.from_payload(
            cls.vectors["port_graph_envelope_vectors"][0]["payload"]
        )
        cls.policy_data = next(
            x["payload"]["policy"]
            for x in cls.vectors["subdigest_identity_vectors"]
            if x["vector_id"] == "SUBDIGEST-GRC9-EXPANSION-POLICY"
        )
        cls.policy = GRC9ExpansionPolicy.from_payload(cls.policy_data)
        cls.base = cls.vectors["grc9_expansion_vectors"][0]["request"]

    def request(
        self, graph: Graph | None = None, **changes: Any
    ) -> GRC9V4ExpansionRequestInput:
        data = copy.deepcopy(self.base)
        data.update(
            schema_version="grc9v4-expansion-event-request-input-v1",
            expected_event_id=None,
            expected_target_graph_digest=None,
        )
        if graph is not None:
            data["source_graph_digest"] = graph.graph_digest
        data.update(changes)
        return GRC9V4ExpansionRequestInput.from_payload(data)

    def plan(
        self,
        graph: Graph | None = None,
        policy: GRC9ExpansionPolicy | None = None,
        **changes: Any,
    ) -> GRC9V4ExpansionPlan:
        graph = self.graph if graph is None else graph
        request = self.request(graph, **changes)
        return GRC9V4ExpansionPlan(
            graph,
            request.source_state_digest,
            request,
            self.policy if policy is None else policy,
        )

    def assert_code(
        self, code: str, graph: Graph | None = None, **changes: Any
    ) -> None:
        with self.assertRaises(GRC9V4ExpansionError) as raised:
            self.plan(graph, **changes)
        self.assertEqual(raised.exception.code, code)

    def test_all_frozen_allocation_subjects_and_identity_bytes(self) -> None:
        for vector in self.vectors["grc9_expansion_vectors"]:
            with self.subTest(vector=vector["fixture_id"]):
                data = copy.deepcopy(vector["request"])
                data["schema_version"] = "grc9v4-expansion-event-request-input-v1"
                request = GRC9V4ExpansionRequestInput.from_payload(data)
                plan = GRC9V4ExpansionPlan(
                    self.graph, request.source_state_digest, request, self.policy
                )
                expected = vector["expected"]
                self.assertEqual(
                    plan.event_identity_payload(), vector["event_identity_payload"]
                )
                encoded = canonical_json_bytes(plan.event_identity_payload())
                self.assertEqual(
                    encoded.decode(), vector["event_identity_canonical_jcs_utf8"]
                )
                self.assertEqual(
                    "grc-event-sha256:" + hashlib.sha256(encoded).hexdigest(),
                    plan.event_id,
                )
                self.assertEqual(plan.admitted_request_payload(), vector["request"])
                self.assertEqual(
                    plan.target_graph.to_payload(),
                    expected["identity_payloads"]["target_graph"],
                )
                self.assertEqual(
                    plan.target_graph.graph_digest, expected["target_graph_digest"]
                )
                self.assertEqual(
                    plan.branch_extra_counts,
                    tuple(expected["branch_extra_counts"][str(b)] for b in (1, 2, 3)),
                )
                self.assertEqual(
                    plan.canonical_module_node_count,
                    expected["canonical_module_node_count"],
                )
                self.assertEqual(
                    plan.internal_reference_seeds(),
                    {
                        e: (expected["target_W_C_tr"][e], 0.0)
                        for e in plan.internal_edge_ids
                    },
                )

    def test_capacity_safe_integer_edges_and_shells(self) -> None:
        for degree in [*range(9, 5000), 2**53 - 4, 2**53 - 3, 2**53 - 2, 2**53 - 1]:
            expected = max(4, math.ceil(Fraction(degree - 2, 7)))
            self.assertEqual(canonical_module_node_count(degree), expected)
            self.assertGreaterEqual(7 * expected + 2, degree)
            if expected > 4:
                self.assertLess(7 * (expected - 1) + 2, degree)
        for bad in (
            True,
            False,
            "31",
            8,
            0,
            -0.0,
            31.5,
            float("nan"),
            float("inf"),
            2**53,
            10**100,
        ):
            with self.subTest(bad=bad), self.assertRaises((ValueError, TypeError)):
                canonical_module_node_count(cast(Any, bad))
        self.assertEqual(canonical_module_node_count(cast(Any, 31.0)), 5)
        for degree, phase, count in (
            (30, None, 4),
            (31, 1, 5),
            (37, 3, 5),
            (38, 2, 6),
            (44, 1, 6),
            (45, None, 7),
            (51, None, 7),
            (52, 3, 8),
        ):
            self.assertEqual(
                self.plan(
                    target_effective_degree=degree, growth_phase=phase
                ).canonical_module_node_count,
                count,
            )

    def check_tree(self, plan: GRC9V4ExpansionPlan, chirality: int) -> None:
        prefix = plan.event_id + "/"
        internal = [
            e
            for e in plan.target_graph.edges
            if e.edge_id in set(plan.internal_edge_ids)
        ]
        actual = sorted(
            (
                e.edge_id.removeprefix(prefix),
                cast(str, e.tail.node_id).removeprefix(prefix),
                cast(str, e.head.node_id).removeprefix(prefix),
                e.tail.port,
            )
            for e in internal
        )
        self.assertEqual(actual, independent_tree(plan.branch_extra_counts, chirality))
        self.assertEqual(len(internal), len(plan.module_node_ids) - 1)
        reached = {prefix + "core"}
        while True:
            expanded = reached | {
                cast(str, e.head.node_id) for e in internal if e.tail.node_id in reached
            }
            if expanded == reached:
                break
            reached = expanded
        self.assertEqual(reached, set(plan.module_node_ids))
        for e in internal:
            self.assertEqual(e.tail.port, e.head.port)
        rows = Counter((e.tail.port - 1) // 3 for e in internal)
        columns = Counter((e.tail.port - 1) % 3 for e in internal)
        self.assertLessEqual(max(rows.values()) - min(rows.values()), 1)
        self.assertLessEqual(max(columns.values()) - min(columns.values()), 1)
        all_tokens = [
            (end.node_id, end.port)
            for e in plan.target_graph.edges
            for end in (e.tail, e.head)
        ]
        self.assertEqual(len(all_tokens), len(set(all_tokens)))
        occupied = sum(node in reached for node, _ in all_tokens)
        self.assertEqual(9 * len(reached) - occupied + 9, plan.external_capacity)

    def test_independent_bfs_oracle_all_small_sizes_and_deep_trees(self) -> None:
        for count in [*range(4, 45), 103, 104, 105, 304, 305, 306, 1004]:
            remainder = (count - 4) % 3
            for chirality in (-1, 1):
                for phase in (1, 2, 3) if remainder else (None,):
                    with self.subTest(count=count, chirality=chirality, phase=phase):
                        plan = self.plan(
                            target_effective_degree=7 * count + 2,
                            module_chirality=chirality,
                            growth_phase=phase,
                        )
                        self.check_tree(plan, chirality)
                        if count == 1004:
                            self.assertIn(
                                plan.event_id + "/extra/1/0001", plan.module_node_ids
                            )

    def test_all_source_orientations_parallel_edges_and_unaffected_content(
        self,
    ) -> None:
        for mask in range(512):
            source = replace(
                self.graph,
                edges=tuple(
                    replace(e, tail=e.head, head=e.tail) if mask & (1 << i) else e
                    for i, e in enumerate(self.graph.edges)
                ),
            )
            plan = self.plan(source, target_effective_degree=52, growth_phase=3)
            target = {e.edge_id: e for e in plan.target_graph.edges}
            for old in source.edges:
                new = target[old.edge_id]
                self.assertEqual(new.kind, old.kind)
                for a, b in ((old.tail, new.tail), (old.head, new.head)):
                    self.assertEqual(a.port, b.port)
                    self.assertEqual(
                        b.node_id,
                        plan.event_id + f"/satellite/{(a.port - 1) % 3 + 1}"
                        if a.node_id == "source-s"
                        else a.node_id,
                    )
        extra = Edge("unaffected", "tree", Endpoint("", 1), Endpoint("", 9))
        source = Graph(
            ("source-s", 1, "1", "", "isolated"),
            tuple(
                Edge(f"old-{p}", "spine", Endpoint("source-s", p), Endpoint(1, p))
                for p in range(1, 10)
            )
            + (extra,),
        )
        plan = self.plan(source)
        self.assertIn(extra, plan.target_graph.edges)
        self.assertTrue(
            {1, "1", "", "isolated"} <= set(plan.target_graph.live_node_ids)
        )
        for source_id in (1, "1", ""):
            graph = Graph(
                (source_id, "external"),
                tuple(
                    Edge(
                        str(p),
                        "boundary",
                        Endpoint(source_id, p),
                        Endpoint("external", p),
                    )
                    for p in range(1, 10)
                ),
            )
            self.assertNotIn(
                source_id,
                self.plan(graph, source_node_id=source_id).target_graph.live_node_ids,
            )

    def test_frozen_named_admission_failures_precede_target_allocation(self) -> None:
        for vector in self.vectors["atomic_failure_vectors"]:
            if vector["fixture_id"] not in (
                "G9-FAIL-MISSING-CHIRALITY",
                "G9-FAIL-MISSING-ACTIVE-PHASE",
                "G9-FAIL-NONCANONICAL-INACTIVE-PHASE",
                "G9-FAIL-SOURCE-SELF-LOOP",
            ):
                continue
            request = GRC9V4ExpansionRequestInput.from_payload(vector["request_input"])
            source = (
                Graph.from_payload(vector["source_graph_fixture"])
                if "source_graph_fixture" in vector
                else self.graph
            )
            before = canonical_json_bytes(source.to_payload())
            with (
                patch.object(
                    expansion,
                    "_allocate",
                    side_effect=AssertionError("must reject before allocation"),
                ),
                self.assertRaises(GRC9V4ExpansionError) as raised,
            ):
                GRC9V4ExpansionPlan(
                    source, request.source_state_digest, request, self.policy
                )
            self.assertEqual(raised.exception.code, vector["expected"]["code"])
            self.assertEqual(before, canonical_json_bytes(source.to_payload()))

    def test_stale_bindings_inactive_phase_and_assertions(self) -> None:
        self.assert_code(
            "source_not_saturated", replace(self.graph, edges=self.graph.edges[:-1])
        )
        self.assert_code("source_node_not_live", source_node_id="missing")
        self.assert_code(
            "source_graph_digest_mismatch",
            source_graph_digest="grc-graph-sha256:" + "0" * 64,
        )
        with self.assertRaisesRegex(
            GRC9V4ExpansionError, "source_state_digest_mismatch"
        ):
            GRC9V4ExpansionPlan(
                self.graph,
                "grcv4-state-sha256:" + "0" * 64,
                self.request(),
                self.policy,
            )
        self.assert_code("reject_noncanonical_inactive_growth_phase", growth_phase=1)
        self.assert_code("module_growth_phase_required", target_effective_degree=31)
        self.assert_code(
            "expected_event_id_mismatch",
            expected_event_id="grc-event-sha256:" + "0" * 64,
        )
        self.assert_code(
            "expected_target_graph_digest_mismatch",
            expected_target_graph_digest="grc-graph-sha256:" + "0" * 64,
        )

    def test_schema_type_guarding_and_no_caller_allocation_override(self) -> None:
        for name, bad in (
            ("target_effective_degree", True),
            ("module_chirality", True),
            ("growth_phase", False),
            ("source_node_id", True),
            ("target_effective_degree", 31.25),
            ("target_effective_degree", 2**53),
            ("module_chirality", 0),
            ("resource_distribution", [0.5, 0.25]),
            ("resource_distribution", [0.5, 0.5, -0.0]),
            ("resource_distribution", [0.5, 0.5, float("nan")]),
        ):
            with (
                self.subTest(name=name, bad=bad),
                self.assertRaises((ValueError, TypeError)),
            ):
                self.request(**cast(dict[str, Any], {name: bad}))
        for extra in (
            "target_graph",
            "event_id",
            "harness_fault",
            "allocation",
            "bond_seed",
        ):
            with self.subTest(extra=extra), self.assertRaises(V4SchemaError):
                self.request(**cast(dict[str, Any], {extra: {}}))

        class CoercibleInt(int):
            pass

        class CoercibleString(str):
            pass

        for coercible in (CoercibleInt(31), b"31", Fraction(31)):
            with self.assertRaises((ValueError, TypeError)):
                self.request(target_effective_degree=coercible)
        with self.assertRaises((ValueError, TypeError)):
            self.request(operation_id=CoercibleString("operation"))
        request = self.request(
            target_effective_degree=31.0, module_chirality=-1.0, growth_phase=2.0
        )
        self.assertIs(type(request.target_effective_degree), int)
        self.assertIs(type(request.module_chirality), int)
        self.assertIs(type(request.growth_phase), int)

    def test_exact_simplex_and_policy_digest_admission(self) -> None:
        for values in (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (0.5, 0.25, 0.25),
            (0.5, 0.5 - 2**-53, 2**-53),
        ):
            self.assertEqual(sum(Fraction(v) for v in values), 1)
            self.plan(resource_distribution=values)
        # Rounded summation would silently admit both of these non-simplexes.
        for values in (
            (1 / 3,) * 3,
            (0.5, 0.5, math.ulp(0.0)),
            (0, 0, 0),
            (0.5, 0.25, math.nextafter(0.25, 1)),
        ):
            self.assert_code(
                "invalid_resource_distribution", resource_distribution=values
            )
        history = copy.deepcopy(self.base["history_policy"])
        history["candidate"]["policy_id"] = "changed"
        self.assert_code("history_policy_digest_mismatch", history_policy=history)
        for bad in (0, -1, -0.0, float("inf"), True):
            with self.assertRaises((ValueError, TypeError)):
                replace(self.policy, bond_seed=bad)
        for seed in (math.ulp(0.0), sys.float_info.max):
            plan = self.plan(policy=replace(self.policy, bond_seed=seed))
            self.assertEqual(
                set(plan.internal_reference_seeds().values()), {(seed, 0.0)}
            )

    def test_event_identity_fields_and_operation_id_exclusion(self) -> None:
        base = self.plan(target_effective_degree=52, growth_phase=1)
        for changes in (
            {"source_state_digest": "grcv4-state-sha256:" + "1" * 64},
            {"target_profile_template_id": "grcv4-profile-template-sha256:" + "1" * 64},
            {"target_specialization_id": "grc9v4-specialization-sha256:" + "1" * 64},
            {"target_effective_degree": 53},
            {"module_chirality": -1},
            {"growth_phase": 2},
            {"resource_distribution": (1, 0, 0)},
        ):
            args = {"target_effective_degree": 52, "growth_phase": 1, **changes}
            self.assertNotEqual(
                self.plan(**cast(dict[str, Any], args)).event_id, base.event_id
            )
        for channel in ("candidate", "carrier"):
            history = copy.deepcopy(self.base["history_policy"])
            history[channel]["policy_id"] = "alternate-explicit-policy"
            history[channel + "_history_policy_digest"] = payload_identity(
                "history_channel_policy_identity_payload",
                {
                    "schema_version": "grcv4-history-channel-policy-identity-v1",
                    "policy": history[channel],
                },
            )
            self.assertNotEqual(
                self.plan(
                    target_effective_degree=52, growth_phase=1, history_policy=history
                ).event_id,
                base.event_id,
            )
        self.assertNotEqual(
            self.plan(
                policy=replace(self.policy, bond_seed=3),
                target_effective_degree=52,
                growth_phase=1,
            ).event_id,
            base.event_id,
        )
        other = self.plan(
            target_effective_degree=52, growth_phase=1, operation_id="another-operation"
        )
        self.assertEqual(other.event_id, base.event_id)
        self.assertEqual(other.target_graph, base.target_graph)

    def test_role_collisions_reject_without_source_mutation(self) -> None:
        namespace = "grc-event-sha256:" + "b" * 64
        original = payload_identity

        def fixed(schema: str, value: object, **kwargs: Any) -> str:
            return (
                namespace
                if schema == "expansion_event_identity_payload"
                else original(schema, value, **kwargs)
            )

        graphs = [
            replace(
                self.graph,
                live_node_ids=(*self.graph.live_node_ids, namespace + suffix),
            )
            for suffix in ("/core", "/satellite/2", "/extra/1/1")
        ]
        graphs.append(
            replace(
                self.graph,
                live_node_ids=(*self.graph.live_node_ids, "isolated"),
                edges=(
                    *self.graph.edges,
                    Edge(
                        namespace + "/internal/extra/1/1",
                        "tree",
                        Endpoint("isolated", 1),
                        Endpoint("isolated", 2),
                    ),
                ),
            )
        )
        for graph in graphs:
            before = graph.to_payload()
            with patch.object(expansion, "payload_identity", side_effect=fixed):
                self.assert_code(
                    "role_id_collision",
                    graph,
                    target_effective_degree=52,
                    growth_phase=1,
                )
            self.assertEqual(graph.to_payload(), before)

    def test_owned_inputs_exports_and_replace_revalidation(self) -> None:
        data = cast(dict[str, Any], self.request().to_payload())
        request = GRC9V4ExpansionRequestInput.from_payload(data)
        plan = GRC9V4ExpansionPlan(
            self.graph, request.source_state_digest, request, self.policy
        )
        before = plan.event_identity_payload()
        data["history_policy"]["candidate"]["policy_id"] = "mutated"
        data["resource_distribution"][0] = 9
        exported = cast(dict[str, Any], plan.event_identity_payload())
        exported["resource_distribution"][0] = 9
        plan.internal_reference_seeds().clear()
        self.assertEqual(before, plan.event_identity_payload())
        self.assertEqual(len(plan.internal_reference_seeds()), 3)
        self.assertFalse(hasattr(plan, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            plan.event_id = "forged"  # type: ignore[misc]
        with self.assertRaises(ValueError):
            replace(plan, target_graph=self.graph)
        with self.assertRaisesRegex(GRC9V4ExpansionError, "source_not_saturated"):
            graph = replace(self.graph, edges=self.graph.edges[:-1])
            replace(
                plan,
                source_graph=graph,
                request=replace(request, source_graph_digest=graph.graph_digest),
            )

    def test_frozen_metamorphic_vectors(self) -> None:
        fixtures = {v["fixture_id"]: v for v in self.vectors["grc9_expansion_vectors"]}
        for vector in self.vectors["grc9_metamorphic_vectors"]:
            base_args = dict(fixtures[vector["base_vector_id"]]["request"])
            base_args.pop("schema_version")
            base_args.update(expected_event_id=None, expected_target_graph_digest=None)
            base = self.plan(**base_args)
            if vector["kind"] == "source_edge_input_order_permutation":
                graph = Graph.from_payload(vector["input"]["permuted_source_graph"])
                base_args["source_graph_digest"] = graph.graph_digest
                other = self.plan(graph, **base_args)
                self.assertNotEqual(other.event_id, base.event_id)
                transported = json.loads(
                    json.dumps(base.target_graph.to_payload()).replace(
                        base.event_id, other.event_id
                    )
                )
            else:
                expected_args = dict(
                    fixtures[vector["expected_target_vector_id"]]["request"]
                )
                expected_args.pop("schema_version")
                other = self.plan(**expected_args)
                ports = vector["input"]["port_permutation"]
                branches = vector["input"]["branch_permutation"]
                self.assertEqual(
                    vector["normalization_policy_id"],
                    "grc9v4-event-namespace-and-role-covariance-normalization-v1",
                )

                def label(
                    value: str,
                    base: GRC9V4ExpansionPlan = base,
                    other: GRC9V4ExpansionPlan = other,
                    branches: dict[str, int] = branches,
                    ports: dict[str, int] = ports,
                ) -> str:
                    if value.startswith(base.event_id + "/"):
                        parts = value.removeprefix(base.event_id + "/").split("/")
                        for i, part in enumerate(parts):
                            if part in ("1", "2", "3"):
                                parts[i] = str(branches[part])
                                break
                        return other.event_id + "/" + "/".join(parts)
                    stem, port = value.split("-")
                    return stem + "-" + str(ports[port])

                transported = cast(dict[str, Any], base.target_graph.to_payload())
                transported["live_node_ids"] = sorted(
                    label(n) for n in transported["live_node_ids"]
                )
                for e in transported["edges"]:
                    e["edge_id"] = label(e["edge_id"])
                    for side in ("tail", "head"):
                        e[side]["node_id"] = label(e[side]["node_id"])
                        e[side]["port"] = ports[str(e[side]["port"])]
                transported["edges"].sort(key=lambda e: e["edge_id"])
            self.assertEqual(transported, other.target_graph.to_payload())

    @unittest.skipUnless(
        importlib.util.find_spec("flint"), "optional python-flint is not installed"
    )
    def test_python_flint_parity(self) -> None:
        signatures = []
        for backend in (ExactBackend.PYTHON, ExactBackend.FLINT):
            with exact_backend(backend):
                plan = self.plan(target_effective_degree=80, growth_phase=2)
                self.assert_code(
                    "invalid_resource_distribution",
                    resource_distribution=(0.5, 0.5, math.ulp(0.0)),
                )
                signatures.append((plan.event_id, plan.target_graph.graph_digest))
        self.assertEqual(*signatures)

    def test_process_hash_seed_parity(self) -> None:
        plan = self.plan(target_effective_degree=80, growth_phase=2)
        signature = (plan.event_id, plan.target_graph.graph_digest)
        script = """from test_grc_9_v4_expansion import ExpansionTests
ExpansionTests.setUpClass()
p = ExpansionTests().plan(target_effective_degree=80, growth_phase=2)
print(p.event_id, p.target_graph.graph_digest)
"""
        for seed in ("0", "123", "random"):
            env = {
                **os.environ,
                "PYTHONPATH": os.pathsep.join(
                    (str(ROOT / "src"), str(ROOT / "tests/models"))
                ),
                "PYTHONHASHSEED": seed,
                "OPENBLAS_NUM_THREADS": "1",
            }
            result = subprocess.run(
                [sys.executable, "-c", script],
                env=env,
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.stdout.strip(), " ".join(signature))


class COSReconstructionTests(unittest.TestCase):
    def test_nonuniform_old_reference_weights_and_seed_are_stable_id_bound(
        self,
    ) -> None:
        from pygrc.models.grc_9_v4_expansion import (
            GRC9V4COSExpansion,
            cos_profile_template,
        )
        from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture
        from tests.models.test_grc_v4_geometry import stage_reference_fixture

        seed, request = native_cos_fixture()
        original = seed.inputs.geometry.reference
        weights = {
            e: float(i + 2)
            for i, e in enumerate(reversed(original.graph.live_edge_ids))
        }
        reference = stage_reference_fixture(
            graph=original.graph, weights=weights, base=[[0.0] * 9 for _ in range(9)]
        )
        request = replace(
            request,
            target_profile_template_id=cos_profile_template(
                reference
            ).profile_template_id,
        )
        policy = GRC9ExpansionPolicy.from_payload(
            seed.specialization.resolved["expansion"]
        )
        assert original.graph.port_graph is not None
        plan = GRC9V4ExpansionPlan(
            original.graph.port_graph,
            seed.scientific_digest,
            request,
            replace(policy, bond_seed=0.125),
        )
        target = GRC9V4COSExpansion(plan, reference)
        expected = {**weights, **{e: 0.125 for e in plan.internal_edge_ids}}
        self.assertEqual(target.target.edge_weights.to_dict(), expected)
        self.assertEqual(
            target.target.profile.params_resolved.candidate.to_payload()["W_C_tr"],
            expected,
        )
        self.assertEqual(
            target.target.pairings.one_form.matrix,
            tuple(
                tuple(
                    expected[a] if a == b else 0
                    for b in target.target.graph.live_edge_ids
                )
                for a in target.target.graph.live_edge_ids
            ),
        )
        # Scalar physics and the resolved template remain unchanged; only
        # graph-dependent maps/preimages and the resulting profile ID change.
        old: Any = reference.profile.params_resolved.to_payload()
        new: Any = target.target.profile.params_resolved.to_payload()
        for group in old:
            if group not in ("candidate", "geometry"):
                self.assertEqual(old[group], new[group])
        for field in old["candidate"]:
            if field not in ("W_C_tr", "W_C_tr_content_digest"):
                self.assertEqual(old["candidate"][field], new["candidate"][field])
        with self.assertRaisesRegex(ValueError, "zero structural"):
            nonzero = stage_reference_fixture(graph=original.graph, weights=weights)
            GRC9V4COSExpansion(plan, nonzero)
        with self.assertRaisesRegex(ValueError, "template"):
            GRC9V4COSExpansion(
                replace(
                    plan,
                    request=replace(
                        request,
                        target_profile_template_id="grcv4-profile-template-sha256:"
                        + "0" * 64,
                    ),
                ),
                reference,
            )

    def test_resource_map_extremes_use_exact_products_and_leave_core_extras_zero(
        self,
    ) -> None:
        from pygrc.models.grc_9_v4_expansion import GRC9V4COSExpansion
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
        from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture

        seed, request = native_cos_fixture()
        ref = seed.inputs.geometry.reference
        assert ref.graph.port_graph is not None
        policy = GRC9ExpansionPolicy.from_payload(
            seed.specialization.resolved["expansion"]
        )
        for shares in ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.5, 0.25, 0.25)):
            request = replace(request, resource_distribution=shares)
            plan = GRC9V4ExpansionPlan(
                ref.graph.port_graph, seed.scientific_digest, request, policy
            )
            target = GRC9V4COSExpansion(plan, ref)
            for resource in (0.0, math.ulp(0.0), sys.float_info.max):
                state = GRCV4AuthoritativeState((resource, *([2.0] * 9)), None, None)
                actual = dict(
                    zip(
                        plan.target_graph.live_node_ids,
                        target.transfer(state).C,
                        strict=True,
                    )
                )
                for b in (1, 2, 3):
                    self.assertEqual(
                        actual[plan.event_id + f"/satellite/{b}"],
                        float(Fraction(resource) * Fraction(shares[b - 1])),
                    )
                self.assertTrue(
                    all(
                        actual[n] == 0
                        for n in plan.module_node_ids
                        if "/satellite/" not in n
                    )
                )
                self.assertTrue(all(actual[n] == 2 for n in range(1, 10)))
            with self.assertRaisesRegex(ValueError, "neither"):
                target.transfer(GRCV4AuthoritativeState((1.0,) * 10, (1.0,) * 9, None))


class CPCReconstructionTests(unittest.TestCase):
    def test_frozen_carrier_policy_and_content_preimages_are_reproduced(self) -> None:
        from pygrc.models.grc_9_v4_expansion import (
            carrier_content_payload,
            cpc_history_policy,
        )
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState

        vectors = json.loads(
            (ROOT / "specs/grc-v4-conformance-vectors.json").read_text()
        )
        vector = next(
            v
            for v in vectors["grc9_expansion_vectors"]
            if v["fixture_id"] == "G9-EXPAND-C-PC-CARRIER-RESET"
        )
        # The frozen vector's two content tokens exercise the identity codec;
        # they are not a 9x9 current/reset numerical carrier fixture.
        current = GRCV4AuthoritativeState((3,), None, (0.5,))
        reset = GRCV4AuthoritativeState((2,), None, (-0.25,))
        policy = cpc_history_policy(current, reset)
        self.assertEqual(policy, vector["request"]["history_policy"])
        content = carrier_content_payload(current, reset)
        self.assertEqual(content["content"], vector["expected"]["source_carrier"])
        # Literal ASCII JCS is unambiguous for these finite dyadic tokens.
        encoded = b'{"content":[0.5,-0.25],"schema_version":"grcv4-history-content-identity-v1","subject":"carrier"}'
        self.assertEqual(
            "grcv4-history-content-sha256:" + hashlib.sha256(encoded).hexdigest(),
            vector["expected"]["source_carrier_digest"],
        )
        target = carrier_content_payload(
            replace(current, Z_4=(0.0,)), replace(reset, Z_4=(0.0,))
        )
        self.assertEqual(
            payload_identity("history_content_identity_payload", target),
            vector["expected"]["target_carrier_digest"],
        )

    def test_native_cpc_resource_reference_and_carrier_transfer_is_closed(self) -> None:
        from pygrc.models.grc_9_v4_expansion import (
            GRC9V4CPCExpansion,
            cpc_history_policy,
        )
        from tests.models.test_grc_9_v4_lifecycle import native_cpc_fixture

        backend = (
            ExactBackend.FLINT
            if importlib.util.find_spec("flint")
            else ExactBackend.PYTHON
        )
        with exact_backend(backend):
            seed, request, _ = native_cpc_fixture()
            graph = seed.inputs.geometry.reference.graph.port_graph
            assert graph is not None
            plan = GRC9V4ExpansionPlan(
                graph,
                seed.scientific_digest,
                request,
                GRC9ExpansionPolicy.from_payload(
                    seed.specialization.resolved["expansion"]
                ),
            )
            target = GRC9V4CPCExpansion(
                plan,
                seed.inputs.geometry.reference,
                seed.inputs.current,
                seed.inputs.reset,
            )
            source_params: Any = target.source.profile.params_resolved.to_payload()
            expected: Any = target.target.profile.params_resolved.to_payload()
            for key in ("W_C_tr", "W_C_tr_content_digest"):
                source_params["candidate"][key] = expected["candidate"][key]
            for key in ("K4_base_digest", "reference_hodge_digest"):
                source_params["geometry"][key] = expected["geometry"][key]
            self.assertEqual(source_params, expected)
            with self.assertRaises(FrozenInstanceError):
                target.source_current = seed.inputs.reset  # type: ignore[misc]
            with self.assertRaisesRegex(ValueError, "bound source roles"):
                target.transfer(
                    replace(seed.inputs.current, C=(4.0, *seed.inputs.current.C[1:]))
                )
            with self.assertRaisesRegex(ValueError, "coordinates mismatch"):
                pair = (
                    replace(seed.inputs.current, Z_4=(0.5,)),
                    replace(seed.inputs.reset, Z_4=(-0.25,)),
                )
                altered = replace(request, history_policy=cpc_history_policy(*pair))
                small = replace(plan, request=altered)
                GRC9V4CPCExpansion(small, seed.inputs.geometry.reference, *pair)
            archive = target.carrier_archive_payload()
            archive["history_content"]["content"][0] = 99
            self.assertNotEqual(archive, target.carrier_archive_payload())


if __name__ == "__main__":
    unittest.main()
