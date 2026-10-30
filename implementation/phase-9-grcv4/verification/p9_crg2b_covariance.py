"""Small C_RG2b covariance: all signed/order and full-chart obligations."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from dataclasses import replace
import numpy as np
import p9_crg2b_campaign as c
r,b=c.r,c.b
SELF=b.HERE+'p9_crg2b_covariance.py'
POLICY=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13)

def path(checkpoint,kind):return c.BASE+'covariance-'+checkpoint+'-'+kind+'.json.xz'
def algebra(d):return c.chart if 'ports' in d else c.ordering

def cases(m,checkpoint):
 if checkpoint=='e':return [next(cc for cc in m['small_cases'] if cc['request']['target_effective_degree']==52 and cc['request']['growth_phase']==1 and cc['request']['module_chirality']==1),
  next(cc for cc in m['deep_cases'] if cc['request']['target_effective_degree']==94 and cc['request']['growth_phase']==3 and cc['request']['module_chirality']==-1)]
 return [next(cc for cc in m['small_cases'] if cc['request']['target_effective_degree']==degree and cc['request']['module_chirality']==chirality
  and cc['request']['growth_phase']==(None if degree==45 else 1)) for degree in (45,52) for chirality in (1,-1)]

def expected_case(seed,case,d):
 cc=deepcopy(case);request=cc['request'];ref=seed.inputs.geometry.reference
 if 'ports' in d:
  shares=[0.]*3
  for i,x in enumerate(request['resource_distribution'],1):shares[d['branches'][str(i)]-1]=x
  request.update(resource_distribution=shares,module_chirality=request['module_chirality']*d['chirality_factor'],
   growth_phase=None if request['growth_phase'] is None else d['branches'][str(request['growth_phase'])]);node='s'
 else:node=c.ordering.labels(d)[0]['s']
 request.update(source_node_id=node,source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
  target_profile_template_id=c.crg2b_profile_template(ref).profile_template_id,operation_id='crg2b-cov-'+case['fixture_id']+'-'+d['kind'])
 identity=deepcopy(case['oracle']['event_identity'])
 for key in identity:
  if key in request and key!='schema_version':identity[key]=request[key]
 eid='grc-event-sha256:'+b.digest(identity)
 graph=algebra(d).transported_graph(case['oracle']['target_graph'],d,case['oracle']['event_id'],eid)
 cc['oracle']=dict(event_identity=identity,event_id=eid,target_graph=graph);return cc

def execute(job):
 m,checkpoint,d=job;refs=b.bind({SELF,c.INPUTS})
 with r.worker():
  before=b.GeometryStageInputs.from_payload(algebra(d).transform(m['initial_inputs'],d))
  source,after=r.perform_step(before);seed=replace(r.state(m['source']),inputs=replace(after,dt=0))
  rows=[c.run_case(seed,expected_case(seed,cc,d),2) for cc in cases(m,checkpoint)]
 value=b.seal(dict(manifest_digest=m['record_digest'],source_bindings=refs,checkpoint=checkpoint,transform=d,
  source_step=source,source=seed.to_payload(),cases=rows,user_accepted=False))
 c.save(path(checkpoint,d['kind']),value);print('covariance',checkpoint,d['kind'],'PASS',flush=True)
 return value

def pair(a,z,mapping):
 ni,ei,signs=mapping;maximum=0.
 for key in ('J','read_current','baseline','readback','flat','H','source'):
  av=np.asarray(a[key]);expected=av[np.ix_(ei,ei)]*np.outer(signs,signs) if av.ndim==2 else av[ei]*signs
  maximum=max(maximum,b.comparison(z[key],expected,POLICY,'connected_crg2b_'+key)['maximum_error'])
 return maximum

def state_pair(a,z,mapping):
 ni,_,_=mapping;maximum=0.
 for role in r.ROLES:
  b.require(a[role]['W_A'] is z[role]['W_A'] is a[role]['Z_4'] is z[role]['Z_4'] is None,'invented RG history')
  maximum=max(maximum,b.comparison(z[role]['C'],np.asarray(a[role]['C'])[ni],POLICY,'resource')['maximum_error'])
 return maximum

def check(m,checkpoint):
 transforms=(c.ordering if checkpoint=='e' else c.chart).declarations();values=[c.read(path(checkpoint,d['kind'])) for d in transforms]
 base=values[0];maximum=0.
 for d,row in zip(transforms,values,strict=True):
  b.check_digest(row);b.check_bindings(row['source_bindings']);b.require(row['manifest_digest']==m['record_digest'] and row['transform']==d,'covariance subject')
  before=b.GeometryStageInputs.from_payload(algebra(d).transform(m['initial_inputs'],d))
  after=r.check_step(before,row['source_step']);seed=replace(r.state(m['source']),inputs=replace(after,dt=0))
  b.require(seed.to_payload()==row['source'],'mapped source')
  ix=algebra(d).mapping(m['initial_inputs']['reference']['graph'],before.geometry.reference.graph.to_payload(),d)
  maximum=max(maximum,state_pair(base['source']['inputs'],row['source']['inputs'],ix))
  for key in ('reset_read','read','restart'):maximum=max(maximum,pair(base['source_step'][key],row['source_step'][key],ix))
  b.require(len(row['cases'])==len(cases(m,checkpoint)),'case roster')
  for original,reference,actual in zip(cases(m,checkpoint),base['cases'],row['cases'],strict=True):
   b.require(actual['case']==expected_case(seed,original,d),'mapped request/identity')
   c.check_case(seed,actual,2)
   ix=algebra(d).mapping(reference['event']['actual_target']['inputs']['reference']['graph'],actual['event']['actual_target']['inputs']['reference']['graph'],d,
    reference['case']['oracle']['event_id'],actual['case']['oracle']['event_id'])
   maximum=max(maximum,state_pair(reference['event']['actual_target']['inputs'],actual['event']['actual_target']['inputs'],ix))
   for role in r.ROLES:
    for av,zv in zip(reference['roles'][role]['steps'],actual['roles'][role]['steps'],strict=True):
     maximum=max(maximum,state_pair(av['poststate'],zv['poststate'],ix))
     for key in ('read','reset_read','restart'):maximum=max(maximum,pair(av[key],zv[key],ix))
    maximum=max(maximum,pair(reference['roles'][role]['final'],actual['roles'][role]['final'],ix))
 return dict(checkpoint=checkpoint,events=sum(len(v['cases']) for v in values),target_steps=4*sum(len(v['cases']) for v in values),
  required_history_cells=2*len(cases(m,checkpoint))*(len(transforms)-1),maximum_covariance_error=maximum,user_accepted=False)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('run','check'));p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 m=c.check_manifest(c.read(c.INPUTS))
 if a.action=='run':
  jobs=[(m,k,d) for k in ('e','f') for d in (c.ordering if k=='e' else c.chart).declarations() if not (b.ROOT/path(k,d['kind'])).exists()]
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(execute,j) for j in jobs]):f.result()
 for k in ('e','f'):print(check(m,k))
