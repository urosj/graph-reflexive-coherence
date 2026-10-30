"""Large connected C_RG2b: prepared operands, actual event, native continuation.

Each successful segment is retained; a 3600-second cap has no numerical retry.
"""
import argparse,json,time,signal
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from dataclasses import replace
import p9_crg2b_campaign as c
import prepare_p983_all_realizations as mechanical
r,b=c.r,c.b
SELF=b.HERE+'p9_crg2b_large.py'
INPUTS=c.BASE+'LargeInputs.json'

def path(segment,role='current',index=1):
 return c.BASE+'large-'+segment+('' if segment=='event' else '-'+role+(f'-{index}' if segment=='step' else ''))+'.json.xz'

def prepared(which):
 d=c.read(b.BASE+'larger-graph-examples/C_RG2b.json');v=d[which]
 graph=mechanical.GRC9V4PortGraph.from_envelope(v['graph'])
 profile=mechanical.GRCV4Profile.from_canonical_bytes(mechanical.canonical_json_bytes(v['profile']))
 spec=d['specialization'];specialization=r.r.native.GRC9V4Specialization(b.FrozenJSONMap(spec['resolved']),b.FrozenJSONMap(spec['identity_payload']))
 roles={role:mechanical.authority(x,len(graph.edges)) for role,x in v['roles'].items()}
 seed=mechanical.make_state(graph,profile,specialization,roles,'C_RG2b')
 return replace(seed,inputs=r.configure(seed.inputs))

def manifest():
 m=c.check_manifest(c.read(c.INPUTS))
 return b.seal(dict(schema='p9-crg2b-large-inputs-v1',parent_digest=m['record_digest'],
  source_bindings=b.bind(c.paths()|{SELF,c.INPUTS,b.HERE+'prepare_p983_all_realizations.py'}),
  scope=dict(prepared_source_steps=2,prepared_target_steps=2,events=1,target_steps=20,final_reads=2,
    cap_seconds=3600,user_accepted=False,uniform_trajectory_enclosure=False),
  numerical_policy='certified_arb_256',section_policy=r.native_completion.APPROXIMATION))

def checked():
 m=c.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings']);return m

def source():
 value=c.read(path('source','current'));b.check_digest(value)
 return replace(prepared('source'),inputs=replace(b.GeometryStageInputs.from_payload(value['execution']['poststate']),dt=0))

def case(seed):
 d=c.read(b.BASE+'larger-graph-examples/C_RG2b.json');m=c.read(c.INPUTS)
 cc=deepcopy(m['small_cases'][0]);cc.update(fixture_id='large-connected-C_RG2b',case_id='large-connected-C_RG2b')
 cc['request']=deepcopy(d['event_request']);return c.rebind(seed,cc)

def execute(segment,role='current',index=1):
 m=checked();name=path(segment,role,index)
 if (b.ROOT/name).exists():
  row=c.read(name);b.check_digest(row);b.require(row['manifest_digest']==m['record_digest'],'resume identity');return row
 start=time.monotonic()
 def expired(*_):raise TimeoutError('3600-second segment cap; no fallback')
 signal.signal(signal.SIGALRM,expired);signal.alarm(3600)
 try:
  with r.worker() as policy:
   if segment in ('source','prepared_target'):
    seed=prepared('source' if segment=='source' else 'target')
    before=replace(seed.inputs,current=getattr(seed.inputs,role),dt=b.DT)
    execution,after=r.perform_step(before)
    b.require(r.Q(execution['independent_bridge']['exact_real_next_resource_lower'])>0,'prepared positivity uncertified')
   elif segment=='event':
    seed=source();cc=case(seed);target=r.independent_target(dict(expected_source=seed.to_payload()),cc)
    # Exact represented charge is required in BOTH roles before numerical admission.
    for rr in r.ROLES:
     b.require(sum(map(r.exact,getattr(seed.inputs,rr).C))==sum(map(r.exact,getattr(target,rr).C)),'represented split charge mismatch')
    owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(cc['request']))
    b.require(outcome.committed,'large native event failed '+str(outcome.failure))
    r.check_event(seed,cc,event)
    execution=dict(source=seed.to_payload(),case=cc,event=event)
   else:
    event=c.read(path('event'));b.check_digest(event);state=r.state(event['execution']['event']['actual_target'])
    previous=event
    before=replace(state.inputs,current=getattr(state.inputs,role),dt=b.DT)
    if segment=='final' or index>1:
     previous=c.read(path('step',role,10 if segment=='final' else index-1));b.check_digest(previous)
     before=b.GeometryStageInputs.from_payload(previous['execution']['poststate'])
    if segment=='final':execution=dict(before=replace(before,dt=0).to_payload(),read=r.native_read(replace(before,dt=0)))
    else:
     execution,after=r.perform_step(before)
     b.require(r.Q(execution['independent_bridge']['exact_real_next_resource_lower'])>0,'large target positivity uncertified')
    execution.update(event_digest=event['record_digest'],predecessor_digest=previous['record_digest'])
  row=b.seal(dict(schema='p9-crg2b-large-segment-v1',manifest_digest=m['record_digest'],segment=segment,role=role,index=index,
   outcome='passed',elapsed_seconds=time.monotonic()-start,compute_policy=policy,execution=execution,
   user_accepted=False,aggregate_closed=False))
  c.save(name,row)
  print(segment,role,index,'PASS',round(row['elapsed_seconds'],1),flush=True)
  return row
 finally:signal.alarm(0)

def role_run(role):
 for i in range(1,11):execute('step',role,i)
 return execute('final',role)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','prepared','event','continue','segment'))
 p.add_argument('--segment',choices=('source','prepared_target','step','final'));p.add_argument('--role',choices=r.ROLES,default='current')
 p.add_argument('--index',type=int,default=1);a=p.parse_args()
 if a.action=='prepare':c.save(INPUTS,manifest())
 elif a.action=='prepared':
  with ProcessPoolExecutor(max_workers=4) as pool:
   pending=[pool.submit(execute,s,role) for s in ('source','prepared_target') for role in r.ROLES]
   for f in as_completed(pending):f.result()
 elif a.action=='event':execute('event')
 elif a.action=='continue':
  with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(role_run,r.ROLES))
 else:execute(a.segment,a.role,a.index)
