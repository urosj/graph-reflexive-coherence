"""Read-only 8.4h views distinguish an oracle from a native campaign."""
import json
import sys
import unittest
from unittest.mock import patch
import p984h_cos as run
import tranche8_evidence as index

sys.path.insert(0,str(index.ROOT/index.SIDE/'tool/src'))
from grcv4_explorer import tranche8 as api


class LargerRuntimeSurfaces(unittest.TestCase):
    def test_second_beat_native_mechanics_and_fixed_row_trigger(self):
        from pygrc.models.grc_9_v4_expansion import GRC9ExpansionPolicy, GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput, GRC9V4COSExpansion
        from pygrc.models.grc_9_v4_topology import GRC9V4RowDifferential
        with run.exact_backend(run.ExactBackend.FLINT),run.numerical_policy(run.NumericalPolicy.CERTIFIED_ARB_256):
            r=run.read_result();_,initial=run.second_source_input()
            state=run.postbeat(initial,r['source_step']['after_C'])
            declaration,_,request,identity,event,target=run.fresh_subject(state)
            self.assertEqual(state.inputs.step_index,2)
            self.assertEqual(state.inputs.time,2*initial.inputs.dt)
            self.assertEqual(state.inputs.reset,initial.inputs.reset)
            graph=state.inputs.geometry.reference.graph.port_graph
            # Current affects net-flux diagnostics, not this fixed-row gradient.
            # This is a mechanical comparison, not a substitute for native reads.
            rows=GRC9V4RowDifferential(graph,-1).evaluate(state.inputs.current.C,(1.,)*len(graph.edges),(0.,)*len(graph.edges))
            native_gradient=next(x.gradient for x in rows if x.node_id==0)
            self.assertEqual(list(native_gradient),r['trigger']['gradient'])
            plan=GRC9V4ExpansionPlan(graph,state.scientific_digest,GRC9V4ExpansionRequestInput.from_payload(request),
                GRC9ExpansionPolicy.from_payload(declaration['specialization']['resolved']['expansion']))
            self.assertEqual(plan.event_identity_payload(),identity);self.assertEqual(plan.event_id,event)
            self.assertEqual(plan.target_graph.to_payload(),target['graph'])
            expansion=GRC9V4COSExpansion(plan,state.inputs.geometry.reference)
            self.assertEqual(expansion.target.profile.to_payload(),target['profile'])
            for role in run.ROLES:
                self.assertEqual(list(expansion.transfer(getattr(state.inputs,role)).C),target['roles'][role]['C'])

    def test_selected_api_and_browser_are_source_bound_without_solves(self):
        import p984h_cos_event_successor as successor
        with patch.object(api,'_index',return_value=index),patch.object(run,'calculate',side_effect=AssertionError('rerun')),patch.object(run,'check',side_effect=AssertionError('full checker')),patch.object(successor,'check',side_effect=AssertionError('full successor checker')):
            value=api.tranche8_status(index.ROOT,family='C_OS',checkpoint='8.4h')
        row=value['runtime']
        self.assertFalse(value['other_families_checked'])
        self.assertFalse(row['original_trigger']['eligible']);self.assertTrue(row['fresh_trigger']['eligible'])
        self.assertEqual(row['oracle_steps'],2);self.assertEqual(row['source_oracle_steps'],1)
        self.assertEqual(row['source_beats_before_request'],2);self.assertTrue(row['initial_conditions_unchanged'])
        self.assertEqual(row['dense_screen_steps'],20);self.assertEqual(row['exact_reused_reset_cases'],1)
        self.assertEqual(row['native_steps'],38);self.assertEqual(row['native_events'],9)
        self.assertEqual(row['status'],'native_baseline_and_covariance_accepted')
        self.assertEqual(row['accepted_on'],'2026-10-21')
        self.assertTrue(row['original_execution_flags_unchanged'])
        self.assertFalse(row['aggregate_closed'])
        self.assertEqual(row['native']['native_events'],0)  # Original attempt only.
        event=row['event_successor']
        self.assertEqual(event['outcome'],'completed');self.assertEqual(event['native_events'],1)
        self.assertLess(event['seconds'],event['cap_seconds'])
        self.assertTrue(event['both_role_admission_checked']);self.assertFalse(event['failed_attempt_artifact_retained'])
        self.assertEqual(event['publication_observation'],'committed_and_checked')
        self.assertFalse(event['full_reconstruction_rerun']);self.assertFalse(event['native_numerics_rerun'])
        self.assertFalse(event['user_accepted'])
        self.assertEqual(event['target_steps_by_role'],{'current':0,'reset':0})
        continuation=row['continuation']
        self.assertEqual(continuation['target_steps'],20);self.assertEqual(continuation['final_reads'],2)
        self.assertTrue(continuation['baseline_complete'])
        self.assertTrue(continuation['first_steps_match_certified_oracle'])
        self.assertTrue(continuation['detached_continuation'])
        self.assertFalse(continuation['native_numerics_rerun'])
        self.assertFalse(continuation['uniform_trajectory_enclosure'])
        for result in continuation['roles'].values():
            self.assertEqual(result['native_steps'],10);self.assertEqual(result['final_reads'],1)
            self.assertEqual(len(result['results']),11)
            self.assertTrue(all(x>0 for x in result['minimum_resources']))
        self.assertEqual(row['native']['target_steps_by_role'],{'current':0,'reset':0})
        self.assertEqual(row['native']['failures'],[])
        self.assertIn('artifact removed at user request',row['native']['timeout_note'])
        self.assertTrue(row['performance']['full_read_parity'])
        self.assertFalse(row['performance']['event_execution'])
        self.assertGreater(row['performance']['scalar_kernel_cold_seconds'],0)
        self.assertIn('COSScalarReuse',row['performance']['scalar_kernel_result']['path'])
        self.assertGreater(row['performance']['dyadic_cold_seconds'],0)
        self.assertTrue(row['performance']['repeated_source_step_full_parity'])
        self.assertIn('COSDyadicStep',row['performance']['repeated_source_step_result']['path'])
        self.assertTrue(row['covariance_executed']);self.assertTrue(row['user_accepted'])
        covariance=row['covariance']
        self.assertEqual(len(covariance['mechanical_transforms']),8)
        self.assertEqual(covariance['native_events'],8);self.assertEqual(covariance['target_steps'],16)
        self.assertEqual(covariance['completed_numerical_transforms'],covariance['required_transforms'])
        self.assertEqual(covariance['pending_numerical_transforms'],[])
        self.assertTrue(covariance['covariance_complete']);self.assertFalse(covariance['source_prefix_rerun'])
        self.assertFalse(covariance['native_numerics_rerun']);self.assertEqual(covariance['transformed_horizon'],1)
        saved=json.loads((index.ROOT/index.ASSET).read_text().split(' = ',1)[1].rstrip(';\n'))
        self.assertEqual(saved['coverage']['larger_runtime'],[row])
        for name in (*index.LARGER_RUNTIME_COS_SOURCES,*index.LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES,*index.LARGER_RUNTIME_COS_CONTINUATION_SOURCES,*index.LARGER_RUNTIME_COS_COVARIANCE_SOURCES):
            with patch.object(index.Sources,'current_bytes',return_value=b'forged'),self.assertRaisesRegex(ValueError,'source drift'):
                index.Sources(index.ROOT).raw(name)
        with self.assertRaisesRegex(ValueError,'not yet'):
            api.tranche8_status(index.ROOT,family='A_PC',checkpoint='8.4h')

    def test_historical_sources_are_exact_and_do_not_certify_current_code(self):
        import p984h_pre_solve_reuse_sources as history
        name='src/pygrc/models/grc_v4_numerics.py'
        old=history.historical_sha(name)
        self.assertTrue(history.historical_binding(name,old,b'current successor'))
        self.assertFalse(history.historical_binding(name,'forged',b'current successor'))
        self.assertFalse(history.historical_binding('src/pygrc/models/grc_v4_geometry.py',old,b'changed'))
        with self.assertRaises(ValueError):history.historical_sha('unknown')

    def test_covariance_completion_requires_every_event_and_role(self):
        import p984h_cos_covariance as covariance
        import p984h_cos_covariance_transforms as individual
        with patch.object(covariance.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')):
            complete=index.larger_cos_covariance_view(index.Sources(index.ROOT))
            self.assertTrue(complete['covariance_complete'])
            self.assertEqual(len(complete['segments']),24)
            self.assertEqual({(r['kind'],r['segment']) for r in complete['segments']},
                {(k,s) for k in covariance.KINDS for s in ('event',*covariance.ROLES)})
            pins=dict(index.LARGER_RUNTIME_COS_COVARIANCE_SOURCES)
            del pins[individual.path('rotate_twice','reset')]
            with patch.object(index,'LARGER_RUNTIME_COS_COVARIANCE_SOURCES',pins):
                partial=index.larger_cos_covariance_view(index.Sources(index.ROOT))
            self.assertFalse(partial['covariance_complete'])
            self.assertEqual(partial['pending_numerical_transforms'],['rotate_twice'])
            self.assertEqual(partial['target_steps'],15)
            self.assertFalse(complete['user_accepted']);self.assertFalse(partial['user_accepted'])

    def test_complete_covariance_retained_scientific_payloads(self):
        """One final saved-payload review, never another numerical campaign."""
        import p984h_cos_covariance as covariance
        import p984h_cos_covariance_continuation as comparison
        import p984h_cos_covariance_transforms as individual
        with run.exact_backend(run.ExactBackend.FLINT),run.numerical_policy(run.NumericalPolicy.CERTIFIED_ARB_256), \
                patch.object(covariance.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')), \
                patch.object(covariance.native.native,'GRC9V4COSOperation',side_effect=AssertionError('event rerun')), \
                patch.object(covariance,'compare_step',comparison.compare_step):
            original=covariance.native.oracle.old.read(covariance.INPUTS)
            self.assertEqual(original,covariance.manifest())
            for kind in covariance.KINDS:
                with self.subTest(kind=kind):
                    if kind=='combined':
                        declaration=covariance.native.oracle.old.read(comparison.INPUTS)
                        self.assertEqual(declaration,comparison.manifest())
                        covariance.check_record(covariance.read(kind,'event'),original,kind,'event')
                    else:
                        declaration=covariance.native.oracle.old.read(individual.inputs(kind))
                        # Includes the exact event identity/target/admission check once.
                        self.assertEqual(declaration,individual.manifest(kind))
                    for role in covariance.ROLES:
                        record=comparison.read(role) if kind=='combined' else individual.read(kind,role)
                        covariance.check_record(record,declaration,kind,role)

    def test_covariance_geometry_and_role_pressure_without_native_rerun(self):
        from copy import deepcopy
        import p984h_cos_covariance as covariance
        import p984h_cos_covariance_continuation as successor
        if not (index.ROOT/successor.path('current')).exists():self.skipTest('not yet executed')
        with run.exact_backend(run.ExactBackend.FLINT),run.numerical_policy(run.NumericalPolicy.CERTIFIED_ARB_256),patch.object(covariance.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')):
            m=covariance.native.oracle.old.read(successor.INPUTS)
            r=successor.read('current')
            for mutate in (
                lambda x:x['execution']['geometry']['corrector'][0].__setitem__(0,123.),
                lambda x:x['execution'].update(role='reset'),
                lambda x:x['execution'].update(event_record_digest='foreign'),
                lambda x:x['execution']['next_inputs']['reset']['C'].__setitem__(0,123.),
                lambda x:x['execution']['observation'].update(split_admitted=False),
            ):
                bad=deepcopy(r);mutate(bad)
                with self.assertRaises(ValueError):successor.check(covariance.seal(bad),m,'current')


if __name__=='__main__':unittest.main()
