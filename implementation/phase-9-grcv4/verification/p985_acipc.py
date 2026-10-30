"""A_CI_PC lifecycle pressure: six small obligations and fresh large native replay."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
import unittest
from unittest.mock import patch
import p984h_acipc as n
from tests.models import test_grc_9_v4_acipc as prior
from pygrc.models import grc_v4_lifecycle as generic
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_numerics import numerical_policy, NumericalPolicy
from p984h_validation_reuse import validation_reuse
import p9_acipc_compute as compute
import p9_acipc_integration_compute as integration_compute
from p9_cpc_covariance_compute import wire_reuse

b=n.b
SELF=b.HERE+'p985_acipc.py'
INPUTS=b.BASE+'P9-8.5-ACIPCInputs.json'
CASES=('request_boundaries','domain_and_history','atomicity','replay','readmission_no_writers','continuation_reset')
METHODS=dict(domain_and_history=(
    'test_target_whole_chart_rejection_both_roles_even_when_points_regular',
    'test_composite_domain_and_strict_source_slack_are_not_PC_shortcuts',
    'test_both_carrier_roles_are_bound_in_request_and_loss_is_separate'),
    atomicity=('test_charge_both_roles_and_late_receipt_failures_roll_back',),
    replay=('test_replay_rejects_history_reference_identity_and_receipt_tampering','test_complete_archives_and_rehashed_archive_replay_failures',),
    readmission_no_writers=('test_event_admission_runs_neither_W_nor_Z_writer',))
OBSERVATIONS={}


def path(segment):
    b.require(segment in ('small','large'),'lifecycle segment')
    return b.BASE+'P9-8.5-ACIPC-'+segment+'.json.xz'


class Lifecycle(prior.NativeACIPCPressure):
    def note(self,name,**values):OBSERVATIONS[name]=dict(passed=True,**values)
    def exercise(self,name):
        for method in METHODS[name]:getattr(prior.NativeACIPCPressure,method)(self)
        self.note(name,methods=list(METHODS[name]))
    def case_request_boundaries(self):
        codes=[]
        owner=n.native.GRC9V4ACIPCOperation(self.seed)
        for code,change in (('module_chirality_required',dict(module_chirality=None)),
                ('module_growth_phase_required',dict(growth_phase=None)),
                ('reject_noncanonical_inactive_growth_phase',dict(target_effective_degree=30,growth_phase=1))):
            pointer=owner._published;raw=owner.checkpoint()
            result=owner.expand(replace(self.request,**change))
            self.assertFalse(result.committed);self.assertEqual(result.failure.code,code)
            self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
            codes.append(code)
        self.note('request_boundaries',codes=codes,full_publication_rollback=True)
    def case_domain_and_history(self):self.exercise('domain_and_history')
    def case_atomicity(self):
        self.exercise('atomicity');owner=n.native.GRC9V4ACIPCOperation(self.seed)
        pointer,raw=owner._published,owner.checkpoint()
        with patch.object(n.native,'_EventPublication',side_effect=RuntimeError('late publication')):
            with self.assertRaisesRegex(RuntimeError,'late publication'):owner.expand(self.request)
        self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
        with patch.object(prior.GRC9V4ACIPCExpansion,'carrier_archive_payload',side_effect=ValueError('late archive')):
            self.assertFalse(owner.expand(self.request).committed)
        self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
        OBSERVATIONS['atomicity']['late_publication_pointer_unchanged']=True
    def case_replay(self):
        self.exercise('replay');cp=json.loads(self.owner.checkpoint());source=self.seed.inputs
        archive=cp['carrier_archives'];self.assertEqual(len(archive),1)
        self.assertEqual(tuple(archive[0]['history_content']['content']),source.current.Z_4+source.reset.Z_4)
        OBSERVATIONS['replay'].update(archive_count=1,both_whole_histories=True,checkpoint_exact=True)
    def case_readmission_no_writers(self):
        self.exercise('readmission_no_writers');OBSERVATIONS['readmission_no_writers']['zero_temporal_writes']=True
    def case_continuation_reset(self):
        before=self.owner.state.inputs
        owner=generic.GRCV4Operation(before,differential_reference=n.r.backend(before))
        self.assertEqual(owner.state.receipt_ledger,())
        result=owner.step_v4(GRCV4StepRequestInput('grcv4-step-request-input-v1','p985-acipc-step',2**-12,b.FrozenJSONMap({})))
        self.assertTrue(result.committed,result.failure)
        saved=owner.snapshot();owner=generic.GRCV4Operation.from_state(saved)
        self.assertEqual(owner.snapshot(),saved);self.assertNotEqual(owner.state.current.Z_4,before.current.Z_4)
        clock=(owner.state.step_index,owner.state.time);pointer=owner._owned
        with patch.object(generic,'_validate_publication',side_effect=ValueError('late reset')):
            with self.assertRaisesRegex(ValueError,'late reset'):owner.reset()
        self.assertIs(owner._owned,pointer);self.assertEqual(owner.snapshot(),saved)
        owner.reset();self.assertEqual(owner.state.current,before.reset)
        self.assertEqual(owner.state.reset.authoritative,before.reset)
        self.assertEqual((owner.state.step_index,owner.state.time),clock)
        reset=owner.snapshot();self.assertEqual(generic.GRCV4Operation.from_state(reset).snapshot(),reset)
        for field in ('receipt_ledger','commit_records'):
            bad=deepcopy(reset);bad[field].pop()
            with self.assertRaises(ValueError):generic.GRCV4Operation.from_state(bad)
        self.note('continuation_reset',native_steps=1,native_resets=1,full_authority_restored=True,
                    reset_rollback=True,clock_preserved=True,fresh_generic_ledger=True)


def small():
    OBSERVATIONS.clear()
    with integration_compute.worker():
        suite=unittest.TestSuite(Lifecycle('case_'+name) for name in CASES)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    b.require(result.wasSuccessful() and result.testsRun==6 and not result.skipped,'small lifecycle coverage')
    return dict(tests=6,cases=deepcopy(OBSERVATIONS))


def large():
    record=n.read('event');cp=record['execution']['checkpoint'];raw=canonical_json_bytes(cp)
    reads=[];implementation=n.native._FAMILY_IMPLEMENTATIONS['A_CI_PC']
    real=implementation.readmit;probe=n.native.ProvisionalCandidateCIStep
    def observed(state):
        points=[];before=state.to_payload()
        def capture(inputs,*args,**kw):
            b.require(inputs.dt==0,'replay advanced physical time')
            actual=probe(inputs,*args,**kw)
            b.require(actual.carrier_writes==0 and actual.next_inputs.current==inputs.current
                and actual.next_inputs.reset==inputs.reset,'replay changed complete history')
            points.append(dict(inputs=inputs.to_payload(),read=n.retained_read(actual.root),
                reset_read=n.retained_read(actual.reset_root),carrier_writes=actual.carrier_writes))
            return actual
        with patch.object(n.native,'ProvisionalCandidateCIStep',capture):out=real(state)
        b.require(before==state.to_payload() and len(points)==1,'readmission chronology')
        reads.append(dict(state=before,points=points));print('A_CI_PC large readmission '+str(len(reads))+' passed',flush=True)
        return out
    with patch.dict(n.native._FAMILY_IMPLEMENTATIONS,A_CI_PC=replace(implementation,readmit=observed)):
        restored=n.native.GRC9V4ACIPCOperation.replay(raw)
    b.require(restored.checkpoint()==raw and len(reads)==3 and reads[0]==reads[1]
        and reads[-1]['state']==cp['state'],'fresh exact replay')
    return dict(event_record_digest=record['record_digest'],checkpoint=cp,checkpoint_digest=b.digest(cp),
        readmissions=reads,exact_replay=True,fresh_native_events=1,fresh_ordinary_steps=0,temporal_history_writes=0)


def manifest():
    upstream=n.storage.read(n.INPUTS);n.check_manifest(upstream)
    paths={x['path'] for x in upstream['source_bindings']}|{SELF,n.INPUTS,n.filename('event'),
        'tests/models/test_grc_9_v4_lifecycle.py','tests/models/test_grc_9_v4_acipc.py',compute.SELF,compute.PREFLIGHT,
        integration_compute.SELF,integration_compute.PREFLIGHT}
    return b.seal(dict(schema='p985-acipc-inputs-v1',source_bindings=b.bind(paths),cases=list(CASES),
        caps=dict(small=600,large=3600),large_event_digest=n.read('event')['record_digest'],
        exact_backend='flint',small_policy='legacy_exact_v1',large_policy='certified_arb_256',user_accepted=False,aggregate_closed=False))


def check(m,v):
    b.check_digest(m);b.check_digest(v);b.check_bindings(m['source_bindings'])
    e=v['execution'];segment=v['segment']
    b.require(v['schema']=='p985-acipc-execution-v1' and v['manifest_digest']==m['record_digest']
        and v['outcome']=='passed' and 0<v['seconds']<=m['caps'][segment]
        and not v['user_accepted'] and not v['aggregate_closed'],'lifecycle scope')
    if segment=='small':
        b.require(e['tests']==6 and set(e['cases'])==set(CASES) and all(row['passed'] for row in e['cases'].values()),'six lifecycle obligations')
        for name,methods in METHODS.items():b.require(e['cases'][name]['methods']==list(methods),'method substitution')
        b.require(e['cases']['atomicity']['late_publication_pointer_unchanged'] and e['cases']['replay']['both_whole_histories']
            and e['cases']['readmission_no_writers']['zero_temporal_writes']
            and all(e['cases']['continuation_reset'][k] for k in ('full_authority_restored','reset_rollback','clock_preserved')),'lifecycle failures/reset coverage')
    else:
        original=n.read('event');cp=e['checkpoint'];reads=e['readmissions']
        b.require(e['event_record_digest']==m['large_event_digest']==original['record_digest']
            and cp==original['execution']['checkpoint'] and b.digest(cp)==e['checkpoint_digest']
            and len(reads)==3 and reads[0]==reads[1] and reads[-1]['state']==cp['state']
            and e['exact_replay'] and e['fresh_native_events']==1 and e['fresh_ordinary_steps']==e['temporal_history_writes']==0
            and len(cp['receipts'])==4 and len(cp['reference_currents'])==1
            and len(cp['carrier_archives'])==1,'large replay coverage')
        for row in reads:
            state=n.r.state(row['state']);b.require(len(row['points'])==1,'readmission count')
            p=row['points'][0];before=replace(state.inputs,dt=0)
            b.require(p['inputs']==before.to_payload() and p['carrier_writes']==0,'readmission incoming/write scope')
            n.check_read(before,p['read']);n.check_read(n.r.role_input(before,'reset'),p['reset_read'])
    return v


def child(pipe,segment):
    try:
        with wire_reuse(),n.compute_worker():
            pipe.send(('progress','A_CI_PC lifecycle '+segment+' verified FLINT/Arb/cache policy'))
            if segment=='large':result=large()
        # The established small domain counterexample uses the exact policy;
        # never carry Arb matrix facts across that policy boundary.
        if segment=='small':result=small()
        pipe.send(('result',n.portable(result)))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run(segment):
    m=n.storage.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(not (b.ROOT/path(segment)).exists(),'refuse overwrite')
    e,seconds=n.process_budget.capped(child,(segment,),m['caps'][segment])
    v=b.seal(dict(schema='p985-acipc-execution-v1',manifest_digest=m['record_digest'],segment=segment,
        execution=e,seconds=seconds,outcome='passed',user_accepted=False,aggregate_closed=False))
    with wire_reuse(),n.compute_worker():check(m,v)
    n.storage.save(path(segment),v);print(json.dumps(dict(segment=segment,seconds=seconds,outcome='passed')),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run'))
    parser.add_argument('--segment',choices=('small','large'),default='small');args=parser.parse_args()
    if args.action=='prepare':n.storage.save(INPUTS,manifest())
    else:run(args.segment)
