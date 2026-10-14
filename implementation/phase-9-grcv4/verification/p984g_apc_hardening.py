"""Full final-point binding and a predeclared carrier-sensitive A_PC companion."""
import argparse
from copy import deepcopy
import hashlib
import json
import lzma
import signal
import time
import p984g_apc_staged as p

ROOT,BASE,HERE=p.ROOT,p.BASE,p.HERE
SELF=HERE+'p984g_apc_hardening.py';TEST=HERE+'test_p984g_apc_hardening.py'
PLAN=BASE+'P9-8.4g-APCHardeningPlan.md';NOTE=BASE+'P9-8.4g-APCHardening.md'
RESULTS=BASE+'P9-8.4g-APCHardeningResults.json.xz'
q,a,lo,hi,require=p.q,p.a,p.lo,p.hi,p.require


def leading_constraints(v):
    """Exact degree-two baseline rates versus common old-history scale."""
    oldids={e['edge_id'] for e in v['source']['graph']['edges']};rows=[]
    for role in ('current','reset'):
        subject=v['target'];_,ends,c,w,_=p.prior.operands(subject,role)
        def rates(scale):
            weights=[x*scale if e['edge_id'] in oldids else x for x,e in zip(w,subject['graph']['edges'])]
            phi=[q(0) for _ in c];out=[q(0) for _ in c]
            cp=subject['profile']['params_resolved']['candidate']
            for we,(u,z) in zip(weights,ends):
                x=q(cp['kappa_c'])*we*(c[u]-c[z]);phi[u]+=x;phi[z]-=x
            for we,(u,z) in zip(weights,ends):
                x=q(cp['eta'])*we*(phi[u]-phi[z]);out[u]+=x;out[z]-=x
            return out
        zero,plus,minus=rates(q(0)),rates(q(1)),rates(q(-1))
        for i,ci in enumerate(c):
            if ci==0:rows.append(dict(role=role,node=subject['graph']['live_node_ids'][i],
                coefficients=list(map(str,(zero[i],(plus[i]-minus[i])/2,(plus[i]+minus[i])/2-zero[i])))))
    require(len(rows)==10,'both-role empty-node roster');return rows


def selection():
    grid=[q(k)/16 for k in range(8,17)]
    score=lambda s:s**5*((1-s)/(1+s))**2
    constraints=leading_constraints(p.feasible.read())
    margin=lambda s:min(sum((q(x)*s**i for i,x in enumerate(row['coefficients'])),q(0)) for row in constraints)
    admissible=[s for s in grid if margin(s)>0]
    require(admissible,'no leading-feasible scale on declared grid')
    s=min(admissible,key=lambda s:(-score(s),s))
    return dict(scale=str(s),score=str(score(s)),grid=list(map(str,grid)),
        unconstrained_scale=str(min(grid,key=lambda s:(-score(s),s))),
        constraints=constraints,minimum_leading_rate=str(margin(s)),
        rule='maximize_leading_s5_contrast_squared_subject_to_both_role_empty_node_rates')


def companion(v,scale=None):
    scale=q(selection()['scale']) if scale is None else q(scale)
    source=deepcopy(v['source']);target=deepcopy(v['target'])
    for key in ('model_identity','scientific_digest','reset_digest'):source.pop(key,None)
    oldids=[e['edge_id'] for e in source['graph']['edges']]
    seed=p.prior.read(p.prior.PREPARED)['specialization']['resolved']['expansion']['bond_seed']
    for role in ('current','reset'):
        source['roles'][role]['W_A']=[p.rn(scale*q(x)) for x in source['roles'][role]['W_A']]
        lineage=dict(zip(oldids,source['roles'][role]['W_A']))
        target['roles'][role]['W_A']=[lineage.get(e['edge_id'],seed) for e in target['graph']['edges']]
        require(target['roles'][role]['Z_4']=={'recipe':'zero_v1'},'target carrier injection')
    return dict(source=source,target=target)


