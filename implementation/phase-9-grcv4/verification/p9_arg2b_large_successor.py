"""Second-beat large event, preserving the first-beat exclusion and evidence."""
import argparse,signal,time
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
import p9_arg2b_large as old
c,r,b=old.c,old.r,old.b
SELF=b.HERE+'p9_arg2b_large_successor.py'
INPUTS=c.BASE+'LargeSecondBeatInputs.json'

def path(segment,role='current',index=1):
 return c.BASE+'large-second-'+segment+('' if segment in ('event','source') else '-'+role+(f'-{index}' if segment=='step' else ''))+'.json.xz'

def prepare():
 v=c.read(old.path('source','current'));b.check_digest(v)
 raw=v['execution']['poststate_full'];x=raw['current']['C'];g=raw['reference']['graph'];ids=g['live_node_ids'];rows=[[],[],[]]
 for edge in g['edges']:
  for here,there in ((edge['tail'],edge['head']),(edge['head'],edge['tail'])):
   if here['node_id']==0:rows[(here['port']-1)//3].append(r.exact(x[ids.index(there['node_id'])])-r.exact(x[ids.index(0)]))
 gradients=[sum(row,r.Q(0))/len(row) for row in rows]
 b.require(gradients==[0,0,0],'first-beat exclusion changed')
 return b.seal(dict(schema='p9-arg2b-second-beat-inputs-v1',source_bindings=b.bind(c.paths()|{SELF,old.SELF,old.INPUTS,old.path('source','current')}),
  predecessor_digest=v['record_digest'],first_beat_exclusion=dict(row_gradients=[0,0,0],strict_hessian_condition=False,event_committed=False),
  selection='next ordinary source beat; unchanged law, parameters, timestep, trigger and resource shares',
  scope=dict(extra_source_steps=1,events=1,target_steps=20,final_reads=2,cap_seconds=3600),user_accepted=False,aggregate_closed=False))

def checked():
 m=c.read(INPUTS);b.check_digest(m);b.check_bindings(m['source_bindings']);return m

def source():
 v=c.read(path('source'));b.check_digest(v)
 return replace(old.prepared('source'),inputs=replace(b.GeometryStageInputs.from_payload(v['execution']['poststate_full']),dt=0))

def execute(segment,role='current',index=1):
 m=checked();name=path(segment,role,index)
 if (b.ROOT/name).exists():
  row=c.read(name);b.check_digest(row);b.require(row['manifest_digest']==m['record_digest'],'resume identity');return row
 def expired(*_):raise TimeoutError('3600-second cap; no fallback')
 signal.signal(signal.SIGALRM,expired);signal.alarm(3600);start=time.monotonic()
 try:
  with r.worker() as policy:
   if segment=='source':
    before=replace(old.source().inputs,dt=b.DT);execution,after=r.perform_step(before)
    b.require(r.Q(execution['independent_bridge']['exact_real_next_resource_lower'])>0,'source positivity')
   elif segment=='event':
    seed=source();cc=old.case(seed);target=r.independent_target(dict(expected_source=seed.to_payload()),cc)
    for rr in r.ROLES:
     b.require(sum(map(r.exact,getattr(seed.inputs,rr).C))==sum(map(r.exact,getattr(target,rr).C)),'represented split charge mismatch')
    owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(cc['request']))
    b.require(outcome.committed,'second-beat native event failed '+str(outcome.failure));r.check_event(seed,cc,event)
    execution=dict(source=seed.to_payload(),case=cc,event=event)
   else:
    event=c.read(path('event'));b.check_digest(event);state=r.state(event['execution']['event']['actual_target'])
    previous=event;before=replace(state.inputs,current=getattr(state.inputs,role),dt=b.DT)
    if segment=='final' or index>1:
     previous=c.read(path('step',role,10 if segment=='final' else index-1));b.check_digest(previous)
     before=b.GeometryStageInputs.from_payload(previous['execution']['poststate_full'])
    if segment=='final':execution=dict(before=replace(before,dt=0).to_payload(),read=r.native_read(replace(before,dt=0)))
    else:
     execution,after=r.perform_step(before)
     b.require(r.Q(execution['independent_bridge']['exact_real_next_resource_lower'])>0,'target positivity uncertified')
    execution.update(event_digest=event['record_digest'],predecessor_digest=previous['record_digest'])
  row=b.seal(dict(schema='p9-arg2b-large-segment-v1',manifest_digest=m['record_digest'],segment=segment,role=role,index=index,
   outcome='passed',elapsed_seconds=time.monotonic()-start,compute_policy=policy,execution=execution,user_accepted=False,aggregate_closed=False))
  c.save(name,row);print(segment,role,index,'PASS',round(row['elapsed_seconds'],1),flush=True);return row
 finally:signal.alarm(0)

def role_run(role):
 for i in range(1,11):execute('step',role,i)
 return execute('final',role)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','source','event','continue','final'));a=p.parse_args()
 if a.action=='prepare':c.save(INPUTS,prepare())
 elif a.action=='continue':
  with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(role_run,r.ROLES))
 elif a.action=='final':
  with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(execute,['final','final'],r.ROLES))
 else:execute(a.action)
