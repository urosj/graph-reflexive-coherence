"""Pressure on connected A completion and full joint native observations."""
from copy import deepcopy
from dataclasses import replace
import math,unittest
from unittest.mock import patch
import numpy as np
import p9_arg2b_runtime as r
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection,RG2bStageError

class ConnectedANativeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=r.b.GeometryStageInputs.from_payload(r.b.read(r.r.INPUTS)['initial_inputs'])
  cls.before=r.configure(cls.old)
 def test_native_full_joint_step(self):
  with r.worker():
   value,after=r.perform_step(self.before);r.check_step(self.before,value,numerics=True)
  self.assertNotEqual(after.current.W_A,self.before.current.W_A)
  self.assertEqual(after.reset,self.before.reset)
  self.assertGreater(r.Q(value['independent_bridge']['exact_real_next_resource_lower']),0)
 def test_predecessor_policy_stays_distinct(self):
  with r.worker():
   old=CandidateRG2bSection(self.old,r.r.backend(self.old));new=CandidateRG2bSection(self.before,r.r.backend(self.before))
  self.assertNotEqual(old.identity,new.identity)
  self.assertLess(np.max(abs(np.asarray(old.geometry.one_form_hodge.matrix)-new.geometry.one_form_hodge.matrix)),2**-48)
 def test_exact_global_bounds_match_independent_proof(self):
  self.assertEqual(r.native_completion.global_bounds(),r.proof.global_bounds())
 def test_joint_mutation_pressure(self):
  with r.worker():
   sec=CandidateRG2bSection(self.before,r.r.backend(self.before));cert=sec.certificate
   query=list(self.before.current.C)+[512*math.log(w) for w in self.before.current.W_A]
   xs,hs=r.native_completion.propose(cert,query);actual=r.native_completion.admit(self.before.current,ordinary=False)
   for mutation in ('query','terminal','asymmetry','radius','nan'):
    xx=[a.copy() for a in xs];hh=[a.copy() for a in hs]
    if mutation=='query':xx[0][-1]+=.1
    if mutation=='terminal':hh[-1][0,0]+=2**-20
    if mutation=='asymmetry':hh[0][0,1]+=2**-20
    if mutation=='radius':hh[0][0,0]+=1
    if mutation=='nan':xx[1][-1]=float('nan')
    with self.subTest(mutation=mutation),self.assertRaises(RG2bStageError):
     r.native_completion.certify_chain(cert,query,xx,hh,actual)
   xx=[a.copy() for a in xs];xx[1][-1]+=.1
   error,_=r.native_completion.certify_chain(cert,query,xx,hs,actual)
   self.assertGreater(error,r.Q(1,2**48))
 def test_no_fallback(self):
  with r.worker(),patch.object(r.native_completion,'proposal',side_effect=ArithmeticError('forced')):
   with self.assertRaises(RG2bStageError):CandidateRG2bSection(self.before,r.r.backend(self.before))
 def test_selected_geometry_cannot_be_replaced(self):
  with r.worker():value=r.native_read(self.before)
  bad=deepcopy(value);bad['H'][0][0]+=2**-20
  bad=r.b.seal({k:v for k,v in bad.items() if k!='independent_certificate'});bad['independent_certificate']=value['independent_certificate']
  with self.assertRaises(ValueError):r.check_read(self.before,bad)
 def test_graph_and_parameter_limits(self):
  graph=self.before.geometry.reference.graph.port_graph.to_payload();graph['live_node_ids'].append('isolated')
  with self.assertRaises(RG2bStageError):r.native_completion.graph_algebra(graph)
  from tests.models.test_grc_9_v4_arg2b import configure
  bad=configure(self.before,{'candidate':dict(gamma=2**-23)})
  with r.worker(),self.assertRaises(RG2bStageError):CandidateRG2bSection(bad,r.r.backend(bad))

if __name__=='__main__':unittest.main()
