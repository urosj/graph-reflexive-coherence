#!/usr/bin/env python3
"""PC-3 fixed causal certificate: signed carrier, actual roles, uniform return.

One source onset and two target beats per role are numerical witnesses.
Indefinite continuation and source obstruction use rational uniform bounds,
not a long trajectory. Read-only, stdout only, no native implementation.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_pc_causal_chain as pc
r=pc.r

REVIEWED_RECORD_DIGEST='f5269098cdc8ac88c21dd2eb5f1d45b76140316b816d4f68db44a635aff681f6'
REVIEWED_MATH_DIGEST='3809b7fb77887e8598c03bf040df9ea2e561c3f2cfb4e01fac559d5158f73688'


def review_metadata(value):
    mathematical={k:value[k] for k in ('profile_digest','contract_digest','evidence','CI_root_and_OS_pass_calls_forbidden')}
    actual=r.a.digest(mathematical)
    r.require(actual==REVIEWED_MATH_DIGEST,'PC3 reviewed mathematical payload changed')
    return dict(verdict='PASS_bounded_complete_A_PC_causal_chain',
        reviewed_record_digest=REVIEWED_RECORD_DIGEST,reviewed_mathematical_payload_digest=actual,
        review_path=(INV/'evidence/atc-ci-pc/PC3-IndependentReview.md').as_posix(),
        independent_reproduction='reported by supplied review; no corrective numerical rerun required',
        dependency_resolution='use currently bound typed Carrier successor, not earlier raw-matrix copy',
        formal_scoped_adjudication_pending=True)


def current_evidence(read):
    return dict(read_digest=r.a.digest(r.a.encode(read)),H=read['H'],
        potential=read['read']['potential'],baseline=read['read']['baseline'],
        current=read['read']['current'],readback=read['read']['readback'],
        structural_source=read['source'],state_binding=read['state_binding'],
        graph=read['graph'],stage='fixed_geometry_from_committed_carrier')


def norm(carrier): return r.norm_upper(x for row in carrier.values for x in row)


def radius(state): return r.norm_upper(c-F(3,2) for c in state.C)


def equal_matrix(x,y):
    return all(r.same(a,b) for row,other in zip(x,y,strict=True) for a,b in zip(row,other,strict=True))


def run_math():
    bounds=pc.bounds()
    before,reset=r.fixtures();Z=r.diagonal_z(F(1,16384));resetZ=r.diagonal_z(F(1,24576))
    r.require(r.source_check(before,F(29,10)).hi<3*r.GRID,'ordinary source starts below event threshold')
    reset_source_read=r.pc_read(reset,resetZ)
    after,postZ,consumed,restart=r.pc_step(before,Z)
    choice,event_read,targets=pc.event(after,postZ,reset,resetZ)
    r.require(r.a.encode(event_read)==r.a.encode(restart),'fresh event read equals actual committed PC restart')
    r.require(r.a.encode(consumed['read']['current'])!=r.a.encode(event_read['read']['current']),
              'preceding consumed current is not reused as event activity')
    roles={}
    for role,source,sourceZ in (('current',after,postZ),('reset',reset,resetZ)):
        item=targets[role];state,carrier=item['state'],item['carrier']
        r.require(all(r.same(a,b) for a,b in zip(state.W[:4],source.W,strict=True)) and state.W[4].lo==state.W[4].hi==r.GRID,
                  'old W follows exact lineage; bridge alone initialized')
        k=F(choice['k'],65536)
        r.require(r.same(state.C[4],k*source.C[4]) and r.same(state.C[5],(1-k)*source.C[4]),
                  'same current-selected resource map applied to each actual role')
        r.require(norm(carrier)==norm(sourceZ),'sole lossless carrier law preserves each role norm')
        c=item['receipt']['relational_scalar']
        initial_minor=carrier.values[0][0]*carrier.values[4][4]-c.square()
        if role=='current':r.require(initial_minor.hi<0,'live role really enters signed non-PSD carrier domain')
        transferred=state.payload();transferredZ=carrier.values;beats=[]
        for beat in (1,2):
            old,oldZ=state,carrier
            state,carrier,selected,reconstructed=pc.target_step(old,oldZ)
            r.require(equal_matrix(selected['H'],r.geometry(oldZ.values)),'selected geometry uses old Z')
            held=tuple(tuple((z+s)/2 for z,s in zip(row,other,strict=True))
                       for row,other in zip(oldZ.values,selected['source'],strict=True))
            r.require(equal_matrix(carrier.values,held),'Z written once using held pre-continuity source')
            r.require(equal_matrix(reconstructed['H'],r.geometry(carrier.values)),'poststate read uses committed new Z')
            r.require(not equal_matrix(selected['H'],reconstructed['H']),'old and final PC geometries discriminate')
            r.require(any(not r.same(a,b) for a,b in zip(state.W,old.W,strict=True)),'W genuinely evolves')
            r.require(not equal_matrix(carrier.values,oldZ.values),'Z genuinely evolves')
            r.require(radius(state)<F(2,3) and norm(carrier)<=r.Z_RADIUS,'target remains in return/carrier domain')
            if beat==1:r.require(radius(state)<bounds['first_target_X_upper'],'first-entry bound')
            # For the second beat, certify norm contraction against a lower
            # input norm, not merely two unrelated outward upper bounds.
            else:
                old_lower=F(r.p.norm2(tuple(c-F(3,2) for c in old.C)).sqrt().lo,r.GRID)
                r.require(radius(state)<bounds['return_factor']*old_lower,'observed return agrees with uniform contraction')
            r.require(carrier.values[4][4].lo>0,'ordinary writer leaves event image via positive bridge diagonal')
            try:pc.lift.inverse(carrier.values,token=r._DOMAIN_TOKEN,**pc.lift.CANONICAL)
            except r.a.AdmissionError:pass
            else:raise AssertionError('ordinary target incorrectly constrained to event image')
            beats.append(dict(beat=beat,state=state.payload(),Z=carrier.values,
                selected=current_evidence(selected),restart=current_evidence(reconstructed),
                X_upper=radius(state),Z_norm_upper=norm(carrier),
                outside_event_image=True,full_PC_readmission=True,held_source_write_checked=True))
        roles[role]=dict(source=source.payload(),source_Z=sourceZ.values,
            event_state=transferred,event_Z=transferredZ,carrier_receipt=item['receipt'],
            admitted_event_read=current_evidence(item['read']),initial_carrier_minor=initial_minor,
            beats=beats,indefinite_continuation_basis='uniform signed-domain resource contraction and PC carrier induction')
    controls={}
    for label,state,z in (
        ('no_split',after,postZ),('W_reset_only',r.reset_history(after),postZ),
        ('Z_reset_only',after,r.diagonal_z(F(0))),('both_reset',r.reset_history(after),r.diagonal_z(F(0)))):
        x=r.source_check(state);selected=r.pc_read(state,z)
        r.require(norm(z)<=r.Z_RADIUS,'control in invariant source carrier cone')
        controls[label]=dict(state=state.payload(),Z=z.values,read=current_evidence(selected),x=x,
            continuation='unchanged ordinary PC with evolving W/Z after this one-time control',
            resource_positive_continuation_fails_within=67,
            proof='uniform x_next >= (61/60)x; 3(61/60)^67>9, charge=9; no 67-step execution claimed')
    rejected=[]
    captured=r.a.encode(dict(current=after.payload(),currentZ=postZ.values,reset=reset.payload(),resetZ=resetZ.values))
    for name,call in (
        ('inactive_prebeat_guard',lambda:pc.select_event(before,Z)),
        ('projection_is_not_PC3_policy',lambda:pc.event(after,postZ,reset,resetZ,policy_id=pc.lift.control.POLICY)),
        ('whole_reset_is_not_PC3_policy',lambda:pc.event(after,postZ,reset,resetZ,policy_id=pc.lift.control.RESET)),
        ('PSD_policy_is_not_PC3_fallback',lambda:pc.event(after,postZ,reset,resetZ,policy_id='PSD_nonlinear_alternative')),
        ('reset_outside_transfer_domain',lambda:pc.event(after,postZ,r.paired_state(F(4),F(0),F(49,50),F(97,100)),resetZ))):
        try:call()
        except r.a.AdmissionError:rejected.append(name)
        else:raise AssertionError('PC3 admitted excluded case: '+name)
    r.require(captured==r.a.encode(dict(current=after.payload(),currentZ=postZ.values,reset=reset.payload(),resetZ=resetZ.values)),
              'research preparation/rejection leaves captured inputs unchanged')
    return dict(contract=dict(pc.PC3_CONTRACT),uniform_bounds=bounds,
        source=dict(before=before.payload(),Z_before=Z.values,postbeat=after.payload(),Z_postbeat=postZ.values,
            consumed=current_evidence(consumed),event_read=current_evidence(event_read),
            reset_read=current_evidence(reset_source_read),choice=choice,
            onset_after_one_positive_ordinary_beat=True,reset_does_not_select=True),
        roles=roles,controls=controls,rejected=rejected,
        execution_scope='one ordinary source beat and two target beats per actual role; no long trajectory, native owner or fallback',
        event_duration=0,extra_event_W_or_Z_writers=0)


def run():
    # Ensure the PC causal chain cannot accidentally call the OS pass or CI
    # root, while retaining the legitimate shared fixed-geometry evaluator.
    with patch.object(r,'ci_read',side_effect=AssertionError('CI solve forbidden in PC3')):
        with patch.object(r.a,'evaluate',side_effect=AssertionError('OS pass forbidden in PC3')):
            evidence=run_math()
    anchor=json.loads((ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json').read_text())
    value=r.a.encode(dict(schema='grcv4_atc_pc3_causal_chain_v1',
        status='PC3_independent_review_PASS_pending_scoped_adjudication',
        scientific_acceptance=False,graph_admitted=False,native_ATC_executed=False,ATC2_closed=False,PC4_completed=False,
        profile_digest=anchor['profile_digest'],contract_digest=r.a.digest(r.a.encode(dict(pc.PC3_CONTRACT))),
        evidence=evidence,CI_root_and_OS_pass_calls_forbidden=True,
        claim_updates=[dict(claim_id='ATC-PC-CHAIN-02',claim_class='conditional',
            status='review_PASS_bounded_PC3_causal_result_pending_adjudication',profile_scope=['A_PC'],
            predecessor_handles=['ATC-PC-CHAIN-01','ATC-PC-CARRIER-03'],
            debt_refs=['ATC7-DB-'+n for n in ('02','03','04','06','07','08','13','14','15','16','19','26')],
            local_debt_discharge=False,native_authority=False,
            still_open='PC4 broader domains/reference/representation; scoped source admission; wider families and aggregate ATC2')]))
    value['scientific_review']=review_metadata(value)
    paths={Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
        ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/ATCPCRelationalLiftCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/PC3-SolePolicy-ScopeReview.md',
        ROOT/INV/'evidence/atc-ci-pc/PC3-IndependentReview.md',
        ROOT/INV/'decisions/ATCSectorStateDomain.md'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            p=Path(path).resolve()
            if p.is_relative_to(ROOT/INV) and p.suffix=='.py':paths.add(p)
    value['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
    value['record_digest']=r.a.digest(value)
    return value


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
