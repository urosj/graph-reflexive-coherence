"""Bounded metadata-only profile; retained native profiles supply numerical costs."""
from collections import OrderedDict
from contextlib import ExitStack
from copy import deepcopy
import json
import lzma
import sys
from time import perf_counter
from unittest.mock import patch
import p986_first_group as h
from pygrc.models import grc_v4_codec as codec
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from p984h_validation_reuse import validation_reuse

RESULT=h.BASE+'P9-Tranche8-FirstGroupPerformance.json'
SELF=h.HERE+'tranche8_end_performance.py'
PLAN=h.BASE+'P9-Tranche8-FirstGroupEndReview.md'


def measured(call):
    start=perf_counter(); value=call(); return value,perf_counter()-start


def profile(call):
    counters={}
    def timed(label,original):
        def invoke(*args,**kwargs):
            start=perf_counter()
            try:return original(*args,**kwargs)
            finally:
                row=counters.setdefault(label,dict(calls=0,inclusive_seconds=0.0))
                row['calls']+=1;row['inclusive_seconds']+=perf_counter()-start
        return invoke
    with ExitStack() as stack:
        for module,name,label in ((h.handoff,'authenticate','source_authentication'),
                (lzma,'decompress','decompression'),(h,'canonical_json_bytes','checkpoint_canonicalization'),
                (json,'loads','json_decode'),(json,'dumps','json_encode')):
            stack.enter_context(patch.object(module,name,timed(label,getattr(module,name))))
        value,elapsed=measured(call)
    return value,dict(wall_seconds=elapsed,components=counters,
                     inclusive_times_overlap=True,profiled_call=True,
                     instrumentation='coarse call timers; no scalar/function tracing')


