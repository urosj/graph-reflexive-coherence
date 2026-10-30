"""A_RG2b mechanisms at saved operands, with explicit unresolved margins."""
from dataclasses import replace
import p9_arg2b_campaign as c
r,b=c.r,c.b
SELF=b.HERE+'p9_arg2b_science.py'
RESULT=c.BASE+'8.6-mechanisms.json'

def controls(before,read):
 r.check_read(before,read);gb,_=r.proof.global_bounds();section=r.Q(read['error_upper'])
 with r.ctx.workprec(192):
  truth=r.equations(before,read['H']);m=len(before.current.W_A)
  no_history=replace(before,current=replace(before.current,W_A=(1.,)*m))
  alternatives={'geometry':r.equations(before,np_eye(m))['J'],'readback':truth['baseline'],
    'history':r.equations(no_history,read['H'])['J']}
  # Remove only gamma's J0^2 term from the constitutive read; keep C/W/H.
  gamma=[]
  _,data=r.data(before);rows,ends=data[3:];cc=before.current.C;ww=before.current.W_A
  rr=[[sum((r.ball(ww[k])*(r.ball(cc[v])-r.ball(cc[u])) for k,v in row),r.ball(0))/sum((r.ball(ww[k]) for k,_ in row),r.ball(0)) if row else r.ball(0) for row in node] for u,node in enumerate(rows)]
  for k,(u,v) in enumerate(ends):
   g=(-(r.ball(cc[u])+r.ball(cc[v])+sum((r.oracle.square(a-z) for a,z in zip(rr[u],rr[v])),r.ball(0)))/2**25).exp()
   q=(r.ball(ww[k])-g)/(r.ball(ww[k])+g);gamma.append([truth['baseline'][k,0]/(1-q/32)])
  alternatives['current_constitutive_term']=r.oracle.arb_mat(gamma)
  fixed=max(r.mag(r.ball(v)-truth['J'][i,0]) for i,v in enumerate(read['J']));out={}
  for key,other in alternatives.items():
   lower=max(max(r.Q(0),r.oracle.lower(abs(v))) for v in (truth['J']-other).entries())
   out[key]=dict(exact_fixed_H_effect_lower=str(lower),native_fixed_H_error_upper=str(fixed),
    fixed_H_effect_resolved=lower>2*fixed,infinite_section_effect_resolved=lower>2*(fixed+gb['J_H']*section),
    section_current_error_upper=str(gb['J_H']*section))
  difference=r.norm(r.mat(read['H'])-truth['image'])
 return dict(mechanisms=out,section_vs_instantaneous_image_norm=str(difference),section_is_not_a_CI_root=True,
  unresolved_effect_is_not_numerical_conformance_failure=True)

def np_eye(m):return [[float(i==j) for j in range(m)] for i in range(m)]

def run():
 m=c.check_manifest(c.read(c.INPUTS));out=[];refs={SELF,c.INPUTS}
 with r.worker():
  for role,key in (('current','read'),('reset','reset_read')):
   before=b.GeometryStageInputs.from_payload(m['initial_inputs'])
   if role=='reset':before=replace(before,current=before.reset)
   out.append(dict(subject='source/'+role,**controls(before,m['source_step'][key])))
  for degree in (59,66,73,94):
   cc=next(x for x in m['deep_cases'] if x['request']['target_effective_degree']==degree)
   name=c.BASE+'deep-'+cc['fixture_id']+'.json.xz';refs.add(name);value=c.read(name)['execution']
   for role in r.ROLES:
    for label,step in (('first',value['roles'][role]['steps'][0]),('last',value['roles'][role]['steps'][-1])):
     before=b.GeometryStageInputs.from_payload(step['prestate']);out.append(dict(subject=f'D{degree}/{role}/{label}',**controls(before,step['read'])))
 value=b.seal(dict(schema='p9-arg2b-mechanisms-v1',family='A_RG2b',source_bindings=b.bind(refs),cases=out,
  native_trajectory_rerun=False,uniform_parameter_tube=False,user_accepted=False,aggregate_closed=False))
 c.save(RESULT,value);print('8.6 mechanism subjects',len(out),flush=True);return value

if __name__=='__main__':run()
