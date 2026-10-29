"""Exact-policy matrix/schema/byte reuse for the small public integration runs."""
from contextlib import contextmanager
import time

import p984b_ccipc_runtime as r
from p984h_cpc import measure_reuse
from p984h_validation_reuse import validation_reuse
from p9_cpc_covariance_compute import wire_reuse
from pygrc.models.grc_v4_numerics import (
    ExactBackend, NumericalPolicy, MatrixReuse, exact_backend, numerical_policy, matrix_operation,
)

b=r.b
SELF=b.HERE+'p9_ccipc_integration_compute.py'
PREFLIGHT=b.BASE+'P9-CCIPC-IntegrationComputePreflight.json'


@contextmanager
def worker(reuse=MatrixReuse.AUTOMATIC):
    with validation_reuse(),wire_reuse() as wire,exact_backend(ExactBackend.FLINT), \
         numerical_policy(NumericalPolicy.LEGACY_EXACT),matrix_operation(reuse=reuse),measure_reuse() as matrix:
        yield dict(exact_backend='flint',numerical_policy='legacy_exact_v1',
                   matrix_reuse='automatic_exact_operands' if reuse is MatrixReuse.AUTOMATIC else 'fresh_control',
                   matrix=matrix,serialization=wire)


def preflight():
    old=b.read(r.INPUTS);expected=None;rows=[]
    paths={SELF,r.INPUTS,r.SELF,b.HERE+'p984h_cpc.py',b.HERE+'p984h_validation_reuse.py',
           b.HERE+'p9_cpc_covariance_compute.py',b.HERE+'p9_cpc_wire_reuse.py'}
    paths|={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src/pygrc/models').glob('grc*v4*.py')}
    refs=b.bind(paths)
    for mode in (MatrixReuse.FRESH,MatrixReuse.AUTOMATIC):
        start=time.monotonic()
        with worker(mode) as policy:
            seed=r.state(old['expected_source']);owner=r.native.GRC9V4CCIPCOperation(seed)
            result=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(old['cases'][0]['request']))
            b.require(result.committed,'integration compute preflight event')
            raw=owner.checkpoint()
            if expected is None:expected=raw
            b.require(raw==expected,'exact-policy checkpoint byte parity')
        rows.append(dict(seconds=time.monotonic()-start,policy=policy,checkpoint_sha256=b.sha(raw)))
        print(mode.value,rows[-1]['seconds'],policy['matrix'],flush=True)
    # Legacy exact solves consume cached inverses/facts; certified solves use
    # the separate solve memo. A zero solve-lookup count is expected here.
    b.require(rows[1]['policy']['matrix']['fact_hits']>0,
              'exact-policy reuse absent')
    b.check_bindings(refs)
    value=b.seal(dict(schema='p9-ccipc-integration-compute-preflight-v1',outcome='passed',
        source_bindings=refs,native_checkpoint_byte_parity=True,measurements=rows,
        campaign_credit=False,user_accepted=False))
    b.write_new(PREFLIGHT,value)


if __name__=='__main__':preflight()
