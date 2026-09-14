"""Bounded dispatch/cleanup pressure; synthetic outputs are not scientific evidence."""

import ast
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import profile_g2_registry as g


class MaterializerTests(unittest.TestCase):
    def test_pinned_topology_rejects_missing_duplicate_wrong_or_forward_dependencies(self):
        original=g.registry(p.ROOT)
        edits=[lambda v:v['materializers'].pop(),
               lambda v:v['materializers'].append(deepcopy(v['materializers'][0])),
               lambda v:v['materializers'].reverse(),
               lambda v:v['materializers'][0].update(module='os.system'),
               lambda v:v['materializers'][1].update(dependency='profile_conformance_review'),
               lambda v:v['materializers'][-1].update(dependency='a_os_crossings'),
               lambda v:v['materializers'][0].update(kind='g2')]
        for edit in edits:
            value=deepcopy(original);edit(value)
            with self.subTest(edit=edit),self.assertRaises((ValueError,KeyError)):g.validate_materializers(value)

    def test_ordered_materialization_calls_each_scientific_checker_once_and_publishes_no_partial_result(self):
        roster=g.registry(p.ROOT);seed={'record_digest':'synthetic_dispatch_seed'}
        calls=[];built={'profile_conformance_review':seed}
        by_module={r['module']:r for r in roster['materializers']}
        def load(root,name):
            self.assertEqual(root,p.ROOT)
            row=by_module[name]
            def check(**kwargs):
                argument={'local':'initial_review','crossing':'local_product','g2':'bounded_acceptance'}[row['kind']]
                self.assertEqual(kwargs,{argument:built[row['dependency']]})
                calls.append(name)
                result={'test_only_producer':name}
                built[row['view_key']]=result
                return result
            return check
        def bounded(root,views):
            self.assertEqual(set(views),set(roster['reconciliation_views']))
            self.assertEqual(views,{k:built[k] for k in roster['reconciliation_views']})
        normalized={'profiles':['synthetic_gate_view'],'accepted_generic_runtime_support':['synthetic_support']}
        with patch.object(g,'checked',return_value=normalized),patch.object(g,'_checker',side_effect=load), \
             patch.object(g,'project_review',side_effect=lambda root,row,result,support:result), \
             patch.object(g,'checked_reconciliation',side_effect=bounded):
            views,support=g.materialize(p.ROOT,seed)
            self.assertEqual(calls,[r['module'] for r in roster['materializers']])
            self.assertEqual(set(views),{r['view_key'] for r in roster['materializers']}|{'profile_g2'})
            self.assertEqual(support,normalized['accepted_generic_runtime_support'])
            published={}
            def broken(root,name):
                if name==roster['materializers'][2]['module']:raise ValueError('synthetic checker failure')
                return load(root,name)
            with patch.object(g,'_checker',side_effect=broken),self.assertRaisesRegex(ValueError,'synthetic checker failure'):
                published.update(g.materialize(p.ROOT,seed)[0])
            self.assertEqual(published,{})

    def test_current_source_and_import_origin_are_required(self):
        name=g.registry(p.ROOT)['materializers'][0]['module']
        with patch.object(p,'read',return_value={'artifact_bindings':[]}):
            with self.assertRaisesRegex(ValueError,'unbound'):g._checker(p.ROOT,name)
        with patch('importlib.import_module',return_value=SimpleNamespace(__file__='wrong-checker.py',check=lambda:None)):
            with self.assertRaisesRegex(ValueError,'outside pinned source'):g._checker(p.ROOT,name)

    def test_actual_entrypoint_cleanup_loop_removes_every_produced_key(self):
        # Execute the real except-block loop with a synthetic late-failure
        # payload; do not repeat the full status/scientific predecessor chain.
        source=(p.ROOT/p.SIDE/'tool/src/grcv4_explorer/phase9_verification.py').read_text()
        tree=ast.parse(source)
        loops=[n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.iter,ast.Name)
               and n.iter.id=='profile_view_keys']
        self.assertEqual(len(loops),1)
        keys={r['view_key'] for r in g.registry(p.ROOT)['materializers']}|{'profile_g2'}
        payload={key:{'synthetic':'partial result'} for key in keys};payload['unrelated']='keep'
        namespace={'profile_view_keys':keys,'payload':payload}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[loops[0]],type_ignores=[])),
                     'phase9_verification.py:cleanup','exec'),namespace)
        self.assertEqual(payload,{'unrelated':'keep'})
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any(n and n.startswith(('verify_p977_a_os_','verify_p977_a_ci_','verify_p977_c_ci_')) for n in imports))


if __name__=='__main__':
    unittest.main()
