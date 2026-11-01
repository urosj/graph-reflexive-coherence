"""Propose a common rational C-family shape from the retained beat-375 states.

Floating eigendata and Perron-style radius inflation are discovery only. The
separate whole-domain Arb checker certifies every frozen rational operand.
"""
from pathlib import Path
import sys,json,hashlib,argparse,time
import numpy as np
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
import spark_completion_c_earlier as e
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx


def propose():
    start=time.monotonic();paths={e.BASE+'SC2PositiveCandidate.json.xz',e.BASE+'SC2SourceBeat.json.xz',
        e.BASE+'SC2CompleteWitness.json',str(Path(__file__).relative_to(ROOT))}
    old=e.read_json(e.BASE+'SC2PositiveCandidate.json.xz');e.need_seal(old)
    proof=old['checks']['trap'];graphs={k:v['graph']for k,v in old['checks']['targets'].items()}
    def array(M):return np.array([[float(M[i,j].mid().fmpq())for j in range(M.ncols())]for i in range(M.nrows())])
    def exact(A):return fmpq_mat([[fmpq(*float(x).as_integer_ratio())for x in row]for row in A])
    log=[];allr=[]
    with ctx.workprec(e.PRECISION):
        m=e.CCIReference(graphs['1']);n=m.n;d=n-1;C=m.vector(proof['center'])
        E=exact(np.vstack([np.eye(d),-np.ones(d)]));R=exact(np.eye(n)[:d])
        eigen,V=np.linalg.eig(np.array(R.tolist(),dtype=float)@array(m.full_jacobian(C)[0])@np.array(E.tolist(),dtype=float))
        e.need(np.max(abs(eigen.imag))<1e-10,'proposal eigenvectors need a real basis')
        T=V.real;T/=np.max(abs(T),axis=0);Tq=exact(T);G=E*Tq;H=Tq.inv()*R
        Hi=np.array(H.tolist(),dtype=float);center=array(C)[:,0]
        for family in ('C_CI','C_PC','C_CI_PC'):
            coefficients=[]
            for role in ('current','reset'):
                path=e.BASE+'applicability/'+e.PREFIX[family]+'-'+role+'.json.xz';paths.add(path)
                run=e.read_json(path);e.need_seal(run);row=run['checks']['observations'][374]
                e.need(row['step']==375,'proposal checkpoint')
                point=np.array([float(sum(map(e.F,row['C'][x]))/2)for x in m.nodes])
                coefficients.append(Hi@(point-center))
            r0=1.02*np.max(np.abs(coefficients),axis=0)+1e-12;r=r0.copy();zrad=1e-8
            model=e.model(family,graphs['1'])
            for iteration in range(5):
                e.need(time.monotonic()-start<e.TIME_LIMIT,'proposal time cap')
                radii=[sum(abs(G[i,j])*fmpq(*float(r[j]).as_integer_ratio())for j in range(d))for i in range(n)]
                box=arb_mat([[arb(fmpq(proof['center'][x]),radii[i])]for i,x in enumerate(m.nodes)])
                if family=='C_CI':J=model.full_jacobian(box)[0];extra=np.zeros(d)
                else:
                    Z=model.zero()
                    for i,j in model.pairs:Z[i,j]=arb(0,str(zrad));Z[j,i]=Z[i,j]
                    partial=model.partials(box,Z);J=partial['CC'];CZ=arb_mat(H)*partial['CZ']
                    extra=np.array([float(e.norm_upper(arb_mat([[CZ[i,j]for j in range(CZ.ncols())]])))*zrad for i in range(d)])
                D=arb_mat(H)*J*arb_mat(G)
                K=np.array([[float(abs(D[i,j]).upper().fmpq())for j in range(d)]for i in range(d)])
                q=float(max((K@r+extra)/r));log.append(dict(family=family,iteration=iteration,proposed_resource_row=q))
                if q<.996:allr.append(r);break
                for _ in range(1000):r=np.maximum(r0,(K@r+extra)/.995)
                e.need(np.isfinite(r).all() and max(r)<1,'unbounded proposal radii')
            else:raise ValueError('proposal iteration cap')
        radii=np.max(np.array(allr),axis=0)*1.001
    sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest())for p in sorted(paths)]
    return e.sealed(dict(schema='spark-completion-c-earlier-domain-v1',date='2026-11-01',families=list(e.FAMILIES),
        graphs=graphs,center=proof['center'],complete_basins=proof['complete_basins'],resource_dimension=14,
        basis=[[str(fmpq(*float(x).as_integer_ratio()))for x in row]for row in T],
        axis_radii=[str(fmpq(*float(x).as_integer_ratio()))for x in radii],carrier_radius='1/100000000',
        parameters=e.PARAMETERS,proposal=dict(checkpoint=375,roles=['current','reset'],
            only_single_checkpoint_per_role=True,later_states_used=False,numpy_version=np.__version__,
            iterations=log,discovery_not_preregistered=True,eigendata_are_proposals_only=True,
            coordinatewise_common_radius_inflation='1001/1000',floating_discovery_may_vary_by_platform=True),
        sources=sources,accepted_authority=False,native_completion=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    value=propose();args.output.write_text(json.dumps(value,indent=2)+'\n');print(value['record_digest'])
