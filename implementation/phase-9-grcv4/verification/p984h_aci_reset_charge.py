"""Reset step 10/final continuation under the tested charge-check correction.

The native reset step completed but the original retained check rejected its
extra zero-residual predicate. No failed dump is retained. Resume only reset
step 10 and its final root; preserve steps 1-9 and all current-side bindings.
"""
import argparse
import json
from unittest.mock import patch
import p984h_aci_charge_successor as s
c=s.c
SELF=c.HERE+'p984h_aci_reset_charge.py'
INPUTS=c.BASE+'P9-8.4h-ACIResetChargeInputs.json'


def manifest():
    correction=s.manifest()
    c.require(correction==json.loads((c.ROOT/s.INPUTS).read_text()),'charge correction drift')
    paths=set(correction['source_bindings'])|{SELF,s.INPUTS,c.path('step','reset',9)}
    return c.seal({**correction,'schema':'p984h-aci-reset-charge-successor-inputs-v1',
        'source_bindings':{n:c.p.sha(n) for n in sorted(paths)},
        'allowed_role':'reset','allowed_steps':[10],'allowed_final_step':10,
        'prior_charge_correction_digest':correction['record_digest']})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run'));a=parser.parse_args()
    if a.action=='prepare':
        with (c.ROOT/INPUTS).open('x') as stream:json.dump(manifest(),stream,indent=2);stream.write('\n')
    else:
        with patch.object(c,'manifest',manifest),patch.object(c,'INPUTS',INPUTS),patch.object(c,'check_step',s.check_step):
            c.run('step','reset',10)
            c.run('final','reset',10)
