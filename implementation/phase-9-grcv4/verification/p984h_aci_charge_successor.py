"""Explicit retained-checker correction: use the frozen charge inequality.

Production numerics and all earlier execution records remain unchanged. This
runner resumes only the declared unfinished current-history suffix.
"""
import argparse
import json
from dataclasses import replace
from unittest.mock import patch
import p984h_aci_campaign as c
from p984g_cci_closure_check import pairwise

SELF=c.HERE+'p984h_aci_charge_successor.py'
TEST=c.HERE+'test_p984h_aci_charge_successor.py'
PLAN=c.BASE+'P9-8.4h-ACIChargeSuccessor.md'
INPUTS=c.BASE+'P9-8.4h-ACIChargeInputs.json'
ORIGINAL_MANIFEST=c.manifest


def manifest():
    old=ORIGINAL_MANIFEST()
    c.require(old==json.loads((c.ROOT/c.BASE/'P9-8.4h-ACICampaignInputs.json').read_text()),'original campaign drift')
    paths=set(old['source_bindings'])|{c.BASE+'P9-8.4h-ACICampaignInputs.json',SELF,TEST,PLAN}
    return c.seal(dict(schema='p984h-aci-charge-successor-inputs-v1',
        source_bindings={n:c.p.sha(n) for n in sorted(paths)},
        original_manifest_digest=old['record_digest'],caps=old['caps'],
        allowed_role='current',allowed_steps=[8,9,10],allowed_final_step=10,
        numerical_policy=old['numerical_policy'],exact_backend='flint',
        tolerance_changed=False,production_changed=False,automatic_retry=False,
        user_accepted=False,aggregate_closed=False))


def charge_fields(values,target,policy):
    actual=pairwise(values);delta=c.q(actual)-c.q(target)
    bound=c.q(policy.absolute_tolerance)+c.q(policy.relative_tolerance)*max(abs(c.q(target)),c.q(1))
    c.require(abs(delta)<=bound,'charge outside frozen profile inequality')
    return dict(target_charge=target,admitted_charge=actual,residual=float(delta))


def check_charge(e,before,after):
    expected=charge_fields(after.current.C,before.Q_target,before.geometry.reference.profile.params_resolved.charge)
    c.require(e['charge']==expected and e['exact_resource_sum_delta']==str(
        sum(map(c.q,after.current.C),c.q(0))-sum(map(c.q,before.current.C),c.q(0))),'charge receipt/stored-sum distinction')


def check_step(e,before):
    # Same scientific/lifecycle checks as the frozen campaign, with only its
    # extra zero-residual assertion replaced by the declared admission law.
    after=c.p.GeometryStageInputs.from_payload(e['next_inputs'])
    c.require(e['before_digest']==c.digest(before.to_payload()) and after.reset==before.reset and after.geometry==before.geometry
        and after.time==before.time+c.DT and after.step_index==before.step_index+1,'retained step lifecycle')
    for name,operand in (('current',before),('reset',replace(before,current=before.reset)),('final',replace(after,dt=0))):
        c.check_root(e['roots'][name],operand)
    expected=c.p.base.writer_oracle(c.subject(before),'current',after.current.C,e['roots']['current']['actual']['current'],c.DT)
    c.require(e['writer']==dict(C=list(after.current.C),W_A=list(before.current.W_A),J=e['roots']['current']['actual']['current'],
        descriptors=expected['descriptors'],drive=expected['drive'],written_W_A=expected['W_A'])
        and list(after.current.W_A)==expected['W_A'],'retained writer operands')
    resources=e['roots']['current']['oracle']['resources'];lower=min(c.q(r['lower']) for r in resources)
    c.require(lower>0 and str(lower)==e['minimum_exact_root_resource_lower']
        and list(after.current.C)==[r['represented'] for r in resources],'retained local sign/continuity')
    check_charge(e,before,after)
    c.require(e['reset_unchanged'] and e['detached_continuation'] and e['native_steps']==1 and e['native_events']==0,'step credit')
    return after


def run():
    # Explicit adapter; not a numerical-policy switch or failure-triggered retry.
    with patch.object(c,'manifest',manifest),patch.object(c,'INPUTS',INPUTS),patch.object(c,'check_step',check_step):
        for step in (8,9,10):c.run('step','current',step)
        c.run('final','current',10)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run'));args=parser.parse_args()
    if args.action=='prepare':
        with (c.ROOT/INPUTS).open('x') as stream:json.dump(manifest(),stream,indent=2);stream.write('\n')
    else:run()
