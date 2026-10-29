"""C_CI+PC worker policy and a small, source-bound native root preflight."""
import argparse
from contextlib import contextmanager
import cProfile
import json
import pstats
import time
import unittest
from unittest.mock import patch

import p984b_ccipc_runtime as r
from p9_cpc_compute import worker as arithmetic
from p9_cpc_covariance_compute import wire_reuse,LIMITS,cache as wire_cache
from p984h_cpc import measure_reuse

b=r.b
SELF=b.HERE+'p9_ccipc_compute.py'
PREFLIGHT=b.BASE+'P9-CCIPC-ComputePreflight.json'
LARGE_CAP_SECONDS=3600


@contextmanager
def worker():
    with arithmetic() as policy,wire_reuse() as wire:
        yield dict(policy,family='C_CI_PC',large_cap_seconds=LARGE_CAP_SECONDS,
                   serialization_reuse=wire)


def preflight():
    import test_p9_cpc_wire_reuse as tests
    from pygrc.models.grc_v4_numerics import MatrixReuse,matrix_operation
    paths={SELF,r.SELF,r.INPUTS,b.HERE+'p9_cpc_compute.py',
        b.HERE+'p9_cpc_covariance_compute.py',b.HERE+'p9_cpc_wire_reuse.py',
        b.HERE+'test_p9_cpc_wire_reuse.py',b.HERE+'p984h_validation_reuse.py',
        b.HERE+'p984h_cpc.py',b.HERE+'p984b_cci_runtime.py'}
    registrations={'grc_9_v4_api_lifecycle.py','grc_9_v4_legacy.py','grc_9_v4_owner.py'}
    paths|={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src/pygrc/models').glob('grc*v4*.py')
            if p.name not in registrations}
    refs=b.bind(paths);rows=[];expected=None
    with patch.multiple(wire_cache,**LIMITS):
        tested=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    b.require(tested.wasSuccessful() and tested.testsRun==4,'canonical-byte cache regressions')
    inputs=b.read(r.INPUTS)['initial_inputs']
    for label,policy in (('fresh',MatrixReuse.FRESH),('reuse',MatrixReuse.AUTOMATIC)):
        profiler=cProfile.Profile();start=time.monotonic()
        with worker() as active,matrix_operation(reuse=policy),measure_reuse() as cache:
            active=dict(active,matrix_reuse='fresh_control' if label=='fresh' else 'automatic_exact_operands')
            before=b.GeometryStageInputs.from_payload(inputs)
            profiler.enable();root=r.CandidateCIRoot(before);profiler.disable()
            captured=r.capture_root(root)
            digest=b.digest(captured)
            if expected is None:expected=digest
            b.require(digest==expected,'native root/cache byte parity failed')
        top=sorted(pstats.Stats(profiler).stats.items(),key=lambda row:row[1][3],reverse=True)[:20]
        row=dict(policy=label,seconds=time.monotonic()-start,root_digest=digest,
            evaluations=root.evaluations,cache=cache,execution_policy=active,
            profile=[dict(file=key[0].split('/graph-reflexive-coherence/')[-1],line=key[1],
                function=key[2],calls=value[1],own_seconds=value[2],cumulative_seconds=value[3])
                for key,value in top])
        rows.append(row)
        print(json.dumps({k:row[k] for k in ('policy','seconds','evaluations','cache')}),flush=True)
    b.require(rows[1]['cache']['solve_hits']>0 and rows[1]['cache']['fact_hits']>0,'native matrix reuse absent')
    b.require(all(row['execution_policy']['serialization_reuse']['retained_bytes']==0 for row in rows),'wire cache leaked')
    b.check_bindings(refs)
    value=b.seal(dict(schema='p9-ccipc-compute-preflight-v1',family='C_CI_PC',outcome='passed',
        source_bindings=refs,cache_tests=4,small_root_byte_parity=True,measurements=rows,
        large_cap_seconds=LARGE_CAP_SECONDS,native_roots=2,native_steps=0,native_events=0,
        campaign_credit=False,user_accepted=False,aggregate_closed=False))
    b.write_new(PREFLIGHT,value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('preflight',));parser.parse_args()
    preflight()
