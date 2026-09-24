"""Independent Decimal RG2b diagnostic, stdlib only, no reference imports.

Full edge-local A equations; deeper finite graph transform, displaced inverse
initialization, and 110-digit arithmetic. Convergence here is a diagnostic,
not the theorem establishing the completion's invariant section.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F

def dec(x):
    if isinstance(x,D):return x
    q=F(x);return D(q.numerator)/D(q.denominator)

def evaluator(graph,parameters,delta,kh,depth=28):
    n,edges,pos=graph['n'],graph['edges'],graph['positions'];m=len(edges)
    par={k:dec(v) for k,v in parameters.items()};dt=dec(delta);gain=dec(kh)
    decay=(-8*dt*D(2).ln()).exp()
    eye=tuple(tuple(D(int(i==j)) for j in range(m)) for i in range(m))
    def descriptors(C):
        out=[]
        for i in range(n):
            top,bot=D(0),D(1)
            for u,v in edges:
                if i not in (u,v):continue
                j=v if u==i else u;dx=D(pos[j]-pos[i])
                top+=dx*(C[j]-C[i]);bot+=dx*dx
            out.append(top/bot)
        return tuple(out)
    def drive(C,desc,J):
        ex=tuple((par['alpha']*(C[u]+C[v])+par['beta']*(desc[u]-desc[v])**2+par['gamma']*j*j)/2
                 for (u,v),j in zip(edges,J,strict=True))
        return tuple(max(D('0.5'),(-x).exp()) for x in ex)
    def solve(A,b):
        rows=[list(row)+[v] for row,v in zip(A,b,strict=True)]
        for k in range(m):
            pivot=rows[k][k]
            if pivot<=0:raise ArithmeticError('independent SPD pivot')
            rows[k]=[x/pivot for x in rows[k]]
            for i in range(k+1,m):
                q=rows[i][k];rows[i]=[x-q*y for x,y in zip(rows[i],rows[k],strict=True)]
        x=[D(0)]*m
        for i in reversed(range(m)):x[i]=rows[i][-1]-sum(rows[i][j]*x[j] for j in range(i+1,m))
        return tuple(x)
    def read(C,W,H):
        diff=tuple(C[u]-C[v] for u,v in edges)
        hdiff=tuple(sum((H[i][j]-int(i==j))*diff[j] for j in range(m)) for i in range(m))
        lap=[D(0)]*n;geo=[D(0)]*n
        for (u,v),w,d,z in zip(edges,W,diff,hdiff,strict=True):lap[u]+=w*d;lap[v]-=w*d;geo[u]+=z;geo[v]-=z
        pot=tuple(par['a']*c+par['nu']*c*c/2 for c in C)
        phi=tuple(l-v+par['kah']*g for l,v,g in zip(lap,pot,geo,strict=True))
        base=tuple(-w*(phi[u]-phi[v]) for (u,v),w in zip(edges,W,strict=True))
        desc=descriptors(C);gg=drive(C,desc,base)
        q=tuple((w-g)/(w+g) for w,g in zip(W,gg,strict=True));den=tuple(1-par['chi']*x for x in q)
        J=tuple(b/d for b,d in zip(base,den,strict=True));rb=tuple(par['chi']*x*j for x,j in zip(q,J,strict=True))
        flat=solve(H,rb)
        S=tuple(tuple(D(len(set(e)&set(f)))*flat[i]*flat[j]/2 for j,f in enumerate(edges)) for i,e in enumerate(edges))
        return dict(H=H,descriptor=desc,potential=pot,geometry_phi=tuple(geo),phi=phi,baseline=base,
                    drive=gg,effective_exponent=tuple(-g.ln() for g in gg),q=q,denominator=den,current=J,readback=rb,flat=flat,source=S)
    def raw(C,W,H):
        selected=read(C,W,H);cc=list(C)
        for (u,v),j in zip(edges,selected['current'],strict=True):cc[u]-=dt*j;cc[v]+=dt*j
        desc=descriptors(cc);gg=drive(cc,desc,selected['current'])
        ww=tuple((decay*w.ln()+(1-decay)*g.ln()).exp() for w,g in zip(W,gg,strict=True))
        return tuple(cc),ww,dict(selected=selected,writer_descriptor=desc,writer_drive=gg,
                              writer_exponent=tuple(-g.ln() for g in gg),decay=decay)
    def one(x,A,a,b,B):
        if x<=A or x>=B:return D(0)
        if a<=x<=b:return D(1)
        t=(x-A)/(a-A) if x<a else (B-x)/(B-b)
        return 3*t*t-2*t*t*t
    def completion(C,W,H):
        beta=D(1)
        for c in C:beta*=one(c,D(-2),D(-1),D(10),D(11))
        for w in W:beta*=one(w,D('.5'),D('.75'),D('1.25'),D('1.5'))
        if not beta:return C,W,eye
        cc,ww,details=raw(C,W,H)
        HH=tuple(tuple(D(int(i==j))+gain*beta*s for j,s in enumerate(row)) for i,row in enumerate(details['selected']['source']))
        return tuple(x+beta*(y-x) for x,y in zip(C,cc,strict=True)),tuple(x+beta*(y-x) for x,y in zip(W,ww,strict=True)),HH
    def section(C,W):
        query=C+W
        # Unlike the interval evaluator's initial guess, predict the N-beat
        # displacement backwards before iterative inverse correction.
        c1,w1,_=completion(C,W,eye)
        seed=tuple(x-depth*(y-x) for x,y in zip(query,c1+w1,strict=True))
        for it in range(32):
            cc,ww=seed[:n],seed[n:];HH=eye
            for _ in range(depth):cc,ww,HH=completion(cc,ww,HH)
            err=max(abs(y-x) for y,x in zip(cc+ww,query,strict=True))
            if err<D('1e-90'):return dict(H=HH,inverse_residual=err,depth=depth,inverse_iterations=it+1)
            seed=tuple(x-(y-q) for x,y,q in zip(seed,cc+ww,query,strict=True))
        raise ArithmeticError('independent inverse did not resolve')
    return read,raw,completion,section

def evaluate(graph,C,W,parameters,delta,kh,step=False,depth=28):
    with localcontext() as ctx:
        ctx.prec=110
        C,W=tuple(map(dec,C)),tuple(map(dec,W))
        read,raw,_,section=evaluator(graph,parameters,delta,kh,depth)
        sec=section(C,W);rd=read(C,W,sec['H'])
        if not step:return dict(section=sec,read=rd)
        cc,ww,d=raw(C,W,sec['H']);nsec=section(cc,ww)
        return dict(C=cc,W=ww,section=sec,selected=rd,restart=dict(section=nsec,read=read(cc,ww,nsec['H'])),
                    **{k:v for k,v in d.items() if k!='selected'})

def transfer(C,W,k):
    with localcontext() as ctx:
        ctx.prec=110
        C,W=tuple(map(dec,C)),tuple(map(dec,W));s=D(k)/65536
        return C[:4]+(s*C[4],(1-s)*C[4]),W+(D(1),)
