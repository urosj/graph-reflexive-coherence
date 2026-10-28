"""A_OS lifecycle pressure on the accepted small and actual larger target."""
import argparse
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import replace
import json
import lzma
import time
import unittest
from unittest.mock import patch

import p984gh_aos_native as n
import p985_batch as shared
import test_p985_batch as suites
from tests.models import test_grc_9_v4_aos as fixture

b=n.b
SELF=b.HERE+'p985_aos.py'
INPUTS=b.BASE+'P9-8.5-AOSInputs.json'
METHODS=dict(domain=['test_real_target_split_rejects_current_only_and_reset_only',
    'test_policy_rehashed_role_substitutions_fail_at_admission'],
    atomic=['test_charge_both_roles_and_late_receipt_failures_roll_back'],
    replay=['test_replay_rejects_history_reference_identity_and_receipt_tampering',
    'test_rehashed_target_authority_and_source_policy_do_not_bypass_replay'],
    writers=['test_event_admission_never_advances_or_runs_a_writer'])


def path(segment):
    b.require(segment in ('small','large'),'lifecycle segment')
    return b.BASE+'P9-8.5-AOS-'+segment+'.json.xz'


def manifest():
    upstream=n.g.storage.read(n.INPUTS);n.check_manifest(upstream)
    paths={r['path'] for r in upstream['source_bindings']}|{SELF,shared.SELF,shared.TEST,
        shared.common.SELF,n.filename('event'),'tests/models/test_grc_9_v4_aos.py',
        fixture.RECORD.relative_to(b.ROOT).as_posix()}
    return b.seal(dict(schema='p985-aos-inputs-v1',source_bindings=b.bind(paths),
        small_cases=list(shared.CASES),methods=METHODS,caps=dict(small=600,large=1200),
        large_event_digest=n.read('event')['record_digest'],exact_backend='flint',
        small_policy='legacy_exact_v1',large_policy='certified_arb_256_weighted_v1',
        user_accepted=False,aggregate_closed=False))


def small():
    # Reuse the six established lifecycle obligations with explicit A_OS fixture
    # providers and the A_OS-specific natural split/domain rejection methods.
    methods=dict(suites.METHODS,A_OS=METHODS)
    tags=dict(shared.TAGS,A_OS='AOS')
    original=shared.fixture_module
    provider=lambda family:fixture if family=='A_OS' else original(family)
    with patch.dict(suites.METHODS,methods),patch.dict(shared.TAGS,tags),patch.object(shared,'fixture_module',provider),shared.scope('small'):
        shared.OBSERVATIONS.clear()
        def atomicity(self):
            methods=self.prior_cases('atomic');owner=self.Op(self.seed)
            pointer,raw=owner._published,owner.checkpoint()
            # The current transition requires a concrete lifecycle-result type.
            # Inject at final publication rather than replacing that type.
            with patch.object(n.native,'_EventPublication',side_effect=RuntimeError('late publication')):
                with self.assertRaisesRegex(RuntimeError,'late publication'):owner.expand(self.request)
            self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
            self.record_case('atomicity',methods=methods,late_publication_pointer_unchanged=True,
                prospective_archive_and_reference_records_not_published=True)
        cls=type('AOSLifecycle',(suites.FamilyLifecycleTests,),{'FAMILY':'A_OS','test_atomicity':atomicity})
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
        b.require(result.wasSuccessful() and result.testsRun==6 and not result.skipped,'small lifecycle failure')
        return dict(tests=6,cases=deepcopy(shared.OBSERVATIONS))


