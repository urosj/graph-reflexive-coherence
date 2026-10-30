"""Large mechanism discrimination on retained operands, not another trajectory."""
from concurrent.futures import ProcessPoolExecutor
import p9_arg2b_large_successor as n
import p9_arg2b_science as science
c,r,b=n.c,n.r,n.b
SELF=b.HERE+'p9_arg2b_large_science.py'
RESULT=c.BASE+'8.6-large-mechanisms.json'

def case(task):
 role,index=task;name=n.path('step',role,index);record=c.read(name);b.check_digest(record)
 v=record['execution']
 with r.worker():
  before=b.GeometryStageInputs.from_payload(v['prestate']);out=science.controls(before,v['read'])
 return dict(subject=role+'/'+str(index),path=name,record_digest=record['record_digest'],**out)

def run():
 jobs=[(role,i) for role in r.ROLES for i in (1,10)]
 refs=b.bind({SELF,science.SELF,n.INPUTS,*[n.path('step',*job) for job in jobs]})
 with ProcessPoolExecutor(max_workers=4) as pool:cases=list(pool.map(case,jobs))
 b.check_bindings(refs)
 value=b.seal(dict(schema='p9-arg2b-large-mechanisms-v1',cases=cases,source_bindings=refs,
  native_trajectory_rerun=False,uniform_parameter_tube=False,user_accepted=False,aggregate_closed=False))
 c.save(RESULT,value);print('four large first/final mechanism subjects PASS',flush=True);return value

if __name__=='__main__':run()
