"""Exact-charge allocation successor; immutable source steps are reused by digest."""
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor
import argparse
from unittest.mock import patch
import p984h_acipc as n
from p9_ccipc_large_charge import select

b,q=n.b,n.q
SELF=b.HERE+'p9_acipc_large_charge.py'
INPUTS=b.BASE+'P9-8.4g-ACIPCChargeInputs.json'
RESULTS=b.BASE+'P9-8.4g-ACIPCChargeResults.json.xz'
NATIVE=b.BASE+'P9-8.4h-ACIPCChargeInputs.json'
ACTUAL=b.BASE+'P9-8.4h-ACIPCCharge-ActualPreflight.json.xz'
ORIGINAL_INPUTS=n.companion.INPUTS
ORIGINAL_RESULTS=n.companion.RESULTS
ORIGINAL_NATIVE=n.INPUTS


def filename(segment,role='current',index=1):
    if segment=='source':return b.BASE+'P9-8.4h-ACIPC-source-'+role+'.json.xz'
    b.require(segment in ('prepared_target','event','step','final') and role in n.ROLES and 1<=index<=10,'charge segment')
    suffix=segment if segment=='event' else segment+'-'+role+('-'+str(index) if segment=='step' else '')
    return b.BASE+'P9-8.4h-ACIPCCharge-'+suffix+'.json.xz'


@contextmanager
def context():
    import p984h_acipc_actual as actual
    with patch.object(n.companion,'INPUTS',INPUTS),patch.object(n.companion,'RESULTS',RESULTS), \
         patch.object(n,'INPUTS',NATIVE),patch.object(n,'filename',filename),patch.object(actual,'PATH',ACTUAL):yield


def prepare():
    original=n.storage.read(ORIGINAL_INPUTS);prior=n.storage.read(ORIGINAL_RESULTS)
    raw=n.read('source')['execution']['state']['inputs']
    index=raw['reference']['graph']['live_node_ids'].index(original['adjusted']['event_request']['source_node_id'])
    operands=[q(raw[role]['C'][index]) for role in n.ROLES]
    selected=select(original['constraints'],operands)
    adjusted,identity=n.companion.companion(selected['shares'],True)
    b.require(adjusted['source']==original['adjusted']['source'],'changed source forbids reuse')
    residuals={role:str(sum((q(float(operands[i]*q(w))) for w in original['selection']['shares']),q(0))-operands[i]) for i,role in enumerate(n.ROLES)}
    b.require(any(q(x)!=0 for x in residuals.values()),'old allocation not excluded')
    sources={role:dict(path=filename('source',role),record_digest=n.read('source',role)['record_digest']) for role in n.ROLES}
    paths={SELF,ORIGINAL_INPUTS,ORIGINAL_RESULTS,ORIGINAL_NATIVE,n.SELF,n.g.SELF,n.companion.SELF,
        b.HERE+'p9_ccipc_large_charge.py',*(x['path'] for x in sources.values())}
    paths|={r['path'] for r in original['source_bindings']}
    m=b.seal(dict(schema='p984g-acipc-charge-inputs-v1',family='A_CI_PC',adjusted=adjusted,companion=identity,
        constraints=original['constraints'],selection=selected,source_bindings=b.bind(paths),
        actual_source_split_operands=list(map(str,operands)),original_evolved_split_charge_delta=residuals,
        original_prepared_target_reused=False,exact_source_reuse=sources,
        changed_tolerances=False,changed_step_size=False,user_accepted=False,aggregate_closed=False))
    n.storage.save(INPUTS,m)
    with ProcessPoolExecutor(max_workers=2) as pool:
        target=list(pool.map(n.companion.first,[(adjusted,'target',role) for role in n.ROLES]))
    rows=[x for x in prior['cases'] if x['graph']=='source']+target
    b.require(all(not x['negative_vertices'] and not x['unresolved_vertices'] for x in rows),'successor positivity')
    result=b.seal(dict(schema='p984g-acipc-charge-results-v1',manifest_digest=m['record_digest'],cases=rows,
        source_oracle_exact_reuse=prior['record_digest'],ready_for_native=True,native_steps=0,native_events=0,
        user_accepted=False,aggregate_closed=False))
    n.storage.save(RESULTS,result)
    with context():
        native=n.manifest();native['source_bindings']=b.bind({r['path'] for r in native['source_bindings']}|{SELF,INPUTS,RESULTS,b.HERE+'p984h_acipc_actual.py',b.HERE+'p9_acipc_execution_scope.py',b.HERE+'p9_acipc_campaign.py',b.HERE+'test_p9_acipc_review.py'})
        native=b.seal(dict(native,source_manifest_digest=n.storage.read(ORIGINAL_NATIVE)['record_digest'],exact_source_reuse=sources))
        n.storage.save(NATIVE,native)
    print(dict(selection=selected,original_delta=residuals),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','actual','run'));p.add_argument('--segment',default='event');p.add_argument('--role',default='current');p.add_argument('--index',type=int,default=1);args=p.parse_args()
    with n.compute_worker():
        if args.action=='prepare':prepare()
        elif args.action=='actual':
            import p984h_acipc_actual as actual
            with context():actual.run()
        else:
            from p9_acipc_execution_scope import execution_scope
            with execution_scope():n.run(args.segment,args.role,args.index)
