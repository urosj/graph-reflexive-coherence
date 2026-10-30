"""Retained C_RG2b execution coverage, separate from acceptance and research."""
import hashlib,json,lzma
from pathlib import Path
import p9_crg2b_campaign as c
b=c.b
SELF=b.HERE+'p9_crg2b_native_review.py'
PATH=c.BASE+'Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end','9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')

def checked(root=b.ROOT):
 from p9_arg2b_historical import matches
 root=Path(root).resolve();value=json.loads((root/PATH).read_bytes());b.check_digest(value)
 b.require(value['schema']=='p9-crg2b-native-review-v1' and value['family']=='C_RG2b'
  and value['user_accepted'] is False and value['aggregate_closed'] is False and value['C1_regularity_debt']=='narrowed_unresolved',
  'C_RG2b native scope drift')
 b.require(value['stage'] in ('native_execution_in_progress','bounded_native_pass_pending_acceptance')
  and value['large_covariance_selected']==['combined','reflect','rotate']
  and value['large_covariance_deferred']==['edge_order','node_order','relabel','signed','rotate_twice']
  and value['check_level']=='retained_integrity_only_no_numerical_rerun','C_RG2b execution ceiling drift')
 for row in value['source_bindings']:
  b.require(matches(root,row['path'],row['sha256']),'C_RG2b source drift: '+row['path'])
 b.require(set(value['checkpoints'])<=set(STEPS),'unknown checkpoint')
 complete=value['stage']=='bounded_native_pass_pending_acceptance'
 b.require(complete==(set(value['checkpoints'])==set(STEPS)),'premature native closure')
 b.require(all(row['outcome']=='passed' for row in value['checkpoints'].values()),'failed checkpoint advertised')
 return value

def partial():
 """Called after execution/checkers, never interpreted as completed large work."""
 import p9_crg2b_covariance as cov
 import p9_crg2b_integration as integ
 import p9_crg2b_large as large
 import p9_crg2b_lifecycle as life
 import p9_crg2b_science as science
 m=c.check_manifest(c.read(c.INPUTS));refs=set(c.paths())|{SELF,c.INPUTS,large.SELF,large.INPUTS,cov.SELF,
  integ.SELF,life.SELF,science.SELF,life.RESULT,science.RESULT,
  'tests/models/test_grc_9_v4_crg2b_integration.py',b.HERE+'test_p9_crg2b_native.py'}
 checkpoints={}
 for cc in m['deep_cases']:
  name=c.BASE+'deep-'+cc['fixture_id']+'.json.xz';row=c.read(name);b.check_digest(row)
  b.require(row['manifest_digest']==m['record_digest'],'deep source binding')
  # Deep check previously ran all state/read/receipt consumers. This joins exact
  # retained identities without claiming a second producer or numerical rerun.
  b.require(row['execution']['case_passed'] and len(row['execution']['roles']['current']['steps'])==10
   and len(row['execution']['roles']['reset']['steps'])==10,'deep coverage')
  refs.add(name)
 checkpoints['8.4d']=dict(outcome='passed',events=20,target_steps=400,final_reads=40)
 for k in ('e','f'):
  value=cov.check(m,k);checkpoints['8.4'+k]=dict(outcome='passed',**value)
  refs|={cov.path(k,d['kind']) for d in (c.ordering if k=='e' else c.chart).declarations()}
 for s in ('source','prepared_target'):
  for role in c.r.ROLES:
   name=large.path(s,role);row=c.read(name);b.check_digest(row)
   b.require(row['outcome']=='passed' and c.r.Q(row['execution']['independent_bridge']['exact_real_next_resource_lower'])>0,'large first-step admission')
   refs.add(name)
 checkpoints['8.4g']=dict(outcome='passed',native_steps=4,graphs=['100/400','107/407'],histories=['current','reset'])
 for key in integ.GROUPS:
  integ.check(key);refs.add(integ.path(key));checkpoints[key]=dict(outcome='passed',tests=integ.COUNTS[key])
 for name in (life.RESULT,science.RESULT):
  row=c.read(name);b.check_digest(row);b.check_bindings(row['source_bindings'])
  refs|={v['path'] for v in row['source_bindings']}
 value=b.seal(dict(schema='p9-crg2b-native-review-v1',family='C_RG2b',stage='native_execution_in_progress',
  checkpoints=checkpoints,source_bindings=b.bind(refs),small_lifecycle_passed=True,small_mechanisms_passed=True,
  C1_regularity_debt='narrowed_unresolved',large_covariance_selected=['combined','reflect','rotate'],
  large_covariance_deferred=['edge_order','node_order','relabel','signed','rotate_twice'],
  check_level='retained_integrity_only_no_numerical_rerun',user_accepted=False,aggregate_closed=False,
  next_work='Complete actual large event/replay, ten-step histories, prioritized covariance and large lifecycle; then consolidate bounded review.'))
 target=b.ROOT/PATH
 if target.exists():b.require(c.read(PATH)['user_accepted'] is False,'accepted native review is immutable')
 target.write_text(json.dumps(value,indent=2)+'\n')
 return value

if __name__=='__main__':partial();print('C_RG2b progress indexed; large continuation remains open')
