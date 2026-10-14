"""Retained corrected-runtime A_CI successor; independent checks, no native rerun."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from unittest.mock import patch
import p984g_aci_native_successor as run
import p984g_aci_native_check as prior
import p984g_pre_aci_residual_sources as history

ROOT,BASE,HERE=run.ROOT,run.BASE,run.HERE
SELF=HERE+'p984g_aci_native_successor_check.py'
RESULTS=BASE+'P9-8.4g-ACINativeSuccessorResults.json'


@contextmanager
def selected_checks():
    with (patch.object(prior.run,'bindings',run.bindings),patch.object(prior.run,'case_path',run.case_path),
          patch.object(prior.run.oracle,'check_retained',history.check_staged),patch.object(prior,'KNOWN_HOLDS',[])):
        yield


def assess(value,companion,oracle):
    with selected_checks():return prior.assess(value,companion,oracle)


def check():
    with selected_checks():value=prior.check()
    value.update(schema='p984g-aci-corrected-native-summary-v1',
        corrected_operations=['policy_selected_analytic_Hodge_inverse','whole_interval_A_conductance'],
        historical_timeout_preserved=True,predecessor_staged_source_revision=history.REVISION,
        source_bindings={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
            for p in (SELF,prior.SELF,run.SELF,HERE+'test_p984g_aci_native_successor.py')})
    return prior.seal(value)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['check','summarize']);a=p.parse_args();v=check()
    if a.mode=='summarize':
        prior.require(not (ROOT/RESULTS).exists(),'no overwrite');(ROOT/RESULTS).write_text(json.dumps(v,indent=2)+'\n')
    else:prior.require(v==json.loads((ROOT/RESULTS).read_text()),'successor summary drift')
    print(json.dumps({k:v[k] for k in ('native_steps','native_roots','native_prerequisites_complete')}))
