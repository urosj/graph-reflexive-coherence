"""Research A_RG2b C/Y inverse chains: binary64 proposal, fixed Arb192 proof.

No native admission, silent precision escalation or numerical fallback. The
physical writer consumes updated C, incoming W and the selected current.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib,json,lzma,math,time
from functools import lru_cache
import numpy as np
from flint import arb,arb_mat,ctx,fmpq as Q
import p9_arg2b_completion as proof
import p9_crg2b_section as common

ROOT,BASE=proof.ROOT,proof.BASE
SELF=BASE+'verification/p9_arg2b_section.py'
TEST=BASE+'verification/test_p9_arg2b_section.py'
RESULT=BASE+'tranche-8/P9-ARG2b-SectionFeasibility.json.xz'
DEPTH,SWEEPS,BITS=4,18,192
require=proof.require
exact,ball,lower,upper,magnitude,matrix,eye,norm=common.exact,common.ball,common.lower,common.upper,common.magnitude,common.matrix,common.eye,common.norm
encode,decode=common.encode,common.decode


def algebra(graph):
    b,d,mask,_=proof.graphs.graph_algebra(graph)
    nodes=graph['live_node_ids'];index={v:i for i,v in enumerate(nodes)}
    rows=[[[] for _ in range(3)] for _ in nodes];ends=[]
    for k,e in enumerate(graph['edges']):
        u,v=index[e['tail']['node_id']],index[e['head']['node_id']];ends.append((u,v))
        rows[u][(e['tail']['port']-1)//3].append((k,v))
        rows[v][(e['head']['port']-1)//3].append((k,u))
    return b,d,mask,rows,ends


def proposal(data,query):
    b,d,mask,rows,ends=data
    b,d,mask=[np.asarray(a.tolist(),dtype=float) for a in (b,d,mask)]
    n,m=b.shape;ident=np.eye(m)
    xs=[np.asarray(query,dtype=np.float64).copy() for _ in range(DEPTH+1)]
    hs=[ident.copy() for _ in range(DEPTH+1)]
    def literal(x,h):
        c,y=np.clip(x[:n],-1.,5.),np.clip(x[n:],-1.,1.)
        w=np.array([math.exp(float(v)/512) for v in y])
        def exponent(cc,j):
            r=[[sum(w[k]*(cc[v]-cc[u]) for k,v in row)/sum(w[k] for k,_ in row) if row else 0.
                for row in node] for u,node in enumerate(rows)]
            return np.array([(cc[u]+cc[v]+sum((a-z)**2 for a,z in zip(r[u],r[v]))+j[k]**2)/2**25
                for k,(u,v) in enumerate(ends)])
        z=b.T@c;j0=-w*(d@(w*z+.5*((h-ident)@z)))
        g=np.array([math.exp(-float(e)) for e in exponent(c,j0)])
        q=(w-g)/(w+g);j=j0/(1-q/32)
        flat=np.linalg.solve(h,q*j/16)
        dc=-2**-12*(b@j)
        # Direct log-drive E avoids an unnecessary exp/log cancellation.
        dy=(-math.expm1(-2**-12))*(-512*exponent(c+dc,j)-y)
        return np.concatenate((dc,dy)),ident+.25*mask*np.outer(flat,flat)
    for _ in range(SWEEPS):
        for i in range(1,DEPTH+1):
            f,_=literal(xs[i],hs[i]);xs[i]=xs[i-1]-f
        for i in range(DEPTH,0,-1):_,hs[i-1]=literal(xs[i],hs[i])
    return xs,hs


def clip(v,lo,hi):
    if not isinstance(v,arb):return ball(min(Q(hi),max(Q(lo),exact(v))))
    a,b=max(Q(lo),min(Q(hi),lower(v))),max(Q(lo),min(Q(hi),upper(v)))
    return arb((a+b)/2,(b-a)/2)


def square(v):
    # Arb's general power path can return NaN for a nonexact ball containing
    # zero. Multiplication is a valid outward enclosure on that whole ball.
    return v*v


def literal(data,values,h,*,retract=True):
    """Independent outward edge equations and complete fresh-resource writer."""
    b,d,mask,rows,ends=data;n,m=b.nrows(),b.ncols()
    bi,di=matrix(b.tolist()),matrix(d.tolist());ident=eye(m)
    c=[clip(v,-1,5) if retract else (v if isinstance(v,arb) else ball(v)) for v in values[:n]]
    y=[clip(v,-1,1) if retract else (v if isinstance(v,arb) else ball(v)) for v in values[n:]]
    w=[(v/512).exp() for v in y]
    def exponent(cc,j):
        rr=[[sum((w[k]*(cc[v]-cc[u]) for k,v in row),arb(0))/sum((w[k] for k,_ in row),arb(0)) if row else arb(0)
             for row in node] for u,node in enumerate(rows)]
        return [(cc[u]+cc[v]+sum((square(a-z) for a,z in zip(rr[u],rr[v])),arb(0))+square(j[k]))/2**25
                for k,(u,v) in enumerate(ends)]
    z=bi.transpose()*arb_mat([[v] for v in c]);correction=(h-ident)*z
    j0=di*arb_mat([[w[k]*z[k,0]+correction[k,0]/2] for k in range(m)])
    j0=[-w[k]*j0[k,0] for k in range(m)]
    g=[(-e).exp() for e in exponent(c,j0)];q=[(ww-gg)/(ww+gg) for ww,gg in zip(w,g)]
    j=[v/(1-z/32) for v,z in zip(j0,q)];flux=[z*v/16 for z,v in zip(q,j)]
    flat=h.solve(arb_mat([[v] for v in flux]))
    source=arb_mat([[ball(mask[i,k])*flat[i,0]*flat[k,0]/2 for k in range(m)] for i in range(m)])
    dc=-ball(proof.DT)*bi*arb_mat([[v] for v in j])
    ew=exponent([v+dc[i,0] for i,v in enumerate(c)],j)
    dy=[(1-(-ball(proof.DT)).exp())*(-512*e-v) for e,v in zip(ew,y)]
    require(all(v.is_finite() for v in (*dc.entries(),*dy,*source.entries())),'nonfinite literal bounds')
    return dict(increment=arb_mat([[v] for v in (*dc.entries(),*dy)]),image=ident+source/2,
                J=arb_mat([[v] for v in j]),baseline=arb_mat([[v] for v in j0]),
                readback=arb_mat([[v] for v in flux]),flat=flat,source=source,
                writer_target=[(-e).exp() for e in ew])


def coordinates(c,w):
    require(all(math.isfinite(float(v)) for v in (*c,*w)) and all(exact(v)>0 for v in w),'invalid physical coordinates')
    return [ball(v) for v in c]+[512*ball(v).log() for v in w]


def certify(graph,c,w,xs,hs,certificate):
    require(certificate==proof.graph_certificate(graph),'wrong graph certificate')
    require(all(certificate['checks'].values()),'unproved completion')
    data=algebra(graph);b,_,mask,_,_=data;n,m=b.nrows(),b.ncols()
    require(len(c)==n and len(w)==m,'incomplete state/history')
    require(len(xs)==DEPTH+1 and len(hs)==DEPTH+1,'wrong chain depth')
    for arrays,shape in ((xs,(n+m,)),(hs,(m,m))):
        require(all(isinstance(v,np.ndarray) and v.dtype==np.dtype('float64') and v.shape==shape
                    and np.all(np.isfinite(v)) for v in arrays),'invalid represented operands')
    query=list(c)+[512*math.log(v) for v in w]
    require(np.array_equal(xs[0],query) and np.array_equal(hs[-1],np.eye(m)),'query/terminal changed')
    for h in hs:
        require(np.array_equal(h,h.T),'asymmetric geometry')
        require(all(mask[i,k] or h[i,k]==0 for i in range(m) for k in range(m)),'geometry outside star support')
        require(max(sum((abs(exact(h[i,k])-int(i==k)) for k in range(m)),Q(0)) for i in range(m))<=proof.RHO,'geometry outside ball')
    with ctx.workprec(BITS):
        actual=coordinates(c,w)
        require(all(Q(-1,2)<=lower(v) and upper(v)<=Q(9,2) for v in actual[:n])
            and all(magnitude(v)<=Q(3,4) for v in actual[n:]),'query outside signed K')
        query_error=max(magnitude(ball(v)-z) for v,z in zip(query,actual));levels=[]
        for i in range(1,DEPTH+1):
            v=literal(data,xs[i],matrix(hs[i]));f,g=v['increment'],v['image']
            rx=max(magnitude(ball(xs[i][k])-ball(xs[i-1][k])+f[k,0]) for k in range(n+m))
            rh=norm(matrix(hs[i-1])-g)
            levels.append(dict(level=i,state_residual=str(rx),geometry_residual=str(rh)))
        rx=max(Q(v['state_residual']) for v in levels);rh=max(Q(v['geometry_residual']) for v in levels)
        bounds,_=proof.global_bounds();ax,ah,bx,bh=(bounds[k] for k in ('A_X','A_H','B_X','B_H'))
        amp=sum(((1-ax)**(-i) for i in range(1,DEPTH+1)),Q(0));den=1-(bh+bx*amp*ah)/2
        require(den>0,'coupled residual bound inconclusive')
        eh=(rh+bx*amp*rx/2)/den;ex=amp*(rx+ah*eh)
        tail=bounds['four_level_tail_upper'];input_error=proof.LIP*query_error;error=eh+tail+input_error
        v=literal(data,actual,matrix(hs[0]));f=v['increment'];resource_error=proof.DT*Q(9)*bounds['J_H']*error
        intervals=[(lower(ball(x)+f[i,0])-resource_error,upper(ball(x)+f[i,0])+resource_error) for i,x in enumerate(c)]
        index=min(range(n),key=lambda i:intervals[i][0]);minimum,maximum=intervals[index]
        history_upper=max(magnitude(actual[n+i]+f[n+i,0])+ah*error for i in range(m))
        return dict(levels=levels,chain_geometry_error=str(eh),chain_state_error=str(ex),finite_tail=str(tail),
            input_coordinate_error=str(query_error),input_section_error=str(input_error),section_error_upper=str(error),
            section_tolerance=str(Q(1,2**48)),section_tolerance_passes=error<=Q(1,2**48),
            exact_real_next_resource_lower=str(minimum),exact_real_first_step_positive=minimum>0,
            minimum_resource_vertex=graph['live_node_ids'][index],
            exact_real_next_resource_upper_at_minimum=str(maximum),exact_real_first_step_negative=maximum<0,
            exact_real_next_scaled_log_upper=str(history_upper),next_history_inside_K_minus=history_upper<Q(5,8),
            represented_native_step_certified=False)


def subjects():
    large=proof.read(proof.INPUTS[2]);certs=proof.check(proof.read(proof.RESULT))
    certs={v['subject']:v for v in certs['graphs']}
    return [(g,r,large[g]['graph'],large[g]['roles'][r]['C'],large[g]['roles'][r]['W_A'],
             {k:v for k,v in certs['large/'+g].items() if k!='subject'})
            for g in ('source','target') for r in ('current','reset')]


def worker(subject):
    g,r,graph,c,w,cert=subject;start=time.monotonic();data=algebra(graph)
    query=list(c)+[512*math.log(v) for v in w]
    xs,hs=proposal(data,query);proposed=time.monotonic()
    result=certify(graph,c,w,xs,hs,cert)
    return dict(graph=g,role=r,graph_digest=proof.digest(graph),C=c,W_A=w,work=encode(xs,hs),
                certificate=result,proposal_seconds=proposed-start,certification_seconds=time.monotonic()-proposed)


def bindings():
    names=(SELF,TEST,proof.SELF,proof.RESULT,proof.INPUTS[2],common.SELF)
    return [dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in names]


def scope():
    return dict(native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False,
        arithmetic='binary64_proposal_192bit_Arb_certificate',depth=DEPTH,sweeps=SWEEPS,
        proposed_writer='direct_log_drive_expm1_no_exp_log_roundtrip',
        prepared_prebeat_graphs=True,physical_law_changed=False)


def check(record,*,numerics=False):
    require(record==proof.seal(record) and record['source_bindings']==bindings(),'section record/source drift')
    require(record['schema']=='p9-arg2b-section-feasibility-v1' and record['scope']==scope(),'section research scope drift')
    declared=subjects();require(len(record['cases'])==len(declared),'missing subjects')
    for row,(g,r,graph,c,w,cert) in zip(record['cases'],declared,strict=True):
        require((row['graph'],row['role'],row['graph_digest'],row['C'],row['W_A'])==(g,r,proof.digest(graph),c,w),'section subject drift')
        xs,hs=decode(row['work'])
        require(np.array_equal(xs[0],list(c)+[512*math.log(v) for v in w]),'query mismatch')
        if numerics:require(certify(graph,c,w,xs,hs,cert)==row['certificate'],'section certificate mismatch')
    return record


def recheck_case(task):
    row,subject=task;_,_,graph,c,w,cert=subject;xs,hs=decode(row['work'])
    require(certify(graph,c,w,xs,hs,cert)==row['certificate'],'section certificate mismatch');return True


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--check',action='store_true')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    require(args.run!=args.check and 1<=args.workers<=12,'select run/check and 1..12 workers')
    if args.run:
        require(not (ROOT/RESULT).exists(),'refusing to overwrite retained sections')
        with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(worker,subjects()))
        result=proof.seal(dict(schema='p9-arg2b-section-feasibility-v1',source_bindings=bindings(),scope=scope(),cases=rows))
        check(result)
        with lzma.open(ROOT/RESULT,'wt',encoding='utf-8',preset=6) as f:json.dump(result,f,separators=(',',':'))
    else:
        with lzma.open(ROOT/RESULT,'rt',encoding='utf-8') as f:result=json.load(f)
        check(result)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:require(all(pool.map(recheck_case,zip(result['cases'],subjects(),strict=True))),'recheck failure')
    print(json.dumps([dict(graph=r['graph'],role=r['role'],proposal_seconds=r['proposal_seconds'],
        certification_seconds=r['certification_seconds'],**{k:v for k,v in r['certificate'].items() if isinstance(v,bool)},
        section_error_upper=float(Q(r['certificate']['section_error_upper'])),
        exact_real_next_resource_lower=float(Q(r['certificate']['exact_real_next_resource_lower']))) for r in result['cases']],indent=2))

if __name__=='__main__':main()
