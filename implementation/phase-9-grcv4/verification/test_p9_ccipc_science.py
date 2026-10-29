"""Scientific regressions for exact charge, signed CI+PC reads and finite epochs."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import unittest
from unittest.mock import patch

import p9_ccipc_review as p


class CompositeScienceTests(unittest.TestCase):
    def test_deep_distribution_preserves_actual_represented_charges(self):
        manifest=p.deep.read(p.deep.INPUTS)
        source=manifest['expected_source']['inputs']
        for case in manifest['cases']:
            shares=case['request']['resource_distribution']
            if case['request']['target_effective_degree']!=94:continue
            self.assertEqual(sum(map(Fraction,shares)),1)
            self.assertEqual(sorted(shares),sorted([1087/4096,1537/4096,1472/4096]))
            for role in p.large.ROLES:
                c=Fraction(source[role]['C'][0])
                self.assertEqual(sum((Fraction(float(c*Fraction(x))) for x in shares),Fraction()),c)

    def test_original_exclusion_and_both_companions_remain_separate(self):
        g=p.large.g;original=p.deep.read(g.RESULTS)
        self.assertFalse(original['ready_for_native']);self.assertEqual(original['native_steps'],0)
        for row in original['cases']:
            if row['graph']=='target':
                self.assertFalse(row['first_step_nonnegative'])
                self.assertTrue(row['negative_resources'])
                self.assertTrue(all(g.q(x['upper'])<0 for x in row['negative_resources']))
        first=p.deep.read(p.charge.ORIGINAL_INPUTS);selected=p.deep.read(p.charge.INPUTS)
        self.assertEqual(first['selection']['shares'],['1/4','3/8','3/8'])
        self.assertEqual(selected['selection']['shares'],['5/16','5/16','3/8'])
        self.assertEqual(selected['original_evolved_split_charge_delta'],
            dict(current='-1/9007199254740992',reset='0'))
        values=list(map(g.q,selected['actual_source_split_operands']))
        self.assertEqual(selected['selection'],p.charge.select(first['constraints'],values))
        self.assertEqual(selected['adjusted']['source'],first['adjusted']['source'])
        self.assertFalse(selected['original_prepared_target_reused'])
        self.assertFalse(selected['changed_tolerances']);self.assertFalse(selected['changed_step_size'])
        for value in values:
            self.assertEqual(sum((g.q(float(value*g.q(w))) for w in selected['selection']['shares']),g.q(0)),value)

    def test_whole_chart_rejects_invalid_joint_hypotheses(self):
        source=p.deep.read(p.charge.INPUTS)['adjusted']['source']
        with p.compute.worker():
            _,_,bounds=p.large.g.whole_chart(source)
            self.assertGreater(p.large.q(bounds['source_slack']),0)
            for kind in ('gap','radius','tau','transport'):
                subject=deepcopy(source);params=subject['profile']['params_resolved']
                if kind=='gap':params['candidate']['Lambda_C']=1
                elif kind=='radius':params['realization']['radius']=0
                elif kind=='tau':params['realization']['tau_PC']=0
                else:params['candidate']['W_C_tr'][next(iter(params['candidate']['W_C_tr']))]=2
                with self.subTest(kind=kind),self.assertRaises(ValueError):p.large.g.whole_chart(subject)

    def test_complete_step_one_write_and_cache_mutations(self):
        value=p.deep.read(p.charge.filename('source'))['execution']
        with p.compute.worker():
            p.large.check_step(value)
            for kind in ('writes','reset','cache'):
                corrupted=deepcopy(value)
                if kind=='writes':corrupted['carrier_writes']=2
                elif kind=='reset':corrupted['after']['reset']['C'][0]+=1
                else:corrupted['cache_observations']['solve_hits']=0
                with self.subTest(kind=kind),self.assertRaises(ValueError):p.large.check_step(corrupted)

    def test_finite_execution_epoch_rejects_arbitrary_drift(self):
        manifest=p.deep.read(p.charge.ORIGINAL_NATIVE)
        with p.epoch.numerical_campaign():
            p.b.check_bindings(manifest['source_bindings'])
            corrupt=deepcopy(manifest['source_bindings']);corrupt[0]['sha256']='0'*64
            with self.assertRaises(ValueError):p.b.check_bindings(corrupt)
        read=Path.read_bytes;target=p.b.ROOT/p.epoch.SOURCE
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'\n# drift' if path==target else read(path)):
            with self.assertRaises(ValueError):p.epoch.checked()

    def test_retained_pointwise_pilot_has_physical_error_bounds(self):
        with p.epoch.numerical_campaign():
            pilot=p.deep.read(p.pointwise.PILOT)
            p.b.check_digest(pilot);p.b.check_bindings(pilot['source_bindings'])
        result=pilot['result'];q=p.large.q
        self.assertLess(q(result['resource_error']),q(2**-40))
        self.assertLess(q(result['carrier_error']),q(2**-48))
        self.assertGreater(q(result['exact_one_step_resource_lower']),0)
        self.assertFalse(result['uniform_trajectory_enclosure'])


class CompositeSignedConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with p.compute.worker():
            cls.manifest=p.deep.read(p.large.r.INPUTS)
            cls.before=p.b.GeometryStageInputs.from_payload(cls.manifest['initial_inputs'])
            cls.read=p.large.math_check.capture_read(p.large.r.CandidateCIRoot(cls.before))

    def test_resealed_sign_flip_reaches_independent_equation_check(self):
        value=deepcopy(self.read)
        value['flat']=[-x for x in value['flat']]
        # The quadratic source is invariant under this global sign flip.
        # Repair both hashes, so rejection must use signed equations.
        certificate=value.pop('certificate');value=p.b.seal(value)
        certificate['read_digest']=value['record_digest'];value['certificate']=certificate
        with p.compute.worker(),self.assertRaisesRegex(ValueError,'signed formula error'):
            p.large.check_read(self.before,value,numerics=True)

    def test_reference_currents_bind_both_actual_source_roots(self):
        with p.compute.worker():
            seed=p.large.r.state(self.manifest['expected_source']);case=self.manifest['cases'][0]
            execution=p.large.event(seed,case);event=execution['event']
            self.assertTrue(p.evidence.reference_lineage(seed,case,event)['exact_represented_charge'])
            for kind in ('source','target','graph','role'):
                corrupted=deepcopy(event);ref=corrupted['checkpoint']['reference_currents'][0]
                if kind=='graph':ref['source_graph_digest']='grc-graph-sha256:'+'0'*64
                elif kind=='role':ref['roles']['reset']=deepcopy(ref['roles']['current'])
                else:ref['roles']['current'][kind][0]+=1
                with self.subTest(kind=kind),self.assertRaises(ValueError):
                    p.evidence.reference_lineage(seed,case,corrupted)


if __name__=='__main__':unittest.main()
