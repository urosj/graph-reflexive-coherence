"""One final join of executed C_RG2b subjects; no numerical campaign rerun."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import p9_crg2b_native_review as review
import p9_crg2b_large_successor as n
import p9_crg2b_large_covariance as cov
import p9_crg2b_large_science as science
import p9_crg2b_support as support
import p9_crg2b_close as close
c,r,b=n.c,n.r,n.b
SELF=b.HERE+'p9_crg2b_final_review.py'

def segment(task):
 role,index=task;name=n.path('step',role,index);value=c.read(name);b.check_digest(value)
 manifest=n.checked();event=c.read(n.path('event'));b.check_digest(event)
 predecessor=event if index==1 else c.read(n.path('step',role,index-1))
 b.check_digest(predecessor);v=value['execution']
 with r.worker():
  if index==1:
   actual=r.state(event['execution']['event']['actual_target'])
   before=replace(actual.inputs,current=getattr(actual.inputs,role),dt=b.DT)
  else:before=b.GeometryStageInputs.from_payload(predecessor['execution']['poststate'])
  b.require(v['event_digest']==event['record_digest'] and v['predecessor_digest']==predecessor['record_digest'],'large predecessor link')
  r.check_step(before,v)
 b.require(value['manifest_digest']==manifest['record_digest'] and value['outcome']=='passed'
  and (value['segment'],value['role'],value['index'])==('step',role,index)
  and 0<value['elapsed_seconds']<=3600 and value['compute_policy']['exact_backend']=='flint'
  and value['compute_policy']['numerical_policy']=='certified_arb_256'
  and r.Q(v['independent_bridge']['exact_real_next_resource_lower'])>0,'large segment scope')
 return dict(path=name,record_digest=value['record_digest'],seconds=value['elapsed_seconds'],
  resource_lower=v['independent_bridge']['exact_real_next_resource_lower'],resource_error=v['independent_bridge']['resource_error'])

def build():
 prior=review.checked();value=dict(prior);refs={x['path'] for x in prior['source_bindings']}|{SELF,n.SELF,n.INPUTS,n.path('source'),n.path('event'),cov.SELF,science.SELF,science.RESULT,support.SELF,support.MATRIX,support.SUPPORT,close.SELF,close.AUTHORITY}
 # The integration records already bind every Python runtime dependency,
 # including private matrix modules omitted by the numerical module glob.
 # Check those unchanged bytes and include them in the consolidated review.
 import p9_crg2b_integration as integration
 for key in integration.GROUPS:
  integration.check(key)
  refs|={x['path'] for x in c.read(integration.path(key))['source_bindings']}
 refs|={'pyproject.toml','uv.lock'}
 source=c.read(n.path('source'));b.check_digest(source);event=c.read(n.path('event'));b.check_digest(event)
 with r.worker():
  before=replace(n.old.source().inputs,dt=b.DT);r.check_step(before,source['execution'])
  seed=n.source();cc=n.old.case(seed)
  b.require(event['execution']['source']==seed.to_payload() and event['execution']['case']==cc,'actual event subject')
  actual=r.check_event(seed,cc,event['execution']['event'])
 # The event producer already executed fresh native replay. Its checked
 # checkpoint equality is reused here, with the actual event subject pinned.
 b.require(event['execution']['event']['replay_identical'],'large replay absent')
 jobs=[(role,i) for role in r.ROLES for i in range(1,11)]
 with ProcessPoolExecutor(max_workers=12) as pool:segments=list(pool.map(segment,jobs))
 refs|={x['path'] for x in segments};minimum=min(r.Q(v['resource_lower']) for v in segments)
 for role in r.ROLES:
  name=n.path('final',role);v=c.read(name);b.check_digest(v);last=c.read(n.path('step',role,10))
  with r.worker():
   expected=replace(b.GeometryStageInputs.from_payload(last['execution']['poststate']),dt=0)
   b.require(v['execution']['before']==expected.to_payload() and v['execution']['event_digest']==event['record_digest']
    and v['execution']['predecessor_digest']==last['record_digest'],'final lineage')
   r.check_read(expected,v['execution']['read'])
  refs.add(name)
 maximum=0.
 for kind in cov.KINDS:
  ev=c.read(cov.path(kind,'event'));b.check_digest(ev);b.check_bindings(ev['source_bindings']);refs.add(cov.path(kind,'event'))
  b.require(ev['outcome']=='passed' and ev['execution']['event']['replay_identical'],'mapped event/replay')
  for role in r.ROLES:
   name=cov.path(kind,role);v=c.read(name);b.check_digest(v);b.check_bindings(v['source_bindings']);refs.add(name)
   b.require(v['outcome']=='passed' and v['execution']['event_digest']==ev['record_digest']
    and r.Q(v['execution']['step']['independent_bridge']['exact_real_next_resource_lower'])>0,'mapped target continuation')
   maximum=max(maximum,v['execution']['maximum_covariance_error'])
 sc=c.read(science.RESULT);b.check_digest(sc);b.check_bindings(sc['source_bindings']);refs|={v['path'] for v in sc['source_bindings']}
 b.require(len(sc['cases'])==4 and all(all(m['fixed_H_effect_resolved'] for m in row['mechanisms'].values()) for row in sc['cases']),'large defining effects')
 matrix=c.read(support.MATRIX);b.require(matrix==support.matrix(),'matrix changed')
 ss=c.read(support.SUPPORT);b.check_digest(ss);b.check_bindings(ss['source_bindings']);refs|={v['path'] for v in ss['source_bindings']}
 cp=dict(prior['checkpoints']);cp.update({
  '8.4h':dict(outcome='passed',source_beats=2,actual_events=4,target_steps=20,mapped_steps=6,final_reads=2,
   minimum_pointwise_resource_lower=str(minimum),maximum_covariance_error=maximum,uniform_trajectory_enclosure=False),
  '8.4i':dict(outcome='passed',retained_subjects_verified=True,compressed_portable_evidence=True),
  '8.5':dict(outcome='passed',small_tests=6,large_native_replay=True,large_replay_reused_from_event=True,large_reset_executed=False),
  '8.6':dict(outcome='passed',small_mechanism_subjects=18,large_mechanism_subjects=4,C1_regularity_debt='narrowed_unresolved'),
  'tranche8_end':dict(outcome='passed',bounded_execution=True,acceptance='pending'),
  '9.3':dict(outcome='passed',counts=matrix['counts']),
  '9.6':dict(outcome='passed',exact_subject_record=support.SUPPORT,basin='unselected',tranche10='deferred')})
 value.update(stage='bounded_native_pass_pending_acceptance',checkpoints=cp,source_bindings=b.bind(refs),large_segments=segments,
  next_work='User review and bounded C_RG2b acceptance. A_RG2b and Tranche 10 remain outside this result.')
 return b.seal(value)

if __name__=='__main__':
 v=build();(b.ROOT/review.PATH).write_text(json.dumps(v,indent=2)+'\n');review.checked();print('all sixteen C_RG2b checkpoints passed; acceptance pending')
