#!/usr/bin/env python3
"""Independent ATC-1 record, exact-arithmetic and protocol checks.

This is NOT the submitted verify_atc1_causal_boundary.py and imports no pygrc.
Synthetic publications and countermodels below test logical implications only.
Run: python pressure_checks.py --inputs inputs --output pressure_results.json
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import platform
from typing import Any


def digest(obj: Any) -> str:
    # Matches the attached record_digest recipe, not a claim to implement RFC 8785.
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def sealed(record: dict) -> bool:
    body = dict(record)
    supplied = body.pop('record_digest')
    return supplied == digest(body)


def incidence(n: int, edges: tuple[tuple[int, int], ...]) -> tuple:
    out = [[F(0) for _ in edges] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        out[u][e] += 1
        out[v][e] -= 1
    return tuple(map(tuple, out))


def node_form(b: tuple, h: tuple) -> tuple:
    n, m = len(b), len(h)
    return tuple(tuple(sum((b[i][e]*h[e][f]*b[j][f]
                           for e in range(m) for f in range(m)), F())
                       for j in range(n)) for i in range(n))


def projection(s: dict) -> dict:
    # Specification-level surrogate; not the absent production adapter.
    return copy.deepcopy({k: s[k] for k in ('graph','profile','reference','context','current')})


def run(inp: Path) -> dict:
    proposal = json.loads((inp/'ATC1CausalBoundaryProposal.json').read_text())
    submitted = json.loads((inp/'ATC1PressureResults.json').read_text())
    index = json.loads((inp/'proposal_index.json').read_text())
    location = json.loads((inp/'draft8_locations.json').read_text())
    results: dict[str, Any] = {}

    assert sealed(proposal) and sealed(submitted)
    assert submitted['evidence']['bindings']['proposal_record_digest'] == proposal['record_digest']
    assert submitted['script_sha256'] == next(x['sha256'] for x in proposal['source_bindings']
                                             if x['path'] == submitted['script_path'])
    assert len(proposal['source_bindings']) == submitted['evidence']['bindings']['source_files'] == 29
    assert len({x['path'] for x in proposal['source_bindings']}) == 29
    for obj in (proposal, submitted):
        assert not obj['scientific_acceptance'] and not obj['native_ATC_executed']
    results['record_integrity'] = {'records': 2, 'digests_match': True,
        'pressure_links_proposal': True, 'script_pin_agrees': True,
        'principal_source_bindings': 29, 'native_execution_verified': False}

    claims = {c['id']: c for c in index['claims']}
    debts = {d['id']: d for d in index['debts']}
    assert (len(claims),len(debts)) == (35,28)
    forward = {(c['id'],e['debt_id'],e['relation'],e['activation'])
               for c in index['claims'] for e in c['debt_edges']}
    backward = {(e['claim_id'],d['id'],e['relation'],e['activation'])
                for d in index['debts'] for e in d['claim_edges']}
    assert len(forward) == len(backward) == 165 and forward == backward
    retained = 0
    for c in proposal['proposed_claim_refinements']:
        origin = index['claims'][int(c['origin_pointer'].split('/')[-1])]
        assert origin['id'] == c['origin_id']
        assert c['accepted_descendants'] == []
        for k in ('assumptions','source_refs','debt_edges'):
            assert c[k] == origin[k]
        retained += len(c['debt_edges'])
    for d in proposal['proposal_debt_dispositions']:
        origin = index['debts'][int(d['origin_pointer'].split('/')[-1])]
        assert origin['id'] == d['origin_id']
        for k in ('activation','closure_requirement'):
            assert d[k] == origin[k]
    results['proposal_lineage'] = {'claims':35,'debts':28,'reciprocal_links':165,
        'refinements_checked':len(proposal['proposed_claim_refinements']),
        'retained_refinement_debt_edges':retained,
        'debt_dispositions_checked':len(proposal['proposal_debt_dispositions']),
        'accepted_descendants_added':0, 'side_tool_reexecuted':False}

    # Synthetic equality classes: administrative fields must not change the prescription.
    s = dict(graph={'vertices':[0,1,2]}, profile={'family':'A_PC','tau':1},
             reference={'recipe':'fixed'}, context={'value':0},
             current={'C':[2,2,2], 'W':[1,2], 'Z':[[0,0],[0,0]]},
             reset=[1,3,2], charge_target=6, ledger=['old'], operation_id='a',
             telemetry={'polls':0}, step_index=1, time=1., duration=.25, failed_attempts=0)
    variants = 0
    for name in proposal['selected_design']['excluded_physical_inputs']:
        key = {'receipt_archive':'ledger','operation_ids':'operation_id',
               'accumulated_time':'time','request_duration':'duration'}.get(name,name)
        other = copy.deepcopy(s)
        other[key] = {'changed_only_this_excluded_field':True}
        assert projection(other) == projection(s)
        assert digest(other) != digest(s)
        variants += 1
    results['projection_and_binding'] = {'excluded_field_variants':variants,
        'same_projection_different_publication':True,
        'scope':'synthetic equality-class check, not native freshness/CAS or production projection'}

    # Equal charge current/reset examples with a selected merge map.
    t = ((1,1,0),(0,0,1))
    mul = lambda c: tuple(sum((F(a)*F(x) for a,x in zip(row,c)), F()) for row in t)
    cur, good_reset, bad_reset = (2,2,2),(1,2,3),(2,3,1)
    assert sum(cur) == sum(good_reset) == sum(bad_reset) == 6
    assert mul(cur) == (4,2) and mul(good_reset) == (3,3) and mul(bad_reset) == (5,1)
    # Synthetic target domain, not a claimed GRCV4 profile.
    admit = lambda v: max(v) <= 4
    assert admit(mul(cur)) and admit(mul(good_reset)) and not admit(mul(bad_reset))
    # Similarly a tolerated Q offset can be admitted before, but not after redistribution.
    source=(3,3); target=(5,1); q=F(6)+F(1,4)
    # Example purpose: distinct known Q predicates can veto fixed physical maps.
    results['reset_veto'] = {'current_target':list(map(int,mul(cur))),
        'passing_reset_target':list(map(int,mul(good_reset))),
        'failing_reset_target':list(map(int,mul(bad_reset))),
        'equal_source_charge':6, 'requires_new_candidate_selection':False,
        'scope':'exact map and synthetic bound; no native target profile asserted'}

    # Pointwise equality cannot discriminate arbitrary past threshold crossings.
    previous_values = (F(1,2),F(3,2))
    current, threshold = F(3,2),F(1)
    crossing = tuple(v < threshold <= current for v in previous_values)
    assert crossing == (True,False)
    assert tuple(current for _ in previous_values) == (F(3,2),F(3,2))
    results['memoryless_crossing_countermodel'] = {
        'same_present_value':str(current), 'previous_values':list(map(str,previous_values)),
        'crossing_labels':list(crossing),
        'conclusion':'A crossing property that differs within a projection fibre cannot factor through that projection.',
        'scope':'information-theoretic countermodel, not proof these histories are native-reachable'}

    # Diagonal-edge H implies zero coupling of distinct nonadjacent nodes.
    graphs = [(3,((0,1),(1,2))),
              (4,((0,1),(1,0),(1,1),(1,2))),
              (5,((0,1),(1,2),(2,3),(3,0),(1,1)))]
    graph_cases=nonedge_checks=0
    for n,edges in graphs:
        m=len(edges); adjacency={frozenset(e) for e in edges if e[0]!=e[1]}
        for signs in itertools.product((-1,1),repeat=m):
            flipped=tuple((u,v) if sgn>0 else (v,u) for (u,v),sgn in zip(edges,signs))
            b=incidence(n,flipped)
            h=tuple(tuple(F(i+1) if i==j else F() for j in range(m)) for i in range(m))
            kv=node_form(b,h)
            for u,v in itertools.combinations(range(n),2):
                if frozenset((u,v)) not in adjacency:
                    assert kv[u][v] == 0
                    nonedge_checks+=1
            graph_cases+=1
    b=incidence(3,((0,1),(1,2)))
    h=((F(1),F(1,4)),(F(1,4),F(1)))
    kv=node_form(b,h)
    assert kv[0][2] == -F(1,4)
    assert kv[0][0] == kv[2][2] == 1
    results['reference_hodge_obstruction'] = {
        'oriented_multigraph_cases':graph_cases,'nonedge_entries_checked':nonedge_checks,
        'diagonal_reference_nonedge_entry':'0','dense_control_entry':str(kv[0][2]),
        'dense_control_normalized_q':'1/4',
        'scope':'exact incidence algebra; no native pairing/ATC execution',
        'conclusion':'A strict positive q=B H_ref B^T nonedge birth guard is silent on diagonal-reference reads.'}

    # Reproduce the reported scalar continuity using reported consumed J.
    a=submitted['evidence']['native_os_stage']
    dt=F(float.fromhex(a['dt']));j=F(a['consumed_current'][0])
    assert float(F(-2360,1029)) == a['consumed_current'][0]
    after=(float(F(3)-dt*j),float(F(1)+dt*j))
    assert list(after)==a['C_after']
    # Literal baseline with reference geometry, eta=1/4,kappa_c=1/2,
    # chi=1/2,zeta=3/4 and constant unit G_W. Reported W_after is an operand.
    c0,c1=map(F,after); w=F(a['W_after'][0])
    phi=F(float(F(1,2)*w*(c0-c1))); mobility=F(float(F(1,4)*w))
    j0=F(float(-2*mobility*phi));q=(w-1)/(w+1)
    present=float(j0/(1-F(3,8)*q))
    assert present==a['present_reference_current'][0]
    assert present != a['consumed_current'][0]
    results['scalar_stage_replay'] = {'C_after':list(after),
        'consumed_current':a['consumed_current'][0], 'present_reference_current':present,
        'scope':'independent scalar arithmetic using reported written W; no native calls or independent W-writer verification'}

    # Positive dyadic time need not advance represented accumulated time.
    t,dt=F(1),F(1,2**54)
    assert dt>0 and float(t+dt)==1.
    terms=[F(1,2**k) for k in range(1,21)]
    assert sum(terms,F())==F(1048575,1048576)
    assert min(terms)>0
    results['clock_and_rate'] = {'positive_duration':str(dt),'rounded_time':float(t+dt),
        'eligible_despite_clock_stagnation':True,'finite_dyadic_sum':str(sum(terms,F())),
        'non_zeno_theorem':False,
        'qualification':'Finite prefix only. Infinite dyadic durations eventually leave binary64; no native Zeno witness is asserted.'}

    # Exact semigroup, but checking only at positive-beat ends samples differently.
    # x=C0, total resource=4, and C1=4-x. No production dynamics claimed.
    def sampled_crossing(durations):
        x,t=F(1),F(0)
        for delta in durations:
            x+=delta; t+=delta
            if x >= F(3,2):
                return str(t),[str(x),str(4-x)]
        return None
    coarse=sampled_crossing([F(1)])
    fine=sampled_crossing([F(1,2),F(1,2)])
    assert coarse[0]=='1' and fine[0]=='1/2'
    results['sampling_countermodel'] = {'one_beat':coarse,'two_half_beats':fine,
        'base_flow_exact_semigroup':True,
        'conclusion':'A poststate-only guard is not thereby invariant under positive-beat subdivision.',
        'scope':'synthetic conservative flow; not a native ATC law or defect reproduction'}

    # Two-transaction phase semantics, without claiming locks/rollback code exist.
    phase_table={
        'invalid_static_policy':('s0',0), 'ordinary_rejected':('s0',0),
        'ordinary_programmer_error_before_commit':('s0',0),
        'ordinary_zero_success':('s1',1), 'no_event':('s1',1),
        'unresolved':('s1',1), 'uncertified':('s1',1),
        'interrupted_after_ordinary_before_event':('s1',1),
        'event_admission_rejected':('s1',1),
        'event_programmer_error_before_publication':('s1',1),
        'event_committed':('s2',2),
        'response_interrupted_after_event_commit':('s2',2),
    }
    assert proposal['selected_design']['ordinary_failure_retains']=='s0'
    assert proposal['selected_design']['event_failure_after_ordinary_commit_retains']=='s1'
    assert proposal['selected_design']['event_commit_publishes']=='s2'
    assert proposal['selected_design']['event_parent']=='successful_ordinary_primary'
    results['two_transaction_reference_table']={
        'cases':{k:{'retained_state':v[0],'successful_commits':v[1]} for k,v in phase_table.items()},
        'scope':'independent contract expectation table, not native rollback, concurrency or crash test',
        'post_commit_interruption_does_not_undo_s2':True}

    # One byte-identical primary source verifies the precise cited Appendix-D range.
    core=inp/'2025-11-ReflexiveCoherence.md'
    if core.exists():
        bts=core.read_bytes(); sha=hashlib.sha256(bts).hexdigest()
        assert sha==proposal['core_clause_reconciliation'][0]['sha256']
        lines=bts.decode().splitlines();span='\n'.join(lines[373:427])
        assert 'Appendix D:' in span
        for s in ('Global coherence conservation','Topology change','Viability thresholding','Local stability restoration'):
            assert s in span
        results['core_span']={'sha256':sha,'lines':'374-427','four_conditions_present':True,
            'other_three_pinned_core_sources_checked':False}

    return {'schema':'independent_ATC1_review_pressure_v1','status':'passed',
            'check_groups':len(results),'python':platform.python_version(),
            'submitted_verifier_reexecuted':False,'native_ATC_executed':False,
            'accepted_graph_reconstructed':False,'scientific_acceptance':False,
            'results':results}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs',type=Path,default=Path(__file__).parent/'inputs')
    ap.add_argument('--output',type=Path,default=Path(__file__).parent/'pressure_results.json')
    args=ap.parse_args()
    result=run(args.inputs)
    result['check_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(args.inputs.glob('*')) if p.is_file()}
    result['record_digest']=digest(result)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'check_groups':result['check_groups'],
                      'result_path':str(args.output)},indent=2))

if __name__=='__main__':main()