def large():
    prior=n.read('event');cp=prior['execution']['checkpoint']
    raw=n.g.mechanical.canonical_json_bytes(cp);reads=[]
    real_read=n.native._aos_readmit;real_pass=n.native.CandidateAOSPass
    def observed(state):
        points=[];before=state.to_payload()
        def capture(inputs,backend):
            actual=real_pass(inputs,backend)
            expected=n.g.analyze(n.subject(inputs),'current',inputs.dt)
            n.compare_point(n.point(actual.predictor),expected['predictor'])
            n.compare_point(n.point(actual.corrector),expected['corrector'])
            h=[list(row) for row in actual.residual.geometry.one_form_hodge.matrix]
            b.require(h==expected['H'] and actual.residual.admitted,'event OS split')
            points.append(dict(inputs=inputs.to_payload(),predictor=n.point(actual.predictor),
                corrector=n.point(actual.corrector),H=h,oracle=expected))
            return actual
        with patch.object(n.native,'CandidateAOSPass',capture):out=real_read(state)
        b.require(state.to_payload()==before and len(points)==2,'readmission authority/roles')
        reads.append(dict(state=before,roles=list(n.ROLES),points=points))
        print('A_OS large readmission '+str(len(reads))+' passed',flush=True)
        return out
    implementation=n.native._FAMILY_IMPLEMENTATIONS['A_OS']
    with patch.dict(n.native._FAMILY_IMPLEMENTATIONS,A_OS=replace(implementation,readmit=observed)):
        restored=n.native.GRC9V4AOSOperation.replay(raw)
    b.require(restored.checkpoint()==raw and len(reads)==3 and reads[0]==reads[1],'large replay/source reconstruction')
    b.require(reads[-1]['state']==cp['state'] and len(cp['receipts'])==4
        and len(cp['reference_currents'])==1 and not cp.get('carrier_archives'),'large lifecycle coverage')
    return dict(event_record_digest=prior['record_digest'],checkpoint_digest=b.digest(cp),
        checkpoint=cp,readmissions=reads,exact_replay=True,fresh_native_events=1,
        fresh_ordinary_steps=0,temporal_history_writes=0,receipt_count=4)


def check(m,v):
    b.check_digest(m);b.check_digest(v);b.check_bindings(m['source_bindings'])
    segment=v['segment'];e=v['execution']
    b.require(v['schema']=='p985-aos-execution-v1' and v['manifest_digest']==m['record_digest']
        and v['outcome']=='passed' and not v['user_accepted'] and not v['aggregate_closed']
        and 0<v['seconds']<=m['caps'][segment],'lifecycle scope')
    if segment=='small':
        b.require(e['tests']==6 and set(e['cases'])==set(shared.CASES)
            and all(row['passed'] for row in e['cases'].values()),'small coverage')
        for case,key in (('domain_and_history','domain'),('atomicity','atomic'),('replay','replay'),('readmission_no_writers','writers')):
            b.require(e['cases'][case]['methods']==METHODS[key],'A_OS method substitution')
        c=e['cases']['continuation_reset']
        b.require(c['full_authority_restored'] and c['reset_rollback'] and c['native_steps']==c['native_resets']==1,'reset authority')
    else:
        prior=n.read('event');reads=e['readmissions']
        b.require(e['event_record_digest']==m['large_event_digest']==prior['record_digest']
            and e['checkpoint']==prior['execution']['checkpoint'] and e['checkpoint_digest']==b.digest(e['checkpoint'])
            and len(reads)==3 and reads[0]==reads[1] and reads[-1]['state']==e['checkpoint']['state']
            and e['fresh_native_events']==1 and e['fresh_ordinary_steps']==e['temporal_history_writes']==0
            and e['exact_replay'] and e['receipt_count']==4,'large replay coverage')
        for row in reads:
            b.require(row['roles']==list(n.ROLES) and len(row['points'])==2,'readmission roles')
            inputs=n.state(row['state']).inputs
            for role,point in zip(n.ROLES,row['points'],strict=True):
                wanted=replace(inputs,current=getattr(inputs,role),dt=1)
                b.require(point['inputs']==wanted.to_payload() and point['oracle']['subject_digest']==b.digest(n.subject(wanted)),'readmission input')
                for key in ('predictor','corrector'):n.compare_point(point[key],point['oracle'][key])
                b.require(point['H']==point['oracle']['H'],'readmission geometry')
    return v


def run(segment):
    m=n.g.storage.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(not (b.ROOT/path(segment)).exists(),'refuse overwrite')
    started=time.monotonic()
    with b.budget(m['caps'][segment]),(n.policy() if segment=='large' else nullcontext()):
        e=small() if segment=='small' else large()
    v=b.seal(dict(schema='p985-aos-execution-v1',manifest_digest=m['record_digest'],segment=segment,
        execution=e,seconds=time.monotonic()-started,outcome='passed',user_accepted=False,aggregate_closed=False))
    with n.policy():check(m,v)
    with (b.ROOT/path(segment)).open('xb') as stream:stream.write(lzma.compress(json.dumps(v,separators=(',',':')).encode()+b'\n'))
    print(json.dumps(dict(segment=segment,outcome='passed',seconds=v['seconds'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','run'))
    p.add_argument('--segment',choices=('small','large'),default='small');args=p.parse_args()
    if args.action=='prepare':b.write_new(INPUTS,manifest())
    else:run(args.segment)
