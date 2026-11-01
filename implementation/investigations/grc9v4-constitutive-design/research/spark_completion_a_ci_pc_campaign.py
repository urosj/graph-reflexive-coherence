"""Fresh A_CI_PC source/event/dual-history transfer and full-state completion."""
import time
from fractions import Fraction as F
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_a_ci_pc import ACIPCReference,trap_certificate,global_domain
from spark_completion_a_os import geometric_roster,graph_constants
from spark_completion_a_os_campaign import state_payload as cw_payload
from spark_completion_positive import fixture,content_id,norm_upper
from spark_completion_ci_campaign import retained,exact_bounds,matrix_payload,scalar_upper
from spark_completion_continuation import need,spectral_domain

PRECISION=8192
HORIZON=1024
TIME_LIMIT=3600
WINDOW=2


def state_payload(m,C,L,Z):
    return dict(**cw_payload(m,C,L),Z=[exact_bounds(Z[i,j]) for i,j in m.carrier_pairs])


def read_payload(read):
    return dict(H=matrix_payload(read['geometry']),J=matrix_payload(read['selected']['current']),
        flat=matrix_payload(read['selected']['causal_flat']),S=matrix_payload(read['source']),
        root=matrix_payload(read['flat']),error=exact_bounds(read['error']),residual=exact_bounds(read['residual'].upper()),
        proposal=matrix_payload(read['proposal']),proposal_precision_stages=read['proposal_precision_stages'],iterations=read['iterations'])


def initial_carrier(m,role):
    Z=m.zero()
    for i in range(m.m):Z[i,i]=m.q(1,2**16) if role=='current' else m.q(-1,2**17)
    return Z


def interval(pair):
    lo,hi=map(F,pair);need(0<=hi-lo<=F(1,2**110),'retained interval shape/width')
    return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))


def decode(m,row):
    need(set(row['C'])==set(m.nodes) and len(row['logW'])==m.m and len(row['Z'])==m.carrier_dimension,'all retained C/W/Z coordinates')
    C=arb_mat([[interval(row['C'][x])] for x in m.nodes]);L=arb_mat([[interval(x)] for x in row['logW']]);Z=m.zero()
    for (i,j),value in zip(m.carrier_pairs,row['Z']):Z[i,j]=interval(value);Z[j,i]=Z[i,j]
    return C,L,Z


