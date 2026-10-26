"""Closed differential reconstruction: preserve WLS and reject foreign fixed rows."""
from dataclasses import replace
import unittest
from pygrc.models import grc_v4_lifecycle as owner
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
from tests.models.test_grc_v4_candidate_a import current_fixture


class FixedRowRegistryTests(unittest.TestCase):
    def test_wls_keeps_exact_reference_weights_and_graph_binding(self):
        before,backend=current_fixture();reference=before.geometry.reference
        self.assertIs(type(backend),CandidateADifferentialReference)
        restored=owner._backend_registry((backend,), (reference,))[0]
        self.assertEqual(restored,backend)
        weights=backend.reference_weights.to_dict();key=next(iter(weights));weights[key]*=2
        foreign=replace(backend,reference_weights=weights)
        self.assertFalse(owner._differential_matches(foreign,reference))
        with self.assertRaises(ValueError):owner._backend_registry((foreign,), (reference,))

    def test_fixed_rows_are_closed_and_never_wls_or_arbitrary_callbacks(self):
        from tests.models.test_grc_9_v4_aci import fixture,RECORD
        import json
        state,_=fixture(json.loads(RECORD.read_text()))
        backend=state.differential_reference;ref=state.inputs.geometry.reference
        rows=owner._backend_registry((backend,), (ref,))
        self.assertIs(type(rows[0]),GRC9V4CandidateADifferentialReference)
        self.assertEqual(owner._backend_for(ref,rows).to_payload(),backend.to_payload())
        for key,value in (('read_weights','reference_weights'),('curvature_backend','wls'),('extra',True)):
            bad=backend.to_payload();bad[key]=value
            with self.subTest(key=key),self.assertRaises((ValueError,TypeError)):
                owner._backend_registry((bad,), (ref,))
        with self.assertRaises((ValueError,TypeError)):owner._backend_registry((object(),), (ref,))
        with self.assertRaises(ValueError):owner._backend_registry((backend,backend), (ref,))
        graph=backend.port_graph
        foreign=replace(backend,port_graph=replace(graph,live_node_ids=graph.live_node_ids+('isolated',)))
        self.assertFalse(owner._differential_matches(foreign,ref))
        with self.assertRaises(ValueError):owner._backend_registry((foreign,), (ref,))


if __name__=='__main__':unittest.main()
