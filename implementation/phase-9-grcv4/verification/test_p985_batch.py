"""Family-specific internal lifecycle checks; invoked by the bounded batch runner."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
import unittest
from unittest.mock import patch

import p985_batch as h
from pygrc.models import grc_9_v4_lifecycle as native, grc_v4_lifecycle as generic
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_state import FrozenJSONMap

METHODS={
    'C_CI':dict(
        domain=['test_real_target_domain_failure_both_roles_and_reset_only','test_rehashed_history_policy_cannot_add_candidate_or_carrier_history'],
        atomic=['test_both_charge_failures_and_late_publication_errors_roll_back'],
        replay=['test_replay_rejects_receipts_identities_roots_and_role_forgery'],
        writers=['test_event_zero_step_runs_both_roots_without_os_continuity_or_writer']),
    'A_CI':dict(
        domain=['test_real_target_domain_rejects_current_only_and_reset_only','test_policy_rehashed_role_substitutions_fail_at_admission'],
        atomic=['test_charge_both_roles_and_late_receipt_failures_roll_back'],
        replay=['test_replay_rejects_history_reference_identity_and_receipt_tampering','test_rehashed_target_authority_and_source_policy_do_not_bypass_replay'],
        writers=['test_event_admission_never_advances_or_runs_a_writer']),
    'A_PC':dict(
        domain=['test_target_whole_chart_rejection_both_roles_even_when_points_regular','test_policy_rehashed_role_substitutions_fail_at_admission'],
        atomic=['test_charge_both_roles_and_late_receipt_failures_roll_back'],
        replay=['test_replay_rejects_history_reference_identity_and_receipt_tampering','test_rehashed_target_authority_and_source_policy_do_not_bypass_replay','test_complete_archives_and_rehashed_archive_replay_failures'],
        writers=['test_event_admission_runs_neither_W_nor_Z_writer'])}


class FamilyLifecycleTests(unittest.TestCase):
    FAMILY=None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:raise unittest.SkipTest('use p985_batch.py with an explicit family')
        cls.module=h.fixture_module(cls.FAMILY)
        cls.prior=getattr(cls.module,'Native'+h.TAGS[cls.FAMILY]+'Pressure')
        cls.Op=h.operation(cls.FAMILY)
        if cls.FAMILY=='C_CI':cls.seed,cls.request,cls.initial=cls.module.fixture()
        else:
            raw=cls.module.RECORD.read_bytes();h.require(h.sha(raw)==cls.module.ORACLE_SHA,'accepted fixture identity')
            cls.record=json.loads(raw);cls.seed,cls.request=cls.module.fixture(cls.record)
        cls.owner=cls.Op(cls.seed);result=cls.owner.expand(cls.request)
        h.require(result.committed,'accepted small event failed: '+str(result.failure))
        cls.committed=cls.owner.checkpoint()

    def record_case(self,name,**fields):h.OBSERVATIONS[name]=dict(passed=True,**fields)

    def assertRollback(self,owner,request,stage=None):
        pointer=owner._published;raw=owner.checkpoint();result=owner.expand(request)
        self.assertFalse(result.committed);self.assertIsNotNone(result.failure)
        if stage:self.assertEqual(result.failure.stage,stage)
        self.assertIs(owner._published,pointer);self.assertEqual(owner.checkpoint(),raw)
        self.assertEqual(result.failure.prestate_digest,result.failure.poststate_digest)
        self.assertEqual(result.failure.pre_lifecycle_digest,result.failure.post_lifecycle_digest)
        self.assertEqual(result.failure.prestate_digest,owner.state.scientific_digest)
        self.assertEqual(result.failure.pre_lifecycle_digest,owner.state.lifecycle_digest(owner.receipts))
        return result

    def prior_cases(self,kind):
        methods=METHODS[self.FAMILY][kind]
        for name in methods:
            with self.subTest(reused_method=name):getattr(self.prior,name)(self)
        return methods

    def test_request_boundaries(self):
        rows=[];owner=self.Op(self.seed)
        for code,change in (
            ('module_chirality_required',dict(module_chirality=None)),
            ('module_growth_phase_required',dict(growth_phase=None)),
            ('reject_noncanonical_inactive_growth_phase',dict(target_effective_degree=30,growth_phase=1))):
            result=self.assertRollback(owner,replace(self.request,**change),stage='admission')
            self.assertEqual(result.failure.code,code);rows.append(code)
        self.record_case('request_boundaries',codes=rows,full_publication_rollback=True,
            self_loop_reused_from=h.common.result_path('small'))

    def test_domain_and_history(self):
        self.record_case('domain_and_history',methods=self.prior_cases('domain'),
            family_specific=True,reset_only=True,
            domain_controls='injected_whole_chart_and_role_history' if self.FAMILY=='A_PC' else 'natural_sufficient_domain_rejection')

    def test_atomicity(self):
        methods=self.prior_cases('atomic');owner=self.Op(self.seed)
        original=native.GRCV4LifecycleResult
        def fail_success(*args,**kwargs):
            if args and args[0]=='committed':raise ValueError('late result construction')
            return original(*args,**kwargs)
        with patch.object(native,'GRCV4LifecycleResult',fail_success):
            self.assertRollback(owner,self.request,stage='commit')
        self.record_case('atomicity',methods=methods,late_publication_pointer_unchanged=True,
            prospective_archive_and_reference_records_not_published=True)

    def test_replay(self):
        methods=self.prior_cases('replay')
        restored=self.Op.replay(self.committed);self.assertEqual(restored.checkpoint(),self.committed)
        after=restored.state.inputs;source=self.seed.inputs
        before_ids=source.geometry.reference.graph.live_node_ids
        target_ids=after.geometry.reference.graph.live_node_ids
        source_node=self.request.source_node_id
        for role in ('current','reset'):
            incoming=getattr(source,role);out=getattr(after,role)
            by_id=dict(zip(before_ids,incoming.C))
            for n,c in zip(target_ids,out.C):
                if n in by_id:expected=by_id[n]
                elif '/satellite/' in str(n):
                    i=int(n.rsplit('/',1)[1])-1
                    expected=float(Fraction(by_id[source_node])*Fraction(self.request.resource_distribution[i]))
                else:expected=0.0
                self.assertEqual(c,expected)
            if self.FAMILY.startswith('A'):
                weights=dict(zip(source.geometry.reference.graph.live_edge_ids,incoming.W_A))
                seed=self.seed.specialization.resolved['expansion']['bond_seed']
                self.assertEqual(out.W_A,tuple(weights.get(e,seed) for e in after.geometry.reference.graph.live_edge_ids))
            else:self.assertIsNone(out.W_A)
        data=json.loads(self.committed);archives=data.get('carrier_archives',[])
        if self.FAMILY=='A_PC':
            self.assertEqual(tuple(archives[0]['history_content']['content']),source.current.Z_4+source.reset.Z_4)
            for role in ('current','reset'):self.assertEqual(getattr(after,role).Z_4,(0.0,)*len(getattr(after,role).Z_4))
        else:
            for role in ('current','reset'):self.assertIsNone(getattr(after,role).Z_4)
        self.record_case('replay',methods=methods,checkpoint_exact=True,checkpoint_sha256=h.sha(self.committed),
            **h.common.occupancy(restored.state.inputs.geometry.reference.graph.port_graph),
            archive_count=len(archives),independent_resource_and_history_transfer=True)

    def test_readmission_no_writers(self):
        self.record_case('readmission_no_writers',methods=self.prior_cases('writers'),zero_temporal_writes=True)

    def test_continuation_reset(self):
        restored=self.Op.replay(self.committed);before=restored.state.inputs
        kw={} if self.FAMILY=='C_CI' else dict(differential_reference=restored.state.differential_reference)
        owner=generic.GRCV4Operation(before,**kw)
        self.assertEqual(owner.reference,before.geometry.reference)
        self.assertEqual(owner.state.current,before.current)
        self.assertEqual(owner.state.reset.authoritative,before.reset)
        self.assertEqual(owner.state.receipt_ledger,())
        seed=owner.snapshot()
        result=owner.step_v4(GRCV4StepRequestInput('grcv4-step-request-input-v1','p985-'+self.FAMILY+'-step',2**-12,FrozenJSONMap({})))
        self.assertTrue(result.committed,result.failure)
        step=owner.snapshot();owner=generic.GRCV4Operation.from_state(step)
        self.assertEqual(owner.snapshot(),step);self.assertNotEqual(owner.state.current,before.current)
        if self.FAMILY.startswith('A'):self.assertNotEqual(owner.state.current.W_A,before.current.W_A)
        if self.FAMILY=='A_PC':self.assertNotEqual(owner.state.current.Z_4,before.current.Z_4)
        clock=(owner.state.step_index,owner.state.time);ledger=owner.state.receipt_ledger
        pointer=owner._owned
        with patch.object(generic,'_validate_publication',side_effect=ValueError('late reset publication')):
            with self.assertRaisesRegex(ValueError,'late reset'):owner.reset()
        self.assertIs(owner._owned,pointer);self.assertEqual(owner.snapshot(),step)
        owner.reset();reset=owner.snapshot()
        self.assertEqual(owner.state.current,before.reset);self.assertEqual(owner.state.reset.authoritative,before.reset)
        self.assertEqual((owner.state.step_index,owner.state.time),clock)
        self.assertEqual(owner.state.receipt_ledger[:len(ledger)],ledger)
        self.assertGreater(len(owner.state.receipt_ledger),len(ledger))
        rebuilt=generic.GRCV4Operation.from_state(reset);self.assertEqual(rebuilt.snapshot(),reset)
        self.assertEqual(rebuilt.reference.graph.port_graph,before.geometry.reference.graph.port_graph)
        self.assertEqual(self.owner.checkpoint(),self.committed)
        for field in ('receipt_ledger','commit_records'):
            bad=deepcopy(reset);bad[field].pop()
            with self.assertRaises(ValueError):generic.GRCV4Operation.from_state(bad)
        self.record_case('continuation_reset',event_checkpoint_sha256=h.sha(self.committed),
            seed_snapshot_sha256=h.digest(seed),step_snapshot_sha256=h.digest(step),reset_snapshot_sha256=h.digest(reset),
            native_steps=1,native_resets=1,full_authority_restored=True,clock_preserved=True,
            reset_rollback=True,fresh_generic_ledger=True,public_specialization_facade=False)
