"""Source-history companion derived from the mapped zero-vertex baseline sign.

Only source history changes; old boundary W transports identically, new bonds
retain the unit seed. Full section certificates follow the baseline derivation.
"""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import hashlib,json,lzma,math
from flint import fmpq as Q,fmpq_mat
import p9_arg2b_completion as p
import p9_arg2b_section as s

SELF=p.BASE+'verification/p9_arg2b_companion.py'
DECLARATION=p.BASE+'tranche-8/P9-ARG2b-HistoryCompanion.json'
RESULT=p.BASE+'tranche-8/P9-ARG2b-CompanionSections.json.xz'
HISTORY=Q(1025,1024)


def declaration():
 d=p.read(p.INPUTS[2]);source_ids={e['edge_id'] for e in d['source']['graph']['edges']}
 g=d['target']['graph'];bi,gram,_,_=p.graphs.graph_algebra(g)
 old=[e['edge_id'] in source_ids for e in g['edges']];rows=[]
 # Formal baseline polynomial evaluations, not physical zero-W evaluations.
 for role in ('current','reset'):
  c=d['target']['roles'][role]['C'];cc=fmpq_mat([[s.exact(v)] for v in c]);dc=bi.transpose()*cc
  values=[]
  for t in (Q(0),Q(1),Q(2)):
   w=[t if flag else Q(1) for flag in old];phi=fmpq_mat([[ww*dc[k,0]] for k,ww in enumerate(w)])
   drive=gram*phi;j0=fmpq_mat([[-ww*drive[k,0]] for k,ww in enumerate(w)])
   values.append(-p.DT*bi*j0)
  zero=[i for i,v in enumerate(c) if v==0]
  coefficients={}
  for i in zero:
   a=(values[2][i,0]-2*values[1][i,0]+values[0][i,0])/2
   b=values[1][i,0]-values[0][i,0]-a;z=values[0][i,0]
   coefficients[g['live_node_ids'][i]]=[str(v) for v in (z,b,a)]
  rows.append(dict(role=role,reference_hodge_baseline_zero_vertex_polynomials=coefficients))
 # 512 log(1+1/1024) < 1/2 < 5/8, by log(1+x)<x.
 return p.seal(dict(schema='p9-arg2b-history-companion-v1',source_history_uniform=str(HISTORY),
  derived_history_interval='1 < W < exp((5/8)/512)',scaled_log_upper='1/2',
  rationale='positive side of the exact zero-extra baseline root W=1; dyadic W with strict ordinary-history margin',
  target_rule='transport unchanged source W on old edges; seed new edges with one',
  unchanged=['source_C_current','source_C_reset','topology','specialization','resource_shares','dt','coefficients','tolerances'],
  baseline_derivation=rows,baseline_is_not_full_section_certificate=True,
  source_bindings=[dict(path=n,sha256=hashlib.sha256((p.ROOT/n).read_bytes()).hexdigest()) for n in (SELF,p.INPUTS[2],s.SELF,p.RESULT)],
  native_events=0,native_steps=0,user_accepted=False,aggregate_closed=False))


def subjects():
 d=p.read(p.INPUTS[2]);old={e['edge_id'] for e in d['source']['graph']['edges']};out=[]
 for g,r,graph,c,w,cert in s.subjects():
  changed=[float(HISTORY) if e['edge_id'] in old else 1. for e in graph['edges']]
  out.append((g,r,graph,c,changed,cert))
 return out


def main():
 decl=declaration();path=p.ROOT/DECLARATION;p.require(not path.exists(),'companion already declared')
 path.write_text(json.dumps(decl,indent=2)+'\n')
 with ProcessPoolExecutor(max_workers=4) as pool:rows=list(pool.map(s.worker,subjects()))
 result=p.seal(dict(schema='p9-arg2b-companion-sections-v1',declaration_digest=decl['record_digest'],
  source_bindings=s.bindings()+[dict(path=DECLARATION,sha256=hashlib.sha256(path.read_bytes()).hexdigest())],
  cases=rows,native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False))
 with lzma.open(p.ROOT/RESULT,'wt',preset=6) as f:json.dump(result,f,separators=(',',':'))
 print(json.dumps([dict(graph=v['graph'],role=v['role'],positive=v['certificate']['exact_real_first_step_positive'],
  history_admitted=v['certificate']['next_history_inside_K_minus'],section_pass=v['certificate']['section_tolerance_passes'],
  minimum=float(Q(v['certificate']['exact_real_next_resource_lower'])),
  seconds=v['proposal_seconds']+v['certification_seconds']) for v in rows],indent=2))

if __name__=='__main__':main()
