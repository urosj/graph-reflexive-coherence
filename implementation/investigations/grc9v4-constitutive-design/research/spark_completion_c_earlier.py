"""Earlier C-family witnesses in exact anisotropic full-state domains.

The old laws/events and duration 32 are fixed. Rational resource parallelotopes
and, for PC, a positive-radius ball in every symmetric star carrier direction
are certified on their whole domains. No later trajectory proves invariance.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import hashlib,json,lzma,time
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_os_reference import COSReference
from spark_completion_ci import CCIReference
from spark_completion_pc import CPCReference
from spark_completion_ci_pc import CCIPCReference
from spark_completion_positive import full_jacobian,norm_upper,content_id
from spark_completion_ci_campaign import exact_bounds,box_payload
from spark_completion_continuation import need,infnorm,POLICY,spectral_domain
import spark_completion_basins as basins

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
BASE=INV+'evidence/spark-completion/'
EARLIER=BASE+'applicability/earlier-closure/'
FAMILIES=('C_OS','C_CI','C_PC','C_CI_PC')
PREFIX={'C_OS':'COS','C_CI':'CCI','C_PC':'CPC','C_CI_PC':'CCIPC'}
PRECISION=512
EXECUTION_PRECISION=8192
TIME_LIMIT=3600
PARAMETERS=dict(eta='1/1024',duration='32',kappa_Phi='1/64',tau_PC='32',
                source_charge='21',window_beats=2,OS_split_tolerance='1/100000000000')


def read_json(path):
    raw=(ROOT/path).read_bytes()
    return json.loads(lzma.decompress(raw) if path.endswith('.xz') else raw)


def sealed(value):
    v={k:x for k,x in value.items() if k!='record_digest'}
    return {**v,'record_digest':content_id(v)}


def need_seal(v):need(v.get('record_digest')==sealed(v)['record_digest'],'record digest')


def bound_sources(v):
    need_seal(v)
    for ref in v['sources']:
        need(hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256'],
             'scientific input or generator source drift: '+ref['path'])


def interval(pair):
    lo,hi=map(F,pair)
    need(0<=hi-lo<=F(1,2**110),'retained coordinate interval width')
    return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))


@lru_cache(maxsize=8)
def fixed_inverse(encoded):
    e=COSReference(json.loads(encoded),'rational')
    A=e.q(3,4)*e.I+e.Le;inverse=A.inv()
    need(A*inverse==e.I,'exact cached fixed-H inverse')
    return tuple(tuple(str(x) for x in row) for row in inverse.tolist())


class CachedCOS(COSReference):
    """Cache only exact immutable fixed-I algebra; the corrector stays live."""
    def __init__(self,graph):
        super().__init__(graph,'arb');self.precision=ctx.prec
        self.fixed_inverse=arb_mat([[fmpq(x) for x in row]
            for row in fixed_inverse(json.dumps(graph,sort_keys=True))])
        self.fixed_reads=0

    def read(self,C,H,eta=None):
        need(ctx.prec==self.precision,'cached model precision changed')
        if H is not self.I:return super().read(C,H,eta)
        eta=self.q(1) if eta is None else eta
        phi=self.q(1,64)*self.B*self.Bt*C-self.site(C)
        j0=-eta*self.Bt*phi;y=self.fixed_inverse*j0;self.fixed_reads+=1
        return dict(potential=phi,baseline=j0,current=j0+y/4,causal_flat=y/2)


def model(family,graph):
    need(family in FAMILIES,'unknown family')
    return {'C_OS':CachedCOS,'C_CI':CCIReference,'C_PC':CPCReference,
            'C_CI_PC':CCIPCReference}[family](graph)


def chart(declaration):
    need_seal(declaration)
    need(declaration['schema']=='spark-completion-c-earlier-domain-v1' and
         declaration['families']==list(FAMILIES) and declaration['parameters']==PARAMETERS and
         not declaration['accepted_authority'] and not declaration['native_completion'], 'declared domain scope')
    original=read_json(BASE+'SC2PositiveCandidate.json.xz')['checks']
    need(declaration['graphs']=={k:v['graph']for k,v in original['targets'].items()} and
         declaration['center']==original['trap']['center'] and
         declaration['complete_basins']==original['trap']['complete_basins'],
         'original graph, rational center or SC-1 roster changed')
    nodes=declaration['graphs']['1']['live_node_ids'];n=len(nodes);d=n-1
    need(n==15 and declaration['resource_dimension']==d,'resource directions')
    T=fmpq_mat([[fmpq(x) for x in row] for row in declaration['basis']])
    need(T.nrows()==T.ncols()==d,'full resource basis')
    radii=list(map(fmpq,declaration['axis_radii']))
    need(len(radii)==d and min(radii)>0,'positive resource radii')
    try:inverse=T.inv()
    except (ZeroDivisionError,ValueError) as error:raise ValueError('rank-deficient domain') from error
    E=fmpq_mat([[int(i==j) if i<d else -1 for j in range(d)]for i in range(n)])
    R=fmpq_mat([[int(i==j) for j in range(n)]for i in range(d)])
    diagonal=lambda xs:fmpq_mat([[xs[i] if i==j else 0 for j in range(d)]for i in range(d)])
    S=E*T*diagonal(radii);U=diagonal([1/x for x in radii])*inverse*R
    need(U*S==fmpq_mat([[int(i==j)for j in range(d)]for i in range(d)]),'exact domain inverse')
    need(all(sum(S[i,j]for i in range(n))==0 for j in range(d)),'exact charge tangent')
    center=declaration['center'];need(set(center)==set(nodes) and sum(fmpq(x)for x in center.values())==21,'center exact charge')
    z=fmpq(declaration['carrier_radius']);need(0<z<fmpq(1,128),'positive full carrier radius')
    return S,U,z


def geometry(graph,center,S):
    """Fixed-row predicates on a box, correlated edge support on the actual K."""
    nodes=graph['live_node_ids'];n=len(nodes);d=S.ncols();indices={x:i for i,x in enumerate(nodes)}
    radii={x:sum(abs(S[i,j])for j in range(d))for i,x in enumerate(nodes)}
    lo={x:F(str(fmpq(center[x])-radii[x]))for x in nodes};hi={x:F(str(fmpq(center[x])+radii[x]))for x in nodes}
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1))for e in graph['edges']]
    need(min(lo.values())>0 and max(hi.values())<4,'whole resource chart')
    rows=basins.row_intervals(nodes,edges,lo,hi);seeds={x for x in nodes if basins.seed_status(rows[x],POLICY)}
    adj=basins.neighbors(nodes,edges);comparisons={};down={x:set()for x in nodes};bounds=[]
    for e,(a,_,b,_,_) in zip(graph['edges'],edges):
        i,j=indices[a],indices[b];gap=fmpq(center[a])-fmpq(center[b]);r=sum(abs(S[i,k]-S[j,k])for k in range(d))
        need(abs(gap)>r,'domain crosses an edge-order hyperplane')
        comparisons[a,b]=(F(str(gap-r)),F(str(gap+r)));comparisons[b,a]=(-F(str(gap+r)),-F(str(gap-r)))
        down[a if gap<0 else b].add(b if gap<0 else a)
        bounds.append(dict(edge_id=e['edge_id'],orientation=1 if gap>0 else -1,
                           half_width=str(r),strict_margin=str(abs(gap)-r)))
    anchors=set()
    for x in seeds:
        if lo[x]>POLICY['core_resource'] and all(comparisons[x,y][0]>POLICY['contrast']for y in adj[x]):anchors.add(x)
        else:need(hi[x]<=POLICY['core_resource'] or any(comparisons[x,y][1]<=POLICY['contrast']for y in adj[x]),'unresolved anchor')
    destinations={}
    def visit(x):
        if x not in destinations:destinations[x]=set().union(*(visit(y)for y in down[x])) if down[x] else {x}
        return destinations[x]
    for x in nodes:visit(x)
    roster={a:sorted(x for x in nodes if destinations[x]=={a})for a in sorted(anchors)}
    roster={a:v for a,v in roster.items()if len(v)>1}
    return dict(complete_basins=roster,seeds=sorted(seeds),anchors=sorted(anchors),edges=bounds,
        minimum_edge_margin=str(min(fmpq(r['strict_margin'])for r in bounds)),
        coordinate_box_minimum_edge_margin=str(min(fmpq(center[a])-fmpq(center[b])-radii[a]-radii[b]
            if fmpq(center[a])>fmpq(center[b]) else fmpq(center[b])-fmpq(center[a])-radii[a]-radii[b]
            for a,_,b,_,_ in edges)),selector=spectral_domain(graph))


def state_step(family,m,C,Z=None):
    if family=='C_OS':return m.step(C,eta=m.q(1,1024),dt=m.q(32))['after'],None
    if family=='C_CI':return m.ci_step(C)['after'],None
    s=m.pc_step(C,Z) if family=='C_PC' else m.ccipc_step(C,Z)
    return s['after'],s['carrier_after']


def split_bound(m,C):
    """Correlated predictor/corrector difference, via exact resolvent identities.

    Bounding H_p and H_c separately loses their common quadratic source. Let
    D=H_p-I, y0=2 f_p. Then (M0+D Le)(y-y0)=dj-D Le y0 and
    f_c-f_p=(I+D)^-1((y-y0)/2-D f_p). Neumann bounds enclose these
    differences uniformly; the final Frobenius bound retains both factors.
    """
    fp=m.read(C,m.I,eta=m.q(1,1024))['causal_flat'];y0=2*fp
    D=m.matrix([[m.q(m.overlap[i][j],8)*fp[i,0]*fp[j,0]
                 for j in range(m.m)]for i in range(m.m)])
    inverse=m.fixed_inverse;alpha=infnorm(inverse*D*m.Le).upper();beta=infnorm(D).upper()
    need(alpha<1 and beta<1,'OS split Neumann premises')
    rhs=-m.q(1,1024*64)*m.Le*D*m.Bt*C-D*m.Le*y0
    dy=infnorm(inverse).upper()*infnorm(rhs).upper()/(1-alpha)
    df=(dy/2+infnorm(D*fp).upper())/(1-beta)
    coefficient=sum(m.q(m.overlap[i][j],8)**2
                    for i in range(m.m)for j in range(m.m)).sqrt()
    split=coefficient*(2*infnorm(fp).upper()*df+df**2)
    return split,dict(current_neumann=exact_bounds(alpha),hodge_neumann=exact_bounds(beta),
        flat_difference=exact_bounds(df),predictor_flat_norm=exact_bounds(infnorm(fp).upper()),
        norm='Frobenius',method='correlated_resolvent_difference')


def certificate(family,declaration):
    """Prove the whole domain; this interface takes no trajectory argument."""
    with ctx.workprec(PRECISION):
        S,U,zrad=chart(declaration);m=model(family,declaration['graphs']['1']);n=m.n;d=n-1
        C=m.vector(declaration['center']);rad=[sum(abs(S[i,j])for j in range(d))for i in range(n)]
        box=arb_mat([[arb(fmpq(declaration['center'][x]),rad[i])]for i,x in enumerate(m.nodes)])
        root_bound=None;Z=None;split=None;split_operands=None
        if family=='C_OS':
            J=full_jacobian(m,box);split,split_operands=split_bound(m,box)
            need(split<arb(fmpq(PARAMETERS['OS_split_tolerance'])),'whole-domain OS split tolerance')
        elif family=='C_CI':
            J,Ff=m.full_jacobian(box);root_bound=infnorm(Ff).upper()
            need(root_bound<m.root_q,'joint root derivative bound')
        else:
            Z=m.zero()
            for i,j in m.pairs:Z[i,j]=arb(0,zrad);Z[j,i]=Z[i,j]
            partial=m.partials(box,Z);J=partial['CC']
            if family=='C_CI_PC':
                root_bound=infnorm(partial['root_derivative']).upper()
                need(root_bound<m.root_q,'composite root derivative bound')
        transformed=arb_mat(U)*J*arb_mat(S)
        resource_rows=[sum(abs(transformed[i,j]).upper()for j in range(d))for i in range(d)]
        history_cross=[];history_resource=arb(0);history_self=arb(0);history_row=arb(0)
        if Z is not None:
            CZ=arb_mat(U)*partial['CZ'];SC=partial['SC']*arb_mat(S)
            history_cross=[arb(zrad)*norm_upper(arb_mat([[CZ[i,j]for j in range(CZ.ncols())]]))for i in range(d)]
            resource_rows=[r+b for r,b in zip(resource_rows,history_cross)]
            history_resource=(1-m.decay)*sum(norm_upper(arb_mat([[SC[i,j]]for i in range(SC.nrows())]))for j in range(d))/arb(zrad)
            history_self=m.decay+(1-m.decay)*norm_upper(partial['SZ'])
            history_row=history_resource+history_self
        q=max([r.upper()for r in resource_rows]+[history_row.upper()])
        after,Zafter=state_step(family,m,C,m.zero()if Z is not None else None)
        defect=max(abs(x).upper()for x in (arb_mat(U)*(after-C)).entries())
        if Zafter is not None:defect=max(defect,(norm_upper(Zafter)/arb(zrad)).upper())
        margin=1-q-defect;need(q<1 and margin>0,'strict full-state self-map and contraction')
        need(all(sum(J[i,j]for i in range(n)).contains(1)for j in range(n)),'resource derivative charge identity')
        geos={}
        for chi,graph in declaration['graphs'].items():
            other=COSReference(graph,'rational')
            need(other.nodes==m.nodes and other.edges==m.edges and other.overlap==m.overlap,'chiral equation identity')
            geos[chi]=geometry(graph,declaration['center'],S)
            need(geos[chi]['complete_basins']==declaration['complete_basins'],'whole-domain complete basins')
        carrier_dim=len(m.pairs)if Z is not None else 0
        proof=dict(family=family,ordinary_duration='32',resource_dimension=d,carrier_dimension=carrier_dim,
            full_dimension=d+carrier_dim,physical_state=['C','Z_4']if Z is not None else ['C'],
            domain_digest=declaration['record_digest'],contraction=exact_bounds(q),center_defect=exact_bounds(defect),
            strict_image_margin=exact_bounds(margin),resource_row_bounds=[exact_bounds(x)for x in resource_rows],
            carrier_to_resource=[exact_bounds(x)for x in history_cross],resource_to_carrier=exact_bounds(history_resource),
            carrier_self=exact_bounds(history_self),carrier_row=exact_bounds(history_row),
            carrier_pairs=[list(x)for x in m.pairs]if Z is not None else [],
            positive_resource_neighborhood_lower=str(1/max(sum(abs(U[i,j])for j in range(n))for i in range(d))),
            carrier_radius=str(zrad)if Z is not None else None,geometry=geos,
            full_writer_included=Z is not None,both_H_consumers=True,
            same_selected_source_for_geometry_and_writer=family=='C_CI_PC',
            joint_root_derivative=exact_bounds(root_bound)if root_bound is not None else None,
            OS_split_upper=exact_bounds(split)if split is not None else None,OS_split_operands=split_operands,
            precision_bits=PRECISION,
            trajectory_inputs_to_domain_checker=0,supporting_trajectory_steps_after_completion=0,
            accepted_authority=False,native_completion=False)
        return proof,dict(model=m,S=S,U=U,C=C,Cbox=box,Zbox=Z,zrad=zrad,derivative=transformed,
                          partials=partial if Z is not None else None)


def decode(m,row):
    need(set(row['C'])==set(m.nodes),'retained full C coordinates')
    C=arb_mat([[interval(row['C'][x])]for x in m.nodes]);Z=None
    if 'Z'in row:
        need(len(row['Z'])==len(m.pairs),'retained full carrier coordinates')
        Z=m.zero()
        for pair,(i,j)in zip(row['Z'],m.pairs):Z[i,j]=interval(pair);Z[j,i]=Z[i,j]
    return C,Z


def membership(m,C,Z,operands):
    delta=arb_mat(operands['U'])*(C-operands['C'])
    lower=max(abs(x).lower()for x in delta.entries());upper=max(abs(x).upper()for x in delta.entries())
    if Z is not None:
        zl=sum(abs(x).lower()**2 for x in Z.entries()).sqrt()/arb(operands['zrad'])
        zu=norm_upper(Z)/arb(operands['zrad']);lower=max(lower,zl.lower());upper=max(upper,zu.upper())
    return lower,upper


def select_prefix(family,role,rows,declaration,operands,*,origin):
    with ctx.workprec(PRECISION):
        m=operands['model'];entry=None;selected=[];checks=[]
        for step,row in enumerate(rows,1):
            need(row['step']==step,'continuous physical prefix')
            C,Z=decode(m,row);need((Z is not None)==(family in ('C_PC','C_CI_PC')),'physical history omitted')
            need(sum(C.entries()).contains(21),'prefix excludes conserved charge')
            lower,upper=membership(m,C,Z,operands)
            if entry is None and upper<1:entry=step
            elif entry is None:need(lower>1,'earlier membership unresolved')
            if entry is not None:need(upper<1,'positive window leaves domain')
            selected.append({k:row[k]for k in ('step','C','Z')if k in row})
            checks.append(dict(step=step,membership=[exact_bounds(lower)[0],exact_bounds(upper)[1]]))
            if entry is not None and step==entry+2:break
        need(entry is not None and selected[-1]['step']==entry+2,'no positive two-beat window')
        return sealed(dict(schema='spark-completion-c-earlier-prefix-v1',family=family,role=role,
            domain_digest=declaration['record_digest'],origin=origin,ordinary_duration='32',entry=entry,
            completion=entry+2,last_retained_step=entry+2,last_required_execution_step=entry+2,
            last_executed_step=origin.get('original_last_executed_step',entry+2),
            supporting_trajectory_steps_after_completion=0,
            observations=selected,membership_checks=checks,local_gain=int(role=='current'),
            additional_event_gain=0,reset_earns_live_gain=False,accepted_authority=False,native_completion=False))


def preflight_cos(declaration,role):
    """Verify exact-algebra cache and eight full-map comparisons before a run."""
    old=read_json(BASE+'SC2SourceBeat.json.xz')['checks']['prepared'];graph=declaration['graphs']['1']
    with ctx.workprec(EXECUTION_PRECISION):
        m=CachedCOS(graph);plain=COSReference(graph,'arb');C=m.vector(old['transferred_'+role])
        for _ in range(8):
            a=m.step(C,eta=m.q(1,1024),dt=m.q(32));b=plain.step(C,eta=plain.q(1,1024),dt=plain.q(32))
            for key in ('geometry','after','defect'):
                need(all(x.overlaps(y)for x,y in zip(a[key].entries(),b[key].entries())),'cached/original full map disagreement')
            C=a['after']
        need(m.fixed_reads==8,'fixed inverse cache inactive')
        return dict(role=role,target_steps=8,precision_bits=EXECUTION_PRECISION,
            cached_fixed_I_reads=m.fixed_reads,exact_inverse_identity=True,all_full_map_comparisons_overlap=True,
            graph_cache=fixed_inverse.cache_info()._asdict(),no_state_or_corrector_cache=True)


def fresh_cos_prefix(declaration,role,operands):
    """Execute only to certified entry + two beats; never follow a supporting tail."""
    start=time.monotonic();old=read_json(BASE+'SC2SourceBeat.json.xz');prepared=old['checks']['prepared']
    reference=old['checks']['actual_current_target']if role=='current'else read_json(BASE+'SC2PositiveCandidate.json.xz')['checks']['roles']['reset']
    with ctx.workprec(EXECUTION_PRECISION):
        m=CachedCOS(declaration['graphs']['1']);C=m.vector(prepared['transferred_'+role]);rows=[];entry=None;compared=[]
        worst_split=arb(0)
        for k in range(1,401):
            need(time.monotonic()-start<TIME_LIMIT,'one-hour physical-prefix cap')
            s=m.step(C,eta=m.q(1,1024),dt=m.q(32));C=s['after'];split=norm_upper(s['defect'])
            need(split<arb(fmpq(PARAMETERS['OS_split_tolerance'])) and min(C.entries())>0 and max(C.entries())<4,'physical OS admission')
            need(sum(C.entries()).contains(21),'physical charge invariant enclosure')
            row=dict(step=k,C=box_payload(m,C));rows.append(row);worst_split=max(worst_split,split)
            if str(k)in reference['checkpoints']:
                checkpoint=reference['checkpoints'][str(k)]
                for i,node in enumerate(m.nodes):need(C[i,0].overlaps(interval(checkpoint[node])),'accepted prefix checkpoint disagreement')
                compared.append(k)
            with ctx.workprec(PRECISION):
                observed,_=decode(operands['model'],row);_,upper=membership(operands['model'],observed,None,operands)
                if upper<1 and entry is None:entry=k
                if entry is not None:need(upper<1,'physical window leaves direct domain')
            if entry is not None and k==entry+2:break
        need(entry is not None and k==entry+2,'no short-prefix closure')
        need(m.fixed_reads==k,'cached predictor cadence')
    origin=dict(kind='fresh_original_law_prefix_with_exact_fixed_inverse_cache',
        source_record_digest=old['record_digest'],source_and_event_unchanged=True,physical_precision_bits=EXECUTION_PRECISION,
        original_checkpoint_overlaps=compared,cached_fixed_I_reads=m.fixed_reads,
        maximum_steps=400,time_limit_seconds=TIME_LIMIT,automatic_fallback=False,
        maximum_split=exact_bounds(worst_split),elapsed_seconds=time.monotonic()-start)
    return select_prefix('C_OS',role,rows,declaration,operands,origin=origin)


def original_runs():
    """Authenticate the admitted executions before extracting short prefixes."""
    paths={'C_OS':('spark-completion',BASE+'SC2Acceptance.json'),
           'C_CI':('spark-completion-applicability',BASE+'applicability/CCIScientificAcceptance.json'),
           'C_PC':('spark-completion-pc',BASE+'applicability/CPCScientificAcceptance.json'),
           'C_CI_PC':('spark-completion-ci-pc',BASE+'applicability/CCIPCScientificAcceptance.json')}
    runs={};refs={}
    for family,(directory,acceptance_path)in paths.items():
        authority_path=INV+'decisions/'+directory+'/Authority.json'
        authority=read_json(authority_path);acceptance=read_json(acceptance_path)
        need_seal(authority);need_seal(acceptance)
        ref=authority['acceptance'];need(ref['path']==acceptance_path and
            ref['record_digest']==acceptance['record_digest'] and
            hashlib.sha256((ROOT/acceptance_path).read_bytes()).hexdigest()==ref['sha256'],
            'accepted scientific predecessor')
        subjects={r['path']:r['sha256']for r in acceptance['subjects']}
        if family=='C_OS':
            witness_path=BASE+'SC2CompleteWitness.json';witness=read_json(witness_path);need_seal(witness)
            need(hashlib.sha256((ROOT/witness_path).read_bytes()).hexdigest()==subjects[witness_path] and
                 witness['record_digest']==acceptance['witness_record_digest'],'accepted OS witness')
            subjects.update({r['path']:r['sha256']for r in witness['sources']})
        names=[BASE+'SC2SourceBeat.json.xz',BASE+'SC2PositiveCandidate.json.xz',BASE+'SC2CompleteWitness.json']if family=='C_OS'else [BASE+'applicability/'+PREFIX[family]+'-'+role+'.json.xz'for role in ('current','reset')]
        for path in [authority_path,acceptance_path,*names]:
            raw=(ROOT/path).read_bytes();sha=hashlib.sha256(raw).hexdigest()
            refs[path]=dict(path=path,sha256=sha)
            if path not in names:continue
            need(subjects.get(path)==sha,'accepted execution bytes')
            value=read_json(path);need_seal(value)
            for source in value['sources']:
                need(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256'],'accepted producer/operand drift')
                refs[source['path']]=source
            if family!='C_OS':
                role=value['checks']['role']
                need(acceptance['execution_record_digests'][role]==value['record_digest'],'accepted execution identity')
                runs[family,role]=value
    return runs,[refs[p]for p in sorted(refs)]
