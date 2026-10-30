"""Exact compatibility/discovery matrix; passing execution is not acceptance."""
from copy import deepcopy
import p9_arg2b_campaign as c
import p9_arg2b_integration as integration
b=c.b
SELF=b.HERE+'p9_arg2b_support.py'
MATRIX=c.BASE+'9.3-Matrix.json'
SUPPORT=c.BASE+'9.6-Support.json'

def matrix():
 prior=c.read('implementation/phase-9-grcv4/tranche-8/crg2b-native/9.3-Matrix.json');b.check_digest(prior)
 accepted=c.read('implementation/phase-9-grcv4/tranche-9/P9-CRG2b-Acceptance.json');b.check_digest(accepted)
 b.require(accepted['record_digest']=='b4c76c8c0cfd206e1951c833276df50aaae93dfb639772d86697079ff4a81a98' and accepted['user_accepted'],'ninth acceptance')
 executed=c.read(integration.path('9.2'));integration.check('9.2');rows=deepcopy(prior['cells'])
 for row in rows:
  if row['family']=='C_RG2b':row.update(disposition='bounded_accepted',reason='explicit_C_RG2b_acceptance',
    acceptance=dict(path='implementation/phase-9-grcv4/tranche-9/P9-CRG2b-Acceptance.json',record_digest=accepted['record_digest']))
  if row['family']=='A_RG2b':
   proof=executed['evidence'][row['surface']]
   row.update(disposition='passed_pending_acceptance',reason='new_A_RG2b_native_delegate_execution',acceptance=None,
    complete_profile_id=proof['complete_profile_id'],model_identity=proof['model_identity'],target_spec_version=proof['target_spec_version'],
    execution=dict(path=integration.path('9.2'),record_digest=executed['record_digest'],json_pointer='/evidence/'+row['surface']))
 b.require(len(rows)==40 and sum(r['disposition']=='bounded_accepted' for r in rows)==36
  and sum(r['disposition']=='passed_pending_acceptance' for r in rows)==4,'compatibility matrix scope')
 return b.seal(dict(schema='p9-arg2b-compatibility-matrix-v1',source_bindings=b.bind({SELF,integration.path('9.2'),
  'implementation/phase-9-grcv4/tranche-8/crg2b-native/9.3-Matrix.json','implementation/phase-9-grcv4/tranche-9/P9-CRG2b-Acceptance.json'}),
  cells=rows,counts=dict(bounded_accepted=36,passed_pending_acceptance=4,unselected_not_executed=0),user_accepted=False,aggregate_closed=False))

if __name__=='__main__':c.save(MATRIX,matrix());print('40 cells: 36 accepted, 4 passed pending acceptance, 0 unexecuted')
