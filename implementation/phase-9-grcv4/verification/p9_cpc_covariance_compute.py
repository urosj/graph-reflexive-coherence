"""Bounded larger working set for C_PC covariance serialization.

Only capacity changes: exact-content keys, original RFC 8785 bytes, input
validation and the 8 MiB payload limit remain unchanged. Earlier executions
retain the original 16-entry / 64 MiB worker policy.
"""
from contextlib import contextmanager
import json
import time
import unittest
from unittest.mock import patch
import p9_cpc_large_runner as original
import p9_cpc_wire_reuse as cache

n=original.n;b=n.b
SELF=b.HERE+'p9_cpc_covariance_compute.py'
PREFLIGHT=b.BASE+'P9-CPC-CovarianceComputePreflight.json'
LIMITS=dict(MAX_ENTRIES=64,TOTAL_BYTES=128*1024*1024)


@contextmanager
def wire_reuse():
    active=cache._ACTIVE.get()
    if active is not None:
        b.require(active['max_entries']==LIMITS['MAX_ENTRIES']
            and active['total_byte_budget']==LIMITS['TOTAL_BYTES'],'mixed serialization capacities')
        yield active
        return
    with patch.multiple(cache,**LIMITS),cache.wire_reuse() as stats:yield stats


def bindings():
    v=n.g.storage.read(PREFLIGHT);b.check_digest(v);b.check_bindings(v['source_bindings'])
    b.require(v['outcome']=='passed' and v['tests']==4 and v['limits']==LIMITS
        and v['prepared_payload_parity'] and v['native_credit'] is False
        and v['expanded']['hits']>v['original']['hits']
        and v['expanded']['evictions']<v['original']['evictions']
        and v['expanded']['retained_bytes']==0,'covariance compute preflight')
    return b.bind({SELF,PREFLIGHT,*[r['path'] for r in original.bindings()]})


def preflight():
    import p984h_cpc_covariance as c
    import test_p9_cpc_wire_reuse as tests
    paths={SELF,c.SELF,c.maps.SELF,c.maps.ordering.SELF,c.maps.chart.SELF,n.INPUTS,
        n.filename('event'),n.filename('source'),*[r['path'] for r in original.bindings()]}
    paths|={r['path'] for r in n.g.storage.read(n.INPUTS)['source_bindings']}
    refs=b.bind(paths);started=time.monotonic();results={};timings={};expected=None
    with b.budget(900):
        with patch.multiple(cache,**LIMITS):
            result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
        b.require(result.wasSuccessful() and result.testsRun==4 and not result.skipped,'capacity regression tests')
        for label,context in (('original',cache.wire_reuse),('expanded',wire_reuse)):
            start=time.monotonic()
            with context() as stats,n.compute_worker():
                for _ in range(2):
                    c.subject.cache_clear();c.baseline.cache_clear();c.baseline_source.cache_clear()
                    seed,case,target=c.subject('combined')
                    digest=b.digest(dict(source=seed.to_payload(),case=case,target=target.to_payload()))
                    if expected is None:expected=digest
                    b.require(digest==expected,'prepared transport payload drift')
            results[label]=stats;timings[label]=time.monotonic()-start
            print(json.dumps(dict(capacity=label,seconds=timings[label],statistics=stats)),flush=True)
    b.require(results['expanded']['hits']>results['original']['hits']
        and results['expanded']['evictions']<results['original']['evictions'],'capacity did not improve actual reuse')
    b.check_bindings(refs)
    value=b.seal(dict(schema='p9-cpc-covariance-compute-preflight-v1',source_bindings=refs,
        limits=LIMITS,max_payload_bytes=cache.MAX_BYTES,tests=4,outcome='passed',native_credit=False,
        prepared_payload_parity=True,prepared_payload_digest=expected,runtime_producer_changed=False,
        seconds=time.monotonic()-started,cap_seconds=900,timings=timings,**results))
    n.g.storage.save(PREFLIGHT,value)


if __name__=='__main__':preflight()
