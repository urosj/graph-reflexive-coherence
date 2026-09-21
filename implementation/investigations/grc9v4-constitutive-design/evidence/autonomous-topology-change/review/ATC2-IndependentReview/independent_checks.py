#!/usr/bin/env python3
"""Independent ATC-2 checks. No production pygrc is imported.

Exact research functions are AST-extracted unchanged from the uploaded verifier.
The graph/reference/backend shims implement DATA SHAPES only; builder tests do
not establish native schema, reference, profile or numerical target admission.
A Node.js serializer independently computes ECMAScript content identities.
"""
from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json, math, random, struct
import subprocess, sys, types, zipfile
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

JS = r'''const rl=require('readline').createInterface({input:process.stdin});
function c(x){if(x===null||typeof x!=='object')return JSON.stringify(x);
if(Array.isArray(x))return '['+x.map(c).join(',')+']';
return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+c(x[k])).join(',')+'}';}
rl.on('line',l=>console.log(JSON.stringify(c(JSON.parse(l)))));'''
class Canonical:
    def __init__(self): self.p=subprocess.Popen(['node','-e',JS],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def __call__(self,x):
        self.p.stdin.write(json.dumps(x,allow_nan=False,ensure_ascii=True)+'\n'); self.p.stdin.flush()
        return json.loads(self.p.stdout.readline()).encode()
    def close(self):self.p.stdin.close(); self.p.wait(timeout=5)
CAN=None

def dh(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def cid(prefix,x):return prefix+':'+hashlib.sha256(CAN(x)).hexdigest()
PREFIX={'k4_identity_payload':'grcv4-k4-sha256','reference_hodge_identity_payload':'grcv4-hodge-sha256',
        'resolved_params':'grcv4-params-sha256','wctr_identity_payload':'grcv4-wctr-sha256'}
def payload_identity(kind,p):return cid(PREFIX[kind],p)
class FrozenJSONMap(dict):
    def to_dict(self):return copy.deepcopy(dict(self))
class Box:
    def __init__(self,p):self.p=copy.deepcopy(p)
    def to_payload(self):return copy.deepcopy(self.p)
    def __getattr__(self,k):return self.p[k]
class Profile:
    def __init__(self,p,i):self.params_resolved=Box(p);self.identity_payload=Box(i)
    @property
    def complete_profile_id(self):return cid('grcv4-profile-sha256',self.identity_payload.p)
    def to_payload(self):return dict(identity_payload=self.identity_payload.to_payload(),params_resolved=self.params_resolved.to_payload(),complete_profile_id=self.complete_profile_id)
def resolve_profile(p,i):return Profile(p,i)
@dataclass(frozen=True)
class Edge:
    edge_id:str;tail_node_id:object;head_node_id:object
    def to_payload(self):return dict(edge_id=self.edge_id,tail_node_id=self.tail_node_id,head_node_id=self.head_node_id)
@dataclass(frozen=True)
class Graph:
    live_node_ids:tuple;oriented_edges:tuple
    def __post_init__(self):
        assert len(set(self.live_node_ids))==len(self.live_node_ids)
        assert len(set(self.live_edge_ids))==len(self.live_edge_ids)
        assert all(e.tail_node_id in self.live_node_ids and e.head_node_id in self.live_node_ids for e in self.oriented_edges)
    @property
    def live_edge_ids(self):return tuple(e.edge_id for e in self.oriented_edges)
    @property
    def incidence(self):return tuple(tuple(int(e.tail_node_id==v)-int(e.head_node_id==v) for e in self.oriented_edges) for v in self.live_node_ids)
    def to_payload(self):return dict(schema_version='grcv4-serialized-graph-v1',live_node_ids=list(self.live_node_ids),oriented_edges=[e.to_payload() for e in self.oriented_edges])
    def node_index(self,v):return self.live_node_ids.index(v)
    @classmethod
    def from_payload(cls,p):return cls(tuple(p['live_node_ids']),tuple(Edge(**e) for e in p['oriented_edges']))
@dataclass
class Reference:
    graph:Graph;profile:Profile;context:dict;K4_base:tuple;edge_weights:FrozenJSONMap
    def to_payload(self):return dict(descriptor_version='grcv4-reference-geometry-v1',structural_coordinates_id='grcv4-vertex-star-dense-row-major-v1',graph=self.graph.to_payload(),profile=self.profile.to_payload(),context=self.context,K4_base=[list(r) for r in self.K4_base],reference_hodge=dict(schema_version='grcv4-reference-hodge-identity-v1',edge_weights=dict(self.edge_weights)))
    @classmethod
    def from_payload(cls,p):return cls(Graph.from_payload(p['graph']),Profile(p['profile']['params_resolved'],p['profile']['identity_payload']),p['context'],tuple(map(tuple,p['K4_base'])),FrozenJSONMap(p['reference_hodge']['edge_weights']))
@dataclass
class Backend:
    graph:Graph;dimension:int;positions:tuple;reference_weights:dict;regularization:float
    def to_payload(self):return dict(backend='grcv3_host_frame_reference_weighted_gradient_v1',graph=self.graph.to_payload(),dimension=self.dimension,positions=[list(r) for r in self.positions],reference_weights=dict(self.reference_weights),regularization=self.regularization,rounding='exact_binary64_input_normal_equations_then_binary64_gradient_v1')
    @property
    def identity(self):return cid('grcv4-a-descriptor-sha256',self.to_payload())
    @classmethod
    def from_payload(cls,p):return cls(Graph.from_payload(p['graph']),p['dimension'],tuple(map(tuple,p['positions'])),p['reference_weights'],p['regularization'])

def load_research(path):
    tree=ast.parse(path.read_text()); names={'canonical','digest','bounded','select','birth','merge','root_round','geometric_mean','dyadic','fresh','build'}
    keep=[ast.ImportFrom(module='__future__',names=[ast.alias('annotations')],level=0)]
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in node.targets):keep.append(node)
        if isinstance(node,ast.ClassDef) and node.name=='Uncertified':keep.append(node)
        if isinstance(node,ast.FunctionDef) and node.name in names:keep.append(node)
    module=ast.fix_missing_locations(ast.Module(body=keep,type_ignores=[]))
    env=dict(F=F,json=json,hashlib=hashlib,math=math,struct=struct,itertools=itertools,
             GRCV4Graph=Graph,GRCV4ReferenceGeometry=Reference,OrientedEdge=Edge,
             resolve_profile=resolve_profile,payload_identity=payload_identity)
    # Only these two constructor-import bindings are shims; no pygrc numerical
    # owner or lifecycle is loaded or imitated.
    a=types.ModuleType('pygrc.models.grc_v4_candidate_a');a.CandidateADifferentialReference=Backend
    s=types.ModuleType('pygrc.models.grc_v4_state');s.FrozenJSONMap=FrozenJSONMap
    sys.modules[a.__name__]=a;sys.modules[s.__name__]=s
    exec(compile(module,str(path),'exec'),env)
    return env

def mm(a,b):return [[sum((F(x)*F(y) for x,y in zip(r,c)),F()) for c in zip(*b)] for r in a]
def tr(a):return list(map(list,zip(*a)))
def apply_T(flat,n,c):return [float(sum((F(flat[i*n+j])*F(c[j]) for j in range(n)),F())) or 0. for i in range(len(flat)//n)]
def norm2(z):return sum((F(v)**2 for r in z for v in r),F())
def selection_oracle(rows,gap):
    if not rows:return {'outcome':'no_event','locus':None,'scores':[]}
    winners=[l for l,s in rows if all(s>t+gap for m,t in rows if m!=l)]
    return {'outcome':'resolved' if len(winners)==1 else 'unresolved','locus':list(winners[0]) if len(winners)==1 else None,'scores':[dict(locus=list(l),score=str(s)) for l,s in rows]}
def birth_oracle(g,h,pol):
    b=g.incidence;k=mm(mm(b,h),tr(b));rows=[]
    for i,j in itertools.combinations(range(len(b)),2):
        a,v=g.live_node_ids[i],g.live_node_ids[j]
        if any({e.tail_node_id,e.head_node_id}=={a,v} for e in g.oriented_edges):continue
        if k[i][i]<=0 or k[j][j]<=0:return 'uncertified'
        s=k[i][j]**2/k[i][i]/k[j][j]
        if not 0<=s<=1:return 'uncertified'
        if s>F(pol['birth_threshold']):rows.append(((a,v),s))
    return selection_oracle(rows,F(pol['birth_gap']))
def merge_oracle(g,c,j,pol):
    f=[-x[0] for x in mm(g.incidence,[[v] for v in j])];rows=[]
    for a,b in itertools.combinations(range(len(c)),2):
        pair=(g.live_node_ids[a],g.live_node_ids[b])
        if not any({e.tail_node_id,e.head_node_id}==set(pair) for e in g.oriented_edges):continue
        ac=(F(c[a])-F(c[b]))**2/(2*F(pol['merge_epsilon_C'])**2)
        af=(f[a]-f[b])**2/(2*F(pol['merge_epsilon_f'])**2)
        if ac<=1 and af<=1:rows.append((pair,1/(1+ac+af)))
    return selection_oracle(rows,F(pol['merge_gap']))

def main(root,out):
    global CAN
    CAN=Canonical(); result={'schema':'independent_atc2_review_checks_v1','native_pygrc_executed':False,'groups':{},'limitations':['Exact source research functions executed by AST extraction; data-only shims replace graph/reference/backend constructors.','No native solver, initializer, whole-profile admission, lifecycle, automatic dispatcher or forensic graph reconstruction executed.','This compact input set retains only the research verifier among the 169 imported Python source subjects; production modules are not imported.','Content identities checked without executing native schema validators; complete snapshots and initializer-pair preimages are not retained in the ATC2 record.']}
    p=json.loads((root/'ATC2CandidateClosureProposal.json').read_text());r=json.loads((root/'ATC2PressureResults.json').read_text());env=load_research(root/'verify_atc2_candidates.py'); pol=env['POLICY'];Uncert=env['Uncertified']
    G=result['groups']
    for d in (p,r):assert dh({k:v for k,v in d.items() if k!='record_digest'})==d['record_digest']
    assert p['policy']==r['policy']==pol and p['policy_digest']==r['policy_digest']==dh(pol)
    assert p['pressure_run']['record_digest']==r['record_digest'] and p['pressure_run']['source_commit']==r['source_commit']
    files={}
    for f in root.iterdir():
        if f.is_file():files.setdefault(hashlib.sha256(f.read_bytes()).hexdigest(),[]).append(f.name)
    bindings=[dict(path=b['path'],sha256=b['sha256'],matches=files.get(b['sha256'],[])) for b in r['source_bindings']]
    own=next(b for b in r['source_bindings'] if b['path'].endswith('/verify_atc2_candidates.py'))
    assert own['sha256']==hashlib.sha256((root/'verify_atc2_candidates.py').read_bytes()).hexdigest()
    for b in p['source_bindings']:
        local=root/Path(b['path']).name
        if Path(b['path']).name in ('ATC2CandidateClosureProposal.md','ATC2PressureResults.json','verify_atc2_candidates.py'):
            assert hashlib.sha256(local.read_bytes()).hexdigest()==b['sha256'],b['path']
    G['record_bindings']=dict(status='pass',record_digests=2,policy_digest=True,execution_source_count=len(bindings),byte_matched_execution_sources=sum(bool(b['matches']) for b in bindings),source_commit=r['source_commit'])
    (out/'source_inventory.json').write_text(json.dumps(bindings,indent=2)+'\n')
    if (root/'proposal_index.json').exists():idx=json.loads((root/'proposal_index.json').read_text())
    else:
        with zipfile.ZipFile(root/'ATC-Draft8-CompanionBundle.zip') as z:idx=json.loads(z.read('ATC-Draft8/proposal_index.json'))
    if (root/'proposal_index.json').exists(): index_bytes=(root/'proposal_index.json').read_bytes()
    else:
        with zipfile.ZipFile(root/'ATC-Draft8-CompanionBundle.zip') as z:index_bytes=z.read('ATC-Draft8/proposal_index.json')
    assert hashlib.sha256(index_bytes).hexdigest()==next(b['sha256'] for b in p['source_bindings'] if b['path'].endswith('/proposal_index.json'))
    # Inspect origin schema; stable IDs and debt lists must match exactly.
    claim_by={x['id']:x for x in idx['claims']}; debt_by={x['id']:x for x in idx['debts']}
    edges=0
    for c in p['claims']:
        orig=claim_by[c['origin_claim_id']]
        expected=[e['debt_id'] for e in orig['debt_edges']]
        assert c['origin_debt_ids']==expected
        assert c['status']=='proposed_not_admitted' and c['accepted_descendants']==[]
        for did in expected:
            assert c['origin_claim_id'] in [e['claim_id'] for e in debt_by[did]['claim_edges']]
        edges+=len(expected)
    assert len(claim_by)==len(p['claims'])==35 and len(debt_by)==len(p['debts'])==28 and edges==165
    assert all(d['origin_debt_id'] in debt_by and not d['discharged'] and d['status']=='open' for d in p['debts'])
    G['claim_debt_origins']=dict(status='pass',claims=35,debts=28,edges=edges)
    traces=[]
    for q in p['forensic_queries']:
        d=q['result']; pre={k:v for k,v in d.items() if k!='trace_digest'}
        matched=dh(pre)==d['trace_digest']
        traces.append(dict(operation=q['operation'],query=q['query'],recomputed=matched))
    G['forensic_trace_self_consistency']=dict(status='pass' if all(x['recomputed'] for x in traces) else 'recipe_requires_inspection',traces=traces,reconstructed_graph=False)
    # Record-level independent identity checks.
    receipt_count=profile_count=authority_count=commit_count=0
    def profiles(obj):
        nonlocal profile_count
        if isinstance(obj,dict):
            if set(('identity_payload','params_resolved','complete_profile_id'))<=obj.keys():
                assert cid('grcv4-params-sha256',obj['params_resolved'])==obj['identity_payload']['params_hash']
                assert cid('grcv4-profile-sha256',obj['identity_payload'])==obj['complete_profile_id'];profile_count+=1
            for v in obj.values():profiles(v)
        elif isinstance(obj,list):
            for v in obj:profiles(v)
    profiles(r['evidence'])
    def receipts(obj):
        nonlocal receipt_count
        if isinstance(obj,dict):
            if obj.get('schema_version')=='grcv4-successful-receipt-envelope-v1':
                assert cid('grc-receipt-sha256',obj['identity_payload'])==obj['receipt_id'];receipt_count+=1
            for v in obj.values():receipts(v)
        elif isinstance(obj,list):
            for v in obj:receipts(v)
    receipts(r['evidence'])
    summaries=[]
    for case in r['evidence']['native_supplied_event_cases']:
        g=Graph.from_payload(case['source']['reference']['graph']);w=case['postordinary_witness'];c=case['postordinary_current']['C'];law=case['law']
        decision=env['birth'](g,w['H']) if law=='birth' else env['merge'](g,c,w['J'])
        oracle=birth_oracle(g,w['H'],pol) if law=='birth' else merge_oracle(g,c,w['J'],pol)
        assert decision==oracle==case['decision']
        assert case['initial_decision']['outcome']=='resolved'
        mat=case['request']['resource_transform']['row_major_coefficients'];n=len(c);nt=len(mat)//n
        for j in range(n):assert sum(F(mat[i*n+j]) for i in range(nt))==1
        for name,old,new in [('current',case['postordinary_current'],case['target_current']['authoritative']),('reset',case['postordinary_reset'],case['target_reset']['authoritative'])]:
            assert apply_T(mat,n,old['C'])==new['C']
            if old['Z_4'] is not None:assert new['Z_4']==[0.]*len(new['Z_4'])
        core=case['event_receipts'][0]['identity_payload']['core']
        for key in ('ordinary_receipts','event_receipts','identity_history_control_receipts'):
            group=case[key];cc=group[0]['identity_payload']['core']
            payload=dict(schema_version='grcv4-commit-payload-v1',operation_id=cc['operation_id'],
                source_state_digest=cc['source_state_digest'],target_state_digest=cc['target_state_digest'],
                emitted_receipt_ids=[rr['receipt_id'] for rr in group],
                target_step_index=case['target_current']['step_index'],target_time=case['target_current']['time'])
            assert all(rr['commit_id']==cid('grc-commit-sha256',payload) for rr in group)
            assert all(rr['identity_payload']['core']==cc for rr in group)
            commit_count+=1
        assert cid('grcv4-state-sha256',case['target_current'])==core['target_state_digest']
        assert cid('grcv4-reset-sha256',case['target_reset'])==core['target_reset_digest']
        for role,state in [('source',case['postordinary_current']),('target',case['target_current']['authoritative'])]:
            assert cid('grcv4-authoritative-sha256',dict(schema_version='grcv4-authoritative-state-identity-v1',authoritative=state))==core[role+'_authoritative_digest'];authority_count+=1
        assert core['parent_receipt_ids']==[case['ordinary_receipts'][0]['receipt_id']]
        assert case['target_current']['step_index']==case['source']['step_index']+1
        assert case['target_current']['time']==case['source']['time']+case['source']['dt']
        assert case['postordinary_witness']!=case['identity_history_control_witness']
        ref=Reference.from_payload(case['source']['reference']);be=Backend.from_payload(case['backend']) if case['backend'] else None
        outref,outbe,outmat,lineage=env['build'](ref,be,law,tuple(decision['locus']))
        assert CAN(outref.to_payload())==CAN(case['target'])
        assert list(outmat)==mat and json.loads(json.dumps(lineage))==case['lineage']
        assert (outbe is None and case['target_backend'] is None) or CAN(outbe.to_payload())==CAN(case['target_backend'])
        summary=dict(candidate=case['candidate'],law=law,profile=case['source']['reference']['profile']['identity_payload']['profile_family_id'],selected_score=float(F(decision['scores'][0]['score'])),all_retained_inputs_outputs_consistent=True)
        if law=='merge':
            oldf=[-v[0] for v in mm(g.incidence,[[v] for v in w['J']])]
            newg=Graph.from_payload(case['target']['graph']);newf=[-v[0] for v in mm(newg.incidence,[[v] for v in case['target_witness']['J']])]
            grouped=mm([mat[i*n:(i+1)*n] for i in range(nt)],[[v] for v in oldf])
            mismatch=[newf[i]-grouped[i][0] for i in range(nt)]
            summary.update(grouped_source_f=[float(v[0]) for v in grouped],target_f=list(map(float,newf)),resource_vector_field_mismatch=list(map(float,mismatch)))
        else:
            summary['identity_history_control_decision']=env['birth'](g,case['identity_history_control_witness']['H'])
        summaries.append(summary)
    G['retained_event_reconstruction']=dict(status='pass',cases=3,profile_occurrences=profile_count,receipt_ids=receipt_count,commit_ids=commit_count,authority_ids=authority_count,full_target_data_reconstructed=3,native_owners_rerun=False,summaries=summaries)
    # Independent execution of the source-stated A reference-pass equations on
    # the retained alpha=beta=0 subfamily; not the production initializer owner.
    initializer_rows=[]
    for case in r['evidence']['native_supplied_event_cases']:
        if case['candidate']!='A':continue
        for control in (False,True):
            refp=case['source']['reference'] if control else case['target']
            g=Graph.from_payload(refp['graph']);pa=refp['profile']['params_resolved']['candidate']
            assert pa['alpha']==pa['beta']==0
            for role in ('current','reset'):
                endpoint=case['identity_history_control_'+role] if control else case['target_'+role]['authoritative']
                C=endpoint['C'];m=len(g.live_edge_ids);B=g.incidence
                wb=[max(pa['W_floor'],1.)]*m
                dC=[x[0] for x in mm(tr(B),[[x] for x in C])]
                phi=[float(F(pa['kappa_c'])*sum((F(B[i][e])*F(wb[e])*dC[e] for e in range(m)),F())) for i in range(len(C))]
                mobility=[float(F(pa['eta'])*F(w)) for w in wb]
                jr=[float(-F(mobility[e])*sum((F(B[i][e])*F(phi[i]) for i in range(len(C))),F())) for e in range(m)]
                expected=[max(pa['W_floor'],math.exp(float(-F(pa['gamma'])*F(jj)**2/2))) for jj in jr]
                assert expected==endpoint['W_A']
                initializer_rows.append(dict(control=control,role=role,J_ref=jr,W=expected))
    G['independent_A_initializer_formula']=dict(status='pass',role_cases=len(initializer_rows),scope='source-stated reference pass, alpha=beta=0 only; system math.exp, no new correctly-rounded transcendental claim',cases=initializer_rows)
    # Ten reads: retained projections actually equal, but J variant not archived separately.
    for i,row in enumerate(r['evidence']['ten_product_reads']):
        dis=next(d for d in p['profile_dispositions'] if d['family']==row['family'])
        assert dis['read_evidence_pointer']=='/evidence/ten_product_reads/'+str(i)
        assert dis['read_profile_id']==row['source']['reference']['profile']['complete_profile_id']
        a,b=row['source'],row['variant']; assert a['reference']==b['reference'] and a['current']==b['current']
        assert a['reset']!=b['reset']
    G['ten_read_record_scope']=dict(status='pass',products=10,reset_C_changed=10,charge_target_changed=9,reset_W_or_Z_varied=0,native_equality_is_submission_reported=True)
    # Exact score oracle and full edge-reordering covariance on independent data.
    rng=random.Random(27092026); score_cases=0;cov_cases=0
    for trial in range(50):
        n=3+trial%4;nodes=tuple('v'+str(i) for i in range(n));m=n+trial%3
        edges=tuple(Edge('e'+str(i),nodes[rng.randrange(n)],nodes[rng.randrange(n)]) for i in range(m))
        g=Graph(nodes,edges)
        A=[[F(rng.randint(-4,4),8) for j in range(m)] for i in range(m)]
        h=mm(A,tr(A));h=[[float(h[i][j]+int(i==j)) for j in range(m)] for i in range(m)]
        c=[float(F(rng.randint(0,12),8)) for i in range(n)];j=[float(F(rng.randint(-10,10),4)) for i in range(m)]
        expected=birth_oracle(g,h,pol)
        if expected=='uncertified':
            try:env['birth'](g,h);raise AssertionError('expected undefined')
            except Uncert:pass
        else:assert env['birth'](g,h)==expected
        merged=merge_oracle(g,c,j,pol);assert env['merge'](g,c,j)==merged;score_cases+=2
        for rep in range(3):
            vp=list(range(n));ep=list(range(m));rng.shuffle(vp);rng.shuffle(ep);sg=[rng.choice((-1,1)) for _ in range(m)]
            gg=Graph(tuple(nodes[i] for i in vp),tuple(Edge(edges[k].edge_id,edges[k].tail_node_id if s==1 else edges[k].head_node_id,edges[k].head_node_id if s==1 else edges[k].tail_node_id) for k,s in zip(ep,sg)))
            hh=[[sg[a]*sg[b]*h[ep[a]][ep[b]] for b in range(m)] for a in range(m)]
            cc=[c[k] for k in vp];jj=[s*j[k] for k,s in zip(ep,sg)]
            def normalized(d):return d['outcome'],frozenset(d['locus'] or ()),{frozenset(x['locus']):x['score'] for x in d['scores']}
            assert normalized(env['merge'](gg,cc,jj))==normalized(merged)
            if expected!='uncertified':assert normalized(env['birth'](gg,hh))==normalized(expected)
            else:
                try:env['birth'](gg,hh);raise AssertionError('expected undefined')
                except Uncert:pass
            cov_cases+=1
    G['exact_score_oracle_and_covariance']=dict(status='pass',oracle_cases=score_cases,permutation_orientation_edge_order_controls=cov_cases,scope='synthetic admitted-shape dyadic operators; not native profile admission')
    # Strict score guards and dominance; at, below, above declared thresholds.
    g=Graph(('a','b','c'),(Edge('e','a','b'),Edge('f','b','c')));x=2.**-25
    scores=[]
    for v in (math.nextafter(x,0.),x,math.nextafter(x,math.inf)):
        d=env['birth'](g,((1.,v),(v,1.)));scores.append(d['outcome'])
    assert scores==['no_event','no_event','resolved']
    gap=F(pol['merge_gap']);delta=F(1,2**80);rank=[]
    for diff in (gap-delta,gap,gap+delta):
        d=env['select']([(('a','b'),F(1)),(('b','c'),1-diff)],gap);rank.append(d['outcome'])
    assert rank==['unresolved','unresolved','resolved']
    d=env['merge'](g,(1.,1.125,1.5),(0.,0.));assert len(d['scores'])==2 and d['locus']==['a','b']
    G['strict_guards']=dict(status='pass',birth_near_threshold_outcomes=scores,dominance_near_gap_outcomes=rank,two_eligible_unequal_merge=d)
    # High-range random geometric-mean checks against adjacent exact rounding intervals.
    gmcount=0
    fixed=[[2.**-1074,2.**1022],[float.fromhex('0x1.fffffffffffffp1023')]*3,[2.**-1074]*3,[1.,4.],[.5,2.,8.]]
    for _ in range(100):
        n=rng.randint(1,9);fixed.append([struct.unpack('>d',struct.pack('>Q',rng.randrange(1,0x7ff0000000000000)))[0] for k in range(n)])
    for values in fixed:
        v=env['geometric_mean'](values);prod=math.prod(F(a) for a in values);n=len(values)
        prev=math.nextafter(v,0.);nxt=math.nextafter(v,math.inf)
        lower=((F(prev)+F(v))/2)**n
        assert prod>=lower
        if math.isfinite(nxt):assert prod<=((F(v)+F(nxt))/2)**n
        assert env['geometric_mean'](list(reversed(values)))==v;gmcount+=1
    lo=1.;hi=math.nextafter(lo,math.inf)
    assert env['root_round'](((F(lo)+F(hi))/2)**2,2)==lo
    lo=hi;hi=math.nextafter(lo,math.inf)
    assert env['root_round'](((F(lo)+F(hi))/2)**2,2)==hi
    G['geometric_mean_rounding']=dict(status='pass',exact_adjacent_interval_cases=gmcount,midpoint_tie_parities=2,includes_min_subnormal_and_max_finite=True)
    dyads=0
    for bits in (1,2,4,16,31,52):
        N=2**bits
        for _ in range(100):
            a,b=F(rng.randrange(10000),2**rng.randrange(20)),F(rng.randrange(10000),2**rng.randrange(20))
            s,t=env['dyadic'](a,b,bits);u,v=env['dyadic'](b,a,bits)
            assert F(s)+F(t)==1 and (s,t)==(v,u)
            assert abs(F(s)-(a/(a+b) if a+b else F(1,2)))<=F(1,2*N);dyads+=1
    tiny=F(2.**-1074)
    assert F(1/3)+F(2/3)==1-F(1,2**54)
    assert float(tiny/2)==0. and float(tiny/2+tiny/2)==float(tiny)
    G['dyadic_allocation']=dict(status='pass',cases=dyads,complementarity_exact=True,rounding_error_bound=True,thirds_exact_sum=str(F(1/3)+F(2/3)),subnormal_counterexample=True)
    # Extended conditional constructors: all half-edge partitions; merge loops/parallel; ID collisions.
    source=copy.deepcopy(r['evidence']['native_supplied_event_cases'][0]['source']['reference'])
    graph=Graph(('a','v','b','atc2:child:0','atc2:child:1'),(Edge('p','v','a'),Edge('q','v','b'),Edge('parallel','v','b'),Edge('loop','v','v'),Edge('atc2:edge:0','a','b')))
    ref=Reference.from_payload(source);ref.graph=graph
    weights={e.edge_id:float(k+1) for k,e in enumerate(graph.oriented_edges)};ref.edge_weights=FrozenJSONMap(weights)
    # Nontrivial signed star-supported K4; masking tested, not native positive geometry.
    ref.K4_base=tuple(tuple(float(F((-1)**(i+j),8)) if i!=j and {e.tail_node_id,e.head_node_id}&{f.tail_node_id,f.head_node_id} else float(i==j) for j,f in enumerate(graph.oriented_edges)) for i,e in enumerate(graph.oriented_edges))
    be=Backend(graph,2,tuple((float(i),float(2*i)) for i in range(len(graph.live_node_ids))),weights,1.)
    halves=[(e.edge_id,role) for e in graph.oriented_edges for role,node in (('tail',e.tail_node_id),('head',e.head_node_id)) if node=='v']
    splitcount=0;currents=(1.,2.,3.,4.,5.)
    for mask in range(1,2**len(halves)-1):
        group=tuple(h for i,h in enumerate(halves) if mask>>i&1)
        target,backend,mat,lineage=env['build'](ref,be,'split',('v',group),currents)
        n=len(graph.live_node_ids);nt=len(target.graph.live_node_ids)
        assert nt==n+1 and len(target.graph.live_edge_ids)==len(graph.live_edge_ids)+1
        assert set(graph.live_edge_ids)<set(target.graph.live_edge_ids)
        assert all(sum(F(mat[i*n+j]) for i in range(nt))==1 for j in range(n))
        assert norm2(target.K4_base)<=norm2(ref.K4_base)
        assert all(v not in graph.live_node_ids for v in lineage['children'])
        assert all(v not in graph.live_edge_ids for v in lineage['new_edges'])
        for child in lineage['children']:assert backend.positions[target.graph.node_index(child)]==be.positions[graph.node_index('v')]
        other,obe,omat,olin=env['build'](ref,be,'split',('v',tuple(h for h in halves if h not in group)),currents)
        assert tuple(lineage['shares'])==tuple(reversed(olin['shares']))
        swap=dict(zip(lineage['children'],reversed(olin['children'])))
        for left,right in zip(target.graph.oriented_edges,other.graph.oriented_edges):
            endpoints=(swap.get(left.tail_node_id,left.tail_node_id),swap.get(left.head_node_id,left.head_node_id))
            wanted=(right.tail_node_id,right.head_node_id)
            assert endpoints==(tuple(reversed(wanted)) if left.edge_id in lineage['new_edges'] else wanted)
        splitcount+=1
    merged,bm,mat,lineage=env['build'](ref,be,'merge',('v','b'))
    assert set(lineage['dropped_edges'])=={'q','parallel','loop'}
    assert set(merged.graph.live_edge_ids)=={'p','atc2:edge:0'}
    assert bm.positions[-1]==(1.5,3.)
    G['conditional_constructor_pressure']=dict(status='pass',all_nontrivial_halfedge_partitions=splitcount,loop_and_parallel_merge_drop_control=True,name_collisions=True,nonzero_K4_mask=True,admission_scope='data-shape constructors only')
    # A root/tolerance caveat is already retained; show more exact consequences, not failures.
    # Disconnected-component birth impossibility under block-diagonal H.
    gg=Graph(('a','b','c','d'),(Edge('ab','a','b'),Edge('cd','c','d')))
    assert env['birth'](gg,((2.,0.),(0.,3.)))['outcome']=='no_event'
    G['birth_structural_limits']=dict(status='pass',disconnected_block_hodge_no_birth=True,identity_history_control_can_remove_guard=True,scope='conditional algebra; does not ban profiles with admitted cross-component H')
    # Bound changes must not make a selected target trigger another law.
    limited=Graph(tuple(range(16)),(Edge('a',0,1),Edge('b',1,2)))
    try:env['birth'](Graph(tuple(range(17)),limited.oriented_edges),((1.,0.),(0.,1.)));raise AssertionError('bound')
    except Uncert:pass
    G['scope_and_bounds']=dict(status='pass',source_graph_bound_reject=True,all_ATC_support_flags_false=all(not d['ATC_supported'] for d in p['profile_dispositions']),native_trigger_onset_not_claimed=not p['pressure_run']['native_trigger_onset_demonstrated'])
    CAN.close();result['status']='passed';result['group_count']=len(G)
    (out/'pressure_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2));print('groups',[(k,v['status']) for k,v in G.items()])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    main(args.input,args.output)
