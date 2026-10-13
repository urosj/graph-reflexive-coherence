"""Declared-graph stencil extension, reuse and full A_PC coverage pressure."""
from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch
import numpy as np

import p984d_apc_full as g
from test_p984d_apc_feasibility import literal,overlap


class FullAPCTests(unittest.TestCase):
    def test_generic_context_matches_D94_and_literal_equations(self):
        old=g.b.read(g.prior.INPUTS);runtime=old['runtime_manifest'];seed=g.r.state(runtime['expected_source'])
        case=runtime['cases'][0]
        for role in g.r.ROLES:
            a=g.context(runtime,case,role);z=g.f.context(runtime,role=role)
            for key in ('B','w','L','M','initial','first','second'):
                self.assertTrue(np.array_equal(a[key],z[key]))
        for degree in (59,66,73,94):
            template=next(c for c in g.b.read(g.h.c.prior.INPUTS)['cases'] if c['request']['target_effective_degree']==degree)
            case=g.template(seed,template)
            for role in g.r.ROLES:
                ctx=g.context(runtime,case,role)
                for x,y in ((Q(47,128),Q(47,128)),(Q(0),Q(0)),(Q(1),Q(0))):
                    first,second=literal(ctx,x,y);enc=g.f.enclose(ctx,(x,x,y,y))
                    for key,truth,error in (('first',first,enc['first_error']),('second',second,enc['second_error'])):
                        if truth is None:continue
                        bound=g.f.affine(ctx[key],g.f.number(x),g.f.number(y))+error
                        self.assertTrue(all(overlap(a,z) for a,z in zip(truth,bound)))
        bad=deepcopy(case);bad['request']['target_effective_degree']=100
        with self.assertRaises(ValueError):g.context(runtime,bad,'current')

    def test_selections_reuse_and_scope_reject_mutations(self):
        m=g.b.read(g.INPUTS);g.check_manifest(m)
        for mutate in (lambda v:v['selections'].pop(),lambda v:v.update(new_source_steps=1),
                lambda v:v.update(uniform_native_domain=True),
                lambda v:v['selections'][0]['derivation']['selection'].update(shares=['1/3']*3),
                lambda v:v['runtime_manifest']['cases'][0]['request'].update(operation_id='changed')):
            bad=deepcopy(m);mutate(bad)
            with self.assertRaises(ValueError):g.check_manifest(g.b.seal(bad))

    def test_retained_complete_roster_without_native_rerun(self):
        m,v=g.b.read(g.INPUTS),g.b.read(g.RESULTS)
        predecessor=g.predecessor()
        with (patch.object(g,'predecessor',return_value=predecessor),
                patch.object(g.r,'perform_step',side_effect=AssertionError('native step')),
                patch.object(g.r,'event_capture',side_effect=AssertionError('native event')),
                patch.object(g.r,'validate',side_effect=AssertionError('status must not repeat full consumer audit'))):
            summary=g.status(m,v)
        self.assertEqual(summary['attempted_cases'],20)
        self.assertEqual(summary['reused_cases'],1)
        self.assertEqual(summary['accepted_cells'],0)
        self.assertEqual(summary['passed_cases'],20)
        self.assertEqual(summary['target_steps'],400)
        self.assertEqual(summary['final_reads'],40)
        self.assertEqual(summary['verification_level'],'authenticated_structure')
        bad=deepcopy(v);bad['reuse']['case_digest']='forged'
        with self.assertRaises(ValueError):g.materialize(m,bad)
        exe=g.h.prior.previous.expand(v['execution']);exe['cases'][0]['continuation'].pop()
        bad=deepcopy(v);bad['execution']=g.h.prior.previous.compact(g.b.seal(exe))
        with self.assertRaisesRegex(ValueError,'incomplete success schedule'):g.status(m,g.b.seal(bad))
        exe=g.h.prior.previous.expand(v['execution']);exe['cases'].pop()
        bad=deepcopy(v);bad['execution']=g.h.prior.previous.compact(g.b.seal(exe))
        with self.assertRaises(ValueError):g.materialize(m,bad)


if __name__=='__main__':unittest.main()
