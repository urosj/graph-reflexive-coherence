#!/usr/bin/env python3
"""CI-1/PC-1 fixed-anchor certificates; research only, stdout only.

No target search, parameter sweep, native ATC or alteration of accepted A_OS.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
INV=Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0,str(ROOT/INV/'research'))
import atc_ci_pc_anchor as r

REVIEWED_NUMERICS_SHA256='7a4b8856b701a6df02b72e15c19de761a889faf0636c6d7e6f514aabd9e200ea'


def numerical_projection(value):
    """Only review status and expanded joint-read metadata digest may differ."""
    if isinstance(value,dict):
        return {k:numerical_projection(v) for k,v in value.items()
                if k not in ('status','selected_joint_read_digest')}
    if isinstance(value,list): return [numerical_projection(v) for v in value]
    return value


def review_resolution():
    """Resolve the quoted HOLD against the accepted, relocated G7 chain.

    No git executable or machine-local history is needed for reproduction.
    The file-level comparison with accepted commit 5e1a63a was additionally
    performed during review resolution; the frozen G7 bindings travel in git.
    """
    g7path=ROOT/INV/'evidence/autonomous-topology-change/ATCSectorReferenceConformance.json'
    g7=json.loads(g7path.read_text())
    frozen={b['path']:b['sha256'] for b in g7['source_bindings']}
    checked=[]
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if not name: continue
        path=Path(name).resolve()
        if not path.is_relative_to(ROOT/INV) or path.suffix!='.py' or path in (
                Path(__file__).resolve(),ROOT/INV/'research/atc_ci_pc_anchor.py'): continue
        rel=path.relative_to(ROOT).as_posix()
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        r.require(frozen.get(rel)==sha,'inherited kernel must match frozen accepted G7: '+rel)
        checked.append(dict(path=rel,sha256=sha))
    # Every required inherited math module must be covered, not a vacuous pass.
    r.require(len(checked)>=5,'complete inherited module roster')
    paths=[g7path,Path(__file__).resolve(),ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
           ROOT/INV/'evidence/atc-ci-pc/CI1PC1-IndependentReview.md']
    value=dict(schema='grcv4_atc_ci_pc_review_resolution_v1',
        scientific_review=dict(CI0='PASS',CI1='PASS_bounded_complete_anchor',PC1='PASS_bounded_source_and_support'),
        reviewed_record_digest='70386c47cc86d29f14fe69b2e6c80ebafb0cb1bd00dc4b2a7c28bff3ecbf2ac1',
        reviewed_profile_digest='88620d22a0a3663f76d51ecfb79249cedde397dd94a6a058cd3a06ad7f27c97b',
        provenance_disposition='resolved_against_accepted_relocated_G7_bindings',
        accepted_repository_commit='5e1a63a',inherited_kernel_bindings=sorted(checked,key=lambda b:b['path']),
        external_old_versions='two quoted old prefixes cannot be reconstructed from path changes alone; exact external files not available',
        review_scope='reviewer dense-solver and finite-pressure results retained as report, not new local runs',
        hardening='exact-rational charge/pairing/star/symmetry admission before interval conversion; constructive derived witnesses',
        boundary_refresh='working-note source binding only; retained numerical cases unchanged, no owner rerun',
        formal_adjudication_pending=True,graph_admitted=False,local_debt_discharge=False,native_authority=False)
    value['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                              for p in sorted(paths)]+value['inherited_kernel_bindings']
    value['record_digest']=r.a.digest(value)
    return value


def read_evidence(value):
    return dict(selected_joint_read_digest=r.a.digest(r.a.encode(value)),
        H=value['H'],current=value['read']['current'],
        certificate_kind=value['certificate']['kind'],
        certificate_digest=r.a.digest(r.a.encode(value['certificate'])),
        root_error=value.get('root_error'),iterations=value.get('iterations'),
        source_norm_upper=r.norm_upper(x for row in value['source'] for x in row))


def ci_anchor():
    before,reset=r.fixtures()
    initial=r.ci_read('paired_source',before)
    reset_root=r.ci_read('paired_source',reset)
    r.require(r.source_check(before,F(29,10)).hi<3*r.GRID,'guard inactive before ordinary beat')
    after=r.advance('paired_source',before,initial)
    event_root=r.ci_read('paired_source',after)
    chosen=r.event_select(after,event_root)
    roles={}
    for role,state in (('current',after),('reset',reset)):
        target=r.transfer(state,chosen['k'])
        root=r.ci_read('paired_target',target)
        following=r.advance('paired_target',target,root)
        final_root=r.ci_read('paired_target',following)
        radius=r.norm_upper(c-F(3,2) for c in following.C)
        r.require(radius<F(2,3),'both-role first target step enters return domain')
        roles[role]=dict(transferred=target.payload(),root=read_evidence(root),
            first_step=following.payload(),restart=read_evidence(final_root),return_radius_upper=radius,
            old_edge_W_preserved=True,new_bridge_W=1,exact_charge_conservation='incidence/linear split identity')
    controls={}
    for label,state in (('no_split',after),('W_reset_only',r.reset_history(after))):
        r.source_check(state)
        root=r.ci_read('paired_source',state)
        controls[label]=dict(root=read_evidence(root),source_cone=True,failure_by_further_proposals=67,
                            evidence='uniform evolving-history growth theorem, not a fitted trajectory')
    return dict(status='bounded_causal_anchor_independently_reviewed_PASS',before=before.payload(),
        reset=reset.payload(),initial_root=read_evidence(initial),reset_root=read_evidence(reset_root),postbeat=after.payload(),
        poststate_root=read_evidence(event_root),choice=chosen,roles=roles,controls=controls,
        ordinary_onset_from_inactive_guard=True,source_only_selection=True,
        operation_support='star parent split changes the obstructing stiffness; source 5m>a, target lambda<=73/16<a')


def pc_anchor():
    before,reset=r.fixtures()
    Z=r.diagonal_z(F(1,16384));resetZ=r.diagonal_z(F(1,24576))
    reset_read=r.pc_read(reset,resetZ)
    r.require(r.source_check(before,F(29,10)).hi<3*r.GRID,'PC obstruction threshold initially inactive')
    after,Zn,selected,restart=r.pc_step(before,Z)
    r.source_check(after)
    r.require(any(x.hi<y.lo or y.hi<x.lo for row,other in zip(Z.values,Zn.values) for x,y in zip(row,other)),
              'carrier evolution is not suppressed')
    # e0/e2 share the old parent; after binary fission they no longer meet.
    r.require(Zn.values[0][2].lo>0,'nonzero cross-sector carrier component')
    target=r.p.TARGET
    r.require(not set(target[0]) & set(target[2]),'naive old-array embedding violates target star support')
    controls={}
    for name,state,carrier in (
        ('no_split',after,Zn),('W_reset_only',r.reset_history(after),Zn),
        ('Z_reset_only',after,r.diagonal_z(F(0))),
        ('both_reset',r.reset_history(after),r.diagonal_z(F(0)))):
        r.source_check(state);read=r.pc_read(state,carrier)
        controls[name]=dict(read=read_evidence(read),source_cone=True,failure_by_further_proposals=67,
                           evidence='uniform W/Z invariant-cone theorem')
    return dict(status='bounded_source_and_support_independently_reviewed_PASS',
        before=before.payload(),Z_before=Z.values,reset=reset.payload(),reset_Z=resetZ.values,
        reset_read=read_evidence(reset_read),selected=read_evidence(selected),held_source=selected['source'],
        postbeat=after.payload(),Z_postbeat=Zn.values,
        event_read=read_evidence(restart),controls=controls,ordinary_entry_into_obstruction_cone=True,
        exact_decorated_pair_sectors=True,carrier_radius=r.Z_RADIUS,
        tau_PC='1/(8 log 2)',held_source_writer_coefficient=F(1,2),
        nontransportable_naive_cross_sector_entry=Zn.values[0][2],
        carrier_event_law_selected=False,target_restoration_claimed=False,
        operation_support='the resource/stiffness obstruction persists uniformly in the carrier ball; splitting changes that support')


def run():
    resolution=review_resolution()
    retained=json.loads((ROOT/INV/'evidence/atc-ci-pc/CI1PC1ReviewResolution.json').read_text())
    r.require(retained==resolution,'review resolution must match current inherited bindings')
    bounds=r.dynamical_bounds()
    # Recheck the inherited exact incidence/spectral lemmas, not OS dynamics.
    algebra=r.a.mathref.algebra_checks()
    ci=ci_anchor();pc=pc_anchor()
    result=r.a.encode(dict(schema='grcv4_atc_ci_pc_anchor_v1',
        status='CI1_PC1_review_PASS_hardened_successor_pending_scoped_adjudication',
        review_resolution_digest=resolution['record_digest'],
        scientific_acceptance=False,graph_admitted=False,native_ATC_executed=False,
        ATC2_closed=False,profile=dict(schema='atc_ci_pc_fixed_anchor_profile_v1',
            candidate='A',realizations=['CI','PC'],params=dict(r.a.PARAMS),
            fixed_geometry_reference_profile=r.a.PROFILE_ID,
            site_law='p(c)=(19/4)c+c^2/131072',zeta_A=1,eta=1,kappa_c=1,W_floor=F(1,2),
            h=r.H,tau_A='1/(8 log 2)',tau_PC='1/(8 log 2)',
            CI_geometry_radius=r.RHO,PC_carrier_radius=r.Z_RADIUS,
            graphs={k:v for k,v in r.a.profile_payload()['graphs'].items() if k.startswith('paired_')},
            native_authority=False),
        interval_encoding='outward integer endpoints divided by 2**256',
        uniform_bounds=bounds,algebra=algebra,CI_1=ci,PC_1=pc,
        claim_updates=[
            dict(claim_id='ATC-CI-CHAIN-01',claim_class='conditional',
                 status='review_PASS_bounded_result_pending_adjudication',profile_scope=['A_CI'],
                 evidence_pointer='/CI_1',
                 debt_refs=['ATC7-DB-'+n for n in ('02','05','06','07','08','14','16','19','26')],
                 local_debt_discharge=False,native_authority=False),
            dict(claim_id='ATC-PC-CHAIN-01',claim_class='conditional',
                 status='review_PASS_source_result_carrier_policy_and_restoration_separate',profile_scope=['A_PC'],
                 evidence_pointer='/PC_1',
                 debt_refs=['ATC7-DB-'+n for n in ('02','07','08','13','15','14','16','19','26')],
                 open_front=['ATC7-DB-15','ATC7-DB-14','ATC7-DB-16','ATC7-DB-19'],
                 local_debt_discharge=False,native_authority=False)],source_bindings=[]))
    paths={Path(__file__).resolve(),ROOT/INV/'research/atc_ci_pc_anchor.py',
           ROOT/INV/'decisions/ATCCIPCRealizationNativeProgram.md',
           ROOT/INV/'evidence/atc-ci-pc/CI1PC1ReviewResolution.json',
           ROOT/INV/'evidence/atc-ci-pc/ATCCIPCStepBoundaryAudit.json'}
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix=='.py':paths.add(path)
    for name in ('ATCSectorStateDomain.md','ATCSectorChannelsAndRequests.md',
                 'ATCSectorReferenceAdjudication.md'):
        paths.add(ROOT/INV/'decisions'/name)
    result['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),
                                  sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
    result['profile_digest']=r.a.digest(result['profile'])
    numerics={k:numerical_projection(result[k]) for k in ('uniform_bounds','algebra','CI_1','PC_1')}
    numerical_digest=r.a.digest(numerics)
    r.require(numerical_digest==REVIEWED_NUMERICS_SHA256,'reviewed mathematical payload changed')
    result['reviewed_numerical_regression']=dict(passed=True,digest=numerical_digest,
        reviewed_record_digest=resolution['reviewed_record_digest'],
        excluded_fields=['status','selected_joint_read_digest'])
    result['record_digest']=r.a.digest(result)
    return result


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
