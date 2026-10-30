"""Exact compatibility/discovery matrix; passing execution is not acceptance."""
from copy import deepcopy
import p9_crg2b_campaign as c
import p9_crg2b_integration as integration
b=c.b
SELF=b.HERE+'p9_crg2b_support.py'
MATRIX=c.BASE+'9.3-Matrix.json'
SUPPORT=c.BASE+'9.6-Support.json'

def matrix():
 prior=c.read('implementation/phase-9-grcv4/tranche-9/P9-9.3-ACIPCMatrix.json');b.check_digest(prior)
 accepted=c.read('implementation/phase-9-grcv4/tranche-9/P9-ACIPC-Acceptance.json');b.check_digest(accepted)
 b.require(accepted['record_digest']=='6d793202d07e1057cbc43297a9ae539e5475898fe6b5b060dae50c7770022c6f' and accepted['user_accepted'],'eighth acceptance')
 executed=c.read(integration.path('9.2'));integration.check('9.2');rows=deepcopy(prior['cells'])
 for row in rows:
  if row['family']=='A_CI_PC':row.update(disposition='bounded_accepted',reason='explicit_A_CI_PC_acceptance',
    acceptance=dict(path='implementation/phase-9-grcv4/tranche-9/P9-ACIPC-Acceptance.json',record_digest=accepted['record_digest']))
  if row['family']=='C_RG2b':
   proof=executed['evidence'][row['surface']]
   row.update(disposition='passed_pending_acceptance',reason='new_C_RG2b_native_delegate_execution',acceptance=None,
    complete_profile_id=proof['complete_profile_id'],model_identity=proof['model_identity'],target_spec_version=proof['target_spec_version'],
    execution=dict(path=integration.path('9.2'),record_digest=executed['record_digest'],json_pointer='/evidence/'+row['surface']))
 b.require(len(rows)==40 and sum(r['disposition']=='bounded_accepted' for r in rows)==32
  and sum(r['disposition']=='passed_pending_acceptance' for r in rows)==4,'compatibility matrix scope')
 return b.seal(dict(schema='p9-crg2b-compatibility-matrix-v1',source_bindings=b.bind({SELF,integration.path('9.2'),
  'implementation/phase-9-grcv4/tranche-9/P9-9.3-ACIPCMatrix.json','implementation/phase-9-grcv4/tranche-9/P9-ACIPC-Acceptance.json'}),
  cells=rows,counts=dict(bounded_accepted=32,passed_pending_acceptance=4,unselected_not_executed=4),user_accepted=False,aggregate_closed=False))

if __name__=='__main__':c.save(MATRIX,matrix());print('40 cells: 32 accepted, 4 passed pending acceptance, 4 unexecuted')
