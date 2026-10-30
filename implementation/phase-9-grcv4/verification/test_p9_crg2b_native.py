"""Pressure on the selected connected completion and independent consumers."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import numpy as np
import p9_crg2b_runtime as r
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection,RG2bStageError
from pygrc.models.grc_9_v4_rg2b import EXTENSION as OLD
from tests.models.test_grc_9_v4_crg2b import configure as old_configure

class ConnectedNativeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before=r.configure(r.b.GeometryStageInputs.from_payload(r.b.read(r.r.INPUTS)['initial_inputs']))
 def test_native_full_step_independent_edge_equations(self):
  with r.worker():
   value,after=r.perform_step(self.before)
   self.assertNotEqual(after.current.C,after.reset.C)
   self.assertGreater(r.Q(value['independent_bridge']['exact_real_next_resource_lower']),0)
   r.check_step(self.before,value,numerics=True)
 def test_old_policy_unchanged_and_distinct(self):
  with r.worker():
   old=old_configure(self.before)
   self.assertEqual(old.geometry.reference.profile.params_resolved.realization.extension_evaluator_id,OLD)
   a,b=CandidateRG2bSection(old),CandidateRG2bSection(self.before)
   self.assertNotEqual(a.identity,b.identity)
   self.assertLess(np.max(abs(np.array(a.geometry.one_form_hodge.matrix)-np.array(b.geometry.one_form_hodge.matrix))),2**-48)
 def test_chain_rejects_wrong_query_terminal_and_geometry(self):
  with r.worker():
   sec=CandidateRG2bSection(self.before);cert=sec.certificate
   xs,hs=r.native_completion.propose(cert,self.before.current.C)
   for mutation in ('query','terminal','asymmetry','radius'):
    xx=[a.copy() for a in xs];hh=[a.copy() for a in hs]
    if mutation=='query':xx[0][0]+=1
    if mutation=='terminal':hh[-1][0,0]+=2**-20
    if mutation=='asymmetry':hh[0][0,1]+=2**-20
    if mutation=='radius':hh[0][0,0]+=1
    with self.subTest(mutation=mutation),self.assertRaises(RG2bStageError):
     r.native_completion.certify_chain(cert,self.before.current.C,xx,hh)
 def test_stale_full_geometry_rejected_even_with_same_current(self):
  with r.worker():value=r.native_read(self.before)
  bad=deepcopy(value);bad['H'][0][0]+=2**-20
  bad=r.b.seal({k:v for k,v in bad.items() if k!='independent_certificate'})
  bad['independent_certificate']=value['independent_certificate']
  with self.assertRaises(ValueError):r.check_read(self.before,bad)
 def test_no_fallback_on_unproved_numerics(self):
  with r.worker(),patch.object(r.native_completion,'proposal',side_effect=ArithmeticError('forced numerical failure')):
   with self.assertRaises(RG2bStageError):CandidateRG2bSection(self.before)
 def test_connected_graph_and_selector_limits_fail_explicitly(self):
  graph=self.before.geometry.reference.graph.port_graph.to_payload()
  bad=deepcopy(graph);bad['live_node_ids'].append('isolated')
  with self.assertRaises(RG2bStageError):r.native_completion.graph_algebra(bad)
  # Long connected paths fail the sufficient constant-selector certificate.
  graph=dict(schema_version='grc9v4-port-graph-v1',live_node_ids=list(range(60)),edges=[
   dict(edge_id=str(i),kind='tree',tail=dict(node_id=i,port=1),head=dict(node_id=i+1,port=2)) for i in range(59)])
  with self.assertRaises(RG2bStageError):r.native_completion._graph_constants(r.b.canonical_json_bytes(graph))

if __name__=='__main__':unittest.main()