def excluded_companion(v,dt):
    bad=companion(v,selection()['unconstrained_scale']);out=[]
    for role in ('current','reset'):
        md=p.feasible.state_box(bad['target'],role)
        c=[x-a(dt)*sum((int(b)*j for b,j in zip(row,md['J'])),p.arb(0)) for x,row in zip(md['c'],md['b'])]
        negative=[dict(node=n,upper=str(hi(x))) for n,x in zip(bad['target']['graph']['live_node_ids'],c) if hi(x)<0]
        require(negative,'lost unconstrained exclusion');out.append(dict(role=role,negative=negative))
    return dict(scale=selection()['unconstrained_scale'],cases=out,
        disposition='excluded_by_mixed_old_history_unit_seed_resource_balance_not_solver_failure')


def point_digest(subject,role,r):
    f=r['final']
    return p.digest(dict(C=r['C'],W_A=r['W_A'],Z=r['Z'],H=f['H'],
        current=f['current'],readback=f['flux'],flat=f['flat'],source=f['source']))


def bind_final(subject,role,r):
    """Cheap algebraic binding, independent of mutable/recomputed local hashes."""
    z=p.unpack(r['Z']);n=len(subject['graph']['edges'])
    require(len(z)==len(r['W_A'])==n and len(r['C'])==len(subject['graph']['live_node_ids']),'final dimensions')
    kh=subject['profile']['params_resolved']['geometry']['kappa_H']
    expected=[[float(i==j)+p.rn(q(kh)*q(x)) for j,x in enumerate(row)] for i,row in enumerate(z)]
    require(r['final']['H']==p.sparse(expected),'final H is not bound to committed Z')
    require(r['final']['point_digest']==point_digest(subject,role,r),'final point not bound to C/W/Z/read fields')


def compare_final(subject,role,r):
    """Explicit numerical check; not called by retained-integrity verification."""
    bind_final(subject,role,r)
    fresh=p.read(p.model(subject,role,r['C'],r['W_A']),p.unpack(r['Z']))
    require(r['final']==fresh,'final complete read differs from fresh C/W/Z reconstruction')


def separation(subject,role,r):
    md=p.model(subject,role,r['C'],r['W_A']);z=p.unpack(r['Z']);n=len(z)
    _,real,_,_=p.hodge(z,md['params']['geometry']['kappa_H'])
    fresh=p.analytic(md,real)['current'];off=p.analytic(md,p.eye(n))['current']
    other=p.fixed.represented(md,p.eye(n));actual=r['final']['current']
    lowers=[max(q(0),lo(abs(x-y))) for x,y in zip(fresh,off)]
    errors=[hi(abs(a(x)-u))+hi(abs(a(y)-v)) for x,y,u,v in zip(actual,other['current'],fresh,off)]
    i=max(range(n),key=lambda i:lowers[i]-errors[i])
    return dict(witness=i,effect_lower=str(lowers[i]),two_read_error_upper=str(errors[i]),
        margin=str(lowers[i]-errors[i]),separated_coordinates=sum(x>e for x,e in zip(lowers,errors)),
        changed_current_coordinates=sum(x!=y for x,y in zip(actual,other['current'])),
        changed_flat_coordinates=sum(x!=y for x,y in zip(r['final']['flat'],other['flat'])),
        stale_H_digest=p.digest(p.sparse([[float(i==j) for j in range(n)] for i in range(n)])),
        fresh_H_digest=p.digest(r['final']['H']))


def original_pressure(v,subjects):
    rows=[]
    for case in v['cases']:
        graph,role,r=case['graph'],case['role'],case['result'];bind_final(subjects[graph],role,r)
        bad=deepcopy(r);bad['final']['H']=deepcopy(r['initial']['H'])
        bad['final']['point_digest']=point_digest(subjects[graph],role,bad)
        bad['full_chain_digest']=p.digest(dict(initial=bad['initial'],C=bad['C'],W_A=bad['W_A'],Z=bad['Z'],final=bad['final']))
        try:bind_final(subjects[graph],role,bad)
        except ValueError:rejected=True
        else:raise ValueError('stale H accepted after resealing')
        rows.append(dict(graph=graph,role=role,stale_H_resealed_rejected=rejected,
            stale_Z_current_changed_coordinates=r['stale_Z_final_current_changed_coordinates']))
    return rows


def bindings():
    names=[SELF,TEST,PLAN,p.SELF,p.RESULTS,p.feasible.SELF,p.feasible.RESULTS]
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in names}


