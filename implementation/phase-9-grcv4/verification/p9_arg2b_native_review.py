"""Join executed A_RG2b records without rerunning their numerical producers."""
from pathlib import Path
from copy import deepcopy
from dataclasses import replace
import json
import p9_arg2b_campaign as c
b,r=c.b,c.r
SELF=b.HERE+'p9_arg2b_native_review.py'
PATH=c.BASE+'Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end','9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')
SELECTED=['combined','reflect','rotate']
DEFERRED=['edge_order','node_order','relabel','signed','rotate_twice']
COUNTS=dict(bounded_accepted=36,passed_pending_acceptance=4,unselected_not_executed=0)

def checked(root=b.ROOT):
 root=Path(root).resolve();v=json.loads((root/PATH).read_bytes());b.check_digest(v)
 b.require(v['schema']=='p9-arg2b-native-review-v1' and v['family']=='A_RG2b'
  and v['stage']=='bounded_native_pass_pending_acceptance' and v['user_accepted'] is False
  and v['aggregate_closed'] is False and v['C1_regularity_debt']=='narrowed_unresolved'
  and v['check_level']=='retained_integrity_only_no_numerical_rerun'
  and v['large_covariance_selected']==SELECTED and v['large_covariance_deferred']==DEFERRED
  and v['uniform_trajectory_enclosure'] is False and v['tranche10']=='deferred', 'A_RG2b scope drift')
 b.require(set(v['checkpoints'])==set(STEPS) and all(x['outcome']=='passed' for x in v['checkpoints'].values()),'incomplete checkpoint coverage')
 cp=v['checkpoints']
 b.require(cp['9.3']['counts']==COUNTS and cp['8.4d']['events']==20 and cp['8.4d']['target_steps']==400
  and cp['8.4h']['actual_events']==4 and cp['8.4h']['target_steps']==20 and cp['8.4h']['mapped_steps']==6
  and cp['8.5']['small_tests']==6 and cp['8.6']['small_mechanism_subjects']==18
  and cp['8.6']['large_mechanism_subjects']==4, 'A_RG2b coverage drift')
 names=[row['path'] for row in v['source_bindings']]
 b.require(len(names)==len(set(names)) and c.paths()|{SELF,c.INPUTS}<=set(names),'missing native source bindings')
 for row in v['source_bindings']:
  name=Path(row['path'])
  b.require(not name.is_absolute() and '..' not in name.parts,'nonportable source binding')
  b.require(b.sha((root/row['path']).read_bytes())==row['sha256'],'A_RG2b source drift: '+row['path'])
 return v

