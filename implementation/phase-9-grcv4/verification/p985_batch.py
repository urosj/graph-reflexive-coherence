"""Independent remaining-first-group lifecycle workers, with compact results."""
import argparse
from contextlib import ExitStack
import importlib
import json
import lzma
import os
from pathlib import Path
import signal
import sys
import time
import unittest
from unittest.mock import patch

import p985_cos as common
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_numerics import ExactBackend, NumericalPolicy, exact_backend, numerical_policy, matrix_operation
from p984h_validation_reuse import validation_reuse

ROOT,BASE,HERE,SIDE=common.ROOT,common.BASE,common.HERE,common.SIDE
require,seal,sha,safe=common.require,common.seal,common.sha,common.safe
FAMILIES=('C_CI','A_CI','A_PC')
TAGS=dict(zip(FAMILIES,('CCI','ACI','APC')))
CAPS=dict(small=600,large=3600)
CASES=('request_boundaries','domain_and_history','atomicity','replay','readmission_no_writers','continuation_reset')
SELF=HERE+'p985_batch.py';TEST=HERE+'test_p985_batch.py'
PLAN=BASE+'P9-8.5-RemainingFirstGroupPlan.md'
OBSERVATIONS={}


def path(family,kind):
    require(family in FAMILIES and kind in ('inputs','small','large','review'),'unknown family/segment')
    return BASE+'P9-8.5-'+TAGS[family]+'-'+kind+('.md' if kind=='review' else '.json')


def event_path(family):return BASE+'P9-8.4h-'+TAGS[family]+'-event.json.xz'


def fixture_module(family):return importlib.import_module('tests.models.test_grc_9_v4_'+TAGS[family].lower())


def operation(family):return getattr(native,'GRC9V4'+TAGS[family]+'Operation')


def digest(value):return sha(canonical_json_bytes(value))


def manifest(family,root=ROOT):
    require(family in FAMILIES,'unselected family')
    root=Path(root);module=fixture_module(family)
    names={SELF,TEST,PLAN,common.SELF,HERE+'test_p985_fixed_row_owner.py',HERE+'p984h_validation_reuse.py',HERE+'p984i_first_group.py',
           common.HANDOFF,common.INPUTS,common.result_path('small'),BASE+'P9-8.5-COSAcceptance.json',event_path(family)}
    if hasattr(module,'RECORD'):names.add(str(module.RECORD.relative_to(ROOT)))
    for pattern in ('src/pygrc/models/grc_v4*.py','src/pygrc/models/grc_9_v4*.py',
                    'src/pygrc/models/_grc_v4*.py','tests/models/test_grc_v4*.py',
                    'tests/models/test_grc_9_v4*.py','specs/grc*v4*.json'):
        names.update(str(p.relative_to(root)) for p in root.glob(pattern))
    # Exact fixture import dependencies, without running their numerical campaigns.
    for loaded in list(sys.modules.values()):
        filename=getattr(loaded,'__file__',None)
        if filename:
            try:rel=Path(filename).resolve().relative_to(ROOT)
            except ValueError:continue
            if str(rel).startswith(HERE) and rel.suffix=='.py' and rel.name not in ('test_p985_batch_surfaces.py','p985_status.py'):
                names.add(str(rel))
    return seal(dict(schema='p985-family-inputs-v1',family=family,cases=list(CASES),caps=CAPS,
        source_bindings={n:sha(safe(root,n).read_bytes()) for n in sorted(names)},
        exact_backend='flint',small_policy='legacy_exact_v1',large_policy='certified_arb_256_weighted_v1',
        public_specialization_facade=False,max_workers=3,threads_per_worker=1,
        shared_reuse=dict(self_loop=common.result_path('small'),acceptance=BASE+'P9-8.5-COSAcceptance.json'),
        raw_budget_per_result=150000))


def scope(segment):
    stack=ExitStack();stack.enter_context(exact_backend(ExactBackend.FLINT))
    stack.enter_context(numerical_policy(NumericalPolicy.LEGACY_EXACT if segment=='small' else NumericalPolicy.CERTIFIED_ARB_256))
    stack.enter_context(validation_reuse())
    if segment=='large':stack.enter_context(matrix_operation())
    return stack


def point_summary(root):
    selected=root.selected
    value=dict(J=list(root.current.values),H=selected.inputs.geometry.one_form_hodge.matrix,
        generated=selected.generated.one_form_hodge.matrix,source=selected.structural_source.increment,
        certificate=root.certificate.bounds.to_dict(),
        domain_id=root.inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
        recipe_identity=root.identity)
    return dict(kind='joint_CI_root',joint_digest=digest(value),J_digest=digest(value['J']),
        H_digest=digest(value['H']),certificate_digest=digest(value['certificate']),domain_id=value['domain_id'],
        recipe_identity=root.identity)


