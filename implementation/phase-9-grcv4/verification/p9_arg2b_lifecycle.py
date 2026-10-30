"""Connected A_RG2b 8.5: role histories, rollback, replay and reset."""
import unittest
from dataclasses import replace
from unittest.mock import patch
import p9_arg2b_campaign as c
from tests.models import test_grc_9_v4_arg2b as old
from tests.models.test_grc_9_v4_arg2b_integration import seed
from pygrc.models import grc_v4_lifecycle as generic
from pygrc.models.grc_v4 import GRCV4StepRequestInput
r,b=c.r,c.b
SELF=b.HERE+'p9_arg2b_lifecycle.py'
RESULT=c.BASE+'8.5-small.json.xz'
OBSERVATIONS={}

class Lifecycle(old.NativeARG2bPressure):
 @classmethod
 def setUpClass(cls):
  cls.seed,cls.request=seed();cls.owner=old.GRC9V4ARG2bOperation(cls.seed)
  out=cls.owner.expand(cls.request);assert out.committed,out.failure
  cls.checkpoint=cls.owner.checkpoint()
 def case_atomicity(self):
  self.test_charge_both_roles_and_late_receipt_failures_roll_back()
  owner=old.GRC9V4ARG2bOperation(self.seed);pointer,raw=owner._published,owner.checkpoint()
  with patch.object(old.native,'_EventPublication',side_effect=RuntimeError('late publication')):
   with self.assertRaisesRegex(RuntimeError,'late publication'):owner.expand(self.request)
  self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
  OBSERVATIONS['atomicity']=dict(both_roles=True,late_receipts_and_publication=True,whole_rollback=True)
 def case_replay(self):
  self.test_replay_rejects_history_reference_identity_and_receipt_tampering()
  self.test_rehashed_target_authority_and_source_policy_do_not_bypass_replay()
  self.test_duplicate_concurrent_events_publish_once()
  OBSERVATIONS['replay']=dict(authority_history_reference_receipt_forgery_rejected=True,duplicate_once=True)
 def case_no_writers(self):
  self.test_event_runs_no_physical_step_or_history_writer()
  OBSERVATIONS['no_writers']=dict(fresh_sections=True,no_ordinary_step=True,no_carrier=True)
 def case_boundaries(self):
  self.test_C_Y_chart_boundaries_and_dt_zero_admission()
  OBSERVATIONS['boundaries']=dict(C_and_scaled_log_W=True,K_vs_K_minus=True,neighboring_represented_faces=True)
 def case_history_binding(self):
  self.test_policy_rehashed_role_substitutions_fail_at_admission()
  OBSERVATIONS['history_binding']=dict(both_role_substitution_rejected=True,unselected_loss_rejected=True)
 def case_reset(self):
  before=self.owner.state.inputs;owner=generic.GRCV4Operation(before,differential_reference=r.r.backend(before))
  out=owner.step_v4(GRCV4StepRequestInput('grcv4-step-request-input-v1','arg2b-reset-pressure',b.DT,b.FrozenJSONMap({})))
  self.assertTrue(out.committed,out.failure);saved=owner.snapshot();owner=generic.GRCV4Operation.from_state(saved)
  self.assertEqual(owner.snapshot(),saved);clock=(owner.state.step_index,owner.state.time);pointer=owner._owned
  with patch.object(generic,'_validate_publication',side_effect=ValueError('late reset')):
   with self.assertRaisesRegex(ValueError,'late reset'):owner.reset()
  self.assertIs(owner._owned,pointer);self.assertEqual(owner.snapshot(),saved)
  owner.reset();self.assertEqual(owner.state.current,before.reset);self.assertEqual((owner.state.step_index,owner.state.time),clock)
  self.assertEqual(generic.GRCV4Operation.from_state(owner.snapshot()).snapshot(),owner.snapshot())
  OBSERVATIONS['reset']=dict(native_step=True,full_C_W_authority_restored=True,clock_preserved=True,late_reset_rollback=True,replay_exact=True)

CASES=('atomicity','replay','no_writers','boundaries','history_binding','reset')
def run():
 refs=b.bind({SELF,'tests/models/test_grc_9_v4_arg2b.py','tests/models/test_grc_9_v4_arg2b_integration.py',c.INPUTS}|c.paths())
 with r.worker():result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Lifecycle('case_'+k) for k in CASES))
 b.require(result.wasSuccessful() and result.testsRun==6 and not result.skipped,'8.5 incomplete');b.check_bindings(refs)
 c.save(RESULT,b.seal(dict(schema='p9-arg2b-small-lifecycle-v1',source_bindings=refs,tests_run=6,observations=OBSERVATIONS,
  outcome='passed',user_accepted=False,aggregate_closed=False)))
if __name__=='__main__':run()
