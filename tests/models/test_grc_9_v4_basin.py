"""Native basin conformance: pure graph pressure and four small lifecycle fixtures."""

from copy import deepcopy
from dataclasses import replace
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from jsonschema.exceptions import ValidationError

from pygrc.models import GRC9V4
from pygrc.models import grc_9_v4_basin as b
from pygrc.models import grc_9_v4_crossing as crossing
from pygrc.models.grc_9_v4_contracts import GRC9V4Configuration
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortGraph,
    GRC9V4PortEdge,
    GRC9V4PortEndpoint,
)
from tests.models.test_grc_9_v4 import (
    configuration,
    seed,
    branch_request,
    migration_request,
)
from tests.models.test_grc_9_v4_crossing import step_request

EVIDENCE = {}


def graph(nodes, pairs):
    ports = dict.fromkeys(nodes, 0)
    edges = []
    for i, (u, v) in enumerate(pairs):
        ports[u] += 1
        tail = GRC9V4PortEndpoint(u, ports[u])
        ports[v] += 1
        edges.append(
            GRC9V4PortEdge(str(i), "boundary", tail, GRC9V4PortEndpoint(v, ports[v]))
        )
    return GRC9V4PortGraph(tuple(nodes), tuple(edges))


def synthetic(g, currents, *, gradient=(0.0, 0.0, 0.0), gt=1.0, ht=0.01):
    # Explicit synthetic operands: not a native admitted state or read.
    binding = dict(
        role="current",
        role_state_digest="0" * 64,
        profile_id="synthetic",
        model_identity="synthetic",
        graph_digest=g.graph_digest,
        orientation_identity=g.orientation_identity,
        context_contract_id="synthetic",
        context_value_digest=None,
        numerical_policy_id="synthetic",
        scalar_backend_id="binary64",
        evaluator_id="synthetic",
        release_id="synthetic",
        stage="fresh_poststate_readmission",
        root_certificate_binding=None,
        read_identity=None,
    )
    witness = dict(
        edges=[
            dict(
                edge_id=e.edge_id,
                tail=b.typed_node(e.tail.node_id),
                head=b.typed_node(e.head.node_id),
                current=float(j).hex(),
            )
            for e, j in zip(g.edges, currents, strict=True)
        ],
        rows=[
            dict(
                node=b.typed_node(n),
                gradient=[float(x).hex() for x in gradient],
                signed_hessian_diagonal=[float(x).hex() for x in gradient],
                row_net_flux=[(0.0).hex()] * 3,
            )
            for n in sorted(g.live_node_ids, key=b.node_key)
        ],
        gradient_tolerance=float(gt).hex(),
        hessian_tolerance=float(ht).hex(),
        hessian_sign=1,
    )
    return b.observation(binding, witness)