def prepare_source(source,targets,role):
    need(role in ('current','reset'),'role')
    old=retained('SC2SourceBeat.json.xz')['checks']['prepared'];m=ACIPCReference(source)
    C0=m.vector(old['current_prestate']);L0=arb_mat([[m.q(4097,4096).log()] for _ in range(m.m)]);Z0=initial_carrier(m,'current')
    reset=m.vector(old['reset_prestate']);lr=arb_mat([[m.q(8191,8192).log()] for _ in range(m.m)]);zr=initial_carrier(m,'reset')
    ordinary=m.step(C0,L0,Z0);post,lp,zp=ordinary['after'],ordinary['logW_after'],ordinary['carrier_after']
    fresh=m.pc_read(post,lp,zp);reset_read=m.pc_read(reset,lr,zr)
    need(all(x>0 for x in post.entries()),'positive actual source')
    roster=geometric_roster(m,post,lp);need(roster=={'p':sorted(m.nodes)},'actual A_CI_PC complete parent')
    rows,_=m.rows(post,m.exp(lp));gv=rows[m.nodes.index('v')]
    gradient=16-sum(x*x for x in gv);spark=m.q(1,8)-min(-x for x in gv)
    need(gradient>0 and spark>0,'fresh A_CI_PC event trigger')
    ports=[edge[end]['port'] for edge in source['edges'] for end in ('tail','head') if edge[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'source saturation')
    need(all(sum(F(x) for x in old[k].values())==21 for k in ('current_prestate','reset_prestate')),'source charge')
    need(all(sum(m.B[i,j] for i in range(m.n))==0 for j in range(m.m)),'incidence conservation')
    target=targets['1'];module=target['module'];t=ACIPCReference(target['graph']);c,l=(post,lp) if role=='current' else (reset,lr)
    values={node:c[i,0] for i,node in enumerate(m.nodes) if node!='v'};values[module[0]]=arb(0)
    shares=['1/128','63/64','1/128'];need(sum(map(F,shares))==1,'allocation charge')
    for node,share in zip(module[1:],shares):values[node]=c[m.nodes.index('v'),0]*arb(fmpq(share))
    C=arb_mat([[values[node]] for node in t.nodes]);old_weights=dict(zip(m.edge_ids,l.entries()))
    L=arb_mat([[old_weights.get(edge,arb(0))] for edge in t.edge_ids]);Z=t.zero()
    need(set(m.edge_ids)<=set(t.edge_ids) and len(set(t.edge_ids)-set(m.edge_ids))==3,'literal W lineage')
    need(set(geometric_roster(t,C,L))=={'p'},'event alone credited as gain')
    selectors={}
    for label,g in [('source',source),('target',t.graph)]:
        domain=spectral_domain(g);lower=F(domain['nonconstant_eigenvalue_lower'])*F(99,100)*F(127,128)
        need(lower>F(1,64),'W/carrier-adjusted selector cutoff')
        selectors[label]={**domain,'W_lower':'99/100','H_lower':'127/128','weighted_carrier_eigenvalue_lower':str(lower)}
    archive={r:state_payload(m,cs,ls,zs) for r,cs,ls,zs in [('current',post,lp,zp),('reset',reset,lr,zr)]}
    history=dict(policy_id='event_loss_and_zero_target_carrier_v1',disposition='whole_carrier_reset',
        target_initializer_id='canonical_zero_carrier_v1',information_loss='carrier_history_loss',
        source_carrier_pairs=m.carrier_pairs,source_archive=archive,source_archive_digest=content_id(archive),
        target_carrier_pairs=t.carrier_pairs,target_all_dense_entries_zero=True,target_dense_entries=t.m*t.m,
        native_release=False,source_history_nonzero=True)
    return t,C,L,Z,dict(current_prestate=state_payload(m,C0,L0,Z0),actual_A_CI_PC_poststate=state_payload(m,post,lp,zp),
        consumed_current_read=read_payload(ordinary['read']),fresh_event_read=read_payload(fresh),reset_state=state_payload(m,reset,lr,zr),
        reset_read=read_payload(reset_read),complete_parent=roster,gradient_squared_margin=exact_bounds(gradient),
        spark_margin=exact_bounds(spark),source_steps=1,reset_advanced=False,allocation_shares=shares,charge='21',
        charge_argument='Exact zero-column-sum incidence and rational shares; no trajectory normalization.',domain=m.domain,
        W_transfer=dict(policy='preserve_old_edge_W_and_seed_three_internal_edges_at_one',retained_edge_ids=m.edge_ids,
            new_edge_ids=sorted(set(t.edge_ids)-set(m.edge_ids)),source_archive=archive,source_archive_digest=content_id(archive),
            old_history_discarded=False),carrier_history=history,selectors=selectors)


def distances(m,C,L,Z,proof,U):
    dc=C-m.vector(proof['center']);dl=L-arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
    z=U*arb_mat(dc.tolist()+dl.tolist());x=max(abs(v).upper() for v in z.entries())
    carrier=norm_upper(Z)/arb(fmpq(proof['carrier_radius']))
    return x,carrier,max(x,carrier.upper())


def campaign(role,maximum_steps=HORIZON,require_completion=True):
    start=time.monotonic();source,_,targets=fixture();proof,U=trap_certificate(targets)
    with ctx.workprec(PRECISION):
        m,C,L,Z,s=prepare_source(source,targets,role);metric=arb_mat(U)
        charts={chi:ACIPCReference(t['graph']) for chi,t in targets.items()}
        need(all(c.nodes==m.nodes and c.pairs==m.pairs and c.terms==m.terms and c.carrier_pairs==m.carrier_pairs for c in charts.values()),'chiral equation identity')
        initial=state_payload(m,C,L,Z);read=m.pc_read(C,L,Z);checkpoints={'event':dict(**initial,read=read_payload(read))}
        rows=[];entry=None;gain=None;reads=m.selected_read_count;writes=m.writer_count;zwrites=m.carrier_writer_count
        for k in range(1,maximum_steps+1):
            need(time.monotonic()-start<TIME_LIMIT,'explicit one-hour campaign cap')
            C,L,Z=m.advance(C,L,Z,read)
            need(all(0<x<4 for x in C.entries()) and sum(C.entries()).contains(21),'positive charge-21 state')
            read=m.pc_read(C,L,Z);xd,zd,total=distances(m,C,L,Z,proof,metric);state=state_payload(m,C,L,Z)
            cb,lb,zb=decode(m,state);rosters={chi:geometric_roster(chart,cb,lb) for chi,chart in charts.items()}
            if gain is None and rosters==proof['complete_basins']:gain=k
            if entry is None and total<1:
                need(rosters==proof['complete_basins'],'entry basin mismatch');entry=k
                checkpoints['entry']=dict(**state,read=read_payload(read))
            if entry is not None:need(total<1 and rosters==proof['complete_basins'],'positive window left trap')
            rows.append(dict(step=k,**state,complete_basins=rosters,full_distance_upper=scalar_upper(total),
                CW_distance_upper=scalar_upper(xd),weighted_carrier_distance_upper=scalar_upper(zd),
                carrier_norm_upper=scalar_upper(norm_upper(Z)),source_norm_upper=scalar_upper(norm_upper(read['source']))))
            if k%50==0 or entry is not None:print(role,k,'seconds',round(time.monotonic()-start,1),'distance',total.str(8),flush=True)
            if entry is not None and k==entry+WINDOW:
                checkpoints['completion']=dict(**state,read=read_payload(read));break
        complete=entry is not None and len(rows)==entry+WINDOW
        if require_completion:need(complete,'no full A_CI_PC completion within declared horizon')
        need(m.selected_read_count-reads==m.writer_count-writes==m.carrier_writer_count-zwrites==len(rows),'selected-read/two-writer cadence')
        return dict(role=role,source_graph=source,targets=targets,source=s,proof=proof,initial_target=initial,
            observations=rows,checkpoints=checkpoints,decision=dict(role=role,scientific_completion=complete and role=='current',
                local_gain=int(complete and role=='current'),reset_probe_earns_live_gain=False,first_spatial_gain=gain,
                first_certified_entry=entry,target_completion_step=len(rows) if complete else None,window_beats=WINDOW,
                window_elapsed='64',full_state=['C','W_A','Z_4'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False),
            arithmetic=dict(precision_bits=PRECISION,trapping_precision_bits=512,maximum_target_steps=HORIZON,
                time_limit_seconds=TIME_LIMIT,automatic_fallback=False,midpoint_evolution=False,storage_bits=112),
            optimization=dict(graph_cache_hits=graph_constants.cache_info().hits,graph_cache_misses=graph_constants.cache_info().misses,
                domain_cache_hits=global_domain.cache_info().hits,domain_cache_misses=global_domain.cache_info().misses,
                identical_full_state_read_reuse=True,weighted_rows_reused_within_read=True,multi_RHS_carrier_derivative_solve=True,multi_RHS_implicit_solve=True,
                staged_root_proposals=True,same_selected_source_for_geometry_and_writer=True,
                target_root_calls=m.root_calls-reads,root_proposal_iterations=m.proposal_iterations,
                chiral_incidence_and_row_identity=True,target_selected_reads=m.selected_read_count-reads,
                target_W_writer_calls=m.writer_count-writes,target_Z_writer_calls=m.carrier_writer_count-zwrites,trajectory_results_cached=False),
            elapsed_seconds=time.monotonic()-start,earlier_family_trajectory_reused=False,native_steps=0)
