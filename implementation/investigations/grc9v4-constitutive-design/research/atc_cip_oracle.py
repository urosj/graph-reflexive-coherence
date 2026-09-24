"""Independent Decimal CI+PC equations: no interval/reference-stage imports.

Inputs explicitly supply the graph, profile and state. Dense edge-local
assembly and a different initial geometry cross-check the joint root; this
numerical oracle is not the Banach existence/regularity proof.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F


def decimal(value):
    if isinstance(value,D): return value
    value=F(value)
    return D(value.numerator)/D(value.denominator)


def evaluate(graph,C,W,Z,parameters,h=None):
    with localcontext() as ctx:
        ctx.prec=110
        n,edges,pos=graph;m=len(edges)
        C,W=tuple(map(decimal,C)),tuple(map(decimal,W))
        Z=tuple(tuple(map(decimal,row)) for row in Z)
        par={k:decimal(v) for k,v in parameters}

        def descriptors(resources):
            answer=[]
            for i in range(n):
                numerator,denominator=D(0),D(1)
                for u,v in edges:
                    if i not in (u,v): continue
                    j=v if u==i else u;dx=D(pos[j]-pos[i])
                    numerator+=dx*(resources[j]-resources[i]);denominator+=dx*dx
                answer.append(numerator/denominator)
            return tuple(answer)

        def conductance(resources,desc,current):
            return tuple((-(par['alpha']*(resources[u]+resources[v])+
                par['beta']*(desc[u]-desc[v])**2+par['gamma']*j*j)/2).exp()
                for (u,v),j in zip(edges,current,strict=True))

        def solve(matrix,b):
            rows=[list(row)+[v] for row,v in zip(matrix,b,strict=True)]
            for k in range(m):
                pivot=rows[k][k]
                if pivot<=0: raise ArithmeticError('oracle SPD pivot')
                rows[k]=[x/pivot for x in rows[k]]
                for i in range(k+1,m):
                    factor=rows[i][k];rows[i]=[x-factor*y for x,y in zip(rows[i],rows[k],strict=True)]
            answer=[D(0)]*m
            for k in reversed(range(m)):
                answer[k]=rows[k][-1]-sum(rows[k][j]*answer[j] for j in range(k+1,m))
            return tuple(answer)

        def read(resources,weights,H):
            diff=tuple(resources[u]-resources[v] for u,v in edges)
            correction=tuple(sum((H[i][j]-int(i==j))*diff[j] for j in range(m)) for i in range(m))
            lap,geometry=[D(0)]*n,[D(0)]*n
            for (u,v),w,d,g in zip(edges,weights,diff,correction,strict=True):
                lap[u]+=w*d;lap[v]-=w*d;geometry[u]+=g;geometry[v]-=g
            potential=tuple(par['a']*c+par['nu']*c*c/2 for c in resources)
            phi=tuple(l-v+par['kah']*g for l,v,g in zip(lap,potential,geometry,strict=True))
            baseline=tuple(-w*(phi[u]-phi[v]) for (u,v),w in zip(edges,weights,strict=True))
            descriptor=descriptors(resources);drive=conductance(resources,descriptor,baseline)
            q=tuple((w-g)/(w+g) for w,g in zip(weights,drive,strict=True))
            denominator=tuple(1-par['chi']*v for v in q)
            J=tuple(b/d for b,d in zip(baseline,denominator,strict=True))
            readback=tuple(par['chi']*v*j for v,j in zip(q,J,strict=True))
            flat=solve(H,readback)
            S=tuple(tuple(D(len(set(e)&set(f)))*flat[i]*flat[j]/2 for j,f in enumerate(edges))
                    for i,e in enumerate(edges))
            return dict(potential=potential,phi=phi,baseline=baseline,descriptor=descriptor,
                drive=drive,q=q,denominator=denominator,current=J,readback=readback,flat=flat,source=S)

        def root(resources,weights,carrier):
            H=tuple(tuple(D(int(i==j))*(1+D(1)/65536) for j in range(m)) for i in range(m))
            for iteration in range(64):
                selected=read(resources,weights,H)
                generated=tuple(tuple(D(int(i==j))+par['kh']*(carrier[i][j]+s) for j,s in enumerate(row))
                                for i,row in enumerate(selected['source']))
                residual=max(abs(x-y) for row,other in zip(H,generated,strict=True) for x,y in zip(row,other,strict=True))
                if residual<D('1e-100'):
                    return dict(H=H,generated_H=generated,read=selected,residual=residual,iterations=iteration+1)
                H=generated
            raise ArithmeticError('independent CI+PC oracle did not resolve root')

        selected=root(C,W,Z)
        if h is None: return selected
        hh=decimal(h);newC=list(C)
        for (u,v),j in zip(edges,selected['read']['current'],strict=True):
            newC[u]-=hh*j;newC[v]+=hh*j
        desc=descriptors(newC);drive=conductance(newC,desc,selected['read']['current'])
        decay=(-8*hh*D(2).ln()).exp()
        newW=tuple((decay*w.ln()+(1-decay)*g.ln()).exp() for w,g in zip(W,drive,strict=True))
        newZ=tuple(tuple(decay*z+(1-decay)*s for z,s in zip(row,other,strict=True))
                   for row,other in zip(Z,selected['read']['source'],strict=True))
        return dict(C=tuple(newC),W=newW,Z=newZ,selected=selected,writer_descriptor=desc,
                    writer_drive=drive,decay=decay,restart=root(newC,newW,newZ))


def transfer(source,k):
    """Independent canonical signed bridge map, not reference transport."""
    with localcontext() as ctx:
        ctx.prec=110
        C,W=tuple(map(decimal,source['C'])),tuple(map(decimal,source['W']))
        Z=tuple(tuple(map(decimal,row)) for row in source['Z'])
        aa,b,c,d,e=Z[0][0],Z[0][1],Z[0][2],Z[2][2],Z[2][3]
        target=((aa,b,D(0),D(0),-c),(b,aa,D(0),D(0),-c),
                (D(0),D(0),d,e,c),(D(0),D(0),e,d,c),(-c,-c,c,c,D(0)))
        share=D(k)/65536
        return dict(C=C[:4]+(share*C[4],(1-share)*C[4]),W=W+(D(1),),Z=target)
