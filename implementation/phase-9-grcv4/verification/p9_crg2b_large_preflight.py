"""Independent second-beat target screen, explicitly without native credit."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import p9_crg2b_large_successor as n
c,r,b=n.c,n.r,n.b
SELF=b.HERE+'p9_crg2b_large_preflight.py'
RESULT=c.BASE+'LargeSecondBeatPreflight.json'

def screen(role):
 with r.worker():
  seed=n.source();case=n.old.case(seed);before=r.independent_target(dict(expected_source=seed.to_payload()),case)
  rows=c.preflight(replace(before,current=getattr(before,role)),10)
 return dict(role=role,steps=rows)

def run():
 refs=b.bind({SELF,n.INPUTS,n.path('source'),c.SELF,r.SELF,r.oracle.SELF})
 with ProcessPoolExecutor(max_workers=2) as pool:rows=list(pool.map(screen,r.ROLES))
 b.check_bindings(refs);value=b.seal(dict(schema='p9-crg2b-large-screen-v1',source_bindings=refs,roles=rows,
  native_steps=0,native_events=0,positivity_certified=False,selection_changed=False,user_accepted=False,aggregate_closed=False))
 c.save(RESULT,value);print('ten-step target screen PASS for both histories; native/rounding certification still required',flush=True)

if __name__=='__main__':run()
