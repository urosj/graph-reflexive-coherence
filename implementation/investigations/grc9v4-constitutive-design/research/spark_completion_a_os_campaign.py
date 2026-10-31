"""Fresh bounded A_OS source, lawful D11 transfer, and full-state approach."""
import time
from fractions import Fraction as F
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_a_os import AOSReference,trap_certificate,geometric_roster,graph_constants
from spark_completion_positive import fixture,norm_upper,content_id
from spark_completion_ci_campaign import retained,exact_bounds,box_payload,matrix_payload,scalar_upper
from spark_completion_continuation import need,spectral_domain

PRECISION=8192
HORIZON=1536
TIME_LIMIT=3600
WINDOW=2


def state_payload(m,C,L):
    return dict(C=box_payload(m,C),logW=[exact_bounds(x) for x in L.entries()])


def read_payload(s):
    return dict(H=matrix_payload(s['geometry']),J=matrix_payload(s['corrector']['current']),
                predictor_J=matrix_payload(s['predictor']['current']),
                flat=matrix_payload(s['corrector']['causal_flat']),split_upper=scalar_upper(s['split_upper']))


def prepare_source(source,targets,role):
    need(role in ('current','reset'),'role')
    old=retained('SC2SourceBeat.json.xz')['checks']['prepared'];m=AOSReference(source)
    C0=m.vector(old['current_prestate']);L0=arb_mat([[m.q(4097,4096).log()] for _ in range(m.m)])
    Creset=m.vector(old['reset_prestate']);Lreset=arb_mat([[m.q(8191,8192).log()] for _ in range(m.m)])
    step=m.step(C0,L0);post,lp=step['after'],step['logW_after'];fresh=m.os_read(post,lp)
    reset_read=m.os_read(Creset,Lreset)
    need(all(m.q(99,100)<w<m.q(101,100) for l in (L0,lp,Lreset) for w in m.exp(l).entries()),'source W selector/domain')
    need(all(post[i,0]>0 for i in range(m.n)),'source positive poststate')
    roster=geometric_roster(m,post,lp);need(roster=={'p':sorted(m.nodes)},'actual A postbeat parent')
    rows,_=m.rows(post,m.exp(lp));gv=rows[m.nodes.index('v')]
    gradient=16-sum(x*x for x in gv);spark=m.q(1,8)-min(-x for x in gv)
    need(gradient>0 and spark>0,'fresh committed-W source trigger')
    ports=[e[end]['port'] for e in source['edges'] for end in ('tail','head') if e[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'source saturation')
    need(sum(F(v) for v in old['current_prestate'].values())==21 and sum(F(v) for v in old['reset_prestate'].values())==21,'exact source charge')
    need(all(sum(m.B[i,j] for i in range(m.n))==0 for j in range(m.m)),'incidence charge identity')
    target=targets['1'];module=target['module'];t=AOSReference(target['graph'])
    c,l=(post,lp) if role=='current' else (Creset,Lreset)
    values={n:c[i,0] for i,n in enumerate(m.nodes) if n!='v'};values[module[0]]=arb(0)
    shares=['1/128','63/64','1/128'];need(sum(map(F,shares))==1,'allocation charge')
    for n,share in zip(module[1:],shares):values[n]=c[m.nodes.index('v'),0]*arb(fmpq(share))
    C=arb_mat([[values[n]] for n in t.nodes])
    old_weights=dict(zip(m.edge_ids,l.entries()));L=arb_mat([[old_weights.get(e,arb(0))] for e in t.edge_ids])
    need(set(m.edge_ids)<=set(t.edge_ids) and len(set(t.edge_ids)-set(m.edge_ids))==3,'literal edge lineage')
    need(set(geometric_roster(t,C,L))=={'p'},'event alone credited as gain')
    selectors={}
    for label,g in [('source',source),('target',t.graph)]:
        domain=spectral_domain(g);lower=F(domain['nonconstant_eigenvalue_lower'])*F(99,100)
        need(lower>F(1,64),'weighted selector cutoff')
        selectors[label]={**domain,'W_lower':'99/100','weighted_eigenvalue_lower':str(lower)}
    archive={r:state_payload(m,cs,ls) for r,cs,ls in [('current',post,lp),('reset',Creset,Lreset)]}
    return t,C,L,dict(current_prestate=state_payload(m,C0,L0),actual_A_OS_poststate=state_payload(m,post,lp),
        consumed_read=read_payload(step),fresh_event_read=read_payload(fresh),reset_state=state_payload(m,Creset,Lreset),
        reset_read=read_payload(reset_read),complete_parent=roster,gradient_squared_margin=exact_bounds(gradient),
        spark_margin=exact_bounds(spark),source_steps=1,reset_advanced=False,allocation_shares=shares,charge='21',
        charge_argument='Exact zero-column-sum incidence and rational shares; no trajectory normalization.',
        W_transfer=dict(policy='preserve_old_edge_W_and_seed_three_internal_edges_at_one',
            retained_edge_ids=m.edge_ids,new_edge_ids=sorted(set(t.edge_ids)-set(m.edge_ids)),
            source_archive=archive,source_archive_digest=content_id(archive),old_history_discarded=False),selectors=selectors)


def distance(m,C,L,proof,P):
    dc=C-m.vector(proof['center']);dl=L-arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
    # Positive quadratic form may have a tiny negative lower endpoint at zero.
    # Its upper endpoint is a rigorous upper bound; no midpoint trajectory is used.
    resource=(dc.transpose()*P*dc)[0,0].upper().sqrt().upper()
    conductance=proof['weight']*norm_upper(dl)
    return resource,conductance,max(resource,conductance.upper())


def campaign(role,maximum_steps=HORIZON,require_completion=True):
    start=time.monotonic();source,_,targets=fixture();proof,P=trap_certificate(targets)
    with ctx.workprec(PRECISION):
        m,C,L,s=prepare_source(source,targets,role);metric=arb_mat(P);radius=arb(fmpq(proof['radius']))
        charts={chi:AOSReference(t['graph']) for chi,t in targets.items()}
        need(all(c.pairs==m.pairs and c.terms==m.terms and c.nodes==m.nodes for c in charts.values()),'chiral equation identity')
        initial=state_payload(m,C,L);read=m.os_read(C,L);checkpoints={'event':dict(**initial,read=read_payload(read))}
        rows=[];entry=None;gain=None;reads=m.read_count;writes=m.writer_count
        for k in range(1,maximum_steps+1):
            need(time.monotonic()-start<TIME_LIMIT,'explicit one-hour campaign cap')
            C,L=m.advance(C,L,read)
            need(all(0<C[i,0]<4 for i in range(m.n)),'positive C domain')
            need(all(m.q(99,100)<w<m.q(101,100) for w in m.exp(L).entries()),'W selector/domain')
            need(sum(C.entries()).contains(21),'charge enclosure')
            read=m.os_read(C,L)
            rd,wd,total=distance(m,C,L,proof,metric)
            # Inspection uses compact outward boxes, never recurrence operands.
            state=state_payload(m,C,L)
            def ball(x):
                a,b=map(F,x);return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
            cb=arb_mat([[ball(state['C'][n])] for n in m.nodes]);lb=arb_mat([[ball(x)] for x in state['logW']])
            rosters={chi:geometric_roster(cm,cb,lb) for chi,cm in charts.items()}
            if gain is None and rosters==proof['complete_basins']:gain=k
            if entry is None and total<radius:
                need(rosters==proof['complete_basins'],'entry basin mismatch');entry=k
                checkpoints['entry']=dict(**state,read=read_payload(read))
            if entry is not None:need(total<radius and rosters==proof['complete_basins'],'positive window left full trap')
            rows.append(dict(step=k,**state,complete_basins=rosters,resource_distance_upper=scalar_upper(rd),
                weighted_logW_distance_upper=scalar_upper(wd),full_distance_upper=scalar_upper(total),split_upper=scalar_upper(read['split_upper'])))
            if k%100==0 or entry is not None:print(role,k,'seconds',round(time.monotonic()-start,1),'distance',total.str(9),flush=True)
            if entry is not None and k==entry+WINDOW:
                checkpoints['completion']=dict(**state,read=read_payload(read));break
        complete=entry is not None and len(rows)==entry+WINDOW
        if require_completion:need(complete,'no full-state completion within declared horizon')
        need(m.read_count-reads==2*len(rows) and m.writer_count-writes==len(rows),'read/write cadence')
        return dict(role=role,source_graph=source,targets=targets,source=s,proof=proof,initial_target=initial,
            observations=rows,checkpoints=checkpoints,decision=dict(role=role,scientific_completion=complete and role=='current',
                local_gain=int(complete and role=='current'),reset_probe_earns_live_gain=False,first_spatial_gain=gain,
                first_certified_entry=entry,target_completion_step=len(rows) if complete else None,window_beats=WINDOW,
                window_elapsed='64',full_state=['C','W_A'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False),
            arithmetic=dict(precision_bits=PRECISION,trapping_precision_bits=512,maximum_target_steps=HORIZON,
                time_limit_seconds=TIME_LIMIT,automatic_fallback=False,midpoint_evolution=False,storage_bits=112),
            optimization=dict(graph_cache_hits=graph_constants.cache_info().hits,graph_cache_misses=graph_constants.cache_info().misses,
                identical_full_state_read_reuse=True,fixed_row_reuse_between_predictor_corrector=True,
                predictor_identity_solve_elided=True,chiral_incidence_and_row_identity=True,
                target_physical_reads=m.read_count-reads,target_writer_calls=m.writer_count-writes,
                trajectory_results_cached=False),elapsed_seconds=time.monotonic()-start,earlier_family_trajectory_reused=False,native_steps=0)
