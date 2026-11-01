"""Fresh A_RG2b source/event/history transfer and finite direct completion prefix."""
import time
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_a_rg2b import *
from spark_completion_a_rg2b_direct import (metric,metric_norm,curve_at,RADIUS,DECAY,
    ENTRY,WINDOW,EXPECTED)
from spark_completion_a_os import geometric_roster
from spark_completion_positive import fixture,content_id
from spark_completion_ci_campaign import matrix_payload


def state_payload(m,X,r):
    C,L=m.unpack(m.tube_box(X,r))
    return dict(center=[str(v.fmpq()) for v in X.entries()],radius=str(r.fmpq()),
        coordinate_system='C_then_64_logW',C={n:exact_bounds(C[i,0]) for i,n in enumerate(m.nodes)},
        logW=[exact_bounds(v) for v in L.entries()])


def decode(m,row):
    need(row['coordinate_system']=='C_then_64_logW' and len(row['center'])==m.d,'full retained coordinates')
    X=arb_mat([[ball(v)] for v in row['center']]);r=ball(row['radius'])
    need(sum(X[i,0] for i in range(m.n))==21 and 0<r<arb(2)**-64,'retained exact charge/tube')
    need(state_payload(m,X,r)=={k:row[k] for k in state_payload(m,X,r)},'retained state projection drift')
    return X,r


def section_payload(m,X,r,s,*,chain=False):
    need(s['subject'] is X,'checkpoint section subject')
    error=(s['error']+ball(m.domain['image_lipschitz'])*r).upper()
    H=arb_mat([[arb(s['proposal'][i,j].fmpq(),error.fmpq()) if m.overlap[i][j] else arb(0)
        for j in range(m.m)] for i in range(m.m)])
    read=m.lag(m.tube_box(X,r),H)
    out=dict(proposal=[[str(v.fmpq()) for v in row] for row in s['proposal'].tolist()],
        error=exact_bounds(s['error'],384),whole_tube_section_error=exact_bounds(error,384),
        H=matrix_payload(H),J=matrix_payload(read['current']),
        whole_tube_read=True,writer_target=matrix_payload(read['logW_after']))
    if chain:
        out.update(chain=s['chain'],state_residual=exact_bounds(s['state_residual'],384),
            geometry_residual=exact_bounds(s['geometry_residual'],384),tail=exact_bounds(s['tail'],768))
    return out


def point(m,C,W):
    actual=m.pack(m.vector(C),arb_mat([[ball(W).log()] for _ in range(m.m)]))
    X=m.quantize(actual);r=ball(ceil_dyadic(maxnorm(actual-X),256))
    need(sum(F(v) for v in C.values())==21 and m.in_agreement(m.tube_box(X,r)),'prepared source admission')
    return X,r


