"""Fresh A_CI source/event/transfer and positive full-state completion window."""
import time
from fractions import Fraction as F
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_a_ci import ACIReference,trap_certificate,global_root_domain
from spark_completion_a_os import geometric_roster,graph_constants
from spark_completion_a_os_campaign import state_payload
from spark_completion_positive import fixture,content_id
from spark_completion_ci_campaign import retained,exact_bounds,matrix_payload,scalar_upper
from spark_completion_continuation import need,spectral_domain,infnorm

PRECISION=8192
HORIZON=1024
TIME_LIMIT=3600
WINDOW=2


def root_payload(root):
    return dict(flat=matrix_payload(root['flat']),H=matrix_payload(root['geometry']),
        J=matrix_payload(root['selected']['current']),selected_flat=matrix_payload(root['selected']['causal_flat']),
        root_error_upper=scalar_upper(root['error']),root_residual_upper=scalar_upper(root['residual'].upper()),
        proposal_iterations=root['iterations'],proposal_precision_stages=root['proposal_precision_stages'])


def prepare_source(source,targets,role):
    need(role in ('current','reset'),'role')
    old=retained('SC2SourceBeat.json.xz')['checks']['prepared'];m=ACIReference(source)
    C0=m.vector(old['current_prestate']);L0=arb_mat([[m.q(4097,4096).log()] for _ in range(m.m)])
    reset=m.vector(old['reset_prestate']);lr=arb_mat([[m.q(8191,8192).log()] for _ in range(m.m)])
    ordinary=m.step(C0,L0);post,lp=ordinary['after'],ordinary['logW_after'];fresh=m.root(post,lp);reset_root=m.root(reset,lr)
    need(all(x>0 for x in post.entries()),'positive actual source')
    roster=geometric_roster(m,post,lp);need(roster=={'p':sorted(m.nodes)},'actual A_CI complete parent')
    rows,_=m.rows(post,m.exp(lp));gv=rows[m.nodes.index('v')]
    gradient=16-sum(x*x for x in gv);spark=m.q(1,8)-min(-x for x in gv)
    need(gradient>0 and spark>0,'fresh A_CI event trigger')
    ports=[edge[end]['port'] for edge in source['edges'] for end in ('tail','head') if edge[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'source saturation')
    need(all(sum(F(x) for x in old[k].values())==21 for k in ('current_prestate','reset_prestate')),'source charge')
    need(all(sum(m.B[i,j] for i in range(m.n))==0 for j in range(m.m)),'incidence conservation')
    target=targets['1'];module=target['module'];t=ACIReference(target['graph']);c,l=(post,lp) if role=='current' else (reset,lr)
    values={node:c[i,0] for i,node in enumerate(m.nodes) if node!='v'};values[module[0]]=arb(0)
    shares=['1/128','63/64','1/128'];need(sum(map(F,shares))==1,'allocation charge')
    for node,share in zip(module[1:],shares):values[node]=c[m.nodes.index('v'),0]*arb(fmpq(share))
    C=arb_mat([[values[node]] for node in t.nodes]);old_weights=dict(zip(m.edge_ids,l.entries()))
    L=arb_mat([[old_weights.get(edge,arb(0))] for edge in t.edge_ids])
    need(set(m.edge_ids)<=set(t.edge_ids) and len(set(t.edge_ids)-set(m.edge_ids))==3,'literal W lineage')
    need(set(geometric_roster(t,C,L))=={'p'},'event alone credited as gain')
    selectors={}
    for label,g in [('source',source),('target',t.graph)]:
        domain=spectral_domain(g);lower=F(domain['nonconstant_eigenvalue_lower'])*F(99,100)
        need(lower>F(1,64),'weighted selector cutoff')
        selectors[label]={**domain,'W_lower':'99/100','weighted_eigenvalue_lower':str(lower)}
    archive={r:state_payload(m,cs,ls) for r,cs,ls in [('current',post,lp),('reset',reset,lr)]}
    return t,C,L,dict(current_prestate=state_payload(m,C0,L0),actual_A_CI_poststate=state_payload(m,post,lp),
        consumed_joint_root=root_payload(ordinary['root']),fresh_event_root=root_payload(fresh),reset_state=state_payload(m,reset,lr),
        reset_root=root_payload(reset_root),complete_parent=roster,gradient_squared_margin=exact_bounds(gradient),
        spark_margin=exact_bounds(spark),source_steps=1,reset_advanced=False,allocation_shares=shares,charge='21',
        charge_argument='Exact zero-column-sum incidence and rational shares; no trajectory normalization.',
        root_domain=m.domain,W_transfer=dict(policy='preserve_old_edge_W_and_seed_three_internal_edges_at_one',
            retained_edge_ids=m.edge_ids,new_edge_ids=sorted(set(t.edge_ids)-set(m.edge_ids)),
            source_archive=archive,source_archive_digest=content_id(archive),old_history_discarded=False),selectors=selectors)


def distance(m,C,L,proof,U):
    dc=C-m.vector(proof['center']);dl=L-arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
    z=U*arb_mat(dc.tolist()+dl.tolist())
    return max(abs(x).upper() for x in z.entries())


def campaign(role,maximum_steps=HORIZON,require_completion=True):
    start=time.monotonic();source,_,targets=fixture();proof,U=trap_certificate(targets)
    with ctx.workprec(PRECISION):
        m,C,L,s=prepare_source(source,targets,role);metric=arb_mat(U)
        charts={chi:ACIReference(t['graph']) for chi,t in targets.items()}
        need(all(c.nodes==m.nodes and c.pairs==m.pairs and c.terms==m.terms for c in charts.values()),'chiral equation identity')
        initial=state_payload(m,C,L);root=m.root(C,L);checkpoints={'event':dict(**initial,root=root_payload(root))}
        rows=[];entry=None;gain=None;roots=m.root_calls;writes=m.writer_count;iterations=m.proposal_iterations
        for k in range(1,maximum_steps+1):
            need(time.monotonic()-start<TIME_LIMIT,'explicit one-hour campaign cap')
            C,L=m.advance(C,L,root)
            need(all(0<x<4 for x in C.entries()) and sum(C.entries()).contains(21),'positive charge-21 state')
            root=m.root(C,L)
            need(all(x.contains(0) for x in (root['selected']['causal_flat']-root['flat']).entries()),'joint-root residual enclosure')
            total=distance(m,C,L,proof,metric);state=state_payload(m,C,L)
            def interval(pair):
                lo,hi=map(F,pair);return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))
            cb=arb_mat([[interval(state['C'][node])] for node in m.nodes]);lb=arb_mat([[interval(x)] for x in state['logW']])
            rosters={chi:geometric_roster(chart,cb,lb) for chi,chart in charts.items()}
            if gain is None and rosters==proof['complete_basins']:gain=k
            if entry is None and total<1:
                need(rosters==proof['complete_basins'],'entry basin mismatch');entry=k
                checkpoints['entry']=dict(**state,root=root_payload(root))
            if entry is not None:need(total<1 and rosters==proof['complete_basins'],'positive window left trap')
            rows.append(dict(step=k,**state,complete_basins=rosters,full_distance_upper=scalar_upper(total),
                root_error_upper=scalar_upper(root['error']),root_residual_upper=scalar_upper(root['residual'].upper()),
                root_proposal_iterations=root['iterations']))
            if k%50==0 or entry is not None:print(role,k,'seconds',round(time.monotonic()-start,1),'distance',total.str(8),flush=True)
            if entry is not None and k==entry+WINDOW:
                checkpoints['completion']=dict(**state,root=root_payload(root));break
        complete=entry is not None and len(rows)==entry+WINDOW
        if require_completion:need(complete,'no full A_CI completion within declared horizon')
        need(m.root_calls-roots==len(rows) and m.writer_count-writes==len(rows),'root/write cadence')
        return dict(role=role,source_graph=source,targets=targets,source=s,proof=proof,initial_target=initial,
            observations=rows,checkpoints=checkpoints,decision=dict(role=role,scientific_completion=complete and role=='current',
                local_gain=int(complete and role=='current'),reset_probe_earns_live_gain=False,first_spatial_gain=gain,
                first_certified_entry=entry,target_completion_step=len(rows) if complete else None,window_beats=WINDOW,
                window_elapsed='64',full_state=['C','W_A'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False),
            arithmetic=dict(precision_bits=PRECISION,trapping_precision_bits=512,maximum_target_steps=HORIZON,
                time_limit_seconds=TIME_LIMIT,automatic_fallback=False,midpoint_evolution=False,storage_bits=112,
                root_proposal_precision_policy='128 then powers of two through the fixed full precision; proposals only',
                root_newton_limit_per_precision=12),
            optimization=dict(graph_cache_hits=graph_constants.cache_info().hits,graph_cache_misses=graph_constants.cache_info().misses,
                root_domain_cache_hits=global_root_domain.cache_info().hits,root_domain_cache_misses=global_root_domain.cache_info().misses,
                identical_full_state_root_reuse=True,weighted_rows_reused_within_root_proposal=True,
                multi_RHS_geometry_derivative_solve=True,staged_root_proposals=True,chiral_incidence_and_row_identity=True,
                target_joint_roots=m.root_calls-roots,target_writer_calls=m.writer_count-writes,
                target_proposal_iterations=m.proposal_iterations-iterations,trajectory_results_cached=False),
            elapsed_seconds=time.monotonic()-start,earlier_family_trajectory_reused=False,native_steps=0)