def pc_summary(read):
    point=read.point
    value=dict(inputs=point.inputs.to_payload(),J=list(point.current.values),
        H=point.inputs.geometry.one_form_hodge.matrix,source=read.structural_source.increment)
    return dict(kind='fixed_carrier_PC_point',point_digest=digest(value),J_digest=digest(value['J']),H_digest=digest(value['H']))


def large(family):
    original=json.loads(lzma.decompress((ROOT/event_path(family)).read_bytes()))
    require(original==seal(original) and original['outcome']=='completed','event integrity')
    cp=original['execution']['checkpoint'];raw=canonical_json_bytes(cp)
    reads=[];probes=[];read_name='_'+TAGS[family].lower()+'_readmit'
    real_read=getattr(native,read_name)
    def observed(s):
        before=digest(s.to_payload());start=time.monotonic()
        print(f'{family}: readmission {len(reads)+1} started',flush=True)
        result=real_read(s)
        require(digest(s.to_payload())==before,'readmission mutated scientific state')
        reads.append(dict(scientific_digest=s.scientific_digest,reset_digest=s.reset_digest,roles=['current','reset']))
        print(f'{family}: readmission {len(reads)} passed ({time.monotonic()-start:.1f}s)',flush=True)
        return result
    probe_name='ProvisionalCandidatePCStep' if family=='A_PC' else 'ProvisionalCandidateCIStep'
    real_probe=getattr(native,probe_name)
    def observed_probe(before,*args,**kwargs):
        require(before.dt==0,'event must not advance physical time')
        result=real_probe(before,*args,**kwargs)
        if family=='A_PC':pair=[pc_summary(result.read),pc_summary(result.reset_read)]
        else:pair=[point_summary(result.root),point_summary(result.reset_root)]
        probes.append(dict(current=pair[0],reset=pair[1]));return result
    with patch.object(native,read_name,observed),patch.object(native,probe_name,observed_probe):
        restored=operation(family).replay(raw)
    require(restored.checkpoint()==raw,'native replay must reproduce original bytes')
    require(len(reads)==len(probes)==3 and reads[0]==reads[1] and probes[0]==probes[1],
        'source root/point reconstruction differs')
    require(reads[-1]['scientific_digest']==cp['state']['scientific_digest'],'target subject')
    require(len(restored.receipts)==4 and len(cp['reference_currents'])==1,'receipt/reference coverage')
    archives=cp.get('carrier_archives',[])
    require(len(archives)==int(family=='A_PC'),'carrier archive scope')
    return dict(checkpoint_sha256=sha(raw),event_record_digest=original['record_digest'],
        event_id=original['execution']['event_id'],checkpoint_exact=True,
        **common.occupancy(restored.state.inputs.geometry.reference.graph.port_graph),
        readmissions=reads,selected_points=probes,receipt_count=4,reference_current_records=1,
        archive_count=len(archives),archive_digest=digest(archives),
        lifecycle_digest=cp['lifecycle_digest'],fresh_native_events=1,fresh_ordinary_steps=0)


def run(family,segment):
    m=json.loads((ROOT/path(family,'inputs')).read_text())
    require(m==manifest(family),'execution source drift')
    require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single-thread worker required')
    destination=ROOT/path(family,segment);require(not destination.exists(),'refuse to overwrite retained results')
    def timeout(*_):raise TimeoutError(f'{family} {segment} cap exceeded')
    old=signal.signal(signal.SIGALRM,timeout);signal.alarm(CAPS[segment]);started=time.monotonic()
    try:
        with scope(segment):
            if segment=='large':observations=large(family)
            else:
                import test_p985_batch as tests
                cls=type('Lifecycle_'+TAGS[family],(tests.FamilyLifecycleTests,),{'FAMILY':family})
                OBSERVATIONS.clear()
                result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
                require(result.wasSuccessful() and result.testsRun==len(CASES) and not result.skipped,'family small suite failed')
                require(set(OBSERVATIONS)==set(CASES),'missing small observations')
                observations=dict(tests=result.testsRun,cases=dict(OBSERVATIONS),shared_self_loop=common.result_path('small'))
        value=seal(dict(schema='p985-family-execution-v1',family=family,segment=segment,
            manifest_digest=m['record_digest'],outcome='passed',observations=observations,
            elapsed_seconds=time.monotonic()-started,user_accepted=False,aggregate_closed=False,
            public_specialization_facade=False,new_G2_support=[],G3_accepted=False))
        raw=(json.dumps(value,indent=2)+'\n').encode();require(len(raw)<=m['raw_budget_per_result'],'evidence budget')
        destination.write_bytes(raw);print(f'{family} {segment} PASS {value["elapsed_seconds"]:.2f}s',flush=True)
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,old)


