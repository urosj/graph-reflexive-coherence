"""Resumable connected A_RG2b native campaigns; one declared policy, no retries.

New numerical operands are bound independently of later publication wiring.
Each successful job retains full chains, reads, state/receipts and checks.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from dataclasses import replace
import json,lzma,time,signal
from pathlib import Path
import numpy as np
import p9_arg2b_runtime as r
import p984d_cos as deep
import p984c_cos as construction
import p984e_cos as ordering
import p984f_cos as chart
from pygrc.models.grc_9_v4_expansion import arg2b_profile_template
b=r.b
SELF=b.HERE+'p9_arg2b_campaign.py'
BASE=b.BASE+'arg2b-native/'
INPUTS=BASE+'Inputs.json'
ROLES=r.ROLES

def read(path):
 p=b.ROOT/path
 return json.loads(lzma.decompress(p.read_bytes()) if p.suffix=='.xz' else p.read_bytes())

def save(path,value):
 from p9_ccipc_capture import portable
 path=b.ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
 raw=json.dumps(portable(value),separators=(',',':'),allow_nan=False).encode()+b'\n'
 if path.suffix=='.xz':raw=lzma.compress(raw)
 with path.open('xb') as f:f.write(raw)

def paths():
 excluded={'grc_9_v4_api_lifecycle.py','grc_9_v4_owner.py','grc_9_v4_legacy.py'}
 result={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src/pygrc/models').glob('grc*v4*.py') if p.name not in excluded}
 result|={SELF,r.SELF,r.r.SELF,r.proof.SELF,r.oracle.SELF,deep.SELF,construction.SELF,ordering.SELF,chart.SELF,b.SELF,
  b.HERE+'p984b_cci_runtime.py',b.HERE+'p9_arg2b_positive.py',b.HERE+'p9_cpc_compute.py',b.HERE+'p9_cpc_covariance_compute.py',b.HERE+'p9_cpc_wire_reuse.py',
  b.HERE+'p984h_validation_reuse.py',b.HERE+'p9_ccipc_capture.py',r.r.INPUTS,deep.INPUTS,b.BASE+'P9-8.4c-ARG2bCases.json',
  b.BASE+'larger-graph-examples/A_RG2b.json','tests/models/test_grc_9_v4_arg2b.py',
  'specs/grc-9-v4-connected-a-rg2b-spec.md',b.BASE+'P9-ARG2b-ConnectedCompletionRelease.json'}
 return result

def rebind(seed,case,*,layout=None):
 case=deepcopy(case);ref=seed.inputs.geometry.reference;req=case['request']
 req.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
  target_profile_template_id=arg2b_profile_template(ref).profile_template_id,
  operation_id='arg2b-connected-'+case['fixture_id'])
 req['history_policy']=r.r.history_policy(seed)
 identity=deepcopy(case['oracle']['event_identity'])
 for key in identity:
  if key in req and key!='schema_version':identity[key]=req[key]
 for channel in ('candidate','carrier'):
  key=channel+'_history_policy_digest';identity[key]=req['history_policy'][key]
 case['oracle']['event_identity']=identity
 if layout is None:
  degree=req['target_effective_degree'];n=max(4,(degree+4)//7);q,remainder=divmod(n-4,3);extras=[q]*3
  for j in range(remainder):extras[(req['growth_phase']-1+req['module_chirality']*j)%3]+=1
  layout=dict(chirality=req['module_chirality'],expected=dict(module_nodes=n,branch_extras=extras))
 case['oracle']=construction.target_oracle(seed.to_payload(),case,req,layout)
 return case

def make_manifest():
 old=read(b.BASE+'P9-8.4c-ARG2bCases.json');initial=r.configure(b.GeometryStageInputs.from_payload(old['initial_inputs']))
 nominal=replace(r.state(old['nominal_source']),inputs=replace(initial,dt=0))
 # A fresh native source beat under the newly selected completion identity.
 with r.worker():source_step,after=r.perform_step(initial)
 seed=replace(nominal,inputs=replace(after,dt=0));cases=[]
 for layout in deep.layouts():
  c=deepcopy(old['cases'][0]);c.update(fixture_id=layout['id'],case_id=layout['id']+'::A_RG2b')
  c['request'].update(target_effective_degree=layout['degree'],module_chirality=layout['chirality'],
    growth_phase=layout['phase'],resource_distribution=layout['shares'])
  cases.append(rebind(seed,c,layout=layout))
 small=[rebind(seed,c) for c in old['cases']]
 return b.seal(dict(schema='p9-arg2b-native-inputs-v1',family='A_RG2b',source_bindings=b.bind(paths()),
  initial_inputs=initial.to_payload(),source_step=source_step,source=seed.to_payload(),deep_cases=cases,small_cases=small,
  scope=dict(deep_events=20,deep_steps_per_role=10,small_covariance_steps_per_role=2,large_steps_per_role=10,
    large_cap_seconds=3600,at_most_workers=12,uniform_trajectory_enclosure=False,C1_regularity_debt='narrowed_unresolved'),
  user_accepted=False,aggregate_closed=False))

def check_manifest(m):
 b.check_digest(m);b.check_bindings(m['source_bindings'])
 b.require(m['family']=='A_RG2b' and len(m['deep_cases'])==20 and not m['user_accepted'],'manifest scope')
 return m

def preflight(target,steps):
 _,data=r.data(target);n=len(target.current.C)
 current=np.asarray(list(target.current.C)+[512*r.math.log(w) for w in target.current.W_A]);rows=[]
 for _ in range(steps):
  xs,hs=r.oracle.proposal(data,current)
  with r.ctx.workprec(192):
   f=r.oracle.literal(data,current,r.mat(hs[0]))['increment']
   following=np.asarray([float(r.ball(v)+f[k,0]) for k,v in enumerate(current)])
  b.require(min(following[:n])>=0 and max(following[:n])<=4.25 and max(abs(following[n:]))<.625,'declared continuation outside physical K_minus')
  rows.append(dict(minimum=float(min(following[:n])),C=following[:n].tolist(),Y=following[n:].tolist()));current=following
 return rows

def positivity(before,value,case):
 if case['request']['target_effective_degree']==94:
  import p9_arg2b_positive as p
  read=value['read'];result=p.certify(before.geometry.reference.graph.port_graph.to_payload(),before.current.C,before.current.W_A,
   read['chain']['work'],read['independent_certificate']['section'])
  value['componentwise_positivity']=result
  b.require(result['strictly_positive'],'componentwise infinite-section positivity unresolved')
 else:b.require(r.Q(value['independent_bridge']['exact_real_next_resource_lower'])>0,'uncertified positive target step')

def selected(m):
 companion=read(BASE+'D94Allocation.json');b.check_digest(companion)
 for case in m['deep_cases']:
  if case['request']['target_effective_degree']==94:
   yield r.state(companion['source']),next(v for v in companion['cases'] if v['fixture_id']==case['fixture_id'])
  else:yield r.state(m['source']),case

def run_case(seed,case,steps):
 target=r.independent_target(dict(expected_source=seed.to_payload()),case)
 predictions={role:preflight(replace(target,current=getattr(target,role)),steps) for role in ROLES}
 owner=r.r.native.GRC9V4ARG2bOperation(seed);checkpoint=owner.checkpoint()
 stale=dict(case['request'],source_state_digest='grcv4-state-sha256:'+'0'*64)
 rejected=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(stale))
 b.require(not rejected.committed and owner.checkpoint()==checkpoint,'stale request publication changed')
 owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(case['request']))
 b.require(outcome.committed,'native event failed: '+str(outcome.failure))
 actual=r.check_event(seed,case,event);roles={}
 for role in ROLES:
  before=replace(actual.inputs,current=getattr(actual.inputs,role),dt=b.DT);rows=[]
  for i in range(steps):
   incoming=before;value,before=r.perform_step(before)
   positivity(incoming,value,case)
   b.require(max(abs(v-w) for v,w in zip(before.current.C,predictions[role][i]['C'],strict=True))<2**-39,'independent screened trajectory mismatch')
   rows.append(value)
  roles[role]=dict(steps=rows,final=r.native_read(replace(before,dt=0)))
 return dict(source=seed.to_payload(),case=case,event=event,roles=roles,preflight=predictions,stale_rejection=rejected.failure.to_payload(),
   whole_publication_rollback=True,case_passed=True)

def deep_job(args):
 source,c=args;start=time.monotonic()
 with r.worker():value=run_case(r.state(source),c,10)
 print(c['fixture_id'],'PASS',round(time.monotonic()-start,1),flush=True)
 return value

def check_case(seed,row,steps,*,numerics=False):
 target=r.check_event(seed,row['case'],row['event'],numerics=numerics)
 case_degree=row['case']['request']['target_effective_degree']
 b.require(row['case_passed'] and row['whole_publication_rollback'] and row['stale_rejection'],'event/rollback scope')
 for role in ROLES:
  values=row['roles'][role];before=replace(target.inputs,current=getattr(target.inputs,role),dt=b.DT)
  b.require(len(values['steps'])==steps,'missing target steps')
  for value in values['steps']:
   before=r.check_step(before,value,numerics=numerics)
   if case_degree==94:
    v=value['componentwise_positivity'];b.check_digest(v)
    b.require(v['policy']=='joint_inverse_componentwise_image_arb192_v1' and v['strictly_positive'] and min(map(r.Q,v['resource_lowers']))==r.Q(v['exact_real_next_resource_lower'])>0
     and v['section_certificate_digest']==b.digest(value['read']['independent_certificate']['section']),'componentwise positivity binding')
   else:b.require(r.Q(value['independent_bridge']['exact_real_next_resource_lower'])>0,'target positivity')
  r.check_read(replace(before,dt=0),values['final'],numerics=numerics)
 return target

def run_deep(m,workers):
 results=[];pending=[]
 with ProcessPoolExecutor(max_workers=workers) as pool:
  for seed,c in selected(m):
   name=BASE+'deep-'+c['fixture_id']+'.json.xz'
   if (b.ROOT/name).exists():
    row=read(name);b.check_digest(row);b.require(row['manifest_digest']==m['record_digest'],'resume manifest');results.append(row)
   else:pending.append((pool.submit(deep_job,(seed.to_payload(),c)),name))
  by_future=dict(pending)
  for future in as_completed(by_future):
   row=b.seal(dict(manifest_digest=m['record_digest'],execution=future.result(),user_accepted=False))
   save(by_future[future],row);results.append(row)
 for row in results:
  case=row['execution']['case'];seed=next(seed for seed,cc in selected(m) if cc['fixture_id']==case['fixture_id'])
  check_case(seed,row['execution'],10)
 return dict(events=len(results),target_steps=40*len(results)//2,user_accepted=False)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','deep','check'))
 p.add_argument('--workers',type=int,default=12);a=p.parse_args()
 b.require(1<=a.workers<=12,'worker cap')
 if a.action=='prepare':save(INPUTS,make_manifest());print(INPUTS)
 else:
  m=check_manifest(read(INPUTS))
  if a.action=='deep':print(json.dumps(run_deep(m,a.workers)))
  else:
   for seed,c in selected(m):
    row=read(BASE+'deep-'+c['fixture_id']+'.json.xz');b.check_digest(row)
    b.require(row['manifest_digest']==m['record_digest'],'retained manifest')
    check_case(seed,row['execution'],10)
   print('20 events / 400 target steps: retained integrity PASS (no native rerun)')
