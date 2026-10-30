"""Exact comparison-system and marginal-sign certificate pressure."""
import unittest
from copy import deepcopy
from dataclasses import replace
from flint import fmpq as Q
import p9_arg2b_positive as p
import p9_arg2b_allocation as a

class PositiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  c,r=a.c,a.r;m=c.read(a.RESULT);seed=r.state(m['source']);target=r.independent_target(dict(expected_source=seed.to_payload()),m['cases'][0])
  cls.before=replace(target,dt=c.b.DT)
  with r.worker():cls.read=r.native_read(cls.before)
 def test_comparison_system_dominates_every_level(self):
  certificate=self.read['independent_certificate']['section'];ex,eh,w=p.bounds(certificate);g,_=p.p.global_bounds()
  self.assertTrue(all(v>0 for v in w))
  for i,row in enumerate(certificate['levels']):
   parent=Q(certificate['input_coordinate_error']) if i==0 else ex[i-1]
   child=eh[i+1] if i<3 else p.p.RHO
   self.assertGreaterEqual(ex[i],parent+g['A_X']*ex[i]+g['A_H']*child+Q(row['state_residual']))
   self.assertGreaterEqual(eh[i],(g['B_X']*ex[i]+g['B_H']*child)/2+Q(row['geometry_residual']))
 def test_frontier_sign_resolved_without_global_claim(self):
  b=self.before;read=self.read;sc=read['independent_certificate']['section']
  self.assertLess(Q(sc['exact_real_next_resource_lower']),0)
  v=p.certify(b.geometry.reference.graph.port_graph.to_payload(),b.current.C,b.current.W_A,read['chain']['work'],sc)
  self.assertTrue(v['strictly_positive']);self.assertGreater(Q(v['exact_real_next_resource_lower']),0)
  self.assertLess(float(Q(v['exact_real_next_resource_lower'])),1e-20)
 def test_residual_forgery_rejected(self):
  b=self.before;read=self.read;sc=deepcopy(read['independent_certificate']['section']);sc['levels'][0]['state_residual']='0'
  with self.assertRaises(ValueError):p.certify(b.geometry.reference.graph.port_graph.to_payload(),b.current.C,b.current.W_A,read['chain']['work'],sc)
 def test_terminal_uncertainty_is_not_discarded(self):
  sc=deepcopy(self.read['independent_certificate']['section'])
  sc['input_coordinate_error']='0'
  for row in sc['levels']:row.update(state_residual='0',geometry_residual='0')
  ex,eh,_=p.bounds(sc);self.assertTrue(all(v>0 for v in ex+eh))

if __name__=='__main__':unittest.main()
