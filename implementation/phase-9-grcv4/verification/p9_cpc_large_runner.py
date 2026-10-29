"""Execute unchanged C_PC large segments with additional byte-exact JCS reuse."""
import argparse
import json
import time
import unittest
import p984h_cpc as n
from p9_cpc_wire_reuse import wire_reuse

b=n.b
SELF=b.HERE+'p9_cpc_large_runner.py'
CACHE=b.HERE+'p9_cpc_wire_reuse.py'
TEST=b.HERE+'test_p9_cpc_wire_reuse.py'
PREFLIGHT=b.BASE+'P9-CPC-WirePreflight.json'


def bindings():
    value=n.g.storage.read(PREFLIGHT);b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(value['outcome']=='passed' and value['tests']==4 and value['native_checkpoint_byte_parity']
        and value['runtime_producer_changed'] is False,'serialization preflight')
    return b.bind({SELF,CACHE,TEST,PREFLIGHT})


def child(pipe,segment,role,index):
    try:
        with wire_reuse() as stats,n.compute_worker() as policy:
            pipe.send(('progress',segment+'/'+role+'/'+str(index)+' verified FLINT/Arb/matrix/schema/JCS reuse'))
            value=n.execute(segment,role,index)
            b.require(stats['hits']>0,'large execution did not reuse canonical bytes')
        pipe.send(('result',dict(execution=value,compute_policy=policy,serialization_reuse=stats)))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


def run(segment,role,index):
    m=n.g.storage.read(n.INPUTS);n.check_manifest(m);refs=bindings();name=n.filename(segment,role,index)
    b.require(not (b.ROOT/name).exists(),'refuse overwrite')
    cap=m['caps']['event' if segment=='event' else 'final' if segment=='final' else 'step']
    value,seconds=n.process_budget.capped(child,(segment,role,index),cap)
    n.check_manifest(m);b.check_bindings(refs)
    record=b.seal(dict(schema='p984h-cpc-segment-v1',manifest_digest=m['record_digest'],segment=segment,
        role=role,index=index,**value,compute_bindings=refs,elapsed_seconds=seconds,outcome='completed',
        user_accepted=False,aggregate_closed=False))
    n.g.storage.save(name,record)
    print(json.dumps(dict(segment=segment,role=role,index=index,seconds=seconds,wire=value['serialization_reuse'])),flush=True)


def preflight():
    import test_p9_cpc_wire_reuse as tests
    start=time.monotonic()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    b.require(result.wasSuccessful() and result.testsRun==4 and not result.skipped,'wire memo tests')
    original=n.g.storage.read(n.r.INPUTS)
    with n.compute_worker():
        seed=n.r.state(original['expected_source'])
        request=n.GRC9V4ExpansionRequestInput.from_payload(original['cases'][0]['request'])
        owner=n.native.GRC9V4CPCOperation(seed);result=owner.expand(request)
        b.require(result.committed,'uncached parity event');plain=owner.checkpoint()
    with wire_reuse() as stats,n.compute_worker():
        owner=n.native.GRC9V4CPCOperation(seed);result=owner.expand(request)
        b.require(result.committed and owner.checkpoint()==plain,'byte-exact native checkpoint parity')
    value=b.seal(dict(schema='p9-cpc-wire-preflight-v1',outcome='passed',tests=4,
        source_bindings=b.bind({SELF,CACHE,TEST}),native_checkpoint_byte_parity=True,runtime_producer_changed=False,
        seconds=time.monotonic()-start,policy=dict(max_entries=16,total_bytes=64*1024*1024,max_payload_bytes=8*1024*1024),
        parity_cache=stats))
    n.g.storage.save(PREFLIGHT,value);print('native checkpoint byte parity passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--segment',choices=('source','prepared_target','event','step','final'))
    parser.add_argument('--role',choices=n.ROLES,default='current');parser.add_argument('--index',type=int,default=1)
    args=parser.parse_args()
    if args.preflight:preflight()
    else:run(args.segment,args.role,args.index)
