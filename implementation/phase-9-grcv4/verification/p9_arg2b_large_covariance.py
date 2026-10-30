"""Three prioritized large counterparts; exact mappings and full native reads."""
import argparse,time,signal
from concurrent.futures import ProcessPoolExecutor,as_completed
from contextlib import contextmanager
from functools import lru_cache
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch
import p9_arg2b_large_successor as n
import p9_arg2b_covariance as small
import p984h_cos_covariance as maps
c,r,b=n.c,n.r,n.b
SELF=b.HERE+'p9_arg2b_large_covariance.py'
KINDS=('combined','reflect','rotate')

def path(kind,segment):return c.BASE+'large-covariance-'+kind+'-'+segment+'.json.xz'
@lru_cache(maxsize=1)
def baseline():
 # Immutable retained input only: mapping labels must not repeatedly decompress
 # and hash the same large event for every matrix coordinate. No native result
 # or admission decision is cached.
 v=c.read(n.path('event'));b.check_digest(v);return v['execution']['source'],v['execution']
@contextmanager
def transport():
 with patch.object(maps,'base',baseline):yield

def conjugate(a,ei,sign):return [[a[i][j]*sign[k]*sign[l] if a[i][j] else 0. for l,j in enumerate(ei)] for k,i in enumerate(ei)]

def input_image(original,graph,d,old_event=None,new_event=None):
 return small.image(original,graph,maps.mapping(original['reference']['graph'],graph,d,old_event,new_event))

def subject(kind):
 old,event=baseline();base=r.state(old)
 with transport():
  d=maps.declaration(kind);incoming=input_image(old['inputs'],maps.graph_image(old['inputs']['reference']['graph'],d,source=True),d)
  seed=replace(base,inputs=incoming);cc=deepcopy(event['case']);req=cc['request'];branches=d['chart']['branches'];shares=[0.]*3
  for i,x in enumerate(req['resource_distribution'],1):shares[branches[str(i)]-1]=x
  req.update(operation_id='arg2b-large-cov-'+kind,source_node_id=maps.rename(req['source_node_id'],d),
   source_state_digest=seed.scientific_digest,source_graph_digest=incoming.geometry.reference.graph.graph_digest,
   target_profile_template_id=c.arg2b_profile_template(incoming.geometry.reference).profile_template_id,
   resource_distribution=shares,module_chirality=req['module_chirality']*d['chart']['chirality_factor'],growth_phase=branches[str(req['growth_phase'])])
  req['history_policy']=r.r.history_policy(seed)
  identity=cc['oracle']['event_identity']
  for key in identity:
   if key in req and key!='schema_version':identity[key]=req[key]
  for channel in ('candidate','carrier'):
   key=channel+'_history_policy_digest';identity[key]=req['history_policy'][key]
  eid='grc-event-sha256:'+b.digest(identity)
  graph=maps.graph_image(event['event']['actual_target']['inputs']['reference']['graph'],d,cc['oracle']['event_id'],eid)
  cc['oracle']=dict(event_identity=identity,event_id=eid,target_graph=graph)
 return seed,cc,d

def execute(kind,segment):
 name=path(kind,segment)
 if (b.ROOT/name).exists():return c.read(name)
 refs=b.bind({SELF,small.SELF,n.INPUTS,n.path('event'),maps.SELF,c.ordering.SELF,c.chart.SELF})
 def expire(*_):raise TimeoutError('3600-second cap; no fallback')
 signal.signal(signal.SIGALRM,expire);signal.alarm(3600);start=time.monotonic()
 try:
  with r.worker() as policy:
   seed,cc,d=subject(kind)
   if segment=='event':
    owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(cc['request']))
    b.require(outcome.committed,'mapped native event rejected '+str(outcome.failure));r.check_event(seed,cc,event)
    execution=dict(source=seed.to_payload(),case=cc,event=event)
   else:
    ev=c.read(path(kind,'event'));b.check_digest(ev);target=r.state(ev['execution']['event']['actual_target'])
    before=replace(target.inputs,current=getattr(target.inputs,segment),dt=b.DT)
    value,after=r.perform_step(before);base=c.read(n.path('step',segment,1))['execution']
    original=baseline()[1]['event']['actual_target']['inputs']['reference']['graph']
    with transport():ix=maps.mapping(original,target.inputs.geometry.reference.graph.to_payload(),d,baseline()[1]['case']['oracle']['event_id'],cc['oracle']['event_id'])
    maximum=small.state_pair(base['poststate_full'],value['poststate_full'],ix)
    for key in ('read','reset_read','restart'):maximum=max(maximum,small.pair(base[key],value[key],ix))
    b.require(r.Q(value['independent_bridge']['exact_real_next_resource_lower'])>0,'mapped positivity')
    execution=dict(step=value,event_digest=ev['record_digest'],maximum_covariance_error=maximum)
  b.check_bindings(refs);row=b.seal(dict(schema='p9-arg2b-large-covariance-v1',source_bindings=refs,kind=kind,segment=segment,
   transform=d,outcome='passed',execution=execution,elapsed_seconds=time.monotonic()-start,compute_policy=policy,
   user_accepted=False,aggregate_closed=False));c.save(name,row)
  print('large covariance',kind,segment,'PASS',round(row['elapsed_seconds'],1),flush=True);return row
 finally:signal.alarm(0)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('events','steps'));a=p.parse_args()
 jobs=[(kind,segment) for kind in KINDS for segment in (('event',) if a.action=='events' else r.ROLES)]
 with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
  for f in as_completed([pool.submit(execute,*job) for job in jobs]):f.result()