class BasinGraphTests(unittest.TestCase):
    def test_all_three_node_supports_against_transitive_closure(self):
        nodes = (0, 1, 2)
        pairs = tuple(itertools.permutations(nodes, 2))
        g = graph(nodes, pairs)
        for mask in range(64):
            currents = tuple(float(bool(mask & (1 << i))) for i in range(6))
            value = synthetic(g, currents)
            b.validate_observation(value, g)
            arcs = {(u, v) for (u, v), j in zip(pairs, currents) if j}
            reach = {(u, v): u == v or (u, v) in arcs for u in nodes for v in nodes}
            for k in nodes:
                for u in nodes:
                    for v in nodes:
                        reach[u, v] |= reach[u, k] and reach[k, v]
            components = {
                frozenset(v for v in nodes if reach[u, v] and reach[v, u])
                for u in nodes
            }
            terminals = {
                s for s in components if not any(u in s and v not in s for u, v in arcs)
            }
            for row in value["nodes"]:
                u = row["node"]["value"]
                reached = {s for s in terminals if any(reach[u, v] for v in s)}
                expected = None
                if len(reached) == 1:
                    s = next(iter(reached))
                    if len(s) == 1 and any(v in s and u not in s for u, v in arcs):
                        expected = b.typed_node(next(iter(s)))
                self.assertEqual(row["assigned_sink"], expected, (mask, u))

    def test_partial_coverage_cycles_loops_and_typed_empty_string_sink(self):
        for nodes, pairs, currents in (
            ((), (), ()),
            (("",), (), ()),
            ((0, "0", ""), ((0, ""), ("0", "")), (1.0, 1.0)),
            ((0, 1, 2, "isolate"), ((0, 1), (1, 0), (1, 2)), (1.0, 1.0, 1.0)),
            ((0, 1, 2), ((0, 1), (1, 1), (0, 2)), (1.0, 1.0, 1.0)),
        ):
            g = graph(nodes, pairs)
            v = synthetic(g, currents)
            b.validate_observation(v, g)
            members = [n for c in v["components"] for n in c["members"]]
            self.assertEqual(
                sorted(members, key=lambda n: b.node_key(n["value"])),
                [r["node"] for r in v["nodes"]],
            )
            assigned = [r["node"] for r in v["nodes"] if r["basin_id"] is not None]
            region = [n for r in v["regions"] for n in r["members"]]
            self.assertEqual(
                sorted(region, key=lambda n: b.node_key(n["value"])), assigned
            )
        self.assertEqual(v["nodes"][0]["status"], "ambiguous")
        self.assertTrue(any(c["cyclic"] for c in v["components"]))

    def test_signs_parallel_routes_and_exact_seed_extremes(self):
        g = graph((0, 1), ((0, 1), (0, 1)))
        opposite = synthetic(g, (5e-324, -5e-324))
        self.assertFalse(opposite["regions"])
        self.assertEqual(opposite["nodes"][0]["status"], "recirculating")
        zero = synthetic(g, (0.0, 0.0))
        negative_zero = synthetic(g, (-0.0, 0.0))
        self.assertEqual(zero["nodes"], negative_zero["nodes"])
        self.assertNotEqual(
            zero["observation_digest"], negative_zero["observation_digest"]
        )
        g = graph(("",), ())
        cases = (
            ((1.0, 0.0, 0.0), 1.0, 0.01, False),
            ((0.1,) * 3, 1.0, 0.1, False),
            ((2e-323,) * 3, 8e-323, 5e-324, True),
            ((1e200,) * 3, 2e200, 1.0, True),
        )
        for gradient, gt, ht, expected in cases:
            v = synthetic(g, (), gradient=gradient, gt=gt, ht=ht)
            self.assertEqual(v["nodes"][0]["seed"], expected)
            self.assertEqual(v["regions"], [])

    def test_wire_semantic_mutations_and_canonical_partial_order(self):
        g = graph(("isolate", "", 0, "0"), ((0, ""), ("0", "")))
        value = synthetic(g, (1.0, 1.0), gradient=(0.1,) * 3)
        self.assertEqual(
            value["regions"][0]["members"], list(map(b.typed_node, (0, "", "0")))
        )
        self.assertEqual(
            value["regions"][0]["seed_members"], value["regions"][0]["members"]
        )
        projected = b.identity_projection(value)
        self.assertEqual([r["node"] for r in projected], value["regions"][0]["members"])
        mutations = (
            lambda v: v["regions"].clear(),
            lambda v: v["regions"][0]["members"].reverse(),
            lambda v: v["regions"][0]["seed_members"].reverse(),
            lambda v: v["regions"][0]["seed_members"].pop(),
            lambda v: v["nodes"].append(deepcopy(v["nodes"][0])),
            lambda v: v["components"][0].update(cyclic=True),
            lambda v: v["nodes"][0].update(component_ref=999),
            lambda v: v["witness"]["edges"].reverse(),
            lambda v: v["witness"]["rows"].pop(),
            lambda v: v["witness"].update(gradient_tolerance=(-1.0).hex()),
            lambda v: v["witness"]["edges"][0].update(current="0x1p+0"),
            lambda v: v["witness"]["edges"][0].update(current=(-1.0).hex()),
        )
        for mutation in mutations:
            v = deepcopy(value)
            mutation(v)
            v["operand_digest"] = b.digest(v["witness"])
            v["observation_digest"] = b.digest(
                {
                    k: v[k]
                    for k in (
                        "schema_version",
                        "policy_id",
                        "binding",
                        "operand_digest",
                    )
                }
            )
            with self.assertRaises((ValueError, ValidationError)):
                b.validate_observation(v, g)
        # Relabeling/order and orientation transport affect graph hashes, not route selection.
        swapped = graph(("isolate", "", 0, "0"), (("", 0), ("", "0")))
        moved = synthetic(swapped, (-1.0, -1.0), gradient=(0.1,) * 3)
        self.assertEqual(
            [n["assigned_sink"] for n in value["nodes"]],
            [n["assigned_sink"] for n in moved["nodes"]],
        )
        from tests.models.test_grc_9_v4_contracts import PublicContractTests
        from pygrc.models.grc_9_v4 import GRC9V4ExecutionUnavailable

        PublicContractTests.setUpClass()
        for name, old in PublicContractTests.configs.items():
            cfg = replace(old, specialization=old.specialization.with_basin_policy())
            wire = cfg.to_payload()
            self.assertEqual(GRC9V4Configuration.from_payload(wire).to_payload(), wire)
            for version in ("grc9v4-configuration-v1", "grc9v4-configuration-v3"):
                with self.assertRaises(ValueError):
                    GRC9V4Configuration.from_payload(dict(wire, schema_version=version))
            if name not in ("C_OS", "C_CI", "A_CI", "A_PC", "A_OS", "C_PC", "C_CI_PC"):
                with self.assertRaises(GRC9V4ExecutionUnavailable):
                    GRC9V4(cfg)