def build():
 import p9_arg2b_covariance as cov
 import p9_arg2b_large as large
 import p9_arg2b_large_successor as n
 import p9_arg2b_large_covariance as mapped
 import p9_arg2b_lifecycle as life
 import p9_arg2b_science as science
 import p9_arg2b_large_science as large_science
 import p9_arg2b_integration as integration
 import p9_arg2b_support as support
 import p9_arg2b_close as close
 refs=set(c.paths())|{SELF,c.INPUTS,c.BASE+'D94Allocation.json',cov.SELF,cov.INPUTS,n.SELF,n.INPUTS,
  large.SELF,large.INPUTS,mapped.SELF,life.SELF,science.SELF,large_science.SELF,
  integration.SELF,support.SELF,close.SELF,'pyproject.toml','uv.lock'}
 def read(name):
  v=c.read(name)
  if name in {integration.path(key) for key in integration.GROUPS}:
   b.require(v==integration.seal(v),'native integration JSON digest')
  else:b.check_digest(v)
  refs.add(name)
  if 'source_bindings' in v:
   b.check_bindings(v['source_bindings']);refs.update(x['path'] for x in v['source_bindings'])
  return v
 m=c.check_manifest(read(c.INPUTS));comp=read(c.BASE+'D94Allocation.json');cp={}
 for cc in m['deep_cases']:
  row=read(c.BASE+'deep-'+cc['fixture_id']+'.json.xz');v=row['execution']
  b.require(row['manifest_digest']==m['record_digest'] and v['case_passed'],'deep result/subject')
  companion=cc['request']['target_effective_degree']==94
  expected=next(x for x in comp['cases'] if x['fixture_id']==cc['fixture_id']) if companion else cc
  source=(comp if companion else m)['source']
  # Every event retained its actual source checkpoint. Later records also
  # duplicate that source at top level; the checkpoint is the common binding.
  b.require(v['case']==expected and v['event']['source_checkpoint']['state']==source,'deep source/allocation subject')
  if 'source' in v:b.require(v['source']==source,'duplicated source mismatch')
  for role in r.ROLES:
   b.require(len(v['roles'][role]['steps'])==10,'missing deep steps')
   for step in v['roles'][role]['steps']:
    # The producer already checked full selected point, writer and continuation.
    # Retain global vs componentwise positivity as separate certificates.
    bridge=step['independent_bridge']
    if cc['request']['target_effective_degree']!=94:
     b.require(r.Q(bridge['exact_real_next_resource_lower'])>0,'deep global sign')
    else:
     cert=step['componentwise_positivity'];b.check_digest(cert)
     b.require(cert['strictly_positive'] and min(map(r.Q,cert['resource_lowers']))==r.Q(cert['exact_real_next_resource_lower'])>0
      and cert['section_certificate_digest']==b.digest(step['read']['independent_certificate']['section']),'deep componentwise sign binding')
 cp['8.4d']=dict(outcome='passed',events=20,target_steps=400,final_reads=40,
  D94_componentwise_frontier_certificate=True,original_exclusion_preserved=True)
 cm=c.check_manifest(read(cov.INPUTS))
 for k in ('e','f'):
  declarations=(c.ordering if k=='e' else c.chart).declarations();events=0
  for d in declarations:
   v=read(cov.path(k,d['kind']));b.require(v['manifest_digest']==cm['record_digest'] and v['transform']==d,'mapped identity')
   b.require(all(x['case_passed'] for x in v['cases']),'mapped case failed');events+=len(v['cases'])
  cp['8.4'+k]=dict(outcome='passed',events=events,target_steps=4*events,required_history_cells=2*len(cov.cases(cm,k))*(len(declarations)-1))
 for s in ('source','prepared_target'):
  for role in r.ROLES:
   v=read(large.path(s,role));b.require(v['outcome']=='passed' and r.Q(v['execution']['independent_bridge']['exact_real_next_resource_lower'])>0,'prepared sign')
 cp['8.4g']=dict(outcome='passed',native_steps=4,graphs=['100/400','107/407'],histories=list(r.ROLES))
 nm=read(n.INPUTS);source=read(n.path('source'));event=read(n.path('event'))
 b.require(source['manifest_digest']==event['manifest_digest']==nm['record_digest'] and event['outcome']=='passed'
  and event['execution']['event']['replay_identical'],'large event/replay')
 minimum=None;segments=[]
 for role in r.ROLES:
  previous=event
  for i in range(1,11):
   name=n.path('step',role,i);v=read(name);ex=v['execution']
   b.require(v['manifest_digest']==nm['record_digest'] and v['outcome']=='passed'
    and (v['segment'],v['role'],v['index'])==('step',role,i)
    and ex['event_digest']==event['record_digest'] and ex['predecessor_digest']==previous['record_digest']
    and 0<v['elapsed_seconds']<=3600 and v['compute_policy']['exact_backend']=='flint', 'large chain subject')
   if i>1:b.require(ex['prestate']==previous['execution']['poststate_full'],'large state chain')
   else:
    target=b.GeometryStageInputs.from_payload(event['execution']['event']['actual_target']['inputs'])
    expected=replace(target,current=getattr(target,role),dt=b.DT).to_payload()
    b.require(ex['prestate']==expected,'large actual event target/role binding')
   lower=r.Q(ex['independent_bridge']['exact_real_next_resource_lower']);b.require(lower>0,'large certified positivity')
   minimum=lower if minimum is None else min(minimum,lower)
   segments.append(dict(path=name,record_digest=v['record_digest'],seconds=v['elapsed_seconds'],resource_lower=str(lower)))
   previous=v
  final=read(n.path('final',role));ex=final['execution']
  expected=replace(b.GeometryStageInputs.from_payload(previous['execution']['poststate_full']),dt=0.).to_payload()
  b.require(final['outcome']=='passed' and ex['before']==expected and ex['predecessor_digest']==previous['record_digest']
   and ex['event_digest']==event['record_digest'],'final read lineage')
 maximum=0.
 for kind in mapped.KINDS:
  ev=read(mapped.path(kind,'event'));b.require(ev['outcome']=='passed' and ev['execution']['event']['replay_identical'],'mapped replay')
  for role in r.ROLES:
   v=read(mapped.path(kind,role));ex=v['execution']
   b.require(v['outcome']=='passed' and ex['event_digest']==ev['record_digest']
    and r.Q(ex['step']['independent_bridge']['exact_real_next_resource_lower'])>0,'mapped target sign')
   maximum=max(maximum,ex['maximum_covariance_error'])
 cp['8.4h']=dict(outcome='passed',source_beats=2,actual_events=4,target_steps=20,mapped_steps=6,final_reads=2,
  minimum_pointwise_resource_lower=str(minimum),maximum_covariance_error=maximum)
 cp['8.4i']=dict(outcome='passed',retained_subjects_verified=True,uniform_trajectory_enclosure=False)
 lv=read(life.RESULT);b.require(lv['tests_run']==6 and lv['outcome']=='passed','lifecycle coverage')
 cp['8.5']=dict(outcome='passed',small_tests=6,large_native_replay=True,large_reset_executed=False)
 for name,count in ((science.RESULT,18),(large_science.RESULT,4)):
  v=read(name);b.require(len(v['cases'])==count and all(all(m['fixed_H_effect_resolved'] for m in x['mechanisms'].values()) for x in v['cases']),'defining mechanism margins')
 cp['8.6']=dict(outcome='passed',small_mechanism_subjects=18,large_mechanism_subjects=4,C1_regularity_debt='narrowed_unresolved')
 cp['tranche8_end']=dict(outcome='passed',bounded_execution=True,acceptance='pending')
 for key in integration.GROUPS:
  integration.check(key);read(integration.path(key));cp[key]=dict(outcome='passed',tests=integration.COUNTS[key])
 matrix=read(support.MATRIX);b.require(matrix==support.matrix(),'compatibility matrix');read(close.AUTHORITY);read(support.SUPPORT)
 cp['9.3']=dict(outcome='passed',counts=matrix['counts'])
 cp['9.6']=dict(outcome='passed',exact_subject_record=support.SUPPORT,basin='unselected',tranche10='deferred')
 return b.seal(dict(schema='p9-arg2b-native-review-v1',family='A_RG2b',stage='bounded_native_pass_pending_acceptance',
  checkpoints=cp,source_bindings=b.bind(refs),large_segments=segments,C1_regularity_debt='narrowed_unresolved',
  large_covariance_selected=SELECTED,large_covariance_deferred=DEFERRED,uniform_trajectory_enclosure=False,
  check_level='retained_integrity_only_no_numerical_rerun',user_accepted=False,aggregate_closed=False,tranche10='deferred',
  next_work='Review and bounded A_RG2b acceptance; implementation commit first, acceptance separately. Tranche 10 remains deferred.'))

if __name__=='__main__':
 v=build();(b.ROOT/PATH).write_text(json.dumps(v,indent=2)+'\n');checked();print('sixteen A_RG2b checkpoints passed; acceptance pending')
