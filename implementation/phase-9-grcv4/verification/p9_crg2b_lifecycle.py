"""Connected C_RG2b event failures, reset/replay and mechanism pressure (8.5/8.6)."""
import argparse,json,time,unittest,math
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch
import p9_crg2b_campaign as c
import p9_crg2b_integration as integration
from tests.models import test_grc_9_v4_crg2b as old
from tests.models.test_grc_9_v4_crg2b_integration import seed
from pygrc.models import grc_v4_lifecycle as generic
from pygrc.models.grc_v4 import GRCV4StepRequestInput
r,b=c.r,c.b
SELF=b.HERE+'p9_crg2b_lifecycle.py'
RESULT=c.BASE+'8.5-small.json.xz'
OBSERVATIONS={}

class Lifecycle(old.NativeCRG2bPressure):
 @classmethod
 def setUpClass(cls):
  cls.seed,cls.request=seed();cls.initial=b.GeometryStageInputs.from_payload(c.read(c.INPUTS)['initial_inputs'])
  cls.owner=old.GRC9V4CRG2bOperation(cls.seed);out=cls.owner.expand(cls.request)
  assert out.committed,out.failure
  cls.committed=cls.owner.checkpoint()
 def case_atomicity(self):
  self.test_real_target_parameter_failure_and_late_failure_are_atomic()
  self.test_current_and_reset_charge_corruption_roll_back()
  owner=old.GRC9V4CRG2bOperation(self.seed);pointer,raw=owner._published,owner.checkpoint()
  with patch.object(old.native,'_EventPublication',side_effect=RuntimeError('late publication')):
   with self.assertRaisesRegex(RuntimeError,'late publication'):owner.expand(self.request)
  self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
  OBSERVATIONS['atomicity']=dict(both_role_charge_failure=True,late_reference_receipts_publication=True,whole_rollback=True)
 def case_replay(self):
  self.test_rehashed_authority_reference_and_receipt_forgery_rejects()
  self.test_duplicate_concurrent_events_and_backend_ownership()
  OBSERVATIONS['replay']=dict(authority_reference_receipt_forgery_rejected=True,duplicate_event_once=True,exact_replay=True)
 def case_no_writers(self):
  self.test_event_runs_no_step_CI_OS_writer_or_inherited_section()
  OBSERVATIONS['no_writers']=dict(fresh_sections=True,no_ordinary_step=True,no_persistent_history=True)
 def case_boundaries(self):
  self.test_equilibrium_and_K_vs_K_minus_boundaries()
  owner=old.GRC9V4CRG2bOperation(self.seed);raw=owner.checkpoint()
  for kwargs in (dict(module_chirality=None),dict(growth_phase=None),dict(target_effective_degree=30,growth_phase=1)):
   out=owner.expand(replace(self.request,**kwargs));self.assertFalse(out.committed);self.assertEqual(owner.checkpoint(),raw)
  OBSERVATIONS['boundaries']=dict(K_vs_K_minus=True,exact_faces=True,semantic_request_rollback=True)
 def case_excluded_simplex(self):
  for shares in ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)):
   owner=old.GRC9V4CRG2bOperation(self.seed);out=owner.expand(replace(self.request,resource_distribution=shares));self.assertTrue(out.committed,out.failure)
   raw=owner.checkpoint()
   for role in r.ROLES:
    before=replace(owner.state.inputs,current=getattr(owner.state.inputs,role),dt=b.DT)
    read=r.native_read(before)
    with r.ctx.workprec(192):
     truth=r.equations(before,read['H']);upper=min(r.oracle.upper(r.ball(v)+truth['increment'][i,0]) for i,v in enumerate(before.current.C))
    self.assertLess(upper,0)
    with self.assertRaises(old.ResourceBoundaryError):r.r.rg.ProvisionalCandidateRG2bStep(before)
    self.assertEqual(owner.checkpoint(),raw)
  OBSERVATIONS['excluded_simplex']=dict(events_admitted=3,negative_role_steps_rejected=6,no_clipping=True)
 def case_reset(self):
  before=self.owner.state.inputs;owner=generic.GRCV4Operation(before)
  out=owner.step_v4(GRCV4StepRequestInput('grcv4-step-request-input-v1','crg2b-reset-pressure',b.DT,b.FrozenJSONMap({})))
  self.assertTrue(out.committed,out.failure);saved=owner.snapshot();owner=generic.GRCV4Operation.from_state(saved)
  self.assertEqual(owner.snapshot(),saved);clock=(owner.state.step_index,owner.state.time);pointer=owner._owned
  with patch.object(generic,'_validate_publication',side_effect=ValueError('late reset')):
   with self.assertRaisesRegex(ValueError,'late reset'):owner.reset()
  self.assertIs(owner._owned,pointer);self.assertEqual(owner.snapshot(),saved)
  owner.reset();self.assertEqual(owner.state.current,before.reset);self.assertEqual((owner.state.step_index,owner.state.time),clock)
  self.assertEqual(generic.GRCV4Operation.from_state(owner.snapshot()).snapshot(),owner.snapshot())
  OBSERVATIONS['reset']=dict(native_step=True,full_authority_restored=True,clock_preserved=True,late_reset_rollback=True,replay_exact=True)

CASES=('atomicity','replay','no_writers','boundaries','excluded_simplex','reset')

def small():
 OBSERVATIONS.clear();refs=b.bind({SELF,'tests/models/test_grc_9_v4_crg2b.py','tests/models/test_grc_9_v4_crg2b_integration.py',c.INPUTS}|c.paths())
 with integration.compute.worker():
  result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Lifecycle('case_'+k) for k in CASES))
 b.require(result.wasSuccessful() and result.testsRun==6 and not result.skipped,'8.5 lifecycle pressure incomplete')
 b.check_bindings(refs)
 value=b.seal(dict(schema='p9-crg2b-small-lifecycle-v1',source_bindings=refs,tests_run=6,observations=OBSERVATIONS,
  outcome='passed',user_accepted=False,aggregate_closed=False));c.save(RESULT,value);return value

if __name__=='__main__':small();print('8.5 small PASS')