def check(family,root=ROOT):
    root=Path(root);m=json.loads((root/path(family,'inputs')).read_text())
    require(m==seal(m) and m['family']==family and m['cases']==list(CASES) and m['caps']==CAPS,'manifest scope')
    required={SELF,TEST,PLAN,common.SELF,event_path(family),common.result_path('small'),BASE+'P9-8.5-COSAcceptance.json'}
    require(required<=set(m['source_bindings']),'incomplete source roster')
    for n,v in m['source_bindings'].items():require(sha(safe(root,n).read_bytes())==v,'execution source drift: '+n)
    result={}
    for segment in CAPS:
        v=json.loads((root/path(family,segment)).read_text())
        require(v==seal(v) and v['manifest_digest']==m['record_digest'] and v['family']==family
            and v['segment']==segment and v['outcome']=='passed' and 0<=v['elapsed_seconds']<=CAPS[segment], 'execution integrity')
        require(not v['user_accepted'] and not v['aggregate_closed'] and not v['public_specialization_facade']
            and v['new_G2_support']==[] and not v['G3_accepted'],'scope widening')
        result[segment]=v
    small=result['small']['observations'];large_result=result['large']['observations']
    require(small['tests']==len(CASES) and set(small['cases'])==set(CASES)
        and all(v['passed'] for v in small['cases'].values()),'small coverage')
    c=small['cases'];require(c['atomicity']['late_publication_pointer_unchanged']
        and c['continuation_reset']['full_authority_restored'] and c['continuation_reset']['reset_rollback']
        and c['continuation_reset']['fresh_generic_ledger'] and not c['continuation_reset']['public_specialization_facade'],
        'lifecycle boundary')
    from test_p985_batch import METHODS
    for case,key in (('domain_and_history','domain'),('atomicity','atomic'),('replay','replay'),('readmission_no_writers','writers')):
        require(c[case]['methods']==METHODS[family][key],'family-specific pressure roster')
    require(c['request_boundaries']['codes']==['module_chirality_required','module_growth_phase_required',
        'reject_noncanonical_inactive_growth_phase'] and c['request_boundaries']['full_publication_rollback']
        and c['domain_and_history']['reset_only'] and c['continuation_reset']['native_steps']==c['continuation_reset']['native_resets']==1,
        'required failure/reset coverage')
    require(c['replay']['checkpoint_exact'] and c['replay']['archive_count']==int(family=='A_PC')
        and c['readmission_no_writers']['zero_temporal_writes'],'history/writer scope')
    event=json.loads(lzma.decompress((root/event_path(family)).read_bytes()));cp=event['execution']['checkpoint']
    require(large_result['checkpoint_sha256']==digest(cp) and large_result['event_record_digest']==event['record_digest']
        and large_result['event_id']==event['execution']['event_id'] and large_result['checkpoint_exact'], 'original checkpoint link')
    require((large_result['vertices'],large_result['edges'],large_result['occupied_ports'])==(107,407,814)
        and large_result['receipt_count']==4 and large_result['reference_current_records']==1
        and large_result['archive_count']==int(family=='A_PC') and large_result['archive_digest']==digest(cp.get('carrier_archives',[]))
        and large_result['lifecycle_digest']==cp['lifecycle_digest']
        and large_result['fresh_native_events']==1 and large_result['fresh_ordinary_steps']==0,'large coverage')
    reads,points=large_result['readmissions'],large_result['selected_points']
    require(len(reads)==len(points)==3 and reads[0]==reads[1] and points[0]==points[1]
        and reads[-1]['scientific_digest']==cp['state']['scientific_digest'],'readmission coverage')
    for pair in points:
        require(set(pair)=={'current','reset'},'both point roles required')
        for point in pair.values():
            require(point['kind']==('fixed_carrier_PC_point' if family=='A_PC' else 'joint_CI_root'),'point type')
            fields=('point_digest','J_digest','H_digest') if family=='A_PC' else ('joint_digest','J_digest','H_digest','certificate_digest')
            require(all(len(point[k])==64 for k in fields),'incomplete point evidence')
    return m,result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run-small','run-large','check'))
    parser.add_argument('family',choices=FAMILIES);args=parser.parse_args()
    if args.action=='prepare':
        target=ROOT/path(args.family,'inputs');require(not target.exists(),'manifest already exists')
        target.write_text(json.dumps(manifest(args.family),indent=2)+'\n')
    elif args.action=='check':check(args.family);print(args.family+' retained PASS; no numerics')
    else:run(args.family,args.action[4:])


if __name__=='__main__':
    sys.modules['p985_batch']=sys.modules[__name__];main()
