"""P9-8.0 numerical entry probes, not GRC9V4 runtime conformance.

Frozen allocation/identity vectors are not automatically admitted numerical
fixtures. Preserve their exact cutoff-boundary counterexample without changing
the release or using a successful nearby primitive as full-profile admission.
"""
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from pygrc.models.grc_v4_candidate_c import CandidateCSelector, CandidateCStageError
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph, OrientedEdge, VertexScalar, reference_pairings,
)
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState


class SpecializationReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(
            (ROOT / "specs/grc-v4-conformance-vectors.json").read_text()
        )

    def inputs(self, target=False):
        identities = {r["vector_id"]: r for r in self.vectors["identity_vectors"]}
        if target:
            expected = self.vectors["grc9_expansion_vectors"][0]["expected"]
            graph_payload = expected["identity_payloads"]["target_graph"]
            params = expected["identity_payloads"]["target_params"]
            resources = expected["target_resource_by_node"]
        else:
            graph_payload = self.vectors["port_graph_envelope_vectors"][0]["payload"]
            params = identities["IDENTITY-GRCV4-PARAMS-C-OS"]["payload"]
            resources = {n: 3 if n == "source-s" else 0
                         for n in graph_payload["live_node_ids"]}
        graph = GRCV4Graph(
            tuple(graph_payload["live_node_ids"]),
            tuple(OrientedEdge(e["edge_id"], e["tail"]["node_id"], e["head"]["node_id"])
                  for e in graph_payload["edges"]),
        )
        weights = tuple(params["candidate"]["W_C_tr"][e] for e in graph.live_edge_ids)
        pairings = reference_pairings(
            graph, vertex_measure=(1,) * len(graph.live_node_ids),
            reference_edge_weights=weights,
        )
        resource = VertexScalar(graph, tuple(resources[n] for n in graph.live_node_ids))
        return graph, resource, pairings, weights, params["candidate"]["Lambda_C"]

    def assert_exact_boundary(self, target):
        graph, resource, pairings, weights, cutoff = self.inputs(target)
        self.assertEqual(cutoff, 1)
        # Independent exact witness: these two leaves share their parent both
        # before expansion and after column-preserving reassignment to s_1.
        witness = {n: Fraction(0) for n in graph.live_node_ids}
        witness.update({"outside-1": Fraction(1), "outside-4": Fraction(-1)})
        stiffness_action = dict.fromkeys(graph.live_node_ids, Fraction(0))
        for edge, weight in zip(graph.oriented_edges, weights, strict=True):
            flux = Fraction(weight) * (witness[edge.tail_node_id] - witness[edge.head_node_id])
            stiffness_action[edge.tail_node_id] += flux
            stiffness_action[edge.head_node_id] -= flux
        self.assertEqual(stiffness_action, witness)  # L v = 1 v, v != 0.
        with self.assertRaisesRegex(CandidateCStageError, "cutoff lies on the exact spectrum"):
            CandidateCSelector(resource, pairings, cutoff)

    def test_frozen_source_reference_is_on_selector_boundary(self):
        self.assert_exact_boundary(target=False)

    def test_frozen_d30_target_reference_is_on_selector_boundary(self):
        self.assert_exact_boundary(target=True)

    def test_nearby_selector_control_is_not_a_profile_admission(self):
        _, resource, pairings, _, _ = self.inputs()
        selector = CandidateCSelector(resource, pairings, 0.5)
        self.assertEqual(selector.rank, 1)
        for value in selector.selected.values:
            self.assertAlmostEqual(value, 0.3, places=12)
        # Zero resource is legal authoritative data; the spectral rejection
        # above must not be 'fixed' by inventing positive core resources.
        state = GRCV4AuthoritativeState(resource.values, None, None)
        self.assertIn(0, state.C)


if __name__ == "__main__":
    unittest.main()