def calculate():
    v=p.feasible.check_retained();old=p.check_retained();subjects=companion(v)
    require(p.ctx.threads==1,'one FLINT thread');cases=[]
    dt=p.prior.read(p.prior.PREPARED)['selected_configuration']['ordinary_dt']
    def timeout(*_):raise TimeoutError('300-second cap; no fallback')
    saved=signal.signal(signal.SIGALRM,timeout)
    try:
        with p.ctx.workprec(p.BITS):
            controls=original_pressure(old,v)
            exclusion=excluded_companion(v,dt)
            for graph,role in p.prior.rows.shared.CASES:
                signal.alarm(300);start=time.monotonic();subject=subjects[graph]
                r=p.analyze(subject,role,dt);bind_final(subject,role,r)
                effect=separation(subject,role,r)
                require(effect['separated_coordinates']>0 and effect['changed_current_coordinates']>0,'carrier response unresolved')
                trigger=None
                if graph=='source':
                    declaration=p.prior.read(p.prior.PREPARED);declaration['source']=subject
                    trigger=p.prior.scalar.trigger(declaration,list(map(a,r['C'])),list(map(a,r['W_A'])))
                    require(trigger['small_gradient'] and q(trigger['minimum_signed_hessian_upper'])<0,'source trigger missing')
                cases.append(dict(graph=graph,role=role,result=r,carrier_separation=effect,source_trigger=trigger))
                signal.alarm(0);print(graph,role,'complete',round(time.monotonic()-start,2),'s',flush=True)
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,saved)
    return p.prior.seal(dict(schema='p984g-apc-hardening-v1',family='A_PC',selection=selection(),subjects=subjects,
        original_staged_digest=old['record_digest'],original_pressure=controls,unconstrained_exclusion=exclusion,cases=cases,source_bindings=bindings(),
        scope='prepared_history_companion_full_PC_read_not_postbeat_event_or_native',precision_bits=p.BITS,
        native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,aggregate_closed=False))


def load():return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def check_retained(v=None):
    v=load() if v is None else v
    require(v==p.prior.seal(v) and v['source_bindings']==bindings(),'hardening identity/source drift')
    require(v['schema']=='p984g-apc-hardening-v1' and v['family']=='A_PC' and v['precision_bits']==p.BITS,'hardening schema')
    require(v['scope']=='prepared_history_companion_full_PC_read_not_postbeat_event_or_native','hardening scope')
    require(v['selection']==selection() and v['subjects']==companion(p.feasible.check_retained()),'selection/operands drift')
    old=p.check_retained();require(v['original_staged_digest']==old['record_digest'],'original evidence lost')
    require(v['original_pressure']==original_pressure(old,p.feasible.read()),'original pressure drift')
    require(v['unconstrained_exclusion']['scale']==v['selection']['unconstrained_scale']
        and [c['role'] for c in v['unconstrained_exclusion']['cases']]==['current','reset']
        and all(c['negative'] and all(q(x['upper'])<0 for x in c['negative']) for c in v['unconstrained_exclusion']['cases']),'exclusion lost')
    require([(c['graph'],c['role']) for c in v['cases']]==list(p.prior.rows.shared.CASES),'case roster')
    require(all(v[k]==0 for k in ('native_steps','native_events','ready_for_8_4h','user_accepted','aggregate_closed')),'scope promotion')
    for c in v['cases']:
        r=c['result'];bind_final(v['subjects'][c['graph']],c['role'],r)
        require(r['full_chain_digest']==p.digest(dict(initial=r['initial'],C=r['C'],W_A=r['W_A'],Z=r['Z'],final=r['final'])),'chain drift')
        e=c['carrier_separation'];require(q(e['margin'])==q(e['effect_lower'])-q(e['two_read_error_upper'])>0
            and e['separated_coordinates']>0 and e['changed_current_coordinates']>0,'effect not separated')
        require(r['minimum_resource']==min(r['C'])>0 and r['final_read_executed'] and not r['native_admission'],'read scope')
        if c['graph']=='source':require(c['source_trigger']['small_gradient'] and q(c['source_trigger']['minimum_signed_hessian_upper'])<0,'trigger')
    return v


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','check'));args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite');v=calculate();check_retained(v)
        raw=(json.dumps(v,separators=(',',':'))+'\n').encode();require(len(raw)<8000000,'raw budget')
        (ROOT/RESULTS).write_bytes(lzma.compress(raw,preset=6))
    else:check_retained()
