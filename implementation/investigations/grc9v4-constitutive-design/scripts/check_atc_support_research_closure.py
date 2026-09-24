#!/usr/bin/env python3
"""Check retained closure evidence and allocation hardening; no campaign rerun."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'
REFS = INV/'evidence/autonomous-topology-change'
sys.path.insert(0,str(INV/'research'))
import atc_support as model
from atc_support_fission import checked_fixed_fission


def run():
    path = REFS/'ATCSupportLocalExperiment.json'
    old = json.loads(path.read_text())
    assert old['record_digest'] == '976d0d808ed1d95f329ca9128ace80b1d091d1ccf41f6a54e7639cbe3d4b0bc6'
    assert old['record_digest'] == model.digest({k:v for k,v in old.items() if k!='record_digest'})
    for row in old['source_bindings']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    assert old['tests']==dict(run=8,failures=0,errors=0)
    assert old['causal']['F_D_baseline_equal']
    assert old['causal']['F_observation']==old['causal']['D_observation']
    assert len(old['encounter_protocol']['cases'])==18
    for case in old['encounter_protocol']['cases']:
        assert case['F_D_equal'] and case['inside_box'] and case['energy_decreases']

    s = old['fission']['source']
    state = model.State(model.SOURCE_GRAPH,tuple(s['current']['C']),tuple(s['reset']['C']))
    prescription = old['fission']['unchanged_F2']['prescription']
    target,initializers = checked_fixed_fission(state,prescription)
    assert model.canonical(target.scientific_payload())==model.canonical(old['fission']['target'])
    assert model.canonical(initializers)==model.canonical(old['fission']['initializations'])
    rejections=[]
    for label,value in (
        ('wrong_sum',['1','1']),('wrong_split',['1','2']),('missing_entry',['3/2']),
        ('numeric_instead_of_canonical_strings',[1.5,1.5]),('null',None),
        ('equivalent_noncanonical_strings',['1.5','1.5'])):
        changed=deepcopy(prescription)
        changed['allocated_current']=value
        try:
            checked_fixed_fission(state,changed)
        except model.ResearchDomainError:
            rejections.append(label)
        else:
            raise AssertionError('inconsistent allocation accepted')
    changed=deepcopy(prescription)
    del changed['allocated_current']
    try:
        checked_fixed_fission(state,changed)
    except model.ResearchDomainError:
        rejections.append('absent_field')
    else:
        raise AssertionError('missing allocation accepted')

    paths=[Path(__file__).resolve(),INV/'research/atc_support_fission.py',INV/'research/atc_support.py',path]
    record=dict(schema='grcv4_atc_research_closure_checks_v1',status='passed',
        predecessor_experiment_digest=old['record_digest'],original_execution_preserved=True,
        allocation_interface='checked_fixed_fission; original full campaign driver remains a historical reproducer',
        valid_construction_matches_reviewed=True,rejected_allocations=rejections,
        ordinary_updates=0,production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
    record['record_digest']=model.digest(record)
    return record


if __name__=='__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))
