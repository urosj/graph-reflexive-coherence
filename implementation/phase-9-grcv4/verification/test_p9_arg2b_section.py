from copy import deepcopy
import math
import unittest
import numpy as np
from flint import arb,ctx,fmpq as Q
import p9_arg2b_completion as p
import p9_arg2b_section as s
from test_p9_crg2b_completion import graph
import test_p980_rg2b_completion as prior
from test_p980_os_effect_witness import IV,PARAMS,IntervalRows,number,endpoint,vector

class ASectionPressure(unittest.TestCase):
 def setUp(self):
  self.graph=graph(4,[(0,1),(1,2),(2,3),(3,0),(0,2)])
  self.data=s.algebra(self.graph);self.cert=p.graph_certificate(self.graph)
  self.c=[3.,1.,2.,0.];self.w=[1023/1024+(i-2)*2**-24 for i in range(5)]
  self.query=self.c+[512*math.log(v) for v in self.w]
  self.x,self.h=s.proposal(self.data,self.query)
 def test_chain_full_history_and_sparse_round_trip(self):
  result=s.certify(self.graph,self.c,self.w,self.x,self.h,self.cert)
  self.assertTrue(result['section_tolerance_passes']);self.assertTrue(result['next_history_inside_K_minus'])
  self.assertGreater(Q(result['input_coordinate_error']),0)
  x,h=s.decode(s.encode(self.x,self.h))
  for a,b in zip(self.x+self.h,x+h,strict=True):np.testing.assert_array_equal(a,b)
 def test_independent_signed_equations_and_writer_stage(self):
  model=prior.AuxiliaryRows(prior.physical.StagedRows(self.graph['live_node_ids'],self.graph['edges'],PARAMS))
  x=list(self.query);x[0]=-.5
  h=np.eye(5);h[0,1]=h[1,0]=2**-15;h[0,0]+=2**-14
  expected_f,expected_s=prior.literal_signed_increment(model,'A',vector(x),IV.matrix(h.tolist()))
  with ctx.workprec(s.BITS):
   got=s.literal(self.data,x,s.matrix(h));actual_s=got['source'];f=got['increment']
   for a,z in zip(f.entries(),expected_f):
    lo,hi=endpoint(z,0),endpoint(z,1)
    self.assertLessEqual(s.lower(a),Q(hi.numerator,hi.denominator));self.assertGreaterEqual(s.upper(a),Q(lo.numerator,lo.denominator))
   for i in range(5):
    for j in range(5):
     lo,hi=endpoint(expected_s[i,j],0),endpoint(expected_s[i,j],1)
     self.assertLessEqual(s.lower(actual_s[i,j]),Q(hi.numerator,hi.denominator));self.assertGreaterEqual(s.upper(actual_s[i,j]),Q(lo.numerator,lo.denominator))
   c=vector(x[:4]);w=IV.matrix([IV.exp(number(v)/512) for v in x[4:]])
   read=model.read('A',c,w,IV.matrix(h.tolist()))
   wrong=model.conductance(c,w,read['J'])
   wrong_dy=[(1-IV.exp(-number(p.DT)))*(512*IV.ln(g)-number(y)) for g,y in zip(wrong,x[4:])]
   self.assertTrue(any(abs(float(f[4+i,0])-float(z.mid))>1e-12 for i,z in enumerate(wrong_dy)))
 def test_clipping_faces_and_inactive_floor(self):
  x=list(self.query);x[0]=-2.;x[-1]=1.5
  projected=[min(5.,max(-1.,v)) for v in x[:4]]+[min(1.,max(-1.,v)) for v in x[4:]]
  with ctx.workprec(s.BITS):
   a=s.literal(self.data,x,s.matrix(self.h[1]));b=s.literal(self.data,projected,s.matrix(self.h[1]),retract=False)
   for key in ('increment','image'):
    self.assertEqual([(s.lower(v),s.upper(v)) for v in a[key].entries()],[(s.lower(v),s.upper(v)) for v in b[key].entries()])
 def test_zero_containing_current_intervals_are_finite(self):
  with ctx.workprec(s.BITS):
   v=arb(0,Q(1,2**170));self.assertTrue(s.square(v).is_finite())
   x=[arb(2,Q(1,2**170)) for _ in range(4)]+[arb(0) for _ in range(5)]
   got=s.literal(self.data,x,s.eye(5),retract=False)
   self.assertTrue(all(v.is_finite() and v.contains(0) for v in got['J'].entries()))
   self.assertTrue(all(v.is_finite() for v in got['increment'].entries()))
 def test_full_root_and_intermediate_history_mutations_are_seen(self):
  for kind in ('history','geometry'):
   x=[v.copy() for v in self.x];h=[v.copy() for v in self.h]
   if kind=='history':x[2][-1]+=2**-14
   else:h[2][0,0]+=2**-20
   with self.subTest(kind=kind):self.assertFalse(s.certify(self.graph,self.c,self.w,x,h,self.cert)['section_tolerance_passes'])
 def test_query_terminal_support_and_finite_failures(self):
  for kind in ('query','terminal','asymmetric','nonfinite'):
   x=[v.copy() for v in self.x];h=[v.copy() for v in self.h]
   if kind=='query':x[0][-1]+=2**-20
   elif kind=='terminal':h[-1][0,0]+=2**-20
   elif kind=='asymmetric':h[1][0,1]+=2**-20
   else:x[2][0]=float('nan')
   with self.subTest(kind=kind),self.assertRaises(ValueError):s.certify(self.graph,self.c,self.w,x,h,self.cert)
 def test_wrong_certificate_history_roster_and_sparse_duplicates(self):
  bad=deepcopy(self.cert);bad['class_certificate_digest']='0'*64
  with self.assertRaises(ValueError):s.certify(self.graph,self.c,self.w,self.x,self.h,bad)
  with self.assertRaises(ValueError):s.certify(self.graph,self.c,self.w[:-1],self.x,self.h,self.cert)
  packed=s.encode(self.x,self.h);packed['h_upper_nonzero'][0].append(packed['h_upper_nonzero'][0][0])
  with self.assertRaises(ValueError):s.decode(packed)

if __name__=='__main__':unittest.main()
