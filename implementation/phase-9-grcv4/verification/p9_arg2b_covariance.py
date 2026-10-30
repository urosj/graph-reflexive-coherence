"""Small A_RG2b covariance: all signed/order and full-chart obligations."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from dataclasses import replace
import numpy as np
import p9_arg2b_campaign as c
import p984e_aci as order_a
r,b=c.r,c.b
SELF=b.HERE+'p9_arg2b_covariance.py'
INPUTS=c.BASE+'CovarianceInputs.json'
POLICY=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13)

def prepare():
 old=c.read(c.INPUTS);comp=c.read(c.BASE+'D94Allocation.json');seed=r.state(comp['source'])
 small=[c.rebind(seed,cc) for cc in old['small_cases']]
 for ch in (1,-1):
  cc=deepcopy(next(v for v in small if v['request']['target_effective_degree']==45 and v['request']['module_chirality']==ch))
  cc.update(fixture_id=f'P984F-D52-E{ch}-P1',case_id=f'P984F-D52-E{ch}-P1::A_RG2b')
  cc['request'].update(target_effective_degree=52,growth_phase=1,resource_distribution=[float(r.Q(v)) for v in comp['selected']]);small.append(c.rebind(seed,cc))
 deep=[c.rebind(seed,cc) for cc in old['deep_cases']]
 for i,cc in enumerate(deep):
  if cc['request']['target_effective_degree']==94:deep[i]=next(v for v in comp['cases'] if v['fixture_id']==cc['fixture_id'])
 return b.seal(dict(schema='p9-arg2b-covariance-inputs-v1',family='A_RG2b',initial_inputs=comp['initial_inputs'],source_step=comp['source_step'],
  source=seed.to_payload(),small_cases=small,deep_cases=deep,source_bindings=b.bind(c.paths()|{SELF,c.INPUTS,c.BASE+'D94Allocation.json'}),
  user_accepted=False,aggregate_closed=False))

def path(checkpoint,kind):return c.BASE+'covariance-'+checkpoint+'-'+kind+'.json.xz'
def algebra(d):return c.chart if 'ports' in d else order_a

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
   growth_phase=None if request['growth_phase'] is None else d['branches'][str(request['growth_phase'])]);node='source-s'
 else:node=order_a.labels(d)[0]['source-s']
 request.update(source_node_id=node,source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
  target_profile_template_id=c.arg2b_profile_template(ref).profile_template_id,operation_id='arg2b-cov-'+case['fixture_id']+'-'+d['kind'])
 request['history_policy']=r.r.history_policy(seed)
 identity=deepcopy(case['oracle']['event_identity'])
 for key in identity:
  if key in request and key!='schema_version':identity[key]=request[key]
 for channel in ('candidate','carrier'):
  key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
 eid='grc-event-sha256:'+b.digest(identity)
 graph=algebra(d).transported_graph(case['oracle']['target_graph'],d,case['oracle']['event_id'],eid)
 cc['oracle']=dict(event_identity=identity,event_id=eid,target_graph=graph);return cc

def execute(job):
 m,checkpoint,d=job;refs=b.bind({SELF,INPUTS,order_a.SELF,c.chart.SELF,c.ordering.SELF})
 with r.worker():
  before=b.GeometryStageInputs.from_payload(transform(m['initial_inputs'],d))
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
  maximum=max(maximum,b.comparison(z[key],expected,POLICY,'connected_arg2b_'+key)['maximum_error'])
 return maximum

def state_pair(a,z,mapping):
 ni,ei,_=mapping;maximum=0.
 for role in r.ROLES:
  b.require(a[role]['Z_4'] is z[role]['Z_4'] is None,'invented RG carrier')
  maximum=max(maximum,b.comparison(z[role]['C'],np.asarray(a[role]['C'])[ni],POLICY,'resource')['maximum_error'])
  maximum=max(maximum,b.comparison(z[role]['W_A'],np.asarray(a[role]['W_A'])[ei],POLICY,'unsigned_history')['maximum_error'])
 return maximum

def image(value,graph,mapping):
 ni,ei,signs=mapping;before=b.GeometryStageInputs.from_payload(value);ref=deepcopy(value['reference']);ref['graph']=graph
 ref['K4_base']=(np.asarray(ref['K4_base'])[np.ix_(ei,ei)]*np.outer(signs,signs)).tolist()
 ref['reference_hodge']['edge_weights']={e['edge_id']:list(value['reference']['reference_hodge']['edge_weights'].values())[i] for e,i in zip(graph['edges'],ei,strict=True)}
 r.reidentify(ref);reference=b.GRCV4ReferenceGeometry.from_payload(ref)
 h=(np.asarray(value['H1_form'])[np.ix_(ei,ei)]*np.outer(signs,signs)).tolist()
 roles={role:b.GRCV4AuthoritativeState(tuple(value[role]['C'][i] for i in ni),tuple(value[role]['W_A'][i] for i in ei),None) for role in r.ROLES}
 return replace(before,geometry=b.GRCV4Geometry(reference,b.OneFormHodge(reference.graph,tuple(map(tuple,h)))),**roles)

def transform(value,d):
 original=value['reference']['graph'];graph=deepcopy(original)
 if 'ports' in d:graph=c.chart.transported_graph(original,d)
 else:
  nodes,edges=order_a.labels(d);old=graph['edges'];graph['live_node_ids']=[nodes[graph['live_node_ids'][i]] for i in d['node_order']];graph['edges']=[]
  for i in d['edge_order']:
   e=deepcopy(old[i]);e['edge_id']=edges[e['edge_id']]
   for end in ('tail','head'):e[end]['node_id']=nodes[e[end]['node_id']]
   if d['signs'][i]<0:e['tail'],e['head']=e['head'],e['tail']
   graph['edges'].append(e)
 return image(value,graph,algebra(d).mapping(original,graph,d)).to_payload()

def check(m,checkpoint):
 transforms=(c.ordering if checkpoint=='e' else c.chart).declarations();values=[c.read(path(checkpoint,d['kind'])) for d in transforms]
 base=values[0];maximum=0.
 for d,row in zip(transforms,values,strict=True):
  b.check_digest(row);b.check_bindings(row['source_bindings']);b.require(row['manifest_digest']==m['record_digest'] and row['transform']==d,'covariance subject')
  before=b.GeometryStageInputs.from_payload(transform(m['initial_inputs'],d))
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
     maximum=max(maximum,state_pair(av['poststate_full'],zv['poststate_full'],ix))
     for key in ('read','reset_read','restart'):maximum=max(maximum,pair(av[key],zv[key],ix))
    maximum=max(maximum,pair(reference['roles'][role]['final'],actual['roles'][role]['final'],ix))
 return dict(checkpoint=checkpoint,events=sum(len(v['cases']) for v in values),target_steps=4*sum(len(v['cases']) for v in values),
  required_history_cells=2*len(cases(m,checkpoint))*(len(transforms)-1),maximum_covariance_error=maximum,user_accepted=False)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','run','check'));p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 if a.action=='prepare':c.save(INPUTS,prepare());raise SystemExit(0)
 m=c.check_manifest(c.read(INPUTS))
 if a.action=='run':
  jobs=[(m,k,d) for k in ('e','f') for d in (c.ordering if k=='e' else c.chart).declarations() if not (b.ROOT/path(k,d['kind'])).exists()]
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(execute,j) for j in jobs]):f.result()
 for k in ('e','f'):print(check(m,k))
