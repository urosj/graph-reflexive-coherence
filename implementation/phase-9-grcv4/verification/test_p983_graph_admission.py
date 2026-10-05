"""Pressure the prepared larger-graph contract without a constitutive run."""

import json
import unittest
from copy import deepcopy
from fractions import Fraction as Q

import numpy as np
import prepare_p983_graph_admission as prep

from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_profile import GRCV4Profile, list_supported_profiles


class LargerGraphPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = list_supported_profiles()
        cls.record = prep.prepare()

    def test_retained_record_reconstructs_and_registry_does_not_change(self):
        retained = json.loads((prep.ROOT / prep.RECORD).read_text())
        self.assertEqual(
            canonical_json_bytes(retained), canonical_json_bytes(self.record)
        )
        self.assertEqual(list_supported_profiles(), self.registry)
        self.assertFalse(retained["execution"]["runtime_admitted"])
        self.assertEqual(retained["execution"]["receipts"], [])
        self.assertEqual(
            {row["family"] for row in retained["families"]}, set(prep.FAMILIES)
        )

    def test_literal_topology_counts_connectivity_and_port_occupancy(self):
        graph = GRC9V4PortGraph.from_envelope(self.record["source"]["port_graph"])
        self.assertEqual(graph.live_node_ids, tuple(range(100)))
        actual = {(e.tail.node_id, e.head.node_id) for e in graph.edges}
        expected = {(i, (i + d) % 100) for i in range(100) for d in (1, 2, 3, 4)}
        expected.remove((50, 54))
        expected.add((0, 54))
        self.assertEqual(actual, expected)
        tokens = [
            (end.node_id, end.port) for e in graph.edges for end in (e.tail, e.head)
        ]
        self.assertEqual(len(set(tokens)), 800)
        # The untouched offset-one Hamiltonian cycle proves connectedness.
        self.assertTrue({(i, (i + 1) % 100) for i in range(100)} <= actual)
        self.assertEqual(
            self.record["graph_facts"]["source"]["degree_histogram"],
            {"7": 1, "8": 98, "9": 1},
        )

    def test_operator_norms_against_literal_integer_matrices(self):
        for side in ("source", "target"):
            graph = GRC9V4PortGraph.from_envelope(self.record[side]["port_graph"])
            n, m = len(graph.live_node_ids), len(graph.edges)
            indices = {v: i for i, v in enumerate(graph.live_node_ids)}
            b = np.zeros((n, m), dtype=np.int64)
            incidence = np.zeros((n, m), dtype=np.int64)
            for j, e in enumerate(graph.edges):
                b[indices[e.tail.node_id], j] = -1
                b[indices[e.head.node_id], j] = 1
                incidence[indices[e.tail.node_id], j] = 1
                incidence[indices[e.head.node_id], j] = 1
            gram = b.T @ b
            mask_twice = incidence.T @ incidence
            facts = self.record["graph_facts"][side]
            self.assertEqual(
                int(np.abs(b).sum(axis=1).max()), facts["incidence_infinity_norm"]
            )
            self.assertEqual(
                int(np.abs(gram).sum(axis=1).max()), facts["edge_gram_infinity_norm"]
            )
            mask = facts["star_mask_infinity_norm"]
            self.assertEqual(
                Q(int(mask_twice.sum(axis=1).max()), 2),
                Q(mask["numerator"], mask["denominator"]),
            )
            # Independent floating spectrum is only a pressure cross-check of
            # the exact connected-graph theorem, never its certificate.
            spectrum = np.linalg.eigvalsh((b @ b.T).astype(float))
            proof = self.record["reference_selector_proof"][side]
            lower = proof["nonzero_reference_laplacian_lower"]
            self.assertGreater(spectrum[1], lower["numerator"] / lower["denominator"])
            self.assertEqual(facts["cycle_rank"], 301)

    def test_target_resource_lineage_and_equal_charge_both_roles(self):
        target = self.record["target"]
        event_id = self.record["mechanical_plan"]["event_id"]
        nodes = target["port_graph"]["live_node_ids"]
        for role in ("current", "reset"):
            source_values = self.record["source"]["roles"][role]["C"]
            values = dict(zip(nodes, target["roles"][role]["C"], strict=True))
            self.assertEqual(sum(map(Q, values.values())), 200)
            for node in range(1, 100):
                self.assertEqual(values[node], source_values[node])
            self.assertEqual(
                [values[event_id + f"/satellite/{i}"] for i in (1, 2, 3)], [1, 0.5, 0.5]
            )
            for node in nodes:
                if isinstance(node, str) and "/satellite/" not in node:
                    self.assertEqual(values[node], 0)
            self.assertIsNone(target["roles"][role]["W_A"])
            self.assertIsNone(target["roles"][role]["Z_4"])
        self.assertNotEqual(target["roles"]["current"], target["roles"]["reset"])

    def test_legal_size_is_insufficient_and_existing_domains_fail(self):
        for side in ("source", "target"):
            for row in self.record["pc_resource_preflight"][side].values():
                self.assertFalse(row["accepted_M16_fits"])
                self.assertTrue(row["proposed_M32_fits_resources_only"])
            rg = self.record["native_rg2b_scope_preflight"][side]
            self.assertFalse(rg["tree17_hypothesis"])
            self.assertFalse(rg["gram_le_10"])
            self.assertFalse(rg["star_mask_le_5"])
        payload = deepcopy(self.record["source"]["port_graph"])
        payload.pop("graph_digest")
        # Same 100/400 counts, but reuse a port already occupied at node zero.
        payload["edges"][0]["tail"]["port"] = 9
        with self.assertRaisesRegex(ValueError, "occupied"):
            GRC9V4PortGraph.from_payload(payload)

    def test_parameter_change_reidentifies_without_rewriting_old_declaration(self):
        original = self.record["source"]["profile"]
        graph = prep.source_graph()
        vectors = json.loads((prep.ROOT / prep.VECTORS).read_text())
        request = deepcopy(self.record["request"])
        request["kappa_H"] = 0.25
        changed = prep.profile_for(graph, request, vectors)
        self.assertNotEqual(
            changed.complete_profile_id, original["complete_profile_id"]
        )
        self.assertEqual(changed.params_resolved.geometry.kappa_H, 0.25)
        self.assertEqual(original["params_resolved"]["geometry"]["kappa_H"], 0.5)
        stale = deepcopy(original)
        stale["params_resolved"]["geometry"]["kappa_H"] = 0.25
        with self.assertRaises(ValueError):
            GRCV4Profile.from_canonical_bytes(canonical_json_bytes(stale))

    def test_rehashed_claim_promotion_and_omitted_profile_reject(self):
        for field, value in (("runtime_admitted", True), ("events_committed", 1)):
            bad = deepcopy(self.record)
            bad["execution"][field] = value
            bad["record_digest"] = prep.record_digest(bad)
            with self.assertRaisesRegex(ValueError, "reconstruction"):
                prep.check_record(bad)
        bad = deepcopy(self.record["request"])
        bad["required_families"].pop()
        with self.assertRaisesRegex(ValueError, "ten-family"):
            prep.validate_request(bad)

    def test_unknown_recipe_and_reference_cutoff_not_certified_reject(self):
        for key in ("graph_recipe", "parameter_selection_policy"):
            bad = deepcopy(self.record["request"])
            bad[key] = "silently_change_the_experiment"
            with self.assertRaisesRegex(ValueError, "unsupported"):
                prep.validate_request(bad)
        bad = deepcopy(self.record["request"])
        bad["candidate_overrides"]["Lambda_C"] = 1
        with self.assertRaisesRegex(ValueError, "cutoff not certified"):
            prep.prepare(bad)

    def test_actual_materialized_source_matches_prepared_identity(self):
        # Geometry/state construction only: no CandidateCCurrent, OS pass,
        # event operation, current/root/section, or temporal step is called.
        owner = prep.materialize_source(self.record)
        self.assertEqual(
            owner.scientific_payload, self.record["source"]["scientific_payload"]
        )
        self.assertEqual(owner.reset_payload, self.record["source"]["reset_payload"])
        self.assertEqual(len(owner.inputs.current.C), 100)


if __name__ == "__main__":
    unittest.main()
