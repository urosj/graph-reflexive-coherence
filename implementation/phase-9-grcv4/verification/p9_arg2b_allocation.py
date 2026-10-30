"""D94 exact-charge allocation screen, preserving the original exclusion."""
from fractions import Fraction
from itertools import permutations
from copy import deepcopy
import p9_arg2b_campaign as c
r,b=c.r,c.b
SELF=b.HERE+'p9_arg2b_allocation.py'
RESULT=c.BASE+'D94Allocation.json'

def derive():
 m=c.read(c.INPUTS);seed=r.state(m['source']);original=next(v for v in m['deep_cases'] if v['request']['target_effective_degree']==94)
 initial=b.GeometryStageInputs.from_payload(m['initial_inputs'])
 initial=r.replace(initial,**{role:r.replace(getattr(initial,role),W_A=(1025/1024,)*len(initial.current.W_A)) for role in r.ROLES})
 with r.worker():source_step,after=r.perform_step(initial)
 seed=r.replace(seed,inputs=r.replace(after,dt=0));original=c.rebind(seed,original)
 n=seed.inputs.geometry.reference.graph.live_node_ids.index(original['request']['source_node_id'])
 cs=[Fraction(getattr(seed.inputs,k).C[n]) for k in r.ROLES];old=original['request']['resource_distribution']
 candidates=[]
 for da in range(-8,9):
  for db in range(-8,9):
   a=Fraction(old[0])+Fraction(da,2**20);z=Fraction(old[1])+Fraction(db,2**20)
   x=(a,z,1-a-z)
   if all(v>0 for v in x) and all(sum(Fraction(float(q*v)) for v in x)==q for q in cs):candidates.append(x)
 candidates.sort(key=lambda x:(sum(abs(v-Fraction(w)) for v,w in zip(x,old)),x))
 failures=[];chosen=None
 with r.worker():
  for index,shares in enumerate(candidates):
   if index%100==0:print('allocation candidate',index,'of',len(candidates),flush=True)
   trial=deepcopy(original);trial['request']['resource_distribution']=list(map(float,shares));trial=c.rebind(seed,trial)
   target=r.independent_target(dict(expected_source=seed.to_payload()),trial)
   try:pred={role:c.preflight(r.replace(target,current=getattr(target,role)),10) for role in r.ROLES}
   except ValueError as exc:
    failures.append(dict(shares=list(map(str,shares)),reason=str(exc)));continue
   chosen=shares;break
 b.require(chosen is not None,'no exact-charge positive companion')
 replacements=[]
 for oldcase in m['deep_cases']:
  if oldcase['request']['target_effective_degree']!=94:continue
  # Carry branch-role allocation equivariantly from the first declared layout.
  oldshares=oldcase['request']['resource_distribution'];shares=[float(chosen[old.index(v)]) for v in oldshares]
  trial=deepcopy(oldcase);trial['request']['resource_distribution']=shares
  replacements.append(c.rebind(seed,trial))
 out=b.seal(dict(schema='p9-arg2b-d94-allocation-v1',parent_digest=m['record_digest'],source_bindings=b.bind({SELF,c.SELF,r.SELF,c.INPUTS}),
  original_exclusion='original D94 shares change represented charge; no denominator-64 allocation passed the original below-one history ten-step screen',
  selection='nearest declared 2^-20 simplex neighborhood satisfying exact charge in both roles and ten-step independent joint screening',
  initial_inputs=initial.to_payload(),source_step=source_step,source=seed.to_payload(),allocation_neighborhood=dict(denominator=2**20,offsets=list(range(-8,9))),enumeration_count=len(candidates),unsuccessful_screens=failures,selected=list(map(str,chosen)),cases=replacements,
  parameters_changed=False,tolerances_changed=False,native_success_inferred=False,user_accepted=False))
 c.save(RESULT,out);print('selected',out['selected'],'screens',len(failures)+1,flush=True)

if __name__=='__main__':derive()
