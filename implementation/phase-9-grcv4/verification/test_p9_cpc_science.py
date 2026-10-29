"""Independent C_PC numerical, cache-policy, history and provenance pressure."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import p9_cpc_review as p
import p9_cpc_compute as compute


class CPCScienceTests(unittest.TestCase):
    def test_compute_policy_is_required_and_scoped(self):
        from pygrc.models import grc_v4_codec as codec
        before=(codec._VALIDATION_LIMIT,codec._VALIDATION_MAX_BYTES)
        with compute.worker() as result:
            self.assertEqual(result['exact_backend'],'flint')
            self.assertFalse(result['tolerances_relaxed'])
            self.assertEqual(compute.verify_active(),result)
            with patch.dict(compute.os.environ,OPENBLAS_NUM_THREADS='2'):
                with self.assertRaisesRegex(ValueError,'single-thread'):compute.verify_active()
        self.assertEqual((codec._VALIDATION_LIMIT,codec._VALIDATION_MAX_BYTES),before)
        with self.assertRaises(ValueError):compute.verify_active()

    def test_deep_allocation_preserves_exact_represented_charge(self):
        m=p.deep.read(p.deep.INPUTS);p.b.check_digest(m)
        source=m['expected_source']['inputs']
        c=Fraction(source['current']['C'][0])
        old=[Fraction(x,64) for x in (17,24,23)]
        self.assertEqual(sum((Fraction(float(c*x)) for x in old),Fraction())-c,-Fraction(1,2**52))
        cases=[x for x in m['cases'] if 'D94' in x['fixture_id']]
        self.assertEqual(len(cases),6)
        for case in cases:
            shares=case['request']['resource_distribution']
            self.assertEqual(sum(map(Fraction,shares)),1)
            self.assertEqual(sorted(shares),sorted([1087/4096,1537/4096,1472/4096]))
            for role in p.large.ROLES:
                c=Fraction(source[role]['C'][0])
                self.assertEqual(sum((Fraction(float(c*Fraction(x))) for x in shares),Fraction()),c)

    def test_original_exclusion_and_separate_companion_have_no_native_credit(self):
        g=p.large.g;m=p.deep.read(g.INPUTS);v=p.deep.read(g.RESULTS)
        p.b.check_digest(m);p.b.check_digest(v)
        self.assertFalse(v['ready_for_native']);self.assertEqual(v['native_steps'],0)
        targets=[r for r in v['cases'] if r['graph']=='target']
        self.assertEqual({r['role'] for r in targets},{'current','reset'})
        for row in targets:
            self.assertFalse(row['first_step_nonnegative'])
            self.assertTrue(all(g.q(x['upper'])<0 for x in row['negative_resources']))
        cm=p.deep.read(p.large.companion.INPUTS);cv=p.deep.read(p.large.companion.RESULTS)
        self.assertTrue(cv['ready_for_native']);self.assertEqual(cv['native_steps'],0)
        self.assertEqual(cm['companion']['source_deficit'],'1/1024')
        self.assertFalse(cm['changed_tolerances']);self.assertFalse(cm['changed_step_size'])

    def test_whole_chart_rejects_invalid_hypotheses(self):
        subject=p.deep.read(p.large.companion.INPUTS)['adjusted']['source']
        with compute.worker():
            self.assertGreater(p.large.q(p.large.g.whole_chart(subject)['source_slack']),0)
            for kind in ('gap','radius','tau','transport'):
                s=deepcopy(subject);params=s['profile']['params_resolved']
                if kind=='gap':params['candidate']['Lambda_C']=1
                elif kind=='radius':params['realization']['radius']=0
                elif kind=='tau':params['realization']['tau_PC']=0
                else:params['candidate']['W_C_tr'][next(iter(params['candidate']['W_C_tr']))]=2
                with self.subTest(kind=kind),self.assertRaises(ValueError):p.large.g.whole_chart(s)

    def test_complete_step_and_one_write_mutations(self):
        value=p.large.read('source')['execution']
        with p.wire_reuse(),compute.worker():
            p.large.check_step(value)
            errors=p.step_error_bounds(value)
            self.assertFalse(errors['uniform_trajectory_enclosure'])
            for kind in ('writes','reset','cache'):
                v=deepcopy(value)
                if kind=='writes':v['carrier_writes']=2
                elif kind=='reset':v['after']['reset']['C'][0]+=1
                else:v['cache_observations']['solve_hits']=0
                with self.subTest(kind=kind),self.assertRaises(ValueError):p.large.check_step(v)

    def test_signed_flat_error_cannot_hide_behind_resealed_certificate(self):
        value=p.large.read('source')['execution']
        read=deepcopy(value['read']);read['flat']=[-x for x in read['flat']]
        # Also repair the staged source, which is quadratic in flat and hence
        # unchanged by a global sign flip. Magnitudes alone cannot catch this.
        cert=read.pop('certificate');read=p.b.seal(read);cert['read_digest']=read['record_digest'];read['certificate']=cert
        with p.wire_reuse(),compute.worker(),self.assertRaisesRegex(ValueError,'formula error|equation drift'):
            before=p.b.GeometryStageInputs.from_payload(value['before'])
            p.large.check_read(before,read,numerics=True)

    def test_finite_verifier_epoch_rejects_arbitrary_drift(self):
        m=p.deep.read(p.large.INPUTS);p.repairs.check_bindings(m['source_bindings'])
        value=deepcopy(m['source_bindings']);value[0]['sha256']='0'*64
        with self.assertRaises(ValueError):p.repairs.check_bindings(value)
        read=Path.read_bytes;target=p.b.ROOT/p.repairs.SELF
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'\n# altered' if path==target else read(path)):
            with self.assertRaises(ValueError):p.repairs.check_bindings(m['source_bindings'])

    def test_large_consumer_checks_complete_history_schema_on_native_small_event(self):
        # The same large consumer can be exercised cheaply on the accepted
        # small unit-reference chart, with its own independent Arb equations.
        with p.wire_reuse(),compute.worker():
            m=p.deep.read(p.large.r.INPUTS);seed=p.large.r.state(m['expected_source']);case=m['cases'][0]
            execution=p.large.event(seed,case);event=execution['event']
            self.assertEqual(event['receipts'][0]['identity_payload']['history']['schema_version'],
                             'grcv4-history-bundle-receipt-v1')
            bad=deepcopy(event);bad['receipts'][0]['identity_payload']['history'].pop('schema_version')
            with self.assertRaises(ValueError):p.large.check_event(seed,case,bad)


if __name__=='__main__':unittest.main()
