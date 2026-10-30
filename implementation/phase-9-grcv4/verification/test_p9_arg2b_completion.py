from copy import deepcopy
from fractions import Fraction
import unittest
from unittest.mock import patch
from flint import fmpq as Q
import p9_arg2b_completion as a
import test_p980_rg2b_completion as old

class ConnectedAProof(unittest.TestCase):
 def test_old_bounds_exactly_reproduced(self):
  got,checks=a.global_bounds(Q(9),Q(10),Q(5));expected=old.global_bounds('A');expected.update(old.section_budgets(expected))
  for key,value in expected.items():self.assertEqual(got[key],Q(value.numerator,value.denominator),key)
  self.assertTrue(all(checks.values()))
 def test_full_nine_port_bounds_and_budget(self):
  v,checks=a.global_bounds();self.assertTrue(all(checks.values()))
  self.assertGreater(v['M_C'],Q(23,100));self.assertLess(v['M_C'],Q(1,4))
  self.assertLess(v['four_level_tail_upper'],Q(1,2**48))
  with patch.object(old,'DEGREE',Fraction(9)),patch.object(old,'EDGE_GRAM',Fraction(18)),patch.object(old,'MASK_NORM',Fraction(9)):
   expected=old.global_bounds('A');expected.update(old.section_budgets(expected))
  for key,value in expected.items():self.assertEqual(v[key],Q(value.numerator,value.denominator),key)
 def test_cyclic_graphs_and_orientation(self):
  large=a.read(a.INPUTS[2]);g=large['source']['graph'];v=a.graph_certificate(g)
  self.assertEqual(v['cycle_rank'],301);self.assertEqual(v['actual_norms'],['9','17','17/2'])
  changed=deepcopy(g)
  for e in changed['edges']:e['tail'],e['head']=e['head'],e['tail']
  fresh=a.graph_certificate(changed)
  self.assertEqual(v['actual_norms'],fresh['actual_norms']);self.assertEqual(v['class_certificate_digest'],fresh['class_certificate_digest'])
  nodes=[str(i) for i in range(10)];ports={n:{v:k+1 for k,v in enumerate(x for x in nodes if x!=n)} for n in nodes}
  full=dict(live_node_ids=nodes,edges=[dict(edge_id=f'{u}-{v}',tail=dict(node_id=u,port=ports[u][v]),head=dict(node_id=v,port=ports[v][u])) for i,u in enumerate(nodes) for v in nodes[i+1:]])
  self.assertEqual(a.graph_certificate(full)['actual_norms'],['9','18','9'])
 def test_collision_self_loop_duplicate_and_disconnection(self):
  g=a.read(a.INPUTS[0])['cases'][0]['oracle']['target_graph']
  for kind in ('collision','loop','duplicate','disconnected'):
   bad=deepcopy(g)
   if kind=='collision':bad['edges'][1]['tail']=deepcopy(bad['edges'][0]['tail'])
   elif kind=='loop':bad['edges'][0]['head']=deepcopy(bad['edges'][0]['tail'])
   elif kind=='duplicate':bad['edges'][1]['edge_id']=bad['edges'][0]['edge_id']
   else:bad['live_node_ids'].append('isolated')
   with self.subTest(kind=kind),self.assertRaises(ValueError):a.graph_certificate(bad)
 def test_out_of_class_norms_and_parameter_drift_reject(self):
  for norms in ((10,18,9),(9,19,9),(9,18,10),(0,1,1)):
   with self.subTest(norms=norms),self.assertRaises(ValueError):a.global_bounds(*map(Q,norms))
  large=a.read(a.INPUTS[2]);a.validate_large_recipe(large)
  for key in ('gamma','chi_A','alpha','W_floor'):
   bad=deepcopy(large);bad['target']['profile']['params_resolved']['candidate'][key]*=2
   with self.subTest(key=key),self.assertRaises(ValueError):a.validate_large_recipe(bad)
 def test_all_declared_subjects_no_native_credit(self):
  subjects=a.subjects();self.assertEqual(len(subjects),54)
  self.assertTrue(all(all(a.graph_certificate(g)['checks'].values()) for _,g in subjects))
  self.assertEqual(a.scope()['native_steps'],0);self.assertFalse(a.scope()['physical_positivity_certified'])

if __name__=='__main__':unittest.main()
