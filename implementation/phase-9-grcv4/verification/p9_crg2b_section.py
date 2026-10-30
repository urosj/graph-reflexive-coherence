"""Bounded numerical research for the proposed connected C_RG2b completion.

NumPy proposes a finite signed inverse chain; fixed 192-bit Arb certifies
every residual in the unchanged real equations. No native admission is run.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import lzma
import math
import time

import numpy as np
from flint import arb, arb_mat, ctx, fmpq as Q
import p9_crg2b_completion as completion

ROOT, BASE = completion.ROOT, completion.BASE
SELF = BASE+'verification/p9_crg2b_section.py'
TEST = BASE+'verification/test_p9_crg2b_section.py'
RESULT = BASE+'tranche-8/P9-CRG2b-SectionFeasibility.json.xz'
DEPTH, SWEEPS, BITS = 6, 18, 192
require = completion.require


def exact(v):
    return Q(*float(v).as_integer_ratio()) if isinstance(v,(float,np.floating)) else Q(v)


def ball(v):return arb(exact(v))
def upper(v):return v.upper().fmpq()
def lower(v):return v.lower().fmpq()
def magnitude(v):return max(abs(lower(v)),abs(upper(v)))
def matrix(v):return arb_mat([[ball(x) for x in row] for row in v])
def eye(n):return arb_mat([[int(i==j) for j in range(n)] for i in range(n)])
def norm(v):return max((sum((magnitude(v[i,j]) for j in range(v.ncols())),Q(0)) for i in range(v.nrows())),default=Q(0))


def proposal(b,mask,query):
    """Fixed 6x18 work; vertex-reduced solve, no implicit precision/fallback."""
    n,m=b.shape;bt=b.T;d=bt@b;ident=np.eye(m);identn=np.eye(n)
    xs=[np.asarray(query,dtype=np.float64).copy() for _ in range(DEPTH+1)]
    hs=[ident.copy() for _ in range(DEPTH+1)]
    def read(x,h):
        c=np.clip(x,-1.,5.)
        t=math.exp(2**-24*math.tanh(math.fsum(c)/n));p=2**-33;s=1-p
        j0=-t*d@(h@(bt@c))
        v=np.linalg.solve(s*identn+t*b@h@bt,b@j0)
        u=(j0-t*h@bt@v)/s
        j=j0+p*u
        flat=np.linalg.solve(h,16*u)
        return -2**-12*(b@j),ident+2**-38*mask*np.outer(flat,flat)
    for _ in range(SWEEPS):
        for i in range(1,DEPTH+1):
            f,_=read(xs[i],hs[i]);xs[i]=xs[i-1]-f
        for i in range(DEPTH,0,-1):
            _,hs[i-1]=read(xs[i],hs[i])
    return xs,hs


def literal(b,mask,values,h):
    """Outward real equations; exact represented operands and signed arguments."""
    n,m=b.nrows(),b.ncols();bt=b.transpose();d=bt*b
    c=arb_mat([[ball(min(Q(5),max(Q(-1),exact(v))))] for v in values])
    t=(ball(completion.KM)*(sum((c[i,0] for i in range(n)),arb(0))/n).tanh()).exp()
    p=ball(completion.CHI*completion.ZETA);s=1-p
    j0=-t*d*h*bt*c
    vertex=(s*eye(n)+t*b*h*bt).solve(b*j0)
    u=(j0-t*h*bt*vertex)/s
    j=j0+p*u
    flat=h.solve(16*u)
    source=arb_mat([[ball(completion.ZETA)*ball(mask[i,k])*flat[i,0]*flat[k,0]
        for k in range(m)] for i in range(m)])
    return -ball(completion.DT)*b*j,eye(m)+source/2,j


def certify(graph,query,xs,hs,certificate):
    require(certificate['graph_digest']==completion.digest(graph),'wrong graph certificate')
    require(all(certificate['checks'].values()),'unproved graph/section hypothesis')
    b,d,mask,_=completion.graph_algebra(graph);n,m=b.nrows(),b.ncols()
    require(len(query)==n and all(math.isfinite(float(v)) and Q(-1,2)<=exact(v)<=Q(9,2) for v in query),
            'query outside signed K')
    require(len(xs)==DEPTH+1 and len(hs)==DEPTH+1,'wrong chain depth')
    for arrays,shape in ((xs,(n,)),(hs,(m,m))):
        require(all(isinstance(v,np.ndarray) and v.dtype==np.dtype('float64') and v.shape==shape
                    and np.all(np.isfinite(v)) for v in arrays),'invalid represented operands')
    require(np.array_equal(xs[0],np.asarray(query)) and np.array_equal(hs[-1],np.eye(m)),
            'query/terminal geometry changed')
    for h in hs:
        require(np.array_equal(h,h.T),'asymmetric geometry')
        require(all(mask[i,k] or h[i,k]==0 for i in range(m) for k in range(m)),
                'geometry outside star support')
        require(max(sum((abs(exact(h[i,k])-int(i==k)) for k in range(m)),Q(0)) for i in range(m))<=completion.RHO,
                'geometry outside section ball')
    with ctx.workprec(BITS):
        bi=matrix(b.tolist());levels=[]
        for i in range(1,DEPTH+1):
            f,g,_=literal(bi,mask,xs[i],matrix(hs[i]))
            rx=max(magnitude(ball(xs[i][k])-ball(xs[i-1][k])+f[k,0]) for k in range(n))
            rh=norm(matrix(hs[i-1])-g)
            levels.append(dict(level=i,state_residual=str(rx),geometry_residual=str(rh)))
        rx=max(Q(r['state_residual']) for r in levels);rh=max(Q(r['geometry_residual']) for r in levels)
        bounds={k:Q(v) for k,v in certificate['bounds'].items()}
        ax,ah,bx,bh=(bounds[k] for k in ('A_X','A_H','B_X','B_H'))
        amplification=sum(((1-ax)**(-i) for i in range(1,DEPTH+1)),Q(0))
        denominator=1-(bh+bx*amplification*ah)/2
        require(denominator>0,'coupled residual estimate inconclusive')
        eh=(rh+bx*amplification*rx/2)/denominator
        ex=amplification*(rx+ah*eh)
        tail=bounds['six_level_tail_upper'];error=eh+tail
        # Actual fixed-H real read plus the proved entire-chart H slope.
        f,_,_=literal(bi,mask,query,matrix(hs[0]))
        jh=ah/(completion.DT*completion.norm(b))
        resource_error=completion.DT*completion.norm(b)*jh*error
        intervals=[(lower(ball(v)+f[i,0])-resource_error,
                    upper(ball(v)+f[i,0])+resource_error) for i,v in enumerate(query)]
        minimum=min(lo for lo,hi in intervals)
        return dict(levels=levels,chain_geometry_error=str(eh),chain_state_error=str(ex),
            finite_tail=str(tail),section_error_upper=str(error),
            section_tolerance=str(Q(1,2**48)),section_tolerance_passes=error<=Q(1,2**48),
            exact_real_next_resource_lower=str(minimum),exact_real_first_step_positive=minimum>0,
            first_inverse_state_error_upper=str(ex+bounds['inverse_lipschitz']*ah*bounds['contraction']**5*bounds['value_radius']),
            represented_native_step_certified=False)


def encode(xs,hs):
    return dict(x=[v.tolist() for v in xs],matrix_dimension=len(hs[0]),
                h_upper_nonzero=[[[i,j,float(h[i,j])] for i in range(len(h))
                                 for j in range(i,len(h)) if h[i,j]!=0] for h in hs])


def decode(value):
    xs=[np.asarray(v,dtype=np.float64) for v in value['x']];m=value['matrix_dimension'];hs=[]
    require(type(m) is int and m>0,'invalid sparse matrix dimension')
    for entries in value['h_upper_nonzero']:
        h=np.zeros((m,m),dtype=np.float64);seen=set()
        for i,j,v in entries:
            require(type(i) is int and type(j) is int and 0<=i<=j<m and (i,j) not in seen
                    and math.isfinite(v) and v!=0,'invalid sparse H coordinate')
            seen.add((i,j));h[i,j]=h[j,i]=v
        hs.append(h)
    require(encode(xs,hs)==value,'noncanonical sparse chain')
    return xs,hs


def subjects():
    large=completion.read(completion.INPUTS[1])
    certs=completion.check(completion.read(completion.RESULT))
    certs={r['subject']:r for r in certs['graphs']}
    return [(graph,role,large[graph]['graph'],large[graph]['roles'][role]['C'],certs['large/'+graph])
            for graph in ('source','target') for role in ('current','reset')]


def worker(subject):
    name,role,graph,query,cert=subject;start=time.monotonic()
    b,_,mask,_=completion.graph_algebra(graph)
    xs,hs=proposal(np.asarray(b.tolist(),dtype=float),np.asarray(mask.tolist(),dtype=float),query)
    proposed=time.monotonic()
    result=certify(graph,query,xs,hs,cert)
    return dict(graph=name,role=role,graph_digest=completion.digest(graph),query=list(query),
                work=encode(xs,hs),certificate=result,
                proposal_seconds=proposed-start,certification_seconds=time.monotonic()-proposed)


def bindings():
    return [dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest())
            for p in (SELF,TEST,completion.SELF,completion.RESULT,completion.INPUTS[1])]


def check(record,*,numerics=False):
    require(record==completion.seal(record) and record['source_bindings']==bindings(),'section record/source drift')
    require(record['schema']=='p9-crg2b-section-feasibility-v1','unknown section schema')
    require(record['scope']==dict(native_steps=0,native_events=0,user_accepted=False,
        aggregate_closed=False,arithmetic='binary64_proposal_192bit_Arb_certificate',
        depth=DEPTH,sweeps=SWEEPS,prepared_prebeat_graphs=True,physical_law_changed=False),
        'section research scope drift')
    declared=subjects()
    require(len(record['cases'])==len(declared),'incomplete case roster')
    for row,(name,role,graph,query,cert) in zip(record['cases'],declared,strict=True):
        require(row['graph']==name and row['role']==role and row['graph_digest']==completion.digest(graph)
                and row['query']==query,'section subject drift')
        xs,hs=decode(row['work'])
        require(np.array_equal(xs[0],query),'work query mismatch')
        if numerics:require(certify(graph,query,xs,hs,cert)==row['certificate'],'section certificate mismatch')
    return record


def recheck_case(args):
    row,subject=args
    _,_,graph,query,cert=subject
    xs,hs=decode(row['work'])
    require(certify(graph,query,xs,hs,cert)==row['certificate'],'section certificate mismatch')
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
    p.add_argument('--check',action='store_true');p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();require(a.run != a.check and 1<=a.workers<=12,'select run/check and 1..12 workers')
    if a.run:
        require(not (ROOT/RESULT).exists(),'refuse to overwrite section evidence')
        with ProcessPoolExecutor(max_workers=a.workers) as pool:rows=list(pool.map(worker,subjects()))
        result=completion.seal(dict(schema='p9-crg2b-section-feasibility-v1',source_bindings=bindings(),
            scope=dict(native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False,
                       arithmetic='binary64_proposal_192bit_Arb_certificate',depth=DEPTH,sweeps=SWEEPS,
                       prepared_prebeat_graphs=True,physical_law_changed=False),cases=rows))
        check(result)
        with lzma.open(ROOT/RESULT,'wt',encoding='utf-8',preset=6) as f:json.dump(result,f,separators=(',',':'))
    else:
        with lzma.open(ROOT/RESULT,'rt',encoding='utf-8') as f:result=json.load(f)
        check(result)
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            require(all(pool.map(recheck_case,zip(result['cases'],subjects(),strict=True))), 'certificate recheck failed')
    print(json.dumps([dict(graph=r['graph'],role=r['role'],proposal_seconds=r['proposal_seconds'],
        certification_seconds=r['certification_seconds'],**{k:v for k,v in r['certificate'].items()
        if isinstance(v,bool)},section_error_upper=float(Q(r['certificate']['section_error_upper'])),
        exact_real_next_resource_lower=float(Q(r['certificate']['exact_real_next_resource_lower'])))
        for r in result['cases']],indent=2))


if __name__=='__main__':main()
