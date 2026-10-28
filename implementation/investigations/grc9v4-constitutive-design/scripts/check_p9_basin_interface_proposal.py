"""Conditional finite-graph proposal checks and a source-bound authority audit.

No native model, accepted classifier, basin birth or conformance is exercised.
Run from the repository root with .venv/bin/python; --write retains the small
audit/results, --check compares retained records to current sources and queries.
"""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
BASE = INV + "evidence/p9-basin-interface/"
PROPOSAL = INV + "decisions/P9BasinInterfaceAuthorityProposal.md"
SELF = INV + "scripts/check_p9_basin_interface_proposal.py"
REVIEW = BASE + "IndependentReview.md"


def typed_node(node):
    """Wire encoding of already-normalized V4 IDs, including the empty string."""
    if type(node) not in (int, str):
        raise ValueError("expected a normalized int/string node ID")
    if type(node) is int and abs(node) > 2**53 - 1:
        raise ValueError("node ID must be a safe integer")
    if type(node) is str:
        node.encode("utf-8")
    return dict(kind="int" if type(node) is int else "str", value=node)


def node_key(node):
    encoded = json.dumps(
        typed_node(node), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return (0 if type(node) is int else 1, encoded.encode())


def seal(v):
    body = {k: x for k, x in v.items() if k != "record_digest"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return dict(body, record_digest=hashlib.sha256(raw).hexdigest())


def ref(name):
    return dict(
        path=name, sha256=hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    )


def arcs(nodes, edges):
    for node in nodes:
        typed_node(node)
    vertices = set(nodes)
    if len(vertices) != len(nodes):
        raise ValueError("duplicate node")
    result = set()
    for u, v, j in edges:
        typed_node(u)
        typed_node(v)
        if u not in vertices or v not in vertices or not math.isfinite(j):
            raise ValueError("invalid represented current graph")
        if j > 0:
            result.add((u, v))
        elif j < 0:
            result.add((v, u))
    return result


def flow_analysis(nodes, edges):
    """Research-only iterative SCC calculation, preserving all nonzero routes."""
    directed = arcs(nodes, edges)
    adjacency = {v: [] for v in nodes}
    reverse = {v: [] for v in nodes}
    for u, v in directed:
        adjacency[u].append(v)
        reverse[v].append(u)
    seen, order = set(), []
    for start in nodes:
        if start in seen:
            continue
        stack = [(start, False)]
        while stack:
            v, exiting = stack.pop()
            if exiting:
                order.append(v)
            elif v not in seen:
                seen.add(v)
                stack.append((v, True))
                stack.extend((w, False) for w in adjacency[v] if w not in seen)
    component = {}
    for start in reversed(order):
        if start in component:
            continue
        members, pending = set(), [start]
        while pending:
            v = pending.pop()
            if v in members or v in component:
                continue
            members.add(v)
            pending.extend(reverse[v])
        frozen = frozenset(members)
        component.update((v, frozen) for v in members)
    outgoing = {s: set() for s in component.values()}
    incoming = {s: set() for s in component.values()}
    for u, v in directed:
        a, b = component[u], component[v]
        if a != b:
            outgoing[a].add(b)
            incoming[b].add(a)
    pending = {s: len(outgoing[s]) for s in outgoing}
    ready = [s for s in outgoing if not outgoing[s]]
    targets = {s: {s} if not outgoing[s] else set() for s in outgoing}
    terminal_kind = {
        s: "recirculating"
        if len(s) > 1 or any((v, v) in directed for v in s)
        else "sink"
        if incoming[s]
        else "quiescent"
        for s in ready
    }
    while ready:
        s = ready.pop()
        for parent in incoming[s]:
            targets[parent].update(targets[s])
            pending[parent] -= 1
            if not pending[parent]:
                ready.append(parent)
    rows = {}
    for v in nodes:
        terminals = frozenset(targets[component[v]])
        if not terminals:
            raise AssertionError("finite condensation must reach a terminal")
        kind = (
            "ambiguous" if len(terminals) > 1 else terminal_kind[next(iter(terminals))]
        )
        rows[v] = (terminals, kind, next(iter(terminals)) if kind == "sink" else None)
    return dict(
        rows=rows,
        node_components=component,
        components=frozenset(outgoing),
        terminal_kind=terminal_kind,
        cyclic=frozenset(
            s for s in outgoing if len(s) > 1 or any((v, v) in directed for v in s)
        ),
    )


def terminal_regions(nodes, edges):
    return flow_analysis(nodes, edges)["rows"]


def flow_view(nodes, edges):
    """Research projection of SCC evidence, not the native observable/schema."""
    value = flow_analysis(nodes, edges)
    components = sorted(
        value["components"], key=lambda s: tuple(sorted(map(node_key, s)))
    )
    indices = {s: i for i, s in enumerate(components)}
    return dict(
        components=[
            dict(
                component_ref=i,
                members=[typed_node(v) for v in sorted(s, key=node_key)],
                cyclic=s in value["cyclic"],
                is_terminal=s in value["terminal_kind"],
                terminal_kind=value["terminal_kind"].get(s),
            )
            for i, s in enumerate(components)
        ],
        nodes=[
            dict(
                node=typed_node(v),
                component_ref=indices[value["node_components"][v]],
                reachable_terminals=sorted(indices[s] for s in value["rows"][v][0]),
                status=value["rows"][v][1],
                assigned_sink=None
                if value["rows"][v][2] is None
                else typed_node(next(iter(value["rows"][v][2]))),
            )
            for v in sorted(nodes, key=node_key)
        ],
    )


def reachability_oracle(nodes, edges):
    """Independent transitive-closure definition; no SCC or DAG algorithm reuse."""
    directed = arcs(nodes, edges)
    reachable = {(u, v): u == v or (u, v) in directed for u in nodes for v in nodes}
    for k in nodes:
        for u in nodes:
            for v in nodes:
                reachable[u, v] |= reachable[u, k] and reachable[k, v]
    classes = {
        frozenset(v for v in nodes if reachable[u, v] and reachable[v, u])
        for u in nodes
    }
    terminal = {
        s for s in classes if not any(u in s and v not in s for u, v in directed)
    }
    rows = {}
    for u in nodes:
        targets = frozenset(s for s in terminal if any(reachable[u, v] for v in s))
        if len(targets) > 1:
            kind = "ambiguous"
        else:
            s = next(iter(targets))
            kind = (
                "recirculating"
                if len(s) > 1 or any((v, v) in directed for v in s)
                else "sink"
                if any(v in s and w not in s for w, v in directed)
                else "quiescent"
            )
        rows[u] = (targets, kind, next(iter(targets)) if kind == "sink" else None)
    return rows


def seed(g, sign, gradient_tolerance, hessian_tolerance):
    q = Fraction.from_float
    return (
        sum(q(x) ** 2 for x in g) < q(gradient_tolerance) ** 2
        and min(sign * x for x in g) > hessian_tolerance
    )


class ProposalChecks(unittest.TestCase):
    def test_all_four_node_directed_graphs(self):
        nodes = tuple(range(4))
        possible = tuple((u, v, 1.0) for u in nodes for v in nodes if u != v)
        for mask in range(1 << len(possible)):
            edges = tuple(e for i, e in enumerate(possible) if mask & (1 << i))
            rows = terminal_regions(nodes, edges)
            self.assertEqual(rows, reachability_oracle(nodes, edges), mask)
            for v, (terminals, kind, assigned) in rows.items():
                if kind == "quiescent":
                    self.assertEqual(terminals, frozenset((frozenset((v,)),)))
                    self.assertFalse(any(v in (u, w) for u, w, _ in edges))
                if assigned is not None:
                    self.assertTrue(
                        all(rows[w][2] == assigned for u, w, _ in edges if u == v)
                    )
            divergence = {
                v: sum(j for u, _, j in edges if u == v)
                - sum(j for _, w, j in edges if w == v)
                for v in nodes
            }
            if all(x == 0 for x in divergence.values()):
                self.assertTrue(all(row[2] is None for row in rows.values()))

    def test_branching_keeps_both_routes_even_with_unequal_weights(self):
        for other in (1.0, 2.0, math.nextafter(0.0, 1.0)):
            rows = terminal_regions((0, 1, 2), ((0, 1, 1.0), (0, 2, other)))
            self.assertEqual(
                rows[0],
                (frozenset((frozenset((1,)), frozenset((2,)))), "ambiguous", None),
            )
            self.assertEqual(rows[1][1:], ("sink", frozenset((1,))))
            self.assertEqual(rows[2][1:], ("sink", frozenset((2,))))

    def test_cycles_quiescence_and_leaking_cycle(self):
        rows = terminal_regions((0, 1, 2), ((0, 1, 1.0), (1, 0, 1.0)))
        self.assertEqual(rows[0][1:], ("recirculating", None))
        self.assertEqual(rows[2][1:], ("quiescent", None))
        rows = terminal_regions((0, 1, 2), ((0, 1, 1.0), (1, 0, 1.0), (1, 2, 1.0)))
        self.assertTrue(all(r[2] == frozenset((2,)) for r in rows.values()))
        self.assertEqual(
            terminal_regions((0,), ((0, 0, 1.0),))[0][1:], ("recirculating", None)
        )

    def test_orientation_order_and_relabel_covariance(self):
        nodes = tuple(range(4))
        edges = ((0, 1, 2.0), (1, 2, 1.0), (1, 3, 1.0))
        expected = terminal_regions(nodes, edges)
        self.assertEqual(
            expected,
            terminal_regions(
                nodes[::-1], tuple((v, u, -j) for u, v, j in reversed(edges))
            ),
        )
        for values in itertools.permutations(nodes):
            mapping = dict(zip(nodes, values))
            actual = terminal_regions(
                values, tuple((mapping[u], mapping[v], j) for u, v, j in edges)
            )
            for v, (targets, kind, assigned) in expected.items():
                mapped = frozenset(frozenset(mapping[x] for x in s) for s in targets)
                sink = (
                    None
                    if assigned is None
                    else frozenset(mapping[x] for x in assigned)
                )
                self.assertEqual(actual[mapping[v]], (mapped, kind, sink))

    def test_parallel_signed_zero_and_invalid_inputs(self):
        nodes = (0, 1)
        rows = terminal_regions(nodes, ((0, 1, 1.0), (0, 1, -1.0)))
        self.assertTrue(all(r[1] == "recirculating" for r in rows.values()))
        rows = terminal_regions(nodes, ((0, 1, 0.0), (0, 1, -0.0)))
        self.assertTrue(all(r[1] == "quiescent" for r in rows.values()))
        for edges in (((0, 1, math.nan),), ((0, 1, math.inf),), ((0, 2, 1.0),)):
            with self.assertRaises(ValueError):
                terminal_regions(nodes, edges)
        with self.assertRaises(ValueError):
            terminal_regions((0, 0), ())
        self.assertEqual(terminal_regions((), ()), {})

    def test_strict_seed_boundaries_and_sign(self):
        self.assertFalse(seed((1.0, 2.0, 2.0), 1, 3.0, 0.5))
        self.assertTrue(seed((1.0, 2.0, 2.0), 1, math.nextafter(3.0, math.inf), 0.5))
        for cutoff, expected in (
            (math.nextafter(1.0, 0.0), True),
            (1.0, False),
            (math.nextafter(1.0, math.inf), False),
        ):
            self.assertEqual(seed((1.0, 1.0, 1.0), 1, 4.0, cutoff), expected)
        self.assertFalse(seed((1.0, 1.0, 1.0), -1, 4.0, 0.5))
        self.assertTrue(seed((-1.0, -1.0, -1.0), -1, 4.0, 0.5))

    def test_nonterminal_cycle_is_visible_despite_same_terminal_and_divergence(self):
        nodes = ("a", "b", "s")
        plain = (("a", "b", 1.0), ("b", "a", 0.0), ("b", "s", 1.0))
        cyclic = (("a", "b", 2.0), ("b", "a", 1.0), ("b", "s", 1.0))
        self.assertEqual(
            terminal_regions(nodes, plain), terminal_regions(nodes, cyclic)
        )
        for edges in (plain, cyclic):
            divergence = tuple(
                sum(j for u, _, j in edges if u == v)
                - sum(j for _, w, j in edges if w == v)
                for v in nodes
            )
            self.assertEqual(divergence, (1.0, 0.0, -1.0))
        view = flow_view(nodes, cyclic)
        self.assertNotEqual(flow_view(nodes, plain), view)
        own = view["components"][view["nodes"][0]["component_ref"]]
        self.assertEqual(own["members"], [typed_node("a"), typed_node("b")])
        self.assertTrue(own["cyclic"])
        self.assertFalse(own["is_terminal"])
        self.assertIsNone(own["terminal_kind"])
        # Reachable recirculation is independent of a node's own cyclicity.
        view = flow_view(("a", "b"), (("a", "b", 1.0), ("b", "b", 1.0)))
        self.assertEqual([n["status"] for n in view["nodes"]], ["recirculating"] * 2)
        self.assertEqual([s["cyclic"] for s in view["components"]], [False, True])
        self.assertFalse(
            flow_view(("a",), (("a", "a", 0.0),))["components"][0]["cyclic"]
        )

    def test_typed_wire_identity_and_canonical_order(self):
        nodes = (0, "0", "")
        edges = ((0, "", 1.0), ("0", "", 1.0))
        expected = flow_view(nodes, edges)
        self.assertEqual(json.loads(json.dumps(expected)), expected)
        self.assertEqual(
            [n["node"] for n in expected["nodes"]],
            [typed_node(0), typed_node(""), typed_node("0")],
        )
        self.assertTrue(
            all(n["assigned_sink"] == typed_node("") for n in expected["nodes"])
        )
        for order in itertools.permutations(nodes):
            self.assertEqual(flow_view(order, edges[::-1]), expected)
        unassigned = flow_view(nodes, ())
        self.assertEqual(len(unassigned["nodes"]), 3)
        self.assertTrue(all(n["assigned_sink"] is None for n in unassigned["nodes"]))
        for invalid in (True, 0.0, None, 2**53):
            with self.assertRaises(ValueError):
                flow_view((invalid,), ())

    def test_captured_signs_and_bindings_cannot_be_replaced_by_tolerance(self):
        # Synthetic read operands: a contract discriminant, not native replay.
        nodes = (0, "0")
        tiny = math.nextafter(0.0, 1.0)
        state_digest = seal(dict(scientific_input="fixed synthetic preimage"))[
            "record_digest"
        ]
        observations, assignments = [], []
        for j in (tiny, -tiny, 0.0, -0.0):
            self.assertLessEqual(abs(j), tiny)  # all within one exact-zero error bound
            witness = dict(
                edges=[
                    dict(
                        edge_id="e",
                        tail=typed_node(0),
                        head=typed_node("0"),
                        current=j.hex(),
                    )
                ]
            )
            binding = dict(
                role="current",
                role_state_digest=state_digest,
                numerical_policy="synthetic-fixed-policy",
                read_stage="fresh",
                context="fixed synthetic context",
                operand_digest=seal(witness)["record_digest"],
            )
            observation = seal(binding)
            observations.append(observation)
            assignments.append(flow_view(nodes, ((0, "0", j),)))
            self.assertEqual(
                float.fromhex(witness["edges"][0]["current"]).hex(), j.hex()
            )
            self.assertEqual(json.loads(json.dumps(observation)), observation)
            for key, different in (
                ("role", "reset"),
                ("numerical_policy", "other-policy"),
                ("context", "other-context"),
                ("read_stage", "consumed"),
            ):
                self.assertNotEqual(
                    seal(dict(binding, **{key: different})), observation
                )
        self.assertEqual(len({o["role_state_digest"] for o in observations}), 1)
        self.assertEqual(len({o["record_digest"] for o in observations}), 4)
        self.assertNotEqual(assignments[0], assignments[1])
        self.assertNotEqual(assignments[0], assignments[2])
        self.assertEqual(assignments[2], assignments[3])  # both zeros omit arcs
        # Exact capture replay compares the complete binding; tolerance equality
        # and even equal labels do not identify the same represented observation.
        self.assertNotEqual(observations[2], observations[3])

    def test_seed_squares_do_not_round_underflow_or_overflow_first(self):
        tiny = math.nextafter(0.0, 1.0)
        for g, threshold, h in ((2 * tiny, 4 * tiny, tiny), (1e200, 2e200, 1.0)):
            self.assertFalse(g * g < threshold * threshold)
            self.assertTrue(seed((g,) * 3, 1, threshold, h))
        self.assertFalse(seed((tiny,) * 3, 1, tiny, 0.0))
        self.assertFalse(seed((1e200,) * 3, 1, 1e200, 1.0))


def audit():
    side = ROOT / INV / "tools/exploratory-side-tool"
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, object_dependents

    context = load_current_forensic_context(ROOT, side)
    ids = [
        "D10.2-EC-PARENT-" + s
        for s in (
            "BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
            "GRC9-HYBRID-SPARK",
            "GRC9-CHILD-BASIN-STABILIZATION",
            "BASE-DISABLED-LIFECYCLE",
            "L-SNAPSHOT-RESET",
            "L-ATOMICITY",
        )
    ]
    traces = {cid: contract_provenance(context, cid) for cid in ids}
    traces["GRC9-CHILD-BASIN-STABILIZATION"] = object_dependents(
        context, "GRC9-CHILD-BASIN-STABILIZATION"
    )
    misses = []
    for oid in ("GRC_basin_identity", "GRC9-BASIN-IDENTITY", "BASE-GRC-BASIN-IDENTITY"):
        try:
            object_dependents(context, oid)
        except KeyError as exc:
            misses.append(
                dict(query="object_dependents", object_id=oid, error=str(exc))
            )
        else:
            raise ValueError("newly resolved basin authority; re-review the finding")
    names = [
        SELF,
        PROPOSAL,
        REVIEW,
        "specs/grc-v4-numerical-policy.md",
        "specs/grc-9-v4-spec.md",
        "specs/grc-v3-spec.md",
        "specs/grc-9-v3-spec.md",
        INV + "drafts/2026-09-GRC-V4.md",
        INV + "drafts/GRCV4-proposal.md",
        INV + "decisions/D4GeometryMobilityAndTopologyOwnership.json",
        "src/pygrc/models/grc_9_v4_lifecycle.py",
        "src/pygrc/models/grc_9_v4_api_lifecycle.py",
        "src/pygrc/models/grc_9_v4_contracts.py",
        "src/pygrc/models/grc_9_v3_runtime.py",
    ]
    return seal(
        dict(
            schema="p9101a-basin-authority-audit-v1",
            status="open_authority_gap_review_corrected_proposal_pending_acceptance",
            baseline_commit="1735d671",
            policy_id="grc9v4-terminal-flow-regions-v1",
            proposal_accepted=False,
            runtime_implemented=False,
            native_execution=False,
            accepted_graph_changed=False,
            full_GRC9V4_conformance=False,
            review_disposition=dict(
                mathematical_verdict="pass_finite_represented_flow_rule",
                corrected_findings=["BIF-1", "BIF-2", "BIF-3"],
                external_pressure_artifacts_supplied=False,
                native_replay_validated=False,
            ),
            traces=traces,
            unresolved_object_queries=misses,
            inventory_observation=[
                k for k in sorted(context.nodes) if "basin" in k.lower()
            ],
            observation_ceiling="Source audit and unresolved queries expose no selected enabled-V4 membership/identity producer in the inspected contracts; absence of one queried ID alone is not a universal negative proof.",
            open_debt=dict(
                debt_id="P9-10.1a-DEBT-BASIN-IDENTITY",
                status="open",
                origin="P9-9.6 basin_surface",
                blocking_scope="baseline enabled-GRC9V4 basin interface and lifecycle identity",
                missing_contract="membership, branching/cycle/no-flow disposition, exact read stage, label lifetime, snapshot/reset/atomic behavior",
                forbidden_assumptions=[
                    "seed_predicate_defines_partition",
                    "disabled_classifier_is_enabled_authority",
                    "flow_region_is_stable_attractor",
                    "diagnostic_label_change_is_physical_basin_birth",
                ],
                resolution="Review/adjudicate successor claim, admit authority, propagate proposal then paper then V4 spec/schema, then native P9-10.1a conformance.",
                accepted_predecessors_reopened=False,
            ),
            proposed_claim=dict(
                claim_id="P9-10.1a-CL-P-BASIN-001",
                claim_class="proposed",
                status="not_admitted",
                statement="Select represented all-route terminal-flow regions with separate geometric seed attributes as the baseline enabled-GRC9V4 basin surface; no dynamical attraction or completion claim.",
            ),
            source_refs=[ref(n) for n in names],
        )
    )


def conditional_evidence(authority, tests):
    return seal(
        dict(
            schema="p9101a-basin-proposal-checks-v1",
            outcome="passed_conditional_finite_graph_checks",
            tests=tests,
            exhaustive_directed_graphs=4096,
            nodes_per_exhaustive_graph=4,
            relabelings=24,
            review_regressions=[
                "nonterminal_and_self_loop_cycle_evidence",
                "typed_node_identity_and_canonical_order",
                "captured_read_sign_and_binding_distinctions_not_native_replay",
                "exact_seed_squares_underflow_overflow",
                "exhaustive_forward_closure_quiescent_isolation_divergence_free_unit_currents",
            ],
            native_model_runs=0,
            proposal_accepted=False,
            claim_ceiling="Finite represented-graph rule only; not realization feasibility, attraction stability or native lifecycle conformance.",
            authority_audit_digest=authority["record_digest"],
            source_refs=[ref(SELF), ref(PROPOSAL), ref(REVIEW)],
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProposalChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise SystemExit(1)
    authority = audit()
    evidence = conditional_evidence(authority, result.testsRun)
    for name, value in (
        ("AuthorityAudit.json", authority),
        ("ConditionalChecks.json", evidence),
    ):
        path = ROOT / BASE / name
        if args.write:
            with path.open("x") as f:
                json.dump(value, f, indent=2)
                f.write("\n")
        elif json.loads(path.read_bytes()) != value:
            raise ValueError("retained proposal evidence drift: " + name)
    print(
        json.dumps(
            {
                "authority_gap": "open",
                "conditional_tests": result.testsRun,
                "native_runs": 0,
                "proposal_accepted": False,
            }
        )
    )


if __name__ == "__main__":
    main()
