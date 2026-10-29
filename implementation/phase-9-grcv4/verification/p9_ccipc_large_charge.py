"""Charge-preserving successor allocation selected against the actual source beat.

The original companion's source is identical and its two completed source
steps are reused by digest. Its prepared target is a different scientific
subject. New target prerequisites, event and continuations get separate paths.
"""
from contextlib import contextmanager
import json
from unittest.mock import patch

import p984h_ccipc as n
import p9_ccipc_execution_epoch as epoch

b,q=n.b,n.q
SELF=b.HERE+'p9_ccipc_large_charge.py'
INPUTS=b.BASE+'P9-8.4g-CCIPCChargeCompanionInputs.json'
RESULTS=b.BASE+'P9-8.4g-CCIPCChargeCompanionResults.json.xz'
NATIVE=b.BASE+'P9-8.4h-CCIPCChargeInputs.json'
ACTUAL=b.BASE+'P9-8.4h-CCIPCCharge-ActualPreflight.json.xz'
ORIGINAL_INPUTS=b.BASE+'P9-8.4g-CCIPCCompanionInputs.json'
ORIGINAL_RESULTS=b.BASE+'P9-8.4g-CCIPCCompanionResults.json.xz'
ORIGINAL_NATIVE=b.BASE+'P9-8.4h-CCIPCInputs.json'


def select(constraints,values):
    equations=[row for rows in constraints.values() for row in rows]
    for denominator in (2,4,8,16,32,64):
        choices=[]
        for i in range(1,denominator):
            for j in range(1,denominator-i):
                shares=tuple(q(x)/denominator for x in (i,j,denominator-i-j))
                if any(sum((q(float(x*w)) for w in shares),q(0))!=x for x in values):continue
                margin=min(q(row['offset'])+sum((q(x)*w for x,w in zip(row['coefficients'],shares)),q(0)) for row in equations)
                if margin>0:choices.append((margin,shares))
        if choices:
            margin,shares=sorted(choices,key=lambda x:(-x[0],x[1]))[0]
            return dict(shares=list(map(str,shares)),denominator=denominator,leading_margin=str(margin),
                rule='first_dyadic_grid_exact_both_evolved_charges_positive_then_max_min_lexicographic')
    raise ValueError('no exact represented-charge candidate in declared grids')


def filename(segment,role='current',index=1):
    b.require(segment in ('source','prepared_target','event','step','final') and role in n.ROLES
              and 1<=index<=10,'charge companion segment roster')
    if segment=='source':return b.BASE+'P9-8.4h-CCIPC-source-'+role+'.json.xz'
    suffix=segment if segment=='event' else segment+'-'+role+('-'+str(index) if segment=='step' else '')
    return b.BASE+'P9-8.4h-CCIPCCharge-'+suffix+'.json.xz'


@contextmanager
def context():
    import p984h_ccipc_actual as actual
    with patch.object(n.companion,'INPUTS',INPUTS),patch.object(n.companion,'RESULTS',RESULTS), \
         patch.object(n,'INPUTS',NATIVE),patch.object(n,'filename',filename),patch.object(actual,'PATH',ACTUAL):
        yield


def prepare():
    original=n.storage.read(ORIGINAL_INPUTS);prior=n.storage.read(ORIGINAL_RESULTS)
    source=n.read('source');b.check_digest(source)
    raw=source['execution']['state']['inputs']
    index=raw['reference']['graph']['live_node_ids'].index(original['adjusted']['event_request']['source_node_id'])
    values=[q(raw[role]['C'][index]) for role in n.ROLES]
    chosen=select(original['constraints'],values)
    shares=chosen['shares'];adjusted,identity=n.companion.companion(shares,True)
    b.require(adjusted['source']==original['adjusted']['source'],'source changed: exact native reuse forbidden')
    residuals={role:str(sum((q(float(values[i]*q(w))) for w in original['selection']['shares']),q(0))-values[i])
               for i,role in enumerate(n.ROLES)}
    b.require(any(q(x)!=0 for x in residuals.values()),'original evolved charge exclusion required')
    sources={role:dict(path=filename('source',role),record_digest=n.read('source',role)['record_digest']) for role in n.ROLES}
    paths={SELF,ORIGINAL_INPUTS,ORIGINAL_RESULTS,ORIGINAL_NATIVE,n.SELF,n.g.SELF,n.companion.SELF,
           n.g.iv.SELF,n.g.pc.graph_math.SELF,epoch.SELF,epoch.PATH,*(r['path'] for r in sources.values())}
    paths|={r['path'] for r in original['source_bindings']}
    m=b.seal(dict(schema='p984g-ccipc-charge-companion-inputs-v1',family='C_CI_PC',
        adjusted=adjusted,companion=identity,selection=chosen,source_bindings=b.bind(paths),
        predecessor_digest=original['record_digest'],original_evolved_split_charge_delta=residuals,
        original_prepared_target_reused=False,exact_source_reuse=sources,
        actual_source_split_operands=list(map(str,values)),
        changed_tolerances=False,changed_step_size=False,user_accepted=False,aggregate_closed=False))
    n.storage.save(INPUTS,m)
    rows=[row for row in prior['cases'] if row['graph']=='source']
    for role in n.ROLES:
        rows.append(dict(graph='target',**n.g.first_step(adjusted['target'],role,n.DT)))
    b.require(len(rows)==4 and all(row['first_step_nonnegative'] for row in rows),'charge companion feasibility')
    result=b.seal(dict(schema='p984g-ccipc-charge-companion-results-v1',manifest_digest=m['record_digest'],
        cases=rows,source_oracle_exact_reuse=prior['record_digest'],ready_for_native=True,
        native_steps=0,native_events=0,user_accepted=False,aggregate_closed=False))
    n.storage.save(RESULTS,result)
    with context():
        native=b.seal(dict(n.manifest(),exact_source_reuse=sources,
                          source_manifest_digest=n.storage.read(ORIGINAL_NATIVE)['record_digest']))
        n.storage.save(NATIVE,native)
        import p984h_ccipc_actual as actual
        actual.run()
    print(json.dumps(dict(selection=chosen,source_reuse=sources,original_split_delta=residuals)),flush=True)


if __name__=='__main__':
    with epoch.numerical_campaign(),n.compute_worker():prepare()
