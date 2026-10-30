"""Mechanism controls from retained native operands; no trajectory rerun."""
import argparse
from dataclasses import replace
import p9_crg2b_campaign as c
r,b=c.r,c.b
SELF=b.HERE+'p9_crg2b_science.py'
RESULT=c.BASE+'8.6-mechanisms.json'

def controls(before,read):
 r.check_read(before,read)
 certificate,_,_=r.data(before);bound={k:r.Q(v) for k,v in certificate['bounds'].items()}
 section=r.Q(read['error_upper']);jh=bound['A_H']/(r.proof.DT*r.Q(certificate['incidence_norm']))
 with r.ctx.workprec(192):
  truth=r.equations(before,read['H']);rows={}
  for key in ('geometry','feedback','modulation'):
   other=r.equations(before,read['H'],**{key:False})
   delta=truth['J']-other['J'];lower=max(max(r.Q(0),r.oracle.lower(abs(v))) for v in delta.entries())
   fixed=max(r.mag(r.ball(v)-truth['J'][i,0]) for i,v in enumerate(read['J']))
   rows[key]=dict(exact_fixed_H_effect_lower=str(lower),native_fixed_H_error_upper=str(fixed),
    fixed_H_effect_resolved=lower>2*fixed,
    infinite_section_effect_resolved=lower>2*(fixed+jh*section),
    section_current_error_upper=str(jh*section))
  image=truth['image'];different=r.norm(r.mat(read['H'])-image)
 work=read['chain']['work'];xs,hs=r.oracle.decode(work)
 chain=read['independent_certificate']['section'];error=r.Q(chain['first_inverse_state_error_upper'])
 zeros=[dict(index=i,upper=str(r.exact(xs[1][i])+error),negative=r.exact(xs[1][i])+error<0) for i,v in enumerate(before.current.C) if v==0]
 return dict(mechanisms=rows,section_vs_instantaneous_image_norm=str(different),
  signed_zero_query_predecessors=zeros,section_is_not_a_CI_root=True)

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
    first=value['roles'][role]['steps'][0];last=value['roles'][role]['steps'][-1]
    for label,step in (('first',first),('last',last)):
     before=b.GeometryStageInputs.from_payload(step['prestate'])
     out.append(dict(subject=f'D{degree}/{role}/{label}',**controls(before,step['read'])))
 b.require(all(all(v['fixed_H_effect_resolved'] for v in row['mechanisms'].values()) for row in out),'unresolved defining fixed-H mechanism')
 value=b.seal(dict(schema='p9-crg2b-mechanisms-v1',family='C_RG2b',source_bindings=b.bind(refs),cases=out,
  numerical_rerun=False,native_trajectory_rerun=False,uniform_parameter_tube=False,user_accepted=False,aggregate_closed=False))
 c.save(RESULT,value);print('8.6 mechanisms',len(out),'PASS',flush=True)
 return value

if __name__=='__main__':run()