class NativeBasinTests(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select a native family")
        old = GRC9V4.from_config(configuration(cls.FAMILY))
        cls.config = replace(
            old.configuration,
            specialization=old.configuration.specialization.with_basin_policy(),
        )

    def model(self):
        return GRC9V4(self.config)

    def test_fresh_both_roles_configuration_and_observation(self):
        m = self.model()
        p = m._operation._published
        wire = m.configuration.to_payload()
        self.assertEqual(wire["schema_version"], "grc9v4-configuration-v2")
        self.assertEqual(GRC9V4Configuration.from_payload(wire).to_payload(), wire)
        with patch.object(b, "_read_once", wraps=b._read_once) as reads:
            obs = m.compute_observables()
            self.assertEqual(reads.call_count, 1)
        v = obs["basin_attributes"]
        native = p.owner.state
        self.assertEqual(
            v["binding"]["role_state_digest"], b.digest(native.scientific_payload)
        )
        self.assertEqual(
            [float.fromhex(e["current"]) for e in v["witness"]["edges"]],
            obs["authoritative_current"]["values"],
        )
        self.assertEqual(v["binding"]["scalar_backend_id"], "flint")
        for r in v["witness"]["rows"]:
            i = p.reference.graph.live_node_ids.index(r["node"]["value"])
            self.assertEqual(
                list(map(float.fromhex, r["gradient"])), obs["row_gradient"][i]
            )
            self.assertEqual(
                list(map(float.fromhex, r["signed_hessian_diagonal"])),
                obs["signed_row_hessian"][i],
            )
        pair = m._operation._basin_pair(p)
        self.assertEqual(pair[0].inputs.current, native.inputs.current)
        self.assertEqual(pair[1].inputs.current, native.inputs.reset)
        self.assertNotEqual(native.inputs.current, native.inputs.reset)
        self.assertNotEqual(
            pair[0].observation["binding"], pair[1].observation["binding"]
        )
        self.assertEqual(
            pair[1].observation["binding"]["role_state_digest"],
            b.digest(native.reset_payload),
        )
        self.assertEqual(m.state.lifecycle.basin_attributes.to_dict(), v)
        self.assertEqual(
            [r.to_dict() for r in m.state.lifecycle.basin_identity],
            obs["basin_identity"],
        )
        self.assertNotIn("basin_attributes", native.scientific_payload)
        if self.FAMILY.endswith("CI"):
            root = pair[0].read
            self.assertIs(pair[0].point, root.selected.point)
            self.assertIn("joint-root", v["binding"]["root_certificate_binding"])
            self.assertEqual(
                pair[0].point.inputs.geometry, root.selected.inputs.geometry
            )
        EVIDENCE["capture"] = dict(
            family=self.FAMILY,
            model_identity=m.active_model_identity,
            configuration_digest=b.digest(wire),
            observation_digests=[x.observation["observation_digest"] for x in pair],
            one_native_read_per_observation=True,
            both_roles=True,
            observations=[x.observation.to_dict() for x in pair],
        )

    def test_explicit_policy_migration_steps_expansion_and_reset_replay(self):
        m = GRC9V4.from_config(configuration(self.FAMILY))
        old = m.active_model_identity
        self.assertNotIn("basin_attributes", m.compute_observables())
        self.assertNotIn("basin_attributes", m.list_capabilities())
        with self.assertRaises(ValueError):
            m.snapshot(replay_mode="state_only")
        original = m.configuration.current
        result = m.migrate_basin_policy("enable-basin")
        self.assertTrue(result.committed, result.failure)
        self.assertNotEqual(old, m.active_model_identity)
        self.assertEqual(m.configuration.current, original)
        self.assertIn("basin_attributes", m.list_capabilities())
        with self.assertRaises(ValueError):
            m.migrate_basin_policy("again")
        self.assertEqual(m.duplicate().snapshot(), m.snapshot())
        # Baseline fixture expansion request remains a mechanical declaration;
        # target model identity is reconstructed with the same v2 specialization.
        action = next(a for a in seed(self.FAMILY)["journal"] if a["kind"] == "expand")
        self.assertTrue(m.step_v4_input(step_request("prefix", 0)).committed)
        request = dict(
            action["request"],
            target_specialization_id=m.configuration.specialization.specialization_id,
            source_state_digest=m._operation._published.owner.state.scientific_digest,
        )
        result = m.expand(GRC9V4ExpansionRequestInput.from_payload(request))
        self.assertTrue(result.committed, result.failure)
        with patch.object(b, "_read_once", wraps=b._read_once) as reads:
            result = m.step_v4_input(step_request("after-event"))
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(reads.call_count, 2)
        self.assertEqual(len(result.observables["basin_attributes"]["nodes"]), 17)
        m.reset()
        m.rebase_reset_baseline()
        m.reset()
        exact = m.snapshot()
        self.assertEqual(m.duplicate().snapshot(), exact)
        state_only = m.snapshot(replay_mode="state_only")
        self.assertIsNone(state_only["owner"]["basin"]["current_observation"])
        restored = GRC9V4.from_state(state_only)
        self.assertEqual(restored.snapshot(replay_mode="state_only"), state_only)
        self.assertEqual(
            restored.compute_observables()["basin_attributes"],
            m.compute_observables()["basin_attributes"],
        )
        m.set_state(m.state)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "basin.json"
            m.save(path)
            self.assertEqual(GRC9V4.load(path).snapshot(), m.snapshot())
        EVIDENCE["lifecycle"] = dict(
            expansion=True,
            positive_target_step=True,
            reset_rebase=True,
            explicit_policy_migration=True,
            exact_replay=True,
            state_only=True,
            assignment=True,
            save_load=True,
            final_checkpoint_digest=b.digest(exact),
            final_observations=exact["owner"]["basin"],
        )

    def test_replay_semantics_tampering_and_atomic_failures(self):
        m = self.model()
        snap = m.snapshot()
        pointer = m._operation._published
        for change in ("swap", "missing", "stale_root", "row", "order"):
            bad = deepcopy(snap)
            ext = bad["owner"]["basin"]
            v = ext["current_observation"]
            if change == "swap":
                ext["current_observation"], ext["reset_observation"] = (
                    ext["reset_observation"],
                    v,
                )
            elif change == "missing":
                ext["reset_observation"] = None
            elif change == "stale_root":
                v["binding"]["root_certificate_binding"] = "stale-joint-geometry"
            elif change == "row":
                v["witness"]["rows"][0]["gradient"][0] = (0.5).hex()
            elif change == "order":
                v["nodes"].reverse()
            if change not in ("swap", "missing"):
                v["operand_digest"] = b.digest(v["witness"])
                v["observation_digest"] = b.digest(
                    {
                        k: v[k]
                        for k in (
                            "schema_version",
                            "policy_id",
                            "binding",
                            "operand_digest",
                        )
                    }
                )
            with self.assertRaises((ValueError, ValidationError)):
                m.set_state(replace(m.state, checkpoint=json.dumps(bad).encode()))
            self.assertIs(m._operation._published, pointer)
        captured = b.capture

        def fail_reset(state, role):
            if role == "reset":
                raise ValueError("injected reset-only diagnostic failure")
            return captured(state, role)

        operations = (
            lambda: m.step_v4_input(step_request("rejected")),
            m.reset,
            m.rebase_reset_baseline,
            lambda: m.migrate_profile(migration_request(m, m.configuration.reference)),
        )
        for operation in operations:
            with patch.object(b, "capture", side_effect=fail_reset):
                with self.assertRaises(ValueError):
                    operation()
            self.assertIs(m._operation._published, pointer)
        expanded = self.model()
        self.assertTrue(expanded.step_v4_input(step_request("prefix", 0)).committed)
        expansion_pointer = expanded._operation._published
        req = dict(
            next(a for a in seed(self.FAMILY)["journal"] if a["kind"] == "expand")[
                "request"
            ],
            target_specialization_id=expanded.configuration.specialization.specialization_id,
            source_state_digest=expanded._operation._published.owner.state.scientific_digest,
        )
        with patch.object(b, "capture", side_effect=fail_reset):
            with self.assertRaises(ValueError):
                expanded.expand(GRC9V4ExpansionRequestInput.from_payload(req))
        self.assertIs(expanded._operation._published, expansion_pointer)
        with patch.object(
            crossing.GRC9V4BranchOperation,
            "_publish",
            side_effect=RuntimeError("late publication"),
        ):
            with self.assertRaises(RuntimeError):
                m.step_v4_input(step_request("late"))
        self.assertIs(m._operation._published, pointer)
        self.assertEqual(m.snapshot(), snap)
        # A successful ordinary change makes the old root/point an invalid read.
        old = m._operation._basin_pair(pointer)[0]
        self.assertTrue(m.step_v4_input(step_request("freshness")).committed)
        with patch.object(b, "_read_once", return_value=(old.read, old.point)):
            with self.assertRaises(ValueError):
                m.compute_observables()
        EVIDENCE["pressure"] = dict(
            rehashed_replay_mutations=5,
            reset_only_failures=5,
            complete_publication_rollback=True,
            stale_read_rejected=True,
            late_publication_rollback=True,
        )

    def test_disabled_delegation_and_profile_migration_preserve_boundaries(self):
        m = self.model()
        ref = m.configuration.reference
        result = m.migrate_profile(migration_request(m, ref))
        self.assertTrue(result.committed, result.failure)
        self.assertTrue(m.migrate_branch(branch_request(m, "disable")).committed)
        legacy = m._operation._published.owner
        self.assertEqual(m.compute_observables(), legacy.compute_observables())
        self.assertNotIn("basin_attributes", m.compute_observables())
        disabled = m.snapshot()
        self.assertNotIn("basin", disabled["owner"])
        self.assertEqual(GRC9V4.from_state(disabled).snapshot(), disabled)
        self.assertTrue(m.migrate_branch(branch_request(m, "enable", ref)).committed)
        self.assertIn("basin_attributes", m.compute_observables())
        self.assertEqual(m.duplicate().snapshot(), m.snapshot())
        EVIDENCE["compatibility"] = dict(
            exact_disabled_observables=True,
            enabled_return=True,
            same_profile_migration=True,
            full_conformance=False,
        )


class COSBasinTests(NativeBasinTests):
    FAMILY = "C_OS"


class CCIBasinTests(NativeBasinTests):
    FAMILY = "C_CI"


class ACIBasinTests(NativeBasinTests):
    FAMILY = "A_CI"


class APCBasinTests(NativeBasinTests):
    FAMILY = "A_PC"


if __name__ == "__main__":
    unittest.main()