def prepare(role,declaration):
    need(role in ('current','reset'),'history role')
    source,_,raw=fixture();targets={chi:dict(graph=t['graph'],module=t['module']) for chi,t in raw.items()}
    sm=ARG2bReference(source)
    X0,r0=point(sm,declaration['prepared_source']['current'],declaration['source_W']['current'])
    reset,rr=point(sm,declaration['prepared_source']['reset'],declaration['source_W']['reset'])
    before=sm.section(X0,retain_chain=True);post,rp,diag=sm.advance_tube(X0,r0,before)
    fresh=sm.section(post,retain_chain=True);reset_section=sm.section(reset,retain_chain=True)
    C,L=sm.unpack(sm.tube_box(post,rp));W=sm.exp(L)
    need(all(x>0 for x in C.entries()),'actual source postbeat positive')
    roster=geometric_roster(sm,C,L);need(roster=={'p':sorted(sm.nodes)},'actual full parent basin')
    rows,_=sm.rows(C,W);gv=rows[sm.nodes.index('v')]
    gradient=16-sum(v*v for v in gv);spark=sm.q(1,8)-min(-v for v in gv)
    need(gradient>0 and spark>0,'actual source event trigger')
    ports=[e[end]['port'] for e in source['edges'] for end in ('tail','head') if e[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'saturated source ports')
    m=ARG2bReference(targets['1']['graph']);metric(m);module=targets['1']['module']
    shares=list(map(F,declaration['allocation_shares']));need(sum(shares)==1 and all(v>=0 for v in shares),'lawful shares')
    transfer=fmpq_mat(m.d,sm.d)
    for i,node in enumerate(m.nodes):
        if node in sm.nodes and node!='v':transfer[i,sm.nodes.index(node)]=1
        elif node in module[1:]:transfer[i,sm.nodes.index('v')]=fmpq(str(shares[module[1:].index(node)]))
    for k,edge in enumerate(m.edge_ids):
        if edge in sm.edge_ids:transfer[m.n+k,sm.n+sm.edge_ids.index(edge)]=1
    need(all(sum(transfer[i,j] for i in range(m.n))==1 for j in range(sm.n)),'allocation charge identity')
    need(set(sm.edge_ids)<=set(m.edge_ids) and len(set(m.edge_ids)-set(sm.edge_ids))==3,'literal W lineage')
    operand,r=(post,rp) if role=='current' else (reset,rr)
    value=arb_mat(transfer)*operand;X=m.quantize(value)
    radius=ball(ceil_dyadic(ball(F(str(infnorm(transfer))))*r+maxnorm(value-X),256))
    need(m.in_agreement(m.tube_box(X,radius)),'event target outside own completion')
    tc,tl=m.unpack(m.tube_box(X,radius));need(set(geometric_roster(m,tc,tl))=={'p'},'event alone earns gain')
    archive={r:state_payload(sm,x,width) for r,x,width in [('current',post,rp),('reset',reset,rr)]}
    record=dict(source_graph=source,prepared_current=state_payload(sm,X0,r0),actual_poststate=archive['current'],reset=archive['reset'],
        source_steps=1,reset_advanced=False,consumed_section=section_payload(sm,X0,r0,before,chain=True),
        fresh_event_section=section_payload(sm,post,rp,fresh,chain=True),reset_section=section_payload(sm,reset,rr,reset_section,chain=True),
        source_domain=sm.domain,source_tube={k:exact_bounds(v,256) for k,v in diag.items()},
        gradient_squared_margin=exact_bounds(gradient),spark_margin=exact_bounds(spark),complete_parent=roster,
        allocation_shares=declaration['allocation_shares'],exact_charge='21',
        resource_transfer=[[str(v) for v in row] for row in transfer.tolist()],
        W_transfer=dict(policy='preserve_old_edge_W_and_seed_three_internal_edges_at_one',
            old_edge_ids=sm.edge_ids,new_edge_ids=sorted(set(m.edge_ids)-set(sm.edge_ids)),
            source_archive=archive,source_archive_digest=content_id(archive),old_history_discarded=False),
        target_section_rebuilt=True,geometry_history_transported=False)
    return m,X,radius,record,targets


def membership(m,Q,X,r,step,entry_parameter):
    need(ENTRY<=step<=ENTRY+WINDOW,'declared positive window')
    need(0<entry_parameter<=1,'entry curve parameter outside unit interval')
    parameter=entry_parameter*DECAY**(step-ENTRY)
    center=arb_mat(curve_at(Q,parameter));distance=metric_norm(m,X-center)
    convert=max((m.n*m.trace).sqrt().upper(),arb(m.m).sqrt().upper())
    distance=(distance+convert*r).upper();margin=(ball(RADIUS)-distance).lower()
    need(margin>0,'whole executed tube outside direct domain')
    return dict(step=step,parameter=str(parameter),distance=exact_bounds(distance),strict_margin=exact_bounds(margin))


def campaign(role,declaration,domain,*,maximum_steps=None):
    start=time.monotonic();limit=ENTRY+WINDOW if maximum_steps is None else maximum_steps
    need(1<=limit<=ENTRY+WINDOW,'no subsequent supporting trajectory permitted')
    with ctx.workprec(PRECISION):
        m,X,r,source,targets=prepare(role,declaration);initial=state_payload(m,X,r)
        section=m.section(X,retain_chain=True);event=section_payload(m,X,r,section,chain=True)
        Q=fmpq_mat([[fmpq(v) for v in row] for row in domain['curves'][role]])
        charts={chi:ARG2bReference(t['graph']) for chi,t in targets.items()}
        need(all(c.nodes==m.nodes and c.pairs==m.pairs and c.terms==m.terms for c in charts.values()),'chiral identity')
        rows=[];window=[];fresh={};first=None;minimum=arb(1)
        for step in range(1,limit+1):
            need(time.monotonic()-start<3600,'explicit one-hour campaign limit')
            oldX,oldr=X,r;X,r,diag=m.advance_tube(X,r,section)
            strict=r-(diag['lipschitz']*oldr+diag['center_defect'])
            need(strict>0,'strict full-state successor tube');minimum=min(minimum,strict.lower())
            section=m.reuse(oldX,section,X);box=m.tube_box(X,r);C,L=m.unpack(box)
            need(m.in_agreement(box) and all(c>0 for c in C.entries()),'physical continuation admission')
            rosters={chi:geometric_roster(chart,C,L) for chi,chart in charts.items()}
            if first is None and all(v==EXPECTED for v in rosters.values()):first=step
            if step in (1,ENTRY,ENTRY+WINDOW):
                rebuilt=m.section(X,retain_chain=True)
                need(all(a.overlaps(b) for a,b in zip(rebuilt['geometry'].entries(),section['geometry'].entries())),'fresh section/reuse inconsistency')
                fresh[str(step)]=dict(section=section_payload(m,X,r,rebuilt,chain=True),overlap_consistency=True,
                    proof_role='consistency only; reuse follows section invariance and full-base center shift')
            rows.append(dict(step=step,**state_payload(m,X,r),complete_basins=rosters,
                section_proposal=[[str(v.fmpq()) for v in row] for row in section['proposal'].tolist()],
                section_error=exact_bounds(section['error'],384),
                tube=dict(lipschitz=exact_bounds(diag['lipschitz'],256),center_defect=exact_bounds(diag['center_defect'],384),
                    strict_image_margin=exact_bounds(strict,384))))
            if step>=ENTRY:
                need(all(v==EXPECTED for v in rosters.values()),'completion window basins')
                window.append(membership(m,Q,X,r,step,F(declaration['entry_parameters'][role])))
            if step%50==0 or step>=ENTRY:print(role,step,'seconds',round(time.monotonic()-start,2),'tube',r.str(5),flush=True)
        return dict(role=role,source=source,targets=targets,initial_target=initial,event_section=event,
            observations=rows,fresh_section_checks=fresh,window_membership=window,
            first_spatial_gain=first,entry=ENTRY if limit>=ENTRY else None,
            completion=ENTRY+WINDOW if limit==ENTRY+WINDOW else None,last_executed_step=limit,
            minimum_tube_image_margin=exact_bounds(minimum,384),
            decision=dict(scientific_completion=limit==ENTRY+WINDOW and role=='current',
                local_gain=int(limit==ENTRY+WINDOW and role=='current'),reset_probe_earns_live_gain=False,
                window_beats=WINDOW,window_elapsed=str(WINDOW*DT),ordinary_duration=str(DT),
                elapsed_from_event=str(limit*DT),full_state=['C','W_A'],relative_dimension=m.n-1+m.m,
                supporting_trajectory_steps_after_completion=0,native_completion=False,accepted_authority=False),
            section_reuse=dict(initial_section_fresh=True,each_transfer_from_invariance=True,
                full_base_center_shifts_enclosed=True,geometry_history_transported_at_event=False,
                geometry_is_independent_physical_state=False,forward_reuse_steps=m.section_reuses),
            optimization=dict(graph_cache_hits=graph_constants.cache_info().hits,domain_cache_hits=global_domain.cache_info().hits,
                certified_section_reuse=True,proposal_early_stop=True,multi_RHS_partials=True,
                exact_charge_tubes=True,trajectory_results_cached=False),
            arithmetic=dict(precision_bits=PRECISION,proposal_bits=PROPOSAL_BITS,center_bits=CENTER_BITS,
                tube_radius_bits=256,section_depth=DEPTH,horizon=limit,time_limit_seconds=3600,automatic_fallback=False),
            elapsed_seconds=time.monotonic()-start)
