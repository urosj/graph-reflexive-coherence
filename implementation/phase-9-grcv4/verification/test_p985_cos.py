"""Native C_OS lifecycle pressure; bounded internal composition, no public facade."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
import unittest
from unittest.mock import patch

import p985_cos as campaign
from pygrc.models import grc_9_v4_lifecycle as native, grc_v4_lifecycle as generic
from pygrc.models.grc_9_v4_expansion import GRC9V4COSExpansion, cos_profile_template
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_geometry import GRCV4Graph, GRCV4ReferenceGeometry, GeometryStageInputs
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap
from pygrc.models.grc_v4_numerics import NumericalPolicy, numerical_policy, CertificationInconclusive
from tests.models.test_grc_9_v4_lifecycle import native_cos_fixture
from tests.models import test_grc_9_v4_lifecycle as prior
from tests.models.test_grc_v4_geometry import stage_reference_fixture


class COSLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with campaign.scope():cls.seed,cls.request=native_cos_fixture()

    def setUp(self):
        scope=campaign.scope();scope.__enter__();self.addCleanup(scope.__exit__,None,None,None)
        self.owner=native.GRC9V4COSOperation(self.seed)

    def record(self,name,**values):
        campaign.OBSERVATIONS[name]=dict(passed=True,**values)

    def assert_rejected(self,owner,request,code,stage=None):
        pointer=owner._published;checkpoint=owner.checkpoint()
        result=owner.expand(request)
        self.assertFalse(result.committed);self.assertIsNotNone(result.failure)
        self.assertEqual(result.failure.code,code)
        if stage:self.assertEqual(result.failure.stage,stage)
        self.assertIs(owner._published,pointer)
        self.assertEqual(owner.checkpoint(),checkpoint)
        self.assertEqual(result.failure.prestate_digest,result.failure.poststate_digest)
        self.assertEqual(result.failure.pre_lifecycle_digest,result.failure.post_lifecycle_digest)
        self.assertEqual(result.failure.prestate_digest,owner.state.scientific_digest)
        self.assertEqual(result.failure.pre_lifecycle_digest,owner.state.lifecycle_digest(owner.receipts))
        self.assertEqual(len(result.emitted_receipts),1)  # emitted failure is not appended
        return dict(code=code,stage=result.failure.stage,checkpoint_sha256=campaign.sha(checkpoint),
                    whole_publication_unchanged=True,failure_receipt_not_persisted=True)

    def committed(self):
        result=self.owner.expand(self.request)
        self.assertTrue(result.committed, result.failure)
        return result

    def test_frozen_request_failures(self):
        rows=[]
        for name,changes,code in (
            ('G9-FAIL-MISSING-CHIRALITY',dict(module_chirality=None),'module_chirality_required'),
            ('G9-FAIL-MISSING-ACTIVE-PHASE',dict(growth_phase=None),'module_growth_phase_required'),
            ('G9-FAIL-NONCANONICAL-INACTIVE-PHASE',dict(target_effective_degree=30,growth_phase=1),
             'reject_noncanonical_inactive_growth_phase')):
            rows.append(dict(fixture_id=name,**self.assert_rejected(self.owner,replace(self.request,**changes),code)))
        self.record('frozen_request_failures',failures=rows)

    def test_self_loop(self):
        vectors=json.loads((campaign.ROOT/'specs/grc-v4-conformance-vectors.json').read_text())
        vector=next(v for v in vectors['atomic_failure_vectors'] if v['fixture_id']=='G9-FAIL-SOURCE-SELF-LOOP')
        graph=GRC9V4PortGraph.from_payload(vector['source_graph_fixture'])
        n=len(graph.edges)
        reference=stage_reference_fixture(graph=GRCV4Graph.from_port_graph(graph),
            weights={e.edge_id:1.0 for e in graph.edges},base=[[0.0]*n for _ in range(n)],
            changes={'candidate':{'Lambda_C':1/512},'realization':{'tolerance':1e-8},
                     'solver':{'absolute_tolerance':1e-11,'relative_tolerance':1e-11}})
        role=GRCV4AuthoritativeState((1.0,)*len(graph.live_node_ids),None,None)
        inputs=replace(self.seed.inputs,geometry=reference.geometry(),current=role,reset=role,Q_target=float(len(role.C)))
        seed=native.GRC9V4COSState(inputs,self.seed.specialization)
        owner=native.GRC9V4COSOperation(seed)
        request=replace(self.request,source_node_id='source-s',source_state_digest=seed.scientific_digest,
            source_graph_digest=graph.graph_digest,
            target_profile_template_id=cos_profile_template(reference).profile_template_id)
        # No target is constructed: this is a native semantic rejection, not a forged graph.
        with patch.object(native,'GRC9V4COSExpansion',side_effect=AssertionError('target must not construct')):
            row=self.assert_rejected(owner,request,'source_self_loop_unsupported')
        self.record('self_loop',fixture_id=vector['fixture_id'],**row)

    with_os_tolerance=prior.NativeCOSEventTests.with_os_tolerance

    def test_reset_only_split(self):
        # Reuse the unchanged scientific discriminator; augment with pointer/ledger observations.
        with numerical_policy(NumericalPolicy.LEGACY_EXACT):
            prior.NativeCOSEventTests.test_actual_target_os_split_failures_reject_current_and_reset_atomically(self)
            seed,request=self.with_os_tolerance(2**-54)
            owner=native.GRC9V4COSOperation(seed)
            row=self.assert_rejected(owner,request,'target_readmission_failure','target_readmission')
        # A separate, explicitly selected sufficient certificate is inconclusive here.
        # Preserve its typed exception: it is not proof that the domain is empty.
        bounded=native.GRC9V4COSOperation(seed);pointer=bounded._published;checkpoint=bounded.checkpoint()
        with self.assertRaisesRegex(CertificationInconclusive,'no inertia fallback'):
            bounded.expand(request)
        self.assertIs(bounded._published,pointer);self.assertEqual(bounded.checkpoint(),checkpoint)
        self.record('reset_only_split',fixture_id='G9-FAIL-TARGET-READMISSION',natural_OS_split_failure=True,
            exact_policy='legacy_exact_v1',bounded_policy='certified_arb_256_weighted_v1',
            bounded_outcome='CertificationInconclusive',bounded_publication_unchanged=True,
            current_control_passes=True,reset_tolerance=2**-54,current_failure_tolerance=2**-56,**row)

    def test_publication_failures(self):
        rows=[];transfer=GRC9V4COSExpansion.transfer
        for role in ('current','reset'):
            authority=getattr(self.seed.inputs,role)
            def changed(target,state):
                value=transfer(target,state)
                return replace(value,C=(value.C[0]+1,*value.C[1:])) if state==authority else value
            with patch.object(GRC9V4COSExpansion,'transfer',changed):
                rows.append(dict(role=role,injected=True,**self.assert_rejected(
                    self.owner,self.request,'target_readmission_failure','target_readmission')))
        readmit=native._cos_readmit;admitted=[]
        def observe(s):
            readmit(s);admitted.append(s.scientific_digest)
        # Raise after the prospective publication tuple is assembled, before the sole pointer swap.
        result_type=native.GRCV4LifecycleResult
        def fail_success(*args,**kwargs):
            if args and args[0]=='committed':raise ValueError('late result construction')
            return result_type(*args,**kwargs)
        with patch.object(native,'_cos_readmit',observe),patch.object(native,'GRCV4LifecycleResult',fail_success):
            rows.append(dict(injected=True,location='after_prospective_publication',**self.assert_rejected(
                self.owner,self.request,'invalid_topology_event','commit')))
        self.assertEqual(len(admitted),2)
        self.assertNotEqual(admitted[0],admitted[1])
        self.record('publication_failures',failures=rows,both_source_and_target_admitted=True)

    def test_event_replay(self):
        self.committed();checkpoint=self.owner.checkpoint()
        restored=native.GRC9V4COSOperation.replay(checkpoint)
        self.assertEqual(restored.checkpoint(),checkpoint)
        self.assertEqual(restored.state.to_payload(),self.owner.state.to_payload())
        counts=campaign.occupancy(restored.state.inputs.geometry.reference.graph.port_graph)
        mutations={
            'current':lambda d:d['state']['inputs']['current']['C'].__setitem__(0,123),
            'reset':lambda d:d['state']['inputs']['reset']['C'].__setitem__(0,123),
            'receipt':lambda d:d['receipts'].pop(),
            'chirality':lambda d:d['requests'][0].__setitem__('module_chirality',-1),
            'model_identity':lambda d:d['initial'].__setitem__('model_identity',d['state']['model_identity']),
            'lifecycle_identity':lambda d:d.__setitem__('lifecycle_digest','grcv4-lifecycle-sha256:'+'0'*64),
        }
        for name,mutate in mutations.items():
            d=json.loads(checkpoint);mutate(d)
            with self.subTest(mutation=name),self.assertRaises((ValueError,TypeError)):
                native.GRC9V4COSOperation.replay(canonical_json_bytes(d))
        self.assertEqual(self.owner.checkpoint(),checkpoint)
        self.record('event_replay',**counts,checkpoint_sha256=campaign.sha(checkpoint),
            receipt_count=len(restored.receipts),rejected_mutations=list(mutations),checkpoint_exact=True)

    def test_incomplete_reference(self):
        self.committed();reference=self.owner.state.inputs.geometry.reference
        payload=reference.to_payload();params=payload['profile']['params_resolved']
        weights=params['candidate']['W_C_tr'];weights.pop(next(iter(weights)))
        params['candidate']['W_C_tr_content_digest']=payload_identity('wctr_identity_payload',
            {'schema_version':'grcv4-wctr-identity-v1','W_C_tr':weights})
        payload['profile']['identity_payload']['params_hash']=payload_identity('resolved_params',params)
        payload['profile']['complete_profile_id']=payload_identity('profile_identity_payload',payload['profile']['identity_payload'])
        with self.assertRaisesRegex(ValueError,'reference|edge|W_C_tr'):
            GRCV4ReferenceGeometry.from_payload(payload)
        self.record('incomplete_reference',content_and_params_reidentified=True,
            boundary='reference reconstruction before ownership')

    def continuation(self):
        self.committed();cp=self.owner.checkpoint()
        restored=native.GRC9V4COSOperation.replay(cp)
        before=restored.state.inputs
        owner=generic.GRCV4Operation(before)
        self.assertEqual(owner.reference,before.geometry.reference)
        self.assertEqual(owner.state.current,before.current)
        self.assertEqual(owner.state.reset.authoritative,before.reset)
        self.assertEqual(owner.state.receipt_ledger,())
        return owner,before,cp

    def test_continuation_reset(self):
        owner,before,cp=self.continuation()
        # Verify transfer independently, by node role, for both different resource histories.
        ids=before.geometry.reference.graph.live_node_ids
        for role in ('current','reset'):
            source=getattr(self.seed.inputs,role);target=getattr(before,role)
            for node,value in zip(ids,target.C):
                if isinstance(node,int):expected=source.C[node]
                elif '/satellite/' in node:expected=float(Fraction(source.C[0])* (Fraction(1,2) if node.endswith('/1') else Fraction(1,4)))
                else:expected=0.0
                self.assertEqual(value,expected)
        seed_snapshot=owner.snapshot();step=owner.step_v4(GRCV4StepRequestInput(
            'grcv4-step-request-input-v1','p985-cos-continuation',1/4096,FrozenJSONMap({})))
        self.assertTrue(step.committed,step.failure)
        stepped=owner.snapshot();restored=generic.GRCV4Operation.from_state(stepped)
        self.assertEqual(restored.snapshot(),stepped)
        self.assertNotEqual(restored.state.current,before.current)
        clock=(restored.state.step_index,restored.state.time)
        ledger=tuple(restored.state.receipt_ledger)
        restored.reset();reset=restored.snapshot()
        self.assertEqual(restored.state.current,before.reset)
        self.assertEqual(restored.state.reset.authoritative,before.reset)
        self.assertEqual((restored.state.step_index,restored.state.time),clock)
        self.assertEqual(tuple(restored.state.receipt_ledger)[:len(ledger)],ledger)
        self.assertGreater(len(restored.state.receipt_ledger),len(ledger))
        again=generic.GRCV4Operation.from_state(reset)
        self.assertEqual(again.snapshot(),reset)
        self.assertEqual(campaign.occupancy(again.reference.graph.port_graph),campaign.occupancy(before.geometry.reference.graph.port_graph))
        self.assertEqual(self.owner.checkpoint(),cp)
        for key in ('receipt_ledger','commit_records'):
            changed=deepcopy(reset);changed[key].pop()
            with self.assertRaises(ValueError):generic.GRCV4Operation.from_state(changed)
        self.record('continuation_reset',event_checkpoint_sha256=campaign.sha(cp),
            event_target_inputs_sha256=campaign.sha(canonical_json_bytes(before.to_payload())),
            seed_snapshot_sha256=campaign.sha(canonical_json_bytes(seed_snapshot)),
            stepped_snapshot_sha256=campaign.sha(canonical_json_bytes(stepped)),
            reset_snapshot_sha256=campaign.sha(canonical_json_bytes(reset)),
            fresh_generic_ledger=True,native_steps=1,native_resets=1,
            reset_baseline_preserved=True,clock_preserved_on_reset=True,
            event_checkpoint_unchanged=True,public_specialization_facade=False)

    def test_reset_rollback(self):
        owner,before,cp=self.continuation();snapshot=owner.snapshot();pointer=owner._owned
        with patch.object(generic,'_validate_publication',side_effect=ValueError('late reset publication')):
            with self.assertRaisesRegex(ValueError,'late reset'):owner.reset()
        self.assertIs(owner._owned,pointer);self.assertEqual(owner.snapshot(),snapshot)
        self.assertEqual(self.owner.checkpoint(),cp)
        self.record('reset_rollback',injected=True,whole_publication_unchanged=True,
            generic_snapshot_sha256=campaign.sha(canonical_json_bytes(snapshot)),event_checkpoint_unchanged=True)


if __name__=='__main__':unittest.main()
