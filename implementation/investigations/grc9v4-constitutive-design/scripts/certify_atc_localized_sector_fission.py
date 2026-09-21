#!/usr/bin/env python3
"""Source-selected localized-sector fission, bounded exact research only.

No native owner, automatic substrate change, target search or claim admission.
One prescription is selected from source alone before its target is built.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from certify_atc_os_geometry_feedback import canonical, mv, sha, stringify

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'
REFS = INV/'evidence/autonomous-topology-change'
A, H, GRID = F(19, 4), F(1, 8), 2**16
SOURCE_EDGES = tuple((i, 4) for i in range(4))
C0 = (F(1),)*4+(F(5),)
W0 = (F(361, 400),)*2+(F(5929, 6400),)*2
W1 = (F(19, 20),)*2+(F(77, 80),)*2


def incidence(n, edges):
    return tuple(tuple(int(i == u)-int(i == v) for u, v in edges) for i in range(n))


def lap(B, W):
    return tuple(tuple(sum(x*w*y for x, w, y in zip(row, W, other, strict=True))
                       for other in B) for row in B)


def read(B, C, W, a=A):
    edge = mv(tuple(zip(*B)), C)
    stiffness = mv(B, tuple(w*x for w, x in zip(W, edge)))
    potential = tuple(a*c-x for c, x in zip(C, stiffness))
    return tuple(w*x for w, x in zip(W, mv(tuple(zip(*B)), potential)))


def next_C(B, C, J, h=H):
    return tuple(c-h*x for c, x in zip(C, mv(B, J)))


def prescribe(n, edges, C, W):
    """Physical operands only: no reset, target, time, step, receipt or duration.

    Exact rational research convention. Index order names coordinates only.
    Domain and constitutive choices are fixed by this immutable script.
    """
    if not (len(C) == n and len(W) == len(edges) and 0 < n <= 16 and len(edges) <= 32):
        return dict(outcome='uncertified', reason='size_or_coordinate_domain')
    if any(not isinstance(x,(F,int)) or isinstance(x,bool) for x in (*C,*W)):
        return dict(outcome='uncertified', reason='exact_rational_operand_required')
    if any(x <= 0 for x in C) or any(not F(1, 2) <= w <= 1 for w in W):
        return dict(outcome='uncertified', reason='positive_resource_or_mobility_domain')
    if any(not (0 <= u < n and 0 <= v < n) or u == v for u, v in edges):
        return dict(outcome='uncertified', reason='graph_domain')
    if len({frozenset(e) for e in edges}) != len(edges):
        return dict(outcome='uncertified', reason='parallel_edge_domain')
    stars = [tuple(i for i, e in enumerate(edges) if v in e) for v in range(n)]
    B = incidence(n, edges); J = read(B, C, W)
    active, rows, ambiguous = [], [], False
    for parent in range(n):
        es = stars[parent]
        if len(es) != 4:
            continue
        neighbours = {e: next(v for v in edges[e] if v != parent) for e in es}
        if any(len(stars[v]) != 1 for v in neighbours.values()):
            continue
        rayleigh = F(5, 4)*sum(W[e] for e in es)
        row = dict(parent=parent, rayleigh=rayleigh, reason='spectral_certificate_inactive')
        rows.append(row)
        if rayleigh <= A:
            continue
        inward = {e: -B[parent][e]*J[e] for e in es}
        row['inward'] = inward
        if any(j <= 0 for j in inward.values()):
            row['reason'] = 'not_four_strict_inflows'
            continue
        weights = sorted({W[e] for e in es})  # Physical W order, never ID ranking.
        groups = [tuple(e for e in es if W[e] == w) for w in weights]
        if len(groups) != 2 or any(len(g) != 2 for g in groups):
            row['reason'] = 'response_partition_unresolved'; ambiguous = True
            continue
        resources = [{C[neighbours[e]] for e in group} for group in groups]
        if any(len(values) != 1 for values in resources):
            row['reason'] = 'within_sector_resource_mismatch'; ambiguous = True
            continue
        ru, rv = (next(iter(values)) for values in resources)
        x, y = C[parent]-(ru+rv)/2, (ru-rv)/2
        row.update(x=x, y=y)
        if x <= 0 or y < 0:
            row['reason'] = 'outside_declared_obstruction_cone'
            continue
        activities = [sum(inward[e] for e in group) for group in groups]
        k = round(GRID*activities[0]/sum(activities))
        shares = (F(k, GRID), F(GRID-k, GRID))
        funding = tuple(s*C[parent]-r for s, r in zip(shares, (ru, rv)))
        if min(funding) <= 0:
            row['reason'] = 'child_funding_not_strict'
            continue
        row['reason'] = 'active_localized_sector_fission'
        active.append(dict(parent=parent, blocks=groups, shares=shares, k=k,
            sector_W=weights, activities=activities, funding_margins=funding))
    outcome = 'unresolved' if ambiguous or len(active) > 1 else 'resolved' if active else 'no_event'
    if outcome=='resolved' and (n+1>16 or len(edges)+1>32):
        return dict(outcome='uncertified',reason='selected_target_size_bound',
                    prescription=None,diagnostics=rows,current=J)
    return dict(outcome=outcome, prescription=active[0] if outcome == 'resolved' else None,
                active_loci=[r['parent'] for r in active], diagnostics=rows, current=J)


def build(prescription, n, edges, current_C, reset_C):
    """One fixed post-resolution map; no target feedback into prescribe()."""
    parent = prescription['parent']; blocks = prescription['blocks']
    assert set(blocks[0]).isdisjoint(blocks[1])
    survivors = [v for v in range(n) if v != parent]
    index = {v:i for i, v in enumerate(survivors)}
    children = (n-1, n)
    edge_class = {e:k for k, block in enumerate(blocks) for e in block}
    target_edges = []
    for e, (u, v) in enumerate(edges):
        target_edges.append(tuple(children[edge_class[e]] if x == parent else index[x] for x in (u, v)))
    target_edges.append(children)
    T = tuple(tuple(F(v == old) for old in range(n)) for v in survivors)
    T += tuple(tuple(s*F(old == parent) for old in range(n)) for s in prescription['shares'])
    assert all(sum(row[j] for row in T) == 1 for j in range(n))
    cur, rst = mv(T, current_C), mv(T, reset_C)
    assert min(cur) > 0 and min(rst) > 0 and sum(cur) == sum(current_C) and sum(rst) == sum(reset_C)
    return dict(edges=tuple(target_edges), transfer=T, current_C=cur, reset_C=rst,
        current_W=(F(1),)*len(target_edges), reset_W=(F(1),)*len(target_edges),
        history_disposition='explicit_loss_all_A_W_and_independent_target_reference_pass',
        native_initializer_or_owner_called=False, reference_weights=(F(1),)*len(target_edges))


def exact_stage():
    B = incidence(5, SOURCE_EDGES)
    assert tuple(w*w for w in W1) == W0
    initial = prescribe(5, SOURCE_EDGES, C0, W0)
    assert initial['outcome'] == 'no_event'
    C1 = next_C(B, C0, initial['current'])
    assert min(C1) > 0 and sum(C1) == 9 and C1 != C0
    selected = prescribe(5, SOURCE_EDGES, C1, W1)
    assert selected['outcome'] == 'resolved' and selected['prescription']['k'] == 30876
    activities=selected['prescription']['activities']
    allocation_bin_margin=F(1,2)-abs(GRID*activities[0]/sum(activities)-30876)
    assert allocation_bin_margin>0
    # Only now construct a target; no external partition or selected target input.
    target = build(selected['prescription'], 5, SOURCE_EDGES, C1, C0)
    BT = incidence(6, target['edges']); Lt = lap(BT, (F(1),)*5)
    q_upper, radius = F(457, 512), F(2, 3)
    assert F(33, 8)**2 > 17 and q_upper < 1
    M = tuple(tuple(F(i == j)+H*(sum(Lt[i][k]*Lt[k][j] for k in range(6))-A*Lt[i][j])
                    for j in range(6)) for i in range(6))
    # Explicit complete invariant decomposition: three modes, the constant,
    # and the two-dimensional odd sector with polynomial lambda^2-5lambda+2.
    v1, v2 = (1,-1,0,0,0,0), (0,0,1,-1,0,0)
    v3 = (1,1,1,1,-2,-2)
    for v, eig in ((v1, 1), (v2, 1), (v3, 3)):
        assert mv(Lt, v) == tuple(eig*x for x in v)
    p, q = (1,1,-1,-1,0,0), (0,0,0,0,1,-1)
    assert mv(Lt, p) == tuple(x-2*y for x,y in zip(p,q))
    assert mv(Lt, q) == tuple(-x+4*y for x,y in zip(p,q))
    assert mv(Lt, (1,)*6) == (0,)*6
    entries = {}
    for role in ('current', 'reset'):
        C = target[role+'_C']; J = read(BT, C, target[role+'_W'])
        after = next_C(BT, C, J)
        assert after == mv(M, C) and min(after) > 0 and sum(after) == 9
        before_norm2 = sum((x-F(3,2))**2 for x in C)
        after_norm2 = sum((x-F(3,2))**2 for x in after)
        assert after_norm2 < F(2,5) < radius**2
        assert after_norm2 <= q_upper**2*before_norm2
        entries[role] = dict(initial_norm_squared=before_norm2, first_current=J,
            first_C=after, first_min=min(after), first_norm_squared=after_norm2)
    assert entries['current']['initial_norm_squared'] < F(9,4)
    assert entries['reset']['initial_norm_squared'] > F(9,4)
    u,v = W1[0],W1[2]; S=u+v; delta=v-u
    lower_A = S*(F(5,2)*S-A)
    assert lower_A == F(153,2560)
    assert 1+F(5,2)*H*lower_A == F(8345,8192)
    assert 1-H*A*2/2 == F(13,32)
    assert 5*max(W0) < A < F(5,2)*S
    # The other sector root lies between u and v; the top root is simple and >v.
    characteristic=lambda lam:lam*lam-3*S*lam+5*u*v
    assert characteristic(u)==2*u*(v-u)>0
    assert characteristic(v)==-2*v*(v-u)<0
    # Full source matrix versus independently derived sector recurrence.
    J1 = selected['current']; after = next_C(B,C1,J1)
    x=C1[4]-(C1[0]+C1[2])/2; y=(C1[0]-C1[2])/2
    aa=F(5,2)*S*S+delta*delta/2-A*S;bb=delta*(3*S-A);dd=A*S-S*S/2-F(5,2)*delta*delta
    assert after[4]-(after[0]+after[2])/2 == (1+F(5,2)*H*aa)*x+F(5,2)*H*bb*y
    assert (after[0]-after[2])/2 == H*bb*x/2+(1-H*dd/2)*y

    controls = {}
    controls['homogeneous'] = prescribe(5,SOURCE_EDGES,(F(9,5),)*5,W1)
    controls['uniform_history_ambiguous'] = prescribe(5,SOURCE_EDGES,C0,(F(1),)*4)
    mismatch = list(C1);mismatch[0]+=F(1,100000);mismatch[1]-=F(1,100000)
    controls['resource_sector_mismatch'] = prescribe(5,SOURCE_EDGES,tuple(mismatch),W1)
    edges2=SOURCE_EDGES+tuple((u+5,v+5) for u,v in SOURCE_EDGES)
    controls['two_active_loci'] = prescribe(10,edges2,C1+C1,W1+W1)
    controls['target_reapplication'] = prescribe(6,target['edges'],target['current_C'],target['current_W'])
    controls['target_size_bound'] = prescribe(16,SOURCE_EDGES,C1+(F(1),)*11,W1)
    assert controls['homogeneous']['outcome'] == controls['target_reapplication']['outcome'] == 'no_event'
    assert all(controls[name]['outcome'] == 'unresolved' for name in
               ('uniform_history_ambiguous','resource_sector_mismatch','two_active_loci'))
    assert controls['target_size_bound']['outcome']=='uncertified'
    # Exact representative permutation/reorientation actions, not all-group enumeration.
    covariance = []
    for vp in ((4,0,1,2,3),(2,3,0,1,4),(1,3,4,0,2)):
        inv={old:new for new,old in enumerate(vp)}
        for ep in ((3,1,0,2),(2,3,0,1)):
            for signs in ((1,1,1,1),(-1,1,-1,1)):
                edges=tuple(tuple(inv[x] for x in (SOURCE_EDGES[e] if s==1 else SOURCE_EDGES[e][::-1]))
                            for e,s in zip(ep,signs))
                r=prescribe(5,edges,tuple(C1[i] for i in vp),tuple(W1[i] for i in ep))
                assert r['outcome']=='resolved'; p2=r['prescription']; p1=selected['prescription']
                assert vp[p2['parent']]==p1['parent'] and p2['shares']==p1['shares']
                assert [set(ep[e] for e in block) for block in p2['blocks']]==[set(b) for b in p1['blocks']]
                covariance.append(dict(vertex_order=vp,edge_order=ep,orientation_signs=signs))
    # Companion only: explicitly expose ideal-vs-represented rounding, without native admission.
    rounded_C=tuple(F(float(x)) for x in C1);rounded_W=tuple(F(float(x)) for x in W1)
    rounded=prescribe(5,SOURCE_EDGES,rounded_C,rounded_W)
    assert rounded['outcome']=='resolved' and rounded['prescription']['k']==30876
    represented=build(rounded['prescription'],5,SOURCE_EDGES,rounded_C,C0)
    rounded_roles={}
    for role in ('current','reset'):
        exact=represented[role+'_C']; stored=tuple(F(float(c)) for c in exact)
        rounded_roles[role]=dict(stored_C=stored, exact_stored_sum=sum(stored),
            exact_input_sum=sum(rounded_C if role=='current' else C0),
            stored_minus_input=sum(stored)-sum(rounded_C if role=='current' else C0))
    return dict(initial_decision=initial,ordinary_post_C=C1,ordinary_post_W=W1,
        poststate_decision=selected,target=target,target_step_matrix=M,target_entry=entries,
        target_q_upper=q_upper,positive_return_radius=radius,positive_resource_lower=F(5,6),
        source_growth_multiplier_lower=F(8345,8192),source_initial_lambda_upper=5*max(W0),
        source_post_rayleigh=F(5,2)*S,source_sector_characteristic=(F(1),-3*S,5*u*v),
        allocation_bin_margin=allocation_bin_margin,source_controls=controls,covariance_checks=covariance,
        represented_companion=dict(selected_k=30876,roles=rounded_roles,native_charge_admission=False))


def finite_runs(exact):
    with localcontext() as ctx:
        ctx.prec=96
        def dec(f):
            f=F(f);return D(f.numerator)/D(f.denominator)
        a,h=dec(A),dec(H);tol=D('1e-75')
        B=incidence(5,SOURCE_EDGES);runs={}
        u,v=dec(W1[0]),dec(W1[2]);S=u+v
        lam=(3*S+(9*S*S-20*u*v).sqrt())/2
        mode=(-u/(lam-u),)*2+(-v/(lam-v),)*2+(D(1),)
        mode_image=mv(lap(B,tuple(map(dec,W1))),mode)
        assert max(abs(x-lam*y) for x,y in zip(mode_image,mode))<tol and abs(sum(mode))<tol
        contact=(lam/(lam-u),)*2+(lam/(lam-v),)*2
        assert contact[0]==contact[1]<contact[2]==contact[3]
        counts=dict(reduced_reads=0,positive_resource_updates=0,history_writes=0,
            rejected_proposals=0,native_steps=0,native_events=0,selected_research_maps=1)
        for name in ('no_split','history_reset_without_split','split_current','split_reset'):
            target=name.startswith('split_')
            if target:
                role=name.removeprefix('split_');Bnow=incidence(6,exact['target']['edges'])
                C=tuple(map(dec,exact['target'][role+'_C']));W=(D(1),)*5;limit=12
            elif name=='no_split':
                Bnow=B;C=tuple(map(dec,C0));W=tuple(map(dec,W0));limit=64
            else:
                Bnow=B;C=tuple(map(dec,exact['ordinary_post_C']));W=(D(1),)*4;limit=64
            rows=[]
            for attempt in range(1,limit+1):
                J=read(Bnow,C,W,a);Cp=next_C(Bnow,C,J,h);counts['reduced_reads']+=1
                assert abs(sum(Cp)-9)<tol
                row=dict(attempt=attempt,C=C,W=W,current=J,proposed_C=Cp,
                         structural_current='zero',geometry='identity reference')
                if not target:
                    u,v=W[0],W[2];S=u+v;delta=v-u
                    x=C[4]-(C[0]+C[2])/2;y=(C[0]-C[2])/2
                    aa=D('2.5')*S*S+delta*delta/2-a*S;bb=delta*(3*S-a);dd=a*S-S*S/2-D('2.5')*delta*delta
                    xn=(1+D('2.5')*h*aa)*x+D('2.5')*h*bb*y
                    yn=h*bb*x/2+(1-h*dd/2)*y
                    assert abs(Cp[4]-(Cp[0]+Cp[2])/2-xn)<tol and abs((Cp[0]-Cp[2])/2-yn)<tol
                    if S>=dec(F(153,80))-tol:
                        assert x>0 and y>=-tol and xn>=dec(F(8345,8192))*x-tol
                    row['independent_sector_next']=(xn,yn)
                else:
                    before_norm2=sum((x-D('1.5'))**2 for x in C)
                    norm2=sum((x-D('1.5'))**2 for x in Cp)
                    assert norm2<=dec(exact['target_q_upper'])**2*before_norm2+tol
                    assert max(abs(x-y) for x,y in zip(Cp,mv(tuple(tuple(map(dec,r)) for r in exact['target_step_matrix']),C)))<tol
                    if attempt>=1:
                        assert norm2 < dec(F(4,9)) and min(Cp)>dec(F(5,6))
                    row['norm_squared_after']=norm2
                if min(Cp)<=0:
                    row.update(disposition='resource_rejection_no_commit',retained_writer_executed=False)
                    counts['rejected_proposals']+=1;rows.append(row);break
                Wp=tuple(w.sqrt() for w in W)
                row.update(disposition='positive_mathematical_update',retained_writer_executed=True,
                           retained_C_after=Cp,retained_W_after=Wp)
                counts['positive_resource_updates']+=1;counts['history_writes']+=1
                C,W=Cp,Wp;rows.append(row)
            if not target:
                assert rows[-1]['disposition']=='resource_rejection_no_commit'
            runs[name]=rows
        assert len(runs['no_split'])==10 and len(runs['history_reset_without_split'])==7
        assert counts['reduced_reads']==41 and counts['positive_resource_updates']==39
        return stringify(dict(precision=96,interval_certified=False,counts=counts,runs=runs,
            source_top_mode=dict(eigenvalue=lam,vector=mode,parent_contact_signature=contact),
            exact_anchor_ordinary_commit_recorded_separately=True,
            rejected_states_never_write_history=True,targets_searched=0))


def run():
    predecessor_paths=(REFS/'ATCCriticalModeCertificate.json',REFS/'ATCPartitionOSFeedbackCertificate.json')
    expected=('6e3a7831bd7ae9ec3f5fa45925d3776837d1e996a6d6dec88e602ca3cf09e647',
              '76e5ece4e49a64b73d53f61b198ac2117474bbb3c9b1416929aeadcd525c85c8')
    predecessors=[];paths={Path(__file__).resolve()}
    for p,digest in zip(predecessor_paths,expected):
        v=json.loads(p.read_text())
        assert v['record_digest']==digest==sha(canonical({k:x for k,x in v.items() if k!='record_digest'}))
        for b in v['source_bindings']:
            assert sha((ROOT/b['path']).read_bytes())==b['sha256'],b['path']
            paths.add(ROOT/b['path'])
        paths.add(p);predecessors.append(dict(path=p.relative_to(ROOT).as_posix(),record_digest=digest))
    exact=exact_stage();finite=finite_runs(exact)
    side=INV/'tools/exploratory-side-tool';sys.path.insert(0,str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance,reconstruction_path
    ctx=load_current_forensic_context(ROOT,side)
    traces=[contract_provenance(ctx,key) for key in
            ('D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY','D10.2-EC-PARENT-A-WRITER-TARGET',
             'P9-EC-A-INITIALIZER-REFERENCE-PASS')]
    traces.append(reconstruction_path(ctx,'P9-7.2a-CL-O-INIT-001'))
    paths.update((INV/'decisions/ATC1CausalBoundaryProposal.md',INV/'decisions/ATC2CandidateClosureProposal.md',
        INV/'decisions/ATCSourceFissionProposal.md',ROOT/'specs/grc-v4-a-initializer-spec.md',
        INV/'scripts/certify_atc_os_geometry_feedback.py'))
    record=stringify(dict(schema='grcv4_atc_localized_sector_fission_certificate_v1',
        status='passed_bounded_source_selected_restorative_witness',
        scientific_status='new_constitutive_hypothesis_and_mathematics_pending_independent_review',
        predecessors=predecessors,exact=exact,decimal_diagnostics=finite,authority_traces=traces,
        scope=dict(candidate='A',realization='one-pass OS zero-read control',potential='19*C/4',
            alpha=0,beta=0,gamma=0,chi_A=0,eta=1,kappa_c=1,kappa_H=1,kappa_Ah=1,zeta_A=1,
            carrier=None,W_floor='1/2',h='1/8',tau_A='h/log(2)',reference_weights='all one',
            H0='unit measure',initial_C=C0,initial_W=W0,reset_C=C0,reset_W=W0,
            source_edges=SOURCE_EDGES,physical_inputs='graph,C,W,fixed research law only',
            source_rule='isolated four-star, two exact response sectors, certified cone obstruction, inflow and dyadic funding',
            history_policy='explicit all-W loss, separate target-reference-pass formula for both roles',
            prepared_source_history_not_generated_by_canonical_zero_channel_initializer=True,
            native_potential_initializer_backend_and_atomic_owner_admission=False),
        ceilings=['new sector-to-site constitutive postulate, not forced by ordinary V4',
            'exact response-sector symmetry is essential; no approximate grouping tolerance',
            'positive both-role continuation at this actual selected boundary, not all guard-positive states',
            'canonical initialization gives W=1; prepared source history has no new formation proof',
            'zero read-back/formation channels, no generic feedback or all-family closure',
            'explicit history loss is part of the mechanism, not claimed lossless transport',
            'no native owner/events, no accepted claims/debt or ATC-2 closure'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in sorted(paths)],
        production_changes=False))
    record['record_digest']=sha(canonical(record));return record


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,separators=(',',':'),allow_nan=False))