def run():
    refs={}
    def read(path):
        raw=h.safe(h.ROOT,path).read_bytes();refs[path]=h.handoff.reference(h.ROOT,path)
        return json.loads(lzma.decompress(raw) if path.endswith('.xz') else raw)
    small=read(h.BASE+'P9-8.3C-CI-Validation.json')['numerical_observations']['checkpoint']
    large=read(h.BASE+'P9-8.4h-APC-event.json.xz')['execution']['checkpoint']
    observations=[]
    for size,checkpoint in [('small_C_CI',small),('large_A_PC',large)]:
        for state in ('initial','state'):
            reference=checkpoint[state]['inputs']['reference']
            subjects=[('port_graph',reference['graph']),('K4',dict(schema_version='grcv4-k4-identity-v1',K4_base=reference['K4_base']))]
            for kind,payload in subjects:
                if state == 'state' and kind == 'K4':continue  # graph pre/post, K4 once per size
                row=dict(size=size,state=state,kind=kind,canonical_bytes=len(codec.canonical_json_bytes(payload)),modes={})
                ids=[]
                for mode in ('fresh','default','worker_8x4MiB'):
                    with ExitStack() as stack:
                        if mode=='worker_8x4MiB':stack.enter_context(validation_reuse())
                        else:
                            stack.enter_context(patch.object(codec,'_VALIDATED_PAYLOADS',OrderedDict()))
                            if mode=='fresh':stack.enter_context(patch.object(codec,'_VALIDATION_MAX_BYTES',0))
                        def call():
                            if kind=='K4':return codec.payload_identity('k4_identity_payload',payload)
                            graph=GRC9V4PortGraph.from_payload(payload)
                            return graph.to_envelope()
                        first,cold=measured(call);second,warm=measured(call)
                        h.require(first==second,'warm result drift');ids.append(first)
                        print(size,state,kind,mode,round(cold,3),round(warm,3),flush=True)
                        row['modes'][mode]=dict(first_seconds=cold,repeat_seconds=warm,
                            memo_entries=len(codec._VALIDATED_PAYLOADS))
                h.require(ids[0]==ids[1]==ids[2],'cache mode output drift')
                row['identity']=ids[0] if kind=='K4' else ids[0]['graph_digest']
                row['all_modes_identical']=True;observations.append(row)
    pressure=[]
    for mode in ('fresh','worker_8x4MiB'):
        with ExitStack() as stack:
            stack.enter_context(validation_reuse())
            if mode=='fresh':stack.enter_context(patch.object(codec,'_VALIDATION_MAX_BYTES',0))
            payload=dict(schema_version='grcv4-k4-identity-v1',K4_base=deepcopy(small['state']['inputs']['reference']['K4_base']))
            old=codec.payload_identity('k4_identity_payload',payload)
            changed=deepcopy(payload);changed['K4_base'][0][0]+=1
            h.require(codec.payload_identity('k4_identity_payload',changed)!=old,'changed content reused')
            changed['K4_base'][0][0]=True
            try:codec.payload_identity('k4_identity_payload',changed)
            except codec.V4SchemaError:rejected=True
            else:rejected=False
            h.require(rejected,'invalid changed content admitted')
            pressure.append(dict(mode=mode,changed_key_distinguished=True,invalid_boolean_rejected=True))
    sys.path.insert(0,str(h.ROOT/h.handoff.SIDE/'tool/src'))
    from grcv4_explorer.tranche8 import tranche8_status,tranche8_source
    print('status measurement',flush=True)
    first,first_profile=profile(lambda:tranche8_status(h.ROOT,family='first_group',checkpoint='8.6'))
    second,warm=measured(lambda:tranche8_status(h.ROOT,family='first_group',checkpoint='8.6'))
    h.require(first==second,'status warm result drift')
    name='src/pygrc/models/grc_v4_lifecycle.py'
    (raw,ref),source_profile=profile(lambda:tranche8_source(h.ROOT,name,family='A_PC',checkpoint='8.6'))
    h.require(h.sha(raw)==ref['sha256'],'retrieved source drift')
    native=read(h.BASE+'P9-8.4h-COSSolveReuse.json.xz')
    scalar=read(h.BASE+'P9-8.4h-COSScalarReuse.json.xz')
    grids=[]
    for name in ('grid_transport_a_primitive_reuse_comparison.json','grid_transport_matrix_reuse_comparison.json'):
        value=read('implementation/evidence/grcv4-performance/'+name)
        grids.append(dict(path='implementation/evidence/grcv4-performance/'+name,
            scope='historical generic grid comparison, not a GRC9V4 timing claim',
            grid=value.get('grid'),method=value.get('method'),comparisons=value.get('comparisons')))
    for name in (SELF,PLAN,h.HERE+'p984h_validation_reuse.py',
                 h.HERE+'test_p984h_validation_reuse.py','src/pygrc/models/grc_v4_codec.py',
                 'src/pygrc/models/grc_9_v4_topology.py',h.HERE+'p986_acceptance.py',
                 h.HERE+'tranche8_evidence.py',h.handoff.SIDE+'tool/src/grcv4_explorer/tranche8.py'):
        refs[name]=h.handoff.reference(h.ROOT,name)
    return h.seal(dict(schema='tranche8-first-group-performance-review-v1',date='2026-10-27',
        families=list(h.FAMILIES),new_native_steps=0,new_native_events=0,new_cache_implementation=False,
        metadata_measurements=observations,pressure=pressure,
        status=dict(first=first_profile,repeat_wall_seconds=warm,identical=True,
                    meaning='fresh process-local first call versus warm repeat; no status-result cache',source=source_profile),
        retained_native=dict(scope=native['scope'],baseline_seconds=native['baseline_elapsed_seconds'],
            comparisons=[{k:r[k] for k in ('name','elapsed_seconds','baseline_parity','scientific_view_digest')} for r in native['records']],
            scalar_seconds=scalar['elapsed_seconds'],scalar_baseline_parity=scalar['baseline_parity']),
        generic_grid_comparisons=grids,source_refs=list(refs.values()),
        disposition='No new cache. Preserve exact operation-local numerical facts and explicit research-only schema memo. Public integrated-operation tuning belongs with Tranche 9 callers; read-only source authentication remains fresh.'))


if __name__=='__main__':
    h.write(RESULT,run())
    print('Bounded metadata performance review recorded; no native trajectories')
