"""Retain thirty independent saved-input update enclosures without native reruns."""
import argparse
import time

import p9_ccipc_evidence as e
import p9_ccipc_execution_epoch as epoch
import p9_ccipc_large_charge as charge
import p984h_ccipc_covariance as covariance

b,n=e.b,e.n
SELF=b.HERE+'p9_ccipc_pointwise.py'
PATH=b.BASE+'P9-CCIPC-LargePointwiseErrors.json.xz'
PILOT=b.BASE+'P9-CCIPC-PointwiseSourcePilot.json'
LIMITS=dict(resource_error=2**-40,carrier_error=2**-48)
JOURNAL=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification/ccipc-pointwise'


def paths():
    return [*(charge.filename(s,r) for s in ('source','prepared_target') for r in n.ROLES),
        *(charge.filename('step',r,i) for r in n.ROLES for i in range(1,11)),
        *(covariance.path(k,r) for k in covariance.KINDS for r in n.ROLES)]


def verify(row,path,record):
    b.check_digest(row)
    errors=row['errors'];value=record['execution']
    b.require(row['native_path']==path and row['native_record_digest']==record['record_digest']
        and row['oracle_sha256']==b.sha((b.ROOT/e.SELF).read_bytes())
        and errors['input_identity']==value['read']['input_identity']
        and errors['read_digest']==value['read']['record_digest']
        and errors['poststate_digest']==b.digest(value['after'])
        and errors['precision_bits']==e.g.BITS and errors['uniform_trajectory_enclosure'] is False,
        'pointwise input/oracle binding')
    b.require(all(0<=e.q(errors[k])<e.q(v) for k,v in LIMITS.items())
        and e.q(errors['exact_one_step_resource_lower'])>=0,'pointwise update/sign bound')


def build_available():
    JOURNAL.mkdir(parents=True,exist_ok=True)
    complete=[]
    for path in paths():
        if not (b.ROOT/path).exists():continue
        record=n.storage.read(path);b.check_digest(record)
        oracle=b.sha((b.ROOT/e.SELF).read_bytes())
        key=b.digest([path,record['record_digest'],oracle])
        destination=JOURNAL/(key+'.json.xz')
        if destination.exists():row=n.storage.read(destination)
        else:
            started=time.monotonic()
            if path==charge.filename('source','current'):
                pilot=n.storage.read(PILOT);b.check_digest(pilot);b.check_bindings(pilot['source_bindings'])
                b.require(pilot['source_record_digest']==record['record_digest'],'pointwise pilot lineage')
                errors=pilot['result'];reused=PILOT
            else:errors=e.step_error_bounds(record['execution']);reused=None
            row=b.seal(dict(native_path=path,native_record_digest=record['record_digest'],
                oracle_sha256=oracle,errors=errors,seconds=time.monotonic()-started,exact_reuse=reused))
            verify(row,path,record);n.storage.save(destination,row)
            print('independent pointwise enclosure',path,flush=True)
        verify(row,path,record);complete.append(row)
    return complete


def check(value=None):
    value=n.storage.read(PATH) if value is None else value
    b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(value['schema']=='p9-ccipc-large-pointwise-v1' and value['limits']==LIMITS
        and [row['native_path'] for row in value['cases']]==paths() and len(value['cases'])==30
        and value['native_reruns']==0 and value['uniform_trajectory_enclosure'] is False
        and value['user_accepted'] is False,'pointwise coverage/scope')
    for row in value['cases']:
        record=n.storage.read(row['native_path']);b.check_digest(record)
        verify(row,row['native_path'],record)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('available','finish','check'));args=p.parse_args()
    with epoch.numerical_campaign(),charge.context(),n.compute_worker():
        if args.action=='check':check()
        else:
            rows=build_available()
            if args.action=='finish':
                b.require(len(rows)==30,'pointwise campaign incomplete')
                names={SELF,e.SELF,epoch.SELF,epoch.PATH,charge.SELF,charge.INPUTS,charge.NATIVE,PILOT,*paths()}
                names|={ref['path'] for ref in n.storage.read(charge.NATIVE)['source_bindings']}
                value=b.seal(dict(schema='p9-ccipc-large-pointwise-v1',source_bindings=b.bind(names),
                    limits=LIMITS,cases=rows,native_reruns=0,uniform_trajectory_enclosure=False,user_accepted=False))
                check(value);n.storage.save(PATH,value)
            print('pointwise enclosures retained',len(rows),'of 30',flush=True)
