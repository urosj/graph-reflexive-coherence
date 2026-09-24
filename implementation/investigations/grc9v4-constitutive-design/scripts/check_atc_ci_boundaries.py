#!/usr/bin/env python3
"""Exact closed CI domains versus numerical enclosures: bounded regressions.

No tolerance or target search. Can run alone; also part of the CI-3 checker.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
import atc_ci_reference as t
a,I,GRID,require=t.a,t.I,t.GRID,t.require


def reject(call,label):
    try: call()
    except a.AdmissionError as exc: return dict(case=label,reason=str(exc))
    raise AssertionError('boundary pressure admitted: '+label)


def proof_interface(before,following,details,profile):
    """Public forgery pressure plus internal defense-in-depth fault injection."""
    predicates=t.predicates
    require(not hasattr(predicates,'after_step'), 'raw-output proof promotion must not be exported')
    operation=following.predicates.step_provenance
    expected=dict(before_witness_digest=a.digest(before.payload()),
        selected_joint_root_digest=details['selected']['selected_joint_root_digest'],
        h=t.domains.HMIN,profile_digest=profile.identity,
        result_numerical_digest=a.digest(following.data.payload()),
        theorem_digest=a.digest(a.encode(t.domains.domain_bounds())))
    require(asdict(operation)==expected, 'successor binds the actual complete operation')
    require(details['restart']['domain_witness_binding']==a.digest(following.payload()),
            'restart root binds operation-derived witness')
    wrong_charge=a.State((I(F(7,5)),)*6,(I(F(97,100)),)*5)
    wrong_history=a.State(before.C,(I(F(4,5)),)*5)
    unrelated=a.State((I(F(3,2)),)*6,(I(F(99,100)),)*5)
    require(unrelated.payload()!=following.data.payload(), 'unrelated target is not the computed successor')
    forgeries=[]
    # No state may be minted, even for an otherwise lawful unrelated target.
    with patch.object(predicates,'State',side_effect=AssertionError('forgery reached certified State construction')):
        for label,data in (
            ('forged_after_step_wrong_charge',wrong_charge),
            ('forged_after_step_history_below_floor',wrong_history),
            ('forged_after_step_unrelated_target_state',unrelated)):
            forgeries.append(reject(lambda:predicates.certified_step(before,data,profile),label))
        receipt_rejection=reject(lambda:predicates.certified_step(before,asdict(operation),profile),
            'serialized_execution_receipt_not_proof_authority')
    # White-box injections deliberately possess the private constructor token.
    # These are consistency checks, not proof that a step took place.
    base=replace(before.predicates,exact=None)
    consistency=[]
    for label,graph,data,facts in (
        ('contradictory_charge',before.graph,wrong_charge,base),
        ('contradictory_history_floor',before.graph,wrong_history,base),
        ('contradictory_target_radius',before.graph,before.data,replace(base,radius_squared_upper=F(0))),
        ('contradictory_step_result_binding',following.graph,following.data,
            replace(following.predicates,step_provenance=replace(operation,result_numerical_digest='forged')))):
        consistency.append(reject(lambda:predicates.State(graph,data,facts,token=predicates._TOKEN),label))
    source=t.paired_state(F(13,4),F(1,100),F(99,100),F(1))
    for label,facts in (
        ('contradictory_source_x',replace(source.predicates,exact=None,x=(F(4),F(4)))),
        ('contradictory_source_y',replace(source.predicates,exact=None,y=(F(1,50),F(1,50))))):
        consistency.append(reject(lambda:predicates.State(source.graph,source.data,facts,token=predicates._TOKEN),label))
    return dict(raw_promotion_entrypoint_removed=True,forged_outputs_rejected_before_construction=forgeries,
        receipt_rejection=receipt_rejection,consistency_pressure=consistency,
        execution_provenance=a.encode(expected),complete_restart_binding=True)


def run():
    profile=t.Profile();passed=[];negatives=[];M=t.domains.M
    def source(x=F(13,4),y=F(1,100),u=F(99,100),v=F(1)):
        return t.paired_state(x,y,u,v)
    def check_root(label,state):
        root=t.root(state,profile)
        require(root['domain_witness_binding']==a.digest(state.payload()), 'full predicate witness bound to root')
        passed.append(dict(case=label,exact_predicates=a.encode(state.predicates.exact),
            selected_joint_root_digest=root['selected_joint_root_digest']))
        return root
    check_root('source_x_29_over_10',source(x=F(29,10)))
    check_root('source_W_24_over_25',source(u=M))
    for label,state in (
        ('event_x_3_y_0',source(x=F(3),y=F(0))),
        ('event_x_7_over_2',source(x=F(7,2))),
        ('event_y_1_over_50_and_W_floor',source(y=F(1,50),u=M)),
        ('reset_y_minus_1_over_50',source(y=-F(1,50)))):
        if label.startswith('reset'):
            t.role_transfer_domain(state);k=32768
        else:k=t.select(state,profile)['k']
        target,root=t.transfer(state,k,profile)
        nxt,details=t.step(target,t.domains.HMIN,profile)
        require(target.predicates.transfer_entry and not nxt.predicates.transfer_entry,
                'transfer-entry fact consumed once')
        require(nxt.predicates.radius_squared_upper<=t.domains.domain_bounds()['target_first_X_upper']**2,
                'proved first-entry predicate propagates')
        passed.append(dict(case=label,k=k,target_root=root['selected_joint_root_digest'],
            first_step_root=details['restart']['selected_joint_root_digest']))
    C=(F(7,5),)*2+(F(8,5),)*2+(F(3,2),)*2
    target=t.exact_state('paired_target',C,(M,)*4+(F(1),))
    require(any(w.lo<M*GRID for w in target.W), 'regression actually straddles rational history floor')
    check_root('target_W_24_over_25',target)
    nxt,details=t.step(target,t.domains.HMIN,profile)
    require(nxt.predicates.history_lower>=M, 'log-writer history invariant propagates')
    provenance=proof_interface(target,nxt,details,profile)
    deviations=(F(21,44),)*2+(-F(21,44),)*2+(F(9,11),-F(9,11))
    Cedge=tuple(F(3,2)+x for x in deviations)
    edge=t.exact_state('paired_target',Cedge,(F(97,100),)*5)
    require(edge.predicates.radius_squared_upper==F(9,4), 'exact target radius endpoint')
    check_root('target_X_3_over_2',edge)
    # The input itself, not a small epsilon-expanded domain, decides admission.
    tiny=F(1,2**300)
    for label,call in (
        ('x_below_root_by_subgrid',lambda:t.root(source(x=F(29,10)-tiny),profile)),
        ('source_W_below_floor_by_subgrid',lambda:t.root(source(u=M-tiny),profile)),
        ('event_x_below_3_by_subgrid',lambda:t.select(source(x=3-tiny),profile)),
        ('event_x_above_7_over_2_by_subgrid',lambda:t.select(source(x=F(7,2)+tiny),profile)),
        ('event_y_below_0_by_subgrid',lambda:t.select(source(y=-tiny),profile)),
        ('event_y_above_1_over_50_by_subgrid',lambda:t.select(source(y=F(1,50)+tiny),profile)),
        ('reset_y_below_minus_1_over_50_by_subgrid',lambda:t.role_transfer_domain(source(y=-F(1,50)-tiny))),
        ('target_W_below_floor_by_subgrid',lambda:t.root(t.exact_state('paired_target',C,(M-tiny,)*5),profile)),
        ('target_radius_outside_by_subgrid',lambda:t.root(t.exact_state('paired_target',
            tuple(F(3,2)+(1+tiny)*x for x in deviations),(F(97,100),)*5),profile)),
        ('nonexact_charge',lambda:t.exact_state('paired_target',C[:4]+(C[4]+tiny,C[5]),(F(1),)*5)),
        ('nonexact_pairing',lambda:t.exact_state('paired_target',(C[0]+tiny,C[1]-tiny)+C[2:],(F(1),)*5)),
        ('equal_decorated_sectors',lambda:t.select(source(u=F(1)),profile))):
        negatives.append(reject(call,label))
    # No overlap-based symmetry argument, even when the discrepancy is tiny.
    point=t.exact_state('paired_target',C,(F(97,100),)*5).data.represented()
    badC=list(point.C);badC[1]=I.bounds(badC[1].lo+1,badC[1].hi+1)
    badW=list(point.W);badW[1]=I.bounds(badW[1].lo+1,badW[1].hi+1)
    boxes=list(point.C);boxes[0]=I.bounds(boxes[0].lo-1,boxes[0].hi+1)
    boxes[1]=I.bounds(boxes[1].lo,boxes[1].hi+2)
    with patch.object(t.r,'paired_enclosures',side_effect=AssertionError('intersection before pairing proof')):
        for label,bad in (('unequal_point_C',a.State(tuple(badC),point.W)),
                          ('unequal_point_W',a.State(point.C,tuple(badW))),
                          ('overlapping_nonpoint_boxes',a.State(tuple(boxes),point.W))):
            negatives.append(reject(lambda:t.represented_step(bad,F(1,8),profile),label))
            negatives.append(reject(lambda:t.advance_raw('paired_target',bad,F(1,8),{},profile,
                represented_tau=True),label+'_direct_advance'))
    # Pointwise pairing does not silently import exact charge nine.
    drift=list(point.C);drift[0]=drift[1]=point.C[0]+F(1,2**48)
    drift=a.State(tuple(drift),point.W)
    require(sum(F(c.lo,GRID) for c in drift.C)!=9,'non-charge-nine represented control')
    _,details=t.represented_step(drift,F(1,8),profile)
    require(details['selected']['domain_witness_binding'] is None, 'no exact-charge theorem granted to represented state')
    negatives.append(reject(lambda:t.root(drift,profile),'represented_point_not_constructive_exact_state'))
    return dict(exact_boundaries=passed,negative_pressure=negatives,
        derived_state_provenance=provenance,
        subgrid_outside_offset=str(tiny),represented_paired_nonzero_charge_drift_admitted=True,
        scope='closed rational predicates and operation facts; unresolved derived predicates and root/share enclosures still fail closed')


if __name__=='__main__':print(json.dumps(a.encode(run()),indent=2))
